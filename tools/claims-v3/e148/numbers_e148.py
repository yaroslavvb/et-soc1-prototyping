#!/usr/bin/env python3
"""E148 (desk, written after the run; reported only, no rule reads it): every number the data README quotes, printed from the committed
reduction and scores, so each sentence has a file and a key behind it. Standard library only.

    python3 tools/claims-v3/e148/numbers_e148.py docs/reports/data/2026-11-02-e148-int8-excess > docs/reports/data/2026-11-02-e148-int8-excess/readme-numbers.txt
SPDX-License-Identifier: Apache-2.0"""
import glob
import json
import os
import sys


def f(c, k=3):
    if not isinstance(c, dict) or c.get("mean") is None:
        return "-"
    return f"{c['mean']:+.{k}f}" + ("" if c.get("half") is None else f" ± {c['half']:.{k}f} [{c['lo']:+.{k}f}, {c['hi']:+.{k}f}]")


def main():
    d = sys.argv[1]
    sc = json.load(open(os.path.join(d, "scored.json")))
    red = json.load(open(os.path.join(d, "e148.json")))
    st, R = sc["stats"], sc["rules"]
    print(f"scored on: {sc['which_reduction_scores']}; passes {sc['passes']} (primary kept {sc['primary_kept']}, relaxed {sc['relaxed_kept']}); "
          f"set aside primary {sc['set_aside_primary']} relaxed {sc['set_aside_relaxed']}; leak {sc.get('leak')}")
    print(f"runs kept {red.get('kept')}; failed {red.get('failed')}; idle invalid {red.get('idle_invalid_runs')}; idle level {red['idle_level']}")
    for k in ("N", "N1", "N2", "D21", "N_minus_N1", "r2_over_r1_fp32", "r2_over_r1_int8", "r1_over_m0_fp32", "r1_over_m0_int8"):
        print(f"{k}: {f(st[k])}  per pass {[round(x, 4) for x in st[k]['per_pass']]}")
    print("N1 - N/2 per pass:", [round(x, 4) for x in st["N1_minus_halfN"]])
    for it, a in st["arms"].items():
        print(f"arm {it}: S {f(a['S'])}  D {f(a['D'])}  rate {a['rate']['mean'] / 1e9:.4f}e9  cpo {a['cpo']}")
    for k, v in R.items():
        print(f"rule {k}: {json.dumps(v)[:900]}")
    print("reported:", json.dumps(sc["reported"])[:2500])
    print("cycles_per_op (reduction):", red.get("cycles_per_op"))
    print("tie drift:", red.get("tie_drift_w"), "anchors:", json.dumps(red.get("anchors"))[:800])
    for v in ("relaxed", "dipskept", "auto"):
        p = os.path.join(d, f"scored-{v}.json")
        if os.path.exists(p):
            s = json.load(open(p))
            print(f"arm {v}: passes {s['passes']}; N {f(s['stats']['N'])}; N1 {f(s['stats']['N1'])}; N2 {f(s['stats']['N2'])}; D21 {f(s['stats']['D21'])}; "
                  + "; ".join(f"{k} {x.get('verdict') if isinstance(x, dict) and 'verdict' in x else ''}" for k, x in s["rules"].items() if k != "R6"))
    # heats and run lengths from the raw passes
    for pdir in sorted(glob.glob(os.path.join(d, "aifoundry1-c1", "e148", "p148*"))):
        if ".attempt-" in pdir:
            continue
        heats, n_rec = {}, 0
        rr = os.path.join(pdir, "runs.jsonl")
        if os.path.exists(rr):
            for line in open(rr):
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                n_rec += 1
                heats.setdefault((r.get("pos"), r.get("attempt")), r.get("heats"))
        heats = [h for h in heats.values() if h is not None]
        hs = sorted(heats)
        print(f"{os.path.basename(pdir)}: launch records {n_rec}; heats a run median {hs[len(hs) // 2] if hs else None}, max {max(hs) if hs else None}, n {len(hs)}")


if __name__ == "__main__":
    main()
