# Syntharra Supabase Schema

_Exported: 2026-03-27_

**Project:** hgheyqwnrcvwtgngqdnq.supabase.co

---

## hvac_standard_agent

| Column | Notes |
|--------|-------|
| id | str |
| conversation_flow_id | str |
| agent_id | str |
| voice_id | str |
| agent_language | str |
| twilio_from | str |
| twilio_number | str |
| company_name | str |
| owner_name | str |
| company_phone | str |
| website | str |
| years_in_business | str |
| client_email | str |
| timezone | str |
| industry_type | str |
| agent_name | str |
| voice_gender | str |
| custom_greeting | str |
| company_tagline | str |
| services_offered | str |
| brands_serviced | str |
| service_area | str |
| service_area_radius | str |
| certifications | str |
| licensed_insured | str |
| business_hours | str |
| response_time | str |
| emergency_service | str |
| emergency_phone | str |
| after_hours_behavior | str |
| pricing_policy | str |
| diagnostic_fee | str |
| standard_fees | str |
| free_estimates | str |
| financing_available | str |
| financing_details | str |
| warranty | str |
| warranty_details | str |
| payment_methods | str |
| maintenance_plans | str |
| membership_program | str |
| lead_contact_method | str |
| lead_phone | str |
| lead_email | str |
| booking_system | str |
| transfer_phone | str |
| transfer_triggers | str |
| transfer_behavior | str |
| unique_selling_points | str |
| current_promotion | str |
| seasonal_services | str |
| google_review_rating | str |
| google_review_count | str |
| do_not_service | str |
| additional_info | str |
| created_at | str |
| updated_at | str |
| plan_type | str |
| stripe_customer_id | null |
| subscription_id | null |
| timestamp | str |
| notification_email_2 | null |
| notification_email_3 | null |
| notification_sms_2 | null |
| notification_sms_3 | null |

## hvac_call_log

| Column | Notes |
|--------|-------|
| id | str |
| call_id | str |
| agent_id | str |
| company_name | str |
| call_timestamp | str |
| caller_name | str |
| caller_phone | str |
| service_requested | str |
| lead_score | int |
| urgency | str |
| summary | str |
| is_lead | bool |
| duration_seconds | int |
| created_at | str |
| call_tier | str |
| caller_address | str |
| notes | str |
| geocode_status | str |
| geocode_formatted | str |
| job_type | str |
| vulnerable_occupant | bool |
| caller_sentiment | int |

## stripe_payment_data

_Table is empty - columns unknown_

## client_subscriptions

_Table is empty - columns unknown_

## billing_cycles

_Table is empty - columns unknown_

## overage_charges

_Table is empty - columns unknown_

