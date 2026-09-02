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
import marketdb
trk = marketdb.load_price_track()
names = load_names()

doc = {"vintage": frz["asof"], "snapshots": len(trk["snapshots"]),
       "latest": trk["snapshots"][-1]["date"]}

# ---- forward test, one per registered vintage -------------------------------
# The protocol may register several vintages (a logic version freezes its own
# engine); each is graded on its own scores and its own freeze prices, from the
# same weekly track. doc["forward"] keeps the first (primary) for the page.
pro = json.load(open(os.path.join(R, "evaluation_protocol.json"), encoding="utf-8"))
vintages = pro.get("vintages") or [{"tag": "v2.0", "file": pro["vintage"]["file"]}]
latest = trk["snapshots"][-1]["px"]
doc["forward_by_vintage"] = {}
for v in vintages:
    fz = json.load(open(os.path.join(R, v["file"]), encoding="utf-8"))
    t0 = fz["prices"]
    fwd = {tk: latest[tk] / t0[tk] - 1 for tk in t0 if t0.get(tk) and latest.get(tk)}
    days = (np.datetime64(doc["latest"]) - np.datetime64(fz["asof"])).astype(int)
    if days < 14 or len(trk["snapshots"]) < 3:
        rep = {"status": "accruing", "days_elapsed": int(days),
               "note": "the forward test begins reporting once the track holds three weekly snapshots spanning two weeks or more; endpoints are pre-registered in evaluation_protocol.json"}
    else:
        sc = {tk: fz["scores"][tk]["score"] for tk in fz["scores"] if tk in fwd}
        common = sorted(sc)
        ic = spearman([sc[t] for t in common], [fwd[t] for t in common])
        tiers = {}
        for tk in common:
            tiers.setdefault(fz["scores"][tk]["tier"], []).append(fwd[tk])
        tm = {t: round(float(np.mean(x)), 4) for t, x in tiers.items()}
        rep = {"status": "reporting", "days_elapsed": int(days), "n": len(common),
               "information_coefficient": round(ic, 3), "tier_mean_returns": tm,
               "t1_minus_exit": round(tm.get("t1", 0) - tm.get("exit", 0), 4)}
    rep["vintage_asof"] = fz["asof"]
    doc["forward_by_vintage"][v["tag"]] = rep
doc["forward"] = doc["forward_by_vintage"][vintages[0]["tag"]]

# ---- the whole universe faces the test too ---------------------------------
uf = json.load(open(os.path.join(R, "universe_freeze_2026-08-28.json"), encoding="utf-8"))
ut = marketdb.load_universe_track()
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
sp = marketdb.load_spark()["s"]
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
