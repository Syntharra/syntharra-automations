# Cold Email Sequence

3-email drip. Sent from solutions@syntharra.com via SMTP2GO.
Stops automatically on reply, unsubscribe, or booking.

---

## Sequence Overview

| Email | Day | Subject Goal | CTA |
|---|---|---|---|
| Email 1 | Day 0 | Grab attention with a real scenario | Watch the demo |
| Email 2 | Day 3 | Build credibility + urgency | Book a call |
| Email 3 | Day 7 | Final attempt, direct ask | Reply or book |

---

## Variables Available Per Lead
```
{{business_name}}    — e.g., "Arctic Breeze HVAC"
{{first_name}}       — owner first name if known, else "Hi there"
{{city}}             — e.g., "Houston"
{{industry}}         — e.g., "HVAC" / "plumbing" / "electrical"
{{demo_url}}         — unique tracked URL per lead
{{booking_url}}      — Cal.com booking link
{{utm_code}}         — unique per lead for click tracking
```

---

## Email 1 — The Hook (Day 0)

**Subject line options (A/B test):**
- `Your phone just cost you a customer, {{business_name}}`
- `8:47pm Friday. AC down. Did you answer?`
- `How {{city}} HVAC companies are never missing calls again`

**Winner for HVAC:** Option 2 (most specific, most visceral)

---

### Email 1 HTML Template

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#F7F7FB;font-family:Inter,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F7F7FB;padding:32px 16px;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #E5E7EB;">

        <!-- Header -->
        <tr>
          <td style="background:#6C63FF;padding:24px 32px;">
            <span style="color:#ffffff;font-size:20px;font-weight:700;letter-spacing:-0.5px;">Syntharra</span>
            <span style="color:rgba(255,255,255,0.6);font-size:11px;letter-spacing:2px;text-transform:uppercase;margin-left:8px;">AI SOLUTIONS</span>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:32px;">
            <p style="margin:0 0 16px;color:#1A1A2E;font-size:15px;line-height:1.6;">
              Hi {{first_name}},
            </p>
            <p style="margin:0 0 16px;color:#1A1A2E;font-size:15px;line-height:1.6;">
              It's 8:47pm on a Friday. Someone's AC just failed. They're in Houston,
              it's 97°F, and they have an elderly parent at home.
            </p>
            <p style="margin:0 0 16px;color:#1A1A2E;font-size:15px;line-height:1.6;">
              They called <strong>{{business_name}}</strong>.
            </p>
            <p style="margin:0 0 16px;color:#1A1A2E;font-size:15px;line-height:1.6;">
              Did someone answer?
            </p>
            <p style="margin:0 0 24px;color:#4A4A6A;font-size:15px;line-height:1.6;">
              We built an AI receptionist that answers every call, 24/7 — captures the
              lead, triages the urgency, books the appointment, and alerts your tech.
              In under 3 minutes. No voicemail. No missed jobs.
            </p>

            <!-- CTA Button -->
            <table cellpadding="0" cellspacing="0">
              <tr>
                <td style="background:#6C63FF;border-radius:8px;padding:14px 28px;">
                  <a href="{{demo_url}}" style="color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;">
                    Watch the 2-minute demo →
                  </a>
                </td>
              </tr>
            </table>

            <p style="margin:24px 0 0;color:#8A8AA0;font-size:13px;line-height:1.6;">
              Real call. Real AI. Real results. No sales pitch — just press play.
            </p>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="padding:20px 32px;border-top:1px solid #E5E7EB;">
            <p style="margin:0;color:#8A8AA0;font-size:12px;line-height:1.6;">
              Syntharra Global AI Solutions &nbsp;·&nbsp;
              <a href="mailto:solutions@syntharra.com" style="color:#6C63FF;text-decoration:none;">solutions@syntharra.com</a>
              &nbsp;·&nbsp;
              <a href="{{unsubscribe_url}}" style="color:#8A8AA0;text-decoration:none;">Unsubscribe</a>
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
```

---

## Email 2 — Social Proof + Urgency (Day 3)

**Send only if:** Email 1 not replied to, not unsubscribed, not booked.

**Subject line options:**
- `Re: {{business_name}} — quick follow up`
- `The call that booked a $9,200 job at 9pm`
- `While your competitor was closed, their AI was working`

---

### Email 2 HTML Template

```html
<!-- Same header/footer as Email 1, body content: -->

<p style="margin:0 0 16px;color:#1A1A2E;font-size:15px;line-height:1.6;">
  Hi {{first_name}},
</p>
<p style="margin:0 0 16px;color:#1A1A2E;font-size:15px;line-height:1.6;">
  Following up from earlier in the week.
</p>
<p style="margin:0 0 16px;color:#1A1A2E;font-size:15px;line-height:1.6;">
  The average {{industry}} business misses 35–40% of inbound calls.
  Most of those callers don't leave a voicemail. They call the next company on the list.
</p>
<p style="margin:0 0 16px;color:#1A1A2E;font-size:15px;line-height:1.6;">
  Our AI receptionist is already handling calls for {{industry}} contractors across the US —
  after hours, on weekends, during jobs. It doesn't get tired, doesn't forget to call back,
  and never puts a customer on hold.
</p>
<p style="margin:0 0 24px;color:#4A4A6A;font-size:15px;line-height:1.6;">
  Setup takes under a week. No new hardware. Starts at $197/month.
</p>

<!-- CTA: Book a call -->
<table cellpadding="0" cellspacing="0">
  <tr>
    <td style="background:#6C63FF;border-radius:8px;padding:14px 28px;">
      <a href="{{booking_url}}" style="color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;">
        Book a 15-min call →
      </a>
    </td>
  </tr>
</table>

<p style="margin:24px 0 0;color:#8A8AA0;font-size:13px;">
  No commitment. Just a conversation.
</p>
```

---

## Email 3 — Final Ask (Day 7)

**Send only if:** No reply, no booking in 7 days.

**Subject line:**
- `Last message from me, {{first_name}}`
- `Closing your file — one last thing`

---

### Email 3 HTML Template (body only)

```html
<p style="margin:0 0 16px;color:#1A1A2E;font-size:15px;line-height:1.6;">
  Hi {{first_name}},
</p>
<p style="margin:0 0 16px;color:#1A1A2E;font-size:15px;line-height:1.6;">
  This is my last email — I don't want to clog your inbox.
</p>
<p style="margin:0 0 16px;color:#1A1A2E;font-size:15px;line-height:1.6;">
  Just one question: is missing after-hours calls actually a problem for
  {{business_name}}, or is it covered?
</p>
<p style="margin:0 0 24px;color:#4A4A6A;font-size:15px;line-height:1.6;">
  If it's a problem — reply "yes" and I'll send over a 2-minute demo.
  If it's not — reply "no" and I'll stop emailing. Either way, I'll respect it.
</p>

<!-- Two buttons side by side -->
<table cellpadding="0" cellspacing="0">
  <tr>
    <td style="background:#6C63FF;border-radius:8px;padding:12px 24px;margin-right:12px;">
      <a href="{{interested_url}}" style="color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;">
        Yes, show me the demo
      </a>
    </td>
    <td width="12"></td>
    <td style="background:#F7F7FB;border:1px solid #E5E7EB;border-radius:8px;padding:12px 24px;">
      <a href="{{unsubscribe_url}}" style="color:#4A4A6A;font-size:14px;font-weight:600;text-decoration:none;">
        No thanks
      </a>
    </td>
  </tr>
</table>
```

---

## n8n Email Sequence Logic

```
Trigger: New lead inserted to Supabase (status = 'new')
  │
  ├── Wait 0 min → Send Email 1 → Update status to 'emailed'
  │
  ├── Wait 3 days
  │   Check: status still 'emailed'? (not replied/booked/unsubscribed)
  │   Yes → Send Email 2
  │
  ├── Wait 4 more days (7 total)
  │   Check: status still 'emailed'?
  │   Yes → Send Email 3
  │
  └── Done. Lead stays in DB for future re-engagement (30 days cooldown)
```

---

## Click Tracking (Hot Lead Detection)

Every demo video link = unique URL:
```
https://syntharra.com/demo?ref={{utm_code}}
```

n8n webhook listener on this URL:
- Logs click to `email_events` table
- Updates lead `status` to 'clicked'
- Updates `video_clicked_at` timestamp
- Sends instant alert to admin@syntharra.com:
  ```
  🔥 HOT LEAD: {{business_name}} ({{city}}) just watched your demo.
  Phone: {{phone}}
  Email: {{email}}
  Click time: {{timestamp}}
  [Book them now →]
  ```

---

## SMTP2GO Configuration

```
Host: mail.smtp2go.com
Port: 587
Username: syntharra.com
API Key: api-0BE30DA64A074BC79F28BE6AEDC9DB9E
From: solutions@syntharra.com
From Name: Dan at Syntharra
Reply-To: solutions@syntharra.com
```

---

## Sending Limits & Compliance

- Max 200 emails/day to start (warm up the domain)
- Ramp: 50/day week 1 → 100/day week 2 → 200/day week 3+
- Always include physical address in footer (CAN-SPAM)
- One-click unsubscribe required
- Store unsubscribes in Supabase, never email again
- Add SPF, DKIM, DMARC to syntharra.com DNS before launching
