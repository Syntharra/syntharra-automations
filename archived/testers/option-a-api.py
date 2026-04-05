#!/usr/bin/env python3
"""
Syntharra Option A: API Routes
===============================
Flask endpoints that tie the system together.

Endpoints:
- POST /api/diagnose — Run diagnosis on agent
- POST /api/test-fix — Test fix on test agent
- POST /api/deploy-fix — Deploy to production
- POST /api/rollback — Rollback deployment
- GET /api/status — Get system status
"""

from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

from issue_diagnosis_engine import IssueDetector, DiagnosisDashboard
from test_agent_controller import TestAgentController
from production_deployer import ProductionDeployer

# ============================================================================
# SETUP
# ============================================================================

app = Flask(__name__)

RETELL_KEY = os.getenv("RETELL_API_KEY", "key_xxx")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJ...")
CLAUDE_KEY = os.getenv("CLAUDE_API_KEY", "sk_xxx")

detector = IssueDetector(RETELL_KEY, SUPABASE_KEY)
dashboard = DiagnosisDashboard(detector)
test_controller = TestAgentController(RETELL_KEY, CLAUDE_KEY)
deployer = ProductionDeployer(RETELL_KEY, SUPABASE_KEY)

# ============================================================================
# API ROUTES
# ============================================================================

@app.route("/api/agents", methods=["GET"])
def get_agents():
    """
    Get list of available agents
    
    Returns:
    {
      "agents": [
        { "agent_id": "...", "name": "...", "plan": "standard" or "premium" }
      ]
    }
    """
    # In production, query Supabase
    agents = [
        {"agent_id": "agent_4afbfdb3fcb1ba9569353af28d", "name": "Arctic Breeze HVAC", "plan": "standard"}
    ]
    return jsonify({"agents": agents})


@app.route("/api/diagnose", methods=["POST"])
def diagnose():
    """
    Run diagnosis on an agent (scan recent calls for issues)
    
    Request:
    {
      "agent_id": "agent_xxx",
      "days": 30  # Optional, default 30
    }
    
    Response:
    {
      "agent_id": "...",
      "scan_timestamp": "...",
      "total_issues_found": N,
      "critical_count": N,
      "high_count": N,
      "medium_count": N,
      "low_count": N,
      "issues": [
        {
          "issue_type": "emergency_routing_failure",
          "severity": "CRITICAL",
          "frequency": 3,
          "affected_agents": ["agent_xxx"],
          "description": "...",
          "proposed_fix": "...",
          "sample_call_id": "...",
          "actions": ["Fix It", "Skip", "Investigate"]
        }
      ]
    }
    """
    data = request.get_json()
    agent_id = data.get("agent_id")
    days = data.get("days", 30)

    if not agent_id:
        return jsonify({"error": "agent_id required"}), 400

    try:
        result = dashboard.get_dashboard_data(agent_id)
        
        # Log diagnosis to Supabase
        # TODO: log_to_supabase(...)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/test-fix", methods=["POST"])
def test_fix():
    """
    Test a fix on test agent (with optional auto test calls)
    
    Request:
    {
      "agent_id": "agent_xxx",
      "issue_type": "emergency_routing_failure",
      "issue_id": "emergency_routing_failure_0",
      "test_mode": "auto" or "manual"  # Default "auto"
    }
    
    Response:
    {
      "test_passed": bool,
      "test_agent_id": "...",
      "duration_minutes": N,
      "pass_count": N,
      "fail_count": N,
      "test_result_details": {},
      "message": "..."
    }
    """
    data = request.get_json()
    agent_id = data.get("agent_id")
    issue_type = data.get("issue_type")
    issue_id = data.get("issue_id")
    test_mode = data.get("test_mode", "auto")

    if not agent_id or not issue_type:
        return jsonify({"error": "agent_id and issue_type required"}), 400

    try:
        # Step 1: Get proposed fix
        detector_instance = IssueDetector(RETELL_KEY, SUPABASE_KEY)
        calls = detector_instance.get_recent_calls(agent_id, limit=50)
        sample_call = next((c for c in calls if c.get("call_id") == ""), None)
        proposed_fix = detector_instance.generate_fix_proposal(issue_type, "")

        # Step 2: Create test agent
        test_agent_id = test_controller.clone_agent_for_testing(agent_id)

        # Step 3: Apply fix to test agent
        success = test_controller.apply_fix_to_agent(test_agent_id, issue_type, proposed_fix)
        if not success:
            return jsonify({"error": "Failed to apply fix to test agent"}), 500

        # Step 4: Run tests
        if test_mode == "auto":
            test_result = test_controller.run_auto_test_calls(test_agent_id, issue_type, scenario_count=3)
        else:
            test_result = test_controller.wait_for_manual_test(test_agent_id)

        # Step 5: Monitor test agent
        monitor_result = test_controller.monitor_test_agent(test_agent_id, duration_minutes=10)

        # Step 6: Cleanup test agent
        test_controller.cleanup_test_agent(test_agent_id)

        # Log to Supabase
        # TODO: log_test_result_to_supabase(...)

        return jsonify({
            "test_passed": test_result.get("test_passed", False),
            "test_agent_id": test_agent_id,
            "test_mode": test_mode,
            "test_result": test_result,
            "monitor_result": monitor_result,
            "message": test_result.get("message", "")
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/deploy-fix", methods=["POST"])
def deploy_fix():
    """
    Deploy fix from test agent to production
    (only enabled if test passed)
    
    Request:
    {
      "issue_id": "issue_xxx",
      "test_agent_id": "agent_test_xxx",
      "target": "standard" or "premium" or "all" or ["agent_id_1", "agent_id_2"]
    }
    
    Response:
    {
      "success": bool,
      "deployment_id": "deploy_2026-03-31T...",
      "status": "pending" | "in_progress" | "completed" | "failed",
      "total_agents": N,
      "agents_succeeded": N,
      "agents_failed": N,
      "layer_results": {
        "layer1": { "passed": bool, "message": "..." },
        "layer2": { "passed": bool, "message": "..." },
        "layer3": { "passed": bool, "message": "..." },
        "layer4": { "passed": bool, "message": "..." }
      },
      "message": "..."
    }
    """
    data = request.get_json()
    issue_id = data.get("issue_id")
    test_agent_id = data.get("test_agent_id")
    target = data.get("target", "standard")

    if not issue_id or not test_agent_id:
        return jsonify({"error": "issue_id and test_agent_id required"}), 400

    try:
        fix_data = {
            "issue_type": "emergency_routing_failure",  # Would fetch from DB
            "proposed_fix": "PROMPT_FIX: ..."  # Would fetch from DB
        }

        # Layer 1: Pre-deployment validation
        layer1 = deployer.validate_fix_in_test_agent(test_agent_id, "emergency_routing_failure")

        if not layer1["passed"]:
            return jsonify({
                "success": False,
                "layer_results": {"layer1": layer1},
                "message": layer1["reason"]
            }), 400

        # Layer 2: Canary deployment
        layer2 = deployer.deploy_to_canary_agents(test_agent_id, fix_data, canary_count=2)

        if not layer2["passed"]:
            return jsonify({
                "success": False,
                "layer_results": {"layer1": layer1, "layer2": layer2},
                "message": layer2["reason"]
            }), 400

        # Layer 3: Batch deployment
        layer3 = deployer.deploy_to_production(test_agent_id, fix_data, target=target)

        if not layer3["passed"]:
            return jsonify({
                "success": False,
                "deployment_id": layer3["results"]["deployment_id"],
                "layer_results": {"layer1": layer1, "layer2": layer2, "layer3": layer3},
                "message": layer3["reason"]
            }), 400

        # Layer 4: Post-deployment validation
        layer4 = deployer.validate_production_deployment(
            layer3["results"]["deployment_id"],
            duration_minutes=30
        )

        # Log deployment to Supabase
        # TODO: log_deployment_to_supabase(...)

        return jsonify({
            "success": layer4["validation_passed"],
            "deployment_id": layer4["deployment_id"],
            "layer_results": {
                "layer1": {"passed": layer1["passed"]},
                "layer2": {"passed": layer2["passed"]},
                "layer3": {"passed": layer3["passed"]},
                "layer4": {"passed": layer4["validation_passed"]}
            },
            "deployment_results": layer3["results"],
            "validation_results": layer4,
            "message": "Deployment completed successfully" if layer4["validation_passed"] else "Deployment validation failed"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/rollback", methods=["POST"])
def rollback():
    """
    Manually rollback a deployment
    
    Request:
    {
      "deployment_id": "deploy_xxx"
    }
    
    Response:
    {
      "success": bool,
      "deployment_id": "...",
      "rolled_back": N,
      "failed": N,
      "message": "..."
    }
    """
    data = request.get_json()
    deployment_id = data.get("deployment_id")

    if not deployment_id:
        return jsonify({"error": "deployment_id required"}), 400

    try:
        result = deployer.rollback_deployment(deployment_id)
        
        # Log rollback to Supabase
        # TODO: log_rollback_to_supabase(...)

        return jsonify({
            "success": True,
            "deployment_id": deployment_id,
            "rolled_back": result["rolled_back"],
            "failed": result["failed"],
            "message": f"Rolled back {result['rolled_back']} agents"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/test-result", methods=["POST"])
def submit_test_result():
    """
    Submit manual test result (for manual test mode)
    
    Request:
    {
      "test_agent_id": "agent_test_xxx",
      "passed": bool,
      "notes": "..."
    }
    
    Response:
    {
      "success": bool,
      "message": "..."
    }
    """
    data = request.get_json()
    test_agent_id = data.get("test_agent_id")
    passed = data.get("passed", False)
    notes = data.get("notes", "")

    if not test_agent_id:
        return jsonify({"error": "test_agent_id required"}), 400

    try:
        # Log to Supabase that manual test was completed
        # TODO: update_test_result_in_supabase(...)

        return jsonify({
            "success": True,
            "message": f"Test result recorded: {'PASSED' if passed else 'FAILED'}"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/status", methods=["GET"])
def status():
    """
    Get system health status
    
    Returns:
    {
      "status": "healthy" | "degraded" | "error",
      "retell_api": "ok" | "error",
      "supabase": "ok" | "error",
      "claude_api": "ok" | "error",
      "timestamp": "2026-03-31T..."
    }
    """
    # Check all APIs
    retell_ok = True
    supabase_ok = True
    claude_ok = True

    try:
        # Quick Retell check
        import urllib.request
        req = urllib.request.Request(
            "https://api.retellai.com/list-agents",
            method="GET",
            headers={"Authorization": f"Bearer {RETELL_KEY}"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            pass
    except:
        retell_ok = False

    # Determine overall status
    if retell_ok and supabase_ok and claude_ok:
        overall = "healthy"
    elif not retell_ok or not supabase_ok:
        overall = "error"
    else:
        overall = "degraded"

    return jsonify({
        "status": overall,
        "retell_api": "ok" if retell_ok else "error",
        "supabase": "ok" if supabase_ok else "error",
        "claude_api": "ok" if claude_ok else "error",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """Simple health check"""
    return jsonify({"status": "ok"}), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request"}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
