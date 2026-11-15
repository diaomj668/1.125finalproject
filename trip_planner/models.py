"""Validate inputs before planning. Times are local Cambridge wall-clock times."""
from dataclasses import dataclass, asdict, field
from datetime import date
import math
import re

class InputError(ValueError):
    pass

def minute(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{2}:\d{2}", value):
        raise InputError("Use a time such as 11:00.")
    hour, mins = map(int, value.split(":"))
    if hour > 23 or mins > 59:
        raise InputError("The time is outside a 24-hour day.")
    return hour * 60 + mins

def clock(value):
    return f"{int(value)//60:02d}:{int(value)%60:02d}"

def whole(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise InputError(f"{name} must be a whole number between {low} and {high}.")
    return value

@dataclass
class TripRequest:
    date: str
    start: str = "11:00"
    end: str = "17:00"
    adults: int = 1
    budget: float = 40
    max_walk_minutes: int = 45
    stop_count: int = 3
    interests: list = field(default_factory=lambda: ["museums", "art"])
    source_mode: str = "checked"
    excluded_ids: list = field(default_factory=list)
    notes: str = ""

    @classmethod
    def parse(cls, value):
        if not isinstance(value, dict):
            raise InputError("The request must be a JSON object.")
        extra = set(value) - set(cls.__dataclass_fields__)
        if extra:
            raise InputError("Unknown request fields: " + ", ".join(sorted(extra)))
        try:
            req = cls(**value)
            date.fromisoformat(req.date)
        except (TypeError, ValueError):
            raise InputError("Choose a valid date in YYYY-MM-DD format.") from None
        if minute(req.end) <= minute(req.start):
            raise InputError("End time must be after start time on the same day.")
        whole(req.adults, "Adults", 1, 6)
        whole(req.stop_count, "Stops", 2, 5)
        whole(req.max_walk_minutes, "Walking limit", 0, 180)
        if type(req.budget) not in (int, float) or not math.isfinite(req.budget) or not 0 <= req.budget <= 1000:
            raise InputError("Admission budget must be between $0 and $1,000.")
        if req.source_mode not in ("checked", "historical"):
            raise InputError("Choose checked or historical data.")
        if (not isinstance(req.interests, list) or not 1 <= len(req.interests) <= 5
                or any(x not in ("museums", "art", "science", "history", "nature", "food") for x in req.interests)):
            raise InputError("Choose between one and five supported interests.")
        if not isinstance(req.excluded_ids, list) or len(req.excluded_ids) > 20 or any(not isinstance(x, str) or len(x)>150 for x in req.excluded_ids):
            raise InputError("Invalid excluded place IDs.")
        if not isinstance(req.notes, str) or len(req.notes) > 500:
            raise InputError("Notes must be at most 500 characters.")
        return req

    def to_dict(self):
        return asdict(self)
