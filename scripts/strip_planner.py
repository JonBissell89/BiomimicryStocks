# -*- coding: utf-8 -*-
"""Owner ruling: the lump-sum planner is removed. Strip its JS, its CSS, and the
weight bookkeeping that only existed to feed it, so nothing dangles."""
import os
from paths import SCRIPTS
P = os.path.join(SCRIPTS, "refresh_app.py")
s = open(P, encoding="utf-8").read()
n = len(s)

CUTS = [
# --- state / helpers -------------------------------------------------------
("let ui=null,art=null,lastAlloc=[];",
 "let ui=null,art=null;"),
('function uiDefaults(){const s={sleeve:"",p:[60,28,10,0],wt:{},mkt:"all",cap:99999,minScore:0,holdOnly:false,sort:"score"};\n'
 '  NAMES.forEach(n=>{s.wt[n[0]]=(n[F.tier]==="t4"||n[F.tier]==="exit"||gateOf(n)==="fail")?0:1;});return s;}',
 'function uiDefaults(){return {mkt:"all",cap:99999,minScore:0,holdOnly:false,sort:"score"};}'),
("function uiLoad(){try{const r=localStorage.getItem('bsUI');if(r){const s=JSON.parse(r);const d=uiDefaults();return {...d,...s,wt:{...d.wt,...s.wt}};}}catch(e){}return uiDefaults();}",
 "function uiLoad(){try{const r=localStorage.getItem('bsUI');if(r)return {...uiDefaults(),...JSON.parse(r)};}catch(e){}return uiDefaults();}"),
('// Added companies default to a normal share so the "what I added" slider does something.\n'
 "function wtOf(tk){const w=ui.wt[tk];return w===undefined?1:(+w||0);}\n", ""),
("  $('planpanel').style.display=funded?'block':'none';\n", ""),
# --- wiring ----------------------------------------------------------------
("$('useall').onclick=()=>{ui.sleeve=String(Math.floor((L().cash||0)*100)/100);pushUI();render();};\n", ""),
("$('sleeve').addEventListener('input',()=>{ui.sleeve=$('sleeve').value;render();});\n", ""),
('["p1","p2","p3","p4"].forEach((id,i)=>$(id).addEventListener(\'input\',()=>{ui.p[i]=+$(id).value;render();}));\n', ""),
("$('reset').addEventListener('click',()=>{ui=uiDefaults();pushUI();render();});\n", ""),
("$('buyallocbtn').addEventListener('click',buyAllocation);\n", ""),
("function pushUI(){$('sleeve').value=ui.sleeve;$('mktsel').value=ui.mkt||'all';",
 "function pushUI(){$('mktsel').value=ui.mkt||'all';"),
('  $(\'sortsel\').value=ui.sort;["p1","p2","p3","p4"].forEach((id,i)=>$(id).value=ui.p[i]);}',
 "  $('sortsel').value=ui.sort;}"),
# --- CSS -------------------------------------------------------------------
(".slider-row{display:grid;grid-template-columns:96px 1fr 46px;gap:8px;align-items:center;margin:5px 0}\n", ""),
(".slider-row .sl{font-family:var(--mono);font-size:11px}\n", ""),
(".slider-row .sv{font-family:var(--mono);font-size:11.5px;text-align:right}\n", ""),
(".plangrid{display:grid;grid-template-columns:210px 1fr;gap:18px;align-items:start}\n", ""),
("@media(max-width:700px){.plangrid{grid-template-columns:1fr}}\n", ""),
]
missing = []
for a, b in CUTS:
    if a in s:
        s = s.replace(a, b, 1)
    else:
        missing.append(a.strip().split("\n")[0][:60])

# buyAllocation is a whole function: cut from its signature to the line before startFund
i = s.find("async function buyAllocation(){")
j = s.find("async function startFund(", i)
if i > 0 and j > i:
    s = s[:i] + s[j:]
else:
    missing.append("buyAllocation block")

# planbox/planrow css block
for line in [".planbox{", ".planrow{", ".planrow:last-child{", ".planrow.head{"]:
    k = s.find(line)
    if k > 0:
        e = s.find("\n", k)
        s = s[:k] + s[e + 1:]
    else:
        missing.append(line)

open(P, "w", encoding="utf-8").write(s)
print(f"removed {n - len(s)} chars")
print("NOT FOUND:", missing if missing else "none")
for tok in ["lastAlloc", "buyAllocation", "ui.sleeve", "ui.wt", "wtOf(", "planpanel",
            "plansum", "planbreak", "plangrid", "slider-row", "planbox", "planrow"]:
    c = s.count(tok)
    print(f"  {tok:<16s} {c}" + ("   <-- still referenced" if c else ""))
