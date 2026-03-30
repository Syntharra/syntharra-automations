// ============================================================
// Syntharra Premium — Welcome Email v2 (Light Theme)
// ============================================================

const data = $input.first().json;
const companyName = data.company_name || data.companyName || '';
const clientEmail = data.client_email || data.extractedData?.client_email || '';
const agentName = data.agent_name || data.extractedData?.agent_name || '';
const calendarPlatform = data.calendar_platform || data.extractedData?.calendar_platform || '';
const crmPlatform = data.crm_platform || data.extractedData?.crm_platform || '';
const clientName = data.owner_name || data.extractedData?.owner_name || '';

const v = '#6C63FF';
const bg = '#F7F7FB';
const card = '#FFFFFF';
const text = '#1A1A2E';
const muted = '#6B7280';
const border = '#E5E7EB';
const green = '#10B981';
const amber = '#F59E0B';
const ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png';
const LOGO = `<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td style="vertical-align:middle;padding-right:10px"><img src="${ICON_URL}" alt="" width="36" height="36" style="display:block;border:0"></td><td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="text-align:left;padding:0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:16px;font-weight:700;letter-spacing:-0.3px;color:#0f0f1a;line-height:1;text-align:left">Syntharra</div></td></tr><tr><td style="text-align:left;padding:3px 0 0 0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:7.5px;font-weight:600;letter-spacing:1.2px;color:#6C63FF;text-transform:uppercase;line-height:1;text-align:left">Global AI Solutions</div></td></tr></table></td></tr></table>`;

const hasCalendar = calendarPlatform && calendarPlatform !== 'None';
const hasCRM = crmPlatform && crmPlatform !== 'None';

let integrationNote = '';
if (hasCalendar || hasCRM) {
  let items = '';
  if (hasCalendar) items += `<tr><td style="padding:6px 0;color:${text};font-size:14px;">📅 ${calendarPlatform}</td><td style="padding:6px 0;text-align:right;"><span style="background:#FFF7ED;color:#92400E;padding:2px 10px;border-radius:10px;font-size:12px;font-weight:600;">Setup email sent</span></td></tr>`;
  if (hasCRM) items += `<tr><td style="padding:6px 0;color:${text};font-size:14px;">🔗 ${crmPlatform}</td><td style="padding:6px 0;text-align:right;"><span style="background:#FFF7ED;color:#92400E;padding:2px 10px;border-radius:10px;font-size:12px;font-weight:600;">Setup email sent</span></td></tr>`;

  integrationNote = `
<div style="margin:20px 0;padding:16px;background:#F0EFFF;border-radius:8px;">
  <p style="color:${text};font-size:14px;font-weight:600;margin:0 0 8px;">📋 Integration Setup</p>
  <p style="color:${muted};font-size:13px;line-height:1.5;margin:0 0 10px;">You have received a separate email with simple instructions to connect your tools. Most take under 60 seconds.</p>
  <table style="width:100%;border-collapse:collapse;">${items}</table>
  <p style="color:${muted};font-size:12px;margin:10px 0 0;">Until connected, your AI will capture all caller details and notify you for manual follow-up.</p>
</div>`;
}

const subject = `Your AI Receptionist is Live — ${companyName}`;

const bodyContent = `
<h2 style="color:${text};font-size:22px;font-weight:700;margin:0 0 6px;">Welcome to Syntharra Premium</h2>
<p style="color:${muted};font-size:15px;line-height:1.5;margin:0 0 24px;">${clientName ? `Hi ${clientName},` : 'Hi,'} your AI Receptionist for <strong style="color:${text}">${companyName}</strong> is now live.</p>

<div style="margin:0 0 20px;">
  <table style="width:100%;border-collapse:collapse;">
    <tr><td style="padding:8px 0;color:${text};font-size:14px;border-bottom:1px solid ${border};">🤖 Agent</td><td style="padding:8px 0;text-align:right;color:${v};font-size:14px;font-weight:600;border-bottom:1px solid ${border};">${agentName}</td></tr>
    <tr><td style="padding:8px 0;color:${text};font-size:14px;border-bottom:1px solid ${border};">📞 Calls</td><td style="padding:8px 0;text-align:right;color:${green};font-size:14px;font-weight:600;border-bottom:1px solid ${border};">Active</td></tr>
    <tr><td style="padding:8px 0;color:${text};font-size:14px;border-bottom:1px solid ${border};">📊 Analysis</td><td style="padding:8px 0;text-align:right;color:${green};font-size:14px;font-weight:600;border-bottom:1px solid ${border};">Active</td></tr>
    <tr><td style="padding:8px 0;color:${text};font-size:14px;border-bottom:1px solid ${border};">📧 Notifications</td><td style="padding:8px 0;text-align:right;color:${green};font-size:14px;font-weight:600;border-bottom:1px solid ${border};">Active</td></tr>
    <tr><td style="padding:8px 0;color:${text};font-size:14px;">📅 Booking</td><td style="padding:8px 0;text-align:right;color:${hasCalendar ? amber : green};font-size:14px;font-weight:600;">${hasCalendar ? 'Pending Setup' : 'Lead Capture'}</td></tr>
  </table>
</div>

${integrationNote}

<div style="margin:20px 0;padding:14px 16px;background:#F9FAFB;border-radius:8px;border:1px solid ${border};">
  <p style="color:${text};font-size:13px;line-height:1.6;margin:0;">💬 <strong>Questions?</strong> Reply to this email anytime. We typically respond within a few hours.</p>
</div>

<p style="color:${muted};font-size:13px;margin:20px 0 0;text-align:center;">— The Syntharra Team</p>`;

const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
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
  <p style="color:${muted};font-size:12px;margin:0;">support@syntharra.com | www.syntharra.com</p>
</td></tr>
</table></td></tr></table></body></html>`;

return {
  welcomeEmail: { to: clientEmail, subject, html },
  companyName, clientEmail
};
