# -*- coding: utf-8 -*-
"""The rigor layer's own audit: the vintage is immutable, the protocol is
registered, and every instrument has a fresh, well-formed reading."""
import json, os, sys
from paths import DATA
from rigor_lib import load_names, sha_scores

R = os.path.join(DATA, "rigor")
errs, warns = [], []
def need(fn):
    p = os.path.join(R, fn)
    if not os.path.exists(p): errs.append("missing " + fn); return None
    return json.load(open(p, encoding="utf-8"))

frz = need("freeze_2026-08-28.json")
pro = need("evaluation_protocol.json")
trk = need("price_track.json")
rep = need("report_card.json")
sen = need("sensitivity.json")
rsk = need("risk_profile.json")
cov = need("coverage.json")
if errs: [print("  !", e) for e in errs]; sys.exit(1)

# the vintage is what it says it is, and the protocol points at it
import hashlib
canon = json.dumps(sorted([[tk, v["score"], v["tier"], v["gate"]] for tk, v in frz["scores"].items()]),
                   separators=(",", ":"))
if hashlib.sha256(canon.encode()).hexdigest() != frz["sha256_scores"]:
    errs.append("freeze file does not match its own hash: the vintage was edited")
if pro["vintage"]["sha256_scores"] != frz["sha256_scores"]:
    errs.append("protocol points at a different vintage than the freeze file")
if len(frz["scores"]) != len(load_names()):
    warns.append("live engine name count differs from the vintage (allowed; the vintage still governs)")

# the track starts at the freeze and stays ordered
if trk["snapshots"][0]["date"] != frz["asof"]:
    errs.append("price track does not start at the freeze date")
dates = [s["date"] for s in trk["snapshots"]]
if dates != sorted(dates): errs.append("price track dates out of order")
if rep["latest"] != dates[-1]: errs.append("report card is stale; rerun report_card.py")

# instruments carry readings, and the stability floor holds
if sen["rank_stability_spearman"]["mean"] < 0.7:
    errs.append("weights dominate the ranking: mean rank stability %.2f" % sen["rank_stability_spearman"]["mean"])
elif sen["rank_stability_spearman"]["mean"] < 0.9:
    warns.append("rank stability under weight perturbation is soft: %.2f" % sen["rank_stability_spearman"]["mean"])
for k in ("effective_independent_bets", "avg_pairwise_correlation", "pc1_variance_share"):
    if k not in rsk: errs.append("risk profile missing " + k)
if "momentum_contamination" not in rep: errs.append("report card missing the contamination check")
if cov["blind_rescore_sample"]["status"].startswith("awaiting"):
    warns.append("false-negative rate is unmeasured: the blind re-score sample awaits research")

print("RIGOR")
print("  vintage 2026-08-28 locked, hash %s..., protocol registered %s" % (frz["sha256_scores"][:12], pro["registered"]))
print("  forward test: %s (%d snapshots) | contamination rho %.3f" %
      (rep["forward"]["status"], rep["snapshots"], rep["momentum_contamination"]["spearman_score_vs_trailing_year_return"]))
print("  weights vs measurement: rank stability %.3f | tier retention %.3f | alpha %.2f" %
      (sen["rank_stability_spearman"]["mean"], sen["tier_retention"]["mean"], sen["cronbach_alpha"]))
print("  risk: effective bets %.1f | avg corr %.2f | PC1 %.0f%% | investable HHI %.2f" %
      (rsk["effective_independent_bets"], rsk["avg_pairwise_correlation"],
       rsk["pc1_variance_share"] * 100, rsk["concentration_investable"]["hhi"]))
print("  coverage: %d near-miss names on the frontier, blind sample of %d registered" %
      (len(cov["near_miss_frontier"]), sum(len(v) for v in cov["blind_rescore_sample"]["picks"].values())))
for w in warns: print("  ~", w)
if errs:
    [print("  !", e) for e in errs]; sys.exit(1)
print("rigor audit: clean")
