# -*- coding: utf-8 -*-
"""The screen's error bar: what did the funnel cut, and how close was it?

Counts every stage of the funnel, lists the near-miss frontier (names that
passed the business review and were cut on growth and finances), and draws a
deterministic, seeded sample of cut names for a blind re-score, so the false
negative rate can become a measurement instead of a hope. The sample sits
here as an open obligation until the re-scores exist."""
import json, os, random
from collections import Counter
from paths import DATA

si = json.load(open(os.path.join(DATA, "search_index.json"), encoding="utf-8"))
STAGE = {"0": "cut on the first screen", "1": "too small, shell, or sub-5c",
         "2": "screened, did not advance", "3": "passed review, cut on growth and finances",
         "4": "late-round cut", "R": "made the list", "X": "removed"}
stages = Counter(v[1] for v in si.values())
near = sorted(((tk, v[0], v[2]) for tk, v in si.items() if v[1] == "3"),
              key=lambda x: -x[2])[:20]
rng = random.Random(42)
pools = {s: [tk for tk, v in si.items() if v[1] == s] for s in ("0", "2", "3")}
sample = {s: sorted(rng.sample(p, 4)) for s, p in pools.items()}
doc = {"funnel": {s: {"count": c, "meaning": STAGE.get(s, "?")} for s, c in sorted(stages.items())},
       "near_miss_frontier": [{"tk": t, "name": n, "first_screen_score": s} for t, n, s in near],
       "blind_rescore_sample": {"seed": 42, "status": "awaiting research; the false-negative rate is unmeasured until these are deeply scored",
                                 "picks": sample},
       "reading": "the frontier names are the screen's most likely false negatives; the seeded sample is the audit that would measure the rate"}
json.dump(doc, open(os.path.join(DATA, "rigor", "coverage.json"), "w"), indent=1)
print("coverage: funnel", dict(stages), "| near-miss top:", [t for t, _, _ in near[:5]])
