#!/usr/bin/env python3
"""E188's smoke gate (E188.md section 6, the smoke "gated"), on the stop-path test (block 18802) and the smoke (block 18801). A port of
tools/claims-v3/e186/smoke_gate_e186.py (E186's gate on this card, run on 9 Nov 2026; itself E182's, E178's, E171's, E163's, E153's and
E141's) with E188's items, tags and files (E188: e188_common, harness-e188.json for the registered binaries, the train host under
build/e188host/):

  --part kinds (E178's checks, unchanged): the stop-path test (die, board and watch each rc=6, each STOP naming its stop and the sample's
      age read from telemetry.jsonl.raw within 2.0 s; no launch); the smoke's kinds items (e188_common.SMOKE_ITEMS: the tie, E78's six
      anchors and E188's six new tiles, fp32.e188_a1_b3f800010, _b3f800020, _b3f800400, _b3f800c00, _b3f804400 and _b3f880000, each run
      2 s, their first launches on a card): launch records, ok, tensor_errors 0, median cycles per op within 0.5% of 546 / 318, every clock
      0.595-0.605 GHz, the two config reads 0 W / 65 C / 600 MHz, every dumped tile equal to its registered sha256, no STOP, live telemetry
      (100 samples or more, since_reset_ms -1 throughout, board maximum under 65 W), the C log present, its host records naming the
      registered C-logging host and kernel, every launch paired with a C record (ok, poisoned, unmasked, unstreamed, non-empty), the
      median launch gap at most 10 ms;
  --part train (E182's): <smoke>/train/: train.rc 0; exactly two processes (B05's first two, SFFS then FSSF: the train the kit names for
      the smoke, the session's first); each 14 launch records (launches -1 to 12), every one ok with tensor_errors 0, its train_kind by the
      registered schedule and its train_values the kind's tile; median cycles per op within 0.5% of 546 (fp32) and every clock 0.595-0.605
      GHz; the dumped F and S tiles equal their registered sha256; the block's C log holds host records naming the train host (its build
      record's binary sha256) and the kernel, the two tile sets, and a C record for every train launch with the scheduled kind's fnv; the
      median gap between a process's launches at most 10 ms. (Its arithmetic, every train launch against its own tiles, is checked at the
      desk by ccheck.py.)
The gate reads no power step against a band, so E184 A2-5's refresh rule has nothing to apply to here.

Exit 0 if the part passes, 1 if not. Standard library only.

    python3 tools/claims-v3/e188/smoke_gate_e188.py <smoke dir> <stop-test dir> --part kinds|train
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
import e188_common as e153  # noqa: E402  (the name kept from E153's gate; E188's module)

CPO = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
AGE_MAX_S = 2.0
TESTS = (("die", "E188 die stop: minion-shire reading minshire[0]"), ("board", "E188 board-power stop: board_w"),
         ("watch", "E188 watcher board-power stop: board_w"))


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


def clog(d, bad):
    """E153's change 1: the C log is there and pairs with every launch record (structure only; ccheck.py checks the arithmetic)."""
    want = json.load(open(os.path.join(HERE, "harness-e188.json")))["box_binaries_sha256"]                    # E188
    host_sha = want["build/ccheck/b/host/sparsity_host"]
    kern_sha = want["build/sparsity/kernel/sparsity.elf"]
    recs = jl(os.path.join(d, "c-log.jsonl.gz")) or jl(os.path.join(d, "c-log.jsonl"))
    hosts = [r for r in recs if r.get("kind") == "host"]
    cs = {(r.get("t_start_ms"), r.get("t_end_ms")): r for r in recs if r.get("kind") == "c"}
    if not hosts:
        bad.append("C log: no host record (the wrapper did not run)")
    tr_sha = train_host_sha(d)
    for h in hosts:
        if h.get("host_sha256") == tr_sha and tr_sha and h.get("kernel_sha256") == kern_sha:
            continue                                          # E182's: the train smoke's records (read by --part train)
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
    # Registered (E153, E163, E171, and E178 by "Gated as E171's smoke"): the median gap between consecutive measured launches
    # (launch >= 0) of a smoke run <= 10 ms.
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


def train_host_sha(d):
    """the train host's binary sha256 from the block's binaries.sha256 (copied from its build record at the block's start)"""
    p = os.path.join(d, "binaries.sha256")
    if not os.path.exists(p):
        return None
    for line in open(p):
        if line.strip().endswith("build/e188host/b/host/sparsity_host"):
            return line.split()[0]
    return None


def train(d, bad):
    """E182's: the smoke's two train processes (E188: B05's)"""
    td = os.path.join(d, "train")
    t = e153.train_of_block(e153.SMOKE_PASS)
    try:
        rc = open(os.path.join(d, "train.rc")).read().strip()
    except OSError:
        rc = None
    if rc != "0":
        bad.append(f"train: train.rc {rc!r} (want 0)")
    recs = jl(os.path.join(td, "train.jsonl"))
    procs = sorted({r["process"] for r in recs})
    if procs != list(range(e153.SMOKE_TRAIN_PROCESSES)):
        bad.append(f"train: processes {procs} (want {list(range(e153.SMOKE_TRAIN_PROCESSES))})")
    items = {it["name"]: it for it in e153.load_items()}
    tiles = {"F": items[t["first"]], "S": items[t["second"]]}
    gaps, cpos, ghz = [], [], set()
    for k in procs:
        rr = sorted((r for r in recs if r["process"] == k), key=lambda r: r["launch"])
        ori = t["orientations"][k]
        sched = [ori[0] if n < 1 else ori[(n - 1) % 4] for n in range(-1, e153.LAUNCHES)]
        kinds = [r.get("train_kind") for r in rr]
        if [r["launch"] for r in rr] != list(range(-1, e153.LAUNCHES)) or kinds != sched:
            bad.append(f"train process {k} ({ori}): launches {[r['launch'] for r in rr]}, kinds {''.join(x or '?' for x in kinds)} "
                       f"against {''.join(sched)}")
        for r in rr:
            if not r.get("ok") or r.get("tensor_errors", 0) != 0 or r.get("abba") != ori or r.get("orientation") != ori:
                bad.append(f"train process {k} launch {r['launch']}: ok={r.get('ok')} tensor_errors={r.get('tensor_errors')} abba={r.get('abba')}")
            kk = r.get("train_kind")
            if kk in tiles and not str(r.get("train_values", "")).endswith(tiles[kk]["tile"]):
                bad.append(f"train process {k} launch {r['launch']}: train_values {r.get('train_values')} is not {tiles[kk]['tile']}")
            if r["launch"] >= 0:
                cpos.append(r["cycles_per_op"])
                ghz.add(r.get("ghz"))
        ms = [r for r in rr if r["launch"] >= 0]
        gaps += [b["t_start_ms"] - a["t_end_ms"] for a, b in zip(ms, ms[1:])]
    if cpos and abs(statistics.median(cpos) / CPO[t["type"]] - 1) > 0.005:
        bad.append(f"train: median cycles per op {statistics.median(cpos)} not within 0.5% of {CPO[t['type']]}")
    if not all(isinstance(g, (int, float)) and 0.595 <= g <= 0.605 for g in ghz):
        bad.append(f"train: clock {sorted(ghz, key=str)} GHz outside 0.595-0.605")
    dumps = os.path.join(td, "tiles", f"train.b{e153.SMOKE_PASS}.bin")
    for path, kk in ((dumps, "F"), (dumps + ".S", "S")):
        ok = os.path.exists(path) and hashlib.sha256(open(path, "rb").read()).hexdigest() == tiles[kk]["sha256"]
        if not ok:
            bad.append(f"train: the dumped {kk} tile {os.path.basename(path)} is not {tiles[kk]['name']}'s registered sha256")
    want = json.load(open(os.path.join(HERE, "harness-e188.json")))["box_binaries_sha256"]
    tr_sha = train_host_sha(d)
    cl = jl(os.path.join(d, "c-log.jsonl.gz")) or jl(os.path.join(d, "c-log.jsonl"))
    hosts = [r for r in cl if r.get("kind") == "host" and r.get("host_sha256") == tr_sha and tr_sha]
    if not hosts or any(h.get("kernel_sha256") != want["build/sparsity/kernel/sparsity.elf"] for h in hosts):
        bad.append(f"train: the C log has no host record of the train host ({(tr_sha or '')[:12]}) with the registered kernel")
    fnv = {}
    for r in cl:
        if r.get("kind") == "tiles":
            fnv[r.get("values")] = r.get("fnv")
    cs = {(r.get("t_start_ms"), r.get("t_end_ms")): r for r in cl if r.get("kind") == "c"}
    miss = 0
    for r in recs:
        c = cs.get((r.get("t_start_ms"), r.get("t_end_ms")))
        if c is None or c.get("fnv") != fnv.get(r.get("train_values")) or not (c.get("ok") is True and c.get("poison") is True and c.get("groups")):
            miss += 1
    if miss:
        bad.append(f"train: {miss} train launches without a C record of the scheduled kind's tiles")
    if gaps and statistics.median(gaps) > 10:
        bad.append(f"train: the median gap between a process's launches is {statistics.median(gaps)} ms, above 10 ms")
    print(f"train: {len(procs)} processes, {len(recs)} launch records, median cycles per op {statistics.median(cpos) if cpos else None}, "
          f"median gap {statistics.median(gaps) if gaps else None} ms, {miss} launches without their C record")


def main():
    d, t = sys.argv[1], sys.argv[2]
    part = sys.argv[sys.argv.index("--part") + 1] if "--part" in sys.argv else "kinds"
    bad = []
    if part == "kinds":
        stoptest(t, bad)
        smoke(d, bad, e153.stops()["board_w"])
        clog(d, bad)
    elif part == "train":
        train(d, bad)
    else:
        print(f"--part {part}: only kinds or train")
        sys.exit(2)
    ok = not bad
    print(f"SMOKE-GATE ({part})", "PASS" if ok else "FAIL", {"bad": bad})
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
