# Biomimicry Stocks

A stock screen that asks one mechanical question of every public company an American
investor can buy: **does this business move its system toward balance, or does it earn
by holding the system out of balance?**

Not a morality test. Natural systems carry no morality; they are either in balance or
accumulating an imbalance that eventually gets corrected, by regulation, substitution,
exhaustion or collapse. A company deferring its real costs onto a water table, a health
system or a supply chain is holding a liability with a delay on it. This measures that.

**Research output, not investment advice. Nobody here is a licensed financial advisor.
The money in the simulation is pretend.**

---

## Layer 0: where is the species out of balance?

The engine does not start with companies. It starts with the question an ecologist would ask of any
species: **where is the metabolism of Homo sapiens furthest from a stable regenerative state?** Money is
treated as what it is, an information layer coordinating access to energy, matter, labour, land and time,
not as the underlying system.

[`data/imbalance_map.json`](data/imbalance_map.json) holds twenty-one civilization-scale stocks, eleven
Earth-system and ten provisioning, each with its safe range, measured state, movement, causal flows,
required correction, clock, and a severity index (distance x load x divergence rate x exposure x
irreversibility) on an open instrument whose ceiling, 486, is reserved for readings that would mean the
species cannot live there. [`data/imbalance_series.json`](data/imbalance_series.json) carries each stock's
time series, sampled weekly by `collect_imbalance.py`.
Two failure forms are tracked: **ecological overshoot** (throughput past regenerative capacity) and
**provisioning deficit** (an essential need undersupplied despite heavy resource use). The bridge between
them is the target: more need met with less energy, extraction, waste and disruption.

```
PLANET -> IMBALANCE -> STOCK -> FLOW -> CORRECTION -> COMPANY
       -> CORRECTION PER DOLLAR -> LOOP -> SURVIVABILITY -> INVESTMENT
```

The written labels are not authority: `derive_imbalance.py` derives movement from each stock's series and
distance from its control variable, overwriting any label that disagrees, and `audit_imbalance.py` fails
the build on any mismatch. `audit_imbalance.py` also enforces the ordering: every company in the engine
must attach to an imbalance that exists without it, and corrections with no investable company yet are reported as findings (currently
forests, ocean chemistry, and the completed ozone recovery, kept as proof a global correction can finish).
The rule that governs all of it: measure the imbalance, the direction the physical system must move, and
the clock, then find the mechanisms carrying civilization that way. The crystal ball is not a prediction;
it is the distance from equilibrium.

## The scorecard

Balance is a property of a **stock**, meaning something that accumulates and can drain
or pile up: aquifer volume, housing units, sterile-procedure capacity, safe units in a
blood supply, soil carbon, spare grid capacity. Stocks change through **flows**. A stock
is in balance when inflow and outflow match. A company is never itself in or out of
balance; it is a mechanism attached to a flow, and that is what gets scored.

Six measures, 100 points, the same six for every company:

| | Measure | Points |
|---|---|---|
| **A** | **The stock.** Name the accumulation. Is it load-bearing and outside its safe range? Moat deduction lives here. | 20 |
| **B** | **The flow.** Direction and magnitude per dollar of revenue. Needs a quantified before and after. | 25 |
| **C** | **The loop.** Does success reduce its own demand or manufacture more, and does revenue survive a rebalance? | 20 |
| **D** | **Growth pattern.** Does it copy a proven unit the way cells divide, or swell? Can it stop growing and stay solvent? | 15 |
| **E** | **Buffer.** Efficiency that keeps slack, or efficiency bought by removing it. | 10 |
| **F** | **Clock.** How fast does this correction land, and is it visibly moving now? | 10 |

**Survivability is a gate, not a measure.** Under 12 months of runway with no committed
financing, three-year dilution above 25 percent, a pending buyout, or going-concern doubt
sets a company aside regardless of score. A company that runs out of money did not score
badly, it produced no result.

Full rubric with bands and worked examples: [`V2_RUBRIC.md`](V2_RUBRIC.md).

## Two things worth knowing before you trust a number

**This scorecard replaced an earlier one, and the correlation between them is 0.07.**
Across the same 53 companies. That is not one ranking shifted down, it is a different
measurement. An old score and a new score are not comparable.

**Tier bands never move to preserve tier sizes.** The rebuild dropped the mean 7 points
and moved 42 of 53 names down. Sliding the bands to keep the top tier populated would
have reproduced the previous answer by arithmetic. Tier 1 got smaller instead.

## Does the philosophy show up in the numbers?

It does, monotonically, which is the real test of whether the rubric measures what it says:

| Coupling | mean | | Loop sign | mean |
|---|---|---|---|---|
| survives a rebalance | 76.5 | | self-damping | 77.9 |
| neutral | 69.7 | | neutral | 72.8 |
| shrinks | 68.1 | | amplifying | 62.8 |

## Layout

```
data/     imbalance_map.json is Layer 0, the civilization imbalance map.
          engine_tiers.json is the graded table and the source of truth.
          search_index.json holds every company that entered, with why it was cut.
          price_cache.json, paper_state.json, and the tournament audit trail.
scripts/  the pipeline. paths.py resolves everything relative to the repo.
build/    the rendered page (gitignored, built by the workflow)
```

## How it runs

- **Weekly** ([`.github/workflows/weekly.yml`](.github/workflows/weekly.yml)): sample
  the imbalance series, refresh
  prices, rebalance the simulated book, rebuild, verify, deploy to Pages. Never changes
  a score, because filings do not change weekly.
## The rigor layer

The score's own quality is measured, not asserted, in [`data/rigor/`](data/rigor/):

- **A frozen vintage.** Scores and prices as of 2026-08-28, hash-locked; the forward test grades this
  vintage forever, whatever the monthly judgment run later changes. Git history is the point-in-time record.
- **A pre-registered protocol.** Endpoints, horizons and success thresholds were written down before the
  data could arrive (tier spread and information coefficient at 12 months, the basket vs the S&P stated
  either way, and the convergence hypothesis in local form: median counterforce access rising by 2028).
  Nothing about the test can be moved afterward.
- **A report card** that accrues weekly and reports honestly ("accruing") until the window is real, always
  beside a momentum-contamination check: the frozen scores correlate at -0.24 with the trailing year's
  returns, so the rubric is not last year's winners in a lab coat.
- **Sensitivity**: 1,000 weight perturbations move the ranking almost nowhere (rank stability 0.995), so the
  measurement, not the weights, produces the order. Cronbach's alpha of 0.47 says the six measures are six
  things, not one, which the framework accepts and states.
- **A risk profile** from a year of weekly closes: 14.3 effective independent bets across 52 names, average
  pairwise correlation 0.08, first principal component 16 percent, so the health-heavy list is more
  independent wagers than its sector share implies.
- **Coverage**: the near-miss frontier (topped by water utilities cut on growth and finances) and a seeded
  blind re-score sample that stands as an open obligation until the false-negative rate is measured.

Executed since registration:

- **The whole universe faces the clock.** All 15,797 first-screen judgments are frozen and hash-locked, a
  monthly universe price track runs beside the weekly ranked one, and the protocol (v2, superseding v1 with
  v1 preserved and hashed) registers universe endpoints: an information coefficient across every priced
  name, and the advanced-minus-cut spread, published either way.
- **The blind re-score happened, twice.** Six independent blind scorers re-judged two pre-registered
  12-name samples from web research alone: pooled agreement rho 0.76 across 24 names, one false negative
  found and then confirmed (VMD, home respiratory care growing about 25 percent a year, cut at the first
  screen at 33 but graded t2 at 76 by a full blind six-measure scoring; it sits in the judgment queue while
  the frozen vintages keep the cut so the forward test prices the miss), one recorded score corrected (IRS,
  a mall operator recorded at 42 against the engine's own rent-extraction pricing, corrected to 24), and
  zero new misses in the second batch, which agreed to 2.6 points of 50. The estimated false-negative rate
  on hard cuts fell from 1-in-8 to 1-in-16 as the sample widened.
- **A blind second scorer re-scored 16 ranked names on the six measures, in two batches.** Gate verdicts
  agreed 16 of 16, including an independent BFLY fail on dilution; totals agreed within about 6 points of
  100. The two batches answered different questions: inside batch one's narrow 65-to-81 band the ordering
  was scorer noise (rho 0.05), while across batch two's wider 57-to-82 band both scorers ordered the names
  the same way (rho 0.85). The instrument measures level and coarse ordering reliably and fine ordering
  inside a tier band unreliably; the recorded scores also run about 3 points hot against the blind ones,
  so tier edges deserve less confidence than the gate, and the framework now says so.
- **Attribution, internal:** 94 percent of basket variance is the internal market plus the health tilt; the
  external factor test could not be run from the build environment and is registered as pending so it
  cannot be quietly dropped.

`audit_rigor.py` enforces all of it: both vintage hashes, the protocol supersession chain, track ordering,
freshness, the registered sample sizes, and a floor under rank stability.

- **Monthly**: the judgment run. Gates re-checked against filings, tripwires, score and
  tier changes on verified facts. The only thing allowed to change a score.

Verification chain, all of which must pass before anything publishes:
`collect_imbalance.py` then `derive_imbalance.py` then `audit_imbalance.py` then
`track_prices.py` then `universe_vintage.py` then `report_card.py` then `rigor_summary.py` then `audit_rigor.py` then `audit_engine_v2.py` then `refresh_app.py` then `check_page.py`, `check_structure.py`,
and `validate_console.js`.

## The page

One self-contained HTML file with no runtime network calls at all. It carries the engine,
every company, the prices and the logic. Each visitor gets $5,000 of pretend money kept
in their own browser and sent nowhere. They can buy anything in the universe, including
companies the screen cut, and watch their picks against the ranking's own book and the
S&P 500 over time.

A ranking that cannot be checked is just an opinion with numbers on it. That is what the
simulation is for.
