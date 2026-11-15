"""Find records, draft a day, check it, then make a bounded revision."""
import itertools
import os
import time

from .catalog import Catalog
from .checker import check_plan
from .claude import ClaudePlanner, ModelError
from .geometry import walking_minutes, WALK_METHOD
from .models import TripRequest, minute, clock

VISIT_MINUTES = 60

def first_draft(request, candidates):
    """Simple ranked-list baseline, before hours, cost or travel are checked."""
    begin=minute(request.start)
    stops=[]
    for place in candidates[:request.stop_count]:
        stops.append({"place_id":place["place_id"],"start":clock(begin),"duration_minutes":VISIT_MINUTES})
        begin+=VISIT_MINUTES+10
    return stops

def schedule(request, order, records):
    begin=minute(request.start)
    stops=[]
    previous=None
    for pid in order:
        if previous:
            begin+=walking_minutes(records[previous],records[pid])
        facts=records[pid]["facts"]
        if facts["hours_status"]=="verified":
            windows=facts["hours"] or []
            possible=[max(begin,minute(a)) for a,b in windows
                      if max(begin,minute(a))+VISIT_MINUTES<=minute(b)]
            if not possible:
                return None
            begin=min(possible)
        if begin+VISIT_MINUTES>minute(request.end):
            return None
        stops.append({"place_id":pid,"start":clock(begin),"duration_minutes":VISIT_MINUTES})
        begin+=VISIT_MINUTES
        previous=pid
    return stops

def revise_local(request, candidates, records, catalog, deadline):
    """Search at most ten candidates; never relax a user's constraints."""
    ids=[p["place_id"] for p in candidates]
    best=None
    best_score=None
    tried=0
    timed_out=False
    relevance={p["place_id"]:p["match_score"] for p in candidates}
    for order in itertools.permutations(ids,request.stop_count):
        if time.monotonic()>=deadline:
            timed_out=True
            break
        tried+=1
        stops=schedule(request,order,records)
        if stops is None:
            continue
        checked=check_plan(request,stops,records,catalog.estimate_walk(order))
        if checked["has_failures"]:
            continue
        # Prefer fewer unknowns, then relevant places, then shorter walks.
        score=(checked["unknown_count"],-sum(relevance[p] for p in order),checked["walking_minutes"])
        if best_score is None or score<best_score:
            best_score=score
            best=stops
    return best,{"orders_examined":tried,"search_timed_out":timed_out}

def plan(value,catalog=None,provider=None):
    request=TripRequest.parse(value)
    catalog=catalog or Catalog()
    provider=provider or os.getenv("PLANNER_PROVIDER","local")
    if provider not in ("local","claude"):
        raise ModelError("PLANNER_PROVIDER must be local or claude.")
    started=time.monotonic()
    candidates=catalog.search(request)
    records={p["place_id"]:catalog.record(p["place_id"],request.date) for p in candidates}
    trace=[{"step":"Find places","detail":f"Found {len(candidates)} matching Cambridge records (up to 10)."}]
    engine=ClaudePlanner() if provider=="claude" else None
    attempts=[]
    search={}
    draft=engine.generate(request,records) if engine else first_draft(request,candidates)
    trace.append({"step":"Draft plan","detail":"Claude drafted the stops and times." if engine else "Local baseline used the top-ranked records, one hour per stop."})
    for attempt in range(3 if engine else 2):
        ids=[s["place_id"] for s in draft]
        checked=check_plan(request,draft,records,catalog.estimate_walk(ids))
        attempts.append({"attempt":attempt,"draft":draft,"result":checked})
        trace.append({"step":"Check plan" if attempt==0 else "Check revised plan",
                      "detail":f'{checked["failure_count"]} failed checks; {checked["unknown_count"]} unknown checks.'})
        if not checked["has_failures"]:
            break
        if attempt==(2 if engine else 1):
            break
        if engine:
            if time.monotonic()-started>60:
                trace.append({"step":"Stop","detail":"The model-call time budget has been reached."})
                break
            draft=engine.generate(request,records,previous=checked)
        else:
            repaired,search=revise_local(request,candidates,records,catalog,started+20)
            if repaired is None:
                detail=("The search time limit was reached without finding a fitting plan." if search["search_timed_out"]
                        else "No one-hour-per-stop plan fits these constraints in the retrieved records. Try fewer stops, more time, or a different date.")
                trace.append({"step":"Stop","detail":detail})
                break
            draft=repaired
        trace.append({"step":"Revise plan","detail":"Revised stops or times using the failed checks. The request stayed the same."})
    final=attempts[-1]["result"]
    return {"request":request.to_dict(),"provider":provider,
            "provider_label":"Claude API" if engine else "Local planner (no LLM call)",
            "model":engine.model if engine else None,"model_usage":engine.usage if engine else [],
            "candidate_count":len(candidates),"candidates":[{"place_id":p["place_id"],"name":p["name"],
                "matched_terms":p["matched_terms"],"match_score":p["match_score"]} for p in candidates],
            "trace":trace,"attempts":attempts,"result":final,"search":search,
            "elapsed_seconds":round(time.monotonic()-started,3),"walking_method":WALK_METHOD,
            "snapshot_date":catalog.snapshot["checked_at"],
            "limits":["Cambridge pilot, one day, adults only.",
                      "Admission budget only; meals, shopping and travel to the first stop are excluded.",
                      "Walking times are geometric estimates, not street routes or accessibility guidance.",
                      "Verified means checked against a dated official source, not guaranteed live availability."]}
