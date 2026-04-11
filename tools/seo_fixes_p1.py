#!/usr/bin/env python3
"""
Syntharra SEO Fixes - Part 1
Fixes from 2026-04-11 audit:
  - index.html: fix double H1 + add Organization/WebSite/Service JSON-LD
  - how-it-works.html: fix double H1 + fix schema pricing + fix og:image
  - faq.html: add meta description, OG tags, Twitter card, canonical
  - case-studies.html: add Twitter card, enrich og:title
  - blog.html: enrich og:title, fix og:image
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests, base64, time, re

TOKEN = "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"
REPO  = "Syntharra/syntharra-website"
API   = f"https://api.github.com/repos/{REPO}/contents"
H     = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

ICON = "https://raw.githubusercontent.com/Syntharra/syntharra-automations/main/brand-assets/email-signature/syntharra-icon.png"
OG   = "https://www.syntharra.com/og-image.png"

def fetch(filename):
    r = requests.get(f"{API}/{filename}", headers=H)
    if r.status_code != 200:
        raise Exception(f"Fetch {filename}: {r.status_code} {r.text[:120]}")
    d = r.json()
    return d["sha"], base64.b64decode(d["content"]).decode("utf-8")

def push(filename, content, sha, msg):
    payload = {
        "message": msg,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "sha": sha
    }
    r = requests.put(f"{API}/{filename}", headers=H, json=payload)
    ok = r.status_code in (200, 201)
    status = "PUSHED" if ok else "FAILED"
    print(f"  [{status}] {filename} [{r.status_code}]")
    if not ok:
        print(f"    Error: {r.text[:300]}")
    time.sleep(1.5)
    return ok

def sub(content, old, new, label):
    if old not in content:
        print(f"  [WARN] NOT FOUND: {label}")
        return content
    result = content.replace(old, new, 1)
    print(f"  [OK] replaced: {label}")
    return result

def rsub(content, pattern, replacement, label, flags=re.DOTALL):
    result, n = re.subn(pattern, replacement, content, flags=flags)
    if n == 0:
        print(f"  [WARN] REGEX NOT FOUND: {label}")
    else:
        print(f"  [OK] regex replaced ({n}x): {label}")
    return result


# ───────────────────────────────────────────────────────────────────────
# 1. index.html — fix double H1 + add full JSON-LD schema block
# ───────────────────────────────────────────────────────────────────────
print("\n=== 1/5  index.html ===")
sha, c = fetch("index.html")

# Fix: "Ready to scale up?" CTA section uses H1 — demote to H2
c = rsub(c,
    r'<h1([^>]*?)>([\s\S]*?Ready to scale up\?[\s\S]*?)</h1>',
    r'<h2\1>\2</h2>',
    "index CTA H1 demoted to H2")

# Add Organisation + WebSite + Service JSON-LD before </head>
SCHEMA = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://www.syntharra.com/#organization",
      "name": "Syntharra",
      "url": "https://www.syntharra.com",
      "logo": {
        "@type": "ImageObject",
        "url": "https://www.syntharra.com/favicon.svg",
        "width": 512,
        "height": 512
      },
      "description": "AI phone receptionist for HVAC and trade businesses. Answers every call 24/7, qualifies leads, and books jobs automatically.",
      "contactPoint": {
        "@type": "ContactPoint",
        "contactType": "customer support",
        "email": "support@syntharra.com",
        "areaServed": "US",
        "availableLanguage": "English"
      }
    },
    {
      "@type": "WebSite",
      "@id": "https://www.syntharra.com/#website",
      "url": "https://www.syntharra.com",
      "name": "Syntharra",
      "publisher": { "@id": "https://www.syntharra.com/#organization" },
      "potentialAction": {
        "@type": "SearchAction",
        "target": {
          "@type": "EntryPoint",
          "urlTemplate": "https://www.syntharra.com/faq.html?q={search_term_string}"
        },
        "query-input": "required name=search_term_string"
      }
    },
    {
      "@type": "Service",
      "@id": "https://www.syntharra.com/#service",
      "name": "Syntharra AI Receptionist",
      "provider": { "@id": "https://www.syntharra.com/#organization" },
      "serviceType": "AI Phone Receptionist",
      "description": "24/7 AI receptionist for HVAC, plumbing, and electrical contractors. Captures every lead, qualifies callers, books jobs, and sends instant notifications.",
      "offers": {
        "@type": "Offer",
        "name": "HVAC Standard",
        "price": "697",
        "priceCurrency": "USD",
        "description": "700 minutes/month, 24/7 AI receptionist, HVAC-trained scripts, setup included, no contracts"
      },
      "areaServed": {
        "@type": "Country",
        "name": "United States"
      }
    }
  ]
}
</script>
</head>'''

c = sub(c, "</head>", SCHEMA, "index JSON-LD schema insert")
push("index.html", c, sha, "seo(P0): fix double H1 + add Organization/WebSite/Service JSON-LD schema")


# ───────────────────────────────────────────────────────────────────────
# 2. how-it-works.html — fix double H1 + fix schema pricing + fix og:image
# ───────────────────────────────────────────────────────────────────────
print("\n=== 2/5  how-it-works.html ===")
sha, c = fetch("how-it-works.html")

# Fix: "Ready to get started?" H1 demote to H2
c = rsub(c,
    r'<h1([^>]*?)>([\s\S]*?Ready to get started\?[\s\S]*?)</h1>',
    r'<h2\1>\2</h2>',
    "how-it-works CTA H1 demoted to H2")

# Fix schema: replace Product JSON-LD block that has wrong $497/$997 pricing
def fix_pricing_schema(m):
    s = m.group(0)
    if '"497"' in s or '"997"' in s or '497' in s:
        return (
            '<script type="application/ld+json">\n'
            '{\n'
            '  "@context": "https://schema.org",\n'
            '  "@type": "Service",\n'
            '  "name": "How Syntharra AI Receptionist Works",\n'
            '  "provider": {\n'
            '    "@type": "Organization",\n'
            '    "name": "Syntharra",\n'
            '    "url": "https://www.syntharra.com"\n'
            '  },\n'
            '  "serviceType": "AI Phone Receptionist",\n'
            '  "description": "Set up your AI receptionist in 24 hours. Forward your number, Syntharra trains your agent, you start capturing leads immediately. No hardware, no contracts.",\n'
            '  "offers": {\n'
            '    "@type": "Offer",\n'
            '    "name": "HVAC Standard",\n'
            '    "price": "697",\n'
            '    "priceCurrency": "USD",\n'
            '    "description": "700 minutes/month, 24/7 AI receptionist, HVAC-trained scripts, setup included"\n'
            '  },\n'
            '  "areaServed": {\n'
            '    "@type": "Country",\n'
            '    "name": "United States"\n'
            '  }\n'
            '}\n'
            '</script>'
        )
    return s

orig_c = c
c = re.sub(r'<script type="application/ld\+json">[\s\S]*?</script>', fix_pricing_schema, c)
if c != orig_c:
    print("  [OK] replaced: how-it-works schema pricing fixed")
else:
    print("  [WARN] schema pricing block not found or unchanged")

# Fix og:image
if ICON in c:
    c = c.replace(ICON, OG)
    print("  [OK] replaced: how-it-works og:image")
else:
    print("  [INFO] og:image already correct or icon not found")

push("how-it-works.html", c, sha,
     "seo(P0): fix double H1 + fix schema pricing $497/$997->$697 + fix og:image")


# ───────────────────────────────────────────────────────────────────────
# 3. faq.html — add meta description, full OG block, Twitter card, canonical
# ───────────────────────────────────────────────────────────────────────
print("\n=== 3/5  faq.html ===")
sha, c = fetch("faq.html")

FAQ_META = (
    '<meta name="description" content="Every question answered about Syntharra\'s AI receptionist for HVAC contractors'
    ' -- pricing, setup, integrations, call handling, and 24/7 availability.">\n'
    '<meta property="og:title" content="HVAC AI Answering Service FAQ | Syntharra">\n'
    '<meta property="og:description" content="Every question answered about Syntharra\'s AI receptionist for HVAC contractors'
    ' -- pricing, setup, integrations, call handling, and 24/7 availability.">\n'
    '<meta property="og:image" content="https://www.syntharra.com/og-image.png">\n'
    '<meta property="og:image:width" content="1200">\n'
    '<meta property="og:image:height" content="630">\n'
    '<meta property="og:url" content="https://www.syntharra.com/faq.html">\n'
    '<meta property="og:type" content="website">\n'
    '<meta name="twitter:card" content="summary_large_image">\n'
    '<meta name="twitter:title" content="HVAC AI Answering Service FAQ | Syntharra">\n'
    '<meta name="twitter:description" content="Every question answered about Syntharra\'s AI receptionist for HVAC contractors'
    ' -- pricing, setup, integrations, call handling, and 24/7 availability.">\n'
    '<meta name="twitter:image" content="https://www.syntharra.com/og-image.png">\n'
    '<link rel="canonical" href="https://www.syntharra.com/faq.html">'
)

if 'og:title' in c:
    print("  [INFO] OG tags already present -- skipping")
else:
    c = rsub(c, r'(</title>)', r'\1\n' + FAQ_META, "faq OG/Twitter/canonical insert")

push("faq.html", c, sha,
     "seo(P1): add meta description, OG tags, Twitter card, canonical URL")


# ───────────────────────────────────────────────────────────────────────
# 4. case-studies.html — add Twitter card + enrich og:title + add og:url
# ───────────────────────────────────────────────────────────────────────
print("\n=== 4/5  case-studies.html ===")
sha, c = fetch("case-studies.html")

# Enrich og:title
c = sub(c,
    'content="Case Studies | Syntharra"',
    'content="HVAC AI Receptionist Results &amp; Case Studies | Syntharra"',
    "case-studies og:title enrich")

# Add og:url if missing
if 'og:url' not in c:
    c = rsub(c,
        r'(<meta property="og:image"[^>]+>)',
        r'\1\n<meta property="og:url" content="https://www.syntharra.com/case-studies.html">',
        "case-studies og:url insert")

# Add Twitter card
if 'twitter:card' not in c:
    TWITTER_BLOCK = (
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="twitter:title" content="HVAC AI Receptionist Results &amp; Case Studies | Syntharra">\n'
        '<meta name="twitter:description" content="Real results from HVAC contractors using Syntharra. '
        'See how they captured missed calls, booked more jobs, and grew revenue 24/7.">\n'
        '<meta name="twitter:image" content="https://www.syntharra.com/og-image.png">'
    )
    c = rsub(c,
        r'(<meta property="og:image"[^>]+>)',
        r'\1\n' + TWITTER_BLOCK,
        "case-studies Twitter card insert")
else:
    print("  [INFO] twitter:card already present")

push("case-studies.html", c, sha,
     "seo(P1): enrich og:title + add og:url + add Twitter card")


# ───────────────────────────────────────────────────────────────────────
# 5. blog.html — enrich og:title + fix og:image
# ───────────────────────────────────────────────────────────────────────
print("\n=== 5/5  blog.html ===")
sha, c = fetch("blog.html")

c = sub(c,
    'content="Blog | Syntharra"',
    'content="HVAC &amp; Contractor AI Blog | Syntharra"',
    "blog og:title enrich")

if ICON in c:
    c = c.replace(ICON, OG)
    print("  [OK] replaced: blog og:image")
else:
    print("  [INFO] blog og:image already correct or icon not found")

push("blog.html", c, sha,
     "seo(P2): enrich og:title + fix og:image to branded 1200x630")

print("\n=== Part 1 complete. Run seo_fixes_p2.py next. ===")
