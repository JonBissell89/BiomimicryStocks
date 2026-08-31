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
    focus() {}, closest() { return null; }, hidden: false,
    classList: { toggle() {}, add() {}, remove() {} },
  };
}
const els = {};
const document = {
  body: { style: {} },
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
  window: { claude: undefined, addEventListener() {}, scrollTo() {} },
  navigator: { clipboard: { writeText: async () => {} } },
  confirm: () => true,
  alert: () => {},
  btoa: s => Buffer.from(s, 'binary').toString('base64'),
  atob: s => Buffer.from(s, 'base64').toString('binary'),
  location: { hash: '' }, history: { pushState() {} }, scrollTo() {},
  setTimeout, JSON, Math, Object, Array, String, Number, Boolean, Date, RegExp, Error, parseFloat, parseInt, isNaN, isFinite,
};
sandbox.globalThis = sandbox;
sandbox.window.localStorage = localStorage;
vm.createContext(sandbox);

try {
  const EXPORT = ';globalThis.__X={NAMES:typeof NAMES!=="undefined"?NAMES:null,SIDX:typeof SIDX!=="undefined"?SIDX:null,ui:typeof ui!=="undefined"?ui:null,trade:typeof trade!=="undefined"?trade:null,lookup:typeof lookup!=="undefined"?lookup:null,render:typeof render!=="undefined"?render:null,myCard:typeof myCard!=="undefined"?myCard:null,quickPick:typeof quickPick!=="undefined"?quickPick:null,pickedList:typeof pickedList!=="undefined"?pickedList:null,basketPlan:typeof basketPlan!=="undefined"?basketPlan:null,buyBasket:typeof buyBasket!=="undefined"?buyBasket:null,gateOf:typeof gateOf!=="undefined"?gateOf:null,snapshotMine:typeof snapshotMine!=="undefined"?snapshotMine:null,MARK:typeof MARK!=="undefined"?MARK:null,PX:typeof PX!=="undefined"?PX:null,allRows:typeof allRows!=="undefined"?allRows:null,rec:typeof rec!=="undefined"?rec:null,F:typeof F!=="undefined"?F:null,marketOf:typeof marketOf!=="undefined"?marketOf:null,mineAdded:typeof mineAdded!=="undefined"?mineAdded:null,buyAllocation:typeof buyAllocation!=="undefined"?buyAllocation:null,renderBoard:typeof renderBoard!=="undefined"?renderBoard:null,"$":typeof $!=="undefined"?$:null,IMB:typeof IMB!=="undefined"?IMB:null,renderImbalance:typeof renderImbalance!=="undefined"?renderImbalance:null};';
  scripts.forEach((sc,i)=>vm.runInContext(i===scripts.length-1? sc+EXPORT : sc, sandbox, { timeout: 20000 }));
  console.log('PARSE+RUN: ok');
} catch (e) {
  console.log('FAILED:', e.message);
  process.exit(1);
}

const ctx = Object.assign({}, sandbox, sandbox.__X);
console.log('ranked names:', ctx.NAMES.length, '| search index:', Object.keys(ctx.SIDX).length);

// the $5,000 should already be there on arrival, with no click
setTimeout(() => {
  const mine = JSON.parse(store.bsMine || '{}');
  console.log('auto-funded on load -> cash:', mine.cash, '| txns:', (mine.txns || []).length,
    '| start recorded:', !!mine.start);
  console.log('  no start button in the page:', !/id="fundbtn"/.test(html));

  // buy $100 of the top-scoring name
  // The list page no longer carries per-row amount boxes, so drive trade()
  // with an explicit amount the way the trading page and the quick picks do.
  const top = ctx.NAMES.slice().sort((a, b) => b[2] - a[2])[0];
  ctx.trade(top[0], 'BUY', 100);
  setTimeout(() => {
    const m2 = JSON.parse(store.bsMine || '{}');
    const pos = m2.positions[top[0]];
    console.log('after buy', top[0], '-> shares:', pos && pos.shares.toFixed(4), '| cash:', m2.cash.toFixed(2));

    // sell half
    ctx.trade(top[0], 'SELL', 50);
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
        ctx.trade(offList, 'BUY', 75);
      }
      // market filter
      ctx.ui.mkt = 'ord'; ctx.render();
      const ordCount = (ctx.$('mktbody').innerHTML.match(/<tr/g) || []).length;
      ctx.ui.mkt = 'us'; ctx.render();
      const usCount = (ctx.$('mktbody').innerHTML.match(/<tr/g) || []).length;
      ctx.ui.mkt = 'all'; ctx.render();
      const allCount = (ctx.$('mktbody').innerHTML.match(/<tr/g) || []).length;
      console.log('market filter -> ord:', ordCount, 'us:', usCount, 'all:', allCount);

      // the basket: quick picks, even split, and the actual bulk purchase
      const cashBefore = JSON.parse(store.bsMine).cash;
      ctx.quickPick('need');
      const nNeed = ctx.pickedList().length;
      const needs = new Set(ctx.pickedList().map(n => String(n[ctx.F.need] || '?').split(' · ')[0]));
      console.log('quick pick "one of each need" ->', nNeed, 'companies,',
        needs.size, 'distinct needs | one per need:', nNeed === needs.size);
      ctx.quickPick('top10');
      console.log('quick pick "top 10" ->', ctx.pickedList().length,
        '| all gate-passing:', ctx.pickedList().every(n => ctx.gateOf(n) !== 'fail'));
      ctx.ui.spend = '1000'; ctx.render();
      const plan = ctx.basketPlan();
      const each = plan.rows.length ? plan.rows[0][1] : 0;
      console.log('  split $1000 ->', plan.rows.length, 'rows at', each.toFixed(2),
        'each | total', plan.total.toFixed(2), '| even:',
        plan.rows.every(r => Math.abs(r[1] - each) < 0.01));
      console.log('  summary reads:',
        ctx.$('bksum').innerHTML.replace(/<[^>]+>/g, '').trim().slice(0, 105));
      ctx.buyBasket();

      // add / remove affordances must be visible without hunting
      const body = ctx.$('mktbody').innerHTML;
      console.log('Remove button on own rows:', body.indexOf('data-drop') >= 0,
        '| no buying from the list:', body.indexOf('data-buy') < 0
          && body.indexOf('data-sell') < 0 && body.indexOf('id="amt_') < 0,
        '| no duplicate add row in table:', body.indexOf('jumpadd') < 0);
      // Layer 0 must be present, rendered, and correlated: 21 systems, the
      // required-correction chain visible, every company chip a real ticker,
      // and the no-company gaps stated rather than hidden.
      const imb = ctx.IMB, im = ctx.$('imbmap').innerHTML;
      const rows = (im.match(/data-imb="/g) || []).length;
      const chips = [...im.matchAll(/data-imbco="([A-Z0-9]+)"/g)].map(m => m[1]);
      const known = new Set(ctx.NAMES.map(n => n[0]));
      const mapped = new Set(imb ? imb.systems.flatMap(s => s.tickers) : []);
      console.log('layer 0 -> systems in data:', imb && imb.systems.length,
        '| rows rendered:', rows,
        '| chain shown:', im.indexOf('Required correction') >= 0 && im.indexOf('Correction clock') >= 0);
      console.log('  company chips:', chips.length,
        '| all real tickers:', chips.every(t => known.has(t)),
        '| every company traced to an imbalance:', [...known].every(t => mapped.has(t)),
        '| gaps stated:', (im.match(/clears the screen on this correction yet/g) || []).length);
      console.log('  labels are the framework vocabulary:',
        im.indexOf('frm-overshoot') >= 0 && im.indexOf('frm-deficit') >= 0
          && im.indexOf('dir-worsening') < 0 && im.indexOf('improving') < 0,
        '| envelopes shown:', (im.match(/Natural rhythm and envelope/g) || []).length);
      // The About table is the ranking and nothing else: no picking, no holdings,
      // no filter on what you own. This kept creeping back, so it is asserted.
      console.log('  no portfolio state on About:',
        body.indexOf('data-pick') < 0 && body.indexOf('data-l="Held"') < 0
          && body.indexOf('data-l="Value"') < 0 && body.indexOf('data-l="P/L"') < 0,
        '| no Only-what-I-own filter:', !/id="holdonly"/.test(html));
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
