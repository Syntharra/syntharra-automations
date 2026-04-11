#!/usr/bin/env python3
"""
Shared utility for all Syntharra hooks that need Claude.

Uses the Claude Code CLI (`claude -p`) rather than the Anthropic API directly —
no separate API key needed, uses your existing Claude Code subscription.

Usage in a hook:
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from hook_env import call_claude, append_rule, append_to_memory
"""
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent  # hooks/ -> .claude/ -> repo root


# ── Claude CLI path resolution ────────────────────────────────────────────────

# Known install locations for Windows (npm global install)
_CLAUDE_CANDIDATES = [
    r"C:\Users\danie\AppData\Roaming\npm\claude.cmd",
    r"C:\Users\danie\AppData\Roaming\npm\claude",
]


def _find_claude() -> str:
    """Return the full path to the claude CLI, or 'claude' to rely on PATH."""
    import shutil
    # Try PATH first
    on_path = shutil.which("claude")
    if on_path:
        return on_path
    # Fall back to known locations
    for candidate in _CLAUDE_CANDIDATES:
        if pathlib.Path(candidate).exists():
            return candidate
    return "claude"   # last resort — will fail loudly if missing


CLAUDE_BIN = _find_claude()


# ── Claude CLI call ───────────────────────────────────────────────────────────

def call_claude(prompt: str, tools: str = "Read,Write,Edit", timeout: int = 120) -> str:
    """
    Run Claude Code in non-interactive mode with the given prompt.
    Claude can read and write files directly — no API key needed.
    Returns stdout text, or "" on failure.

    Writes prompt to a temp file and pipes it via stdin to avoid Windows
    32KB command-line length limit when prompts are large.

    On Windows, .cmd files cannot be executed directly via subprocess list —
    must use ['cmd', '/c', CLAUDE_BIN, ...]. See Rule 40/49.
    """
    import platform, tempfile, os
    tmp = None
    try:
        # Write prompt to a temp file, then pipe it into claude via stdin
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write(prompt)
            tmp = f.name

        # Rule 40/49: on Windows, .cmd files need cmd /c — never shell=True (breaks stdin piping)
        claude_args = ["-p", "-", "--allowedTools", tools, "--output-format", "text"]
        if platform.system() == "Windows":
            cmd = ["cmd", "/c", CLAUDE_BIN] + claude_args
        else:
            cmd = [CLAUDE_BIN] + claude_args

        with open(tmp, "r", encoding="utf-8") as stdin_file:
            result = subprocess.run(
                cmd,
                stdin=stdin_file,
                capture_output=True,
                text=True,
                encoding="utf-8",   # Rule 41: never rely on Windows cp1252 default
                errors="replace",
                timeout=timeout,
                cwd=str(ROOT),
            )
        return result.stdout.strip()
    except FileNotFoundError:
        return ""
    except subprocess.TimeoutExpired:
        return ""
    except Exception:
        return ""
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def claude_available() -> bool:
    """Return True if the claude CLI can be found."""
    return pathlib.Path(CLAUDE_BIN).exists() or CLAUDE_BIN == "claude"


# ── RULES.md helpers ──────────────────────────────────────────────────────────

RULES_PATH = ROOT / "docs" / "RULES.md"


def next_rule_number() -> int:
    import re
    if not RULES_PATH.exists():
        return 1
    nums = [int(m) for m in re.findall(r"^## (\d+)\.", RULES_PATH.read_text(), re.MULTILINE)]
    return max(nums) + 1 if nums else 1


def append_rule(title: str, body: str, source: str = "auto-distilled") -> int:
    """Append a new numbered rule to RULES.md. Returns the rule number."""
    if not RULES_PATH.exists():
        return 0
    n = next_rule_number()
    block = f"\n## {n}. {title}\n\n{body.strip()}\n\n_Source: {source}_\n"
    with open(RULES_PATH, "a", encoding="utf-8") as f:
        f.write(block)
    return n


def rule_exists(text: str) -> bool:
    if not RULES_PATH.exists():
        return False
    return text[:40].lower() in RULES_PATH.read_text(encoding="utf-8").lower()


# ── Memory helpers ────────────────────────────────────────────────────────────

MEMORY_DIR = pathlib.Path(
    r"C:\Users\danie\.claude\projects"
    r"\c--Users-danie-Desktop-Syntharra-Cowork-Syntharra-Project-syntharra-automations"
    r"\memory"
)
ANTI_PATTERNS = MEMORY_DIR / "feedback_anti_patterns.md"


def append_to_memory(section: str, rule: str, why: str, how: str):
    """Append a structured rule entry to feedback_anti_patterns.md."""
    if not ANTI_PATTERNS.exists():
        return
    content = ANTI_PATTERNS.read_text(encoding="utf-8")
    if rule[:50].lower() in content.lower():
        return  # already there
    entry = f"\n**{rule}**\n**Why:** {why}\n**How to apply:** {how}\n"
    header = f"## {section}"
    if header in content:
        content = content.replace(header, header + "\n" + entry.strip(), 1)
    else:
        content = content.rstrip() + f"\n\n{header}\n\n{entry.strip()}\n"
    ANTI_PATTERNS.write_text(content, encoding="utf-8")
