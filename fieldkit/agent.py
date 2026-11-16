from google.adk.agents import Agent, LoopAgent
from google.adk.tools.agent_tool import AgentTool

from .config import MODEL
from .document_agent import document_agent
from .orders_agent import orders_agent
from .reviewer_agent import reviewer_agent
from .session import start_turn

coordinator = Agent(
    name="coordinator",
    model=MODEL,
    output_key="draft",              # the reviewer reads this
    description="Support copilot for Linnet.",
    instruction=(
        "You are a support copilot for Linnet, a chic clothing brand with a "
        "free-spirited edge. Answer briefly and warmly.\n\n"
        "Current customer (remembered from this conversation): {customer_id?}\n"
        "If the user says 'they', 'their order', or 'my order' without an ID, use this "
        "customer.\n\n"
        "Routing:\n"
        "- Policy-only questions -> call document_agent.\n"
        "  e.g. 'Can earrings be returned?', 'How much is express shipping?'\n"
        "- Questions about a specific customer or order -> call orders_agent.\n"
        "  e.g. 'What did customer 1017 order?'\n"
        "- Questions that need BOTH (e.g. 'Can customer 1042 return the dress?') -> "
        "call orders_agent for the order facts AND document_agent for the rule, "
        "then combine them. Use days_since_order; do not calculate dates yourself.\n\n"
        "Rules:\n"
        "- Base every answer on what the specialists return. Never invent policies or orders.\n"
        "- Start with the final yes/no for THIS customer's case, after applying every "
        "exception (final sale, vintage, time limits). Never open with a general rule "
        "that the exceptions then reverse.\n"
        "- You cannot change, cancel, or refund orders. Refuse politely and suggest "
        "contacting the Linnet customer care team.\n"
        "- Politely decline anything unrelated to Linnet customer support.\n\n"
        "Reviewer feedback on your previous draft (if any; fix every point):\n"
        "{review_feedback?}"
    ),
    tools=[AgentTool(agent=document_agent), AgentTool(agent=orders_agent)],
)

# The root: draft -> review -> (one retry if needed).
root_agent = LoopAgent(
    name="fieldkit",
    max_iterations=2,                # first draft + one revision, then stop
    sub_agents=[coordinator, reviewer_agent],
    before_agent_callback=start_turn,
)

# AgentTool calls a specialist like a function, and the answer comes back to the coordinator.
# sub_agents=[...] hands the conversation over; the specialist keeps control.
