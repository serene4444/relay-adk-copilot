from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .document_agent import document_agent

root_agent = Agent(
    name="coordinator",
    model="gemini-3.8-flash",
    description="Support copilot for Linnet.",
    instruction=(
        "You are a support copilot for Linnet, a chic clothing brand with a "
        "free-spirited edge. Answer briefly and warmly.\n"
        "For any question about policies (returns, shipping, defects), call "
        "document_agent and base your answer on what it returns.\n"
        "If a request is unrelated to Linnet customer support, politely decline."
    ),
    tools=[AgentTool(agent=document_agent)],
)

#AgentTool calls the specialist like a function, and the answer comes back to the coordinator.

#sub_agents=[...] hands the conversation over. The specialist takes control and doesn't return it to the coordinator.
