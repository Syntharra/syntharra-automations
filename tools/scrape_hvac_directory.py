#!/usr/bin/env python3
"""
scrape_hvac_directory.py — Phase 0 cold lead sourcing engine.

Scrapes US HVAC contractor businesses by city using either:

  PRIMARY:  OpenStreetMap Overpass API (free, no key, ethical, public data)
  FALLBACK: Yelp Fusion API (free 5K calls/day, needs YELP_FUSION_API_KEY)

Outputs a CSV with columns:
  name, phone, address, city, state, website, source, source_id, lat, lon

Usage:
  source .env.local
  python tools/scrape_hvac_directory.py --city "Austin" --state "TX" --out leads/hvac-austin-tx.csv
  python tools/scrape_hvac_directory.py --city "Phoenix" --state "AZ" --out leads/hvac-phoenix-az.csv --source yelp

Recommended target cities (ranked by HVAC after-hours emergency density,
which is the strongest predictor of pilot conversion):
  Florida:    Miami, Tampa, Orlando, Jacksonville, Fort Myers, Sarasota
  Texas:      Houston, Austin, Dallas, San Antonio, Fort Worth
  Arizona:    Phoenix, Tucson, Mesa
  Nevada:     Las Vegas
  California: Fresno, Bakersfield, Riverside, Sacramento (inland/Central Valley
              not coastal — coastal CA has milder HVAC demand)
  Georgia:    Atlanta, Savannah
  Alabama:    Birmingham
  Louisiana:  New Orleans, Baton Rouge

Cost: $0 with OSM. With Yelp Fusion: free up to 5K calls/day (each city
search is 1 call returning up to 50 businesses; need pagination for more).

This tool DOES NOT send any email. It only builds the lead list. Pair with
tools/find_email_from_website.py to enrich with email addresses, then
tools/build_cold_outreach.py to generate personalized copy.
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from typing import Iterable

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# City center → (lat, lon, radius_km). Used to build a tight Overpass bbox so
# the API doesn't 504 on huge state queries. Top Phase 0 target cities.
US_CITY_CENTERS: dict[str, tuple[float, float, float]] = {
    # (lat, lon, radius_km)
    "miami,fl":        (25.7617, -80.1918, 35),
    "tampa,fl":        (27.9506, -82.4572, 35),
    "orlando,fl":      (28.5383, -81.3792, 35),
    "jacksonville,fl": (30.3322, -81.6557, 40),
    "fort myers,fl":   (26.6406, -81.8723, 30),
    "sarasota,fl":     (27.3364, -82.5307, 25),
    "houston,tx":      (29.7604, -95.3698, 50),
    "austin,tx":       (30.2672, -97.7431, 35),
    "dallas,tx":       (32.7767, -96.7970, 45),
    "san antonio,tx":  (29.4241, -98.4936, 40),
    "fort worth,tx":   (32.7555, -97.3308, 35),
    "phoenix,az":      (33.4484, -112.0740, 50),
    "tucson,az":       (32.2226, -110.9747, 30),
    "mesa,az":         (33.4152, -111.8315, 25),
    "las vegas,nv":    (36.1699, -115.1398, 35),
    "fresno,ca":       (36.7378, -119.7871, 30),
    "bakersfield,ca":  (35.3733, -119.0187, 30),
    "riverside,ca":    (33.9533, -117.3962, 30),
    "sacramento,ca":   (38.5816, -121.4944, 35),
    "atlanta,ga":      (33.7490, -84.3880, 40),
    "savannah,ga":     (32.0809, -81.0912, 25),
    "birmingham,al":   (33.5186, -86.8104, 30),
    "new orleans,la":  (29.9511, -90.0715, 30),
    "baton rouge,la":  (30.4515, -91.1871, 30),
    "charlotte,nc":    (35.2271, -80.8431, 35),
    "raleigh,nc":      (35.7796, -78.6382, 30),
    "memphis,tn":      (35.1495, -90.0490, 30),
    "nashville,tn":    (36.1627, -86.7816, 35),
    "oklahoma city,ok": (35.4676, -97.5164, 35),
    "albuquerque,nm":  (35.0844, -106.6504, 30),
}


def city_bbox(city: str, state: str) -> tuple[float, float, float, float]:
    """Return (south, west, north, east) bbox for a city via lookup table.
    Approximation: 1 degree latitude ≈ 111 km, 1 degree longitude ≈ 111 * cos(lat) km."""
    import math
    key = f"{city.strip().lower()},{state.strip().lower()}"
    center = US_CITY_CENTERS.get(key)
    if not center:
        sys.exit(f"unknown city {key!r} — add to US_CITY_CENTERS or use --source yelp")
    lat, lon, radius_km = center
    dlat = radius_km / 111.0
    dlon = radius_km / (111.0 * max(0.1, math.cos(math.radians(lat))))
    return (lat - dlat, lon - dlon, lat + dlat, lon + dlon)


# ---------- OpenStreetMap Overpass (no key, primary) ---------------------- #

OSM_OVERPASS_MIRRORS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
]


def nominatim_search(city: str, state: str) -> list[dict]:
    """Fallback: search Nominatim for 'hvac' in a city. Faster but lower
    coverage than Overpass tag-based queries."""
    rows = []
    queries = [
        f"hvac {city} {state}",
        f"heating air conditioning {city} {state}",
        f"hvac contractor {city} {state}",
    ]
    seen_ids = set()
    for q in queries:
        url = (
            "https://nominatim.openstreetmap.org/search?"
            + urllib.parse.urlencode({
                "q": q,
                "format": "json",
                "limit": 50,
                "countrycodes": "us",
                "addressdetails": 1,
                "extratags": 1,
            })
        )
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "SyntharraOutreach/1.0 (daniel@syntharra.com)",
            })
            with urllib.request.urlopen(req, timeout=20) as resp:
                results = json.loads(resp.read().decode())
        except Exception as e:
            print(f"  [warn] nominatim {q!r}: {e}", file=sys.stderr)
            time.sleep(1)
            continue
        for r in results:
            osm_id = f"{r.get('osm_type')}/{r.get('osm_id')}"
            if osm_id in seen_ids:
                continue
            seen_ids.add(osm_id)
            tags = r.get("extratags") or {}
            addr = r.get("address") or {}
            rows.append({
                "name": r.get("display_name", "").split(",")[0].strip() or tags.get("name", ""),
                "phone": tags.get("phone") or tags.get("contact:phone") or "",
                "address": " ".join(filter(None, [
                    addr.get("house_number"),
                    addr.get("road"),
                ])),
                "city": addr.get("city") or addr.get("town") or city,
                "state": addr.get("state") or state.upper(),
                "website": tags.get("website") or tags.get("contact:website") or "",
                "source": "nominatim",
                "source_id": osm_id,
                "lat": float(r["lat"]) if r.get("lat") else None,
                "lon": float(r["lon"]) if r.get("lon") else None,
            })
        time.sleep(1.1)  # Nominatim asks for max 1 req/sec
    return rows


def osm_query(state: str, city: str, timeout: int = 45) -> list[dict]:
    """Query OSM Overpass for HVAC-related businesses in a given city/state.

    Uses a city-radius bbox (not the entire state) and tries multiple mirrors
    so a single overloaded endpoint doesn't kill the run. Falls back to
    Nominatim search if all Overpass mirrors return 504/timeouts.
    """
    south, west, north, east = city_bbox(city, state)
    # Overpass QL query targeting HVAC tags. Coverage in the US is partial but
    # the businesses that ARE tagged are owner-operator independent shops —
    # exactly the persona we want.
    query = f"""
[out:json][timeout:{timeout}];
(
  node["shop"="hvac"]({south},{west},{north},{east});
  way["shop"="hvac"]({south},{west},{north},{east});
  node["craft"="hvac"]({south},{west},{north},{east});
  way["craft"="hvac"]({south},{west},{north},{east});
  node["shop"="heating"]({south},{west},{north},{east});
  way["shop"="heating"]({south},{west},{north},{east});
  node["craft"="heating_engineer"]({south},{west},{north},{east});
  node["amenity"="air_conditioning"]({south},{west},{north},{east});
);
out center tags;
"""
    data = urllib.parse.urlencode({"data": query}).encode()
    payload = None
    for mirror in OSM_OVERPASS_MIRRORS:
        try:
            req = urllib.request.Request(mirror, data=data, method="POST", headers={
                "User-Agent": "SyntharraOutreach/1.0 (daniel@syntharra.com)",
            })
            with urllib.request.urlopen(req, timeout=timeout + 10) as resp:
                payload = json.loads(resp.read().decode())
                print(f"  [overpass] {mirror} OK", file=sys.stderr)
                break
        except urllib.error.HTTPError as e:
            print(f"  [overpass] {mirror} HTTP {e.code}", file=sys.stderr)
            continue
        except Exception as e:
            print(f"  [overpass] {mirror} {type(e).__name__}", file=sys.stderr)
            continue
    if payload is None:
        print("  [overpass] all mirrors failed — falling back to nominatim", file=sys.stderr)
        return nominatim_search(city, state)

    elements = payload.get("elements") or []
    rows = []
    for el in elements:
        tags = el.get("tags") or {}
        name = tags.get("name") or tags.get("operator")
        if not name:
            continue
        # Filter to the target city if the address tag is present
        addr_city = (tags.get("addr:city") or "").lower()
        if city and addr_city and city.lower() not in addr_city:
            continue
        center = el.get("center") or {}
        lat = el.get("lat") or center.get("lat")
        lon = el.get("lon") or center.get("lon")
        rows.append({
            "name": name,
            "phone": tags.get("phone") or tags.get("contact:phone") or "",
            "address": " ".join(filter(None, [
                tags.get("addr:housenumber"),
                tags.get("addr:street"),
            ])),
            "city": tags.get("addr:city") or city,
            "state": tags.get("addr:state") or state.upper(),
            "website": tags.get("website") or tags.get("contact:website") or "",
            "source": "osm",
            "source_id": f"{el.get('type')}/{el.get('id')}",
            "lat": lat,
            "lon": lon,
        })
    return rows


# ---------- Yelp Fusion (key, fallback) ----------------------------------- #

def yelp_query(state: str, city: str, limit: int = 50, max_pages: int = 4) -> list[dict]:
    """Query Yelp Fusion for HVAC contractors in a city. Paginates up to
    max_pages * limit results."""
    api_key = os.environ.get("YELP_FUSION_API_KEY")
    if not api_key:
        sys.exit(
            "YELP_FUSION_API_KEY not in env. Either source .env.local with the "
            "key or use --source osm (no key required)."
        )
    headers = {"Authorization": f"Bearer {api_key}"}
    rows = []
    for page in range(max_pages):
        offset = page * limit
        params = urllib.parse.urlencode({
            "term": "HVAC contractor",
            "location": f"{city}, {state}",
            "categories": "hvac",
            "limit": limit,
            "offset": offset,
            "country": "US",
        })
        url = f"https://api.yelp.com/v3/businesses/search?{params}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            sys.exit(f"Yelp HTTP {e.code}: {e.read().decode()[:300]}")
        businesses = payload.get("businesses") or []
        if not businesses:
            break
        for b in businesses:
            loc = b.get("location") or {}
            coords = b.get("coordinates") or {}
            rows.append({
                "name": b.get("name", ""),
                "phone": b.get("phone", ""),
                "address": " ".join(loc.get("display_address") or []),
                "city": loc.get("city", city),
                "state": loc.get("state", state.upper()),
                "website": b.get("url", ""),  # Yelp page; real website needs scrape
                "source": "yelp",
                "source_id": b.get("id", ""),
                "lat": coords.get("latitude"),
                "lon": coords.get("longitude"),
            })
        time.sleep(0.25)  # rate-limit politeness
    return rows


# ---------- main ---------------------------------------------------------- #

def write_csv(rows: Iterable[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fieldnames = [
        "name", "phone", "address", "city", "state", "website",
        "source", "source_id", "lat", "lon",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True, help="City name (e.g. 'Austin')")
    ap.add_argument("--state", required=True, help="2-letter state code (e.g. 'TX')")
    ap.add_argument("--source", choices=["osm", "yelp", "auto"], default="auto",
                    help="Data source. 'auto' = yelp if YELP_FUSION_API_KEY set, else osm.")
    ap.add_argument("--out", required=True, help="Output CSV path")
    args = ap.parse_args()

    source = args.source
    if source == "auto":
        source = "yelp" if os.environ.get("YELP_FUSION_API_KEY") else "osm"
    print(f"[scrape] source={source} city={args.city!r} state={args.state!r}", file=sys.stderr)

    if source == "osm":
        rows = osm_query(args.state, args.city)
    elif source == "yelp":
        rows = yelp_query(args.state, args.city)
    else:
        sys.exit(f"unknown source: {source}")

    print(f"[scrape] {len(rows)} businesses found", file=sys.stderr)
    if rows:
        # Dedupe by name+phone
        seen = set()
        deduped = []
        for r in rows:
            key = (r["name"].lower().strip(), (r["phone"] or "").strip())
            if key in seen:
                continue
            seen.add(key)
            deduped.append(r)
        print(f"[scrape] {len(deduped)} after dedupe", file=sys.stderr)
        write_csv(deduped, args.out)
        print(f"[scrape] wrote {args.out}", file=sys.stderr)
    else:
        print("[scrape] no rows — try a different source/city", file=sys.stderr)


if __name__ == "__main__":
    main()
