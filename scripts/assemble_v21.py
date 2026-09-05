# -*- coding: utf-8 -*-
"""Assemble the v2.1 engine file from the six-measure cards.

Inputs : data/rigor/v21_cards_rescore.json  (the 53 recorded names re-scored
         on the amended measures; C2, D and the gate carried)
         data/rigor/v21_cards_new.json      (the field admitted by the v2.1
         first screen, scored from scratch; optional until it exists)
         data/engine_tiers.json             (v2.0: jurisdiction penalties,
         names, needs, notes carried unchanged)
Output : data/engine_tiers_v21.json, the same shape as engine_tiers.json so
         freeze_vintage.py, load_names() and the report card read it as a
         second vintage; data/rigor/v21_assembly.json, the per-name deltas.

Arithmetic is assemble_v2.py's: score = sum of the ten components plus the
carried jurisdiction penalty; tiers 80/74/69/65; a gate fail sits in exit
review whatever its total. Nothing here judges; it adds and sorts.
"""
import json, os, sys, datetime
from paths import DATA
from rigor_lib import tier_of

COMP = ["A", "B", "C1", "C2", "D_rep", "D_inhib", "D_exit", "E", "F_clock", "F_now"]
CARD_EXTRA = ["host_flow", "evidence_class", "attribution", "rebound", "ceiling", "penetration",
              "enlarging", "largest_node", "moat_tests", "clock_basis", "developmental", "gate_note", "sources"]
R = os.path.join(DATA, "rigor")
eng = json.load(open(os.path.join(DATA, "engine_tiers.json"), encoding="utf-8"))
v20 = {}
for t in eng["tiers"]:
    for n in t["names"]:
        v20[n["tk"]] = dict(n, tier=t["id"])


def load_cards(fn):
    p = os.path.join(R, fn)
    if not os.path.exists(p):
        return []
    d = json.load(open(p, encoding="utf-8"))
    return d["cards"] if isinstance(d, dict) else d


cards = {}
for fn, origin in (("v21_cards_rescore.json", "rescore"), ("v21_cards_new.json", "new")):
    for c in load_cards(fn):
        c = dict(c); c["origin"] = origin
        cards[str(c["ticker"]).upper().strip()] = c
if not cards:
    sys.exit("no cards found in data/rigor/")

errs = []
names, deltas = [], []
for tk, c in cards.items():
    dims = {k: int(round(float(c[k]))) for k in COMP}
    calc = sum(dims.values())
    if abs(calc - float(c.get("total", calc))) > 0.5:
        errs.append("%s: stated total %s vs components %d (components used)" % (tk, c.get("total"), calc))
    old = v20.get(tk, {})
    jx = int(old.get("jx_penalty", 0) or 0)
    score = calc + jx
    gate = "fail" if str(c.get("gate", "pass")).lower().startswith("fail") else "pass"
    tier = "exit" if gate == "fail" else tier_of(score)
    rec = {"tk": tk, "nm": old.get("nm") or c.get("company", ""), "score": score, "score_base": calc,
           "jx_penalty": jx, "jx": old.get("jx", ""), "depth": "v2.1", "gate": gate,
           "gate_note": c.get("gate_note", "") or old.get("gate_note", ""), "dims": dims,
           "stock": c.get("stock", ""), "loop": c.get("loop", ""), "coupling": c.get("coupling", ""),
           "clock": c.get("clock_label", ""), "evidence": c.get("evidence", ""), "note": c.get("note", ""),
           "sofi": old.get("sofi", False), "sofi_note": old.get("sofi_note", ""),
           "values": old.get("values", ""), "values_note": old.get("values_note", ""),
           "need": old.get("need") or c.get("need", ""), "prev_score": old.get("score"),
           "origin": c["origin"], "verified": c.get("verified", ""),
           "card": {k: c.get(k) for k in CARD_EXTRA if k in c}}
    names.append((tier, rec))
    if old:
        od = old.get("dims", {})
        deltas.append({"tk": tk, "v20": int(old["score"]), "v21": score, "delta": score - int(old["score"]),
                       "tier_v20": old["tier"], "tier_v21": tier,
                       "by_measure": {k: dims[k] - int(od.get(k, 0)) for k in COMP if dims[k] != int(od.get(k, 0))},
                       "verified": c.get("verified", "")})
    else:
        deltas.append({"tk": tk, "v20": None, "v21": score, "delta": None, "tier_v20": None, "tier_v21": tier,
                       "by_measure": {}, "verified": c.get("verified", "")})

order = {"t1": 0, "t2": 1, "t3": 2, "t4": 3, "exit": 4}
out = {k: v for k, v in eng.items() if k != "tiers"}
out["_engine_version"] = "v2.1 stock-and-flow, first screen v2.1"
out["_scored_at"] = datetime.date.today().isoformat()
out["_v21"] = {"note": "assembled by assemble_v21.py from data/rigor/v21_cards_*.json; the v2.0 engine file is untouched and stays the live page engine until the v2.1 vintage is frozen and registered",
               "cards": len(cards), "rescored": sum(1 for c in cards.values() if c["origin"] == "rescore"),
               "new": sum(1 for c in cards.values() if c["origin"] == "new")}
out["tiers"] = []
for t in sorted(eng["tiers"], key=lambda t: order.get(t["id"], 99)):
    members = sorted([r for tr, r in names if tr == t["id"]], key=lambda r: (-r["score"], r["tk"]))
    out["tiers"].append({"id": t["id"], "label": t["label"], "names": members})
json.dump(out, open(os.path.join(DATA, "engine_tiers_v21.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=True)

summary = {"assembled": out["_scored_at"], "cards": len(cards), "arithmetic_errors": errs,
           "tiers": {t["id"]: len(t["names"]) for t in out["tiers"]},
           "tiers_v20": {t["id"]: len(t["names"]) for t in eng["tiers"]},
           "moved_band": [d for d in deltas if d["tier_v20"] and d["tier_v20"] != d["tier_v21"]],
           "mean_delta_rescored": (sum(d["delta"] for d in deltas if d["delta"] is not None) /
                                   max(1, sum(1 for d in deltas if d["delta"] is not None))),
           "measure_moves": {k: sum(1 for d in deltas if k in d["by_measure"]) for k in COMP},
           "deltas": sorted(deltas, key=lambda d: -(d["delta"] or 0))}
json.dump(summary, open(os.path.join(R, "v21_assembly.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=True)
print("v2.1 engine: %d names | tiers %s (v2.0 %s) | mean delta on re-scored %.1f | band moves %d | arithmetic errors %d"
      % (len(cards), summary["tiers"], summary["tiers_v20"], summary["mean_delta_rescored"], len(summary["moved_band"]), len(errs)))
for e in errs: print("  !", e)
for d in summary["moved_band"]: print("  %-7s %s -> %s (%s -> %s) %s" % (d["tk"], d["v20"], d["v21"], d["tier_v20"], d["tier_v21"], d["by_measure"]))
