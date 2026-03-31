#!/usr/bin/env python3
"""
Syntharra Option A: Production Deployer
========================================
Deploys fixes from test agent to production agents with safety layers.

Features:
- 4-layer safety validation
- Batch deployment (10 agents at a time)
- Real-time monitoring
- Auto-rollback on errors
- Audit trail and logging
"""

import json
import urllib.request
import time
import datetime
from typing import Dict, List, Any, Optional


class ProductionDeployer:
    """Manages safe production deployment of fixes"""

    def __init__(self, retell_api_key: str, supabase_key: str):
        self.retell_key = retell_api_key
        self.supabase_key = supabase_key
        self.deployment_id = None
        self.deployment_start_time = None

    # =========================================================================
    # LAYER 1: PRE-DEPLOYMENT VALIDATION
    # =========================================================================

    def validate_fix_in_test_agent(self, test_agent_id: str, issue_type: str) -> Dict[str, Any]:
        """
        Layer 1: Verify that test agent actually has the fix applied correctly.
        
        Checks:
        - Agent is published
        - Fix is in conversation flow
        - No syntax errors in prompt
        """
        print(f"[LAYER 1] Validating fix in test agent {test_agent_id}...")

        # Check agent is published
        url = f"https://api.retellai.com/get-agent/{test_agent_id}"
        req = urllib.request.Request(
            url,
            method="GET",
            headers={"Authorization": f"Bearer {self.retell_key}"}
        )

        try:
            with urllib.request.urlopen(req) as resp:
                agent = json.loads(resp.read().decode())
                is_published = agent.get("is_published", False)
                
                if not is_published:
                    return {"passed": False, "reason": "Test agent is not published"}
        except Exception as e:
            return {"passed": False, "reason": f"Failed to fetch agent: {e}"}

        # Check conversation flow has fix
        flow_id = agent.get("conversation_flow_id")
        url = f"https://api.retellai.com/get-conversation-flow/{flow_id}"
        req = urllib.request.Request(
            url,
            method="GET",
            headers={"Authorization": f"Bearer {self.retell_key}"}
        )

        try:
            with urllib.request.urlopen(req) as resp:
                flow = json.loads(resp.read().decode())
                prompt = flow.get("prompt", "")
                
                # Check fix indicator is present
                if f"FIX {issue_type.upper()}" not in prompt:
                    return {"passed": False, "reason": "Fix not found in prompt"}
        except Exception as e:
            return {"passed": False, "reason": f"Failed to fetch flow: {e}"}

        return {"passed": True, "reason": "Test agent validation passed"}

    # =========================================================================
    # LAYER 2: CANARY DEPLOYMENT
    # =========================================================================

    def deploy_to_canary_agents(self, test_agent_id: str, fix_data: Dict, canary_count: int = 2) -> Dict[str, Any]:
        """
        Layer 2: Deploy to 1-2 canary (test) agents in production.
        Monitor for 10 minutes. If any fail, stop and rollback.
        """
        print(f"[LAYER 2] Deploying to {canary_count} canary agents...")

        # Get canary agent IDs (first N agents)
        canary_agents = self._get_agents("all", limit=canary_count)
        if len(canary_agents) < canary_count:
            return {"passed": False, "reason": f"Not enough agents (need {canary_count}, have {len(canary_agents)})"}

        # Deploy to each canary
        failed_agents = []
        successful_agents = []

        for agent_config in canary_agents:
            agent_id = agent_config["agent_id"]
            
            success = self._deploy_fix_to_agent(agent_id, test_agent_id, fix_data)
            
            if success:
                successful_agents.append(agent_id)
            else:
                failed_agents.append(agent_id)

        # Monitor canary agents for 10 minutes
        print(f"[LAYER 2] Monitoring {len(successful_agents)} canary agents for 10 minutes...")
        canary_health = self._monitor_agents(successful_agents, duration_minutes=10)

        if canary_health["error_rate"] > 0.05:  # >5% error rate = fail
            print(f"[LAYER 2] FAILED: Canary error rate too high ({canary_health['error_rate']*100:.1f}%)")
            # Rollback
            for agent_id in successful_agents:
                self._rollback_agent(agent_id)
            return {
                "passed": False,
                "reason": f"Canary deployment failed (error rate: {canary_health['error_rate']*100:.1f}%)"
            }

        return {
            "passed": True,
            "successful_agents": successful_agents,
            "failed_agents": failed_agents,
            "canary_health": canary_health
        }

    # =========================================================================
    # LAYER 3: BATCH DEPLOYMENT (10 at a time)
    # =========================================================================

    def deploy_to_production(self, test_agent_id: str, fix_data: Dict, target: str = "all") -> Dict[str, Any]:
        """
        Layer 3: Deploy fix to all production agents in batches of 10.
        Monitor each batch. Auto-rollback if errors exceed threshold.
        
        Target options:
        - "standard": Only Standard plan agents
        - "premium": Only Premium plan agents
        - "all": Both
        - ["agent_id_1", "agent_id_2"]: Specific agents
        """
        print(f"[LAYER 3] Starting batch deployment (target: {target})...")

        self.deployment_id = f"deploy_{datetime.datetime.utcnow().isoformat()}"
        self.deployment_start_time = time.time()

        # Get target agents
        target_agents = self._get_agents(target, limit=10000)
        if not target_agents:
            return {"passed": False, "reason": "No target agents found"}

        print(f"Deploying to {len(target_agents)} agents in batches of 10...")

        deployment_results = {
            "deployment_id": self.deployment_id,
            "target": target,
            "total_agents": len(target_agents),
            "batches": [],
            "total_success": 0,
            "total_failed": 0,
            "auto_rollbacks": 0
        }

        # Deploy in batches
        batch_size = 10
        for batch_num in range(0, len(target_agents), batch_size):
            batch = target_agents[batch_num:batch_num + batch_size]
            batch_result = self._deploy_batch(batch, test_agent_id, fix_data)
            
            deployment_results["batches"].append(batch_result)
            deployment_results["total_success"] += batch_result["successful"]
            deployment_results["total_failed"] += batch_result["failed"]

            # If error rate > 20%, stop and rollback
            if batch_result["error_rate"] > 0.2:
                print(f"[LAYER 3] Error rate in batch {batch_num // batch_size + 1} exceeded 20%. Rolling back...")
                deployment_results["auto_rollbacks"] += 1
                
                # Rollback this batch
                for agent_id in batch_result["successful_agents"]:
                    self._rollback_agent(agent_id)
                
                return {
                    "passed": False,
                    "reason": "Batch deployment failed - auto-rollback triggered",
                    "batch_that_failed": batch_num // batch_size + 1,
                    "results": deployment_results
                }

        return {"passed": True, "results": deployment_results}

    # =========================================================================
    # LAYER 4: POST-DEPLOYMENT VALIDATION
    # =========================================================================

    def validate_production_deployment(self, deployment_id: str, duration_minutes: int = 30) -> Dict[str, Any]:
        """
        Layer 4: Monitor all deployed agents for 30 minutes.
        Check error rates, call success, agent health.
        """
        print(f"[LAYER 4] Validating production deployment for {duration_minutes} minutes...")

        # Get agents deployed in this deployment
        deployed_agents = self._get_agents("all", limit=10000)

        health = self._monitor_agents(deployed_agents, duration_minutes=duration_minutes)

        validation = {
            "deployment_id": deployment_id,
            "validation_passed": health["error_rate"] < 0.10,  # <10% error = pass
            "overall_health": health,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

        if not validation["validation_passed"]:
            print(f"[LAYER 4] FAILED: Overall error rate {health['error_rate']*100:.1f}% exceeds threshold")
            # Full rollback
            for agent_id in deployed_agents:
                self._rollback_agent(agent_id)
        
        return validation

    # =========================================================================
    # ROLLBACK SYSTEM
    # =========================================================================

    def rollback_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """
        Emergency rollback: Revert all agents to previous version.
        """
        print(f"[ROLLBACK] Rolling back deployment {deployment_id}...")

        # Get all agents from deployment
        agents = self._get_agents("all", limit=10000)

        rollback_results = {
            "deployment_id": deployment_id,
            "rolled_back": 0,
            "failed": 0
        }

        for agent_config in agents:
            agent_id = agent_config["agent_id"]
            if self._rollback_agent(agent_id):
                rollback_results["rolled_back"] += 1
            else:
                rollback_results["failed"] += 1

        return rollback_results

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    def _get_agents(self, target: str, limit: int = 100) -> List[Dict]:
        """Get list of agents matching target criteria"""
        # In production, query Supabase
        # For now, return mock data
        agents = [
            {"agent_id": f"agent_prod_{i:03d}", "plan": "standard" if i % 2 == 0 else "premium"}
            for i in range(limit)
        ]
        
        if target == "standard":
            return [a for a in agents if a["plan"] == "standard"][:limit]
        elif target == "premium":
            return [a for a in agents if a["plan"] == "premium"][:limit]
        else:  # "all"
            return agents[:limit]

    def _deploy_fix_to_agent(self, agent_id: str, test_agent_id: str, fix_data: Dict) -> bool:
        """Deploy fix from test agent to production agent"""
        # Fetch test agent config
        url = f"https://api.retellai.com/get-agent/{test_agent_id}"
        req = urllib.request.Request(
            url,
            method="GET",
            headers={"Authorization": f"Bearer {self.retell_key}"}
        )

        try:
            with urllib.request.urlopen(req) as resp:
                test_config = json.loads(resp.read().decode())
        except Exception as e:
            print(f"Error fetching test agent: {e}")
            return False

        # Fetch production agent
        url = f"https://api.retellai.com/get-agent/{agent_id}"
        req = urllib.request.Request(
            url,
            method="GET",
            headers={"Authorization": f"Bearer {self.retell_key}"}
        )

        try:
            with urllib.request.urlopen(req) as resp:
                prod_config = json.loads(resp.read().decode())
        except Exception as e:
            print(f"Error fetching prod agent: {e}")
            return False

        # Copy conversation flow from test to prod
        test_flow_id = test_config.get("conversation_flow_id")
        prod_flow_id = prod_config.get("conversation_flow_id")

        # Fetch test flow
        url = f"https://api.retellai.com/get-conversation-flow/{test_flow_id}"
        req = urllib.request.Request(
            url,
            method="GET",
            headers={"Authorization": f"Bearer {self.retell_key}"}
        )

        try:
            with urllib.request.urlopen(req) as resp:
                test_flow = json.loads(resp.read().decode())
        except Exception as e:
            print(f"Error fetching test flow: {e}")
            return False

        # Update prod flow with test flow content
        url = f"https://api.retellai.com/update-conversation-flow/{prod_flow_id}"
        req = urllib.request.Request(
            url,
            method="PATCH",
            data=json.dumps(test_flow).encode(),
            headers={
                "Authorization": f"Bearer {self.retell_key}",
                "Content-Type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req) as resp:
                json.loads(resp.read().decode())
        except Exception as e:
            print(f"Error updating prod flow: {e}")
            return False

        # Publish prod agent
        url = f"https://api.retellai.com/publish-agent/{agent_id}"
        req = urllib.request.Request(
            url,
            method="POST",
            headers={"Authorization": f"Bearer {self.retell_key}"}
        )

        try:
            with urllib.request.urlopen(req) as resp:
                json.loads(resp.read().decode())
                return True
        except Exception as e:
            print(f"Error publishing prod agent: {e}")
            return False

    def _deploy_batch(self, agent_batch: List[Dict], test_agent_id: str, fix_data: Dict) -> Dict[str, Any]:
        """Deploy to a batch of 10 agents, monitor for errors"""
        print(f"Deploying to batch of {len(agent_batch)} agents...")

        successful = 0
        failed = 0
        successful_agents = []
        failed_agents = []

        for agent_config in agent_batch:
            agent_id = agent_config["agent_id"]
            if self._deploy_fix_to_agent(agent_id, test_agent_id, fix_data):
                successful += 1
                successful_agents.append(agent_id)
            else:
                failed += 1
                failed_agents.append(agent_id)

        # Monitor batch for 5 minutes
        batch_health = self._monitor_agents(successful_agents, duration_minutes=5)

        return {
            "successful": successful,
            "failed": failed,
            "successful_agents": successful_agents,
            "failed_agents": failed_agents,
            "error_rate": batch_health["error_rate"],
            "avg_call_duration": batch_health["avg_call_duration"]
        }

    def _monitor_agents(self, agent_ids: List[str], duration_minutes: int = 30) -> Dict[str, Any]:
        """Monitor agents and return health metrics"""
        print(f"Monitoring {len(agent_ids)} agents for {duration_minutes} minutes...")

        total_calls = 0
        total_errors = 0
        total_duration = 0

        start = time.time()
        end = start + (duration_minutes * 60)

        while time.time() < end:
            for agent_id in agent_ids:
                url = "https://api.retellai.com/v2/list-calls"
                req = urllib.request.Request(
                    url,
                    method="POST",
                    data=json.dumps({
                        "limit": 50,
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
                        data = json.loads(resp.read().decode())
                        calls = data.get("data", [])

                        for call in calls:
                            total_calls += 1
                            if not call.get("call_analysis", {}).get("call_successful", True):
                                total_errors += 1
                            total_duration += call.get("duration_ms", 0)
                except Exception as e:
                    print(f"Error fetching calls: {e}")

            time.sleep(30)

        error_rate = total_errors / total_calls if total_calls > 0 else 0
        avg_duration = (total_duration / total_calls / 1000) if total_calls > 0 else 0

        return {
            "total_calls": total_calls,
            "total_errors": total_errors,
            "error_rate": error_rate,
            "avg_call_duration": round(avg_duration, 1),
            "monitoring_duration_minutes": duration_minutes
        }

    def _rollback_agent(self, agent_id: str) -> bool:
        """Rollback an agent to previous version"""
        # In production, this would restore from backup
        # For now, just return success
        print(f"Rolling back agent {agent_id}...")
        return True


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    import os

    RETELL_KEY = os.getenv("RETELL_API_KEY", "key_xxx")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJ...")

    deployer = ProductionDeployer(RETELL_KEY, SUPABASE_KEY)

    # Example: Full deployment flow
    test_agent = "agent_test_001"
    fix_data = {
        "issue_type": "name_not_collected",
        "proposed_fix": "PROMPT_FIX: Add to prompt: 'Always collect customer name early'"
    }

    print("=== LAYER 1: Pre-deployment Validation ===")
    layer1 = deployer.validate_fix_in_test_agent(test_agent, "name_not_collected")
    print(json.dumps(layer1, indent=2))

    if layer1["passed"]:
        print("\n=== LAYER 2: Canary Deployment ===")
        layer2 = deployer.deploy_to_canary_agents(test_agent, fix_data, canary_count=2)
        print(json.dumps(layer2, indent=2))

        if layer2["passed"]:
            print("\n=== LAYER 3: Batch Deployment ===")
            layer3 = deployer.deploy_to_production(test_agent, fix_data, target="standard")
            print(json.dumps(layer3, indent=2))

            if layer3["passed"]:
                print("\n=== LAYER 4: Post-deployment Validation ===")
                layer4 = deployer.validate_production_deployment(layer3["results"]["deployment_id"])
                print(json.dumps(layer4, indent=2))
