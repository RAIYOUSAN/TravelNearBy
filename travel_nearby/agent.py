"""Heuristic travel planner coordinating filtering, routing, and validation."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Tuple

from .models import Itinerary, ItineraryDay, ItineraryStop, TravelMode, UserPreference, ValidationReport
from .tools import build_route, filter_pois, schedule_day, validate_itinerary


@dataclass
class PlanRequest:
    city: str
    days: int
    radius_km: float
    themes: List[str]
    budget_per_day: float
    travel_mode: TravelMode = "driving"
    start_time: str = "09:00"
    end_time: str = "19:00"


class TravelPlanner:
    """Lightweight planner coordinating POI retrieval, routing, and validation."""

    def plan(self, request: PlanRequest) -> Tuple[Itinerary, ValidationReport]:
        preference = UserPreference(
            city=request.city,
            days=request.days,
            radius_km=request.radius_km,
            themes=request.themes,
            budget_per_day=request.budget_per_day,
            travel_mode=request.travel_mode,
            start_time=datetime.strptime(request.start_time, "%H:%M").time(),
            end_time=datetime.strptime(request.end_time, "%H:%M").time(),
        )

        pois = filter_pois(preference)
        ordered = build_route(preference, pois)
        days: List[ItineraryDay] = []
        leftovers = list(ordered)
        current_date = datetime.today()

        for idx in range(preference.days):
            scheduled, remaining_pois = schedule_day(
                start_time=preference.start_time,
                ordered_pois=leftovers,
                latest_end=preference.end_time,
            )
            stops = [
                ItineraryStop(
                    poi=poi,
                    arrival_time=arrival,
                    departure_time=departure,
                    travel_minutes=travel_minutes,
                    notes=_build_notes(preference, poi, travel_minutes),
                )
                for poi, arrival, departure, travel_minutes in scheduled
            ]
            days.append(
                ItineraryDay(
                    label=(current_date + timedelta(days=idx)).strftime("Day %d"),
                    stops=stops,
                )
            )
            leftovers = [(poi, 0) for poi in remaining_pois]

        itinerary = Itinerary(preference=preference, days=days)
        validation = validate_itinerary(
            ((stop.poi, stop.arrival_time, stop.departure_time, stop.travel_minutes) for day in days for stop in day.stops),
            preference,
        )
        return itinerary, validation


def _build_notes(preference: UserPreference, poi, travel_minutes: int) -> str:
    reasons: List[str] = []
    if set(poi.themes).intersection(preference.themes):
        reasons.append("符合偏好主题")
    if travel_minutes > 60:
        reasons.append("路途稍远，注意时间安排")
    price_hint = {"$": "免费/低消费", "$$": "中等消费", "$$$": "较高消费"}.get(poi.price_level)
    if price_hint:
        reasons.append(price_hint)
    return "；".join(reasons)
