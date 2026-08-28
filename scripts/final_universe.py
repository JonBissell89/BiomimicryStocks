"""Combine exchange-listed + SEC-only + OTC into the final tournament universe."""
import os
from paths import DATA
import re
import pandas as pd

DATA = DATA

u = pd.read_csv(os.path.join(DATA, "universe.csv"))          # exchange + sec_only
otc = pd.read_csv(os.path.join(DATA, "raw_otc_yahoo.csv"))   # OTC/Pink

otc = otc[otc["quoteType"].fillna("EQUITY") == "EQUITY"].copy()
otc["listing"] = "otc"
otc = otc.rename(columns={"exchange": "exch"})
otc = otc[["ticker", "company", "price", "marketCap", "listing"]]
for col in ["country", "sector", "industry", "ipoyear", "volume"]:
    otc[col] = None

allc = pd.concat([u, otc], ignore_index=True)
allc["ticker"] = allc["ticker"].astype(str).str.strip().str.upper()
allc = allc.drop_duplicates("ticker", keep="first")

SUFFIX = re.compile(
    r"\b(INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|LTD|LIMITED|PLC|HOLDINGS?|HLDGS?|GROUP|SA|NV|AG|SE|AB|ASA|SPA|OYJ|KK|BHD|TBK|PJSC|JSC|LLC|LP|L P|THE|COM|CL A|CL B|CLASS [A-Z]|ADR|ADS|NEW|/[A-Z]+)\b\.?",
)
def normname(x):
    x = str(x).upper()
    x = re.sub(r"[^A-Z0-9 ]", " ", x)
    x = SUFFIX.sub(" ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x

allc["normname"] = allc["company"].map(normname)
# priority: exchange (0) > otc-with-cap (1) > otc (2) > sec_only (3)
prio = {"exchange": 0, "otc": 1, "sec_only": 3}
allc["prio"] = allc["listing"].map(prio)
allc.loc[(allc["listing"] == "otc") & (allc["marketCap"].isna()), "prio"] = 2
allc = allc.sort_values(["normname", "prio"])
dups = allc[allc.duplicated("normname", keep="first") & (allc["normname"] != "")]
allc = allc[~(allc.duplicated("normname", keep="first") & (allc["normname"] != ""))]

allc = allc.drop(columns=["prio"])
allc.to_csv(os.path.join(DATA, "universe_final.csv"), index=False)
dups[["ticker", "company", "listing"]].to_csv(os.path.join(DATA, "excluded_duplicate_listings.csv"), index=False)
print(f"cross-listing duplicates removed: {len(dups)}")
print(f"FINAL UNIVERSE: {len(allc)} unique companies")
print(allc["listing"].value_counts().to_dict())
print(f"with price data: {allc['price'].notna().sum()}, with mktcap: {allc['marketCap'].notna().sum()}")
