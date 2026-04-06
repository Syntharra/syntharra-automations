# Retell Git-IaC — Multi-Tenant Scaling Addendum

**Companion to:** `docs/plans/retell-git-iac-execution-playbook.md`
**Purpose:** How Syntharra scales the Git-IaC model from 1 MASTER to thousands of live client agents, with per-client customisation and eventual client self-service.

---

## Core Principle

**Every client agent is a pure function of:**
```
client_flow = build(master_template_at_release_tag, client_overrides)
```

No client flow is ever hand-edited. Every client flow is reproducible from Git + the client's override record. This is what makes 1-to-N fan-out safe and what makes client self-service possible later.

---

## 1. Data Model

### Supabase: `client_agents` table
```
client_id            uuid PK
company_name         text
tier                 text  -- 'standard' | 'premium'
retell_agent_id      text
retell_flow_id       text
retell_phone_number  text
current_release_tag  text  -- e.g. 'release-hvac-standard-v26-emergency-fix'
overrides            jsonb -- client-specific fields
status               text  -- 'active' | 'paused' | 'onboarding' | 'churned'
last_deployed_at     timestamptz
created_at           timestamptz
```

### `overrides` jsonb schema (per client)
```json
{
  "company_name": "Arctic Breeze HVAC",
  "owner_name": "Mike",
  "phone_transfer": "+18563630633",
  "service_area": ["Austin", "Round Rock", "Cedar Park"],
  "hours": {"mon_fri": "7-19", "sat": "8-16", "sun": "closed"},
  "emergency_fee": 150,
  "diagnostic_fee": 89,
  "brands_serviced": ["Trane", "Carrier", "Lennox"],
  "voice_id": "11labs-Adrian",
  "greeting_style": "casual",
  "custom_objection_responses": {},
  "tier_features": {"booking": true, "sms_confirm": true}
}
```

### `client_rollout_log` table
```
id, client_id, from_release, to_release, initiated_at, completed_at,
status ('pending'|'success'|'failed'|'rolled_back'), error, duration_ms
```

---

## 2. Client Onboarding (New Client → Live Agent in Minutes)

`scripts/onboard_client.py`:

1. Read client data from Jotform/HubSpot submission
2. Insert row into `client_agents` with overrides jsonb
3. `build_agent.py --manifest manifests/hvac-{tier}.yaml --overrides <client_id> --out build/{client_id}.json`
4. POST new Retell conversation flow + agent via API
5. Assign phone number from Retell pool
6. PATCH flow with built JSON, publish
7. Update `client_agents` row with agent_id, flow_id, phone, `current_release_tag = <latest master tag>`
8. Smoke call → mark `status = active`

Every new client is born on the latest MASTER release. No drift.

---

## 3. Fleet-Wide Change (The "100 clients, one fix" Question)

`scripts/rollout.py`:

```
python scripts/rollout.py \
    --release release-hvac-standard-v26-emergency-fix \
    --tier standard \
    --strategy canary \
    --canary-size 5 \
    --batch-size 20 \
    --monitor-minutes 120
```

Flow:
1. Verify release tag exists and points to a built, tested template
2. SELECT clients FROM `client_agents` WHERE tier=standard AND status=active
3. **Canary phase:** pick 5 lowest-volume clients. For each:
   - Build flow with new template + that client's overrides
   - PATCH client flow, publish
   - Log to `client_rollout_log`
4. **Monitor window:** watch Supabase `hvac_call_log` for 2 hours. Metrics:
   - Call success rate vs canary's previous 7-day baseline
   - Transfer rate delta
   - Avg call duration delta
   - Any spike in transcript analysis "bad" flags
5. **Gate:** if any canary metric degrades beyond threshold → auto-rollback canary, stop, alert Dan
6. **Full rollout:** remaining clients in batches of 20, parallel within batch, sequential between batches
7. Every client's `current_release_tag` updated on success
8. Final report: N succeeded, N failed, N rolled back, total time

**Scale math:** 1000 clients / 20 per batch × ~5 sec per PATCH = ~4 minutes of API work. Canary monitor is the long pole, not the deploy.

---

## 4. Per-Client Hotfix

A single client needs something changed (new service area, different transfer number, custom greeting):

`scripts/update_client.py --client <id> --set hours.sat="7-18"`

1. Mutate `overrides` jsonb in `client_agents`
2. Rebuild only that client's flow from current release tag + new overrides
3. PATCH that flow, publish
4. Log to `client_rollout_log`

Zero impact on every other client. Zero risk to MASTER.

---

## 5. Per-Client Rollback

`scripts/rollback.py --client <id> --to <previous-release-tag>`

1. Look up client's `overrides` (current, unchanged)
2. Build flow from the *old* release tag + current overrides
3. PATCH flow, publish
4. Update `current_release_tag` back

One client can rollback while the other 999 stay on the new version.

---

## 6. Client Self-Service (Future)

This is why the data model matters. Because `overrides` is the ONLY per-client mutable surface, client self-service becomes a CRUD form over that jsonb field.

### Phase A — Jotform change-request form
Client submits form → n8n webhook → validate against override schema → diff against current overrides → require Dan approval for sensitive fields (transfer number, fees) → auto-apply for safe fields (hours, brands_serviced) → call `update_client.py`.

### Phase B — Client Dashboard (`syntharra-client-dashboard`)
React dashboard. Client logs in, sees their `overrides` as a form:
- Hours editor
- Service area picker
- Emergency fee slider
- Voice selector (from approved list)
- Greeting style dropdown

Save → POST to API → API writes to `client_agents.overrides` → triggers `update_client.py` → flow rebuilt and redeployed → client sees "Changes live" within 30 seconds.

### Phase C — Approval workflow for risky changes
Any override change beyond a whitelist of "safe fields" goes to a `pending_client_changes` queue. Dan (or an agent) reviews, approves, change applies. Auto-approved for low-risk.

### Phase D — Audit log
Every override change logged with who/what/when. Client can see their change history. Syntharra can diff any two points in time for any client.

---

## 7. Why This Scales Cleanly to Thousands

- **Git is the template registry, Supabase is the fleet registry.** Separation of concerns.
- **Rollouts are data-driven, not code-driven.** Adding client #1001 is an INSERT, not a deploy.
- **Per-client state is a single jsonb column.** Easy to index, query, diff, version, backup.
- **Every deploy is reproducible.** `(release_tag, overrides)` → exact flow JSON, every time.
- **Blast radius is bounded.** Canary + batch + per-client rollback means one bad fix can never take down the fleet.
- **Client self-service is the same code path as an internal update.** The dashboard and `update_client.py` and `rollout.py` all end in the same build→patch→publish primitive.
- **Premium and Standard share the pipeline.** Adding a new tier or a new vertical (plumbing, electrical) is a new manifest file, not a new system.

---

## 8. Implementation Order (Phases 6+)

These come AFTER the Standard MASTER promotion (Phase 5) in the main playbook.

**Phase 6 — Client Registry**
- Create `client_agents` and `client_rollout_log` Supabase tables
- Migrate existing clients (if any) into the registry with their current overrides
- Write `scripts/lib/client_resolver.py` — merges manifest + overrides → flow JSON

**Phase 7 — Onboarding Pipeline**
- `scripts/onboard_client.py` wired to Jotform webhook via n8n
- Replaces current manual Retell agent creation
- First live client onboarded via the new pipeline

**Phase 8 — Fleet Rollout**
- `scripts/rollout.py` with canary, batch, monitor, auto-rollback
- First fleet-wide test: a no-op release (template unchanged) to prove the pipeline
- Then a real change (e.g. tightened emergency detection) rolled to all clients

**Phase 9 — Per-Client Ops**
- `scripts/update_client.py` (per-client override edits)
- `scripts/rollback.py --client` (per-client rollback)

**Phase 10 — Client Self-Service**
- Phase A: Jotform change-request form
- Phase B: React dashboard in `syntharra-client-dashboard`
- Phase C: Approval queue for risky changes
- Phase D: Audit log + change history

---

## 9. Guardrails at Scale

- **Override schema validation.** Every override write validated against a JSON schema. Invalid writes rejected before PATCH.
- **Rate limits.** Rollout script respects Retell API rate limits (batch size + sleep).
- **Circuit breaker.** If >5% of canary clients degrade, rollout halts automatically.
- **Dry-run first.** Every rollout and every client update supports `--dry-run` that prints intended PATCH bodies without hitting Retell.
- **Immutable release tags.** Once a release is tagged and clients are on it, that tag is never moved. New fixes = new tags.
- **MASTER is still sacred.** Clients never point at MASTER directly — they point at the release tag MASTER was on at the time of their last deploy. MASTER can move forward while slow-rollout clients stay on older tags safely.

---

This addendum is the answer to: *"How do we fix one thing and push it to 1000 clients safely, and how do clients change their own settings?"*

The architecture handles both because client customisation and fleet-wide change are the same primitive: `build(template, overrides) → PATCH → publish`.
