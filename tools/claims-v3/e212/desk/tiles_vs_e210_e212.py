"""E212 (reg-e212, Q208): THE OPERAND-PATTERN RULE's byte test - every tile file of E212's proposal (src/tiles/) against every tile
file of E210's registration (tools/claims-v3/e210/tiles/), by sha256 (reads only; Python's own modules).

    /usr/bin/python3 -I -B tiles_vs_e210_e212.py <E212 proposal src dir> <E210 tiles dir>

Prints one line per E212 tile (EQUAL-TO-E210 or differs, its sha256 and length), how many are equal, and a digest of E210's tile
set: the count of its files and the sha256 of their sorted sha256 list (one hex digest a line, newline-terminated), so the same
test can be re-run against E210's tiles once they are on GitHub main and the set recognised. It prints no E210 file name: E210's
patterns are public with E210's registration.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import os
import sys


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def bins(d):
    out = []
    for root, dirs, fs in os.walk(d):
        dirs.sort()
        out += [os.path.join(root, f) for f in sorted(fs) if f.endswith(".bin")]
    return out


src, e210 = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
e10 = sorted(sha(p) for p in bins(e210))
idx = set(e10)
digest = hashlib.sha256("".join(h + "\n" for h in e10).encode()).hexdigest()
print("# E210's tile set: %d files, %d distinct sha256; sha256 of the sorted list of their sha256s: %s" % (len(e10), len(idx), digest))
e12 = bins(os.path.join(src, "tiles"))
hits = 0
for p in e12:
    h = sha(p)
    eq = h in idx
    hits += eq
    print("%s %s %5d B  %s" % ("EQUAL-TO-E210" if eq else "differs      ", h, os.path.getsize(p), os.path.relpath(p, os.path.dirname(src))))
print("E212 tile files equal byte for byte to an E210 tile file: %d of %d" % (hits, len(e12)))
