#!/usr/bin/env python3
"""Desk test of count_kernel.py's log reader on lines in the exact formats sw-sysemu 353f20e prints.

    python3 -I -B tools/counter/test_count_kernel.py          # prints one line per check, exits 0 when all pass

Each tensor line is made from its C format string, transcribed with its conversions (insns/tensors.cpp at et-platform
353f20e: TensorLoad line 358, TensorLoadL2SCP 734, TensorStoreFromScp 1038, TensorStore 1100, TensorFMA32,
TensorFMA16A32 and TensorIMA8A32 1639-1652; the Execute TensorLoad line with its tmask as the simulator's own log
shows it; LOG_TENSOR_MASK in insn_util.h). TensorStore and TensorStoreFromScp print addr and stride as %016 PRIx64,
hex without 0x: the reader before this test (Thu 12 Nov 2026, verify-counter's major fault) raised ValueError on
`0000008000c08880` and read `00000000bf840000` as 0. A small hand-written disassembly and log then check the counts:
tensor stores by bytes and region, a masked load's rows, the firmware's work outside the kernel by privilege mode, a
kill, a conditional branch's direction changes and the CSR names. Desk only. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import count_kernel as ck  # noqa: E402

# The C format strings, transcribed (PRIx64 -> x, %016 PRIx64 -> %016x, PRIu64 and %u -> d).
F_TLOAD = ("\t(TL-H%d-%d) Start TensorLoad with msk: %d, coop: %d, cmd: %d, "
           "start: %d, tenb: %d, addr: 0x%x, boffset: %d, rows: %d, "
           "stride: 0x%x, id: %d")
F_TLOAD_EXEC = ("(TL-H%d-%d) Execute TensorLoad with msk: %d, coop: %d, start: %d, tenb: %d, addr: 0x%x, "
                "boffset: %d, rows: %d, stride: 0x%x, id: %d, tmask: 0x%x")
F_TMASK = "\ttensor_mask : 0x%x"
F_L2SCP = ("\tStart/Execute TensorLoadL2SCP with msk:%d, start: %d, "
           "addr: 0x%x, rows: %d, stride: 0x%x, id: %d")
F_TSTORE_SCP = "\tStart/Execute TensorStoreFromScp with addr: %016x, stride: %016x, rows: %d, scpstart: %d, srcinc: %d"
F_TSTORE = ("\t(TS-H%d-%d) Start TensorStore with addr: %016x, "
            "stride: %016x, regstart: %d, rows: %d, cols: %d, "
            "srcinc: %d, coop: %d")
F_TSTORE_EXEC = ("(TS-H%d-%d) Execute TensorStore with addr: %016x, "
                 "stride: %016x, regstart: %d, rows: %d, cols: %d, srcinc: %d, "
                 "coop: %d")
F_FMA32 = ("\t(TM-H%d-%d) Start TensorFMA32 with msk: %d, bcols: %d, "
           "arows: %d, acols: %d, aoffset: %d, tenb: %d, bstart: %d, "
           "astart: %d, mul: %d, rm: %s")
F_FMA16 = ("\t(TM-H%d-%d) Start TensorFMA16A32 with msk: %d, bcols: %d, "
           "arows: %d, acols: %d, aoffset: %d, tenb: %d, bstart: %d, "
           "astart: %d, mul: %d, rm: rtz")
F_IMA8 = ("\t(TM-H%d-%d) Start TensorIMA8A32 with msk: %d, bcols: %d, "
          "arows: %d, acols: %d, aoffset: %d, dst: %d, ub: %d, ua: %d, "
          "tenb: %d, bstart: %d, astart: %d mul: %d")

SCP_OWN = 0x80000000 + (0x7F << 23) + 0x40000      # the PRM's format 0, the local shire: 0xbf840000
DRAM = 0x8000C08880

DIS = """
kernel.elf:     file format elf64-littleriscv


Disassembly of section .text:

0000000000001000 <_start>:
    1000:\t00100793          \tli\ta5,1
    1004:\t83179073          \tcsrw\ttensor_store,a5
    1008:\t83f79073          \tcsrw\ttensor_load,a5
    100c:\tfe071ce3          \tbnez\ta4,1004 <_start+0x4>
    1010:\tf1402573          \tcsrr\ta0,mhartid
    1014:\t0000100b          \tfgwl.ps\tft0,ft1(a0)
    1018:\t80179073          \tcsrw\ttensor_fma,a5
    101c:\t00008067          \tret
"""

OFF = 0x8005B35000


def line(cyc, hart, msg):
    s, rest = hart // 64, hart % 64
    n, c, t = rest // 16, (rest % 16) // 2, hart % 2
    return f"{cyc}: DEBUG EMU: [H{hart} S{s}:N{n}:C{c}:T{t}] {msg}\n"


def ins(cyc, hart, prv, pc, bits, text):
    return line(cyc, hart, f"I({prv}): 0x{pc:x} (0x{bits}) {text}")


def build_log():
    L = []
    u = lambda vma: vma + OFF  # noqa: E731
    # hart 0: firmware (M mode) with a tensor op and a write, then the kernel
    L.append(ins(10, 0, "M", 0x40001000, "00000013", "addi x0,x0,0"))
    L.append(line(10, 0, F_IMA8 % (0, 1, 0, 16, 16, 64, 0, 0, 0, 0, 1, 0, 0, 1)))
    L.append(line(10, 0, "\tMEM64[0x40100000] = 0x0"))
    L.append(ins(20, 0, "U", u(0x1000), "00100793", "addi x15,x0,1"))
    L.append(ins(21, 0, "U", u(0x1004), "83179073", "csrrw x0,tensor_store,x15"))
    L.append(line(21, 0, F_TSTORE % (0, 2, SCP_OWN, 0x40, 0, 16, 2, 1, 1)))
    L.append(line(30, 0, F_TSTORE_EXEC % (0, 2, SCP_OWN, 0x40, 0, 16, 2, 1, 1)))
    L.append(ins(31, 0, "U", u(0x1008), "83f79073", "csrrw x0,tensor_load,x15"))
    L.append(line(31, 0, F_TLOAD % (0, 3, 1, 0, 0, 0, 0, SCP_OWN, 0, 16, 0x40, 0)))
    L.append(line(31, 0, F_TMASK % 0x00FF))
    L.append(ins(32, 0, "U", u(0x100c), "fe071ce3", "c.bnez x14,-8"))          # taken: back to 0x1004
    L.append(line(33, 0, F_TLOAD_EXEC % (0, 3, 1, 0, 0, 0, SCP_OWN, 0, 16, 0x40, 0, 0x00FF)))
    L.append(ins(34, 0, "U", u(0x1004), "83179073", "csrrw x0,tensor_store,x15"))
    L.append(line(34, 0, F_TSTORE_SCP % (DRAM, 0x40, 4, 0, 1)))
    L.append(ins(35, 0, "U", u(0x1008), "83f79073", "csrrw x0,tensor_load,x15"))
    L.append(line(35, 0, F_L2SCP % (0, 0, DRAM, 2, 0x40, 0)))
    L.append(ins(36, 0, "U", u(0x100c), "fe071ce3", "c.bnez x14,-8"))          # not taken: falls to 0x1010
    L.append(ins(37, 0, "U", u(0x1010), "f1402573", "csrrs x10,mhartid,x0"))
    L.append(line(37, 0, "\tInstruction killed and will be restarted"))
    L.append(ins(38, 0, "U", u(0x1010), "f1402573", "csrrs x10,mhartid,x0"))
    L.append(ins(39, 0, "S", 0x40002000, "00000013", "addi x0,x0,0"))          # a trap into the firmware
    L.append(line(39, 0, "\tMEM32[0x00100000] : 0x5"))
    L.append(ins(40, 0, "S", 0x40002004, "00000013", "addi x0,x0,0"))
    L.append(line(40, 0, "\tInstruction killed and will be restarted"))
    L.append(ins(41, 0, "U", u(0x101c), "00008067", "jalr x0,x1,0"))
    # hart 2: three formats of TensorFMA from one CSR write each
    for k, (fmt, args) in enumerate(((F_FMA32, (2, 10, 0, 16, 16, 16, 0, 0, 0, 0, 1, "rne")),
                                     (F_FMA16, (2, 11, 0, 16, 16, 32, 0, 0, 0, 0, 1)),
                                     (F_IMA8, (2, 12, 0, 16, 16, 64, 0, 0, 0, 0, 1, 0, 0, 1)))):
        L.append(ins(50 + k, 2, "U", u(0x1018), "80179073", "csrrw x0,tensor_fma,x15"))
        L.append(line(50 + k, 2, fmt % args))
    return "".join(L)


def main():
    fails = []

    def check(name, got, want):
        ok = got == want
        print(f"{'PASS' if ok else 'FAIL'} {name}: got {got!r}" + ("" if ok else f", want {want!r}"))
        if not ok:
            fails.append(name)

    # 1. every format parses, and addr/stride are hex with or without 0x
    kv = ck.kv_fields((F_TSTORE % (0, 2, DRAM, 0x40, 0, 16, 2, 1, 1)).split("TensorStore", 1)[1])
    check("TensorStore addr (%016x, no 0x)", kv.get("addr"), DRAM)
    check("TensorStore stride", kv.get("stride"), 0x40)
    check("TensorStore rows, cols", (kv.get("rows"), kv.get("cols")), (16, 2))
    kv = ck.kv_fields((F_TSTORE_SCP % (SCP_OWN, 0x40, 4, 0, 1)).split("FromScp", 1)[1])
    check("TensorStoreFromScp addr (%016x)", kv.get("addr"), SCP_OWN)
    kv = ck.kv_fields((F_TLOAD % (0, 3, 1, 0, 0, 0, 1, DRAM, 0, 16, 0x40, 0)).split("TensorLoad", 1)[1])
    check("TensorLoad addr (0x%x), tenb, msk", (kv.get("addr"), kv.get("tenb"), kv.get("msk")), (DRAM, 1, 1))
    kv = ck.kv_fields((F_L2SCP % (0, 5, DRAM, 2, 0x40, 0)).split("L2SCP", 1)[1])
    check("TensorLoadL2SCP msk:%d (no space), rows", (kv.get("msk"), kv.get("rows"), kv.get("addr")), (0, 2, DRAM))
    kv = ck.kv_fields((F_FMA32 % (0, 1, 0, 16, 16, 16, 0, 0, 0, 0, 1, "dyn")).split("TensorFMA32", 1)[1])
    check("TensorFMA32 fields, `rm: dyn` not read", (kv.get("arows"), kv.get("acols"), kv.get("bcols"), "rm" in kv),
          (16, 16, 16, False))
    for name, fmt, args in (("TensorStore", F_TSTORE, (0, 2, DRAM, 0x40, 0, 16, 2, 1, 1)),
                            ("TensorStoreFromScp", F_TSTORE_SCP, (DRAM, 0x40, 4, 0, 1)),
                            ("TensorLoad", F_TLOAD, (0, 3, 0, 0, 0, 0, 1, DRAM, 0, 16, 0x40, 0)),
                            ("TensorLoadL2SCP", F_L2SCP, (0, 0, DRAM, 2, 0x40, 0)),
                            ("TensorFMA32", F_FMA32, (0, 1, 0, 16, 16, 16, 0, 0, 0, 0, 1, "rne")),
                            ("TensorFMA16A32", F_FMA16, (0, 1, 0, 16, 16, 32, 0, 0, 0, 0, 1)),
                            ("TensorIMA8A32", F_IMA8, (0, 1, 0, 16, 16, 64, 0, 0, 0, 0, 1, 0, 0, 1))):
        rest = fmt % args
        mt = ck.TSTART2.search(rest) or ck.TSTART.search(rest)
        try:
            key, d = ck.tensor_shape(mt.group(1), mt.group(2))
            check(f"{name} line parses", key in ("store", "load", "load_tenb", "load_l2scp", "fma_fp32", "fma_fp16",
                                                 "fma_int8"), True)
        except Exception as e:  # noqa: BLE001
            check(f"{name} line parses", f"{type(e).__name__}: {e}", "no exception")
    check("the Execute TensorStore line is not a second start", ck.TSTART.search(F_TSTORE_EXEC % (0, 2, DRAM, 0x40, 0,
                                                                                                  16, 2, 1, 1)), None)

    # 2. classes the verifier found missing
    for mn, want in (("fcvt.ps.pw", "vector_float"), ("fcvt.ps.pwu", "vector_float"), ("fcvt.ps.f16", "vector_float"),
                     ("fcvt.pw.ps", "vector_float"), ("fgwl.ps", "gather_scatter_past_l1"),
                     ("fgwg.ps", "gather_scatter_past_l1"), ("fscwl.ps", "gather_scatter_past_l1"),
                     ("fscwg.ps", "gather_scatter_past_l1"), ("fgw.ps", "gather_scatter"),
                     ("fg32w.ps", "gather_scatter"), ("fsc32w.ps", "gather_scatter"), ("flwl.ps", "load_past_l1")):
        check(f"class of {mn}", ck.classify(mn), want)

    # 3. a whole log through the reader
    with tempfile.TemporaryDirectory() as td:
        dis = os.path.join(td, "k.dis")
        log = os.path.join(td, "sysemu.log")
        open(dis, "w").write(DIS)
        open(log, "w").write(build_log())
        insns = ck.parse_dis(dis)
        harts, off, outside = ck.count_log(log, insns, OFF, None)
        leaders = set(i.target for i in insns if i.target is not None)
    h0 = harts[0]
    check("hart 0 executions at 0x1004, 0x1010 (one killed)", (h0.pc_exec[OFF + 0x1004], h0.pc_exec[OFF + 0x1010]), (2, 1))
    check("hart 0 kills", h0.killed, 1)
    check("hart 0 tensor store: ops, bytes", (h0.tensor["store"]["ops"], h0.tensor["store"]["bytes"]),
          (2, 16 * 2 * 16 + 4 * 64))
    check("tensor store bytes by region", (h0.tensor["store"]["bytes_scratchpad_own"], h0.tensor["store"]["bytes_dram"]),
          (512, 256))
    check("masked TensorLoad: only its 8 set rows", (h0.tensor["load"]["bytes"], h0.tensor["load"]["masked_ops"]),
          (8 * 64, 1))
    check("TensorLoadL2SCP bytes from DRAM", h0.tensor["load_l2scp"]["bytes_dram"], 128)
    check("branch at 0x100c: taken once, one direction change",
          (h0.pc_taken[OFF + 0x100c], h0.pc_dirchg[OFF + 0x100c]), (1, 1))
    o0 = outside[0]
    check("outside the kernel, by mode (one S instruction killed)", dict(o0.by_mode), {"M": 1, "S": 1})
    check("outside the kernel: the firmware's TensorIMA8A32", dict(o0.tensor["fma_int8"]), {"ops": 1, "macs": 16 * 64 * 16})
    check("outside the kernel: memory by mode and region",
          (o0.mem[("M", "sp")]["write_bytes"], o0.mem[("S", "io")]["read_bytes"]), (8, 4))
    h2 = harts[2]
    check("hart 2: one op of each format, MACs as printed",
          {k: dict(v) for k, v in sorted(h2.tensor.items())},
          {"fma_fp16": {"ops": 1, "macs": 16 * 32 * 16}, "fma_fp32": {"ops": 1, "macs": 16 * 16 * 16},
           "fma_int8": {"ops": 1, "macs": 16 * 64 * 16}})
    exe = {pc - off: n for pc, n in h0.pc_exec.items()}
    tk = {pc - off: n for pc, n in h0.pc_taken.items()}
    s = ck.summarize(insns, exe, tk, off, tensor_by_pc=h0.tensor_by_pc, leaders=leaders)
    check("by_csr names each CSR", s["by_csr"], {"csrw tensor_store": 2, "csrw tensor_load": 2, "csrr mhartid": 1})
    check("by_class: branches, jumps, system", (s["by_class"]["branch_taken"], s["by_class"]["branch_not_taken"],
                                                s["by_class"]["jump"], s["by_class"]["system"]), (1, 1, 1, 1))
    print("TEST-COUNT-KERNEL", "OK" if not fails else f"FAILED {len(fails)}: {fails}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
