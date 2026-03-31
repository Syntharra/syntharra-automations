# Self-Healing Loop v2 — Master Template Architecture

## The Correct Model

### What You Have (Currently)
```
Client A: agent_xxx1 (Standard template)
Client B: agent_xxx2 (Standard template copy)
Client C: agent_xxx3 (Standard template copy)
...
Client Z: agent_xxxZ (Standard template copy)
↓
All 50 agents have IDENTICAL prompts/nodes/config
```

### The Problem (What I Built Wrong)
```
❌ Self-healing loop running 50 times in parallel
❌ Each checking calls for the same agent template
❌ Each generating the same fix
❌ Each validating the same fix
❌ 50x the cost, 0x the benefit
```

### The Solution (What We Actually Need)
```
✅ ONE master Standard agent (template source of truth)
✅ Aggregate call logs from ALL 50 client agents
✅ Detect issues (using combined data)
✅ Fix ONLY the master agent
✅ Auto-deploy to all 50 agents simultaneously
✅ Cost: Same as 1 agent ($1/month), benefits all 50
```

---

## Architecture v2: Master + Clients

### Layer 1: AGGREGATE & DIAGNOSE
```
Pull calls from all 50 client agents:
  agent_client_1 → calls
  agent_client_2 → calls
  agent_client_3 → calls
  ...
  agent_client_50 → calls
        ↓
  Merge into single dataset (2,500 calls)
        ↓
  Scan for patterns (12 detections)
        ↓
  Rank by severity + frequency
        ↓
  Output: Issues detected from REAL AGGREGATE DATA
  
Cost: FREE (just log reading)
Benefit: Issues surfaced from 2,500 calls, not 50
```

### Layer 2: FIX MASTER TEMPLATE
```
Issue detected: "Emergency keywords not triggering transfer"
        ↓
  Claude generates fix
        ↓
  Apply to MASTER agent: agent_standard_hvac_master
        ↓
  Publish master agent
        ↓
  Store fix in Supabase with version number
        ↓
  Trigger auto-deployment
  
Cost: $0.02
Affected: 1 agent
But fixes: 50 clients simultaneously
```

### Layer 3: VALIDATE + DEPLOY
```
Run 1-scenario test on master:
  Does fix work? YES → Proceed
  Does fix work? NO  → Rollback, try again next cycle
        ↓
  If PASS:
    1. Commit fix to Supabase (version: v19 → v20)
    2. Tag all 50 client agents with new master version
    3. Trigger n8n deployment workflow
         ├─ For each client agent:
         │  ├─ Fetch master flow (v20)
         │  ├─ Inject client-specific variables
         │  │  (company_name, phone, transfer_number, etc.)
         │  ├─ Publish to client agent
         │  └─ Log deployment
         └─ Email clients: "Your agent improved! New version deployed"
  
Cost: $0.15 (1 validation)
Deploys to: All 50 agents automatically
Time: 5 minutes

Result: All 50 agents instantly running the improved version
```

---

## Real Example: 3 Months In, Issue on 25 Agents

### Scenario
```
You've got 50 HVAC Standard clients.
3 months in, you notice:
  - 25 agents have a call tag: "Customer said 'gas smell' but agent asked for AC type first"
  - Issue: Emergency routing not triggered on gas smell
  - Root cause: Missing "gas" in emergency_condition_edge
```

### Old Way (Manual)
```
1. You manually identify the issue (hours of review)
2. You hand-write a fix
3. You test on one agent (30 mins)
4. You deploy to 50 agents... manually? Copy-paste? Script?
5. You hope it works for everyone

Time: 3-4 hours
Risk: Human error, missed agents, inconsistent deployment
Cost: Your time
```

### New Way (Automated)
```
Day 1, 2 AM UTC:
  1. Loop aggregates calls from all 50 agents
  2. Detects: "gas" keyword in 25 calls, no emergency routing triggered
  3. Severity: CRITICAL, Frequency: 25/2500 (1%)
  4. Claude generates fix:
     "Add 'gas, gas smell, gas leak' to emergency_condition_edge"
  5. Apply to master agent
  6. Publish master
  
Day 1, 2:15 AM:
  1. Run 1-scenario test: "Caller: I smell gas in my house"
  2. Agent routes to emergency? YES → PASS ✅
  
Day 1, 2:20 AM:
  1. Tag all 50 client agents with new master version
  2. n8n deployment workflow triggers:
     FOR agent in [client_1, client_2, ... client_50]:
       - Fetch master flow (v20 with gas fix)
       - Inject client variables (name, phone, etc.)
       - Publish to client agent
       - Log: "client_1: Deployed v20 ✅"
       - Email: "Your HVAC agent improved! Gas smell detection added."
  3. Done in 3 minutes (parallel execution)

Day 1, 2:30 AM:
  All 50 agents are now running the fix
  Next call with "gas smell" → routes to emergency correctly
  
Cost: $0.17
Time: 30 minutes (automated)
Clients: All notified automatically
Risk: Zero (if validation passes, deployed to all; if fails, none)
```

---

## The Real Architecture

### Master Agent (1)
```
agent_standard_hvac_master (source of truth)
  - Flow version: v20
  - Prompt version: v20
  - Shared with ALL clients
  - Located in: Retell
  - Backed up in: GitHub
  - Updated: Nightly by self-healing loop
```

### Client Agents (50+)
```
agent_client_acme_hvac_001
agent_client_bestair_hvac_002
agent_client_coolrunner_hvac_003
... (48 more)

Each client agent:
  - Points to master flow ID (conversation_flow_34d169608460)
  - Injects client-specific variables:
    {{company_name}} = "ACME HVAC"
    {{phone_number}} = "555-0001"
    {{transfer_phone}} = "555-0002"
    {{manager_name}} = "Mike"
  - Publishes independently to Retell
  - Can have independent call logs (but same core logic)
```

### Supabase Schema
```
hvac_standard_template_versions
├── version: v19
├── timestamp: 2026-03-30 14:00
├── flow_json: {...}
├── changes: "Fixed emergency routing for CO alarm"
├── test_passed: true
├── deployed_to: 50
└── git_commit: abc123

client_agents
├── client_id: "acme_001"
├── agent_id: "agent_xxx1"
├── master_version: v20  ← Points to latest master
├── deployed_at: 2026-04-01 02:30
├── custom_vars: {company_name, phone, etc.}
└── call_log_count: 247
```

### Data Flow on Fix Deployment

```
Master agent (v20) published
        ↓
Supabase: master_version = 20
        ↓
n8n trigger: "New master version available"
        ↓
FOR EACH client_agent WHERE master_version < 20:
  ├─ Fetch master flow (v20) from Retell
  ├─ Load client variables from Supabase
  ├─ Render flow with variables:
  │  - "Hello, {{company_name}}" → "Hello, ACME HVAC"
  │  - "Call {{transfer_phone}}" → "Call 555-0002"
  ├─ Publish to client agent via Retell API
  ├─ Update client_agents.master_version = 20
  ├─ Log: "Client ACME: Deployed v20 ✅"
  └─ Email client: "Your agent improved!"
        ↓
All 50 agents running v20 within 5 minutes
```

---

## How Aggregate Diagnosis Works

### The Call Log Aggregator

```python
def aggregate_calls_for_diagnosis(client_agents: List[str], limit: int = 50):
    """
    Pull calls from all client agents, merge for pattern detection.
    
    Args:
        client_agents: List of 50 agent IDs
        limit: Calls per agent (50 × 50 = 2,500 total calls)
    
    Returns:
        Aggregated call dataset for pattern scanning
    """
    
    all_calls = []
    
    for agent_id in client_agents:
        # Fetch calls for this client
        calls = retell_api.list_calls(agent_id, limit=50)
        
        # Enrich with client metadata
        for call in calls:
            call['source_agent'] = agent_id
            call['source_client'] = resolve_client_from_agent(agent_id)
        
        all_calls.extend(calls)
    
    # Return: 2,500 calls from all clients (rich dataset)
    return all_calls


def diagnose_from_aggregate(all_calls: List[Dict]):
    """
    Same pattern detection, but on aggregate data.
    
    Advantages:
    - Detect rare issues that only happen in specific scenarios
    - See patterns across different client calls
    - Issue frequency is real (25/2500, not 25/50)
    - Confidence in fixes is higher
    """
    
    issues = []
    
    # Pattern 1: Emergency routing (same as before, but aggregate)
    emergency_keywords = ['gas', 'fire', 'smoke', 'flood', 'co alarm']
    emergency_calls = [c for c in all_calls 
                       if any(kw in c['transcript_text'].lower() 
                              for kw in emergency_keywords)]
    
    emergency_not_routed = [c for c in emergency_calls 
                           if 'transfer' not in c['transcript_text'].lower()]
    
    if len(emergency_not_routed) > len(emergency_calls) * 0.1:  # >10% of emergencies
        issues.append({
            "issue_id": "emergency_routing_failure",
            "severity": "CRITICAL",
            "frequency": len(emergency_not_routed),
            "total_emergencies": len(emergency_calls),
            "rate": f"{len(emergency_not_routed)}/{len(emergency_calls)}",
            "affected_clients": len(set(c['source_client'] for c in emergency_not_routed)),
            "description": f"Gas/fire/emergency keywords detected in {len(emergency_calls)} calls, "
                         f"but only {len(emergency_calls) - len(emergency_not_routed)} routed to transfer"
        })
    
    return issues
```

---

## The n8n Deployment Workflow

### Trigger
```
When: New master agent version published
  OR: Manual trigger (Dan clicks "Deploy latest")
  OR: Scheduled (optional backup sync daily)
```

### Workflow Steps
```
1. Read Supabase master_version
   → Current: v20

2. Get all client agents WHERE master_version < v20
   → Returns: [client_1, client_2, ... client_47]
   → Count: 47 agents need updating

3. FOR EACH client agent (parallel, 5 at a time):
   a) Fetch master flow from Retell API
      → conversation_flow_34d169608460
   
   b) Load client variables from Supabase
      → company_name, phone_number, transfer_phone, etc.
   
   c) Render flow with variables
      → Template substitution
      → {{company_name}} → "ACME HVAC"
   
   d) Publish to client agent
      → PUT /update-agent/{agent_id}
      → with rendered flow
   
   e) Publish agent (make live)
      → POST /publish-agent/{agent_id}
   
   f) Update Supabase
      → master_version = v20
      → deployed_at = now()
   
   g) Log deployment
      → GitHub or Supabase log table
      → "Client ACME: v20 deployed ✅"

4. Send batch emails
   TO: [client_1@email, client_2@email, ...]
   SUBJECT: "Your HVAC agent improved!"
   BODY: "New version deployed: Gas smell emergency detection added"

5. Summary notification
   TO: admin@syntharra.com
   FROM: Self-healing loop
   BODY: "47 agents updated to v20 (deployment took 3m 45s)"
```

---

## Cost Model (Corrected)

### Per-Cycle Cost
```
Diagnose (aggregate all client calls):   $0.00 (Retell log read)
Generate fix (Claude):                   $0.02 (1 call)
Validate (1 test on master):             $0.15 (1 test)
Deploy to 50 agents:                     $0.00 (API calls only)
─────────────────────────────────────────────────
Total per fix:                           $0.17
```

### Monthly Cost
```
Fixes per month: 4-8 (depends on real issues)
Cost per agent: $0.17 × 6 fixes ÷ 50 agents = ~$0.02/agent/month

For entire fleet (50 agents): ~$1/month 💰
For 500 agents: ~$1/month (yes, same cost!)
For 5,000 agents: ~$1/month (still the same!)

Why? Because you're fixing 1 template, deploying to all clients.
```

---

## The Real Question: How to Keep Client Configs Separate?

### What Gets Deployed (Template)
```
Conversation flow (nodes, logic, prompts)
├── greeting
├── identify_call
├── emergency routing ← Fixed here
├── leadcapture
└── ... (all 12 nodes with standard HVAC logic)

Cost: Fixed (doesn't change per client)
```

### What Stays Client-Specific
```
Client variables (injected at runtime):
├── {{company_name}}        → "ACME HVAC" vs "Cool Runner"
├── {{phone_number}}        → "555-0001" vs "555-0002"
├── {{transfer_phone}}      → "555-0002" vs "555-0003"
├── {{manager_name}}        → "Mike" vs "Sarah"
├── {{service_area}}        → "New York" vs "Los Angeles"
└── {{call_recording_url}}  → Unique per call

Cost: Zero (just variable substitution)
Handled: In n8n before publishing
```

### Implementation
```python
def deploy_master_to_client(
    master_flow_json: Dict,
    client_id: str,
    master_version: str
) -> bool:
    """
    Take master flow + client variables, deploy to client agent.
    """
    
    # 1. Fetch client variables from Supabase
    client_vars = get_client_variables(client_id)
    # {
    #   "company_name": "ACME HVAC",
    #   "phone_number": "555-0001",
    #   "transfer_phone": "555-0002",
    #   ...
    # }
    
    # 2. Deep copy master flow (don't mutate)
    client_flow = json.loads(json.dumps(master_flow_json))
    
    # 3. Substitute variables in all text fields
    def substitute_variables(text: str, vars: Dict) -> str:
        for key, value in vars.items():
            text = text.replace(f"{{{{{key}}}}}", str(value))
        return text
    
    for node in client_flow['nodes']:
        if 'instructions' in node:
            node['instructions'] = substitute_variables(
                node['instructions'], client_vars
            )
        if 'prompt' in node:
            node['prompt'] = substitute_variables(
                node['prompt'], client_vars
            )
        # ... repeat for all text fields
    
    # 4. Get client's agent ID
    agent_id = get_client_agent_id(client_id)
    
    # 5. Update agent with new flow
    retell_api.update_agent(
        agent_id=agent_id,
        conversation_flow=client_flow
    )
    
    # 6. Publish (make live)
    retell_api.publish_agent(agent_id)
    
    # 7. Log deployment
    log_deployment(client_id, agent_id, master_version)
    
    return True
```

---

## What Happens 3 Months In

### Scenario: Issue on 25 Agents

```
Day 1, 2:00 AM UTC - Self-Healing Loop Runs:

[Diagnose Phase]
├─ Pull 50 calls from each of 50 agents = 2,500 calls total
├─ Scan all 2,500 for patterns
├─ Find: "Gas smell" in 25 calls, but NOT routed to emergency
├─ Frequency: 25/2,500 = 1% (flagged: CRITICAL)
├─ Affected: 25 different clients
└─ Issue detected: "Emergency keywords not routing to transfer"

[Generate Fix Phase]
├─ Claude: "Add 'gas, gas smell' to emergency_condition_edge"
├─ Apply to master agent (v19 → v20)
├─ Publish master
└─ Cost: $0.02

[Validate Phase]
├─ Create test: "Caller: I smell gas"
├─ Run 1-scenario test on master v20
├─ Result: PASS ✅ (agent routes to transfer)
└─ Cost: $0.15

[Deploy Phase]
├─ n8n workflow triggers
├─ FOR EACH of 50 clients:
│  ├─ Fetch v20 (with gas fix)
│  ├─ Inject their variables
│  ├─ Publish to their agent
│  └─ Log deployment
├─ Time: ~3 minutes
├─ All 50 agents now running v20
└─ Cost: $0.00

[Notify Phase]
├─ Email 50 clients:
│  "Your agent improved! Emergency detection enhanced."
└─ Email Dan:
   "v20 deployed to 50 agents. Issue resolved."

Total Cost: $0.17
Total Time: 30 minutes
Clients Fixed: 50
Benefit: All clients immediately get the fix
```

---

## Why This is a Game Changer

### For You
```
✅ One template to manage
✅ Fixes automatically deploy to all clients
✅ No manual deployment, no "I forgot client X"
✅ Cost doesn't scale with # of agents
✅ Build competitive moat (clients improve continuously)
```

### For Clients
```
✅ Their agent gets smarter automatically
✅ No manual upgrade needed
✅ No downtime
✅ Notified of improvements
✅ Huge value add (competitors don't do this)
```

### Competitive Advantage
```
Competitor: "Your agent is good at day 1"
You: "Your agent improves every single night, automatically"

That's unstoppable.
```

---

## Implementation Checklist

```
[PHASE 1: Architecture]
✅ Define master agent (already done)
✅ Define client agent template (already done)
✅ Design deployment workflow (this doc)
✅ Design call log aggregation (added above)

[PHASE 2: Code Updates]
- Update IssueDetector to aggregate from multiple agents
- Build deployment workflow in n8n
- Add Supabase tracking for versions
- Build client variable injection

[PHASE 3: Testing]
- Test on 3 client agents
- Verify deployment works
- Verify client variables injected correctly
- Verify notifications send

[PHASE 4: Go Live]
- Deploy master loop
- Watch it fix, deploy, notify
- Monitor all 50 agents
- Collect metrics
```

---

## The Key Files to Update

```
tools/self-healing-loop.py
  - IssueDetector.diagnose() 
    OLD: Pull calls from 1 agent
    NEW: Pull calls from all 50, aggregate
  
  - FixValidator.validate()
    (no change - still validates on master)

[NEW] tools/deployment-workflow.py
  - Deploy master to all clients
  - Inject variables
  - Parallel execution
  - Error handling + rollback

[NEW] n8n workflow
  - Trigger: Master v published
  - Execute: Python deployment script
  - Log results
  - Email clients
```

Is this the model you were thinking of?

