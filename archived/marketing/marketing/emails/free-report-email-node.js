// Website Lead → Free Report Email (SMTP2GO) — APPROVED BRANDING
const input = $input.first().json;
const email = input.email || input.lead_email || '';
if (!email) { return { sent: false }; }

const LOGO = `<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr>
  <td style="vertical-align:middle;padding-right:10px">
    <img src="https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png" alt="" width="36" height="36" style="display:block;border:0">
  </td>
  <td style="vertical-align:middle;text-align:left">
    <table cellpadding="0" cellspacing="0" border="0"><tr><td style="text-align:left;padding:0;margin:0">
      <div style="font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:16px;font-weight:700;letter-spacing:-0.3px;color:#0f0f1a;line-height:1;text-align:left">Syntharra</div>
    </td></tr><tr><td style="text-align:left;padding:3px 0 0 0;margin:0">
      <div style="font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:7.5px;font-weight:600;letter-spacing:1.2px;color:#6C63FF;text-transform:uppercase;line-height:1;text-align:left">Global AI Solutions</div>
    </td></tr></table>
  </td>
</tr></table>`;

const freeReportHtml = `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700&display=swap" rel="stylesheet"></head>
<body style="margin:0;padding:0;background-color:#F7F7FB;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F7F7FB;padding:40px 16px"><tr><td align="center">
<table width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%">
<tr><td style="padding:0 0 24px;text-align:center">${LOGO}</td></tr>
<tr><td style="background-color:#ffffff;border-radius:12px;border:1px solid #E5E7EB;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
<div style="height:3px;background:linear-gradient(90deg,#6C63FF,#8B7FFF)"></div>
<div style="padding:32px 36px">
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px"><tr><td>
  <span style="display:inline-block;font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#6C63FF;background-color:#F0EEFF;padding:4px 12px;border-radius:20px">Free Report</span>
</td></tr></table>
<h1 style="color:#1A1A2E;font-size:24px;font-weight:700;margin:0 0 6px;line-height:1.3">The Hidden Cost of Missed Calls in the Trade Industry</h1>
<p style="color:#6B7280;font-size:14px;line-height:1.6;margin:0 0 28px">You requested this report from syntharra.com. Here\u2019s what the data shows.</p>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;background-color:#F0EEFF;border-radius:12px;overflow:hidden"><tr><td style="padding:28px;text-align:center">
  <p style="font-size:12px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#6C63FF;margin:0 0 8px">Average trade business loses</p>
  <div style="font-size:44px;font-weight:700;color:#EF4444;line-height:1">$8,400 \u2014 $21,000</div>
  <p style="font-size:14px;color:#6B7280;margin:8px 0 0">per month in missed call revenue</p>
</td></tr></table>
<h2 style="font-size:17px;font-weight:700;color:#1A1A2E;margin:0 0 16px">How we calculated this</h2>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;border:1px solid #E5E7EB;border-radius:10px;overflow:hidden">
<tr><td style="padding:14px 20px;border-bottom:1px solid #E5E7EB;background-color:#FAFAFA;font-size:12px;font-weight:700;color:#6B7280;letter-spacing:0.05em;text-transform:uppercase" colspan="2">Industry Averages</td></tr>
<tr><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;color:#1A1A2E;font-size:14px">Inbound calls per week</td><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;text-align:right;font-weight:600;color:#1A1A2E;font-size:14px">35 \u2014 60</td></tr>
<tr><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;color:#1A1A2E;font-size:14px">Calls missed</td><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;text-align:right;font-weight:700;color:#EF4444;font-size:14px">30 \u2014 40%</td></tr>
<tr><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;color:#1A1A2E;font-size:14px">Callers who leave a voicemail</td><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;text-align:right;font-weight:700;color:#EF4444;font-size:14px">Only 38%</td></tr>
<tr><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;color:#1A1A2E;font-size:14px">Callers who try a competitor</td><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;text-align:right;font-weight:700;color:#EF4444;font-size:14px">85%</td></tr>
<tr><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;color:#1A1A2E;font-size:14px">Average job value</td><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;text-align:right;font-weight:600;color:#1A1A2E;font-size:14px">$250 \u2014 $500</td></tr>
<tr><td style="padding:14px 20px;background-color:#ffffff;color:#1A1A2E;font-size:14px;font-weight:600">Estimated monthly loss</td><td style="padding:14px 20px;background-color:#ffffff;text-align:right;font-weight:700;color:#EF4444;font-size:18px">$8,400 \u2014 $21,000</td></tr>
</table>
<h2 style="font-size:17px;font-weight:700;color:#1A1A2E;margin:0 0 16px">When are you missing calls?</h2>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px"><tr>
  <td style="width:32%;background-color:#FEF2F2;border-radius:10px;padding:16px;text-align:center"><div style="font-size:24px;font-weight:700;color:#EF4444">42%</div><div style="font-size:11px;color:#991B1B;margin-top:4px;font-weight:600">After hours</div></td>
  <td style="width:2%"></td>
  <td style="width:32%;background-color:#FEF3C7;border-radius:10px;padding:16px;text-align:center"><div style="font-size:24px;font-weight:700;color:#F59E0B">35%</div><div style="font-size:11px;color:#92400E;margin-top:4px;font-weight:600">On the job</div></td>
  <td style="width:2%"></td>
  <td style="width:32%;background-color:#F0EEFF;border-radius:10px;padding:16px;text-align:center"><div style="font-size:24px;font-weight:700;color:#6C63FF">23%</div><div style="font-size:11px;color:#3C3489;margin-top:4px;font-weight:600">Weekends</div></td>
</tr></table>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;background-color:#ECFDF5;border-radius:12px;overflow:hidden"><tr><td style="padding:24px">
  <h2 style="font-size:17px;font-weight:700;color:#065F46;margin:0 0 10px">The fix takes 24 hours</h2>
  <p style="font-size:14px;color:#047857;line-height:1.7;margin:0 0 16px">An AI receptionist answers every call instantly, 24/7. It captures the caller\u2019s name, number, address, and what they need, then alerts you within seconds.</p>
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td style="width:48%;background-color:#ffffff;border-radius:8px;padding:14px;text-align:center"><div style="font-size:11px;color:#6B7280;font-weight:600;text-transform:uppercase">Without AI</div><div style="font-size:20px;font-weight:700;color:#EF4444;margin:4px 0">60-70%</div><div style="font-size:11px;color:#6B7280">calls answered</div></td>
    <td style="width:4%"></td>
    <td style="width:48%;background-color:#ffffff;border-radius:8px;padding:14px;text-align:center"><div style="font-size:11px;color:#6B7280;font-weight:600;text-transform:uppercase">With Syntharra</div><div style="font-size:20px;font-weight:700;color:#10B981;margin:4px 0">100%</div><div style="font-size:11px;color:#6B7280">calls answered</div></td>
  </tr></table>
</td></tr></table>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px"><tr>
  <td style="background-color:#F7F7FB;border-radius:10px;padding:16px;text-align:center;width:48%"><div style="font-size:13px;color:#6B7280;margin-bottom:4px">Starts at</div><div style="font-size:28px;font-weight:700;color:#6C63FF">$497</div><div style="font-size:12px;color:#6B7280">/month</div></td>
  <td style="width:4%"></td>
  <td style="background-color:#F7F7FB;border-radius:10px;padding:16px;text-align:center;width:48%"><div style="font-size:13px;color:#6B7280;margin-bottom:4px">Typical return</div><div style="font-size:28px;font-weight:700;color:#10B981">17x</div><div style="font-size:12px;color:#6B7280">ROI</div></td>
</tr></table>
<div style="text-align:center;margin:0 0 12px"><a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" style="display:inline-block;background-color:#6C63FF;color:#ffffff;padding:16px 44px;border-radius:10px;text-decoration:none;font-weight:700;font-size:16px;box-shadow:0 4px 14px rgba(108,99,255,0.35)">See It Live \u2014 Book a Free Demo</a></div>
<p style="text-align:center;font-size:12px;color:#9CA3AF;margin:12px 0 0">15 minutes. No commitment. We\u2019ll show you how it works with your business name.</p>
</div></td></tr>
<tr><td style="padding:20px;text-align:center"><a href="https://checkout.syntharra.com/" style="color:#6C63FF;font-size:13px;font-weight:600;text-decoration:none;margin:0 10px">View Pricing</a><span style="color:#D1D5DB"> | </span><a href="https://www.syntharra.com/demo.html" style="color:#6C63FF;font-size:13px;font-weight:600;text-decoration:none;margin:0 10px">Try the AI Demo</a></td></tr>
<tr><td style="text-align:center"><p style="color:#9CA3AF;font-size:11px;margin:0;line-height:1.6">Syntharra AI Solutions<br><a href="https://www.syntharra.com" style="color:#6C63FF;text-decoration:none">syntharra.com</a> &middot; <a href="mailto:support@syntharra.com" style="color:#6C63FF;text-decoration:none">support@syntharra.com</a></p></td></tr>
</table></td></tr></table></body></html>`;

const SMTP2GO_KEY = 'api-0BE30DA64A074BC79F28BE6AEDC9DB9E';
try {
  await this.helpers.httpRequest({
    method: 'POST', url: 'https://api.smtp2go.com/v3/email/send',
    headers: { 'Content-Type': 'application/json' },
    body: { api_key: SMTP2GO_KEY, sender: 'Syntharra AI <noreply@syntharra.com>', to: [email],
      subject: 'Your Free Report: The Hidden Cost of Missed Calls', html_body: freeReportHtml },
    json: true
  });
  return { ...input, _report_sent: true };
} catch (e) { return { ...input, _report_sent: false, _error: e.message }; }
