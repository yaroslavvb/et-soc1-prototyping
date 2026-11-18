#!/usr/bin/env python3
"""MM1-v3.1's masked walk (Q217, lane v31-trace): the subset walk of the lab's two matmul kernels at any shire mask, as code with NO
fitted constant, read from the kernels' sources. Desk: a model of the kernels' own addresses and order; checked against traced sys_emu
runs by check_v31.py (traces/). Standard library only; /usr/bin/python3 3.12.3.

    python3 -I -B walk_v31.py summary <kernel> <MB>x<NB>x<KB> <mask> [--l2] [--l3-cap-mb 32]   the walk's per-shire and chip numbers (JSON)
    python3 -I -B walk_v31.py minion  <kernel> <MB>x<NB>x<KB> <mask> <shire> <minion>        one minion's event list (JSON lines)

KERNELS (sources: tools/claims-v3/e136/rgm136/kernel/sparsity.c run_gemm_large; tools/claims-v3/e211/rgm211/kernel/sparsity.c
run_gemm_large_nm; the hosts' testArm and Session::launch):
  rgm136.gemmL    rgm136's ELF, cooperative loads, the C blocks mb outer, nb inner ('mn')            (E136-E212's kernel)
  rgm136.gemmLnc  rgm136's ELF, its non-cooperative branch (coop 0: every minion loads for itself), 'mn' (E211's gemmLnc, rgm211's host)
  rgm211.gemmLn   rgm211's ELF, cooperative loads, the C blocks nb outer, mb inner ('nm')             (E211's second kernel)
  rgm211.gemmL    rgm211's ELF built from rgm136's text, cooperative, 'mn' (rgm211's own gemmL loop)

WHICH MINIONS A MASK ENABLES (entry_point; Session::launch sets the runtime's shire mask to the same mask): hart 0 of minions 0..per_shire-1
(per_shire must be 32 for a GEMM arm) of every shire s < 32 whose mask bit is set runs the GEMM; hart 1 of those minions enters and returns;
no other shire is launched. A minion's work does NOT depend on the mask: it keeps the full chip's partition, so a subset computes the
masked shires' share of every C block (each minion does 64 MB NB KB TensorFMAs, as at the full chip).

EACH MINION'S TILE ORDER (shire s, minion m; dim0 = m & 7, dim1 = (m >> 3) & 3, s0 = s & 3, s1 = (s >> 2) & 7; row0 = 8 s1 + 2 dim1,
col = 8 s0 + dim0): for it < iters { for (mb, nb) in the walk's block order { for r in 0, 1 { row = row0 + r; for kb < KB { for k < 32 {
op } } pending C tile = C(mb, nb, row, col) } } } then the last TensorStore, TensorWait 7 and 8, fence. One op, in program order:
  1. [coop: csrw tensor_coop = coop_A] TensorLoad A: 16 lines of 64 B from a_pool + (mb KB + kb) 2 MiB + (row 32 + k) 1 KiB, stride 64,
     into L1 scratchpad lines aline..aline+15 (aline = 16 (op & 1)), load id 0; coop_A = 0xFF << 8 | (1 << dim1) << 16 (group 0: the 8
     minions of the neighbourhood; one read serves them);
  2. [coop: csrw tensor_coop = coop_B] TensorLoad B into TenB: 16 lines from b_pool + (kb NB + nb) 1 MiB + (col 32 + k) 1 KiB, stride
     64, load id 1; coop_B = (dim0 + 1) | (1 << dim0) << 8 | 0xF << 16 (group dim0 + 1: the minions at position dim0 in the shire's 4
     neighbourhoods); gemmLnc: the same two loads with coop 0 (stride field 64, ids 0 and 1);
  3. if a C tile is pending: TensorStore 16 rows x 64 B (cols 4) of f0.. to c_pool + (mb NB + nb) 2 MiB + (row 32 + col) 1 KiB,
     stride 64, bypassing L1 and L2 (the previous tile's, issued in this tile's first op);
  4. TensorWait 0; 5. TensorFMA (16 x 16 x 16, B from TenB, astart = aline, mul = first op of the tile, int8's TenC-to-RF on its last).
WHAT IT FETCHES FROM WHICH LEVEL (the model; levels are NOT in any simulator): per op step a shire issues 4 A tile reads (one per
neighbourhood) and 8 B tile reads (one per position): 192 lines (coop); gemmLnc issues 32 + 32 tile reads, of which 4 + 8 distinct. An
A tile is asked by the active shires of its row group (s1), a B tile by those of its column group (s0). The level of each request comes
from exact LRU stack distances with no fitted constant: the shire's L2 by the lab's desk L2 model (E105/E136: 2,048 sets x 4 ways of
64 B lines, LRU, the shire's own line stream, second pass) and the chip's L3 as one fully associative LRU over 1 KiB tiles of the
ACTIVE shires' requests in lock step (E136/E206/E211's convention: one step = every active minion's op at one (r, kb, k); C's TensorStores
allocate after each row half; a request whose tile another shire asked earlier in the same step counts as in flight), strict at a
capacity given in MB (32 by default; MM1's retention laws can be applied to the distances afterwards).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import hashlib
import json
import re
import sys

KT, NT, MT = 32, 32, 64
TILE, LINE = 1024, 64
ABLK, BBLK, CBLK = MT * KT * TILE, KT * NT * TILE, MT * NT * TILE      # 2 MiB, 1 MiB, 2 MiB
L2_SETS, L2_WAYS = 2048, 4                                              # the lab's desk L2 model (E105's l2sim.py, E136)
INF = 1 << 60

KERNELS = {
    "rgm136.gemmL": {"walk": "mn", "coop": True, "elf": "rgm136", "host": "rgm136", "arm": "gemmL"},
    "rgm136.gemmLnc": {"walk": "mn", "coop": False, "elf": "rgm136", "host": "rgm211", "arm": "gemmLnc"},
    "rgm211.gemmLn": {"walk": "nm", "coop": True, "elf": "rgm211", "host": "rgm211", "arm": "gemmLn"},
    "rgm211.gemmL": {"walk": "mn", "coop": True, "elf": "rgm211", "host": "rgm211", "arm": "gemmL"},
}
FMT = {"fp32": "fp32", "fp16": "fp16", "int8": "int8"}


def parse_shape(s):
    m = re.fullmatch(r"(\d+)x(\d+)x(\d+)", s)
    if not m:
        raise ValueError("shape must be <MB>x<NB>x<KB>: " + s)
    return tuple(int(x) for x in m.groups())


def parse_mask(mask):
    return int(mask, 16) if isinstance(mask, str) else int(mask)


def mask_shires(mask):
    m = parse_mask(mask)
    return [s for s in range(32) if (m >> s) & 1]


def enabled(mask, per_shire=32):
    """(working harts, harts that enter and return): hart id = 64 shire + 2 minion + thread"""
    if per_shire != 32:
        raise ValueError("a GEMM arm needs --per-shire 32 (the host refuses anything else)")
    work, idle = [], []
    for s in mask_shires(mask):
        for m in range(per_shire):
            work.append(64 * s + 2 * m)
            idle.append(64 * s + 2 * m + 1)
    return work, idle


def coords(shire, minion):
    m = minion & 31
    dim0, dim1, s0, s1 = m & 7, (m >> 3) & 3, shire & 3, (shire >> 2) & 7
    return {"dim0": dim0, "dim1": dim1, "s0": s0, "s1": s1, "row0": s1 * 8 + dim1 * 2, "col": s0 * 8 + dim0}


def tcoop_a(dim1):
    return (0xFF << 8) | ((1 << dim1) << 16)


def tcoop_b(dim0):
    return (dim0 + 1) | ((1 << dim0) << 8) | (0xF << 16)


def block_order(walk, MB, NB):
    if walk == "mn":
        return [(mb, nb) for mb in range(MB) for nb in range(NB)]
    if walk == "nm":
        return [(mb, nb) for nb in range(NB) for mb in range(MB)]
    raise ValueError(walk)


def a_off(MB, NB, KB, mb, kb, row, k):
    return (mb * KB + kb) * ABLK + (row * KT + k) * TILE


def b_off(MB, NB, KB, kb, nb, col, k):
    return (kb * NB + nb) * BBLK + (col * KT + k) * TILE


def c_off(MB, NB, KB, mb, nb, row, col):
    return (mb * NB + nb) * CBLK + (row * NT + col) * TILE


def minion_events(kernel, MB, NB, KB, shire, minion, fmt="fp32", iters=1):
    """one working minion's tensor events in program order, canonical tuples (pool-relative offsets):
         ('LA', off, start, coop, tcoop, rows, stride, id)   TensorLoad A into the L1 scratchpad
         ('LB', off, coop, tcoop, rows, stride, id)          TensorLoad B into TenB
         ('S', off, rows, cols, stride)                      TensorStore of a C tile
         ('F', astart, mul, last)                            TensorFMA (last = int8's TenC-to-RF bit; 0 for fp32/fp16)"""
    K = KERNELS[kernel]
    c = coords(shire, minion)
    coop = 1 if K["coop"] else 0
    ta, tb = (tcoop_a(c["dim1"]), tcoop_b(c["dim0"])) if coop else (0, 0)
    op, pending = 0, None
    for _ in range(iters):
        for mb, nb in block_order(K["walk"], MB, NB):
            for r in range(2):
                row = c["row0"] + r
                for kb in range(KB):
                    for k in range(KT):
                        aline = (op & 1) * 16
                        yield ("LA", a_off(MB, NB, KB, mb, kb, row, k), aline, coop, ta, 16, 64, 0)
                        yield ("LB", b_off(MB, NB, KB, kb, nb, c["col"], k), coop, tb, 16, 64, 1)
                        if pending is not None:
                            yield ("S", pending, 16, 4, 64)
                            pending = None
                        first = 1 if (kb == 0 and k == 0) else 0
                        last = 1 if (fmt == "int8" and kb + 1 == KB and k + 1 == KT) else 0
                        yield ("F", aline, first, last)
                        op += 1
                pending = c_off(MB, NB, KB, mb, nb, row, c["col"])
    yield ("S", pending, 16, 4, 64)


def minion_counts(kernel, MB, NB, KB, fmt="fp32", iters=1):
    """closed-form counts a working minion (the same for every minion and mask)"""
    ops = iters * MB * NB * 2 * KB * KT
    return {"fma": ops, "load_a": ops, "load_b": ops, "store": iters * MB * NB * 2, "lines_read": 32 * ops,
            "bytes_read": 2048 * ops, "bytes_stored": 1024 * iters * MB * NB * 2}


def events_sha(events):
    h = hashlib.sha256()
    for e in events:
        h.update((",".join(str(x) for x in e) + "\n").encode())
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------ shire and chip streams
def shire_step_requests(kernel, MB, NB, KB, shire):
    """per op step (lock step, the op's (mb, nb, r, kb, k)) the shire's tile READS after cooperation: (A offsets, B offsets) with the
    minions each serves. coop: 4 A reads (one per neighbourhood, serving its 8 minions) and 8 B reads (one per position, serving 4);
    gemmLnc: every minion's own reads (32 + 32; duplicates of 4 + 8 distinct tiles)."""
    K = KERNELS[kernel]
    s0, s1 = shire & 3, (shire >> 2) & 7
    for mb, nb in block_order(K["walk"], MB, NB):
        for r in range(2):
            for kb in range(KB):
                for k in range(KT):
                    if K["coop"]:
                        A = [(a_off(MB, NB, KB, mb, kb, s1 * 8 + 2 * d + r, k), 8) for d in range(4)]
                        B = [(b_off(MB, NB, KB, kb, nb, s0 * 8 + p, k), 4) for p in range(8)]
                    else:
                        A = [(a_off(MB, NB, KB, mb, kb, s1 * 8 + 2 * ((m >> 3) & 3) + r, k), 1) for m in range(32)]
                        B = [(b_off(MB, NB, KB, kb, nb, s0 * 8 + (m & 7), k), 1) for m in range(32)]
                    yield (mb, nb, r, kb, k), A, B


def chip_steps(kernel, MB, NB, KB, mask):
    """the active shires in lock step: per step the distinct A and B tiles with the shires asking each, then after each row half the C
    tiles stored (every active minion's). Tile ids are pool-relative offsets // 1 KiB with the pools apart (A, B, C)."""
    K = KERNELS[kernel]
    sh = mask_shires(mask)
    rows = collections.defaultdict(list)
    cols = collections.defaultdict(list)
    for s in sh:
        rows[(s >> 2) & 7].append(s)
        cols[s & 3].append(s)
    A0, B0, C0 = 0, 1 << 32, 1 << 33
    for mb, nb in block_order(K["walk"], MB, NB):
        for r in range(2):
            for kb in range(KB):
                for k in range(KT):
                    A = [((A0 + a_off(MB, NB, KB, mb, kb, s1 * 8 + 2 * d + r, k)) >> 10, tuple(rows[s1]))
                         for s1 in sorted(rows) for d in range(4)]
                    B = [((B0 + b_off(MB, NB, KB, kb, nb, s0 * 8 + p, k)) >> 10, tuple(cols[s0]))
                         for s0 in sorted(cols) for p in range(8)]
                    yield ("op", (mb, nb, r, kb, k), A, B)
            # every active minion's C tile of this row half, in E136/E206/E211's order (row pair q, then column c; shire 4 (q // 4) + c // 8)
            shs = set(sh)
            C = [(C0 + c_off(MB, NB, KB, mb, nb, 2 * q + r, c)) >> 10 for q in range(32) for c in range(NT) if 4 * (q // 4) + c // 8 in shs]
            yield ("store", (mb, nb, r), C)


def footprint_tiles(kernel, MB, NB, KB, mask):
    """distinct tiles a pass touches, by pool (exact, from the walk)"""
    a, b, c = set(), set(), set()
    for st in chip_steps(kernel, MB, NB, KB, mask):
        if st[0] == "op":
            a.update(t for t, _ in st[2])
            b.update(t for t, _ in st[3])
        else:
            c.update(st[2])
    return {"A": len(a), "B": len(b), "C": len(c), "MB": round((len(a) + len(b) + len(c)) / 1024.0, 4)}


class _Fenwick:
    def __init__(self, n):
        self.n, self.t = n, [0] * (n + 1)

    def add(self, i, v):
        while i <= self.n:
            self.t[i] += v
            i += i & -i

    def sum(self, i):
        s = 0
        while i > 0:
            s += self.t[i]
            i -= i & -i
        return s


def l3_distances(kernel, MB, NB, KB, mask, passes=2):
    """exact LRU stack distances (distinct tiles touched since the tile's last touch; INF for a first touch) of every distinct operand tile
    request of the last pass, per step: A and B lists of (distance, sharing shires); C stores touch the LRU. A tile asked by w shires in one
    step is one request here (the others are in flight behind it)."""
    steps = list(chip_steps(kernel, MB, NB, KB, mask))
    per_pass = sum(len(s[2]) + len(s[3]) if s[0] == "op" else len(s[2]) for s in steps)
    fw = _Fenwick(passes * per_pass + 1)
    last, T, ndist = {}, 0, 0
    recA, recB = [], []
    for p in range(passes):
        rec = p == passes - 1
        for st in steps:
            if st[0] == "store":
                lists = [[(t, None) for t in st[2]]]
            else:
                lists = [st[2], st[3]]
            outs = []
            for lst in lists:
                ds = []
                for t, who in lst:
                    T += 1
                    L = last.get(t)
                    if L is None:
                        d = INF
                        ndist += 1
                    else:
                        d = ndist - fw.sum(L)
                        fw.add(L, -1)
                    fw.add(T, 1)
                    last[t] = T
                    ds.append((d, who))
                outs.append(ds)
            if rec and st[0] == "op":
                recA.append(outs[0])
                recB.append(outs[1])
    return recA, recB


def l2_shire(kernel, MB, NB, KB, shire, passes=2):
    """the lab's desk L2 model on one shire's own line stream (A's and B's reads of each op interleaved by line, as E136's reuse_e136.l2_pass
    issues them): per op of the last pass, (A lines that hit, B lines that hit); duplicates of a non-cooperative kernel are separate reads."""
    sets = collections.defaultdict(list)
    out = []
    for p in range(passes):
        rec = p == passes - 1
        for _, A, B in shire_step_requests(kernel, MB, NB, KB, shire):
            ha = hb = 0
            tiles = [(a, "A") for a, _ in A] + [((1 << 32) + b, "B") for b, _ in B]
            for i in range(16):
                for t, which in tiles:
                    line = (t >> 6) + i
                    s = sets[line & (L2_SETS - 1)]
                    if line in s:
                        s.remove(line)
                        s.append(line)
                        if which == "A":
                            ha += 1
                        else:
                            hb += 1
                    else:
                        s.append(line)
                        if len(s) > L2_WAYS:
                            s.pop(0)
            if rec:
                out.append((ha, hb))
    return out


def l2_shire_tiles(kernel, MB, NB, KB, shire, passes=2):
    """as l2_shire, per op of the last pass the hit lines (of 16) of each READ in the shire's stream: (A list, B list) in stream order"""
    sets = collections.defaultdict(list)
    out = []
    for p in range(passes):
        rec = p == passes - 1
        for _, A, B in shire_step_requests(kernel, MB, NB, KB, shire):
            tiles = [a for a, _ in A] + [(1 << 32) + b for b, _ in B]
            hits = [0] * len(tiles)
            for i in range(16):
                for j, t in enumerate(tiles):
                    line = (t >> 6) + i
                    s = sets[line & (L2_SETS - 1)]
                    if line in s:
                        s.remove(line)
                        s.append(line)
                        hits[j] += 1
                    else:
                        s.append(line)
                        if len(s) > L2_WAYS:
                            s.pop(0)
            if rec:
                out.append((hits[:len(A)], hits[len(A):]))
    return out


def minion_levels(kernel, MB, NB, KB, mask, shire, minion, l3_cap_mb=32.0, _cache=None):
    """WHAT ONE MINION FETCHES FROM WHICH LEVEL, IN ORDER (the model, steady state = the second pass; no fitted constant): per op, for its A
    and B reads, ('L2', hit lines) when the desk L2 model holds all 16 lines, else 'L3' when the chip's strict LRU of the active shires'
    tiles holds the tile at l3_cap_mb (stack distance below the capacity), else 'F' (fresh, from DRAM); with the tile's stack distance and
    the number of active shires that read it in that step. Returns a list of (op, A level, A L2 hits, A distance, A sharing, B level, ...)."""
    K = KERNELS[kernel]
    if shire not in mask_shires(mask):
        return []
    c = coords(shire, minion)
    key = (kernel, MB, NB, KB, parse_mask(mask))
    cache = _cache if _cache is not None else {}
    if ("l3",) + key not in cache:
        cache[("l3",) + key] = l3_distances(kernel, MB, NB, KB, mask)
    if ("l2", kernel, MB, NB, KB, shire) not in cache:
        cache[("l2", kernel, MB, NB, KB, shire)] = l2_shire_tiles(kernel, MB, NB, KB, shire)
    recA, recB = cache[("l3",) + key]
    l2 = cache[("l2", kernel, MB, NB, KB, shire)]
    sh = mask_shires(mask)
    rowsg = sorted({(s >> 2) & 7 for s in sh})
    colsg = sorted({s & 3 for s in sh})
    ia = rowsg.index(c["s1"]) * 4 + c["dim1"]
    ib = colsg.index(c["s0"]) * 8 + c["dim0"]
    # this minion's read in the shire's stream: coop, its neighbourhood's A read and its position's B read; gemmLnc, its own reads
    ja, jb = (c["dim1"], c["dim0"]) if K["coop"] else (minion & 31, minion & 31)
    cap = int(round(l3_cap_mb * 1024))
    out = []
    for op, ((dA, wA), (dB, wB), (hA, hB)) in enumerate(zip((x[ia] for x in recA), (x[ib] for x in recB), l2)):
        la = "L2" if hA[ja] == 16 else ("L3" if dA < cap else "F")
        lb = "L2" if hB[jb] == 16 else ("L3" if dB < cap else "F")
        out.append((op, la, hA[ja], (dA if dA < INF else -1), len(wA), lb, hB[jb], (dB if dB < INF else -1), len(wB)))
    return out


def summary(kernel, MB, NB, KB, mask, l2=False, l3_cap_mb=32.0):
    """the walk's numbers for one (kernel, shape, mask): minions, counts, the shire and chip request streams, the sharing, the footprint,
    and (strict, no fitted constant) the L3 levels of the chip's requests at a capacity; optionally the desk L2 model per active shire"""
    K = KERNELS[kernel]
    sh = mask_shires(mask)
    work, idle = enabled(mask)
    rowsg = sorted({(s >> 2) & 7 for s in sh})
    colsg = sorted({s & 3 for s in sh})
    cnt = minion_counts(kernel, MB, NB, KB)
    reqA = 4 if K["coop"] else 32
    reqB = 8 if K["coop"] else 32
    # sharing per distinct tile of a step (the active shires asking it): a row group's 4 A tiles (rows 8 s1 + 2 d + r, d < 4) and a column
    # group's 8 B tiles (columns 8 s0 + p, p < 8)
    shareA = collections.Counter(len([s for s in sh if (s >> 2) & 7 == g]) for g in rowsg for _ in range(4))
    shareB = collections.Counter(len([s for s in sh if s & 3 == g]) for g in colsg for _ in range(8))
    out = {"kernel": kernel, "walk": K["walk"], "coop": K["coop"], "shape": "%dx%dx%d" % (MB, NB, KB), "mask": "0x%x" % parse_mask(mask),
           "shires": sh, "n": len(sh), "row_groups": rowsg, "col_groups": colsg, "working_harts": len(work), "idle_harts": len(idle),
           "per_minion": cnt, "steps_per_pass": MB * NB * 2 * KB * KT,
           "per_shire_step": {"A_reads": reqA, "B_reads": reqB, "A_distinct": 4, "B_distinct": 8, "lines_read": 16 * (reqA + reqB),
                              "lines_distinct": 192},
           "chip_step": {"A_distinct": 4 * len(rowsg), "B_distinct": 8 * len(colsg), "shire_requests": len(sh) * 12,
                         "A_sharing_hist": {str(k): v for k, v in sorted(shareA.items())},
                         "B_sharing_hist": {str(k): v for k, v in sorted(shareB.items())}},
           "footprint": footprint_tiles(kernel, MB, NB, KB, mask)}
    cap = int(round(l3_cap_mb * 1024))
    recA, recB = l3_distances(kernel, MB, NB, KB, mask)
    nA = nB = inA = inB = 0
    wA = wB = winA = winB = 0
    for stepA, stepB in zip(recA, recB):
        for d, who in stepA:
            nA += 1
            wA += len(who)
            h = d < cap
            inA += h
            winA += len(who) * h
        for d, who in stepB:
            nB += 1
            wB += len(who)
            h = d < cap
            inB += h
            winB += len(who) * h
    out["l3_strict"] = {"cap_MB": l3_cap_mb, "A_tile_requests": nA, "B_tile_requests": nB,
                        "A_in_L3_share_distinct": round(inA / nA, 6), "B_in_L3_share_distinct": round(inB / nB, 6),
                        "A_in_L3_share_by_shire_request": round(winA / wA, 6), "B_in_L3_share_by_shire_request": round(winB / wB, 6),
                        "chip_fresh_tiles_per_step": round(((nA - inA) + (nB - inB)) / len(recA), 6),
                        "chip_fresh_lines_per_step": round(16 * ((nA - inA) + (nB - inB)) / len(recA), 6)}
    if l2:
        per = {}
        for s in sh:
            hits = l2_shire(kernel, MB, NB, KB, s)
            n = len(hits)
            per[str(s)] = {"A_L2_lines_per_op": round(sum(h[0] for h in hits) / n, 6), "B_L2_lines_per_op": round(sum(h[1] for h in hits) / n, 6)}
        out["l2_desk"] = per
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("summary")
    a.add_argument("kernel", choices=sorted(KERNELS))
    a.add_argument("shape")
    a.add_argument("mask")
    a.add_argument("--l2", action="store_true")
    a.add_argument("--l3-cap-mb", type=float, default=32.0)
    b = sub.add_parser("minion")
    b.add_argument("kernel", choices=sorted(KERNELS))
    b.add_argument("shape")
    b.add_argument("mask")
    b.add_argument("shire", type=int)
    b.add_argument("minion", type=int)
    b.add_argument("--fmt", default="fp32", choices=sorted(FMT))
    c = sub.add_parser("levels")
    c.add_argument("kernel", choices=sorted(KERNELS))
    c.add_argument("shape")
    c.add_argument("mask")
    c.add_argument("shire", type=int)
    c.add_argument("minion", type=int)
    c.add_argument("--l3-cap-mb", type=float, default=32.0)
    args = ap.parse_args(argv)
    MB, NB, KB = parse_shape(args.shape)
    if args.cmd == "summary":
        print(json.dumps(summary(args.kernel, MB, NB, KB, args.mask, l2=args.l2, l3_cap_mb=args.l3_cap_mb), indent=1))
    elif args.cmd == "levels":
        lv = minion_levels(args.kernel, MB, NB, KB, args.mask, args.shire, args.minion, l3_cap_mb=args.l3_cap_mb)
        cnt = collections.Counter((x[1], x[5]) for x in lv)
        print(json.dumps({"ops": len(lv), "classes_A_B": {"%s/%s" % k: v for k, v in sorted(cnt.items())},
                          "columns": ["op", "A level", "A L2 hit lines", "A stack distance (tiles, -1 first touch)", "A sharing shires",
                                      "B level", "B L2 hit lines", "B stack distance", "B sharing shires"]}))
        for x in lv:
            print(json.dumps(x))
    else:
        if args.shire not in mask_shires(args.mask):
            print(json.dumps({"enabled": False, "why": "shire not in the mask: never launched"}))
            return 0
        ev = list(minion_events(args.kernel, MB, NB, KB, args.shire, args.minion, fmt=args.fmt))
        print(json.dumps({"enabled": True, "events": len(ev), "sha256": events_sha(ev)}))
        for e in ev:
            print(json.dumps(e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
