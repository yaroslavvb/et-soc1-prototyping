#!/usr/bin/env python3
"""E183 (Q155, the kit's dated note 1): the self-test of the reduction v2 (reduce_e183_v2.py) with the scorer (score_e183.py, unchanged),
on E180's committed data and on synthetic sessions in the box's layout (fake_card_e183.py, v1, and fake_card_e183_v2.py).

    /usr/bin/python3 -B tools/claims-v3/e183/selftest_score_e183_v2.py <scratch dir>      # prints SELFTEST-SCORE-E183-V2 <k> of <n> PASS

ON E180'S COMMITTED DATA (docs/reports/data/2026-11-06-e180-vector-add-aifoundry3/, c8a3a6ee), through reduce v2's own functions:
  A1  the launch reading on E180's six passes, launches (1, 2, 3, 4) of each one-number fadd.ps burst as a quad: 144 quads, sd sigma_q;
  A2  the anchors' reduction: D(random) - D(zeros) per pass equals E180's committed RA5 on the board, pass by pass, to 1e-9 W.
v1's TWELVE SESSIONS, scored both ways (R1-R12): each of selftest_score_e183.py's B1-B12 (its seeds, worlds, noise and cuts) is made by
  fake_card_e183.py and reduced by reduce_e183.py (v1), then made by fake_card_e183_v2.py (the same blocks, with block.json's t0_ms and
  t1_ms) and reduced by reduce_e183_v2.py --t0; both are scored by score_e183.py. The two scored files must be EQUAL: no rule v2 adds
  bites on a session v1 reads in full, so v1's committed verdicts (logs/selftest-score-e183.txt, 14 of 14) stand under v2.
THE VERIFIER'S CASES (verify-e183, Sat 7 Nov 2026):
  S1  (fault 1) a live stop in T5's process 150 (7 of its 13 launches recorded; the box's post-block check run; block.json status "stop"):
      v1 sets T5's block aside and E183-HT reads NOT SCORED; v2 reduces it: 150 of 202 processes with a value, process 150 "7 launches",
      the 51 after it "0 launches", 75 units, E183-HT scored (POSITIVE in this RESULT world), the box's check carried as box_check;
  S2  the stop fired after process 150's 13th launch: that one process "a stop fired during it", 150 of 202;
  S3  a stop at T3's first closing anchor: every one of T3's 52 processes keeps its value, the closing anchors' pair is None;
  S4  status "stop" with no stop.json: the block is set aside ("cannot be named");
  I1  (nit 6) T1's process 3 ran the S image on its F launches: v2 gives it no value ("a launch's image is not its kind's"), 51 of 52, and
      the box's check reads partial with the same fault; v1 used it (52 of 52);
  T1  (nit 8) T5's block.json t0_ms an hour before the session's T0: set aside ("before the session's T0"), E183-HT NOT SCORED;
  T2  T2's block.json without t0_ms: set aside ("no t0_ms");  T3  reduce v2 without --t0 refuses (2);
  N1  (nit 7, the registered reading) T3 cut to 12 processes (6 units, NOT SCORED): TR-N pools every reduced train's quads, T3's 36 among
      them, as E183.md section 5.2 registers ("every train's quads"): the scorer's pooled sd equals this test's own recomputation over the
      six blocks, and differs from a pool of the five scored trains alone.
The seeds are fixed; the RESULT world's noise is a quarter of sigma_q, so the words asserted are certain.
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
import e183_common as E       # noqa: E402
import e183_stats as S        # noqa: E402
import reduce_e183_v2 as RD2  # noqa: E402

E180 = os.path.join(TOP, "docs/reports/data/2026-11-06-e180-vector-add-aifoundry3")
PY = "/usr/bin/python3"
BASE_MS = 1_800_000_000_000
T0 = BASE_MS // 1000 - 600          # the synthetic session's T0: ten minutes before its blocks' first samples
results = []


def check(name, ok, what):
    results.append((name, bool(ok)))
    print(f"{name}: {'PASS' if ok else 'FAIL'} - {what}")


def run(args):
    return subprocess.run([PY, "-B"] + args, capture_output=True, text=True)


def a1():
    q = []
    for p in ("p18010", "p18011", "p18012", "p18013", "p18014", "p18015"):
        d = os.path.join(E180, "raw", "e180", p)
        tel = RD2.jl(os.path.join(d, "telemetry.jsonl"))
        runs = RD2.jl(os.path.join(d, "runs.jsonl"))
        ts, ws, _ = RD2.kept_samples(tel)
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
    ac = RD2.analyzer(TOP)
    ra5 = json.load(open(os.path.join(E180, "scored-e180.json")))["reported_v2"]["RA5_anchors"]["fadd.ps/random - zeros, D"]["x"]
    got = []
    for p in ("p18010", "p18011", "p18012", "p18013", "p18014", "p18015"):
        d = os.path.join(E180, "raw", "e180", p)
        tel, runs = RD2.jl(os.path.join(d, "telemetry.jsonl")), RD2.jl(os.path.join(d, "runs.jsonl"))
        res = ac.bursts_of(tel, runs)
        bl = res[0] if isinstance(res, tuple) else res
        by = {}
        for b in bl:
            if b["mhz_busy_all_600"]:
                by.setdefault(b["cfg"].split("/h2")[0], []).append(b["over_idle_w"])
        got.append(st.mean(by["e180/fadd.ps/random"]) - st.mean(by["e180/fadd.ps/zeros"]))
    worst = max(abs(a - b) for a, b in zip(got, ra5))
    check("A2", len(got) == 6 and worst < 1e-9, f"random - zeros per pass equals E180's RA5 on the board, worst difference {worst:.1e} W")


def make(tmp, name, fake, args):
    raw = os.path.join(tmp, name, "raw")
    shutil.rmtree(os.path.join(tmp, name), ignore_errors=True)
    r = run([os.path.join(HERE, fake), raw] + args)
    assert r.returncode == 0, (name, r.stderr[-800:])
    return raw


def reduce_score(tmp, name, raw, v2=True, t0=T0):
    os.makedirs(os.path.join(tmp, name), exist_ok=True)
    red = os.path.join(tmp, name, "reduced.json")
    if v2:
        r = run([os.path.join(HERE, "reduce_e183_v2.py"), "--raw", raw, "--t0", str(t0), "--out", red, "--root", TOP])
    else:
        r = run([os.path.join(HERE, "reduce_e183.py"), "--raw", raw, "--out", red, "--root", TOP])
    assert r.returncode == 0, (name, r.stderr[-800:])
    r = run([os.path.join(HERE, "score_e183.py"), "--reduced", red, "--out", os.path.join(tmp, name, "scored")])
    assert r.returncode == 0, (name, r.stderr[-800:])
    return json.load(open(red)), json.load(open(os.path.join(tmp, name, "scored.json")))


def blk(red, train):
    return [v for v in red["blocks"].values() if v["train"] == train][0]


def fail_t4(raw):
    d = os.path.join(raw, "e183", "p18312")
    j = json.load(open(os.path.join(d, "block.json")))
    j["status"] = "fail"
    json.dump(j, open(os.path.join(d, "block.json"), "w"))


def main():
    tmp = sys.argv[1] if len(sys.argv) > 1 else None
    if not tmp or os.path.abspath(tmp).startswith(TOP):
        print("usage: selftest_score_e183_v2.py <scratch dir outside the repository>")
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
    # v1's twelve sessions (selftest_score_e183.py B1-B12), each scored through v1's path and v2's
    v1cases = [
        ("R1", ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "11"], None),
        ("R2", ["--b", "0", "--c", str(OP), "--sigma", q4, "--seed", "12"], None),
        ("R3", ["--b", str(bb), "--c", str(cb), "--sigma", q4, "--seed", "13"], None),
        ("R4", ["--b", "0", "--c", "0", "--sigma", q4, "--seed", "14"], None),
        ("R5", ["--b", str(BL), "--c", "0", "--seed", "15"], None),
        ("R6", ["--b", str(BL), "--c", "0", "--sigma", f"{2 * sq:.6f}", "--seed", "16"], None),
        ("R7", ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "17", "--cut", "T3:12"], None),
        ("R8", ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "18", "--bad-launch", "T1:5"], None),
        ("R9", ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "19", "--flip-orientation", "T2:7"], None),
        ("R10", ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "20", "--plan", "SHORT"], None),
        ("R11", ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "21", "--override", f"T6:{6 * BL + 0.020}"], None),
        ("R12", ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "22"], fail_t4),
    ]
    for name, args, mut in v1cases:
        raw1 = make(tmp, name + "-v1", "fake_card_e183.py", args)
        raw2 = make(tmp, name + "-v2", "fake_card_e183_v2.py", args)
        if mut:
            mut(raw1)
            mut(raw2)
        _, s1 = reduce_score(tmp, name + "-v1", raw1, v2=False)
        r2, s2 = reduce_score(tmp, name + "-v2", raw2, v2=True)
        R = s2["rules"]
        check(name, s1 == s2, f"v1's B{name[1:]} scored the same through reduce v1 and reduce v2 (--t0): MECH {R['E183-MECH']['verdict']}, "
              f"HT {R['E183-HT']['sign']}, X {R['E183-X']['verdict']}, TR-N {R['E183-TR']['N']['verdict']}, set aside "
              f"{sorted(r2['set_aside'])}")
    world = ["--b", str(BL), "--c", "0", "--sigma", q4, "--seed", "31"]
    # S1: a live stop in T5's process 150
    raw = make(tmp, "s1", "fake_card_e183_v2.py", world + ["--stop", "T5:150", "--box-check"])
    red1, s1 = reduce_score(tmp, "s1-v1", raw, v2=False)
    red2, s2 = reduce_score(tmp, "s1", raw, v2=True)
    b5 = blk(red2, "T5")
    why = {p["process"]: p["why_no_value"] for p in b5["process_info"]}
    after = {why[k] for k in range(151, 202)}
    check("S1", "18315" in red1["set_aside"] and s1["rules"]["E183-HT"]["sign"] == "NOT SCORED" and b5["status"] == "stop"
          and b5["n_processes_with_value"] == 150 and why[150] == "7 launches" and after == {"0 launches"}
          and all(why[k] is None for k in range(150)) and s2["trains"]["T5"]["units"] == 75 and s2["rules"]["E183-HT"]["sign"] == "POSITIVE"
          and (b5["box_check"] or {}).get("status") in ("partial", "fail"),
          f"v1: set aside ({red1['set_aside'].get('18315', '')[:60]}...), HT {s1['rules']['E183-HT']['sign']}; v2: {b5['n_processes_with_value']} "
          f"of {b5['n_processes_planned']} with a value, process 150 '{why[150]}', 151-201 {sorted(after)}, T5 {s2['trains']['T5']['units']} units "
          f"{s2['trains']['T5']['mean']:+.5f} W, HT {s2['rules']['E183-HT']['sign']}, box check {(b5['box_check'] or {}).get('status')}")
    # S2: the stop fired after process 150's last launch
    raw = make(tmp, "s2", "fake_card_e183_v2.py", world + ["--stop", "T5:150:13"])
    red, s = reduce_score(tmp, "s2", raw)
    b5 = blk(red, "T5")
    why = {p["process"]: p["why_no_value"] for p in b5["process_info"]}
    check("S2", b5["n_processes_with_value"] == 150 and why[150] == "a stop fired during it" and s["rules"]["E183-HT"]["sign"] == "POSITIVE",
          f"the stop after process 150's 13th launch: process 150 '{why[150]}', {b5['n_processes_with_value']} of 202 with a value")
    # S3: a stop at T3's first closing anchor
    raw = make(tmp, "s3", "fake_card_e183_v2.py", world + ["--stop-anchor", "T3"])
    red, s = reduce_score(tmp, "s3", raw)
    b3 = blk(red, "T3")
    check("S3", b3["status"] == "stop" and b3["n_processes_with_value"] == 52 and b3["random_minus_zeros_close_w"] is None
          and b3["random_minus_zeros_open_w"] is not None and s["trains"]["T3"]["units"] == 26,
          f"a stop at {str(b3['stop']['where'])}: {b3['n_processes_with_value']} of 52 with a value, close pair "
          f"{b3['random_minus_zeros_close_w']}, open pair {b3['random_minus_zeros_open_w']:+.3f} W")
    # S4: status stop with no stop.json
    raw = make(tmp, "s4", "fake_card_e183_v2.py", world + ["--stop-no-json", "T5"])
    red, s = reduce_score(tmp, "s4", raw)
    check("S4", "cannot be named" in red["set_aside"].get("18315", "") and s["rules"]["E183-HT"]["sign"] == "NOT SCORED",
          f"set aside: {red['set_aside'].get('18315', '-')[:90]}")
    # I1: a wrong image in T1's process 3
    raw = make(tmp, "i1", "fake_card_e183_v2.py", world + ["--wrong-image", "T1:3", "--box-check"])
    red1, _ = reduce_score(tmp, "i1-v1", raw, v2=False)
    red2, s2 = reduce_score(tmp, "i1", raw, v2=True)
    b1v1, b1 = blk(red1, "T1"), blk(red2, "T1")
    why = {p["process"]: p["why_no_value"] for p in b1["process_info"]}
    bc = b1["box_check"] or {}
    check("I1", b1v1["n_processes_with_value"] == 52 and b1["n_processes_with_value"] == 51 and why[3] == "a launch's image is not its kind's"
          and bc.get("status") == "partial" and any("image" in f for f in bc.get("train_faults", [])) and s2["trains"]["T1"]["units"] == 25,
          f"v1 {b1v1['n_processes_with_value']} of 52; v2 {b1['n_processes_with_value']} of 52, process 3 '{why[3]}'; the box's check "
          f"{bc.get('status')}: {bc.get('train_faults')}")
    # T1: a block from an earlier session (t0_ms an hour before T0)
    raw = make(tmp, "t1", "fake_card_e183_v2.py", world + ["--stale", f"T5:{(T0 - 3600) * 1000}"])
    red, s = reduce_score(tmp, "t1", raw)
    check("T1", "before the session's T0" in red["set_aside"].get("18315", "") and len(red["blocks"]) == 5
          and s["rules"]["E183-HT"]["sign"] == "NOT SCORED" and s["rules"]["E183-MECH"]["verdict"] == "RESULT",
          f"set aside: {red['set_aside'].get('18315', '-')[:100]}; {len(red['blocks'])} blocks reduced; MECH {s['rules']['E183-MECH']['verdict']}")
    # T2: no t0_ms;  T3: no --t0
    raw = make(tmp, "t2", "fake_card_e183_v2.py", world + ["--no-t0", "T2"])
    red, s = reduce_score(tmp, "t2", raw)
    check("T2", "no t0_ms" in red["set_aside"].get("18314", "") and s["rules"]["E183-C"]["from"] == ["T4"],
          f"set aside: {red['set_aside'].get('18314', '-')[:90]}; c from {s['rules']['E183-C']['from']}")
    r = run([os.path.join(HERE, "reduce_e183_v2.py"), "--raw", raw, "--out", os.path.join(tmp, "t3.json")])
    check("T3", r.returncode == 2 and "--t0" in r.stderr, f"reduce v2 without --t0: rc {r.returncode} ({r.stderr.strip().splitlines()[-1][:90]})")
    # N1: TR-N pools every train's quads, a NOT SCORED train's among them (E183.md section 5.2)
    raw = make(tmp, "n1", "fake_card_e183_v2.py", world + ["--cut", "T3:12"])
    red, s = reduce_score(tmp, "n1", raw)

    def pooled(blocks):
        ss, n, g = 0.0, 0, 0
        for b in blocks:
            for ori in ("SFFS", "FSSF"):
                q = [x for o, qs in b["processes"] if o == ori for x in qs]
                if len(q) >= 2:
                    m = st.mean(q)
                    ss += sum((x - m) ** 2 for x in q)
                    n += len(q)
                    g += 1
        return math.sqrt(ss / (n - g)), n
    every, n_every = pooled(red["blocks"].values())
    scored5, n5 = pooled([b for b in red["blocks"].values() if b["train"] != "T3"])
    got = s["rules"]["E183-TR"]["N"]["pooled_quad_sd_w"]
    nq3 = sum(len(q) for _, q in blk(red, "T3")["processes"])
    check("N1", s["trains"]["T3"].get("lo") is None and abs(got - every) < 1e-12 and abs(got - scored5) > 1e-9 and nq3 == 36,
          f"T3 NOT SCORED ({s['trains']['T3'].get('units')} units); TR-N's pooled sd {got:.6f} W = every train's {every:.6f} ({n_every} "
          f"quads, T3's {nq3} among them), not the five scored trains' {scored5:.6f} ({n5})")
    k = sum(1 for _, ok in results if ok)
    print(f"SELFTEST-SCORE-E183-V2 {k} of {len(results)} {'PASS' if k == len(results) else 'FAIL'}")
    sys.exit(0 if k == len(results) else 1)


if __name__ == "__main__":
    main()
