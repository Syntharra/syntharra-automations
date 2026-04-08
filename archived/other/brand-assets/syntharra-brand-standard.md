# Syntharra

Official Syntharra brand theme — clean AI-tech identity. This is the standard for ALL Syntharra work: presentations, documents, emails, and any branded output.

---

## Logo Assets

### Variants

| Variant | File | Use When |
|---|---|---|
| Icon — transparent bg | `syntharra-icon (Transparent).png` | Light backgrounds, documents, decks |
| Icon — dark bg | `syntharra-icon (Dark Background).png` | Dark sections, dark slide backgrounds |
| Full logo (serif wordmark) | `syntharra-logo-swapped-v2.png` | Cover slides, document headers, formal docs |
| Full logo (violet wordmark) | `syntharra-workspace-logo.png` | Brand-forward contexts, workspace, internal |
| Hosted icon (email-safe PNG) | `https://raw.githubusercontent.com/Syntharra/syntharra-automations/main/brand-assets/email-signature/syntharra-icon.png` | All emails — use this URL, never base64 |

### Local Path
`C:\Users\danie\OneDrive\Desktop\Syntharra\syntharra_logo\`

### Logo Construction
- 4 ascending vertical bars, rounded corners, flat `#6C63FF`
- Wordmark: Georgia / Times New Roman serif, 22px, normal weight, `#6C63FF`, letter-spacing 0.5px
- Tagline: Arial / Helvetica, 8px, bold, uppercase, letter-spacing 3.5px, `#111111`
- Tagline text: **Global AI Solutions**

### Logo Usage Rules
- **Never** stretch, recolor, or add effects to the logo
- **Never** place the transparent icon on a busy background — use the dark-bg variant on dark sections
- **Never** use base64-encoded SVGs in emails — Gmail mobile breaks them; always use the hosted PNG URL
- Minimum clear space: equal to the height of one bar on all sides

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

---

## Typography

### Documents & Presentations
- **Headers**: Inter Bold
- **Body**: Inter Regular
- **Source**: Google Fonts — `https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap`

### Emails
- **Wordmark / Name**: Georgia, 'Times New Roman', serif
- **Body / Labels**: Arial, Helvetica, sans-serif
- **Reason**: Email clients don't load Google Fonts reliably — always use system fonts in emails

---

## Email Standard

### Template Rules
- Outer background: `#F7F7FB`
- Card/body background: `#FFFFFF`
- Text: `#1A1A2E`
- Accent: `#6C63FF`
- **Never dark-theme emails** — always light; let email clients handle dark mode
- Max width: 600px, centered

### Logo Block (copy into every email template)

Extracted from `syntharra_signatures/` — this is the canonical logo HTML for all emails and documents:

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
- Use this exact block in all emails, documents, and decks that need a logo
- Tagline is always **"Global AI Solutions"** — uppercase, letter-spaced
- The base64 icon is self-contained — no external URL dependency for emails
- For hosted contexts (website, n8n, etc.) you can swap the base64 `src` for the hosted URL: `https://raw.githubusercontent.com/Syntharra/syntharra-automations/main/brand-assets/email-signature/syntharra-icon.png`

### Email Signature
- Name font: Georgia serif, 17px bold, `#111111`
- Title font: Arial, 10px bold uppercase, letter-spacing 2.5px, `#6C63FF`
- Contact links: Arial 13px, `#6C63FF`
- Divider: 2px solid `#6C63FF`
- Footer tagline: "AI Receptionists · Built for the Trades · Available 24/7"
- Signature source: `C:\Users\danie\OneDrive\Desktop\Syntharra\syntharra_signatures\` (10 role-specific signatures)
- Tagline under wordmark: **"Global AI Solutions"** (always this — not "AI Solutions" or "AI SOLUTIONS")

---

## Document & Deck Standard

### Slides / Presentations
- Background: `#FAFAFA`
- Slide header: Inter Bold, `#1A1A2E` or `#6C63FF` for emphasis
- Body: Inter Regular, `#4A4A6A`
- Accent bar / gradient: `linear-gradient(135deg, #6C63FF 0%, #8B85FF 100%)`
- Cover slide: full logo (`syntharra-logo-swapped-v2.png`), centered or top-left
- Dark slides: use dark-section gradient, white text, cyan `#00D4FF` for highlights
- Cards: white surface, 20px border-radius, 1px `#E5E7EB` border, violet top strip on featured cards
- Buttons: gradient primary or `#6C63FF` outline

### Documents (Word / PDF)
- Header: full logo top-left, 40px tall
- Heading 1: Inter Bold 24px, `#1A1A2E`
- Heading 2: Inter Bold 18px, `#6C63FF`
- Body: Inter 14px, `#4A4A6A`, line-height 1.7
- Dividers: 1px `#E5E7EB`
- Footer: Syntharra icon + "syntharra.com" + page number, `#8A8AA0`

---

## Best Used For

All Syntharra materials — sales decks, investor pitches, client onboarding, case studies, email templates, email signatures, internal documents, blog headers, and any other branded output.
