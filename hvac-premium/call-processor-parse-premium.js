// ============================================================
// HVAC Premium — Parse Call Data node (v2)
// ============================================================
// Runs AFTER GPT: Analyze Transcript
// Extracts all booking + lead + notification data
// Builds notification HTML for each call type
// ============================================================

const gptResponse = $input.first().json;
const clientData = $('Parse Client Data').first().json;
const callAnalysis = $('Extract Call Data').first().json.call_analysis || {};

// ── Parse GPT response ──────────────────────────────────────
let callData = {};
try {
  const text = gptResponse.message?.content || gptResponse.text || JSON.stringify(gptResponse);
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  callData = jsonMatch ? JSON.parse(jsonMatch[0]) : {};
} catch (e) {
  callData = {
    lead_score: 0,
    summary: 'Failed to parse GPT response',
    is_hot_lead: false,
    booking_attempted: false,
    booking_success: false,
    call_type: 'unknown',
    urgency: 'low'
  };
}

// ── Merge Retell post-call analysis (higher priority than GPT) ──
const pca = callAnalysis;
const callerName = pca.caller_name || callData.caller_name || '';
const callerPhone = pca.caller_phone || callData.caller_phone || clientData.from_number || '';
const callerAddress = pca.caller_address || callData.caller_address || '';
const serviceRequested = pca.service_requested || callData.service_requested || '';
const bookingAttempted = pca.booking_attempted ?? callData.booking_attempted ?? false;
const bookingSuccess = pca.booking_success ?? callData.booking_success ?? false;
const appointmentDate = pca.appointment_date || callData.appointment_date || '';
const appointmentTimeWindow = pca.appointment_time_window || callData.appointment_time_window || '';
const jobTypeBooked = pca.job_type_booked || callData.job_type_booked || '';
const rescheduleOrCancel = pca.reschedule_or_cancel || callData.reschedule_or_cancel || 'neither';
const callType = pca.call_type || callData.call_type || 'unknown';
const urgency = pca.urgency || callData.urgency || 'low';
const isHotLead = pca.is_hot_lead ?? callData.is_hot_lead ?? false;
const leadScore = pca.lead_score ?? callData.lead_score ?? 0;
const summary = pca.call_summary || callData.summary || '';
const callerSentiment = pca.user_sentiment || callData.caller_sentiment || '';

// ── Determine notification type ─────────────────────────────
// Priority: booking_confirmed > reschedule > cancellation > emergency > hot_lead > general_lead > info_only
let notificationType = 'info_only';
let notifyClient = false;

if (bookingSuccess) {
  notificationType = 'booking_confirmed';
  notifyClient = true;
} else if (rescheduleOrCancel === 'reschedule') {
  notificationType = 'reschedule';
  notifyClient = true;
} else if (rescheduleOrCancel === 'cancel') {
  notificationType = 'cancellation';
  notifyClient = true;
} else if (callType === 'emergency' || urgency === 'emergency') {
  notificationType = 'emergency';
  notifyClient = true;
} else if (bookingAttempted && !bookingSuccess) {
  // Booking was attempted but failed (calendar unavailable, caller declined, etc.)
  // This is a hot lead that needs follow-up
  notificationType = 'booking_failed_lead';
  notifyClient = true;
} else if (isHotLead || leadScore >= 7) {
  notificationType = 'hot_lead';
  notifyClient = true;
} else if (leadScore >= 4) {
  notificationType = 'general_lead';
  notifyClient = true;
} else if (callType === 'existing_customer' || callType === 'callback') {
  notificationType = 'follow_up_required';
  notifyClient = true;
} else if (callType === 'general_question') {
  notificationType = 'info_only';
  notifyClient = false; // Only log, don't notify for simple FAQ
} else if (callType === 'spam') {
  notificationType = 'spam';
  notifyClient = false;
}

// ── Build email HTML ────────────────────────────────────────
const companyName = clientData.company_name || 'Your Company';
const timestamp = new Date().toLocaleString('en-US', { timeZone: clientData.timezone || 'America/Chicago' });
const duration = clientData.duration_seconds || 0;

// Color theming per notification type
const typeColors = {
  booking_confirmed: { accent: '#10B981', emoji: '📅', label: 'Booking Confirmed' },
  reschedule: { accent: '#F59E0B', emoji: '🔄', label: 'Appointment Rescheduled' },
  cancellation: { accent: '#EF4444', emoji: '❌', label: 'Appointment Cancelled' },
  emergency: { accent: '#DC2626', emoji: '🚨', label: 'EMERGENCY CALL' },
  booking_failed_lead: { accent: '#F97316', emoji: '📋', label: 'Booking Failed — Follow Up Required' },
  hot_lead: { accent: '#EF4444', emoji: '🔥', label: 'Hot Lead Alert' },
  general_lead: { accent: '#6C63FF', emoji: '📞', label: 'New Lead' },
  follow_up_required: { accent: '#8B5CF6', emoji: '↩️', label: 'Follow-Up Required' },
  info_only: { accent: '#9CA3AF', emoji: 'ℹ️', label: 'Info Call Logged' },
  spam: { accent: '#6B7280', emoji: '🤖', label: 'Spam / Robocall' }
};

const tc = typeColors[notificationType] || typeColors.info_only;

// Build rows dynamically based on what data exists
let rows = '';

const addRow = (label, value) => {
  if (value && value.trim && value.trim() !== '' && value !== 'null' && value !== 'undefined') {
    rows += `<tr><td style="padding:8px 12px;border:1px solid #e2e8f0;font-weight:600;width:160px;background:#f8fafc">${label}</td><td style="padding:8px 12px;border:1px solid #e2e8f0">${value}</td></tr>`;
  }
};

addRow('Caller', callerName || 'Unknown');
addRow('Phone', callerPhone);
addRow('Address', callerAddress);
addRow('Service', serviceRequested || jobTypeBooked);

if (bookingSuccess || bookingAttempted) {
  addRow('Booking Status', bookingSuccess ? '✅ Confirmed' : '⚠️ Attempted but not completed');
  addRow('Appointment', appointmentDate ? `${appointmentDate} — ${appointmentTimeWindow || 'TBD'}` : 'Pending');
  addRow('Job Type', jobTypeBooked);
}

if (rescheduleOrCancel !== 'neither') {
  addRow('Action', rescheduleOrCancel === 'reschedule' ? '🔄 Rescheduled' : '❌ Cancelled');
  if (appointmentDate) addRow('New Date', `${appointmentDate} — ${appointmentTimeWindow || 'TBD'}`);
}

addRow('Urgency', urgency.charAt(0).toUpperCase() + urgency.slice(1));
addRow('Lead Score', `${leadScore}/10`);
addRow('Sentiment', callerSentiment);

const emailHtml = `
<div style="font-family:Arial,Helvetica,sans-serif;max-width:640px;margin:0 auto">
  <div style="background:${tc.accent};padding:16px 20px;border-radius:8px 8px 0 0">
    <h2 style="color:#fff;margin:0;font-size:18px">${tc.emoji} ${tc.label} — ${companyName}</h2>
  </div>
  <div style="border:1px solid #e2e8f0;border-top:0;padding:20px;border-radius:0 0 8px 8px">
    <table style="border-collapse:collapse;width:100%">
      ${rows}
    </table>
    <div style="margin-top:16px;padding:12px;background:#f8fafc;border-radius:6px;border-left:4px solid ${tc.accent}">
      <strong>Summary:</strong> ${summary || 'No summary available.'}
    </div>
    ${callData.follow_up_notes ? `<div style="margin-top:12px;padding:12px;background:#FFFBEB;border-radius:6px;border-left:4px solid #F59E0B"><strong>Follow-up Notes:</strong> ${callData.follow_up_notes}</div>` : ''}
    <p style="color:#9CA3AF;font-size:11px;margin-top:16px">${timestamp} | Duration: ${duration}s | Call ID: ${clientData.call_id || ''}</p>
  </div>
</div>`;

// ── Build SMS text ──────────────────────────────────────────
let smsText = '';
if (notificationType === 'booking_confirmed') {
  smsText = `📅 Booking Confirmed — ${callerName || 'Caller'} booked for ${jobTypeBooked || serviceRequested || 'service'} on ${appointmentDate || 'TBD'} (${appointmentTimeWindow || 'TBD'}). Phone: ${callerPhone}`;
} else if (notificationType === 'emergency') {
  smsText = `🚨 EMERGENCY — ${callerName || 'Caller'} at ${callerAddress || 'address not given'}. ${serviceRequested || summary}. Call: ${callerPhone}`;
} else if (notificationType === 'reschedule') {
  smsText = `🔄 Rescheduled — ${callerName || 'Caller'} moved to ${appointmentDate || 'TBD'} (${appointmentTimeWindow || 'TBD'}). Phone: ${callerPhone}`;
} else if (notificationType === 'cancellation') {
  smsText = `❌ Cancelled — ${callerName || 'Caller'} cancelled their appointment. Phone: ${callerPhone}. ${summary}`;
} else if (notificationType === 'booking_failed_lead') {
  smsText = `📋 Follow Up — ${callerName || 'Caller'} wanted to book ${serviceRequested || 'service'} but booking wasn't completed. Call them: ${callerPhone}`;
} else if (notificationType === 'hot_lead') {
  smsText = `🔥 Hot Lead — ${callerName || 'Caller'} needs ${serviceRequested || 'service'}. Score: ${leadScore}/10. Call: ${callerPhone}`;
} else if (notificationType === 'general_lead') {
  smsText = `📞 New Lead — ${callerName || 'Caller'} called about ${serviceRequested || 'service'}. Score: ${leadScore}/10. Phone: ${callerPhone}`;
} else if (notificationType === 'follow_up_required') {
  smsText = `↩️ Follow Up — ${callerName || 'Caller'} (${callType === 'callback' ? 'returning call' : 'existing customer'}). Phone: ${callerPhone}. ${summary}`;
}

// ── Build email subject line ────────────────────────────────
const subjectMap = {
  booking_confirmed: `📅 Booking Confirmed — ${callerName || 'New Customer'} | ${companyName}`,
  reschedule: `🔄 Appointment Rescheduled — ${callerName || 'Customer'} | ${companyName}`,
  cancellation: `❌ Appointment Cancelled — ${callerName || 'Customer'} | ${companyName}`,
  emergency: `🚨 EMERGENCY — ${callerName || 'Caller'} | ${companyName}`,
  booking_failed_lead: `📋 Booking Failed — Follow Up ${callerName || 'Caller'} | ${companyName}`,
  hot_lead: `🔥 Hot Lead — ${callerName || 'Unknown'} — ${serviceRequested || 'Service'} | ${companyName}`,
  general_lead: `📞 New Lead — ${callerName || 'Unknown'} — ${serviceRequested || 'Service'} | ${companyName}`,
  follow_up_required: `↩️ Follow Up Required — ${callerName || 'Caller'} | ${companyName}`,
  info_only: `ℹ️ Call Logged — ${companyName}`,
  spam: `🤖 Spam Call — ${companyName}`
};
const emailSubject = subjectMap[notificationType] || `Call Alert — ${companyName}`;

// ── Return everything ───────────────────────────────────────
return {
  // Identifiers
  call_id: clientData.call_id || '',
  agent_id: clientData.agent_id || '',
  company_name: companyName,
  call_tier: 'premium',
  
  // Caller info
  caller_name: callerName,
  caller_phone: callerPhone,
  caller_address: callerAddress,
  caller_sentiment: callerSentiment,
  
  // Call classification
  call_type: callType,
  urgency: urgency,
  service_requested: serviceRequested,
  summary: summary,
  follow_up_notes: callData.follow_up_notes || '',
  
  // Booking fields
  booking_attempted: bookingAttempted,
  booking_success: bookingSuccess,
  appointment_date: appointmentDate || null,
  appointment_time_window: appointmentTimeWindow || null,
  job_type_booked: jobTypeBooked || null,
  reschedule_or_cancel: rescheduleOrCancel,
  
  // Lead fields
  lead_score: leadScore,
  is_lead: !bookingSuccess && leadScore >= 4,
  is_hot_lead: isHotLead,
  
  // Notification
  notification_type: notificationType,
  notify_client: notifyClient,
  email_html: emailHtml,
  email_subject: emailSubject,
  sms_text: smsText,
  
  // Carry forward from client data
  lead_email: clientData.lead_email || '',
  lead_phone: clientData.lead_phone || '',
  notification_email_2: clientData.notification_email_2 || '',
  notification_email_3: clientData.notification_email_3 || '',
  notification_sms_2: clientData.notification_sms_2 || '',
  notification_sms_3: clientData.notification_sms_3 || '',
  lead_contact_method: clientData.lead_contact_method || 'Both',
  twilio_from: clientData.twilio_from || '',
  from_number: clientData.from_number || '',
  duration_seconds: clientData.duration_seconds || 0,
  call_timestamp: clientData.call_timestamp || new Date().toISOString(),
  timezone: clientData.timezone || 'America/Chicago'
};
