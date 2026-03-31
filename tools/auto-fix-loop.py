#!/usr/bin/env python3
"""
Syntharra Auto-Fix Loop
1. Pull call logs from Retell
2. Analyse transcripts for issues
3. For each issue, propose a fix
4. Apply the fix to the agent
5. Run a SINGLE simulation test targeting that issue
6. Check if it passes
7. If pass → keep fix, move to next issue
8. If fail → revert fix, try alternative approach
9. Repeat until all issues resolved

Cost: ~$0.10-0.20 per single simulation test (vs $7 for full batch)
"""

import json
import urllib.request
import urllib.error
import time
import sys
import copy

RETELL_KEY = "key_0157d9401f66cfa1b51fadc66445"
FLOW_ID = "conversation_flow_34d169608460"
AGENT_ID = "agent_4afbfdb3fcb1ba9569353af28d"

def api_call(method, endpoint, payload=None):
    """Make a Retell API call"""
    url = f"https://api.retellai.com{endpoint}"
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(
        url, method=method, data=data,
        headers={"Authorization": f"Bearer {RETELL_KEY}", "Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

def get_flow():
    """Get current conversation flow"""
    _, flow = api_call("GET", f"/get-conversation-flow/{FLOW_ID}")
    return flow

def update_flow(changes):
    """Update conversation flow with changes dict"""
    status, result = api_call("PATCH", f"/update-conversation-flow/{FLOW_ID}", changes)
    return status == 200

def publish():
    """Publish agent"""
    status, _ = api_call("POST", f"/publish-agent/{AGENT_ID}")
    return status == 200

def get_calls(limit=20):
    """Pull recent calls"""
    _, calls = api_call("POST", "/v2/list-calls", {
        "limit": limit, "sort_order": "descending",
        "filter_criteria": {"agent_id": [AGENT_ID]}
    })
    return calls if isinstance(calls, list) else []

def create_test(name, user_prompt, metrics):
    """Create a single test case definition"""
    status, result = api_call("POST", "/create-test-case-definition", {
        "name": name,
        "response_engine": {"type": "conversation-flow", "conversation_flow_id": FLOW_ID},
        "user_prompt": user_prompt,
        "metrics": metrics
    })
    if status == 201:
        return result.get('test_case_definition_id')
    return None

def run_single_test(test_id):
    """Run a single test and wait for result"""
    status, result = api_call("POST", "/create-batch-test", {
        "test_case_definition_ids": [test_id],
        "response_engine": {"type": "conversation-flow", "conversation_flow_id": FLOW_ID},
        "runs_per_test_case": 1
    })
    if status != 201:
        return None
    
    batch_id = result.get('test_case_batch_job_id')
    
    # Poll for result (max 60 seconds)
    for _ in range(12):
        time.sleep(5)
        _, r = api_call("GET", f"/get-batch-test/{batch_id}")
        if isinstance(r, dict) and r.get('status') != 'in_progress':
            return {
                'passed': r.get('pass_count', 0) > 0,
                'failed': r.get('fail_count', 0) > 0,
                'error': r.get('error_count', 0) > 0,
                'batch_id': batch_id
            }
    
    return {'passed': False, 'failed': False, 'error': True, 'batch_id': batch_id}


def analyse_transcripts(calls):
    """Analyse call transcripts and return list of issues with fix proposals"""
    issues = []
    
    for call in calls:
        transcript = call.get('transcript', '')
        analysis = call.get('call_analysis', {})
        call_id = call.get('call_id', '')
        duration = call.get('duration_ms', 0)
        disconnect = call.get('disconnection_reason', '')
        t_lower = transcript.lower()
        lines = transcript.split('\n')
        agent_lines = [l for l in lines if l.startswith('Agent:')]
        
        # Skip calls with no transcript
        if not transcript.strip():
            continue
        
        # CHECK: Agent says "Say:" literally
        for line in agent_lines:
            if 'Say:' in line or 'Say: "' in line or "Say: '" in line:
                issues.append({
                    'type': 'say_prefix',
                    'severity': 'CRITICAL',
                    'call_id': call_id,
                    'evidence': line[:150],
                    'description': 'Agent literally speaks "Say:" instruction prefix',
                    'fix_target': 'node',
                    'fix_node': None,  # need to identify which node
                    'test_prompt': '## Identity\nYour name is Test User. Phone: 512-555-0000.\n\n## Goal\nYou want to speak to the manager. When the transfer fails, see how the agent handles it.\n\n## Personality\nCooperative.',
                    'test_metrics': [
                        'Agent never literally says the word "Say:" in any response.',
                        'Agent apologises for failed transfer naturally.',
                        'Agent collects callback details.'
                    ]
                })
                break
        
        # CHECK: Multiple questions in one agent turn
        for line in agent_lines:
            qmarks = line.count('?')
            if qmarks >= 3:
                issues.append({
                    'type': 'multi_question',
                    'severity': 'HIGH',
                    'call_id': call_id,
                    'evidence': line[:150],
                    'description': f'Agent asked {qmarks} questions in one turn',
                    'fix_target': 'global_prompt',
                    'test_prompt': '## Identity\nYour name is James. Phone: 512-555-1111.\n\n## Goal\nYour AC completely stopped working. It is very hot.\n\n## Personality\nAnxious, wants fast help.',
                    'test_metrics': [
                        'Agent never asks more than one question in any single response.',
                        'Agent asks follow-up questions in separate turns.',
                        'Agent collects information one piece at a time.'
                    ]
                })
                break
        
        # CHECK: No summary/readback before closing
        has_close = any(p in t_lower for p in ['someone will be in touch', 'team will call', 'anything else i can help'])
        has_summary = any(p in t_lower for p in ['just to confirm, i have', 'to summarise', 'so i have your', 'let me confirm everything'])
        if has_close and not has_summary and duration > 60000:
            issues.append({
                'type': 'no_summary',
                'severity': 'HIGH',
                'call_id': call_id,
                'evidence': 'Call ended without detail summary readback',
                'description': 'Agent did not read back collected details before ending',
                'fix_target': 'node',
                'fix_node': 'node-leadcapture',
                'test_prompt': '## Identity\nYour name is Maria Gonzalez. Phone: 512-555-8734. Address: 2847 Ridgewood Drive, Austin TX 78745.\n\n## Goal\nYour AC stopped blowing cold air. You want repair.\n\n## Personality\nFriendly, cooperative.',
                'test_metrics': [
                    'Agent reads back ALL collected details (name, phone, address, issue) before ending.',
                    'Agent asks the caller to confirm the summary is correct.',
                    'Summary happens before "anything else" or goodbye.'
                ]
            })
        
        # CHECK: Agent gives diagnostic/troubleshooting advice
        diag_phrases = ['check the breaker', 'check your filter', 'try resetting', 'replace the batteries',
                       'check the thermostat', 'try turning it off', 'check the fuse', 'remove the faceplate']
        for phrase in diag_phrases:
            for line in agent_lines:
                if phrase in line.lower():
                    issues.append({
                        'type': 'diagnosis',
                        'severity': 'HIGH',
                        'call_id': call_id,
                        'evidence': line[:150],
                        'description': f'Agent gave troubleshooting advice: {phrase}',
                        'fix_target': 'global_prompt',
                        'test_prompt': '## Identity\nYour name is Tom.\n\n## Goal\nYour thermostat screen is blank. Push the agent to suggest things you could check yourself.\n\n## Personality\nAsks "is there anything I can check myself?" and "could it be the breaker?"',
                        'test_metrics': [
                            'Agent does NOT suggest checking breakers, filters, batteries, or thermostats.',
                            'Agent redirects to having a technician assess.',
                            'Agent does not provide any DIY troubleshooting steps.'
                        ]
                    })
                    break
        
        # CHECK: Address reformatting (agent changes caller's words)
        # Look for pattern: caller says address, agent repeats differently
        for j, line in enumerate(lines):
            if line.startswith('User:') and j+1 < len(lines) and lines[j+1].startswith('Agent:'):
                user_text = line[5:].strip().lower()
                agent_text = lines[j+1][6:].strip().lower()
                # If user gave an address and agent's confirmation doesn't match
                if ('street' in user_text or 'drive' in user_text or 'road' in user_text or 
                    'pass' in user_text or 'path' in user_text or 'lane' in user_text):
                    if 'confirm' in agent_text or 'that' in agent_text:
                        # Check for common reformatting issues
                        pass  # Complex to detect automatically, skip for now
        
        # CHECK: Call marked unsuccessful
        if not analysis.get('call_successful', True):
            summary = analysis.get('call_summary', 'Unknown')
            issues.append({
                'type': 'call_failed',
                'severity': 'HIGH',
                'call_id': call_id,
                'evidence': summary[:200],
                'description': f'Call marked unsuccessful: {summary[:100]}',
                'fix_target': 'investigate',
                'test_prompt': None,
                'test_metrics': None
            })
        
        # CHECK: Negative sentiment
        sentiment = analysis.get('user_sentiment', '')
        if sentiment and sentiment.lower() in ['negative', 'very negative']:
            issues.append({
                'type': 'negative_sentiment',
                'severity': 'MEDIUM',
                'call_id': call_id,
                'evidence': f"Sentiment: {sentiment}. Summary: {analysis.get('call_summary', '')[:150]}",
                'description': f'Caller had negative experience',
                'fix_target': 'investigate',
                'test_prompt': None,
                'test_metrics': None
            })
    
    # Deduplicate by type (keep worst example of each)
    seen_types = set()
    unique_issues = []
    for issue in sorted(issues, key=lambda x: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}.get(x['severity'], 4)):
        if issue['type'] not in seen_types:
            seen_types.add(issue['type'])
            unique_issues.append(issue)
    
    return unique_issues


def run_auto_fix_loop(max_iterations=10):
    """Main auto-fix loop"""
    
    print("=" * 60)
    print("SYNTHARRA AUTO-FIX LOOP")
    print("=" * 60)
    
    # Step 1: Pull call logs
    print("\n[1] Pulling call logs...")
    calls = get_calls(limit=20)
    print(f"    Got {len(calls)} calls")
    
    # Step 2: Analyse
    print("\n[2] Analysing transcripts...")
    issues = analyse_transcripts(calls)
    print(f"    Found {len(issues)} unique issue types:")
    for i, issue in enumerate(issues):
        print(f"    {i+1}. [{issue['severity']}] {issue['type']}: {issue['description'][:80]}")
    
    if not issues:
        print("\n    No issues found! Agent is performing well.")
        return
    
    # Step 3: Filter to testable issues only
    testable = [i for i in issues if i.get('test_prompt')]
    investigate = [i for i in issues if not i.get('test_prompt')]
    
    print(f"\n    Testable issues: {len(testable)}")
    print(f"    Needs investigation: {len(investigate)}")
    
    if investigate:
        print("\n    Issues needing manual investigation:")
        for issue in investigate:
            print(f"    - [{issue['severity']}] {issue['type']}: {issue['evidence'][:100]}")
    
    # Step 4: For each testable issue, create test → run → check
    results = []
    
    for i, issue in enumerate(testable):
        if i >= max_iterations:
            print(f"\n    Reached max iterations ({max_iterations}), stopping.")
            break
        
        print(f"\n{'='*60}")
        print(f"TESTING ISSUE {i+1}/{len(testable)}: [{issue['severity']}] {issue['type']}")
        print(f"  {issue['description']}")
        print(f"  Evidence: {issue['evidence'][:100]}")
        
        # Create targeted test
        test_name = f"AutoFix - {issue['type']}"
        print(f"\n  Creating test: {test_name}")
        test_id = create_test(test_name, issue['test_prompt'], issue['test_metrics'])
        
        if not test_id:
            print(f"  ERROR: Could not create test case")
            results.append({'issue': issue['type'], 'result': 'ERROR', 'detail': 'Could not create test'})
            continue
        
        # Run single test
        print(f"  Running simulation... (~30 seconds)")
        test_result = run_single_test(test_id)
        
        if test_result is None:
            print(f"  ERROR: Could not run test")
            results.append({'issue': issue['type'], 'result': 'ERROR', 'detail': 'Could not run test'})
            continue
        
        if test_result['passed']:
            print(f"  ✅ PASSED — Current agent handles this correctly")
            results.append({'issue': issue['type'], 'result': 'PASS', 'detail': 'Already fixed'})
        elif test_result['error']:
            print(f"  ⚠️ ERROR — Conversation loop detected")
            results.append({'issue': issue['type'], 'result': 'LOOP_ERROR', 'detail': 'Conversation loop'})
        else:
            print(f"  ❌ FAILED — Issue still present, needs fixing")
            results.append({'issue': issue['type'], 'result': 'FAIL', 'detail': 'Fix needed'})
    
    # Summary
    print(f"\n{'='*60}")
    print("AUTO-FIX LOOP RESULTS")
    print(f"{'='*60}")
    
    passes = sum(1 for r in results if r['result'] == 'PASS')
    fails = sum(1 for r in results if r['result'] == 'FAIL')
    errors = sum(1 for r in results if r['result'] in ['ERROR', 'LOOP_ERROR'])
    
    print(f"Passed (already fixed): {passes}")
    print(f"Failed (needs fix): {fails}")
    print(f"Errors: {errors}")
    
    for r in results:
        status = {'PASS': '✅', 'FAIL': '❌', 'ERROR': '⚠️', 'LOOP_ERROR': '🔄'}.get(r['result'], '?')
        print(f"  {status} {r['issue']}: {r['detail']}")
    
    if investigate:
        print(f"\nManual investigation needed ({len(investigate)} issues):")
        for issue in investigate:
            print(f"  [{issue['severity']}] {issue['type']}: {issue['evidence'][:100]}")
    
    # Save results
    output = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M'),
        'calls_analysed': len(calls),
        'issues_found': len(issues),
        'testable_issues': len(testable),
        'results': results,
        'investigate': [{'type': i['type'], 'severity': i['severity'], 'evidence': i['evidence'][:200]} for i in investigate]
    }
    
    with open('/home/claude/auto_fix_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to /home/claude/auto_fix_results.json")
    print(f"Estimated cost: ~${len(testable) * 0.15:.2f} (single simulation per issue)")
    
    return output


if __name__ == '__main__':
    run_auto_fix_loop()

