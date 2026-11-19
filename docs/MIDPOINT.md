# Midpoint check-in

Mingjiao Diao, Massachusetts Trip Planner

## Direction

The original proposal covered Massachusetts trips. After the proposal feedback, I narrowed the midpoint to one day around Harvard Square. The aim is to show that the app can find a problem in a draft itinerary and make a reasonable revision.

The interface has a date, a time window, interests, an admission budget and a walking limit. The result includes a schedule, source links and the checks behind it. There is also a way to remove a stop and try again.

## Progress

The local planning loop is working. It retrieves records, drafts stops, checks the draft, and searches for a revision if a rule fails. The local search considers up to ten records, uses one hour per stop and stops after 20 seconds. It returns an unresolved draft when it cannot find a fitting plan. It does not claim that the request is impossible across every place in Cambridge.

The default planner is deterministic. The Claude adapter follows the same check-and-revise flow, with at most three model calls in total. After the first live run, the Claude prompt was revised: it now receives precomputed walking times, fixed 60-minute visits and closure facts, and revisions name the failing stop. Three repeated runs of the revised prompt matched all three live cases. Those cases were used to revise the prompt, so they do not show how it performs on other requests. Most of the evaluation evidence is still for the local planner.

## Main questions investigated

| Question | What this version does | Remaining limit |
| --- | --- | --- |
| Can old data support current claims? | Uses official fact sheets for five museums and marks other hours/prices unknown. | Facts need refreshing. The 2021 metadata may also have changed. |
| Can a draft be checked and revised? | A Saturday example replaces closed museums and fixes travel gaps. | Local search is limited to ten candidates and fixed one-hour visits. |
| Can the budget be checked? | Checks adult admission and counts the joint museum ticket once. | Meals, discounts, children and transport fares are not included. |
| Can travel clashes be checked? | Uses one declared walking formula for every leg. | A geometric estimate is not a real walking route. |
| Is the Claude integration ready? | Request construction, output format checks and missing-key handling are implemented and tested without network calls. The prompt was revised after one live run; three repeated live runs then matched all three cases. | The three live cases were used to revise the prompt, and a set of saved requests it was not tuned on has not been run yet. Latency and cost come from only a few calls. |

## Evidence

The saved run on November 13, 2026 includes 20 requests. Eight end with no failed or unknown checks, although walking is still estimated. Nine require changes. Three have no known rule violation but still need confirmation of missing facts. All 20 match the expected result for that case.

Ten first drafts with known rule violations were revised into drafts without those violations. Three of these revised plans still have unknown facts. This comparison is against a simple local ranked-list draft, not against an LLM. There were zero real Claude calls in the saved run.

The test suite has 42 passing tests as of November 18, 2026, including checks for overlap, closure dates, malformed IDs, party costs, shared admission, old facts and constraints that cannot be met. The newer tests also send real HTTP requests to a local server and check that the API key stays out of its responses. The full saved scenario outputs are in `evidence/`.

Windows startup and local key setup are included. The three-case live script has been run four times: once with the earlier prompt on November 16, 2026 (one of three matched), and three times with the revised prompt on November 18, 2026 (three of three matched each time). The results are in `evidence/claude_live.json` and `evidence/live_runs/`.

## Plan for the rest of the project

1. **Next work session:** run the revised prompt on the saved requests it was not tuned on, record the failed checks for each plan, and fix any cases that fail.
2. **Following sessions:** compare local planning, Claude with checks, and a plain-chatbot draft on the same requests. Review failures individually. Manually inspect a few walking legs and refresh the fact sheets.
3. **Before the final demo:** improve confusing parts of the interface and finish a reproducible demonstration.
4. **Only if time remains:** add review-based taste ranking, then consider a two-day plan. Live closures, reservations and payments are outside the current scope.

No midpoint deadline beyond the supplied course overview has been assumed. No GCP deployment is planned for this version.
