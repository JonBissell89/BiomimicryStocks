# -*- coding: utf-8 -*-
import os
from paths import DATA
import json, re
D = DATA
d = json.load(open(os.path.join(D, "engine_tiers.json"), encoding="utf-8"))
blob = json.dumps(d, ensure_ascii=False)
EM = "\u2014"
print("EM DASH CONTEXTS")
for m in re.finditer(r".{0,80}" + EM + r".{0,80}", blob):
    print("  ..." + m.group(0).replace("\n", " ") + "...")
print()
print("MORAL-WORD CONTEXTS")
for w in ["bad company", "philosophically good"]:
    for m in re.finditer(r".{0,110}" + w + r".{0,110}", blob, re.I):
        print("  ..." + m.group(0).replace("\n", " ") + "...")
print()
print("BLANK EVIDENCE ROWS")
for t in d["tiers"]:
    for n in t["names"]:
        if not str(n.get("evidence", "")).strip():
            print(f"  {n['tk']} ({n['nm']}) score {n['score']} B={n['dims']['B']}")
            print(f"     note: {str(n.get('note',''))[:220]}")
