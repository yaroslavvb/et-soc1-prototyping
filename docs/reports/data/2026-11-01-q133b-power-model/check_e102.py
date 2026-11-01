#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q133(b): M5 and M4 on E102's single-bit prices, a set neither was fitted on (aifoundry1 card 1; each price over its own
zero item, as E103's score_all.py reads them). Post hoc for both: E102's data were on main before either form was chosen.

    python3 check_e102.py > check-e102.txt
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_m5 as F  # noqa: E402
from predict_blind3 import m4_reproduced  # noqa: E402

E102 = os.path.join(F.DD, "2026-11-01-e102-balanced-bit-prices")
GROUPS = {"fp32 B balanced": lambda e: e["type"] == "fp32" and e["layout"] == "bp", "fp32 B all-in": lambda e: e["type"] == "fp32" and e["layout"] == "bj",
          "fp32 A balanced": lambda e: e["type"] == "fp32" and e["layout"] == "ap", "fp32 A all-in": lambda e: e["type"] == "fp32" and e["layout"] == "aj",
          "fp16 balanced": lambda e: e["type"] == "fp16" and e["layout"] in ("bp", "ap"), "fp16 all-in": lambda e: e["type"] == "fp16" and e["layout"] in ("bj", "aj"),
          "int8 B": lambda e: e["type"] == "int8"}


def main():
    rows, _ = F.assemble()
    m4 = m4_reproduced(rows)
    m5 = F.load(os.path.join(HERE, "m5.json"))["families"]
    sc = F.load(os.path.join(E102, "scored.json"))["primary"]
    c102 = F.load(os.path.join(E102, "bench", "counts-e102.json"))["rows"]
    t102 = F.load(os.path.join(F.K, "e102", "e102.json"))["tiles"]

    def feats(kind, t):
        f = F.fmt_feats(F.bench_feats(c102[kind]["mean"], c102[f"{t}.zeros"]["mean"] if f"{t}.zeros" in c102 else F.load(os.path.join(F.B, "counts-v2.json"))["rows"][f"{t}.zeros"]["mean"]), t)
        p = os.path.join(F.K, "e102", "tiles", t, kind.split(".", 1)[1] + ".bin")
        f.update({k: v for k, v in F.tile_feats(p, t).items() if k != "sha256"})
        return f

    out = {}
    for g, want in GROUPS.items():
        res = []
        for name, e in sc["prices"].items():
            if not want(e) or e["board"]["W"]["mean"] is None:
                continue
            t = e["type"]
            kind = f"{t}.{name.split('@')[0].split('.', 1)[1]}"
            z = t102[kind].get("zero")
            if z is None or kind not in c102:
                continue
            zk = z if "." in z else f"{t}.{z}"
            if zk not in c102:
                continue
            fa, fz = feats(kind, t), feats(zk, t)
            fam = "int8" if t == "int8" else "float"
            rate = F.RATE[t]
            p = {}
            for w in ("M5", "M4"):
                if w == "M5":
                    b, terms, s = np.array(m5[fam]["coef_J"]), m5[fam]["terms"], m5[fam]["card1_scale"]
                else:
                    b, terms, s = m4[fam]["b"], m4[fam]["terms"], m4[fam]["scale"]
                p[w] = float(np.array([rate * (fa[q] - fz[q]) for q in terms]) @ b) * s
            res.append({"key": name, "D": e["board"]["W"]["mean"], **p})
        if len(res) >= 2:
            y = np.array([r["D"] for r in res])
            o = {"n": len(res)}
            for w in ("M5", "M4"):
                pp = np.array([r[w] for r in res])
                o[w] = {"rms_w": float(np.sqrt(np.mean((y - pp) ** 2))), "bias_w": float(np.mean(pp - y)), "measured_over_predicted": float(pp @ y / (pp @ pp))}
            out[g] = o
            print(f"{g:16s} n {len(res):2d}  M5 rms {o['M5']['rms_w']:.3f} bias {o['M5']['bias_w']:+.3f} meas/pred {o['M5']['measured_over_predicted']:.3f}   "
                  f"M4 rms {o['M4']['rms_w']:.3f} bias {o['M4']['bias_w']:+.3f} meas/pred {o['M4']['measured_over_predicted']:.3f}")
    json.dump(out, open(os.path.join(HERE, "check-e102.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
