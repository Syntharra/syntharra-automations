"""
Generate 20 HVAC answering service SEO landing pages (Northeast & Mid-Atlantic)
and push them to Syntharra/syntharra-website on GitHub.
"""

import base64
import json
import time
import requests

TOKEN = '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'
REPO  = 'Syntharra/syntharra-website'
API   = f'https://api.github.com/repos/{REPO}/contents'
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Content-Type':  'application/json',
    'Accept':        'application/vnd.github.v3+json',
}

CITIES = [
    {
        "name": "Philadelphia", "state": "PA", "slug": "philadelphia",
        "climate": "Philly summers are brutally humid — heat index well above 100°F is common in July and August. Winters bring serious cold with occasional major snow events. Row houses and aging brownstones throughout the city mean constant HVAC demand year-round.",
        "season": "hot humid summers and cold winters",
        "neighborhoods": "neighborhoods like Fishtown, South Philly, and Kensington",
        "local_detail": "The dense row-house blocks of South Philadelphia and the aging brownstones of West Philly mean a single broken AC unit can make an entire household uninhabitable on a 98-degree July afternoon.",
        "seasonal_q": "How does Syntharra handle the surge in calls during Philadelphia's summer heat waves?",
        "seasonal_a": "During Philly's brutal July and August heat waves — when the heat index pushes past 105°F — call volume can triple overnight. Syntharra handles unlimited simultaneous calls, so every homeowner in Fishtown, South Philly, or Kensington gets answered instantly, even on the hottest day of the year.",
        "testimonial_idx": 0,
    },
    {
        "name": "Boston", "state": "MA", "slug": "boston",
        "climate": "Boston winters are serious — blizzards, ice storms, and temperatures well below freezing from December through March. Summers bring surprising humidity. Older Back Bay and triple-decker housing stock means contractors are always busy with aging systems.",
        "season": "severe winters and humid summers",
        "neighborhoods": "neighborhoods like Back Bay, Dorchester, and Somerville",
        "local_detail": "Boston's triple-deckers — the iconic three-family wood-frame buildings packed across Dorchester, Roxbury, and Jamaica Plain — rely heavily on aging boilers and radiator systems that need constant attention through a brutal New England winter.",
        "seasonal_q": "How does Syntharra help Boston HVAC contractors during nor'easters and blizzards?",
        "seasonal_a": "When a nor'easter hits Boston and temperatures plunge, furnace failures become life-safety emergencies. Syntharra answers every call — even at 2am during a blizzard — captures the full job details, and texts you immediately so no homeowner in Dorchester or Back Bay is left without heat.",
        "testimonial_idx": 1,
    },
    {
        "name": "Baltimore", "state": "MD", "slug": "baltimore",
        "climate": "Baltimore sits in the heat and humidity corridor of the mid-Atlantic — summers hit 95°F with oppressive humidity, and Chesapeake Bay moisture makes winters damp and cold. Row houses throughout the city create steady HVAC demand.",
        "season": "hot humid summers and cold winters",
        "neighborhoods": "neighborhoods like Fells Point, Federal Hill, and Hampden",
        "local_detail": "Baltimore's iconic marble-stoop row houses look beautiful but were built for a different era — their aging ductwork and boiler systems struggle hard when the heat index pushes past 100°F in July, and contractors serving Fells Point, Canton, and Federal Hill stay slammed all summer.",
        "seasonal_q": "Does Baltimore's humidity make HVAC calls more frequent than other cities?",
        "seasonal_a": "Absolutely. Baltimore's position in the mid-Atlantic humidity corridor means AC systems run harder and fail more often than in drier climates. Combined with the city's aging row-house housing stock, Chesapeake-area contractors typically see 30–40% higher call volume per unit compared to the national average. Syntharra makes sure none of those calls go to voicemail.",
        "testimonial_idx": 2,
    },
    {
        "name": "Virginia Beach", "state": "VA", "slug": "virginia-beach",
        "climate": "Virginia Beach's coastal location means high humidity year-round, brutal summer heat, and a salt air environment that accelerates HVAC wear. Contractors serving the resort strip and sprawling suburban neighborhoods need 24/7 availability.",
        "season": "year-round coastal humidity and summer heat",
        "neighborhoods": "neighborhoods like Oceanfront, Chesapeake Beach, and Great Neck",
        "local_detail": "The salt air environment along the Virginia Beach Oceanfront isn't just hard on cars — it corrodes AC coils, refrigerant lines, and electrical components faster than inland climates. Homeowners in Great Neck and Chesapeake Beach need more frequent service calls, and every one of those calls is a revenue opportunity.",
        "seasonal_q": "How does salt air affect HVAC demand in Virginia Beach?",
        "seasonal_a": "Salt air corrosion is a real accelerant for HVAC wear in Virginia Beach — coils and components that would last 15 years inland might need replacement in 8-10 years near the coast. That means more service calls per household, year-round. Syntharra captures every one of those calls so competitors don't get them instead.",
        "testimonial_idx": 0,
    },
    {
        "name": "Richmond", "state": "VA", "slug": "richmond",
        "climate": "Richmond's inland location makes it hotter and more humid than the Virginia coast — summers regularly hit 95°F+ with high humidity. The city's colonial housing stock means older HVAC systems that need frequent service and replacement.",
        "season": "hot humid summers and cold winters",
        "neighborhoods": "neighborhoods like the Fan District, Church Hill, and Scott's Addition",
        "local_detail": "Richmond's Fan District is packed with stunning Victorian and Colonial Revival homes — but their old ductwork, wall units, and aging central systems are a constant source of service calls. When the humidity hits 90% in August and the AC dies, homeowners in Church Hill call the first contractor who picks up.",
        "seasonal_q": "Richmond gets both extreme heat and cold — how does Syntharra handle both busy seasons?",
        "seasonal_a": "Richmond contractors run two full busy seasons — summer AC calls peak in July-August when the city bakes at 95°F+, and heating calls surge in December-January when temps drop into the 20s. Syntharra runs 24/7/365 and handles both seasons equally well, capturing every emergency call whether it's a dead AC in August or a broken furnace on Christmas Eve.",
        "testimonial_idx": 1,
    },
    {
        "name": "Norfolk", "state": "VA", "slug": "norfolk",
        "climate": "Norfolk's Navy and port presence means dense residential neighborhoods with diverse housing stock. Chesapeake Bay humidity and coastal heat push AC demand hard in summer, while cold wet winters drive heating calls. Contractors here run two full busy seasons.",
        "season": "coastal humidity year-round",
        "neighborhoods": "neighborhoods like Ghent, Ocean View, and Wards Corner",
        "local_detail": "Norfolk's military housing — the dense residential clusters near Naval Station Norfolk — represents thousands of households with rotating tenants and aging HVAC systems. Combine that with Ghent's historic craftsman homes and Ocean View's coastal properties, and contractors here have an enormous, year-round service territory.",
        "seasonal_q": "Does Syntharra work well for contractors serving military housing in Norfolk?",
        "seasonal_a": "Syntharra is ideal for high-volume territories like Norfolk's military housing clusters. When dozens of households near Naval Station Norfolk all experience AC issues on the same hot weekend, Syntharra handles every simultaneous call, captures each job's full details — unit number, issue, contact info — and texts you immediately so you can dispatch efficiently.",
        "testimonial_idx": 2,
    },
    {
        "name": "Buffalo", "state": "NY", "slug": "buffalo",
        "climate": "Buffalo is legendary for lake-effect snow — averaging over 90 inches per year. Furnace emergencies during January blizzards are life-safety events. HVAC contractors here need 24/7 call coverage from October through April — a missed call during a snowstorm is a client lost forever.",
        "season": "extreme lake-effect snow and cold winters",
        "neighborhoods": "neighborhoods like Elmwood Village, South Buffalo, and the Northtowns",
        "local_detail": "When a Lake Erie lake-effect band drops 30 inches of snow on South Buffalo overnight and temperatures plunge to single digits, furnace failures aren't inconvenient — they're dangerous. A family in Elmwood Village can't wait until morning when you check your voicemail. They call the next contractor on the list.",
        "seasonal_q": "How does Syntharra handle the extreme call volume during Buffalo's lake-effect snow events?",
        "seasonal_a": "Buffalo's lake-effect events are unlike anything else in the continental US — a single storm can generate dozens of furnace emergency calls overnight. Syntharra handles unlimited simultaneous calls with no degradation in quality, answers in under 3 seconds, and texts you each job immediately. You wake up to a full dispatch list instead of a voicemail box you can't get through.",
        "testimonial_idx": 0,
    },
    {
        "name": "Worcester", "state": "MA", "slug": "worcester",
        "climate": "Worcester's inland New England location means serious winters with heavy snowfall and cold snaps. The city's dense triple-decker housing stock and older commercial buildings create steady year-round HVAC demand.",
        "season": "harsh New England winters",
        "neighborhoods": "neighborhoods like Main South, Burncoat, and Tatnuck",
        "local_detail": "Worcester's triple-deckers are everywhere — from Main South to Burncoat — and their boiler systems, radiators, and converted forced-air setups require constant service. When a boiler dies in a three-family building in January, three households go without heat simultaneously. Every call matters.",
        "seasonal_q": "What's the biggest challenge for Worcester HVAC contractors in winter?",
        "seasonal_a": "Worcester winters are unforgiving — the city sits at elevation and catches every cold snap that rolls through New England. Heating emergencies in January and February often come in clusters, overwhelming contractors who rely on voicemail. Syntharra answers every call instantly, even when you're already on three jobs, so no Worcester family gets left in the cold.",
        "testimonial_idx": 1,
    },
    {
        "name": "Providence", "state": "RI", "slug": "providence",
        "climate": "Providence winters are genuinely harsh — cold, snowy, and relentless. The city's historic housing stock from the 1800s and early 1900s means aging boilers and HVAC systems that break down regularly. Contractors who answer fastest capture the market.",
        "season": "cold New England winters",
        "neighborhoods": "neighborhoods like College Hill, Federal Hill, and Fox Point",
        "local_detail": "Providence's College Hill is packed with Federal and Victorian-era homes — gorgeous architecture with ancient heating systems that have been patched, converted, and re-converted for 150 years. When those systems fail in January, homeowners on Benefit Street aren't waiting around — they're calling every HVAC number they can find.",
        "seasonal_q": "Does Providence's older housing stock mean more heating calls than average?",
        "seasonal_a": "Dramatically more. Providence has one of the oldest housing stocks in America — a huge percentage of homes in College Hill, Federal Hill, and Fox Point date from before 1940 with heating systems that have been jury-rigged through multiple renovations. Failure rates are higher, service frequency is higher, and the contractor who answers first gets the lifetime client.",
        "testimonial_idx": 2,
    },
    {
        "name": "Newark", "state": "NJ", "slug": "newark",
        "climate": "Newark's urban density and proximity to the NYC metro means extreme heat island effect in summer — temperatures routinely exceed 95°F. Dense residential housing, industrial areas, and commercial properties create diverse, high-volume HVAC demand year-round.",
        "season": "intense urban heat and cold winters",
        "neighborhoods": "neighborhoods like the Ironbound, Forest Hill, and Weequahic",
        "local_detail": "The Ironbound — Newark's dense Portuguese and Brazilian neighborhood — is packed with multi-family homes where a single broken AC unit in a top-floor apartment can create an uninhabitable situation within hours when the heat island effect pushes temperatures past 100°F. Speed of answer is everything.",
        "seasonal_q": "How does the heat island effect in Newark affect HVAC call volume?",
        "seasonal_a": "Urban heat island effect in Newark can push temperatures 8-10°F above surrounding suburbs on hot days — meaning a 90°F day in Short Hills becomes a 100°F emergency in the Ironbound. This dramatically increases the frequency and urgency of AC failures in summer. Syntharra ensures every call from Newark's dense residential neighborhoods gets answered instantly.",
        "testimonial_idx": 0,
    },
    {
        "name": "Jersey City", "state": "NJ", "slug": "jersey-city",
        "climate": "Jersey City's rapid gentrification has brought a surge of high-value renovations — clients expecting premium service, instant response, and no missed calls. Summer heat and cold winters create year-round HVAC demand across its dense, mixed-use buildings.",
        "season": "urban heat and cold winters",
        "neighborhoods": "neighborhoods like Journal Square, the Heights, and Downtown",
        "local_detail": "Jersey City's Downtown and Hamilton Park neighborhoods have gentrified rapidly — the brownstones and converted lofts that now sell for $1.2M are occupied by professionals who expect instant, premium service. A contractor who goes to voicemail gets replaced immediately. The bar here is higher than almost anywhere else in the country.",
        "seasonal_q": "Do Jersey City's high-end clients have different expectations than other markets?",
        "seasonal_a": "Absolutely. Downtown Jersey City and the Heights attract clients who are used to instant everything — Uber, DoorDash, same-day delivery. When their AC fails on a hot July night, they expect to reach someone immediately. Syntharra answers in under 3 seconds, professionally, and gets them the information they need. That first impression determines whether you get the job — and the referrals that come with it.",
        "testimonial_idx": 1,
    },
    {
        "name": "Yonkers", "state": "NY", "slug": "yonkers",
        "climate": "Just north of New York City, Yonkers deals with the full range of metro weather — brutal summers with heat-island effect and cold, snowy winters. Dense residential housing stacked on hillsides means contractors serve multiple neighborhoods with aging systems.",
        "season": "urban heat and cold winters",
        "neighborhoods": "neighborhoods like Northwest Yonkers, Nepperhan, and Park Hill",
        "local_detail": "Yonkers is one of the most densely populated mid-sized cities in America — its hillside neighborhoods are packed with pre-war apartment buildings and multi-family homes with aging boilers and window units that get pushed hard every summer and winter. The potential client pool is enormous for contractors who show up first.",
        "seasonal_q": "What makes Yonkers different from other Westchester County HVAC markets?",
        "seasonal_a": "Yonkers has the density of New York City combined with the housing age of a classic Rust Belt city — it's an unusually high-demand HVAC market. The hills and dense urban blocks mean contractors can run multiple jobs close together when they're organized. Syntharra captures every call, texts you instantly, and helps you fill your calendar with the high-volume work Yonkers generates.",
        "testimonial_idx": 2,
    },
    {
        "name": "Bridgeport", "state": "CT", "slug": "bridgeport",
        "climate": "Connecticut summers are more humid than people expect — heat index regularly hits 100°F in Bridgeport's urban core. Winters bring real cold and snow. The city's aging industrial and residential housing stock means constant HVAC service calls.",
        "season": "humid summers and cold winters",
        "neighborhoods": "neighborhoods like Black Rock, the North End, and South End",
        "local_detail": "Bridgeport's Black Rock neighborhood — a mix of working-class homes and new waterfront development — represents the diversity of the HVAC market here. From aging oil-fired systems in century-old bungalows to modern mini-split installations in renovated condos, contractors serving Bridgeport need to be ready for everything, all year.",
        "seasonal_q": "Is Bridgeport really that much hotter than the rest of Connecticut in summer?",
        "seasonal_a": "Yes — Bridgeport's coastal urban core creates a pronounced heat island effect that makes it consistently the hottest spot in Connecticut during summer heat waves. Heat index values of 100-105°F are common in July and August, pushing AC systems to their limits. When those systems fail, homeowners need someone to answer immediately — and that's what Syntharra delivers.",
        "testimonial_idx": 0,
    },
    {
        "name": "Hartford", "state": "CT", "slug": "hartford",
        "climate": "Hartford's inland New England location brings cold winters and humid summers. Insurance industry professionals and families in the metro area expect immediate response when HVAC fails — contractors who miss calls lose them to the next available company.",
        "season": "cold winters and humid summers",
        "neighborhoods": "neighborhoods like West Hartford, Blue Hills, and Parkville",
        "local_detail": "Hartford's insurance industry workforce — the professionals and families who make this the 'insurance capital of the world' — are exactly the kind of clients who expect a premium experience. When the AC fails in a West Hartford colonial, they're not leaving a voicemail. They're calling the next number before the beep finishes.",
        "seasonal_q": "How does the Hartford market respond to after-hours HVAC emergencies?",
        "seasonal_a": "Hartford's metro clientele — the insurance professionals, healthcare workers, and business owners concentrated in West Hartford and surrounding towns — make rapid decisions. If they can't reach you, they call someone else and often never come back. Syntharra answers every after-hours call in under 3 seconds, captures every job detail, and texts you the lead immediately, keeping you ahead of competitors who rely on voicemail.",
        "testimonial_idx": 1,
    },
    {
        "name": "Syracuse", "state": "NY", "slug": "syracuse",
        "climate": "Syracuse averages over 120 inches of snow annually — one of the snowiest cities in America. Furnace emergencies in January are frequent and urgent. HVAC contractors who answer every call during snowstorms build loyalty that lasts decades.",
        "season": "extreme snowfall and cold winters",
        "neighborhoods": "neighborhoods like Eastwood, Strathmore, and the Near Westside",
        "local_detail": "When a Syracuse January storm drops 18 inches overnight and temperatures hit -5°F, a dead furnace is a genuine emergency. Families in Eastwood and Strathmore don't care about business hours — they need heat now. The contractor who answers that 2am call earns a customer for life. The one who lets it go to voicemail loses them forever.",
        "seasonal_q": "How does Syntharra handle the intensity of Syracuse's winter emergency call volume?",
        "seasonal_a": "Syracuse winters generate a category of call volume that most cities never see — multiple simultaneous furnace emergencies during major snow events, many of them life-safety situations. Syntharra handles unlimited parallel calls, never has a busy signal, and texts each job to you instantly so you can triage and dispatch efficiently even when you're already on multiple jobs across the city.",
        "testimonial_idx": 2,
    },
    {
        "name": "Albany", "state": "NY", "slug": "albany",
        "climate": "New York's capital deals with serious winters — cold, snowy, and long. The city's historic Victorian and colonial housing stock means older heating systems that fail regularly. Contractors serving the Capital District need round-the-clock availability.",
        "season": "cold snowy winters and humid summers",
        "neighborhoods": "neighborhoods like Center Square, Pine Hills, and Arbor Hill",
        "local_detail": "Albany's Center Square and Pine Hills neighborhoods are packed with 19th-century brownstones and Victorian homes — beautiful buildings with heating systems that have been patchworked across a hundred years of renovations. A single cold snap in December generates dozens of emergency calls as aging boilers across the Capital District finally give out.",
        "seasonal_q": "Does Albany's government workforce create a different kind of HVAC client?",
        "seasonal_a": "Albany's large state government workforce means a stable, year-round population of homeowners and renters who expect professional service. When heating fails in a Center Square brownstone in January, the state employee living there needs it fixed before the workday — not next week. Syntharra captures every call immediately and gets you that information so you can respond fast and win that long-term client relationship.",
        "testimonial_idx": 0,
    },
    {
        "name": "Rochester", "state": "NY", "slug": "rochester",
        "climate": "Rochester is another upstate New York city hit hard by lake-effect snow — averaging over 100 inches annually. Heating emergencies in winter are common. Summers bring welcome warmth but also AC service calls as older systems struggle.",
        "season": "extreme lake-effect snow and cold winters",
        "neighborhoods": "neighborhoods like the Neighborhood of the Arts, Park Avenue, and Greece",
        "local_detail": "Rochester's Park Avenue neighborhood — tree-lined streets of craftsman bungalows and colonial revivals — is home to the kind of long-term homeowners who build loyal client relationships with their HVAC contractor. But loyalty starts with being available. When a Park Avenue furnace dies in February, whoever answers first gets the relationship.",
        "seasonal_q": "How does Rochester's lake-effect snow season compare to Buffalo's for HVAC contractors?",
        "seasonal_a": "Rochester's lake-effect snow is slightly less intense than Buffalo's but still one of the most demanding in the country at 100+ inches per year. The critical difference is the extended season — Rochester contractors need to be on full alert from mid-October through April. Syntharra provides that 24/7/365 call coverage throughout the entire winter season, not just during storms.",
        "testimonial_idx": 1,
    },
    {
        "name": "Chesapeake", "state": "VA", "slug": "chesapeake",
        "climate": "Chesapeake's vast suburban footprint — one of America's largest cities by area — means contractors drive long distances between jobs. Hot, humid Tidewater summers and cold winters create year-round demand. Missing a call means that long drive belongs to a competitor.",
        "season": "hot humid summers and cold winters",
        "neighborhoods": "neighborhoods like Great Bridge, Greenbrier, and Western Branch",
        "local_detail": "Chesapeake covers more square miles than most people realize — from the Great Bridge historic district to the sprawling subdivisions of Western Branch, contractors can spend 30 minutes between jobs. In that drive time, three calls might come in. Syntharra captures all of them, so none of those long-drive opportunities go to a competitor.",
        "seasonal_q": "How does Syntharra help contractors manage Chesapeake's wide service territory?",
        "seasonal_a": "Chesapeake's enormous geographic footprint creates a unique challenge — when you're driving from Great Bridge to Western Branch, you're on the road for 30-40 minutes. During that time in peak summer or winter season, multiple calls can come in. Syntharra answers every one instantly, captures full job details, and texts you everything so you can make smart routing decisions and fill your day efficiently.",
        "testimonial_idx": 2,
    },
    {
        "name": "Hampton", "state": "VA", "slug": "hampton-va",
        "climate": "Hampton's NASA and military presence means a stable, professional client base that expects instant response. Chesapeake Bay humidity, hot summers, and cold winters create year-round HVAC demand across its mix of historic and newer residential neighborhoods.",
        "season": "coastal humidity year-round",
        "neighborhoods": "neighborhoods like Phoebus, Buckroe Beach, and Aberdeen",
        "local_detail": "Hampton's Langley Air Force Base and NASA Langley Research Center bring in thousands of engineering professionals and military families — a client base that is systematic, organized, and has zero tolerance for missed calls or unprofessional responses. First impressions are everything in this market.",
        "seasonal_q": "Do Hampton's military and NASA clients have higher service expectations?",
        "seasonal_a": "Yes — Hampton's military families and NASA professionals are among the most exacting clients an HVAC contractor can serve. They document everything, expect immediate response, and won't give a second chance to a contractor who goes to voicemail. Syntharra answers every call professionally in under 3 seconds, captures full job details, and gives these high-value clients the instant response they expect.",
        "testimonial_idx": 0,
    },
    {
        "name": "Newport News", "state": "VA", "slug": "newport-news",
        "climate": "Newport News is a major shipbuilding and military hub with dense residential areas. Hampton Roads' coastal humidity makes summers brutal for AC systems, and winters bring cold and damp conditions that test heating equipment.",
        "season": "coastal humidity and seasonal extremes",
        "neighborhoods": "neighborhoods like Hilton, Denbigh, and the East End",
        "local_detail": "Newport News Shipbuilding is one of the largest private employers in Virginia — and the dense residential neighborhoods surrounding it, from the East End to the newer subdivisions of Denbigh, represent thousands of households with year-round HVAC needs. The shipyard workforce runs 24/7, and their family emergencies don't respect business hours.",
        "seasonal_q": "Does the shipyard workforce in Newport News create unusual HVAC call patterns?",
        "seasonal_a": "Absolutely. Newport News Shipbuilding operates around the clock with shift workers who may need an HVAC contractor at 6am or 11pm — hours when most contractors rely on voicemail. Syntharra handles those off-hours calls with the same speed and professionalism as a midday call, capturing every job from Hilton to Denbigh and texting you instantly regardless of what time it comes in.",
        "testimonial_idx": 1,
    },
]

TESTIMONIALS = [
    {
        "quote": "We were losing 8-10 calls a week after hours. Syntharra fixed that in 24 hours. We recovered $14,000 in the first month from jobs we would have lost entirely.",
        "cite": "— Mark T., Arctic Breeze HVAC, Phoenix AZ",
    },
    {
        "quote": "My receptionist cost $3,200 a month and still missed calls. Syntharra costs less and never misses. It's not even a comparison.",
        "cite": "— Jason S., Reliable Plumbing, Denver CO",
    },
    {
        "quote": "Customers genuinely can't tell it's AI. We captured 40+ jobs in the first month. The ROI is incredible.",
        "cite": "— Rachel C., Bright Spark Electric, Austin TX",
    },
]

NAV = '''<nav class="fixed top-6 left-1/2 -translate-x-1/2 w-[96%] max-w-[1900px] z-50 bg-white/70 backdrop-blur-2xl rounded-full border border-white/20 shadow-[0_8px_32px_rgba(0,0,0,0.05)] transition-all duration-500"><div class="flex justify-between items-center px-8 py-3"><a href="/" class="flex items-center gap-3"><div class="flex items-end gap-1"><div class="w-1 h-3 bg-primary rounded-full"></div><div class="w-1 h-5 bg-primary rounded-full"></div><div class="w-1 h-7 bg-primary rounded-full"></div><div class="w-1 h-9 bg-primary rounded-full"></div></div><div class="flex flex-col leading-none" style="margin-top:-4px"><span class="text-2xl font-black tracking-tighter text-slate-900 font-headline">Syntharra</span><span class="text-[9px] font-bold tracking-[0.2em] text-primary uppercase opacity-80">Global AI Solutions</span></div></a><div class="hidden md:flex items-center space-x-8"><a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/how-it-works.html">How It Works</a><a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/demo.html">Demo</a><a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/case-studies.html">Results</a></div><div class="flex items-center gap-2"><a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="bg-primary text-white px-6 py-2 rounded-full font-bold text-sm hover:scale-105 active:scale-95 transition-all font-headline shadow-lg shadow-primary/20">Get Started &rarr;</a><button id="hbg" aria-label="Open menu" class="flex items-center gap-1.5 text-slate-600 hover:text-primary px-3 py-2 rounded-full border border-slate-200 hover:border-primary/30 hover:bg-primary/5 transition-all cursor-pointer"><span class="material-symbols-outlined" style="font-size:18px;line-height:1">menu</span><span class="hidden md:inline text-sm font-semibold">Menu</span></button></div></div></nav>
<div id="bd" class="fixed inset-0 bg-black/60 z-[1000] opacity-0 pointer-events-none transition-opacity duration-250 backdrop-blur-sm"></div>
<div id="mp" class="fixed top-0 right-0 bottom-0 w-[300px] bg-white border-l border-slate-100 z-[1001] translate-x-full transition-transform duration-[380ms] ease-[cubic-bezier(0.16,1,0.3,1)] p-7 flex flex-col overflow-y-auto"><button id="mx" class="self-end text-slate-400 hover:text-slate-900 text-xl mb-6 transition-colors">&times;</button><div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Product</div><div class="flex flex-col gap-2"><a href="/how-it-works.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">How It Works</a><a href="/demo.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Live Demo</a><a href="/faq.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">FAQ</a><a href="/ai-readiness.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">AI Readiness Score</a><a href="/calculator.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Revenue Calculator</a></div></div><div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Learn</div><div class="flex flex-col gap-2"><a href="/case-studies.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Case Studies</a><a href="/blog.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Blog</a></div></div><div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Industries</div><div class="flex flex-col gap-2"><a href="/hvac.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">HVAC</a><a href="/plumbing.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Plumbing</a><a href="/electrical.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Electrical</a></div></div><div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Company</div><div class="flex flex-col gap-2"><a href="/about.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">About</a><a href="/affiliate.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Affiliate Program</a><a href="/careers.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Careers</a><a href="/status.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">System Status</a></div></div><a href="/demo.html" class="mt-auto bg-primary text-white text-center py-4 rounded-2xl font-black text-sm hover:opacity-90 transition-opacity">Book a Free Demo &rarr;</a></div>'''

FOOTER_JS = '''<footer style="background:#0f172a;color:#fff;padding:60px 24px 32px"><div style="max-width:1400px;margin:0 auto"><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:40px;margin-bottom:48px"><div><div style="font-family:sans-serif;font-size:20px;font-weight:900;margin-bottom:12px">Syntharra</div><p style="color:rgba(255,255,255,0.4);font-size:14px;line-height:1.6;margin-bottom:16px">AI voice agents for trade businesses.</p><a href="mailto:support@syntharra.com" style="color:rgba(255,255,255,0.3);font-size:13px;display:block">support@syntharra.com</a></div><div><h4 style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#6366f1;margin-bottom:16px">Product</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/how-it-works.html" style="color:rgba(255,255,255,0.5);font-size:14px">How It Works</a><a href="/demo.html" style="color:rgba(255,255,255,0.5);font-size:14px">Live Demo</a><a href="/calculator.html" style="color:rgba(255,255,255,0.5);font-size:14px">Revenue Calculator</a><a href="/faq.html" style="color:rgba(255,255,255,0.5);font-size:14px">FAQ</a></div></div><div><h4 style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#6366f1;margin-bottom:16px">Industries</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/hvac.html" style="color:rgba(255,255,255,0.5);font-size:14px">HVAC</a><a href="/plumbing.html" style="color:rgba(255,255,255,0.5);font-size:14px">Plumbing</a><a href="/electrical.html" style="color:rgba(255,255,255,0.5);font-size:14px">Electrical</a></div></div><div><h4 style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#6366f1;margin-bottom:16px">Company</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/about.html" style="color:rgba(255,255,255,0.5);font-size:14px">About</a><a href="/case-studies.html" style="color:rgba(255,255,255,0.5);font-size:14px">Case Studies</a><a href="/blog.html" style="color:rgba(255,255,255,0.5);font-size:14px">Blog</a></div></div></div><div style="border-top:1px solid rgba(255,255,255,0.08);padding-top:24px;text-align:center;color:rgba(255,255,255,0.2);font-size:12px">&copy; 2026 Syntharra Global AI Solutions. All rights reserved.</div></div></footer>
<script>const bd=document.getElementById('bd'),mp=document.getElementById('mp'),mx=document.getElementById('mx'),hbg=document.getElementById('hbg');function openMenu(){bd.classList.add('opacity-100','pointer-events-auto');mp.style.transform='translateX(0)';document.body.style.overflow='hidden';}function closeMenu(){bd.classList.remove('opacity-100','pointer-events-auto');mp.style.transform='';document.body.style.overflow='';}if(hbg)hbg.addEventListener('click',openMenu);if(mx)mx.addEventListener('click',closeMenu);if(bd)bd.addEventListener('click',closeMenu);</script>'''

CSS = """*{box-sizing:border-box;margin:0;padding:0}html,body{overflow-x:clip}body{font-family:'DM Sans',system-ui,sans-serif;color:#1a1a2e;background:#fff;-webkit-font-smoothing:antialiased}a{color:inherit;text-decoration:none}:root{--primary:#4d41df}.font-headline{font-family:'Bricolage Grotesque',sans-serif}.bg-primary{background:#4d41df!important}.text-primary{color:#4d41df!important}.border-primary{border-color:#4d41df!important}.container{max-width:900px;margin:0 auto;padding:0 24px}.hero{padding:120px 24px 60px;text-align:center;background:linear-gradient(180deg,#f5f2ff 0%,#fff 100%)}.eyebrow{display:inline-block;font-size:11px;font-weight:700;color:#4d41df;letter-spacing:.18em;text-transform:uppercase;background:rgba(77,65,223,.08);padding:6px 16px;border-radius:99px;margin-bottom:20px}h1{font-family:'Bricolage Grotesque',sans-serif;font-size:clamp(36px,5vw,64px);font-weight:800;line-height:1.05;letter-spacing:-.03em;color:#1a1a2e;margin-bottom:20px}h1 .accent{background:linear-gradient(135deg,#4d41df,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}.hero-sub{font-size:18px;color:#464555;max-width:680px;margin:0 auto 32px;line-height:1.6}.btn-primary{display:inline-flex;align-items:center;gap:10px;background:#4d41df;color:#fff;padding:18px 36px;border-radius:99px;font-weight:700;font-size:16px;text-decoration:none;box-shadow:0 12px 40px -8px rgba(77,65,223,.5);transition:all .2s}.btn-primary:hover{transform:translateY(-2px)}.fine-print{display:block;margin-top:14px;font-size:12px;color:#777587}section{padding:72px 24px}.section-label{font-size:11px;font-weight:700;color:#4d41df;letter-spacing:.18em;text-transform:uppercase;display:block;margin-bottom:12px}h2{font-family:'Bricolage Grotesque',sans-serif;font-size:clamp(28px,3.5vw,44px);font-weight:800;letter-spacing:-.02em;color:#1a1a2e;margin-bottom:16px}p{color:#464555;line-height:1.75;margin-bottom:14px}.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;margin-top:40px}.card{background:#fff;border:1px solid #e2e0fc;border-radius:20px;padding:28px 32px}.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:24px;margin-top:40px}.step{text-align:center;padding:32px 24px}.step-num{font-family:'Bricolage Grotesque',sans-serif;font-size:48px;font-weight:800;color:rgba(77,65,223,.15);line-height:1;margin-bottom:8px}.step-title{font-family:'Bricolage Grotesque',sans-serif;font-size:18px;font-weight:800;color:#1a1a2e;margin-bottom:8px}.math-box{background:#f5f2ff;border:1px solid rgba(77,65,223,.15);border-radius:20px;padding:32px;margin:32px 0}.math-box h3{font-family:'Bricolage Grotesque',sans-serif;font-size:16px;font-weight:800;color:#1a1a2e;margin-bottom:20px;text-transform:uppercase;letter-spacing:.05em}.math-row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px dashed rgba(77,65,223,.15);font-size:15px;color:#464555}.math-row:last-child{border:none;font-weight:800;font-size:16px;color:#4d41df;padding-top:16px;margin-top:8px;border-top:2px solid #4d41df}.faq-item{border:1px solid #e2e0fc;border-radius:16px;padding:22px 26px;margin-bottom:12px}.faq-q{font-family:'Bricolage Grotesque',sans-serif;font-size:16px;font-weight:700;color:#1a1a2e;margin-bottom:8px}.faq-a{font-size:14px;color:#464555;line-height:1.7}.testimonial{background:#1a1a2e;border-radius:24px;padding:40px;color:#fff;margin:40px 0}.testimonial blockquote{font-family:'Bricolage Grotesque',sans-serif;font-size:20px;font-style:italic;line-height:1.5;margin-bottom:24px}.testimonial cite{font-size:13px;color:rgba(255,255,255,.5);font-style:normal}.cta-block{background:#4d41df;border-radius:32px;padding:64px 40px;text-align:center;color:#fff;margin:0 24px 80px}.cta-block h2{color:#fff}.cta-block p{color:rgba(255,255,255,.75)}@media(max-width:768px){h1{font-size:36px}.hero{padding:100px 20px 40px}section{padding:48px 20px}.card-grid,.steps{grid-template-columns:1fr}}"""


def generate_page(city: dict) -> str:
    name       = city["name"]
    state      = city["state"]
    slug       = city["slug"]
    climate    = city["climate"]
    season     = city["season"]
    neighborhoods = city["neighborhoods"]
    local_detail  = city["local_detail"]
    seasonal_q    = city["seasonal_q"]
    seasonal_a    = city["seasonal_a"]
    t             = TESTIMONIALS[city["testimonial_idx"]]

    canonical = f"https://syntharra.com/hvac-answering-service-{slug}.html"
    title     = f"HVAC Answering Service {name}, {state} | AI Call Answering — Syntharra"
    desc      = (
        f"Never miss another HVAC call in {name}, {state}. Syntharra's AI answers every call "
        f"in under 3 seconds, captures full job details, and texts you instantly. "
        f"Built for {season}."
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;700;800&family=DM+Sans:wght@400;500;700&family=Material+Symbols+Outlined" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<style>
{CSS}
</style>
</head>
<body>

{NAV}

<main>

<!-- HERO -->
<section class="hero">
  <div class="container">
    <span class="eyebrow">HVAC Answering Service &mdash; {name}, {state}</span>
    <h1>Every HVAC Call in <span class="accent">{name}</span><br>Answered Instantly</h1>
    <p class="hero-sub">{climate} Your AI-powered answering service captures every lead, 24/7 — no voicemail, no missed revenue.</p>
    <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="btn-primary">
      Start Answering Every Call &rarr;
    </a>
    <span class="fine-print">No setup fees &bull; Live in 24 hours &bull; $697/mo flat</span>
  </div>
</section>

<!-- PROBLEM SECTION -->
<section style="background:#f8f8fc;">
  <div class="container">
    <span class="section-label">The Problem</span>
    <h2>Missed Calls Are Costing You Real Money in {name}</h2>
    <p>{local_detail}</p>
    <p>In {name}'s competitive HVAC market, every missed call is a direct transfer of revenue to the contractor who answers. Homeowners dealing with {season} emergencies don't leave voicemails and wait — they call the next number on their list within 60 seconds of hitting your voicemail. That job, that relationship, and every referral that comes with it goes to your competition.</p>
    <p>The math is simple and brutal. If you're missing even 3-4 calls a week — after hours, during peak season, when you're on another job — you're hemorrhaging revenue that your business will never recover.</p>

    <div class="math-box">
      <h3>The Cost of Missed Calls in {name}</h3>
      <div class="math-row"><span>Calls missed per week (conservative estimate)</span><span>4</span></div>
      <div class="math-row"><span>Average HVAC job value in {name}, {state}</span><span>$850</span></div>
      <div class="math-row"><span>Close rate on answered calls</span><span>60%</span></div>
      <div class="math-row"><span>Revenue lost per week</span><span>$2,040</span></div>
      <div class="math-row"><span>Lifetime value of a {name} client (referrals included)</span><span>$4,200+</span></div>
      <div class="math-row"><span><strong>Annual revenue walking out the door</strong></span><span>$176k&ndash;$265k</span></div>
    </div>
  </div>
</section>

<!-- HOW IT WORKS -->
<section>
  <div class="container">
    <span class="section-label">How It Works</span>
    <h2>Three Steps. Live in 24 Hours.</h2>
    <p>No hardware. No complicated setup. Syntharra plugs into your existing phone number and starts working immediately.</p>
    <div class="steps">
      <div class="step">
        <div class="step-num">01</div>
        <div class="step-title">Forward Your Number</div>
        <p>Point your existing {name} business line to Syntharra — on missed calls, after hours, or always. Takes 5 minutes.</p>
      </div>
      <div class="step">
        <div class="step-num">02</div>
        <div class="step-title">AI Answers Every Call</div>
        <p>Syntharra answers in under 3 seconds, professionally introduces your business, and captures the caller's name, address, issue, and contact info.</p>
      </div>
      <div class="step">
        <div class="step-num">03</div>
        <div class="step-title">You Get a Text Immediately</div>
        <p>The moment the call ends, you receive a complete text message with every detail — ready to call back, dispatch, or follow up.</p>
      </div>
    </div>
  </div>
</section>

<!-- FEATURES -->
<section style="background:#f8f8fc;">
  <div class="container">
    <span class="section-label">What You Get</span>
    <h2>Built for {name} HVAC Contractors</h2>
    <p>Syntharra isn't a generic answering service. It's purpose-built for HVAC businesses dealing with {season} — where speed, professionalism, and zero missed calls are non-negotiable.</p>
    <div class="card-grid">
      <div class="card">
        <div class="step-num" style="font-size:32px;text-align:left;margin-bottom:12px">&#9889;</div>
        <div class="step-title">Answered in Under 3 Seconds</div>
        <p>No rings, no hold music, no voicemail. Every caller in {name} and {neighborhoods} is greeted immediately — on the hottest day of August or the coldest night in January.</p>
      </div>
      <div class="card">
        <div class="step-num" style="font-size:32px;text-align:left;margin-bottom:12px">&#128203;</div>
        <div class="step-title">Full Job Details Captured</div>
        <p>Name, address, issue description, best callback number — Syntharra collects everything you need to dispatch or quote the job, structured and ready to act on.</p>
      </div>
      <div class="card">
        <div class="step-num" style="font-size:32px;text-align:left;margin-bottom:12px">&#128241;</div>
        <div class="step-title">Instant Text to You</div>
        <p>Every completed call generates an immediate text to your phone. You're informed of every new lead the moment it comes in — whether you're on a job in {name} or asleep at midnight.</p>
      </div>
    </div>
  </div>
</section>

<!-- TESTIMONIAL -->
<section>
  <div class="container">
    <span class="section-label">Results</span>
    <h2>What HVAC Contractors Say</h2>
    <div class="testimonial">
      <blockquote>"{t['quote']}"</blockquote>
      <cite>{t['cite']}</cite>
    </div>
  </div>
</section>

<!-- FAQ -->
<section style="background:#f8f8fc;">
  <div class="container">
    <span class="section-label">FAQ</span>
    <h2>Questions About HVAC Answering Service in {name}</h2>

    <div class="faq-item">
      <div class="faq-q">{seasonal_q}</div>
      <div class="faq-a">{seasonal_a}</div>
    </div>

    <div class="faq-item">
      <div class="faq-q">Will callers know they're talking to an AI?</div>
      <div class="faq-a">Most don't. Syntharra speaks naturally, adapts to the caller's tone, and handles the most common HVAC intake scenarios fluently. Callers get a professional, helpful experience from the first second — which is all that matters for capturing the lead.</div>
    </div>

    <div class="faq-item">
      <div class="faq-q">What happens if a caller has an unusual request?</div>
      <div class="faq-a">Syntharra captures the core contact and job information, notes that the request requires follow-up, and texts you immediately. No lead falls through the cracks. You get every caller's details regardless of whether their situation fits a standard script.</div>
    </div>

    <div class="faq-item">
      <div class="faq-q">How quickly can I get Syntharra running for my {name} HVAC business?</div>
      <div class="faq-a">Most contractors are live within 24 hours of signing up. There's no hardware to install and no complicated phone system integration. You forward your number to Syntharra, we configure your agent with your business name and details, and you start capturing every call the same day.</div>
    </div>

  </div>
</section>

<!-- CTA BLOCK -->
<div class="cta-block">
  <h2>Stop Losing {name} Jobs to Voicemail</h2>
  <p style="max-width:560px;margin:0 auto 32px;">Every call you miss is a job you'll never see. Start capturing every lead in {name} today — no setup fees, live in 24 hours.</p>
  <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="btn-primary" style="background:#fff;color:#4d41df;">
    Get Started — $697/mo &rarr;
  </a>
  <span class="fine-print" style="color:rgba(255,255,255,0.6);">Flat monthly rate &bull; No contracts &bull; Cancel anytime</span>
</div>

</main>

{FOOTER_JS}

</body>
</html>"""
    return html


def push_file(filename: str, content: str, city_name: str) -> bool:
    path = filename
    url  = f"{API}/{path}"
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    payload = {
        "message": f"feat(seo): add HVAC answering service page — {city_name}",
        "content": encoded,
    }
    resp = requests.put(url, headers=HEADERS, data=json.dumps(payload))
    if resp.status_code in (200, 201):
        print(f"  OK  {filename}  (HTTP {resp.status_code})")
        return True
    else:
        print(f"  FAIL {filename}  (HTTP {resp.status_code}) — {resp.text[:200]}")
        return False


def main():
    results = {}
    for city in CITIES:
        slug     = city["slug"]
        filename = f"hvac-answering-service-{slug}.html"
        print(f"\n[{city['name']}, {city['state']}]  ->  {filename}")
        html = generate_page(city)
        ok   = push_file(filename, html, f"{city['name']}, {city['state']}")
        results[city["name"]] = "OK" if ok else "FAIL"
        time.sleep(1.5)

    print("\n\n=== RESULTS ===")
    for city_name, status in results.items():
        print(f"  {status:4s}  {city_name}")
    ok_count   = sum(1 for s in results.values() if s == "OK")
    fail_count = len(results) - ok_count
    print(f"\n{ok_count} OK  /  {fail_count} FAIL  out of {len(results)} cities")


if __name__ == "__main__":
    main()
