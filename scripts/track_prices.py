# -*- coding: utf-8 -*-
"""Weekly price snapshots for the ranked names: the forward test's raw data.

Appends the current price cache reading for every ranked ticker, at most once
per six days, so forward returns are computed from a steady record rather
than from whatever prices happen to be in memory when someone asks."""
from rigor_lib import load_names
import marketdb

pc = marketdb.load_price_cache()
names = [n["tk"] for n in load_names()]
doc = marketdb.load_price_track()
if doc["snapshots"] and doc["snapshots"][-1]["date"] >= pc["asof"]:
    print("price track: already holds", doc["snapshots"][-1]["date"]); raise SystemExit(0)
import datetime
if doc["snapshots"]:
    gap = (datetime.date.fromisoformat(pc["asof"]) -
           datetime.date.fromisoformat(doc["snapshots"][-1]["date"])).days
    if gap < 6:
        print("price track: last snapshot %d days old; weekly cadence holds" % gap); raise SystemExit(0)
marketdb.append_price_snapshot(pc["asof"], {tk: pc["px"].get(tk) for tk in names})
print("price track: snapshot %s appended (%d total)" % (pc["asof"], len(doc["snapshots"]) + 1))
