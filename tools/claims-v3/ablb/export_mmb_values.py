#!/usr/bin/env python3
"""ABLB-2b's kernel clause input for tools/claims-v3/ablb/reduce.py --mmb-values, from V3-MMB's passes.

    python3 tools/claims-v3/ablb/export_mmb_values.py --data <dir with one directory per card> --out <results>/inputs/mmb_values.json

PLAN3 V3-ABL-B, ABLB-2b: "the difference is the kernel" is kept only if V3-MMB's mmbench int8 above-idle exceeds this
session's int8_randn_l1 above-idle by > 10 W on each card. V3-MMB defines that quantity in MMB-c: per pass, the
int8-tensor-L2 E1 workload's above-idle power, mean_w - idle_before_w (mmbench-power.py's results.json). The values
here are exactly MMB-c's pass values: tools/claims-v3/mmb/reduce.py's load_card and e1_values(D, card,
"int8-tensor-L2", "above_idle_w"), imported unchanged, so the same drop rules apply (launch implied clock, the
registered and busy clock rules, power_ok). Shape: {"<card>": [W per kept pass, pass order], ...}; "passes" and
"unit" are records, not read by the reducer.
"""
import argparse
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
WORKLOAD = "int8-tensor-L2"


def mmb_reduce():
    """tools/claims-v3/mmb/reduce.py as a module (load_card, e1_values), unchanged."""
    p = os.path.join(HERE, "..", "mmb", "reduce.py")
    spec = importlib.util.spec_from_file_location("mmb_reduce", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    M = mmb_reduce()
    cards = [c for c in sorted(os.listdir(a.data)) if os.path.isdir(os.path.join(a.data, c, "mmb"))]
    D = {c: M.load_card(os.path.join(a.data, c), c) for c in cards}
    out = {"unit": "W", "quantity": f"V3-MMB {WORKLOAD} above idle (mean_w - idle_before_w) per kept pass, "
           "as MMB-c (tools/claims-v3/mmb/reduce.py e1_values)", "passes": {}}
    for c in cards:
        vals = M.e1_values(D, c, WORKLOAD, "above_idle_w")
        ks = [P["pass"] for P in D[c]["passes"] if WORKLOAD in P["e1"] and P["e1"][WORKLOAD]["power_ok"]
              and P["e1"][WORKLOAD]["above_idle_w"] is not None]
        assert len(ks) == len(vals)
        out[c] = [round(v, 6) for v in vals]
        out["passes"][c] = ks
        print(f"{c}: {WORKLOAD} above idle W per pass {dict(zip(ks, out[c]))}"
              + (f", mean {sum(vals) / len(vals):.3f}" if vals else ""))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
