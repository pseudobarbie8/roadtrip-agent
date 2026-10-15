"""Tools the agent can call. All use free, keyless public APIs, so the data is live."""
import json
import time
from functools import lru_cache

import httpx

HEADERS = {"User-Agent": "trip-planner-agent/0.1 (learning project)"}

TOOLS = [
    {
        "name": "get_weather",
        "description": "Daily weather forecast (max/min temperature in C, rain in mm) for a city, starting today.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "days": {"type": "integer", "minimum": 1, "maximum": 16},
            },
            "required": ["city"],
        },
    },
    {
        "name": "find_places",
        "description": "Find real places (restaurants, museums, parks, viewpoints...) in a city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "e.g. 'museums' or 'seafood restaurants'"},
                "city": {"type": "string"},
            },
            "required": ["query", "city"],
        },
    },
]


@lru_cache
def geocode(city: str):
    """(lat, lon) for a city name, or None."""
    time.sleep(1)  # Nominatim allows 1 request per second
    r = httpx.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": city, "format": "json", "limit": 1},
        headers=HEADERS,
        timeout=15,
    ).json()
    return (float(r[0]["lat"]), float(r[0]["lon"])) if r else None


def get_weather(city: str, days: int = 3):
    point = geocode(city)
    if point is None:
        return {"error": f"could not find {city!r}"}
    d = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": point[0],
            "longitude": point[1],
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "forecast_days": min(max(days, 1), 16),
        },
        timeout=15,
    ).json()["daily"]
    return [
        {"date": date, "max_c": hi, "min_c": lo, "rain_mm": rain}
        for date, hi, lo, rain in zip(
            d["time"], d["temperature_2m_max"], d["temperature_2m_min"], d["precipitation_sum"]
        )
    ]


def find_places(query: str, city: str):
    time.sleep(1)
    r = httpx.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": f"{query} in {city}", "format": "json", "limit": 5},
        headers=HEADERS,
        timeout=15,
    ).json()
    return [{"name": p["display_name"].split(",")[0], "address": p["display_name"]} for p in r]


FUNCTIONS = {"get_weather": get_weather, "find_places": find_places}


def run_tool(name: str, args: dict) -> str:
    """Run a tool by name and return JSON text. Errors are returned to the model, not raised."""
    try:
        return json.dumps(FUNCTIONS[name](**args))
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})
