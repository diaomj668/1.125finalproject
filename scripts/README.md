# Evaluation

From the repository root, run `python scripts/evaluate.py`.

This reruns the 20 requests in `tests/scenarios.json` using the local planner. It overwrites `evidence/evaluation.json` and `evidence/scenario_plans.json` with the new results. It does not call a paid API.

`configure_claude.py` asks for a key with hidden input and saves the local, ignored `.env` file. It makes no API calls.

`verify_claude.py` checks whether the local key is configured. Add `--run` to try three real requests, making at most nine paid calls. It writes `evidence/claude_live.json` only after a live attempt and stops on an API error. The key is never included in that report.
