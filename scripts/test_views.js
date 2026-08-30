// Verify the three-view split: routing, the row detail popup, the pick bar, and
// the sell list. The DOM stub is richer than the other harness because these
// features use querySelector and closest().
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const store = {}, els = {};
const mk = id => ({ id, value:'', textContent:'', innerHTML:'', checked:false, hidden:false,
  style:{}, title:'', dataset:{}, onclick:null, onkeydown:null, disabled:false,
  classList:{ toggle(){}, add(){}, remove(){} },
  addEventListener(){}, querySelector(){return null;}, querySelectorAll(){return [];},
  appendChild(){}, select(){}, focus(){}, closest(){return null;} });
const sandbox = {
  document:{ getElementById:id=>(els[id]=els[id]||mk(id)), querySelectorAll:()=>[],
    querySelector:()=>null, createElement:mk, addEventListener(){},
    body:{ style:{} } },
  localStorage:{ getItem:k=>(k in store?store[k]:null), setItem:(k,v)=>{store[k]=String(v);},
    removeItem:k=>{delete store[k];}, clear(){} },
  console, navigator:{clipboard:{writeText:async()=>{}}},
  location:{ hash:'' }, history:{ pushState(){} },
  window:{ claude:undefined, addEventListener(){}, scrollTo(){} },
  confirm:()=>true, alert:()=>{},
  btoa:s=>Buffer.from(s,'binary').toString('base64'),
  atob:s=>Buffer.from(s,'base64').toString('binary'),
  setTimeout, JSON, Math, Object, Array, String, Number, Boolean, Date, RegExp, Error,
  parseFloat, parseInt, isNaN, isFinite,
};
sandbox.globalThis = sandbox;
sandbox.window.localStorage = sandbox.localStorage;
sandbox.window.scrollTo = () => {};
sandbox.scrollTo = () => {};
vm.createContext(sandbox);
const EXPORT = ';globalThis.__X={showView:typeof showView!=="undefined"?showView:null,'
 + 'currentView:typeof currentView!=="undefined"?currentView:null,'
 + 'openDetail:typeof openDetail!=="undefined"?openDetail:null,'
 + 'closeDetail:typeof closeDetail!=="undefined"?closeDetail:null,'
 + 'renderPickBar:typeof renderPickBar!=="undefined"?renderPickBar:null,'
 + 'renderSell:typeof renderSell!=="undefined"?renderSell:null,'
 + 'quickPick:typeof quickPick!=="undefined"?quickPick:null,'
 + 'pickedList:typeof pickedList!=="undefined"?pickedList:null,'
 + 'trade:typeof trade!=="undefined"?trade:null,NAMES:typeof NAMES!=="undefined"?NAMES:null,'
 + 'F:typeof F!=="undefined"?F:null,ui:typeof ui!=="undefined"?ui:null,'
 + 'VIEWS:typeof VIEWS!=="undefined"?VIEWS:null,"$":typeof $!=="undefined"?$:null};';
try {
  scripts.forEach((sc,i)=>vm.runInContext(i===scripts.length-1? sc+EXPORT : sc, sandbox, {timeout:20000}));
  console.log('PARSE+RUN: ok');
} catch (e) { console.log('FAILED:', e.message); process.exit(1); }
const ctx = Object.assign({}, sandbox, sandbox.__X);

console.log('views declared:', JSON.stringify(ctx.VIEWS));
// routing
['list','trade','me'].forEach(v => {
  ctx.showView(v, false);
  const shown = ctx.VIEWS.filter(k => ctx.$('v-'+k).style.display === 'block');
  console.log('  showView(' + v + ') -> visible:', JSON.stringify(shown),
    '| exactly one:', shown.length === 1 && shown[0] === v);
});
sandbox.location.hash = '#trade';
console.log('  hash #trade resolves to:', ctx.currentView());
sandbox.location.hash = '#nonsense';
console.log('  unknown hash falls back to:', ctx.currentView());

// the row detail popup
setTimeout(() => {
  const top = ctx.NAMES.slice().sort((a,b)=>b[2]-a[2])[0];
  ctx.openDetail(top[0]);
  const body = ctx.$('modalbody').innerHTML;
  console.log('\ndetail for', top[0] + ':');
  console.log('  opened (modal not hidden):', ctx.$('modal').hidden === false);
  console.log('  has the six measures:', body.includes('The six measures'));
  console.log('  names the stock it touches:', body.includes('Stock it touches'));
  console.log('  has score and price stats:', body.includes('Score') && body.includes('Price'));
  // Committing moved to the Buy & sell page, so the detail picks but never trades.
  console.log('  has the pick action:', body.includes('data-dpick'));
  console.log('  cannot buy or sell from the detail:',
    !body.includes('data-dbuy') && !body.includes('data-dsell') && !body.includes('id="damt"'));
  console.log('  aria-labelled dialog:', /id="modaltitle"/.test(body));
  ctx.closeDetail();
  console.log('  closes:', ctx.$('modal').hidden === true);

  // pick bar and sell list
  ctx.quickPick('top10');
  ctx.renderPickBar();
  const pb = ctx.$('pickbar').innerHTML.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
  console.log('\npick bar:', pb.slice(0, 88));
  ctx.renderSell();
  console.log('sell list, nothing held:',
    ctx.$('sellbox').innerHTML.replace(/<[^>]+>/g,'').trim().slice(0, 60));
  ctx.trade(top[0], 'BUY', '250');
  setTimeout(() => {
    ctx.renderSell();
    const sb = ctx.$('sellbox').innerHTML;
    console.log('after buying 250 of', top[0] + ':',
      'row present:', sb.includes(top[0]), '| has a sell control:', sb.includes('data-ssell'));
    console.log('\nALL VIEW CHECKS DONE');
  }, 40);
}, 40);
