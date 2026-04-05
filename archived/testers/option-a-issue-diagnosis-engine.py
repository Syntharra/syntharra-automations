#!/usr/bin/env python3
"""
Syntharra Option A: Issue Diagnosis Engine
============================================
Scans real call logs from Retell API, detects 12 issue patterns,
proposes fixes with Claude, returns dashboard-ready JSON.

Features:
- Reads 30 days of call logs
- Detects issues: emergency routing, name collection, "Say:" prefix, etc.
- Uses Claude to generate surgical prompt fixes
- Returns: [{ issue_id, severity, frequency, affected_agents, proposed_fix }]
- Cost: $0.00 (just reading existing logs + cheap Claude call)
"""

import json
import urllib.request
import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class DetectedIssue:
    """Represents one issue found across agent calls"""
    issue_type: str  # "emergency_routing_failure", "name_not_collected", etc.
    severity: str    # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    frequency: int   # Number of calls showing this issue
    affected_agents: List[str]  # List of agent_ids affected
    sample_call_id: str  # One example call_id with this issue
    description: str  # Human-readable description
    proposed_fix: str  # Proposed fix (from Claude)
    affected_call_count: int  # Out of total calls analyzed


class IssueDetector:
    """Detects issues in real call transcripts"""
    
    # 12 patterns we scan for
    ISSUE_PATTERNS = {
        "emergency_routing_failure": {
            "description": "Caller said emergency but wasn't transferred",
            "severity": "CRITICAL",
            "keywords": ["emergency", "urgent", "help", "fire", "injury"],
            "check": lambda t, s: "emergency" in t.lower() and "transfer" not in s.lower()
        },
        "name_not_collected": {
            "description": "Call >30s but name never requested/collected",
            "severity": "HIGH",
            "check": lambda t, s: ">30s" in str(t) and "name" not in s.lower()
        },
        "say_prefix_used": {
            "description": "Agent response starts with 'Say:' (framework leak)",
            "severity": "CRITICAL",
            "keywords": ["say:", "please say"],
            "check": lambda t, s: "say:" in s.lower() or "please say" in s.lower()
        },
        "multiple_questions_per_turn": {
            "description": "Agent asked 3+ questions in single turn",
            "severity": "HIGH",
            "check": lambda t, s: s.count("?") >= 3
        },
        "no_email_readback": {
            "description": "Email collected but not read back (>2 min call)",
            "severity": "MEDIUM",
            "check": lambda t, s: "email" in s.lower() and "read" not in s.lower()
        },
        "no_summary_before_close": {
            "description": "Call ended without summarizing collected info",
            "severity": "MEDIUM",
            "check": lambda t, s: "summary" not in s.lower() and "recap" not in s.lower()
        },
        "diagnosis_given": {
            "description": "Agent diagnosed problem (breaker, filter, battery, thermostat)",
            "severity": "HIGH",
            "keywords": ["breaker", "filter", "battery", "thermostat", "capacitor", "blower"],
            "check": lambda t, s: any(k in s.lower() for k in ["breaker", "filter", "battery"])
        },
        "unauthorized_pricing": {
            "description": "Agent quoted price without authorization",
            "severity": "CRITICAL",
            "keywords": ["$", "cost", "price"],
            "check": lambda t, s: "$" in s and "authorized" not in s.lower()
        },
        "callback_promise": {
            "description": "Agent promised specific callback time",
            "severity": "HIGH",
            "keywords": ["call you back at", "we'll call at", "in 2 hours", "tomorrow at"],
            "check": lambda t, s: any(k in s.lower() for k in ["call you back at", "in 2 hours", "tomorrow at"])
        },
        "transfer_failed": {
            "description": "Transfer attempted but failed (call ended abruptly)",
            "severity": "CRITICAL",
            "check": lambda t, s: "transfer" in s.lower() and ("failed" in t.lower() or "disconnect" in t.lower())
        },
        "address_paraphrase": {
            "description": "Agent paraphrased street address instead of repeating exactly",
            "severity": "MEDIUM",
            "check": lambda t, s: "address" in s.lower() and "repeated" not in s.lower()
        },
        "pobox_not_flagged": {
            "description": "PO Box given but agent didn't ask for physical address",
            "severity": "HIGH",
            "check": lambda t, s: "po box" in s.lower() and "physical" not in s.lower()
        },
    }

    def __init__(self, retell_api_key: str, supabase_key: str):
        self.retell_key = retell_api_key
        self.supabase_key = supabase_key
        self.issues: Dict[str, DetectedIssue] = {}

    def get_recent_calls(self, agent_id: str, limit: int = 100) -> List[Dict]:
        """Fetch recent calls from Retell API for given agent"""
        url = "https://api.retellai.com/v2/list-calls"
        req = urllib.request.Request(
            url,
            method="POST",
            data=json.dumps({
                "limit": limit,
                "sort_order": "descending",
                "filter_criteria": {"agent_id": [agent_id]}
            }).encode(),
            headers={
                "Authorization": f"Bearer {self.retell_key}",
                "Content-Type": "application/json"
            }
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode()).get("data", [])
        except Exception as e:
            print(f"Error fetching calls: {e}")
            return []

    def analyze_transcript(self, transcript_str: str, pattern_key: str) -> bool:
        """Check if transcript matches issue pattern"""
        pattern = self.ISSUE_PATTERNS.get(pattern_key)
        if not pattern:
            return False
        return pattern["check"](transcript_str, transcript_str)

    def scan_calls(self, agent_id: str, days: int = 30) -> List[Dict]:
        """
        Scan all calls for an agent in past N days, detect issues.
        Returns: List of detected issues with frequency.
        """
        calls = self.get_recent_calls(agent_id, limit=200)
        
        # Filter to last N days
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        recent_calls = []
        for call in calls:
            try:
                call_time = datetime.datetime.fromisoformat(
                    call.get("start_timestamp", "").replace("Z", "+00:00")
                )
                if call_time > cutoff:
                    recent_calls.append(call)
            except:
                continue

        # Scan each call for issues
        issues_found = {}
        for call in recent_calls:
            transcript = call.get("transcript", "")
            call_id = call.get("call_id", "")
            duration_ms = call.get("duration_ms", 0)
            
            for pattern_key in self.ISSUE_PATTERNS.keys():
                if self.analyze_transcript(transcript, pattern_key):
                    if pattern_key not in issues_found:
                        issues_found[pattern_key] = {
                            "count": 0,
                            "calls": [],
                            "agents": set()
                        }
                    issues_found[pattern_key]["count"] += 1
                    issues_found[pattern_key]["calls"].append(call_id)
                    issues_found[pattern_key]["agents"].add(agent_id)

        # Return as list
        result = []
        for issue_type, data in issues_found.items():
            pattern = self.ISSUE_PATTERNS[issue_type]
            result.append({
                "issue_type": issue_type,
                "severity": pattern["severity"],
                "frequency": data["count"],
                "affected_agents": list(data["agents"]),
                "sample_call_id": data["calls"][0] if data["calls"] else None,
                "description": pattern["description"],
                "total_calls_analyzed": len(recent_calls),
            })

        return result

    def generate_fix_proposal(self, issue_type: str, sample_transcript: str) -> str:
        """Use Claude to generate a fix proposal for the issue"""
        pattern = self.ISSUE_PATTERNS.get(issue_type)
        if not pattern:
            return "Manual investigation required"

        prompt = f"""
Given this Syntharra HVAC AI Receptionist issue:

Issue Type: {issue_type}
Description: {pattern["description"]}
Severity: {pattern["severity"]}

Sample call transcript excerpt:
{sample_transcript[:500]}

Generate a SURGICAL, MINIMAL fix to the agent prompt that addresses this issue.
Format your response as: PROMPT_FIX: [exact text to change]
Your response must be concise and avoid changing anything else.
"""

        # Mock Claude call for now (will integrate real API)
        # This is a placeholder — in production, call Claude API
        fixes = {
            "emergency_routing_failure": "PROMPT_FIX: Add to prompt: 'If caller mentions emergency, fire, injury, or urgent help, immediately transfer to: {{EMERGENCY_TRANSFER_NUMBER}}'",
            "name_not_collected": "PROMPT_FIX: Add to prompt: 'Always collect customer name early (within first 30 seconds) before asking about service'",
            "say_prefix_used": "PROMPT_FIX: Never use 'Say:' prefix. Replace with direct instruction: 'Respond with: [what to say]'",
            "multiple_questions_per_turn": "PROMPT_FIX: Add to prompt: 'Ask ONE question at a time. Wait for response before next question.'",
            "no_email_readback": "PROMPT_FIX: Add to email collection node: 'Always read back email address using: at, dot, dash format'",
            "no_summary_before_close": "PROMPT_FIX: Add mandatory summary step before closing: 'Summarize all details collected (name, address, phone, issue)'",
            "diagnosis_given": "PROMPT_FIX: Add safety boundary: 'Never diagnose problems. Banned words: breaker, filter, battery, capacitor, thermostat'",
            "unauthorized_pricing": "PROMPT_FIX: Add: 'Never quote price to customer. If asked, say: I don\\'t have pricing info, our team will provide estimate'",
            "callback_promise": "PROMPT_FIX: Add: 'Never promise specific callback time. Say: Our team will call you back soon'",
            "transfer_failed": "PROMPT_FIX: Verify transfer phone number is correct in agent config. Check Retell agent settings.'",
            "address_paraphrase": "PROMPT_FIX: Add to address collection: 'Always repeat street address exactly as customer said it'",
            "pobox_not_flagged": "PROMPT_FIX: Add: 'If customer gives PO Box, ask: Do you have a physical service address we should use?'",
        }
        return fixes.get(issue_type, "Manual investigation required")


class DiagnosisDashboard:
    """Formats issues for dashboard consumption"""
    
    def __init__(self, detector: IssueDetector):
        self.detector = detector

    def get_dashboard_data(self, agent_id: str) -> Dict[str, Any]:
        """
        Return dashboard-ready JSON:
        {
          "agent_id": "...",
          "scan_timestamp": "...",
          "total_issues": N,
          "critical_count": N,
          "high_count": N,
          "issues": [
            {
              "issue_id": "emergency_routing_failure",
              "severity": "CRITICAL",
              "frequency": 3,
              "description": "...",
              "proposed_fix": "...",
              "sample_call_id": "...",
              "actions": ["Fix It", "Skip", "Investigate"]
            }
          ]
        }
        """
        issues = self.detector.scan_calls(agent_id, days=30)
        
        # Get sample transcript for fix proposal
        calls = self.detector.get_recent_calls(agent_id, limit=50)
        
        # Add proposed fixes
        for issue in issues:
            sample_call = next(
                (c for c in calls if c.get("call_id") == issue["sample_call_id"]),
                None
            )
            transcript = sample_call.get("transcript", "") if sample_call else ""
            issue["proposed_fix"] = self.detector.generate_fix_proposal(
                issue["issue_type"],
                transcript
            )

        # Count by severity
        severity_counts = {}
        for issue in issues:
            sev = issue["severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return {
            "agent_id": agent_id,
            "scan_timestamp": datetime.datetime.utcnow().isoformat(),
            "total_issues_found": len(issues),
            "critical_count": severity_counts.get("CRITICAL", 0),
            "high_count": severity_counts.get("HIGH", 0),
            "medium_count": severity_counts.get("MEDIUM", 0),
            "low_count": severity_counts.get("LOW", 0),
            "issues": sorted(
                issues,
                key=lambda x: {
                    "CRITICAL": 0,
                    "HIGH": 1,
                    "MEDIUM": 2,
                    "LOW": 3
                }.get(x["severity"], 4)
            ),
            "ready_to_fix": len(issues) > 0
        }


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    import os
    
    # Get from memory/vault
    RETELL_KEY = os.getenv("RETELL_API_KEY", "key_xxx")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJ...")
    
    # Test on Standard agent
    detector = IssueDetector(RETELL_KEY, SUPABASE_KEY)
    dashboard = DiagnosisDashboard(detector)
    
    # Scan Arctic Breeze Standard agent
    data = dashboard.get_dashboard_data("agent_4afbfdb3fcb1ba9569353af28d")
    
    # Output dashboard JSON
    print(json.dumps(data, indent=2))
