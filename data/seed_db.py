"""Build data/orders.db, Linnet's "legacy" orders database.

The schema imitates a 10-year-old system: cryptic uppercase column names,
status codes instead of words, and dates stored as text.
"""
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

DB = Path(__file__).parent / "orders.db"

PRODUCTS = [
    ("Sunday Morning Maxi Dress", "dresses", 148.00),
    ("Crochet Festival Top", "tops", 78.00),
    ("Vintage-Wash Flare Jeans", "denim", 128.00),
    ("Lace Bralette", "intimates", 48.00),                  # final sale (hygiene)
    ("Turquoise Drop Earrings", "jewelry", 38.00),          # final sale by POLICY, not DB flag
    ("One-of-a-Kind Vintage Suede Jacket", "vintage", 225.00),  # final sale
    ("Patchwork Duster Cardigan", "sweaters", 168.00),
]

# Categories the old system flags as final sale. Earrings are deliberately NOT
# flagged here: the agent has to read the return policy to catch them.
FINAL_SALE_CATS = {"intimates", "vintage"}

SNAPSHOT_DATE = date(2026, 11, 13)  # fixed so the data is identical every run


def main():
    random.seed(42)  # same data every run = reproducible evals
    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE ORD_HDR (
        ORD_NO     INTEGER PRIMARY KEY,
        CUST_ID    INTEGER,
        ORD_DT     TEXT,
        ITEM_DESC  TEXT,
        ITEM_CAT   TEXT,
        AMT        REAL,
        STATUS_CD  TEXT,
        FINAL_SALE INTEGER)""")

    # The example question: customer 1042's maxi dress from October.
    rows = [(5001, 1042, "2026-10-22", "Sunday Morning Maxi Dress", "dresses", 148.00, "DLV", 0)]

    for i in range(49):
        name, cat, amt = random.choice(PRODUCTS)
        d = SNAPSHOT_DATE - timedelta(days=random.randint(1, 400))
        rows.append((
            5002 + i,
            random.randint(1000, 1060),
            d.isoformat(),
            name,
            cat,
            amt,
            random.choice(["DLV", "SHP", "CXL"]),
            int(cat in FINAL_SALE_CATS),
        ))

    con.executemany("INSERT INTO ORD_HDR VALUES (?,?,?,?,?,?,?,?)", rows)
    con.commit()
    con.close()
    print(f"Wrote {len(rows)} orders to {DB}")


if __name__ == "__main__":
    main()
