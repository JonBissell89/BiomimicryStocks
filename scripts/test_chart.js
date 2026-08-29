// The live ledger has one snapshot, so the chart's empty state is all you would
// see. Inject a plausible multi-week history and confirm the drawing is sane:
// three polylines, a zero guide, endpoint dots, and a legend that agrees with
// the last value of each series.
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const store = {};
const els = {};
const mk = id => ({ id, value:'', textContent:'', innerHTML:'', checked:false, style:{}, title:'',
  dataset:{}, onclick:null, onkeydown:null, disabled:false, hidden:false,
  classList:{toggle(){},add(){},remove(){}},
  addEventListener(){}, querySelector(){return null;},
  querySelectorAll(){return [];}, appendChild(){}, select(){}, focus(){}, closest(){return null;} });
const sandbox = {
  document:{ getElementById:id=>(els[id]=els[id]||mk(id)), querySelectorAll:()=>[],
             querySelector:()=>null, createElement:mk, addEventListener(){},
             body:{style:{}} },
  localStorage:{ getItem:k=>(k in store?store[k]:null), setItem:(k,v)=>{store[k]=String(v);},
                 removeItem:k=>{delete store[k];}, clear(){} },
  console, window:{claude:undefined,addEventListener(){},scrollTo(){}},
  navigator:{clipboard:{writeText:async()=>{}}},
  location:{hash:''}, history:{pushState(){}}, scrollTo(){},
  confirm:()=>true, alert:()=>{}, btoa:s=>Buffer.from(s,'binary').toString('base64'),
  atob:s=>Buffer.from(s,'base64').toString('binary'),
  setTimeout, JSON, Math, Object, Array, String, Number, Boolean, Date, RegExp, Error,
  parseFloat, parseInt, isNaN, isFinite,
};
sandbox.globalThis = sandbox; sandbox.window.localStorage = sandbox.localStorage;
vm.createContext(sandbox);
const EXPORT = ';globalThis.__X={renderChart:typeof renderChart!=="undefined"?renderChart:null,'
  + 'sparkline:typeof sparkline!=="undefined"?sparkline:null,SPARK:typeof SPARK!=="undefined"?SPARK:null,'
  + 'MINE:typeof MINE!=="undefined"?MINE:null,"$":typeof $!=="undefined"?$:null};';
scripts.forEach((sc,i)=>vm.runInContext(i===scripts.length-1? sc+EXPORT : sc, sandbox, {timeout:20000}));
const ctx = Object.assign({}, sandbox, sandbox.__X);

// six weeks: you beat the list early then give it back, the index drifts up
const hist = [
  {date:'2026-08-29', value:5000, spx:7700, list:100},
  {date:'2026-09-05', value:5120, spx:7745, list:101.2},
  {date:'2026-09-12', value:5260, spx:7690, list:100.4},
  {date:'2026-09-19', value:5180, spx:7810, list:102.9},
  {date:'2026-09-26', value:5395, spx:7855, list:103.6},
  {date:'2026-10-03', value:5310, spx:7902, list:104.8},
];
ctx.MINE.cash = 100; ctx.MINE.start = {date:'2026-08-29', cash:5000};
ctx.MINE.history = hist;
ctx.renderChart();
const svg = ctx.$('chart').innerHTML;

const polys = (svg.match(/<polyline/g) || []).length;
const dots  = (svg.match(/<circle/g) || []).length;
console.log('polylines:', polys, '(expect 3)');
console.log('endpoint dots:', dots, '(expect 3)');
console.log('has zero guide:', /opacity="0\.35"/.test(svg));
console.log('has date labels:', svg.includes('2026-08-29') && svg.includes('2026-10-03'));
console.log('has aria-label:', /aria-label="[^"]{30,}"/.test(svg));
console.log('no NaN in path data:', !/NaN/.test(svg));
const legend = svg.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
console.log('legend:', legend.slice(-90));
// legend percentages must match the arithmetic
const youPct = 100*(hist[5].value-hist[0].value)/hist[0].value;
const listPct = 100*(hist[5].list-hist[0].list)/hist[0].list;
const spxPct = 100*(hist[5].spx-hist[0].spx)/hist[0].spx;
console.log('you should read', youPct.toFixed(2)+'%,',
            'list', listPct.toFixed(2)+'%,', 'spx', spxPct.toFixed(2)+'%');
console.log('  all three present:',
  svg.includes(youPct.toFixed(2)) && svg.includes(listPct.toFixed(2)) && svg.includes(spxPct.toFixed(2)));

// coordinates must sit inside the viewBox
const nums = [...svg.matchAll(/points="([^"]+)"/g)].flatMap(m=>m[1].split(' ').map(p=>p.split(',').map(Number)));
const outside = nums.filter(([x,y])=>x<0||x>720||y<0||y>230);
console.log('points outside the viewBox:', outside.length);

// one-snapshot fallback
ctx.MINE.history = [hist[0]];
ctx.renderChart();
console.log('single-snapshot state:', ctx.$('chart').innerHTML.replace(/<[^>]+>/g,'').trim().slice(0,80));

// sparklines
const keys = Object.keys(ctx.SPARK||{});
const s = ctx.sparkline(keys[0]);
console.log('\nsparkline names:', keys.length, '| sample renders:', s.includes('<polyline'),
            '| no NaN:', !/NaN/.test(s));
console.log('unknown ticker returns empty:', ctx.sparkline('ZZZZ') === '');
