#!/usr/bin/env python3
"""
Generate and push 20 HVAC answering service SEO landing pages
for California & Pacific West cities to the Syntharra website repo.
"""

import json
import base64
import time
import urllib.request
import urllib.error

TOKEN = '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'
REPO = 'Syntharra/syntharra-website'
API = f'https://api.github.com/repos/{REPO}/contents'
HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Content-Type': 'application/json',
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'Syntharra-PageGen/1.0'
}

CITIES = [
    {"name": "Los Angeles", "state": "CA", "slug": "los-angeles", "climate": "With scorching San Fernando Valley summers regularly hitting 110°F and millions of aging AC units across LA County, HVAC contractors here are overwhelmed from June through September. One missed call during a heat emergency is a job handed to the competition.", "market": "large", "pop": "4M+", "season": "summer heat waves"},
    {"name": "San Diego", "state": "CA", "slug": "san-diego", "climate": "San Diego's marine layer keeps coastal temps mild, but inland zones like El Cajon, Santee, and Escondido hit 100°F+ in summer. HVAC contractors serving both coastal and inland markets need 24/7 coverage year-round.", "market": "large", "pop": "1.4M+", "season": "inland heat and year-round demand"},
    {"name": "San Jose", "state": "CA", "slug": "san-jose", "climate": "Silicon Valley summers surprise newcomers — inland Santa Clara County regularly hits 95-100°F. With high property values and tech workers expecting instant service, HVAC contractors who miss calls lose premium accounts.", "market": "large", "pop": "1M+", "season": "summer heat spikes"},
    {"name": "San Francisco", "state": "CA", "slug": "san-francisco", "climate": "SF's fog keeps most residents comfortable, but the East Bay, South Bay, and Peninsula heat up significantly. Multi-unit properties and commercial HVAC dominate — contractors can't afford after-hours silence.", "market": "large", "pop": "900K+", "season": "year-round commercial demand"},
    {"name": "Fresno", "state": "CA", "slug": "fresno", "climate": "The Central Valley's brutal summers — often 105°F+ from June through September — make Fresno one of the highest-demand HVAC markets in the US. AC failures here are medical emergencies for elderly residents.", "market": "medium", "pop": "550K+", "season": "extreme summer heat"},
    {"name": "Sacramento", "state": "CA", "slug": "sacramento", "climate": "Sacramento summers regularly exceed 100°F with little coastal relief. The sprawling suburbs of Elk Grove, Folsom, and Roseville mean contractors serve huge service areas — every call that gets missed is revenue lost to a faster competitor.", "market": "large", "pop": "500K+", "season": "summer heat emergencies"},
    {"name": "Long Beach", "state": "CA", "slug": "long-beach", "climate": "Long Beach's port-adjacent humidity combined with summer heat creates constant HVAC demand across its dense residential areas. Contractors serving LA's South Bay can't afford gaps in call coverage.", "market": "medium", "pop": "470K+", "season": "summer humidity and heat"},
    {"name": "Bakersfield", "state": "CA", "slug": "bakersfield", "climate": "Bakersfield is one of the hottest cities in California — summer temperatures above 100°F are routine, and triple-digit days can stretch for weeks. For HVAC contractors, summer is a sprint and every missed call is hundreds of dollars lost.", "market": "medium", "pop": "400K+", "season": "extreme dry heat summers"},
    {"name": "Anaheim", "state": "CA", "slug": "anaheim", "climate": "Orange County's dense population and aging housing stock mean constant HVAC demand. Anaheim summers push into the 90s with high humidity, and contractors serving the resort district need 24/7 reliability.", "market": "medium", "pop": "350K+", "season": "summer heat and humidity"},
    {"name": "Santa Ana", "state": "CA", "slug": "santa-ana", "climate": "Santa Ana is one of Orange County's densest cities with high concentrations of older multi-unit housing. High HVAC service demand and a large Spanish-speaking population mean contractors need bilingual, always-on call handling.", "market": "medium", "pop": "310K+", "season": "year-round demand"},
    {"name": "Riverside", "state": "CA", "slug": "riverside", "climate": "The Inland Empire sits in a heat basin that regularly sees 110°F summers. Riverside HVAC contractors face a massive demand spike every June that stretches into October — missing a single after-hours call can mean losing a $3,000 service contract.", "market": "medium", "pop": "315K+", "season": "extreme summer heat"},
    {"name": "Stockton", "state": "CA", "slug": "stockton", "climate": "Stockton's Central Valley location means blistering summers and cold, foggy winters — HVAC contractors here run both heating and cooling seasons at full capacity. Call volume spikes hard in May and doesn't let up until October.", "market": "medium", "pop": "320K+", "season": "summer heat and winter heating"},
    {"name": "Irvine", "state": "CA", "slug": "irvine", "climate": "Irvine's planned communities and high-value homes mean HVAC contractors command premium pricing — and clients expect premium responsiveness. A missed call from an Irvine homeowner means they're calling your competitor within 60 seconds.", "market": "medium", "pop": "300K+", "season": "summer heat and premium market"},
    {"name": "Chula Vista", "state": "CA", "slug": "chula-vista", "climate": "Chula Vista's rapid growth and newer housing stock create strong HVAC demand across its eastern hillside developments. Proximity to the Mexico border brings a bilingual client base that competitors routinely ignore — Syntharra handles both.", "market": "medium", "pop": "280K+", "season": "year-round demand"},
    {"name": "Fontana", "state": "CA", "slug": "fontana", "climate": "Fontana sits deep in the Inland Empire heat pocket — easily 105°F+ in summer. A rapidly growing population and dense warehouse district mean HVAC contractors here are perpetually busy, especially when heatwaves hit.", "market": "medium", "pop": "215K+", "season": "extreme Inland Empire heat"},
    {"name": "Moreno Valley", "state": "CA", "slug": "moreno-valley", "climate": "One of California's fastest-growing cities, Moreno Valley bakes in Inland Empire summers with minimal shade and aging AC systems in its affordable housing stock. Emergency calls surge May through September.", "market": "medium", "pop": "210K+", "season": "summer heat emergencies"},
    {"name": "Glendale", "state": "CA", "slug": "glendale-ca", "climate": "Glendale's Foothill location means hot, dry summers with minimal ocean breeze relief. Dense Armenian and Latino communities with multi-unit housing keep HVAC contractors booked — but only if they answer the phone.", "market": "medium", "pop": "200K+", "season": "summer heat"},
    {"name": "Huntington Beach", "state": "CA", "slug": "huntington-beach", "climate": "Surf City's coastal location moderates temperatures, but inland areas and commercial strip malls create steady HVAC demand. High-value beach properties mean clients expect instant response — missed calls go straight to Yelp reviews.", "market": "medium", "pop": "200K+", "season": "year-round coastal demand"},
    {"name": "Oxnard", "state": "CA", "slug": "oxnard", "climate": "Ventura County's largest city has a year-round maritime climate with significant temperature swings between coastal and inland areas. Agricultural and commercial HVAC alongside dense residential keeps contractors busy 12 months a year.", "market": "medium", "pop": "210K+", "season": "year-round demand"},
    {"name": "Portland", "state": "OR", "slug": "portland", "climate": "Portland shattered its reputation as a mild city during the 2021 heat dome — 116°F killed hundreds and overwhelmed every HVAC contractor in the region. Pacific Northwest summers now see intense heat waves, and contractors who missed calls during that event lost clients permanently.", "market": "large", "pop": "650K+", "season": "summer heat waves and rainy season heating"},
]

# Testimonials to rotate across pages
TESTIMONIALS = [
    {"quote": "We were losing 8-10 calls a week after hours. Syntharra fixed that in 24 hours. Recovered $14,000 in the first month.", "name": "Mark T.", "company": "Arctic Breeze HVAC", "location": "Phoenix, AZ"},
    {"quote": "My receptionist cost $3,200/mo and still missed calls. Syntharra costs less and never misses.", "name": "Jason S.", "company": "Reliable Plumbing", "location": "Denver, CO"},
    {"quote": "Customers can't tell it's AI. We booked 40+ jobs in the first month.", "name": "Rachel C.", "company": "Bright Spark Electric", "location": "Austin, TX"},
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
/* hero */
.hero{padding:120px 24px 60px;text-align:center;background:linear-gradient(180deg,#f5f2ff 0%,#fff 100%)}
.eyebrow{display:inline-block;font-size:11px;font-weight:700;color:#4d41df;letter-spacing:.18em;text-transform:uppercase;background:rgba(77,65,223,.08);padding:6px 16px;border-radius:99px;margin-bottom:20px}
h1{font-family:'Bricolage Grotesque',sans-serif;font-size:clamp(36px,5vw,64px);font-weight:800;line-height:1.05;letter-spacing:-.03em;color:#1a1a2e;margin-bottom:20px}
h1 .accent{background:linear-gradient(135deg,#4d41df,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hero-sub{font-size:18px;color:#464555;max-width:680px;margin:0 auto 32px;line-height:1.6}
.btn-primary{display:inline-flex;align-items:center;gap:10px;background:#4d41df;color:#fff;padding:18px 36px;border-radius:99px;font-weight:700;font-size:16px;text-decoration:none;box-shadow:0 12px 40px -8px rgba(77,65,223,.5);transition:all .2s}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 18px 48px -8px rgba(77,65,223,.65)}
.btn-secondary{display:inline-flex;align-items:center;gap:8px;border:2px solid rgba(77,65,223,.3);color:#4d41df;padding:16px 28px;border-radius:99px;font-weight:600;font-size:15px;text-decoration:none;transition:all .2s}
.btn-secondary:hover{background:rgba(77,65,223,.05)}
.fine-print{display:block;margin-top:14px;font-size:12px;color:#777587}
/* sections */
section{padding:72px 24px}
.section-label{font-size:11px;font-weight:700;color:#4d41df;letter-spacing:.18em;text-transform:uppercase;display:block;margin-bottom:12px}
h2{font-family:'Bricolage Grotesque',sans-serif;font-size:clamp(28px,3.5vw,44px);font-weight:800;letter-spacing:-.02em;color:#1a1a2e;margin-bottom:16px}
p{color:#464555;line-height:1.75;margin-bottom:14px}
/* cards */
.card{background:#fff;border:1px solid #e2e0fc;border-radius:20px;padding:28px 32px;transition:box-shadow .2s}
.card:hover{box-shadow:0 12px 40px rgba(77,65,223,.08)}
.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;margin-top:40px}
/* steps */
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:24px;margin-top:40px}
.step{text-align:center;padding:32px 24px}
.step-num{font-family:'Bricolage Grotesque',sans-serif;font-size:48px;font-weight:800;color:rgba(77,65,223,.15);line-height:1;margin-bottom:8px}
.step-title{font-family:'Bricolage Grotesque',sans-serif;font-size:18px;font-weight:800;color:#1a1a2e;margin-bottom:8px}
/* math */
.math-box{background:#f5f2ff;border:1px solid rgba(77,65,223,.15);border-radius:20px;padding:32px;margin:32px 0}
.math-box h3{font-family:'Bricolage Grotesque',sans-serif;font-size:16px;font-weight:800;color:#1a1a2e;margin-bottom:20px;text-transform:uppercase;letter-spacing:.05em}
.math-row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px dashed rgba(77,65,223,.15);font-size:15px;color:#464555}
.math-row:last-child{border:none;font-weight:800;font-size:16px;color:#4d41df;padding-top:16px;margin-top:8px;border-top:2px solid #4d41df}
/* faq */
.faq-item{border:1px solid #e2e0fc;border-radius:16px;padding:22px 26px;margin-bottom:12px}
.faq-q{font-family:'Bricolage Grotesque',sans-serif;font-size:16px;font-weight:700;color:#1a1a2e;margin-bottom:8px}
.faq-a{font-size:14px;color:#464555;line-height:1.7}
/* testimonial */
.testimonial{background:#1a1a2e;border-radius:24px;padding:40px;color:#fff;margin:40px 0}
.testimonial blockquote{font-family:'Bricolage Grotesque',sans-serif;font-size:20px;font-style:italic;line-height:1.5;margin-bottom:24px}
.testimonial cite{font-size:13px;color:rgba(255,255,255,.5);font-style:normal}
/* cta block */
.cta-block{background:#4d41df;border-radius:32px;padding:64px 40px;text-align:center;color:#fff;margin:0 24px 80px}
.cta-block h2{color:#fff}
.cta-block p{color:rgba(255,255,255,.75)}
/* responsive */
@media(max-width:768px){h1{font-size:36px}.hero{padding:100px 20px 40px}section{padding:48px 20px}.card-grid,.steps{grid-template-columns:1fr}}"""

NAV = """<!-- FLOATING NAV -->
<nav class="fixed top-6 left-1/2 -translate-x-1/2 w-[96%] max-w-[1900px] z-50 bg-white/70 backdrop-blur-2xl rounded-full border border-white/20 shadow-[0_8px_32px_rgba(0,0,0,0.05)] transition-all duration-500">
  <div class="flex justify-between items-center px-8 py-3">
    <a href="/" class="flex items-center gap-3">
      <div class="flex items-end gap-1">
        <div class="w-1 h-3 bg-primary rounded-full"></div>
        <div class="w-1 h-5 bg-primary rounded-full"></div>
        <div class="w-1 h-7 bg-primary rounded-full"></div>
        <div class="w-1 h-9 bg-primary rounded-full"></div>
      </div>
      <div class="flex flex-col leading-none" style="margin-top:-4px">
        <span class="text-2xl font-black tracking-tighter text-slate-900 font-headline">Syntharra</span>
        <span class="text-[9px] font-bold tracking-[0.2em] text-primary uppercase opacity-80">Global AI Solutions</span>
      </div>
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

FOOTER = """<footer class="bg-slate-950 text-white pt-20 pb-10 border-t border-white/5">
  <div class="max-width-container mx-auto px-8">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
      <div>
        <a href="/" class="flex items-center gap-3 mb-6">
          <div class="flex items-end gap-1"><div class="w-1 h-3 bg-indigo-500 rounded-full"></div><div class="w-1 h-5 bg-indigo-500 rounded-full"></div><div class="w-1 h-7 bg-indigo-500 rounded-full"></div><div class="w-1 h-9 bg-indigo-500 rounded-full"></div></div>
          <div><div class="text-xl font-black text-white" style="font-family:sans-serif">Syntharra</div><div style="font-size:8px;letter-spacing:2px;color:#6366f1;text-transform:uppercase;font-weight:700">Global AI Solutions</div></div>
        </a>
        <p style="color:rgba(255,255,255,0.4);font-size:14px;line-height:1.6">AI voice agents for trade businesses. Never miss a call or lose a job to voicemail.</p>
        <div style="margin-top:16px;display:flex;flex-direction:column;gap:6px"><a href="mailto:support@syntharra.com" style="color:rgba(255,255,255,0.3);font-size:13px">support@syntharra.com</a><a href="mailto:feedback@syntharra.com" style="color:rgba(255,255,255,0.3);font-size:13px">feedback@syntharra.com</a></div>
      </div>
      <div><h4 style="font-size:10px;font-weight:900;text-transform:uppercase;letter-spacing:3px;color:#6366f1;margin-bottom:16px">Product</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/how-it-works.html" style="color:rgba(255,255,255,0.5);font-size:14px">How It Works</a><a href="/demo.html" style="color:rgba(255,255,255,0.5);font-size:14px">Live Demo</a><a href="/calculator.html" style="color:rgba(255,255,255,0.5);font-size:14px">Revenue Calculator</a><a href="/faq.html" style="color:rgba(255,255,255,0.5);font-size:14px">FAQ</a></div></div>
      <div><h4 style="font-size:10px;font-weight:900;text-transform:uppercase;letter-spacing:3px;color:#6366f1;margin-bottom:16px">Industries</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/hvac.html" style="color:rgba(255,255,255,0.5);font-size:14px">HVAC</a><a href="/plumbing.html" style="color:rgba(255,255,255,0.5);font-size:14px">Plumbing</a><a href="/electrical.html" style="color:rgba(255,255,255,0.5);font-size:14px">Electrical</a></div></div>
      <div><h4 style="font-size:10px;font-weight:900;text-transform:uppercase;letter-spacing:3px;color:#6366f1;margin-bottom:16px">Company</h4><div style="display:flex;flex-direction:column;gap:10px"><a href="/about.html" style="color:rgba(255,255,255,0.5);font-size:14px">About</a><a href="/case-studies.html" style="color:rgba(255,255,255,0.5);font-size:14px">Case Studies</a><a href="/blog.html" style="color:rgba(255,255,255,0.5);font-size:14px">Blog</a><a href="/careers.html" style="color:rgba(255,255,255,0.5);font-size:14px">Careers</a></div></div>
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


def get_city_content(city, testimonial_idx):
    """Generate unique body content for each city."""
    name = city['name']
    state = city['state']
    slug = city['slug']
    climate = city['climate']
    pop = city['pop']
    season = city['season']
    market = city['market']
    t = TESTIMONIALS[testimonial_idx % len(TESTIMONIALS)]

    # City-specific pain sections
    pain_sections = {
        "Los Angeles": {
            "pain1": "Los Angeles HVAC contractors operate in one of the most competitive service markets in the country. With over 4 million residents spread across dozens of distinct neighborhoods — from the scorching Valley to the cooler Westside — every incoming call represents a customer who's already suffering in the heat. When the San Fernando Valley bakes at 108°F and AC units fail simultaneously across Chatsworth, Northridge, and Van Nuys, the phones don't stop ringing.",
            "pain2": "The problem isn't call volume — it's what happens to those calls after business hours. LA homeowners search Google at 9 PM when their unit dies. They call the first result. If you go to voicemail, they hang up and call the next contractor. By morning, that $1,200 repair job belongs to your competitor. In a market this size, that happens dozens of times per week across every HVAC operation.",
            "pain3": "Small and mid-size HVAC businesses in LA are caught in a squeeze: they can't afford a full-time receptionist for $3,000/month, but they can't afford to miss calls that represent their entire profit margin. The solution isn't hiring — it's deploying AI that handles the call, captures the lead, and texts you instantly so you can respond when it matters.",
        },
        "San Diego": {
            "pain1": "San Diego's split personality — mild coast, brutal inland — creates an unusual HVAC challenge. Contractors who serve El Cajon, Santee, Spring Valley, and Escondido deal with summer heat that regularly tops 100°F, while their coastal clients need heat pump maintenance and year-round service. This geographic spread means the phone rings all year, not just in summer.",
            "pain2": "The marine layer that tourists love is actually an obstacle for HVAC contractors. Homeowners and property managers in Mission Hills, Normal Heights, and North Park don't think they need AC — until a Santa Ana wind event hits and the temperature jumps 20 degrees in two hours. Emergency calls flood in and contractors who aren't answering lose those jobs permanently.",
            "pain3": "San Diego's strong military presence and large property management sector add commercial contracts on top of residential demand. Property managers in particular call once — if they can't reach you, they move down the list and build a relationship with whoever answered. Syntharra ensures San Diego HVAC contractors capture every inquiry, every time.",
        },
        "San Jose": {
            "pain1": "Silicon Valley homeowners are accustomed to instant digital service. When they call their HVAC contractor and hit voicemail, they don't leave a message — they Google the next option. The expectation of immediate response that tech culture has created in this market means HVAC contractors face a higher abandonment rate than in almost any other US city.",
            "pain2": "Santa Clara County's housing market — where the median home value exceeds $1.5 million in many neighborhoods — creates significant opportunity for HVAC contractors who show up professionally. A missed call in Willow Glen or Almaden Valley isn't just a lost repair ticket; it's a lost multi-year service relationship with a homeowner who will spend tens of thousands on HVAC over their lifetime.",
            "pain3": "The commercial density in downtown San Jose and along the Route 101 corridor means HVAC contractors serve everything from single-family homes in Cambrian Park to large office complexes near SAP Center. After-hours facility emergencies at commercial properties are high-value calls that go to whoever answers first — that has to be you.",
        },
        "San Francisco": {
            "pain1": "San Francisco's HVAC market is dominated by commercial and multi-unit residential accounts — buildings in SoMa, the Tenderloin, and Mission District require constant maintenance, and a single large property management relationship can be worth $20,000+ annually. These clients call at odd hours and expect professional handling every time.",
            "pain2": "Contractors who serve the full Bay Area — from Daly City to the Peninsula to the East Bay — deal with temperature variation that keeps demand active across all seasons. Walnut Creek and Concord regularly hit 100°F+ while the Sunset District barely breaks 65°F. Managing this spread requires always-on call coverage that no human receptionist can provide cost-effectively.",
            "pain3": "Building owners and HOA managers in San Francisco are notoriously demanding. They conduct due diligence before hiring contractors and a missed initial inquiry is rarely recovered. Syntharra gives SF HVAC contractors enterprise-grade call handling at a fraction of the cost of a dedicated phone line team.",
        },
        "Fresno": {
            "pain1": "Fresno is ground zero for HVAC emergencies. The Central Valley summer — sustained heat above 100°F for months — puts genuine medical risk on the table for elderly residents and young children. When AC fails in a Fresno home in July, it is not an inconvenience; it is a health crisis. Homeowners call in a panic, and they need to reach someone immediately.",
            "pain2": "Fresno's demographic mix — including large Latino and Hmong communities alongside longtime Central Valley families — means contractors serve clients across a wide range of communication preferences. First-generation homeowners may be more hesitant to leave voicemails but will engage with a live voice. Syntharra's AI answers every call with the professionalism of a trained receptionist.",
            "pain3": "The Fresno market is intensely competitive during peak summer months. Contractors who built their reputation on reliability are being undercut by new entrants who are more available by phone. Losing the perception of availability — even temporarily — can cost years of customer loyalty. Never let that happen again.",
        },
        "Sacramento": {
            "pain1": "Sacramento's heat is relentless and its geography is sprawling. Contractors serving Elk Grove, Folsom, Rancho Cordova, Roseville, and Citrus Heights cover hundreds of square miles. A crew out on a job in Folsom can't answer a call coming in from Natomas — and that 90-second window before a customer hangs up is the difference between winning and losing the job.",
            "pain2": "Sacramento's housing boom has filled the suburbs with newer homes that require regular maintenance and emergency service. New homeowners in Elk Grove and West Sacramento are establishing their contractor relationships right now. The business that answers first — and sounds most professional — is the one that gets the multi-year maintenance contract.",
            "pain3": "State government and commercial real estate anchor Sacramento's economy. Facility managers for Capitol-area office buildings and state agency properties call contractors during business hours — but emergencies don't respect schedules. Syntharra captures every call, captures the lead details, and texts the owner instantly so nothing falls through the cracks.",
        },
        "Long Beach": {
            "pain1": "Long Beach's port-adjacent neighborhoods face a unique combination: industrial humidity from the harbor combined with summer heat creates persistent HVAC demand across dense residential areas like Bixby Knolls, Signal Hill, and North Long Beach. Older housing stock in these neighborhoods means more frequent service calls and emergency breakdowns.",
            "pain2": "Long Beach sits at the intersection of LA's South Bay and Orange County markets. Contractors here compete with both LA-based firms and OC operations — the contractor who sounds most professional and responds fastest wins. In this market, your phone answering is your first impression, and first impressions are made in the first 10 seconds.",
            "pain3": "The dense apartment and condo market along the coast means property managers are high-value recurring clients for Long Beach HVAC contractors. These clients call once — if you're not available or your voicemail message doesn't impress, they move on. Syntharra ensures you never present as unavailable.",
        },
        "Bakersfield": {
            "pain1": "Bakersfield is in a category of its own for heat. Triple-digit temperatures from May through October are the norm, not the exception. Kern County's oil industry workers, agricultural families, and growing commuter population depend on functioning HVAC for their health and productivity. When units fail in Bakersfield, customers call every number they can find.",
            "pain2": "The Bakersfield HVAC market operates at full capacity during summer months — technicians are booked out, parts are on backorder, and contractors are turning away business. In this environment, the HVAC companies that grow are not the ones doing the most installs; they are the ones that capture every inquiry, prioritize correctly, and never lose a lead to a missed call.",
            "pain3": "East Bakersfield, Oildale, and the newer developments south of Stockdale Highway have distinct market dynamics. Working families in Oildale need fast, affordable emergency service. Newer homeowners in the south want professional, reliable contractors. Syntharra's AI captures the caller's needs, urgency level, and contact details — giving you a qualified lead before you call back.",
        },
        "Anaheim": {
            "pain1": "Anaheim's identity as a resort destination belies its residential HVAC reality. The neighborhoods east of Disneyland — Anaheim Hills, Yorba Linda border areas, and the dense corridors around Lincoln and Ball — see sustained summer demand that rivals any market in Southern California. Aging housing stock plus summer heat creates a constant call flow.",
            "pain2": "Orange County HVAC competition is fierce. Contractors in Anaheim compete with companies based in Fullerton, Garden Grove, Santa Ana, and even north Orange County. In this crowded market, responsiveness is a real differentiator. A homeowner who calls three contractors and only one answers is choosing that contractor — not for price, not for reviews, just for availability.",
            "pain3": "Commercial HVAC in Anaheim's resort district is a separate high-value market. Hotel and hospitality facility managers expect enterprise-level responsiveness from their contractors. Missing a call from a hotel facilities director is not just losing one job — it is losing a recurring commercial account worth thousands per month.",
        },
        "Santa Ana": {
            "pain1": "Santa Ana is the most densely populated city in Orange County, with a predominantly Spanish-speaking community and a large proportion of rental housing. Property owners and residents here place enormous value on contractors who are responsive and accessible. A ringing phone that goes to an English-only voicemail is a lost lead in Santa Ana.",
            "pain2": "The high density of multi-family housing in Santa Ana means HVAC service calls cluster — when one unit in a complex fails, others often follow. Property managers who handle 10-20 units in a building become extremely valuable recurring clients. The contractor they call first and trust most gets every call. That trust is built on consistent, professional availability.",
            "pain3": "Santa Ana's HVAC contractors serve a market that is price-sensitive but also deeply loyal once a relationship is established. First impressions matter enormously. Syntharra's AI answers in under three seconds, captures the caller's name, address, and problem description, and texts the owner immediately — giving contractors the information to respond quickly and professionally.",
        },
        "Riverside": {
            "pain1": "Riverside is the economic hub of the Inland Empire, and its HVAC market is one of California's most intense. Sitting in a natural heat basin that channels hot air from the desert, Riverside regularly sees temperatures above 110°F in summer. Residential and commercial AC failures during peak heat are handled as emergencies — and customers need to reach someone fast.",
            "pain2": "The Inland Empire's rapid growth has created a large market of homeowners who are new to the region and don't have established contractor relationships. These homeowners search Google when their AC fails and call the first few results. The contractors that answer — and sound professional — lock in new customers who will stay for years.",
            "pain3": "University of California Riverside and the region's growing commercial sector create a steady commercial HVAC demand alongside residential. Facility managers, property management companies, and commercial building owners call during and after hours. Syntharra ensures Riverside HVAC contractors never leave a high-value commercial inquiry on the table.",
        },
        "Stockton": {
            "pain1": "Stockton's location at the edge of the Sacramento-San Joaquin Delta gives it a climate unlike anywhere else in the Central Valley: sweltering summers followed by cold, foggy 'tule fog' winters. HVAC contractors here stay busy across both seasons — summer AC emergencies give way to heating season calls without a break. The phone rings twelve months a year.",
            "pain2": "Stockton's diverse neighborhoods — from the established homes in Lincoln Village to the newer developments in the south — represent a wide range of HVAC equipment ages. Older neighborhoods like Brookside and Quail Lakes have systems due for replacement. Newer areas need maintenance contracts. Each segment calls differently, and all of them need to reach a contractor who answers.",
            "pain3": "Stockton's HVAC market is maturing rapidly as the city grows. Contractors who established themselves as reliable and responsive in the past few years are building multi-year maintenance relationships that generate recurring revenue. The key differentiator? Availability. Customers who can reach you at 7 PM when their heater goes out in December become lifetime clients.",
        },
        "Irvine": {
            "pain1": "Irvine is the premium end of the Southern California HVAC market. Planned communities like Woodbridge, Northwood, and Quail Hill have newer, more complex HVAC systems — multi-zone, smart thermostat integrated, high-efficiency — that require specialized knowledge and premium service. Homeowners here have high expectations and limited patience for contractors who don't respond professionally.",
            "pain2": "Irvine homeowners have high disposable income and will pay premium prices for contractors who deliver professional service. But premium service starts with the first interaction. A contractor whose phone goes to voicemail during a peak period is immediately perceived as unprofessional — in a market where Yelp and Google reviews dominate, that perception can cost far more than one missed call.",
            "pain3": "The UCI campus, Irvine Spectrum, and the dense commercial corridors along Alton Parkway create substantial commercial HVAC opportunities for contractors in the area. Commercial clients in Irvine are particularly demanding about responsiveness. Syntharra ensures every call — residential or commercial — is answered professionally and the lead is captured within seconds.",
        },
        "Chula Vista": {
            "pain1": "Chula Vista has become one of California's fastest-growing cities, with major residential development spreading east toward the Otay Ranch and Eastlake communities. New homes in these areas represent prime opportunities for HVAC contractors to establish first-time maintenance relationships. But new homeowners research and call multiple contractors — the one who answers wins.",
            "pain2": "Chula Vista's proximity to the US-Mexico border creates a bilingual market that many HVAC contractors are not prepared to serve. A significant portion of residents and property owners in the western neighborhoods of Chula Vista prefer to communicate in Spanish. Contractors who handle bilingual calls professionally have a real competitive advantage that most of their competitors are ignoring.",
            "pain3": "The South Bay's year-round mild climate doesn't eliminate HVAC demand — it spreads it. Heat pump maintenance, indoor air quality systems, and commercial refrigeration keep contractors busy across all seasons. Property managers overseeing the large apartment complexes along Third Avenue and Broadway are recurring revenue anchors for Chula Vista HVAC operations.",
        },
        "Fontana": {
            "pain1": "Fontana bakes. Sitting in the Inland Empire heat basin with the San Gabriel Mountains blocking ocean air, Fontana regularly reaches 108-112°F during peak summer. The city's blend of working-class neighborhoods and rapid new development means both aging systems prone to failure and new systems needing setup and maintenance. The call volume in summer is relentless.",
            "pain2": "Fontana's large warehouse and distribution sector — serving companies along the I-10 corridor — creates significant commercial HVAC demand. Facility managers for Amazon, UPS, and regional distribution centers need HVAC contractors who are responsive and professional. Commercial contracts are worth substantially more than residential calls and are lost instantly when the contractor doesn't answer.",
            "pain3": "The Inland Empire HVAC market is highly competitive, but it rewards professionalism. In Fontana's mix of established neighborhoods and new developments in the north, the contractors who grow are not the cheapest — they are the most available, most responsive, and most trustworthy. Syntharra gives every Fontana contractor enterprise-level availability at $697/mo.",
        },
        "Moreno Valley": {
            "pain1": "Moreno Valley has grown dramatically in recent years, driven by affordable housing and logistics industry expansion. This growth means a large population of newer residents who do not have established HVAC contractor relationships. When their system fails on a 105°F day, they search Google and call whoever looks credible. The first contractor to answer is the one who gets the job.",
            "pain2": "The housing stock in Moreno Valley spans a wide range — from 1980s track homes in the established western neighborhoods to brand-new builds near the Inland Valley Medical Center. Older systems fail frequently and unexpectedly. New systems need programming, setup, and first-year maintenance. Both segments are calling simultaneously during peak season, and contractors who can't handle the volume lose business.",
            "pain3": "Moreno Valley's HVAC contractors compete with firms from Riverside, Perris, and even Rancho Cucamonga. The differentiator is not price — it is responsiveness. When three contractors are bidding on the same job, the one who called back within 10 minutes wins. Syntharra's instant-text alerts ensure Moreno Valley contractors know about every call the moment it happens.",
        },
        "Glendale": {
            "pain1": "Glendale's location at the base of the Verdugo Mountains gives it a microclimate that intensifies summer heat. While coastal LA communities enjoy moderate temperatures, Glendale and neighboring Burbank sit in a hot air basin that pushes summer temps to 100°F+ with frequency. HVAC demand here outpaces what most small contractor operations can manually track.",
            "pain2": "Glendale has one of the largest Armenian-American communities in the United States, as well as significant Latino and Korean populations. Multi-unit housing in neighborhoods like Adams Square and Tropico means property managers oversee dozens of units — when they have an HVAC emergency, they need a contractor who answers, communicates professionally, and shows up. Voicemail doesn't work in this market.",
            "pain3": "The commercial corridors along Brand Boulevard and Central Avenue, plus Glendale's significant medical office density near Adventist Health Glendale, create high-value commercial HVAC accounts. Facility managers at medical office buildings have zero tolerance for contractor unavailability — these are premium accounts that go to the most responsive bidder.",
        },
        "Huntington Beach": {
            "pain1": "Huntington Beach's reputation as 'Surf City' understates its HVAC market reality. The coastal areas enjoy mild temperatures, but properties just a few miles inland — along Edinger, Warner, and Slater — see real summer heat. The high property values throughout HB mean homeowners have money to spend on quality HVAC service and they expect instant responsiveness.",
            "pain2": "Huntington Beach has an active short-term rental and vacation property market. Property managers overseeing beach houses and investment properties need HVAC contractors who are available around the clock — a system failure on a holiday weekend with guests in residence is an emergency that can cost a 5-star review. Contractors who answer those calls build the most valuable client relationships in the market.",
            "pain3": "The commercial density along Beach Boulevard — one of the longest commercial corridors in Orange County — creates consistent commercial HVAC demand. Restaurant HVAC, retail HVAC, and medical office systems all need service providers who answer the phone. In a market where Yelp reviews drive significant business, the contractor who answers professionally and responds fast dominates the leaderboard.",
        },
        "Oxnard": {
            "pain1": "Oxnard's position at the edge of the Pacific creates a year-round HVAC market that's different from most of California. Coastal fog and temperature swings mean heat pumps and dual-zone systems are common. Agricultural operations and commercial cold storage facilities add a commercial dimension that keeps contractors busy outside the traditional residential peak season.",
            "pain2": "Ventura County's second-largest city has a large Spanish-speaking community, significant agricultural worker population, and growing residential developments east of the 101. Contractors who serve this diverse market need to handle calls professionally across all segments. Property managers overseeing agricultural worker housing are particularly high-volume clients whose calls come at all hours.",
            "pain3": "The Port of Hueneme and adjacent industrial facilities create substantial commercial HVAC demand in Oxnard. Facility managers at port operations and food processing plants need responsive contractors — downtime in a food processing environment is measured in tens of thousands of dollars per hour. Contractors who answer, capture the details, and call back fast win these premium contracts.",
        },
        "Portland": {
            "pain1": "Portland's HVAC market was transformed by the 2021 heat dome. Before that event, most Portland homes — particularly in inner neighborhoods like Hawthorne, Division, and the Pearl District — had no AC at all. After 116°F killed hundreds and left tens of thousands without relief, the entire region rushed to install cooling. Portland's HVAC demand has been structurally transformed.",
            "pain2": "The post-heat-dome installation wave created a generation of new AC systems across Portland that now require ongoing maintenance. Every home that installed mini-splits or central air in 2021-2023 is entering its first maintenance cycle. At the same time, Portland winters — amplified by La Niña patterns — create significant heating season demand. Portland HVAC contractors now operate true year-round businesses.",
            "pain3": "Portland's tech industry and sustainability-focused culture have created a market segment that actively seeks smart HVAC, heat pump technology, and efficiency upgrades. These customers research extensively and call multiple contractors — but they also respond well to professional, immediate service. Contractors who answer these calls professionally and follow up fast win the high-value installation and upgrade market.",
        },
    }

    city_pain = pain_sections.get(name, {
        "pain1": f"{name}'s HVAC market demands constant availability. Whether it's peak summer heat or winter heating emergencies, contractors who miss calls lose jobs to competitors who answer.",
        "pain2": f"With a population of {pop}, {name} generates significant HVAC call volume throughout the year. Every missed call represents revenue that goes directly to your competition.",
        "pain3": f"The {name} market rewards responsiveness. Homeowners and property managers call once — if you don't answer, they call the next contractor. Syntharra ensures you never miss that call.",
    })

    # City-specific FAQ questions (4th question varies by city)
    climate_faqs = {
        "Los Angeles": ("Does Syntharra handle after-hours calls during LA heat waves?", "Absolutely. LA heat waves are precisely when HVAC call volume spikes hardest — often doubling or tripling normal call rates within 24 hours of a heat advisory. Syntharra's AI handles unlimited concurrent calls during peak events, so even when half of LA's AC units are failing simultaneously, every customer who calls your number gets a professional response, not a busy signal or voicemail."),
        "San Diego": ("Can Syntharra handle calls from both coastal and inland San Diego customers?", "Yes. Whether your caller is in Pacific Beach dealing with a heat pump question or in El Cajon with a failed AC unit in 105°F heat, Syntharra captures every call the same way — professionally, immediately, and with full lead details texted to you. The AI doesn't know geography; it knows how to answer, qualify, and capture every caller."),
        "San Jose": ("Will Silicon Valley customers know they're talking to AI?", "Most won't, and it doesn't matter to them. What Silicon Valley customers care about is instant, professional response. Syntharra answers in under 3 seconds, collects their issue, captures their contact details, and texts you immediately. Tech-savvy customers appreciate efficient service — that's exactly what Syntharra delivers."),
        "San Francisco": ("Does Syntharra work for commercial HVAC accounts in San Francisco?", "Yes. Commercial property managers and building owners expect professional call handling at all hours. Syntharra answers every call — whether it's a residential client in the Richmond or a facility manager in SoMa — with the same professional response, captures the details, and alerts you immediately. Commercial clients specifically value the consistency that AI call handling provides."),
        "Fresno": ("How does Syntharra handle heat emergency calls in Fresno?", "When a Fresno homeowner calls in panic because their AC failed on a 107°F day, Syntharra answers immediately, acknowledges the urgency, captures their address and contact details, and texts you right away so you can triage. You decide how to prioritize — Syntharra ensures you have every lead captured and no one goes to voicemail during the highest-stakes moments of your business year."),
        "Sacramento": ("Can Syntharra handle calls for contractors serving greater Sacramento — Elk Grove, Roseville, Folsom?", "Yes. Syntharra works for any caller who dials your number, regardless of their location. Whether your customer is in midtown Sacramento or in Folsom 30 miles east, the call is answered the same way, the details are captured, and you're texted immediately. Your service area doesn't constrain Syntharra's ability to answer professionally."),
        "Long Beach": ("Does Syntharra handle calls for Long Beach contractors who also serve LA and Orange County?", "Yes. If your number serves customers in Long Beach, San Pedro, Carson, or across the South Bay, every call to that number is answered and captured by Syntharra. You can serve a multi-city territory with a single Syntharra-connected number, and every lead is texted to you the moment the call ends."),
        "Bakersfield": ("How does Syntharra handle the intense call volume during Bakersfield's summer heat?", "Syntharra has no call volume ceiling — it handles concurrent calls simultaneously with no degradation in service quality. During Bakersfield's brutal summer peaks when every AC contractor in town is being called simultaneously, Syntharra ensures every caller to your number gets a professional answer rather than a voicemail. That's how you capture revenue your competitors are losing."),
        "Anaheim": ("Does Syntharra work for HVAC contractors serving the Anaheim Hills and resort district?", "Yes. Whether you're answering calls from Anaheim Hills homeowners with high-end systems or commercial inquiries from the resort district, Syntharra handles every call professionally. The AI captures the caller's location, the nature of the issue, and their contact details, then texts you so you can prioritize and respond appropriately."),
        "Santa Ana": ("Can Syntharra handle calls from Spanish-speaking customers in Santa Ana?", "Syntharra supports bilingual call handling. For Santa Ana contractors serving a predominantly Spanish-speaking market, this is a significant advantage. Many of your competitors are losing Spanish-speaking callers to language barriers — Syntharra captures those leads and texts you the details so you can respond in the caller's preferred language."),
        "Riverside": ("How does Syntharra handle emergency calls during Inland Empire heat events?", "During extreme heat events when temperatures in Riverside and the Inland Empire reach 110°F+, HVAC call volume spikes dramatically. Syntharra handles every call to your number simultaneously — there's no limit and no degradation in service. Every caller gets a professional response, their details are captured, and you're alerted instantly so you can prioritize the true emergencies."),
        "Stockton": ("Does Syntharra cover both heating and cooling season calls in Stockton?", "Yes. Stockton's dual-season HVAC market — summer cooling emergencies and winter heating failures — means your phone rings year-round. Syntharra is active 24/7/365 and handles both seasonal call patterns equally well. Whether a caller needs emergency AC repair in August or their furnace replaced in December, every call is captured and sent to you."),
        "Irvine": ("Will Syntharra meet the expectations of Irvine's premium homeowner market?", "Yes. Irvine homeowners expect professional, immediate service from every contractor they interact with. Syntharra answers in under 3 seconds with a professional greeting, captures the issue and contact details thoroughly, and provides a seamless experience. The AI is indistinguishable from a trained human receptionist in the interactions that matter — first contact and lead capture."),
        "Chula Vista": ("Can Syntharra handle bilingual calls for Chula Vista HVAC contractors?", "Yes. Syntharra supports bilingual call handling for English and Spanish, which is a meaningful advantage in Chula Vista's market. Many of your potential customers prefer to communicate in Spanish and will move on from a contractor who can't accommodate that. Syntharra captures every bilingual lead and texts you the details so you can respond in the customer's preferred language."),
        "Fontana": ("How does Syntharra help Fontana HVAC contractors capture commercial accounts?", "Commercial clients in Fontana's industrial corridor — facility managers for warehouses, distribution centers, and manufacturing operations along I-10 — make single calls and decide quickly. Syntharra ensures every commercial inquiry is answered professionally, the contact details and nature of the problem are captured immediately, and you're alerted so you can prioritize high-value commercial opportunities."),
        "Moreno Valley": ("How quickly does Syntharra alert me when a Moreno Valley customer calls?", "Within seconds of the call ending, you receive a text with the caller's name, phone number, address, and a summary of their issue. Most Syntharra contractors report calling back within 2-5 minutes of receiving the alert. In Moreno Valley's competitive HVAC market, that response speed is often the deciding factor in who gets the job."),
        "Glendale": ("Does Syntharra handle calls from Armenian and Spanish-speaking customers in Glendale?", "Yes. Syntharra supports bilingual handling and is trained to serve diverse communities professionally. For Glendale contractors serving Armenian-American, Latino, and Korean-American communities, professional bilingual call handling is a genuine competitive differentiator. Syntharra captures every lead from every community you serve."),
        "Huntington Beach": ("Can Syntharra handle after-hours calls for vacation and rental properties in Huntington Beach?", "Yes. Property managers and vacation rental hosts need contractors who answer at 9 PM on a Saturday when a system fails with guests in the property. Syntharra is always on — 24/7, 365 days a year — and handles every after-hours call with the same professionalism as business hours calls. Your property management clients will notice the difference immediately."),
        "Oxnard": ("Does Syntharra work for Oxnard contractors with agricultural and commercial clients?", "Yes. Whether your caller is a homeowner in a residential neighborhood, a property manager in a commercial complex, or a facility manager at an agricultural operation, Syntharra captures every call the same way. The AI handles calls in English and Spanish, which matters particularly in Oxnard's agricultural worker housing market."),
        "Portland": ("Does Syntharra work year-round for Portland contractors handling both heat and cold seasons?", "Yes. Portland's newly expanded HVAC season — intense summer heat waves plus significant rainy season heating demand — means contractors need year-round call coverage. Syntharra operates 24/7/365 and handles both AC emergency calls in summer and heating emergencies in winter with the same professional response and immediate owner alerts."),
    }

    climate_faq = climate_faqs.get(name, (
        f"How does Syntharra help during {name}'s {season}?",
        f"Syntharra operates 24/7/365, meaning the AI is answering calls during peak demand periods just as reliably as during slow months. During {name}'s {season}, when call volume is highest and the cost of missed calls is greatest, Syntharra ensures every caller reaches a professional voice and every lead is captured and texted to you immediately."
    ))

    # Testimonial assignment
    testimonial = TESTIMONIALS[testimonial_idx % len(TESTIMONIALS)]

    state_full = "California" if state == "CA" else ("Oregon" if state == "OR" else state)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="apple-touch-icon" href="/favicon.svg">
  <meta name="theme-color" content="#4d41df">
  <title>{name} HVAC Answering Service — 24/7 AI from $697/mo | Syntharra</title>
  <meta name="description" content="{name} HVAC answering service. 24/7 AI receptionist trained on HVAC scripts — captures every lead, texts you instantly. Flat $697/mo. Free 200-minute pilot. Live in 24 hours.">
  <link rel="canonical" href="https://www.syntharra.com/hvac-answering-service-{slug}.html">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://www.syntharra.com/hvac-answering-service-{slug}.html">
  <meta property="og:title" content="{name} HVAC Answering Service — 24/7 AI from $697/mo">
  <meta property="og:description" content="{name} HVAC answering service. 24/7 AI that answers in under 3 seconds, captures lead details, and texts you instantly. Never miss another call.">
  <meta property="og:image" content="https://raw.githubusercontent.com/Syntharra/syntharra-automations/main/brand-assets/email-signature/syntharra-icon.png">
  <meta property="og:site_name" content="Syntharra">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:url" content="https://www.syntharra.com/hvac-answering-service-{slug}.html">
  <meta name="twitter:title" content="{name} HVAC Answering Service — 24/7 AI from $697/mo">
  <meta name="twitter:description" content="{name} HVAC answering service. 24/7 AI that answers in under 3 seconds, captures lead details, and texts you instantly. Never miss another call.">
  <meta name="twitter:image" content="https://raw.githubusercontent.com/Syntharra/syntharra-automations/main/brand-assets/email-signature/syntharra-icon.png">

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@400;700;800&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
  <!-- Tailwind CDN (for nav utility classes) -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>tailwind.config={{theme:{{extend:{{colors:{{primary:'#4d41df'}}}}}}}}</script>
  <style>
{CSS}
  </style>
</head>
<body>

{NAV}

<!-- HERO -->
<div class="hero">
  <div class="container">
    <span class="eyebrow">{name}, {state} &bull; HVAC Answering Service</span>
    <h1>The <span class="accent">{name} HVAC</span><br>Answering Service That<br>Never Misses a Call</h1>
    <p class="hero-sub">{climate}</p>
    <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap">
      <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="btn-primary">Get Your Free 200-Min Pilot &rarr;</a>
      <a href="/how-it-works.html" class="btn-secondary">See How It Works</a>
    </div>
    <span class="fine-print">No credit card. No contract. Live in 24 hours. $697/mo flat after trial.</span>
  </div>
</div>

<!-- PAIN SECTION -->
<section style="background:#fafafa">
  <div class="container">
    <span class="section-label">The Problem</span>
    <h2>Why {name} HVAC Contractors Lose Jobs Every Day</h2>
    <p>{city_pain["pain1"]}</p>
    <p>{city_pain["pain2"]}</p>
    <p>{city_pain["pain3"]}</p>
  </div>
</section>

<!-- WHAT SYNTHARRA DOES -->
<section>
  <div class="container">
    <span class="section-label">The Solution</span>
    <h2>24/7 AI Call Handling Built for {name} HVAC</h2>
    <p>Syntharra is an AI voice agent trained specifically on HVAC service calls. It answers your phone in under 3 seconds, collects the caller&rsquo;s details and problem description, and texts you immediately — so you can respond to real leads fast instead of returning calls that are already cold.</p>
    <div class="card-grid">
      <div class="card">
        <div style="font-size:32px;margin-bottom:12px">&#9889;</div>
        <div class="step-title">Answers in Under 3 Seconds</div>
        <p style="margin-bottom:0">Every call to your number is answered within 3 seconds, 24 hours a day, 7 days a week. No rings to voicemail, no missed calls during peak season, no calls lost to competitors because you were already on the line.</p>
      </div>
      <div class="card">
        <div style="font-size:32px;margin-bottom:12px">&#128221;</div>
        <div class="step-title">Captures Full Lead Details</div>
        <p style="margin-bottom:0">Syntharra collects the caller&rsquo;s name, address, phone number, and a clear description of their HVAC issue. You receive a qualified lead with context — not just a phone number you have to call back blind.</p>
      </div>
      <div class="card">
        <div style="font-size:32px;margin-bottom:12px">&#128241;</div>
        <div class="step-title">Texts You Instantly</div>
        <p style="margin-bottom:0">The moment the call ends, you receive a text alert with every detail captured. Most Syntharra contractors respond to leads within minutes. In {name}&rsquo;s competitive HVAC market, that speed wins jobs.</p>
      </div>
    </div>
  </div>
</section>

<!-- ROI MATH BOX -->
<section style="background:#f5f2ff">
  <div class="container">
    <span class="section-label">The Math</span>
    <h2>What Missed Calls Are Actually Costing You in {name}</h2>
    <p>Most HVAC contractors in {name} don&rsquo;t track missed calls — they just know revenue feels inconsistent. Here&rsquo;s what the numbers actually look like when you put a dollar value on missed call volume.</p>
    <div class="math-box">
      <h3>Missed Call Revenue Calculator — {name} HVAC</h3>
      <div class="math-row"><span>Average HVAC ticket value</span><span>$800</span></div>
      <div class="math-row"><span>Estimated missed calls per week</span><span>4 calls</span></div>
      <div class="math-row"><span>Lost revenue per week</span><span>$3,200</span></div>
      <div class="math-row"><span>Lost revenue per month</span><span>$13,800</span></div>
      <div class="math-row"><span>Lost revenue per year</span><span style="color:#ef4444">$166,400</span></div>
      <div class="math-row"><span>Syntharra annual cost</span><span>$8,364</span></div>
      <div class="math-row"><span>Net annual ROI</span><span>$158,000+</span></div>
    </div>
    <p style="font-size:13px;color:#777587;margin-bottom:0">Conservative estimate assuming 4 missed calls/week at $800 average ticket. Many contractors report capturing 8-12 missed calls/week. Results vary.</p>
  </div>
</section>

<!-- HOW IT WORKS -->
<section>
  <div class="container">
    <span class="section-label">How It Works</span>
    <h2>Live in {name} in Under 24 Hours</h2>
    <p>Getting Syntharra running for your {name} HVAC operation takes less time than a typical service call. There&rsquo;s no hardware, no complex setup, and no technical expertise required.</p>
    <div class="steps">
      <div class="step">
        <div class="step-num">01</div>
        <div class="step-title">Forward Your Number</div>
        <p>Forward your existing business line — or set up a new local {name} number — to Syntharra. Takes 5 minutes with your carrier. No downtime, no disruption.</p>
      </div>
      <div class="step">
        <div class="step-num">02</div>
        <div class="step-title">AI Answers Instantly</div>
        <p>Every call is answered in under 3 seconds by an AI trained on HVAC service conversations. The AI collects the caller&rsquo;s name, address, and issue description professionally.</p>
      </div>
      <div class="step">
        <div class="step-num">03</div>
        <div class="step-title">You Get a Text</div>
        <p>The moment the call ends, you receive a complete lead summary via text. You call back with full context, sound professional, and win the job before your competitor even knows it was available.</p>
      </div>
    </div>
  </div>
</section>

<!-- TESTIMONIAL -->
<section style="background:#fafafa">
  <div class="container">
    <div class="testimonial">
      <blockquote>&ldquo;{testimonial["quote"]}&rdquo;</blockquote>
      <cite>&mdash; {testimonial["name"]}, {testimonial["company"]}, {testimonial["location"]}</cite>
    </div>
  </div>
</section>

<!-- FAQ -->
<section>
  <div class="container">
    <span class="section-label">FAQ</span>
    <h2>Questions from {name} HVAC Contractors</h2>

    <div class="faq-item">
      <div class="faq-q">Does Syntharra work for {name} HVAC contractors?</div>
      <div class="faq-a">Yes — Syntharra is designed specifically for trade service businesses including HVAC contractors in {state_full}. It works for any HVAC operation regardless of size: solo operators, 2-5 person crews, and larger regional operations. As long as you have a phone number customers call, Syntharra can answer it.</div>
    </div>

    <div class="faq-item">
      <div class="faq-q">What happens when my {name} customer calls after hours?</div>
      <div class="faq-a">The exact same thing that happens during business hours: the AI answers in under 3 seconds, collects the caller&rsquo;s name, address, phone number, and issue description, and texts you immediately. You decide when and whether to call back — but the lead is captured. No more lost jobs because someone called at 8 PM and hit your voicemail.</div>
    </div>

    <div class="faq-item">
      <div class="faq-q">How quickly can I go live in {name}?</div>
      <div class="faq-a">Most contractors are fully live within 24 hours of signing up. There&rsquo;s no hardware to install, no complex configuration, and no technical background required. You forward your number, we configure the AI for your business, and you start capturing leads immediately. The free 200-minute pilot gives you full functionality from day one.</div>
    </div>

    <div class="faq-item">
      <div class="faq-q">{climate_faq[0]}</div>
      <div class="faq-a">{climate_faq[1]}</div>
    </div>
  </div>
</section>

<!-- CTA -->
<div class="cta-block">
  <div class="container">
    <span class="eyebrow" style="background:rgba(255,255,255,.15);color:#fff">{name} HVAC Answering Service</span>
    <h2 style="margin-top:16px">Stop Losing {name} Jobs to Voicemail</h2>
    <p style="max-width:520px;margin:0 auto 32px">Start your free 200-minute pilot today. No credit card, no contract. Most {name} contractors are live within 24 hours and capturing their first leads the same day.</p>
    <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="btn-primary" style="background:#fff;color:#4d41df;box-shadow:0 12px 40px -8px rgba(0,0,0,0.2)">Start Free Pilot &rarr;</a>
    <span class="fine-print" style="color:rgba(255,255,255,.5)">200 free minutes. No credit card. $697/mo flat after trial.</span>
  </div>
</div>

{FOOTER}

</body>
</html>'''
    return html


def push_file(filename, content, city_name):
    """Push a single file to GitHub via the REST API."""
    url = f"{API}/{filename}"
    encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    payload = json.dumps({
        "message": f"feat(seo): add {city_name} HVAC answering service landing page",
        "content": encoded
    }).encode('utf-8')

    req = urllib.request.Request(url, data=payload, method='PUT')
    for k, v in HEADERS.items():
        req.add_header(k, v)

    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status in (200, 201):
                return True
            return False
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f"  HTTPError {e.code}: {body[:200]}")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print(f"Generating and pushing {len(CITIES)} HVAC city pages...\n")
    ok = 0
    fail = 0

    for i, city in enumerate(CITIES):
        filename = f"hvac-answering-service-{city['slug']}.html"
        content = get_city_content(city, i)
        print(f"[{i+1:02d}/{len(CITIES)}] {filename} ...", end=" ", flush=True)

        success = push_file(filename, content, city['name'])
        if success:
            print("OK")
            ok += 1
        else:
            print("FAIL")
            fail += 1

        if i < len(CITIES) - 1:
            time.sleep(1.5)

    print(f"\nDone. {ok} OK, {fail} FAIL out of {len(CITIES)} pages.")


if __name__ == "__main__":
    main()
