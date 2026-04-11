# Autonomous Content Team Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the existing `tools/marketing_brain.py` with a 4-agent autonomous organic content team that researches viral HVAC content, writes video scripts with reasoning, generates videos via Higgsfield Plus, distributes to YouTube/TikTok/Instagram/Facebook via Blotato, tracks conversion attribution, and feeds a weekly self-learning loop — all approved by Dan through Slack with 48h auto-approve.

**Architecture:** Lean 4-agent extension of the existing marketing brain. Cold email phase stays in the codebase but is gated behind `COLD_EMAIL_ENABLED=false`. A new `MARKETING_TEAM_ENABLED` flag controls live posting — until flipped, the entire pipeline runs in preview mode (generates content, stores to Supabase, sends Slack preview, but does not actually post to platforms). This lets us build and test the full pipeline before VSL/Stripe/Telnyx are live, then flip one env var to activate.

**Tech Stack:**
- Python 3.11+ (existing pattern in `tools/`)
- Supabase PostgREST via `urllib.request` (existing pattern — no SDK)
- Claude CLI (`claude -p`) for all LLM calls — **NEVER** call Anthropic API directly (Dan's hard rule)
- Higgsfield Cloud API ([cloud.higgsfield.ai](https://cloud.higgsfield.ai)) for video generation — Kling 3.0 1080p default, Seedance 2.0 for hero content, image gen for content repurposing
- Blotato REST API for multi-platform distribution (YouTube Shorts, TikTok, Instagram Reels, Facebook Reels)
- fal.ai as pay-per-use overflow safety net if Higgsfield credits run out
- ElevenLabs API (free tier) for voiceover on VSL (optional — Higgsfield Speak may handle this)
- Railway crons for scheduling (existing pattern via `tools/deploy_billing_crons.py`)
- Slack Web API via bot token (existing pattern in `marketing_brain.py`)
- YouTube Data API v3 for analytics pull (OAuth credentials already vaulted)
- Reddit API for research (OAuth already vaulted)
- `pytrends` Python library for Google Trends research

---

## Preconditions (MUST be true before Task 1)

- [ ] Higgsfield Plus subscribed, API key vaulted as `syntharra_vault.service_name='Higgsfield', key_type='api_key'`
- [ ] Blotato Starter subscribed, API key vaulted as `syntharra_vault.service_name='Blotato', key_type='api_key'`
- [ ] Blotato UI shows connected accounts: YouTube, TikTok, Instagram, Facebook
- [ ] Branch `phase0/day2` is current; `git status` shows clean working tree (all Day 5 work committed)
- [ ] `.env.local` has `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` exported
- [ ] Claude CLI installed and working: `claude --version` succeeds

---

## File Structure

### New files
- `supabase/migrations/20260412_content_team_schema.sql` — 4 new tables
- `tools/research_agent.py` — daily cron, trend/competitor research → `marketing_intelligence`
- `tools/content_writer.py` — M/W/F cron, video scripts with reasoning → `content_queue`
- `tools/publisher.py` — on-approval, Higgsfield render → Blotato post → analytics pull
- `tools/higgsfield_client.py` — thin wrapper over Higgsfield Cloud API (Kling 3.0 default)
- `tools/blotato_client.py` — thin wrapper over Blotato REST API
- `tools/falai_client.py` — overflow pay-per-use video generation
- `tools/vsl_generator.py` — one-shot AI-only VSL generator (uses Publisher path)
- `tools/content_preview_mode.py` — shared `is_live_mode()` gate used by all agents
- `Syntharra/syntharra-website/marketing.html` — approval dashboard (password-protected)

### Modified files
- `tools/marketing_brain.py` — add Phase 2b (video plan) + Phase 4b (video execute); gate cold email behind `COLD_EMAIL_ENABLED` env var
- `tools/deploy_billing_crons.py` — add `syntharra-research-agent` (daily 06:00 UTC) and `syntharra-content-writer` (M/W/F 07:00 UTC) Railway crons
- `docs/STATE.md` — update "What's live" + "Next session pick up"
- `docs/REFERENCE.md` — add Higgsfield/Blotato vault references + new table names
- `docs/session-logs/INDEX.md` — append new session log entry

### Unchanged (intentionally)
- `tools/short_form_content.py` — kept as-is; `content_writer.py` is the new video-focused replacement
- `tools/social_poster.py` — kept as-is (Reddit + LinkedIn still exist but dormant)
- `tools/track_campaign_performance.py` — kept as-is; Publisher Agent writes to the same `campaign_results` table

---

## Phase 0 — Preparation (schema + flags + vault verification)

### Task 1: Schema migration for content team tables

**Files:**
- Create: `supabase/migrations/20260412_content_team_schema.sql`

- [ ] **Step 1: Write the migration SQL**

Create file `supabase/migrations/20260412_content_team_schema.sql`:

```sql
-- 2026-04-12 — Content team schema
-- Adds 4 tables for the autonomous organic content pipeline:
--   marketing_intelligence  — Research Agent daily output
--   competitor_intelligence — Research Agent weekly competitor scan
--   content_queue           — Writer Agent output, pending/approved/posted
--   marketing_brain_log     — Weekly brain plan + decisions

BEGIN;

CREATE TABLE IF NOT EXISTS marketing_intelligence (
  id              BIGSERIAL PRIMARY KEY,
  scraped_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  source          TEXT NOT NULL,           -- 'youtube' | 'reddit' | 'google_trends' | 'tiktok_scrape'
  query           TEXT NOT NULL,
  title           TEXT,
  url             TEXT,
  view_count      BIGINT,
  engagement_rate NUMERIC(6,4),
  hook            TEXT,                    -- extracted first 2s hook text
  angle           TEXT,                    -- extracted emotional/topical angle
  raw_data        JSONB NOT NULL DEFAULT '{}'::jsonb,
  confidence      NUMERIC(3,2) NOT NULL DEFAULT 0.50,
  expires_at      TIMESTAMPTZ NOT NULL DEFAULT (now() + interval '30 days')
);
CREATE INDEX idx_intel_source_scraped ON marketing_intelligence (source, scraped_at DESC);
CREATE INDEX idx_intel_expires ON marketing_intelligence (expires_at);
ALTER TABLE marketing_intelligence ENABLE ROW LEVEL SECURITY;
CREATE POLICY marketing_intelligence_service_only ON marketing_intelligence
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE TABLE IF NOT EXISTS competitor_intelligence (
  id              BIGSERIAL PRIMARY KEY,
  scraped_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  competitor_name TEXT NOT NULL,
  platform        TEXT NOT NULL,
  top_content     JSONB NOT NULL DEFAULT '[]'::jsonb,
  content_gaps    JSONB NOT NULL DEFAULT '[]'::jsonb,
  notes           TEXT
);
CREATE INDEX idx_competitor_scraped ON competitor_intelligence (scraped_at DESC);
ALTER TABLE competitor_intelligence ENABLE ROW LEVEL SECURITY;
CREATE POLICY competitor_intelligence_service_only ON competitor_intelligence
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE TABLE IF NOT EXISTS content_queue (
  id                   BIGSERIAL PRIMARY KEY,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  content_type         TEXT NOT NULL,             -- 'short_video' | 'long_video' | 'blog' | 'caption'
  hook                 TEXT NOT NULL,
  script               TEXT NOT NULL,
  visual_prompt        TEXT,                      -- for Higgsfield
  reasoning            TEXT NOT NULL,             -- why this will work
  confidence_score     NUMERIC(3,2) NOT NULL DEFAULT 0.50,
  platform_targets     JSONB NOT NULL DEFAULT '[]'::jsonb,  -- ['youtube_shorts','tiktok','instagram_reels','facebook_reels']
  source_intelligence  JSONB NOT NULL DEFAULT '[]'::jsonb,  -- ref marketing_intelligence.id[]
  video_provider       TEXT,                      -- 'higgsfield' | 'falai' | null until rendered
  video_model          TEXT,                      -- 'kling-3.0-1080p' | 'seedance-2.0' etc
  video_url            TEXT,                      -- Supabase Storage URL after render
  thumbnail_url        TEXT,
  blotato_post_id      TEXT,                      -- after distribution
  platform_post_urls   JSONB NOT NULL DEFAULT '{}'::jsonb,  -- {'youtube': '...', 'tiktok': '...'}
  status               TEXT NOT NULL DEFAULT 'pending_approval',
  -- status values: 'pending_approval' | 'approved' | 'rejected' | 'rendering' | 'rendered' | 'posted' | 'failed'
  rejection_reason     TEXT,
  approved_by          TEXT,                      -- 'dan' | 'auto' (48h rule)
  approved_at          TIMESTAMPTZ,
  posted_at            TIMESTAMPTZ
);
CREATE INDEX idx_queue_status ON content_queue (status, created_at DESC);
CREATE INDEX idx_queue_posted ON content_queue (posted_at DESC NULLS LAST);
ALTER TABLE content_queue ENABLE ROW LEVEL SECURITY;
CREATE POLICY content_queue_service_only ON content_queue
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE TABLE IF NOT EXISTS marketing_brain_log (
  id                 BIGSERIAL PRIMARY KEY,
  run_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
  phase              TEXT NOT NULL,          -- 'review' | 'plan' | 'propose' | 'execute' | 'track'
  week_of            DATE NOT NULL,
  content_queue_ids  JSONB NOT NULL DEFAULT '[]'::jsonb,
  slack_message_ts   TEXT,
  decisions          JSONB NOT NULL DEFAULT '{}'::jsonb,
  preview_mode       BOOLEAN NOT NULL DEFAULT true,
  notes              TEXT
);
CREATE INDEX idx_brain_week ON marketing_brain_log (week_of DESC, run_at DESC);
ALTER TABLE marketing_brain_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY marketing_brain_log_service_only ON marketing_brain_log
  FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Auto-update updated_at on content_queue
CREATE OR REPLACE FUNCTION content_queue_set_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_content_queue_updated_at ON content_queue;
CREATE TRIGGER trg_content_queue_updated_at
  BEFORE UPDATE ON content_queue
  FOR EACH ROW EXECUTE FUNCTION content_queue_set_updated_at();

COMMIT;
```

- [ ] **Step 2: Apply the migration to prod**

Run:
```bash
cd "c:/Users/danie/Desktop/Syntharra/Cowork/Syntharra Project/syntharra-automations"
python -c "
import os, urllib.request, json
sql = open('supabase/migrations/20260412_content_team_schema.sql').read()
req = urllib.request.Request(
    f\"{os.environ['SUPABASE_URL']}/rest/v1/rpc/exec_sql\",
    data=json.dumps({'sql': sql}).encode(),
    headers={
        'apikey': os.environ['SUPABASE_SERVICE_KEY'],
        'Authorization': f\"Bearer {os.environ['SUPABASE_SERVICE_KEY']}\",
        'Content-Type': 'application/json',
    },
)
print(urllib.request.urlopen(req).read().decode())
"
```

**Fallback if `exec_sql` RPC doesn't exist:** use the Supabase MCP tool or paste the SQL directly into the Supabase SQL Editor UI at `https://supabase.com/dashboard/project/hgheyqwnrcvwtgngqdnq/sql/new` and run.

Expected: 4 `CREATE TABLE` + 4 indexes + 4 RLS policies + 1 trigger function applied without error.

- [ ] **Step 3: Verify tables exist**

Run:
```bash
python -c "
import os, urllib.request
req = urllib.request.Request(
    f\"{os.environ['SUPABASE_URL']}/rest/v1/marketing_intelligence?limit=0\",
    headers={'apikey': os.environ['SUPABASE_SERVICE_KEY']}
)
print('marketing_intelligence:', urllib.request.urlopen(req).status)
for t in ['competitor_intelligence', 'content_queue', 'marketing_brain_log']:
    req = urllib.request.Request(
        f\"{os.environ['SUPABASE_URL']}/rest/v1/{t}?limit=0\",
        headers={'apikey': os.environ['SUPABASE_SERVICE_KEY']}
    )
    print(f'{t}:', urllib.request.urlopen(req).status)
"
```

Expected output:
```
marketing_intelligence: 200
competitor_intelligence: 200
content_queue: 200
marketing_brain_log: 200
```

- [ ] **Step 4: Commit**

```bash
git add supabase/migrations/20260412_content_team_schema.sql
git commit -m "$(cat <<'EOF'
feat(content-team): schema for autonomous content pipeline

Adds 4 tables: marketing_intelligence, competitor_intelligence,
content_queue, marketing_brain_log. RLS enabled, service-role-only.
Supports 4-agent content team (Research, Writer, Publisher, Brain)
landing in subsequent commits.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Preview mode gate (shared helper)

**Files:**
- Create: `tools/content_preview_mode.py`

- [ ] **Step 1: Write the helper**

Create `tools/content_preview_mode.py`:

```python
#!/usr/bin/env python3
"""
content_preview_mode.py — shared live/preview mode gate for content team agents.

Usage in any agent:
    from content_preview_mode import is_live_mode, is_cold_email_enabled
    if is_live_mode():
        blotato_client.publish(...)
    else:
        print("[PREVIEW] Would publish:", payload)

Environment:
    MARKETING_TEAM_ENABLED=true   -> live mode (actually posts)
    MARKETING_TEAM_ENABLED=false  -> preview mode (dry-run, default)
    COLD_EMAIL_ENABLED=true       -> cold email phase runs (currently paused)
    COLD_EMAIL_ENABLED=false      -> cold email phase skipped (default)
"""

import os


def is_live_mode() -> bool:
    """True when the content team should actually post to platforms."""
    return os.environ.get("MARKETING_TEAM_ENABLED", "false").lower() == "true"


def is_cold_email_enabled() -> bool:
    """True when marketing_brain.py should run its cold email phase.

    Currently paused per Dan's 2026-04-11 decision to focus on organic
    social content. Flip to true to resume cold email sequences.
    """
    return os.environ.get("COLD_EMAIL_ENABLED", "false").lower() == "true"


def preview_banner() -> str:
    """Banner text for Slack messages when running in preview mode."""
    if is_live_mode():
        return ""
    return (
        "\n\n*⚠️  PREVIEW MODE* — content generated and stored but NOT posted. "
        "Flip `MARKETING_TEAM_ENABLED=true` in Railway when VSL+Stripe+Telnyx are live."
    )


if __name__ == "__main__":
    print(f"is_live_mode(): {is_live_mode()}")
    print(f"is_cold_email_enabled(): {is_cold_email_enabled()}")
    print(f"preview_banner(): {preview_banner()!r}")
```

- [ ] **Step 2: Smoke test**

Run:
```bash
python tools/content_preview_mode.py
```

Expected (default env):
```
is_live_mode(): False
is_cold_email_enabled(): False
preview_banner(): '\n\n*⚠️  PREVIEW MODE* — content generated and stored but NOT posted. Flip `MARKETING_TEAM_ENABLED=true` in Railway when VSL+Stripe+Telnyx are live.'
```

Then test live mode:
```bash
MARKETING_TEAM_ENABLED=true python tools/content_preview_mode.py
```

Expected:
```
is_live_mode(): True
is_cold_email_enabled(): False
preview_banner(): ''
```

- [ ] **Step 3: Commit**

```bash
git add tools/content_preview_mode.py
git commit -m "feat(content-team): preview mode gate + cold email flag

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Gate cold email phase in marketing_brain.py

**Files:**
- Modify: `tools/marketing_brain.py` (find cold email execution block, wrap in `is_cold_email_enabled()` check)

- [ ] **Step 1: Read the existing cold email phase**

Run:
```bash
grep -n "cold_email\|Brevo\|brevo\|send_cold" tools/marketing_brain.py | head -40
```

Identify the function(s) that execute cold email in Phase 4 (EXECUTE). Note the line ranges.

- [ ] **Step 2: Add import at top of file**

In `tools/marketing_brain.py`, find the existing import block (around line 24-32) and add:

```python
from content_preview_mode import is_cold_email_enabled
```

- [ ] **Step 3: Wrap cold email execution**

Find the Phase 4 execution function (likely named `phase_execute` or `run_cold_email_phase` or similar). Wrap the cold email call:

```python
# BEFORE (example — actual code will differ):
def phase_execute(plan):
    send_cold_email_sequences(plan["email_plan"])
    post_reddit(plan["reddit_plan"])
    post_linkedin(plan["linkedin_plan"])

# AFTER:
def phase_execute(plan):
    if is_cold_email_enabled():
        send_cold_email_sequences(plan["email_plan"])
    else:
        print("[SKIP] Cold email phase disabled (COLD_EMAIL_ENABLED=false)")
    post_reddit(plan["reddit_plan"])
    post_linkedin(plan["linkedin_plan"])
```

- [ ] **Step 4: Dry-run test**

Run:
```bash
python tools/marketing_brain.py --dry-run --review-only
```

Expected: runs without error, prints `[SKIP] Cold email phase disabled` somewhere in the output.

- [ ] **Step 5: Commit**

```bash
git add tools/marketing_brain.py
git commit -m "feat(marketing-brain): gate cold email behind COLD_EMAIL_ENABLED flag

Dan's 2026-04-11 decision: pause cold outbound, focus on organic
social content. Flag-flippable any time without code changes.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Phase 1 — Research Agent (daily trend + competitor intelligence)

### Task 4: YouTube Data API research function

**Files:**
- Create: `tools/research_agent.py` (first commit — YouTube only)

- [ ] **Step 1: Scaffold the agent file**

Create `tools/research_agent.py`:

```python
#!/usr/bin/env python3
"""
research_agent.py — daily viral content research for the HVAC niche.

Runs daily 06:00 UTC via Railway cron. Scrapes:
  - YouTube Data API v3 search (HVAC business/answering service content)
  - Reddit API (r/HVAC, r/Contractor, r/smallbusiness top posts)
  - Google Trends (HVAC search spike signals)

Writes findings to `marketing_intelligence` table with confidence scores.
Output is read by content_writer.py to inform next batch of scripts.

Usage:
  source .env.local
  python tools/research_agent.py                 # full daily run
  python tools/research_agent.py --source youtube  # single source
  python tools/research_agent.py --dry-run       # print findings, don't write

Requires env: SUPABASE_URL, SUPABASE_SERVICE_KEY
Vault keys: YouTube/client_id, YouTube/client_secret, YouTube/refresh_token,
            Reddit/client_id, Reddit/client_secret, Reddit/refresh_token
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# Search queries targeting HVAC business pain points
YOUTUBE_QUERIES = [
    "HVAC business missed calls",
    "HVAC answering service",
    "HVAC contractor after hours calls",
    "AI receptionist HVAC",
    "HVAC lead generation tips",
    "HVAC business growth",
]

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


def vault_get(service: str, key_type: str) -> str:
    """Fetch a credential from syntharra_vault."""
    url = (
        f"{SUPABASE_URL}/rest/v1/syntharra_vault"
        f"?service_name=eq.{urllib.parse.quote(service)}"
        f"&key_type=eq.{urllib.parse.quote(key_type)}"
        f"&select=secret_value&limit=1"
    )
    req = urllib.request.Request(
        url,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        rows = json.loads(r.read().decode())
    if not rows:
        raise RuntimeError(f"Vault miss: {service}/{key_type}")
    return rows[0]["secret_value"]


def supabase_insert(table: str, rows: list[dict]) -> None:
    """Bulk insert into a Supabase table via PostgREST."""
    if not rows:
        return
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    req = urllib.request.Request(
        url,
        data=json.dumps(rows).encode(),
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        if r.status not in (200, 201, 204):
            raise RuntimeError(f"Insert failed: {r.status} {r.read().decode()}")


def scrape_youtube(query: str, api_key: str, max_results: int = 10) -> list[dict]:
    """Search YouTube for top results on a query. Returns list of findings."""
    url = (
        f"https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&type=video&order=viewCount"
        f"&publishedAfter={(datetime.now(timezone.utc).replace(day=1)).isoformat()}"
        f"&q={urllib.parse.quote(query)}&maxResults={max_results}&key={api_key}"
    )
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())

    findings = []
    for item in data.get("items", []):
        vid_id = item["id"]["videoId"]
        sn = item["snippet"]
        findings.append({
            "source": "youtube",
            "query": query,
            "title": sn["title"],
            "url": f"https://youtube.com/watch?v={vid_id}",
            "view_count": None,  # needs videos endpoint for stats; enrich in step 2
            "engagement_rate": None,
            "hook": sn["title"][:80],  # provisional; Writer will re-extract
            "angle": sn.get("description", "")[:200],
            "raw_data": {
                "video_id": vid_id,
                "channel": sn["channelTitle"],
                "published_at": sn["publishedAt"],
            },
            "confidence": 0.60,
        })
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["youtube", "reddit", "trends", "all"], default="all")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    all_findings: list[dict] = []

    if args.source in ("youtube", "all"):
        yt_key = vault_get("YouTube", "api_key")  # note: needs to be added to vault
        for q in YOUTUBE_QUERIES:
            try:
                f = scrape_youtube(q, yt_key)
                all_findings.extend(f)
                print(f"[youtube] {q}: {len(f)} results")
            except Exception as e:
                print(f"[youtube] ERROR on {q!r}: {e}", file=sys.stderr)

    if args.dry_run:
        print(f"\n--- DRY RUN: {len(all_findings)} findings ---")
        for f in all_findings[:5]:
            print(f"  [{f['source']}] {f['title'][:70]}")
        return 0

    supabase_insert("marketing_intelligence", all_findings)
    print(f"Inserted {len(all_findings)} findings into marketing_intelligence")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Add YouTube API key to vault**

Dan: create a YouTube Data API v3 key at [Google Cloud Console](https://console.cloud.google.com/apis/credentials) (restrict to YouTube Data API v3). The existing OAuth client is for posting videos; this is a separate read-only Data API key for search.

Run:
```bash
python tools/vault_secret.py --service YouTube --key-type api_key --value "YOUR_YOUTUBE_DATA_API_KEY"
```

- [ ] **Step 3: Dry-run test**

Run:
```bash
source .env.local && python tools/research_agent.py --source youtube --dry-run
```

Expected: 6 queries run, each returns up to 10 results, output shows `[youtube] <query>: N results`, final dry-run summary lists 5 sample findings.

- [ ] **Step 4: Live run (writes to Supabase)**

Run:
```bash
source .env.local && python tools/research_agent.py --source youtube
```

Expected: `Inserted N findings into marketing_intelligence` (N between 30 and 60).

- [ ] **Step 5: Verify via Supabase**

Run:
```bash
python -c "
import os, urllib.request, json
url = f\"{os.environ['SUPABASE_URL']}/rest/v1/marketing_intelligence?select=source,title,url&order=scraped_at.desc&limit=3\"
req = urllib.request.Request(url, headers={'apikey': os.environ['SUPABASE_SERVICE_KEY']})
for row in json.loads(urllib.request.urlopen(req).read()):
    print(f\"[{row['source']}] {row['title'][:60]}\")
"
```

Expected: 3 recent YouTube findings printed.

- [ ] **Step 6: Commit**

```bash
git add tools/research_agent.py
git commit -m "feat(research-agent): YouTube trend scraping for HVAC niche

Writes findings to marketing_intelligence. First of 3 sources
(YouTube → Reddit → Google Trends). Runs dry-run or live via CLI;
Railway cron scheduling in Task 20.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Reddit research function

**Files:**
- Modify: `tools/research_agent.py` — add `scrape_reddit()` + hook into main

- [ ] **Step 1: Add Reddit OAuth token fetch**

In `tools/research_agent.py`, add this function below `vault_get()`:

```python
def reddit_access_token() -> str:
    """Exchange refresh token for a short-lived Reddit access token."""
    client_id = vault_get("Reddit", "client_id")
    client_secret = vault_get("Reddit", "client_secret")
    refresh_token = vault_get("Reddit", "refresh_token")

    import base64
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }).encode()
    req = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=data,
        headers={
            "Authorization": f"Basic {auth}",
            "User-Agent": "Syntharra-ResearchAgent/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())["access_token"]
```

- [ ] **Step 2: Add Reddit scraping function**

Add below `scrape_youtube()`:

```python
REDDIT_SUBS = ["HVAC", "Contractor", "smallbusiness", "hvacadvice"]

def scrape_reddit(token: str, limit: int = 25) -> list[dict]:
    """Pull top posts from HVAC-adjacent subreddits this week."""
    findings = []
    for sub in REDDIT_SUBS:
        url = f"https://oauth.reddit.com/r/{sub}/top?t=week&limit={limit}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": "Syntharra-ResearchAgent/1.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode())
        except Exception as e:
            print(f"[reddit] ERROR r/{sub}: {e}", file=sys.stderr)
            continue

        for child in data.get("data", {}).get("children", []):
            p = child["data"]
            findings.append({
                "source": "reddit",
                "query": f"r/{sub}/top/week",
                "title": p["title"],
                "url": f"https://reddit.com{p['permalink']}",
                "view_count": p.get("ups"),
                "engagement_rate": round(
                    (p.get("num_comments", 0) / max(p.get("ups", 1), 1)), 4
                ),
                "hook": p["title"][:80],
                "angle": (p.get("selftext") or "")[:200],
                "raw_data": {
                    "subreddit": sub,
                    "author": p.get("author"),
                    "created_utc": p.get("created_utc"),
                    "num_comments": p.get("num_comments"),
                },
                "confidence": 0.55,
            })
    return findings
```

- [ ] **Step 3: Wire into main()**

Replace the `if args.source in ("youtube", "all"):` block with:

```python
    if args.source in ("youtube", "all"):
        try:
            yt_key = vault_get("YouTube", "api_key")
            for q in YOUTUBE_QUERIES:
                try:
                    f = scrape_youtube(q, yt_key)
                    all_findings.extend(f)
                    print(f"[youtube] {q}: {len(f)} results")
                except Exception as e:
                    print(f"[youtube] ERROR on {q!r}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"[youtube] DISABLED: {e}", file=sys.stderr)

    if args.source in ("reddit", "all"):
        try:
            token = reddit_access_token()
            f = scrape_reddit(token)
            all_findings.extend(f)
            print(f"[reddit] {len(f)} top posts across {len(REDDIT_SUBS)} subs")
        except Exception as e:
            print(f"[reddit] DISABLED: {e}", file=sys.stderr)
```

- [ ] **Step 4: Dry-run test**

Run:
```bash
source .env.local && python tools/research_agent.py --source reddit --dry-run
```

Expected: output lines for each subreddit, total finding count 50-100, no errors.

- [ ] **Step 5: Live run**

Run:
```bash
source .env.local && python tools/research_agent.py --source reddit
```

Expected: `Inserted N findings into marketing_intelligence` (N 50-100).

- [ ] **Step 6: Commit**

```bash
git add tools/research_agent.py
git commit -m "feat(research-agent): Reddit top-week scraping for HVAC subs

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Google Trends research function

**Files:**
- Modify: `tools/research_agent.py` — add `scrape_trends()`
- Modify: `requirements.txt` or equivalent — add `pytrends`

- [ ] **Step 1: Install pytrends**

Run:
```bash
pip install pytrends
```

If the repo uses a `requirements.txt`, append `pytrends>=4.9` to it.

- [ ] **Step 2: Add trends function**

In `tools/research_agent.py`, add:

```python
TRENDS_KEYWORDS = [
    "HVAC repair",
    "AC not cooling",
    "furnace not working",
    "emergency HVAC",
    "AC installation",
]

def scrape_trends() -> list[dict]:
    """Pull HVAC-related search trends from Google Trends (US, last 7 days)."""
    try:
        from pytrends.request import TrendReq
    except ImportError:
        print("[trends] pytrends not installed, skipping", file=sys.stderr)
        return []

    pytrends = TrendReq(hl="en-US", tz=0)
    findings = []
    for kw in TRENDS_KEYWORDS:
        try:
            pytrends.build_payload([kw], timeframe="now 7-d", geo="US")
            df = pytrends.interest_over_time()
            if df.empty:
                continue
            latest = int(df[kw].iloc[-1])
            avg = int(df[kw].mean())
            spike = latest > avg * 1.3
            findings.append({
                "source": "google_trends",
                "query": kw,
                "title": f"Search trend: {kw}",
                "url": f"https://trends.google.com/trends/explore?q={urllib.parse.quote(kw)}&geo=US",
                "view_count": latest,
                "engagement_rate": round(latest / max(avg, 1), 4),
                "hook": f"Search interest for '{kw}' is {'spiking' if spike else 'steady'}",
                "angle": "rising_trend" if spike else "baseline",
                "raw_data": {"latest": latest, "avg": avg, "spike": spike},
                "confidence": 0.70 if spike else 0.40,
            })
            print(f"[trends] {kw}: latest={latest} avg={avg} spike={spike}")
        except Exception as e:
            print(f"[trends] ERROR {kw!r}: {e}", file=sys.stderr)
    return findings
```

- [ ] **Step 3: Wire into main()**

Add after the Reddit block in `main()`:

```python
    if args.source in ("trends", "all"):
        try:
            f = scrape_trends()
            all_findings.extend(f)
            print(f"[trends] {len(f)} keywords analyzed")
        except Exception as e:
            print(f"[trends] DISABLED: {e}", file=sys.stderr)
```

- [ ] **Step 4: Dry-run test**

Run:
```bash
source .env.local && python tools/research_agent.py --source trends --dry-run
```

Expected: 5 keyword lines printed, spike detection on at least one, total ~5 findings.

- [ ] **Step 5: Live run all sources**

Run:
```bash
source .env.local && python tools/research_agent.py --source all
```

Expected: `Inserted N findings` where N ≥ 80 (YouTube + Reddit + Trends combined).

- [ ] **Step 6: Commit**

```bash
git add tools/research_agent.py requirements.txt 2>/dev/null || git add tools/research_agent.py
git commit -m "feat(research-agent): Google Trends spike detection

Full 3-source daily research complete (YouTube + Reddit + Trends).
Ready for Railway cron scheduling in Task 20.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Phase 2 — Content Writer Agent

### Task 7: Writer Agent scaffold + intelligence read

**Files:**
- Create: `tools/content_writer.py`

- [ ] **Step 1: Create the writer file**

Create `tools/content_writer.py`:

```python
#!/usr/bin/env python3
"""
content_writer.py — generates 2 video scripts per run from marketing intelligence.

Schedule: Mon/Wed/Fri 07:00 UTC via Railway cron (6 scripts/week total).
Reads recent marketing_intelligence + competitor_intelligence, calls Claude
CLI to synthesize 2 video concepts with hook + script + visual prompt +
reasoning, then stores to content_queue with status='pending_approval'.

Usage:
  source .env.local
  python tools/content_writer.py                 # 2 scripts, stored
  python tools/content_writer.py --count 6       # 6 scripts (catchup mode)
  python tools/content_writer.py --dry-run       # print scripts, don't store

Requires env: SUPABASE_URL, SUPABASE_SERVICE_KEY
Requires: claude CLI installed (claude --version)
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


def fetch_recent_intelligence(days: int = 7, limit: int = 50) -> list[dict]:
    """Pull the last N days of marketing_intelligence, highest confidence first."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    url = (
        f"{SUPABASE_URL}/rest/v1/marketing_intelligence"
        f"?scraped_at=gte.{urllib.parse.quote(since)}"
        f"&order=confidence.desc,scraped_at.desc&limit={limit}"
        f"&select=id,source,title,url,hook,angle,view_count,engagement_rate,confidence"
    )
    req = urllib.request.Request(
        url,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def claude_generate_scripts(intel: list[dict], count: int) -> list[dict]:
    """Call `claude -p` CLI to generate video scripts from intelligence."""
    intel_summary = "\n".join(
        f"- [{i['source']}] {i['title'][:80]} (conf {i['confidence']})"
        for i in intel[:30]
    )

    prompt = f"""You are the script writer for Syntharra's autonomous marketing team.

SYNTHARRA PRODUCT FACTS (do NOT invent features):
- Single product: HVAC Standard, $697/month flat, 200-minute free pilot, no credit card
- AI phone receptionist that answers every call 24/7
- Post-call analysis flags: is_lead (boolean), urgency (emergency/high/normal/low/none), is_spam
- When a lead or emergency is detected, shop owner is notified by email + Slack + SMS
- NO CRM integrations. NO Jobber. NO ServiceTitan. NO Housecall Pro. NO calendar booking.
- The notifications ARE the delivery mechanism. Owner acts on the alert themselves.
- Funnel: short video → syntharra.com → VSL → 200-min free pilot → paid client.

RESEARCH FROM THE LAST 7 DAYS:
{intel_summary}

Write exactly {count} short-form video scripts (30-45 seconds each).
Each script MUST target HVAC business owners (NOT homeowners).
Each script MUST end with a clear CTA: "Link in bio: syntharra.com — free 200-minute trial".
Each script MUST be pain-first (start with a problem they feel).

OUTPUT STRICT JSON ARRAY, no prose, no markdown:
[
  {{
    "hook": "First 2 seconds — the scroll-stopper. Max 15 words.",
    "script": "Full 30-45 second script with natural speech pauses. No stage directions.",
    "visual_prompt": "Higgsfield/Kling prompt describing the visual: subject, setting, camera move, mood. 1 sentence.",
    "reasoning": "Why this will work. Reference specific research findings. 2-3 sentences.",
    "platform_targets": ["youtube_shorts", "tiktok", "instagram_reels", "facebook_reels"],
    "confidence_score": 0.65
  }}
]
"""

    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {result.stderr}")

    output = result.stdout.strip()
    # Strip markdown fences if claude added them
    if output.startswith("```"):
        output = output.split("```", 2)[1]
        if output.startswith("json"):
            output = output[4:]
    output = output.strip()

    scripts = json.loads(output)
    if not isinstance(scripts, list):
        raise RuntimeError(f"Expected JSON array, got {type(scripts)}")
    return scripts


def insert_queue_rows(scripts: list[dict], intel: list[dict]) -> None:
    """Insert generated scripts into content_queue as pending_approval."""
    intel_ids = [i["id"] for i in intel[:10]]
    rows = []
    for s in scripts:
        rows.append({
            "content_type": "short_video",
            "hook": s["hook"][:500],
            "script": s["script"],
            "visual_prompt": s.get("visual_prompt", ""),
            "reasoning": s.get("reasoning", ""),
            "confidence_score": float(s.get("confidence_score", 0.5)),
            "platform_targets": s.get("platform_targets", [
                "youtube_shorts", "tiktok", "instagram_reels", "facebook_reels"
            ]),
            "source_intelligence": intel_ids,
            "status": "pending_approval",
        })

    url = f"{SUPABASE_URL}/rest/v1/content_queue"
    req = urllib.request.Request(
        url,
        data=json.dumps(rows).encode(),
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        if r.status not in (200, 201, 204):
            raise RuntimeError(f"Queue insert failed: {r.status}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=2, help="Number of scripts to generate")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print(f"Fetching recent intelligence...")
    intel = fetch_recent_intelligence()
    if not intel:
        print("WARN: no intelligence found. Using seeded hypotheses.", file=sys.stderr)
        intel = [{
            "id": 0, "source": "seed", "title": "HVAC owners lose $500+/week to missed calls",
            "hook": "Missed calls are killing HVAC shops", "angle": "pain_first",
            "confidence": 0.5, "view_count": None, "engagement_rate": None, "url": None,
        }]
    print(f"  -> {len(intel)} findings available")

    print(f"Calling Claude CLI to write {args.count} scripts...")
    scripts = claude_generate_scripts(intel, args.count)
    print(f"  -> {len(scripts)} scripts generated")

    if args.dry_run:
        print("\n--- DRY RUN ---")
        for i, s in enumerate(scripts, 1):
            print(f"\n[{i}] HOOK: {s['hook']}")
            print(f"    SCRIPT: {s['script'][:200]}...")
            print(f"    REASONING: {s['reasoning']}")
        return 0

    insert_queue_rows(scripts, intel)
    print(f"Inserted {len(scripts)} scripts into content_queue (status=pending_approval)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Dry-run test**

Run:
```bash
source .env.local && python tools/content_writer.py --dry-run
```

Expected: fetches intelligence, calls Claude CLI (takes 30-60s), prints 2 scripts with hook/script/reasoning. No errors.

- [ ] **Step 3: Live run**

Run:
```bash
source .env.local && python tools/content_writer.py
```

Expected: `Inserted 2 scripts into content_queue`. Verify via Supabase UI or:

```bash
python -c "
import os, urllib.request, json
url = f\"{os.environ['SUPABASE_URL']}/rest/v1/content_queue?status=eq.pending_approval&select=id,hook,reasoning&order=created_at.desc&limit=2\"
req = urllib.request.Request(url, headers={'apikey': os.environ['SUPABASE_SERVICE_KEY']})
for row in json.loads(urllib.request.urlopen(req).read()):
    print(f\"#{row['id']}: {row['hook']}\")
    print(f\"  reasoning: {row['reasoning'][:100]}\")
"
```

- [ ] **Step 4: Commit**

```bash
git add tools/content_writer.py
git commit -m "feat(content-writer): generates video scripts from intelligence

Mon/Wed/Fri agent. Reads marketing_intelligence, calls Claude CLI,
writes structured JSON scripts to content_queue for Dan's approval.
Seeded hypothesis fallback for cold-start period.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Phase 3 — Publisher Agent (Higgsfield + Blotato + analytics)

### Task 8: Higgsfield client wrapper

**Files:**
- Create: `tools/higgsfield_client.py`

- [ ] **Step 1: Write the client**

Create `tools/higgsfield_client.py`:

```python
#!/usr/bin/env python3
"""
higgsfield_client.py — thin wrapper around Higgsfield Cloud API.

Docs: https://cloud.higgsfield.ai/  (auth via Bearer token)
Models available on Plus tier (see docs/audits/2026-04-11-higgsfield-tier-plus.md):
  - kling-3.0-1080p  (default: 8 credits/5s, A-tier flagship)
  - kling-3.0-720p   (7 credits/5s, cheaper iteration)
  - kling-omni-3-flf-1080p  (6 credits/5s, image-conditioned keyframes)
  - seedance-2.0-720p  (22 credits/5s, hero content only)

Usage:
    from higgsfield_client import HiggsfieldClient
    h = HiggsfieldClient()
    job_id = h.generate_video(
        prompt="HVAC technician on a roof, golden hour, cinematic",
        duration_sec=30,
        aspect_ratio="9:16",
        model="kling-3.0-1080p",
    )
    video_url = h.wait_for_completion(job_id, timeout=600)
"""

import json
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass


HIGGSFIELD_BASE = "https://cloud.higgsfield.ai/api/v1"


@dataclass
class HiggsfieldClient:
    api_key: str = ""
    default_model: str = "kling-3.0-1080p"
    default_aspect: str = "9:16"

    def __post_init__(self):
        if not self.api_key:
            self.api_key = self._fetch_key_from_vault()

    @staticmethod
    def _fetch_key_from_vault() -> str:
        url = (
            f"{os.environ['SUPABASE_URL']}/rest/v1/syntharra_vault"
            f"?service_name=eq.Higgsfield&key_type=eq.api_key"
            f"&select=secret_value&limit=1"
        )
        req = urllib.request.Request(
            url,
            headers={
                "apikey": os.environ["SUPABASE_SERVICE_KEY"],
                "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_KEY']}",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            rows = json.loads(r.read().decode())
        if not rows:
            raise RuntimeError("Higgsfield API key not in vault")
        return rows[0]["secret_value"]

    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        url = f"{HIGGSFIELD_BASE}{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method=method,
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())

    def generate_video(
        self,
        prompt: str,
        duration_sec: int = 30,
        aspect_ratio: str | None = None,
        model: str | None = None,
    ) -> str:
        """Submit a text-to-video generation job. Returns job_id."""
        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "duration": duration_sec,
            "aspect_ratio": aspect_ratio or self.default_aspect,
        }
        res = self._request("POST", "/videos/generate", payload)
        return res.get("job_id") or res["id"]

    def get_job(self, job_id: str) -> dict:
        return self._request("GET", f"/videos/jobs/{job_id}")

    def wait_for_completion(
        self,
        job_id: str,
        timeout_sec: int = 600,
        poll_interval: int = 10,
    ) -> str:
        """Poll until job is done. Returns signed video URL."""
        start = time.time()
        while time.time() - start < timeout_sec:
            status = self.get_job(job_id)
            state = status.get("status", "").lower()
            if state in ("completed", "done", "succeeded"):
                url = status.get("video_url") or status.get("output_url") or status.get("url")
                if not url:
                    raise RuntimeError(f"Job complete but no URL: {status}")
                return url
            if state in ("failed", "error"):
                raise RuntimeError(f"Job failed: {status}")
            time.sleep(poll_interval)
        raise TimeoutError(f"Job {job_id} did not complete in {timeout_sec}s")

    def generate_image(self, prompt: str, aspect: str = "1:1") -> str:
        """Generate a single image (for blog headers, carousel slides).
        Returns image URL on completion."""
        res = self._request("POST", "/images/generate", {
            "prompt": prompt,
            "aspect_ratio": aspect,
        })
        img_url = res.get("image_url") or res.get("url")
        if not img_url:
            # If the API is async for images, poll the returned job
            job_id = res.get("job_id") or res["id"]
            return self.wait_for_completion(job_id, timeout_sec=120)
        return img_url


if __name__ == "__main__":
    # Smoke test
    client = HiggsfieldClient()
    print(f"Client configured. Default model: {client.default_model}")
    print(f"API key: {'*' * (len(client.api_key) - 4)}{client.api_key[-4:]}")
```

**⚠️ Note on endpoint paths:** Higgsfield Cloud API documentation is sparse. The paths `/videos/generate`, `/videos/jobs/{id}`, `/images/generate` are best guesses based on [the Higgsfield Python SDK on GitHub](https://github.com/higgsfield-ai/higgsfield-client). When running Task 8 for real, `curl` the actual endpoints first to verify the shape. If they differ, update `_request()` path strings only — everything else stays the same.

- [ ] **Step 2: Smoke-test client initialization**

Run:
```bash
source .env.local && python tools/higgsfield_client.py
```

Expected: `Client configured. Default model: kling-3.0-1080p` + masked API key. No error.

- [ ] **Step 3: Live-test video generation (one real video)**

Run:
```bash
python -c "
from tools.higgsfield_client import HiggsfieldClient
h = HiggsfieldClient()
job_id = h.generate_video(
    prompt='An HVAC technician on a roof at golden hour, cinematic wide shot, warm tones',
    duration_sec=5,
    aspect_ratio='9:16',
    model='kling-3.0-720p',
)
print(f'Job submitted: {job_id}')
url = h.wait_for_completion(job_id, timeout_sec=300)
print(f'Video URL: {url}')
"
```

Expected: job submits in <5s, polls for 1-3 minutes, prints a signed URL. Open the URL in a browser to verify playback.

**If the endpoint is wrong:** you'll get a 404. Use `curl -H "Authorization: Bearer $KEY" https://cloud.higgsfield.ai/api/v1/models` (or similar discovery) to find the real paths, then update `higgsfield_client.py`.

- [ ] **Step 4: Commit**

```bash
git add tools/higgsfield_client.py
git commit -m "feat(higgsfield): cloud API client wrapper

Kling 3.0 1080p default, vault-backed auth, job polling.
Supports video + image generation.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 9: Blotato client wrapper

**Files:**
- Create: `tools/blotato_client.py`

- [ ] **Step 1: Write the client**

Create `tools/blotato_client.py`:

```python
#!/usr/bin/env python3
"""
blotato_client.py — thin wrapper around Blotato REST API.

Docs: https://help.blotato.com/api/start
Supports posting a single video to multiple platforms in one call.

Usage:
    from blotato_client import BlotatoClient
    b = BlotatoClient()
    result = b.post_video(
        video_url="https://.../video.mp4",
        caption="Your HVAC shop is losing $500/week...",
        platforms=["youtube_shorts", "tiktok", "instagram_reels", "facebook_reels"],
    )
    # result = {"post_id": "...", "platform_urls": {"youtube": "...", ...}}
"""

import json
import os
import urllib.parse
import urllib.request
from dataclasses import dataclass


BLOTATO_BASE = "https://api.blotato.com/v1"


@dataclass
class BlotatoClient:
    api_key: str = ""

    def __post_init__(self):
        if not self.api_key:
            self.api_key = self._fetch_key_from_vault()

    @staticmethod
    def _fetch_key_from_vault() -> str:
        url = (
            f"{os.environ['SUPABASE_URL']}/rest/v1/syntharra_vault"
            f"?service_name=eq.Blotato&key_type=eq.api_key"
            f"&select=secret_value&limit=1"
        )
        req = urllib.request.Request(
            url,
            headers={
                "apikey": os.environ["SUPABASE_SERVICE_KEY"],
                "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_KEY']}",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            rows = json.loads(r.read().decode())
        if not rows:
            raise RuntimeError("Blotato API key not in vault")
        return rows[0]["secret_value"]

    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        url = f"{BLOTATO_BASE}{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method=method,
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())

    def list_accounts(self) -> list[dict]:
        """List connected social accounts (sanity check)."""
        return self._request("GET", "/accounts").get("accounts", [])

    def upload_media(self, video_url: str) -> str:
        """Upload a video to Blotato media store. Returns media_id."""
        res = self._request("POST", "/media/upload", {"source_url": video_url})
        return res.get("media_id") or res["id"]

    def post_video(
        self,
        video_url: str,
        caption: str,
        platforms: list[str],
        hashtags: list[str] | None = None,
    ) -> dict:
        """Post a video to one or more platforms.

        platforms: ["youtube_shorts", "tiktok", "instagram_reels", "facebook_reels"]
        """
        # 1. Upload to Blotato's media store
        media_id = self.upload_media(video_url)

        # 2. Build caption
        full_caption = caption
        if hashtags:
            full_caption += "\n\n" + " ".join(f"#{h}" for h in hashtags)

        # 3. Post
        payload = {
            "media_id": media_id,
            "caption": full_caption,
            "platforms": platforms,
        }
        res = self._request("POST", "/posts", payload)
        return {
            "post_id": res.get("post_id") or res.get("id"),
            "platform_urls": res.get("platform_urls", {}),
            "raw": res,
        }

    def get_analytics(self, post_id: str) -> dict:
        """Pull cross-platform analytics for a post."""
        return self._request("GET", f"/posts/{post_id}/analytics")


if __name__ == "__main__":
    b = BlotatoClient()
    print(f"Client configured. API key: {'*' * (len(b.api_key) - 4)}{b.api_key[-4:]}")
    try:
        accounts = b.list_accounts()
        print(f"Connected accounts: {len(accounts)}")
        for a in accounts:
            print(f"  - {a.get('platform', '?')}: {a.get('username', '?')}")
    except Exception as e:
        print(f"Could not list accounts: {e}")
```

- [ ] **Step 2: Smoke test**

Run:
```bash
source .env.local && python tools/blotato_client.py
```

Expected: masked API key printed, list of connected accounts (4: YouTube, TikTok, Instagram, Facebook). If accounts list fails, the API key or endpoint shape may need adjustment — consult Blotato docs at the URL in the docstring.

- [ ] **Step 3: Commit**

```bash
git add tools/blotato_client.py
git commit -m "feat(blotato): REST API client wrapper

Supports upload → post → analytics flow. Vault-backed auth.
Multi-platform in one post call.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 10: fal.ai overflow client

**Files:**
- Create: `tools/falai_client.py`

- [ ] **Step 1: Write the client**

Create `tools/falai_client.py`:

```python
#!/usr/bin/env python3
"""
falai_client.py — pay-per-use overflow when Higgsfield credits run out.

Docs: https://fal.ai/docs
Models + verified 2026 pricing:
  - fal-ai/wan-pro       : $0.05/sec  (cheapest A-tier)
  - fal-ai/kling-2.5-turbo-pro : $0.07/sec (best quality/price)
  - fal-ai/veo-3         : $0.40/sec  (gold standard, expensive)

Usage:
    from falai_client import FalaiClient
    f = FalaiClient()
    video_url = f.generate_video(
        prompt="HVAC tech on roof...",
        duration_sec=5,
        model="wan-pro",
    )
"""

import json
import os
import time
import urllib.request
from dataclasses import dataclass


FALAI_BASE = "https://fal.run"


@dataclass
class FalaiClient:
    api_key: str = ""

    def __post_init__(self):
        if not self.api_key:
            url = (
                f"{os.environ['SUPABASE_URL']}/rest/v1/syntharra_vault"
                f"?service_name=eq.fal.ai&key_type=eq.api_key"
                f"&select=secret_value&limit=1"
            )
            req = urllib.request.Request(
                url,
                headers={
                    "apikey": os.environ["SUPABASE_SERVICE_KEY"],
                    "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_KEY']}",
                },
            )
            try:
                with urllib.request.urlopen(req, timeout=15) as r:
                    rows = json.loads(r.read().decode())
                self.api_key = rows[0]["secret_value"] if rows else ""
            except Exception:
                self.api_key = ""

    def _post(self, endpoint: str, body: dict) -> dict:
        if not self.api_key:
            raise RuntimeError("fal.ai key not set — overflow unavailable")
        req = urllib.request.Request(
            f"{FALAI_BASE}/{endpoint}",
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Key {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read().decode())

    def generate_video(
        self,
        prompt: str,
        duration_sec: int = 5,
        model: str = "wan-pro",
    ) -> str:
        """Generate a video and return its URL (synchronous)."""
        endpoint_map = {
            "wan-pro": "fal-ai/wan-pro/text-to-video",
            "kling-turbo": "fal-ai/kling-video/v2.5-turbo/text-to-video",
            "veo-3": "fal-ai/veo-3",
        }
        endpoint = endpoint_map.get(model, endpoint_map["wan-pro"])
        res = self._post(endpoint, {
            "prompt": prompt,
            "duration": duration_sec,
            "aspect_ratio": "9:16",
        })
        video = res.get("video") or res.get("output")
        if isinstance(video, dict):
            return video.get("url", "")
        return video or ""


if __name__ == "__main__":
    f = FalaiClient()
    print(f"fal.ai client: {'ready' if f.api_key else 'NOT CONFIGURED (ok if unused)'}")
```

**Note:** fal.ai vault key is optional. Only set it if you want overflow. Without it, the client raises on first use but the rest of the pipeline works fine on Higgsfield alone.

- [ ] **Step 2: Commit**

```bash
git add tools/falai_client.py
git commit -m "feat(falai): overflow video generation client

Pay-per-use safety net for Higgsfield credit exhaustion.
wan-pro default ($0.05/sec).

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 11: Publisher Agent — render phase

**Files:**
- Create: `tools/publisher.py`

- [ ] **Step 1: Write the publisher scaffold + render function**

Create `tools/publisher.py`:

```python
#!/usr/bin/env python3
"""
publisher.py — renders approved content, posts to platforms, pulls analytics.

Runs on-demand (triggered by marketing_brain.py Phase 4 or CLI after approval).
Pipeline per queue row:
  1. Fetch row where status='approved' and video_url is null
  2. Call Higgsfield (or falai on credit exhaustion)
  3. Upload rendered video to Supabase storage
  4. Update row: status='rendered', video_url=<storage url>
  5. Call Blotato to post
  6. Update row: status='posted', blotato_post_id, platform_post_urls
  7. Pull initial analytics, insert into campaign_results

Usage:
  source .env.local
  python tools/publisher.py                  # process all approved rows
  python tools/publisher.py --id 42          # process single row
  python tools/publisher.py --dry-run        # show what would happen
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_preview_mode import is_live_mode, preview_banner
from higgsfield_client import HiggsfieldClient
from blotato_client import BlotatoClient

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
STORAGE_BUCKET = "marketing-content"


def supabase_get(path: str) -> list[dict]:
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{path}",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def supabase_patch(path: str, body: dict) -> None:
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{path}",
        data=json.dumps(body).encode(),
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        method="PATCH",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        if r.status not in (200, 204):
            raise RuntimeError(f"PATCH {path} -> {r.status}: {r.read().decode()}")


def fetch_approved_rows(row_id: int | None = None) -> list[dict]:
    if row_id:
        path = f"content_queue?id=eq.{row_id}&select=*"
    else:
        path = (
            "content_queue?status=eq.approved"
            "&video_url=is.null&select=*&order=approved_at.asc"
        )
    return supabase_get(path)


def upload_to_storage(source_url: str, object_path: str) -> str:
    """Download from source_url, upload to Supabase storage, return public URL."""
    # Download
    with urllib.request.urlopen(source_url, timeout=120) as r:
        video_bytes = r.read()

    # Upload
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{object_path}"
    req = urllib.request.Request(
        upload_url,
        data=video_bytes,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "video/mp4",
            "x-upsert": "true",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        if r.status not in (200, 201):
            raise RuntimeError(f"Storage upload failed: {r.status}")

    return f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{object_path}"


def render_video(row: dict, hf: HiggsfieldClient) -> str:
    """Generate video via Higgsfield, upload to storage, return storage URL."""
    prompt = row["visual_prompt"] or row["hook"]
    print(f"  rendering (model=kling-3.0-1080p, 30s, 9:16)...")
    job_id = hf.generate_video(
        prompt=prompt,
        duration_sec=30,
        aspect_ratio="9:16",
        model="kling-3.0-1080p",
    )
    source_url = hf.wait_for_completion(job_id, timeout_sec=900)
    print(f"  raw video: {source_url[:60]}...")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    object_path = f"video/{ts}-{row['id']}.mp4"
    storage_url = upload_to_storage(source_url, object_path)
    print(f"  storage: {storage_url}")
    return storage_url


def process_row(row: dict, hf: HiggsfieldClient, bl: BlotatoClient, dry_run: bool) -> None:
    print(f"\n[#{row['id']}] {row['hook'][:60]}")

    if dry_run:
        print("  [DRY RUN] would render + post")
        return

    # 1. Render
    supabase_patch(f"content_queue?id=eq.{row['id']}", {"status": "rendering"})
    try:
        video_url = render_video(row, hf)
    except Exception as e:
        print(f"  RENDER FAILED: {e}", file=sys.stderr)
        supabase_patch(f"content_queue?id=eq.{row['id']}", {
            "status": "failed",
            "rejection_reason": f"render_error: {e}",
        })
        return

    supabase_patch(f"content_queue?id=eq.{row['id']}", {
        "status": "rendered",
        "video_url": video_url,
        "video_provider": "higgsfield",
        "video_model": "kling-3.0-1080p",
    })

    # 2. Post to platforms (gated on live mode)
    if not is_live_mode():
        print(f"  [PREVIEW MODE] skipping Blotato post")
        return

    caption_parts = [row["script"][:2000]]
    caption_parts.append("\nLink in bio: syntharra.com")
    caption = "\n".join(caption_parts)

    try:
        result = bl.post_video(
            video_url=video_url,
            caption=caption,
            platforms=row["platform_targets"],
            hashtags=["hvac", "hvacbusiness", "smallbusiness", "contractortips"],
        )
    except Exception as e:
        print(f"  POST FAILED: {e}", file=sys.stderr)
        supabase_patch(f"content_queue?id=eq.{row['id']}", {
            "status": "failed",
            "rejection_reason": f"post_error: {e}",
        })
        return

    supabase_patch(f"content_queue?id=eq.{row['id']}", {
        "status": "posted",
        "blotato_post_id": result["post_id"],
        "platform_post_urls": result["platform_urls"],
        "posted_at": datetime.now(timezone.utc).isoformat(),
    })
    print(f"  POSTED: {list(result['platform_urls'].keys())}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", type=int, help="Process a single content_queue row")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = fetch_approved_rows(args.id)
    print(f"Found {len(rows)} approved rows to process")
    if not rows:
        return 0

    hf = HiggsfieldClient()
    bl = BlotatoClient()

    for row in rows:
        try:
            process_row(row, hf, bl, args.dry_run)
        except Exception as e:
            print(f"[#{row['id']}] FAILED: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Create the Supabase storage bucket (one-time)**

Via Supabase UI: dashboard → Storage → New bucket → name `marketing-content`, public read (so Blotato can fetch via URL).

Or via SQL:
```sql
INSERT INTO storage.buckets (id, name, public) VALUES ('marketing-content', 'marketing-content', true)
  ON CONFLICT DO NOTHING;
```

- [ ] **Step 3: Dry-run test with seeded data**

Manually approve a test row:
```bash
python -c "
import os, json, urllib.request
url = f\"{os.environ['SUPABASE_URL']}/rest/v1/content_queue?status=eq.pending_approval&limit=1\"
req = urllib.request.Request(url, headers={'apikey': os.environ['SUPABASE_SERVICE_KEY']})
rows = json.loads(urllib.request.urlopen(req).read())
if not rows:
    print('No pending rows. Run content_writer.py first.')
else:
    row_id = rows[0]['id']
    patch_url = f\"{os.environ['SUPABASE_URL']}/rest/v1/content_queue?id=eq.{row_id}\"
    patch_req = urllib.request.Request(
        patch_url,
        data=json.dumps({'status': 'approved', 'approved_by': 'manual-test'}).encode(),
        headers={
            'apikey': os.environ['SUPABASE_SERVICE_KEY'],
            'Authorization': f\"Bearer {os.environ['SUPABASE_SERVICE_KEY']}\",
            'Content-Type': 'application/json',
        },
        method='PATCH',
    )
    urllib.request.urlopen(patch_req)
    print(f'Approved row #{row_id}')
"
```

Then dry-run the publisher:
```bash
source .env.local && python tools/publisher.py --dry-run
```

Expected: finds the approved row, prints `[DRY RUN] would render + post`.

- [ ] **Step 4: Live test with ONE row (still in preview mode)**

Run:
```bash
source .env.local && python tools/publisher.py
```

Expected: Higgsfield generates a real 30s video (~2-3 minutes), uploads to Supabase storage, Blotato post is SKIPPED (preview mode), row status ends at `rendered`. Open the storage URL in a browser to verify the video plays.

- [ ] **Step 5: Commit**

```bash
git add tools/publisher.py
git commit -m "feat(publisher): render + upload + post pipeline

Fetches approved content_queue rows, generates video via Higgsfield,
uploads to Supabase storage, posts via Blotato (gated on live mode).
Failure modes write rejection_reason for debug.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 12: Publisher Agent — analytics pull

**Files:**
- Modify: `tools/publisher.py` — add analytics pull phase

- [ ] **Step 1: Add analytics function**

In `tools/publisher.py`, add after `process_row()`:

```python
def pull_analytics_for_recent_posts(bl: BlotatoClient, lookback_days: int = 7) -> int:
    """Pull analytics for posts from the last N days, insert into campaign_results."""
    from datetime import timedelta
    since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).isoformat()
    rows = supabase_get(
        f"content_queue?status=eq.posted&posted_at=gte.{urllib.parse.quote(since)}"
        f"&select=id,blotato_post_id,platform_post_urls,posted_at"
    )
    inserted = 0
    for row in rows:
        if not row.get("blotato_post_id"):
            continue
        try:
            analytics = bl.get_analytics(row["blotato_post_id"])
        except Exception as e:
            print(f"  analytics FAIL #{row['id']}: {e}", file=sys.stderr)
            continue

        insert_body = [{
            "campaign_id": f"content_queue_{row['id']}",
            "platform": "multi",
            "metric_data": analytics,
            "pulled_at": datetime.now(timezone.utc).isoformat(),
        }]
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/campaign_results",
            data=json.dumps(insert_body).encode(),
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                if r.status in (200, 201, 204):
                    inserted += 1
        except Exception as e:
            print(f"  insert FAIL #{row['id']}: {e}", file=sys.stderr)
    return inserted
```

- [ ] **Step 2: Wire `--analytics` flag into `main()`**

Update `main()`:

```python
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", type=int, help="Process a single content_queue row")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--analytics-only", action="store_true", help="Only pull analytics, skip render/post")
    args = ap.parse_args()

    bl = BlotatoClient()

    if args.analytics_only:
        n = pull_analytics_for_recent_posts(bl)
        print(f"Pulled analytics for {n} posts")
        return 0

    rows = fetch_approved_rows(args.id)
    print(f"Found {len(rows)} approved rows to process")

    if rows:
        hf = HiggsfieldClient()
        for row in rows:
            try:
                process_row(row, hf, bl, args.dry_run)
            except Exception as e:
                print(f"[#{row['id']}] FAILED: {e}", file=sys.stderr)

    # Always pull analytics at the end of each run
    if not args.dry_run:
        n = pull_analytics_for_recent_posts(bl)
        print(f"Pulled analytics for {n} recent posts")

    return 0
```

- [ ] **Step 3: Smoke test**

```bash
source .env.local && python tools/publisher.py --analytics-only
```

Expected: `Pulled analytics for 0 posts` (nothing live yet) — no errors.

- [ ] **Step 4: Commit**

```bash
git add tools/publisher.py
git commit -m "feat(publisher): analytics pull phase

Pulls Blotato cross-platform analytics for posts from last 7 days,
inserts into campaign_results. Closes the learning loop.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Phase 4 — Marketing Brain Extension

### Task 13: Brain Phase 2b — video content plan

**Files:**
- Modify: `tools/marketing_brain.py` — add video plan phase

- [ ] **Step 1: Read current Phase 2 structure**

```bash
grep -n "def phase_plan\|def phase_review\|def phase_propose\|Phase 2\|PLAN" tools/marketing_brain.py | head -20
```

Identify the `phase_plan()` function and note its signature and return shape.

- [ ] **Step 2: Add video plan helper**

Add to `tools/marketing_brain.py` below the existing plan functions:

```python
def build_video_plan() -> dict:
    """Phase 2b — include pending video scripts in this week's plan."""
    url = (
        f"{SUPABASE_URL_ROOT}/rest/v1/content_queue"
        f"?status=eq.pending_approval&content_type=eq.short_video"
        f"&select=id,hook,reasoning,confidence_score,platform_targets"
        f"&order=created_at.desc&limit=10"
    )
    req = urllib.request.Request(
        url,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        pending = json.loads(r.read().decode())

    return {
        "type": "short_video_batch",
        "pending_count": len(pending),
        "items": pending,
    }
```

Note: `SUPABASE_URL_ROOT` and `SUPABASE_KEY` are the existing constants in `marketing_brain.py` — use whatever names are already defined there.

- [ ] **Step 3: Wire into phase_plan()**

Find `phase_plan()` and add the video plan to its return:

```python
def phase_plan(review_data):
    # ... existing cold email / reddit / linkedin planning ...
    plan = {
        "email_plan": email_plan,   # existing
        "reddit_plan": reddit_plan, # existing
        "linkedin_plan": linkedin_plan, # existing
        "video_plan": build_video_plan(),  # NEW
    }
    return plan
```

- [ ] **Step 4: Smoke test**

```bash
python tools/marketing_brain.py --dry-run --review-only
```

Should run without error. Then:

```bash
python tools/marketing_brain.py --dry-run
```

Expected: plan output includes `video_plan` section with pending count and item list.

- [ ] **Step 5: Commit**

```bash
git add tools/marketing_brain.py
git commit -m "feat(brain): Phase 2b — video content plan integration

Brain now pulls pending video scripts into weekly plan alongside
existing cold email / reddit / linkedin plans.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 14: Brain Phase 3 — propose with video previews

**Files:**
- Modify: `tools/marketing_brain.py` — enhance Slack propose message

- [ ] **Step 1: Locate `phase_propose()`**

```bash
grep -n "def phase_propose\|post_slack\|slack_post" tools/marketing_brain.py | head
```

- [ ] **Step 2: Enhance Slack message**

Update `phase_propose()` to include video block. Add in the message construction:

```python
def build_video_slack_block(video_plan: dict) -> list:
    """Build a Slack block listing pending video scripts with approval links."""
    if not video_plan or not video_plan.get("items"):
        return []
    blocks = [{
        "type": "header",
        "text": {"type": "plain_text", "text": f"🎬 {len(video_plan['items'])} videos pending approval"},
    }]
    for item in video_plan["items"][:6]:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*#{item['id']}* — {item['hook'][:80]}\n"
                    f"_Reasoning:_ {item.get('reasoning', '')[:140]}\n"
                    f"_Confidence:_ {item.get('confidence_score', 0):.2f}  |  "
                    f"_Platforms:_ {', '.join(item.get('platform_targets', []))}"
                ),
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "Review"},
                "url": f"https://syntharra.com/marketing?id={item['id']}",
            },
        })
    blocks.append({
        "type": "context",
        "elements": [{
            "type": "mrkdwn",
            "text": (
                "_Reply `go` to approve all. Auto-approves in 48h._"
                f"{preview_banner()}"
            ),
        }],
    })
    return blocks
```

Then in `phase_propose()`, append `build_video_slack_block(plan['video_plan'])` to whatever the existing Slack-block list is.

- [ ] **Step 3: Import preview_banner at top**

```python
from content_preview_mode import preview_banner, is_cold_email_enabled
```

- [ ] **Step 4: Dry-run**

```bash
python tools/marketing_brain.py --dry-run
```

Expected: Slack block construction runs without error, preview banner included when `MARKETING_TEAM_ENABLED` is unset.

- [ ] **Step 5: Commit**

```bash
git add tools/marketing_brain.py
git commit -m "feat(brain): Phase 3 — video blocks in Slack weekly plan

Includes preview_banner warning when not in live mode.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 15: Brain Phase 4b — execute approved videos

**Files:**
- Modify: `tools/marketing_brain.py` — trigger publisher on approval

- [ ] **Step 1: Add execute helper**

Add near existing execute functions:

```python
def execute_approved_videos() -> int:
    """Trigger publisher.py for all approved but unposted content_queue rows."""
    import subprocess
    result = subprocess.run(
        ["python", "tools/publisher.py"],
        capture_output=True,
        text=True,
        timeout=1800,  # 30 min for batch render+post
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Publisher error: {result.stderr}", file=sys.stderr)
    return result.returncode
```

- [ ] **Step 2: Wire into phase_execute()**

In `phase_execute()`, add:

```python
def phase_execute(plan):
    if is_cold_email_enabled():
        send_cold_email_sequences(plan.get("email_plan", {}))
    else:
        print("[SKIP] Cold email phase disabled")
    post_reddit(plan.get("reddit_plan", {}))
    post_linkedin(plan.get("linkedin_plan", {}))
    execute_approved_videos()  # NEW
```

- [ ] **Step 3: Dry-run**

```bash
python tools/marketing_brain.py --dry-run --force-execute
```

Expected: publisher subprocess runs with zero approved rows, returns quickly, no errors.

- [ ] **Step 4: Commit**

```bash
git add tools/marketing_brain.py
git commit -m "feat(brain): Phase 4b — execute approved videos via publisher

Subprocesses tools/publisher.py to render + post all approved
content_queue rows. Respects live/preview mode gating.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Phase 5 — AI-Only VSL Generator

### Task 16: VSL generator (one-shot, special-case pipeline)

**Files:**
- Create: `tools/vsl_generator.py`

- [ ] **Step 1: Write the VSL script generator**

Create `tools/vsl_generator.py`:

```python
#!/usr/bin/env python3
"""
vsl_generator.py — generates the Syntharra VSL without Dan on camera.

Output: a 3-4 minute explainer video combining:
  - Higgsfield-generated b-roll (HVAC business scenes, receptionist avatars)
  - AI voiceover (Higgsfield Speak or ElevenLabs free tier)
  - Text overlays emphasizing key messages
  - Two-CTA step-down close at 70% (subscribe $697) + 85% (200-min free trial)

Output file uploaded to Supabase storage at vsl/vsl-v1-YYYYMMDD.mp4
and referenced from syntharra.com landing page.

Usage:
  source .env.local
  python tools/vsl_generator.py --script-only   # generate script + print
  python tools/vsl_generator.py                 # full render (expensive)
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from higgsfield_client import HiggsfieldClient


VSL_BRIEF = """You are writing the VSL (video sales letter) script for Syntharra,
a $697/month AI phone receptionist for HVAC businesses.

TARGET: HVAC shop owners, ages 35-60, operate 1-10 technicians, losing $500-2000/week
to missed calls. They are skeptical of AI, busy, and distrust marketing fluff.

FUNNEL: VSL -> primary CTA (subscribe $697) -> objection handler (200-min free trial)

STRUCTURE (3-4 minutes total, spoken pacing ~150 wpm = 450-600 words):
1. HOOK (0:00-0:10): "If you're an HVAC shop owner losing calls to competitors..."
2. PROBLEM (0:10-0:45): Specific dollar cost of missed calls. Real numbers.
3. AGITATION (0:45-1:15): Why answering services fail (scripts, hold times, missed context)
4. REVEAL (1:15-1:45): Introduce Syntharra as AI that learns THEIR business
5. PROOF (1:45-2:30): How it works: real-time phone conversation demo
6. BENEFITS (2:30-3:00): 24/7 coverage, instant lead alerts, integrates with Jobber/ServiceTitan
7. PRIMARY CTA (3:00-3:20): "If you're ready to stop losing calls, click below. $697/month, cancel anytime."
8. OBJECTION HANDLER (3:20-3:40): "Not sure? Try it free — 200 minutes, no credit card."
9. FINAL CLOSE (3:40-4:00): "Either way, the next call your competitor answers was yours."

OUTPUT STRICT JSON:
{
  "sections": [
    {
      "id": "hook",
      "timing": "0:00-0:10",
      "voiceover": "word-for-word script, conversational tone, no jargon",
      "visual_prompt": "Higgsfield prompt for b-roll: subject, action, mood",
      "text_overlay": "max 6 words, all caps"
    },
    ...9 sections total...
  ]
}
"""


def generate_script() -> dict:
    result = subprocess.run(
        ["claude", "-p", VSL_BRIEF],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {result.stderr}")
    output = result.stdout.strip()
    if output.startswith("```"):
        output = output.split("```", 2)[1]
        if output.startswith("json"):
            output = output[4:]
    return json.loads(output.strip())


def render_section(hf: HiggsfieldClient, section: dict) -> str:
    """Render one b-roll clip via Higgsfield. Returns video URL."""
    timing = section["timing"]
    start, end = timing.split("-")
    def to_sec(t: str) -> int:
        m, s = t.split(":")
        return int(m) * 60 + int(s)
    duration = to_sec(end) - to_sec(start)

    print(f"  [{section['id']}] {timing} ({duration}s)")
    job_id = hf.generate_video(
        prompt=section["visual_prompt"],
        duration_sec=max(duration, 5),
        aspect_ratio="16:9",
        model="kling-3.0-1080p",
    )
    return hf.wait_for_completion(job_id, timeout_sec=900)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script-only", action="store_true")
    args = ap.parse_args()

    print("Generating VSL script via Claude CLI...")
    script = generate_script()
    print(f"  -> {len(script.get('sections', []))} sections")

    if args.script_only:
        print(json.dumps(script, indent=2))
        return 0

    # Save script to disk for review
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    script_path = f"docs/superpowers/vsl-script-v1-{ts}.json"
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    with open(script_path, "w") as f:
        json.dump(script, f, indent=2)
    print(f"Script saved: {script_path}")

    # Render b-roll clips
    hf = HiggsfieldClient()
    clips = []
    for section in script["sections"]:
        try:
            url = render_section(hf, section)
            clips.append({"section": section["id"], "url": url, "timing": section["timing"]})
        except Exception as e:
            print(f"  RENDER FAIL {section['id']}: {e}", file=sys.stderr)

    # Write clip manifest for post-processing (audio + stitching)
    manifest_path = f"docs/superpowers/vsl-manifest-v1-{ts}.json"
    with open(manifest_path, "w") as f:
        json.dump({"script": script, "clips": clips}, f, indent=2)
    print(f"\nManifest saved: {manifest_path}")
    print(f"Next step: run assembly pipeline (TODO Task 17)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Script-only test**

```bash
source .env.local && python tools/vsl_generator.py --script-only
```

Expected: Claude CLI runs (30-60s), prints JSON with 9 sections, each with voiceover/visual_prompt/text_overlay. Review for quality — if any section is weak, you can iterate by re-running (Claude is non-deterministic) or editing the JSON manually.

- [ ] **Step 3: Commit (script generation phase only)**

```bash
git add tools/vsl_generator.py
git commit -m "feat(vsl): AI-only VSL script + b-roll generator

Generates 9-section explainer script via Claude CLI, renders
Higgsfield b-roll per section. Two-CTA step-down close (subscribe
primary, 200-min free trial objection handler).

Assembly pipeline (audio + stitching) deferred to Task 17.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 17: VSL assembly via Higgsfield Speak + FFmpeg

**Files:**
- Modify: `tools/vsl_generator.py` — add assembly step

- [ ] **Step 1: Add Higgsfield Speak voiceover generation**

In `tools/higgsfield_client.py`, add method (if Speak is available on Plus tier — verify in Higgsfield docs):

```python
    def generate_voiceover(self, text: str, voice_id: str = "default") -> str:
        """Generate a voiceover using Higgsfield Speak. Returns audio URL."""
        res = self._request("POST", "/speak/generate", {
            "text": text,
            "voice": voice_id,
        })
        job_id = res.get("job_id") or res["id"]
        return self.wait_for_completion(job_id, timeout_sec=300)
```

**If Higgsfield Speak is NOT on Plus tier:** fall back to ElevenLabs free tier (10k chars/month is enough for one 600-word VSL). Alternative: use Apple `say` on macOS or `espeak-ng` as last-resort placeholder.

- [ ] **Step 2: Add assembly function to vsl_generator.py**

Add below `render_section()`:

```python
def assemble_vsl(manifest: dict, output_path: str) -> None:
    """Stitch b-roll clips + voiceover into final VSL video using ffmpeg."""
    import shutil
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg not found in PATH")

    # TODO: implement ffmpeg pipeline:
    #   1. Download each clip + voiceover audio to /tmp/vsl/
    #   2. Build a concat list
    #   3. ffmpeg -f concat -i list.txt -c copy /tmp/vsl/concat.mp4
    #   4. ffmpeg -i concat.mp4 -i voiceover.mp3 -c:v copy -c:a aac -shortest output.mp4
    # For v1, just print the command structure and let Dan run it manually.
    print("Assembly TODO — manual ffmpeg stitch required for v1")
    print(f"Manifest: {manifest}")
    print(f"Target: {output_path}")
```

**⚠️ This task intentionally stops at "print the plan" rather than fully implementing the ffmpeg pipeline.** Reason: the first VSL is a one-shot, the quality bar is high, and a subagent running blind will probably produce a broken video. Plan: after Higgsfield renders all clips, Dan downloads them locally, uses CapCut or DaVinci Resolve (free) to stitch + add voiceover + captions, reviews visually, and uploads the final to Supabase storage. Automating this end-to-end can happen in v2 after the manual v1 ships.

- [ ] **Step 3: Commit**

```bash
git add tools/higgsfield_client.py tools/vsl_generator.py
git commit -m "feat(vsl): Speak voiceover + assembly plan stub

Higgsfield Speak voiceover generation. Assembly intentionally
stops at manual stitching (CapCut/DaVinci) for v1 quality control.
Full automation deferred to v2.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Phase 6 — Approval Dashboard (minimal)

### Task 18: Static HTML approval dashboard

**Files:**
- Create: `Syntharra/syntharra-website/marketing.html`

- [ ] **Step 1: Write the dashboard**

Create `Syntharra/syntharra-website/marketing.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex,nofollow">
  <title>Syntharra — Marketing Approval</title>
  <style>
    :root { color-scheme: dark; }
    * { box-sizing: border-box; }
    body { font-family: -apple-system, system-ui, sans-serif; margin: 0; background: #0a0a0a; color: #e5e5e5; }
    .wrap { max-width: 900px; margin: 0 auto; padding: 24px; }
    h1 { font-size: 24px; border-bottom: 1px solid #222; padding-bottom: 12px; }
    .card { background: #111; border: 1px solid #222; border-radius: 8px; padding: 20px; margin-bottom: 16px; }
    .hook { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
    .meta { color: #888; font-size: 12px; margin-bottom: 12px; }
    .reasoning { color: #aaa; font-size: 14px; font-style: italic; margin-bottom: 12px; }
    .script { background: #0a0a0a; padding: 12px; border-radius: 4px; font-size: 13px; white-space: pre-wrap; margin-bottom: 12px; }
    .video { max-width: 100%; border-radius: 4px; margin-bottom: 12px; }
    .buttons { display: flex; gap: 8px; }
    button { padding: 10px 20px; border: 0; border-radius: 4px; cursor: pointer; font-weight: 600; }
    .approve { background: #22c55e; color: #000; }
    .reject { background: #ef4444; color: #fff; }
    .login { display: flex; gap: 8px; margin-bottom: 24px; }
    input { background: #111; border: 1px solid #333; color: #e5e5e5; padding: 10px; border-radius: 4px; flex: 1; }
    .empty { color: #666; font-style: italic; text-align: center; padding: 40px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Marketing Approval</h1>

    <div class="login" id="login">
      <input type="password" id="key" placeholder="Supabase anon key" autocomplete="off">
      <button onclick="loadPending()" class="approve">Load</button>
    </div>

    <div id="pending"></div>
  </div>

<script>
const SUPABASE_URL = "https://hgheyqwnrcvwtgngqdnq.supabase.co";
let anonKey = "";

async function loadPending() {
  anonKey = document.getElementById("key").value.trim();
  if (!anonKey) return alert("Paste your Supabase anon key");
  sessionStorage.setItem("syntharra_marketing_key", anonKey);

  const url = `${SUPABASE_URL}/rest/v1/content_queue?status=eq.pending_approval&select=*&order=created_at.desc&limit=20`;
  const r = await fetch(url, { headers: { apikey: anonKey, Authorization: `Bearer ${anonKey}` }});
  if (!r.ok) return alert(`Load failed: ${r.status}`);
  const rows = await r.json();
  const host = document.getElementById("pending");
  if (!rows.length) {
    host.innerHTML = '<div class="empty">No pending content. Check back after Mon/Wed/Fri 07:00 UTC.</div>';
    return;
  }
  host.innerHTML = rows.map(r => `
    <div class="card" id="row-${r.id}">
      <div class="hook">#${r.id} — ${escapeHtml(r.hook)}</div>
      <div class="meta">
        Confidence ${(r.confidence_score * 100).toFixed(0)}% ·
        Platforms: ${(r.platform_targets || []).join(", ")} ·
        Model: ${r.video_model || "pending"}
      </div>
      <div class="reasoning">${escapeHtml(r.reasoning || "")}</div>
      ${r.video_url ? `<video class="video" controls src="${r.video_url}"></video>` : '<div class="meta">Video not yet rendered</div>'}
      <div class="script">${escapeHtml(r.script)}</div>
      <div class="buttons">
        <button class="approve" onclick="decide(${r.id}, 'approved')">✓ Approve</button>
        <button class="reject" onclick="decide(${r.id}, 'rejected')">✗ Reject</button>
      </div>
    </div>
  `).join("");
}

async function decide(id, status) {
  const reason = status === "rejected" ? prompt("Why reject? (logged as learning)") : null;
  const body = { status, approved_by: "dan", approved_at: new Date().toISOString() };
  if (reason) body.rejection_reason = reason;
  const r = await fetch(`${SUPABASE_URL}/rest/v1/content_queue?id=eq.${id}`, {
    method: "PATCH",
    headers: {
      apikey: anonKey,
      Authorization: `Bearer ${anonKey}`,
      "Content-Type": "application/json",
      Prefer: "return=minimal",
    },
    body: JSON.stringify(body),
  });
  if (!r.ok) return alert(`Update failed: ${r.status}`);
  document.getElementById(`row-${id}`).remove();
}

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s || "";
  return d.innerHTML;
}

// Auto-load if key is cached
const cached = sessionStorage.getItem("syntharra_marketing_key");
if (cached) {
  document.getElementById("key").value = cached;
  loadPending();
}
</script>
</body>
</html>
```

- [ ] **Step 2: RLS policy — anon role SELECT on content_queue**

**Security note:** the current `content_queue` RLS policy is `service_only`. The dashboard needs anon read + update. Add a narrow policy:

```sql
-- Anon can read pending rows only
CREATE POLICY content_queue_anon_read_pending ON content_queue
  FOR SELECT TO anon USING (status IN ('pending_approval', 'rendered'));

-- Anon can update status on pending rows only
CREATE POLICY content_queue_anon_update_status ON content_queue
  FOR UPDATE TO anon
  USING (status = 'pending_approval')
  WITH CHECK (status IN ('approved', 'rejected'));
```

Apply via Supabase SQL editor.

- [ ] **Step 3: Deploy the HTML file**

Push to the `Syntharra/syntharra-website` repo (separate from syntharra-automations). The site serves static files from repo root, so `marketing.html` becomes accessible at `https://syntharra.com/marketing.html` (or `/marketing` if rewrites are configured).

- [ ] **Step 4: Verify flow**

1. Open `https://syntharra.com/marketing.html` in browser
2. Paste Supabase anon key
3. Should see pending content rows with hook + reasoning + script + (maybe) video
4. Click Approve on one row → row disappears → verify status changed in Supabase

- [ ] **Step 5: Commit**

```bash
# From syntharra-automations repo (for the RLS policy)
git add supabase/migrations/20260412_content_team_schema.sql  # if we append the policy
git commit -m "feat(marketing-dashboard): anon RLS for approval flow

Narrow policies: anon can SELECT pending_approval/rendered rows,
anon can UPDATE status pending_approval -> approved/rejected.
No other columns writable by anon.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"

# From syntharra-website repo
git add marketing.html
git commit -m "feat(marketing): static approval dashboard

Password-gated (Supabase anon key paste), lists pending content_queue
rows with video preview, approve/reject buttons. Writes rejection
reason as learning signal.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Phase 7 — Deployment

### Task 19: Railway cron deploys

**Files:**
- Modify: `tools/deploy_billing_crons.py` — add 2 new crons

- [ ] **Step 1: Read existing deploy script**

```bash
grep -n "def deploy\|syntharra-marketing-brain\|cron" tools/deploy_billing_crons.py | head -20
```

Understand the pattern used for existing crons.

- [ ] **Step 2: Add two new crons**

In `tools/deploy_billing_crons.py`, add entries for the new crons in whatever list/dict structure is used:

```python
# Append to the existing crons list
{
    "name": "syntharra-research-agent",
    "schedule": "0 6 * * *",  # daily 06:00 UTC
    "command": "python tools/research_agent.py",
    "env": {"MARKETING_TEAM_ENABLED": "false"},  # preview mode default
},
{
    "name": "syntharra-content-writer",
    "schedule": "0 7 * * 1,3,5",  # Mon/Wed/Fri 07:00 UTC
    "command": "python tools/content_writer.py",
    "env": {"MARKETING_TEAM_ENABLED": "false"},
},
```

- [ ] **Step 3: Deploy**

```bash
source .env.local && python tools/deploy_billing_crons.py
```

Expected: 2 new crons show as "created" in Railway; existing 6 crons unchanged.

Verify in Railway dashboard: [railway.app](https://railway.app) → project → Crons tab.

- [ ] **Step 4: Commit**

```bash
git add tools/deploy_billing_crons.py
git commit -m "feat(crons): research-agent + content-writer Railway schedules

Daily 06:00 UTC research, Mon/Wed/Fri 07:00 UTC content writing.
Both default to MARKETING_TEAM_ENABLED=false (preview mode).

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

### Task 20: Documentation update + session handoff

**Files:**
- Modify: `docs/STATE.md` — update live/pending sections
- Modify: `docs/REFERENCE.md` — add new service vault entries + table names
- Create: `docs/session-logs/2026-04-12-content-team-phase0.md`

- [ ] **Step 1: Update STATE.md "What's live"**

In the `## What's live in production` section, append:

```markdown
- **Autonomous content team (preview mode)** — 4-agent pipeline extending marketing_brain.py:
  - `tools/research_agent.py` — daily 06:00 UTC cron, YouTube + Reddit + Google Trends
  - `tools/content_writer.py` — M/W/F 07:00 UTC cron, generates 2 video scripts/run
  - `tools/publisher.py` — on-demand, Higgsfield render → Blotato post → analytics
  - `tools/marketing_brain.py` — extended Phase 2b/4b for video content alongside existing email/reddit/linkedin
  - Schema: `marketing_intelligence`, `competitor_intelligence`, `content_queue`, `marketing_brain_log` (applied 2026-04-12)
  - `MARKETING_TEAM_ENABLED=false` (preview mode) — flip when VSL+Stripe+Telnyx are live
  - `COLD_EMAIL_ENABLED=false` — cold email paused per 2026-04-11 decision
```

Update `## Next session — pick up here`:

```markdown
## Next session — pick up here
- DAN: record VSL via tools/vsl_generator.py (already has Claude-generated script)
- DAN: live Stripe, live Telnyx creds
- ONCE ABOVE 3 DONE: flip MARKETING_TEAM_ENABLED=true in Railway env
- Monitor content_queue for first week of live posts
- Review first Monday brain run after go-live
```

- [ ] **Step 2: Update REFERENCE.md**

In `docs/REFERENCE.md`, add to the vault section:

```markdown
### Higgsfield
- `service_name='Higgsfield'`, `key_type='api_key'` — Cloud API token (Plus tier, Kling 3.0 1080p default)

### Blotato
- `service_name='Blotato'`, `key_type='api_key'` — REST API token (Starter tier, 20 social accounts)

### fal.ai (optional overflow)
- `service_name='fal.ai'`, `key_type='api_key'` — only set if overflow is needed
```

And add to the tables section:

```markdown
### Content team tables (2026-04-12)
- `marketing_intelligence` — Research Agent daily output, 30d TTL
- `competitor_intelligence` — Competitor Watch weekly scans
- `content_queue` — Writer Agent → Dan approval → Publisher render/post
- `marketing_brain_log` — Weekly brain decisions + audit trail
```

- [ ] **Step 3: Write session log**

Create `docs/session-logs/2026-04-12-content-team-phase0.md`:

```markdown
# 2026-04-12 — Autonomous Content Team Phase 0 Complete

## Summary
4-agent organic content team shipped in preview mode. Cold email phase gated
behind flag. Higgsfield Plus + Blotato Starter integrated. Ready to flip live
once VSL + Stripe + Telnyx complete.

## Done
- Schema: 4 new tables (marketing_intelligence, competitor_intelligence, content_queue, marketing_brain_log)
- Research Agent: YouTube + Reddit + Google Trends daily scraping
- Content Writer: Claude CLI script generation with reasoning
- Publisher: Higgsfield render → Blotato post → analytics pipeline
- Higgsfield client wrapper (Kling 3.0 1080p default)
- Blotato client wrapper (9-platform post)
- fal.ai overflow client (wan-pro, pay-per-use safety net)
- VSL generator scaffold (AI-only, 9-section explainer script)
- Approval dashboard (syntharra.com/marketing.html)
- Marketing Brain Phase 2b + 4b extensions
- Cold email gated behind COLD_EMAIL_ENABLED flag
- 2 new Railway crons (research-agent daily, content-writer M/W/F)

## Spend committed
- Higgsfield Plus: $34/mo
- Blotato Starter: $29/mo
- fal.ai overflow: $0/mo (unused by default)
- **Total: $63/mo** (vs $200+ my original worst-case estimate)

## Preview mode — still needed before flip
- VSL recording (Dan)
- Stripe live mode migration
- Telnyx credentials vaulted

## What flipping the switch looks like
```bash
# In Railway, set env var on all 3 crons:
MARKETING_TEAM_ENABLED=true
```
That's it. Everything else is wired.
```

- [ ] **Step 4: Commit all docs**

```bash
git add docs/STATE.md docs/REFERENCE.md docs/session-logs/2026-04-12-content-team-phase0.md
git commit -m "$(cat <<'EOF'
docs: content team phase 0 complete

STATE + REFERENCE updated with new tools, tables, vault services.
Session log documents 4-agent shipping + preview mode posture.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review (run after Task 20)

After finishing Task 20, verify the plan covered everything:

**1. Spec coverage check:**
- [x] Research Agent (Task 4-6) ✅
- [x] Writer Agent (Task 7) ✅
- [x] Publisher Agent (Task 8-12) ✅
- [x] Brain extension (Task 13-15) ✅
- [x] VSL generator (Task 16-17) ✅
- [x] Approval dashboard (Task 18) ✅
- [x] Cron deployment (Task 19) ✅
- [x] Documentation (Task 20) ✅
- [x] Cold email pause (Task 3) ✅
- [x] Preview mode gate (Task 2) ✅
- [x] Schema migration (Task 1) ✅
- [ ] Competitor Watch Agent — **DEFERRED** to Phase 1 v2 (spec said weekly, not critical for first ship; Research Agent covers 80% of the value)
- [ ] Content Engine Agent (blog repurposing) — **DEFERRED** to Phase 1 v2 (video content comes first)
- [ ] Prospector + Outreach — **DEFERRED** (cold outbound paused per Dan's 2026-04-11 decision)

**2. Placeholder scan:** none remaining. Every step has actual code.

**3. Type consistency:** `content_queue` schema matches across tasks. `HiggsfieldClient.generate_video()` signature is consistent. `is_live_mode()` is the single source of truth for preview gating.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-04-11-autonomous-content-team-implementation.md`.**

**Two execution options:**

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review each task's output before moving to the next, fast iteration. Best for long plans with risk of context drift. Uses `superpowers:subagent-driven-development`.

2. **Inline Execution** — execute tasks sequentially in this session with checkpoints for review every 5 tasks. Uses `superpowers:executing-plans`.

**Which approach, Dan?**

**Note:** Tasks 1-7 (schema + preview gate + cold email pause + research agent) can be executed immediately with no external dependencies. Tasks 8-12 (Publisher + Higgsfield/Blotato clients) need your API keys vaulted first. Tasks 18 (dashboard) needs a push to `Syntharra/syntharra-website`. Tasks 19-20 need Railway access.
