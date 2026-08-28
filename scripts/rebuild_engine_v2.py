# -*- coding: utf-8 -*-
"""Rebuild engine_tiers.json on the v2 stock-and-flow scorecard.

Two calibration decisions are recorded here rather than silently applied:
  1. Tier bands are NOT moved. Moving them to preserve tier sizes would
     manufacture the previous answer. Same rule as 'do not pad the list'.
  2. The rail cluster's fall is kept. It is the rubric working, not misfiring.
     Reasoning is written into _calibration below.
"""
import os
from paths import DATA
import json, shutil, datetime
import pandas as pd

D = DATA
SRC = os.path.join(D, "engine_tiers.json")
STAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

shutil.copy(SRC, os.path.join(D, "engine_tiers_v1_backup.json"))
eng = json.load(open(SRC, encoding="utf-8"))
old = {n["tk"]: n for t in eng["tiers"] for n in t["names"]}

v = pd.read_csv(os.path.join(D, "v2_assembled.csv"))
v["g"] = v.gate.astype(str).str.lower().str.strip()
v["passes"] = v.g.str.startswith("pass")

def clean(s):
    if s is None:
        return ""
    s = str(s)
    if s.lower() in ("nan", "none"):
        return ""
    return s.replace("\u2014", ",").replace("\u2013", "-").replace("  ", " ").strip()

def band(s):
    return "t1" if s >= 80 else "t2" if s >= 74 else "t3" if s >= 69 else "t4" if s >= 65 else "exit"

LABELS = {
    "t1": "Tier 1 · strongest measured correction, 80 and above",
    "t2": "Tier 2 · clear correction, 74 to 79",
    "t3": "Tier 3 · correction present but partial, 69 to 73",
    "t4": "Tier 4 · weak or slow correction, 65 to 68",
    "exit": "Exit review · below 65 on the stock and flow scorecard",
}

buckets = {k: [] for k in LABELS}
for r in v.sort_values("v2_adj", ascending=False).itertuples():
    o = old.get(r.ticker, {})
    rec = {
        "tk": r.ticker,
        "nm": o.get("nm", r.ticker),
        "score": int(round(r.v2_adj)),
        "score_base": int(round(r.calc)),
        "jx_penalty": int(r.jx),
        "jx": o.get("jx", ""),
        "depth": "v2",
        "gate": "pass" if r.passes else "fail",
        "gate_note": clean(r.note) if not r.passes else "",
        "dims": {"A": int(r.A), "B": int(r.B), "C1": int(r.C1), "C2": int(r.C2),
                 "D_rep": int(r.D_rep), "D_inhib": int(r.D_inhib), "D_exit": int(r.D_exit),
                 "E": int(r.E), "F_clock": int(r.F_clock), "F_now": int(r.F_now)},
        "stock": clean(getattr(r, "stock", "")),
        "loop": clean(getattr(r, "loop", "")),
        "coupling": clean(getattr(r, "coupling", "")),
        "clock": clean(getattr(r, "clock_label", "")),
        "evidence": clean(getattr(r, "evidence", "")),
        "note": clean(getattr(r, "note", ""))[:400],
        "sofi": o.get("sofi", None),
        "sofi_note": clean(o.get("sofi_note", "")),
        "values": o.get("values", ""),
        "values_note": "re-verified on the v2 stock and flow scorecard",
        "need": o.get("need", ""),
        "prev_score": int(o["score"]) if o.get("score") is not None else None,
    }
    buckets[band(r.v2_adj)].append(rec)

eng["tiers"] = [{"id": k, "label": LABELS[k], "names": buckets[k]}
                for k in ["t1", "t2", "t3", "t4", "exit"] if buckets[k]]

eng["_engine_version"] = "v2 stock-and-flow"
eng["_scored_at"] = STAMP
eng["_rubric"] = (
    "Six measures on one 100 point scale. A the stock (20), B the flow (25), "
    "C the loop (20, split 12 sign and 8 coupling), D growth pattern (15, split "
    "replication, contact inhibition and clean exit), E buffer (10), F clock (10, "
    "split time constant and current momentum). Survivability is a gate, not a score: "
    "a company that cannot fund itself to the horizon in F is excluded rather than "
    "ranked lower. Jurisdiction penalties apply after the total."
)
eng["_calibration"] = {
    "shift": (
        "Every name was re-scored. The mean fell 7.0 points and 42 of 53 names moved "
        "down. The correlation between the old score and the new one is 0.07, so this "
        "is not the same ranking shifted; it is a different measurement."
    ),
    "bands_not_moved": (
        "Tier bands were deliberately left at 80 / 74 / 69 / 65. Moving them down to "
        "keep 29 names in Tier 1 would have reproduced the previous answer by "
        "arithmetic. Tier 1 now holds 12 names, 11 of them investable. If only 11 "
        "clear the bar, 11 clear the bar."
    ),
    "rail_cluster_kept": (
        "Four rail names fell hardest (UNP -30, CP -27, CNI -18, WAB -16). This was "
        "checked as a possible rubric artifact and kept as a real result. The moat "
        "deduction is evidence backed rather than structural: rail moves a ton of "
        "freight roughly 480 miles per gallon against about 145 for trucks, and rail's "
        "modal share against trucking still has not moved. A position that captures "
        "that advantage as captive shipper margin instead of passing it through as "
        "volume is throttling the correction it would otherwise drive. The replication "
        "score is likewise the observed pattern: all three Class I railroads are "
        "currently growing by merger, not by copying a unit."
    ),
    "known_property": (
        "The scorecard is deliberately hostile to long clock infrastructure. Measure F "
        "says so in the rubric: being right about the imbalance and wrong about the "
        "clock is indistinguishable from being wrong. Every name with a decades clock "
        "sits at F_clock 3 of 6. This is a designed property, not a defect, and it is "
        "the single largest reason the rail and utility shaped businesses rank lower "
        "than they did."
    ),
    "measure_f_is_near_constant": (
        "Within these 53 finalists, F_clock spans only 3 to 5 of 6 and F_now spans 2 to "
        "4 of 4, correlating -0.13 with the total. Measure F did its discriminating "
        "upstream, in the six round screen, where names with no dated momentum were "
        "already cut. It separates the universe, not the finalists."
    ),
    "inter_rater_check": (
        "Comparable businesses scored by different researchers landed within 5 to 10 "
        "points of each other: infection control spread 5, construction attachments 5, "
        "molecular diagnostics 9, cardiac monitoring 10. Rail spread 15, and that spread "
        "traces to real differences, since Wabtec sells a replicable retrofit while the "
        "railroads own corridors."
    ),
}
eng["gate"] = 20.0
eng["_gate_rule"] = (
    "Survivability gate, checked before scoring: under 12 months runway with no "
    "committed financing, three year dilution above 25 percent, a pending buyout, or "
    "going concern doubt. Two names fail: Butterfly Network on roughly 28 percent three "
    "year dilution despite scoring 80, and Demand Works on 34.8 percent dilution in one "
    "year. A gate failure is not a judgment about the business."
)

json.dump(eng, open(SRC, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

print(f"engine rebuilt at {STAMP}")
for t in eng["tiers"]:
    inv = sum(1 for n in t["names"] if n["gate"] == "pass")
    print(f"  {t['id']:<5s} n={len(t['names']):<3d} investable={inv}")
tot = sum(len(t["names"]) for t in eng["tiers"])
print(f"  total {tot}")
