# -*- coding: utf-8 -*-
"""Round 3 for a v2.1 admission set: the recorded financial screen, unchanged,
applied to the Round 2 verdicts the v2.1 business read produced.

Inputs : data/rigor/v21_round2.json (rows: ticker, verdict, reason, financial
         fields the judges verified), data/round1_v21_newly_advancing.csv
Outputs: data/rigor/v21_round3.json (every name with its R3 score, notes and
         cut), printed field for Round 4.

The arithmetic is round3_financials.py's, line for line: growth 0-10,
survivability 0-10, margin 0-5, three commercial-reality cuts. Nothing about
the screen changed in v2.1, so a name here is scored exactly as the 935
Round 2 A and B names were in Aug 2026.
"""
import json, os, sys
import numpy as np
import pandas as pd
from paths import DATA

R2 = os.path.join(DATA, "rigor", "v21_round2.json")
r2 = json.load(open(R2, encoding="utf-8"))
rows_in = r2["rows"] if isinstance(r2, dict) else r2
adm = pd.read_csv(os.path.join(DATA, "round1_v21_newly_advancing.csv")).set_index("ticker")


def num(x):
    try:
        v = float(x)
        return v if np.isfinite(v) else np.nan
    except (TypeError, ValueError):
        return np.nan


out = []
for r in rows_in:
    tk = str(r["ticker"]).upper().strip()
    rec = {"ticker": tk, "verdict": r["verdict"], "r2_reason": r.get("reason", ""),
           "need": adm.need.get(tk), "need_score": (int(adm.need_score.get(tk)) if tk in adm.index else None),
           "company": adm.company.get(tk), "corporate_action": r.get("corporate_action", "none"),
           "audited": bool(r.get("audited", False))}
    if r["verdict"] not in ("A", "B"):
        rec.update({"r3_fin_score": None, "r3_notes": "", "r3_cut": "R2: verdict C"})
        out.append(rec); continue
    cap = num(r.get("marketCap")) if num(r.get("marketCap")) == num(r.get("marketCap")) else num(adm.marketCap.get(tk))
    rg, gm = num(r.get("revenueGrowth")), num(r.get("grossMargins"))
    cash, fcf, debt, rev = num(r.get("totalCash")), num(r.get("freeCashflow")), num(r.get("totalDebt")), num(r.get("totalRevenue"))
    score, notes, cut = 0, [], None
    if pd.notna(rg):
        if rg >= 0.25: score += 10
        elif rg >= 0.12: score += 8
        elif rg >= 0.05: score += 6
        elif rg >= 0.00: score += 3
        else: notes.append("revenue shrinking %.0f%%" % (rg * 100))
    else:
        score += 3; notes.append("growth unknown")
    s = 5
    if pd.notna(fcf) and fcf > 0:
        s = 9
        if pd.notna(debt) and pd.notna(cash) and debt > cash and pd.notna(cap) and debt - cash > 2.5 * cap:
            s = 4; notes.append("heavy net debt vs cap")
    elif pd.notna(fcf) and fcf < 0 and pd.notna(cash) and cash > 0:
        runway = cash / abs(fcf)
        if runway >= 3: s = 7
        elif runway >= 1.5: s = 5
        elif runway >= 0.75: s = 3; notes.append("runway %.1fy" % runway)
        else: s = 1; notes.append("runway %.1fy - dilution imminent" % runway)
    score += s
    if pd.notna(gm):
        if gm >= 0.45: score += 5
        elif gm >= 0.30: score += 4
        elif gm >= 0.18: score += 2
        else: score += 1; notes.append("thin gm %.0f%%" % (gm * 100))
    else:
        score += 2
    if pd.notna(rev) and rev < 5e6 and (pd.isna(rg) or rg < 0.5):
        cut = "pre-commercial: revenue <$5M without hypergrowth"
    if pd.notna(rg) and rg < -0.15:
        cut = "contractionary: revenue %.0f%%" % (rg * 100)
    if pd.notna(fcf) and fcf < 0 and pd.notna(cash) and cash > 0 and cash / abs(fcf) < 0.6 and (pd.isna(cap) or cap < 5e8):
        cut = "runway <0.6y small-cap - forced dilution/financing dependence"
    ca = str(r.get("corporate_action") or "none").lower()
    if ca not in ("none", "", "null") and any(w in ca for w in ("buyout", "acquired", "going private", "delist", "merger agreement", "take-private")):
        cut = "corporate action: " + r["corporate_action"]
    rec.update({"r3_fin_score": score, "r3_notes": "; ".join(notes), "r3_cut": cut,
                "composite": (score + rec["need_score"]) if rec["need_score"] is not None else None,
                "fields": {k: (None if pd.isna(num(r.get(k))) else num(r.get(k))) for k in
                           ("totalRevenue", "revenueGrowth", "grossMargins", "freeCashflow", "totalCash", "totalDebt", "marketCap", "price")}})
    out.append(rec)

doc = {"logic": "v2.1", "run": pd.Timestamp.today().strftime("%Y-%m-%d"), "rule": "round3_financials.py arithmetic, unchanged",
       "counts": {"in": len(out), "A": sum(1 for x in out if x["verdict"] == "A"), "B": sum(1 for x in out if x["verdict"] == "B"),
                  "C": sum(1 for x in out if x["verdict"] == "C"),
                  "r3_pass": sum(1 for x in out if x["verdict"] in "AB" and not x["r3_cut"]),
                  "r3_cut": sum(1 for x in out if x["verdict"] in "AB" and x["r3_cut"])},
       "rows": out}
json.dump(doc, open(os.path.join(DATA, "rigor", "v21_round3.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=True)
print(doc["counts"])
surv = [x for x in out if x["verdict"] in "AB" and not x["r3_cut"]]
surv.sort(key=lambda x: (x["verdict"], -(x["composite"] or 0)))
for x in surv:
    print("  %-7s %s %-22s need %2d fin %2d  %s" % (x["ticker"], x["verdict"], str(x["need"])[:22], x["need_score"], x["r3_fin_score"], x["r2_reason"][:60]))
