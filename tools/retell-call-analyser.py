#!/usr/bin/env python3
"""
Syntharra Call Log Analyser
Pulls call history from Retell API and analyses for issues.
Run this in any Claude session — paste the output back for recommendations.

Usage: python3 retell_call_analyser.py [--days 7] [--limit 50] [--agent AGENT_ID]
"""

import json
import urllib.request
import sys
from datetime import datetime, timedelta

# Config
RETELL_KEY = "key_0157d9401f66cfa1b51fadc66445"
DEFAULT_AGENT = "agent_4afbfdb3fcb1ba9569353af28d"

def list_calls(limit=50, agent_id=None):
    """Pull calls from Retell API"""
    payload = {"limit": limit, "sort_order": "descending"}
    if agent_id:
        payload["filter_criteria"] = {"agent_id": [agent_id]}
    
    req = urllib.request.Request(
        "https://api.retellai.com/v2/list-calls",
        method="POST",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {RETELL_KEY}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def analyse_call(call):
    """Analyse a single call for issues"""
    issues = []
    call_id = call.get('call_id', 'unknown')
    transcript = call.get('transcript', '')
    analysis = call.get('call_analysis', {})
    duration = call.get('duration_ms', 0)
    disconnect = call.get('disconnection_reason', '')
    status = call.get('call_status', '')
    tokens = call.get('llm_token_usage', {})
    latency = call.get('latency', {})
    
    # Issue 1: Call not successful
    if not analysis.get('call_successful', True):
        issues.append({
            'severity': 'HIGH',
            'type': 'call_failed',
            'detail': f"Call marked unsuccessful. Summary: {analysis.get('call_summary', 'N/A')}"
        })
    
    # Issue 2: Negative sentiment
    sentiment = analysis.get('user_sentiment', 'Neutral')
    if sentiment and sentiment.lower() in ['negative', 'very negative', 'angry', 'frustrated']:
        issues.append({
            'severity': 'HIGH',
            'type': 'negative_sentiment',
            'detail': f"User sentiment: {sentiment}"
        })
    
    # Issue 3: Abnormal disconnection
    if disconnect in ['agent_hangup', 'error', 'machine_detected']:
        issues.append({
            'severity': 'MEDIUM',
            'type': 'abnormal_disconnect',
            'detail': f"Disconnection reason: {disconnect}"
        })
    
    # Issue 4: Very short call (under 15 seconds — likely spam or error)
    if duration and duration < 15000 and disconnect != 'machine_detected':
        issues.append({
            'severity': 'LOW',
            'type': 'very_short_call',
            'detail': f"Call only {duration/1000:.0f} seconds"
        })
    
    # Issue 5: Very long call (over 5 minutes — might be stuck)
    if duration and duration > 300000:
        issues.append({
            'severity': 'MEDIUM',
            'type': 'very_long_call',
            'detail': f"Call was {duration/60000:.1f} minutes"
        })
    
    # Issue 6: High token usage (over 6000 average)
    avg_tokens = tokens.get('average', 0)
    if avg_tokens > 6000:
        issues.append({
            'severity': 'LOW',
            'type': 'high_token_usage',
            'detail': f"Average {avg_tokens} tokens per turn"
        })
    
    # Issue 7: High latency (LLM p50 over 1000ms)
    llm_latency = latency.get('llm', {})
    if llm_latency.get('p50', 0) > 1000:
        issues.append({
            'severity': 'MEDIUM',
            'type': 'high_latency',
            'detail': f"LLM p50 latency: {llm_latency.get('p50', 0)}ms"
        })
    
    # Transcript-based analysis
    t_lower = transcript.lower()
    
    # Issue 8: Agent diagnosed/troubleshot
    diag_phrases = ['check the breaker', 'check your filter', 'try resetting', 'replace the batteries',
                    'check the thermostat', 'try turning it off and on', 'check the fuse']
    for phrase in diag_phrases:
        if phrase in t_lower:
            issues.append({
                'severity': 'HIGH',
                'type': 'agent_diagnosed',
                'detail': f"Agent gave troubleshooting advice: '{phrase}'"
            })
            break
    
    # Issue 9: Agent quoted prices it shouldn't have
    price_patterns = ['$', 'dollars per hour', 'hourly rate', 'typically costs', 'usually runs',
                      'average price', 'roughly', 'ballpark']
    # Exclude known allowed prices
    allowed_prices = ['$89', '$129', '$50 surcharge', '$50 off', '$3,000', '$300']
    for pattern in price_patterns:
        if pattern in t_lower:
            # Check if it's in an agent turn and not an allowed price
            lines = transcript.split('\n')
            for line in lines:
                if line.startswith('Agent:') and pattern in line.lower():
                    is_allowed = any(ap.lower() in line.lower() for ap in allowed_prices)
                    if not is_allowed and pattern == '$':
                        # Dollar sign could be in allowed prices, skip
                        continue
                    if not is_allowed:
                        issues.append({
                            'severity': 'CRITICAL',
                            'type': 'price_leaked',
                            'detail': f"Agent may have quoted unauthorized price: {line[:100]}"
                        })
                        break
    
    # Issue 10: Agent asked multiple questions
    lines = transcript.split('\n')
    for line in lines:
        if line.startswith('Agent:'):
            question_marks = line.count('?')
            if question_marks >= 3:
                issues.append({
                    'severity': 'MEDIUM',
                    'type': 'multiple_questions',
                    'detail': f"Agent asked {question_marks} questions in one turn: {line[:120]}..."
                })
                break
    
    # Issue 11: Agent didn't collect name
    agent_asked_name = any(x in t_lower for x in ['your name', 'your full name', 'first name', 'last name'])
    if duration > 30000 and not agent_asked_name and 'spam' not in t_lower:
        issues.append({
            'severity': 'HIGH',
            'type': 'no_name_collected',
            'detail': "Agent did not appear to ask for caller's name"
        })
    
    # Issue 12: No summary/readback before closing
    closing_phrases = ['passed all of that', 'someone will be in touch', 'team will call', 'have a great day']
    summary_phrases = ['just to confirm', 'to summarise', 'so i have', 'let me confirm']
    has_close = any(p in t_lower for p in closing_phrases)
    has_summary = any(p in t_lower for p in summary_phrases)
    if has_close and not has_summary and duration > 60000:
        issues.append({
            'severity': 'MEDIUM',
            'type': 'no_summary',
            'detail': "Call ended without confirming details back to caller"
        })
    
    return issues

def generate_report(calls):
    """Generate analysis report from call data"""
    
    total_calls = len(calls)
    all_issues = []
    calls_with_issues = 0
    
    for call in calls:
        issues = analyse_call(call)
        if issues:
            calls_with_issues += 1
            for issue in issues:
                issue['call_id'] = call.get('call_id', '')
                issue['call_summary'] = call.get('call_analysis', {}).get('call_summary', '')
                issue['duration'] = call.get('duration_ms', 0)
                all_issues.append(issue)
    
    # Group by issue type
    issue_groups = {}
    for issue in all_issues:
        itype = issue['type']
        if itype not in issue_groups:
            issue_groups[itype] = {'severity': issue['severity'], 'occurrences': [], 'count': 0}
        issue_groups[itype]['occurrences'].append(issue)
        issue_groups[itype]['count'] += 1
    
    # Sort by severity then count
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    sorted_groups = sorted(issue_groups.items(), 
                          key=lambda x: (severity_order.get(x[1]['severity'], 4), -x[1]['count']))
    
    # Build report
    report = []
    report.append("# Syntharra Call Log Analysis Report")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"**Calls analysed:** {total_calls}")
    report.append(f"**Calls with issues:** {calls_with_issues} ({calls_with_issues/max(total_calls,1)*100:.0f}%)")
    report.append(f"**Total issues found:** {len(all_issues)}")
    report.append("")
    
    # Summary counts
    sev_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    for issue in all_issues:
        sev_counts[issue['severity']] = sev_counts.get(issue['severity'], 0) + 1
    
    report.append("## Severity Breakdown")
    report.append(f"- CRITICAL: {sev_counts.get('CRITICAL', 0)}")
    report.append(f"- HIGH: {sev_counts.get('HIGH', 0)}")
    report.append(f"- MEDIUM: {sev_counts.get('MEDIUM', 0)}")
    report.append(f"- LOW: {sev_counts.get('LOW', 0)}")
    report.append("")
    
    # Issue details
    report.append("## Issues by Type (sorted by severity × frequency)")
    report.append("")
    
    for itype, group in sorted_groups:
        report.append(f"### [{group['severity']}] {itype} — {group['count']} occurrence(s)")
        for occ in group['occurrences'][:3]:  # Show max 3 examples
            report.append(f"- {occ['detail']}")
            if occ.get('call_summary'):
                report.append(f"  Call: {occ['call_summary'][:150]}")
        if group['count'] > 3:
            report.append(f"- ...and {group['count'] - 3} more")
        report.append("")
    
    # Call quality stats
    report.append("## Call Quality Stats")
    durations = [c.get('duration_ms', 0) for c in calls if c.get('duration_ms')]
    if durations:
        avg_dur = sum(durations) / len(durations)
        report.append(f"- Average call duration: {avg_dur/60000:.1f} minutes")
    
    sentiments = [c.get('call_analysis', {}).get('user_sentiment', '') for c in calls]
    sentiment_counts = {}
    for s in sentiments:
        if s:
            sentiment_counts[s] = sentiment_counts.get(s, 0) + 1
    if sentiment_counts:
        report.append(f"- Sentiment distribution: {json.dumps(sentiment_counts)}")
    
    success_count = sum(1 for c in calls if c.get('call_analysis', {}).get('call_successful', False))
    report.append(f"- Successful calls: {success_count}/{total_calls} ({success_count/max(total_calls,1)*100:.0f}%)")
    
    tokens_avg = [c.get('llm_token_usage', {}).get('average', 0) for c in calls if c.get('llm_token_usage', {}).get('average')]
    if tokens_avg:
        report.append(f"- Average tokens per turn: {sum(tokens_avg)/len(tokens_avg):.0f}")
    
    return '\n'.join(report)


# Main execution
if __name__ == '__main__':
    limit = 50
    agent_id = DEFAULT_AGENT
    
    # Parse args
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == '--limit' and i+1 < len(args):
            limit = int(args[i+1])
        if arg == '--agent' and i+1 < len(args):
            agent_id = args[i+1]
    
    print(f"Pulling last {limit} calls for agent {agent_id}...")
    calls = list_calls(limit=limit, agent_id=agent_id)
    print(f"Got {len(calls)} calls")
    
    report = generate_report(calls)
    print(report)
    
    # Save report
    with open('/home/claude/call_analysis_report.md', 'w') as f:
        f.write(report)
    print(f"\nReport saved to /home/claude/call_analysis_report.md")

