# The Stock and Flow Scorecard (engine v2)

**This is the company-level layer.** It runs underneath Layer 0, the civilization imbalance map
(`data/imbalance_map.json`), which establishes the imbalance, its direction, its causal flows, its required
correction and its clock before any company is examined. The six measures below are unchanged by that
layer; what changes is the order of operations: a company is only ever scored as a mechanism on a
correction that Layer 0 already established. `audit_imbalance.py` fails the build if a company attaches to
no established imbalance.

Balance is a property of **stocks**, not of companies. A company is a mechanism attached to a **flow**.
Score the mechanism by what it does to the stock, whether the loop back from the stock damps or amplifies
it, whether it can grow the way cells grow, and whether the correction arrives on a human clock.

**Survivability is a GATE, not a score.** Check it first. If a company cannot fund itself to the horizon in
measure F, it is excluded, not ranked lower. Gate fails: negative FCF with under 12 months runway and no
committed financing; 3-year dilution above 25%; a pending buyout; going-concern doubt.

Every measure requires a **citation or a computed number**. "Appears to" and "likely" score at the bottom of
their band. Where evidence does not exist, score the bottom of the band and mark `evidence: none`.

---

## A · THE STOCK: 20 points

Which accumulation does this business touch, and what state is it in?

- **Name the stock** in concrete terms (aquifer volume, soil carbon, grid balancing capacity, housing units,
  installed transport capacity, sterile-procedure capacity, blood supply safety, material in circulation,
  arable topsoil, skilled-labour hours). If you cannot name one specific accumulation, score ≤ 6.
- **Load-bearing test**: would the system fail or degrade materially if this stock left its viable range?
- **State**: draining / matched / harmfully accumulating.

| Band | Meaning |
|---|---|
| 17–20 | Stock is named, unambiguously load-bearing, and currently outside viable range (draining or harmfully accumulating) |
| 12–16 | Named and load-bearing, currently near balance |
| 7–11 | Named but not clearly load-bearing, or the company touches it only indirectly |
| 0–6 | No specific stock identifiable; the business sits on preference rather than necessity |

**Moat adjustment applies here, not as its own measure.** If the company's defensibility comes from
*blocking substitution* (lock-in, patent thickets on an essential, regulatory capture, single-source
control of a load-bearing stock), subtract 3. It is holding the stock hostage. A moat earned by *performing
the function better* (manufacturing difficulty, evidence-won approval, installed base won on results) is
neutral here and credited under B as durability.

## B · THE FLOW: 25 points

Direction and magnitude of the company's effect on that stock, per unit of business.

- **Direction**: raises inflow to a depleted stock / cuts outflow from one / drains it further.
- **Magnitude**: how much correction per dollar of revenue. This is the heaviest single measure.
- **Measured, not claimed.** A quantified before/after is required for the top band.

| Band | Meaning |
|---|---|
| 21–25 | Correct direction with a **quantified** effect (e.g. Tristel ~10× cheaper per decontamination; Bonesupport amputations 18%→2%, ~$28k saved per patient; Full Truck empty miles 39%→35%; engcon one machine replacing two) |
| 15–20 | Correct direction, effect evidenced but not cleanly quantified |
| 8–14 | Correct direction, asserted only; or mixed effect across segments |
| 1–7 | Neutral to the stock; sells into the system without changing the flow |
| 0 | Drains a load-bearing stock or feeds a harmful accumulation |

## C · THE LOOP: 20 points

The feedback line from stock level back to the company. Two questions.

**C1 · Sign of the loop (0–12).** Does success reduce or increase the need for the product?

| Band | Meaning |
|---|---|
| 10–12 | **Self-damping.** Success destroys the demand it feeds on (CorMedix prevents the infections it is paid to prevent) |
| 6–9 | **Neutral.** Demand tracks an independent driver the company does not create |
| 2–5 | **Mildly amplifying.** Success creates adjacent demand for itself |
| 0–1 | **Runaway.** The product manufactures the problem it sells against |

**C2 · Coupling (0–8).** What must remain true for the revenue to exist?

| Band | Meaning |
|---|---|
| 7–8 | Revenue survives, or grows, if the system rebalances |
| 4–6 | Revenue is neutral to whether the system rebalances |
| 1–3 | Revenue **shrinks** if the system rebalances (a closed loop inside a broken system) |
| 0 | Revenue **requires** the imbalance to persist and deepen |

> Worked example: **Darling Ingredients** renders animal byproduct into fuel and ingredients, a genuine
> loop (C1 high). But its feedstock is the waste stream of industrial animal agriculture, so if the protein
> system rebalanced toward the regenerative standard this framework prefers, its inputs shrink. C2 scores
> 1–3. This is the test that the previous engine lacked, and it is why Darling was mistakenly labelled the
> regenerative benchmark.

## D · GROWTH PATTERN: 15 points

Cells divide rather than swell, stop at contact, and dismantle obsolete parts cleanly. Score the pattern.

- **Replication over enlargement (0–6).** Scales by copying a proven unit (product, module, licence,
  franchise, standardised install) = 5–6. Scales by one entity growing without limit, or by rebuilding a
  local operation in each market = 0–2.
- **Contact inhibition (0–5).** Is there a size at which it remains solvent without further growth?
  Profitable and self-funding at current scale = 4–5. Requires perpetual growth or fresh capital to stay
  solvent = 0–1.
- **Clean exit (0–4).** When its product or plant becomes obsolete, does the system strand assets, or does
  it dismantle and recycle cleanly? Long-lived stranded infrastructure = 0–1.
  *Clarified in application:* this asks whether obsolescence **strands**, not whether the asset is
  long-lived. An asset that does not go obsolete is not stranded. A rail corridor in continuous use for
  150 years scores mid-band; a single-purpose refinery built for one fuel policy scores 1.

## E · BUFFER: 10 points

Efficiency that keeps slack, versus efficiency bought by removing it. This is the fragility qualifier on B.

| Band | Meaning |
|---|---|
| 8–10 | Efficiency that **adds** redundancy: distributed or modular deployment, repairable, multi-sourced, locally adaptable, works when a central node fails |
| 5–7 | Efficiency neutral to system slack |
| 2–4 | Efficiency that mildly concentrates: heavy reliance on one plant, one supplier, or one customer |
| 0–1 | Efficiency bought by stripping buffers: single global facility, zero-inventory dependency, one customer above 40% of revenue |

*Computable inputs where available: customer concentration, supplier concentration, number of production
sites, revenue share of largest facility, inventory days.*

## F · CLOCK: 10 points

Does the correction land on a horizon a human investor can hold to?

- **Time constant of the stock (0–6):** reimbursement or substitution, months to a few years = 5–6;
  regulation, litigation, technology displacement, years to a decade = 4–5; infrastructure or demographic
  cycles, decades = 2–3; soil, aquifers, oceans, climate, centuries = 0–1.
- **Evidence it is moving now (0–4):** dated orders, approvals, backlog, installed-base growth in the last
  four quarters = 3–4; announced intentions only = 0–1.

A company correctly aligned with a three-hundred-year correction and no current momentum scores near zero
here **by design**. Being right about the imbalance and wrong about the clock is indistinguishable from
being wrong.

---

## Recording format

Each company produces: `A, B, C1, C2, D_rep, D_inhib, D_exit, E, F_clock, F_now`, a `stock` name string, a
`loop` label (damping / neutral / amplifying / runaway), a `coupling` label, a `clock` label, a one-line
`evidence` citation for B, and `gate: pass|fail` with reason.

Total = A + B + C1 + C2 + D(3 parts) + E + F(2 parts) = 100.

Jurisdiction penalties (china-vie −6, china-direct −4, taiwan-linked −2) apply after the total, unchanged.

## Tiers

T1 ≥ 80 · T2 74–79 · T3 69–73 · T4 65–68 · below 65 is exit-review.

**The bands were deliberately not moved when v2 was applied.** The re-score dropped the mean 7.0 points and
moved 42 of 53 names down. Shifting the bands down to keep 29 names in Tier 1 would have reproduced the old
answer by arithmetic. Tier 1 now holds 12 names, 11 of them investable. This is the "do not pad the list"
rule applied to tiers rather than to the list.

---

## What application taught us (recorded 28 Aug 2026)

**The rubric is measuring something genuinely different.** Correlation between the v1 score and the v2 score
across the same 53 companies is **0.07**. This is not the old ranking shifted down; it is a different
instrument. Anyone comparing a v1 score to a v2 score is comparing two different measurements.

**Both claims the philosophy makes are visible in the scores, monotonically:**

| Coupling (C2) | n | mean total | | Loop sign (C1) | n | mean total |
|---|---|---|---|---|---|---|
| survives a rebalance | 24 | 76.5 | | self-damping | 7 | 77.9 |
| neutral | 20 | 69.7 | | neutral | 41 | 72.8 |
| shrinks | 9 | 68.1 | | amplifying | 5 | 62.8 |

**Measure F barely discriminates inside the finalist pool.** F_clock spans only 3–5 of 6 here and F_now spans
2–4 of 4, correlating −0.13 with the total. This is not a broken measure: F did its work upstream in the
six-round screen, where names with no dated momentum were already cut. F separates the universe, not the
survivors. Expect it to matter again on the next full-universe run.

**The scorecard is deliberately hostile to long-clock infrastructure.** Every name with a decades-scale
clock sits at F_clock 3 of 6, and that is measure F working as written. It is the single largest reason
rail- and utility-shaped businesses rank lower than they did. This is a designed property to be aware of,
not a defect to correct.

**Inter-rater reliability is acceptable.** Comparable businesses scored by different researchers landed
within 5–10 points: infection control 5, construction attachments 5, molecular diagnostics 9, cardiac
monitoring 10. Rail spanned 15, and that spread traces to a real difference rather than rubric ambiguity,
since Wabtec sells a replicable retrofit while the railroads own corridors.

**The moat deduction under A was tested against the rail cluster and kept.** The concern was that penalising
a natural monopoly punishes geography rather than conduct. The evidence answered it: rail moves a ton of
freight roughly 480 miles per gallon against about 145 for trucks, and rail's modal share against trucking
still has not moved. A position that captures that advantage as captive-shipper margin instead of passing it
through as volume is throttling the very correction it would otherwise drive. The deduction is charged on
conduct, and the test to apply is: **does the company use its position to restrict the flow it corrects?**


---

# v2.1 amendments (registered 3 Sep 2026): coordination tissues, evidence parity, and the first screen

**What this section does.** v2.0 measures tissue repair: a mechanism attached to a flow, scored on homeostasis
(A, B), damping (C), contact inhibition and clean exit (D), slack (E) and the clock (F). Medicine is that
biology with a payer, which is one reason the ranked list holds 27 health names and the first screen advanced
60 percent of health against 0 of 323 software, 0 of 265 media, 0 of 603 materials and 0 of 171 services. A
body also has tissues whose work is measured somewhere other than the tissue itself: nervous tissue
(information, sensing), circulatory tissue (transport, and matter returned to use), immune tissue (resilience).
Layer 0 already lists information, tools, transport, resilient infrastructure and recoverable materials as
stocks in deficit or overshoot; the first screen priced their mechanisms under a class called
`infrastructure` that names no stock, and stage 2 then cut them as enablers (15 of the 16 verdicts that use
the words enabler or indirect need fall on that class). v2.1 repairs the identified structural biases and
nothing else.

**What does not move.** The six measures and their weights. The tier bands (80, 74, 69, 65). The survivability
gate in every term. The jurisdiction penalties. The two first-screen thresholds (need 20 or more AND viability
9 or more, both hard). Every terminal-consumption prior (food, water, shelter, energy, health). The rule that
every band needs a citation or a computed number and that `evidence: none` scores the bottom of its band. No
rule below is justified by the names it would admit: each is tied to a Layer 0 correction text or to a
documented inconsistency between two table entries, and the pre-registered predictions at the end are written
to catch drift in either direction. Movement of a stock is written as toward or away from its safe range, as
overshoot or deficit, never as a verdict.

## Recorded on every card (additions to the v2.0 format)

Each card now also carries: `host_flow` (the physical unit scored under B, the host stock, and its Layer 0 id);
`evidence_class` (1 to 5); `attribution` (the company's share of the host flow, or `not computable`);
`rebound` (absorbed, partial, induced, none, or exempt); `ceiling` (variable, figure, source, date);
`penetration` (percent, date); `enlarging` (the cited statement, or none); `largest_node` (share of throughput,
or none, or n/a); `moat_tests` (pass, fail or silent for each of the three tests); `clock_basis` (asset, or
adoption with its three numbers); and, only on a gate fail for dilution, `developmental` (yes or no). A blind
second scorer checks these numbers rather than re-judging the words.

## A · The stock: the moat deduction is charged by three document tests (amended)

The deduction of 3 is charged on conduct, decided by three tests from public documents. Write pass, fail or
silent for each on the card.

- **Test 1, interface.** Pass when a third party's attachment to the product is documented by someone other
  than the company: a standards body listing the interface, a regulator's interoperability compliance record,
  or a named third party whose product, consumable or listing runs on the interface in that third party's own
  filing or catalogue. Fail when the filings describe proprietary consumables or exclusivity, or when the
  company has enforced patents or trade secrets against a substitute in the last five years (litigation or an
  ITC action, cited by docket). Silent otherwise. An API page authored by the company is silent, not a pass.
- **Test 2, price conduct.** The price per unit of the corrected flow (take rate per order, price per
  procedure, tariff per tonne-km, price per connection, price per seat) over the last three years, from
  filings, the regulator or a published price list, against the consumer price index of the company's largest
  revenue geography. Pass when flat or falling in real terms, or when the filings disclose pass-through of a
  cost advantage. Fail when it rose faster than that index, or when the filings name pricing as the growth
  driver. Silent when no series exists; write `price: none`. Cite the series either way.
- **Test 3, exit cost.** Pass when switching lives in the customer's own data and export in a standard format
  is documented. Fail on contractual exit fees, minimum-volume or exclusivity clauses, a captive-shipper or
  captive-territory finding by a regulator or court in the last five years, or a pending merger review that
  would leave two suppliers. Silent otherwise.

| Result | Deduction |
|---|---|
| Two or three fails among the testable tests | subtract 3 |
| One fail | subtract 1 |
| No fails, at least two tests testable | none |
| Fewer than two tests testable | subtract 1, write `moat: unmeasured` |

A standard that others may implement (a protocol, a container, an interface adopted by rivals) passes test 1
by definition and can never by itself trigger the deduction: that is the difference between a standard and a
hostage. Geography alone (a natural-monopoly corridor, a licensed territory, a patent won on evidence) is not a
fail. The question stays as recorded on 28 Aug 2026: does the company use its position to restrict the flow
it corrects? The bands of A are unchanged.

## B · The flow: the correction is measured where it lands (amended)

**Step 1, name the host flow.** The flow scored is the flow of a Layer 0 stock at whichever site it changes.
For a mechanism whose product is coordination, sensing, compute, connectivity, a component, a material or a
tool, that site is the customer or the system, not the company's own operations: empty miles per shipment,
kWh per unit delivered, virgin tonnes per tonne of product, clinician-hours per patient, litres lost to leakage
per litre delivered, outage minutes per connection. Record `host_flow`, the host stock and the Layer 0 id. A
liver's work is measured in the blood, not in the liver.

**Step 2, evidence class, binding on every sector.** QUANTIFIED means five things present: a number, a
baseline, a period, a population size (n), and a named source. Any two missing caps B at 14.

| Class | What qualifies |
|---|---|
| 1 | A controlled comparison on the flow (randomised trial, matched cohort, A/B test on the host flow) whose endpoint is a resource or flow quantity, peer-reviewed or on a regulator's label |
| 2 | An operational before-and-after on the host flow disclosed in a document lodged with a securities, utility or transport regulator: by the company (a metric the regulator or exchange requires, or one in the audited annual report), by a customer (the customer's own filing or rate-case exhibit), or a national statistical series naming the company's product or its customers |
| 3 | An independent system study of the mechanism class (regulator, agency, peer-reviewed) applied to the company's disclosed volume; or an efficacy trial with no flow endpoint. Mandatory computation: when the trial gives the clinical inputs and a payer tariff or public cost table gives the price, the flow effect must be computed with both inputs cited, and the result is class 2 |
| 4 | A dated public plan, backlog or approval whose earlier milestone in the same plan was met on schedule, both dates cited |
| 5 | Assertion, case study without n, award, an "up to" figure, dollars saved without a physical unit, a case study published by the company about its own customer |

Band access: 21 to 25 requires class 1 or 2; class 3 caps B at 20; class 4 caps at 14; class 5 caps at 10.
Direction still places a name within its band, and the four bands and their worked examples are unchanged. A
public plan is never class 1 or 2 whatever the size of the company. A company-run trial that is peer-reviewed
is class 1; a customer's fleet pilot reported in the customer's own filing is class 2; these are the same band.
Write the class number in square brackets in the evidence line, for example `[class 2, customer filing]`.

**Step 3, attribution.** A company may claim the host flow only when its share of that flow is disclosed or
computable (its units divided by the host's units, both cited). When the share is not computable, score B on
the product's own per-unit performance metric disclosed in the company's filing (fuel per unit, kWh per unit,
litres per cycle), capped at 14.

**Step 4, rebound test (Jevons).** Applies when the host flow is a drain on an overshoot-side stock (a Layer 0
stock in overshoot, or the overshoot side of food: vehicle-kilometres, fossil kWh, virgin tonnes, hectares,
nitrogen applied, waste generated) and B is scored at 15 or above. Deficit-side inflows (patients treated,
persons connected, dwellings delivered, organs transplanted, litres delivered) are exempt: a rising system
total there is the correction, not the rebound; write `rebound: exempt`. Source: the national statistical
agency, energy agency or transport ministry of the company's largest revenue geography. Window: the latest
five published years. Need series: the ceiling denominator for the attached stock (table under C1). Cite both
growth rates on the card and record one outcome:

| Outcome | Reading | Effect |
|---|---|---|
| absorbed | the system total of the host flow fell, or held within 2 percent, while need rose | none |
| partial | the system total rose, slower than need | none, recorded |
| induced | the system total rose faster than need | the company's before-and-after is contradicted at system level, so B is capped at 20, and the outcome is recorded as evidence for C2's unchanged 1 to 3 band |
| none | no public series exists | none, recorded |

**Sensing and prediction are scored here and nowhere else.** A sensor, meter or forecaster scores B on the
host's variance or loss metric (leakage located, outage minutes, forecast error in MWh, unplanned downtime
hours, false-alarm rate, tonnes of input not applied) with the same five elements and the same classes. The A
stock for a sensing company is the physical stock measured, never uncertainty itself; a sensing company that
cannot name the Layer 0 stock its measurement serves scores A at 6 or below. No credit for sensing exists under
any other measure.

## C1 · Sign of the loop: amplification is scored by its bound (amended)

Before assigning a band, record three items on the card:

- **(i) ceiling**: the physical count that bounds demand for the unit, taken from the table below for the
  attached Layer 0 stock, with the published figure, source and date;
- **(ii) penetration**: the company's units (its disclosed volume metric, or revenue divided by a disclosed
  average selling price) divided by the ceiling, as a percent with its date;
- **(iii) enlarging mechanism**: any statement in the company's own filings, or a regulator's finding, that use
  of the product raises total consumption of the ceiling variable or widens the population it is sold to (an
  added indication, a consumer tier, a wellness label).

Ceiling table (the denominator of the Layer 0 correction; the same denominator serves the rebound test):

| Layer 0 id | Ceiling variable | Source type |
|---|---|---|
| transport | registered commercial vehicles above 3.5 tonnes; tonne-km shipped as the need series | national vehicle registry; statistical office |
| information | persons or households (one connection each is bounded) | census; telecom regulator |
| tools | establishments or licensed operators in the served sector | business register; licensing body |
| healthcare | patients in the labelled indication; procedures per year | label; national prevalence statistic; registry |
| shelter | households or dwellings | census |
| energy_access, ghg | connections or households; kWh delivered; fossil kWh in the host segment as the drain | utility regulator; energy agency |
| water_access, freshwater, sanitation | connections or persons served; litres withdrawn; tonnes of waste generated | utility regulator; statistical office |
| food, hanpp, soil, nutrients | hectares under cultivation; persons; tonnes of nitrogen applied | agriculture ministry; FAO |
| materials, novel | tonnes of the material consumed nationally; containers or tonnes put on the market | geological survey; statistical office |
| infrastructure | installed assets of the class (bridges, km of pipe, km of line) | asset registry; regulator |
| forests, biosphere, ocean | hectares; the ghg denominator for ocean | national inventory |

A person-count is a ceiling only when the unit consumed per person is physically bounded (one connection, one
dwelling, one procedure per patient). A unit whose consumption per person is unbounded (compute cycles,
content hours, consumable volume) has no ceiling under this test.

| Band | Meaning |
|---|---|
| 10 to 12 | **Self-damping**, unchanged: success removes the demand it is paid for; cite the mechanism and a number |
| 6 to 9 | **Neutral**, unchanged, and now explicitly including bounded developmental amplification: a network or adoption feedback whose ceiling is recorded from the table, whose penetration is computed, and for which no enlarging mechanism is documented, scores 6 to 7 within this band |
| 2 to 5 | **Mildly amplifying**: adjacent demand for the company's own products (a consumable annuity, an indication the company widened, an installed base of proprietary consumables), a network effect with no recorded ceiling, or a unit with no ceiling under the table |
| 0 to 1 | **Runaway**: an enlarging mechanism documented under (iii); the product manufactures the problem it sells against |

Rules: nothing scores 10 to 12 on a network effect; the reduction of a host flow is paid once, under B, and
earns nothing here; `evidence: none` scores the bottom of whichever band the words support. Biological anchor:
development is positive feedback that stops at the size of the organism; cancer is positive feedback that
recruits its own blood supply. The test is whether the company produces, or widens, its own ceiling.

## C2 · Coupling (unchanged)

The bands and the Darling worked example stand as written. An induced rebound outcome under B is evidence for
the 1 to 3 band (revenue riding on induced volume shrinks if the system rebalances) and is recorded there; it
does not change the band text.

## D · Growth pattern (unchanged)

The replication score of a corridor owner (1 to 2) is the observed pattern, growth by merger and enlargement,
and stands. A coordination unit, a retrofit kit, a meter, a machine or a deposit machine is a replicated unit
and scores 5 to 6 as before.

## E · Buffer: two tests, the lower governs (amended)

**Slack test** (the existing bands, with their computable inputs made explicit): inventory days; spare
capacity or fleet reserve as a share of fleet; crew or maintenance headcount trend over three years; largest
customer share of revenue; single-sourced inputs; number of production sites. 8 to 10 adds redundancy
(distributed or modular, repairable, multi-sourced, works when a central node fails); 5 to 7 neutral; 2 to 4
concentrates (one plant, one supplier, one customer); 0 to 1 buffers stripped on the record (a single global
facility, zero-inventory dependency, one customer above 40 percent of revenue, or a reserve cut on the public
record: stored fleet above 10 percent with maintenance headcount cut, embargoes).

**Node test** (new), applied only to a company whose product is carried by a network or deployment it
operates (a carrier, a platform, a grid, a logistics network, a hosting deployment); for a product company
write `largest_node: n/a` and score the slack test alone. Inputs: the largest node's share of throughput
(facility, hub, region, corridor, port), the number of nodes and whether they are replicated units, any
disclosed loss of a node in the last five years with the revenue effect in that quarter, and alternative paths
named in filings.

| Band | Node test |
|---|---|
| 8 to 10 | largest node under 15 percent of throughput; or a disclosed loss of the largest node rerouted with a revenue effect under 5 percent in the quarter, cited |
| 5 to 7 | largest node 15 to 35 percent with two or more alternative nodes or paths named in filings; or hub-and-spoke where the spokes are replicated units |
| 2 to 4 | largest node 35 to 60 percent; or 15 to 35 percent with no rerouting evidence |
| 0 to 1 | largest node above 60 percent; or more than 60 percent of throughput inside one licence, concession or export-control regime named in the filings |

Node definition: for an asset-light company the largest node is the largest hosting region or facility
disclosed; when none is disclosed write `largest_node: none` and take 5 to 7 on this test. Precedence: the
share bands decide first; rerouting evidence moves a name only inside the 15 to 35 percent band. Where both
tests apply, E is the lower of the two.

**Hub rule.** A scale-free network is robust to random node loss and fragile to targeted loss of its hub, so
the deduction attaches to the single unreroutable hub, never to the existence of hubs and never to the size
of the company's position in its system. No credit is given under E for sensing.

## F · Clock: the adoption clock is computable (amended)

F_clock asks on what clock the correction lands, read from the mechanism doing the correcting (the clock
principle). Record `clock_basis` on the card.

- **Asset basis.** A company that owns or operates the slow stock itself (a corridor, a grid, a mains network,
  a housing stock, an aquifer) is always scored on that stock's turnover: decades 2 to 3, centuries 0 to 1.
  The existing band text applies to every other name as before: reimbursement or substitution, months to a
  few years, 5 to 6; regulation, litigation, technology displacement, years to a decade, 4 to 5; infrastructure
  or demographic cycles, decades, 2 to 3; soil, aquifers, oceans, climate, centuries, 0 to 1. Without the three
  adoption numbers below, 6 is unavailable.
- **Adoption basis** (override, lifts only). Available when the company sells a replicable unit (D_rep 4 or
  above) that is its largest revenue segment as disclosed, and all three numbers are cited: the ceiling from
  the C1 card, penetration, and the doubling time of units (or of unit revenue deflated by a disclosed average
  selling price) over the last eight quarters. Reimbursement is one adoption clock among several: a device on
  reimbursement, a meter on a procurement cycle and a coordination unit on a fleet are read from the same
  numbers.

| Band | Adoption basis |
|---|---|
| 5 to 6 | penetration 10 to 50 percent and doubling time of three years or less (the steep phase) |
| 4 to 5 | penetration 3 to 10 percent with doubling time of three years or less (early, real); or penetration 10 to 80 percent with doubling time above three years while unit growth still exceeds the growth of the ceiling (the shoulder) |
| asset basis stands | penetration under 3 percent (pre-inflection), unit growth at or below the ceiling's growth (saturated), or any of the three numbers missing |

The override can raise a band, never lower one: a name that cites the numbers keeps the higher of the two
readings, and a corridor owner is never read on the adoption basis. A retrofit at 1 percent of the fleet it
serves stays on its host stock's clock by measurement, not by assumption.

**F_now** (0 to 4), bands unchanged, evidence widened to parity: dated orders, approvals, backlog,
installed-base or active-unit growth in the last four quarters with a public number, 3 to 4; a public plan with
dates counts 2 to 3 only when an earlier milestone in that plan was met on schedule, both dates cited;
announced intentions with no met milestone, 0 to 1.

## The survivability gate (unchanged) and the developmental annotation

The gate is unchanged in every term: negative FCF with under 12 months runway and no committed financing,
three-year dilution above 25 percent, a pending buyout, going-concern doubt. A fail is a fail; there is no
carve-out. On a card that fails for dilution only, the scorer also records `developmental: yes` when all four
hold from filings, else `no`: (a) the company states a solvency point at a defined scale (units deployed,
installed base or revenue) with a date; (b) unit or segment gross margin is positive and rose in four of the
last four quarters; (c) segment or unit operating income is positive in the last two quarters; (d) runway at
the current burn is 24 months or more, or financing is committed to the stated point. The annotation changes
nothing: not the gate, not the tier, not the list. It exists so that after twelve months the engine can count
how many dilution fails were developmental and what became of them. Yolk is finite and sized to a stage; an
embryo that has not hatched when the yolk is gone is not a slow developer.

## The first screen, v2.1

### Class vocabulary

A first-screen class is a Layer 0 stock id or a registered alias for a group of them. The class
`infrastructure` is no longer a catch-all for enablers; it names the resilient-infrastructure stock and is
reached only by description.

| First-screen class | Layer 0 ids it attaches to |
|---|---|
| food | food, hanpp, soil, nutrients |
| water | water_access, freshwater, sanitation |
| shelter | shelter |
| energy | energy_access, ghg |
| health | healthcare |
| transport | transport, ghg (flag `coordination` for load matching, brokerage, intermodal) |
| tools | tools |
| information | information (flag `sensing`: the host stock measured is named at stage 3) |
| infrastructure | infrastructure (resilient infrastructure: repair over replacement, observability) |
| materials | materials, novel, forests (flag `circulation`: the recovery loop; flag `commodity`: extraction) |
| software, services, conglomerate | uninformative bases; the description attaches them as `software:<class>` (services and conglomerate keep the `software:` prefix for continuity of the funnel strings) or `<class>:<flag>` for other bases |
| finance, media, discretionary, retail, clothing, food-service, health-adjacent, unknown | below the bar; no attachment |

### Prior changes (the full table is data/rubric/prior_v21.json)

Relabels at unchanged numbers, exchange codes: Semiconductors 22, Telecommunications Equipment 20 (the
duplicate key with a trailing space is merged), Precision Instruments 20 (flag sensing), Computer peripheral
equipment 14 (enrich), Computer Manufacturing 16 (enrich) and Radio And Television Broadcasting And
Communications Equipment 15 (enrich, content-mix) to `information`; Industrial Machinery/Components 21,
Electronic Components 20, Tools/Hardware 16, Industrial Specialties 16 (enrich), Metal Fabrications 15 (enrich),
Professional and commerical equipment 14, Electronics Distribution 14, Wholesale Distributors 12 (enrich) and
Miscellaneous manufacturing industries 12 (enrich) to `tools`; Specialty Chemicals 16, Containers/Packaging 14,
Major Chemicals 12, Paper 12, Paints/Coatings 12 and Plastic Products 10 to `materials` (enrich, commodity flag
kept where present); Steel/Iron Ore 10, Aluminum 10, Mining & Quarrying of Nonmetallic Minerals 10, Metal
Mining 8 and Other Metals and Minerals 8 keep `materials` and gain enrich; Environmental Services 25 moves
from `water` to `materials` with flag circulation. Yahoo entries: Semiconductors 22, Communication Equipment 20,
Scientific & Technical Instruments 22 (sensing), Computer Hardware 14 (desc) to `information`; Semiconductor
Equipment & Materials 22, Specialty Industrial Machinery 22, Electronic Components 20, Industrial Distribution
16 (desc), Tools & Accessories 16, Metal Fabrication 15 (desc) to `tools`; Specialty Chemicals 16, Packaging &
Containers 14, Chemicals 12, Paper & Paper Products 12 (all desc), Steel 10, Aluminum 10, Copper 12, Other
Industrial Metals & Mining 8 (all desc, commodity kept) and Waste Management 25 (circulation) to `materials`;
Infrastructure Operations 20 to `transport`; Conglomerates 12 and Trucking 18 gain desc.

Parity fixes (each a documented same-evidence or same-business gap between two table entries): Yahoo Telecom
Services 14 to 20, class `information`, flag utility-slow-growth (28 carriers under the exchange code
Telecommunications Equipment already carry 20 while 62 no-code carriers of the same business carried 14; a
delivery utility of the information deficit is priced between Natural Gas Distribution 18 and Electric
Utilities 22, with the same slow-growth flag); Yahoo Information Technology Services 10 to 12 (identical
software:health evidence advanced at Software - Application 12 plus 8 and failed at 10 plus 8; 40 names);
Yahoo Specialty Business Services 8 to 10 and the exchange codes Business, Professional and Diversified
Commercial Services 8 to 10 (at 8 the enrich flag was dead code: no boost reaches 20); EDP Services and
Programming Data Processing 10 to 12 for consistency with Prepackaged Software (inert for profiled names,
whose base is the Yahoo entry). Route fixes at unchanged numbers: Computer Communications Equipment 18 gains
enrich (the code mixes carriage hardware with enterprise IT; the Yahoo entry and the description decide);
Transportation Services 18 gains enrich (the code holds online travel, charter aviation and tankers beside
freight coordination; the Yahoo entry decides, and a travel name falls to Travel Services 4); Cable & Other Pay
Television Services 6 to 12, class `information`, flags enrich, content-mix and rent-extraction-risk (the code
mixes broadband carriage with content; after the profile fetch a carrier lands on Telecom Services 20 and a
content name on Entertainment 2; inert until fetched). Multi-Sector Companies 10 keeps its enrich flag and the
boost loop now covers the conglomerate class, which it never did.

Rejected from the tables, with the reason: Transportation Services to 20 (the 21 viable names are Booking,
Expedia, Virgin Galactic, charter aviation and LPG tankers; four are freight coordination); Precision
Instruments to 22 (the registered v2.0 prior is 20); a description route for Telecom Services (every carrier
description matches broadband or 5G, so the boost could not fail); the SEMICONDUCT name line at 20 (the
name-only discount elsewhere in the table is 6 to 9 points, not 2); Marine Transportation to 18 (not one of the
identified biases; deferred).

### Description boosts (second pass), in order; on equal boosts the earlier entry wins

The boost is added to the Yahoo base of any entry carrying the desc flag and of every entry in the classes
software, services and conglomerate; the single largest boost applies; the boosted total is capped at 24; the
words artificial intelligence, AI and machine learning are barred from every regex (199 of 3,055 stage 2
descriptions carry them and they are claims, not functions). Descriptions are matched in lower case.

| Order | Regex (lower case) | Boost | Label |
|---|---|---|---|
| 1 | `water\|wastewater\|irrigat\|desalin` | 10 | water (unchanged) |
| 2 | `grid\|smart meter\|energy management\|energy efficien\|renewable\|solar\|battery\|ev charg` | 10 | energy (unchanged) |
| 3 | `recycl\|\bscrap\b\|secondary (metal\|alumin\|steel\|fib\|material\|raw material)\|remanufactur\|reverse logistics\|deposit[- ]return\|electric arc furnace\|\beaf\b\|recovered (fiber\|fibre\|paper\|material\|metal\|carbon)\|e-waste\|refurbish\|tailings (re\|retreat\|reprocess)` | 10 | circulation (class materials, flag circulation) |
| 4 | `agricultur\|farm\|food safety\|crop` | 9 | food (unchanged) |
| 5 | `health\|clinical\|patient\|hospital\|medical\|diagnos\|pharma` | 8 | health (unchanged) |
| 6 | `logistics\|freight\|fleet\|transport\|rail\|transit\|supply chain` | 8 | transport (unchanged) |
| 7 | `construction\|building information\|infrastructure (software\|management)\|geospatial\|survey` | 8 | shelter (unchanged) |
| 8 | `\bsensors?\b\|telemat\|smart meter\|advanced metering\|condition monitor\|predictive maintenance\|leak detection\|earth observation\|satellite imag\|lidar\|remote monitoring\|\biot\b\|structural health monitoring` | 8 | sensing (class information, flag sensing) |
| 9 | `data cent(er\|re)\|semiconductor (manufactur\|fabricat)\|wafer\|foundry\|broadband\|fiber[- ]optic\|fibre[- ]optic\|optical fib\|wireless carrier\|mobile network operator\|\b5g\b\|satellite communic\|internet service provider\|network infrastructure\|optical transport` | 8 | information |
| 10 | `industrial automation\|factory automation\|automation equipment\|robot\|machine tool\|\bcnc\b\|manufacturing execution\|\bplc\b\|\bscada\b\|motion control` | 8 | tools (replaces the 6-point `manufactur` entry, which matched 36 percent of all stage 2 descriptions) |
| 11 | `grid (resilien\|hardening)\|asset integrity\|non[- ]?destructive testing\|pipeline (inspection\|integrity)\|structural health\|trenchless\|corrosion (monitoring\|protection)\|infrastructure (inspection\|monitoring)` | 8 | infrastructure (resilient infrastructure) |
| 12 | `freight matching\|load matching\|empty mile\|freight broker\|third[- ]party logistics\|\b3pl\b\|intermodal\|route optimi\|digital freight` | 8 | coordination (class transport, flag coordination; for a software base entry 6 already matches) |
| 13 | `cybersecurity\|network security\|endpoint (security\|protection)\|identity and access` | 4 | security (records the match; 12 plus 4 never crosses; enterprise security names no Layer 0 stock) |

Excluded on measured hit rates, and not to be re-added without a new measurement: bare `manufactur` (1,094 of
3,055), bare `monitoring` (199), `inspection`, `predictive`, `forecast`, bare `fiber` (glass, dietary and
textile fibre), `gpu`, `accelerator`, `inference`, `edge comput`, `cloud infrastructure`, `hyperscale`,
`circular`, `closed-loop`, `reuse`, `reclaim`, `end-of-life` (adjectives without a noun), `dispatch`, `fleet
management`, `supply chain management`, `workforce management`.

### Name patterns (names with no exchange code and no profile), in order; first match wins

| Order | Regex (upper case) | Prior | Class and flag |
|---|---|---|---|
| 1 | `WATER\|AQUA\|HYDRAUL\|IRRIGAT\|DESALIN\|WASTEWATER` | 24 | water |
| 2 | `\bFOOD\|FARM\|AGRI\|AGRO\|DAIRY\|GRAIN\|SEED\|CROP\|NUTRI\|BAKER\|MEAT\b\|FISHER` | 22 | food |
| 3 | `\bSOLAR\|RENEWABLE\|GEOTHERM\|HYDRO(?!GEN)\|WIND ENERG\|ENERG\|\bPOWER\|ELECTRIC\|GRID\|BATTER\|UTILIT` | 20 | energy (POWER now bounded: EMPOWER and MANPOWER no longer score 20) |
| 4 | `PHARMA\|THERAPEUT\|BIOSCI\|MEDIC\|HEALTH\|DIAGNOST\|SURG\|DENTAL\|CLINIC\|HOSPITAL\|VACCIN\|BIOTECH\|LIFE SCIENCE` | 20 | health |
| 5 | `\bRAIL\|TRANSIT\|TRANSPORT\|LOGISTIC\|FREIGHT\|INTERMODAL\|\bFLEET\|SHIPPING\|MARITIME\|AIRLINE\|MOTOR\|\bAUTO\b\|VEHICLE\|MOBILITY` | 18 | transport (FREIGHT, INTERMODAL, FLEET added at the unchanged number) |
| 6 | `CONSTRUCT\|BUILD\|HOME\|HOUS\|CEMENT\|CONCRETE\|LUMBER\|TIMBER\|STEEL\|INFRASTRUCT` | 18 | shelter (unchanged) |
| 7 | `RECYCL\|CIRCULAR\|REMANUFACTUR\|\bSCRAP\b\|SALVAGE\|WASTE\|ENVIRONMENT` | 22 | materials, flag circulation (split from the old infrastructure line; SUSTAINAB removed) |
| 8 | `\bBANK\|BANC\|FINANC\|CAPITAL\|INSUR\|INVEST\|ASSET\|WEALTH\|MORTGAGE\|CREDIT\|FUND\b\|SECURITIES\|REALTY\|PROPERTIES\|REIT\b` | 4 | finance (moved ahead of the enabler lines so Bank of Communications is a bank) |
| 9 | `SEMICONDUCT\|MICROELECTRON\|PHOTONIC\|TELECOM\|WIRELESS\|BROADBAND\|\bNETWORK\|COMMUNICAT\|SATELLIT\|DATA CENT` | 15 | information, flag enrich-if-viable |
| 10 | `SENSOR\|SENSING\|INSTRUMENT\|METROLOG\|LIDAR\|TELEMAT\|GEOSPATIAL\|\bMETER(ING)?\b` | 15 | information, flags sensing and enrich-if-viable (METER bounded: PARAMETER and KILOMETER excluded) |
| 11 | `INDUSTRI\|MANUFACTUR\|MACHIN\|ENGINEER\|AUTOMAT\|ROBOT\|\bTOOL` | 15 | tools, flag enrich-if-viable |
| 12 | `MATERIAL\|CHEMICAL\|POLYMER\|ALLOY\|\bMETAL` | 15 | materials, flag enrich-if-viable |
| 13 | `SOFTWARE\|DIGITAL\|\bDATA\b\|ANALYTIC\|\bCLOUD\b\|PLATFORM` | 12 | software, flag enrich-if-viable (was unknown 8) |
| 14 | `SUSTAINAB\|\bGREEN\b\|\bECO\b\|CLIMATE` | 10 | unknown, flag enrich-if-viable (marketing words; SUSTAINAB earned 22 before) |
| 15 | `MEDIA\|ENTERTAIN\|STUDIO\|GAMES\|RESORT\|RESTAURANT\|BRANDS\|RETAIL\|FASHION\|LUXURY` | 4 | discretionary (unchanged) |
| else | | 8 | unknown, flag enrich-if-viable |

No name line crosses the bar on an information, tools, materials or software word alone; the class it sets
routes the row to the profile fetch with a Layer 0 attachment already named. The hard-reject name patterns are
unchanged.

### Priors for classified overrides and hybrids (class_prior in prior_v21.json)

The 367 keyword-only names classified by web research on 2 Sep 2026 are priced by their override class at the
name-line number for that class, because the classifier read a profile the screen did not have but not a
description the boost could act on: water 24, food 22, circulation 22, energy 20, health 20, transport 18,
shelter 18, information 15, tools 15, infrastructure 15, materials 12, coordination 12, software 12,
conglomerate 10, materials_extraction 8, services 8, unknown 8, finance 4, discretionary 4,
media_entertainment 2; shell_or_dead (operating false) is a reject as before. Hybrid labels (`software:<x>`,
`materials:circulation`) are never keys in class_prior: a hybrid is priced as base plus boost and the delta
script must not overwrite it by class.

### Obligations on the pipeline (a logic change under register_logic.py, version v2.1)

1. `round1_v21.py` applies class-only relabels (it currently re-prices only when the number differs) and keeps
   the regression: a v2.0 prior file reproduces the recorded screen name for name.
2. `round1_merge_enriched.py`: the boost loop runs when the Yahoo entry carries desc or the class is software,
   services or conglomerate (the condition was `fl == "desc"`, which a `commodity desc` flag would miss); the
   hybrid label is `software:<label>` for software and services bases and `<class>:<label>` otherwise; the
   boosted total is capped at 24; ties resolve by list order.
3. `fetch_profiles.py` fetches every viable name in a code that now carries enrich (about 330 names in Metal
   Fabrications, Industrial Specialties, Major Chemicals, Steel/Iron Ore, Containers/Packaging, Paper, Plastic
   Products, Radio and Television equipment, Computer peripheral equipment, Cable, Metal Mining, Nonmetallic
   Minerals and Other Metals). Enrich obligation: no need cut is recorded on a viable name in an enrich or
   desc code until its description has been read; when no description exists the cut reason says `no
   description available`, so the false-negative sample can target it.
4. The 2026-08-28 vintages stay frozen and are graded on v2.0 scores; the v2.1 re-screen is a new instrument
   compared only with itself, and the predictions below are registered as a superseding protocol entry that
   preserves every v2.0 endpoint unchanged.

### Stage 2 admissibility

A stage 2 cut of a name whose first-screen class is a Layer 0 id or alias (food, water, shelter, energy,
health, transport, tools, information, infrastructure, materials, and any `software:` or flagged sub-label)
must name the missing B item: `no host flow named`, `no host number`, `attribution not computable`, `rebound
induced`, or a survivability fact. The words enabler, indirect need and not a direct need are not banned; they
are simply not a reason, because Layer 0 names compute, connectivity, observability and secondary material as
corrections, and a cut must say which number is missing. The rule applies to every class equally, including
regulated utilities. The R1.5 clinical-stage programmatic cut is unchanged and no first-screen analogue is
added for coordination names.

## Registration and pre-registration

This section is a `--logic` change: the version becomes v2.1, the refresh queue owes a full universe re-screen
and a ranked re-score, and the predictions registered beside it (advance count, per-family admissions, the
health control group, stage 2 vocabulary and pass rates, ranked-cluster means, blind-scorer agreement and the
universe information coefficient) are committed before the re-screen runs. Each has a lower falsifier for an
inert change and an upper falsifier for a floodgate; the media and extraction lines are guards, since the
proposal claims connectivity is the deficit and content is not, and circulation is the correction and
extraction is not. A rule that fails its falsifier is withdrawn to its v2.0 text at the next registration, and
the withdrawal is published.
