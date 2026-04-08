// ============================================================
// Syntharra Premium — Setup Email Builder v2
// ============================================================
// Light theme, Syntharra violet (#6C63FF) accent.
// Two flows:
//   OAuth platforms → "Connect Now" one-click button
//   API key platforms → 2-3 simple steps
// ============================================================

const data = $input.first().json;
const companyName = data.company_name || data.companyName || '';
const clientEmail = data.client_email || data.extractedData?.client_email || '';
const clientName = data.owner_name || data.extractedData?.owner_name || '';
const crmPlatform = data.crm_platform || data.extractedData?.crm_platform || '';
const calendarPlatform = data.calendar_platform || data.extractedData?.calendar_platform || '';
const agentId = data.agent_id || '';

// ── Brand ───────────────────────────────────────────────────
const v = '#6C63FF'; // Syntharra violet
const bg = '#F7F7FB';
const card = '#FFFFFF';
const text = '#1A1A2E';
const muted = '#6B7280';
const border = '#E5E7EB';
const green = '#10B981';
const amber = '#F59E0B';
const ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png';
const LOGO = `<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td style="vertical-align:middle;padding-right:10px"><img src="${ICON_URL}" alt="" width="36" height="36" style="display:block;border:0"></td><td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="text-align:left;padding:0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:16px;font-weight:700;letter-spacing:-0.3px;color:#0f0f1a;line-height:1;text-align:left">Syntharra</div></td></tr><tr><td style="text-align:left;padding:3px 0 0 0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:7.5px;font-weight:600;letter-spacing:1.2px;color:#6C63FF;text-transform:uppercase;line-height:1;text-align:left">Global AI Solutions</div></td></tr></table></td></tr></table>`;

// OAuth connect URL — client clicks this, authenticates, done.
// The auth server will handle the rest (exchange code for token, store encrypted, activate)
const connectBaseUrl = 'https://auth.syntharra.com/connect';

// ── Email Shell (Light Theme) ───────────────────────────────
function shell(bodyContent) {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:${bg};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:${bg};padding:40px 16px;">
<tr><td align="center">
<table width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%;">
<tr><td style="padding:0 0 24px;text-align:center;">
  ${LOGO}
</td></tr>
<tr><td style="background:${card};border-radius:12px;border:1px solid ${border};overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.06);">
<div style="height:3px;background:linear-gradient(90deg,${v},#8B7FFF);"></div>
<div style="padding:32px 36px;">${bodyContent}</div>
</td></tr>
<tr><td style="padding:20px 0;text-align:center;">
  <p style="color:${muted};font-size:12px;margin:0;">Questions? Reply to this email or contact support@syntharra.com</p>
  <p style="color:${muted};font-size:12px;margin:4px 0 0;">www.syntharra.com</p>
</td></tr>
</table></td></tr></table></body></html>`;
}

// ── Button ──────────────────────────────────────────────────
function btn(text, url) {
  return `<table cellpadding="0" cellspacing="0" style="margin:24px auto;"><tr>
<td style="background:${v};border-radius:8px;padding:14px 36px;">
<a href="${url}" style="color:#fff;text-decoration:none;font-weight:600;font-size:15px;display:block;">${text}</a>
</td></tr></table>`;
}

// ── Heading ─────────────────────────────────────────────────
function h(t) { return `<h2 style="color:${text};font-size:22px;font-weight:700;margin:0 0 8px;">${t}</h2>`; }
function sub(t) { return `<p style="color:${muted};font-size:15px;line-height:1.6;margin:0 0 20px;">${t}</p>`; }
function note(icon, t, bgColor) {
  bgColor = bgColor || '#F0EFFF';
  return `<div style="margin:20px 0;padding:14px 16px;background:${bgColor};border-radius:8px;">
<p style="color:${text};font-size:13px;line-height:1.6;margin:0;">${icon} ${t}</p></div>`;
}

// ── Step (for API key platforms) ────────────────────────────
function step(n, title, desc) {
  return `<div style="margin-bottom:16px;display:flex;">
<div style="min-width:28px;height:28px;background:${v};color:#fff;border-radius:50%;text-align:center;line-height:28px;font-weight:700;font-size:13px;margin-right:14px;">${n}</div>
<div><p style="color:${text};font-size:14px;font-weight:600;margin:0 0 4px;">${title}</p>
<p style="color:${muted};font-size:14px;line-height:1.5;margin:0;">${desc}</p></div></div>`;
}

// ============================================================
// PLATFORM DEFINITIONS
// ============================================================

const platforms = {

  // ── CALENDARS (OAuth — one click) ─────────────────────────

  'Google Calendar': {
    type: 'oauth',
    category: 'calendar',
    subject: `Connect Your Google Calendar — 1 Click Setup`,
    body: `
${h('Connect Your Google Calendar')}
${sub(`${clientName ? clientName + ', your' : 'Your'} AI Receptionist for <strong>${companyName}</strong> needs access to your Google Calendar to book appointments in real time.`)}
<p style="color:${text};font-size:14px;line-height:1.6;margin:0 0 4px;">Click the button below, sign in with your Google account, and approve access. That's it — your AI will start booking appointments immediately.</p>
${btn('Connect Google Calendar →', connectBaseUrl + '?platform=google_calendar&agent=' + agentId)}
${note('🔒', '<strong>Privacy:</strong> We only access your calendar events. We cannot read your email, contacts, or any other data.')}
${note('💡', '<strong>Tip:</strong> If you use a shared team calendar, sign in with the account that owns that calendar.')}`
  },

  'Microsoft Outlook': {
    type: 'oauth',
    category: 'calendar',
    subject: `Connect Your Outlook Calendar — 1 Click Setup`,
    body: `
${h('Connect Your Outlook Calendar')}
${sub(`${clientName ? clientName + ', your' : 'Your'} AI Receptionist needs access to your Outlook calendar to book appointments.`)}
<p style="color:${text};font-size:14px;line-height:1.6;margin:0 0 4px;">Click the button below, sign in with your Microsoft account, and approve access.</p>
${btn('Connect Outlook Calendar →', connectBaseUrl + '?platform=outlook&agent=' + agentId)}
${note('🔒', '<strong>Privacy:</strong> We only access your calendar. No emails, files, or contacts.')}`
  },

  'Calendly': {
    type: 'oauth',
    category: 'calendar',
    subject: `Connect Your Calendly — 1 Click Setup`,
    body: `
${h('Connect Your Calendly')}
${sub(`Your AI Receptionist for <strong>${companyName}</strong> will create bookings directly in Calendly.`)}
<p style="color:${text};font-size:14px;line-height:1.6;margin:0 0 4px;">Click the button below and sign in with your Calendly account.</p>
${btn('Connect Calendly →', connectBaseUrl + '?platform=calendly&agent=' + agentId)}
${note('💡', '<strong>Note:</strong> Make sure you have a Calendly event type set up for service appointments (e.g., "Service Call — 60 min"). Let us know the name so we can map it.')}`
  },

  'Cal.com': {
    type: 'oauth',
    category: 'calendar',
    subject: `Connect Your Cal.com — 1 Click Setup`,
    body: `
${h('Connect Your Cal.com Calendar')}
${sub(`Your AI Receptionist for <strong>${companyName}</strong> will book appointments through Cal.com.`)}
${btn('Connect Cal.com →', connectBaseUrl + '?platform=calcom&agent=' + agentId)}
${note('💡', 'Make sure you have an event type configured for service bookings.')}`
  },

  'Acuity Scheduling': {
    type: 'oauth',
    category: 'calendar',
    subject: `Connect Your Acuity Scheduling — 1 Click Setup`,
    body: `
${h('Connect Acuity Scheduling')}
${sub(`Your AI Receptionist will book directly into Acuity.`)}
${btn('Connect Acuity →', connectBaseUrl + '?platform=acuity&agent=' + agentId)}
${note('💡', 'Ensure your appointment types are set up in Acuity before connecting.')}`
  },

  'Square Appointments': {
    type: 'oauth',
    category: 'calendar',
    subject: `Connect Your Square Appointments — 1 Click Setup`,
    body: `
${h('Connect Square Appointments')}
${sub(`Your AI Receptionist will schedule directly through Square.`)}
${btn('Connect Square →', connectBaseUrl + '?platform=square&agent=' + agentId)}`
  },

  // ── CALENDARS (API key — built into CRM) ──────────────────

  'Jobber Calendar': {
    type: 'combined',
    category: 'calendar',
    subject: `Connect Your Jobber — 1 Click Setup`,
    body: `
${h('Connect Your Jobber Account')}
${sub(`Since Jobber handles both your calendar and customer management, this single connection gives your AI Receptionist full booking and CRM access.`)}
${btn('Connect Jobber →', connectBaseUrl + '?platform=jobber&agent=' + agentId)}
${note('✅', '<strong>One connection, everything linked.</strong> Your AI will create jobs, book appointments, and add new customers — all in Jobber.', '#ECFDF5')}`
  },

  'ServiceTitan Calendar': {
    type: 'apikey',
    category: 'calendar',
    subject: `Connect Your ServiceTitan — Quick Setup`,
    body: `
${h('Connect Your ServiceTitan')}
${sub(`Your AI Receptionist for <strong>${companyName}</strong> needs ServiceTitan access. Since ServiceTitan requires API approval, here is what to do:`)}
${step(1, 'Contact your ServiceTitan rep', 'Ask them to enable <strong>API access</strong> for your account. Tell them it is for an AI receptionist integration.')}
${step(2, 'Send us your credentials', 'Once approved, ServiceTitan will give you a Client ID, Client Secret, and Tenant ID. Just reply to this email with all three.')}
<p style="color:${muted};font-size:13px;margin:20px 0 0;">We will handle everything from there. Your credentials are encrypted and stored securely.</p>
${note('⏱️', '<strong>Timeline:</strong> ServiceTitan approval typically takes 2–5 business days. We will activate your integration the same day you send us the credentials.', '#FFF7ED')}`
  },

  'Housecall Pro Calendar': {
    type: 'oauth',
    category: 'calendar',
    subject: `Connect Your Housecall Pro — 1 Click Setup`,
    body: `
${h('Connect Housecall Pro')}
${sub(`Housecall Pro handles both your schedule and customer data, so this one connection covers everything.`)}
${btn('Connect Housecall Pro →', connectBaseUrl + '?platform=housecallpro&agent=' + agentId)}
${note('✅', '<strong>Full integration.</strong> Your AI will book jobs, add customers, and update your schedule — all in HCP.', '#ECFDF5')}`
  },

  // ── CRMs (OAuth) ──────────────────────────────────────────

  'Jobber': {
    type: 'oauth',
    category: 'crm',
    subject: `Connect Your Jobber CRM — 1 Click`,
    body: `
${h('Connect Your Jobber CRM')}
${sub(`Your AI Receptionist will automatically create contacts and log jobs in Jobber after every call.`)}
${btn('Connect Jobber →', connectBaseUrl + '?platform=jobber&agent=' + agentId)}`
  },

  'GoHighLevel': {
    type: 'oauth',
    category: 'crm',
    subject: `Connect Your GoHighLevel CRM — 1 Click`,
    body: `
${h('Connect GoHighLevel')}
${sub(`Your AI Receptionist will push new contacts and job details into GoHighLevel automatically.`)}
${btn('Connect GoHighLevel →', connectBaseUrl + '?platform=gohighlevel&agent=' + agentId)}`
  },

  'HubSpot': {
    type: 'oauth',
    category: 'crm',
    subject: `Connect Your HubSpot CRM — 1 Click`,
    body: `
${h('Connect HubSpot')}
${sub(`Your AI Receptionist will create contacts and deals in HubSpot after every call.`)}
${btn('Connect HubSpot →', connectBaseUrl + '?platform=hubspot&agent=' + agentId)}`
  },

  'Zoho CRM': {
    type: 'oauth',
    category: 'crm',
    subject: `Connect Your Zoho CRM — 1 Click`,
    body: `
${h('Connect Zoho CRM')}
${sub(`Your AI will automatically push new contacts and job data to Zoho CRM.`)}
${btn('Connect Zoho →', connectBaseUrl + '?platform=zoho&agent=' + agentId)}`
  },

  'Pipedrive': {
    type: 'oauth',
    category: 'crm',
    subject: `Connect Your Pipedrive — 1 Click`,
    body: `
${h('Connect Pipedrive')}
${sub(`Leads captured by your AI Receptionist will flow into Pipedrive automatically.`)}
${btn('Connect Pipedrive →', connectBaseUrl + '?platform=pipedrive&agent=' + agentId)}`
  },

  'Salesforce': {
    type: 'oauth',
    category: 'crm',
    subject: `Connect Your Salesforce — 1 Click`,
    body: `
${h('Connect Salesforce')}
${sub(`Your AI Receptionist will create leads and contacts in Salesforce automatically.`)}
${btn('Connect Salesforce →', connectBaseUrl + '?platform=salesforce&agent=' + agentId)}`
  },

  // ── CRMs (API key) ────────────────────────────────────────

  'ServiceTitan': {
    type: 'apikey',
    category: 'crm',
    subject: `Connect Your ServiceTitan CRM — Quick Setup`,
    body: `
${h('Connect ServiceTitan')}
${sub(`Your AI Receptionist needs ServiceTitan API access to create customers and jobs.`)}
${step(1, 'Contact your ServiceTitan rep', 'Request <strong>API access</strong> for third-party integration.')}
${step(2, 'Send us your credentials', 'Reply to this email with your Client ID, Client Secret, and Tenant ID.')}
${note('🔒', 'All credentials are AES-256 encrypted. Only the automated system can access them.')}`
  },

  'Housecall Pro': {
    type: 'oauth',
    category: 'crm',
    subject: `Connect Your Housecall Pro — 1 Click`,
    body: `
${h('Connect Housecall Pro')}
${sub(`Your AI Receptionist will push contacts and jobs into Housecall Pro.`)}
${btn('Connect Housecall Pro →', connectBaseUrl + '?platform=housecallpro&agent=' + agentId)}`
  },

  'FieldEdge': {
    type: 'apikey',
    category: 'crm',
    subject: `Connect Your FieldEdge — Quick Setup`,
    body: `
${h('Connect FieldEdge')}
${sub(`Your AI needs FieldEdge access to push customer and job data.`)}
${step(1, 'Contact FieldEdge support', 'Request API access for your account.')}
${step(2, 'Send us your API key', 'Reply to this email with the key they provide.')}
${note('⏱️', 'FieldEdge setup typically takes 1–3 business days.', '#FFF7ED')}`
  },

  'Kickserv': {
    type: 'apikey',
    category: 'crm',
    subject: `Connect Your Kickserv — Quick Setup`,
    body: `
${h('Connect Kickserv')}
${sub(`Let us connect your Kickserv so leads and bookings flow automatically.`)}
${step(1, 'Log in to Kickserv', 'Go to <strong>kickserv.com</strong> → Settings → API.')}
${step(2, 'Copy your API token', 'Reply to this email with it.')}
${note('📋', 'Your AI will automatically create jobs and contacts in Kickserv.')}`
  },

  'ServiceM8': {
    type: 'oauth',
    category: 'crm',
    subject: `Connect Your ServiceM8 — 1 Click`,
    body: `
${h('Connect ServiceM8')}
${sub(`Your AI Receptionist will sync leads and jobs to ServiceM8.`)}
${btn('Connect ServiceM8 →', connectBaseUrl + '?platform=servicem8&agent=' + agentId)}`
  },

  'Workiz': {
    type: 'apikey',
    category: 'crm',
    subject: `Connect Your Workiz — Quick Setup`,
    body: `
${h('Connect Workiz')}
${sub(`Your AI needs Workiz API access to create jobs and contacts.`)}
${step(1, 'Log in to Workiz', 'Go to Settings → Integrations → API.')}
${step(2, 'Copy your API key', 'Reply to this email with it.')}`
  }
};

// ============================================================
// BUILD EMAIL LIST
// ============================================================
const emails = [];

// Calendar setup email
if (calendarPlatform && calendarPlatform !== 'None' && calendarPlatform !== 'Custom / Other') {
  const p = platforms[calendarPlatform];
  if (p) {
    emails.push({
      to: clientEmail,
      subject: p.subject,
      html: shell(p.body),
      type: p.type,
      category: 'calendar',
      platform: calendarPlatform
    });
  }
}

// CRM setup email (only if different from calendar platform)
const calIsCRM = ['Jobber Calendar', 'ServiceTitan Calendar', 'Housecall Pro Calendar'].includes(calendarPlatform);
if (crmPlatform && crmPlatform !== 'None' && crmPlatform !== 'Custom / Other' && !calIsCRM) {
  const p = platforms[crmPlatform];
  if (p) {
    emails.push({
      to: clientEmail,
      subject: p.subject,
      html: shell(p.body),
      type: p.type,
      category: 'crm',
      platform: crmPlatform
    });
  }
}

return {
  setupEmails: emails,
  emailCount: emails.length,
  calendarPlatform,
  crmPlatform,
  clientEmail,
  companyName
};
