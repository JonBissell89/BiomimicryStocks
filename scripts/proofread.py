# -*- coding: utf-8 -*-
"""Mechanical proofread of the rendered page.

Catches what a human eye slides over: duplicated sentences, orphaned controls,
promises the page no longer keeps, doubled words, and stale references to things
that were removed. Judgment about tone still needs reading it.
"""
import os, re, collections
from paths import BUILD

h = open(os.path.join(BUILD, "bs_console.html"), encoding="utf-8").read()
# strip script and style so we proofread prose, not code
prose_html = re.sub(r"<(script|style)\b[^>]*>[\s\S]*?</\1>", " ", h)
text = re.sub(r"<[^>]+>", " ", prose_html)
text = re.sub(r"&[a-z]+;|&#\d+;", " ", text)
text = re.sub(r"\s+", " ", text)

issues = 0

def flag(label, items, limit=6):
    global issues
    items = list(items)
    if not items:
        return
    issues += len(items)
    print(f"\n{label}  ({len(items)})")
    for it in items[:limit]:
        print(f"   {it}")
    if len(items) > limit:
        print(f"   ... and {len(items)-limit} more")

# 1. duplicated sentences
sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 45]
dupes = [f'"{s[:88]}..."' for s, c in collections.Counter(sents).items() if c > 1]
flag("DUPLICATED SENTENCES", dupes)

# 2. doubled words
flag("DOUBLED WORDS", {f'"{m.group(0)}"' for m in
     re.finditer(r"\b(\w+)\s+\1\b", text, re.I)
     if m.group(1).lower() not in ("that", "had") and not m.group(1).isdigit()})

# 3. buttons and inputs with no JS handler
ids = re.findall(r'<(?:button|input|select)[^>]*\bid="([^"]+)"', h)
scripts = "".join(re.findall(r"<script\b[^>]*>([\s\S]*?)</script>", h))
orphan = [i for i in ids if f"'{i}'" not in scripts and f'"{i}"' not in scripts]
flag("CONTROLS WITH NO HANDLER", orphan)

# 4. JS referencing element ids that do not exist
refs = set(re.findall(r"\$\('([A-Za-z0-9_]+)'\)", scripts))
missing = [r for r in refs if f'id="{r}"' not in h]
flag("JS REFERENCES A MISSING ELEMENT", missing)

# 5. promises the page no longer keeps
STALE = {
    r"\bplanner\b": "the planner was removed",
    r"spread a lump sum": "the planner was removed",
    r"Only stocks on SoFi": "the SoFi filter was removed",
    r"Hide insurance-premium": "the health filter was removed",
    r"1st of (?:each|every) month": "the cadence is weekly now",
    r"refresh monthly|prices refresh monthly": "the cadence is weekly now",
    r"scorecard code": "renamed to profile",
    r"Compare with friends": "renamed to Leaderboard",
    r"\bStep 5\b|\bStep 6\b": "steps were merged; only 1 to 4 exist",
    r"the next step": "sections were merged, check this still points somewhere",
}
flag("STALE PROMISES", [f'"{p}"  -> {why}' for p, why in STALE.items()
                        if re.search(p, text, re.I)])

# 6. duplicate visible button labels
labels = [re.sub(r"<[^>]+>", "", m).strip() for m in
          re.findall(r"<button[^>]*>([\s\S]*?)</button>", prose_html)]
labels = [l for l in labels if l]
flag("DUPLICATE BUTTON LABELS", [f'"{l}" x{c}' for l, c in
                                 collections.Counter(labels).items() if c > 1])

# 7. straight quotes and typography
flag("TYPOGRAPHY", ([f"em dashes: {text.count(chr(8212))}"] if chr(8212) in text else [])
     + ([f'double spaces after a period: {len(re.findall(r"[.] {2,}[A-Z]", text))}']
        if re.findall(r"[.] {2,}[A-Z]", text) else []))

# 8. headings outline
print("\nHEADING OUTLINE")
for m in re.finditer(r"<(h[12345])[^>]*>([\s\S]*?)</\1>", prose_html):
    lvl = int(m.group(1)[1])
    t = re.sub(r"<[^>]+>", "", m.group(2)).strip()
    print("   " + "  " * (lvl - 1) + f"h{lvl}  {t[:70]}")

print(f"\n{'=' * 60}")
print(f"issues found: {issues}")
if issues:
    raise SystemExit(1)
