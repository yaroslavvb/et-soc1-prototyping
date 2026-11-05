#!/usr/bin/env python3
"""E171's registered smoke gate (E171.md, "The session plan"), on the stop-path test (pass 17102) and the smoke (pass 17101). A copy of
tools/claims-v3/e163/smoke_gate_e163.py (E163's gate on this card, itself E153's and E141's) with E171's items, tags and registration
files (E171: e171_common, plan-e171.json for the stops, harness-e171.json for the registered binaries); its checks are E163's:

  the stop-path test: stoptest.rc reads die:rc=6, board:rc=6 and watch:rc=6 (each run_e171.py invocation ended with EXIT_HOT); STOP.die
      names the die stop, STOP.board the board-power stop and STOP.watch the in-run watcher's board-power stop, each read from
      telemetry.jsonl.raw (the running sampler's live file) at most 2.0 s after the sample was taken; no launch record and no run mark
      exist (nothing ran);
  the smoke: every smoke item (e171_common.SMOKE_ITEMS) has launch records; every record is ok, with tensor_errors 0; each item's median
      cycles per op (launch >= 0) is within 0.5% of E78's 546 (fp32, fp16) or 318 (int8); every launch record's clock reads 0.595-0.605 GHz
      (600 MHz); the block's two config reads read aifoundry3's TDP 0 W, threshold 65 C, 600 MHz; every item's dumped tile equals its
      registered sha256 (the pool's tiles; E78's built-in kinds dump what the host program generated, which has no registered hash and is
      not checked); no STOP file; the smoke's telemetry is live: at least 100 samples, `since_reset_ms` -1 in every one (no statistics
      reset), and its board maximum below the registered board stop;
  the C log is there (its arithmetic is checked at the desk, ccheck.py, never on the box): the pass's c-log.jsonl(.gz) holds at least one
      host record, and every host record names the registered C-logging host and the power passes' kernel by sha256 (harness-e171.json
      > box_binaries_sha256); every launch record of every smoke item has a C record with the same t_start_ms and t_end_ms, ok, poison
      on, the tensor mask and B streaming off, and at least one C group;
  the C log's DMA fits E78's window: the median gap between consecutive measured launches of a smoke run is at most 10 ms.

Exit 0 if the gate passes, 1 if not. Standard library only.

    python3 tools/claims-v3/e171/smoke_gate_e171.py <smoke pass dir> <stop-test pass dir>
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
import e171_common as e153  # noqa: E402  (E171: the name kept from E153's gate, E171's module)

CPO = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
AGE_MAX_S = 2.0
TESTS = (("die", "E171 die stop: minion-shire reading minshire[0]"), ("board", "E171 board-power stop: board_w"),
         ("watch", "E171 watcher board-power stop: board_w"))


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
    miss = [n for n in e153.SMOKE_ITEMS if n not in seen]
    if miss:
        bad.append(f"smoke items without launch records: {miss}")
    items = {it["name"]: it for it in e153.load_items()}
    td = os.path.join(d, "tiles")
    for n in e153.SMOKE_ITEMS:
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
        if not (isinstance(c, dict) and c.get("tdp_w") == 0 and c.get("temp_threshold_c") == 65 and c.get("minion_mhz") == 600):
            bad.append(f"{nm}: {c} is not aifoundry3's 0 W / 65 C / 600 MHz")
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



def clog(d, bad, reg):
    """E153's change 1: the C log is there and pairs with every launch record (structure only; ccheck.py checks the arithmetic)."""
    want = json.load(open(os.path.join(HERE, "harness-e171.json")))["box_binaries_sha256"]                    # E171
    host_sha = want["build/ccheck/b/host/sparsity_host"]
    kern_sha = want["build/sparsity/kernel/sparsity.elf"]
    recs = jl(os.path.join(d, "c-log.jsonl.gz")) or jl(os.path.join(d, "c-log.jsonl"))
    hosts = [r for r in recs if r.get("kind") == "host"]
    cs = {(r.get("t_start_ms"), r.get("t_end_ms")): r for r in recs if r.get("kind") == "c"}
    if not hosts:
        bad.append("C log: no host record (the wrapper did not run)")
    for h in hosts:
        if h.get("host_sha256") != host_sha or h.get("kernel_sha256") != kern_sha:
            bad.append(f"C log: host record {h.get('host_sha256', '')[:12]} / kernel {h.get('kernel_sha256', '')[:12]} is not the registered "
                       f"{host_sha[:12]} / {kern_sha[:12]}")
            break
    runs = jl(os.path.join(d, "runs.jsonl"))
    miss, flags = 0, 0
    for r in runs:
        c = cs.get((r.get("t_start_ms"), r.get("t_end_ms")))
        if c is None:
            miss += 1
            continue
        if not (c.get("ok") is True and c.get("poison") is True and c.get("use_mask") == 0 and c.get("b_stream") == 0
                and c.get("groups")):
            flags += 1
    if miss or flags:
        bad.append(f"C log: {miss} launch records without a C record, {flags} C records not ok/poisoned/unmasked/unstreamed/non-empty")
    print(f"C log: {len(hosts)} host records, {len(cs)} C records, {len(runs)} launch records, {miss} unpaired, {flags} flagged")
    # E153's change 2: the C log's extra DMA (1 MiB written before each launch, 1 MiB read after it) must leave E78's window covered.
    # E141's launches here were 480-494 ms with a 1 ms median gap (duty 0.996); E78's per-run gate needs duty >= 0.97, about a
    # 14 ms gap. Registered: the median gap between consecutive measured launches (launch >= 0) of a smoke run <= 10 ms.
    by = {}
    for r in runs:
        if isinstance(r.get("launch"), int) and r["launch"] >= 0 and r.get("t_start_ms") and r.get("t_end_ms"):
            by.setdefault((r.get("item"), r.get("pos"), r.get("attempt")), []).append(r)
    gaps = []
    for v in by.values():
        v.sort(key=lambda r: r["t_start_ms"])
        gaps += [b["t_start_ms"] - a["t_end_ms"] for a, b in zip(v, v[1:])]
    if not gaps:
        bad.append("C log: no two consecutive launches to time the DMA gap")
    else:
        g = statistics.median(gaps)
        print(f"launch gaps with the C log: median {g} ms, max {max(gaps)} ms over {len(gaps)} gaps (registered: median <= 10 ms)")
        if g > 10:
            bad.append(f"C log: the median gap between launches is {g} ms, above the registered 10 ms (E78's duty gate would bind)")

def main():
    d, t = sys.argv[1], sys.argv[2]
    reg = json.load(open(os.path.join(HERE, "plan-e171.json")))
    bad = []
    stoptest(t, bad)
    smoke(d, bad, reg["plan"]["stops"]["kinds"]["board_w"])
    clog(d, bad, reg)
    ok = not bad
    print("SMOKE-GATE", "PASS" if ok else "FAIL", {"bad": bad})
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
