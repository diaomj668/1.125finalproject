"""Read the three local settings without executing shell code."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
SETTING_NAMES = {"PLANNER_PROVIDER", "ANTHROPIC_API_KEY", "ANTHROPIC_MODEL"}


def load_settings(path=None, environ=None):
    """Explicit shell settings take precedence over the ignored .env file."""
    target = os.environ if environ is None else environ
    path = Path(path) if path is not None else ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name, value = name.strip(), value.strip()
        if name not in SETTING_NAMES:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        # Empty shell values count as unset, so the local .env can still supply them.
        if not target.get(name):
            target[name] = value
