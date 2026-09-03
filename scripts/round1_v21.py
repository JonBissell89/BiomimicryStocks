# -*- coding: utf-8 -*-
"""Apply a first-screen prior version as a DELTA on the recorded screen.

The recorded first screen (data/round1_final_scores.csv) came from two prior
tables, the exchange industry code table in round1_score.py and the Yahoo
industry table used for enrichment in round1_merge_enriched.py, plus
description boosts that produced the software:<need> hybrids, plus a price
check that resolved the sec_only names. None of that is recomputed here.
Every recorded need score is attributed to the table entry that produced
it and re-priced only where the new prior changes that entry (number or
class), where a classification override supplies a class for a name that
had none, or where a business description now exists for a name whose entry
carries the description route. Viability, the hard rejects and the price
check are untouched: they are not logic, they are data.

A prior file with no changes must therefore reproduce the recorded screen
name for name, which is the regression test (prior_v20.json).

Usage: python round1_v21.py data/rubric/prior_v21.json [data/classification_overrides.json]
Writes data/round1_<ver>_scores.csv and data/round1_<ver>_newly_advancing.csv.
"""
import json, os, re, sys
import pandas as pd
from paths import DATA
import marketdb

prior_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DATA, "rubric", "prior_v20.json")
ov_path = sys.argv[2] if len(sys.argv) > 2 else None
P = json.load(open(prior_path, encoding="utf-8"))
BASE = json.load(open(os.path.join(DATA, "rubric", "prior_v20.json"), encoding="utf-8"))
IND0 = {k: v["prior"] for k, v in BASE["industry"].items()}
Y0 = {k: v["prior"] for k, v in BASE["yahoo_industry"].items()}
IND0C = {k: v["class"] for k, v in BASE["industry"].items()}
Y0C = {k: v["class"] for k, v in BASE["yahoo_industry"].items()}
IND1 = {k: (v["prior"], v["class"], v.get("flag", "")) for k, v in P.get("industry", {}).items()}
Y1 = {k: (v["prior"], v["class"], v.get("flag", "")) for k, v in P.get("yahoo_industry", {}).items()}
CLASS1 = P.get("class_prior", {})
BOOSTS = sorted(P.get("desc_boost", []), key=lambda b: b["order"])
RULES = P.get("desc_rules", {"cap": 24})
NEED_MIN, VIA_MIN = P["advance"]["need_min"], P["advance"]["viability_min"]
ver = P.get("version", "vX")
overrides = {}
if ov_path:
    o = json.load(open(ov_path, encoding="utf-8"))
    overrides = o.get("overrides", o)
try:
    PROFILES = marketdb.load_profiles()
except Exception:
    PROFILES = {}

r1 = pd.read_csv(os.path.join(DATA, "round1_final_scores.csv"))


def source(r):
    """Attribute the recorded need score to the table entry that produced it.
    A hybrid label (software:health) is a Yahoo base plus a description boost,
    and the boost is the recorded remainder over that base."""
    yi = r.y_industry if isinstance(r.y_industry, str) else ""
    ind = r.industry if isinstance(r.industry, str) else ""
    if ":" in str(r.need) and yi in Y0 and r.need_score > Y0[yi]:
        return "boost", yi
    if yi and yi in Y0 and Y0[yi] == r.need_score: return "yahoo", yi
    if ind and ind in IND0 and IND0[ind] == r.need_score: return "industry", ind
    return "other", str(r.need)


def best_boost(desc):
    """The single largest boost whose regex matches; earlier entry wins ties."""
    d = desc.lower()
    best = None
    for b in BOOSTS:
        if re.search(b["regex"], d) and (best is None or b["boost"] > best["boost"]):
            best = b
    return best


def hybrid(base_class, label):
    return ("software:" if base_class in ("software", "services") else base_class + ":") + label


def route_desc(base_prior, base_class, desc):
    """Base plus the largest boost, capped, with the hybrid label."""
    b = best_boost(desc)
    if not b:
        return base_prior, base_class, ""
    return min(base_prior + b["boost"], RULES.get("cap", 24)), hybrid(base_class, b["label"]), b["label"]


def routed(c1, f1):
    return ("desc" in f1) or c1 in ("software", "services", "conglomerate")


rows = []
for r in r1.itertuples(index=False):
    status = r.status if isinstance(r.status, str) else ""
    need, ns = r.need, int(r.need_score)
    reason = r.reason if isinstance(r.reason, str) else ""
    changed = ""
    src, key = source(r)
    ov = overrides.get(r.ticker)
    yi = r.y_industry if isinstance(r.y_industry, str) else ""
    ind = r.industry if isinstance(r.industry, str) else ""
    desc = (PROFILES.get(r.ticker) or {}).get("summary") or ""
    # an enrich-flagged exchange code defers to the Yahoo entry when one exists
    if src == "industry" and key in IND1 and "enrich" in IND1[key][2] and yi in Y1:
        src, key = "yahoo", yi
    if ov and status == "" and ov.get("operating") is False:
        status, reason, changed = "reject", "classification review: no evidence of an operating business", "override:dead"
    elif ov and status == "" and ov.get("class") in CLASS1 and r.need in ("unknown", "unmapped", "y-unmapped"):
        need, ns, changed = ov["class"], CLASS1[ov["class"]], "override:class"
    elif src == "boost" and key in Y1:
        # the recorded boost rides on the new base; the label keeps its suffix
        p1, c1, f1 = Y1[key]
        b = ns - Y0[key]
        ns2 = min(p1 + b, RULES.get("cap", 24))
        need2 = hybrid(c1, str(need).split(":", 1)[1])
        if ns2 != ns or need2 != need:
            ns, need, changed = ns2, need2, "base:" + key
    elif src == "yahoo" and key in Y1:
        p1, c1, f1 = Y1[key]
        if routed(c1, f1) and desc:
            ns2, need2, lab = route_desc(p1, c1, desc)
            if ns2 != ns or need2 != need:
                ns, need, changed = ns2, need2, "desc:" + (lab or "none")
        elif p1 != ns or c1 != Y0C.get(key):
            ns, need, changed = p1, c1, "yahoo:" + key
    elif src == "industry" and key in IND1:
        p1, c1, f1 = IND1[key]
        if p1 != ns or c1 != IND0C.get(key):
            ns, need, changed = p1, c1, "industry:" + key
    # enrich obligation: a viable name in a routed code is not cut on need
    # until its description has been read; the reason says so meanwhile
    in_route = (ind in IND1 and "enrich" in IND1[ind][2]) or (yi in Y1 and routed(Y1[yi][1], Y1[yi][2]))
    if status == "" and int(r.viability) >= VIA_MIN and ns < NEED_MIN and in_route and not desc:
        reason = "no description available"
    status0 = r.status if isinstance(r.status, str) else ""
    adv0 = status0 == "" and int(r.need_score) >= 20 and int(r.viability) >= 9
    adv1 = status == "" and ns >= NEED_MIN and int(r.viability) >= VIA_MIN
    rows.append({"ticker": r.ticker, "company": r.company, "price": r.price, "marketCap": r.marketCap,
                 "industry": r.industry, "y_industry": r.y_industry, "listing": r.listing,
                 "need_v20": r.need, "need_score_v20": int(r.need_score), "need": need, "need_score": ns,
                 "viability": int(r.viability), "r1_score": ns + int(r.viability), "status": status,
                 "reason": reason, "prior_source": src, "changed": changed,
                 "has_description": bool(desc), "advance_v20": bool(adv0), "advance": bool(adv1)})

df = pd.DataFrame(rows)
tag = ver.replace(".", "")
df.to_csv(os.path.join(DATA, "round1_%s_scores.csv" % tag), index=False)
newly_in = df[df.advance & ~df.advance_v20]
newly_out = df[~df.advance & df.advance_v20]
newly_in.to_csv(os.path.join(DATA, "round1_%s_newly_advancing.csv" % tag), index=False)
print("%s: %d names | changed %d | advance %d (v2.0: %d) | newly advancing %d | newly cut %d | descriptions on file %d"
      % (ver, len(df), int((df.changed != "").sum()), int(df.advance.sum()), int(df.advance_v20.sum()),
         len(newly_in), len(newly_out), int(df.has_description.sum())))
if len(newly_in):
    print("  newly advancing by class:", newly_in.need.value_counts().to_dict())
if len(newly_out):
    print("  newly cut by class:", newly_out.need_v20.value_counts().to_dict())
kinds = df[df.changed != ""].changed.str.split(":").str[0].value_counts().to_dict()
print("  change kinds:", kinds)
