# -*- coding: utf-8 -*-
"""The engine's report card: does the frozen score predict anything?

Forward test: Spearman information coefficient between the frozen 2026-08-28
scores and forward returns from the price track, plus the tier return spread
(t1 minus exit). Accrues one reading per weekly snapshot; it reports
"accruing" honestly until the window is real.

Contamination check, computable now: the correlation between the frozen
score and the TRAILING year's return. The scores were written knowing these
prices, so a high value would mean the rubric was momentum wearing a lab
coat. A value near zero is evidence the score is measuring something other
than what already went up."""
import json, os
import numpy as np
from paths import DATA
from rigor_lib import load_names, spearman

R = os.path.join(DATA, "rigor")
frz = json.load(open(os.path.join(R, "freeze_2026-08-28.json"), encoding="utf-8"))
trk = json.load(open(os.path.join(R, "price_track.json"), encoding="utf-8"))
names = load_names()

doc = {"vintage": frz["asof"], "snapshots": len(trk["snapshots"]),
       "latest": trk["snapshots"][-1]["date"]}

# ---- forward test ----------------------------------------------------------
t0 = frz["prices"]; latest = trk["snapshots"][-1]["px"]
fwd = {tk: latest[tk] / t0[tk] - 1 for tk in t0
       if t0.get(tk) and latest.get(tk)}
days = (np.datetime64(doc["latest"]) - np.datetime64(frz["asof"])).astype(int)
if days < 14 or len(trk["snapshots"]) < 3:
    doc["forward"] = {"status": "accruing", "days_elapsed": int(days),
                      "note": "the forward test begins reporting once the track holds three weekly snapshots spanning two weeks or more; endpoints are pre-registered in evaluation_protocol.json"}
else:
    sc = {n["tk"]: frz["scores"][n["tk"]]["score"] for n in names if n["tk"] in fwd}
    common = sorted(sc)
    ic = spearman([sc[t] for t in common], [fwd[t] for t in common])
    tiers = {}
    for n in names:
        if n["tk"] in fwd:
            tiers.setdefault(frz["scores"][n["tk"]]["tier"], []).append(fwd[n["tk"]])
    tm = {t: round(float(np.mean(v)), 4) for t, v in tiers.items()}
    doc["forward"] = {"status": "reporting", "days_elapsed": int(days),
                      "information_coefficient": round(ic, 3),
                      "tier_mean_returns": tm,
                      "t1_minus_exit": round(tm.get("t1", 0) - tm.get("exit", 0), 4)}

# ---- the whole universe faces the test too ---------------------------------
uf = json.load(open(os.path.join(R, "universe_freeze_2026-08-28.json"), encoding="utf-8"))
ut = json.load(open(os.path.join(R, "universe_track.json"), encoding="utf-8"))
udays = (np.datetime64(ut["snapshots"][-1]["date"]) - np.datetime64(uf["asof"])).astype(int)
if udays < 28 or len(ut["snapshots"]) < 2:
    doc["universe"] = {"status": "accruing", "names_in_vintage": uf["n"],
                       "priced": len(ut["snapshots"][-1]["px"]),
                       "note": "universe IC and advanced-minus-cut spread report once two monthly snapshots exist; endpoints pre-registered"}
else:
    p0 = ut["snapshots"][0]["px"]; p1 = ut["snapshots"][-1]["px"]
    ufwd, usc, grp = [], [], {"adv": [], "cut": []}
    for tk, (stage, sc) in uf["scores"].items():
        if p0.get(tk) and p1.get(tk):
            r = p1[tk] / p0[tk] - 1
            ufwd.append(r); usc.append(sc)
            (grp["adv"] if stage in ("R", "3", "4") else grp["cut"]).append(r)
    doc["universe"] = {"status": "reporting", "days_elapsed": int(udays), "n": len(ufwd),
                       "information_coefficient": round(spearman(usc, ufwd), 3),
                       "advanced_minus_cut": round(float(np.mean(grp["adv"]) - np.mean(grp["cut"])), 4)}

# ---- contamination check (computable on day one) ---------------------------
sp = json.load(open(os.path.join(DATA, "spark.json"), encoding="utf-8"))["s"]
trail = {tk: v[-1] / v[0] - 1 for tk, v in sp.items() if v and v[0]}
sc2 = {n["tk"]: n["score"] for n in names if n["tk"] in trail}
common = sorted(sc2)
rho = spearman([sc2[t] for t in common], [trail[t] for t in common])
doc["momentum_contamination"] = {
    "spearman_score_vs_trailing_year_return": round(rho, 3), "names": len(common),
    "reading": "near zero means the score is not a costume on last year's winners; strongly positive would mean the rubric absorbed momentum"}
json.dump(doc, open(os.path.join(R, "report_card.json"), "w"), indent=1)
f = doc["forward"]
print("report card: forward %s (%d days) | contamination rho %.3f over %d names"
      % (f["status"], f["days_elapsed"], rho, len(common)))
