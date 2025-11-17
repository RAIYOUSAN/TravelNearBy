"""Seed POI data used by the offline planner.

In production this module should be replaced by an external data source
such as a maps API or a pre-built POI database.
"""
from __future__ import annotations

from datetime import time
from typing import Dict, List, Tuple

from .models import POI

# Approximate city centers for distance calculations
CITY_CENTERS: Dict[str, Tuple[float, float]] = {
    "北京": (39.9042, 116.4074),
    "上海": (31.2304, 121.4737),
}

SEED_POIS: List[POI] = [
    POI(
        name="颐和园",
        city="北京",
        latitude=39.9996,
        longitude=116.2755,
        themes=["文化", "公园", "历史"],
        price_level="$$",
        open_time=time(hour=6, minute=30),
        close_time=time(hour=18),
        typical_duration_minutes=150,
    ),
    POI(
        name="798 艺术区",
        city="北京",
        latitude=39.9840,
        longitude=116.4975,
        themes=["艺术", "购物", "打卡"],
        price_level="$",
        open_time=time(hour=9),
        close_time=time(hour=21),
        typical_duration_minutes=120,
    ),
    POI(
        name="什刹海",
        city="北京",
        latitude=39.9405,
        longitude=116.3804,
        themes=["公园", "夜景", "美食"],
        price_level="$",
        open_time=time(hour=0),
        close_time=time(hour=23, minute=59),
        typical_duration_minutes=90,
    ),
    POI(
        name="故宫博物院",
        city="北京",
        latitude=39.9163,
        longitude=116.3972,
        themes=["文化", "历史", "博物馆"],
        price_level="$$$",
        open_time=time(hour=8, minute=30),
        close_time=time(hour=17, minute=30),
        typical_duration_minutes=180,
    ),
    POI(
        name="外滩",
        city="上海",
        latitude=31.2400,
        longitude=121.4900,
        themes=["夜景", "历史", "步行"],
        price_level="$",
        open_time=time(hour=0),
        close_time=time(hour=23, minute=59),
        typical_duration_minutes=90,
    ),
    POI(
        name="豫园",
        city="上海",
        latitude=31.2270,
        longitude=121.4920,
        themes=["文化", "美食", "历史"],
        price_level="$$",
        open_time=time(hour=8, minute=30),
        close_time=time(hour=20),
        typical_duration_minutes=120,
    ),
    POI(
        name="徐家汇天主教堂",
        city="上海",
        latitude=31.1942,
        longitude=121.4346,
        themes=["文化", "建筑"],
        price_level="$",
        open_time=time(hour=7),
        close_time=time(hour=17),
        typical_duration_minutes=60,
    ),
    POI(
        name="上海博物馆",
        city="上海",
        latitude=31.2305,
        longitude=121.4730,
        themes=["博物馆", "文化", "历史"],
        price_level="$$",
        open_time=time(hour=9),
        close_time=time(hour=17),
        typical_duration_minutes=150,
    ),
]
