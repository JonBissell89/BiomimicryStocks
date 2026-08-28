# -*- coding: utf-8 -*-
"""Last pass: does anything anywhere still describe the retired engine?"""
import os
from paths import BUILD
import json, re, glob
D = r"C:\Users\jbiss\Desktop\Stocks"
RETIRED = ["permanent need", "cost compression", "expansion signal", "scale velocity",
           "proven functions", "uniqueness / moat", "system balance ", "eight dimension"]

eng = json.load(open(os.path.join(D, "tournament\\data\\engine_tiers.json"), encoding="utf-8"))
meta = {k: v for k, v in eng.items() if k.startswith("_")}
blob = json.dumps(meta, ensure_ascii=False).lower()
print("ENGINE METADATA still describing the retired scorecard:")
hits = [w for w in RETIRED if w in blob]
print("  " + (", ".join(hits) if hits else "none"))
for w in hits:
    for m in re.finditer(r".{0,100}" + re.escape(w) + r".{0,100}", blob):
        print("    ..." + m.group(0) + "...")

print("\nDOC FILES:")
for f in [os.path.join(D, "HOLDING_FRAMEWORK.md"), os.path.join(D, "tournament\\V2_RUBRIC.md"),
          os.path.join(D, "tournament\\RUNBOOK.md")]:
    try:
        t = open(f, encoding="utf-8").read().lower()
    except Exception as e:
        print(f"  {f.split(chr(92))[-1]}: {e}"); continue
    h = [w for w in RETIRED if w in t]
    print(f"  {f.split(chr(92))[-1]:<24s} retired terms: {h if h else 'none'}   "
          f"em dashes: {t.count(chr(8212))}")

print("\nENGINE vs PAGE consistency:")
names = [n for t in eng["tiers"] for n in t["names"]]
page = open(os.path.join(BUILD, "bs_console.html"),
            encoding="utf-8").read()
m = re.search(r"const NAMES=(\[.*?\]);\n", page, re.S)
pn = json.loads(m.group(1))
print(f"  engine names {len(names)}  page names {len(pn)}")
emap = {n["tk"]: n for n in names}
bad = 0
for r in pn:
    e = emap.get(r[0])
    if not e:
        print(f"  page has {r[0]} not in engine"); bad += 1; continue
    if r[2] != e["score"]:
        print(f"  {r[0]} score page {r[2]} vs engine {e['score']}"); bad += 1
    if len(r) < 12 or len(r[10]) != 10:
        print(f"  {r[0]} missing scorecard dims"); bad += 1
    if r[11][3] != e["gate"]:
        print(f"  {r[0]} gate page {r[11][3]} vs engine {e['gate']}"); bad += 1
print(f"  mismatches: {bad}")

gf = [n["tk"] for n in names if n["gate"] == "fail"]
print(f"  gate failures: {gf}")
print(f"  tier counts: " + ", ".join(f"{t['id']}={len(t['names'])}" for t in eng["tiers"]))
