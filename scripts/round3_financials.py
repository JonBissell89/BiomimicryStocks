"""Round 3: merge R2 verdicts, verify coverage, apply financial screens.

Inputs : round2_candidates.csv, r2_verdicts_a1..a8.csv, profiles.jsonl
Outputs: round2_results.csv (all verdicts+reasons), round3_scored.csv,
         round3_survivors.csv, round3_cut_log.csv, r2_missing.csv (coverage gaps)
"""
import os
from paths import DATA
import glob, json
import numpy as np
import pandas as pd

DATA = DATA

cand = pd.read_csv(os.path.join(DATA, "round2_candidates.csv"))

# ---- merge verdicts (repair file takes precedence over originals) ----
vs = []
files = sorted(glob.glob(os.path.join(DATA, "r2_verdicts_*.csv")))
files = [f for f in files if "repair" in f] + [f for f in files if "repair" not in f]
for f in files:
    try:
        v = pd.read_csv(f, on_bad_lines="skip")
        v.columns = [c.strip().lower() for c in v.columns]
        v = v[["ticker", "verdict", "reason"]]
        v["judge"] = f.split("_")[-1].replace(".csv", "")
        vs.append(v)
    except Exception as e:
        print(f"BAD FILE {f}: {e}")
v = pd.concat(vs, ignore_index=True)
v["ticker"] = v["ticker"].astype(str).str.strip().str.upper()
v["verdict"] = v["verdict"].astype(str).str.strip().str.upper().str[0]
v = v[v["verdict"].isin(list("ABC"))]
v = v.drop_duplicates("ticker", keep="first")
print(f"verdicts parsed: {len(v)} | A={sum(v.verdict=='A')} B={sum(v.verdict=='B')} C={sum(v.verdict=='C')}")

m = cand.merge(v[["ticker", "verdict", "reason"]], on="ticker", how="left", suffixes=("", "_r2"))
missing = m[m["verdict"].isna()]
missing.to_csv(os.path.join(DATA, "r2_missing.csv"), index=False)
print(f"coverage gaps (no verdict): {len(missing)}")
m.to_csv(os.path.join(DATA, "round2_results.csv"), index=False)

# ---- Round 3 financial screens on A + B ----
profs = {}
with open(os.path.join(DATA, "profiles.jsonl"), encoding="utf-8") as f:
    for line in f:
        try:
            j = json.loads(line)
            if j.get("ok"):
                profs[j["ticker"]] = j
        except Exception:
            pass

surv = m[m["verdict"].isin(["A", "B"])].copy()

def g(t, k):
    x = (profs.get(t) or {}).get(k)
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan

for k in ["totalCash", "totalDebt", "freeCashflow", "operatingCashflow", "totalRevenue",
          "revenueGrowth", "grossMargins", "operatingMargins", "debtToEquity",
          "sharesOutstanding", "floatShares", "fullTimeEmployees", "earningsGrowth"]:
    surv[k] = surv["ticker"].map(lambda t, k=k: g(t, k))

rows = []
for r in surv.itertuples(index=False):
    cap = pd.to_numeric(r.marketCap, errors="coerce")
    score, notes, cut = 0, [], None

    # Growth / expansion signal (0-10)
    rg = r.revenueGrowth
    if pd.notna(rg):
        if rg >= 0.25: score += 10
        elif rg >= 0.12: score += 8
        elif rg >= 0.05: score += 6
        elif rg >= 0.00: score += 3
        else:
            score += 0; notes.append(f"revenue shrinking {rg:.0%}")
    else:
        score += 3; notes.append("growth unknown")

    # Survivability (0-10)
    cash, fcf, debt = r.totalCash, r.freeCashflow, r.totalDebt
    s = 5
    if pd.notna(fcf) and fcf > 0:
        s = 9
        if pd.notna(debt) and pd.notna(cash) and debt > cash and pd.notna(cap) and debt - cash > 2.5 * cap:
            s = 4; notes.append("heavy net debt vs cap")
    elif pd.notna(fcf) and fcf < 0 and pd.notna(cash) and cash > 0:
        runway = cash / abs(fcf)
        if runway >= 3: s = 7
        elif runway >= 1.5: s = 5
        elif runway >= 0.75: s = 3; notes.append(f"runway {runway:.1f}y")
        else: s = 1; notes.append(f"runway {runway:.1f}y - dilution imminent")
    score += s

    # Margin quality (0-5)
    gm = r.grossMargins
    if pd.notna(gm):
        if gm >= 0.45: score += 5
        elif gm >= 0.30: score += 4
        elif gm >= 0.18: score += 2
        else: score += 1; notes.append(f"thin gm {gm:.0%}")
    else:
        score += 2

    # Commercial reality
    rev = r.totalRevenue
    if pd.notna(rev) and rev < 5e6 and (pd.isna(rg) or rg < 0.5):
        cut = "pre-commercial: revenue <$5M without hypergrowth"
    if pd.notna(rg) and rg < -0.15:
        cut = f"contractionary: revenue {rg:.0%}"
    if pd.notna(fcf) and fcf < 0 and pd.notna(cash) and cash > 0 and cash / abs(fcf) < 0.6 and (pd.isna(cap) or cap < 5e8):
        cut = "runway <0.6y small-cap - forced dilution/financing dependence"

    rows.append({**r._asdict(), "r3_fin_score": score, "r3_notes": "; ".join(notes), "r3_cut": cut})

out = pd.DataFrame(rows)
out.to_csv(os.path.join(DATA, "round3_scored.csv"), index=False)
cut = out[out.r3_cut.notna()]
keep = out[out.r3_cut.isna()]
cut[["ticker", "company", "price", "marketCap", "need", "verdict", "r3_cut"]].to_csv(os.path.join(DATA, "round3_cut_log.csv"), index=False)
keep.to_csv(os.path.join(DATA, "round3_survivors_raw.csv"), index=False)
print(f"R3: {len(surv)} in -> {len(cut)} cut, {len(keep)} pass financial screens")
print("\npass by verdict:", keep["verdict"].value_counts().to_dict())
print("pass, fin-score distribution:")
print(keep["r3_fin_score"].describe().round(1).to_string())
for c in [14, 16, 18, 20]:
    a = keep[(keep.verdict == "A") & (keep.r3_fin_score >= c)]
    ab = keep[keep.r3_fin_score >= c]
    print(f"  fin>={c}: A-only {len(a)}, A+B {len(ab)}")
