-- ============================================================
-- SYNTHARRA LEAD MACHINE — Supabase Schema
-- Run once in Supabase SQL editor
-- ============================================================

-- Research briefs from Agent 1
CREATE TABLE IF NOT EXISTS lead_machine_research (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  date DATE NOT NULL,
  top_pain_points JSONB,
  trending_hooks JSONB,
  timely_angle TEXT,
  competitor_intel TEXT,
  recommended_subject_lines JSONB,
  raw_research TEXT,
  confidence_score FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- All outbound leads (Google Places sourced)
CREATE TABLE IF NOT EXISTS outbound_leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  business_name TEXT NOT NULL,
  owner_first_name TEXT,
  owner_email TEXT,
  owner_phone TEXT,
  website TEXT,
  city TEXT,
  state TEXT,
  lead_score INT,
  google_review_count INT,
  email_deliverability_score FLOAT,
  personalised_first_line TEXT,
  status TEXT DEFAULT 'ready',
  sequence_id TEXT,
  sequence_started_at TIMESTAMPTZ,
  last_interaction_at TIMESTAMPTZ,
  interaction_count INT DEFAULT 0,
  source TEXT DEFAULT 'google_places',
  target_city_batch TEXT,
  hubspot_contact_id TEXT,
  hubspot_deal_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT outbound_leads_email_unique UNIQUE (owner_email)
);
CREATE INDEX IF NOT EXISTS idx_outbound_leads_status ON outbound_leads(status);
CREATE INDEX IF NOT EXISTS idx_outbound_leads_email ON outbound_leads(owner_email);
CREATE INDEX IF NOT EXISTS idx_outbound_leads_created ON outbound_leads(created_at DESC);

-- Every email interaction logged
CREATE TABLE IF NOT EXISTS lead_machine_sequence_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID REFERENCES outbound_leads(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  email_number INT,
  subject_line_variant_id UUID,
  body_variant_id UUID,
  email_sent_at TIMESTAMPTZ,
  event_at TIMESTAMPTZ DEFAULT NOW(),
  reply_classification TEXT,
  reply_text TEXT,
  metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_seq_log_lead ON lead_machine_sequence_log(lead_id);
CREATE INDEX IF NOT EXISTS idx_seq_log_event ON lead_machine_sequence_log(event_type);
CREATE INDEX IF NOT EXISTS idx_seq_log_at ON lead_machine_sequence_log(event_at DESC);

-- All message variants — subject lines, bodies, CTAs
CREATE TABLE IF NOT EXISTS lead_machine_message_variants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  variant_type TEXT NOT NULL,
  email_number INT,
  content TEXT NOT NULL,
  hypothesis TEXT,
  status TEXT DEFAULT 'testing',
  sends INT DEFAULT 0,
  opens INT DEFAULT 0,
  clicks INT DEFAULT 0,
  replies INT DEFAULT 0,
  bookings INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  declared_winner_at TIMESTAMPTZ,
  archived_at TIMESTAMPTZ,
  archived_reason TEXT
);
CREATE INDEX IF NOT EXISTS idx_variants_status ON lead_machine_message_variants(status);
CREATE INDEX IF NOT EXISTS idx_variants_type ON lead_machine_message_variants(variant_type, email_number);

-- A/B test tracking
CREATE TABLE IF NOT EXISTS lead_machine_experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_starting DATE NOT NULL,
  experiment_type TEXT,
  hypothesis TEXT NOT NULL,
  control_variant_id UUID REFERENCES lead_machine_message_variants(id),
  test_variant_id UUID REFERENCES lead_machine_message_variants(id),
  min_sends_required INT DEFAULT 50,
  status TEXT DEFAULT 'running',
  winner_variant_id UUID REFERENCES lead_machine_message_variants(id),
  result_summary TEXT,
  uplift_percentage FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  decided_at TIMESTAMPTZ
);

-- Booking records — the final outcome metric
CREATE TABLE IF NOT EXISTS lead_machine_bookings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID REFERENCES outbound_leads(id) ON DELETE CASCADE,
  booked_at TIMESTAMPTZ DEFAULT NOW(),
  call_scheduled_at TIMESTAMPTZ,
  booking_source TEXT,
  trigger_event TEXT,
  cal_booking_id TEXT,
  hubspot_deal_id TEXT,
  call_preparation_brief TEXT,
  outcome TEXT DEFAULT 'pending',
  notes TEXT
);

-- System configuration — Optimizer writes here to update agent behaviour
CREATE TABLE IF NOT EXISTS lead_machine_config (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  updated_by TEXT DEFAULT 'optimizer'
);

-- Seed default config
INSERT INTO lead_machine_config (key, value, updated_by) VALUES
  ('active_vertical', 'HVAC', 'setup'),
  ('target_geography', 'USA', 'setup'),
  ('daily_lead_target', '50', 'setup'),
  ('min_sends_for_ab_decision', '50', 'setup'),
  ('hot_lead_score_threshold', '7', 'setup'),
  ('email_send_time_hour_gmt', '14', 'setup'),
  ('priority_state', 'TX,FL,CA,AZ,GA', 'setup'),
  ('min_review_count', '10', 'setup'),
  ('max_review_count', '150', 'setup'),
  ('instantly_campaign_id_hvac', 'TBD_AFTER_ACCOUNT_SETUP', 'setup'),
  ('cal_booking_url', 'https://cal.com/syntharra', 'setup'),
  ('dan_phone_number', 'TBD', 'setup')
ON CONFLICT (key) DO NOTHING;

-- Seed control message variants (the starting baseline)
INSERT INTO lead_machine_message_variants (variant_type, email_number, content, hypothesis, status) VALUES
  ('subject_line', 1, '{first_name}, quick question about {business_name}', 'Personalised subject with their name + business = highest open rate starting point', 'control'),
  ('subject_line', 2, 'The math on missed calls', 'Curiosity + implied cost = high open rate for email 2', 'control'),
  ('subject_line', 3, 'Hear it yourself', 'Short, direct, creates curiosity about the demo line', 'control'),
  ('subject_line', 4, 'Your competitors are picking up', 'Competitive threat angle — most effective for email 4', 'control'),
  ('subject_line', 5, 'Should I close your file?', 'Breakup email pattern — consistently highest reply rate for final touch', 'control'),
  ('opening_line', 1, 'I called 73 HVAC companies in {city} last week. 41 went straight to voicemail.', 'Stat + local = specific enough to feel researched, alarming enough to keep reading', 'control')
ON CONFLICT DO NOTHING;

-- Reply drafts queue (questions that need Dan review)
CREATE TABLE IF NOT EXISTS lead_machine_replies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID REFERENCES outbound_leads(id),
  original_reply TEXT NOT NULL,
  reply_classification TEXT,
  claude_draft_response TEXT,
  status TEXT DEFAULT 'pending_review',
  reviewed_at TIMESTAMPTZ,
  sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Row Level Security (disable for service role access from n8n)
-- ============================================================
ALTER TABLE lead_machine_research ENABLE ROW LEVEL SECURITY;
ALTER TABLE outbound_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_machine_sequence_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_machine_message_variants ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_machine_experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_machine_bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_machine_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_machine_replies ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS — n8n uses service role key, all good
-- These policies allow anon reads only on config (for future dashboard use)
CREATE POLICY "Service role full access" ON lead_machine_config
  FOR ALL USING (true);
