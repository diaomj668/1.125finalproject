# Midpoint check-in

Mingjiao Diao, Massachusetts Trip Planner

## Direction

The original proposal covered Massachusetts trips. After the proposal feedback, I narrowed the midpoint to one day around Harvard Square. The aim is to show that the app can find a problem in a draft itinerary and make a reasonable revision.

The interface has a date, a time window, interests, an admission budget and a walking limit. The result includes a schedule, source links and the checks behind it. There is also a way to remove a stop and try again.

## Progress

The local planning loop is working. It retrieves records, drafts stops, checks the draft, and searches for a revision if a rule fails. The local search considers up to ten records, uses one hour per stop and stops after 20 seconds. It returns an unresolved draft when it cannot find a fitting plan. It does not claim that the request is impossible across every place in Cambridge.

The default planner is deterministic. The Claude adapter follows the same check-and-revise flow, with at most three model calls in total. Real API calls remain untested. The current evidence is for the local planner only.

## Main questions investigated

| Question | What this version does | Remaining limit |
| --- | --- | --- |
| Can old data support current claims? | Uses official fact sheets for five museums and marks other hours/prices unknown. | Facts need refreshing. The 2021 metadata may also have changed. |
| Can a draft be checked and revised? | A Saturday example replaces closed museums and fixes travel gaps. | Local search is limited to ten candidates and fixed one-hour visits. |
| Can the budget be checked? | Checks adult admission and counts the joint museum ticket once. | Meals, discounts, children and transport fares are not included. |
| Can travel clashes be checked? | Uses one declared walking formula for every leg. | A geometric estimate is not a real walking route. |
| Is the Claude integration ready? | Request construction, output format checks and missing-key handling are implemented and tested without network calls. | A real response, latency, token usage and cost still need testing. |

## Evidence

The saved run on November 13, 2026 includes 20 requests. Eight end with no failed or unknown checks, although walking is still estimated. Nine require changes. Three have no known rule violation but still need confirmation of missing facts. All 20 match the expected result for that case.

Ten first drafts with known rule violations were revised into drafts without those violations. Three of these revised plans still have unknown facts. This comparison is against a simple local ranked-list draft, not against an LLM. There were zero real Claude calls in the saved run.

The test suite has 34 passing tests as of November 15, 2026, including checks for overlap, closure dates, malformed IDs, party costs, shared admission, old facts and constraints that cannot be met. The newer tests also send real HTTP requests to a local server and check that the API key stays out of its responses. The full saved scenario outputs are in `evidence/`.

Windows startup and local key setup are now included. The three-case live verification script records actual model names, token usage and elapsed time when a key is available. Preparing this script is not the same as completing a real Claude run; that step remains open.

## Plan for the rest of the project

1. **Next work session:** connect a Claude key, run a small live API check, and save the exact model ID, token usage and response time. Fix parsing or retry issues before expanding the app.
2. **Following sessions:** compare local planning, Claude with checks, and a plain-chatbot draft on the same requests. Review failures individually. Manually inspect a few walking legs and refresh the fact sheets.
3. **Before the final demo:** have another person follow the setup instructions, improve confusing parts of the interface, and finish a reproducible demonstration.
4. **Only if time remains:** add review-based taste ranking, then consider a two-day plan. Live closures, reservations and payments are outside the current scope.

No midpoint deadline beyond the supplied course overview has been assumed. No GCP deployment is planned for this version.
