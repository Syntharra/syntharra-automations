# Google Cloud OAuth Setup — Syntharra

## Step 1: Create Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click **Select a project** → **New Project**
3. Name: `Syntharra OAuth`
4. Click **Create**

## Step 2: Enable Google Calendar API

1. In the left sidebar: **APIs & Services** → **Library**
2. Search for **Google Calendar API**
3. Click **Enable**

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** user type → **Create**
3. Fill in:
   - App name: `Syntharra AI`
   - User support email: `support@syntharra.com`
   - App logo: Upload Syntharra logo
   - Developer contact: `daniel@syntharra.com`
4. Click **Save and Continue**
5. **Scopes** → Add scope: `https://www.googleapis.com/auth/calendar`
6. Click **Save and Continue**
7. **Test users** → Add: `daniel@syntharra.com` (for testing)
8. Click **Save and Continue**

> **Note:** While in "Testing" status, only test users can connect. To allow any Google user, you'll need to submit for Google verification (takes 2-6 weeks). You can onboard clients during testing by adding their email as a test user first.

## Step 4: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth client ID**
3. Application type: **Web application**
4. Name: `Syntharra OAuth Server`
5. **Authorized redirect URIs** → Add:
   - `https://auth.syntharra.com/callback`
6. Click **Create**
7. Copy the **Client ID** and **Client Secret**

## Step 5: Add to Railway Environment Variables

1. Go to [Railway Dashboard](https://railway.app) → Syntharra OAuth Server project
2. Click on the service → **Variables**
3. Add these two variables:
   - `GOOGLE_CLIENT_ID` = *(paste client ID)*
   - `GOOGLE_CLIENT_SECRET` = *(paste client secret)*
4. Railway will auto-redeploy

## Step 6: Test the Flow

1. Visit: `https://auth.syntharra.com/connect?platform=google_calendar&agent=agent_4afbfdb3fcb1ba9569353af28d`
2. You should see Google's consent screen
3. Authorize → should redirect back to success page
4. Check Supabase `hvac_premium_agent` table to confirm tokens stored

## Future: Microsoft Outlook (same process)

1. Go to [portal.azure.com](https://portal.azure.com) → Azure Active Directory → App Registrations
2. New Registration → Name: `Syntharra OAuth` → Redirect URI: `https://auth.syntharra.com/callback`
3. Under Certificates & Secrets → New client secret
4. Add to Railway: `MS_CLIENT_ID` and `MS_CLIENT_SECRET`
5. API permissions: `Calendars.ReadWrite`, `offline_access`

## Supported Platforms (OAuth server already coded)

| Platform | Env Vars Needed | Category |
|----------|----------------|----------|
| Google Calendar | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Calendar |
| Microsoft Outlook | `MS_CLIENT_ID`, `MS_CLIENT_SECRET` | Calendar |
| Calendly | `CALENDLY_CLIENT_ID`, `CALENDLY_CLIENT_SECRET` | Calendar |
| Jobber | `JOBBER_CLIENT_ID`, `JOBBER_CLIENT_SECRET` | CRM + Calendar |
| Housecall Pro | `HCP_CLIENT_ID`, `HCP_CLIENT_SECRET` | CRM + Calendar |
| HubSpot | `HUBSPOT_CLIENT_ID`, `HUBSPOT_CLIENT_SECRET` | CRM |
| GoHighLevel | `GHL_CLIENT_ID`, `GHL_CLIENT_SECRET` | CRM |

The OAuth server at `auth.syntharra.com` handles all of these — you just need to create credentials in each platform's developer portal and add the env vars to Railway.

For CRMs that use API keys instead of OAuth (ServiceTitan, FieldEdge), clients use the `/submit-key` endpoint which is already built.
