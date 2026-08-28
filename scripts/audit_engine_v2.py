# -*- coding: utf-8 -*-
"""Validate the rebuilt v2 engine: arithmetic, provenance, text hygiene,
and whether the philosophy's own claims survive contact with the scores."""
import os
from paths import DATA
import json, re
D = DATA
eng = json.load(open(os.path.join(D, "engine_tiers.json"), encoding="utf-8"))
names = [n for t in eng["tiers"] for n in t["names"]]
COMP = ["A", "B", "C1", "C2", "D_rep", "D_inhib", "D_exit", "E", "F_clock", "F_now"]
MAX = {"A": 20, "B": 25, "C1": 12, "C2": 8, "D_rep": 6, "D_inhib": 5, "D_exit": 4,
       "E": 10, "F_clock": 6, "F_now": 4}

print(f"names: {len(names)}   tiers: {[t['id'] for t in eng['tiers']]}")

err = 0
for n in names:
    d = n["dims"]
    s = sum(d.values())
    if s != n["score_base"]:
        print(f"  ARITH {n['tk']}: dims sum {s} != score_base {n['score_base']}"); err += 1
    if n["score_base"] + n["jx_penalty"] != n["score"]:
        print(f"  JX    {n['tk']}: base {n['score_base']} + jx {n['jx_penalty']} != {n['score']}"); err += 1
    for k, mx in MAX.items():
        if not (0 <= d[k] <= mx):
            print(f"  RANGE {n['tk']}: {k}={d[k]} outside 0-{mx}"); err += 1
    for f in ("stock", "loop", "coupling", "evidence"):
        if not str(n.get(f, "")).strip():
            print(f"  EMPTY {n['tk']}: {f} is blank"); err += 1
print(f"arithmetic / range / completeness errors: {err}")

# tier bands honoured
band = lambda s: "t1" if s >= 80 else "t2" if s >= 74 else "t3" if s >= 69 else "t4" if s >= 65 else "exit"
mis = [(n["tk"], t["id"], band(n["score"])) for t in eng["tiers"] for n in t["names"]
       if band(n["score"]) != t["id"]]
print(f"tier band violations: {len(mis)} {mis}")

# text hygiene
blob = json.dumps(eng, ensure_ascii=False)
print(f"em dashes in engine text: {blob.count(chr(8212))}")
moral = [w for w in ["good company", "bad company", "good investment", "bad investment",
                     "philosophically good", "morally"] if w in blob.lower()]
print(f"moral language found: {moral if moral else 'none'}")

# does the philosophy hold up in the numbers?
print("\nDOES THE SCORECARD BEHAVE AS THE PHILOSOPHY CLAIMS?")
import statistics as st
def mean(f, sel=lambda n: True):
    xs = [f(n) for n in names if sel(n)]
    return sum(xs) / len(xs) if xs else 0

cs = {"survives": [], "neutral": [], "shrinks": []}
for n in names:
    k = str(n["coupling"]).strip().lower()
    if k in cs:
        cs[k].append(n["score"])
print("  coupling label vs mean score (claim: revenue that survives a rebalance ranks higher)")
for k in ["survives", "neutral", "shrinks"]:
    if cs[k]:
        print(f"     {k:<9s} n={len(cs[k]):<3d} mean {st.mean(cs[k]):.1f}")

ls = {}
for n in names:
    ls.setdefault(str(n["loop"]).strip().lower(), []).append(n["score"])
print("  loop sign vs mean score (claim: self-damping ranks higher than amplifying)")
for k in ["damping", "neutral", "amplifying", "runaway"]:
    if k in ls:
        print(f"     {k:<10s} n={len(ls[k]):<3d} mean {st.mean(ls[k]):.1f}")

# the moat inversion: is high defensibility now a cost rather than a credit?
pen = [n for n in names if n["dims"]["A"] <= 13]
print(f"\n  names carrying a low stock score (A<=13): {len(pen)} -> "
      f"{[n['tk'] for n in pen]}")
print(f"  their mean total {st.mean([n['score'] for n in pen]):.1f} vs "
      f"all-names mean {st.mean([n['score'] for n in names]):.1f}")
