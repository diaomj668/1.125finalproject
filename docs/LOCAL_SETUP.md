# Run the project on a laptop

No cloud server or GCP account is needed. The website runs at `http://127.0.0.1:8000` and is available only on this computer. Python 3.11 or newer is enough; the app has no extra packages to install.

## Local mode

Double-click `start_windows.cmd` on Windows, or run `python run.py --open-browser`. With no `.env` file or shell settings, the app uses the local planner. This mode makes no paid API calls.

If `.env` already selects Claude, change `PLANNER_PROVIDER=local` to return to the local planner. Restart the server after changing settings.

## Claude mode

1. Use an API key from [Claude Console](https://platform.claude.com/settings/keys). The API account needs access to the selected model and available usage credits.
2. Double-click `configure_claude.cmd`, or run `python scripts/configure_claude.py`. Paste the key at the hidden prompt. This writes `.env` in the project folder. The key is not put in GitHub or returned to the browser.
3. Run `python scripts/verify_claude.py`. It reports whether a key is configured without sending a request to Claude. It does not prove the key is valid.
4. Run `python scripts/verify_claude.py --run` for three saved requests: Saturday closures, a Saturday with no admission budget, and places with missing facts. This makes at most nine API calls and can incur charges. It stops on an API error.
5. Read `evidence/claude_live.json`, then start the app. The app's mode label should say Claude. Keep the server terminal open.

The key can also be entered by copying `.env.example` to `.env`. Put it after `ANTHROPIC_API_KEY=` and choose `PLANNER_PROVIDER=claude`. There is no need to paste it into chat or a source file. Explicit shell settings override the file.

## Common problems

| Message or symptom | What to check |
| --- | --- |
| Key not configured | Save `.env` in the project folder, with the exact variable name, then restart. |
| API key rejected | Use a valid Claude Console API key and replace it in local setup. |
| Request rejected | Check the model name and API account billing in Console. |
| Model not found or access denied | Check `ANTHROPIC_MODEL` and the key's model access. |
| Rate limit or temporary overload | Wait and try the same request again; do not keep clicking. |
| Page cannot connect | Keep the server terminal open. If the port is in use, run `python run.py --port 8125 --open-browser`. |
| Plan still needs changes | Read the failed checks. A working API does not guarantee that a request is feasible. |

The checked museum facts are still the November 13 snapshot. Local hosting does not make those facts live. The three API checks are an integration test, not a full quality comparison with a chatbot.
