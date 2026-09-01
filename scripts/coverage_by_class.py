# -*- coding: utf-8 -*-
"""Raw coverage percentage is the wrong measure. What matters is whether the
companies a visitor would plausibly type are priced. Exchange-listed tickers are
1 to 4 characters; 5-character tickers ending F or Y are thin OTC lines."""
import os
from paths import DATA
import json
D = DATA
import marketdb
px = marketdb.load_price_cache()["px"]
sidx = json.load(open(os.path.join(D, "search_index.json"), encoding="utf-8"))

def cls(t):
    if len(t) <= 4:
        return "exchange-listed (1-4 char)"
    if t.endswith("F"):
        return "OTC foreign ordinary (…F)"
    if t.endswith("Y"):
        return "OTC depositary receipt (…Y)"
    return "other 5-char"

g = {}
for t in sidx:
    k = cls(t)
    g.setdefault(k, [0, 0])
    g[k][0] += 1
    if px.get(t):
        g[k][1] += 1
for k in sorted(g, key=lambda x: -g[x][0]):
    tot, got = g[k]
    print(f"  {k:<30s} {got:>5d}/{tot:<5d}  {100*got/tot:5.1f}%")

WELL_KNOWN = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "BRK-B", "JPM",
              "XOM", "JNJ", "WMT", "PG", "KO", "DIS", "NFLX", "AMD", "INTC", "BA", "F",
              "GME", "AMC", "PLTR", "SOFI", "COIN", "RIVN", "LCID", "NIO", "ACB", "AGI",
              "MFC", "DFTX", "AQN", "IONQ", "EVTL", "GEVO", "ABAT"]
have = [t for t in WELL_KNOWN if px.get(t)]
miss = [t for t in WELL_KNOWN if t in sidx and not px.get(t)]
notin = [t for t in WELL_KNOWN if t not in sidx]
print(f"\n  well-known sample: {len(have)}/{len(WELL_KNOWN)} priced")
if miss:
    print(f"  in the index but unpriced: {miss}")
if notin:
    print(f"  not in the search index at all: {notin}")
