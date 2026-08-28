import os
from paths import DATA
import re, json, sys
src_path = sys.argv[1]
src = open(src_path, encoding="utf-8").read()
m = re.search(r"const STATE=(\{.*?\});\n", src)
state = json.loads(m.group(1))
json.dump(state, open(os.path.join(DATA, "paper_state.json"), "w", encoding="utf-8"))
print("cash:", round(state["cash"], 2))
print("positions:")
for tk, p in state["positions"].items():
    if p["shares"] > 0.0001:
        print(f"  {tk}: {p['shares']:.4f} sh, cost ${p['cost']:.2f}")
print("txns:", len(state["txns"]), "| history rows:", len(state["history"]))
for t in state["txns"][-12:]:
    print(" ", t)
