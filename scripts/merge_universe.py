"""Merge NASDAQ + SEC into one deduplicated company universe."""
import os
from paths import DATA
import re
import pandas as pd

DATA = DATA

n = pd.read_csv(os.path.join(DATA, "raw_nasdaq.csv"))
s = pd.read_csv(os.path.join(DATA, "raw_sec.csv"))

# --- Clean NASDAQ listed set ---
n["symbol"] = n["symbol"].astype(str).str.strip()
n["price"] = pd.to_numeric(n["lastsale"].astype(str).str.replace("$", "", regex=False), errors="coerce")
n["marketCap"] = pd.to_numeric(n["marketCap"], errors="coerce")

# Derivative securities are not companies: warrants, rights, units
deriv_name = n["name"].str.contains(r"\bWarrant|\bRight(s)?\b|\bUnit(s)? |\bUnits$", case=False, na=False)
deriv_sym = n["symbol"].str.contains(r"\^|[./](W|WS|R|U|RT|UN)$", na=False)
derivs = n[deriv_name | deriv_sym]
n = n[~(deriv_name | deriv_sym)].copy()
print(f"NASDAQ: removed {len(derivs)} warrants/units/rights, kept {len(n)}")

# Multiple share classes of same company: keep the more liquid (higher volume) per base name
n["base"] = n["name"].str.replace(r"\s+(Common Stock|Class [A-Z]|Ordinary Shares|American Depositary Shares|ADS|ADR).*$", "", regex=True, case=False).str.strip().str.upper()
n = n.sort_values("volume", ascending=False).drop_duplicates("base", keep="first")
print(f"NASDAQ after share-class dedup: {len(n)}")

# --- SEC set ---
s["ticker"] = s["ticker"].astype(str).str.strip().str.upper()
# drop derivative tickers
s = s[~s["ticker"].str.contains(r"-(WT|UN|RT|WS|R|U|W)$", na=False)]
# dedup by CIK (share classes)
s = s.drop_duplicates("cik_str", keep="first")
print(f"SEC after dedup: {len(s)}")

nasdaq_syms = set(n["symbol"])
# SEC tickers not on the NASDAQ list (dots/dashes normalization)
def norm(t): return re.sub(r"[.\-]", "", str(t))
nasdaq_norm = {norm(x) for x in nasdaq_syms}
sec_only = s[~s["ticker"].map(lambda t: norm(t) in nasdaq_norm)].copy()
print(f"SEC-only companies (mostly OTC/small registrants): {len(sec_only)}")

# --- Build unified universe ---
u1 = pd.DataFrame({
    "ticker": n["symbol"], "company": n["name"], "price": n["price"],
    "marketCap": n["marketCap"], "country": n["country"], "sector": n["sector"],
    "industry": n["industry"], "ipoyear": n["ipoyear"], "volume": n["volume"],
    "listing": "exchange",
})
u2 = pd.DataFrame({
    "ticker": sec_only["ticker"], "company": sec_only["title"], "price": None,
    "marketCap": None, "country": None, "sector": None, "industry": None,
    "ipoyear": None, "volume": None, "listing": "sec_only",
})
u = pd.concat([u1, u2], ignore_index=True)
u.to_csv(os.path.join(DATA, "universe.csv"), index=False)
derivs[["symbol", "name"]].to_csv(os.path.join(DATA, "excluded_derivative_securities.csv"), index=False)
print(f"UNIVERSE TOTAL: {len(u)} companies -> universe.csv")
