import os
import sys
from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

from .config import MODEL

SERVER = Path(__file__).resolve().parent.parent / "mcp_server" / "orders_server.py"

# ADK launches the MCP server as a subprocess and talks to it over stdio.
orders_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,          # same Python as the venv
            args=[str(SERVER)],
            env=dict(os.environ),            # passes FIELDKIT_TODAY through
        ),
        timeout=30,
    ),
    tool_filter=["get_customer_orders", "get_order"],   # allow-list
)

orders_agent = Agent(
    name="orders_agent",
    model=MODEL,
    description="Looks up Linnet customer orders: what they bought, when, the price, "
                "the status, and how many days ago it was ordered.",
    instruction=(
        "You look up orders in Linnet's order system.\n"
        "1. Use get_customer_orders for a customer ID, or get_order for an order number.\n"
        "2. Report the facts exactly as returned: item, order date, days_since_order, "
        "status, and flagged_final_sale.\n"
        "3. If the customer or order is not found, say so plainly. Never guess.\n"
        "4. You are READ-ONLY. You cannot change, cancel, or refund orders. If asked, "
        "say that this has to go through a human on the customer care team."
    ),
    tools=[orders_tools],
)
