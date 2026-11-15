"""Adapted from The Routevengers' roamwise/planner.py (see docs/SOURCES.md).
This is a geometric estimate, not a street route or measured journey.
"""
import math

def distance_km(a, b):
    lat1, lat2 = math.radians(a["latitude"]), math.radians(b["latitude"])
    dlat = lat2-lat1
    dlon = math.radians(b["longitude"]-a["longitude"])
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371*2*math.asin(min(1, math.sqrt(h)))

def walking_minutes(a, b):
    if a["place_id"] == b["place_id"]:
        return 0
    return math.ceil(distance_km(a,b)*1.35/4*60) + 5

WALK_METHOD = "Great-circle distance × 1.35, walking at 4 km/h, plus 5 minutes per leg. No street routing."
