# -*- coding: utf-8 -*-
"""The judging logic is versioned, and changing it creates an obligation.

A score is only comparable to another score made the same way. The documents
that define the way (the ones a blind scorer is handed) are hashed here; the
rigor audit fails any build where they changed without being registered. Two
kinds of change exist and the person making it must say which:

  --prose "why"   the documents changed but the judgment did not (recorded
                  results, wording). Re-hash, log, no obligation.
  --logic "why"   the way of judging changed. The version bumps and the
                  refresh queue is stamped with what a new instrument owes:
                  a full universe re-screen and a ranked re-score. The
                  quarterly refresh runs immediately on that stamp, and the
                  obligation stays visible on the page until fulfilled.
  --fulfill       the re-screen and re-score happened; clear the obligation
                  (records into history what was cleared and when).

No argument: report status.
"""
import datetime, hashlib, json, os, sys
from paths import DATA, ROOT

LOGIC_FILES = ["V2_RUBRIC.md", "FRAMEWORK.md"]
P = os.path.join(DATA, "rigor", "logic_version.json")
Q = os.path.join(DATA, "refresh_queue.json")


def hashes():
    out = {}
    for fn in LOGIC_FILES:
        with open(os.path.join(ROOT, fn), "rb") as f:
            out[fn] = hashlib.sha256(f.read()).hexdigest()
    return out


def load():
    if os.path.exists(P):
        return json.load(open(P, encoding="utf-8"))
    return None


def save(doc):
    json.dump(doc, open(P, "w", encoding="utf-8"), indent=1)


def drift(doc):
    now = hashes()
    return [fn for fn in LOGIC_FILES if now.get(fn) != doc["files"].get(fn)]


def main():
    today = datetime.date.today().isoformat()
    doc = load()
    if doc is None:
        doc = {"version": "v2.0", "registered": today, "files": hashes(),
               "note": ("hashes of the documents that define the judgment; "
                        "audit_rigor fails when they drift unregistered"),
               "history": [{"date": today, "version": "v2.0", "kind": "initial"}]}
        save(doc)
        print("logic registered: v2.0 over %s" % ", ".join(LOGIC_FILES)); return

    changed = drift(doc)
    reason = next((a for a in sys.argv[1:] if not a.startswith("--")), "")

    if "--prose" in sys.argv:
        if not changed:
            print("nothing drifted; nothing to register"); return
        doc["files"] = hashes()
        doc["history"].append({"date": today, "version": doc["version"],
                               "kind": "prose", "files": changed, "reason": reason})
        save(doc)
        print("prose change registered on %s; version stays %s" % (", ".join(changed), doc["version"]))
        return

    if "--logic" in sys.argv:
        major, minor = doc["version"].lstrip("v").split(".")
        doc["version"] = "v%s.%d" % (major, int(minor) + 1)
        doc["registered"] = today
        doc["files"] = hashes()
        doc["history"].append({"date": today, "version": doc["version"],
                               "kind": "logic", "files": changed, "reason": reason})
        save(doc)
        q = json.load(open(Q, encoding="utf-8"))
        q["obligations"] = {"logic_version": doc["version"], "registered": today,
                            "universe_rescreen": True, "ranked_rescore": True,
                            "reason": reason or "logic change"}
        json.dump(q, open(Q, "w", encoding="utf-8"), indent=1)
        print("LOGIC CHANGE registered: %s. The refresh queue now owes a full "
              "universe re-screen and a ranked re-score; the next refresh run "
              "fires regardless of cadence." % doc["version"])
        return

    if "--fulfill" in sys.argv:
        q = json.load(open(Q, encoding="utf-8"))
        if not q.get("obligations"):
            print("no open obligation"); return
        doc["history"].append({"date": today, "version": doc["version"],
                               "kind": "fulfilled", "cleared": q["obligations"],
                               "reason": reason})
        save(doc)
        q["obligations"] = {}
        json.dump(q, open(Q, "w", encoding="utf-8"), indent=1)
        print("obligation cleared and recorded"); return

    # status
    if changed:
        print("DRIFT: %s changed since %s was registered. Run register_logic.py "
              "--prose or --logic with a reason." % (", ".join(changed), doc["version"]))
        sys.exit(1)
    print("logic %s registered %s; documents match" % (doc["version"], doc["registered"]))


if __name__ == "__main__":
    main()
