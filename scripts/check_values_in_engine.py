# -*- coding: utf-8 -*-
"""Is the health 'embedded vs pushback' judgment already priced by the v2 engine?

The owner's ruling: that distinction belongs in the engine, not in a UI filter.
Under v2 the natural home is C2 coupling. 'Embedded' means the economics depend on
premium reimbursement inside the existing payment machine, which is exactly the
question C2 asks: does the revenue survive if the system rebalances?
So: check whether embedded names already score low on C2. If they do, the engine
prices it and the tag is only a label. If they do not, the ruling is unapplied.
"""
import os
from paths import DATA
import json, statistics as st
D = DATA
eng = json.load(open(os.path.join(D, "engine_tiers.json"), encoding="utf-8"))
names = [n for t in eng["tiers"] for n in t["names"]]

grp = {}
for n in names:
    v = (n.get("values") or "none").strip().lower()
    grp.setdefault(v, []).append(n)

print("values tag -> C2 coupling, C1 loop, and total")
for k in sorted(grp):
    g = grp[k]
    print(f"  {k:<10s} n={len(g):<3d} "
          f"C2 mean {st.mean(n['dims']['C2'] for n in g):.1f}  "
          f"C1 mean {st.mean(n['dims']['C1'] for n in g):.1f}  "
          f"total mean {st.mean(n['score'] for n in g):.1f}")

print("\nEvery health name, C2 and coupling label:")
for n in sorted(names, key=lambda x: -x["dims"]["C2"]):
    v = (n.get("values") or "").strip().lower()
    if v in ("embedded", "pushback"):
        print(f"  {n['tk']:<7s} {v:<9s} C2={n['dims']['C2']}  "
              f"coupling={n['coupling']:<9s} C1={n['dims']['C1']:<3d} total={n['score']}")

emb = [n for n in names if (n.get("values") or "").lower() == "embedded"]
pb = [n for n in names if (n.get("values") or "").lower() == "pushback"]
if emb and pb:
    print(f"\n  embedded C2 mean {st.mean(n['dims']['C2'] for n in emb):.2f} "
          f"vs pushback C2 mean {st.mean(n['dims']['C2'] for n in pb):.2f}")
    print(f"  embedded total   {st.mean(n['score'] for n in emb):.1f} "
          f"vs pushback total   {st.mean(n['score'] for n in pb):.1f}")
