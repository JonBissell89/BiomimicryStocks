# -*- coding: utf-8 -*-
"""Queue first-screen admissions that stage 2 has not judged.

The v2.1 description route converges over weekly profile fetches: each run
can admit names the recorded screen never read. Every admission owes a
Round 2 business read, so this script re-runs the v2.1 first screen on the
recorded universe and writes the unjudged admissions to
data/refresh_queue.json under pending_stage2, where the rigor audit warns
and the page shows the obligation until the research pipeline judges them.
"""
import json, os, subprocess, sys
from paths import DATA

R = os.path.join(DATA, "rigor")
here = os.path.dirname(os.path.abspath(__file__))
subprocess.run([sys.executable, os.path.join(here, "round1_v21.py"), os.path.join(DATA, "rubric", "prior_v21.json"),
                os.path.join(DATA, "classification_overrides.json")], check=True, stdout=subprocess.DEVNULL)
import pandas as pd
v = pd.read_csv(os.path.join(DATA, "round1_v21_scores.csv"))
judged = set()
for fn in os.listdir(R):
    if fn.startswith("v21_round2") and fn.endswith(".json"):
        judged |= {x["ticker"] for x in json.load(open(os.path.join(R, fn), encoding="utf-8"))["rows"]}
new = v[v.advance & ~v.advance_v20 & ~v.ticker.isin(judged)]
q = json.load(open(os.path.join(DATA, "refresh_queue.json"), encoding="utf-8"))
q["pending_stage2"] = [{"ticker": r.ticker, "need": r.need, "need_score": int(r.need_score), "via": str(r.changed)} for r in new.itertuples()]
q["descriptions_owed"] = int((v.reason == "no description available").sum())
q["log"] = (q.get("log") or [])[-30:] + [{"date": pd.Timestamp.today().strftime("%Y-%m-%d"), "event": "stage2 queue",
             "pending_stage2": len(new), "descriptions_on_file": int(v.has_description.sum()), "descriptions_owed": q["descriptions_owed"]}]
json.dump(q, open(os.path.join(DATA, "refresh_queue.json"), "w", encoding="utf-8"), indent=1)
print("stage 2 queue: %d admissions unjudged | descriptions on file %d | owed %d" % (len(new), int(v.has_description.sum()), q["descriptions_owed"]))
