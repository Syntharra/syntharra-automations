# YouTube Learning Skill
# Syntharra — Agentic Marketing Intelligence
# Trigger: User provides a YouTube URL with intent to learn from it

## What This Skill Does

Takes any YouTube URL, extracts the full transcript, synthesises a structured learnings
report, stores it as permanent marketing intelligence in GitHub, and immediately
implements all Quick Win takeaways via the relevant Syntharra marketing skills.
Major strategy changes are flagged for Dan's approval before anything is touched.

---

## Step 1 — Extract Transcript

Install and run youtube-transcript-api via Python executor:

```python
import subprocess
subprocess.run(["pip", "install", "youtube-transcript-api", "--break-system-packages", "-q"], check=True)

from youtube_transcript_api import YouTubeTranscriptApi
import re

def extract_video_id(url):
    patterns = [
        r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

url = "YOUTUBE_URL_HERE"
video_id = extract_video_id(url)

try:
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    full_text = " ".join([t["text"] for t in transcript_list])
    print(f"Transcript length: {len(full_text)} chars")
    print(full_text[:500])  # preview
except Exception as e:
    print(f"Error: {e}")
    # Fallback: try fetching auto-generated captions
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        for t in transcripts:
            transcript_list = t.fetch()
            full_text = " ".join([item["text"] for item in transcript_list])
            print(f"Got transcript via: {t.language_code}")
            break
    except Exception as e2:
        print(f"All transcript methods failed: {e2}")
```

If transcript extraction fails entirely, use Claude in Chrome to navigate to the video
and manually read visible captions or description, then proceed with what's available.

---

## Step 2 — Synthesise Report

Use the transcript to generate the following structured report. Keep it tight —
the purpose is actionable intelligence, not a wall of text.

### Report Template

```markdown
# 📺 YouTube Learning Report
**Video**: [Title]
**Channel**: [Channel Name]
**URL**: [URL]
**Date Processed**: [YYYY-MM-DD]
**Topic Category**: [Content Marketing / Paid Ads / SEO / Cold Outreach / Sales / Brand / General Business / Other]

---

## TL;DR
[2–3 sentence summary of the core message]

---

## Key Learnings
[Max 7 numbered points. Each learning = 1–2 sentences. Be specific, not vague.]

1.
2.
3.
...

---

## Syntharra Applications
[For each key learning above, map it to a specific Syntharra context]

| # | Learning | Syntharra Application | Area |
|---|---|---|---|
| 1 | [brief] | [specific application for HVAC AI receptionist marketing] | [Content / Ads / Email / SEO / Social / Brand] |
...

---

## Implementation Plan

### ✅ Quick Wins (Implement Now — No Approval Needed)
[Small tests, new angles, format experiments, copy tweaks, new content ideas]

| Action | Skill to Use | Estimated Impact |
|---|---|---|
| [specific action] | [syntharra-marketing:content-engine / outreach / etc] | [Low/Med/High] |

### 🔐 Requires Dan's Approval
[Major pivots only — channel strategy, pricing, brand voice, killing something, budget reallocation]

| Proposed Change | Why | Risk Level |
|---|---|---|
| [change] | [rationale from video] | [Low/Med/High] |

---

## Confidence Score
How relevant is this video to Syntharra's current stage? [1–10] — [brief reason]

---

## Source Notes
[Any caveats about the content — is the creator credible? Is this B2C advice being applied to B2B? Trade-specific nuances?]
```

---

## Step 3 — Save to GitHub

Push the completed report to the syntharra-automations repo:

**Path**: `docs/marketing-learnings/YYYY-MM-DD-{slug}.md`
**Slug**: lowercase, hyphens, derived from video title (max 50 chars)

Also update the index file at `docs/marketing-learnings/INDEX.md`:
- Append a new row: `| YYYY-MM-DD | [Title] | [Category] | [Quick Win count] | [Link] |`
- If INDEX.md doesn't exist, create it with the header first

Use GitHub MCP:
```
mcp__562ca274-ff68-4873-8410-8ecc5c606bd6__create_or_update_file
repo: syntharra-automations
org: Syntharra
```

---

## Step 4 — Implement Quick Wins

For each Quick Win in the report, spawn parallel agents:

**Routing logic:**
| Action type | Skill to invoke |
|---|---|
| New blog post angle / article | `syntharra-marketing:content-engine` |
| Social media post / hook test | `syntharra-marketing:content-engine` |
| Cold email subject line / copy tweak | `syntharra-marketing:outreach` |
| Short-form video hook or script | `syntharra-marketing:video-content` |
| Competitor positioning insight | `syntharra-marketing:competitor-watch` |
| Conversion / landing page angle | `syntharra-marketing:conversion-optimizer` |
| Prospect targeting angle | `syntharra-marketing:prospector` |
| General intelligence / strategy note | Log to `docs/MARKETING.md` on GitHub |

Spawn all Quick Win agents in parallel. Each agent receives:
1. The specific action from the Quick Win table
2. The relevant learning excerpt from the report
3. The Syntharra context (HVAC AI receptionist, pre-launch, US market)

Document what each agent produced in a short implementation log appended to the report.

---

## Step 5 — Present to Dan

After all parallel agents complete:

1. **Show the report** (inline or link to GitHub file)
2. **List what was implemented** — one bullet per Quick Win, what was created/changed
3. **Flag approval items** clearly — present each one with the proposed change, rationale, and your recommendation
4. Ask: "Approve any of these?" — Dan replies with numbers or "all" or "none"

Once Dan approves an item, immediately route it to the relevant marketing skill.

---

## Approval Gate — What Requires Dan's Sign-Off

**Always require approval:**
- Changing pricing strategy or packaging ($497/$997 tiers)
- Abandoning or adding a major marketing channel (e.g., "stop cold email, start YouTube ads")
- Brand voice or positioning shifts
- Changing ad spend strategy or targeting fundamentals
- Overhauling existing email sequences
- Anything touching the product offering or demo flow
- Changing the ICP definition

**Never needs approval (implement immediately):**
- New blog post topics or angles
- New social post hooks or formats
- A/B test ideas for subject lines
- New cold email opening line variations
- Adding a content angle to an existing sequence
- Short-form video script ideas
- New content calendar items
- Competitor monitoring additions
- SEO keyword opportunities
- New ad headline variations to test

---

## Agentic Learning Loop

Every report saved to GitHub is permanent memory for the marketing agents.
Before any major marketing task, agents should check `docs/marketing-learnings/INDEX.md`
for relevant prior learnings and apply them.

This is the mechanism by which the Syntharra marketing system teaches itself
from external knowledge continuously. Over time, the learnings directory becomes
the strategic brain behind every campaign decision.

---

## Error Handling

| Problem | Action |
|---|---|
| Transcript unavailable (private/restricted video) | Ask Dan to provide transcript manually, or use Chrome MCP to read description + comments |
| Video is non-English | Attempt auto-translated transcript; note translation quality in Source Notes |
| Video is very long (>2 hours) | Process in chunks; summarise each chunk, then meta-summarise |
| Skill invocation fails | Log the failure, continue with other Quick Wins, flag the failed one for manual follow-up |
| GitHub push fails | Save report to Cowork workspace as fallback, note the push failure |

---

## Usage Examples

```
"Learn from this: https://youtube.com/watch?v=xxx"
"Extract key points from [YouTube URL]"
"Watch this and implement anything useful: [URL]"
"What can we learn from this video for our marketing: [URL]"
```
