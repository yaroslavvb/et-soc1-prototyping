#!/usr/bin/env python3
# Verifier's desk check for E101 (a): does one gemm1 block fit the shire's L2 in the port's packed layout, and in the vendor's strided layout?
# L2 geometry: CORE-ET-Shire-Cache-Specification, Table 4 and Table 7 (mode 0: 128 sets per sub-bank, 4 ways, 4 banks, 4 sub-banks, 512 KB) and
# section 1.4.1.1: offset 5:0, bank 7:6, sbank 9:8, set 19:10 masked to 7 bits (16:10). So address bits 16:6 pick one of 2,048 sets of 4 ways, true LRU (2.14.4).
# Access pattern: one shire's distinct lines (coop: 4 A tiles, 8 B tiles per op), r = 0,1, k = 0..31, cyclic. TensorStore is a WriteAround: not allocated in L2 data (spec 3.5).
import random, collections, sys

IDXBITS = 11
WAYS = 4
LINE = 64


def port_a(A0, row, k, i):
    return A0 + (row * 32 + k) * 1024 + i * 64


def port_b(B0, k, col, i):
    return B0 + (k * 32 + col) * 1024 + i * 64


def vend_a(A0, row, k, i):
    return A0 + (row * 16 + i) * 2048 + k * 64


def vend_b(B0, k, col, i):
    return B0 + (k * 16 + i) * 2112 + col * 64


def sweep(fa, fb, A0, B0, s0, s1, order):
    seq = []
    for r in range(2):
        for k in range(32):
            tiles = [("A", fa, s1 * 8 + dim1 * 2 + r, k) for dim1 in range(4)] + [("B", fb, k, s0 * 8 + p) for p in range(8)]
            if order == "tile":
                for name, f, x, y in tiles:
                    base = A0 if name == "A" else B0
                    for i in range(16):
                        seq.append((name, f(base, x, y, i)))
            else:  # line by line across the tiles, as concurrent loads would interleave
                for i in range(16):
                    for name, f, x, y in tiles:
                        base = A0 if name == "A" else B0
                        seq.append((name, f(base, x, y, i)))
    return seq


def simulate(seq, passes=5, ways=WAYS, idxbits=IDXBITS):
    sets = collections.defaultdict(list)
    res = None
    mask = (1 << idxbits) - 1
    for p in range(passes):
        m = collections.Counter()
        n = collections.Counter()
        for name, a in seq:
            line = a >> 6
            s = sets[line & mask]
            n[name] += 1
            if line in s:
                s.remove(line)
                s.append(line)
            else:
                m[name] += 1
                if len(s) >= ways:
                    s.pop(0)
                s.append(line)
        res = (m, n)
    return res


def occupancy(seq, idxbits=IDXBITS):
    mask = (1 << idxbits) - 1
    per = collections.defaultdict(set)
    for name, a in seq:
        per[(a >> 6) & mask].add(a >> 6)
    c = collections.Counter(len(v) for v in per.values())
    return dict(sorted(c.items())), len(per), sum(len(v) for v in per.values())


def main():
    rng = random.Random(132)
    print("L2: 2,048 sets (address bits 16:6), 4 ways, LRU. One shire's distinct lines of one block. Bases random, 4 KB aligned.")
    print("%-8s %-5s %-4s %8s %8s %8s %8s  lines-per-set histogram (lines: count of sets) [sets used, distinct lines]" % ("layout", "order", "shr", "A miss", "B miss", "all", "lines/op", ))
    for layout, fa, fb in (("port", port_a, port_b), ("vendor", vend_a, vend_b)):
        for order in ("line", "tile"):
            tot = []
            for trial in range(6):
                A0 = rng.randrange(0, 1 << 16) * 4096
                B0 = rng.randrange(0, 1 << 16) * 4096
                for s0, s1 in ((0, 0), (1, 3), (2, 5), (3, 7)):
                    seq = sweep(fa, fb, A0, B0, s0, s1, order)
                    m, n = simulate(seq)
                    tot.append((m["A"] / n["A"], m["B"] / n["B"], (m["A"] + m["B"]) / (n["A"] + n["B"]), (m["A"] + m["B"]) / 64))
                    if trial == 0 and (s0, s1) == (0, 0):
                        occ = occupancy(seq)
            am = sum(t[0] for t in tot) / len(tot)
            bm = sum(t[1] for t in tot) / len(tot)
            al = sum(t[2] for t in tot) / len(tot)
            lo = sum(t[3] for t in tot) / len(tot)
            print("%-8s %-5s %-4d %7.1f%% %7.1f%% %7.1f%% %8.1f  %s" % (layout, order, len(tot), 100 * am, 100 * bm, 100 * al, lo, occ))
    # mm16 for contrast: 16 tile pairs contiguous, A and B pools
    print()
    A0 = 0x10000000
    B0 = 0x10004000
    seq = []
    for t in range(16):
        for i in range(16):
            seq.append(("A", A0 + t * 1024 + i * 64))
            seq.append(("B", B0 + t * 1024 + i * 64))
    m, n = simulate(seq)
    print("mm16, 16 pairs: A miss %.1f%% B miss %.1f%%, occupancy %s" % (100 * m["A"] / n["A"], 100 * m["B"] / n["B"], occupancy(seq)))
    # How the port's B tiles land: the offsets of one shire's B tiles in the 128 KB way.
    offs = sorted({(((k * 32 + c) * 1024) % (128 * 1024)) // 1024 for k in range(32) for c in range(8)})
    print("port: B tile offsets (KB) within a 128 KB way, shire s0=0:", offs, "->", len(offs), "KB of 128 KB")
    # What a fix would do: packed tiles with the vendor's pitch logic. E.g. B tile lines strided by 33 lines, A packed.
    print()
    print("Variants: port A with vendor B; vendor A with port B")
    for name, fa, fb in (("portA+vendB", port_a, vend_b), ("vendA+portB", vend_a, port_b)):
        tot = []
        for trial in range(6):
            A0 = rng.randrange(0, 1 << 16) * 4096
            B0 = rng.randrange(0, 1 << 16) * 4096
            for s0, s1 in ((0, 0), (1, 3), (2, 5), (3, 7)):
                seq = sweep(fa, fb, A0, B0, s0, s1, "line")
                m, n = simulate(seq)
                tot.append((m["A"] / n["A"], m["B"] / n["B"], (m["A"] + m["B"]) / (n["A"] + n["B"])))
        print("%-12s A %.1f%% B %.1f%% all %.1f%%" % (name, 100 * sum(t[0] for t in tot) / len(tot), 100 * sum(t[1] for t in tot) / len(tot), 100 * sum(t[2] for t in tot) / len(tot)))


if __name__ == "__main__":
    main()


def port_b_colmajor(B0, k, col, i):   # one edit: B packed by column, so one column group's tiles are contiguous
    return B0 + (col * 32 + k) * 1024 + i * 64


def half_block_a(A0, row, k, i):      # a block that fits: half the k range, 16 k tiles, A and B each 128 KB per shire
    return A0 + (row * 16 + (k % 16)) * 1024 + i * 64


def half_block_b(B0, k, col, i):
    return B0 + ((k % 16) * 32 + col) * 1024 + i * 64


print()
print("One-edit variants of the port (line order):")
rng = random.Random(7)
for name, fa, fb in (("port A + B column-major", port_a, port_b_colmajor), ("half K, port's B order", half_block_a, half_block_b)):
    tot = []
    for trial in range(6):
        A0 = rng.randrange(0, 1 << 16) * 4096
        B0 = rng.randrange(0, 1 << 16) * 4096
        for s0, s1 in ((0, 0), (1, 3), (2, 5), (3, 7)):
            seq = sweep(fa, fb, A0, B0, s0, s1, "line")
            m, n = simulate(seq)
            occ = occupancy(seq)
            tot.append((m["A"] / n["A"], m["B"] / n["B"], (m["A"] + m["B"]) / (n["A"] + n["B"])))
    print("%-26s A %.1f%% B %.1f%% all %.1f%%  occupancy %s" % (name, 100 * sum(t[0] for t in tot) / len(tot), 100 * sum(t[1] for t in tot) / len(tot), 100 * sum(t[2] for t in tot) / len(tot), occ))
