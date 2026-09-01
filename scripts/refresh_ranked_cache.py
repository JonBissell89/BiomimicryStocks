# -*- coding: utf-8 -*-
"""Fresh weekly closes for the ranked names, written into the market database.

track_prices.py snapshots whatever the price cache holds at the cache's asof
date, so the weekly job must land fresh ranked prices in the cache first or
the forward test would re-record stale numbers under a new date. The guard
runs the other way too: if the fetch comes back badly short, the asof date is
left where it was, track_prices sees nothing new, and no snapshot is taken.
A missing week is honest; a stale week dressed as fresh is not.
"""
import json, os, time, warnings
warnings.filterwarnings("ignore")
import pandas as pd, yfinance as yf
from paths import DATA
import marketdb

eng = json.load(open(os.path.join(DATA, "engine_tiers.json"), encoding="utf-8"))
tickers = [n["tk"] for t in eng["tiers"] for n in t["names"]] + ["^GSPC"]

fresh = {}
for attempt in range(4):
    need = [t for t in tickers if t not in fresh]
    if not need:
        break
    if attempt:
        time.sleep(15 * attempt)
    try:
        px = yf.download(need, period="5d", progress=False, threads=True, auto_adjust=True)["Close"]
        if not len(px):
            continue
        if isinstance(px, pd.Series):
            px = px.to_frame(need[0])
        last = px.ffill().iloc[-1]
        for t in need:
            v = last.get(t)
            if pd.notna(v) and v > 0:
                fresh[t] = round(float(v), 4)
    except Exception as e:
        print("  attempt %d: %s" % (attempt + 1, type(e).__name__), flush=True)

FLOOR = int(0.8 * len(tickers))
pc = marketdb.load_price_cache()
if len(fresh) < FLOOR:
    print("only %d of %d ranked prices came back live (floor %d); cache asof stays %s and no snapshot will be taken"
          % (len(fresh), len(tickers), FLOOR, pc["asof"]))
    raise SystemExit(0)

pc["px"].update(fresh)
pc["asof"] = time.strftime("%Y-%m-%d")
marketdb.save_price_cache(pc)
missing = [t for t in tickers if t not in fresh]
print("ranked cache refreshed: %d of %d live, asof %s%s"
      % (len(fresh), len(tickers), pc["asof"],
         (" | missing " + ",".join(missing)) if missing else ""))
