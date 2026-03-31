#!/usr/bin/env python3
"""
Safety Checks Module

Pre-deployment safety validation:
- Variable injection checks
- Flow syntax validation
- Client config validation
- Emergency exit checks
"""

import re
import json
from typing import List, Dict, Tuple, Optional

# ============================================================================
# VARIABLE INJECTION VALIDATOR
# ============================================================================

class VariableInjectionValidator:
    """Validate that variables can be safely injected."""
    
    @staticmethod
    def validate_variables(
        client_variables: Dict,
        required_variables: List[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Check that all required variables are present and valid.
        """
        if required_variables is None:
            required_variables = [
                'company_name',
                'phone_number',
                'transfer_phone',
                'manager_name'
            ]
        
        # Check for missing variables
        missing = [v for v in required_variables if v not in client_variables]
        if missing:
            return False, f"Missing variables: {missing}"
        
        # Check for empty values
        empty = [k for k, v in client_variables.items() if not v or str(v).strip() == ""]
        if empty:
            return False, f"Empty variables: {empty}"
        
        # Check for obviously invalid values
        if not isinstance(client_variables.get('phone_number'), (str, int)):
            return False, "phone_number must be string or int"
        
        if not isinstance(client_variables.get('transfer_phone'), (str, int)):
            return False, "transfer_phone must be string or int"
        
        # Validate phone format (basic)
        for phone_key in ['phone_number', 'transfer_phone']:
            phone = str(client_variables.get(phone_key, ''))
            if not re.match(r'^\+?1?\d{10,}$', phone.replace('-', '').replace(' ', '')):
                return False, f"{phone_key} format invalid: {phone}"
        
        return True, None
    
    @staticmethod
    def test_substitution(
        template_text: str,
        variables: Dict
    ) -> Tuple[bool, str, List[str]]:
        """
        Test variable substitution on template text.
        
        Returns:
            (success, rendered_text, unsubstituted_vars)
        """
        rendered = template_text
        
        # Substitute each variable
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            rendered = rendered.replace(placeholder, str(value))
        
        # Find remaining unsubstituted variables
        unsubstituted = re.findall(r'\{\{[^}]+\}\}', rendered)
        
        if unsubstituted:
            return False, rendered, unsubstituted
        
        # Check for broken syntax
        if "{{" in rendered or "}}" in rendered:
            return False, rendered, ["Broken template syntax"]
        
        return True, rendered, []
    
    @staticmethod
    def validate_all_clients(
        all_clients: List[Dict]
    ) -> Tuple[bool, List[Dict]]:
        """
        Validate variables for all clients.
        
        Returns:
            (all_valid, list_of_errors)
        """
        errors = []
        
        for client in all_clients:
            client_id = client.get('id')
            variables = {
                'company_name': client.get('company_name'),
                'phone_number': client.get('phone_number'),
                'transfer_phone': client.get('transfer_phone'),
            }
            
            valid, error = VariableInjectionValidator.validate_variables(variables)
            
            if not valid:
                errors.append({
                    'client_id': client_id,
                    'error': error
                })
        
        all_valid = len(errors) == 0
        return all_valid, errors


# ============================================================================
# FLOW SYNTAX VALIDATOR
# ============================================================================

class FlowSyntaxValidator:
    """Validate flow JSON structure."""
    
    @staticmethod
    def validate_flow_structure(flow_json: Dict) -> Tuple[bool, Optional[str]]:
        """
        Check that flow JSON has required structure.
        """
        if not isinstance(flow_json, dict):
            return False, "Flow must be a dict"
        
        required_fields = ['id', 'nodes', 'edges']
        missing = [f for f in required_fields if f not in flow_json]
        
        if missing:
            return False, f"Missing required fields: {missing}"
        
        # Validate nodes
        nodes = flow_json.get('nodes', [])
        if not isinstance(nodes, list):
            return False, "Nodes must be a list"
        
        if len(nodes) == 0:
            return False, "Flow must have at least 1 node"
        
        node_ids = set()
        for node in nodes:
            if not isinstance(node, dict):
                return False, f"Node must be dict, got {type(node)}"
            
            if 'id' not in node:
                return False, "All nodes must have 'id' field"
            
            node_ids.add(node['id'])
        
        # Validate edges
        edges = flow_json.get('edges', [])
        if not isinstance(edges, list):
            return False, "Edges must be a list"
        
        for edge in edges:
            if not isinstance(edge, dict):
                return False, f"Edge must be dict, got {type(edge)}"
            
            for field in ['from_node_id', 'to_node_id']:
                if field not in edge:
                    return False, f"Edge missing required field: {field}"
                
                if edge[field] not in node_ids:
                    return False, f"Edge references non-existent node: {edge[field]}"
        
        return True, None
    
    @staticmethod
    def validate_no_say_prefix(flow_json: Dict) -> Tuple[bool, List[str]]:
        """
        Check that no node contains literal "Say:" prefix.
        """
        problems = []
        
        nodes = flow_json.get('nodes', [])
        for node in nodes:
            for field in ['instructions', 'prompt', 'message']:
                text = node.get(field, '')
                
                if isinstance(text, str) and text.startswith('Say:'):
                    problems.append(f"Node {node['id']}: {field} starts with 'Say:'")
                
                if isinstance(text, str) and ' Say:' in text:
                    problems.append(f"Node {node['id']}: {field} contains ' Say:' (should use 'Respond with:')")
        
        return len(problems) == 0, problems
    
    @staticmethod
    def validate_emergency_routing(flow_json: Dict) -> Tuple[bool, Optional[str]]:
        """
        Check that flow has emergency routing logic.
        """
        # Check for emergency-related node
        nodes = flow_json.get('nodes', [])
        
        emergency_keywords = ['emergency', 'urgent', 'critical']
        has_emergency_handling = any(
            any(kw in str(node).lower() for kw in emergency_keywords)
            for node in nodes
        )
        
        if not has_emergency_handling:
            return False, "Flow missing emergency routing logic"
        
        return True, None


# ============================================================================
# CONFIG VALIDATOR
# ============================================================================

class ConfigValidator:
    """Validate deployment configuration."""
    
    @staticmethod
    def validate_deployment_config(config: Dict) -> Tuple[bool, List[str]]:
        """
        Validate full deployment configuration.
        """
        errors = []
        
        # Check master agent
        if not config.get('master_agent_id'):
            errors.append("Missing master_agent_id")
        
        if not config.get('master_flow_id'):
            errors.append("Missing master_flow_id")
        
        # Check client agents
        clients = config.get('client_agents', [])
        if not clients:
            errors.append("No client agents provided")
        
        if len(clients) > 1000:
            errors.append(f"Too many clients ({len(clients)}) - max 1000")
        
        # Check each client
        for i, client in enumerate(clients):
            if not client.get('id'):
                errors.append(f"Client {i} missing 'id'")
            
            if not client.get('agent_id'):
                errors.append(f"Client {i} missing 'agent_id'")
        
        # Check version
        version = config.get('version')
        if not version or not re.match(r'^v\d+$', version):
            errors.append(f"Invalid version format: {version} (use v1, v2, etc.)")
        
        # Check safety parameters
        failure_threshold = config.get('failure_threshold', 0.20)
        if failure_threshold < 0 or failure_threshold > 1:
            errors.append(f"failure_threshold must be 0-1, got {failure_threshold}")
        
        return len(errors) == 0, errors


# ============================================================================
# EMERGENCY EXIT
# ============================================================================

class EmergencyExit:
    """Emergency stop mechanisms."""
    
    @staticmethod
    def validate_emergency_stop_capable(
        deployment_ids: List[str],
        backup: Dict
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify that we can quickly rollback if needed.
        """
        # Check that all agents have backups
        backed_up = set(backup.get("agents", {}).keys())
        deploying = set(deployment_ids)
        
        not_backed_up = deploying - backed_up
        if not_backed_up:
            return False, f"Not all agents backed up: {not_backed_up}"
        
        return True, None
    
    @staticmethod
    def create_emergency_stop_trigger(
        trigger_conditions: Dict
    ) -> Dict:
        """
        Create emergency stop trigger configuration.
        """
        return {
            "enabled": True,
            "conditions": {
                "failure_rate_threshold": trigger_conditions.get('failure_rate_threshold', 0.30),
                "error_spike_threshold": trigger_conditions.get('error_spike_threshold', 5),
                "consecutive_failures": trigger_conditions.get('consecutive_failures', 3),
                "timeout_mins": trigger_conditions.get('timeout_mins', 60)
            },
            "action": "auto_rollback_all",
            "notify": "admin@syntharra.com"
        }


# ============================================================================
# PRE-DEPLOYMENT CHECKLIST
# ============================================================================

class PreDeploymentChecklist:
    """Complete pre-deployment validation."""
    
    @staticmethod
    def run_full_validation(
        deployment_config: Dict,
        master_flow: Dict,
        all_clients: List[Dict]
    ) -> Tuple[bool, Dict]:
        """
        Run complete pre-deployment validation.
        
        Returns:
            (all_passed, results_dict)
        """
        results = {
            "timestamp": str(__import__('datetime').datetime.now()),
            "checks": {},
            "passed": True
        }
        
        # Check 1: Config validation
        config_valid, config_errors = ConfigValidator.validate_deployment_config(deployment_config)
        results["checks"]["config"] = {
            "passed": config_valid,
            "errors": config_errors
        }
        if not config_valid:
            results["passed"] = False
        
        # Check 2: Flow structure validation
        flow_valid, flow_error = FlowSyntaxValidator.validate_flow_structure(master_flow)
        results["checks"]["flow_structure"] = {
            "passed": flow_valid,
            "error": flow_error
        }
        if not flow_valid:
            results["passed"] = False
        
        # Check 3: Say prefix check
        no_say, say_problems = FlowSyntaxValidator.validate_no_say_prefix(master_flow)
        results["checks"]["no_say_prefix"] = {
            "passed": no_say,
            "problems": say_problems
        }
        if not no_say:
            results["passed"] = False
        
        # Check 4: Emergency routing
        has_emergency, emergency_error = FlowSyntaxValidator.validate_emergency_routing(master_flow)
        results["checks"]["emergency_routing"] = {
            "passed": has_emergency,
            "error": emergency_error
        }
        # Note: Don't fail on this, just warn
        
        # Check 5: Client variable validation
        all_valid, var_errors = VariableInjectionValidator.validate_all_clients(all_clients)
        results["checks"]["client_variables"] = {
            "passed": all_valid,
            "errors": var_errors[:10]  # First 10 errors
        }
        if not all_valid:
            results["passed"] = False
        
        # Check 6: Emergency stop capability
        backup = deployment_config.get('backup', {})
        stop_capable, stop_error = EmergencyExit.validate_emergency_stop_capable(
            [c['agent_id'] for c in all_clients],
            backup
        )
        results["checks"]["emergency_stop"] = {
            "passed": stop_capable,
            "error": stop_error
        }
        if not stop_capable:
            results["passed"] = False
        
        return results["passed"], results


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Example usage
    test_config = {
        "master_agent_id": "agent_xxx",
        "master_flow_id": "flow_xxx",
        "client_agents": [
            {"id": "client_1", "agent_id": "agent_1"}
        ],
        "version": "v20"
    }
    
    test_flow = {
        "id": "flow_xxx",
        "nodes": [{"id": "node_1"}],
        "edges": []
    }
    
    test_clients = [
        {
            "id": "client_1",
            "company_name": "Test Co",
            "phone_number": "5551234567",
            "transfer_phone": "5551234568"
        }
    ]
    
    passed, results = PreDeploymentChecklist.run_full_validation(
        test_config,
        test_flow,
        test_clients
    )
    
    print(json.dumps(results, indent=2))
    print(f"\nAll checks passed: {passed}")
