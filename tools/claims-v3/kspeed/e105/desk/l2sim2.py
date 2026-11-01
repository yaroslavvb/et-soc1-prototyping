#!/usr/bin/env python3
# Verifier: the rest of the layouts, lighter, plus a one-shot launch from a cold L2 (the vendor's kernel as generated runs one pass per launch and has empty prefetchers).
import collections, random

MASK = (1 << 11) - 1
WAYS = 4


def port_a(A0, row, k, i):
    return A0 + (row * 32 + k) * 1024 + i * 64


def port_b(B0, k, col, i):
    return B0 + (k * 32 + col) * 1024 + i * 64


def vend_a(A0, row, k, i):
    return A0 + (row * 16 + i) * 2048 + k * 64


def vend_b(B0, k, col, i):
    return B0 + (k * 16 + i) * 2112 + col * 64


def col_b(B0, k, col, i):  # the one edit: B packed by column
    return B0 + (col * 32 + k) * 1024 + i * 64


def half_a(A0, row, k, i):  # a block that fits with room: 16 k tiles instead of 32, repeated
    return A0 + (row * 32 + (k % 16)) * 1024 + i * 64


def half_b(B0, k, col, i):
    return B0 + (col * 32 + (k % 16)) * 1024 + i * 64


def sweep(fa, fb, A0, B0, s0, s1):
    seq = []
    for r in range(2):
        for k in range(32):
            tiles = [("A", fa, s1 * 8 + d * 2 + r, k) for d in range(4)] + [("B", fb, k, s0 * 8 + p) for p in range(8)]
            for i in range(16):
                for name, f, x, y in tiles:
                    seq.append((name, (f(A0 if name == "A" else B0, x, y, i)) >> 6))
    return seq


def run(seq, passes):
    sets = collections.defaultdict(list)
    res = None
    for _ in range(passes):
        m = collections.Counter()
        n = collections.Counter()
        for name, line in seq:
            s = sets[line & MASK]
            n[name] += 1
            if line in s:
                s.remove(line)
                s.append(line)
            else:
                m[name] += 1
                if len(s) >= WAYS:
                    s.pop(0)
                s.append(line)
        res = (m, n)
    return res


rng = random.Random(11)
print("%-26s %-16s %7s %7s %7s  (mean over 2 base pairs x 2 shires; A: 4 tiles/op, B: 8 tiles/op; 192 lines/op)" % ("layout", "mode", "A miss", "B miss", "all"))
for name, fa, fb in (("port (packed, as run)", port_a, port_b), ("vendor strides", vend_a, vend_b), ("packed, B by column", port_a, col_b), ("half K, B by column", half_a, half_b)):
    for mode, passes in (("steady, repeated", 3), ("one pass, cold", 1)):
        ta, tb, tt = [], [], []
        for _ in range(2):
            A0 = rng.randrange(0, 1 << 16) * 4096
            B0 = rng.randrange(0, 1 << 16) * 4096
            for s0, s1 in ((0, 0), (2, 5)):
                seq = sweep(fa, fb, A0, B0, s0, s1)
                m, n = run(seq, passes)
                ta.append(m["A"] / n["A"])
                tb.append(m["B"] / n["B"])
                tt.append((m["A"] + m["B"]) / (n["A"] + n["B"]))
        print("%-26s %-16s %6.1f%% %6.1f%% %6.1f%%" % (name, mode, 100 * sum(ta) / len(ta), 100 * sum(tb) / len(tb), 100 * sum(tt) / len(tt)))
