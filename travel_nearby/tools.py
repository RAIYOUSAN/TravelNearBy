"""Utility tools to support itinerary planning without external dependencies."""
from __future__ import annotations

import math
from datetime import datetime, time, timedelta
from typing import Iterable, List, Sequence, Tuple

from .data import CITY_CENTERS, SEED_POIS
from .models import POI, TravelMode, UserPreference, ValidationIssue, ValidationReport

EARTH_RADIUS_KM = 6371


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute distance between two coordinates in kilometers."""

    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_RADIUS_KM * c


def city_center(city: str) -> Tuple[float, float]:
    """Return city center coordinates; defaults to first POI if unknown."""

    if city in CITY_CENTERS:
        return CITY_CENTERS[city]
    for poi in SEED_POIS:
        if poi.city == city:
            return poi.latitude, poi.longitude
    return SEED_POIS[0].latitude, SEED_POIS[0].longitude


def filter_pois(preference: UserPreference) -> List[POI]:
    """Return POIs matching city, radius, and theme intersection."""

    matches = []
    center_lat, center_lon = city_center(preference.city)
    for poi in SEED_POIS:
        if poi.city != preference.city:
            continue
        if preference.themes and not set(poi.themes).intersection(preference.themes):
            continue
        distance = haversine_distance(center_lat, center_lon, poi.latitude, poi.longitude)
        if distance <= preference.radius_km:
            matches.append(poi)
    return matches


def travel_minutes_between(p1: POI, p2: POI, mode: TravelMode) -> int:
    """Estimate travel minutes between two POIs using simple speed defaults."""

    speed_map = {"walking": 4.5, "transit": 20, "driving": 40}
    speed = speed_map.get(mode, 30)  # km/h
    distance = haversine_distance(p1.latitude, p1.longitude, p2.latitude, p2.longitude)
    hours = distance / speed
    return max(10, int(hours * 60))


def build_route(preference: UserPreference, pois: Sequence[POI]) -> List[Tuple[POI, int]]:
    """Greedy route ordering by nearest neighbor starting from city center."""

    if not pois:
        return []

    # Seed with the closest POI to the city center to avoid skewed starting points
    center_lat, center_lon = city_center(preference.city)
    sorted_pois = sorted(pois, key=lambda poi: haversine_distance(center_lat, center_lon, poi.latitude, poi.longitude))
    ordered: List[Tuple[POI, int]] = []
    remaining = list(sorted_pois)
    current = remaining.pop(0)
    ordered.append((current, 0))

    while remaining:
        next_poi = min(remaining, key=lambda p: travel_minutes_between(current, p, preference.travel_mode))
        travel_minutes = travel_minutes_between(current, next_poi, preference.travel_mode)
        ordered.append((next_poi, travel_minutes))
        current = next_poi
        remaining.remove(next_poi)
    return ordered


def schedule_day(start_time: time, ordered_pois: Sequence[Tuple[POI, int]], latest_end: time) -> Tuple[List[Tuple[POI, time, time, int]], List[POI]]:
    """Create a day schedule returning accepted POIs and leftovers."""

    accepted: List[Tuple[POI, time, time, int]] = []
    remaining: List[POI] = []
    current_time = datetime.combine(datetime.today(), start_time)

    for poi, travel_minutes in ordered_pois:
        arrival = current_time + timedelta(minutes=travel_minutes)
        stay_duration = timedelta(minutes=poi.typical_duration_minutes)
        departure = arrival + stay_duration
        if departure.time() > latest_end:
            remaining.append(poi)
            continue
        accepted.append((poi, arrival.time(), departure.time(), travel_minutes))
        current_time = departure
    return accepted, remaining


def validate_itinerary(stops: Iterable[Tuple[POI, time, time, int]], preference: UserPreference) -> ValidationReport:
    issues: List[ValidationIssue] = []
    stops_list = list(stops)

    for poi, arrival, departure, travel_minutes in stops_list:
        if arrival < poi.open_time or departure > poi.close_time:
            issues.append(
                ValidationIssue(
                    message=f"{poi.name} 可能不在营业时间内",
                    level="warning",
                    hint=f"开放 {poi.open_time.strftime('%H:%M')} - {poi.close_time.strftime('%H:%M')}",
                )
            )
        if travel_minutes > 90:
            issues.append(
                ValidationIssue(
                    message=f"从上一站到 {poi.name} 路途较远，耗时 {travel_minutes} 分钟",
                    level="warning",
                    hint="考虑缩小游玩半径或调整主题",
                )
            )

    estimated_cost = len(stops_list) * 200
    if estimated_cost > preference.budget_per_day * preference.days:
        issues.append(
            ValidationIssue(
                message="预算可能不足",
                level="error",
                hint=f"预计费用约 ¥{estimated_cost}，每日预算 ¥{preference.budget_per_day}",
            )
        )

    if preference.themes:
        visited_themes = set(t for poi, *_ in stops_list for t in poi.themes)
        missing = set(preference.themes) - visited_themes
        if missing:
            issues.append(
                ValidationIssue(
                    message=f"以下主题覆盖不足：{', '.join(sorted(missing))}",
                    level="warning",
                    hint="调整筛选条件或增加行程天数",
                )
            )

    return ValidationReport(issues=issues)
