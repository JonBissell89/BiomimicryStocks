# -*- coding: utf-8 -*-
"""Layer 0 audit: the civilization imbalance map, checked before any score.

The architecture this enforces: the imbalance exists independently of any
company. Every system separates STATE / DIRECTION / FLOW / CORRECTION / CLOCK /
COMPANIES, and every company in the engine must attach to at least one
already-established imbalance. A company with no imbalance behind it is the
failure mode this layer exists to prevent: finding an attractive business first
and rationalizing why it matters afterward.

Run order: audit_imbalance.py, then audit_engine_v2.py, then the build.
"""
import json, os, sys
from paths import DATA
from derive_imbalance import measure, derive_distance

FIELDS = ["id","name","cls","form","stock","safe_range","state","distance_note",
          "direction","severity","counterforce","turn","cause","correction","clock","tickers"]
COUPLING = {"grows":2, "flat":1, "weakens":0.5}
DIRECTION_RATE = {"returning":{0.5}, "holding":{1}, "diverging":{2,3}}

m = json.load(open(os.path.join(DATA,"imbalance_map.json"), encoding="utf-8"))
ser = json.load(open(os.path.join(DATA,"imbalance_series.json"), encoding="utf-8"))["series"]
eng = json.load(open(os.path.join(DATA,"engine_tiers.json"), encoding="utf-8"))
engine_tk = {n["tk"]: n for t in eng["tiers"] for n in t["names"]}

errs, warns = [], []
sy = m["systems"]

# ---- schema, arithmetic, hygiene -------------------------------------------
seen=set()
for s in sy:
    sid=s.get("id","?")
    for f in FIELDS:
        if f not in s: errs.append(f"{sid}: missing field {f}")
    if sid in seen: errs.append(f"duplicate id {sid}")
    seen.add(sid)
    if s.get("cls") not in ("earth","provisioning"): errs.append(f"{sid}: bad cls")
    if s.get("form") not in ("overshoot","deficit","both"): errs.append(f"{sid}: bad form")
    sv=s.get("severity",{})
    D,L,R,X,I=(sv.get(k) for k in ("distance","load","rate","exposure","irreversibility"))
    if D not in (0,1,2,3,4,5,6): errs.append(f"{sid}: distance {D}")
    if L not in (1,2,3): errs.append(f"{sid}: load {L}")
    if R not in (0.5,1,2,3): errs.append(f"{sid}: rate {R}")
    if X not in (1,2,3): errs.append(f"{sid}: exposure {X}")
    if I not in (1,2,3): errs.append(f"{sid}: irreversibility {I}")
    raw=D*L*R*X*I
    if abs(raw-sv.get("raw",-1))>0.05: errs.append(f"{sid}: raw {sv.get('raw')} != {raw}")
    if sv.get("index")!=round(raw): errs.append(f"{sid}: index {sv.get('index')} != {round(raw)}")
    if raw>m["_severity"]["ceiling"]: errs.append(f"{sid}: index above the instrument ceiling")
    c=s.get("counterforce",{})
    if c.get("pressure") not in (0,1,2,3): errs.append(f"{sid}: counterforce pressure {c.get('pressure')}")
    if c.get("access") not in (0,1,2,3): errs.append(f"{sid}: counterforce access {c.get('access')}")
    if c.get("coupling") not in COUPLING: errs.append(f"{sid}: counterforce coupling {c.get('coupling')}")
    for f2 in ("mechanisms","alternatives","evidence"):
        if not c.get(f2): errs.append(f"{sid}: counterforce needs {f2}")
    t=s.get("turn",{})
    want=round(D*c.get("pressure",0)*c.get("access",0)*COUPLING.get(c.get("coupling"),0))
    if t.get("value")!=want: errs.append(f"{sid}: turn {t.get('value')} != {want}")
    if t.get("ceiling")!=108: errs.append(f"{sid}: turn ceiling")
    d=s.get("direction")
    if d not in DIRECTION_RATE: errs.append(f"{sid}: direction {d}")
    elif R not in DIRECTION_RATE[d]: errs.append(f"{sid}: direction {d} inconsistent with rate {R}")
    for tk in s.get("tickers",[]):
        if tk not in engine_tk: errs.append(f"{sid}: ticker {tk} not in engine")

def every_string(o):
    if isinstance(o,str): yield o
    elif isinstance(o,dict):
        for v in o.values(): yield from every_string(v)
    elif isinstance(o,list):
        for v in o: yield from every_string(v)
for t in every_string(m):
    if "—" in t: errs.append("em dash in: "+t[:60])
    if any(ord(c)>127 for c in t): errs.append("non-ascii in: "+t[:60])

# ---- adherence: every written label must match its measurement --------------
for s2 in sy:
    e=ser.get(s2["id"]); mm=measure(e) if e else None
    if mm is None: errs.append(s2["id"]+": no measurable series, so movement cannot adhere"); continue
    if s2["direction"]!=mm["movement"]:
        errs.append("%s: written movement '%s' disagrees with the measured '%s'; run derive_imbalance.py"
                    % (s2["id"],s2["direction"],mm["movement"]))
    dd=derive_distance(s2)
    if dd is not None and s2["severity"]["distance"]!=dd:
        errs.append("%s: written distance %d disagrees with the control variable's %d; run derive_imbalance.py"
                    % (s2["id"],s2["severity"]["distance"],dd))
    st=s2.get("measured")
    if not st or st.get("movement")!=mm["movement"] or abs(st.get("rate",1e9)-mm["rate"])>1e-6:
        errs.append(s2["id"]+": stored measurement is stale; run derive_imbalance.py")

# ---- coverage: every company traces to a pre-existing imbalance ------------
# ---- the time series: one per stock, dated, ascending, numeric --------------
for s2 in sy:
    e=ser.get(s2["id"])
    if not e: errs.append(s2["id"]+": no time series"); continue
    if not e.get("unit"): errs.append(s2["id"]+": series without a unit")
    pts=e.get("points",[])
    if len(pts)<2 and s2["id"]!="transport": warns.append(s2["id"]+": fewer than 2 points")
    dates=[p[0] for p in pts]
    if dates!=sorted(dates): errs.append(s2["id"]+": series dates not ascending")
    for pt in pts:
        d,v=pt[0],pt[1]
        if not isinstance(v,(int,float)): errs.append(s2["id"]+": non-numeric value at "+str(d))
        if len(pt)>2 and pt[2]!="carried": errs.append(s2["id"]+": unknown point flag "+str(pt[2]))
for sid in ser:
    if sid not in {s2["id"] for s2 in sy}: errs.append("series for unknown system: "+sid)

mapped={tk for s in sy for tk in s["tickers"]}
orphans=sorted(set(engine_tk)-mapped)
if orphans: errs.append("companies with NO imbalance behind them: "+", ".join(orphans))
ghost_gaps=[s["id"] for s in sy if not s["tickers"]]
for s in sy:
    if s["cls"]=="earth" and not s.get("envelope"): warns.append(s["id"]+": earth-system row without a rhythm/envelope note")

# ---- report ----------------------------------------------------------------
print("LAYER 0  civilization imbalance map  (as of %s)" % m.get("asof","?"))
print("systems: %d  (%d earth-system, %d provisioning)" % (
    len(sy), sum(1 for s in sy if s["cls"]=="earth"), sum(1 for s in sy if s["cls"]=="provisioning")))
print("companies mapped: %d of %d in the engine" % (len(mapped & set(engine_tk)), len(engine_tk)))
print()
print("%-8s %-7s %-13s %-44s %-10s %s" % ("index","turn","class","system","movement","companies"))
for s in sorted(sy,key=lambda x:-x["severity"]["index"]):
    print("%4d/%-3d %3d/108 %-13s %-44s %-10s %d" % (s["severity"]["index"],m["_severity"]["ceiling"],s["turn"]["value"],s["cls"],s["name"],s["direction"],len(s["tickers"])))
print()
if ghost_gaps:
    print("corrections with NO company in the current universe (a finding, not an error):")
    print("  " + ", ".join(ghost_gaps))
print()

# one full traversal, to show the chain the hierarchy demands
fw=next(s for s in sy if s["id"]=="freshwater")
print("TRAVERSAL (freshwater):")
print("  STATE      "+fw["state"])
print("  MOVEMENT   "+fw["direction"]+" (relative to the safe range)")
if "envelope" in fw: print("  ENVELOPE   "+fw["envelope"])
print("  FLOW       "+fw["cause"])
print("  COUNTER    "+fw["counterforce"]["mechanisms"])
print("  ACCESS     "+fw["counterforce"]["alternatives"])
print("  TURN       %d/108 (pressure %d, access %d, coupling %s)" % (fw["turn"]["value"],fw["counterforce"]["pressure"],fw["counterforce"]["access"],fw["counterforce"]["coupling"]))
print("  CORRECTION "+fw["correction"])
print("  CLOCK      "+fw["clock"])
print("  COMPANIES  "+", ".join("%s (%d %s)"%(tk,engine_tk[tk]["score"],
      next(t["id"] for t in eng["tiers"] for n in t["names"] if n["tk"]==tk)) for tk in fw["tickers"]))
print()

if warns:
    print("warnings:"); [print("  -",w) for w in warns]
if errs:
    print("ERRORS: %d" % len(errs)); [print("  !",e) for e in errs]; sys.exit(1)
print("layer 0 audit: clean")
