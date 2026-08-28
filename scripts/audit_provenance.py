# -*- coding: utf-8 -*-
"""Where does each engine score actually come from?"""
import os
from paths import DATA
import glob, json
import pandas as pd

D = DATA
eng = json.load(open(os.path.join(D, "engine_tiers.json"), encoding="utf-8"))
names = {n["tk"]: n for t in eng["tiers"] for n in t["names"]}
cols = ["permanent_need", "system_balance", "cost_compression", "moat",
        "proven_functions", "scale_velocity", "expansion_signal", "survivability"]

r4 = pd.read_csv(os.path.join(D, "round4_results.csv"))
r4["ticker"] = r4.ticker.astype(str).str.upper()
r4 = r4.drop_duplicates("ticker").set_index("ticker")

deep = pd.concat([pd.read_csv(f, on_bad_lines="skip") for f in sorted(glob.glob(os.path.join(D, "final_deep_f*.csv")))],
                 ignore_index=True)
deep["ticker"] = deep.ticker.astype(str).str.upper()
deep = deep.drop_duplicates("ticker", keep="last").set_index("ticker")

light = pd.concat([pd.read_csv(f, on_bad_lines="skip") for f in sorted(glob.glob(os.path.join(D, "final_light_w*.csv")))],
                  ignore_index=True)
light["ticker"] = light.ticker.astype(str).str.upper()
light = light.drop_duplicates("ticker", keep="last").set_index("ticker")

def num(x):
    try: return float(str(x).strip())
    except Exception: return None

print(f"{'TK':7s} {'engine':>6} {'R4sum':>6} {'R4tot':>6} {'DEEPtot':>7} {'DEEPsum':>7} {'LIGHTtot':>8}  source")
print("-" * 78)
srcs = {}
for tk, n in sorted(names.items(), key=lambda x: -x[1]["score"]):
    base = n.get("score_base", n["score"])
    r4sum = sum(float(r4.loc[tk][c]) for c in cols) if tk in r4.index else None
    r4tot = num(r4.loc[tk]["total"]) if tk in r4.index else None
    dtot = num(deep.loc[tk]["total"]) if tk in deep.index else None
    dsum = None
    if tk in deep.index:
        try: dsum = sum(float(deep.loc[tk][c]) for c in cols)
        except Exception: dsum = None
    ltot = num(light.loc[tk]["total"]) if tk in light.index else None
    src = "?"
    if dtot is not None and abs(dtot - base) < 0.5: src = "FINAL deep pass"
    elif ltot is not None and abs(ltot - base) < 0.5: src = "final light pass"
    elif r4tot is not None and abs(r4tot - base) < 0.5: src = "round 4"
    srcs[src] = srcs.get(src, 0) + 1
    print(f"{tk:7s} {n['score']:>6} {r4sum if r4sum else 0:>6.0f} {r4tot if r4tot else 0:>6.0f} "
          f"{dtot if dtot else 0:>7.0f} {dsum if dsum else 0:>7.0f} {ltot if ltot else 0:>8.0f}  {src}")
print()
print("SCORE PROVENANCE:", srcs)
print()
print("Do the FINAL deep-pass scores sum to their own dimensions?")
mism = 0
for tk in deep.index:
    try:
        dsum = sum(float(deep.loc[tk][c]) for c in cols)
        dtot = num(deep.loc[tk]["total"])
        if dtot is not None and abs(dsum - dtot) > 0.5:
            mism += 1
            print(f"  {tk:7s} total={dtot:.0f} but dimensions sum to {dsum:.0f}  ({dtot-dsum:+.0f})")
    except Exception:
        pass
print(f"  deep-pass rows checked: {len(deep)}   internally inconsistent: {mism}")
