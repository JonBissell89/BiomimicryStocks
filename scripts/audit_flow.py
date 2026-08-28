import os
from paths import BUILD
import re

p = os.path.join(BUILD, "bs_console.html")
s = open(p, encoding="utf-8").read()
body = s[s.find("<nav>"):s.find("<footer")]

def strip(t):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t or "")).strip()

nav = re.findall(r'<a href="#([^"]+)">(.*?)</a>', body)
print("NAV:", " | ".join(f"{txt}(#{i})" for i, txt in nav))
print()

for m in re.finditer(r'<section[^>]*id="([^"]+)"[^>]*>(.*?)</section>', body, re.S):
    sid, inner = m.group(1), m.group(2)
    step = re.search(r'class="step">(.*?)</p>', inner, re.S)
    h = re.search(r"<h1[^>]*>(.*?)</h1>", inner, re.S) or re.search(r"<h2[^>]*>(.*?)</h2>", inner, re.S)
    paras = [strip(x) for x in re.findall(r"<p[^>]*>(.*?)</p>", inner, re.S)]
    paras = [x for x in paras if len(x) > 40][:3]
    btns = [strip(b) for b in re.findall(r"<button[^>]*>(.*?)</button>", inner)]
    print("=" * 74)
    print(f"#{sid}   [{strip(step.group(1)) if step else '(no step label)'}]")
    print("HEAD:", strip(h.group(1)) if h else "(none)")
    for x in paras:
        print("   -", x[:200])
    if btns:
        print("   BUTTONS:", ", ".join(btns[:6]))
