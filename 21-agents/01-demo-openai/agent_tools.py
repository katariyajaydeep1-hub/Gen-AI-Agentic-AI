"""Tools available to the agent. Each tool is a Python function returning a string."""
from datetime import datetime
import pytz

INDIA_TZ = pytz.timezone("Asia/Kolkata")

def get_current_day_india():
    return datetime.now(INDIA_TZ).strftime("%A")

def get_current_date_india():
    return datetime.now(INDIA_TZ).strftime("%B %d, %Y")

def get_current_time_india():
    return datetime.now(INDIA_TZ).strftime("%I:%M %p IST")

def get_current_datetime_india():
    now = datetime.now(INDIA_TZ)
    return now.strftime("%A, %B %d, %Y at %I:%M %p IST")


def agent_router(topic):
    """Rule-based router: match the user's text and call the right tool."""
    t = topic.lower()

    # Check more specific patterns first (date AND time together)
    if ("date and time" in t) or ("time and date" in t) or \
       ("date" in t and "time" in t):
        return f"The current date and time in India is {get_current_datetime_india()}."

    if "time" in t and "current" in t:
        return f"The current time in India is {get_current_time_india()}."

    if "date" in t and ("current" in t or "today" in t):
        return f"The current date in India is {get_current_date_india()}."

    if "day today" in t or "current day" in t or "what day" in t:
        return f"The current day in India is {get_current_day_india()}."

    return None


if __name__ == "__main__":
    print("Day  :", get_current_day_india())
    print("Date :", get_current_date_india())
    print("Time :", get_current_time_india())
    print()
    print(agent_router("what is the current date and time?"))
