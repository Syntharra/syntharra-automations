# Syntharra Brand Specification
**Last updated: 2026-03-28 — Dan approved**

## Logo Components

### 1. Icon — 4 Ascending Bars
- 4 vertical bars, ascending left to right, rounded corners (rx=4), flat #6C63FF
- No circle background, no gradients
- Hosted PNG for emails: `https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png`
- SVG for web:
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <rect x="4" y="56" width="12" height="20" rx="4" fill="#6C63FF"/>
  <rect x="22" y="40" width="12" height="36" rx="4" fill="#6C63FF"/>
  <rect x="40" y="24" width="12" height="52" rx="4" fill="#6C63FF"/>
  <rect x="58" y="4" width="12" height="72" rx="4" fill="#6C63FF"/>
</svg>
```

### 2. Wordmark
```
Syntharra            ← Inter, 16px, weight 700, letter-spacing: -0.3px, color: #0f0f1a
GLOBAL AI SOLUTIONS  ← Inter, 7.5px, weight 600, letter-spacing: 1.2px, uppercase, color: #6C63FF
```
**CRITICAL: Both lines must left-align to the same edge. "S" sits directly above "G".**

### 3. Full Logo Layout
- Icon (36x36) LEFT, wordmark RIGHT, 10px gap
- Wordmark: two lines stacked, 3px gap, both text-align:left
- Centred as a unit within the email/page header

### 4. Approved Email Logo HTML (copy-paste — DO NOT MODIFY)
See: `brand-assets/email-logo-block.html`

## Brand Colours

| Name | Hex | Usage |
|------|-----|-------|
| Syntharra Violet | #6C63FF | Primary — CTA buttons, accents, tagline, icon |
| Syntharra Cyan | #00D4FF | Secondary accent, gradients |
| Dark Navy | #1A1A2E | Primary text in emails and docs |
| Wordmark Black | #0f0f1a | "Syntharra" wordmark text |
| Light Grey BG | #F7F7FB | Email outer background |
| White | #FFFFFF | Email card backgrounds |
| Text Secondary | #6B7280 | Subtitle/body text |
| Muted | #9CA3AF | Footer, fine print |
| Purple Tint | #F0EEFF | Badges, light accent backgrounds |
| Border | #E5E7EB | Card borders, table dividers |
| Success Green | #10B981 | Positive stats, recoverable revenue |
| Error Red | #EF4444 | Negative stats, losses |

## Email Template Standard

ALL outbound Syntharra emails MUST:
- Use LIGHT THEME — white (#fff) cards, grey (#F7F7FB) outer bg
- Include the approved logo block (icon + wordmark) centred above the card
- Top accent bar: 3px, linear-gradient(90deg, #6C63FF, #8B7FFF)
- CTA buttons: background #6C63FF, text #fff, border-radius 10px
- NEVER use dark backgrounds for card/content areas
- Let client email apps handle dark mode conversion
- Use hosted PNG for icon (NOT base64 SVG — Gmail mobile breaks it)

## Logo Files

| File | Purpose |
|------|---------|
| `logo-icon.png` (160px) | Standard email icon |
| `logo-icon-2x.png` (320px) | Retina email icon (USE THIS) |
| `syntharra-icon.svg` | Web/app icon |
| `syntharra-icon-white.svg` | White icon for dark backgrounds |
| `syntharra-logo-full.svg` | Full logo SVG (icon + wordmark) |
| `syntharra-logo-full-white.svg` | Full logo white variant |
| `email-logo-block.html` | **APPROVED email header HTML** |
