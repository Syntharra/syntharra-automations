# Session Start — Syntharra Automations

> **Single entry point for every Cowork session.** Read this top-to-bottom before doing anything else. ~3 minutes, ~5k tokens.

## 1. Read these 4 files in order (do not skip)

1. **`docs/STATE.md`** — current reality. Auto-maintained by `tools/session_end.py`. Source of truth for what's live, what's in flight, what's blocked.
2. **`docs/RULES.md`** — hard don'ts. Violations have burned us before.
3. **`docs/REFERENCE.md`** — every agent/flow/workflow ID. **Sole source.** Never inline IDs anywhere else.
4. **`docs/FAILURES.md`** — past incidents and fixes. Skim the last 10 rows. If your task touches any system listed there, read the full row.

Total: ~200 lines of canonical context. Everything else is on-demand.

## 2. Orient (30 seconds)

Run:
```
python tools/session_start.py
```

This prints:
- **Last session** from `INDEX.md` + ⚠️ ghost-session warning if commits happened after `session_end` wasn't run
- **Recent commits** (last 8) — the ground truth regardless of whether `session_end` was called
- **Last 3 failures** from `FAILURES.md`
- **In flight / blocked** from `STATE.md`
- **Next session priorities** from `STATE.md` — written by the previous `session_end --priorities`
- **Uncommitted files**

If the ghost-session warning fires, read the listed commits to reconstruct what was done. The commit log is always accurate; `INDEX.md` is only accurate if `session_end` was run.

## 3. Work rules

- **IDs come from `REFERENCE.md` only.** If you need an ID, read REFERENCE.md, don't recall it from memory.
- **Never touch live Retell agents.** Clone to TESTING, promote via `retell-iac/scripts/promote.py`. See RULES.md §1.
- **Per-client data lives in Supabase, not docs.** The `client_agents` table is the source for every client clone. Docs only carry MASTER templates. This is how we scale to 1000+ without doc bloat.
- **If GitHub MCP 403s, use Desktop Commander.** See RULES.md §4 and FAILURES.md 2026-04-07.

## 4. At session end (always)

```
python tools/session_end.py --topic <short-slug> --summary "<one-line>" [--priorities "- item 1\n- item 2"]
```

This:
- Refreshes STATE.md's header (last updated, last commit)
- Appends a row to `docs/session-logs/INDEX.md`
- Writes `--priorities` into STATE.md `## Next session — pick up here` (shown at next session start)
- Warns if you added a FAILURES row without a matching RULES update

**Always pass `--priorities`** with what the next session should pick up. This is the primary handoff mechanism — it shows up first thing next session. If the session produced a new standing rule, add it to RULES.md in the same commit.

## 5. Scale-to-1000 invariants

These are the rails that keep this repo sane as client count grows:

| What | Where it lives | Why |
|---|---|---|
| MASTER agent prompts/flows | `retell-agents/HVAC-{STANDARD,PREMIUM}-AGENT-TEMPLATE.md` | Single source for all clones |
| MASTER IDs | `docs/REFERENCE.md` | One file, ~100 lines, never grows per-client |
| Per-client clones | Supabase `client_agents` table | Unbounded without touching the repo |
| Client onboarding | n8n workflows `4Hx7aRdzMl5N0uJP` (Std), `kz1VmwNccunRMEaF` (Prem) | See REFERENCE.md |
| Session memory | `docs/session-logs/INDEX.md` (auto-maintained) | Chronological, append-only |
| Learnings | `docs/FAILURES.md` + `docs/RULES.md` | Every mistake becomes a rule |

If you find yourself writing a per-client file into the repo, **stop** — that belongs in Supabase.
