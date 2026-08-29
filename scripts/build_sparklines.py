# -*- coding: utf-8 -*-
"""A year of weekly closes for each ranked company, so every row can show its own
shape rather than just today's price.

Small on purpose: 53 names times about 52 weekly closes, rounded, is roughly 25KB.
Values are normalised to the first close in the window so the page can draw them
without knowing anything about scale, and so a $400 stock and a $4 stock are
directly comparable by shape.
"""
import json, os, time, warnings
warnings.filterwarnings("ignore")
import pandas as pd, yfinance as yf
from paths import DATA

eng = json.load(open(os.path.join(DATA, "engine_tiers.json"), encoding="utf-8"))
tickers = [n["tk"] for t in eng["tiers"] for n in t["names"]]
print(f"fetching 1y weekly closes for {len(tickers)} names", flush=True)

out, got = {}, 0
CH = 25
for i in range(0, len(tickers), CH):
    part = tickers[i:i + CH]
    try:
        df = yf.download(part, period="1y", interval="1wk", progress=False,
                         threads=True, auto_adjust=True)["Close"]
    except Exception as e:
        print(f"  chunk {i}: {type(e).__name__}", flush=True)
        continue
    if isinstance(df, pd.Series):
        df = df.to_frame(part[0])
    for t in part:
        if t not in df.columns:
            continue
        s = df[t].dropna()
        if len(s) < 8:            # too short to say anything about shape
            continue
        base = float(s.iloc[0])
        if base <= 0:
            continue
        out[t] = [round(float(v) / base, 4) for v in s]
        got += 1
    if i + CH < len(tickers):
        time.sleep(6)
    print(f"  {min(i+CH,len(tickers))}/{len(tickers)}  have {got}", flush=True)

path = os.path.join(DATA, "spark.json")
json.dump({"asof": time.strftime("%Y-%m-%d"), "n": got, "s": out},
          open(path, "w", encoding="utf-8"), separators=(",", ":"))
print(f"\n{got}/{len(tickers)} with history | {os.path.getsize(path)/1024:.0f} KB", flush=True)
if got:
    lens = [len(v) for v in out.values()]
    print(f"points per name: {min(lens)} to {max(lens)}", flush=True)
