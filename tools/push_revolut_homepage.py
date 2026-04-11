#!/usr/bin/env python3
"""Push Revolut-quality homepage to syntharra.com"""
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
<meta name="description" content="Never miss a service call again. Syntharra deploys AI voice agents for HVAC, plumbing, and electrical businesses — answering calls 24/7, booking jobs, and growing revenue automatically.">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
/* ===== RESET & BASE ===== */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale}
body{font-family:'Inter',sans-serif;background:#ffffff;color:#0a0a14;overflow-x:clip}

/* ===== TOKENS ===== */
:root{
  --violet:#6C63FF;
  --ice:#00D4FF;
  --ink:#0a0a14;
  --ink-mid:#3a3a52;
  --ink-light:#7a7a96;
  --border:rgba(0,0,0,0.08);
  --surface:#ffffff;
  --bg-pale:#f8f8fc;
  --bg-dark:#06060f;
  --gradient:linear-gradient(135deg,#6C63FF 0%,#8B5CF6 50%,#00D4FF 100%);
  --gradient-dark:linear-gradient(135deg,#0d0d1f 0%,#15153a 100%);
  --r-sm:12px;
  --r-md:20px;
  --r-lg:32px;
}

/* ===== ANIMATIONS ===== */
@keyframes fadeUp{from{opacity:0;transform:translateY(40px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes floatPhone{0%,100%{transform:translateY(0) rotate(-2deg)}50%{transform:translateY(-16px) rotate(-2deg)}}
@keyframes gradShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes pulseGlow{0%,100%{box-shadow:0 0 0 0 rgba(108,99,255,0)}50%{box-shadow:0 0 60px 20px rgba(108,99,255,0.18)}}
@keyframes spinSlow{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
@keyframes dotBlink{0%,80%,100%{opacity:0}40%{opacity:1}}
@keyframes slideIn{from{opacity:0;transform:translateX(-20px)}to{opacity:1;transform:translateX(0)}}
@keyframes countUp{from{opacity:0;transform:scale(0.8)}to{opacity:1;transform:scale(1)}}

/* Scroll reveal */
.reveal{opacity:0;transform:translateY(48px);transition:opacity 0.7s cubic-bezier(.22,.61,.36,1),transform 0.7s cubic-bezier(.22,.61,.36,1)}
.reveal.visible{opacity:1;transform:translateY(0)}
.reveal-left{opacity:0;transform:translateX(-48px);transition:opacity 0.7s cubic-bezier(.22,.61,.36,1),transform 0.7s cubic-bezier(.22,.61,.36,1)}
.reveal-left.visible{opacity:1;transform:translateX(0)}
.reveal-right{opacity:0;transform:translateX(48px);transition:opacity 0.7s cubic-bezier(.22,.61,.36,1),transform 0.7s cubic-bezier(.22,.61,.36,1)}
.reveal-right.visible{opacity:1;transform:translateX(0)}
.reveal-scale{opacity:0;transform:scale(0.92);transition:opacity 0.6s cubic-bezier(.22,.61,.36,1),transform 0.6s cubic-bezier(.22,.61,.36,1)}
.reveal-scale.visible{opacity:1;transform:scale(1)}
.delay-1{transition-delay:0.1s}
.delay-2{transition-delay:0.2s}
.delay-3{transition-delay:0.3s}
.delay-4{transition-delay:0.4s}
.delay-5{transition-delay:0.5s}

/* ===== NAV ===== */
nav{
  position:fixed;top:0;left:0;right:0;z-index:1000;
  padding:0 32px;height:72px;
  display:flex;align-items:center;justify-content:space-between;
  transition:background 0.35s ease,backdrop-filter 0.35s ease,border-bottom 0.35s ease;
}
nav.scrolled{
  background:rgba(255,255,255,0.88);
  backdrop-filter:blur(24px);
  -webkit-backdrop-filter:blur(24px);
  border-bottom:1px solid var(--border);
}
.nav-logo{display:flex;align-items:center;gap:10px;text-decoration:none}
.nav-logo-icon svg{display:block}
.nav-logo-text{display:flex;flex-direction:column;line-height:1}
.nav-logo-name{font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:#ffffff;letter-spacing:-0.2px}
nav.scrolled .nav-logo-name{color:var(--ink)}
.nav-logo-sub{font-size:7px;font-weight:600;letter-spacing:1.8px;text-transform:uppercase;color:var(--violet);margin-top:3px}
.nav-links{display:flex;align-items:center;gap:32px;list-style:none}
.nav-links a{font-size:14px;font-weight:500;color:rgba(255,255,255,0.75);text-decoration:none;transition:color 0.2s}
.nav-links a:hover{color:#ffffff}
nav.scrolled .nav-links a{color:var(--ink-mid)}
nav.scrolled .nav-links a:hover{color:var(--ink)}
.nav-cta{
  font-family:'Syne',sans-serif;font-size:13px;font-weight:700;
  background:var(--violet);color:#fff;padding:10px 22px;
  border-radius:100px;text-decoration:none;letter-spacing:0.2px;
  transition:transform 0.2s,box-shadow 0.2s;white-space:nowrap;
}
.nav-cta:hover{transform:translateY(-1px);box-shadow:0 8px 24px rgba(108,99,255,0.4)}
.hamburger{
  display:flex;flex-direction:column;justify-content:center;gap:5px;
  width:40px;height:40px;cursor:pointer;background:none;border:none;padding:8px;
}
.hamburger span{
  display:block;width:22px;height:2px;background:#ffffff;
  transition:transform 0.3s,opacity 0.3s;border-radius:2px;
}
nav.scrolled .hamburger span{background:var(--ink)}

/* ===== MENU PANEL ===== */
.menu-backdrop{
  position:fixed;inset:0;background:rgba(10,10,20,0.6);z-index:1100;
  opacity:0;pointer-events:none;transition:opacity 0.3s;
  backdrop-filter:blur(4px);
}
.menu-backdrop.open{opacity:1;pointer-events:all}
.menu-panel{
  position:fixed;top:0;right:0;bottom:0;width:320px;
  background:#ffffff;z-index:1200;
  transform:translateX(100%);transition:transform 0.38s cubic-bezier(.22,.61,.36,1);
  overflow-y:auto;padding:28px 28px 40px;
  display:flex;flex-direction:column;
}
.menu-panel.open{transform:translateX(0)}
.menu-close{
  align-self:flex-end;width:36px;height:36px;background:var(--bg-pale);
  border-radius:50%;border:none;cursor:pointer;
  display:flex;align-items:center;justify-content:center;margin-bottom:24px;
  font-size:18px;color:var(--ink);
}
.menu-section{margin-bottom:28px}
.menu-section-title{
  font-size:10px;font-weight:700;letter-spacing:1.6px;text-transform:uppercase;
  color:var(--ink-light);margin-bottom:10px;
}
.menu-section a{
  display:block;font-size:15px;font-weight:500;color:var(--ink-mid);
  text-decoration:none;padding:7px 0;
  border-bottom:1px solid var(--border);transition:color 0.2s;
}
.menu-section a:last-child{border-bottom:none}
.menu-section a:hover{color:var(--violet)}
.menu-book{
  margin-top:auto;display:block;text-align:center;
  background:var(--gradient);color:#fff;padding:16px;border-radius:var(--r-md);
  font-family:'Syne',sans-serif;font-weight:700;font-size:15px;
  text-decoration:none;letter-spacing:0.2px;
  transition:transform 0.2s,box-shadow 0.2s;
}
.menu-book:hover{transform:translateY(-2px);box-shadow:0 8px 32px rgba(108,99,255,0.4)}

/* ===== HERO ===== */
.hero{
  min-height:100dvh;display:flex;flex-direction:column;justify-content:center;
  position:relative;overflow:hidden;padding:120px 32px 80px;
  background:var(--bg-dark);
}
/* animated mesh gradient */
.hero-bg{
  position:absolute;inset:0;z-index:0;
  background:radial-gradient(ellipse 80% 60% at 20% 40%,rgba(108,99,255,0.22) 0%,transparent 70%),
             radial-gradient(ellipse 60% 80% at 80% 20%,rgba(0,212,255,0.12) 0%,transparent 60%),
             radial-gradient(ellipse 40% 60% at 60% 80%,rgba(108,99,255,0.12) 0%,transparent 70%),
             var(--bg-dark);
  animation:gradShift 12s ease infinite;
  background-size:200% 200%;
}
/* grain texture overlay */
.hero-bg::after{
  content:'';position:absolute;inset:0;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
  background-size:200px 200px;opacity:0.4;pointer-events:none;
}
.hero-inner{
  position:relative;z-index:1;
  max-width:1400px;margin:0 auto;width:100%;
  display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:80px;
}
.hero-left{max-width:580px}
.hero-eyebrow{
  display:inline-flex;align-items:center;gap:8px;
  font-size:12px;font-weight:600;letter-spacing:1.4px;text-transform:uppercase;
  color:var(--ice);background:rgba(0,212,255,0.1);
  border:1px solid rgba(0,212,255,0.2);
  border-radius:100px;padding:7px 16px;margin-bottom:28px;
  animation:fadeUp 0.6s ease both;
}
.hero-eyebrow-dot{
  width:6px;height:6px;border-radius:50%;background:var(--ice);
  animation:pulseGlow 2s ease infinite;
}
.hero-h1{
  font-family:'Syne',sans-serif;
  font-size:clamp(46px,5.5vw,82px);
  font-weight:800;line-height:1.0;letter-spacing:-2px;
  color:#ffffff;margin-bottom:28px;
  animation:fadeUp 0.6s ease 0.1s both;
}
.hero-h1 .grad{
  background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;background-size:200% 200%;animation:gradShift 4s ease infinite;
}
.hero-body{
  font-size:18px;line-height:1.7;color:rgba(255,255,255,0.6);
  max-width:480px;margin-bottom:44px;font-weight:300;
  animation:fadeUp 0.6s ease 0.2s both;
}
.hero-actions{
  display:flex;flex-wrap:wrap;gap:14px;align-items:center;
  animation:fadeUp 0.6s ease 0.3s both;
}
.btn-primary{
  font-family:'Syne',sans-serif;font-size:15px;font-weight:700;
  background:var(--gradient);color:#fff;padding:16px 32px;
  border-radius:100px;text-decoration:none;letter-spacing:0.2px;
  transition:transform 0.2s,box-shadow 0.2s;white-space:nowrap;
  background-size:200% 200%;animation:gradShift 4s ease infinite;
}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 12px 40px rgba(108,99,255,0.5)}
.btn-ghost{
  font-size:15px;font-weight:500;color:rgba(255,255,255,0.7);
  text-decoration:none;padding:16px 24px;display:flex;align-items:center;gap:8px;
  transition:color 0.2s;
}
.btn-ghost:hover{color:#fff}
.btn-ghost-icon{
  width:36px;height:36px;border-radius:50%;
  background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.1);
  display:flex;align-items:center;justify-content:center;font-size:12px;
  transition:background 0.2s;
}
.btn-ghost:hover .btn-ghost-icon{background:rgba(255,255,255,0.14)}

/* Phone mockup */
.hero-right{display:flex;justify-content:center;align-items:center;position:relative;animation:fadeUp 0.8s ease 0.4s both}
.phone-wrap{position:relative;animation:floatPhone 5s ease-in-out infinite}
.phone-glow{
  position:absolute;inset:-40px;
  background:radial-gradient(ellipse 70% 70% at 50% 50%,rgba(108,99,255,0.25) 0%,transparent 70%);
  border-radius:50%;pointer-events:none;animation:pulseGlow 3s ease infinite;
}
.phone-mockup{
  width:260px;background:#ffffff;border-radius:40px;
  box-shadow:0 60px 120px rgba(0,0,0,0.6),0 20px 60px rgba(0,0,0,0.4),inset 0 1px 0 rgba(255,255,255,0.2);
  overflow:hidden;position:relative;z-index:1;
}
.phone-notch{
  height:28px;background:#ffffff;display:flex;align-items:center;justify-content:center;
}
.phone-notch-island{
  width:100px;height:18px;background:#000;border-radius:0 0 16px 16px;
}
.phone-screen{background:#06060f;padding:20px 20px 24px;min-height:420px}
.phone-status{
  display:flex;justify-content:space-between;align-items:center;
  margin-bottom:20px;
}
.phone-status-time{font-size:13px;font-weight:600;color:#fff}
.phone-status-icons{display:flex;gap:5px;align-items:center}
.phone-status-dot{width:4px;height:4px;border-radius:50%;background:rgba(255,255,255,0.5)}
.phone-app-header{margin-bottom:20px}
.phone-app-title{font-size:12px;font-weight:600;letter-spacing:0.8px;color:rgba(255,255,255,0.4);text-transform:uppercase;margin-bottom:4px}
.phone-app-subtitle{font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:#fff}
.phone-call-card{
  background:linear-gradient(135deg,rgba(108,99,255,0.15),rgba(0,212,255,0.08));
  border:1px solid rgba(108,99,255,0.2);border-radius:16px;padding:14px;margin-bottom:12px;
}
.phone-call-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.phone-call-name{font-size:14px;font-weight:600;color:#fff}
.phone-call-live{
  display:flex;align-items:center;gap:5px;
  font-size:10px;font-weight:700;letter-spacing:0.8px;
  color:#22c55e;background:rgba(34,197,94,0.1);
  border-radius:100px;padding:3px 8px;
}
.phone-call-live-dot{width:5px;height:5px;border-radius:50%;background:#22c55e;animation:pulseGlow 1.5s ease infinite}
.phone-call-msg{font-size:12px;color:rgba(255,255,255,0.55);line-height:1.5}
.phone-stat-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px}
.phone-stat{
  background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.06);
  border-radius:12px;padding:12px;
}
.phone-stat-label{font-size:10px;color:rgba(255,255,255,0.4);margin-bottom:4px;letter-spacing:0.5px}
.phone-stat-value{font-family:'Syne',sans-serif;font-size:18px;font-weight:700;color:#fff}
.phone-stat-change{font-size:10px;color:#22c55e;margin-top:2px}
.phone-jobs-row{
  background:rgba(108,99,255,0.08);border:1px solid rgba(108,99,255,0.15);
  border-radius:12px;padding:12px;
  display:flex;justify-content:space-between;align-items:center;
}
.phone-jobs-left{}
.phone-jobs-label{font-size:10px;color:rgba(255,255,255,0.4);margin-bottom:2px}
.phone-jobs-value{font-family:'Syne',sans-serif;font-size:20px;font-weight:700;color:var(--violet)}
.phone-jobs-icon{
  width:36px;height:36px;border-radius:10px;
  background:var(--violet);display:flex;align-items:center;justify-content:center;
  font-size:18px;
}

/* Floating badges around phone */
.hero-badge{
  position:absolute;background:#ffffff;border-radius:14px;
  padding:10px 14px;display:flex;align-items:center;gap:9px;
  box-shadow:0 12px 40px rgba(0,0,0,0.25);
  animation:fadeIn 0.6s ease both;
}
.hero-badge-1{top:18%;right:-14%;animation-delay:0.8s}
.hero-badge-2{bottom:25%;left:-14%;animation-delay:1s}
.hero-badge-icon{font-size:20px}
.hero-badge-label{font-size:11px;font-weight:600;color:var(--ink-mid);line-height:1.3}
.hero-badge-value{font-family:'Syne',sans-serif;font-size:15px;font-weight:800;color:var(--ink)}

/* ===== TRUST BAR ===== */
.trust-bar{
  background:var(--bg-dark);border-top:1px solid rgba(255,255,255,0.04);
  padding:32px;
}
.trust-inner{
  max-width:1400px;margin:0 auto;
  display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:0;
}
.trust-stat{
  flex:1;min-width:180px;text-align:center;padding:16px 24px;
  border-right:1px solid rgba(255,255,255,0.06);
}
.trust-stat:last-child{border-right:none}
.trust-num{
  font-family:'Syne',sans-serif;font-size:36px;font-weight:800;
  background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;line-height:1;margin-bottom:6px;
}
.trust-label{font-size:13px;font-weight:500;color:rgba(255,255,255,0.4);letter-spacing:0.3px}

/* ===== HOW IT WORKS ===== */
.how{padding:120px 32px;background:#ffffff}
.how-inner{max-width:1400px;margin:0 auto}
.section-label{
  display:inline-block;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;
  color:var(--violet);background:rgba(108,99,255,0.07);border-radius:100px;
  padding:6px 16px;margin-bottom:20px;
}
.section-h2{
  font-family:'Syne',sans-serif;font-size:clamp(36px,4vw,56px);font-weight:800;
  letter-spacing:-1.5px;color:var(--ink);line-height:1.1;max-width:600px;margin-bottom:16px;
}
.section-body{font-size:18px;line-height:1.7;color:var(--ink-mid);max-width:520px;margin-bottom:64px;font-weight:300}

.steps-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:24px}
.step{
  padding:32px 28px;border-radius:var(--r-md);
  border:1px solid var(--border);background:#ffffff;
  transition:border-color 0.3s,transform 0.3s,box-shadow 0.3s;
  position:relative;overflow:hidden;
}
.step::before{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:var(--gradient);transform:scaleX(0);transform-origin:left;
  transition:transform 0.4s ease;
}
.step:hover{border-color:rgba(108,99,255,0.2);transform:translateY(-4px);box-shadow:0 16px 48px rgba(108,99,255,0.08)}
.step:hover::before{transform:scaleX(1)}
.step-num{
  font-family:'Syne',sans-serif;font-size:42px;font-weight:800;letter-spacing:-2px;
  color:rgba(108,99,255,0.08);line-height:1;margin-bottom:20px;
}
.step-icon{
  width:44px;height:44px;border-radius:12px;background:rgba(108,99,255,0.08);
  display:flex;align-items:center;justify-content:center;font-size:20px;margin-bottom:16px;
}
.step-title{font-family:'Syne',sans-serif;font-size:17px;font-weight:700;color:var(--ink);margin-bottom:10px}
.step-body{font-size:14px;line-height:1.65;color:var(--ink-mid)}

/* ===== FEATURES ===== */
.features{padding:120px 32px;background:var(--bg-pale)}
.features-inner{max-width:1400px;margin:0 auto}
.features-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:64px}
.feat{
  background:#ffffff;border-radius:var(--r-lg);padding:40px;
  border:1px solid var(--border);overflow:hidden;position:relative;
  transition:transform 0.3s,box-shadow 0.3s,border-color 0.3s;
}
.feat:hover{transform:translateY(-4px);box-shadow:0 24px 60px rgba(0,0,0,0.07);border-color:rgba(108,99,255,0.15)}
.feat-large{grid-column:span 1;grid-row:span 2;display:flex;flex-direction:column;justify-content:space-between;min-height:420px}
.feat-icon{
  width:52px;height:52px;border-radius:14px;
  background:rgba(108,99,255,0.08);
  display:flex;align-items:center;justify-content:center;
  font-size:24px;margin-bottom:24px;
}
.feat-title{font-family:'Syne',sans-serif;font-size:22px;font-weight:700;color:var(--ink);margin-bottom:12px;line-height:1.2}
.feat-body{font-size:15px;line-height:1.7;color:var(--ink-mid)}
.feat-visual{
  margin-top:auto;border-radius:12px;
  background:var(--gradient-dark);padding:20px;
  display:flex;flex-direction:column;gap:10px;
}
.feat-bar-row{display:flex;align-items:center;gap:12px}
.feat-bar-label{font-size:12px;color:rgba(255,255,255,0.5);width:80px;flex-shrink:0}
.feat-bar-track{flex:1;height:6px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden}
.feat-bar-fill{height:100%;border-radius:3px;background:var(--gradient)}
.feat-bar-val{font-size:12px;font-weight:600;color:rgba(255,255,255,0.7);width:36px;text-align:right}
.feat-accent{background:linear-gradient(135deg,rgba(108,99,255,0.06),rgba(0,212,255,0.03));border-color:rgba(108,99,255,0.1)}

/* ===== INDUSTRIES ===== */
.industries{padding:120px 32px;background:#ffffff}
.industries-inner{max-width:1400px;margin:0 auto}
.industries-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:64px}
.industry{
  border-radius:var(--r-lg);overflow:hidden;position:relative;
  aspect-ratio:4/5;cursor:pointer;
  transition:transform 0.4s cubic-bezier(.22,.61,.36,1);
}
.industry:hover{transform:scale(1.02)}
.industry-bg{
  position:absolute;inset:0;
  display:flex;align-items:center;justify-content:center;font-size:80px;
}
.industry-bg-hvac{background:linear-gradient(160deg,#0d1b2a,#1a3a5c)}
.industry-bg-plumbing{background:linear-gradient(160deg,#0d2419,#1a4a32)}
.industry-bg-electrical{background:linear-gradient(160deg,#2a1a0d,#5c3a1a)}
.industry-overlay{
  position:absolute;inset:0;
  background:linear-gradient(to top,rgba(6,6,15,0.95) 0%,rgba(6,6,15,0.4) 50%,transparent 100%);
}
.industry-content{
  position:absolute;bottom:0;left:0;right:0;padding:32px;
}
.industry-tag{
  font-size:10px;font-weight:700;letter-spacing:1.6px;text-transform:uppercase;
  color:var(--ice);background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.2);
  border-radius:100px;padding:4px 12px;display:inline-block;margin-bottom:12px;
}
.industry-name{
  font-family:'Syne',sans-serif;font-size:26px;font-weight:800;color:#fff;
  margin-bottom:8px;letter-spacing:-0.5px;
}
.industry-body{font-size:14px;color:rgba(255,255,255,0.55);line-height:1.6;margin-bottom:20px}
.industry-link{
  display:inline-flex;align-items:center;gap:8px;
  font-size:13px;font-weight:600;color:var(--violet);text-decoration:none;
  transition:gap 0.2s;
}
.industry-link:hover{gap:12px}

/* ===== PROOF ===== */
.proof{padding:120px 32px;background:var(--bg-dark)}
.proof-inner{max-width:1400px;margin:0 auto}
.proof-header{text-align:center;margin-bottom:64px}
.proof-header .section-h2{color:#ffffff;margin:0 auto;text-align:center}
.proof-header .section-body{margin:16px auto 0;text-align:center;color:rgba(255,255,255,0.5)}
.proof-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.proof-card{
  background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);
  border-radius:var(--r-md);padding:32px;
  transition:background 0.3s,border-color 0.3s,transform 0.3s;
}
.proof-card:hover{background:rgba(255,255,255,0.06);border-color:rgba(108,99,255,0.25);transform:translateY(-4px)}
.proof-stars{display:flex;gap:3px;margin-bottom:20px}
.proof-star{color:#f59e0b;font-size:16px}
.proof-text{font-size:16px;line-height:1.7;color:rgba(255,255,255,0.7);margin-bottom:24px;font-weight:300}
.proof-author{display:flex;align-items:center;gap:12px}
.proof-avatar{
  width:40px;height:40px;border-radius:50%;
  background:var(--gradient);display:flex;align-items:center;justify-content:center;
  font-family:'Syne',sans-serif;font-size:14px;font-weight:800;color:#fff;
  flex-shrink:0;
}
.proof-name{font-size:14px;font-weight:600;color:#fff}
.proof-role{font-size:12px;color:rgba(255,255,255,0.4);margin-top:2px}

/* ===== CTA ===== */
.cta-section{
  padding:120px 32px;
  background:linear-gradient(135deg,#0d0d1f,#15153a);
  position:relative;overflow:hidden;
}
.cta-section::before{
  content:'';position:absolute;
  top:-200px;left:50%;transform:translateX(-50%);
  width:800px;height:800px;border-radius:50%;
  background:radial-gradient(ellipse,rgba(108,99,255,0.15) 0%,transparent 70%);
  pointer-events:none;
}
.cta-inner{max-width:800px;margin:0 auto;text-align:center;position:relative;z-index:1}
.cta-h2{
  font-family:'Syne',sans-serif;font-size:clamp(40px,5vw,68px);font-weight:800;
  letter-spacing:-2px;color:#fff;line-height:1.05;margin-bottom:20px;
}
.cta-h2 .grad{
  background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.cta-body{font-size:18px;color:rgba(255,255,255,0.5);line-height:1.7;margin-bottom:44px;font-weight:300}
.cta-actions{display:flex;flex-wrap:wrap;gap:14px;justify-content:center;align-items:center}
.btn-outline-white{
  font-family:'Syne',sans-serif;font-size:15px;font-weight:700;
  color:#fff;border:1.5px solid rgba(255,255,255,0.25);padding:16px 32px;
  border-radius:100px;text-decoration:none;letter-spacing:0.2px;
  transition:border-color 0.2s,background 0.2s;
}
.btn-outline-white:hover{border-color:rgba(255,255,255,0.6);background:rgba(255,255,255,0.05)}
.cta-disclaimer{font-size:13px;color:rgba(255,255,255,0.25);margin-top:24px}

/* ===== FOOTER ===== */
footer{background:var(--bg-dark);border-top:1px solid rgba(255,255,255,0.05);padding:80px 32px 40px}
.footer-inner{max-width:1400px;margin:0 auto}
.footer-top{display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr;gap:48px;margin-bottom:64px}
.footer-brand-logo{display:flex;align-items:center;gap:10px;text-decoration:none;margin-bottom:16px}
.footer-brand-name{font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:#fff}
.footer-brand-sub{font-size:7px;font-weight:600;letter-spacing:1.8px;text-transform:uppercase;color:var(--violet);display:block;margin-top:3px}
.footer-desc{font-size:14px;line-height:1.7;color:rgba(255,255,255,0.4);max-width:260px;margin-bottom:24px}
.footer-contact a{display:block;font-size:13px;color:rgba(255,255,255,0.35);text-decoration:none;margin-bottom:6px;transition:color 0.2s}
.footer-contact a:hover{color:rgba(255,255,255,0.7)}
.footer-col-title{font-size:11px;font-weight:700;letter-spacing:1.6px;text-transform:uppercase;color:rgba(255,255,255,0.3);margin-bottom:18px}
.footer-col a{display:block;font-size:14px;color:rgba(255,255,255,0.45);text-decoration:none;margin-bottom:11px;transition:color 0.2s}
.footer-col a:hover{color:rgba(255,255,255,0.85)}
.footer-bottom{
  padding-top:32px;border-top:1px solid rgba(255,255,255,0.06);
  display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;
}
.footer-copy{font-size:13px;color:rgba(255,255,255,0.25)}
.footer-legal{display:flex;gap:24px}
.footer-legal a{font-size:13px;color:rgba(255,255,255,0.25);text-decoration:none;transition:color 0.2s}
.footer-legal a:hover{color:rgba(255,255,255,0.6)}

/* ===== RESPONSIVE ===== */
@media(max-width:1024px){
  .hero-inner{grid-template-columns:1fr;gap:60px;text-align:center}
  .hero-left{max-width:100%}
  .hero-h1{font-size:clamp(40px,6vw,70px)}
  .hero-body{max-width:100%}
  .hero-actions{justify-content:center}
  .hero-right{display:none}
  .steps-grid{grid-template-columns:repeat(2,1fr)}
  .features-grid{grid-template-columns:1fr}
  .feat-large{grid-row:auto}
  .industries-grid{grid-template-columns:1fr}
  .proof-grid{grid-template-columns:1fr}
  .footer-top{grid-template-columns:1fr 1fr}
}
@media(max-width:768px){
  nav{padding:0 20px}
  .nav-links{display:none}
  .hero{padding:100px 20px 60px}
  .how,.features,.industries,.proof,.cta-section{padding:80px 20px}
  .steps-grid{grid-template-columns:1fr}
  .trust-bar{padding:24px 20px}
  .trust-stat{border-right:none;border-bottom:1px solid rgba(255,255,255,0.06);padding:14px}
  .trust-stat:last-child{border-bottom:none}
  .footer-top{grid-template-columns:1fr}
  .footer-bottom{flex-direction:column;text-align:center}
  .hero-badge{display:none}
}
@media(max-width:480px){
  .hero-h1{letter-spacing:-1px}
  .cta-h2{letter-spacing:-1px}
}
</style>
</head>
<body>

<!-- NAV -->
<nav id="mainNav">
  <a href="/" class="nav-logo" aria-label="Syntharra home">
    <div class="nav-logo-icon">
      <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="4" y="20" width="5" height="8" rx="2" fill="#6C63FF"/>
        <rect x="12" y="13" width="5" height="15" rx="2" fill="#6C63FF"/>
        <rect x="20" y="7" width="5" height="21" rx="2" fill="#6C63FF"/>
      </svg>
    </div>
    <div class="nav-logo-text">
      <span class="nav-logo-name">Syntharra</span>
      <span class="nav-logo-sub">Global AI Solutions</span>
    </div>
  </a>
  <ul class="nav-links">
    <li><a href="/how-it-works.html">How It Works</a></li>
    <li><a href="/hvac.html">HVAC</a></li>
    <li><a href="/case-studies.html">Case Studies</a></li>
    <li><a href="/faq.html">FAQ</a></li>
  </ul>
  <div style="display:flex;align-items:center;gap:12px">
    <a href="/demo.html" class="nav-cta">Get a Demo</a>
    <button class="hamburger" id="menuBtn" aria-label="Open menu">
      <span></span><span></span><span></span>
    </button>
  </div>
</nav>

<!-- MENU PANEL -->
<div class="menu-backdrop" id="menuBackdrop"></div>
<div class="menu-panel" id="menuPanel">
  <button class="menu-close" id="menuClose" aria-label="Close menu">&#x2715;</button>
  <div class="menu-section">
    <div class="menu-section-title">Product</div>
    <a href="/how-it-works.html">How It Works</a>
    <a href="/demo.html">Live Demo</a>
    <a href="/faq.html">FAQ</a>
    <a href="/ai-readiness.html">AI Readiness Score</a>
    <a href="/calculator.html">Revenue Calculator</a>
  </div>
  <div class="menu-section">
    <div class="menu-section-title">Learn</div>
    <a href="/case-studies.html">Case Studies</a>
    <a href="/blog.html">Blog</a>
  </div>
  <div class="menu-section">
    <div class="menu-section-title">Industries</div>
    <a href="/hvac.html">HVAC</a>
    <a href="/plumbing.html">Plumbing</a>
    <a href="/electrical.html">Electrical</a>
  </div>
  <div class="menu-section">
    <div class="menu-section-title">Company</div>
    <a href="/about.html">About</a>
    <a href="/affiliate.html">Affiliate Program</a>
    <a href="/careers.html">Careers</a>
    <a href="/status.html">System Status</a>
  </div>
  <a href="/demo.html" class="menu-book">Book a Free Demo &rarr;</a>
</div>

<!-- HERO -->
<section class="hero">
  <div class="hero-bg"></div>
  <div class="hero-inner">
    <div class="hero-left">
      <div class="hero-eyebrow">
        <span class="hero-eyebrow-dot"></span>
        AI Voice Agents — Live 24/7
      </div>
      <h1 class="hero-h1">
        Never Miss<br>
        a Service Call.<br>
        <span class="grad">Ever Again.</span>
      </h1>
      <p class="hero-body">Syntharra deploys AI voice agents that answer every call, book jobs, and handle after-hours — so your trade business grows while you work, not while you&#8217;re on the phone.</p>
      <div class="hero-actions">
        <a href="/demo.html" class="btn-primary">See It In Action &rarr;</a>
        <a href="/calculator.html" class="btn-ghost">
          <span class="btn-ghost-icon">&#9654;</span>
          Calculate Your Missed Revenue
        </a>
      </div>
    </div>
    <div class="hero-right">
      <div class="phone-wrap">
        <div class="phone-glow"></div>
        <div class="phone-mockup">
          <div class="phone-notch"><div class="phone-notch-island"></div></div>
          <div class="phone-screen">
            <div class="phone-status">
              <span class="phone-status-time">9:41</span>
              <div class="phone-status-icons">
                <div class="phone-status-dot"></div>
                <div class="phone-status-dot"></div>
                <div class="phone-status-dot"></div>
              </div>
            </div>
            <div class="phone-app-header">
              <div class="phone-app-title">Today</div>
              <div class="phone-app-subtitle">12 Jobs Booked</div>
            </div>
            <div class="phone-call-card">
              <div class="phone-call-header">
                <span class="phone-call-name">Mike T. — AC Repair</span>
                <div class="phone-call-live"><div class="phone-call-live-dot"></div> LIVE</div>
              </div>
              <div class="phone-call-msg">&#8220;...booked for Thursday 2pm, confirmation sent.&#8221;</div>
            </div>
            <div class="phone-stat-row">
              <div class="phone-stat">
                <div class="phone-stat-label">Calls Answered</div>
                <div class="phone-stat-value">47</div>
                <div class="phone-stat-change">&#8593; 23% vs last week</div>
              </div>
              <div class="phone-stat">
                <div class="phone-stat-label">Revenue Added</div>
                <div class="phone-stat-value">$8.4k</div>
                <div class="phone-stat-change">&#8593; This month</div>
              </div>
            </div>
            <div class="phone-jobs-row">
              <div class="phone-jobs-left">
                <div class="phone-jobs-label">Jobs In Queue</div>
                <div class="phone-jobs-value">5 pending</div>
              </div>
              <div class="phone-jobs-icon">&#128197;</div>
            </div>
          </div>
        </div>
        <!-- Floating badges -->
        <div class="hero-badge hero-badge-1">
          <div class="hero-badge-icon">&#9989;</div>
          <div>
            <div class="hero-badge-label">After-hours call<br>answered + booked</div>
          </div>
        </div>
        <div class="hero-badge hero-badge-2">
          <div class="hero-badge-icon">&#128176;</div>
          <div>
            <div class="hero-badge-label">Revenue recovered</div>
            <div class="hero-badge-value">+$1,240/mo</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- TRUST BAR -->
<div class="trust-bar">
  <div class="trust-inner">
    <div class="trust-stat reveal delay-1">
      <div class="trust-num">97%</div>
      <div class="trust-label">Call answer rate</div>
    </div>
    <div class="trust-stat reveal delay-2">
      <div class="trust-num">24/7</div>
      <div class="trust-label">Always on, never sleeps</div>
    </div>
    <div class="trust-stat reveal delay-3">
      <div class="trust-num">3 min</div>
      <div class="trust-label">Average time to live</div>
    </div>
    <div class="trust-stat reveal delay-4">
      <div class="trust-num">$8–12k</div>
      <div class="trust-label">Average monthly revenue added</div>
    </div>
    <div class="trust-stat reveal delay-5">
      <div class="trust-num">0</div>
      <div class="trust-label">Missed calls after go-live</div>
    </div>
  </div>
</div>

<!-- HOW IT WORKS -->
<section class="how">
  <div class="how-inner">
    <div class="reveal">
      <div class="section-label">How It Works</div>
      <h2 class="section-h2">Live in 3 minutes. No technical setup required.</h2>
      <p class="section-body">We handle everything. You provide your business info — we deploy a trained AI agent that sounds like your own staff.</p>
    </div>
    <div class="steps-grid">
      <div class="step reveal delay-1">
        <div class="step-num">01</div>
        <div class="step-icon">&#128203;</div>
        <div class="step-title">Onboard in 5 minutes</div>
        <p class="step-body">Fill out a short form. Tell us your services, service area, pricing, and hours. That&#8217;s it.</p>
      </div>
      <div class="step reveal delay-2">
        <div class="step-num">02</div>
        <div class="step-icon">&#129302;</div>
        <div class="step-title">We train your agent</div>
        <p class="step-body">Your AI agent learns your business — how to answer questions, qualify leads, and book jobs in your calendar.</p>
      </div>
      <div class="step reveal delay-3">
        <div class="step-num">03</div>
        <div class="step-icon">&#128222;</div>
        <div class="step-title">Forward your phone</div>
        <p class="step-body">Point your business number to your Syntharra line. Works with any phone system in under 60 seconds.</p>
      </div>
      <div class="step reveal delay-4">
        <div class="step-num">04</div>
        <div class="step-icon">&#128176;</div>
        <div class="step-title">Watch revenue grow</div>
        <p class="step-body">Every call answered, every job booked. Your dashboard shows calls, bookings, and revenue recovered in real time.</p>
      </div>
    </div>
  </div>
</section>

<!-- FEATURES -->
<section class="features">
  <div class="features-inner">
    <div class="reveal">
      <div class="section-label">The Platform</div>
      <h2 class="section-h2">Everything your business needs to never miss a job.</h2>
    </div>
    <div class="features-grid">
      <div class="feat feat-large feat-accent reveal-left">
        <div>
          <div class="feat-icon">&#127752;</div>
          <h3 class="feat-title">Natural conversation that actually books jobs</h3>
          <p class="feat-body">Your AI agent doesn&#8217;t just answer — it qualifies the lead, checks availability, gives a price range, and books the job directly into your calendar. Callers never know it&#8217;s AI.</p>
        </div>
        <div class="feat-visual">
          <div class="feat-bar-row">
            <div class="feat-bar-label">Call answered</div>
            <div class="feat-bar-track"><div class="feat-bar-fill" style="width:97%"></div></div>
            <div class="feat-bar-val">97%</div>
          </div>
          <div class="feat-bar-row">
            <div class="feat-bar-label">Job booked</div>
            <div class="feat-bar-track"><div class="feat-bar-fill" style="width:74%"></div></div>
            <div class="feat-bar-val">74%</div>
          </div>
          <div class="feat-bar-row">
            <div class="feat-bar-label">After-hours</div>
            <div class="feat-bar-track"><div class="feat-bar-fill" style="width:100%"></div></div>
            <div class="feat-bar-val">100%</div>
          </div>
        </div>
      </div>
      <div class="feat reveal-right delay-1">
        <div class="feat-icon">&#128336;</div>
        <h3 class="feat-title">24/7 after-hours coverage</h3>
        <p class="feat-body">The majority of missed calls happen outside business hours. Your AI handles them all — nights, weekends, holidays — without overtime pay.</p>
      </div>
      <div class="feat reveal-right delay-2">
        <div class="feat-icon">&#128203;</div>
        <h3 class="feat-title">Direct calendar integration</h3>
        <p class="feat-body">Bookings go straight to your scheduling software. No manual entry. No double-booking. No follow-up required.</p>
      </div>
      <div class="feat reveal delay-3">
        <div class="feat-icon">&#128202;</div>
        <h3 class="feat-title">Real-time revenue dashboard</h3>
        <p class="feat-body">See every call, every booking, every dollar recovered — in one clean dashboard built for trade business owners, not IT teams.</p>
      </div>
    </div>
  </div>
</section>

<!-- INDUSTRIES -->
<section class="industries">
  <div class="industries-inner">
    <div class="reveal">
      <div class="section-label">Industries</div>
      <h2 class="section-h2">Built for the trades, not generic call centres.</h2>
      <p class="section-body">Syntharra&#8217;s AI agents are trained specifically on HVAC, plumbing, and electrical — the terminology, the job types, the pricing conversations.</p>
    </div>
    <div class="industries-grid">
      <div class="industry reveal delay-1">
        <div class="industry-bg industry-bg-hvac">&#10052;&#65039;</div>
        <div class="industry-overlay"></div>
        <div class="industry-content">
          <div class="industry-tag">Most Popular</div>
          <div class="industry-name">HVAC</div>
          <p class="industry-body">AC repair, furnace service, duct cleaning — your agent knows it all and books it effortlessly.</p>
          <a href="/hvac.html" class="industry-link">Explore HVAC &#8594;</a>
        </div>
      </div>
      <div class="industry reveal delay-2">
        <div class="industry-bg industry-bg-plumbing">&#128166;</div>
        <div class="industry-overlay"></div>
        <div class="industry-content">
          <div class="industry-tag">High Demand</div>
          <div class="industry-name">Plumbing</div>
          <p class="industry-body">From emergency leaks to routine maintenance — capture every call before your competitor does.</p>
          <a href="/plumbing.html" class="industry-link">Explore Plumbing &#8594;</a>
        </div>
      </div>
      <div class="industry reveal delay-3">
        <div class="industry-bg industry-bg-electrical">&#9889;</div>
        <div class="industry-overlay"></div>
        <div class="industry-content">
          <div class="industry-tag">Fast Growing</div>
          <div class="industry-name">Electrical</div>
          <p class="industry-body">Panel upgrades, EV charger installs, service calls — your AI agent qualifies and books every lead.</p>
          <a href="/electrical.html" class="industry-link">Explore Electrical &#8594;</a>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- PROOF -->
<section class="proof">
  <div class="proof-inner">
    <div class="proof-header reveal">
      <div class="section-label">Results</div>
      <h2 class="section-h2">Real businesses. Real revenue.</h2>
      <p class="section-body">Trade business owners who switched to Syntharra don&#8217;t go back.</p>
    </div>
    <div class="proof-grid">
      <div class="proof-card reveal delay-1">
        <div class="proof-stars">
          <span class="proof-star">&#9733;</span><span class="proof-star">&#9733;</span>
          <span class="proof-star">&#9733;</span><span class="proof-star">&#9733;</span>
          <span class="proof-star">&#9733;</span>
        </div>
        <p class="proof-text">&#8220;We were losing 8&#8211;10 calls a week after hours. Syntharra fixed that in the first 24 hours. Within a month we&#8217;d booked over $14k in jobs we would have missed.&#8221;</p>
        <div class="proof-author">
          <div class="proof-avatar">MT</div>
          <div>
            <div class="proof-name">Mark T.</div>
            <div class="proof-role">Owner, Arctic Breeze HVAC &#183; Phoenix, AZ</div>
          </div>
        </div>
      </div>
      <div class="proof-card reveal delay-2">
        <div class="proof-stars">
          <span class="proof-star">&#9733;</span><span class="proof-star">&#9733;</span>
          <span class="proof-star">&#9733;</span><span class="proof-star">&#9733;</span>
          <span class="proof-star">&#9733;</span>
        </div>
        <p class="proof-text">&#8220;My receptionist was costing me $3,200/mo and still missing calls on busy days. Syntharra costs less and never misses. It&#8217;s not even a comparison anymore.&#8221;</p>
        <div class="proof-author">
          <div class="proof-avatar">JS</div>
          <div>
            <div class="proof-name">Jason S.</div>
            <div class="proof-role">Owner, Reliable Plumbing Co. &#183; Denver, CO</div>
          </div>
        </div>
      </div>
      <div class="proof-card reveal delay-3">
        <div class="proof-stars">
          <span class="proof-star">&#9733;</span><span class="proof-star">&#9733;</span>
          <span class="proof-star">&#9733;</span><span class="proof-star">&#9733;</span>
          <span class="proof-star">&#9733;</span>
        </div>
        <p class="proof-text">&#8220;I was skeptical about AI on the phone but customers genuinely can&#8217;t tell. We&#8217;ve booked 40+ jobs in the first month. The ROI is insane for a small shop like mine.&#8221;</p>
        <div class="proof-author">
          <div class="proof-avatar">RC</div>
          <div>
            <div class="proof-name">Rachel C.</div>
            <div class="proof-role">Owner, Bright Spark Electric &#183; Austin, TX</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- CTA -->
<section class="cta-section">
  <div class="cta-inner">
    <div class="reveal">
      <h2 class="cta-h2">Your next missed call<br>is <span class="grad">revenue left behind.</span></h2>
      <p class="cta-body">Every unanswered call is an average of $400&#8211;$800 in lost revenue. Syntharra makes sure that never happens again.</p>
      <div class="cta-actions">
        <a href="/demo.html" class="btn-primary">Get Your Free Demo</a>
        <a href="/calculator.html" class="btn-outline-white">Calculate Your Revenue Gap</a>
      </div>
      <p class="cta-disclaimer">No contract. No technical setup. Live in under 3 minutes.</p>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div class="footer-inner">
    <div class="footer-top">
      <div>
        <a href="/" class="footer-brand-logo">
          <svg width="28" height="28" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="20" width="5" height="8" rx="2" fill="#6C63FF"/>
            <rect x="12" y="13" width="5" height="15" rx="2" fill="#6C63FF"/>
            <rect x="20" y="7" width="5" height="21" rx="2" fill="#6C63FF"/>
          </svg>
          <div>
            <span class="footer-brand-name">Syntharra</span>
            <span class="footer-brand-sub">Global AI Solutions</span>
          </div>
        </a>
        <p class="footer-desc">AI voice agents built for trade businesses. Never miss a call. Never lose a job to voicemail again.</p>
        <div class="footer-contact">
          <a href="mailto:support@syntharra.com">support@syntharra.com</a>
          <a href="mailto:feedback@syntharra.com">feedback@syntharra.com</a>
        </div>
      </div>
      <div>
        <div class="footer-col-title">Product</div>
        <div class="footer-col">
          <a href="/how-it-works.html">How It Works</a>
          <a href="/demo.html">Live Demo</a>
          <a href="/calculator.html">Revenue Calculator</a>
          <a href="/ai-readiness.html">AI Readiness Score</a>
          <a href="/faq.html">FAQ</a>
        </div>
      </div>
      <div>
        <div class="footer-col-title">Industries</div>
        <div class="footer-col">
          <a href="/hvac.html">HVAC</a>
          <a href="/plumbing.html">Plumbing</a>
          <a href="/electrical.html">Electrical</a>
        </div>
        <div class="footer-col-title" style="margin-top:24px">Learn</div>
        <div class="footer-col">
          <a href="/case-studies.html">Case Studies</a>
          <a href="/blog.html">Blog</a>
        </div>
      </div>
      <div>
        <div class="footer-col-title">Company</div>
        <div class="footer-col">
          <a href="/about.html">About</a>
          <a href="/affiliate.html">Affiliates</a>
          <a href="/careers.html">Careers</a>
          <a href="/status.html">System Status</a>
        </div>
        <div class="footer-col-title" style="margin-top:24px">Legal</div>
        <div class="footer-col">
          <a href="/privacy.html">Privacy Policy</a>
          <a href="/terms.html">Terms of Service</a>
          <a href="/security.html">Security</a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="footer-copy">&copy; 2026 Syntharra Global AI Solutions. All rights reserved.</div>
      <div class="footer-legal">
        <a href="/privacy.html">Privacy</a>
        <a href="/terms.html">Terms</a>
        <a href="/security.html">Security</a>
      </div>
    </div>
  </div>
</footer>

<script>
// Nav scroll behaviour
const nav = document.getElementById('mainNav');
window.addEventListener('scroll', () => {
  if (window.scrollY > 40) nav.classList.add('scrolled');
  else nav.classList.remove('scrolled');
}, {passive: true});

// Hamburger menu
const menuBtn = document.getElementById('menuBtn');
const menuClose = document.getElementById('menuClose');
const menuPanel = document.getElementById('menuPanel');
const menuBackdrop = document.getElementById('menuBackdrop');

function openMenu() {
  menuPanel.classList.add('open');
  menuBackdrop.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeMenu() {
  menuPanel.classList.remove('open');
  menuBackdrop.classList.remove('open');
  document.body.style.overflow = '';
}

menuBtn.addEventListener('click', openMenu);
menuClose.addEventListener('click', closeMenu);
menuBackdrop.addEventListener('click', closeMenu);

// Scroll reveal
const revealEls = document.querySelectorAll('.reveal, .reveal-left, .reveal-right, .reveal-scale');
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, {threshold: 0.1, rootMargin: '0px 0px -40px 0px'});

revealEls.forEach(el => observer.observe(el));
</script>

</body>
</html>'''

# Fetch current SHA
print("Fetching current file SHA...")
r = requests.get(API, headers=HEADERS)
r.raise_for_status()
data = r.json()
sha = data["sha"]
print(f"SHA: {sha}")

# Verify single style block
assert HTML.count("<style>") == 1, f"Multiple <style> blocks! Count: {HTML.count('<style>')}"
print("Style block check: OK")

# Push
encoded = base64.b64encode(HTML.encode('utf-8')).decode()
payload = {
    "message": "feat(website): Revolut-quality homepage — animated scroll reveals, editorial typography, phone mockup, premium dark design",
    "content": encoded,
    "sha": sha
}

print("Pushing to GitHub...")
resp = requests.put(API, headers=HEADERS, data=json.dumps(payload))

if resp.status_code in (200, 201):
    commit_sha = resp.json()["commit"]["sha"]
    print(f"SUCCESS — commit {commit_sha[:8]}")
    print("Live at: https://syntharra.com (deploy in ~60-90s)")
else:
    print(f"FAILED: {resp.status_code}")
    sys.stdout.buffer.write(resp.text.encode('utf-8'))
    sys.exit(1)
