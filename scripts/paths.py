# -*- coding: utf-8 -*-
"""One place that knows where things live.

Everything resolves from this file's own location, so the pipeline runs the same
from a checkout on a CI runner as it does from the folder on Jonathan's desktop.
Set BS_ROOT to override, which is only useful if you split data from code.
"""
import os

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("BS_ROOT") or os.path.dirname(SCRIPTS)
DATA = os.path.join(ROOT, "data")
BUILD = os.path.join(ROOT, "build")
LOGS = os.path.join(ROOT, "logs")
PAGE = os.path.join(BUILD, "bs_console.html")

for _d in (DATA, BUILD, LOGS):
    os.makedirs(_d, exist_ok=True)
