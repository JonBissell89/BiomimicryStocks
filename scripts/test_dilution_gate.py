# -*- coding: utf-8 -*-
"""Does the new dilution prong reproduce the two failures the humans found,
and stay quiet on the names they cleared?"""
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf

# ticker -> what the researchers concluded from the filings
TRUTH = {"BFLY": "FAIL ~28% 3y", "DMTRF": "FAIL +34.8% 1y", "ADMA": "pass",
         "SHLS": "pass, $67.2M liquidity", "CRMD": "pass", "CERS": "pass"}
HOME = {"DMTRF": "7777.T"}

for tk, truth in TRUTH.items():
    src = HOME.get(tk, tk)
    verdict = "no data"
    try:
        sh = yf.Ticker(src).get_shares_full(start="2023-01-01")
        if sh is not None and len(sh) > 1:
            a, b = float(sh.iloc[0]), float(sh.iloc[-1])
            pct = 100.0 * (b - a) / a
            verdict = f"{pct:+6.1f}% since {str(sh.index[0])[:10]}  ->  " \
                      f"{'FAIL' if pct > 25 else 'pass'}"
    except Exception as e:
        verdict = f"error {type(e).__name__}"
    print(f"  {tk:<6s} computed {verdict:<44s} | filings said: {truth}")
