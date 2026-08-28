# -*- coding: utf-8 -*-
"""Fill the price cache, converging over repeated passes.

Yahoo rate-limits sustained bulk quoting: an isolated 400-ticker chunk prices 98%,
the same code under continuous load prices ~22%. So this does not try to win in one
sweep. It makes passes, backing off harder each time, and stops when a pass stops
recovering. Every chunk is written to disk, so it is resumable and never restarts.

Run standalone, or from the monthly job before refresh_app.py.
"""
import os
from paths import DATA
import json, os, sys, time, warnings
warnings.filterwarnings("ignore")
import pandas as pd, yfinance as yf

D = DATA
OUT = os.path.join(D, "price_cache.json")
sidx = json.load(open(os.path.join(D, "search_index.json"), encoding="utf-8"))
universe = sorted(sidx.keys())

cache = {}
if os.path.exists(OUT):
    try:
        cache = json.load(open(OUT, encoding="utf-8"))["px"]
    except Exception:
        cache = {}
for t in universe:
    cache.setdefault(t, None)

def save():
    json.dump({"asof": time.strftime("%Y-%m-%d"), "px": cache},
              open(OUT, "w", encoding="utf-8"), separators=(",", ":"))

def priced():
    return sum(1 for v in cache.values() if v)

MAX_PASSES = int(sys.argv[1]) if len(sys.argv) > 1 else 6
CH = 400
print(f"universe {len(universe)} | priced {priced()}", flush=True)

for p in range(1, MAX_PASSES + 1):
    gaps = [t for t in universe if not cache.get(t)]
    if not gaps:
        break
    pause = 10 * p                      # 10s, 20s, 30s ... back off each pass
    start = priced()
    print(f"\npass {p}: {len(gaps)} gaps, {pause}s between chunks", flush=True)
    for i in range(0, len(gaps), CH):
        part = gaps[i:i + CH]
        try:
            px = yf.download(part, period="5d", progress=False,
                             threads=True, auto_adjust=True)["Close"]
            last = px.ffill().iloc[-1] if len(px) else pd.Series(dtype=float)
            for t in part:
                v = last.get(t)
                if pd.notna(v) and v > 0:
                    cache[t] = round(float(v), 4)
        except Exception as e:
            print(f"    chunk {i}: {type(e).__name__}", flush=True)
        save()
        if i + CH < len(gaps):
            time.sleep(pause)
    gained = priced() - start
    print(f"  pass {p} recovered {gained} -> {priced()}/{len(universe)} "
          f"({100*priced()/len(universe):.1f}%)", flush=True)
    if gained < 50:
        print("  pass stopped recovering, converged", flush=True)
        break

save()
live = priced()
print(f"\nfinal: {live}/{len(universe)} priced ({100*live/len(universe):.1f}%) | "
      f"{os.path.getsize(OUT)/1024:.0f} KB", flush=True)
short = [t for t in universe if len(t) <= 4]
sl = sum(1 for t in short if cache.get(t))
print(f"exchange-listed (1-4 char): {sl}/{len(short)} ({100*sl/len(short):.1f}%)", flush=True)
