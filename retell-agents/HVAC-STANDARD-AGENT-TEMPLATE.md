# HVAC Standard Agent — Master Template
> **Source of truth for all Standard HVAC AI receptionist agents.**  
> Generated from live n8n workflow `4Hx7aRdzMl5N0uJP` on 2026-04-02.  
> All new Standard clients get this exact template — no exceptions.  
> To update the template, update the n8n workflow nodes, then re-export here.

---

## What This File Is

This is the canonical reference for the **Standard HVAC Agent template**.  
When onboarding a new Standard client, the n8n workflow reads Jotform data,  
injects it into this template structure, creates a Retell conversation flow + agent,  
and writes all fields to Supabase `hvac_standard_agent`.

**For E2E testing:** the test script (`shared/e2e-test.py`) fires a Jotform  
webhook payload, then validates Supabase + Retell output against the spec below.

---

## Conversation Flow — 12 Nodes (Standard)

| # | Node ID | Internal Name | Type | Purpose |
|---|---|---|---|---|
| 1 | `node-greeting` | `greeting_node` | conversation | Initial greeting — uses custom or default greeting |
| 2 | `node-identify-call` | `identify_call_node` | conversation | Routes caller to correct branch |
| 3 | `node-leadcapture` | `nonemergency_leadcapture_node` | conversation | Captures service/quote leads |
| 4 | `node-verify-emergency` | `verify_emergency_node` | conversation | Confirms if situation is emergency |
| 5 | `node-existing-customer` | `existing_customer_node` | conversation | Handles existing customer enquiries |
| 6 | `node-general-questions` | `general_questions_node` | conversation | Answers FAQs using company info |
| 7 | `node-callback` | `callback_node` | conversation | Captures callback request details |
| 8 | `node-spam-robocall` | `spam_robocall_node` | conversation | Handles spam/robocall politely + ends |
| 9 | `node-transfer-call` | `Transfer Call` | transfer_call | Cold transfers to configured number |
| 10 | `node-transfer-failed` | `transfer_failed_node` | conversation | Takes message if transfer fails |
| 11 | `node-ending` | `Ending` | conversation | Closing — asks if anything else needed |
| 12 | `node-end-call` | `End Call` | end | Terminates the call |

### identify_call routing edges
```
Repair / Service / Maintenance      → node-leadcapture
Quote / Estimate / Price / Install  → node-leadcapture
Emergency                           → node-verify-emergency
Existing Customer                   → node-existing-customer
General Questions                   → node-general-questions
Live Person / Owner / Manager       → node-transfer-call
Callback Request                    → node-callback
Spam / Robocall / Scam             → node-spam-robocall
```

---

## Agent Configuration (Standard)

| Setting | Value |
|---|---|
| Voice (female) | `retell-Sloane` |
| Voice (male) | `retell-Nico` |
| Language | `multi` (multilingual) |
| Webhook URL | `https://n8n.syntharra.com/webhook/retell-hvac-webhook` |
| Ambient sound | `call-center` at volume `0.8` |
| Max call duration | `600000ms` (10 min) |
| Post-call analysis | call_summary, call_successful, user_sentiment |
| Model | `gpt-4.1` (cascading) |
| flex_mode | `false` |
| start_speaker | `agent` |

---

## Supabase Fields Written on Onboarding (`hvac_standard_agent`)

All fields below are populated from Jotform → n8n → Supabase on every new Standard client.

### System
| Column | Source | Notes |
|---|---|---|
| `agent_id` | Retell API response | Foreign key to Retell |
| `conversation_flow_id` | Retell API response | |
| `voice_id` | Build Retell Prompt | retell-Sloane or retell-Nico |
| `agent_language` | hardcoded | `en-US` |
| `industry_type` | hardcoded | `HVAC` |
| `plan_type` | hardcoded | `standard` |
| `timestamp` | n8n | ISO8601 |

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
| Column | Jotform Field | Key |
|---|---|---|
| `agent_name` | q10 | `q10_aiAgent10` |
| `voice_gender` | q11 | `q11_aiVoice` |
| `custom_greeting` | q38 | `q38_customGreeting` |
| `company_tagline` | q39 | `q39_companyTagline` |

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

### Additional Notification Contacts
| Column | Jotform Field | Key |
|---|---|---|
| `notification_email_2` | q66 | `q66_notifEmail2` |
| `notification_email_3` | q67 | `q67_notifEmail3` |
| `notification_sms_2` | q64 | `q64_notifSms2` |
| `notification_sms_3` | q65 | `q65_notifSms3` |

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

### Billing (written by Stripe workflow, not onboarding)
| Column | Source |
|---|---|
| `stripe_customer_id` | Stripe webhook |
| `subscription_id` | Stripe webhook |

---

## n8n Workflow — Node Pipeline

```
JotForm Webhook Trigger
  → Parse JotForm Data          [maps all 52 Jotform fields to clean vars]
  → Validate: Token Budget      [guards against oversized prompts]
  → Build Retell Prompt         [builds global_prompt + 12-node conversation flow]
  → Create Retell LLM           [POST /create-conversation-flow → returns flow ID]
  → IF LLM Error                [on error → Error Notification Email → stop]
  → Create Retell Agent         [POST /create-agent → returns agent ID]
  → IF Agent Error              [on error → Error Notification Email → stop]
  → Merge LLM & Agent Data      [combines all data into Supabase payload]
  → Write Client Data to Supabase [POST hvac_standard_agent]
  → Publish Retell Agent        [POST /publish-agent/AGENT_ID]
  → Reconcile: Check Stripe     [waits 60s, checks stripe_payment_data]
  → Build Welcome Email HTML    [renders branded email]
  → Send Setup Instructions     [SMTP2GO send]
  → Email Summary to Dan        [internal notification]
```

---

## E2E Test Reference

**Test script:** `shared/e2e-test.py`  
**Webhook:** `POST https://n8n.syntharra.com/webhook/jotform-hvac-onboarding`  
**Test company:** `Polar Peak HVAC {timestamp}`  
**Cleanup:** auto-deletes Retell agent + flow + Supabase row after 5 min

### Assertions (75 total)
- HTTP 200 from webhook ✅
- Supabase row created with all 40+ fields populated ✅
- Retell agent exists + published ✅
- Conversation flow: exactly **12 nodes** ✅
- callback_node present ✅
- spam_robocall_node present ✅
- Call processor: lead scored, logged to hvac_call_log ✅
- Stripe gate: correctly skips Twilio in TEST mode ✅

---

## How to Update This Template

1. Edit the **Build Retell Prompt** node in n8n workflow `4Hx7aRdzMl5N0uJP`
2. Test via E2E test (`python3 shared/e2e-test.py`)
3. When passing, update this file to reflect changes
4. Push to GitHub

> ⚠️ **Never edit this MD directly as a substitute for updating n8n.**  
> n8n is the live source. This file is the documented reference.

---

## Version History

| Date | Change | Nodes |
|---|---|---|
| 2026-04-02 | **CURRENT** — callback + spam_robocall restored; notification fields fixed | 12 |
| pre-2026-04-02 | Missing callback + spam nodes; notification fields not mapped | 10 |
| Arctic Breeze live | emergency_fallback + spanish_routing added (client-specific) | 14 |
