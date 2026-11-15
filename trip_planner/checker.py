"""Check a proposed plan using code and stored facts, never model-written prices."""
from .models import minute, clock

def check_plan(request, stops, records, walk):
    checks=[]
    def add(rule, result, evidence, message, place_id=None):
        checks.append({"rule":rule,"result":result,"evidence":evidence,"message":message,"place_id":place_id})

    if not isinstance(stops,list):
        add("place_ids","fail","verified","The plan must contain a list of stops.")
        return result(checks,[],None,0)
    ids=[s.get("place_id") for s in stops if isinstance(s,dict)]
    if len(stops)!=request.stop_count or len(ids)!=len(stops):
        add("stop_count","fail","verified",f"The plan needs exactly {request.stop_count} stops.")
    else:
        add("stop_count","pass","verified",f"{len(stops)} stops.")
    if len(ids)!=len(stops) or any(not isinstance(pid,str) for pid in ids):
        add("place_ids","fail","verified","Each stop needs a text place ID.")
        return result(checks,[],None,0)
    valid=True
    if len(set(ids))!=len(ids):
        add("place_ids","fail","verified","A place appears more than once.")
        valid=False
    if any(pid not in records or pid in request.excluded_ids for pid in ids):
        add("place_ids","fail","verified","A stop is missing from the allowed records or was excluded.")
        valid=False
    if not valid:
        return result(checks,[],None,0)
    add("place_ids","pass","verified","Every stop points to an allowed local record.")
    legs={(x["from_id"],x["to_id"]):x for x in walk}
    last_end=None
    previous=None
    timeline=[]
    total_walk=0
    cost=0
    unknown_cost=False
    paid=set()
    for stop in stops:
        pid=stop["place_id"]
        record=records[pid]
        facts=record["facts"]
        try:
            begin=minute(stop["start"])
            duration=stop["duration_minutes"]
            if type(duration) is not int or not 20<=duration<=180:
                raise ValueError()
        except (KeyError,ValueError,TypeError):
            add("schedule","fail","verified","Each stop needs a valid start and 20–180 minute visit.",pid)
            continue
        end=begin+duration
        travel=legs.get((previous,pid)) if previous else None
        if previous and travel is None:
            add("travel","unknown","unknown","No walking estimate is available for this leg.",pid)
        mins=travel["minutes"] if travel else 0
        total_walk+=mins
        if begin<minute(request.start) or end>minute(request.end):
            add("time_window","fail","verified","This stop is outside the requested day.",pid)
        else:
            add("time_window","pass","verified","Within the requested time window.",pid)
        if last_end is not None:
            if begin<last_end:
                add("overlap","fail","verified","This stop overlaps the previous visit.",pid)
            elif travel and begin<last_end+mins:
                add("travel_gap","fail","estimated","There is not enough time for the estimated walk.",pid)
            elif travel:
                add("travel_gap","pass","estimated",f"Allows the {mins}-minute estimated walk.",pid)
        hrs=facts["hours"]
        if facts["hours_status"]=="unknown":
            add("opening_hours","unknown","unknown","Opening hours need checking for this date.",pid)
        elif not hrs:
            add("opening_hours","fail","verified","The saved official schedule says closed on this date.",pid)
        elif any(begin>=minute(a) and end<=minute(b) for a,b in hrs):
            add("opening_hours","pass","verified","Visit fits published hours in the dated snapshot.",pid)
        else:
            add("opening_hours","fail","verified","Visit falls outside the published hours.",pid)
        group=facts["ticket_group"]
        admission=None
        if facts["price_status"]=="unknown" or facts["admission_usd"] is None:
            unknown_cost=True
            add("admission","unknown","unknown","No numeric admission price has been checked.",pid)
        else:
            admission=0 if group in paid else facts["admission_usd"]*request.adults
            paid.add(group)
            cost+=admission
            add("admission","pass","verified","Uses the dated adult admission price. Shared tickets are counted once.",pid)
        timeline.append({"place_id":pid,"name":record["name"],"start":clock(begin),"end":clock(end),
                         "duration_minutes":duration,"walk_before":travel,"charged_admission_usd":admission,
                         "record":record})
        last_end=end
        previous=pid
    if unknown_cost:
        if cost>request.budget:
            add("budget","fail","verified",f"Known admission alone is ${cost:g}, above the budget.")
        else:
            add("budget","unknown","unknown",f"Known admission is ${cost:g}; other admission costs are unknown.")
    else:
        add("budget","pass" if cost<=request.budget else "fail","verified",
            f"Admission for {request.adults} adult(s): ${cost:g} / ${request.budget:g}. Meals and shopping are excluded.")
    add("walking_limit","pass" if total_walk<=request.max_walk_minutes else "fail","estimated",
        f"Between-stop walking estimate: {total_walk} / {request.max_walk_minutes} minutes. Travel to the first stop is excluded.")
    return result(checks,timeline,None if unknown_cost else cost,total_walk,known_cost=cost)

def result(checks,timeline,cost,walk,known_cost=None):
    failures=[c for c in checks if c["result"]=="fail"]
    unknowns=[c for c in checks if c["result"]=="unknown"]
    return {"checks":checks,"stops":timeline,"has_failures":bool(failures),"has_unknowns":bool(unknowns),
            "status":"needs_change" if failures else ("needs_confirmation" if unknowns else "fits_estimates"),
            "total_admission_usd":cost,"known_admission_usd":cost if known_cost is None else known_cost,
            "walking_minutes":walk,"failure_count":len(failures),"unknown_count":len(unknowns)}
