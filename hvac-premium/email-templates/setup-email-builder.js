// ============================================================
// Syntharra Premium — Integration Setup Email Builder
// ============================================================
// Generates branded HTML setup instruction emails based on
// which CRM and Calendar platform the client selected.
//
// Called from the onboarding workflow AFTER agent creation.
// Input: extractedData from the prompt builder
// Output: { setupEmails: [...] } — array of emails to send
// ============================================================

const data = $input.first().json;
const companyName = data.company_name || data.companyName || 'Your Company';
const clientEmail = data.client_email || data.extractedData?.client_email || '';
const crmPlatform = data.crm_platform || data.extractedData?.crm_platform || '';
const calendarPlatform = data.calendar_platform || data.extractedData?.calendar_platform || '';
const agentName = data.agent_name || data.extractedData?.agent_name || '';

// ── Brand Constants ─────────────────────────────────────────
const brand = {
  violet: '#6C63FF',
  cyan: '#00D4FF',
  dark: '#0D0D1A',
  darkPanel: '#141428',
  lightText: '#E8E8F0',
  mutedText: '#9999B0',
  white: '#FFFFFF',
  green: '#10B981',
  amber: '#F59E0B',
  logoUrl: 'https://i.postimg.cc/zBSrKLDb/company-logo-link.png',
  supportEmail: 'support@syntharra.com',
  website: 'www.syntharra.com'
};

// ── Email Shell ─────────────────────────────────────────────
function wrapEmail(subject, bodyContent) {
  return `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:${brand.dark};font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:${brand.dark};padding:32px 16px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

<!-- Header -->
<tr><td style="padding:24px 32px;text-align:center;">
  <img src="${brand.logoUrl}" alt="Syntharra" width="180" style="display:block;margin:0 auto 8px;">
  <p style="color:${brand.mutedText};font-size:13px;margin:0;">AI Receptionist for the Trades</p>
</td></tr>

<!-- Main Card -->
<tr><td style="background:${brand.darkPanel};border-radius:16px;border:1px solid rgba(108,99,255,0.2);overflow:hidden;">

<!-- Accent Bar -->
<div style="height:4px;background:linear-gradient(90deg,${brand.violet},${brand.cyan});"></div>

<!-- Content -->
<div style="padding:32px;">
${bodyContent}
</div>

</td></tr>

<!-- Footer -->
<tr><td style="padding:24px 32px;text-align:center;">
  <p style="color:${brand.mutedText};font-size:12px;margin:0 0 4px;">Need help? Reply to this email or contact us at ${brand.supportEmail}</p>
  <p style="color:${brand.mutedText};font-size:12px;margin:0;">${brand.website} | Syntharra AI Solutions</p>
</td></tr>

</table>
</td></tr>
</table>
</body>
</html>`;
}

// ── Step Builder ────────────────────────────────────────────
function step(number, title, description, imageHint) {
  return `
<div style="margin-bottom:24px;padding:16px;background:rgba(108,99,255,0.06);border-radius:12px;border-left:3px solid ${brand.violet};">
  <div style="display:flex;align-items:center;margin-bottom:8px;">
    <span style="display:inline-block;width:28px;height:28px;background:${brand.violet};color:${brand.white};border-radius:50%;text-align:center;line-height:28px;font-weight:700;font-size:14px;margin-right:12px;">${number}</span>
    <strong style="color:${brand.white};font-size:15px;">${title}</strong>
  </div>
  <p style="color:${brand.lightText};font-size:14px;line-height:1.6;margin:0 0 0 40px;">${description}</p>
  ${imageHint ? `<p style="color:${brand.mutedText};font-size:12px;margin:8px 0 0 40px;font-style:italic;">${imageHint}</p>` : ''}
</div>`;
}

function infoBox(text, color) {
  color = color || brand.cyan;
  return `<div style="margin:20px 0;padding:14px 16px;background:rgba(0,212,255,0.08);border-radius:10px;border:1px solid ${color}30;">
  <p style="color:${brand.lightText};font-size:13px;line-height:1.6;margin:0;">${text}</p>
</div>`;
}

function heading(text) {
  return `<h2 style="color:${brand.white};font-size:22px;font-weight:700;margin:0 0 8px;font-family:Georgia,'Times New Roman',serif;">${text}</h2>`;
}

function subtext(text) {
  return `<p style="color:${brand.mutedText};font-size:14px;line-height:1.5;margin:0 0 24px;">${text}</p>`;
}

// ── Platform-Specific Instructions ──────────────────────────

const calendarGuides = {
  'Google Calendar': {
    subject: `Connect Your Google Calendar — ${companyName} AI Receptionist`,
    body: `
${heading('Connect Your Google Calendar')}
${subtext(`Hi there! Your AI Receptionist for <strong style="color:${brand.white}">${companyName}</strong> is almost ready. We just need to connect your Google Calendar so your receptionist can check availability and book appointments in real time.`)}

${step(1, 'Open Google Calendar Settings', 'Go to <strong>calendar.google.com</strong> and click the gear icon (⚙️) in the top right corner, then select <strong>Settings</strong>.', '')}

${step(2, 'Find Your Calendar ID', 'In the left sidebar, click on the calendar you want to use for bookings (e.g., your main business calendar). Scroll down to <strong>Integrate calendar</strong> and copy the <strong>Calendar ID</strong>. It looks like: <code style="background:rgba(108,99,255,0.15);color:${brand.cyan};padding:2px 6px;border-radius:4px;">yourcompany@gmail.com</code> or a long ID ending in <code>@group.calendar.google.com</code>.', '')}

${step(3, 'Share Your Calendar with Syntharra', 'Still in your calendar settings, scroll to <strong>Share with specific people or groups</strong>. Click <strong>Add people and groups</strong> and enter: <code style="background:rgba(108,99,255,0.15);color:${brand.cyan};padding:2px 6px;border-radius:4px;">integrations@syntharra.com</code>. Set permission to <strong>Make changes to events</strong>.', '')}

${step(4, 'Send Us Your Calendar ID', 'Reply to this email with your Calendar ID from Step 2. We will link it to your AI Receptionist and activate real-time booking within 24 hours.', '')}

${infoBox('💡 <strong>Tip:</strong> If you use a shared team calendar for scheduling, use that Calendar ID instead of your personal one. This way all technicians see the bookings.')}

${infoBox('🔒 <strong>Privacy:</strong> Your AI Receptionist can only see and create events on the specific calendar you share. It cannot access your personal email, contacts, or other calendars.', brand.green)}`
  },

  'Microsoft Outlook': {
    subject: `Connect Your Outlook Calendar — ${companyName} AI Receptionist`,
    body: `
${heading('Connect Your Outlook Calendar')}
${subtext(`Your AI Receptionist for <strong style="color:${brand.white}">${companyName}</strong> needs access to your Outlook calendar to book appointments. Here is how to connect it.`)}

${step(1, 'Open Outlook Calendar', 'Go to <strong>outlook.office.com/calendar</strong> and sign in with your business Microsoft account.', '')}

${step(2, 'Share Your Calendar', 'Click the <strong>Share</strong> button at the top of the calendar view. Enter: <code style="background:rgba(108,99,255,0.15);color:${brand.cyan};padding:2px 6px;border-radius:4px;">integrations@syntharra.com</code>. Set permission to <strong>Can edit</strong>.', '')}

${step(3, 'Confirm & Reply', 'Reply to this email to confirm you have shared your calendar. Our team will complete the connection within 24 hours.', '')}

${infoBox('🔒 <strong>Privacy:</strong> We only access the calendar you explicitly share. No emails, contacts, or other data.')}`
  },

  'Calendly': {
    subject: `Connect Your Calendly — ${companyName} AI Receptionist`,
    body: `
${heading('Connect Your Calendly')}
${subtext(`Your AI Receptionist for <strong style="color:${brand.white}">${companyName}</strong> needs to connect with Calendly to book appointments directly during calls.`)}

${step(1, 'Log in to Calendly', 'Go to <strong>calendly.com</strong> and sign in to your account.', '')}

${step(2, 'Get Your API Key', 'Click your profile icon → <strong>Integrations</strong> → scroll down to <strong>API & Webhooks</strong> → click <strong>Generate New Token</strong>. Name it "Syntharra AI" and copy the token.', '')}

${step(3, 'Send Us Your API Token', 'Reply to this email with your Calendly API token. We will configure your AI Receptionist to create bookings directly in Calendly.', '')}

${infoBox('⏱️ <strong>Event Type:</strong> Make sure you have an Event Type set up in Calendly for service appointments (e.g., "HVAC Service Call — 60 minutes"). Let us know the name so we can map it correctly.')}`
  },

  'Jobber Calendar': {
    subject: `Connect Your Jobber Calendar — ${companyName} AI Receptionist`,
    body: `
${heading('Connect Your Jobber Calendar')}
${subtext(`Your AI Receptionist for <strong style="color:${brand.white}">${companyName}</strong> will book directly into Jobber. Since Jobber handles both your calendar and CRM, this single connection covers everything.`)}

${step(1, 'Log in to Jobber', 'Go to <strong>getjobber.com</strong> and sign in to your account.', '')}

${step(2, 'Find Your API Key', 'Go to <strong>Settings</strong> → <strong>Apps & Integrations</strong> → <strong>API Access</strong>. If you do not see this option, you may need to contact Jobber support to enable API access on your plan.', '')}

${step(3, 'Send Us Your API Key', 'Reply to this email with your Jobber API key. We will configure your AI Receptionist to create jobs and schedule visits directly in Jobber.', '')}

${infoBox('✅ <strong>Jobber handles everything:</strong> Since Jobber is both your calendar and CRM, this one connection lets your AI book appointments, create new clients, and log jobs automatically.')}`
  },

  'ServiceTitan Calendar': {
    subject: `Connect Your ServiceTitan — ${companyName} AI Receptionist`,
    body: `
${heading('Connect Your ServiceTitan')}
${subtext(`Your AI Receptionist for <strong style="color:${brand.white}">${companyName}</strong> will integrate directly with ServiceTitan for booking and job management.`)}

${step(1, 'Contact Your ServiceTitan Rep', 'ServiceTitan API access requires approval from your account representative. Reach out and request <strong>API access for third-party integration</strong>. Mention it is for your AI Receptionist booking system.', '')}

${step(2, 'Get Your API Credentials', 'Once approved, ServiceTitan will provide your <strong>Client ID</strong>, <strong>Client Secret</strong>, and <strong>Tenant ID</strong>. Keep these safe.', '')}

${step(3, 'Send Us Your Credentials', 'Reply to this email with your Client ID, Client Secret, and Tenant ID. All credentials are encrypted and stored securely.', '')}

${infoBox('🔒 <strong>Security:</strong> Your API credentials are encrypted with AES-256 and never stored in plain text. Only the automated integration system can access them.', brand.green)}

${infoBox('⏱️ <strong>Timeline:</strong> ServiceTitan API approval typically takes 2-5 business days. We will have everything ready on our end so activation is instant once approved.', brand.amber)}`
  },

  'Housecall Pro Calendar': {
    subject: `Connect Your Housecall Pro — ${companyName} AI Receptionist`,
    body: `
${heading('Connect Your Housecall Pro')}
${subtext(`Your AI Receptionist for <strong style="color:${brand.white}">${companyName}</strong> will book directly into Housecall Pro.`)}

${step(1, 'Log in to Housecall Pro', 'Go to <strong>housecallpro.com</strong> and sign in.', '')}

${step(2, 'Enable API Access', 'Go to <strong>Settings</strong> → <strong>Integrations</strong>. Look for the API section or contact Housecall Pro support to request API access for your account.', '')}

${step(3, 'Get Your API Key', 'Once enabled, copy your API key from the integrations page.', '')}

${step(4, 'Send Us Your API Key', 'Reply to this email with your Housecall Pro API key. We will connect your AI Receptionist within 24 hours.', '')}

${infoBox('✅ <strong>Housecall Pro handles both:</strong> Since HCP is your calendar and CRM, this single API key lets your AI book jobs, create customers, and schedule dispatches.')}`
  }
};

// CRM-only guides (for when CRM is different from calendar)
const crmGuides = {
  'Jobber': {
    subject: `Connect Your Jobber CRM — ${companyName} AI Receptionist`,
    body: `
${heading('Connect Your Jobber CRM')}
${subtext(`Your AI Receptionist for <strong style="color:${brand.white}">${companyName}</strong> needs to connect with Jobber to automatically create contacts and log jobs from phone calls.`)}

${step(1, 'Log in to Jobber', 'Go to <strong>getjobber.com</strong> and sign in.', '')}

${step(2, 'Find Your API Key', 'Go to <strong>Settings</strong> → <strong>Apps & Integrations</strong> → <strong>API Access</strong>. Copy your API key.', '')}

${step(3, 'Send Us Your API Key', 'Reply to this email with your Jobber API key.', '')}

${infoBox('📋 <strong>What happens:</strong> When your AI Receptionist books an appointment or captures a lead, the contact and job details are automatically created in Jobber.')}`
  },

  'ServiceTitan': {
    subject: `Connect Your ServiceTitan CRM — ${companyName} AI Receptionist`,
    body: `
${heading('Connect Your ServiceTitan CRM')}
${subtext(`Your AI Receptionist needs ServiceTitan API access to create customers and jobs automatically.`)}

${step(1, 'Contact Your ServiceTitan Rep', 'Request <strong>API access for third-party integration</strong>.', '')}

${step(2, 'Get Your Credentials', 'You will receive a <strong>Client ID</strong>, <strong>Client Secret</strong>, and <strong>Tenant ID</strong>.', '')}

${step(3, 'Send Them To Us', 'Reply to this email with all three credentials. They are encrypted and stored securely.', '')}

${infoBox('🔒 All credentials are AES-256 encrypted.', brand.green)}`
  },

  'Housecall Pro': {
    subject: `Connect Your Housecall Pro CRM — ${companyName} AI Receptionist`,
    body: `
${heading('Connect Your Housecall Pro CRM')}
${subtext(`Let us connect your Housecall Pro so your AI Receptionist can create customers and jobs automatically.`)}

${step(1, 'Log in to Housecall Pro', 'Go to <strong>housecallpro.com</strong> and sign in.', '')}

${step(2, 'Get Your API Key', 'Go to <strong>Settings</strong> → <strong>Integrations</strong> → copy your API key.', '')}

${step(3, 'Send It To Us', 'Reply to this email with your API key.', '')}

${infoBox('📋 Your AI will automatically push new contacts and job details to Housecall Pro after every call.')}`
  },

  'FieldEdge': {
    subject: `Connect Your FieldEdge CRM — ${companyName} AI Receptionist`,
    body: `
${heading('Connect Your FieldEdge CRM')}
${subtext(`Your AI Receptionist needs FieldEdge API access to push customer and job data automatically.`)}

${step(1, 'Contact FieldEdge Support', 'Request API access for your account. Mention it is for an AI receptionist integration.', '')}

${step(2, 'Get Your API Credentials', 'FieldEdge will provide your API key and any required authentication details.', '')}

${step(3, 'Send Them To Us', 'Reply to this email with your credentials.', '')}

${infoBox('⏱️ FieldEdge API setup typically takes 1-3 business days.', brand.amber)}`
  },

  'Kickserv': {
    subject: `Connect Your Kickserv CRM — ${companyName} AI Receptionist`,
    body: `
${heading('Connect Your Kickserv CRM')}
${subtext(`Let us connect your Kickserv account so leads and bookings flow automatically.`)}

${step(1, 'Log in to Kickserv', 'Go to <strong>kickserv.com</strong> and sign in.', '')}

${step(2, 'Find Your API Key', 'Go to <strong>Settings</strong> → <strong>API</strong> → copy your API token.', '')}

${step(3, 'Send It To Us', 'Reply to this email with your Kickserv API token.', '')}

${infoBox('📋 Your AI Receptionist will automatically create jobs and contacts in Kickserv.')}`
  }
};

// ── Build Email List ────────────────────────────────────────
const emails = [];

// Determine which calendar guide to send
if (calendarPlatform && calendarPlatform !== 'None') {
  const calGuide = calendarGuides[calendarPlatform];
  if (calGuide) {
    emails.push({
      to: clientEmail,
      subject: calGuide.subject,
      html: wrapEmail(calGuide.subject, calGuide.body),
      type: 'calendar_setup',
      platform: calendarPlatform
    });
  }
}

// Determine which CRM guide to send (only if CRM is different from calendar platform)
// e.g., if they use Google Calendar + Jobber CRM, send both guides
// But if they use Jobber Calendar (which IS Jobber CRM), don't send a separate CRM guide
const calendarIsCRM = ['Jobber Calendar', 'ServiceTitan Calendar', 'Housecall Pro Calendar'].includes(calendarPlatform);
const crmBaseName = crmPlatform.replace(' Calendar', '');

if (crmPlatform && crmPlatform !== 'None' && !calendarIsCRM) {
  const crmGuide = crmGuides[crmPlatform];
  if (crmGuide) {
    emails.push({
      to: clientEmail,
      subject: crmGuide.subject,
      html: wrapEmail(crmGuide.subject, crmGuide.body),
      type: 'crm_setup',
      platform: crmPlatform
    });
  }
}

// If no integrations selected, send a "no setup needed" note
if (emails.length === 0 && (!crmPlatform || crmPlatform === 'None') && (!calendarPlatform || calendarPlatform === 'None')) {
  // No integration emails needed — the welcome email covers it
}

return {
  setupEmails: emails,
  emailCount: emails.length,
  calendarPlatform: calendarPlatform,
  crmPlatform: crmPlatform,
  clientEmail: clientEmail,
  companyName: companyName
};
