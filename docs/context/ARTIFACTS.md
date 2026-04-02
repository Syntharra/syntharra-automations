# Syntharra — Artifacts
> Load when: working on Claude chat artifacts, email previews, brand visuals

## Repo: `Syntharra/syntharra-artifacts`
Artifacts are React JSX files rendered live in Claude chat.
To load one: fetch the file, paste into chat, Claude renders it.
To edit: say "Edit [filename] — [change]" and Claude fetches, edits, pushes.
Commit format: `artifact(filename): description`

## File Map
| File | What it shows | Status |
|---|---|---|
| `brand/brand-showcase.jsx` | Colours, logo variants, typography, gradients | ✅ Done |
| `brand/signatures-viewer.jsx` | All 9 email signatures with preview | ✅ Done |
| `sales/vsl-cost-comparison.jsx` | VSL Scene 4 animated cost graphic | ✅ Done |
| `sales/roi-calculator.jsx` | Interactive ROI calculator | ✅ Done |
| `client-dashboard/client-dashboard.jsx` | Client portal (mock data — wire to Supabase) | ✅ Done |
| `emails/external/welcome-standard.jsx` | Standard welcome email with live controls | ✅ Done |
| `emails/external/welcome-premium.jsx` | Premium welcome email | 🔲 Scaffold |
| `emails/external/weekly-report.jsx` | Weekly report email with controls | ✅ Done |
| `emails/external/youre-live.jsx` | You're Live email | ✅ Done |
| `emails/internal/call-notification.jsx` | Internal call notification (all types) | ✅ Done |
| `emails/internal/hot-lead-alert.jsx` | Hot lead alert | 🔲 Scaffold |
| `admin/section-preview.jsx` | Admin dashboard section prototype | 🔲 Scaffold |
| `website/landing-section-preview.jsx` | Website section prototype | 🔲 Scaffold |

## Design Standards (all artifacts)
- Colours: `#6C63FF` violet, `#00D4FF` cyan, `#1A1A2E` text, `#F4F5F9` bg, `#fff` cards
- Font: DM Sans (import from Google Fonts in every artifact)
- Theme: LIGHT — white cards, grey outer. Never dark-theme
- Logo: 4 ascending bars in `#6C63FF` — never emoji
- Email logo: hosted PNG + Inter wordmark (see syntharra-email skill)

## Pending
- Dan to paste Syntharra brand theme factory .skill from Claude Code
- Once installed, rebuild all artifacts to match theme factory exactly
