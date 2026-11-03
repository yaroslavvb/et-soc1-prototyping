#!/usr/bin/env python3
"""E151's desk self-test (Q139), run on the Intel before the registration commit and before any E151 data; its output is
selftest-e151.txt. Standard library only (the reductions it compares were written by e145_under_filter.py with numpy).

  1. the rail filter on synthetic lines: a lone glitch at the running maximum (F1 and F2), a pair of glitches (F1 both), a load step
     (nothing), a glitch at a high load under 4 W above its neighbours (F2 only), an aifoundry3-like stream (nothing);
  2. the rail filter on E145's committed blocks marks E145's post-hoc 15 samples (posthoc/rail-spikes.json: 15 spikes, 15 at the
     running maximum), and none in E138's or E130's aifoundry3 blocks;
  3. E145's reducer with the filter (e145_under_filter.py) reproduces E145's post-hoc reduction byte for byte (runs.csv; the reduce json);
  4. the scorer (score_e151.score_session, through E145's, E138's and E130's scorers unchanged) gives back E138's registered rail
     numbers on E138's runs, E130's rail arm on E130's, and E145's post-hoc numbers on E145's filtered runs (R1 RECODED there);
  5. the stop guard (run_e151._check_line) fires on a live line at 1 W and at 1 C, reads minshire[0] and not the 87 C latch, and passes
     a normal line at the registered 45 W / 68 C;
  6. the smoke gate's stop-path test passes a correct stop test and fails a stale one and a launched one;
  7. check_e151.py --desk reads HARNESS OK, and e151_common.py --verify finds no problem.

    python3 tools/claims-v3/e151/selftest_e151.py > tools/claims-v3/e151/selftest-e151.txt
SPDX-License-Identifier: Apache-2.0
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import railfilter_e151 as rf  # noqa: E402

D = os.path.join(ROOT, "docs/reports/data")
D130, D138, D145 = (os.path.join(D, x) for x in ("2026-11-02-e130-int8-netlists", "2026-11-02-e138-int8-b-rail",
                                                  "2026-11-02-e145-int8-b-card1"))
F145 = os.path.join(HERE, "e145-filtered")
FAILS = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))
    if not ok:
        FAILS.append(name)


def line(r, m=34.5, board=31.0, die=(52.0, 46.0, 87.0), t=None):
    return {"t_ms": t, "board_w": board, "sp": {"minion_w": [r, r, m]}, "temp_c": {"minshire": list(die)}}


def close(a, b, tol=0.006):
    return a is not None and b is not None and abs(a - b) <= tol


def main():
    print(f"E151 self-test, {time.strftime('%Y-%m-%d %H:%M %Z')}")
    # 1. synthetic
    base = [13.5] * 11
    s = list(base); s[5] = 34.5
    f = rf.flags([line(x) for x in s])
    check("1a lone glitch at the running maximum: F1 and F2", f["F1"] == {5} and f["F2"] == {5}, json.dumps({k: sorted(v) for k, v in f.items()}))
    s = list(base); s[5] = s[6] = 34.5
    f = rf.flags([line(x) for x in s])
    check("1b a pair of glitches: both marked", f["union"] == {5, 6}, json.dumps(sorted(f["union"])))
    s = [9.0] * 5 + [15.0] * 6
    f = rf.flags([line(x, m=38.375) for x in s])
    check("1c a load step: nothing marked", not f["union"], json.dumps(sorted(f["union"])))
    s = [30.5] * 11; s[5] = 34.5
    f = rf.flags([line(x) for x in s])
    check("1d a glitch at a high load under 4 W above its neighbours: F2 only", f["F1"] == set() and f["F2"] == {5})
    s = [12.0 + 0.1 * (i % 3) for i in range(40)]
    f = rf.flags([line(x, m=38.375) for x in s])
    check("1e an aifoundry3-like stream (max field 38.375 W): nothing marked", not f["union"])
    # 2. committed blocks
    c145 = rf.census([os.path.join(D145, "aifoundry1-c1", "kinds")])["total"]
    ph = json.load(open(os.path.join(D145, "posthoc", "rail-spikes.json")))["E145 (aifoundry1 card 1)"]["total"]
    check("2a E145's 16 blocks: the filter marks E145's post-hoc 15, all at the running maximum",
          c145["union"] == ph["spikes"] == 15 and c145["F2"] == ph["spikes_at_max_register"] == 15 and c145["samples"] == ph["samples"],
          json.dumps(c145))
    for name, d, sub in (("E138", D138, "aifoundry3/kinds"), ("E130", D130, "aifoundry3/kinds")):
        c = rf.census([os.path.join(d, sub)])["total"]
        check(f"2b {name}'s aifoundry3 blocks: nothing marked", c["union"] == 0 and c["samples"] > 10000, json.dumps(c))
    # 3. E145's reducer with the filter = E145's post hoc
    same_csv = open(os.path.join(F145, "runs.csv"), "rb").read() == open(os.path.join(D145, "posthoc", "runs-posthoc.csv"), "rb").read()
    same_json = json.load(open(os.path.join(F145, "e145-filtered.json"))) == json.load(open(os.path.join(D145, "posthoc", "e145-posthoc.json")))
    check("3 E145's reducer with E151's filter reproduces E145's post-hoc reduction byte for byte", same_csv and same_json,
          f"runs.csv {same_csv}, reduce json {same_json}")
    # 4. the scorer
    import score_e151 as S151
    reg = json.load(open(os.path.join(HERE, "predictions-e151.json")))
    S151.check_reg(reg)
    tiles = {"int8." + t["tile"]: t for t in json.load(open(os.path.join(HERE, "e130-items.json")))["tiles"]}
    want138 = json.load(open(os.path.join(D138, "scored.json")))["primary"]["B_odd_minus_even_board_equivalent_fJ"]
    want145 = json.load(open(os.path.join(D145, "posthoc", "scored-posthoc.json")))["primary"]["B_odd_minus_even_board_equivalent_fJ"]
    for name, cp, rp, num, want, rule in (
            ("E138", f"{D138}/runs.csv", f"{D138}/e138.json", "e138", want138, "INCONCLUSIVE"),
            ("E130", f"{D130}/runs.csv", f"{D130}/e130.json", "e130", {"mean": 33.15, "lo": 29.56, "hi": 36.75, "n": 6}, "INCONCLUSIVE"),
            ("E145 filtered", f"{F145}/runs.csv", f"{F145}/e145-filtered.json", "e145", want145, "RECODED")):
        r = S151.score_session((cp, rp), {}, {}, reg, tiles, num)
        e = r["primary"]["B_odd_minus_even_board_equivalent_fJ"]
        tol = 1e-9 if name != "E130" else 0.006
        ok = all(close(e[k], want[k], tol) for k in ("mean", "lo", "hi")) and e["n"] == want["n"] and r["primary"]["verdicts"]["E151-R1"] == rule
        check(f"4 the scorer on {name}: B odd - even {e['mean']:+.2f} [{e['lo']:+.2f}, {e['hi']:+.2f}] (n {e['n']}), R1 {r['primary']['verdicts']['E151-R1']}",
              ok, f"want {want.get('mean'):+.2f} [{want.get('lo'):+.2f}, {want.get('hi'):+.2f}], R1 {rule}")
    # 5. the stop guard
    import run_e151 as R
    now_ms = time.time() * 1000
    live = line(12.0, m=38.375, board=23.4, die=(52.0, 46.0, 87.0), t=now_ms)
    check("5a a normal live line passes at the registered 45 W / 68 C (minshire[2] = 87 C is the latch)",
          R._check_line(live, 45.0, 68.0, "E151", "telemetry.jsonl.raw") is None)
    m = R._check_line(live, 1.0, 68.0, "E151", "telemetry.jsonl.raw") or ""
    check("5b the board stop at 1.0 W fires and names the sample's age", "E151 board-power stop: board_w" in m and "read " in m, m[:120])
    m = R._check_line(live, 45.0, 1.0, "E151", "telemetry.jsonl.raw") or ""
    check("5c the die stop at 1.0 C fires on minshire[0]", "E151 die stop: minion-shire reading minshire[0] 52.0" in m, m[:120])
    hot = line(12.0, m=38.375, board=46.0, die=(52.0, 46.0, 87.0), t=now_ms)
    check("5d a 46 W line trips the 45 W stop", (R._check_line(hot, 45.0, 68.0, "E151", "x") or "").startswith("E151 board-power stop"))
    warm = line(12.0, m=38.375, board=30.0, die=(68.0, 46.0, 87.0), t=now_ms)
    check("5e a 68 C minshire[0] trips the 68 C die stop", "die stop" in (R._check_line(warm, 45.0, 68.0, "E151", "x") or ""))
    # 6. the smoke gate's stop-path test
    import smoke_gate_e151 as G
    tmp = tempfile.mkdtemp()
    try:
        def mk(age, launched=False):
            d = tempfile.mkdtemp(dir=tmp)
            open(os.path.join(d, "stoptest.rc"), "w").write("die:rc=6\nboard:rc=6\nwatch:rc=6\n")
            for k, word in G.TESTS:
                open(os.path.join(d, f"STOP.{k}"), "w").write(
                    f"{word} 52.0 C >= 1.0 C (sample t_ms 1, read {age} s after it was taken, from telemetry.jsonl.raw)\n")
            if launched:
                open(os.path.join(d, "runs.jsonl"), "w").write('{"item": "int8.hb1"}\n')
            return d
        for name, age, launched, want in (("correct", 0.05, False, True), ("stale", 3.5, False, False), ("launched", 0.05, True, False)):
            bad = []
            out = io.StringIO()
            so, sys.stdout = sys.stdout, out
            try:
                G.stoptest(mk(age, launched), bad)
            finally:
                sys.stdout = so
            check(f"6 the smoke gate's stop test, {name}: {'passes' if want else 'fails'}", (not bad) == want, "; ".join(bad)[:160])
    finally:
        shutil.rmtree(tmp)
    # 7. the harness check and the orders
    r = subprocess.run([sys.executable, os.path.join(HERE, "check_e151.py"), "--desk"], capture_output=True, text=True)
    check("7a check_e151.py --desk", r.returncode == 0 and "HARNESS OK" in r.stdout, r.stdout.strip()[:160])
    r = subprocess.run([sys.executable, os.path.join(HERE, "e151_common.py"), "--verify"], capture_output=True, text=True)
    check("7b e151_common.py --verify", r.returncode == 0 and '"problems": []' in r.stdout, r.stdout.strip()[:160])
    print("SELFTEST", "PASS" if not FAILS else "FAIL", FAILS)
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
