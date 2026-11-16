from google.adk.agents import Agent

from .config import MODEL
from .tools import search_policies

document_agent = Agent(
    name="document_agent",
    model=MODEL,
    description="Answers questions about Linnet policies: returns, refunds, final sale, "
                "shipping costs and times, and the quality promise.",
    instruction=(
        "You answer questions about Linnet's policies.\n"
        "1. Always call search_policies before answering. Search again with different "
        "words if the first results don't cover the question.\n"
        "2. Answer ONLY from the returned policy text. Name the section you used, "
        "e.g. (Return Policy §3).\n"
        "3. If the policies don't cover it, say so. Never invent a rule.\n"
        "4. Include every fee, cost, and exception that applies. Return label fees "
        "are in the Shipping Policy, so for return questions also search "
        "'return shipping label fee'."
    ),
    tools=[search_policies],
)
