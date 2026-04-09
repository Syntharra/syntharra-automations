#!/usr/bin/env python3
"""
analyze_failures.py — Parse docs/FAILURES.md and report failure patterns by area.

Helps identify system hotspots and where to add proactive validation.

Usage:
    python tools/analyze_failures.py              # Full report, all areas
    python tools/analyze_failures.py --area n8n   # Filter to one area
    python tools/analyze_failures.py --json        # Machine-readable output
    python tools/analyze_failures.py --top 5       # Show top N areas only
"""
import argparse
import json
import pathlib
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAILURES = ROOT / "docs" / "FAILURES.md"

# Area keyword mapping — normalize common area strings to canonical names
AREA_MAP = {
    "n8n sdk": "n8n",
    "n8n onboarding": "n8n",
    "n8n standard onboarding": "n8n",
    "n8n premium onboarding": "n8n",
    "n8n raw rest put": "n8n",
    "n8n mcp": "n8n",
    "postgres alter batch": "supabase",
    "syntharra_vault upsert": "supabase",
    "rls audit": "supabase",
    "supabase vault wrong table": "supabase",
    "slack credential discovery": "n8n",
    "testing": "testing",
    "agent-testing": "testing",
    "email": "email",
    "github-mcp": "github-mcp",
    "github mcp": "github-mcp",
    "brevo api key": "credentials",
    "standard master auto-layout": "retell",
    "retell": "retell",
}


@dataclass
class Failure:
    date: str
    area: str
    symptom: str
    root_cause: str
    fix: str
    resolved: str = "?"
    rule: str = ""


def normalize_area(raw: str) -> str:
    lower = raw.lower().strip()
    for key, canonical in AREA_MAP.items():
        if key in lower:
            return canonical
    # Detect common keywords in the area string itself
    for keyword in ("retell", "n8n", "supabase", "stripe", "email", "slack", "twilio", "telnyx", "github"):
        if keyword in lower:
            return keyword
    return lower or "unknown"


def parse_table_rows(text: str) -> list[Failure]:
    """Parse pipe-delimited table rows (| date | area | symptom | ... |)."""
    failures = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 3:
            continue
        date = parts[0]
        # Skip header and separator rows
        if date.lower() in ("date", "---", "") or "---" in date:
            continue
        area_raw = parts[1] if len(parts) > 1 else "unknown"
        symptom = parts[2] if len(parts) > 2 else ""
        root_cause = parts[3] if len(parts) > 3 else ""
        fix = parts[4] if len(parts) > 4 else ""
        resolved = parts[5] if len(parts) > 5 else "?"
        if not date or not area_raw:
            continue
        failures.append(Failure(
            date=date.strip(),
            area=normalize_area(area_raw),
            symptom=symptom,
            root_cause=root_cause,
            fix=fix,
            resolved=resolved,
        ))
    return failures


def infer_area_from_text(title: str, body: str) -> str:
    """Infer area from section title and body text."""
    combined = (title + " " + body).lower()
    for keyword in ("retell", "n8n", "supabase", "stripe", "email", "slack",
                    "twilio", "telnyx", "github", "brevo", "credential", "testing"):
        if keyword in combined:
            return keyword
    return "general"


def parse_section_failures(text: str) -> list[Failure]:
    """Parse markdown section-style failures (## YYYY-MM-DD — title)."""
    failures = []
    pattern = re.compile(
        r"^## (\d{4}-\d{2}-\d{2}) — (.+?)$(.*?)(?=^## \d{4}|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for m in pattern.finditer(text):
        date = m.group(1)
        title = m.group(2).strip()
        body = m.group(3)

        area = infer_area_from_text(title, body)

        symptom_m = re.search(r"\*\*What failed:\*\*\s*(.+?)(?:\n|$)", body)
        symptom = symptom_m.group(1).strip() if symptom_m else title

        root_m = re.search(r"\*\*Root cause:\*\*\s*(.+?)(?:\n|$)", body)
        root_cause = root_m.group(1).strip() if root_m else ""

        fix_m = re.search(r"\*\*Fix:\*\*\s*(.+?)(?:\n|$)", body)
        fix = fix_m.group(1).strip() if fix_m else ""

        rule_m = re.search(r"\*\*Rule:\*\*\s*(.+?)(?:\n|$)", body)
        rule = rule_m.group(1).strip() if rule_m else ""

        resolved = "yes" if (fix and fix.lower() not in ("not yet fixed", "pending", "")) else "?"

        failures.append(Failure(
            date=date,
            area=area,
            symptom=symptom,
            root_cause=root_cause,
            fix=fix,
            resolved=resolved,
            rule=rule,
        ))
    return failures


def load_failures() -> list[Failure]:
    if not FAILURES.exists():
        print(f"ERROR: {FAILURES} not found", file=sys.stderr)
        sys.exit(1)
    text = FAILURES.read_text(encoding="utf-8")
    failures = parse_table_rows(text)
    failures += parse_section_failures(text)
    # Deduplicate by (date, symptom[:40]) — table rows and section rows can overlap
    seen = set()
    unique = []
    for f in failures:
        key = (f.date, f.symptom[:40].lower())
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return sorted(unique, key=lambda f: f.date)


def summarize(failures: list[Failure], filter_area: Optional[str] = None) -> dict:
    by_area: dict[str, list[Failure]] = defaultdict(list)
    for f in failures:
        by_area[f.area].append(f)

    if filter_area:
        needle = filter_area.lower()
        by_area = {k: v for k, v in by_area.items() if needle in k}

    areas = {}
    for area, fs in sorted(by_area.items(), key=lambda x: -len(x[1])):
        recent = sorted(fs, key=lambda f: f.date, reverse=True)[:3]
        areas[area] = {
            "count": len(fs),
            "unresolved": sum(1 for f in fs if f.resolved.lower() not in ("yes", "y", "true")),
            "recent": [
                {
                    "date": f.date,
                    "symptom": f.symptom,
                    "resolved": f.resolved,
                    "rule": f.rule,
                }
                for f in recent
            ],
        }

    return {
        "total": len(failures),
        "areas": areas,
        "hotspots": [
            {"area": area, "count": data["count"]}
            for area, data in areas.items()
            if data["count"] >= 3
        ],
    }


def print_report(summary: dict, top: Optional[int] = None):
    bar = "=" * 64
    print(bar)
    print(f"FAILURES ANALYSIS -- {summary['total']} total incidents")
    print(bar)

    areas = list(summary["areas"].items())
    if top:
        areas = areas[:top]

    for area, data in areas:
        unresolved = data["unresolved"]
        flag = f"  [{unresolved} unresolved]" if unresolved else ""
        print(f"\n[{area.upper()}] -- {data['count']} incident(s){flag}")
        for r in data["recent"]:
            resolved_icon = "[OK]" if r["resolved"].lower() in ("yes", "y", "true") else "[!] "
            symptom = r["symptom"][:72] + ("..." if len(r["symptom"]) > 72 else "")
            print(f"  {resolved_icon} {r['date']}: {symptom}")
            if r.get("rule"):
                rule_short = r["rule"][:64] + ("..." if len(r["rule"]) > 64 else "")
                print(f"       Rule: {rule_short}")

    print()
    if summary["hotspots"]:
        print("HOTSPOTS (3+ failures) -- consider adding pre-task validation:")
        for h in sorted(summary["hotspots"], key=lambda x: -x["count"]):
            print(f"  - {h['area']}: {h['count']} failures")
        print()
        print("  -> Add a validation step to the relevant skill file")
        print("  -> Add a GOTCHA entry to the domain skill")
        print("  -> Consider a pre-task safety check in tools/safety-checks.py")
    else:
        print("No hotspots detected (no area with 3+ failures).")

    print(bar)



def main():
    parser = argparse.ArgumentParser(
        description="Analyze Syntharra FAILURES.md for patterns and hotspots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--area", metavar="AREA",
                        help="Filter to a specific area (e.g. n8n, retell, supabase, email)")
    parser.add_argument("--json", dest="as_json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--top", type=int, metavar="N",
                        help="Show only the top N areas by failure count")
    args = parser.parse_args()

    failures = load_failures()
    if not failures:
        print("No failures found in FAILURES.md.")
        return 0

    summary = summarize(failures, filter_area=args.area)

    if args.as_json:
        print(json.dumps(summary, indent=2))
    else:
        print_report(summary, top=args.top)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
