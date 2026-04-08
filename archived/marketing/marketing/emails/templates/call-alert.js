// ── Call Alert Email — Standard + Premium ──
// Input: processed call data from GPT analysis
const d = $input.first().json;
const companyName = d.company_name || 'your company';
const callerName = d.caller_name || 'Unknown Caller';
const callerPhone = d.caller_phone || 'Not provided';
const serviceType = d.service_type || d.job_type || 'General Enquiry';
const urgency = d.urgency || 'Normal';
const address = d.caller_address || d.address || 'Not provided';
const summary = d.call_summary || d.ai_summary || '';
const callDuration = d.call_duration || '';
const callTime = d.call_time || new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
const isLead = d.is_lead !== false;

// Premium-only fields
const appointmentBooked = d.appointment_booked || false;
const appointmentTime = d.appointment_time || '';
const assignedTech = d.assigned_technician || '';

const urgencyColor = urgency.toLowerCase().includes('high') || urgency.toLowerCase().includes('emergency') ? '#EF4444' : urgency.toLowerCase().includes('medium') ? '#F59E0B' : '#10B981';
const badge = isLead ? 'New Lead' : 'Call Handled';

const ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png';
const LOGO = `<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td style="vertical-align:middle;padding-right:10px"><img src="${ICON_URL}" alt="" width="36" height="36" style="display:block;border:0"></td><td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="text-align:left;padding:0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:16px;font-weight:700;letter-spacing:-0.3px;color:#0f0f1a;line-height:1;text-align:left">Syntharra</div></td></tr><tr><td style="text-align:left;padding:3px 0 0 0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:7.5px;font-weight:600;letter-spacing:1.2px;color:#6C63FF;text-transform:uppercase;line-height:1;text-align:left">Global AI Solutions</div></td></tr></table></td></tr></table>`;
const FOOTER = `<tr><td style="padding:20px;text-align:center"><a href="https://www.syntharra.com" style="color:#6C63FF;font-size:13px;font-weight:600;text-decoration:none">syntharra.com</a></td></tr><tr><td style="text-align:center;padding:0 0 16px"><p style="color:#9CA3AF;font-size:11px;margin:0">Syntharra AI Solutions</p></td></tr>`;

const appointmentBlock = appointmentBooked ? `
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;background-color:#ECFDF5;border-radius:10px;overflow:hidden"><tr><td style="padding:18px 22px">
  <p style="font-size:12px;font-weight:700;color:#065F46;letter-spacing:0.05em;text-transform:uppercase;margin:0 0 8px">\ud83d\udcc5 Appointment Booked</p>
  <p style="font-size:16px;font-weight:700;color:#065F46;margin:0">${appointmentTime}</p>
  ${assignedTech ? `<p style="font-size:13px;color:#047857;margin:4px 0 0">Assigned to: ${assignedTech}</p>` : ''}
</td></tr></table>` : '';

const emailHtml = `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700&display=swap" rel="stylesheet"></head>
<body style="margin:0;padding:0;background-color:#F7F7FB;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F7F7FB;padding:40px 16px"><tr><td align="center">
<table width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%">
<tr><td style="padding:0 0 24px;text-align:center">${LOGO}</td></tr>
<tr><td style="background-color:#ffffff;border-radius:12px;border:1px solid #E5E7EB;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
<div style="height:3px;background:linear-gradient(90deg,#6C63FF,#8B7FFF)"></div>
<div style="padding:32px 36px">
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:16px"><tr><td><span style="display:inline-block;font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#6C63FF;background-color:#F0EEFF;padding:4px 12px;border-radius:20px">${badge}</span></td></tr></table>
<h1 style="color:#1A1A2E;font-size:24px;font-weight:700;margin:0 0 6px;line-height:1.3">${isLead ? 'New Lead Captured' : 'Call Handled'}${appointmentBooked ? ' & Booked' : ''}</h1>
<p style="color:#6B7280;font-size:14px;line-height:1.6;margin:0 0 24px">Your AI Receptionist just handled a call for ${companyName}.</p>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;border:1px solid #E5E7EB;border-radius:10px;overflow:hidden">
<tr><td style="padding:14px 20px;border-bottom:1px solid #E5E7EB;background-color:#FAFAFA;font-size:12px;font-weight:700;color:#6B7280;letter-spacing:0.05em;text-transform:uppercase" colspan="2">Call Details</td></tr>
<tr><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;color:#1A1A2E;font-size:14px">Caller</td><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;text-align:right;font-weight:600;color:#1A1A2E;font-size:14px">${callerName}</td></tr>
<tr><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;color:#1A1A2E;font-size:14px">Phone</td><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;text-align:right;font-weight:600;color:#1A1A2E;font-size:14px">${callerPhone}</td></tr>
<tr><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;color:#1A1A2E;font-size:14px">Service</td><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;text-align:right;font-weight:600;color:#1A1A2E;font-size:14px">${serviceType}</td></tr>
<tr><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;color:#1A1A2E;font-size:14px">Urgency</td><td style="padding:12px 20px;border-bottom:1px solid #E5E7EB;background-color:#ffffff;text-align:right;font-weight:600;color:${urgencyColor};font-size:14px">${urgency}</td></tr>
<tr><td style="padding:12px 20px;background-color:#ffffff;color:#1A1A2E;font-size:14px">Address</td><td style="padding:12px 20px;background-color:#ffffff;text-align:right;font-weight:600;color:#1A1A2E;font-size:14px">${address}</td></tr>
</table>
${appointmentBlock}
${summary ? `<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;background-color:#F9F9FC;border-radius:10px"><tr><td style="padding:16px 20px">
  <p style="font-size:12px;font-weight:700;color:#6B7280;letter-spacing:0.05em;text-transform:uppercase;margin:0 0 8px">AI Summary</p>
  <p style="font-size:14px;color:#1A1A2E;line-height:1.6;margin:0">${summary}</p>
</td></tr></table>` : ''}
<p style="text-align:center;font-size:13px;color:#9CA3AF;margin:0">Call handled at ${callTime}${callDuration ? ` \u2014 Duration: ${callDuration}` : ''}</p>
</div></td></tr>
${FOOTER}
</table></td></tr></table></body></html>`;

const emailSubject = `\ud83d\udcde ${isLead ? 'New Lead' : 'Call'}: ${callerName} \u2014 ${serviceType} | ${companyName}`;

return [{ json: { ...d, emailHtml, email_subject: emailSubject } }];
