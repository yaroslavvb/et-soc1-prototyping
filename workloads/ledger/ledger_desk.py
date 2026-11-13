#!/usr/bin/env python3
"""The ledger programs' desk side: the inputs' generator (host/main.cpp's, mirrored) and the SHA-256 digests
computed on the desk with Python's hashlib, independent of the host's and the kernel's own SHA-256.

  ledger_desk.py digests --seed S --block B --repeat R --participants P --out FILE
      one line per participant, "p hex": SHA-256 of its B-byte block repeated R times (the host's --expect FILE)
  ledger_desk.py compare --want FILE --got FILE
      every participant of --want against a --digests-out FILE of a run: prints MATCH n/n or the first difference
  ledger_desk.py keys --seed S --keys N --participant p [--order sorted|shuffled]
      one participant's sort input, for a hand check

Generator: s = seed ^ tag * 0xA0761D6478BD642F ^ (p + 1) * 0xE7037ED1A0B428DB (mod 2^64), then splitmix64; tag 1 the
copy's random source, 2 a SHA-256 block (little-endian 8-byte words), 3 sort keys (top 32 bits), 4 the shuffle.

Desk only: no device. Standard library only; run with python3 -I -B. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import struct
import sys

M64 = (1 << 64) - 1


def stream_seed(seed, tag, p):
    return (seed ^ ((tag * 0xA0761D6478BD642F) & M64) ^ (((p + 1) * 0xE7037ED1A0B428DB) & M64)) & M64


def splitmix64(state):
    """Returns (output, new state)."""
    state = (state + 0x9E3779B97F4A7C15) & M64
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31), state


def words(seed, tag, p, n):
    s = stream_seed(seed, tag, p)
    out = []
    for _ in range(n):
        x, s = splitmix64(s)
        out.append(x)
    return out


def block_bytes(seed, p, block):
    return struct.pack("<%dQ" % (block // 8), *words(seed, 2, p, block // 8))


def keys(seed, n, p, order):
    k = sorted(x >> 32 for x in words(seed, 3, p, n))
    if order == "shuffled":
        s = stream_seed(seed, 4, p)
        for i in range(n - 1, 0, -1):
            x, s = splitmix64(s)
            j = x % (i + 1)
            k[i], k[j] = k[j], k[i]
    return k


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("digests")
    d.add_argument("--seed", type=lambda x: int(x, 0), default=1)
    d.add_argument("--block", type=int, required=True)
    d.add_argument("--repeat", type=int, required=True)
    d.add_argument("--participants", type=int, required=True)
    d.add_argument("--out", required=True)
    c = sub.add_parser("compare")
    c.add_argument("--want", required=True)
    c.add_argument("--got", required=True)
    k = sub.add_parser("keys")
    k.add_argument("--seed", type=lambda x: int(x, 0), default=1)
    k.add_argument("--keys", type=int, required=True)
    k.add_argument("--participant", type=int, required=True)
    k.add_argument("--order", default="shuffled", choices=["sorted", "shuffled"])
    a = ap.parse_args(argv)
    if a.cmd == "digests":
        if a.block % 64:
            sys.exit("--block: a multiple of 64")
        with open(a.out, "w") as f:
            for p in range(a.participants):
                h = hashlib.sha256()
                blk = block_bytes(a.seed, p, a.block)
                for _ in range(a.repeat):
                    h.update(blk)
                f.write("%d %s\n" % (p, h.hexdigest()))
        print("DIGESTS %d participants -> %s" % (a.participants, a.out))
        return 0
    if a.cmd == "compare":
        def read(path):
            return dict(line.split() for line in open(path) if line.strip())
        want, got = read(a.want), read(a.got)
        bad = [p for p in want if got.get(p) != want[p]]
        extra = sorted(set(got) - set(want))
        if bad or extra:
            print("DIFFER: %d of %d; first %s; %d extra" % (len(bad), len(want), bad[:1], len(extra)))
            return 1
        print("MATCH %d/%d" % (len(want), len(want)))
        return 0
    print(" ".join(str(x) for x in keys(a.seed, a.keys, a.participant, a.order)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
