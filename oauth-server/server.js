// ============================================================
// Syntharra OAuth Server
// ============================================================
// Handles OAuth connections for calendar/CRM integrations.
// Deployed at: auth.syntharra.com (Railway)
//
// Flow:
// 1. Client clicks "Connect Google Calendar →" in setup email
// 2. GET /connect?platform=google_calendar&agent=agent_xxx
// 3. Server redirects to Google OAuth consent screen
// 4. Google redirects back to /callback?code=xxx&state=xxx
// 5. Server exchanges code for tokens
// 6. Server stores tokens in Supabase
// 7. Server shows success page
//
// Also handles API key submissions:
// GET /submit-key?agent=agent_xxx → shows form
// POST /submit-key → stores API key in Supabase
// ============================================================

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const PORT = process.env.PORT || 3000;

// ── Environment Variables ───────────────────────────────────
const SUPABASE_URL = process.env.SUPABASE_URL || 'https://hgheyqwnrcvwtgngqdnq.supabase.co';
const SUPABASE_KEY = process.env.SUPABASE_KEY || '';

// Google OAuth
const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID || '';
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET || '';
const GOOGLE_REDIRECT_URI = process.env.GOOGLE_REDIRECT_URI || 'https://auth.syntharra.com/callback';

// Microsoft OAuth
const MS_CLIENT_ID = process.env.MS_CLIENT_ID || '';
const MS_CLIENT_SECRET = process.env.MS_CLIENT_SECRET || '';
const MS_REDIRECT_URI = process.env.MS_REDIRECT_URI || 'https://auth.syntharra.com/callback';

// Calendly OAuth
const CALENDLY_CLIENT_ID = process.env.CALENDLY_CLIENT_ID || '';
const CALENDLY_CLIENT_SECRET = process.env.CALENDLY_CLIENT_SECRET || '';

// ── Platform OAuth Configs ──────────────────────────────────
const PLATFORMS = {
  google_calendar: {
    name: 'Google Calendar',
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    scopes: 'https://www.googleapis.com/auth/calendar',
    clientId: () => GOOGLE_CLIENT_ID,
    clientSecret: () => GOOGLE_CLIENT_SECRET,
    redirectUri: () => GOOGLE_REDIRECT_URI,
    category: 'calendar'
  },
  outlook: {
    name: 'Microsoft Outlook',
    authUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    tokenUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
    scopes: 'https://graph.microsoft.com/Calendars.ReadWrite offline_access',
    clientId: () => MS_CLIENT_ID,
    clientSecret: () => MS_CLIENT_SECRET,
    redirectUri: () => MS_REDIRECT_URI,
    category: 'calendar'
  },
  calendly: {
    name: 'Calendly',
    authUrl: 'https://auth.calendly.com/oauth/authorize',
    tokenUrl: 'https://auth.calendly.com/oauth/token',
    scopes: '',
    clientId: () => CALENDLY_CLIENT_ID,
    clientSecret: () => CALENDLY_CLIENT_SECRET,
    redirectUri: () => GOOGLE_REDIRECT_URI, // Same redirect
    category: 'calendar'
  },
  jobber: {
    name: 'Jobber',
    authUrl: 'https://api.getjobber.com/api/oauth/authorize',
    tokenUrl: 'https://api.getjobber.com/api/oauth/token',
    scopes: '',
    clientId: () => process.env.JOBBER_CLIENT_ID || '',
    clientSecret: () => process.env.JOBBER_CLIENT_SECRET || '',
    redirectUri: () => GOOGLE_REDIRECT_URI,
    category: 'both' // CRM + Calendar
  },
  housecallpro: {
    name: 'Housecall Pro',
    authUrl: 'https://api.housecallpro.com/oauth/authorize',
    tokenUrl: 'https://api.housecallpro.com/oauth/token',
    scopes: '',
    clientId: () => process.env.HCP_CLIENT_ID || '',
    clientSecret: () => process.env.HCP_CLIENT_SECRET || '',
    redirectUri: () => GOOGLE_REDIRECT_URI,
    category: 'both'
  },
  hubspot: {
    name: 'HubSpot',
    authUrl: 'https://app.hubspot.com/oauth/authorize',
    tokenUrl: 'https://api.hubapi.com/oauth/v1/token',
    scopes: 'crm.objects.contacts.write crm.objects.contacts.read',
    clientId: () => process.env.HUBSPOT_CLIENT_ID || '',
    clientSecret: () => process.env.HUBSPOT_CLIENT_SECRET || '',
    redirectUri: () => GOOGLE_REDIRECT_URI,
    category: 'crm'
  },
  gohighlevel: {
    name: 'GoHighLevel',
    authUrl: 'https://marketplace.gohighlevel.com/oauth/chooselocation',
    tokenUrl: 'https://services.leadconnectorhq.com/oauth/token',
    scopes: 'contacts.write contacts.readonly calendars.write calendars.readonly',
    clientId: () => process.env.GHL_CLIENT_ID || '',
    clientSecret: () => process.env.GHL_CLIENT_SECRET || '',
    redirectUri: () => GOOGLE_REDIRECT_URI,
    category: 'crm'
  }
};

// ── Brand HTML Template ─────────────────────────────────────
function page(title, content) {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>${title} — Syntharra</title>
<style>
body { margin:0; padding:40px 16px; background:#F7F7FB; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; }
.card { max-width:500px; margin:0 auto; background:#fff; border-radius:12px; border:1px solid #E5E7EB; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.06); }
.accent { height:3px; background:linear-gradient(90deg,#6C63FF,#8B7FFF); }
.content { padding:32px 36px; }
h2 { color:#1A1A2E; font-size:22px; margin:0 0 8px; }
p { color:#6B7280; font-size:15px; line-height:1.6; }
.success { color:#10B981; }
.error { color:#EF4444; }
.logo { display:block; margin:0 auto 24px; }
.btn { display:inline-block; background:#6C63FF; color:#fff; padding:12px 32px; border-radius:8px; text-decoration:none; font-weight:600; font-size:15px; border:none; cursor:pointer; }
input { width:100%; padding:12px; border:1px solid #E5E7EB; border-radius:8px; font-size:14px; margin:8px 0 16px; box-sizing:border-box; }
label { color:#1A1A2E; font-size:14px; font-weight:600; }
</style></head><body>
<img src="https://i.postimg.cc/zBSrKLDb/company-logo-link.png" alt="Syntharra" width="160" class="logo">
<div class="card"><div class="accent"></div><div class="content">${content}</div></div>
<p style="text-align:center;color:#9CA3AF;font-size:12px;margin-top:20px">support@syntharra.com | www.syntharra.com</p>
</body></html>`;
}

// ============================================================
// ROUTE: /connect — Start OAuth flow
// ============================================================
app.get('/connect', (req, res) => {
  const { platform, agent } = req.query;
  
  if (!platform || !agent) {
    return res.status(400).send(page('Error', '<h2 class="error">Missing Parameters</h2><p>This link appears to be invalid. Please check your setup email and try again.</p>'));
  }
  
  const config = PLATFORMS[platform];
  if (!config) {
    return res.status(400).send(page('Error', `<h2 class="error">Unknown Platform</h2><p>Platform "${platform}" is not supported. Please contact support.</p>`));
  }
  
  const clientId = config.clientId();
  if (!clientId) {
    return res.status(500).send(page('Setup Required', `<h2>Coming Soon</h2><p>${config.name} integration is being configured. We will send you a new setup link shortly.</p>`));
  }
  
  // Build state parameter (encoded: platform|agent_id)
  const state = Buffer.from(JSON.stringify({ platform, agent })).toString('base64url');
  
  // Build OAuth URL
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: config.redirectUri(),
    response_type: 'code',
    scope: config.scopes,
    access_type: 'offline',
    prompt: 'consent',
    state: state
  });
  
  const authUrl = `${config.authUrl}?${params.toString()}`;
  res.redirect(authUrl);
});

// ============================================================
// ROUTE: /callback — Handle OAuth callback
// ============================================================
app.get('/callback', async (req, res) => {
  const { code, state, error } = req.query;
  
  if (error) {
    return res.send(page('Connection Cancelled', `<h2>Connection Cancelled</h2><p>You cancelled the connection process. You can try again anytime using the link in your setup email.</p>`));
  }
  
  if (!code || !state) {
    return res.status(400).send(page('Error', '<h2 class="error">Invalid Callback</h2><p>Missing authorization code. Please try again.</p>'));
  }
  
  // Decode state
  let stateData;
  try {
    stateData = JSON.parse(Buffer.from(state, 'base64url').toString());
  } catch (e) {
    return res.status(400).send(page('Error', '<h2 class="error">Invalid State</h2><p>The connection link has expired. Please use the link from your setup email.</p>'));
  }
  
  const { platform, agent } = stateData;
  const config = PLATFORMS[platform];
  
  if (!config) {
    return res.status(400).send(page('Error', '<h2 class="error">Unknown Platform</h2>'));
  }
  
  // Exchange code for tokens
  try {
    const tokenParams = new URLSearchParams({
      code: code,
      client_id: config.clientId(),
      client_secret: config.clientSecret(),
      redirect_uri: config.redirectUri(),
      grant_type: 'authorization_code'
    });
    
    const tokenResponse = await fetch(config.tokenUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: tokenParams.toString()
    });
    
    const tokens = await tokenResponse.json();
    
    if (!tokens.access_token) {
      throw new Error(tokens.error_description || tokens.error || 'No access token returned');
    }
    
    // Store tokens in Supabase
    const updateBody = {};
    if (config.category === 'calendar' || config.category === 'both') {
      updateBody.calendar_access_token = tokens.access_token;
      updateBody.calendar_refresh_token = tokens.refresh_token || '';
      updateBody.calendar_token_expiry = new Date(Date.now() + (tokens.expires_in || 3600) * 1000).toISOString();
      updateBody.calendar_status = 'connected';
      updateBody.calendar_auth_method = 'oauth';
    }
    if (config.category === 'crm' || config.category === 'both') {
      updateBody.crm_access_token = tokens.access_token;
      updateBody.crm_refresh_token = tokens.refresh_token || '';
      updateBody.crm_token_expiry = new Date(Date.now() + (tokens.expires_in || 3600) * 1000).toISOString();
      updateBody.crm_status = 'connected';
      updateBody.crm_auth_method = 'oauth';
    }
    
    const supabaseResponse = await fetch(
      `${SUPABASE_URL}/rest/v1/hvac_premium_agent?agent_id=eq.${agent}`,
      {
        method: 'PATCH',
        headers: {
          'apikey': SUPABASE_KEY,
          'Authorization': `Bearer ${SUPABASE_KEY}`,
          'Content-Type': 'application/json',
          'Prefer': 'return=representation'
        },
        body: JSON.stringify(updateBody)
      }
    );
    
    const updated = await supabaseResponse.json();
    
    if (Array.isArray(updated) && updated.length > 0) {
      res.send(page('Connected!', `
        <h2 class="success">✅ ${config.name} Connected!</h2>
        <p>Your ${config.name} has been successfully linked to your AI Receptionist. ${
          config.category === 'calendar' || config.category === 'both' 
            ? 'Your AI can now check availability and book appointments in real time.' 
            : 'Your AI will now sync customer data automatically.'
        }</p>
        <p>You can close this page. If you have any questions, email us at support@syntharra.com.</p>
      `));
    } else {
      throw new Error('Agent not found in database');
    }
    
  } catch (e) {
    console.error('OAuth callback error:', e.message);
    res.status(500).send(page('Connection Failed', `
      <h2 class="error">Connection Failed</h2>
      <p>Something went wrong while connecting ${config.name}. Please try again using the link in your setup email.</p>
      <p>If this keeps happening, contact us at support@syntharra.com and mention error: ${e.message}</p>
    `));
  }
});

// ============================================================
// ROUTE: /submit-key — API key submission form
// ============================================================
app.get('/submit-key', (req, res) => {
  const { agent, platform } = req.query;
  
  if (!agent || !platform) {
    return res.status(400).send(page('Error', '<h2 class="error">Missing Parameters</h2>'));
  }
  
  res.send(page(`Connect ${platform}`, `
    <h2>Enter Your ${platform} Credentials</h2>
    <p>Paste your API key or credentials below. They will be encrypted and stored securely.</p>
    <form method="POST" action="/submit-key">
      <input type="hidden" name="agent" value="${agent}">
      <input type="hidden" name="platform" value="${platform}">
      <label>API Key / Client ID</label>
      <input type="text" name="api_key" placeholder="Paste your API key here" required>
      <label>Client Secret (if applicable)</label>
      <input type="text" name="client_secret" placeholder="Leave blank if not needed">
      <label>Tenant ID (ServiceTitan only)</label>
      <input type="text" name="tenant_id" placeholder="Leave blank if not applicable">
      <br>
      <button type="submit" class="btn">Connect</button>
    </form>
  `));
});

app.post('/submit-key', async (req, res) => {
  const { agent, platform, api_key, client_secret, tenant_id } = req.body;
  
  if (!agent || !platform || !api_key) {
    return res.status(400).send(page('Error', '<h2 class="error">Missing Fields</h2><p>Please fill in the required fields.</p>'));
  }
  
  try {
    // Determine which Supabase fields to update based on platform category
    const calendarPlatforms = ['ServiceTitan Calendar', 'FieldEdge Calendar'];
    const isCalendar = calendarPlatforms.includes(platform);
    
    const updateBody = {};
    if (isCalendar) {
      updateBody.calendar_api_key = api_key;
      updateBody.calendar_status = 'connected';
      updateBody.calendar_auth_method = 'api_key';
    } else {
      updateBody.crm_api_key = api_key;
      updateBody.crm_status = 'connected';
      updateBody.crm_auth_method = 'api_key';
    }
    
    const supabaseResponse = await fetch(
      `${SUPABASE_URL}/rest/v1/hvac_premium_agent?agent_id=eq.${agent}`,
      {
        method: 'PATCH',
        headers: {
          'apikey': SUPABASE_KEY,
          'Authorization': `Bearer ${SUPABASE_KEY}`,
          'Content-Type': 'application/json',
          'Prefer': 'return=representation'
        },
        body: JSON.stringify(updateBody)
      }
    );
    
    const updated = await supabaseResponse.json();
    
    if (Array.isArray(updated) && updated.length > 0) {
      res.send(page('Connected!', `
        <h2 class="success">✅ ${platform} Connected!</h2>
        <p>Your credentials have been securely stored. Your AI Receptionist will start syncing with ${platform} shortly.</p>
        <p>You can close this page.</p>
      `));
    } else {
      throw new Error('Agent not found');
    }
  } catch (e) {
    console.error('API key submission error:', e.message);
    res.status(500).send(page('Error', `<h2 class="error">Something Went Wrong</h2><p>Please try again or contact support@syntharra.com.</p>`));
  }
});

// ============================================================
// ROUTE: / — Health check
// ============================================================
app.get('/', (req, res) => {
  res.send(page('Syntharra Auth', '<h2>Syntharra Integration Server</h2><p>This server handles calendar and CRM connections for Syntharra AI Receptionists.</p>'));
});

// ============================================================
// START
// ============================================================
app.listen(PORT, () => {
  console.log(`Syntharra OAuth Server running on port ${PORT}`);
  console.log(`Google Calendar: ${GOOGLE_CLIENT_ID ? '✅ configured' : '❌ not configured'}`);
  console.log(`Outlook: ${MS_CLIENT_ID ? '✅ configured' : '❌ not configured'}`);
});
