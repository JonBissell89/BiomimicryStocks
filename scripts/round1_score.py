"""Round 1: universal preliminary scoring of all 15,797 companies.

Score components (coarse proxies of the 100-pt framework, same for everyone):
  need_score  0-30  industry/name alignment with the 7 durable needs
  viability   0-20  market cap / price / trading existence prior
Hard rejects recorded with explicit reasons. No sector pre-filtering:
finance/media/etc. are scored by the framework and fail on merit.
"""
import os
from paths import BUILD, DATA
import re
import pandas as pd

DATA = DATA
u = pd.read_csv(os.path.join(DATA, "universe_final.csv"))

# ---------------- industry -> (need_score, need_label, flag) ----------------
IND = {
# FOOD
"Packaged Foods": (26,"food",""), "Farming/Seeds/Milling": (27,"food",""),
"Food Distributors": (24,"food",""), "Food Chains": (22,"food",""),
"Specialty Foods": (24,"food",""), "Meat/Poultry/Fish": (18,"food","factory-farming-risk"),
"Agricultural Chemicals": (18,"food","toxicity-risk"),
"Beverages (Production/Distribution)": (14,"food","alcohol-mix"),
"Restaurants": (8,"food-service",""),
# WATER
"Water Supply": (28,"water","utility-slow-growth"),
"Water Sewer Pipeline Comm & Power Line Construction": (26,"water",""),
"Pollution Control Equipment": (27,"water",""),
"Environmental Services": (25,"water",""),
"Fluid Controls": (24,"water",""),
# SHELTER
"Homebuilding": (24,"shelter",""), "Building Products": (24,"shelter",""),
"Building Materials": (22,"shelter",""), "RETAIL: Building Materials": (18,"shelter",""),
"Engineering & Construction": (22,"shelter",""),
"General Bldg Contractors - Nonresidential Bldgs": (20,"shelter",""),
"Forest Products": (16,"shelter",""), "Home Furnishings": (10,"shelter",""),
"Building operators": (10,"shelter",""), "Real Estate": (8,"shelter","rent-extraction-risk"),
"Real Estate Investment Trusts": (8,"shelter","rent-extraction-risk"),
# ENERGY
"Electric Utilities: Central": (22,"energy","utility-slow-growth"),
"Power Generation": (25,"energy",""), "Natural Gas Distribution": (18,"energy","utility-slow-growth"),
"Electrical Products": (24,"energy",""),
"Oil & Gas Production": (8,"energy","commodity"), "Integrated oil Companies": (8,"energy","commodity"),
"Oilfield Services/Equipment": (10,"energy","commodity"), "Oil and Gas Field Machinery": (12,"energy","commodity"),
"Oil/Gas Transmission": (12,"energy",""), "Oil Refining/Marketing": (8,"energy","commodity"),
# HEALTH
"Biotechnology: Pharmaceutical Preparations": (20,"health","binary-science-risk"),
"Biotechnology: Biological Products (No Diagnostic Substances)": (20,"health","binary-science-risk"),
"Medical/Dental Instruments": (26,"health",""), "Medical Specialities": (25,"health",""),
"Biotechnology: In Vitro & In Vivo Diagnostic Substances": (26,"health",""),
"Biotechnology: Electromedical & Electrotherapeutic Apparatus": (25,"health",""),
"Biotechnology: Laboratory Analytical Instruments": (26,"health",""),
"Medical Electronics": (25,"health",""), "Ophthalmic Goods": (23,"health",""),
"Medical/Nursing Services": (20,"health",""), "Hospital/Nursing Management": (18,"health",""),
"Other Pharmaceuticals": (20,"health",""), " Medicinal Chemicals and Botanical Products ": (20,"health",""),
"Misc Health and Biotechnology Services": (18,"health",""),
"Biotechnology: Commercial Physical & Biological Resarch": (16,"health",""),
"Managed Health Care": (10,"health","cost-monetization-risk"),
"Retail-Drug Stores and Proprietary Stores": (12,"health",""),
"Pharmaceuticals and Biotechnology": (20,"health","binary-science-risk"),
# TRANSPORT
"Railroads": (27,"transport",""), "Marine Transportation": (16,"transport","commodity"),
"Trucking Freight/Courier Services": (18,"transport",""), "Air Freight/Delivery Services": (18,"transport",""),
"Auto Manufacturing": (20,"transport",""), "Auto Parts:O.E.M.": (20,"transport",""),
"Motor Vehicles": (20,"transport",""), "Transportation Services": (18,"transport",""),
"Integrated Freight & Logistics": (20,"transport",""),
"Construction/Ag Equipment/Trucks": (23,"transport",""),
"Automotive Aftermarket": (19,"transport",""), "Auto & Home Supply Stores": (12,"transport",""),
"Aerospace": (15,"transport","defense-mix"), "Other Transportation": (18,"transport",""),
"Retail-Auto Dealers and Gas Stations": (8,"transport",""),
"Rental/Leasing Companies": (10,"transport",""), "Misc Corporate Leasing Services": (8,"transport",""),
# ESSENTIAL INFRASTRUCTURE / ENABLERS
"Semiconductors": (22,"infrastructure",""), "Telecommunications Equipment": (20,"infrastructure",""),
"Industrial Machinery/Components": (21,"infrastructure",""),
"Electronic Components": (20,"infrastructure",""), "Precision Instruments": (20,"infrastructure",""),
"Metal Fabrications": (15,"infrastructure",""), "Industrial Specialties": (16,"infrastructure",""),
"Specialty Chemicals": (16,"infrastructure",""), "Major Chemicals": (12,"infrastructure","commodity"),
"Containers/Packaging": (14,"infrastructure",""), "Paper": (12,"infrastructure",""),
"Plastic Products": (10,"infrastructure",""), "Paints/Coatings": (12,"infrastructure",""),
"Computer Communications Equipment": (18,"infrastructure",""),
"Radio And Television Broadcasting And Communications Equipment": (15,"infrastructure",""),
"Computer Manufacturing": (16,"infrastructure",""), "Computer peripheral equipment": (14,"infrastructure",""),
"Tools/Hardware": (16,"infrastructure",""), "Professional and commerical equipment": (14,"infrastructure",""),
"Electronics Distribution": (14,"infrastructure",""), "Wholesale Distributors": (12,"infrastructure",""),
"Miscellaneous manufacturing industries": (12,"infrastructure",""),
"Steel/Iron Ore": (10,"materials","commodity"), "Aluminum": (10,"materials","commodity"),
"Metal Mining": (8,"materials","commodity"), "Other Metals and Minerals": (8,"materials","commodity"),
"Mining & Quarrying of Nonmetallic Minerals (No Fuels)": (10,"materials","commodity"),
"Coal Mining": (0,"REJECT","coal"),
"Precious Metals": (3,"materials","no-durable-need"),
# SOFTWARE / SERVICES (label uninformative -> enrich viable ones)
"Computer Software: Prepackaged Software": (12,"software","enrich"),
"EDP Services": (10,"software","enrich"),
"Computer Software: Programming Data Processing": (10,"software","enrich"),
"Retail: Computer Software & Peripheral Equipment": (8,"software",""),
"Business Services": (8,"services","enrich"), "Professional Services": (8,"services","enrich"),
"Diversified Commercial Services": (8,"services","enrich"),
"Other Consumer Services": (6,"services",""),
# LOW ALIGNMENT
"Major Banks": (5,"finance",""), "Commercial Banks": (5,"finance",""), "Banks": (5,"finance",""),
"Savings Institutions": (5,"finance",""), "Finance: Consumer Services": (4,"finance",""),
"Investment Managers": (2,"finance",""), "Finance/Investors Services": (3,"finance",""),
"Finance Companies": (4,"finance",""), "Investment Bankers/Brokers/Service": (3,"finance",""),
"Property-Casualty Insurers": (6,"finance",""), "Life Insurance": (5,"finance",""),
"Specialty Insurers": (6,"finance",""), "Accident &Health Insurance": (6,"finance",""),
"Diversified Financial Services": (3,"finance",""),
"Advertising": (2,"media",""), "Broadcasting": (2,"media",""), "Movies/Entertainment": (2,"media",""),
"Publishing": (3,"media",""), "Newspapers/Magazines": (3,"media",""), "Books": (3,"media",""),
"Cable & Other Pay Television Services": (6,"media",""),
"Telecommunications Equipment ": (20,"infrastructure",""),
"Hotels/Resorts": (4,"discretionary",""), "Services-Misc. Amusement & Recreation": (3,"discretionary","gambling-risk"),
"Recreational Games/Products/Toys": (3,"discretionary",""),
"Apparel": (7,"clothing",""), "Clothing/Shoe/Accessory Stores": (5,"clothing",""),
"Shoe Manufacturing": (7,"clothing",""), "Garments and Clothing": (7,"clothing",""), "Textiles": (8,"clothing",""),
"Package Goods/Cosmetics": (10,"health-adjacent",""),
"Consumer Electronics/Appliances": (8,"discretionary",""), "Consumer Electronics/Video Chains": (4,"discretionary",""),
"Department/Specialty Retail Stores": (4,"retail",""), "Other Specialty Stores": (4,"retail",""),
"Catalog/Specialty Distribution": (5,"retail",""), "Office Equipment/Supplies/Services": (5,"services",""),
"Consumer Specialties": (6,"discretionary",""), "Durable Goods": (10,"discretionary",""),
"Multi-Sector Companies": (10,"conglomerate","enrich"), "Miscellaneous": (6,"unknown",""),
# HARD REJECT INDUSTRIES
"Blank Checks": (0,"REJECT","spac"),
"Trusts Except Educational Religious and Charitable": (0,"REJECT","fund"),
"Military/Government/Technical": (0,"REJECT","weapons"),
"Ordnance And Accessories": (0,"REJECT","weapons"),
"Tobacco": (0,"REJECT","addiction"),
}

HARD_REASONS = {
    "spac": "blank-check SPAC - no operating business",
    "fund": "closed-end fund/royalty trust - not an operating company",
    "weapons": "economics depend on war/weapons (hard rejection rule)",
    "addiction": "economics depend on addiction (hard rejection rule)",
    "coal": "maintains broken system that should disappear (coal)",
}

# name-pattern hard rejects (applied to all listings)
NAME_REJECT = [
    (r"\bACQUISITION (CORP|CO|COMPANY|HOLDINGS)|\bSPAC\b|BLANK CHECK", "spac"),
    (r"\bCASINO|\bGAMING CORP|\bSLOT|\bLOTTERY|\bBETT?ING|SPORTSBOOK|DRAFTKINGS", "addiction"),
    (r"\bTOBACCO|\bCIGAR|\bVAPE|\bVAPOR BRANDS", "addiction"),
    (r"\bCANNABIS|\bCANNABI|\bMARIJUANA|\bHEMP CO|PSYCHEDELIC", "addiction"),
    (r"\bBITCOIN|\bBLOCKCHAIN|\bCRYPTO(CURRENCY)?\b|DIGITAL ASSET", "artificial scarcity (crypto)"),
    (r"\bDEFENSE (CORP|TECH|SYSTEMS)|\bMISSILE|\bMUNITION|\bARMAMENT|\bORDNANCE", "weapons"),
    (r"\bETF\b|\bINDEX FUND|\bMUTUAL FUND|\bCLOSED.END FUND", "fund"),
    (r"\bROYALTY TRUST|\bINCOME TRUST\b|\bMINERAL TRUST", "fund"),
]

# name keywords -> need score for companies with NO industry data
NAME_NEED = [
    (r"WATER|AQUA|HYDRAUL|IRRIGAT|DESALIN|WASTEWATER", 24, "water"),
    (r"\bFOOD|FARM|AGRI|AGRO|DAIRY|GRAIN|SEED|CROP|NUTRI|BAKER|MEAT\b|FISHER", 22, "food"),
    (r"\bSOLAR|RENEWABLE|GEOTHERM|HYDRO(?!GEN)|WIND ENERG|ENERG|POWER|ELECTRIC|GRID|BATTER|UTILIT", 20, "energy"),
    (r"PHARMA|THERAPEUT|BIOSCI|MEDIC|HEALTH|DIAGNOST|SURG|DENTAL|CLINIC|HOSPITAL|VACCIN|BIOTECH|LIFE SCIENCE", 20, "health"),
    (r"\bRAIL|TRANSIT|TRANSPORT|LOGISTIC|SHIPPING|MARITIME|AIRLINE|MOTOR|\bAUTO\b|VEHICLE|MOBILITY", 18, "transport"),
    (r"CONSTRUCT|BUILD|HOME|HOUS|CEMENT|CONCRETE|LUMBER|TIMBER|STEEL|INFRASTRUCT", 18, "shelter"),
    (r"RECYCL|CIRCULAR|WASTE|ENVIRONMENT|SUSTAINAB", 22, "infrastructure"),
    (r"SEMICONDUCT|TELECOM|NETWORK|COMMUNICAT|MATERIAL|CHEMICAL|INDUSTRI|MANUFACTUR|MACHIN|ENGINEER", 15, "infrastructure"),
    (r"\bBANK|BANC|FINANC|CAPITAL|INSUR|INVEST|ASSET|WEALTH|MORTGAGE|CREDIT|FUND\b|SECURITIES|REALTY|PROPERTIES|REIT\b", 4, "finance"),
    (r"MEDIA|ENTERTAIN|STUDIO|GAMES|RESORT|RESTAURANT|BRANDS|RETAIL|FASHION|LUXURY", 4, "discretionary"),
]

def viability(cap, price, listing):
    v = 0
    if pd.notna(cap):
        if cap >= 2e9: v = 20
        elif cap >= 5e8: v = 18
        elif cap >= 1e8: v = 15
        elif cap >= 5e7: v = 12
        elif cap >= 2.5e7: v = 9
        elif cap >= 1e7: v = 5
        else: v = 2
    elif listing == "sec_only":
        v = 3  # unknown, flagged for price check
    if pd.notna(price) and price < 0.10:
        v = max(0, v - 6)  # chronic-dilution price signal
    return v

rows = []
for r in u.itertuples(index=False):
    name = str(r.company).upper()
    ind = r.industry if isinstance(r.industry, str) else None
    need_score, need, flag, status, reason = 0, "unknown", "", "", ""

    # 1) name-pattern hard rejects
    for pat, why in NAME_REJECT:
        if re.search(pat, name):
            status, reason = "reject", HARD_REASONS.get(why, why)
            break

    # 2) industry mapping
    if not status:
        if ind and ind in IND:
            need_score, need, flag = IND[ind]
            if need == "REJECT":
                status, reason = "reject", HARD_REASONS[flag]
        elif ind:
            need_score, need, flag = 8, "unmapped", ""
        else:
            # no industry data: name keywords
            matched = False
            for pat, sc, lab in NAME_NEED:
                if re.search(pat, name):
                    need_score, need, matched = sc, lab, True
                    break
            if not matched:
                need_score, need, flag = 8, "unknown", "enrich-if-viable"

    via = viability(r.marketCap, r.price, r.listing)
    score = need_score + via

    if not status:
        # data-based rejections
        if r.listing == "sec_only" and pd.isna(r.price) and pd.isna(r.marketCap):
            status, reason = "check_price", "no market data yet - verify trading exists"
        elif pd.notna(r.marketCap) and r.marketCap < 1e7:
            status, reason = "reject", f"market cap ${r.marketCap/1e6:.1f}M < $10M - fails survivability prior (shell/nano-cap)"
        elif pd.notna(r.price) and r.price < 0.05 :
            status, reason = "reject", "sub-5-cent stock - chronic dilution profile"
        elif pd.isna(r.marketCap) and r.listing == "otc":
            status, reason = "reject", "OTC with no market cap data - dark/non-reporting"

    rows.append({
        "ticker": r.ticker, "company": r.company, "price": r.price, "marketCap": r.marketCap,
        "country": r.country, "sector": r.sector, "industry": ind, "listing": r.listing,
        "need": need, "need_score": need_score, "viability": via, "r1_score": score,
        "flag": flag, "status": status, "reason": reason,
    })

df = pd.DataFrame(rows)
df.to_csv(os.path.join(DATA, "round1_all_scores.csv"), index=False)

rejected = df[df.status == "reject"]
check = df[df.status == "check_price"]
alive = df[df.status == ""]
print(f"scored: {len(df)} | hard/data rejects: {len(rejected)} | need price check: {len(check)} | alive: {len(alive)}")
print("\nalive score distribution:")
print(alive["r1_score"].describe().round(1).to_string())
for cut in [30, 32, 34, 36, 38, 40]:
    print(f"  cut>={cut}: {len(alive[alive.r1_score >= cut])} survivors")
