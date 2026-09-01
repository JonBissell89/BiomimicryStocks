# -*- coding: utf-8 -*-
"""Quarterly universe refresh: the market changes, so the judged set must too.

The 15,797-name universe was judged once and frozen. This script keeps the
LIVE universe honest on a quarterly clock: it pulls the current exchange
symbol directories and the SEC filer list, diffs them against the judged set,
and queues what it finds. It never judges anything itself.

- A ticker in the fresh listings but not in the universe enters the queue as
  needs_first_screen: a research run (the same agent pipeline that scored the
  original tournament) owes it a first-screen judgment.
- A ticker the universe holds as exchange-listed that has left the exchange
  directories is flagged delisted_check: a human or the monthly judgment run
  confirms before anything is removed. OTC and SEC-only names get no liveness
  test here; absence from a scraped OTC list proves nothing.
- Securities the original screen excluded by construction (warrants, rights,
  units, preferreds, notes, ETFs, test issues) are excluded again by the same
  rules, so the queue holds companies, not paperwork.

Cadence: 92 days, self-guarded like the other trackers. A registered logic
change (data/rigor/logic_version.json obligations) forces a run regardless,
because a new way of judging owes every name a fresh look.
"""
import csv, datetime, io, json, os, sys, urllib.request
from paths import DATA

Q = os.path.join(DATA, "refresh_queue.json")
CADENCE = 92
UA = {"User-Agent": "BiomimicryStocks universe refresh (research; contact via repo)"}

BAD_NAME = ("warrant", "right", " unit", "units ", "preferred", "preference",
            "% note", "notes due", "depositary", "trust preferred", "when issued")


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def company_like(name):
    n = (name or "").lower()
    return not any(b in n for b in BAD_NAME)


def parse_symdir(text, sym_col, name_col, etf_col, test_col):
    """nasdaqtrader symbol directories: pipe-delimited with a footer line."""
    out = {}
    rows = [r for r in csv.reader(io.StringIO(text), delimiter="|")]
    head = rows[0]
    ix = {c: head.index(c) for c in (sym_col, name_col, etf_col, test_col)}
    for r in rows[1:]:
        if len(r) != len(head) or r[0].startswith("File Creation"):
            continue
        if r[ix[etf_col]] == "Y" or r[ix[test_col]] == "Y":
            continue
        tk, nm = r[ix[sym_col]].strip().upper(), r[ix[name_col]].strip()
        if tk and company_like(nm):
            out[tk] = nm
    return out


def current_listings():
    """Exchange-listed companies and SEC filers, or None when unreachable."""
    try:
        nas = parse_symdir(fetch("https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"),
                           "Symbol", "Security Name", "ETF", "Test Issue")
        oth = parse_symdir(fetch("https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"),
                           "ACT Symbol", "Security Name", "ETF", "Test Issue")
        sec_raw = json.loads(fetch("https://www.sec.gov/files/company_tickers.json"))
        sec = {v["ticker"].strip().upper(): v["title"].strip()
               for v in sec_raw.values() if v.get("ticker")}
        return {"exchange": {**oth, **nas}, "sec": sec}
    except Exception as e:
        print("listing sources unreachable (%s); refresh skipped, queue untouched" % type(e).__name__)
        return None


def load_queue():
    if os.path.exists(Q):
        return json.load(open(Q, encoding="utf-8"))
    return {"cadence_days": CADENCE,
            "note": ("what the market changed and the engine has not yet judged. "
                     "pending_first_screen names owe a first-screen judgment by the "
                     "research pipeline; delisted_check names await confirmation "
                     "before removal; obligations are stamped by register_logic.py "
                     "when the judging logic itself changes."),
            "last_refresh": None, "obligations": {},
            "pending_first_screen": [], "delisted_check": [], "log": []}


def main():
    force = "--force" in sys.argv
    queue = load_queue()
    today = datetime.date.today().isoformat()
    obliged = bool(queue.get("obligations"))
    if queue["last_refresh"] and not force and not obliged:
        age = (datetime.date.fromisoformat(today)
               - datetime.date.fromisoformat(queue["last_refresh"])).days
        if age < CADENCE:
            print("universe refresh: last ran %s (%d days ago); %d-day cadence holds"
                  % (queue["last_refresh"], age, CADENCE)); return

    listings = current_listings()
    if listings is None:
        return

    si = json.load(open(os.path.join(DATA, "search_index.json"), encoding="utf-8"))
    universe = set(si.keys())
    excluded = set()
    for fn in ("excluded_derivative_securities.csv", "excluded_duplicate_listings.csv"):
        p = os.path.join(DATA, fn)
        if os.path.exists(p):
            with open(p, encoding="utf-8", errors="replace") as f:
                excluded |= {r[0].strip().upper() for r in csv.reader(f) if r and r[0].strip()}

    fresh = {**listings["sec"], **listings["exchange"]}
    queued = {e["tk"] for e in queue["pending_first_screen"]}
    added = 0
    for tk, nm in sorted(fresh.items()):
        if tk in universe or tk in excluded or tk in queued:
            continue
        src = "exchange" if tk in listings["exchange"] else "sec"
        queue["pending_first_screen"].append(
            {"tk": tk, "name": nm, "source": src, "first_seen": today})
        added += 1

    # liveness only for names the exchanges once carried and no longer do
    was_exchange = set()
    p = os.path.join(DATA, "raw_nasdaq.csv")
    if os.path.exists(p):
        with open(p, encoding="utf-8", errors="replace") as f:
            was_exchange = {r["symbol"].strip().upper() for r in csv.DictReader(f)}
    flagged_now = {e["tk"] for e in queue["delisted_check"]}
    flagged = 0
    for tk in sorted((universe & was_exchange) - set(listings["exchange"]) - flagged_now):
        queue["delisted_check"].append({"tk": tk, "flagged": today,
                                        "reason": "absent from current exchange symbol directories"})
        flagged += 1

    queue["last_refresh"] = today
    queue["log"].append({"date": today, "new_queued": added, "delist_flagged": flagged,
                         "exchange_listed": len(listings["exchange"]), "sec_filers": len(listings["sec"]),
                         "forced_by_obligation": obliged or None})
    json.dump(queue, open(Q, "w", encoding="utf-8"), indent=1)
    print("universe refresh %s: %d new names queued for first-screen judgment, %d flagged delisted_check; "
          "%d pending total" % (today, added, flagged, len(queue["pending_first_screen"])))
    if obliged:
        print("NOTE: a registered logic change holds open obligations: %s"
              % json.dumps(queue["obligations"]))


if __name__ == "__main__":
    main()
