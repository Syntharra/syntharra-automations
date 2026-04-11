#!/usr/bin/env python3
"""Push Concept A homepage to syntharra-website. Run: python tools/push_concept_a.py"""
import requests, base64, sys

TOKEN   = 'GITHUB_TOKEN_REDACTED'
REPO    = 'Syntharra/syntharra-website'
API     = f'https://api.github.com/repos/{REPO}/contents'
HEADERS = {'Authorization': f'token {TOKEN}', 'Content-Type': 'application/json'}

# ── Logo: bare SVG, no box, white text for dark header ───────────────────────
LOGO = '''<svg xmlns="http://www.w3.org/2000/svg" width="158" height="34" viewBox="0 0 158 34" role="img" aria-label="Syntharra">
  <g fill="#6C63FF">
    <rect x="0"  y="21" width="4" height="9"  rx="1"/>
    <rect x="7"  y="17" width="4" height="13" rx="1"/>
    <rect x="14" y="13" width="4" height="17" rx="1"/>
    <rect x="21" y="9"  width="4" height="21" rx="1"/>
  </g>
  <text x="37" y="21" font-family="Inter,Arial,sans-serif" font-weight="700" font-size="16" fill="#ffffff" letter-spacing="-0.48">Syntharra</text>
  <text x="37" y="32" font-family="Inter,Arial,sans-serif" font-weight="500" font-size="8"  fill="#6C63FF" letter-spacing="1.2">GLOBAL AI SOLUTIONS</text>
</svg>'''

HTML = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="apple-touch-icon" href="/favicon.svg">
<meta name="theme-color" content="#6C63FF">
<title>Syntharra | AI Receptionist for HVAC &amp; Trade Businesses</title>
<meta name="description" content="Syntharra AI Receptionist answers every call 24/7 for HVAC contractors. Capture leads, never miss revenue. $697/mo.">
<meta name="keywords" content="AI receptionist, HVAC answering service, 24/7 call answering, AI receptionist for contractors, plumbing answering service, electrical answering service, trade business AI">
<link rel="canonical" href="https://www.syntharra.com/">
<meta property="og:type" content="website">
<meta property="og:url" content="https://www.syntharra.com/">
<meta property="og:title" content="Syntharra | Global AI Solutions — AI Receptionist for Trade Businesses">
<meta property="og:description" content="Stop missing calls. Stop losing $80,000 a year. AI receptionist built for HVAC contractors.">
<meta property="og:image" content="https://www.syntharra.com/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="twitter:card" content="summary_large_image">
<meta property="twitter:url" content="https://www.syntharra.com/">
<meta property="twitter:title" content="Syntharra | Global AI Solutions — AI Receptionist for Trade Businesses">
<meta property="twitter:description" content="Stop missing calls. Stop losing $80,000 a year. AI receptionist built for HVAC contractors.">
<meta property="twitter:image" content="https://www.syntharra.com/og-image.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
html,body{{overflow-x:clip}}
body{{font-family:'Inter',system-ui,sans-serif;background:#060913;color:#fff;-webkit-font-smoothing:antialiased;line-height:1.6}}
a{{text-decoration:none;color:inherit}}
img{{max-width:100%;display:block}}
:root{{
  --navy:#060913;--surface:#15192B;
  --violet:#6C63FF;--violet-l:#8B84FF;--violet-d:#5048D6;
  --ice:#00D4FF;
  --border-subtle:rgba(255,255,255,0.08);
  --text-dim:rgba(255,255,255,0.55);
}}

/* Header */
#header{{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(6,9,19,0.80);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:1px solid var(--border-subtle);height:72px;display:flex;align-items:center;}}
.header-inner{{max-width:1280px;margin:0 auto;padding:0 24px;width:100%;display:flex;align-items:center;justify-content:space-between;gap:24px;}}
.logo-section{{display:flex;align-items:center;flex-shrink:0;}}
.logo-section svg{{height:30px;width:auto;}}
.nav-right{{display:flex;align-items:center;gap:12px;}}

/* Desktop nav pill */
.nav-menu{{display:flex;list-style:none;align-items:center;gap:2px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.10);border-radius:9999px;padding:4px;}}
.nav-menu a{{display:block;padding:7px 18px;border-radius:9999px;font-size:13.5px;font-weight:500;color:rgba(255,255,255,0.65);transition:color .15s,background .15s;white-space:nowrap;}}
.nav-menu a:hover{{color:#fff;background:rgba(255,255,255,0.09);}}
.nav-menu .nav-cta{{background:var(--violet);color:#fff !important;font-weight:600;}}
.nav-menu .nav-cta:hover{{background:var(--violet-d);box-shadow:0 0 16px rgba(108,99,255,0.45);}}

/* Hamburger */
.hamburger{{display:none;flex-direction:column;gap:5px;cursor:pointer;background:none;border:none;padding:6px;}}
.hamburger span{{display:block;width:22px;height:2px;background:#fff;border-radius:2px;transition:transform .3s,opacity .3s;}}

/* Mobile nav */
.mobile-nav{{position:fixed;top:72px;left:0;right:0;bottom:0;z-index:99;background:rgba(6,9,19,0.97);backdrop-filter:blur(24px);overflow-y:auto;padding:24px 24px 40px;transform:translateX(100%);transition:transform .35s cubic-bezier(.4,0,.2,1);}}
.mobile-nav.open{{transform:translateX(0);}}
.mobile-nav-section{{margin-bottom:28px;}}
.mobile-nav-label{{font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--violet-l);margin-bottom:10px;}}
.mobile-nav-link{{display:block;padding:11px 0;font-size:16px;font-weight:500;color:rgba(255,255,255,0.75);border-bottom:1px solid rgba(255,255,255,0.05);transition:color .15s,padding-left .15s;}}
.mobile-nav-link:hover{{color:#fff;padding-left:6px;}}
.mobile-nav-cta{{display:block;margin-top:28px;padding:16px;text-align:center;background:var(--violet);color:#fff;font-weight:700;font-size:16px;border-radius:12px;box-shadow:0 0 20px rgba(108,99,255,0.35);}}

/* Hero */
.hero{{position:relative;min-height:100dvh;padding:160px 24px 80px;display:flex;align-items:center;overflow:hidden;background:linear-gradient(135deg,#060913 55%,#0e0c1f 100%);}}
.hero-glow{{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse 80% 60% at 70% 40%,rgba(108,99,255,0.16) 0%,rgba(0,212,255,0.04) 40%,transparent 70%);}}
.hero-grid{{position:absolute;inset:0;pointer-events:none;opacity:.028;background-image:linear-gradient(rgba(255,255,255,1) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,1) 1px,transparent 1px);background-size:44px 44px;}}
.hero-inner{{max-width:1280px;margin:0 auto;width:100%;position:relative;z-index:1;display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:center;}}

/* Hero copy */
.hero-badge{{display:inline-flex;align-items:center;gap:8px;padding:5px 14px;border-radius:9999px;margin-bottom:24px;background:rgba(21,25,43,0.7);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,0.10);font-size:11px;font-weight:600;letter-spacing:.10em;text-transform:uppercase;color:var(--violet-l);}}
.hero-badge-dot{{width:7px;height:7px;border-radius:50%;background:var(--ice);animation:pdot 2s infinite;}}
@keyframes pdot{{0%,100%{{opacity:1}}50%{{opacity:.5}}}}
.hero-title{{font-size:clamp(2.8rem,5.5vw,4.8rem);font-weight:800;line-height:1.05;letter-spacing:-0.04em;color:#fff;margin-bottom:20px;}}
.hero-grad{{background:linear-gradient(90deg,var(--violet),var(--ice),rgba(255,255,255,0.85));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
.hero-sub{{font-size:1.08rem;font-weight:300;color:rgba(255,255,255,0.52);max-width:440px;line-height:1.78;margin-bottom:36px;}}
.ctas{{display:flex;gap:14px;flex-wrap:wrap;}}
.btn-p{{display:inline-flex;align-items:center;gap:8px;padding:14px 26px;background:#fff;color:#060913;font-weight:700;font-size:14.5px;border-radius:9999px;transition:background .15s,box-shadow .15s;white-space:nowrap;}}
.btn-p:hover{{background:#f0f0ff;box-shadow:0 0 24px rgba(255,255,255,0.10);}}
.btn-g{{display:inline-flex;align-items:center;gap:8px;padding:14px 26px;border:1px solid rgba(255,255,255,0.20);color:#fff;font-weight:500;font-size:14.5px;border-radius:9999px;transition:background .15s;white-space:nowrap;}}
.btn-g:hover{{background:rgba(255,255,255,0.06);}}
.trust-checks{{display:flex;gap:16px;flex-wrap:wrap;margin-top:24px;}}
.tc{{display:flex;align-items:center;gap:6px;font-size:12px;color:rgba(255,255,255,0.40);}}
.tc::before{{content:"✓";color:#4ade80;font-weight:700;font-size:13px;}}

/* Phone UI */
.hero-visual{{position:relative;display:flex;justify-content:flex-end;align-items:center;}}
.phone-wrap{{position:relative;width:100%;max-width:295px;animation:floatS 8s ease-in-out infinite;}}
@keyframes floatS{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-18px)}}}}
.phone-outer{{background:rgba(21,25,43,0.75);border:1px solid rgba(255,255,255,0.13);border-radius:40px;padding:8px;box-shadow:inset 0 1px 0 rgba(255,255,255,0.08),0 40px 80px rgba(0,0,0,0.6);position:relative;}}
.phone-outer::before{{content:'';position:absolute;inset:-28px;background:#6C63FF;filter:blur(60px);opacity:.13;z-index:-1;border-radius:50px;}}
.phone-screen{{background:#0b0c10;border-radius:33px;overflow:hidden;border:1px solid rgba(255,255,255,0.04);display:flex;flex-direction:column;aspect-ratio:9/19.5;}}
.phone-bar{{height:44px;display:flex;align-items:center;justify-content:space-between;padding:0 18px;position:relative;flex-shrink:0;}}
.phone-time{{font-size:10px;font-weight:600;color:#fff;}}
.phone-island{{position:absolute;left:50%;transform:translateX(-50%);width:78px;height:17px;background:#000;border-radius:20px;display:flex;align-items:center;justify-content:center;gap:5px;}}
.phone-island-dot{{width:6px;height:6px;border-radius:50%;background:#22c55e;animation:pdot 1.8s infinite;}}
.phone-island-txt{{font-size:7px;color:#22c55e;font-weight:700;}}
.phone-caller{{padding:14px 18px;display:flex;flex-direction:column;align-items:center;border-bottom:1px solid rgba(255,255,255,0.05);background:linear-gradient(to bottom,rgba(108,99,255,0.10),transparent);flex-shrink:0;}}
.phone-av{{width:46px;height:46px;border-radius:50%;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.10);display:flex;align-items:center;justify-content:center;margin-bottom:6px;font-size:18px;}}
.phone-cn{{font-weight:600;font-size:13px;margin-bottom:2px;}}
.phone-cs{{font-size:9px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--ice);}}
.phone-chat{{flex:1;padding:12px 14px;display:flex;flex-direction:column;gap:9px;overflow:hidden;}}
.cb-c{{display:flex;gap:7px;align-items:flex-start;}}
.cav{{width:20px;height:20px;border-radius:50%;background:#374151;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:7px;font-weight:600;}}
.ct{{background:rgba(55,65,81,0.9);border-radius:12px;border-top-left-radius:3px;padding:7px 10px;font-size:10.5px;color:#d1d5db;max-width:84%;line-height:1.5;}}
.cb-ai{{display:flex;gap:7px;align-items:flex-start;flex-direction:row-reverse;}}
.cav-ai{{width:20px;height:20px;border-radius:50%;background:var(--violet);flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:7px;font-weight:700;box-shadow:0 0 8px rgba(108,99,255,0.5);}}
.ct-ai{{background:rgba(108,99,255,0.12);border:1px solid rgba(108,99,255,0.20);border-radius:12px;border-top-right-radius:3px;padding:7px 10px;font-size:10.5px;color:#fff;max-width:84%;line-height:1.5;}}
.phone-actions{{height:56px;border-top:1px solid rgba(255,255,255,0.05);background:rgba(255,255,255,0.04);display:flex;align-items:center;justify-content:space-between;padding:0 22px;flex-shrink:0;}}
.pbtn{{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:none;cursor:pointer;font-size:13px;}}
.pbtn-end{{background:rgba(239,68,68,0.2);color:#ef4444;}}
.pbtn-ok{{background:rgba(255,255,255,0.08);color:#fff;}}
.pact{{text-align:center;}}
.pact-l{{display:block;font-size:8.5px;color:rgba(255,255,255,0.38);}}
.pact-v{{font-size:9.5px;font-weight:600;color:var(--ice);}}

/* Booking card */
.bcard{{position:absolute;right:-18px;bottom:56px;width:225px;background:rgba(21,25,43,0.88);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,0.10);border-radius:15px;padding:13px;box-shadow:0 20px 40px rgba(0,0,0,0.4);animation:floatF 5s ease-in-out infinite;}}
@keyframes floatF{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(13px)}}}}
.bcard-hd{{display:flex;align-items:center;gap:7px;margin-bottom:9px;font-size:11.5px;font-weight:600;color:#fff;}}
.bcard-time{{margin-left:auto;font-size:9px;color:rgba(255,255,255,0.38);}}
.bcard-body{{background:rgba(0,0,0,0.3);border-radius:10px;padding:9px;border:1px solid rgba(255,255,255,0.05);}}
.bcard-row{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:7px;}}
.bcard-lbl{{font-size:9px;color:rgba(255,255,255,0.38);}}
.bcard-name{{font-size:12px;font-weight:500;color:#fff;}}
.bcard-badge{{background:rgba(108,99,255,0.20);color:var(--violet-l);font-size:9px;padding:3px 7px;border-radius:5px;font-weight:600;font-family:monospace;}}
.bcard-addr{{font-size:9px;color:rgba(255,255,255,0.38);padding-top:6px;border-top:1px solid rgba(255,255,255,0.07);}}

/* Trust bar */
.trust-bar{{padding:30px 24px;background:#060913;border-bottom:1px solid rgba(255,255,255,0.05);}}
.trust-bar-inner{{max-width:1280px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:24px;opacity:.42;}}
.trust-bar-lbl{{font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:rgba(255,255,255,0.5);white-space:nowrap;flex-shrink:0;}}
.trust-logos{{display:flex;align-items:center;gap:28px;flex-wrap:wrap;}}
.trust-logos span{{font-weight:700;font-size:14.5px;color:rgba(255,255,255,0.6);letter-spacing:-.02em;}}

/* Features / Bento */
.features{{padding:96px 24px;background:#FAFAFA;}}
.feat-inner{{max-width:1280px;margin:0 auto;}}
.sec-header{{text-align:center;max-width:600px;margin:0 auto 52px;}}
.sec-eyebrow{{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.10em;text-transform:uppercase;color:var(--violet);background:rgba(108,99,255,0.08);padding:4px 14px;border-radius:20px;margin-bottom:14px;}}
.sec-title{{font-size:clamp(1.75rem,3.5vw,2.7rem);font-weight:800;letter-spacing:-.04em;color:#0f172a;line-height:1.15;margin-bottom:14px;}}
.sec-sub{{color:#64748b;font-size:1rem;line-height:1.7;}}
.bento{{display:grid;grid-template-columns:repeat(12,1fr);gap:18px;}}
.bc{{border-radius:24px;padding:36px;}}
.bc-8{{grid-column:span 8;}}
.bc-4{{grid-column:span 4;}}
.bc-6{{grid-column:span 6;}}
.bc-lt{{background:#fff;border:1px solid #e8e8f0;}}
.bc-dk{{background:#060913;color:#fff;position:relative;overflow:hidden;}}
.bc-dk::before{{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(108,99,255,0.18),transparent);opacity:.6;}}
.bc-dk-in{{position:relative;z-index:1;}}
.bi{{width:44px;height:44px;border-radius:12px;background:rgba(108,99,255,0.10);display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:18px;}}
.bh{{font-size:1.25rem;font-weight:700;color:#0f172a;margin-bottom:8px;letter-spacing:-.02em;}}
.bt{{font-size:.9rem;color:#64748b;line-height:1.7;}}
.bh-dk{{font-size:1.05rem;font-weight:600;color:var(--violet-l);margin-bottom:8px;}}
.bt-dk{{font-size:.875rem;color:rgba(255,255,255,0.48);line-height:1.7;}}
.bn-dk{{font-size:3.4rem;font-weight:800;letter-spacing:-.04em;color:#fff;line-height:1;display:flex;align-items:baseline;gap:6px;}}
.bn-dk-s{{font-size:1.2rem;color:rgba(255,255,255,0.38);font-weight:400;}}
.stats{{display:flex;gap:30px;margin-top:28px;flex-wrap:wrap;}}
.stt{{text-align:center;}}
.stn{{font-size:2.1rem;font-weight:800;letter-spacing:-.04em;color:var(--violet);line-height:1;}}
.stl{{font-size:.72rem;color:#94a3b8;margin-top:4px;}}

/* Dark CTA */
.dark-cta{{padding:96px 24px;background:#060913;position:relative;overflow:hidden;border-top:1px solid rgba(255,255,255,0.05);}}
.dcta-orb1{{position:absolute;top:0;right:0;width:380px;height:380px;background:#6C63FF;border-radius:50%;filter:blur(120px);opacity:.18;pointer-events:none;}}
.dcta-orb2{{position:absolute;bottom:0;left:0;width:280px;height:280px;background:#00D4FF;border-radius:50%;filter:blur(100px);opacity:.10;pointer-events:none;}}
.dcta-inner{{max-width:800px;margin:0 auto;text-align:center;position:relative;z-index:1;}}
.dcta-title{{font-size:clamp(2.4rem,5.5vw,4.4rem);font-weight:800;letter-spacing:-.04em;color:#fff;line-height:1.05;margin-bottom:20px;}}
.dcta-grad{{background:linear-gradient(90deg,var(--violet),var(--ice));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}}
.dcta-sub{{font-size:1.1rem;color:rgba(255,255,255,0.50);max-width:460px;margin:0 auto 36px;font-weight:300;line-height:1.75;}}
.dcta-btns{{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;}}

/* Footer */
footer{{background:#030408;padding:56px 24px 32px;border-top:1px solid rgba(255,255,255,0.05);}}
.foot-inner{{max-width:1280px;margin:0 auto;}}
.foot-grid{{display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;gap:36px;margin-bottom:44px;}}
.foot-brand-txt{{color:rgba(255,255,255,0.38);font-size:.875rem;line-height:1.7;max-width:220px;margin-top:14px;}}
.foot-tag{{color:rgba(255,255,255,0.22);font-size:.75rem;margin-top:8px;}}
.fcol-title{{font-weight:600;font-size:.875rem;color:#fff;margin-bottom:14px;}}
.fcol ul{{list-style:none;display:flex;flex-direction:column;gap:10px;}}
.fcol ul a{{font-size:.875rem;color:rgba(255,255,255,0.42);transition:color .15s;}}
.fcol ul a:hover{{color:#fff;}}
.foot-bottom{{padding-top:26px;border-top:1px solid rgba(255,255,255,0.05);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;font-size:.8rem;color:rgba(255,255,255,0.28);}}
.sdot{{display:inline-flex;align-items:center;gap:6px;}}
.sdot::before{{content:'';width:7px;height:7px;border-radius:50%;background:#4ade80;display:inline-block;}}

/* Responsive */
@media(max-width:1024px){{
  .hero-inner{{grid-template-columns:1fr;gap:52px;}}
  .hero-visual{{justify-content:center;}}
  .bcard{{display:none;}}
  .bc-8,.bc-4,.bc-6{{grid-column:span 12;}}
  .foot-grid{{grid-template-columns:1fr 1fr;}}
}}
@media(max-width:768px){{
  .nav-menu{{display:none;}}
  .hamburger{{display:flex;}}
  .hero{{padding-top:110px;}}
  .bento{{grid-template-columns:1fr;}}
  .bc-8,.bc-4,.bc-6{{grid-column:span 1;}}
  .foot-grid{{grid-template-columns:1fr;}}
  .trust-bar-inner{{flex-direction:column;text-align:center;}}
}}
</style>
</head>
<body>

<header id="header">
  <div class="header-inner">
    <a href="/" class="logo-section" aria-label="Syntharra — Global AI Solutions">
{LOGO}
    </a>
    <div class="nav-right">
      <ul class="nav-menu">
        <li><a href="/#solutions">Solutions</a></li>
        <li><a href="/how-it-works.html">How It Works</a></li>
        <li><a href="/case-studies.html">Results</a></li>
        <li><a href="/demo.html">Demo</a></li>
        <li><a href="/faq.html">FAQ</a></li>
        <li><a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="nav-cta">Book a Call &rarr;</a></li>
      </ul>
      <button class="hamburger" id="hamburger" aria-label="Open menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>

<nav class="mobile-nav" id="mobileNav">
  <div class="mobile-nav-section">
    <div class="mobile-nav-label">Product</div>
    <a href="/#solutions" class="mobile-nav-link">Solutions</a>
    <a href="/how-it-works.html" class="mobile-nav-link">How It Works</a>
    <a href="/demo.html" class="mobile-nav-link">Demo</a>
    <a href="/faq.html" class="mobile-nav-link">FAQ</a>
    <a href="/ai-readiness.html" class="mobile-nav-link">AI Readiness Score</a>
    <a href="/calculator.html" class="mobile-nav-link">Revenue Calculator</a>
    <a href="/plan-quiz.html" class="mobile-nav-link">Which Plan?</a>
  </div>
  <div class="mobile-nav-section">
    <div class="mobile-nav-label">Learn</div>
    <a href="/case-studies.html" class="mobile-nav-link">Case Studies</a>
    <a href="/blog.html" class="mobile-nav-link">Blog</a>
    <a href="/vs-answering-service.html" class="mobile-nav-link">Why AI Wins</a>
    <a href="/hvac.html" class="mobile-nav-link">HVAC</a>
    <a href="/plumbing.html" class="mobile-nav-link">Plumbing</a>
    <a href="/electrical.html" class="mobile-nav-link">Electrical</a>
  </div>
  <div class="mobile-nav-section">
    <div class="mobile-nav-label">Company</div>
    <a href="/about.html" class="mobile-nav-link">About</a>
    <a href="/affiliate.html" class="mobile-nav-link">Affiliate Program</a>
    <a href="/careers.html" class="mobile-nav-link">Careers</a>
    <a href="/status.html" class="mobile-nav-link">System Status</a>
  </div>
  <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="mobile-nav-cta">Book a Call &rarr;</a>
</nav>

<section class="hero">
  <div class="hero-glow"></div>
  <div class="hero-grid"></div>
  <div class="hero-inner">
    <div class="hero-copy">
      <div class="hero-badge">
        <span class="hero-badge-dot"></span>
        Built for HVAC, Plumbing &amp; Electrical
      </div>
      <h1 class="hero-title">
        Stop missing calls.<br>
        <span class="hero-grad">Start capturing jobs.</span>
      </h1>
      <p class="hero-sub">
        Syntharra answers every call, qualifies every lead, and escalates every emergency &mdash; 24/7. Your AI receptionist is live in under 24 hours.
      </p>
      <div class="ctas">
        <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="btn-p">Book Your Free Demo</a>
        <a href="/demo.html" class="btn-g">&#9654; Try the Live Demo</a>
      </div>
      <div class="trust-checks">
        <span class="tc">200 free minutes</span>
        <span class="tc">No credit card</span>
        <span class="tc">Live in 24h</span>
      </div>
    </div>
    <div class="hero-visual">
      <div class="phone-wrap">
        <div class="phone-outer">
          <div class="phone-screen">
            <div class="phone-bar">
              <span class="phone-time">9:41</span>
              <div class="phone-island">
                <div class="phone-island-dot"></div>
                <span class="phone-island-txt">LIVE</span>
              </div>
            </div>
            <div class="phone-caller">
              <div class="phone-av">&#128100;</div>
              <div class="phone-cn">Incoming Call</div>
              <div class="phone-cs">AI Answering Now</div>
            </div>
            <div class="phone-chat">
              <div class="cb-c">
                <div class="cav">C</div>
                <div class="ct">&ldquo;My AC stopped working and it&rsquo;s 95&deg; outside!&rdquo;</div>
              </div>
              <div class="cb-ai">
                <div class="cav-ai">AI</div>
                <div class="ct-ai">&ldquo;That&rsquo;s urgent. I can get a tech to you by 2&nbsp;PM. What&rsquo;s your address?&rdquo;</div>
              </div>
            </div>
            <div class="phone-actions">
              <button class="pbtn pbtn-end">&#10005;</button>
              <div class="pact"><span class="pact-l">Action</span><span class="pact-v">Booking Tech</span></div>
              <button class="pbtn pbtn-ok">&#10003;</button>
            </div>
          </div>
        </div>
        <div class="bcard">
          <div class="bcard-hd">
            <span>&#128197;</span> Job Booked
            <span class="bcard-time">Just now</span>
          </div>
          <div class="bcard-body">
            <div class="bcard-row">
              <div><div class="bcard-lbl">Customer</div><div class="bcard-name">Mike Thornton</div></div>
              <div class="bcard-badge">+$380 est.</div>
            </div>
            <div class="bcard-addr">&#128205; 847 Maple Ave, Riverside</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="trust-bar">
  <div class="trust-bar-inner">
    <span class="trust-bar-lbl">Trusted by contractors nationwide</span>
    <div class="trust-logos">
      <span>ApexHVAC</span>
      <span>ClearFlow</span>
      <span>BoltElec.</span>
      <span>ClimaTeam</span>
      <span>HydroMasters</span>
    </div>
  </div>
</section>

<section class="features" id="solutions">
  <div class="feat-inner">
    <div class="sec-header">
      <span class="sec-eyebrow">Why Syntharra</span>
      <h2 class="sec-title">Built for trade businesses.<br>Priced for growth.</h2>
      <p class="sec-sub">Every missed call is $300&ndash;$2,000 walking to your competitor. Syntharra ends that permanently.</p>
    </div>
    <div class="bento">
      <div class="bc bc-8 bc-lt" style="position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;right:0;padding:24px;opacity:.04;font-size:8rem;pointer-events:none;line-height:1;">&#128222;</div>
        <div class="bi">&#128222;</div>
        <h3 class="bh">Answers in under 3 seconds. Every time.</h3>
        <p class="bt">No hold music. No voicemail. No lost leads. Syntharra picks up the moment your customer calls &mdash; day, night, weekend, holiday.</p>
        <div class="stats">
          <div class="stt"><div class="stn">24/7</div><div class="stl">Always On</div></div>
          <div class="stt"><div class="stn">200</div><div class="stl">Free Pilot Minutes</div></div>
          <div class="stt"><div class="stn">&lt;3s</div><div class="stl">Response Time</div></div>
          <div class="stt"><div class="stn">24h</div><div class="stl">Live Onboarding</div></div>
        </div>
      </div>
      <div class="bc bc-4 bc-dk">
        <div class="bc-dk-in">
          <div style="font-size:1.5rem;margin-bottom:12px;">&#9889;</div>
          <div class="bn-dk">$80k<span class="bn-dk-s">/yr</span></div>
          <div class="bh-dk" style="margin-top:10px;">Avg. Revenue Lost</div>
          <p class="bt-dk">From missed calls alone &mdash; before counting jobs your competitor picks up.</p>
        </div>
      </div>
      <div class="bc bc-6 bc-lt">
        <div class="bi">&#127919;</div>
        <h3 class="bh">Smart Lead Capture</h3>
        <p class="bt">Captures name, address, issue, urgency, and preferred time &mdash; then routes it directly to your team via text and email.</p>
      </div>
      <div class="bc bc-6 bc-lt">
        <div class="bi">&#128680;</div>
        <h3 class="bh">Emergency Escalation</h3>
        <p class="bt">Gas leaks, flooded basements, no heat in winter &mdash; identified instantly and your on-call tech gets a text in seconds.</p>
      </div>
    </div>
  </div>
</section>

<section class="dark-cta" id="pricing">
  <div class="dcta-orb1"></div>
  <div class="dcta-orb2"></div>
  <div class="dcta-inner">
    <h2 class="dcta-title">
      Your AI receptionist<br>goes live <span class="dcta-grad">tonight.</span>
    </h2>
    <p class="dcta-sub">200 free minutes. No credit card. Setup in under 24 hours.</p>
    <div class="dcta-btns">
      <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="btn-p">Book a Free Demo</a>
      <a href="/demo.html" class="btn-g">Try the Live Demo &rarr;</a>
    </div>
  </div>
</section>

<footer>
  <div class="foot-inner">
    <div class="foot-grid">
      <div class="foot-brand">
        <a href="/" aria-label="Syntharra — Global AI Solutions" class="logo-section">
{LOGO}
        </a>
        <p class="foot-brand-txt">The AI receptionist built for HVAC, plumbing, and electrical contractors across the US.</p>
        <p class="foot-tag">Global AI Solutions</p>
      </div>
      <div class="fcol">
        <div class="fcol-title">Product</div>
        <ul>
          <li><a href="/how-it-works.html">How It Works</a></li>
          <li><a href="/demo.html">Demo</a></li>
          <li><a href="/calculator.html">Revenue Calculator</a></li>
          <li><a href="/ai-readiness.html">AI Readiness Score</a></li>
          <li><a href="/faq.html">FAQ</a></li>
        </ul>
      </div>
      <div class="fcol">
        <div class="fcol-title">Industries</div>
        <ul>
          <li><a href="/hvac.html">HVAC</a></li>
          <li><a href="/plumbing.html">Plumbing</a></li>
          <li><a href="/electrical.html">Electrical</a></li>
          <li><a href="/vs-answering-service.html">Why AI Wins</a></li>
          <li><a href="/case-studies.html">Case Studies</a></li>
        </ul>
      </div>
      <div class="fcol">
        <div class="fcol-title">Company</div>
        <ul>
          <li><a href="/about.html">About</a></li>
          <li><a href="/blog.html">Blog</a></li>
          <li><a href="/affiliate.html">Affiliate Program</a></li>
          <li><a href="/careers.html">Careers</a></li>
          <li><a href="/status.html">System Status</a></li>
        </ul>
      </div>
      <div class="fcol">
        <div class="fcol-title">Legal</div>
        <ul>
          <li><a href="/privacy.html">Privacy Policy</a></li>
          <li><a href="/terms.html">Terms of Service</a></li>
          <li><a href="/security.html">Security</a></li>
          <li><a href="mailto:support@syntharra.com">support@syntharra.com</a></li>
          <li><a href="mailto:feedback@syntharra.com">feedback@syntharra.com</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span>&copy; 2026 Syntharra Global AI Solutions. All rights reserved.</span>
      <span class="sdot">All systems operational</span>
    </div>
  </div>
</footer>

<script>
var hamburger = document.getElementById('hamburger');
var mobileNav = document.getElementById('mobileNav');
if (hamburger && mobileNav) {{
    hamburger.addEventListener('click', function(e) {{ e.stopPropagation(); mobileNav.classList.toggle('open'); }});
    document.addEventListener('click', function(e) {{
        if (!mobileNav.contains(e.target) && !hamburger.contains(e.target)) mobileNav.classList.remove('open');
    }});
}}
</script>
</body>
</html>'''

def push_file(filename, content, message):
    r = requests.get(f'{API}/{filename}', headers=HEADERS)
    if r.status_code != 200:
        print(f'Cannot fetch {filename}: {r.status_code}')
        return False
    sha = r.json()['sha']
    assert content.count('<style>') == 1, f'Multiple <style> blocks! Count: {content.count("<style>")}'
    b64 = base64.b64encode(content.encode('utf-8')).decode()
    resp = requests.put(f'{API}/{filename}', headers=HEADERS, json={'message': message, 'content': b64, 'sha': sha})
    if resp.status_code in (200, 201):
        print(f'OK  {filename}')
        return True
    else:
        print(f'ERR {filename}: {resp.status_code} {resp.text[:300]}')
        return False

if __name__ == '__main__':
    ok = push_file('index.html', HTML, 'feat(design): Concept A homepage — dark prestige redesign with glass nav, bento features, corrected bare SVG logo')
    sys.exit(0 if ok else 1)
