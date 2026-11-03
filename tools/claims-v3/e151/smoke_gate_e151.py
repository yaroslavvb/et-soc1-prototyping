#!/usr/bin/env python3
"""E151's registered smoke gate (README.md, "Protocol", "Stops" and "The meter"), on the stop-path test (pass 15102) and the smoke
(pass 15101). A port of tools/claims-v3/e145/smoke_gate_e145.py with tools/claims-v3/e141/smoke_gate_e141.py's aifoundry3 stop test,
each change marked E151:

  the stop-path test (E141's, E151 change 1): stoptest.rc reads die:rc=6, board:rc=6 and watch:rc=6 (each run_e151.py invocation
      ended with EXIT_HOT); STOP.die names the die stop (minshire[0]), STOP.board the board-power stop and STOP.watch the in-run
      watcher's board-power stop, each read from telemetry.jsonl.raw (the running sampler's live file) at most 2.0 s after the sample
      was taken; no launch record and no launch mark exist (nothing ran);
  the smoke, E145's gate on int8: every smoke item (e151_common.SMOKE_ITEMS) has launch records; every record is ok, with
      tensor_errors 0; each item's median cycles per op (launch >= 0) is within 0.5% of E78's 318; every launch record's clock reads
      0.595-0.605 GHz (600 MHz); every item's dumped tile equals its registered sha256; no STOP file; and (E151 change 2) the block's
      two config reads read aifoundry3's TDP 0 W, threshold 65 C and 600 MHz; `since_reset_ms` -1 in every sample (no statistics
      reset); the board's maximum below the registered board stop (45 W);
  the minion rail is LIVE (E145's test): in the smoke's telemetry sp.minion_w[0] takes at least 20 distinct values, its 5th-95th
      percentile range is at least 1.0 W, and no 30 consecutive samples hold one value; and CLEAN (E151 change 3, README.md "The
      meter"): the registered rail filter (railfilter_e151.py) marks at most 1% of the smoke's samples (on aifoundry3 it has marked
      none of about 700,000 since 1 Nov; card 1's rate was 0.06%). If either part fails, the session runs no block.

Exit 0 if the gate passes, 1 if not. Standard library only.

    python3 tools/claims-v3/e151/smoke_gate_e151.py <smoke pass dir> <stop-test pass dir>
SPDX-License-Identifier: Apache-2.0"""
import gzip
import hashlib
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e151_common as e151  # noqa: E402
import railfilter_e151 as rf  # noqa: E402

CPO = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
AGE_MAX_S = 2.0
RAIL_DISTINCT_MIN, RAIL_RANGE_MIN_W, RAIL_STUCK_MAX, RAIL_GLITCH_MAX_FRAC = 20, 1.0, 30, 0.01
TESTS = (("die", "E151 die stop: minion-shire reading minshire[0]"), ("board", "E151 board-power stop: board_w"),
         ("watch", "E151 watcher board-power stop: board_w"))
CONFIG = {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}                         # E151 change 2: aifoundry3's reads


def jl(path):
    if not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        return [json.loads(x) for x in f if x.strip().startswith("{")]


def stoptest(d, bad):
    try:
        rcs = dict(x.strip().split(":", 1) for x in open(os.path.join(d, "stoptest.rc")) if ":" in x)
    except OSError:
        rcs = {}
    for k, word in TESTS:
        if rcs.get(k) != "rc=6":
            bad.append(f"stop test {k}: {rcs.get(k)} (want rc=6, EXIT_HOT)")
        try:
            txt = open(os.path.join(d, f"STOP.{k}")).read()
        except OSError:
            txt = ""
        m = re.search(r"read (-?[0-9.]+) s after it was taken, from (\S+)\)", txt)
        if word not in txt or not m:
            bad.append(f"stop test {k}: STOP.{k} does not name the stop and the sample's age: {txt[:200]!r}")
            continue
        age, src = float(m.group(1)), m.group(2)
        if not (age <= AGE_MAX_S) or src != "telemetry.jsonl.raw":
            bad.append(f"stop test {k}: sample read {age} s after it was taken, from {src} (want <= {AGE_MAX_S} s, telemetry.jsonl.raw)")
        print(f"stop test {k}: {rcs.get(k)}; {txt.strip()[:240]}")
    runs = jl(os.path.join(d, "runs.jsonl"))
    marks = [m for m in jl(os.path.join(d, "marks.jsonl")) if m.get("kind") in ("run", "heater", "burnin")]
    if runs or marks:
        bad.append(f"stop test: {len(runs)} launch records and {len(marks)} launch marks (want none: no launch)")


def smoke(d, bad, board_stop_w):
    recs = jl(os.path.join(d, "runs.jsonl"))
    seen = {}
    for r in recs:
        seen.setdefault(r["item"], []).append(r)
        if not r.get("ok") or r.get("tensor_errors", 0) != 0:
            bad.append(f"{r['item']}: ok={r.get('ok')} tensor_errors={r.get('tensor_errors')} result={r.get('result')}")
    miss = [n for n in e151.SMOKE_ITEMS if n not in seen]
    if miss:
        bad.append(f"smoke items without launch records: {miss}")
    items = {it["name"]: it for it in e151.load_items()}
    td = os.path.join(d, "tiles")
    for n in e151.SMOKE_ITEMS:
        rr = [r for r in seen.get(n, []) if r.get("launch", 0) >= 0]
        if not rr:
            continue
        ty = rr[0]["type"]
        cpo = statistics.median(r["cycles_per_op"] for r in rr)
        ghz = sorted({r.get("ghz") for r in rr})
        if abs(cpo / CPO[ty] - 1) > 0.005:
            bad.append(f"{n}: median cycles per op {cpo} not within 0.5% of {CPO[ty]}")
        if not all(isinstance(g, (int, float)) and 0.595 <= g <= 0.605 for g in ghz):
            bad.append(f"{n}: clock {ghz} GHz outside 0.595-0.605")
        dumps = [f for f in (os.listdir(td) if os.path.isdir(td) else []) if f.startswith(n + ".b")]
        same = [hashlib.sha256(open(os.path.join(td, f), "rb").read()).hexdigest() == items[n]["sha256"] for f in dumps]
        if not dumps or not all(same):
            bad.append(f"{n}: dumped tile {dumps} equal to its registered sha256: {same}")
        print(f"smoke {n}: {len(rr)} launch records, median cycles per op {cpo}, ghz {ghz[0]}-{ghz[-1]}, dump equals sha256 {same}")
    for nm in ("config_start", "config_end"):
        try:
            c = json.load(open(os.path.join(d, nm + ".json")))
        except (OSError, ValueError):
            c = None
        if not (isinstance(c, dict) and all(c.get(k) == v for k, v in CONFIG.items())):
            bad.append(f"{nm}: {c} is not aifoundry3's 0 W / 65 C / 600 MHz")
        print(f"smoke {nm}: {c}")
    if os.path.exists(os.path.join(d, "STOP")):
        bad.append("smoke: a STOP file exists in the smoke pass")
    tel = jl(os.path.join(d, "telemetry.jsonl.gz")) or jl(os.path.join(d, "telemetry.jsonl"))
    rail = []
    for s in tel:
        try:
            rail.append(float(s["sp"]["minion_w"][0]))
        except (KeyError, IndexError, TypeError, ValueError):
            pass
    if len(rail) < 20 or len(rail) < len(tel):
        bad.append(f"rail: {len(rail)} of {len(tel)} samples carry sp.minion_w (want the rail in every sample)")
        return
    resets = sorted({s.get("since_reset_ms") for s in tel})
    if resets != [-1]:
        bad.append(f"since_reset_ms {resets} (want -1 in every sample: no statistics reset)")
    board = [s.get("board_w") for s in tel if isinstance(s.get("board_w"), (int, float))]
    if not board or max(board) >= board_stop_w:
        bad.append(f"board maximum {max(board) if board else None} W not below the registered stop {board_stop_w} W")
    q = sorted(rail)
    p5, p95 = q[int(0.05 * (len(q) - 1))], q[int(0.95 * (len(q) - 1))]
    stuck, run = 1, 1
    for a, b in zip(rail, rail[1:]):
        run = run + 1 if a == b else 1
        stuck = max(stuck, run)
    distinct = len(set(rail))
    fl = rf.flags(tel)                                                                                    # E151 change 3
    frac = len(fl["union"]) / len(tel)
    print(f"rail: {len(rail)} samples, {distinct} distinct, 5-95% {p5:.3f}-{p95:.3f} W, longest constant run {stuck}; "
          f"the registered filter marks {len(fl['union'])} (F1 {len(fl['F1'])}, F2 {len(fl['F2'])}, {100 * frac:.2f}%); "
          f"board {min(board):.2f}-{max(board):.2f} W; die (minshire[0]) "
          f"{min(s['temp_c']['minshire'][0] for s in tel)}-{max(s['temp_c']['minshire'][0] for s in tel)} C; since_reset_ms {resets}")
    if distinct < RAIL_DISTINCT_MIN or p95 - p5 < RAIL_RANGE_MIN_W or stuck >= RAIL_STUCK_MAX:
        bad.append(f"rail not live: {distinct} distinct values, 5-95% range {p95 - p5:.3f} W, longest constant run {stuck} samples")
    if frac > RAIL_GLITCH_MAX_FRAC:
        bad.append(f"rail not clean: the registered filter marks {len(fl['union'])} of {len(tel)} samples ({100 * frac:.2f}% > 1%)")


def main():
    d, t = sys.argv[1], sys.argv[2]
    reg = json.load(open(os.path.join(HERE, "predictions-e151.json")))
    bad = []
    stoptest(t, bad)
    smoke(d, bad, reg["plan"]["stops"]["board_w"])
    ok = not bad
    print("SMOKE-GATE", "PASS" if ok else "FAIL", {"bad": bad})
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
