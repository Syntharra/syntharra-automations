# System Audit — 2026-03-27

## E2E Test: 78/78 PASSED ✅

## Systems Audit

### n8n Workflows
- 12 active workflows, 3 inactive (old scenario runners), 9 archived
- All active workflows executing successfully
- No hardcoded email issues in critical paths
- Error handling present on all HTTP request nodes in onboarding

### Retell
- 4 unique agents (Polar Peak TEST, Demo Sophie, Demo Jake, HVAC Standard)
- 2 conversation flows linked to agents
- **60 orphaned flows cleaned up** (leftover from E2E tests)
- Warm transfer configured on both Transfer Call and Emergency Transfer nodes

### Supabase
- All tables exist with correct schemas
- transfer_attempted and transfer_success columns added to hvac_call_log
- after_hours_transfer column added to hvac_standard_agent

### Prompt Builder (v6.4)
- 13 unique node IDs, all valid
- Warm transfer on both transfer nodes
- After-hours section conditionally injected (requires businessHours + non-default setting)
- 7 finetune example sets on identify_call
- No duplicate name step in lead capture
- Emergency transfer separate from general transfer

### Call Processor
- 25 nodes, all functioning
- GPT detects transfer_attempted and transfer_success
- Classify Notification handles: lead, emergency, customer_query, transfer_failed, log_only
- Email subjects differentiated per type (📵 📞 🚨 💬)
- Supabase Log Call writes all 21 expected fields

### Jotform
- 59 questions total
- 3 new toggle questions (q69, q70, q71) for conditional sections
- q68 after-hours transfer question with value mapping
- Conditional logic rules documented (7 rules, must set in UI)
- Field IDs mapped with backward compatibility (q64-67 primary, q59-62 fallback)

## Improvements Made This Session
1. Email Summary to Dan double-brace bug fixed
2. Transfer number logic fixed (transfer_phone default, emergency override)
3. Emergency Transfer node added (13 nodes)
4. Warm transfer with whisper on both transfer nodes
5. Lead capture duplicate name step fixed
6. Improved prompts on verify_emergency, identify_call, callback, general_questions
7. 7 finetune example sets on identify_call (was 5)
8. Transfer-failed notification pipeline (GPT → Classify → Email/SMS)
9. After-hours configurable behavior (all/emergency_only/never)
10. Jotform toggle questions for shorter form
11. 60 orphaned Retell flows cleaned up
12. 3 old scenario runners deactivated
13. Jotform field ID mapping fixed (q64-67)

## Pre-Launch Checklist
- [ ] Set Jotform conditional logic in UI (7 rules)
- [ ] Fix Jotform rule 1: use IS NOT EQUAL TO "No" (not IS EQUAL TO "Yes - 24/7")
- [ ] Switch Stripe to live mode (products, prices, coupons, webhook)
- [ ] Update Railway STRIPE_SECRET_KEY to sk_live_
- [ ] Telnyx AI evaluation approval → buy toll-free number
- [ ] Change internal notification emails to support@syntharra.com
- [ ] Test with a real Jotform submission (not webhook POST)
