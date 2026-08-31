# -*- coding: utf-8 -*-
"""Do the weights do the work, or does the measurement?

Monte Carlo over the six measure weights (each perturbed up to 20 percent,
renormalized to 100) with the ranking and fixed tier bands recomputed each
draw. If ranks reshuffle under small weight changes, the weights are the
signal and the rubric is not. Also reports the rubric's internal consistency
(Cronbach's alpha across the six measures) and the inter-measure correlation
matrix, so redundancy between measures is a number rather than a suspicion."""
import json, os
import numpy as np
from paths import DATA
from rigor_lib import load_names, group_scores, GROUPS, tier_of, spearman, ranks

rng = np.random.default_rng(42)
names = load_names()
raw = {n["tk"]: group_scores(n["dims"]) for n in names}
base_w = {g: mx for g, (_, mx) in GROUPS.items()}

def totals(w):
    return {tk: sum(raw[tk][g] / base_w[g] * w[g] for g in w) - nx["jx"]
            for tk, nx in ((n["tk"], n) for n in names)}

base = totals(base_w)
base_rank = ranks([base[n["tk"]] for n in names])
base_tier = {n["tk"]: tier_of(base[n["tk"]]) for n in names}
base_top10 = set(sorted(base, key=base.get, reverse=True)[:10])

N = 1000
taus, keeps, overlaps = [], [], []
for _ in range(N):
    w = {g: base_w[g] * rng.uniform(0.8, 1.2) for g in base_w}
    scale = 100 / sum(w.values()); w = {g: v * scale for g, v in w.items()}
    t = totals(w)
    taus.append(spearman([base[n["tk"]] for n in names], [t[n["tk"]] for n in names]))
    keeps.append(sum(tier_of(t[n["tk"]]) == base_tier[n["tk"]] for n in names) / len(names))
    overlaps.append(len(base_top10 & set(sorted(t, key=t.get, reverse=True)[:10])) / 10)

# internal consistency: six normalized measures as items over 53 names
M = np.array([[raw[n["tk"]][g] / base_w[g] for g in GROUPS] for n in names], float)
k = M.shape[1]
alpha = k / (k - 1) * (1 - M.var(axis=0, ddof=1).sum() / M.sum(axis=1).var(ddof=1))
corr = [[round(spearman(M[:, i], M[:, j]), 2) for j in range(k)] for i in range(k)]

doc = {"draws": N, "perturbation": "each weight x U(0.8,1.2), renormalized to 100",
       "rank_stability_spearman": {"mean": round(float(np.mean(taus)), 4),
                                   "p05": round(float(np.percentile(taus, 5)), 4),
                                   "min": round(float(np.min(taus)), 4)},
       "tier_retention": {"mean": round(float(np.mean(keeps)), 4),
                          "p05": round(float(np.percentile(keeps, 5)), 4)},
       "top10_overlap": {"mean": round(float(np.mean(overlaps)), 4),
                         "p05": round(float(np.percentile(overlaps, 5)), 4)},
       "cronbach_alpha": round(float(alpha), 3),
       "measures": list(GROUPS.keys()),
       "inter_measure_spearman": corr,
       "reading": "stability near 1 means the measurement, not the weights, produces the ranking; alpha far below 0.7 means the six measures are not one construct, which the framework accepts as long as it is stated"}
json.dump(doc, open(os.path.join(DATA, "rigor", "sensitivity.json"), "w"), indent=1)
print("sensitivity: rank stability mean %.3f (p05 %.3f) | tier retention %.3f | top10 overlap %.3f | alpha %.2f"
      % (doc["rank_stability_spearman"]["mean"], doc["rank_stability_spearman"]["p05"],
         doc["tier_retention"]["mean"], doc["top10_overlap"]["mean"], alpha))
