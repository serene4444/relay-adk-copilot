from google.adk.agents import Agent

root_agent = Agent(
    name="coordinator",
    model="gemini-2.5-flash",
    description="Support copilot for Lone Star Outfitters.",
    instruction="You are a support copilot for Lone Star Outfitters, an outdoor retailer. "
                "Answer briefly. If you don't know, say so.",
)
