---
name: syntharra-brand
description: >
  Complete Syntharra brand standard — colors, typography, logo, email, documents, and decks.
  ALWAYS load this skill when: creating any branded output (presentations, documents, emails,
  artifacts, landing pages, reports, blog posts, social content); applying Syntharra colors or
  fonts; using the logo; building or editing any email template; creating slide decks or PDFs;
  designing any UI that carries the Syntharra brand; checking which logo variant to use;
  ensuring color or typography consistency across any deliverable. This skill is the single
  source of truth for ALL Syntharra visual identity. Apply silently — never narrate it.
---

> **Last verified: 2026-04-02** — add freshness date each time skill is confirmed current

# Syntharra — Brand Standard

> Single source of truth for all Syntharra visual identity.
> Apply to every branded output: decks, docs, emails, artifacts, UI, social.

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
```

**Email outer background:** `#F7F7FB` (slightly different from page bg — email-specific)

---

## Typography

### Documents, Decks, Artifacts, Web
| Role | Font | Weight | Notes |
|---|---|---|---|
| Headings | Inter | Bold (700) | Google Fonts |
| Body | Inter | Regular (400) | Google Fonts |
| Import | `https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap` | | |

### Emails only (system fonts — Google Fonts don't load in email clients)
| Role | Font stack |
|---|---|
| Wordmark / name | Georgia, 'Times New Roman', serif |
| Body / labels / UI | Arial, Helvetica, sans-serif |

---

## Logo

### Variants — which to use when
| Variant | Filename | Use when |
|---|---|---|
| Icon — transparent bg | `syntharra-icon (Transparent).png` | Light backgrounds, docs, decks |
| Icon — dark bg | `syntharra-icon (Dark Background).png` | Dark slides, dark sections |
| Full logo — serif wordmark | `syntharra-logo-swapped-v2.png` | Cover slides, doc headers, formal |
| Full logo — violet wordmark | `syntharra-workspace-logo.png` | Brand-forward, workspace, internal |
| **Email-safe hosted PNG** | URL below | **All emails — always use this** |

**Hosted icon URL (email-safe, never base64 in n8n/website):**
`https://raw.githubusercontent.com/Syntharra/syntharra-automations/main/brand-assets/email-signature/syntharra-icon.png`

**Local path:** `C:\Users\danie\OneDrive\Desktop\Syntharra\syntharra_logo\`

### Logo Construction
- 4 ascending vertical bars, rounded corners, flat `#6C63FF`
- Wordmark: Georgia / Times New Roman serif, 22px, normal weight, `#6C63FF`, letter-spacing 0.5px
- Tagline: Arial / Helvetica, 8px, bold, uppercase, letter-spacing 3.5px, `#111111`
- Tagline text: **"Global AI Solutions"** — always this exact phrase, always uppercase

### Logo Rules
- **Never** stretch, recolor, or add effects
- **Never** place transparent icon on busy background — use dark-bg variant on dark sections
- **Never** base64 SVG in emails — Gmail mobile breaks them; always use hosted PNG URL
- Minimum clear space: height of one bar on all sides

---

## Logo HTML Block (canonical — copy into every email / doc)

```html
<table cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">
  <tr>
    <td style="vertical-align:middle; padding-right:10px;">
      <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAEA0lEQVR4nO2bPWwcRRTHfzPrs/HZJv5IghJHQhBZWBApBisFIONAgUSBlCJBIKooDUUqOtp0kahQCpqIKlKEFKUgUhoiBSoQCFlAJIMTRakiZHCEfeZy5nZeivXmNps7337Neu/jX93Ozb55//+8eTM7s6vICWfPiMSpf+GiUrZ8CcJaI3EJt4MtQTI3mjXxMLIWIjNjtomHkZUQqY3kTTyMtEIkvnm3iYeRVAid5KaikYfkPsUWoIjkfSTxLXLYFJl4M0QdEpEioNPIQ3Sf2wrQieR9RPE9URLsJuwoQCf3vo92HFoK0A3kfezEpakA3UTeRytOPZ8Dnpori9r7Y8+yevIjbk/tYw+C1GpsXbtK6e4djsSxE14fDGTrpj0svM2t145xPFj2wccsnz+Xzu4TQ6CovQ9QLqOMwa3XqRlD3RjcoSGeiWsnzLFjIsAY0BoHEKXQSqFFSN1hjyOgyL3fEirZ43yQa8/PAhqK0fujo6zNzLI08xJLh2f41XZ7PudC5IDxCe5/+hkyMcmcX7ayzNIXnzeubaEQQ+D5F7g3MclB1+V/Y3BFMDOzzB2Y5rbttgsRAYASwfjZXSnvWiuM7YZ1EcY/gFJPRmP42gbOnhEpxBDYTfS8ALnkgNmX+eX1BWpaewuXOyvUbn7LYh5tt4N1AYaHWT/9CS+Wy4z7ZXPzsPoXP936jWO2228H+wKU2SiVmDKGOoDrUnccSlP7qNpuOwqsCyCyPaVpBkQQx/EealzX3tF8HOSSBFWTjRel0j/JZYH+LJCFkfEJ7g8O8RBgs8KezQqTWdjNA6kFWDjO9ydOMT9QYr9SqEqFta++ZGnlD/sPMlkg9RB4Y5HnBocYARDBjI2x981F/kvvWj7Qad+wcF3c4NZUFttUeeHCRaVSR4ACpQJbUyrhNtVuoedngb4AkN9bmUWCzzl1BAjtk16zOiKNXJF4SybLc4HEr5kptL+PJwZjDG4oKYrCO9UR8f43BtfRDee1Rrbvf1xHBAkul7X2bATtJE24Qa6pF0LVKtXtExsnUFb3fz+sMmIMbsmr45/usLnZaLuywbBSaGeAwZDtsv97YwOjNY5/P0C93mgnKVKfDh88xMqJU6yPjnrOPnjA+pXLTK/9zSG/ztw8P7zzLiOO45G+d5fVry/xVtDOe+9z85Wj7AcQg/z8I/98d6NRZ7jMvyc/5PcD00yKwFaNrevfYP5c5tU4/oYjvWOOx7NCWICnkmA3zwjNuPXXAc0KuzEKWnFqGQHdJMJOXHYcAt0gQjsO/RzQrkInR0EU3yNFQCeKENXn2MSKvlCK21mxc0CRoyGJb4mSYBFFSOpT/7O5rBzp2Q8nw+jZT2fD6NmPp1uhqJ/PPwJ0VJJMh1QmBQAAAABJRU5ErkJggg=="
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

**Rules:**
- Use this exact block in all emails and documents that need a logo
- For hosted contexts (website, n8n) swap base64 src for: `https://raw.githubusercontent.com/Syntharra/syntharra-automations/main/brand-assets/email-signature/syntharra-icon.png`
- Tagline is always **"Global AI Solutions"** — uppercase, letter-spaced, never abbreviated

---

## Email Standard

| Property | Value |
|---|---|
| Outer background | `#F7F7FB` |
| Card / body background | `#FFFFFF` |
| Text | `#1A1A2E` |
| Accent | `#6C63FF` |
| Max width | 600px, centered |
| Theme | **Always light** — never dark email |

### Email Signature Spec
| Element | Style |
|---|---|
| Name | Georgia serif, 17px, bold, `#111111` |
| Title | Arial, 10px, bold uppercase, letter-spacing 2.5px, `#6C63FF` |
| Contact links | Arial, 13px, `#6C63FF` |
| Divider | 2px solid `#6C63FF` |
| Footer tagline | "AI Receptionists · Built for the Trades · Available 24/7" |

Signature files: `C:\Users\danie\OneDrive\Desktop\Syntharra\syntharra_signatures\` (10 role-specific)

---

## Slide / Presentation Standard

| Element | Spec |
|---|---|
| Background | `#FAFAFA` |
| Slide header | Inter Bold, `#1A1A2E` or `#6C63FF` for emphasis |
| Body | Inter Regular, `#4A4A6A` |
| Accent bar | `linear-gradient(135deg, #6C63FF 0%, #8B85FF 100%)` |
| Cover slide | Full logo (`syntharra-logo-swapped-v2.png`), centered or top-left |
| Dark slides | Dark-section gradient, white text, `#00D4FF` highlights |
| Cards | White surface, 20px border-radius, 1px `#E5E7EB` border, violet top strip on featured |
| Buttons | Gradient primary or `#6C63FF` outline |

---

## Document Standard (Word / PDF)

| Element | Spec |
|---|---|
| Header | Full logo top-left, 40px tall |
| Heading 1 | Inter Bold 24px, `#1A1A2E` |
| Heading 2 | Inter Bold 18px, `#6C63FF` |
| Body | Inter 14px, `#4A4A6A`, line-height 1.7 |
| Dividers | 1px `#E5E7EB` |
| Footer | Syntharra icon + "syntharra.com" + page number, `#8A8AA0` |

---

## HTML / Artifact / Web UI Standard

```css
/* Always import Inter */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

/* Root tokens */
:root {
  --primary:        #6C63FF;
  --secondary:      #00D4FF;
  --gradient:       linear-gradient(135deg, #6C63FF 0%, #8B85FF 100%);
  --bg:             #FAFAFA;
  --surface:        #FFFFFF;
  --text:           #1A1A2E;
  --text-secondary: #4A4A6A;
  --text-muted:     #8A8AA0;
  --border:         #E5E7EB;
}

body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); }
h1, h2, h3 { font-weight: 700; color: var(--text); }
.accent { color: var(--primary); }
.card { background: var(--surface); border-radius: 12px; border: 1px solid var(--border); }
.btn-primary { background: var(--gradient); color: #fff; border-radius: 8px; }
```

---

## Brand Rules (never break these)

1. **Never** dark-theme emails — always light with `#F7F7FB` outer bg
2. **Never** base64 SVG in emails — use hosted PNG URL
3. **Never** stretch, recolor, or add effects to the logo
4. **Never** abbreviate the tagline — always "Global AI Solutions"
5. **Always** Inter for web/docs/decks, system fonts (Georgia/Arial) for emails
6. **Always** `overflow-x: clip` on body in HTML artifacts
7. **Always** one `<style>` block per HTML page — no inline style sprawl
8. **Always** use `#6C63FF` for accent, never approximate purples
9. **Always** confirm information back — Syntharra voice is warm, professional, concise
