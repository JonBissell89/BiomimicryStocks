"""Check whether the 1,769 sec_only registrants actually trade (fairness pass)."""
import os
from paths import DATA
import warnings
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")
DATA = DATA
df = pd.read_csv(os.path.join(DATA, "round1_all_scores.csv"))
todo = df[df.status == "check_price"]["ticker"].tolist()
print(f"checking {len(todo)} sec_only tickers for active trading")

found = {}
for i in range(0, len(todo), 200):
    chunk = todo[i:i+200]
    try:
        px = yf.download(chunk, period="5d", progress=False, threads=True, auto_adjust=True)["Close"]
        if isinstance(px, pd.Series):
            px = px.to_frame(chunk[0])
        last = px.ffill().iloc[-1]
        for t, v in last.items():
            if pd.notna(v):
                found[t] = float(v)
    except Exception as e:
        print(f"chunk {i}: {type(e).__name__}")
    print(f"{min(i+200,len(todo))}/{len(todo)} checked, {len(found)} trade", flush=True)

out = pd.DataFrame([{"ticker": k, "price": v} for k, v in found.items()])
out.to_csv(os.path.join(DATA, "sec_only_traders.csv"), index=False)
print(f"RESULT: {len(found)} of {len(todo)} sec_only names have live prices; rest = no active market")
