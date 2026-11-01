#!/usr/bin/env python3
"""E97 Part A: E89's registered reducer, tools/claims-v3/e89/reduce_e89.py, byte for byte, on E97's blocks. Only its module-level block names change
(BLOCK_ITEMS, REF, LOW), and its denominators come from E78's e78.json plus E86's three int8 real tiles (e86.json), in a merged file it writes beside its output. Its
rules are read from E89's frozen predictions-e89.json, so reducer/scored.json scores E89's rules, with E89's bands, with the lap as the unit. E97's own verdicts, with the pass
as the unit, are score_e97.py's.

    python3 tools/claims-v3/e97/reduce_e97.py <pass dir> [<pass dir> ...] --out <dir>
writes <dir>/reducer/{e89.json, scored.json, results.md, denominators.json}
"""
import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e97_common as c  # noqa: E402

E78_JSON = os.path.join(c.ROOT, "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json")
E86_JSON = os.path.join(c.ROOT, "docs/reports/data/2026-10-31-e86-real-tensors-energy/e86.json")
E89_PRED = os.path.join(c.TOOLS, "e89", "predictions-e89.json")
REDUCER = os.path.join(c.TOOLS, "e89", "reduce_e89.py")


def load_reducer():
    spec = importlib.util.spec_from_file_location("reduce_e89_e97", REDUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.BLOCK_ITEMS = dict(c.BLOCKS)
    mod.REF = c.REF_BLOCK
    mod.LOW = list(c.LOW_BLOCKS)
    return mod


def merged_denominators(path):
    e78 = json.load(open(E78_JSON))
    e86 = json.load(open(E86_JSON))
    items = {k: e78["items"][k] for k in e78["items"]}
    for k, v in e86["items"].items():
        if k.startswith("int8.real_"):
            items[k] = v
    json.dump({"what": "E78's items (e78.json) plus E86's three int8 real tiles (e86.json), unchanged", "items": items}, open(path, "w"), indent=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--allow-different-reused", action="store_true", help="only for the self-test's copies")
    a = ap.parse_args()
    if not a.allow_different_reused:
        bad = c.check_reused()
        if bad:
            raise SystemExit("E97: a reused file differs from the freeze: " + "; ".join(bad))
    out = os.path.join(a.out, "reducer")
    os.makedirs(out, exist_ok=True)
    den = os.path.join(out, "denominators.json")
    merged_denominators(den)
    red = load_reducer()
    sys.argv = ["reduce_e89.py"] + a.dirs + ["--out", out, "--e78", den, "--pred", E89_PRED]
    red.main()


if __name__ == "__main__":
    main()
