"""Unify the engine: fold all light-track (former Watch bench) names into the
tiers as first-class graded entries with owner-rule tags and a verification-depth
flag. Price becomes a pure view filter; membership never changes with price."""
import os
from paths import DATA
import json
import pandas as pd

DATA = DATA
eng = json.load(open(os.path.join(DATA, "engine_tiers.json"), encoding="utf-8"))
tiered = {n["tk"] for t in eng["tiers"] for n in t["names"]}

NAMES = {
 "NTRA": "Natera", "TSM": "TSMC", "WAB": "Wabtec", "UNP": "Union Pacific",
 "LGRDY": "Legrand", "AHICF": "Asahi Intecc", "WST": "West Pharm", "GH": "Guardant",
 "BSY": "Bentley", "TOELY": "Tokyo Electron", "BOEUF": "Bonesupport", "CP": "CPKC",
 "GKOS": "Glaukos", "IOT": "Samsara", "HTFL": "Heartflow", "VCYT": "Veracyte",
 "PLPC": "Preformed Line", "CAI": "Caris", "CNI": "CN Rail", "DXCM": "DexCom",
 "BLLN": "BillionToOne", "TMDX": "TransMedics", "CBLL": "CeriBell", "IRTC": "iRhythm",
 "RMD": "ResMed", "MBRFF": "Mo-BRUK", "DAR": "Darling", "MHGVY": "Mowi",
 "ATRC": "AtriCure", "LEGH": "Legacy Housing",
}
JX = {"TSM": ("taiwan-linked", -2)}
VALUES = {  # provisional per owner definitions; auditable on challenge
 "pushback": ["BOEUF", "VCYT", "HTFL", "GH", "AHICF", "IRTC", "TMDX", "CAI"],
 "embedded": ["NTRA", "WST", "GKOS", "DXCM", "BLLN", "CBLL", "RMD", "ATRC"],
}
VMAP = {tk: tag for tag, tks in VALUES.items() for tk in tks}
SOFI_LISTED = {"NTRA","WAB","UNP","WST","GH","BSY","IOT","CP","HTFL","GKOS","VCYT",
               "PLPC","CAI","CNI","DXCM","BLLN","TMDX","CBLL","IRTC","RMD","DAR",
               "ATRC","LEGH","TSM"}  # NYSE/NASDAQ listings (TSM = NYSE-listed ADR)
SOFI_PENDING = {"TOELY","LGRDY","MHGVY"}  # Y-ADRs, pending owner in-app check
SPECIAL_NOTES = {
 "MHGVY": "regeneration-standard review pending (aquaculture producer)",
 "DAR": "regenerative food benchmark",
 "TSM": "jx -2 taiwan-linked",
 "CBLL": "score adjusted 80->79 in light verification",
}

wb = pd.read_csv(os.path.join(DATA, "final_watch.csv"))
wb["ticker"] = wb.ticker.astype(str).str.upper()
wb = wb[~wb.ticker.isin(tiered | {"INPOY"})].drop_duplicates("ticker")
wb["score"] = pd.to_numeric(wb["total"].astype(str).str.extract(r"([0-9]+)")[0], errors="coerce")

added = []
for r in wb.itertuples():
    tk = r.ticker
    if tk not in NAMES or pd.isna(r.score):
        continue
    score = int(r.score)
    entry = {"tk": tk, "nm": NAMES[tk], "score": score,
             "depth": "light",
             "note": "light-verified — deep pass pending" + (" · " + SPECIAL_NOTES[tk] if tk in SPECIAL_NOTES else ""),
             "sofi": tk in SOFI_LISTED}
    if tk in SOFI_PENDING:
        entry["sofi_note"] = "Y-ADR, likely — pending owner in-app check"
    elif tk in SOFI_LISTED:
        entry["sofi_note"] = "NYSE/NASDAQ listing (availability by listing fact)"
    if tk in JX:
        tag, pen = JX[tk]
        entry["score_base"] = score
        entry["jx"] = tag
        entry["jx_penalty"] = pen
        entry["score"] = score + pen
    if tk in VMAP:
        entry["values"] = VMAP[tk]
        entry["values_note"] = "provisional (light verification) — auditable on challenge"
    added.append(entry)

t1, t2, t3 = eng["tiers"][0], eng["tiers"][1], eng["tiers"][2]
for e in added:
    (t1 if e["score"] >= 80 else t2 if e["score"] >= 74 else t3)["names"].append(e)
for t in (t1, t2, t3):
    t["names"].sort(key=lambda n: -n["score"])

eng["watch_alerts"] = []
eng["_unified"] = ("Unified graded table (owner ruling, Aug 27 2026): all 54 tournament finalists "
  "(minus removals/buyouts) are tiered by score band (T1>=80, T2 74-79, T3 69-73) regardless of price. "
  "Price is a VIEW filter only; the gate value is the default price view. Each name carries depth: "
  "'deep' (final-round full verification + owner rules applied) or 'light' (score-confirmed only; "
  "dilution/runway not deep-audited; values tags provisional). Deep passes upgrade names on request.")
json.dump(eng, open(os.path.join(DATA, "engine_tiers.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
for t in eng["tiers"]:
    print(t["id"], len(t["names"]), [(n["tk"], n["score"]) for n in t["names"]])
