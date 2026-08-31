# -*- coding: utf-8 -*-
"""Shared pieces of the rigor layer: ranks, correlations, group scores."""
import json, os, hashlib
import numpy as np
from paths import DATA

GROUPS = {"A": (["A"], 20), "B": (["B"], 25), "C": (["C1", "C2"], 20),
          "D": (["D_rep", "D_inhib", "D_exit"], 15), "E": (["E"], 10),
          "F": (["F_clock", "F_now"], 10)}
BANDS = [(80, "t1"), (74, "t2"), (69, "t3"), (65, "t4")]

def load_names():
    eng = json.load(open(os.path.join(DATA, "engine_tiers.json"), encoding="utf-8"))
    out = []
    for t in eng["tiers"]:
        for n in t["names"]:
            out.append({"tk": n["tk"], "score": n["score"], "tier": t["id"],
                        "gate": n["gate"], "need": n.get("need", ""),
                        "jx": n.get("jx_penalty", 0), "dims": n["dims"]})
    return out

def group_scores(dims):
    return {g: sum(dims[k] for k in ks) for g, (ks, mx) in GROUPS.items()}

def tier_of(total):
    for cut, t in BANDS:
        if total >= cut: return t
    return "exit"

def ranks(v):
    v = np.asarray(v, dtype=float)
    order = np.argsort(v)
    r = np.empty(len(v)); r[order] = np.arange(1, len(v) + 1)
    # average ranks for ties
    out = r.copy()
    for val in np.unique(v):
        m = v == val
        if m.sum() > 1: out[m] = r[m].mean()
    return out

def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ra -= ra.mean(); rb -= rb.mean()
    d = np.sqrt((ra**2).sum() * (rb**2).sum())
    return float((ra * rb).sum() / d) if d else 0.0

def sha_scores(names):
    canon = json.dumps(sorted([[n["tk"], n["score"], n["tier"], n["gate"]] for n in names]),
                       separators=(",", ":"))
    return hashlib.sha256(canon.encode()).hexdigest()
