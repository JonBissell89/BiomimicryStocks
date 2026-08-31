# -*- coding: utf-8 -*-
"""Freeze the point-in-time vintage the forward test is scored against.

Written once and never rewritten: the file refuses to overwrite itself, its
hash is registered in the evaluation protocol, and audit_rigor.py fails the
build if either changes. The monthly judgment run may change live scores;
the evaluation always grades this vintage.
"""
import json, os, sys
from paths import DATA
from rigor_lib import load_names, sha_scores

P = os.path.join(DATA, "rigor", "freeze_2026-08-28.json")
if os.path.exists(P):
    print("freeze exists; refusing to rewrite a vintage"); sys.exit(0)
names = load_names()
px = json.load(open(os.path.join(DATA, "price_cache.json"), encoding="utf-8"))
doc = {"asof": "2026-08-28",
       "note": "scores and prices as committed on the freeze date; the forward test grades this vintage regardless of later score changes",
       "scores": {n["tk"]: {"score": n["score"], "tier": n["tier"], "gate": n["gate"]} for n in names},
       "prices": {n["tk"]: px["px"].get(n["tk"]) for n in names},
       "sha256_scores": sha_scores(names)}
json.dump(doc, open(P, "w", encoding="utf-8"), indent=1)
print("froze vintage 2026-08-28:", len(doc["scores"]), "names, hash", doc["sha256_scores"][:16])
