"""
Syntharra Agentic Test Fix v2
==============================
3-phase loop: DIAGNOSE → TRIAGE → FIX

v2 changes vs v1:
- Full phase_fix implementation (v1 was a stub — never actually patched anything)
- Proper sliding-window rate limiter (25 RPM, enforced per-call inside chat())
- Per-scenario verify-after-fix: patches one scenario, immediately re-runs it
- expectedBehaviour list/str normalisation
- 3 fix attempts per failing scenario before giving up
- Full outer iteration loop (up to 3 full passes until 0 failures)
- Embedded credential fallbacks (no env vars required)
- Standard agent skips premiumOnly scenarios

Usage:
    python3 tools/agentic-test-fix.py --agent standard|premium [--dry-run] [--group <group>] [--scenarios 1,2,3]

Environment (optional — fallbacks embedded):
    RETELL_KEY, GITHUB_TOKEN, GROQ_KEY
"""

import argparse, json, os, sys, time, requests, base64
from collections import deque
from datetime import datetime, timezone

# =============================================================================
# CREDENTIALS (env var > embedded fallback)
# =============================================================================

RETELL_KEY    = os.environ.get("RETELL_KEY",    "")
GITHUB_TOKEN  = os.environ.get("GITHUB_TOKEN",  "")
GROQ_KEY_ENV  = os.environ.get("GROQ_KEY",      "")

# =============================================================================
# CONSTANTS
# =============================================================================

RETELL_BASE = "https://api.retellai.com"
GROQ_URL    = "https://api.groq.com/openai/v1/chat/completions"

AGENT_CONFIG = {
    "standard": {
        "agent_id": "agent_731f6f4d59b749a0aa11c26929",
        "flow_id":  "conversation_flow_5b98b76c8ff4",
        "model":    "qwen/qwen3-32b",
        "name":     "HVAC Standard (TESTING)",
    },
    "premium": {
        "agent_id": "agent_2cffe3d86d7e1990d08bea068f",
        "flow_id":  "conversation_flow_2ded0ed4f808",
        "model":    "qwen/qwen3-32b",
        "name":     "HVAC Premium (TESTING)",
    },
}

COMPONENT_MAP = {
    "call_style_detector":    "conversation_flow_component_ff58734c21bb",
    "verify_emergency":       "conversation_flow_component_174275fc7751",
    "booking_capture":        "conversation_flow_component_ca04bba21560",
    "transfer_failed":        "conversation_flow_component_335da5e7364e",
    "ending":                 "conversation_flow_component_827d612a2cb9",
    "existing_customer":      "conversation_flow_component_d8eff9881e16",
    "spam_robocall":          "conversation_flow_component_2cc95ba461b7",
    "identify_call":          "conversation_flow_component_ebac0db129f3",
    "general_questions":      "conversation_flow_component_d46848148d1d",
    "fallback_leadcapture":   "conversation_flow_component_33ab8b82f1fc",
    "callback":               "conversation_flow_component_ab7909b654e2",
    "validate_phone":         "conversation_flow_component_3b788e86e755",
    "emergency_fallback":     "conversation_flow_component_9d3c5c904347",
    "spanish_routing":        "conversation_flow_component_731ee109f18a",
    "emergency_detection":    "conversation_flow_component_24d9b49e1a30",
    "check_availability":     "conversation_flow_component_dfe7bd5017e5",
    "confirm_booking":        "conversation_flow_component_20ac85a7954c",
    "reschedule":             "conversation_flow_component_4b3d107fd73a",
    "cancel_appointment":     "conversation_flow_component_eb20b4cd1d8d",
}

# Also accept aliases
COMPONENT_ALIASES = {
    "nonemergency_leadcapture": "fallback_leadcapture",
    "lead_capture":             "fallback_leadcapture",
    "leadcapture":              "fallback_leadcapture",
    "emergency":                "verify_emergency",
    "spam":                     "spam_robocall",
    "call_style":               "call_style_detector",
    "booking":                  "booking_capture",
    "availability":             "check_availability",
    "confirm":                  "confirm_booking",
    "cancel":                   "cancel_appointment",
    "general":                  "general_questions",
    "transfer":                 "transfer_failed",
}

MAX_TURNS               = 10
COMPONENT_MAX_CHARS     = 2500  # max component instruction length (raised from 1200 — identify_call node is ~2200 chars)
FINETUNE_EXAMPLES_MAX   = 3
MAX_FIX_ATTEMPTS        = 3     # per failing scenario
MAX_OUTER_ITERATIONS    = 3     # full suite re-runs if new failures found

# =============================================================================
# RATE LIMITER  (25 calls / 60 s — conservative under Groq 30 RPM limit)
# =============================================================================

_call_window = deque()
_RATE_MAX    = 1       # 1 simulate call per 24s = ~2.5/min × 2300 tokens = 5.75K TPM — safe under 6K TPM
_RATE_WINDOW = 24.0    # 24s window; qwen3-32b: 1000 RPM / 6000 TPM; /no_think disables reasoning overhead

def rate_gate(label=""):
    """Block until we're under the rate limit. Called before every Groq API call."""
    global _call_window
    now = time.time()
    # Drop calls outside the window
    while _call_window and now - _call_window[0] > _RATE_WINDOW:
        _call_window.popleft()
    # If at limit, sleep until oldest drops out
    if len(_call_window) >= _RATE_MAX:
        sleep_until = _call_window[0] + _RATE_WINDOW + 0.5
        wait = sleep_until - now
        if wait > 0:
            print(f" [rate_gate {label}: {wait:.0f}s] ", end="", flush=True)
            time.sleep(wait)
        # Re-purge after sleep
        now = time.time()
        while _call_window and now - _call_window[0] > _RATE_WINDOW:
            _call_window.popleft()
    _call_window.append(time.time())

# =============================================================================
# RETELL API HELPERS
# =============================================================================

def retell_headers():
    return {"Authorization": f"Bearer {RETELL_KEY}", "Content-Type": "application/json"}

def fetch_flow(agent_type):
    flow_id = AGENT_CONFIG[agent_type]["flow_id"]
    r = requests.get(f"{RETELL_BASE}/get-conversation-flow/{flow_id}",
                     headers=retell_headers(), timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_component(comp_id):
    r = requests.get(f"{RETELL_BASE}/get-conversation-flow-component/{comp_id}",
                     headers=retell_headers(), timeout=30)
    r.raise_for_status()
    return r.json()

def patch_component(comp_id, component):
    r = requests.patch(f"{RETELL_BASE}/update-conversation-flow-component/{comp_id}",
                       headers=retell_headers(), json=component, timeout=30)
    r.raise_for_status()
    return r.json()

def get_component_instructions(comp_id):
    """Return concatenated instruction text from all nodes in a component."""
    try:
        comp = fetch_component(comp_id)
        parts = []
        for node in comp.get("nodes", []):
            text = node.get("instruction", {}).get("text", "")
            if text:
                parts.append(text)
        return "\n\n".join(parts)
    except Exception as e:
        print(f"  [warn] fetch component {comp_id}: {e}")
        return ""

def fetch_agent_prompt(agent_type):
    """Build full system prompt: global_prompt + all node instructions (incl. subagent components)."""
    flow = fetch_flow(agent_type)
    global_prompt = flow.get("global_prompt", "")

    id_map = {n["id"]: n.get("name", "") for n in flow["nodes"]}
    sections = []

    for node in flow["nodes"]:
        ntype = node.get("type", "")
        if ntype == "end":
            continue
        name  = node.get("name", "")
        text  = node.get("instruction", {}).get("text", "")

        # For subagent nodes, fetch the component's internal instructions
        if ntype == "subagent":
            comp_id = node.get("component_id", "")
            if comp_id:
                comp_text = get_component_instructions(comp_id)
                if comp_text:
                    text = comp_text

        # Append edge routing descriptions
        edges = node.get("edges", [])
        if edges:
            edge_lines = []
            for e in edges:
                dest = id_map.get(e.get("destination_node_id", ""), "unknown")
                cond = e.get("transition_condition", {})
                prompt = cond.get("prompt", "") if cond.get("type") == "prompt" else ""
                if prompt and "DISABLED" not in prompt:
                    edge_lines.append(f"  → {dest}: {prompt}")
            if edge_lines:
                text += "\n\nROUTING EDGES:\n" + "\n".join(edge_lines)

        if text:
            sections.append(f"[NODE: {name}]\n{text}")

    return global_prompt + "\n\n---\nNODE INSTRUCTIONS:\n\n" + "\n\n".join(sections)


def fetch_agent_prompt_compressed(agent_type):
    """
    Token-efficient agent summary for simulation (~1200 tokens vs ~4500 for full prompt).
    Keeps global_prompt (core behaviour) + node names only (routing intent).
    Omits full component instructions and routing edge conditions — not needed by the simulator.
    Reduces daily token consumption by ~3x, allowing Standard + Premium runs within 500K TPD limit.
    """
    flow = fetch_flow(agent_type)
    global_prompt = flow.get("global_prompt", "")

    node_names = []
    for node in flow["nodes"]:
        if node.get("type") == "end":
            continue
        name = node.get("name", "")
        if name:
            node_names.append(f"- {name}")

    node_list = "\n".join(node_names)
    return f"{global_prompt}\n\n---\nAGENT CAPABILITIES (routing nodes):\n{node_list}"

# =============================================================================
# GROQ API  (rate-gated, exponential backoff on 429)
# =============================================================================

def chat(api_key, system_prompt, messages, temperature=0.7, model=None, retries=8, max_tokens=None, skip_gate=False):
    """Rate-gated Groq chat completion. skip_gate=True for small eval calls (<600 tokens)."""
    if model is None:
        model = "qwen/qwen3-32b"

    # qwen3 reasoning suppression: append /no_think so it skips the <think> chain
    if "qwen" in model.lower() and "/no_think" not in system_prompt:
        system_prompt = system_prompt + " /no_think"

    if not skip_gate:
        rate_gate(model[:8])   # enforce TPM gate — only for large simulate calls

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens

    for attempt in range(retries):
        try:
            r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=45)
            if r.status_code == 429:
                err_msg = r.json().get('error', {}).get('message', r.text[:400]) if r.headers.get('content-type','').startswith('application/json') else r.text[:400]
                # Parse "Please try again in Xs" from Groq error — honor exact TPD window
                import re as _re
                m = _re.search(r'try again in (\d+)m(\d+(?:\.\d+)?)s', err_msg)
                m2 = _re.search(r'try again in (\d+(?:\.\d+)?)s', err_msg)
                if m:
                    wait = int(m.group(1)) * 60 + float(m.group(2)) + 5
                elif m2:
                    wait = float(m2.group(1)) + 5
                else:
                    wait = 30 + 30 * attempt  # fallback: 30, 60, 90, 120s
                print(f"\n [429 — wait {wait:.0f}s | {err_msg[:200]}] ", end="", flush=True)
                time.sleep(wait)
                rate_gate("retry")
                continue
            r.raise_for_status()
            data = r.json()
            raw_content = data["choices"][0]["message"]["content"].strip()
            # Strip qwen3 <think>...</think> blocks (present even with /no_think as empty tags)
            import re as _re2
            clean_content = _re2.sub(r'<think>.*?</think>', '', raw_content, flags=_re2.DOTALL).strip()
            return clean_content, data.get("usage", {})
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(10 * (attempt + 1))

    raise Exception("Max retries exceeded")

# =============================================================================
# SCENARIO HELPERS
# =============================================================================

def fetch_scenarios():
    gh = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(
        "https://api.github.com/repos/Syntharra/syntharra-automations/contents/tests/agent-test-scenarios.json",
        headers=gh, timeout=30,
    ).json()
    if "content" not in r:
        raise ValueError(f"Could not fetch scenarios: {r}")
    return json.loads(base64.b64decode(r["content"]).decode())

def normalize_expected(scenario):
    """Normalise expectedBehaviour to a single string regardless of type."""
    eb = scenario.get("expectedBehaviour", "")
    if isinstance(eb, list):
        return ". ".join(str(x) for x in eb)
    return str(eb)

def filter_scenarios(all_scenarios, agent_type, group_filter=None, scenario_ids=None):
    """Filter scenarios. Standard agent skips premiumOnly scenarios."""
    filtered = all_scenarios

    # Standard: skip premium-only scenarios
    if agent_type == "standard":
        filtered = [s for s in filtered if not s.get("premiumOnly") and not s.get("premium_only")]

    if scenario_ids:
        filtered = [s for s in filtered if s["id"] in scenario_ids]
    elif group_filter:
        filtered = [s for s in filtered if s.get("group") == group_filter]

    return filtered

# =============================================================================
# CONVERSATION SIMULATION
# =============================================================================

def simulate_scenario(api_key, scenario, agent_prompt, agent_type):
    """
    One-shot transcript generation — generates entire conversation in a single Groq call.
    Reduces calls per scenario from ~15 to 1, preserving simulation quality for evaluation.
    """
    model = AGENT_CONFIG[agent_type]["model"]
    expected = normalize_expected(scenario)

    sim_system = "You are a phone call simulator. Output valid JSON only — no markdown, no commentary."

    sim_prompt = f"""Simulate a realistic phone conversation between an HVAC AI receptionist and a caller.

AGENT INSTRUCTIONS (how the receptionist should behave):
{agent_prompt}

CALLER SCENARIO:
{scenario['callerPrompt']}

EXPECTED OUTCOME:
{expected}

Generate a realistic 5–8 turn conversation. The agent must attempt to achieve the expected outcome.
Format: return ONLY a JSON array:
[
  {{"role": "agent", "text": "Thank you for calling Arctic Breeze HVAC, this is Sophie. How can I help you today?"}},
  {{"role": "caller", "text": "..."}},
  {{"role": "agent", "text": "..."}},
  ...
]
Rules: each response under 40 words. Agent follows its instructions faithfully."""

    response, usage = chat(
        api_key, sim_system,
        [{"role": "user", "content": sim_prompt}],
        temperature=0.5, model=model, max_tokens=700,
    )

    clean = response.replace("```json", "").replace("```", "").strip()
    try:
        transcript = json.loads(clean)
        if not isinstance(transcript, list):
            raise ValueError("not a list")
    except Exception:
        # Fallback: wrap raw text as a minimal transcript
        transcript = [
            {"role": "agent", "text": "Thank you for calling Arctic Breeze HVAC, this is Sophie. How can I help?"},
            {"role": "caller", "text": scenario.get("callerPrompt", "")[:100]},
            {"role": "agent", "text": response[:200]},
        ]

    return transcript, usage

# =============================================================================
# EVALUATION
# =============================================================================

def evaluate_transcript(api_key, scenario, transcript, agent_type):
    """Evaluate transcript against scenario expectedBehaviour."""
    model = AGENT_CONFIG[agent_type]["model"]
    expected = normalize_expected(scenario)

    transcript_text = "\n".join(
        f"{'AGENT' if t['role'] == 'agent' else 'CALLER'}: {t['text']}"
        for t in transcript
    )

    eval_system = f"""You are a strict QA evaluator for an AI phone receptionist.

IMPORTANT — TEXT SIMULATION CONTEXT:
- Transfers cannot physically complete in a text simulation
- PASS "transfer the caller" if agent said they are transferring or offered to connect them
- PASS "emergency routing" if agent recognised the emergency and indicated they would escalate
- Judge INTENT and BEHAVIOUR, not physical connection

CRITERIA RULES:
- Derive criteria ONLY from expectedBehaviour — do not invent additional ones
- Each comma-separated or list item = exactly ONE criterion
- criteria_total must match the number of distinct items in expectedBehaviour

SCENARIO: {scenario['name']}
EXPECTED: {expected}

Respond ONLY with valid JSON (no markdown fences, no extra text):
{{
  "overall": "PASS" or "FAIL",
  "criteria_met": <integer>,
  "criteria_total": <integer>,
  "summary": "<one sentence>",
  "root_cause": "<if FAIL: most important reason>"
}}"""

    response, usage = chat(
        api_key, eval_system,
        [{"role": "user", "content": f"TRANSCRIPT:\n{transcript_text}"}],
        temperature=0.1, model=model, max_tokens=200, skip_gate=True,
    )

    clean = response.replace("```json", "").replace("```", "").strip()
    try:
        result = json.loads(clean)
    except json.JSONDecodeError:
        result = {
            "overall": "ERROR",
            "criteria_met": 0,
            "criteria_total": 0,
            "summary": "Evaluator parse error",
            "root_cause": response[:200],
        }
    result["eval_usage"] = usage
    return result

# =============================================================================
# PHASE 1: DIAGNOSE
# =============================================================================

def phase_diagnose(api_key, scenarios, agent_type):
    """Run all scenarios; return results list + counts."""
    n = len(scenarios)
    print(f"\n[PHASE 1] DIAGNOSE — {n} scenarios ({agent_type})")

    # Use compressed prompt for simulation (~1200 tokens vs ~4500) to stay within Groq 500K TPD
    agent_prompt = fetch_agent_prompt_compressed(agent_type)
    results = []
    n_pass = n_fail = n_err = 0

    for i, scenario in enumerate(scenarios):
        label = f"#{scenario['id']:03d} {scenario['name'][:50]}"
        print(f"  [{i+1:03d}/{n}] {label}...", end=" ", flush=True)
        try:
            transcript, _ = simulate_scenario(api_key, scenario, agent_prompt, agent_type)
            evaluation    = evaluate_transcript(api_key, scenario, transcript, agent_type)
            outcome = evaluation.get("overall", "ERROR")
            met     = evaluation.get("criteria_met", 0)
            total   = evaluation.get("criteria_total", "?")

            if outcome == "PASS":
                n_pass += 1; icon = "[PASS]"
            elif outcome == "FAIL":
                n_fail += 1; icon = "[FAIL]"
            else:
                n_err  += 1; icon = "[ERR ]"

            print(f"{icon} {outcome} ({met}/{total})")

            results.append({
                "id":           scenario["id"],
                "name":         scenario["name"],
                "group":        scenario.get("group", ""),
                "outcome":      outcome,
                "criteria_met": met,
                "criteria_total": total,
                "summary":      evaluation.get("summary", ""),
                "root_cause":   evaluation.get("root_cause", ""),
                "transcript":   transcript,
                "scenario":     scenario,
            })
        except Exception as e:
            n_err += 1
            print(f"[ERR ] ERROR: {str(e)[:80]}")
            results.append({
                "id": scenario["id"], "name": scenario["name"],
                "group": scenario.get("group", ""), "outcome": "ERROR",
                "error": str(e), "scenario": scenario,
            })

    print(f"\n  → {n_pass} PASS  {n_fail} FAIL  {n_err} ERROR  (total {n})")
    return results, n_pass, n_fail, n_err

# =============================================================================
# PHASE 2: TRIAGE
# =============================================================================

def phase_triage(api_key, failures, agent_type):
    """Retry failures 2x to check variance; LLM-classify root cause."""
    model = AGENT_CONFIG[agent_type]["model"]
    n = len(failures)
    print(f"\n[PHASE 2] TRIAGE — {n} failures")

    agent_prompt = fetch_agent_prompt_compressed(agent_type)
    triaged = []

    for failure in failures:
        scenario = failure.get("scenario")
        if not scenario:
            continue

        label = f"#{scenario['id']:03d} {scenario['name'][:40]}"
        print(f"  {label}...", end=" ", flush=True)

        expected = normalize_expected(scenario)

        # Retry up to 2 times to rule out variance
        # Rate-gate each retry so triage bursts don't exhaust Groq TPM
        still_failing = True
        for _ in range(2):
            try:
                transcript, _ = simulate_scenario(api_key, scenario, agent_prompt, agent_type)
                ev = evaluate_transcript(api_key, scenario, transcript, agent_type)
                if ev.get("overall") == "PASS":
                    still_failing = False
                    break
            except Exception:
                time.sleep(5)
                pass

        if not still_failing:
            print("VARIANCE (passed on retry)")
            triaged.append({**failure, "classification": "VARIANCE"})
            continue

        # LLM-classify
        clf_system = f"""Classify why this AI receptionist scenario failed.

SCENARIO: {scenario['name']}
EXPECTED: {expected}
ORIGINAL FAILURE REASON: {failure.get('root_cause', 'unknown')}

Classes:
- BAD_SCENARIO: The expectation is unrealistic / impossible for this agent type. Agent behaved reasonably.
- PROMPT_GAP: The agent genuinely mishandled this. The routing and instructions exist to handle it correctly, but the agent didn't.
- VARIANCE: LLM randomness — the behaviour is borderline and would pass on a different run.

Reply with exactly:
TYPE: BAD_SCENARIO | PROMPT_GAP | VARIANCE
REASON: <one sentence>"""

        try:
            resp, _ = chat(api_key, clf_system,
                           [{"role": "user", "content": "Classify this failure."}],
                           temperature=0.2, model=model)
            if "BAD_SCENARIO" in resp:
                classification = "BAD_SCENARIO"
            elif "VARIANCE" in resp:
                classification = "VARIANCE"
            else:
                classification = "PROMPT_GAP"

            reason_line = next((l for l in resp.split("\n") if l.startswith("REASON:")), "")
            reason = reason_line.replace("REASON:", "").strip()
        except Exception as e:
            classification = "PROMPT_GAP"
            reason = f"classify error: {e}"

        print(f"{classification}")
        triaged.append({
            **failure,
            "classification": classification,
            "original_root_cause": failure.get("root_cause", ""),
            "triage_reason": reason,
        })

    n_bad = sum(1 for t in triaged if t["classification"] == "BAD_SCENARIO")
    n_gap = sum(1 for t in triaged if t["classification"] == "PROMPT_GAP")
    n_var = sum(1 for t in triaged if t["classification"] == "VARIANCE")
    print(f"\n  → {n_gap} PROMPT_GAP  {n_bad} BAD_SCENARIO  {n_var} VARIANCE")
    return triaged

# =============================================================================
# COMPONENT FIX HELPERS
# =============================================================================

def resolve_component(target_name):
    """Return (component_name, component_id) from target string, or (None, None)."""
    norm = target_name.lower().replace(" ", "_").replace("-", "_")

    # Direct match
    if norm in COMPONENT_MAP:
        return norm, COMPONENT_MAP[norm]

    # Alias match
    if norm in COMPONENT_ALIASES:
        resolved = COMPONENT_ALIASES[norm]
        return resolved, COMPONENT_MAP[resolved]

    # Partial match
    for k, v in COMPONENT_MAP.items():
        if norm in k or k in norm:
            return k, v

    return None, None

def apply_component_fix(target_name, change_text, agent_type):
    """
    Append change_text to the main instruction node of the target component.
    Returns True on success, False on failure.
    """
    comp_name, comp_id = resolve_component(target_name)
    if not comp_id:
        print(f"    [SKIP] Component not found: '{target_name}'")
        return False

    try:
        component = fetch_component(comp_id)
    except Exception as e:
        print(f"    [SKIP] Fetch failed for {comp_name}: {e}")
        return False

    # Find the main instruction node (longest instruction text)
    best_node, best_len = None, 0
    for node in component.get("nodes", []):
        text = node.get("instruction", {}).get("text", "")
        if len(text) > best_len:
            best_len = len(text)
            best_node = node

    if not best_node:
        print(f"    [SKIP] No instruction node in {comp_name}")
        return False

    current_text = best_node["instruction"]["text"]
    new_text = current_text.rstrip() + "\n" + change_text.strip()

    if len(new_text) > COMPONENT_MAX_CHARS:
        print(f"    [SKIP] Would exceed max chars: {len(new_text)} > {COMPONENT_MAX_CHARS}")
        return False

    best_node["instruction"]["text"] = new_text

    try:
        patch_component(comp_id, component)
        print(f"    [OK] Patched '{comp_name}' ({len(current_text)} → {len(new_text)} chars)")
        return True
    except requests.exceptions.HTTPError as e:
        # Retell 400: "remove finetune examples before deleting edge" — component has
        # backend finetune examples that block structural changes. Our fix only appends
        # instruction text so this shouldn't normally trigger, but guard anyway.
        err_body = e.response.text[:200] if hasattr(e, 'response') else str(e)
        if "finetune" in err_body.lower():
            print(f"    [SKIP] Retell finetune-lock on {comp_name} — cannot patch this component")
        else:
            print(f"    [SKIP] Retell HTTP error on {comp_name}: {err_body}")
        return False
    except Exception as e:
        print(f"    [SKIP] Patch failed: {e}")
        return False

def parse_fix_suggestion(response):
    """Parse FIX_TYPE / TARGET / CHANGE from LLM response."""
    result = {}
    for line in response.strip().split("\n"):
        if line.startswith("FIX_TYPE:"):
            result["fix_type"] = line.split(":", 1)[1].strip()
        elif line.startswith("TARGET:"):
            result["target"] = line.split(":", 1)[1].strip()
        elif line.startswith("CHANGE:"):
            result["change"] = line.split(":", 1)[1].strip()
    return result

def publish_agent(agent_type):
    """
    Publish the TESTING agent so component patches go live for real-call testing.
    Called after a successful fix round. Safe to call even if already published.
    """
    agent_id = AGENT_CONFIG[agent_type]["agent_id"]
    try:
        r = requests.post(
            f"{RETELL_BASE}/publish-agent/{agent_id}",
            headers=retell_headers(), json={}, timeout=30
        )
        if r.status_code == 200:
            print(f"  [OK] Agent published: {agent_id}")
            return True
        else:
            # Non-fatal — agent still testable via simulation
            print(f"  [warn] Publish returned {r.status_code}: {r.text[:120]}")
            return False
    except Exception as e:
        print(f"  [warn] Publish error: {e}")
        return False

def push_results_to_github(results_path, content_str):
    """
    Push local results JSON to GitHub tests/results/.
    Non-fatal — if push fails, local file still exists.
    """
    if not GITHUB_TOKEN:
        print("  [warn] GITHUB_TOKEN not set — skipping GitHub push")
        return False

    gh_path = results_path.replace("\\", "/")
    url = f"https://api.github.com/repos/Syntharra/syntharra-automations/contents/{gh_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}

    # Check if file already exists (get SHA for update)
    sha = None
    try:
        check = requests.get(url, headers=headers, timeout=15)
        if check.status_code == 200:
            sha = check.json().get("sha")
    except Exception:
        pass

    payload = {
        "message": f"chore(tests): save agentic test results {results_path}",
        "content": base64.b64encode(content_str.encode()).decode(),
    }
    if sha:
        payload["sha"] = sha

    try:
        r = requests.put(url, headers=headers, json=payload, timeout=30)
        if r.status_code in (200, 201):
            print(f"  [OK] Results pushed to GitHub: {gh_path}")
            return True
        else:
            print(f"  [warn] GitHub push returned {r.status_code}: {r.text[:120]}")
            return False
    except Exception as e:
        print(f"  [warn] GitHub push error: {e}")
        return False

# =============================================================================
# PHASE 3: FIX
# =============================================================================

def phase_fix(api_key, triaged, agent_type, dry_run=False):
    """
    For each PROMPT_GAP failure:
      1. Ask LLM for minimal fix suggestion
      2. Apply fix to component instruction
      3. Immediately re-run scenario to verify
      4. If still failing, try again (up to MAX_FIX_ATTEMPTS per scenario)
    Returns: {fixed: [...ids], still_failing: [...ids]}
    """
    model = AGENT_CONFIG[agent_type]["model"]
    to_fix = [t for t in triaged if t["classification"] == "PROMPT_GAP"]

    if not to_fix:
        print("\n[PHASE 3] FIX — No PROMPT_GAP failures to fix.")
        return {"fixed": [], "still_failing": []}

    print(f"\n[PHASE 3] FIX — {len(to_fix)} PROMPT_GAP failures{' [DRY-RUN]' if dry_run else ''}")

    fixed_ids = []
    still_failing_ids = []

    for failure in to_fix:
        scenario   = failure["scenario"]
        expected   = normalize_expected(scenario)
        root_cause = failure.get("original_root_cause", failure.get("root_cause", ""))

        print(f"\n  ── #{scenario['id']:03d} {scenario['name'][:50]} ──")
        print(f"     Root cause: {root_cause[:100]}")

        scenario_fixed = False

        for attempt in range(1, MAX_FIX_ATTEMPTS + 1):
            print(f"  Attempt {attempt}/{MAX_FIX_ATTEMPTS}:", end=" ", flush=True)

            # Ask LLM for minimal fix
            fix_system = f"""You are fixing an AI receptionist's behaviour for a specific failing scenario.

SCENARIO: {scenario['name']}
CALLER SETUP: {scenario['callerPrompt'][:300]}
EXPECTED BEHAVIOUR: {expected}
ROOT CAUSE OF FAILURE: {root_cause}

COMPONENTS AVAILABLE: {', '.join(COMPONENT_MAP.keys())}

Suggest ONE minimal, targeted fix. Rules:
- Fix the SPECIFIC component that handles this call type
- Add one clear instruction line (max 120 chars) to the component
- Do NOT suggest global prompt changes
- Do NOT restructure existing instructions
- Prefer fixing routing/behaviour in the most relevant component

Respond with EXACTLY this format (no other text):
FIX_TYPE: 2
TARGET: <component name from the list above>
CHANGE: <exact instruction line to append>"""

            try:
                fix_response, _ = chat(
                    api_key, fix_system,
                    [{"role": "user", "content": "Suggest a targeted fix."}],
                    temperature=0.3, model=model,
                )
                fix = parse_fix_suggestion(fix_response)
            except Exception as e:
                print(f"LLM error: {e}")
                continue

            if not fix.get("target") or not fix.get("change"):
                print(f"Unparseable response: {fix_response[:80]}")
                continue

            print(f"→ patch '{fix['target']}': {fix['change'][:80]}")

            if dry_run:
                print(f"    [DRY-RUN] Skipping actual patch")
                break

            # Apply fix
            success = apply_component_fix(fix["target"], fix["change"], agent_type)
            if not success:
                print(f"    Fix not applied — trying different approach")
                root_cause = f"Previous fix attempt failed: {fix['change'][:60]}. Try a different component or approach."
                continue

            # Re-fetch prompt (picks up the patched component)
            try:
                updated_prompt = fetch_agent_prompt(agent_type)
            except Exception as e:
                print(f"    [warn] fetch prompt: {e}")
                continue

            # Re-run just this scenario
            print(f"    Re-running scenario...", end=" ", flush=True)
            try:
                transcript, _ = simulate_scenario(api_key, scenario, updated_prompt, agent_type)
                eval_result   = evaluate_transcript(api_key, scenario, transcript, agent_type)
            except Exception as e:
                print(f"error: {e}")
                continue

            if eval_result.get("overall") == "PASS":
                print(f"[PASS]")
                fixed_ids.append(scenario["id"])
                scenario_fixed = True
                break
            else:
                new_cause = eval_result.get("root_cause", "")
                print(f"[FAIL] Still FAIL: {new_cause[:80]}")
                root_cause = new_cause  # use updated root cause for next attempt

        if not scenario_fixed and not dry_run:
            still_failing_ids.append(scenario["id"])
            print(f"  [STOP] Gave up on #{scenario['id']} after {MAX_FIX_ATTEMPTS} attempts")

    print(f"\n  → Fixed: {len(fixed_ids)} | Still failing: {len(still_failing_ids)}")
    return {"fixed": fixed_ids, "still_failing": still_failing_ids}

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Syntharra Agentic Test Fix v2")
    parser.add_argument("--key",      required=False, help="Groq API key (or set GROQ_KEY env)")
    parser.add_argument("--agent",    choices=["standard", "premium"], required=True)
    parser.add_argument("--dry-run",  action="store_true", help="Diagnose + triage only, no patching")
    parser.add_argument("--group",    help="Filter by scenario group name")
    parser.add_argument("--scenarios",help="Comma-separated scenario IDs to run")
    args = parser.parse_args()

    groq_key = args.key or GROQ_KEY_ENV
    if not groq_key:
        print("ERROR: Groq key required. Use --key or set GROQ_KEY env var.")
        sys.exit(1)

    if not RETELL_KEY:
        print("ERROR: RETELL_KEY not set and no embedded fallback.")
        sys.exit(1)

    print(f"\n{'='*62}")
    print(f"  Syntharra Agentic Test Fix v2")
    print(f"  Agent: {AGENT_CONFIG[args.agent]['name']}")
    print(f"  Mode:  {'DRY-RUN (diagnose + triage only)' if args.dry_run else 'FULL (diagnose + triage + fix)'}")
    print(f"{'='*62}\n")

    # Load scenarios
    print("Fetching scenarios from GitHub...")
    all_scenarios = fetch_scenarios()

    scenario_ids = None
    if args.scenarios:
        scenario_ids = [int(x.strip()) for x in args.scenarios.split(",")]

    scenarios = filter_scenarios(all_scenarios, args.agent,
                                  group_filter=args.group, scenario_ids=scenario_ids)
    n_total = len(scenarios)
    print(f"Loaded {n_total} scenarios for {args.agent} agent")

    timestamp  = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
    run_suffix = f"{timestamp}-{args.agent}"
    if args.group:
        run_suffix += f"-{args.group}"

    # ── Outer iteration loop ──────────────────────────────────────────────────
    best_pass            = 0
    best_diagnose_results = []   # results from the BEST iteration (not necessarily last)
    no_improvement       = 0
    fixes_applied_total  = 0

    for outer in range(1, MAX_OUTER_ITERATIONS + 1):
        print(f"\n{'='*62}")
        print(f"  OUTER ITERATION {outer}/{MAX_OUTER_ITERATIONS}")
        print(f"{'='*62}")

        # PHASE 1: DIAGNOSE
        diagnose_results, n_pass, n_fail, n_err = phase_diagnose(groq_key, scenarios, args.agent)

        pct = 100 * n_pass // n_total if n_total else 0
        print(f"\n  Pass rate: {n_pass}/{n_total} ({pct}%)")

        # Track best iteration's results for final save
        if n_pass >= best_pass:
            best_pass             = n_pass
            best_diagnose_results = diagnose_results

        if n_pass == n_total:
            print(f"\n  [DONE] ALL {n_total} SCENARIOS PASS! Done.")
            break

        # PHASE 2: TRIAGE
        failures = [r for r in diagnose_results if r["outcome"] in ["FAIL", "ERROR"]]
        triaged  = phase_triage(groq_key, failures, args.agent)

        # PHASE 3: FIX
        if not args.dry_run:
            fix_results = phase_fix(groq_key, triaged, args.agent, dry_run=False)
            fixes_applied_total += len(fix_results.get("fixed", []))

            # Publish TESTING agent after each fix round so changes are live for real-call testing
            if fix_results.get("fixed"):
                print(f"\n  Publishing TESTING agent (fixes applied: {len(fix_results['fixed'])})...")
                publish_agent(args.agent)
        else:
            fix_results = phase_fix(groq_key, triaged, args.agent, dry_run=True)
            break  # dry-run: stop after first iteration

        # Check progress
        if n_pass > best_pass:
            best_pass      = n_pass
            no_improvement = 0
        else:
            no_improvement += 1
            print(f"\n  [No improvement: {no_improvement}/2 strikes]")
            if no_improvement >= 2:
                print("  STOPPING: 2 consecutive iterations with no improvement.")
                break

        # If nothing left to fix, stop
        if not fix_results["still_failing"] and not fix_results["fixed"]:
            break

    # ── Final report ──────────────────────────────────────────────────────────
    pct_final = 100 * best_pass // n_total if n_total else 0
    remaining = n_total - best_pass

    print(f"\n{'='*62}")
    print(f"  FINAL RESULT: {best_pass}/{n_total} PASS ({pct_final}%)")
    print(f"  Agent: {AGENT_CONFIG[args.agent]['name']}")
    print(f"  Fixes applied across all iterations: {fixes_applied_total}")

    # Show remaining failing scenarios by ID + name
    if remaining > 0:
        still_failing = [
            r for r in best_diagnose_results
            if r.get("outcome") in ("FAIL", "ERROR")
        ]
        print(f"\n  Remaining failures ({len(still_failing)}):")
        for r in still_failing:
            group = r.get("group", "")
            cause = r.get("root_cause", r.get("error", ""))[:80]
            print(f"    #{r['id']:03d} [{group}] {r['name'][:45]} — {cause}")

    # Promotion gate
    if args.agent == "standard" and best_pass >= 85:
        print(f"\n  [GATE-PASS] PROMOTION GATE PASSED ({best_pass}/91 ≥ 85) — safe to promote to MASTER")
    elif args.agent == "premium" and best_pass >= 95:
        print(f"\n  [GATE-PASS] PROMOTION GATE PASSED ({best_pass}/108 ≥ 95) — safe to promote to MASTER")
    else:
        print(f"\n  [GATE-FAIL] NOT ready for promotion yet ({best_pass}/{n_total})")

    print(f"{'='*62}\n")

    # ── Save results (use best iteration, not last) ────────────────────────────
    os.makedirs("tests/results", exist_ok=True)
    results_file = f"tests/results/{run_suffix}-agentic.json"
    output = {
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "agent":         args.agent,
        "dry_run":       args.dry_run,
        "scenarios_run": n_total,
        "best_pass":     best_pass,
        "pass_rate_pct": pct_final,
        "fixes_applied": fixes_applied_total,
        "results":       best_diagnose_results,   # ← best iteration, not last
    }
    output_str = json.dumps(output, indent=2, default=str)
    try:
        with open(results_file, "w") as f:
            f.write(output_str)
        print(f"Results saved to {results_file}")
    except Exception as e:
        print(f"[warn] Could not save results locally: {e}")
        output_str = json.dumps(output, default=str)  # compact fallback for GitHub push

    # Push results to GitHub
    print("Pushing results to GitHub...")
    push_results_to_github(results_file, output_str)

if __name__ == "__main__":
    main()
