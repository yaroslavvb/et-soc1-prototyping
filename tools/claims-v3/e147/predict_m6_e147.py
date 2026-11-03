#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E147 (Q138): M6's and M5's frozen predictions for E147's tiles, computed mechanically with Q137(m)'s committed code and
model (no refit, nothing tuned), as Q137(m)'s predict_blind4.py computes them for blind pool 4. Desk only.

    python3 tools/claims-v3/e147/predict_m6_e147.py [--tiles <e1xx-tiles.json> --tile-dir <dir> --counts <json>[,<json>...]
                                                     --out <json>]

Defaults: E147's 73 tiles (tools/claims-v3/e147/e147/), the bench's counts of them (docs/reports/data/
2026-11-02-e147-bit-prices-rest/bench/counts-e147.json, with E134's counts-e134.json for the three tiles E147 reuses from
E134 without re-counting: a67q, bj_16, bp_16), written to .../bench/m6-e147.json. With E134's files it gives the same
numbers for E134's 57 tiles (post hoc there: E134 ran before M6 was frozen, though M6's fit left E134's rows out).

For every tile: M6's and M5's D, board W over the format's zeros at 600 MHz on aifoundry3 card 0 (Q137(m)'s footing: the
model's terms times its rate, fit_m5.RATE), x @ coef_J exactly as predict_blind4.py computes it. For every item: the STEP over
its own zero, D(item) - D(zero), and that step per designed flipped bit, fJ. The interval M6 claims for one row is 1.96 x its
nested rms for fp32 on aifoundry3 (m6.json > families > float > interval_pool_by_format_card > fp32|a3); a step is a
difference of two rows of one session, so that band is reported beside it, never used as a rule's line.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MODEL = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-q137m-model")
sys.path.insert(0, MODEL)
import fit_m6 as M  # noqa: E402  (Q137(m)'s, unchanged; it imports M5's fit_m5 as M.F)
F = M.F
DATA = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e147-bit-prices-rest")
E134_COUNTS = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e134-bit-prices-more", "bench", "counts-e134.json")
REL = lambda p: os.path.relpath(p, ROOT)  # noqa: E731


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tiles", default=os.path.join(HERE, "e147", "e147-tiles.json"))
    ap.add_argument("--tile-dir", default=os.path.join(HERE, "e147"))
    ap.add_argument("--counts", default=os.path.join(DATA, "bench", "counts-e147.json") + "," + E134_COUNTS)
    ap.add_argument("--out", default=os.path.join(DATA, "bench", "m6-e147.json"))
    a = ap.parse_args()
    m6p = os.path.join(MODEL, "m6.json")
    m5p = os.path.join(F.DD, "2026-11-01-q133b-power-model", "m5.json")
    m6 = json.load(open(m6p))
    m5 = json.load(open(m5p))
    zc = json.load(open(os.path.join(F.DD, "2026-11-01-q132-rtl-bench", "counts-v2.json")))["rows"]
    zero_row = zc["fp32.zeros"]["mean"]
    tiles = json.load(open(a.tiles))["tiles"]
    counts, csrc = {}, {}
    for cp in a.counts.split(","):
        for name, row in json.load(open(cp))["rows"].items():
            if name not in counts:                     # the first file named wins; later files fill what it lacks
                counts[name] = row
                csrc[name] = REL(cp)
            else:                                      # a tile counted twice must count the same (the bench is deterministic)
                same = (row["mean"]["vpu"]["nets_map"] == counts[name]["mean"]["vpu"]["nets_map"] and
                        row["mean"]["ff"]["all"]["clocked"] == counts[name]["mean"]["ff"]["all"]["clocked"])
                csrc[name] += f" = {REL(cp)}" if same else f" DIFFERS FROM {REL(cp)}"
    t = "fp32"
    rate = F.RATE[t]
    out = {"_note": "E147: M6's and M5's frozen predictions (Q137(m)'s code and model, unchanged) for E147's tiles; "
                    "board W over the format's zeros (D) and each item's step over its own zero, aifoundry3 card 0, 600 MHz",
           "m6_sha256": sha_file(m6p), "m5_sha256": sha_file(m5p), "fit_m6_sha256": sha_file(os.path.join(MODEL, "fit_m6.py")),
           "fit_m5_sha256": sha_file(os.path.join(F.DD, "2026-11-01-q133b-power-model", "fit_m5.py")),
           "tiles_json": REL(a.tiles), "tiles_json_sha256": sha_file(a.tiles),
           "counts": {REL(cp): sha_file(cp) for cp in a.counts.split(",")}, "rate_ops_per_s": rate,
           "m6_row_band_w": round(1.96 * m6["families"]["float"]["interval_pool_by_format_card"]["fp32|a3"]["rms_w"], 4),
           "tiles": {}, "items": {}}
    D = {}
    for name, meta in sorted(tiles.items()):
        p = os.path.join(a.tile_dir, meta["file"])
        crow = counts.get(name)
        if crow is None:
            out["tiles"][name] = {"error": "no bench count"}
            continue
        f = F.fmt_feats(F.bench_feats(crow["mean"], zero_row), t)
        f.update({k: v for k, v in F.tile_feats(p, t).items() if k != "sha256"})
        f.update(M.flip_feats(p, t))
        rec = {"sha256": sha_file(p), "counts_from": csrc[name], "check_mismatch": crow["mean"].get("check_mismatch"),
               "features": f}
        for lab, mod in (("M6", m6["families"]["float"]), ("M5", m5["families"]["float"])):
            x = np.array([rate * f[q] for q in mod["terms"]])
            rec[f"{lab}_D_w"] = float(x @ np.array(mod["coef_J"]))
            # the step's terms, kept for the report: each term's watts
            rec[f"{lab}_terms_w"] = {q: float(rate * f[q] * c) for q, c in zip(mod["terms"], mod["coef_J"])}
        out["tiles"][name] = rec
        D[name] = rec
    for name, meta in sorted(tiles.items()):
        z = meta.get("zero")
        if not z or name not in D or z not in D:
            continue
        fl = meta["designed_flips_per_op"]
        it = {"zero": z, "bit": meta["bit"], "side": meta["side"], "layout": meta["layout"], "word": meta["word"],
              "designed_flips_per_op": fl}
        for lab in ("M6", "M5"):
            step = D[name][f"{lab}_D_w"] - D[z][f"{lab}_D_w"]
            it[f"{lab}_step_w"] = round(step, 4)
            it[f"{lab}_fJ_per_flip"] = round(1e15 * step / (fl * rate), 2)
            it[f"{lab}_step_terms_w"] = {q: round(D[name][f"{lab}_terms_w"][q] - D[z][f"{lab}_terms_w"][q], 4)
                                         for q in D[name][f"{lab}_terms_w"]}
        out["items"][name] = it
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True)
    miss = [n for n, r in out["tiles"].items() if "error" in r]
    bad = [n for n, r in out["tiles"].items() if r.get("check_mismatch") not in (0, 0.0, None)]
    print(json.dumps({"wrote": REL(a.out), "tiles": len(out["tiles"]), "items": len(out["items"]), "no_count": miss,
                      "check_mismatch": bad, "row_band_w": out["m6_row_band_w"]}))


if __name__ == "__main__":
    main()
