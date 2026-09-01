# -*- coding: utf-8 -*-
"""What is this portfolio actually one bet on?

From the year of weekly closes the repo already carries: per-name volatility,
average pairwise correlation, the effective number of independent bets (the
participation ratio of the correlation spectrum), the share of variance in
the first principal component, and concentration by need. A ranking can be
right about every company and still be a single wager in disguise; this
makes that a number."""
import json, os
import numpy as np
from paths import DATA
from rigor_lib import load_names

import marketdb
sp = marketdb.load_spark()["s"]
names = load_names()
need_of = {n["tk"]: (n["need"].split("·")[0].strip() or "other") for n in names}
inv = [n["tk"] for n in names if n["gate"] == "pass" and n["tier"] != "exit"]

# common window of weekly returns across every series
minlen = min(len(v) for v in sp.values())
R = {tk: np.diff(np.array(v[-minlen:], float)) / np.array(v[-minlen:], float)[:-1] for tk, v in sp.items()}
tks = sorted(R)
M = np.array([R[t] for t in tks])
C = np.corrcoef(M)
iu = np.triu_indices(len(tks), 1)
avg_corr = float(C[iu].mean())
ev = np.linalg.eigvalsh(C)
enb = float(ev.sum() ** 2 / (ev ** 2).sum())
pc1 = float(ev.max() / ev.sum())
vols = M.std(axis=1, ddof=1) * np.sqrt(52)
w = np.ones(len(tks)) / len(tks)
cov = np.cov(M)
port_vol = float(np.sqrt(w @ cov @ w) * np.sqrt(52))

def hhi(universe):
    from collections import Counter
    c = Counter(need_of.get(t, "other") for t in universe)
    tot = sum(c.values())
    return {"shares": {k: round(v / tot, 3) for k, v in sorted(c.items(), key=lambda x: -x[1])},
            "hhi": round(sum((v / tot) ** 2 for v in c.values()), 3)}

doc = {"window_weeks": int(minlen - 1), "names_with_series": len(tks),
       "avg_pairwise_correlation": round(avg_corr, 3),
       "effective_independent_bets": round(enb, 1),
       "pc1_variance_share": round(pc1, 3),
       "equal_weight_portfolio_vol_annual": round(port_vol, 3),
       "median_name_vol_annual": round(float(np.median(vols)), 3),
       "concentration_all_ranked": hhi([n["tk"] for n in names]),
       "concentration_investable": hhi(inv),
       "reading": "effective bets far below the name count, or a dominant first component, means the list is fewer wagers than it looks; the need concentration says which wager"}
json.dump(doc, open(os.path.join(DATA, "rigor", "risk_profile.json"), "w"), indent=1)
print("risk: %d names, %dw window | avg corr %.2f | effective bets %.1f of %d | PC1 %.0f%% | port vol %.0f%% | health share (investable) %s"
      % (len(tks), minlen - 1, avg_corr, enb, len(tks), pc1 * 100, port_vol * 100,
         doc["concentration_investable"]["shares"].get("Health")))
