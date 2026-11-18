from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")

class State(TypedDict, total=False):
    question: str
    customer_id: str          # survives across turns via the checkpointer
    needs: list[str]          # ["orders", "docs"]
    order_facts: str
    policy_sources: str
    draft: str
    feedback: str
    revisions: int
    verdict: str

def route(state: State) -> dict:
    # Ask the LLM (structured output) which specialists the question needs,
    # or "refuse" for out-of-scope / write requests.
    ...

def orders(state: State) -> dict:
    # Call get_customer_orders / get_order through langchain-mcp-adapters
    # against the SAME mcp_server/orders_server.py.
    ...

def docs(state: State) -> dict:
    # Reuse the Chroma query from fieldkit/tools.py.
    ...

def draft(state: State) -> dict:
    # Same rules as the ADK coordinator prompt, plus {feedback} if any.
    ...

def review(state: State) -> dict:
    # Same checks as reviewer_agent; returns verdict + feedback, revisions += 1.
    ...

def after_route(state: State) -> list[str] | Literal["refuse"]:
    return state["needs"] or "refuse"          # list -> runs branches in parallel

def after_review(state: State) -> Literal["draft", "__end__"]:
    if state["verdict"] == "sent_back" and state.get("revisions", 0) < 2:
        return "draft"
    return END

g = StateGraph(State)
for name, fn in [("route", route), ("orders", orders), ("docs", docs),
                 ("draft", draft), ("review", review), ("refuse", draft)]:
    g.add_node(name, fn)
g.add_edge(START, "route")
g.add_conditional_edges("route", after_route, ["orders", "docs", "refuse"])
g.add_edge("orders", "draft")
g.add_edge("docs", "draft")
g.add_edge("draft", "review")
g.add_conditional_edges("review", after_review, ["draft", END])
g.add_edge("refuse", END)

app = g.compile(checkpointer=MemorySaver())
# app.invoke({"question": q}, config={"configurable": {"thread_id": "session-1"}})
