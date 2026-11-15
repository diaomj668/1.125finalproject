"""Save a Claude key locally. This setup step makes no API calls."""
import getpass
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from trip_planner.config import DEFAULT_MODEL


def main():
    print("Massachusetts Trip Planner - local Claude setup")
    print("Paste your own Claude Console API key below. Input is hidden.")
    print("The key stays in this project's ignored .env file.")
    print("This step does not call the API or buy credits. Ctrl+C cancels.\n")
    target = ROOT / ".env"
    if target.exists():
        if input("Replace the existing local .env settings? [y/N] ").lower() != "y":
            print("Existing settings kept.")
            return 0
    try:
        key = getpass.getpass("Claude API key: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled. Nothing saved.")
        return 1
    if not key.startswith("sk-ant-") or any(c.isspace() for c in key):
        print("No settings saved. Use a Claude Console API key starting with sk-ant-.")
        return 1
    content = ("# Private local settings. Do not upload this file.\n"
               "PLANNER_PROVIDER=claude\n"
               f"ANTHROPIC_API_KEY={key}\n"
               f"ANTHROPIC_MODEL={DEFAULT_MODEL}\n")
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(content)
    print("\nSaved locally. The key has not been tested yet.")
    print("Next: python scripts/verify_claude.py --run")
    print("To open the app: double-click start_windows.cmd")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
