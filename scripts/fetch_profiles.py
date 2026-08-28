"""Fetch Yahoo profiles+financial snapshots for R1 pre-survivors, enrichment pool,
and sec_only traders. Incremental JSONL, resumable."""
import os
from paths import DATA
import json, os, time, warnings
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")
DATA = DATA
OUTF = os.path.join(DATA, "profiles.jsonl")

df = pd.read_csv(os.path.join(DATA, "round1_all_scores.csv"))
alive = df[df.status.isna() | (df.status == "")]

pre_surv = alive[alive.r1_score >= 36]["ticker"]
enrich = alive[((alive.need.isin(["unknown", "unmapped"])) |
                (alive.flag.astype(str).str.contains("enrich"))) & (alive.marketCap >= 2.5e7)]["ticker"]
sec_tr = pd.read_csv(os.path.join(DATA, "sec_only_traders.csv"))
sec_tr = sec_tr[sec_tr.price >= 0.05]["ticker"]

queue = pd.concat([pre_surv, enrich, sec_tr]).drop_duplicates().tolist()

done = set()
if os.path.exists(OUTF):
    with open(OUTF, encoding="utf-8") as f:
        for line in f:
            try: done.add(json.loads(line)["ticker"])
            except Exception: pass
queue = [t for t in queue if t not in done]
print(f"queue: {len(queue)} tickers to fetch ({len(done)} already done)", flush=True)

KEEP = ["sector","industry","longBusinessSummary","country","marketCap","currentPrice",
        "totalCash","totalDebt","totalRevenue","revenueGrowth","earningsGrowth","grossMargins",
        "operatingMargins","profitMargins","freeCashflow","operatingCashflow","sharesOutstanding",
        "floatShares","fullTimeEmployees","trailingEps","totalCashPerShare","debtToEquity",
        "currentRatio","returnOnEquity","enterpriseValue","priceToSalesTrailing12Months",
        "fiftyTwoWeekLow","fiftyTwoWeekHigh","averageVolume","exchange","quoteType","currency",
        "financialCurrency","website","longName"]

f = open(OUTF, "a", encoding="utf-8")
errs = 0
for n, t in enumerate(queue):
    rec = {"ticker": t}
    for attempt in range(2):
        try:
            i = yf.Ticker(t).get_info()
            if i and len(i) > 3:
                for k in KEEP:
                    v = i.get(k)
                    if k == "longBusinessSummary" and isinstance(v, str):
                        v = v[:1500]
                    rec[k] = v
                rec["ok"] = True
            else:
                rec["ok"] = False
            break
        except Exception as e:
            if attempt == 0:
                time.sleep(3)
            else:
                rec["ok"] = False
                rec["err"] = type(e).__name__
                errs += 1
    f.write(json.dumps(rec, default=str) + "\n")
    if n % 25 == 0:
        f.flush()
    if n % 250 == 0:
        print(f"{n}/{len(queue)} fetched, errs={errs}", flush=True)
    time.sleep(0.35)
f.close()
print(f"DONE: {len(queue)} fetched, {errs} errors", flush=True)
