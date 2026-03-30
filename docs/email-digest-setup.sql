-- ============================================================
-- Syntharra Email Digest — Supabase Table Setup
-- Run this in Supabase SQL Editor before activating the n8n workflow
-- ============================================================

CREATE TABLE IF NOT EXISTS email_digest (
  id              bigserial PRIMARY KEY,
  digest_date     date NOT NULL,                          -- e.g. 2026-03-30
  inbox_address   text NOT NULL,                          -- e.g. support@syntharra.com
  inbox_label     text,                                   -- e.g. Support
  email_id        text,                                   -- Gmail message ID
  thread_id       text,                                   -- Gmail thread ID
  from_address    text,                                   -- Full From: header
  subject         text,                                   -- Email subject
  snippet         text,                                   -- Raw Gmail snippet
  ai_summary      text,                                   -- AI-generated one-line summary
  importance      text CHECK (importance IN ('high','medium','low')),
  category        text,                                   -- client_enquiry, sales_lead, etc.
  action_required boolean DEFAULT false,
  flag            text CHECK (flag IN ('urgent','opportunity','hire') OR flag IS NULL),
  received_at     timestamptz,
  created_at      timestamptz DEFAULT now()
);

-- Index for fast daily queries
CREATE INDEX IF NOT EXISTS email_digest_date_idx ON email_digest (digest_date DESC);
CREATE INDEX IF NOT EXISTS email_digest_inbox_idx ON email_digest (inbox_address, digest_date DESC);
CREATE INDEX IF NOT EXISTS email_digest_importance_idx ON email_digest (importance, digest_date DESC);

-- Enable RLS (Row Level Security)
ALTER TABLE email_digest ENABLE ROW LEVEL SECURITY;

-- Allow anon reads (admin dashboard uses anon key to read)
CREATE POLICY "Allow anon read email_digest"
  ON email_digest FOR SELECT
  USING (true);

-- Allow service role full access (n8n workflow writes using service role key)
CREATE POLICY "Allow service role all email_digest"
  ON email_digest FOR ALL
  USING (auth.role() = 'service_role');
