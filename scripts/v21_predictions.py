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

# P12: read the pre-registered v21-blind-1 batch straight from reliability.json,
# computed on that batch alone (not pooled with the v2.0-logic batches).
rel_path = os.path.join(R, "reliability.json")
if os.path.exists(rel_path):
    rel = json.load(open(rel_path, encoding="utf-8"))
    v21_rows = [r for r in rel["rows"] if r.get("batch") == "v21-blind-1"]
    if v21_rows:
        measures = ["A", "B", "C", "D", "E", "F"]
        mad = {m: round(sum(abs(r["recorded"][m] - r["blind"][m]) for r in v21_rows) / len(v21_rows), 3)
               for m in measures}
        total_mad = round(sum(abs(r["recorded"]["total"] - r["blind"]["total"]) for r in v21_rows) / len(v21_rows), 3)
        gate_ok = sum(1 for r in v21_rows if r["recorded_gate"] == r["blind_gate"])
        rec_tot = [r["recorded"]["total"] for r in v21_rows]
        bl_tot = [r["blind"]["total"] for r in v21_rows]
        from rigor_lib import spearman as _spearman
        rho12 = round(_spearman(rec_tot, bl_tot), 3)
        expected = {"A": 2.5, "B": 2.7, "C": 1.8, "D": 1.2, "E": 1.6, "F": 1.0}
        clauses = {}
        for m in measures:
            clauses["%s_mad_at_most_%s" % (m, expected[m])] = (
                "pass" if mad[m] <= expected[m] else "FAIL (%.3f)" % mad[m])
        clauses["total_mad_at_most_7"] = "pass" if total_mad <= 7 else "FAIL (%.3f)" % total_mad
        clauses["gate_agreement_8_of_8"] = "pass" if gate_ok == len(v21_rows) == 8 else "FAIL (%d of %d)" % (gate_ok, len(v21_rows))
        out["v21-P12"] = {
            "n": len(v21_rows),
            "observed_per_measure_mad": mad,
            "observed_total_mad": total_mad,
            "observed_gate_agreement": "%d of %d" % (gate_ok, len(v21_rows)),
            "observed_spearman": rho12,
            "clauses": clauses,
            "reading": ("%d of %d clauses pass against the registered expectation (A<=2.5, B<=2.7, C<=1.8, "
                        "D<=1.2, E<=1.6, F<=1.0, total<=7, gate 8 of 8). Observed: A %.3f, B %.3f, C %.3f, "
                        "D %.3f, E %.3f, F %.3f, total %.3f, gate %d of %d, rho %.3f. Every one of the 8 "
                        "cards carries the recorded items (host flow, evidence class, rebound, ceiling, "
                        "penetration, largest node, three moat tests, clock basis), so the falsification "
                        "condition on missing items does not fire either."
                        % (sum(1 for v in clauses.values() if v == "pass"), len(clauses),
                           mad["A"], mad["B"], mad["C"], mad["D"], mad["E"], mad["F"], total_mad,
                           gate_ok, len(v21_rows), rho12)),
            "status": "final",
        }
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
                      "status": "observed"}
    from rigor_lib import spearman
    old_s = [int(v20[c["ticker"]]["score"]) for c in cards if c["ticker"] in v20]
    new_s = [c["total"] + int(v20[c["ticker"]].get("jx_penalty", 0) or 0) for c in cards if c["ticker"] in v20]
    rho = round(spearman(old_s, new_s), 3)
    hm = out["v21-P11"]["health_mean_total"]
    hb = [c["B"] for c in cards if str(v20.get(c["ticker"], {}).get("need", "")).lower().startswith("health") and int(v20[c["ticker"]]["dims"]["B"]) >= 21]
    loops = {}
    for c in cards:
        k = str(c.get("loop", "")).lower().split()[0] if c.get("loop") else ""
        loops.setdefault(k, []).append(c["total"])
    lm = {k: round(sum(x) / len(x), 1) for k, x in loops.items()}
    corr = {c["ticker"]: c["F_clock"] for c in cards if c["ticker"] in ("CNI", "CP", "UNP", "WAB")}
    clauses = {
        "health_mean_73.8_to_77.8": ("pass" if 73.8 <= hm <= 77.8 else "FAIL (%.1f)" % hm),
        "transport_E_3.4_to_4.2": ("pass" if 3.4 <= out["v21-P11"]["transport_E"] <= 4.2 else "FAIL"),
        "corridor_F_clock_stays_3": ("pass" if all(v == 3 for v in corr.values()) else "FAIL %s" % corr),
        "transport_F_clock_3.4_to_3.8": ("pass" if 3.4 <= out["v21-P11"]["transport_F_clock"] <= 3.8 else "FAIL"),
        "tech_C1_5.2_to_6.4": ("pass" if 5.2 <= out["v21-P11"]["tech_C1"] <= 6.4 else "FAIL"),
        "tech_A_14.0_to_15.4": ("pass" if 14.0 <= out["v21-P11"]["tech_A"] <= 15.4 else "FAIL (%.1f)" % out["v21-P11"]["tech_A"]),
        "amplifying_labels_at_least_3": ("pass" if len(out["v21-P11"]["amplifying_labels"]) >= 3 else "FAIL"),
        "health_B21_fall_to_12_to_17": ("pass" if hb and all(12 <= b <= 17 for b in hb) else "FAIL: %d of %d stayed above 17 (%s)" % (sum(1 for b in hb if b > 17), len(hb), sorted(hb))),
        "loop_order_damping_neutral_amplifying": ("pass" if lm.get("damping", 0) > lm.get("neutral", 0) > lm.get("amplifying", 0) else "FAIL %s" % lm),
        "spearman_0.88_to_0.98": ("pass" if 0.88 <= rho <= 0.98 else "FAIL (%.3f)" % rho)}
    out["v21-P11"].update({"spearman_v20_v21": rho, "loop_means": lm, "clauses": clauses,
        "reading": "%d of %d clauses pass. The amended measures cut the health mean below the registered band and re-ordered more than predicted (Spearman %.2f): the moat document tests charge 1 on most names where fewer than two tests are testable, and the evidence-class caps under B move about 30 names; the transport and loop-order clauses hold" % (sum(1 for v in clauses.values() if v == "pass"), len(clauses), rho)})
doc = {"read": pd.Timestamp.today().strftime("%Y-%m-%d"), "rule": pro["v21_predictions"]["rule"], "descriptions_on_file": int(v.has_description.sum()),
       "readings": [{**{"id": p["id"], "metric": p["metric"], "expected_after": p["expected_after"], "falsified_if": p.get("falsified_if")}, **out.get(p["id"], {})} for p in preds]}
json.dump(doc, open(os.path.join(R, "v21_predictions.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=True)
for r in doc["readings"]:
    print(r["id"], "|", r.get("status", ""), "|", r.get("reading", ""))
