# -*- coding: utf-8 -*-
"""Place and rebalance the artifact's own $5,000 against the current engine.

This is the page's house ledger: a SIMULATION in virtual dollars that holds what
the ranking itself implies, so a visitor can see the engine's own judgment running
alongside their picks and the S&P. It is not advice and nobody's real money moves.

Targets:
  - only names that clear the survivability gate and have a price
  - tier exposure follows the framework's own guardrails: T1 60%, T2 28%, T3 12%.
    T4 and exit-review get nothing, which is what those tiers mean.
  - equal weight inside a tier. Per-name size therefore differs between tiers,
    because the guardrail is about total exposure per tier, not per company.

Rebalancing sells anything that left the eligible set (a tier demotion, a gate
failure, a removal) and trues everything else up to target. A drift threshold
keeps the transaction log readable instead of churning on cent-level moves.

Run with --dry to see the plan without writing.
"""
import os
from paths import DATA
import json, sys, warnings
from datetime import datetime, timezone
warnings.filterwarnings("ignore")
import pandas as pd, yfinance as yf

D = DATA
TIER_W = {"t1": 0.60, "t2": 0.28, "t3": 0.12}
FUND = 5000.0
MIN_TRADE = 2.00        # dollars
MIN_DRIFT = 0.03        # and at least 3% off target
DRY = "--dry" in sys.argv

eng = json.load(open(os.path.join(D, "engine_tiers.json"), encoding="utf-8"))
state = json.load(open(os.path.join(D, "paper_state.json"), encoding="utf-8"))
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

rows = [(t["id"], n) for t in eng["tiers"] for n in t["names"]]
elig = [(tid, n) for tid, n in rows if tid in TIER_W and n.get("gate") != "fail"]

held = set(state.get("positions", {}).keys())
need = sorted({n["tk"] for _, n in elig} | held)
px = yf.download(need, period="5d", progress=False, threads=True, auto_adjust=True)["Close"]
last = px.ffill().iloc[-1]
asof = str(px.index[-1].date())
price = {t: round(float(last.get(t)), 4) for t in need
         if pd.notna(last.get(t)) and float(last.get(t)) > 0}
missing = [t for t in need if t not in price]
if missing:
    print(f"  no price for {missing}, excluded from targets this run")

elig = [(tid, n) for tid, n in elig if n["tk"] in price]
by_tier = {}
for tid, n in elig:
    by_tier.setdefault(tid, []).append(n)

# ---- portfolio value now -------------------------------------------------
pos = {tk: dict(p) for tk, p in state.get("positions", {}).items()}
funded = state.get("cash") is not None
cash = float(state.get("cash") or 0.0)
if not funded:
    cash = FUND
    state["start"] = {"date": today, "cash": FUND}
    state.setdefault("txns", []).append(
        {"d": today, "a": "START", "amt": FUND, "by": "The list"})
    print(f"funding the house ledger with ${FUND:,.0f} on {today}")

mv = sum(p["shares"] * price.get(tk, 0.0) for tk, p in pos.items())
total = cash + mv
print(f"portfolio value ${total:,.2f}  (cash ${cash:,.2f} + positions ${mv:,.2f})"
      f"   prices as of {asof}")

# ---- targets -------------------------------------------------------------
target = {}
for tid, names in by_tier.items():
    per = total * TIER_W[tid] / len(names)
    for n in names:
        target[n["tk"]] = per
for tk in pos:
    target.setdefault(tk, 0.0)      # anything no longer eligible goes to zero

print("\ntarget book")
for tid in ("t1", "t2", "t3"):
    if tid in by_tier:
        per = total * TIER_W[tid] / len(by_tier[tid])
        print(f"  {tid}: {len(by_tier[tid])} names x ${per:,.2f} "
              f"= ${total*TIER_W[tid]:,.2f} ({TIER_W[tid]*100:.0f}%)")

# ---- trades --------------------------------------------------------------
trades = []
for tk in sorted(target, key=lambda t: -target[t]):
    p = price.get(tk)
    if not p:
        continue
    cur = pos.get(tk, {}).get("shares", 0.0) * p
    want = target[tk]
    d = want - cur
    if want == 0 and cur > 0.005:
        trades.append((tk, "SELL", cur, p))
        continue
    if abs(d) < MIN_TRADE or (want > 0 and abs(d) / want < MIN_DRIFT):
        continue
    trades.append((tk, "BUY" if d > 0 else "SELL", abs(d), p))

sells = [t for t in trades if t[1] == "SELL"]
buys = [t for t in trades if t[1] == "BUY"]
print(f"\n{len(sells)} sells, {len(buys)} buys")
for tk, side, amt, p in sells + buys:
    why = "" if target.get(tk, 0) else "  (no longer eligible)"
    print(f"  {side:<4s} ${amt:>8,.2f}  {tk}{why}")

if DRY:
    print("\ndry run, nothing written")
    sys.exit(0)

# apply sells first so cash is available
txns = state.setdefault("txns", [])
for tk, side, amt, p in sells:
    sh = amt / p
    q = pos.get(tk)
    if not q:
        continue
    sh = min(sh, q["shares"])
    ratio = sh / q["shares"] if q["shares"] else 0
    q["cost"] = round(q["cost"] * (1 - ratio), 6)
    q["shares"] = round(q["shares"] - sh, 8)
    cash += sh * p
    txns.append({"d": today, "a": "SELL", "tk": tk, "sh": round(sh, 6),
                 "px": p, "amt": round(sh * p, 2), "by": "The list"})
    if q["shares"] < 1e-6:
        pos.pop(tk, None)

for tk, side, amt, p in buys:
    amt = min(amt, cash)
    if amt < MIN_TRADE:
        continue
    sh = amt / p
    q = pos.setdefault(tk, {"shares": 0.0, "cost": 0.0})
    q["shares"] = round(q["shares"] + sh, 8)
    q["cost"] = round(q["cost"] + amt, 6)
    cash -= amt
    txns.append({"d": today, "a": "BUY", "tk": tk, "sh": round(sh, 6),
                 "px": p, "amt": round(amt, 2), "by": "The list"})

state["positions"] = pos
state["cash"] = round(cash, 2)
state["last_rebalance"] = today
json.dump(state, open(os.path.join(D, "paper_state.json"), "w", encoding="utf-8"))

newmv = sum(p["shares"] * price.get(tk, 0.0) for tk, p in pos.items())
print(f"\nafter: {len(pos)} positions worth ${newmv:,.2f} + ${cash:,.2f} cash "
      f"= ${newmv+cash:,.2f}")
big = sorted(((p["shares"] * price.get(tk, 0), tk) for tk, p in pos.items()), reverse=True)[:3]
print("largest: " + ", ".join(f"{tk} {100*v/(newmv+cash):.1f}%" for v, tk in big))
