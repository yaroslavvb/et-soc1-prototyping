#!/usr/bin/env python3
"""E110: a pipeline test of reduce_e110.py, before any E110 pass exists. E99's committed passes are relabelled onto E110's item names, so
the numbers mean nothing as E110 results; what must hold is that the reducer reproduces E99's registered reducer on the runs both read.

    python3 tools/claims-v3/e110/selftest_e110.py <E99 data dir> <E110 gen dir> <scratch dir>

Checks, pass by pass, on E99's unfiltered passes 9911-9915 at E99's own unfiltered leakage slope: S16, Sc1, V16, tie18 and D against E99's
t_raw, half, t_both, tie18 and D (dm-unfiltered.json per_pass.contrasts_W), and the minion column against E99's rail_W. Then that every
registered verdict key is present.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = {"dm_r08": "wl_32", "dm_r26": "wl_64", "dm_r44": "wl_128", "dm_u2": "wl_256", "dm_a26": "vl_32", "dm_a35": "vl_64",
       "dm_u5": "vl_128", "dm_u7": "vl_256", "dm_w1": "l2_zeros", "dm_L1": "l2_u1", "dm_L3": "l2_u8"}
PASSES = ("p9911", "p9912", "p9913", "p9914", "p9915")


def main():
    e99, gen, work = sys.argv[1:4]
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    dirs = []
    for p in PASSES:
        s, d = os.path.join(e99, "passes", p), os.path.join(work, p)
        shutil.copytree(s, d)
        for fn in ("runs.jsonl", "marks.jsonl"):
            t = open(os.path.join(d, fn)).read()
            for a, b in MAP.items():
                t = t.replace('"item": "%s"' % a, '"item": "%s"' % b)
            open(os.path.join(d, fn), "w").write(t)
        dirs.append(d)
    ref = json.load(open(os.path.join(e99, "dm-unfiltered.json")))
    leak = ref["gates"]["leak_W_per_C"]
    out = os.path.join(work, "e110.json")
    subprocess.run([sys.executable, os.path.join(HERE, "reduce_e110.py")] + dirs +
                   ["--gen", gen, "--pred", os.path.join(HERE, "predictions.json"), "--out", out, "--warmup", "9910",
                    "--leak", repr(leak), "--csv", os.path.join(work, "runs.csv")], check=True)
    r = json.load(open(out))
    bad = 0
    for p in [x[1:] for x in PASSES]:
        for mine, theirs in (("S16", "t_raw"), ("Sc1", "half"), ("V16", "t_both"), ("tie18", "tie18"), ("D", "D")):
            a_ = r["per_pass"][p]["contrasts"]["board"][mine]
            b_ = ref["per_pass"][p]["contrasts_W"][theirs]
            ok = a_ is not None and b_ is not None and abs(a_ - b_) < 1e-9
            print("%s pass %s %-5s %+.4f W, E99's %-6s %+.4f W" % ("ok " if ok else "BAD", p, mine, a_ or 0, theirs, b_ or 0))
            bad += 0 if ok else 1
        for it in ("dm_l08", "dm_u4", "dp_c1", "dp_zeros"):
            a_ = r["per_pass"][p]["items"]["minion"][it]
            b_ = ref["per_pass"][p]["rail_W"][it]
            ok = a_ is not None and b_ is not None and abs(a_ - b_) < 1e-9
            print("%s pass %s minion %-8s %.4f W, E99's rail_W %.4f W" % ("ok " if ok else "BAD", p, it, a_ or 0, b_ or 0))
            bad += 0 if ok else 1
    want = {"R1_tie", "R2_raw_width", "R3_raw_or_encoded", "R4_half_line", "R5_ddr_die_rail", "R6_one_off_rail", "where",
            "prices_pJ_per_toggled_bit", "models_rms_W"}
    have = set(r["verdicts"])
    ok = want <= have
    print("%s verdict keys %s" % ("ok " if ok else "BAD", sorted(have)))
    bad += 0 if ok else 1
    print("selftest: %d bad" % bad)
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
