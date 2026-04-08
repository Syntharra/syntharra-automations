// Syntharra Approved Email Branding — 2026-03-28
// DO NOT MODIFY without Dan's approval

const ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png';

const LOGO = `<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr>
  <td style="vertical-align:middle;padding-right:10px"><img src="${ICON_URL}" alt="" width="36" height="36" style="display:block;border:0"></td>
  <td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="text-align:left;padding:0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:16px;font-weight:700;letter-spacing:-0.3px;color:#0f0f1a;line-height:1;text-align:left">Syntharra</div></td></tr><tr><td style="text-align:left;padding:3px 0 0 0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:7.5px;font-weight:600;letter-spacing:1.2px;color:#6C63FF;text-transform:uppercase;line-height:1;text-align:left">Global AI Solutions</div></td></tr></table></td>
</tr></table>`;

const FOOTER = `<tr><td style="padding:20px;text-align:center"><a href="https://www.syntharra.com" style="color:#6C63FF;font-size:13px;font-weight:600;text-decoration:none">syntharra.com</a></td></tr>
<tr><td style="text-align:center;padding:0 0 16px"><p style="color:#9CA3AF;font-size:11px;margin:0">Syntharra AI Solutions \u2014 AI Receptionists for the Trade Industry</p></td></tr>`;

function wrapEmail(badge, content) {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700&display=swap" rel="stylesheet"></head>
<body style="margin:0;padding:0;background-color:#F7F7FB;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F7F7FB;padding:40px 16px"><tr><td align="center">
<table width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%">
<tr><td style="padding:0 0 24px;text-align:center">${LOGO}</td></tr>
<tr><td style="background-color:#ffffff;border-radius:12px;border:1px solid #E5E7EB;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
<div style="height:3px;background:linear-gradient(90deg,#6C63FF,#8B7FFF)"></div>
<div style="padding:32px 36px">
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:16px"><tr><td>
  <span style="display:inline-block;font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#6C63FF;background-color:#F0EEFF;padding:4px 12px;border-radius:20px">${badge}</span>
</td></tr></table>
${content}
</div></td></tr>
${FOOTER}
</table></td></tr></table></body></html>`;
}

const SMTP2GO_KEY = 'api-0BE30DA64A074BC79F28BE6AEDC9DB9E';

async function sendEmail(helpers, to, subject, html, attachments) {
  const body = { api_key: SMTP2GO_KEY, sender: 'Syntharra AI <noreply@syntharra.com>', to: [to], subject, html_body: html };
  if (attachments) body.attachments = attachments;
  await helpers.httpRequest({ method: 'POST', url: 'https://api.smtp2go.com/v3/email/send', headers: { 'Content-Type': 'application/json' }, body, json: true });
}
