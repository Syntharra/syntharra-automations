#!/usr/bin/env python3
"""
generate_city_pages.py — Generate HVAC answering service city landing pages.

Creates self-contained HTML pages for syntharra-website matching the
hvac-answering-service-{slug}.html pattern established by the Nashville page.

Usage:
  python tools/generate_city_pages.py                    # generate all cities in CITIES list
  python tools/generate_city_pages.py --city "Memphis"   # one city only
  python tools/generate_city_pages.py --dry-run          # print slugs only
  python tools/generate_city_pages.py --skip-existing    # don't overwrite

Output: ../syntharra-website/hvac-answering-service-{slug}.html
"""
from __future__ import annotations
import argparse
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ── City definitions ──────────────────────────────────────────────────────────
# Each entry drives 100% of the page customization. Context must be:
# - Factually defensible (no made-up statistics)
# - HVAC-specific to the local climate or market
CITIES = [
    {
        "slug":       "raleigh",
        "city":       "Raleigh",
        "state":      "NC",
        "area_code":  "919",
        "region_desc": "Raleigh and the Research Triangle",
        "suburbs":    "Cary, Durham, Chapel Hill, and Apex",
        "climate_hook": "Raleigh's hot, humid summers and cold winters drive year-round demand for responsive HVAC service across the Research Triangle.",
        "hero_sub":   "Raleigh's rapid growth and hot, humid Carolina summers mean HVAC contractors compete for every emergency call. When a homeowner's AC fails during a July heat wave in Wake County, the first shop to answer wins. Syntharra is a 24/7 AI receptionist trained on HVAC scripts and Triangle service areas. Flat $697/month, 700 minutes, free 14-day pilot, no credit card.",
        "heat_context": "Raleigh and the Research Triangle",
        "heat_detail":  "Raleigh's summers bring heat and humidity that can push indoor temperatures to dangerous levels within hours of an AC failure. The city's rapid growth also means a highly competitive HVAC market — contractors who answer every call grow faster than those who don't.",
        "story_city":   "Cary",
        "story_time":   "10:45 p.m. on a Thursday in August",
        "story_temp":   "84°F and climbing",
        "story_context": "young children",
        "ac_type":      "Dual-zone system",
        "heat_pump_state": "North Carolina",
        "heat_wave_month": "July",
        "faq": [
            {"q": "Do you support area code 919?", "a": "Yes — Syntharra provisions a local Raleigh-area number in the 919 area code, covering Raleigh and the Research Triangle including Cary, Durham, Chapel Hill, and Apex. You can forward your existing number to the AI or use the AI's number as your main line."},
            {"q": "How fast can I be live in Raleigh?", "a": "24 hours from the time you finish the 5-minute onboarding form. You give us your service areas, your after-hours emergency rate, your truck rolls per day, and your preferred dispatch number — we configure the AI agent and it's answering calls the next morning."},
            {"q": "What if I already have an answering service in Raleigh?", "a": "Run the pilot in parallel. Keep your current answering service on your daytime line and put the Syntharra pilot number as your after-hours forward. After 14 days, compare how many after-hours emergencies the AI caught versus what went to voicemail."},
            {"q": "Does the AI handle dual-zone systems common in Triangle-area homes?", "a": "Yes. The AI is trained on multi-zone HVAC terminology and can classify zone-specific failures — 'upstairs zone not cooling,' 'one zone stuck on heat' — and dispatch them with the right urgency. It doesn't try to diagnose; it captures the symptom accurately so you can."},
            {"q": "How does the AI handle call surges during summer heat waves?", "a": "The AI handles unlimited concurrent calls. When multiple homeowners call simultaneously during a heat wave, all get answered instantly and dispatched to your cell in priority order — emergencies first, then scheduled service, then general inquiries."},
        ],
    },
    {
        "slug":       "birmingham",
        "city":       "Birmingham",
        "state":      "AL",
        "area_code":  "205",
        "region_desc": "Birmingham and the greater Jefferson County area",
        "suburbs":    "Hoover, Vestavia Hills, Homewood, and Pelham",
        "climate_hook": "Birmingham's long, hot Alabama summers and mild winters keep HVAC contractors busy nearly year-round across the metro.",
        "hero_sub":   "Birmingham's deep-south heat makes AC reliability a basic necessity from May through September. When a homeowner calls at midnight because their unit quit during an Alabama summer, that call is worth a service visit — not a voicemail. Syntharra is a 24/7 AI receptionist trained on HVAC scripts and Jefferson County service areas. Flat $697/month, 700 minutes, free 14-day pilot, no credit card.",
        "heat_context": "Birmingham and greater Jefferson County",
        "heat_detail":  "Alabama summers are long and relentless. Birmingham consistently sees heat indices above 100°F through July and August, and older housing stock in the region puts more strain on aging HVAC systems. After-hours emergency calls are a predictable, recurring revenue opportunity for contractors who answer them.",
        "story_city":   "Hoover",
        "story_time":   "11:15 p.m. on a Wednesday in July",
        "story_temp":   "83°F indoors",
        "story_context": "elderly parents staying over",
        "ac_type":      "Central AC",
        "heat_pump_state": "Alabama",
        "heat_wave_month": "July",
        "faq": [
            {"q": "Do you support area code 205?", "a": "Yes — Syntharra provisions a local Birmingham-area number in the 205 area code, covering Birmingham and the greater Jefferson County area including Hoover, Vestavia Hills, Homewood, and Pelham."},
            {"q": "How fast can I be live in Birmingham?", "a": "24 hours from the time you finish the 5-minute onboarding form. You give us your service areas, your after-hours emergency rate, your truck rolls per day, and your preferred dispatch number."},
            {"q": "What if I already have an answering service?", "a": "Run the pilot in parallel for 14 days. Put Syntharra as your after-hours forward, keep your current service on daytime. After two weeks, compare call capture rates and decide."},
            {"q": "Does the AI understand older HVAC systems common in Birmingham?", "a": "Yes. The AI is trained on general HVAC terminology that covers older equipment — Freon-based systems, older Trane and Carrier units, window units — and can capture symptom descriptions accurately regardless of equipment age."},
            {"q": "How does the AI handle Alabama summer call spikes?", "a": "The AI handles unlimited concurrent calls. When multiple homeowners call simultaneously during an Alabama heat wave, all get answered instantly and dispatched in priority order — emergencies first, then scheduled service, then general inquiries."},
        ],
    },
    {
        "slug":       "new-orleans",
        "city":       "New Orleans",
        "state":      "LA",
        "area_code":  "504",
        "region_desc": "New Orleans and the greater Greater New Orleans area",
        "suburbs":    "Metairie, Kenner, Slidell, and Gretna",
        "climate_hook": "New Orleans' extreme heat and humidity make HVAC failures genuine emergencies — owners cannot afford to miss a single call.",
        "hero_sub":   "New Orleans has some of the most demanding HVAC conditions in the country. High heat combined with near-tropical humidity means an AC failure isn't just uncomfortable — it can be dangerous within hours. Syntharra is a 24/7 AI receptionist trained on HVAC scripts and Greater New Orleans service areas. Flat $697/month, 700 minutes, free 14-day pilot, no credit card.",
        "heat_context": "New Orleans and Greater New Orleans",
        "heat_detail":  "New Orleans heat and humidity is a combination found in few other US markets. The City consistently logs some of the highest heat indices in the country, and with high humidity, a home without AC can reach dangerous conditions quickly. HVAC contractors in the area deal with after-hours emergency calls at a higher frequency than most US markets.",
        "story_city":   "Metairie",
        "story_time":   "1:00 a.m. on a Saturday in August",
        "story_temp":   "86°F and 90% humidity",
        "story_context": "a newborn at home",
        "ac_type":      "Split AC system",
        "heat_pump_state": "Louisiana",
        "heat_wave_month": "August",
        "faq": [
            {"q": "Do you support area code 504?", "a": "Yes — Syntharra provisions a local New Orleans-area number in the 504 area code, covering New Orleans and the greater metro including Metairie, Kenner, Slidell, and Gretna."},
            {"q": "How fast can I be live in New Orleans?", "a": "24 hours from the time you finish the 5-minute onboarding form. You give us your service areas, your after-hours emergency rate, your truck rolls per day, and your preferred dispatch number."},
            {"q": "Does the AI understand high-humidity HVAC issues common in Louisiana?", "a": "Yes. The AI is trained on humidity-related HVAC terminology — 'feels damp,' 'dripping inside,' 'coils freezing,' 'dehumidifier mode' — and can classify humidity-related failures alongside temperature failures accurately."},
            {"q": "What if my customers speak Cajun or have strong Louisiana accents?", "a": "The AI uses advanced speech recognition that handles regional accents and non-standard pronunciations well. It captures contact details and symptoms accurately across a wide range of accents — this has been tested extensively across the US South."},
            {"q": "How does the AI handle New Orleans summer call surges?", "a": "The AI handles unlimited concurrent calls. During peak heat, when multiple homeowners call simultaneously, all get answered instantly and dispatched in priority order — no busy signal, no voicemail."},
        ],
    },
    {
        "slug":       "fort-worth",
        "city":       "Fort Worth",
        "state":      "TX",
        "area_code":  "817",
        "region_desc": "Fort Worth and Tarrant County",
        "suburbs":    "Arlington, Hurst, Euless, and Bedford",
        "climate_hook": "Fort Worth's scorching Texas summers and cold winter snaps mean HVAC is a year-round business across Tarrant County.",
        "hero_sub":   "Fort Worth HVAC contractors deal with Texas extremes at both ends — blistering summer heat and sudden winter cold snaps that drive emergency calls around the clock. When homeowners call after hours, whoever answers first wins. Syntharra is a 24/7 AI receptionist trained on HVAC scripts and Tarrant County service areas. Flat $697/month, 700 minutes, free 14-day pilot, no credit card.",
        "heat_context": "Fort Worth and Tarrant County",
        "heat_detail":  "Fort Worth experiences Texas heat at full intensity — sustained temperatures above 100°F are common in July and August, and the city's flat terrain means there's little natural shelter. The DFW metroplex spans millions of homes across Tarrant and neighboring counties, giving HVAC contractors a large service territory with high call volume during weather extremes.",
        "story_city":   "Arlington",
        "story_time":   "10:30 p.m. on a Sunday in July",
        "story_temp":   "over 100°F outside and climbing inside",
        "story_context": "pets in the house",
        "ac_type":      "2-ton system",
        "heat_pump_state": "Texas",
        "heat_wave_month": "July",
        "faq": [
            {"q": "Do you support area code 817?", "a": "Yes — Syntharra provisions a local Fort Worth-area number in the 817 area code, covering Fort Worth and Tarrant County including Arlington, Hurst, Euless, and Bedford."},
            {"q": "How fast can I be live in Fort Worth?", "a": "24 hours from the time you finish the 5-minute onboarding form. You give us your service areas, after-hours rate, truck rolls per day, and dispatch number."},
            {"q": "We're near Dallas — will the AI understand DFW service area boundaries?", "a": "Yes. The AI captures the customer's address and ZIP code accurately during the call and includes it in the SMS dispatch to you. You decide in real time whether the address falls within your territory — the AI doesn't make that call for you."},
            {"q": "What about the freeze events Texas has experienced?", "a": "Yes. The AI handles winter emergency calls — 'heat not working,' 'pipes near the furnace,' 'unit frozen up' — with the same urgency classification it uses for summer AC failures. Texas freeze events are classified as high-urgency and dispatched immediately."},
            {"q": "How does the AI handle peak-summer call volume in Fort Worth?", "a": "The AI handles unlimited concurrent calls. During Texas heat waves, when multiple customers call simultaneously, all get answered instantly and dispatched in priority order with no busy signal."},
        ],
    },
    {
        "slug":       "indianapolis",
        "city":       "Indianapolis",
        "state":      "IN",
        "area_code":  "317",
        "region_desc": "Indianapolis and the greater Marion County area",
        "suburbs":    "Carmel, Fishers, Greenwood, and Zionsville",
        "climate_hook": "Indianapolis's four-season climate keeps HVAC contractors busy from winter furnace emergencies to summer AC failures across Marion County.",
        "hero_sub":   "Indianapolis HVAC contractors deal with cold Indiana winters driving furnace calls and hot, humid summers driving AC calls — year-round demand. When homeowners need help after hours, whoever answers first gets the job. Syntharra is a 24/7 AI receptionist trained on HVAC scripts and central Indiana service areas. Flat $697/month, 700 minutes, free 14-day pilot, no credit card.",
        "heat_context": "Indianapolis and Marion County",
        "heat_detail":  "Indianapolis experiences genuine four-season weather extremes. January can see temperatures well below freezing, driving emergency furnace calls. July and August bring heat and humidity that push AC systems hard. Contractors who serve both heating and cooling markets get twice the call volume — and twice as many after-hours emergencies.",
        "story_city":   "Carmel",
        "story_time":   "9:45 p.m. on a Tuesday in August",
        "story_temp":   "80°F and climbing",
        "story_context": "a young family",
        "ac_type":      "Carrier system",
        "heat_pump_state": "Indiana",
        "heat_wave_month": "August",
        "faq": [
            {"q": "Do you support area code 317?", "a": "Yes — Syntharra provisions a local Indianapolis-area number in the 317 area code, covering Indianapolis and the greater Marion County area including Carmel, Fishers, Greenwood, and Zionsville."},
            {"q": "How fast can I be live in Indianapolis?", "a": "24 hours from the time you finish the 5-minute onboarding form. You give us your service areas, after-hours rate, truck rolls per day, and dispatch number."},
            {"q": "Does the AI handle both furnace and AC calls?", "a": "Yes. The AI is trained on both heating and cooling HVAC terminology — 'furnace not igniting,' 'no heat,' 'AC not cooling,' 'frozen coils,' and everything in between. It classifies urgency correctly for both heating and cooling emergencies regardless of season."},
            {"q": "What if I already have an answering service?", "a": "Run the pilot in parallel. Put Syntharra as your after-hours forward for 14 days, keep your current service on daytime, and compare call capture rates."},
            {"q": "How does the AI handle Indiana winter furnace emergency spikes?", "a": "The AI handles unlimited concurrent calls. During cold snaps when multiple homeowners call with furnace failures, all get answered instantly and dispatched in urgency order — 'no heat with elderly or children in the home' is classified higher than 'furnace is making a noise.'"},
        ],
    },
    {
        "slug":       "columbus",
        "city":       "Columbus",
        "state":      "OH",
        "area_code":  "614",
        "region_desc": "Columbus and Franklin County",
        "suburbs":    "Dublin, Westerville, Grove City, and Hilliard",
        "climate_hook": "Columbus's humid continental climate drives year-round HVAC demand — hot summers and cold Ohio winters keep contractors busy across Franklin County.",
        "hero_sub":   "Columbus HVAC contractors service one of Ohio's fastest-growing metros through hot, humid summers and cold winters that drive emergency calls around the clock. The contractor who answers first wins. Syntharra is a 24/7 AI receptionist trained on HVAC scripts and central Ohio service areas. Flat $697/month, 700 minutes, free 14-day pilot, no credit card.",
        "heat_context": "Columbus and Franklin County",
        "heat_detail":  "Columbus combines humid Ohio summers with cold winters that create significant HVAC demand on both ends. The metro has grown substantially over the past decade, adding housing stock and increasing the base of potential HVAC customers. Contractors in Columbus compete for every emergency call — the one who answers fastest wins both the immediate job and the long-term relationship.",
        "story_city":   "Dublin",
        "story_time":   "11:00 p.m. on a Monday in July",
        "story_temp":   "82°F and humid",
        "story_context": "a newborn at home",
        "ac_type":      "Bryant system",
        "heat_pump_state": "Ohio",
        "heat_wave_month": "July",
        "faq": [
            {"q": "Do you support area code 614?", "a": "Yes — Syntharra provisions a local Columbus-area number in the 614 area code, covering Columbus and Franklin County including Dublin, Westerville, Grove City, and Hilliard."},
            {"q": "How fast can I be live in Columbus?", "a": "24 hours from the time you finish the 5-minute onboarding form. You give us your service areas, after-hours rate, truck rolls per day, and dispatch number."},
            {"q": "Does the AI handle both furnace and AC emergencies?", "a": "Yes. Columbus HVAC contractors need both heating and cooling coverage, and the AI handles both — 'furnace not igniting' in January and 'AC not cooling' in July are both classified, dispatched, and summarized accurately."},
            {"q": "What if I already have an answering service?", "a": "Run the pilot in parallel. Use Syntharra as your after-hours forward for 14 days and compare capture rates before switching."},
            {"q": "How does the AI handle Columbus summer call peaks?", "a": "The AI handles unlimited concurrent calls. During Ohio heat waves, all callers get answered instantly with no busy signal, and dispatched to your cell in priority order."},
        ],
    },
    {
        "slug":       "memphis",
        "city":       "Memphis",
        "state":      "TN",
        "area_code":  "901",
        "region_desc": "Memphis and Shelby County",
        "suburbs":    "Germantown, Bartlett, Collierville, and Cordova",
        "climate_hook": "Memphis's intense summer heat and high humidity make AC failures urgent emergencies for homeowners across Shelby County.",
        "hero_sub":   "Memphis HVAC contractors deal with some of the most demanding summer conditions in the mid-south — high heat combined with high humidity means a failed AC is a health and safety issue, not just a comfort problem. The contractor who answers first owns the job. Syntharra is a 24/7 AI receptionist trained on HVAC scripts and Shelby County service areas. Flat $697/month, 700 minutes, free 14-day pilot, no credit card.",
        "heat_context": "Memphis and Shelby County",
        "heat_detail":  "Memphis sits in the mid-south where summer heat and humidity converge. The city consistently experiences high heat indices from June through September, and with an older housing stock in many neighborhoods, AC systems are working harder than ever. Emergency calls spike sharply on the hottest days, and whoever answers the phone first — not voicemail — gets the job.",
        "story_city":   "Germantown",
        "story_time":   "12:30 a.m. on a Thursday in August",
        "story_temp":   "85°F and climbing",
        "story_context": "an elderly homeowner",
        "ac_type":      "Older Trane system",
        "heat_pump_state": "Tennessee",
        "heat_wave_month": "August",
        "faq": [
            {"q": "Do you support area code 901?", "a": "Yes — Syntharra provisions a local Memphis-area number in the 901 area code, covering Memphis and Shelby County including Germantown, Bartlett, Collierville, and Cordova."},
            {"q": "How fast can I be live in Memphis?", "a": "24 hours from the time you finish the 5-minute onboarding form. You give us your service areas, after-hours rate, truck rolls per day, and dispatch number."},
            {"q": "Does the AI understand older HVAC systems common in Memphis?", "a": "Yes. The AI captures symptom descriptions accurately for older equipment — R-22 systems, older Trane and Carrier units — and doesn't try to diagnose. It captures what the homeowner reports and dispatches it to you with the right urgency."},
            {"q": "What if I already have an answering service?", "a": "Run the pilot in parallel. Keep your current service on daytime and use Syntharra as your after-hours forward for 14 days, then compare."},
            {"q": "How does the AI handle Memphis peak-summer call volume?", "a": "Unlimited concurrent calls. During Memphis heat events, all callers get answered instantly in priority order — emergencies first, no busy signals, no voicemail."},
        ],
    },
    {
        "slug":       "albuquerque",
        "city":       "Albuquerque",
        "state":      "NM",
        "area_code":  "505",
        "region_desc": "Albuquerque and Bernalillo County",
        "suburbs":    "Rio Rancho, Corrales, Edgewood, and Tijeras",
        "climate_hook": "Albuquerque's high-desert heat and cold winters create year-round HVAC demand across Bernalillo County and the greater metro.",
        "hero_sub":   "Albuquerque HVAC contractors deal with high-desert extremes — summer temperatures regularly exceed 100°F, and winter nights can drop below freezing, driving both AC and furnace emergency calls year-round. The contractor who answers first wins. Syntharra is a 24/7 AI receptionist trained on HVAC scripts and New Mexico service areas. Flat $697/month, 700 minutes, free 14-day pilot, no credit card.",
        "heat_context": "Albuquerque and Bernalillo County",
        "heat_detail":  "Albuquerque's high-desert climate means extreme temperature swings — hot summer days and cool nights, plus cold winters with freeze risk. While the dry air makes the heat feel different from Gulf Coast markets, afternoon temperatures routinely climb above 100°F in June and July, and evaporative coolers (swamp coolers) add a maintenance and emergency category unique to this market.",
        "story_city":   "Rio Rancho",
        "story_time":   "2:00 p.m. on a Saturday in June",
        "story_temp":   "103°F outside and no cooling inside",
        "story_context": "a young family with no shade",
        "ac_type":      "Evaporative cooler and ducted AC",
        "heat_pump_state": "New Mexico",
        "heat_wave_month": "June",
        "faq": [
            {"q": "Do you support area code 505?", "a": "Yes — Syntharra provisions a local Albuquerque-area number in the 505 area code, covering Albuquerque and Bernalillo County including Rio Rancho, Corrales, Edgewood, and Tijeras."},
            {"q": "How fast can I be live in Albuquerque?", "a": "24 hours from the time you finish the 5-minute onboarding form. You give us your service areas, after-hours rate, truck rolls per day, and dispatch number."},
            {"q": "Does the AI understand evaporative coolers (swamp coolers) common in New Mexico?", "a": "Yes. The AI is trained on evaporative cooler terminology — 'swamp cooler not working,' 'pads need replacing,' 'pump not running,' 'water leak from cooler' — in addition to standard AC and furnace terminology. It can classify both correctly."},
            {"q": "What about the altitude — does it affect anything?", "a": "The AI doesn't need to account for altitude — it captures the homeowner's symptom descriptions and dispatches them to you. You make the diagnostic call. The AI focuses on lead capture and urgency classification, not diagnosis."},
            {"q": "How does the AI handle summer afternoon peak call times in Albuquerque?", "a": "Unlimited concurrent calls. During peak afternoon heat, all callers get answered instantly and dispatched in urgency order — emergencies first, no voicemail."},
        ],
    },
    {
        "slug":       "el-paso",
        "city":       "El Paso",
        "state":      "TX",
        "area_code":  "915",
        "region_desc": "El Paso and El Paso County",
        "suburbs":    "Socorro, Horizon City, and Anthony",
        "climate_hook": "El Paso's extreme summer heat — routinely above 100°F — makes HVAC reliability a matter of home safety across El Paso County.",
        "hero_sub":   "El Paso sees some of the most extreme summer heat in the continental US, with temperatures regularly above 100°F from June through September. When an AC fails in El Paso, it's a health emergency — especially for the elderly. Syntharra is a 24/7 AI receptionist trained on HVAC scripts and El Paso County service areas. Flat $697/month, 700 minutes, free 14-day pilot, no credit card.",
        "heat_context": "El Paso and El Paso County",
        "heat_detail":  "El Paso's Chihuahuan Desert climate means summers are intense and extended — months of triple-digit heat with low humidity that bakes homes quickly when AC fails. The city has a large proportion of elderly residents, for whom AC failure can become a medical emergency within hours. HVAC contractors in El Paso who answer every call build reputations that drive referral businesses year over year.",
        "story_city":   "El Paso",
        "story_time":   "3:00 p.m. on a Wednesday in July",
        "story_temp":   "105°F outside and 92°F inside within the hour",
        "story_context": "an 80-year-old homeowner",
        "ac_type":      "Window and central AC",
        "heat_pump_state": "Texas",
        "heat_wave_month": "July",
        "faq": [
            {"q": "Do you support area code 915?", "a": "Yes — Syntharra provisions a local El Paso-area number in the 915 area code, covering El Paso and El Paso County including Socorro, Horizon City, and Anthony."},
            {"q": "How fast can I be live in El Paso?", "a": "24 hours from the time you finish the 5-minute onboarding form. You give us your service areas, after-hours rate, truck rolls per day, and dispatch number."},
            {"q": "Does the AI understand the desert climate context of El Paso calls?", "a": "Yes. The AI classifies calls by urgency, and in extreme heat markets like El Paso, mentions of elderly residents, children, or extreme indoor temperatures are flagged as highest urgency and dispatched to your cell immediately — not held for morning."},
            {"q": "Does the AI handle both Spanish and English speakers?", "a": "The AI handles English calls with high accuracy. For Spanish-language calls, it captures as much as it can and flags the call for callback — ensuring no lead is lost even if the full conversation requires a bilingual follow-up from your team."},
            {"q": "How does the AI handle El Paso's daytime peak call volume?", "a": "Unlimited concurrent calls. During El Paso's afternoon heat peak — when calls come in simultaneously — all get answered instantly with no busy signal and dispatched in priority order."},
        ],
    },
]


def build_page(c: dict) -> str:
    """Render a complete city landing page from city config dict."""
    slug = c["slug"]
    city = c["city"]
    state = c["state"]
    area_code = c["area_code"]
    region_desc = c["region_desc"]
    suburbs = c["suburbs"]
    hero_sub = c["hero_sub"]
    heat_context = c["heat_context"]
    heat_detail = c["heat_detail"]
    story_city = c["story_city"]
    story_time = c["story_time"]
    story_temp = c["story_temp"]
    story_context = c["story_context"]
    ac_type = c["ac_type"]
    heat_pump_state = c["heat_pump_state"]

    faq_html = "\n".join(
        f"""                <div class="faq-item">
                    <div class="faq-q">{q['q']}</div>
                    <div class="faq-a">{q['a']}</div>
                </div>"""
        for q in c["faq"]
    )

    faq_schema = ",\n".join(
        f'            {{"@type": "Question", "name": {json_str(q["q"])}, "acceptedAnswer": {{"@type": "Answer", "text": {json_str(q["a"])}}}}}'
        for q in c["faq"]
    )

    utm = f"hvac-{slug}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="icon" type="image/svg+xml" href="/favicon.svg">
    <link rel="apple-touch-icon" href="/favicon.svg">
    <meta name="theme-color" content="#6C63FF">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{city} HVAC Answering Service \u2014 24/7 AI from $697/mo | Syntharra</title>
    <meta name="description" content="{city} HVAC answering service. 24/7 AI receptionist trained on HVAC scripts, flat $697/mo, 700 minutes. Free 14-day pilot, no credit card, live in 24 hours.">
    <link rel="canonical" href="https://syntharra.com/hvac-answering-service-{slug}.html">

    <!-- Open Graph -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://syntharra.com/hvac-answering-service-{slug}.html">
    <meta property="og:title" content="{city} HVAC Answering Service \u2014 24/7 AI from $697/mo">
    <meta property="og:description" content="{city} HVAC answering service. 24/7 AI receptionist trained on HVAC scripts, flat $697/mo, 700 minutes. Free 14-day pilot, no credit card, live in 24 hours.">
    <meta property="og:image" content="https://raw.githubusercontent.com/Syntharra/syntharra-automations/main/brand-assets/email-signature/syntharra-icon.png">
    <meta property="og:site_name" content="Syntharra">

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="https://syntharra.com/hvac-answering-service-{slug}.html">
    <meta name="twitter:title" content="{city} HVAC Answering Service \u2014 24/7 AI from $697/mo">
    <meta name="twitter:description" content="{city} HVAC answering service. 24/7 AI receptionist trained on HVAC scripts, flat $697/mo, 700 minutes. Free 14-day pilot, no credit card, live in 24 hours.">
    <meta name="twitter:image" content="https://raw.githubusercontent.com/Syntharra/syntharra-automations/main/brand-assets/email-signature/syntharra-icon.png">

    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
:root{{
  --violet:#6C63FF; --violet-2:#8B85FF; --violet-d:#5A52E0;
  --ink:#0E0E1A; --ink-2:#1A1A2E; --body:#4A4A6A; --muted:#8A8AA8;
  --bg:#F7F7FB; --card:#FFFFFF; --border:#E8E8F0; --line:#EFEFF6;
  --green:#10B981; --red:#EF4444; --amber:#F59E0B;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{overflow-x:clip}}
body{{font-family:'Inter',system-ui,sans-serif;color:var(--ink-2);background:var(--bg);font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}}
a{{color:inherit;text-decoration:none}}
img{{max-width:100%;display:block}}
.container{{max-width:980px;margin:0 auto;padding:0 24px}}
#header{{position:sticky;top:0;z-index:50;backdrop-filter:saturate(180%) blur(14px);background:rgba(247,247,251,.78);border-bottom:1px solid var(--line)}}
.header-inner{{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;max-width:1560px;margin:0 auto}}
.nav-cta{{background:var(--violet);color:#fff !important;padding:10px 18px;border-radius:11px;font-weight:600;box-shadow:0 6px 24px -8px rgba(108,99,255,.55);transition:all .2s}}
.nav-cta:hover{{background:var(--violet-d);transform:translateY(-1px)}}
.logo-section{{display:inline-flex;align-items:center;gap:12px;text-decoration:none}}
footer{{padding:56px 0 32px;background:#fff;border-top:1px solid var(--line)}}
.footer-content{{max-width:980px;margin:0 auto;padding:0 24px}}
.footer-bottom{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}}
.footer-copyright{{font-size:12px;color:var(--muted)}}
.footer-links{{list-style:none;display:flex;gap:20px;padding:0;margin:0}}
.footer-links a{{font-size:12px;color:var(--muted);text-decoration:none}}
.footer-links a:hover{{color:var(--violet)}}
.hero{{padding:60px 0 24px;text-align:center}}
.hero-tag{{display:inline-block;font-size:11px;font-weight:700;color:var(--violet);letter-spacing:.16em;text-transform:uppercase;background:rgba(108,99,255,.08);padding:6px 14px;border-radius:20px;margin-bottom:18px}}
.hero h1{{font-size:clamp(30px,4.4vw,46px);font-weight:800;line-height:1.12;letter-spacing:-.02em;color:var(--ink);margin-bottom:18px}}
.hero h1 .accent{{background:linear-gradient(135deg,#6C63FF 0%,#8B85FF 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.hero-sub{{font-size:18px;color:var(--body);max-width:720px;margin:0 auto 26px;line-height:1.55}}
.hero-cta{{display:inline-flex;align-items:center;gap:10px;background:linear-gradient(135deg,#6C63FF 0%,#8B85FF 100%);color:#fff;padding:16px 32px;border-radius:12px;font-weight:700;font-size:15px;text-decoration:none;box-shadow:0 12px 36px -10px rgba(108,99,255,.55);transition:all .2s}}
.hero-cta:hover{{transform:translateY(-2px);box-shadow:0 16px 44px -10px rgba(108,99,255,.7)}}
.hero-fineprint{{display:block;margin-top:14px;font-size:12px;color:var(--muted)}}
.compare{{padding:32px 0}}
.compare-card{{background:var(--card);border:1px solid var(--border);border-radius:18px;overflow:hidden;box-shadow:0 8px 32px -8px rgba(14,14,26,.06)}}
.compare-card::before{{content:"";display:block;height:4px;background:linear-gradient(135deg,#6C63FF 0%,#8B85FF 100%)}}
.compare-card-inner{{padding:28px 32px}}
.compare-card h2{{font-size:22px;font-weight:800;color:var(--ink);margin-bottom:6px;letter-spacing:-.015em}}
.compare-card-sub{{font-size:13px;color:var(--muted);margin-bottom:22px}}
table.compare-table{{width:100%;border-collapse:collapse;font-size:14px}}
.compare-table th,.compare-table td{{padding:14px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}}
.compare-table th{{font-size:11px;font-weight:700;color:var(--muted);letter-spacing:.06em;text-transform:uppercase}}
.compare-table th.col-syntharra,.compare-table td.col-syntharra{{background:rgba(108,99,255,.04);color:var(--ink)}}
.compare-table td.label{{font-weight:600;color:var(--ink-2);width:32%}}
.compare-table .yes{{color:var(--green);font-weight:700}}
.section{{padding:36px 0}}
.section h2{{font-size:24px;font-weight:800;color:var(--ink);margin-bottom:14px;letter-spacing:-.015em}}
.section p{{font-size:15px;color:var(--body);margin-bottom:14px;line-height:1.7}}
.section blockquote{{margin:18px 0;padding:14px 18px;border-left:3px solid var(--violet);background:rgba(108,99,255,.03);font-style:italic;font-size:14px;color:var(--ink-2);border-radius:0 10px 10px 0}}
.section blockquote cite{{display:block;margin-top:8px;font-style:normal;font-size:12px;color:var(--muted);font-weight:600}}
.faq{{padding:32px 0}}
.faq h2{{font-size:24px;font-weight:800;color:var(--ink);text-align:center;margin-bottom:24px;letter-spacing:-.015em}}
.faq-list{{display:flex;flex-direction:column;gap:12px}}
.faq-item{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px 22px}}
.faq-q{{font-size:15px;font-weight:700;color:var(--ink);margin-bottom:6px}}
.faq-a{{font-size:14px;color:var(--body);line-height:1.6}}
.final-cta{{padding:48px 0 64px;text-align:center}}
.final-cta h2{{font-size:26px;font-weight:800;color:var(--ink);margin-bottom:12px;letter-spacing:-.015em}}
.final-cta p{{font-size:15px;color:var(--body);margin-bottom:24px;max-width:560px;margin-left:auto;margin-right:auto}}
@media(max-width:680px){{
  .container{{padding:0 18px}}
  .compare-card-inner{{padding:22px 18px}}
  .compare-table th,.compare-table td{{padding:10px 6px;font-size:13px}}
}}
    </style>
</head>
<body data-page="hvac-answering-service-{slug}" data-asset-id="hvac-{slug}-2026-04">
    <header id="header">
        <div class="header-inner">
            <a href="/" class="logo-section" aria-label="Syntharra \u2014 Global AI Solutions">
                <svg xmlns="http://www.w3.org/2000/svg" width="158" height="34" viewBox="0 0 158 34" role="img">
                    <g fill="#6C63FF">
                        <rect x="0"  y="21" width="4" height="9"  rx="1"/>
                        <rect x="7"  y="17" width="4" height="13" rx="1"/>
                        <rect x="14" y="13" width="4" height="17" rx="1"/>
                        <rect x="21" y="9"  width="4" height="21" rx="1"/>
                    </g>
                    <text x="37" y="21" font-family="Inter,Arial,sans-serif" font-weight="700" font-size="16" fill="#1A1A2E" letter-spacing="-0.48">Syntharra</text>
                    <text x="37" y="32" font-family="Inter,Arial,sans-serif" font-weight="500" font-size="8" fill="#6C63FF" letter-spacing="1.2">GLOBAL AI SOLUTIONS</text>
                </svg>
            </a>
            <a href="/start" class="nav-cta" data-cta="header">Start free pilot \u2192</a>
        </div>
    </header>

    <main>
        <section class="hero container">
            <div class="hero-tag">HVAC answering service \u2014 {city}, {state}</div>
            <h1>{city} HVAC contractors \u2014<br><span class="accent">your phone is answered.</span></h1>
            <p class="hero-sub">{hero_sub}</p>
            <a href="/start?utm_source={utm}&amp;utm_medium=organic&amp;utm_campaign=city-landing&amp;stx_asset_id=hvac-{slug}-2026-04" class="hero-cta" data-cta="hero">
                Try the free 14-day pilot \u2192
            </a>
            <span class="hero-fineprint">200 minutes \u00b7 No credit card \u00b7 Live in 24 hours</span>
        </section>

        <section class="section container">
            <h2>Why HVAC contractors in {city} need a 24/7 AI receptionist</h2>
            <p>{heat_detail}</p>
            <p>When homeowners lose their AC or furnace after hours, they call through the list until someone answers. The contractor who picks up first wins not just the immediate service call but the long-term maintenance relationship and all the referrals that come with it. Letting calls go to voicemail at night doesn't just cost you one job — it costs you the customer relationship.</p>
            <p>A 24/7 AI receptionist that answers under one second, classifies the urgency, captures the contact details and symptoms, and texts your cell within 30 seconds is the most cost-effective way to stop losing after-hours leads. At $697/month flat, a single captured emergency call covers a significant portion of the monthly cost.</p>
        </section>

        <section class="compare container">
            <div class="compare-card">
                <div class="compare-card-inner">
                    <h2>What's included in the $697 flat</h2>
                    <p class="compare-card-sub">No per-call surcharges, no after-hours add-on, no setup fees. {city} HVAC shops, Phase 0 pilot pricing.</p>
                    <table class="compare-table">
                        <thead>
                            <tr>
                                <th></th>
                                <th class="col-syntharra">Included in $697/mo</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="label">Answer every call 24/7</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 midnight, holidays, summer heat waves, all included</td>
                            </tr>
                            <tr>
                                <td class="label">Trained on HVAC keywords</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 "no cooling," "burning smell," "breaker tripped," "frozen line"</td>
                            </tr>
                            <tr>
                                <td class="label">Auto-dispatch emergencies</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 instant SMS to your cell within 30 seconds</td>
                            </tr>
                            <tr>
                                <td class="label">700 minutes/month</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 unlimited calls in budget; overage only $0.18/min</td>
                            </tr>
                            <tr>
                                <td class="label">Call transcripts + AI summary</td>
                                <td class="col-syntharra"><span class="yes">Yes</span> \u2014 full transcript, intent, urgency, lead flag per call</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <section class="section container">
            <h2>How it works in a {city} emergency</h2>
            <p>It's {story_time}. A homeowner in {story_city} wakes up to find their AC has stopped — {story_temp}. They're worried about {story_context}. They grab their phone and start calling HVAC shops. You're the second number on the list.</p>
            <p>The AI answers on the first ring \u2014 0.4 seconds, not a voicemail beep. It hears the urgency, classifies the call as <code>urgency=emergency</code>, <code>is_lead=true</code>. It responds calmly: <em>"I understand how stressful that is. Let me get your details to a technician right away. Can I confirm your address and a callback number?"</em> Within 30 seconds, your phone gets a text: customer name, address in {story_city}, symptom and urgency level.</p>
            <p>You call back, confirm the visit, and turn the emergency into a long-term maintenance customer. The first shop on the list sent the call to voicemail and lost both the job and the relationship.</p>
        </section>

        <section class="faq container">
            <h2>{city} HVAC answering service \u2014 common questions</h2>
            <div class="faq-list">
{faq_html}
            </div>
        </section>

        <section class="final-cta container">
            <h2>Stop losing {city} after-hours leads to voicemail.</h2>
            <p>14 days. 200 minutes. No credit card. Live in 24 hours. If the AI doesn't pay for itself, you walk away with every transcript and we never charge you.</p>
            <a href="/start?utm_source={utm}&amp;utm_medium=organic&amp;utm_campaign=city-landing&amp;stx_asset_id=hvac-{slug}-2026-04" class="hero-cta" data-cta="footer" style="margin:0 auto">
                Start my free 14-day pilot \u2192
            </a>
        </section>
    </main>

    <footer>
        <div class="footer-content">
            <div class="footer-bottom">
                <div class="footer-copyright">\u00a9 2026 Syntharra \u00b7 Global AI Solutions. All rights reserved.</div>
                <ul class="footer-links">
                    <li><a href="/privacy.html">Privacy</a></li>
                    <li><a href="/terms.html">Terms</a></li>
                    <li><a href="/security.html">Security</a></li>
                    <li><a href="mailto:support@syntharra.com">Contact</a></li>
                </ul>
            </div>
        </div>
    </footer>

    <script src="/marketing-tracker.js" defer></script>
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "Syntharra HVAC Answering Service - {city}",
        "description": "{city} HVAC answering service. 24/7 AI receptionist trained on HVAC scripts, flat $697/mo, 700 minutes. Free 14-day pilot, no credit card, live in 24 hours.",
        "url": "https://syntharra.com/hvac-answering-service-{slug}.html",
        "telephone": "+1-000-000-0000",
        "priceRange": "$$$",
        "address": {{
            "@type": "PostalAddress",
            "addressLocality": "{city}",
            "addressRegion": "{state}",
            "addressCountry": "US"
        }},
        "areaServed": {{
            "@type": "City",
            "name": "{city}"
        }},
        "openingHoursSpecification": {{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
            "opens": "00:00",
            "closes": "23:59"
        }}
    }}
    </script>
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
{faq_schema}
        ]
    }}
    </script>
</body>
</html>"""


def json_str(s: str) -> str:
    """JSON-encode a string for embedding in script blocks."""
    import json
    return json.dumps(s)


def main():
    ap = argparse.ArgumentParser(description="Generate HVAC city landing pages")
    ap.add_argument("--city", help="Generate only this city (display name)")
    ap.add_argument("--dry-run", action="store_true", help="List cities, don't write")
    ap.add_argument("--skip-existing", action="store_true", help="Skip already-existing files")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    website_dir = os.path.normpath(os.path.join(here, "..", "..", "syntharra-website"))
    if not os.path.isdir(website_dir):
        # Try sibling of automations
        website_dir = os.path.normpath(
            os.path.join(here, "..", "..",
                         "Syntharra Project", "syntharra-website")
        )

    cities = CITIES
    if args.city:
        cities = [c for c in CITIES if c["city"].lower() == args.city.lower()]
        if not cities:
            sys.exit(f"City not found: {args.city!r}. Known: {[c['city'] for c in CITIES]}")

    if args.dry_run:
        print("Would generate:")
        for c in cities:
            path = os.path.join(website_dir, f"hvac-answering-service-{c['slug']}.html")
            exists = " (exists)" if os.path.exists(path) else ""
            print(f"  {c['slug']:30} → {os.path.basename(path)}{exists}")
        return

    written = 0
    skipped = 0
    for c in cities:
        filename = f"hvac-answering-service-{c['slug']}.html"
        path = os.path.join(website_dir, filename)
        if args.skip_existing and os.path.exists(path):
            print(f"[skip] {filename}")
            skipped += 1
            continue
        html = build_page(c)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        lines = html.count("\n") + 1
        print(f"[ok]   {filename}  ({lines} lines)")
        written += 1

    print(f"\nDone: {written} written, {skipped} skipped.")
    if written:
        print("Run generate_sitemap.py to update sitemap.xml")


if __name__ == "__main__":
    main()
