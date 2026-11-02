#!/usr/bin/env python3
"""E133: the checks behind the README's corrections after verification (Mon 2 Nov 2026). Post hoc, desk only, committed files only.

Run from the top of the repository:

    python3 docs/reports/data/2026-11-02-e133-heat-holds/corrections_e133.py docs/reports/data/2026-11-02-e133-heat-holds \
        > docs/reports/data/2026-11-02-e133-heat-holds/corrections_e133.txt

[A] H-F32's plateau, the scorer's 300 s window (results.json A.H-F32.plateau t0_ms..t1_ms), on every raw row of
    W2/tel/HOLDF-00-fp32-randn-hold-r1.jsonl.gz: the die readings (temp_c.minshire[0], the firmware's whole-degree mean of
    the minion-shire sensors, the scorer's "die") and the clock (mhz.minion), as counts. The scorer itself reads only the
    rows inside a kernel (results.json A.H-F32.plateau n).
[B] Every REST block's raw rows: the die readings as counts, and the same inside the scorer's idle window (results.json
    A.idles.<step> t0_ms..t1_ms).
[C] The SP trace dumps, */sp/*.bin: the 8 KiB trace buffer as `ettelem sptrace` read it at each step's start, after every
    run and at each step's end. Each entry is an 8-byte little-endian timestamp, a 4-byte length and 4 more bytes, then
    its text. A dump holds the buffer's last entries, so dumps repeat entries; distinct entries are told apart by their
    timestamp. Counted: the thermal throttle-down lines, the distinct events, every distinct text, and the run whose dump
    first carries each event (in session order).
[D] The minute wander of both holds (results.json beside.*.minutes.wander) and the cool probe's lead on E98's W-derived
    rest-die scale (results.json B.B3c, B.rest_die), as the corrected text cites them.

Nothing here is a registered reading; the registered verdicts are reduce_e133.py's, unchanged.
"""
import collections
import glob
import gzip
import json
import os
import re
import struct
import sys

D = sys.argv[1]
STEPS = ["SMOKE", "W2", "END", "W1B", "END2"]
res = json.load(open(os.path.join(D, "results.json")))


def tel(path):
    with gzip.open(path, "rt", errors="replace") as fh:
        for line in fh:
            if not line.startswith("{"):
                continue
            try:
                d = json.loads(line)
                yield int(d["t_ms"]), d["temp_c"]["minshire"][0], d["mhz"]["minion"]
            except (ValueError, KeyError, TypeError, IndexError):
                continue


def counts(c):
    n = sum(c.values())
    return ", ".join(f"{k}: {v} ({100.0 * v / n:.1f}%)" for k, v in sorted(c.items())) + f"; {n} rows"


def runs(step):
    return [json.loads(x)["run"] for x in open(os.path.join(D, step, "runs.jsonl")) if x.strip()]


# [A]
pl = res["A"]["H-F32"]["plateau"]
a, b = pl["t0_ms"], pl["t1_ms"]
die, mhz = collections.Counter(), collections.Counter()
for t, d, m in tel(os.path.join(D, "W2", "tel", "HOLDF-00-fp32-randn-hold-r1.jsonl.gz")):
    if a <= t < b:
        die[d] += 1
        mhz[m] += 1
n = sum(die.values())
print(f"[A] H-F32's plateau, {a}..{b} ms (results.json A.H-F32.plateau), every raw row of W2/tel/HOLDF-00-fp32-randn-hold-r1.jsonl.gz")
print(f"  die readings (C): {counts(die)}")
print(f"  their mean: {sum(k * v for k, v in die.items()) / n:.3f} C (the scorer's, on its {pl['n']} in-kernel rows: {pl['die']})")
print(f"  clock (MHz): {counts(mhz)}")
print(f"  share at 600 MHz: {mhz[600] / n:.4f} (the scorer's, in-kernel: {pl['share_clock']})")

# [B]
print()
print("[B] the REST blocks: die readings on every raw row, and in the scorer's idle, the block's last 60 s (results.json A.idles)")
for s in STEPS:
    for r in runs(s):
        if not r.endswith("-rest-r1"):
            continue
        p = os.path.join(D, s, "tel", r + ".jsonl.gz")
        if not os.path.exists(p):
            continue
        rows = list(tel(p))
        allr = collections.Counter(d for _, d, _ in rows)
        t1 = max(t for t, _, _ in rows)
        last = collections.Counter(d for t, d, _ in rows if t >= t1 - 60000)
        w = (res["A"].get("idles") or {}).get(s)
        line = f"  {s}/{r}: every row {counts(allr)}; the last 60 s {counts(last)}"
        if w:
            line += f" (results.json A.idles.{s}: die {w['die']}, {w['n']} samples)"
        print(line)

# [C]
print()
print("[C] the SP trace dumps (*/sp/*.bin), in session order")
DOWN = re.compile(rb"Thermal throttle down event, current temperature: \d+, threshold: \d+")
ANY = re.compile(rb"(Thermal throttle down event|Power throttle up event|New OP: Freq)")
order = []
for s in STEPS:
    for nm in ["start"] + runs(s) + ["end"]:
        p = os.path.join(D, s, "sp", nm + ".bin")
        if os.path.exists(p):
            order.append((f"{s}/{nm}", p))
seen = {p for _, p in order}
for p in sorted(set(glob.glob(os.path.join(D, "*", "sp", "*.bin"))) - seen):
    order.append((os.path.relpath(p, D)[:-4], p))
first, texts, lines, per_dump, entries = {}, collections.Counter(), 0, [], []
for name, p in order:
    buf = open(p, "rb").read()
    k = 0
    entries.append(len(ANY.findall(buf)))
    for m in DOWN.finditer(buf):
        if m.start() < 16:
            continue
        ts = struct.unpack_from("<Q", buf, m.start() - 16)[0]
        lines += 1
        k += 1
        if ts not in first:
            first[ts] = name
            texts[m.group().decode()] += 1
    if k:
        per_dump.append(f"{name} {k}")
print(f"  {len(order)} dumps; timestamped entries per dump {min(entries)}-{max(entries)}")
print(f"  thermal throttle-down lines: {lines}, in {len(per_dump)} dumps: {'; '.join(per_dump)}")
print(f"  distinct throttle-down events (by timestamp): {len(first)}")
for txt, k in texts.most_common():
    print(f"    {k} x '{txt}'")
print(f"  first carried by: {dict(collections.Counter(first.values()))}")

# [D]
print()
for h in ("H-F32", "H-I8"):
    w = res["beside"][h]["minutes"]["wander"]
    print(f"[D] {h}'s minute bins from minute {w['from_min']}: {w['lo']}-{w['hi']} C, range {w['range_c']} C (results.json beside.{h}.minutes.wander)")
b3 = res["B"]["B3c"]
pp = b3["per_probe"]["E133-W2"]
print(f"[D] the cool probe E133-W2: dx {pp['dx_c']} C on E98's W-derived rest-die scale (results.json B.rest_die E133-W2 "
      f"{res['B']['rest_die']['E133-W2']} against the P3/P6/P7 mean {b3['baseline_values']['rest_die_w_derived']}); "
      f"line {pp['line_per_c']} per C, hold {pp['hold_per_c']} per C (results.json B.B3c.per_probe.E133-W2)")
