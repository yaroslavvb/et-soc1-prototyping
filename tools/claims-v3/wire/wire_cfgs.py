#!/usr/bin/env python3
"""V3-WIRE: the configurations of one pass, in that pass's shuffled order (no device access).

    python3 tools/claims-v3/wire/wire_cfgs.py --root <tree root> --seed S [--only CFG,CFG] [--json OUT]
    python3 tools/claims-v3/wire/wire_cfgs.py --root <tree root> --check-runner

configs.json (next to this file) holds the 28 configurations of PLAN3 V3-WIRE, i.e. workloads/enercat/run_wire.py
--set v2 --only wu/p0/,wu/p0.5/,wu/p1/,wsep/p0/,wsep/p0.5/, in the runner's own list order. The order printed is
random.Random(S).shuffle of that list's indices, which is exactly the order run_wire.py uses for its pass p when
S = --seed + p; the block passes S = 31 + (pass - 1) on aifoundry2 and 41 + (pass - 1) on aifoundry3, so block pass
N reproduces the runner's pass N-1 of `--passes 6 --seed 31` (a2) / `--seed 41` (a3); aifoundry1's cards, which the
runner never ran, take 51 + (pass - 1) (aifoundry1-c0) and 61 + (pass - 1) (aifoundry1-c1), orders of their own.

The table is used instead of importing run_wire.py on the card so that both cards run byte-identical arguments even
if ~/nekko's copy of the runner differs; --check-runner compares the table with the tree's run_wire.py.

Output: one line per configuration, tab separated: cfg, fill pattern, fill operands, burst arguments (space separated).
"""
import argparse
import json
import os
import random
import sys

TABLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="the tree root (lib.sh's V3_ROOT)")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--only", default="", help="exact configuration names (the smoke block uses two)")
    ap.add_argument("--json", help="also write the ordered list here")
    ap.add_argument("--check-runner", action="store_true")
    a = ap.parse_args()
    os.chdir(a.root)
    cfgs = json.load(open(TABLE))["configs"]
    if a.check_runner:
        sys.dont_write_bytecode = True
        sys.path.insert(0, os.path.join(a.root, "workloads", "enercat"))
        try:
            import run_wire as rw
            ref = [c for c in rw.configs_v2() if any(c["cfg"].startswith(k) for k in json.load(open(TABLE))["only"].split(","))]
            mine = [(c["cfg"], "uniq:" + c["fill_operands"], c["args"]) for c in cfgs]
            theirs = [(c["cfg"], c["fill"], c["args"]) for c in ref]
            if mine != theirs:
                print(f"configs.json differs from {a.root}/workloads/enercat/run_wire.py ({len(mine)} vs {len(theirs)} configurations)")
                return 1
            print(f"configs.json matches {a.root}/workloads/enercat/run_wire.py ({len(mine)} configurations)")
            return 0
        except Exception as e:   # an older runner copy (no configs_v2): the table still defines the pass
            print(f"cannot compare with this tree's run_wire.py: {e!r}")
            return 1
    if a.seed is None:
        ap.error("--seed is required")
    order = list(range(len(cfgs)))
    random.Random(a.seed).shuffle(order)
    sel = [cfgs[i] for i in order]
    if a.only:
        names = a.only.split(",")
        sel = [c for c in cfgs if c["cfg"] in names]
        sel.sort(key=lambda c: names.index(c["cfg"]))
        if len(sel) != len(names):
            print("unknown configuration in --only", file=sys.stderr)
            return 2
    for c in sel:
        print("\t".join([c["cfg"], c["fill_pattern"], c["fill_operands"], " ".join(c["args"])]))
    if a.json:
        json.dump({"seed": a.seed, "only": a.only, "order": [c["cfg"] for c in sel]}, open(a.json, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
