# Syntharra Sales Materials

## Sales Pitch Document
Generate the sales pitch DOCX:
```bash
npm install -g docx
node generate-sales-pitch.js
```
Output: `syntharra-sales-pitch.docx`

## Contents
- Company overview and problem statement
- Feature list with descriptions (13 features)
- How the automated onboarding works
- Pricing table (Standard $497/mo, Premium $997/mo)
- ROI comparison (with vs without Syntharra)
- Contact information

## Client Dashboard
The client-facing call log dashboard is at `shared/client-dashboard.jsx`.
Access via: `https://syntharra.com/dashboard?agent_id=<client_agent_id>`

Features:
- Real-time call log from Supabase
- Lead scoring badges (hot/warm/standard)
- Emergency and missed transfer highlighting
- Expandable call details with summaries and notes
- Address geocode links to Google Maps
- Date range filtering (7d/14d/30d)
- Stat cards (total calls, leads, avg score, emergencies)
