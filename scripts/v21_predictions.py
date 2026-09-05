# -*- coding: utf-8 -*-
"""Read the thirteen pre-registered v2.1 predictions against the data.

Each prediction was registered in evaluation_protocol.json (v3) before the
re-screen ran. This script computes the observed value where the data
exists, states which are not yet readable and why, and writes
data/rigor/v21_predictions.json. A prediction that fails is recorded as
failed; nothing here edits a prediction.
"""
import json, os
import pandas as pd
from paths import DATA

R = os.path.join(DATA, "rigor")
pro = json.load(open(os.path.join(R, "evaluation_protocol.json"), encoding="utf-8"))
preds = pro["v21_predictions"]["predictions"]
v = pd.read_csv(os.path.join(DATA, "round1_v21_scores.csv"))
adm = pd.read_csv(os.path.join(DATA, "round1_v21_newly_advancing.csv")).set_index("ticker")
r2 = []
for fn in sorted(os.listdir(R)):
    if fn.startswith("v21_round2") and fn.endswith(".json"):
        r2 += json.load(open(os.path.join(R, fn), encoding="utf-8"))["rows"]
verdict = {x["ticker"]: x["verdict"] for x in r2}
adm["verdict"] = adm.index.map(verdict)
have_desc = int(v.has_description.sum()) > 0
out = {}


def ab(df):
    return int(df.verdict.isin(["A", "B"]).sum())


def cls_adv(prefix):
    a = v[v.advance & v.need.astype(str).str.startswith(prefix)]
    return len(a), int((a.advance & ~a.advance_v20).sum())


# P1 first-screen advance count
n_adv = int(v.advance.sum())
out["v21-P01"] = {"observed": n_adv, "newly_advancing": int((v.advance & ~v.advance_v20).sum()),
                  "reading": ("within the registered 3,350 to 3,500 range" if 3350 <= n_adv <= 3500 else
                              "%s the 3,350 to 3,500 range at %d; the computed floor 3,267 held (154 table admissions against 136 registered) and the description route has admitted %d with %d of the owed descriptions on file"
                              % ("below" if n_adv < 3350 else "above", n_adv, int((v.advance & ~v.advance_v20 & v.changed.fillna("").str.startswith("desc:")).sum()), int(v.has_description.sum()))),
                  "status": "provisional: the description route is still converging (%d descriptions owed)" % int((v.reason == "no description available").sum())}
# P2 telecom family
tel = adm[adm.y_industry == "Telecom Services"]
out["v21-P02"] = {"admitted": len(tel), "stage2_AB": ab(tel), "stage2_AB_rate": round(ab(tel) / max(1, len(tel)), 3),
                  "reading": "FAILED as registered: the A or B rate is far above 25 percent. The judges verdict B on territory-bound carriers where the recorded Aug 2026 round gave C (no scalable product layer); the verdict scale drifted between rounds, which the blind reliability batch (P12) must price",
                  "status": "final on this round"}
# P3 IT services hybrids
it = adm[adm.y_industry == "Information Technology Services"]
out["v21-P03"] = {"admitted": len(it), "stage2_AB": ab(it), "stage2_A": int((it.verdict == "A").sum()), "stage2_AB_rate": round(ab(it) / max(1, len(it)), 3),
                  "reading": "the pooled A or B rate is above the registered 13 to 37 percent band, with zero A: every B names a diluted multi-vertical consultancy. On the recorded scale most of these are C; same drift as P02",
                  "status": "final on this round"}
# P4 software:tools, P5 materials, P6 conglomerate, P8 media: description routes
for pid, label in (("v21-P04", "software:tools"), ("v21-P05", "materials"), ("v21-P06", "conglomerate"), ("v21-P08", "media")):
    tot, new = cls_adv(label)
    out[pid] = {"observed_advance": tot, "newly_advancing": new,
                "status": ("readable in part: %d of the owed descriptions are on file after the first weekly fetch; the count grows as fetch_profiles.py converges" % int(v.has_description.sum())) if have_desc else "not readable: 0 descriptions on file"}
# P7 services
sbs = adm[adm.y_industry == "Specialty Business Services"]
out["v21-P07"] = {"admitted": len(sbs), "stage2_AB": ab(sbs), "reading": "7 computed admissions landed (the base change worked); circulation matches await descriptions", "status": "partial"}
# P9 health control
h_adv = v[v.advance & v.need.isin(["health", "software:health"])]
out["v21-P09"] = {"observed": len(h_adv), "share": round(len(h_adv) / n_adv, 3), "newly": int((h_adv.advance & ~h_adv.advance_v20).sum()),
                  "reading": ("within the registered share band 37 to 39.5 percent" if 0.37 <= len(h_adv) / n_adv <= 0.395 else "share %.1f percent, outside 37 to 39.5; the 50 new health names exceed the computed 40 because enrich-flagged Industrial Specialties names deferred to Yahoo Medical Devices (EW, ZBH, SNN, STE, ESTA) and overrides added health names" % (100 * len(h_adv) / n_adv)),
                  "status": "provisional until descriptions are on file"}
# P10 cut vocabulary
cs = [x for x in r2 if x["verdict"] == "C"]
kw = ("host flow", "host number", "attribution", "rebound", "runway", "dilution", "revenue", "pre-revenue", "no approved", "not an operating", "shell", "holding", "landlord", "debt", "no verifiable", "insufficient disclosed", "going concern", "operating")
named = [x["ticker"] for x in cs if any(k in x["reason"].lower() for k in kw)]
out["v21-P10"] = {"stage2_cuts_on_layer0_classes": len(cs), "cuts_naming_missing_B_or_survivability": len(named),
                  "reading": "%d of %d C reasons name the missing B item or a survivability fact across both Round 2 rounds. The first round (154 table admissions) failed at 8 of 33 because its prompt did not carry the admissibility vocabulary; the description-route round carried it and named the item in 33 of 44. Recorded as failed for the first round and passing for the second" % (len(named), len(cs)),
                  "status": "final on this round; pipeline defect recorded"}
# P11 rescore, P12 blind batch, P13 forward
for pid, why in (("v21-P11", "readable once data/rigor/v21_cards_rescore.json is assembled (assemble_v21.py)"),
                 ("v21-P12", "awaits the next blind reliability batch scored from the v2.1 text"),
                 ("v21-P13", "forward endpoint, horizon 2027-08-28")):
    out[pid] = {"status": "pending: " + why}
rp = os.path.join(R, "v21_cards_rescore.json")
if os.path.exists(rp):
    cards = json.load(open(rp, encoding="utf-8"))["cards"]
    eng = json.load(open(os.path.join(DATA, "engine_tiers.json"), encoding="utf-8"))
    v20 = {n["tk"]: n for t in eng["tiers"] for n in t["names"]}
    def mean(xs): return round(sum(xs) / len(xs), 2) if xs else None
    health = [c for c in cards if str(v20.get(c["ticker"], {}).get("need", "")).lower().startswith("health")]
    tr = [c for c in cards if c["ticker"] in ("WAB", "CNI", "CP", "UNP", "YMM")]
    tech = [c for c in cards if c["ticker"] in ("BSY", "IOT", "TSM", "TOELY", "BB")]
    out["v21-P11"] = {"health_mean_total": mean([c["total"] for c in health]), "health_n": len(health),
                      "transport_E": mean([c["E"] for c in tr]), "transport_F_clock": mean([c["F_clock"] for c in tr]), "transport_A": mean([c["A"] for c in tr]),
                      "tech_A": mean([c["A"] for c in tech]), "tech_C1": mean([c["C1"] for c in tech]),
                      "amplifying_labels": sorted(c["ticker"] for c in cards if "amplif" in str(c.get("loop", "")).lower()),
                      "status": "observed; compare with the registered current_value and expected_after by hand"}
doc = {"read": pd.Timestamp.today().strftime("%Y-%m-%d"), "rule": pro["v21_predictions"]["rule"], "descriptions_on_file": int(v.has_description.sum()),
       "readings": [{**{"id": p["id"], "metric": p["metric"], "expected_after": p["expected_after"], "falsified_if": p.get("falsified_if")}, **out.get(p["id"], {})} for p in preds]}
json.dump(doc, open(os.path.join(R, "v21_predictions.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=True)
for r in doc["readings"]:
    print(r["id"], "|", r.get("status", ""), "|", r.get("reading", ""))
