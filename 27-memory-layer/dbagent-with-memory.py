from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.graph import StateGraph, END

import sqlite3
import json
import pickle
import os

from typing import TypedDict, List
from dotenv import load_dotenv


# ============================================================
# LOAD ENV VARIABLES
# ============================================================

load_dotenv(dotenv_path="../.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY missing in .env")


# ============================================================
# PICKLE DEMO
# ============================================================

my_data = {"users": ["Alice", "Bob"], "count": 42}

with open("data.pkl", "wb") as f:
    pickle.dump(my_data, f)

with open("data.pkl", "rb") as f:
    restored = pickle.load(f)

print("Pickle Loaded:", restored)


# ============================================================
# STATE
# ============================================================

class AgentState(TypedDict):
    input: str
    plan: dict
    result: str
    status: str
    messages: List[dict]


# ============================================================
# DATABASE
# ============================================================

DB_FILE = "users.db"


def setup_db():

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        authenticated INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()


def seed_data():

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    users = [
        ("ML001", "Raj", 1),
        ("ML002", "Ram", 0),
        ("ML003", "Sham", 1)
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO users VALUES (?, ?, ?)",
        users
    )

    conn.commit()
    conn.close()


# ============================================================
# TOOLS
# ============================================================

@tool
def add_user(name: str, user_id: str) -> str:
    """Add user to database"""

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:

        # CHECK EXISTING USER
        cursor.execute(
            "SELECT * FROM users WHERE id=?",
            (user_id,)
        )

        existing = cursor.fetchone()

        if existing:
            return f"User with ID {user_id} already exists"

        # INSERT USER
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (user_id, name, 1)
        )

        conn.commit()

        # SAVE MEMORY
        cursor.execute(
            "INSERT OR REPLACE INTO memory VALUES (?, ?)",
            ("last_user", f"{name}:{user_id}")
        )

        conn.commit()

        return f"User {name} added with ID {user_id}"

    except Exception as e:
        return f"ERROR: {str(e)}"

    finally:
        conn.close()


@tool
def list_users() -> str:
    """List all users"""

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, authenticated FROM users"
    )

    rows = cursor.fetchall()

    conn.close()

    if not rows:
        return "No users found"

    return "\n".join([str(r) for r in rows])


@tool
def get_memory(key: str) -> str:
    """Retrieve memory"""

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT value FROM memory WHERE key=?",
        (key,)
    )

    row = cursor.fetchone()

    conn.close()

    if row:
        return row[0]

    return "No memory found"


TOOLS = {
    "add_user": add_user,
    "list_users": list_users,
    "get_memory": get_memory
}


# ============================================================
# LLM
# ============================================================

def get_llm():

    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=OPENAI_API_KEY,
        temperature=0
    )


# ============================================================
# UTIL
# ============================================================

def safe_parse_json(text):

    try:
        return json.loads(text)

    except Exception:

        try:
            start = text.find("{")
            end = text.rfind("}") + 1

            return json.loads(text[start:end])

        except Exception:
            return None


# ============================================================
# NODES
# ============================================================

def create_planner_node(llm):

    def planner_node(state: AgentState):

        messages = state["messages"]

        prompt = f"""
You are a planner.

Conversation history:
{messages}

Available actions:
- add_user(name, user_id)
- list_users()
- get_memory(key)

Examples:

"Add user Alice ML100"
-> {{"action":"add_user","args":{{"name":"Alice","user_id":"ML100"}}}}

"List users"
-> {{"action":"list_users","args":{{}}}}

"Who was the last user added?"
-> {{"action":"get_memory","args":{{"key":"last_user"}}}}

Return ONLY valid JSON.

User input:
{state['input']}
"""

        response = llm.invoke(prompt)

        content = response.content

        plan = safe_parse_json(content)

        if not plan:
            plan = {
                "action": "list_users",
                "args": {}
            }

        return {"plan": plan}

    return planner_node


def executor_node(state: AgentState):

    action = state["plan"].get("action")
    args = state["plan"].get("args", {})

    if action in TOOLS:

        try:
            result = TOOLS[action].invoke(args)

        except Exception as e:
            result = f"ERROR: {str(e)}"

    else:
        result = "ERROR: Unknown action"

    # SHORT TERM MEMORY
    new_messages = state["messages"] + [
        {
            "role": "user",
            "content": state["input"]
        },
        {
            "role": "assistant",
            "content": result
        }
    ]

    if "ERROR" in result:

        return {
            "result": result,
            "status": "ERROR",
            "messages": new_messages
        }

    return {
        "result": result,
        "status": "VALID",
        "messages": new_messages
    }


def create_validator_node(llm):

    def validator_node(state: AgentState):

        if state.get("status") == "ERROR":
            return {"status": "ERROR"}

        prompt = f"""
Validate result.

User: {state['input']}
Result: {state['result']}

Answer ONLY:
VALID or INVALID
"""

        response = llm.invoke(prompt)

        status = response.content.strip()

        if status not in ["VALID", "INVALID"]:
            status = "VALID"

        return {"status": status}

    return validator_node


# ============================================================
# ROUTER
# ============================================================

def route(state: AgentState):
    return END


# ============================================================
# GRAPH
# ============================================================

def build_graph(llm):

    graph = StateGraph(AgentState)

    graph.add_node(
        "planner",
        create_planner_node(llm)
    )

    graph.add_node(
        "executor",
        executor_node
    )

    graph.add_node(
        "validator",
        create_validator_node(llm)
    )

    graph.set_entry_point("planner")

    graph.add_edge("planner", "executor")

    graph.add_edge("executor", "validator")

    graph.add_conditional_edges(
        "validator",
        route
    )

    return graph.compile()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    setup_db()
    seed_data()

    llm = get_llm()

    app = build_graph(llm)

    state: AgentState = {
        "input": "",
        "plan": {},
        "result": "",
        "status": "",
        "messages": []
    }

    queries = [
        "Add user Sunil with id ML608",
        "Now list users",
        "Who was the last user added?"
    ]

    for q in queries:

        print("\n======================")
        print("USER:", q)

        state["input"] = q

        state = app.invoke(state)

        print("RESULT:", state["result"])