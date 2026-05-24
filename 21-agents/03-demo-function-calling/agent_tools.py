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
    if not city:
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

        weather = requests.get(
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current_weather=true",
            timeout=10,
        ).json()

        temp = weather["current_weather"]["temperature"]
        wind = weather["current_weather"]["windspeed"]

        return f"{city}: {temp}°C, wind {wind} km/h"

    except Exception as e:
        return f"Weather fetch failed: {e}"


TOOLS = {
    "get_time": get_time,
    "get_date": get_date,
    "get_day": get_day,
    "get_datetime": get_datetime,
    "get_weather": get_weather,
}