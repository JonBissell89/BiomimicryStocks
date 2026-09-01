# -*- coding: utf-8 -*-
"""Price the companies a visitor is actually likely to type, before grinding
through the long tail.

Coverage percentage across 15,797 tickers is the wrong target: nobody types a
$4M OTC shell. Market cap is the right priority signal, so this walks the
universe largest-first. A visitor who types TSLA and gets no price experiences
the feature as broken; one who types a microcap and gets no price does not.
"""
import os
from paths import DATA
import json, os, sys, time, warnings
warnings.filterwarnings("ignore")
import pandas as pd, yfinance as yf

import marketdb

D = DATA
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000

cache = marketdb.load_price_cache()["px"]
sidx = json.load(open(os.path.join(D, "search_index.json"), encoding="utf-8"))
r1 = pd.read_csv(os.path.join(D, "round1_final_scores.csv"))
r1 = r1[r1.ticker.isin(sidx.keys())].copy()
r1["marketCap"] = pd.to_numeric(r1["marketCap"], errors="coerce").fillna(0)
r1 = r1.sort_values("marketCap", ascending=False)

want = [t for t in r1.ticker if not cache.get(t)][:N]
print(f"universe {len(sidx)} | priced {sum(1 for v in cache.values() if v)} | "
      f"fetching top {len(want)} unpriced by market cap", flush=True)
if want:
    caps = r1.set_index("ticker").marketCap
    print(f"  largest unpriced: {[f'{t} ${caps[t]/1e9:.0f}B' for t in want[:6]]}", flush=True)

CH, filled = 250, 0
for i in range(0, len(want), CH):
    part = want[i:i + CH]
    try:
        px = yf.download(part, period="5d", progress=False, threads=True, auto_adjust=True)["Close"]
        last = px.ffill().iloc[-1] if len(px) else pd.Series(dtype=float)
        for t in part:
            v = last.get(t)
            if pd.notna(v) and v > 0:
                cache[t] = round(float(v), 4); filled += 1
    except Exception as e:
        print(f"  chunk {i}: {type(e).__name__}", flush=True)
    marketdb.save_price_cache({"asof": time.strftime("%Y-%m-%d"), "px": cache})
    got = sum(1 for t in part if cache.get(t))
    print(f"  {min(i+CH,len(want))}/{len(want)}  filled {filled}  (this chunk {got}/{len(part)})",
          flush=True)
    if i + CH < len(want):
        # A chunk that returns nothing means Yahoo is in a hard-limit state; waiting
        # longer is the only thing that clears it, and hammering extends it.
        time.sleep(90 if got == 0 else 20)

live = sum(1 for v in cache.values() if v)
print(f"\nfilled {filled} | total priced {live}/{len(cache)} "
      f"({100*live/len(cache):.1f}%)", flush=True)
