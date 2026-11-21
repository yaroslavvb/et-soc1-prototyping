#!/usr/bin/env python3
"""mask-mesh (Q238, track M): THE MECHANISM, as code with no fitted constant. For rgm136's cooperative gemmL loop at any shire mask:
the active shires' tile request stream (MM1-v3.1's walk, tools/matmul/mm1/v3.1/walk/walk_v31.py chip_steps, re-made here tile for tile and
checked against it by test_mesh_l3.py) run through TWO models of the chip's L3, and the active shires' places on the mesh.

THE L3 (32 slices of 1 MiB, one a compute shire):
  SA  the L3 as the shire cache specification decodes it (the lab's memory-levels report, 2026-09-28, l3.decode and l2.partition.rows;
      default swizzle0): a 64 B line's home slice is PA[10:6], within the slice its bank PA[12:11], sub-bank PA[14:13] and set PA[22:15]
      (256 L3 sets a sub-bank in Mode 0, 4 ways). So two lines compete for the same 4 ways iff PA[22:6] are equal: the L3 is 4-way set
      associative over 131,072 sets with an 8 MiB aliasing period. A 1 KiB tile (16 lines, PA[9:6] = 0..15) puts its 16 lines in 16 homes
      at ONE set index PA[22:11] and one PA[10]: tiles compete iff their tile index (PA >> 10) agrees mod 8,192. Replacement: LRU (ASSUMED).
  FA  the walk's own convention: one fully associative strict LRU over 1 KiB tiles at 32 MiB (MM1's retention laws are of this kind).
  Both see the same stream: per lock step every distinct A and B tile the active shires ask (a tile asked by w shires is one request, the
  others in flight), then each row half's C TensorStores (they allocate, as the walk's convention says); two passes, the second scored.
THE ADDRESSES: pool-relative offsets are the walk's (A (mb KB + kb) 2 MiB + (row 32 + k) 1 KiB; B (kb NB + nb) 1 MiB + (col 32 + k) 1 KiB;
  C (mb NB + nb) 2 MiB + (row 32 + col) 1 KiB). THE POOL BASES (KNOWN for the simulator, ASSUMED for the card): in every traced sys_emu run
  (walk/traces/runs/*/check.json) the host's pools sit back to back, C first, then A, then B: A0 = C0 + 2 MiB MB NB, B0 = A0 + 2 MiB MB KB
  (2x4x16: C 0x8005b3a000, A +16 MiB, B +64 MiB; 1x1x16: A +2 MiB, B +32 MiB). The card's host runs the same runtime allocator; only the
  relative offsets matter here (a common shift of the three pools permutes the sets).
THE MESH (KNOWN, docs/et-soc1-notes.md): the 32 compute shires on marty1885's map (MARTY), memory shires 0-3 at (1-4, -1), 4-7 at (1-4, 6);
  an L3 hit costs 110 + 12 x hops(requester, home) cycles, home = PA[10:6]; the DRAM leg 91 + 12 x hops(home, memory shire PA[8:6]).
  Lines interleave uniformly over the 32 homes, so a shire's mean L3 latency is L(s) = 110 + 12 hbar(s), hbar = its mean hop to the homes.
  ROUTES (ASSUMED, for the REPORTED link loads only): dimension order X then Y on that map.
Standard library only; /usr/bin/python3 3.12.3. SPDX-License-Identifier: Apache-2.0
"""
import collections
import json
import re
import sys

KT, NT = 32, 32
NSETS, WAYS = 8192, 4               # tile-sets (PA[22:10]) x 4 ways = 32 MiB
FA_TILES = 32768                    # 32 MiB of 1 KiB tiles
BASE_C = 0x8005b3a000 >> 10         # the traced C pool base, in KiB (any common shift is equivalent)
GEMML = re.compile(r'gemmL(\d+)x(\d+)x(\d+)$')
FULL = 0xffffffff

MARTY = {
    0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0),
    8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1), 10: (4, 1), 19: (5, 1),
    3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2),
    12: (1, 3), 21: (2, 3), 22: (3, 3), 26: (4, 3),
    20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4),
    28: (1, 5), 5: (2, 5), 6: (3, 5), 7: (4, 5), 31: (5, 5),
}
MEM = {m: (1 + (m % 4), -1 if m < 4 else 6) for m in range(8)}


def hops(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


HBAR = {s: sum(hops(MARTY[s], MARTY[h]) for h in range(32)) / 32.0 for s in range(32)}      # mean hop to the 32 homes
L3LAT = {s: 110.0 + 12.0 * HBAR[s] for s in range(32)}                                         # cycles, the lab's L3 law
HMEM = sum(hops(MARTY[h], MEM[h & 7]) for h in range(32)) / 32.0                              # mean home -> memory-shire hop
L3LAT_FULL = sum(L3LAT.values()) / 32.0


def shape(arm):
    m = GEMML.match(arm)
    if not m:
        raise ValueError(arm)
    return tuple(int(x) for x in m.groups())


def mask_shires(mask):
    m = int(mask, 16) if isinstance(mask, str) else int(mask)
    return [s for s in range(32) if (m >> s) & 1]


def pools(MB, NB, KB):
    """(A0, B0, C0) in KiB: C first, then A, then B, back to back (the traced allocator)"""
    C0 = BASE_C
    A0 = C0 + 2048 * MB * NB
    B0 = A0 + 2048 * MB * KB
    return A0, B0, C0


def stream(MB, NB, KB, mask):
    """the walk's chip stream in tile ids (KiB), one pass: yields ('A', tile, row group) / ('B', tile, column group) per lock step in the
    walk's order (A list: row groups sorted, d = 0..3; then B list: column groups sorted, p = 0..7), then ('C', tile, None) after each row half"""
    sh = mask_shires(mask)
    shs = set(sh)
    R = sorted({(s >> 2) & 7 for s in sh})
    Cg = sorted({s & 3 for s in sh})
    A0, B0, C0 = pools(MB, NB, KB)
    for mb in range(MB):
        for nb in range(NB):
            for r in range(2):
                for kb in range(KB):
                    ab = A0 + (mb * KB + kb) * 2048
                    bb = B0 + (kb * NB + nb) * 1024
                    for k in range(KT):
                        for g in R:
                            for d in range(4):
                                yield 'A', ab + (g * 8 + 2 * d + r) * KT + k, g
                        for g in Cg:
                            for p in range(8):
                                yield 'B', bb + (g * 8 + p) * KT + k, g
                cb = C0 + (mb * NB + nb) * 2048
                for q in range(32):
                    for c in range(NT):
                        if 4 * (q // 4) + c // 8 in shs:
                            yield 'C', cb + (2 * q + r) * NT + c, None


def simulate(MB, NB, KB, mask, passes=2):
    """both L3 models over the stream; the last pass tallied per operand and group: requests, SA misses, FA misses"""
    sa = [[] for _ in range(NSETS)]
    fa = collections.OrderedDict()
    tal = {'A': collections.defaultdict(lambda: [0, 0, 0]), 'B': collections.defaultdict(lambda: [0, 0, 0]), 'C': collections.defaultdict(lambda: [0, 0, 0])}
    # the stream is the same every pass: generated afresh each pass (no list kept, so the largest shapes stay small in memory)
    nreq = 0
    for p in range(passes):
        rec = p == passes - 1
        for op, t, g in stream(MB, NB, KB, mask):
            nreq += rec
            L = sa[t & (NSETS - 1)]
            if t in L:
                hs = True
                if L[0] != t:
                    L.remove(t)
                    L.insert(0, t)
            else:
                hs = False
                L.insert(0, t)
                if len(L) > WAYS:
                    L.pop()
            if t in fa:
                hf = True
                fa.move_to_end(t)
            else:
                hf = False
                fa[t] = None
                if len(fa) > FA_TILES:
                    fa.popitem(last=False)
            if rec:
                x = tal[op][g]
                x[0] += 1
                x[1] += (not hs)
                x[2] += (not hf)
    return {op: {str(g): v for g, v in d.items()} for op, d in tal.items()}, nreq


def features(arm, mask, sim=None, sim_full=None):
    """per configuration, from the two L3 models and the map: per active shire its A and B miss shares (SA, FA), the laggard s* (most SA misses
    per request, then the largest hbar, then the lowest id), and the chip's shares"""
    MB, NB, KB = shape(arm)
    sh = mask_shires(mask)
    if sim is None:
        sim, _ = simulate(MB, NB, KB, mask)

    def per_shire(sim, sh):
        out = {}
        for s in sh:
            a = sim['A'][str((s >> 2) & 7)]
            b = sim['B'][str(s & 3)]
            out[s] = {'xA_SA': a[1] / a[0], 'xB_SA': b[1] / b[0], 'xA_FA': a[2] / a[0], 'xB_FA': b[2] / b[0]}
        return out

    def chip(sim):
        def tot(op, j):
            return sum(v[j] for v in sim[op].values())
        return {'A_SA': tot('A', 1) / tot('A', 0), 'B_SA': tot('B', 1) / tot('B', 0), 'A_FA': tot('A', 2) / tot('A', 0),
                'B_FA': tot('B', 2) / tot('B', 0), 'reqA': tot('A', 0), 'reqB': tot('B', 0), 'reqC': tot('C', 0),
                'C_SA_miss': tot('C', 1), 'C_FA_miss': tot('C', 2)}

    ps = per_shire(sim, sh)
    lag = max(sh, key=lambda s: (round(ps[s]['xA_SA'] + ps[s]['xB_SA'], 12), HBAR[s], -s))
    out = {'arm': arm, 'mask': '0x%x' % int(mask, 16) if isinstance(mask, str) else '0x%x' % mask, 'n': len(sh),
           'R': len({s >> 2 for s in sh}), 'C': len({s & 3 for s in sh}), 'per_shire': {str(s): v for s, v in ps.items()},
           'laggard': lag, 'chip': chip(sim),
           'hbar_mean': sum(HBAR[s] for s in sh) / len(sh), 'hbar_max': max(HBAR[s] for s in sh), 'hbar_lag': HBAR[lag],
           'L3lat_mean': sum(L3LAT[s] for s in sh) / len(sh), 'L3lat_lag': L3LAT[lag],
           'hmem_mean': sum(min(hops(MARTY[s], MEM[m]) for m in range(8)) for s in sh) / len(sh),
           'collide_share': sum(1 for s in sh if ((s >> 2) & 3) == (s & 3)) / len(sh)}
    out.update(link_loads(sh))
    return out


# ---------------------------------------------------------------------------------------------------------- REPORTED: link loads (XY)
def xy_path(a, b):
    """directed links from a to b, X first then Y (ASSUMED routing)"""
    (x, y), (x1, y1) = a, b
    links = []
    while x != x1:
        nx = x + (1 if x1 > x else -1)
        links.append(((x, y), (nx, y)))
        x = nx
    while y != y1:
        ny = y + (1 if y1 > y else -1)
        links.append(((x, y), (x, ny)))
        y = ny
    return links


_PATH = {}


def path(a, b):
    k = (a, b)
    if k not in _PATH:
        _PATH[k] = xy_path(a, b)
    return _PATH[k]


def link_loads(sh):
    """per op step each active shire takes one line from each of the 32 homes (uniform interleave): the response load on every directed link
    (XY), its largest value, and the largest value over the links into each active shire; per shire (divided by the active count)"""
    load = collections.Counter()
    for s in sh:
        for h in range(32):
            if h == s:
                continue
            for ln in path(MARTY[h], MARTY[s]):
                load[ln] += 1
    mx = max(load.values()) if load else 0
    return {'link_max_resp': mx, 'link_max_resp_per_shire': mx / len(sh), 'links_used': len(load)}


if __name__ == '__main__':
    arm, mask = sys.argv[1], sys.argv[2]
    MB, NB, KB = shape(arm)
    sim, n = simulate(MB, NB, KB, mask)
    print(json.dumps(features(arm, mask, sim), indent=1))
