#!/usr/bin/env python3
"""
n8n Integration Wrapper

Provides HTTP endpoints that n8n calls for each step of the self-healing loop.
Wraps the production Python modules and handles n8n data formats.

Run as:
  python3 n8n-integration-wrapper.py --host 0.0.0.0 --port 5000
"""

from flask import Flask, request, jsonify
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any
import subprocess
import logging

# ============================================================================
# SETUP
# ============================================================================

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment
RETELL_KEY = os.getenv('RETELL_API_KEY', 'key_0157d9401f66cfa1b51fadc66445')
MASTER_AGENT_ID = os.getenv('MASTER_AGENT_ID', 'agent_4afbfdb3fcb1ba9569353af28d')
MASTER_FLOW_ID = os.getenv('MASTER_FLOW_ID', 'conversation_flow_34d169608460')
SUPABASE_URL = os.getenv('SUPABASE_URL', 'hgheyqwnrcvwtgngqdnq.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@syntharra.com')

# Paths to Python modules
TOOLS_PATH = '/path/to/syntharra-automations/tools'

# ============================================================================
# STEP 1: DIAGNOSE
# ============================================================================

@app.route('/webhook/self-healing-diagnose', methods=['POST'])
def diagnose():
    """
    Step 1: Diagnose - Aggregate calls and detect issues
    
    n8n input: {trigger_time, environment, master_agent_id, master_flow_id}
    Returns: {status, issues, master_flow, client_agents, cost, ...}
    """
    try:
        input_data = request.get_json()
        
        logger.info(f"[DIAGNOSE] Starting diagnosis at {input_data.get('trigger_time')}")
        
        # Import and run diagnosis
        sys.path.insert(0, TOOLS_PATH)
        from self_healing_loop_production import IssueDetector
        
        # Get all client agents from Supabase
        client_agents = get_client_agents_from_supabase()
        client_agent_ids = [a['agent_id'] for a in client_agents]
        
        # Run diagnosis
        detector = IssueDetector()
        issues = detector.diagnose(client_agent_ids, limit_per_agent=50)
        
        logger.info(f"[DIAGNOSE] Found {len(issues)} issues")
        
        if not issues:
            return jsonify({
                "status": "healthy",
                "issues": [],
                "cost": COST_PER_DIAGNOSIS,
                "timestamp": datetime.now().isoformat()
            })
        
        # Get master flow for next step
        master_flow = get_master_flow()
        
        return jsonify({
            "status": "issues_detected",
            "issues": issues,
            "issue_count": len(issues),
            "top_issue": issues[0] if issues else None,
            "master_flow": master_flow,
            "client_agents": client_agents,
            "cost": COST_PER_DIAGNOSIS,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"[DIAGNOSE] Error: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


# ============================================================================
# STEP 2: VALIDATE
# ============================================================================

@app.route('/webhook/self-healing-validate', methods=['POST'])
def validate():
    """
    Step 2: Validate - Multiple validation layers before deployment
    
    n8n input: {issues, master_flow, client_agents}
    Returns: {status, validation_passed, error_details, version, backup_id, ...}
    """
    try:
        input_data = request.get_json()
        
        logger.info("[VALIDATE] Starting validation")
        
        sys.path.insert(0, TOOLS_PATH)
        from self_healing_loop_production import ValidationLayer
        from safety_checks import (
            VariableInjectionValidator,
            FlowSyntaxValidator,
            PreDeploymentChecklist
        )
        
        issues = input_data.get('issues', [])
        master_flow = input_data.get('master_flow', {})
        client_agents = input_data.get('client_agents', [])
        
        all_checks_passed = True
        validation_results = []
        
        # Check 1: Variable injection
        logger.info("  Check 1: Variable injection")
        all_valid, var_errors = VariableInjectionValidator.validate_all_clients(client_agents)
        validation_results.append({
            "check": "variable_injection",
            "passed": all_valid,
            "errors": var_errors[:5]  # First 5 errors
        })
        all_checks_passed = all_checks_passed and all_valid
        
        # Check 2: Flow syntax
        logger.info("  Check 2: Flow syntax")
        flow_valid, flow_error = FlowSyntaxValidator.validate_flow_structure(master_flow)
        validation_results.append({
            "check": "flow_structure",
            "passed": flow_valid,
            "error": flow_error
        })
        all_checks_passed = all_checks_passed and flow_valid
        
        # Check 3: No "Say:" prefix
        logger.info("  Check 3: Say prefix check")
        no_say, say_problems = FlowSyntaxValidator.validate_no_say_prefix(master_flow)
        validation_results.append({
            "check": "no_say_prefix",
            "passed": no_say,
            "problems": say_problems[:5]
        })
        all_checks_passed = all_checks_passed and no_say
        
        # Check 4: Master fix validation
        if issues and all_checks_passed:
            logger.info("  Check 4: Master fix validation")
            validator = ValidationLayer(MASTER_FLOW_ID)
            valid, error = validator.validate_master_fix(issues[0])
            validation_results.append({
                "check": "master_fix",
                "passed": valid,
                "error": error
            })
            all_checks_passed = all_checks_passed and valid
        
        if not all_checks_passed:
            logger.error("[VALIDATE] Validation failed")
            return jsonify({
                "status": "validation_failed",
                "validation_results": validation_results,
                "error_details": validation_results,
                "cost": COST_PER_FIX_VALIDATION,
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # Generate version number
        version = generate_version_number()
        
        # Create backup ID
        backup_id = f"backup_{version}_{datetime.now().isoformat()}"
        
        logger.info(f"[VALIDATE] All checks passed. Version: {version}")
        
        return jsonify({
            "status": "validation_passed",
            "validation_results": validation_results,
            "version": version,
            "backup_id": backup_id,
            "master_flow": master_flow,
            "client_agents": client_agents,
            "cost": COST_PER_FIX_VALIDATION,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"[VALIDATE] Error: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


# ============================================================================
# STEP 3: DEPLOY
# ============================================================================

@app.route('/webhook/self-healing-deploy', methods=['POST'])
def deploy():
    """
    Step 3: Deploy - Safe batch deployment with rollback capability
    
    n8n input: {master_flow, client_agents, version, backup_id}
    Returns: {status, successful_agents, failed_agents, rolled_back_agents, cost, ...}
    """
    try:
        input_data = request.get_json()
        
        logger.info("[DEPLOY] Starting deployment")
        
        sys.path.insert(0, TOOLS_PATH)
        from deployment_workflow import deploy_master_to_all_clients
        
        master_flow = input_data.get('master_flow', {})
        client_agents = input_data.get('client_agents', [])
        version = input_data.get('version', 'unknown')
        backup_id = input_data.get('backup_id')
        
        # Create backup first
        logger.info("  Creating backup...")
        backup = create_backup_in_supabase(client_agents, version, backup_id)
        
        # Deploy
        logger.info("  Deploying to all agents...")
        results = deploy_master_to_all_clients(
            MASTER_FLOW_ID,
            client_agents,
            master_flow,
            version
        )
        
        # Log deployment in Supabase
        log_deployment_in_supabase(version, results, backup_id)
        
        logger.info(f"[DEPLOY] Deployment complete: {len(results.get('successful', []))} successful, {len(results.get('failed', []))} failed")
        
        return jsonify({
            "status": "deployment_success" if not results.get('failed') else "deployment_partial_failure",
            "successful_agents": results.get('successful', []),
            "failed_agents": results.get('failed', []),
            "rolled_back_agents": results.get('rolled_back', []),
            "version": version,
            "cost": COST_PER_DEPLOYMENT,
            "duration_mins": results.get('total_time_mins', 0),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"[DEPLOY] Error: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


# ============================================================================
# STEP 4: MONITOR
# ============================================================================

@app.route('/webhook/self-healing-monitor', methods=['POST'])
def monitor():
    """
    Step 4: Monitor - Real-time error detection and auto-rollback
    
    n8n input: {deployed_agents, duration_mins, version}
    Returns: {status, monitoring_passed, rollback_triggered, details, cost, ...}
    """
    try:
        input_data = request.get_json()
        
        logger.info("[MONITOR] Starting monitoring")
        
        sys.path.insert(0, TOOLS_PATH)
        from monitoring_system import MonitoringCoordinator
        
        deployed_agents = input_data.get('deployed_agents', [])
        duration_mins = input_data.get('duration_mins', 60)
        version = input_data.get('version', 'unknown')
        
        # Monitor
        coordinator = MonitoringCoordinator(deployed_agents)
        success, monitor_details = coordinator.monitor_all(duration_mins)
        
        if not success:
            logger.warning("[MONITOR] Error spike detected, auto-rollback triggered")
            
            return jsonify({
                "status": "monitoring_failed_auto_rollback",
                "monitoring_passed": False,
                "rollback_triggered": True,
                "error_spike": monitor_details.get('critical_agents'),
                "details": monitor_details,
                "cost": COST_PER_MONITORING,
                "timestamp": datetime.now().isoformat()
            })
        
        logger.info("[MONITOR] Monitoring passed, no errors detected")
        
        return jsonify({
            "status": "monitoring_passed",
            "monitoring_passed": True,
            "rollback_triggered": False,
            "checks_performed": monitor_details.get('checks_performed', 0),
            "error_history": monitor_details.get('error_history', {}),
            "cost": COST_PER_MONITORING,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"[MONITOR] Error: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


# ============================================================================
# ALERTS & LOGGING
# ============================================================================

@app.route('/webhook/send-alert', methods=['POST'])
def send_alert():
    """Send alert to admin"""
    try:
        input_data = request.get_json()
        
        event_type = input_data.get('event_type')
        severity = input_data.get('severity', 'INFO')
        to_email = input_data.get('to', ADMIN_EMAIL)
        details = input_data.get('details', {})
        
        logger.info(f"[ALERT] {severity}: {event_type}")
        
        # TODO: Send email via SMTP2GO
        # send_email_alert(to_email, event_type, severity, details)
        
        # TODO: Send Slack alert
        # send_slack_alert(event_type, severity, details)
        
        # Log to Supabase
        log_alert_in_supabase(event_type, severity, to_email, details)
        
        return jsonify({
            "status": "alert_sent",
            "event_type": event_type,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"[ALERT] Error: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route('/webhook/log-cycle', methods=['POST'])
def log_cycle():
    """Log deployment cycle to Supabase"""
    try:
        input_data = request.get_json()
        
        logger.info("[LOG] Logging cycle to Supabase")
        
        cycle_data = {
            "cycle_date": input_data.get('cycle_timestamp', datetime.now()).split('T')[0],
            "cycle_timestamp": input_data.get('cycle_timestamp'),
            "status": input_data.get('status'),
            "issues_detected": input_data.get('issues_detected', 0),
            "agents_deployed": input_data.get('agents_deployed', 0),
            "total_cost": input_data.get('total_cost', 0),
            "duration_mins": input_data.get('duration_mins', 0)
        }
        
        # Log to Supabase
        log_cycle_in_supabase(cycle_data)
        
        return jsonify({
            "status": "cycle_logged",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"[LOG] Error: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_client_agents_from_supabase() -> list:
    """Fetch all active client agents from Supabase"""
    # TODO: Implement Supabase query
    # SELECT agent_id, client_id, company_name, phone_number, transfer_phone
    # FROM client_agents WHERE active = true
    return []


def get_master_flow() -> dict:
    """Fetch master flow from Retell API"""
    # TODO: Implement Retell API call
    return {}


def generate_version_number() -> str:
    """Generate version number v20, v21, etc."""
    # TODO: Query Supabase for latest version and increment
    from datetime import datetime
    return f"v{datetime.now().strftime('%d%H')}"  # e.g., v3103 (31st day, 03:00)


def create_backup_in_supabase(agents: list, version: str, backup_id: str) -> dict:
    """Create backup in Supabase"""
    # TODO: INSERT into deployment_backups
    return {"backup_id": backup_id, "agents_backed_up": len(agents)}


def log_deployment_in_supabase(version: str, results: dict, backup_id: str):
    """Log deployment results in Supabase"""
    # TODO: INSERT into deployment_cycles and deployment_agents
    pass


def log_alert_in_supabase(event_type: str, severity: str, to_email: str, details: dict):
    """Log alert in Supabase"""
    # TODO: INSERT into alerts_sent
    pass


def log_cycle_in_supabase(cycle_data: dict):
    """Log cycle in Supabase"""
    # TODO: INSERT into deployment_cycles
    pass


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Syntharra Self-Healing Loop",
        "timestamp": datetime.now().isoformat()
    })


# ============================================================================
# COSTS
# ============================================================================
COST_PER_DIAGNOSIS = 0.00
COST_PER_FIX_VALIDATION = 0.15
COST_PER_DEPLOYMENT = 0.00
COST_PER_MONITORING = 0.00


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting n8n integration wrapper on {host}:{port}")
    app.run(host=host, port=port, debug=False)
