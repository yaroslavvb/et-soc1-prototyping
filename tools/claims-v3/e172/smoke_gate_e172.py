#!/usr/bin/env python3
"""E172's registered smoke gate (E172.md, Stops), on the stop-path test (pass 17202) and the smoke (pass 17201). A port of
tools/claims-v3/e157/smoke_gate_e157.py, unchanged but for E172's names, its smoke items (e172_common.SMOKE_ITEMS), its stops
(plan-e172.json > plan.stops) and its pins (harness-e172.json > box_binaries_sha256), each marked E172:

  the stop-path test (E145's, plus E142 change 1): stoptest.rc reads die:rc=6, board:rc=6 and watch:rc=6 (each run_e172.py
      invocation ended with EXIT_HOT); STOP.die names the die stop, STOP.board the board-power stop and STOP.watch the in-run
      watcher's board-power stop, each read from telemetry.jsonl.raw (the running sampler's live file) at most 2.0 s after the
      sample was taken; no launch record and no run mark exist (nothing ran);
  the smoke (E145's gate on three formats, E142 change 2): every smoke item has launch records; every record is ok, with
      tensor_errors 0; each item's median cycles per op (launch >= 0) is within 0.5% of E78's 546 (fp32, fp16) or 318 (int8); every
      launch record's clock reads 0.595-0.605 GHz (600 MHz); the block's two config reads read card 1's TDP 65 W, threshold 65 C and
      600 MHz; every item's dumped tile equals its registered sha256 (the pools' tiles; E78's built-in kinds dump what the host program
      generated, which has no registered hash and is not checked); no STOP file; and (E142 change 3) the smoke's telemetry is live:
      at least 100 samples, `since_reset_ms` -1 in every one (no statistics reset), and its board maximum below the registered stop;
  the C log (E157 change 1): the smoke pass has a C log (c-log.jsonl or .gz); every process wrote a host record naming the patched
      host and the kernel with the registered sha256; every launch record in runs.jsonl has a C record with the same t_start_ms and
      t_end_ms, ok, poison on, use_mask 0, b_stream 0, row_mask 0xffff and 1,024 participants. The C itself is checked at the desk
      (ccheck.py check), never on the box. The launch gaps are printed, a reading only.

Exit 0 if the gate passes, 1 if not. Standard library only.

    python3 -B tools/claims-v3/e172/smoke_gate_e172.py <smoke pass dir> <stop-test pass dir>
SPDX-License-Identifier: Apache-2.0"""
import gzip
import hashlib
import json
import os
import re
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e172_common as e172  # noqa: E402

CPO = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
AGE_MAX_S = 2.0
TESTS = (("die", "E172 die stop: hottest minion-shire reading"), ("board", "E172 board-power stop: board_w"),     # E172
         ("watch", "E172 watcher board-power stop: board_w"))


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
    miss = [n for n in e172.SMOKE_ITEMS if n not in seen]
    if miss:
        bad.append(f"smoke items without launch records: {miss}")
    items = {it["name"]: it for it in e172.load_items()}
    td = os.path.join(d, "tiles")
    for n in e172.SMOKE_ITEMS:
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
        same = None
        if items[n].get("values") is None and items[n].get("tile"):
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
    if len(tel) < 100:
        bad.append(f"telemetry: {len(tel)} samples (want at least 100)")
        return
    rs = sorted({s.get("since_reset_ms") for s in tel}, key=str)
    if rs != [-1]:
        bad.append(f"telemetry: since_reset_ms takes {rs[:5]} (want -1 in every sample: no statistics reset)")
    board = [s.get("board_w") for s in tel if isinstance(s.get("board_w"), (int, float))]
    mean = [s["temp_c"]["minshire"][0] for s in tel if (s.get("temp_c") or {}).get("minshire")]
    print(f"telemetry: {len(tel)} samples, board {min(board):.2f}-{max(board):.2f} W, shire mean {min(mean)}-{max(mean)} C, "
          f"since_reset_ms {rs}")
    if max(board) >= board_stop_w:
        bad.append(f"telemetry: board maximum {max(board)} W at or above the registered stop {board_stop_w} W")


def clog(d, bad, pins):
    """E157 change 1: the C log's structure (the C is checked at the desk)."""
    recs = jl(os.path.join(d, "c-log.jsonl.gz")) or jl(os.path.join(d, "c-log.jsonl"))
    if not recs:
        bad.append("C log: no c-log.jsonl(.gz) records in the smoke pass")
        return
    hosts = [r for r in recs if r.get("kind") == "host"]
    cs = [r for r in recs if r.get("kind") == "c"]
    tiles = [r for r in recs if r.get("kind") == "tiles"]
    want_h = pins.get("build/ccheck/b/host/sparsity_host")
    want_k = pins.get("build/sparsity/kernel/sparsity.elf")
    for h in hosts:
        if h.get("host_sha256") != want_h or h.get("kernel_sha256") != want_k:
            bad.append(f"C log host record: host {h.get('host_sha256', '')[:12]} kernel {h.get('kernel_sha256', '')[:12]} "
                       f"(want {str(want_h)[:12]} / {str(want_k)[:12]})")
            break
    byt = {(r.get("t_start_ms"), r.get("t_end_ms")): r for r in cs}
    runs = jl(os.path.join(d, "runs.jsonl"))
    miss, badrec = [], []
    for r in runs:
        c = byt.get((r.get("t_start_ms"), r.get("t_end_ms")))
        if c is None:
            miss.append((r.get("item"), r.get("launch")))
            continue
        if not (c.get("ok") and c.get("poison") is True and c.get("use_mask") == 0 and c.get("b_stream") == 0
                and c.get("row_mask") == "0xffff" and c.get("participants") == 1024):
            badrec.append((r.get("item"), r.get("launch")))
    if miss:
        bad.append(f"C log: {len(miss)} launch records without a C record: {miss[:6]}")
    if badrec:
        bad.append(f"C log: {len(badrec)} C records not ok / poison / mask 0 / stream 0 / 1,024 participants: {badrec[:6]}")
    ng = sorted({len(c.get("groups") or []) for c in cs})
    gaps = []
    for a, b in zip(runs, runs[1:]):
        if a.get("item") == b.get("item") and a.get("pos") == b.get("pos") and b.get("launch", -1) >= 0:
            try:
                gaps.append(int(b["t_start_ms"]) - int(a["t_end_ms"]))
            except (KeyError, TypeError, ValueError):
                pass
    gaps.sort()
    print(f"C log: {len(hosts)} host records, {len(tiles)} tiles records, {len(cs)} C records for {len(runs)} launch records; "
          f"distinct C per launch {ng}; launch gaps ms min/median/max "
          f"{gaps[0] if gaps else '-'}/{gaps[len(gaps) // 2] if gaps else '-'}/{gaps[-1] if gaps else '-'} (a reading only)")


def main():
    d, t = sys.argv[1], sys.argv[2]
    reg = json.load(open(os.path.join(HERE, "plan-e172.json")))                    # E172
    har = json.load(open(os.path.join(HERE, "harness-e172.json")))                        # E172
    bad = []
    stoptest(t, bad)
    smoke(d, bad, reg["plan"]["stops"]["board_w"])
    clog(d, bad, har["box_binaries_sha256"])
    ok = not bad
    print("SMOKE-GATE", "PASS" if ok else "FAIL", {"bad": bad})
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
