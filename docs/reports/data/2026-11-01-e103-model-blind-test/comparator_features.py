#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""For corrections-check.py: the no-simulator features of E78's kinds and E95's tiles. Desk compute; it reads tiles only.

    python3 comparator_features.py --root <lab repo> --out comparator-features.json

Q130(n)'s features (real/make_real.features) and E92's stream counts (posthoc_fit_e92.counts_of). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
K = os.path.join(a.root, "tools/claims-v3/kinds")
sys.path[:0] = [K, os.path.join(K, "real"), os.path.join(a.root, "tools/claims-v3/rpath")]
import make_real as mr  # noqa: E402
sys.argv = ["x", "a", "b"]
import posthoc_fit_e92 as pf  # noqa: E402

out = {}
kj = json.load(open(os.path.join(K, "kinds.json")))
tiles = []
for t in ("fp32", "fp16", "int8"):
    for kind, v in kj["kinds"][t].items():
        tiles.append((f"{t}.{kind}", t, os.path.join(K, v["file"])))
    d = os.path.join(K, "real2", "tiles", t)
    for f in sorted(os.listdir(d)):
        tiles.append((f"{t}.r2_{f[:-4]}", t, os.path.join(d, f)))
for name, t, p in tiles:
    raw = open(p, "rb").read()
    r = {"features": mr.features(raw, t)}
    if t != "int8":
        r["counts_e92"] = pf.counts_of(t, raw)
    out[name] = r
json.dump(out, open(a.out, "w"), sort_keys=True)
print("done", len(out))
