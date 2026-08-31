"""Balanced Systems Console: narrative single-page app.
Flow: What is this -> The idea -> How it was judged -> Results and your $5,000
(one section: fund, browse and add any ticker, spread a lump sum) ->
Track over time -> Compare -> Full rules.
Self-saving artifact (house ledger); every visitor gets their own browser ledger.
Sync paper_state.json from the published artifact BEFORE regenerating."""
import os
from paths import BUILD, DATA
import json, time, urllib.parse, warnings
from datetime import datetime, timezone
warnings.filterwarnings("ignore")
import pandas as pd
import yfinance as yf

DATA = DATA
OUT = (os.path.join(BUILD, "bs_console.html"))

eng = json.load(open(os.path.join(DATA, "engine_tiers.json"), encoding="utf-8"))
state = json.load(open(os.path.join(DATA, "paper_state.json"), encoding="utf-8"))
sidx = json.load(open(os.path.join(DATA, "search_index.json"), encoding="utf-8"))
imb_map = json.load(open(os.path.join(DATA, "imbalance_map.json"), encoding="utf-8"))
# Prices for the whole searchable universe, so a visitor can buy companies that
# never made the list. Names without a price are addable but not buyable.
try:
    pxcache = json.load(open(os.path.join(DATA, "price_cache.json"), encoding="utf-8")).get("px", {})
    pxcache = {k: v for k, v in pxcache.items() if v}
except Exception:
    pxcache = {}
# A year of weekly closes per ranked company, normalised to the first close, so a
# row can show its own shape instead of only today's number.
try:
    _sp = json.load(open(os.path.join(DATA, "spark.json"), encoding="utf-8"))
    spark, spark_asof = _sp.get("s", {}), _sp.get("asof", "")
except Exception:
    spark, spark_asof = {}, ""

allnames = [(t["id"], n) for t in eng["tiers"] for n in t["names"]]
tickers = [n["tk"] for _, n in allnames] + ["^GSPC"]

# The ranked names are the one set of prices that must not be missing, and Yahoo
# rate-limits hard when a universe-wide fetch has been running. Retry with backoff,
# then fall back to the price cache for anything still short. Never ship a page
# whose ranked prices silently came back as zero.
prices, asof, last = {}, None, None
for attempt in range(5):
    need = [t for t in tickers if not prices.get(t)]
    if not need:
        break
    if attempt:
        time.sleep(20 * attempt)
    try:
        px = yf.download(need, period="5d", progress=False, threads=True, auto_adjust=True)["Close"]
        if not len(px):
            continue
        last = px.ffill().iloc[-1]
        asof = asof or str(px.index[-1].date())
        for t in need:
            v = last.get(t)
            if pd.notna(v) and v > 0:
                prices[t] = round(float(v), 2)
    except Exception as e:
        print(f"  price attempt {attempt+1}: {type(e).__name__}")
    if attempt:
        print(f"  price attempt {attempt+1}: {len(tickers)-len([t for t in tickers if prices.get(t)])} still missing")

stale = [t for t in tickers if not prices.get(t)]
for t in stale:                      # last resort: the universe cache from the previous run
    if pxcache.get(t):
        prices[t] = round(float(pxcache[t]), 2)
recovered = [t for t in stale if prices.get(t)]
missing = [t for t in tickers if not prices.get(t)]
if recovered:
    print(f"  {len(recovered)} ranked prices taken from the cached universe: {recovered}")
if missing:
    print(f"  WARNING {len(missing)} ranked names have NO price: {missing}")
for t in tickers:
    prices.setdefault(t, None)
asof = asof or datetime.now(timezone.utc).strftime("%Y-%m-%d")
stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
spx = prices.get("^GSPC")

# A reference basket so a visitor can see their own picks against the ranking itself,
# not only against the market. Equal weight across every gate-passing ranked name, so
# it is the list's own judgment with no sizing opinion layered on top. Recorded as an
# index level: it accrues forward from the first run that wrote it, and is deliberately
# NOT backfilled, because a list built with knowledge of the past would flatter itself.
basket = [n["tk"] for _, n in allnames
          if n.get("gate") != "fail" and prices.get(n["tk"])]
bpx = {t: prices[t] for t in basket}
bref = state.get("basket_ref")
if bref:
    held = [t for t in bref["px"] if bpx.get(t) and bref["px"].get(t)]
    if held:
        growth = sum(bpx[t] / bref["px"][t] for t in held) / len(held)
        basket_level = round(bref.get("scale", 100.0) * growth, 4)
    else:
        basket_level = bref.get("scale", 100.0)
else:
    basket_level = 100.0            # first run sets the base

# Rebase every run, independently of whether the house ledger takes a snapshot.
# The basket is the benchmark every visitor's ledger is measured against, so tying
# its upkeep to the house portfolio would freeze it at 100 whenever that is unfunded.
# Chain-linking on each run also means a name entering or leaving the list never
# creates a phantom jump: only names present on both sides of a step are compared.
state_dirty = False
if not bref or bref.get("date") != today:
    state["basket_ref"] = {"date": today, "px": bpx, "scale": basket_level}
    state_dirty = True

if state.get("cash") is not None:
    total = state["cash"] + sum(p["shares"] * (prices.get(tk) or 0)
                                for tk, p in state.get("positions", {}).items())
    hist = state.setdefault("history", [])
    due = True
    if hist:
        due = (datetime.now() - datetime.strptime(hist[-1]["date"], "%Y-%m-%d")).days > 6
    if due:
        hist.append({"date": today, "value": round(total, 2), "spx": spx,
                     "list": basket_level})
        state_dirty = True
        print(f"snapshot appended: {today}")
if state_dirty:
    json.dump(state, open(os.path.join(DATA, "paper_state.json"), "w", encoding="utf-8"))
print(f"list benchmark: {len(basket)} names, index level {basket_level}")

KID = {
 "WRTBY":"Makes huge engines and batteries that keep electricity working when sun and wind stop",
 "TSNLF":"Makes a foam that cleans hospital tools so germs can't spread",
 "TMRAY":"Builds the machines that give you money back for recycling bottles and cans",
 "CLPBY":"Makes medical supplies some people need every single day",
 "TDVXF":"Builds computers that talk for people who can't speak",
 "SBDHF":"Fixes old bridges and tunnels so they don't have to be torn down",
 "SSMXY":"Makes the machines that check your blood at the doctor",
 "KMDA":"Turns donated blood into medicine for people who get sick easily",
 "BB":"Makes the software brain inside millions of cars",
 "DLEGF":"Builds the power boxes that feed electricity to giant computer centers",
 "ENGCF":"Makes a wrist for excavators so one machine does the work of two",
 "CRMD":"Makes a liquid that stops infections for people on dialysis",
 "BMBRF":"Runs stores in Turkey that sell food cheaper than anyone else",
 "CODYY":"Makes what keeps buildings warm - insulation, walls, windows",
 "YMM":"An app that matches trucks with loads so trucks don't drive around empty",
 "CERS":"Cleans donated blood so it's safe to give to patients",
 "SHLS":"Makes the wires and connectors that link up big solar farms",
 "DMTRF":"Makes a gel that stops bleeding during surgery",
 "ADMA":"Makes medicine from blood for people whose bodies can't fight germs",
 "BIRMF":"Uses friendly bacteria to clean smelly air at water plants",
 "WSIOF":"Makes smart electricity meters for homes around the world",
 "NTRA":"Checks on babies before they're born and finds cancer early, from one blood draw",
 "TSM":"Makes the tiny chips inside almost every phone and computer",
 "WAB":"Builds train engines and the brakes for the biggest trains",
 "UNP":"Runs one of the biggest railroads in America",
 "LGRDY":"Makes the switches and outlets in buildings all over the world",
 "AHICF":"Makes ultra-thin wires doctors use to fix hearts without big surgery",
 "WST":"Makes the seals and parts that keep medicine safe inside its container",
 "GH":"Finds cancer early with a blood test",
 "BSY":"Makes the software engineers use to design bridges, roads and water systems",
 "TOELY":"Builds the machines that make computer chips",
 "BOEUF":"Makes bone paste with medicine inside that helps broken bones heal",
 "CP":"Runs a railroad from Canada through the US to Mexico",
 "GKOS":"Makes tiny eye implants that keep people from going blind",
 "IOT":"Puts smart sensors on trucks so drivers stay safe and use less fuel",
 "HTFL":"Uses AI to look at hearts so people can skip an invasive test",
 "VCYT":"Tests that tell doctors if a lump is dangerous or harmless",
 "PLPC":"Makes the metal pieces that hold up power lines and fiber cables",
 "CAI":"Reads the code inside a cancer to pick the medicine most likely to work",
 "CNI":"Runs a railroad across all of Canada",
 "DXCM":"Makes a patch that tells people with diabetes their sugar level all day",
 "BLLN":"Blood tests for expecting parents that check the baby's health",
 "TMDX":"Keeps donated organs alive on the way to the person who needs them",
 "CBLL":"A headband that spots brain seizures in minutes",
 "IRTC":"A sticker you wear that watches your heartbeat for weeks",
 "RMD":"Makes masks that help people breathe while they sleep",
 "MBRFF":"Cleans up dangerous industrial waste",
 "DAR":"Turns leftover food and animal scraps into fuel and ingredients",
 "MHGVY":"Raises salmon in ocean farms",
 "ATRC":"Makes tools that fix irregular heartbeats during surgery",
 "LEGH":"Builds affordable homes inside factories",
 "BFLY":"A pocket ultrasound so any doctor anywhere can look inside your body",
 "SRTA":"Flies donated organs to hospitals fast",
}

# Tier counts for the results summary, read from the engine rather than typed in,
# so they can never drift from what the table actually shows.
TIERLAB = {"t1": "Tier 1 · 80 and up", "t2": "Tier 2 · 74 to 79",
           "t3": "Tier 3 · 69 to 73", "t4": "Tier 4 · 65 to 68",
           "exit": "Exit review · under 65"}
chips = []
for t in eng["tiers"]:
    if not t["names"]:
        continue
    n_pass = sum(1 for x in t["names"] if x.get("gate") != "fail")
    gated = len(t["names"]) - n_pass
    extra = f" ({gated} set aside)" if gated else ""
    chips.append(f'<div class="tierchip"><b>{n_pass}</b>'
                 f'<span>{TIERLAB.get(t["id"], t["id"])}{extra}</span></div>')
tiersum_html = "".join(chips)

# The house book, summarised from the state the rebalancer wrote.
hp = state.get("positions", {})
hmv = sum(p["shares"] * (prices.get(tk) or 0) for tk, p in hp.items())
htot = hmv + float(state.get("cash") or 0)
hstart = (state.get("start") or {}).get("cash") or 0
hgain = htot - hstart if hstart else 0
tier_of = {n["tk"]: tid for tid, n in allnames}
hby = {}
for tk, p in hp.items():
    hby.setdefault(tier_of.get(tk, "?"), 0.0)
    hby[tier_of.get(tk, "?")] += p["shares"] * (prices.get(tk) or 0)
split = ", ".join(f"{100*v/htot:.0f}% {TIERLAB.get(k, k).split(' · ')[0]}"
                  for k, v in sorted(hby.items()) if htot)
biggest = sorted(((p["shares"] * (prices.get(tk) or 0), tk) for tk, p in hp.items()),
                 reverse=True)[:1]
house_note = (
    f"{len(hp)} companies worth ${htot:,.2f}, against the ${hstart:,.0f} it started with"
    f" on {(state.get('start') or {}).get('date', '')}"
    f", {'up' if hgain >= 0 else 'down'} ${abs(hgain):,.2f}. Split {split}."
    + (f" Largest holding {biggest[0][1]} at {100*biggest[0][0]/htot:.1f}%."
       if biggest and htot else "")
    + " Simulated money on the same terms as yours, not advice.")

names_js = []
for tid, n in allnames:
    d = n.get("dims", {})
    names_js.append([n["tk"], n["nm"], n["score"], n.get("need", ""),
                     prices.get(n["tk"]) or 0, n.get("note", ""),
                     n.get("values", ""), bool(n.get("sofi")), tid,
                     KID.get(n["tk"], ""),
                     [d.get(k, 0) for k in ("A", "B", "C1", "C2", "D_rep",
                                            "D_inhib", "D_exit", "E", "F_clock", "F_now")],
                     [n.get("stock", ""), n.get("loop", ""), n.get("coupling", ""),
                      n.get("gate", "pass"), n.get("evidence", ""), n.get("clock", "")]])

RULES_HTML = """
<h3>The gate, checked before any scoring</h3>
<p class="rl" style="max-width:82ch">Survivability is not a dimension, because a company that runs out of money did not score badly, it produced no result at all. Any of these sets a company aside regardless of its score: under 12 months of cash with no committed financing · more than 25% of the company issued as new shares over three years · a pending buyout · a going-concern doubt from its auditor. This is a reading of the balance sheet, not a judgment about the business.</p>
<h3>The 100-point score, applied to every company the same way</h3>
<p class="rl" style="max-width:82ch">Balance is a property of a <b>stock</b>, meaning something that accumulates and can run out or pile up, and a stock is in balance when its inflow and outflow match. A company is a mechanism attached to one of those flows. The six measures score the mechanism.</p>
<ul class="rl"><li><b>A · The stock · 20.</b> Name the accumulation in concrete terms. Is it load-bearing, meaning would the system degrade if it left its safe range, and is it outside that range now? No nameable stock caps this at 6. <b>The moat adjustment lives here:</b> defensibility earned by doing the job better is neutral, but defensibility that comes from blocking substitution, a chokepoint on something essential, or single-source control of a load-bearing stock takes −3, because that is holding the stock hostage.</li>
<li><b>B · The flow · 25.</b> Direction and magnitude of the effect on that stock per dollar of revenue. The heaviest single measure. The top band requires a quantified before and after; "appears to" and "likely" score at the bottom of their band, and where no evidence exists the measure is scored low and marked <i>evidence: none</i>.</li>
<li><b>C · The loop · 20.</b> Two questions. <b>Sign (12):</b> does success reduce the demand it feeds on (self-damping) or create more of it (amplifying)? <b>Coupling (8):</b> does the revenue survive if the system rebalances, or does it require the imbalance to persist? A closed loop inside a system that has to stay broken scores low here.</li>
<li><b>D · Growth pattern · 15.</b> Cells divide rather than swell, stop at contact, and dismantle obsolete parts cleanly. <b>Replication (6):</b> copies a proven unit, or grows one entity without limit. <b>Contact inhibition (5):</b> is there a size at which it stays solvent without further growth? <b>Clean exit (4):</b> when the product is obsolete, does it strand assets? An asset that does not go obsolete is not stranded.</li>
<li><b>E · Buffer · 10.</b> Efficiency that keeps slack versus efficiency bought by removing it. Distributed, modular, repairable and multi-sourced scores high. A single global plant, zero-inventory dependency, or one customer above 40% of revenue scores at the bottom. This is the fragility qualifier on B.</li>
<li><b>F · Clock · 10.</b> <b>Time constant (6):</b> months for reimbursement and substitution, years for regulation and technology displacement, decades for infrastructure, centuries for soil and aquifers. <b>Moving now (4):</b> dated orders, approvals, backlog or installed-base growth inside four quarters. Correct alignment with no momentum scores near zero here on purpose.</li></ul>
<h3>Automatic disqualifiers</h3>
<p class="rl" style="max-width:80ch">Each of these earns by holding a system out of balance on purpose, which makes the earnings a liability with a delay on it rather than a durable position:<br>War and weapons · addiction · artificial scarcity (including crypto treasuries) · planned obsolescence · keeping people chronically sick where durable healing is possible · maintaining a broken system that should disappear · concentrated factory-farm waste · profiting from water scarcity rather than reducing it · rapidly inflating system costs · a single uncertain breakthrough · excessive dilution or short runway · stagnant commercialization · undifferentiated commodities.</p>
<h3>The clock rule</h3>
<p class="rl" style="max-width:82ch">An imbalance corrects on the clock of whatever does the correcting, which is often far slower than any holding period. Direction without timing is not investable, so measure F carries the timing question directly. A company can be correctly aligned and still be a poor position for thirty years, and a company earning from a slow imbalance can pay well the whole time. The framework's claim is only about what happens when a correction actually lands, not about when it lands. One consequence is worth stating plainly: <b>this scorecard is deliberately hostile to long-clock infrastructure.</b> Every company whose correction runs on a decades scale sits at 3 of 6 on the time constant, and that is measure F working as written rather than a flaw to be patched.</p>
<h3>Tiers</h3>
<ul class="rl"><li><b>T1 · Core.</b> Score 80+. Suggested 50–70% of a plan.</li>
<li><b>T2 · Growers.</b> Score 74–79. Suggested 20–35%.</li>
<li><b>T3 · Catalysts.</b> Score 69–73, riskier, often waiting on one specific event. Suggested 5–15%, sized so a total loss wouldn't hurt much.</li>
<li><b>T4 · Weak signal.</b> Score 65–68. The correction is real but slow, partial, or thinly evidenced.</li>
<li><b>Exit review.</b> Below 65. Held only for a stated reason, and the reason is on the record.</li>
<li><b>SAND.</b> Kept by choice outside the rules. 0–10%.</li></ul>
<p class="rl" style="max-width:82ch"><b>The bands do not move when the scorecard changes.</b> Rebuilding the engine on the stock-and-flow measures moved 42 of 53 companies down and dropped the average by 7 points. Sliding the tier bands down to keep the same number of names in T1 would have reproduced the previous answer by arithmetic. They were left where they were, and T1 got smaller.</p>
<h3>Rulings that shaped this list (Aug 27, 2026)</h3>
<ul class="rl"><li><b>Health tags:</b> <i class="pb2">pb</i> = makes healthcare cheaper or fairer overall · <i class="emb2">emb</i> = earns through premium prices paid by insurance. Tags get re-checked against evidence when challenged (Tristel confirmed <i>pb</i> at roughly 10× cheaper per use; Cerus moved to <i>emb</i> on evidence of +30% cost per unit).</li>
<li><b>Country risk is scored, not hidden:</b> China-VIE −6 · China-direct −4 · Taiwan-linked −2.</li>
<li><b>Food:</b> distributing industrial food efficiently is optimization, not regeneration. It moves an existing flow faster without changing what the flow does to any stock, so it scores in the neutral band on the flow measure.</li>
<li><b>Two removal rules:</b> a company carrying both a country penalty and a values-sensitive health tag is removed; so is one majority-controlled by an operator of an excluded system.</li>
<li><b>Price is a view, not a merit test.</b> With fractional shares, a $400 stock and a $4 stock are equally buyable.</li>
<li><b>A closed loop is not enough on its own.</b> If the loop's inputs are the waste stream of a system that has to stay out of balance for those inputs to keep arriving, the coupling measure scores it low however elegant the loop is. This is what moved Darling Ingredients down, and the evidence is not hypothetical: management reported the US cattle herd at a 75-year low.</li>
<li><b>Depth:</b> every company on the list is now scored on all six measures with the same evidence standard. The older split between deep and light audits is gone.</li></ul>
<p class="rl" style="color:var(--muted)">Research output, not investment advice. The author is not a licensed financial advisor. All trading here is simulated with pretend money.</p>
"""

TEMPLATE = r"""<title>Balanced Systems Console</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --ground:#F7F9F8; --card:#FFFFFF; --ink:#16211F; --muted:#5C6B67;
  --accent:#1D5D51; --accent-soft:#E3EEEB; --warn:#A8663B; --warn-soft:#F6ECE4;
  --line:#DCE4E1; --chipbg:#EDF2F0; --good:#1D5D51; --bad:#A8663B;
  --serif:"Newsreader",Georgia,serif; --sans:"IBM Plex Sans",system-ui,sans-serif; --mono:"IBM Plex Mono",Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --ground:#101715; --card:#17201D; --ink:#E8EEEB; --muted:#93A39E;
  --accent:#5FA894; --accent-soft:#1C2E29; --warn:#D08B5C; --warn-soft:#2C231A;
  --line:#26332F; --chipbg:#1E2A26; --good:#5FA894; --bad:#D08B5C;}}
:root[data-theme="dark"]{
  --ground:#101715; --card:#17201D; --ink:#E8EEEB; --muted:#93A39E;
  --accent:#5FA894; --accent-soft:#1C2E29; --warn:#D08B5C; --warn-soft:#2C231A;
  --line:#26332F; --chipbg:#1E2A26; --good:#5FA894; --bad:#D08B5C;}
*{box-sizing:border-box}
body{background:var(--ground);color:var(--ink);font-family:var(--sans);margin:0;line-height:1.55;font-size:15px}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px 90px}
nav{position:sticky;top:0;z-index:20;background:var(--ground);border-bottom:1px solid var(--line);display:flex;gap:2px;flex-wrap:wrap;align-items:center;padding:8px 0;margin-bottom:4px}
nav a{font-family:var(--mono);font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);text-decoration:none;padding:6px 9px;border-radius:4px;white-space:nowrap}
nav a:hover{background:var(--chipbg);color:var(--ink)}
nav .money{margin-left:auto;font-family:var(--mono);font-size:12px;color:var(--muted);white-space:nowrap}
nav .money b{color:var(--ink);font-size:14px}
section{padding:34px 0 10px;border-bottom:1px solid var(--line)}
section:last-of-type{border-bottom:none}
.step{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 6px}
h1{font-family:var(--serif);font-weight:500;font-size:clamp(29px,5.4vw,44px);line-height:1.04;margin:0 0 14px;text-wrap:balance}
h2{font-family:var(--serif);font-weight:600;font-size:clamp(21px,3.2vw,27px);margin:0 0 10px;text-wrap:balance}
h3{font-family:var(--serif);font-weight:600;font-size:17px;margin:18px 0 6px}
p.lede{font-size:17px;color:var(--ink);max-width:70ch;margin:0 0 12px}
p{max-width:76ch;color:var(--muted)}
p b,li b{color:var(--ink)}
.hero{padding:40px 0 18px}
.big3{display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:14px;margin:18px 0}
.big3 .c{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:15px 17px}
.big3 .n{font-family:var(--serif);font-size:26px;font-weight:600}
.big3 .l{font-size:13px;color:var(--muted);line-height:1.4}
.panel{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px 18px;margin:12px 0}
input,select,textarea{font-family:var(--mono);font-size:13px;padding:7px 9px;border:1px solid var(--line);border-radius:5px;background:var(--ground);color:var(--ink)}
input:focus,select:focus,button:focus,a:focus{outline:2px solid var(--accent);outline-offset:1px}
button{font-family:var(--mono);font-size:12.5px;padding:8px 14px;border:1px solid var(--accent);border-radius:5px;background:var(--accent-soft);color:var(--accent);cursor:pointer}
button:hover{background:var(--accent);color:var(--card)}
button:disabled{opacity:.45;cursor:not-allowed}
button.sell{border-color:var(--warn);background:var(--warn-soft);color:var(--warn)}
button.sell:hover{background:var(--warn);color:var(--card)}
button.ghost{border-color:var(--line);background:none;color:var(--muted)}
button.big{font-size:15px;padding:12px 22px}
.controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap;font-size:13px;margin:10px 0}
.controls label{cursor:pointer;white-space:nowrap}
input[type=range]{width:100%;accent-color:var(--accent);padding:0}
.tablewrap{overflow-x:auto;margin:8px 0}
table{border-collapse:collapse;width:100%;font-size:12.5px}
table.mkt{min-width:1040px}
th{font-family:var(--mono);font-size:9.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);text-align:left;padding:7px;border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:6px 7px;border-bottom:1px solid var(--line);vertical-align:middle;font-variant-numeric:tabular-nums}
td.tk{font-family:var(--mono);font-weight:500;white-space:nowrap}
td.co{max-width:300px}
td.co .cn{color:var(--ink);font-size:12.5px;white-space:nowrap}
td.co .blurb{color:var(--muted);font-size:11.5px;line-height:1.35;white-space:normal}
td.nm{color:var(--muted);font-size:12px;white-space:nowrap}
td.r{text-align:right;font-family:var(--mono);white-space:nowrap}
td input.wt{width:50px;font-size:12px;padding:3px 5px}
td input.amt{width:74px;font-size:12px;padding:3px 5px}
.tierpill{font-family:var(--mono);font-size:9.5px;color:var(--accent)}
.vtag{font-family:var(--mono);font-size:9.5px;padding:1px 5px;border-radius:3px;margin-left:5px}
.vtag.pb,.pb2{background:var(--accent-soft);color:var(--accent);font-style:normal;padding:1px 5px;border-radius:3px}
.vtag.emb,.emb2{background:var(--chipbg);color:var(--muted);font-style:normal;padding:1px 5px;border-radius:3px}
.legend{font-family:var(--mono);font-size:11.5px;color:var(--muted);margin:6px 0 0;max-width:none}
tr.ownrow td{background:var(--accent-soft)}
tr.ownrow .tierpill{font-weight:600}
.dropx{background:none;border:0;color:var(--muted);font-size:14px;line-height:1;padding:0 0 0 5px;cursor:pointer;min-height:0}
.dropx:hover{color:var(--bad);background:none}
/* Three views, one file. The nav swaps which is shown; the hash drives it so the
   back button and shared links behave. No server, no extra page loads. */
.view{display:none}
nav a.tab{border:1px solid transparent}
nav a.tab.on{color:var(--accent);border-color:var(--line);background:var(--chipbg)}
.plusref{font-style:normal;font-family:var(--mono);color:var(--accent);font-weight:600}

/* Rows open a detail panel, because a title attribute does not exist on a phone
   and all the reasoning behind a score was unreachable there. */
tr.rowclick{cursor:pointer}
tr.rowclick:hover td{background:var(--chipbg)}
tr.rowclick:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.modal{position:fixed;inset:0;z-index:60;display:flex;align-items:center;justify-content:center;padding:18px}
.modal[hidden]{display:none}
.modalbg{position:absolute;inset:0;background:rgba(0,0,0,.55)}
.modalcard{position:relative;background:var(--ground);border:1px solid var(--line);border-radius:10px;
 max-width:640px;width:100%;max-height:88vh;overflow-y:auto;padding:20px 22px 22px}
.modalx{position:absolute;top:8px;right:10px;background:none;border:0;color:var(--muted);
 font-size:24px;line-height:1;padding:4px 8px;min-height:0;cursor:pointer}
.modalx:hover{color:var(--ink);background:none}
.dhead{display:flex;align-items:baseline;gap:9px;margin:0 30px 4px 0;flex-wrap:wrap}
.dtier{font-family:var(--mono);font-size:10.5px;color:var(--accent);letter-spacing:.06em}
.dhead h3{margin:0;font-size:19px}
.dtk{font-family:var(--mono);font-size:13px;color:var(--muted);font-weight:400}
.dblurb{font-size:13.5px;color:var(--muted);margin:4px 0 12px;line-height:1.5}
.dstats{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 14px}
.dstat{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:7px 11px;min-width:82px}
.dstat span{display:block;font-family:var(--mono);font-size:9.5px;letter-spacing:.06em;
 text-transform:uppercase;color:var(--muted);margin-bottom:2px}
.dstat b{font-family:var(--mono);font-size:15px;font-variant-numeric:tabular-nums}
.dstat b i{font-style:normal;font-size:10px;color:var(--muted)}
.dact{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:16px;
 padding-top:14px;border-top:1px solid var(--line)}
.dact input{width:120px}

/* A running count of what you have picked, where you are picking it. */

/* The three lines over time. Percentage change from each series' own first
   reading, which is the only honest way to put a $5,000 book and an index on
   the same axis. */
.chartwrap{background:var(--card);border:1px solid var(--line);border-radius:8px;
 padding:12px 14px 8px;margin:14px 0 10px}
.chartwrap svg{display:block;width:100%;height:auto;color:var(--ink)}
.chartleg{display:flex;flex-wrap:wrap;gap:16px;margin-top:8px;padding-top:9px;
 border-top:1px solid var(--line);font-family:var(--mono);font-size:12px;color:var(--muted)}
.chartleg .lg{display:flex;align-items:center;gap:7px}
.chartleg .lg i{width:14px;height:3px;border-radius:2px;display:inline-block}
.chartleg .lg b{font-variant-numeric:tabular-nums}
.chartempty{background:var(--card);border:1px dashed var(--line);border-radius:8px;
 padding:22px 16px;margin:14px 0 10px;color:var(--muted);font-size:13px;text-align:center}

/* The basket. Picking a set and splitting one number across it is one decision
   you can check before it happens, instead of twenty guesses typed into rows. */
.basket{border:1px solid var(--accent);border-radius:8px;padding:14px 16px;margin:6px 0 12px;
 background:var(--accent-soft)}
.bkhead b{display:block;font-size:15px;color:var(--ink);margin-bottom:3px}
.bkhead span{display:block;font-size:12.5px;color:var(--muted);line-height:1.45;max-width:80ch}
.bkhead i{font-style:normal;font-family:var(--mono);color:var(--accent);font-weight:600}
.picks{display:flex;flex-wrap:wrap;gap:7px;margin:11px 0}
.qp{font-size:12.5px;padding:7px 12px;min-height:0;background:var(--card);border:1px solid var(--line);color:var(--ink)}
.qp:hover{border-color:var(--accent);color:var(--accent);background:var(--card)}
.qp.ghost{color:var(--muted)}
.bkbuy{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:10px 0 8px}
.bkbuy label{font-family:var(--mono);font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
.bkbuy input{width:130px}
#bksum{margin:6px 0}
#bkbreak .planbox{max-height:320px;overflow-y:auto}
/* the pick control in each row */
svg.spark{display:block;width:64px;height:20px;margin-top:2px;margin-left:auto;opacity:.85}
td.cPx{white-space:nowrap}
.pick{font-family:var(--mono);font-size:15px;font-weight:600;line-height:1;width:30px;height:30px;
 min-height:0;padding:0;border:1px solid var(--line);background:var(--bg);color:var(--muted)}
.pick:hover{border-color:var(--accent);color:var(--accent);background:var(--bg)}
.pick.on{background:var(--accent);border-color:var(--accent);color:var(--ground)}
.pick:disabled{opacity:.3;cursor:not-allowed}
tr.picked td{background:var(--accent-soft)}
/* The add control sits against the table, because "add a row" has to look like
   something the table does, not like a search box parked in the prose. */
.addbar{border:1px solid var(--accent);border-radius:7px;padding:13px 15px;margin:4px 0 10px;
 background:var(--accent-soft)}
.addbar label{display:block;margin-bottom:9px}
.addbar label b{display:block;font-size:14px;color:var(--ink);margin-bottom:3px}
.addbar label span{display:block;font-size:12.5px;color:var(--muted);line-height:1.45;max-width:78ch}
.addctl{display:flex;gap:8px;flex-wrap:wrap}
.addctl input{flex:1 1 260px;min-width:0}
#qres:not(:empty){margin-top:12px}
.rm{background:none;border:1px solid var(--line);color:var(--muted)}
.rm:hover{border-color:var(--bad);color:var(--bad);background:none}
.tiersum{display:flex;flex-wrap:wrap;gap:7px;margin:11px 0 4px}
.tierchip{display:flex;align-items:baseline;gap:6px;padding:5px 10px;border:1px solid var(--line);
 border-radius:5px;background:var(--bg);font-family:var(--mono);font-size:11.5px}
.tierchip b{font-size:15px;color:var(--ink);font-variant-numeric:tabular-nums}
.tierchip span{color:var(--muted)}
.addline{font-size:12.5px;color:var(--muted)}
.addline.ok{color:var(--accent)}
.addline.warn{color:var(--warn)}
#mktnote{margin:2px 0 8px;font-size:12px}

/* Mobile: the market table becomes one card per company.
   The earlier version stacked all twelve cells as labelled rows, which made every
   card about 650px tall, three of those rows being placeholder dashes for holdings
   you do not have. Fifty-three of those is an unusable scroll. This packs the same
   information into a five-row grid and drops the empty holdings entirely.
   Scoped to .mktwrap so the history and transaction tables keep scrolling. */
@media(max-width:760px){
  .tablewrap.mktwrap{overflow-x:visible}
  table.mkt{min-width:0;display:block}
  table.mkt tbody{display:block}
  table.mkt thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
  table.mkt tr{
    display:grid;
    grid-template-columns:auto 1fr auto auto;
    grid-template-areas:
      "tier tk  sc  px"
      "co   co  co  co"
      "ind  ind ind ind"
      "rm   rm  rm  rm";
    gap:3px 8px;align-items:center;
    border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin:0 0 8px;
    background:var(--card)}
  /* labels are for the wide table; the phone card is legible without them */
  table.mkt td::before{content:none}
  table.mkt td{display:flex;align-items:baseline;gap:6px;border:0;padding:0;font-size:13px;min-width:0}
  table.mkt td.tierpill{grid-area:tier;font-size:10px}
  table.mkt td.tk{grid-area:tk;font-size:15px;font-weight:600}
  table.mkt td[data-l="Score"]{grid-area:sc;font-family:var(--mono);font-size:15px;font-weight:600}
  table.mkt td[data-l="Score"]::after{content:"/100";font-size:9.5px;color:var(--muted);font-weight:400}
  table.mkt td[data-l="Price"]{grid-area:px;font-family:var(--mono);font-size:14px;
    flex-direction:column;align-items:flex-end;gap:0}
  table.mkt svg.spark{width:56px;height:17px}
  table.mkt td.co{grid-area:co;flex-direction:column;align-items:stretch;margin:2px 0 1px}
  table.mkt td.co .cn{white-space:normal;font-size:13.5px}
  table.mkt td.co .blurb{font-size:12px}
  table.mkt td.nm{grid-area:ind;font-size:11px;white-space:normal;margin-bottom:3px}
  table.mkt td.flat{display:none}
  table.mkt td.cRow{grid-area:rm}
  /* 44px is the smallest comfortable touch target. */
  table.mkt td.cRow button{min-width:76px;min-height:44px;padding:9px 12px;font-size:13.5px}
  table.mkt tr.ownrow td{background:none}
  .controls{gap:9px 12px}
  .controls select,.controls input[type=text]{max-width:100%}
  .qp{min-height:40px;font-size:13px;padding:8px 13px}
  .bkbuy input{flex:1 1 120px;width:auto}
  #basketbuy{flex:1 1 100%}
}
/* History and transaction tables stay tabular but get compact enough to fit. */
@media(max-width:760px){
  .tablewrap:not(.mktwrap) table{font-size:11.5px}
  .tablewrap:not(.mktwrap) th{padding:5px 4px;font-size:8.5px;letter-spacing:.04em}
  .tablewrap:not(.mktwrap) td{padding:5px 4px}
}
@media(max-width:760px){
  section{padding:22px 0}
  nav{gap:0;padding:6px 0}
  nav a{padding:6px 7px;font-size:10px}
  nav .money{width:100%;margin:4px 0 0;text-align:right}
  .runbox{padding:13px 14px}
  input,select,button{font-size:16px}
}
.msg{font-family:var(--mono);font-size:12.5px;color:var(--warn);min-height:17px;margin:5px 0}
.imbhead{font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:16px 0 6px}
.imbrow{display:flex;width:100%;text-align:left;align-items:center;gap:10px;padding:10px 12px;min-height:44px;
  border:1px solid var(--line);border-radius:7px;background:var(--card);margin:0 0 6px;cursor:pointer;font-size:13.5px;color:var(--ink)}
.imbrow .sev{font-family:var(--mono);font-weight:600;min-width:30px;text-align:right}
.imbrow .sevbar{height:4px;background:var(--chipbg);border-radius:2px;flex:0 0 56px;overflow:hidden}
.imbrow .sevbar i{display:block;height:100%;background:var(--warn)}
.imbrow .nm2{font-weight:600;flex:1 1 auto;min-width:0}
.imbrow .frm{font-family:var(--mono);font-size:10px;text-transform:uppercase;letter-spacing:.05em;
  padding:3px 7px;border-radius:4px;white-space:nowrap}
.frm-overshoot{background:var(--warn-soft);color:var(--warn)}
.frm-deficit{background:var(--accent-soft);color:var(--accent)}
.frm-both{background:var(--chipbg);color:var(--muted)}
.imbrow .mv{font-family:var(--mono);font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.imbrow .nco{font-family:var(--mono);font-size:10.5px;color:var(--muted)}
.imbx{border:1px solid var(--line);border-top:0;border-radius:0 0 7px 7px;margin:-7px 0 8px;padding:6px 14px 12px;background:var(--card);font-size:13px}
.imbx dl{margin:0}
.imbx dt{font-family:var(--mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-top:9px}
.imbx dd{margin:2px 0 0}
.imbco{display:inline-block;margin:5px 6px 0 0;padding:7px 10px;min-height:34px;border:1px solid var(--line);
  border-radius:6px;background:var(--chipbg);font-family:var(--mono);font-size:12px;cursor:pointer;color:var(--ink)}
pre.hier{font-family:var(--mono);font-size:12px;line-height:1.75;overflow-x:auto;border:1px solid var(--line);
  border-radius:7px;padding:12px 16px;background:var(--card);margin:10px 0 16px}
.note{background:var(--warn-soft);border-left:3px solid var(--warn);padding:10px 14px;border-radius:0 5px 5px 0;margin:14px 0;max-width:84ch;font-size:12.5px;color:var(--ink)}
.pos{color:var(--good)} .neg{color:var(--bad)}
.money-line{font-family:var(--mono);font-size:12.5px;color:var(--muted);margin:6px 0;max-width:none}
.money-line b{color:var(--ink)}
.card2{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:13px 16px;margin:8px 0}
.card2 .h{font-family:var(--serif);font-size:17px;font-weight:600}
.card2 .sub{font-family:var(--mono);font-size:11.5px;color:var(--muted)}
.verdict{display:inline-block;font-family:var(--mono);font-size:11px;padding:2px 8px;border-radius:4px;margin:6px 0}
.v-in{background:var(--accent-soft);color:var(--accent)} .v-out{background:var(--chipbg);color:var(--muted)}
ul.rl{padding-left:20px;max-width:82ch}ul.rl li{margin-bottom:7px;font-size:14px;color:var(--muted)}
.runbox{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px 18px;margin:18px 0}
.runhead{font-family:var(--mono);font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--accent);margin-bottom:6px}
.runhead b{color:var(--ink)} .runhead span{color:var(--muted);text-transform:none;letter-spacing:0}
.runnote{font-size:12.5px;color:var(--muted);margin:6px 0;max-width:82ch}
.clocks{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px;margin:14px 0}
.ck{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:5px;padding:10px 13px}
.ck .t{display:block;font-family:var(--mono);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin-bottom:3px}
.ck .m{font-size:12.5px;color:var(--muted);line-height:1.45}
.ck .m b{color:var(--ink)}
.mcard{margin:10px 0 2px;padding:11px 13px;background:var(--bg);border:1px solid var(--line);border-radius:6px}
.mhead{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin-bottom:7px}
.mrow{display:grid;grid-template-columns:118px 1fr 46px;gap:9px;align-items:center;margin:3px 0}
.mrow .ml{font-size:11.5px;color:var(--muted)}
.mrow .mbar{height:7px;background:var(--line);border-radius:3px;overflow:hidden}
.mrow .mbar i{display:block;height:100%;background:var(--accent);border-radius:3px}
.mrow .mv{font-family:var(--mono);font-size:11.5px;text-align:right;font-variant-numeric:tabular-nums}
.mrow .mv .mo{color:var(--muted)}
.mlab{font-size:12px;color:var(--muted);line-height:1.45;margin-top:6px}
.mlab b{color:var(--ink);font-weight:600}
.gdot{display:inline-block;margin-left:4px;width:13px;height:13px;line-height:13px;text-align:center;
 border-radius:50%;background:#b4462a;color:#fff;font-size:9px;font-weight:700;vertical-align:middle;cursor:help}
.gatefail{display:inline-block;font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;
 text-transform:uppercase;color:#b4462a;border:1px solid #b4462a;border-radius:3px;padding:1px 6px;margin-left:6px}
@media(max-width:520px){.mrow{grid-template-columns:96px 1fr 42px}}
.fig{margin:20px 0;padding:0}
.fig svg{display:block;width:100%;max-width:720px;height:auto;margin:0 auto;color:var(--ink)}
.fig figcaption{font-size:12.5px;color:var(--muted);line-height:1.5;max-width:74ch;margin:10px auto 0;text-align:left}
.fig figcaption b{color:var(--accent);font-family:var(--mono);font-size:11.5px}
.dims{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:6px 18px;margin:14px 0}
.dim{display:flex;gap:10px;align-items:baseline;font-size:13.5px}
.dim .w{font-family:var(--mono);font-size:12px;color:var(--accent);font-weight:600;min-width:20px;text-align:right}
.dim .d{color:var(--muted)} .dim .d b{color:var(--ink)}
.funnel{display:flex;flex-direction:column;gap:5px;margin:14px 0;max-width:640px}
.frow{display:grid;grid-template-columns:150px 1fr 62px;gap:12px;align-items:center}
.frow .fl{font-family:var(--mono);font-size:11px;color:var(--muted);text-align:right}
.frow .fn{font-family:var(--mono);font-size:12px;font-variant-numeric:tabular-nums}
.fbar{height:14px;background:var(--accent);border-radius:2px;opacity:.9;min-width:3px}
@media(max-width:560px){.frow{grid-template-columns:104px 1fr 54px}}
.lb{display:flex;flex-direction:column;gap:6px;margin:12px 0}
.lbrow{display:flex;gap:12px;align-items:baseline;padding:8px 12px;border:1px solid var(--line);border-radius:6px;background:var(--card);font-family:var(--mono);font-size:13px}
.lbrow .rank{color:var(--accent);font-weight:600;width:20px}
.lbrow .who{flex:1;color:var(--ink)}
.lbrow.me{border-color:var(--accent)}
.lbrow.bot{border-style:dashed}
.lbx{background:none;border:0;color:var(--muted);font-size:16px;line-height:1;padding:0 0 0 10px;cursor:pointer;min-height:0}
.lbx:hover{color:var(--bad);background:none}
.botpill{font-family:var(--mono);font-size:9.5px;letter-spacing:.06em;text-transform:uppercase;background:var(--chipbg);color:var(--muted);padding:1px 6px;border-radius:3px;margin-left:6px}
footer{margin-top:30px;padding-top:14px;border-top:2px solid var(--ink);color:var(--muted);font-size:12px;max-width:84ch}
</style>
<div class="wrap">
<nav>
  <a href="#list" class="tab" data-view="list">About</a>
  <a href="#trade" class="tab" data-view="trade">Buy &amp; sell</a>
  <a href="#me" class="tab" data-view="me">My portfolio</a>
  <span class="money" id="navmoney"></span>
</nav>

<div class="view" id="v-list">
<section class="hero" id="what">
  <p class="step">What this is</p>
  <h1>An engine that measures where civilization is furthest from balance, which way each system must move to correct, and which public companies accelerate that correction.</h1>
  <p class="lede">It is not looking for good companies; there is no such measurement. It starts one level above companies, with the species itself, and only reaches the ranked table at the end of a chain that begins with the planet.</p>
</section>

<section id="observer">
  <p class="step">Step 0 &middot; The diagnosis</p>
  <h2>Imagine a scientist discovering Homo sapiens for the first time</h2>
  <p>A scientist walks into a rainforest and finds a species never described before. The scientist does not know its currencies, its political parties, its stock markets or its industries, and does not ask about them. They measure what ecology measures for any organism: population, energy use, resource flows, waste streams, habitat modification, cooperation, competition, and the feedback loops created by its tools. Then they ask the question ecology always asks: <b>is this species moving toward a relationship with its environment that can persist?</b></p>
  <p>Seen from outside, Homo sapiens consumes energy and matter, occupies habitat, moves resources, produces waste, modifies its niche, reproduces, cooperates, competes, builds networks, stores information, and grows external organs in the form of tools and technology. Civilization is a metabolism. Money is not the underlying system; it is an information layer the species built to coordinate access to energy, matter, labour, land and time. Technology has let the species push many natural feedbacks further away in time. That does not eliminate the feedback. It accumulates it.</p>
  <p>So the first question this engine asks has nothing to do with companies: <b>where is the metabolism of Homo sapiens furthest from a stable regenerative state?</b></p>
  <p>Balance is not a fixed point, because nothing in nature holds still. Wolves multiply until they outrun the deer; the crash feeds the deer's recovery, and the deer's recovery feeds the wolves'. Tree stocks grow, burn, die and regrow. Every living system breathes like this, and the ebb and flow is not imbalance; it is what balance actually looks like. So this map never scores movement as getting better or worse. A <b>safe range</b> here means the envelope a stock's own oscillations have stayed inside for as long as the record runs. A stock inside its envelope is in rhythm, however fast it is moving. Imbalance is something narrower and checkable: <b>the stock has left its envelope, or is leaving it at a speed the envelope never contained.</b> Atmospheric CO2 breathed between 180 and 300 parts per million through every glacial cycle of the last 800,000 years; it now stands near 425 and is moving roughly a hundred times faster than any swing in that record. That is not the planet's rhythm. That is a wolf population still climbing, and the correction arrives either as a managed return or as the die-off arm of the loop.</p>
  <p>A stock can leave its envelope because the species takes too much of something, produces too much of something, regenerates too little of it, or because an essential need stays undersupplied while plenty is consumed getting it wrong. That gives the only two labels the map uses, and every row carries one:</p>
  <div class="dims">
    <div class="dim"><span class="w">&#8599;</span><span class="d"><b>Ecological overshoot.</b> Human throughput exceeds the regenerative or assimilative capacity of the surrounding system.</span></div>
    <div class="dim"><span class="w">&#8601;</span><span class="d"><b>Provisioning deficit.</b> The system fails to provide an essential human need adequately despite consuming substantial resources.</span></div>
  </div>
  <p>The future lies where both shrink at once: <b>more human need satisfied with less energy, material extraction, waste, scarcity and ecological disruption.</b> That is the bridge between biomimicry and a resource-based economy, and nothing on this page treats it as guaranteed.</p>
  <p>Wherever science provides a quantitative control variable, the map uses it instead of opinion. Seven of nine planetary-boundary processes currently sit outside their safe operating space. Extinctions run above 100 per million species-years against a boundary below 10. Human appropriation of net primary production is roughly 30 percent against a boundary near 10. Those are exactly the numbers an ecologist observing Homo sapiens from outside the species would write down.</p>

  <h3>Where civilization is furthest from balance</h3>
  <p>Each row is a civilization-scale stock. Severity is its distance from equilibrium: distance from the safe range x load-bearing importance x rate of divergence x scale of exposure x irreversibility, on a 0 to 100 scale. Open any row for the full chain: state, movement relative to the safe range, the natural rhythm where a record exists, the physical flows causing the excursion, the required correction, the clock that correction runs on, and the public companies in this universe attached to it. The imbalance is established first and exists whether or not any company serves it; a correction with no company yet is listed as exactly that.</p>
  <div id="imbmap"></div>
  <p class="legend">Severity reads distance from equilibrium, not moral urgency and not a prediction. Stratospheric ozone stays on the map at zero as the one completed return: a stock that left its envelope and was brought back inside it. Definitions, anchors and sources live in the engine repository, and the map is re-researched, not assumed.</p>

  <p style="margin-top:18px">The whole engine runs on one ordering, and the ordering is the discipline: nothing to the right is examined until everything to its left is established. This is what keeps it from discovering an attractive company first and rationalizing why it matters afterward. The imbalance must exist independently of the company.</p>
  <pre class="hier">PLANET / CIVILIZATION
  &rarr; IMBALANCE
    &rarr; STOCK
      &rarr; PHYSICAL FLOW CAUSING THE IMBALANCE
        &rarr; REQUIRED CORRECTION
          &rarr; COMPANY / TECHNOLOGY
            &rarr; MEASURED CORRECTION PER DOLLAR OF REVENUE
              &rarr; SELF-DAMPING OR SELF-AMPLIFYING LOOP
                &rarr; SURVIVABILITY
                  &rarr; INVESTMENT</pre>

  <h3>The convergence hypothesis, stated so it can fail</h3>
  <p>Underneath the map sits one falsifiable question, and this site is an instrument for testing it: <b>as technological capability increases, does civilization systematically move toward greater abundance of essential outcomes while requiring less scarce material, energy and human labour per outcome?</b></p>
  <p>The mechanisms that would drive it are each measurable on their own curve. AI lowers the cost of intelligence and coordination. Automation lowers the labour required per unit of production. Renewable and advanced energy systems lower the resource cost of usable energy. Precision agriculture and biological systems lower inputs per unit of nutrition. Closed-loop manufacturing lowers virgin material demand. Distributed production lowers transportation and coordination requirements. Preventive and regenerative medicine lowers the resources required to maintain health. If these converge, economic organization can shift from maximizing resource throughput toward maximizing useful human outcomes per unit of physical resource consumed.</p>
  <p>If the hypothesis is right, companies that make essential outcomes cheaper, more abundant, regenerative, distributed and resource-efficient should progressively capture larger physical and economic flows, and the tracked record on this site should show it. If it is wrong, the same record should eventually demonstrate that too. Either answer is the experiment working.</p>
  <div class="note"><b>The governing rule for everything here:</b> do not predict the future by extrapolating markets. Measure the imbalance. Determine the direction the physical system must move to resolve it. Measure the clock. Then find the mechanisms carrying civilization in that direction. The crystal ball is not a prediction. The crystal ball is the distance from equilibrium.</div>
</section>

<section id="why">
  <p class="step">Step 1 · The idea</p>
  <h2>Balance is a physical property, not a virtue</h2>
  <p>Nothing in nature is good or bad. Systems are simply in balance or out of it, and everything inside them is constantly pushed back toward equilibrium. Waste gets consumed by something. Concentration gets dispersed. An organism that spends more energy than it captures dies, and a population that outruns its food supply corrects. Nothing is exempt and nothing is forgiven; imbalance is a debt that always comes due, and the only variable is when.</p>
  <p>A living system has no opinion about its parts. An organ that moves resources efficiently, wastes little and costs the body less persists; one that consumes more than it returns is carried for a while and then shed. Not because it was wicked, but because the arithmetic of energy and materials caught up with it. Every ecosystem, every watershed, every body runs on that same self-correction.</p>
  <p>Economies are not outside this, because they are made of energy, materials, labour and time. When a company defers its real costs onto a water table, a health system, a supply chain, or a customer who cannot afford the alternative, the cost does not vanish. It accumulates somewhere in the system as an imbalance, and imbalances get corrected: by regulation, by substitution, by exhaustion of the thing being drawn down, or by collapse. Reading a business through that lens is not idealism, it is accounting over a longer horizon than a quarter.</p>
  <p>So the scorecard is not a morality test and it does not ask what a company deserves. It asks a mechanical question: does this business help its system settle, by closing loops, cutting the energy and cost per useful outcome, spreading capacity instead of concentrating it, and repairing instead of depleting? Or does it work against that settling, and therefore hold a debt the system will eventually collect?</p>
  <p>Answering that mechanically means being precise about what is actually out of balance. It is never the company. It is some quantity that accumulates: water in an aquifer, homes in a city, safe units in a blood supply, carbon in a soil, spare capacity on a grid. Those quantities are the things that can be drained or overfilled, and a company is only ever a mechanism attached to the flow running into or out of one of them. Step 2 turns that into the six measures that produce the score.</p>
  <p>Some business models are disqualified outright, however profitable they look right now: weapons, addiction, artificial scarcity, planned obsolescence, and revenue that depends on people staying sick or water staying scarce. Not because they are evil, but because each one earns by <i>holding a system out of balance on purpose</i>. That is a position with a bill attached, and the bill is what eventually arrives. <a href="#rules" style="color:var(--accent)">The full rules are at the bottom.</a></p>
  <div class="note"><b>The important catch:</b> being aligned with balance tells you which way a system will push over decades. It does not tell you that this particular company will still be standing to capture it, since plenty of well-aligned businesses run out of cash first. That question is kept completely separate from the score. It is checked first, as a pass or fail, and a company that fails it is set aside no matter how well it scores. Two companies on this list did.</div>

  <h3>Direction is only half of it. The clock is the other half.</h3>
  <p>Balance says which way a system is pushing. It says nothing about when the push arrives, and that timing is not set by you. It is set by whatever mechanism does the correcting, and those mechanisms run on wildly different clocks.</p>
  <p>A system can sit out of balance for what a person experiences as an entire investing life while barely registering on the clock of the thing that will eventually correct it. An aquifer being drawn down faster than it recharges is in obvious imbalance, and it can stay that way for eighty years. A soil losing carbon corrects over centuries. To a forest that is a moment; to a solar system it is nothing at all; to someone holding a stock it is longer than they will hold anything. Being right about the imbalance and wrong about the clock is indistinguishable from being wrong.</p>
  <div class="clocks">
    <div class="ck"><span class="t">Months to a few years</span><span class="m">Substitution when a cheaper option already exists. Reimbursement and pricing decisions. Anything where a buyer can simply switch. <b>Fast enough to trade.</b></span></div>
    <div class="ck"><span class="t">Years to a decade</span><span class="m">Regulation, litigation, standards changes, technology displacing an incumbent. <b>The zone this list mostly lives in.</b></span></div>
    <div class="ck"><span class="t">Decades</span><span class="m">Infrastructure replacement cycles, demographic shifts, resource depletion becoming expensive rather than merely visible. <b>Longer than most holding periods.</b></span></div>
    <div class="ck"><span class="t">Centuries and beyond</span><span class="m">Soil, aquifers, oceans, climate. Real, measurable, and almost never the reason a stock moves in your lifetime. <b>Not an investment clock.</b></span></div>
  </div>
  <p>This is why the scorecard does not stop at whether a company points the right way. A whole measure exists purely to ask about the clock: how fast this particular correction moves, and whether it is visibly moving <i>now</i>, in real orders and approvals and adoption inside the last four quarters. A company aligned with a centuries-long correction and no near-term momentum scores near zero there, by design.</p>
  <p>The same caution runs the other way, and it is the honest limit of this whole approach: a business earning from an imbalance on a slow clock can pay you well for decades. Nothing in this framework claims otherwise. What it claims is narrower, and worth stating plainly: <b>when a correction does arrive, it lands on the businesses that were holding the system out of balance, and the ones helping it settle absorb the demand that gets released.</b> Which clock you are betting on is a decision you make, not one the algorithm makes for you.</p>
</section>

<section id="how">
  <p class="step">Step 2 · How it was judged</p>
  <h2>Turning that idea into something that can actually grade a company</h2>
  <p>A principle you cannot apply is just an opinion. So the question from Step 1 had to become something checkable. The move that makes it checkable is to stop scoring <i>companies</i> and start scoring what a company does to a <b>stock</b>.</p>
  <p>A stock is anything that accumulates and can run out or pile up: water in an aquifer, homes in a city, safe blood in a supply, topsoil on a field, working capacity on a grid, plastic in circulation. Stocks change through <b>flows</b>, the rates going in and out. Balance is not a mood or a virtue. It is a stock whose inflow and outflow match. Every company is a mechanism attached to one of those flows, and that is the thing the engine measures.</p>

  <figure class="fig">
    <svg viewBox="0 0 720 258" role="img" aria-label="A stock accumulates between an inflow and an outflow. A company sits on one flow as a valve. A feedback line runs from the stock level back to the company, which is the loop the scorecard measures." xmlns="http://www.w3.org/2000/svg">
      <defs>
        <marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="currentColor"/>
        </marker>
        <marker id="arA" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="var(--accent)"/>
        </marker>
      </defs>
      <g fill="none" stroke="currentColor" stroke-width="1.6">
        <line x1="24" y1="96" x2="238" y2="96" marker-end="url(#ar)"/>
        <line x1="416" y1="96" x2="536" y2="96" marker-end="url(#ar)"/>
        <line x1="664" y1="96" x2="704" y2="96" marker-end="url(#ar)"/>
        <rect x="242" y="58" width="172" height="76" rx="4"/>
      </g>
      <rect x="538" y="70" width="124" height="52" rx="4" fill="none" stroke="var(--accent)" stroke-width="1.8"/>
      <path d="M328,136 L328,196 L600,196 L600,124" fill="none" stroke="var(--accent)" stroke-width="1.5"
            stroke-dasharray="5 4" marker-end="url(#arA)"/>
      <g font-family="ui-monospace,SFMono-Regular,Menlo,monospace" font-size="10.5" fill="var(--accent)"
         letter-spacing="1" text-anchor="middle">
        <text x="328" y="50">A</text><text x="131" y="82">B</text><text x="464" y="212">C</text>
      </g>
      <g font-size="12.5" fill="currentColor" text-anchor="middle">
        <text x="328" y="92" font-size="13.5" font-weight="600">THE STOCK</text>
        <text x="328" y="112" opacity="0.72">what accumulates</text>
        <text x="600" y="92" font-size="12.5" font-weight="600">THE COMPANY</text>
        <text x="600" y="110" opacity="0.72" font-size="11.5">a valve on one flow</text>
      </g>
      <g font-size="11.5" fill="currentColor" opacity="0.72">
        <text x="131" y="115" text-anchor="middle">inflow</text>
        <text x="476" y="86" text-anchor="middle">outflow</text>
        <text x="464" y="228" text-anchor="middle">the loop: does succeeding change the need?</text>
      </g>
    </svg>
    <figcaption>The whole scorecard is three questions about this picture. <b>A</b>: which stock, and is it outside its safe range? <b>B</b>: which way does this company push the flow, and how hard per dollar of revenue? <b>C</b>: what comes back down the dashed line when it succeeds?</figcaption>
  </figure>

  <p>That picture is the scorecard. Six measures, 100 points, the same six for every company. The weights are the argument: two thirds of the score is the stock, the flow, and the loop, because those are the only three things that decide whether a business is helping a system settle or holding it open.</p>
  <div class="dims">
    <div class="dim"><span class="w">20</span><span class="d"><b>The stock.</b> Name the accumulation it touches. Is it load-bearing, and is it outside its safe range right now?</span></div>
    <div class="dim"><span class="w">25</span><span class="d"><b>The flow.</b> Which direction, and how much correction per dollar of revenue. Needs a measured before and after, not a claim</span></div>
    <div class="dim"><span class="w">20</span><span class="d"><b>The loop.</b> Does succeeding destroy its own demand or manufacture more? And does the revenue survive if the system rebalances?</span></div>
    <div class="dim"><span class="w">15</span><span class="d"><b>Growth pattern.</b> Does it copy a proven unit the way cells divide, or swell? Can it stop growing and stay solvent?</span></div>
    <div class="dim"><span class="w">10</span><span class="d"><b>Buffer.</b> Efficiency that keeps slack, or efficiency bought by removing it. One plant and one customer is fragility, not thrift</span></div>
    <div class="dim"><span class="w">10</span><span class="d"><b>Clock.</b> The Step 1 question, scored. How fast does this correction land, and is it visibly moving in the last four quarters?</span></div>
  </div>
  <p>Two of those deserve a note, because they are what the earlier version of this engine got wrong.</p>
  <p><b>The loop is the half that gets missed.</b> It is easy to admire a business with a beautiful circular process and never ask what its inputs depend on. A company can run a genuinely closed loop <i>inside</i> a system that has to stay broken for the loop to have anything to feed on. Asking the question directly moved several highly ranked names a long way down, and it is the single biggest change in how this list is built.</p>
  <p><b>Being hard to replace is not automatically a credit.</b> If a company is hard to displace because it does the job better, that shows up as durability. If it is hard to displace because it sits on a chokepoint and charges for the privilege, that is a deduction, because it is holding the stock hostage. The test is whether the company uses its position to restrict the very flow it is supposed to be correcting.</p>
  <p>One thing is deliberately <b>not</b> scored. Whether a company can survive long enough to matter is a <b>gate</b>, checked before anything else: under a year of cash with no financing lined up, more than a quarter of the company issued as new shares in three years, a pending buyout, or an auditor doubting it can continue. Fail any of those and it is set aside regardless of score, because a high score on a company that runs out of money is not a smaller success, it is not a result at all. That is a statement about the balance sheet, not about the business.</p>
  <p>Then that scorecard was run as a tournament: six rounds, each one harder than the last, every elimination written down with its reason. Scores are not opinions held privately; every survivor and every rejection is recorded and searchable in the next two steps.</p>

  <div class="runbox">
    <div class="runhead">Latest run <b>@@STAMP@@</b> <span>(prices at market close @@ASOF@@)</span></div>
    <p class="runnote">These counts are the output of that run, not fixed facts. They change every time the engine runs, which is every week.</p>
    <div class="funnel">
      <div class="frow"><span class="fl">Companies entered</span><div class="fbar" style="width:100%"></div><span class="fn">@@UNIV@@</span></div>
      <div class="frow"><span class="fl">Round 1 · the screen</span><div class="fbar" style="width:44%"></div><span class="fn">3,055</span></div>
      <div class="frow"><span class="fl">Round 2 · what it sells</span><div class="fbar" style="width:24%"></div><span class="fn">935</span></div>
      <div class="frow"><span class="fl">Round 3 · the finances</span><div class="fbar" style="width:9%"></div><span class="fn">104</span></div>
      <div class="frow"><span class="fl">Round 4 · deep research</span><div class="fbar" style="width:6%"></div><span class="fn">54</span></div>
      <div class="frow"><span class="fl">Left standing</span><div class="fbar" style="width:4%"></div><span class="fn">@@RANKED@@</span></div>
    </div>
    <p class="runnote">The universe is every company an American investor can actually buy: every listing on the NYSE, NASDAQ and NYSE American, plus every SEC-registered filer, plus every foreign company reachable through a US over-the-counter listing or ADR. W&auml;rtsil&auml; of Finland, Coloplast of Denmark and Tomra of Norway all entered that way. It is not every listed company on earth; roughly 60,000 exist across all the world's exchanges, and most trade only in their home market where a US investor cannot reach them without a specialist broker.</p>
  </div>

  <p>A score of <b>81</b> means a company earned 81 of those 100 points on the six measures above. The scale is demanding on purpose, and 80 is a high bar rather than a common one. Companies are then grouped into <b>tiers</b> by score, T1 at 80 and above down to T4 at 65, with anything below 65 marked for exit review. The tier is shorthand for how much weight a company might reasonably carry, not a prediction about its share price.</p>
  <p class="runnote">These bands were left exactly where they were when the scorecard was rebuilt, even though the rebuild moved almost every score down. Sliding the bands down to keep the same number of companies in the top tier would have reproduced the old answer by arithmetic and told you nothing. If fewer companies clear the bar, fewer companies clear the bar.</p>
  <p style="font-size:13px">Want the exact rules, the disqualifiers, and every judgment call that shaped the list? <a href="#rules" style="color:var(--accent)">The full reference is at the bottom.</a></p>
</section>

<section id="list">
  <p class="step">Step 3 · The list, and testing it</p>
  <h2>Results summary</h2>
  <p>Everything in the universe was scored. This is what came through all six rounds. Most companies were cut early for breaking a hard rule, being too small or inactive to grade, or not serving a need that lasts.</p>

  <div class="runbox">
    <div class="runhead">Last engine run <b>@@STAMP@@</b> <span>(prices at market close @@ASOF@@)</span></div>
    <p class="runnote"><b>@@RANKED@@</b> companies came through, out of <b>@@UNIV@@</b> that entered. Every number here changes when the engine runs again, which is every week.</p>
    <div class="tiersum">@@TIERSUM@@</div>
    <p class="runnote">Two companies are set aside by the survivability gate whatever they scored, because a company that runs out of money did not score badly, it produced no result. Research output, not investment advice.</p>
  </div>

  <p><b>You do not have to take any of it on faith, and you should not.</b> If you are sceptical about a ranking built on somebody else's rules, that is the correct instinct. The prices here are real and update every week, so over time you can find out whether the ranking was right, whether your own picks beat it, and whether either beat simply owning the whole market.</p>

  <h2 style="margin-top:30px">Results</h2>
  <p style="font-size:13.5px">Each row says what the company does in plain words, what it scored out of 100, and which need it serves. Tap or hover any row for the reasoning behind it.</p>
  <div class="controls">
    <label for="mktsel">Where it trades:</label><select id="mktsel">
      <option value="all" selected>anywhere</option>
      <option value="us">US exchanges (NYSE, NASDAQ)</option>
      <option value="adr">ADRs, over the counter</option>
      <option value="ord">foreign ordinary shares, over the counter</option>
    </select>
    <label for="capsel">Price under:</label><select id="capsel"><option value="10">$10</option><option value="20">$20</option><option value="30">$30</option><option value="50">$50</option><option value="99999" selected>any price</option></select>
    <label for="scorepol">Score at least:</label><select id="scorepol"><option value="0" selected>any</option><option value="70">70</option><option value="75">75</option><option value="80">80</option><option value="85">85</option></select>
    <label for="sortsel">Sort by:</label><select id="sortsel"><option value="score" selected>rank (score)</option><option value="tier">tier</option><option value="price">price, low to high</option><option value="industry">industry</option></select>
  </div>
  <p class="money-line" id="mktnote">Most mainstream investing apps carry US exchange listings. Some carry ADRs. Foreign ordinary shares usually need a full-service broker. That is about access, not quality, and it never affects a score.</p>

  <div class="tablewrap mktwrap"><table class="mkt">
  <thead><tr>
  <th title="T1 = 80 and above. T2 = 74 to 79. T3 = 69 to 73. T4 = 65 to 68. EXIT = below 65, on the record for review. YOURS = a company you added.">Tier</th>
  <th title="The company's short code on the exchange">Ticker</th>
  <th>Company · what it actually does</th>
  <th style="text-align:right" title="How well it fits the rules, out of 100">Score</th>
  <th title="Which human need it serves">Industry</th>
  <th style="text-align:right" title="What one share costs, and its shape over the past year">Price</th>
  <th></th></tr></thead>
  <tbody id="mktbody"></tbody></table></div>
  <div id="emptymsg" style="display:none;color:var(--muted);font-style:italic;padding:14px">Nothing matches those filters. Loosen one.</div>

  <div class="addbar">
    <label for="q"><b>Add any company to this table</b><span>Not just the ones that survived. Every company that entered is here, and it arrives with what the engine found on it: how far it got, what it scored, and why it was cut. Yours are marked <b>YOURS</b> and can be removed again any time.</span></label>
    <div class="addctl">
      <input type="text" id="q" placeholder="ticker or company name, e.g. TSLA" autocomplete="off">
      <button id="qbtn">Add row</button>
    </div>
    <div id="qres"></div>
  </div>

  <p class="legend">Score = fit with the rules out of 100 · <span class="pb2">pb</span> makes healthcare cheaper or fairer · <span class="emb2">emb</span> earns through insurance-paid prices. Both tags are already priced into the score; they are shown so you can see why a score landed where it did.</p>
</section>

<section id="rules">
  <p class="step">Reference · Full rules</p>
  <h2>How the grading works, in full</h2>
  @@RULES@@
</section>
</div><!-- /v-list -->

<div class="view" id="v-trade">
<section>
  <p class="step">Buy and sell</p>
  <h2>Build your portfolio</h2>
  <p>Pick companies on <a href="#list" class="tab" data-view="list">the list</a> with the <i class="plusref">+</i> button, or start from one of these. Then choose one amount and it splits across everything you picked, so you decide once instead of guessing a figure for every company.</p>
  <div class="panel" id="moneybar2"><div id="moneybartext2" class="money-line"></div></div>

  <div class="basket">
    <div class="bkhead"><b>Start from</b><span>Any of these replaces what you have picked. You can then add or drop individual companies from the list.</span></div>
    <div class="picks">
      <button class="qp" data-qp="all">The whole list</button>
      <button class="qp" data-qp="top10">Top 10 by score</button>
      <button class="qp" data-qp="need">One of each need</button>
      <button class="qp" data-qp="cheap">Under $10 a share</button>
      <button class="qp" data-qp="mirror">Copy the list's own portfolio</button>
      <button class="qp ghost" data-qp="none">Clear</button>
    </div>
    <div class="bkbuy">
      <label for="spend">Spend</label>
      <input type="number" id="spend" min="1" step="50" placeholder="dollars">
      <button class="ghost" id="spendall">All my cash</button>
      <button class="big" id="basketbuy">Buy</button>
    </div>
    <div class="money-line" id="bksum"></div>
    <div id="bkbreak"></div>
    <div class="msg" id="bkmsg"></div>
  </div>

  <h3 style="margin-top:30px">What you hold</h3>
  <p style="font-size:13.5px">Selling turns shares back into cash, which is the only way to free up more to spend.</p>
  <div id="sellbox"></div>
  <div class="msg" id="buymsg"></div>

  <div class="controls">
    <label for="ledgersel">Viewing:</label><select id="ledgersel"><option value="mine">My simulation</option><option value="house">The list's own $5,000</option></select>
    <label for="whoname">Your name:</label><input type="text" id="whoname" placeholder="optional" style="width:130px">
    <span class="money-line" id="tradermsg"></span>
  </div>
</section>
</div><!-- /v-trade -->

<div class="view" id="v-me">
<section id="track">
  <p class="step">My portfolio</p>
  <h2>Come back over time</h2>
  <p>Every number here is a real market movement. Prices refresh every week and a snapshot of your total gets added to this table, so the gains and losses you see are exactly what would have happened to real money invested the same way on the same day.</p>
  <p>The table below puts three things side by side over the same stretch: <b>you</b>, <b>the list</b> held in equal amounts, and <b>the S&amp;P 500</b>, which is what buying the whole market and not thinking about it gets you. That is the whole experiment. If the ranking is worth anything it should show up here, and if it is not, that will show up here too. Either answer is useful, and neither one costs you money to find out.</p>
  <div id="chart"></div>
  <div class="tablewrap"><table>
  <thead><tr><th>Date</th><th style="text-align:right">Your total</th><th style="text-align:right">Change $</th><th style="text-align:right">You, %</th><th style="text-align:right" title="Every ranked company that clears the gate, equal weight, over the same stretch">The list, %</th><th style="text-align:right" title="Buying the whole market and not thinking about it">S&amp;P 500, %</th></tr></thead>
  <tbody id="histbody"></tbody></table></div>
  <p class="legend">"The list" is every ranked company that clears the survivability gate, held in equal amounts, measured over the same stretch as your own picks. It starts the first time you take a snapshot and is never backfilled, because a list built with knowledge of the past would flatter itself.</p>
  <h3>Everything you have done</h3>
  <div class="tablewrap"><table>
  <thead><tr><th>Date</th><th>Who</th><th>Action</th><th>Ticker</th><th style="text-align:right">Shares</th><th style="text-align:right">Price</th><th style="text-align:right">Amount</th></tr></thead>
  <tbody id="txnbody"></tbody></table></div>
</section>

<section id="compare" style="border-bottom:none;padding-top:0">
  <h3 style="font-size:20px;margin-top:26px">Leaderboard</h3>
  <p><b>The list</b> is in here as a player, holding its own $5,000 in exactly what the engine says: gate-passing companies only, 60 percent across Tier 1, 28 across Tier 2, 12 across Tier 3, nothing in Tier 4 or exit review, rebalanced every week when prices refresh. Beating it means your judgment beat the algorithm's. Switch the view selector above to <b>The list's own $5,000</b> to see every trade it has made.</p>
  <p>Everyone's simulation lives privately in their own browser, so there is no central scoreboard yet. Share your profile, paste in one you are sent, and the standing assembles on your screen.</p>
  <div class="panel">
    <button id="copycard">Share my profile</button>
    <span class="money-line" id="cardmsg"></span>
    <div style="margin-top:10px"><input type="text" id="friendcode" placeholder="paste a profile someone shared with you" style="width:min(420px,100%)"> <button class="ghost" id="addfriend">Add</button> <button class="ghost" id="clearfriends">Remove everyone</button></div>
    <div class="lb" id="leaderboard"></div>
    <p class="legend" style="margin-top:10px">The list's portfolio as of @@HOUSESTAMP@@: @@HOUSENOTE@@</p>
  </div>
</section>
</div><!-- /v-me -->

<div id="modal" class="modal" hidden>
  <div class="modalbg" data-close="1"></div>
  <div class="modalcard" role="dialog" aria-modal="true" aria-labelledby="modaltitle">
    <button class="modalx" data-close="1" aria-label="Close">&times;</button>
    <div id="modalbody"></div>
  </div>
</div>

<footer>Balanced Systems Console · @@RANKED@@ graded companies from a @@UNIV@@-company US-investable screen (counts as of the run stamped above) (US exchanges + SEC filers + OTC/ADR lines; not all ~60,000 companies listed worldwide) · real companies at real market prices, invested with pretend money · prices refresh every week · your simulation is stored in your own browser and never sent anywhere · the list's own $5,000 is a tracked experiment held to the same rules · research output, not investment advice, and no one here is a licensed financial advisor.</footer>
</div>
<script>
const STATE=%%STATE%%;
const NAMES=@@NAMES@@;
const SIDX=window.__SIDX||{};
const PX=window.__PX||{};
const SPARK=window.__SPARK||{};
const IMB=@@IMBALANCE@@;
// A year of weekly closes as one small path. Green when the year is up, red when
// it is down, judged on the same series that is drawn, so the colour cannot
// disagree with the line.
function sparkline(tk){
  const d=SPARK[tk];
  if(!d||d.length<8)return '';
  const W=64,H=20,P=2;
  let lo=Math.min.apply(null,d),hi=Math.max.apply(null,d);
  if(hi-lo<1e-6){hi=lo+1e-6;}
  const pts=d.map(function(v,i){
    const x=P+(W-2*P)*(i/(d.length-1));
    const y=P+(H-2*P)*(1-(v-lo)/(hi-lo));
    return x.toFixed(1)+','+y.toFixed(1);}).join(' ');
  const up=d[d.length-1]>=d[0];
  const pct=Math.round(100*(d[d.length-1]/d[0]-1));
  return '<svg class="spark" viewBox="0 0 '+W+' '+H+'" role="img" aria-label="'+
    tk+' over the past year, '+(pct>=0?'up ':'down ')+Math.abs(pct)+' percent">'+
    '<polyline points="'+pts+'" fill="none" stroke="'+(up?'var(--good)':'var(--bad)')+
    '" stroke-width="1.4" stroke-linejoin="round" stroke-linecap="round"/></svg>';
}
// Benchmark levels stamped at the last engine run, so a visitor's own ledger can
// record a snapshot against the same yardsticks the house ledger uses.
const MARK=@@MARK@@;
const TODAY='@@TODAY@@';
const TPL_ENC='@@TPLENC@@';
const $=id=>document.getElementById(id);
const fmt=n=>'$'+n.toLocaleString(undefined,{maximumFractionDigits:2,minimumFractionDigits:2});
const F={tk:0,nm:1,sc:2,need:3,px:4,note:5,vt:6,sofi:7,tier:8,kid:9,dims:10,meta:11};
const MEA=[["The stock",20],["The flow",25],["Loop sign",12],["Coupling",8],
 ["Replication",6],["Contact inhibition",5],["Clean exit",4],["Buffer",10],
 ["Clock speed",6],["Moving now",4]];
function esc(s){return String(s).replace(/[&<>"]/g,function(c){
 return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function gateOf(n){return ((n&&n[F.meta])||[])[3]||'pass';}
function scorecard(n){
  const d=n[F.dims]||[],m=n[F.meta]||[];
  if(!d.length)return '';
  const rows=MEA.map(function(x,i){
    const v=d[i]||0,pc=Math.round(100*v/x[1]);
    return '<div class="mrow"><span class="ml">'+x[0]+'</span>'+
      '<span class="mbar"><i style="width:'+pc+'%"></i></span>'+
      '<span class="mv">'+v+'<span class="mo">/'+x[1]+'</span></span></div>';}).join('');
  const lab=function(t,v){return v?'<div class="mlab"><b>'+t+'</b> '+esc(String(v))+'</div>':'';};
  return '<div class="mcard"><div class="mhead">The six measures</div>'+rows+
    lab('Stock it touches:',m[0])+lab('Loop:',m[1])+
    lab('If the system rebalances, its revenue:',m[2])+lab('Clock:',m[5])+
    lab('Evidence behind the flow score:',m[4])+'</div>';
}
const HOUSE=STATE;
const FRESH={cash:null,start:null,positions:{},txns:[],history:[]};
function loadMine(){try{const r=localStorage.getItem('bsMine');if(r)return JSON.parse(r);}catch(e){}return JSON.parse(JSON.stringify(FRESH));}
function saveMine(s){try{localStorage.setItem('bsMine',JSON.stringify(s));}catch(e){}}
let MINE=loadMine();
function whichLedger(){try{return localStorage.getItem('bsLedger')||'mine';}catch(e){return 'mine';}}
function isHouse(){return whichLedger()==='house';}
function L(){return isHouse()?HOUSE:MINE;}
function whoNow(){try{return (localStorage.getItem('bsWho')||'').trim();}catch(e){return '';}}
// Where a company trades, derived from the ticker shape. Access, not quality.
function marketOf(tk){
  if(tk.length===5&&tk.slice(-1)==='F')return 'ord';
  if(tk.length===5&&tk.slice(-1)==='Y')return 'adr';
  return 'us';}
const MKTLAB={us:'US exchange',adr:'ADR, over the counter',ord:'foreign ordinary, over the counter'};

// Companies the visitor added themselves, kept in their own browser.
function mineAdded(){try{return JSON.parse(localStorage.getItem('bsAdded')||'[]');}catch(e){return [];}}
function saveAdded(a){try{localStorage.setItem('bsAdded',JSON.stringify(a));}catch(e){}}
// Build a table row for an added ticker out of what the engine actually recorded.
function addedRow(tk){
  const v=SIDX[tk];if(!v)return null;
  const inList=v[1]==='R';
  if(inList)return null;                     // already in the ranked table
  const sc=(v[3]===100&&v[2]>0)?v[2]:0;
  return [tk,v[0],sc,v[6]||'',(PX[tk]||0),v[5]||'','',true,'own','',[],
          ['','','', 'pass','', ''],v[1],v[2],v[3]];}
const AF={stage:12,rawsc:13,scale:14};
function allRows(){
  const extra=mineAdded().map(addedRow).filter(Boolean);
  return NAMES.concat(extra);}
function rec(tk){return allRows().find(n=>n[0]===tk);}

// ---- the basket -------------------------------------------------------------
// Typing a dollar figure into twenty rows is twenty guesses. Picking a set and
// splitting one number across it is a single decision you can see the result of
// before it happens, which is the whole difference in how this feels to use.
function buyable(n){return n[F.px]>0&&gateOf(n)!=='fail';}
function pickedList(){return allRows().filter(n=>ui.picked[n[F.tk]]&&buyable(n));}
function setPicks(list){ui.picked={};list.forEach(n=>{ui.picked[n[F.tk]]=true;});}
function quickPick(which){
  const inv=allRows().filter(n=>buyable(n)&&n[F.tier]!=='t4'&&n[F.tier]!=='exit');
  const byScore=inv.slice().sort((a,b)=>b[F.sc]-a[F.sc]);
  if(which==='none'){ui.picked={};}
  else if(which==='all'){setPicks(inv);}
  else if(which==='top10'){setPicks(byScore.slice(0,10));}
  else if(which==='cheap'){setPicks(inv.filter(n=>n[F.px]<=10));}
  else if(which==='need'){
    // the best-scoring company in each need, which also breaks up the fact that
    // two thirds of the investable list is health
    const seen={},out=[];
    byScore.forEach(n=>{const k=String(n[F.need]||'?').split(' · ')[0];
      if(!seen[k]){seen[k]=1;out.push(n);}});
    setPicks(out);
  }
  else if(which==='mirror'){setPicks(allRows().filter(n=>heldByList(n[F.tk])));}
  uiSave();render();
}
function heldByList(tk){const p=(HOUSE.positions||{})[tk];return p&&p.shares>0.0001;}
// "Copy the list's own book" is the one weighted option: it matches the engine's
// tier split rather than spreading evenly, because that is what the list does.
function basketPlan(){
  const picks=pickedList();
  const amt=parseFloat(ui.spend);
  if(!picks.length||!(amt>0))return {picks:picks,rows:[],total:0};
  const mirror=picks.length&&picks.every(n=>heldByList(n[F.tk]))&&
               picks.length===Object.keys(HOUSE.positions||{}).filter(t=>heldByList(t)).length;
  let rows;
  if(mirror){
    const W={t1:0.60,t2:0.28,t3:0.12};
    const byTier={};picks.forEach(n=>{(byTier[n[F.tier]]=byTier[n[F.tier]]||[]).push(n);});
    const wsum=Object.keys(byTier).reduce((a,k)=>a+(W[k]||0),0)||1;
    rows=[];
    Object.keys(byTier).forEach(k=>{
      const share=amt*((W[k]||0)/wsum)/byTier[k].length;
      byTier[k].forEach(n=>rows.push([n,share]));});
  }else{
    const each=amt/picks.length;
    rows=picks.map(n=>[n,each]);
  }
  return {picks:picks,rows:rows,total:rows.reduce((a,r)=>a+r[1],0),mirror:mirror};
}
function heldOf(tk){const p=(L().positions||{})[tk];return p?p.shares:0;}
function costOf(tk){const p=(L().positions||{})[tk];return p?p.cost:0;}
function totalValue(s){let t=s.cash||0;for(const tk in (s.positions||{}))t+=(s.positions[tk].shares||0)*((rec(tk)||[])[F.px]||0);return t;}
// A visitor's ledger takes its own weekly snapshot: the house ledger is written at
// build time, but each browser holds its own, so without this their tracker stays empty.
function snapshotMine(){
  const s=MINE;
  if(s.cash===null||s.cash===undefined)return;
  const h=s.history||(s.history=[]);
  const lastD=h.length?h[h.length-1].date:null;
  if(lastD===MARK.d)return;
  if(lastD){
    const days=(new Date(MARK.d)-new Date(lastD))/86400000;
    if(days<6)return;
  }
  h.push({date:MARK.d,value:+totalValue(s).toFixed(2),spx:MARK.spx,list:MARK.list});
  saveMine(s);
}
let ui=null,art=null;
function uiDefaults(){return {mkt:"all",cap:99999,minScore:0,sort:"score",picked:{},spend:""};}
function uiLoad(){try{const r=localStorage.getItem('bsUI');if(r)return {...uiDefaults(),...JSON.parse(r)};}catch(e){}return uiDefaults();}
function uiSave(){try{localStorage.setItem('bsUI',JSON.stringify(ui));}catch(e){}}
function filtered(n){
  return (ui.mkt&&ui.mkt!=='all'&&marketOf(n[F.tk])!==ui.mkt)
    ||(ui.cap&&n[F.px]>ui.cap)
    ||(ui.minScore&&n[F.sc]<ui.minScore);}
// The three lines over the same stretch, drawn from the weekly snapshots. Each
// series is a percentage change from its own first reading, because that is the
// only way to put a $5,000 book and an index on one axis honestly.
function renderChart(){
  const h=(L().history||[]);
  const el=$('chart');
  if(h.length<2){
    el.innerHTML='<div class="chartempty">'+(h.length
      ? 'One snapshot so far, taken '+h[0].date+'. The lines start drawing at the next weekly update.'
      : 'The chart starts once you have a snapshot.')+'</div>';
    return;}
  const base=h[0];
  const series=[
    {k:'you', lab:'You',        c:'var(--accent)', d:h.map(r=>base.value?100*(r.value-base.value)/base.value:0)},
    {k:'list',lab:'The list',   c:'var(--ink)',    d:h.map(r=>(base.list&&r.list)?100*(r.list-base.list)/base.list:null)},
    {k:'spx', lab:'S&amp;P 500',c:'var(--muted)',  d:h.map(r=>(base.spx&&r.spx)?100*(r.spx-base.spx)/base.spx:null)}
  ];
  const all=series.flatMap(s=>s.d).filter(v=>v!==null&&isFinite(v));
  let lo=Math.min(0,...all),hi=Math.max(0,...all);
  if(hi-lo<1){lo-=1;hi+=1;}
  const pad=(hi-lo)*0.12;lo-=pad;hi+=pad;
  const W=720,H=230,L0=44,R=12,T=14,B=30;
  const x=i=>L0+(W-L0-R)*(h.length===1?0.5:i/(h.length-1));
  const y=v=>T+(H-T-B)*(1-(v-lo)/(hi-lo));
  const zero=y(0);
  let g='';
  // horizontal guides at zero and at the extremes
  [lo+pad,0,hi-pad].forEach(function(v){
    const yy=y(v);
    g+='<line x1="'+L0+'" y1="'+yy.toFixed(1)+'" x2="'+(W-R)+'" y2="'+yy.toFixed(1)+
       '" stroke="currentColor" stroke-width="1" opacity="'+(Math.abs(v)<0.001?0.35:0.12)+'"'+
       (Math.abs(v)<0.001?'':' stroke-dasharray="3 4"')+'/>';
    g+='<text x="'+(L0-7)+'" y="'+(yy+3.5).toFixed(1)+'" text-anchor="end" font-size="10.5" '+
       'fill="currentColor" opacity="0.6" font-family="ui-monospace,monospace">'+
       (v>0?'+':'')+v.toFixed(1)+'%</text>';});
  series.forEach(function(s){
    const pts=s.d.map((v,i)=>v===null?null:x(i).toFixed(1)+','+y(v).toFixed(1)).filter(Boolean);
    if(pts.length<2)return;
    g+='<polyline points="'+pts.join(' ')+'" fill="none" stroke="'+s.c+'" stroke-width="'+
       (s.k==='you'?2.4:1.6)+'" stroke-linejoin="round" stroke-linecap="round"'+
       (s.k==='spx'?' stroke-dasharray="5 4"':'')+'/>';
    const last=s.d.map((v,i)=>[v,i]).filter(p=>p[0]!==null).pop();
    if(last)g+='<circle cx="'+x(last[1]).toFixed(1)+'" cy="'+y(last[0]).toFixed(1)+
       '" r="'+(s.k==='you'?3.6:2.6)+'" fill="'+s.c+'"/>';});
  g+='<text x="'+L0+'" y="'+(H-9)+'" font-size="10.5" fill="currentColor" opacity="0.6" '+
     'font-family="ui-monospace,monospace">'+h[0].date+'</text>';
  g+='<text x="'+(W-R)+'" y="'+(H-9)+'" text-anchor="end" font-size="10.5" fill="currentColor" '+
     'opacity="0.6" font-family="ui-monospace,monospace">'+h[h.length-1].date+'</text>';
  const leg=series.map(function(s){
    const last=s.d.filter(v=>v!==null).pop();
    return '<span class="lg"><i style="background:'+s.c+
      (s.k==='spx'?';opacity:.7':'')+'"></i>'+s.lab+
      (last===undefined||last===null?'':' <b class="'+(last>=0?'pos':'neg')+'">'+
       (last>=0?'+':'')+last.toFixed(2)+'%</b>')+'</span>';}).join('');
  el.innerHTML='<div class="chartwrap"><svg viewBox="0 0 '+W+' '+H+'" role="img" '+
    'aria-label="Percentage change over time for your simulation, the list, and the S&amp;P 500, '+
    'measured from '+h[0].date+'">'+g+'</svg><div class="chartleg">'+leg+'</div></div>';
}
// ---- three views in one file ------------------------------------------------
// Browsing, trading and reviewing are three different frames of mind, so they get
// three pages. It stays a single self-contained file: the nav swaps which view is
// shown and the hash drives it, so links and the back button behave normally and
// nothing needs a server.
const VIEWS=['list','trade','me'];
function currentView(){
  const h=(location.hash||'').replace('#','');
  return VIEWS.indexOf(h)>=0?h:'list';
}
function showView(v,push){
  if(VIEWS.indexOf(v)<0)v='list';
  VIEWS.forEach(function(k){
    const el=$('v-'+k);if(el)el.style.display=(k===v)?'block':'none';});
  document.querySelectorAll('nav a.tab').forEach(function(a){
    a.classList.toggle('on',a.dataset.view===v);});
  // One nav serves every view, so the money readout is hidden rather than removed.
  const nmoney=$('navmoney');if(nmoney)nmoney.style.display=(v==='list')?'none':'';
  if(push&&location.hash!=='#'+v){history.pushState(null,'','#'+v);}
  window.scrollTo(0,0);
  render();
}

// ---- the row detail ---------------------------------------------------------
// The reasoning behind a score used to live only in a title attribute, which does
// not exist on a touch screen. On a phone it was simply unreachable. Tapping a row
// opens it instead, so the reasoning behind a score is reachable on any device.
function openDetail(tk){
  const n=rec(tk);if(!n)return;
  const m=n[F.meta]||[],own=n[F.tier]==='own',gf=gateOf(n)==='fail';
  const sh=heldOf(tk),mv=sh*(n[F.px]||0),pl=mv-costOf(tk);
  const d=SPARK[tk];
  let yearLine='';
  if(d&&d.length>7){
    const pct=100*(d[d.length-1]/d[0]-1);
    yearLine='<div class="dstat"><span>Past year</span><b class="'+(pct>=0?'pos':'neg')+'">'+
      (pct>=0?'+':'')+pct.toFixed(1)+'%</b></div>';}
  const lab=function(t,v){return v?'<div class="mlab"><b>'+t+'</b> '+esc(String(v))+'</div>':'';};
  $('modalbody').innerHTML=
    '<div class="dhead"><span class="dtier">'+(own?'YOURS':n[F.tier].toUpperCase())+'</span>'+
      '<h3 id="modaltitle">'+esc(n[F.nm])+' <span class="dtk">'+tk+'</span></h3></div>'+
    '<p class="dblurb">'+esc(String(n[F.kid]||n[F.need]||''))+'</p>'+
    '<div class="dstats">'+
      '<div class="dstat"><span>Score</span><b>'+(n[F.sc]||'-')+'<i>/100</i></b></div>'+
      '<div class="dstat"><span>Price</span><b>'+(n[F.px]?fmt(n[F.px]):'n/a')+'</b></div>'+
      yearLine+
      (sh>0.0001?'<div class="dstat"><span>You hold</span><b>'+sh.toFixed(4)+' sh</b></div>'+
        '<div class="dstat"><span>Worth</span><b>'+fmt(mv)+'</b></div>'+
        '<div class="dstat"><span>P/L</span><b class="'+(pl>=0?'pos':'neg')+'">'+
          (pl>=0?'+':'-')+fmt(Math.abs(pl)).slice(1)+'</b></div>':'')+
    '</div>'+
    (gf?'<div class="note" style="margin:12px 0">Set aside by the survivability gate, whatever it scored. '+
        'That is a reading of its balance sheet, not of its business, and it stays out of any portfolio here.</div>':'')+
    (own?'<p class="dblurb"><i>'+esc(String(n[F.note]||'You added this.'))+'</i></p>':scorecard(n))+
    lab('Stock it touches:',m[0])+lab('Loop:',m[1])+
    lab('If the system rebalances, its revenue:',m[2])+lab('Clock:',m[5])+
    lab('Evidence behind the flow score:',m[4])+
    '<div class="dact">'+
    '</div><div class="msg" id="dmsg"></div>';
  $('modal').hidden=false;
  document.body.style.overflow='hidden';
  const wire=function(sel,fn){const b=document.querySelector(sel);if(b)b.onclick=fn;};
}
function closeDetail(){$('modal').hidden=true;document.body.style.overflow='';}

// What you own, on the trading page, so selling does not mean hunting the big table.
function renderSell(){
  const el=$('sellbox');if(!el)return;
  const pos=L().positions||{};
  const rows=Object.keys(pos).filter(tk=>pos[tk].shares>0.0001)
    .map(function(tk){const n=rec(tk);const px=(n||[])[F.px]||0;
      return {tk:tk,n:n,sh:pos[tk].shares,mv:pos[tk].shares*px,pl:pos[tk].shares*px-pos[tk].cost};})
    .sort((a,b)=>b.mv-a.mv);
  if(!rows.length){
    el.innerHTML='<div class="chartempty">You do not own anything yet. Pick companies above and buy.</div>';return;}
  el.innerHTML='<div class="tablewrap"><table><thead><tr><th>Ticker</th><th>Company</th>'+
    '<th style="text-align:right">Shares</th><th style="text-align:right">Worth</th>'+
    '<th style="text-align:right">P/L</th><th>$ to sell</th><th></th></tr></thead><tbody>'+
    rows.map(function(r){
      return '<tr><td class="tk">'+r.tk+'</td><td>'+esc((r.n||[])[F.nm]||r.tk)+'</td>'+
        '<td class="r">'+r.sh.toFixed(4)+'</td><td class="r">'+fmt(r.mv)+'</td>'+
        '<td class="r '+(r.pl>=0?'pos':'neg')+'">'+(r.pl>=0?'+':'-')+fmt(Math.abs(r.pl)).slice(1)+'</td>'+
        '<td><input type="number" class="amt" min="1" step="10" id="samt_'+r.tk+'" '+
          'aria-label="dollars of '+r.tk+' to sell"></td>'+
        '<td><button class="sell" data-ssell="'+r.tk+'">Sell</button></td></tr>';}).join('')+
    '</tbody></table></div>'+
    '<div class="money-line" style="margin-top:8px">Total holdings '+
      fmt(rows.reduce((a,r)=>a+r.mv,0))+' plus '+fmt(L().cash||0)+' cash.</div>';
  el.querySelectorAll('button[data-ssell]').forEach(b=>b.onclick=()=>{
    const tk=b.dataset.ssell;const v=$('samt_'+tk).value;
    if(!v){$('buymsg').textContent='Enter how many dollars of '+tk+' to sell.';return;}
    trade(tk,'SELL',v);});
}
// Show the arithmetic before anything happens: how many, how much each, what is
// left over. Nobody should have to trust a button with their whole balance.
function renderBasket(){
  const p=basketPlan();
  const cash=L().cash||0;
  const n=p.picks.length;
  if(!n){
    $('bksum').innerHTML='Nothing picked yet. Use one of the buttons above to choose a starting set.';
    $('bkbreak').innerHTML='';return;}
  if(!p.rows.length){
    $('bksum').innerHTML='<b>'+n+'</b> picked. Enter how much to spend and it splits across them.';
    $('bkbreak').innerHTML='';return;}
  const each=p.total/n;
  const over=p.total>cash+0.001;
  $('bksum').innerHTML=(p.mirror
      ? 'Splitting <b>'+fmt(p.total)+'</b> across <b>'+n+'</b> companies the way the list does, 60% Tier 1, 28% Tier 2, 12% Tier 3.'
      : 'Splitting <b>'+fmt(p.total)+'</b> evenly across <b>'+n+'</b> companies, <b>'+fmt(each)+'</b> each.')
    +' You have '+fmt(cash)+' in cash'
    +(over?', which is <b class="neg">'+fmt(p.total-cash)+' short</b>.':', leaving '+fmt(cash-p.total)+'.');
  const sorted=p.rows.slice().sort((a,b)=>b[1]-a[1]||b[0][F.sc]-a[0][F.sc]);
  $('bkbreak').innerHTML='<div class="planbox">'+sorted.map(function(r){
    const nn=r[0],d=r[1],sh=nn[F.px]?d/nn[F.px]:0;
    return '<div class="planrow"><span><b>'+nn[F.tk]+'</b> <span style="color:var(--muted)">'+esc(nn[F.nm])+'</span></span>'+
           '<span>'+fmt(d)+' <span style="color:var(--muted)">= '+sh.toFixed(3)+' sh</span></span></div>';})
    .join('')+'</div>';
}
function render(){
  uiSave();
  const funded=L().cash!==null&&L().cash!==undefined;
  const tot=funded?totalValue(L()):0;
  $('navmoney').innerHTML=funded?('<b>'+fmt(tot)+'</b> · cash '+fmt(L().cash)):'<b>$5,000</b> waiting for you';
  const cashNow=funded?fmt(L().cash):'';
  // The About page carries no money line at all. Everything about the money lives
  // on the trading page, where it can actually be moved.
  const mb2=$('moneybartext2');if(mb2)mb2.innerHTML=funded
    ? ('You have <b>'+cashNow+'</b> of pretend money in cash, kept privately in your own browser. '
       +'Buying and selling happen here, and every trade shows you the arithmetic before anything '
       +'happens. Selling puts cash back. There is no more where it came from, so selling is the '
       +'only way to free up more to spend.')
    : ('This is the list\'s own book, rebalanced weekly by the engine. It is read-only here. '
       +'Switch the view above to your own simulation to trade.');
  renderBasket();renderSell();
  const ROWS=allRows();
  let rows=ROWS.map(n=>{const tk=n[0],sh=heldOf(tk),mv=sh*(n[F.px]||0),pl=mv-costOf(tk);
    return{n:n,tk:tk,sh:sh,mv:mv,pl:pl,
      visible:!filtered(n)};});
  const k=ui.sort;
  rows.sort((a,b)=>{
    if(k==="tier"){const t=a.n[F.tier].localeCompare(b.n[F.tier]);return t!==0?t:b.n[F.sc]-a.n[F.sc];}
    if(k==="price")return a.n[F.px]-b.n[F.px];
    if(k==="industry"){const t=(a.n[F.need]||"").localeCompare(b.n[F.need]||"");return t!==0?t:b.n[F.sc]-a.n[F.sc];}
    return b.n[F.sc]-a.n[F.sc];});
  let h='',vis=0;
  rows.forEach(r=>{if(!r.visible)return;vis++;const n=r.n,tk=r.tk;
    const vchip=n[F.vt]?'<span class="vtag '+(n[F.vt]==="pushback"?"pb":"emb")+'" title="'+(n[F.vt]==="pushback"?"makes healthcare cheaper or fairer overall":"earns through premium prices paid by insurance")+'">'+(n[F.vt]==="pushback"?"pb":"emb")+'</span>':'';
    const mt=n[F.meta]||[],gf=gateOf(n)==='fail';
    const tip=[mt[0]?'Stock: '+mt[0]:'',mt[1]?'Loop: '+mt[1]:'',
      mt[2]?'If the system rebalances, revenue '+mt[2]:'',String(n[F.note]||'')]
      .filter(Boolean).join('\n\n').replace(/"/g,'&quot;');
    const own=n[F.tier]==='own';
    const scLbl=own?(n[F.sc]>0?n[F.sc]:(n[AF.rawsc]>0?n[AF.rawsc]+'<span style="color:var(--muted);font-size:10px">/50</span>':'-')):n[F.sc];
    h+='<tr title="'+tip+'" data-tk="'+tk+'" tabindex="0" role="button" '+
      'aria-label="Open details for '+esc(n[F.nm])+'" class="rowclick '+(own?'ownrow':'')+'">'+
      '<td class="tierpill" data-l="Tier">'+(own?'YOURS':n[F.tier].toUpperCase())+(gf?'<span class="gdot" title="Did not clear the survivability gate, so it is excluded from any plan">!</span>':'')+'</td>'+
      '<td class="tk" data-l="Ticker">'+tk+'</td>'+
      '<td class="co" data-l="Company"><span class="cn">'+n[F.nm]+vchip+'</span><div class="blurb">'+(n[F.kid]||n[F.need]||'')+(own?'<br><i>'+esc(String(n[F.note]||'You added this.'))+'</i>':'')+'</div></td>'+
      '<td class="r" style="font-weight:600" data-l="Score">'+scLbl+'</td><td class="nm" data-l="Industry">'+(n[F.need]||'')+'</td>'+
      '<td class="r cPx" data-l="Price">'+(n[F.px]?fmt(n[F.px]):'n/a')+sparkline(tk)+'</td>'+
      // Committing happens on Buy & sell. Browsing only picks, so the row
      // carries no amount box and no Buy or Sell. Rows you added keep Remove.
      '<td class="cRow'+(own?'':' flat')+'" data-l="">'+(own
        ? '<button class="rm" data-drop="'+tk+'" title="Take this row out of your table">Remove</button>'
        : '')+'</td></tr>';});
  $('mktbody').innerHTML=h;$('emptymsg').style.display=vis?'none':'block';
  document.querySelectorAll('button[data-drop]').forEach(b=>b.onclick=()=>{
    const tk=b.dataset.drop;
    if(heldOf(tk)>0.0001){alert('Sell your '+tk+' shares first, then it can be removed.');return;}
    saveAdded(mineAdded().filter(x=>x!==tk));render();lookup();});
  // Tapping anywhere else on a row opens its detail. Buttons and inputs inside the
  // row stop the event, so the two do not fight.
  document.querySelectorAll('#mktbody tr[data-tk]').forEach(function(tr){
    tr.onclick=function(e){
      if(e.target.closest('button,input,select,a'))return;
      openDetail(tr.dataset.tk);};
    tr.onkeydown=function(e){
      if(e.key==='Enter'||e.key===' '){e.preventDefault();openDetail(tr.dataset.tk);}};});
  let hh='';(L().history||[]).forEach(r=>{const d=r.value-(L().start?L().start.cash:r.value);
    const p2=L().start?100*d/L().start.cash:0;const h0=L().history[0]||{};
    const sp=(h0.spx&&r.spx)?(100*(r.spx-h0.spx)/h0.spx):null;
    const li=(h0.list&&r.list)?(100*(r.list-h0.list)/h0.list):null;
    const pc=function(v){return v===null?'<td class="r">-</td>'
      :'<td class="r '+(v>=0?'pos':'neg')+'">'+v.toFixed(2)+'%</td>';};
    hh+='<tr><td>'+r.date+'</td><td class="r">'+fmt(r.value)+'</td><td class="r '+(d>=0?'pos':'neg')+'">'+(d>=0?'+':'−')+fmt(Math.abs(d)).slice(1)+'</td>'+pc(p2)+pc(li)+pc(sp)+'</tr>';});
  $('histbody').innerHTML=hh||'<tr><td colspan="6" style="color:var(--muted)">Your first snapshot is taken now, and another lands at each weekly update from here.</td></tr>';
  renderChart();
  let th='';(L().txns||[]).slice(-30).reverse().forEach(t=>{
    th+='<tr><td>'+t.d+'</td><td>'+(t.by||'You')+'</td><td>'+t.a+'</td><td class="tk">'+(t.tk||'-')+'</td><td class="r">'+(t.sh?t.sh.toFixed(4):'-')+'</td><td class="r">'+(t.px?fmt(t.px):'-')+'</td><td class="r">'+fmt(t.amt)+'</td></tr>';});
  $('txnbody').innerHTML=th||'<tr><td colspan="7" style="color:var(--muted)">Nothing yet.</td></tr>';
  $('ledgersel').value=whichLedger();
  if($('whoname').value!==whoNow())$('whoname').value=whoNow();
  $('tradermsg').textContent=isHouse()?(art?'House ledger: your trades save into the page.':'The house ledger is read-only for you. Switch to My simulation to trade.'):'Your own $5,000, saved privately in this browser.';
  renderBoard();
}
if(window.claude&&claude.use){claude.use('artifact').then(a=>{art=a;render();}).catch(()=>{render();});}
// amtOverride lets the detail popup and the sell list drive the same code path as
// the table row, so there is one place where a trade actually happens.
async function trade(tk,act,amtOverride){
  const inp=$('amt_'+tk);
  const amt=parseFloat(amtOverride!==undefined?amtOverride:(inp&&inp.value));
  const n=rec(tk);const p=n?n[F.px]:null;
  if(!(amt>0)||!p){$('buymsg').textContent='Enter a dollar amount for '+tk+' first.';return;}
  if(L().cash===null||L().cash===undefined){$('buymsg').textContent='This book is read-only. Switch the view to your own simulation.';return;}
  const who=whoNow()||'You';
  const s=JSON.parse(JSON.stringify(L()));s.positions=s.positions||{};
  if(act==='BUY'){
    if(amt>s.cash+0.001){$('buymsg').textContent='Not enough cash: you have '+fmt(s.cash)+' and that costs '+fmt(amt)+'. Sell something first.';return;}
    const sh=amt/p;
    if(!confirm(who+' is buying '+n[F.nm]+' ('+tk+')\n\n'+fmt(amt)+' ÷ '+fmt(p)+' per share = '+sh.toFixed(4)+' shares\nCash left after: '+fmt(s.cash-amt)+'\n\nOK?'))return;
    const q=s.positions[tk]||{shares:0,cost:0};q.shares+=sh;q.cost+=amt;s.positions[tk]=q;s.cash-=amt;
    s.txns.push({d:TODAY,a:'BUY',tk:tk,sh:sh,px:p,amt:amt,by:who});
  }else{
    const q=s.positions[tk];
    if(!q||q.shares<0.0001){$('buymsg').textContent='You do not own any '+tk+'.';return;}
    const sh=Math.min(q.shares,amt/p);const proceeds=sh*p;
    if(!confirm(who+' is selling '+n[F.nm]+' ('+tk+')\n\n'+sh.toFixed(4)+' shares × '+fmt(p)+' each = '+fmt(proceeds)+' back to cash\nShares left after: '+(q.shares-sh).toFixed(4)+'\n\nOK?'))return;
    q.cost=q.cost*(1-sh/q.shares);q.shares-=sh;if(q.shares<0.0001){q.shares=0;q.cost=0;}
    s.cash+=proceeds;s.txns.push({d:TODAY,a:'SELL',tk:tk,sh:sh,px:p,amt:proceeds,by:who});
  }
  await commit(s,'buymsg');
}
async function buyBasket(){
  const p=basketPlan();
  if(!p.picks.length){$('bkmsg').textContent='Pick at least one company first.';return;}
  if(!p.rows.length){$('bkmsg').textContent='Enter how much you want to spend.';return;}
  const s=JSON.parse(JSON.stringify(L()));
  if(s.cash===null||s.cash===undefined){$('bkmsg').textContent='This book is read-only. Switch the view to your own simulation.';return;}
  if(p.total>s.cash+0.001){
    $('bkmsg').textContent='That is '+fmt(p.total-s.cash)+' more than your '+fmt(s.cash)+' in cash. Lower the amount or sell something.';return;}
  const who=whoNow()||'You';
  if(!confirm(who+' is buying '+p.picks.length+' companies\n\n'+fmt(p.total)+' total\n'
    +'Cash left after: '+fmt(s.cash-p.total)+'\n\nOK?'))return;
  let spent=0,bought=0;
  p.rows.forEach(function(r){
    const n=r[0],amt=r[1],px=n[F.px];
    if(!px||amt<0.01)return;
    const sh=amt/px;
    const q=s.positions[n[F.tk]]||(s.positions[n[F.tk]]={shares:0,cost:0});
    q.shares+=sh;q.cost+=amt;spent+=amt;bought++;
    s.txns.push({d:TODAY,a:'BUY',tk:n[F.tk],sh:sh,px:px,amt:amt,by:who});});
  s.cash-=spent;
  ui.picked={};ui.spend="";uiSave();
  await commit(s,'bkmsg');
  $('bkmsg').textContent='Bought '+bought+' companies for '+fmt(spent)+'.';
}
// Everyone gets the same $5,000, so hand it over on arrival rather than making
// them click for it. Visitor ledger only; the house book is the weekly job's.
function autoFund(){
  if(MINE.start)return;
  MINE.cash=5000;
  MINE.start={date:TODAY,cash:5000};
  (MINE.txns||(MINE.txns=[])).push({d:TODAY,a:'START',amt:5000,by:whoNow()||'You'});
  saveMine(MINE);
}
async function commit(s,msgId){
  if(!isHouse()){MINE=s;saveMine(MINE);$(msgId).textContent='Saved.';render();return;}
  if(!art){$(msgId).textContent='The house ledger is read-only for visitors. Switch to "My simulation" to trade your own $5,000.';return;}
  $(msgId).textContent='Saving…';
  const body=decodeURIComponent(TPL_ENC).replace('%%'+'STATE'+'%%',JSON.stringify(s)).replace('@@'+'TPLENC'+'@@',TPL_ENC);
  const idx='<scr'+'ipt>window.__SIDX='+JSON.stringify(SIDX)+';</scr'+'ipt>';
  const doc='<!doctype html>\n<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'+idx+body+'</body></html>';
  try{await art.publish(doc);$(msgId).textContent='Saved.';}
  catch(e){const c=(e&&e.code)||'';
    $(msgId).textContent=c==='conflict'?'A newer version exists. Reload the page.':(c==='not_writer'||c==='not_granted')?'Read-only: only the owner can trade in the house ledger.':'Save failed. Try again.';}
}
const STAGE={
 R:['Made the list','v-in','It passed every round and every rule.'],
 X:['Removed by a ruling','v-out','It scored well enough, but an owner ruling took it out.'],
 '4':['Cut in the final research round','v-out','It reached the last 104 companies and was studied in depth, then cut.'],
 '3':['Cut on growth and finances','v-out','Its business fit the philosophy, but its numbers or ranking did not hold up.'],
 '2':['Cut on what the business actually does','v-out','On a close read of the business, it did not fit the philosophy.'],
 '1':['Rejected in the first screen','v-out','It broke a hard rule or was too small or inactive to grade.'],
 '0':['Screened, did not advance','v-out','It was scored in the first pass but ranked too low to research further.']};
function lookup(){
  const q=($('q').value||'').trim().toUpperCase();
  if(!q){$('qres').innerHTML='';return;}
  let hits=[];
  if(SIDX[q])hits.push([q,SIDX[q]]);
  if(hits.length<6){for(const k in SIDX){if(hits.length>=6)break;if(k===q)continue;
    if(k.startsWith(q)||String(SIDX[k][0]).toUpperCase().indexOf(q)>=0)hits.push([k,SIDX[k]]);}}
  if(!hits.length){$('qres').innerHTML='<div class="card2">No company matched "'+q+'". Try the ticker symbol.</div>';return;}
  $('qres').innerHTML=hits.map(function(x){
    const tk=x[0],v=x[1],nm=v[0],stage=v[1],sc=v[2],scale=v[3],tier=v[4],why=v[5],need=v[6];
    const st=STAGE[stage]||['Screened','v-out',''];const inList=stage==='R';
    const n=rec(tk);const gf=inList&&gateOf(n)==='fail';
    let scoreLine='';
    if(sc>0&&scale===100){scoreLine='<b>'+sc+' out of 100</b> on the six measures'+(inList?', tier '+String(tier).toUpperCase():'');}
    else if(sc>0){scoreLine='<b>'+sc+' out of 50</b> on the first screen <span style="color:var(--muted)">(need and survivability only; it never reached the full 100-point grading)</span>';}
    else{scoreLine='<span style="color:var(--muted)">No score: it was disqualified before grading.</span>';}
    const already=mineAdded().indexOf(tk)>=0;
    const px=PX[tk]||0;
    let action;
    if(inList){action='<div class="addline ok">Already in the table above.</div>';}
    else if(already){action='<div class="addline ok">In your table. Scroll down to buy it.</div>'+
      '<button class="ghost" data-unadd="'+tk+'">Remove from my table</button>';}
    else{action='<button data-add="'+tk+'">Add '+tk+' to my table</button>'+
      (px?'<span class="addline"> at '+fmt(px)+' a share</span>'
         :'<div class="addline warn">The last engine run could not get a price for this one, so it can be added to your table but not bought until the next run picks one up. That usually means it trades thinly or not at all.</div>');}
    return '<div class="card2"><div class="h">'+nm+' <span class="sub">'+tk+(need?' \u00b7 '+need:'')+'</span></div>'+
      '<div class="verdict '+st[1]+'">'+st[0]+(gf?'<span class="gatefail">gate: set aside</span>':'')+'</div>'+
      '<div style="font-size:13.5px;margin:2px 0">'+scoreLine+'</div>'+
      (gf?'<div style="font-size:12.5px;color:var(--muted);margin-top:4px">It scores well, but it did not clear the survivability gate, so it is kept out of any plan. That is a reading of its balance sheet, not of its business.</div>':'')+
      (inList&&n?scorecard(n):'')+
      '<div style="font-size:13px;color:var(--muted);margin-top:4px">'+(inList
        ? 'Find it in the table above with the rest of the list.'
        : '<b style="color:var(--ink)">Why:</b> '+(why||st[2]))+'</div>'+
      (inList?'':'<div style="font-size:12px;color:var(--muted);margin-top:4px">'+st[2]+'</div>')+
      '<div style="margin-top:8px">'+action+'</div>'+
      '</div>';}).join('');
  document.querySelectorAll('button[data-add]').forEach(b=>b.onclick=()=>{
    const tk=b.dataset.add,a=mineAdded();
    if(a.indexOf(tk)<0){a.push(tk);saveAdded(a);}
    render();lookup();
    const row=document.querySelector('#mktbody tr');
    if(row)document.querySelector('.tablewrap').scrollIntoView({behavior:'smooth',block:'start'});});
  document.querySelectorAll('button[data-unadd]').forEach(b=>b.onclick=()=>{
    const tk=b.dataset.unadd;
    if(heldOf(tk)>0.0001){alert('Sell your '+tk+' shares first, then it can be removed.');return;}
    saveAdded(mineAdded().filter(x=>x!==tk));render();lookup();});
}
// A stable id for this browser so a profile shared from here is recognisable
// when it comes back, and cannot be added as if it were somebody else.
function myId(){
  try{
    let i=localStorage.getItem('bsId');
    if(!i){i=Math.random().toString(36).slice(2,10);localStorage.setItem('bsId',i);}
    return i;
  }catch(e){return 'local';}
}
function myCard(){
  const s=L();const tot=totalValue(s);const start=s.start?s.start.cash:0;
  const top=Object.keys(s.positions||{}).filter(tk=>s.positions[tk].shares>0.0001)
    .map(tk=>[tk,s.positions[tk].shares*((rec(tk)||[])[F.px]||0)]).sort((a,b)=>b[1]-a[1]).slice(0,3).map(x=>x[0]);
  return btoa(JSON.stringify({i:myId(),n:(whoNow()||'Anonymous').slice(0,20),v:+tot.toFixed(2),s:start,d:TODAY,t:top}));
}
function friends(){try{return JSON.parse(localStorage.getItem('bsFriends')||'[]');}catch(e){return [];}}
function saveFriends(a){try{localStorage.setItem('bsFriends',JSON.stringify(a));}catch(e){}}
// The list is a player, not a section of its own. It runs the same $5,000 on the
// same terms, so beating it is a real result rather than a slogan.
function listPlayer(){
  if(HOUSE.cash===null||HOUSE.cash===undefined)return null;
  const top=Object.keys(HOUSE.positions||{})
    .filter(tk=>HOUSE.positions[tk].shares>0.0001)
    .map(tk=>[tk,HOUSE.positions[tk].shares*((rec(tk)||[])[F.px]||0)])
    .sort((a,b)=>b[1]-a[1]).slice(0,3).map(x=>x[0]);
  return {n:'The list',v:totalValue(HOUSE),s:HOUSE.start?HOUSE.start.cash:0,t:top,bot:true};
}
function renderBoard(){
  const s=L();const funded=s.cash!==null&&s.cash!==undefined;
  const me={n:(whoNow()||'You'),v:funded?totalValue(s):0,s:s.start?s.start.cash:0,t:[],me:true};
  const bot=isHouse()?null:listPlayer();
  const all=(funded?[me]:[]).concat(friends()).concat(bot?[bot]:[]);
  if(!all.length){$('leaderboard').innerHTML='<div class="money-line">Buy something and you will appear here, next to the list.</div>';return;}
  all.sort((a,b)=>((b.v-b.s)/(b.s||1))-((a.v-a.s)/(a.s||1)));
  $('leaderboard').innerHTML=all.map(function(p,i){
    const gain=p.v-p.s;const pct=p.s?100*gain/p.s:0;
    const tag=p.me?' (you)':(p.bot?'<span class="botpill">the algorithm</span>':'');
    const key=p.i||p.n;
    const drop=(p.me||p.bot)?'':'<button class="lbx" data-unfriend="'+esc(String(key))+'" title="Remove '+esc(p.n)+' from the board">&times;</button>';
    return '<div class="lbrow'+(p.me?' me':'')+(p.bot?' bot':'')+'"><span class="rank">'+(i+1)+'</span><span class="who">'+esc(p.n)+tag+
      (p.t&&p.t.length?' <span style="color:var(--muted)">· '+p.t.join(' ')+'</span>':'')+'</span>'+
      '<span>'+fmt(p.v)+'</span><span class="'+(gain>=0?'pos':'neg')+'">'+(gain>=0?'+':'')+pct.toFixed(2)+'%</span>'+drop+'</div>';}).join('');
  document.querySelectorAll('button[data-unfriend]').forEach(b=>b.onclick=()=>{
    const k=b.dataset.unfriend;
    saveFriends(friends().filter(x=>String(x.i||x.n)!==k));renderBoard();
    $('cardmsg').textContent='Removed.';});
}
document.querySelectorAll('button[data-qp]').forEach(b=>b.onclick=()=>quickPick(b.dataset.qp));
$('spend').addEventListener('input',()=>{ui.spend=$('spend').value;uiSave();renderBasket();});
$('spendall').onclick=()=>{ui.spend=String(Math.floor((L().cash||0)*100)/100);$('spend').value=ui.spend;uiSave();renderBasket();};
$('basketbuy').onclick=buyBasket;
$('qbtn').onclick=lookup;
$('q').addEventListener('keydown',function(e){if(e.key==='Enter')lookup();});
$('copycard').onclick=async()=>{const c=myCard();
  try{await navigator.clipboard.writeText(c);$('cardmsg').textContent='Copied. Send it to a friend.';}
  catch(e){$('friendcode').value=c;$('cardmsg').textContent='Copy the code from the box below.';}};
$('addfriend').onclick=()=>{const raw=($('friendcode').value||'').trim();if(!raw)return;
  try{const p=JSON.parse(atob(raw));if(!p.n||typeof p.v!=='number')throw 0;
    if(p.i&&p.i===myId()){
      $('cardmsg').textContent='That is your own profile. You are already on the board.';
      $('friendcode').value='';return;}
    const a=friends().filter(x=>(p.i?x.i!==p.i:x.n!==p.n));a.push(p);saveFriends(a);
    $('friendcode').value='';$('cardmsg').textContent='Added '+p.n+'.';renderBoard();}
  catch(e){$('cardmsg').textContent='That code did not look right.';}};
$('clearfriends').onclick=()=>{saveFriends([]);renderBoard();$('cardmsg').textContent='Cleared.';};
$('ledgersel').addEventListener('change',()=>{try{localStorage.setItem('bsLedger',$('ledgersel').value)}catch(e){}render();});
$('whoname').addEventListener('input',()=>{try{localStorage.setItem('bsWho',$('whoname').value.trim().slice(0,24))}catch(e){}renderBoard();});
$('mktsel').addEventListener('change',()=>{ui.mkt=$('mktsel').value;render();});
$('capsel').addEventListener('change',()=>{ui.cap=+$('capsel').value;render();});
$('scorepol').addEventListener('change',()=>{ui.minScore=+$('scorepol').value;render();});
$('sortsel').addEventListener('change',()=>{ui.sort=$('sortsel').value;render();});
function pushUI(){$('mktsel').value=ui.mkt||'all';$('spend').value=ui.spend||'';
  $('capsel').value=String(ui.cap);$('scorepol').value=String(ui.minScore);
  $('sortsel').value=ui.sort;}
// ---- layer 0: the civilization imbalance map -------------------------------
// Rendered from IMB, which the build injects from data/imbalance_map.json.
// The diagnosis comes first; companies appear only at the end of each chain,
// which is the ordering the whole engine runs on.
function imbChip(tk){
  const n=rec(tk);if(!n)return '';
  return '<button class="imbco" data-imbco="'+tk+'" title="Open the company detail">'+
    tk+' &middot; '+n[F.sc]+' &middot; '+String(n[F.tier]).toUpperCase()+'</button>';
}
function renderImbalance(){
  const el=$('imbmap');if(!el||typeof IMB==='undefined')return;
  const grp=[['earth','Earth-system stocks'],['provisioning','Human provisioning stocks']];
  el.innerHTML=grp.map(function(g){
    const rows=IMB.systems.filter(s=>s.cls===g[0]).sort((a,b)=>b.severity.score-a.severity.score);
    return '<div class="imbhead">'+g[1]+'</div>'+rows.map(function(s){
      const co=s.tickers.map(imbChip).join('')||
        '<i>No public company in this universe clears the screen on this correction yet. The imbalance is recorded anyway; it exists without one.</i>';
      return '<button class="imbrow" data-imb="'+s.id+'" aria-expanded="false" aria-controls="imbx_'+s.id+'">'+
        '<span class="sev">'+s.severity.score+'</span>'+
        '<span class="sevbar"><i style="width:'+Math.max(2,s.severity.score)+'%"></i></span>'+
        '<span class="nm2">'+s.name+'</span>'+
        '<span class="frm frm-'+s.form+'">'+(s.form==='both'?'overshoot + deficit':s.form)+'</span>'+
        '<span class="mv">'+s.direction+'</span>'+
        '<span class="nco">'+(s.tickers.length?s.tickers.length+' co':'gap')+'</span></button>'+
        '<div class="imbx" id="imbx_'+s.id+'" hidden><dl>'+
        '<dt>Stock</dt><dd>'+s.stock+'</dd>'+
        '<dt>Safe range</dt><dd>'+s.safe_range+'</dd>'+
        '<dt>State</dt><dd>'+s.state+'</dd>'+
        '<dt>Distance from equilibrium</dt><dd>'+s.distance_note+'</dd>'+
        '<dt>Movement</dt><dd>'+({diverging:'diverging from the safe range',holding:'holding its distance from the safe range',returning:'returning toward the safe range'})[s.direction]+'</dd>'+
        (s.envelope?'<dt>Natural rhythm and envelope</dt><dd>'+s.envelope+'</dd>':'')+
        '<dt>Physical flows causing it</dt><dd>'+s.cause+'</dd>'+
        '<dt>Required correction</dt><dd>'+s.correction+'</dd>'+
        '<dt>Correction clock</dt><dd>'+s.clock+'</dd>'+
        '<dt>Companies on this correction</dt><dd>'+co+'</dd>'+
        '</dl></div>';
    }).join('');
  }).join('');
  el.querySelectorAll('button[data-imb]').forEach(function(b){
    b.onclick=function(){const x=$('imbx_'+b.dataset.imb);if(!x)return;
      x.hidden=!x.hidden;b.setAttribute('aria-expanded',String(!x.hidden));};});
  el.querySelectorAll('button[data-imbco]').forEach(function(b){
    b.onclick=function(e){e.stopPropagation();openDetail(b.dataset.imbco);};});
}

// nav, hash routing and the modal
document.querySelectorAll('nav a.tab').forEach(function(a){
  a.onclick=function(e){e.preventDefault();showView(a.dataset.view,true);};});
window.addEventListener('popstate',function(){showView(currentView(),false);});
document.querySelectorAll('#modal [data-close]').forEach(function(el){el.onclick=closeDetail;});
document.addEventListener('keydown',function(e){
  if(e.key==='Escape'&&!$('modal').hidden)closeDetail();});

ui=uiLoad();autoFund();snapshotMine();pushUI();renderImbalance();showView(currentView(),false);
</script>
"""

tpl = (TEMPLATE
       .replace("@@NAMES@@", json.dumps(names_js))
       .replace("@@IMBALANCE@@", json.dumps(imb_map, separators=(",", ":")))
       .replace("@@RULES@@", RULES_HTML)
       .replace("@@UNIV@@", f"{len(sidx):,}")
       .replace("@@RANKED@@", str(len(names_js)))
       .replace("@@MARK@@", json.dumps({"d": today, "spx": spx, "list": basket_level}))
       .replace("@@TIERSUM@@", tiersum_html)
       .replace("@@HOUSENOTE@@", house_note)
       .replace("@@HOUSESTAMP@@", state.get("last_rebalance") or today)
       .replace("@@TODAY@@", today)
       .replace("@@ASOF@@", asof)
       .replace("@@STAMP@@", stamp))
tpl_enc = urllib.parse.quote(tpl, safe="")
# Search index and price map ride outside the quine template so the self-save
# payload stays small; the page reads them from window.
idx_script = ("<script>window.__SIDX=" + json.dumps(sidx, separators=(",", ":")) +
              ";window.__PX=" + json.dumps(pxcache, separators=(",", ":")) +
              ";window.__SPARK=" + json.dumps(spark, separators=(",", ":")) + ";</script>\n")
page = idx_script + tpl.replace("%%STATE%%", json.dumps(state)).replace("@@TPLENC@@", tpl_enc)
open(OUT, "w", encoding="utf-8").write(page)
print(f"console rendered: {len(names_js)} ranked, {len(sidx)} searchable, "
      f"{len(pxcache)} priced | {len(page)//1024} KB")
