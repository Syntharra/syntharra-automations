// ============================================================
// HVAC Premium — Parse Call Data node
// ============================================================
// Extracts booking data OR lead data from post-call analysis.
// Differs from standard: booking fields are primary, lead fields secondary.
// ============================================================

const gptResponse = $input.first().json;
const clientData = $('Parse Client Data').first().json;

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
    booking_success: false
  };
}

// Determine call tier — premium always
const callTier = 'premium';

// Booking outcome
const bookingAttempted = callData.booking_attempted || false;
const bookingSuccess = callData.booking_success || false;
const appointmentDate = callData.appointment_date || null;
const appointmentTimeWindow = callData.appointment_time_window || null;
const jobTypeBooked = callData.job_type_booked || null;
const rescheduleOrCancel = callData.reschedule_or_cancel || 'neither';

// Lead fields (used when booking was not made)
const leadScore = callData.lead_score || 0;
const isLead = bookingSuccess ? false : (leadScore >= 6); // if booking succeeded, not a pending lead

return {
  ...clientData,
  ...callData,
  call_tier: callTier,
  lead_score: leadScore,
  is_lead: isLead,
  booking_attempted: bookingAttempted,
  booking_success: bookingSuccess,
  appointment_date: appointmentDate,
  appointment_time_window: appointmentTimeWindow,
  job_type_booked: jobTypeBooked,
  reschedule_or_cancel: rescheduleOrCancel,
  // Standard fields carried forward from clientData via spread above
  // notification_email_2, notification_email_3, notification_sms_2, notification_sms_3
};
