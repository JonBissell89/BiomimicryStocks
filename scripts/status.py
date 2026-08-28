# -*- coding: utf-8 -*-
"""Current engine status, read from the files rather than from memory."""
import os
from paths import BUILD, DATA
import json, os, datetime
D = DATA
eng = json.load(open(os.path.join(D, "engine_tiers.json"), encoding="utf-8"))
names = [(t["id"], n) for t in eng["tiers"] for n in t["names"]]

print(f"engine version : {eng.get('_engine_version')}")
print(f"scored at      : {eng.get('_scored_at')}")
print(f"names          : {len(names)}")
print(f"tier bands     : 80 / 74 / 69 / 65, held fixed")
print()
for t in eng["tiers"]:
    inv = [n for n in t["names"] if n["gate"] == "pass"]
    lo = min(n["score"] for n in t["names"]); hi = max(n["score"] for n in t["names"])
    print(f"  {t['id']:<5s} n={len(t['names']):<3d} investable={len(inv):<3d} range {lo}-{hi}")
    print(f"        {' '.join(n['tk'] + ('*' if n['gate']=='fail' else '') for n in t['names'])}")
print("  (* fails the survivability gate)")

print()
print("HOLDINGS (real positions), where they sit now")
for tk in ["WRTBY", "BSY", "BB", "YMM", "SHLS", "CRMD"]:
    for tid, n in names:
        if n["tk"] == tk:
            print(f"  {tk:<6s} {n['score']:>3d}  {tid:<5s} (was {n['prev_score']})  "
                  f"loop {n['loop']:<10s} coupling {n['coupling']}")

print()
print("FILE FRESHNESS")
for f in ["engine_tiers.json", "v2_assembled.csv", "search_index.json"]:
    p = os.path.join(D, f)
    if os.path.exists(p):
        m = datetime.datetime.fromtimestamp(os.path.getmtime(p))
        print(f"  {f:<24s} {m:%Y-%m-%d %H:%M}")
page = os.path.join(BUILD, "bs_console.html")
if os.path.exists(page):
    m = datetime.datetime.fromtimestamp(os.path.getmtime(page))
    print(f"  {'console page':<24s} {m:%Y-%m-%d %H:%M}  ({os.path.getsize(page)//1024} KB)")
