# Syntharra — Infinite Self-Healing Agent Loop

## Vision

**Goal:** Build a fully autonomous testing & fixing system that:
- Runs continuously (daily/hourly if needed)
- Costs pennies per run (not dollars)
- Auto-detects issues from real call logs
- Auto-applies fixes to prompts
- Auto-validates fixes work
- Never needs human approval
- Scales to 50+ client agents without extra cost

**End state:** "Let it run. Check back in a week. Agent is now 100% ready to sell."

---

## Architecture: Three-Layer Loop

```
LAYER 1: DIAGNOSE (FREE)
├─ Pull last 20 real calls from Retell
├─ Scan transcripts for 12 issue patterns
├─ Rank by severity + frequency
└─ Output: [Issue 1, Issue 2, Issue 3...]
   Cost: $0 (just log reading)

LAYER 2: GENERATE FIX (FREE - LOCAL)
├─ For each issue:
│  ├─ Identify which node/prompt caused it
│  ├─ Use Claude API to generate fix (local, no test yet)
│  ├─ Apply fix to flow JSON in Supabase
│  ├─ Publish agent
│  └─ Store fix in git log with timestamp
   Cost: $0.02 (small Claude API call)

LAYER 3: VALIDATE FIX (CHEAP)
├─ For each fix applied:
│  ├─ Create single test case (~$0.15)
│  ├─ Run 1-scenario batch
│  ├─ Check pass/fail
│  ├─ If FAIL: roll back, try different fix, retry
│  ├─ If PASS: commit fix, move to next issue
│  └─ Hard stop at $2.00 per run
   Cost: $0.15–$2.00 per cycle

REPEAT NIGHTLY
└─ Cron: 2 AM UTC every night
   └─ Process both Standard + Premium in parallel
   └─ Email summary report
```

---

## Cost Analysis

### Old Way (Manual Iteration)
- Human finds issue in dashboard
- Human writes prompt fix
- Human runs full 95-scenario batch to validate
- Cost per fix: **$47–95**
- Time: **2 hours**
- Annual cost for 20 fixes: **$940–1900**

### New Way (Auto-Healing Loop)
- System finds issue automatically
- System generates fix with Claude
- System runs 1-scenario validation
- Cost per fix: **$0.15 + $0.02 = $0.17**
- Time: **2 minutes (automated)**
- Annual cost for 500 fixes: **$85**

**Savings: 90% cost reduction, 98% time reduction**

---

## Layer 1: Diagnose (FREE)

### Call Log Analyser v2

```python
def diagnose_issues(agent_id, limit=20):
    """
    Pull real calls, scan for issues, return ranked list.
    
    Returns:
    [
        {
            "issue_id": "emergency_not_detected_001",
            "severity": "CRITICAL",
            "frequency": 3,  # Seen in 3 of last 20 calls
            "description": "Emergency keywords (gas, fire) not triggering emergency flow",
            "example_call_id": "call_xyz",
            "example_user_input": "I smell gas in my house",
            "example_agent_error": "Asked for repair type instead of routing to emergency",
            "affected_node": "identify_call",
            "affected_field": "emergency_condition_edge"
        },
        {
            "issue_id": "no_name_collected_005",
            "severity": "HIGH",
            "frequency": 5,
            "description": "Calls >30s but no name collected before ending",
            "example_call_id": "call_abc",
            "affected_node": "leadcapture",
            "affected_field": "name_required_validation"
        }
    ]
    """
    
    calls = pull_calls(agent_id, limit)
    issues = []
    
    # Pattern 1: Emergency not detected
    emergency_keywords = ['gas', 'fire', 'smoke', 'flood', 'co alarm', 'carbon monoxide']
    emergency_calls = [c for c in calls 
                       if any(kw in c.get('transcript_text', '').lower() 
                              for kw in emergency_keywords)]
    
    for call in emergency_calls:
        # Check if agent routed to emergency node
        if 'Transfer Call' not in call.get('nodes_visited', []):
            issues.append({
                "issue_id": "emergency_not_detected_001",
                "severity": "CRITICAL",
                "frequency": len([c for c in emergency_calls if 'Transfer Call' not in c.get('nodes_visited', [])]),
                "description": "Emergency detected in call but not routed to transfer",
                "example_call_id": call.get('call_id'),
                "affected_node": "identify_call",
                "affected_field": "emergency_condition_edge"
            })
            break  # Count once, don't duplicate
    
    # Pattern 2: No name collected on long calls
    long_calls = [c for c in calls if c.get('duration_ms', 0) > 30000]
    no_name_calls = [c for c in long_calls 
                     if 'name' not in c.get('transcript_text', '').lower()]
    
    if len(no_name_calls) > len(long_calls) * 0.3:  # >30% of long calls
        issues.append({
            "issue_id": "no_name_collected_005",
            "severity": "HIGH",
            "frequency": len(no_name_calls),
            "description": f"{len(no_name_calls)}/{len(long_calls)} long calls missing name collection",
            "example_call_id": no_name_calls[0].get('call_id'),
            "affected_node": "leadcapture",
            "affected_field": "name_required_validation"
        })
    
    # Pattern 3: "Say:" prefix in agent response
    for call in calls:
        transcript = call.get('transcript', [])
        for turn in transcript:
            agent_msg = turn.get('agent_message', '')
            if agent_msg.startswith('Say:'):
                issues.append({
                    "issue_id": "say_prefix_critical_003",
                    "severity": "CRITICAL",
                    "frequency": 1,
                    "description": "Agent output contains 'Say:' prefix (should use 'Respond with:')",
                    "example_call_id": call.get('call_id'),
                    "example_agent_error": agent_msg[:100],
                    "affected_node": "unknown",
                    "affected_field": "prompt_instruction"
                })
                break
    
    # [Continue for 12 patterns...]
    
    # Sort by severity + frequency
    severity_rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    issues = sorted(issues, 
                    key=lambda x: (severity_rank[x['severity']], -x['frequency']))
    
    # Deduplicate (keep highest frequency instance of each issue type)
    seen = {}
    unique_issues = []
    for issue in issues:
        issue_type = issue['issue_id'].rsplit('_', 1)[0]  # Strip the number
        if issue_type not in seen:
            seen[issue_type] = issue
            unique_issues.append(issue)
    
    return unique_issues


def pull_calls(agent_id, limit=20):
    """Fetch calls from Retell, enrich with node visit tracking"""
    # ... existing code ...
    
    calls = retell_api_call(...)
    
    # Enrich: determine which nodes were visited
    for call in calls:
        call['nodes_visited'] = extract_nodes_from_transcript(call['transcript'])
    
    return calls
```

### Cost: **$0.00 per run** (just reading logs you already have)

---

## Layer 2: Generate Fix (FREE - LOCAL)

### Auto-Fix Generator

This uses **Claude local** (your API call) to generate the fix code. No Retell testing yet.

```python
def generate_fix(issue, agent_config, flow_json):
    """
    Use Claude to generate a fix for this issue.
    
    Input:
    {
        "issue_id": "emergency_not_detected_001",
        "severity": "CRITICAL",
        "affected_node": "identify_call",
        "affected_field": "emergency_condition_edge",
        "description": "Emergency keywords not detected"
    }
    
    Output:
    {
        "fix_id": "FIX-20260331-001",
        "issue_id": "emergency_not_detected_001",
        "node_name": "identify_call",
        "change_type": "prompt_update",
        "old_value": "...",
        "new_value": "...",
        "confidence": 0.95,
        "reasoning": "Added CO/carbon monoxide detection..."
    }
    """
    
    # Build context for Claude
    affected_node = next((n for n in flow_json['nodes'] 
                         if n['id'] == issue['affected_node']), None)
    
    if not affected_node:
        return None  # Can't fix if node not found
    
    prompt = f"""
You are an expert HVAC AI receptionist prompt engineer.

Current issue:
{issue['description']}

Affected flow node:
{json.dumps(affected_node, indent=2)}

Agent config:
{json.dumps(agent_config, indent=2)}

Your task:
1. Identify the root cause in the prompt/edge condition
2. Generate a minimal, surgical fix
3. Do NOT change the node structure, only the text content
4. Ensure fix is consistent with agent brand voice
5. Return ONLY valid JSON in response

Output format (JSON):
{{
  "fix_applied": true,
  "node_id": "node-identify-call",
  "field": "instructions",
  "old_text": "...",
  "new_text": "...",
  "reasoning": "Why this fixes it"
}}
"""
    
    # Call Claude API (local, cheap)
    response = claude_api_call(
        model="claude-opus-4-20250514",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.3  # Low temp = consistent, reliable fixes
    )
    
    fix_json = extract_json_from_response(response)
    return fix_json


def apply_fix_to_flow(fix, flow_json):
    """
    Apply the generated fix to the flow JSON.
    Return updated flow.
    """
    
    if not fix or not fix.get('fix_applied'):
        return None
    
    node_id = fix['node_id']
    field = fix['field']
    new_text = fix['new_text']
    
    # Find and update the node
    for node in flow_json.get('nodes', []):
        if node['id'] == node_id:
            # Handle different field types
            if field == 'instructions':
                node['instructions'] = new_text
            elif field == 'prompt':
                node['prompt'] = new_text
            elif field == 'edge_condition':
                # Update the edge that matches
                # ... more complex logic ...
                pass
            
            return flow_json
    
    return None  # Node not found


def publish_fix(agent_id, updated_flow, fix):
    """
    Publish the agent with the new flow.
    Store fix metadata.
    """
    
    # Step 1: Update flow in Retell
    retell_api_patch(f"/update-conversation-flow/{flow_id}", 
                     {"nodes": updated_flow['nodes']})
    
    # Step 2: Publish agent
    retell_api_post(f"/publish-agent/{agent_id}", {})
    
    # Step 3: Log fix to GitHub
    fix_log = {
        "timestamp": datetime.now().isoformat(),
        "agent_id": agent_id,
        "fix_id": fix['fix_id'],
        "issue": fix['issue_id'],
        "applied": True,
        "validation_pending": True,
        "reasoning": fix['reasoning']
    }
    
    append_to_github_log("docs/fixes-log.md", fix_log)
    
    return True
```

### Cost: **$0.02 per fix** (small Claude API call, no testing)

---

## Layer 3: Validate Fix (CHEAP)

### Auto-Test Single-Scenario

Run only ONE test scenario per fix (vs 95 for full batch).

```python
def validate_fix(fix_id, agent_id, flow_id, issue):
    """
    Create and run a single test case for this specific fix.
    Cost: ~$0.15 per test
    
    Use Retell batch test API with 1 scenario.
    """
    
    # Step 1: Create targeted test case
    test_case = {
        "name": f"AutoFix Validation — {fix_id}",
        "response_engine": {
            "type": "conversation-flow",
            "conversation_flow_id": flow_id,
            "llm_config": {
                "model": "gpt-4.1-mini"  # Cheaper for validation
            }
        },
        "user_prompt": generate_test_prompt_for_issue(issue),
        "metrics": [f"Fixed: {issue['issue_id']}"]
    }
    
    test_case_id = retell_create_test_case(test_case)
    
    # Step 2: Run as 1-item batch
    batch = {
        "test_case_ids": [test_case_id],
        "response_engine": test_case["response_engine"]
    }
    
    batch_id = retell_create_batch_test(batch)
    
    # Step 3: Poll until complete
    result = retell_poll_batch(batch_id, timeout=60)
    
    # Step 4: Record result
    validation = {
        "fix_id": fix_id,
        "test_case_id": test_case_id,
        "batch_id": batch_id,
        "passed": result['passed_tests'] > 0,
        "failed": result['failed_tests'],
        "errors": result['error_count'],
        "cost": 0.15
    }
    
    return validation


def generate_test_prompt_for_issue(issue):
    """
    Create a test prompt that would have failed before the fix.
    Example: if issue is "emergency not detected", 
    test prompt includes emergency keywords.
    """
    
    issue_id = issue['issue_id']
    
    if 'emergency_not_detected' in issue_id:
        return """
Caller: I have a gas leak in my house, it's an emergency!
Goal: Agent must immediately route to emergency transfer, not ask questions
"""
    
    elif 'no_name_collected' in issue_id:
        return """
Caller: I need AC repair
Agent collects service info and other details
Goal: Before hanging up, agent must have collected caller's name
"""
    
    elif 'say_prefix' in issue_id:
        return """
Caller: Can you help me?
Goal: Agent must never output 'Say:' literal text in response
"""
    
    # [Continue for all issue types...]
```

### Cost: **$0.15 per validation** (single scenario test, cheap LLM model)

---

## Full Loop: Orchestration

### The Main Loop (Runs Nightly)

```python
def self_healing_loop(agent_id, max_cost_per_run=2.00):
    """
    Main loop: diagnose → fix → validate, repeat.
    Runs daily or on-demand.
    """
    
    print(f"\n{'='*70}")
    print(f"SELF-HEALING LOOP — {agent_id}")
    print(f"{'='*70}")
    
    total_cost = 0.0
    total_fixes_applied = 0
    total_fixes_validated = 0
    
    # STEP 1: DIAGNOSE (FREE)
    print("\n[1/3] DIAGNOSE — Scanning real calls...")
    issues = diagnose_issues(agent_id, limit=20)
    
    if not issues:
        print("  ✓ No issues found! Agent is healthy.")
        return {
            "status": "healthy",
            "issues_found": 0,
            "fixes_applied": 0,
            "cost": 0
        }
    
    print(f"  ✓ Found {len(issues)} issues:")
    for issue in issues:
        print(f"     [{issue['severity']}] {issue['issue_id']} (freq: {issue['frequency']})")
    
    # STEP 2: GENERATE & APPLY FIXES (FREE—$0.02)
    print("\n[2/3] GENERATE FIXES — Using Claude...")
    
    # Fetch current flow
    flow_json = retell_get_flow(agent_id)
    
    fixes_to_validate = []
    
    for issue in issues[:5]:  # Process top 5 issues
        print(f"\n  Processing: {issue['issue_id']}")
        
        # Generate fix with Claude
        fix = generate_fix(issue, agent_config, flow_json)
        
        if not fix or not fix.get('fix_applied'):
            print(f"    ✗ Could not generate fix")
            continue
        
        print(f"    → Claude generated fix: {fix['node_id']}.{fix['field']}")
        print(f"    → Reason: {fix['reasoning'][:60]}...")
        
        # Apply fix to flow
        updated_flow = apply_fix_to_flow(fix, flow_json)
        
        if updated_flow:
            # Publish agent
            publish_fix(agent_id, updated_flow, fix)
            print(f"    ✓ Fix published, waiting for validation...")
            
            fixes_to_validate.append({
                "fix": fix,
                "issue": issue,
                "agent_id": agent_id,
                "flow_id": agent_flow_id
            })
            
            total_fixes_applied += 1
        else:
            print(f"    ✗ Failed to apply fix")
    
    # STEP 3: VALIDATE FIXES (CHEAP — $0.15 each)
    print(f"\n[3/3] VALIDATE FIXES — Running {len(fixes_to_validate)} tests...")
    
    passed_fixes = []
    failed_fixes = []
    
    for item in fixes_to_validate:
        fix = item['fix']
        issue = item['issue']
        
        print(f"\n  Testing: {fix['fix_id']}")
        
        try:
            validation = validate_fix(fix['fix_id'], 
                                    item['agent_id'], 
                                    item['flow_id'], 
                                    issue)
            
            total_cost += validation['cost']
            
            if validation['passed']:
                print(f"    ✅ PASS — Fix validated!")
                passed_fixes.append(fix)
                total_fixes_validated += 1
            else:
                print(f"    ❌ FAIL — Fix did not work")
                print(f"       Failures: {validation['failed']}, Errors: {validation['errors']}")
                failed_fixes.append(fix)
                
                # Optionally: rollback and try again
                # rollback_fix(agent_id, fix)
            
            # Cost gate check
            if total_cost > max_cost_per_run:
                print(f"\n  ⚠️  Cost gate hit: ${total_cost:.2f} > ${max_cost_per_run:.2f}")
                break
        
        except Exception as e:
            print(f"    ✗ Error validating: {e}")
    
    # FINAL REPORT
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Issues found:        {len(issues)}")
    print(f"Fixes generated:     {total_fixes_applied}")
    print(f"Fixes validated:     {total_fixes_validated} ✅")
    print(f"Fixes failed:        {len(failed_fixes)} ❌")
    print(f"Total cost:          ${total_cost:.2f}")
    print(f"Estimated pass rate: {len(passed_fixes) / (len(passed_fixes) + len(failed_fixes)) * 100 if (len(passed_fixes) + len(failed_fixes)) else 0:.0f}%")
    
    # Send email report
    send_loop_report({
        "agent_id": agent_id,
        "issues_found": len(issues),
        "fixes_applied": total_fixes_applied,
        "fixes_passed": total_fixes_validated,
        "cost": total_cost,
        "passed_fixes": passed_fixes,
        "failed_fixes": failed_fixes
    })
    
    return {
        "status": "complete",
        "issues_found": len(issues),
        "fixes_applied": total_fixes_applied,
        "fixes_validated": total_fixes_validated,
        "cost": total_cost
    }
```

### Cost per Run: **$0.17 + $0.15 per fix validated = $0.32–$2.00**

---

## Deployment: Daily Cron Job

### n8n Workflow: Auto-Healing Loop

```
Trigger: Daily at 2:00 AM UTC
├─ Standard Agent: agent_4afbfdb3fcb1ba9569353af28d
├─ Premium Agent: agent_c6d7493d164a0616e9d8469370
├─ (Future: All 50+ client agents)
│
├─ FOR EACH AGENT (parallel):
│  ├─ Call: self_healing_loop(agent_id)
│  └─ Wait for completion
│
├─ Collect results
├─ Send summary email to admin@
└─ Log to GitHub (fixes-log.md, cost-tracker.md)

Total time: 5 minutes per agent
Total cost: $0.50–$3.00 per agent per run
Annual cost for 2 agents: ~$360 ($1 per day)
```

### GitHub Logs

**`docs/fixes-log.md`** — Every fix applied
```markdown
## 2026-03-31

### agent_4afbfdb3fcb1ba9569353af28d (Standard)

**FIX-20260331-001:** Emergency routing improved
- Issue: CO alarm not triggering emergency
- Applied to: identify_call.emergency_condition_edge
- Validation: PASS ✅

**FIX-20260331-002:** Name collection enforced
- Issue: No name collected on 5/20 long calls
- Applied to: leadcapture.required_fields
- Validation: PASS ✅

### agent_c6d7493d164a0616e9d8469370 (Premium)
- No issues detected
- Agent healthy ✅
```

**`docs/cost-tracker.md`** — Monthly spending log
```markdown
## March 2026

| Date | Agent | Issues | Fixes Applied | Cost | Status |
|---|---|---|---|---|---|
| 2026-03-31 | Standard | 3 | 2 | $0.32 | ✅ |
| 2026-03-31 | Premium | 0 | 0 | $0.00 | ✅ |
| 2026-03-30 | Standard | 5 | 3 | $0.47 | ✅ |

**Total this month: $0.79**
**Budget per agent: $30/month** ← Well under
```

---

## Failure Scenarios & Rollback

### What If a Fix Breaks the Agent?

```python
def validate_fix_with_fallback(fix_id, agent_id):
    """
    Run fix validation.
    If FAIL: automatically rollback.
    """
    
    # Store current state before applying fix
    backup_flow = save_flow_backup(agent_id)
    
    # Apply fix
    publish_fix(agent_id, updated_flow, fix)
    
    # Validate
    validation = validate_fix(...)
    
    if not validation['passed']:
        print(f"Fix failed. Rolling back...")
        # Restore from backup
        restore_flow_from_backup(agent_id, backup_flow)
        retell_publish_agent(agent_id)
        return False
    
    return True
```

### What If Claude Generates Bad Code?

The system is **self-correcting**:
1. Claude generates fix
2. Test case runs
3. If FAIL → log it, try different approach next cycle
4. Over time, system learns which types of fixes work

No human is left holding the bag.

---

## Scaling to 50+ Agents

### Cost Scaling
- Per-agent cost: ~$2.00/month
- 50 agents: ~$100/month (vs $5,000+ in manual testing)

### Deployment
```python
# Fetch all active client agents from Supabase
clients = get_active_clients()

for client in clients:
    agent_id = client['agent_id']
    flow_id = client['flow_id']
    
    # Run loop for each agent
    result = self_healing_loop(agent_id, max_cost=2.00)
    
    # Email results to client
    send_client_report(client['email'], result)
    
    # Log for Syntharra admin
    log_to_admin_dashboard(client, result)
```

---

## Implementation Roadmap

### Phase 1: Foundation (This Week)
- [ ] Build diagnose_issues() function ✓ (core logic ready)
- [ ] Build generate_fix() with Claude API ✓ (architecture ready)
- [ ] Build validate_fix() single-scenario test ✓ (logic ready)
- [ ] Test on Standard agent (5 iterations)
- [ ] Test on Premium agent (5 iterations)
- [ ] Document learnings

### Phase 2: Automation (Next Week)
- [ ] Deploy as n8n workflow
- [ ] Add daily cron trigger
- [ ] Email reporting
- [ ] GitHub logging
- [ ] Cost tracking

### Phase 3: Scaling (Week 3)
- [ ] Deploy to all client agents
- [ ] Multi-agent parallel execution
- [ ] Client dashboards
- [ ] Automated client notifications

### Phase 4: Live (Week 4)
- [ ] Monitor first month
- [ ] Adjust issue detection patterns based on real data
- [ ] Launch as "Always-On Agent Optimization" feature
- [ ] Begin selling

---

## Key Differences from Manual Testing

| Aspect | Manual | Auto-Healing |
|---|---|---|
| Cost per fix | $47–95 | $0.17 |
| Time per fix | 2 hours | 2 minutes |
| Trigger | Human remembers | Automatic nightly |
| Validation | Human judgment | Automated test |
| Scaling | 10 agents max | 1000+ agents |
| Annual cost (100 fixes) | $4,700–9,500 | $17 |

---

## Success Metrics

**Agent is "done" when:**
- ✅ Pass rate ≥ 95% on full 95-scenario batch
- ✅ No CRITICAL issues in last 7 days of real calls
- ✅ Same test prompt always passes (consistency)
- ✅ Ready to sell and scale to customers

**For Standard & Premium to be launch-ready:**
- Standard: 95% pass rate (in progress, Auto-Healing Loop will get us there)
- Premium: 100% pass rate (already achieved, just maintain)

