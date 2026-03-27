// ============================================================
// HVAC Premium — Parse Call Data + Build Notifications
// ============================================================
// This runs AFTER the GPT analysis node.
// It parses the GPT response, determines the notification type,
// builds the appropriate email HTML, and outputs everything
// for the downstream notification nodes.
//
// NOTIFICATION TYPES:
//   1. booking_confirmed  — appointment booked successfully
//   2. booking_failed     — booking attempted but failed (calendar error, no slots)
//   3. reschedule         — appointment rescheduled
//   4. cancellation       — appointment cancelled
//   5. hot_lead           — no booking made but high-value lead (score >= 7)
//   6. warm_lead          — no booking made, moderate lead (score 4-6)
//   7. emergency          — emergency call, transferred or details taken
//   8. existing_customer  — existing customer enquiry
//   9. general_info       — general question answered, no lead
//  10. spam               — spam/robocall, no notification needed
// ============================================================

const gptResponse = $input.first().json;
const clientData = $('Parse Client Data').first().json;
const callData_raw = $('Extract Call Data').first().json;

// ── Parse GPT Response ────────────────────────────────────────
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

// ── Also pull from post_call_analysis if available ────────────
const pca = callData_raw.call_analysis || {};

// ── Extract Fields (GPT first, then post_call_analysis fallback) ──
const callerName = callData.caller_name || pca.caller_name || '';
const callerPhone = callData.caller_phone || pca.caller_phone || callData_raw.from_number || '';
const callerAddress = callData.caller_address || pca.caller_address || '';
const serviceRequested = callData.service_requested || pca.service_requested || '';
const summary = callData.summary || pca.call_summary || '';
const urgency = callData.urgency || pca.urgency || 'low';
const notes = callData.notes || '';
const leadScore = parseInt(callData.lead_score || pca.lead_score || 0);
const isHotLead = callData.is_hot_lead || pca.is_hot_lead || leadScore >= 7;
const callType = callData.call_type || pca.call_type || 'unknown';

// Booking fields
const bookingAttempted = callData.booking_attempted || pca.booking_attempted || false;
const bookingSuccess = callData.booking_success || pca.booking_success || false;
const appointmentDate = callData.appointment_date || pca.appointment_date || '';
const appointmentTimeWindow = callData.appointment_time_window || pca.appointment_time_window || '';
const jobTypeBooked = callData.job_type_booked || pca.job_type_booked || '';
const rescheduleOrCancel = callData.reschedule_or_cancel || pca.reschedule_or_cancel || 'neither';

// Additional fields
const jobType = callData.job_type || serviceRequested || '';
const vulnerableOccupant = callData.vulnerable_occupant || false;
const callerSentiment = callData.caller_sentiment || pca.user_sentiment || '';
const transferAttempted = callData.transfer_attempted || false;
const transferSuccess = callData.transfer_success || null;

// Client config
const companyName = clientData.company_name || '';
const leadEmail = clientData.lead_email || '';
const leadPhone_client = clientData.lead_phone || '';
const notificationEmail2 = clientData.notification_email_2 || '';
const notificationEmail3 = clientData.notification_email_3 || '';
const notificationSms2 = clientData.notification_sms_2 || '';
const notificationSms3 = clientData.notification_sms_3 || '';

// ── Determine Notification Type ───────────────────────────────
let notificationType = 'general_info';
let shouldNotify = true;
let notificationPriority = 'normal'; // normal, high, urgent

if (callType === 'spam' || leadScore === 0) {
  notificationType = 'spam';
  shouldNotify = false;
} else if (callType === 'emergency' || urgency === 'emergency') {
  notificationType = 'emergency';
  notificationPriority = 'urgent';
} else if (bookingSuccess && rescheduleOrCancel === 'reschedule') {
  notificationType = 'reschedule';
  notificationPriority = 'high';
} else if (rescheduleOrCancel === 'cancel') {
  notificationType = 'cancellation';
  notificationPriority = 'high';
} else if (bookingSuccess) {
  notificationType = 'booking_confirmed';
  notificationPriority = 'normal';
} else if (bookingAttempted && !bookingSuccess) {
  notificationType = 'booking_failed';
  notificationPriority = 'high';
} else if (callType === 'existing_customer') {
  notificationType = 'existing_customer';
  notificationPriority = 'normal';
} else if (isHotLead || leadScore >= 7) {
  notificationType = 'hot_lead';
  notificationPriority = 'high';
} else if (leadScore >= 4) {
  notificationType = 'warm_lead';
  notificationPriority = 'normal';
} else if (callType === 'general_question') {
  notificationType = 'general_info';
  shouldNotify = leadScore >= 3;
}

// ── Build Email Subject ───────────────────────────────────────
const subjectMap = {
  booking_confirmed: `✅ New Booking — ${callerName || 'Customer'} — ${jobTypeBooked || serviceRequested} | ${companyName}`,
  booking_failed: `⚠️ Booking Failed — ${callerName || 'Customer'} Needs Callback | ${companyName}`,
  reschedule: `🔄 Appointment Rescheduled — ${callerName || 'Customer'} | ${companyName}`,
  cancellation: `❌ Appointment Cancelled — ${callerName || 'Customer'} | ${companyName}`,
  hot_lead: `🔥 Hot Lead — ${callerName || 'Unknown'} — ${serviceRequested || 'Service'} | ${companyName}`,
  warm_lead: `📋 New Lead — ${callerName || 'Unknown'} — ${serviceRequested || 'Service'} | ${companyName}`,
  emergency: `🚨 EMERGENCY — ${callerName || 'Unknown'} | ${companyName}`,
  existing_customer: `📞 Existing Customer — ${callerName || 'Customer'} | ${companyName}`,
  general_info: `ℹ️ Call Summary — ${callerName || 'Caller'} | ${companyName}`
};
const emailSubject = subjectMap[notificationType] || `📞 Call Summary | ${companyName}`;

// ── Build Email HTML ──────────────────────────────────────────
const brandColor = '#6C63FF';

function urgencyColor(urg) {
  const map = { emergency: '#e53e3e', high: '#dd6b20', medium: '#d69e2e', low: '#38a169' };
  return map[urg] || '#718096';
}

function leadScoreColor(score) {
  if (score >= 8) return '#e53e3e';
  if (score >= 6) return '#dd6b20';
  if (score >= 4) return '#d69e2e';
  return '#718096';
}

function headerIcon(type) {
  const map = {
    booking_confirmed: '✅', booking_failed: '⚠️', reschedule: '🔄',
    cancellation: '❌', hot_lead: '🔥', warm_lead: '📋',
    emergency: '🚨', existing_customer: '📞', general_info: 'ℹ️'
  };
  return map[type] || '📞';
}

function headerTitle(type) {
  const map = {
    booking_confirmed: 'New Booking Confirmed',
    booking_failed: 'Booking Failed — Callback Required',
    reschedule: 'Appointment Rescheduled',
    cancellation: 'Appointment Cancelled',
    hot_lead: 'Hot Lead Alert',
    warm_lead: 'New Lead',
    emergency: 'EMERGENCY CALL',
    existing_customer: 'Existing Customer Enquiry',
    general_info: 'Call Summary'
  };
  return map[type] || 'Call Summary';
}

// Common table row builder
function row(label, value, highlight) {
  if (!value) return '';
  const style = highlight
    ? `padding:8px;border:1px solid #ddd;font-weight:bold;color:${highlight}`
    : 'padding:8px;border:1px solid #ddd';
  return `<tr><td style='padding:8px;border:1px solid #ddd;font-weight:bold'>${label}</td><td style='${style}'>${value}</td></tr>`;
}

// Build the table rows based on notification type
let tableRows = '';

// Always include caller info
tableRows += row('Company', companyName);
tableRows += row('Caller', callerName || 'Unknown');
tableRows += row('Phone', callerPhone || 'Not provided');
tableRows += row('Address', callerAddress || 'Not provided');

// Booking-specific rows
if (['booking_confirmed', 'reschedule'].includes(notificationType)) {
  tableRows += row('Service', jobTypeBooked || serviceRequested || 'Not specified');
  tableRows += row('Date', appointmentDate || 'Not confirmed');
  tableRows += row('Time Window', appointmentTimeWindow ? (appointmentTimeWindow.charAt(0).toUpperCase() + appointmentTimeWindow.slice(1)) : 'Not specified');
}

if (notificationType === 'cancellation') {
  tableRows += row('Cancelled Service', jobTypeBooked || serviceRequested || 'Not specified');
  tableRows += row('Original Date', appointmentDate || 'Unknown');
}

if (notificationType === 'booking_failed') {
  tableRows += row('Service Requested', serviceRequested || 'Not specified');
  tableRows += row('Preferred Date', appointmentDate || 'Not specified');
  tableRows += row('Preferred Time', appointmentTimeWindow || 'Not specified');
  tableRows += row('Reason', 'Calendar unavailable or no suitable slot found');
}

// Lead-specific rows
if (['hot_lead', 'warm_lead'].includes(notificationType)) {
  tableRows += row('Service', serviceRequested || 'General');
  tableRows += row('Lead Score', `${leadScore}/10`, leadScoreColor(leadScore));
  tableRows += row('Urgency', urgency.charAt(0).toUpperCase() + urgency.slice(1), urgencyColor(urgency));
  if (bookingAttempted) {
    tableRows += row('Booking Attempted', 'Yes — but not completed');
  }
}

// Emergency rows
if (notificationType === 'emergency') {
  tableRows += row('Issue', serviceRequested || 'Emergency');
  tableRows += row('Urgency', 'EMERGENCY', '#e53e3e');
  tableRows += row('Transfer Attempted', transferAttempted ? 'Yes' : 'No');
  if (transferAttempted) {
    tableRows += row('Transfer Connected', transferSuccess === true ? 'Yes' : transferSuccess === false ? 'No — details taken' : 'Unknown');
  }
}

// Existing customer rows
if (notificationType === 'existing_customer') {
  tableRows += row('Enquiry', serviceRequested || notes || 'Not specified');
  tableRows += row('Action Needed', transferAttempted ? (transferSuccess ? 'Transferred successfully' : 'Transfer failed — callback required') : 'Callback requested');
}

// General info
if (notificationType === 'general_info') {
  tableRows += row('Topic', serviceRequested || 'General question');
  if (leadScore >= 3) tableRows += row('Lead Score', `${leadScore}/10`, leadScoreColor(leadScore));
}

// Vulnerable occupant flag
if (vulnerableOccupant) {
  tableRows += row('⚠️ Vulnerable Occupant', 'Yes — elderly, disabled, or young children present', '#e53e3e');
}

const emailHtml = `<div style='font-family:Arial,sans-serif;max-width:600px'>
<h2 style='color:${notificationType === 'emergency' ? '#e53e3e' : brandColor}'>${headerIcon(notificationType)} ${headerTitle(notificationType)}</h2>
<table style='border-collapse:collapse;width:100%'>
${tableRows}
</table>
<h3>Call Summary</h3>
<p>${summary || 'No summary available.'}</p>
${notes ? `<h3>Notes</h3><p>${notes}</p>` : ''}
<p style='color:#718096;font-size:12px'>${callData_raw.call_timestamp || new Date().toISOString()} | Duration: ${callData_raw.duration_seconds || 0}s | Call ID: ${callData_raw.call_id || 'N/A'}</p>
</div>`;

// ── Build SMS Message ─────────────────────────────────────────
const smsMap = {
  booking_confirmed: `✅ NEW BOOKING: ${callerName || 'Customer'} booked ${jobTypeBooked || serviceRequested || 'service'} for ${appointmentDate || 'TBC'} ${appointmentTimeWindow || ''}. Ph: ${callerPhone || 'N/A'}`,
  booking_failed: `⚠️ BOOKING FAILED: ${callerName || 'Customer'} tried to book ${serviceRequested || 'service'} but could not complete. CALLBACK NEEDED. Ph: ${callerPhone || 'N/A'}`,
  reschedule: `🔄 RESCHEDULED: ${callerName || 'Customer'} moved to ${appointmentDate || 'TBC'} ${appointmentTimeWindow || ''}. Ph: ${callerPhone || 'N/A'}`,
  cancellation: `❌ CANCELLED: ${callerName || 'Customer'} cancelled ${appointmentDate || ''} appointment. Ph: ${callerPhone || 'N/A'}`,
  hot_lead: `🔥 HOT LEAD (${leadScore}/10): ${callerName || 'Unknown'} needs ${serviceRequested || 'service'}. Ph: ${callerPhone || 'N/A'}. ${urgency === 'high' ? 'URGENT.' : ''}`,
  warm_lead: `📋 NEW LEAD (${leadScore}/10): ${callerName || 'Unknown'} — ${serviceRequested || 'service'}. Ph: ${callerPhone || 'N/A'}`,
  emergency: `🚨 EMERGENCY: ${callerName || 'Unknown'} — ${serviceRequested || 'emergency issue'}. Ph: ${callerPhone || 'N/A'}. ${transferSuccess ? 'Transferred.' : 'CALLBACK NEEDED.'}`,
  existing_customer: `📞 EXISTING CUSTOMER: ${callerName || 'Customer'} re: ${serviceRequested || notes || 'enquiry'}. Ph: ${callerPhone || 'N/A'}`,
  general_info: `ℹ️ CALL: ${callerName || 'Caller'} asked about ${serviceRequested || 'general info'}. Ph: ${callerPhone || 'N/A'}`
};
const smsMessage = smsMap[notificationType] || `📞 Call from ${callerName || 'Unknown'}: ${summary || 'No details'}. Ph: ${callerPhone || 'N/A'}`;

// ── Output ────────────────────────────────────────────────────
return {
  // Caller data
  caller_name: callerName,
  caller_phone: callerPhone,
  caller_address: callerAddress,
  service_requested: serviceRequested,
  summary: summary,
  notes: notes,
  urgency: urgency,
  caller_sentiment: callerSentiment,
  vulnerable_occupant: vulnerableOccupant,

  // Lead data
  lead_score: leadScore,
  is_lead: leadScore >= 4,
  is_hot_lead: isHotLead,

  // Booking data
  booking_attempted: bookingAttempted,
  booking_success: bookingSuccess,
  appointment_date: appointmentDate,
  appointment_time_window: appointmentTimeWindow,
  job_type_booked: jobTypeBooked,
  reschedule_or_cancel: rescheduleOrCancel,

  // Call metadata
  call_type: callType,
  call_tier: 'premium',
  job_type: jobType,
  transfer_attempted: transferAttempted,
  transfer_success: transferSuccess,

  // Notification config
  notification_type: notificationType,
  notification_priority: notificationPriority,
  should_notify: shouldNotify,
  email_subject: emailSubject,
  email_html: emailHtml,
  sms_message: smsMessage,

  // Client notification recipients
  lead_email: leadEmail,
  lead_phone: leadPhone_client,
  notification_email_2: notificationEmail2,
  notification_email_3: notificationEmail3,
  notification_sms_2: notificationSms2,
  notification_sms_3: notificationSms3,
  company_name: companyName,

  // Raw data passthrough
  call_id: callData_raw.call_id,
  agent_id: callData_raw.agent_id,
  from_number: callData_raw.from_number,
  duration_seconds: callData_raw.duration_seconds,
  call_timestamp: callData_raw.call_timestamp,
  disconnection_reason: callData_raw.disconnection_reason
};
