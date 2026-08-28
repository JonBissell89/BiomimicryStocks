// Headless validation of the console: parse the page, run its script against a
// minimal DOM stub, and exercise fund -> buy -> sell -> search -> leaderboard.
const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync(process.argv[2], 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
console.log('script blocks:', scripts.length);

const store = {};
function mkEl(id) {
  return {
    id, value: '', textContent: '', innerHTML: '', checked: false, style: {}, title: '',
    dataset: {}, onclick: null, disabled: false,
    addEventListener() {}, querySelector() { return null; },
    querySelectorAll() { return []; }, appendChild() {}, select() {},
  };
}
const els = {};
const document = {
  getElementById(id) { return (els[id] = els[id] || mkEl(id)); },
  querySelectorAll() { return []; },
  querySelector() { return null; },
  createElement(t) { return mkEl(t); },
  addEventListener() {},
};
const localStorage = {
  getItem: k => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v); },
  removeItem: k => { delete store[k]; },
  clear: () => { for (const k in store) delete store[k]; },
};
const sandbox = {
  document, localStorage, console,
  window: { claude: undefined },
  navigator: { clipboard: { writeText: async () => {} } },
  confirm: () => true,
  alert: () => {},
  btoa: s => Buffer.from(s, 'binary').toString('base64'),
  atob: s => Buffer.from(s, 'base64').toString('binary'),
  setTimeout, JSON, Math, Object, Array, String, Number, Boolean, Date, RegExp, Error, parseFloat, parseInt, isNaN,
};
sandbox.globalThis = sandbox;
sandbox.window.localStorage = localStorage;
vm.createContext(sandbox);

try {
  const EXPORT = ';globalThis.__X={NAMES:typeof NAMES!=="undefined"?NAMES:null,SIDX:typeof SIDX!=="undefined"?SIDX:null,ui:typeof ui!=="undefined"?ui:null,trade:typeof trade!=="undefined"?trade:null,lookup:typeof lookup!=="undefined"?lookup:null,render:typeof render!=="undefined"?render:null,myCard:typeof myCard!=="undefined"?myCard:null,snapshotMine:typeof snapshotMine!=="undefined"?snapshotMine:null,MARK:typeof MARK!=="undefined"?MARK:null,PX:typeof PX!=="undefined"?PX:null,allRows:typeof allRows!=="undefined"?allRows:null,rec:typeof rec!=="undefined"?rec:null,F:typeof F!=="undefined"?F:null,marketOf:typeof marketOf!=="undefined"?marketOf:null,mineAdded:typeof mineAdded!=="undefined"?mineAdded:null,buyAllocation:typeof buyAllocation!=="undefined"?buyAllocation:null,renderBoard:typeof renderBoard!=="undefined"?renderBoard:null,"$":typeof $!=="undefined"?$:null};';
  scripts.forEach((sc,i)=>vm.runInContext(i===scripts.length-1? sc+EXPORT : sc, sandbox, { timeout: 20000 }));
  console.log('PARSE+RUN: ok');
} catch (e) {
  console.log('FAILED:', e.message);
  process.exit(1);
}

const ctx = Object.assign({}, sandbox, sandbox.__X);
console.log('ranked names:', ctx.NAMES.length, '| search index:', Object.keys(ctx.SIDX).length);

// fund
ctx.$('fundbtn').onclick();
setTimeout(() => {
  const mine = JSON.parse(store.bsMine || '{}');
  console.log('after start -> cash:', mine.cash, '| txns:', (mine.txns || []).length);

  // buy $100 of the top-scoring name
  const top = ctx.NAMES.slice().sort((a, b) => b[2] - a[2])[0];
  ctx.$('amt_' + top[0]).value = '100';
  ctx.trade(top[0], 'BUY');
  setTimeout(() => {
    const m2 = JSON.parse(store.bsMine || '{}');
    const pos = m2.positions[top[0]];
    console.log('after buy', top[0], '-> shares:', pos && pos.shares.toFixed(4), '| cash:', m2.cash.toFixed(2));

    // sell half
    ctx.$('amt_' + top[0]).value = '50';
    ctx.trade(top[0], 'SELL');
    setTimeout(() => {
      const m3 = JSON.parse(store.bsMine || '{}');
      console.log('after sell -> shares:', m3.positions[top[0]].shares.toFixed(4), '| cash:', m3.cash.toFixed(2));

      // search
      ctx.$('q').value = 'TSLA';
      ctx.lookup();
      const res = ctx.$('qres').innerHTML;
      console.log('search TSLA ->', res.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 120));
      ctx.$('q').value = 'AAPL'; ctx.lookup();
      console.log('search AAPL ->', ctx.$('qres').innerHTML.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 120));
      ctx.$('q').value = 'WRTBY'; ctx.lookup();
      console.log('search WRTBY ->', ctx.$('qres').innerHTML.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 120));

      // add an off-list company, then buy it
      const priced = Object.keys(ctx.PX || {});
      const offList = priced.find(t => ctx.SIDX[t] && ctx.SIDX[t][1] !== 'R' && ctx.PX[t] > 0);
      if (!offList) { console.log('ADD-ROW: no priced off-list ticker available'); }
      else {
        const before = ctx.NAMES.length, rowsBefore = ctx.allRows().length;
        store.bsAdded = JSON.stringify([offList]);
        ctx.render();
        const rowsAfter = ctx.allRows().length;
        const row = ctx.rec(offList);
        console.log('add-row', offList, '-> rows', rowsBefore, '->', rowsAfter,
          '| tier:', row && row[ctx.F.tier], '| price:', row && row[ctx.F.px],
          '| name:', row && row[ctx.F.nm]);
        console.log('  NAMES untouched:', ctx.NAMES.length === before);
        console.log('  appears in table:', ctx.$('mktbody').innerHTML.indexOf(offList) >= 0,
          '| marked YOURS:', ctx.$('mktbody').innerHTML.indexOf('YOURS') >= 0);
        ctx.$('amt_' + offList).value = '75';
        ctx.trade(offList, 'BUY');
      }
      // market filter
      ctx.ui.mkt = 'ord'; ctx.render();
      const ordCount = (ctx.$('mktbody').innerHTML.match(/<tr/g) || []).length;
      ctx.ui.mkt = 'us'; ctx.render();
      const usCount = (ctx.$('mktbody').innerHTML.match(/<tr/g) || []).length;
      ctx.ui.mkt = 'all'; ctx.render();
      const allCount = (ctx.$('mktbody').innerHTML.match(/<tr/g) || []).length;
      console.log('market filter -> ord:', ordCount, 'us:', usCount, 'all:', allCount);

      // add / remove affordances must be visible without hunting
      const body = ctx.$('mktbody').innerHTML;
      console.log('Remove button on own rows:', body.indexOf('data-drop') >= 0,
        '| Sell on ranked rows:', body.indexOf('data-sell') >= 0,
        '| no duplicate add row in table:', body.indexOf('jumpadd') < 0);
      console.log('planner gone:', typeof ctx.buyAllocation !== 'function'
        && body.indexOf('data-wt') < 0);
      // removing a row the visitor added, after selling out of it
      if (offList) {
        const held = ctx.rec(offList) ? 1 : 0;
        store.bsAdded = '[]'; ctx.render();
        console.log('after remove -> rows:', ctx.allRows().length,
          '| gone from table:', ctx.$('mktbody').innerHTML.indexOf('>' + offList + '<') < 0);
        store.bsAdded = JSON.stringify([offList]); ctx.render();
      }

      // tracker: the visitor's own ledger must record a snapshot with benchmarks
      const m4 = JSON.parse(store.bsMine || '{}');
      const h = m4.history || [];
      console.log('history rows:', h.length,
        '| first row:', h[0] ? JSON.stringify(h[0]) : 'none');
      console.log('  benchmarks present -> spx:', !!(h[0] && h[0].spx != null),
        '| list:', !!(h[0] && h[0].list != null));
      const hb = ctx.$('histbody').innerHTML;
      console.log('  tracker table cols:', (hb.match(/<td/g) || []).length,
        '| renders:', hb.indexOf('<tr') >= 0);
      // a second call must not add a duplicate row for the same run
      ctx.snapshotMine();
      console.log('  no duplicate on re-snapshot:',
        (JSON.parse(store.bsMine).history || []).length === h.length);

      // leaderboard
      const card = ctx.myCard();
      console.log('scorecard length:', card.length, '| decodes:', JSON.parse(ctx.atob(card)).n !== undefined);
      console.log('leaderboard ->', ctx.$('leaderboard').innerHTML.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 120));
      console.log('ALL CHECKS DONE');
    }, 30);
  }, 30);
}, 30);
