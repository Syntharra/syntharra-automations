#!/usr/bin/env python3
"""Push premium clean homepage to syntharra.com"""
import requests, base64, json, sys

TOKEN = "GITHUB_TOKEN_REDACTED"
REPO = "Syntharra/syntharra-website"
FILE = "index.html"
API = f"https://api.github.com/repos/{REPO}/contents/{FILE}"
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Syntharra — AI Voice Agents for Trade Businesses</title>
<meta name="description" content="Never miss a service call again. Syntharra deploys AI voice agents that answer every call, book jobs, and grow your trade business — 24/7, automatically.">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
body{font-family:'Plus Jakarta Sans',sans-serif;background:#08080f;color:#ffffff;overflow-x:clip}

:root{
  --purple:#6C63FF;
  --ink:#08080f;
  --white:#ffffff;
  --muted:rgba(255,255,255,0.45);
  --subtle:rgba(255,255,255,0.08);
  --border:rgba(255,255,255,0.07);
  --card:rgba(255,255,255,0.03);
}

/* SCROLL REVEAL */
.sr{opacity:0;transform:translateY(28px);transition:opacity .9s cubic-bezier(.16,1,.3,1),transform .9s cubic-bezier(.16,1,.3,1)}
.sr.in{opacity:1;transform:none}
.sr-l{opacity:0;transform:translateX(-28px);transition:opacity .9s cubic-bezier(.16,1,.3,1),transform .9s cubic-bezier(.16,1,.3,1)}
.sr-l.in{opacity:1;transform:none}
.sr-r{opacity:0;transform:translateX(28px);transition:opacity .9s cubic-bezier(.16,1,.3,1),transform .9s cubic-bezier(.16,1,.3,1)}
.sr-r.in{opacity:1;transform:none}
.d1{transition-delay:.08s}.d2{transition-delay:.16s}.d3{transition-delay:.24s}
.d4{transition-delay:.32s}.d5{transition-delay:.40s}

/* NAV */
nav{
  position:fixed;top:0;left:0;right:0;z-index:900;
  height:64px;padding:0 40px;
  display:flex;align-items:center;justify-content:space-between;
  transition:background .3s,border-color .3s;
  border-bottom:1px solid transparent;
}
nav.scrolled{
  background:rgba(8,8,15,0.85);
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border-bottom-color:var(--border);
}
.logo{display:flex;align-items:center;gap:10px;text-decoration:none}
.logo-mark svg{display:block}
.logo-text{line-height:1}
.logo-name{font-size:15px;font-weight:700;letter-spacing:-.2px;color:#fff}
.logo-sub{font-size:7px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--purple);margin-top:3px;display:block}
.nav-links{display:flex;align-items:center;gap:36px;list-style:none}
.nav-links a{font-size:14px;font-weight:500;color:var(--muted);text-decoration:none;transition:color .2s}
.nav-links a:hover{color:#fff}
.nav-right{display:flex;align-items:center;gap:12px}
.btn-nav{
  font-size:13px;font-weight:600;letter-spacing:-.1px;
  background:var(--purple);color:#fff;
  padding:9px 20px;border-radius:8px;text-decoration:none;
  transition:opacity .2s,transform .2s;
}
.btn-nav:hover{opacity:.88;transform:translateY(-1px)}
.hamburger{
  display:flex;flex-direction:column;gap:5px;
  background:none;border:none;cursor:pointer;padding:8px;
}
.hamburger span{display:block;width:20px;height:1.5px;background:var(--muted);border-radius:2px;transition:background .2s}
.hamburger:hover span{background:#fff}

/* MENU */
.menu-bd{position:fixed;inset:0;background:rgba(8,8,15,.7);z-index:1000;opacity:0;pointer-events:none;transition:opacity .25s;backdrop-filter:blur(6px)}
.menu-bd.on{opacity:1;pointer-events:all}
.menu-panel{
  position:fixed;top:0;right:0;bottom:0;width:300px;
  background:#0f0f1c;border-left:1px solid var(--border);
  z-index:1001;transform:translateX(100%);transition:transform .35s cubic-bezier(.16,1,.3,1);
  padding:24px;display:flex;flex-direction:column;overflow-y:auto;
}
.menu-panel.on{transform:none}
.menu-x{
  align-self:flex-end;width:32px;height:32px;border-radius:6px;
  background:var(--subtle);border:none;cursor:pointer;color:var(--muted);
  font-size:16px;display:flex;align-items:center;justify-content:center;
  margin-bottom:28px;transition:background .2s,color .2s;
}
.menu-x:hover{background:rgba(255,255,255,0.12);color:#fff}
.menu-g{margin-bottom:24px}
.menu-g-title{font-size:10px;font-weight:700;letter-spacing:1.8px;text-transform:uppercase;color:rgba(255,255,255,0.25);margin-bottom:8px}
.menu-g a{
  display:block;font-size:14px;font-weight:500;color:var(--muted);
  text-decoration:none;padding:8px 0;border-bottom:1px solid var(--border);
  transition:color .2s;
}
.menu-g a:last-child{border:none}
.menu-g a:hover{color:#fff}
.menu-cta{
  margin-top:auto;display:block;text-align:center;
  background:var(--purple);color:#fff;padding:14px;border-radius:8px;
  font-weight:700;font-size:14px;text-decoration:none;
  transition:opacity .2s,transform .2s;
}
.menu-cta:hover{opacity:.88;transform:translateY(-1px)}

/* HERO */
.hero{
  min-height:100dvh;display:flex;align-items:center;
  padding:120px 40px 100px;position:relative;overflow:hidden;
}
.hero-noise{
  position:absolute;inset:0;z-index:0;
  background:
    radial-gradient(ellipse 60% 50% at 70% 30%,rgba(108,99,255,.12) 0%,transparent 70%),
    radial-gradient(ellipse 40% 60% at 20% 70%,rgba(108,99,255,.06) 0%,transparent 70%);
}
/* subtle grid lines */
.hero-grid{
  position:absolute;inset:0;z-index:0;
  background-image:
    linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);
  background-size:80px 80px;
  mask-image:radial-gradient(ellipse 80% 80% at 50% 50%,black 0%,transparent 100%);
}
.hero-inner{
  position:relative;z-index:1;
  max-width:1160px;margin:0 auto;width:100%;
  display:grid;grid-template-columns:1fr 440px;align-items:center;gap:80px;
}
.hero-tag{
  display:inline-flex;align-items:center;gap:7px;
  font-size:11px;font-weight:600;letter-spacing:1.2px;text-transform:uppercase;
  color:var(--purple);border:1px solid rgba(108,99,255,.25);
  border-radius:100px;padding:6px 14px;margin-bottom:28px;
}
.hero-tag-dot{width:5px;height:5px;border-radius:50%;background:var(--purple);animation:blink 2.4s ease infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
h1{
  font-size:clamp(44px,5vw,76px);font-weight:800;
  letter-spacing:-2.5px;line-height:1.0;
  color:#fff;margin-bottom:24px;
}
h1 em{
  font-style:normal;
  background:linear-gradient(90deg,#6C63FF,#a78bfa);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.hero-sub{
  font-size:17px;line-height:1.75;color:var(--muted);
  max-width:460px;margin-bottom:44px;font-weight:400;
}
.hero-btns{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.btn-primary{
  font-size:14px;font-weight:700;
  background:var(--purple);color:#fff;
  padding:14px 28px;border-radius:8px;text-decoration:none;letter-spacing:-.1px;
  transition:opacity .2s,transform .2s,box-shadow .2s;
}
.btn-primary:hover{opacity:.9;transform:translateY(-1px);box-shadow:0 8px 32px rgba(108,99,255,.35)}
.btn-secondary{
  font-size:14px;font-weight:600;color:var(--muted);
  padding:14px 20px;text-decoration:none;
  border:1px solid var(--border);border-radius:8px;
  transition:color .2s,border-color .2s,background .2s;
}
.btn-secondary:hover{color:#fff;border-color:rgba(255,255,255,.2);background:var(--subtle)}

/* phone */
.hero-phone-wrap{animation:float 5s ease-in-out infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
.phone{
  background:#101018;border:1px solid rgba(255,255,255,.1);
  border-radius:32px;overflow:hidden;
  box-shadow:0 40px 80px rgba(0,0,0,.6),0 0 0 1px rgba(255,255,255,.04);
  width:100%;max-width:340px;margin:0 auto;
}
.phone-bar{
  height:44px;background:#0d0d1a;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 20px;border-bottom:1px solid var(--border);
}
.phone-bar-time{font-size:12px;font-weight:600;color:#fff}
.phone-bar-pill{
  width:90px;height:22px;background:#000;
  border-radius:0 0 12px 12px;
}
.phone-body{padding:20px}
.phone-section-label{
  font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;
  color:rgba(255,255,255,.3);margin-bottom:12px;
}
.phone-heading{font-size:20px;font-weight:800;color:#fff;letter-spacing:-.5px;margin-bottom:16px}
/* live call card */
.p-live{
  background:rgba(108,99,255,.1);border:1px solid rgba(108,99,255,.2);
  border-radius:12px;padding:14px;margin-bottom:12px;
}
.p-live-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.p-live-name{font-size:13px;font-weight:600;color:#fff}
.p-live-badge{
  display:flex;align-items:center;gap:4px;
  font-size:9px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;
  color:#4ade80;background:rgba(74,222,128,.1);border-radius:100px;padding:3px 8px;
}
.p-live-badge-dot{width:4px;height:4px;border-radius:50%;background:#4ade80;animation:blink 1.2s ease infinite}
.p-live-msg{font-size:12px;color:rgba(255,255,255,.45);line-height:1.5}
/* stats */
.p-stats{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px}
.p-stat{
  background:var(--card);border:1px solid var(--border);
  border-radius:10px;padding:12px;
}
.p-stat-l{font-size:10px;color:rgba(255,255,255,.3);margin-bottom:4px}
.p-stat-v{font-size:19px;font-weight:800;color:#fff;letter-spacing:-.5px}
.p-stat-c{font-size:10px;color:#4ade80;margin-top:2px}
.p-jobs{
  display:flex;justify-content:space-between;align-items:center;
  background:var(--card);border:1px solid var(--border);
  border-radius:10px;padding:12px;
}
.p-jobs-label{font-size:10px;color:rgba(255,255,255,.3);margin-bottom:2px}
.p-jobs-val{font-size:16px;font-weight:700;color:var(--purple)}
.p-jobs-ico{
  width:32px;height:32px;border-radius:8px;
  background:rgba(108,99,255,.15);
  display:flex;align-items:center;justify-content:center;font-size:14px;
}

/* STATS BAR */
.stats-bar{
  border-top:1px solid var(--border);border-bottom:1px solid var(--border);
  padding:40px 40px;
}
.stats-inner{
  max-width:1160px;margin:0 auto;
  display:grid;grid-template-columns:repeat(5,1fr);
}
.stat-item{
  padding:0 28px;
  border-right:1px solid var(--border);
  text-align:center;
}
.stat-item:first-child{padding-left:0;text-align:left}
.stat-item:last-child{border-right:none;text-align:right;padding-right:0}
.stat-n{font-size:32px;font-weight:800;letter-spacing:-1.5px;color:#fff;line-height:1;margin-bottom:5px}
.stat-l{font-size:12px;color:rgba(255,255,255,.35);font-weight:500;line-height:1.4}

/* SECTION COMMON */
section{padding:120px 40px}
.s-inner{max-width:1160px;margin:0 auto}
.s-tag{
  display:inline-block;font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;
  color:var(--purple);margin-bottom:16px;
}
h2{
  font-size:clamp(32px,3.5vw,52px);font-weight:800;
  letter-spacing:-1.8px;line-height:1.05;color:#fff;margin-bottom:16px;
}
.s-sub{
  font-size:17px;line-height:1.75;color:var(--muted);
  max-width:500px;font-weight:400;
}

/* HOW IT WORKS */
.how{background:#08080f}
.how-grid{
  display:grid;grid-template-columns:repeat(4,1fr);gap:1px;
  background:var(--border);border:1px solid var(--border);border-radius:16px;
  overflow:hidden;margin-top:64px;
}
.how-step{
  background:#08080f;padding:36px 28px;
  transition:background .25s;
}
.how-step:hover{background:#0d0d1c}
.step-n{font-size:11px;font-weight:700;letter-spacing:1.5px;color:rgba(255,255,255,.2);margin-bottom:24px}
.step-ico{font-size:28px;margin-bottom:16px;display:block}
.step-t{font-size:16px;font-weight:700;color:#fff;margin-bottom:8px;letter-spacing:-.3px}
.step-b{font-size:13px;line-height:1.65;color:var(--muted)}

/* FEATURE SPLITS */
.splits{background:#08080f}
.split{
  display:grid;grid-template-columns:1fr 1fr;gap:80px;
  align-items:center;max-width:1160px;margin:0 auto;
  padding:80px 0;border-top:1px solid var(--border);
}
.split:first-child{border-top:none;padding-top:0}
.split.flip{direction:rtl}
.split.flip > *{direction:ltr}
.split-text .s-tag{display:block}
.split-text h2{max-width:440px}
.split-text .s-sub{max-width:400px;margin-top:16px}
.split-text .s-link{
  display:inline-flex;align-items:center;gap:8px;
  font-size:14px;font-weight:600;color:var(--purple);
  text-decoration:none;margin-top:28px;transition:gap .2s;
}
.split-text .s-link:hover{gap:12px}
.split-visual{
  background:#0d0d1c;border:1px solid var(--border);
  border-radius:16px;overflow:hidden;
  aspect-ratio:4/3;display:flex;align-items:stretch;
}
/* visual panels inside feature boxes */
.vis-pad{padding:28px;width:100%;display:flex;flex-direction:column;gap:12px}
.vis-row{
  display:flex;align-items:center;justify-content:space-between;
  background:var(--card);border:1px solid var(--border);
  border-radius:10px;padding:14px 16px;
}
.vis-row-l{font-size:13px;font-weight:500;color:#fff}
.vis-row-r{font-size:12px;font-weight:600;color:var(--muted)}
.vis-row-pill{
  font-size:10px;font-weight:700;background:rgba(74,222,128,.1);
  color:#4ade80;border-radius:100px;padding:3px 10px;
}
.vis-bar-wrap{padding:24px 28px;width:100%;display:flex;flex-direction:column;justify-content:center;gap:16px}
.vis-bar-item{}
.vis-bar-top{display:flex;justify-content:space-between;margin-bottom:6px}
.vis-bar-label{font-size:12px;font-weight:500;color:var(--muted)}
.vis-bar-val{font-size:12px;font-weight:700;color:#fff}
.vis-bar-track{height:4px;background:rgba(255,255,255,.07);border-radius:2px;overflow:hidden}
.vis-bar-fill{height:100%;border-radius:2px;background:linear-gradient(90deg,var(--purple),#a78bfa);transition:width .8s cubic-bezier(.16,1,.3,1)}

/* INDUSTRIES */
.ind{background:#0d0d1c;padding:120px 40px}
.ind .s-inner{}
.ind-grid{
  display:grid;grid-template-columns:repeat(3,1fr);gap:16px;
  margin-top:64px;
}
.ind-card{
  border:1px solid var(--border);border-radius:16px;
  padding:36px;background:#08080f;
  display:flex;flex-direction:column;
  transition:border-color .25s,transform .35s cubic-bezier(.16,1,.3,1),background .25s;
  cursor:pointer;text-decoration:none;
}
.ind-card:hover{
  border-color:rgba(108,99,255,.3);
  transform:translateY(-4px);
  background:#0d0d1c;
}
.ind-icon{font-size:32px;margin-bottom:28px;display:block}
.ind-name{font-size:20px;font-weight:800;color:#fff;letter-spacing:-.5px;margin-bottom:8px}
.ind-desc{font-size:14px;line-height:1.65;color:var(--muted);flex:1;margin-bottom:24px}
.ind-arrow{
  display:flex;align-items:center;gap:6px;
  font-size:13px;font-weight:600;color:var(--purple);
  transition:gap .2s;
}
.ind-card:hover .ind-arrow{gap:10px}

/* TESTIMONIALS */
.testimonials{background:#08080f;padding:120px 40px}
.test-grid{
  display:grid;grid-template-columns:repeat(3,1fr);gap:16px;
  margin-top:64px;
}
.test-card{
  background:#0d0d1c;border:1px solid var(--border);
  border-radius:16px;padding:32px;
  transition:border-color .25s;
}
.test-card:hover{border-color:rgba(108,99,255,.25)}
.test-stars{display:flex;gap:2px;margin-bottom:20px}
.test-star{font-size:14px;color:#f59e0b}
.test-q{
  font-size:15px;line-height:1.75;color:rgba(255,255,255,.65);
  margin-bottom:24px;font-weight:400;
}
.test-author{display:flex;align-items:center;gap:12px}
.test-av{
  width:38px;height:38px;border-radius:50%;
  background:linear-gradient(135deg,var(--purple),#a78bfa);
  display:flex;align-items:center;justify-content:center;
  font-size:13px;font-weight:800;color:#fff;flex-shrink:0;letter-spacing:-.5px;
}
.test-name{font-size:13px;font-weight:700;color:#fff;margin-bottom:2px}
.test-role{font-size:12px;color:rgba(255,255,255,.3)}

/* CTA */
.cta-wrap{
  background:#0d0d1c;padding:120px 40px;
  border-top:1px solid var(--border);
}
.cta-box{
  max-width:720px;margin:0 auto;text-align:center;
}
.cta-box h2{letter-spacing:-2px}
.cta-box .s-sub{margin:20px auto 44px;text-align:center;max-width:460px}
.cta-btns{display:flex;flex-wrap:wrap;gap:12px;justify-content:center}
.btn-outline{
  font-size:14px;font-weight:600;color:rgba(255,255,255,.6);
  padding:14px 24px;border-radius:8px;text-decoration:none;
  border:1px solid var(--border);
  transition:color .2s,border-color .2s,background .2s;
}
.btn-outline:hover{color:#fff;border-color:rgba(255,255,255,.25);background:var(--subtle)}
.cta-footnote{font-size:12px;color:rgba(255,255,255,.2);margin-top:20px}

/* FOOTER */
footer{
  background:#08080f;border-top:1px solid var(--border);
  padding:80px 40px 40px;
}
.ft-inner{max-width:1160px;margin:0 auto}
.ft-top{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:48px;margin-bottom:64px}
.ft-brand-logo{display:flex;align-items:center;gap:10px;text-decoration:none;margin-bottom:14px}
.ft-name{font-size:15px;font-weight:700;color:#fff}
.ft-sub{font-size:7px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--purple);display:block;margin-top:3px}
.ft-desc{font-size:13px;line-height:1.75;color:rgba(255,255,255,.3);max-width:240px;margin-bottom:20px}
.ft-mail a{display:block;font-size:13px;color:rgba(255,255,255,.3);text-decoration:none;margin-bottom:4px;transition:color .2s}
.ft-mail a:hover{color:rgba(255,255,255,.7)}
.ft-col-h{font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:rgba(255,255,255,.2);margin-bottom:16px}
.ft-col a{display:block;font-size:13px;color:rgba(255,255,255,.4);text-decoration:none;margin-bottom:10px;transition:color .2s}
.ft-col a:hover{color:rgba(255,255,255,.85)}
.ft-col a:last-child{margin-bottom:0}
.ft-bot{
  padding-top:32px;border-top:1px solid var(--border);
  display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;
}
.ft-copy{font-size:12px;color:rgba(255,255,255,.2)}
.ft-legal{display:flex;gap:20px}
.ft-legal a{font-size:12px;color:rgba(255,255,255,.2);text-decoration:none;transition:color .2s}
.ft-legal a:hover{color:rgba(255,255,255,.6)}

/* RESPONSIVE */
@media(max-width:1024px){
  .hero-inner{grid-template-columns:1fr;gap:0}
  .hero-phone-wrap{display:none}
  h1{letter-spacing:-1.5px}
  .how-grid{grid-template-columns:1fr 1fr}
  .split{grid-template-columns:1fr;gap:48px}
  .split.flip{direction:ltr}
  .ind-grid{grid-template-columns:1fr 1fr}
  .test-grid{grid-template-columns:1fr}
  .ft-top{grid-template-columns:1fr 1fr}
  .stats-inner{grid-template-columns:repeat(3,1fr);row-gap:24px}
  .stat-item:nth-child(3){border-right:none}
  .stat-item{text-align:center!important;padding:0 20px!important}
}
@media(max-width:768px){
  nav{padding:0 20px}
  .nav-links{display:none}
  section,.stats-bar,.ind,.testimonials,.cta-wrap,footer{padding-left:20px;padding-right:20px}
  .hero{padding:100px 20px 80px}
  .stats-inner{grid-template-columns:1fr 1fr}
  .stat-item:nth-child(3){border-right:1px solid var(--border)}
  .how-grid{grid-template-columns:1fr}
  .ind-grid{grid-template-columns:1fr}
  .ft-top{grid-template-columns:1fr}
  .ft-bot{flex-direction:column;text-align:center}
}
</style>
</head>
<body>

<!-- NAV -->
<nav id="nav">
  <a href="/" class="logo">
    <div class="logo-mark">
      <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="3" y="19" width="5" height="8" rx="2" fill="#6C63FF"/>
        <rect x="11" y="12" width="5" height="15" rx="2" fill="#6C63FF"/>
        <rect x="19" y="6" width="5" height="21" rx="2" fill="#6C63FF"/>
      </svg>
    </div>
    <div class="logo-text">
      <span class="logo-name">Syntharra</span>
      <span class="logo-sub">Global AI Solutions</span>
    </div>
  </a>
  <ul class="nav-links">
    <li><a href="/how-it-works.html">How It Works</a></li>
    <li><a href="/hvac.html">HVAC</a></li>
    <li><a href="/case-studies.html">Case Studies</a></li>
    <li><a href="/faq.html">FAQ</a></li>
  </ul>
  <div class="nav-right">
    <a href="/demo.html" class="btn-nav">Get a Demo</a>
    <button class="hamburger" id="hbg" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
  </div>
</nav>

<!-- MENU -->
<div class="menu-bd" id="bd"></div>
<div class="menu-panel" id="mp">
  <button class="menu-x" id="mx">&#x2715;</button>
  <div class="menu-g">
    <div class="menu-g-title">Product</div>
    <a href="/how-it-works.html">How It Works</a>
    <a href="/demo.html">Live Demo</a>
    <a href="/faq.html">FAQ</a>
    <a href="/ai-readiness.html">AI Readiness Score</a>
    <a href="/calculator.html">Revenue Calculator</a>
  </div>
  <div class="menu-g">
    <div class="menu-g-title">Learn</div>
    <a href="/case-studies.html">Case Studies</a>
    <a href="/blog.html">Blog</a>
  </div>
  <div class="menu-g">
    <div class="menu-g-title">Industries</div>
    <a href="/hvac.html">HVAC</a>
    <a href="/plumbing.html">Plumbing</a>
    <a href="/electrical.html">Electrical</a>
  </div>
  <div class="menu-g">
    <div class="menu-g-title">Company</div>
    <a href="/about.html">About</a>
    <a href="/affiliate.html">Affiliate Program</a>
    <a href="/careers.html">Careers</a>
    <a href="/status.html">System Status</a>
  </div>
  <a href="/demo.html" class="menu-cta">Book a Free Demo &rarr;</a>
</div>

<!-- HERO -->
<section class="hero">
  <div class="hero-noise"></div>
  <div class="hero-grid"></div>
  <div class="hero-inner">
    <div class="hero-text">
      <div class="hero-tag">
        <span class="hero-tag-dot"></span>
        AI Voice Agents &mdash; Live 24/7
      </div>
      <h1>Never miss<br>a service call.<br><em>Ever again.</em></h1>
      <p class="hero-sub">Syntharra deploys AI voice agents that answer every call, book jobs automatically, and cover after-hours &mdash; so your trade business grows without you being on the phone.</p>
      <div class="hero-btns">
        <a href="/demo.html" class="btn-primary">See It In Action &rarr;</a>
        <a href="/calculator.html" class="btn-secondary">Calculate Your Revenue Gap</a>
      </div>
    </div>
    <div class="hero-phone-wrap">
      <div class="phone">
        <div class="phone-bar">
          <span class="phone-bar-time">9:41</span>
          <div class="phone-bar-pill"></div>
          <span style="font-size:11px;color:rgba(255,255,255,.3);font-weight:600">&#9679;&#9679;&#9679;</span>
        </div>
        <div class="phone-body">
          <div class="phone-section-label">Live Dashboard</div>
          <div class="phone-heading">12 Jobs Booked</div>
          <div class="p-live">
            <div class="p-live-row">
              <span class="p-live-name">Mike T. &mdash; AC Repair</span>
              <div class="p-live-badge"><div class="p-live-badge-dot"></div> LIVE</div>
            </div>
            <div class="p-live-msg">&ldquo;Booked for Thursday 2pm. Confirmation sent.&rdquo;</div>
          </div>
          <div class="p-stats">
            <div class="p-stat">
              <div class="p-stat-l">Calls Answered</div>
              <div class="p-stat-v">47</div>
              <div class="p-stat-c">&#8593; 23% this week</div>
            </div>
            <div class="p-stat">
              <div class="p-stat-l">Revenue Added</div>
              <div class="p-stat-v">$8.4k</div>
              <div class="p-stat-c">&#8593; This month</div>
            </div>
          </div>
          <div class="p-jobs">
            <div>
              <div class="p-jobs-label">Jobs In Queue</div>
              <div class="p-jobs-val">5 pending</div>
            </div>
            <div class="p-jobs-ico">&#128197;</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- STATS BAR -->
<div class="stats-bar sr">
  <div class="stats-inner">
    <div class="stat-item sr d1">
      <div class="stat-n">97%</div>
      <div class="stat-l">Call answer rate</div>
    </div>
    <div class="stat-item sr d2">
      <div class="stat-n">24/7</div>
      <div class="stat-l">Always on, never sleeps</div>
    </div>
    <div class="stat-item sr d3">
      <div class="stat-n">&lt;3 min</div>
      <div class="stat-l">Average time to go live</div>
    </div>
    <div class="stat-item sr d4">
      <div class="stat-n">$8&ndash;12k</div>
      <div class="stat-l">Avg. monthly revenue added</div>
    </div>
    <div class="stat-item sr d5">
      <div class="stat-n">0</div>
      <div class="stat-l">Missed calls after go-live</div>
    </div>
  </div>
</div>

<!-- HOW IT WORKS -->
<section class="how">
  <div class="s-inner">
    <div class="sr">
      <div class="s-tag">How It Works</div>
      <h2>Live in minutes.<br>No setup required.</h2>
      <p class="s-sub">We handle everything. You fill out one form &mdash; we deploy a trained AI agent that sounds like your own front desk.</p>
    </div>
    <div class="how-grid">
      <div class="how-step sr d1">
        <div class="step-n">01</div>
        <span class="step-ico">&#128203;</span>
        <div class="step-t">Onboard in 5 minutes</div>
        <p class="step-b">Fill out a short form. Tell us your services, service area, and hours. That&rsquo;s it.</p>
      </div>
      <div class="how-step sr d2">
        <div class="step-n">02</div>
        <span class="step-ico">&#129302;</span>
        <div class="step-t">We train your agent</div>
        <p class="step-b">Your AI learns your business &mdash; pricing, services, how to qualify leads and book into your calendar.</p>
      </div>
      <div class="how-step sr d3">
        <div class="step-n">03</div>
        <span class="step-ico">&#128222;</span>
        <div class="step-t">Forward your number</div>
        <p class="step-b">Point your business line to Syntharra. Works with any phone system in under 60 seconds.</p>
      </div>
      <div class="how-step sr d4">
        <div class="step-n">04</div>
        <span class="step-ico">&#128202;</span>
        <div class="step-t">Watch revenue grow</div>
        <p class="step-b">Every call answered. Every job booked. Your dashboard shows revenue recovered in real time.</p>
      </div>
    </div>
  </div>
</section>

<!-- FEATURE SPLITS -->
<section class="splits">
  <div class="s-inner" style="padding-top:0">

    <!-- Split 1 -->
    <div class="split">
      <div class="split-text sr-l">
        <div class="s-tag">Natural Conversation</div>
        <h2>Books jobs,<br>not just messages.</h2>
        <p class="s-sub">Your AI doesn&rsquo;t just take a name and number. It qualifies the lead, checks availability, gives a price range, and books the job directly into your calendar. Callers never know it&rsquo;s AI.</p>
        <a href="/how-it-works.html" class="s-link">See how it works &rarr;</a>
      </div>
      <div class="split-visual sr-r">
        <div class="vis-pad">
          <div class="vis-row">
            <span class="vis-row-l">Incoming call — Sarah M.</span>
            <span class="vis-row-pill">LIVE</span>
          </div>
          <div class="vis-row">
            <span class="vis-row-l">Service: AC Not Cooling</span>
            <span class="vis-row-r">Qualified</span>
          </div>
          <div class="vis-row">
            <span class="vis-row-l">Appointment booked</span>
            <span class="vis-row-r">Thu 2pm &#10003;</span>
          </div>
          <div class="vis-row">
            <span class="vis-row-l">Confirmation sent</span>
            <span class="vis-row-r">SMS + Email &#10003;</span>
          </div>
          <div class="vis-row">
            <span class="vis-row-l">Job value est.</span>
            <span class="vis-row-r" style="color:#fff;font-weight:700">$380&ndash;$520</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Split 2 -->
    <div class="split flip">
      <div class="split-text sr-r">
        <div class="s-tag">After-Hours Coverage</div>
        <h2>The calls you&rsquo;re missing<br>right now.</h2>
        <p class="s-sub">Most missed calls happen outside business hours. Your Syntharra agent handles every one of them &mdash; nights, weekends, holidays &mdash; without overtime pay or voicemail.</p>
        <a href="/calculator.html" class="s-link">Calculate your revenue gap &rarr;</a>
      </div>
      <div class="split-visual sr-l">
        <div class="vis-bar-wrap">
          <div class="vis-bar-item">
            <div class="vis-bar-top">
              <span class="vis-bar-label">Business hours calls answered</span>
              <span class="vis-bar-val">100%</span>
            </div>
            <div class="vis-bar-track"><div class="vis-bar-fill" data-w="100" style="width:0%"></div></div>
          </div>
          <div class="vis-bar-item">
            <div class="vis-bar-top">
              <span class="vis-bar-label">After-hours calls answered</span>
              <span class="vis-bar-val">100%</span>
            </div>
            <div class="vis-bar-track"><div class="vis-bar-fill" data-w="100" style="width:0%"></div></div>
          </div>
          <div class="vis-bar-item">
            <div class="vis-bar-top">
              <span class="vis-bar-label">Calls converted to bookings</span>
              <span class="vis-bar-val">74%</span>
            </div>
            <div class="vis-bar-track"><div class="vis-bar-fill" data-w="74" style="width:0%"></div></div>
          </div>
          <div class="vis-bar-item">
            <div class="vis-bar-top">
              <span class="vis-bar-label">Customer satisfaction score</span>
              <span class="vis-bar-val">4.9/5</span>
            </div>
            <div class="vis-bar-track"><div class="vis-bar-fill" data-w="98" style="width:0%"></div></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Split 3 -->
    <div class="split">
      <div class="split-text sr-l">
        <div class="s-tag">Real-Time Dashboard</div>
        <h2>Every call. Every dollar.<br>One screen.</h2>
        <p class="s-sub">See every call, booking, and dollar recovered in a clean dashboard built for trade business owners &mdash; not IT teams. No spreadsheets, no guessing.</p>
        <a href="/demo.html" class="s-link">See the dashboard &rarr;</a>
      </div>
      <div class="split-visual sr-r">
        <div class="vis-pad">
          <div class="vis-row">
            <span class="vis-row-l">Today&rsquo;s calls handled</span>
            <span class="vis-row-r" style="color:#fff;font-weight:700">47</span>
          </div>
          <div class="vis-row">
            <span class="vis-row-l">Jobs booked today</span>
            <span class="vis-row-r" style="color:#fff;font-weight:700">12</span>
          </div>
          <div class="vis-row">
            <span class="vis-row-l">Revenue added (month)</span>
            <span class="vis-row-r" style="color:#4ade80;font-weight:700">$8,420</span>
          </div>
          <div class="vis-row">
            <span class="vis-row-l">Missed calls</span>
            <span class="vis-row-r" style="color:#4ade80;font-weight:700">0</span>
          </div>
          <div class="vis-row">
            <span class="vis-row-l">Agent uptime</span>
            <span class="vis-row-pill">100%</span>
          </div>
        </div>
      </div>
    </div>

  </div>
</section>

<!-- INDUSTRIES -->
<section class="ind">
  <div class="s-inner">
    <div class="sr">
      <div class="s-tag">Industries</div>
      <h2>Built for the trades.</h2>
      <p class="s-sub">Not a generic call centre. Syntharra agents are trained on HVAC, plumbing, and electrical &mdash; the terminology, job types, and pricing conversations specific to your trade.</p>
    </div>
    <div class="ind-grid">
      <a href="/hvac.html" class="ind-card sr d1">
        <span class="ind-icon">&#10052;&#65039;</span>
        <div class="ind-name">HVAC</div>
        <p class="ind-desc">AC repair, furnace service, duct cleaning, tune-ups &mdash; your agent knows every job type and books them effortlessly.</p>
        <div class="ind-arrow">Explore HVAC <span>&#8594;</span></div>
      </a>
      <a href="/plumbing.html" class="ind-card sr d2">
        <span class="ind-icon">&#128166;</span>
        <div class="ind-name">Plumbing</div>
        <p class="ind-desc">From emergency leaks to routine maintenance &mdash; capture every call before your competitor picks it up.</p>
        <div class="ind-arrow">Explore Plumbing <span>&#8594;</span></div>
      </a>
      <a href="/electrical.html" class="ind-card sr d3">
        <span class="ind-icon">&#9889;</span>
        <div class="ind-name">Electrical</div>
        <p class="ind-desc">Panel upgrades, EV charger installs, service calls &mdash; your AI qualifies and books every lead automatically.</p>
        <div class="ind-arrow">Explore Electrical <span>&#8594;</span></div>
      </a>
    </div>
  </div>
</section>

<!-- TESTIMONIALS -->
<section class="testimonials">
  <div class="s-inner">
    <div class="sr">
      <div class="s-tag">Results</div>
      <h2>Real businesses.<br>Real revenue.</h2>
      <p class="s-sub">Trade business owners who switched to Syntharra don&rsquo;t go back.</p>
    </div>
    <div class="test-grid">
      <div class="test-card sr d1">
        <div class="test-stars">
          <span class="test-star">&#9733;</span><span class="test-star">&#9733;</span>
          <span class="test-star">&#9733;</span><span class="test-star">&#9733;</span>
          <span class="test-star">&#9733;</span>
        </div>
        <p class="test-q">&ldquo;We were losing 8&ndash;10 calls a week after hours. Syntharra fixed that in the first 24 hours. Within a month we&rsquo;d recovered over $14k in jobs we would have missed.&rdquo;</p>
        <div class="test-author">
          <div class="test-av">MT</div>
          <div>
            <div class="test-name">Mark T.</div>
            <div class="test-role">Owner, Arctic Breeze HVAC &bull; Phoenix, AZ</div>
          </div>
        </div>
      </div>
      <div class="test-card sr d2">
        <div class="test-stars">
          <span class="test-star">&#9733;</span><span class="test-star">&#9733;</span>
          <span class="test-star">&#9733;</span><span class="test-star">&#9733;</span>
          <span class="test-star">&#9733;</span>
        </div>
        <p class="test-q">&ldquo;My receptionist cost $3,200 a month and still missed calls on busy days. Syntharra costs less and never misses. It&rsquo;s not even a comparison.&rdquo;</p>
        <div class="test-author">
          <div class="test-av">JS</div>
          <div>
            <div class="test-name">Jason S.</div>
            <div class="test-role">Owner, Reliable Plumbing Co. &bull; Denver, CO</div>
          </div>
        </div>
      </div>
      <div class="test-card sr d3">
        <div class="test-stars">
          <span class="test-star">&#9733;</span><span class="test-star">&#9733;</span>
          <span class="test-star">&#9733;</span><span class="test-star">&#9733;</span>
          <span class="test-star">&#9733;</span>
        </div>
        <p class="test-q">&ldquo;I was skeptical about AI on the phone, but customers genuinely can&rsquo;t tell. We booked 40+ jobs in the first month. The ROI is insane for a small shop like mine.&rdquo;</p>
        <div class="test-author">
          <div class="test-av">RC</div>
          <div>
            <div class="test-name">Rachel C.</div>
            <div class="test-role">Owner, Bright Spark Electric &bull; Austin, TX</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- CTA -->
<div class="cta-wrap">
  <div class="cta-box sr">
    <div class="s-tag" style="display:block;text-align:center">Get Started</div>
    <h2>Every missed call is<br>revenue left behind.</h2>
    <p class="s-sub">Every unanswered call costs your business $400&ndash;$800 on average. Syntharra makes sure that never happens again.</p>
    <div class="cta-btns">
      <a href="/demo.html" class="btn-primary">Get Your Free Demo</a>
      <a href="/calculator.html" class="btn-outline">Calculate Your Revenue Gap</a>
    </div>
    <p class="cta-footnote">No contract &bull; No technical setup &bull; Live in under 3 minutes</p>
  </div>
</div>

<!-- FOOTER -->
<footer>
  <div class="ft-inner">
    <div class="ft-top">
      <div>
        <a href="/" class="ft-brand-logo">
          <svg width="26" height="26" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="19" width="5" height="8" rx="2" fill="#6C63FF"/>
            <rect x="11" y="12" width="5" height="15" rx="2" fill="#6C63FF"/>
            <rect x="19" y="6" width="5" height="21" rx="2" fill="#6C63FF"/>
          </svg>
          <div>
            <span class="ft-name">Syntharra</span>
            <span class="ft-sub">Global AI Solutions</span>
          </div>
        </a>
        <p class="ft-desc">AI voice agents for trade businesses. Never miss a call. Never lose a job to voicemail again.</p>
        <div class="ft-mail">
          <a href="mailto:support@syntharra.com">support@syntharra.com</a>
          <a href="mailto:feedback@syntharra.com">feedback@syntharra.com</a>
        </div>
      </div>
      <div>
        <div class="ft-col-h">Product</div>
        <div class="ft-col">
          <a href="/how-it-works.html">How It Works</a>
          <a href="/demo.html">Live Demo</a>
          <a href="/calculator.html">Revenue Calculator</a>
          <a href="/ai-readiness.html">AI Readiness Score</a>
          <a href="/faq.html">FAQ</a>
        </div>
      </div>
      <div>
        <div class="ft-col-h">Industries</div>
        <div class="ft-col">
          <a href="/hvac.html">HVAC</a>
          <a href="/plumbing.html">Plumbing</a>
          <a href="/electrical.html">Electrical</a>
        </div>
        <div class="ft-col-h" style="margin-top:24px">Learn</div>
        <div class="ft-col">
          <a href="/case-studies.html">Case Studies</a>
          <a href="/blog.html">Blog</a>
        </div>
      </div>
      <div>
        <div class="ft-col-h">Company</div>
        <div class="ft-col">
          <a href="/about.html">About</a>
          <a href="/affiliate.html">Affiliates</a>
          <a href="/careers.html">Careers</a>
          <a href="/status.html">System Status</a>
        </div>
        <div class="ft-col-h" style="margin-top:24px">Legal</div>
        <div class="ft-col">
          <a href="/privacy.html">Privacy Policy</a>
          <a href="/terms.html">Terms of Service</a>
          <a href="/security.html">Security</a>
        </div>
      </div>
    </div>
    <div class="ft-bot">
      <div class="ft-copy">&copy; 2026 Syntharra Global AI Solutions. All rights reserved.</div>
      <div class="ft-legal">
        <a href="/privacy.html">Privacy</a>
        <a href="/terms.html">Terms</a>
        <a href="/security.html">Security</a>
      </div>
    </div>
  </div>
</footer>

<script>
// Nav scroll
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 30);
}, {passive: true});

// Menu
const hbg = document.getElementById('hbg');
const mx = document.getElementById('mx');
const bd = document.getElementById('bd');
const mp = document.getElementById('mp');
const open = () => { mp.classList.add('on'); bd.classList.add('on'); document.body.style.overflow = 'hidden'; };
const close = () => { mp.classList.remove('on'); bd.classList.remove('on'); document.body.style.overflow = ''; };
hbg.addEventListener('click', open);
mx.addEventListener('click', close);
bd.addEventListener('click', close);

// Scroll reveal
const els = document.querySelectorAll('.sr,.sr-l,.sr-r');
const obs = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in'); });
}, { threshold: 0.08, rootMargin: '0px 0px -32px 0px' });
els.forEach(el => obs.observe(el));

// Animate bars when visible
const bars = document.querySelectorAll('.vis-bar-fill');
const barObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const w = e.target.getAttribute('data-w');
      e.target.style.width = w + '%';
      barObs.unobserve(e.target);
    }
  });
}, { threshold: 0.3 });
bars.forEach(b => barObs.observe(b));
</script>

</body>
</html>'''

# Fetch current SHA
print("Fetching SHA...")
r = requests.get(API, headers=HEADERS)
r.raise_for_status()
data = r.json()
sha = data["sha"]
print(f"SHA: {sha}")

# Verify single style block
assert HTML.count("<style>") == 1, f"Multiple <style> blocks: {HTML.count('<style>')}"
print("Style check: OK")

# Push
encoded = base64.b64encode(HTML.encode('utf-8')).decode()
payload = {
    "message": "feat(website): premium clean homepage — Plus Jakarta Sans, Linear/Vercel aesthetic, animated splits, crisp dark theme",
    "content": encoded,
    "sha": sha
}

print("Pushing...")
resp = requests.put(API, headers=HEADERS, data=json.dumps(payload))

if resp.status_code in (200, 201):
    sha = resp.json()["commit"]["sha"]
    print(f"SUCCESS — {sha[:8]}")
    print("Live at https://syntharra.com in ~60-90s")
else:
    print(f"FAILED {resp.status_code}")
    sys.stdout.buffer.write(resp.text.encode('utf-8'))
    sys.exit(1)
