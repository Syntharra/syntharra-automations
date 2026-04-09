// Reach back to webhook for submission_id (Parse node doesn't forward it)
// Fixed 2026-04-07 regression
const j = $input.first().json;
let webhookRaw;
try { webhookRaw = $('JotForm Webhook Trigger').first().json; } catch(e) { webhookRaw = j; }
const wb = webhookRaw.body || webhookRaw;
const nested = (wb && wb.body) ? wb.body : wb;
const submission_id =
  (nested && (nested.submission_id || nested.submissionID || nested.submission)) ||
  (wb && (wb.submission_id || wb.submissionID || wb.submission)) ||
  j.submission_id || j.submissionID || '';
if (!submission_id) {
  throw new Error('submission_id missing from webhook. Webhook keys: ' + Object.keys(wb||{}).join(',') + ' | item keys: ' + Object.keys(j).join(','));
}
const tier = 'standard';
const client_id = j.company_name || (nested && nested.company_name) || 'unknown';
return {
  ...j,
  submission_id: String(submission_id),
  tier,
  client_id,
  timestamp: j.timestamp || new Date().toISOString()
};
