from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .config import MODEL
from .document_agent import document_agent
from .orders_agent import orders_agent

root_agent = Agent(
    name="coordinator",
    model=MODEL,
    description="Support copilot for Linnet.",
    instruction=(
        "You are a support copilot for Linnet, a chic clothing brand with a "
        "free-spirited edge. Answer briefly and warmly.\n\n"
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
        "- You cannot change, cancel, or refund orders. Refuse politely and suggest "
        "contacting the Linnet customer care team.\n"
        "- Politely decline anything unrelated to Linnet customer support."
    ),
    tools=[AgentTool(agent=document_agent), AgentTool(agent=orders_agent)],
)

#AgentTool calls the specialist like a function, and the answer comes back to the coordinator.

#sub_agents=[...] hands the conversation over. The specialist takes control and doesn't return it to the coordinator.
