// ── You're Live Email — HVAC Standard ──────────────────────────────────────
// Paste the content of this file into the "Build You're Live Email" Code node
// of the HVAC Standard onboarding workflow (4Hx7aRdzMl5N0uJP).
//
// Design system: matches https://n8n.syntharra.com/form/client-update exactly.
//   Background #F2F1FF · Card border #E8E6FF · Primary #6C63FF
//   Accent bar: 4px linear-gradient(90deg, #6C63FF, #8B7FFF, #A78BFA)
//
// Input fields expected from upstream Build Retell Prompt node:
//   company_name, agent_name, agent_phone_number, lead_email, plan_name
// ────────────────────────────────────────────────────────────────────────────

const input = $input.first().json;
const companyName    = input.company_name        || 'your company';
const agentName      = input.agent_name          || 'your AI Receptionist';
const phone          = input.agent_phone_number  || '';
const leadEmail      = input.lead_email          || '';

// Tier data — passed from onboarding workflow via Stripe session lookup
const tier          = (input.tier || 'professional').toLowerCase();
const minutesLimit  = input.minutes_limit  || (tier === 'starter' ? 350 : tier === 'business' ? 1400 : 700);
const overageRate   = input.overage_rate   || (tier === 'starter' ? 0.25 : tier === 'business' ? 0.12 : 0.18);
const whatsappNum   = input.whatsapp_number || '';  // set when Telnyx WhatsApp number is confirmed

const TIER_LABELS = { starter: 'Starter', professional: 'Professional', business: 'Business' };
const TIER_SUPPORT = {
  starter:      null,
  professional: { label: 'Priority WhatsApp Support', desc: 'Reach us via WhatsApp for priority assistance.' },
  business:     { label: 'Dedicated WhatsApp Line',   desc: 'Your dedicated Syntharra contact via WhatsApp.' },
};
const tierLabel   = TIER_LABELS[tier] || 'Professional';
const tierSupport = TIER_SUPPORT[tier];

if (!leadEmail || !phone) {
  return [{ json: { ...input, _skip: true, _reason: 'missing email or phone' } }];
}

// Format phone for display: +1 (XXX) XXX-XXXX
const digits     = phone.replace(/\D/g, '');
const d          = digits.slice(-10);
const displayNum = `+1 (${d.slice(0,3)}) ${d.slice(3,6)}-${d.slice(6)}`;

// QR codes for call-forwarding setup
const QR_IPHONE  = 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&color=6C63FF&bgcolor=F0EEFF&data=' + encodeURIComponent('App-Prefs:root=Phone&path=CALL_FORWARDING');
const QR_ANDROID = 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&color=6C63FF&bgcolor=F0EEFF&data=' + encodeURIComponent('tel:**21*' + digits + '#');

// Staircase bar-chart logo — identical to client-update form header
const LOGO_BARS = `<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse"><tr><td style="vertical-align:bottom;padding-right:3px"><div style="width:5px;height:13px;background:#6C63FF;font-size:1px;line-height:1px">&nbsp;</div></td><td style="vertical-align:bottom;padding-right:3px"><div style="width:5px;height:19px;background:#6C63FF;font-size:1px;line-height:1px">&nbsp;</div></td><td style="vertical-align:bottom;padding-right:3px"><div style="width:5px;height:26px;background:#6C63FF;font-size:1px;line-height:1px">&nbsp;</div></td><td style="vertical-align:bottom"><div style="width:5px;height:33px;background:#6C63FF;font-size:1px;line-height:1px">&nbsp;</div></td></tr></table>`;

const emailHtml = `<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#F2F1FF;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;color:#0D0D1A">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F2F1FF;padding:40px 20px">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:18px;overflow:hidden;border:1px solid #E8E6FF;box-shadow:0 8px 40px rgba(108,99,255,.10),0 1px 3px rgba(0,0,0,.04)">

<!-- Accent bar -->
<tr><td style="height:4px;background:linear-gradient(90deg,#6C63FF,#8B7FFF,#A78BFA);font-size:0;line-height:0">&nbsp;</td></tr>

<!-- Header -->
<tr><td style="padding:24px 40px;border-bottom:1px solid #E8E6FF;background:#ffffff">
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
<td style="padding-right:11px;vertical-align:middle">${LOGO_BARS}</td>
<td style="vertical-align:middle">
<div style="font-size:16px;font-weight:700;color:#0D0D1A;letter-spacing:-0.02em;line-height:1">Syntharra</div>
<div style="font-size:12px;color:#6B7280;margin-top:5px;line-height:1">Your AI Receptionist is live</div>
</td></tr></table>
</td></tr>

<!-- Body -->
<tr><td style="padding:32px 40px;background:#ffffff">

<!-- You're Live badge -->
<div style="margin-bottom:20px">
  <span style="display:inline-block;background:#6C63FF;color:#ffffff;padding:5px 14px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase">You're Live</span>
</div>

<h1 style="font-size:22px;font-weight:700;color:#0D0D1A;margin:0 0 8px;letter-spacing:-0.02em">Your AI Receptionist is answering calls</h1>
<p style="font-size:14px;color:#6B7280;line-height:1.7;margin:0 0 24px">${agentName} is configured and ready to answer calls 24/7 for ${companyName}. Forward your business number to activate it.</p>

<!-- Active status card -->
<div style="padding:16px 20px;background:#ECFDF5;border-radius:10px;border:1px solid #A7F3D0;margin-bottom:20px">
  <div style="font-size:13px;color:#047857;margin-bottom:4px"><strong style="color:#065F46">Agent:</strong> ${agentName}</div>
  <div style="font-size:13px;color:#047857"><strong style="color:#065F46">Status:</strong> &#x2705; Active &mdash; answering calls 24/7</div>
</div>

<!-- Phone number box -->
<div style="padding:22px;background:#F0EEFF;border-radius:12px;border:1px solid #D0CAFF;text-align:center;margin-bottom:28px">
  <div style="font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#6C63FF;margin-bottom:8px">Your AI Receptionist Number</div>
  <div style="font-size:28px;font-weight:700;color:#0D0D1A;letter-spacing:0.5px">${displayNum}</div>
  <div style="font-size:12px;color:#6B7280;margin-top:8px">Forward your existing business number to this number</div>
</div>

<!-- Setup section -->
<h2 style="font-size:17px;font-weight:700;color:#0D0D1A;margin:0 0 4px">Quick Setup &mdash; Scan to Activate</h2>
<p style="font-size:13px;color:#6B7280;line-height:1.6;margin:0 0 18px">Open your phone camera and scan the QR code for your device type.</p>

<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:10px">
<tr>
  <td width="48%" style="background:#F8F7FF;border:1px solid #E8E6FF;border-radius:12px;padding:20px;text-align:center;vertical-align:top">
    <div style="font-size:13px;font-weight:700;color:#0D0D1A;margin-bottom:12px">&#x1F4F1; iPhone</div>
    <img src="${QR_IPHONE}" width="120" height="120" style="display:block;margin:0 auto 12px;border-radius:8px" alt="iPhone QR code">
    <p style="font-size:11px;color:#6B7280;line-height:1.5;margin:0">Opens Call Forwarding settings directly</p>
  </td>
  <td width="4%"></td>
  <td width="48%" style="background:#F8F7FF;border:1px solid #E8E6FF;border-radius:12px;padding:20px;text-align:center;vertical-align:top">
    <div style="font-size:13px;font-weight:700;color:#0D0D1A;margin-bottom:12px">&#x1F4F1; Android</div>
    <img src="${QR_ANDROID}" width="120" height="120" style="display:block;margin:0 auto 12px;border-radius:8px" alt="Android QR code">
    <p style="font-size:11px;color:#6B7280;line-height:1.5;margin:0">Dials the forwarding code automatically</p>
  </td>
</tr>
</table>

<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px">
<tr>
  <td width="48%" style="vertical-align:top;padding:8px 4px 0 0">
    <p style="font-size:11px;color:#6B7280;line-height:1.6;margin:0 0 3px">&#x2022; Scan QR with your camera</p>
    <p style="font-size:11px;color:#6B7280;line-height:1.6;margin:0 0 3px">&#x2022; Toggle Call Forwarding on</p>
    <p style="font-size:11px;color:#6B7280;line-height:1.6;margin:0">&#x2022; Enter <strong style="color:#0D0D1A">${displayNum}</strong></p>
  </td>
  <td width="4%"></td>
  <td width="48%" style="vertical-align:top;padding:8px 0 0 4px">
    <p style="font-size:11px;color:#6B7280;line-height:1.6;margin:0 0 3px">&#x2022; Scan QR with your camera</p>
    <p style="font-size:11px;color:#6B7280;line-height:1.6;margin:0 0 3px">&#x2022; It dials the code for you</p>
    <p style="font-size:11px;color:#6B7280;line-height:1.6;margin:0">&#x2022; Wait for confirmation tone</p>
  </td>
</tr>
</table>

<!-- Plan details card -->
<div style="padding:18px 20px;background:#F8F7FF;border-radius:10px;border:1px solid #E8E6FF;margin-bottom:20px">
  <div style="font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#6C63FF;margin-bottom:10px">Your Plan — ${tierLabel}</div>
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td style="font-size:13px;color:#6B7280;padding:5px 0;border-bottom:1px solid #E8E6FF">Included minutes / month</td>
      <td style="font-size:13px;font-weight:700;color:#0D0D1A;text-align:right;padding:5px 0;border-bottom:1px solid #E8E6FF">${minutesLimit} min</td>
    </tr>
    <tr>
      <td style="font-size:13px;color:#6B7280;padding:5px 0;border-bottom:1px solid #E8E6FF">Overage rate</td>
      <td style="font-size:13px;color:#0D0D1A;text-align:right;padding:5px 0;border-bottom:1px solid #E8E6FF">$${overageRate.toFixed(2)}/min</td>
    </tr>
    <tr>
      <td style="font-size:13px;color:#6B7280;padding:5px 0">Dashboard access</td>
      <td style="font-size:13px;color:#047857;text-align:right;padding:5px 0">&#x2705; Included</td>
    </tr>
  </table>
</div>

${tierSupport ? `
<!-- WhatsApp support card (Professional / Business) -->
<div style="padding:16px 20px;background:#E8F5E9;border-radius:10px;border:1px solid #A5D6A7;margin-bottom:20px">
  <div style="font-size:13px;font-weight:700;color:#1B5E20;margin-bottom:4px">&#x1F4AC; ${tierSupport.label}</div>
  <div style="font-size:12px;color:#2E7D32;line-height:1.5">${tierSupport.desc}${whatsappNum ? ` WhatsApp: <strong>${whatsappNum}</strong>` : ' Our team will reach out via WhatsApp shortly.'}</div>
</div>` : ''}

<!-- What happens next -->
<div style="padding:18px 20px;background:#F0EEFF;border-radius:10px;border:1px solid #D0CAFF;margin-bottom:20px">
  <div style="font-size:14px;font-weight:700;color:#0D0D1A;margin-bottom:10px">Once forwarding is active</div>
  <div style="font-size:13px;color:#4A4A6A;line-height:1.6;margin-bottom:4px">&#x2022; Every call answered instantly by ${agentName}</div>
  <div style="font-size:13px;color:#4A4A6A;line-height:1.6;margin-bottom:4px">&#x2022; Lead alerts emailed to you within 30 seconds</div>
  <div style="font-size:13px;color:#4A4A6A;line-height:1.6">&#x2022; Weekly activity report every Sunday at 6 pm</div>
</div>

<!-- Setup guide callout -->
<div style="padding:18px 20px;background:#6C63FF;border-radius:10px;margin-bottom:20px">
  <div style="font-size:14px;font-weight:700;color:#ffffff;margin-bottom:6px">&#x1F4CE; Full Setup Guide Attached</div>
  <div style="font-size:13px;color:rgba(255,255,255,0.88);line-height:1.6">We've attached a PDF with step-by-step instructions for every carrier, VoIP provider, and business phone system — including scannable QR codes. Share it with your team.</div>
</div>

<div style="margin-top:28px;padding-top:24px;border-top:1px solid #E8E6FF">
<a href="https://syntharra.com/dashboard.html?a=${encodeURIComponent(input.agent_id || '')}" style="display:inline-block;background:#6C63FF;color:#ffffff;text-decoration:none;padding:14px 28px;border-radius:10px;font-weight:600;font-size:15px">Open your dashboard</a>
</div>
<p style="font-size:13px;color:#6B7280;line-height:1.6;margin:16px 0 0">Need help? Email us at <a href="mailto:support@syntharra.com" style="color:#6C63FF;font-weight:600;text-decoration:none">support@syntharra.com</a></p>

</td></tr>

<!-- Footer -->
<tr><td style="padding:18px 40px;border-top:1px solid #E8E6FF;background:#ffffff">
<div style="font-size:12px;color:#6B7280;text-align:center;line-height:1.7">
Syntharra AI Receptionist &nbsp;&middot;&nbsp; <a href="https://syntharra.com" style="color:#6C63FF;text-decoration:none">syntharra.com</a>
</div>
</td></tr>

</table>
</td></tr>
</table>
</body>
</html>`;

return [{
  json: {
    ...input,
    emailHtml,
    emailSubject: `Your AI Receptionist is Live \u2014 ${companyName}`,
    lead_email: leadEmail,
    tier,
    minutes_limit: minutesLimit,
    overage_rate: overageRate,
  },
}];
