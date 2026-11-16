#!/usr/bin/env python3
"""An instruction-exact interpreter of the ledger kernel's sort path, with each hart's data-address trace (ledger v3, Q193).

    /usr/bin/python3 -I -B tools/counter/ledger_interp.py --check      # reproduce the counter's per-sort counts at 512 keys
    /usr/bin/python3 -I -B tools/counter/ledger_interp.py --keys 16 --order shuffled --participants 0-2047 [--out FILE]

WHAT IT IS. A small RV64 integer interpreter of the instructions a sort repetition runs in the committed ledger kernel
(docs/reports/data/2026-11-12-q166-progs/kernel/ledger.dis.gz, the kernel whose .text E189 pinned): copy_keys and
merge_sort, plus entry_point's repetition loop (its 14 instructions and their 4 stack accesses, read from the same
disassembly at 0x8005801dca-0x8005801de8), on the host's own inputs (workloads/ledger/ledger_desk.py's mirror of
workloads/ledger/host/main.cpp: splitmix64, the stream seed, the sort, then the Fisher-Yates shuffle). Anything outside
the subset those functions use stops it.

WHAT IT IS NOT. It is not the lab's counter (tools/count_kernel.py over the profiling simulator's log, run on aifoundry3)
and it is not the simulator. Its first job is to reproduce the counter's committed per-sort counts at 512 keys
(docs/reports/data/2026-11-12-q166-progs/estimates.json, per_unit_per_participant, the mean of shire 0's 64 participants):
`--check` does that, mnemonic by mnemonic and branch outcome by branch outcome. Its second job is the data-address trace
the L1 model reads (tools/counter/l1_model.py): each load and store in program order, with its address and size.
Its third: every participant's own count, so a forecast can name the slowest minion's (the scorer's seconds read the
slowest minion; the counter logs 64 participants only).

Port of the fix's design lane's desk interpreter (Q193 fix5-design, rvcount.py), with the paths made relative to the
repository and the host's inputs taken from ledger_desk.py. Desk only: no device, no simulator. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
DIS_REL = "docs/reports/data/2026-11-12-q166-progs/kernel/ledger.dis.gz"
ESTIMATES_REL = "docs/reports/data/2026-11-12-q166-progs/estimates.json"
M64 = (1 << 64) - 1

ABI = {"zero": 0, "ra": 1, "sp": 2, "gp": 3, "tp": 4, "t0": 5, "t1": 6, "t2": 7, "s0": 8, "fp": 8, "s1": 9,
       "a0": 10, "a1": 11, "a2": 12, "a3": 13, "a4": 14, "a5": 15, "a6": 16, "a7": 17, "s2": 18, "s3": 19,
       "s4": 20, "s5": 21, "s6": 22, "s7": 23, "s8": 24, "s9": 25, "s10": 26, "s11": 27, "t3": 28, "t4": 29,
       "t5": 30, "t6": 31}
BRANCHES = {"beq", "bne", "bltu", "bgeu", "blt", "bge", "beqz", "bnez"}
JUMPS = {"j", "jal", "ret"}

# entry_point's repetition loop (0x8005801dca-0x8005801de8): mv a2,s3; mv a1,s9; mv a0,s2; sd a5,8(sp); sd a3,0(sp);
# jal copy_keys; mv a2,s3; mv a1,s7; mv a0,s2; jal merge_sort; ld a5,8(sp); ld a3,0(sp); addi a5,a5,1; bne a5,a3
REP_LOOP = {"mv": 6, "sd": 2, "jal": 2, "ld": 2, "addi": 1, "bne": 1}

# the addresses the trace uses when no other is given: an input part, a work area (two buffers) and a stack, each in
# DRAM's cached range; only their low bits matter to a 512 B L1 (set = PA bit 6)
SRC, DST, SP = 0x8100000000, 0x8200000000, 0x8007F00000


def _desk():
    sys.path.insert(0, os.path.join(REPO, "workloads", "ledger"))
    import ledger_desk  # noqa: E402  (the host's inputs, mirrored)
    return ledger_desk


def read_dis(path=None):
    """PC -> (mnemonic, operands, size in bytes) and symbol -> [start, end) from the committed objdump -d -w (.gz)."""
    ins, syms, last = {}, {}, None
    path = path or os.path.join(REPO, DIS_REL)
    fh = gzip.open(path, "rt") if path.endswith(".gz") else open(path)
    with fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.endswith(">:") and " <" in line:
                a, name = line.split(" <", 1)
                last = name[:-2]
                syms[last] = [int(a, 16), None]
                continue
            parts = line.split("\t")
            if len(parts) >= 3 and parts[0].strip().endswith(":"):
                pc = int(parts[0].strip()[:-1], 16)
                size = len(parts[1].strip()) // 2
                ops = parts[3].strip() if len(parts) > 3 else ""
                ops = ops.split("#")[0].strip()
                ins[pc] = (parts[2].strip(), ops, size)
                if last:
                    syms[last][1] = pc + size
    return ins, syms


def s64(x):
    x &= M64
    return x - (1 << 64) if x >> 63 else x


class Mem:
    def __init__(self):
        self.b = {}

    def ld(self, a, n):
        v = 0
        for i in range(n):
            v |= self.b.get(a + i, 0) << (8 * i)
        return v

    def st(self, a, n, v):
        for i in range(n):
            self.b[a + i] = (v >> (8 * i)) & 0xFF


class CPU:
    def __init__(self, ins, mem):
        self.ins = ins
        self.mem = mem
        self.x = [0] * 32
        self.counts = {}
        self.taken = 0
        self.not_taken = 0
        self.jumps = 0
        self.trace = []          # (address, nbytes, is_write), program order

    def r(self, name):
        return self.x[ABI[name]]

    def w(self, name, v):
        if ABI[name]:
            self.x[ABI[name]] = v & M64

    def addr(self, op):
        off, base = op.rstrip(")").split("(")
        return (self.r(base) + int(off, 0)) & M64

    def count(self, mn):
        self.counts[mn] = self.counts.get(mn, 0) + 1

    def call(self, pc, ret_pc=0xDEAD0000):
        """Run from pc until a ret returns to ret_pc."""
        self.w("ra", ret_pc)
        while pc != ret_pc:
            mn, ops, size = self.ins[pc]
            o = [t.strip() for t in ops.split(",")] if ops else []
            nxt = pc + size
            self.count(mn)
            if mn == "li":
                self.w(o[0], int(o[1], 0))
            elif mn == "mv":
                self.w(o[0], self.r(o[1]))
            elif mn == "addi":
                self.w(o[0], self.r(o[1]) + int(o[2], 0))
            elif mn == "add":
                self.w(o[0], self.r(o[1]) + self.r(o[2]))
            elif mn == "sub":
                self.w(o[0], self.r(o[1]) - self.r(o[2]))
            elif mn == "or":
                self.w(o[0], self.r(o[1]) | self.r(o[2]))
            elif mn == "andi":
                self.w(o[0], self.r(o[1]) & (int(o[2], 0) & M64))
            elif mn == "slli":
                self.w(o[0], self.r(o[1]) << int(o[2], 0))
            elif mn == "srli":
                self.w(o[0], self.r(o[1]) >> int(o[2], 0))
            elif mn in ("lw", "ld"):
                n = 4 if mn == "lw" else 8
                a = self.addr(o[1])
                v = self.mem.ld(a, n)
                if mn == "lw" and v >> 31:
                    v |= M64 ^ 0xFFFFFFFF
                self.w(o[0], v)
                self.trace.append((a, n, False))
            elif mn in ("sw", "sd"):
                n = 4 if mn == "sw" else 8
                a = self.addr(o[1])
                self.mem.st(a, n, self.r(o[0]) & ((1 << (8 * n)) - 1))
                self.trace.append((a, n, True))
            elif mn in BRANCHES:
                if mn in ("beqz", "bnez"):
                    a_, b_, tgt = self.r(o[0]), 0, o[1]
                else:
                    a_, b_, tgt = self.r(o[0]), self.r(o[1]), o[2]
                tgt = int(tgt.split()[0], 16)
                cond = {"beq": a_ == b_, "bne": a_ != b_, "beqz": a_ == 0, "bnez": a_ != 0,
                        "bltu": a_ < b_, "bgeu": a_ >= b_, "blt": s64(a_) < s64(b_), "bge": s64(a_) >= s64(b_)}[mn]
                if cond:
                    self.taken += 1
                    nxt = tgt
                else:
                    self.not_taken += 1
            elif mn == "j":
                self.jumps += 1
                nxt = int(o[0].split()[0], 16)
            elif mn == "ret":
                self.jumps += 1
                nxt = self.r("ra")
            else:
                raise SystemExit(f"ledger_interp: instruction {mn} {ops} at {pc:#x} is outside the interpreted subset")
            pc = nxt


def sort_rep(ins, syms, n, p, order, seed=1, src=SRC, dst=DST, sp=SP, reps=2):
    """One participant's sort: the counts of its last repetition (the steady state: reps >= 2) and that repetition's data
    trace. Counts by mnemonic with branches and jumps folded into taken / not_taken / jumps (the counter's classes);
    entry_point's loop added (its bne taken once a repetition, its two jal)."""
    mem = Mem()
    keys = _desk().keys(seed, n, p, order)
    inp = src + p * n * 4
    w0 = dst + p * n * 8
    w1 = w0 + n * 4
    for i, kv in enumerate(keys):
        mem.st(inp + 4 * i, 4, kv)
    for i in range(2 * n):
        mem.st(w0 + 4 * i, 4, 0x5A5A5A5A)
    cpu = CPU(ins, mem)
    per = []
    for _ in range(reps):
        c0 = dict(cpu.counts)
        t0, nt0, j0, tr0 = cpu.taken, cpu.not_taken, cpu.jumps, len(cpu.trace)
        cpu.trace.append((sp + 8, 8, True))           # the repetition loop's own stack stores
        cpu.trace.append((sp + 0, 8, True))
        cpu.w("sp", sp)
        cpu.w("a0", w0)
        cpu.w("a1", inp)
        cpu.w("a2", n)
        cpu.call(syms["copy_keys"][0])
        cpu.w("sp", sp)
        cpu.w("a0", w0)
        cpu.w("a1", w1)
        cpu.w("a2", n)
        cpu.call(syms["merge_sort"][0])
        cpu.trace.append((sp + 8, 8, False))          # and its loads
        cpu.trace.append((sp + 0, 8, False))
        d = {k: cpu.counts.get(k, 0) - c0.get(k, 0) for k in cpu.counts}
        for k, v in REP_LOOP.items():
            d[k] = d.get(k, 0) + v
        tk = cpu.taken - t0 + 1
        jm = cpu.jumps - j0 + 2
        ntk = cpu.not_taken - nt0
        d = {k: v for k, v in d.items() if v}
        per.append({"counts": d, "instructions": sum(d.values()), "taken": tk, "not_taken": ntk, "jumps": jm,
                    "trace": cpu.trace[tr0:]})
    return per[-1]


def counter_form(r):
    """A repetition's counts in the counter's form (ledger_estimate.vec): mnemonics without branches and jumps, plus
    @taken / @not_taken / @jump."""
    v = {m: c for m, c in r["counts"].items() if m not in BRANCHES and m not in JUMPS}
    v["@taken"], v["@not_taken"], v["@jump"] = r["taken"], r["not_taken"], r["jumps"]
    return v


def sort_counts(n, order, participants, seed=1, dis=None):
    """Per participant: instructions, taken branches + jumps (B) and the counter-form counts of one sort; and their mean."""
    ins, syms = dis or read_dis()
    rows = {}
    mean = {}
    for p in participants:
        r = sort_rep(ins, syms, n, p, order, seed=seed)
        v = counter_form(r)
        rows[p] = {"instructions": r["instructions"], "B": r["taken"] + r["jumps"], "counts": v}
        for k, c in v.items():
            mean[k] = mean.get(k, 0.0) + c
    k = len(rows)
    mean = {m: c / k for m, c in sorted(mean.items())}
    return {"per_participant": rows, "mean": mean, "participants": k}


def check512(dis=None):
    """The counter's committed per-sort counts at 512 keys (Q166 estimates.json) against this interpreter's, mean of
    participants 0-63 (shire 0, as the simulator logged them), mnemonic by mnemonic."""
    ref = json.load(open(os.path.join(REPO, ESTIMATES_REL)))["programs"]
    out = {}
    d = dis or read_dis()
    for order in ("sorted", "shuffled"):
        mine = sort_counts(512, order, range(64), dis=d)["mean"]
        cref = ref["sort-" + order]["per_unit_per_participant"]
        diffs = {k: [mine.get(k, 0.0), cref.get(k, 0.0)] for k in sorted(set(mine) | set(cref))
                 if abs(mine.get(k, 0.0) - cref.get(k, 0.0)) > 1e-6}
        out[order] = {"interpreter_total": sum(mine.values()), "counter_total": sum(cref.values()), "differences": diffs,
                      "same": not diffs}
    return out


def _parts(s):
    out = []
    for piece in s.split(","):
        if "-" in piece:
            a, b = piece.split("-")
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(piece))
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="reproduce the counter's per-sort counts at 512 keys")
    ap.add_argument("--keys", type=int)
    ap.add_argument("--order", choices=["sorted", "shuffled"], default="shuffled")
    ap.add_argument("--participants", default="0-63", help="e.g. 0-2047 or 0,5,9")
    ap.add_argument("--seed", type=lambda x: int(x, 0), default=1)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if a.check:
        res = check512()
        ok = all(v["same"] for v in res.values())
        for o, v in res.items():
            print(f"512 keys {o:8s}: interpreter {v['interpreter_total']:.5f} instructions a sort, counter "
                  f"{v['counter_total']:.5f}; differences {v['differences'] if v['differences'] else 'none'}")
        print("INTERP CHECK " + ("PASS" if ok else "FAIL"))
        if a.out:
            json.dump(res, open(a.out, "w"), indent=1, sort_keys=True)
        return 0 if ok else 1
    if not a.keys:
        ap.error("--keys or --check")
    res = sort_counts(a.keys, a.order, _parts(a.participants), seed=a.seed)
    ins = [v["instructions"] for v in res["per_participant"].values()]
    bs = [v["B"] for v in res["per_participant"].values()]
    print(f"sort {a.keys} {a.order}: {res['participants']} participants; instructions a sort mean "
          f"{sum(ins) / len(ins):.3f} (min {min(ins)}, max {max(ins)}); taken + jumps mean {sum(bs) / len(bs):.3f} "
          f"(min {min(bs)}, max {max(bs)})")
    if a.out:
        json.dump({"keys": a.keys, "order": a.order, "seed": a.seed, "mean": res["mean"],
                   "per_participant": {str(p): {"instructions": v["instructions"], "B": v["B"]}
                                       for p, v in res["per_participant"].items()}},
                  open(a.out, "w"), indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
