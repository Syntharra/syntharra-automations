# Session Log — 2026-03-30

## What changed

### syntharra-checkout / public/index.html

1. **Enterprise card added** — third column alongside Standard and Premium
   - Initial version: dark (`#0F0E1A`) with cyan accents
   - Final version: **Frosted Violet** (`#F0F0FF` bg, `#C8C2FF` border, purple accents) — chosen by Dan from 12-option preview
   - CTA: `mailto:sales@syntharra.com`

2. **Divider alignment fixed** — all 3 cards now have identical structure above the divider (badge → name → tagline → price → setup row → minutes pill → divider). Enterprise `ent-volume` pill has `margin-top:14px` to nudge it down and align the divider line across all 3 cards.

3. **Setup fee redesigned** — replaced inline text with a clean pill row: "SETUP FEE | ~~$X,XXX~~ **$X,XXX**"

4. **"Everything in Standard, plus" redesigned** — replaced plain text label with a visual callout banner (icon + bold heading + subline) inside the Premium card

5. **Page polish:**
   - Subtle dot-grid background pattern (`radial-gradient` at `28px` intervals)
   - Premium card uses linear gradient (`#7B72FF → #5A52E0`) instead of flat colour
   - Popular badge has cyan drop shadow
   - Slightly improved spacing and typography hierarchy

6. **Logo** — replaced CSS-drawn icon with inline SVG matching syntharra.com exactly (4 ascending bars, `#6C63FF`, `viewBox="0 0 80 80"`)

7. **Grid** — expanded to 3-col (`1fr 1fr 1fr`), max-width `1060px`, responsive breakpoints at 820px (2-col) and 540px (1-col)

### Root cause of "no updates showing" issue
Railway serves from `public/index.html` — NOT root `index.html`. Early edits were pushed to the wrong file. Fixed by always editing `public/index.html` and triggering manual redeploy via Railway GraphQL API when needed.

## Files changed
- `Syntharra/syntharra-checkout` → `public/index.html`
- `Syntharra/syntharra-automations` → `docs/project-state.md` (this log)

## Commits
- checkout: `b823272299675c8b4d5170b12854a8375daf1443` (final v3)
- project-state: `a5c70b8b11730d71c813403bf797dcaea4629c29`
