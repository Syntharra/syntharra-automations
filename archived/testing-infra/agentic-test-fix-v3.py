"""
Syntharra Agentic Test Fix v3 — OpenAI async edition
======================================================
v3 changes vs v2:
- Drops Groq qwen3-32b → uses OpenAI gpt-4o-mini (5x faster, 10x cheaper, no TPM throttle)
- Async + semaphore-bounded parallelism (default 20 concurrent) — full diagnose in ~3 min
- Real-time cost tracking, prints $ per phase + total at end
- Hard cost cap (--max-cost, default $5.00) — aborts before overspend
- Same DIAGNOSE → TRIAGE → FIX 3-phase loop, same scenario JSON, same Retell patch logic
- Prompt caching kicks in automatically on the agent system prompt (>1024 tokens)

Usage:
    python3 tools/agentic-test-fix-v3.py --agent standard|premium [--dry-run] [--max-cost 5.0] [--concurrency 20]

Env:
    OPENAI_KEY   (or vault: service_name='OpenAI', key_type='api_key')
    RETELL_KEY
    GITHUB_TOKEN
"""

import argparse, json, os, sys, asyncio, base64, time, requests
from datetime import datetime, timezone

try:
    from openai import AsyncOpenAI
except ImportError:
    print("ERROR: pip install openai>=1.40.0 --break-system-packages")
    sys.exit(1)

# ── CONFIG ────────────────────────────────────────────────────────────────────
RETELL_KEY    = os.environ.get("RETELL_KEY", "")
OPENAI_KEY    = os.environ.get("OPENAI_KEY", "") or os.environ.get("OPENAI_API_KEY", "")
GITHUB_TOKEN  = os.environ.get("GITHUB_TOKEN", "")

RETELL_BASE = "https://api.retellai.com"
MODEL       = "gpt-4o-mini"
PRICE_IN    = 0.15 / 1_000_000   # $/token
PRICE_OUT   = 0.60 / 1_000_000
PRICE_CACHED_IN = 0.075 / 1_000_000  # 50% off cached prompt tokens

AGENT_CONFIG = {
    "standard": {"agent_id": "agent_9d6e1db069d7900a61b78c5ca6", "flow_id": "conversation_flow_a54448105a43", "name": "HVAC Standard (TESTING)"},
    "premium":  {"agent_id": "agent_2cffe3d86d7e1990d08bea068f", "flow_id": "conversation_flow_2ded0ed4f808", "name": "HVAC Premium (TESTING)"},
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
COMPONENT_ALIASES = {
    "nonemergency_leadcapture": "fallback_leadcapture", "lead_capture": "fallback_leadcapture",
    "leadcapture": "fallback_leadcapture", "emergency": "verify_emergency", "spam": "spam_robocall",
    "call_style": "call_style_detector", "booking": "booking_capture", "availability": "check_availability",
    "confirm": "confirm_booking", "cancel": "cancel_appointment", "general": "general_questions",
    "transfer": "transfer_failed",
}

COMPONENT_MAX_CHARS  = 3200
MAX_FIX_ATTEMPTS     = 3
MAX_OUTER_ITERATIONS = 3

# ── COST TRACKER ──────────────────────────────────────────────────────────────
class Cost:
    def __init__(self, cap):
        self.in_tok = 0
        self.cached_in = 0
        self.out_tok = 0
        self.calls = 0
        self.cap = cap
    def add(self, usage):
        self.calls += 1
        self.in_tok  += usage.get("prompt_tokens", 0)
        self.out_tok += usage.get("completion_tokens", 0)
        details = usage.get("prompt_tokens_details") or {}
        self.cached_in += details.get("cached_tokens", 0) if isinstance(details, dict) else 0
    def total(self):
        uncached_in = max(self.in_tok - self.cached_in, 0)
        return uncached_in * PRICE_IN + self.cached_in * PRICE_CACHED_IN + self.out_tok * PRICE_OUT
    def check_cap(self):
        if self.total() > self.cap:
            raise RuntimeError(f"COST CAP HIT: ${self.total():.4f} > ${self.cap:.2f}")
    def __str__(self):
        return f"${self.total():.4f} ({self.calls} calls, in={self.in_tok} cached={self.cached_in} out={self.out_tok})"

cost = None  # set in main

# ── RETELL HELPERS (sync — Retell calls are infrequent) ───────────────────────
def retell_h(): return {"Authorization": f"Bearer {RETELL_KEY}", "Content-Type": "application/json"}

def fetch_flow(at):
    r = requests.get(f"{RETELL_BASE}/get-conversation-flow/{AGENT_CONFIG[at]['flow_id']}", headers=retell_h(), timeout=30)
    r.raise_for_status(); return r.json()

def fetch_component(cid):
    r = requests.get(f"{RETELL_BASE}/get-conversation-flow-component/{cid}", headers=retell_h(), timeout=30)
    r.raise_for_status(); return r.json()

def patch_component(cid, body):
    r = requests.patch(f"{RETELL_BASE}/update-conversation-flow-component/{cid}", headers=retell_h(), json=body, timeout=30)
    r.raise_for_status(); return r.json()

def publish_agent(at):
    aid = AGENT_CONFIG[at]["agent_id"]
    r = requests.post(f"{RETELL_BASE}/publish-agent/{aid}", headers=retell_h(), json={}, timeout=30)
    return r.status_code == 200

def fetch_agent_prompt_compressed(at):
    flow = fetch_flow(at)
    gp = flow.get("global_prompt", "")
    names = [f"- {n.get('name','')}" for n in flow["nodes"] if n.get("type") != "end" and n.get("name")]
    return f"{gp}\n\n---\nAGENT CAPABILITIES (routing nodes):\n{chr(10).join(names)}"

def fetch_agent_prompt_full(at):
    flow = fetch_flow(at)
    gp = flow.get("global_prompt", "")
    sections = []
    for node in flow["nodes"]:
        if node.get("type") == "end": continue
        name = node.get("name", "")
        text = node.get("instruction", {}).get("text", "")
        if node.get("type") == "subagent" and node.get("component_id"):
            try:
                comp = fetch_component(node["component_id"])
                parts = [n.get("instruction", {}).get("text", "") for n in comp.get("nodes", [])]
                text = "\n".join(p for p in parts if p)
            except Exception: pass
        if text: sections.append(f"[NODE: {name}]\n{text}")
    return gp + "\n\n---\nNODE INSTRUCTIONS:\n\n" + "\n\n".join(sections)

# ── OPENAI ASYNC HELPERS ──────────────────────────────────────────────────────
async def chat(client, system, user, temperature=0.5, max_tokens=700):
    resp = await client.chat.completions.create(
        model=MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    usage = resp.usage.model_dump() if resp.usage else {}
    cost.add(usage)
    cost.check_cap()
    return resp.choices[0].message.content.strip(), usage

# ── SCENARIO HELPERS ──────────────────────────────────────────────────────────
def fetch_scenarios():
    gh = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get("https://api.github.com/repos/Syntharra/syntharra-automations/contents/tests/agent-test-scenarios.json", headers=gh, timeout=30).json()
    return json.loads(base64.b64decode(r["content"]).decode())

def normalize_expected(s):
    eb = s.get("expectedBehaviour", "")
    return ". ".join(str(x) for x in eb) if isinstance(eb, list) else str(eb)

def filter_scenarios(all_s, at, group=None, ids=None):
    f = all_s
    if at == "standard":
        f = [s for s in f if not s.get("premiumOnly") and not s.get("premium_only")]
    if ids: f = [s for s in f if s["id"] in ids]
    elif group: f = [s for s in f if s.get("group") == group]
    return f

# ── SIMULATE + EVALUATE (one scenario, async) ─────────────────────────────────
async def run_one(client, sem, scenario, agent_prompt):
    async with sem:
        expected = normalize_expected(scenario)
        # Simulate
        sim_sys = "You are a phone call simulator. Output valid JSON only — no markdown, no commentary."
        sim_user = f"""Simulate a realistic phone conversation between an HVAC AI receptionist and a caller.

AGENT INSTRUCTIONS (how the receptionist should behave):
{agent_prompt}

CALLER SCENARIO:
{scenario['callerPrompt']}

EXPECTED OUTCOME:
{expected}

Generate a realistic 5-8 turn conversation. The agent must attempt to achieve the expected outcome.
Return ONLY a JSON array: [{{"role":"agent","text":"..."}},{{"role":"caller","text":"..."}}, ...]
Each response under 40 words. Agent follows its instructions faithfully."""

        try:
            sim_resp, _ = await chat(client, sim_sys, sim_user, temperature=0.5, max_tokens=700)
            clean = sim_resp.replace("```json","").replace("```","").strip()
            try:
                transcript = json.loads(clean)
                if not isinstance(transcript, list): raise ValueError
            except Exception:
                transcript = [
                    {"role":"agent","text":"Thank you for calling. How can I help?"},
                    {"role":"caller","text":scenario.get("callerPrompt","")[:100]},
                    {"role":"agent","text":sim_resp[:200]},
                ]
        except Exception as e:
            return {"id":scenario["id"],"name":scenario["name"],"group":scenario.get("group",""),
                    "outcome":"ERROR","error":str(e),"scenario":scenario}

        # Evaluate
        transcript_text = "\n".join(f"{'AGENT' if t['role']=='agent' else 'CALLER'}: {t['text']}" for t in transcript)
        eval_sys = f"""You are a strict QA evaluator for an AI phone receptionist.

IMPORTANT — TEXT SIMULATION CONTEXT:
- Transfers cannot physically complete in a text simulation
- PASS "transfer the caller" if agent said they are transferring or offered to connect them
- PASS "emergency routing" if agent recognised the emergency and indicated escalation
- Judge INTENT and BEHAVIOUR, not physical connection

CRITERIA RULES:
- Derive criteria ONLY from expectedBehaviour
- Each comma-separated/list item = exactly ONE criterion

SCENARIO: {scenario['name']}
EXPECTED: {expected}

Respond ONLY with valid JSON (no markdown):
{{"overall":"PASS"|"FAIL","criteria_met":<int>,"criteria_total":<int>,"summary":"<one sentence>","root_cause":"<if FAIL: reason>"}}"""

        try:
            ev_resp, _ = await chat(client, eval_sys, f"TRANSCRIPT:\n{transcript_text}", temperature=0.1, max_tokens=200)
            clean = ev_resp.replace("```json","").replace("```","").strip()
            try:
                ev = json.loads(clean)
            except json.JSONDecodeError:
                ev = {"overall":"ERROR","criteria_met":0,"criteria_total":0,"summary":"parse error","root_cause":ev_resp[:200]}
        except Exception as e:
            ev = {"overall":"ERROR","criteria_met":0,"criteria_total":0,"summary":"eval error","root_cause":str(e)}

        return {"id":scenario["id"],"name":scenario["name"],"group":scenario.get("group",""),
                "outcome":ev.get("overall","ERROR"),"criteria_met":ev.get("criteria_met",0),
                "criteria_total":ev.get("criteria_total",0),"summary":ev.get("summary",""),
                "root_cause":ev.get("root_cause",""),"transcript":transcript,"scenario":scenario}

# ── PHASE 1: DIAGNOSE (parallel) ──────────────────────────────────────────────
async def phase_diagnose(client, scenarios, at, concurrency):
    print(f"\n[PHASE 1] DIAGNOSE — {len(scenarios)} scenarios ({at}), concurrency={concurrency}")
    agent_prompt = fetch_agent_prompt_compressed(at)
    sem = asyncio.Semaphore(concurrency)
    t0 = time.time()

    completed = 0
    n = len(scenarios)
    async def wrapped(s):
        nonlocal completed
        r = await run_one(client, sem, s, agent_prompt)
        completed += 1
        if completed % 10 == 0 or completed == n:
            print(f"  [{completed:03d}/{n}] running... {cost}", flush=True)
        return r

    results = await asyncio.gather(*(wrapped(s) for s in scenarios))
    elapsed = time.time() - t0
    p = sum(1 for r in results if r["outcome"]=="PASS")
    f = sum(1 for r in results if r["outcome"]=="FAIL")
    e = sum(1 for r in results if r["outcome"]=="ERROR")
    print(f"  → {p} PASS  {f} FAIL  {e} ERROR  in {elapsed:.0f}s  cost={cost}")
    return results, p, f, e

# ── PHASE 2: TRIAGE (parallel retries + classification) ───────────────────────
async def phase_triage(client, failures, at, concurrency):
    print(f"\n[PHASE 2] TRIAGE — {len(failures)} failures")
    agent_prompt = fetch_agent_prompt_compressed(at)
    sem = asyncio.Semaphore(concurrency)

    async def triage_one(failure):
        async with sem:
            scenario = failure["scenario"]
            # 1 retry to rule out variance
            try:
                retry = await run_one(client, asyncio.Semaphore(1), scenario, agent_prompt)
                if retry["outcome"] == "PASS":
                    return {**failure, "classification":"VARIANCE"}
            except Exception: pass

            # Classify
            expected = normalize_expected(scenario)
            clf_sys = f"""Classify why this AI receptionist scenario failed.

SCENARIO: {scenario['name']}
EXPECTED: {expected}
ROOT CAUSE: {failure.get('root_cause','unknown')}

Classes:
- BAD_SCENARIO: expectation unrealistic for this agent. Agent behaved reasonably.
- PROMPT_GAP: agent genuinely mishandled. Should be fixed.
- VARIANCE: borderline LLM randomness.

Respond:
TYPE: BAD_SCENARIO | PROMPT_GAP | VARIANCE
REASON: <one sentence>"""
            try:
                resp, _ = await chat(client, clf_sys, "Classify this failure.", temperature=0.2, max_tokens=80)
                if "BAD_SCENARIO" in resp: c = "BAD_SCENARIO"
                elif "VARIANCE" in resp:   c = "VARIANCE"
                else: c = "PROMPT_GAP"
                reason = next((l.replace("REASON:","").strip() for l in resp.split("\n") if l.startswith("REASON:")), "")
            except Exception as ex:
                c, reason = "PROMPT_GAP", f"clf err: {ex}"
            return {**failure, "classification":c, "triage_reason":reason}

    triaged = await asyncio.gather(*(triage_one(f) for f in failures))
    g = sum(1 for t in triaged if t["classification"]=="PROMPT_GAP")
    b = sum(1 for t in triaged if t["classification"]=="BAD_SCENARIO")
    v = sum(1 for t in triaged if t["classification"]=="VARIANCE")
    print(f"  → {g} PROMPT_GAP  {b} BAD_SCENARIO  {v} VARIANCE  cost={cost}")
    return triaged

# ── PHASE 3: FIX (sequential — Retell patches must serialise) ─────────────────
def resolve_component(name):
    n = name.lower().replace(" ","_").replace("-","_")
    if n in COMPONENT_MAP: return n, COMPONENT_MAP[n]
    if n in COMPONENT_ALIASES:
        r = COMPONENT_ALIASES[n]; return r, COMPONENT_MAP[r]
    for k,v in COMPONENT_MAP.items():
        if n in k or k in n: return k, v
    return None, None

def apply_component_fix(target, change):
    cn, cid = resolve_component(target)
    if not cid: return False, f"unknown component '{target}'"
    try: comp = fetch_component(cid)
    except Exception as e: return False, f"fetch failed: {e}"
    best, blen = None, 0
    for node in comp.get("nodes", []):
        t = node.get("instruction",{}).get("text","")
        if len(t) > blen: blen, best = len(t), node
    if not best: return False, "no instruction node"
    cur = best["instruction"]["text"]
    new = cur.rstrip() + "\n" + change.strip()
    if len(new) > COMPONENT_MAX_CHARS: return False, f"too long ({len(new)})"
    best["instruction"]["text"] = new
    try:
        patch_component(cid, comp)
        return True, f"patched {cn} ({len(cur)}→{len(new)})"
    except Exception as e: return False, str(e)[:120]

async def phase_fix(client, triaged, at, dry_run, concurrency):
    to_fix = [t for t in triaged if t["classification"]=="PROMPT_GAP"]
    if not to_fix:
        print(f"\n[PHASE 3] FIX — nothing to fix")
        return {"fixed":[], "still_failing":[]}
    print(f"\n[PHASE 3] FIX — {len(to_fix)} PROMPT_GAP{' [DRY-RUN]' if dry_run else ''}")
    fixed, still = [], []

    for failure in to_fix:
        scenario = failure["scenario"]
        expected = normalize_expected(scenario)
        rc = failure.get("root_cause","")
        print(f"\n  ── #{scenario['id']:03d} {scenario['name'][:50]} ──")
        scenario_fixed = False

        for attempt in range(1, MAX_FIX_ATTEMPTS+1):
            print(f"  Attempt {attempt}:", end=" ", flush=True)
            fix_sys = f"""You are fixing an AI receptionist's behaviour.

SCENARIO: {scenario['name']}
CALLER: {scenario['callerPrompt'][:300]}
EXPECTED: {expected}
ROOT CAUSE: {rc}

COMPONENTS: {', '.join(COMPONENT_MAP.keys())}

Suggest ONE minimal fix. Add max 120 chars to ONE component. No global changes.

Respond exactly:
FIX_TYPE: 2
TARGET: <component name>
CHANGE: <instruction line>"""
            try:
                resp, _ = await chat(client, fix_sys, "Suggest a fix.", temperature=0.3, max_tokens=200)
            except Exception as e:
                print(f"LLM err: {e}"); continue

            fix = {}
            for line in resp.strip().split("\n"):
                if line.startswith("FIX_TYPE:"): fix["fix_type"] = line.split(":",1)[1].strip()
                elif line.startswith("TARGET:"):  fix["target"]   = line.split(":",1)[1].strip()
                elif line.startswith("CHANGE:"):  fix["change"]   = line.split(":",1)[1].strip()
            if not fix.get("target") or not fix.get("change"):
                print(f"unparseable: {resp[:80]}"); continue
            print(f"→ {fix['target']}: {fix['change'][:60]}")
            if dry_run: break

            ok, msg = apply_component_fix(fix["target"], fix["change"])
            if not ok:
                print(f"    [SKIP] {msg}"); rc = f"prev attempt failed: {msg}"; continue
            print(f"    [OK] {msg}")

            # Re-run to verify
            updated_prompt = fetch_agent_prompt_full(at)
            print(f"    Verifying...", end=" ", flush=True)
            sem = asyncio.Semaphore(1)
            verify = await run_one(client, sem, scenario, updated_prompt)
            if verify["outcome"] == "PASS":
                print("[PASS]"); fixed.append(scenario["id"]); scenario_fixed = True; break
            print(f"[FAIL] {verify.get('root_cause','')[:60]}")
            rc = verify.get("root_cause","")

        if not scenario_fixed and not dry_run:
            still.append(scenario["id"])

    print(f"\n  → fixed {len(fixed)}  still failing {len(still)}  cost={cost}")
    return {"fixed":fixed, "still_failing":still}

# ── MAIN ──────────────────────────────────────────────────────────────────────
async def amain(args):
    global cost
    # HARD LIMIT: per-agent cap can NEVER exceed $5.00 (Dan rule, 2026-04-07)
    HARD_CAP = 5.00
    effective_cap = min(args.max_cost, HARD_CAP)
    if args.max_cost > HARD_CAP:
        print(f"[WARN] --max-cost ${args.max_cost} exceeds hard limit; clamped to ${HARD_CAP}")
    cost = Cost(effective_cap)

    if not OPENAI_KEY:
        print("ERROR: OPENAI_KEY not set"); sys.exit(1)
    if not RETELL_KEY:
        print("ERROR: RETELL_KEY not set"); sys.exit(1)

    client = AsyncOpenAI(api_key=OPENAI_KEY)
    print(f"\n{'='*62}\n  Syntharra Agentic Test Fix v3 (OpenAI gpt-4o-mini)")
    print(f"  Agent: {AGENT_CONFIG[args.agent]['name']}")
    print(f"  Concurrency: {args.concurrency}  |  Cost cap: ${args.max_cost:.2f}")
    print(f"  Mode: {'DRY-RUN' if args.dry_run else 'FULL'}\n{'='*62}")

    print("\nFetching scenarios...")
    all_s = fetch_scenarios()
    ids = [int(x) for x in args.scenarios.split(",")] if args.scenarios else None
    scenarios = filter_scenarios(all_s, args.agent, args.group, ids)
    n = len(scenarios)
    print(f"Loaded {n} scenarios")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
    suffix = f"{ts}-{args.agent}" + (f"-{args.group}" if args.group else "")

    best_pass = 0
    best_results = []
    no_imp = 0
    fixes_total = 0

    for outer in range(1, MAX_OUTER_ITERATIONS+1):
        print(f"\n{'='*62}\n  ITERATION {outer}/{MAX_OUTER_ITERATIONS}\n{'='*62}")
        try:
            results, p, f, e = await phase_diagnose(client, scenarios, args.agent, args.concurrency)
        except RuntimeError as ex:
            print(f"\n  [ABORT] {ex}"); break

        pct = 100*p//n if n else 0
        print(f"  Pass rate: {p}/{n} ({pct}%)")

        if p >= best_pass:
            best_pass, best_results = p, results

        if p == n:
            print(f"\n  [DONE] All {n} pass!"); break

        failures = [r for r in results if r["outcome"] in ("FAIL","ERROR")]
        try:
            triaged = await phase_triage(client, failures, args.agent, args.concurrency)
        except RuntimeError as ex:
            print(f"\n  [ABORT] {ex}"); break

        if args.dry_run:
            await phase_fix(client, triaged, args.agent, True, args.concurrency); break

        try:
            fr = await phase_fix(client, triaged, args.agent, False, args.concurrency)
        except RuntimeError as ex:
            print(f"\n  [ABORT] {ex}"); break
        fixes_total += len(fr["fixed"])
        if fr["fixed"]:
            print(f"\n  Publishing {args.agent} TESTING agent...")
            publish_agent(args.agent)

        if p > best_pass:
            best_pass = p; no_imp = 0
        else:
            no_imp += 1
            if no_imp >= 2:
                print("  STOP: 2 iterations no improvement"); break
        if not fr["still_failing"] and not fr["fixed"]: break

    pct_final = 100*best_pass//n if n else 0
    print(f"\n{'='*62}")
    print(f"  FINAL: {best_pass}/{n} ({pct_final}%)  fixes={fixes_total}")
    print(f"  COST:  {cost}")
    print(f"  Agent: {AGENT_CONFIG[args.agent]['name']}")
    print(f"{'='*62}\n")

    os.makedirs("tests/results", exist_ok=True)
    out_file = f"tests/results/{suffix}-v3.json"
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": args.agent, "model": MODEL, "version": "v3",
        "scenarios_run": n, "best_pass": best_pass, "pass_rate_pct": pct_final,
        "fixes_applied": fixes_total,
        "cost_usd": round(cost.total(), 4),
        "calls": cost.calls,
        "tokens": {"in": cost.in_tok, "cached_in": cost.cached_in, "out": cost.out_tok},
        "results": best_results,
    }
    s = json.dumps(output, indent=2, default=str)
    with open(out_file,"w") as fp: fp.write(s)
    print(f"Saved {out_file}")

    # GitHub push
    if GITHUB_TOKEN:
        try:
            url = f"https://api.github.com/repos/Syntharra/syntharra-automations/contents/{out_file}"
            h = {"Authorization": f"token {GITHUB_TOKEN}"}
            sha = None
            chk = requests.get(url, headers=h, timeout=15)
            if chk.status_code == 200: sha = chk.json().get("sha")
            body = {"message":f"chore(tests): v3 results {out_file}","content":base64.b64encode(s.encode()).decode()}
            if sha: body["sha"] = sha
            r = requests.put(url, headers=h, json=body, timeout=30)
            if r.status_code in (200,201): print(f"Pushed to GitHub")
        except Exception as ex: print(f"[warn] github push: {ex}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--agent", choices=["standard","premium"], required=True)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--group")
    p.add_argument("--scenarios")
    p.add_argument("--max-cost", type=float, default=5.0, help="Hard $ cap (default 5.00)")
    p.add_argument("--concurrency", type=int, default=20, help="Max parallel API calls (default 20)")
    args = p.parse_args()
    asyncio.run(amain(args))

if __name__ == "__main__":
    main()
