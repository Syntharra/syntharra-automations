#!/usr/bin/env node
// Harness: run the n8n `Build Retell Prompt` JS code node standalone.
//
// Reads a Supabase `hvac_standard_agent` row (JSON) from argv[2], runs it
// through the JotForm adapter logic (to reconstruct the `data` shape that
// `Build Retell Prompt` expects — including companyInfoBlock), then evals
// the JS compiler code with that `data` injected.
//
// Usage:  node tools/run_js_compiler.js <supabase_row.json> <out_golden.json>
//
// This harness exists ONLY to generate golden fixtures for parity-testing
// the Python port. It is NOT part of production.

const fs = require('fs');
const path = require('path');

if (process.argv.length < 4) {
  console.error('Usage: node run_js_compiler.js <input_row.json> <output.json>');
  process.exit(1);
}

const inputPath = process.argv[2];
const outputPath = process.argv[3];
const FIXED_TIMESTAMP = '2026-04-09T00:00:00.000Z';

const row = JSON.parse(fs.readFileSync(inputPath, 'utf-8'));

// ----- Adapter: Supabase row -> `data` shape expected by Build Retell Prompt.
// The schema stores `company_phone` but BRP reads `main_phone`; map it.
// Also rebuild `companyInfoBlock` using Parse_JotForm_Data logic verbatim.
// Null -> '' so `||` defaults in BRP fire correctly.
function nn(v) { return (v === null || v === undefined) ? '' : v; }

const ed = {
  company_name:         nn(row.company_name),
  owner_name:           nn(row.owner_name),
  main_phone:           nn(row.company_phone), // schema rename
  client_email:         nn(row.client_email),
  website:              nn(row.website),
  years_in_business:    nn(row.years_in_business),
  timezone:             nn(row.timezone) || 'America/Chicago',
  services_offered:     nn(row.services_offered),
  brands_serviced:      nn(row.brands_serviced),
  certifications:       nn(row.certifications),
  service_area:         nn(row.service_area),
  service_area_radius:  nn(row.service_area_radius),
  licensed_insured:     nn(row.licensed_insured) || 'Yes',
  agent_name:           nn(row.agent_name),
  voice_gender:         nn(row.voice_gender) || 'Female',
  custom_greeting:      nn(row.custom_greeting),
  company_tagline:      nn(row.company_tagline),
  business_hours:       nn(row.business_hours),
  response_time:        nn(row.response_time),
  emergency_service:    nn(row.emergency_service) || 'No',
  emergency_phone:      nn(row.emergency_phone),
  after_hours_behavior: nn(row.after_hours_behavior),
  after_hours_transfer: nn(row.after_hours_transfer),
  pricing_policy:       nn(row.pricing_policy) || 'We provide free quotes on-site',
  diagnostic_fee:       nn(row.diagnostic_fee),
  standard_fees:        nn(row.standard_fees),
  free_estimates:       nn(row.free_estimates) || 'Yes - always free',
  do_not_service:       nn(row.do_not_service),
  transfer_phone:       nn(row.transfer_phone),
  transfer_triggers:    nn(row.transfer_triggers),
  transfer_behavior:    nn(row.transfer_behavior) || 'Try once - take message if no answer',
  lead_contact_method:  nn(row.lead_contact_method) || 'Both',
  lead_phone:           nn(row.lead_phone),
  lead_email:           nn(row.lead_email),
  notification_sms_2:   row.notification_sms_2,
  notification_sms_3:   row.notification_sms_3,
  notification_email_2: row.notification_email_2,
  notification_email_3: row.notification_email_3,
  google_review_rating:  nn(row.google_review_rating),
  google_review_count:   nn(row.google_review_count),
  unique_selling_points: nn(row.unique_selling_points),
  current_promotion:     nn(row.current_promotion),
  seasonal_services:     nn(row.seasonal_services),
  membership_program:    nn(row.membership_program),
  maintenance_plans:     nn(row.maintenance_plans) || 'No',
  financing_available:   nn(row.financing_available) || 'No',
  financing_details:     nn(row.financing_details),
  warranty:              nn(row.warranty) || 'Yes',
  warranty_details:      nn(row.warranty_details),
  payment_methods:       nn(row.payment_methods),
  additional_info:       nn(row.additional_info),
  stripe_customer_id:    nn(row.stripe_customer_id),
  industry_type:         nn(row.industry_type) || 'HVAC',
  submission_id:         nn(row.submission_id),
  separate_emergency_phone: '', // not stored; default
  is_demo:               false, // not stored; updates default to live
};

// ----- Build companyInfoBlock (verbatim port of Parse_JotForm_Data lines 112-182)
let companyInfoBlock = '## Company Overview\n';
companyInfoBlock += `- Company Name: ${ed.company_name}\n`;
if (ed.main_phone) companyInfoBlock += `- Main Phone: ${ed.main_phone}\n`;
if (ed.years_in_business) companyInfoBlock += `- Experience: ${ed.years_in_business} years in business\n`;
if (ed.owner_name) companyInfoBlock += `- Owner/Manager: ${ed.owner_name}\n`;
if (ed.company_tagline) companyInfoBlock += `- Tagline: ${ed.company_tagline}\n`;
if (ed.website) companyInfoBlock += `- Website: ${ed.website}\n`;
companyInfoBlock += `- Licensed & Insured: ${ed.licensed_insured}\n`;
if (ed.certifications) companyInfoBlock += `- Certifications: ${ed.certifications}\n`;

companyInfoBlock += '\n## Services\n';
if (ed.services_offered) companyInfoBlock += `- Services: ${ed.services_offered}\n`;
if (ed.brands_serviced) companyInfoBlock += `- Brands Serviced: ${ed.brands_serviced}\n`;
if (ed.service_area) {
  let areaLine = ed.service_area;
  if (ed.service_area_radius) areaLine += ` (within ${ed.service_area_radius})`;
  companyInfoBlock += `- Service Area: ${areaLine}\n`;
}
if (ed.do_not_service) companyInfoBlock += `- DO NOT Service: ${ed.do_not_service}\n`;

companyInfoBlock += '\n## Hours & Availability\n';
if (ed.business_hours) companyInfoBlock += `- Business Hours: ${ed.business_hours}\n`;
if (ed.response_time) companyInfoBlock += `- Typical Response Time: ${ed.response_time}\n`;

companyInfoBlock += '\n## Pricing & Policies\n';
companyInfoBlock += `- Pricing Policy: ${ed.pricing_policy}\n`;
if (ed.diagnostic_fee) companyInfoBlock += `- Diagnostic/Service Call Fee: ${ed.diagnostic_fee} (applied to repair if customer proceeds)\n`;
if (ed.standard_fees) companyInfoBlock += `- Set Fees (ONLY share these specific fees when asked): ${ed.standard_fees}\n`;
companyInfoBlock += `- Free Estimates: ${ed.free_estimates}\n`;
if (ed.financing_available !== 'No') {
  let finLine = 'Financing Available: Yes';
  if (ed.financing_details) finLine += ` - ${ed.financing_details}`;
  companyInfoBlock += `- ${finLine}\n`;
}
if (ed.warranty !== 'No') {
  let warLine = 'Warranty: Yes';
  if (ed.warranty_details) warLine += ` - ${ed.warranty_details}`;
  companyInfoBlock += `- ${warLine}\n`;
}
if (ed.maintenance_plans !== 'No') {
  let mainLine = 'Maintenance Plans: Available';
  if (ed.membership_program) mainLine += ` - "${ed.membership_program}"`;
  companyInfoBlock += `- ${mainLine}\n`;
}
if (ed.payment_methods) companyInfoBlock += `- Payment Methods: ${ed.payment_methods}\n`;

if (ed.emergency_service && ed.emergency_service !== 'No') {
  companyInfoBlock += '\n## Emergency Service\n';
  companyInfoBlock += `- Emergency Service: ${ed.emergency_service}\n`;
  if (ed.emergency_phone) companyInfoBlock += `- Emergency Contact: ${ed.emergency_phone}\n`;
  if (ed.after_hours_behavior) companyInfoBlock += `- After Hours Handling: ${ed.after_hours_behavior}\n`;
}

if (ed.google_review_rating || ed.current_promotion || ed.seasonal_services || ed.unique_selling_points) {
  companyInfoBlock += '\n## Promotions & Highlights\n';
  if (ed.google_review_rating && ed.google_review_rating !== 'Not listed on Google') {
    let reviewLine = `Google Rating: ${ed.google_review_rating} stars`;
    if (ed.google_review_count && ed.google_review_count !== 'Not listed on Google') {
      reviewLine += ` with ${ed.google_review_count} reviews`;
    }
    companyInfoBlock += `- ${reviewLine}\n`;
  }
  if (ed.current_promotion) companyInfoBlock += `- Current Promotion: ${ed.current_promotion}\n`;
  if (ed.seasonal_services) companyInfoBlock += `- Seasonal Services: ${ed.seasonal_services}\n`;
  if (ed.unique_selling_points) companyInfoBlock += `- Why Choose Us: ${ed.unique_selling_points}\n`;
}

if (ed.additional_info) {
  companyInfoBlock += '\n## Additional Notes\n';
  companyInfoBlock += `${ed.additional_info}\n`;
}

// Final `data` object: Parse_JotForm output shape
const data = { ...ed, companyInfoBlock };

// Persist the exact input that will feed Build Retell Prompt,
// so the Python port can be tested against the SAME input.
const brpInputPath = path.join(path.dirname(outputPath), 'brp_input.json');
fs.writeFileSync(brpInputPath, JSON.stringify(data, null, 2));

// ----- Load Build Retell Prompt source and neutralise n8n-only references.
const brpSource = fs.readFileSync(
  path.join(__dirname, '..', 'tests', 'fixtures', 'prompt_compiler', 'Build_Retell_Prompt.js'),
  'utf-8'
);

// Strip the `const data = $("...").first().json;` line so we can inject our own.
const brpBody = brpSource.replace(
  /const\s+data\s*=\s*\$\(.*?\)\.first\(\)\.json\s*;/,
  '/* data injected by harness */'
);
if (brpBody === brpSource) {
  console.error('FAILED to strip `const data = $(...)` line from BRP source');
  process.exit(2);
}

// Mock Date so new Date().toISOString() is deterministic.
const RealDate = Date;
global.Date = class extends RealDate {
  constructor(...args) {
    if (args.length === 0) return new RealDate(FIXED_TIMESTAMP);
    return new RealDate(...args);
  }
  static now() { return new RealDate(FIXED_TIMESTAMP).getTime(); }
};

// Eval the compiler body wrapped in a function so the `return` at the end works.
const compilerFn = new Function('data', brpBody);
const result = compilerFn(data);

fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
console.log(`Wrote golden: ${outputPath} (${fs.statSync(outputPath).size} bytes)`);
console.log(`Wrote BRP input: ${brpInputPath}`);
