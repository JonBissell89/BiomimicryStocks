# -*- coding: utf-8 -*-
"""Apply a first-screen prior change as a DELTA on the recorded screen.

The recorded first screen (data/round1_final_scores.csv) came from two prior
tables, the exchange industry code table in round1_score.py and the Yahoo
industry table used for enrichment in round1_merge_enriched.py, plus
description keywords that produced the software:<need> hybrids, plus a price
check that resolved the sec_only names. None of that is recomputed here.
Instead every recorded need score is attributed to the table entry that
produced it, and re-priced only where the new prior changes that entry, or
where a classification override supplies a class for a name that had none.
Viability, the hard rejects and the price check are untouched: they are not
logic, they are data.

A prior file with no changes must therefore reproduce the recorded screen
name for name, which is the regression test.

Usage: python round1_v21.py data/rubric/prior_v21.json [data/classification_overrides.json]
Writes data/round1_<ver>_scores.csv and data/round1_<ver>_newly_advancing.csv.
"""
import json, os, sys
import pandas as pd
from paths import DATA

prior_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DATA, "rubric", "prior_v20.json")
ov_path = sys.argv[2] if len(sys.argv) > 2 else None
P = json.load(open(prior_path, encoding="utf-8"))
BASE = json.load(open(os.path.join(DATA, "rubric", "prior_v20.json"), encoding="utf-8"))
IND0 = {k: v["prior"] for k, v in BASE["industry"].items()}
Y0 = {k: v["prior"] for k, v in BASE["yahoo_industry"].items()}
IND1 = {k: (v["prior"], v["class"]) for k, v in P.get("industry", {}).items()}
Y1 = {k: (v["prior"], v["class"]) for k, v in P.get("yahoo_industry", {}).items()}
CLASS1 = P.get("class_prior", {})          # need class -> prior (for hybrids, overrides, name-pattern names)
NEED_MIN, VIA_MIN = P["advance"]["need_min"], P["advance"]["viability_min"]
overrides = json.load(open(ov_path, encoding="utf-8")) if ov_path else {}
ver = P.get("version", "vX")

r1 = pd.read_csv(os.path.join(DATA, "round1_final_scores.csv"))


def source(r):
    yi = r.y_industry if isinstance(r.y_industry, str) else ""
    ind = r.industry if isinstance(r.industry, str) else ""
    if yi and yi in Y0 and Y0[yi] == r.need_score: return "yahoo", yi
    if ind and ind in IND0 and IND0[ind] == r.need_score: return "industry", ind
    if str(r.need).startswith("software:"): return "desc", str(r.need)
    return "other", str(r.need)


rows = []
for r in r1.itertuples(index=False):
    status = r.status if isinstance(r.status, str) else ""
    need, ns, reason, changed = r.need, int(r.need_score), (r.reason if isinstance(r.reason, str) else ""), ""
    src, key = source(r)
    ov = overrides.get(r.ticker)
    if ov and status == "" and ov.get("operating") is False:
        status, reason, changed = "reject", "classification review: no evidence of an operating business", "override:dead"
    elif ov and status == "" and ov.get("class") in CLASS1 and r.need in ("unknown", "unmapped", "y-unmapped"):
        need, ns, changed = ov["class"], CLASS1[ov["class"]], "override:class"
    elif src == "yahoo" and key in Y1 and Y1[key][0] != ns:
        ns, need, changed = Y1[key][0], Y1[key][1], "yahoo:" + key
    elif src == "industry" and key in IND1 and IND1[key][0] != ns:
        ns, need, changed = IND1[key][0], IND1[key][1], "industry:" + key
    elif src in ("desc", "other") and need in CLASS1 and CLASS1[need] != ns:
        ns, changed = CLASS1[need], "class:" + need
    status0 = r.status if isinstance(r.status, str) else ""
    adv0 = status0 == "" and int(r.need_score) >= 20 and int(r.viability) >= 9
    adv1 = status == "" and ns >= NEED_MIN and int(r.viability) >= VIA_MIN
    rows.append({"ticker": r.ticker, "company": r.company, "price": r.price, "marketCap": r.marketCap,
                 "industry": r.industry, "y_industry": r.y_industry, "listing": r.listing,
                 "need_v20": r.need, "need_score_v20": int(r.need_score), "need": need, "need_score": ns,
                 "viability": int(r.viability), "r1_score": ns + int(r.viability), "status": status,
                 "reason": reason, "prior_source": src, "changed": changed, "advance_v20": bool(adv0), "advance": bool(adv1)})

df = pd.DataFrame(rows)
tag = ver.replace(".", "")
df.to_csv(os.path.join(DATA, "round1_%s_scores.csv" % tag), index=False)
newly_in = df[df.advance & ~df.advance_v20]
newly_out = df[~df.advance & df.advance_v20]
newly_in.to_csv(os.path.join(DATA, "round1_%s_newly_advancing.csv" % tag), index=False)
print("%s: %d names | changed priors %d | advance %d (v2.0: %d) | newly advancing %d | newly cut %d"
      % (ver, len(df), int((df.changed != "").sum()), int(df.advance.sum()), int(df.advance_v20.sum()),
         len(newly_in), len(newly_out)))
if len(newly_in):
    print("  newly advancing by class:", newly_in.need.value_counts().to_dict())
if len(newly_out):
    print("  newly cut by class:", newly_out.need_v20.value_counts().to_dict())
print("  source attribution:", df.prior_source.value_counts().to_dict())
