"""Per-turn state handling: runs once at the start of every user message."""
import re

from google.adk.agents.callback_context import CallbackContext

# "customer 1042", "customer ID 1017", "Customer #9999"
CUSTOMER_ID = re.compile(r"\bcustomer\s*(?:id\s*)?#?\s*(\d{3,6})\b", re.IGNORECASE)

# Scratch values for ONE question. Cleared each turn so the reviewer never
# checks a new answer against the previous question's sources.
PER_TURN_KEYS = ("draft", "policy_sources", "order_facts", "review_feedback", "review_verdict")


def start_turn(callback_context: CallbackContext) -> None:
    state = callback_context.state
    for key in PER_TURN_KEYS:
        state[key] = ""
    state["revisions"] = 0

    # customer_id is NOT cleared. It survives across turns, so follow-ups work.
    content = callback_context.user_content
    text = "".join(p.text or "" for p in (content.parts or [])) if content else ""
    match = CUSTOMER_ID.search(text)
    if match:
        state["customer_id"] = match.group(1)
