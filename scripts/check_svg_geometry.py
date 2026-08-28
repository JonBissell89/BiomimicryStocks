# -*- coding: utf-8 -*-
"""Geometry check on the stock-and-flow figure: everything inside the viewBox,
text inside its box, no element collisions."""
import os
from paths import BUILD
import re
P = os.path.join(BUILD, "bs_console.html")
s = re.search(r"<svg[\s\S]*?</svg>", open(P, encoding="utf-8").read()).group(0)
VW, VH = [float(x) for x in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', s).groups()]
print(f"viewBox {VW:.0f} x {VH:.0f}")

rects = [tuple(float(g) for g in m.groups()) for m in
         re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', s)]
texts = [(float(m.group(1)), float(m.group(2)), m.group(3)) for m in
         re.finditer(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*>([^<]*)</text>', s)]
lines = [tuple(float(g) for g in m.groups()) for m in
         re.finditer(r'<line x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', s)]

bad = 0
for x, y, w, h in rects:
    print(f"  rect  x {x:>5.0f}-{x+w:<5.0f} y {y:>5.0f}-{y+h:<5.0f}")
    if x < 0 or y < 0 or x + w > VW or y + h > VH:
        print("        OUT OF VIEWBOX"); bad += 1
for x1, y1, x2, y2 in lines:
    if max(x1, x2) > VW or max(y1, y2) > VH:
        print(f"  line ({x1},{y1})->({x2},{y2}) OUT OF VIEWBOX"); bad += 1

# does the arrowhead of each line clear the next shape?
xs = sorted([(x, x + w) for x, y, w, h in rects])
for i in range(len(xs) - 1):
    gap = xs[i + 1][0] - xs[i][1]
    print(f"  gap between boxes: {gap:.0f}px" + ("  TOO TIGHT" if gap < 40 else ""))

print("\n  text placement:")
for x, y, t in texts:
    inside = [i for i, (rx, ry, rw, rh) in enumerate(rects)
              if rx <= x <= rx + rw and ry <= y <= ry + rh]
    where = f"inside rect {inside[0]}" if inside else "free-standing"
    oob = " OUTSIDE VIEWBOX" if not (0 <= x <= VW and 0 <= y <= VH) else ""
    if oob:
        bad += 1
    print(f"    ({x:>5.0f},{y:>5.0f}) {where:<16s} {t[:42]!r}{oob}")

print(f"\n  problems: {bad}")
