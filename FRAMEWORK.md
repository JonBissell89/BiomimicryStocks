# Balanced Systems Holding Framework

**Premise (corrected Aug 28, 2026).** There is no philosophically good or bad company. Natural systems
carry no morality. They are either in balance or accumulating an imbalance that gets corrected, by
regulation, substitution, exhaustion, or collapse. Everything in nature is working toward equilibrium,
and economies are not exempt because they run on energy, materials, labour, and time. The framework
therefore scores one mechanical question: **does this business move its system toward balance, or does it
earn by holding the system out of balance?** The second is not wickedness; it is a liability with a delay
on it.

**Layer 0: the civilization imbalance map (added Aug 31, 2026).** The engine is not looking for good
companies; there is no such measurement. It is attempting to identify where the human species has driven a
system furthest from regenerative equilibrium, determine the direction in which that system must eventually
correct, and find the mechanisms accelerating that correction. The method is an ecologist's, applied to our
own species: do not begin with economics, industries, ideology, ESG categories, or what humans say they
want. Begin with the organism. Homo sapiens consumes energy and matter, occupies habitat, moves resources,
produces waste, modifies its niche, reproduces, cooperates, competes, builds networks, stores information,
and grows external organs in the form of tools. Civilization is a metabolism. Money is not the underlying
system; it is an information layer the species built to coordinate access to energy, matter, labour, land
and time. The first question is therefore: **where is the metabolism of Homo sapiens furthest from a stable
regenerative state?**

That question is answered in `data/imbalance_map.json` and checked by `scripts/audit_imbalance.py`, before
any company is scored. The map holds twenty-one civilization-scale stocks in two classes. Earth-system
stocks (greenhouse gases, biological diversity, appropriated biological productivity, forests, freshwater,
soil, nitrogen and phosphorus, ocean chemistry, persistent synthetics, recoverable materials, stratospheric
ozone) can be in **ecological overshoot**: human throughput exceeding regenerative or assimilative capacity.
Provisioning stocks (food, water, shelter, energy, healthcare, sanitation, transport, tools, information,
resilient infrastructure) can be in **provisioning deficit**: an essential need undersupplied despite
substantial resource consumption. Less is not always better, and movement is never scored as better or worse. Nothing in nature holds
still: wolves outrun their deer, crash, and recover as the deer recover; tree stocks grow, burn and regrow.
A safe range therefore means the oscillation envelope a stock's own record has stayed inside, and imbalance
means the stock has left that envelope or is leaving it at a speed the envelope never contained. Balance is
a safe range, and a stock can sit
outside it from overconsumption, overproduction, under-regeneration, or under-supply of a need. The future
lies where both forms shrink at once: more human need satisfied with less energy, material extraction,
waste, scarcity and ecological disruption. That is the bridge between biomimicry and a resource-based
economy.

Each system carries an **imbalance severity index**: distance from the safe range x load-bearing
importance x rate of divergence x scale of exposure x irreversibility, on an open instrument with a ceiling
of 486. The ceiling is deliberately lethal: it would mean a load-bearing global stock past a hard limit for
the species, effectively permanent, and still diverging fast. Nothing on the map is near it, which is the
point; the top of the scale is reserved for readings that would actually mean the species cannot live
there. On this instrument biological diversity reads 324 and CO2 reads 162, one third of the ceiling. For a
deficit, distance means the share of the species without the essential, with 6 meaning the need cannot be
met at all. None of this is a danger to the planet itself; planets have no preferred state, and Earth has
run far hotter and far colder. The envelope belongs to the species. Each stock also carries a time series
in `data/imbalance_series.json`, sampled weekly by `scripts/collect_imbalance.py`; most underlying
assessments update yearly or slower, so a flat stretch means the science has not re-measured yet. The anchors are in the map file and
the arithmetic is audited; the exact calculation is expected to evolve as evidence improves. What is fixed
is the separation the audit enforces on every system, in order: **STATE** (how far from equilibrium),
**MOVEMENT** (diverging from the safe range, holding its distance, or returning), **FLOW** (the physical flows causing it), **CORRECTION** (what moves
it toward its safe range), **CLOCK** (the realistic timescale), **COMPANIES** (the mechanisms accelerating
the correction). Quantitative control variables are used wherever science provides them: seven of nine
planetary-boundary processes sit outside their safe range in the 2025 assessment; extinctions run above 100
per million species-years against a boundary below 10; human appropriation of net primary production is
roughly 30 percent against a boundary near 10.

**The counterforce, and why the clock is not a guess (added Aug 31, 2026).** Whenever a system moves in
one direction, the counterforce against that movement gathers as it goes: the wolves' hunger grows with
every deer eaten, and the hunger is what flips the momentum. But pressure alone does not decide the flip;
access to the alternative does, so the counterforce is two measured things. **Pressure** (0 to 3) is the
signal pushing back: a scarcity price, a damage bill, a liability, hunger itself. **Access** (0 to 3) is
the reachability of the path the system could take instead: 0 means no alternative exists, 3 means the
alternative sits at or below parity and is scaling. Access decides which arm the correction takes. With an
accessible alternative the flip is a managed return; without one it is the die-off arm. The wolves have no
second prey, so their correction is a crash. The makers of CFCs had substitutes at comparable cost, so
ozone's correction was a treaty. Access is also where technology enters the equation: as general capability
rises, AI and automation raise access across many systems at once, which is the convergence hypothesis
acting inside the counterforce, and it makes that hypothesis locally testable: if it is true, turn
pressures across the map should rise over the coming years even where pressure holds still.

From these a **turn pressure** is derived: distance x pressure x access x coupling (whether the
counterforce grows with the excursion, stays flat, or is eroded by it), ceiling 108. High distance with
high turn pressure is a compressed spring: a flip near, predictable, and headed for a managed return; the
top of the current map is greenhouse gases at 36, whose substitutes are at parity and compounding. High
distance with low turn pressure is the dangerous reading: biological diversity sits 324 of 486 out with a
turn pressure of 4, because extinction has no price signal and no substitute exists for a species, so its
spring must be built rather than waited for. Shelter's split is diagnostic in the other direction:
pressure 2, access 1, the deficit that persists because the alternative barely exists, not because nobody
feels it. This is the company engine's measure C, the loop, applied one level up; the clock in every entry
is a reading of the counterforce, not a date pulled from air.

The hierarchy the whole engine now runs on:

```
PLANET / CIVILIZATION
  -> IMBALANCE
    -> STOCK
      -> PHYSICAL FLOW CAUSING THE IMBALANCE
        -> REQUIRED CORRECTION
          -> COMPANY / TECHNOLOGY
            -> MEASURED CORRECTION PER DOLLAR OF REVENUE
              -> SELF-DAMPING OR SELF-AMPLIFYING LOOP
                -> SURVIVABILITY
                  -> INVESTMENT
```

The point of the ordering is discipline: the imbalance must exist independently of the company. The audit
fails if any company in the engine attaches to no established imbalance, which is the mechanical guard
against discovering an attractive business first and rationalizing why it matters afterward. The reverse is
allowed and reported as a finding: corrections with no investable company yet (currently forests, ocean
chemistry, and the completed ozone recovery, which is kept on the map as proof that a global correction can
finish).

**The convergence hypothesis (stated to be falsifiable, not believed).** Human civilization may be moving
toward a state where increasingly capable technology satisfies essential needs with progressively less
marginal labour, energy, extraction and waste: AI lowers the cost of intelligence and coordination,
automation the labour per unit, renewables the resource cost of energy, precision agriculture the inputs
per unit of nutrition, closed-loop manufacturing the virgin material demand, distributed production the
transport and coordination requirement, preventive medicine the resources needed to maintain health. If
those converge, economic organization can shift from maximizing resource throughput toward maximizing
useful human outcomes per unit of physical resource. Nothing here states that a resource-based economy is
guaranteed. The testable form: as technological capability increases, does civilization systematically move
toward greater abundance of essential outcomes while requiring less scarce material, energy and human
labour per outcome? The tracked portfolio is one running test. If the hypothesis is right, companies making
essential outcomes cheaper, more abundant, regenerative, distributed and resource-efficient should capture
progressively larger physical and economic flows. If it is wrong, the portfolio should eventually
demonstrate that too.

**The governing rule, everywhere on the site.** Do not predict the future by extrapolating markets. Measure
the imbalance. Determine the direction the physical system must move to resolve it. Measure the clock. Then
find the mechanisms carrying civilization in that direction. The crystal ball is not a prediction. The
crystal ball is the distance from equilibrium.

**Engine v2, stock-and-flow (rebuilt Aug 28, 2026).** Balance is a property of a **stock**, not of a
company. A stock is anything that accumulates and can drain or pile up: aquifer volume, housing units,
sterile-procedure capacity, safe units in a blood supply, soil carbon, grid balancing capacity, material in
circulation. Stocks change through **flows**. A stock is in balance when inflow and outflow match. A company
is never itself in or out of balance; it is a mechanism attached to a flow, and that is what gets scored.

Six measures, 100 points: **A the stock** (20, and the moat deduction lives here), **B the flow** (25),
**C the loop** (20, split into C1 the sign of the feedback and C2 coupling), **D growth pattern** (15, split
into replication, contact inhibition, and clean exit), **E buffer** (10), **F clock** (10). The full rubric
with bands and worked examples is `tournament/V2_RUBRIC.md`.

**Survivability is a gate, not a dimension.** Under 12 months runway with no committed financing, three-year
dilution above 25 percent, a pending buyout, or going-concern doubt sets a company aside regardless of
score. A company that runs out of money did not score badly; it produced no result. This is a statement
about a balance sheet, not about a business.

**The rebuild was a different measurement, not a reweighting.** All 53 names were re-scored from scratch.
The correlation between the v1 score and the v2 score is **0.07**, the mean fell 7.0 points, and 42 of 53
names moved down. A v1 score and a v2 score are not comparable. The tier bands were deliberately left where
they were, so Tier 1 shrank from 29 names to 12, of which 11 clear the gate. Moving the bands to preserve
tier sizes would have reproduced the old answer by arithmetic.

**Built August 27, 2026** from the 15,797-company tournament, rebuilt on the stock-and-flow scorecard
August 28. A rules-based structure for classifying, sizing, and reviewing holdings. The parameters are yours
to set; this document defines the machine, not your trades. Not investment advice; I am not a licensed
advisor.

## The clock principle (added Aug 28, 2026)

Time is relative to the correcting system, not to the observer. An imbalance corrects on the clock of
whatever does the correcting: **substitution and reimbursement** in months to a few years; **regulation,
litigation, technology displacement** in years to a decade; **infrastructure and demographic cycles** over
decades; **soil, aquifers, oceans, climate** over centuries. A system can sit out of balance for an entire
human investing life while barely registering on the clock of the thing that will eventually correct it.
Being right about the imbalance and wrong about the clock is indistinguishable from being wrong.

Consequences, binding on scoring:
1. **Direction without timing is not investable.** Measure F carries the clock directly: F_clock scores the
   time constant of the stock, F_now scores dated momentum inside four quarters.
2. A name aligned with a centuries-scale correction but showing no near-term momentum **scores near zero on
   measure F by design**; it is not credited for eventually being right.
   *Known property:* this makes the scorecard deliberately hostile to long-clock infrastructure. Every name
   with a decades-scale correction sits at F_clock 3 of 6, and that is the largest single reason rail- and
   utility-shaped businesses rank lower under v2 than they did under v1. This is the design, not a defect.
3. The framework's claim is narrow: **when** a correction lands, it lands on businesses holding the system
   out of balance, and those helping it settle absorb the released demand. It says nothing about **when**.
   A business earning from a slow imbalance may pay well for decades; nothing here disputes that.
4. Which clock you are betting on is an owner decision. The tripwire calendar is the practical expression
   of it: dated, checkable events on a human timescale.

---

> **Everything below this line was written before the v2 rebuild (Aug 28, 2026) and its scores and tier
> memberships are v1.** The rules, the rulings, the overlays, and the tripwire calendar all still stand.
> The *numbers and the names in each tier do not*, because v2 re-scored all 53 companies on a different
> instrument and moved 42 of them. `tournament/data/engine_tiers.json` is the only current source of
> truth for what sits in which tier. Read the score bands below as structure, never as membership.
>
> Specific things below that v2 has since overturned: Tier 1 no longer holds 29 names, it holds 12 of
> which 11 clear the gate. Darling Ingredients is no longer the regenerative benchmark, its coupling to
> industrial animal agriculture is exactly what v2 measures and it fell to 58. Survivability is no longer
> a scored dimension, it is a pass/fail gate, and BFLY and DMTRF currently fail it.

---

## The five tiers

Every security you hold or consider gets classified by the same gates the tournament used. A name moves tiers only on new verified facts, never on price action alone.

### Tier 1: Core compounders
**Entry gate:** verified framework score ≥ 80 · FCF-positive · 3-yr dilution ≤ ~2% · durable verified moat · real current expansion signal.
**Framework role:** the ballast; the largest sleeve. Typical guardrail: 50–70% of the equity sleeve, no single name above ~15%.
**Qualifying today:** WRTBY (86) · TSNLF (85) · CLPBY (84) · TDVXF (82) · YMM (80) · SBDHF (81, *home-exchange-only access*) · DLEGF (80, *valuation flag: ~100× P/E, qualifies on business, fails on price discipline; treat as Watch-for-multiple*).

### Tier 2: Proven growers
**Entry gate:** score 75–79 · profitable or clearly self-funding · growth verified this year · dilution < 5%/yr.
**Role:** the growth engine. Guardrail: 20–35% of sleeve, single name ≤ ~8%.
**Qualifying today:** BMBRF (79) · KMDA (78) · BB (78) · ENGCF (77) · CRMD (77, *conditional, see tripwires: 2027 TDAPA cliff*) · SCTTF (75) · CODYY (74, mature anchor variant).

### Tier 3: Asymmetric catalysts
**Entry gate:** score ≥ 69 · a specific, dated, verifiable catalyst that re-rates the company · balance sheet that survives the catalyst slipping once.
**Role:** convexity. Guardrail: 5–15% of sleeve *in total*, single name ≤ ~3–4%, each sized to survive going to zero. Thin lines bought only with limit orders, or on the home exchange.
**Qualifying today:** PEJMF (78, TEER/TTVR approvals; HK line) · CERS (75, RBC CE Mark H1 2027) · SHLS (72, $801M backlog conversion by Q2-27) · DMTRF (72, US GI rollout; Tokyo line) · ADMA (72, probe resolution + buyback) · BIRMF (71, backlog conversion; microcap) · WSIOF (69, overseas re-acceleration; HK line).

### Watch bench (no capital, active alerts)
Names that beat most of the list on score but fail a gate today, price gate, valuation flag, or unresolved objection.
- **Price-gate alerts:** TMRAY 85 at $11.83 and SSMXY 81 at $12.14 (52-wk low $8.01) are the two nearest; full 32-name list in the tournament report with scores.
- **Watch bench examples:** BFLY (rated A on mission; objection = no margin path yet, promotable on two consecutive gross-margin-expanding, loss-narrowing quarters) and SRTA (rated A; objection = unprofitable number two against TransMedics, promotable on sustained profitability or a competitive win). Both reached the top 0.7% of the field; Watch-class is not an error.

### Excluded (framework holds 0%)
Hard-rule and gate failures. Worked examples of the rules biting: a cannabis producer on the addiction rule, a gold miner on no durable need, a life insurer on financial intermediation, a clinical-psychedelics name on the single-unproven-breakthrough rule, a utility roll-up with no product layer, and several pre-revenue names where the thesis is plausible but the economics are unproven. The tournament's consistent finding was that thesis and economics must both be true.
An optional "sandbox" parameter (0–10% of sleeve) exists for names you want exposure to despite gate failure, the framework's honesty rule is that sandbox names are labeled as such, never promoted by hope.

## Jurisdiction penalties: in the ranking itself (owner-directed, Aug 27 2026)

Country risk is scored, not filtered. Penalty schedule (parameters, adjustable): **china-vie −6** (a VIE ADR is a contractual claim, not ownership) · **china-direct −4** (regime risk, real equity) · **taiwan-linked −2** (tail scenario, full rule of law). Applied: YMM 80→74 (T1→T2), Peijia 78→74 (T3), Wasion 69→65 (T3, **at the exit-review floor**), Delta Thailand 80→78 (T1→T2). Base scores and penalties are preserved in `engine_tiers.json`. TSMC on the Watch bench takes −2 at next verification. Consequence: Tier 1 is now five names (WRTBY, TSNLF, CLPBY, TDVXF, SBDHF), higher concentration, zero direct China exposure.

**Ownership rule (Aug 27 2026):** majority control by an operator of an excluded system removes the name, the controller sets strategy, and the growth trajectory follows the excluded system. First applied: **Scott Technology removed** (53.7% JBS; JBS related-party revenue ~16% and nearly doubled YoY; largest-ever contract at JBS's Brooks industrial beef plant, pipeline aimed at JBS US feedlot-beef sites; pasture-linked Protein segment ~22% of revenue and shrinking, Forsyth Barr 1H26 note, Apr 2026). Sub-$10 field: 19.

**Intersection rule (Aug 27 2026):** any name carrying both a jurisdiction penalty and a values-sensitive health tag is removed outright, correlated failure modes (a regime that compresses prices by decree can change medical rules by decree). First applied: **Peijia Medical removed** from Tier 3 (also effectively untradeable in the US; real market HKG:9996). The sub-$10 field stands at 20. Removals are preserved in the engine file's `removed` list for audit; the original tournament report remains the unedited historical record.

The engine re-runs automatically on the **1st of every month at 9:00 AM** (scheduled task `monthly-framework-reverify`): live prices, gate checks, tripwires due, promotion tests on BFLY/SRTA, score/tier updates on verified facts only, artifact republish, and a dated summary in `tournament/logs/`. Runs happen while the Claude app is open; a missed run fires on next launch.

## Price gate raised $10 → $20 (owner ruling, Aug 27 2026)

Fractional-share trading dissolved the per-share access rationale of the original $10 rule; the gate is retained at **$20** to preserve the framework's small/asymmetric tilt rather than abolished. Consequence computed, not assumed: exactly **two** admissions, **Tomra (85 → Tier 1)** and **Sysmex (81 → Tier 1**, embedded tag provisional per the Cerus precedent, auditable on challenge). Ranked field: **21**. New gate-watch alerts: Asahi Intecc $21.41, Mowi $22.42. Both admissions are Y-ADRs with SoFi availability pending empirical in-app checks. The historical tournament report remains the unedited $10-era record.

## Access overlay: SoFi availability (Aug 27 2026)

Owner's brokerage is SoFi Invest. Corrected Aug 27: SoFi trades NYSE/NASDAQ listings **plus a curated set of OTC ADRs (Y-suffix tickers)**, but not F-shares (F-suffix foreign ordinaries). **SoFi-tradable (10 of 19, all empirically confirmed Aug 27):** WRTBY *(fill)*, CLPBY *(in-app check)*, CODYY *(in-app check)*, BB, YMM, KMDA, CRMD, CERS, SHLS, ADMA (+ Watch-bench BFLY, SRTA). Tier 1 on SoFi: WRTBY + CLPBY (2 of 5). **Genuinely unavailable on SoFi (all F-shares):** TSNLF, TDVXF, SBDHF, DLEGF, ENGCF, BMBRF, DMTRF, BIRMF, WSIOF, these need Fidelity/Schwab/IBKR for OTC or IBKR for home exchanges. Engine names carry a `sofi` flag; the calculator and Paper Ledger default to SoFi-only view with a toggle. The Paper Ledger simulation has no broker constraint. Rule: availability flags are set empirically (a real fill or in-app check), not by assumption.

## Regeneration standard: food names (owner ruling, Aug 27 2026)

Pure distribution of industrial food is optimization, not regeneration: accessibility alone caps system-balance at 6/15 for food distributors. Applied: **BIM 79→74** (bottom of Tier 2; base score preserved in the engine file). The regenerative/circular food standard is Darling Ingredients (closes the waste loop; Watch bench). Binding on future entrants: a food name reaches Tier 1 only by transforming the food system, not by distributing its output efficiently. Honest consequence recorded: no sub-$10 name currently represents regenerative food, the public market barely offers one at investable scale.

## Values overlay: health names (owner-defined, Aug 2026)

Every health name carries a tag in `tournament/data/engine_tiers.json`:
- **pushback**: adoption reduces total system spend or threatens incumbent revenue (prevention, democratized access, forced price compression): Tristel, CorMedix, Peijia, Cerus; Butterfly and Strata on the Watch bench.
- **embedded**: economics depend on premium reimbursement inside the existing payment machine: Coloplast, Tobii Dynavox, Kamada, 3-D Matrix, ADMA.

The Allocation Arithmetic calculator has a one-click filter that excludes embedded names and redistributes their tier weight. The tag records how each business makes its money, not a judgment of its patients' need; applying the filter is the owner's call. Note the trade-off it creates: with the filter on, Tier 1 loses Coloplast and Tobii Dynavox, its two most defensive names, so a filtered core leans harder on Wärtsilä/YMM cyclicality.

## Standing rules

1. **Entry:** nothing enters any tier without passing the hard-rejection screen and a verification pass (current price, dilution, runway, corporate actions, the same checklist as the tournament's final round).
2. **Exit review triggers (any one forces a re-verification, not an automatic sale):** a hard-rule event · 3-yr dilution crossing 10% · two consecutive quarters contradicting the thesis · verified score dropping below 65 · a pending buyout (capital is dead money post-announcement, see InPost/Penumbra/IHS).
3. **Liquidity rule:** for † thin-line names, position ≤ a few days of home-exchange volume; US OTC prints are access artifacts, never valuation signals.
4. **Cash is a position.** It deploys against dated catalysts and price-gate alerts, not on a schedule.
5. **Price ≤ $10 is an access screen, not a merit screen.** Market cap and dilution are the valuation facts (DLEGF: $8 share, $95B company).
6. **Quarterly refresh:** re-run verification on every held name + the Watch bench; the tournament data files are the baseline to diff against.

## Tripwire calendar (from verified final-round research)

| When | What | Names |
|---|---|---|
| Sep 10, 2026 | Q1 FY27 results | DMTRF |
| Sep 24, 2026 | Q2 FY27 results (QNX royalty conversion) | BB |
| Oct 2026 | Q3 reports: Oct 21 TDVXF · Oct 27 WRTBY · late-Oct ENGCF, DLEGF · Oct 12 TSNLF FY26 audited · mid-Oct SCTTF FY26 (record guided) | Tier 1/2 cluster |
| Late 2026 | CMS post-TDAPA payment clarity, the single biggest risk on the list | CRMD |
| Nov 2026 | Q3s: KMDA, YMM, SHLS, ADMA (+ ACAAI outcomes data), BIRMF backlog conversion, SBDHF Q1 · Coloplast FY guidance early Nov | broad |
| H1 2027 | INTERCEPT red-blood-cell CE Mark decision, the largest catalyst in Tier 3 | CERS |
| Mid-2027 | DefenCath post-TDAPA economics become real | CRMD |
| Rolling | Price-gate alerts: TMRAY < $10 · SSMXY < $10 · promotion checks on BFLY/SRTA earnings | Watch |

---

*This is the public copy. The private working document continues past this point with
one section classifying a specific person's actual holdings against these rules. That
section is deliberately not published, and nothing in this repository contains anyone's
real positions, balances or trades. The $5,000 in the simulation is pretend money.*
