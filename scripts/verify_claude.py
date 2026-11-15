"""Check local setup, then optionally save three real Claude trial runs."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from trip_planner.catalog import Catalog
from trip_planner.claude import ModelError
from trip_planner.config import DEFAULT_MODEL, load_settings
from trip_planner.planner import plan

CASE_IDS = ("saturday_closures", "saturday_free", "old_nature_records")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="Make up to nine paid API calls.")
    args = parser.parse_args()
    load_settings()
    ready = bool(os.getenv("ANTHROPIC_API_KEY", "").strip())
    print(json.dumps({"key_configured": ready,
                      "model": os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL),
                      "live_calls_requested": args.run}, indent=2))
    if not ready:
        print("Add a key with configure_claude.cmd or python scripts/configure_claude.py.")
        return 2
    if not args.run:
        print("No API calls made. Add --run to test the three saved demo requests.")
        return 0
    cases = json.loads((ROOT / "tests/scenarios.json").read_text(encoding="utf-8"))
    catalog = Catalog()
    report = {"run_at_utc": datetime.now(timezone.utc).isoformat(),
              "provider": "claude", "model": os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL),
              "scope": "Three live integration checks, not a full benchmark.",
              "max_calls": 9, "outcomes": []}
    for case_id in CASE_IDS:
        case = next(c for c in cases if c["id"] == case_id)
        started = time.monotonic()
        try:
            output = plan(case["request"], catalog, provider="claude")
        except ModelError as exc:
            report["outcomes"].append({"scenario_id": case_id, "error": str(exc),
                "elapsed_seconds": round(time.monotonic()-started, 3)})
            print(f"STOP {case_id}: {exc}")
            break
        result = output["result"]
        report["outcomes"].append({"scenario_id": case_id,
            "expected_status": case["expected_status"], "actual_status": result["status"],
            "matches_expected": result["status"] == case["expected_status"], "output": output})
        print(f"{case_id}: {result['status']}; {len(output['model_calls'])} API call(s)")
    complete = len(report["outcomes"]) == len(CASE_IDS) and all("output" in x for x in report["outcomes"])
    report["completed_all_cases"] = complete
    report["expected_outcomes_matched"] = sum(x.get("matches_expected", False) for x in report["outcomes"])
    calls = [c for x in report["outcomes"] for c in x.get("output", {}).get("model_calls", [])]
    report["recorded_successful_calls"] = len(calls)
    report["usage_note"] = "Tokens below cover completed plans only; an error can leave additional billed calls unrecorded."
    report["input_tokens"] = sum(c["usage"].get("input_tokens", 0) for c in calls)
    report["output_tokens"] = sum(c["usage"].get("output_tokens", 0) for c in calls)
    # Pricing reference: https://platform.claude.com/docs/en/models/haiku-4-5/overview
    if report["model"] == DEFAULT_MODEL:
        report["estimated_recorded_api_cost_usd"] = round(
            (report["input_tokens"] + 5 * report["output_tokens"]) / 1_000_000, 6)
        report["price_note"] = "Haiku 4.5 standard text rates checked Nov 15, 2026: $1/M input and $5/M output; estimate, not an invoice."
    destination = ROOT / "evidence/claude_live.json"
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Saved evidence/claude_live.json. No API key is included.")
    return 0 if complete and report["expected_outcomes_matched"] == len(CASE_IDS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
