# Lead Sourcing Reference

## Overview

Three-tier approach to building a prospect list of trade businesses.
All leads stored in Supabase `marketing_leads` table.

---

## Supabase Schema

```sql
CREATE TABLE marketing_leads (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  business_name TEXT NOT NULL,
  industry TEXT NOT NULL,                    -- 'hvac', 'plumbing', 'electrical', etc.
  region TEXT NOT NULL,                      -- 'Texas', 'California', 'USA', etc.
  city TEXT,
  state TEXT,
  country TEXT DEFAULT 'USA',
  phone TEXT,
  email TEXT,
  website TEXT,
  address TEXT,
  google_place_id TEXT,
  rating NUMERIC(2,1),
  review_count INTEGER,
  source TEXT,                               -- 'google_places', 'apollo', 'scrape'
  status TEXT DEFAULT 'new',                -- 'new', 'emailed', 'opened', 'clicked', 'booked', 'unsubscribed'
  email_sent_at TIMESTAMPTZ,
  email_opened_at TIMESTAMPTZ,
  video_clicked_at TIMESTAMPTZ,
  demo_booked_at TIMESTAMPTZ,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE email_events (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  lead_id UUID REFERENCES marketing_leads(id),
  event_type TEXT,                          -- 'sent', 'opened', 'clicked', 'replied', 'bounced'
  email_number INTEGER,                     -- 1, 2, or 3
  utm_code TEXT,                            -- unique per lead for click tracking
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE booked_demos (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  lead_id UUID REFERENCES marketing_leads(id),
  booking_time TIMESTAMPTZ,
  cal_event_id TEXT,
  status TEXT DEFAULT 'scheduled',          -- 'scheduled', 'completed', 'no_show', 'cancelled'
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

---

## Method 1: Google Places API (Primary)

### n8n HTTP Request Node — Search

```
POST https://maps.googleapis.com/maps/api/place/textsearch/json
  ?query={{industry}} contractor {{city}} {{state}}
  &type=establishment
  &key={{GOOGLE_PLACES_API_KEY}}
```

### Filter Criteria
- `user_ratings_total` >= 5 (established, not brand new)
- Has `formatted_phone_number`
- NOT a chain/franchise (filter out: "Home Depot", "Lowes", "Sears")

### Fields to Extract
```javascript
{
  business_name: result.name,
  google_place_id: result.place_id,
  address: result.formatted_address,
  phone: result.formatted_phone_number,
  website: result.website,
  rating: result.rating,
  review_count: result.user_ratings_total,
  city: city,
  state: state,
  industry: industry,
  source: 'google_places'
}
```

### City List for USA HVAC (Starting Set)
```javascript
const USA_HVAC_CITIES = [
  { city: "Houston", state: "TX" },
  { city: "Phoenix", state: "AZ" },
  { city: "Dallas", state: "TX" },
  { city: "San Antonio", state: "TX" },
  { city: "Jacksonville", state: "FL" },
  { city: "Austin", state: "TX" },
  { city: "Charlotte", state: "NC" },
  { city: "Fort Worth", state: "TX" },
  { city: "Memphis", state: "TN" },
  { city: "Atlanta", state: "GA" },
  { city: "Oklahoma City", state: "OK" },
  { city: "Tucson", state: "AZ" },
  { city: "Las Vegas", state: "NV" },
  { city: "Miami", state: "FL" },
  { city: "Tampa", state: "FL" }
];
// Hot climate cities = most HVAC businesses = highest pain point
```

---

## Method 2: Email Discovery (Hunter.io / Apollo.io)

After getting business name + domain from Places API:

### Hunter.io Domain Search
```
GET https://api.hunter.io/v2/domain-search
  ?domain={{website_domain}}
  &type=personal
  &api_key={{HUNTER_API_KEY}}
```

Returns first/last name + email of owner/manager.
Best format: `firstname@domain.com` or `owner@domain.com`

### Fallback Email Patterns (try in order)
```
info@{{domain}}
contact@{{domain}}
office@{{domain}}
service@{{domain}}
```

### Email Validation
Always validate before adding to sequence.
Mark `email_valid: false` and skip if bounces on first send.

---

## Method 3: Scrape Fallback (No API Key)

Use n8n HTTP Request + Extract HTML nodes on:

### Yelp
```
GET https://www.yelp.com/search?find_desc={{industry}}&find_loc={{city}}%2C+{{state}}
```
Extract: business name, phone, website, address from listing cards.

### Angi (formerly Angie's List)
```
GET https://www.angi.com/companylist/us/{{state}}/{{city}}/{{industry}}-contractors.htm
```

**Note:** Rate limit — max 1 request per 3 seconds. Rotate user agents.

---

## Deduplication Logic

Before inserting to Supabase, check:
```sql
SELECT id FROM marketing_leads
WHERE (phone = $1 OR (business_name ILIKE $2 AND city = $3))
AND industry = $4
LIMIT 1;
```
If exists → skip. Log as duplicate.

---

## Target Volume

| Phase | Leads | Timeline |
|---|---|---|
| Phase 1 (HVAC USA) | 500 | Week 1 |
| Phase 2 (HVAC USA expanded) | 2,000 | Month 1 |
| Phase 3 (Plumbing USA) | 1,000 | Month 2 |
| Phase 4 (International) | 500/country | Month 3+ |

---

## n8n Workflow Structure for Lead Sourcing

Nodes in order:
1. **Schedule Trigger** — runs nightly at 2am
2. **Set Parameters** — industry, cities array, API keys
3. **Loop Over Cities** — SplitInBatches node
4. **Google Places Search** — HTTP Request per city
5. **Filter Results** — Function node (apply filter criteria)
6. **Check Duplicates** — Supabase SELECT
7. **Hunter.io Email Lookup** — HTTP Request per new lead
8. **Insert to Supabase** — Supabase INSERT
9. **Count + Notify** — sends summary to admin@syntharra.com

API Keys needed (set as n8n credentials or env vars):
- `GOOGLE_PLACES_API_KEY`
- `HUNTER_API_KEY` (optional, fallback to pattern guessing)
