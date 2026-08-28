# -*- coding: utf-8 -*-
import os
from paths import DATA
import pandas as pd, textwrap
D = DATA
v = pd.read_csv(os.path.join(D, "v2_assembled.csv")).sort_values("v2_adj", ascending=False)
v["g"] = v.gate.astype(str).str.lower().str.strip()

print("GATE FAILURES")
for r in v[~v.g.str.startswith("pass")].itertuples():
    print(f"\n  {r.ticker}  score {r.v2_adj:.0f} (would rank #{list(v.ticker).index(r.ticker)+1})")
    print("     gate: " + str(r.gate)[:300])
    print("     note: " + textwrap.shorten(str(r.note), 260))

print("\n\nGATE REASONS THAT ARE NOT A BARE 'PASS' (flagged conditions on passing names)")
for r in v[v.g.str.startswith("pass")].itertuples():
    g = str(r.gate)
    if len(g) > 12:
        print(f"  {r.ticker:<7s} {g[:120]}")

print("\n\nTIER ASSIGNMENT under the EXISTING bands (T1>=80, T2 74-79, T3 69-73, exit <65)")
def band(s):
    return "T1" if s >= 80 else "T2" if s >= 74 else "T3" if s >= 69 else "T4" if s >= 65 else "EXIT"
v["newtier"] = v.v2_adj.map(band)
for t in ["T1", "T2", "T3", "T4", "EXIT"]:
    sub = v[v.newtier == t]
    gated = [f"{r.ticker}*" if not str(r.g).startswith("pass") else r.ticker for r in sub.itertuples()]
    print(f"  {t:<5s} n={len(sub):<3d}  {' '.join(gated)}")
print("  (* = gate failure, excluded from investable set regardless of score)")
