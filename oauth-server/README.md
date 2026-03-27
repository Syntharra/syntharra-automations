# Syntharra OAuth Server

Handles OAuth connections for calendar/CRM integrations. Deployed at `auth.syntharra.com`.

## Setup

1. Copy `.env.example` to `.env` and fill in credentials
2. Deploy to Railway (same pattern as syntharra-checkout)
3. Set custom domain to `auth.syntharra.com` in Railway

## Endpoints

| Route | Method | Purpose |
|---|---|---|
| `/connect?platform=X&agent=Y` | GET | Starts OAuth flow — redirects to platform consent screen |
| `/callback?code=X&state=Y` | GET | Handles OAuth callback — exchanges code for tokens, stores in Supabase |
| `/submit-key?agent=Y&platform=X` | GET | Shows API key submission form (for non-OAuth platforms) |
| `/submit-key` | POST | Processes API key submission, stores in Supabase |
| `/` | GET | Health check |

## Supported Platforms

**OAuth (one-click):** Google Calendar, Microsoft Outlook, Calendly, Jobber, Housecall Pro, HubSpot, GoHighLevel

**API Key (form):** ServiceTitan, FieldEdge, Kickserv, Workiz

## How It Works

1. Client clicks "Connect" button in setup email
2. Server redirects to platform's OAuth consent screen
3. Client approves access
4. Platform redirects back to `/callback` with authorization code
5. Server exchanges code for access_token + refresh_token
6. Tokens stored in Supabase `hvac_premium_agent` table
7. Integration Dispatcher automatically uses stored tokens on next call

## Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project → Enable Google Calendar API
3. Create OAuth 2.0 credentials (Web application)
4. Add redirect URI: `https://auth.syntharra.com/callback`
5. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in Railway env
