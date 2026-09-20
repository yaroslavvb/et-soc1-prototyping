#!/usr/bin/env python3
"""Op lists for memprobe_host --program (format in memprobe_args.h).

Each experiment writes <out>/<name>.ops and <out>/<name>.json. The JSON describes every timed op in order
(a label per result), so the analysis can match the u32 results to what was measured.

    gen_ops.py timer    --out D
    gen_ops.py ladder   --out D [--lines 64] [--seed 1]
    gen_ops.py bits     --out D --base 0x... [--trials 24] [--delay 0]
    gen_ops.py decomp   --out D [--lines 2048] [--reps 4]
    gen_ops.py l3map    --out D [--lines 4096]
    gen_ops.py refresh  --out D [--n 60000]
    gen_ops.py pagetimeout --out D --base 0x...
    gen_ops.py table --pattern l1|l2|l3near|l3far|dram_seq|dram_row --out-file t.tbl [--shires MASK]
"""
import argparse
import json
import os
import random
import struct

OP_END, OP_LOAD, OP_TLOAD, OP_EVICT, OP_TEVICT, OP_FENCE, OP_DELAY, OP_STAMP, OP_STORE, OP_TFENCE, OP_TNOP, OP_RAW, OP_TLOAD2, OP_MSREAD = range(14)
L1, L2, L3, MEM = 0, 1, 2, 3  # evict_va destination: where the line is left
TIMED = {OP_TLOAD, OP_TEVICT, OP_STAMP, OP_TFENCE, OP_TNOP, OP_TLOAD2, OP_MSREAD}
MAX_OPS = 0x180000 // 16


class Prog:
    def __init__(self):
        self.ops = []
        self.labels = []

    def op(self, code, addr=0, arg=0, label=None):
        self.ops.append((code | (arg << 8), addr))
        if code in TIMED:
            self.labels.append(label)

    def load(self, a): self.op(OP_LOAD, a)
    def tload(self, a, label): self.op(OP_TLOAD, a, label=label)
    def evict(self, a, level): self.op(OP_EVICT, a, level)
    def tevict(self, a, level, label): self.op(OP_TEVICT, a, level, label=label)
    def fence(self): self.op(OP_FENCE)
    def tfence(self, label): self.op(OP_TFENCE, label=label)
    def delay(self, cycles): self.op(OP_DELAY, arg=cycles)
    def tload2(self, a, b, label):
        """Load a, then immediately a timed load of b. b rides in the next op, which the kernel skips."""
        self.op(OP_TLOAD2, a, label=label)
        self.ops.append((OP_LOAD, b))

    def raw(self, label):
        """Two raw back-to-back hpmcounter3 reads (plus two zero words): four results."""
        self.ops.append((OP_RAW, 0))
        self.labels += [label + (k,) for k in ("t0", "t1", "c0", "c1")]

    def msread(self, ms, pmc, label): self.op(OP_MSREAD, arg=ms | (pmc << 8), label=label)

    def tnop(self, label): self.op(OP_TNOP, label=label)
    def stamp(self, label): self.op(OP_STAMP, label=label)
    def store(self, a, value=0): self.op(OP_STORE, a, value)

    def write(self, out, name, meta):
        assert len(self.ops) < MAX_OPS, f"{name}: {len(self.ops)} ops"
        self.op(OP_END)
        with open(os.path.join(out, name + ".ops"), "wb") as f:
            for w, a in self.ops:
                f.write(struct.pack("<QQ", w, a))
        with open(os.path.join(out, name + ".json"), "w") as f:
            json.dump({"name": name, "meta": meta, "labels": self.labels}, f)
        print(f"{name}: {len(self.ops)} ops, {len(self.labels)} timed")


def place(p, a, level, delay=300):
    """Leave line a where `evict to level` puts it: load it into L1, evict, wait."""
    p.load(a)
    if level is not None:
        p.evict(a, level)
        p.fence()
        p.delay(delay)


def timer(args):
    """The cycle counter itself: raw back-to-back read pairs (t_raw) and corrected timed no-ops (t_glitch)."""
    p = Prog()
    for i in range(4000):
        p.raw(("raw", i))
    p.write(args.out, "t_raw", {})
    p = Prog()
    for i in range(4000):
        p.stamp(("s", i))
        p.tnop(("n", i))
    p.write(args.out, "t_glitch", {})


def ladder(args):
    """For each line: time a load after placing it with each evict level; plus overhead and ordering checks."""
    rng = random.Random(args.seed)
    p = Prog()
    for i in range(64):  # timer overhead
        p.stamp(("stamp", i))
        p.tnop(("tnop", i))
    lines = [rng.randrange(0, (1 << 28) // 64) * 64 for _ in range(args.lines)]
    for rep in range(2):
        for a in lines:
            for level in (None, L1, L2, L3, MEM):
                place(p, a, level)
                p.tload(a, ("ladder", a, -1 if level is None else level, rep))
            # Is the evict asynchronous? No fence and no delay before the load.
            p.load(a)
            p.evict(a, MEM)
            p.tload(a, ("nofence", a, MEM, rep))
            # Fence, no delay.
            p.load(a)
            p.evict(a, MEM)
            p.fence()
            p.tload(a, ("nodelay", a, MEM, rep))
            # Cost of the evict itself, clean and dirty.
            p.load(a)
            p.tevict(a, MEM, ("tevict_clean", a, MEM, rep))
            p.store(a, a)
            p.tevict(a, MEM, ("tevict_dirty", a, MEM, rep))
            p.tfence(("tfence", a, MEM, rep))
    p.write(args.out, "ladder", {"lines": lines})


def bits(args):
    """DRAM address-bit sweep. For each bit b: evict A and B = A ^ (1 << b) to memory, load A (opens its row),
    then time the load of B. Same row: fast; same bank, other row: slow; other bank or channel: in between.
    Each pair is followed by a baseline: both evicted again, then B loaded alone.
    Addresses are physical: A and B are converted to arena offsets with --base."""
    rng = random.Random(args.seed)
    base, size = int(args.base, 0), 1 << args.arena_log2
    p = Prog()
    for t in range(args.trials):
        a_off = rng.randrange(0, size // 64) * 64
        for b in [-1] + list(range(6, args.arena_log2)):
            b_off = a_off if b < 0 else ((base + a_off) ^ (1 << b)) - base
            for x in {a_off, b_off}:
                p.load(x)
                p.evict(x, MEM)
            p.fence()
            p.delay(args.pre_delay)
            p.tload(a_off, ("A", b, t))
            if b < 0:
                p.evict(a_off, MEM)
                p.fence()
            if args.delay:
                p.delay(args.delay)
            p.tload(b_off, ("B", b, t))
            p.evict(b_off, MEM)
            p.fence()
            p.delay(args.pre_delay)
            p.tload(b_off, ("B0", b, t))
            # Back to back: B issued one cycle after A, so it reaches the DRAM while A's row is open.
            for x in {a_off, b_off}:
                p.load(x)
                p.evict(x, MEM)
            p.fence()
            p.delay(args.pre_delay)
            p.tload2(a_off, b_off, ("AB", b, t))
    p.write(args.out, args.name or "bits", {"base": args.base, "arena_log2": args.arena_log2, "delay": args.delay})


def l3map(args):
    """Time an L3 hit (line evicted from L1 and L2 only) for many consecutive lines: which L3 slice each
    line lives in shows up as its distance on the mesh."""
    p = Prog()
    for i in range(args.lines):
        a = args.start + i * 64
        place(p, a, L3, delay=100)
        p.tload(a, ("l3", a))
        place(p, a, L2, delay=100)
        p.tload(a, ("l2", a))
    p.write(args.out, args.name or "l3map", {"start": args.start, "lines": args.lines})


def decomp(args):
    """Per-line latency decomposition: for each line, an L2 hit, an L3 hit (slice distance) and a DRAM
    access, several times each. DRAM minus L3 isolates the leg from the L3 slice to the memory shire."""
    rng = random.Random(args.seed)
    lines = sorted({rng.randrange(0, (1 << args.arena_log2) // 64) * 64 for _ in range(args.lines)})
    p = Prog()
    for rep in range(args.reps):
        for a in lines:
            place(p, a, L2, delay=100)
            p.tload(a, ("l2", a, rep))
            place(p, a, L3, delay=100)
            p.tload(a, ("l3", a, rep))
            place(p, a, MEM, delay=args.pre_delay)
            p.tload(a, ("mem", a, rep))
    p.write(args.out, args.name or "decomp", {"lines": lines, "reps": args.reps})


def msmap(args):
    """Which memory shire serves a line: snapshot all 8 memory shires' read counters (syscall 10), load the
    line from DRAM 16 times, snapshot again. The shire whose count rose by 16 served it."""
    rng = random.Random(args.seed)
    lines = [rng.randrange(0, (1 << args.arena_log2) // 64) * 64 for _ in range(args.lines)]
    p = Prog()
    for a in lines:
        for ms in range(8):
            p.msread(ms, 1, ("before", a, ms))
        for _ in range(16):
            p.load(a)
            p.evict(a, MEM)
            p.fence()
            p.delay(300)
        for ms in range(8):
            p.msread(ms, 1, ("after", a, ms))
    p.write(args.out, args.name or "msmap", {"lines": lines})


def refresh(args):
    """A long series of DRAM loads to one line (evicted to memory each time), with a time stamp per
    load: refresh shows up as periodic slow loads. --jitter adds a random delay before each load.
    Without it the loop locks onto the refresh period."""
    rng = random.Random(args.seed)
    p = Prog()
    a = args.start
    p.load(a)
    for i in range(args.n):
        p.evict(a, MEM)
        p.fence()
        if args.jitter:  # random phase against the refresh period, so some loads land inside a refresh
            p.delay(rng.randrange(args.jitter))
        p.stamp(("t", i))
        p.tload(a, ("lat", i))
    p.write(args.out, args.name or "refresh", {"start": a, "n": args.n})


def pagetimeout(args):
    """Row-buffer hit after a delay: load A, wait d cycles, load A's same-row neighbour. If the controller
    closes idle rows after a timeout, the hit turns into a miss once d passes it."""
    rng = random.Random(args.seed)
    p = Prog()
    neighbour = 1 << args.row_bit  # a bit that stays inside the row (from the bits sweep)
    for t in range(args.trials):
        a = rng.randrange(0, (1 << 27) // 64) * 64 * 2 & ~neighbour
        for d in args.delays:
            for x in (a, a ^ neighbour):
                p.load(x)
                p.evict(x, MEM)
            p.fence()
            p.delay(2000)
            p.tload(a, ("A", d, t))
            p.delay(d)
            p.tload(a ^ neighbour, ("B", d, t))
    p.write(args.out, args.name or "pagetimeout", {"row_bit": args.row_bit, "delays": args.delays})


# Shire coordinates on the 6x6 mesh (marty1885's map, as in workloads/nocbench/analyze.py).
MESH = {
    0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0),
    8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1), 10: (4, 1), 19: (5, 1),
    3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2),
    12: (1, 3), 21: (2, 3), 22: (3, 3), 26: (4, 3),
    20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4),
    28: (1, 5), 5: (2, 5), 6: (3, 5), 7: (4, 5), 31: (5, 5),
}


def hops(a, b):
    (xa, ya), (xb, yb) = MESH[a], MESH[b]
    return abs(xa - xb) + abs(ya - yb)


def far_homes():
    """A bijection shire -> L3 home shire, each far away on the mesh (greedy, farthest pairs first),
    so every home slice holds exactly one shire's working set."""
    free = set(range(32))
    home = {}
    for s in sorted(range(32), key=lambda s: -max(hops(s, h) for h in range(32))):
        h = max(free, key=lambda h: (hops(s, h), -h))
        home[s] = h
        free.remove(h)
    return home


# Strided power-loop patterns: (evict level, stride, lines per minion, per-minion base).
# The arena is aligned to its size, so offset bits are physical address bits: PA[10:6] picks the L3
# home shire, PA[8:6] the memory shire, PA[9] the channel, PA[12:10] the DRAM bank, PA[34:18] the row.
# A cyclic walk over more lines than a cache holds misses it on every access (LRU), with no evicts.
STRIDED = {
    "l1": (4, 64, 4),            # 256 B: stays in L1 (8 lines already spill in scratchpad mode)
    "l2": (4, 64, 16),           # 1 KB: misses L1, 32 KB per shire hits L2
    "l3near": (4, 2048, 384),    # 768 KB per shire homed in its own L3 slice: misses L2 (512 KB), fits the 1 MB slice
    "l3far": (4, 2048, 384),     # the same, homed in a far shire (far_homes)
    "dram_seq": (4, 64, 1024),   # 64 KB per minion, 64 MB in all: misses L3 (32 MB); consecutive lines
    "dram_row": (4, 1 << 18, 1024),  # every access the same bank, the next row: a row conflict each time
}


def table(args):
    """Address table for memprobe_host --loop (one base address per minion of --shires); run it with the
    --level/--stride/--lines that `gen_ops.py table` prints."""
    shires = [s for s in range(32) if (args.shires >> s) & 1]
    level, stride, n = STRIDED[args.pattern]
    far = far_homes()
    bases = []
    for si, s in enumerate(shires):
        for mi in range(32):
            m = si * 32 + mi
            pat = args.pattern
            if pat in ("l1", "l2"):
                # Contiguous per minion: minions sharing low address bits would pile into the same sets.
                bases.append(m * n * 64)
            elif pat in ("l3near", "l3far"):
                home = s if pat == "l3near" else far[s]
                bases.append(((m * n) << 11) + (home << 6))
            elif pat == "dram_seq":
                bases.append(m * n * 64)
            elif pat == "dram_row":
                # Low bits give each minion its own line in a (memory shire, channel, bank); minions m and
                # m + 128 share the bank but use different columns.
                bases.append(((m % 128) << 6) + ((m // 128) << 13))
    with open(args.out_file, "wb") as f:
        f.write(struct.pack("<Q", 1))
        for b in bases:
            f.write(struct.pack("<Q", b))
    print(f"{args.out_file}: {len(bases)} minions; run with --level {level} --stride {stride} --lines {n}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("experiment")
    ap.add_argument("--out", default=".")
    ap.add_argument("--out-file")
    ap.add_argument("--pattern")
    ap.add_argument("--shires", type=lambda s: int(s, 0), default=0xFFFFFFFF)
    ap.add_argument("--name")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--lines", type=int, default=64)
    ap.add_argument("--base", default="0")
    ap.add_argument("--arena-log2", type=int, default=30)
    ap.add_argument("--trials", type=int, default=24)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--delay", type=int, default=0)
    ap.add_argument("--pre-delay", type=int, default=2000)
    ap.add_argument("--start", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--n", type=int, default=24000)
    ap.add_argument("--jitter", type=int, default=0)
    ap.add_argument("--row-bit", type=int, default=6)
    ap.add_argument("--delays", type=lambda s: [int(x) for x in s.split(",")],
                    default=[0, 50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600])
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    {"timer": timer, "ladder": ladder, "bits": bits, "decomp": decomp, "l3map": l3map, "refresh": refresh, "pagetimeout": pagetimeout, "msmap": msmap,
     "table": table}[args.experiment](args)


if __name__ == "__main__":
    main()
