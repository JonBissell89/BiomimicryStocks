# -*- coding: utf-8 -*-
"""Owner ruling (Aug 28 2026): the health values distinction belongs in the engine,
not in a display filter.

Applied as a CAP derived from the rubric's own band definitions, not as an arbitrary
deduction. C2's top band (7-8) reads "revenue survives, or grows, if the system
rebalances". The 'embedded' tag reads "economics depend on premium reimbursement
inside the existing payment machine". Those are contradictory statements, so an
embedded name cannot occupy the top C2 band. Cap at 6, the top of the neutral band,
where a name can still sit if the product is needed regardless and only margin
compresses.

Pushback names are untouched: their C2 was already scored on its merits, and several
sit LOW (CorMedix 3) precisely because preventing the problem shrinks their own market.
That is the engine working, and it is why this is a cap rather than a bonus.
"""
import os
from paths import DATA
import json, datetime
D = DATA
P = os.path.join(D, "engine_tiers.json")
eng = json.load(open(P, encoding="utf-8"))
CAP = 6
STAMP = datetime.datetime.now().strftime("%Y-%m-%d")

def band(s):
    return "t1" if s >= 80 else "t2" if s >= 74 else "t3" if s >= 69 else "t4" if s >= 65 else "exit"

moved = []
for t in eng["tiers"]:
    for n in t["names"]:
        if (n.get("values") or "").strip().lower() != "embedded":
            continue
        c2 = n["dims"]["C2"]
        if c2 <= CAP:
            continue
        n["dims"]["C2"] = CAP
        n["score_base"] = sum(n["dims"].values())
        old = n["score"]
        n["score"] = n["score_base"] + n["jx_penalty"]
        n["coupling"] = "neutral" if n["coupling"] == "survives" else n["coupling"]
        n["note"] = (f"[{STAMP}] C2 capped {c2}->{CAP} by the embedded-economics ruling: "
                     f"revenue tied to premium reimbursement cannot occupy the C2 band "
                     f"reserved for revenue that survives a rebalance. " + (n.get("note") or ""))[:400]
        moved.append((n["tk"], c2, old, n["score"], band(old), band(n["score"])))

# re-tier
alln = [n for t in eng["tiers"] for n in t["names"]]
LAB = {t["id"]: t["label"] for t in eng["tiers"]}
buckets = {k: [] for k in ["t1", "t2", "t3", "t4", "exit"]}
for n in sorted(alln, key=lambda x: -x["score"]):
    buckets[band(n["score"])].append(n)
eng["tiers"] = [{"id": k, "label": LAB.get(k, k), "names": v} for k, v in buckets.items() if v]

eng["_rulings"] = (eng.get("_rulings", "") + " || VALUES RULING (Aug 28 2026): the health "
    "embedded/pushback distinction is scored, not filtered. An 'embedded' name, whose economics "
    "depend on premium reimbursement inside the existing payment machine, is capped at C2=6 "
    "because the C2 top band is reserved for revenue that survives a system rebalance. The "
    "display filter that used to hide these names was removed; the judgment now lives in the "
    "score where it can be audited. Pushback names are untouched and several score LOW on C2 "
    "on their own merits, CorMedix at 3, because preventing a problem shrinks its own market.")
json.dump(eng, open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

print(f"names moved: {len(moved)}")
for tk, c2, old, new, bo, bn in moved:
    tier = f"  {bo} -> {bn}" if bo != bn else ""
    print(f"  {tk:<7s} C2 {c2}->{CAP}   score {old} -> {new}{tier}")
print()
for t in eng["tiers"]:
    print(f"  {t['id']:<5s} n={len(t['names']):<3d} "
          f"{' '.join(n['tk'] for n in t['names'])}")
