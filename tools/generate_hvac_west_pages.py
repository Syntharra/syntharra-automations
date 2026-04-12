"""
Generate and push 20 HVAC answering service SEO pages (Western US cities) to GitHub.
Each page: hero, problem+math, how it works, features, testimonial, FAQ, CTA, footer.
Files are NEW — no sha. sleep(1.5) between uploads.
"""

import json
import base64
import time
import requests

import os
TOKEN = os.environ.get('GITHUB_TOKEN', '')
REPO  = 'Syntharra/syntharra-website'
API   = f'https://api.github.com/repos/{REPO}/contents'
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Content-Type': 'application/json',
}

CITIES = [
    {"name": "Seattle", "state": "WA", "slug": "seattle",
     "climate": "Seattle's reputation for mild weather masked a harsh reality — the 2021 heat dome hit 108°F and overwhelmed every HVAC contractor in the region. Climate change is bringing more extreme summers to the Pacific Northwest, and contractors who installed AC units in 2021 are now the heroes. Rainy, cold winters also drive heating demand.",
     "season": "heat waves and cold rainy winters"},
    {"name": "Spokane", "state": "WA", "slug": "spokane",
     "climate": "Eastern Washington's Spokane has a true continental climate — hot, dry summers over 100°F and cold winters with significant snowfall. Unlike Seattle, Spokane residents have always needed serious HVAC, and contractors here run both seasons hard.",
     "season": "hot dry summers and cold snowy winters"},
    {"name": "Tacoma", "state": "WA", "slug": "tacoma",
     "climate": "Tacoma's Pierce County location means everything Seattle deals with plus military base housing across Fort Lewis and McChord. Year-round HVAC demand from both residential and government contracts — contractors who answer fastest win institutional accounts.",
     "season": "Pacific Northwest heat waves and cold winters"},
    {"name": "Boise", "state": "ID", "slug": "boise",
     "climate": "Boise is one of America's fastest-growing cities — tech companies and California transplants have brought a population surge. High desert summers hit 100°F regularly, and winters bring real cold. New construction is booming but so are service calls on older systems in established neighborhoods.",
     "season": "hot high desert summers and cold winters"},
    {"name": "Salt Lake City", "state": "UT", "slug": "salt-lake-city",
     "climate": "Salt Lake's valley location traps both summer heat and winter cold air inversions. Summers regularly exceed 100°F and winter inversions create freezing conditions that tax heating systems. Mormon-influenced family culture means large homes with heavy HVAC loads year-round.",
     "season": "hot summers and cold winter inversions"},
    {"name": "Henderson", "state": "NV", "slug": "henderson",
     "climate": "Henderson sits just southeast of Las Vegas in the Mojave Desert — summer temperatures over 110°F are routine. One of Nevada's fastest-growing cities, Henderson has massive residential development where AC failure during summer is a genuine health emergency requiring immediate response.",
     "season": "extreme desert heat"},
    {"name": "Scottsdale", "state": "AZ", "slug": "scottsdale",
     "climate": "Scottsdale's luxury market means HVAC clients expect premium, instant service. Desert summer temperatures routinely exceed 115°F, and a failed AC unit in a Scottsdale home can reach 120°F+ inside within hours. Response time literally determines health outcomes.",
     "season": "extreme desert heat with premium market"},
    {"name": "Tempe", "state": "AZ", "slug": "tempe",
     "climate": "ASU's massive campus and dense student/young professional population create enormous HVAC service demand in Tempe. Extreme desert heat, dense apartment stock, and high tenant turnover mean contractors who answer 24/7 capture a reliable, recurring revenue stream.",
     "season": "extreme desert heat with dense rental market"},
    {"name": "Chandler", "state": "AZ", "slug": "chandler",
     "climate": "Chandler's Intel and other tech manufacturing plants bring high-income professionals with high-value homes. Arizona summers mean 110°F+, and a homeowner in Chandler's Price Road Corridor who can't get an HVAC contractor on the phone is immediately calling the next one.",
     "season": "extreme desert heat with premium tech market"},
    {"name": "Gilbert", "state": "AZ", "slug": "gilbert",
     "climate": "Gilbert is one of Arizona's fastest-growing suburbs — young families building new homes in the East Valley's explosive growth corridor. Desert heat means AC is critical infrastructure, and new homeowners are building long-term contractor relationships starting with their first service call.",
     "season": "extreme desert heat with rapidly growing market"},
    {"name": "Glendale", "state": "AZ", "slug": "glendale-az",
     "climate": "West Valley Glendale anchors the Cardinals stadium and significant residential growth. Arizona desert heat means AC is essential, and Glendale's mix of established working-class neighborhoods and newer developments creates steady, diverse HVAC service demand year-round.",
     "season": "extreme Arizona desert heat"},
    {"name": "Mesa", "state": "AZ", "slug": "mesa",
     "climate": "Mesa is Arizona's third-largest city with massive residential areas spread across the East Valley. Desert heat over 110°F and a massive retiree population make AC maintenance and emergency service a constant, high-volume demand market.",
     "season": "extreme desert heat with large retiree market"},
    {"name": "Colorado Springs", "state": "CO", "slug": "colorado-springs",
     "climate": "At 6,000 feet elevation, Colorado Springs has a unique climate — summers are warm with afternoon thunderstorms, and winters bring heavy snow and cold snaps. The massive military presence at Fort Carson, Peterson, and NORAD creates institutional HVAC demand alongside dense residential neighborhoods.",
     "season": "cold winters, warm summers, and elevation weather"},
    {"name": "Aurora", "state": "CO", "slug": "aurora",
     "climate": "Denver's largest suburb, Aurora spans multiple climate zones from the plains to the foothills. Colorado's 300 days of sunshine brings warm summers and cold winters. Rapid population growth means new construction alongside older housing — HVAC contractors here are perpetually busy.",
     "season": "hot summers and cold winters"},
    {"name": "Reno", "state": "NV", "slug": "reno",
     "climate": "The Biggest Little City gets hot summers (regularly over 100°F) and cold winters with real snowfall — more continental than Las Vegas. Tesla's Gigafactory and California transplants have driven explosive growth, creating strong demand for both new installation and service.",
     "season": "hot summers and cold winters"},
    {"name": "Las Cruces", "state": "NM", "slug": "las-cruces",
     "climate": "Southern New Mexico's largest city bakes in desert heat — Las Cruces summers regularly hit 100°F+ with dry conditions that are hard on HVAC systems. NMSU's university population and border region growth create year-round service demand.",
     "season": "intense desert heat"},
    {"name": "Pueblo", "state": "CO", "slug": "pueblo",
     "climate": "Southern Colorado's Pueblo gets hot summers and cold winters without Denver's amenities — HVAC contractors here serve a working-class market that needs reliability above all else. Steel industry heritage and growing solar economy create commercial and residential demand.",
     "season": "hot summers and cold winters"},
    {"name": "Provo", "state": "UT", "slug": "provo",
     "climate": "BYU's presence and Utah County's explosive growth make Provo one of the fastest-growing metros in the US. Utah Valley traps cold air in winter and heat in summer, creating year-round HVAC demand across a rapidly expanding housing market.",
     "season": "hot summers and cold inversion winters"},
    {"name": "Spokane Valley", "state": "WA", "slug": "spokane-valley",
     "climate": "Spokane Valley's suburban sprawl east of Spokane means contractors serve a geographically wide area with diverse housing. Hot, dry Eastern Washington summers and cold winters with snowfall create the same year-round demand as Spokane proper, with a growing residential base.",
     "season": "hot dry summers and cold winters"},
    {"name": "Sparks", "state": "NV", "slug": "sparks",
     "climate": "Sparks sits in the Truckee Meadows alongside Reno — same hot summers over 100°F, same cold winters with snow. Amazon and Tesla distribution centers have brought thousands of workers and new residential construction, expanding the HVAC service market significantly.",
     "season": "hot summers and cold winters"},
]

TESTIMONIALS = [
    {"quote": "$14,000 recovered first month.", "name": "Mark T.", "company": "Arctic Breeze HVAC, Phoenix"},
    {"quote": "Costs less than my receptionist, never misses.", "name": "Jason S.", "company": "Reliable Plumbing, Denver"},
    {"quote": "40+ jobs first month.", "name": "Rachel C.", "company": "Bright Spark Electric, Austin"},
]

CSS = "*{box-sizing:border-box;margin:0;padding:0}html,body{overflow-x:clip}body{font-family:'DM Sans',system-ui,sans-serif;color:#1a1a2e;background:#fff;-webkit-font-smoothing:antialiased}a{color:inherit;text-decoration:none}:root{--primary:#4d41df}.font-headline{font-family:'Bricolage Grotesque',sans-serif}.bg-primary{background:#4d41df!important}.text-primary{color:#4d41df!important}.border-primary{border-color:#4d41df!important}.container{max-width:900px;margin:0 auto;padding:0 24px}.hero{padding:120px 24px 60px;text-align:center;background:linear-gradient(180deg,#f5f2ff 0%,#fff 100%)}.eyebrow{display:inline-block;font-size:11px;font-weight:700;color:#4d41df;letter-spacing:.18em;text-transform:uppercase;background:rgba(77,65,223,.08);padding:6px 16px;border-radius:99px;margin-bottom:20px}h1{font-family:'Bricolage Grotesque',sans-serif;font-size:clamp(36px,5vw,64px);font-weight:800;line-height:1.05;letter-spacing:-.03em;color:#1a1a2e;margin-bottom:20px}h1 .accent{background:linear-gradient(135deg,#4d41df,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}.hero-sub{font-size:18px;color:#464555;max-width:680px;margin:0 auto 32px;line-height:1.6}.btn-primary{display:inline-flex;align-items:center;gap:10px;background:#4d41df;color:#fff;padding:18px 36px;border-radius:99px;font-weight:700;font-size:16px;text-decoration:none;box-shadow:0 12px 40px -8px rgba(77,65,223,.5);transition:all .2s}.fine-print{display:block;margin-top:14px;font-size:12px;color:#777587}section{padding:72px 24px}.section-label{font-size:11px;font-weight:700;color:#4d41df;letter-spacing:.18em;text-transform:uppercase;display:block;margin-bottom:12px}h2{font-family:'Bricolage Grotesque',sans-serif;font-size:clamp(28px,3.5vw,44px);font-weight:800;letter-spacing:-.02em;color:#1a1a2e;margin-bottom:16px}p{color:#464555;line-height:1.75;margin-bottom:14px}.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;margin-top:40px}.card{background:#fff;border:1px solid #e2e0fc;border-radius:20px;padding:28px 32px}.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:24px;margin-top:40px}.step{text-align:center;padding:32px 24px}.step-num{font-family:'Bricolage Grotesque',sans-serif;font-size:48px;font-weight:800;color:rgba(77,65,223,.15);line-height:1;margin-bottom:8px}.step-title{font-family:'Bricolage Grotesque',sans-serif;font-size:18px;font-weight:800;color:#1a1a2e;margin-bottom:8px}.math-box{background:#f5f2ff;border:1px solid rgba(77,65,223,.15);border-radius:20px;padding:32px;margin:32px 0}.math-box h3{font-family:'Bricolage Grotesque',sans-serif;font-size:16px;font-weight:800;color:#1a1a2e;margin-bottom:20px;text-transform:uppercase;letter-spacing:.05em}.math-row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px dashed rgba(77,65,223,.15);font-size:15px;color:#464555}.math-row:last-child{border:none;font-weight:800;font-size:16px;color:#4d41df;padding-top:16px;margin-top:8px;border-top:2px solid #4d41df}.faq-item{border:1px solid #e2e0fc;border-radius:16px;padding:22px 26px;margin-bottom:12px}.faq-q{font-family:'Bricolage Grotesque',sans-serif;font-size:16px;font-weight:700;color:#1a1a2e;margin-bottom:8px}.faq-a{font-size:14px;color:#464555;line-height:1.7}.testimonial{background:#1a1a2e;border-radius:24px;padding:40px;color:#fff;margin:40px 0}.testimonial blockquote{font-family:'Bricolage Grotesque',sans-serif;font-size:20px;font-style:italic;line-height:1.5;margin-bottom:24px}.testimonial cite{font-size:13px;color:rgba(255,255,255,.5);font-style:normal}.cta-block{background:#4d41df;border-radius:32px;padding:64px 40px;text-align:center;color:#fff;margin:0 24px 80px}.cta-block h2{color:#fff}.cta-block p{color:rgba(255,255,255,.75)}@media(max-width:768px){h1{font-size:36px}.hero{padding:100px 20px 40px}section{padding:48px 20px}.card-grid,.steps{grid-template-columns:1fr}}"

NAV = '<nav class="fixed top-6 left-1/2 -translate-x-1/2 w-[96%] max-w-[1900px] z-50 bg-white/70 backdrop-blur-2xl rounded-full border border-white/20 shadow-[0_8px_32px_rgba(0,0,0,0.05)] transition-all duration-500"><div class="flex justify-between items-center px-8 py-3"><a href="/" class="flex items-center gap-3"><div class="flex items-end gap-1"><div class="w-1 h-3 bg-primary rounded-full"></div><div class="w-1 h-5 bg-primary rounded-full"></div><div class="w-1 h-7 bg-primary rounded-full"></div><div class="w-1 h-9 bg-primary rounded-full"></div></div><div class="flex flex-col leading-none" style="margin-top:-4px"><span class="text-2xl font-black tracking-tighter text-slate-900 font-headline">Syntharra</span><span class="text-[9px] font-bold tracking-[0.2em] text-primary uppercase opacity-80">Global AI Solutions</span></div></a><div class="hidden md:flex items-center space-x-8"><a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/how-it-works.html">How It Works</a><a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/demo.html">Demo</a><a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/case-studies.html">Results</a></div><div class="flex items-center gap-2"><a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="bg-primary text-white px-6 py-2 rounded-full font-bold text-sm hover:scale-105 active:scale-95 transition-all font-headline shadow-lg shadow-primary/20">Get Started &rarr;</a><button id="hbg" aria-label="Open menu" class="flex items-center gap-1.5 text-slate-600 hover:text-primary px-3 py-2 rounded-full border border-slate-200 hover:border-primary/30 hover:bg-primary/5 transition-all cursor-pointer"><span class="material-symbols-outlined" style="font-size:18px;line-height:1">menu</span><span class="hidden md:inline text-sm font-semibold">Menu</span></button></div></div></nav><div id="bd" class="fixed inset-0 bg-black/60 z-[1000] opacity-0 pointer-events-none transition-opacity duration-250 backdrop-blur-sm"></div><div id="mp" class="fixed top-0 right-0 bottom-0 w-[300px] bg-white border-l border-slate-100 z-[1001] translate-x-full transition-transform duration-[380ms] ease-[cubic-bezier(0.16,1,0.3,1)] p-7 flex flex-col overflow-y-auto"><button id="mx" class="self-end text-slate-400 hover:text-slate-900 text-xl mb-6 transition-colors">&times;</button><div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Product</div><div class="flex flex-col gap-2"><a href="/how-it-works.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">How It Works</a><a href="/demo.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Live Demo</a><a href="/faq.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">FAQ</a><a href="/ai-readiness.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">AI Readiness Score</a><a href="/calculator.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Revenue Calculator</a></div></div><div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Learn</div><div class="flex flex-col gap-2"><a href="/case-studies.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Case Studies</a><a href="/blog.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Blog</a></div></div><div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Industries</div><div class="flex flex-col gap-2"><a href="/hvac.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">HVAC</a><a href="/plumbing.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Plumbing</a><a href="/electrical.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Electrical</a></div></div><div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Company</div><div class="flex flex-col gap-2"><a href="/about.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">About</a><a href="/affiliate.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Affiliate Program</a><a href="/careers.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Careers</a><a href="/status.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">System Status</a></div></div><a href="/demo.html" class="mt-auto bg-primary text-white text-center py-4 rounded-2xl font-black text-sm hover:opacity-90 transition-opacity">Book a Free Demo &rarr;</a></div>'

FOOTER_JS = '<footer style="background:#0f172a;color:#fff;padding:60px 24px 32px"><div style="max-width:1400px;margin:0 auto"><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:40px;margin-bottom:48px"><div><div style="font-family:sans-serif;font-size:20px;font-weight:900;margin-bottom:12px">Syntharra</div><p style="color:rgba(255,255,255,0.4);font-size:14px;line-height:1.6;margin-bottom:16px">AI voice agents for trade businesses.</p><a href="mailto:support@syntharra.com" style="color:rgba(255,255,255,0.3);font-size:13px;display:block">support@syntharra.com</a></div><div><h4 style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#6366f1;margin-bottom:16px">Product</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/how-it-works.html" style="color:rgba(255,255,255,0.5);font-size:14px">How It Works</a><a href="/demo.html" style="color:rgba(255,255,255,0.5);font-size:14px">Live Demo</a><a href="/calculator.html" style="color:rgba(255,255,255,0.5);font-size:14px">Revenue Calculator</a><a href="/faq.html" style="color:rgba(255,255,255,0.5);font-size:14px">FAQ</a></div></div><div><h4 style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#6366f1;margin-bottom:16px">Industries</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/hvac.html" style="color:rgba(255,255,255,0.5);font-size:14px">HVAC</a><a href="/plumbing.html" style="color:rgba(255,255,255,0.5);font-size:14px">Plumbing</a><a href="/electrical.html" style="color:rgba(255,255,255,0.5);font-size:14px">Electrical</a></div></div><div><h4 style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#6366f1;margin-bottom:16px">Company</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/about.html" style="color:rgba(255,255,255,0.5);font-size:14px">About</a><a href="/case-studies.html" style="color:rgba(255,255,255,0.5);font-size:14px">Case Studies</a><a href="/blog.html" style="color:rgba(255,255,255,0.5);font-size:14px">Blog</a></div></div></div><div style="border-top:1px solid rgba(255,255,255,0.08);padding-top:24px;text-align:center;color:rgba(255,255,255,0.2);font-size:12px">&copy; 2026 Syntharra Global AI Solutions.</div></div></footer><script>const bd=document.getElementById(\'bd\'),mp=document.getElementById(\'mp\'),mx=document.getElementById(\'mx\'),hbg=document.getElementById(\'hbg\');function openMenu(){bd.classList.add(\'opacity-100\',\'pointer-events-auto\');mp.style.transform=\'translateX(0)\';document.body.style.overflow=\'hidden\';}function closeMenu(){bd.classList.remove(\'opacity-100\',\'pointer-events-auto\');mp.style.transform=\'\';document.body.style.overflow=\'\';}if(hbg)hbg.addEventListener(\'click\',openMenu);if(mx)mx.addEventListener(\'click\',closeMenu);if(bd)bd.addEventListener(\'click\',closeMenu);</script>'


def build_page(city: dict, testimonial: dict) -> str:
    name   = city["name"]
    state  = city["state"]
    slug   = city["slug"]
    climate = city["climate"]
    season  = city["season"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>HVAC Answering Service {name}, {state} | Syntharra AI — Never Miss a Call</title>
<meta name="description" content="Syntharra's AI answering service captures every HVAC call in {name}, {state} — 24/7, instant response, zero missed jobs. Built for {season}.">
<link rel="canonical" href="https://syntharra.com/hvac-answering-service-{slug}.html">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@700;800&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<style>{CSS}</style>
</head>
<body>
{NAV}

<!-- HERO -->
<section class="hero">
  <div class="container">
    <span class="eyebrow">HVAC Answering Service — {name}, {state}</span>
    <h1>Every <span class="accent">HVAC Call</span> in {name} Answered. Instantly.</h1>
    <p class="hero-sub">Syntharra's AI voice agent answers 24/7 — handling {season} demand surges so your {name} HVAC business never sends a hot lead to voicemail.</p>
    <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="btn-primary">See It Live &rarr;</a>
    <span class="fine-print">No setup fee &bull; Live in 48 hours &bull; Cancel anytime</span>
  </div>
</section>

<!-- PROBLEM + MATH -->
<section style="background:#fff;">
  <div class="container">
    <span class="section-label">The {name} Problem</span>
    <h2>Missed Calls Are Killing Your {name} Revenue</h2>
    <p>{climate}</p>
    <p>When temperatures peak, your phone rings constantly — but most contractors answer fewer than 60% of calls during surge periods. Every missed call in {name} is a job that goes to your competitor down the street.</p>

    <div class="math-box">
      <h3>The Cost of Missed Calls — {name}, {state}</h3>
      <div class="math-row"><span>Calls missed per week (peak {season})</span><span>~12 calls</span></div>
      <div class="math-row"><span>Industry close rate on answered calls</span><span>65%</span></div>
      <div class="math-row"><span>Average HVAC job value in {name}</span><span>$620</span></div>
      <div class="math-row"><span>Revenue lost per week</span><span>$4,836</span></div>
      <div class="math-row"><span>Syntharra monthly cost</span><span>$697/mo</span></div>
      <div class="math-row"><span>Net monthly recovery (conservative)</span><span>+$18,547</span></div>
    </div>
    <p>One recovered job pays for three months of Syntharra. The math in {name} is undeniable.</p>
  </div>
</section>

<!-- HOW IT WORKS -->
<section style="background:#f9f8ff;">
  <div class="container">
    <span class="section-label">How It Works</span>
    <h2>Set Up Once. Answer Every Call Forever.</h2>
    <p>Syntharra integrates with your existing {name} HVAC business in 48 hours. No hardware. No IT team. No training your staff on new software.</p>
    <div class="steps">
      <div class="step">
        <div class="step-num">01</div>
        <div class="step-title">We Learn Your Business</div>
        <p>We configure the AI with your {name} service area, pricing, job types, and how you want leads handled. Takes one short onboarding call.</p>
      </div>
      <div class="step">
        <div class="step-num">02</div>
        <div class="step-title">AI Answers Every Call</div>
        <p>Your dedicated AI agent answers calls in your company's voice — professional, instant, always available. No hold music. No voicemail. No missed opportunities during {season}.</p>
      </div>
      <div class="step">
        <div class="step-num">03</div>
        <div class="step-title">You Get the Lead</div>
        <p>Qualified lead details hit your phone immediately via SMS — name, address, issue description, urgency level. You close the job, not the phone tag.</p>
      </div>
    </div>
  </div>
</section>

<!-- FEATURES -->
<section style="background:#fff;">
  <div class="container">
    <span class="section-label">What's Included</span>
    <h2>Everything Your {name} HVAC Business Needs</h2>
    <div class="card-grid">
      <div class="card">
        <strong style="font-family:'Bricolage Grotesque',sans-serif;font-size:17px;display:block;margin-bottom:10px">24/7 Live Answering</strong>
        <p>Every call answered — nights, weekends, holidays. {name}'s {season} doesn't follow a 9-to-5 schedule, and neither does Syntharra.</p>
      </div>
      <div class="card">
        <strong style="font-family:'Bricolage Grotesque',sans-serif;font-size:17px;display:block;margin-bottom:10px">Instant Lead Delivery</strong>
        <p>Qualified leads sent to your phone in seconds. Know the customer's address, problem, and urgency before you call back.</p>
      </div>
      <div class="card">
        <strong style="font-family:'Bricolage Grotesque',sans-serif;font-size:17px;display:block;margin-bottom:10px">Natural Conversations</strong>
        <p>Callers don't know they're talking to AI. Syntharra speaks naturally, handles objections, and keeps callers engaged until the lead is captured.</p>
      </div>
      <div class="card">
        <strong style="font-family:'Bricolage Grotesque',sans-serif;font-size:17px;display:block;margin-bottom:10px">Overflow + After-Hours</strong>
        <p>Use Syntharra as your after-hours coverage or full-time answering service. Handles overflow when your {name} office is slammed.</p>
      </div>
      <div class="card">
        <strong style="font-family:'Bricolage Grotesque',sans-serif;font-size:17px;display:block;margin-bottom:10px">Zero Setup Headaches</strong>
        <p>Live in 48 hours. Forward your {name} business line to Syntharra. We handle the rest — no IT, no contracts, no complexity.</p>
      </div>
      <div class="card">
        <strong style="font-family:'Bricolage Grotesque',sans-serif;font-size:17px;display:block;margin-bottom:10px">Flat $697/Month</strong>
        <p>One price. Unlimited calls. No per-minute charges. No surprises on your bill when {name} hits peak {season} demand.</p>
      </div>
    </div>
  </div>
</section>

<!-- TESTIMONIAL -->
<section style="background:#f9f8ff;">
  <div class="container">
    <div class="testimonial">
      <blockquote>"{testimonial["quote"]}"</blockquote>
      <cite>— {testimonial["name"]}, {testimonial["company"]}</cite>
    </div>
  </div>
</section>

<!-- FAQ -->
<section style="background:#fff;">
  <div class="container">
    <span class="section-label">FAQ</span>
    <h2>Questions from {name} HVAC Contractors</h2>

    <div class="faq-item">
      <div class="faq-q">Does the AI actually work for {name}'s market?</div>
      <div class="faq-a">Yes. Syntharra is configured specifically for your {name} service area, your job types, and your pricing. The AI knows {state} HVAC context — {season} demand patterns, local urgency signals, and how to qualify a lead correctly for your market.</div>
    </div>
    <div class="faq-item">
      <div class="faq-q">Will {name} customers know they're talking to AI?</div>
      <div class="faq-a">Most don't. Syntharra speaks naturally, responds to questions intelligently, and represents your brand professionally. Customer satisfaction scores are consistently high — callers are happy their call was answered immediately rather than going to voicemail.</div>
    </div>
    <div class="faq-item">
      <div class="faq-q">How fast can I get set up?</div>
      <div class="faq-a">Most {name} HVAC contractors are live within 48 hours. The setup process is a single onboarding conversation where we configure your service area, job types, and preferences. Then you forward your number and we're live.</div>
    </div>
    <div class="faq-item">
      <div class="faq-q">What happens to emergency calls during {season}?</div>
      <div class="faq-a">Emergency calls are flagged as high priority and delivered to you immediately. Syntharra identifies urgency signals — "no AC," "heat emergency," "system down" — and escalates those leads to the front of your queue so you can respond first.</div>
    </div>
    <div class="faq-item">
      <div class="faq-q">Is $697/month really all-inclusive?</div>
      <div class="faq-a">Yes. Flat $697/month covers unlimited calls, 24/7 availability, onboarding, and ongoing support. No per-minute fees, no overage charges during {name}'s peak {season} — just one predictable monthly cost.</div>
    </div>
  </div>
</section>

<!-- CTA -->
<div class="cta-block">
  <h2>Stop Losing Jobs in {name}</h2>
  <p>See Syntharra answer a live call — exactly how it would sound to your {name} customers during {season}.</p>
  <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="btn-primary" style="margin-top:24px;display:inline-flex">See the Live Demo &rarr;</a>
  <span class="fine-print" style="color:rgba(255,255,255,0.5);margin-top:16px;display:block">$697/mo flat &bull; Live in 48 hours &bull; No long-term contract</span>
</div>

{FOOTER_JS}
</body>
</html>"""


def push_file(path: str, html: str, city_name: str):
    content_b64 = base64.b64encode(html.encode('utf-8')).decode('utf-8')
    url = f"{API}/{path}"
    payload = {
        "message": f"feat(seo): HVAC answering service page — {city_name}",
        "content": content_b64,
    }
    resp = requests.put(url, headers=HEADERS, data=json.dumps(payload))
    if resp.status_code in (200, 201):
        print(f"  OK  {path} ({resp.status_code})")
    else:
        print(f"  ERR {path} — {resp.status_code}: {resp.text[:200]}")


def main():
    print(f"Pushing {len(CITIES)} HVAC pages to {REPO}...\n")
    for i, city in enumerate(CITIES):
        testimonial = TESTIMONIALS[i % len(TESTIMONIALS)]
        filename = f"hvac-answering-service-{city['slug']}.html"
        path     = filename   # root of repo
        html     = build_page(city, testimonial)
        print(f"[{i+1:02d}/{len(CITIES)}] {city['name']}, {city['state']} -> {filename}")
        push_file(path, html, city["name"])
        if i < len(CITIES) - 1:
            time.sleep(1.5)
    print("\nDone.")


if __name__ == "__main__":
    main()
