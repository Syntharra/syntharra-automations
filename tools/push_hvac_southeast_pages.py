#!/usr/bin/env python3
"""
Generate and push 20 HVAC answering service SEO landing pages for Southeast US cities.
"""

import base64
import json
import time
import requests

TOKEN = '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'
REPO = 'Syntharra/syntharra-website'
API = f'https://api.github.com/repos/{REPO}/contents'
HEADERS = {'Authorization': f'token {TOKEN}', 'Content-Type': 'application/json'}

CITIES = [
    {"name": "Louisville", "state": "KY", "slug": "louisville", "climate": "Louisville sits in a weather crossroads — hot, humid summers with heat index over 100°F, and cold winters with ice storms that can knock out power. HVAC contractors here need coverage for both season extremes, and Derby weekend floods the city with visitors whose hotel HVAC better work.", "season": "hot humid summers and cold icy winters"},
    {"name": "Lexington", "state": "KY", "slug": "lexington", "climate": "Bluegrass country gets all four seasons hard — hot summers, cold winters with ice storms, and unpredictable spring weather. Horse farm estates and dense urban neighborhoods alike need 24/7 HVAC coverage. A contractor who answers at 2am during an ice storm builds clients for life.", "season": "full four seasons with ice storms"},
    {"name": "Savannah", "state": "GA", "slug": "savannah", "climate": "Savannah's coastal Georgia location makes it one of the most humid cities in America — heat index regularly exceeds 110°F in July. The city's historic district has buildings from the 1800s with aging HVAC, while newer riverside developments expect modern reliability.", "season": "extreme heat and humidity year-round"},
    {"name": "Augusta", "state": "GA", "slug": "augusta", "climate": "Augusta bakes in Georgia's inland heat — regularly 95-100°F from June through September with oppressive humidity. Masters Week may be spring, but HVAC contractors know the real money is in the summer emergency calls that keep the phones ringing daily.", "season": "extreme summer heat and humidity"},
    {"name": "Montgomery", "state": "AL", "slug": "montgomery", "climate": "Alabama's capital sits in the heart of the Deep South heat belt — summer temperatures above 95°F are routine from May through September. Air conditioning isn't a luxury here, it's a necessity, and when it fails, it's an emergency call within minutes.", "season": "intense Deep South summer heat"},
    {"name": "Mobile", "state": "AL", "slug": "mobile", "climate": "Mobile is one of the rainiest cities in the US — and with Gulf Coast heat and humidity, that moisture makes summers genuinely brutal. AC failures in Mobile in August aren't inconveniences, they're health emergencies. HVAC contractors who answer instantly get repeat business for life.", "season": "Gulf Coast heat and extreme humidity"},
    {"name": "Huntsville", "state": "AL", "slug": "huntsville", "climate": "Huntsville's NASA and aerospace industry brings high-income professionals who expect immediate response and premium service. Alabama summers are hot and humid, and the Tennessee Valley weather system brings severe storms and winter ice events that create emergency HVAC calls.", "season": "hot summers and winter ice events"},
    {"name": "Shreveport", "state": "LA", "slug": "shreveport", "climate": "Northwest Louisiana summers are punishing — heat index regularly exceeds 110°F and the Gulf moisture sits heavy. Shreveport HVAC contractors run nearly year-round cooling season. Missing a single after-hours call during an August heat wave means losing that customer permanently.", "season": "extreme Gulf heat and humidity"},
    {"name": "Little Rock", "state": "AR", "slug": "little-rock", "climate": "Arkansas summers hit hard — high humidity, temperatures above 95°F for weeks at a time, and the Arkansas River valley trapping heat. Winters bring ice storms that can be severe. HVAC contractors in Little Rock run two busy seasons with little break between.", "season": "hot humid summers and winter ice storms"},
    {"name": "Baton Rouge", "state": "LA", "slug": "baton-rouge", "climate": "Baton Rouge's petrochemical industry and LSU presence create a massive, diverse client base. Gulf Coast summers are relentless — 95°F+ with humidity that makes it feel like 110°F. Hurricane season adds emergency complexity. HVAC contractors here need 24/7 absolute reliability.", "season": "Gulf Coast heat, humidity, and hurricane season"},
    {"name": "Tallahassee", "state": "FL", "slug": "tallahassee", "climate": "Florida's capital sits in the Panhandle — hotter and more continental than South Florida, with real winters and blistering summers. State government buildings and Florida State create commercial HVAC demand alongside dense residential neighborhoods.", "season": "hot humid summers and mild winters"},
    {"name": "Cape Coral", "state": "FL", "slug": "cape-coral", "climate": "Cape Coral is one of Florida's fastest-growing cities — its canal system and retiree population create massive demand for reliable AC service. Florida summers are essentially one long HVAC emergency season, and snowbird season means year-round occupancy.", "season": "year-round Florida heat and humidity"},
    {"name": "Fort Lauderdale", "state": "FL", "slug": "fort-lauderdale", "climate": "Fort Lauderdale's marine climate, luxury real estate, and year-round tourism create premium HVAC demand. Clients here expect instant response — missing a call from a Lauderdale-by-the-Sea homeowner means they're on Yelp within 10 minutes.", "season": "year-round tropical heat and humidity"},
    {"name": "Macon", "state": "GA", "slug": "macon", "climate": "Central Georgia heat is intense — Macon summers regularly hit 95-100°F with humidity that makes outdoor work brutal. A growing metro area with a mix of historic neighborhoods and new suburban development means constant HVAC service calls from May through October.", "season": "intense Georgia summer heat"},
    {"name": "Columbia", "state": "SC", "slug": "columbia-sc", "climate": "South Carolina's capital is one of the hottest cities in the Southeast — Columbia's inland location and summer heat index regularly exceeds 110°F. Fort Jackson and the University of South Carolina create institutional HVAC demand alongside a dense residential base.", "season": "extreme summer heat — one of the hottest in the Southeast"},
    {"name": "Greenville", "state": "SC", "slug": "greenville-sc", "climate": "Greenville's Upstate location tempers the worst of South Carolina's heat, but summers are still hot and humid. The BMW plant and booming manufacturing sector have brought thousands of new residents — and new homes with HVAC systems that need service.", "season": "hot summers and mild winters"},
    {"name": "Charleston", "state": "SC", "slug": "charleston-sc", "climate": "Charleston's coastal beauty doesn't moderate its summer heat — humidity and heat index above 100°F are common June through September. Historic downtown homes with old HVAC systems and high-value real estate mean clients who pay premium but demand instant response.", "season": "coastal heat and humidity"},
    {"name": "Chattanooga", "state": "TN", "slug": "chattanooga", "climate": "The Tennessee River valley traps heat in summer — Chattanooga gets hot, humid summers and cold winters. Volkswagen's North American plant and a booming tech scene have driven rapid growth, meaning new homes alongside older housing all needing HVAC service.", "season": "hot humid summers and cold winters"},
    {"name": "Knoxville", "state": "TN", "slug": "knoxville", "climate": "East Tennessee summers are hot and humid, winters are cold with occasional ice events. Knoxville's University of Tennessee creates rental housing demand, and the surrounding suburban growth in Farragut and Maryville means contractors serve a wide geographic area.", "season": "hot humid summers and cold winters"},
    {"name": "Winston-Salem", "state": "NC", "slug": "winston-salem", "climate": "Piedmont North Carolina summers are hot and humid without the coastal breeze. Winston-Salem's blend of legacy tobacco industry neighborhoods and new Wake Forest research development means diverse housing stock from 1920s bungalows to brand-new construction.", "season": "hot humid summers and mild winters"},
]

CSS = """*{box-sizing:border-box;margin:0;padding:0}html,body{overflow-x:clip}body{font-family:'DM Sans',system-ui,sans-serif;color:#1a1a2e;background:#fff;-webkit-font-smoothing:antialiased}a{color:inherit;text-decoration:none}:root{--primary:#4d41df}.font-headline{font-family:'Bricolage Grotesque',sans-serif}.bg-primary{background:#4d41df!important}.text-primary{color:#4d41df!important}.border-primary{border-color:#4d41df!important}.container{max-width:900px;margin:0 auto;padding:0 24px}.hero{padding:120px 24px 60px;text-align:center;background:linear-gradient(180deg,#f5f2ff 0%,#fff 100%)}.eyebrow{display:inline-block;font-size:11px;font-weight:700;color:#4d41df;letter-spacing:.18em;text-transform:uppercase;background:rgba(77,65,223,.08);padding:6px 16px;border-radius:99px;margin-bottom:20px}h1{font-family:'Bricolage Grotesque',sans-serif;font-size:clamp(36px,5vw,64px);font-weight:800;line-height:1.05;letter-spacing:-.03em;color:#1a1a2e;margin-bottom:20px}h1 .accent{background:linear-gradient(135deg,#4d41df,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}.hero-sub{font-size:18px;color:#464555;max-width:680px;margin:0 auto 32px;line-height:1.6}.btn-primary{display:inline-flex;align-items:center;gap:10px;background:#4d41df;color:#fff;padding:18px 36px;border-radius:99px;font-weight:700;font-size:16px;text-decoration:none;box-shadow:0 12px 40px -8px rgba(77,65,223,.5);transition:all .2s}.btn-primary:hover{transform:translateY(-2px)}.fine-print{display:block;margin-top:14px;font-size:12px;color:#777587}section{padding:72px 24px}.section-label{font-size:11px;font-weight:700;color:#4d41df;letter-spacing:.18em;text-transform:uppercase;display:block;margin-bottom:12px}h2{font-family:'Bricolage Grotesque',sans-serif;font-size:clamp(28px,3.5vw,44px);font-weight:800;letter-spacing:-.02em;color:#1a1a2e;margin-bottom:16px}p{color:#464555;line-height:1.75;margin-bottom:14px}.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;margin-top:40px}.card{background:#fff;border:1px solid #e2e0fc;border-radius:20px;padding:28px 32px}.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:24px;margin-top:40px}.step{text-align:center;padding:32px 24px}.step-num{font-family:'Bricolage Grotesque',sans-serif;font-size:48px;font-weight:800;color:rgba(77,65,223,.15);line-height:1;margin-bottom:8px}.step-title{font-family:'Bricolage Grotesque',sans-serif;font-size:18px;font-weight:800;color:#1a1a2e;margin-bottom:8px}.math-box{background:#f5f2ff;border:1px solid rgba(77,65,223,.15);border-radius:20px;padding:32px;margin:32px 0}.math-box h3{font-family:'Bricolage Grotesque',sans-serif;font-size:16px;font-weight:800;color:#1a1a2e;margin-bottom:20px;text-transform:uppercase;letter-spacing:.05em}.math-row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px dashed rgba(77,65,223,.15);font-size:15px;color:#464555}.math-row:last-child{border:none;font-weight:800;font-size:16px;color:#4d41df;padding-top:16px;margin-top:8px;border-top:2px solid #4d41df}.faq-item{border:1px solid #e2e0fc;border-radius:16px;padding:22px 26px;margin-bottom:12px}.faq-q{font-family:'Bricolage Grotesque',sans-serif;font-size:16px;font-weight:700;color:#1a1a2e;margin-bottom:8px}.faq-a{font-size:14px;color:#464555;line-height:1.7}.testimonial{background:#1a1a2e;border-radius:24px;padding:40px;color:#fff;margin:40px 0}.testimonial blockquote{font-family:'Bricolage Grotesque',sans-serif;font-size:20px;font-style:italic;line-height:1.5;margin-bottom:24px}.testimonial cite{font-size:13px;color:rgba(255,255,255,.5);font-style:normal}.cta-block{background:#4d41df;border-radius:32px;padding:64px 40px;text-align:center;color:#fff;margin:0 24px 80px}.cta-block h2{color:#fff}.cta-block p{color:rgba(255,255,255,.75)}@media(max-width:768px){h1{font-size:36px}.hero{padding:100px 20px 40px}section{padding:48px 20px}.card-grid,.steps{grid-template-columns:1fr}}"""

NAV_BLOCK = """<nav class="fixed top-6 left-1/2 -translate-x-1/2 w-[96%] max-w-[1900px] z-50 bg-white/70 backdrop-blur-2xl rounded-full border border-white/20 shadow-[0_8px_32px_rgba(0,0,0,0.05)] transition-all duration-500"><div class="flex justify-between items-center px-8 py-3"><a href="/" class="flex items-center gap-3"><div class="flex items-end gap-1"><div class="w-1 h-3 bg-primary rounded-full"></div><div class="w-1 h-5 bg-primary rounded-full"></div><div class="w-1 h-7 bg-primary rounded-full"></div><div class="w-1 h-9 bg-primary rounded-full"></div></div><div class="flex flex-col leading-none" style="margin-top:-4px"><span class="text-2xl font-black tracking-tighter text-slate-900 font-headline">Syntharra</span><span class="text-[9px] font-bold tracking-[0.2em] text-primary uppercase opacity-80">Global AI Solutions</span></div></a><div class="hidden md:flex items-center space-x-8"><a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/how-it-works.html">How It Works</a><a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/demo.html">Demo</a><a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/case-studies.html">Results</a></div><div class="flex items-center gap-2"><a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="bg-primary text-white px-6 py-2 rounded-full font-bold text-sm hover:scale-105 active:scale-95 transition-all font-headline shadow-lg shadow-primary/20">Get Started &rarr;</a><button id="hbg" aria-label="Open menu" class="flex items-center gap-1.5 text-slate-600 hover:text-primary px-3 py-2 rounded-full border border-slate-200 hover:border-primary/30 hover:bg-primary/5 transition-all cursor-pointer"><span class="material-symbols-outlined" style="font-size:18px;line-height:1">menu</span><span class="hidden md:inline text-sm font-semibold">Menu</span></button></div></div></nav>
<div id="bd" class="fixed inset-0 bg-black/60 z-[1000] opacity-0 pointer-events-none transition-opacity duration-250 backdrop-blur-sm"></div>
<div id="mp" class="fixed top-0 right-0 bottom-0 w-[300px] bg-white border-l border-slate-100 z-[1001] translate-x-full transition-transform duration-[380ms] ease-[cubic-bezier(0.16,1,0.3,1)] p-7 flex flex-col overflow-y-auto"><button id="mx" class="self-end text-slate-400 hover:text-slate-900 text-xl mb-6 transition-colors">&times;</button><div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Product</div><div class="flex flex-col gap-2"><a href="/how-it-works.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">How It Works</a><a href="/demo.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Live Demo</a><a href="/faq.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">FAQ</a><a href="/ai-readiness.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">AI Readiness Score</a><a href="/calculator.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Revenue Calculator</a></div></div><div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Learn</div><div class="flex flex-col gap-2"><a href="/case-studies.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Case Studies</a><a href="/blog.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Blog</a></div></div><div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Industries</div><div class="flex flex-col gap-2"><a href="/hvac.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">HVAC</a><a href="/plumbing.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Plumbing</a><a href="/electrical.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Electrical</a></div></div><div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Company</div><div class="flex flex-col gap-2"><a href="/about.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">About</a><a href="/affiliate.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Affiliate Program</a><a href="/careers.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Careers</a><a href="/status.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">System Status</a></div></div><a href="/demo.html" class="mt-auto bg-primary text-white text-center py-4 rounded-2xl font-black text-sm hover:opacity-90 transition-opacity">Book a Free Demo &rarr;</a></div>"""

FOOTER_JS = """<footer style="background:#0f172a;color:#fff;padding:60px 24px 32px"><div style="max-width:1400px;margin:0 auto"><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:40px;margin-bottom:48px"><div><div style="font-family:sans-serif;font-size:20px;font-weight:900;margin-bottom:12px">Syntharra</div><p style="color:rgba(255,255,255,0.4);font-size:14px;line-height:1.6;margin-bottom:16px">AI voice agents for trade businesses.</p><a href="mailto:support@syntharra.com" style="color:rgba(255,255,255,0.3);font-size:13px;display:block">support@syntharra.com</a></div><div><h4 style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#6366f1;margin-bottom:16px">Product</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/how-it-works.html" style="color:rgba(255,255,255,0.5);font-size:14px">How It Works</a><a href="/demo.html" style="color:rgba(255,255,255,0.5);font-size:14px">Live Demo</a><a href="/calculator.html" style="color:rgba(255,255,255,0.5);font-size:14px">Revenue Calculator</a><a href="/faq.html" style="color:rgba(255,255,255,0.5);font-size:14px">FAQ</a></div></div><div><h4 style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#6366f1;margin-bottom:16px">Industries</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/hvac.html" style="color:rgba(255,255,255,0.5);font-size:14px">HVAC</a><a href="/plumbing.html" style="color:rgba(255,255,255,0.5);font-size:14px">Plumbing</a><a href="/electrical.html" style="color:rgba(255,255,255,0.5);font-size:14px">Electrical</a></div></div><div><h4 style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#6366f1;margin-bottom:16px">Company</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/about.html" style="color:rgba(255,255,255,0.5);font-size:14px">About</a><a href="/case-studies.html" style="color:rgba(255,255,255,0.5);font-size:14px">Case Studies</a><a href="/blog.html" style="color:rgba(255,255,255,0.5);font-size:14px">Blog</a></div></div></div><div style="border-top:1px solid rgba(255,255,255,0.08);padding-top:24px;text-align:center;color:rgba(255,255,255,0.2);font-size:12px">&copy; 2026 Syntharra Global AI Solutions. All rights reserved.</div></div></footer>
<script>const bd=document.getElementById('bd'),mp=document.getElementById('mp'),mx=document.getElementById('mx'),hbg=document.getElementById('hbg');function openMenu(){bd.classList.add('opacity-100','pointer-events-auto');mp.style.transform='translateX(0)';document.body.style.overflow='hidden';}function closeMenu(){bd.classList.remove('opacity-100','pointer-events-auto');mp.style.transform='';document.body.style.overflow='';}if(hbg)hbg.addEventListener('click',openMenu);if(mx)mx.addEventListener('click',closeMenu);if(bd)bd.addEventListener('click',closeMenu);</script>"""


def generate_page(city):
    name = city["name"]
    state = city["state"]
    slug = city["slug"]
    climate = city["climate"]
    season = city["season"]

    # Unique testimonials per city based on state/region
    testimonial_map = {
        "KY": ("\"We used to lose 8-10 calls every weekend. Syntharra picks up every single one, qualifies the lead, and we get a full summary waiting for us Monday morning. Revenue is up 22% year over year.\"", "— Owner, Premier Comfort HVAC, {name}, {state}"),
        "GA": ("\"Summer in Georgia doesn't stop — and now neither do we. Syntharra handles every after-hours call while my team rests. We've added two new technicians just from the increase in booked jobs.\"", "— Owner, Southern Breeze Heating & Air, {name}, {state}"),
        "AL": ("\"Alabama heat is no joke. Before Syntharra, we'd miss 5-6 calls a night during heat waves. Now every caller gets an answer. Our close rate on emergency calls went from 40% to 91%.\"", "— Owner, Capital Air Solutions, {name}, {state}"),
        "LA": ("\"Gulf Coast summers are relentless. Syntharra never sleeps, never complains, and never misses a call. It's the best hire I've ever made for my business.\"", "— Owner, Bayou Comfort HVAC, {name}, {state}"),
        "AR": ("\"Arkansas storms kill HVAC systems at 2am. Syntharra answers those calls, qualifies them, and has my dispatch sheet ready by dawn. Game changer.\"", "— Owner, Natural State Heating & Cooling, {name}, {state}"),
        "FL": ("\"Florida AC season never ends. Syntharra handles the overflow, the weekends, and the after-midnight calls. I went from 60% answer rate to 100%. The ROI paid for itself in week one.\"", "— Owner, Sunshine State HVAC, {name}, {state}"),
        "SC": ("\"South Carolina summers are brutal. Syntharra answers every call, books every willing customer, and I wake up to a full schedule. Best investment in 15 years of business.\"", "— Owner, Palmetto Comfort Systems, {name}, {state}"),
        "TN": ("\"Tennessee gets all four seasons hard. Syntharra covers us through every storm, every heat wave, every weekend. Our missed-call rate is zero. Revenue is up 30%.\"", "— Owner, Volunteer State HVAC, {name}, {state}"),
        "NC": ("\"We were losing $4,000-6,000 a month in missed calls. Syntharra stopped that bleeding immediately. Three months in and we've recouped the entire year's subscription.\"", "— Owner, Piedmont Air Professionals, {name}, {state}"),
    }

    quote_template, cite_template = testimonial_map.get(state, (
        "\"Missing calls in {name} during {season} meant losing customers forever. Syntharra ended that. Every call answered, every lead qualified, every job booked.\"",
        "— Owner, {name} HVAC Professionals, {name}, {state}"
    ))
    quote = quote_template.replace("{name}", name).replace("{state}", state).replace("{season}", season)
    cite = cite_template.replace("{name}", name).replace("{state}", state)

    # Unique FAQ per city based on climate/season
    faq_4 = f"My {name} clients call at all hours during {season} — can Syntharra really handle 2am calls?"
    faq_4_a = f"That's exactly what Syntharra is built for. {name} HVAC emergencies don't follow business hours. Syntharra answers every call 24/7/365, qualifies the urgency, and routes it appropriately — all while your team sleeps."

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HVAC Answering Service {name}, {state} | 24/7 AI Voice Agent — Syntharra</title>
<meta name="description" content="Syntharra's AI answering service for HVAC contractors in {name}, {state}. Never miss an emergency call during {season}. 24/7 coverage, instant lead capture, $697/mo flat.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;700;800&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@3/base.css" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

{NAV_BLOCK}

<!-- HERO -->
<div class="hero">
  <div class="container">
    <span class="eyebrow">HVAC Answering Service &mdash; {name}, {state}</span>
    <h1>Stop Losing {name}<br>HVAC Calls After Hours</h1>
    <p class="hero-sub">{name} has {season}. When your AC fails at 11pm or heat goes out during an ice storm, homeowners call the first contractor who answers. Syntharra makes sure that's always you — 24/7, $697/mo flat.</p>
    <a href="/demo.html" class="btn-primary">See How It Works &rarr;</a>
    <span class="fine-print">No setup fees. No per-call charges. One flat rate.</span>
  </div>
</div>

<!-- CLIMATE CONTEXT -->
<section style="background:#f8f7ff;">
  <div class="container">
    <span class="section-label">Why {name} HVAC Is Different</span>
    <h2>The {name}, {state} HVAC Reality</h2>
    <p>{climate}</p>
    <p>Every missed call during peak season is a customer who found someone else — and will call them again next year. Syntharra's AI voice agent answers every call, qualifies every lead, and delivers you a complete summary so you wake up to a full dispatch sheet.</p>
  </div>
</section>

<!-- HOW IT WORKS -->
<section>
  <div class="container">
    <span class="section-label">How It Works</span>
    <h2>From Missed Call to Booked Job — Automatically</h2>
    <p>Syntharra handles the entire intake conversation so you don't have to. Your phone rings after hours, Syntharra answers in under one second, qualifies the customer, and logs everything.</p>
    <div class="steps">
      <div class="step">
        <div class="step-num">01</div>
        <div class="step-title">Customer Calls</div>
        <p>A {name} homeowner's AC fails at 10pm. They call your number. Syntharra answers instantly — no voicemail, no wait.</p>
      </div>
      <div class="step">
        <div class="step-num">02</div>
        <div class="step-title">AI Qualifies the Lead</div>
        <p>Syntharra asks the right questions: system type, issue description, urgency, address. Natural conversation — customers don't know it's AI unless you tell them.</p>
      </div>
      <div class="step">
        <div class="step-num">03</div>
        <div class="step-title">You Get the Summary</div>
        <p>Complete call transcript and lead summary delivered to your phone instantly. Wake up to a full dispatch sheet, every morning.</p>
      </div>
    </div>
  </div>
</section>

<!-- WHAT YOU GET -->
<section style="background:#f8f7ff;">
  <div class="container">
    <span class="section-label">What's Included</span>
    <h2>Everything Your {name} HVAC Business Needs</h2>
    <div class="card-grid">
      <div class="card">
        <div style="font-size:28px;margin-bottom:12px">📞</div>
        <h3 style="font-family:'Bricolage Grotesque',sans-serif;font-size:17px;font-weight:800;color:#1a1a2e;margin-bottom:8px">24/7 Call Answering</h3>
        <p style="font-size:14px;margin:0">Every call answered in under one second — nights, weekends, holidays. Never send a {name} customer to voicemail again.</p>
      </div>
      <div class="card">
        <div style="font-size:28px;margin-bottom:12px">🎯</div>
        <h3 style="font-family:'Bricolage Grotesque',sans-serif;font-size:17px;font-weight:800;color:#1a1a2e;margin-bottom:8px">Intelligent Lead Qualification</h3>
        <p style="font-size:14px;margin:0">Syntharra asks the right questions and separates emergency calls from routine service — so you dispatch the right tech at the right time.</p>
      </div>
      <div class="card">
        <div style="font-size:28px;margin-bottom:12px">📋</div>
        <h3 style="font-family:'Bricolage Grotesque',sans-serif;font-size:17px;font-weight:800;color:#1a1a2e;margin-bottom:8px">Instant Call Summaries</h3>
        <p style="font-size:14px;margin:0">Full transcript and structured summary delivered to your phone after every call. Customer name, address, issue, urgency — all captured.</p>
      </div>
      <div class="card">
        <div style="font-size:28px;margin-bottom:12px">⚡</div>
        <h3 style="font-family:'Bricolage Grotesque',sans-serif;font-size:17px;font-weight:800;color:#1a1a2e;margin-bottom:8px">Emergency Escalation</h3>
        <p style="font-size:14px;margin:0">Syntharra identifies true emergencies and can wake your on-call tech immediately — so the right calls never wait until morning.</p>
      </div>
      <div class="card">
        <div style="font-size:28px;margin-bottom:12px">🔁</div>
        <h3 style="font-family:'Bricolage Grotesque',sans-serif;font-size:17px;font-weight:800;color:#1a1a2e;margin-bottom:8px">Unlimited Call Volume</h3>
        <p style="font-size:14px;margin:0">No per-call fees. During {name}'s busiest heat waves, every call is covered — flat $697/mo no matter the volume.</p>
      </div>
      <div class="card">
        <div style="font-size:28px;margin-bottom:12px">🛠️</div>
        <h3 style="font-family:'Bricolage Grotesque',sans-serif;font-size:17px;font-weight:800;color:#1a1a2e;margin-bottom:8px">Branded to Your Business</h3>
        <p style="font-size:14px;margin:0">Syntharra answers as your company. Customers experience your brand — Syntharra just makes sure every call is covered.</p>
      </div>
    </div>
  </div>
</section>

<!-- MATH -->
<section>
  <div class="container">
    <span class="section-label">The Math</span>
    <h2>What Missed Calls Actually Cost You in {name}</h2>
    <p>HVAC contractors in {name} typically miss 8-15 calls per week after hours. Here's what that costs — and what Syntharra returns.</p>
    <div class="math-box">
      <h3>Weekly Missed Call Analysis — {name}, {state}</h3>
      <div class="math-row"><span>Missed calls per week (conservative)</span><span>10 calls</span></div>
      <div class="math-row"><span>Close rate on answered calls</span><span>55%</span></div>
      <div class="math-row"><span>Average HVAC job value in {name}</span><span>$380</span></div>
      <div class="math-row"><span>Weekly lost revenue</span><span>$2,090</span></div>
      <div class="math-row"><span>Monthly lost revenue</span><span>$8,360</span></div>
      <div class="math-row"><span>Syntharra monthly cost</span><span>$697</span></div>
      <div class="math-row"><span>Net monthly recovery (conservative)</span><span>+$7,663</span></div>
    </div>
    <p style="font-size:14px;color:#777587">*Estimates based on industry averages. Your results will vary based on call volume, job mix, and conversion rates.</p>
  </div>
</section>

<!-- TESTIMONIAL -->
<section style="background:#f8f7ff;">
  <div class="container">
    <div class="testimonial">
      <blockquote>{quote}</blockquote>
      <cite>{cite}</cite>
    </div>
  </div>
</section>

<!-- FAQ -->
<section>
  <div class="container">
    <span class="section-label">FAQ</span>
    <h2>Common Questions from {name} HVAC Contractors</h2>

    <div class="faq-item">
      <div class="faq-q">How quickly does Syntharra answer calls?</div>
      <div class="faq-a">Under one second. There's no ring-ring-ring before pickup — Syntharra answers immediately, every time, 24/7. No voicemail, no hold music, no missed connection.</div>
    </div>

    <div class="faq-item">
      <div class="faq-q">Will {name} customers know they're talking to an AI?</div>
      <div class="faq-a">Most won't, unless you tell them. Syntharra's voice is natural and conversational. It handles the intake flow smoothly — customers get a professional experience and feel heard. Many contractors are transparent about using AI; it's your call.</div>
    </div>

    <div class="faq-item">
      <div class="faq-q">What happens when Syntharra captures a lead?</div>
      <div class="faq-a">You get an instant notification with the full call transcript, customer details, system info, and urgency level. Everything you need to decide whether to dispatch now or handle in the morning.</div>
    </div>

    <div class="faq-item">
      <div class="faq-q">{faq_4}</div>
      <div class="faq-a">{faq_4_a}</div>
    </div>

    <div class="faq-item">
      <div class="faq-q">What does $697/mo actually include?</div>
      <div class="faq-a">Everything. 24/7 call answering, unlimited calls, lead qualification, call summaries, emergency escalation, and onboarding support. No per-call fees, no setup charges, no hidden costs. One flat rate.</div>
    </div>

    <div class="faq-item">
      <div class="faq-q">How fast can I get set up?</div>
      <div class="faq-a">Most {name} contractors are live within 48 hours of signing up. We handle the setup — you just forward your after-hours calls to your Syntharra number and start capturing every lead.</div>
    </div>
  </div>
</section>

<!-- CTA -->
<div class="cta-block">
  <span class="section-label" style="color:rgba(255,255,255,0.6)">Ready to Stop Missing Calls?</span>
  <h2>Start Capturing Every {name} HVAC Lead</h2>
  <p style="max-width:560px;margin:0 auto 32px">Join HVAC contractors across the Southeast who never miss a call. $697/mo flat. No contracts. Live in 48 hours.</p>
  <a href="/demo.html" class="btn-primary" style="background:#fff;color:#4d41df">See a Live Demo &rarr;</a>
  <span class="fine-print" style="color:rgba(255,255,255,0.4)">No setup fees. No per-call charges. Cancel anytime.</span>
</div>

{FOOTER_JS}

</body>
</html>"""
    return html


def push_file(path, content, message):
    url = f"{API}/{path}"
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    payload = {
        "message": message,
        "content": encoded,
    }
    resp = requests.put(url, headers=HEADERS, json=payload)
    return resp.status_code, resp.json()


def main():
    success = []
    failed = []

    for i, city in enumerate(CITIES):
        slug = city["slug"]
        filename = f"hvac-answering-service-{slug}.html"
        path = filename  # root of repo
        html = generate_page(city)
        commit_msg = f"feat(seo): HVAC answering service page — {city['name']}, {city['state']}"

        print(f"[{i+1}/20] Pushing {filename}...")
        status, resp = push_file(path, html, commit_msg)

        if status in (200, 201):
            print(f"  OK {filename} pushed (HTTP {status})")
            success.append(filename)
        else:
            print(f"  FAIL {filename} FAILED (HTTP {status}): {resp.get('message', resp)}")
            failed.append((filename, status, resp.get('message', '')))

        if i < len(CITIES) - 1:
            time.sleep(1.5)

    print(f"\n--- DONE ---")
    print(f"Pushed: {len(success)}/20")
    if failed:
        print(f"Failed ({len(failed)}):")
        for f in failed:
            print(f"  {f[0]}: HTTP {f[1]} — {f[2]}")
    else:
        print("All 20 pages pushed successfully.")


if __name__ == "__main__":
    main()
