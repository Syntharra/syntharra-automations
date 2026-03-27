// ============================================================
// Syntharra Premium — Welcome Email Builder
// ============================================================
// Sent immediately after agent creation + publish.
// Contains: welcome message, what's live, what to expect next,
// and a preview of what setup instructions are coming.
// ============================================================

const data = $input.first().json;
const companyName = data.company_name || data.companyName || 'Your Company';
const clientEmail = data.client_email || data.extractedData?.client_email || '';
const agentName = data.agent_name || data.extractedData?.agent_name || '';
const calendarPlatform = data.calendar_platform || data.extractedData?.calendar_platform || '';
const crmPlatform = data.crm_platform || data.extractedData?.crm_platform || '';
const clientName = data.owner_name || data.extractedData?.owner_name || '';

const brand = {
  violet: '#6C63FF',
  cyan: '#00D4FF',
  dark: '#0D0D1A',
  darkPanel: '#141428',
  lightText: '#E8E8F0',
  mutedText: '#9999B0',
  white: '#FFFFFF',
  green: '#10B981',
  logoUrl: 'https://i.postimg.cc/zBSrKLDb/company-logo-link.png',
  supportEmail: 'support@syntharra.com',
  website: 'www.syntharra.com'
};

const hasCalendar = calendarPlatform && calendarPlatform !== 'None';
const hasCRM = crmPlatform && crmPlatform !== 'None';
const hasIntegrations = hasCalendar || hasCRM;

// Integration status section
let integrationSection = '';
if (hasIntegrations) {
  integrationSection = `
<div style="margin:24px 0;padding:20px;background:rgba(108,99,255,0.06);border-radius:12px;border:1px solid rgba(108,99,255,0.15);">
  <h3 style="color:${brand.white};font-size:16px;margin:0 0 12px;">📋 Integration Setup — What Happens Next</h3>
  <p style="color:${brand.lightText};font-size:14px;line-height:1.6;margin:0 0 12px;">You will receive a separate email shortly with simple step-by-step instructions to connect:</p>
  <table style="width:100%;border-collapse:collapse;">
    ${hasCalendar ? `<tr>
      <td style="padding:8px 0;color:${brand.lightText};font-size:14px;">📅 <strong>Calendar:</strong> ${calendarPlatform}</td>
      <td style="padding:8px 0;text-align:right;"><span style="background:${brand.amber};color:#000;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;">Setup Required</span></td>
    </tr>` : ''}
    ${hasCRM ? `<tr>
      <td style="padding:8px 0;color:${brand.lightText};font-size:14px;">🔗 <strong>CRM:</strong> ${crmPlatform}</td>
      <td style="padding:8px 0;text-align:right;"><span style="background:${brand.amber};color:#000;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;">Setup Required</span></td>
    </tr>` : ''}
  </table>
  <p style="color:${brand.mutedText};font-size:13px;margin:12px 0 0;">Once connected, your AI Receptionist will be able to book appointments and sync customer data automatically. Until then, it will capture all caller details and notify you for manual follow-up.</p>
</div>`;
} else {
  integrationSection = `
<div style="margin:24px 0;padding:20px;background:rgba(16,185,129,0.06);border-radius:12px;border:1px solid rgba(16,185,129,0.15);">
  <p style="color:${brand.lightText};font-size:14px;line-height:1.6;margin:0;">✅ <strong>No integration setup needed.</strong> Your AI Receptionist will capture all caller details and send you notifications for each call. You can add calendar or CRM integrations at any time by contacting us.</p>
</div>`;
}

const subject = `🎉 Your AI Receptionist is Live — ${companyName}`;

const bodyContent = `
<h2 style="color:${brand.white};font-size:24px;font-weight:700;margin:0 0 8px;font-family:Georgia,'Times New Roman',serif;">Welcome to Syntharra Premium!</h2>
<p style="color:${brand.mutedText};font-size:15px;line-height:1.5;margin:0 0 24px;">${clientName ? `Hi ${clientName},` : 'Hi there,'} your AI Receptionist for <strong style="color:${brand.white}">${companyName}</strong> is now live and ready to take calls.</p>

<!-- What's Live -->
<div style="margin:0 0 24px;">
  <h3 style="color:${brand.white};font-size:16px;margin:0 0 12px;">✅ What is Live Right Now</h3>
  <table style="width:100%;border-collapse:collapse;">
    <tr>
      <td style="padding:6px 0;color:${brand.lightText};font-size:14px;">🤖 <strong>AI Agent Name:</strong></td>
      <td style="padding:6px 0;color:${brand.cyan};font-size:14px;text-align:right;">${agentName}</td>
    </tr>
    <tr>
      <td style="padding:6px 0;color:${brand.lightText};font-size:14px;">📞 <strong>Call Handling:</strong></td>
      <td style="padding:6px 0;color:${brand.green};font-size:14px;text-align:right;">Active</td>
    </tr>
    <tr>
      <td style="padding:6px 0;color:${brand.lightText};font-size:14px;">📊 <strong>Call Analysis:</strong></td>
      <td style="padding:6px 0;color:${brand.green};font-size:14px;text-align:right;">Active</td>
    </tr>
    <tr>
      <td style="padding:6px 0;color:${brand.lightText};font-size:14px;">📧 <strong>Email Notifications:</strong></td>
      <td style="padding:6px 0;color:${brand.green};font-size:14px;text-align:right;">Active</td>
    </tr>
    <tr>
      <td style="padding:6px 0;color:${brand.lightText};font-size:14px;">📅 <strong>Appointment Booking:</strong></td>
      <td style="padding:6px 0;color:${hasCalendar ? brand.amber : brand.green};font-size:14px;text-align:right;">${hasCalendar ? 'Pending Setup' : 'Lead Capture Mode'}</td>
    </tr>
  </table>
</div>

${integrationSection}

<!-- How It Works -->
<div style="margin:24px 0;">
  <h3 style="color:${brand.white};font-size:16px;margin:0 0 12px;">📖 How It Works</h3>
  <p style="color:${brand.lightText};font-size:14px;line-height:1.7;margin:0;">When someone calls your business number, your AI Receptionist answers professionally, identifies what the caller needs, collects their details, and ${hasCalendar ? 'books appointments directly into your calendar' : 'captures all their information for your team'}. After each call, you receive a detailed notification by email${hasCRM ? ' and the contact is synced to your CRM' : ''}.</p>
</div>

<!-- Support -->
<div style="margin:24px 0;padding:16px;background:rgba(0,212,255,0.06);border-radius:12px;border:1px solid rgba(0,212,255,0.15);">
  <p style="color:${brand.lightText};font-size:14px;line-height:1.6;margin:0;">💬 <strong>Questions?</strong> Just reply to this email. Our team typically responds within a few hours during business hours. You can also email us directly at <a href="mailto:${brand.supportEmail}" style="color:${brand.cyan};text-decoration:none;">${brand.supportEmail}</a>.</p>
</div>

<p style="color:${brand.mutedText};font-size:13px;margin:24px 0 0;text-align:center;">— The Syntharra Team</p>`;

const html = `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:${brand.dark};font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:${brand.dark};padding:32px 16px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
<tr><td style="padding:24px 32px;text-align:center;">
  <img src="${brand.logoUrl}" alt="Syntharra" width="180" style="display:block;margin:0 auto 8px;">
  <p style="color:${brand.mutedText};font-size:13px;margin:0;">AI Receptionist for the Trades</p>
</td></tr>
<tr><td style="background:${brand.darkPanel};border-radius:16px;border:1px solid rgba(108,99,255,0.2);overflow:hidden;">
<div style="height:4px;background:linear-gradient(90deg,${brand.violet},${brand.cyan});"></div>
<div style="padding:32px;">${bodyContent}</div>
</td></tr>
<tr><td style="padding:24px 32px;text-align:center;">
  <p style="color:${brand.mutedText};font-size:12px;margin:0 0 4px;">Need help? Reply to this email or contact us at ${brand.supportEmail}</p>
  <p style="color:${brand.mutedText};font-size:12px;margin:0;">${brand.website} | Syntharra AI Solutions</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>`;

return {
  welcomeEmail: {
    to: clientEmail,
    subject: subject,
    html: html
  },
  companyName: companyName,
  clientEmail: clientEmail
};
