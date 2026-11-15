# Tests

Run `python -m unittest discover -s tests -v` from the repository root.

The tests cover the checker, repair behavior and Claude error/format handling without making network calls. The 20 cases in `scenarios.json` also drive the saved evaluation. They include requests that should succeed, requests that should remain unresolved, and requests with missing facts.
