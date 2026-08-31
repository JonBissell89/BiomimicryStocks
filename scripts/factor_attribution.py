# -*- coding: utf-8 -*-
"""Internal factor attribution: how much of the basket is one wager?

External factor data (size, value, quality, momentum from the French library
or ETF proxies) is not reachable from this environment, so that test is
registered as pending in the protocol. What IS computable from the repo's own
year of weekly closes: the basket's beta to the internal equal-weight market
of all ranked names, the share of variance that market explains, and the
loading on an internal health-minus-rest factor, since health is the list's
declared concentration. Labeled internal throughout; it bounds the question,
it does not settle it."""
import json, os
import numpy as np
from paths import DATA
from rigor_lib import load_names

sp = json.load(open(os.path.join(DATA, "spark.json"), encoding="utf-8"))["s"]
names = load_names()
need = {n["tk"]: n["need"].split("·")[0].strip() for n in names}
inv = [n["tk"] for n in names if n["gate"] == "pass" and n["tier"] != "exit" and n["tk"] in sp]

minlen = min(len(v) for v in sp.values())
R = {tk: np.diff(np.array(v[-minlen:], float)) / np.array(v[-minlen:], float)[:-1] for tk, v in sp.items()}
mkt = np.mean([R[t] for t in R], axis=0)
health = [t for t in R if need.get(t) == "Health"]
rest = [t for t in R if need.get(t) != "Health"]
hml = np.mean([R[t] for t in health], axis=0) - np.mean([R[t] for t in rest], axis=0)
basket = np.mean([R[t] for t in inv], axis=0)

def regress(y, X):
    X1 = np.column_stack([np.ones(len(y))] + X)
    b, *_ = np.linalg.lstsq(X1, y, rcond=None)
    resid = y - X1 @ b
    r2 = 1 - resid.var() / y.var()
    return b, float(r2)

b1, r2_m = regress(basket, [mkt])
b2, r2_mh = regress(basket, [mkt, hml])
doc = {"kind": "INTERNAL attribution only; external factor test pending network access, registered in the protocol",
       "window_weeks": int(minlen - 1),
       "basket": "equal-weight investable, %d names" % len(inv),
       "beta_internal_market": round(float(b1[1]), 2),
       "r2_internal_market": round(r2_m, 3),
       "health_factor_loading": round(float(b2[2]), 2),
       "r2_market_plus_health": round(r2_mh, 3),
       "idiosyncratic_share": round(1 - r2_mh, 3),
       "reading": "the share of basket variance NOT explained by the internal market and the health tilt is the part that can even in principle be the thesis at work; performance attribution to the thesis itself needs the external factors"}
json.dump(doc, open(os.path.join(DATA, "rigor", "factor_internal.json"), "w"), indent=1)
print("internal attribution: beta %.2f | market R2 %.2f | +health R2 %.2f | idiosyncratic %.0f%%"
      % (doc["beta_internal_market"], r2_m, r2_mh, doc["idiosyncratic_share"] * 100))
