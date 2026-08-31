# -*- coding: utf-8 -*-
"""Weekly sampler for the Layer 0 time series.

Run from the weekly job before the rebuild. For every civilization stock it
appends this week's sample: the latest figure the record holds, carried
forward, so the charts are sampled on a steady weekly clock even though most
underlying assessments update yearly or slower. When a new assessment lands,
edit the latest point (or add one) in data/imbalance_series.json and the carry
picks it up from there. A flat stretch therefore means the science has not
re-measured yet, never that the stock stood still.
"""
import json, os, datetime
from paths import DATA

P = os.path.join(DATA, "imbalance_series.json")
doc = json.load(open(P, encoding="utf-8"))
today = datetime.date.today().isoformat()
appended = 0
for sid, e in doc["series"].items():
    pts = e["points"]
    last_d, last_v = pts[-1][0], pts[-1][1]
    days = (datetime.date.fromisoformat(today) - datetime.date.fromisoformat(last_d)).days
    if days >= 6:
        pts.append([today, last_v, "carried"])
        appended += 1
doc["asof"] = today[:7]
json.dump(doc, open(P, "w", encoding="utf-8"), indent=1)
print("imbalance series: %d of %d sampled this week (carried latest known values)"
      % (appended, len(doc["series"])))
