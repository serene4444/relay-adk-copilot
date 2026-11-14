from google.adk.agents import Agent
from google.adk.tools import ToolContext

from .config import MODEL


def approve_answer(tool_context: ToolContext) -> dict:
    """Approve the draft: it is accurate, grounded in the sources, and safe."""
    tool_context.state["review_verdict"] = "approved"
    tool_context.actions.escalate = True              # stops the review loop
    tool_context.actions.skip_summarization = True    # no extra model call afterward
    return {"status": "approved"}


def request_revision(problems: str, tool_context: ToolContext) -> dict:
    """Send the draft back to the coordinator to fix.

    Args:
        problems: Exactly what is wrong, and what the sources actually say.
    """
    tool_context.state["review_feedback"] = problems
    tool_context.state["review_verdict"] = "sent_back"
    tool_context.state["revisions"] = tool_context.state.get("revisions", 0) + 1
    tool_context.actions.skip_summarization = True
    return {"status": "sent back for revision"}


reviewer_agent = Agent(
    name="reviewer_agent",
    model=MODEL,
    description="Checks every draft answer for accuracy and safety before it goes out.",
    instruction=(
        "You are a strict quality reviewer for Linnet support answers. "
        "You never talk to the customer.\n\n"
        "DRAFT ANSWER:\n{draft?}\n\n"
        "POLICY SOURCES RETRIEVED:\n{policy_sources?}\n\n"
        "ORDER FACTS RETRIEVED:\n{order_facts?}\n\n"
        "Check the draft:\n"
        "1. Accuracy: every rule, number, date, and item matches the sources above.\n"
        "2. Grounded: any policy it states appears in the policy sources. Nothing invented.\n"
        "3. Correct decision: the yes/no matches the rule. For returns, compare "
        "days_since_order with the 30-day and 45-day windows, and check final sale.\n"
        "4. Safe: it never claims an order was changed, cancelled, or refunded.\n"
        "Polite refusals of off-topic or data-changing requests, and 'customer not "
        "found' answers, are correct. Approve them.\n\n"
        "Then call exactly ONE tool: approve_answer if every check passes, otherwise "
        "request_revision listing the specific problems. Write no other text."
    ),
    tools=[approve_answer, request_revision],
)
