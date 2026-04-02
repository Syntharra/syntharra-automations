"""
Syntharra Agent Simulator — OpenAI powered
==========================================
Simulates caller conversations against the HVAC Standard agent prompt
and evaluates pass/fail per scenario. ~$0.002 per scenario vs $0.15 on Retell.

Usage:
    python3 simulator.py --key sk-... --scenarios all
    python3 simulator.py --key sk-... --scenarios 81,82,83,89,90,91,92
    python3 simulator.py --key sk-... --group boundary_safety
    python3 simulator.py --key sk-... --scenarios all --max-turns 8

Groups: core_flow, service_variations, caller_personalities,
        info_collection, edge_cases, pricing_traps, boundary_safety
"""

import argparse
import json
import os
import sys
import time
import requests
import base64
from datetime import datetime

# ── CONFIG ───────────────────────────────────────────────────────────────────

RETELL_KEY = os.environ.get("RETELL_KEY", "key_0157d9401f66cfa1b51fadc66445")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")  # Set via env var or --github-token arg
TESTING_FLOW = "conversation_flow_5b98b76c8ff4"
OPENAI_URL   = "https://api.openai.com/v1/chat/completions"
MODEL        = "gpt-4o-mini"   # Cheap, fast, very capable — ~$0.15/1M input
MAX_TURNS    = 10              # Max back-and-forth turns per simulation

# ── FETCH AGENT PROMPT FROM RETELL ───────────────────────────────────────────

def fetch_agent_prompt():
    rh = {"Authorization": f"Bearer {RETELL_KEY}", "Content-Type": "application/json"}
    flow = requests.get(
        f"https://api.retellai.com/get-conversation-flow/{TESTING_FLOW}", headers=rh
    ).json()

    global_prompt = flow["global_prompt"]
    node_sections = []
    for node in flow["nodes"]:
        name  = node.get("name", "")
        instr = node.get("instruction", {})
        text  = instr.get("text", "")
        ntype = node.get("type", "")
        if text and ntype != "end":
            node_sections.append(f"[NODE: {name}]\n{text}")

    return global_prompt + "\n\n---\nNODE INSTRUCTIONS:\n\n" + "\n\n".join(node_sections)


# ── FETCH SCENARIOS FROM GITHUB ───────────────────────────────────────────────

def fetch_scenarios():
    gh = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(
        "https://api.github.com/repos/Syntharra/syntharra-automations/contents/tests/agent-test-scenarios.json",
        headers=gh
    ).json()
    return json.loads(base64.b64decode(r["content"]).decode())


# ── OPENAI CALL ───────────────────────────────────────────────────────────────

def chat(api_key, system_prompt, messages, temperature=0.7):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":  "application/json"
    }
    payload = {
        "model":       MODEL,
        "temperature": temperature,
        "messages":    [{"role": "system", "content": system_prompt}] + messages
    }
    r = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip(), data.get("usage", {})


# ── SIMULATE ONE SCENARIO ─────────────────────────────────────────────────────

def simulate_scenario(api_key, scenario, agent_prompt, max_turns=MAX_TURNS):
    """
    Runs a full simulated conversation between:
      - The AGENT (powered by the HVAC Standard prompt)
      - The CALLER (powered by the scenario callerPrompt)
    Returns the full transcript and token usage.
    """

    caller_system = f"""You are simulating a caller to an HVAC company.

CALLER BRIEF:
{scenario['callerPrompt']}

RULES:
- Respond naturally as this caller would — short, realistic sentences
- Do NOT offer all information at once; respond to what the agent asks
- Stay in character throughout — do not break role
- When the call is clearly over (agent says goodbye), respond with only: [END CALL]
- Keep responses under 30 words per turn
"""

    agent_system = f"""You are Sophie, a virtual AI receptionist for an HVAC company.
You are handling an inbound phone call.

{agent_prompt}

RULES:
- Respond as Sophie would in a real phone call — concise, professional, warm
- One question or statement per turn — never more
- When you have collected all necessary information and the call is complete, 
  say goodbye and end with: [END CALL]
- Keep responses under 50 words per turn
"""

    # Start: agent greets
    agent_history   = []  # agent's view of conversation
    caller_history  = []  # caller's view of conversation
    transcript      = []
    total_usage     = {"prompt_tokens": 0, "completion_tokens": 0}

    # Agent opens
    greeting = "Thank you for calling, this is Sophie. How can I help you today?"
    transcript.append({"role": "agent", "text": greeting})
    caller_history.append({"role": "user",      "content": f"[Agent]: {greeting}"})
    agent_history.append( {"role": "assistant", "content": greeting})

    for turn in range(max_turns):
        # ── CALLER TURN ──
        caller_reply, usage = chat(api_key, caller_system, caller_history, temperature=0.8)
        total_usage["prompt_tokens"]     += usage.get("prompt_tokens", 0)
        total_usage["completion_tokens"] += usage.get("completion_tokens", 0)

        transcript.append({"role": "caller", "text": caller_reply})

        if "[END CALL]" in caller_reply:
            break

        caller_history.append({"role": "assistant", "content": caller_reply})
        agent_history.append( {"role": "user",      "content": f"[Caller]: {caller_reply}"})

        # ── AGENT TURN ──
        agent_reply, usage = chat(api_key, agent_system, agent_history, temperature=0.4)
        total_usage["prompt_tokens"]     += usage.get("prompt_tokens", 0)
        total_usage["completion_tokens"] += usage.get("completion_tokens", 0)

        transcript.append({"role": "agent", "text": agent_reply})

        if "[END CALL]" in agent_reply:
            break

        agent_history.append( {"role": "assistant", "content": agent_reply})
        caller_history.append({"role": "user",      "content": f"[Agent]: {agent_reply}"})

    return transcript, total_usage


# ── EVALUATE TRANSCRIPT ───────────────────────────────────────────────────────

def evaluate_transcript(api_key, scenario, transcript):
    """
    Feeds the transcript to GPT and asks it to evaluate pass/fail
    against the expectedBehaviour and specific metrics.
    """
    transcript_text = "\n".join(
        f"{'AGENT' if t['role']=='agent' else 'CALLER'}: {t['text']}"
        for t in transcript
    )

    metrics = scenario.get("metrics", [])
    metrics_list = "\n".join(f"- {m}" for m in metrics) if metrics else f"- {scenario.get('expectedBehaviour','')}"

    evaluator_prompt = f"""You are a strict quality evaluator for an AI phone receptionist.

Evaluate the following conversation transcript against the success criteria below.
Be strict — partial completion counts as a fail for that criterion.

SCENARIO: {scenario['name']}
EXPECTED BEHAVIOUR: {scenario.get('expectedBehaviour', 'N/A')}

SUCCESS CRITERIA:
{metrics_list}

TRANSCRIPT:
{transcript_text}

Respond in this exact JSON format (no markdown, no explanation outside JSON):
{{
  "overall": "PASS" or "FAIL",
  "score": <number of criteria met> out of <total criteria>,
  "criteria": [
    {{"criterion": "<criterion text>", "result": "PASS" or "FAIL", "reason": "<1 sentence>"}}
  ],
  "summary": "<1-2 sentence overall assessment>",
  "root_cause": "<if FAIL: the single most important reason why>"
}}
"""

    response, usage = chat(api_key, evaluator_prompt, [], temperature=0.1)

    # Parse JSON — strip any markdown fences
    clean = response.replace("```json","").replace("```","").strip()
    try:
        result = json.loads(clean)
    except json.JSONDecodeError:
        result = {
            "overall": "ERROR",
            "score": "0/0",
            "criteria": [],
            "summary": "Evaluator returned unparseable response",
            "root_cause": response[:200],
            "raw": response
        }

    result["eval_usage"] = usage
    return result


# ── RUN SCENARIOS ─────────────────────────────────────────────────────────────

def run_scenarios(api_key, scenarios_to_run, agent_prompt, max_turns=MAX_TURNS):
    results      = []
    total_pass   = 0
    total_fail   = 0
    total_error  = 0
    total_tokens = {"prompt_tokens": 0, "completion_tokens": 0}

    for i, scenario in enumerate(scenarios_to_run):
        print(f"  [{i+1:02d}/{len(scenarios_to_run)}] #{scenario['id']} {scenario['name']}...", end=" ", flush=True)

        try:
            transcript, sim_usage = simulate_scenario(api_key, scenario, agent_prompt, max_turns)
            evaluation             = evaluate_transcript(api_key, scenario, transcript)

            outcome = evaluation.get("overall", "ERROR")
            score   = evaluation.get("score", "?")

            if outcome == "PASS":
                total_pass += 1
                icon = "✅"
            elif outcome == "FAIL":
                total_fail += 1
                icon = "❌"
            else:
                total_error += 1
                icon = "⚠️ "

            print(f"{icon} {outcome} ({score})")

            # Accumulate token usage
            for k in total_tokens:
                total_tokens[k] += sim_usage.get(k, 0)
                total_tokens[k] += evaluation.get("eval_usage", {}).get(k, 0)

            results.append({
                "id":           scenario["id"],
                "name":         scenario["name"],
                "group":        scenario["group"],
                "outcome":      outcome,
                "score":        score,
                "summary":      evaluation.get("summary", ""),
                "root_cause":   evaluation.get("root_cause", ""),
                "criteria":     evaluation.get("criteria", []),
                "transcript":   transcript
            })

        except Exception as e:
            total_error += 1
            print(f"⚠️  ERROR: {e}")
            results.append({
                "id":       scenario["id"],
                "name":     scenario["name"],
                "group":    scenario["group"],
                "outcome":  "ERROR",
                "error":    str(e)
            })

        time.sleep(0.5)  # Rate limit buffer

    return results, total_pass, total_fail, total_error, total_tokens


# ── REPORT ────────────────────────────────────────────────────────────────────

def build_report(results, total_pass, total_fail, total_error, total_tokens, run_label):
    total = total_pass + total_fail + total_error
    pass_rate = (total_pass / total * 100) if total > 0 else 0

    # Cost estimate (gpt-4o-mini pricing)
    input_cost  = total_tokens["prompt_tokens"]     * 0.15  / 1_000_000
    output_cost = total_tokens["completion_tokens"] * 0.60  / 1_000_000
    total_cost  = input_cost + output_cost

    # Group breakdown
    groups = {}
    for r in results:
        g = r.get("group", "unknown")
        if g not in groups:
            groups[g] = {"pass": 0, "fail": 0, "error": 0}
        groups[g][r["outcome"].lower() if r["outcome"] in ["PASS","FAIL"] else "error"] += 1

    # Failures with root cause
    failures = [r for r in results if r["outcome"] in ["FAIL", "ERROR"]]

    report = {
        "run_label":    run_label,
        "timestamp":    datetime.utcnow().isoformat(),
        "flow_id":      TESTING_FLOW,
        "model":        MODEL,
        "summary": {
            "total":     total,
            "pass":      total_pass,
            "fail":      total_fail,
            "error":     total_error,
            "pass_rate": round(pass_rate, 1),
            "cost_usd":  round(total_cost, 4),
            "tokens":    total_tokens
        },
        "group_breakdown": groups,
        "failures":     failures,
        "all_results":  results
    }

    return report


def print_report(report):
    s = report["summary"]
    print("\n" + "="*60)
    print(f"RUN: {report['run_label']}")
    print(f"Model: {report['model']} | Flow: {report['flow_id']}")
    print("="*60)
    print(f"RESULT: {s['pass']}/{s['total']} PASS — {s['pass_rate']}% pass rate")
    print(f"Fail: {s['fail']} | Error: {s['error']}")
    print(f"Cost: ${s['cost_usd']} ({s['tokens']['prompt_tokens']}+{s['tokens']['completion_tokens']} tokens)")
    print()

    print("GROUP BREAKDOWN:")
    for group, counts in report["group_breakdown"].items():
        total_g = counts["pass"] + counts["fail"] + counts["error"]
        rate    = round(counts["pass"]/total_g*100) if total_g > 0 else 0
        bar     = "█" * (rate//10) + "░" * (10 - rate//10)
        print(f"  {group:<25} {bar} {rate:3d}%  ({counts['pass']}/{total_g})")

    print()
    if report["failures"]:
        print(f"FAILURES ({len(report['failures'])}):")
        for f in report["failures"]:
            rc = f.get("root_cause") or f.get("error", "")
            print(f"  #{f['id']:02d} {f['name']}")
            print(f"       → {rc}")
        print()


# ── PUSH RESULTS TO GITHUB ────────────────────────────────────────────────────

def push_results(report, run_label):
    gh = {"Authorization": f"token {GITHUB_TOKEN}", "Content-Type": "application/json"}
    timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H%M")
    path = f"tests/results/simulator-run-{timestamp}.json"
    content = base64.b64encode(json.dumps(report, indent=2).encode()).decode()

    payload = {
        "message": f"Simulator run: {run_label} — {report['summary']['pass_rate']}% pass rate",
        "content": content
    }
    r = requests.put(
        f"https://api.github.com/repos/Syntharra/syntharra-automations/contents/{path}",
        headers=gh, json=payload
    )
    if r.status_code in (200, 201):
        print(f"✅ Results pushed to GitHub: {path}")
    else:
        print(f"⚠️  GitHub push failed: {r.status_code}")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Syntharra Agent Simulator")
    parser.add_argument("--key",       required=True, help="OpenAI API key")
    parser.add_argument("--scenarios", default="all",  help="Comma-separated IDs, 'all', or group name")
    parser.add_argument("--group",     default=None,   help="Run a specific group only")
    parser.add_argument("--max-turns", type=int, default=MAX_TURNS, help="Max conversation turns")
    parser.add_argument("--label",     default=None,   help="Run label for reporting")
    parser.add_argument("--no-push",   action="store_true", help="Don't push results to GitHub")
    args = parser.parse_args()

    api_key = args.key

    print("🔄 Fetching agent prompt from Retell...")
    agent_prompt = fetch_agent_prompt()
    print(f"   Agent prompt: {len(agent_prompt)} chars")

    print("🔄 Fetching scenarios from GitHub...")
    all_scenarios = fetch_scenarios()
    standard_scenarios = [s for s in all_scenarios if not s.get("premiumOnly")]
    print(f"   Total: {len(all_scenarios)} | Standard: {len(standard_scenarios)}")

    # Filter scenarios
    if args.group:
        group_map = {
            "core_flow":           "core_flow",
            "service_variations":  "service_variations",
            "caller_personalities":"caller_personalities",
            "info_collection":     "info_collection",
            "edge_cases":          "edge_cases",
            "pricing_traps":       "pricing_traps",
            "boundary_safety":     "boundary_safety",
        }
        g = group_map.get(args.group, args.group)
        scenarios_to_run = [s for s in standard_scenarios if s.get("group") == g]
    elif args.scenarios == "all":
        scenarios_to_run = standard_scenarios
    else:
        ids = [int(x.strip()) for x in args.scenarios.split(",")]
        scenarios_to_run = [s for s in all_scenarios if s["id"] in ids]

    if not scenarios_to_run:
        print("❌ No scenarios matched. Check --scenarios or --group")
        sys.exit(1)

    run_label = args.label or f"simulator-{datetime.utcnow().strftime('%Y%m%d-%H%M')}"

    # Cost estimate before running
    est_cost = len(scenarios_to_run) * 0.002
    print(f"\n📋 Scenarios to run: {len(scenarios_to_run)}")
    print(f"💰 Estimated cost:   ~${est_cost:.3f}")
    print(f"🏷️  Run label:        {run_label}")
    print(f"🔄 Max turns/sim:    {args.max_turns}")
    print()

    print("▶  Running simulations...\n")
    results, total_pass, total_fail, total_error, total_tokens = run_scenarios(
        api_key, scenarios_to_run, agent_prompt, args.max_turns
    )

    report = build_report(results, total_pass, total_fail, total_error, total_tokens, run_label)
    print_report(report)

    if not args.no_push:
        push_results(report, run_label)

    # Exit code — non-zero if pass rate < 90%
    sys.exit(0 if report["summary"]["pass_rate"] >= 90 else 1)


if __name__ == "__main__":
    main()
