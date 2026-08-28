"""Select the Round 4 deep-research field (~95) from R3 survivors."""
import os
from paths import DATA
import re
import pandas as pd

DATA = DATA
df = pd.read_csv(os.path.join(DATA, "round3_survivors_raw.csv"))
df["price"] = pd.to_numeric(df.price, errors="coerce")
df["cap"] = pd.to_numeric(df.marketCap, errors="coerce")

# dedupe cross-listings: keep canonical (prefer exchange listing, then higher volume proxy = larger cap consistency)
DROP = {"BRSYF", "BTSGU", "CLVLF", "CODGF", "MCHPP", "NONOF", "RSMDF", "STMEF", "TEVJF"}
df = df[~df.ticker.isin(DROP)].copy()

df["composite"] = df["need_score"] + df["r3_fin_score"]

a = df[df.verdict == "A"].sort_values("composite", ascending=False)
b = df[df.verdict == "B"].sort_values("composite", ascending=False)

sel = set()
# 1) all A priced <= $10 (the investable pipeline)
sel |= set(a[a.price <= 10].ticker)
# 2) top A overall to 70 slots
for t in a.ticker:
    if len(sel) >= 70: break
    sel.add(t)
# 3) need diversity: top-2 A per need not already in
for need, grp in a.groupby("need"):
    for t in grp.head(2).ticker:
        sel.add(t)
# 4) top sub-$10 B's with fin>=16 (15 slots)
b10 = b[(b.price <= 10) & (b.r3_fin_score >= 16)]
for t in b10.head(15).ticker:
    sel.add(t)
# 5) top B overall (10 slots)
for t in b.head(10).ticker:
    sel.add(t)

out = df[df.ticker.isin(sel)].sort_values(["verdict", "composite"], ascending=[True, False])
out.to_csv(os.path.join(DATA, "round4_field.csv"), index=False)
notsel = df[~df.ticker.isin(sel)]
notsel.assign(reason="R3: ranked below R4 cut (composite need+financial score)")[
    ["ticker", "company", "price", "cap", "need", "verdict", "r3_fin_score", "reason"]
].to_csv(os.path.join(DATA, "round3_belowcut_log.csv"), index=False)
print(f"R4 field: {len(out)} | A={sum(out.verdict=='A')} B={sum(out.verdict=='B')} | sub-$10: {(out.price<=10).sum()}")
print(out.need.value_counts().to_string())
