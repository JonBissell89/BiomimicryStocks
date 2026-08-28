# -*- coding: utf-8 -*-
"""Audit: does the engine's actual behaviour match the stated philosophy?"""
import os
from paths import DATA
import pandas as pd

D = DATA
r4 = pd.read_csv(os.path.join(D, "round4_results.csv"))
adv = r4[r4.verdict.str.upper().str.strip() == "ADVANCE"].copy()
cols = ["permanent_need", "system_balance", "cost_compression", "moat",
        "proven_functions", "scale_velocity", "expansion_signal", "survivability"]
for c in cols:
    adv[c] = pd.to_numeric(adv[c], errors="coerce")
adv["total_n"] = pd.to_numeric(adv["total"], errors="coerce")
adv = adv.dropna(subset=cols + ["total_n"])

print("A. HOW MUCH WORK EACH DIMENSION ACTUALLY DOES")
print("   (a dimension with no spread cannot rank anything)")
maxes = dict(zip(cols, [15, 15, 15, 15, 10, 10, 10, 10]))
for c in cols:
    v = adv[c]
    used = (v.max() - v.min()) / maxes[c]
    print(f"   {c:18s} range {v.min():>2.0f}-{v.max():>2.0f} of {maxes[c]:>2}"
          f"  uses {used*100:>3.0f}% of its scale   sd {v.std():.2f}   r-with-total {v.corr(adv.total_n):+.2f}")

print()
print("B. WHAT IF THE WEIGHTS MATCHED THE STATED PHILOSOPHY?")
# philosophy-true weighting: balance and cost compression lead; moat is a durability
# check on the balancing function, not the main event; clock instruments raised.
NEW = {"permanent_need": 15, "system_balance": 20, "cost_compression": 20, "moat": 10,
       "proven_functions": 5, "scale_velocity": 10, "expansion_signal": 10, "survivability": 10}
OLD = {"permanent_need": 15, "system_balance": 15, "cost_compression": 15, "moat": 15,
       "proven_functions": 10, "scale_velocity": 10, "expansion_signal": 10, "survivability": 10}
adv["rescored"] = sum(adv[c] / OLD[c] * NEW[c] for c in cols)
a = adv.sort_values("total_n", ascending=False).reset_index(drop=True)
b = adv.sort_values("rescored", ascending=False).reset_index(drop=True)
rank_now = {t: i + 1 for i, t in enumerate(a.ticker)}
rank_new = {t: i + 1 for i, t in enumerate(b.ticker)}
adv["move"] = adv.ticker.map(lambda t: rank_now[t] - rank_new[t])
print("   Biggest RISERS under philosophy-true weights:")
for r in adv.sort_values("move", ascending=False).head(6).itertuples():
    print(f"     {r.ticker:6s} #{rank_now[r.ticker]:>2} -> #{rank_new[r.ticker]:<2}  "
          f"(bal {r.system_balance:.0f}, cost {r.cost_compression:.0f}, moat {r.moat:.0f})")
print("   Biggest FALLERS:")
for r in adv.sort_values("move").head(6).itertuples():
    print(f"     {r.ticker:6s} #{rank_now[r.ticker]:>2} -> #{rank_new[r.ticker]:<2}  "
          f"(bal {r.system_balance:.0f}, cost {r.cost_compression:.0f}, moat {r.moat:.0f})")
same_top10 = len(set(a.ticker.head(10)) & set(b.ticker.head(10)))
print(f"   Top 10 overlap between current and philosophy-true ranking: {same_top10}/10")

print()
print("C. THE MOAT CONTRADICTION, NAMED")
hi = adv[(adv.moat >= 13)]
print(f"   {len(hi)} names score 13+ on moat. A moat means the system CANNOT route around them,")
print("   which is concentration, the opposite of the distributed resilience the philosophy prizes.")
print("   Names where high moat coincides with weaker balance:")
for r in adv[(adv.moat >= 13) & (adv.system_balance <= 11)].itertuples():
    print(f"     {r.ticker:6s} moat {r.moat:.0f} vs balance {r.system_balance:.0f}  (total {r.total_n:.0f})")
