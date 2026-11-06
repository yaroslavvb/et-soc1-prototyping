#!/usr/bin/env python3
"""E180 (the kit's dated note 2, KIT.md.dated-note-2.md section 1; the registration's dated note A1, rule A1-7): do the accumulating
sums walk? The disassembly walk, v2, read AT THE DESK on the box's own kernel listing, which step 22 v3 copies back.

    python3 tools/claims-v3/e180/check_elf_e180_v2.py <the box's objdump -d listing> [--also-160]

check_elf_e180.py (v1, kit note 1, 90a1312f), which stays as committed and still runs on the box at step 6 v2 (its line is kept beside,
never read for a verdict), with the kit verifier's two walk faults fixed (kitv-e180, Fri 6 Nov 2026: fault 1 major, fault 2 minor):
  1. The zeroing block is the case's OWN: the nearest complete block (fxor.pi f8..f15, f0, f0) before the loop's head with no
     unconditional jump (j, jr, ret, tail, or a jal or jalr without a link) and no backward branch between it and the head, looked for
     at most 400 instructions back. Another case's block, behind that case's own loop and exit jump, is never taken. v1 wanted exactly
     one block in the 400 instructions before the loop; the compiler lays the generated cases out about 104 instructions apart, so on the
     box kernel 261 and 262 would each see the other's block, and one of the two would read UNREAD in either order.
  2. The readings are A1-7's words (E180.md.dated-note-A1.md section 7), which bind:
     FAIL    the body is found once and, on the sums' path from the end of the case's own zeroing block to the loop's backward branch,
             there is a write to f8-f15 by an instruction other than the 64 body ops (an f-register destination; a store's register,
             and any other read, is not a write), or a call; or the zeroing block lies inside the loop. Every reason found is named.
     UNREAD  no listing (A1-7's "no objdump": the file is absent or holds no instruction), or the body not found once (A1-7); and the two
             cases where the listing does not show what A1-7's words presuppose, so that no FAIL can be read: the loop's backward branch
             not within 30 instructions of the body (E61's reading), or no zeroing block of the case's own before a clean loop (the
             walker's limit, not the kernel's: an asm volatile block is never deleted).
     PASS    otherwise.
     Other f-register instructions in the loop (E61's rule, which v1 read as FAIL), stores of f8-f15 on the path, and earlier zeroing
     blocks in the same case are listed as remarks on the line, never as reasons.
Each mode prints one line in v1's form, "<PASS|FAIL|UNREAD> <name> mode <m>: ...", which score_e180_v2.elf_reading reads by its first word,
and the last line counts them. Exit 0 unless a mode reads FAIL (exit 1), as v1. With --also-160 the plain mode 160 is walked by v1's own
function, unchanged: a control of the parse on a real listing, not an A1-7 reading. Standard library only; it reads one file.
SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_elf_e180 as v1  # noqa: E402  (v1's parse, register names, find, is_f, is_call and the modes, unchanged)

SUMS = v1.SUMS
WINDOW = 400          # v1's window: how far back the case's own zeroing block is looked for (never past a boundary)
TAIL = 30             # E61's: the loop's backward branch within 30 instructions after the body
UNCOND = {"j", "jr", "ret", "tail", "mret", "sret", "uret"}


def target_of(t):
    """the hex address a branch or jump names as its last operand, or None"""
    if not t[2]:
        return None
    tok = t[2][-1].split()[0]
    return int(tok, 16) if re.fullmatch(r"[0-9a-f]+", tok) else None


def is_store(t):
    """an f-register store (fsw, fsw.ps, fswl.ps, fsd, ...): its first operand is read, not written"""
    return t[1].startswith("fs") and bool(t[2]) and "(" in t[2][-1]


def f_write(t):
    """the f register an instruction writes, or None: its first operand when that is an f register, unless it is a store or a branch"""
    if not t[2] or is_store(t) or t[1].startswith("b"):
        return None
    return v1.freg(t[2][0])


def is_boundary(t):
    """control never falls through it: an unconditional jump or return, or a backward branch (another loop's end)"""
    mn, ops = t[1], t[2]
    if mn in UNCOND:
        return True
    if mn in ("jal", "jalr") and ops and ops[0] in ("zero", "x0"):
        return True
    if mn.startswith("b"):
        a = target_of(t)
        return a is not None and a <= t[0]
    return False


def at(t):
    return f"{t[1]} at {t[0]:x}"


def walk(ins, mode, spec):
    body = [v1.norm(o) for o in spec["body"]] * 8
    zero = [v1.norm(o) for o in spec["zero"]]
    head = f"{spec['name']:28s} mode {mode}:"
    if not ins:
        return "UNREAD", f"{head} no objdump listing (no instruction parsed)"
    hits = v1.find(ins, body)
    if len(hits) != 1:
        return "UNREAD", f"{head} RUN body of {len(body)} ops found {len(hits)} time(s)"
    i = hits[0]
    j = i + len(body)
    tail = ins[j:j + TAIL]
    br = next((k for k, t in enumerate(tail) if t[1].startswith("b") and target_of(t) is not None and target_of(t) <= ins[i][0]), None)
    if br is None:
        return "UNREAD", f"{head} RUN body found once; no backward branch to it within {TAIL} instructions (the loop's end not found)"
    target = target_of(tail[br])
    kb = j + br                                   # the loop's backward branch
    kh = i                                        # the loop's head: the first instruction at or after the branch's target
    while kh > 0 and ins[kh - 1][0] >= target:
        kh -= 1
    loop = range(kh, kb + 1)
    in_body = set(range(i, j))
    why, notes = [], []
    zhits = v1.find(ins, zero)
    inside = [z for z in zhits if kh <= z <= kb]
    if inside:
        why.append(f"its zeroing block inside the loop (at {ins[inside[0]][0]:x})")
    w_in = [ins[k] for k in loop if k not in in_body and f_write(ins[k]) in SUMS]
    if w_in:
        why.append(f"{len(w_in)} write(s) to f8-f15 inside the loop other than the body's ({at(w_in[0])})")
    c_in = [ins[k] for k in loop if v1.is_call(ins[k])]
    if c_in:
        why.append(f"a call inside the loop ({at(c_in[0])})")
    other = [ins[k] for k in loop if k not in in_body and v1.is_f(ins[k]) and f_write(ins[k]) not in SUMS]
    if other:
        notes.append(f"remark: {len(other)} other f-register instruction(s) in the loop, not an A1-7 reason (E61's rule; v1 read FAIL): "
                     f"{at(other[0])}")
    msg = f"{head} RUN body of {len(body)} ops found once, loop {target:x}-{tail[br][0]:x} ({kb - kh + 1} instructions)"
    zends = {z + len(zero) - 1: z for z in zhits}
    z, stop, k = None, None, kh - 1
    while k >= 0 and k >= kh - WINDOW:
        if k in zends:
            z = zends[k]
            break
        if is_boundary(ins[k]):
            stop = ins[k]
            break
        k -= 1
    if z is None:
        if why:
            return "FAIL", f"{msg}; " + "; ".join(why + notes)
        where = f"the scan stopped at {at(stop)}" if stop else f"none in the {WINDOW} instructions before the loop"
        return "UNREAD", f"{msg}; no zeroing block of the case's own before the loop ({where}): the walk cannot place the sums' start" + \
            "".join(f"; {n}" for n in notes)
    between = ins[z + len(zero):kh]
    w_b = [t for t in between if f_write(t) in SUMS]
    c_b = [t for t in between if v1.is_call(t)]
    s_b = [t for t in between if is_store(t) and v1.freg(t[2][0]) in SUMS]
    if w_b:
        why.append(f"{len(w_b)} write(s) to f8-f15 between the zeroing block and the loop ({at(w_b[0])})")
    if c_b:
        why.append(f"a call between the zeroing block and the loop ({at(c_b[0])})")
    if s_b:
        notes.append(f"remark: {len(s_b)} store(s) of f8-f15 between the zeroing block and the loop, reads not writes ({at(s_b[0])})")
    earlier = [q for q in zhits if kh - WINDOW <= q < z and all(not is_boundary(ins[m]) for m in range(q, z))]
    if earlier:
        notes.append(f"remark: {len(earlier)} earlier zeroing block(s) in the case's own code; the nearest is the sums' start")
    msg += (f"; the case's own zeroing block {ins[i][0] - ins[z][0]} bytes before the body, outside the loop, "
            f"{len(between)} instructions between")
    if why:
        return "FAIL", f"{msg}; " + "; ".join(why + notes)
    return "PASS", msg + "".join(f"; {n}" for n in notes)


def main(argv):
    if not argv or argv[0].startswith("-"):
        print("usage: check_elf_e180_v2.py <objdump -d listing> [--also-160]")
        return 2
    path = argv[0]
    present = os.path.isfile(path)
    ins = v1.parse(path) if present else []
    res = []
    for mode in (261, 262):
        spec = v1.MODES[mode]
        if not present:
            v, msg = "UNREAD", f"{spec['name']:28s} mode {mode}: no objdump listing ({os.path.basename(path)} is not there)"
        else:
            v, msg = walk(ins, mode, spec)
        res.append(v)
        print(f"{v} {msg}")
    if "--also-160" in argv:
        if ins:
            v, msg = v1.walk(ins, 160, v1.M160)
        else:
            v, msg = "UNREAD", f"{v1.M160['name']:28s} mode 160: no objdump listing"
        res.append(v)
        print(f"{v} {msg}")
    print(f"ELFCHECK-E180-V2: {res.count('PASS')} PASS, {res.count('FAIL')} FAIL, {res.count('UNREAD')} UNREAD "
          f"(of {len(res)}; {len(ins)} instructions parsed; A1-7's words, KIT.md.dated-note-2.md section 1)")
    return 1 if "FAIL" in res else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
