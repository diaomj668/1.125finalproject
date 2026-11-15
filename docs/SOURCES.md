# Sources and reused material

Project author: Mingjiao Diao

## Starting project

This individual project builds on [RoamWise, The Routevengers' AC215 project](https://github.com/xiping-zhang-0708/ac215_The-Routevengers). The starting local snapshot was `c6b5d7c7ae98c9459005fe82f6b376f56dc52f30`.

| Material | How it is used here |
| --- | --- |
| `data/processed/places.jsonl` | Copied as `data/places.jsonl`: 500 place metadata records. Review texts and reviewer profiles are not included. |
| `roamwise/planner.py` | Starting point for the great-circle distance helper and conservative travel estimates. The checker and repair approach already existed in RoamWise and is not claimed as a new idea here. |
| Existing RoamWise prototype image | `web/boston.jpg` is an illustrative hero image from that prototype. It is not evidence of a route or a museum's current condition. |

The midpoint version uses a smaller Python standard-library app. It adds the five-museum fact sheet, the dated-source policy, explicit verified/estimated/unknown results, shared-ticket costs, a bounded local search, a Claude adapter and the saved test scenarios. The original Chroma index, review ranker, hosted model, GCP services and cloud credentials are not used here.

## Place data

The place subset originates from the [UCSD McAuley Lab Google Local data](https://mcauleylab.ucsd.edu/public_datasets/gdrive/googlelocal/), through RoamWise's processed data. The stored snapshot is from 2021. The proposal's 87,588-business count describes a broader processed Massachusetts collection, not the 500 records shipped here. This midpoint app searches only the Cambridge records within that subset.

Names, categories, descriptions, map links and approximate coordinates are used for finding places. Historical opening hours and dollar-sign categories are kept as background information. They are not converted into current opening hours or numeric admission fees. Review-based taste ranking has not been implemented in this version.

## Checked museum facts

These official pages were checked on November 13, 2026. The stored facts in `data/checked_places.json` include regular hours, listed closures, adult admission and ticket groups. They are a dated snapshot rather than a live feed.

- [Harvard Art Museums: visit](https://harvardartmuseums.org/visit) and [hours and closings](https://harvardartmuseums.org/visit/policies/hours-closings)
- [Harvard Museum of Natural History: plan your visit](https://www.hmnh.harvard.edu/plan-your-visit)
- [Peabody Museum: hours and admission](https://peabody.harvard.edu/hours-admission)
- [Collection of Historical Scientific Instruments: visit](https://chsi.harvard.edu/visit-us)
- [Harvard Museum of the Ancient Near East: visit](https://hmane.harvard.edu/visit)

The app assumes standard adult admission without discounts. It counts the Natural History / Peabody joint ticket once per adult. Coordinates remain approximate historical metadata, so the walking calculation is labelled estimated.

## Course and technical references

- [1.125 PS06 instructions, including the midpoint overview](https://github.com/onexi/ps06/blob/main/README.md)
- [Submitted proposal](https://github.com/onexi/ps06/blob/main/diaomj668/proposal.pdf)
- [John's proposal feedback](https://github.com/onexi/ps06/blob/main/diaomj668/feedback_John.md)
- [Abel's proposal feedback](https://github.com/onexi/ps06/blob/main/diaomj668/feedback_abel.md)
- [Anthropic API overview](https://platform.claude.com/docs/en/api/overview)
- [Anthropic API primer](https://platform.claude.com/docs/en/claude_api_primer)
- [Haiku 4.5 model and pricing](https://platform.claude.com/docs/en/models/haiku-4-5/overview), checked November 15, 2026; used only to estimate the cost of recorded live calls.

Python's standard library is used for the app, server and tests. No paid routing service is used. The optional Claude model defaults to `claude-haiku-4-5-20251001` and can be changed with `ANTHROPIC_MODEL`. There were no real Claude API calls in the saved local evaluation.

An AI coding assistant helped draft and debug code and documentation. It is a tool used in preparing the project, not a project author. Reused code, data and images are identified above.
