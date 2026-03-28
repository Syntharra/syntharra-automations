# Lead Capture Email Implementation Guide
## Deploy when network is back — or push manually via GitHub

---

## WHAT NEEDS TO HAPPEN

### 1. Website (index.html) — Add AI Readiness Quiz popup + wire exit-intent popup

Both popups need to:
- Save lead to Supabase `website_leads` table
- Trigger n8n webhook to send the appropriate email

### 2. Supabase — Ensure `website_leads` table has correct columns

Required columns: `id`, `created_at`, `email`, `source`, `metadata`

### 3. n8n — Create 2 webhook workflows

- `/webhook/ai-readiness-score` → sends AI Readiness results email
- `/webhook/free-report` → sends Free Report email

---

## STEP 1: Check/create Supabase table

Run this SQL in Supabase SQL Editor if `website_leads` doesn't have `metadata`:

```sql
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS metadata jsonb;
ALTER TABLE website_leads ADD COLUMN IF NOT EXISTS source text DEFAULT 'unknown';
```

## STEP 2: Add to index.html

Find the existing exit-intent popup code and the AI readiness popup code.

For the **exit-intent popup** ("Wait — before you go"), update the form submit handler to:

```javascript
// After capturing email from exit-intent popup
async function submitExitIntent(email) {
  // Save to Supabase
  await fetch('https://hgheyqwnrcvwtgngqdnq.supabase.co/rest/v1/website_leads', {
    method: 'POST',
    headers: {
      'apikey': 'YOUR_ANON_KEY',
      'Authorization': 'Bearer YOUR_ANON_KEY',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, source: 'exit_intent' })
  });
  
  // Trigger email via n8n
  await fetch('https://syntharra.app.n8n.cloud/webhook/free-report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
}
```

For the **AI Readiness quiz**, replace the existing AI readiness popup with the quiz component from `ai-readiness-quiz-preview.html`. The quiz already includes Supabase save + n8n webhook trigger code.

## STEP 3: Create n8n workflows

### Workflow A: Free Report Email
- Trigger: Webhook at `/webhook/free-report` (POST)
- Node 1: Code node with content from `free-report-email-node.js`
- Activate and Publish

### Workflow B: AI Readiness Score Email  
- Trigger: Webhook at `/webhook/ai-readiness-score` (POST)
- Node 1: Code node with content from `ai-readiness-email-node.js`
- Activate and Publish

## STEP 4: Test

1. Open syntharra.com
2. Trigger exit-intent popup → enter test email → check Supabase + inbox
3. Trigger AI readiness popup → complete quiz → enter test email → check Supabase + inbox

---

## FILES READY TO DEPLOY

| File | Purpose | Location |
|------|---------|----------|
| `ai-readiness-quiz-preview.html` | Full quiz widget (embed in index.html) | outputs/ |
| `free-report-email-node.js` | n8n code node for Free Report email | syntharra-lead-emails/ |
| `ai-readiness-email-node.js` | n8n code node for AI Readiness email | syntharra-lead-emails/ |
| `email-free-report-missed-calls.html` | Email template preview | outputs/ |
| `email-ai-readiness-score.html` | Email template preview | outputs/ |
