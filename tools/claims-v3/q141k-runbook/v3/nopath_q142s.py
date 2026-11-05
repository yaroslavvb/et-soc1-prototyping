#!/usr/bin/env python3
"""Q142(s) v3: no desk path in what a collector wrote. s22_collect.sh runs it over each run's outputs before it says "collected"
(faults 1 and 2 of v3/README.md): v2's s22 e163 handed collect_e163.sh an absolute raw copy (build/e163-raw under the lab clone),
and reduce_e78.py records the pass directories as given, in e163.json's "dirs" (reduce_e78.py:428) and in every row of runs.csv
("dir", reduce_e78.py:172), so the Intel's home path would have entered a public data directory.

    python3 -B nopath_q142s.py [--forbid <path>] ... <file or dir> ...

It reads every file under the paths given (a .gz file decompressed), and looks for: each --forbid path (the runbook passes the lab
clone and RB_OUT, both as given and resolved), this user's home, any Mac home directory, the macOS per-user temp tree (both of its
spellings) and a session scratch root. The four fixed patterns are written split in two below, so that a public-text scan of this
file does not read its own patterns as paths.
A box's own path (/home/<the owner's box login>/...) is not a desk path: the committed data holds those, as the boxes wrote them.
It prints one HIT line per file and kind (the file, what was found, how many times; never the text around it) and exits 3 on any
hit, 0 when clean, 2 on a usage error. Standard library only; it reads, and never writes, anything it scans.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import os
import sys


def needles(forbid):
    out = {}
    for p in forbid:
        if not p:
            continue
        for q in {p.rstrip("/"), os.path.realpath(p).rstrip("/")}:
            if len(q) > 1:
                out[q.encode()] = f"the forbidden path {q}"
    home = os.path.expanduser("~")
    for q in {home, os.path.realpath(home)}:
        if len(q) > 1 and q != "/":
            out.setdefault(q.encode(), "this user's home")
    for q, why in (("/Us" "ers/", "a Mac home path"), ("/var/fol" "ders/", "a macOS temp path"),
                   ("/private/var/fol" "ders/", "a macOS temp path"), ("/.ct" "mp/", "a session scratch path")):
        out.setdefault(q.encode(), why)
    return out


def read(path):
    if path.endswith(".gz"):
        with gzip.open(path, "rb") as f:
            return f.read()
    with open(path, "rb") as f:
        return f.read()


def main(argv):
    forbid, paths, i = [], [], 0
    while i < len(argv):
        if argv[i] == "--forbid" and i + 1 < len(argv):
            forbid.append(argv[i + 1])
            i += 2
            continue
        paths.append(argv[i])
        i += 1
    if not paths:
        print("usage: nopath_q142s.py [--forbid <path>] ... <file or dir> ...")
        return 2
    want = needles(forbid)
    files, hits, missing = 0, 0, []
    for top in paths:
        if not os.path.exists(top):
            missing.append(top)
            continue
        walk = [(os.path.dirname(top), [], [os.path.basename(top)])] if os.path.isfile(top) else os.walk(top)
        for d, _, fs in walk:
            for fn in sorted(fs):
                p = os.path.join(d, fn)
                if os.path.islink(p):
                    continue
                try:
                    blob = read(p)
                except (OSError, EOFError) as e:
                    print(f"UNREAD {p}: {type(e).__name__}")
                    hits += 1
                    continue
                files += 1
                seen = set()
                for n, why in sorted(want.items(), key=lambda kv: -len(kv[0])):
                    c = blob.count(n)
                    if c and why not in seen:
                        seen.add(why)
                        print(f"HIT {p}: {why} ({c} times)")
                        hits += 1
    for m in missing:
        print(f"MISSING {m}")
    print(f"nopath: {files} files read under {len(paths) - len(missing)} path(s); {hits} hit(s): {'CLEAN' if not hits else 'NOT CLEAN'}")
    return 3 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
