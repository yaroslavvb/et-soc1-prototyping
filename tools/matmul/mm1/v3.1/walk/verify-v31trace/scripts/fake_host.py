#!/usr/bin/python3 -I
"""verify-v31trace (Q217) desk stand-in for the host, used ONLY to desk-test vt_run.py's plumbing on aifoundry2 (inside slot.sh and
nodev.sh): it opens no device and runs no simulator; it writes a few lines in sys_emu's printf formats (emu_gio.cpp lprintf prefix,
insn_util.h I(%c), tensors.cpp Start/Execute lines, LOG_TENSOR_COOP, LOG_MEMREAD512) to ./sysemu.log, one SPARSITY line to stdout, a few
stderr lines, and exits 0."""
import json
import sys

L = []


def p(step, h, msg):
    s, n, c, t = h >> 6, (h >> 4) & 3, (h >> 1) & 7, h & 1
    L.append("%d: DEBUG EMU: [H%d S%d:N%d:C%d:T%d] %s" % (step, h, s, n, c, t, msg))


step = 100
A0, B0, C0 = 0x8005D3A000, 0x8007D3A000, 0x8005B3A000
for h in (0, 1, 64, 1984):
    p(step, h, "I(M): 0x8000000000 (0x00000013) addi x0,x0,0")
    step += 1
for op in range(2):
    h = 0
    p(step, h, "I(U): 0x8000001000 (0x80451073) csrrw x0,tensor_coop,x10"); step += 1
    p(step, h, "\ttensor_coop : 0xf0101 (neighs:0xf minions:0x01 group:1)"); step += 1
    p(step, h, "\ttensor_coop = 0x1ff00 (neighs:0x1 minions:0xff group:0)"); step += 1
    p(step, h, "I(U): 0x8000001004 (0x83ff9073) csrrw x0,0x83f,x31"); step += 1
    p(step, h, "\t(TL-H0-%d) Start TensorLoad with msk: 0, coop: 1, cmd: 0, start: %d, tenb: 0, addr: 0x%x, boffset: 0, rows: 16, "
      "stride: 0x40, id: 0" % (3 * op + 1, 16 * (op & 1), A0 + op * 1024)); step += 1
    p(step, h, "\ttensor_coop : 0x1ff00 (neighs:0x1 minions:0xff group:0)"); step += 1
    p(step, h, "I(U): 0x8000001008 (0x80451073) csrrw x0,tensor_coop,x11"); step += 1
    p(step, h, "\ttensor_coop : 0x1ff00 (neighs:0x1 minions:0xff group:0)"); step += 1
    p(step, h, "I(U): 0x800000100c (0x83ff9073) csrrw x0,0x83f,x31"); step += 1
    p(step, h, "\t(TL-H0-%d) Start TensorLoad with msk: 0, coop: 1, cmd: 0, start: 0, tenb: 1, addr: 0x%x, boffset: 0, rows: 16, "
      "stride: 0x40, id: 1" % (3 * op + 2, B0 + op * 1024)); step += 1
    p(step, h, "\ttensor_coop : 0xf0101 (neighs:0xf minions:0x01 group:1)"); step += 1
    for which, base, uid in (("A", A0 + op * 1024, 3 * op + 1), ("B", B0 + op * 1024, 3 * op + 2)):
        p(step, h, "(TL-H0-%d) Execute TensorLoad with msk: 0, coop: 1, cmd: 0, start: 0, tenb: %d, addr: 0x%x, boffset: 0, rows: 16, "
          "stride: 0x40, id: %d" % (uid, 1 if which == "B" else 0, base, 1 if which == "B" else 0)); step += 1
        for i in range(16):
            p(step, h, "\tMEM512[0x%x] : { 0:0x00000000 }" % (base + 64 * i)); step += 1
    p(step, h, "I(U): 0x8000001010 (0x00000013) tensorfma"); step += 1
    p(step, h, "\t(TM-H0-%d) Start TensorFMA32 with msk: 0, bcols: 16, arows: 16, acols: 16, aoffset: 0, tenb: 1, bstart: 0, astart: %d, "
      "mul: %d, rm: rne" % (3 * op + 3, 16 * (op & 1), 1 if op == 0 else 0)); step += 1
p(step, 0, "I(U): 0x8000001020 (0x87ff9073) csrrw x0,0x87f,x31"); step += 1
p(step, 0, "\t(TS-H0-7) Start TensorStore with addr: %016x, stride: 0000000000000040, regstart: 0, rows: 16, cols: 4, srcinc: 1, coop: 1"
  % C0); step += 1
p(step, 0, "(TS-H0-7) Execute TensorStore with addr: %016x, stride: 0000000000000040, regstart: 0, rows: 16, cols: 4, srcinc: 1, coop: 1"
  % C0); step += 1
for i in range(64):
    p(step, 0, "\tMEM128[0x%x] = 0x0" % (C0 + 64 * (i // 4) + 16 * (i % 4))); step += 1
for _ in range(3):
    p(step, 1, "I(U): 0x8000000100 (0x00000013) addi x0,x0,0"); step += 1
p(step, 2, "Instruction killed and will be restarted"); step += 1
with open("sysemu.log", "w") as f:
    f.write("\n".join(L) + "\n")
sys.stderr.write("INFO Device memory read at 0x0\nINFO Processing request 1\nsome other stderr line\n")
print("SPARSITY " + json.dumps({"test": "fma", "arm": "gemmL1x1x16", "minions": 128, "iters": 1024, "ok": True, "cycles_per_op": 1.0}))
print("SPARSITY " + json.dumps({"test": "check", "result": "exact", "ok": True}))
