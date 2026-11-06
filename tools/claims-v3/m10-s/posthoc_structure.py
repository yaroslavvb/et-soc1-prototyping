#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q145(b), POST HOC (written after term S's fit outputs; it decides nothing): where M10's single-bit miss sits, by the tiles' byte
structure. Every one of M10's 959 rows is classed by T_S (term_s.t_s) on its tile's bytes: a single B bit with one base word in all
lanes (pool 6's and 7's case S), a single B bit with eight base words (the price lists' construction; E102's and E147's rows), the
structure's zero with one word in every lane (a one-number B against a one-word A), its zero with eight words, or other. For each class
it reports M10's committed held-out errors (rows-m10.json, err_w["B+a+b"] for floats, ["B"] for int8): a reading, never a verdict.

    python3 -B posthoc_structure.py > posthoc-structure.txt      (writes posthoc-structure.json beside --out, default the data dir)
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import term_s as TS  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(TS.DD, "2026-11-06-q145b-m10-s")
rows, _ = TS.FM.assemble()
by = {(r["exp"], r["key"]): r for r in rows}
cls = {}
for r in TS.load(os.path.join(TS.M10D, "rows-m10.json")):
    a = by[(r["exp"], r["key"])]
    if a["type"] not in TS.ONE:
        continue
    p = os.path.join(TS.TOP, a["tile_path"]) if a.get("tile_path") else None
    s = TS.t_s(open(p, "rb").read(), a["type"]) if p and os.path.exists(p) else None
    if s is None:
        c = "other"
    elif s.get("zero"):
        c = "zero, one word in every lane" if s["one_base"] else "zero, eight lane words"
    else:
        c = "single B bit, one base word" if s["one_base"] else "single B bit, eight base words"
    e = r["err_w"]["B+a+b"]
    cls.setdefault(c, []).append({"exp": r["exp"], "key": r["key"], "card": r["card"], "type": a["type"], "e_w": e,
                                  "a_word": f"{s['a_word']:08x}" if s else None, "bit": (s or {}).get("bit")})
out = {"label": "POST HOC (after term S's outputs): M10's committed held-out errors by the tiles' structure", "classes": {}}
for c, v in sorted(cls.items()):
    es = [x["e_w"] for x in v]
    out["classes"][c] = {"n_rows": len(v), "rms_w": math.sqrt(sum(e * e for e in es) / len(es)), "bias_w": sum(es) / len(es),
                         "by_card": {cd: {"n": len([x for x in v if x["card"] == cd]),
                                          "bias_w": (sum(x["e_w"] for x in v if x["card"] == cd) / max(1, len([x for x in v if x["card"] == cd])))}
                                     for cd in ("a3", "c1")},
                         "rows": v if c != "other" else None}
json.dump(out, open(os.path.join(OUT, "posthoc-structure.json"), "w"), indent=1)
for c, v in out["classes"].items():
    print(f"{c:34s} n {v['n_rows']:4d}  rms {v['rms_w']:.3f} W  bias {v['bias_w']:+.3f} W  "
          f"(a3 {v['by_card']['a3']['n']} {v['by_card']['a3']['bias_w']:+.3f}; c1 {v['by_card']['c1']['n']} {v['by_card']['c1']['bias_w']:+.3f})")
    if c.startswith("zero, one word") or c.startswith("single B bit, one"):
        for x in v["rows"]:
            print(f"      {x['exp']} {x['card']} {x['key']:40s} A {x['a_word']} bit {x['bit']}  e {x['e_w']:+.3f}")
