"""Local source records and a small, separately checked museum set."""
import json
from pathlib import Path
import re
from datetime import date
from .geometry import walking_minutes, WALK_METHOD

ROOT = Path(__file__).resolve().parents[1]

class Catalog:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.places = {p["place_id"]:p for p in
                       (json.loads(line) for line in (self.root/"data/places.jsonl").read_text(encoding="utf-8").splitlines())}
        self.snapshot = json.loads((self.root/"data/checked_places.json").read_text(encoding="utf-8"))
        self.checked = {p["place_id"]:p for p in self.snapshot["places"]}

    def search(self, request, limit=10):
        words=set(re.findall(r"[a-z]+", " ".join(request.interests).lower()))
        related={"museums":{"museum","museums","gallery","collection"},
                 "art":{"art","arts","paintings","visual"},"science":{"science","scientific","natural","instruments"},
                 "history":{"history","historical","archaeology","ancient","ethnology"},
                 "nature":{"park","nature","outdoors","garden"},"food":{"restaurant","cafe","food"}}
        terms=set().union(*(related.get(w,{w}) for w in words))
        candidates=[]
        for pid, p in self.places.items():
            if p["city"]!="Cambridge" or pid in request.excluded_ids:
                continue
            if request.source_mode=="checked" and pid not in self.checked:
                continue
            if p["category"]=="lodging":
                continue
            text=" ".join([p["name"],p.get("description") or ""," ".join(p.get("categories",[])),
                           " ".join(self.checked.get(pid,{}).get("tags",[]))]).lower()
            tokens=set(re.findall(r"[a-z]+",text))
            matches=sorted(tokens & terms)
            if not matches:
                continue
            # Metadata matching only. Review-based taste ranking is future work.
            score=len(matches)+sum(t in p["name"].lower() for t in terms)
            candidates.append({**p,"match_score":score,"matched_terms":matches})
        candidates.sort(key=lambda p:(-p["match_score"],p["name"]))
        return candidates[:limit]

    def facts(self, pid, day):
        p=self.places[pid]
        c=self.checked.get(pid)
        if c is None:
            return {"hours":None,"hours_status":"unknown","admission_usd":None,
                    "price_status":"unknown","ticket_group":pid,"source_urls":[p["source_url"]],
                    "checked_at":None,"historical_hours":p.get("historical_hours"),
                    "historical_price_category":p.get("price"),
                    "note":"Only a 2021 record is available. A $ symbol is not a ticket price."}
        day=date.fromisoformat(day)
        age=(day-date.fromisoformat(self.snapshot["checked_at"])).days
        in_window=0<=age<=self.snapshot["planning_horizon_days"]
        hours=c["overrides"].get(day.isoformat(),c["weekly_hours"].get(str(day.weekday())))
        return {"hours":hours if in_window else None,
                "hours_status":"verified" if in_window else "unknown",
                "admission_usd":c["adult_admission_usd"] if in_window else None,
                "price_status":"verified" if in_window else "unknown",
                "ticket_group":c["ticket_group"],"source_urls":c["source_urls"],
                "checked_at":self.snapshot["checked_at"],
                "historical_hours":p.get("historical_hours"),"historical_price_category":p.get("price"),
                "note":c["note"] if in_window else "The trip is outside this snapshot's 30-day planning window. Refresh the facts."}

    def record(self, pid, day):
        return {**self.places[pid],"facts":self.facts(pid,day)}

    def estimate_walk(self, ids):
        legs=[]
        for a,b in zip(ids,ids[1:]):
            if a not in self.places or b not in self.places:
                continue
            legs.append({"from_id":a,"to_id":b,"minutes":walking_minutes(self.places[a],self.places[b]),
                         "status":"estimated","method":WALK_METHOD})
        return legs
