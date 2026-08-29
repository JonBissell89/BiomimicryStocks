# -*- coding: utf-8 -*-
"""What is in the repo, what is deliberately outside it, and what is neither.

The repo root is the tournament folder, not the Stocks folder, so anything living
one level up is outside version control. Some of that is deliberate. Anything
that is neither tracked nor deliberately excluded is a gap worth knowing about.
"""
import os, subprocess
from paths import ROOT

os.chdir(ROOT)
tracked = set(subprocess.run(["git", "ls-files"], capture_output=True, text=True)
              .stdout.split("\n"))
ignored = subprocess.run(["git", "ls-files", "--others", "--ignored", "--exclude-standard"],
                         capture_output=True, text=True).stdout.split("\n")
untracked = [f for f in subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                                       capture_output=True, text=True).stdout.split("\n") if f]

print(f"REPO  {ROOT}")
print(f"  tracked files: {len([t for t in tracked if t])}")
size = sum(os.path.getsize(t) for t in tracked if t and os.path.exists(t))
print(f"  tracked size:  {size/1024/1024:.1f} MB")

print("\nIGNORED ON PURPOSE (inside the repo folder, not committed)")
seen = set()
for f in ignored:
    if not f:
        continue
    top = f.split("/")[0]
    if top in seen:
        continue
    seen.add(top)
    p = os.path.join(ROOT, top)
    sz = (os.path.getsize(p) / 1024 / 1024 if os.path.isfile(p)
          else sum(os.path.getsize(os.path.join(r, x))
                   for r, _, fs in os.walk(p) for x in fs) / 1024 / 1024)
    print(f"  {top:<28s} {sz:6.1f} MB")

if untracked:
    print("\nUNTRACKED AND NOT IGNORED (would be committed on the next `git add -A`)")
    for f in untracked[:20]:
        print(f"  {f}")
else:
    print("\nUNTRACKED AND NOT IGNORED: none")

parent = os.path.dirname(ROOT)
print(f"\nOUTSIDE THE REPO ENTIRELY  ({parent})")
for name in sorted(os.listdir(parent)):
    p = os.path.join(parent, name)
    if os.path.abspath(p) == os.path.abspath(ROOT):
        continue
    if os.path.isfile(p):
        kb = os.path.getsize(p) / 1024
        why = ""
        if name == "HOLDING_FRAMEWORK.md":
            why = "  <- deliberately out: holds real positions and a cash balance"
        print(f"  {name:<34s} {kb:8.0f} KB{why}")
    else:
        print(f"  {name}/")
