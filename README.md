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
Earth-system and ten provisioning, each with its safe range, measured state, direction, causal flows,
required correction, clock, and severity (distance x load x divergence rate x exposure x irreversibility).
Two failure forms are tracked: **ecological overshoot** (throughput past regenerative capacity) and
**provisioning deficit** (an essential need undersupplied despite heavy resource use). The bridge between
them is the target: more need met with less energy, extraction, waste and disruption.

```
PLANET -> IMBALANCE -> STOCK -> FLOW -> CORRECTION -> COMPANY
       -> CORRECTION PER DOLLAR -> LOOP -> SURVIVABILITY -> INVESTMENT
```

`audit_imbalance.py` enforces the ordering: every company in the engine must attach to an imbalance that
exists without it, and corrections with no investable company yet are reported as findings (currently
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

- **Weekly** ([`.github/workflows/weekly.yml`](.github/workflows/weekly.yml)): refresh
  prices, rebalance the simulated book, rebuild, verify, deploy to Pages. Never changes
  a score, because filings do not change weekly.
- **Monthly**: the judgment run. Gates re-checked against filings, tripwires, score and
  tier changes on verified facts. The only thing allowed to change a score.

Verification chain, all of which must pass before anything publishes:
`audit_imbalance.py` then `audit_engine_v2.py` then `refresh_app.py` then `check_page.py`, `check_structure.py`,
and `validate_console.js`.

## The page

One self-contained HTML file with no runtime network calls at all. It carries the engine,
every company, the prices and the logic. Each visitor gets $5,000 of pretend money kept
in their own browser and sent nowhere. They can buy anything in the universe, including
companies the screen cut, and watch their picks against the ranking's own book and the
S&P 500 over time.

A ranking that cannot be checked is just an opinion with numbers on it. That is what the
simulation is for.
