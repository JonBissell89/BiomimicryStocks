# -*- coding: utf-8 -*-
"""One-time migration: the four growing price JSONs into data/market.db.

Verifies the round trip before touching anything: what marketdb loads back
must equal what the JSON held, value for value. Idempotent; refuses to run
if the database already carries data unless --force is given.
"""
import json, os, sys
from paths import DATA
import marketdb

R = os.path.join(DATA, "rigor")
FILES = {
    "price_cache": os.path.join(DATA, "price_cache.json"),
    "spark": os.path.join(DATA, "spark.json"),
    "price_track": os.path.join(R, "price_track.json"),
    "universe_track": os.path.join(R, "universe_track.json"),
}

con = marketdb.connect()
have = con.execute("SELECT count(*) FROM price_cache").fetchone()[0]
con.close()
if have and "--force" not in sys.argv:
    print("market.db already carries %d cached prices; refusing to re-migrate (use --force)" % have)
    sys.exit(0)

missing = [k for k, p in FILES.items() if not os.path.exists(p)]
if missing:
    print("nothing to migrate; missing source files:", ", ".join(missing))
    sys.exit(0)

pc = json.load(open(FILES["price_cache"], encoding="utf-8"))
sp = json.load(open(FILES["spark"], encoding="utf-8"))
pt = json.load(open(FILES["price_track"], encoding="utf-8"))
ut = json.load(open(FILES["universe_track"], encoding="utf-8"))

marketdb.save_price_cache(pc)
marketdb.save_spark(sp)
for s in pt["snapshots"]:
    marketdb.append_price_snapshot(s["date"], s["px"])
for s in ut["snapshots"]:
    marketdb.append_universe_snapshot(s["date"], s["px"])
con = marketdb.connect()
with con:
    con.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('universe_cadence_days',?)",
                (str(ut.get("cadence_days", 28)),))
con.close()

# the round trip must be exact before the JSON files may go
errs = []
if marketdb.load_price_cache() != pc: errs.append("price_cache")
if marketdb.load_spark() != sp: errs.append("spark")
if marketdb.load_price_track() != pt: errs.append("price_track")
if marketdb.load_universe_track() != ut: errs.append("universe_track")
if errs:
    print("ROUND TRIP FAILED for: %s -- JSON files left in place" % ", ".join(errs))
    sys.exit(1)

print("migrated and verified: %d cached prices, %d sparklines, %d ranked snapshots, %d universe snapshots"
      % (len(pc["px"]), len(sp["s"]), len(pt["snapshots"]), len(ut["snapshots"])))
print("round trip exact; the JSON sources may be removed")
