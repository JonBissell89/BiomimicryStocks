# -*- coding: utf-8 -*-
"""Can this page live anywhere, or does it secretly need a host?
Anything it fetches at runtime is a dependency on somebody else's server."""
import os
from paths import BUILD
import re
P = os.path.join(BUILD, "bs_console.html")
h = open(P, encoding="utf-8").read()

print(f"page size: {len(h)/1024/1024:.2f} MB\n")

print("EXTERNAL URLs REFERENCED")
urls = sorted(set(re.findall(r'https?://[^\s"\'<>)]+', h)))
for u in urls:
    print(f"  {u[:100]}")

print("\nRUNTIME NETWORK CALLS (would break offline or on another host)")
for pat, label in [(r"\bfetch\s*\(", "fetch()"), (r"XMLHttpRequest", "XMLHttpRequest"),
                   (r"new\s+WebSocket", "WebSocket"), (r"navigator\.sendBeacon", "sendBeacon"),
                   (r"import\s*\(", "dynamic import"), (r"<script[^>]+src=", "external script"),
                   (r'<link[^>]+href="https?://', "external stylesheet"),
                   (r'<img[^>]+src="https?://', "remote image")]:
    n = len(re.findall(pat, h))
    print(f"  {label:<20s} {n}" + ("   <-- external dependency" if n and "stylesheet" not in label else ""))

print("\nWHAT IT NEEDS FROM A HOST")
print("  server-side code:      none, it is one HTML file")
print("  database:              none, state is localStorage per visitor")
print("  build step at serve:   none, it is pre-rendered")
print(f"  claude.ai runtime:     optional, guarded by "
      f"{'yes' if 'window.claude&&claude.use' in h.replace(' ','') else 'NO GUARD'}")
print("\nSTATE STORAGE")
for k in sorted(set(re.findall(r"localStorage\.\w+\('(\w+)'", h))):
    print(f"  localStorage.{k}")
