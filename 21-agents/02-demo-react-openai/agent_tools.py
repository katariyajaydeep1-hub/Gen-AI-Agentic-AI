"""ReAct-style tool registry — same tools, robust parsing."""
from datetime import datetime
import pytz
import requests

INDIA_TZ = pytz.timezone("Asia/Kolkata")


def get_time(_=None):
    return datetime.now(INDIA_TZ).strftime("%I:%M:%S %p IST")

def get_date(_=None):
    return datetime.now(INDIA_TZ).strftime("%A, %B %d, %Y")

def get_day(_=None):
    return datetime.now(INDIA_TZ).strftime("%A")

def get_datetime(_=None):
    return datetime.now(INDIA_TZ).strftime(
        "%A, %B %d, %Y at %I:%M:%S %p IST"
    )

def get_weather(city="Bangalore"):
    if not city or city.lower() in {"none", "null", ""}:
        city = "Bangalore"
    try:
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}",
            timeout=10,
        ).json()
        if not geo.get("results"):
            return f"Could not find location for '{city}'."
        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        w = requests.get(
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current_weather=true",
            timeout=10,
        ).json()
        temp = w["current_weather"]["temperature"]
        wind = w["current_weather"]["windspeed"]
        return f"{city}: {temp}°C, wind {wind} km/h"
    except Exception as e:
        return f"Weather fetch failed: {e}"


TOOLS = {
    "get_time":     get_time,
    "get_date":     get_date,
    "get_day":      get_day,
    "get_datetime": get_datetime,
    "get_weather":  get_weather,
}


def match_tool(action_text):
    """Map fuzzy LLM action text to a canonical tool name."""
    if not action_text:
        return None
    t = action_text.lower()
    if "datetime" in t or ("date" in t and "time" in t):
        return "get_datetime"
    if "time" in t:
        return "get_time"
    if "date" in t:
        return "get_date"
    if "day" in t:
        return "get_day"
    if "weather" in t:
        return "get_weather"
    return None


def handle_tool_call(llm_output, step_num):
    """Parse a ReAct-style LLM message and execute the requested tool."""
    if "Action" not in llm_output:
        return None  # signals "no more tool calls needed"

    try:
        action = None
        action_input = None
        for line in llm_output.split("\n"):
            low = line.lower().strip()
            if low.startswith("action input"):
                action_input = line.split(":", 1)[-1].strip()
            elif low.startswith("action") and action is None:
                action = line.split(":", 1)[-1].strip()

        tool_name = match_tool(action)
        if tool_name not in TOOLS:
            return f"Observation: No matching tool for '{action}'"

        if tool_name == "get_weather":
            result = TOOLS[tool_name](action_input or "Bangalore")
        else:
            result = TOOLS[tool_name]()

        return f"Observation: {result}"
    except Exception as e:
        return f"Observation: Error - {e}"