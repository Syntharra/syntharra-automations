#!/usr/bin/env python3
"""
social_poster.py — Post Syntharra content to Reddit and LinkedIn.

Handles actual API posting with graceful fallback: if credentials are not yet
vaulted, the tool posts the draft content to Slack instead of crashing.
Rate limits are enforced via Supabase (marketing_campaigns table).

Platforms:
  Reddit  — OAuth2 client credentials flow, text (self) posts.
             Target subreddits: r/HVAC, r/hvacadvice, r/Contractor, r/smallbusiness
             Rate limit: 1 post per subreddit per 7 days.
  LinkedIn — REST API v2 ugcPosts, PUBLIC visibility.
             Rate limit: 1 post per day.

Fallback: If credentials are missing from vault, the tool sends the content
          to Slack (#content-ops) with a manual copy-paste note — so the tool
          is always useful, even before credentials are wired up.

Usage:
    source .env.local
    python tools/social_poster.py --platform reddit --subreddit HVAC --content "text"
    python tools/social_poster.py --platform linkedin --content "text"
    python tools/social_poster.py --platform all --content-file leads/this_week_posts.json
    python tools/social_poster.py --dry-run --platform reddit --subreddit HVAC --content "x"

Required env vars (from .env.local):
    SUPABASE_URL          https://hgheyqwnrcvwtgngqdnq.supabase.co
    SUPABASE_SERVICE_KEY  service_role JWT
    SLACK_BOT_TOKEN       for fallback posting (optional but strongly recommended)

Vault credentials looked up automatically:
    Reddit:   service_name='Reddit'   key_type in [client_id, client_secret, username, password]
    LinkedIn: service_name='LinkedIn' key_type in [access_token, person_urn]

Cost: $0 per run (API calls are free on Reddit/LinkedIn free tiers).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REDDIT_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
REDDIT_SUBMIT_URL = "https://oauth.reddit.com/api/submit"
REDDIT_USER_AGENT = "Syntharra:social_poster:v1.0 (by /u/syntharra_hvac)"
REDDIT_RATE_LIMIT_DAYS = 7

LINKEDIN_POST_URL = "https://api.linkedin.com/v2/ugcPosts"
LINKEDIN_RATE_LIMIT_HOURS = 24

SLACK_CHANNEL_FALLBACK = "#content-ops"
SLACK_POST_URL = "https://slack.com/api/chat.postMessage"

SUPABASE_CAMPAIGNS_TABLE = "marketing_campaigns"

# ---------------------------------------------------------------------------
# HTTP helper (stdlib only — no requests)
# ---------------------------------------------------------------------------


def http_request(
    method: str,
    url: str,
    headers: dict,
    body=None,
    form_data: dict | None = None,
    timeout: int = 30,
) -> tuple[int, object]:
    """
    Make an HTTP request. Body can be a dict (JSON-encoded) or bytes.
    form_data, if set, is URL-encoded and overrides body.
    Returns (status_code, parsed_response).
    """
    if form_data is not None:
        data = urllib.parse.urlencode(form_data).encode("utf-8")
        headers = {**headers, "Content-Type": "application/x-www-form-urlencoded"}
    elif body is not None:
        data = json.dumps(body).encode("utf-8") if not isinstance(body, bytes) else body
        if "Content-Type" not in headers:
            headers = {**headers, "Content-Type": "application/json; charset=utf-8"}
    else:
        data = None

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            status = resp.status
            parsed = json.loads(raw) if raw.strip() else {}
            return status, parsed
    except urllib.error.HTTPError as exc:
        try:
            err_body = exc.read().decode("utf-8")[:800]
        except Exception:
            err_body = "(unreadable)"
        return exc.code, {"error": err_body}
    except urllib.error.URLError as exc:
        return 0, {"error": f"URLError: {exc}"}


# ---------------------------------------------------------------------------
# Env / Supabase helpers
# ---------------------------------------------------------------------------


def _env(name: str, required: bool = True) -> str:
    v = os.environ.get(name, "").strip()
    if required and not v:
        sys.exit(
            f"Missing env var: {name}\n"
            "Run: source .env.local   (or ask Dan for the .env.local file)"
        )
    return v


def _sb_headers() -> dict:
    key = _env("SUPABASE_SERVICE_KEY")
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def _sb_url(path: str) -> str:
    return _env("SUPABASE_URL").rstrip("/") + path


# ---------------------------------------------------------------------------
# Vault lookup
# ---------------------------------------------------------------------------


def vault_get(service_name: str, key_type: str) -> str | None:
    """
    Fetch a single credential from syntharra_vault.
    Returns None (never raises) if not found or on any HTTP error.
    """
    try:
        qs = urllib.parse.urlencode({
            "service_name": f"eq.{service_name}",
            "key_type": f"eq.{key_type}",
            "select": "key_value",
            "limit": "1",
        })
        url = _sb_url(f"/rest/v1/syntharra_vault?{qs}")
        status, data = http_request("GET", url, _sb_headers())
        if status == 200 and isinstance(data, list) and data:
            return data[0].get("key_value") or None
    except Exception:
        pass
    return None


def vault_require(service_name: str, key_type: str) -> str | None:
    """Like vault_get but prints a warning when missing."""
    val = vault_get(service_name, key_type)
    if val is None:
        print(
            f"[warn] vault missing: service='{service_name}' key_type='{key_type}'",
            file=sys.stderr,
        )
    return val


# ---------------------------------------------------------------------------
# Rate limit enforcement (Supabase marketing_campaigns table)
# ---------------------------------------------------------------------------


def check_rate_limit(platform: str, target: str, sb_key: str) -> bool:
    """
    Return True if it is safe to post (within rate limit), False if blocked.

    Checks marketing_campaigns for a row where:
        platform = <platform>
        target   = <target>       (e.g. 'HVAC' for subreddit, 'company_page' for LI)
        status   = 'posted'
        posted_at >= now() - rate_limit_window

    The sb_key param is accepted for signature compatibility but the function
    uses env vars directly — consistent with the rest of this codebase.
    """
    if platform == "reddit":
        window_start = datetime.now(tz=timezone.utc) - timedelta(days=REDDIT_RATE_LIMIT_DAYS)
        window_label = f"{REDDIT_RATE_LIMIT_DAYS}d"
    elif platform == "linkedin":
        window_start = datetime.now(tz=timezone.utc) - timedelta(hours=LINKEDIN_RATE_LIMIT_HOURS)
        window_label = f"{LINKEDIN_RATE_LIMIT_HOURS}h"
    else:
        # Unknown platform — allow posting (no rule defined)
        return True

    since_iso = window_start.isoformat()
    try:
        qs = urllib.parse.urlencode({
            "platform": f"eq.{platform}",
            "target": f"eq.{target}",
            "status": "eq.posted",
            "posted_at": f"gte.{since_iso}",
            "select": "id",
            "limit": "1",
        })
        url = _sb_url(f"/rest/v1/{SUPABASE_CAMPAIGNS_TABLE}?{qs}")
        status, data = http_request("GET", url, _sb_headers())
        if status == 200 and isinstance(data, list) and data:
            print(
                f"[rate-limit] {platform}/{target} was posted within the last "
                f"{window_label}. Skipping.",
                file=sys.stderr,
            )
            return False
    except Exception as exc:
        # If the table doesn't exist yet or query fails, log and allow.
        print(
            f"[warn] rate-limit check failed for {platform}/{target}: {exc}. "
            "Allowing post (table may not exist yet).",
            file=sys.stderr,
        )
    return True


def record_post(platform: str, target: str, post_url: str | None, content_preview: str) -> None:
    """
    Insert a row into marketing_campaigns to record the post.
    Non-fatal — logs a warning on failure.
    """
    now = datetime.now(tz=timezone.utc).isoformat()
    payload = {
        "platform": platform,
        "target": target,
        "status": "posted",
        "posted_at": now,
        "post_url": post_url or "",
        "content_preview": content_preview[:500],
    }
    try:
        url = _sb_url(f"/rest/v1/{SUPABASE_CAMPAIGNS_TABLE}")
        status, data = http_request("POST", url, {**_sb_headers(), "Prefer": "return=minimal"}, body=payload)
        if status not in (200, 201):
            print(f"[warn] failed to record post in Supabase: {status} {data}", file=sys.stderr)
    except Exception as exc:
        print(f"[warn] record_post exception: {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Slack fallback
# ---------------------------------------------------------------------------


def fallback_to_slack(platform: str, content: str, slack_token: str | None = None) -> None:
    """
    When credentials for <platform> are not yet set up, post the content draft
    to Slack (#content-ops) so Dan can copy-paste it manually.

    Never raises — this is a best-effort notification, not a critical path.
    """
    token = slack_token or os.environ.get("SLACK_BOT_TOKEN", "").strip()
    note = (
        f":warning: *{platform.title()} credentials not yet vaulted* — "
        f"here's the post draft for manual copy-paste:\n\n"
        f"```{content[:3000]}```\n\n"
        f"_To enable auto-posting: vault the credentials using "
        f"`python tools/vault_secret.py` — see credential setup notes below._"
    )

    if not token:
        # Last resort: just print to stdout so it's never silently dropped
        print(f"\n{'='*60}")
        print(f"FALLBACK (no Slack token) — {platform.upper()} draft:")
        print(f"{'='*60}")
        print(content)
        print(f"{'='*60}\n")
        print("[info] Set SLACK_BOT_TOKEN in .env.local to enable Slack fallback.", file=sys.stderr)
        return

    body = {
        "channel": SLACK_CHANNEL_FALLBACK,
        "text": note,
    }
    status, data = http_request(
        "POST",
        SLACK_POST_URL,
        {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        body=body,
    )
    if status == 200 and isinstance(data, dict) and data.get("ok"):
        print(f"[fallback] Draft posted to Slack {SLACK_CHANNEL_FALLBACK} (credentials not vaulted).")
    else:
        # Even Slack failed — dump to stdout as last resort
        print(f"[fallback] Slack post failed ({status}). Printing draft to stdout:\n", file=sys.stderr)
        print(content)


# ---------------------------------------------------------------------------
# Reddit
# ---------------------------------------------------------------------------


def _reddit_get_token(client_id: str, client_secret: str, username: str, password: str) -> str | None:
    """
    Obtain a Reddit OAuth2 access token using password grant (script apps).
    Returns the token string, or None on failure.
    """
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    status, data = http_request(
        "POST",
        REDDIT_TOKEN_URL,
        {
            "Authorization": f"Basic {credentials}",
            "User-Agent": REDDIT_USER_AGENT,
        },
        form_data={
            "grant_type": "password",
            "username": username,
            "password": password,
        },
    )
    if status != 200 or not isinstance(data, dict):
        print(f"[reddit] token fetch failed: {status} {data}", file=sys.stderr)
        return None
    token = data.get("access_token")
    if not token:
        print(f"[reddit] no access_token in response: {data}", file=sys.stderr)
    return token


def post_to_reddit(
    subreddit: str,
    title: str,
    body: str,
    vault_sb_key: str,  # accepted for API compat; not used directly (we use env)
) -> dict:
    """
    Submit a self (text) post to a subreddit.

    Returns a result dict with keys:
        success (bool), platform, target, post_url (str|None), error (str|None)

    Gracefully falls back to Slack if credentials are missing.
    """
    result: dict = {
        "success": False,
        "platform": "reddit",
        "target": subreddit,
        "post_url": None,
        "error": None,
    }

    # Fetch credentials
    client_id = vault_require("Reddit", "client_id")
    client_secret = vault_require("Reddit", "client_secret")
    username = vault_require("Reddit", "username")
    password = vault_require("Reddit", "password")

    if not all([client_id, client_secret, username, password]):
        fallback_to_slack("Reddit", f"r/{subreddit}\n\nTitle: {title}\n\n{body}")
        result["error"] = "credentials_missing"
        return result

    # Rate limit check
    if not check_rate_limit("reddit", subreddit, vault_sb_key):
        result["error"] = "rate_limited"
        return result

    # Authenticate
    token = _reddit_get_token(client_id, client_secret, username, password)
    if not token:
        fallback_to_slack("Reddit", f"r/{subreddit}\n\nTitle: {title}\n\n{body}")
        result["error"] = "auth_failed"
        return result

    # Submit post
    status, data = http_request(
        "POST",
        REDDIT_SUBMIT_URL,
        {
            "Authorization": f"bearer {token}",
            "User-Agent": REDDIT_USER_AGENT,
        },
        form_data={
            "sr": subreddit,
            "kind": "self",
            "title": title,
            "text": body,
            "nsfw": "false",
            "spoiler": "false",
            "resubmit": "true",
        },
    )

    if status != 200:
        error_msg = f"HTTP {status}: {data}"
        print(f"[reddit] submit failed: {error_msg}", file=sys.stderr)

        # Check for flair-required error and fall back gracefully
        if isinstance(data, dict):
            errors = str(data.get("error", "") or data.get("json", {}).get("errors", ""))
            if "FLAIR_REQUIRED" in errors.upper() or "flair" in errors.lower():
                print(
                    f"[reddit] r/{subreddit} requires post flair. "
                    "Falling back to Slack draft — add flair manually.",
                    file=sys.stderr,
                )
                fallback_to_slack(
                    "Reddit",
                    f"r/{subreddit} requires flair. Post manually:\n\n"
                    f"Title: {title}\n\n{body}",
                )
                result["error"] = "flair_required"
                return result

        result["error"] = error_msg
        return result

    # Parse Reddit's response structure
    try:
        json_data = data.get("json", {})
        errors = json_data.get("errors", [])
        if errors:
            result["error"] = str(errors)
            print(f"[reddit] API errors: {errors}", file=sys.stderr)
            return result

        post_url = json_data.get("data", {}).get("url") or None
    except Exception as exc:
        result["error"] = f"parse_error: {exc}"
        return result

    result["success"] = True
    result["post_url"] = post_url
    print(f"[reddit] Posted to r/{subreddit}: {post_url}")
    record_post("reddit", subreddit, post_url, f"{title}\n{body[:200]}")
    return result


# ---------------------------------------------------------------------------
# LinkedIn
# ---------------------------------------------------------------------------


def post_to_linkedin(
    body: str,
    vault_sb_key: str,  # accepted for API compat
) -> dict:
    """
    Publish a PUBLIC text post to the authenticated LinkedIn member's feed.

    Returns a result dict with keys:
        success (bool), platform, target, post_url (str|None), error (str|None)

    Gracefully falls back to Slack if credentials are missing.
    """
    result: dict = {
        "success": False,
        "platform": "linkedin",
        "target": "linkedin_feed",
        "post_url": None,
        "error": None,
    }

    # Fetch credentials
    access_token = vault_require("LinkedIn", "access_token")
    person_urn = vault_require("LinkedIn", "person_urn")

    if not access_token or not person_urn:
        fallback_to_slack("LinkedIn", body)
        result["error"] = "credentials_missing"
        return result

    # Rate limit check
    if not check_rate_limit("linkedin", "linkedin_feed", vault_sb_key):
        result["error"] = "rate_limited"
        return result

    # Build ugcPost payload
    # LinkedIn API v2 ugcPosts: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api
    payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": body,
                },
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC",
        },
    }

    status, data = http_request(
        "POST",
        LINKEDIN_POST_URL,
        {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202304",
        },
        body=payload,
    )

    if status not in (200, 201):
        error_msg = f"HTTP {status}: {data}"
        print(f"[linkedin] post failed: {error_msg}", file=sys.stderr)
        if status == 401:
            print(
                "[linkedin] 401 Unauthorized — access token may be expired. "
                "LinkedIn tokens last ~60 days. Re-vault a fresh token.",
                file=sys.stderr,
            )
            fallback_to_slack("LinkedIn (token expired)", body)
            result["error"] = "token_expired"
        else:
            result["error"] = error_msg
        return result

    # LinkedIn returns the post URN in the response headers or body id field
    post_id = data.get("id") if isinstance(data, dict) else None
    post_url = f"https://www.linkedin.com/feed/update/{post_id}" if post_id else None

    result["success"] = True
    result["post_url"] = post_url
    print(f"[linkedin] Posted successfully. ID: {post_id}")
    record_post("linkedin", "linkedin_feed", post_url, body[:200])
    return result


# ---------------------------------------------------------------------------
# Content file loader
# ---------------------------------------------------------------------------


def load_content_file(path: str) -> list[dict]:
    """
    Load a JSON file of posts. Expected format:
        [
          {"platform": "reddit", "subreddit": "HVAC", "title": "...", "body": "..."},
          {"platform": "linkedin", "body": "..."},
          ...
        ]
    Returns a list of post dicts.
    """
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
        sys.exit(f"content-file must be a JSON array or object, got: {type(data)}")
    except FileNotFoundError:
        sys.exit(f"content-file not found: {path}")
    except json.JSONDecodeError as exc:
        sys.exit(f"content-file is not valid JSON: {exc}")


# ---------------------------------------------------------------------------
# Dry run renderer
# ---------------------------------------------------------------------------


def dry_run_output(platform: str, subreddit: str | None, content: str, title: str | None) -> None:
    print(f"\n{'='*60}")
    print(f"DRY RUN — would post to: {platform.upper()}")
    if subreddit:
        print(f"Subreddit: r/{subreddit}")
    if title:
        print(f"Title: {title}")
    print(f"\nContent ({len(content)} chars):")
    print("-" * 40)
    print(content)
    print("=" * 60)
    print("\n[dry-run] No actual post made. Remove --dry-run to post for real.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=(
            "Post Syntharra content to Reddit and/or LinkedIn. "
            "Falls back to Slack if credentials are not yet vaulted."
        )
    )
    ap.add_argument(
        "--platform",
        choices=("reddit", "linkedin", "all"),
        required=True,
        help="Target platform.",
    )
    ap.add_argument(
        "--subreddit",
        help="Subreddit name (no r/ prefix) — required for reddit platform.",
    )
    ap.add_argument(
        "--title",
        help=(
            "Post title for Reddit. If omitted, the first line of --content "
            "is used as the title."
        ),
    )
    ap.add_argument(
        "--content",
        help="Post body text (use quotes). Mutually exclusive with --content-file.",
    )
    ap.add_argument(
        "--content-file",
        metavar="PATH",
        help="JSON file of posts to publish. See docs for format.",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be posted without making any API calls.",
    )
    return ap


def _resolve_title_body(args_title: str | None, content: str) -> tuple[str, str]:
    """
    If a title is provided, use it. Otherwise split the first line of content
    as the title and the rest as the body.
    """
    if args_title:
        return args_title, content
    lines = content.split("\n", 1)
    title = lines[0].strip()[:300]
    body = lines[1].strip() if len(lines) > 1 else content
    return title, body


def main() -> None:
    ap = build_parser()
    args = ap.parse_args()

    # Validate content source
    if args.content and args.content_file:
        ap.error("Use --content OR --content-file, not both.")
    if not args.content and not args.content_file:
        ap.error("One of --content or --content-file is required.")

    # Supabase key stub (env-based internally, param accepted for API compat)
    sb_key = os.environ.get("SUPABASE_SERVICE_KEY", "")

    # Content file mode
    if args.content_file:
        posts = load_content_file(args.content_file)
        results = []
        for post in posts:
            plat = post.get("platform", "").lower()
            body_text = post.get("body") or post.get("content") or ""
            if not body_text:
                print(f"[warn] skipping post with no body: {post}", file=sys.stderr)
                continue

            if plat == "reddit":
                sub = post.get("subreddit", "")
                if not sub:
                    print(f"[warn] reddit post missing subreddit: {post}", file=sys.stderr)
                    continue
                t, b = _resolve_title_body(post.get("title"), body_text)
                if args.dry_run:
                    dry_run_output("reddit", sub, b, t)
                else:
                    results.append(post_to_reddit(sub, t, b, sb_key))

            elif plat == "linkedin":
                if args.dry_run:
                    dry_run_output("linkedin", None, body_text, None)
                else:
                    results.append(post_to_linkedin(body_text, sb_key))
            else:
                print(f"[warn] unknown platform in content-file: '{plat}'", file=sys.stderr)

        if not args.dry_run:
            print(json.dumps(results, indent=2))
        return

    # Single-post mode
    content = args.content or ""
    platform = args.platform

    if platform in ("reddit", "all"):
        if not args.subreddit:
            ap.error("--subreddit is required when posting to Reddit.")
        title, body = _resolve_title_body(args.title, content)
        if args.dry_run:
            dry_run_output("reddit", args.subreddit, body, title)
        else:
            result = post_to_reddit(args.subreddit, title, body, sb_key)
            print(json.dumps(result, indent=2))

    if platform in ("linkedin", "all"):
        if args.dry_run:
            dry_run_output("linkedin", None, content, None)
        else:
            result = post_to_linkedin(content, sb_key)
            print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
