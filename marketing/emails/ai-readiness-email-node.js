// AI Readiness Score → Results Email (SMTP2GO) — Light Theme
const input = $input.first().json;
const email = input.email || '';
const score = input.score || 0;
const scoreLabel = input.score_label || 'Calculated';
const scoreExplanation = input.score_explanation || '';

if (!email) { return { sent: false }; }

const scoreColor = score >= 75 ? '#10B981' : score >= 50 ? '#6C63FF' : score >= 30 ? '#F59E0B' : '#6B7280';
const scoreBg = score >= 75 ? '#ECFDF5' : score >= 50 ? '#F0EEFF' : score >= 30 ? '#FEF3C7' : '#F3F4F6';

const emailHtml = `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#F7F7FB;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F7F7FB;padding:40px 16px"><tr><td align="center">
<table width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%">
<tr><td style="padding:0 0 24px;text-align:center">
  <img src="data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgODAgODAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3QgeD0iNCIgeT0iNTYiIHdpZHRoPSIxMiIgaGVpZ2h0PSIyMCIgcng9IjQiIGZpbGw9IiM2QzYzRkYiLz48cmVjdCB4PSIyMiIgeT0iNDAiIHdpZHRoPSIxMiIgaGVpZ2h0PSIzNiIgcng9IjQiIGZpbGw9IiM2QzYzRkYiLz48cmVjdCB4PSI0MCIgeT0iMjQiIHdpZHRoPSIxMiIgaGVpZ2h0PSI1MiIgcng9IjQiIGZpbGw9IiM2QzYzRkYiLz48cmVjdCB4PSI1OCIgeT0iNCIgd2lkdGg9IjEyIiBoZWlnaHQ9IjcyIiByeD0iNCIgZmlsbD0iIzZDNjNGRiIvPjwvc3ZnPg==" alt="Syntharra" width="36" height="36" style="display:block;margin:0 auto">
</td></tr>
<tr><td style="background:#ffffff;border-radius:12px;border:1px solid #E5E7EB;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
<div style="height:3px;background:linear-gradient(90deg,#6C63FF,#8B7FFF)"></div>
<div style="padding:32px 36px">
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px"><tr><td>
  <span style="display:inline-block;font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#6C63FF;background:#F0EEFF;padding:4px 12px;border-radius:20px">Your AI Readiness Results</span>
</td></tr></table>
<h1 style="color:#1A1A2E;font-size:24px;font-weight:700;margin:0 0 6px;line-height:1.3">Here\u2019s Your Score</h1>
<p style="color:#6B7280;font-size:14px;line-height:1.6;margin:0 0 28px">Based on your answers, here\u2019s how AI-ready your business is \u2014 and what it means for your revenue.</p>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px"><tr><td style="text-align:center">
  <div style="display:inline-block;width:120px;height:120px;border-radius:50%;background:${scoreBg};border:4px solid ${scoreColor};line-height:120px;text-align:center"><span style="font-size:44px;font-weight:700;color:${scoreColor}">${score}</span></div>
  <p style="font-size:18px;font-weight:700;color:#1A1A2E;margin:14px 0 4px">${scoreLabel}</p>
  <p style="font-size:13px;color:#6B7280;margin:0">out of 100</p>
</td></tr></table>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;background:#F9F9FC;border-radius:10px;overflow:hidden"><tr><td style="padding:20px">
  <p style="font-size:14px;color:#1A1A2E;line-height:1.7;margin:0">${scoreExplanation}</p>
</td></tr></table>
<h2 style="font-size:17px;font-weight:700;color:#1A1A2E;margin:0 0 16px">The Numbers Behind Your Score</h2>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;border:1px solid #E5E7EB;border-radius:10px;overflow:hidden">
<tr><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background:#fff;color:#1A1A2E;font-size:14px">Average missed calls per week</td><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background:#fff;text-align:right;font-weight:700;color:#EF4444;font-size:14px">12 calls</td></tr>
<tr><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background:#fff;color:#1A1A2E;font-size:14px">Average job value in trades</td><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background:#fff;text-align:right;font-weight:600;color:#1A1A2E;font-size:14px">$350</td></tr>
<tr><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background:#fff;color:#1A1A2E;font-size:14px">Estimated monthly revenue lost</td><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background:#fff;text-align:right;font-weight:700;color:#EF4444;font-size:18px">$16,800</td></tr>
<tr><td style="padding:12px 20px;background:#fff;color:#1A1A2E;font-size:14px">Revenue recoverable with AI</td><td style="padding:12px 20px;background:#fff;text-align:right;font-weight:700;color:#10B981;font-size:18px">$14,280+</td></tr>
</table>
<h2 style="font-size:17px;font-weight:700;color:#1A1A2E;margin:0 0 16px">3 Quick Wins to Stop Losing Calls</h2>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px"><tr><td style="width:32px;vertical-align:top;padding-top:2px"><div style="width:28px;height:28px;border-radius:50%;background:#F0EEFF;text-align:center;line-height:28px;font-size:13px;font-weight:700;color:#6C63FF">1</div></td><td style="padding:0 0 16px 12px"><p style="font-size:14px;font-weight:600;color:#1A1A2E;margin:0 0 4px">Answer every call, 24/7</p><p style="font-size:13px;color:#6B7280;line-height:1.5;margin:0">An AI receptionist picks up instantly \u2014 nights, weekends, holidays.</p></td></tr></table>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:12px"><tr><td style="width:32px;vertical-align:top;padding-top:2px"><div style="width:28px;height:28px;border-radius:50%;background:#ECFDF5;text-align:center;line-height:28px;font-size:13px;font-weight:700;color:#10B981">2</div></td><td style="padding:0 0 16px 12px"><p style="font-size:14px;font-weight:600;color:#1A1A2E;margin:0 0 4px">Get instant lead alerts</p><p style="font-size:13px;color:#6B7280;line-height:1.5;margin:0">Every qualified lead scored and sent to you via SMS and email within seconds.</p></td></tr></table>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px"><tr><td style="width:32px;vertical-align:top;padding-top:2px"><div style="width:28px;height:28px;border-radius:50%;background:#FEF3C7;text-align:center;line-height:28px;font-size:13px;font-weight:700;color:#F59E0B">3</div></td><td style="padding:0 0 16px 12px"><p style="font-size:14px;font-weight:600;color:#1A1A2E;margin:0 0 4px">Track everything from one dashboard</p><p style="font-size:13px;color:#6B7280;line-height:1.5;margin:0">See every call, every lead, every trend. Weekly reports straight to your inbox.</p></td></tr></table>
<div style="text-align:center;margin:0 0 12px"><a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" style="display:inline-block;background:#6C63FF;color:#ffffff;padding:16px 44px;border-radius:10px;text-decoration:none;font-weight:700;font-size:16px;box-shadow:0 4px 14px rgba(108,99,255,0.35)">Book a Free Demo Call</a></div>
<p style="text-align:center;font-size:12px;color:#9CA3AF;margin:12px 0 0">15 minutes. No commitment. See it working live with your business name.</p>
</div></td></tr>
<tr><td style="padding:20px;text-align:center"><a href="https://syntharra-checkout-production.up.railway.app/" style="color:#6C63FF;font-size:13px;font-weight:600;text-decoration:none;margin:0 10px">View Pricing</a><span style="color:#D1D5DB">|</span><a href="https://www.syntharra.com/demo.html" style="color:#6C63FF;font-size:13px;font-weight:600;text-decoration:none;margin:0 10px">Try the AI Demo</a></td></tr>
<tr><td style="text-align:center"><p style="color:#9CA3AF;font-size:11px;margin:0;line-height:1.6">Syntharra AI Solutions<br><a href="https://www.syntharra.com" style="color:#6C63FF;text-decoration:none">syntharra.com</a> &middot; <a href="mailto:support@syntharra.com" style="color:#6C63FF;text-decoration:none">support@syntharra.com</a></p></td></tr>
</table></td></tr></table></body></html>`;

const SMTP2GO_KEY = 'api-0BE30DA64A074BC79F28BE6AEDC9DB9E';
try {
  await this.helpers.httpRequest({
    method: 'POST', url: 'https://api.smtp2go.com/v3/email/send',
    headers: { 'Content-Type': 'application/json' },
    body: { api_key: SMTP2GO_KEY, sender: 'Syntharra AI <noreply@syntharra.com>', to: [email],
      subject: `Your AI Readiness Score: ${score}/100 — ${scoreLabel}`, html_body: emailHtml },
    json: true
  });
  return { ...input, _email_sent: true };
} catch (e) { return { ...input, _email_sent: false, _error: e.message }; }
