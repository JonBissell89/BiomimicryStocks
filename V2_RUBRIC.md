# The Stock and Flow Scorecard (engine v2)

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
