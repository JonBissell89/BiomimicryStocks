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

import marketdb
frz = need("freeze_2026-08-28.json")
pro = need("evaluation_protocol.json")
trk = marketdb.load_price_track()
rep = need("report_card.json")
sen = need("sensitivity.json")
rsk = need("risk_profile.json")
cov = need("coverage.json")
ufz = need("universe_freeze_2026-08-28.json")
utk = marketdb.load_universe_track()
fnr = need("fn_rescore.json")
rel = need("reliability.json")
fac = need("factor_internal.json")
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

# the universe vintage is intact and the protocol chain is unbroken
canon_u = json.dumps(sorted([[tk, v[0], v[1]] for tk, v in ufz["scores"].items()]), separators=(",", ":"))
if hashlib.sha256(canon_u.encode()).hexdigest() != ufz["sha256"]:
    errs.append("universe vintage does not match its own hash")
if "supersedes" in pro:
    old_p = need(pro["supersedes"]["file"])
    if old_p and hashlib.sha256(json.dumps(old_p, sort_keys=True, separators=(",", ":")).encode()).hexdigest() != pro["supersedes"]["sha256"]:
        errs.append("superseded protocol was edited after the fact")
if utk["snapshots"][0]["date"] != ufz["asof"]:
    errs.append("universe track does not start at the universe freeze")
if "pending_external" not in pro["endpoints"]:
    errs.append("the pending external factor test fell out of the protocol")

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
fn_registered = sum(b["n"] for b in fnr.get("batches", [{"n": 12}]))
if len(fnr["rows"]) != fn_registered:
    errs.append("fn_rescore rows do not cover the registered %d-name samples" % fn_registered)
if "estimated_fn_rate" not in fnr: errs.append("fn_rescore missing the rate estimate")
rel_registered = sum(b["n"] for b in rel.get("batches", [{"n": 8}]))
if len(rel["rows"]) != rel_registered or rel["n"] != rel_registered:
    errs.append("reliability rows do not cover the registered %d-name samples" % rel_registered)

# the judging logic matches its registered version, and market drift is queued
import register_logic
logic = register_logic.load()
if logic is None:
    errs.append("no registered logic version; run register_logic.py")
else:
    drifted = register_logic.drift(logic)
    if drifted:
        errs.append("judgment documents drifted unregistered (%s): run register_logic.py "
                    "--prose or --logic with a reason" % ", ".join(drifted))
rq_path = os.path.join(DATA, "refresh_queue.json")
if not os.path.exists(rq_path):
    errs.append("missing data/refresh_queue.json; run universe_refresh.py")
else:
    rq = json.load(open(rq_path, encoding="utf-8"))
    if rq.get("obligations"):
        warns.append("OPEN OBLIGATION from logic change %s: full universe re-screen and ranked re-score owed"
                     % rq["obligations"].get("logic_version"))
    if rq.get("pending_first_screen"):
        warns.append("%d new market entrants await a first-screen judgment" % len(rq["pending_first_screen"]))
    if rq.get("delisted_check"):
        warns.append("%d names flagged delisted_check await confirmation" % len(rq["delisted_check"]))
    if rq.get("last_refresh"):
        import datetime as _dt
        age = (_dt.date.today() - _dt.date.fromisoformat(rq["last_refresh"])).days
        if age > rq.get("cadence_days", 92) + 14:
            warns.append("universe refresh overdue: last ran %s" % rq["last_refresh"])

print("RIGOR")
print("  vintage 2026-08-28 locked, hash %s..., protocol registered %s" % (frz["sha256_scores"][:12], pro["registered"]))
print("  forward test: %s (%d snapshots) | contamination rho %.3f" %
      (rep["forward"]["status"], rep["snapshots"], rep["momentum_contamination"]["spearman_score_vs_trailing_year_return"]))
print("  weights vs measurement: rank stability %.3f | tier retention %.3f | alpha %.2f" %
      (sen["rank_stability_spearman"]["mean"], sen["tier_retention"]["mean"], sen["cronbach_alpha"]))
print("  risk: effective bets %.1f | avg corr %.2f | PC1 %.0f%% | investable HHI %.2f" %
      (rsk["effective_independent_bets"], rsk["avg_pairwise_correlation"],
       rsk["pc1_variance_share"] * 100, rsk["concentration_investable"]["hhi"]))
print("  universe: vintage of %d locked | %d priced tracked | forward %s" %
      (ufz["n"], len(utk["snapshots"][-1]["px"]), rep.get("universe", {}).get("status", "?")))
print("  blind re-score: MAD %.1f/50, rho %.2f | potential FN %s | attribution: idiosyncratic %.0f%% (internal)" %
      (fnr["agreement"]["mean_absolute_deviation_of_50"], fnr["agreement"]["spearman"],
       ",".join(fnr["potential_false_negatives"]["names"]) or "none", fac["idiosyncratic_share"] * 100))
print("  coverage: %d near-miss names on the frontier" % len(cov["near_miss_frontier"]))
for w in warns: print("  ~", w)
if errs:
    [print("  !", e) for e in errs]; sys.exit(1)
print("rigor audit: clean")
