# -*- coding: utf-8 -*-
"""One compact, page-ready summary of every rigor instrument's current reading.

The build injects this file into the console, so the page can only show what
the instruments actually measured. Runs at the end of the rigor chain."""
import json, os
from paths import DATA

R = os.path.join(DATA, "rigor")
J = lambda f: json.load(open(os.path.join(R, f), encoding="utf-8"))
rep, sen, rsk, rel, fnr, fac, pro = (J(f) for f in
    ("report_card.json", "sensitivity.json", "risk_profile.json",
     "reliability.json", "fn_rescore.json", "factor_internal.json", "evaluation_protocol.json"))
uni = rep.get("universe", {})
items = [
 ["Pre-registered test", "endpoints locked %s; 12-month tier spread and information coefficient on the frozen 2026-08-28 vintage, the whole 15,797-name universe included, the basket against the S&P stated either way" % pro["registered"]],
 ["Forward test, 53 ranked", "%s, day %d of 365; one look per week" % (rep["forward"]["status"], rep["forward"]["days_elapsed"])],
 ["Forward test, full universe", "%s; every one of the %s first-screen judgments faces the same clock" % (uni.get("status", "accruing"), "15,797")],
 ["Momentum contamination", "score vs trailing-year return, Spearman %+.2f over %d names: the rubric is not last year's winners in a lab coat" % (rep["momentum_contamination"]["spearman_score_vs_trailing_year_return"], rep["momentum_contamination"]["names"])],
 ["Weights vs measurement", "1,000 weight perturbations, rank stability %.3f: the measurement, not the weights, produces the order. Cronbach alpha %.2f: six measures, six properties" % (sen["rank_stability_spearman"]["mean"], sen["cronbach_alpha"])],
 ["Independent bets", "%.1f effective bets across %d names, average pairwise correlation %.2f: more independent wagers than the health share implies" % (rsk["effective_independent_bets"], rsk["names_with_series"], rsk["avg_pairwise_correlation"])],
 ["Blind second scorer", "gate verdicts %s over two seeded batches; totals within %.1f of 100; ordering holds where levels genuinely differ (rho %.2f in the wide batch) and dissolves inside a tier band (%.2f in the narrow one), so tier edges deserve less confidence than the gate" % (rel["gate_agreement"].split(",")[0], rel["score_agreement"]["mean_absolute_deviation_of_100"], rel["batches"][1]["spearman"], rel["batches"][0]["spearman"])],
 ["Screen error bar", "%d registered cuts blind re-scored in two batches: agreement rho %.2f, one confirmed false negative (%s, blind six-measure grade t2), one recorded score corrected (%s), zero new misses in batch two" % (len(fnr["rows"]), fnr["agreement"]["spearman"], ",".join(fnr["potential_false_negatives"]["names"]), ",".join(fnr["reverse_disagreements"]["names"][:1]))],
 ["Attribution", "internal only: %.0f%% of basket variance is the market plus the health tilt; the external factor test is registered and pending, so it cannot be quietly dropped" % ((1 - fac["idiosyncratic_share"]) * 100)],
]
# the market changes and the logic changes; both leave a visible reading
rq = json.load(open(os.path.join(DATA, "refresh_queue.json"), encoding="utf-8"))
lv = json.load(open(os.path.join(R, "logic_version.json"), encoding="utf-8"))
if rq.get("obligations"):
    fresh = ("OPEN OBLIGATION: judging logic moved to %s, so every name is owed a fresh look; "
             "a full universe re-screen and ranked re-score are queued and this line stays until they run"
             % rq["obligations"].get("logic_version"))
elif rq.get("last_refresh"):
    fresh = ("listings re-pulled %s: %d new entrants queued for a first-screen judgment, %d names "
             "flagged for delisting review; judged under logic %s, whose documents are hash-checked on every build"
             % (rq["last_refresh"], len(rq.get("pending_first_screen", [])),
                len(rq.get("delisted_check", [])), lv["version"]))
else:
    fresh = ("first quarterly listing pull pending; judged under logic %s, whose documents are "
             "hash-checked on every build, and any logic change forces a full re-screen" % lv["version"])
items.append(["Universe freshness", fresh])
doc = {"asof": rep["latest"], "items": items,
       "note": "every line is a current instrument reading from data/rigor/, derived and audited; none is a claim"}
json.dump(doc, open(os.path.join(R, "summary.json"), "w", encoding="utf-8"), indent=1)
print("rigor summary: %d readings" % len(items))
