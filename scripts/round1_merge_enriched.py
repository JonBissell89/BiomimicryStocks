"""Merge enriched Yahoo profiles back into Round 1, re-score previously
unclassified names using Yahoo sector/industry + description keywords,
and produce the final Round 1 survivor list."""
import os
from paths import DATA
import json, re
import pandas as pd

DATA = DATA

# Yahoo industry -> (need_score, need, flag). Applied to names that lacked
# NASDAQ industry data (OTC/sec_only) or carried an 'enrich' flag.
YIND = {
# water
"Utilities - Regulated Water": (28, "water", "utility-slow-growth"),
"Pollution & Treatment Controls": (27, "water", ""),
"Waste Management": (25, "water", ""),
# food
"Farm Products": (26, "food", ""), "Packaged Foods": (26, "food", ""),
"Food Distribution": (24, "food", ""), "Grocery Stores": (20, "food", ""),
"Agricultural Inputs": (20, "food", "toxicity-risk"),
"Farm & Heavy Construction Machinery": (23, "food", ""),
"Beverages - Non-Alcoholic": (16, "food", ""),
"Beverages - Wineries & Distilleries": (0, "REJECT", "addiction"),
"Beverages - Brewers": (0, "REJECT", "addiction"),
"Confectioners": (12, "food", ""),
"Restaurants": (8, "food-service", ""),
# shelter
"Residential Construction": (24, "shelter", ""), "Building Products & Equipment": (24, "shelter", ""),
"Building Materials": (22, "shelter", ""), "Engineering & Construction": (22, "shelter", ""),
"Lumber & Wood Production": (18, "shelter", ""), "Furnishings, Fixtures & Appliances": (10, "shelter", ""),
"Real Estate Services": (8, "shelter", ""), "Real Estate - Development": (10, "shelter", ""),
"Real Estate - Diversified": (8, "shelter", ""),
# energy
"Utilities - Regulated Electric": (22, "energy", "utility-slow-growth"),
"Utilities - Renewable": (24, "energy", ""),
"Utilities - Independent Power Producers": (22, "energy", ""),
"Utilities - Diversified": (20, "energy", "utility-slow-growth"),
"Utilities - Regulated Gas": (18, "energy", "utility-slow-growth"),
"Solar": (22, "energy", ""), "Electrical Equipment & Parts": (24, "energy", ""),
"Oil & Gas E&P": (8, "energy", "commodity"), "Oil & Gas Integrated": (8, "energy", "commodity"),
"Oil & Gas Midstream": (12, "energy", ""), "Oil & Gas Equipment & Services": (10, "energy", "commodity"),
"Oil & Gas Refining & Marketing": (8, "energy", "commodity"), "Oil & Gas Drilling": (8, "energy", "commodity"),
"Thermal Coal": (0, "REJECT", "coal"), "Coking Coal": (5, "materials", "commodity"),
"Uranium": (16, "energy", ""),
# health
"Drug Manufacturers - Specialty & Generic": (22, "health", ""),
"Drug Manufacturers - General": (20, "health", ""),
"Biotechnology": (20, "health", "binary-science-risk"),
"Medical Devices": (26, "health", ""), "Medical Instruments & Supplies": (26, "health", ""),
"Diagnostics & Research": (26, "health", ""), "Medical Care Facilities": (18, "health", ""),
"Medical Distribution": (22, "health", ""), "Health Information Services": (22, "health", ""),
"Healthcare Plans": (10, "health", "cost-monetization-risk"),
"Pharmaceutical Retailers": (12, "health", ""),
# transport
"Railroads": (27, "transport", ""), "Marine Shipping": (16, "transport", "commodity"),
"Trucking": (18, "transport", ""), "Integrated Freight & Logistics": (20, "transport", ""),
"Airlines": (14, "transport", ""), "Airports & Air Services": (18, "transport", ""),
"Auto Manufacturers": (20, "transport", ""), "Auto Parts": (20, "transport", ""),
"Recreational Vehicles": (8, "transport", ""), "Auto & Truck Dealerships": (8, "transport", ""),
"Aerospace & Defense": (8, "transport", "defense-mix"),
# infrastructure/enablers
"Semiconductors": (22, "infrastructure", ""), "Semiconductor Equipment & Materials": (22, "infrastructure", ""),
"Communication Equipment": (20, "infrastructure", ""), "Electronic Components": (20, "infrastructure", ""),
"Specialty Industrial Machinery": (22, "infrastructure", ""), "Industrial Distribution": (16, "infrastructure", ""),
"Scientific & Technical Instruments": (22, "infrastructure", ""),
"Specialty Chemicals": (16, "infrastructure", ""), "Chemicals": (12, "infrastructure", "commodity"),
"Packaging & Containers": (14, "infrastructure", ""), "Paper & Paper Products": (12, "infrastructure", ""),
"Metal Fabrication": (15, "infrastructure", ""), "Infrastructure Operations": (20, "infrastructure", ""),
"Telecom Services": (14, "infrastructure", "utility-slow-growth"),
"Utilities - Water": (28, "water", "utility-slow-growth"),
"Conglomerates": (12, "conglomerate", ""),
"Steel": (10, "materials", "commodity"), "Aluminum": (10, "materials", "commodity"),
"Copper": (12, "materials", "commodity"), "Other Industrial Metals & Mining": (8, "materials", "commodity"),
"Gold": (3, "materials", "no-durable-need"), "Silver": (3, "materials", "no-durable-need"),
"Other Precious Metals & Mining": (3, "materials", "no-durable-need"),
"Building Products": (24, "shelter", ""),
# software/services - description decides, default modest
"Software - Application": (12, "software", "desc"), "Software - Infrastructure": (12, "software", "desc"),
"Information Technology Services": (10, "software", "desc"),
"Computer Hardware": (14, "infrastructure", ""), "Consumer Electronics": (8, "discretionary", ""),
"Electronic Gaming & Multimedia": (2, "discretionary", ""),
"Internet Content & Information": (4, "media", ""), "Internet Retail": (5, "retail", ""),
"Specialty Business Services": (8, "services", "desc"), "Consulting Services": (6, "services", ""),
"Rental & Leasing Services": (8, "services", ""), "Security & Protection Services": (10, "services", ""),
"Staffing & Employment Services": (5, "services", ""), "Education & Training Services": (10, "services", ""),
"Personal Services": (5, "services", ""), "Advertising Agencies": (2, "media", ""),
# low
"Banks - Regional": (5, "finance", ""), "Banks - Diversified": (5, "finance", ""),
"Insurance - Life": (5, "finance", ""), "Insurance - Property & Casualty": (6, "finance", ""),
"Insurance - Diversified": (5, "finance", ""), "Insurance - Specialty": (6, "finance", ""),
"Insurance - Reinsurance": (5, "finance", ""), "Insurance Brokers": (5, "finance", ""),
"Asset Management": (2, "finance", ""), "Capital Markets": (3, "finance", ""),
"Credit Services": (4, "finance", ""), "Mortgage Finance": (4, "finance", ""),
"Financial Data & Stock Exchanges": (6, "finance", ""), "Shell Companies": (0, "REJECT", "spac"),
"Financial Conglomerates": (4, "finance", ""),
"Tobacco": (0, "REJECT", "addiction"), "Gambling": (0, "REJECT", "addiction"),
"Resorts & Casinos": (0, "REJECT", "addiction"), "Cannabis": (0, "REJECT", "addiction"),
"Leisure": (4, "discretionary", ""), "Lodging": (4, "discretionary", ""), "Travel Services": (4, "discretionary", ""),
"Apparel Manufacturing": (7, "clothing", ""), "Apparel Retail": (5, "clothing", ""),
"Footwear & Accessories": (7, "clothing", ""), "Textile Manufacturing": (8, "clothing", ""),
"Luxury Goods": (2, "discretionary", ""), "Household & Personal Products": (12, "health-adjacent", ""),
"Tools & Accessories": (16, "infrastructure", ""),
"Publishing": (3, "media", ""), "Broadcasting": (2, "media", ""), "Entertainment": (2, "media", ""),
"Department Stores": (3, "retail", ""), "Specialty Retail": (4, "retail", ""),
"Discount Stores": (8, "retail", ""), "Home Improvement Retail": (14, "shelter", ""),
}

HARD_REASONS = {
    "spac": "shell company/SPAC - no operating business",
    "addiction": "economics depend on addiction (hard rejection rule)",
    "coal": "maintains broken system that should disappear (coal)",
}

# description keyword boosts for software/services with 'desc' flag:
DESC_BOOST = [
    (r"water|wastewater|irrigat|desalin", 10, "water"),
    (r"grid|smart meter|energy management|energy efficien|renewable|solar|battery|ev charg", 10, "energy"),
    (r"health|clinical|patient|hospital|medical|diagnos|pharma", 8, "health"),
    (r"agricultur|farm|food safety|crop", 9, "food"),
    (r"logistics|freight|fleet|transport|rail|transit|supply chain", 8, "transport"),
    (r"construction|building information|infrastructure (software|management)|geospatial|survey", 8, "shelter"),
    (r"manufactur|industrial automation|asset management software|predictive maintenance|iot", 6, "infrastructure"),
    (r"cybersecurity|network security", 4, "infrastructure"),
]

def viability(cap, price):
    v = 0
    if pd.notna(cap):
        if cap >= 2e9: v = 20
        elif cap >= 5e8: v = 18
        elif cap >= 1e8: v = 15
        elif cap >= 5e7: v = 12
        elif cap >= 2.5e7: v = 9
        elif cap >= 1e7: v = 5
        else: v = 2
    if pd.notna(price) and price < 0.10:
        v = max(0, v - 6)
    return v

# ---- load ----
r1 = pd.read_csv(os.path.join(DATA, "round1_all_scores.csv"))
profs = {}
with open(os.path.join(DATA, "profiles.jsonl"), encoding="utf-8") as f:
    for line in f:
        try:
            j = json.loads(line)
            profs[j["ticker"]] = j
        except Exception:
            pass
print(f"profiles loaded: {len(profs)}")

sec_prices = pd.read_csv(os.path.join(DATA, "sec_only_traders.csv")).set_index("ticker")["price"].to_dict()

out = []
for r in r1.itertuples(index=False):
    t = r.ticker
    rec = dict(
        ticker=t, company=r.company, price=r.price, marketCap=r.marketCap,
        country=r.country, sector=r.sector, industry=r.industry, listing=r.listing,
        need=r.need, need_score=r.need_score, viability=r.viability, r1_score=r.r1_score,
        flag=r.flag, status=r.status if isinstance(r.status, str) else "",
        reason=r.reason if isinstance(r.reason, str) else "",
    )
    p = profs.get(t)
    # sec_only that trade: fill price
    if r.listing == "sec_only" and t in sec_prices and rec["status"] == "check_price":
        rec["price"] = sec_prices[t]
        rec["status"], rec["reason"] = "", ""
    elif rec["status"] == "check_price":
        rec["status"], rec["reason"] = "reject", "no active trading market (no price data on any venue)"

    if p and p.get("ok"):
        # fill fresher data
        if p.get("marketCap") is not None:
            rec["marketCap"] = p["marketCap"]
        if p.get("currentPrice") is not None:
            rec["price"] = p["currentPrice"]
        if p.get("sector") and not isinstance(r.sector, str):
            rec["sector"] = p["sector"]
        yind = p.get("industry")
        desc = (p.get("longBusinessSummary") or "").lower()
        rec["y_industry"] = yind
        # re-score if previously unclassified/desc-flagged
        needs_rescore = (r.need in ("unknown", "unmapped")) or ("enrich" in str(r.flag)) or ("desc" in str(r.flag))
        if needs_rescore and yind:
            if yind in YIND:
                ns, nd, fl = YIND[yind]
                if nd == "REJECT":
                    rec["status"], rec["reason"] = "reject", HARD_REASONS[fl]
                    rec["need"], rec["need_score"] = "REJECT", 0
                else:
                    if fl == "desc" or nd in ("software", "services"):
                        best = 0; bestlab = nd
                        for pat, boost, lab in DESC_BOOST:
                            if re.search(pat, desc) and boost > best:
                                best, bestlab = boost, lab
                        ns = ns + best
                        nd = f"software:{bestlab}" if best else nd
                    rec["need"], rec["need_score"], rec["flag"] = nd, ns, fl
            else:
                rec["need"] = "y-unmapped"
                rec["need_score"] = max(rec["need_score"], 8)

    rec["viability"] = viability(pd.to_numeric(rec["marketCap"], errors="coerce"),
                                 pd.to_numeric(rec["price"], errors="coerce"))
    rec["r1_score"] = rec["need_score"] + rec["viability"]

    # final data rejects after enrichment
    if rec["status"] == "":
        cap = pd.to_numeric(rec["marketCap"], errors="coerce")
        px = pd.to_numeric(rec["price"], errors="coerce")
        if pd.notna(cap) and cap < 1e7:
            rec["status"], rec["reason"] = "reject", "market cap < $10M - fails survivability prior"
        elif pd.notna(px) and px < 0.05:
            rec["status"], rec["reason"] = "reject", "sub-5-cent stock - chronic dilution profile"
        elif pd.isna(cap) and r.listing != "exchange":
            rec["status"], rec["reason"] = "reject", "no market cap data - non-reporting/dark"
    out.append(rec)

df = pd.DataFrame(out)
df.to_csv(os.path.join(DATA, "round1_final_scores.csv"), index=False)
alive = df[df.status == ""]
print(f"total: {len(df)} | rejected: {(df.status=='reject').sum()} | alive: {len(alive)}")
for cut in [34, 36, 38, 40, 42]:
    print(f"  cut>={cut}: {(alive.r1_score>=cut).sum()} survivors")
print("\nalive by need at cut>=38:")
print(alive[alive.r1_score >= 38]["need"].value_counts().head(30).to_string())
