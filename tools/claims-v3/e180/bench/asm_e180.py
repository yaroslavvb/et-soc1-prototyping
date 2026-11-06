#!/usr/bin/env python3
"""E180's bench programs: the energy catalogue's inner loop (workloads/enercat), assembled for core-et's whole minion.

    python3 asm_e180.py --mode fadd.ps --word 0x40800000 --layout A --out prog.hex [--json prog.json]

The loop is the catalogue's RUN() as kernel/enercat.c writes it, with gen_ops.py's generated block for the mode:
    loop:  8 x <the 8-op block>          (gen_ops.py emit_vec: "op f(8+i), f(i), f((i+1)%8)", i = 0..7)
           addi s1, s1, 1                (++iters)
           .p2align 4                    (cycles(): ".p2align 4" then four "csrr %0, hpmcounter3")
           csrr t2, hpmcounter3  x 4
           bltu t2, s2, loop             (while (cycles() < deadline))
The kernel's own prologue (load_vsrc: "mov.m.x m0, zero, 0xff" and eight flw.ps of the 256 B image) is replaced by
register-only instructions with the same end state, so the bench needs no data memory: mstatus.FS set, m0 = 0xff by
mov.m.x from an integer register, f0..f7 = the word in every lane by fbcx.ps (the image of a one-number kind is that
word 64 times), and for the accumulating modes f8..f15 = 0 (the sum starts at zero, as a launch's does).

Modes (the first four are the catalogue's generated modes, unchanged; the two .acc modes are E180's new ones):
    fadd.ps      op f(8+i), f(i), f((i+1)%8)     catalogue mode 160
    fadd.pi      the same with fadd.pi           catalogue mode 172
    nop, add     catalogue modes (validation of the issue rate only)
    spin         the hand-written EC_SPIN block (8 x addi t0..t6), validation only
    fadd.ps.acc  op f(8+i), f(8+i), f(i)          E180: c += v on eight read-write chains
    fadd.pi.acc  the same with fadd.pi           E180

Layouts (where the loop sits against the 32 B fetch blocks; the compiled kernel's own layout is not in the repo):
    A  no compressed instructions, the loop's first op at a 32 B boundary (the registered primary)
    B  as A with ++iters as c.addi and the .p2align padding as the assembler pads with RVC (c.nop first)
    C  as A with the loop's first op 16 B past a 32 B boundary
    o<k>, o<k>r  the loop's first op k bytes past a 32 B boundary (k = 0, 4, ..., 28), without / with RVC as in B

Encodings: RV64I base; the ET vector ones from core-et b38a1a3 rtl/inc/instructions.vh (FADD_PS 0000000.....1111011,
FADD_PI 0000011..000.1111011, FBCX_PS ...011.....0001011, MOV_M_X 0101011........00...1111011).

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import struct

BASE = 0x1000
X = {"zero": 0, "t0": 5, "t1": 6, "t2": 7, "s1": 9, "a0": 10, "s2": 18, "s3": 19}
CSR_MSTATUS, CSR_HPMCOUNTER3 = 0x300, 0xC03
MODES = ("fadd.ps", "fadd.pi", "fadd.ps.acc", "fadd.pi.acc", "nop", "add", "spin")


def r_type(f7, rs2, rs1, f3, rd, op):
    return (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | op


def i_type(imm, rs1, f3, rd, op):
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | op


def lui(rd, imm20):
    return ((imm20 & 0xFFFFF) << 12) | (rd << 7) | 0b0110111


def addi(rd, rs1, imm):
    assert -2048 <= imm < 2048
    return i_type(imm, rs1, 0, rd, 0b0010011)


def add(rd, rs1, rs2):
    return r_type(0, rs2, rs1, 0, rd, 0b0110011)


def csrrs(rd, csr, rs1):
    return i_type(csr, rs1, 0b010, rd, 0b1110011)


def bltu(rs1, rs2, off):
    assert off % 2 == 0 and -4096 <= off < 4096
    o = off & 0x1FFF
    return (((o >> 12) & 1) << 31) | (((o >> 5) & 0x3F) << 25) | (rs2 << 20) | (rs1 << 15) | (0b110 << 12) | \
           (((o >> 1) & 0xF) << 8) | (((o >> 11) & 1) << 7) | 0b1100011


def jal(rd, off):
    o = off & 0x1FFFFF
    return (((o >> 20) & 1) << 31) | (((o >> 1) & 0x3FF) << 21) | (((o >> 11) & 1) << 20) | (((o >> 12) & 0xFF) << 12) | \
           (rd << 7) | 0b1101111


def nop():
    return addi(0, 0, 0)


def fadd_ps(fd, fs1, fs2, rm=0b111):
    return r_type(0b0000000, fs2, fs1, rm, fd, 0b1111011)


def fadd_pi(fd, fs1, fs2):
    return r_type(0b0000011, fs2, fs1, 0b000, fd, 0b1111011)


def fbcx_ps(fd, rs1):
    return (rs1 << 15) | (0b011 << 12) | (fd << 7) | 0b0001011


def mov_m_x(md, rs1):
    assert 0 <= md < 8
    return (0b0101011 << 25) | (rs1 << 15) | (md << 7) | 0b1111011


C_NOP = 0x0001


def c_addi(rd, imm):
    return (0b000 << 13) | (((imm >> 5) & 1) << 12) | (rd << 7) | ((imm & 0x1F) << 2) | 0b01


def li32(rd, w):
    """lui + addi for a 32-bit word (the low 32 bits are what fbcx.ps broadcasts)."""
    w &= 0xFFFFFFFF
    lo = w & 0xFFF
    lo = lo - 0x1000 if lo >= 0x800 else lo
    hi = ((w - lo) >> 12) & 0xFFFFF
    return [lui(rd, hi), addi(rd, rd, lo)]


def block(mode):
    """The 8-op block, as gen_ops.py emits it for the generated modes (and enercat.c's EC_SPIN for spin)."""
    if mode == "fadd.ps":
        return [fadd_ps(8 + i, i, (i + 1) % 8) for i in range(8)]
    if mode == "fadd.pi":
        return [fadd_pi(8 + i, i, (i + 1) % 8) for i in range(8)]
    if mode == "fadd.ps.acc":
        return [fadd_ps(8 + i, 8 + i, i) for i in range(8)]
    if mode == "fadd.pi.acc":
        return [fadd_pi(8 + i, 8 + i, i) for i in range(8)]
    if mode == "nop":
        return [nop() for _ in range(8)]
    if mode == "add":   # sinks a0..a7 (x10-x17), sources s3..s10 (x19-x26), rotating as emit_int_block
        return [add(10 + i, 19 + i, 19 + (i + 1) % 8) for i in range(8)]
    if mode == "spin":  # EC_SPIN: addi t0..t6 (x5-x7, x28-x31), then t0 again
        regs = [5, 6, 7, 28, 29, 30, 31, 5]
        return [addi(r, r, 1) for r in regs]
    raise SystemExit(f"unknown mode {mode}")


class Image:
    def __init__(self):
        self.b = bytearray()

    def w32(self, x):
        self.b += struct.pack("<I", x & 0xFFFFFFFF)

    def w16(self, x):
        self.b += struct.pack("<H", x & 0xFFFF)

    def pad_to(self, align, rvc):
        while len(self.b) % align:
            if rvc and len(self.b) % 4 == 2:
                self.w16(C_NOP)
            else:
                self.w32(nop())

    def here(self):
        return BASE + len(self.b)


LAYOUTS = {"A": (0, False), "B": (0, True), "C": (16, False)}


def parse_layout(layout):
    """A, B, C, or o<k>[r]: the loop's first op k bytes past a 32 B boundary (k = 0, 4, ..., 28), r = RVC as layout B."""
    if layout in LAYOUTS:
        return LAYOUTS[layout]
    if layout.startswith("o"):
        rvc = layout.endswith("r")
        k = int(layout[1:-1] if rvc else layout[1:])
        if k % 4 or not 0 <= k < 32:
            raise SystemExit(f"layout {layout}: k must be 0, 4, ..., 28")
        return k, rvc
    raise SystemExit(f"unknown layout {layout}")


CSR_MHARTID = 0xF14


def andi(rd, rs1, imm):
    return i_type(imm, rs1, 0b111, rd, 0b0010011)


def bne(rs1, rs2, off):
    return (bltu(rs1, rs2, off) & ~(0b111 << 12)) | (0b001 << 12)


def load_image(im, words, mode):
    """f0..f7 = the 256 B image (word 8r + l is lane l of f_r, as flw.ps loads it). A one-number image is broadcast by
    fbcx.ps; any other is written lane by lane, fbcx.ps under a one-lane m0, and m0 = 0xff at the end. Then t0 = 0: no
    integer register holds an operand in the loop (the kernel's flw.ps loads leave none), so the integer pipe's reads
    are the same for every image."""
    if len(set(words)) == 1:
        for x in li32(X["t0"], words[0]):
            im.w32(x)
        for r in range(8):
            im.w32(fbcx_ps(r, X["t0"]))
        if mode == "add":   # the scalar sources from the word, as the host fills every source register
            for i in range(8):
                im.w32(addi(19 + i, X["t0"], i))
    else:
        for lane in range(8):
            im.w32(addi(X["t0"], 0, 1 << lane))
            im.w32(mov_m_x(0, X["t0"]))
            for r in range(8):
                for x in li32(X["t0"], words[8 * r + lane]):
                    im.w32(x)
                im.w32(fbcx_ps(r, X["t0"]))
        im.w32(addi(X["t0"], 0, 0xFF))
        im.w32(mov_m_x(0, X["t0"]))
    im.w32(addi(X["t0"], 0, 0))


def build(mode, words0, layout, words1=None, c0=0):
    """words0 / words1: hart 0's and hart 1's 64-word images (the host gives every hart its own 256 B; a one-number
    kind and every file: image give both harts the same)."""
    if isinstance(words0, int):
        words0 = [words0 & 0xFFFFFFFF] * 64
    words1 = words0 if words1 is None else words1
    off, rvc = parse_layout(layout)
    im = Image()
    # prologue: FS on, m0 = 0xff, f0..f7 = the hart's image, (acc) f8..f15 = 0, deadline, iters
    for x in li32(X["t1"], 0x6000):
        im.w32(x)
    im.w32(csrrs(0, CSR_MSTATUS, X["t1"]))
    im.w32(addi(X["t0"], 0, 0xFF))
    im.w32(mov_m_x(0, X["t0"]))
    if words1 == words0:
        load_image(im, words0, mode)
    else:
        im.w32(csrrs(X["t1"], CSR_MHARTID, 0))
        im.w32(andi(X["t1"], X["t1"], 1))
        at_bne = len(im.b)
        im.w32(0)                              # bne t1, zero, <hart 1's image> (patched below)
        load_image(im, words0, mode)
        at_j = len(im.b)
        im.w32(0)                              # j <join> (patched below)
        h1 = len(im.b)
        load_image(im, words1, mode)
        join = len(im.b)
        im.b[at_bne:at_bne + 4] = struct.pack("<I", bne(X["t1"], 0, h1 - at_bne))
        im.b[at_j:at_j + 4] = struct.pack("<I", jal(0, join - at_j))
        for x in li32(X["t1"], 0x6000):        # t1 as the one-image path leaves it
            im.w32(x)
    if mode.endswith(".acc"):              # the sum starts at c0 (0 at a launch's start; a launch point for the bench)
        if c0:
            for x in li32(X["t0"], c0):
                im.w32(x)
        for i in range(8):
            im.w32(fbcx_ps(8 + i, X["t0"] if c0 else 0))
        if c0:
            im.w32(addi(X["t0"], 0, 0))
    im.w32(lui(X["s2"], 0x7FFFF))          # deadline: far beyond any bench window
    im.w32(addi(X["s1"], 0, 0))            # iters
    im.pad_to(32, False)
    for _ in range(off // 4):
        im.w32(nop())
    loop = im.here()
    for _ in range(8):
        for x in block(mode):
            im.w32(x)
    if rvc:
        im.w16(c_addi(X["s1"], 1))
    else:
        im.w32(addi(X["s1"], X["s1"], 1))
    im.pad_to(16, rvc)
    csr_at = im.here()
    for _ in range(4):
        im.w32(csrrs(X["t2"], CSR_HPMCOUNTER3, 0))
    br_at = im.here()
    im.w32(bltu(X["t2"], X["s2"], loop - br_at))
    j_at = im.here()
    im.w32(jal(0, loop - j_at))
    im.pad_to(32, False)
    for _ in range(16):                    # a tail of nops, so a fetch past the end reads defined bits
        im.w32(nop())
    pad = (csr_at - (loop + 256 + (2 if rvc else 4)))
    return im, {"mode": mode, "word": f"0x{words0[0]:08x}", "one_number": len(set(words0)) == 1 and words1 == words0,
                "layout": layout, "base": BASE, "loop": loop, "loop_mod32": loop % 32, "csr_at": csr_at, "branch_at": br_at,
                "loop_bytes": br_at + 4 - loop, "ops_per_iter": 64,
                "insts_per_iter": 64 + 1 + 4 + 1 + (pad // 4 + (1 if pad % 4 else 0)), "bytes": len(im.b)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=MODES)
    ap.add_argument("--word", default="0x40800000", help="the one number's 32-bit word (fbcx.ps broadcasts it)")
    ap.add_argument("--img0", help="hart 0's 256 B image (instead of --word); --img1 hart 1's (default: img0's)")
    ap.add_argument("--img1")
    ap.add_argument("--c0", default="0", help="accumulating modes: the sum's 32-bit word at the window's start (default 0)")
    ap.add_argument("--layout", default="A", help="A, B, C, or o<k>[r] (see the header)")
    ap.add_argument("--out", required=True, help="hex file: one 32-bit little-endian word per line, from BASE")
    ap.add_argument("--json")
    a = ap.parse_args()
    def words(path):
        b = open(path, "rb").read()
        if len(b) != 256:
            raise SystemExit(f"{path}: an image is exactly 256 bytes (the host's --operands file: rule)")
        return list(struct.unpack("<64I", b))
    if a.img0:
        im, info = build(a.mode, words(a.img0), a.layout, words(a.img1) if a.img1 else None, c0=int(a.c0, 0))
    else:
        im, info = build(a.mode, int(a.word, 0), a.layout, c0=int(a.c0, 0))
    info["c0"] = a.c0
    if len(im.b) % 4:
        im.b += b"\0\0"
    with open(a.out, "w") as f:
        for i in range(0, len(im.b), 4):
            f.write(f"{struct.unpack('<I', im.b[i:i + 4])[0]:08x}\n")
    if a.json:
        json.dump(info, open(a.json, "w"), indent=1)
    print(json.dumps(info))


if __name__ == "__main__":
    main()
