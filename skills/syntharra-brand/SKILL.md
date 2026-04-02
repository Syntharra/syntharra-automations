---
name: syntharra-brand
description: >
  Complete Syntharra brand standard — colors, typography, logo usage, email rules, and document
  templates. ALWAYS load this skill when: creating any branded output (presentations, documents,
  emails, PDFs, HTML artifacts, sales decks, client reports), applying Syntharra colors or fonts,
  using or placing the Syntharra logo, building email templates or signatures, creating slide decks,
  generating any artifact that will be seen by a client or external party, or whenever Dan asks
  for anything to look "on-brand" or "Syntharra-styled". This is the single source of truth for
  all Syntharra visual identity. Do not guess brand values — always load this skill first.
---

# Syntharra Brand Standard
> Single source of truth for all Syntharra visual identity.
> Apply this to every client-facing or branded output without exception.

---

## Color Palette

```css
--primary:        #6C63FF;   /* Syntharra Violet — headers, buttons, accents */
--secondary:      #00D4FF;   /* Cyan Spark — highlights, callouts */
--gradient:       linear-gradient(135deg, #6C63FF 0%, #8B85FF 100%);
--background:     #FAFAFA;   /* Page / slide background */
--surface:        #FFFFFF;   /* Cards, panels */
--text-primary:   #1A1A2E;   /* Deep Navy — all body copy */
--text-secondary: #4A4A6A;   /* Slate — secondary text */
--text-tertiary:  #8A8AA0;   /* Muted — disclaimers, meta */
--border:         #E5E7EB;   /* Dividers, card borders */
--dark-section:   linear-gradient(135deg, #0d0d1a, #1a1a3e);
/* EMAIL ONLY */
--email-outer-bg: #F7F7FB;
--email-card-bg:  #FFFFFF;
```

---

## Typography

### Documents & Presentations (Google Fonts)
```
Headers:  Inter Bold 700
Body:     Inter Regular 400
Source:   https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap
```

### Emails (system fonts only — clients don't load Google Fonts)
```
Wordmark / Name:  Georgia, 'Times New Roman', serif
Body / Labels:    Arial, Helvetica, sans-serif
```

---

## Logo

### Variants
| Variant | Use when |
|---|---|
| Icon — transparent bg | Light backgrounds, documents, decks |
| Icon — dark bg | Dark sections, dark slide backgrounds |
| Full logo (serif wordmark) `syntharra-logo-swapped-v2.png` | Cover slides, document headers |
| Full logo (violet wordmark) `syntharra-workspace-logo.png` | Brand-forward, internal |
| Hosted PNG (email-safe) | All emails — always use URL, never base64 in hosted contexts |

### Hosted icon URL (for n8n, website, hosted contexts)
```
https://raw.githubusercontent.com/Syntharra/syntharra-automations/main/brand-assets/email-signature/syntharra-icon.png
```

### Local path (Dan's machine)
```
C:\Users\danie\OneDrive\Desktop\Syntharra\syntharra_logo\
```

### Logo Construction
- 4 ascending vertical bars, rounded corners, flat `#6C63FF`
- Wordmark: Georgia / Times New Roman serif, 22px, normal weight, `#6C63FF`, letter-spacing 0.5px
- Tagline: Arial / Helvetica, 8px, bold, uppercase, letter-spacing 3.5px, `#111111`
- Tagline text: **Global AI Solutions** (always this exact casing — never "AI Solutions" or "AI SOLUTIONS")

### Logo Rules — Never Break These
- Never stretch, recolor, or add effects
- Never place transparent icon on busy background — use dark-bg variant on dark sections
- Never base64-encode SVGs in emails — Gmail mobile breaks them; use the hosted PNG URL
- Minimum clear space: height of one bar on all sides

---

## Email Standard

### Layout Rules
- Outer background: `#F7F7FB`
- Card background: `#FFFFFF`
- Text: `#1A1A2E`
- Accent: `#6C63FF`
- Max width: 600px, centered
- **Always light theme** — never dark emails

### Logo Block (paste into every email template)
```html
<table cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">
  <tr>
    <td style="vertical-align:middle; padding-right:10px;">
      <img src="https://raw.githubusercontent.com/Syntharra/syntharra-automations/main/brand-assets/email-signature/syntharra-icon.png"
           width="36" height="36" alt="Syntharra"
           style="display:block; border:0;" />
    </td>
    <td style="vertical-align:middle;">
      <div style="font-family:Georgia,'Times New Roman',serif; font-size:22px; font-weight:normal; color:#6C63FF; letter-spacing:0.5px; line-height:1.1;">Syntharra</div>
      <div style="font-family:Arial,Helvetica,sans-serif; font-size:8px; font-weight:bold; color:#111111; letter-spacing:3.5px; text-transform:uppercase; margin-top:3px;">Global AI Solutions</div>
    </td>
  </tr>
</table>
```

> For standalone emails use the hosted URL above.
> For email clients that block external images, swap `src` for the base64 version in `brand-assets/email-logo-block.html`.

### Email Signature Spec
- Name: Georgia serif, 17px bold, `#111111`
- Title: Arial, 10px bold uppercase, letter-spacing 2.5px, `#6C63FF`
- Contact links: Arial 13px, `#6C63FF`
- Divider: 2px solid `#6C63FF`
- Footer tagline: "AI Receptionists · Built for the Trades · Available 24/7"
- Signatures source: `C:\Users\danie\OneDrive\Desktop\Syntharra\syntharra_signatures\` (10 role-specific variants)

---

## Documents & Decks

### Presentations / Slides
- Background: `#FAFAFA`
- Slide header: Inter Bold, `#1A1A2E` or `#6C63FF` for emphasis
- Body: Inter Regular, `#4A4A6A`
- Accent bar / gradient: `linear-gradient(135deg, #6C63FF 0%, #8B85FF 100%)`
- Cover slide: full logo centered or top-left
- Dark slides: `linear-gradient(135deg, #0d0d1a, #1a1a3e)`, white text, cyan `#00D4FF` highlights
- Cards: white surface, 20px border-radius, 1px `#E5E7EB` border, violet top strip on featured cards
- Buttons: gradient primary or `#6C63FF` outline

### Word / PDF Documents
- Header: full logo top-left, 40px tall
- Heading 1: Inter Bold 24px, `#1A1A2E`
- Heading 2: Inter Bold 18px, `#6C63FF`
- Body: Inter 14px, `#4A4A6A`, line-height 1.7
- Dividers: 1px `#E5E7EB`
- Footer: Syntharra icon + "syntharra.com" + page number, `#8A8AA0`

---

## Artifact / HTML Standard

When building HTML artifacts or Claude.ai React components:

```css
/* Always import Inter */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

body {
  font-family: 'Inter', sans-serif;
  background: #FAFAFA;
  color: #1A1A2E;
}

/* Primary button */
.btn-primary {
  background: linear-gradient(135deg, #6C63FF, #8B85FF);
  color: #fff;
  border: none;
  border-radius: 8px;
}

/* Card */
.card {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 20px;
}

/* Accent text */
.accent { color: #6C63FF; }
.secondary { color: #00D4FF; }
```

---

## Credential Access Rule
ALL Syntharra API keys are in Supabase `syntharra_vault`.
Brand asset files are in `syntharra-automations/brand-assets/` and `syntharra-artifacts/brand/`.
