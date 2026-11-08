#!/usr/bin/env python3
"""E183 (Q155, the kit): the reduction's and the scorer's self-test, on E180's committed data and on synthetic sessions in the box's layout.

    /usr/bin/python3 -B tools/claims-v3/e183/selftest_score_e183.py <scratch dir>      # prints SELFTEST-SCORE-E183 <k> of <n> PASS (exit 0)

ON E180'S COMMITTED DATA (docs/reports/data/2026-11-06-e180-vector-add-aifoundry3/, c8a3a6ee):
  A1  the reduction's launch reading (reduce_e183.kept_samples, then e182_stats.launch_reading) on E180's six passes, launches (1, 2, 3, 4)
      of each one-number fadd.ps burst as a quad: 144 quads whose sd is noise-e183.json's sigma_q (0.06249 W), to its rounding;
  A2  the anchors' reduction (analyze_catalogue.bursts_of, as reduce_e183 calls it) on E180's six passes: D(random) - D(zeros) per pass
      equals E180's committed RA5 on the board (scored-e180.json > reported_v2 > RA5_anchors), pass by pass, to 1e-9 W.
ON SYNTHETIC SESSIONS (fake_card_e183.py), each reduced and scored by the kit's own reduce_e183.py and score_e183.py:
  B1  the RESULT world (b at the blind price, c = 0; noise a quarter of sigma_q, so the words are certain): MECH RESULT, b PASS against
      BLIND and AGREES with E180-L, HT POSITIVE and PASS against BLIND, X and J CONSISTENT, the owner's sentence measured;
  B2  the OPERAND world: MECH OPERAND, c PASS against OPER, b DIFFERS LOW from E180-L, the owner's sentence not measured;
  B3  the BOTH world (E180-O's b and c): MECH BOTH;  B4  no difference: MECH NEITHER, HT NOT RESOLVED;
  B5  the RESULT world at sigma_q itself: b within 4 se of its truth, TR-N AS FORECAST, TR-H AS PLANNED;
  B6  at twice sigma_q: TR-N's ratio within 10% of 2 (WORSE or FAILS), TR-H WORSE or FAILS;
  B7  T3 cut to 12 processes (6 units): T3 NOT SCORED, b from T1 alone, MECH still scored;
  B8  a launch not ok in T1's process 5: that process gives no value, T1 is scored on the rest;
  B9  T2's process 7 written with the other orientation: no value for it;
  B10 the SHORT plan (T5 and T6 not run): HT and X NOT SCORED, MECH scored on T1-T4;
  B11 T6 0.020 W above 6 b - c: E183-X INCONSISTENT;
  B12 T4's block set aside (its block.json says fail): c from T2 alone, the set-aside named.
The seeds are fixed. Where c's truth is 0, its interval excludes 0 by chance 5% of the time at any noise (the registered NULL power, 0.95),
so B1-B4 assert the mechanism word for their seeds, and B7, B10 and B12, which test a train's absence, assert only that the word is scored.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import math
import os
import shutil
import statistics as st
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e183_common as E   # noqa: E402
import e183_stats as S    # noqa: E402
import reduce_e183 as RD  # noqa: E402

E180 = os.path.join(TOP, "docs/reports/data/2026-11-06-e180-vector-add-aifoundry3")
PY = "/usr/bin/python3"
results = []


def check(name, ok, what):
    results.append((name, bool(ok)))
    print(f"{name}: {'PASS' if ok else 'FAIL'} - {what}")


def a1():
    q = []
    for p in ("p18010", "p18011", "p18012", "p18013", "p18014", "p18015"):
        d = os.path.join(E180, "raw", "e180", p)
        tel = RD.jl(os.path.join(d, "telemetry.jsonl"))
        runs = RD.jl(os.path.join(d, "runs.jsonl"))
        ts, ws, _ = RD.kept_samples(tel)
        by = {}
        for r in runs:
            if r.get("ok", True):
                by.setdefault(r["cfg"], []).append(r)
        for cfg, L in by.items():
            kind = L[0]["kind"]
            if not kind.startswith("fadd.ps/") or kind in ("fadd.ps/zeros", "fadd.ps/random"):
                continue
            L.sort(key=lambda r: r["t_start_ms"])
            rd = {i: S.launch_reading(ts, ws, r["t_start_ms"], r["t_end_ms"]) for i, r in enumerate(L)}
            if all(rd.get(i) is not None for i in (1, 2, 3, 4)):
                q.append((rd[2] + rd[3] - rd[1] - rd[4]) / 2)
    want = json.load(open(os.path.join(HERE, "noise", "noise-e183.json")))["sigma_q_w"]
    sd = st.stdev(q)
    check("A1", len(q) == 144 and round(sd, 5) == want, f"{len(q)} quads, sd {sd:.6f} W against noise-e183.json's {want}")


def a2():
    ac = RD.analyzer(TOP)
    ra5 = json.load(open(os.path.join(E180, "scored-e180.json")))["reported_v2"]["RA5_anchors"]["fadd.ps/random - zeros, D"]["x"]
    got = []
    for p in ("p18010", "p18011", "p18012", "p18013", "p18014", "p18015"):
        d = os.path.join(E180, "raw", "e180", p)
        tel, runs = RD.jl(os.path.join(d, "telemetry.jsonl")), RD.jl(os.path.join(d, "runs.jsonl"))
        res = ac.bursts_of(tel, runs)
        bl = res[0] if isinstance(res, tuple) else res
        by = {}
        for b in bl:
            if b["mhz_busy_all_600"]:
                by.setdefault(b["cfg"].split("/h2")[0], []).append(b["over_idle_w"])
        got.append(st.mean(by["e180/fadd.ps/random"]) - st.mean(by["e180/fadd.ps/zeros"]))
    worst = max(abs(a - b) for a, b in zip(got, ra5))
    check("A2", len(got) == 6 and worst < 1e-9, f"random - zeros per pass equals E180's RA5 on the board, worst difference {worst:.1e} W")


def session(tmp, name, fake_args, mutate=None):
    raw = os.path.join(tmp, name, "raw")
    shutil.rmtree(os.path.join(tmp, name), ignore_errors=True)
    subprocess.run([PY, "-B", os.path.join(HERE, "fake_card_e183.py"), raw] + fake_args, check=True, capture_output=True, text=True)
    if mutate:
        mutate(raw)
    red = os.path.join(tmp, name, "reduced.json")
    subprocess.run([PY, "-B", os.path.join(HERE, "reduce_e183.py"), "--raw", raw, "--out", red, "--root", TOP], check=True,
                   capture_output=True, text=True)
    subprocess.run([PY, "-B", os.path.join(HERE, "score_e183.py"), "--reduced", red, "--out", os.path.join(tmp, name, "scored")],
                   check=True, capture_output=True, text=True)
    return json.load(open(red)), json.load(open(os.path.join(tmp, name, "scored.json")))


def main():
    tmp = sys.argv[1] if len(sys.argv) > 1 else None
    if not tmp or os.path.abspath(tmp).startswith(TOP):
        print("usage: selftest_score_e183.py <scratch dir outside the repository>")
        sys.exit(2)
    os.makedirs(tmp, exist_ok=True)
    fc = E.forecast()
    BL = fc["prices"]["BLIND"]["b_W_per_result_bit"]
    OP = fc["prices"]["OPER"]["c_W_per_operand_bit"]
    bb, cb = fc["prices"]["BOTH"]["b_W_per_result_bit"], fc["prices"]["BOTH"]["c_W_per_operand_bit"]
    sq = E.plan()["sigma_q_w"]
    q4 = f"{sq / 4:.6f}"
    a1()
    a2()
    _, s = session(tmp, "b1", ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "11"])
    R = s["rules"]
    check("B1", R["E183-MECH"]["verdict"] == "RESULT" and R["E183-B"]["size_BLIND"] == "PASS" and R["E183-B"]["repeat_E180L"] == "AGREES"
          and R["E183-HT"]["sign"] == "POSITIVE" and R["E183-HT"]["size"]["BLIND"] == "PASS" and R["E183-X"]["verdict"] == "CONSISTENT"
          and R["E183-J"]["R"] == "CONSISTENT" and R["E183-J"]["O"] == "CONSISTENT" and s["owners_sentence_measured"],
          f"RESULT world: MECH {R['E183-MECH']['verdict']}, b {R['E183-B']['b']['mean']:+.6f} {R['E183-B']['size_BLIND']}, HT "
          f"{R['E183-HT']['sign']}, X {R['E183-X']['verdict']}, owner's sentence {s['owners_sentence_measured']}")
    _, s = session(tmp, "b2", ["--b", "0", "--c", str(OP), "--sigma", q4, "--seed", "12"])
    R = s["rules"]
    check("B2", R["E183-MECH"]["verdict"] == "OPERAND" and R["E183-C"]["size_OPER"] == "PASS" and R["E183-B"]["repeat_E180L"] == "DIFFERS LOW"
          and not s["owners_sentence_measured"], f"OPERAND world: MECH {R['E183-MECH']['verdict']}, c {R['E183-C']['size_OPER']}")
    _, s = session(tmp, "b3", ["--b", str(bb), "--c", str(cb), "--sigma", q4, "--seed", "13"])
    check("B3", s["rules"]["E183-MECH"]["verdict"] == "BOTH", f"BOTH world: MECH {s['rules']['E183-MECH']['verdict']}")
    _, s = session(tmp, "b4", ["--b", "0", "--c", "0", "--sigma", q4, "--seed", "14"])
    check("B4", s["rules"]["E183-MECH"]["verdict"] == "NEITHER" and s["rules"]["E183-HT"]["sign"] == "NOT RESOLVED",
          f"no difference: MECH {s['rules']['E183-MECH']['verdict']}, HT {s['rules']['E183-HT']['sign']}")
    _, s = session(tmp, "b5", ["--b", str(BL), "--c", "0", "--seed", "15"])
    b = s["rules"]["E183-B"]["b"]
    tr = s["rules"]["E183-TR"]
    check("B5", abs(b["mean"] - BL) < 4 * b["se"] and tr["N"]["verdict"] == "AS FORECAST" and tr["H"]["verdict"] == "AS PLANNED",
          f"sigma_q: b {b['mean']:+.6f} (se {b['se']:.6f}), TR-N {tr['N']['verdict']} ({tr['N']['ratio']:.3f}), TR-H {tr['H']['verdict']}")
    _, s = session(tmp, "b6", ["--b", str(BL), "--c", "0", "--sigma", f"{2 * sq:.6f}", "--seed", "16"])
    tr = s["rules"]["E183-TR"]
    check("B6", 1.8 <= tr["N"]["ratio"] <= 2.2 and tr["N"]["verdict"] in ("WORSE", "FAILS") and tr["H"]["verdict"] in ("WORSE", "FAILS"),
          f"twice sigma_q: TR-N {tr['N']['verdict']} ({tr['N']['ratio']:.3f}), TR-H {tr['H']['verdict']}")
    _, s = session(tmp, "b7", ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "17", "--cut", "T3:12"])
    check("B7", s["trains"]["T3"].get("lo") is None and s["rules"]["E183-B"]["from"] == ["T1"] and s["rules"]["E183-MECH"]["verdict"] != "NOT SCORED",
          f"T3 cut: T3 units {s['trains']['T3'].get('units')}, b from {s['rules']['E183-B']['from']}, MECH {s['rules']['E183-MECH']['verdict']}")
    red, s = session(tmp, "b8", ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "18", "--bad-launch", "T1:5"])
    t1 = [v for v in red["blocks"].values() if v["train"] == "T1"][0]
    why = [p["why_no_value"] for p in t1["process_info"] if p["process"] == 5]
    check("B8", t1["n_processes_with_value"] == 51 and why == ["a launch record not ok"] and s["trains"]["T1"]["units"] == 25,
          f"a bad launch: T1 {t1['n_processes_with_value']} of 52 processes with a value ({why}), {s['trains']['T1']['units']} units")
    red, s = session(tmp, "b9", ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "19", "--flip-orientation", "T2:7"])
    t2 = [v for v in red["blocks"].values() if v["train"] == "T2"][0]
    why = [p["why_no_value"] for p in t2["process_info"] if p["process"] == 7]
    check("B9", t2["n_processes_with_value"] == 51 and why and "orientation" in why[0],
          f"an orientation mismatch: T2 {t2['n_processes_with_value']} of 52 ({why})")
    _, s = session(tmp, "b10", ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "20", "--plan", "SHORT"])
    R = s["rules"]
    check("B10", R["E183-HT"]["sign"] == "NOT SCORED" and R["E183-X"]["verdict"] == "NOT SCORED" and R["E183-MECH"]["verdict"] != "NOT SCORED"
          and R["E183-B"]["from"] == ["T1", "T3"] and R["E183-C"]["from"] == ["T2", "T4"],
          f"SHORT: HT {R['E183-HT']['sign']}, X {R['E183-X']['verdict']}, MECH {R['E183-MECH']['verdict']}")
    _, s = session(tmp, "b11", ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "21", "--override", f"T6:{6 * BL + 0.020}"])
    check("B11", s["rules"]["E183-X"]["verdict"] == "INCONSISTENT", f"T6 off the sum rule: X {s['rules']['E183-X']['verdict']}")

    def fail_t4(raw):
        d = os.path.join(raw, "e183", "p18312")
        j = json.load(open(os.path.join(d, "block.json")))
        j["status"] = "fail"
        json.dump(j, open(os.path.join(d, "block.json"), "w"))

    red, s = session(tmp, "b12", ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "22"], mutate=fail_t4)
    check("B12", "18312" in red["set_aside"] and s["rules"]["E183-C"]["from"] == ["T2"] and s["rules"]["E183-MECH"]["verdict"] != "NOT SCORED",
          f"T4's block set aside ({red['set_aside'].get('18312', '')[:40]}): c from {s['rules']['E183-C']['from']}")
    k = sum(1 for _, ok in results if ok)
    print(f"SELFTEST-SCORE-E183 {k} of {len(results)} {'PASS' if k == len(results) else 'FAIL'}")
    sys.exit(0 if k == len(results) else 1)


if __name__ == "__main__":
    main()
