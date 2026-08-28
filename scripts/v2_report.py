# -*- coding: utf-8 -*-
import os
from paths import DATA
import pandas as pd
D = DATA
v = pd.read_csv(os.path.join(D, "v2_assembled.csv"))
v = v.sort_values("v2_adj", ascending=False)

def show(df, cols, w=None):
    for r in df.itertuples():
        print(f"  {r.v2_adj:>5.0f}  {r.v1:>3.0f} {r.delta:>+5.0f}  {r.ticker:<7s} "
              f"{str(r.loop)[:9]:<10s} {str(r.coupling)[:9]:<10s} {str(r.clock_label)[:24]:<25s}")

print("FULL RANKING (v2 adj | v1 | delta | ticker | loop | coupling | clock)")
print("-" * 88)
show(v, None)

print()
print("BIGGEST FALLS")
print("-" * 88)
show(v.nsmallest(10, "delta"), None)
print()
print("RISERS")
print("-" * 88)
show(v[v.delta > 0].sort_values("delta", ascending=False), None)

print()
print("COUPLING LABEL DISTRIBUTION (the measure v1 did not have at all)")
print(v.coupling.astype(str).str.strip().str.lower().value_counts().to_string())
print()
print("LOOP SIGN DISTRIBUTION")
print(v.loop.astype(str).str.strip().str.lower().value_counts().to_string())

print()
print("PERCENTILE CUTS on the new scale (equal-count bands matching old tier sizes)")
import json
eng = json.load(open(os.path.join(D, "engine_tiers.json"), encoding="utf-8"))
sizes = [(t["id"], len(t["names"])) for t in eng["tiers"]]
print("  old tier sizes:", sizes)
run = 0
for tid, n in sizes:
    band = v.iloc[run:run + n]
    if len(band):
        print(f"  {tid}: n={n:<3d} v2 range {band.v2_adj.min():.0f}-{band.v2_adj.max():.0f}")
    run += n
print()
for q in [90, 80, 70, 60, 50, 40, 25]:
    print(f"  p{q}: {v.v2_adj.quantile(q/100):.1f}")
