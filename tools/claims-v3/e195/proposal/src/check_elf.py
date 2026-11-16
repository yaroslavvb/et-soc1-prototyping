#!/usr/bin/env python3
"""Check the kernel ELF's five timed loops against the source's design (no device, no emulator).

    python3 check_elf.py build/kernel/x09mem.elf [--objdump /opt/et/bin/riscv64-unknown-elf-objdump]

Finds each loop by its access instruction (flw.ps into f8 for reads, a write of the tensor-store CSR for writes, by
name or as 0x87f for an objdump that does not know it, a write of zero to the floating-point flags for the paced loop
that stores nothing) and its backward branch, and checks:
flat loops hold exactly 8 accesses, paced loops exactly 1; every wrap of the pointer moves the base register into the
pointer register (not a register into itself); the store loops set x31 to 32 before the loop; the no-store loop is
the paced store loop instruction for instruction but for its access, and holds no tensor store. Prints each loop's
static instruction count per iteration (the wrap's move excluded). Exit 0 when all hold.
"""
import argparse
import re
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument("elf")
parser.add_argument("--objdump", default="/opt/et/bin/riscv64-unknown-elf-objdump")
a = parser.parse_args()
dis = subprocess.run([a.objdump, "-d", a.elf], capture_output=True, text=True, check=True).stdout
ins = []
for line in dis.splitlines():
    m = re.match(r"\s*([0-9a-f]+):\s+[0-9a-f]+\s+(\S+)\s*(.*)", line)
    if m:
        ins.append((int(m.group(1), 16), m.group(2), m.group(3).split("#")[0].strip()))
addr = {x[0]: i for i, x in enumerate(ins)}
TSTORE = ("tensor_store", "0x87f")   # the tensor-store CSR as objdump names it, or its number


def target(ops):
    m = re.search(r"([0-9a-f]+) <", ops)
    return int(m.group(1), 16) if m else None


loops = []
for i, (pc, op, ops) in enumerate(ins):
    if op in ("bltu", "bgeu", "bne", "blt") and target(ops) is not None and target(ops) < pc:
        j = addr.get(target(ops))
        if j is None:
            continue
        body = ins[j:i + 1]
        nld = sum(1 for _, o, s in body if o == "flw.ps" and s.startswith("fs0,0("))
        nst = sum(1 for _, o, s in body if o == "csrw" and s.startswith(TSTORE))
        nfl = sum(1 for _, o, s in body if (o == "fsflags" and s == "zero") or (o == "csrw" and s.startswith("fflags")))
        if nld or nst or nfl:
            loops.append((j, i, nld, nst, nfl, body))
bad = []
seen = set()
shape = {}
for j, i, nld, nst, nfl, body in loops:
    if (nld, nst, nfl) in ((1, 0, 0), (0, 1, 0), (0, 0, 1)) and any(b[1] == "j" for b in body):
        kind = "paced " + ("read" if nld else ("write" if nst else "no-store"))
    elif (nld, nst, nfl) in ((8, 0, 0), (0, 8, 0)):
        kind = "flat " + ("read" if nld else "write")
    else:
        continue
    # the instruction sequence with the access instruction and the registers it names left out
    shape[kind] = [o for _, o, s in body if o not in ("nop", "c.nop") and
                   not (o in ("csrw", "fsflags") and (s.startswith(TSTORE) or s.startswith("fflags") or
                                                      s == "zero"))]
    nops = sum(1 for b in body if b[1] in ("nop", "c.nop"))
    # the pointer wraps: every `mv` right after a forward bltu must move another register
    for k, (pc, op, ops) in enumerate(body):
        if op == "mv":
            dst, src = [x.strip() for x in ops.split(",")[:2]]
            if dst == src:
                bad.append(f"{kind} loop at {body[0][0]:x}: wrap moves {dst} into itself")
    if "write" in kind or "no-store" in kind:
        pre = ins[max(0, j - 30):j]
        if not any(o == "li" and s.replace(" ", "") in ("t6,32", "t6,0x20") for _, o, s in pre + body):
            bad.append(f"{kind} loop at {body[0][0]:x}: x31 is not set to 32 before the loop")
    static = len([b for b in body if b[1] != "mv"])
    seen.add(kind)
    print(f"{kind:14s} loop {body[0][0]:x}-{body[-1][0]:x}: {len(body)} instructions ({static} without the wrap "
          f"moves; {nops} alignment nops), {max(nld, nst, nfl)} access(es) an iteration")
for k in ("flat read", "flat write", "paced read", "paced write", "paced no-store"):
    if k not in seen:
        bad.append(f"no {k} loop found")
if "paced write" in shape and "paced no-store" in shape and shape["paced write"] != shape["paced no-store"]:
    bad.append("the no-store loop is not the paced store loop with its access replaced")
if bad:
    print("CHECK FAIL:")
    for b in bad:
        print("  " + b)
    sys.exit(1)
print("CHECK OK: five timed loops as designed")
