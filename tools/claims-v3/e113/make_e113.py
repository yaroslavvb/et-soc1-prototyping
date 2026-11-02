#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E113 (Q133): the operand set for the A side's two layouts at fixed Hamming weight.

    python3 tools/claims-v3/e113/make_e113.py <out-dir>            # tiles/, srcs/, manifest.json
    python3 tools/claims-v3/e113/make_e113.py <out-dir> --check    # also re-derive every count from the files

It first writes make_hl.py's whole set unchanged (so every file E60, E65, E67 and E70 ran is byte-identical here,
and the runner, block.sh and reduce_hl.py read this directory exactly as they read build/hl-gen5), then adds:

  alq_h3, alq_h6   the low layout at k = 3 and 6 (E70 ran k = 1, 2, 4, 8, 12, 16, 23), so both layouts have every k
  als_h<k>         the SPREAD layout on A, k = 2, 3, 4, 6, 8, 12, 16: A's k flipping bits spread evenly over the 23
                   mantissa positions with make_hl.spread_mask(k), the mask E70's B-side ls_h<k> used. Same shared A
                   base word as abit_<j> and alq_h<k>, B = 1.0 (the quiet partner), zero aq_h0. At k = 23 the spread
                   mask is the low mask, so alq_h23 is both layouts' top rung (as lq_h23 was on B).

Every item carries "zero": "aq_h0", which reduce_hl.py's item_zero() reads before its family map.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hl"))
import make_hl as H  # noqa: E402  (read only: E70's generator and helpers)

ALQ_NEW = [3, 6]
ALS_K = [2, 3, 4, 6, 8, 12, 16]


def build(out):
    items = H.build(out)                       # make_hl.py's whole set, unchanged, and its manifest
    a0, _ = H.a_base_words()
    for k in ALQ_NEW:
        A, B = H.a_tiles(a0, a0 ^ H.low_mask(k), H.ONE)
        nm = f"alq_h{k}"
        H.write_tiles(f"{out}/tiles/{nm}.bin", A, B)
        items.append({"name": nm, "kind": "fma", "family": "alq", "h": k, "mask": hex(H.low_mask(k)),
                      "partner_b": "1.0", "zero": "aq_h0", "flips": H.fma_flips(A, B), "added_by": "E113"})
    for k in ALS_K:
        m = H.spread_mask(k)
        assert H.is_normal(a0) and H.is_normal(a0 ^ m)
        A, B = H.a_tiles(a0, a0 ^ m, H.ONE)
        nm = f"als_h{k}"
        H.write_tiles(f"{out}/tiles/{nm}.bin", A, B)
        items.append({"name": nm, "kind": "fma", "family": "als", "h": k, "mask": hex(m),
                      "bits": [b for b in range(23) if m >> b & 1],
                      "partner_b": "1.0", "zero": "aq_h0", "flips": H.fma_flips(A, B), "added_by": "E113"})
    json.dump({"seed": H.SEED, "items": items, "e113": {"alq_new": ALQ_NEW, "als_k": ALS_K}},
              open(f"{out}/manifest.json", "w"), indent=1)
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    items = build(a.out)
    for it in items:
        if it.get("added_by") == "E113":
            f = it["flips"]
            print(f"{it['name']:10s} mask {it['mask']:>10s}  A bits flipped per op (8 lanes) {f['a_all']:6d} "
                  f"(mant {f['a_mant']}, exp {f['a_exp']}, sign {f['a_sign']})  B {f['b_all']}")
    if a.check:
        for it in items:
            if it["kind"] == "fma" and "flips" in it:
                raw = np.fromfile(f"{a.out}/tiles/{it['name']}.bin", dtype="<u4")
                A, B = raw[:256].reshape(16, 16).tolist(), raw[256:].reshape(16, 16).tolist()
                assert H.fma_flips(A, B) == it["flips"], it["name"]
        print(f"check: every count re-derived from the files ({sum(1 for i in items if i['kind'] == 'fma' and 'flips' in i)} fma items)")


if __name__ == "__main__":
    main()
