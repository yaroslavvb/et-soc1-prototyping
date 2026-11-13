#!/usr/bin/env python3
"""E191, dated note 1's checks (Q171, fix-reg191, Fri 13 Nov 2026, before any E189 or E191 datum): desk reads of committed records,
nothing measured. Standard library only. Run from the top of the tree:

    /usr/bin/python3 -I -B tools/claims-v3/e191/note1_checks_e191.py

Part 1  aifoundry1's two cards in the committed config reads (docs/reports/data/, every text file under 20 MB; .gz skipped): every
        dict carrying "tdp_w" and "minion_mv", by card, counted by (minion_mv, tdp_w, temp_threshold_c, minion_mhz) with the files
        that hold it, and power_state_name; and every 'PCIe target:' and 'Physical device ID:' line (the device layer prints them on
        a config read's stderr), by card. A path is card 1's when a path segment is 'aifoundry1-c1' or names 'card1' between
        hyphens, card 0's likewise ('aifoundry1-c0', 'card0'); every such folder is aifoundry1's (its README says so). Other paths
        are not counted. A dict that a log echoes is counted where it is found.
Part 2  E184 arm B (aifoundry1-c1, 8 Nov 2026): each telemetry file's first 5 s (t_ms - first t_ms <= 5000), its board mean, its
        shire-mean die (temp_c.minshire[0]) mean, and the residual against card 1's idle law as frozen
        (docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json idle_laws 'aifoundry1-c1': quad on 56-70 C, else the exponential
        law) at that die.
Part 3  temp_c.minshire's outer entries ([1], [2]) on card 1: samples reading (46, 65) in E137, E145 and E184 arm B, file by file,
        with the samples whose since_reset_ms is 0 or more (the statistics reset running).
Part 4  E191.md's references to E189.md by section number (the text E191 cites by content).
SPDX-License-Identifier: Apache-2.0
"""
import collections
import glob
import gzip
import json
import math
import os
import re
import statistics

DATA = "docs/reports/data"
SEG1 = re.compile(r"(?:^|/)(?:aifoundry1-c1|(?:[^/]*-)?card1(?:-[^/]*)?)(?:/|$)")
SEG0 = re.compile(r"(?:^|/)(?:aifoundry1-c0|(?:[^/]*-)?card0(?:-[^/]*)?)(?:/|$)")
DICT = re.compile(r'\{[^{}]*"tdp_w"[^{}]*\}')
TGT = re.compile(r"PCIe target:\s+(/dev/\S+)")
DID = re.compile(r"Physical device ID:\s+(\d+)")
SKIP = (".gz", ".png", ".jpg", ".jpeg", ".bin", ".elf", ".pdf", ".svg", ".so", ".o")


def card_of(rel):
    if SEG1.search(rel):
        return "card 1"
    if SEG0.search(rel):
        return "card 0"
    return None


def part1():
    print("== Part 1: aifoundry1's config reads by card (docs/reports/data)")
    keys = collections.defaultdict(collections.Counter)
    kfiles = collections.defaultdict(lambda: collections.defaultdict(set))
    pstate = collections.defaultdict(collections.Counter)
    tgt = collections.defaultdict(collections.Counter)
    tsess = collections.defaultdict(set)
    did = collections.defaultdict(collections.Counter)
    sess = collections.defaultdict(set)
    for dp, dn, fn in os.walk(DATA):
        dn.sort()
        for f in sorted(fn):
            if f.endswith(SKIP):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, DATA)
            c = card_of(rel)
            if c is None:
                continue
            try:
                if os.path.getsize(p) > 20_000_000:
                    continue
                with open(p, "rb") as fh:
                    raw = fh.read()
            except OSError:
                continue
            if b"\x00" in raw[:4096]:
                continue
            s = raw.decode("utf-8", errors="replace")
            for m in DICT.findall(s):
                try:
                    d = json.loads(m)
                except ValueError:
                    continue
                if "minion_mv" not in d:
                    continue
                k = (d.get("minion_mv"), d.get("tdp_w"), d.get("temp_threshold_c"), d.get("minion_mhz"))
                keys[c][k] += 1
                kfiles[c][k].add(rel)
                pstate[c][d.get("power_state_name")] += 1
                sess[c].add(rel.split("/")[0])
            for t in TGT.findall(s):
                tgt[c][t] += 1
                tsess[(c, t)].add(rel.split("/")[0])
            for t in DID.findall(s):
                did[c][t] += 1
    for c in ("card 0", "card 1"):
        n = sum(keys[c].values())
        nf = len(set().union(*kfiles[c].values())) if kfiles[c] else 0
        print(f"{c}: {n} config dicts in {nf} files, {len(sess[c])} session folders: {', '.join(sorted(sess[c]))}")
        for k, v in sorted(keys[c].items(), key=lambda kv: (-kv[1], str(kv[0]))):
            print(f"   minion_mv {k[0]}, tdp_w {k[1]}, temp_threshold_c {k[2]}, minion_mhz {k[3]}: {v} dicts in {len(kfiles[c][k])} files")
        mvs = sorted({k[0] for k in keys[c]})
        print(f"   minion_mv values: {mvs}")
        print(f"   power_state_name: {dict(sorted(pstate[c].items(), key=lambda kv: str(kv[0])))}")
        for t, v in sorted(tgt[c].items()):
            print(f"   'PCIe target: {t}' x{v} in {len(tsess[(c, t)])} session folders: {', '.join(sorted(tsess[(c, t)]))}")
        print(f"   'Physical device ID': {dict(sorted(did[c].items()))}")
        if c == "card 1":
            for k in sorted(kfiles[c], key=str):
                if k[0] != 499:
                    print(f"   files holding minion_mv {k[0]}: {', '.join(sorted(kfiles[c][k]))}")
    print()


def law():
    with open(os.path.join(DATA, "2026-11-12-q166-ledger-v2/frozen-v2.json")) as fh:
        L = json.load(fh)["idle_laws"]["aifoundry1-c1"]

    def p(t):
        lo, hi = L["quad_band_c"]
        if lo <= t <= hi:
            q = L["quad"]
            return q["a"] * t * t + q["b"] * t + q["c"]
        e = L["exp"]
        return e["B"] + e["A80"] * math.exp((t - 80.0) / e["T_L"])
    return p


def rows_of(f):
    out = []
    with gzip.open(f, "rt") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln.startswith("{"):
                continue
            try:
                d = json.loads(ln)
            except ValueError:
                continue
            out.append((d.get("t_ms"), d.get("board_w"), (d.get("temp_c") or {}).get("minshire"), d.get("since_reset_ms")))
    return out


E184B = os.path.join(DATA, "2026-11-08-e184-sensor-validation/raw/aifoundry1-c1/**/telemetry.jsonl.gz")


def part2():
    p = law()
    print("== Part 2: E184 arm B, each telemetry file's first 5 s (idle), against card 1's law as frozen")
    print(f"   the law: P(54) {p(54):.3f} W, P(55) {p(55):.3f} W, P(56) {p(56):.3f} W, P(57) {p(57):.3f} W")
    per = []
    for f in sorted(glob.glob(E184B, recursive=True)):
        r = rows_of(f)
        t0 = r[0][0]
        hd = [x for x in r if x[0] is not None and x[0] - t0 <= 5000 and x[1] is not None and x[2]]
        b = statistics.mean(x[1] for x in hd)
        dm = statistics.mean(x[2][0] for x in hd)
        per.append((t0, os.path.basename(os.path.dirname(f)), b, dm, len(hd), b - p(dm)))
    for t0, name, b, dm, n, res in sorted(per):
        print(f"   {name}: board {b:.2f} W, die {dm:.2f} C ({n} samples); the law there {p(dm):.2f} W; residual {res:+.2f} W")
    bs = [x[2] for x in per]
    print(f"   first-5-s board means {min(bs):.2f}-{max(bs):.2f} W, at one decimal {min(bs):.1f}-{max(bs):.1f} W; "
          f"the largest |residual| {max(abs(x[5]) for x in per):.2f} W")
    print()


def part3():
    print("== Part 3: temp_c.minshire's outer entries on card 1 reading (46, 65)")
    sets = [("E137", "2026-11-02-e137-fp16-sign-rest/aifoundry1-c1/**/telemetry.jsonl.gz"),
            ("E145", "2026-11-02-e145-int8-b-card1/aifoundry1-c1/**/telemetry.jsonl.gz"),
            ("E184 arm B", "2026-11-08-e184-sensor-validation/raw/aifoundry1-c1/**/telemetry.jsonl.gz")]
    for name, pat in sets:
        files = sorted(glob.glob(os.path.join(DATA, pat), recursive=True))
        tot = hit = 0
        per = []
        for f in files:
            r = rows_of(f)
            n = sum(1 for x in r if x[2] and len(x[2]) >= 3)
            k = sum(1 for x in r if x[2] and len(x[2]) >= 3 and (x[2][1], x[2][2]) == (46, 65))
            rs = sum(1 for x in r if x[3] is not None and x[3] >= 0)
            tot += n
            hit += k
            per.append((r[0][0] if r else 0, os.path.basename(os.path.dirname(f)), k, n, rs))
        print(f"   {name}: {len(files)} files; (46, 65) in {hit} of {tot} samples")
        if name == "E184 arm B":
            for t0, fn, k, n, rs in sorted(per):
                print(f"      {fn} (in the session's order): (46, 65) in {k} of {n}; since_reset_ms 0 or more in {rs}")
    print()


def part4():
    print("== Part 4: E191.md's references to E189.md by section")
    with open("tools/claims-v3/e191/E191.md") as fh:
        s = fh.read()
    refs = collections.Counter(re.findall(r"E189\.md (\d+(?:\.\d+)?)", s))
    print(f"   {sum(refs.values())} references to {len(refs)} sections: "
          + ", ".join(f"{k} x{v}" for k, v in sorted(refs.items(), key=lambda kv: [int(x) for x in kv[0].split('.')])))
    print()


if __name__ == "__main__":
    print("E191 dated note 1's checks: desk reads of committed records (nothing measured)")
    print()
    part1()
    part2()
    part3()
    part4()
    print("NOTE1 CHECKS DONE")
