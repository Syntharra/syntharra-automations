// ── Usage Alert Email ──
const d = $input.first().json;
const companyName = d.company_name || 'your company';
const minutesUsed = d.minutes_used || 0;
const minutesIncluded = d.minutes_included || 475;
const usagePct = Math.round((minutesUsed / minutesIncluded) * 100);
const resetDate = d.billing_cycle_reset || 'the 1st of next month';

const ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png';
const LOGO = `<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td style="vertical-align:middle;padding-right:10px"><img src="${ICON_URL}" alt="" width="36" height="36" style="display:block;border:0"></td><td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="text-align:left;padding:0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:16px;font-weight:700;letter-spacing:-0.3px;color:#0f0f1a;line-height:1;text-align:left">Syntharra</div></td></tr><tr><td style="text-align:left;padding:3px 0 0 0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:7.5px;font-weight:600;letter-spacing:1.2px;color:#6C63FF;text-transform:uppercase;line-height:1;text-align:left">Global AI Solutions</div></td></tr></table></td></tr></table>`;
const FOOTER = `<tr><td style="padding:20px;text-align:center"><a href="https://www.syntharra.com" style="color:#6C63FF;font-size:13px;font-weight:600;text-decoration:none">syntharra.com</a></td></tr><tr><td style="text-align:center;padding:0 0 16px"><p style="color:#9CA3AF;font-size:11px;margin:0">Syntharra AI Solutions</p></td></tr>`;

const emailHtml = `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700&display=swap" rel="stylesheet"></head>
<body style="margin:0;padding:0;background-color:#F7F7FB;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F7F7FB;padding:40px 16px"><tr><td align="center">
<table width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%">
<tr><td style="padding:0 0 24px;text-align:center">${LOGO}</td></tr>
<tr><td style="background-color:#ffffff;border-radius:12px;border:1px solid #E5E7EB;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
<div style="height:3px;background:linear-gradient(90deg,#6C63FF,#8B7FFF)"></div>
<div style="padding:32px 36px">
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:16px"><tr><td><span style="display:inline-block;font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#6C63FF;background-color:#F0EEFF;padding:4px 12px;border-radius:20px">Usage Alert</span></td></tr></table>
<h1 style="color:#1A1A2E;font-size:24px;font-weight:700;margin:0 0 6px;line-height:1.3">You\u2019re at ${usagePct}% of Your Minutes</h1>
<p style="color:#6B7280;font-size:14px;line-height:1.6;margin:0 0 24px">Your AI Receptionist for ${companyName} has used ${minutesUsed} of your ${minutesIncluded} included minutes this billing cycle.</p>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px"><tr><td>
  <div style="background-color:#E5E7EB;border-radius:6px;height:12px;overflow:hidden"><div style="background:linear-gradient(90deg,#6C63FF,${usagePct >= 90 ? '#EF4444' : '#F59E0B'});height:12px;width:${usagePct}%;border-radius:6px"></div></div>
  <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:8px"><tr>
    <td style="font-size:13px;color:#1A1A2E;font-weight:600">${minutesUsed} min used</td>
    <td style="font-size:13px;color:#6B7280;text-align:right">${minutesIncluded} min included</td>
  </tr></table>
</td></tr></table>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;background-color:#FEF3C7;border-radius:10px;overflow:hidden"><tr><td style="padding:18px 22px">
  <p style="font-size:14px;color:#92400E;line-height:1.6;margin:0"><strong>What happens if you go over?</strong> Overage minutes are billed at $0.25/min at the end of your billing cycle. No interruption to service \u2014 your AI Receptionist keeps answering calls.</p>
</td></tr></table>
<p style="color:#6B7280;font-size:14px;line-height:1.6;margin:0 0 16px">Billing cycle resets: <strong style="color:#1A1A2E">${resetDate}</strong></p>
<p style="color:#6B7280;font-size:13px;margin:0">Questions about your usage? Email <a href="mailto:support@syntharra.com" style="color:#6C63FF;font-weight:600;text-decoration:none">support@syntharra.com</a></p>
</div></td></tr>
${FOOTER}
</table></td></tr></table></body></html>`;

return [{ json: { ...d, emailHtml, emailSubject: `\u26a0\ufe0f Usage Alert \u2014 ${usagePct}% of Minutes Used | ${companyName}` } }];
