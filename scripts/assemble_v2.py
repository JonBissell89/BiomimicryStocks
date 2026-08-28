# -*- coding: utf-8 -*-
"""Assemble the v2 re-score, verify arithmetic, apply penalties, and compare
the two distributions before deciding anything about tiers."""
import os
from paths import DATA
import glob, json
import pandas as pd

D = DATA
COMP = ["A", "B", "C1", "C2", "D_rep", "D_inhib", "D_exit", "E", "F_clock", "F_now"]

frames = []
for f in sorted(glob.glob(os.path.join(D, "v2_scores_b*.csv"))):
    df = pd.read_csv(f, on_bad_lines="skip")
    df["batch"] = f[-6:-4]
    frames.append(df)
v2 = pd.concat(frames, ignore_index=True)
v2["ticker"] = v2.ticker.astype(str).str.upper().str.strip()
v2 = v2.drop_duplicates("ticker", keep="last")
for c in COMP + ["total"]:
    v2[c] = pd.to_numeric(v2[c], errors="coerce")

print(f"rows: {len(v2)}")
v2["calc"] = v2[COMP].sum(axis=1)
bad = v2[(v2.calc - v2.total).abs() > 0.5]
print(f"arithmetic errors: {len(bad)}")
for r in bad.itertuples():
    print(f"   {r.ticker}: stated {r.total} vs components {r.calc}")

eng = json.load(open(os.path.join(D, "engine_tiers.json"), encoding="utf-8"))
v1 = {n["tk"]: n for t in eng["tiers"] for n in t["names"]}
missing = [tk for tk in v1 if tk not in set(v2.ticker)]
print(f"engine names missing from v2: {len(missing)} {missing}")

# jurisdiction penalties carry over unchanged
JX = {tk: n.get("jx_penalty", 0) or 0 for tk, n in v1.items()}
v2["jx"] = v2.ticker.map(lambda t: JX.get(t, 0))
v2["v2_adj"] = v2["calc"] + v2["jx"]
v2["v1"] = v2.ticker.map(lambda t: v1[t]["score"] if t in v1 else None)
v2["delta"] = v2["v2_adj"] - v2["v1"]
v2["gate"] = v2["gate"].astype(str).str.lower().str.strip()

print()
print("DISTRIBUTION COMPARISON")
passed = v2[v2.gate.str.startswith("pass")]
print(f"  v1: mean {v2.v1.mean():.1f}  median {v2.v1.median():.0f}  range {v2.v1.min():.0f}-{v2.v1.max():.0f}")
print(f"  v2: mean {v2.v2_adj.mean():.1f}  median {v2.v2_adj.median():.0f}  range {v2.v2_adj.min():.0f}-{v2.v2_adj.max():.0f}")
print(f"  mean shift: {v2.delta.mean():+.1f} points   sd of shift: {v2.delta.std():.1f}")
print(f"  moved up: {(v2.delta>0).sum()}   moved down: {(v2.delta<0).sum()}   flat: {(v2.delta==0).sum()}")
print(f"  gate failures: {(~v2.gate.str.startswith('pass')).sum()} -> {list(v2[~v2.gate.str.startswith('pass')].ticker)}")
print()
print("  Correlation between v1 and v2 scores: "
      f"{v2['v1'].corr(v2['v2_adj']):.2f}  (low = the rubric really is measuring something different)")

# how much work each measure does now
print()
print("HOW MUCH WORK EACH v2 MEASURE DOES")
maxes = {"A": 20, "B": 25, "C1": 12, "C2": 8, "D_rep": 6, "D_inhib": 5, "D_exit": 4, "E": 10, "F_clock": 6, "F_now": 4}
for c in COMP:
    s = v2[c]
    print(f"   {c:9s} range {s.min():>2.0f}-{s.max():>2.0f} of {maxes[c]:>2}  "
          f"uses {100*(s.max()-s.min())/maxes[c]:>3.0f}%  sd {s.std():.2f}  r-with-total {s.corr(v2.calc):+.2f}")

v2.to_csv(os.path.join(D, "v2_assembled.csv"), index=False)
print()
print("saved v2_assembled.csv")
