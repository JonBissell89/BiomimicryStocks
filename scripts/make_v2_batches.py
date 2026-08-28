# -*- coding: utf-8 -*-
from paths import DATA
import os
import pandas as pd

D = DATA
B = os.path.join(D, "v2_batches")
os.makedirs(B, exist_ok=True)
df = pd.read_csv(os.path.join(D, "v2_inputs.csv")).sort_values("score_v1", ascending=False).reset_index(drop=True)

def money(x):
    try:
        x = float(x)
    except Exception:
        return "?"
    for u, d in (("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(x) >= d:
            return f"${x/d:,.2f}{u}"
    return f"${x:,.0f}"

SIZE = 7
n = 0
for i in range(0, len(df), SIZE):
    n += 1
    chunk = df.iloc[i:i + SIZE]
    with open(os.path.join(B, f"batch_{n:02d}.txt"), "w", encoding="utf-8") as f:
        for r in chunk.itertuples():
            f.write(f"=== {r.ticker} | {r.name} | v1 score {r.score_v1} | tier {r.tier} | need: {r.need}\n")
            f.write(f"    data source for financials: {r.src}\n")
            f.write(f"    revenue {money(r.revenue)} | growth {r.rev_growth} | gross margin {r.gross_margin} | "
                    f"op margin {r.op_margin}\n")
            f.write(f"    FCF {money(r.fcf)} | cash {money(r.cash)} | debt {money(r.debt)} | "
                    f"net cash {money(getattr(r,'net_cash',None))}\n")
            f.write(f"    GATE hint, funding: {r.gate_funding}\n")
            f.write(f"    GATE hint, dilution: {getattr(r,'gate_dilution','unknown')}\n")
            f.write(f"    (both GATE lines are HINTS from a price API and have been wrong in both "
                    f"directions. Verify against the filing before passing or failing.)\n")
            f.write(f"    D-inhibition proxy: {r.d_inhibition_proxy}\n")
            f.write(f"    capital/revenue {getattr(r,'capital_per_revenue','?')} | "
                    f"revenue per employee {getattr(r,'rev_per_employee','?')} | employees {r.employees}\n")
            s = str(r.summary).replace("\n", " ")[:600]
            f.write(f"    business: {s}\n\n")
print(f"{n} batches written to {B}")
