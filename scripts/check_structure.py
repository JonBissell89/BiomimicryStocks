# -*- coding: utf-8 -*-
"""Verify the Step 3 restructure landed: sections merged, controls swapped,
add-row present, mobile rules present, nothing orphaned."""
import os
from paths import BUILD
import re
P = os.path.join(BUILD, "bs_console.html")
h = open(P, encoding="utf-8").read()

print("SECTIONS")
for m in re.finditer(r'<section[^>]*id="([^"]+)"', h):
    sid = m.group(1)
    step = re.search(r'<p class="step">([^<]*)</p>', h[m.start():m.start() + 400])
    print(f"  #{sid:<9s} {step.group(1) if step else ''}")

print("\nGONE (should all be False)")
for k, pat in [("#lookup section", r'<section[^>]*id="lookup"'),
               ("#money section", r'<section[^>]*id="money"'),
               ("SoFi checkbox", r'id="sf"'),
               ("health filter checkbox", r'id="vf"'),
               ("'Only stocks on SoFi'", r'Only stocks on SoFi'),
               ("'Hide insurance-premium'", r'Hide insurance-premium'),
               ("count in the h2", r'<h2>Results: the \d'),
               ("lump-sum planner", r'Spread a lump sum'),
               ("planner panel", r'id="planpanel"'),
               ("tier sliders", r'id="p1"'),
               ("weight column", r'data-l="Wt"'),
               ("plan column", r'data-l="Plan \$"'),
               ("duplicate add affordance", r"jumpadd|addfoot")]:
    print(f"  {k:<26s} {bool(re.search(pat, h))}")

print("\nPRESENT (should all be True)")
for k, pat in [("market select", r'id="mktsel"'),
               ("market options", r'value="adr"'),
               ("add-row button", r'id="qbtn">Add row'),
               ("added-row storage", r"bsAdded"),
               ("marketOf()", r"function marketOf"),
               ("allRows()", r"function allRows"),
               ("addedRow()", r"function addedRow"),
               ("drop button handler", r"data-drop"),
               ("PX price map", r"window\.__PX"),
               ("mobile table rules", r"table\.mkt thead\{position:absolute"),
               ("data-l labels", r'data-l="Ticker"'),
               ("own-row style", r"tr\.ownrow"),
               ("Results summary heading", r"<h2>Results summary</h2>"),
               ("Results heading", r'<h2 style="margin-top:30px">Results</h2>'),
               ("tier summary chips", r'class="tiersum"'),
               ("add bar at the table", r'class="addbar"'),
               ("Step 4 track", r"Step 4 · How you&#x27;re doing|Step 4 · How you're doing")]:
    print(f"  {k:<26s} {bool(re.search(pat, h))}")

print("\nHYGIENE")
print(f"  em dashes: {h.count(chr(8212))}")
ids = re.findall(r"\$\('([a-zA-Z0-9_]+)'\)", h)
missing = sorted({i for i in set(ids) if f'id="{i}"' not in h})
print(f"  JS references to element ids that do not exist: {missing if missing else 'none'}")
print(f"  page size: {len(h)//1024} KB")
