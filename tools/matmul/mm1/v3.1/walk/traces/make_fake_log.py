#!/usr/bin/env python3
"""v31-trace (Q217) desk test material: a SYNTHETIC sys_emu log in the simulator's own line formats (sw-sysemu insns/tensors.cpp,
insn_util.h, emu_gio/testLog: '<cycle>: DEBUG EMU: [H<h> S<s>:N<n>:C<c>:T<t>] ...'), made from the walk, to test trace_run.py's summarizer
and check_v31.py before any simulator run. Not a measurement of anything. Standard library only.

    python3 -I -B make_fake_log.py --kernel rgm136.gemmL --shape 2x2x1 --mask 0xf --harts 0,18,...  --out fake.log [--perturb KIND]

What it writes per logged hart: firmware lines in M and S mode with an S-mode tensor operation (must be left out), U-mode instruction lines
(with an occasional 'Instruction killed and will be restarted'), each TensorLoad's Start line, its tensor_coop ':' line and Leader-neigh line
(cooperative loads), its Execute line and 16 MEM512 reads with SCP lines between, each TensorStore's Start and Execute lines with 64 MEM128
writes and FREG lines, each TensorFMA32's Start line; harts interleaved op by op as a lock step with jitter; hart 1 of each minion enters and
returns. Pools at bases that are not 256-B aligned for B (so the leader of B's groups is 1, by the simulator's rule) and PA = VA + 0x0.
--perturb: swapA (op 5's and 6's A addresses swapped on the first hart), bumpB (op 7's B address + 1 KiB on the first hart), dropS (the first
hart's first TensorStore left out), none.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "walk"))
import walk_v31 as W  # noqa: E402

BASE = {"A": 0x8000300000, "B": 0x8004300040, "C": 0x8008200000}
DATA16 = " ".join("%d:0x%08x" % (i, 0) for i in range(16))
DATA8 = " ".join("%d:0x%08x" % (i, 0) for i in range(8))
DATA4 = " ".join("%d:0x%08x" % (i, 0) for i in range(4))


def pref(cyc, h):
    s, rest = h // 64, h % 64
    n, c, t = rest // 16, (rest % 16) // 2, h % 2
    return "%d: DEBUG EMU: [H%d S%d:N%d:C%d:T%d] " % (cyc, h, s, n, c, t)


def ins(cyc, h, prv, pc, text):
    return pref(cyc, h) + "I(%s): 0x%x (0x00000013) %s\n" % (prv, pc, text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", required=True)
    ap.add_argument("--shape", required=True)
    ap.add_argument("--mask", required=True)
    ap.add_argument("--harts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--perturb", default="none", choices=["none", "swapA", "bumpB", "dropS"])
    a = ap.parse_args()
    MB, NB, KB = W.parse_shape(a.shape)
    harts = [int(x) for x in a.harts.split(",")]
    rng = random.Random(7)
    per = {}
    sh = set(W.mask_shires(a.mask))
    for h in harts:
        s, m, t = h // 64, (h % 64) // 2, h % 2
        if s in sh and t == 0:
            ev = list(W.minion_events(a.kernel, MB, NB, KB, s, m))
            if h == harts[0] and a.perturb != "none":
                ops = [i for i, e in enumerate(ev) if e[0] == "LA"]
                if a.perturb == "swapA":
                    i5, i6 = ops[5], ops[6]
                    e5, e6 = list(ev[i5]), list(ev[i6])
                    e5[1], e6[1] = e6[1], e5[1]
                    ev[i5], ev[i6] = tuple(e5), tuple(e6)
                elif a.perturb == "bumpB":
                    jb = [i for i, e in enumerate(ev) if e[0] == "LB"][7]
                    e = list(ev[jb])
                    e[1] += 1024
                    ev[jb] = tuple(e)
                elif a.perturb == "dropS":
                    js = [i for i, e in enumerate(ev) if e[0] == "S"][0]
                    ev = ev[:js] + ev[js + 1:]
            # group into ops: an op ends at its F
            ops, cur = [], []
            for e in ev:
                cur.append(e)
                if e[0] == "F":
                    ops.append(cur)
                    cur = []
            ops.append(cur)   # the last store
            per[h] = ops
        else:
            per[h] = None
    with open(a.out, "w") as f:
        f.write("INFO: sys_emu starting (synthetic)\n")
        for h in harts:   # firmware first, M and S mode, with an S-mode tensor op that must be left out
            f.write(ins(5, h, "M", 0x8000001000, "addi x0,x0,0"))
            f.write(ins(6, h, "S", 0x8000101000, "csrrw x0,tensor_load,x15"))
            f.write(pref(6, h) + "\t(TL-H%d-1) Start TensorLoad with msk: 0, coop: 0, cmd: 0, start: 0, tenb: 0, addr: 0x8000110000, boffset: 0, rows: 1, stride: 0x40, id: 0\n" % h)
            f.write(pref(7, h) + "(TL-H%d-1) Execute TensorLoad with msk: 0, coop: 0, start: 0, tenb: 0, addr: 0x8000110000, boffset: 0, rows: 1, stride: 0x40, id: 0, tmask: 0xffff\n" % h)
            f.write(pref(7, h) + "\tMEM512[0x8000110000] : { %s }\n" % DATA16)
            f.write(pref(7, h) + "\tSCP[0] = { %s }\n" % DATA16)
        uid = {h: 10 for h in harts}
        nops = max(len(v) for v in per.values() if v) if any(per.values()) else 0
        for i in range(nops):
            order = list(harts)
            rng.shuffle(order)
            for h in order:
                ops = per[h]
                cyc = 100 + 47 * i + rng.randint(0, 5)
                if ops is None:
                    if i == 0 and (h // 64) in sh:
                        f.write(ins(cyc, h, "U", 0x8005b35000, "addi x2,x2,-16"))
                        f.write(ins(cyc + 1, h, "U", 0x8005b35004, "jalr x0,x1,0"))
                    continue
                if i >= len(ops):
                    continue
                for e in ops[i]:
                    k = e[0]
                    f.write(ins(cyc, h, "U", 0x8005b35100, "ld x15,8(x2)"))
                    f.write(pref(cyc, h) + "\tMEM64[0x%x] : 0x%x\n" % (0x8000fff000 + 8 * (h % 64), 0x1234))   # a scalar stack load
                    f.write(pref(cyc, h) + "\tx15 = 0x1234\n")
                    f.write(ins(cyc, h, "U", 0x8005b35104, "sd x15,16(x2)"))
                    f.write(pref(cyc, h) + "\tMEM64[0x%x] = 0x%x\n" % (0x8000fff100 + 8 * (h % 64), 0x1234))   # a scalar stack store
                    if rng.random() < 0.02:
                        f.write(pref(cyc, h) + "\tInstruction killed and will be restarted\n")
                        f.write(ins(cyc + 1, h, "U", 0x8005b35100, "ld x15,8(x2)"))
                    uid[h] += 1
                    u = uid[h]
                    if k in ("LA", "LB"):
                        if k == "LA":
                            _, off, start, coop, tc, rows, stride, idd = e
                            tenb, addr = 0, BASE["A"] + off
                        else:
                            _, off, coop, tc, rows, stride, idd = e
                            tenb, start, addr = 1, 0, BASE["B"] + off
                        if coop:
                            f.write(pref(cyc, h) + "\ttensor_coop = 0x%x (neighs:0x%x minions:0x%02x group:%d)\n" % (tc, (tc >> 16) & 0xf, (tc >> 8) & 0xff, tc & 0x1f))
                        f.write(ins(cyc, h, "U", 0x8005b35120, "csrrw x0,tensor_load,x15"))
                        f.write(pref(cyc, h) + "\tx31 : 0x%x\n" % (stride | idd))
                        f.write(pref(cyc, h) + "\t(TL-H%d-%d) Start TensorLoad with msk: 0, coop: %d, cmd: 0, start: %d, tenb: %d, addr: 0x%x, boffset: 0, rows: %d, stride: 0x%x, id: %d\n"
                                % (h, u, coop, start, tenb, addr, rows, stride, idd))
                        if coop:
                            f.write(pref(cyc, h) + "\ttensor_coop : 0x%x (neighs:0x%x minions:0x%02x group:%d)\n" % (tc, (tc >> 16) & 0xf, (tc >> 8) & 0xff, tc & 0x1f))
                            neighs = (tc >> 16) & 0xF
                            sel = (addr >> 6) & 3
                            leader = [b for b in range(4) if (neighs >> b) & 1]
                            ld = sel if (neighs >> sel) & 1 else leader[0]
                            f.write(pref(cyc, h) + "\tLeader-neigh: %d, minion-mask=0x%08x, pending-mask=0x%08x\n" % (ld, 0xff, 0))
                        f.write(pref(cyc + 2, h) + "(TL-H%d-%d) Execute TensorLoad with msk: 0, coop: %d, start: %d, tenb: %d, addr: 0x%x, boffset: 0, rows: %d, stride: 0x%x, id: %d, tmask: 0xffff\n"
                                % (h, u, coop, start, tenb, addr, rows, stride, idd))
                        for r in range(rows):
                            f.write(pref(cyc + 2, h) + "\tMEM512[0x%x] : { %s }\n" % (addr + r * stride, DATA16))
                            f.write(pref(cyc + 2, h) + "\tSCP[%d] = { %s }\n" % (start + r, DATA16))
                    elif k == "S":
                        _, off, rows, cols, stride = e
                        addr = BASE["C"] + off
                        f.write(ins(cyc, h, "U", 0x8005b35140, "csrrw x0,tensor_store,x15"))
                        f.write(pref(cyc, h) + "\t(TS-H%d-%d) Start TensorStore with addr: %016x, stride: %016x, regstart: 0, rows: %d, cols: %d, srcinc: 1, coop: 1\n"
                                % (h, u, addr, stride, rows, cols))
                        f.write(pref(cyc + 3, h) + "(TS-H%d-%d) Execute TensorStore with addr: %016x, stride: %016x, regstart: 0, rows: %d, cols: %d, srcinc: 1, coop: 1\n"
                                % (h, u, addr, stride, rows, cols))
                        for r in range(rows):
                            for c in range(cols):
                                if not (c & 1):
                                    f.write(pref(cyc + 3, h) + "\tf%d : { %s }\n" % (r, DATA8))
                                f.write(pref(cyc + 3, h) + "\tMEM128[0x%x] = { %s }\n" % (addr + r * stride + c * 16, DATA4))
                    elif k == "F":
                        _, astart, mul, last = e
                        f.write(ins(cyc, h, "U", 0x8005b35160, "csrrw x0,tensor_fma,x15"))
                        f.write(pref(cyc, h) + "\t(TM-H%d-%d) Start TensorFMA32 with msk: 0, bcols: 16, arows: 16, acols: 16, aoffset: 0, tenb: 1, bstart: 0, astart: %d, mul: %d, rm: rne\n"
                                % (h, u, astart, mul))
                        f.write(pref(cyc + 4, h) + "\tf0 = { %s }\n" % DATA8)
        f.write("INFO: sys_emu done (synthetic)\n")
    print("wrote", a.out, os.path.getsize(a.out), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
