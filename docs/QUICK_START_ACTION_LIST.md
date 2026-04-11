# Syntharra — Dan's Quick Start Action List

> **Status as of 2026-04-11:** Everything is built and running. These are the 15 actions that only YOU can take. In priority order.

---

## RIGHT NOW (takes < 30 min total)

### 1. Submit sitemap to Google Search Console (~15 min)
**Why first:** 82 pages are live but Google hasn't indexed them. Without this, zero organic traffic.
**How:** See `docs/google_search_console_setup.md` — full step-by-step.

### 2. Send the 3 cold outreach emails already queued (~5 min)
**Why:** Last test showed 3 Las Vegas HVAC shops with emails found and sequences generated.
**How:**
```bash
# Preview first (no sends):
python tools/send_cold_outreach.py --city "Las Vegas" --preview

# Send for real (opens Brevo):
python tools/send_cold_outreach.py --city "Las Vegas" --backend brevo
```
Then pick 2-3 more cities:
```bash
python tools/scrape_hvac_directory.py --city "Phoenix" --state AZ --limit 20
python tools/find_email_from_website.py leads/phoenix_hvac_leads.json
python tools/build_cold_outreach.py leads/phoenix_hvac_leads.json
python tools/send_cold_outreach.py leads/phoenix_cold_outreach.json --backend brevo
```

### 3. Post one community post to r/HVAC (~5 min)
**Why:** Zero-cost word-of-mouth. HVAC subreddits have tens of thousands of owner-operators.
**How:** Open `docs/community_post_drafts.md` → find a Reddit draft → copy + paste to reddit.com/r/HVAC.
Pick the one titled "How do you handle 2 a.m. calls?" — it's the least salesy and will get the most engagement.

---

## THIS WEEK

### 4. Send affiliate outreach to 1-2 HVAC YouTubers
**Why:** A single recommendation from Bryan Orr (HVAC School, 200K subscribers) could send 50+ leads.
**How:** Run `python tools/build_affiliate_outreach.py` → open `leads/affiliate_outreach_*.txt` → send Touch 1 to 1-2 channels manually.
Priority: HVAC School (Bryan Orr) and AC Service Tech (Craig Migliaccio).

### 5. Vault your Telnyx credentials
**Why:** WITHOUT THIS, pilots sign up but can't receive calls. The AI answers nobody.
**What you need:**
- Telnyx API key (from telnyx.com → API Keys)  
- Retell SIP connection ID (from Retell dashboard → Connections)
**How:** Run this in terminal:
```bash
python tools/vault_secret.py "Telnyx" "api_key" "YOUR_TELNYX_KEY"
python tools/vault_secret.py "Telnyx" "retell_sip_connection_id" "YOUR_SIP_ID"
```
Or add directly in Supabase dashboard → `syntharra_vault` table.

### 6. Post 2-3 community posts (LinkedIn + HVAC-Talk forum)
**Why:** LinkedIn HVAC groups have business owners, not just techs. HVAC-Talk has owner-operators.
**How:** `docs/community_post_drafts.md` → grab LinkedIn drafts → post to your LinkedIn.

### 7. Deploy the marketing digest cron (needs RAILWAY_TOKEN, ~2 min)
**Why:** Gets you a daily Slack ping with funnel numbers — pilot signups, outreach sends, conversions.
**How:**
1. Go to railway.com → Account Settings → Tokens → create a token
2. Run: `RAILWAY_TOKEN=<token> python tools/deploy_billing_crons.py`
   (Will skip the 4 already-deployed services, only create `syntharra-marketing-digest`)
3. Also: add Slack bot token to vault so the digest actually posts:
   `python tools/vault_secret.py "Slack" "bot_token" "xoxb-YOUR-TOKEN"`

### 8. Film the founder VSL
**Why:** This is the biggest conversion unlock. Cold traffic needs to see your face.
**What:** 60 seconds on your iPhone. Script is in `docs/superpowers/specs/2026-04-10-phase-0-vsl-funnel-design.md` § 3.2.
**Key line:** Open with: *"I ran out of my own 40th birthday party to get on site for a client."*

---

## BEFORE FIRST PAYING CLIENT

### 9. Vault Stripe live key
```bash
python tools/vault_secret.py "Stripe" "secret_key_live" "sk_live_..."
```

### 10. Register Stripe webhook
1. In Stripe dashboard → Developers → Webhooks → Add endpoint
2. URL: `https://hgheyqwnrcvwtgngqdnq.supabase.co/functions/v1/stripe-webhook`
3. Events: `payment_intent.succeeded`, `customer.subscription.created`, `customer.subscription.deleted`
4. Copy the signing secret → vault it:
   ```bash
   python tools/vault_secret.py "Stripe" "webhook_signing_secret" "whsec_..."
   ```

### 11. Rotate Mux secret
**Why:** The original Mux secret was sent in a plaintext chat message (leak vector).
1. Go to Mux dashboard → Settings → API Access Tokens → revoke old, create new
2. Update vault: update the row in Supabase `syntharra_vault` where `service_name='Mux' AND key_type='secret_key'`

---

## AFTER 2 PAYING CLIENTS (unlock paid tools)

### 12. Upgrade Hunter.io (currently free — 25 searches/month)
**Current:** Free tier, API key already vaulted. Hits 25 email lookups then stops.
**When to upgrade:** After 2 clients close via outreach. Proof of channel working.
**Upgrade:** hunter.io → Starter plan (~$49/mo) → 500 searches/month.

### 13. Consider Yelp Fusion API
**Cost:** ~$300/mo for meaningful volume
**Only after:** 2+ clients from organic outreach. Proves the channel before paying.

---

## MONITORING DASHBOARD (run anytime)

```bash
# See today's funnel (pilots, outreach, conversions)
python tools/marketing_digest.py

# See what's live right now
python tools/session_start.py
```

**Railway crons already running (no action needed):**
- `syntharra-pilot-lifecycle` — daily 00:00 UTC — auto-handles all pilot emails
- `syntharra-usage-alert` — daily 08:00 UTC
- `syntharra-monthly-billing` — 2nd of month 09:00 UTC
- `syntharra-weekly-report` — Sunday 18:00 UTC
- `syntharra-marketing-digest` — daily 09:00 UTC (needs RAILWAY_TOKEN deploy — action #7 above)

---

## THE MATH (reminder of why all this matters)

| If Dan does | Expected result |
|---|---|
| GSC + sitemap submit | ~20-50 indexed pages within 30 days → organic impressions start |
| 3 city cold outreach campaigns | ~60 emails sent → statistically ~2-4 replies → 1 pilot |
| 1 affiliate YouTuber deal | 1 mention to 50K-200K subscribers → 3-10 qualified leads |
| 1 community post (Reddit) | 1K-10K views if it resonates → 2-5 inbound contacts |
| VSL filmed + on start page | Cold traffic converts at 2-5% instead of ~0% |

One pilot = $0 upfront risk. One conversion = $697/mo × 12 months = $8,364 LTV.
You need 2 conversions to unlock paid tools. You need ~10 to go full send on paid acquisition.

---

*Last updated: 2026-04-11. Update this file as blockers clear.*
