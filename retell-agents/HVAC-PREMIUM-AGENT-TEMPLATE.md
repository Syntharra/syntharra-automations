# HVAC Premium Agent — Master Template
> **Source of truth for all Premium HVAC AI receptionist agents.**  
> Generated from live n8n workflow `kz1VmwNccunRMEaF` + live Premium agent `agent_9822f440f5c3a13bc4d283ea90` on 2026-04-02.  
> All new Premium clients get this exact template — no exceptions.  
> To update the template, update the n8n workflow nodes, then re-export here.

---

## What This File Is

This is the canonical reference for the **Premium HVAC Agent template**.  
When onboarding a new Premium client, the n8n workflow reads Jotform data,  
injects it into this template structure, creates a Retell conversation flow + agent,  
and writes all fields to Supabase `hvac_standard_agent` with `plan_type = 'premium'`.

**Premium differs from Standard in three key ways:**
1. **18-node conversation flow** (vs 12) — adds full booking engine (capture → availability → confirm → reschedule → cancel → fallback)
2. **Integration awareness** — routes to calendar dispatcher (Google Calendar, Calendly, Jobber, etc.) via n8n tool calls
3. **Premium call processor** — detects repeat callers, extracts booking outcomes (appointment_date, job_type_booked, booking_success)

**For E2E testing:** the test script (`shared/e2e-test-premium.py`) fires a Jotform  
webhook payload, then validates Supabase + Retell output against the spec below.

---

## Conversation Flow — 18 Nodes (Premium)

| # | Node ID | Internal Name | Type | Purpose |
|---|---|---|---|---|
| 1 | `node-greeting` | `greeting_node` | conversation | Initial greeting — uses greeting resolved from style + custom text |
| 2 | `node-identify-call` | `identify_call_node` | conversation | Routes caller to correct branch |
| 3 | `node-booking-capture` | `booking_capture_node` | conversation | Captures service type, preferred date/time for booking |
| 4 | `node-check-availability` | `check_availability_node` | conversation | Checks calendar availability via dispatcher tool |
| 5 | `node-confirm-booking` | `confirm_booking_node` | conversation | Confirms appointment details and books via dispatcher |
| 6 | `node-reschedule` | `reschedule_node` | conversation | Handles reschedule requests |
| 7 | `node-cancel-appointment` | `cancel_appointment_node` | conversation | Handles cancellation requests |
| 8 | `node-fallback-leadcapture` | `fallback_leadcapture_node` | conversation | Lead capture fallback when calendar unavailable or caller declines booking |
| 9 | `node-verify-emergency` | `verify_emergency_node` | conversation | Confirms if situation is emergency |
| 10 | `node-callback` | `callback_node` | conversation | Captures callback request details |
| 11 | `node-existing-customer` | `existing_customer_node` | conversation | Handles existing customer enquiries |
| 12 | `node-general-questions` | `general_questions_node` | conversation | Answers FAQs using company info |
| 13 | `node-spam-robocall` | `spam_robocall_node` | conversation | Handles spam/robocall politely + ends |
| 14 | `node-transfer-call` | `Transfer Call` | transfer_call | Cold transfers to configured number (non-emergency) |
| 15 | `node-emergency-transfer` | `Emergency Transfer` | transfer_call | Direct transfer to emergency line |
| 16 | `node-transfer-failed` | `transfer_failed_node` | conversation | Takes message if transfer fails |
| 17 | `node-ending` | `Ending` | conversation | Closing — asks if anything else needed |
| 18 | `node-end-call` | `End Call` | end | Terminates the call |

### identify_call routing edges
```
New service / repair / maintenance / quote / install   → node-booking-capture
Reschedule appointment                                 → node-reschedule
Cancel appointment                                     → node-cancel-appointment
Emergency                                              → node-verify-emergency
Existing customer enquiry                              → node-existing-customer
General questions                                      → node-general-questions
Transfer request / live person / manager               → node-transfer-call
Callback request                                       → node-callback
Spam / robocall                                        → node-spam-robocall
```

### booking_capture routing edges
```
Caller provides job type + date/time preference        → node-check-availability
Caller declines to book / prefers lead capture         → node-fallback-leadcapture
Emergency detected                                     → node-verify-emergency
```

### check_availability → confirm_booking → end
```
Slot available → confirm_booking → ending → end-call
No slot available → fallback-leadcapture → ending → end-call
```

---

## Agent Configuration (Premium)

| Setting | Value |
|---|---|
| Voice (female) | `retell-Sloane` |
| Voice (male) | `retell-Nico` |
| Language | `multi` (multilingual) |
| Webhook URL | `https://n8n.syntharra.com/webhook/retell-hvac-premium-webhook` |
| Ambient sound | `call-center` at volume `0.8` |
| Max call duration | `600000ms` (10 min) |
| Post-call analysis | call_summary, call_successful, user_sentiment, booking_attempted, booking_success, appointment_date, appointment_time, job_type_booked |
| Model | `gpt-4.1` (cascading) |
| flex_mode | `false` |
| start_speaker | `agent` |

> **Note**: Premium agent `agent_name` in Retell is set to `{company_name} - HVAC Premium`. The receptionist name (e.g. "Nova") appears in the conversation flow greeting and global prompt — not as the Retell `agent_name` field.

---

## Supabase Fields Written on Onboarding (`hvac_standard_agent`)

All fields below are populated from Jotform → n8n → Supabase on every new Premium client.

### System
| Column | Source | Notes |
|---|---|---|
| `agent_id` | Retell API response | Foreign key to Retell |
| `conversation_flow_id` | Retell API response | |
| `voice_id` | Build Premium Prompt | retell-Sloane or retell-Nico |
| `industry_type` | hardcoded | `HVAC` |
| `plan_type` | hardcoded | `premium` |

### Business Info (from Jotform)
| Column | Jotform Field | Key |
|---|---|---|
| `company_name` | q4 | `q4_hvacCompany` |
| `owner_name` | q54 | `q54_ownerName` |
| `company_phone` | q6 | `q6_mainCompany` |
| `client_email` | q5 | `q5_emailAddress` |
| `website` | q7 | `q7_companyWebsite` |
| `years_in_business` | q8 | `q8_yearsIn` |
| `timezone` | q34 | `q34_timezone` |
| `services_offered` | q13 | `q13_servicesOffered` |
| `brands_serviced` | q14 | `q14_brandsequipmentServiced` |
| `service_area` | q16 | `q16_primaryService` |
| `service_area_radius` | q40 | `q40_serviceAreaRadius` |
| `certifications` | q29 | `q29_certifications` |
| `licensed_insured` | q28 | `q28_licensedAnd` |

### AI Configuration
| Column | Jotform Field | Key | Notes |
|---|---|---|---|
| `agent_name` | q10 | `q10_aiAgent10` | Receptionist name (e.g. "Nova") |
| `voice_gender` | q11 | `q11_aiVoice` | Male or Female |
| `greeting_style` | q75 | `q75_greetingStyle` | warm / professional / urgent/direct / custom / standard |
| `custom_greeting` | resolved | — | Computed server-side from q75 style + q76 custom text |
| `company_tagline` | q39 | `q39_companyTagline` | |

> **Premium greeting resolution**: Unlike Standard (which uses `q38_customGreeting` directly), Premium resolves the greeting server-side in the Parse JotForm Premium Data node using `resolveGreeting(style, customText, agentName, companyName)`. The `custom_greeting` field in Supabase always contains the final resolved string.

### Hours & Availability
| Column | Jotform Field | Key |
|---|---|---|
| `business_hours` | q17 | `q17_businessHours` |
| `response_time` | q18 | `q18_typicalResponse` |
| `emergency_service` | q20 | `q20_247Emergency` |
| `emergency_phone` | q21 | `q21_emergencyAfterhours` |
| `after_hours_behavior` | q22 | `q22_afterhoursBehavior` |

### Pricing & Policies
| Column | Jotform Field | Key |
|---|---|---|
| `pricing_policy` | q42 | `q42_pricingPolicy` |
| `diagnostic_fee` | q41 | `q41_diagnosticFee` |
| `standard_fees` | q43 | `q43_standardFees` |
| `free_estimates` | q24 | `q24_freeEstimates` |
| `financing_available` | q25 | `q25_financingAvailable` |
| `financing_details` | q44 | `q44_financingDetails` |
| `warranty` | q26 | `q26_serviceWarranties` |
| `warranty_details` | q27 | `q27_warrantyDetails` |
| `payment_methods` | q45 | `q45_paymentMethods` |
| `maintenance_plans` | q46 | `q46_maintenancePlans` |
| `membership_program` | q58 | `q58_membershipProgramName` |

### Lead & Transfer
| Column | Jotform Field | Key |
|---|---|---|
| `lead_contact_method` | q31 | `q31_leadContact` |
| `lead_phone` | q32 | `q32_leadNotification` |
| `lead_email` | q33 | `q33_leadNotification33` |
| `transfer_phone` | q48 | `q48_transferPhone` |
| `transfer_triggers` | q49 | `q49_transferTriggers` |
| `transfer_behavior` | q50 | `q50_transferBehavior` |

### Additional Notification Contacts (Premium — different from Standard)
> ⚠️ Premium uses `q79–q82`. Standard uses `q64–q67`. Do NOT mix these up.

| Column | Jotform Field | Key |
|---|---|---|
| `notification_sms_2` | q79 | `q79_notifSms2` |
| `notification_sms_3` | q80 | `q80_notifSms3` |
| `notification_email_2` | q81 | `q81_notifEmail2` |
| `notification_email_3` | q82 | `q82_notifEmail3` |

### Branding & Extras
| Column | Jotform Field | Key |
|---|---|---|
| `google_review_rating` | q55 | `q55_googleReviewRating` |
| `google_review_count` | q56 | `q56_googleReviewCount` |
| `unique_selling_points` | q51 | `q51_uniqueSellingPoints` |
| `current_promotion` | q52 | `q52_currentPromotion` |
| `seasonal_services` | q53 | `q53_seasonalServices` |
| `do_not_service` | q57 | `q57_doNotServiceList` |
| `additional_info` | q37 | `q37_additionalInfo` |

### Premium-Only Booking Fields (Section 7 of Jotform)
| Column | Jotform Field | Key | Default |
|---|---|---|---|
| `slot_duration_minutes` | q87 | `q87_slot_duration` | 60 |
| `buffer_time_minutes` | q90 | `q90_buffer_time` | 30 |
| `min_notice_hours` | q88 | `q88_min_notice` | 2 |
| `booking_hours` | q89 | `q89_booking_hours` | — |
| `bookable_job_types` | q86 | `q86_bookable_job_types` | JSON array |
| `booking_confirmation_method` | q91 | `q91_confirmation_method` | email |

### Billing (written by Stripe workflow, not onboarding)
| Column | Source |
|---|---|
| `stripe_customer_id` | Stripe webhook |
| `subscription_id` | Stripe webhook |

---

## n8n Workflow — Node Pipeline

```
JotForm Premium Webhook Trigger  (path: /webhook/jotform-hvac-premium-onboarding)
  → Parse JotForm Premium Data    [maps all Jotform fields; resolves greeting from style]
  → Build Premium Prompt + Flow   [builds global_prompt + 18-node conversation flow]
  → Create Retell Conversation Flow  [POST /create-conversation-flow → returns flow ID]
  → Build Agent Payload           [combines flow ID + agent config]
  → Create Retell Agent           [POST /create-agent → returns agent ID]
  → Extract Agent ID              [pulls agent_id + conversation_flow_id]
  → Save to Supabase              [POST hvac_standard_agent with plan_type='premium']
  → Update Supabase with Agent ID [PATCH to add agent_id + conversation_flow_id]
  → Publish Retell Agent          [POST /publish-agent/AGENT_ID]
  → Stripe Gate (IF)              [if stripe_customer_id present → purchase Twilio number]
  → Build Integration Email HTML  [renders OAuth/setup email]
  → Send Integration Setup Email  [SMTP2GO: OAuth links for Google Calendar / Outlook etc.]
  → Email Summary to Dan          [internal notification]
```

---

## Premium Call Processor — Architecture

**Workflow:** `STQ4Gt3rH8ptlvMi`  
**Webhook:** `/webhook/retell-hvac-premium-webhook`  
**Rebuilt:** 2026-04-02 (original had `n8n-nodes-base.filter` bug — crashed silently)

```
Retell Premium Webhook
  → Filter: call_analyzed Only    [n8n-nodes-base.if — must NOT be filter node type]
  → Extract Call Data             [agent_id, call_id, transcript, from_number]
  → Look Up Client (Supabase)     [hvac_standard_agent by agent_id]
  → Parse Client Data             [extracts company_name, lead_email, etc.]
  → Check Repeat Caller           [queries hvac_call_log for previous calls]
  → GPT: Analyze Call             [gpt-4o-mini — returns nested section-header JSON]
  → Parse Lead Data               [flattens nested GPT response using section keys]
  → Is Lead? (IF)                 [score >= 6 → notify path; else → log only]
  → Log Call to Supabase          [hvac_call_log with call_tier='Premium']
  → Route Notifications           [determines if email/SMS notification needed]
  → Should Notify? (IF)           [routes to notification or log-only]
  → Send Client Email / SMS       [lead notification to client]
  → Internal Notification         [Syntharra admin alerts on errors]
```

### GPT Response Format (Premium-Specific)
The Premium GPT prompt returns **nested JSON with section headers**:
```json
{
  "CALLER INFORMATION": { "caller_name": "...", "caller_phone": "...", ... },
  "CALL CLASSIFICATION": { "service_requested": "...", "urgency": "...", ... },
  "BOOKING DATA": { "booking_attempted": true, "booking_success": true, ... },
  "LEAD QUALIFICATION": { "lead_score": 9, "is_lead": true, ... },
  "ADDITIONAL": { "summary": "...", "notes": "..." }
}
```
Parse Lead Data flattens this using section-key extraction (`ci`, `cc`, `bd`, `lq`, `ad`).

> ⚠️ **Code length limit on Parse Lead Data**: Keep under ~1100 chars. The Railway n8n instance has a JS compilation limit. Exceeding it causes a workflow-level crash with empty runData.

---

## Integration Dispatcher Pipeline (Premium-Only)

Premium clients connect a calendar/CRM platform via OAuth. Once connected, the **Premium Integration Dispatcher** (`73Y0MHVBu05bIm5p`) routes booking tool calls to the correct platform:

| Platform | Dispatcher Workflow |
|---|---|
| Google Calendar | `rGrnCr5mPFP2TIc7` |
| Outlook / Microsoft 365 | `La99yvfmWg6AuvM2` |
| Calendly | `b9xRG7wtqCZ5fdxo` |
| Jobber | `BxnR17qUfAb5BZCz` |
| HubSpot | `msEy13eRz66LPxW6` |

Token refresh: `5vphecmEhxnwFz2X` runs daily at 02:00 UTC.

---

## E2E Test Reference

**Test script:** `shared/e2e-test-premium.py`  
**Webhook:** `POST https://n8n.syntharra.com/webhook/jotform-hvac-premium-onboarding`  
**Test company:** `FrostKing HVAC Premium {timestamp}` (Dallas/Fort Worth, Texas)  
**Cleanup:** auto-deletes Retell agent + flow + Supabase row after 5 min

### Assertions (89 total)
- HTTP 200 from Premium onboarding webhook ✅
- n8n Premium onboarding workflow executes successfully ✅
- Supabase row created with `plan_type='premium'` ✅
- All 49 Supabase fields populated (standard + Premium booking fields) ✅
- Premium notification fields (q79-q82) correctly mapped ✅
- Retell agent: webhook URL = `/webhook/retell-hvac-premium-webhook` ✅
- Conversation flow: exactly **18 nodes** ✅
- All 6 Premium-only nodes present (booking_capture, check_availability, confirm_booking, reschedule, cancel_appointment, fallback_leadcapture) ✅
- Emergency transfer node present ✅
- Premium call processor: call logged with `call_tier='Premium'` ✅
- GPT extraction: caller_name, caller_phone, service_requested, lead_score ≥ 6 ✅
- Dedup: second identical call_id not logged ✅
- Stripe gate: correctly skips Twilio in TEST mode ✅

---

## How to Update This Template

1. Edit the **Build Premium Prompt + Flow** node in n8n workflow `kz1VmwNccunRMEaF`
2. Test via E2E test (`python3 shared/e2e-test-premium.py`)
3. When passing, update this file to reflect changes
4. Push to GitHub

> ⚠️ **Never edit this MD directly as a substitute for updating n8n.**  
> n8n is the live source. This file is the documented reference.

---

## Version History

| Date | Change | Nodes |
|---|---|---|
| 2026-04-02 | **CURRENT** — Premium E2E 89/89 passing; call processor rebuilt from Standard base; Parse Lead Data nested JSON flattener added; 18-node flow verified | 18 |
| pre-2026-04-02 | Premium call processor using `n8n-nodes-base.filter` — crashed silently, never logged a call | 18 |
