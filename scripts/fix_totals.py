# -*- coding: utf-8 -*-
"""Data hygiene: totals must be numbers. Move prose into a notes column."""
import os
from paths import DATA
import glob, re
import pandas as pd

D = DATA
fixed = 0
for f in sorted(glob.glob(os.path.join(D, "final_light_w*.csv"))) + sorted(glob.glob(os.path.join(D, "final_deep_f*.csv"))):
    df = pd.read_csv(f, on_bad_lines="skip")
    if "total" not in df.columns:
        continue
    notes, nums, touched = [], [], 0
    for v in df["total"].astype(str):
        m = re.match(r"\s*(\d+(?:\.\d+)?)\s*(.*)$", v.strip())
        if m:
            nums.append(float(m.group(1)))
            extra = m.group(2).strip().strip("()").strip()
            notes.append(extra)
            if extra:
                touched += 1
        else:
            nums.append(None)
            notes.append(v.strip())
            touched += 1
    df["total"] = nums
    if "confirm_note" not in df.columns:
        df["confirm_note"] = notes
    else:
        df["confirm_note"] = [a or b for a, b in zip(notes, df["confirm_note"].astype(str))]
    df.to_csv(f, index=False)
    if touched:
        fixed += touched
        print(f"  {f.split(chr(92))[-1]}: {touched} rows cleaned")
print(f"TOTAL rows repaired: {fixed}")

# verify
bad = 0
for f in sorted(glob.glob(os.path.join(D, "final_*.csv"))):
    df = pd.read_csv(f, on_bad_lines="skip")
    if "total" in df.columns:
        v = pd.to_numeric(df["total"], errors="coerce")
        bad += int(v.isna().sum())
print(f"non-numeric totals remaining across all final CSVs: {bad}")
