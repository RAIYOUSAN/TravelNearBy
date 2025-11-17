"""Run a sample itinerary plan using the offline TravelPlanner."""

from pathlib import Path
import sys

# Ensure local package is importable when running directly
sys.path.append(str(Path(__file__).resolve().parents[1]))

from travel_nearby import PlanRequest, TravelPlanner


def main() -> None:
    planner = TravelPlanner()
    request = PlanRequest(
        city="北京",
        days=2,
        radius_km=30,
        themes=["公园", "文化"],
        budget_per_day=600,
        travel_mode="driving",
    )
    itinerary, report = planner.plan(request)
    print("行程提要：")
    print(itinerary.describe())
    print("\n校验：")
    print(report.summarize())


if __name__ == "__main__":
    main()
