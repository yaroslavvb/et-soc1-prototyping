#!/usr/bin/env python3
"""Q130(i): the fp32 accumulator stream for sim/tb_gate_audit.sv, one word per micro-op.

WHY THIS FILE EXISTS. The testbench first computed the fused multiply-add itself, with
`$bitstoshortreal` / `$shortrealtobits` around a `shortreal` expression. Verilator does not
support `shortreal`: it promotes it to `real` (a 64-bit double) and warns
`Unsupported: shortreal being promoted to real`, which the build's `-Wno-lint` hid. The two
bit-cast functions then operate on a double's bit pattern, so `$bitstoshortreal(32'h3f800000)`
is a denormal of about 5.2e-315 rather than 1.0, every product underflows to zero, and the
multiply-add degenerated to `return c`. The register file was still being written and read, with
the operand tiles' own initial C values moving around it, so the write-side and address-side
counters were unaffected -- but the `mux_out_tr`, `rd_data_tr` and `wrdata_latch_tr` columns were
measured on an accumulator that never accumulated. Found 31 Oct 2026 by displaying one
multiply-add: `A=3f800000 B=3f800000 C=467a0000 fma=467a0000`, i.e. 1.0 * 1.0 + 16000.0 = 16000.0.

So the arithmetic is done here instead, in one place, with no floating point in the testbench at
all. The stream is the PRM 9.4 / `vpu_tensorfma.v` order -- for each B row k, for each A row i,
two micro-ops (C columns 0-7, then 8-15) -- for `warm + ops` consecutive matrix instructions on
the same tiles, which is what the testbench replays. One lane.

The multiply-add is FUSED, like `fmadd.ps`: the product and the sum are formed in double, which
is exact for binary32 inputs (a 48-bit product plus a 24-bit addend needs at most 53 bits except
in cases this stimulus does not contain), and rounded to binary32 exactly once, by
`struct.pack('<f', ...)`. No numpy, so any python3 runs it.

One stream serves BOTH wirings. A gated micro-op has a zero operand, so its result is the
accumulator it read, unchanged; not writing it leaves the same value in the file as writing it
would. `--check` asserts exactly that over the whole stream.

    python3 accum.py <tiles.hex> <out.hex> [--ops N] [--warm N] [--lane L] [--check]

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import struct


def f32(bits):
    return struct.unpack('<f', struct.pack('<I', bits & 0xffffffff))[0]


def bits32(x):
    return struct.unpack('<I', struct.pack('<f', x))[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tiles")
    ap.add_argument("out")
    ap.add_argument("--ops", type=int, default=1)
    ap.add_argument("--warm", type=int, default=1)
    ap.add_argument("--lane", type=int, default=0)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    words = [int(t, 16) for t in open(a.tiles).read().split()]
    if len(words) != 768:
        raise SystemExit("expected 768 words (A, B, C), got %d" % len(words))
    A = [[words[16 * i + j] for j in range(16)] for i in range(16)]
    B = [[words[256 + 16 * i + j] for j in range(16)] for i in range(16)]
    C = [[words[512 + 16 * i + j] for j in range(16)] for i in range(16)]

    res = []
    gated_same = 0
    gated = 0
    for _ in range(a.warm + a.ops):
        for k in range(16):
            for i in range(16):
                for h in range(2):
                    aw = A[i][k]
                    bw = B[k][8 * h + a.lane]
                    cw = C[i][8 * h + a.lane]
                    rw = bits32(f32(aw) * f32(bw) + f32(cw))
                    if aw == 0 or bw == 0:
                        gated += 1
                        if rw == cw:
                            gated_same += 1
                    res.append(rw)
                    C[i][8 * h + a.lane] = rw

    with open(a.out, "w") as fh:
        for n, w in enumerate(res):
            fh.write("%08x%s" % (w, "\n" if n % 8 == 7 else " "))
        if len(res) % 8:
            fh.write("\n")

    print("%s -> %s: %d micro-ops (%d warm + %d measured ops x 512), lane %d"
          % (a.tiles, a.out, len(res), a.warm, a.ops, a.lane))
    if a.check:
        if gated != gated_same:
            raise SystemExit("CHECK FAILED: %d of %d zero-operand micro-ops changed the "
                             "accumulator" % (gated - gated_same, gated))
        print("check: all %d zero-operand micro-ops leave the accumulator bit-identical, so one "
              "stream serves both wirings" % gated)


if __name__ == "__main__":
    main()
