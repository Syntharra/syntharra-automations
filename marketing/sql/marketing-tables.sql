-- ============================================================
-- Syntharra Marketing DB Setup
-- Run in Supabase SQL Editor: hgheyqwnrcvwtgngqdnq.supabase.co
-- ============================================================

-- Marketing Leads (all sourced prospects)
CREATE TABLE IF NOT EXISTS marketing_leads (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  business_name TEXT NOT NULL,
  industry TEXT NOT NULL DEFAULT 'hvac',
  region TEXT,
  city TEXT,
  state TEXT,
  country TEXT DEFAULT 'USA',
  phone TEXT,
  email TEXT,
  website TEXT,
  address TEXT,
  google_place_id TEXT UNIQUE,
  rating NUMERIC(3,1),
  review_count INTEGER DEFAULT 0,
  source TEXT DEFAULT 'google_places',
  status TEXT DEFAULT 'new',
  -- Status values: new | emailed | opened | clicked | booked | unsubscribed | sequence_complete
  email_sent_at TIMESTAMPTZ,
  email_opened_at TIMESTAMPTZ,
  video_clicked_at TIMESTAMPTZ,
  demo_booked_at TIMESTAMPTZ,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Email Events (every send, open, click, bounce)
CREATE TABLE IF NOT EXISTS email_events (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  lead_id UUID REFERENCES marketing_leads(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  -- event_type values: sent | opened | clicked | replied | bounced | unsubscribed
  email_number INTEGER,
  utm_code TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Booked Demos
CREATE TABLE IF NOT EXISTS booked_demos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  lead_id UUID REFERENCES marketing_leads(id) ON DELETE CASCADE,
  booking_time TIMESTAMPTZ,
  cal_event_id TEXT,
  status TEXT DEFAULT 'scheduled',
  -- Status: scheduled | completed | no_show | cancelled
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_leads_status ON marketing_leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_industry ON marketing_leads(industry);
CREATE INDEX IF NOT EXISTS idx_leads_email_sent ON marketing_leads(email_sent_at);
CREATE INDEX IF NOT EXISTS idx_leads_city_state ON marketing_leads(city, state);
CREATE INDEX IF NOT EXISTS idx_events_lead_id ON email_events(lead_id);
CREATE INDEX IF NOT EXISTS idx_events_utm ON email_events(utm_code);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_marketing_leads_updated_at
  BEFORE UPDATE ON marketing_leads
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Unsubscribe function (call via RPC from website)
CREATE OR REPLACE FUNCTION unsubscribe_lead(p_lead_id UUID)
RETURNS void AS $$
BEGIN
  UPDATE marketing_leads SET status = 'unsubscribed' WHERE id = p_lead_id;
  INSERT INTO email_events (lead_id, event_type) VALUES (p_lead_id, 'unsubscribed');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Useful views
CREATE OR REPLACE VIEW marketing_dashboard AS
SELECT
  industry,
  COUNT(*) FILTER (WHERE status = 'new') AS new_leads,
  COUNT(*) FILTER (WHERE status = 'emailed') AS emailed,
  COUNT(*) FILTER (WHERE status = 'clicked') AS hot_leads,
  COUNT(*) FILTER (WHERE status = 'booked') AS booked,
  COUNT(*) FILTER (WHERE status = 'unsubscribed') AS unsubscribed,
  COUNT(*) AS total,
  ROUND(COUNT(*) FILTER (WHERE status IN ('clicked','booked'))::numeric / NULLIF(COUNT(*) FILTER (WHERE status != 'new'),0) * 100, 1) AS engagement_rate_pct
FROM marketing_leads
GROUP BY industry;

-- Row Level Security (optional but recommended)
ALTER TABLE marketing_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE booked_demos ENABLE ROW LEVEL SECURITY;

-- Allow service role full access (n8n uses service role key)
CREATE POLICY "Service role full access - leads" ON marketing_leads
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access - events" ON email_events
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access - demos" ON booked_demos
  FOR ALL USING (auth.role() = 'service_role');
