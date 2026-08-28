"""Assemble the final tournament output: Top 25 (price <= $10), Watch Below $10,
near misses. Produces final_top25.csv, final_watch.csv, final_nearmiss.csv."""
import os
from paths import DATA
import glob
import pandas as pd

DATA = DATA

deep = pd.concat([pd.read_csv(f, on_bad_lines="skip") for f in sorted(glob.glob(os.path.join(DATA, "final_deep_f*.csv")))],
                 ignore_index=True)
deep["ticker"] = deep.ticker.astype(str).str.strip().str.upper()
deep = deep.drop_duplicates("ticker", keep="last")

light = pd.concat([pd.read_csv(f, on_bad_lines="skip") for f in sorted(glob.glob(os.path.join(DATA, "final_light_w*.csv")))],
                  ignore_index=True)
light["ticker"] = light.ticker.astype(str).str.strip().str.upper()
light = light.drop_duplicates("ticker", keep="last")

def pnum(x):
    import re
    m = re.search(r"([0-9]+\.?[0-9]*)", str(x).replace(",", ""))
    return float(m.group(1)) if m else None

deep["px"] = deep.price.map(pnum)
light["px"] = light.price.map(pnum)
deep["total"] = deep.total.map(pnum)
light["total"] = light.total.map(pnum)

top = deep[deep.px <= 10].sort_values("total", ascending=False)
over_deep = deep[deep.px > 10]

r4 = pd.read_csv(os.path.join(DATA, "round4_results.csv"))
r4["ticker"] = r4.ticker.astype(str).str.strip().str.upper()
need = dict(zip(r4.ticker, r4.need))
company = {}
f4 = pd.read_csv(os.path.join(DATA, "round4_field.csv"))
for r in f4.itertuples():
    company[r.ticker.upper()] = r.company

top = top.assign(need=top.ticker.map(need), company=top.ticker.map(company))
top.to_csv(os.path.join(DATA, "final_top25.csv"), index=False)

watch = light.sort_values("total", ascending=False).assign(
    need=light.ticker.map(need), company=light.ticker.map(company))
# add any deep-track names that verified above $10
for r in over_deep.itertuples():
    watch = pd.concat([watch, pd.DataFrame([{
        "ticker": r.ticker, "price": r.price, "marketCap": r.marketCap,
        "latest_quarter": "", "catalyst": getattr(r, "catalysts", ""),
        "total": r.total, "why_watch": getattr(r, "top25_case", ""),
        "px": r.px, "need": need.get(r.ticker), "company": company.get(r.ticker),
    }])], ignore_index=True)
watch = watch.sort_values("total", ascending=False)
watch.to_csv(os.path.join(DATA, "final_watch.csv"), index=False)

print(f"TOP (price<=10): {len(top)}")
for r in top.itertuples():
    print(f"  {r.total:>3.0f} {r.ticker:6s} ${r.px:<6.2f} {str(r.need)[:12]}")
print(f"\nWATCH (>$10): {len(watch)}")
for r in watch.head(40).itertuples():
    print(f"  {pnum(r.total):>3.0f} {r.ticker:6s} ${r.px}")
