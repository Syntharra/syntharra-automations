#!/usr/bin/env python3
"""Push new Syntharra homepage (new design system) to syntharra-website."""
import requests, base64, sys, json

TOKEN = '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'
REPO  = 'Syntharra/syntharra-website'
API   = f'https://api.github.com/repos/{REPO}/contents'
HDRS  = {'Authorization': f'token {TOKEN}', 'Content-Type': 'application/json'}

HTML = '''<!DOCTYPE html>
<html class="scroll-smooth" lang="en">
<head>
<meta charset="UTF-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<link rel="icon" type="image/svg+xml" href="/favicon.svg"/>
<link rel="apple-touch-icon" href="/favicon.svg"/>
<meta name="theme-color" content="#4d41df"/>
<title>Syntharra | AI Receptionist for HVAC &amp; Trade Businesses</title>
<meta name="description" content="Syntharra AI Receptionist answers every call 24/7 for HVAC contractors. Capture leads, never miss revenue. $697/mo."/>
<meta name="keywords" content="AI receptionist, HVAC answering service, 24/7 call answering, AI receptionist for contractors, plumbing answering service, electrical answering service, trade business AI"/>
<link rel="canonical" href="https://www.syntharra.com/"/>
<meta property="og:type" content="website"/>
<meta property="og:url" content="https://www.syntharra.com/"/>
<meta property="og:title" content="Syntharra | AI Receptionist for Trade Businesses"/>
<meta property="og:description" content="Stop missing calls. Stop losing $80,000 a year. AI receptionist built for HVAC contractors."/>
<meta property="og:image" content="https://www.syntharra.com/og-image.png"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta property="twitter:card" content="summary_large_image"/>
<meta property="twitter:url" content="https://www.syntharra.com/"/>
<meta property="twitter:title" content="Syntharra | AI Receptionist for Trade Businesses"/>
<meta property="twitter:description" content="Stop missing calls. Stop losing $80,000 a year. AI receptionist built for HVAC contractors."/>
<meta property="twitter:image" content="https://www.syntharra.com/og-image.png"/>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,700;12..96,800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600&family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script id="tailwind-config">
tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: "#4d41df",
        "primary-container": "#675df9",
        "primary-fixed": "#e3dfff",
        "primary-fixed-dim": "#c4c0ff",
        "on-primary": "#ffffff",
        "on-primary-fixed": "#100069",
        "on-primary-fixed-variant": "#3622ca",
        secondary: "#00677e",
        "secondary-container": "#00d2fd",
        "secondary-fixed": "#b4ebff",
        "secondary-fixed-dim": "#3cd7ff",
        "on-secondary": "#ffffff",
        "on-secondary-container": "#005669",
        "on-secondary-fixed": "#001f27",
        "on-secondary-fixed-variant": "#004e5f",
        tertiary: "#914800",
        "tertiary-container": "#b65c00",
        "tertiary-fixed": "#ffdcc6",
        "tertiary-fixed-dim": "#ffb785",
        "on-tertiary": "#ffffff",
        "on-tertiary-container": "#fffbff",
        "on-tertiary-fixed": "#301400",
        "on-tertiary-fixed-variant": "#713700",
        surface: "#fcf8ff",
        "surface-bright": "#fcf8ff",
        "surface-dim": "#dad7f3",
        "surface-variant": "#e2e0fc",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f5f2ff",
        "surface-container": "#efecff",
        "surface-container-high": "#e8e5ff",
        "surface-container-highest": "#e2e0fc",
        "surface-tint": "#4f44e2",
        "on-surface": "#1a1a2e",
        "on-surface-variant": "#464555",
        background: "#fcf8ff",
        "on-background": "#1a1a2e",
        outline: "#777587",
        "outline-variant": "#c7c4d8",
        "inverse-surface": "#2f2e43",
        "inverse-on-surface": "#f2efff",
        "inverse-primary": "#c4c0ff",
        error: "#ba1a1a",
        "error-container": "#ffdad6",
        "on-error": "#ffffff",
        "on-error-container": "#93000a"
      },
      borderRadius: {
        DEFAULT: "1.5rem",
        lg: "2.5rem",
        xl: "4rem",
        full: "9999px"
      },
      fontFamily: {
        headline: ["Bricolage Grotesque", "sans-serif"],
        body: ["DM Sans", "sans-serif"],
        label: ["DM Sans", "sans-serif"]
      }
    }
  }
}
</script>
<style type="text/tailwindcss">
@keyframes floating {
  0% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(2deg); }
  100% { transform: translateY(0px) rotate(0deg); }
}
.animate-floating { animation: floating 6s ease-in-out infinite; }
.text-violet-gradient {
  background: linear-gradient(135deg, #4d41df, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.organic-shape { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
.bento-shadow { box-shadow: 0 40px 100px -20px rgba(26,26,46,0.08); }
.diagonal-reveal { clip-path: polygon(0 0, 100% 0, 100% 100%, 0 95%); }
.diagonal-reveal-reverse { clip-path: polygon(0 5%, 100% 0, 100% 100%, 0 100%); }
html, body { overflow-x: clip; }
</style>
</head>
<body class="bg-white text-on-surface font-body selection:bg-primary-container selection:text-white antialiased">

<!-- FLOATING NAV -->
<nav class="fixed top-6 left-1/2 -translate-x-1/2 w-[96%] max-w-[1900px] z-50 bg-white/70 backdrop-blur-2xl rounded-full border border-white/20 shadow-[0_8px_32px_rgba(0,0,0,0.05)] transition-all duration-500">
  <div class="flex justify-between items-center px-8 py-3">
    <!-- Logo -->
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
    <!-- Desktop links -->
    <div class="hidden md:flex items-center space-x-8">
      <a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/how-it-works.html">How It Works</a>
      <a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/demo.html">Demo</a>
      <a class="text-slate-600 hover:text-primary font-medium text-sm tracking-tight transition-all" href="/case-studies.html">Results</a>
    </div>
    <!-- CTA + Menu button (always visible) -->
    <div class="flex items-center gap-2">
      <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="bg-primary text-white px-6 py-2 rounded-full font-bold text-sm hover:scale-105 active:scale-95 transition-all font-headline shadow-lg shadow-primary/20">
        Get Started &rarr;
      </a>
      <button id="hbg" aria-label="Open menu" class="flex items-center gap-1.5 text-slate-600 hover:text-primary px-3 py-2 rounded-full border border-slate-200 hover:border-primary/30 hover:bg-primary/5 transition-all cursor-pointer">
        <span class="material-symbols-outlined" style="font-size:18px;line-height:1">menu</span>
        <span class="hidden md:inline text-sm font-semibold">Menu</span>
      </button>
    </div>
  </div>
</nav>

<!-- MOBILE MENU -->
<div id="bd" class="fixed inset-0 bg-black/60 z-[1000] opacity-0 pointer-events-none transition-opacity duration-250 backdrop-blur-sm"></div>
<div id="mp" class="fixed top-0 right-0 bottom-0 w-[300px] bg-white border-l border-slate-100 z-[1001] translate-x-full transition-transform duration-[380ms] ease-[cubic-bezier(0.16,1,0.3,1)] p-7 flex flex-col overflow-y-auto">
  <button id="mx" class="self-end text-slate-400 hover:text-slate-900 text-xl mb-6 transition-colors">&times;</button>
  <div class="mb-6">
    <div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Product</div>
    <div class="flex flex-col gap-2">
      <a href="/how-it-works.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">How It Works</a>
      <a href="/demo.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Live Demo</a>
      <a href="/faq.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">FAQ</a>
      <a href="/ai-readiness.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">AI Readiness Score</a>
      <a href="/calculator.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Revenue Calculator</a>
    </div>
  </div>
  <div class="mb-6">
    <div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Learn</div>
    <div class="flex flex-col gap-2">
      <a href="/case-studies.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Case Studies</a>
      <a href="/blog.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Blog</a>
    </div>
  </div>
  <div class="mb-6">
    <div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Industries</div>
    <div class="flex flex-col gap-2">
      <a href="/hvac.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">HVAC</a>
      <a href="/plumbing.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Plumbing</a>
      <a href="/electrical.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Electrical</a>
    </div>
  </div>
  <div class="mb-6">
    <div class="text-[10px] font-black tracking-widest uppercase text-primary mb-3">Company</div>
    <div class="flex flex-col gap-2">
      <a href="/about.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">About</a>
      <a href="/affiliate.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Affiliate Program</a>
      <a href="/careers.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">Careers</a>
      <a href="/status.html" class="text-slate-700 hover:text-primary font-medium text-sm transition-colors py-1">System Status</a>
    </div>
  </div>
  <a href="/demo.html" class="mt-auto bg-primary text-white text-center py-4 rounded-2xl font-black text-sm hover:opacity-90 transition-opacity">Book a Free Demo &rarr;</a>
</div>

<main class="pt-32">

  <!-- HERO -->
  <section class="max-w-[1700px] mx-auto px-8 relative mb-40">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

      <!-- Left: copy -->
      <div class="lg:col-span-8 space-y-12">
        <div class="relative">
          <span class="inline-flex items-center px-4 py-1.5 rounded-full bg-primary/5 text-primary text-[10px] font-black tracking-[2px] uppercase ring-1 ring-primary/20 mb-8">
            Built for HVAC Contractors
          </span>
          <h1 class="text-[72px] md:text-[120px] leading-[0.85] font-headline font-black tracking-[-6px] text-on-surface">
            Stop missing calls.<br/>
            <span class="text-violet-gradient">Recapture $80k.</span>
          </h1>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
          <p class="text-xl md:text-2xl text-on-surface-variant font-medium leading-tight max-w-md">
            Every missed call is $300&ndash;$2,000 handed to your competitor. Syntharra handles the triage while you handle the tools.
          </p>
          <div class="flex flex-col gap-4">
            <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="bg-primary text-on-primary px-8 py-6 rounded-[2rem] font-black text-xl hover:-translate-y-1 transition-all shadow-2xl shadow-primary/30 flex items-center justify-center gap-3 group font-headline">
              Book Your Free Demo
              <span class="material-symbols-outlined group-hover:translate-x-1 transition-transform" style="font-size:20px">arrow_forward</span>
            </a>
            <a href="/demo.html" class="border-2 border-primary/30 text-primary px-8 py-4 rounded-[2rem] font-bold text-base hover:bg-primary/5 transition-all flex items-center justify-center gap-2">
              &#9654; Hear the AI live
            </a>
            <div class="flex items-center gap-6 text-[10px] font-black tracking-widest uppercase text-on-surface-variant/60 pt-1">
              <span>No contracts</span>
              <span>Live in 24h</span>
              <span>Cancel anytime</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: phone mockup -->
      <div class="lg:col-span-4 relative mt-20 lg:mt-0">
        <div class="animate-floating relative z-20">
          <div class="bg-slate-950 p-2 rounded-[3.5rem] shadow-2xl ring-1 ring-white/10 overflow-hidden rotate-2">
            <div class="relative bg-slate-900/40 backdrop-blur-3xl rounded-[3rem] p-8 flex flex-col min-h-[560px]">
              <!-- Status bar -->
              <div class="flex justify-between text-white/40 text-[10px] font-bold mb-6">
                <span>9:41</span>
                <span class="flex items-center gap-1">
                  <span>&#11044;&#11044;&#11044; 5G</span>
                </span>
              </div>
              <!-- Call card -->
              <div class="bg-white/10 rounded-2xl p-4 mb-6 flex items-center gap-3">
                <div class="w-9 h-9 rounded-full bg-primary flex items-center justify-center">
                  <span class="material-symbols-outlined text-white" style="font-size:18px">call</span>
                </div>
                <div>
                  <div class="text-white text-xs font-bold">Live call &bull; 00:02.8</div>
                  <div class="text-white/50 text-[10px]">Austin, TX +1 (512) 555-0188</div>
                </div>
                <div class="ml-auto w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
              </div>
              <!-- Conversation -->
              <div class="flex-1 space-y-4">
                <div class="bg-white/10 p-4 rounded-3xl rounded-tl-none border border-white/10">
                  <p class="text-white/60 text-[10px] font-bold uppercase tracking-widest mb-1">Caller</p>
                  <p class="text-white text-xs">&ldquo;My AC just stopped working and it&rsquo;s 95 degrees in the house.&rdquo;</p>
                </div>
                <div class="bg-primary/20 p-4 rounded-3xl rounded-tr-none border border-primary/30 ml-4">
                  <p class="text-primary text-[10px] font-bold uppercase tracking-widest mb-1">Syntharra</p>
                  <p class="text-white text-xs">&ldquo;I can get a tech out today. Can I grab your address and a callback number?&rdquo;</p>
                </div>
              </div>
              <!-- Lead captured -->
              <div class="mt-6 bg-emerald-500/10 p-4 rounded-2xl border border-emerald-500/20">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-emerald-400 font-bold text-xs">&#10003; Lead Captured</span>
                  <span class="text-emerald-400 text-xs">$1,450 ticket</span>
                </div>
                <div class="flex gap-4 text-[10px] text-white/50">
                  <span>Sarah M.</span>
                  <span>AC failure (urgent)</span>
                  <span>Owner notified</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- Ambient glows -->
        <div class="absolute -bottom-20 -left-20 w-64 h-64 bg-primary/20 blur-[100px] organic-shape pointer-events-none"></div>
        <div class="absolute -top-10 -right-10 w-48 h-48 bg-indigo-500/10 blur-[80px] rounded-full pointer-events-none"></div>
      </div>
    </div>
  </section>

  <!-- STATS BENTO -->
  <section class="mb-40 relative">
    <div class="max-w-[1700px] mx-auto px-8">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 items-end">
        <div class="bg-surface-container-low p-12 rounded-[3rem] h-64 flex flex-col justify-between hover:bg-primary hover:text-white transition-all duration-500 group cursor-default">
          <span class="text-[10px] font-black tracking-widest uppercase text-on-surface-variant group-hover:text-white/70 transition-colors">Answer Rate</span>
          <div class="text-7xl font-black font-headline tracking-tighter text-on-surface group-hover:text-white transition-colors">97%</div>
        </div>
        <div class="bg-surface-container-high p-12 rounded-[4rem] h-80 flex flex-col justify-between translate-y-8 hover:bg-primary hover:text-white transition-all duration-500 group cursor-default">
          <span class="text-[10px] font-black tracking-widest uppercase text-on-surface-variant group-hover:text-white/70 transition-colors">Response</span>
          <div class="text-7xl font-black font-headline tracking-tighter text-on-surface group-hover:text-white transition-colors">&lt;3s</div>
        </div>
        <div class="bg-primary p-12 rounded-[3.5rem] h-72 text-white flex flex-col justify-between -translate-y-4 hover:scale-105 transition-all duration-500 cursor-default">
          <span class="text-[10px] font-black tracking-widest uppercase text-white/70">Monthly Revenue</span>
          <div class="text-7xl font-black font-headline tracking-tighter">$10k+</div>
        </div>
        <div class="bg-surface-container-highest p-12 rounded-[3rem] h-64 flex flex-col justify-between hover:bg-primary hover:text-white transition-all duration-500 group cursor-default">
          <span class="text-[10px] font-black tracking-widest uppercase text-on-surface-variant group-hover:text-white/70 transition-colors">Go Live</span>
          <div class="text-7xl font-black font-headline tracking-tighter text-on-surface group-hover:text-white transition-colors">24h</div>
        </div>
      </div>
    </div>
  </section>

  <!-- HOW IT WORKS -->
  <section class="py-40 relative overflow-hidden">
    <div class="max-w-[1300px] mx-auto px-8 mb-24">
      <span class="inline-flex items-center px-4 py-1.5 rounded-full bg-primary/5 text-primary text-[10px] font-black tracking-[2px] uppercase ring-1 ring-primary/20 mb-6">How It Works</span>
      <h2 class="text-7xl md:text-[100px] font-headline font-black tracking-[-5px] leading-none">Live in minutes.<br/>Zero setup.</h2>
    </div>
    <div class="max-w-[1700px] mx-auto px-8 grid grid-cols-1 md:grid-cols-12 gap-12 items-center">
      <!-- Steps -->
      <div class="md:col-span-5 space-y-16">
        <div class="flex gap-8 group">
          <div class="text-4xl font-black text-primary/20 group-hover:text-primary transition-colors font-headline flex-shrink-0">01</div>
          <div>
            <h3 class="text-3xl font-headline font-black mb-4">Onboard in 5 minutes</h3>
            <p class="text-on-surface-variant leading-relaxed">Tell us your services, area, and hours. No technical knowledge needed whatsoever.</p>
          </div>
        </div>
        <div class="flex gap-8 group translate-x-8">
          <div class="text-4xl font-black text-primary/20 group-hover:text-primary transition-colors font-headline flex-shrink-0">02</div>
          <div>
            <h3 class="text-3xl font-headline font-black mb-4">We train your agent</h3>
            <p class="text-on-surface-variant leading-relaxed">Your AI learns your pricing, job types, and how to qualify and book calls.</p>
          </div>
        </div>
        <div class="flex gap-8 group">
          <div class="text-4xl font-black text-primary/20 group-hover:text-primary transition-colors font-headline flex-shrink-0">03</div>
          <div>
            <h3 class="text-3xl font-headline font-black mb-4">Forward your number</h3>
            <p class="text-on-surface-variant leading-relaxed">Point your business line to Syntharra. Works with any phone system in under 60 seconds.</p>
          </div>
        </div>
        <div class="flex gap-8 group translate-x-8">
          <div class="text-4xl font-black text-primary/20 group-hover:text-primary transition-colors font-headline flex-shrink-0">04</div>
          <div>
            <h3 class="text-3xl font-headline font-black mb-4">Revenue starts growing</h3>
            <p class="text-on-surface-variant leading-relaxed">Every call answered, every job booked. Track every dollar recovered in real time.</p>
          </div>
        </div>
      </div>
      <!-- Feature cards right -->
      <div class="md:col-span-7 grid grid-cols-1 gap-6">
        <div class="bg-surface-container-low p-10 rounded-[3rem] bento-shadow border border-slate-100 flex items-start gap-6 hover:-translate-y-1 transition-transform duration-300">
          <div class="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center flex-shrink-0">
            <span class="material-symbols-outlined text-primary" style="font-size:28px">call</span>
          </div>
          <div>
            <h4 class="text-xl font-headline font-black mb-2">Instant Pickup</h4>
            <p class="text-on-surface-variant text-sm leading-relaxed">AI answers on ring one. Zero hold times. Professional triage for every service inquiry, 24/7/365.</p>
          </div>
        </div>
        <div class="bg-surface-container-low p-10 rounded-[3rem] bento-shadow border border-slate-100 flex items-start gap-6 hover:-translate-y-1 transition-transform duration-300">
          <div class="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center flex-shrink-0">
            <span class="material-symbols-outlined text-primary" style="font-size:28px">psychology</span>
          </div>
          <div>
            <h4 class="text-xl font-headline font-black mb-2">Smart Qualification</h4>
            <p class="text-on-surface-variant text-sm leading-relaxed">Qualifies leads by job type, urgency, and zip code. Real-time data handed off to your phone instantly.</p>
          </div>
        </div>
        <div class="bg-primary p-10 rounded-[3rem] flex items-start gap-6 hover:scale-[1.02] transition-transform duration-300">
          <div class="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center flex-shrink-0">
            <span class="material-symbols-outlined text-white" style="font-size:28px">notifications_active</span>
          </div>
          <div>
            <h4 class="text-xl font-headline font-black mb-2 text-white">You&rsquo;re Notified Instantly</h4>
            <p class="text-white/70 text-sm leading-relaxed">The second a call ends, you get a text with the caller&rsquo;s name, issue, and number. No lead ever goes cold.</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- DARK FEATURES -->
  <section class="py-40 bg-slate-950 diagonal-reveal text-white relative overflow-hidden">
    <div class="max-w-[1300px] mx-auto px-8 mb-20 relative z-10">
      <span class="text-primary font-black tracking-widest uppercase text-[10px] mb-4 block">Engineered For Trades</span>
      <h2 class="text-6xl md:text-8xl font-headline font-black tracking-[-4px]">Frontline performance.</h2>
    </div>
    <div class="max-w-[1700px] mx-auto px-8 grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
      <!-- Big feature card -->
      <div class="md:col-span-1 bg-white/5 backdrop-blur-md rounded-[3rem] p-12 border border-white/10 hover:bg-white/10 transition-all overflow-hidden relative min-h-[500px]">
        <span class="material-symbols-outlined text-6xl text-primary mb-12 block" style="font-variation-settings:'FILL' 0">shield_lock</span>
        <h3 class="text-4xl font-headline font-bold mb-6">Unfailing Reliability</h3>
        <p class="text-white/50 text-xl leading-relaxed">Your business never sleeps. Neither does your digital foreman. 24/7 coverage for the hardest workers in the trades.</p>
        <div class="absolute -bottom-20 -right-20 w-80 h-80 bg-primary/20 blur-[100px] rounded-full pointer-events-none"></div>
      </div>
      <!-- Right column -->
      <div class="md:col-span-2 space-y-6">
        <!-- SMS feature -->
        <div class="bg-primary/10 backdrop-blur-md rounded-[3rem] p-12 border border-primary/20 hover:bg-primary/20 transition-all flex flex-col md:flex-row gap-12 items-center">
          <div class="flex-1">
            <span class="material-symbols-outlined text-4xl text-white mb-6 block">textsms</span>
            <h3 class="text-3xl font-headline font-bold mb-4">Instant Lead Handoff</h3>
            <p class="text-white/60">AI captures the lead, then fires a text to your phone in seconds. Name, issue, urgency &mdash; everything you need to call back.</p>
          </div>
          <div class="w-full md:w-64 aspect-video bg-slate-900 rounded-2xl ring-1 ring-white/10 p-4 shadow-2xl rotate-2 flex-shrink-0">
            <div class="text-[10px] text-white/30 font-bold mb-3">New lead from Syntharra</div>
            <div class="h-1.5 w-full bg-white/10 rounded-full mb-2"></div>
            <div class="h-1.5 w-3/4 bg-primary/40 rounded-full mb-2"></div>
            <div class="h-1.5 w-1/2 bg-white/10 rounded-full"></div>
          </div>
        </div>
        <!-- Industry cards -->
        <div class="grid grid-cols-3 gap-4">
          <a href="/hvac.html" class="bg-white/5 p-8 rounded-3xl border border-white/5 hover:border-primary transition-all text-center group">
            <span class="material-symbols-outlined text-primary mb-4 block text-4xl" style="font-variation-settings:'FILL' 0">ac_unit</span>
            <div class="font-bold font-headline text-sm uppercase tracking-widest text-white">HVAC</div>
          </a>
          <a href="/plumbing.html" class="bg-white/5 p-8 rounded-3xl border border-white/5 hover:border-secondary-fixed-dim transition-all text-center translate-y-4 group">
            <span class="material-symbols-outlined text-secondary-fixed-dim mb-4 block text-4xl" style="font-variation-settings:'FILL' 0">plumbing</span>
            <div class="font-bold font-headline text-sm uppercase tracking-widest text-white">Plumbing</div>
          </a>
          <a href="/electrical.html" class="bg-white/5 p-8 rounded-3xl border border-white/5 hover:border-amber-400 transition-all text-center group">
            <span class="material-symbols-outlined text-amber-400 mb-4 block text-4xl" style="font-variation-settings:'FILL' 0">bolt</span>
            <div class="font-bold font-headline text-sm uppercase tracking-widest text-white">Electrical</div>
          </a>
        </div>
      </div>
    </div>
    <!-- Ambient glow -->
    <div class="absolute top-0 right-0 w-full h-full pointer-events-none opacity-20">
      <div class="absolute -top-[20%] -right-[10%] w-[60%] h-[80%] organic-shape bg-primary blur-[150px]"></div>
    </div>
  </section>

  <!-- TESTIMONIALS -->
  <section class="py-40 relative">
    <div class="max-w-[1300px] mx-auto px-8 grid grid-cols-1 lg:grid-cols-2 gap-32 items-center">
      <div class="relative">
        <div class="absolute -top-40 -left-20 text-[200px] font-headline font-black text-slate-100 -z-10 select-none leading-none">REAL</div>
        <span class="inline-flex items-center px-4 py-1.5 rounded-full bg-primary/5 text-primary text-[10px] font-black tracking-[2px] uppercase ring-1 ring-primary/20 mb-8">Results</span>
        <h2 class="text-6xl md:text-8xl font-headline font-black tracking-[-4px] leading-tight">Real businesses.<br/>Real revenue.</h2>
        <p class="text-xl text-on-surface-variant mt-6 max-w-sm leading-relaxed">Contractors across the US are reclaiming hours and capturing jobs they used to lose to voicemail.</p>
      </div>
      <div class="space-y-8">
        <!-- Featured testimonial -->
        <div class="bg-white p-12 rounded-[3.5rem] bento-shadow border border-slate-50 relative rotate-1 hover:rotate-0 transition-transform duration-500">
          <div class="flex text-amber-400 mb-8">
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
          </div>
          <blockquote class="text-2xl font-medium font-headline italic mb-10">&ldquo;We were losing 8&ndash;10 calls a week after hours. Syntharra fixed that in the first 24 hours. Within a month we&rsquo;d recovered over $14,000 in jobs we would have lost entirely.&rdquo;</blockquote>
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-slate-900 rounded-full flex items-center justify-center text-white font-bold text-sm">MT</div>
            <div>
              <div class="font-bold text-sm">Mark T.</div>
              <div class="text-[10px] uppercase font-black tracking-widest text-on-surface-variant/40">Arctic Breeze HVAC &bull; Phoenix, AZ</div>
            </div>
          </div>
        </div>
        <!-- Second testimonial -->
        <div class="bg-slate-900 text-white p-12 rounded-[4rem] bento-shadow -rotate-2 hover:rotate-0 transition-transform duration-500 translate-x-8">
          <div class="flex text-amber-400 mb-6">
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
          </div>
          <blockquote class="text-2xl font-medium font-headline italic mb-10">&ldquo;My receptionist cost $3,200 a month and still missed calls. Syntharra costs less and never misses. Not even a comparison.&rdquo;</blockquote>
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-primary rounded-full flex items-center justify-center font-bold text-sm">JS</div>
            <div>
              <div class="font-bold text-sm">Jason S.</div>
              <div class="text-[10px] uppercase font-black tracking-widest text-white/40">Reliable Plumbing Co. &bull; Denver, CO</div>
            </div>
          </div>
        </div>
        <!-- Third testimonial -->
        <div class="bg-white p-10 rounded-[3rem] bento-shadow border border-slate-50 relative rotate-1 hover:rotate-0 transition-transform duration-500 -translate-x-4">
          <div class="flex text-amber-400 mb-4">
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1">star</span>
          </div>
          <blockquote class="text-lg font-medium font-headline italic mb-6">&ldquo;Customers genuinely can&rsquo;t tell it&rsquo;s AI. We booked 40+ jobs in the first month. The ROI is insane for a small electrical shop.&rdquo;</blockquote>
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-xs text-white" style="background:linear-gradient(135deg,#d97706,#f59e0b)">RC</div>
            <div>
              <div class="font-bold text-sm">Rachel C.</div>
              <div class="text-[10px] uppercase font-black tracking-widest text-on-surface-variant/40">Bright Spark Electric &bull; Austin, TX</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA BLOCK -->
  <section class="px-8 pb-40">
    <div class="max-w-[1700px] mx-auto bg-primary rounded-[5rem] p-24 md:p-40 text-center text-white relative overflow-hidden shadow-[0_80px_160px_-40px_rgba(77,65,223,0.5)]">
      <div class="relative z-10 max-w-4xl mx-auto">
        <h2 class="text-7xl md:text-[140px] leading-[0.8] font-headline font-black tracking-[-8px] mb-12">Ready to<br/>scale up?</h2>
        <p class="text-2xl md:text-3xl font-medium mb-16 text-white/80 leading-tight">Every unanswered call costs $400&ndash;$800 on average. Syntharra makes sure that never happens again.</p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-6">
          <a href="https://calendar.app.google/jxUu7XfiMXMqvdiw6" class="bg-white text-primary px-16 py-8 rounded-[2.5rem] font-black text-2xl hover:scale-105 active:scale-95 transition-all shadow-2xl font-headline">
            Book Free Demo
          </a>
          <a href="/calculator.html" class="border-2 border-white/30 text-white px-10 py-7 rounded-[2.5rem] font-black text-xl hover:bg-white/10 transition-all font-headline">
            Calculate Revenue Gap
          </a>
        </div>
        <p class="mt-8 text-[10px] font-black tracking-[4px] uppercase text-white/40">No credit card &bull; No technical setup &bull; Live in under 24 hours</p>
      </div>
      <!-- Ambient -->
      <div class="absolute top-0 right-0 w-full h-full pointer-events-none">
        <div class="absolute top-[-20%] left-[-20%] w-[80%] h-[140%] organic-shape bg-white/10 blur-[120px] rotate-12"></div>
        <div class="absolute bottom-[-20%] right-[-10%] w-[60%] h-[100%] rounded-full bg-indigo-400/20 blur-[150px]"></div>
      </div>
    </div>
  </section>

</main>

<!-- FOOTER -->
<footer class="bg-slate-950 text-white pt-40 pb-20 border-t border-white/5 relative overflow-hidden">
  <div class="max-w-[1700px] mx-auto px-8 relative z-10">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-16 mb-40">
      <!-- Brand -->
      <div class="md:col-span-4 space-y-8">
        <a href="/" class="flex items-center gap-3 w-fit">
          <div class="flex items-end gap-1">
            <div class="w-1 h-3 bg-primary rounded-full"></div>
            <div class="w-1 h-5 bg-primary rounded-full"></div>
            <div class="w-1 h-7 bg-primary rounded-full"></div>
            <div class="w-1 h-9 bg-primary rounded-full"></div>
          </div>
          <div class="flex flex-col leading-none">
            <span class="text-2xl font-black tracking-tighter text-white font-headline">Syntharra</span>
            <span class="text-[9px] font-bold tracking-[0.2em] text-primary uppercase opacity-80">Global AI Solutions</span>
          </div>
        </a>
        <p class="text-white/40 text-lg max-w-sm leading-relaxed">AI voice agents for trade businesses. Never miss a call. Never lose a job to voicemail again.</p>
        <div class="flex flex-col gap-2">
          <a href="mailto:support@syntharra.com" class="text-white/40 hover:text-white text-sm transition-colors">support@syntharra.com</a>
          <a href="mailto:feedback@syntharra.com" class="text-white/40 hover:text-white text-sm transition-colors">feedback@syntharra.com</a>
        </div>
      </div>
      <!-- Product -->
      <div class="md:col-span-2 space-y-6">
        <h4 class="text-[10px] font-black uppercase tracking-widest text-primary">Product</h4>
        <ul class="space-y-4 text-white/60 text-sm">
          <li><a class="hover:text-white transition-colors" href="/how-it-works.html">How It Works</a></li>
          <li><a class="hover:text-white transition-colors" href="/demo.html">Live Demo</a></li>
          <li><a class="hover:text-white transition-colors" href="/calculator.html">Revenue Calculator</a></li>
          <li><a class="hover:text-white transition-colors" href="/ai-readiness.html">AI Readiness Score</a></li>
          <li><a class="hover:text-white transition-colors" href="/faq.html">FAQ</a></li>
        </ul>
      </div>
      <!-- Industries & Learn -->
      <div class="md:col-span-2 space-y-6">
        <h4 class="text-[10px] font-black uppercase tracking-widest text-primary">Industries</h4>
        <ul class="space-y-4 text-white/60 text-sm">
          <li><a class="hover:text-white transition-colors" href="/hvac.html">HVAC</a></li>
          <li><a class="hover:text-white transition-colors" href="/plumbing.html">Plumbing</a></li>
          <li><a class="hover:text-white transition-colors" href="/electrical.html">Electrical</a></li>
        </ul>
        <h4 class="text-[10px] font-black uppercase tracking-widest text-primary pt-4">Learn</h4>
        <ul class="space-y-4 text-white/60 text-sm">
          <li><a class="hover:text-white transition-colors" href="/case-studies.html">Case Studies</a></li>
          <li><a class="hover:text-white transition-colors" href="/blog.html">Blog</a></li>
        </ul>
      </div>
      <!-- Company & Newsletter -->
      <div class="md:col-span-4 space-y-8">
        <div class="space-y-6">
          <h4 class="text-[10px] font-black uppercase tracking-widest text-primary">Company</h4>
          <ul class="space-y-4 text-white/60 text-sm flex flex-wrap gap-x-6">
            <li><a class="hover:text-white transition-colors" href="/about.html">About</a></li>
            <li><a class="hover:text-white transition-colors" href="/affiliate.html">Affiliates</a></li>
            <li><a class="hover:text-white transition-colors" href="/careers.html">Careers</a></li>
            <li><a class="hover:text-white transition-colors" href="/status.html">System Status</a></li>
            <li><a class="hover:text-white transition-colors" href="/privacy.html">Privacy</a></li>
            <li><a class="hover:text-white transition-colors" href="/terms.html">Terms</a></li>
          </ul>
        </div>
        <div class="bg-white/5 p-8 rounded-[2rem] border border-white/10">
          <h4 class="text-base font-bold font-headline mb-4">Stay ahead of the competition</h4>
          <p class="text-white/40 text-xs mb-4">Trade business tips, AI updates, and exclusive offers.</p>
          <div class="flex gap-2">
            <input class="bg-transparent border-b border-white/20 px-0 py-2 text-white text-sm focus:outline-none focus:border-primary w-full placeholder-white/30" placeholder="your@email.com" type="email"/>
            <button class="bg-white text-slate-950 px-5 py-2 rounded-full font-bold text-xs flex-shrink-0 hover:bg-primary hover:text-white transition-colors">Join</button>
          </div>
        </div>
      </div>
    </div>
    <!-- Bottom bar -->
    <div class="pt-10 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-6">
      <p class="text-white/20 text-xs font-medium uppercase tracking-widest">&copy; 2026 Syntharra Global AI Solutions. All rights reserved.</p>
      <p class="text-white/20 text-xs italic">Built for the trades.</p>
    </div>
  </div>
</footer>

<script>
const bd = document.getElementById('bd');
const mp = document.getElementById('mp');
const mx = document.getElementById('mx');
const hbg = document.getElementById('hbg');
function openMenu() { bd.classList.add('opacity-100','pointer-events-auto'); mp.style.transform='translateX(0)'; document.body.style.overflow='hidden'; }
function closeMenu() { bd.classList.remove('opacity-100','pointer-events-auto'); mp.style.transform=''; document.body.style.overflow=''; }
if(hbg) hbg.addEventListener('click', openMenu);
if(mx) mx.addEventListener('click', closeMenu);
if(bd) bd.addEventListener('click', closeMenu);
</script>
</body>
</html>'''

def push(filename, html, msg):
    r = requests.get(f'{API}/{filename}', headers=HDRS)
    if r.status_code == 404:
        sha = None
    else:
        sha = r.json()['sha']
    b64 = base64.b64encode(html.encode()).decode()
    payload = {'message': msg, 'content': b64}
    if sha:
        payload['sha'] = sha
    resp = requests.put(f'{API}/{filename}', headers=HDRS, data=json.dumps(payload))
    if resp.status_code in (200, 201):
        print(f'OK Pushed {filename} ({resp.status_code})')
    else:
        print(f'FAIL {filename}: {resp.status_code} {resp.text[:200]}')
        sys.exit(1)

# Validate single style block
assert HTML.count('<style') == 1, 'Multiple style blocks!'

push('index.html', HTML, 'feat(homepage): new design system — Tailwind/BricolageGrotesque/floating-nav')
print('Done. Deploy lag ~90s then check https://syntharra.com')
