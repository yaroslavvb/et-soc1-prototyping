#!/usr/bin/env python3
"""E145's desk self-test (Q138), run on the Intel before the freeze is committed; its output is selftest-e145.txt.

  S1  the scorer on card 0's committed sessions, each with its own pass numbers: E138's (9 B blocks) must give back E138's registered
      rail numbers (+35.9 [+30.5, +41.4] board-equivalent fJ, ratio 1.91 [1.71, 2.16], R1 INCONCLUSIVE, R1n and R1q NEITHER (BETWEEN));
      E130's (6 B, 4 A) its rail arm's (+33.15 board-equivalent, A FLAT and RISES at any scale, A's rail/board 0.811 [0.756, 0.872]);
  S2  the stop guard on a live and a stale sampler line written here (no card): the board stop at 1 W and the die stop at 1 C each
      fire on a fresh line with EXIT_HOT (6), a STOP line naming the stop and the line's age; at the registered 60 W / 72 C a fresh
      line passes through unchanged;
  S3  the smoke gate on a synthetic stop-test directory: it passes a correct one and fails one with a stale sample or a launch.

    python3 tools/claims-v3/e145/selftest_e145.py
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
D130 = os.path.join(ROOT, "docs/reports/data/2026-11-02-e130-int8-netlists")
D138 = os.path.join(ROOT, "docs/reports/data/2026-11-02-e138-int8-b-rail")
fails = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")
    if not cond:
        fails.append(name)


def s1():
    r = subprocess.run([sys.executable, os.path.join(HERE, "score_e145.py"), "--selftest",
                        f"{D130}/runs.csv,{D130}/e130.json", f"{D138}/runs.csv,{D138}/e138.json"], capture_output=True, text=True)
    if r.returncode:
        check("S1 scorer runs", False, r.stderr[-600:])
        return
    o = json.loads(r.stdout)
    e = o["E138"]["B_odd_minus_even_board_equivalent_fJ"]
    q = o["E138"]["B_odd_over_even"]
    v = o["E138"]["verdicts_rail"]
    check("S1 E138 rail B odd-even", (round(e["mean"], 1), round(e["lo"], 1), round(e["hi"], 1)) == (35.9, 30.5, 41.4),
          f"{e['mean']:.2f} [{e['lo']:.2f}, {e['hi']:.2f}] n {e['n']}")
    check("S1 E138 ratio", (round(q["ratio"], 2), round(q["lo"], 2), round(q["hi"], 2)) == (1.91, 1.71, 2.16),
          f"{q['ratio']:.3f} [{q['lo']:.3f}, {q['hi']:.3f}]")
    check("S1 E138 verdicts", (v["E145-R1"], v["E145-R1n"], v["E145-R1q"]) == ("INCONCLUSIVE", "NEITHER (BETWEEN)", "NEITHER (BETWEEN)"),
          json.dumps({k: v[k] for k in ("E145-R1", "E145-R1n", "E145-R1q", "E145-R2", "E145-C1")}))
    e = o["E130"]["B_odd_minus_even_board_equivalent_fJ"]
    v = o["E130"]["verdicts_rail"]
    a = o["E130"]["scale_A"]
    check("S1 E130 rail B odd-even", round(e["mean"], 2) == 33.15 and round(e["lo"], 2) == 29.56 and round(e["hi"], 2) == 36.75,
          f"{e['mean']:.2f} [{e['lo']:.2f}, {e['hi']:.2f}]")
    check("S1 E130 A control", (v["E145-R2"], v["E145-R3"], v["E145-C1"]) == ("FLAT", "RISES", "REPRODUCES card 0"),
          json.dumps({k: v[k] for k in ("E145-R2", "E145-R3", "E145-C1", "E145-R4", "E145-R5", "E145-R6")}))
    check("S1 E130 A-based rail/board scale", (round(a["ratio"], 3), round(a["lo"], 3), round(a["hi"], 3)) == (0.811, 0.756, 0.872),
          json.dumps(a))
    print("S1 E130 netlists (rail, board-equivalent):", json.dumps(v["E145-N"]))
    print("S1 E130 board arm:", json.dumps(o["E130"]["board_verdicts"]), json.dumps(o["E130"]["board_B_odd_minus_even"]))


def s2():
    import run_e145
    t = tempfile.mkdtemp(prefix="e145-st-")
    try:
        raw = os.path.join(t, "telemetry.jsonl.raw")

        def write(age):
            line = {"t_ms": int((time.time() - age) * 1000), "board_w": 40.0, "temp_c": {"minshire": [55, 50, 61], "pmic": 50}}
            open(raw, "w").write(json.dumps(line) + "\n")

        def fake_e78():
            m = types.SimpleNamespace(EXIT_HOT=6)

            def last_sample(path):
                return json.loads(open(path).read().splitlines()[-1])
            m.last_sample = last_sample
            return m

        for k, (bw, dc, word) in {"board": (1.0, 72.0, "board-power stop"), "die": (60.0, 1.0, "die stop")}.items():
            write(0.1)
            m = fake_e78()
            run_e145.guard_stops(m, bw, dc, t)
            try:
                m.last_sample(raw)
                check(f"S2 {k} stop fires", False, "no exit")
            except SystemExit as ex:
                txt = open(os.path.join(t, "STOP")).read()
                check(f"S2 {k} stop fires", ex.code == 6 and word in txt and "read 0." in txt and "telemetry.jsonl.raw" in txt, txt.strip())
            os.remove(os.path.join(t, "STOP"))
        write(0.1)
        m = fake_e78()
        run_e145.guard_stops(m, 60.0, 72.0, t)
        s = m.last_sample(raw)
        check("S2 registered stops pass a 40 W / 61 C line", s["board_w"] == 40.0 and not os.path.exists(os.path.join(t, "STOP")))
    finally:
        shutil.rmtree(t)


def s3():
    import smoke_gate_e145 as g
    t = tempfile.mkdtemp(prefix="e145-sg-")
    try:
        open(os.path.join(t, "stoptest.rc"), "w").write("die:rc=6\nboard:rc=6\n")
        open(os.path.join(t, "STOP.die"), "w").write("E145 die stop: hottest minion-shire reading 61.0 C >= 1.0 C (sample t_ms 1, read 0.12 s after it was taken, from telemetry.jsonl.raw)\n")
        open(os.path.join(t, "STOP.board"), "w").write("E145 board-power stop: board_w 33.1 W >= 1.0 W (sample t_ms 1, read 0.2 s after it was taken, from telemetry.jsonl.raw)\n")
        bad = []
        g.stoptest(t, bad)
        check("S3 gate passes a correct stop test", not bad, json.dumps(bad))
        open(os.path.join(t, "STOP.board"), "w").write("E145 board-power stop: board_w 33.1 W >= 1.0 W (sample t_ms 1, read 9.5 s after it was taken, from telemetry.jsonl)\n")
        open(os.path.join(t, "marks.jsonl"), "w").write(json.dumps({"kind": "run", "item": "int8.hb1"}) + "\n")
        bad = []
        g.stoptest(t, bad)
        check("S3 gate fails a stale sample, the wrong file and a launch", len(bad) == 2, json.dumps(bad))
    finally:
        shutil.rmtree(t)


def main():
    s1()
    s2()
    s3()
    print("SELFTEST", "PASS" if not fails else f"FAIL {fails}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
