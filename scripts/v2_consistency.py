# -*- coding: utf-8 -*-
"""Inter-rater reliability check. Same business scored by different agents
should score alike. Where it doesn't, the rubric is ambiguous, not the company."""
import os
from paths import DATA
import pandas as pd, textwrap
D = DATA
v = pd.read_csv(os.path.join(D, "v2_assembled.csv"))
COMP = ["A", "B", "C1", "C2", "D_rep", "D_inhib", "D_exit", "E", "F_clock", "F_now"]

GROUPS = {
    "Class I rail + rail equipment": ["UNP", "CP", "CNI", "WAB"],
    "Molecular diagnostics (cancer/genomic)": ["NTRA", "GH", "VCYT", "CBLL"],
    "Implanted/wearable cardiac monitoring": ["IRTC", "DXCM", "RMD"],
    "Single-use medical consumable, infection control": ["TSNLF", "CRMD", "CERS"],
    "Industrial construction attachment / equipment": ["ENGCF", "SSMXY", "AHICF"],
}

for label, tks in GROUPS.items():
    sub = v[v.ticker.isin(tks)].set_index("ticker").reindex(tks).dropna(how="all")
    if len(sub) < 2:
        continue
    print(f"\n{label}")
    print("  " + "ticker".ljust(8) + "".join(c.rjust(8) for c in COMP) + "   total")
    for tk, r in sub.iterrows():
        print("  " + str(tk).ljust(8) + "".join(f"{r[c]:>8.0f}" for c in COMP) + f"   {r['v2_adj']:>5.0f}")
    spread = {c: sub[c].max() - sub[c].min() for c in COMP}
    worst = sorted(spread.items(), key=lambda x: -x[1])[:3]
    print(f"  widest disagreement: " + ", ".join(f"{c} spans {int(s)}" for c, s in worst))
    print(f"  total spread: {sub.v2_adj.max()-sub.v2_adj.min():.0f} points")

print("\n" + "=" * 78)
print("RAIL DETAIL: what each agent wrote")
for tk in ["UNP", "CP", "CNI", "WAB"]:
    r = v[v.ticker == tk]
    if not len(r):
        continue
    r = r.iloc[0]
    print(f"\n{tk}  total {r.v2_adj:.0f}   A={r.A:.0f} B={r.B:.0f} C1={r.C1:.0f} C2={r.C2:.0f} "
          f"Drep={r.D_rep:.0f} Dinh={r.D_inhib:.0f} Dexit={r.D_exit:.0f} E={r.E:.0f} "
          f"Fc={r.F_clock:.0f} Fn={r.F_now:.0f}")
    print("   stock: " + str(r.get("stock", ""))[:150])
    print("   evid : " + textwrap.shorten(str(r.get("evidence", "")), 230))
    print("   note : " + textwrap.shorten(str(r.get("note", "")), 230))
