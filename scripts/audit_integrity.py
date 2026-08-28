# -*- coding: utf-8 -*-
"""Is the engine internally consistent? Does score == sum(dimensions) + penalties?"""
from paths import DATA
import json
import pandas as pd

D = DATA
eng = json.load(open(os.path.join(D, "engine_tiers.json"), encoding="utf-8"))
names = {n["tk"]: n for t in eng["tiers"] for n in t["names"]}
r4 = pd.read_csv(os.path.join(D, "round4_results.csv"))
r4["ticker"] = r4.ticker.astype(str).str.upper()
r4 = r4.drop_duplicates("ticker").set_index("ticker")
cols = ["permanent_need", "system_balance", "cost_compression", "moat",
        "proven_functions", "scale_velocity", "expansion_signal", "survivability"]

print("QUESTION 1: does the engine score equal the sum of its eight dimensions?")
bad, ok, nodata = [], 0, []
for tk, n in names.items():
    if tk not in r4.index:
        nodata.append(tk); continue
    row = r4.loc[tk]
    try:
        dsum = sum(float(row[c]) for c in cols)
    except Exception:
        nodata.append(tk); continue
    pen = n.get("jx_penalty", 0) or 0
    expect = dsum + pen
    if abs(expect - n["score"]) > 0.5:
        bad.append((tk, n["score"], dsum, pen, expect, n.get("note", "")[:40]))
    else:
        ok += 1
print(f"  consistent: {ok}   mismatched: {len(bad)}   no dimension data: {len(nodata)}")
for tk, sc, dsum, pen, exp, note in bad[:15]:
    print(f"    {tk:6s} engine={sc:>3}  dims={dsum:>5.0f}  pen={pen:>3}  should be {exp:>5.0f}  diff {sc-exp:+.0f}   {note}")

print()
print("QUESTION 2: were the light-track names ever scored on the eight dimensions,")
print("            or did the total come from somewhere else?")
light = [tk for tk, n in names.items() if n.get("depth") == "light"]
print(f"  light-track names: {len(light)}")
sample = [t for t in light if t in r4.index][:5]
for tk in sample:
    row = r4.loc[tk]
    vals = {c: row[c] for c in cols}
    print(f"    {tk}: {vals}  total={row.get('total')}")

print()
print("QUESTION 3: can the engine be re-run from source, or are scores baked in?")
import os
scripts = os.listdir(os.path.join(D, "..\scripts"))
producers = [s for s in scripts if s.startswith(("round", "final_", "unify"))]
print("  scripts that PRODUCE scores:", producers)
print("  scripts that only REFRESH prices/pages:",
      [s for s in scripts if s.startswith("refresh_")])
print()
print("  Round 4 scoring was done by research agents writing CSVs by hand;")
print("  there is no script that recomputes a dimension from data.")
