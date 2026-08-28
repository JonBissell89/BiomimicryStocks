# Tournament Runbook: best practices and known gotchas
Distilled from the Aug 27, 2026 full run (15,797 companies, ~24h wall-clock including
two session-limit outages). Target for the next full run: **2–4 hours**.

## Why the first run took 24+ hours
1. **Serial profile fetches**: 6,022 Yahoo `get_info` calls at ~0.8s each ≈ 80 min, run twice
   in places (repair passes). 2. **Session-limit kills**: two multi-agent waves (8 R2 judges,
   13 R4 researchers, 9 final verifiers) were killed mid-flight by usage-limit resets and had
   to be inventoried and relaunched. 3. **Serial verification**: final-round deep passes were
   agent-bound and web-search heavy. 4. **Rework**: empty-description repair, ADR-price
   corrections, and buyout discoveries all happened late, forcing re-verification.

## Speedups for the next full run
- **Cache-first**: `profiles.jsonl` is resumable, refetch only entries older than the run
  date or missing. A quarterly re-run refetches ~10–20%, not 100%.
- **Thread the fetches**: yfinance info calls tolerate 6–8 worker threads → 80 min → ~12 min.
  Prices always via batched `yf.download` (500/chunk), never per-ticker.
- **Persist verdicts**: R2 judgments only change on material business change. Re-judge only:
  new listings, name/segment changes, and companies whose revenue/margins moved >25%.
  Everything else carries forward with its recorded verdict.
- **Buyout/corporate-action check in Round 3, not the final round**: five finalists were
  mid-buyout (InPost, Penumbra, IHS, RLLWF, PSI); catching that early saves deep research.
- **Home-exchange prices from the start**: OTC F-share prints are stale. The engine should
  carry `home_ticker` + FX pair per thin name (e.g. SBDHF→1414.T×JPYUSD) and compute implied
  USD directly. (TODO: add to engine + refresh scripts.)
- **Repair-all-empties, low threshold**: any empty business description above the $25M
  viability floor gets one immediate retry + judgment, never a "no verifiable description"
  cut above that bar (the MVIS/$100M-threshold gotcha).
- **Never let a computed layer decide a gate.** `v2_inputs.py` produced wrong gate data in both
  directions on its first run (SHLS falsely flagged out of cash against $67.2M liquidity; DMTRF
  falsely cleared while actually failing on +34.8% dilution). Its dilution flag was measured
  afterward against six known-truth names: it caught both real failures and cleared both clean
  names, but also flagged SHLS and CRMD, whose share counts rose through an Up-C class conversion
  and an acquisition respectively. Full recall, poor precision. Computed inputs tell a researcher
  where to read; the filing decides.
- **Launch all agent waves at once with incremental file writes**: resumability beat
  scheduling; the inventory-then-relaunch pattern (count rows per output file, relaunch only
  gaps) recovered both outages losslessly. Keep every agent appending per-item.

## Known data-source gotchas
- NASDAQ screener API needs browser headers + Origin/Referer; returns all NASDAQ/NYSE/AMEX.
- stockanalysis.com API endpoints 404 (dead as of Aug 2026). OTC Markets bot-blocks scripts.
- Yahoo screener (`yf.screen`, exchange=PNK) covers ~9.5k OTC names, 250/page.
- SEC company_tickers.json needs a UA with contact email; ~40% of SEC-only tickers don't trade.
- Yahoo `get_info` intermittently returns empty summaries for majors (ABT, MMM), always retry.
- ADR vs F-share: Y-suffix = ADR (SoFi carries a curated set); F-suffix = foreign ordinary
  (not on SoFi). Availability flags are set empirically only (fill or in-app check).
- Dual listings survive name-dedup (TEVA/TEVJF etc.), keep the known-pairs drop list.

## Architecture (post-v2 rebuild, Aug 28 2026)
- **The scoring rubric is `V2_RUBRIC.md`, stock-and-flow.** The v1 eight-dimension scorecard is
  retired; `data/engine_tiers_v1_backup.json` keeps it for provenance only, never score against it.
  Six measures on 100: A stock 20 (moat deduction lives here), B flow 25, C loop 20 (C1 sign +
  C2 coupling), D growth 15 (replication + contact inhibition + clean exit), E buffer 10,
  F clock 10. **Survivability is a GATE, not a dimension.**
- `data/engine_tiers.json`, single source of truth: 53 graded names in tiers t1/t2/t3/t4/exit.
  Each carries `dims{A,B,C1,C2,D_rep,D_inhib,D_exit,E,F_clock,F_now}`, `score_base` (= sum of
  dims), `jx_penalty`, `score` (= base + penalty), `gate`, `stock`, `loop`, `coupling`, `clock`,
  `evidence`, `prev_score`, plus `_rubric`, `_calibration`, `_gate_rule`, `_premise`, `_clock`,
  `_rulings`, `removed[]`.
- Price is a **view filter**; membership never changes with price. The `gate` value at the top
  level is only the default price view, unrelated to the survivability gate on each name.
- **Tier bands are frozen at 80 / 74 / 69 / 65.** They were deliberately held when v2 dropped the
  mean 7 points. Never slide them to keep tier populations stable; that reproduces the previous
  answer by arithmetic. See `_calibration` in the engine.
- All 53 names are scored to the same depth now. The old `depth: deep|light` split is gone.
- Pages: `refresh_app.py` renders the ONE console FROM the engine; republish to the fixed artifact
  URL. Ledger state syncs FROM the published artifact BEFORE any regeneration.
- Verification chain, run in this order and all must be clean before publishing:
  `audit_engine_v2.py` (arithmetic, ranges, completeness, tier bands, em dashes) →
  `build_search_index.py` → `fill_price_cache.py` → `refresh_app.py` →
  `check_page.py` (page hygiene + SVG geometry) → `check_structure.py` (sections and controls) →
  `validate_console.js <page path>` (headless fund/buy/sell/search/add-row/filter/plan).
- **`price_cache.json` prices the searchable universe**, so a visitor can add and buy companies
  that never made the list. **Yahoo rate-limits sustained bulk quoting hard**: an isolated
  400-ticker chunk prices 98%, the same code under continuous load prices 22%, and coverage
  collapses uniformly across ticker classes rather than only on obscure names. Pacing and
  repeated passes are the fix, not bigger chunks. Both fillers write per chunk, so they resume
  and never restart, and the cache persists between months so coverage compounds.
  - **Run `fill_priority_prices.py` first.** It walks the universe largest-first by market cap.
    Total coverage percentage is the wrong target: nobody types a $4M OTC shell, and a visitor
    who types TSLA and gets no price experiences the feature as broken. Cap order fixes the
    cases that matter in the first few chunks.
  - `fill_price_cache.py` then grinds the long tail in converging passes with escalating
    backoff, stopping when a pass recovers under 50 names.
  - Check `coverage_by_class.py` afterwards. Unpriced names stay addable to the table but not
    buyable, and the page says so plainly.
- **`refresh_app.py` retries the 53 ranked prices with backoff and falls back to the cache**,
  because a universe fill running beforehand will otherwise leave every ranked price at zero and
  silently ship a dead page. It prints a WARNING naming any ranked name it still could not
  price. Never publish past that warning.
- **Two scheduled jobs, deliberately split by what actually changes at that cadence:**
  - `weekly-house-rebalance` (Mondays 9:00 AM): prices and the house book only. Syncs the
    ledger from the published artifact, tops up the price cache, rebalances the console's own
    $5,000, rebuilds, republishes, logs to `logs/weekly_house_YYYY-MM.md`. **Never touches
    engine_tiers.json.** Filings do not change weekly, so scores must not either.
  - `monthly-framework-reverify` (1st, 9:00 AM): the judgment run. Gates re-checked against
    filings, tripwires, score and tier changes on verified facts, full price-cache fill,
    republish, dated log. This is the only job allowed to change a score.
- **The house ledger** (`paper_state.json`) is the page's own $5,000 simulation, holding what
  the ranking implies so a visitor can watch the engine's judgment run beside their own picks
  and the S&P. `rebalance_house.py` targets gate-passing names only, tier exposure 60/28/12
  across T1/T2/T3, nothing in T4 or exit review, equal weight inside a tier. Run it `--dry`
  first. Virtual dollars, and not advice. First placed 28 Aug 2026, which unwound a v1-era
  book that had drifted to 60% in a single name.
- **Snapshot cadence is weekly** (`days > 6`) in both the house ledger and each visitor's
  browser ledger, matching the weekly republish.
- **The page builds to `tournament\build\bs_console.html`, a fixed path.** It used to be pinned
  to one Claude session's scratchpad under `%TEMP%`, which meant every scheduled run had to
  hand-edit the script and would have written into a directory that no longer existed. Ten
  scripts carried that path. Never reintroduce a session id into a script path.

## Standing owner rulings (see engine `_rulings` for full text)
Values overlay (pushback/embedded, evidence-audited) · jurisdiction penalties (vie −6,
china-direct −4, taiwan-linked −2) · regeneration standard (food distributors sb≤6) ·
intersection rule (jx + health tag = remove) · ownership rule (majority control by excluded-
system operator = remove) · empirical availability flags · unified table (price = view).
