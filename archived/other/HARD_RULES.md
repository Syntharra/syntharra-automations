# SYNTHARRA HARD RULES — NEVER VIOLATE

## RULE 1: Retell batch simulation testing
**NEVER run Retell batch simulation testing without Dan's EXPLICIT permission given THREE separate times.**
Reason: previous incident — Retell batch sim run unattended generated a massive surprise bill.
Applies to: any tool, script, agent, or workflow that triggers Retell call simulations in bulk.
If in doubt: do not run. Ask Dan. Wait for three confirmations.

## RULE 2: OpenAI scenario testing cost cap
Hard cap: **$5.00 per agent run, no exceptions.**
The tester (`tools/agentic-test-fix-v3.py`) clamps `--max-cost` to $5.00 even if a higher value is passed.
Never remove or raise the `HARD_CAP` constant without Dan's written approval.
