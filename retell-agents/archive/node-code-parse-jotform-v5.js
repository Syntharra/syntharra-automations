// ============================================================
// Parse JotForm Data v5 — Supabase Edition
// ============================================================

const formData = $input.first().json.body;

function normalizeList(val) {
  if (!val) return '';
  if (Array.isArray(val)) return val.filter(Boolean).join(', ');
  return String(val).trim();
}

function clean(val, fallback = '') {
  if (!val) return fallback;
  return String(val).trim() || fallback;
}

const extractedData = {
  // Section 1: Business Information
  company_name:         clean(formData.q4_hvacCompany || formData['q4_hvacCompany']),
  owner_name:           clean(formData.q54_ownerName || formData['q54_ownerName']),
  main_phone:           clean(formData.q6_mainCompany || formData['q6_mainCompany']),
  client_email:         clean(formData.q5_emailAddress || formData['q5_emailAddress']),
  website:              clean(formData.q7_companyWebsite || formData['q7_companyWebsite']),
  years_in_business:    clean(formData.q8_yearsIn || formData['q8_yearsIn']),
  timezone:             clean(formData.q34_timezone || formData['q34_timezone'], 'America/Chicago'),
  services_offered:     normalizeList(formData.q13_servicesOffered || formData['q13_servicesOffered']),
  brands_serviced:      normalizeList(formData.q14_brandsequipmentServiced || formData['q14_brandsequipmentServiced']),
  service_area:         clean(formData.q16_primaryService || formData['q16_primaryService']),
  service_area_radius:  clean(formData.q40_serviceAreaRadius || formData['q40_serviceAreaRadius']),
  certifications:       normalizeList(formData.q29_certifications || formData['q29_certifications']),
  licensed_insured:     clean(formData.q28_licensedAnd || formData['q28_licensedAnd'], 'Yes'),

  // Section 2: AI Receptionist Configuration
  agent_name:           clean(formData.q10_aiAgent10 || formData['q10_aiAgent10']),
  voice_gender:         clean(formData.q11_aiVoice || formData['q11_aiVoice'], 'Female'),
  custom_greeting:      clean(formData.q38_customGreeting || formData['q38_customGreeting']),
  company_tagline:      clean(formData.q39_companyTagline || formData['q39_companyTagline']),
  business_hours:       clean(formData.q17_businessHours || formData['q17_businessHours']),
  response_time:        clean(formData.q18_typicalResponse || formData['q18_typicalResponse']),
  emergency_service:    clean(formData.q20_247Emergency || formData['q20_247Emergency'], 'No'),
  emergency_phone:      clean(formData.q21_emergencyAfterhours || formData['q21_emergencyAfterhours']),
  after_hours_behavior: clean(formData.q22_afterhoursBehavior || formData['q22_afterhoursBehavior']),

  // Section 3: Call Handling & Pricing
  pricing_policy:       clean(formData.q42_pricingPolicy || formData['q42_pricingPolicy'], 'We provide free quotes on-site'),
  diagnostic_fee:       clean(formData.q41_diagnosticFee || formData['q41_diagnosticFee']),
  standard_fees:        clean(formData.q43_standardFees || formData['q43_standardFees']),
  free_estimates:       clean(formData.q24_freeEstimates || formData['q24_freeEstimates'], 'Yes - always free'),
  do_not_service:       clean(formData.q57_doNotServiceList || formData['q57_doNotServiceList']),
  transfer_phone:       clean(formData.q48_transferPhone || formData['q48_transferPhone']),
  transfer_triggers:    normalizeList(formData.q49_transferTriggers || formData['q49_transferTriggers']),
  transfer_behavior:    clean(formData.q50_transferBehavior || formData['q50_transferBehavior'], 'Try once - take message if no answer'),

  // Section 4: Lead Capture & Notifications
  lead_contact_method:  clean(formData.q31_leadContact || formData['q31_leadContact'], 'Both'),
  lead_phone:           clean(formData.q32_leadNotification || formData['q32_leadNotification']),
  lead_email:           clean(formData.q33_leadNotification33 || formData['q33_leadNotification33']),

  // Section 5: Branding, Promotions & Extras
  google_review_rating: clean(formData.q55_googleReviewRating || formData['q55_googleReviewRating']),
  google_review_count:  clean(formData.q56_googleReviewCount || formData['q56_googleReviewCount']),
  unique_selling_points: clean(formData.q51_uniqueSellingPoints || formData['q51_uniqueSellingPoints']),
  current_promotion:    clean(formData.q52_currentPromotion || formData['q52_currentPromotion']),
  seasonal_services:    clean(formData.q53_seasonalServices || formData['q53_seasonalServices']),
  membership_program:   clean(formData.q58_membershipProgramName || formData['q58_membershipProgramName']),
  maintenance_plans:    clean(formData.q46_maintenancePlans || formData['q46_maintenancePlans'], 'No'),
  financing_available:  clean(formData.q25_financingAvailable || formData['q25_financingAvailable'], 'No'),
  financing_details:    clean(formData.q44_financingDetails || formData['q44_financingDetails']),
  warranty:             clean(formData.q26_serviceWarranties || formData['q26_serviceWarranties'], 'Yes'),
  warranty_details:     clean(formData.q27_warrantyDetails || formData['q27_warrantyDetails']),
  payment_methods:      normalizeList(formData.q45_paymentMethods || formData['q45_paymentMethods']),
  additional_info:      clean(formData.q37_additionalInfo || formData['q37_additionalInfo']),

  // Additional Notification Contacts (q64-q67)
  notification_sms_2:   clean(formData.q64_notifSms2   || formData['q64_notifSms2']),
  notification_sms_3:   clean(formData.q65_notifSms3   || formData['q65_notifSms3']),
  notification_email_2: clean(formData.q66_notifEmail2 || formData['q66_notifEmail2']),
  notification_email_3: clean(formData.q67_notifEmail3 || formData['q67_notifEmail3']),

  // Stripe
  stripe_customer_id:   clean(formData.stripe_customer_id || formData['stripe_customer_id'])
};

// === Build company info block for the Retell prompt ===
let companyInfoBlock = `## Company Overview\n`;
companyInfoBlock += `- Company Name: ${extractedData.company_name}\n`;
if (extractedData.main_phone) companyInfoBlock += `- Main Phone: ${extractedData.main_phone}\n`;
if (extractedData.years_in_business) companyInfoBlock += `- Experience: ${extractedData.years_in_business} years in business\n`;
if (extractedData.owner_name) companyInfoBlock += `- Owner/Manager: ${extractedData.owner_name}\n`;
if (extractedData.company_tagline) companyInfoBlock += `- Tagline: ${extractedData.company_tagline}\n`;
if (extractedData.website) companyInfoBlock += `- Website: ${extractedData.website}\n`;
companyInfoBlock += `- Licensed & Insured: ${extractedData.licensed_insured}\n`;
if (extractedData.certifications) companyInfoBlock += `- Certifications: ${extractedData.certifications}\n`;

companyInfoBlock += `\n## Services\n`;
if (extractedData.services_offered) companyInfoBlock += `- Services: ${extractedData.services_offered}\n`;
if (extractedData.brands_serviced) companyInfoBlock += `- Brands Serviced: ${extractedData.brands_serviced}\n`;
if (extractedData.service_area) {
  let areaLine = extractedData.service_area;
  if (extractedData.service_area_radius) areaLine += ` (within ${extractedData.service_area_radius})`;
  companyInfoBlock += `- Service Area: ${areaLine}\n`;
}
if (extractedData.do_not_service) companyInfoBlock += `- DO NOT Service: ${extractedData.do_not_service}\n`;

companyInfoBlock += `\n## Hours & Availability\n`;
if (extractedData.business_hours) companyInfoBlock += `- Business Hours: ${extractedData.business_hours}\n`;
if (extractedData.response_time) companyInfoBlock += `- Typical Response Time: ${extractedData.response_time}\n`;

companyInfoBlock += `\n## Pricing & Policies\n`;
companyInfoBlock += `- Pricing Policy: ${extractedData.pricing_policy}\n`;
if (extractedData.diagnostic_fee) companyInfoBlock += `- Diagnostic/Service Call Fee: ${extractedData.diagnostic_fee} (applied to repair if customer proceeds)\n`;
if (extractedData.standard_fees) companyInfoBlock += `- Set Fees (ONLY share these specific fees when asked): ${extractedData.standard_fees}\n`;
companyInfoBlock += `- Free Estimates: ${extractedData.free_estimates}\n`;
if (extractedData.financing_available !== 'No') {
  let finLine = `Financing Available: Yes`;
  if (extractedData.financing_details) finLine += ` - ${extractedData.financing_details}`;
  companyInfoBlock += `- ${finLine}\n`;
}
if (extractedData.warranty !== 'No') {
  let warLine = `Warranty: Yes`;
  if (extractedData.warranty_details) warLine += ` - ${extractedData.warranty_details}`;
  companyInfoBlock += `- ${warLine}\n`;
}
if (extractedData.maintenance_plans !== 'No') {
  let mainLine = `Maintenance Plans: Available`;
  if (extractedData.membership_program) mainLine += ` - "${extractedData.membership_program}"`;
  companyInfoBlock += `- ${mainLine}\n`;
}
if (extractedData.payment_methods) companyInfoBlock += `- Payment Methods: ${extractedData.payment_methods}\n`;

if (extractedData.emergency_service && extractedData.emergency_service !== 'No') {
  companyInfoBlock += `\n## Emergency Service\n`;
  companyInfoBlock += `- Emergency Service: ${extractedData.emergency_service}\n`;
  if (extractedData.emergency_phone) companyInfoBlock += `- Emergency Contact: ${extractedData.emergency_phone}\n`;
  if (extractedData.after_hours_behavior) companyInfoBlock += `- After Hours Handling: ${extractedData.after_hours_behavior}\n`;
}

if (extractedData.google_review_rating || extractedData.current_promotion || extractedData.seasonal_services || extractedData.unique_selling_points) {
  companyInfoBlock += `\n## Promotions & Highlights\n`;
  if (extractedData.google_review_rating && extractedData.google_review_rating !== 'Not listed on Google') {
    let reviewLine = `Google Rating: ${extractedData.google_review_rating} stars`;
    if (extractedData.google_review_count && extractedData.google_review_count !== 'Not listed on Google') {
      reviewLine += ` with ${extractedData.google_review_count} reviews`;
    }
    companyInfoBlock += `- ${reviewLine}\n`;
  }
  if (extractedData.current_promotion) companyInfoBlock += `- Current Promotion: ${extractedData.current_promotion}\n`;
  if (extractedData.seasonal_services) companyInfoBlock += `- Seasonal Services: ${extractedData.seasonal_services}\n`;
  if (extractedData.unique_selling_points) companyInfoBlock += `- Why Choose Us: ${extractedData.unique_selling_points}\n`;
}

if (extractedData.additional_info) {
  companyInfoBlock += `\n## Additional Notes\n`;
  companyInfoBlock += `${extractedData.additional_info}\n`;
}

return {
  ...extractedData,
  companyInfoBlock,
  timestamp: new Date().toISOString()
};