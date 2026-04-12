#!/usr/bin/env python3
"""
short_form_content.py — Short-form video script generator for Syntharra.

Generates 30-second TikTok / Instagram Reels / YouTube Shorts scripts
targeting HVAC owner-operators who lose calls when they're busy.

10 pre-written script templates. Each has a hook (3s), problem (5s),
solution (10s), CTA (5s), platform notes, visual direction, category,
and performance notes.

Usage:
    python tools/short_form_content.py                   # print all 10 scripts
    python tools/short_form_content.py --script 1       # print script 1
    python tools/short_form_content.py --week 1         # scripts 1-3 (week 1)
    python tools/short_form_content.py --week 2         # scripts 4-6 (week 2)
    python tools/short_form_content.py --week 3         # scripts 7-10 (week 3)
    python tools/short_form_content.py --output slack   # Slack-formatted block
    python tools/short_form_content.py --output json    # machine-readable JSON

Cost: $0. Pure Python stdlib, no API calls.
"""
from __future__ import annotations

import argparse
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Script library
# ---------------------------------------------------------------------------

SCRIPTS: list[dict] = [
    {
        "id": 1,
        "title": "Birthday Party",
        "category": "social_proof",
        "hook": (
            "I ran out of my own birthday party mid-song because a homeowner's "
            "AC died. That moment changed everything."
        ),
        "problem": (
            "Every HVAC owner knows it. You're off the clock, with your family, "
            "and your phone doesn't care. Miss that call, lose the job."
        ),
        "solution": (
            "So I built Syntharra. An AI receptionist that answers every HVAC "
            "call — 24 hours a day, 7 days a week, $697 a month flat. It "
            "captures the lead, books the appointment, and texts you a summary. "
            "I tested it on my own business first. Now other contractors use it."
        ),
        "cta": (
            "14-day free pilot at syntharra.com. No credit card until you decide "
            "it's paying for itself."
        ),
        "platform_notes": (
            "TikTok: Open mid-action — party noise cuts to silence, then Dan "
            "speaking to camera. Keep face in frame the whole time, emotion "
            "carries the watch-time.\n"
            "Reels: Caption-subtitle every word — founder story resonates best "
            "on Reels with sound OFF. Use the birthday-party B-roll as cover art.\n"
            "Shorts: Put the URL card at second 25. Shorts algorithm favors "
            "replays; end with a direct question: 'Sound familiar?'"
        ),
        "visual_direction": (
            "Open: 3-second clip of a birthday cake with candles (B-roll or "
            "stock). Cut to Dan at his desk or in his truck, talking directly "
            "to camera. Mid-roll: screen-record of the Syntharra AI picking up "
            "a call (anonymized). Close: syntharra.com URL card."
        ),
        "estimated_performance": (
            "Founder story + relatable pain = high share rate. The birthday "
            "party detail is specific and visual — viewers mentally place "
            "themselves in the scene. Specificity outperforms vague claims in "
            "HVAC owner communities every time."
        ),
    },
    {
        "id": 2,
        "title": "2am Math",
        "category": "pain_point",
        "hook": (
            "It's 2am. AC breaks. Homeowner calls 3 HVAC shops back to back. "
            "Who gets the job?"
        ),
        "problem": (
            "The one who answers. Not the best tech. Not the cheapest price. "
            "The one who picked up. At 2am, that's almost never you."
        ),
        "solution": (
            "Syntharra answers every call you can't. It sounds like a real "
            "receptionist, captures the job details, schedules the appointment, "
            "and pings you immediately. You wake up to a booked job, not a "
            "missed opportunity. $697 a month, one phone number, zero missed calls."
        ),
        "cta": (
            "Try it free for 14 days at syntharra.com. If it doesn't book you "
            "a single job, walk away. No hard feelings."
        ),
        "platform_notes": (
            "TikTok: Rhetorical hook works ONLY if delivered fast and punchy. "
            "No pause between 'Who gets the job?' and the answer. Rapid cut "
            "on the answer line.\n"
            "Reels: Text overlay '2AM' in large font for silent viewers. "
            "Tap-to-unmute rate increases with strong text hooks.\n"
            "Shorts: This script loops well — the rhetorical question pulls "
            "replays. End card must be visible 3+ seconds."
        ),
        "visual_direction": (
            "Open: Dark room, phone screen glowing (2:07am timestamp). Cut to "
            "three phones ringing in quick succession (can be illustrated with "
            "text on screen). Cut to Dan in front of his phone setup. "
            "Mid-roll: Syntharra call answer animation or screen-record demo. "
            "Close: Calm — Dan asleep, phone on desk, notification pops."
        ),
        "estimated_performance": (
            "Rhetorical hook creates an immediate mental simulation. HVAC owners "
            "have *lived* this scenario. The specific time (2am) is credible and "
            "visceral. This format works in saturated feeds because it asks a "
            "question the viewer can't immediately answer."
        ),
    },
    {
        "id": 3,
        "title": "$697 Reality Check",
        "category": "education",
        "hook": (
            "Why does an AI phone receptionist cost $697 a month? I'll show you "
            "the math in 30 seconds."
        ),
        "problem": (
            "A human receptionist costs $3,000 to $4,000 a month, works 8 hours, "
            "takes breaks, and calls in sick. And they still miss calls."
        ),
        "solution": (
            "Syntharra is always on. It answers HVAC emergencies at midnight, "
            "captures every lead, books appointments, and texts you a summary. "
            "No benefits. No PTO. No 'I'll call them back after lunch.' "
            "$697 flat, one number, unlimited calls. We built it for HVAC "
            "contractors specifically — it knows the lingo, knows the urgency, "
            "knows when to escalate."
        ),
        "cta": (
            "14-day free pilot. No card up front. syntharra.com."
        ),
        "platform_notes": (
            "TikTok: Transparency hook performs extremely well in the B2B / "
            "small-biz creator niche. 'I'll show you the math' is a pattern "
            "interrupt that earns 10+ second retention.\n"
            "Reels: Works well as a talking-head with price overlaid in text. "
            "No fancy production needed — authenticity drives credibility here.\n"
            "Shorts: Put 'WHY $697?' as a title card in the first frame. "
            "YouTube Shorts titles are visible before play."
        ),
        "visual_direction": (
            "Dan to camera, conversational tone — NOT pitchy. Optional: "
            "split-screen showing a human receptionist (stock photo) vs "
            "a phone screen showing the AI. Text overlays for each price point. "
            "End with a simple URL card."
        ),
        "estimated_performance": (
            "Transparency pricing content consistently outperforms promotional "
            "content in trades audiences. HVAC owners are skeptical buyers — "
            "showing the math disarms objections before they're raised. "
            "High save rate expected (people bookmark pricing content)."
        ),
    },
    {
        "id": 4,
        "title": "Before / After Voicemail",
        "category": "comparison",
        "hook": (
            "Before Syntharra: [voicemail beep, generic message]. "
            "After Syntharra: [AI answers, takes the job]. $697 a month."
        ),
        "problem": (
            "Every homeowner calling an HVAC shop after hours is deciding: "
            "do I leave a message and hope, or do I call the next number? "
            "Most call the next number."
        ),
        "solution": (
            "Syntharra answers with your company name, takes the job details, "
            "books the appointment, and confirms it in writing. The homeowner "
            "feels like they've already been helped. You get a booked job in "
            "your inbox when you wake up. No voicemail. No callback limbo."
        ),
        "cta": (
            "Try it free for 14 days. No card. syntharra.com."
        ),
        "platform_notes": (
            "TikTok: The audio contrast (voicemail beep vs professional AI) "
            "is the hook. Use actual audio — record your own voicemail, then "
            "record Syntharra answering. Side-by-side audio is visceral.\n"
            "Reels: Works as a split-screen. Left: phone going to voicemail. "
            "Right: Syntharra picking up. Static text overlays explain each side.\n"
            "Shorts: Voicemail beep + long silence can be used as a comedic "
            "pause before the cut to Syntharra. Play the contrast for effect."
        ),
        "visual_direction": (
            "Half the video: phone going to a generic voicemail, frustration "
            "on the homeowner's face (can be recreated). Second half: phone "
            "rings, AI voice answers confidently, call is booked. "
            "Clean cut between the two states. No narration needed — "
            "the audio contrast carries the message."
        ),
        "estimated_performance": (
            "Before/after format is the most reliably engaging structure in "
            "short-form video. The specificity (voicemail beep as the 'before') "
            "makes it instantly recognizable to HVAC owners. Zero production "
            "cost, high shareability."
        ),
    },
    {
        "id": 5,
        "title": "Competition Reveal",
        "category": "pain_point",
        "hook": (
            "Every time your phone goes to voicemail, THIS is what's happening "
            "at your competitor's shop."
        ),
        "problem": (
            "There's always an HVAC company in your market that answers faster "
            "than you. They're not better technicians. They just have a system. "
            "And they're taking your emergency calls right now."
        ),
        "solution": (
            "Syntharra is that system. AI receptionist, answers immediately, "
            "24/7, for $697 a month. Captures every inbound lead your competitor "
            "would have gotten if you sent them to voicemail. "
            "One phone number. Unlimited calls. No missed jobs."
        ),
        "cta": (
            "syntharra.com — 14-day free pilot. See what you've been missing."
        ),
        "platform_notes": (
            "TikTok: 'THIS is happening' with a pointed finger or dramatic cut "
            "is a pattern that performs well. The competitor-awareness angle "
            "triggers loss aversion, which drives shares.\n"
            "Reels: Works well with B-roll of a busy competitor shop (stock "
            "footage of a bustling office or phone center). Contrast matters.\n"
            "Shorts: Can open with a mock phone ringing and going unanswered, "
            "then pivot to the competitor answering. Simple but effective."
        ),
        "visual_direction": (
            "Open on Dan pointing at camera or at a whiteboard with 'YOUR "
            "COMPETITOR' written on it. Cut to B-roll of a busy phone operation "
            "or a ringing phone being answered. Back to Dan for the solution. "
            "Close on URL card with urgency text: 'They already have this.'"
        ),
        "estimated_performance": (
            "Loss aversion is the most powerful motivator for small business "
            "owners. 'Your competitor is taking your customers' outperforms "
            "'you could gain X customers' in nearly every test. "
            "High comment engagement expected — this creates tribal reactions."
        ),
    },
    {
        "id": 6,
        "title": "The Math",
        "category": "education",
        "hook": (
            "One missed HVAC emergency call is worth more than you think. "
            "Let me show you the math."
        ),
        "problem": (
            "$350 service call. $89 a month maintenance plan if they sign. "
            "2-3 referrals over their lifetime. Now multiply that by 5 missed "
            "calls a month. That's not $1,750 lost — that's $30,000 or more "
            "over a year, if you factor in the downstream."
        ),
        "solution": (
            "Syntharra costs $697 a month. It answers every call you miss. "
            "You break even on month one if it catches just two after-hours "
            "emergencies. Every call after that is pure margin. "
            "HVAC owners who run the math don't go back to voicemail."
        ),
        "cta": (
            "Try Syntharra free for 14 days. No card. syntharra.com."
        ),
        "platform_notes": (
            "TikTok: 'Let me show you the math' is a proven retention hook. "
            "Use text overlays for each number — viewers who pause to read stay "
            "longer. This format works even for viewers who mute.\n"
            "Reels: Calculator aesthetic (literal or illustrated) performs well "
            "as a recurring visual motif for finance/ROI content.\n"
            "Shorts: Keep the math on screen as overlaid text throughout. "
            "YouTube viewers are more likely to screenshot useful data."
        ),
        "visual_direction": (
            "Dan at a whiteboard or desk, writing numbers as he talks. "
            "Text overlays for each figure: $350 / $89 / referrals / 5 calls. "
            "Simple running total animation or hand-written tally. "
            "End with '$697/mo Syntharra' vs the loss number side by side."
        ),
        "estimated_performance": (
            "ROI content has the highest save rate of any format in B2B social. "
            "HVAC owner-operators respond to concrete numbers — they think in "
            "margins already. This script will drive traffic from people who "
            "screenshot the math and share it with their business partners."
        ),
    },
    {
        "id": 7,
        "title": "Objection Flip",
        "category": "education",
        "hook": (
            "'I don't need an AI — I have voicemail.' I've heard this 100 times. "
            "Here's what the data says."
        ),
        "problem": (
            "80% of callers who reach voicemail don't leave a message. "
            "They hang up and call someone else. Your voicemail isn't catching "
            "leads — it's redirecting them to your competition."
        ),
        "solution": (
            "Syntharra answers immediately, every time, and sounds like a real "
            "receptionist. It doesn't say 'please leave a message.' "
            "It says 'Let me get that booked for you.' "
            "The difference in conversion is not subtle. "
            "$697 a month. 14-day free pilot. Zero risk to find out."
        ),
        "cta": (
            "syntharra.com — try it free and measure the difference yourself."
        ),
        "platform_notes": (
            "TikTok: Opening with a common objection verbatim triggers "
            "recognition — HVAC owners think 'wait, that's what I said.' "
            "The pivot to data reframes the conversation without being preachy.\n"
            "Reels: Works well in a point-counterpoint format. Text on screen: "
            "MYTH vs REALITY. Simple, scannable, shareable.\n"
            "Shorts: The objection-then-flip structure creates natural replay "
            "behavior — viewers want to hear the data point again."
        ),
        "visual_direction": (
            "Dan to camera, casual, slightly amused tone on the objection. "
            "Pivot to serious/direct for the data. Optional: text card showing "
            "'80% hang up on voicemail' as a pull quote. "
            "Close: Dan relaxed, URL on screen, no urgency pressure."
        ),
        "estimated_performance": (
            "Objection-flip content targets people who are already aware of the "
            "problem but have rationalized not acting. This is the highest-value "
            "audience segment — close to purchase intent. "
            "Expected: high comment volume from people debating the stat."
        ),
    },
    {
        "id": 8,
        "title": "Real Call Demo",
        "category": "social_proof",
        "hook": (
            "Here's what actually happens when an HVAC emergency comes in at "
            "midnight — and you're asleep."
        ),
        "problem": (
            "The homeowner is sweating. Their AC is out. They need someone now. "
            "You're in bed. Your phone is on silent. They're about to call "
            "the next number in their list."
        ),
        "solution": (
            "Syntharra picks up on the first ring. Greets them with your "
            "company name. Gets the address, the issue, the urgency. Books the "
            "appointment or takes a message depending on your rules. "
            "Sends you a text summary while you sleep. You wake up to a "
            "booked emergency call. No missed job. $697 a month."
        ),
        "cta": (
            "Watch the full demo at syntharra.com. 14-day pilot, free to start."
        ),
        "platform_notes": (
            "TikTok: Demo content works best when the actual AI audio is in the "
            "video — show a real call (anonymized). The credibility of hearing "
            "the AI speak is far stronger than describing it.\n"
            "Reels: Split-screen works well: left panel shows the sleeping "
            "homeowner (or Dan asleep), right panel shows the AI handling the "
            "call in real time.\n"
            "Shorts: Walk through the exact call flow as a screen recording. "
            "Show each step: pickup, data collection, booking confirmation, "
            "text to Dan. Real product = real trust."
        ),
        "visual_direction": (
            "Open: Dark bedroom at midnight, phone screen glowing. "
            "Transition: screen-record of Syntharra receiving the call. "
            "Show the AI's responses in real time (or subtitled). "
            "Show the confirmation text hitting Dan's phone. "
            "Cut to Dan checking his phone in the morning — booked job waiting."
        ),
        "estimated_performance": (
            "Product demos convert better than any other format when the product "
            "is genuinely impressive. An AI that sounds human answering a real "
            "call at midnight is remarkable — people will share it just because "
            "it's surprising. This is the closest thing to a live sales demo "
            "at zero cost per view."
        ),
    },
    {
        "id": 9,
        "title": "Seasonal Urgency",
        "category": "pain_point",
        "hook": (
            "June hits. Your AC dies. 47 homeowners call HVAC shops in one night. "
            "You answer 3."
        ),
        "problem": (
            "Summer is your busiest season and your highest-miss-rate season. "
            "You can't physically be on the phone at 9pm when half your market "
            "discovers their AC quit after work. Every call you miss is a job "
            "your competitor books."
        ),
        "solution": (
            "Syntharra handles every overflow call during peak season. "
            "No additional staff. No answering service markups. "
            "$697 a month flat — whether you get 10 calls or 1,000. "
            "It knows HVAC, knows urgency, and books the job while "
            "your competition's voicemail fills up."
        ),
        "cta": (
            "Don't wait until June. syntharra.com — 14-day free pilot now."
        ),
        "platform_notes": (
            "TikTok: Post this in April/May for maximum algorithm timing. "
            "The specific number (47 homeowners) makes the scenario visceral. "
            "Urgency without a deadline creates anxiety that drives action.\n"
            "Reels: Works well as a countdown/urgency post. Text overlay: "
            "'Summer is 6 weeks away' drives the seasonal FOMO.\n"
            "Shorts: The opening stat (47 calls, answer 3) is designed to be "
            "screenshot-worthy. Put it as large text on the first frame."
        ),
        "visual_direction": (
            "Open: Stock B-roll of a hot summer day — thermometer, sun, "
            "air conditioner unit. Cut to Dan speaking to camera. "
            "Text overlay: '47 calls. You answered 3.' "
            "Mid-roll: phone call montage — ring, ring, ring, voicemail. "
            "Close: Syntharra answering all of them. Calm resolution."
        ),
        "estimated_performance": (
            "Seasonal urgency works because it's both relevant and time-limited. "
            "HVAC owners think in seasons — summer is their make-or-break period. "
            "This script taps peak anxiety 4-6 weeks before the season, when "
            "buying decisions are still being made. Highest purchase-intent timing."
        ),
    },
    {
        "id": 10,
        "title": "Pilot Offer",
        "category": "pain_point",
        "hook": (
            "14 days. Zero dollars. If it doesn't pay for itself, you walk away. "
            "Why wouldn't you try it?"
        ),
        "problem": (
            "Most HVAC owners who don't try new tools aren't skeptical of the "
            "tool — they're skeptical of the risk. Switching costs. Setup pain. "
            "What if it doesn't work. I get it."
        ),
        "solution": (
            "So we made the pilot zero-risk. No credit card for 14 days. "
            "We set it up for you — one phone number forward, done in 20 minutes. "
            "If in 14 days Syntharra hasn't answered calls you would have missed "
            "and booked at least one job you wouldn't have gotten, "
            "you cancel, you pay nothing, no hard feelings."
        ),
        "cta": (
            "syntharra.com — start your free pilot today. Takes 20 minutes to set up."
        ),
        "platform_notes": (
            "TikTok: The opening rhetorical question ('Why wouldn't you try it?') "
            "works because it challenges inaction directly. Pair with a direct, "
            "slightly frustrated tone — not aggressive, just honest.\n"
            "Reels: This script works as a text-over-talking-head with each "
            "objection rebuttal on screen. Visual list format increases saves.\n"
            "Shorts: End card with a pinned URL and '20 min setup' — "
            "low time commitment is a powerful CTA amplifier on Shorts."
        ),
        "visual_direction": (
            "Dan at his desk, relaxed, speaking directly to camera. "
            "Tone: 'I understand the hesitation, and I've removed every barrier.' "
            "Optional: show the literal setup steps (3-step graphic: "
            "sign up → forward number → done). "
            "Close: Dan smiling, URL on screen, no urgency pressure — "
            "confidence in the offer sells it."
        ),
        "estimated_performance": (
            "Pure offer content converts best when trust is already established "
            "(watch this after scripts 1-8 have run). The zero-friction "
            "framing ('why wouldn't you try it') uses rhetorical reversal — "
            "it shifts the burden of proof to inaction. "
            "Expected: high click-through rate, lower share rate than story scripts."
        ),
    },
]

WEEK_MAP: dict[int, list[int]] = {
    1: [1, 2, 3],
    2: [4, 5, 6],
    3: [7, 8, 9, 10],
}

# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

DIVIDER = "=" * 72


def render_text(script: dict, index: int, total: int) -> str:
    lines = [
        DIVIDER,
        f"SCRIPT {script['id']} of {total}: {script['title'].upper()}",
        f"Category: {script['category']}",
        DIVIDER,
        "",
        f"[HOOK — 0:00-0:03]",
        script["hook"],
        "",
        f"[PROBLEM — 0:03-0:08]",
        script["problem"],
        "",
        f"[SOLUTION — 0:08-0:18]",
        script["solution"],
        "",
        f"[CTA — 0:18-0:23]",
        script["cta"],
        "",
        "--- Platform Notes ---",
        script["platform_notes"],
        "",
        "--- Visual Direction ---",
        script["visual_direction"],
        "",
        "--- Why This Hook Works ---",
        script["estimated_performance"],
        "",
    ]
    return "\n".join(lines)


def render_slack(scripts: list[dict]) -> str:
    """Format for posting to Slack — concise summary per script."""
    lines = [
        f"*Syntharra Short-Form Script Pack* — {len(scripts)} script(s)",
        "",
    ]
    for s in scripts:
        lines.append(f"*Script {s['id']}: {s['title']}* `{s['category']}`")
        lines.append(f"> *Hook:* {s['hook']}")
        lines.append(f"> *CTA:* {s['cta']}")
        lines.append("")
    lines.append("Run `python tools/short_form_content.py --script N` for full details.")
    return "\n".join(lines)


def render_json(scripts: list[dict]) -> str:
    return json.dumps(scripts, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Syntharra short-form video script generator for HVAC owner audiences.",
    )
    group = ap.add_mutually_exclusive_group()
    group.add_argument(
        "--script",
        type=int,
        metavar="N",
        choices=range(1, 11),
        help="Print a single script (1-10).",
    )
    group.add_argument(
        "--week",
        type=int,
        metavar="W",
        choices=[1, 2, 3],
        help="Print scripts for a posting week (1=scripts 1-3, 2=scripts 4-6, 3=scripts 7-10).",
    )
    ap.add_argument(
        "--output",
        choices=("text", "slack", "json"),
        default="text",
        help="Output format (default: text).",
    )
    return ap


def main() -> None:
    ap = build_parser()
    args = ap.parse_args()

    # Determine which scripts to render
    if args.script is not None:
        selected = [s for s in SCRIPTS if s["id"] == args.script]
    elif args.week is not None:
        ids = WEEK_MAP[args.week]
        selected = [s for s in SCRIPTS if s["id"] in ids]
    else:
        selected = SCRIPTS

    if not selected:
        sys.exit("No scripts matched your filter.")

    # Render
    if args.output == "json":
        print(render_json(selected))
    elif args.output == "slack":
        print(render_slack(selected))
    else:
        total = len(SCRIPTS)
        for i, script in enumerate(selected):
            print(render_text(script, i + 1, total))


if __name__ == "__main__":
    main()
