# n8n Workflow Specifications — Syntharra Social Leads
# All workflows live on Railway n8n at n8n.syntharra.com
# API keys always retrieved from Supabase syntharra_vault at runtime

---

## WORKFLOW 1 — Weekly Content Generation Loop
**Name:** `Social - Content Generation`
**Schedule:** CRON — Monday 7:00am EST
**Phase:** 1+

### Steps

1. **CRON Trigger** — Every Monday 7:00am

2. **Get Vault Keys** (HTTP Request)
   - Fetch Claude API key, Blotato API key, Supabase service role key
   - Pattern: `GET /rest/v1/syntharra_vault?service_name=eq.Claude&key_type=eq.api_key`

3. **Get Weekly Pattern Brief** (Supabase)
   - Query `content_patterns` WHERE `week_of = last week's date`
   - If exists: extract `brief_for_next_week` — inject into Claude prompt
   - If null: use default prompt (first week)

4. **Set Parameters** (Set Node)
   - `industry`: "HVAC"  ← change to "electrical" or "plumbing" for Phase 3
   - `vertical`: "hvac"
   - `week_of`: current Monday's date
   - `post_count`: 7

5. **Generate Ideas** (HTTP Request → Claude API)
   ```
   POST https://api.anthropic.com/v1/messages
   Model: claude-sonnet-4-20250514
   System: "You are a social media strategist for Syntharra, an AI receptionist
   company for HVAC businesses. Generate content in JSON format only."
   
   Prompt: "Generate {{post_count}} content ideas for HVAC business owners
   about AI receptionist pain points.
   
   Context from last week's performance:
   {{weekly_pattern_brief}}
   
   Rules:
   - Rotate through these pillars: missed_calls_cost, after_hours, admin_inefficiency,
     ai_vs_receptionist, follow_up_problem, demo_call, ad_spend_waste, hvac_specific
   - Rotate hook styles: stat, story, question, bold_claim — never same twice in a row
   - Mix formats: at least 4 faceless_video, 2 static_image, 1 text_post
   - Every third idea should reference the demo call (+1 812 994 4371)
   
   Return JSON array: [{title, content_pillar, format_type, hook_style, platform}]"
   ```

6. **Parse + Write Ideas** (Code Node + Supabase)
   - Parse Claude JSON response
   - Loop: INSERT each idea into `content_ideas` with `week_of` + `vertical`

7. **Generate Scripts** (HTTP Request → Claude API, loop per idea)
   ```
   For each idea:
   
   "Write a complete social media script for this HVAC AI receptionist video:
   Title: {{title}}
   Pillar: {{content_pillar}}
   Hook style: {{hook_style}}
   
   Return JSON with:
   - hook (first 3 seconds — must stop the scroll)
   - body (15–40 seconds spoken at normal pace)
   - cta (must use one of: Comment DEMO / Link in bio / Call +1 812 994 4371)
   - caption_raw (full caption with hashtags, under 150 words)
   - caption_facebook (conversational, slightly longer)
   - caption_tiktok (punchy, under 100 chars + hashtags)
   - caption_youtube (SEO-friendly, 1 sentence)
   - caption_instagram (same as tiktok)"
   ```

8. **Write Scripts to Supabase** (Supabase)
   - INSERT into `content_scripts` with `idea_id` FK

9. **Generate Videos via Blotato** (HTTP Request, loop per video script)
   - Only for `format_type = 'faceless_video'`
   - POST to Blotato video API with script body + voice + model settings
   - Store `blotato_video_id` in `content_scripts`

10. **Poll Blotato for Completion** (Loop + Wait)
    - Every 5 minutes check if video is ready
    - Max wait: 30 minutes
    - On success: update `content_scripts.video_url` + status = 'ready'

11. **Schedule Posts via Blotato** (HTTP Request, loop per ready script)
    - For each platform (Facebook, TikTok, YouTube, Instagram):
      - POST to Blotato publish endpoint with platform-specific caption
      - Set `scheduledTime` = spread across Tue–Sat, optimal posting times
      - Facebook: 7pm EST | TikTok: 6pm EST | YouTube: 9am EST | Instagram: 12pm EST
    - INSERT into `content_posts` with UTM parameters

12. **Notify Dan** (SMTP2GO Email)
    - Subject: "This week's content is scheduled ✅"
    - Body: list of 7 titles, platforms, scheduled times, credit usage estimate

---

## WORKFLOW 2 — Organic Performance Feedback Loop
**Name:** `Social - Performance Analysis`
**Schedule:** CRON — Sunday 11:00pm EST
**Phase:** 1+

### Steps

1. **CRON Trigger** — Every Sunday 11:00pm

2. **Get All Posts from Past 7 Days** (Supabase)
   - Query `content_posts` WHERE `posted_at > NOW() - INTERVAL '7 days'`
   - AND `status = 'posted'`

3. **Pull Facebook Metrics** (HTTP Request → Meta Graph API)
   ```
   For each Facebook post_id:
   GET /{{fb_post_id}}/insights?metric=post_impressions,post_engaged_users,
       post_clicks,post_video_avg_time_watched,post_video_complete_views_organic
   Headers: Authorization: Bearer {{page_access_token}}
   ```

4. **Pull TikTok Metrics** (HTTP Request → TikTok API)
   ```
   POST https://business-api.tiktok.com/open_api/v1.3/video/list/
   Body: { "advertiser_id": "{{tiktok_advertiser_id}}", 
           "video_ids": [{{list_of_video_ids}}] }
   ```

5. **Write Metrics to Supabase** (Supabase, loop)
   - UPSERT into `content_performance` per post per platform

6. **Analyse Performance** (HTTP Request → Claude API)
   ```
   "Analyse these 7 posts from this week for a HVAC AI receptionist company.
   
   Posts data: {{json_of_posts_with_metrics}}
   
   Identify:
   1. Best performing hook style (stat/story/question/bold_claim) — by link_clicks
   2. Best performing content pillar — by watch_time_pct
   3. Best performing format — by overall engagement
   4. Best platform this week
   5. Any post that significantly outperformed others — what made it work?
   6. Revenue-generating angles (if attributed_revenue > 0)
   
   Then write a content brief for next Monday's generation. Be specific.
   Tell it exactly what angles, hooks, and formats to prioritise.
   
   Return JSON: {winning_hook_style, winning_pillar, winning_format,
   winning_platform, top_post_id, brief_for_next_week, raw_reasoning}"
   ```

7. **Write Pattern to Supabase** (Supabase)
   - INSERT into `content_patterns` with analysis output

8. **Send Weekly Summary** (SMTP2GO)
   - Subject: "Weekly Content Report — w/e {{date}}"
   - Top 3 posts with metrics
   - Claude's key recommendations
   - What Loop 1 will prioritise next week

---

## WORKFLOW 3 — Auto-Boost Winners (Phase 2)
**Name:** `Social - Auto Boost`
**Schedule:** CRON — Every 48 hours, 9:00am EST
**Phase:** 2+

### Steps

1. **CRON Trigger** — Every 48 hours

2. **Get Recent Posts with High Performance** (Supabase)
   ```sql
   SELECT cp.*, cpp.watch_time_pct, cpp.link_clicks, cpp.views
   FROM content_posts cp
   JOIN content_performance cpp ON cpp.post_id = cp.id
   WHERE cp.posted_at > NOW() - INTERVAL '7 days'
   AND cp.platform = 'facebook'
   AND cp.status = 'posted'  -- not already boosted
   AND cpp.watch_time_pct > 60
   AND cpp.link_clicks > 10
   AND cp.id NOT IN (SELECT post_id FROM content_ads WHERE post_id IS NOT NULL)
   ```

3. **Check Total Active Ad Spend** (Meta Marketing API)
   - GET all active ads
   - Sum daily budgets
   - IF total >= $50/day → skip (safety cap reached)

4. **Create Ad from Post** (HTTP Request → Meta Marketing API)
   ```
   POST /act_{{ad_account_id}}/ads
   {
     "name": "Boost - {{post_title}} - {{date}}",
     "adset_id": "{{hvac_cold_adset_id}}",  // pre-created adset targeting HVAC owners
     "creative": { "object_story_id": "{{page_id}}_{{fb_post_id}}" },
     "status": "ACTIVE",
     "daily_budget": 1000  // $10.00 in cents
   }
   ```

5. **Log to Supabase** (Supabase)
   - INSERT into `content_ads` with meta_ad_id, post_id, daily_budget=10

6. **Log Decision** (Supabase)
   - INSERT into `loop_decisions`: decision_type='boost_organic', reasoning='Exceeded threshold: watch_time>60%, link_clicks>10'

7. **Notify Dan** (SMTP2GO)
   - "Post '[title]' was auto-boosted at $10/day. Check in 5 days."

---

## WORKFLOW 4 — Ad Scale/Pause Engine (Phase 2)
**Name:** `Social - Ad Optimiser`
**Schedule:** CRON — Every 24 hours, 6:00am EST
**Phase:** 2+

### Steps

1. **CRON Trigger** — Every 24 hours

2. **Get All Active Ads** (Supabase)
   - SELECT from `content_ads` WHERE `status = 'active'`

3. **Pull Ad Metrics** (HTTP Request → Meta Marketing API)
   ```
   GET /act_{{ad_account_id}}/insights
   ?fields=ad_id,spend,impressions,clicks,cpc,ctr,actions
   &date_preset=last_7d
   ```

4. **Calculate Days Running** (Code Node)
   - For each ad: `days_running = NOW() - created_at`
   - Only process ads with `days_running >= 3` (minimum data window)

5. **Analyse Each Ad** (HTTP Request → Claude API)
   ```
   "You are a performance marketing analyst for Syntharra (HVAC AI receptionist).
   
   For each of these Facebook ads, recommend SCALE, PAUSE, or HOLD.
   
   Benchmarks:
   - Good CPC: under $1.50 | Bad CPC: over $3.00
   - Good CTR: above 3% | Bad CTR: under 1%
   - Minimum run time before decision: 3 days
   - Never scale an ad running less than 3 days
   
   Ads data: {{json_of_ads_with_metrics}}
   
   Return JSON array: [{ad_id, recommendation, reasoning, confidence_score}]"
   ```

6. **Execute Decisions** (Switch Node → HTTP Request)
   - **SCALE:** `POST /{{meta_ad_id}}` `{"daily_budget": {{current_budget * 1.5}}}`
   - **PAUSE:** `POST /{{meta_ad_id}}` `{"status": "PAUSED"}`
   - **HOLD:** No API call

7. **Update Supabase** (Supabase, loop)
   - UPDATE `content_ads` status, budget, last_scaled_at/last_paused_at
   - INSERT into `loop_decisions` for every SCALE/PAUSE decision

8. **Weekly Digest** (SMTP2GO, only on Sundays)
   - Summary of all decisions from past 7 days
   - Top performing ad + attributed bookings
   - Total spend vs attributed revenue

---

## WORKFLOW 5 — Revenue Attribution + Cross-Platform Learning
**Name:** `Social - Revenue Attribution`
**Schedule:** CRON — Monday 6:00am EST (runs before Loop 1)
**Phase:** 2+

### Steps

1. **CRON Trigger** — Monday 6:00am

2. **Get Recent Stripe Payments** (HTTP Request → Stripe API)
   ```
   GET https://api.stripe.com/v1/checkout/sessions
   ?created[gte]={{7_days_ago_unix}}&limit=100
   Headers: Authorization: Bearer {{stripe_secret_key}}
   ```

3. **Match Payments to Leads** (Supabase, loop)
   ```sql
   SELECT * FROM website_leads
   WHERE email = '{{customer_email}}'
   AND utm_content IS NOT NULL
   ORDER BY created_at DESC LIMIT 1
   ```

4. **Attribute Revenue to Content Posts** (Supabase, loop)
   ```sql
   UPDATE content_performance
   SET attributed_revenue = attributed_revenue + {{payment_amount}}
   WHERE post_id = (
     SELECT id FROM content_posts WHERE utm_content = '{{utm_content}}'
   )
   ```

5. **Identify Revenue-Generating Angles** (Supabase query)
   ```sql
   SELECT cp.utm_content, cs.hook, ci.content_pillar, ci.hook_style,
          SUM(cperf.attributed_revenue) as total_revenue
   FROM content_posts cp
   JOIN content_scripts cs ON cs.id = cp.script_id
   JOIN content_ideas ci ON ci.id = cs.idea_id
   JOIN content_performance cperf ON cperf.post_id = cp.id
   WHERE cperf.attributed_revenue > 0
   AND cp.posted_at > NOW() - INTERVAL '30 days'
   GROUP BY cp.utm_content, cs.hook, ci.content_pillar, ci.hook_style
   ORDER BY total_revenue DESC
   ```

6. **Generate Revenue-Informed Brief** (HTTP Request → Claude API)
   ```
   "These content pieces generated real Stripe revenue in the past 30 days:
   {{revenue_attributed_content}}
   
   Identify the exact pattern: hook style, content angle, CTA used.
   Write a specific instruction for next week's content generation loop
   to create 3 more scripts using this exact pattern.
   Be specific — name the angle, describe the hook formula, suggest scenarios."
   ```

7. **Update content_patterns** (Supabase)
   - UPDATE this week's pattern record with `revenue_attributed_angle`
   - This gets picked up by Loop 1 at 7am

8. **Notify Dan** (SMTP2GO)
   - "Revenue attribution complete. [X] payments matched to content.
     Top-performing angle: [angle]. Loop 1 will prioritise this today."

---

## WORKFLOW 6 — Comment-to-DM (Phase 1, via Spur webhook)
**Name:** `Social - Comment DM Handler`
**Trigger:** Webhook from Spur when "DEMO" comment detected
**Phase:** 1+

### Steps

1. **Webhook Trigger** — POST from Spur
   - Payload includes: commenter_name, commenter_id, platform, post_id, comment_text

2. **Check for Duplicate** (Supabase)
   - Has this commenter_id already received a DM this week?
   - If yes: skip (prevent spam)

3. **Log to website_leads** (Supabase)
   - INSERT: source='comment_dm', platform, name, utm_source=platform

4. **Score Lead** (HTTP Request → Claude API)
   - Quick 1–5 score based on available context (platform, post they commented on)
   - High score: add to hot lead queue

5. **Trigger Spur DM** (HTTP Request → Spur API)
   - Send the pre-written DM template with commenter's name + Cal.com link

6. **Schedule Follow-up Check** (n8n Wait node — 48hrs)
   - After 48hrs: check if lead booked via Cal.com
   - If not: send one follow-up DM (once only)

---

## WORKFLOW 7 — Facebook Lead Ad Handler (Phase 2)
**Name:** `Social - Lead Ad Capture`
**Trigger:** Facebook Lead Ads Trigger node (native n8n)
**Phase:** 2+

### Steps

1. **Facebook Lead Ads Trigger** — fires on every form submission

2. **Extract Lead Data** (Set Node)
   - name, email, phone, form answers (call_volume, current_service)

3. **Score Lead** (HTTP Request → Claude API)
   - Prompt: "Score this HVAC business lead 1–10.
     Call volume: {{call_volume}}. Currently using answering service: {{current_service}}.
     10 = high call volume, no current service. 1 = low volume, already covered.
     Return JSON: {score, reasoning}"

4. **Route by Score** (Switch Node)
   - Score 7–10: HOT → Step 5a
   - Score 4–6: WARM → Step 5b
   - Score 1–3: COLD → Step 5c

5a. **HOT Lead Flow**
   - INSERT into `website_leads` with score + source='fb_lead_ad'
   - Telnyx SMS to Dan: "🔥 Hot lead: [name], [phone], [call_volume] calls/day"
   - SMTP2GO email to lead: immediate personal-feeling email + Cal.com link
   - Notify hot lead detector (existing workflow)

5b. **WARM Lead Flow**
   - INSERT into `website_leads`
   - Enter 3-email SMTP2GO nurture sequence (same as lead magnet sequence)

5c. **COLD Lead Flow**
   - INSERT into `website_leads` with score + tag 'cold'
   - No immediate follow-up — enters monthly re-engagement list

---

## NAMING CONVENTIONS

All workflow names prefixed `Social -` for easy filtering in n8n dashboard.
All webhook URLs: `https://n8n.syntharra.com/webhook/social-[name]`

## ADDING A NEW VERTICAL

In Workflow 1, Step 4 (Set Parameters):
- Duplicate the Set node
- Change `industry` to "Electrical" or "Plumbing"
- Change `vertical` to "electrical" or "plumbing"
- Update Blotato brand_kit_id in Step 9
- Update social account IDs in Step 11
- All other logic is identical — no rebuild needed
