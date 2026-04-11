# Syntharra Website — Design System Source of Truth

> Auto-generated from brand standard + current live site (syntharra.com, April 2026).
> Use this file as the DESIGN SYSTEM block in all Stitch prompts for this project.

---

## Identity

**Product:** Syntharra — AI Receptionist for HVAC & Trade Businesses  
**Audience:** HVAC contractors, plumbers, electricians — owner-operated trade businesses  
**Tone:** Confident, direct, business-results-first. No fluff. Think Stripe meets a trade contractor.  
**Vibe:** Sophisticated tech startup with blue-collar grit. Premium but approachable.

---

## Color Palette

| Role | Name | Hex |
|:---|:---|:---|
| Primary Accent / Brand | Syntharra Violet | `#6C63FF` |
| Primary Accent Hover | Violet Deep | `#5A52E0` |
| Primary Accent Light | Violet Soft | `#8B85FF` |
| Secondary Accent | Cyan Spark | `#00D4FF` |
| Page Background | Cloud White | `#FAFAFA` |
| Card / Surface | Pure White | `#FFFFFF` |
| Light Section Background | Mist | `#F7F7FB` |
| Heading Text | Deep Navy | `#1A1A2E` |
| Body Text | Slate | `#4A4A6A` |
| Muted / Meta Text | Ash | `#8A8AA0` |
| Border / Divider | Feather | `#E5E7EB` |
| Success / Live | Emerald | `#10B981` |
| Dark Section Background | Near Black | `#0c0c1d` |
| Dark Section Gradient | Dark Gradient | `linear-gradient(135deg, #0d0d1a, #1a1a3e)` |

---

## Typography

| Role | Font | Weight | Size |
|:---|:---|:---|:---|
| Display / Hero Headlines | Bricolage Grotesque | 800 | clamp(52px, 6.5vw, 100px) |
| Section Headlines | Bricolage Grotesque | 700–800 | 40–56px |
| Body / UI Text | DM Sans | 300–600 | 14–20px |
| Nav Labels | DM Sans | 500 | 14px |
| Eyebrow Tags | DM Sans | 600 | 11px, letter-spacing 1.4px, ALL CAPS |
| Monospace (live timer) | JetBrains Mono | 600 | 13px |

---

## Component Styles

### Buttons
- **Primary CTA:** Syntharra Violet `#6C63FF` fill, white text, `border-radius: 12px`, padding `16px 34px`, box-shadow `0 4px 24px rgba(108,99,255,.4)`, hover lifts 2px
- **Ghost / Secondary:** Transparent with 1px `rgba(255,255,255,.12)` border on dark, 1px `#E5E7EB` on light, `border-radius: 12px`
- **Nav CTA:** Same violet fill, smaller `10px 22px` padding, `border-radius: 10px`

### Cards
- Background: `#FFFFFF`, `border-radius: 24–32px`, border `1px solid #E5E7EB`
- Elevation: `box-shadow: 0 8px 32px rgba(14,14,26,.08)` (whisper-soft)
- Featured cards: dark background `#06060d`, white text, violet accent glow

### Navigation
- Sticky top nav, `height: 68px`, starts transparent over dark hero
- Scrolled state: glassmorphism — `rgba(255,255,255,.92)` + `backdrop-filter: blur(20px)`
- Logo: 4 ascending violet bars + "Syntharra" wordmark in Bricolage Grotesque 800

### Tags / Pills
- Eyebrow: `font-size: 11px`, `font-weight: 600`, all-caps, letter-spaced, violet or green accent, pill-shaped with matching tinted border

### Badges / Floating Callouts
- White background, `border-radius: 14–16px`, `box-shadow: 0 20px 40px -16px rgba(14,14,26,.18)`, floating animation `translateY(-8px)` on a 5s ease loop

---

## Layout

- **Max content width:** 1280–1560px, centered, `padding: 0 48px`
- **Grid:** Predominantly 2-column asymmetric (`1.05fr .95fr`) for hero; 3–4 column for features
- **Spacing rhythm:** Sections separated by `80–100px` padding
- **Diagonal transitions:** `clip-path: polygon(0 0,100% 0,100% calc(100% - 80px),0 100%)` used for hero-to-content edge

---

## Page Structure (Current Homepage)

1. **Sticky Nav** — Logo + links + "Book Demo" violet CTA
2. **Hero** — Light `#FAFAFA` background, Inter 800 headline, violet gradient em, 2-col grid with phone mockup right
3. **Stats Strip** — White bg, 4 large stats with bold numbers
4. **How It Works** — 3 staggered steps, dark/light alternating, scroll-triggered reveals
5. **Bento Features Grid** — 5-cell bento: 2 dark tall cards + 3 light cards with icons/charts
6. **Industries** — Curved section break, HVAC/plumbing/electrical/etc. icon cards, dark bg
7. **Testimonials** — 1 large featured dark card (left) + 2 mini cards stacked (right), animated gradient border on featured
8. **CTA Block** — Full-width violet gradient `#6C63FF → #8B85FF`, white text, 36px rounded, centered CTA
9. **Footer** — Dark `#0c0c1d`, 3-col links, logo, tagline "AI Receptionists · Built for the Trades · Available 24/7"

---

## Animations

- **Scroll reveals:** `opacity 0→1 + translateY(32px)→0`, `0.9s cubic-bezier(.16,1,.3,1)`, staggered 70ms delay steps
- **Floating badges:** `translateY(0→-8px)` on 5s ease-in-out infinite loop
- **Live pulse:** Green dot `scale 1→1.5, opacity 1→0` ring animation, 1.8s
- **Social proof toast:** Bottom-right, slides up + fades in, cycles every ~5s
- **Scroll progress bar:** Thin `2px` violet-to-cyan gradient at top of viewport
- **Cursor glow:** 600px radial gradient follows mouse in hero section only

---

## Do Not

- Never use Arial, Roboto, or system fonts for headings
- Never use flat purple-on-white without Bricolage Grotesque — it looks generic
- Never remove the scroll reveal animations — they're core to the premium feel
- Never use more than 2 accent colors in the same section
- Always keep the phone mockup in the hero — it's the primary trust signal
