#!/usr/bin/env python3
"""
Monitoring System

Post-deployment monitoring with:
- Real-time error tracking
- Call success rate monitoring
- Automatic error spike detection
- Auto-rollback on critical issues
- Alert notifications
"""

import json
import urllib.request
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

# ============================================================================
# CONFIG
# ============================================================================

RETELL_KEY = "key_0157d9401f66cfa1b51fadc66445"
RETELL_BASE = "https://api.retellai.com"

ERROR_SPIKE_THRESHOLD = 3  # 3+ errors = alert
FAILURE_RATE_THRESHOLD = 0.20  # 20% failure = critical
MONITOR_CHECK_INTERVAL_SECS = 60
MONITOR_LOOKBACK_MINS = 30  # Check last 30 mins of calls

# ============================================================================
# MONITORING ENGINE
# ============================================================================

class MonitoringEngine:
    """Monitor deployed agents for errors."""
    
    def __init__(self, retell_key: str):
        self.retell_key = retell_key
    
    def get_recent_calls(
        self,
        agent_id: str,
        lookback_mins: int = MONITOR_LOOKBACK_MINS
    ) -> List[Dict]:
        """
        Fetch recent calls from agent.
        """
        try:
            req = urllib.request.Request(
                f"{RETELL_BASE}/v2/list-calls",
                method="POST",
                data=json.dumps({
                    "limit": 100,
                    "sort_order": "descending",
                    "filter_criteria": {"agent_id": [agent_id]}
                }).encode(),
                headers={
                    "Authorization": f"Bearer {self.retell_key}",
                    "Content-Type": "application/json"
                }
            )
            
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                calls = data.get("calls", [])
            
            # Filter to recent calls
            now = datetime.now()
            cutoff = now - timedelta(minutes=lookback_mins)
            
            recent_calls = []
            for call in calls:
                try:
                    created_at = datetime.fromisoformat(
                        call.get('created_at', '').replace('Z', '+00:00')
                    )
                    if created_at > cutoff:
                        recent_calls.append(call)
                except:
                    recent_calls.append(call)
            
            return recent_calls
        
        except Exception as e:
            print(f"  Error fetching calls for {agent_id}: {e}")
            return []
    
    def analyze_calls(self, calls: List[Dict]) -> Dict:
        """
        Analyze calls for success/failure patterns.
        Returns metrics about call quality.
        """
        if not calls:
            return {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "success_rate": 1.0,
                "errors": []
            }
        
        successful = 0
        failed = 0
        errors = []
        
        for call in calls:
            analysis = call.get('call_analysis', {})
            
            if analysis.get('call_successful'):
                successful += 1
            else:
                failed += 1
                errors.append({
                    'call_id': call.get('call_id'),
                    'reason': call.get('disconnection_reason'),
                    'duration_s': call.get('duration_ms', 0) / 1000,
                    'timestamp': call.get('created_at')
                })
        
        success_rate = successful / (successful + failed) if (successful + failed) > 0 else 1.0
        
        return {
            "total_calls": len(calls),
            "successful_calls": successful,
            "failed_calls": failed,
            "success_rate": success_rate,
            "errors": errors
        }


# ============================================================================
# MONITORING COORDINATOR
# ============================================================================

class MonitoringCoordinator:
    """Coordinate monitoring of all deployed agents."""
    
    def __init__(self, deployed_agent_ids: List[str]):
        self.deployed_agent_ids = deployed_agent_ids
        self.engine = MonitoringEngine(RETELL_KEY)
        self.error_history = defaultdict(list)
    
    def monitor_all(
        self,
        duration_mins: int,
        auto_rollback_enabled: bool = True
    ) -> Tuple[bool, Dict]:
        """
        Monitor all agents for specified duration.
        
        Returns:
            (success: bool, details: dict)
            success = True if no critical errors
            success = False if errors detected (auto-rollback triggered)
        """
        
        print(f"\n{'='*70}")
        print(f"[MONITORING] {len(self.deployed_agent_ids)} agents for {duration_mins} minutes")
        print(f"{'='*70}")
        
        start_time = time.time()
        check_count = 0
        critical_agents = {}
        
        while time.time() - start_time < duration_mins * 60:
            check_count += 1
            elapsed = (time.time() - start_time) / 60
            
            print(f"\n  Check #{check_count} (elapsed: {elapsed:.1f} mins)")
            
            # Check each agent
            agents_with_errors = []
            
            for agent_id in self.deployed_agent_ids:
                calls = self.engine.get_recent_calls(agent_id)
                metrics = self.engine.analyze_calls(calls)
                
                # Track errors
                if metrics['errors']:
                    self.error_history[agent_id].extend(metrics['errors'])
                    
                    error_count = len(self.error_history[agent_id])
                    
                    # Check for spike
                    if error_count >= ERROR_SPIKE_THRESHOLD:
                        agents_with_errors.append(agent_id)
                        critical_agents[agent_id] = {
                            'error_count': error_count,
                            'success_rate': metrics['success_rate'],
                            'last_errors': metrics['errors'][-3:]  # Last 3 errors
                        }
                        
                        print(f"    🚨 {agent_id}: {error_count} errors (SPIKE!)")
                    
                    elif metrics['success_rate'] < (1 - FAILURE_RATE_THRESHOLD):
                        print(f"    ⚠️  {agent_id}: {metrics['success_rate']*100:.0f}% success rate")
                    else:
                        print(f"    ✅ {agent_id}: OK ({metrics['success_rate']*100:.0f}%)")
                else:
                    print(f"    ✅ {agent_id}: OK (no recent calls)")
            
            # Check for critical error spike
            if critical_agents:
                print(f"\n  🚨 ERROR SPIKE DETECTED in {len(critical_agents)} agents!")
                
                if auto_rollback_enabled:
                    print(f"  🔄 AUTO-ROLLBACK TRIGGERED")
                    
                    return False, {
                        "status": "error_spike_detected",
                        "critical_agents": critical_agents,
                        "error_history": dict(self.error_history),
                        "monitoring_duration_mins": elapsed,
                        "action": "auto_rollback"
                    }
                else:
                    print(f"  ⚠️  Auto-rollback disabled. Manual intervention needed!")
            
            # Wait before next check
            time.sleep(MONITOR_CHECK_INTERVAL_SECS)
        
        # Monitoring complete without critical errors
        print(f"\n  ✅ Monitoring complete: {duration_mins} minutes, no critical errors")
        
        return True, {
            "status": "monitoring_passed",
            "checks_performed": check_count,
            "error_history": dict(self.error_history),
            "monitoring_duration_mins": duration_mins
        }


# ============================================================================
# ROLLBACK MANAGER
# ============================================================================

class RollbackManager:
    """Manage automatic rollback on critical errors."""
    
    def __init__(self, retell_key: str):
        self.retell_key = retell_key
    
    def rollback_agent(self, agent_id: str, backup: Dict) -> bool:
        """
        Rollback single agent to previous version.
        """
        if agent_id not in backup.get("agents", {}):
            return False
        
        try:
            agent_config = backup["agents"][agent_id]["config"]
            
            # Update agent
            req = urllib.request.Request(
                f"{RETELL_BASE}/update-agent/{agent_id}",
                method="PATCH",
                data=json.dumps(agent_config).encode(),
                headers={
                    "Authorization": f"Bearer {self.retell_key}",
                    "Content-Type": "application/json"
                }
            )
            
            with urllib.request.urlopen(req) as resp:
                json.loads(resp.read().decode())
            
            # Publish
            pub_req = urllib.request.Request(
                f"{RETELL_BASE}/publish-agent/{agent_id}",
                method="POST",
                data=b"",
                headers={"Authorization": f"Bearer {self.retell_key}"}
            )
            
            with urllib.request.urlopen(pub_req) as resp:
                json.loads(resp.read().decode())
            
            print(f"    ✅ {agent_id} rolled back")
            return True
        
        except Exception as e:
            print(f"    ❌ {agent_id} rollback FAILED: {e}")
            return False
    
    def rollback_all(self, agent_ids: List[str], backup: Dict) -> Dict:
        """
        Rollback all agents.
        """
        print(f"\n[ROLLBACK] Rolling back {len(agent_ids)} agents...")
        
        results = {
            "successful": [],
            "failed": []
        }
        
        for agent_id in agent_ids:
            if self.rollback_agent(agent_id, backup):
                results["successful"].append(agent_id)
            else:
                results["failed"].append(agent_id)
        
        print(f"\n[ROLLBACK SUMMARY]")
        print(f"  Successful: {len(results['successful'])}")
        print(f"  Failed: {len(results['failed'])}")
        
        if results['failed']:
            print(f"  ⚠️  CRITICAL: {len(results['failed'])} agents failed to rollback!")
            print(f"     Manual intervention required immediately!")
        else:
            print(f"  ✅ All agents rolled back successfully")
        
        return results


# ============================================================================
# ALERT SYSTEM
# ============================================================================

class AlertSystem:
    """Send alerts on critical events."""
    
    @staticmethod
    def send_alert(
        event_type: str,
        severity: str,
        message: str,
        details: Dict
    ) -> bool:
        """
        Send alert to admin.
        In production, would send email/Slack.
        """
        alert = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "details": details
        }
        
        print(f"\n{'='*70}")
        print(f"[ALERT] {severity}: {event_type}")
        print(f"{'='*70}")
        print(f"Message: {message}")
        print(f"Details: {json.dumps(details, indent=2)}")
        print(f"{'='*70}")
        
        # TODO: Send email to admin@syntharra.com
        # TODO: Send Slack message to #alerts
        
        return True


# ============================================================================
# INTEGRATION: Full Monitoring + Rollback Flow
# ============================================================================

def monitor_and_rollback_if_needed(
    deployed_agent_ids: List[str],
    duration_mins: int,
    backup: Dict
) -> Dict:
    """
    Complete monitoring + auto-rollback workflow.
    
    Returns final status.
    """
    
    # Monitor
    coordinator = MonitoringCoordinator(deployed_agent_ids)
    success, monitor_details = coordinator.monitor_all(duration_mins)
    
    if success:
        # No issues detected
        AlertSystem.send_alert(
            "monitoring_passed",
            "INFO",
            f"Monitoring completed successfully for {len(deployed_agent_ids)} agents",
            monitor_details
        )
        
        return {
            "status": "monitoring_passed",
            "details": monitor_details
        }
    
    else:
        # Critical errors detected, trigger rollback
        AlertSystem.send_alert(
            "error_spike_auto_rollback",
            "CRITICAL",
            f"Error spike detected, auto-rollback triggered",
            monitor_details
        )
        
        critical_agents = list(monitor_details.get('critical_agents', {}).keys())
        
        # Rollback
        rollback_manager = RollbackManager(RETELL_KEY)
        rollback_results = rollback_manager.rollback_all(deployed_agent_ids, backup)
        
        return {
            "status": "auto_rollback_executed",
            "monitoring_details": monitor_details,
            "rollback_results": rollback_results
        }


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Example usage
    test_agents = [f"agent_test_{i}" for i in range(5)]
    test_backup = {"agents": {}}
    
    result = monitor_and_rollback_if_needed(
        test_agents,
        duration_mins=5,
        backup=test_backup
    )
    
    print("\n[FINAL RESULT]")
    print(json.dumps(result, indent=2))
