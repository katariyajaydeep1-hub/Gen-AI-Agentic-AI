"""
Long-term memory layer for the agent.
Uses Python's built-in pickle module to serialize the messages list
to disk so the agent remembers past conversations across runs.
"""
import os
import pickle
from typing import List

DEFAULT_MEMORY_FILE = "agent_memory.pkl"
MAX_MESSAGES = 100   # rolling window — keep only the last 100 messages


def save_long_term_memory(messages: List[dict],
                          filepath: str = DEFAULT_MEMORY_FILE) -> None:
    """Pickle the messages list to disk.

    Keeps only the last MAX_MESSAGES so the file doesn't grow forever.
    """
    trimmed = messages[-MAX_MESSAGES:] if len(messages) > MAX_MESSAGES else messages
    try:
        with open(filepath, "wb") as f:
            pickle.dump(trimmed, f)
    except Exception as e:
        print(f"[memory] Failed to save: {e}")


def load_long_term_memory(filepath: str = DEFAULT_MEMORY_FILE) -> List[dict]:
    """Load pickled messages from disk. Returns [] if no file or corrupted."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "rb") as f:
            messages = pickle.load(f)
        if not isinstance(messages, list):
            return []
        return messages
    except (pickle.UnpicklingError, EOFError) as e:
        print(f"[memory] Corrupted memory file ({e}). Starting fresh.")
        return []
    except Exception as e:
        print(f"[memory] Failed to load: {e}")
        return []


def clear_long_term_memory(filepath: str = DEFAULT_MEMORY_FILE) -> None:
    """Delete the memory file. Useful for testing or resetting."""
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"[memory] Cleared {filepath}")


def show_memory_summary(filepath: str = DEFAULT_MEMORY_FILE) -> None:
    """Print a summary of what's currently in long-term memory."""
    messages = load_long_term_memory(filepath)
    if not messages:
        print("[memory] No long-term memory found.")
        return
    print(f"[memory] {len(messages)} messages stored in {filepath}:")
    for i, msg in enumerate(messages[-10:], 1):  # last 10
        role = msg.get("role", "?")
        content = str(msg.get("content", ""))[:80]
        print(f"  {i:2}. [{role}] {content}")
