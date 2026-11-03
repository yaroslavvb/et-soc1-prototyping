#!/usr/bin/env python3
"""E145's registered smoke gate (README.md, "Protocol" and "Stops"), on the stop-path test (pass 14502) and the smoke (pass 14501).
A port of tools/claims-v3/e137/smoke_gate_e137.py with three E145 changes, each marked:

  the stop-path test (E145 change 1): stoptest.rc reads die:rc=6 and board:rc=6 (each run_e145.py invocation ended with EXIT_HOT on
      its first reading); STOP.die names the die stop and STOP.board the board-power stop, each read from telemetry.jsonl.raw (the
      running sampler's live file) at most 2.0 s after the sample was taken; no launch record and no run mark exist (nothing ran);
  the smoke, E137's gate on int8: every smoke item (e145_common.SMOKE_ITEMS) has launch records; every record is ok, with
      tensor_errors 0; each item's median cycles per op (launch >= 0) is within 0.5% of E78's 318; every launch record's clock reads
      0.595-0.605 GHz (600 MHz); the block's two config reads read card 1's TDP 65 W, threshold 65 C and 600 MHz; and (E145 change 2)
      every item's dumped tile equals its registered sha256;
  the minion rail is live on this card (E145 change 3; the registered primary needs it, README.md "The meter"): in the smoke's
      telemetry sp.minion_w[0] takes at least 20 distinct values, its 5th-95th percentile range is at least 1.0 W, and no 30
      consecutive samples hold one value. If this part fails, the session runs no block: the board as primary would need about
      60 B blocks at E138's board scatter, beyond the 50 card-minutes (README.md, "The meter").

Exit 0 if the gate passes, 1 if not. Standard library only.

    python3 tools/claims-v3/e145/smoke_gate_e145.py <smoke pass dir> <stop-test pass dir>
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
import e145_common as e145  # noqa: E402

CPO = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
AGE_MAX_S = 2.0
RAIL_DISTINCT_MIN, RAIL_RANGE_MIN_W, RAIL_STUCK_MAX = 20, 1.0, 30


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
    for k, word in (("die", "E145 die stop: hottest minion-shire reading"), ("board", "E145 board-power stop: board_w")):
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
    marks = [m for m in jl(os.path.join(d, "marks.jsonl")) if m.get("kind") == "run"]
    if runs or marks:
        bad.append(f"stop test: {len(runs)} launch records and {len(marks)} run marks (want none: no launch)")


def smoke(d, bad):
    recs = jl(os.path.join(d, "runs.jsonl"))
    seen = {}
    for r in recs:
        seen.setdefault(r["item"], []).append(r)
        if not r.get("ok") or r.get("tensor_errors", 0) != 0:
            bad.append(f"{r['item']}: ok={r.get('ok')} tensor_errors={r.get('tensor_errors')} result={r.get('result')}")
    miss = [n for n in e145.SMOKE_ITEMS if n not in seen]
    if miss:
        bad.append(f"smoke items without launch records: {miss}")
    items = {it["name"]: it for it in e145.load_items()}
    td = os.path.join(d, "tiles")
    for n in e145.SMOKE_ITEMS:
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
        if not (isinstance(c, dict) and c.get("tdp_w") == 65 and c.get("temp_threshold_c") == 65 and c.get("minion_mhz") == 600):
            bad.append(f"{nm}: {c} is not card 1's 65 W / 65 C / 600 MHz")
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
    if len(rail) < 20:
        bad.append(f"rail: {len(rail)} samples carry sp.minion_w (want the rail in every sample)")
        return
    q = sorted(rail)
    p5, p95 = q[int(0.05 * (len(q) - 1))], q[int(0.95 * (len(q) - 1))]
    stuck, run = 1, 1
    for a, b in zip(rail, rail[1:]):
        run = run + 1 if a == b else 1
        stuck = max(stuck, run)
    distinct = len(set(rail))
    board = [s.get("board_w") for s in tel if isinstance(s.get("board_w"), (int, float))]
    print(f"rail: {len(rail)} samples, {distinct} distinct, 5-95% {p5:.3f}-{p95:.3f} W, longest constant run {stuck}; "
          f"board {min(board):.2f}-{max(board):.2f} W; die (shire mean) "
          f"{min(s['temp_c']['minshire'][0] for s in tel)}-{max(s['temp_c']['minshire'][0] for s in tel)} C")
    if distinct < RAIL_DISTINCT_MIN or p95 - p5 < RAIL_RANGE_MIN_W or stuck >= RAIL_STUCK_MAX:
        bad.append(f"rail not live: {distinct} distinct values, 5-95% range {p95 - p5:.3f} W, longest constant run {stuck} samples")


def main():
    d, t = sys.argv[1], sys.argv[2]
    bad = []
    stoptest(t, bad)
    smoke(d, bad)
    ok = not bad
    print("SMOKE-GATE", "PASS" if ok else "FAIL", {"bad": bad})
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
