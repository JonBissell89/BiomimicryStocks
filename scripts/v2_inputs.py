# -*- coding: utf-8 -*-
"""Compute the measurable inputs the v2 rubric needs, so researchers score
against numbers where numbers exist.

WARNING, do not trust gate_funding as authoritative. On the 28 Aug 2026 run this
layer was wrong in BOTH directions and every error was caught downstream by a human
reading the filing:
  - SHLS was flagged "0.4y runway" against roughly $67.2M of actual liquidity
  - DMTRF and ADMA were flagged clean; DMTRF actually fails the gate on +34.8%
    one-year dilution
  - AHICF arrived all-nan and was scored entirely from primary sources
Two causes: yfinance freeCashflow is a trailing snapshot that ignores committed
financing, and this file never checked the dilution prong at all, which is the prong
both real failures tripped. A dilution flag was added afterward and measured against
the six names whose gate status was established from filings. It caught both real
failures (BFLY, DMTRF) and cleared both clean names (ADMA, CERS), but also flagged
SHLS and CRMD, which pass: Shoals' share count rose through an Up-C class conversion
that is not economic dilution, and CorMedix issued stock to acquire Melinta. So the
flag has full recall and poor precision. Use it to decide where to read, never to
decide an outcome.

Treat every field here as a hint that tells a researcher where to look, never as a
finding. The gate is decided from the filing.
"""
import os
from paths import DATA
import json, time, warnings
warnings.filterwarnings("ignore")
import pandas as pd
import yfinance as yf

D = DATA
eng = json.load(open(os.path.join(D, "engine_tiers.json"), encoding="utf-8"))
names = [(t["id"], n) for t in eng["tiers"] for n in t["names"]]

HOME = {  # thin US lines: use the real market for financials
 "TSNLF": "TSTL.L", "TDVXF": "TDVOX.ST", "SBDHF": "1414.T", "DLEGF": "DELTA.BK",
 "ENGCF": "ENGCON-B.ST", "BMBRF": "BIMAS.IS", "DMTRF": "7777.T", "BIRMF": "BRM.V",
 "WSIOF": "3393.HK", "WRTBY": "WRT1V.HE", "CLPBY": "COLO-B.CO", "CODYY": "SGO.PA",
 "TMRAY": "TOM.OL", "MHGVY": "MOWI.OL", "SSMXY": "6869.T", "TOELY": "8035.T",
 "LGRDY": "LR.PA", "AHICF": "7333.T", "MBRFF": "MBR.WA", "SAEYY": "RDC.DE",
}

rows = []
for tid, n in names:
    tk = n["tk"]
    src = HOME.get(tk, tk)
    rec = {"ticker": tk, "name": n["nm"], "tier": tid, "score_v1": n["score"],
           "need": n.get("need", ""), "src": src}
    for attempt in range(2):
        try:
            info = yf.Ticker(src).get_info()
            if info and len(info) > 3:
                rec.update({
                    "mktcap": info.get("marketCap"),
                    "revenue": info.get("totalRevenue"),
                    "rev_growth": info.get("revenueGrowth"),
                    "gross_margin": info.get("grossMargins"),
                    "op_margin": info.get("operatingMargins"),
                    "fcf": info.get("freeCashflow"),
                    "ocf": info.get("operatingCashflow"),
                    "cash": info.get("totalCash"),
                    "debt": info.get("totalDebt"),
                    "shares": info.get("sharesOutstanding"),
                    "employees": info.get("fullTimeEmployees"),
                    "country": info.get("country"),
                    "summary": (info.get("longBusinessSummary") or "")[:700],
                })
                break
        except Exception:
            time.sleep(2)
    # ---- computable rubric inputs ----
    fcf, rev, cash, debt = rec.get("fcf"), rec.get("revenue"), rec.get("cash"), rec.get("debt")
    # GATE: runway / self-funding
    if fcf is not None and fcf > 0:
        rec["gate_funding"] = "self-funding (FCF positive)"
    elif fcf is not None and cash:
        yrs = cash / abs(fcf) if fcf else None
        rec["gate_funding"] = f"burning; ~{yrs:.1f}y cash runway" if yrs else "burning"
    else:
        rec["gate_funding"] = "unknown"
    # GATE, dilution prong. This is the prong that actually caught the real failures,
    # so compute it rather than inferring solvency from cash flow alone.
    try:
        sh = yf.Ticker(src).get_shares_full(start="2023-01-01")
        if sh is not None and len(sh) > 1:
            first, latest = float(sh.iloc[0]), float(sh.iloc[-1])
            if first > 0:
                pct = 100.0 * (latest - first) / first
                rec["dilution_3y_pct"] = round(pct, 1)
                since = str(sh.index[0])[:10]
                rec["gate_dilution"] = (
                    f"REVIEW, raw share count +{pct:.1f}% since {since}. This is a flag, "
                    f"not a verdict: check whether the increase is cash-burn dilution, a "
                    f"share-class conversion, or stock issued for an acquisition"
                    if pct > 25 else f"no flag, raw share count {pct:+.1f}% since {since}")
    except Exception:
        pass
    rec.setdefault("gate_dilution", "unknown, check the filing")
    # D-contact-inhibition proxy: solvent without growth?
    rec["d_inhibition_proxy"] = (
        "profitable and self-funding at current scale" if (fcf or 0) > 0 and (rec.get("op_margin") or 0) > 0
        else "requires growth or external capital")
    # D-replication proxy: capital intensity per unit revenue
    if rev and rec.get("mktcap"):
        rec["capital_per_revenue"] = round(rec["mktcap"] / rev, 2)
    # E-buffer proxy: revenue per employee (asset/labour concentration hint)
    if rev and rec.get("employees"):
        rec["rev_per_employee"] = int(rev / rec["employees"])
    # leverage
    if cash is not None and debt is not None:
        rec["net_cash"] = cash - debt
    rows.append(rec)
    time.sleep(0.25)

df = pd.DataFrame(rows)
df.to_csv(os.path.join(D, "v2_inputs.csv"), index=False)
print(f"computed inputs for {len(df)} names")
print("with revenue:", df.revenue.notna().sum(), "| with FCF:", df.fcf.notna().sum(),
      "| with summary:", (df.summary.astype(str).str.len() > 50).sum())
