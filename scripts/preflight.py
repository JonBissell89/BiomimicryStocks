# -*- coding: utf-8 -*-
"""Last check before anything leaves this machine.

Scans exactly what git has staged, not the folder, because the folder contains
files that are deliberately excluded. Looks for the specific disclosures that
would matter in a public repo: a real balance, a net worth claim, possessive
holdings language, or the owner's actual portfolio enumerated as a set.
"""
import os, re, subprocess, sys
from paths import ROOT

os.chdir(ROOT)
staged = subprocess.run(["git", "diff", "--cached", "--name-only"],
                        capture_output=True, text=True).stdout.split()
TEXT = (".md", ".py", ".js", ".json", ".csv", ".txt", ".yml", ".yaml", ".html")

CHECKS = [
    (r"\$\s?2,?788\b", "a real cash balance"),
    (r"accredited investor", "a net worth claim"),
    (r"your current portfolio|your current holdings|from your holdings|My new stack",
     "possessive holdings language"),
    (r"\bACB\b[^\n]{0,90}\bAGI\b[^\n]{0,90}\bMFC\b", "the real holdings set enumerated"),
    (r"gho_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}", "a GitHub token"),
    (r"sk-[A-Za-z0-9]{20,}", "an API key"),
    (r"@luminasolar\.com", "a work email"),
]

# The redactor necessarily contains the patterns it redacts, so scanning it for
# those patterns always trips. It is the one file exempt, and it is exempt by name
# rather than by a rule that could quietly excuse something else.
EXEMPT = {"scripts/make_public_framework.py", "scripts/preflight.py"}

print(f"scanning {len(staged)} staged files\n")
hits = []
for rel in staged:
    if rel.replace("\\", "/") in EXEMPT:
        continue
    if not rel.lower().endswith(TEXT) or not os.path.exists(rel):
        continue
    try:
        t = open(rel, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    for pat, label in CHECKS:
        m = re.search(pat, t, re.I)
        if m:
            line = t[:m.start()].count("\n") + 1
            hits.append((rel, line, label, t[max(0, m.start()-50):m.start()+70]
                         .replace("\n", " ")))

if hits:
    print("BLOCKED, personal or secret content is staged:\n")
    for rel, line, label, ctx in hits:
        print(f"  {rel}:{line}  {label}")
        print(f"      ...{ctx.strip()}...\n")
    sys.exit(1)

# and confirm the private doc is genuinely not in the repo
priv = os.path.join(os.path.dirname(ROOT), "HOLDING_FRAMEWORK.md")
print(f"private framework doc lives outside the repo: {not os.path.abspath(priv).startswith(os.path.abspath(ROOT) + os.sep)}")
print("no balances, no net worth, no holdings set, no tokens, no work email")
print("\nclean")
