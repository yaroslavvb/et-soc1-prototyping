#!/usr/bin/env python3
"""E132: a pipeline test of reduce_e132.py, before any E132 pass exists. E110's committed passes are relabelled onto E132's item names, so
the numbers mean nothing as E132 results; what must hold is that the reducer reproduces E110's registered reducer on the runs both read.

    python3 tools/claims-v3/e132/selftest_e132.py <E110 data dir> <E132 gen dir> <scratch dir>

The seven images E132 shares with E110 keep their names; fourteen E110 items E132 does not run stand in for E132's new ones. Checks,
pass by pass, on E110's unfiltered passes 11011-11016 at E110's own unfiltered leakage slope: S64, S128, V16, V64 and V128 on the board,
on the three rails and on the DDR die rail against E110's (e110-unfiltered.json per_pass.contrasts), and the items' minion and DDR columns.
Then that a hand-built contrast matches (E56 from its definition) and that every registered verdict key is present.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAP = {"dm_a08": "ab_0", "wl_32": "ab_1", "wl_256": "ab_2", "dp_c1": "ab_3", "vl_32": "ab_4", "vl_256": "ab_5", "dm_u1": "ab_6",
       "dm_u8": "ab_7", "dm_L2": "ab_x70", "dm_L8192": "ab_rnd", "dp_bern": "eh_64", "l2_u1": "el_64", "l2_u8": "c3_64",
       "l2_zeros": "c3_128"}
PASSES = ("p11010", "p11011", "p11012", "p11013", "p11014", "p11015", "p11016")


def main():
    e110, gen, work = sys.argv[1:4]
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    dirs = []
    for p in PASSES:
        s, d = os.path.join(e110, "passes", p), os.path.join(work, p)
        shutil.copytree(s, d)
        for fn in ("runs.jsonl", "marks.jsonl"):
            t = open(os.path.join(d, fn)).read()
            for a, b in MAP.items():
                t = t.replace('"item": "%s"' % a, '"item": "%s"' % b)
            open(os.path.join(d, fn), "w").write(t)
        dirs.append(d)
    ref = json.load(open(os.path.join(e110, "e110-unfiltered.json")))
    leak = ref["gates"]["leak_W_per_C"]
    out = os.path.join(work, "e132.json")
    subprocess.run([sys.executable, os.path.join(HERE, "reduce_e132.py")] + dirs +
                   ["--gen", gen, "--pred", os.path.join(HERE, "predictions.json"), "--out", out, "--warmup", "11010",
                    "--leak", repr(leak), "--csv", os.path.join(work, "runs.csv")], check=True)
    r = json.load(open(out))
    bad = 0
    for p in [x[1:] for x in PASSES[1:]]:
        for cn in ("S64", "S128", "V16", "V64", "V128"):
            for col in ("board", "noc", "sram", "minion", "off", "ddr_mv"):
                a_ = r["per_pass"][p]["contrasts"][col][cn]
                b_ = ref["per_pass"][p]["contrasts"][col][cn]
                ok = a_ is not None and b_ is not None and abs(a_ - b_) < 1e-9
                if not ok or col == "board":
                    print("%s pass %s %-5s %-6s %+.4f, E110's %+.4f" % ("ok " if ok else "BAD", p, cn, col, a_ or 0, b_ or 0))
                bad += 0 if ok else 1
        for it in ("dm_l08", "dm_u4", "wl_64", "vl_128", "dp_zeros"):
            for col in ("minion", "ddr_mv"):
                a_ = r["per_pass"][p]["items"][col][it]
                b_ = ref["per_pass"][p]["items"][col][it]
                ok = a_ is not None and b_ is not None and abs(a_ - b_) < 1e-9
                bad += 0 if ok else 1
                if not ok:
                    print("BAD pass %s %s %s %.4f vs %.4f" % (p, it, col, a_ or 0, b_ or 0))
        # E56 by hand from the items, the registration's formula
        I = r["per_pass"][p]["items"]["board"]
        hp = 0.5 * ((I["c3_64"] - I["wl_64"]) + (I["c3_128"] - I["wl_128"]))
        e56 = (I["eh_64"] - I["el_64"]) - 98 / 496.0 * (I["dm_a44"] - I["dm_u4"]) - 32 / 192.0 * hp
        got = r["per_pass"][p]["contrasts"]["board"]["E56"]
        ok = abs(got - e56) < 1e-9
        print("%s pass %s E56 %+.4f W, by hand %+.4f" % ("ok " if ok else "BAD", p, got, e56))
        bad += 0 if ok else 1
        # a hart-corrected rung by hand: R_4 = (ab_4 - ab_3) - (k4 - k3)/(k_x70 - k_7) (ab_x70 - ab_7)
        k = r["stream_k"]
        r4 = (I["ab_4"] - I["ab_3"]) - (k["ab_4"] - k["ab_3"]) / (k["ab_x70"] - k["ab_7"]) * (I["ab_x70"] - I["ab_7"])
        got = r["per_pass"][p]["contrasts"]["board"]["R_4"]
        ok = abs(got - r4) < 1e-9
        print("%s pass %s R_4 %+.4f W, by hand %+.4f" % ("ok " if ok else "BAD", p, got, r4))
        bad += 0 if ok else 1
    want = {"R1_tie", "R2_channel_rung", "R3_encoded_ddr", "R4_encoded_board", "R5_rail_steps", "R6_high_pins_ddr", "where"}
    have = set(r["verdicts"])
    ok = want <= have
    print("%s verdict keys %s" % ("ok " if ok else "BAD", sorted(have)))
    bad += 0 if ok else 1
    ok = r["passes_headline"] == [11011, 11012, 11013, 11014, 11015, 11016]
    print("%s headline passes %s" % ("ok " if ok else "BAD", r["passes_headline"]))
    bad += 0 if ok else 1
    print("selftest: %d bad" % bad)
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
