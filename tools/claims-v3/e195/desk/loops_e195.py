#!/usr/bin/env python3
"""Where E195's timed loops sit in the kernel ELF (a desk check of code; no device, no simulator).

    python3 -I -B loops_e195.py <objdump> <x09mem.elf>

Finds the five timed loops as the proposal's check_elf.py does (the access instruction and the loop's backward branch)
and, inside each paced loop, its poll loop (the backward branch to a point inside the loop). For each it prints the head's
address, the head modulo 32 (the lab's E61 trap: a loop's issue rate can depend on its head's address mod 32), the bytes
of the body and how many instructions are 2-byte (compressed) encodings. It then sets the paced store loop beside the
paced no-store loop instruction by instruction: the same mnemonics and encoding lengths, the access alone different, and
the distance between them. Prints facts; exit 0 unless a loop is missing.
"""
import re
import subprocess
import sys

od, elf = sys.argv[1], sys.argv[2]
dis = subprocess.run([od, "-d", elf], capture_output=True, text=True, check=True).stdout
ins = []
for line in dis.splitlines():
    m = re.match(r"\s*([0-9a-f]+):\s+([0-9a-f]+)\s+(\S+)\s*(.*)", line)
    if m:
        ins.append((int(m.group(1), 16), len(m.group(2)) // 2, m.group(3), m.group(4).split("#")[0].strip()))
at = {x[0]: i for i, x in enumerate(ins)}


def target(ops):
    m = re.search(r"([0-9a-f]+) <", ops)
    return int(m.group(1), 16) if m else None


loops = {}
for i, (pc, n, op, ops) in enumerate(ins):
    t = target(ops)
    if op in ("bltu", "bgeu", "bne", "blt") and t is not None and t < pc and t in at:
        body = ins[at[t]:i + 1]
        nld = sum(1 for b in body if b[2] == "flw.ps" and b[3].startswith("fs0,0("))
        nst = sum(1 for b in body if b[2] == "csrw" and b[3].startswith(("tensor_store", "0x87f")))
        nfl = sum(1 for b in body if (b[2] == "fsflags" and b[3] == "zero") or (b[2] == "csrw" and b[3].startswith("fflags")))
        paced = any(b[2] == "j" for b in body)
        kind = None
        if (nld, nst, nfl) == (8, 0, 0):
            kind = "flat read"
        elif (nld, nst, nfl) == (0, 8, 0):
            kind = "flat write"
        elif paced and (nld, nst, nfl) == (1, 0, 0):
            kind = "paced read"
        elif paced and (nld, nst, nfl) == (0, 1, 0):
            kind = "paced write"
        elif paced and (nld, nst, nfl) == (0, 0, 1):
            kind = "paced no-store"
        if kind:
            loops[kind] = body
missing = [k for k in ("flat read", "flat write", "paced read", "paced write", "paced no-store") if k not in loops]
for kind in ("flat read", "flat write", "paced read", "paced write", "paced no-store"):
    if kind not in loops:
        continue
    body = loops[kind]
    head = body[0][0]
    nbytes = body[-1][0] + body[-1][1] - head
    short = sum(1 for b in body if b[1] == 2)
    line = (f"{kind:15s} head 0x{head:x} (mod 32 = {head % 32:2d}), {len(body)} instructions, {nbytes} bytes, "
            f"{short} of them 2-byte encodings")
    if kind.startswith("paced"):
        inner = [b for b in body if b[2] == "bltu" and target(b[3]) is not None and head < target(b[3]) <= b[0]]
        if inner:
            ph = target(inner[0][3])
            line += f"; poll loop head 0x{ph:x} (mod 32 = {ph % 32:2d})"
    print(line)
if "paced write" in loops and "paced no-store" in loops:
    a, b = loops["paced write"], loops["paced no-store"]
    pairs = list(zip(a, b))

    def rel(x):
        """operands with a branch's absolute target replaced by its offset from the instruction"""
        t = target(x[3])
        return re.sub(r"[0-9a-f]+ <[^>]*>", f"pc{t - x[0]:+d}", x[3]) if t is not None else x[3]
    diff = [(x, y) for x, y in pairs if (x[1], x[2], rel(x)) != (y[1], y[2], rel(y))]
    print(f"paced write against paced no-store: {len(a)} and {len(b)} instructions; distance 0x{b[0][0] - a[0][0]:x} bytes "
          f"(mod 32 = {(b[0][0] - a[0][0]) % 32}); instructions that differ in mnemonic, length or operands: {len(diff)}")
    for x, y in diff:
        print(f"  0x{x[0]:x} {x[2]} {x[3]}  |  0x{y[0]:x} {y[2]} {y[3]}")
print("LOOPS " + ("FOUND: 5 of 5" if not missing else "MISSING: " + ", ".join(missing)))
sys.exit(1 if missing else 0)
