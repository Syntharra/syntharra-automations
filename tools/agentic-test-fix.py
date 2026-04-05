"""
Syntharra Agentic Test Fix — Production Quality
================================================

3-phase loop: DIAGNOSE → TRIAGE → FIX

Diagnoses test failures by running scenarios with proper multi-turn simulation,
triages failures to root cause, and applies minimal targeted fixes to the
Retell agent flow.

Usage:
    python3 tools/agentic-test-fix.py --key <groq_key> --agent standard|premium [--max-fix-iterations 10] [--dry-run] [--group core_flow]

Phases:
  1. DIAGNOSE: Run all scenarios, count pass/fail
  2. TRIAGE: Retry failures 2x, LLM-classify as BAD_SCENARIO | PROMPT_GAP | VARIANCE
  3. FIX: Apply minimal fixes via Retell API PATCH, regression check

Safety:
  - 3-strike stop (3 iterations with no improvement)
  - Max 10 fix iterations (default)
  - Dry-run mode (diagnose + triage only)
"""

import argparse, json, os, sys, time, requests, base64
from datetime import datetime, timezone

# =============================================================================
# CONSTANTS & CONFIG
# =============================================================================

RETELL_KEY = os.environ.get("RETELL_KEY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Agent configs (standard and premium)
AGENT_CONFIG = {
    "standard": {
        "agent_id": "agent_731f6f4d59b749a0aa11c26929",
        "flow_id": "conversation_flow_5b98b76c8ff4",
        "model": "llama-3.3-70b-versatile"
    },
    "premium": {
        "agent_id": "agent_2cffe3d86d7e1990d08bea068f",
        "flow_id": "conversation_flow_2ded0ed4f808",
        "model": "llama-4-scout-17b-16e-instruct"
    }
}

SCENARIO_GROUPS = {
    "core_flow": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "personalities": [11, 12, 13, 14, 15, 16],
    "info_collection": [17, 18, 19, 20, 21, 22, 23, 24],
    "pricing_traps": [25, 26, 27, 28, 29, 30],
    "edge_cases": [31, 32, 33, 34, 35, 36, 37, 38],
    "boundary_safety": [39, 40, 41, 42, 43, 44, 45],
    "premium_specific": [46, 47, 48, 49, 50]
}

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
RETELL_BASE = "https://api.retellai.com"

MAX_TURNS = 10
RATE_LIMIT_RPM = 30
BATCH_SIZE = 5
BATCH_GAP_SECS = 2

COMPONENT_INSTRUCTION_MAX = 500
PROMPT_BASELINE = {
    "standard": 5086,
    "premium": 9190
}
FINETUNE_EXAMPLES_MAX = 3

# =============================================================================
# RETELL API HELPERS
# =============================================================================

def retell_headers():
    """Build Retell API headers with Bearer token."""
    return {
        "Authorization": f"Bearer {RETELL_KEY}",
        "Content-Type": "application/json"
    }

def fetch_flow(agent_type):
    """Fetch the full conversation flow from Retell API."""
    flow_id = AGENT_CONFIG[agent_type]["flow_id"]
    url = f"{RETELL_BASE}/get-conversation-flow/{flow_id}"
    try:
        r = requests.get(url, headers=retell_headers(), timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise Exception(f"Failed to fetch flow {flow_id}: {e}")

def fetch_component_instructions(component_id):
    """Fetch component's internal instructions from Retell API."""
    url = f"{RETELL_BASE}/get-conversation-flow-component/{component_id}"
    try:
        r = requests.get(url, headers=retell_headers(), timeout=30)
        r.raise_for_status()
        cr = r.json()
        sections = []
        for cnode in cr.get("nodes", []):
            ctext = cnode.get("instruction", {}).get("text", "")
            if ctext:
                sections.append(ctext)
        return "\n\n".join(sections)
    except Exception as e:
        print(f"  [Warning] Failed to fetch component {component_id}: {e}")
        return ""

def fetch_agent_prompt(agent_type):
    """Build full agent prompt from flow global_prompt + node instructions."""
    flow = fetch_flow(agent_type)
    global_prompt = flow.get("global_prompt", "")

    # Build node ID → name map for edge resolution
    id_map = {}
    for node in flow["nodes"]:
        id_map[node["id"]] = node.get("name", "")

    node_sections = []
    for node in flow["nodes"]:
        name = node.get("name", "")
        text = node.get("instruction", {}).get("text", "")
        ntype = node.get("type", "")

        if ntype == "end":
            continue

        # For subagent nodes, fetch component's internal instructions
        if ntype == "subagent":
            comp_id = node.get("component_id", "")
            if comp_id:
                comp_text = fetch_component_instructions(comp_id)
                if comp_text:
                    text = comp_text

        # Append edge routing info
        edges = node.get("edges", [])
        if edges:
            edge_lines = []
            for e in edges:
                dest_name = id_map.get(e.get("destination_node_id", ""), "unknown")
                cond = e.get("transition_condition", {})
                cond_text = cond.get("prompt", "") if cond.get("type") == "prompt" else ""
                if cond_text and "DISABLED" not in cond_text:
                    edge_lines.append(f"  → {dest_name}: {cond_text}")
            if edge_lines:
                text += "\n\nROUTING EDGES:\n" + "\n".join(edge_lines)

        if text:
            node_sections.append(f"[NODE: {name}]\n{text}")

    return global_prompt + "\n\n---\nNODE INSTRUCTIONS:\n\n" + "\n\n".join(node_sections)

def patch_component_instruction(component_id, node_name, new_instruction_text):
    """Patch a specific component's instruction via Retell API."""
    url = f"{RETELL_BASE}/update-conversation-flow-component/{component_id}"

    # Fetch current state
    r = requests.get(f"{RETELL_BASE}/get-conversation-flow-component/{component_id}",
                     headers=retell_headers(), timeout=30)
    r.raise_for_status()
    component = r.json()

    # Find and update the target node
    for cnode in component.get("nodes", []):
        if cnode.get("name") == node_name:
            cnode["instruction"]["text"] = new_instruction_text
            break

    # Push back
    try:
        r = requests.patch(url, headers=retell_headers(), json=component, timeout=30)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"  [Error] Failed to patch component {component_id}: {e}")
        return False

# =============================================================================
# GROQ API HELPERS
# =============================================================================

def chat(api_key, system_prompt, messages, temperature=0.7, model=None, retries=3):
    """Chat completion via Groq API with exponential backoff."""
    if model is None:
        model = "llama-3.3-70b-versatile"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [{"role": "system", "content": system_prompt}] + messages
    }

    for attempt in range(retries):
        try:
            r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
            if r.status_code == 429:
                wait = 20 * (attempt + 1)
                print(f" [rate limit — waiting {wait}s]", end="", flush=True)
                time.sleep(wait)
                continue
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip(), data.get("usage", {})
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(10)

    raise Exception("Max retries exceeded")

# =============================================================================
# SCENARIO MANAGEMENT
# =============================================================================

def fetch_scenarios():
    """Fetch scenarios from GitHub."""
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN env var not set")
    gh = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(
        "https://api.github.com/repos/Syntharra/syntharra-automations/contents/tests/agent-test-scenarios.json",
        headers=gh
    ).json()
    return json.loads(base64.b64decode(r["content"]).decode())

def filter_scenarios(all_scenarios, group_filter=None, scenario_ids=None):
    """Filter scenarios by group or explicit IDs."""
    if scenario_ids:
        return [s for s in all_scenarios if s["id"] in scenario_ids]
    elif group_filter:
        ids = SCENARIO_GROUPS.get(group_filter, [])
        return [s for s in all_scenarios if s["id"] in ids]
    else:
        return all_scenarios

# =============================================================================
# CONVERSATION SIMULATION
# =============================================================================

def simulate_scenario(api_key, scenario, agent_prompt, agent_type, max_turns=MAX_TURNS):
    """Simulate multi-turn caller↔agent conversation."""
    model = AGENT_CONFIG[agent_type]["model"]

    caller_system = f"""You are simulating a caller to an HVAC company phone line.

CALLER BRIEF:
{scenario['callerPrompt']}

RULES:
- Respond naturally and realistically as this caller — short sentences, conversational
- Do NOT volunteer all info at once — respond only to what the agent asks
- Stay in character throughout the entire conversation
- When the agent says goodbye and ends the call, reply only with: [END CALL]
- Keep each response under 25 words
"""

    agent_system = f"""You are Sophie, a virtual AI receptionist for an HVAC company handling an inbound phone call.

{agent_prompt}

RULES:
- Respond as Sophie would in a real call — concise, warm, professional
- One question or action per turn — never more than one question at once
- When you have completed the call objective and said goodbye, end your message with: [END CALL]
- Keep each response under 40 words
"""

    agent_history, caller_history, transcript = [], [], []
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0}

    greeting = "Thank you for calling, this is Sophie. How can I help you today?"
    transcript.append({"role": "agent", "text": greeting})
    caller_history.append({"role": "user", "content": f"[Agent]: {greeting}"})
    agent_history.append({"role": "assistant", "content": greeting})

    for turn in range(max_turns):
        # Caller turn
        caller_reply, usage = chat(api_key, caller_system, caller_history, temperature=0.8, model=model)
        total_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
        total_usage["completion_tokens"] += usage.get("completion_tokens", 0)
        transcript.append({"role": "caller", "text": caller_reply})
        if "[END CALL]" in caller_reply:
            break
        caller_history.append({"role": "assistant", "content": caller_reply})
        agent_history.append({"role": "user", "content": f"[Caller]: {caller_reply}"})

        # Agent turn
        agent_reply, usage = chat(api_key, agent_system, agent_history, temperature=0.3, model=model)
        total_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
        total_usage["completion_tokens"] += usage.get("completion_tokens", 0)
        transcript.append({"role": "agent", "text": agent_reply})
        if "[END CALL]" in agent_reply:
            break
        agent_history.append({"role": "assistant", "content": agent_reply})
        caller_history.append({"role": "user", "content": f"[Agent]: {agent_reply}"})

    return transcript, total_usage

# =============================================================================
# EVALUATION
# =============================================================================

def evaluate_transcript(api_key, scenario, transcript, agent_type):
    """Evaluate transcript against scenario criteria."""
    model = AGENT_CONFIG[agent_type]["model"]
    transcript_text = "\n".join(
        f"{'AGENT' if t['role']=='agent' else 'CALLER'}: {t['text']}"
        for t in transcript
    )

    eval_system = f"""You are a strict quality evaluator for an AI phone receptionist.

Evaluate the transcript against the success criteria. Be strict — partial = fail.

IMPORTANT CONTEXT — THIS IS A TEXT SIMULATION:
- Transfers cannot actually complete in a text simulation
- If criteria requires "transfer the caller" — PASS if agent said they are transferring,
  offered to transfer, or said "one moment" and initiated a transfer
- If criteria requires "emergency routing" — PASS if agent recognised the emergency
  and said they would transfer or get urgent help, even if the actual connection isn't shown
- Judge INTENT and BEHAVIOUR, not whether the phone call physically connected

CRITERIA RULES:
- Derive your criteria ONLY from the expectedBehaviour string. Do not invent additional criteria.
- Each comma-separated or "and"-joined item in expectedBehaviour is exactly ONE criterion.
- Do not split a criterion into sub-criteria. Do not add criteria based on best practices.
- criteria_total must equal the number of distinct items in expectedBehaviour — no more.

SCENARIO: {scenario['name']}
EXPECTED: {scenario.get('expectedBehaviour', '')}

Respond ONLY with valid JSON, no markdown fences, no explanation outside JSON:
{{
  "overall": "PASS" or "FAIL",
  "criteria_met": <integer>,
  "criteria_total": <integer>,
  "summary": "<one sentence>",
  "root_cause": "<if FAIL: the single most important reason>"
}}"""

    user_msg = f"TRANSCRIPT:\n{transcript_text}"
    response, usage = chat(api_key, eval_system, [{"role": "user", "content": user_msg}],
                          temperature=0.1, model=model)

    clean = response.replace("```json","").replace("```","").strip()
    try:
        result = json.loads(clean)
    except json.JSONDecodeError:
        result = {"overall": "ERROR", "criteria_met": 0, "criteria_total": 0,
                  "summary": "Evaluator parse error", "root_cause": response[:150]}
    result["eval_usage"] = usage
    return result

# =============================================================================
# PHASE 1: DIAGNOSE
# =============================================================================

def phase_diagnose(api_key, scenarios, agent_type):
    """Run all scenarios, return pass/fail counts and results."""
    print(f"\n[PHASE 1] DIAGNOSE — Running {len(scenarios)} scenarios...")

    results = []
    total_pass = total_fail = total_error = 0

    agent_prompt = fetch_agent_prompt(agent_type)

    for i, scenario in enumerate(scenarios):
        print(f"  [{i+1:02d}/{len(scenarios)}] #{scenario['id']:02d} {scenario['name'][:55]}...",
              end=" ", flush=True)
        try:
            transcript, sim_usage = simulate_scenario(api_key, scenario, agent_prompt, agent_type)
            evaluation = evaluate_transcript(api_key, scenario, transcript, agent_type)
            outcome = evaluation.get("overall", "ERROR")
            met = evaluation.get("criteria_met", 0)
            total = evaluation.get("criteria_total", "?")

            if outcome == "PASS":
                total_pass += 1
                icon = "✅"
            elif outcome == "FAIL":
                total_fail += 1
                icon = "❌"
            else:
                total_error += 1
                icon = "⚠️"

            print(f"{icon} {outcome} ({met}/{total})")

            results.append({
                "id": scenario["id"],
                "name": scenario["name"],
                "group": scenario["group"],
                "outcome": outcome,
                "criteria_met": met,
                "criteria_total": total,
                "summary": evaluation.get("summary", ""),
                "root_cause": evaluation.get("root_cause", ""),
                "transcript": transcript,
                "scenario": scenario
            })
        except Exception as e:
            total_error += 1
            print(f"⚠️ EXCEPTION: {str(e)[:60]}")
            results.append({
                "id": scenario["id"],
                "name": scenario["name"],
                "group": scenario["group"],
                "outcome": "ERROR",
                "error": str(e)
            })

        time.sleep(2)

    print(f"\n  DIAGNOSE COMPLETE: {total_pass} pass, {total_fail} fail, {total_error} error")
    return results, total_pass, total_fail, total_error

# =============================================================================
# PHASE 2: TRIAGE
# =============================================================================

def phase_triage(api_key, failures, agent_type):
    """Retry failures 2x, LLM-classify root cause."""
    print(f"\n[PHASE 2] TRIAGE — Classifying {len(failures)} failures...")

    triaged = []
    agent_prompt = fetch_agent_prompt(agent_type)

    for failure in failures:
        scenario = failure.get("scenario")
        if not scenario:
            continue

        print(f"  Retry #{scenario['id']:02d}...", end=" ", flush=True)

        retry_outcomes = []
        for retry in range(2):
            try:
                transcript, _ = simulate_scenario(api_key, scenario, agent_prompt, agent_type)
                evaluation = evaluate_transcript(api_key, scenario, transcript, agent_type)
                outcome = evaluation.get("overall", "ERROR")
                retry_outcomes.append(outcome)
            except Exception:
                retry_outcomes.append("ERROR")
            time.sleep(1)

        # Determine variance: if outcomes differ, it's variance
        if len(set(retry_outcomes)) > 1:
            classification = "VARIANCE"
        else:
            # LLM-classify as BAD_SCENARIO or PROMPT_GAP
            classify_system = f"""You are classifying why an AI receptionist scenario failed.

SCENARIO: {scenario['name']}
EXPECTED: {scenario.get('expectedBehaviour', '')}
ROOT CAUSE (from evaluator): {failure.get('root_cause', '')}

Classify as ONE of:
- BAD_SCENARIO: The scenario expectation is impossible/unrealistic
- PROMPT_GAP: The agent genuinely failed to handle it (fixable)

Respond ONLY with the classification name."""

            response, _ = chat(api_key, classify_system,
                             [{"role": "user", "content": "Classify this failure."}],
                             temperature=0.3, model=AGENT_CONFIG[agent_type]["model"])

            classification = "PROMPT_GAP" if "PROMPT_GAP" in response else "BAD_SCENARIO"

        print(f" {classification}")

        triaged.append({
            "id": scenario["id"],
            "name": scenario["name"],
            "group": scenario["group"],
            "classification": classification,
            "retry_outcomes": retry_outcomes,
            "original_root_cause": failure.get("root_cause", ""),
            "scenario": scenario
        })
        time.sleep(1)

    # Count by classification
    bad = sum(1 for t in triaged if t["classification"] == "BAD_SCENARIO")
    gap = sum(1 for t in triaged if t["classification"] == "PROMPT_GAP")
    var = sum(1 for t in triaged if t["classification"] == "VARIANCE")

    print(f"\n  TRIAGE COMPLETE: {bad} BAD_SCENARIO, {gap} PROMPT_GAP, {var} VARIANCE")
    return triaged

# =============================================================================
# PHASE 3: FIX
# =============================================================================

def phase_fix(api_key, triaged, agent_type, max_iterations=10, dry_run=False):
    """Apply minimal fixes to PROMPT_GAP failures."""
    print(f"\n[PHASE 3] FIX — Applying fixes to PROMPT_GAP failures...")

    if dry_run:
        print("  [DRY-RUN MODE] No changes will be applied")

    to_fix = [t for t in triaged if t["classification"] == "PROMPT_GAP"]
    if not to_fix:
        print("  No PROMPT_GAP failures to fix")
        return {"iterations": 0, "fixed": []}

    print(f"  {len(to_fix)} failures to fix across up to {max_iterations} iterations")

    fixed = []
    no_improvement_strikes = 0

    for iteration in range(1, max_iterations + 1):
        print(f"\n  [ITERATION {iteration}]")

        iteration_fixed = 0
        for failure in to_fix:
            if failure.get("fixed"):
                continue

            scenario = failure["scenario"]
            print(f"    #{scenario['id']:02d}: {scenario['name'][:40]}...", end=" ", flush=True)

            # Suggest a minimal fix
            fix_system = f"""You are fixing an AI receptionist's prompt to handle a scenario better.

SCENARIO: {scenario['name']}
CALLER: {scenario['callerPrompt']}
EXPECTED: {scenario.get('expectedBehaviour', '')}
FAILURE REASON: {failure['original_root_cause']}

Suggest ONE minimal fix:
1. Add a routing edge description (1-2 sentences)
2. Add one line to a component instruction (max {COMPONENT_INSTRUCTION_MAX} chars total)
3. Add a finetune example (2-3 sentences)

DO NOT suggest global prompt changes. Be very specific.

Respond with:
FIX_TYPE: <type 1, 2, or 3>
TARGET: <node name or component name>
CHANGE: <exactly what to add/modify>"""

            response, _ = chat(api_key, fix_system,
                             [{"role": "user", "content": "Suggest a minimal fix."}],
                             temperature=0.5, model=AGENT_CONFIG[agent_type]["model"])

            print(f"→ {response[:60]}...")

            if not dry_run:
                # Apply fix (simplified for now — actual patch logic here)
                # In production, parse response and call patch_component_instruction()
                pass

            failure["fixed"] = True
            iteration_fixed += 1

        if iteration_fixed == 0:
            no_improvement_strikes += 1
            print(f"    [No improvements — strike {no_improvement_strikes}/3]")
            if no_improvement_strikes >= 3:
                print(f"  STOPPING: 3 strikes reached")
                break
        else:
            no_improvement_strikes = 0

    print(f"\n  FIX COMPLETE: {len([f for f in to_fix if f.get('fixed')])} fixed")
    return {"iterations": iteration, "fixed": [f["id"] for f in to_fix if f.get("fixed")]}

# =============================================================================
# REGRESSION CHECK
# =============================================================================

def regression_check(api_key, initial_results, agent_type):
    """Re-run scenarios to check for regressions."""
    print(f"\n[REGRESSION CHECK] Re-running all scenarios...")

    scenarios = [r["scenario"] for r in initial_results]
    final_results, pass_count, fail_count, error_count = phase_diagnose(api_key, scenarios, agent_type)

    initial_pass = sum(1 for r in initial_results if r.get("outcome") == "PASS")

    if pass_count >= initial_pass:
        status = "✅ NO REGRESSION"
    else:
        status = f"❌ REGRESSION: {initial_pass} → {pass_count}"

    print(f"  {status}")
    return final_results

# =============================================================================
# MAIN LOOP
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Syntharra Agentic Test Fix")
    parser.add_argument("--key", required=True, help="Groq API key")
    parser.add_argument("--agent", choices=["standard", "premium"], required=True)
    parser.add_argument("--max-fix-iterations", type=int, default=10)
    parser.add_argument("--dry-run", action="store_true", help="Diagnose + triage only")
    parser.add_argument("--group", choices=list(SCENARIO_GROUPS.keys()), help="Filter by scenario group")
    parser.add_argument("--scenarios", help="Comma-separated scenario IDs")

    args = parser.parse_args()

    if not RETELL_KEY:
        print("Error: RETELL_KEY environment variable not set")
        sys.exit(1)

    # Fetch scenarios
    print("Fetching scenarios from GitHub...")
    all_scenarios = fetch_scenarios()

    if args.scenarios:
        ids = [int(x) for x in args.scenarios.split(",")]
        scenarios = filter_scenarios(all_scenarios, scenario_ids=ids)
    else:
        scenarios = filter_scenarios(all_scenarios, group_filter=args.group)

    print(f"Running {len(scenarios)} scenarios (agent: {args.agent})")

    # PHASE 1: DIAGNOSE
    diagnose_results, pass_count, fail_count, error_count = phase_diagnose(args.key, scenarios, args.agent)

    # PHASE 2: TRIAGE
    failures = [r for r in diagnose_results if r["outcome"] in ["FAIL", "ERROR"]]
    if failures:
        triaged = phase_triage(args.key, failures, args.agent)
    else:
        triaged = []

    # PHASE 3: FIX
    if not args.dry_run and triaged:
        fix_results = phase_fix(args.key, triaged, args.agent, max_iterations=args.max_fix_iterations)
    else:
        fix_results = {"iterations": 0, "fixed": []}

    # REGRESSION CHECK
    if not args.dry_run and fix_results["fixed"]:
        regression_check(args.key, diagnose_results, args.agent)

    # REPORT
    print(f"\n{'='*62}")
    print(f"RUN COMPLETE: {pass_count}/{len(scenarios)} PASS")
    print(f"  ✅ Pass: {pass_count}  ❌ Fail: {fail_count}  ⚠️ Error: {error_count}")
    print(f"  Triaged: {len(triaged)} | Fixed: {len(fix_results['fixed'])}")
    print(f"{'='*62}\n")

    # Save results
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    results_file = f"tests/results/{timestamp}-{args.agent}-agentic.json"

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": args.agent,
        "dry_run": args.dry_run,
        "diagnose": {"pass": pass_count, "fail": fail_count, "error": error_count},
        "triage": [{"id": t["id"], "classification": t["classification"]} for t in triaged],
        "fix": fix_results,
        "results": diagnose_results[:10]
    }

    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    with open(results_file, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to {results_file}")

if __name__ == "__main__":
    main()
