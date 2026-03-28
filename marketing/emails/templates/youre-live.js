// ── You're Live Email — Standard + Premium ──
// Dynamic variables from Jotform onboarding + agent creation
const input = $input.first().json;
const companyName = input.company_name || 'your company';
const agentName = input.agent_name || 'your AI Receptionist';
const phone = input.agent_phone_number || '';
const leadEmail = input.lead_email || '';
const planName = input.plan_name || 'Standard';

if (!leadEmail || !phone) {
  return [{ json: { ...input, _skip: true, _reason: 'missing email or phone' } }];
}

const digits = phone.replace(/\D/g, '');
const d = digits.slice(-10);
const displayNum = '+1 (' + d.slice(0,3) + ') ' + d.slice(3,6) + '-' + d.slice(6);

const QR_IPHONE = 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&color=6C63FF&data=' + encodeURIComponent('App-Prefs:root=Phone&path=CALL_FORWARDING');
const QR_ANDROID = 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&color=6C63FF&data=' + encodeURIComponent('tel:**21*' + digits + '#');

const ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png';
const LOGO = `<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td style="vertical-align:middle;padding-right:10px"><img src="${ICON_URL}" alt="" width="36" height="36" style="display:block;border:0"></td><td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="text-align:left;padding:0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:16px;font-weight:700;letter-spacing:-0.3px;color:#0f0f1a;line-height:1;text-align:left">Syntharra</div></td></tr><tr><td style="text-align:left;padding:3px 0 0 0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:7.5px;font-weight:600;letter-spacing:1.2px;color:#6C63FF;text-transform:uppercase;line-height:1;text-align:left">Global AI Solutions</div></td></tr></table></td></tr></table>`;
const FOOTER = `<tr><td style="padding:20px;text-align:center"><a href="https://www.syntharra.com" style="color:#6C63FF;font-size:13px;font-weight:600;text-decoration:none">syntharra.com</a></td></tr><tr><td style="text-align:center;padding:0 0 16px"><p style="color:#9CA3AF;font-size:11px;margin:0">Syntharra AI Solutions \u2014 AI Receptionists for the Trade Industry</p></td></tr>`;

const premiumNote = planName === 'Premium' ? `
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;background-color:#F0EEFF;border-radius:10px;overflow:hidden"><tr><td style="padding:16px 22px">
  <p style="font-size:13px;font-weight:700;color:#6C63FF;margin:0 0 6px">Premium Features Active</p>
  <p style="font-size:12px;color:#6B7280;line-height:1.5;margin:0">\u2713 Calendar integration \u2022 \u2713 Smart dispatching \u2022 \u2713 CRM sync</p>
</td></tr></table>` : '';

const emailHtml = `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700&display=swap" rel="stylesheet"></head>
<body style="margin:0;padding:0;background-color:#F7F7FB;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F7F7FB;padding:40px 16px"><tr><td align="center">
<table width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%">
<tr><td style="padding:0 0 24px;text-align:center">${LOGO}</td></tr>
<tr><td style="background-color:#ffffff;border-radius:12px;border:1px solid #E5E7EB;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
<div style="height:3px;background:linear-gradient(90deg,#6C63FF,#8B7FFF)"></div>
<div style="padding:32px 36px">
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:16px"><tr><td><span style="display:inline-block;font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#6C63FF;background-color:#F0EEFF;padding:4px 12px;border-radius:20px">You\u2019re Live</span></td></tr></table>
<h1 style="color:#1A1A2E;font-size:24px;font-weight:700;margin:0 0 6px;line-height:1.3">Your AI Receptionist is Live!</h1>
<p style="color:#6B7280;font-size:14px;line-height:1.6;margin:0 0 24px">Great news \u2014 ${agentName} is configured and answering calls 24/7 for ${companyName}. Forward your business number to get started.</p>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;background-color:#ECFDF5;border-radius:10px;overflow:hidden"><tr><td style="padding:16px 22px">
  <p style="margin:4px 0;font-size:13px;color:#047857"><strong style="color:#065F46">Agent:</strong> ${agentName}</p>
  <p style="margin:4px 0;font-size:13px;color:#047857"><strong style="color:#065F46">Status:</strong> \u2705 Active \u2014 Answering calls 24/7</p>
</td></tr></table>
${premiumNote}
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;background-color:#F0EEFF;border-radius:12px;overflow:hidden"><tr><td style="padding:22px;text-align:center">
  <p style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#6C63FF;margin:0 0 6px">Your AI Receptionist Number</p>
  <p style="font-size:26px;font-weight:700;color:#1A1A2E;margin:0;letter-spacing:0.5px">${displayNum}</p>
  <p style="font-size:12px;color:#6B7280;margin:8px 0 0">Forward your existing business number to this number</p>
</td></tr></table>
<h2 style="font-size:17px;font-weight:700;color:#1A1A2E;margin:0 0 4px">Quick Setup \u2014 Scan to Activate</h2>
<p style="color:#6B7280;font-size:13px;line-height:1.5;margin:0 0 16px">Open your phone camera and scan the QR code for your device.</p>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:8px"><tr>
  <td style="width:48%;background-color:#F9F9FC;border:1px solid #E5E7EB;border-radius:10px;padding:18px;text-align:center;vertical-align:top">
    <p style="font-size:13px;font-weight:700;color:#1A1A2E;margin:0 0 10px">\ud83d\udcf1 iPhone</p>
    <img src="${QR_IPHONE}" width="120" height="120" style="display:block;margin:0 auto 10px;border-radius:8px" alt="iPhone QR">
    <p style="font-size:11px;color:#6B7280;line-height:1.4;margin:0">Opens Call Forwarding settings directly</p>
  </td>
  <td style="width:4%"></td>
  <td style="width:48%;background-color:#F9F9FC;border:1px solid #E5E7EB;border-radius:10px;padding:18px;text-align:center;vertical-align:top">
    <p style="font-size:13px;font-weight:700;color:#1A1A2E;margin:0 0 10px">\ud83e\udd16 Android</p>
    <img src="${QR_ANDROID}" width="120" height="120" style="display:block;margin:0 auto 10px;border-radius:8px" alt="Android QR">
    <p style="font-size:11px;color:#6B7280;line-height:1.4;margin:0">Dials the forwarding code automatically</p>
  </td>
</tr></table>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px"><tr>
  <td style="width:48%;vertical-align:top;padding:8px 4px 0 0">
    <p style="font-size:11px;color:#6B7280;line-height:1.5;margin:0 0 3px">\u2022 Scan QR with your camera</p>
    <p style="font-size:11px;color:#6B7280;line-height:1.5;margin:0 0 3px">\u2022 Toggle Call Forwarding on</p>
    <p style="font-size:11px;color:#6B7280;line-height:1.5;margin:0">\u2022 Enter <strong style="color:#1A1A2E">${displayNum}</strong></p>
  </td>
  <td style="width:4%"></td>
  <td style="width:48%;vertical-align:top;padding:8px 0 0 4px">
    <p style="font-size:11px;color:#6B7280;line-height:1.5;margin:0 0 3px">\u2022 Scan QR with your camera</p>
    <p style="font-size:11px;color:#6B7280;line-height:1.5;margin:0 0 3px">\u2022 It dials the code for you</p>
    <p style="font-size:11px;color:#6B7280;line-height:1.5;margin:0">\u2022 Wait for confirmation tone</p>
  </td>
</tr></table>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;background-color:#ECFDF5;border-radius:10px;overflow:hidden"><tr><td style="padding:18px 22px">
  <p style="font-size:14px;font-weight:700;color:#065F46;margin:0 0 8px">\u2705 What happens once forwarding is active</p>
  <p style="font-size:13px;color:#047857;line-height:1.6;margin:0 0 4px">\u2022 Every call answered instantly by ${agentName}</p>
  <p style="font-size:13px;color:#047857;line-height:1.6;margin:0 0 4px">\u2022 Lead alerts emailed to you within 30 seconds</p>
  <p style="font-size:13px;color:#047857;line-height:1.6;margin:0">\u2022 Weekly call summary report every Monday</p>
</td></tr></table>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;background-color:#6C63FF;border-radius:10px;overflow:hidden"><tr><td style="padding:18px 22px">
  <p style="font-size:14px;font-weight:700;color:#ffffff;margin:0 0 6px">\ud83d\udcce Full Setup Guide Attached</p>
  <p style="font-size:13px;color:rgba(255,255,255,0.85);line-height:1.5;margin:0">We\u2019ve attached a detailed PDF with step-by-step instructions for every carrier, VoIP provider, landline, and business phone system \u2014 including scannable QR codes. Save it or share it with your team.</p>
</td></tr></table>
<p style="color:#6B7280;font-size:13px;line-height:1.6;margin:0">Need help? Email us at <a href="mailto:support@syntharra.com" style="color:#6C63FF;font-weight:600;text-decoration:none">support@syntharra.com</a></p>
</div></td></tr>
${FOOTER}
</table></td></tr></table></body></html>`;

return [{ json: { ...input, emailHtml, emailSubject: `Your AI Receptionist is Live \u2014 ${companyName}`, lead_email: leadEmail } }];
