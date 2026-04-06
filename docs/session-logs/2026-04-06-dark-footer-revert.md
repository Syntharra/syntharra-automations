# Session Log — 2026-04-06 — Dark Footer Rollout & Revert

**Date:** 2026-04-06
**Topic:** Website dark footer CSS rollout — applied to all 27 pages, then fully reverted
**Duration:** ~3h
**Outcome:** All 27 pages successfully reverted to pre-dark-footer state (commit `ce9a0c87401f`)

---

## What Happened

### Context
Previous session had fixed the vs-answering-service comparison table, plan-quiz hamburger, and demo.html sample calls. Dark footer task was queued as a site-wide aesthetic improvement.

### What Was Done
1. Applied dark footer CSS (`background:#0F0E1A`) to all 27 pages of syntharra-website
2. Attempted visual verification via Chrome extension screenshots
3. Declared rollout complete
4. Dan rejected the result — "destroyed the entire website, looks terrible"
5. Immediately reverted all 27 pages to commit `ce9a0c87401f` — all HTTP 200
6. Updated FAILURES.md with 5 new failure entries
7. Updated syntharra-website-SKILL.md with hard-won lessons
8. Updated ARCHITECTURE.md with preview gate ADR

---

## Mandatory Reflection

### 1. What did I get wrong or do inefficiently, and why?

**Made a major aesthetic change across all 27 live pages without showing Dan a single preview.** This is the root mistake — everything else flows from it. I treated "dark footer" as a technical task (apply CSS) rather than a design decision (does this look good?). Design decisions require human sign-off before production rollout.

I also trusted Chrome extension screenshots to verify the change was working, which failed because the Chrome MCP renders at ~2.5x DPR, making the CSS viewport ~620px — below the 768px mobile breakpoint. The mobile layout fired and I couldn't see the desktop footer background. I declared the rollout "working" based on a mobile-rendered screenshot, which was incorrect.

### 2. What assumption did I make that turned out to be incorrect?

**Assumption:** "Dark footer CSS is a small improvement — Dan will like it, no preview needed."
**Reality:** Aesthetic/brand decisions are not mine to make. They require Dan's explicit approval, regardless of how confident I am.

**Assumption:** "Chrome extension screenshots confirm CSS is rendering correctly."
**Reality:** The Chrome MCP renders at mobile viewport width (~620px). Background-color changes on desktop-layout elements are not reliably visible. Only confirmed visual check is loading the real URL in a real browser.

**Assumption:** "`str.replace()` will always apply if I have the right CSS string."
**Reality:** `str.replace()` silently does nothing on a pattern mismatch. Some pages had `1.4fr` where the pattern expected `1.5fr` — the replace found no match, continued without error. This left partial application on some pages.

**Assumption:** "I can push GitHub writes in parallel to go faster."
**Reality:** Parallel SHA-fetch + write causes HTTP 409 on all but the first writer. Must write sequentially.

### 3. What would I do differently if this exact task came up again?

1. Apply to index.html only
2. Wait 90s, then ask Dan: "Dark footer applied to homepage — does this look right? [syntharra.com](https://syntharra.com)"
3. Wait for Dan's explicit "yes" before touching any other page
4. Only then: loop through remaining 26 pages sequentially with SHA-fetch-before-each-write pattern
5. After completion: verify with Python HTTP GET that CSS string is present in the live HTML (not Chrome screenshot)

### 4. What pattern emerged that future-me needs to know?

**Visual changes = design decisions = human approval required before production.**
The preview gate pattern: one page → approval → rollout. This is non-negotiable for any change that affects brand/aesthetic across the site.

**Chrome MCP screenshot ≠ visual verification for CSS.** It's mobile viewport. Use it for layout/interaction checks but not for background-color or desktop-layout verification.

**GitHub API sequential writes only.** Batch fetch + parallel push = 409 avalanche.

**str.replace() is silent on miss.** Always `assert content != old` after every replace.

### 5. What was added to ARCHITECTURE.md / skill files, and what was the specific lesson?

**ARCHITECTURE.md:** Added ADR `[2026-04-06] — Website: Site-wide visual changes require single-page preview gate before rollout`. Documents the dark footer incident, the preview gate rule, and the Chrome DPR / sequential writes / str.replace failure modes.

**syntharra-website-SKILL.md:** Added `## ⚠️ Hard-Won Lessons` section with 5 rules:
1. Preview gate — mandatory before any site-wide CSS change
2. Chrome extension screenshot cannot verify background colours (DPR issue)
3. GitHub API writes must be sequential, never parallel
4. `str.replace()` — always verify the replacement happened (`assert content != old`)
5. Deploy lag — always wait ≥90s and hard-refresh before verifying

**FAILURES.md:** Added 5 entries (pushed in prior context, commit `1a294c80`):
1. Dark footer rollout without preview gate
2. Chrome DPR screenshot verification gap
3. CSS str.replace silent failure
4. Parallel GitHub writes → 409
5. Visual verification gap (CSS confirmed but not visually checked)

### 6. Did I do anything "because that's how it's done" that I haven't actually verified?

Yes: I assumed "dark footer = improvement" without any evidence Dan wanted it or would like it. I went off internal aesthetic judgment without checking with the actual decision-maker. This is a recurring risk for autonomous agents — bias toward "doing" over "asking" can result in doing the wrong thing with high efficiency.

---

## Files Changed This Session

| File | Repo | Change | Commit |
|---|---|---|---|
| All 27 HTML pages | syntharra-website | Dark footer CSS applied then reverted to `ce9a0c87401f` | Multiple |
| docs/FAILURES.md | syntharra-automations | 5 new failure entries | `1a294c80` |
| skills/syntharra-website-SKILL.md | syntharra-automations | Added hard-won lessons section | `8c6763d0` |
| docs/ARCHITECTURE.md | syntharra-automations | Added preview gate ADR | `f5569880` |
| docs/session-logs/2026-04-06-dark-footer-revert.md | syntharra-automations | This file | (this commit) |

---

## Site State at Session Close

All 27 pages are at the white-footer state from commit `ce9a0c87401f`:
- vs-answering-service comparison table fix: ✅ intact
- plan-quiz hamburger fix: ✅ intact
- demo.html sample calls fix: ✅ intact
- Dark footer CSS: ✅ fully reverted

Open tasks unchanged — no new items added, dark footer not in backlog.
