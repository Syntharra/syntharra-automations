// ── Stripe Welcome Email — Approved Branding ──
// Workflow: ydzfhitWiF5wNzEy (Extract Session Data node)
// All variables from Stripe checkout session

const body = $input.first().json.body;
const session = body.data.object;

const customerId = session.customer;
const subscriptionId = session.subscription;
const sessionId = session.id;
const customerEmail = session.customer_details?.email || '';
const customerName = session.customer_details?.name || 'Valued Client';
const paymentStatus = session.payment_status;

const plans = {
  'price_1TDckaECS71NQsk8DdNsWy1o': { name: 'Standard', billing: 'Monthly', amount: '$497/mo', setupFeePrice: 'price_1TEKKrECS71NQsk8Mw3Z8CoC', minutes: '475', jotformUrl: 'https://form.jotform.com/260795139953066' },
  'price_1TDckiECS71NQsk8fqDio8pw': { name: 'Standard', billing: 'Annual',  amount: '$414/mo', setupFeePrice: 'price_1TEKKrECS71NQsk8Mw3Z8CoC', minutes: '475', jotformUrl: 'https://form.jotform.com/260795139953066' },
  'price_1TDclGECS71NQsk8OoLoMV0q': { name: 'Premium',  billing: 'Monthly', amount: '$997/mo', setupFeePrice: 'price_1TEKKvECS71NQsk8vWGjHLUP', minutes: '1,000', jotformUrl: 'https://form.jotform.com/260819259556671' },
  'price_1TDclPECS71NQsk8S9bAPGoJ': { name: 'Premium',  billing: 'Annual',  amount: '$831/mo', setupFeePrice: 'price_1TEKKvECS71NQsk8vWGjHLUP', minutes: '1,000', jotformUrl: 'https://form.jotform.com/260819259556671' }
};

const priceId = session.metadata?.price_id || '';
let plan = plans[priceId];
if (!plan && session.line_items?.data) {
  const li = session.line_items.data.find(l => plans[l.price?.id]);
  if (li) plan = plans[li.price.id];
}
if (!plan) plan = plans['price_1TDckaECS71NQsk8DdNsWy1o'];

const signupDate = new Date(session.created * 1000).toLocaleDateString('en-AU', { day: '2-digit', month: 'long', year: 'numeric' });

const ICON_URL = 'https://raw.githubusercontent.com/Syntharra/syntharra-website/main/logo-icon-2x.png';
const LOGO = `<table cellpadding="0" cellspacing="0" style="margin:0 auto"><tr><td style="vertical-align:middle;padding-right:10px"><img src="${ICON_URL}" alt="" width="36" height="36" style="display:block;border:0"></td><td style="vertical-align:middle;text-align:left"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="text-align:left;padding:0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:16px;font-weight:700;letter-spacing:-0.3px;color:#0f0f1a;line-height:1;text-align:left">Syntharra</div></td></tr><tr><td style="text-align:left;padding:3px 0 0 0"><div style="font-family:Inter,-apple-system,sans-serif;font-size:7.5px;font-weight:600;letter-spacing:1.2px;color:#6C63FF;text-transform:uppercase;line-height:1;text-align:left">Global AI Solutions</div></td></tr></table></td></tr></table>`;
const FOOTER = `<tr><td style="padding:20px;text-align:center"><a href="https://www.syntharra.com" style="color:#6C63FF;font-size:13px;font-weight:600;text-decoration:none">syntharra.com</a></td></tr><tr><td style="text-align:center;padding:0 0 16px"><p style="color:#9CA3AF;font-size:11px;margin:0">Syntharra AI Solutions \u2014 AI Receptionists for the Trade Industry</p></td></tr>`;

const emailHtml = `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700&display=swap" rel="stylesheet"></head>
<body style="margin:0;padding:0;background-color:#F7F7FB;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#F7F7FB;padding:40px 16px"><tr><td align="center">
<table width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%">
<tr><td style="padding:0 0 24px;text-align:center">${LOGO}</td></tr>
<tr><td style="background-color:#ffffff;border-radius:12px;border:1px solid #E5E7EB;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
<div style="height:3px;background:linear-gradient(90deg,#6C63FF,#8B7FFF)"></div>
<div style="padding:32px 36px">
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:16px"><tr><td><span style="display:inline-block;font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#6C63FF;background-color:#F0EEFF;padding:4px 12px;border-radius:20px">Payment Confirmed</span></td></tr></table>
<h1 style="color:#1A1A2E;font-size:24px;font-weight:700;margin:0 0 6px;line-height:1.3">Welcome to Syntharra!</h1>
<p style="color:#6B7280;font-size:14px;line-height:1.6;margin:0 0 24px">Hi ${customerName}, your payment has been received and your AI Receptionist subscription is confirmed. One last step to get you live.</p>
<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;background-color:#F0EEFF;border-radius:10px;overflow:hidden"><tr><td style="padding:18px 22px">
  <p style="margin:4px 0;font-size:13px;color:#6B7280"><strong style="color:#1A1A2E">Plan:</strong> ${plan.name} \u2014 AI Receptionist${plan.name === 'Premium' ? ' Pro' : ''}</p>
  <p style="margin:4px 0;font-size:13px;color:#6B7280"><strong style="color:#1A1A2E">Billing:</strong> ${plan.billing} (${plan.amount})</p>
  <p style="margin:4px 0;font-size:13px;color:#6B7280"><strong style="color:#1A1A2E">Minutes:</strong> ${plan.minutes} minutes/month</p>
  <p style="margin:4px 0;font-size:13px;color:#6B7280"><strong style="color:#1A1A2E">Date:</strong> ${signupDate}</p>
</td></tr></table>
<p style="color:#6B7280;font-size:14px;line-height:1.6;margin:0 0 24px">Complete your onboarding form (takes less than 5 minutes) so we can build and configure your AI Receptionist to your exact business requirements.</p>
<div style="text-align:center;margin:0 0 16px"><a href="${plan.jotformUrl}" style="display:inline-block;background-color:#6C63FF;color:#ffffff;padding:16px 44px;border-radius:10px;text-decoration:none;font-weight:700;font-size:16px">Complete Onboarding Form \u2192</a></div>
<p style="text-align:center;font-size:12px;color:#9CA3AF;margin:0">Your AI Receptionist will be live within 1 business day of form submission.</p>
<p style="color:#6B7280;font-size:13px;line-height:1.6;margin:16px 0 0">Questions? Email us at <a href="mailto:support@syntharra.com" style="color:#6C63FF;font-weight:600;text-decoration:none">support@syntharra.com</a></p>
</div></td></tr>
${FOOTER}
</table></td></tr></table></body></html>`;

return [{ json: { customerId, subscriptionId, sessionId, customerEmail, customerName, planName: plan.name, planBilling: plan.billing, planAmount: plan.amount, setupFeePrice: plan.setupFeePrice, minutes: plan.minutes, jotformUrl: plan.jotformUrl, emailHtml, paymentStatus, signupDate } }];
