"""Data models used by the TravelNearby planner."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time, timedelta
from typing import List, Literal, Sequence

TravelMode = Literal["walking", "transit", "driving"]


@dataclass
class POI:
    """Point of interest metadata."""

    name: str
    city: str
    latitude: float
    longitude: float
    themes: List[str]
    price_level: str
    open_time: time
    close_time: time
    typical_duration_minutes: int


@dataclass
class UserPreference:
    """User constraints for a short trip request."""

    city: str
    days: int
    radius_km: float
    themes: List[str]
    budget_per_day: float
    travel_mode: TravelMode = "driving"
    start_time: time = time(hour=9)
    end_time: time = time(hour=19)


@dataclass
class ItineraryStop:
    poi: POI
    arrival_time: time
    departure_time: time
    travel_minutes: int
    notes: str = ""


@dataclass
class ItineraryDay:
    label: str
    stops: List[ItineraryStop]

    @property
    def total_travel_minutes(self) -> int:
        return sum(stop.travel_minutes for stop in self.stops)


@dataclass
class Itinerary:
    preference: UserPreference
    days: List[ItineraryDay] = field(default_factory=list)

    def describe(self) -> str:
        lines: List[str] = []
        for day in self.days:
            lines.append(f"=== {day.label} ===")
            for stop in day.stops:
                total = timedelta(minutes=stop.travel_minutes + stop.poi.typical_duration_minutes)
                lines.append(
                    (
                        f"{stop.arrival_time.strftime('%H:%M')} → {stop.departure_time.strftime('%H:%M')} | "
                        f"{stop.poi.name} | 交通 {stop.travel_minutes} 分钟 | {stop.notes or '建议游览'} | 总耗时 {total}"
                    )
                )
            lines.append("")
        return "\n".join(lines).strip()


@dataclass
class ValidationIssue:
    message: str
    level: Literal["warning", "error"] = "warning"
    hint: str | None = None


@dataclass
class ValidationReport:
    issues: Sequence[ValidationIssue]

    @property
    def has_blockers(self) -> bool:
        return any(issue.level == "error" for issue in self.issues)

    def summarize(self) -> str:
        if not self.issues:
            return "行程已通过基础校验"
        lines = []
        for issue in self.issues:
            prefix = "[严重]" if issue.level == "error" else "[提示]"
            suffix = f" 建议：{issue.hint}" if issue.hint else ""
            lines.append(f"{prefix} {issue.message}{suffix}")
        return "\n".join(lines)
