#!/usr/bin/env python3
"""make_images.py: the loop forms, operand images and designed counts of the regfile workload.

Written from the public RV64I instruction set only. One loop form is one stream of 128 32-bit integer instructions
(no load, no store, no branch inside the body); one image is the values of the registers the form uses; one kind is
a (form, image) pair. Every kind of one form runs byte-identical code: only the register values differ.

Every timed loop is the same frame around its body: the body (128 instructions, head 64-byte aligned), then the
loop's own three instructions on fixed registers that no form names (addi x10, x10, 1 ; csrr x13, hpmcounter3 ;
bltu x13, x28, head), then 29 copies of one instruction on the loop's deadline register, which is dead once the loop
ends (addi x28, x28, 2), so that the 64-byte block holding the branch and the block after it are the same bytes in
every form: whatever is fetched past the branch is the same in every kind. They run once, when the loop ends. That
instruction's fields are chosen from the encoding alone so that, where a body meets the frame, the two kinds of a
train change about the same number of fetched bits, at every aligned block size from 8 to 64 bytes, with or without
the block after the branch (--frame prints the table for every train of trains.tsv; --check bounds rot against rot2
and resf against resz).

Forms (sources are never written, sinks are never read):
  rot    sixteen-instruction phrase: mv d_i, s_i (i = 0..7), then mv d_(i+3 mod 8), s_i (i = 0..7)
         -> each sink receives s_m and s_(m-3) in turn: its cells change by popcount(s_m ^ s_(m-3)) bits a write
  rot2   the same with the second half mv d_(i+2 mod 8), s_i: each sink receives s_m and s_(m-2) in turn
         -> rot and rot2 run the same source, port and result stream; on the two images below s_(m-2) = s_m, so rot2's
            sinks keep their values while rot's change. The eight sinks are chosen so that the destination field
            changes in the same bits, bit position by bit position, between instructions 1, 2, 4 and 8 apart, in rot
            and rot2 alike (--check verifies it): the two forms' code differs in the order of the destinations only,
            not in how often each encoding bit changes at those distances
  res    and d0, a, b ; or d1, a, b         fixed sources; the result alternates a&b, a|b (popcount(a^b) bits);
                                            each destination keeps its value
  resf   and d0, a, b ; or d0, a, b         the same results into ONE destination: its cells change every write
  resz   and x0, a, b ; or x0, a, b         the same results, destination x0 (no architectural write)
  rd2i   andi x5, x0, 21 ; andi x5, x0, 26  no register operand is used; bits 24:20 of the two encodings name x21
                                            and x26 (RISC-V keeps register fields in fixed places): does the core read
                                            the register those bits name anyway, and what does it cost?
  rd2r   and x5, x0, x21 ; and x5, x0, x26  the same two registers read as the second operand, result held at 0
  rd1u   lui x5, 21<<3 ; lui x5, 26<<3      bits 19:15 of the encodings name x21 and x26, no operand used
  idx0   and x5, x0, x22                    one register read again (zero contents)
  idx1   and x5, x0, x22 ; and x5, x0, x23  the second source field changes in 1 bit (zero contents)
  idx3   ... x22 ; ... x24                  in 3 bits
  idx5   ... x22 ; ... x9                   in 5 bits
  rn8    and x5, x0, p for p in a cycle of eight registers, one field bit changing per step (zero contents)
  wn1    and x16, x0, x0                    one destination written with 0
  wn2    and x16 / and x17                  two destinations in turn, one field bit apart
  wn8    and d, x0, x0 over a cycle of eight destinations, one field bit changing per step
  nop    nop

Images: W-words are 64-bit with 32 ones; M is a fixed such word (seeded), M32 a second one 32 bits from M.
For rot/rot2: x64 (the sources alternate M and ~M: every rot write changes 64 cells, every rot2 write none, and the
port and the result change in 64 bits an instruction in both) and x0 (every source holds M: nothing changes but the
destination order). For res/resf/resz: k0 (a = b = M), k32 (a = M, b = M32), k64 (b = ~a). For rd2i/rd2r/rd1u: d64
(x21 = M, x26 = ~M), e32 (both M), e0 (both 0), e64 (both all ones). idx*, rn8, wn*, nop: z (every register the form
names holds 0).

Usage:
  python3 make_images.py --list               every kind with its designed counts per instruction
  python3 make_images.py --json               the same as JSON
  python3 make_images.py --emit SRC           write SRC/kernel/regfile_bodies.inc and SRC/host/regfile_kinds.h
  python3 make_images.py --check [SRC]        re-derive every count from the values and, with SRC, compare the files
"""
import argparse, hashlib, json, os, random, sys

M64 = (1 << 64) - 1
BODY = 128
TAIL_IT, TAIL_T, TAIL_DL = 10, 13, 28     # the loop's own registers: iteration count, cycle reading, deadline
PAD = 29                                  # words after the branch: 524 + 116 = 640 bytes, ten 64-byte blocks
PAD_INS = ('addi', TAIL_DL, TAIL_DL, 2)   # the padding instruction (the deadline register is dead after the loop)
CSR_CYCLE = 0xC03                         # hpmcounter3


def pop(x):
    return bin(x & M64).count('1')


# ---------------------------------------------------------------------------------------------- encodings (RV64I)
def enc_r(f7, rs2, rs1, f3, rd, op=0x33):
    return (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | op


def enc_i(imm, rs1, f3, rd, op=0x13):
    return ((imm & 0xFFF) << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | op


def enc_u(imm20, rd, op=0x37):
    return ((imm20 & 0xFFFFF) << 12) | (rd << 7) | op


def enc_b(off, rs2, rs1, f3, op=0x63):
    i = off & 0x1FFF
    return ((((i >> 12) & 1) << 31) | (((i >> 5) & 0x3F) << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12)
            | (((i >> 1) & 0xF) << 8) | (((i >> 11) & 1) << 7) | op)


F3 = {'add': 0, 'and': 7, 'or': 6, 'xor': 4}


def encode(ins):
    op = ins[0]
    if op in ('and', 'or', 'add', 'xor'):
        return enc_r(0, ins[3], ins[2], F3[op], ins[1])
    if op == 'addi':
        return enc_i(ins[3], ins[2], 0, ins[1])
    if op == 'andi':
        return enc_i(ins[3], ins[2], 7, ins[1])
    if op == 'lui':
        return enc_u(ins[2], ins[1])
    raise ValueError(op)


def text(ins):
    op = ins[0]
    if op in ('and', 'or', 'add', 'xor'):
        return '%s x%d, x%d, x%d' % ins
    if op in ('addi', 'andi'):
        return '%s x%d, x%d, %d' % ins
    if op == 'lui':
        return 'lui x%d, %d' % ins[1:]
    raise ValueError(op)


def execute(ins, R):
    """architectural result of one instruction; R is a dict reg -> value (x0 = 0)"""
    op = ins[0]
    g = lambda r: 0 if r == 0 else R.get(r, 0)
    if op == 'and':
        return g(ins[2]) & g(ins[3])
    if op == 'or':
        return g(ins[2]) | g(ins[3])
    if op == 'add':
        return (g(ins[2]) + g(ins[3])) & M64
    if op == 'xor':
        return g(ins[2]) ^ g(ins[3])
    if op == 'addi':
        imm = ins[3] - 4096 if ins[3] & 0x800 else ins[3]
        return (g(ins[2]) + imm) & M64
    if op == 'andi':
        imm = (ins[3] - 4096 if ins[3] & 0x800 else ins[3]) & M64
        return g(ins[2]) & imm
    if op == 'lui':
        v = (ins[2] << 12) & 0xFFFFFFFF
        return v | (M64 ^ 0xFFFFFFFF) if v & 0x80000000 else v
    raise ValueError(op)


def uses(ins):
    """(rs1 used, rs2 used) architecturally"""
    op = ins[0]
    if op in ('and', 'or', 'add', 'xor'):
        return True, True
    if op in ('addi', 'andi'):
        return True, False
    return False, False


# ---------------------------------------------------------------------------------------------- forms
S = [18, 19, 20, 21, 22, 23, 24, 25]          # rot/rot2 sources
D = [11, 12, 9, 15, 30, 14, 6, 8]             # rot/rot2 sinks (see the docstring and --check)
CYC8 = [16, 17, 19, 18, 26, 27, 25, 24]       # eight registers, one field bit changing per step (cyclic)


def mv(d, s):
    return ('addi', d, s, 0)


FORMS = {
    'rot': [mv(D[i], S[i]) for i in range(8)] + [mv(D[(i + 3) % 8], S[i]) for i in range(8)],
    'rot2': [mv(D[i], S[i]) for i in range(8)] + [mv(D[(i + 2) % 8], S[i]) for i in range(8)],
    'res': [('and', 5, 18, 19), ('or', 6, 18, 19)],
    'resf': [('and', 5, 18, 19), ('or', 5, 18, 19)],
    'resz': [('and', 0, 18, 19), ('or', 0, 18, 19)],
    'rd2i': [('andi', 5, 0, 21), ('andi', 5, 0, 26)],
    'rd2r': [('and', 5, 0, 21), ('and', 5, 0, 26)],
    'rd1u': [('lui', 5, 21 << 3), ('lui', 5, 26 << 3)],
    'idx0': [('and', 5, 0, 22)],
    'idx1': [('and', 5, 0, 22), ('and', 5, 0, 23)],
    'idx3': [('and', 5, 0, 22), ('and', 5, 0, 24)],
    'idx5': [('and', 5, 0, 22), ('and', 5, 0, 9)],
    'rn8': [('and', 5, 0, p) for p in CYC8],
    'wn1': [('and', 16, 0, 0)],
    'wn2': [('and', 16, 0, 0), ('and', 17, 0, 0)],
    'wn8': [('and', d, 0, 0) for d in CYC8],
    'nop': [('addi', 0, 0, 0)],
}
FORM_ID = {f: i + 1 for i, f in enumerate(FORMS)}


def body(form):
    ph = FORMS[form]
    assert BODY % len(ph) == 0, form
    return ph * (BODY // len(ph))


def tail_words():
    """the loop's own three instructions after the body, then the padding: the same words in every form"""
    off = -4 * (BODY + 2)
    return ([enc_i(1, TAIL_IT, 0, TAIL_IT), (CSR_CYCLE << 20) | (2 << 12) | (TAIL_T << 7) | 0x73,
             enc_b(off, TAIL_DL, TAIL_T, 6)] + [encode(PAD_INS)] * PAD)


def fetch_bits(form, B, past):
    """fetched-bit changes per loop iteration in aligned B-byte blocks, in loop order (the block holding the branch,
    then, if past, the block after it, then back to the head)"""
    w = loop_words(form)
    per = B // 4
    last = ((BODY + 3) * 4 - 1) // B
    order = list(range(last + 1)) + ([last + 1] if past else [])
    blk = [w[per * k: per * k + per] for k in range(last + 2)]
    return sum(sum(pop(x ^ y) for x, y in zip(blk[order[i]], blk[order[(i + 1) % len(order)]])) for i in range(len(order)))


def frame_residue(fa, fb):
    """{(B, past): fetched-bit changes per iteration of form fa minus form fb}"""
    return {(B, p): fetch_bits(fa, B, p) - fetch_bits(fb, B, p) for B in (8, 16, 32, 64) for p in (0, 1)}


def loop_words(form):
    return [encode(x) for x in body(form)] + tail_words()


def regs_named(form):
    """every register a form's body names in any field (rd, bits 19:15, bits 24:20), x0 excluded"""
    out = set()
    for ins in FORMS[form]:
        w = encode(ins)
        for r in ((w >> 7) & 31, (w >> 15) & 31, (w >> 20) & 31):
            if r:
                out.add(r)
    return sorted(out)


def regs_written(form):
    return sorted({ins[1] for ins in FORMS[form] if ins[1]})


def field_toggles(form, w):
    """per encoding bit, the changes between instruction t and t + w over the cyclic body"""
    ws = [encode(x) for x in body(form)]
    return [sum(((ws[t] >> b) & 1) != ((ws[(t + w) % BODY] >> b) & 1) for t in range(BODY)) for b in range(32)]


# ---------------------------------------------------------------------------------------------- images
def word32(rng):
    """a 64-bit word with exactly 32 ones"""
    pos = rng.sample(range(64), 32)
    v = 0
    for p in pos:
        v |= 1 << p
    return v


def images():
    rng = random.Random('regfile|M')
    Mw = word32(rng)
    # a second word of 32 ones that differs from M in exactly 32 bits: move 16 of M's ones onto 16 of its zeros
    ones = [i for i in range(64) if (Mw >> i) & 1]
    zeros = [i for i in range(64) if not (Mw >> i) & 1]
    r2 = random.Random('regfile|M32')
    off, on = r2.sample(ones, 16), r2.sample(zeros, 16)
    M32 = Mw
    for i in off:
        M32 &= ~(1 << i)
    for i in on:
        M32 |= 1 << i
    img = {}
    # x64: the sources alternate M and ~M (rot changes all 64 cells a write, rot2 none; the port and the result change
    # in 64 bits an instruction in both); x0: every source holds M (nothing changes but the destination order)
    rot_words = {'x64': [Mw if j % 2 == 0 else Mw ^ M64 for j in range(8)], 'x0': [Mw] * 8}
    for name, src in rot_words.items():
        R = {S[i]: src[i] for i in range(8)}
        # sinks start at d_m = s_(m-3), rot's steady state (rot2's on x0; on x64 rot2's first pass writes each once)
        for m in range(8):
            R[D[m]] = src[(m - 3) % 8]
        img[name] = R
    img['k0'] = {18: Mw, 19: Mw, 5: Mw, 6: Mw}
    img['k32'] = {18: Mw, 19: M32, 5: Mw & M32, 6: Mw | M32}
    img['k64'] = {18: Mw, 19: Mw ^ M64, 5: 0, 6: M64}
    img['d64'] = {21: Mw, 26: Mw ^ M64, 5: 0}
    img['e32'] = {21: Mw, 26: Mw, 5: 0}
    img['e0'] = {21: 0, 26: 0, 5: 0}
    img['e64'] = {21: M64, 26: M64, 5: 0}
    img['z'] = {}
    return img, Mw, M32


KINDS = [('rot', 'x64'), ('rot2', 'x64'), ('rot', 'x0'), ('rot2', 'x0'),
         ('res', 'k0'), ('res', 'k32'), ('res', 'k64'),
         ('resf', 'k0'), ('resf', 'k32'), ('resf', 'k64'),
         ('resz', 'k0'), ('resz', 'k32'), ('resz', 'k64'),
         ('rd2i', 'd64'), ('rd2i', 'e32'), ('rd2i', 'e0'), ('rd2i', 'e64'),
         ('rd2r', 'd64'), ('rd2r', 'e32'), ('rd2r', 'e0'), ('rd2r', 'e64'),
         ('rd1u', 'd64'), ('rd1u', 'e32'), ('rd1u', 'e0'), ('rd1u', 'e64'),
         ('idx0', 'z'), ('idx1', 'z'), ('idx3', 'z'), ('idx5', 'z'), ('rn8', 'z'),
         ('wn1', 'z'), ('wn2', 'z'), ('wn8', 'z'), ('nop', 'z')]


def kind_name(form, im):
    return '%s.%s' % (form, im)


def full_regs(form, im, IMG):
    """register values at the start of the loop: the image, then 0 for every other register the form names"""
    R = {r: 0 for r in regs_named(form)}
    for r, v in IMG[im].items():
        if r in R:
            R[r] = v
    return R


# ---------------------------------------------------------------------------------------------- designed counts
def counts(form, im, IMG):
    """per body instruction, steady state (the second of two passes over the body), with the previous instruction
    taken cyclically: bits that change between neighbouring instructions in the value of the register named by
    bits 19:15 (f1) and 24:20 (f2), the same only where the instruction uses that operand (a1, a2), the result (res),
    the destination's stored value (cell, rd != x0), the two source fields (i1, i2), the destination field (iw), the
    encoding (enc), and the ones held in the registers the two fields name (h1, h2)."""
    R = dict(full_regs(form, im, IMG))
    b = body(form)
    tot = {k: 0 for k in ('f1', 'f2', 'a1', 'a2', 'res', 'cell', 'i1', 'i2', 'iw', 'enc', 'h1', 'h2', 'writes')}
    prev = None
    for npass in range(2):
        for ins in b:
            w = encode(ins)
            r1, r2, rd = (w >> 15) & 31, (w >> 20) & 31, (w >> 7) & 31
            u1, u2 = uses(ins)
            g = lambda r: 0 if r == 0 else R.get(r, 0)
            v1, v2 = g(r1), g(r2)
            res = execute(ins, R)
            cur = {'w': w, 'r1': r1, 'r2': r2, 'rd': rd, 'v1': v1, 'v2': v2, 'u1': u1, 'u2': u2, 'res': res}
            if npass == 1:
                p = prev
                tot['f1'] += pop(v1 ^ p['v1'])
                tot['f2'] += pop(v2 ^ p['v2'])
                tot['a1'] += pop(v1 ^ p['v1']) if (u1 and p['u1']) else (pop(v1) if u1 else 0)
                tot['a2'] += pop(v2 ^ p['v2']) if (u2 and p['u2']) else (pop(v2) if u2 else 0)
                tot['res'] += pop(res ^ p['res'])
                tot['i1'] += pop(r1 ^ p['r1'])
                tot['i2'] += pop(r2 ^ p['r2'])
                tot['iw'] += pop(rd ^ p['rd'])
                tot['enc'] += pop(w ^ p['w'])
                tot['h1'] += pop(v1)
                tot['h2'] += pop(v2)
                if rd:
                    tot['cell'] += pop(res ^ g(rd))
                    tot['writes'] += 1
            if rd:
                R[rd] = res
            prev = cur
    n = float(len(b))
    return {k: v / n for k, v in tot.items()}, R


def table():
    IMG, Mw, M32 = images()
    rows = []
    for form, im in KINDS:
        c, Rend = counts(form, im, IMG)
        R0 = full_regs(form, im, IMG)
        rows.append({'kind': kind_name(form, im), 'form': form, 'form_id': FORM_ID[form], 'image': im,
                     'regs': {('x%d' % r): '%016x' % v for r, v in sorted(R0.items())},
                     'end': {('x%d' % r): '%016x' % Rend[r] for r in regs_written(form)},
                     'per_instr': {k: round(v, 6) for k, v in c.items()}})
    return rows, Mw, M32


# ---------------------------------------------------------------------------------------------- emitters
def emit_inc():
    """the kernel's loop bodies, the loop's own tail and padding, and per-form register lists, as C macros"""
    out = ['/* Generated by make_images.py --emit: do not edit. The regfile loop bodies (128 instructions each), the',
           ' * loop tail and padding that every form shares, and the registers each form names (loaded from the image',
           ' * before the loop) and writes. */', '']
    out.append('#define RF_IT "x%d"' % TAIL_IT)
    out.append('#define RF_DL "x%d"' % TAIL_DL)
    out.append('#define RF_TAIL "addi x%d, x%d, 1\\n""csrr x%d, hpmcounter3\\n""bltu x%d, x%d, 1b\\n"' % (
        TAIL_IT, TAIL_IT, TAIL_T, TAIL_T, TAIL_DL))
    out.append('#define RF_PAD ' + ''.join('"%s\\n"' % text(PAD_INS) for _ in range(PAD)))
    out.append('#define RF_TAIL_CLOBBER "x%d", "x%d", "x%d"' % (TAIL_IT, TAIL_T, TAIL_DL))
    out.append('')
    for form in FORMS:
        lines = ''.join('"%s\\n"' % text(ins) for ins in body(form))
        out.append('#define RF_BODY_%s %s' % (form.upper(), lines))
        named = regs_named(form)
        loads = ''.join('"ld x%d, %d(%%[img])\\n"' % (r, 8 * r) for r in named)
        stores = ''.join('"sd x%d, %d(%%[out])\\n"' % (r, 8 * r) for r in named)
        clob = ', '.join(['"x%d"' % r for r in named] + ['"memory"'])
        out.append('#define RF_LOAD_%s %s' % (form.upper(), loads or '""'))
        out.append('#define RF_STORE_%s %s' % (form.upper(), stores or '""'))
        out.append('#define RF_CLOBBER_%s %s' % (form.upper(), clob))
        out.append('#define RF_FORM_%s %d' % (form.upper(), FORM_ID[form]))
        out.append('')
    out.append('#define RF_FORMS(X) ' + ' '.join('X(%s)' % f.upper() for f in FORMS))
    return '\n'.join(out) + '\n'


def emit_h(rows):
    keys = ['f1', 'f2', 'a1', 'a2', 'res', 'cell', 'i1', 'i2', 'iw', 'enc', 'h1', 'h2', 'writes']
    out = ['// Generated by make_images.py --emit: do not edit. One row per kind: name, form, register image',
           '// (values at the loop start, by register number), the written registers\' values after the loop, and the',
           '// designed counts per body instruction (make_images.py explains each).', '#pragma once', '#include <stdint.h>',
           '', 'struct RfKind {', '  const char* name;', '  int form;', '  uint64_t regs[32];', '  uint32_t named;',
           '  uint32_t written;', '  uint64_t end[32];', '  double per_instr[%d];' % len(keys), '};', '',
           'static const char* const RF_COUNT_KEYS[%d] = {%s};' % (len(keys), ', '.join('"%s"' % k for k in keys)),
           'static const int RF_NCOUNTS = %d;' % len(keys), '', 'static const RfKind RF_KINDS[] = {']
    for r in rows:
        regs = [0] * 32
        named = 0
        for k, v in r['regs'].items():
            regs[int(k[1:])] = int(v, 16)
            named |= 1 << int(k[1:])
        end = [0] * 32
        written = 0
        for k, v in r['end'].items():
            end[int(k[1:])] = int(v, 16)
            written |= 1 << int(k[1:])
        out.append('  {"%s", %d,' % (r['kind'], r['form_id']))
        out.append('   {%s},' % ', '.join('0x%016xull' % v for v in regs))
        out.append('   0x%08xu, 0x%08xu,' % (named, written))
        out.append('   {%s},' % ', '.join('0x%016xull' % v for v in end))
        out.append('   {%s}},' % ', '.join(repr(float(r['per_instr'][k])) for k in keys))
    out.append('};')
    out.append('static const int RF_NKINDS = %d;' % len(rows))
    return '\n'.join(out) + '\n'


def check_rows(rows, Mw, M32):
    bad = 0
    # the frame: no form names the loop's own registers or x1-x4 (ra, sp, gp, tp); rot/rot2 sources are never written
    for f in FORMS:
        named = set(regs_named(f))
        if named & {TAIL_IT, TAIL_T, TAIL_DL, 1, 2, 3, 4}:
            print('BAD form %s names a reserved register: %s' % (f, sorted(named & {TAIL_IT, TAIL_T, TAIL_DL, 1, 2, 3, 4})))
            bad += 1
        if len(body(f)) != BODY:
            print('BAD body length', f)
            bad += 1
    if set(regs_written('rot')) & set(S) or set(regs_written('rot2')) & set(S) or set(D) & set(S) or len(set(D)) != 8:
        print('BAD rot sources/sinks')
        bad += 1
    # rot and rot2: the same encoding-bit changes, bit position by bit position, at distances 1, 2, 4 and 8
    for w in (1, 2, 4, 8):
        a, b = field_toggles('rot', w), field_toggles('rot2', w)
        if a != b:
            print('BAD rot/rot2 field changes differ at distance %d: %s' % (w, [x - y for x, y in zip(a, b)]))
            bad += 1
    # the frame: its length, and the fetched bits where a body meets it (rot against rot2, resf against resz)
    tw = tail_words()
    if len(tw) != 3 + PAD or (BODY + 3 + PAD) * 4 % 64:
        print('BAD frame length')
        bad += 1
    for fa, fb in (('rot', 'rot2'), ('resf', 'resz')):
        r = frame_residue(fa, fb)
        if max(abs(v) for v in r.values()) > 4:
            print('BAD fetched-bit changes %s - %s: %s' % (fa, fb, r))
            bad += 1
    # every kind: designed counts as each form and image say
    by = {r['kind']: r['per_instr'] for r in rows}
    for r in rows:
        pi = r['per_instr']
        f = r['form']
        if f in ('rot', 'rot2'):
            c = 64 if r['image'] == 'x64' else 0
            kk = c if f == 'rot' else 0
            if abs(pi['cell'] - kk) > 1e-9 or abs(pi['f1'] - c) > 1e-9 or abs(pi['res'] - c) > 1e-9:
                print('BAD', r['kind'], pi)
                bad += 1
        if f in ('res', 'resf', 'resz'):
            kk = int(r['image'][1:])
            if abs(pi['res'] - kk) > 1e-9 or pi['f1'] or pi['f2']:
                print('BAD', r['kind'], pi)
                bad += 1
            if f == 'res' and pi['cell']:
                print('BAD res cell', r['kind'])
                bad += 1
            if f == 'resf' and abs(pi['cell'] - kk) > 1e-9:
                print('BAD resf cell', r['kind'])
                bad += 1
        if (f in ('rd2i', 'rd2r') and (pi['res'] or pi['cell'])):
            print('BAD read form result or cell', r['kind'], pi)
            bad += 1
    for im in ('x64', 'x0'):
        a, b = by['rot.' + im], by['rot2.' + im]
        for k in a:
            if k != 'cell' and abs(a[k] - b[k]) > 1e-9:
                print('BAD rot.%s and rot2.%s differ in %s' % (im, im, k))
                bad += 1
    if pop(Mw) != 32 or pop(M32) != 32 or pop(Mw ^ M32) != 32:
        print('BAD M words')
        bad += 1
    return bad


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--emit', metavar='DIR')
    parser.add_argument('--check', nargs='?', const='', metavar='DIR')
    parser.add_argument('--frame', action='store_true', help='fetched-bit changes per iteration, F - S, every train')
    a = parser.parse_args()
    rows, Mw, M32 = table()
    if a.list:
        keys = ['f1', 'f2', 'a1', 'a2', 'res', 'cell', 'i1', 'i2', 'iw', 'enc', 'h1', 'h2']
        print('%-11s ' % 'kind' + ' '.join('%6s' % k for k in keys))
        for r in rows:
            print('%-11s ' % r['kind'] + ' '.join('%6.2f' % r['per_instr'][k] for k in keys))
    if a.json:
        print(json.dumps({'body': BODY, 'tail': ['%08x' % w for w in tail_words()], 'kinds': rows}, indent=1))
    if a.frame:
        here = os.path.dirname(os.path.abspath(__file__))
        seen = []
        print('fetched-bit changes per loop iteration (131 instructions), F - S, aligned blocks of 8 .. 64 bytes; '
              '"+" with the block after the branch')
        for line in open(os.path.join(here, 'trains.tsv')):
            if not line.strip() or line.startswith('#'):
                continue
            tr, F, S = line.split('\t')[1:4]
            fa, fb = F.split('.')[0], S.split('.')[0]
            if (tr, fa, fb) in seen:
                continue
            seen.append((tr, fa, fb))
            r = frame_residue(fa, fb)
            print('%-4s %-5s - %-5s ' % (tr, fa, fb) + ' '.join('%2dB%s %+4d' % (B, '+' if p else ' ', v)
                                                           for (B, p), v in sorted(r.items())))
    if a.emit:
        for sub, fn, txt in (('kernel', 'regfile_bodies.inc', emit_inc()), ('host', 'regfile_kinds.h', emit_h(rows))):
            os.makedirs(os.path.join(a.emit, sub), exist_ok=True)
            open(os.path.join(a.emit, sub, fn), 'w').write(txt)
    if a.check is not None:
        bad = check_rows(rows, Mw, M32)
        if a.check:
            for fn, txt in (('kernel/regfile_bodies.inc', emit_inc()), ('host/regfile_kinds.h', emit_h(rows))):
                p = os.path.join(a.check, fn)
                if not os.path.exists(p) or open(p).read() != txt:
                    print('BAD', p, 'differs from what make_images.py writes')
                    bad += 1
        h = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
        print('check: %d kinds, %d forms, %s; kinds sha256 %s' % (len(rows), len(FORMS), 'OK' if not bad else 'FAIL %d' % bad, h))
        sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
