#!/usr/bin/env python3
"""E200's data READMEs, dated note 1 (Mon 16 Nov 2026, after the data verifier): two of the figures the notes quote, read again from
the committed files. Post hoc: it decides nothing, scores nothing and changes no committed file.

    python3 -I -B docs/reports/data/2026-11-16-e200-regfile-sitting-2-aifoundry2/posthoc_note1_e200.py [--data1 DIR --data2 DIR]

It sits in sitting 2's data directory and reads both sittings' directories (sitting 1's beside it, unless --data1 and --data2 name
them, as when it runs from a copy). It reads only files of the two data commits, each checked first against its directory's
SHA256SUMS: session/MANIFEST.sha256 and the files it lists (run/telemetry.jsonl as unpacked from run/telemetry.jsonl.gz), and
run/marks.jsonl, run/runs.jsonl and the telemetry for section 2. It prints plain text to standard output: directory names only, times
relative to a process's first launch, floats rounded to 3 places, no run time; so a re-run prints the same bytes.

Section 0: each directory's SHA256SUMS, entry by entry.
Section 1: the box's manifest (session/MANIFEST.sha256, written on the box before the collection) against the committed files, line by
  line; for a line that does not match, the lines of that file that hold the collection's "~" (the scrub writes the box's home as "~").
Section 2: every train process of blocks A-E (not the smoke): its launches (the launch records of its block that start inside its mark's
  span), S = its first launch's start, E = its last launch's end, its telemetry samples in [S, E]; its climb = the first sample at
  800 MHz (within 1 MHz) less S; OFF when a sample with a clock in [S + 1.5 s, E] is not at 800 MHz within 1 MHz (the sample test of
  THE CLOCK RULE, read here on its own; the registered reduction applies the rule). For each OFF process: its climb, and each run of
  off samples after its first 800 MHz sample: the first and last off sample (seconds after S), the samples in it, the time from the first
  off sample to the next sample at 800 MHz, the clocks read, the die (temp_c.minshire[0]), the latch (temp_c.minshire[2]) and the board
  (board_w). Then, per sitting: the largest and the median climb, and how many processes read 800 MHz within 0.1 s of S.
Standard library only. /usr/bin/python3 3.12.3 printed the committed output (posthoc-note1-e200.txt).
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
S1 = "2026-11-16-e200-regfile-sitting-1-aifoundry2"
S2 = "2026-11-16-e200-regfile-sitting-2-aifoundry2"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def at800(m):
    return m is not None and abs(m - 800) <= 1


def sums(d):
    rows = {}
    for ln in open(os.path.join(d, "SHA256SUMS")):
        h, p = ln.rstrip("\n").split(None, 1)
        rows[p.strip().lstrip("*")] = h
    return rows


def read(d, p, rows):
    b = open(os.path.join(d, p), "rb").read()
    if rows.get(p) != sha(b):
        raise SystemExit(f"STOP: {os.path.basename(d)}/{p} is not at its SHA256SUMS entry")
    return b


def manifest_target(mpath):
    p = mpath[2:] if mpath.startswith("./") else mpath
    if p == "run/telemetry.jsonl":
        return "run/telemetry.jsonl.gz", True
    if p.startswith("run/") or p.startswith("ref/"):
        return p, False
    return "session/" + p, False


def main(argv):
    d1 = os.path.join(HERE, "..", S1)
    d2 = HERE
    if "--data1" in argv:
        d1 = argv[argv.index("--data1") + 1]
    if "--data2" in argv:
        d2 = argv[argv.index("--data2") + 1]
    dirs = [("1", os.path.normpath(d1)), ("2", os.path.normpath(d2))]
    print("E200 data note 1, post hoc read (decides nothing)")
    print("== 0. SHA256SUMS")
    rows = {}
    for s, d in dirs:
        r = sums(d)
        ok = sum(1 for p, h in r.items() if sha(open(os.path.join(d, p), "rb").read()) == h)
        rows[s] = r
        print(f"sitting {s} ({os.path.basename(d)}): {ok} of {len(r)} entries at their sha256")
        if ok != len(r):
            raise SystemExit("STOP: a SHA256SUMS entry does not read")
    print("== 1. the box's manifest against the committed files")
    for s, d in dirs:
        lines = read(d, "session/MANIFEST.sha256", rows[s]).decode().splitlines()
        match, other = 0, []
        for ln in lines:
            h, p = ln.split(None, 1)
            p = p.strip()
            q, gz = manifest_target(p)
            b = read(d, q, rows[s])
            if gz:
                b = gzip.decompress(b)
            if sha(b) == h:
                match += 1
            else:
                other.append((p, q, h, b))
        print(f"sitting {s}: manifest lines {len(lines)}; the committed file is at the manifest's sha256 for {match}; not for {len(other)}")
        for p, q, h, b in other:
            tl = b.decode("utf-8", "replace").split("\n")
            ti = [i + 1 for i, t in enumerate(tl) if "~" in t]
            print(f"  {q}: manifest {h}, committed {sha(b)}; lines holding '~': {ti} ({b.count(b'~')} in the file)")
            for i in ti:
                print(f"    line {i}: {tl[i - 1].strip()}")
    print("== 2. the climbs and the train processes off 800 MHz after 1.5 s")
    allspans, alloff = [], []
    for s, d in dirs:
        marks = [json.loads(x) for x in read(d, "run/marks.jsonl", rows[s]).decode().splitlines() if x.strip()]
        runs = [json.loads(x) for x in read(d, "run/runs.jsonl", rows[s]).decode().splitlines() if x.strip()]
        tel = []
        for x in gzip.decompress(read(d, "run/telemetry.jsonl.gz", rows[s])).decode().splitlines():
            if not x.strip():
                continue
            r = json.loads(x)
            ms = (r.get("temp_c") or {}).get("minshire") or [None, None, None]
            tel.append((r["t_ms"], (r.get("mhz") or {}).get("minion"), ms[0], ms[2], r.get("board_w")))
        tel.sort()
        tm = [m for m in marks if m.get("kind") == "train" and m.get("block") != "smoke"]
        climbs, off = [], []
        for m in tm:
            L = [r for r in runs if r.get("block") == m["block"] and m["t0_ms"] <= r["t_start_ms"] <= m["t1_ms"]]
            S = min(r["t_start_ms"] for r in L)
            E = max(r["t_end_ms"] for r in L)
            smp = [t for t in tel if S <= t[0] <= E]
            f8 = next((t for t in smp if at800(t[1])), None)
            climbs.append(None if f8 is None else (f8[0] - S) / 1000)
            if not any(t[0] >= S + 1500 and t[1] is not None and not at800(t[1]) for t in smp):
                continue
            spans, cur = [], []
            for t in (x for x in smp if f8 is not None and x[0] > f8[0]):
                if t[1] is not None and not at800(t[1]):
                    cur.append(t)
                elif cur and at800(t[1]):
                    spans.append((cur, t))
                    cur = []
            if cur:
                spans.append((cur, None))
            off.append(m)
            alloff.append(climbs[-1])
            parts = []
            for c, back in spans:
                allspans.append((c, back, S))
                parts.append("off %.3f-%.3f s (%d samples; at 800 MHz again %s after the first), clocks %s MHz, die %s-%s C, "
                             "latch %s-%s C, board %.2f-%.2f W" % (
                                 (c[0][0] - S) / 1000, (c[-1][0] - S) / 1000, len(c),
                                 "%.3f s" % ((back[0] - c[0][0]) / 1000) if back else "not",
                                 "/".join(str(v) for v in sorted({x[1] for x in c})), min(x[2] for x in c), max(x[2] for x in c),
                                 min(x[3] for x in c), max(x[3] for x in c), min(x[4] for x in c), max(x[4] for x in c)))
            print(f"sitting {s} block {m['block']} {m['train']} process {m['proc']} ({len(L)} launches): climb "
                  + ("%.3f s" % climbs[-1] if climbs[-1] is not None else "none") + "; " + "; ".join(parts))
        cl = [c for c in climbs if c is not None]
        print(f"sitting {s}: train processes {len(tm)}; OFF {len(off)}; climb largest %.3f s, median %.3f s; at 800 MHz within "
              "0.1 s of S: %d; no sample at 800 MHz: %d" % (max(cl), statistics.median(cl), sum(1 for c in cl if c <= 0.1),
                                                            climbs.count(None)))
    print("both sittings: OFF %d; their climbs %.3f-%.3f s; off runs %d, first off sample %.3f-%.3f s after S, last %.3f-%.3f s; "
          "first to last off sample %.3f-%.3f s; die %s-%s C; latch %s-%s C; board %.2f-%.2f W" % (
              len(alloff), min(alloff), max(alloff), len(allspans),
              min((c[0][0] - S) / 1000 for c, b, S in allspans), max((c[0][0] - S) / 1000 for c, b, S in allspans),
              min((c[-1][0] - S) / 1000 for c, b, S in allspans), max((c[-1][0] - S) / 1000 for c, b, S in allspans),
              min((c[-1][0] - c[0][0]) / 1000 for c, b, S in allspans), max((c[-1][0] - c[0][0]) / 1000 for c, b, S in allspans),
              min(x[2] for c, b, S in allspans for x in c), max(x[2] for c, b, S in allspans for x in c),
              min(x[3] for c, b, S in allspans for x in c), max(x[3] for c, b, S in allspans for x in c),
              min(x[4] for c, b, S in allspans for x in c), max(x[4] for c, b, S in allspans for x in c)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
