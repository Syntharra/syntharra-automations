# Syntharra OAuth Platform Setup Guide
## Complete Registration Instructions for All Integrations

For every platform below, the end result is the same: you get a **Client ID** and **Client Secret**, then add them as environment variables in Railway (OAuth Server → Variables). Railway auto-redeploys after each change.

Railway OAuth Server Variables page: Go to railway.app → your OAuth Server project → click the service → Variables tab.

**Redirect URI for ALL platforms:** `https://auth.syntharra.com/callback`

---

## 1. GOOGLE CALENDAR ✅ DONE

Railway env vars: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`

Already configured and tested. Tokens saving to Supabase confirmed.

---

## 2. MICROSOFT OUTLOOK (Azure)

Railway env vars: `MS_CLIENT_ID`, `MS_CLIENT_SECRET`

**What it is:** Microsoft uses Azure Active Directory (now called "Microsoft Entra ID") to manage all OAuth apps. You register an app there, and it lets Syntharra clients sign in with their Microsoft/Outlook/Office 365 account to grant calendar access.

### Steps:

1. Go to **portal.azure.com**
2. Sign in with any Microsoft account (create a free one if needed)
3. In the search bar at the top, type **"App registrations"** and click it
4. Click **"+ New registration"**
5. Fill in:
   - Name: `Syntharra AI`
   - Supported account types: Select **"Accounts in any organizational directory and personal Microsoft accounts"** (the third option — this covers both business and personal Outlook)
   - Redirect URI: Platform = **Web**, URI = `https://auth.syntharra.com/callback`
6. Click **Register**
7. On the overview page, copy the **"Application (client) ID"** — this is your `MS_CLIENT_ID`
8. In the left sidebar, click **"Certificates & secrets"**
9. Click **"+ New client secret"**
   - Description: `Syntharra OAuth`
   - Expires: 24 months
10. Click **Add** — immediately copy the **Value** (not the Secret ID). This is your `MS_CLIENT_SECRET`. You can only see it once.
11. In the left sidebar, click **"API permissions"**
12. Click **"+ Add a permission"**
13. Choose **"Microsoft Graph"**
14. Choose **"Delegated permissions"**
15. Search and check these permissions:
    - `Calendars.ReadWrite`
    - `offline_access`
    - `User.Read`
16. Click **"Add permissions"**
17. Add both values to Railway:
    - `MS_CLIENT_ID` = the Application (client) ID from step 7
    - `MS_CLIENT_SECRET` = the secret Value from step 10

**Test:** Visit `https://auth.syntharra.com/connect?platform=outlook&agent=agent_demo_dashboard_001`

---

## 3. CALENDLY

Railway env vars: `CALENDLY_CLIENT_ID`, `CALENDLY_CLIENT_SECRET`

### Steps:

1. Go to **developer.calendly.com**
2. Sign in with your Calendly account (create free one if needed)
3. Click **"My Apps"** in the top nav
4. Click **"Create new app"**
5. Fill in:
   - App name: `Syntharra AI`
   - Kind of app: **"Web application"**
   - Redirect URI: `https://auth.syntharra.com/callback`
   - Description: `AI Receptionist calendar integration for trade businesses`
6. Click **Create**
7. Copy the **Client ID** and **Client Secret** shown
8. Add to Railway:
   - `CALENDLY_CLIENT_ID` = Client ID
   - `CALENDLY_CLIENT_SECRET` = Client Secret

**Test:** `https://auth.syntharra.com/connect?platform=calendly&agent=agent_demo_dashboard_001`

---

## 4. JOBBER

Railway env vars: `JOBBER_CLIENT_ID`, `JOBBER_CLIENT_SECRET`

**What it is:** Jobber is the most popular CRM for trade businesses (HVAC, plumbing, electrical). Their API lets us read/write jobs, clients, and calendar entries.

### Steps:

1. Go to **developer.getjobber.com**
2. Click **"Get Started"** or **"Sign Up"**
3. Create a developer account (separate from a regular Jobber account)
4. Once in the developer portal, click **"Create App"**
5. Fill in:
   - App name: `Syntharra AI`
   - App description: `AI Receptionist that books jobs and syncs customer data for trade businesses`
   - Redirect URI: `https://auth.syntharra.com/callback`
   - App type: **"Web application"**
   - Scopes: Select **read and write** for: Jobs, Clients, Calendar, Requests
6. Submit for review (Jobber reviews apps before granting production access — this may take a few days)
7. Once approved, copy the **Client ID** and **Client Secret**
8. Add to Railway:
   - `JOBBER_CLIENT_ID` = Client ID
   - `JOBBER_CLIENT_SECRET` = Client Secret

**Note:** Jobber may require a review period. You can start developing with sandbox credentials immediately, but production access requires approval. Explain that Syntharra is an AI receptionist platform that automates call handling and job booking for Jobber users.

**Test:** `https://auth.syntharra.com/connect?platform=jobber&agent=agent_demo_dashboard_001`

---

## 5. HOUSECALL PRO

Railway env vars: `HCP_CLIENT_ID`, `HCP_CLIENT_SECRET`

**What it is:** Another major CRM for home service businesses. Similar to Jobber but popular in the US market.

### Steps:

1. Go to **developer.housecallpro.com**
2. Sign up for a developer account
3. Create a new app:
   - App name: `Syntharra AI`
   - Description: `AI Receptionist platform for home service businesses`
   - Redirect URI: `https://auth.syntharra.com/callback`
   - Requested scopes: Jobs (read/write), Customers (read/write), Schedule (read/write)
4. Copy the **Client ID** and **Client Secret**
5. Add to Railway:
   - `HCP_CLIENT_ID` = Client ID
   - `HCP_CLIENT_SECRET` = Client Secret

**Note:** Housecall Pro also has an app review process. Apply early.

**Test:** `https://auth.syntharra.com/connect?platform=housecallpro&agent=agent_demo_dashboard_001`

---

## 6. HUBSPOT

Railway env vars: `HUBSPOT_CLIENT_ID`, `HUBSPOT_CLIENT_SECRET`

**What it is:** Major CRM used by some larger trade businesses and multi-location companies.

### Steps:

1. Go to **developers.hubspot.com**
2. Click **"Create a developer account"** (free)
3. Once in, go to **"Apps"** in the top nav
4. Click **"Create app"**
5. Fill in the **App Info** tab:
   - Public app name: `Syntharra AI`
   - Description: `AI Receptionist that captures leads and syncs with HubSpot CRM`
   - Logo: Upload Syntharra logo
   - Support email: `support@syntharra.com`
6. Go to the **Auth** tab:
   - Redirect URL: `https://auth.syntharra.com/callback`
   - Scopes: Add these:
     - `crm.objects.contacts.write`
     - `crm.objects.contacts.read`
     - `crm.objects.deals.write`
     - `crm.objects.deals.read`
7. Click **"Create app"**
8. On the app page, go to **Auth** tab — copy:
   - **Client ID**
   - **Client Secret** (click "Show")
9. Add to Railway:
   - `HUBSPOT_CLIENT_ID` = Client ID
   - `HUBSPOT_CLIENT_SECRET` = Client Secret

**Test:** `https://auth.syntharra.com/connect?platform=hubspot&agent=agent_demo_dashboard_001`

---

## 7. GOHIGHLEVEL

Railway env vars: `GHL_CLIENT_ID`, `GHL_CLIENT_SECRET`

**What it is:** All-in-one marketing and CRM platform popular with agencies and some trade businesses.

### Steps:

1. Go to **marketplace.gohighlevel.com**
2. Sign in with your GoHighLevel account
3. Click **"My Apps"** → **"Create App"**
4. Fill in:
   - App name: `Syntharra AI`
   - Description: `AI Receptionist for trade businesses`
   - Type: **"Web application"**
   - Redirect URI: `https://auth.syntharra.com/callback`
   - Scopes: Select:
     - `contacts.write`
     - `contacts.readonly`
     - `calendars.write`
     - `calendars.readonly`
     - `opportunities.write`
5. Submit the app
6. Once approved, copy **Client ID** and **Client Secret**
7. Add to Railway:
   - `GHL_CLIENT_ID` = Client ID
   - `GHL_CLIENT_SECRET` = Client Secret

**Note:** GoHighLevel requires a paid account to access their developer marketplace.

**Test:** `https://auth.syntharra.com/connect?platform=gohighlevel&agent=agent_demo_dashboard_001`

---

## QUICK REFERENCE — All Railway Environment Variables

After completing all platforms, your Railway OAuth Server should have these variables:

| Variable | Platform | Status |
|----------|----------|--------|
| `SUPABASE_URL` | Supabase | ✅ Set |
| `SUPABASE_KEY` | Supabase | ✅ Set |
| `GOOGLE_CLIENT_ID` | Google Calendar | ✅ Done |
| `GOOGLE_CLIENT_SECRET` | Google Calendar | ✅ Done |
| `GOOGLE_REDIRECT_URI` | All platforms | Set to `https://auth.syntharra.com/callback` |
| `MS_CLIENT_ID` | Microsoft Outlook | To do |
| `MS_CLIENT_SECRET` | Microsoft Outlook | To do |
| `MS_REDIRECT_URI` | Microsoft Outlook | Set to `https://auth.syntharra.com/callback` |
| `CALENDLY_CLIENT_ID` | Calendly | To do |
| `CALENDLY_CLIENT_SECRET` | Calendly | To do |
| `JOBBER_CLIENT_ID` | Jobber | To do |
| `JOBBER_CLIENT_SECRET` | Jobber | To do |
| `HCP_CLIENT_ID` | Housecall Pro | To do |
| `HCP_CLIENT_SECRET` | Housecall Pro | To do |
| `HUBSPOT_CLIENT_ID` | HubSpot | To do |
| `HUBSPOT_CLIENT_SECRET` | HubSpot | To do |
| `GHL_CLIENT_ID` | GoHighLevel | To do |
| `GHL_CLIENT_SECRET` | GoHighLevel | To do |

## PLATFORMS THAT DON'T NEED OAUTH (API Key based)

These are already working via the `/submit-key` endpoint. No setup needed from you — clients enter their own credentials:

- **ServiceTitan** — client enters API key + tenant ID
- **FieldEdge** — client enters API key
- **Kickserv** — client enters API key
- **Workiz** — client enters API key

## TEST EACH PLATFORM

After adding credentials for each platform, test with:

```
https://auth.syntharra.com/connect?platform=[PLATFORM_NAME]&agent=agent_demo_dashboard_001
```

Platform names: `google_calendar`, `outlook`, `calendly`, `jobber`, `housecallpro`, `hubspot`, `gohighlevel`

You should see the platform's login screen. After signing in, you should see the green "Connected!" success page and the tokens should appear in the Supabase `hvac_premium_agent` table.
