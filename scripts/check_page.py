# -*- coding: utf-8 -*-
import os
from paths import BUILD
import re, json
P = os.path.join(BUILD, "bs_console.html")
h = open(P, encoding="utf-8").read()

em = h.count("\u2014")
print(f"em dashes in page: {em}")
if em:
    for m in re.finditer(r".{0,70}\u2014.{0,70}", h):
        print("   ..." + m.group(0).replace("\n", " ") + "...")

# stale references to the retired engine
stale = ["Permanent need", "Cost compression", "expansion signal", "System balance / biomimicry",
         "Global scale velocity", "Proven functions", "eight dimensions", "deeper audit still pending"]
print("\nstale v1 language still on the page:")
hits = [s for s in stale if s in h]
print("  " + (", ".join(hits) if hits else "none"))

# svg sanity
svg = re.search(r"<svg[\s\S]*?</svg>", h)
print(f"\nsvg present: {bool(svg)}")
if svg:
    s = svg.group(0)
    for tag in ["marker", "rect", "line", "path", "text", "g"]:
        o, c = len(re.findall(f"<{tag}[ >]", s)), len(re.findall(f"</{tag}>", s)) + len(re.findall(f"<{tag}[^>]*/>", s))
        flag = "" if o == c else "   <-- UNBALANCED"
        print(f"   {tag:<7s} open {o:>2d}  closed {c:>2d}{flag}")
    print(f"   uses currentColor: {'currentColor' in s}  uses var(--accent): {'var(--accent)' in s}")
    print(f"   has role/aria: {'role=' in s and 'aria-label=' in s}")
    print(f"   no script/style/foreignObject inside: "
          f"{not any(t in s for t in ['<script', '<style', '<foreignObject'])}")

# the six measures should appear as a set
for lbl in ["The stock", "The flow", "The loop", "Growth pattern", "Buffer", "Clock"]:
    print(f"   measure '{lbl}' present: {lbl in h}")
print(f"\npage size: {len(h)/1024:.0f} KB")
