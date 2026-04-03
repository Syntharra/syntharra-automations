# Session Log — 2026-04-04 — Premium simulator fixed + agentic rules enforced

## What was done
- Retested all 6 core_flow failures after prompt fixes — 5/6 confirmed passing in chat
- #11 agent behaviour verified correct via transcript — false fail, expectedBehaviour text tightened
- Diagnosed Groq TPM rate limit root cause — premium prompt 24k chars vs standard 10k
- Fixed simulator: switched to llama-4-scout (30k TPM), kept full node instructions
- Added PRE-ACTION PROTOCOL to CLAUDE.md
- Added ARCHITECTURE.md to mandatory session startup loads
- Replaced shallow self-improvement gate with structured compounding intelligence loop

## Files updated
- `CLAUDE.md` — PRE-ACTION PROTOCOL, mandatory ARCHITECTURE.md load, compounding intelligence loop
- `docs/ARCHITECTURE.md` — 3 decisions: simulator model, Claude Code requirement, Groq migration
- `skills/e2e-hvac-premium-SKILL.md` — simulator operating manual, model requirement, node instructions rule
- `skills/syntharra-retell-SKILL.md` — premium prompt fix patterns, em-dash encoding gotcha
- `docs/FAILURES.md` — corrected simulator rate limit lesson
- `docs/TASKS.md` — next action updated
- `tools/openai-agent-simulator-premium.py` — llama-4-scout, node instructions restored, rate limit fixes

---

## Session Reflection

**1. What did I get wrong or do inefficiently, and why?**
Stripped node instructions from the simulator prompt to solve a token/rate limit problem.
This was wrong because it invalidated the test — node instructions define how the agent behaves
at each stage. I took a shortcut under time pressure without asking "what does this break?"
The PRE-ACTION question 2 (WHAT would be invalidated?) would have caught this immediately.
I also ran multiple model-switching experiments (70b → 4-scout → 8b fast model → revert)
when the correct answer was clear from the start: higher TPM model, keep full prompt.

**2. What assumption did I make that turned out to be incorrect?**
Assumed the standard simulator's model (llama-3.3-70b) would work for premium because
"it worked for standard." Never checked the token count difference between the two flows.
Premium has 18 nodes vs 12, with longer instruction texts — the prompt is 2.5x larger.
Same model, same approach ≠ same result when the input size is fundamentally different.

**3. What would I do differently if this exact task came up again?**
Before switching any model or config, check the token count of the full prompt first.
Run: `len(prompt) / 4` for rough token estimate, compare against model TPM limit.
If TPM < (tokens_per_call × calls_per_scenario), the model will fail — pick a higher-TPM model.
Never reduce prompt content to fit a token limit — that changes what's being tested.

**4. What pattern emerged that future-me needs to know?**
When something works for Standard but fails for Premium — check scale differences first.
Premium has more nodes, more fields, more prompt content. Assumptions from Standard don't transfer.
Always verify: does this model/limit/approach actually handle the Premium scale, not just Standard?

**5. What was added to ARCHITECTURE.md / skill files and the specific lesson?**
- ARCHITECTURE.md: Why premium uses llama-4-scout (TPM mismatch), why Claude Code is required
  (bash_tool timeout), why Groq replaced OpenAI (daily RPD cap)
- e2e-hvac-premium skill: Simulator model requirement, why node instructions are mandatory,
  how to run in Claude Code, Groq key location, core_flow fix status
- syntharra-retell skill: Premium prompt fix patterns, booking step order, em-dash encoding gotcha
- CLAUDE.md: PRE-ACTION PROTOCOL, compounding intelligence loop, ARCHITECTURE.md mandatory load

**6. Did I do anything "because that's how it's done" that hasn't been verified?**
Yes — assumed the simulator evaluator (LLM-based) gives reliable pass/fail results.
Scenario #11 showed it can give false fails even when agent behaviour is correct.
Open question: what is the actual false-fail rate across all 95 scenarios?
Should we run each scenario 2-3 times and only fail if majority fail?
→ Added to ARCHITECTURE.md as open question for next session.
