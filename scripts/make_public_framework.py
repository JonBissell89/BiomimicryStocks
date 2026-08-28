# -*- coding: utf-8 -*-
"""Publish the framework's rules without publishing anyone's positions.

HOLDING_FRAMEWORK.md sits outside this repo on purpose: its closing section names
real holdings, real gains and a real cash balance. The rules above that section are
the valuable part and are safe to share, so copy them and stop at the boundary.

Re-run this if the framework doc changes. It refuses rather than guesses if the
personal section is not where it expects.
"""
import os, re, sys
from paths import ROOT

SRC = os.path.join(os.path.dirname(ROOT), "HOLDING_FRAMEWORK.md")
DST = os.path.join(ROOT, "FRAMEWORK.md")
CUT = "## Where your current portfolio sits in this framework"

if not os.path.exists(SRC):
    sys.exit(f"source not found: {SRC}")
t = open(SRC, encoding="utf-8").read()
if CUT not in t:
    sys.exit("the personal section header moved. Refusing to guess where to cut; "
             "check HOLDING_FRAMEWORK.md and update CUT in this script.")

public = t.split(CUT)[0].rstrip()

# Two lines above the cut still enumerate the owner's actual holdings. A single
# ticker paired with a ruling is fine, that is the framework judging a public
# company. The exact set listed together IS the portfolio, so it goes.
REDACT = [
 (r"- \*\*From your current holdings:\*\* BFLY[^\n]*",
  "- **Watch bench examples:** BFLY (rated A on mission; objection = no margin path yet, "
  "promotable on two consecutive gross-margin-expanding, loss-narrowing quarters) and SRTA "
  "(rated A; objection = unprofitable number two against TransMedics, promotable on sustained "
  "profitability or a competitive win). Both reached the top 0.7% of the field; Watch-class is "
  "not an error."),
 (r"Hard-rule and gate failures\. From your current holdings:[^\n]*",
  "Hard-rule and gate failures. Worked examples of the rules biting: a cannabis producer on the "
  "addiction rule, a gold miner on no durable need, a life insurer on financial intermediation, "
  "a clinical-psychedelics name on the single-unproven-breakthrough rule, a utility roll-up with "
  "no product layer, and several pre-revenue names where the thesis is plausible but the "
  "economics are unproven. The tournament's consistent finding was that thesis and economics "
  "must both be true."),
]
for pat, sub in REDACT:
    public = re.sub(pat, sub, public)

# The disclosure is possessive framing, balances and net worth, not the mere
# presence of a ticker in a rules document.
# "Every security you hold or consider" is generic framework prose, not a
# disclosure, so the check targets statements about what someone actually holds.
LEAK = [(r"\$\s?2,?788", "cash balance"),
        (r"accredited investor|2,000,000", "net worth claim"),
        (r"your current portfolio|your current holdings|from your holdings|My new stack",
         "possessive holdings language"),
        (r"ACB[^\n]{0,80}AGI[^\n]{0,80}MFC", "the real holdings set, enumerated")]
found = [lab for pat, lab in LEAK if re.search(pat, public, re.I)]
if found:
    sys.exit(f"personal content survived the cut: {found}. Not writing.")

public += """

---

*This is the public copy. The private working document continues past this point with
one section classifying a specific person's actual holdings against these rules. That
section is deliberately not published, and nothing in this repository contains anyone's
real positions, balances or trades. The $5,000 in the simulation is pretend money.*
"""
open(DST, "w", encoding="utf-8").write(public)
kept = len(public.split("\n"))
dropped = len(t.split("\n")) - kept
print(f"wrote FRAMEWORK.md: kept {kept} lines, dropped {dropped} personal lines")
print("leak check: clean")
