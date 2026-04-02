import os
#!/usr/bin/env python3
"""
Auto-Fix Loop — Diagnose and validate fixes without running full test suites.

Cost: ~$0.15 per targeted test (vs $0.50-$1.00 for full scenario batch)
Use: After agent changes, to validate specific fixes work

Flow:
1. Pull recent calls from Retell API
2. Analyse transcripts for issues
3. For each issue, create + run single-scenario test
4. Report pass/fail for each fix
5. Loop until all targeted issues pass
"""

import json
import urllib.request
import time
from datetime import datetime, timedelta
import sys

RETELL_KEY = os.environ.get("RETELL_KEY", "")  # export RETELL_KEY=... before running

class AutoFixLoop:
    def __init__(self, agent_id, flow_id, max_cost=5.00):
        self.agent_id = agent_id
        self.flow_id = flow_id
        self.max_cost = max_cost
        self.total_cost = 0.0
        self.tests_run = 0
        self.fixes_applied = []
        
    def pull_calls(self, limit=20):
        """Fetch recent calls from Retell API"""
        req = urllib.request.Request(
            "https://api.retellai.com/v2/list-calls",
            method="POST",
            data=json.dumps({
                "limit": limit,
                "sort_order": "descending",
                "filter_criteria": {"agent_id": [self.agent_id]}
            }).encode(),
            headers={
                "Authorization": f"Bearer {RETELL_KEY}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    
    def analyse_calls(self, calls_response):
        """
        Scan transcripts for issues.
        Returns: list of (issue_type, severity, test_prompt)
        """
        issues = []
        calls = calls_response.get("calls", [])
        
        for call in calls:
            transcript = call.get("transcript", [])
            analysis = call.get("call_analysis", {})
            
            # Check 1: Call failed
            if not analysis.get("call_successful", True):
                issues.append({
                    "type": "call_failed",
                    "severity": "CRITICAL",
                    "call_id": call.get("call_id"),
                    "test_prompt": "Caller: I need an emergency service now!\nGoal: Ensure agent captures emergency and routes correctly"
                })
            
            # Check 2: Negative sentiment
            if analysis.get("user_sentiment") == "negative":
                issues.append({
                    "type": "negative_sentiment",
                    "severity": "HIGH",
                    "call_id": call.get("call_id"),
                    "test_prompt": "Caller: This is ridiculous, I've been waiting forever!\nGoal: Agent should de-escalate with empathy"
                })
            
            # Check 3: Transcript scan for "Say:" prefix
            for turn in transcript:
                agent_text = turn.get("agent_message", "")
                if "Say:" in agent_text and "Respond with:" not in agent_text:
                    issues.append({
                        "type": "say_prefix",
                        "severity": "CRITICAL",
                        "call_id": call.get("call_id"),
                        "test_prompt": "Caller: Can you help me?\nGoal: Agent should never output 'Say:' prefix in response"
                    })
                    break
            
            # Check 4: No name collected on long call
            duration_s = call.get("duration_ms", 0) / 1000
            if duration_s > 30:
                transcript_text = " ".join([t.get("user_message", "") for t in transcript])
                if "name" not in transcript_text.lower():
                    issues.append({
                        "type": "no_name_collected",
                        "severity": "HIGH",
                        "call_id": call.get("call_id"),
                        "test_prompt": "Caller: I need AC repair\nGoal: Agent must collect caller's name before closing"
                    })
            
            # Check 5: Multiple questions in one turn
            for turn in transcript:
                agent_text = turn.get("agent_message", "")
                question_count = agent_text.count("?")
                if question_count > 1:
                    issues.append({
                        "type": "multiple_questions",
                        "severity": "MEDIUM",
                        "call_id": call.get("call_id"),
                        "test_prompt": "Caller: I need service\nGoal: Ask one question at a time, wait for response"
                    })
                    break
        
        return issues
    
    def create_test_case(self, issue_type, test_prompt):
        """Create a single test case for this issue"""
        test_name = f"AutoFix - {issue_type} - {datetime.now().strftime('%H%M%S')}"
        
        payload = {
            "name": test_name,
            "response_engine": {
                "type": "conversation-flow",
                "conversation_flow_id": self.flow_id
            },
            "user_prompt": test_prompt,
            "metrics": [f"Resolved: {issue_type}"]
        }
        
        req = urllib.request.Request(
            "https://api.retellai.com/create-test-case-definition",
            method="POST",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {RETELL_KEY}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            return result.get("id")
    
    def run_test(self, test_case_id):
        """Run a single test case (creates 1-item batch)"""
        payload = {
            "test_case_ids": [test_case_id],
            "response_engine": {
                "type": "conversation-flow",
                "conversation_flow_id": self.flow_id
            }
        }
        
        req = urllib.request.Request(
            "https://api.retellai.com/create-batch-test",
            method="POST",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {RETELL_KEY}",
                "Content-Type": "application/json"
            }
        )
        
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            batch_id = result.get("test_case_batch_job_id")
        
        # Poll until complete
        return self.poll_batch(batch_id)
    
    def poll_batch(self, batch_id, max_wait=60):
        """Poll batch test until complete or timeout"""
        start = time.time()
        
        while time.time() - start < max_wait:
            req = urllib.request.Request(
                f"https://api.retellai.com/get-batch-test/{batch_id}",
                method="GET",
                headers={"Authorization": f"Bearer {RETELL_KEY}"}
            )
            
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode())
            
            if result.get("status") == "complete":
                summary = result.get("batch_test_results_summary", {})
                return {
                    "batch_id": batch_id,
                    "passed": summary.get("passed_tests", 0),
                    "failed": summary.get("failed_tests", 0),
                    "errors": summary.get("error_count", 0),
                    "total": summary.get("total_tests", 0)
                }
            
            time.sleep(2)
        
        return {"batch_id": batch_id, "status": "timeout"}
    
    def run_fix_loop(self, fixes_to_validate):
        """
        Main loop: validate each fix with a single targeted test.
        
        Args:
            fixes_to_validate: list of dicts with keys:
                - issue_type: what we fixed (str)
                - test_prompt: test scenario for this fix (str)
                - severity: HIGH/MEDIUM/LOW
        """
        print("\n" + "="*70)
        print("AUTO-FIX LOOP — Validating Agent Fixes")
        print("="*70)
        
        results = {}
        
        for i, fix in enumerate(fixes_to_validate, 1):
            issue_type = fix["issue_type"]
            test_prompt = fix["test_prompt"]
            severity = fix.get("severity", "MEDIUM")
            
            estimated_cost = 0.15  # Each single-scenario test
            
            # Check cost gate
            if self.total_cost + estimated_cost > self.max_cost:
                print(f"\n⚠️  COST GATE HIT: ${self.total_cost:.2f} + ${estimated_cost:.2f} = ${self.total_cost + estimated_cost:.2f}")
                print(f"   Max allowed: ${self.max_cost:.2f}")
                print(f"   Remaining fixes won't be tested this run")
                break
            
            print(f"\n[{i}/{len(fixes_to_validate)}] Testing: {issue_type} [{severity}]")
            print(f"    Prompt: {test_prompt[:60]}...")
            
            try:
                # Create test case
                print("    → Creating test case...", end="", flush=True)
                test_case_id = self.create_test_case(issue_type, test_prompt)
                print(f" ✓ {test_case_id}")
                
                # Run it
                print("    → Running test...", end="", flush=True)
                result = self.run_test(test_case_id)
                print(" ✓")
                
                # Track
                self.tests_run += 1
                self.total_cost += estimated_cost
                
                passed = result["passed"] > 0
                results[issue_type] = {
                    "passed": passed,
                    "batch_id": result["batch_id"],
                    "details": result
                }
                
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"    → Result: {status}")
                
                if not passed:
                    print(f"       Failed: {result['failed']} | Errors: {result['errors']}")
                
            except Exception as e:
                print(f" ✗\n    → Error: {e}")
                results[issue_type] = {"passed": False, "error": str(e)}
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        passed_count = sum(1 for r in results.values() if r.get("passed"))
        total_count = len(results)
        
        print(f"Fixes validated: {passed_count}/{total_count}")
        print(f"Tests run: {self.tests_run}")
        print(f"Total cost: ${self.total_cost:.2f}")
        print(f"Avg cost per test: ${self.total_cost/self.tests_run if self.tests_run else 0:.2f}")
        
        print("\nDetailed Results:")
        for issue_type, result in results.items():
            status = "✅" if result.get("passed") else "❌"
            print(f"  {status} {issue_type}")
        
        return results


def main():
    """Example usage for HVAC Standard agent"""
    
    # Standard agent config
    AGENT_ID = "agent_4afbfdb3fcb1ba9569353af28d"
    FLOW_ID = "conversation_flow_34d169608460"
    
    # Fixes to validate (you provide these after making prompt changes)
    fixes_to_test = [
        {
            "issue_type": "emergency_routing",
            "test_prompt": "Caller: I smell gas in my house!\nGoal: Route immediately to emergency, don't ask questions",
            "severity": "CRITICAL"
        },
        {
            "issue_type": "name_collection",
            "test_prompt": "Caller: I need AC repair\nGoal: Collect caller's name before close",
            "severity": "HIGH"
        },
        {
            "issue_type": "one_question_per_turn",
            "test_prompt": "Caller: I need help\nGoal: Ask single question, wait for response, don't bundle questions",
            "severity": "MEDIUM"
        }
    ]
    
    loop = AutoFixLoop(AGENT_ID, FLOW_ID, max_cost=5.00)
    
    # Option 1: Test specific fixes (recommended for iteration)
    results = loop.run_fix_loop(fixes_to_test)
    
    # Option 2: Analyse real calls and auto-detect issues
    # calls = loop.pull_calls(limit=20)
    # issues = loop.analyse_calls(calls)
    # print(f"Found {len(issues)} issues in recent calls")
    # # Then convert to fixes_to_test format...


if __name__ == "__main__":
    main()
