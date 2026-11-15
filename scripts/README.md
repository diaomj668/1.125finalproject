# Evaluation

From the repository root, run `python scripts/evaluate.py`.

This reruns the 20 requests in `tests/scenarios.json` using the local planner. It overwrites `evidence/evaluation.json` and `evidence/scenario_plans.json` with the new results. It does not call a paid API.
