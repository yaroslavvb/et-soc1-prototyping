#!/usr/bin/env python3
"""The counter: a kernel file's run in the functional simulator, turned into the energy ledger's counts.

    count_kernel.py count --dis KERNEL.dis (--log sysemu.log[.gz] | --prof prof.txt[.gz]) --out counts.json
                          [--threads 0,1,..] [--pc-offset auto|0xHEX] [--pc-offset-from LOG.json]
                          [--assume-no-wait] [--tensor-map LOG.json] [--label TEXT]
    count_kernel.py compare A.json B.json            # two counts files, hart by hart and class by class
    count_kernel.py table counts.json                # instructions by class, per hart and in total
    count_kernel.py classes                          # the class of every mnemonic the table knows

KERNEL.dis is the ET toolchain's `riscv64-unknown-elf-objdump -d -w` of the kernel ELF. Two inputs, one schema:

  --log   the simulator's instruction log (`--sim-args "-l -ls <shire>,<hart mask> ..."`; the runtime writes it to
          sysemu.log in the host's working directory). Exact: every retired instruction of every logged hart,
          each conditional branch's direction, every memory access's address and size, and every tensor
          operation's format and shape. About 400 B per instruction, so it is read in one pass and may be a pipe:
          run_counted.sh makes sysemu.log a FIFO and nothing of the log is kept.
  --prof  the profiling simulator's block histogram (`--sim-args "-dump_prof <path>"`, only in a simulator built
          with PROFILING=ON plus -DBEMU_PROFILING -DSYSEMU_PROFILING; README.md, "The profiling simulator"): for
          every hart and every PC that a taken branch, jump, trap or return landed on, the number of landings and
          the emulated cycles until the hart's next landing. Small, and covers every hart. The counter rebuilds
          each instruction's execution count from it by flow conservation (below); the tensor formats come from
          the constant the kernel loads into the register it writes to tensor_fma, or from a log of the same
          kernel (--tensor-map).

How the profile becomes counts (desk check of code; validated against the log in README.md). A landing at u
starts a run of straight-line code that ends at the first control transfer actually taken. For each landing PC
u the run's possible ends are the conditional branches after u and the first unconditional transfer. Unknowns:
e[u][x], the landings at u whose run ended at transfer x. Equations: (1) sum over x of e[u][x] = landings at u;
(2) every taken direct transfer x lands on its target v, so sum over u of e[u][x] over all x aimed at v, plus
the returns and traps that land on v, = landings at v; (3) a run that holds no instruction able to make the hart
wait (tensor CSR writes, fcc, flb, stall, wfi) takes one emulated cycle per instruction, so sum over x of
e[u][x] * (instructions from u to x) = the cycles recorded for u (--assume-no-wait applies it to every run:
true when the hart never waited, which a log of the same kernel shows: its cycles_span equals its instructions).
The solver propagates exact integer solutions, enumerates landings counted at most 4 times, and eliminates over
fractions; a pair it cannot pin is listed in `unresolved` and left out of the counts, never guessed. The wait set of
(3) does not hold the FP/vector stall: while thread 0's core has a tensor operation queued, sw-sysemu holds thread 0
at its next float or vector instruction (insn_util.h require_fp_active) until the FMA, quant or reduce is done. A run
holding one can then take more cycles than instructions; such a run is taken for no-wait by (3), so that "lower
bound" rests on the check against the log (README.md), not on a proof: 0 PCs above the log in 11 runs. The offset
of the kernel in the profile is found by `--pc-offset auto` (every 4 KB-aligned candidate scored by the landing
places it explains), or given by `--pc-offset` or `--pc-offset-from` (a log counts file of the same kernel).

Log mode also reports, apart from the kernel's counts: `outside_kernel` (what each logged hart retired outside the
kernel's U-mode text, by privilege mode, with its tensor ops and memory traffic: the firmware around each launch),
per hart `branch_direction_changes` and `branch_changes_per_pc` (a conditional branch's outcome flipping from one
execution to the next: 03a prices a branch that follows the data at about 2.5x a predictable one), and in both
modes `by_csr` (CSR accesses by instruction and CSR name, which `by_mnemonic` lumps together). Masked tensor loads
count only the rows their mask sets (the Execute line's tmask; a masked TensorLoadL2SCP reads the hart's last logged
tensor_mask, else all rows are counted and `masked_ops_rows_assumed_all` says so). `memory["tensor"]` holds the
bytes the tensor instructions moved as the simulator's MEM lines show them: the same bytes as the `tensor` block's
`bytes_*` (plus a TensorLoadL2SCP's write into the scratchpad), so never add the two. Counts add up over every
launch of one host run.

The classes are the energy manual's (docs/energy-manual/03a-every-instruction.md, 03-instructions.md section
3.2 and 04-bytes-memory.md): see CLASSES below. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import gzip
import hashlib
import json
import re
import sys

SCHEMA = "ledger-counts/1"

# ---------------------------------------------------------------------------------------------------------------
# Classes, each with the energy manual section that prices it.
CLASSES = collections.OrderedDict([
    ("scalar_int", "03a: Scalar integer, one cycle (and the compressed forms)"),
    ("int_muldiv", "03a: Scalar integer multiply and divide"),
    ("scalar_float", "03a: Scalar float"),
    ("float_int_xfer", "03a: Between the float and integer register files"),
    ("vector_float", "03a: Vector float, 8 lanes"),
    ("vector_int", "03a: Vector integer, 8 lanes"),
    ("transcendental", "03a: Transcendental unit, 8 lanes"),
    ("mask_broadcast", "03a: Masks and broadcasts (and the mask-register moves)"),
    ("load", "03a: Loads and stores that hit the L1 (loads; the level each one reached is 04's question)"),
    ("store", "03a: Loads and stores that hit the L1 (stores)"),
    ("load_past_l1", "03a: Loads and stores that bypass the L1 (flwl.ps to the L2, flwg.ps to the home L3)"),
    ("store_past_l1", "03a: Loads and stores that bypass the L1 (fswl.ps, fswg.ps)"),
    ("gather_scatter", "03a: Gathers, scatters and packed atomics, from the L1 (E48); 04 section 4.4 by level"),
    ("gather_scatter_past_l1", "04 section 4.4: gathers and scatters that bypass the L1 (fgwl.ps and fscwl.ps to "
                               "the L2, fgwg.ps and fscwg.ps to the home), 27x or more the L1 form"),
    ("branch_taken", "03a: Branches and jumps (a conditional branch taken)"),
    ("branch_not_taken", "03a: Branches and jumps (a conditional branch not taken)"),
    ("jump", "03a: Branches and jumps (jal, jalr: calls, returns, jumps)"),
    ("atomic_local", "03a: Atomics on a private line (amo*l: at the shire's L2)"),
    ("atomic_global", "03a: Atomics on a private line (amo*g: at the line's home); 06 for shared lines"),
    ("atomic_packed", "03a: Gathers, scatters and packed atomics (famo*.pi)"),
    ("atomic_std", "no row: standard RISC-V A-extension forms (lr, sc, amo*.w/d without l or g)"),
    ("tensor", "03 section 3.2 (TensorFMA by format) and 04 (tensor loads and stores by level)"),
    ("cache_op", "no row of its own: cache-control CSR writes (evict, flush, prefetch, lock)"),
    ("sync", "06: credit counters, the fast local barrier, stall (fcc, fccnb, flb, stall)"),
    ("system", "03a: System (fence, csrr, ecall and the other CSR accesses)"),
    ("trap", "03a: the thirteen instructions that trap in U-mode (no energy; the kernel ends)"),
    ("unknown", "not classified: the table below has no rule for it"),
])

BRANCH_COND = {"beq", "bne", "blt", "bge", "bltu", "bgeu", "beqz", "bnez", "blez", "bgez", "bltz", "bgtz",
               "bgt", "ble", "bgtu", "bleu", "c.beqz", "c.bnez"}
JUMPS = {"jal", "jalr", "j", "jr", "ret", "call", "tail", "c.j", "c.jal", "c.jr", "c.jalr"}
XRET = {"mret", "sret", "uret", "dret"}

SCALAR_INT = set("""add sub and or xor sll srl sra slt sltu addw subw sllw srlw sraw addi andi ori xori slli srli srai
slti sltiu addiw slliw srliw sraiw lui auipc nop li mv not neg negw sext.w seqz snez sltz sgtz zext.b zext.h
zext.w sext.b sext.h c.add c.addi c.addiw c.addw c.and c.andi c.li c.lui c.mv c.nop c.or c.slli c.srai c.srli
c.sub c.subw c.xor c.addi16sp c.addi4spn rol ror rori rolw rorw roriw andn orn xnor clz ctz cpop min max minu
maxu""".split())
INT_MULDIV = set("mul mulh mulhu mulhsu mulw div divu rem remu divw divuw remw remuw".split())
TRAPS = {"fdiv.s", "fsqrt.s", "fdiv.ps", "fsqrt.ps", "frsq.ps", "fsin.ps", "fdiv.pi", "fdivu.pi", "frem.pi",
         "fremu.pi", "fcvt.l.s", "fcvt.s.l", "fcvt.lu.s", "fcvt.s.lu"}
TRAP_CSRS = {"cycle", "time", "instret", "mcycle", "minstret"}   # 03a: `csrr cycle` traps in U-mode
SCALAR_FLOAT = set("""fadd.s fsub.s fmul.s fmin.s fmax.s fsgnj.s fsgnjn.s fsgnjx.s fmadd.s fmsub.s fnmadd.s fnmsub.s
fmv.s fneg.s fabs.s""".split())
FLOAT_INT_XFER = set("""feq.s flt.s fle.s fclass.s fcvt.w.s fcvt.wu.s fmv.x.w fmv.x.s fcvt.s.w fcvt.s.wu fmv.w.x
fmv.s.x""".split())
TRANSCENDENTAL = {"fexp.ps", "flog.ps", "frcp.ps", "frcpfxp.ps", "fexp2.ps", "flog2.ps"}
MASK = set("""feqm.ps fltm.ps flem.ps feqm.pi fltm.pi fltum.pi flem.pi fbcx.ps fbci.ps fbci.pi fbc.ps mov.m.x
mova.x.m mova.m.x maskand maskor maskxor masknot maskpopc maskpopcz maskpopc.rast""".split())
VLOAD_L1 = {"flw.ps", "flq2", "flwr.ps", "fbcx.ps.mem", "fld.ps"}
VSTORE_L1 = {"fsw.ps", "fsq2", "fswr.ps"}
LOADS = {"lb", "lh", "lw", "ld", "lbu", "lhu", "lwu", "flw", "fld", "c.lw", "c.ld", "c.lwsp", "c.ldsp", "c.flw",
         "c.flwsp"} | VLOAD_L1
STORES = {"sb", "sh", "sw", "sd", "fsw", "fsd", "c.sw", "c.sd", "c.swsp", "c.sdsp", "c.fsw", "c.fswsp"} | VSTORE_L1
LOAD_PAST = {"flwl.ps": "l2", "flwg.ps": "home", "flql": "l2", "flqg": "home"}
STORE_PAST = {"fswl.ps": "l2", "fswg.ps": "home", "fsql": "l2", "fsqg": "home"}
MEM_BYTES = {"lb": 1, "lbu": 1, "sb": 1, "lh": 2, "lhu": 2, "sh": 2, "lw": 4, "lwu": 4, "sw": 4, "flw": 4,
             "fsw": 4, "ld": 8, "sd": 8, "fld": 8, "fsd": 8, "flw.ps": 32, "fsw.ps": 32, "flwl.ps": 32,
             "fswl.ps": 32, "flwg.ps": 32, "fswg.ps": 32, "flq2": 32, "fsq2": 32}
TENSOR_CSRS = {"tensor_reduce", "tensor_fma", "tensor_conv_size", "tensor_conv_ctrl", "tensor_coop", "tensor_mask",
               "tensor_quant", "tex_send", "tensor_wait", "tensor_load", "tensor_load_l2", "tensor_store"}
CACHE_CSRS = {"cache_invalidate", "evict_sw", "flush_sw", "lock_sw", "unlock_sw", "prefetch_va", "evict_va",
              "flush_va", "lock_va", "unlock_va", "ucache_control"}
SYNC_CSRS = {"fcc", "fccnb", "flb", "stall"}
WAIT_CSRS = TENSOR_CSRS | {"fcc", "flb", "stall"}   # a write here may hold the hart: its run has no cycle equation
CSR_OPS = {"csrrw", "csrrs", "csrrc", "csrrwi", "csrrsi", "csrrci", "csrr", "csrw", "csrs", "csrc", "csrwi",
           "csrsi", "csrci"}
SYSTEM = {"fence", "fence.i", "fence.tso", "ecall", "ebreak", "c.ebreak", "wfi", "sfence.vma"} | XRET
TFMA_TYPES = {0: "fp32", 1: "fp16", 3: "int8"}


def classify(mn, ops=""):
    """The class of one instruction, from its mnemonic and operand text (objdump's or the simulator's)."""
    if mn in TRAPS or (mn.endswith(".d") and mn.startswith("f") and mn not in ("fld", "fsd")):
        return "trap"
    if mn in ("csrr", "csrrs", "rdcycle", "rdtime", "rdinstret"):
        csr = csr_of(mn, ops)
        if csr in TRAP_CSRS or mn in ("rdcycle", "rdtime", "rdinstret"):
            return "trap"
    if mn in BRANCH_COND:
        return "branch"   # split into taken and not taken by the counts
    if mn in JUMPS:
        return "jump"
    if mn in SCALAR_INT:
        return "scalar_int"
    if mn in INT_MULDIV:
        return "int_muldiv"
    if mn in SCALAR_FLOAT:
        return "scalar_float"
    if mn in FLOAT_INT_XFER:
        return "float_int_xfer"
    if mn in TRANSCENDENTAL:
        return "transcendental"
    if mn in MASK:
        return "mask_broadcast"
    if mn in LOAD_PAST:
        return "load_past_l1"
    if mn in STORE_PAST:
        return "store_past_l1"
    if re.match(r"^f(g|sc)[bhw][lg]\.ps$", mn):          # fgwl.ps to the L2, fgwg.ps to the home; fscwl/fscwg
        return "gather_scatter_past_l1"
    if re.match(r"^f(g|sc)(32)?[bhw]\.ps$", mn):
        return "gather_scatter"
    if mn.startswith("fcvt.ps."):                        # fcvt.ps.pw (03a's vector float row), .pwu, .f16, ...
        return "vector_float"
    if mn.startswith("famo"):
        return "atomic_packed"
    if re.match(r"^amo[a-z]+l\.[wd]$", mn):
        return "atomic_local"
    if re.match(r"^amo[a-z]+g\.[wd]$", mn):
        return "atomic_global"
    if re.match(r"^(amo[a-z]+|lr|sc)\.[wd](\.aq|\.rl|\.aqrl)?$", mn):
        return "atomic_std"
    if mn in LOADS:
        return "load"
    if mn in STORES:
        return "store"
    if mn in CSR_OPS:
        csr = csr_of(mn, ops)
        if csr in TENSOR_CSRS:
            return "tensor"
        if csr in CACHE_CSRS:
            return "cache_op"
        if csr in SYNC_CSRS:
            return "sync"
        return "system"
    if mn in SYSTEM:
        return "system"
    if mn.endswith(".pi"):
        return "vector_int"
    if mn.endswith(".ps"):
        return "vector_float"
    return "unknown"


def csr_of(mn, ops):
    """The CSR an instruction names: objdump writes `csrw tensor_fma,a5`, the simulator `csrrw x0,tensor_fma,x14`."""
    parts = [p.strip() for p in ops.split("#")[0].split(",") if p.strip()]
    if mn in ("csrr",):
        return parts[1] if len(parts) > 1 else ""
    if mn in ("csrw", "csrs", "csrc", "csrwi", "csrsi", "csrci"):
        return parts[0] if parts else ""
    if mn in ("csrrw", "csrrs", "csrrc", "csrrwi", "csrrsi", "csrrci"):
        return parts[1] if len(parts) > 1 else ""
    return ""


def is_csr_write(mn, ops):
    if mn in ("csrw", "csrs", "csrc", "csrwi", "csrsi", "csrci", "csrrw", "csrrwi"):
        return True
    if mn in ("csrrs", "csrrc", "csrrsi", "csrrci"):
        parts = [p.strip() for p in ops.split(",")]
        return len(parts) > 2 and parts[2] not in ("zero", "x0", "0")
    return False


# ---------------------------------------------------------------------------------------------------------------
# The disassembly.
DIS_LINE = re.compile(r"^\s*([0-9a-f]+):\s+([0-9a-f]{4}|[0-9a-f]{8})\s+(\S+)\s*(.*)$")
SYM_LINE = re.compile(r"^([0-9a-f]+) <([^>]+)>:\s*$")
TARGET_HEX = re.compile(r"(?:^|,)\s*([0-9a-f]{6,16})\s*(?:<[^>]*>)?\s*$")


class Insn:
    __slots__ = ("addr", "bits", "size", "mn", "ops", "fn", "cls", "kind", "target", "csr", "csrw", "wait",
                 "chain")

    def __init__(self, addr, bits, mn, ops, fn):
        self.addr, self.bits, self.mn, self.ops, self.fn = addr, bits, mn, ops, fn
        self.chain = []           # an inline chain from addr2line, when a caller sets one
        self.size = len(bits) // 2
        self.cls = classify(mn, ops)
        self.csr = csr_of(mn, ops) if mn in CSR_OPS else ""
        self.csrw = mn in CSR_OPS and is_csr_write(mn, ops)
        self.wait = self.csrw and self.csr in WAIT_CSRS or mn == "wfi" or (mn in CSR_OPS and self.csr == "fcc")
        self.target = None
        if mn in BRANCH_COND:
            self.kind = "cond"
        elif mn in ("jal", "j", "call", "tail", "c.j", "c.jal"):
            self.kind = "jump_direct"
        elif mn in ("jalr", "jr", "ret", "c.jr", "c.jalr"):
            self.kind = "jump_indirect"
        elif mn in ("ecall", "ebreak", "c.ebreak") or self.cls == "trap":
            self.kind = "trap"
        elif mn in XRET:
            self.kind = "xret"
        else:
            self.kind = "seq"
        if self.kind in ("cond", "jump_direct"):
            m = TARGET_HEX.search(ops.split("#")[0])
            if m:
                self.target = int(m.group(1), 16)

    def unconditional(self):
        return self.kind in ("jump_direct", "jump_indirect", "trap", "xret")

    def transfers(self):
        return self.kind != "seq"


def read_text(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", errors="replace") as f:
        return f.read()


def parse_dis(path):
    insns, fn = [], ""
    for line in read_text(path).splitlines():
        m = SYM_LINE.match(line)
        if m:
            fn = m.group(2)
            continue
        m = DIS_LINE.match(line)
        if not m:
            continue
        addr, bits, mn, ops = int(m.group(1), 16), m.group(2), m.group(3), m.group(4).strip()
        if mn.startswith("."):    # .insn / .word: data in .text
            mn = "unknown"
        insns.append(Insn(addr, bits, mn, ops, fn))
    insns.sort(key=lambda i: i.addr)
    return insns


# ---------------------------------------------------------------------------------------------------------------
# Constant tracking for tensor_fma's control word (profile mode): li/lui/addi/ori/xori/slli/srli/addiw within the
# block that ends at the csr write, reading the register the write names.
def reg_alias(r):
    names = ["zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2", "s0", "s1"] + [f"a{i}" for i in range(8)] + \
            [f"s{i}" for i in range(2, 12)] + [f"t{i}" for i in range(3, 7)]
    r = r.strip()
    if r == "fp":
        return "s0"
    if r.startswith("x") and r[1:].isdigit():
        return names[int(r[1:])]
    return r


def const_before(insns, idx, reg, leaders):
    """The constant in `reg` just before insns[idx], tracked back to the block's leader; None when unknown."""
    seq, j = [], idx - 1
    while j >= 0 and insns[j].addr not in leaders and not insns[j].transfers():
        seq.append(insns[j])
        j -= 1
    if j >= 0 and insns[j].addr in leaders and not insns[j].transfers():
        seq.append(insns[j])
    seq.reverse()
    vals = {}
    for ins in seq:
        p = [x.strip() for x in ins.ops.split("#")[0].split(",")]
        try:
            if ins.mn == "li" and len(p) == 2:
                vals[reg_alias(p[0])] = int(p[1], 0) & (2**64 - 1)
            elif ins.mn == "lui" and len(p) == 2:
                vals[reg_alias(p[0])] = (int(p[1], 0) << 12) & (2**64 - 1)
            elif ins.mn in ("addi", "addiw", "ori", "xori", "andi", "slli", "srli") and len(p) == 3:
                src = reg_alias(p[1])
                if src in vals or src == "zero":
                    v, imm = vals.get(src, 0), int(p[2], 0)
                    v = {"addi": v + imm, "addiw": v + imm, "ori": v | imm, "xori": v ^ imm, "andi": v & imm,
                         "slli": v << imm, "srli": v >> imm}[ins.mn] & (2**64 - 1)
                    vals[reg_alias(p[0])] = v
                else:
                    vals.pop(reg_alias(p[0]), None)
            elif ins.mn == "mv" and len(p) == 2:
                src = reg_alias(p[1])
                if src in vals:
                    vals[reg_alias(p[0])] = vals[src]
                else:
                    vals.pop(reg_alias(p[0]), None)
            elif p and p[0]:
                vals.pop(reg_alias(p[0]), None)
        except ValueError:
            if p and p[0]:
                vals.pop(reg_alias(p[0]), None)
    return vals.get(reg_alias(reg))


def tfma_from_control(v):
    arows = ((v >> 51) & 0xF) + 1
    acols = ((v >> 47) & 0xF) + 1
    bcols = (((v >> 55) & 3) + 1) * 4
    fmt = TFMA_TYPES.get((v >> 1) & 7, "type%d" % ((v >> 1) & 7))
    k = acols * {"fp32": 1, "fp16": 2, "int8": 4}.get(fmt, 1)
    return fmt, arows * k * bcols


# ---------------------------------------------------------------------------------------------------------------
# Memory regions by physical address (sw-sysemu memmap.h; PRM 15.3 for the scratchpad's shire field).
def region_of(addr, own_shire):
    if addr < 0x0040000000:
        return "io"
    if addr < 0x0080000000:
        return "sp"
    if addr < 0x0100000000:
        sh = (addr >> 23) & 0x7F
        if sh == 0x7F or sh == own_shire:
            return "scratchpad_own"
        return "scratchpad_remote"
    if addr < 0x0200000000:
        return "esr"
    if addr < 0x4000000000:
        return "reserved"
    if addr < 0x8000000000:
        return "pcie"
    if addr & 0x4000000000:
        return "dram_uncached"
    return "dram"


# ---------------------------------------------------------------------------------------------------------------
class HartCounts:
    def __init__(self, tid):
        self.tid = tid
        self.pc_exec = collections.Counter()      # retired executions per PC
        self.pc_taken = collections.Counter()     # taken count per PC (conditional branches)
        self.pc_dirchg = collections.Counter()    # direction changes per PC (conditional branches, log mode)
        self.pc_lastdir = {}
        self.tensor = collections.defaultdict(lambda: collections.Counter())
        self.tensor_by_pc = {}
        self.mem = collections.defaultdict(lambda: collections.Counter())
        self.killed = 0
        self.cycles_first = None
        self.cycles_last = None


class OutsideCounts:
    """What a hart retired OUTSIDE the kernel's U-mode text (the firmware around each launch, in M and S mode, and
    any U-mode instruction outside .text): counted apart, never mixed into the kernel's counts."""

    def __init__(self):
        self.by_mode = collections.Counter()
        self.tensor = collections.defaultdict(lambda: collections.Counter())
        self.mem = collections.defaultdict(lambda: collections.Counter())
        self.killed = 0


def hart_place(tid):
    return {"shire": tid // 64, "minion": (tid % 64) // 2, "hart": tid % 2}


LOG_I = re.compile(r"^(\d+): DEBUG EMU: \[H(\d+) S(\d+):N\d+:C\d+:T\d+\] I\((.)\): 0x([0-9a-f]+) \(0x([0-9a-f]+)\) (\S+)\s*(.*)$")
LOG_D = re.compile(r"^(\d+): DEBUG EMU: \[H(\d+) S(\d+):N\d+:C\d+:T\d+\] (.*)$")
MEM_RE = re.compile(r"MEM(\d+)\[0x([0-9a-f]+)\] ([:=])")
TSTART = re.compile(r"Start (?:/Execute )?(TensorFMA32|TensorFMA16A32|TensorIMA8A32|TensorLoad|TensorLoadL2SCP|"
                    r"TensorStore|TensorStoreFromScp|TensorQuant|TensorReduce|TensorSend|TensorRecv|"
                    r"TensorBroadcast|TensorLoadInterleave8|TensorLoadInterleave16|TensorLoadTranspose8|"
                    r"TensorLoadTranspose16|TensorLoadTranspose32)\b(.*)$")
TSTART2 = re.compile(r"Start/Execute (TensorLoadL2SCP|TensorStoreFromScp)\b(.*)$")
TUUID = re.compile(r"\((T[A-Z]-H\d+-\d+)\) (?:Start|Execute) ")
TEXEC_LOAD = re.compile(r"\((TL-H\d+-\d+)\) Execute TensorLoad with .*\btmask: 0x([0-9a-f]+)")
TMASK_LINE = re.compile(r"^\s*tensor_mask [:=] 0x([0-9a-f]+)")
# A field is `name: value` (`msk:0` in TensorLoadL2SCP's line has no space). sw-sysemu 353f20e prints the TensorLoad
# family's addr and stride as 0x%PRIx64 but TensorStore's and TensorStoreFromScp's as %016 PRIx64, hex WITHOUT 0x
# (insns/tensors.cpp 358, 734, 1038, 1100): `addr` and `stride` are always read as hex, every other field as decimal
# (or hex when it carries 0x). A token must end at a word boundary, so a word such as `rm: dyn` is never half read.
KV = re.compile(r"(\w+): ?(0x[0-9a-fA-F]+\b|-?[0-9a-fA-F]+\b)")
HEX_FIELDS = {"addr", "stride"}


def kv_fields(rest):
    out = {}
    for k, v in KV.findall(rest):
        if v.lower().startswith("0x") or k in HEX_FIELDS:
            try:
                out[k] = int(v, 16)
            except ValueError:
                continue
        elif re.fullmatch(r"-?\d+", v):
            out[k] = int(v, 10)
    return out


def tensor_shape(name, rest):
    kv = kv_fields(rest)
    if name in ("TensorFMA32", "TensorFMA16A32", "TensorIMA8A32"):
        fmt = {"TensorFMA32": "fp32", "TensorFMA16A32": "fp16", "TensorIMA8A32": "int8"}[name]
        macs = kv.get("arows", 0) * kv.get("acols", 0) * kv.get("bcols", 0)   # the log prints acols in elements
        return "fma_" + fmt, {"ops": 1, "macs": macs}
    if name.startswith("TensorLoad"):
        rows = kv.get("rows", 0)
        key = "load_l2scp" if name == "TensorLoadL2SCP" else ("load_tenb" if kv.get("tenb") else "load")
        return key, {"ops": 1, "bytes": rows * 64, "addr": kv.get("addr", 0), "_msk": kv.get("msk", 0),
                     "_rows": rows}
    if name.startswith("TensorStore"):
        rows, cols = kv.get("rows", 0), kv.get("cols", 4)
        nbytes = rows * 64 if name == "TensorStoreFromScp" else rows * cols * 16   # 64 B lines; cols x 16 B a row
        return "store", {"ops": 1, "bytes": nbytes, "addr": kv.get("addr", 0)}
    return name.lower(), {"ops": 1}


def masked_bytes(mask, rows):
    """A masked tensor load moves the rows whose mask bit is set (tensors.cpp: `if (!msk || tmask[i])`)."""
    return 64 * bin(mask & ((1 << rows) - 1)).count("1")


def offset_from_prefix(f, insns, limit=5000):
    """PC minus VMA from the first U-mode lines, in one pass (the log may be a pipe): returns (offset, buffered
    lines). Each U-mode line votes PC - a for every instruction a of the kernel with the same raw bits."""
    bits = collections.defaultdict(list)
    for i in insns:
        bits[int(i.bits, 16)].append(i.addr)
    votes, buf, seen = collections.Counter(), [], 0
    for line in f:
        buf.append(line)
        m = LOG_I.match(line)
        if not m or m.group(4) != "U":
            continue
        pc, b = int(m.group(5), 16), int(m.group(6), 16)
        for a in bits.get(b, ()):
            votes[pc - a] += 1
        seen += 1
        if seen % 256 == 0 or seen >= limit:
            top = votes.most_common(2)
            if top and top[0][1] >= 64 and (len(top) == 1 or top[1][1] * 8 <= top[0][1]):
                return top[0][0], buf
            if seen >= limit:
                break
    if not votes:
        raise SystemExit("log: no U-mode instruction matches the disassembly")
    return votes.most_common(1)[0][0], buf


def count_log(path, insns, pc_offset, threads):
    op = gzip.open if path.endswith(".gz") else open
    f = op(path, "rt", errors="replace")
    buf = []
    if pc_offset is None:
        pc_offset, buf = offset_from_prefix(f, insns)
    lo = insns[0].addr + pc_offset
    hi = insns[-1].addr + insns[-1].size + pc_offset
    by_pc = {i.addr + pc_offset: i for i in insns}
    harts = {}
    outside = {}      # tid -> OutsideCounts: what the hart retired outside the kernel's U-mode text
    cur = {}          # tid -> ("in", pc, insn, shire) or ("out", mode, shire): what the next detail lines belong to
    pending_br = {}   # tid -> pc of a conditional branch whose direction the next instruction decides
    pending_mask = {}  # (tid, uuid) -> (counter dict, region key, rows): a masked TensorLoad awaiting its Execute line
    last_tmask = {}   # tid -> the tensor_mask value last logged (a masked TensorLoadL2SCP reads it)
    import itertools

    def add_tensor(t, d, shire):
        for k, v in d.items():
            if k != "addr" and not k.startswith("_"):
                t[k] += v
        if "addr" in d:
            t["bytes_" + region_of(d["addr"], shire)] += d.get("bytes", 0)

    with f:
        for line in itertools.chain(buf, f):
            m = LOG_I.match(line)
            if m:
                cyc, tid, shire, prv, pc = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4), int(m.group(5), 16)
                if threads is not None and tid not in threads:
                    continue
                inreg = prv == "U" and lo <= pc < hi
                if tid in pending_br:
                    bpc = pending_br.pop(tid)
                    hb = harts[tid]
                    tk = pc != bpc + by_pc[bpc].size
                    if tk:
                        hb.pc_taken[bpc] += 1
                    last = hb.pc_lastdir.get(bpc)
                    if last is not None and last != tk:
                        hb.pc_dirchg[bpc] += 1
                    hb.pc_lastdir[bpc] = tk
                if not inreg:
                    mode = prv if prv != "U" else "U_outside_text"
                    o = outside.get(tid)
                    if o is None:
                        o = outside[tid] = OutsideCounts()
                    o.by_mode[mode] += 1
                    cur[tid] = ("out", mode, shire, o)
                    continue
                h = harts.get(tid)
                if h is None:
                    h = harts[tid] = HartCounts(tid)
                ins = by_pc.get(pc)
                if ins is None:
                    raise SystemExit(f"log: PC 0x{pc:x} of hart {tid} is not an instruction boundary of the "
                                     f"disassembly at offset 0x{pc_offset:x}")
                h.pc_exec[pc] += 1
                if h.cycles_first is None:
                    h.cycles_first = cyc
                h.cycles_last = cyc
                cur[tid] = ("in", pc, ins, shire)
                if ins.kind == "cond":
                    pending_br[tid] = pc
                continue
            m = LOG_D.match(line)
            if not m:
                continue
            tid = int(m.group(2))
            rest = m.group(4)
            mk = TMASK_LINE.match(rest)
            if mk:
                last_tmask[tid] = int(mk.group(1), 16)
            me = TEXEC_LOAD.search(rest)
            if me and (tid, me.group(1)) in pending_mask:     # a masked load's Execute line: only its set rows moved
                t, rk, rows = pending_mask.pop((tid, me.group(1)))
                excess = rows * 64 - masked_bytes(int(me.group(2), 16), rows)
                t["bytes"] -= excess
                t[rk] -= excess
                t["masked_ops"] += 1
                continue
            c = cur.get(tid)
            if not c:
                continue
            if c[0] == "out":
                _, mode, shire, o = c
                if "Instruction killed and will be restarted" in rest:
                    o.by_mode[mode] -= 1
                    o.killed += 1
                    cur[tid] = None
                    continue
                mm = MEM_RE.search(rest)
                if mm and not rest.lstrip().startswith("("):
                    reg = region_of(int(mm.group(2), 16), shire)
                    rw = "read" if mm.group(3) == ":" else "write"
                    o.mem[(mode, reg)][rw + "_bytes"] += int(mm.group(1)) // 8
                    o.mem[(mode, reg)][rw + "s"] += 1
                    continue
                mt = TSTART2.search(rest) or (TSTART.search(rest) if "Start" in rest else None)
                if mt:
                    key, d = tensor_shape(mt.group(1), mt.group(2))
                    add_tensor(o.tensor[key], d, shire)
                continue
            _, pc, ins, shire = c
            h = harts[tid]
            if "Instruction killed and will be restarted" in rest:
                h.pc_exec[pc] -= 1
                h.killed += 1
                pending_br.pop(tid, None)
                cur[tid] = None
                continue
            mm = MEM_RE.search(rest)
            if mm and not rest.lstrip().startswith("("):
                nbytes = int(mm.group(1)) // 8
                reg = region_of(int(mm.group(2), 16), shire)
                rw = "read" if mm.group(3) == ":" else "write"
                h.mem[(ins.cls, reg)][rw + "_bytes"] += nbytes
                h.mem[(ins.cls, reg)][rw + "s"] += 1
                continue
            mt = TSTART2.search(rest) or (TSTART.search(rest) if "Start" in rest else None)
            if mt:
                key, d = tensor_shape(mt.group(1), mt.group(2))
                t = h.tensor[key]
                add_tensor(t, d, shire)
                if d.get("_msk") and key.startswith("load"):
                    rk = "bytes_" + region_of(d["addr"], shire)
                    mu = TUUID.search(rest)
                    if key != "load_l2scp" and mu:
                        pending_mask[(tid, mu.group(1))] = (t, rk, d["_rows"])
                    elif key == "load_l2scp" and tid in last_tmask:
                        excess = d["bytes"] - masked_bytes(last_tmask[tid], d["_rows"])
                        t["bytes"] -= excess
                        t[rk] -= excess
                        t["masked_ops"] += 1
                    else:
                        t["masked_ops_rows_assumed_all"] += 1
                h.tensor_by_pc.setdefault(pc, collections.Counter())[key] += 1
                if key.startswith("fma_"):
                    h.tensor_by_pc.setdefault(("macs", pc), collections.Counter())[key] += d["macs"]
    for (tid, uuid), (t, rk, rows) in pending_mask.items():   # an Execute line never seen: all rows stay counted
        t["masked_ops_rows_assumed_all"] += 1
    return harts, pc_offset, outside


# ---------------------------------------------------------------------------------------------------------------
def read_prof(path):
    prof = collections.defaultdict(dict)
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        for line in f:
            p = line.split()
            if len(p) != 4:
                continue
            prof[int(p[0])][int(p[1], 16)] = (int(p[2]), int(p[3]))
    return prof


def auto_offset(insns, prof):
    """PC minus VMA. The runtime copies the kernel's ELF file to a page-aligned address, so the offset is a
    multiple of 4 KB and a PC keeps its VMA's low 12 bits: each profile PC votes for PC - a over the landing places
    a (branch targets, the instruction after a transfer, the entry) with the same low 12 bits."""
    land = set()
    for k, ins in enumerate(insns):
        if ins.target is not None:
            land.add(ins.target)
        if ins.transfers() and k + 1 < len(insns):
            land.add(insns[k + 1].addr)
    land.add(insns[0].addr)
    by_low = collections.defaultdict(list)
    for a in land:
        by_low[a & 0xFFF].append(a)
    votes = collections.Counter()
    pcs = set(pc for d in prof.values() for pc in d)          # each distinct PC once, whatever the harts
    for pc in pcs:
        for a in by_low.get(pc & 0xFFF, ()):
            votes[pc - a] += 1
    if not votes:
        raise SystemExit("profile: no PC matches a landing place of the kernel")
    # The most-voted offset can be wrong: the firmware's own landings (outside the kernel) vote too, and on a small
    # kernel they can outvote it (verify-counter, a scalar two-hart run: 0x-7fc5400000 won, explaining 50 of 588
    # PCs). So every candidate with at least two votes is scored by what it must explain: the PCs inside its range
    # that are landing places of the kernel, and the entry, which every working hart lands on. The kernel is loaded
    # above its VMA, so a candidate is >= 0. The best-explained candidate wins if it explains 90% of its range.
    def score(off):
        lo, hi = insns[0].addr + off, insns[-1].addr + insns[-1].size + off
        inside = [pc for pc in pcs if lo <= pc < hi]
        hits = sum(1 for pc in inside if (pc - off) in land)
        return hits, len(inside), (insns[0].addr + off) in pcs
    best = None
    for off, n in votes.most_common(400):
        if off < 0 or n < 2:
            continue
        hits, ninside, entry = score(off)
        if ninside and hits >= 0.9 * ninside:
            key = (entry, hits, -ninside)
            if best is None or key > best[0]:
                best = (key, off)
    if best is None:
        off = votes.most_common(1)[0][0]
        hits, ninside, _ = score(off)
        raise SystemExit(f"profile: no offset explains 90% of its range (the most voted, 0x{off:x}, explains {hits} "
                         f"of {ninside}); give --pc-offset, or --pc-offset-from a log counts file of the same kernel")
    return best[1]


def solve_profile(insns, prof, pc_offset, tensor_map=None, assume_no_wait=False):
    """Per hart: execution count per instruction from the landing histogram.

    Unknowns e[u, x]: the landings at u whose straight-line run ended at transfer x (x is a conditional branch
    taken, or the run's first unconditional transfer). Equations: (1) sum over x of e[u, x] = landings at u;
    (2) for a target v no return or trap return can reach: the sum of e[., x] over the transfers x aimed at v =
    landings at v (and when nothing landed at v, every e[., x] aimed at v is 0, returns or not); (3) for a run
    with no instruction able to hold the hart (tensor CSR writes, fcc, flb, stall, wfi) before its last end:
    sum over x of e[u, x] * (instructions from u through x) = the cycles recorded at u. Solved exactly: integer
    propagation, an exhaustive search for landings counted at most 4 times, and sparse Gaussian elimination over
    fractions. What stays unpinned is reported in `unresolved` and left out of the counts."""
    from fractions import Fraction
    import itertools
    addr_ix = {i.addr: k for k, i in enumerate(insns)}
    lo, hi = insns[0].addr, insns[-1].addr + insns[-1].size
    indirect_ok = set(k for k in range(len(insns)) if maybe_indirect(insns[k].addr, insns, addr_ix))
    out = {}
    for tid, d in prof.items():
        L, D = {}, {}
        for pc, (cnt, dur) in d.items():
            a = pc - pc_offset
            if lo <= a < hi:
                if a not in addr_ix:
                    raise SystemExit(f"profile: PC 0x{pc:x} of hart {tid} is not an instruction boundary")
                L[addr_ix[a]], D[addr_ix[a]] = cnt, dur
        if not L:
            continue
        runs = {}
        for u in L:
            k, ln, waited, ends = u, 0, False, []
            while k < len(insns):
                ins = insns[k]
                ln += 1
                waited = waited or ins.wait
                if ins.transfers():
                    ends.append((k, ln, waited))
                    if ins.unconditional():
                        break
                k += 1
            runs[u] = ends
        var_ix = {}
        for u, ends in runs.items():
            for (x, ln, w) in ends:
                var_ix[(u, x)] = len(var_ix)
        by_target = collections.defaultdict(list)
        for (u, x), vi in var_ix.items():
            t = insns[x].target
            if t is not None and t in addr_ix:
                by_target[addr_ix[t]].append(vi)
        eqs = []
        def no_wait(ends):
            return assume_no_wait or (ends and not any(w for (x, ln, w) in ends))
        for u, ends in runs.items():
            eqs.append(({var_ix[(u, x)]: 1 for (x, ln, w) in ends}, L[u]))
            if ends and no_wait(ends):
                eqs.append(({var_ix[(u, x)]: ln for (x, ln, w) in ends}, D[u]))
        for v, vis in by_target.items():
            if L.get(v, 0) == 0:
                for vi in vis:
                    eqs.append(({vi: 1}, 0))
            elif v not in indirect_ok:
                eqs.append(({vi: 1 for vi in vis}, L[v]))
        val = {}

        def propagate():
            progress, again = False, True
            while again:
                again = False
                for coef, rhs in eqs:
                    r, unk = rhs, []
                    for vi, co in coef.items():
                        if vi in val:
                            r -= co * val[vi]
                        else:
                            unk.append((vi, co))
                    if len(unk) == 1 and r % unk[0][1] == 0 and r // unk[0][1] >= 0:
                        val[unk[0][0]] = r // unk[0][1]
                        again = progress = True
                    elif unk and r == 0 and all(co > 0 for vi, co in unk):
                        for vi, co in unk:
                            val[vi] = 0
                        again = progress = True
            return progress

        def enumerate_small():
            progress = False
            for u, ends in runs.items():
                vis = [var_ix[(u, x)] for (x, ln, w) in ends]
                unk = [i for i, vi in enumerate(vis) if vi not in val]
                if not unk or not no_wait(ends):
                    continue
                left = L[u] - sum(val[vi] for vi in vis if vi in val)
                dleft = D[u] - sum(val[vi] * ends[i][1] for i, vi in enumerate(vis) if vi in val)
                lens = sorted(ends[i][1] for i in unk)
                if left > 0 and dleft == left * lens[0]:      # every remaining landing ended at the nearest end
                    for i in unk:
                        val[vis[i]] = left if ends[i][1] == lens[0] else 0
                    progress = True
                    continue
                if left > 0 and dleft == left * lens[-1]:     # or every one at the farthest
                    for i in unk:
                        val[vis[i]] = left if ends[i][1] == lens[-1] else 0
                    progress = True
                    continue
                if left > 4 or len(unk) > 12:
                    continue
                sols = []
                for combo in itertools.combinations_with_replacement(unk, left):
                    c = collections.Counter(combo)
                    if sum(ends[i][1] * m for i, m in c.items()) == dleft:
                        sols.append(c)
                        if len(sols) > 1:
                            break
                if len(sols) == 1:
                    for i in unk:
                        val[vis[i]] = sols[0].get(i, 0)
                    progress = True
            return progress

        while propagate() or enumerate_small():
            pass
        # sparse Gaussian elimination over fractions on what is left
        piv = {}
        for coef, rhs in eqs:
            row = {vi: Fraction(co) for vi, co in coef.items() if vi not in val}
            r = Fraction(rhs) - sum(co * val[vi] for vi, co in coef.items() if vi in val)
            for vi in [v for v in row if v in piv]:
                co = row.pop(vi)
                pr, prr = piv[vi]
                for v2, c2 in pr.items():
                    row[v2] = row.get(v2, 0) - co * c2
                r -= co * prr
            row = {v: c for v, c in row.items() if c != 0}
            if not row:
                continue
            pv = next(iter(row))
            cp = row.pop(pv)
            pr = {v: c / cp for v, c in row.items()}
            prr = r / cp
            for w in list(piv):
                wr, wrr = piv[w]
                if pv in wr:
                    cw = wr.pop(pv)
                    for v2, c2 in pr.items():
                        wr[v2] = wr.get(v2, 0) - cw * c2
                    piv[w] = ({v: c for v, c in wr.items() if c != 0}, wrr - cw * prr)
            piv[pv] = (pr, prr)
        for vi, (pr, prr) in piv.items():
            if not pr and prr.denominator == 1 and prr >= 0:
                val[vi] = int(prr)
        while propagate() or enumerate_small():
            pass
        exe, taken, unres = collections.Counter(), collections.Counter(), []
        for u, ends in runs.items():
            for (x, ln, w) in ends:
                vi = var_ix[(u, x)]
                if vi not in val:
                    unres.append({"landing": f"0x{insns[u].addr:x}", "end": f"0x{insns[x].addr:x}",
                                  "landings": L[u], "fn": insns[u].fn})
                    continue
                c = val[vi]
                if c:
                    for j in range(u, x + 1):
                        exe[insns[j].addr] += c
                    taken[insns[x].addr] += c
        out[tid] = (exe, taken, unres, sum(D.values()), len(L))
    return out


def maybe_indirect(v, insns, addr_ix):
    """Could an indirect transfer (a return, a trap return) land on v? True for the instruction after a call
    (jal/jalr that links ra) or after an ecall, and for the entry."""
    k = addr_ix.get(v)
    if k is None or k == 0:
        return True
    prev = insns[k - 1]
    if prev.kind == "trap":
        return True
    if prev.kind in ("jump_direct", "jump_indirect"):
        p = prev.ops.split(",")[0].strip()
        if prev.mn in ("jal", "jalr", "call") and p in ("ra", "x1", "t0", "x5"):
            return True
        if prev.mn == "jal" and len(prev.ops.split(",")) == 1:   # `jal target` links ra
            return True
    return False


# ---------------------------------------------------------------------------------------------------------------
def summarize(insns, exe, taken, pc_offset, tensor_by_pc=None, tensor_map=None, leaders=None):
    by_addr = {i.addr: i for i in insns}
    by_class = collections.Counter()
    by_mn = collections.Counter()
    by_csr = collections.Counter()      # CSR accesses by instruction and CSR name (by_mnemonic lumps them)
    compressed = 0
    tensor = collections.defaultdict(collections.Counter)
    tensor_src = collections.Counter()
    unknown = collections.Counter()
    traps = collections.Counter()
    addr_ix = {i.addr: k for k, i in enumerate(insns)}
    for a, n in exe.items():
        if n == 0:
            continue
        ins = by_addr[a]
        by_mn[ins.mn] += n
        if ins.mn in CSR_OPS:
            by_csr[f"{ins.mn} {ins.csr or '?'}"] += n
        if ins.size == 2:
            compressed += n
        if ins.cls == "branch":
            t = taken.get(a, 0)
            by_class["branch_taken"] += t
            by_class["branch_not_taken"] += n - t
        else:
            by_class[ins.cls] += n
        if ins.cls == "unknown":
            unknown[ins.mn] += n
        if ins.cls == "trap":
            traps[ins.mn] += n
        if ins.cls == "tensor" and ins.csrw:
            pc = a + pc_offset
            if tensor_by_pc is not None:
                continue      # the log's own tensor lines are counted elsewhere
            op = ins.csr
            if tensor_map and f"0x{a:x}" in tensor_map:     # this site's kinds, as a log of the same kernel saw them
                fm = tensor_map[f"0x{a:x}"]
                tensor_src["log map"] += n
                for key, frac in fm["keys"].items():
                    tensor[key]["ops"] += n * frac
                    if key.startswith("fma_"):
                        tensor[key]["macs"] += n * fm["macs_per_op"].get(key, 0) * frac
                continue
            if op == "tensor_fma":
                reg = ins.ops.split(",")[-1].strip()
                v = const_before(insns, addr_ix[a], reg, leaders or set())
                if v is not None:
                    fmt, macs = tfma_from_control(v)
                    tensor["fma_" + fmt]["ops"] += n
                    tensor["fma_" + fmt]["macs"] += n * macs
                    tensor_src["constant"] += n
                else:
                    tensor["fma_unknown_format"]["ops"] += n
                    tensor_src["unknown"] += n
            else:
                key = {"tensor_load": "load_any", "tensor_load_l2": "load_l2scp", "tensor_store": "store",
                       "tensor_wait": "wait", "tensor_quant": "quant", "tensor_reduce": "reduce",
                       "tensor_coop": "coop", "tensor_mask": "mask", "tex_send": "tex_send"}.get(op, op)
                tensor[key]["ops"] += n
    for c in CLASSES:
        by_class.setdefault(c, 0)
    total = sum(n for a, n in exe.items())
    return {"instructions": total, "compressed_instructions": compressed,
            "by_class": dict((c, by_class[c]) for c in CLASSES),
            "by_mnemonic": dict(sorted(by_mn.items(), key=lambda kv: -kv[1])),
            "by_csr": dict(sorted(by_csr.items(), key=lambda kv: (-kv[1], kv[0]))),
            "tensor": {k: dict(v) for k, v in sorted(tensor.items())},
            "tensor_format_source": dict(tensor_src),
            "traps": dict(traps), "unknown": dict(unknown)}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def add_into(tot, d):
    for k, v in d.items():
        if isinstance(v, dict):
            add_into(tot.setdefault(k, {}), v)
        elif isinstance(v, (int, float)):
            tot[k] = tot.get(k, 0) + v


def cmd_count(a):
    insns = parse_dis(a.dis)
    if not insns:
        raise SystemExit("no instructions in " + a.dis)
    leaders = set(i.target for i in insns if i.target is not None)
    kind_of = {i.addr: i.kind for i in insns}
    res = {"schema": SCHEMA, "tool": "tools/counter/count_kernel.py", "label": a.label,
           "inputs": {"dis": a.dis.split("/")[-1], "dis_sha256": sha256_file(a.dis)},
           "classes": CLASSES, "harts": {}}
    threads = None if not a.threads else set(int(x, 0) for x in a.threads.split(","))
    tmap = None
    if a.tensor_map:
        tmap = json.load(open(a.tensor_map)).get("tensor_map")
    if a.log:
        streamed = not (a.log.endswith(".gz") or __import__("os").path.isfile(a.log))
        res["inputs"].update(mode="log", log=a.log.split("/")[-1],
                             log_sha256="streamed (a pipe: not kept)" if streamed else sha256_file(a.log))
        off = int(a.pc_offset, 0) if a.pc_offset != "auto" else None
        harts, off, outside = count_log(a.log, insns, off, threads)
        res["kernel"] = {"text_vma": f"0x{insns[0].addr:x}", "pc_offset": f"0x{off:x}",
                         "pc_range": [f"0x{insns[0].addr + off:x}", f"0x{insns[-1].addr + insns[-1].size + off:x}"]}
        tmap_out = {}
        for tid in sorted(harts):
            h = harts[tid]
            exe = collections.Counter({pc - off: n for pc, n in h.pc_exec.items()})
            taken = collections.Counter({pc - off: n for pc, n in h.pc_taken.items()})
            s = summarize(insns, exe, taken, off, tensor_by_pc=h.tensor_by_pc, leaders=leaders)
            s["tensor"] = {k: dict(v) for k, v in sorted(h.tensor.items())}
            s["tensor_format_source"] = {"log": sum(v.get("ops", 0) for k, v in h.tensor.items() if k.startswith("fma_"))}
            mem = collections.defaultdict(dict)
            for (cls, reg), c in sorted(h.mem.items()):
                mem[cls][reg] = dict(c)
            s["memory"] = dict(mem)
            s["killed_and_restarted"] = h.killed
            s["cycles_span"] = (h.cycles_last - h.cycles_first + 1) if h.cycles_first is not None else 0
            s.update(hart_place(tid))
            s["per_pc"] = {f"0x{a:x}": [n, taken.get(a, 0)] for a, n in sorted(exe.items()) if n}
            s["branch_direction_changes"] = sum(h.pc_dirchg.values())
            s["branch_changes_per_pc"] = {f"0x{pc - off:x}": n for pc, n in sorted(h.pc_dirchg.items()) if n}
            res["harts"][str(tid)] = s
            for key, c in h.tensor_by_pc.items():
                if isinstance(key, tuple):
                    continue
                d = tmap_out.setdefault(f"0x{key - off:x}", {"keys": collections.Counter(), "macs_per_op": {}})
                d["keys"].update(c)
            for key, c in h.tensor_by_pc.items():
                if isinstance(key, tuple):
                    pc = key[1]
                    d = tmap_out[f"0x{pc - off:x}"]
                    for k2, macs in c.items():
                        d.setdefault("_macs", collections.Counter())[k2] += macs
        tm = {}
        for pc, d in tmap_out.items():
            tot = sum(d["keys"].values())
            tm[pc] = {"keys": {k: v / tot for k, v in d["keys"].items()},
                      "macs_per_op": {k: d.get("_macs", {}).get(k, 0) / d["keys"][k] for k in d["keys"]
                                      if k.startswith("fma_")}}
        res["tensor_map"] = tm
        # the firmware's work around each launch and anything else outside the kernel's U-mode text, apart
        ok = {}
        for tid in sorted(outside):
            o = outside[tid]
            mem = collections.defaultdict(dict)
            for (mode, reg), c in sorted(o.mem.items()):
                mem[mode][reg] = dict(c)
            ok[str(tid)] = {"instructions_by_mode": {k: v for k, v in sorted(o.by_mode.items()) if v},
                            "instructions": sum(o.by_mode.values()),
                            "tensor": {k: dict(v) for k, v in sorted(o.tensor.items())},
                            "memory": dict(mem), "killed_and_restarted": o.killed}
            ok[str(tid)].update(hart_place(tid))
        otot = {}
        for s in ok.values():
            add_into(otot, {k: v for k, v in s.items() if k in ("instructions_by_mode", "instructions", "tensor",
                                                                "memory", "killed_and_restarted")})
        otot["harts"] = len(ok)
        res["outside_kernel"] = {
            "what": "instructions, tensor ops and memory traffic that the logged harts retired OUTSIDE the kernel's "
                    "U-mode text: the firmware around each launch (M and S mode) and any U-mode instruction outside "
                    ".text. Never in `harts` or `total`. A card's hpmcounter4/5 count all privilege modes, so a card "
                    "count compared with `total` must subtract this (README, 'Bytes by level', step 6).",
            "harts": ok, "total": otot}
    elif a.prof:
        res["inputs"].update(mode="profile", prof=a.prof.split("/")[-1], prof_sha256=sha256_file(a.prof))
        prof = read_prof(a.prof)
        if a.pc_offset_from:
            off = int(json.load(open(a.pc_offset_from))["kernel"]["pc_offset"], 16)
            res["inputs"]["pc_offset_from"] = a.pc_offset_from.split("/")[-1]
        else:
            off = int(a.pc_offset, 0) if a.pc_offset != "auto" else auto_offset(insns, prof)
        res["kernel"] = {"text_vma": f"0x{insns[0].addr:x}", "pc_offset": f"0x{off:x}",
                         "pc_range": [f"0x{insns[0].addr + off:x}", f"0x{insns[-1].addr + insns[-1].size + off:x}"]}
        sol = solve_profile(insns, prof, off, tmap, assume_no_wait=a.assume_no_wait)
        res["inputs"]["assume_no_wait"] = a.assume_no_wait
        for tid in sorted(sol):
            if threads is not None and tid not in threads:
                continue
            exe, taken, unres, cyc, nland = sol[tid]
            s = summarize(insns, exe, taken, off, tensor_map=tmap, leaders=leaders)
            s["unresolved"] = unres
            s["cycles_emulated_in_region"] = cyc
            s.update(hart_place(tid))
            s["per_pc"] = {f"0x{a:x}": [n, taken.get(a, 0) if kind_of[a] == "cond" else 0]
                           for a, n in sorted(exe.items()) if n}
            res["harts"][str(tid)] = s
    else:
        raise SystemExit("give --log or --prof")
    tot = {}
    for tid, s in res["harts"].items():
        add_into(tot, {k: v for k, v in s.items() if k in ("instructions", "compressed_instructions", "by_class",
                                                           "by_mnemonic", "by_csr", "tensor", "memory", "traps",
                                                           "unknown", "branch_direction_changes")})
    res["total"] = tot
    res["total"]["harts"] = len(res["harts"])
    res["checks"] = {"unknown_mnemonics": sorted(set(m for s in res["harts"].values() for m in s.get("unknown", {}))),
                     "traps_executed": sorted(set(m for s in res["harts"].values() for m in s.get("traps", {}))),
                     "unresolved_runs": sum(len(s.get("unresolved", [])) for s in res["harts"].values())}
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1, sort_keys=False)
        f.write("\n")
    print(f"count_kernel: {len(res['harts'])} harts, {tot.get('instructions', 0)} instructions, "
          f"unresolved runs {res['checks']['unresolved_runs']}, unknown {res['checks']['unknown_mnemonics']} -> {a.out}")


def cmd_table(a):
    r = json.load(open(a.counts))
    harts = r["harts"]
    cols = list(harts.keys())[:8]
    print(f"{'class':18s} " + " ".join(f"{'h' + c:>10s}" for c in cols) + f" {'total':>12s}")
    for c in CLASSES:
        row = [harts[t]["by_class"].get(c, 0) for t in cols]
        tot = r["total"]["by_class"].get(c, 0)
        if tot or any(row):
            print(f"{c:18s} " + " ".join(f"{v:10d}" for v in row) + f" {tot:12d}")
    print(f"{'instructions':18s} " + " ".join(f"{harts[t]['instructions']:10d}" for t in cols) +
          f" {r['total']['instructions']:12d}")
    for k, v in sorted(r["total"].get("tensor", {}).items()):
        print(f"tensor {k:24s} {json.dumps(v)}")


def cmd_compare(a):
    A, B = json.load(open(a.a)), json.load(open(a.b))
    common = sorted(set(A["harts"]) & set(B["harts"]), key=int)
    worst = 0
    for t in common:
        ha, hb = A["harts"][t], B["harts"][t]
        pa, pb = ha.get("per_pc", {}), hb.get("per_pc", {})
        keys = set(pa) | set(pb)
        dex = sum(1 for k in keys if pa.get(k, [0, 0])[0] != pb.get(k, [0, 0])[0])
        dtk = sum(1 for k in keys if pa.get(k, [0, 0])[1] != pb.get(k, [0, 0])[1])
        dcl = {c: (ha["by_class"].get(c, 0), hb["by_class"].get(c, 0)) for c in CLASSES
               if ha["by_class"].get(c, 0) != hb["by_class"].get(c, 0)}
        worst = max(worst, dex + dtk + len(dcl))
        print(f"hart {t}: instructions {ha['instructions']} vs {hb['instructions']}; PCs differing in executions "
              f"{dex}, in taken {dtk}; classes differing {dcl if dcl else 'none'}")
    only = sorted(set(A["harts"]) ^ set(B["harts"]), key=int)
    if only:
        print("harts in one file only:", only[:20], "..." if len(only) > 20 else "")
    print("COMPARE:", "IDENTICAL" if worst == 0 else "DIFFERENT")
    return 0 if worst == 0 else 1


def cmd_classes(a):
    names = sorted(SCALAR_INT | INT_MULDIV | SCALAR_FLOAT | FLOAT_INT_XFER | TRANSCENDENTAL | MASK | LOADS | STORES |
                   set(LOAD_PAST) | set(STORE_PAST) | BRANCH_COND | JUMPS | SYSTEM | TRAPS)
    for n in names:
        print(f"{n:16s} {classify(n)}")
    for c in sorted(TENSOR_CSRS | CACHE_CSRS | SYNC_CSRS):
        print(f"csrw {c:11s} {classify('csrw', c + ',a0')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("count")
    c.add_argument("--dis", required=True)
    c.add_argument("--log")
    c.add_argument("--prof")
    c.add_argument("--out", required=True)
    c.add_argument("--label", default="")
    c.add_argument("--pc-offset", default="auto")
    c.add_argument("--pc-offset-from", default="", help="profile mode: take the offset from a log mode counts file "
                   "of the same kernel run the same way (its kernel.pc_offset)")
    c.add_argument("--threads", default="", help="comma list of hart ids to keep (default: every hart found)")
    c.add_argument("--assume-no-wait", action="store_true", help="profile mode: take every run's cycles as its "
                   "instruction count (true when the hart never waited; check it with a log of one or two harts)")
    c.add_argument("--tensor-map", default="", help="a log mode counts file: its tensor_map gives each "
                   "tensor_fma PC's format and shape for a profile of the same kernel")
    t = sub.add_parser("table")
    t.add_argument("counts")
    k = sub.add_parser("compare")
    k.add_argument("a")
    k.add_argument("b")
    sub.add_parser("classes")
    a = ap.parse_args()
    if a.cmd == "count":
        return cmd_count(a)
    if a.cmd == "table":
        return cmd_table(a)
    if a.cmd == "compare":
        return cmd_compare(a)
    if a.cmd == "classes":
        return cmd_classes(a)


if __name__ == "__main__":
    sys.exit(main())
