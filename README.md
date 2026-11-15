# Massachusetts Trip Planner

Mingjiao Diao | 1.125 Agentic Engineering | Midpoint check-in

This project helps someone plan a day out and check whether the stops fit together. The current version focuses on five museums around Harvard Square. It checks opening hours, admission costs, visit times and estimated walking time. If a draft fails, it tries a revised plan and shows what changed.

The app runs on a laptop. A cloud deployment or GCP account is not needed.

## Run it

Install Python 3.11 or newer, then run these commands in the project folder:

```bash
python run.py
```

Open **http://127.0.0.1:8000**. There are no third-party Python packages to install for the app or tests. On Windows, `py run.py` also works if Python was installed with the launcher. Use `python run.py --port 8125` if port 8000 is in use.

On Windows, double-click **start_windows.cmd** to start the server and open the app. Keep its terminal window open while using the app.

Start with **Saturday closures**. The first draft includes two museums that are closed on Saturday. The revised plan replaces them, keeps the same budget, and includes enough time for the estimated walks.

## What works at the midpoint

- Find Cambridge places by matching interests to their names, categories and descriptions.
- Draft a one-day plan for 2-5 stops, with one hour per stop in local mode.
- Check place IDs, opening hours, time overlaps, walking gaps and the group's admission budget.
- Count the joint Natural History / Peabody ticket once per adult.
- Revise a failed draft without quietly changing the request.
- Leave out a stop and build another plan.
- Show sources, failed checks and unknown facts. Save the full result as JSON.

The default is a **local, rule-based planner**. It does not call an LLM. An optional Claude adapter is included, but a real Claude run has not been verified yet because an API key was not available for this check-in. The app always shows which mode is running.

## What the labels mean

| Label | Meaning |
| --- | --- |
| Verified | A fact matches a saved official source, or an exact request rule passes. It is not a live availability guarantee. |
| Estimated | A value is calculated using assumptions. All walking times use this label. |
| Unknown | There is not enough current information to check the claim. |

The five museum fact sheets were checked on **November 13, 2026**. They are used only for trips within the next 30 days. This is a project rule, not a promise that a website will stay unchanged. Other records come from a 2021 dataset, so their old hours and price symbols are not treated as current facts.

Walking time is estimated from straight-line distance, multiplied by 1.35, at 4 km/h, with five extra minutes per leg. It does not use street routing, road crossings, weather or accessibility information. Admission is the only cost checked. Meals, shopping and the trip to the first stop are outside the budget calculation.

## Tests and results

```bash
python -m unittest discover -s tests -v
python scripts/evaluate.py
```

The current suite passed **34 tests** on November 15, 2026, including local settings and HTTP requests to the running server. All **20 saved scenarios** from the November 13 evaluation returned the expected outcome:

| Outcome | Scenarios |
| --- | ---: |
| Fits the saved facts and walking estimates | 8 |
| Needs changes because the request cannot be met by this search | 9 |
| Needs confirmation because facts are missing or too old | 3 |

Ten drafts lost their known rule violations after revision. Three of those still had unknown facts. These are small, hand-written regression cases, not proof of performance on all trips. The first-draft comparison uses a local ranked-list baseline, not a plain chatbot.

See [the actual results](evidence/evaluation.json) and [the full saved plans](evidence/scenario_plans.json).

## Optional Claude mode

On Windows, double-click **configure_claude.cmd** and paste a Claude Console API key when prompted. The input is hidden. The script saves a local `.env` file that Git ignores. It does not call the API or buy credits. Then start the app with **start_windows.cmd**.

Alternatively, copy `.env.example` to `.env`, set `PLANNER_PROVIDER=claude` and fill in `ANTHROPIC_API_KEY`. `run.py` now loads this file automatically. Existing shell settings take priority. Restart the server after changing settings.

These shell commands also work:

PowerShell:

```powershell
$env:PLANNER_PROVIDER = "claude"
$env:ANTHROPIC_API_KEY = "your-own-key"
$env:ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
python run.py
```

macOS / Linux:

```bash
export PLANNER_PROVIDER=claude
export ANTHROPIC_API_KEY="your-own-key"
export ANTHROPIC_MODEL=claude-haiku-4-5-20251001
python run.py
```

This calls Anthropic's hosted API and may incur API charges. It does not deploy the website. The model proposes only place IDs and visit times. Python checks the proposal against the same records and can request up to two revisions. A model error is shown as an error; the app does not silently switch to the local planner. Free-form notes are sent only in Claude mode and are not interpreted in local mode.

Check the settings without making a paid call:

```bash
python scripts/verify_claude.py
```

Once the key is configured, run three live integration cases (up to nine API calls):

```bash
python scripts/verify_claude.py --run
```

This saves `evidence/claude_live.json` with the actual outcomes, resolved model, token usage and elapsed time. Failed runs are labelled as failures. No live results are claimed until this command has run. See [local setup](docs/LOCAL_SETUP.md) for troubleshooting.

## Midpoint material

- [Check-in summary](docs/MIDPOINT.md)
- [Short demonstration and speaking notes](docs/DEMO.md)
- [Original submitted proposal](docs/proposal.pdf)
- [Sources and reused material](docs/SOURCES.md)

## What remains

My next step is to test the Claude adapter with a real key and compare its draft with a plain chatbot on the same 20 requests. I also need to inspect a few walking estimates against real routes and test whether another person can run the project from the README. Review-based taste ranking and multi-day trips are later extensions. I will only add them after the one-day version is reliable.

The starting place records and some planning ideas come from the AC215 RoamWise project. This version narrows the scope and adds a small set of checked museum facts, explicit uncertainty labels, shared-ticket handling and saved midpoint scenarios. The source list explains the reuse.
