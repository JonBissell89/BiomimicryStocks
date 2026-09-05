# -*- coding: utf-8 -*-
"""Freeze the v2.1 vintage beside v2.0 and register it, once.

Runs on the weekly runner, where the price cache holds the v2.1 engine's
names, so the freeze carries a price for every name on its own date. The
freeze file refuses to rewrite itself; this script is a no-op once the
protocol lists the v2.1 vintage. Steps, in order: freeze the engine file
(data/engine_tiers_v21.json) at the price cache date; write protocol v4
superseding v3 (preserved and hashed) with the vintage's hash; fulfil the
refresh queue obligation with register_logic.py --fulfill.
"""
import json, hashlib, os, subprocess, sys
from paths import DATA
import marketdb

R = os.path.join(DATA, "rigor")
here = os.path.dirname(os.path.abspath(__file__))
pro = json.load(open(os.path.join(R, "evaluation_protocol.json"), encoding="utf-8"))
if any(v.get("tag") == "v2.1" for v in pro.get("vintages", [])):
    print("v2.1 vintage already registered"); sys.exit(0)
eng = os.path.join(DATA, "engine_tiers_v21.json")
if not os.path.exists(eng):
    print("no v2.1 engine file; nothing to freeze"); sys.exit(0)
pc = marketdb.load_price_cache()
asof = pc["asof"]
names = [n["tk"] for t in json.load(open(eng, encoding="utf-8"))["tiers"] for n in t["names"]]
priced = sum(1 for tk in names if pc["px"].get(tk))
if priced < 0.8 * len(names):
    print("only %d of %d v2.1 names priced on %s; not freezing this week" % (priced, len(names), asof)); sys.exit(0)
fn = "freeze_v21_%s.json" % asof
r = subprocess.run([sys.executable, os.path.join(here, "freeze_vintage.py"), "v2.1", asof, eng], capture_output=True, text=True)
print(r.stdout.strip())
fz = json.load(open(os.path.join(R, fn), encoding="utf-8"))
old_sha = hashlib.sha256(json.dumps(pro, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
if not os.path.exists(os.path.join(R, "evaluation_protocol_v3.json")):
    json.dump(pro, open(os.path.join(R, "evaluation_protocol_v3.json"), "w", encoding="utf-8"), indent=1)
new = dict(pro)
new["registered"] = asof
y, m, d = asof.split("-")
new["vintages"] = pro["vintages"] + [{"tag": "v2.1", "file": fn, "asof": asof, "sha256_scores": fz["sha256_scores"], "logic": "v2.1",
    "n": len(fz["scores"]), "priced": priced,
    "endpoints": "the primary and secondary endpoints read on this vintage at horizon %d-%s-%s beside v2.0; the report card grades both and the comparison is published either way" % (int(y) + 1, m, d)}]
new["pending_vintage"] = dict(pro.get("pending_vintage", {}), status="frozen", file=fn, sha256_scores=fz["sha256_scores"], asof=asof)
new["supersedes"] = {"file": "evaluation_protocol_v3.json", "sha256": old_sha,
                     "reason": "registers the frozen v2.1 vintage beside v2.0; every v3 endpoint, prediction and the v2.0 vintage are preserved unchanged",
                     "chain": [pro.get("supersedes", {})]}
json.dump(new, open(os.path.join(R, "evaluation_protocol.json"), "w", encoding="utf-8"), indent=1)
print("protocol v4 registered: vintages", [v["tag"] for v in new["vintages"]], "| v2.1 hash", fz["sha256_scores"][:16])
r = subprocess.run([sys.executable, os.path.join(here, "register_logic.py"), "--fulfill",
                    "v2.1 universe re-screen (round1_v21.py on the recorded screen, rounds 2 to 4 on the admitted field) and ranked re-score on the amended measures; vintage frozen %s" % asof],
                   capture_output=True, text=True)
print(r.stdout.strip())
