// Merge conversation flow + agent responses with extracted data
const agentResponse = $input.first().json;
const convFlowResponse = $('Create Retell LLM').item.json;
const buildData = $('Build Retell Prompt').item.json;
const ed = buildData.extractedData || {};

return {
  // System fields
  timestamp: new Date().toISOString(),
  conversation_flow_id: convFlowResponse.conversation_flow_id,
  agent_id: agentResponse.agent_id,
  voice_id: buildData.voiceId,
  agent_language: 'en-US',

  // Company basics
  company_name: buildData.companyName || ed.company_name,
  owner_name: ed.owner_name || '',
  company_phone: ed.company_phone || ed.main_phone || '',
  website: ed.website || '',
  years_in_business: ed.years_in_business || '',
  agent_name: buildData.agentName || ed.agent_name,
  timezone: ed.timezone || 'America/Chicago',
  client_email: ed.client_email || '',
  industry_type: ed.industry_type || 'HVAC',

  // AI Agent Setup
  voice_gender: ed.voice_gender || 'female',
  custom_greeting: ed.custom_greeting || `${buildData.companyName || ed.company_name}, this is ${buildData.agentName || ed.agent_name} speaking, how may I assist you?`,
  company_tagline: ed.company_tagline || '',

  // Services & Coverage
  services_offered: ed.services_offered || '',
  brands_serviced: ed.brands_serviced || '',
  service_area: ed.service_area || '',
  service_area_radius: ed.service_area_radius || '',
  certifications: ed.certifications || '',
  licensed_insured: ed.licensed_insured || 'Yes',

  // Hours & Availability
  business_hours: ed.business_hours || '',
  response_time: ed.response_time || '',
  emergency_service: ed.emergency_service || 'No',
  emergency_phone: ed.emergency_phone || '',
  after_hours_behavior: ed.after_hours_behavior || '',

  // Pricing & Policies
  pricing_policy: ed.pricing_policy || 'We provide free quotes on-site',
  diagnostic_fee: ed.diagnostic_fee || '',
  standard_fees: ed.standard_fees || '',
  free_estimates: ed.free_estimates || 'Yes - always free',
  financing_available: ed.financing_available || 'No',
  financing_details: ed.financing_details || '',
  warranty: ed.warranty || 'Yes',
  warranty_details: ed.warranty_details || '',
  payment_methods: ed.payment_methods || '',
  maintenance_plans: ed.maintenance_plans || 'No',
  membership_program: ed.membership_program || '',

  // Lead Handling
  lead_contact_method: ed.lead_contact_method || 'Both',
  lead_phone: ed.lead_phone || '',
  lead_email: ed.lead_email || '',
  booking_system: ed.booking_system || '',

  // Additional Notification Contacts
  notification_email_2: ed.notification_email_2 || null,
  notification_email_3: ed.notification_email_3 || null,
  notification_sms_2:   ed.notification_sms_2   || null,
  notification_sms_3:   ed.notification_sms_3   || null,

  // Escalation & Transfer
  transfer_phone: ed.transfer_phone || '',
  transfer_triggers: ed.transfer_triggers || '',
  transfer_behavior: ed.transfer_behavior || 'Try once - take message if no answer',

  // Promotions & Extras
  unique_selling_points: ed.unique_selling_points || '',
  current_promotion: ed.current_promotion || '',
  seasonal_services: ed.seasonal_services || '',
  google_review_rating: ed.google_review_rating || '',
  google_review_count: ed.google_review_count || '',
  do_not_service: ed.do_not_service || '',
  additional_info: ed.additional_info || '',
  stripe_customer_id: ed.stripe_customer_id || null,
  // Idempotency — carry submission_id through to Supabase
  // Reach back to idempotency node -- submission_id is lost at IF branch
  submission_id: (() => { try { return $('Check Idempotency & Insert (STANDARD)').first().json.submission_id || null; } catch(e) { return null; } })(),

  plan_type: 'standard'
};