#!/usr/bin/env python3
"""E155 (desk, written while the passes ran and before any reduction was read; reported only, no rule reads it): every number the data README quotes,
printed from the committed reduction and scores, so each sentence has a file and a key behind it. A port of tools/claims-v3/e148/numbers_e148.py.
Standard library only.

    python3 tools/claims-v3/e155/numbers_e155.py docs/reports/data/2026-11-03-e155-int8-floor-rows > docs/reports/data/2026-11-03-e155-int8-floor-rows/readme-numbers.txt
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
    red = json.load(open(os.path.join(d, "e155.json")))
    st, R = sc["stats"], sc["rules"]
    print(f"scored on: {sc['which_reduction_scores']}; passes {sc['passes']} (primary kept {sc['primary_kept']}, relaxed {sc['relaxed_kept']}); "
          f"set aside primary {sc['set_aside_primary']} relaxed {sc['set_aside_relaxed']}; leak {sc.get('leak')}")
    print(f"runs kept {red.get('kept')}; failed {red.get('failed')}; idle invalid {red.get('idle_invalid_runs')}; idle level {red['idle_level']}")
    for k in ("N1", "N3", "N3k8", "D31", "D31_less_frozen_shared", "D31_less_session_shared", "shared_session_w", "E_op_session_pJ", "Q31k",
              "r3_over_r1_fp32", "r3_over_r1_int8", "r3k8_over_r3_fp32", "r3k8_over_r3_int8"):
        if k in st:
            print(f"{k}: {f(st[k])}  per pass {[round(x, 4) for x in st[k]['per_pass']]}")
    for k in ("e3_fp32_pJ", "e3_int8_pJ", "de3_raw_pJ", "de3c_pJ"):
        if k in st:
            print(f"{k}: {f(st[k], 1)}  per pass {[round(x, 1) for x in st[k]['per_pass']]}")
    for it, a in st.get("arms", {}).items():
        print(f"arm {it}: S {f(a['S'])}  D {f(a['D'])}  rate {a['rate']['mean'] / 1e9:.4f}e9  cpo {a['cpo']}")
    for k, v in R.items():
        print(f"rule {k}: {json.dumps(v)[:1200]}")
    print("reported:", json.dumps(sc["reported"])[:4000])
    print("cycles_per_op (reduction):", red.get("cycles_per_op"))
    print("tie drift:", red.get("tie_drift_w"), "anchors:", json.dumps(red.get("anchors"))[:800])
    for v in ("relaxed", "dipskept", "auto"):
        p = os.path.join(d, f"scored-{v}.json")
        if os.path.exists(p):
            s = json.load(open(p))
            if not s["passes"]:
                print(f"arm {v}: no passes")
                continue
            ss, rr = s["stats"], s["rules"]
            print(f"arm {v}: passes {s['passes']}; N1 {f(ss['N1'])}; N3 {f(ss['N3'])}; D31 {f(ss['D31'])}; de3c {f(ss['de3c_pJ'], 1)}; "
                  + "; ".join(f"{k} {x.get('verdict')}" for k, x in rr.items() if k != "R6" and isinstance(x, dict)))
    for pdir in sorted(glob.glob(os.path.join(d, "aifoundry1-c1", "e155", "p155*"))):
        if ".attempt-" in pdir:
            continue
        heats, n_rec, nh = {}, 0, 0
        rr = os.path.join(pdir, "runs.jsonl")
        if os.path.exists(rr):
            for line in open(rr):
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                n_rec += 1
                heats.setdefault((r.get("pos"), r.get("attempt")), r.get("heats"))
        mk = os.path.join(pdir, "marks.jsonl")
        t0 = t1 = None
        if os.path.exists(mk):
            for line in open(mk):
                try:
                    m = json.loads(line)
                except ValueError:
                    continue
                nh += m.get("kind") == "heater"
                t0 = m["t_start_ms"] if t0 is None else t0
                t1 = m["t_end_ms"]
        hs = sorted(h for h in heats.values() if h is not None)
        print(f"{os.path.basename(pdir)}: launch records {n_rec}; heats a run median {hs[len(hs) // 2] if hs else None}, max {max(hs) if hs else None}, "
              f"n {len(hs)}; heater launches {nh}; marks span {round((t1 - t0) / 1000) if t0 and t1 else None} s")


if __name__ == "__main__":
    main()
