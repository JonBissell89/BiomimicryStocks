"""Generate the Paper Ledger self-saving artifact page.

Reads engine_tiers.json (names) + paper_state.json (virtual portfolio state) +
live Yahoo prices. Appends a monthly valuation snapshot when due. The page lets
the owner buy/sell virtually and saves new versions of itself (artifact capability).
IMPORTANT for refreshes: sync paper_state.json from the published artifact FIRST
(Artifact read -> extract 'const STATE=...;') so user trades are never clobbered.
"""
import os
from paths import BUILD, DATA
import json, re, urllib.parse, warnings
from datetime import datetime, timezone
warnings.filterwarnings("ignore")
import pandas as pd
import yfinance as yf

DATA = DATA
OUT = os.path.join(BUILD, "paper_ledger.html")

eng = json.load(open(os.path.join(DATA, "engine_tiers.json"), encoding="utf-8"))
state = json.load(open(os.path.join(DATA, "paper_state.json"), encoding="utf-8"))

names = []
for t in eng["tiers"]:
    for n in t["names"]:
        names.append({"tk": n["tk"], "label": f'{n["nm"]} · {n["score"]}',
                      "tier": t["id"], "note": n.get("note", ""), "sofi": bool(n.get("sofi"))})
tickers = [n["tk"] for n in names] + ["^GSPC"]
px = yf.download(tickers, period="5d", progress=False, threads=True, auto_adjust=True)["Close"]
last = px.ffill().iloc[-1]
stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
spx = round(float(last.get("^GSPC")), 2) if pd.notna(last.get("^GSPC")) else None
for n in names:
    v = last.get(n["tk"])
    n["px"] = round(float(v), 2) if pd.notna(v) and v > 0 else None
prices = {n["tk"]: n["px"] for n in names}

# monthly snapshot: append if funded and last snapshot > 25 days old (or none)
if state.get("cash") is not None:
    total = state["cash"] + sum(p["shares"] * (prices.get(tk) or 0)
                                for tk, p in state.get("positions", {}).items())
    hist = state.setdefault("history", [])
    due = True
    if hist:
        lastd = datetime.strptime(hist[-1]["date"], "%Y-%m-%d")
        due = (datetime.now() - lastd).days > 25
    if due:
        hist.append({"date": today, "value": round(total, 2), "spx": spx})
        json.dump(state, open(os.path.join(DATA, "paper_state.json"), "w", encoding="utf-8"))
        print(f"snapshot appended: {today} value={total:,.2f} spx={spx}")

TEMPLATE = r"""<title>Paper Ledger</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --ground:#F7F9F8; --card:#FFFFFF; --ink:#16211F; --muted:#5C6B67;
  --accent:#1D5D51; --accent-soft:#E3EEEB; --warn:#A8663B; --warn-soft:#F6ECE4;
  --line:#DCE4E1; --chipbg:#EDF2F0; --good:#1D5D51; --bad:#A8663B;
  --serif:"Newsreader",Georgia,serif; --sans:"IBM Plex Sans",system-ui,sans-serif; --mono:"IBM Plex Mono",Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#101715; --card:#17201D; --ink:#E8EEEB; --muted:#93A39E;
    --accent:#5FA894; --accent-soft:#1C2E29; --warn:#D08B5C; --warn-soft:#2C231A;
    --line:#26332F; --chipbg:#1E2A26; --good:#5FA894; --bad:#D08B5C;
  }
}
:root[data-theme="dark"]{
  --ground:#101715; --card:#17201D; --ink:#E8EEEB; --muted:#93A39E;
  --accent:#5FA894; --accent-soft:#1C2E29; --warn:#D08B5C; --warn-soft:#2C231A;
  --line:#26332F; --chipbg:#1E2A26; --good:#5FA894; --bad:#D08B5C;
}
*{box-sizing:border-box}
body{background:var(--ground);color:var(--ink);font-family:var(--sans);margin:0;line-height:1.5;font-size:15px}
.wrap{max-width:980px;margin:0 auto;padding:40px 20px 80px}
header.hero{border-bottom:2px solid var(--ink);padding-bottom:20px;margin-bottom:24px;display:flex;flex-wrap:wrap;gap:18px;justify-content:space-between;align-items:end}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 8px}
h1{font-family:var(--serif);font-weight:500;font-size:clamp(28px,5vw,42px);line-height:1.05;margin:0}
.totbox{text-align:right}
.totbox .tv{font-family:var(--serif);font-size:34px;font-weight:600;font-variant-numeric:tabular-nums}
.totbox .tl{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.totbox .chg{font-family:var(--mono);font-size:13px}
.pos{color:var(--good)} .neg{color:var(--bad)}
.bar{display:flex;flex-wrap:wrap;gap:14px;margin:14px 0 22px;font-family:var(--mono);font-size:12.5px;color:var(--muted)}
.bar b{color:var(--ink)}
.panel{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:18px 20px;margin:16px 0}
.panel h3{font-family:var(--serif);font-size:17px;font-weight:600;margin:0 0 10px}
input[type=number]{font-family:var(--mono);font-size:14px;padding:6px 8px;border:1px solid var(--line);border-radius:4px;background:var(--ground);color:var(--ink);width:130px}
input[type=number]:focus{outline:2px solid var(--accent);outline-offset:1px}
button{font-family:var(--mono);font-size:12px;padding:6px 12px;border:1px solid var(--accent);border-radius:4px;background:var(--accent-soft);color:var(--accent);cursor:pointer}
button:hover{background:var(--accent);color:var(--card)}
button:disabled{opacity:.45;cursor:not-allowed}
button.sell{border-color:var(--warn);background:var(--warn-soft);color:var(--warn)}
button.sell:hover{background:var(--warn);color:var(--card)}
button:focus{outline:2px solid var(--accent);outline-offset:1px}
h2{font-family:var(--serif);font-weight:600;font-size:21px;margin:30px 0 8px}
.tablewrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:760px;font-size:13px}
th{font-family:var(--mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:middle;font-variant-numeric:tabular-nums;white-space:nowrap}
td.tk{font-family:var(--mono);font-weight:500}
td.nm{color:var(--muted);font-size:12px;max-width:230px;overflow:hidden;text-overflow:ellipsis}
td.r{text-align:right;font-family:var(--mono)}
.msg{font-family:var(--mono);font-size:12.5px;color:var(--warn);min-height:18px;margin:8px 0}
.note{background:var(--warn-soft);border-left:3px solid var(--warn);padding:10px 14px;border-radius:0 4px 4px 0;margin:18px 0;max-width:82ch;font-size:12.5px}
footer{margin-top:44px;border-top:2px solid var(--ink);padding-top:12px;color:var(--muted);font-size:12px;max-width:80ch}
.tierlabel{font-family:var(--mono);font-size:10px;color:var(--accent)}
</style>
<div class="wrap">
<header class="hero">
  <div>
    <p class="eyebrow">Simulation · virtual dollars · engine last run @@STAMP@@</p>
    <h1>Paper Ledger</h1>
  </div>
  <div class="totbox"><div class="tl">Total virtual value</div><div class="tv" id="total">—</div><div class="chg" id="totchg"></div></div>
</header>
<div class="bar" id="statusbar"></div>
<div class="panel" id="fundpanel" style="display:none">
  <h3>Fund the account (one time)</h3>
  <input type="number" id="fundamt" min="1" step="100" placeholder="virtual dollars">
  <button id="fundbtn">Fund</button>
  <div class="msg" id="fundmsg"></div>
</div>
<div class="msg" id="msg"></div>
<div class="panel" id="importpanel" style="display:none">
  <h3>Import allocation from the Allocation Arithmetic page</h3>
  <textarea id="allocin" rows="2" style="width:100%;font-family:var(--mono);font-size:12px;background:var(--ground);color:var(--ink);border:1px solid var(--line);border-radius:4px;padding:8px" placeholder="paste e.g. WRTBY=600;TSNLF=600;SBDHF=600;BB=840" aria-label="allocation import"></textarea>
  <div style="margin-top:8px"><button id="importbtn">Buy entire allocation</button> <span class="msg" id="importmsg" style="display:inline"></span></div>
  <div style="font-size:12px;color:var(--muted);margin-top:4px">Executes every listed name as a virtual buy at this page&rsquo;s stamped prices, in one saved action. Unknown tickers and names without prices are skipped and reported.</div>
</div>
<h2>Market · buy and sell at stamped prices</h2>
<div style="font-size:13px;margin:4px 0 8px"><label style="cursor:pointer"><input type="checkbox" id="sfonly" checked> <b>SoFi-available only</b> — hide OTC names my brokerage can't trade (hidden positions still count in totals)</label></div>
<div class="tablewrap"><table id="mkt">
<thead><tr><th>Tier</th><th>Ticker</th><th>Company · score</th><th style="text-align:right">Price</th><th style="text-align:right">Held (sh)</th><th style="text-align:right">Mkt value</th><th style="text-align:right">P/L</th><th>$ amount</th><th></th><th></th></tr></thead>
<tbody id="mktbody"></tbody>
</table></div>
<h2>Month over month</h2>
<div class="tablewrap"><table>
<thead><tr><th>Date</th><th style="text-align:right">Value</th><th style="text-align:right">Δ$ from start</th><th style="text-align:right">Δ% from start</th><th style="text-align:right">S&amp;P 500 Δ% (same span)</th></tr></thead>
<tbody id="histbody"></tbody>
</table></div>
<h2>Transactions</h2>
<div class="tablewrap"><table>
<thead><tr><th>Date</th><th>Action</th><th>Ticker</th><th style="text-align:right">Shares</th><th style="text-align:right">Price</th><th style="text-align:right">Amount</th></tr></thead>
<tbody id="txnbody"></tbody>
</table></div>
<div class="note"><b>How this works.</b> This is a simulation with virtual money — nothing here is a real trade or investment advice. Trades execute at the stamped refresh prices above (not live ticks). The page saves each action as a new version of itself; the monthly engine run reprices everything, appends the month-over-month row, and republishes. Names and tiers come from the framework engine (ranked names + sandbox, gate $20).</div>
<footer>Paper Ledger · companion to the Balanced Systems Framework · state is stored in the page itself and updated on each action · engine: Desktop\Stocks\tournament\data\ · S&amp;P baseline set at first engine snapshot after funding.</footer>
</div>
<script>
const STATE=%%STATE%%;
const NAMES=@@NAMES@@;
const SPX=@@SPX@@;
const TODAY='@@TODAY@@';
const TPL_ENC='@@TPLENC@@';
const $=id=>document.getElementById(id);
const fmt=n=>'$'+n.toLocaleString(undefined,{maximumFractionDigits:2,minimumFractionDigits:2});
const fmt0=n=>'$'+n.toLocaleString(undefined,{maximumFractionDigits:0});
let art=null, ready=false;
if(window.claude&&claude.use){claude.use('artifact').then(a=>{art=a;ready=true;syncButtons();}).catch(()=>{ready=true;syncButtons();});}
else{ready=true;}
function priceOf(tk){const n=NAMES.find(x=>x[0]===tk);return n?n[2]:null;}
function totalValue(s){let t=s.cash||0;for(const tk in (s.positions||{}))t+=(s.positions[tk].shares||0)*(priceOf(tk)||0);return t;}
function render(){
  const funded=STATE.cash!==null&&STATE.cash!==undefined;
  $('fundpanel').style.display=funded?'none':'block';
  $('importpanel').style.display=funded?'block':'none';
  const tot=funded?totalValue(STATE):0;
  $('total').textContent=funded?fmt(tot):'unfunded';
  if(funded&&STATE.start){const d=tot-STATE.start.cash;const p=100*d/STATE.start.cash;
    $('totchg').innerHTML='<span class="'+(d>=0?'pos':'neg')+'">'+(d>=0?'+':'')+fmt(Math.abs(d)).replace('$',(d>=0?'$':'-$'))+' ('+p.toFixed(2)+'%) since '+STATE.start.date+'</span>';}
  $('statusbar').innerHTML=funded?('cash <b>'+fmt(STATE.cash)+'</b> · positions <b>'+Object.keys(STATE.positions).filter(k=>STATE.positions[k].shares>0.0001).length+'</b> · started <b>'+(STATE.start?STATE.start.date:'—')+'</b> · '+(art?'saving enabled':'read-only view — open as owner on claude.ai to trade')):'Enter a virtual dollar amount to begin the simulation.';
  let h='';
  const sfOnly=$('sfonly')&&$('sfonly').checked;
  NAMES.forEach(n=>{
    const [tk,label,px,tier,sf]=n;
    const pos=(STATE.positions||{})[tk];
    if(sfOnly&&!sf&&!(pos&&pos.shares>0.0001))return;
    const sh=pos?pos.shares:0, cost=pos?pos.cost:0;
    const mv=sh*(px||0), pl=mv-cost;
    h+='<tr><td class="tierlabel">'+tier.toUpperCase()+'</td><td class="tk">'+tk+'</td><td class="nm">'+label+'</td>'+
       '<td class="r">'+(px?fmt(px):'n/a')+'</td>'+
       '<td class="r">'+(sh>0.0001?sh.toFixed(4):'—')+'</td>'+
       '<td class="r">'+(sh>0.0001?fmt(mv):'—')+'</td>'+
       '<td class="r '+(pl>=0?'pos':'neg')+'">'+(sh>0.0001?(pl>=0?'+':'−')+fmt(Math.abs(pl)).slice(1):'—')+'</td>'+
       '<td><input type="number" min="1" step="10" id="amt_'+tk+'" aria-label="dollar amount '+tk+'"></td>'+
       '<td><button data-buy="'+tk+'" '+(px?'':'disabled')+'>Buy</button></td>'+
       '<td><button class="sell" data-sell="'+tk+'" '+(sh>0.0001?'':'disabled')+'>Sell</button></td></tr>';
  });
  $('mktbody').innerHTML=h;
  let hh='';
  (STATE.history||[]).forEach(r=>{
    const d=r.value-(STATE.start?STATE.start.cash:r.value);
    const p=STATE.start?100*d/STATE.start.cash:0;
    const s0=(STATE.history[0]||{}).spx;
    const sp=(s0&&r.spx)?(100*(r.spx-s0)/s0):null;
    hh+='<tr><td>'+r.date+'</td><td class="r">'+fmt(r.value)+'</td><td class="r '+(d>=0?'pos':'neg')+'">'+(d>=0?'+':'−')+fmt(Math.abs(d)).slice(1)+'</td><td class="r '+(p>=0?'pos':'neg')+'">'+p.toFixed(2)+'%</td><td class="r">'+(sp===null?'—':sp.toFixed(2)+'%')+'</td></tr>';
  });
  $('histbody').innerHTML=hh||'<tr><td colspan="5" style="color:var(--muted)">No snapshots yet — the first appears at the next engine refresh after funding.</td></tr>';
  let th='';
  (STATE.txns||[]).slice(-25).reverse().forEach(t=>{
    th+='<tr><td>'+t.d+'</td><td>'+t.a+'</td><td class="tk">'+(t.tk||'—')+'</td><td class="r">'+(t.sh?t.sh.toFixed(4):'—')+'</td><td class="r">'+(t.px?fmt(t.px):'—')+'</td><td class="r">'+fmt(t.amt)+'</td></tr>';
  });
  $('txnbody').innerHTML=th||'<tr><td colspan="6" style="color:var(--muted)">No transactions yet.</td></tr>';
  bindButtons(); syncButtons();
}
function syncButtons(){document.querySelectorAll('button[data-buy],button[data-sell],#fundbtn').forEach(b=>{if(!art)b.title='Read-only: open as owner on claude.ai';});}
function bindButtons(){
  document.querySelectorAll('button[data-buy]').forEach(b=>b.onclick=()=>trade(b.dataset.buy,'BUY'));
  document.querySelectorAll('button[data-sell]').forEach(b=>b.onclick=()=>trade(b.dataset.sell,'SELL'));
}
if($('sfonly'))$('sfonly').addEventListener('change',render);
$('fundbtn').onclick=async()=>{
  const amt=parseFloat($('fundamt').value);
  if(!(amt>0)){$('fundmsg').textContent='Enter a positive amount.';return;}
  const s=JSON.parse(JSON.stringify(STATE));
  s.cash=amt; s.start={date:TODAY,cash:amt};
  s.txns.push({d:TODAY,a:'FUND',amt:amt});
  await save(s,'fundmsg');
};
async function trade(tk,act){
  const inp=$('amt_'+tk); const amt=parseFloat(inp.value); const px=priceOf(tk);
  if(!(amt>0)||!px){$('msg').textContent='Enter a positive $ amount for '+tk+'.';return;}
  const s=JSON.parse(JSON.stringify(STATE));
  s.positions=s.positions||{};
  if(act==='BUY'){
    if(amt>s.cash+0.001){$('msg').textContent='Not enough virtual cash ('+fmt(s.cash)+').';return;}
    const sh=amt/px;
    const p=s.positions[tk]||{shares:0,cost:0};
    p.shares+=sh; p.cost+=amt; s.positions[tk]=p; s.cash-=amt;
    s.txns.push({d:TODAY,a:'BUY',tk:tk,sh:sh,px:px,amt:amt});
  }else{
    const p=s.positions[tk];
    if(!p||p.shares<0.0001){$('msg').textContent='No position in '+tk+'.';return;}
    const sh=Math.min(p.shares,amt/px);
    const proceeds=sh*px;
    p.cost=p.cost*(1-sh/p.shares); p.shares-=sh;
    if(p.shares<0.0001){p.shares=0;p.cost=0;}
    s.cash+=proceeds;
    s.txns.push({d:TODAY,a:'SELL',tk:tk,sh:sh,px:px,amt:proceeds});
  }
  await save(s,'msg');
}
$('importbtn').onclick=async()=>{
  const raw=($('allocin').value||'').trim();
  if(!raw){$('importmsg').textContent='Paste an allocation string first.';return;}
  const s=JSON.parse(JSON.stringify(STATE));
  s.positions=s.positions||{};
  let spent=0, bought=0; const skipped=[];
  raw.split(/[;,\n]+/).forEach(pair=>{
    const m=pair.trim().match(/^([A-Za-z.\-]+)\s*=\s*\$?([0-9.]+)$/);
    if(!m){if(pair.trim())skipped.push(pair.trim());return;}
    const tk=m[1].toUpperCase(), amt=parseFloat(m[2]), px=priceOf(tk);
    if(!(amt>0)||!px){skipped.push(tk);return;}
    if(spent+amt>s.cash+0.001){skipped.push(tk+' (insufficient cash)');return;}
    const sh=amt/px;
    const p=s.positions[tk]||{shares:0,cost:0};
    p.shares+=sh;p.cost+=amt;s.positions[tk]=p;
    s.txns.push({d:TODAY,a:'BUY',tk:tk,sh:sh,px:px,amt:amt});
    spent+=amt;bought++;
  });
  if(!bought){$('importmsg').textContent='Nothing bought'+(skipped.length?' — skipped: '+skipped.join(', '):'.');return;}
  s.cash-=spent;
  $('importmsg').textContent='Buying '+bought+' names for '+fmt(spent)+(skipped.length?' (skipped: '+skipped.join(', ')+')':'')+' …';
  await save(s,'importmsg');
};
async function save(s,msgId){
  if(!art){$(msgId).textContent='Read-only view — saving requires opening this page as its owner on claude.ai.';return;}
  $(msgId).textContent='Saving…';
  const body=decodeURIComponent(TPL_ENC)
    .replace('%%'+'STATE'+'%%',JSON.stringify(s))
    .replace('@@'+'TPLENC'+'@@',TPL_ENC);
  const doc='<!doctype html>\n<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'+body+'</body></html>';
  try{await art.publish(doc);$(msgId).textContent='Saved.';}
  catch(e){
    const c=(e&&e.code)||'';
    if(c==='conflict'){$(msgId).textContent='A newer version exists — reloading.';}
    else if(c==='not_writer'||c==='not_granted'){$(msgId).textContent='Read-only: only the owner can trade here.';}
    else{$(msgId).textContent='Save failed ('+(c||'error')+') — try again.';}
  }
}
render();
</script>
"""

tpl = (TEMPLATE
       .replace("@@NAMES@@", json.dumps([[n["tk"], n["label"], n["px"], n["tier"], n["sofi"]] for n in names]))
       .replace("@@SPX@@", json.dumps(spx))
       .replace("@@TODAY@@", today)
       .replace("@@STAMP@@", stamp))
tpl_enc = urllib.parse.quote(tpl, safe="")
page = tpl.replace("%%STATE%%", json.dumps(state)).replace("@@TPLENC@@", tpl_enc)
open(OUT, "w", encoding="utf-8").write(page)
print(f"ledger rendered: {len(names)} names, stamp {stamp}, spx {spx}, page {len(page)//1024}KB")
