# Syntharra Brand Specification

## Logo Components

### 1. Icon — 4 Ascending Bars
SVG (use this exact SVG everywhere):
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <rect x="4" y="56" width="12" height="20" rx="4" fill="#6C63FF"/>
  <rect x="22" y="40" width="12" height="36" rx="4" fill="#6C63FF"/>
  <rect x="40" y="24" width="12" height="52" rx="4" fill="#6C63FF"/>
  <rect x="58" y="4" width="12" height="72" rx="4" fill="#6C63FF"/>
</svg>
```
- 4 vertical bars, ascending left to right
- Rounded corners (rx="4")
- Flat fill #6C63FF (Syntharra violet)
- No circle background, no gradients
- Works on light and dark backgrounds
- White variant: same SVG with fill="#FFFFFF" (for dark backgrounds)

### 2. Wordmark — "Syntharra" + "GLOBAL AI SOLUTIONS"
```
Syntharra            ← Inter, 15px, font-weight: 700, letter-spacing: -0.02em, color: #0f0f1a
GLOBAL AI SOLUTIONS  ← Inter, 7px, font-weight: 500, letter-spacing: 0.18em, uppercase, color: #6C63FF
```

### 3. Full Logo (Icon + Wordmark side by side)
Layout: horizontal, icon left, wordmark right
Gap: 9px between icon and wordmark
Wordmark is two lines stacked (flexbox column, gap: 2px)
Icon size: 34x34px (desktop), 28x28px (mobile)

### 4. Full Logo HTML (copy-paste reference)
```html
<div style="display:flex;align-items:center;gap:9px">
  <div style="width:34px;height:34px">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
      <rect x="4" y="56" width="12" height="20" rx="4" fill="#6C63FF"/>
      <rect x="22" y="40" width="12" height="36" rx="4" fill="#6C63FF"/>
      <rect x="40" y="24" width="12" height="52" rx="4" fill="#6C63FF"/>
      <rect x="58" y="4" width="12" height="72" rx="4" fill="#6C63FF"/>
    </svg>
  </div>
  <div style="display:flex;flex-direction:column;gap:2px">
    <span style="font-family:'Inter',sans-serif;font-size:15px;font-weight:700;letter-spacing:-0.02em;color:#0f0f1a;line-height:1">Syntharra</span>
    <span style="font-family:'Inter',sans-serif;font-size:7px;font-weight:500;letter-spacing:0.18em;color:#6C63FF;text-transform:uppercase;line-height:1">Global AI Solutions</span>
  </div>
</div>
```

## Brand Colours

| Name | Hex | Usage |
|------|-----|-------|
| Syntharra Violet | #6C63FF | Primary brand, CTA buttons, accents, tagline, icon fill |
| Syntharra Cyan | #00D4FF | Secondary accent, gradients |
| Dark Navy | #1A1A2E | Primary text colour in all emails and docs |
| Dark Black | #0f0f1a | Wordmark "Syntharra" text |
| Light Grey BG | #F7F7FB | Email outer background |
| White | #FFFFFF | Email card backgrounds, content areas |
| Text Secondary | #6B7280 | Subtitle/body text in emails |
| Muted Text | #9CA3AF | Footer text, fine print |
| Purple Tint | #F0EEFF | Badges, light accent backgrounds |
| Border | #E5E7EB | Card borders, table dividers |

## Typography

| Element | Font | Weight | Size | Notes |
|---------|------|--------|------|-------|
| Wordmark "Syntharra" | Inter | 700 | 15px | letter-spacing: -0.02em |
| Tagline "GLOBAL AI SOLUTIONS" | Inter | 500 | 7px | uppercase, letter-spacing: 0.18em |
| Website headings | DM Serif Display | — | varies | Serif display font |
| Website body | DM Sans | 400-700 | varies | Clean sans-serif |
| Email body | System stack | 400-700 | 14px | -apple-system, BlinkMacSystemFont, etc. |

## Email Template Standard

ALL outbound emails from Syntharra MUST follow this light theme:
- Outer background: #F7F7FB
- Card background: #FFFFFF (white)
- Top accent bar: 3px, linear-gradient(90deg, #6C63FF, #8B7FFF)
- Text: #1A1A2E (headings), #6B7280 (body), #9CA3AF (footer)
- CTA buttons: background #6C63FF, text #FFFFFF, border-radius 10px
- Badges: #6C63FF text on #F0EEFF background
- NEVER use dark backgrounds for card content — let client email apps handle dark mode
- Logo in emails: inline SVG icon only (34x34), centred above card

## Logo Files (in this repo)

- `syntharra-icon.svg` — purple icon, transparent bg
- `syntharra-icon-white.svg` — white icon, transparent bg
- `syntharra-icon-2026-03.png` — purple icon PNG
- `favicon.svg` — website favicon (same icon)
