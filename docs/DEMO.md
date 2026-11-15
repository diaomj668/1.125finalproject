# Short midpoint demo

Mingjiao Diao

Allow about four minutes. The course overview asks for a concise midpoint demonstration but does not give a specific time limit for this deliverable.

## Before presenting

Run `python run.py` and open `http://127.0.0.1:8000`. Keep this page, the README and `evidence/evaluation.json` open. Use the saved November dates for the example. The point is to show a reproducible run against a dated snapshot, not to claim live museum availability.

If a live app cannot be opened, `docs/demo.html` shows three saved runs. It is clearly labelled as a replay and does not make new plans.

## 1. Explain the project, about 30 seconds

"My project is a Massachusetts trip planner. I want it to do more than suggest a list of places. It should also show whether the visits fit the time, admission budget and opening hours.

For the midpoint, I narrowed it to one day around Harvard Square. That gave me a small set of places where I could check the source information."

## 2. Show Saturday closures, about 75 seconds

Click **Saturday closures**. The request is November 14, 2026, from 11:00 to 17:00, with three stops and a $20 admission budget for one adult.

Open **What changed** and compare the drafts. The first draft has three failed checks: two Saturday closures and one walking gap. The revised plan visits Harvard Art Museums, Peabody and Natural History. It costs $20 because the last two share one ticket. The saved run estimates 22 minutes of walking between stops.

"Here is the part I wanted to test. The first draft looks like a reasonable list, but two museums are closed on Saturday. Python catches that. The next draft changes the stops and checks the new schedule again. It keeps the same request."

Point to a source link and an estimated walking label.

"Verified means it matches the source I saved on November 13. It does not mean I have checked live availability. Walking is still an estimate."

## 3. Show an unresolved request, about 40 seconds

Keep Saturday selected and change the admission budget to $0. Build the plan again.

"There are not three free, open museums in this small set on Saturday. The app says the draft still needs changes. It does not quietly raise the budget or invent a free ticket."

## 4. Show missing facts, about 35 seconds

Click **Missing facts**. Explain that these places come from the wider 2021 records.

"The old records are useful for finding places, but they do not prove today's hours or prices. These checks stay unknown. That was one of the main points in the proposal feedback."

## 5. Explain results and next steps, about 50 seconds

"I saved 20 test requests. Eight fit the stored facts and walking estimates, nine need changes, and three need more information. All 20 return the expected result for that test. I also have 34 tests for specific rules, local setup and server requests.

The demonstration uses a local planner. I have written the Claude adapter, but I have not verified a real API call yet. That is the next step. After that, I will compare it with a plain chatbot using the same requests. I am leaving multi-day planning and taste ranking until the one-day checks are reliable."

## Likely questions

**What makes it agentic?** The controller finds records, proposes a plan, checks it and uses the failures to revise the plan. At this point the default controller is rule-based. The Claude adapter can supply the draft and revisions, but I will not claim an LLM demonstration before I test it.

**Why only five museums?** I wanted a small example with usable source information. The repository has 500 older place records, but I am not treating all of them as current.

**Why no cloud deployment?** The midpoint asks for a working repository and a short demonstration. Local execution is enough for this scope.

**What was reused?** The place subset, distance calculation starting point and the idea of checking and repairing a draft came from RoamWise. The source list separates that from the midpoint-specific work.
