#!/usr/bin/env python3
"""Lines past the L1: an L1 data-cache model of the documented 512 B a hart, over an address trace (ledger v3, Q193).

    /usr/bin/python3 -I -B tools/counter/l1_model.py --programs [--out FILE]     # the ledger kernel's programs
    /usr/bin/python3 -I -B tools/counter/l1_model.py --log RUN1.log --log2 RUN2.log --units1 1 --units2 2 [--hart H]

THE L1 a kernel runs with (docs/reports/data/2026-09-28-memory-levels/research/facts-l1.json): the firmware sets D1Split
and ScpEnable before every launch, so each hart has its own 512 B (l1.firmware-mode, l1.modes): 2 sets x 4 ways x 64 B
lines, the set chosen by physical-address bit 6; replacement LRU (l1.lru); write-back and write-allocate: a store that
misses fetches its line, and a dirty victim is written back to the L2 (l1.write-policy); the knee at 512 B is measured
(l1.knee). Two harts of a minion never share lines in this mode. The model counts, per hart: FILLS (lines brought from
the L2: by a load that misses, READ FILLS, or by a store that misses, WRITE FILLS, i.e. allocations) and DIRTY
EVICTIONS (lines written back). Ledger v3 prices a fill at e_r and a dirty eviction at e_w - e_r (tools/ledger/ledger_v3.py,
rule 3), and times them at the L2's line cycles (rule 2).

TRACES (each access: address, bytes, is it a write; program order):
  * the sort: tools/counter/ledger_interp.py, an instruction-exact interpreter of the committed kernel's sort path on
    the host's own inputs (it reproduces the counter's per-sort counts at 512 keys exactly), stack accesses included;
    the participant (so the input's and the work area's lines) and the stack's offset in its line swept;
  * SHA-256: a structural trace of sha256_compress in the committed disassembly's access order (its 352 B frame: w[64]
    at sp+0..255, s0-s11 saved at sp+256..351; K256 at 0x8005801fc0, 64 B aligned; the message line; the caller's st[8]),
    the frame's offset in its line and the set of st's line swept;
  * the copy: copy_v32 (8 vector loads and 8 vector stores of 32 B a 256 B iteration) and entry_point's pass loop
    (ld 0(sp), ld 64(s0), ld 56(s0), ld 72(s0), sd 0(sp): the disassembly at 0x8005801d74-0x8005801d8e);
  * a simulator log (--log): sw-sysemu's own lines as tools/counter/count_kernel.py reads them (its LOG_I, LOG_D and
    MEM_RE): each hart's loads and stores of the counter's classes `load` and `store` to cacheable DRAM addresses
    (0x80_0000_0000 and up, not the uncached alias with bit 38 set), an instruction killed and restarted dropping its
    accesses. Two runs that differ only in their units (Q166's CASES) give the lines a unit by differencing.
    NOT RUN on a real simulator log here (no simulator on aifoundry2; Q166's committed logs keep only a tail without
    memory lines): a kit that uses --log first checks it on a real log beside --programs.

The structural traces are ports of the step-5 diagnosis and design lanes' desk models (Q193 diag5-a l1sim.py, fix5-design
l1model.py and rvcount.py); this file's --programs reproduces their counts (tools/counter/test_l1_model.py).
Desk only: no device, no simulator. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

LINE = 64
SETS = 2
WAYS = 4
L1_BYTES = SETS * WAYS * LINE           # 512 B a hart
GEOMETRY = ("512 B a hart: 2 sets x 4 ways x 64 B lines, set = physical-address bit 6, LRU, write-back, "
            "write-allocate (facts-l1.json: l1.firmware-mode, l1.modes, l1.lru, l1.write-policy, l1.knee)")


class L1:
    """One hart's L1 data cache. access() returns True on a hit."""

    def __init__(self, sets=SETS, ways=WAYS, line=LINE):
        self.sets = [[] for _ in range(sets)]      # each: [[tag, dirty], ...], most recently used last
        self.nsets, self.ways, self.line = sets, ways, line
        self.fills = self.read_fills = self.write_fills = self.wbs = self.accesses = 0

    def access(self, addr, nbytes, write):
        hit_all = True
        for ln in range(addr // self.line, (addr + max(nbytes, 1) - 1) // self.line + 1):
            self.accesses += 1
            s = self.sets[ln % self.nsets]
            for i, (tag, d) in enumerate(s):
                if tag == ln:
                    s.pop(i)
                    s.append([tag, d or write])
                    break
            else:
                hit_all = False
                self.fills += 1
                if write:
                    self.write_fills += 1
                else:
                    self.read_fills += 1
                if len(s) == self.ways:
                    victim = s.pop(0)
                    if victim[1]:
                        self.wbs += 1
                s.append([ln, write])
        return hit_all

    def snap(self):
        return (self.fills, self.read_fills, self.write_fills, self.wbs)


def steady(trace, reps=6, warm=2):
    """The trace of one unit repeated `reps` times on one cold L1; the mean per unit over the repetitions after `warm`."""
    c = L1()
    per = []
    for _ in range(reps):
        a = c.snap()
        for (ad, n, w) in trace:
            c.access(ad, n, w)
        b = c.snap()
        per.append([b[i] - a[i] for i in range(4)])
    ss = per[warm:]
    k = len(ss)
    return {"fills": sum(x[0] for x in ss) / k, "read_fills": sum(x[1] for x in ss) / k,
            "write_fills": sum(x[2] for x in ss) / k, "dirty_evictions": sum(x[3] for x in ss) / k}


def _agg(rows, keys=("fills", "read_fills", "write_fills", "dirty_evictions")):
    out = {k: sum(r[k] for r in rows) / len(rows) for k in keys}
    out["fills_range"] = [min(r["fills"] for r in rows), max(r["fills"] for r in rows)]
    out["dirty_evictions_range"] = [min(r["dirty_evictions"] for r in rows), max(r["dirty_evictions"] for r in rows)]
    out["cases"] = len(rows)
    return out


# ------------------------------------------------------------------ the sort (through the interpreter)
SORT_PARTS = (0, 1, 2, 3, 5, 8, 13, 21)
SORT_SP_OFFSETS = (0, 16, 32, 48)


def sort_lines(n, order, parts=SORT_PARTS, sp_offsets=SORT_SP_OFFSETS, dis=None):
    """Lines past the L1 a sort of n keys, steady state, the mean over participants and stack offsets."""
    import ledger_interp as LI  # noqa: E402
    ins, syms = dis or LI.read_dis()
    rows = []
    for p in parts:
        for off in sp_offsets:
            sp = LI.SP + 0x1000 * p + off
            r = LI.sort_rep(ins, syms, n, p, order, sp=sp)
            s = steady(r["trace"])
            s.update({"participant": p, "sp_offset": off})
            rows.append(s)
    out = _agg(rows)
    out["swept"] = {"participants": list(parts), "stack_offsets_b": list(sp_offsets)}
    return out


def sort_data_trace(keys, w0, w1, inp):
    """The sort's data accesses alone (no stack), merge_sort's order: copy_keys's 8 B moves, then for each output key
    its loads and its store (an independent check of the interpreter's trace; the lines of the data alone)."""
    n = len(keys)
    t = []
    for i in range(0, n, 2):
        t.append((inp + 4 * i, 8, False))
        t.append((w0 + 4 * i, 8, True))
    buf = {w0: list(keys), w1: [0] * n}
    s, d, width = w0, w1, 1
    while width < n:
        S, D = buf[s], buf[d]
        lo = 0
        while lo < n:
            mid, hi = min(lo + width, n), min(lo + 2 * width, n)
            i, j, k = lo, mid, lo
            while i < mid and j < hi:
                t.append((s + 4 * i, 4, False))
                t.append((s + 4 * j, 4, False))
                if S[i] <= S[j]:
                    D[k] = S[i]
                    i += 1
                else:
                    D[k] = S[j]
                    j += 1
                t.append((d + 4 * k, 4, True))
                k += 1
            while i < mid:
                t.append((s + 4 * i, 4, False))
                D[k] = S[i]
                t.append((d + 4 * k, 4, True))
                i += 1
                k += 1
            while j < hi:
                t.append((s + 4 * j, 4, False))
                D[k] = S[j]
                t.append((d + 4 * k, 4, True))
                j += 1
                k += 1
            lo += 2 * width
        s, d = d, s
        width <<= 1
    return t


# ------------------------------------------------------------------ SHA-256 (structural)
K256 = 0x8005801FC0


def sha256_trace(sp, msg, st, K=K256):
    """One compression's data accesses in the committed disassembly's order, as (address, 4, is_write)."""
    t = []

    def R(a):
        t.append((a, 4, False))

    def Wt(a):
        t.append((a, 4, True))
    # phase 1: message words and w[0..15], the callee-saved registers stored in between
    R(msg + 0); R(msg + 4); R(msg + 8); Wt(sp + 4); R(msg + 12); Wt(sp + 8); R(msg + 16); Wt(sp + 12); R(msg + 20)  # noqa: E702
    Wt(sp + 16); R(msg + 24); Wt(sp + 20); R(msg + 28)  # noqa: E702
    for off in range(344, 255, -8):
        Wt(sp + off)
    for o in (36, 40, 44, 48, 52, 32):
        R(msg + o)
    Wt(sp + 24); R(msg + 60); R(msg + 56); Wt(sp + 28)  # noqa: E702
    for o in (32, 0, 36, 40, 44, 48, 52, 56, 60):
        Wt(sp + o)
    # phase 2: the schedule loop, 6 iterations of 7 loads (a5+4..28) and 7 stores (a5+64..88), a5 = sp + 28 k
    for k in range(6):
        a5 = sp + 28 * k
        for o in (4, 12, 8, 16, 20, 24, 28):
            R(a5 + o)
        for o in (64, 68, 72, 76, 80, 84, 88):
            Wt(a5 + o)
    # the tail: the last six w values and the state's loads
    for o in (224, 228, 168, 204, 172, 176, 208, 212, 180, 184, 216):
        R(sp + o)
    Wt(sp + 232); Wt(sp + 236)  # noqa: E702
    for o in (188, 220, 192):
        R(sp + o)
    Wt(sp + 240); Wt(sp + 244)  # noqa: E702
    for o in range(0, 32, 4):
        R(st + o)
    Wt(sp + 248); Wt(sp + 252)  # noqa: E702
    # phase 3: 64 rounds, K[t] and w[t]
    for r in range(64):
        R(K + 4 * r)
        R(sp + 4 * r)
    # the state's stores and the callee-saved registers' loads
    Wt(st + 24); R(sp + 344)  # noqa: E702
    for o in (0, 4, 8, 12, 16, 20, 28):
        Wt(st + o)
    for off in range(336, 255, -8):
        R(sp + off)
    return t


def sha256_case(frame_off, st_set, n_comp=200, block_lines=32, skip=50):
    """Lines past the L1 a compression for one frame offset and one set of st's line, steady state (the message line
    moves through a 2 KiB block, 32 lines)."""
    base_sp = 0x40000000 + 0x1000 - 1024          # an arbitrary hart stack: only the low bits matter
    sp = (base_sp // LINE) * LINE + frame_off
    st = 0x40000000 + 0x1000 - 64 * (3 + (st_set ^ ((0x40000000 + 0x1000) // LINE % 2)))   # a line above the frame
    st = (st // LINE) * LINE + 8
    blk = 0x10000000
    c = L1()
    out = []
    for b in range(n_comp):
        a = c.snap()
        for (ad, n, w) in sha256_trace(sp, blk + LINE * (b % block_lines), st):
            c.access(ad, n, w)
        z = c.snap()
        out.append([z[i] - a[i] for i in range(4)])
    ss = out[skip:]
    k = len(ss)
    return {"fills": sum(x[0] for x in ss) / k, "read_fills": sum(x[1] for x in ss) / k,
            "write_fills": sum(x[2] for x in ss) / k, "dirty_evictions": sum(x[3] for x in ss) / k}


def sha256_lines():
    rows = []
    for off in (0, 16, 32, 48):
        for sts in (0, 1):
            r = sha256_case(off, sts)
            r.update({"frame_offset_b": off, "st_set": sts})
            rows.append(r)
    out = _agg(rows)
    out["swept"] = {"frame_offsets_b": [0, 16, 32, 48], "st_sets": [0, 1]}
    return out


# ------------------------------------------------------------------ the copy (structural)
def copy_trace(part, args=0x8000400000, sp=0x8007F00000, src=0x8100000000, dst=0x8200000000):
    """One pass of copy_v32 over `part` bytes, with entry_point's pass loop's five accesses."""
    t = [(sp, 8, False), (args + 64, 8, False), (args + 56, 8, False), (args + 72, 8, False), (sp, 8, True)]
    for o in range(0, part, 256):
        for k in range(8):
            t.append((src + o + 32 * k, 32, False))
        for k in range(8):
            t.append((dst + o + 32 * k, 32, True))
    return t


def copy_lines(part, sp_offsets=(0, 8, 32)):
    rows = []
    for off in sp_offsets:
        r = steady(copy_trace(part, sp=0x8007F00000 + off), reps=8, warm=3)
        r["sp_offset"] = off
        rows.append(r)
    out = _agg(rows)
    out["data_lines_a_pass"] = 2 * part // LINE
    return out


# ------------------------------------------------------------------ a simulator log
def read_sim_log(path, harts=None):
    """Each hart's cacheable loads and stores from sw-sysemu's log, by count_kernel.py's own patterns: {hart: trace}."""
    import count_kernel as CK  # noqa: E402
    traces, cur, pend = {}, {}, {}
    opener = gzip.open if path.endswith(".gz") else open

    def flush(tid):
        if pend.get(tid):
            traces.setdefault(tid, []).extend(pend[tid])
        pend[tid] = []
    with opener(path, "rt", errors="replace") as fh:
        for line in fh:
            m = CK.LOG_I.match(line)
            if m:
                tid = int(m.group(2))
                if harts is not None and tid not in harts:
                    continue
                flush(tid)
                mn, ops = m.group(7), m.group(8)
                cur[tid] = CK.classify(mn, ops)
                continue
            m = CK.LOG_D.match(line)
            if not m:
                continue
            tid = int(m.group(2))
            if harts is not None and tid not in harts:
                continue
            rest = m.group(4)
            if "Instruction killed and will be restarted" in rest:
                pend[tid] = []
                cur[tid] = None
                continue
            if cur.get(tid) not in ("load", "store"):
                continue
            mm = CK.MEM_RE.search(rest)
            if not mm or rest.lstrip().startswith("("):
                continue
            addr = int(mm.group(2), 16)
            if addr < 0x8000000000 or addr & 0x4000000000:
                continue
            pend.setdefault(tid, []).append((addr, int(mm.group(1)) // 8, mm.group(3) == "="))
    for tid in list(pend):
        flush(tid)
    return traces


def log_lines(path):
    """Fills, read fills, write fills and dirty evictions of each hart over a whole log, from a cold L1."""
    out = {}
    for tid, tr in read_sim_log(path).items():
        c = L1()
        for (a, n, w) in tr:
            c.access(a, n, w)
        out[tid] = dict(zip(("fills", "read_fills", "write_fills", "dirty_evictions"), c.snap()))
    return out


def log_lines_per_unit(path1, path2, units1, units2):
    """Two runs that differ only in their units: the lines a unit a hart by differencing, and their mean and range."""
    a, b = log_lines(path1), log_lines(path2)
    per = {}
    for tid in sorted(set(a) & set(b)):
        per[tid] = {k: (b[tid][k] - a[tid][k]) / float(units2 - units1) for k in a[tid]}
    keys = ("fills", "read_fills", "write_fills", "dirty_evictions")
    mean = {k: sum(v[k] for v in per.values()) / len(per) for k in keys} if per else {}
    return {"per_hart": per, "mean": mean, "harts": len(per)}


# ------------------------------------------------------------------ the programs of the ledger kernel
def programs(sort_keys=(16, 32, 64, 128, 256, 512), copy_parts=(256, 512, 1024, 2048, 4096, 131072, 524288)):
    import ledger_interp as LI  # noqa: E402
    dis = LI.read_dis()
    out = {"geometry": GEOMETRY, "label": "desk check of code: the L1 model over the interpreter's and the "
                                          "disassembly's access orders", "sort": {}, "sha256": sha256_lines(),
           "copy": {}}
    for n in sort_keys:
        for order in ("sorted", "shuffled"):
            out["sort"][f"{n}-{order}"] = sort_lines(n, order, dis=dis)
    for part in copy_parts:
        out["copy"][str(part)] = copy_lines(part)
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--programs", action="store_true", help="the ledger kernel's sorts, SHA-256 and copies")
    ap.add_argument("--keys", default="16,32,64,128,256,512")
    ap.add_argument("--log", help="a simulator log (plain or .gz)")
    ap.add_argument("--log2", help="the second run's log (more units)")
    ap.add_argument("--units1", type=float, default=1.0)
    ap.add_argument("--units2", type=float, default=2.0)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if a.programs:
        res = programs(sort_keys=tuple(int(x) for x in a.keys.split(",")))
        for k, v in res["sort"].items():
            print(f"sort {k:14s}: fills {v['fills']:8.3f} (read {v['read_fills']:8.3f}, write {v['write_fills']:8.3f}), "
                  f"dirty evictions {v['dirty_evictions']:8.3f} a sort; fills range {v['fills_range']}")
        s = res["sha256"]
        print(f"sha256        : fills {s['fills']:8.3f} (read {s['read_fills']:.3f}, write {s['write_fills']:.3f}), dirty "
              f"evictions {s['dirty_evictions']:.3f} a compression; fills range {s['fills_range']}")
        for k, v in res["copy"].items():
            print(f"copy part {k:>7s} B: fills {v['fills']:9.2f} (read {v['read_fills']:.2f}, write {v['write_fills']:.2f}), "
                  f"dirty evictions {v['dirty_evictions']:.2f} a pass; data lines {v['data_lines_a_pass']}")
    elif a.log and a.log2:
        res = log_lines_per_unit(a.log, a.log2, a.units1, a.units2)
        print(json.dumps(res["mean"], sort_keys=True))
    else:
        ap.error("--programs, or --log and --log2")
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
