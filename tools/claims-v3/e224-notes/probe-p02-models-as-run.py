#!/usr/bin/env python3
"""reg-e224 probe after the rule's hash (no freeze): do MM1-v3.1, MM1-v3 and MM1-v2's frozen calls answer at family P's kinds (E212 and E217
patterns) or raise? One P point a kind, arm A 600 MHz; prints only whether each returns energy."""
import os, sys
C = sys.argv[1]
sys.path.insert(0, os.path.join(C, "tools", "claims-v3", "e224", "desk"))
import models_e224 as MZ
M = MZ.Models()
for kind in ("random", "zeros", "ones", "pattern:fld_mant", "pattern:th_top", "pattern:h_th_in", "pattern:i8_t46"):
    fmt = {"pattern:h_th_in": "fp16", "pattern:i8_t46": "int8"}.get(kind, "fp32")
    for mdl in MZ.MODELS:
        try:
            o = M.forecast([{"id": "x", "arm": "gemmL5x1x4", "fmt": fmt, "kind": kind, "mask": "0xffffffff"}], f=600.0, card=MZ.C1, models=(mdl,), cands=False)["x"][mdl]
            print(kind, fmt, mdl, "W" if o.get("W_over_idle") is not None else ("NOT FORECAST: " + str(o.get("energy"))[:80]))
        except Exception as e:
            print(kind, fmt, mdl, "RAISED", type(e).__name__, str(e)[:120])
