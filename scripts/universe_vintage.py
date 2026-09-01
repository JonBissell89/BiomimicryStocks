# -*- coding: utf-8 -*-
"""Freeze and track the WHOLE universe, not just the ranked 53.

Every one of the 15,797 companies carries a first-screen judgment (need plus
viability, out of 50) and a funnel stage. Accuracy of the screen means those
judgments face a forward test too: high first-screen scores should not
systematically underperform low ones if the screen means anything, and the
advanced group should not be beaten by the cut group. This freezes the
universe vintage once (hash-locked, refuses rewrite) and appends a universe
price snapshot every 28 days (roughly 200KB per snapshot, 13 per year)."""
import json, os, sys, hashlib, datetime
from paths import DATA
import marketdb

R = os.path.join(DATA, "rigor")
FRZ = os.path.join(R, "universe_freeze_2026-08-28.json")
si = json.load(open(os.path.join(DATA, "search_index.json"), encoding="utf-8"))
pc = marketdb.load_price_cache()

if not os.path.exists(FRZ):
    scores = {tk: [v[1], v[2]] for tk, v in si.items()}   # [stage, first-screen score]
    canon = json.dumps(sorted([[tk, s, sc] for tk, (s, sc) in scores.items()]), separators=(",", ":"))
    doc = {"asof": "2026-08-28", "n": len(scores),
           "note": "stage and first-screen score (out of 50) for every company that entered; the universe forward test grades this vintage",
           "sha256": hashlib.sha256(canon.encode()).hexdigest(),
           "scores": scores}
    json.dump(doc, open(FRZ, "w", encoding="utf-8"), separators=(",", ":"))
    print("universe vintage frozen: %d names, hash %s" % (len(scores), doc["sha256"][:16]))
else:
    print("universe vintage exists; refusing to rewrite")

doc = marketdb.load_universe_track()
last = doc["snapshots"][-1]["date"] if doc["snapshots"] else None
if last and (datetime.date.fromisoformat(pc["asof"]) - datetime.date.fromisoformat(last)).days < 28:
    print("universe track: last snapshot %s; 28-day cadence holds" % last); sys.exit(0)
if last == pc["asof"]:
    sys.exit(0)
px = {tk: round(p, 4) for tk, p in pc["px"].items() if p and tk in si}
marketdb.append_universe_snapshot(pc["asof"], px)
print("universe track: snapshot %s appended (%d priced, %d total snapshots)"
      % (pc["asof"], len(px), len(doc["snapshots"]) + 1))
