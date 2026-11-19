# Saved midpoint run

`evaluation.json` has the summary and all 20 expected/actual outcomes.

`scenario_plans.json` has the input, retrieved records, first draft, checks, revision and final result for each scenario.

These files were produced by `python scripts/evaluate.py`, most recently on November 18, 2026 (the run time is in `evaluation.json`). The first run was on November 13, 2026. All 20 outcomes matched in both runs. The run used the local planner and made no real Claude API calls. Rerunning the script replaces the evidence with a fresh run.

`claude_live.json` holds the most recent of three repeated live runs of the revised prompt, made on November 18, 2026 (Boston time). Each run used five calls and matched the expected outcome in all three cases. `live_runs/run1.json` to `run3.json` hold all three runs. The earlier live run, made with the previous prompt on November 16, 2026, is in git history (commit d8f3b15).
