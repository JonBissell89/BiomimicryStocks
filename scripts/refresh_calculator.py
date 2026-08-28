"""Regenerate the Allocation Arithmetic page FROM the engine:
tier membership from engine_tiers.json + live Yahoo prices (read-only in the page).
Writes the HTML; republish via the Artifact tool afterwards."""
import os
from paths import BUILD, DATA
import json, warnings
from datetime import datetime, timezone
warnings.filterwarnings("ignore")
import pandas as pd
import yfinance as yf

ENGINE = os.path.join(DATA, "engine_tiers.json")
OUT = os.path.join(BUILD, "allocation_calculator.html")

eng = json.load(open(ENGINE, encoding="utf-8"))
GATE = eng["gate"]
tickers = [n["tk"] for t in eng["tiers"] for n in t["names"]] + [w["tk"] for w in eng["watch_alerts"]]

# watch bench (for the price-view explorer): scored names above the gate
wb = pd.read_csv(os.path.join(DATA, "final_watch.csv"))
wb["ticker"] = wb.ticker.astype(str).str.upper()
tiered = {n["tk"] for t in eng["tiers"] for n in t["names"]}
wb = wb[~wb.ticker.isin(tiered | {"INPOY"})].copy()  # INPOY disqualified (buyout)
wb["score"] = pd.to_numeric(wb["total"].astype(str).str.extract(r"([0-9]+)")[0], errors="coerce")
wb = wb.dropna(subset=["score"]).drop_duplicates("ticker")
tickers += [t for t in wb.ticker if t not in tickers]

px = yf.download(tickers, period="5d", progress=False, threads=True, auto_adjust=True)["Close"]
last = px.ffill().iloc[-1]
asof_px = str(px.index[-1].date())
stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

prices = {}
for t in tickers:
    v = last.get(t)
    prices[t] = round(float(v), 2) if pd.notna(v) else None

watch_js = sorted(
    [[r.ticker, int(r.score), prices.get(r.ticker)] for r in wb.itertuples() if prices.get(r.ticker)],
    key=lambda x: -x[1])

# JS data structure rendered from the engine
tiers_js = []
for tier in eng["tiers"]:
    rows = []
    for n in tier["names"]:
        p = prices.get(n["tk"])
        note = n["note"]
        if n.get("depth") == "light":
            note = (note + " · " if note and "light-verified" not in note else (note + " · " if note else "")) + ""
        rows.append([n["tk"], n["nm"], n["score"], n.get("need", ""), p if p is not None else 0,
                     n["note"], n.get("values", ""), bool(n.get("sofi"))])
    tiers_js.append({"id": tier["id"], "label": tier["label"], "names": rows})
watch_line = "none — bench folded into the unified table"
breach_line = ("Unified graded table: all 51 finalists tiered by score; price is a VIEW filter and never changes membership. "
               "depth=light names are score-confirmed but not deep-audited (dilution/runway); deep passes on request.")

HTML = r"""<title>Allocation Arithmetic</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --ground:#F7F9F8; --card:#FFFFFF; --ink:#16211F; --muted:#5C6B67;
  --accent:#1D5D51; --accent-soft:#E3EEEB; --warn:#A8663B; --warn-soft:#F6ECE4;
  --line:#DCE4E1; --chipbg:#EDF2F0;
  --serif:"Newsreader",Georgia,serif; --sans:"IBM Plex Sans",system-ui,sans-serif; --mono:"IBM Plex Mono",Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#101715; --card:#17201D; --ink:#E8EEEB; --muted:#93A39E;
    --accent:#5FA894; --accent-soft:#1C2E29; --warn:#D08B5C; --warn-soft:#2C231A;
    --line:#26332F; --chipbg:#1E2A26;
  }
}
:root[data-theme="dark"]{
  --ground:#101715; --card:#17201D; --ink:#E8EEEB; --muted:#93A39E;
  --accent:#5FA894; --accent-soft:#1C2E29; --warn:#D08B5C; --warn-soft:#2C231A;
  --line:#26332F; --chipbg:#1E2A26;
}
*{box-sizing:border-box}
body{background:var(--ground);color:var(--ink);font-family:var(--sans);margin:0;line-height:1.5;font-size:15px}
.wrap{max-width:960px;margin:0 auto;padding:42px 20px 80px}
header.hero{border-bottom:2px solid var(--ink);padding-bottom:22px;margin-bottom:26px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 8px}
h1{font-family:var(--serif);font-weight:500;font-size:clamp(30px,5.5vw,44px);line-height:1.05;margin:0 0 10px;text-wrap:balance}
.dek{font-size:15.5px;color:var(--muted);max-width:66ch;margin:0}
.controls{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:24px 0}
@media(max-width:720px){.controls{grid-template-columns:1fr}}
.panel{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:18px 20px}
.panel h3{font-family:var(--serif);font-size:17px;font-weight:600;margin:0 0 12px}
label.big{display:block;font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
input[type=number]{font-family:var(--mono);font-size:16px;padding:8px 10px;border:1px solid var(--line);border-radius:4px;background:var(--ground);color:var(--ink);width:100%}
input[type=number]:focus{outline:2px solid var(--accent);outline-offset:1px}
.slider-row{display:grid;grid-template-columns:120px 1fr 64px;gap:10px;align-items:center;margin:10px 0}
.slider-row .sl{font-family:var(--mono);font-size:12px}
.slider-row .sv{font-family:var(--mono);font-size:13px;text-align:right;font-variant-numeric:tabular-nums}
input[type=range]{width:100%;accent-color:var(--accent)}
.rem{font-family:var(--mono);font-size:12px;color:var(--muted);margin-top:8px}
.rem.bad{color:var(--warn)}
h2{font-family:var(--serif);font-weight:600;font-size:22px;margin:36px 0 10px}
.tierhead{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin:22px 0 6px;border-bottom:1px solid var(--line);padding-bottom:4px;display:flex;justify-content:space-between}
.tierhead .amt{font-variant-numeric:tabular-nums}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:660px;font-size:13.5px}
th{font-family:var(--mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:middle;font-variant-numeric:tabular-nums}
td.tk{font-family:var(--mono);font-weight:500;white-space:nowrap}
td.nm{color:var(--muted);font-size:12.5px}
td.px{font-family:var(--mono);white-space:nowrap}
td input.wt{width:60px;font-size:13px;padding:4px 6px}
td.out{font-family:var(--mono);font-weight:500;white-space:nowrap;text-align:right}
td.sh{font-family:var(--mono);color:var(--muted);white-space:nowrap;text-align:right}
.thin{color:var(--warn);font-size:11px;font-family:var(--mono)}
.vtag{font-family:var(--mono);font-size:10px;letter-spacing:.05em;padding:1px 6px;border-radius:3px;margin-left:6px;white-space:nowrap}
.vtag.pb{background:var(--accent-soft);color:var(--accent)}
.vtag.emb{background:var(--chipbg);color:var(--muted)}
tr.vexcl{opacity:.42}
.wchip{font-family:var(--mono);font-size:12px;border:1px solid var(--line);padding:4px 10px;border-radius:4px;white-space:nowrap;background:var(--chipbg);color:var(--muted)}
.wchip.inview{background:var(--accent-soft);color:var(--accent);border-color:var(--accent)}
.wchip b{font-weight:500}
.vfilter{display:flex;gap:8px;align-items:center;font-size:13.5px;margin:10px 0 4px;flex-wrap:wrap}
.vfilter label{cursor:pointer}
.summary{background:var(--accent-soft);border:1px solid var(--line);border-radius:6px;padding:16px 20px;margin:26px 0;font-family:var(--mono);font-size:13px}
.summary .row{display:flex;justify-content:space-between;padding:3px 0;font-variant-numeric:tabular-nums}
.summary .row.total{border-top:1px solid var(--line);margin-top:6px;padding-top:8px;font-weight:600}
.empty{color:var(--muted);font-style:italic;padding:26px;text-align:center;border:1px dashed var(--line);border-radius:6px;margin:20px 0}
.note{background:var(--warn-soft);border-left:3px solid var(--warn);padding:11px 15px;border-radius:0 4px 4px 0;margin:20px 0;max-width:80ch;font-size:13px}
.note b{color:var(--warn)}
footer{margin-top:48px;border-top:2px solid var(--ink);padding-top:14px;color:var(--muted);font-size:12.5px;max-width:78ch}
button.reset{font-family:var(--mono);font-size:12px;background:none;border:1px solid var(--line);color:var(--muted);border-radius:4px;padding:5px 12px;cursor:pointer;margin-top:10px}
button.reset:focus{outline:2px solid var(--accent)}
</style>

<div class="wrap">
<header class="hero">
  <p class="eyebrow">Engine last run: __STAMP__ · prices as of close __ASOFPX__ · monthly auto-run 1st @ 9:00 AM · on-demand: ask Claude to refresh</p>
  <h1>Allocation Arithmetic</h1>
  <p class="dek">Tickers and tiers come from the engine's verified matrix; prices are pulled at refresh time and are not editable. The page does arithmetic on <b>your</b> inputs — sleeve, tier percentages, weights — and contains no recommendation. Not investment advice.</p>
</header>

<div class="controls">
  <div class="panel">
    <h3>1 · Your equity sleeve</h3>
    <label class="big" for="sleeve">Dollars you have decided to allocate (required)</label>
    <input type="number" id="sleeve" min="0" step="100" placeholder="enter an amount — nothing computes until you do">
    <button class="reset" id="reset">Reset all dials</button>
  </div>
  <div class="panel">
    <h3>2 · Tier percentages <span style="font-weight:400;color:var(--muted);font-size:12px">(guardrails shown; midpoints preset — confirm or move them)</span></h3>
    <div class="slider-row"><span class="sl">Tier 1 · 50–70</span><input type="range" id="p1" min="0" max="100" value="60"><span class="sv" id="v1">60%</span></div>
    <div class="slider-row"><span class="sl">Tier 2 · 20–35</span><input type="range" id="p2" min="0" max="100" value="28"><span class="sv" id="v2">28%</span></div>
    <div class="slider-row"><span class="sl">Tier 3 · 5–15</span><input type="range" id="p3" min="0" max="100" value="10"><span class="sv" id="v3">10%</span></div>
    <div class="slider-row"><span class="sl">Sandbox · 0–10</span><input type="range" id="p4" min="0" max="100" value="0"><span class="sv" id="v4">0%</span></div>
    <div class="rem" id="rem">Unallocated (stays cash): 2%</div>
  </div>
</div>

<h2>3 · Names and weights</h2>
<p style="color:var(--muted);max-width:74ch;margin:0 0 6px">Untick a name to drop it; its tier money redistributes across the rest. Weights are relative within a tier (2 = double an equal share). Prices refresh only when the engine republishes this page — the stamp above is their age.</p>
<div class="vfilter"><label><input type="checkbox" id="vf"> <b>Health values filter:</b> exclude <span class="vtag emb">embedded</span> names (economics run through premium reimbursement) — keep only <span class="vtag pb">pushback</span> (prevention, democratized access, forced price compression)</label></div>
<div class="vfilter"><label><input type="checkbox" id="sf" checked> <b>SoFi-available only:</b> show just the names your brokerage can actually trade (empirically confirmed flags; OTC F-shares greyed out)</label></div>
<div class="vfilter"><label for="capsel"><b>Price view:</b></label> <select id="capsel" style="font-family:var(--mono);font-size:12.5px;padding:4px 8px;border:1px solid var(--line);border-radius:4px;background:var(--ground);color:var(--ink)"><option value="10">show ≤ $10</option><option value="20" selected>show ≤ $20 (default)</option><option value="30">show ≤ $30</option><option value="50">show ≤ $50</option><option value="99999">show all</option></select>
<label for="scorepol" style="margin-left:14px"><b>Score policy:</b></label> <select id="scorepol" style="font-family:var(--mono);font-size:12.5px;padding:4px 8px;border:1px solid var(--line);border-radius:4px;background:var(--ground);color:var(--ink)"><option value="0" selected>all scores</option><option value="70">score ≥ 70</option><option value="75">score ≥ 75</option><option value="80">score ≥ 80</option><option value="85">score ≥ 85</option></select>
<span style="color:var(--muted);font-size:12.5px">— filtered names are hidden entirely (hover a row for its verification notes)</span></div>
<div id="tiers"></div>

<div id="outwrap"></div>

<div class="note"><b>Engine last run __STAMP__.</b> __BREACHLINE__ Watch-bench price alerts: __WATCHLINE__ (gate = $__GATE__). Names marked <span class="thin">†thin</span> have near-untradeable US lines — share counts are only real on the noted home exchange.</div>

<footer>
Tier membership, scores, and notes render from <span style="font-family:var(--mono)">tournament/data/engine_tiers.json</span> (final verification Aug 25–27, 2026); prices pulled __STAMP__. The published page cannot fetch live quotes itself (no market-data connector is available to it), so freshness equals the last engine refresh. Sleeve, percentages, inclusions, and weights are user inputs; the page only multiplies them. Taxes, execution, and timing are outside its scope. Not investment advice.
</footer>
</div>

<script>
const TIERS=__TIERSJSON__;
const WATCH=__WATCHJSON__;
const $=id=>document.getElementById(id);
const fmt=n=>"$"+n.toLocaleString(undefined,{maximumFractionDigits:0});
let state=null;
function defaults(){
  const s={sleeve:"",p:[60,28,10,0],inc:{},wt:{},vf:false,sfOnly:true,cap:20,minScore:0};
  TIERS.forEach(t=>t.names.forEach(([tk])=>{s.inc[tk]=t.id!=="t4";s.wt[tk]=1;}));
  return s;
}
function vtagOf(tk){for(const t of TIERS)for(const n of t.names)if(n[0]===tk)return n[6]||"";return "";}
function sofiOf(tk){for(const t of TIERS)for(const n of t.names)if(n[0]===tk)return !!n[7];return false;}
function pxOf(tk){for(const t of TIERS)for(const n of t.names)if(n[0]===tk)return n[4]||0;return 0;}
function scoreOf(tk){for(const t of TIERS)for(const n of t.names)if(n[0]===tk)return n[2]||0;return 0;}
function excluded(tk){
  return (state.sfOnly&&!sofiOf(tk))||(state.vf&&vtagOf(tk)==="embedded")
       ||(state.cap&&pxOf(tk)>state.cap)||(state.minScore&&scoreOf(tk)<state.minScore);
}
function load(){try{const r=localStorage.getItem("allocCalc2");if(r){const s=JSON.parse(r);const d=defaults();return {...d,...s,inc:{...d.inc,...s.inc},wt:{...d.wt,...s.wt}};}}catch(e){}return defaults();}
function save(){try{localStorage.setItem("allocCalc2",JSON.stringify(state));}catch(e){}}
function buildTiers(){
  const host=$("tiers");host.innerHTML="";
  TIERS.forEach(t=>{
    const head=document.createElement("div");head.className="tierhead";
    head.innerHTML=`<span>${t.label}</span><span class="amt" id="amt_${t.id}"></span>`;
    host.appendChild(head);
    const wrapT=document.createElement("div");wrapT.className="tablewrap";
    const tb=document.createElement("table");
    tb.innerHTML=`<thead><tr><th>In</th><th>Ticker</th><th>Company</th><th style="text-align:right">Score</th><th>Industry</th><th style="text-align:right">Price</th><th>Weight</th><th style="text-align:right">Dollars</th><th style="text-align:right">&asymp; Shares</th></tr></thead>`;
    const body=document.createElement("tbody");
    t.names.forEach(([tk,nm,sc,need,p,note,vt])=>{
      const tr=document.createElement("tr");
      tr.id="row_"+tk;
      if(note)tr.title=note;
      const vchip=vt?`<span class="vtag ${vt==="pushback"?"pb":"emb"}">${vt==="pushback"?"pb":"emb"}</span>`:"";
      tr.innerHTML=`<td><input type="checkbox" id="inc_${tk}" aria-label="include ${tk}"></td>
        <td class="tk">${tk}</td>
        <td class="nm">${nm}${vchip}</td>
        <td class="px" style="text-align:right;font-weight:500">${sc}</td>
        <td class="nm">${need||""}</td>
        <td class="px" style="text-align:right">${p?("$"+p.toFixed(2)):"n/a"}</td>
        <td><input type="number" class="wt" id="wt_${tk}" min="0" step="0.25" aria-label="weight ${tk}"></td>
        <td class="out" id="d_${tk}">&mdash;</td><td class="sh" id="s_${tk}">&mdash;</td>`;
      body.appendChild(tr);
    });
    tb.appendChild(body);wrapT.appendChild(tb);host.appendChild(wrapT);
  });
}
function bind(){
  $("sleeve").addEventListener("input",()=>{state.sleeve=$("sleeve").value;recalc();});
  $("vf").addEventListener("change",()=>{state.vf=$("vf").checked;recalc();});
  $("sf").addEventListener("change",()=>{state.sfOnly=$("sf").checked;recalc();});
  $("capsel").addEventListener("change",()=>{state.cap=+$("capsel").value;recalc();});
  $("scorepol").addEventListener("change",()=>{state.minScore=+$("scorepol").value;recalc();});
  ["p1","p2","p3","p4"].forEach((id,i)=>$(id).addEventListener("input",()=>{state.p[i]=+$(id).value;recalc();}));
  TIERS.forEach(t=>t.names.forEach(([tk])=>{
    $("inc_"+tk).addEventListener("change",()=>{state.inc[tk]=$("inc_"+tk).checked;recalc();});
    $("wt_"+tk).addEventListener("input",()=>{state.wt[tk]=+$("wt_"+tk).value;recalc();});
  }));
  $("reset").addEventListener("click",()=>{state=defaults();push();recalc();});
}
function push(){
  $("sleeve").value=state.sleeve;
  $("vf").checked=!!state.vf;
  $("sf").checked=state.sfOnly!==false;
  $("capsel").value=String(state.cap||20);
  $("scorepol").value=String(state.minScore||0);
  ["p1","p2","p3","p4"].forEach((id,i)=>$(id).value=state.p[i]);
  TIERS.forEach(t=>t.names.forEach(([tk])=>{
    $("inc_"+tk).checked=!!state.inc[tk];
    $("wt_"+tk).value=state.wt[tk];
  }));
}
function priceOf(tk){for(const t of TIERS)for(const n of t.names)if(n[0]===tk)return n[4];return 0;}
function recalc(){
  save();
  const sum=state.p.reduce((a,b)=>a+b,0);
  ["v1","v2","v3","v4"].forEach((id,i)=>$(id).textContent=state.p[i]+"%");
  const rem=$("rem");
  if(sum>100){rem.textContent="Tiers total "+sum+"% — over 100. Reduce a slider.";rem.className="rem bad";}
  else{rem.textContent="Unallocated (stays cash): "+(100-sum)+"%";rem.className="rem";}
  const sleeve=parseFloat(state.sleeve);
  const ok=!isNaN(sleeve)&&sleeve>0&&sum<=100;
  const rows=[];
  TIERS.forEach((t,ti)=>{
    const tierD=ok? sleeve*state.p[ti]/100 : 0;
    $("amt_"+t.id).textContent=ok?fmt(tierD):"";
    const inc=t.names.filter(([tk,,,,p])=>state.inc[tk]&&!excluded(tk)&&state.wt[tk]>0&&p>0);
    const wsum=inc.reduce((a,[tk])=>a+state.wt[tk],0);
    t.names.forEach(([tk,,,,p])=>{
      const ex=excluded(tk);
      const rowEl=$("row_"+tk); if(rowEl)rowEl.style.display=ex?"none":"";
      const cb=$("inc_"+tk); if(cb)cb.disabled=ex;
      const on=state.inc[tk]&&!ex&&state.wt[tk]>0&&p>0&&wsum>0&&ok;
      const d=on? tierD*state.wt[tk]/wsum : 0;
      $("d_"+tk).textContent=on?fmt(d):"\u2014";
      $("s_"+tk).textContent=on&&p>0?Math.floor(d/p).toLocaleString():"\u2014";
      if(on&&d>0)rows.push([tk,d]);
    });
  });
  const out=$("outwrap");
  if(!ok){out.innerHTML='<div class="empty">'+(sum>100?"Fix the tier percentages — they exceed 100%.":"Enter a sleeve amount above and the arithmetic appears here.")+"</div>";return;}
  const alloc=rows.reduce((a,[,d])=>a+d,0);
  let html='<div class="summary"><div class="row"><span>Sleeve entered</span><span>'+fmt(sleeve)+"</span></div>";
  html+='<div class="row"><span>Allocated across '+rows.length+" names</span><span>"+fmt(alloc)+"</span></div>";
  html+='<div class="row total"><span>Remains as cash</span><span>'+fmt(sleeve-alloc)+"</span></div></div>";
  const allocStr=rows.map(([t,d])=>t+"="+d.toFixed(2)).join(";");
  html+='<div class="panel"><h3 style="font-family:var(--serif);font-size:16px;margin:0 0 8px">Export to Paper Ledger</h3>'+
       '<textarea id="allocout" readonly rows="2" style="width:100%;font-family:var(--mono);font-size:12px;background:var(--ground);color:var(--ink);border:1px solid var(--line);border-radius:4px;padding:8px" aria-label="allocation export string">'+allocStr+'</textarea>'+
       '<button class="reset" id="copyalloc" style="margin-top:8px">Copy allocation</button> <span id="copymsg" style="font-family:var(--mono);font-size:12px;color:var(--muted)"></span>'+
       '<div style="font-size:12px;color:var(--muted);margin-top:6px">Paste this into the Paper Ledger&rsquo;s &ldquo;Import allocation&rdquo; box to execute the whole basket as virtual buys.</div></div>';
  out.innerHTML=html;
  const cb=document.getElementById("copyalloc");
  if(cb)cb.onclick=async()=>{try{await navigator.clipboard.writeText(allocStr);document.getElementById("copymsg").textContent="copied";}catch(e){document.getElementById("allocout").select();document.getElementById("copymsg").textContent="press Ctrl+C to copy";}};
}
state=load();buildTiers();bind();push();recalc();
</script>
"""

page = (HTML.replace("__WATCHJSON__", json.dumps(watch_js))
            .replace("__TIERSJSON__", json.dumps(tiers_js))
            .replace("__STAMP__", stamp)
            .replace("__ASOFPX__", asof_px)
            .replace("__BREACHLINE__", breach_line)
            .replace("__WATCHLINE__", watch_line)
            .replace("__GATE__", f"{GATE:.0f}"))
open(OUT, "w", encoding="utf-8").write(page)
print(f"rendered {len(tickers)} tickers | as-of {asof_px} | {breach_line}")
print("watch:", watch_line)
