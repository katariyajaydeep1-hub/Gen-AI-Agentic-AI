"""
Upgraded agent with PERSISTENT long-term memory via pickle.
Uses OpenAI instead of Groq.
ERROR-FREE VERSION
"""

import os
import json
import sqlite3
from typing import TypedDict, List

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.graph import StateGraph, END

from memory_layer import (
    load_long_term_memory,
    save_long_term_memory,
    show_memory_summary,
)

# =============================================================================
# CONFIG
# =============================================================================

load_dotenv(dotenv_path="../.env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY missing in .env")

DB_FILE = "users.db"
MEMORY_FILE = "agent_memory.pkl"


# =============================================================================
# STATE
# =============================================================================

class AgentState(TypedDict):
    input: str
    plan: dict
    result: str
    status: str
    messages: List[dict]


# =============================================================================
# DATABASE
# =============================================================================

def setup_db():

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            authenticated INTEGER
        )
    """)

    conn.commit()
    conn.close()


def seed_data():

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.executemany(
        "INSERT OR IGNORE INTO users VALUES (?, ?, ?)",
        [
            ("ML001", "Raj", 1),
            ("ML002", "Ram", 0),
            ("ML003", "Sham", 1),
        ],
    )

    conn.commit()
    conn.close()


# =============================================================================
# TOOLS
# =============================================================================

@tool
def add_user(name: str, user_id: str) -> str:
    """Add a user to the database."""

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    try:

        # CHECK IF USER EXISTS
        cur.execute(
            "SELECT * FROM users WHERE id=?",
            (user_id,)
        )

        existing_user = cur.fetchone()

        if existing_user:
            return f"User with ID {user_id} already exists"

        # INSERT USER
        cur.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (user_id, name, 1),
        )

        conn.commit()

        return f"User {name} added with ID {user_id}"

    except Exception as e:
        return f"ERROR: {str(e)}"

    finally:
        conn.close()


@tool
def list_users() -> str:
    """List all users in the database."""

    conn = sqlite3.connect(DB_FILE)

    rows = conn.execute(
        "SELECT id, name, authenticated FROM users"
    ).fetchall()

    conn.close()

    if not rows:
        return "No users found"

    return "\n".join(str(r) for r in rows)


@tool
def recall(query: str) -> str:
    """Search long-term memory."""

    past = load_long_term_memory(MEMORY_FILE)

    matches = [
        m for m in past
        if query.lower() in str(m.get("content", "")).lower()
    ]

    if not matches:
        return f"No memory matching '{query}'."

    return "\n".join(
        f"[{m['role']}] {str(m['content'])[:120]}"
        for m in matches[-5:]
    )


TOOLS = {
    "add_user": add_user,
    "list_users": list_users,
    "recall": recall,
}


# =============================================================================
# OPENAI LLM
# =============================================================================

def get_llm():

    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=OPENAI_API_KEY,
        temperature=0,
    )


# =============================================================================
# UTIL
# =============================================================================

def safe_parse_json(text: str):

    try:
        return json.loads(text)

    except Exception:

        try:
            start = text.find("{")
            end = text.rfind("}") + 1

            return json.loads(text[start:end])

        except Exception:
            return None


# =============================================================================
# NODES
# =============================================================================

def create_planner_node(llm):

    def planner_node(state: AgentState):

        recent_context = state["messages"][-6:]

        prompt = f"""
You are a planner for a user-management agent.

Recent conversation context:
{recent_context}

Available actions:
- add_user(name, user_id)
- list_users()
- recall(query)

Examples:

"Add user Alice ML100"
-> {{"action":"add_user","args":{{"name":"Alice","user_id":"ML100"}}}}

"List users"
-> {{"action":"list_users","args":{{}}}}

"Did we add anyone named Sunil before?"
-> {{"action":"recall","args":{{"query":"Sunil"}}}}

Return ONLY valid JSON.

User input:
{state['input']}
"""

        response = llm.invoke(prompt)

        plan = safe_parse_json(response.content)

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
        result = f"ERROR: Unknown action '{action}'"

    # SHORT-TERM MEMORY UPDATE
    new_messages = state["messages"] + [
        {
            "role": "user",
            "content": state["input"],
        },
        {
            "role": "assistant",
            "content": result,
        },
    ]

    # SAVE LONG-TERM MEMORY
    save_long_term_memory(
        new_messages,
        MEMORY_FILE,
    )

    status = (
        "ERROR"
        if str(result).startswith("ERROR")
        else "VALID"
    )

    return {
        "result": result,
        "status": status,
        "messages": new_messages,
    }


def create_validator_node(llm):

    def validator_node(state: AgentState):

        if state.get("status") == "ERROR":
            return {"status": "ERROR"}

        prompt = f"""
Validate this result.

User:
{state['input']}

Result:
{state['result']}

Reply ONLY:
VALID or INVALID
"""

        response = llm.invoke(prompt)

        status = response.content.strip()

        if status not in ["VALID", "INVALID"]:
            status = "VALID"

        return {"status": status}

    return validator_node


# =============================================================================
# GRAPH
# =============================================================================

def build_graph(llm):

    g = StateGraph(AgentState)

    g.add_node(
        "planner",
        create_planner_node(llm)
    )

    g.add_node(
        "executor",
        executor_node
    )

    g.add_node(
        "validator",
        create_validator_node(llm)
    )

    g.set_entry_point("planner")

    g.add_edge("planner", "executor")

    g.add_edge("executor", "validator")

    g.add_conditional_edges(
        "validator",
        lambda s: END
    )

    return g.compile()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":

    setup_db()
    seed_data()

    # LOAD MEMORY
    past_messages = load_long_term_memory(MEMORY_FILE)

    print(
        f"\n[memory] Loaded {len(past_messages)} messages from previous runs.\n"
    )

    llm = get_llm()

    app = build_graph(llm)

    state: AgentState = {
        "input": "",
        "plan": {},
        "result": "",
        "status": "",
        "messages": past_messages,
    }

    queries = [
        "Add user Sunil with id ML608",
        "Now list users",
        "Who did we just add?",
        "Did we ever add anyone named Sunil?",
    ]

    for q in queries:

        print("\n======================")
        print("USER:", q)

        state["input"] = q

        state = app.invoke(state)

        print("RESULT:", state["result"])

    print("\n======================")
    print("FINAL MEMORY SUMMARY")
    print("======================")

    show_memory_summary(MEMORY_FILE)