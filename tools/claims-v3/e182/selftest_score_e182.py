#!/usr/bin/env python3
"""E182 (Q153, the kit): the scorer's and the train reducer's self-test. No card; it writes only under <work dir>.

ON COMMITTED DATA (E178, 6 Nov 2026, docs/reports/data/2026-11-06-e178-one-number-aifoundry3/):
  A1  score_e182's slope rule on E178's 13 int8 kinds (scored.json's D, launch-mean flips and rates) gives E178-W-int8's committed slope
      exactly (to 1e-9 fJ) and its interval to the rounding of E178's t table (E178's scorer read t(11) as 2.201; this scorer's t is
      exact, 2.20099), within 2e-4 fJ;
  A2  e182_stats.spearman on E178's scored P against its measured D gives E178-R-int8's committed rho to 1e-12;
  A3  e182_stats's train functions (dips_kept, launch_reading, quads_of_process), run on E178's committed telemetry with each one-kind
      run read as an SFFS process, give noise-e182.json's int8 and float quad sd (to 1e-5: that file rounds to five places).
ON SYNTHETIC SESSIONS (fake_card_e182.py, the box's layout; reduce_e182.py trains and score_e182.py score, as the collector runs them):
  B1  arm E's world: E182-HT POSITIVE, SIZE E PASS, SIZE P FAIL HIGH, REPEAT AGREES; E182-A NULL, E182-B POSITIVE with SIZE E PASS and
      SIZE P FAIL HIGH, E182-SPLIT B-ONLY; E182-X CONSISTENT; E182-F NULL; E182-TR-N AS FORECAST; E182-W-int8 PASS against E and FAIL
      HIGH against P; E182-C PASS; and an arm (the same reduction passed as one) reads the same W, R and 24 levels;
  B2  a world where half of E's B-side price sits on A: E182-A POSITIVE, E182-B POSITIVE, E182-SPLIT A+B;
  B3  P's world: E182-HT SIZE P PASS; E182-B SIZE P PASS; E182-SPLIT B-ONLY; E182-W-int8 PASS against P;
  B4  noise at 2.5 times the forecast: E182-TR-N FAILS;
  B5  T3 cut to 6 processes (3 units): T3 NOT SCORED, so E182-A, E182-B and E182-SPLIT NOT SCORED, the other trains scored;
  B6  one T5 launch FAILs the check of C: E182-C FAIL and E182-F NOT SCORED;
  B7  one kinds pass: E182-W-int8 and E182-R-int8 NOT SCORED;
  B8  ccsessions_e182's list on a synthetic raw tree: the smoke, every train block (by train.jsonl) and every kinds pass with a launch
      record, and no .attempt copy;
  B9  smoke_gate_e182.py --part train on a synthetic smoke in the box's layout (T1's two processes, the C log's host, tiles and C
      records, the dumps): PASS; with one launch's kind off the schedule: FAIL.
    /usr/bin/python3 -B selftest_score_e182.py <work dir>
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e182_stats as S  # noqa: E402
import score_e182 as SC  # noqa: E402
E178 = os.path.join(TOP, "docs/reports/data/2026-11-06-e178-one-number-aifoundry3")
PY = "/usr/bin/python3"
FAILS, N = [], [0]


def say(ok, what):
    N[0] += 1
    print(("PASS " if ok else "FAIL ") + what, flush=True)
    if not ok:
        FAILS.append(what)


def committed():
    sc = json.load(open(os.path.join(E178, "scored.json")))
    ks = sc["primary"]["reported"]["kinds"]
    w = sc["primary"]["rules"]["E178-W-int8"]
    kinds = list(w["kinds"])
    r = SC.slope_rule({k: ks[k]["D_w"] for k in kinds}, {k: ks[k]["flips_launch_mean"] for k in kinds},
                      {k: ks[k]["rate_per_s"] for k in kinds}, kinds, {"E": 2.7812, "P": w["line_fJ"]})
    say(abs(r["slope_fJ_per_flip"] - w["slope_fJ_per_flip"]) < 1e-9 and abs(r["lo95_fJ"] - w["lo95_fJ"]) < 2e-4 and
        abs(r["hi95_fJ"] - w["hi95_fJ"]) < 2e-4,
        f"A1 E178-W-int8 again: slope {r['slope_fJ_per_flip']:.10f} against {w['slope_fJ_per_flip']:.10f}, interval [{r['lo95_fJ']:.5f}, "
        f"{r['hi95_fJ']:.5f}] against [{w['lo95_fJ']:.5f}, {w['hi95_fJ']:.5f}]")
    rr = sc["primary"]["rules"]["E178-R-int8"]
    rho = S.spearman([ks[k]["P_w"] for k in rr["kinds"]], [ks[k]["D_w"] for k in rr["kinds"]])
    say(abs(rho - rr["rho"]) < 1e-12, f"A2 E178-R-int8 again: rho {rho:.12f} against {rr['rho']:.12f}")
    nz = json.load(open(os.path.join(HERE, "noise", "noise-e182.json")))
    quads = {"int8": [], "float": []}
    for p in ("p17810", "p17811", "p17812", "p17813"):
        d = os.path.join(E178, "aifoundry3", "e178", p)
        rows = []
        with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt") as f:
            for line in f:
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                if isinstance(o.get("board_w"), (int, float)) and isinstance(o.get("t_ms"), (int, float)):
                    rows.append((int(o["t_ms"]), float(o["board_w"])))
        kept = S.dips_kept(sorted(rows))
        ts, ws = [t for t, _ in kept], [w for _, w in kept]
        runs = {}
        for line in open(os.path.join(d, "runs.jsonl")):
            r = json.loads(line)
            if r.get("ok", True) and r["launch"] >= 0:
                runs.setdefault((r["pos"], r["item"]), []).append(r)
        for (pos, item), L in runs.items():
            if item.endswith(".zeros") or item in ("fp32.randn", "fp16.randn", "int8.full", "anchor_pi"):
                continue
            rd = {r["launch"]: S.launch_reading(ts, ws, r["t_start_ms"], r["t_end_ms"]) for r in L}
            q = S.quads_of_process(rd, "SFFS")
            quads["int8" if item.startswith("int8.") else "float"] += q[:2]
    import statistics as st
    got = {k: round(st.stdev(v), 5) for k, v in quads.items()}
    say(got["int8"] == nz["sigma_q_w"]["int8"] and got["float"] == nz["sigma_q_w"]["float"],
        f"A3 the train functions on E178's telemetry: quad sd {got} against noise-e182.json {nz['sigma_q_w']} "
        f"({len(quads['int8'])} and {len(quads['float'])} quads)")


def session(work, name, *args):
    d = os.path.join(work, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    subprocess.run([PY, "-B", os.path.join(HERE, "fake_card_e182.py"), d, *args], check=True, capture_output=True)
    blocks = sorted(os.path.join(d, "raw", "e182", b) for b in os.listdir(os.path.join(d, "raw", "e182")) if b.startswith("p1821"))
    subprocess.run([PY, "-B", os.path.join(HERE, "reduce_e182.py"), "trains", *blocks, "--out", os.path.join(d, "trains-e182.json")],
                   check=True, capture_output=True)
    r = subprocess.run([PY, "-B", os.path.join(HERE, "score_e182.py"), "score", "--reduction", os.path.join(d, "e182.json"), "--runs-csv",
                        os.path.join(d, "runs.csv"), "--trains", os.path.join(d, "trains-e182.json"), "--raw", os.path.join(d, "raw"),
                        "--ccheck", os.path.join(d, "ccheck-all.json"), "--skip-c-gate", "--json", os.path.join(d, "scored.json"), "--md",
                        os.path.join(d, "results.md"), "--arm", f"leak0={os.path.join(d, 'e182.json')},{os.path.join(d, 'runs.csv')}"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        return None
    return json.load(open(os.path.join(d, "scored.json")))


def synthetic(work):
    s = session(work, "b1", "--world", "E", "--seed", "18291")
    v, R = s["verdicts"], s["rules"]
    ok = (v["E182-HT"] == "POSITIVE" and R["E182-HT"]["size_E"] == "PASS" and R["E182-HT"]["size_P"] == "FAIL HIGH" and
          R["E182-HT"]["repeat"] == "AGREES" and v["E182-A"] == "NULL" and v["E182-B"] == "POSITIVE" and R["E182-B"]["size_E"] == "PASS" and
          R["E182-B"]["size_P"] == "FAIL HIGH" and v["E182-SPLIT"] == "B-ONLY" and v["E182-X"] == "CONSISTENT" and v["E182-F"] == "NULL" and
          v["E182-TR-N"] == "AS FORECAST" and R["E182-W-int8"]["size_E"] == "PASS" and R["E182-W-int8"]["size_P"] == "FAIL HIGH" and
          v["E182-C"] == "PASS")
    arm = s["reported"]["arms"]["leak0"]
    ok = ok and arm["E182-W-int8"]["size_E"] == R["E182-W-int8"]["size_E"] and arm["E182-R-int8"]["verdict"] == v["E182-R-int8"] and \
        len(arm["levels"]) == 24
    say(ok, f"B1 arm E's world: {v}; the arm (the same reduction passed as leak0) reads W {arm['E182-W-int8']['size_E']}, "
            f"R {arm['E182-R-int8']['verdict']}, {len(arm['levels'])} levels")
    s = session(work, "b2", "--world", "AB", "--seed", "18292")
    v = s["verdicts"]
    say(v["E182-A"] == "POSITIVE" and v["E182-B"] == "POSITIVE" and v["E182-SPLIT"] == "A+B", f"B2 half of B's price on A: {v}")
    s = session(work, "b3", "--world", "P", "--seed", "18293")
    v, R = s["verdicts"], s["rules"]
    say(R["E182-HT"]["size_P"] == "PASS" and R["E182-B"]["size_P"] == "PASS" and v["E182-SPLIT"] == "B-ONLY" and
        R["E182-W-int8"]["size_P"] == "PASS", f"B3 P's world: {v}; SIZE P {R['E182-HT']['size_P']}, B {R['E182-B']['size_P']}, "
                                               f"W {R['E182-W-int8']['size_P']}")
    s = session(work, "b4", "--world", "E", "--seed", "18294", "--noise-scale", "2.5")
    say(s["verdicts"]["E182-TR-N"] == "FAILS", f"B4 noise at 2.5 times: TR-N {s['verdicts']['E182-TR-N']} "
                                               f"(ratio {s['rules']['E182-TR-N'].get('largest_ratio')})")
    s = session(work, "b5", "--world", "E", "--seed", "18295", "--short", "T3:6")
    v = s["verdicts"]
    say(v["E182-A"] == "NOT SCORED" and v["E182-B"] == "NOT SCORED" and v["E182-SPLIT"] == "NOT SCORED" and v["E182-HT"] != "NOT SCORED",
        f"B5 T3 cut to 6 processes: {v}")
    s = session(work, "b6", "--world", "E", "--seed", "18296", "--cfail", "T5")
    v = s["verdicts"]
    say(v["E182-C"] == "FAIL" and v["E182-F"] == "NOT SCORED" and v["E182-HT"] == "POSITIVE", f"B6 a C FAIL in T5: {v}")
    s = session(work, "b7", "--world", "E", "--seed", "18297", "--passes", "1")
    v = s["verdicts"]
    say(v["E182-W-int8"] == "NOT SCORED" and v["E182-R-int8"] == "NOT SCORED", f"B7 one kinds pass: W {v['E182-W-int8']}, R {v['E182-R-int8']}")
    # B8 the C-session list
    import ccsessions_e182 as CS
    raw = os.path.join(work, "b8raw")
    if os.path.isdir(raw):
        shutil.rmtree(raw)
    for sub in ("e182-smoke/p18201", "e182-stoptest/p18202", "e182/p18210", "e182/p18215", "e182/p18220", "e182/p18221",
                "e182/p18220.attempt-1", "e182/p18222"):
        os.makedirs(os.path.join(raw, sub))
    open(os.path.join(raw, "e182/p18210/train.jsonl"), "w").write(json.dumps({"process": 0, "launch": 0}) + "\n")
    os.makedirs(os.path.join(raw, "e182/p18215/a0"))
    open(os.path.join(raw, "e182/p18215/a0/runs.jsonl"), "w").write(json.dumps({"item": "int8.zeros", "launch": 0}) + "\n")
    for p in ("p18220", "p18220.attempt-1"):
        open(os.path.join(raw, "e182", p, "runs.jsonl"), "w").write(json.dumps({"item": "int8.ones", "launch": 0}) + "\n")
    got = [os.path.relpath(x, raw) for x in CS.listed_sessions("E182", raw)]
    want = ["e182-smoke/p18201", "e182/p18210", "e182/p18215", "e182/p18220"]
    say(got == want, f"B8 the C-session list: {got}")
    # B9 the smoke gate's train part on a synthetic smoke (the box's layout), then with one launch off the schedule
    res = []
    for nm, extra in (("b9", []), ("b9bad", ["--break-schedule"])):
        d = os.path.join(work, nm)
        if os.path.isdir(d):
            shutil.rmtree(d)
        subprocess.run([PY, "-B", os.path.join(HERE, "fake_card_e182.py"), d, "--smoke", *extra], check=True, capture_output=True)
        r = subprocess.run([PY, "-B", os.path.join(HERE, "smoke_gate_e182.py"), os.path.join(d, "p18201"), os.path.join(d, "none"), "--part",
                            "train"], capture_output=True, text=True)
        res.append((r.returncode, r.stdout.strip().splitlines()[-1][:160] if r.stdout.strip() else ""))
    say(res[0][0] == 0 and res[1][0] == 1, f"B9 the smoke gate's train part: a good smoke {res[0]}; one launch off the schedule {res[1]}")


def main():
    work = os.path.abspath(sys.argv[1])
    os.makedirs(work, exist_ok=True)
    committed()
    synthetic(work)
    print(f"SELFTEST-SCORE-E182 {N[0] - len(FAILS)} of {N[0]} PASS" + ("" if not FAILS else ": " + "; ".join(FAILS)))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
