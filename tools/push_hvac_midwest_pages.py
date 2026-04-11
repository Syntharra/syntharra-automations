#!/usr/bin/env python3
"""
Push 20 Midwest HVAC answering service SEO landing pages to Syntharra website GitHub repo.
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
    {"name": "Chicago", "state": "IL", "slug": "chicago", "climate": "Chicago's brutal winters and humid summers create year-round HVAC demand — furnace emergencies in January, AC failures in July. With 2.7 million residents and some of the country's oldest housing stock, HVAC contractors here can't afford to miss a single call.", "season": "brutal winters and humid summers"},
    {"name": "Detroit", "state": "MI", "slug": "detroit", "climate": "Metro Detroit's cold winters — regularly below 0°F with wind chill — mean furnace failures are genuine emergencies. Contractors serving Wayne, Oakland, and Macomb counties need 24/7 call coverage from November through March.", "season": "severe winters and summer humidity"},
    {"name": "Minneapolis", "state": "MN", "slug": "minneapolis", "climate": "Minneapolis has some of the harshest winters in the continental US — wind chills of -30°F are common. A furnace failure at 2am isn't an inconvenience, it's a life-safety emergency. HVAC contractors who miss those calls lose clients permanently.", "season": "extreme winters and warm summers"},
    {"name": "Milwaukee", "state": "WI", "slug": "milwaukee", "climate": "Lake Michigan's moderating effect doesn't prevent Milwaukee's fierce winters and humid summers. Old housing stock throughout the city means constant HVAC repair demand — contractors are busy 12 months a year.", "season": "cold winters and humid summers"},
    {"name": "Omaha", "state": "NE", "slug": "omaha", "climate": "Omaha sits in the heart of the Great Plains with extreme temperature swings — summer heat in the 100s and winter cold below 0°F. HVAC contractors here run both heating and cooling seasons at full capacity with minimal downtime.", "season": "extreme seasonal swings"},
    {"name": "Kansas City", "state": "MO", "slug": "kansas-city", "climate": "Kansas City's central location brings scorching humid summers and cold icy winters. HVAC contractors serve a massive metro area spanning both Missouri and Kansas — and during weather events, every second of missed call time means lost revenue.", "season": "hot humid summers and cold winters"},
    {"name": "St. Louis", "state": "MO", "slug": "st-louis", "climate": "St. Louis has some of the most oppressive summer humidity in the Midwest — heat index regularly exceeds 105°F. Combined with cold winters, HVAC contractors run two full busy seasons every year. Missing after-hours calls during a heat wave is simply not an option.", "season": "oppressive summer humidity and cold winters"},
    {"name": "Cincinnati", "state": "OH", "slug": "cincinnati", "climate": "Cincinnati's Ohio Valley humidity makes summers brutal and winters damp and cold. Older neighborhoods like Hyde Park, Mt. Lookout, and College Hill have aging HVAC systems that need constant attention — and their owners expect answers 24/7.", "season": "humid summers and cold damp winters"},
    {"name": "Cleveland", "state": "OH", "slug": "cleveland", "climate": "Lake Erie delivers brutal lake-effect winters and humid summers to Cleveland. Furnace failures during January blizzards are emergency calls — HVAC contractors who don't answer lose those customers permanently to competitors who do.", "season": "lake-effect winters and humid summers"},
    {"name": "Pittsburgh", "state": "PA", "slug": "pittsburgh", "climate": "Pittsburgh's hilly terrain and unpredictable weather — cold wet winters, humid summers — create constant HVAC demand. The city's Renaissance-era housing stock means older systems that break down frequently.", "season": "cold wet winters and humid summers"},
    {"name": "Toledo", "state": "OH", "slug": "toledo", "climate": "Toledo's Lake Erie proximity brings harsh winters and humid summers. HVAC contractors serving the Toledo metro need full-time call coverage — emergency heating calls in winter and AC failures in summer hit simultaneously with competitors' phones.", "season": "harsh winters and humid summers"},
    {"name": "Akron", "state": "OH", "slug": "akron", "climate": "Northeast Ohio winters are relentless — Akron averages 50 inches of snow annually. Furnace emergencies pile up December through March, and the summer humidity drives AC service calls. HVAC contractors here need 24/7 coverage or they're handing revenue to competitors.", "season": "heavy snow winters and humid summers"},
    {"name": "Dayton", "state": "OH", "slug": "dayton", "climate": "Dayton sits in the Miami Valley where cold continental air meets Gulf moisture — creating cold wet winters and humid summers. A city of working-class neighborhoods with aging housing means frequent HVAC service calls year-round.", "season": "cold winters and humid summers"},
    {"name": "Grand Rapids", "state": "MI", "slug": "grand-rapids", "climate": "Grand Rapids gets significant lake-effect snow from Lake Michigan — 75 inches annually — and humid summers. With a growing metro and a mix of old and new housing, HVAC demand is year-round and contractors who answer fastest win the business.", "season": "lake-effect snow and warm summers"},
    {"name": "Wichita", "state": "KS", "slug": "wichita", "climate": "Wichita's Great Plains location means extreme weather in both directions — summer heat regularly exceeds 100°F and winter blizzards are common. HVAC contractors serve one of the most weather-volatile markets in the US.", "season": "extreme heat and cold weather swings"},
    {"name": "Des Moines", "state": "IA", "slug": "des-moines", "climate": "Iowa's capital sees brutal winters and hot humid summers. Des Moines HVAC contractors run furnace season from October through April and AC season from June through September — with very little downtime between. Missing calls in either season is costly.", "season": "harsh winters and hot humid summers"},
    {"name": "Lincoln", "state": "NE", "slug": "lincoln", "climate": "Lincoln's Great Plains climate delivers hot summers, cold winters, and sudden severe weather. Nebraska HVAC contractors serve a city that grew 15% in a decade — new construction alongside old housing stock means diverse, constant demand.", "season": "hot summers and cold harsh winters"},
    {"name": "Sioux Falls", "state": "SD", "slug": "sioux-falls", "climate": "Sioux Falls is one of the fastest-growing cities in the US, with brutal South Dakota winters and hot summers. New construction is booming, but HVAC contractors servicing older neighborhoods face constant demand — especially during subzero cold snaps.", "season": "extreme winters and hot summers"},
    {"name": "Rockford", "state": "IL", "slug": "rockford", "climate": "Northern Illinois winters hit Rockford hard — significant snowfall and wind chills below -20°F are common. HVAC contractors here run a heavy furnace season and a busy cooling season. Every missed call during a cold snap is a customer gone permanently.", "season": "severe winters and warm summers"},
    {"name": "Madison", "state": "WI", "slug": "madison", "climate": "Wisconsin winters are harsh everywhere, and Madison is no exception. The college town also drives year-round rental HVAC demand — landlords and property managers need contractors who answer immediately when tenants call about heating or cooling failures.", "season": "harsh winters and warm summers"},
]

TESTIMONIALS = [
    {
        "quote": "I used to lose 3–4 calls a week to voicemail. Now Syntharra grabs every one and I get a text in seconds. My close rate on after-hours calls went from zero to almost 80%.",
        "cite": "— Marcus R., HVAC contractor, Ohio"
    },
    {
        "quote": "During our last cold snap I had calls coming in at 11pm, 2am, 6am. Syntharra answered all of them. I woke up to a full list of leads instead of a full voicemail box.",
        "cite": "— Sarah K., HVAC contractor, Illinois"
    },
    {
        "quote": "Setup took less than an hour. I forwarded my number, ran a test call, and it worked perfectly. The AI sounds professional and actually gets the details right every time.",
        "cite": "— Derek T., HVAC contractor, Michigan"
    },
]

CSS = """*{box-sizing:border-box;margin:0;padding:0}
html,body{overflow-x:clip}
body{font-family:'DM Sans','Inter',system-ui,sans-serif;color:#1a1a2e;background:#fff;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
:root{--primary:#4d41df}
.font-headline{font-family:'Bricolage Grotesque',sans-serif}
.bg-primary{background:#4d41df!important}
.text-primary{color:#4d41df!important}
.border-primary{border-color:#4d41df!important}
.container{max-width:900px;margin:0 auto;padding:0 24px}
.max-width-container{max-width:1400px}
.hero{padding:120px 24px 60px;text-align:center;background:linear-gradient(180deg,#f5f2ff 0%,#fff 100%)}
.eyebrow{display:inline-block;font-size:11px;font-weight:700;color:#4d41df;letter-spacing:.18em;text-transform:uppercase;background:rgba(77,65,223,.08);padding:6px 16px;border-radius:99px;margin-bottom:20px}
h1{font-family:'Bricolage Grotesque',sans-serif;font-size:clamp(36px,5vw,64px);font-weight:800;line-height:1.05;letter-spacing:-.03em;color:#1a1a2e;margin-bottom:20px}
h1 .accent{background:linear-gradient(135deg,#4d41df,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero-sub{font-size:18px;color:#464555;max-width:680px;margin:0 auto 32px;line-height:1.6}
.btn-primary{display:inline-flex;align-items:center;gap:10px;background:#4d41df;color:#fff;padding:18px 36px;border-radius:99px;font-weight:700;font-size:16px;text-decoration:none;box-shadow:0 12px 40px -8px rgba(77,65,223,.5);transition:all .2s}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 18px 48px -8px rgba(77,65,223,.65)}
.fine-print{display:block;margin-top:14px;font-size:12px;color:#777587}
section{padding:72px 24px}
.section-label{font-size:11px;font-weight:700;color:#4d41df;letter-spacing:.18em;text-transform:uppercase;display:block;margin-bottom:12px}
h2{font-family:'Bricolage Grotesque',sans-serif;font-size:clamp(28px,3.5vw,44px);font-weight:800;letter-spacing:-.02em;color:#1a1a2e;margin-bottom:16px}
p{color:#464555;line-height:1.75;margin-bottom:14px}
.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;margin-top:40px}
.card{background:#fff;border:1px solid #e2e0fc;border-radius:20px;padding:28px 32px}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:24px;margin-top:40px}
.step{text-align:center;padding:32px 24px}
.step-num{font-family:'Bricolage Grotesque',sans-serif;font-size:48px;font-weight:800;color:rgba(77,65,223,.15);line-height:1;margin-bottom:8px}
.step-title{font-family:'Bricolage Grotesque',sans-serif;font-size:18px;font-weight:800;color:#1a1a2e;margin-bottom:8px}
.math-box{background:#f5f2ff;border:1px solid rgba(77,65,223,.15);border-radius:20px;padding:32px;margin:32px 0}
.math-box h3{font-family:'Bricolage Grotesque',sans-serif;font-size:16px;font-weight:800;color:#1a1a2e;margin-bottom:20px;text-transform:uppercase;letter-spacing:.05em}
.math-row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px dashed rgba(77,65,223,.15);font-size:15px;color:#464555}
.math-row:last-child{border:none;font-weight:800;font-size:16px;color:#4d41df;padding-top:16px;margin-top:8px;border-top:2px solid #4d41df}
.faq-item{border:1px solid #e2e0fc;border-radius:16px;padding:22px 26px;margin-bottom:12px}
.faq-q{font-family:'Bricolage Grotesque',sans-serif;font-size:16px;font-weight:700;color:#1a1a2e;margin-bottom:8px}
.faq-a{font-size:14px;color:#464555;line-height:1.7}
.testimonial{background:#1a1a2e;border-radius:24px;padding:40px;color:#fff;margin:40px 0}
.testimonial blockquote{font-family:'Bricolage Grotesque',sans-serif;font-size:20px;font-style:italic;line-height:1.5;margin-bottom:24px}
.testimonial cite{font-size:13px;color:rgba(255,255,255,.5);font-style:normal}
.cta-block{background:#4d41df;border-radius:32px;padding:64px 40px;text-align:center;color:#fff;margin:0 24px 80px}
.cta-block h2{color:#fff}
.cta-block p{color:rgba(255,255,255,.75)}
@media(max-width:768px){h1{font-size:36px}.hero{padding:100px 20px 40px}section{padding:48px 20px}.card-grid,.steps{grid-template-columns:1fr}}"""

NAV_BLOCK = """<!-- FLOATING NAV -->
<nav class="fixed top-6 left-1/2 -translate-x-1/2 w-[96%] max-w-[1900px] z-50 bg-white/70 backdrop-blur-2xl rounded-full border border-white/20 shadow-[0_8px_32px_rgba(0,0,0,0.05)] transition-all duration-500">
  <div class="flex justify-between items-center px-8 py-3">
    <a href="/" class="flex items-center gap-3">
      <div class="flex items-end gap-1"><div class="w-1 h-3 bg-primary rounded-full"></div><div class="w-1 h-5 bg-primary rounded-full"></div><div class="w-1 h-7 bg-primary rounded-full"></div><div class="w-1 h-9 bg-primary rounded-full"></div></div>
      <div class="flex flex-col leading-none" style="margin-top:-4px"><span class="text-2xl font-black tracking-tighter text-slate-900 font-headline">Syntharra</span><span class="text-[9px] font-bold tracking-[0.2em] text-primary uppercase opacity-80">Global AI Solutions</span></div>
    </a>
    <div class="hidden md:flex items-center space-x-8">
      <a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/how-it-works.html">How It Works</a>
      <a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/demo.html">Demo</a>
      <a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/case-studies.html">Results</a>
    </div>
    <div class="flex items-center gap-2">
      <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="bg-primary text-white px-6 py-2 rounded-full font-bold text-sm hover:scale-105 active:scale-95 transition-all font-headline shadow-lg shadow-primary/20">Get Started &rarr;</a>
      <button id="hbg" aria-label="Open menu" class="flex items-center gap-1.5 text-slate-600 hover:text-primary px-3 py-2 rounded-full border border-slate-200 hover:border-primary/30 hover:bg-primary/5 transition-all cursor-pointer">
        <span class="material-symbols-outlined" style="font-size:18px;line-height:1">menu</span>
        <span class="hidden md:inline text-sm font-semibold">Menu</span>
      </button>
    </div>
  </div>
</nav>
<div id="bd" class="fixed inset-0 bg-black/60 z-[1000] opacity-0 pointer-events-none transition-opacity duration-250 backdrop-blur-sm"></div>
<div id="mp" class="fixed top-0 right-0 bottom-0 w-[300px] bg-white border-l border-slate-100 z-[1001] translate-x-full transition-transform duration-[380ms] ease-[cubic-bezier(0.16,1,0.3,1)] p-7 flex flex-col overflow-y-auto">
  <button id="mx" class="self-end text-slate-400 hover:text-slate-900 text-xl mb-6 transition-colors">&times;</button>
  <div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Product</div><div class="flex flex-col gap-2"><a href="/how-it-works.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">How It Works</a><a href="/demo.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Live Demo</a><a href="/faq.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">FAQ</a><a href="/ai-readiness.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">AI Readiness Score</a><a href="/calculator.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Revenue Calculator</a></div></div>
  <div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Learn</div><div class="flex flex-col gap-2"><a href="/case-studies.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Case Studies</a><a href="/blog.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Blog</a></div></div>
  <div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Industries</div><div class="flex flex-col gap-2"><a href="/hvac.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">HVAC</a><a href="/plumbing.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Plumbing</a><a href="/electrical.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Electrical</a></div></div>
  <div class="mb-6"><div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Company</div><div class="flex flex-col gap-2"><a href="/about.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">About</a><a href="/affiliate.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Affiliate Program</a><a href="/careers.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Careers</a><a href="/status.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">System Status</a></div></div>
  <a href="/demo.html" class="mt-auto bg-primary text-white text-center py-4 rounded-2xl font-black text-sm hover:opacity-90 transition-opacity">Book a Free Demo &rarr;</a>
</div>"""

FOOTER_JS = """<footer style="background:#0f172a;color:#fff;padding:60px 24px 32px">
  <div style="max-width:1400px;margin:0 auto">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:40px;margin-bottom:48px">
      <div><div style="font-family:sans-serif;font-size:20px;font-weight:900;margin-bottom:12px">Syntharra</div><p style="color:rgba(255,255,255,0.4);font-size:14px;line-height:1.6;margin-bottom:16px">AI voice agents for trade businesses.</p><a href="mailto:support@syntharra.com" style="color:rgba(255,255,255,0.3);font-size:13px;display:block">support@syntharra.com</a></div>
      <div><h4 style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#6366f1;margin-bottom:16px">Product</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/how-it-works.html" style="color:rgba(255,255,255,0.5);font-size:14px">How It Works</a><a href="/demo.html" style="color:rgba(255,255,255,0.5);font-size:14px">Live Demo</a><a href="/calculator.html" style="color:rgba(255,255,255,0.5);font-size:14px">Revenue Calculator</a><a href="/faq.html" style="color:rgba(255,255,255,0.5);font-size:14px">FAQ</a></div></div>
      <div><h4 style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#6366f1;margin-bottom:16px">Industries</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/hvac.html" style="color:rgba(255,255,255,0.5);font-size:14px">HVAC</a><a href="/plumbing.html" style="color:rgba(255,255,255,0.5);font-size:14px">Plumbing</a><a href="/electrical.html" style="color:rgba(255,255,255,0.5);font-size:14px">Electrical</a></div></div>
      <div><h4 style="font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#6366f1;margin-bottom:16px">Company</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/about.html" style="color:rgba(255,255,255,0.5);font-size:14px">About</a><a href="/case-studies.html" style="color:rgba(255,255,255,0.5);font-size:14px">Case Studies</a><a href="/blog.html" style="color:rgba(255,255,255,0.5);font-size:14px">Blog</a><a href="/careers.html" style="color:rgba(255,255,255,0.5);font-size:14px">Careers</a></div></div>
    </div>
    <div style="border-top:1px solid rgba(255,255,255,0.08);padding-top:24px;text-align:center;color:rgba(255,255,255,0.2);font-size:12px">&copy; 2026 Syntharra Global AI Solutions. All rights reserved.</div>
  </div>
</footer>
<script>
const bd=document.getElementById('bd'),mp=document.getElementById('mp'),mx=document.getElementById('mx'),hbg=document.getElementById('hbg');
function openMenu(){bd.classList.add('opacity-100','pointer-events-auto');mp.style.transform='translateX(0)';document.body.style.overflow='hidden';}
function closeMenu(){bd.classList.remove('opacity-100','pointer-events-auto');mp.style.transform='';document.body.style.overflow='';}
if(hbg)hbg.addEventListener('click',openMenu);
if(mx)mx.addEventListener('click',closeMenu);
if(bd)bd.addEventListener('click',closeMenu);
</script>"""


def get_city_content(city, testimonial):
    name = city["name"]
    state = city["state"]
    slug = city["slug"]
    climate = city["climate"]
    season = city["season"]

    # Unique problem paragraphs per city
    problem_paragraphs = {
        "Chicago": """<p>Chicago's HVAC market is relentless. The city sits on the shore of Lake Michigan, and that proximity creates a weather machine — polar vortex events that send temperatures plummeting to -20°F one month, heat advisories with humidity making it feel like 105°F the next. There is no slow season for a Chicago HVAC contractor. And with nearly three million residents spread across neighborhoods from Rogers Park to Beverly, the density of demand means your competitors are always just one phone call away from stealing a customer you could have had.</p>
      <p>The city's housing stock compounds this. Greystone three-flats built in the 1920s, brick bungalows from the 1950s, mid-century apartment buildings in Wicker Park and Pilsen — these structures run systems that were installed decades ago and fail at the worst possible times. A furnace going out in a Chicago two-flat in February isn't just uncomfortable; it's a liability for the landlord and a crisis for the tenant. Those calls come in at midnight, at 4am, on Sunday mornings. If you're not picking up, someone else is.</p>
      <p>Every HVAC contractor who operates in the Chicago market knows the rhythm: busy season hits, calls stack up, and the calls you miss during the rush are the ones that go to a competitor and never come back. The window to win a new customer in an emergency is measured in minutes, not hours. Once they've reached someone else and gotten a technician dispatched, that relationship is built — and it won't be with you.</p>""",

        "Detroit": """<p>Metro Detroit HVAC contractors face one of the most demanding service environments in the Midwest. The region's winters are brutal in a way that doesn't get enough national attention — sustained cold snaps with wind chills that drop to -25°F, furnace systems in older Wayne County homes running at full capacity for weeks on end. A heat exchanger failure or a cracked flue doesn't wait for business hours. Those calls come in at night, on weekends, during snowstorms when the dispatcher is overwhelmed and the phone rings through to voicemail.</p>
      <p>The tri-county service area — Wayne, Oakland, and Macomb — covers enormous geographic and demographic range. Grosse Pointe homeowners with high-end systems, Eastside Detroit neighborhoods with aging housing stock, Macomb Township subdivisions built in the 2000s with mid-tier equipment reaching the end of its lifespan. Each segment generates different types of service calls, but they share one common trait: the customer calling in a heating emergency expects to reach someone immediately. Voicemail is not an acceptable answer when it's 5°F outside.</p>
      <p>The summer cooling season adds another layer. Detroit summers are humid and hot enough to turn an AC failure into a medical event for elderly residents. The contractors who win market share in this metro are the ones who project reliability — and nothing signals reliability faster than a phone that gets answered every single time, around the clock, without fail.</p>""",

        "Minneapolis": """<p>Minneapolis HVAC contractors operate in a climate that has no margin for error. The Twin Cities sit in a region where January wind chills routinely reach -35°F, where furnace failures at 2am are classified as genuine life-safety emergencies by local emergency services, and where the difference between a contractor who answers and one who doesn't can be measured in pipes bursting, damage claims, and customers lost permanently. The severity of Minnesota winters means that reliability isn't a differentiator — it's the baseline expectation.</p>
      <p>The Minneapolis market is also geographically complex. Contractors serving the metro navigate dense urban neighborhoods in South Minneapolis and Northeast alongside sprawling suburbs in Edina, Bloomington, Plymouth, and Maple Grove. The housing stock ranges from century-old Victorians near Lake Harriet to 1990s suburban builds with systems approaching the end of their service life. Each generates different call patterns, but all of them peak during the worst weather — and peak call volume is exactly when voicemail is most likely to lose you a customer for good.</p>
      <p>Minnesota homeowners are practical people who do their research before choosing a contractor. They read reviews, ask neighbors, and remember who answered the phone when they had a furnace crisis. The contractor who picks up at midnight during a polar vortex event gets the review, the referral, and the annual maintenance contract that follows. The one who sends it to voicemail gets nothing — and the customer won't call back.</p>""",

        "Milwaukee": """<p>Milwaukee's position on the western shore of Lake Michigan gives it a climate that's simultaneously more moderate and more unpredictable than inland Wisconsin cities. Lake-enhanced snowfall, persistent winter cold, and muggy summers create demand for both heating and cooling services that runs nearly year-round. HVAC contractors in the Milwaukee metro know that there's barely a month between when the last furnace tune-up is done and when the first AC call comes in — and that transition period is exactly when missed calls hurt most.</p>
      <p>The city's housing stock is one of the oldest in the Midwest. Milwaukee's German immigrant heritage produced dense neighborhoods of solid brick construction — sturdy buildings that are now 80 to 120 years old and running HVAC systems that have been retrofitted, upgraded, and pushed past their designed service life. Bay View, Walker's Point, Riverwest, and the north side neighborhoods all have aging infrastructure that breaks at unpredictable times. Landlords and homeowners in these areas don't have the luxury of waiting for business hours when a boiler fails.</p>
      <p>The suburban counties add volume. Waukesha, Ozaukee, and Washington counties have seen significant residential growth over the past two decades — newer homes with systems approaching the 10-to-15-year mark where major repairs become routine. For Milwaukee-area HVAC contractors trying to build recurring revenue, every call that goes unanswered is a maintenance contract that goes to whoever did pick up.</p>""",

        "Omaha": """<p>Omaha's position in the heart of the Great Plains makes it one of the most weather-volatile markets in the country for HVAC contractors. The city sees summer heat that regularly pushes into triple digits with high humidity, and winter cold that can drop below 0°F for sustained periods. Unlike coastal climates with moderating effects, Omaha gets the full force of continental weather — and with almost no buffer between seasons, HVAC demand doesn't taper off between the cooling season and the heating season. Contractors here don't get a slow month.</p>
      <p>The Omaha metro has grown significantly over the past decade, with development spreading into Sarpy County and the western suburbs of Papillion, La Vista, and Gretna. New construction runs alongside the older neighborhoods of Benson, Dundee, and South Omaha — and both segments have distinct needs. Newer homes need commissioning, warranty service, and first-generation repairs. Older homes need aggressive maintenance and frequent emergency calls on aging equipment. Either way, the phone rings.</p>
      <p>Nebraska homeowners are pragmatic. They remember who answered when they called in an emergency, and they tell their neighbors. A single emergency call that gets answered and handled well can produce two or three referrals in neighborhoods where people still talk to each other. A call that goes to voicemail produces zero referrals and often produces a negative mention. In the Omaha market, your phone is your reputation.</p>""",

        "Kansas City": """<p>Kansas City straddles the Missouri-Kansas state line, and the HVAC contractors who serve this market deal with a climate that combines the worst of both regions. Gulf moisture flows north through the Missouri River corridor, making Kansas City summers genuinely oppressive — humidity that makes 90°F feel like 105°F, weeks-long stretches where the AC runs continuously, and systems pushed to failure by sustained high-load operation. Then winter brings Alberta Clippers and ice storms that test furnaces and heat pumps equally hard.</p>
      <p>The metro's sprawl creates a challenging service geography. Contractors who build a strong residential book here end up running service calls from the urban core neighborhoods of Westport and Brookside all the way out to Lee's Summit, Overland Park, and the Johnson County suburbs. That geographic spread means call volume is always distributed across a wide area — and the contractor who builds a reputation for fast response, starting with the phone pickup, wins the referral network that spreads across the whole metro.</p>
      <p>Kansas City's growth trajectory also means a large cohort of homes built in the late 1990s and early 2000s with equipment that is now hitting the 20-to-25-year mark — the age when heat exchangers crack, compressors fail, and homeowners face the replace-versus-repair decision. Those calls are high-value. A contractor who answers promptly and handles that conversation well closes a system replacement at $6,000 to $12,000. A contractor who sends it to voicemail loses that ticket to a competitor who picked up.</p>""",

        "St. Louis": """<p>St. Louis earns its reputation for oppressive summer weather honestly. The city sits in the Mississippi River floodplain where heat and Gulf moisture combine to create conditions that regularly push the heat index above 105°F for days at a stretch. Air conditioning isn't a luxury in St. Louis — it's a health necessity, particularly in the city's older neighborhoods where residents include a large elderly population with serious heat vulnerability. AC failures in August are emergency calls, not service requests, and they demand immediate response.</p>
      <p>The winter side of the equation is equally demanding. Cold continental air pushes down from the north and meets the Missouri River moisture, creating cold wet winters with temperatures regularly dropping below 10°F. The city's historic housing stock — 1920s brick Craftsmans in Tower Grove, turn-of-the-century Victorians in Lafayette Square, post-war ranches in South St. Louis County — runs systems that break down with predictable regularity. An HVAC contractor who has built a strong residential client base in St. Louis is never sitting idle.</p>
      <p>What separates the contractors who grow in this market from those who stay flat is response speed. St. Louis homeowners who call with an emergency and reach a professional, knowledgeable voice immediately are far more likely to book service, accept recommendations, and return for maintenance work. The contractor who lets those calls go to voicemail during a heat wave or cold snap is not just losing that job — they're losing the referral network that would have followed.</p>""",

        "Cincinnati": """<p>Cincinnati's Ohio Valley location creates a specific microclimate that HVAC contractors know well. Hot, humid air flows up from the Gulf through the Ohio River corridor, making Cincinnati summers sticky and exhausting — the kind of heat that accelerates AC compressor wear and sends systems into failure without warning. Meanwhile, the valley geography channels cold air in winter, creating damp cold conditions that are harder on furnaces and heat pumps than straight dry cold. Cincinnati HVAC systems work hard and fail often.</p>
      <p>The city's neighborhoods reflect over a century of urban development, and each has its own HVAC character. Hyde Park and Mt. Lookout have large early-20th-century homes with complex mechanical systems and owners who expect premium service. College Hill and Westwood have working-class housing stock with aging equipment and cost-sensitive customers who nonetheless need reliable contractors. The East Side suburbs — Anderson Township, Loveland, Mason — have newer construction where equipment is hitting the critical 15-to-20-year replacement window. Every segment generates calls; what differentiates contractors is who answers them.</p>
      <p>Cincinnati is a city where word of mouth still drives a significant share of HVAC business. Neighborhoods with stable, long-term residents refer contractors they trust to friends and family with a reliability that outperforms almost any digital marketing channel. To earn that word-of-mouth engine, you have to build the trust first — and trust starts with picking up the phone every time someone calls, whether it's a Tuesday afternoon or a Saturday night in February.</p>""",

        "Cleveland": """<p>Cleveland's position on the southern shore of Lake Erie makes it one of the most demanding HVAC markets in Ohio. Lake-effect snow systems dump multiple feet of snow in compressed time windows — the kind of storms where furnace failures become genuine crises and emergency heating calls stack up faster than any contractor can manually route them. During a major lake-effect event, a Cleveland HVAC contractor with a full-time answering system captures every call that comes in. One without it misses the ones that hit at 11pm, 3am, and Sunday morning.</p>
      <p>The city's neighborhoods span a wide range of housing age and condition. Tremont, Ohio City, and the near west side have older housing stock — much of it built before World War II — with systems that have been retrofitted multiple times and don't always play nicely with modern controls. The eastern suburbs of Shaker Heights, Cleveland Heights, and University Heights have large homes with complex multi-zone systems that require experienced technicians. The outer suburbs of Strongsville, Parma, and Mentor have mid-century and newer construction with more predictable service patterns but equally high expectations for response time.</p>
      <p>Cleveland HVAC contractors who have built strong books of business know that emergency call capture is the engine of their referral network. A homeowner who calls at midnight during a January blizzard and gets a professional response — name captured, issue triaged, contractor notified immediately — becomes a loyal customer and a vocal advocate. The customer who reaches voicemail at midnight calls down the list until someone answers, and their loyalty goes to that contractor instead.</p>""",

        "Pittsburgh": """<p>Pittsburgh's geography is unlike any other major Midwest-adjacent city. The three rivers, the hills, the valleys — all of it creates microclimates that make weather prediction unreliable and HVAC demand highly localized. The North Shore gets different conditions than the South Hills. The Strip District behaves differently from Mt. Lebanon. What's consistent is that Pittsburgh winters are cold, wet, and long — often stretching from October through April with furnace demand running continuously — and summers are humid enough to push AC systems hard from June through September.</p>
      <p>The city's Renaissance-era and post-war housing stock is the dominant factor for most Pittsburgh HVAC contractors. Row houses and brick colonials built in the 1940s and 1950s make up the majority of the residential market in neighborhoods like Lawrenceville, Bloomfield, Shadyside, and Squirrel Hill. These structures have boilers, forced-air systems, and sometimes both — with ductwork that runs through uninsulated spaces and equipment that has been in service for 20 to 30 years. They break down. Often. And the calls come in when the weather is worst, which is exactly when the technicians are already busy and the dispatcher is overwhelmed.</p>
      <p>Pittsburgh's HVAC market rewards contractors who project professionalism. The city has a strong blue-collar work ethic and high standards for trades people — but homeowners are equally quick to shift their loyalty when they feel ignored or under-served. Missing a call from a Squirrel Hill homeowner with a failed boiler at 10pm on a Thursday doesn't just cost you that service call. It costs you the neighbor referral, the annual inspection, and the eventual system replacement. Every missed call in Pittsburgh is a compounding loss.</p>""",

        "Toledo": """<p>Toledo sits at the western end of Lake Erie, and the lake's influence shapes everything about the HVAC season here. Lake-effect snow events hit Toledo with less frequency than Cleveland but with significant intensity — the city averages over 40 inches of snow annually, and the cold temperatures that come with those systems mean furnace demand is sustained and relentless from November through March. During a major cold snap, a Toledo HVAC contractor's phone runs hot, and the calls that go unanswered go to someone else.</p>
      <p>The Toledo metro has a distinctive character shaped by its industrial heritage — auto industry employment, manufacturing, logistics. Working-class neighborhoods on the west side and south side have solid older housing stock where HVAC systems run hard and maintenance budgets are tight. East Toledo and the inner city have older housing that demands frequent service. The suburbs of Maumee, Perrysburg, and Sylvania have newer construction with owners who expect premium responsiveness. Each segment is a viable market for a contractor who builds a reputation for reliability and fast response.</p>
      <p>Toledo homeowners are direct. They call when they have a problem, they expect someone to answer, and they make a decision quickly about whether this contractor is worth trusting with their home. A professional, fast response — even if it's just an AI capturing their name, number, and issue and texting the contractor instantly — signals reliability. Voicemail signals the opposite. In a market where contractors are constantly competing for the same pool of homeowners, the difference between answering and not answering is often the difference between growing and staying flat.</p>""",

        "Akron": """<p>Akron sits in the snowbelt of northeast Ohio, and the numbers reflect it — the city averages more than 50 inches of snow annually, with lake-effect systems from both Lake Erie and Lake Ontario contributing to some of the most consistent winter weather in the state. For HVAC contractors serving Summit County and the surrounding area, furnace season is long, intense, and unforgiving. Emergencies pile up during cold snaps; calls come in around the clock; and contractors who can capture every lead — not just the ones that happen to come in during business hours — separate themselves from competitors who can't.</p>
      <p>The Akron market reflects the city's rubber industry heritage — working-class neighborhoods with solid housing stock, mid-century residential construction that has aged into the frequent-repair zone, and a cost-conscious customer base that nonetheless values reliability above almost everything else. Homeowners in Firestone Park, Highland Square, and West Akron have long memories about which contractors answered when they needed help and which ones sent them to voicemail in January. The HVAC market here is driven by reputation and word of mouth to a degree that makes every single call interaction a marketing decision.</p>
      <p>Summer brings its own pressure. Northeast Ohio humidity is significant, and AC systems that ran hard through the previous cooling season often fail at the start of the next. Memorial Day weekend breakdowns, late June heat waves, and early August surges hit Akron contractors with concentrated call volume that tests every system they have. The contractors who have a professional call-capture system in place don't just survive those surges — they grow through them, while competitors with manual call handling miss the overflow and lose the customers.</p>""",

        "Dayton": """<p>Dayton occupies a geographic position in the Miami Valley that creates a distinctive climate profile. Cold continental air from the north collides with Gulf moisture flowing up from the south, producing winters that are colder and wetter than many Ohio cities and summers that are humid and unpredictable. The Miami River corridor tends to hold moisture, making humidity a year-round factor that accelerates system wear and drives calls at the margins of both seasons. Dayton HVAC contractors deal with a shoulder-season demand that other markets don't have.</p>
      <p>The city's working-class heritage is visible in its neighborhoods. South Park, Belmont, and the Old North Dayton neighborhoods have housing stock built between 1900 and 1960 — sturdy construction with aging HVAC systems that require ongoing maintenance and frequent emergency repairs. The suburbs of Centerville, Kettering, and Miamisburg have post-war and newer construction with equipment hitting the critical replacement window. Wright-Patt Air Force Base drives a population of military families who rotate through the area and need contractors they can trust quickly, without long vetting processes.</p>
      <p>Dayton is a competitive HVAC market precisely because the demand is real and consistent. Contractors who build strong residential books here do so by showing up — by being the one who answered when the customer called at 9pm about a furnace that stopped working, by being the contractor who sent a tech out the next morning and did the job right. That reputation is built call by call. The ones you miss don't just cost you the job; they reset the entire relationship-building process with that homeowner.</p>""",

        "Grand Rapids": """<p>Grand Rapids sits just 30 miles inland from the eastern shore of Lake Michigan, and the lake's influence is enormous. Lake-effect snow systems dump an average of 75 inches of snow on the Grand Rapids area annually — more than almost any other major Midwest city outside the Great Lakes snowbelt. For HVAC contractors serving Kent County and the surrounding region, winter is not just a busy season; it's a sustained emergency response operation that runs from November through March with call volume that peaks during every major snow event.</p>
      <p>The city has been growing significantly for over a decade. Medical Mile development downtown, West Michigan's diversified manufacturing economy, and a strong quality-of-life reputation have driven population growth that shows up in new residential construction across the outer suburbs — Byron Center, Caledonia, Rockford, and Lowell. That new construction sits alongside the older housing stock in Heritage Hill, Eastown, and the West Side neighborhoods, creating demand across the full spectrum from new equipment commissioning to emergency repair on 40-year-old systems. Grand Rapids HVAC contractors who cover both segments never lack for work.</p>
      <p>The West Michigan market has a distinct culture around local business loyalty. Grand Rapids residents actively seek out and support local contractors, particularly when those contractors deliver consistent, professional service. The first point of contact — the phone call — sets the tone for that entire relationship. An HVAC contractor whose phone is always answered, who captures every lead professionally and responds quickly, builds the kind of reputation in this market that sustains a business for decades.</p>""",

        "Wichita": """<p>Wichita's position on the Great Plains makes it one of the most weather-extreme HVAC markets in the country. The city is exposed to the full range of continental climate — summer heat that regularly surpasses 100°F for extended periods, winter cold that drops below 0°F, ice storms, blizzards, and severe thunderstorm seasons that can knock out power and put HVAC systems through extreme stress cycles. Wichita HVAC contractors don't just serve a busy market; they serve a market where weather events drive massive, simultaneous call volumes that test every capacity a contractor has.</p>
      <p>The Wichita metro is geographically spread across Sedgwick County, with the city proper sitting at the center of a service area that stretches from Andover and Derby in the east to Goddard and Haysville in the west. The housing stock reflects the city's growth across multiple eras — early 20th-century homes in College Hill and Riverside, mid-century construction throughout the core, and substantial newer development in the western suburbs. Each segment has different HVAC needs, but all of them generate emergency calls when the weather turns.</p>
      <p>In Wichita's market, responsiveness is the defining characteristic of successful contractors. When a summer heat wave hits and homeowners across the city wake up to a failed AC system, the calls go to whoever answers first. Contractors who have professional, consistent call capture in place grow their customer base during every major weather event. Those who rely on manual call handling during peak periods let revenue walk to competitors — and in Wichita's extreme climate, those peak periods happen multiple times every year.</p>""",

        "Des Moines": """<p>Des Moines sits at the heart of Iowa's agricultural landscape, and the climate that makes Iowa farmland productive is the same climate that drives one of the most demanding HVAC cycles in the Midwest. Furnace season runs from October through April — a full seven months where heating demand is constant and cold snaps can push temperatures to -20°F. The transition to cooling season is brief: June through September, with summer heat and humidity creating AC demand that rivals the southern states. Des Moines HVAC contractors have maybe three or four slow weeks per year, if that.</p>
      <p>The city's growth over the past two decades has been significant. Downtown redevelopment, financial and insurance sector jobs, and a strong quality-of-life reputation have brought population growth that shows up in new residential construction across the suburbs — Ankeny, Johnston, Urbandale, and West Des Moines have all seen substantial development. This new housing stock joins the older neighborhoods of Beaverdale, Drake, and Sherman Hill in generating consistent HVAC service demand. Newer homes need first-generation service; older homes need ongoing repairs on aging equipment.</p>
      <p>Iowa's weather has a specific rhythm that Des Moines HVAC contractors know well — the first major cold snap of the season hits in October or November, homeowners crank up their furnaces for the first time, and phones ring immediately with calls from systems that didn't make it through the summer without issues developing. That first-cold-snap rush is when missed calls are most costly. A homeowner who can't reach their regular contractor at that moment calls down the list and often builds a new contractor relationship that lasts for years.</p>""",

        "Lincoln": """<p>Lincoln's Great Plains climate is defined by extremes in both directions. Summer heat pushes into the upper 90s and triple digits regularly, with humidity that makes outdoor work miserable and indoor AC systems run continuously for weeks. Winter brings persistent cold — the kind that drops below 0°F for multi-day stretches — along with blizzards that pile up snow and put furnace systems under maximum load. Nebraska HVAC contractors who serve Lincoln know there is no easy season; there is only heating season and cooling season, back to back, year after year.</p>
      <p>Lincoln has grown substantially over the past decade — the city expanded by over 15% in population while its geographic footprint pushed out into new residential developments in the southwest and east. University of Nebraska enrollment, state government employment, and a growing technology sector have all contributed to a residential market that includes everything from historic Haymarket neighborhood townhomes to brand-new suburbs in Yankee Hill and Wilderness Hills. The diversity of housing stock means diverse HVAC needs — and diverse call patterns that don't cluster neatly into business hours.</p>
      <p>University towns have a specific character for HVAC contractors. There's a large rental market in the areas near UNL campus — landlords and property management companies who need contractors they can rely on for tenant-reported issues, often reported at inconvenient times. A responsive contractor who captures those calls professionally, routes the lead instantly, and follows up quickly builds the kind of institutional relationships with property managers that generate steady, high-volume work for years.</p>""",

        "Sioux Falls": """<p>Sioux Falls has been one of the fastest-growing cities in the United States for over a decade, and that growth shows up directly in the HVAC market. New residential construction is booming — entire subdivisions going up annually, all of them needing equipment commissioning, warranty service, and first-generation repairs. But underneath the new growth is an established city with older neighborhoods where aging HVAC systems generate the emergency call volume that every contractor depends on. Sioux Falls HVAC contractors are simultaneously serving two very different markets at once.</p>
      <p>South Dakota winters are among the harshest in the country. Sioux Falls sits in the eastern part of the state where blizzards blow in from the northwest with little warning, temperatures can drop to -25°F with wind chill, and furnace failures genuinely put residents at risk. The winters here are long — furnace demand runs from October through April in earnest — and the urgency of heating emergencies in January is real in a way that contractors in milder climates don't fully experience. Every unanswered call during a South Dakota cold snap is a homeowner in distress turning to a competitor.</p>
      <p>The city's growth trajectory also means a lot of new residents who are establishing relationships with local contractors for the first time. Those first service experiences — whether they're warranty calls on new equipment or emergency calls on older homes — shape contractor loyalty that can last for the entire homeownership period. The contractor who answers that first call, captures the lead professionally, and follows up quickly wins a customer who may stay with them for 20 years in a city that's still adding residents every year.</p>""",

        "Rockford": """<p>Rockford sits in northern Illinois, far enough from the lake to miss the most intense lake-effect snow but close enough to the Wisconsin border to get the full force of Midwest cold. The city sees significant snowfall — 35 to 45 inches annually — and wind chills that regularly drop below -20°F during the worst January and February stretches. For HVAC contractors serving Winnebago County and the surrounding area, furnace season is serious business from October through March, and the calls that come in at midnight during a cold snap are the ones that define your reputation for the season.</p>
      <p>Rockford's manufacturing heritage has left it with housing stock that reflects multiple eras of working-class residential development. The near-north side and east side neighborhoods have solid brick construction from the early 20th century — the kind of homes where boilers and early forced-air systems have been patched and repaired for decades and now need consistent professional attention. The outer ring of development in Loves Park and Machesney Park has mid-century and newer construction where equipment age drives service needs. The entire market generates real call volume year-round.</p>
      <p>The cooling season in Rockford is real and underappreciated. Northern Illinois summers are humid and hot — heat index regularly exceeds 95°F through July and August — and AC systems that have run through multiple cooling seasons without service are prone to failure at exactly the moments when homeowners most need them. The contractor who answers that first hot-weather call of the season, captures the information efficiently, and follows up immediately is the contractor who earns the maintenance agreement, the referral, and the system replacement when it comes due.</p>""",

        "Madison": """<p>Madison's HVAC market has a character unlike any other Wisconsin city. The presence of the University of Wisconsin creates an unusually large rental housing sector — student apartments, faculty homes, university-adjacent neighborhoods where property managers are perpetually managing tenant-reported HVAC issues, often reported at inconvenient times via property management portals or direct phone calls that come in at all hours. A Madison HVAC contractor who has built strong relationships with property managers and landlords has a steady, recurring revenue base that buffers the variability of the residential emergency market.</p>
      <p>Wisconsin winters hit Madison hard. The city sits on an isthmus between two lakes, and that geography creates wind exposure that makes already cold temperatures feel more extreme. Wind chills of -25°F to -35°F are not unusual in January and February, and furnace failures during those conditions are genuine emergencies. The city's mix of older campus-area housing, established residential neighborhoods on the west side, and newer development in Verona, Middleton, and Sun Prairie means contractors serve a wide range of equipment age and condition — all of it demanding attention during the same cold-weather events.</p>
      <p>Madison is also a city that values responsiveness in its service providers. The population skews educated and is comfortable switching contractors when service doesn't meet expectations. A missed call during an emergency doesn't just lose you that job — it generates a negative review from a resident who is likely active on Nextdoor, Google, and local community forums. Conversely, a contractor who answers every call, captures leads professionally, and follows up promptly generates the kind of five-star reviews and social proof that drives organic growth in this market for years.</p>""",
    }

    problem_text = problem_paragraphs.get(name, f"""<p>{name}'s climate creates year-round HVAC demand that keeps contractors busy across both {season}. Homeowners here expect fast, professional responses when equipment fails — and during weather emergencies, those calls come in around the clock.</p>
      <p>The local market rewards contractors who project reliability. When a {name} homeowner calls with a heating or cooling emergency, the first contractor who answers and responds professionally wins the job — and the referral that follows. The one who sends it to voicemail loses both.</p>
      <p>Missing 4 to 6 calls per week — a conservative industry average for contractors without dedicated call coverage — costs {name} HVAC businesses over $175,000 in annual revenue at average ticket values. That's not a rounding error; it's a business outcome determined entirely by whether the phone gets answered.</p>""")

    # FAQ items per city (rotate a city-specific climate question)
    faq_items = {
        "Chicago": [
            ("Does this work during Chicago's winter emergencies when I'm overwhelmed?", "Yes — that's exactly when it performs best. During polar vortex events when every contractor in the city is getting calls simultaneously, Syntharra answers every single call in under 3 seconds, captures the details, and texts you immediately. You triage and call back in priority order instead of missing the ones that hit during a busy hour."),
            ("Will callers think they're reaching a robot?", "Callers reach a professional AI voice that handles HVAC inquiries naturally. The important thing is that they get answered instantly — and that you get the lead within seconds of the call ending, ready to call back."),
            ("What's the pricing?", "Flat $697 per month. No per-call fees, no overage charges, no contracts. Unlimited calls. We also offer a 200-minute free pilot with no credit card required."),
            ("How fast is setup?", "Under 24 hours. You forward your business line to your Syntharra number — takes about 60 seconds — and calls are being captured immediately. We handle all the configuration on our end."),
        ],
        "Detroit": [
            ("Does this handle the surge volume during Wayne County cold snaps?", "Absolutely. There's no call volume limit — every call gets answered in under 3 seconds regardless of how many are coming in simultaneously. During a February cold snap when your phone would normally ring busy or overflow to voicemail, Syntharra captures all of them and texts you each lead instantly."),
            ("What information does it capture from each caller?", "Name, callback number, issue type (furnace failure, no heat, strange noise, etc.), and any urgency indicators the caller provides. You get all of that in a text within seconds of the call ending."),
            ("Is there a contract?", "No contract. Month-to-month at $697/mo. The 200-minute free pilot requires no credit card and gives you a real test of the system with your actual callers before you commit."),
            ("Can I use my existing Detroit business number?", "Yes. You forward calls from your existing number to your Syntharra line. Your number stays yours — you're just routing calls through Syntharra when you want coverage."),
        ],
        "Minneapolis": [
            ("What happens during a Minneapolis polar vortex event when calls come in all at once?", "Every call still gets answered in under 3 seconds, regardless of simultaneous volume. During the worst cold snaps — when contractors across the Twin Cities metro are all fielding emergency calls at the same time — Syntharra captures every one and texts you each lead immediately. You work through them in priority order without losing a single caller to voicemail."),
            ("Does the AI understand HVAC-specific issues?", "Yes. It's trained on HVAC terminology and can triage between heating emergencies, routine service requests, and new customer inquiries. It captures the relevant details for each type of call."),
            ("What does it cost?", "Flat $697/mo, no contracts, no per-call fees. Start with a 200-minute free pilot — no credit card required — and see the results with your actual Minneapolis customers before you commit."),
            ("How do I know when I get a lead?", "You get a text message within seconds of every call ending. It includes the caller's name, phone number, and a summary of their issue. You call back when it makes sense for your schedule and triage."),
        ],
    }

    # Default FAQ for cities not explicitly listed
    default_faq = [
        (f"Does this work for {name}'s {season.split(' and ')[0]} emergency calls that come in late at night?", f"Yes — that's the core use case. {name}'s weather creates emergency calls at 11pm, 2am, and early Sunday morning. Syntharra answers every one of them in under 3 seconds and texts you immediately with the lead details. You decide when to call back based on urgency."),
        ("What information does Syntharra capture from each caller?", "Name, callback number, issue type, and urgency level. Everything you need to call back prepared. The text arrives within seconds of the call ending — no lead ever goes cold."),
        ("What does it cost and is there a contract?", "Flat $697/mo, no contract, no per-call fees. We offer a 200-minute free pilot with no credit card required — a real test with your actual callers before you commit to anything."),
        ("How long does setup take?", "Under 24 hours. You forward your business line to your Syntharra number — takes about 60 seconds — and the system is live immediately. No technical setup required on your end."),
    ]

    faq_list = faq_items.get(name, default_faq)

    faq_html = ""
    for q, a in faq_list:
        faq_html += f"""        <div class="faq-item">
          <div class="faq-q">{q}</div>
          <div class="faq-a">{a}</div>
        </div>
"""

    t = testimonial
    testimonial_html = f"""      <div class="testimonial">
        <blockquote>"{t['quote']}"</blockquote>
        <cite>{t['cite']}</cite>
      </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<link rel="icon" type="image/svg+xml" href="/favicon.svg"/>
<title>{name} HVAC Answering Service — 24/7 AI Receptionist | Syntharra</title>
<meta name="description" content="{name} HVAC answering service. 24/7 AI captures every lead, texts you instantly. Flat $697/mo. Free 200-minute pilot, no credit card."/>
<link rel="canonical" href="https://www.syntharra.com/hvac-answering-service-{slug}.html"/>
<meta property="og:title" content="{name} HVAC Answering Service | Syntharra"/>
<meta property="og:description" content="24/7 AI receptionist for {name} HVAC contractors. Never miss a lead."/>
<meta property="og:url" content="https://www.syntharra.com/hvac-answering-service-{slug}.html"/>
<meta property="og:type" content="website"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=Material+Symbols+Outlined:wght,FILL@400,0&display=swap" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com"></script>
<style>
{CSS}
</style>
</head>
<body>
{NAV_BLOCK}
<main>
  <section class="hero">
    <div class="container">
      <span class="eyebrow">HVAC Answering Service — {name}, {state}</span>
      <h1>{name} HVAC contractors —<br><span class="accent">your phone is always answered.</span></h1>
      <p class="hero-sub">{climate}</p>
      <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="btn-primary">Book Your Free Demo &rarr;</a>
      <span class="fine-print">No credit card &bull; 200-minute free pilot &bull; Live in 24 hours</span>
    </div>
  </section>

  <section style="background:#f9f8ff">
    <div class="container">
      <span class="section-label">The Problem</span>
      <h2>Every unanswered call in {name} is revenue walking out the door</h2>
      {problem_text}
      <div class="math-box">
        <h3>What missed calls cost {name} HVAC contractors</h3>
        <div class="math-row"><span>Average HVAC ticket value</span><span>$850</span></div>
        <div class="math-row"><span>Missed calls per week (industry avg)</span><span>4–6</span></div>
        <div class="math-row"><span>Revenue lost per week</span><span>$3,400–$5,100</span></div>
        <div class="math-row"><span>Revenue lost per year</span><span>$176,000–$265,000</span></div>
      </div>
    </div>
  </section>

  <section>
    <div class="container">
      <span class="section-label">How It Works</span>
      <h2>Live in {name} in under 24 hours</h2>
      <div class="steps">
        <div class="step"><div class="step-num">01</div><div class="step-title">Forward your number</div><p>Point your {name} business line to Syntharra. Works with any phone — takes 60 seconds.</p></div>
        <div class="step"><div class="step-num">02</div><div class="step-title">AI answers instantly</div><p>Every call answered in under 3 seconds, 24/7. Callers get professional, knowledgeable triage immediately.</p></div>
        <div class="step"><div class="step-num">03</div><div class="step-title">You get a text</div><p>The second a call ends, you get a text with the caller's name, number, and issue. You call back when it makes sense.</p></div>
      </div>
    </div>
  </section>

  <section style="background:#f9f8ff">
    <div class="container">
      <span class="section-label">What You Get</span>
      <h2>Built for {name} HVAC contractors</h2>
      <div class="card-grid">
        <div class="card"><h3 style="font-family:sans-serif;font-weight:800;font-size:18px;margin-bottom:10px;color:#1a1a2e">Answered in &lt;3 seconds</h3><p style="margin:0">Every call picked up instantly — no hold music, no voicemail, no missed leads.</p></div>
        <div class="card"><h3 style="font-family:sans-serif;font-weight:800;font-size:18px;margin-bottom:10px;color:#1a1a2e">Full lead details captured</h3><p style="margin:0">Name, number, issue type, urgency — everything you need to call back prepared.</p></div>
        <div class="card"><h3 style="font-family:sans-serif;font-weight:800;font-size:18px;margin-bottom:10px;color:#1a1a2e">Instant text to you</h3><p style="margin:0">You're notified the second a call ends. No lead ever sits cold.</p></div>
      </div>
    </div>
  </section>

  <section>
    <div class="container">
{testimonial_html}
    </div>
  </section>

  <section style="background:#f9f8ff">
    <div class="container">
      <span class="section-label">FAQ</span>
      <h2>Questions from {name} HVAC contractors</h2>
{faq_html}    </div>
  </section>
</main>

<div class="container">
  <div class="cta-block">
    <h2>Ready to stop losing {name} jobs to voicemail?</h2>
    <p style="font-size:18px;margin-bottom:32px">Join HVAC contractors across the country capturing every lead. 200-minute free pilot. No credit card.</p>
    <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" style="display:inline-flex;align-items:center;gap:10px;background:#fff;color:#4d41df;padding:18px 40px;border-radius:99px;font-weight:800;font-size:17px;text-decoration:none">Book Free Demo &rarr;</a>
    <span style="display:block;margin-top:14px;font-size:12px;color:rgba(255,255,255,0.5)">No contract &bull; No credit card &bull; Live in 24 hours</span>
  </div>
</div>

{FOOTER_JS}
</body>
</html>"""
    return html


def push_file(filename, content, city_name):
    url = f"{API}/{filename}"
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    payload = {
        "message": f"feat(seo): add HVAC answering service page — {city_name}",
        "content": encoded,
    }
    resp = requests.put(url, headers=HEADERS, data=json.dumps(payload))
    return resp.status_code, resp.json()


def main():
    print("Starting push of 20 Midwest HVAC landing pages...\n")
    results = []
    for i, city in enumerate(CITIES):
        testimonial = TESTIMONIALS[i % len(TESTIMONIALS)]
        html = get_city_content(city, testimonial)
        filename = f"hvac-answering-service-{city['slug']}.html"
        print(f"[{i+1}/20] Pushing {filename} ...", end=" ", flush=True)
        status, resp = push_file(filename, html, city['name'])
        if status in (200, 201):
            print(f"OK ({status})")
            results.append((city['name'], filename, "OK", status))
        else:
            msg = resp.get('message', str(resp))
            print(f"FAILED ({status}): {msg}")
            results.append((city['name'], filename, "FAILED", status))
        if i < len(CITIES) - 1:
            time.sleep(1.5)

    print("\n--- Summary ---")
    ok = sum(1 for r in results if r[2] == "OK")
    fail = sum(1 for r in results if r[2] == "FAILED")
    for city_name, filename, status, code in results:
        mark = "+" if status == "OK" else "X"
        print(f"  [{mark}] {city_name}: {filename} ({code})")
    print(f"\nDone: {ok} succeeded, {fail} failed out of {len(CITIES)} pages.")


if __name__ == "__main__":
    main()
