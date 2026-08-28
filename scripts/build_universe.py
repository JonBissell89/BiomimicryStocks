import os
"""Build the full stock universe from primary sources.

Sources:
  1. NASDAQ screener API  - NASDAQ + NYSE + AMEX listed stocks (price, mktcap, sector, industry, country)
  2. stockanalysis.com    - broad US universe including OTC
  3. SEC EDGAR            - registered filers (ticker/CIK), cross-check + OTC pickup
"""
from paths import DATA
import json, sys, time
import requests
import pandas as pd

OUT = DATA
HDRS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

def nasdaq_screener():
    url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0&download=true"
    r = requests.get(url, headers={**HDRS, "Origin": "https://www.nasdaq.com", "Referer": "https://www.nasdaq.com/"}, timeout=60)
    r.raise_for_status()
    rows = r.json()["data"]["rows"]
    df = pd.DataFrame(rows)
    df["source"] = "nasdaq_screener"
    print(f"NASDAQ screener: {len(df)} rows", flush=True)
    return df

def stockanalysis():
    # stockanalysis.com screener API - request all US stocks incl OTC
    url = ("https://api.stockanalysis.com/api/screener/s/f"
           "?m=marketCap&s=desc"
           "&c=s,n,price,marketCap,sector,industry,exchange,country,revenue"
           "&cn=25000&i=stocks")
    r = requests.get(url, headers=HDRS, timeout=120)
    r.raise_for_status()
    data = r.json()["data"]["data"]
    df = pd.DataFrame(data)
    df["source"] = "stockanalysis"
    print(f"stockanalysis.com: {len(df)} rows", flush=True)
    return df

def sec_tickers():
    # SEC requires a contact address in the User-Agent and will block you without
    # one. It comes from the environment so a real address never lands in the repo.
    contact = os.environ.get("SEC_CONTACT")
    if not contact:
        raise SystemExit(
            "Set SEC_CONTACT to an email address before fetching from SEC EDGAR.\n"
            '  PowerShell:  $env:SEC_CONTACT = "you@example.com"\n'
            "  CI:          add SEC_CONTACT as a repository secret\n"
            "SEC blocks requests without a contact in the User-Agent.")
    url = "https://www.sec.gov/files/company_tickers.json"
    r = requests.get(url, headers={"User-Agent": f"Individual Investor {contact}"},
                     timeout=60)
    r.raise_for_status()
    d = r.json()
    df = pd.DataFrame.from_dict(d, orient="index")
    df["source"] = "sec_edgar"
    print(f"SEC EDGAR tickers: {len(df)} rows", flush=True)
    return df

results = {}
for name, fn in [("nasdaq", nasdaq_screener), ("stockanalysis", stockanalysis), ("sec", sec_tickers)]:
    try:
        results[name] = fn()
        results[name].to_csv(os.path.join(OUT, f"raw_{name}.csv"), index=False)
    except Exception as e:
        print(f"FAILED {name}: {type(e).__name__}: {e}", flush=True)

print("done:", {k: len(v) for k, v in results.items()})
