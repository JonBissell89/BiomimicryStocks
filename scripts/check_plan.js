const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const store = {}, els = {};
function mk(id) { return { id, value: '', textContent: '', innerHTML: '', checked: false, style: {}, dataset: {}, title: '', disabled: false, addEventListener() {}, querySelector: () => null, querySelectorAll: () => [], appendChild() {}, select() {} }; }
const document = { getElementById: id => els[id] = els[id] || mk(id), querySelectorAll: () => [], querySelector: () => null, createElement: t => mk(t), addEventListener() {} };
const localStorage = { getItem: k => k in store ? store[k] : null, setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; }, clear() {} };
const sb = { document, localStorage, console, window: {}, navigator: { clipboard: { writeText: async () => {} } }, confirm: () => true, btoa: s => Buffer.from(s, 'binary').toString('base64'), atob: s => Buffer.from(s, 'base64').toString('binary'), setTimeout, JSON, Math, Object, Array, String, Number, Boolean, Date, RegExp, Error, parseFloat, parseInt, isNaN };
sb.globalThis = sb; vm.createContext(sb);
const EX = ';globalThis.__X={ui:ui,render:render,dollar:$,startFund:startFund};';
scripts.forEach((sc, i) => vm.runInContext(i === scripts.length - 1 ? sc + EX : sc, sb));
const X = sb.__X;
X.startFund('fundmsg');
setTimeout(() => {
  X.ui.sleeve = '2000'; X.render();
  console.log('PLAN SUMMARY:', X.dollar('plansum').innerHTML.replace(/<[^>]+>/g, '').trim());
  const bd = X.dollar('planbreak').innerHTML
    .replace(/<div class="planrow head">/g, '\n== ')
    .replace(/<div class="planrow">/g, '\n   ')
    .replace(/<[^>]+>/g, ' ').replace(/[ \t]+/g, ' ');
  console.log('BREAKDOWN:');
  console.log(bd.split('\n').slice(0, 16).join('\n'));
  console.log('   ... (' + (bd.split('\n').length - 1) + ' lines total)');
  console.log('MONEYBAR:', X.dollar('moneybartext').innerHTML.replace(/<[^>]+>/g, '').trim().slice(0, 160));
}, 40);
