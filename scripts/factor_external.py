# -*- coding: utf-8 -*-
"""The EXTERNAL factor test the protocol registered as pending.

The internal attribution bounds the question (how much of the basket is one
wager on its own market); this settles it against the academic factors:
market, size, value, profitability, investment and momentum from Ken French's
library. The registered success rule reads: the thesis survives only if alpha
remains after the factor loadings.

Method: the daily factors are compounded onto the engine's weekly grid (the
sparkline closes are weekly bars, so the last point is taken as the most
recent complete trading week on or before the sparkline date, and each weekly
factor return is the product of the daily factors in that Friday-to-Friday
window). The equal-weight investable basket's weekly excess return is then
regressed on the six weekly factors. Reported: annualised alpha and its
t-statistic, the loadings, R-squared against the market alone and against all
six, and the idiosyncratic share. Alignment slop is a day at most and is
stated in the file.

Self-guarded: when the library is unreachable (it is, from the build sandbox;
it is not, from the weekly runner) the file records the attempt and the
status stays pending. The registration in the protocol is never edited; this
file is the test's RESULT, kept separate from its pre-registration.
"""
import datetime, io, json, os, re, sys, urllib.request, zipfile
import numpy as np
from paths import DATA
from rigor_lib import load_names
import marketdb

OUT = os.path.join(DATA, "rigor", "factor_external.json")
FF5 = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
MOM = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily_CSV.zip"
UA = {"User-Agent": "BiomimicryStocks rigor layer (research)"}


def fetch_csv(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    name = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
    return z.read(name).decode("utf-8", "replace")


def parse_daily(text, ncols):
    """First daily block only: rows of YYYYMMDD followed by ncols percentages."""
    out = {}
    for line in text.splitlines():
        m = re.match(r"^\s*(\d{8})\s*,(.*)$", line)
        if not m:
            if out and line.strip() == "":
                break                      # the daily block ended; annual rows follow
            continue
        vals = [v.strip() for v in m.group(2).split(",")]
        if len(vals) < ncols:
            continue
        try:
            out[datetime.date(int(m.group(1)[:4]), int(m.group(1)[4:6]), int(m.group(1)[6:]))] = \
                [float(v) / 100.0 for v in vals[:ncols]]
        except ValueError:
            continue
    return out


def weekly_grid(asof, n):
    """n Friday week-ends, the last on or before asof."""
    d = datetime.date.fromisoformat(asof)
    d -= datetime.timedelta(days=(d.weekday() - 4) % 7)
    return [d - datetime.timedelta(weeks=n - 1 - i) for i in range(n)]


def compound(daily, fridays, k):
    """Weekly factor returns: product of (1 + daily) over (prev Friday, Friday]."""
    dates = sorted(daily)
    out = []
    for i in range(1, len(fridays)):
        lo, hi = fridays[i - 1], fridays[i]
        g = 1.0
        seen = 0
        for d in dates:
            if lo < d <= hi:
                g *= 1.0 + daily[d][k]; seen += 1
        out.append(g - 1.0 if seen else np.nan)
    return np.array(out)


def regress(y, X):
    X1 = np.column_stack([np.ones(len(y))] + X)
    b, *_ = np.linalg.lstsq(X1, y, rcond=None)
    resid = y - X1 @ b
    n, k = X1.shape
    s2 = float(resid @ resid) / max(n - k, 1)
    cov = s2 * np.linalg.pinv(X1.T @ X1)
    se = np.sqrt(np.diag(cov))
    r2 = 1 - resid.var() / y.var() if y.var() > 0 else 0.0
    return b, se, float(r2)


def run(ff_text, mom_text, sp, spark_asof, names):
    ff = parse_daily(ff_text, 6)       # Mkt-RF SMB HML RMW CMA RF
    mom = parse_daily(mom_text, 1)     # Mom
    if len(ff) < 250 or len(mom) < 250:
        raise ValueError("factor files parsed too short: %d / %d rows" % (len(ff), len(mom)))
    inv = [n["tk"] for n in names if n["gate"] == "pass" and n["tier"] != "exit" and n["tk"] in sp]
    minlen = min(len(sp[t]) for t in inv)
    R = {t: np.diff(np.array(sp[t][-minlen:], float)) / np.array(sp[t][-minlen:], float)[:-1] for t in inv}
    basket = np.mean([R[t] for t in inv], axis=0)
    fridays = weekly_grid(spark_asof, minlen)
    F = {k: compound(ff, fridays, j) for j, k in enumerate(["mkt_rf", "smb", "hml", "rmw", "cma", "rf"])}
    F["mom"] = compound(mom, fridays, 0)
    ok = np.ones(len(basket), bool)
    for v in F.values():
        ok &= ~np.isnan(v)
    if ok.sum() < 20:
        raise ValueError("only %d aligned weeks; the factor library lags the sparkline date" % ok.sum())
    y = basket[ok] - F["rf"][ok]
    keys = ["mkt_rf", "smb", "hml", "rmw", "cma", "mom"]
    X = [F[k][ok] for k in keys]
    b6, se6, r2_6 = regress(y, X)
    b1, se1, r2_1 = regress(y, [X[0]])
    return {
        "kind": "EXTERNAL attribution against the French library factors; the registered test, now reported",
        "status": "reported",
        "asof": spark_asof,
        "window_weeks": int(ok.sum()),
        "basket": "equal-weight investable, %d names" % len(inv),
        "alignment": "daily factors compounded Friday to Friday onto the weekly close grid; slop at most one trading day",
        "factor_library_through": max(ff).isoformat(),
        "capm": {"beta": round(float(b1[1]), 2), "alpha_annual": round(float(b1[0]) * 52, 4),
                 "alpha_t": round(float(b1[0] / se1[0]) if se1[0] else 0.0, 2), "r2": round(r2_1, 3)},
        "six_factor": {
            "loadings": {k: round(float(b6[i + 1]), 2) for i, k in enumerate(keys)},
            "alpha_annual": round(float(b6[0]) * 52, 4),
            "alpha_t": round(float(b6[0] / se6[0]) if se6[0] else 0.0, 2),
            "r2": round(r2_6, 3),
            "idiosyncratic_share": round(1 - r2_6, 3)},
        "success_rule": "the thesis survives only if alpha remains after factor loadings",
        "reading": None,
    }


def main():
    prev = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    sp = marketdb.load_spark()
    names = load_names()
    try:
        ff_text, mom_text = fetch_csv(FF5), fetch_csv(MOM)
    except Exception as e:
        doc = {"kind": "EXTERNAL attribution: registered in the protocol, still pending",
               "status": "pending",
               "attempts": (prev.get("attempts") or []) + [
                   {"date": datetime.date.today().isoformat(), "outcome": "library unreachable: %s" % type(e).__name__}][-12:],
               "note": "the French library could not be fetched from this environment; the weekly runner retries, and the registration cannot be dropped"}
        json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1)
        print("external factor test: library unreachable (%s); still pending" % type(e).__name__)
        return
    doc = run(ff_text, mom_text, sp["s"], sp["asof"], names)
    a, t = doc["six_factor"]["alpha_annual"], doc["six_factor"]["alpha_t"]
    doc["reading"] = (
        "over %d weeks the six factors explain %.0f%% of the basket's variance (market alone %.0f%%); "
        "what remains is %.1f%% a year of alpha at t=%.1f, which %s the registered survival rule at this sample size; "
        "the window is short and the estimate is noisy, and the forward test is what settles it"
        % (doc["window_weeks"], doc["six_factor"]["r2"] * 100, doc["capm"]["r2"] * 100, a * 100, t,
           "clears" if (a > 0 and abs(t) >= 2) else "does not yet clear"))
    doc["attempts"] = prev.get("attempts") or []
    json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=1)
    print("external factor test: %s" % doc["reading"])


if __name__ == "__main__":
    main()
