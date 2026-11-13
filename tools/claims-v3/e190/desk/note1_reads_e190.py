#!/usr/bin/env python3
"""E190's kit, dated note 1 (Q169, lane fix-e190, Fri 13 Nov 2026, before any E190 datum): the two desk reads of committed records the
note's bounds rest on. Python's own modules only; reads only.

    /usr/bin/python3 -I -B tools/claims-v3/e190/desk/note1_reads_e190.py > tools/claims-v3/e190/desk/note1-reads-e190.txt

  1. THE SAMPLER'S GAPS: in the committed telemetry of the two readers E190 uses (aifoundry2's in E136, E146, E169 and E175; card 1's in
     E157, E164, E172 and E184 arm B), the gaps between consecutive samples of one file (t_ms): the median, the 99.9th percentile, the
     largest, and how many reach 1 s and 2 s. The freshness bound (a sample under 2 s old before every process) must sit far above them.
  2. THE DEVICE LAYER'S BLOCK: in the committed host and reader stderr of the September runs on aifoundry1's card 1 and on aifoundry2
     (docs/reports/data/2026-09-25-claims-v3, 2026-09-29-memp2, 2026-09-29-pcie2: raw/aifoundry1-c1 and raw/aifoundry2), the nodes the
     "PCIe target:" lines name, counted by node: the host watch's "another card" must never be read on a card's own runs.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import json
import os
import re
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(REPO, "docs", "reports", "data")
GAPS = [("aifoundry2", "E136", "2026-11-02-e136-large-gemm"), ("aifoundry2", "E146", "2026-11-02-e146-gemm-stores"),
        ("aifoundry2", "E169", "2026-11-04-e169-stride-shapes"), ("aifoundry2", "E175", "2026-11-05-e175-governed-aifoundry2"),
        ("card 1", "E157", "2026-11-03-e157-blind6-card1"), ("card 1", "E164", "2026-11-04-e164-blind7-card1"),
        ("card 1", "E172", "2026-11-05-e172-blind8-card1"), ("card 1", "E184", "2026-11-08-e184-sensor-validation")]
BLOCKS = ["2026-09-25-claims-v3", "2026-09-29-memp2", "2026-09-29-pcie2"]


def tel_files(d, card1):
    out = []
    for pat in ("**/*.jsonl.gz", "**/*.jsonl"):
        out += glob.glob(os.path.join(DATA, d, pat), recursive=True)
    if card1 and "e184" in d:
        out = [f for f in out if "aifoundry1-c1" in f]
    return sorted(out)


def gaps():
    tot = 0
    for card, exp, d in GAPS:
        g, n, nf = [], 0, 0
        for f in tel_files(d, card == "card 1"):
            op = gzip.open if f.endswith(".gz") else open
            ts = []
            try:
                with op(f, "rt") as fh:
                    for ln in fh:
                        if ln.startswith("{"):
                            try:
                                s = json.loads(ln)
                            except ValueError:
                                continue
                            if "board_w" in s and isinstance(s.get("t_ms"), (int, float)):
                                ts.append(s["t_ms"])
            except (OSError, EOFError):
                continue
            if len(ts) < 50:
                continue
            nf += 1
            n += len(ts)
            g += [b - a for a, b in zip(ts, ts[1:]) if b >= a]
        tot += n
        if not g:
            print(f"  {card} {exp}: no telemetry found")
            continue
        g.sort()
        print(f"  {card} {exp}: {nf} files, {n} samples; the gap's median {statistics.median(g):.0f} ms, 99.9th percentile "
              f"{g[int(0.999 * (len(g) - 1))]:.0f} ms, largest {g[-1]:.0f} ms; gaps of 1 s or more: {sum(1 for x in g if x >= 1000)}, "
              f"of 2 s or more: {sum(1 for x in g if x >= 2000)}")
    print(f"  all: {tot} samples")


def blocks():
    rx = re.compile(r"PCIe target:\s+(/dev/et[0-9]+_[a-z]+)")
    for box in ("aifoundry1-c1", "aifoundry2"):
        c = {}
        for d in BLOCKS:
            for f in glob.glob(os.path.join(DATA, d, "raw", box, "**", "*"), recursive=True):
                if not os.path.isfile(f) or f.endswith((".gz", ".bin")):
                    continue
                try:
                    with open(f, errors="replace") as fh:
                        for ln in fh:
                            m = rx.search(ln)
                            if m:
                                c[m.group(1)] = c.get(m.group(1), 0) + 1
                except OSError:
                    continue
        print(f"  {box}: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))


print("E190 kit note 1's desk reads of committed records (reads only; nothing measured here)")
print("1. the gaps between consecutive samples of each committed telemetry file of the two readers E190 uses:")
gaps()
print("2. the nodes the device layer's 'PCIe target:' lines name in the September host and reader stderr, by box:")
blocks()
print("NOTE1 READS DONE")
