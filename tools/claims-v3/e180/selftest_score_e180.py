#!/usr/bin/env python3
"""The self-test of E180's reduction and scorer, on synthetic sessions (no card data exists).

    python3 tools/claims-v3/e180/selftest_score_e180.py [--root .] > logs/selftest-score-e180.txt   # exit 0 if every case passes

S1-S8 build reduced sessions directly (six passes of every kind's D, from a stated truth plus seeded noise of 0.02 W, small
so the verdicts are certain) and score them; S9-S10 build raw pass directories (10 Hz telemetry with idle brackets, runs in
the enercat host's ENERCAT form) and check that reduce_e180.py, through analyze_catalogue.bursts_of unchanged, gives each
kind's D back. The truths: P, C, E, F and A as forecast-e180.json gives them, an operand-bit term, fadd.pi's write-back
returning to zero, no difference.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import os
import random
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e180 as sc  # noqa: E402

PASSES = [str(p) for p in (18010, 18011, 18012, 18013, 18014, 18015)]


def session(fc, truth, card="aifoundry3", sigma=0.02, seed=1, passes=PASSES, drop=None):
    rng = random.Random(seed)
    K = fc["kinds"]
    red = {"card": card, "passes": {}, "set_aside": {}}
    for p in passes:
        D = {}
        runs = {}
        for nm in K:
            v = 26.0 + truth(nm, card) + rng.gauss(0, sigma)
            D[nm] = v
            runs[nm] = [{"w": v, "ops_per_s": 4.58e11}]
        if drop and p == drop[0]:
            D.pop(drop[1])
            runs.pop(drop[1])
            red["set_aside"][p] = {"why": f"1 kinds with no kept burst: {drop[1]}"}
            continue
        red["passes"][p] = {"D": D, "runs": runs}
    return red


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    a = ap.parse_args()
    fc = json.load(open(os.path.join(HERE, "forecast-e180.json")))
    K = fc["kinds"]
    results = []

    def case(name, cond, detail):
        results.append(cond)
        print(f"{name}: {'PASS' if cond else 'FAIL'} - {detail}")

    def arm(a_):
        return lambda nm, card: K[nm]["W"][card][a_]

    s = sc.score(session(fc, arm("P")), fc, "aifoundry3")
    r = s["rules"]
    case("S1 truth P", r["E180-H"]["sign"] == "POSITIVE" and r["E180-H"]["size"]["P"] == "PASS" and r["E180-L"]["arms_inside"] == ["P"]
         and r["E180-O"]["verdict"] == "NULL" and r["E180-R"]["verdict"] == "PASS" and r["E180-E"]["groups"]["2"]["verdict"] == "PASS"
         and r["E180-E"]["groups"]["3"]["verdict"] == "PASS" and r["E180-I"]["verdict"] == "NULL" and r["E180-X"]["sign"] == "POSITIVE"
         and r["E180-A"]["sign"] == "POSITIVE" and r["E180-A"]["size"]["P"] == "PASS" and s["owners_sentence_measured"],
         "H " + r["E180-H"]["verdict"] + "; L " + r["E180-L"]["verdict"] + "; O " + r["E180-O"]["verdict"] + "; R " +
         r["E180-R"]["verdict"] + f" (rho {r['E180-R']['rho']:.3f}); E " + r["E180-E"]["verdict"] + "; I " + r["E180-I"]["verdict"] +
         "; X " + r["E180-X"]["verdict"] + "; A " + r["E180-A"]["verdict"] + f"; sentence {s['owners_sentence_measured']}")
    s = sc.score(session(fc, arm("C")), fc, "aifoundry3")
    r = s["rules"]
    case("S2 truth C", r["E180-L"]["arms_inside"] == ["C"] and r["E180-L"]["size"]["P"] == "FAIL LOW" and
         r["E180-H"]["sign"] == "POSITIVE" and r["E180-H"]["size"]["P"] == "FAIL LOW" and not s["owners_sentence_measured"],
         "L " + r["E180-L"]["verdict"] + "; H " + r["E180-H"]["verdict"])
    for a_ in ("E", "F", "A"):
        s = sc.score(session(fc, arm(a_)), fc, "aifoundry3")
        r = s["rules"]
        case(f"S3 truth {a_}", r["E180-L"]["arms_inside"] == [a_] and r["E180-L"]["size"]["P"] == "FAIL HIGH",
             "L " + r["E180-L"]["verdict"] + "; H " + r["E180-H"]["verdict"] + "; A " + r["E180-A"]["verdict"])
    op = lambda nm, card: K[nm]["W"][card]["P"] + (0.05 * K[nm]["operand_popcount"] if K[nm]["mode"] == "fadd.ps" and K[nm]["operand_popcount"] else 0.0)
    s = sc.score(session(fc, op), fc, "aifoundry3")
    r = s["rules"]
    case("S4 an operand-bit term (+0.05 W a bit)", r["E180-O"]["verdict"] == "POSITIVE" and not s["owners_sentence_measured"],
         "O " + r["E180-O"]["verdict"] + f" (c {r['E180-O']['mean']:+.4f} W a bit)")
    rz = lambda nm, card: (0.1649 * K[nm]["result_popcount"] if K[nm]["mode"] == "fadd.pi" and K[nm]["result_popcount"] else
                           K[nm]["W"][card]["P"])
    s = sc.score(session(fc, rz), fc, "aifoundry3")
    r = s["rules"]
    case("S5 fadd.pi's write-back returning to zero", r["E180-I"]["verdict"] == "POSITIVE" and r["E180-X"]["sign"] != "POSITIVE",
         "I " + r["E180-I"]["verdict"] + f" (mean {r['E180-I']['mean']:+.3f} W); X " + r["E180-X"]["verdict"])
    null = lambda nm, card: 0.0
    s = sc.score(session(fc, null), fc, "aifoundry3")
    r = s["rules"]
    case("S6 no difference", r["E180-H"]["sign"] == "NOT RESOLVED" and r["E180-L"]["size"]["P"] == "FAIL HIGH" and
         r["E180-R"]["verdict"] == "FAIL" and r["E180-A"]["sign"] == "NOT RESOLVED",
         "H " + r["E180-H"]["verdict"] + "; L " + r["E180-L"]["verdict"] + "; R " + r["E180-R"]["verdict"] + f" (rho {r['E180-R']['rho']:.3f})")
    s = sc.score(session(fc, arm("P"), passes=PASSES[:1]), fc, "aifoundry3")
    case("S7 one kept pass", all(v["verdict"] == "NOT SCORED" for v in s["rules"].values()), f"{len(s['rules'])} rules NOT SCORED")
    s = sc.score(session(fc, arm("P"), card="aifoundry1-c1", drop=("18012", "fadd.ps/f_7")), fc, "aifoundry1-c1")
    r = s["rules"]
    case("S8 card 1's forecasts, one pass set aside", s["n"] == 5 and "18012" in s["set_aside"] and r["E180-H"]["size"]["P"] == "PASS"
         and r["E180-L"]["arms_inside"] == ["P"] and abs(r["E180-L"]["forecast"]["P"] - fc["ladder"]["slope_W_per_bit"]["P"]) > 1e-3,
         f"n {s['n']}, set aside {list(s['set_aside'])}; H {r['E180-H']['verdict']}; L {r['E180-L']['verdict']}"
         f" (card 1's own P slope {r['E180-L']['forecast']['P']:.5f} W a bit against aifoundry3's {fc['ladder']['slope_W_per_bit']['P']:.5f})")
    # S9-S10: raw pass directories through reduce_e180.py and analyze_catalogue.bursts_of
    plan = json.load(open(os.path.join(HERE, "plan-e180.json")))
    cfgs = json.load(open(os.path.join(HERE, "cfgs-e180.json")))
    kind = {c["cfg"]: c["kind"] for c in cfgs["cfgs"]}
    with tempfile.TemporaryDirectory() as t:
        data = os.path.join(t, "e180")
        truthW = {nm: K[nm]["W"]["aifoundry3"]["P"] + 10.0 for nm in K}
        rng = random.Random(7)
        for p in ("18010", "18011"):
            d = os.path.join(data, f"p{p}")
            os.makedirs(d)
            tel, runs = [], []
            tms = 1_800_000_000_000
            idle = 26.0

            def sample(w):
                nonlocal tms
                tel.append({"t_ms": tms, "board_w": w + rng.gauss(0, 0.05), "temp_c": {"minshire": [58.0]},
                            "mhz": {"minion": 600}, "sp": {"minion_w": [8.0, 8.0, 8.0], "sram_w": [2.3, 2.3, 2.3],
                                                            "noc_w": [2.5, 2.5, 2.5]}, "took_ms": 22})
                tms += 100
            for _ in range(100):
                sample(idle)
            for name in plan["order"][p]:
                for _ in range(45):
                    sample(idle)
                t0 = tms
                for _ in range(30):
                    sample(idle + truthW[kind[name]])
                for L in range(7):
                    runs.append({"host": "aifoundry3", "pass": int(p), "cfg": name, "kind": kind[name], "pattern": "x",
                                 "unit": "instruction", "operands": "file", "harts": 2, "scp": False, "participants": 2048,
                                 "shires": 32, "t_start_ms": t0 + L * 400, "t_end_ms": t0 + L * 400 + 399, "ops": 10 ** 11,
                                 "bytes": 0, "cycles_max": 240000000, "ops_per_cycle_per_hart": 0.373, "wall_s": 0.4})
            for _ in range(60):
                sample(idle)
            with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "wt") as f:
                f.write("".join(json.dumps(x) + "\n" for x in tel))
            with gzip.open(os.path.join(d, "runs.jsonl.gz"), "wt") as f:
                f.write("".join(json.dumps(x) + "\n" for x in runs))
            json.dump({"status": "ok"}, open(os.path.join(d, "block.json"), "w"))
        out = os.path.join(t, "reduced.json")
        r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "reduce_e180.py"), "--data", data, "--out", out,
                            "--root", a.root], capture_output=True, text=True)
        ok = r.returncode == 0 and os.path.exists(out)
        red = json.load(open(out)) if ok else {"passes": {}}
        errs = []
        for p, rec in red["passes"].items():
            z = rec["D"]["fadd.ps/zeros"]
            for nm, v in rec["D"].items():
                zz = rec["D"][nm.split("/")[0] + "/zeros"]
                errs.append(abs((v - zz) - (truthW[nm] - truthW[nm.split("/")[0] + "/zeros"])))
        # the synthetic telemetry carries 0.05 W of noise a sample, so one D (a burst against its zeros) is good to about
        # 0.017 W: the mean error must be under 0.02 W and the largest under 0.08 W (5 sd)
        mean_err = sum(errs) / len(errs) if errs else float("nan")
        case("S9 raw passes through reduce_e180 and bursts_of", ok and len(red["passes"]) == 2 and errs and max(errs) < 0.08
             and mean_err < 0.02,
             f"{len(red['passes'])} kept passes; mean |D error| {mean_err:.4f} W, the largest {max(errs) if errs else float('nan'):.4f} W over "
             f"{len(errs)} kind-passes; {r.stdout.strip()[-120:]} {r.stderr.strip()[-300:]}")
        s = sc.score(red, fc, "aifoundry3") if ok else {"rules": {}}
        case("S10 the scorer on the reduced raw passes", ok and s["rules"].get("E180-L", {}).get("arms_inside") == ["P"],
             "L " + s["rules"].get("E180-L", {}).get("verdict", "?") + "; H " + s["rules"].get("E180-H", {}).get("verdict", "?"))
    print(f"SELFTEST {'PASS' if all(results) else 'FAIL'}: {sum(results)} of {len(results)}")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
