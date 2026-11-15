# Saved midpoint run

`evaluation.json` has the summary and all 20 expected/actual outcomes.

`scenario_plans.json` has the input, retrieved records, first draft, checks, revision and final result for each scenario.

These files were produced by `python scripts/evaluate.py` on November 13, 2026. The run used the local planner and made no real Claude API calls. Rerunning the script replaces the evidence with a fresh run.

`claude_live.json` is created only when `python scripts/verify_claude.py --run` is used with a configured key. Its contents distinguish a failed attempt from completed live cases. If the file is absent, no live API evidence has been saved.
