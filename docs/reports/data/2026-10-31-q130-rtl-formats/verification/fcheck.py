#!/usr/bin/env python3
"""Functional check of the bench: does each micro-op's result equal the multiply-add of the operands it was given?

    fcheck.py --bin <obj_dir/Vtb> --tiles <tile.bin | ones5> --fmt fp32|fp16|int8 --workdir <dir>
              [--warm 1] [--mul 1] [--ops 1] [--gap N] [--old] [--label name] [--out results.json]

Added Sat 31 Oct 2026 by the revision-2 correction of Q130(b) (README section 0), to reproduce the verification's
finding that the bench's arithmetic is wrong. It is a diagnostic, not a toggle measurement: it runs the bench
with +check, reads every "CHK a b c r" line (the operands the bench recorded for a result, and the result it
wrote back) and classifies r against references computed from the SAME a, b and c:

  fp32  fma(a, b, c) (a*b is exact in a double; the sum is rounded once more to fp32), and a*b alone
  fp16  c + a_lo*b_lo + a_hi*b_hi, accepted within one fp32 ulp (the two products are exact in fp32 and the
        unit truncates, RTZ), and a_lo*b_lo + a_hi*b_hi alone
  int8  c + the sum of the four signed byte products, mod 2^32, and the products alone

plus whether r == c exactly (the product dropped). The three flags are reported together, not as exclusive
classes ("madd=0,ab=0,c=1" is a result equal to its addend alone). `--tiles ones5` is the synthetic accumulator probe: A = B = 1
in every element and C0 = 5, so a run with every op a MADD (--mul 0) must leave C = 5 + n*16 in fp32,
5 + n*32 in fp16 and 5 + n*64 in int8 after n ops (16 k-steps an op of 1, 2 or 4 unit products).
`--old` runs rtl-sim/fma_toggle's fp32-only bench, which takes no +fmt.
"""
import argparse
import collections
import json
import os
import struct
import subprocess
import tempfile


def u2f(w):
    return struct.unpack("<f", struct.pack("<I", w))[0]


def f2u(x):
    return struct.unpack("<I", struct.pack("<f", x))[0]


def h2f(h):
    return struct.unpack("<e", struct.pack("<H", h))[0]


def sbyte(w, e):
    b = (w >> (8 * e)) & 0xFF
    return b - 256 if b > 127 else b


def ulp32(x):
    w = f2u(abs(x)) & 0x7FFFFFFF
    return abs(u2f(w + 1) - u2f(w)) if w < 0x7F7FFFFF else float("inf")


def classify(fmt, a, b, c, r):
    """Non-exclusive flags: madd (r is the multiply-add), ab (r is the product term alone), c (r is c exactly)."""
    if fmt == "fp32":
        madd = r == f2u(u2f(a) * u2f(b) + u2f(c))
        ab = r == f2u(u2f(a) * u2f(b))
    elif fmt == "fp16":
        p = h2f(a & 0xFFFF) * h2f(b & 0xFFFF) + h2f(a >> 16) * h2f(b >> 16)
        rv = u2f(r)
        madd = abs(rv - (p + u2f(c))) <= ulp32(p + u2f(c))
        ab = abs(rv - p) <= ulp32(p)
    else:
        p = sum(sbyte(a, e) * sbyte(b, e) for e in range(4))
        cs = c - (1 << 32) if c >> 31 else c
        madd = r == (p + cs) & 0xFFFFFFFF
        ab = r == p & 0xFFFFFFFF
    return f"madd={int(madd)},ab={int(ab)},c={int(r == c)}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--tiles", required=True, help="a 2,048-byte Q130(s) tile file, or ones5")
    ap.add_argument("--fmt", required=True, choices=["fp32", "fp16", "int8"])
    ap.add_argument("--workdir", required=True, help="where the hex file and coverage go (deleted after)")
    ap.add_argument("--warm", type=int, default=1)
    ap.add_argument("--mul", type=int, default=1)
    ap.add_argument("--ops", type=int, default=1)
    ap.add_argument("--gap", type=int, default=None)
    ap.add_argument("--old", action="store_true")
    ap.add_argument("--label", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    gap = a.gap if a.gap is not None else (318 - 256 if a.fmt == "int8" else 546 - 512)
    if a.tiles == "ones5":
        one = {"fp32": 0x3F800000, "fp16": 0x3C003C00, "int8": 0x01010101}[a.fmt]
        words, cinit = [one] * 512, [0x40A00000 if a.fmt != "int8" else 5] * 256
        per_op = {"fp32": 16, "fp16": 32, "int8": 64}[a.fmt]
        expect_c = 5 + (a.warm + a.ops) * per_op if a.mul == 0 else None
    else:
        words, cinit, expect_c = list(struct.unpack("<512I", open(a.tiles, "rb").read())), [0] * 256, None
    with tempfile.TemporaryDirectory(dir=a.workdir) as d:
        hexf = os.path.join(d, "t.hex")
        with open(hexf, "w") as f:
            for w in words + cinit:
                f.write(f"{w:08x}\n")
        cmd = [a.bin, f"+tiles={hexf}", f"+ops={a.ops}", f"+warm={a.warm}", f"+mul={a.mul}", f"+gap={gap}",
               f"+check={(a.warm + a.ops) * 4096}", f"+verilator+coverage+file+{os.path.join(d, 'cov.dat')}"]
        if not a.old:
            cmd.append(f"+fmt={a.fmt}")
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    tally = collections.Counter()
    for idx, line in enumerate(l for l in out.splitlines() if l.startswith("CHK")):
        _, x, y, z, r = line.split()
        x, y, z, r = (int(v, 16) for v in (x, y, z, r))
        op = idx // 4096
        kind = "c==0" if z == 0 else "c!=0"
        tally[f"op{op}|{kind}|{classify(a.fmt, x, y, z, r)}"] += 1
    finals = collections.Counter(l.split()[3] for l in out.splitlines() if l.startswith("C "))
    dec = (lambda w: u2f(int(w, 16))) if a.fmt != "int8" else (lambda w: int(w, 16))
    res = {
        "label": a.label or f"{'old' if a.old else 'new'}-{a.fmt}-{os.path.basename(a.tiles)}",
        "bench": "rtl-sim/fma_toggle (old)" if a.old else "rtl-sim/fma_toggle_formats (new)",
        "fmt": a.fmt, "tiles": os.path.basename(a.tiles), "warm": a.warm, "mul": a.mul, "ops": a.ops, "gap": gap,
        "results_checked": sum(tally.values()),
        "tally": dict(sorted(tally.items())),
        "final_C_distinct_top5": [[v, dec(v), n] for v, n in finals.most_common(5)],
        "final_C_expected_if_accumulating": expect_c,
    }
    print(json.dumps(res, indent=1))
    if a.out:
        allres = json.load(open(a.out)) if os.path.exists(a.out) else {"runs": []}
        allres["runs"] = [x for x in allres["runs"] if x["label"] != res["label"]] + [res]
        json.dump(allres, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
