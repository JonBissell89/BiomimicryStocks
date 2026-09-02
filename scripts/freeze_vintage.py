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
import marketdb

# python freeze_vintage.py [tag] [asof] [engine_path]
# defaults reproduce the original v2.0 freeze; a later logic version freezes
# its own engine file beside it, and both are graded by the report card.
tag = sys.argv[1] if len(sys.argv) > 1 else "v2.0"
asof = sys.argv[2] if len(sys.argv) > 2 else "2026-08-28"
engine = sys.argv[3] if len(sys.argv) > 3 else None
fn = "freeze_2026-08-28.json" if tag == "v2.0" else "freeze_%s_%s.json" % (tag.replace(".", ""), asof)
P = os.path.join(DATA, "rigor", fn)
if os.path.exists(P):
    print("freeze exists; refusing to rewrite a vintage"); sys.exit(0)
names = load_names(engine)
px = marketdb.load_price_cache()
doc = {"asof": asof, "logic": tag,
       "note": "scores and prices as committed on the freeze date; the forward test grades this vintage regardless of later score changes",
       "scores": {n["tk"]: {"score": n["score"], "tier": n["tier"], "gate": n["gate"]} for n in names},
       "prices": {n["tk"]: px["px"].get(n["tk"]) for n in names},
       "sha256_scores": sha_scores(names)}
json.dump(doc, open(P, "w", encoding="utf-8"), indent=1)
print("froze vintage %s (%s): %d names, hash %s" % (tag, asof, len(doc["scores"]), doc["sha256_scores"][:16]))
