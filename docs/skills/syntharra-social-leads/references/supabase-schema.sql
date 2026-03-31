-- ============================================================
-- SYNTHARRA SOCIAL LEADS — SUPABASE SCHEMA
-- Run this in Supabase SQL editor
-- All tables use UUID primary keys and timestamptz
-- ============================================================

-- Content Ideas (generated weekly by Claude)
CREATE TABLE IF NOT EXISTS content_ideas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content_pillar TEXT CHECK (content_pillar IN (
    'missed_calls_cost', 'after_hours', 'admin_inefficiency',
    'ai_vs_receptionist', 'follow_up_problem', 'demo_call',
    'ad_spend_waste', 'hvac_specific'
  )),
  format_type TEXT CHECK (format_type IN (
    'faceless_video', 'static_image', 'text_post', 'carousel'
  )),
  platform TEXT DEFAULT 'all',
  vertical TEXT DEFAULT 'hvac' CHECK (vertical IN ('hvac', 'electrical', 'plumbing')),
  hook_style TEXT CHECK (hook_style IN ('stat', 'story', 'question', 'bold_claim')),
  status TEXT DEFAULT 'pending' CHECK (status IN (
    'pending', 'approved', 'scripted', 'produced', 'posted', 'skipped'
  )),
  week_of DATE,
  source TEXT DEFAULT 'ai_generated' CHECK (source IN ('ai_generated', 'manual', 'performance_loop')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Content Scripts (one per idea)
CREATE TABLE IF NOT EXISTS content_scripts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  idea_id UUID REFERENCES content_ideas(id) ON DELETE CASCADE,
  hook TEXT NOT NULL,
  body TEXT NOT NULL,
  cta TEXT NOT NULL,
  caption_raw TEXT,
  caption_facebook TEXT,
  caption_tiktok TEXT,
  caption_youtube TEXT,
  caption_instagram TEXT,
  video_type TEXT CHECK (video_type IN ('faceless_video', 'static_image', 'text_post', 'carousel')),
  blotato_video_id TEXT,
  video_url TEXT,
  thumbnail_url TEXT,
  duration_seconds INT,
  status TEXT DEFAULT 'draft' CHECK (status IN (
    'draft', 'in_production', 'ready', 'posted', 'failed'
  )),
  vertical TEXT DEFAULT 'hvac',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Per-Platform Posts (one row per platform per piece of content)
CREATE TABLE IF NOT EXISTS content_posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  script_id UUID REFERENCES content_scripts(id) ON DELETE CASCADE,
  platform TEXT NOT NULL CHECK (platform IN (
    'facebook', 'tiktok', 'youtube', 'instagram', 'linkedin'
  )),
  caption TEXT,
  hashtags TEXT,
  video_url TEXT,
  blotato_post_id TEXT,
  scheduled_at TIMESTAMPTZ,
  posted_at TIMESTAMPTZ,
  utm_source TEXT,    -- platform name
  utm_medium TEXT,    -- 'organic' or 'paid'
  utm_campaign TEXT,  -- vertical name
  utm_content TEXT,   -- this post's UUID (set after insert)
  status TEXT DEFAULT 'pending' CHECK (status IN (
    'pending', 'scheduled', 'posted', 'failed', 'boosted'
  )),
  vertical TEXT DEFAULT 'hvac',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Update utm_content to self-reference after insert
CREATE OR REPLACE FUNCTION set_utm_content()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.utm_content IS NULL THEN
    NEW.utm_content = NEW.id::TEXT;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_utm_content_trigger
  BEFORE INSERT ON content_posts
  FOR EACH ROW EXECUTE FUNCTION set_utm_content();

-- Weekly Post Performance Metrics
CREATE TABLE IF NOT EXISTS content_performance (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID REFERENCES content_posts(id) ON DELETE CASCADE,
  platform TEXT,
  views INT DEFAULT 0,
  reach INT DEFAULT 0,
  watch_time_seconds INT DEFAULT 0,
  watch_time_pct NUMERIC DEFAULT 0,  -- average % watched
  likes INT DEFAULT 0,
  comments INT DEFAULT 0,
  shares INT DEFAULT 0,
  saves INT DEFAULT 0,
  link_clicks INT DEFAULT 0,
  profile_visits INT DEFAULT 0,
  demo_page_visits INT DEFAULT 0,    -- from UTM matching
  cal_bookings INT DEFAULT 0,        -- from UTM matching
  attributed_revenue NUMERIC DEFAULT 0, -- from Stripe UTM matching
  fetched_at TIMESTAMPTZ DEFAULT NOW()
);

-- Weekly AI Pattern Analysis (output of Loop 2)
CREATE TABLE IF NOT EXISTS content_patterns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_of DATE NOT NULL,
  vertical TEXT DEFAULT 'hvac',
  winning_hook_style TEXT,
  winning_pillar TEXT,
  winning_format TEXT,
  winning_platform TEXT,
  winning_cta TEXT,
  top_post_id UUID REFERENCES content_posts(id),
  revenue_attributed_angle TEXT,     -- from Loop 5
  brief_for_next_week TEXT,          -- injected into Monday Loop 1
  raw_analysis JSONB,                -- full Claude response
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Ad Records (Phase 2)
CREATE TABLE IF NOT EXISTS content_ads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID REFERENCES content_posts(id),
  platform TEXT DEFAULT 'facebook',
  meta_ad_id TEXT,
  meta_adset_id TEXT,
  meta_campaign_id TEXT,
  daily_budget NUMERIC DEFAULT 10,
  total_spent NUMERIC DEFAULT 0,
  status TEXT DEFAULT 'active' CHECK (status IN (
    'pending', 'active', 'paused', 'scaled', 'completed', 'failed'
  )),
  -- Performance
  impressions INT DEFAULT 0,
  clicks INT DEFAULT 0,
  cpc NUMERIC,
  ctr NUMERIC,
  cpm NUMERIC,
  landing_page_views INT DEFAULT 0,
  lead_form_fills INT DEFAULT 0,
  bookings INT DEFAULT 0,
  attributed_revenue NUMERIC DEFAULT 0,
  -- Metadata
  audience_type TEXT CHECK (audience_type IN (
    'cold', 'warm_video_viewers', 'hot_website_visitors', 'lookalike'
  )),
  vertical TEXT DEFAULT 'hvac',
  days_running INT DEFAULT 0,
  last_scaled_at TIMESTAMPTZ,
  last_paused_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI Loop Decisions (audit trail for all automated decisions)
CREATE TABLE IF NOT EXISTS loop_decisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  decision_type TEXT CHECK (decision_type IN (
    'scale_ad', 'pause_ad', 'hold_ad', 'boost_organic',
    'create_similar_content', 'retarget_audience_update'
  )),
  source_post_id UUID REFERENCES content_posts(id),
  source_ad_id UUID REFERENCES content_ads(id),
  recommendation TEXT CHECK (recommendation IN ('SCALE', 'PAUSE', 'HOLD', 'BOOST', 'CREATE')),
  reasoning TEXT NOT NULL,  -- Claude's explanation
  action_taken TEXT,
  budget_before NUMERIC,
  budget_after NUMERIC,
  vertical TEXT DEFAULT 'hvac',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Email Lead Magnet Subscribers
CREATE TABLE IF NOT EXISTS lead_magnet_subscribers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  first_name TEXT,
  company_name TEXT,
  phone TEXT,
  vertical TEXT DEFAULT 'hvac',
  utm_source TEXT,
  utm_medium TEXT,
  utm_content TEXT,
  nurture_step INT DEFAULT 0,  -- 0=just subscribed, 1=day3, 2=day7
  nurture_completed BOOLEAN DEFAULT FALSE,
  booked_call BOOLEAN DEFAULT FALSE,
  became_client BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_email_sent_at TIMESTAMPTZ
);

-- ============================================================
-- INDEXES for performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_content_posts_platform ON content_posts(platform);
CREATE INDEX IF NOT EXISTS idx_content_posts_status ON content_posts(status);
CREATE INDEX IF NOT EXISTS idx_content_posts_utm_content ON content_posts(utm_content);
CREATE INDEX IF NOT EXISTS idx_content_posts_vertical ON content_posts(vertical);
CREATE INDEX IF NOT EXISTS idx_content_performance_post_id ON content_performance(post_id);
CREATE INDEX IF NOT EXISTS idx_content_ads_status ON content_ads(status);
CREATE INDEX IF NOT EXISTS idx_content_ads_post_id ON content_ads(post_id);
CREATE INDEX IF NOT EXISTS idx_loop_decisions_type ON loop_decisions(decision_type);
CREATE INDEX IF NOT EXISTS idx_content_patterns_week ON content_patterns(week_of);

-- ============================================================
-- VAULT ENTRIES TO ADD (run after schema)
-- Add these to syntharra_vault table manually
-- ============================================================
/*
INSERT INTO syntharra_vault (service_name, key_type, key_value) VALUES
  ('Blotato', 'api_key', 'YOUR_BLOTATO_API_KEY'),
  ('Blotato', 'facebook_account_id', 'YOUR_FB_PAGE_ACCOUNT_ID'),
  ('Blotato', 'youtube_account_id', 'YOUR_YT_ACCOUNT_ID'),
  ('Blotato', 'tiktok_account_id', 'YOUR_TIKTOK_ACCOUNT_ID'),
  ('Blotato', 'instagram_account_id', 'YOUR_IG_ACCOUNT_ID'),
  ('Meta', 'page_access_token', 'YOUR_META_PAGE_ACCESS_TOKEN'),
  ('Meta', 'ad_account_id', 'act_YOUR_AD_ACCOUNT_ID'),
  ('Meta', 'app_id', 'YOUR_META_APP_ID'),
  ('Meta', 'app_secret', 'YOUR_META_APP_SECRET'),
  ('Meta', 'pixel_id', 'YOUR_PIXEL_ID'),
  ('TikTok', 'access_token', 'YOUR_TIKTOK_ACCESS_TOKEN'),
  ('TikTok', 'advertiser_id', 'YOUR_TIKTOK_ADVERTISER_ID'),
  ('Spur', 'api_key', 'YOUR_SPUR_API_KEY'),
  ('Spur', 'webhook_url', 'https://n8n.syntharra.com/webhook/spur-comment-dm');
*/
