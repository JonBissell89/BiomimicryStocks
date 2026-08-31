# -*- coding: utf-8 -*-
"""The derivation layer: the map's labels must follow its measurements.

Movement is derived from each stock's own time series. Distance is derived
from the control variable wherever one exists. Severity and turn are then
recomputed from the corrected components. Where a derived value disagrees
with a written label, the label is overwritten and the correction is
reported: prose is not authority here.

Run order in the weekly chain: collect_imbalance.py, then this, then
audit_imbalance.py (which re-derives everything and fails on any mismatch).
"""
import json, os, datetime
from paths import DATA

COUPLING = {"grows": 2, "flat": 1, "weakens": 0.5}
RATE_OF = {"returning": 0.5, "holding": 1}   # a diverging label keeps its judged 2 or 3

def distinct(points):
    """Collapse the collector's carried weekly samples, but keep a genuine
    re-assessment: an equal value a year or more after the last kept reading is
    a measurement of holding, not a carry."""
    out = []
    for d, v in ((p[0], p[1]) for p in points):
        if not out or v != out[-1][1]:
            out.append((d, v)); continue
        gap = (datetime.date.fromisoformat(d) - datetime.date.fromisoformat(out[-1][0])).days
        if gap >= 365:
            out.append((d, v))
    return out

def measure(entry):
    """Movement and rate from the series: the last decade of distinct readings,
    or the last two distinct readings when the decade holds fewer."""
    obs = [p for p in entry["points"] if len(p) < 3 or p[2] != "carried"]
    pts = distinct(obs)
    if len(pts) < 2:
        return None
    end = datetime.date.fromisoformat(pts[-1][0])
    cut = end.replace(year=end.year - 10)
    win = [p for p in pts if datetime.date.fromisoformat(p[0]) >= cut]
    if len(win) < 2:
        win = pts[-2:]
    (d0, v0), (d1, v1) = win[0], win[-1]
    years = (datetime.date.fromisoformat(d1) - datetime.date.fromisoformat(d0)).days / 365.25
    rate = (v1 - v0) / years if years else 0.0
    rel = (v1 - v0) / abs(v0) if v0 else 0.0
    if abs(rel) <= 0.01:
        movement = "holding"
    else:
        movement = "diverging" if rel * entry["away"] > 0 else "returning"
    return {"movement": movement, "rate": round(rate, 4),
            "window": [d0[:4], d1[:4]], "rel": round(rel, 4)}

def band(ratio):
    if ratio < 1: return 0
    if ratio <= 1.02: return 1
    if ratio < 2: return 2
    if ratio < 10: return 3
    if ratio < 100: return 4
    return 5

def derive_distance(system):
    c = system.get("control")
    if not c: return None
    b, cur = c["boundary"], c["current"]
    if b == 0 or cur == 0: return None
    ratio = cur / b if cur >= b and b > 0 else (b / cur if b > 0 else None)
    # a floor variable (staying above the boundary is safe) inverts
    if system["id"] in ("forests", "materials", "ocean") or (0 < cur < b):
        ratio = b / cur
    elif cur >= b:
        ratio = cur / b
    return band(ratio)

def derive_all(m, ser):
    corrections = []
    for s in m["systems"]:
        e = ser["series"].get(s["id"])
        mm = measure(e) if e else None
        if mm:
            summary = ("%+.3g per year in the chart's unit, measured %s to %s; "
                       "movement is derived from this record, not assigned"
                       % (mm["rate"], mm["window"][0], mm["window"][1]))
            dd = derive_distance(s)
            if dd is not None:
                summary += ". Distance is derived from the control variable"
            s["measured"] = {"movement": mm["movement"], "rate": mm["rate"],
                             "window": mm["window"], "distance": dd, "summary": summary}
            if s["direction"] != mm["movement"]:
                corrections.append("%s: movement %s -> %s (the series says so)"
                                   % (s["id"], s["direction"], mm["movement"]))
                s["direction"] = mm["movement"]
                if mm["movement"] in RATE_OF:
                    s["severity"]["rate"] = RATE_OF[mm["movement"]]
                elif s["severity"]["rate"] not in (2, 3):
                    s["severity"]["rate"] = 2
            if dd is not None and s["severity"]["distance"] != dd:
                corrections.append("%s: distance %d -> %d (the control variable says so)"
                                   % (s["id"], s["severity"]["distance"], dd))
                s["severity"]["distance"] = dd
        sv = s["severity"]
        raw = sv["distance"] * sv["load"] * sv["rate"] * sv["exposure"] * sv["irreversibility"]
        sv["raw"] = round(raw, 1); sv["index"] = round(raw)
        c = s["counterforce"]
        s["turn"] = {"value": round(sv["distance"] * c["pressure"] * c["access"] * COUPLING[c["coupling"]]),
                     "ceiling": 108}
    return corrections

def main():
    mp = os.path.join(DATA, "imbalance_map.json")
    sp = os.path.join(DATA, "imbalance_series.json")
    m = json.load(open(mp, encoding="utf-8"))
    ser = json.load(open(sp, encoding="utf-8"))
    corrections = derive_all(m, ser)
    json.dump(m, open(mp, "w", encoding="utf-8"), indent=1)
    print("derivation layer: %d systems measured" % len(m["systems"]))
    if corrections:
        print("labels corrected by measurement:")
        for c in corrections: print("  -", c)
    else:
        print("every written label already matches its measurement")

if __name__ == "__main__":
    main()
