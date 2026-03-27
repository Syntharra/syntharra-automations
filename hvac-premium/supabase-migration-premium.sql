-- ============================================================
-- Syntharra HVAC Premium — Supabase Migration
-- Run in Supabase SQL Editor
-- ============================================================

-- ── hvac_premium_agent ───────────────────────────────────────
-- Mirrors hvac_standard_agent + premium-only columns

CREATE TABLE IF NOT EXISTS hvac_premium_agent (
  id                        UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at                TIMESTAMPTZ DEFAULT now(),

  -- Core identity
  agent_id                  TEXT UNIQUE NOT NULL,
  company_name              TEXT,
  agent_name                TEXT,
  client_email              TEXT,

  -- Contact
  main_phone                TEXT,
  lead_phone                TEXT,
  lead_email                TEXT,
  transfer_phone            TEXT,
  emergency_phone           TEXT,
  website                   TEXT,

  -- Notification recipients (up to 3 per channel)
  notification_email_2      TEXT,
  notification_email_3      TEXT,
  notification_sms_2        TEXT,
  notification_sms_3        TEXT,

  -- Business profile
  industry_type             TEXT DEFAULT 'HVAC',
  years_in_business         TEXT,
  services_offered          TEXT,
  brands_serviced           TEXT,
  service_area              TEXT,
  service_area_radius       TEXT,
  business_hours            TEXT,
  response_time             TEXT,
  timezone                  TEXT DEFAULT 'America/Chicago',

  -- Emergency
  emergency_service         TEXT DEFAULT 'No',
  after_hours_behavior      TEXT,
  after_hours_transfer      TEXT DEFAULT 'all',

  -- Pricing
  free_estimates            TEXT DEFAULT 'Yes - always free',
  diagnostic_fee            TEXT,
  pricing_policy            TEXT,
  standard_fees             TEXT,
  financing_available       TEXT DEFAULT 'No',
  financing_details         TEXT,

  -- Credentials & warranty
  warranty                  TEXT DEFAULT 'Yes',
  warranty_details          TEXT,
  licensed_insured          TEXT DEFAULT 'Yes',
  certifications            TEXT,

  -- Payments & plans
  payment_methods           TEXT,
  maintenance_plans         TEXT DEFAULT 'No',
  membership_program        TEXT,

  -- Agent config
  voice_gender              TEXT DEFAULT 'female',
  voice_id                  TEXT,
  custom_greeting           TEXT,
  company_tagline           TEXT,
  transfer_triggers         TEXT,
  transfer_behavior         TEXT,
  lead_contact_method       TEXT,

  -- Marketing
  unique_selling_points     TEXT,
  current_promotion         TEXT,
  seasonal_services         TEXT,
  google_review_rating      TEXT,
  google_review_count       TEXT,
  owner_name                TEXT,
  do_not_service            TEXT,
  additional_info           TEXT,

  -- Billing
  plan_name                 TEXT DEFAULT 'Premium',
  plan_billing              TEXT,
  minutes_included          INTEGER DEFAULT 1000,
  stripe_customer_id        TEXT,
  stripe_subscription_id    TEXT,

  -- ── PREMIUM-ONLY COLUMNS ──────────────────────────────────
  crm_platform              TEXT,           -- Jobber, ServiceTitan, Housecall Pro, custom, none
  calendar_platform         TEXT,           -- Google Calendar, Calendly, Jobber, ServiceTitan, Housecall Pro, custom
  booking_slot_duration     INTEGER DEFAULT 60,   -- minutes per slot
  booking_lead_time         INTEGER DEFAULT 2,    -- minimum hours before booking
  bookable_job_types        TEXT,           -- comma-separated list
  booking_confirm_method    TEXT DEFAULT 'email', -- email, sms, both
  available_time_slots      TEXT,           -- e.g. "Morning (8am-12pm), Afternoon (12pm-5pm)"
  booking_buffer_minutes    INTEGER DEFAULT 30,
  calendar_webhook_url      TEXT,           -- n8n webhook for calendar check/create
  crm_webhook_url           TEXT,           -- n8n webhook for CRM push
  calendar_api_key          TEXT,           -- encrypted credential placeholder
  crm_api_key               TEXT,           -- encrypted credential placeholder
  calendar_resource_id      TEXT,           -- calendar ID / resource ID for the integration

  -- Status
  is_active                 BOOLEAN DEFAULT true,
  onboarding_complete       BOOLEAN DEFAULT false,
  retell_flow_id            TEXT
);

-- ── hvac_premium_call_log ─────────────────────────────────────
-- Mirrors hvac_call_log + booking-specific columns

CREATE TABLE IF NOT EXISTS hvac_premium_call_log (
  id                        UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at                TIMESTAMPTZ DEFAULT now(),

  -- Agent / client
  agent_id                  TEXT NOT NULL,
  company_name              TEXT,
  call_tier                 TEXT DEFAULT 'premium',

  -- Retell call data
  call_id                   TEXT UNIQUE,
  call_duration_seconds     INTEGER,
  call_status               TEXT,
  call_successful           BOOLEAN,
  call_summary              TEXT,

  -- Caller info
  caller_name               TEXT,
  caller_phone              TEXT,
  caller_address            TEXT,
  caller_sentiment          TEXT,

  -- Standard lead fields (used when booking not made)
  lead_score                INTEGER,
  is_lead                   BOOLEAN DEFAULT false,
  is_hot_lead               BOOLEAN DEFAULT false,
  job_type                  TEXT,
  urgency                   TEXT,
  vulnerable_occupant       BOOLEAN DEFAULT false,
  notes                     TEXT,
  service_requested         TEXT,

  -- Geocoding
  geocode_status            TEXT,
  geocode_formatted         TEXT,

  -- ── PREMIUM BOOKING FIELDS ────────────────────────────────
  booking_attempted         BOOLEAN DEFAULT false,
  booking_success           BOOLEAN DEFAULT false,
  appointment_date          DATE,
  appointment_time_window   TEXT,           -- morning / afternoon
  job_type_booked           TEXT,
  reschedule_or_cancel      TEXT DEFAULT 'neither', -- reschedule / cancel / neither
  calendar_event_id         TEXT,           -- ID of the created calendar event
  crm_job_id                TEXT,           -- ID of the job created in CRM

  -- Notification tracking
  notification_sent         BOOLEAN DEFAULT false,
  notification_email_sent   BOOLEAN DEFAULT false,
  notification_sms_sent     BOOLEAN DEFAULT false
);

-- ── Indexes ───────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_hvac_premium_agent_agent_id    ON hvac_premium_agent(agent_id);
CREATE INDEX IF NOT EXISTS idx_hvac_premium_call_log_agent_id ON hvac_premium_call_log(agent_id);
CREATE INDEX IF NOT EXISTS idx_hvac_premium_call_log_call_id  ON hvac_premium_call_log(call_id);
CREATE INDEX IF NOT EXISTS idx_hvac_premium_call_booking      ON hvac_premium_call_log(booking_success, appointment_date);

-- ── RLS (match standard pattern) ─────────────────────────────
ALTER TABLE hvac_premium_agent    ENABLE ROW LEVEL SECURITY;
ALTER TABLE hvac_premium_call_log ENABLE ROW LEVEL SECURITY;
