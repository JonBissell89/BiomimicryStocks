"""Pull all OTC/Pink-traded equities from Yahoo screener, then rebuild universe.csv."""
import os
from paths import DATA
import time
import pandas as pd
import yfinance as yf

DATA = DATA

q = yf.EquityQuery("and", [yf.EquityQuery("eq", ["region", "us"]), yf.EquityQuery("eq", ["exchange", "PNK"])])
rows, offset = [], 0
while True:
    for attempt in range(3):
        try:
            r = yf.screen(q, offset=offset, size=250, sortField="intradaymarketcap", sortAsc=False)
            break
        except Exception as e:
            print(f"retry offset={offset}: {e}", flush=True)
            time.sleep(5)
    else:
        break
    quotes = r.get("quotes", [])
    if not quotes:
        break
    for x in quotes:
        rows.append({
            "ticker": x.get("symbol"), "company": x.get("longName") or x.get("shortName"),
            "price": x.get("regularMarketPrice"), "marketCap": x.get("marketCap"),
            "exchange": x.get("exchange"), "quoteType": x.get("quoteType"),
        })
    offset += 250
    total = r.get("total", 0)
    if offset % 1000 == 0:
        print(f"{offset}/{total}", flush=True)
    if offset >= min(total, 9750):
        break
    time.sleep(0.6)

otc = pd.DataFrame(rows).drop_duplicates("ticker")
otc.to_csv(os.path.join(DATA, "raw_otc_yahoo.csv"), index=False)
print(f"OTC pulled: {len(otc)}")
