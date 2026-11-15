#!/usr/bin/env python3
"""E193 desk check of code (registration, before any datum): the built kernel's timed bodies against their design.

    python3 -I -B bodies_e193.py <objdump> <x04clock.elf> <gen_blocks.py>

Reads the kernel's disassembly (`objdump -d -M numeric,no-aliases`) and checks, without running anything:
  1. every X04_MIX body that gen_blocks.py designs (4 classes x 7 spacings, plus the two clustered fadd.ps bodies: 30) is in
     the ELF exactly once, slot for slot (mnemonic and registers), every slot a 4-byte instruction;
  2. the spin arm's 512-slot no-op sled and the duty arm's 64-slot no-op sled (each a run of 4-byte `addi x0,x0,0`), and the
     stall arm's chain of 64 dependent 64-bit `div` on one register;
  3. for each body, the loop it sits in: the backward branch that closes it, the loop head (the branch's target) and that
     address mod 32 and mod 64 (the lab's trap, docs/findings/14-card-behaviour.md: a loop head's address mod 32 has set a
     loop's issue rate, E61), and the instructions of one iteration outside the body;
  4. the cycle-counter reads: every `hpmcounter3` read comes in a group of four (the four-read form), each group 16-byte
     aligned (the source's `.p2align 4`).
Prints a report; exit 0 when 1, 2 and 4 hold, else 1. Paths are printed as basenames only.
"""
import collections
import importlib.util
import os
import re
import subprocess
import sys

objdump, elf, gen = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location("gen_blocks", gen)
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)

dis = subprocess.run([objdump, "-d", "-M", "numeric,no-aliases", elf], capture_output=True, text=True, check=True).stdout
LINE = re.compile(r"^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+(\S+)\s*(.*?)\s*$")
ins = []
for ln in dis.splitlines():
    m = LINE.match(ln)
    if m:
        addr, raw, mn, ops = int(m.group(1), 16), m.group(2), m.group(3), m.group(4)
        ops = re.sub(r"\s*<[^>]*>", "", ops)
        ins.append((addr, len(raw) // 2, mn, ops.replace(" ", "")))
print("objdump of %s: %d instructions, %d of them 2-byte" % (os.path.basename(elf), len(ins),
                                                          sum(1 for i in ins if i[1] == 2)))


def norm(s):
    """'fadd.ps f8, f0, f1' -> ('fadd.ps', 'f8,f0,f1'); the design's no-op 'addi x0, x0, 0' -> ('addi', 'x0,x0,0')."""
    mn, _, ops = s.partition(" ")
    return mn, ops.replace(" ", "")


key = [(i[2], i[3]) for i in ins]
size = [i[1] for i in ins]
NOP = ("addi", "x0,x0,0")
ok = True


def loop_of(start, end):
    """The first backward branch at or after `end` whose target is at or before `start`: (branch index, head index)."""
    addr2idx = {i[0]: k for k, i in enumerate(ins)}
    for j in range(end, min(end + 40, len(ins))):
        mn, ops = ins[j][2], ins[j][3]
        if mn.startswith("b") and mn not in ("break",):
            tgt = int(ops.split(",")[-1], 16) if re.fullmatch(r"[0-9a-f]+", ops.split(",")[-1]) else None
            if tgt is not None and tgt <= ins[start][0] and tgt in addr2idx:
                return j, addr2idx[tgt]
    return None, None


def describe_loop(start, n):
    j, h = loop_of(start, start + n)
    if j is None:
        return "no closing backward branch found", None
    extra = [ins[k][2] for k in list(range(h, start)) + list(range(start + n, j + 1))]
    hd = ins[h][0]
    return ("head 0x%x (mod 32 = %d, mod 64 = %d), %d-slot body + %d other instructions an iteration (%s)" % (
        hd, hd % 32, hd % 64, n, len(extra), " ".join(extra))), hd % 32


# 1. the 30 X04_MIX bodies
print("\n" "1. X04_MIX bodies (gen_blocks.py's design), each searched slot for slot:")
designs = []
for cid, (name, mnem) in sorted(G.CLASSES.items()):
    for p in G.SPACINGS:
        designs.append((cid, mnem, p, 0))
for cid, p in G.CLUSTERED:
    designs.append((cid, G.CLASSES[cid][1], p, 1))
mods = collections.Counter()
found = 0
for cid, mnem, p, cl in designs:
    body = [norm(s) for s in G.body(mnem, p, cl)]
    hits = [k for k in range(len(key) - len(body) + 1) if key[k] == body[0] and key[k:k + len(body)] == body]
    four = all(size[k + t] == 4 for k in hits for t in range(len(body)))
    tag = "%s P=%d%s" % (mnem, p, " clustered" if cl else "")
    if len(hits) == 1 and four:
        found += 1
        d, m32 = describe_loop(hits[0], len(body))
        mods[m32] += 1
        print("  OK   %-26s at 0x%x: %d slots, %d class instructions; %s" % (tag, ins[hits[0]][0], len(body),
              sum(1 for b in body if b != NOP), d))
    else:
        ok = False
        print("  BAD  %-26s found %d times, all 4-byte: %s" % (tag, len(hits), four))
print("  %d of %d bodies found once, slot for slot, every slot 4 bytes; loop heads mod 32: %s" % (
    found, len(designs), dict(sorted(mods.items()))))

# 2. the no-op sleds and the divide chain
print("\n" "2. the no-op sleds and the divide chain:")
runs, k = [], 0
while k < len(key):
    if key[k] == NOP and size[k] == 4:
        j = k
        while j < len(key) and key[j] == NOP and size[j] == 4:
            j += 1
        runs.append((k, j - k))
        k = j
    else:
        k += 1
long_runs = [(k, n) for k, n in runs if n >= 64]
mix_cover = set()
for cid, mnem, p, cl in designs:
    body = [norm(s) for s in G.body(mnem, p, cl)]
    for k in range(len(key) - len(body) + 1):
        if key[k] == body[0] and key[k:k + len(body)] == body:
            mix_cover.update(range(k, k + len(body)))
alone = [(k, n) for k, n in long_runs if k not in mix_cover]
for k, n in alone:
    d, _ = describe_loop(k, n)
    print("  no-op run of %d 4-byte slots at 0x%x (outside every class body); %s" % (n, ins[k][0], d))
cnt512 = sum(1 for _, n in alone if n == 512)
cnt64 = sum(1 for _, n in alone if n == 64)
print("  runs outside the class bodies: %d of exactly 512 (the spin sled), %d of exactly 64 (the duty sled); others: %s" % (
    cnt512, cnt64, [n for _, n in alone if n not in (512, 64)]))
if cnt512 != 1 or cnt64 != 1:
    ok = False
divs, k = [], 0
while k < len(key):
    if key[k][0] == "div":
        j = k
        while j < len(key) and key[j][0] == "div" and key[j][1] == key[k][1]:
            j += 1
        divs.append((k, j - k, key[k][1]))
        k = j
    else:
        k += 1
for k, n, ops in divs:
    dst, a, b = ops.split(",")
    dep = dst == a
    d, _ = describe_loop(k, n) if n >= 64 else ("", None)
    print("  div run of %d at 0x%x, operands %s, each depends on the last: %s; %s" % (n, ins[k][0], ops, dep, d))
if not any(n == 64 and ops.split(",")[0] == ops.split(",")[1] for _, n, ops in divs):
    ok = False

# 4. the cycle-counter reads
print("\n" "4. hpmcounter3 reads:")
groups, k = [], 0
while k < len(key):
    if key[k][0] == "csrrs" and "hpmcounter3" in key[k][1]:
        j = k
        while j < len(key) and key[j] == key[k]:
            j += 1
        groups.append((k, j - k))
        k = j
    else:
        k += 1
sizes = collections.Counter(n for _, n in groups)
aligned = sum(1 for k, n in groups if ins[k][0] % 16 == 0)
print("  %d groups; group sizes %s; groups starting 16-byte aligned: %d of %d" % (
    len(groups), dict(sizes), aligned, len(groups)))
if set(sizes) != {4} or aligned != len(groups):
    ok = False
for name in ("hpmcounter4", "hpmcounter5", "hpmcounter7", "hpmcounter8"):
    g = [k for k in range(len(key)) if key[k][0] == "csrrs" and name in key[k][1]]
    print("  %s reads: %d" % (name, len(g)))

print("\nBODIES CHECK %s" % ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
