# -*- coding: utf-8 -*-
"""Put the rendered console where GitHub Pages will serve it.

Pages can deploy straight from a folder in the repo, which needs only the `repo`
scope. That sidesteps the workflow-scope wall entirely: any weekly job that can
commit and push can also publish, with no GitHub Actions involved.

The artifact host wraps the page in a head skeleton for free. Static hosting does
not, so the wrapping happens here.
"""
import os, shutil
from paths import ROOT, BUILD

SRC = os.path.join(BUILD, "bs_console.html")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(DOCS, exist_ok=True)

if not os.path.exists(SRC):
    raise SystemExit(f"no rendered page at {SRC}. Run refresh_app.py first.")

body = open(SRC, encoding="utf-8").read()
doc = (
    '<!doctype html>\n<html lang="en">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    '<meta name="description" content="A stock screen that scores companies on what '
    'they do to the accumulations they touch. Six measures, survivability as a gate, '
    'and $5,000 of pretend money to test it with.">\n'
    '<meta name="color-scheme" content="light dark">\n'
    '</head>\n<body>\n' + body + '\n</body>\n</html>\n'
)
out = os.path.join(DOCS, "index.html")
open(out, "w", encoding="utf-8").write(doc)

# Without this, Jekyll runs over the folder and can drop files, and it slows the
# build for no benefit on a page that is already a finished artifact.
open(os.path.join(DOCS, ".nojekyll"), "w").close()

print(f"wrote {out}  ({len(doc)/1024/1024:.2f} MB)")
print("wrote docs/.nojekyll")
