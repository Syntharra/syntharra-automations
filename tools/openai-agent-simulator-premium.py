"""
Syntharra Agent Simulator — OpenAI powered
==========================================
Simulates caller conversations against the HVAC Premium agent prompt
and evaluates pass/fail per scenario. ~$0.002 per scenario vs $0.15 on Retell.

Usage:
    python3 simulator.py --key gsk_... --scenarios all
    python3 simulator.py --key gsk_... --scenarios 46,47,48,53,69,70
    python3 simulator.py --key gsk_... --group pricing_traps
    python3 simulator.py --key gsk_... --scenarios all --max-turns 8

Groups: core_flow, personalities, info_collection, pricing_traps, edge_cases, boundary_safety, premium_specific
"""

import argparse, json, os, sys, time, requests, base64
from datetime import datetime, timezone

RETELL_KEY   = os.environ.get("RETELL_KEY", "")  # export RETELL_KEY=... before running
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
TESTING_FLOW = "conversation_flow_2ded0ed4f808"
OPENAI_URL   = "https://api.groq.com/openai/v1/chat/completions"
MODEL        = "llama-3.3-70b-versatile"
MAX_TURNS    = 10

def fetch_agent_prompt():
    rh = {"Authorization": f"Bearer {RETELL_KEY}", "Content-Type": "application/json"}
    flow = requests.get(f"https://api.retellai.com/get-conversation-flow/{TESTING_FLOW}", headers=rh).json()
    global_prompt = flow["global_prompt"]
    node_sections = []
    for node in flow["nodes"]:
        name  = node.get("name", "")
        text  = node.get("instruction", {}).get("text", "")
        ntype = node.get("type", "")
        if text and ntype != "end":
            node_sections.append(f"[NODE: {name}]\n{text}")
    return global_prompt + "\n\n---\nNODE INSTRUCTIONS:\n\n" + "\n\n".join(node_sections)

def fetch_scenarios():
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN env var not set")
    gh = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(
        "https://api.github.com/repos/Syntharra/syntharra-automations/contents/tests/agent-test-scenarios.json",
        headers=gh
    ).json()
    return json.loads(base64.b64decode(r["content"]).decode())

def chat(api_key, system_prompt, messages, temperature=0.7, retries=6):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "temperature": temperature,
        "messages": [{"role": "system", "content": system_prompt}] + messages
    }
    time.sleep(1)  # 1s inter-call delay — caller uses fast model, lower token load
    for attempt in range(retries):
        try:
            r = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=30)
            if r.status_code == 429:
                wait = 30 * (attempt + 1)
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

def simulate_scenario(api_key, scenario, agent_prompt, max_turns=MAX_TURNS):
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
        caller_reply, usage = chat(api_key, caller_system, caller_history, temperature=0.8)
        total_usage["prompt_tokens"]     += usage.get("prompt_tokens", 0)
        total_usage["completion_tokens"] += usage.get("completion_tokens", 0)
        transcript.append({"role": "caller", "text": caller_reply})
        if "[END CALL]" in caller_reply:
            break
        caller_history.append({"role": "assistant", "content": caller_reply})
        agent_history.append({"role": "user", "content": f"[Caller]: {caller_reply}"})

        agent_reply, usage = chat(api_key, agent_system, agent_history, temperature=0.3)
        total_usage["prompt_tokens"]     += usage.get("prompt_tokens", 0)
        total_usage["completion_tokens"] += usage.get("completion_tokens", 0)
        transcript.append({"role": "agent", "text": agent_reply})
        if "[END CALL]" in agent_reply:
            break
        agent_history.append({"role": "assistant", "content": agent_reply})
        caller_history.append({"role": "user", "content": f"[Agent]: {agent_reply}"})

    return transcript, total_usage

def evaluate_transcript(api_key, scenario, transcript):
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
    response, usage = chat(api_key, eval_system, [{"role": "user", "content": user_msg}], temperature=0.1)

    clean = response.replace("```json","").replace("```","").strip()
    try:
        result = json.loads(clean)
    except json.JSONDecodeError:
        result = {"overall": "ERROR", "criteria_met": 0, "criteria_total": 0,
                  "summary": "Evaluator parse error", "root_cause": response[:150]}
    result["eval_usage"] = usage
    return result

def run_scenarios(api_key, scenarios_to_run, agent_prompt, max_turns=MAX_TURNS):
    results = []
    total_pass = total_fail = total_error = 0
    total_tokens = {"prompt_tokens": 0, "completion_tokens": 0}

    for i, scenario in enumerate(scenarios_to_run):
        print(f"  [{i+1:02d}/{len(scenarios_to_run)}] #{scenario['id']:02d} {scenario['name'][:55]}...", end=" ", flush=True)
        try:
            time.sleep(5)  # inter-scenario cooldown
        transcript, sim_usage = simulate_scenario(api_key, scenario, agent_prompt, max_turns)
            evaluation = evaluate_transcript(api_key, scenario, transcript)
            outcome = evaluation.get("overall", "ERROR")
            met     = evaluation.get("criteria_met", 0)
            total   = evaluation.get("criteria_total", "?")

            if outcome == "PASS":   total_pass  += 1; icon = "✅"
            elif outcome == "FAIL": total_fail  += 1; icon = "❌"
            else:                   total_error += 1; icon = "⚠️ "

            print(f"{icon} {outcome} ({met}/{total})")

            for k in total_tokens:
                total_tokens[k] += sim_usage.get(k, 0)
                total_tokens[k] += evaluation.get("eval_usage", {}).get(k, 0)

            results.append({
                "id": scenario["id"], "name": scenario["name"], "group": scenario["group"],
                "outcome": outcome, "criteria_met": met, "criteria_total": total,
                "summary": evaluation.get("summary",""), "root_cause": evaluation.get("root_cause",""),
                "transcript": transcript
            })
        except Exception as e:
            total_error += 1
            print(f"⚠️  EXCEPTION: {e}")
            results.append({"id": scenario["id"], "name": scenario["name"],
                            "group": scenario["group"], "outcome": "ERROR", "error": str(e)})
        time.sleep(2)  # Rate limit buffer

    return results, total_pass, total_fail, total_error, total_tokens

def print_report(results, total_pass, total_fail, total_error, total_tokens, run_label):
    total = total_pass + total_fail + total_error
    pass_rate = round(total_pass / total * 100, 1) if total > 0 else 0
    input_cost  = total_tokens["prompt_tokens"]     * 0.15 / 1_000_000
    output_cost = total_tokens["completion_tokens"] * 0.60 / 1_000_000
    total_cost  = input_cost + output_cost

    groups = {}
    for r in results:
        g = r.get("group","unknown")
        if g not in groups: groups[g] = {"pass":0,"fail":0,"error":0}
        key = r["outcome"].lower() if r["outcome"] in ["PASS","FAIL"] else "error"
        groups[g][key] += 1

    print(f"\n{'='*62}")
    print(f"RUN: {run_label}")
    print(f"Model: {MODEL} | Flow: {TESTING_FLOW}")
    print(f"{'='*62}")
    print(f"RESULT: {total_pass}/{total} PASS  —  {pass_rate}% pass rate")
    print(f"  ✅ Pass: {total_pass}  ❌ Fail: {total_fail}  ⚠️  Error: {total_error}")
    print(f"  💰 Cost: ${total_cost:.4f}  ({total_tokens['prompt_tokens']}+{total_tokens['completion_tokens']} tokens)\n")

    print("GROUP BREAKDOWN:")
    for group, counts in groups.items():
        t = counts["pass"] + counts["fail"] + counts["error"]
        rate = round(counts["pass"]/t*100) if t > 0 else 0
        bar = "█" * (rate//10) + "░" * (10 - rate//10)
        print(f"  {group:<25} {bar} {rate:3d}%  ({counts['pass']}/{t})")

    failures = [r for r in results if r["outcome"] in ["FAIL","ERROR"]]
    if failures:
        print(f"\nFAILURES ({len(failures)}):")
        for f in failures:
            rc = f.get("root_cause") or f.get("error","")
            met = f.get("criteria_met","?")
            tot = f.get("criteria_total","?")
            print(f"  #{f['id']:02d} [{f['outcome']}] {f['name']}")
            print(f"       Score: {met}/{tot} — {rc[:100]}")

def push_results(results, total_pass, total_fail, total_error, total_tokens, run_label):
    if not GITHUB_TOKEN:
        print("⚠️  No GITHUB_TOKEN — skipping push")
        return
    total = total_pass + total_fail + total_error
    pass_rate = round(total_pass/total*100, 1) if total > 0 else 0
    report = {
        "run_label": run_label,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "flow_id": TESTING_FLOW, "model": MODEL,
        "summary": {"total": total, "pass": total_pass, "fail": total_fail,
                    "error": total_error, "pass_rate": pass_rate,
                    "cost_usd": round((total_tokens["prompt_tokens"]*0.15 + total_tokens["completion_tokens"]*0.60)/1_000_000, 4),
                    "tokens": total_tokens},
        "failures": [r for r in results if r["outcome"] in ["FAIL","ERROR"]],
        "all_results": [{k:v for k,v in r.items() if k != "transcript"} for r in results]
    }
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")
    path = f"tests/results/simulator-{timestamp}-{run_label}.json"
    gh = {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}
    payload = {"message": f"Simulator: {run_label} — {pass_rate}% pass ({total_pass}/{total})",
               "content": base64.b64encode(json.dumps(report, indent=2).encode()).decode()}
    r = requests.put(f"https://api.github.com/repos/Syntharra/syntharra-automations/contents/{path}", headers=gh, json=payload)
    if r.status_code in (200,201):
        print(f"\n✅ Results → GitHub: {path}")
    else:
        print(f"\n⚠️  GitHub push failed: {r.status_code} — {r.json().get('message','')[:100]}")

def main():
    parser = argparse.ArgumentParser(description="Syntharra Agent Simulator")
    parser.add_argument("--key",       required=True,  help="Groq API key (gsk_...)")
    parser.add_argument("--scenarios", default="all",  help="Comma-separated IDs or 'all'")
    parser.add_argument("--group",     default=None,   help="Run a specific group only")
    parser.add_argument("--max-turns", type=int, default=MAX_TURNS)
    parser.add_argument("--label",     default=None)
    parser.add_argument("--no-push",   action="store_true")
    args = parser.parse_args()

    print("🔄 Fetching agent prompt from Retell...")
    agent_prompt = fetch_agent_prompt()
    print(f"   {len(agent_prompt)} chars loaded")

    print("🔄 Fetching scenarios...")
    all_scenarios = fetch_scenarios()
    # Premium simulator: include premiumOnly scenarios by default
    if args.group == "premium_specific":
        to_run = [s for s in all_scenarios if s.get("group") == "premium_specific"]
    elif args.group:
        to_run = [s for s in all_scenarios if s.get("group") == args.group]
    elif args.scenarios == "all":
        to_run = all_scenarios  # run all 95 including premium_specific
    else:
        ids = [int(x.strip()) for x in args.scenarios.split(",")]
        to_run = [s for s in all_scenarios if s["id"] in ids]

    if not to_run:
        print("❌ No matching scenarios"); sys.exit(1)

    run_label = args.label or f"run-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M')}"
    est_cost = len(to_run) * 0.002

    print(f"\n📋 Scenarios: {len(to_run)}  💰 Est. cost: ~${est_cost:.3f}  🏷️  {run_label}\n")
    print("▶  Running...\n")

    results, tp, tf, te, tokens = run_scenarios(args.key, to_run, agent_prompt, args.max_turns)
    print_report(results, tp, tf, te, tokens, run_label)

    if not args.no_push:
        push_results(results, tp, tf, te, tokens, run_label)

    sys.exit(0 if (tp/(tp+tf+te)*100 if tp+tf+te > 0 else 0) >= 90 else 1)

if __name__ == "__main__":
    main()
