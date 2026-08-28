"""Prepare Round 2 judgment batches: survivors + their business summaries,
sliced into text files for close reading."""
import os
from paths import DATA
import json, os, re, textwrap
import pandas as pd

DATA = DATA
BDIR = os.path.join(DATA, "r2_batches")
os.makedirs(BDIR, exist_ok=True)

df = pd.read_csv(os.path.join(DATA, "round1_final_scores.csv"))
surv = df[(df.status == "") | (df.status.isna())].copy()
# R1 cut: need alignment >= 20 with viability floor (cap >= $25M -> viability >= 9).
# Need-first so small caps are not double-penalized for size.
cut_low_need = surv[surv.need_score < 20]
cut_low_via = surv[(surv.need_score >= 20) & (surv.viability < 9)]
surv = surv[(surv.need_score >= 20) & (surv.viability >= 9)].copy()
cut_low_need = cut_low_need.assign(reason="R1: need alignment below threshold (score "
                                   + cut_low_need.need_score.astype(str) + "/30, need=" + cut_low_need.need.astype(str) + ")")
cut_low_via = cut_low_via.assign(reason="R1: market cap below $25M viability floor")
pd.concat([cut_low_need, cut_low_via])[["ticker","company","price","marketCap","need","r1_score","reason"]].to_csv(
    os.path.join(DATA, "round1_cut_log.csv"), index=False)
print(f"R1 cut: {len(cut_low_need)} low-need, {len(cut_low_via)} low-viability -> {len(surv)} advance")

profs = {}
with open(os.path.join(DATA, "profiles.jsonl"), encoding="utf-8") as f:
    for line in f:
        try:
            j = json.loads(line)
            if j.get("ok"):
                profs[j["ticker"]] = j
        except Exception:
            pass

surv["summary"] = surv["ticker"].map(lambda t: (profs.get(t) or {}).get("longBusinessSummary") or "")
surv["y_ind"] = surv["ticker"].map(lambda t: (profs.get(t) or {}).get("industry") or "")
surv["revGrowth"] = surv["ticker"].map(lambda t: (profs.get(t) or {}).get("revenueGrowth"))
surv["grossM"] = surv["ticker"].map(lambda t: (profs.get(t) or {}).get("grossMargins"))
surv["revenue"] = surv["ticker"].map(lambda t: (profs.get(t) or {}).get("totalRevenue"))

# Philosophy hard rule, programmatic: clinical/preclinical-stage with no meaningful
# revenue and no approved/marketed product = "single unproven breakthrough required".
sl = surv["summary"].str.lower().fillna("")
rev = pd.to_numeric(surv["revenue"], errors="coerce").fillna(0)
clinical = (sl.str.contains(r"clinical[- ]stage|preclinical|pre-clinical", regex=True)
            & ~sl.str.contains(r"approved|commercializ|marketed|launched|fda-cleared|ce mark", regex=True)
            & (rev < 1e7))
cut_clin = surv[clinical]
cut_clin.assign(reason="R1.5: clinical/preclinical-stage, no approved product, revenue<$10M - "
                       "depends on single unproven scientific breakthrough (hard rejection rule)")[
    ["ticker","company","price","marketCap","need","r1_score","reason"]].to_csv(
    os.path.join(DATA, "round1_clinical_cut_log.csv"), index=False)
surv = surv[~clinical].copy()
print(f"clinical-stage pre-revenue cut: {len(cut_clin)} -> {len(surv)} advance to R2 judgment")

surv = surv.sort_values(["need", "r1_score"], ascending=[True, False]).reset_index(drop=True)
surv.to_csv(os.path.join(DATA, "round2_candidates.csv"), index=False)
print(f"R2 candidates: {len(surv)}")
print(surv["need"].value_counts().to_string())

def fmt_cap(c):
    try:
        c = float(c)
        return f"${c/1e9:.2f}B" if c >= 1e9 else f"${c/1e6:.0f}M"
    except Exception:
        return "?"

BATCH = 55
nb = 0
for i in range(0, len(surv), BATCH):
    nb += 1
    with open(os.path.join(BDIR, f"batch_{nb:02d}.txt"), "w", encoding="utf-8") as f:
        for r in surv.iloc[i:i+BATCH].itertuples():
            rg = f"{float(r.revGrowth)*100:.0f}%" if pd.notna(r.revGrowth) else "?"
            gm = f"{float(r.grossM)*100:.0f}%" if pd.notna(r.grossM) else "?"
            rev = fmt_cap(r.revenue) if pd.notna(r.revenue) else "?"
            summ = re.sub(r"\s+", " ", str(r.summary))[:600]
            f.write(f"[{r.ticker}] {str(r.company)[:70]} | px=${r.price} cap={fmt_cap(r.marketCap)} "
                    f"| need={r.need} r1={r.r1_score} | ind={r.y_ind or r.industry} "
                    f"| rev={rev} growth={rg} gm={gm}\n{summ}\n\n")
print(f"{nb} batch files written to {BDIR}")
