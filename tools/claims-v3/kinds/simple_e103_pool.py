#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E103 (Q132): the simple predictors on every pool tile, for select_e103.py. Desk compute; it reads no card data but E78's reduction and E92's published fit.

    python3 tools/claims-v3/kinds/simple_e103_pool.py --root <lab repo> --pool <dir> --e78 <e78.json> --out simple-pool.json

Q130(n)'s predictor: real/make_real.py, fitted on E78's 51 kinds, unchanged. E92's flop-price refit: make_e92's counts of each float tile (posthoc_fit_e92.counts_of); select_e103.py applies
posthoc-fit.json's coefficients. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--pool", required=True)
ap.add_argument("--e78", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
K = os.path.join(a.root, "tools/claims-v3/kinds")
sys.path[:0] = [K, os.path.join(K, "real"), os.path.join(a.root, "tools/claims-v3/rpath")]
import make_real as mr  # noqa: E402
sys.argv = ["x", "a", "b"]
import posthoc_fit_e92 as pf  # noqa: E402

P, rows = mr.fit_predictor(json.load(open(a.e78)), a.root)
pool = json.load(open(os.path.join(a.pool, "pool.json")))
out = {}
for k, v in sorted(pool.items()):
    t = v["type"]
    raw = open(os.path.join(a.pool, t, v["name"] + ".bin"), "rb").read()
    f = mr.features(raw, t)
    q = mr.predict_D(P, t, f, rows[t])
    r = {"q130n_w": q["point_w"], "q130n_model": q["model"], "q130n_outside": q["features_outside_e78_range"], "features": f}
    if t != "int8":
        r["counts_e92"] = pf.counts_of(t, raw)
    out[k] = r
json.dump(out, open(a.out, "w"))
print("done", len(out))
