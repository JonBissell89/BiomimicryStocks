# -*- coding: utf-8 -*-
"""Derive a market class per name from the ticker shape, and sanity-check it
against the empirically-set sofi flags before it replaces the SoFi toggle."""
import os
from paths import DATA
import json
D = DATA
eng = json.load(open(os.path.join(D, "engine_tiers.json"), encoding="utf-8"))
names = [n for t in eng["tiers"] for n in t["names"]]

def market(tk):
    if len(tk) == 5 and tk.endswith("F"):
        return "ord"   # OTC foreign ordinary
    if len(tk) == 5 and tk.endswith("Y"):
        return "adr"   # OTC depositary receipt
    return "us"        # NYSE / NASDAQ / NYSE American

g = {}
for n in names:
    g.setdefault(market(n["tk"]), []).append(n)
for k in ("us", "adr", "ord"):
    v = g.get(k, [])
    print(f"{k:<4s} n={len(v):<3d} sofi-true={sum(1 for n in v if n.get('sofi')):<3d}  "
          f"{' '.join(n['tk'] for n in v)}")

print("\nconflicts between derived market and the empirical sofi flag:")
bad = 0
for n in names:
    m, s = market(n["tk"]), bool(n.get("sofi"))
    if m == "ord" and s:
        print(f"  {n['tk']}: derived OTC-ordinary but flagged available"); bad += 1
    if m == "us" and not s:
        print(f"  {n['tk']}: derived US-listed but flagged unavailable "
              f"({n.get('sofi_note','')[:60]})"); bad += 1
print(f"  conflicts: {bad}")
