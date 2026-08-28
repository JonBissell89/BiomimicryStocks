"""Search index for every company the tournament scored.
Row: [name, stage, score, scale, tier, why, needlabel]
  stage: R ranked · X removed by ruling · 4 cut in deep research · 3 cut on financials
         · 2 cut on business model · 1 rejected in first screen · 0 screened, no advance
  score/scale: the number it earned and what it was out of, so nothing is mysterious.
"""
import os
from paths import DATA
import json, os
import pandas as pd

DATA = DATA
r1 = pd.read_csv(os.path.join(DATA, "round1_final_scores.csv"))
r2 = pd.read_csv(os.path.join(DATA, "round2_results.csv"))
r3 = pd.read_csv(os.path.join(DATA, "round3_scored.csv"))
r4 = pd.read_csv(os.path.join(DATA, "round4_results.csv"))
eng = json.load(open(os.path.join(DATA, "engine_tiers.json"), encoding="utf-8"))

tiered, removed = {}, {}
for t in eng["tiers"]:
    for n in t["names"]:
        tiered[n["tk"]] = (t["id"], n["score"], n.get("need", ""))
for r in eng.get("removed", []):
    removed[r["tk"]] = r.get("removed", "")

r2v, r2r = {}, {}
for r in r2.itertuples():
    tk = str(r.ticker).upper()
    v = getattr(r, "verdict", None)
    if isinstance(v, str):
        r2v[tk] = v
    rr = getattr(r, "reason_r2", None)
    if isinstance(rr, str) and rr != "nan":
        r2r[tk] = rr[:110]

r3cut = {}
for r in r3.itertuples():
    tk = str(r.ticker).upper()
    c = getattr(r, "r3_cut", None)
    if isinstance(c, str) and c != "nan":
        r3cut[tk] = c[:110]

r4d = {}
for r in r4.itertuples():
    tk = str(r.ticker).upper()
    tot = getattr(r, "total", None)
    r4d[tk] = (int(tot) if pd.notna(tot) else 0, str(getattr(r, "reason", ""))[:110])

def clean(x, n=44):
    s = str(x)
    for suf in [" Common Stock", " Ordinary Shares", " American Depositary Shares",
                " Class A Common Stock", " Class B Common Stock", " (The)", " Common Shares"]:
        s = s.replace(suf, "")
    return s.strip()[:n]

FIRST_CUT = {
    "blank-check": "It is a shell company with no real business yet.",
    "fund": "It is a fund or trust, not an operating company.",
    "weapons": "Its economics depend on war or weapons.",
    "addiction": "Its economics depend on addiction.",
    "coal": "It maintains a system the rules say should disappear.",
    "artificial scarcity": "It profits from artificial scarcity.",
    "market cap": "Too small to survive the screen (under $10M).",
    "sub-5-cent": "Trades under 5 cents, a sign of constant share dilution.",
    "no active trading": "It has no active trading market.",
    "no market cap": "It does not report enough data to be graded.",
    "dark": "It does not report enough data to be graded.",
}

idx = {}
for r in r1.itertuples():
    tk = str(r.ticker).upper()
    nm = clean(r.company)
    status = str(r.status) if isinstance(r.status, str) else ""
    reason = str(r.reason) if isinstance(r.reason, str) else ""
    need = str(r.need) if isinstance(r.need, str) else ""
    r1s = int(r.r1_score) if pd.notna(r.r1_score) else 0

    if tk in tiered:
        tier, sc, ndl = tiered[tk]
        idx[tk] = [nm, "R", sc, 100, tier, "", ndl or need]
    elif tk in removed:
        idx[tk] = [nm, "X", r4d.get(tk, (0, ""))[0], 100, "", removed[tk][:120], need]
    elif tk in r4d:
        tot, why = r4d[tk]
        idx[tk] = [nm, "4", tot, 100, "", why, need]
    elif tk in r3cut:
        idx[tk] = [nm, "3", r1s, 50, "", r3cut[tk], need]
    elif r2v.get(tk) == "C":
        idx[tk] = [nm, "2", r1s, 50, "", r2r.get(tk, "Its business did not fit the philosophy."), need]
    elif r2v.get(tk) in ("A", "B"):
        idx[tk] = [nm, "3", r1s, 50, "", "Passed the business review but ranked below the cut on growth and finances.", need]
    elif status == "reject":
        why = next((v for k, v in FIRST_CUT.items() if k in reason.lower()), reason[:110] or "Failed the first screen.")
        idx[tk] = [nm, "1", r1s, 50, "", why, need]
    else:
        idx[tk] = [nm, "0", r1s, 50, "", "Scored too low on the first screen to move on.", need]

out = os.path.join(DATA, "search_index.json")
json.dump(idx, open(out, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
from collections import Counter
print(f"{len(idx)} companies, {os.path.getsize(out)//1024} KB", Counter(v[1] for v in idx.values()))
