# -*- coding: utf-8 -*-
"""Business descriptions for the names the description route can reach.

The v2.1 first screen attaches an uninformative code (software, services,
conglomerate, or any entry carrying the desc flag) to a Layer 0 stock by
reading the business description. The original enrichment read
profiles.jsonl, which is not in the checkout, so the descriptions live in
market.db now, fetched here from Yahoo profiles for the viable names whose
entry carries the route and that have none yet. Converges over runs: each
run fetches at most LIMIT names, records the ones that returned nothing so
they are not retried every week, and leaves everything else alone. The
enrich obligation follows: a viable name in a routed code is not cut on
need until its description has been read, and the cut reason says
`no description available` while it has none.

Usage: python fetch_profiles.py [limit]   (runs on the weekly runner)
"""
import json, os, sys, time, warnings
warnings.filterwarnings("ignore")
import pandas as pd
from paths import DATA
import marketdb

LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 600
P = json.load(open(os.path.join(DATA, "rubric", "prior_v21.json"), encoding="utf-8"))
routed_ind = {k for k, v in P["industry"].items()
              if "enrich" in v.get("flag", "") or "desc" in v.get("flag", "") or v["class"] in ("software", "services", "conglomerate")}
routed_y = {k for k, v in P["yahoo_industry"].items()
            if "desc" in v.get("flag", "") or v["class"] in ("software", "services", "conglomerate")}
r1 = pd.read_csv(os.path.join(DATA, "round1_final_scores.csv"))
alive = r1[(r1.status.fillna("") == "") & (r1.viability >= 9)]
want = alive[alive.industry.isin(routed_ind) | alive.y_industry.isin(routed_y)
             | alive.need.isin(["software", "services", "conglomerate", "unknown", "unmapped", "y-unmapped"])]
have = marketdb.load_profiles()
todo = [t for t in want.ticker if t not in have][:LIMIT]
print("routed viable names %d | with a profile %d | fetching %d this run" % (len(want), len([t for t in want.ticker if t in have]), len(todo)))
if not todo:
    raise SystemExit(0)

import yfinance as yf
got, empty = 0, 0
batch = {}
for i, t in enumerate(todo, 1):
    rec = {"summary": "", "industry": "", "sector": "", "fetched": time.strftime("%Y-%m-%d")}
    try:
        info = yf.Ticker(t).info or {}
        rec["summary"] = info.get("longBusinessSummary") or ""
        rec["industry"] = info.get("industry") or ""
        rec["sector"] = info.get("sector") or ""
        for k in ("marketCap", "currentPrice", "totalRevenue", "revenueGrowth", "grossMargins",
                  "freeCashflow", "totalCash", "totalDebt", "sharesOutstanding"):
            v = info.get(k)
            if isinstance(v, (int, float)):
                rec[k] = v
    except Exception as e:
        rec["error"] = type(e).__name__
    if rec["summary"]:
        got += 1
    else:
        empty += 1
    batch[t] = rec
    if i % 50 == 0:
        marketdb.save_profiles(batch); batch = {}
        print("  %d/%d  descriptions %d  empty %d" % (i, len(todo), got, empty), flush=True)
        time.sleep(15)
    else:
        time.sleep(0.6)
if batch:
    marketdb.save_profiles(batch)
print("profiles: %d fetched with a description, %d empty (recorded so they are not retried weekly)" % (got, empty))
