import os
from paths import DATA
import pandas as pd
DATA = DATA
hold = ["BFLY","ACB","SRTA","DFTX","IONQ","MFC","GEVO","EVTL","AQN","ABAT","AGI","NIO"]
r1 = pd.read_csv(os.path.join(DATA, "round1_final_scores.csv")); r1["ticker"]=r1.ticker.astype(str).str.upper()
r2 = pd.read_csv(os.path.join(DATA, "round2_results.csv")); r2["ticker"]=r2.ticker.astype(str).str.upper()
r4 = pd.read_csv(os.path.join(DATA, "round4_results.csv")); r4["ticker"]=r4.ticker.astype(str).str.upper()
r2rcol = "r2_reason" if "r2_reason" in r2.columns else "reason"
for t in hold:
    a = r1[r1.ticker==t]; b = r2[r2.ticker==t]; c = r4[r4.ticker==t]
    line = t + ": "
    if len(a):
        row = a.iloc[0]
        line += f"R1[need={row.need} score={row.r1_score} status={row.status} {str(row.reason)[:55]}] "
    else:
        line += "NOT IN UNIVERSE "
    if len(b):
        row = b.iloc[0]
        line += f"R2[{row.verdict}: {str(row[r2rcol])[:70]}] "
    if len(c):
        row = c.iloc[0]
        line += f"R4[{row.verdict} {row.total}: {str(row.reason)[:70]}]"
    print(line.encode("ascii","replace").decode())
