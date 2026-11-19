# Saved midpoint run

`evaluation.json` has the summary and all 20 expected/actual outcomes.

`scenario_plans.json` has the input, retrieved records, first draft, checks, revision and final result for each scenario.

These files were produced by `python scripts/evaluate.py`, most recently on November 18, 2026 (the run time is in `evaluation.json`). The first run was on November 13, 2026. All 20 outcomes matched in both runs. The run used the local planner and made no real Claude API calls. Rerunning the script replaces the evidence with a fresh run.

`claude_live.json` was created by `python scripts/verify_claude.py --run` on November 16, 2026 (Boston time), with a configured key. It records three completed live cases: nine calls in total, and one case matching the expected outcome. Its contents distinguish a failed attempt from completed cases.
