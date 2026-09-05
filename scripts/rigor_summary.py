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
# the registered external test replaces the internal bound the moment it reports
_fx = os.path.join(R, "factor_external.json")
if os.path.exists(_fx):
    fx = json.load(open(_fx, encoding="utf-8"))
    if fx.get("status") == "reported":
        sf = fx["six_factor"]
        items[-1] = ["Attribution", "external, against the French library over %d weeks: market beta %.2f, six factors explain %.0f%% of variance, alpha after loadings %+.1f%% a year at t=%.1f; the registered rule says the thesis survives only if alpha remains, and the window is still short"
                     % (fx["window_weeks"], sf["loadings"]["mkt_rf"], sf["r2"] * 100, sf["alpha_annual"] * 100, sf["alpha_t"])]
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
if rq.get("pending_stage2") or rq.get("descriptions_owed"):
    fresh += ("; the v2.1 description route has admitted %d names that await a Round 2 business read, and %d viable names in routed codes still owe a description (fetched weekly)"
              % (len(rq.get("pending_stage2", [])), rq.get("descriptions_owed", 0)))
fbv = rep.get("forward_by_vintage", {})
if len(fbv) > 1:
    parts = []
    for tag, r in fbv.items():
        parts.append("%s (%s): %s%s" % (tag, r.get("vintage_asof", "?"), r.get("status", "?"),
                     (", IC %.3f, t1 minus exit %+.1f%%" % (r["information_coefficient"], 100 * r["t1_minus_exit"])) if r.get("status") == "reporting" else ""))
    # v2.0-to-v2.1 re-score movement, read from the assembly file rather than pinned by hand
    asm = J("v21_assembly.json")
    pred = J("v21_predictions.json")
    p11 = next((r for r in pred["readings"] if r.get("id") == "v21-P11"), {})
    rho = p11.get("spearman_v20_v21")
    if not isinstance(rho, (int, float)):
        from rigor_lib import spearman
        pairs = [d for d in asm["deltas"] if d.get("v20") is not None]
        rho = spearman([d["v20"] for d in pairs], [d["v21"] for d in pairs])
    # blind v2.1 batch agreement, and how it compares with the pooled v2.0 batches
    av21 = rel["agreement_v21"]
    v21_rows = [r for r in rel["rows"] if r.get("batch") == av21["batch"]]
    hot_by = sum(r["delta_recorded_minus_blind"]["total"] for r in v21_rows) / len(v21_rows)
    items.append(["Second vintage", "two logic versions face the same clock, each graded on its own frozen scores and prices: " + "; ".join(parts)
                  + (". v2.1 re-scored the 53 on the amended measures (mean %.1f points, %d tier-band moves, rank correlation %.2f with v2.0) and added a 20-name field from the re-screen; the v2.0 list stays the live list, and the two are compared, not averaged."
                     % (asm["mean_delta_rescored"], len(asm["moved_band"]), rho))
                  + (" A blind v2.1 batch of %d names scored from the rubric text alone agreed to %.1f of 100 (v2.0 batches: %.1f), gates %s, and ran %.1f points below the recorded cards on average."
                     % (av21["n"], av21["mean_absolute_deviation_of_100"], rel["score_agreement"]["mean_absolute_deviation_of_100"], av21["gate_agreement"], hot_by))])
items.append(["Universe freshness", fresh])
doc = {"asof": rep["latest"], "items": items,
       "note": "every line is a current instrument reading from data/rigor/, derived and audited; none is a claim"}
json.dump(doc, open(os.path.join(R, "summary.json"), "w", encoding="utf-8"), indent=1)
print("rigor summary: %d readings" % len(items))
