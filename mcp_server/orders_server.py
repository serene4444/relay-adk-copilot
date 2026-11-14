"""Read-only MCP server over Linnet's legacy orders database."""
import os
import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

DB_PATH = Path(os.environ.get(
    "ORDERS_DB", Path(__file__).resolve().parent.parent / "data" / "orders.db"))

# The legacy system stores status codes; translate them for the agent.
STATUS = {"DLV": "delivered", "SHP": "shipped, in transit", "CXL": "cancelled"}

# Tells MCP clients these tools never change anything.
READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False)

server = MCPServer(name="linnet-orders", instructions="Read-only lookups of Linnet orders.")


def _today() -> date:
    """FIELDKIT_TODAY pins the date so evaluation results are reproducible."""
    fixed = os.environ.get("FIELDKIT_TODAY")
    return date.fromisoformat(fixed) if fixed else date.today()


def _connect() -> sqlite3.Connection:
    # mode=ro: SQLite itself refuses every write. This is the security boundary.
    con = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def _clean(row: sqlite3.Row) -> dict:
    """Translate one legacy row into clear field names."""
    ordered = date.fromisoformat(row["ORD_DT"])
    return {
        "order_number": row["ORD_NO"],
        "customer_id": row["CUST_ID"],
        "order_date": row["ORD_DT"],
        "days_since_order": (_today() - ordered).days,
        "item": row["ITEM_DESC"],
        "category": row["ITEM_CAT"],
        "amount_usd": row["AMT"],
        "status": STATUS.get(row["STATUS_CD"], row["STATUS_CD"]),
        "flagged_final_sale": bool(row["FINAL_SALE"]),
    }


@server.tool(annotations=READ_ONLY)
def get_customer_orders(customer_id: int) -> dict:
    """List every order for one customer, newest first."""
    with closing(_connect()) as con:   # closing() actually closes the connection
        rows = con.execute(
            "SELECT * FROM ORD_HDR WHERE CUST_ID = ? ORDER BY ORD_DT DESC",
            (customer_id,)).fetchall()
    if not rows:
        return {"found": False, "message": f"No customer with ID {customer_id} has any orders."}
    return {"found": True, "today": _today().isoformat(), "orders": [_clean(r) for r in rows]}


@server.tool(annotations=READ_ONLY)
def get_order(order_number: int) -> dict:
    """Look up one order by its order number."""
    with closing(_connect()) as con:
        row = con.execute("SELECT * FROM ORD_HDR WHERE ORD_NO = ?", (order_number,)).fetchone()
    if row is None:
        return {"found": False, "message": f"No order number {order_number}."}
    return {"found": True, "today": _today().isoformat(), "order": _clean(row)}


if __name__ == "__main__":
    server.run()   # stdio transport: ADK starts this file as a subprocess
