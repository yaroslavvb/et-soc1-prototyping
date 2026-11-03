#!/usr/bin/env python3
"""E142, POST HOC (written Mon 2 Nov 2026 ~21:42 PST, after the registered scoring was read; never a verdict). Standard library only.

The registered reported arm "heat at the measured run length" reads each tile's run length as fit_m6.heat_rows does, (the next run's
prev_end_ms - this run's t0_ms), the median over the session's runs. For a low-power tile the next device process is often a heater
launch (the die falls below the launch band after a cool int8 run), so that difference spans the run AND the heater: three int8 tiles
read 7.1-7.2 s. M7's own heat rows leave such items out (fit_m6 HEAT_TRUN_MAX, 5.0 s). This script gives two labelled views of the same
arm: (a) each run's own process time from marks.jsonl (t_end_ms - t_start_ms of its "run" mark), the median per tile over kept passes;
(b) the registered formula with tiles whose median exceeds 5.0 s left out (M7's row rule). Both use the frozen prediction plus H2's ST
term, ST x S_M7 x (T_run - 4.5), ST = -0.1548 C/W/s on card 1 (predictions-e142.json > model.heat_coef_card1).

    python3 tools/claims-v3/e142/posthoc_e142.py <data dir>     # writes <data dir>/posthoc/runlength-posthoc.json
SPDX-License-Identifier: Apache-2.0"""
import glob
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e142 as S  # noqa: E402


def main():
    d = sys.argv[1]
    reg = json.load(open(os.path.join(HERE, "predictions-e142.json")))
    res = json.load(open(os.path.join(d, "e142.json")))
    kept = {str(p) for p in res["passes"]}
    dur = {}
    for m in glob.glob(os.path.join(d, "aifoundry1-c1", "e142", "p142*", "marks.jsonl")):
        p = os.path.basename(os.path.dirname(m))[1:]
        if p not in kept:
            continue
        for line in open(m):
            x = json.loads(line)
            if x.get("kind") == "run" and x.get("block", -1) >= 0:
                dur.setdefault(x["item"], []).append((x["t_end_ms"] - x["t_start_ms"]) / 1000.0)
    t_marks = {k: statistics.median(v) for k, v in dur.items()}
    t_reg = S.run_lengths(os.path.join(d, "runs.csv"))
    mT, _ = S.measured(res, sorted(reg["tiles"]), "dT_win", 2)
    p1 = reg["sets"]["priority1_by_format"]
    cov = reg["sets"]["coverage_tiles"]
    out = {"_note": "POST HOC, labelled; never a verdict (README, Post hoc)", "views": {}}
    for name, tr in (("a_run_mark_duration", t_marks),
                     ("b_registered_formula_items_over_5s_left_out", {k: v for k, v in t_reg.items() if v <= 5.0})):
        rows = S.rows_for(reg, mT, "heat", "M7", tr)
        rows = {t: r for t, r in rows.items() if t in tr}
        v = {"T_run_median_s": {f: statistics.median([tr[t] for t in reg["tiles"] if reg["tiles"][t]["type"] == f and t in tr])
                                for f in ("fp32", "fp16", "int8")},
             "rms_c": {f: S.rms([rows[t]["error"] for t in p1[f] if t in rows and rows[t]["error"] is not None]) for f in ("fp32", "fp16", "int8")},
             "bias_c": {f: S.mean([rows[t]["error"] for t in p1[f] if t in rows and rows[t]["error"] is not None]) for f in ("fp32", "fp16", "int8")},
             "coverage": S.coverage(rows, cov, name), "tiles_left_out": sorted(t for t in reg["tiles"] if t not in tr)}
        out["views"][name] = v
    out["registered_formula_T_run_s"] = {k: round(v, 3) for k, v in sorted(t_reg.items()) if k in reg["tiles"]}
    out["run_mark_T_run_s"] = {k: round(v, 3) for k, v in sorted(t_marks.items()) if k in reg["tiles"]}
    os.makedirs(os.path.join(d, "posthoc"), exist_ok=True)
    json.dump(out, open(os.path.join(d, "posthoc", "runlength-posthoc.json"), "w"), indent=1, default=lambda o: None)
    for n, v in out["views"].items():
        print(n, json.dumps({k: v[k] for k in ("T_run_median_s", "rms_c", "bias_c", "tiles_left_out")}, default=str),
              "coverage", v["coverage"].get("inside"), "of", v["coverage"].get("n"), v["coverage"].get("outside"))


if __name__ == "__main__":
    main()
