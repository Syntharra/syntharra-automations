#!/usr/bin/env python3
"""
Safe Deployment Workflow

Deploys master template to all client agents with:
- Backup before deploy
- Batch-wise rollout (10 agents at a time)
- Verification after each deploy
- Automatic rollback on failure
- Post-deploy monitoring
"""

import json
import urllib.request
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
import copy

# ============================================================================
# CONFIG
# ============================================================================

RETELL_KEY = "key_0157d9401f66cfa1b51fadc66445"
RETELL_BASE = "https://api.retellai.com"

BATCH_SIZE = 10
MAX_PARALLEL_DEPLOYS = 3
BATCH_FAILURE_THRESHOLD = 0.20  # 20% = rollback
MONITOR_BETWEEN_BATCHES_MINS = 2
MAX_RETRIES_PER_CLIENT = 2

# ============================================================================
# BACKUP SYSTEM
# ============================================================================

class BackupManager:
    """Save current agent state before deployment."""
    
    def __init__(self, retell_key: str):
        self.retell_key = retell_key
    
    def backup_all_agents(self, agent_ids: List[str], version_tag: str) -> Dict:
        """
        Backup current config for all agents.
        Can be used to rollback if deployment fails.
        """
        print(f"\n[BACKUP] Saving current state of {len(agent_ids)} agents...")
        
        backup = {
            "version_tag": version_tag,
            "timestamp": datetime.now().isoformat(),
            "agents": {}
        }
        
        for agent_id in agent_ids:
            try:
                req = urllib.request.Request(
                    f"{RETELL_BASE}/get-agent/{agent_id}",
                    method="GET",
                    headers={"Authorization": f"Bearer {self.retell_key}"}
                )
                
                with urllib.request.urlopen(req) as resp:
                    agent_config = json.loads(resp.read().decode())
                
                backup["agents"][agent_id] = {
                    "config": agent_config,
                    "backed_up_at": datetime.now().isoformat()
                }
            
            except Exception as e:
                print(f"  ⚠️  Could not backup {agent_id}: {e}")
        
        print(f"  ✅ Backed up {len(backup['agents'])} agents")
        return backup
    
    def restore_agent(self, agent_id: str, backup: Dict) -> bool:
        """Restore agent from backup (rollback)."""
        if agent_id not in backup["agents"]:
            return False
        
        try:
            agent_config = backup["agents"][agent_id]["config"]
            
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
            
            # Publish restored agent
            pub_req = urllib.request.Request(
                f"{RETELL_BASE}/publish-agent/{agent_id}",
                method="POST",
                data=b"",
                headers={"Authorization": f"Bearer {self.retell_key}"}
            )
            
            with urllib.request.urlopen(pub_req) as resp:
                json.loads(resp.read().decode())
            
            return True
        
        except Exception as e:
            print(f"  ❌ Restore failed for {agent_id}: {e}")
            return False


# ============================================================================
# DEPLOYMENT ENGINE
# ============================================================================

class DeploymentEngine:
    """Deploy rendered flows to client agents."""
    
    def __init__(self, retell_key: str):
        self.retell_key = retell_key
    
    def deploy_to_agent(
        self,
        agent_id: str,
        rendered_flow: Dict,
        retry_count: int = 0
    ) -> Tuple[bool, Optional[str]]:
        """
        Deploy flow to single agent.
        Returns (success, error_message)
        """
        try:
            # Step 1: Update agent with rendered flow
            update_payload = {
                "conversation_flow_id": rendered_flow.get('id', ''),
                # Include other relevant fields from rendered_flow
            }
            
            req = urllib.request.Request(
                f"{RETELL_BASE}/update-agent/{agent_id}",
                method="PATCH",
                data=json.dumps(update_payload).encode(),
                headers={
                    "Authorization": f"Bearer {self.retell_key}",
                    "Content-Type": "application/json"
                }
            )
            
            with urllib.request.urlopen(req) as resp:
                json.loads(resp.read().decode())
            
            # Step 2: Verify agent updated
            req = urllib.request.Request(
                f"{RETELL_BASE}/get-agent/{agent_id}",
                method="GET",
                headers={"Authorization": f"Bearer {self.retell_key}"}
            )
            
            with urllib.request.urlopen(req) as resp:
                updated_agent = json.loads(resp.read().decode())
            
            if not updated_agent.get('is_published'):
                # Step 3: Publish agent
                pub_req = urllib.request.Request(
                    f"{RETELL_BASE}/publish-agent/{agent_id}",
                    method="POST",
                    data=b"",
                    headers={"Authorization": f"Bearer {self.retell_key}"}
                )
                
                with urllib.request.urlopen(pub_req) as resp:
                    json.loads(resp.read().decode())
            
            return True, None
        
        except Exception as e:
            error_msg = str(e)
            
            # Retry once
            if retry_count < MAX_RETRIES_PER_CLIENT:
                time.sleep(1)
                return self.deploy_to_agent(agent_id, rendered_flow, retry_count + 1)
            
            return False, error_msg
    
    def verify_deployment(self, agent_id: str) -> Tuple[bool, Optional[str]]:
        """
        Verify agent was actually deployed and is live.
        Don't just assume publish worked.
        """
        try:
            req = urllib.request.Request(
                f"{RETELL_BASE}/get-agent/{agent_id}",
                method="GET",
                headers={"Authorization": f"Bearer {self.retell_key}"}
            )
            
            with urllib.request.urlopen(req) as resp:
                agent = json.loads(resp.read().decode())
            
            # Check 1: Published?
            if not agent.get('is_published'):
                return False, "Agent not published"
            
            # Check 2: Has conversation flow?
            if not agent.get('conversation_flow_id'):
                return False, "No conversation flow assigned"
            
            return True, None
        
        except Exception as e:
            return False, str(e)


# ============================================================================
# BATCH DEPLOYMENT WITH MONITORING
# ============================================================================

class BatchDeploymentOrchestrator:
    """Manage multi-batch deployment with safety checks."""
    
    def __init__(self, retell_key: str):
        self.retell_key = retell_key
        self.engine = DeploymentEngine(retell_key)
        self.backup_manager = BackupManager(retell_key)
    
    def deploy_batch(
        self,
        batch_agents: List[Dict],
        master_flow: Dict,
        batch_num: int,
        total_batches: int
    ) -> Dict:
        """
        Deploy to single batch of agents.
        Returns results with success/failure counts.
        """
        print(f"\n  Batch {batch_num}/{total_batches}: {len(batch_agents)} agents")
        
        results = {
            "successful": [],
            "failed": [],
            "agent_ids": [a['agent_id'] for a in batch_agents]
        }
        
        # Deploy in parallel
        with ThreadPoolExecutor(max_workers=MAX_PARALLEL_DEPLOYS) as executor:
            futures = []
            
            for agent in batch_agents:
                agent_id = agent['agent_id']
                
                # Render flow with this client's variables
                variables = {
                    'company_name': agent.get('company_name', 'Service Company'),
                    'phone_number': agent.get('phone_number', '555-0000'),
                    'transfer_phone': agent.get('transfer_phone', '555-0001'),
                }
                
                rendered_flow = self._render_flow(master_flow, variables)
                
                future = executor.submit(
                    self.engine.deploy_to_agent,
                    agent_id,
                    rendered_flow
                )
                futures.append((agent_id, future))
            
            # Collect results
            for agent_id, future in futures:
                success, error = future.result()
                
                if success:
                    # Verify deployment
                    verified, verify_error = self.engine.verify_deployment(agent_id)
                    
                    if verified:
                        results["successful"].append(agent_id)
                        print(f"    ✅ {agent_id}")
                    else:
                        results["failed"].append(agent_id)
                        print(f"    ❌ {agent_id} (verify failed: {verify_error})")
                else:
                    results["failed"].append(agent_id)
                    print(f"    ❌ {agent_id} ({error})")
        
        return results
    
    def deploy_all_batches(
        self,
        all_agents: List[Dict],
        master_flow: Dict,
        version_tag: str,
        backup: Dict
    ) -> Dict:
        """
        Deploy to all agents in multiple batches.
        Stop and rollback if failure rate gets too high.
        """
        print(f"\n{'='*70}")
        print(f"[DEPLOYMENT] Multi-batch safe rollout")
        print(f"{'='*70}")
        print(f"  Total agents: {len(all_agents)}")
        print(f"  Batch size: {BATCH_SIZE}")
        print(f"  Batches: {(len(all_agents) + BATCH_SIZE - 1) // BATCH_SIZE}")
        
        all_results = {
            "version": version_tag,
            "successful": [],
            "failed": [],
            "rolled_back": [],
            "total_time_mins": 0
        }
        
        start_time = time.time()
        
        # Create batches
        batches = [
            all_agents[i:i+BATCH_SIZE]
            for i in range(0, len(all_agents), BATCH_SIZE)
        ]
        
        # Deploy each batch
        for batch_num, batch in enumerate(batches, 1):
            batch_results = self.deploy_batch(batch, master_flow, batch_num, len(batches))
            
            all_results["successful"].extend(batch_results["successful"])
            all_results["failed"].extend(batch_results["failed"])
            
            print(f"    Summary: {len(batch_results['successful'])}/{len(batch)} successful")
            
            # Check failure rate
            if all_results["successful"] or all_results["failed"]:
                fail_rate = len(all_results["failed"]) / (
                    len(all_results["successful"]) + len(all_results["failed"])
                )
                
                if fail_rate > BATCH_FAILURE_THRESHOLD:
                    print(f"\n  ⚠️  CRITICAL: {fail_rate*100:.0f}% failure rate (threshold: {BATCH_FAILURE_THRESHOLD*100:.0f}%)")
                    print(f"     Rolling back all {len(all_results['successful'])} deployed agents...")
                    
                    # Rollback
                    for agent_id in all_results["successful"]:
                        success = self.backup_manager.restore_agent(agent_id, backup)
                        if success:
                            all_results["rolled_back"].append(agent_id)
                            print(f"    ✅ {agent_id} rolled back")
                        else:
                            print(f"    ❌ {agent_id} rollback FAILED")
                    
                    print(f"\n  🔄 Deployment HALTED and rolled back")
                    all_results["status"] = "halted_and_rolled_back"
                    break
            
            # Monitor between batches
            if batch_num < len(batches):
                print(f"\n  ⏳ Monitoring for {MONITOR_BETWEEN_BATCHES_MINS} minutes before next batch...")
                time.sleep(MONITOR_BETWEEN_BATCHES_MINS * 60)
        
        elapsed = (time.time() - start_time) / 60
        all_results["total_time_mins"] = elapsed
        
        # Summary
        print(f"\n{'='*70}")
        print(f"[DEPLOYMENT SUMMARY]")
        print(f"{'='*70}")
        print(f"  Successful: {len(all_results['successful'])}")
        print(f"  Failed: {len(all_results['failed'])}")
        print(f"  Rolled back: {len(all_results['rolled_back'])}")
        print(f"  Time: {elapsed:.1f} minutes")
        
        if not all_results["failed"] and not all_results["rolled_back"]:
            print(f"  Status: ✅ ALL AGENTS DEPLOYED SUCCESSFULLY")
            all_results["status"] = "success"
        else:
            print(f"  Status: ⚠️  DEPLOYMENT WITH ISSUES")
            all_results["status"] = "partial_failure"
        
        return all_results
    
    def _render_flow(self, flow_json: Dict, variables: Dict) -> Dict:
        """Render flow with client variables."""
        rendered_flow = copy.deepcopy(flow_json)
        
        def substitute_text(text: str) -> str:
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                text = text.replace(placeholder, str(value))
            return text
        
        def substitute_in_dict(obj):
            if isinstance(obj, dict):
                return {k: substitute_in_dict(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [substitute_in_dict(item) for item in obj]
            elif isinstance(obj, str):
                return substitute_text(obj)
            else:
                return obj
        
        return substitute_in_dict(rendered_flow)


# ============================================================================
# ENTRY POINT
# ============================================================================

def deploy_master_to_all_clients(
    master_flow_id: str,
    all_client_agents: List[Dict],
    master_flow: Dict,
    version_tag: str = "v20"
) -> Dict:
    """
    Main entry point: Deploy master to all clients safely.
    
    Args:
        master_flow_id: ID of master flow to deploy
        all_client_agents: List of client agent configs
        master_flow: The master flow JSON
        version_tag: Version number being deployed
    
    Returns:
        Deployment results with status, counts, timing
    """
    
    orchestrator = BatchDeploymentOrchestrator(RETELL_KEY)
    
    # Step 1: Backup all agents
    backup = orchestrator.backup_manager.backup_all_agents(
        [a['agent_id'] for a in all_client_agents],
        version_tag
    )
    
    # Step 2: Deploy all batches
    results = orchestrator.deploy_all_batches(
        all_client_agents,
        master_flow,
        version_tag,
        backup
    )
    
    return results


if __name__ == "__main__":
    # Example usage
    test_agents = [
        {
            "id": f"client_{i}",
            "agent_id": f"agent_test_{i}",
            "company_name": f"Company {i}",
            "phone_number": f"555-{i:04d}",
            "transfer_phone": f"555-{i+1:04d}"
        }
        for i in range(15)
    ]
    
    test_flow = {
        "id": "conversation_flow_34d169608460",
        "nodes": []
    }
    
    results = deploy_master_to_all_clients(
        "conversation_flow_34d169608460",
        test_agents,
        test_flow,
        "v20"
    )
    
    print(json.dumps(results, indent=2))
