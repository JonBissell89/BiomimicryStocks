"""Write my re-judgments for the 229 empty-description repair candidates."""
import os
from paths import DATA
import pandas as pd

DATA = DATA

A = {
 "AEHR": "wafer-level burn-in test for EV/power semis, proprietary systems",
 "A": "lab analytical/diagnostics instruments - health research infrastructure",
 "ABT": "diagnostics devices nutrition - global health systems at scale",
 "ADPT": "commercial immunosequencing diagnostics platform, proprietary",
 "ADUS": "home care displaces institutionalization - cost per outcome down",
 "ADMA": "commercial plasma biologics for immune deficiency, US supply",
 "KMDA": "commercial plasma-derived therapeutics, proven products growing",
 "AAON": "high-efficiency HVAC and data-center cooling, energy compression",
 "AEIS": "precision power conversion improves industrial energy efficiency",
}
B = {
 "AES": "global renewables+utilities, real assets but heavy debt model",
 "AGRO": "ag production real ops, commodity exposure",
 "TXG": "single-cell analysis platform, contracting revenue",
 "MMM": "diversified industrial, durable-need products but slow growth",
 "ACHC": "behavioral health facilities, flat growth",
 "ACAD": "commercial niche CNS/rare pharma",
 "FDMDF": "novel lung imaging, weak commercialization",
 "AHCO": "home medical equipment roll-up, thin moat",
 "AUNA": "LatAm hospitals/clinics, real growth",
 "EBS": "public-health preparedness products, volatile government demand",
 "FENC": "commercial PEDMARK prevents chemo hearing loss, single product",
 "MIST": "approved PSVT nasal spray converts ER visits to self-care",
 "PLX": "plant-cell recombinant proteins, commercial, cheaper production",
 "LENZ": "approved presbyopia drops, early commercial",
 "HUMA": "bioengineered vessels approved, heavy burn",
 "DERM": "commercial dermatology portfolio growing",
 "LFCR": "integrated CDMO for sterile injectables - health manufacturing",
 "XFOR": "rare-disease drug newly commercial, hypergrowth off small base",
 "AMD": "compute infrastructure enabler, not physical-need system core",
 "ACMR": "semi cleaning equipment, real growth, China concentration",
 "AGCO": "ag equipment durable food need, flat cycle",
 "ADTN": "fiber access networking, modest growth",
 "CLFD": "fiber management hardware for broadband buildout",
 "MASS": "handheld mass-spec for safety/health, defense mix",
 "AYI": "lighting controls/building management efficiency, slow growth",
 "AEBI": "municipal/ag specialty vehicles, merger-driven growth",
 "CAAS": "steering systems incl EPS for Chinese OEMs, growing",
 "RELL": "power-grid tubes/components niche, growing",
 "AEVA": "FMCW lidar safety sensing, pre-profit",
 "INVZ": "automotive lidar design wins, heavy burn",
 "NIU": "electric urban scooters, real volumes",
 "THNOF": "gov/education ERP SaaS, sticky but generic category",
 "AIOT": "fleet AIoT telematics improves transport efficiency",
 "SRI": "commercial-vehicle electronics: e-mirrors, driver monitoring",
}
CLINICAL = ("clinical/preclinical-stage or single-asset binary science - "
            "unproven breakthrough rule")
C_SPECIAL = {
 "ABZPF": "captive-territory regulated utility",
 "AAVVF": "commodity oil and gas E&P", "UNEGF": "commodity upstream oil",
 "ABBV": "premium branded pharma, no cost-compression mechanism",
 "SI": "no data on any venue", "TBB": "bond/preferred listing", "UZE": "bond/preferred listing",
 "UZD": "bond/preferred listing", "HOVNP": "preferred listing", "AHWSF": "no data on any venue",
 "ZHHJY": "no business information available",
 "CGC": "cannabis - addiction rule", "OGI": "cannabis - addiction rule", "SNDL": "cannabis/liquor - addiction rule",
 "CYPH": "crypto treasury - artificial scarcity", "NAKA": "bitcoin treasury - artificial scarcity",
 "DCX": "crypto derivatives platform", "CNTN": "blockchain treasury plus clinical bio mix",
 "ZSTK": "pharma distribution plus digital-assets mix",
 "NATR": "supplement MLM distribution", "NUS": "beauty MLM", "USNA": "supplement MLM",
 "SBC": "cosmetic clinic management - not durable need",
 "AIRS": "cosmetic body contouring - not durable need",
 "SIGA": "single biodefense product, contracting, stockpile dependent",
 "EBSI": "unused", "DNA": "platform contracting sharply", "ORGO": "wound care contracting sharply",
 "MDWD": "commercial but revenue contracting sharply", "IVVD": "single-virus antibody, uncertain durability",
 "VNDA": "stagnant branded CNS portfolio", "PBYI": "branded oncology stagnant, no efficiency mechanism",
 "AMRN": "single product, revenue collapsing", "AKBA": "approved but contracting revenue",
 "ADCT": "approved product but stagnant micro-scale", "ABEO": "single gene therapy, micro-scale",
 "CPIX": "small specialty pharma contracting", "ARCT": "revenue collapsing post-COVID",
 "LFMD": "lifestyle telehealth, declining", "SPOK": "legacy healthcare paging, stagnant",
 "CXDO": "generic UCaaS", "KVHI": "niche connectivity, no durable moat",
 "GOGO": "in-flight connectivity, flat", "ATNI": "small-market telecom incumbent",
 "AUDC": "unified-comms hardware/software, flat", "OCC": "commodity cabling",
 "AMPG": "niche amplifiers, contracting", "ALMU": "pre-scale semis, contracting",
 "ELSLF": "drone connectivity, defense-centric", "SIDU": "smallsat defense-mix, contracting",
 "OPTX": "optics with heavy defense mix", "TTGT": "tech adtech/intent data",
 "TBCH": "gaming accessories - discretionary", "ACU": "scissors/first-aid commodity products",
 "AZ": "smart shopping carts - retail gadget", "RFL": "holding company mix",
 "RLGT": "commodity freight forwarding", "MPAA": "aftermarket parts, contracting",
 "HLLY": "enthusiast performance parts - discretionary", "ADNT": "commodity seating, thin margins",
 "CPS": "commodity sealing, leveraged", "CVGI": "commodity vehicle components",
 "STRT": "legacy lock/key components", "LVWR": "electric motorcycles, deep losses niche",
 "AIIO": "story-stage EV venture", "QUCY": "quantum/cyber acquisition vehicle",
 "CKLSF": "diversified holding, low growth", "LCTX": "clinical-stage cell therapy",
 "ACHV": "single-asset NDA-stage smoking cessation",
}

rep = pd.read_csv(os.path.join(DATA, "r2_repair_profiles.csv"))
rows = []
for t in rep.ticker:
    if t in A: rows.append((t, "A", A[t]))
    elif t in B: rows.append((t, "B", B[t]))
    elif t in C_SPECIAL: rows.append((t, "C", C_SPECIAL[t]))
    else: rows.append((t, "C", CLINICAL))
out = pd.DataFrame(rows, columns=["ticker", "verdict", "reason"])
out.to_csv(os.path.join(DATA, "r2_verdicts_repair.csv"), index=False)
print(f"repair verdicts written: {len(out)} | A={sum(out.verdict=='A')} B={sum(out.verdict=='B')} C={sum(out.verdict=='C')}")
