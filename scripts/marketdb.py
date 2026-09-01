# -*- coding: utf-8 -*-
"""The market database: every growing price series in one SQLite file.

The judgment layer stays as JSON, where a human-readable diff matters and the
vintage hashes bind the content. Prices are different: they only ever append,
nobody reviews them line by line, and the JSON files were growing without
bound. This module owns data/market.db and hands each script exactly the
shape its JSON file used to hold, so the instruments read what they always
read. All writes are transactional; a killed job never leaves a half-written
snapshot the way a truncated json.dump could.
"""
import json, os, sqlite3
from paths import DATA

DB = os.path.join(DATA, "market.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS price_cache(ticker TEXT PRIMARY KEY, px REAL);
CREATE TABLE IF NOT EXISTS spark(ticker TEXT PRIMARY KEY, series TEXT);
CREATE TABLE IF NOT EXISTS price_track(date TEXT, ticker TEXT, px REAL,
    PRIMARY KEY(date, ticker));
CREATE TABLE IF NOT EXISTS universe_track(date TEXT, ticker TEXT, px REAL,
    PRIMARY KEY(date, ticker));
"""


def connect():
    con = sqlite3.connect(DB)
    con.executescript(_SCHEMA)
    return con


def _meta(con, key, default=None):
    row = con.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return row[0] if row else default


def _set_meta(con, key, value):
    con.execute("INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)", (key, str(value)))


# ---- price cache: {"asof": date, "px": {ticker: price-or-None}} -------------

def load_price_cache():
    con = connect()
    try:
        px = {tk: p for tk, p in con.execute("SELECT ticker, px FROM price_cache")}
        return {"asof": _meta(con, "price_cache_asof"), "px": px}
    finally:
        con.close()


def save_price_cache(doc):
    con = connect()
    try:
        with con:
            _set_meta(con, "price_cache_asof", doc["asof"])
            con.execute("DELETE FROM price_cache")
            con.executemany("INSERT INTO price_cache(ticker,px) VALUES(?,?)",
                            list(doc["px"].items()))
    finally:
        con.close()


# ---- sparklines: {"asof": date, "n": count, "s": {ticker: [floats]}} --------

def load_spark():
    con = connect()
    try:
        s = {tk: json.loads(v) for tk, v in con.execute("SELECT ticker, series FROM spark")}
        return {"asof": _meta(con, "spark_asof"), "n": int(_meta(con, "spark_n", 0)), "s": s}
    finally:
        con.close()


def save_spark(doc):
    con = connect()
    try:
        with con:
            _set_meta(con, "spark_asof", doc["asof"])
            _set_meta(con, "spark_n", doc["n"])
            con.execute("DELETE FROM spark")
            con.executemany("INSERT INTO spark(ticker,series) VALUES(?,?)",
                            [(tk, json.dumps(v, separators=(",", ":"))) for tk, v in doc["s"].items()])
    finally:
        con.close()


# ---- snapshot tracks: {"snapshots": [{"date": d, "px": {ticker: price}}]} ---

def _load_track(table):
    con = connect()
    try:
        snaps = {}
        for d, tk, p in con.execute(
                "SELECT date, ticker, px FROM %s ORDER BY date" % table):
            snaps.setdefault(d, {})[tk] = p
        return [{"date": d, "px": px} for d, px in sorted(snaps.items())]
    finally:
        con.close()


def _append_snapshot(table, date, px):
    con = connect()
    try:
        with con:
            con.executemany("INSERT OR REPLACE INTO %s(date,ticker,px) VALUES(?,?,?)" % table,
                            [(date, tk, p) for tk, p in px.items()])
    finally:
        con.close()


def load_price_track():
    return {"snapshots": _load_track("price_track")}


def append_price_snapshot(date, px):
    _append_snapshot("price_track", date, px)


def load_universe_track():
    con = connect()
    try:
        cadence = int(_meta(con, "universe_cadence_days", 28))
    finally:
        con.close()
    return {"cadence_days": cadence, "snapshots": _load_track("universe_track")}


def append_universe_snapshot(date, px):
    _append_snapshot("universe_track", date, px)
