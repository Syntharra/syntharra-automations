#!/usr/bin/env python3
"""
content_preview_mode.py — shared live/preview mode gate for content team agents.

Every agent in the autonomous content team (research_agent, content_writer,
publisher, marketing_brain video phase) imports from this module to decide
whether it should actually POST to platforms or just generate + store.

Until MARKETING_TEAM_ENABLED flips to 'true' (typically done in Railway env
vars after VSL + Stripe live + Telnyx creds land), the entire pipeline runs
in dry-run posture: content is generated, videos are rendered, rows are
written to content_queue, Slack previews are sent — but Blotato is never
actually called, and cold email is skipped entirely.

Usage:
    from content_preview_mode import is_live_mode, is_cold_email_enabled, preview_banner

    if is_live_mode():
        blotato_client.publish(payload)
    else:
        print("[PREVIEW] Would publish:", payload)

    slack_text = f"6 videos ready{preview_banner()}"

Environment flags:
    MARKETING_TEAM_ENABLED=true   -> live mode (actually posts to platforms)
    MARKETING_TEAM_ENABLED=false  -> preview mode (dry-run, default)
    COLD_EMAIL_ENABLED=true       -> cold email phase runs
    COLD_EMAIL_ENABLED=false      -> cold email phase skipped (default, per 2026-04-11)
"""

import os


def is_live_mode() -> bool:
    """True when the content team should actually post to platforms.

    Default is False (preview mode) to keep accidental posts impossible
    until Dan explicitly flips the flag in Railway env vars.
    """
    return os.environ.get("MARKETING_TEAM_ENABLED", "false").strip().lower() == "true"


def is_cold_email_enabled() -> bool:
    """True when marketing_brain.py should run its cold email phase.

    Currently paused per Dan's 2026-04-11 decision to focus on organic
    social content (see docs/STATE.md). Flip to true to resume cold email
    sequences without touching code.
    """
    return os.environ.get("COLD_EMAIL_ENABLED", "false").strip().lower() == "true"


def preview_banner() -> str:
    """Banner appended to Slack messages when running in preview mode.

    Returns empty string when live. Prefixed with two newlines so it can
    be appended to any message text without needing caller-side spacing.
    """
    if is_live_mode():
        return ""
    return (
        "\n\n*PREVIEW MODE* — content generated and stored but NOT posted. "
        "Flip `MARKETING_TEAM_ENABLED=true` in Railway env when VSL + Stripe live "
        "+ Telnyx creds are ready."
    )


if __name__ == "__main__":
    # Smoke test: print the current state + show both branches.
    print(f"is_live_mode(): {is_live_mode()}")
    print(f"is_cold_email_enabled(): {is_cold_email_enabled()}")
    print(f"preview_banner(): {preview_banner()!r}")
