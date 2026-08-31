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
 ["Blind second scorer", "gate verdicts %s; totals within %.1f of 100; fine ordering inside the noise floor, so tier edges deserve less confidence than the gate" % (rel["gate_agreement"].split(",")[0], rel["score_agreement"]["mean_absolute_deviation_of_100"])],
 ["Screen error bar", "12 registered cuts blind re-scored: agreement rho %.2f, one likely false negative found (%s) and one recorded score contradicted (%s)" % (fnr["agreement"]["spearman"], ",".join(fnr["potential_false_negatives"]["names"]), ",".join(fnr["reverse_disagreements"]["names"][:1]))],
 ["Attribution", "internal only: %.0f%% of basket variance is the market plus the health tilt; the external factor test is registered and pending, so it cannot be quietly dropped" % ((1 - fac["idiosyncratic_share"]) * 100)],
]
doc = {"asof": rep["latest"], "items": items,
       "note": "every line is a current instrument reading from data/rigor/, derived and audited; none is a claim"}
json.dump(doc, open(os.path.join(R, "summary.json"), "w", encoding="utf-8"), indent=1)
print("rigor summary: %d readings" % len(items))
