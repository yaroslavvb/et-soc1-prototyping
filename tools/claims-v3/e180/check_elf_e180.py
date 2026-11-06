#!/usr/bin/env python3
"""E180 (the kit's dated note 1, KIT.md.dated-note-1.md section 5; the registration's dated note A1, rule A1-7): do the accumulating
sums walk? The disassembly walk of the box's own E180 kernel, for modes 261 (fadd.ps.acc) and 262 (fadd.pi.acc).

    /opt/et/bin/riscv64-unknown-elf-objdump -d build/enercat-e180/kernel/enercat.elf > build/e180-kernel-dis.txt
    python3 tools/claims-v3/e180/check_elf_e180.py build/e180-kernel-dis.txt [--also-160]

E61's (V3-DTF's) tools/claims-v3/dtf/check_elf.py (d0d68abb; it passed on all three boxes' builds on 21 Oct 2026, docs/reports/data/2026-10-21-dtf/
proof/) ported to the two modes E180 appends: its parse, its register names and its loop walk (the body found once, the loop's backward
branch within 30 instructions, no f-register instruction between the body and that branch or between the loop's head and the body),
unchanged; added for the accumulating modes, since their sums must persist across the loop:
  - the zeroing block (fxor.pi f8..f15, f0, f0) is found once before the loop's head and outside the loop;
  - between that block's end and the loop's head, no instruction writes f8-f15 (f-register destination);
  - inside the loop (head to branch), no call (jal with a link register, jalr other than a plain return) and no f-register instruction
    but the 64 body ops.
Each mode prints one line: PASS, FAIL (the body is found once and one of these fails: the sums would not walk as registered) or UNREAD
(the body or the zeroing block is not found exactly once: the disassembly cannot answer). The last line counts them. Exit 0 unless a mode
reads FAIL (exit 1); UNREAD exits 0, since A1-7 scores E180-A as registered then, labelled "walk not verified". With --also-160 the
registered plain mode 160 (fadd.ps, gen_ops.py's block, no zeroing block) is walked too, as a control of the parse on a real listing.
A trailing rounding-mode operand (rne, rtz, rdn, rup, rmm, dyn), if the objdump prints one, is ignored. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import re
import sys

ABI = {**{f"ft{i}": i for i in range(8)}, "fs0": 8, "fs1": 9, **{f"fa{i}": 10 + i for i in range(8)},
       **{f"fs{i}": 16 + i for i in range(2, 12)}, **{f"ft{i}": 20 + i for i in range(8, 12)}}
RM = {"rne", "rtz", "rdn", "rup", "rmm", "dyn"}
SUMS = set(range(8, 16))
MODES = {
    261: {"name": "fadd.ps.acc", "body": [f"fadd.ps f{8 + i}, f{8 + i}, f{i}" for i in range(8)],
          "zero": [f"fxor.pi f{8 + i}, f0, f0" for i in range(8)]},
    262: {"name": "fadd.pi.acc", "body": [f"fadd.pi f{8 + i}, f{8 + i}, f{i}" for i in range(8)],
          "zero": [f"fxor.pi f{8 + i}, f0, f0" for i in range(8)]},
}
M160 = {"name": "fadd.ps (mode 160, control)", "body": [f"fadd.ps f{8 + i}, f{i}, f{(i + 1) % 8}" for i in range(8)], "zero": None}


def freg(tok):
    tok = tok.strip()
    if re.fullmatch(r"f\d+", tok):
        return int(tok[1:])
    return ABI.get(tok)


def parse(path):
    out = []
    for line in open(path, errors="replace"):
        m = re.match(r"\s*([0-9a-f]+):\s+[0-9a-f]+\s+(\S+)\s*(.*)", line)
        if m:
            ops = [t.strip() for t in m.group(3).split("#")[0].split(",") if t.strip()]
            if ops and ops[-1] in RM:
                ops = ops[:-1]
            out.append((int(m.group(1), 16), m.group(2), ops))
    return out


def norm(op):
    mn, rest = op.split(None, 1)
    return mn, [freg(t) for t in rest.split(",")]


def is_f(ins):
    return any(freg(t) is not None for t in ins[2])


def f_dest(ins):
    return freg(ins[2][0]) if ins[2] else None


def is_call(ins):
    mn, ops = ins[1], ins[2]
    if mn in ("call", "tail", "jalr"):
        return not (mn == "jalr" and ops and ops[0] in ("zero", "x0"))
    if mn == "jal":
        return len(ops) >= 2 and ops[0] not in ("zero", "x0")
    return False


def find(ins, want):
    return [i for i in range(len(ins) - len(want) + 1)
            if all(ins[i + k][1] == want[k][0] and [freg(t) for t in ins[i + k][2]] == want[k][1] for k in range(len(want)))]


def walk(ins, mode, spec):
    body = [norm(o) for o in spec["body"]] * 8
    hits = find(ins, body)
    head = f"{spec['name']:28s} mode {mode}:"
    if len(hits) != 1:
        return "UNREAD", f"{head} RUN body of {len(body)} ops found {len(hits)} time(s)"
    i = hits[0]
    j = i + len(body)
    tail = ins[j:j + 30]
    br = next((k for k, t in enumerate(tail) if t[1].startswith("b") and t[2] and re.fullmatch(r"[0-9a-f]+", t[2][-1].split()[0])
               and int(t[2][-1].split()[0], 16) <= ins[i][0]), None)
    if br is None:
        return "UNREAD", f"{head} body found once; no backward branch to it within 30 instructions"
    target = int(tail[br][2][-1].split()[0], 16)
    loop = [t for t in ins[:j + br + 1] if t[0] >= target]
    why = []
    if any(is_f(t) for t in tail[:br]):
        why.append("an f-register instruction between the body and the loop's branch")
    if any(is_f(t) for t in ins[:i] if t[0] >= target):
        why.append("an f-register instruction between the loop's head and the body")
    if any(is_call(t) for t in loop):
        why.append("a call inside the loop")
    msg = f"{head} RUN body of {len(body)} ops found once, loop {target:x}-{tail[br][0]:x} ({len(loop)} instructions)"
    if spec["zero"]:
        zero = [norm(o) for o in spec["zero"]]
        zh = [k for k in find(ins, zero) if ins[k][0] < target and k > i - 400]
        if len(zh) != 1:
            return "UNREAD", f"{msg}; the zeroing block found {len(zh)} time(s) in the 400 instructions before the loop"
        z = zh[0]
        between = [t for t in ins[z + len(zero):] if t[0] < target]
        stray = [t for t in between if f_dest(t) in SUMS]
        if stray:
            why.append(f"{len(stray)} write(s) to f8-f15 between the zeroing block and the loop ({stray[0][1]} at {stray[0][0]:x})")
        if any(is_f(t) and f_dest(t) in SUMS for t in loop if not any(t is ins[i + k] for k in range(len(body)))):
            why.append("a write to f8-f15 inside the loop other than the body's")
        msg += f"; the zeroing block {ins[i][0] - ins[z][0]} bytes before the body, outside the loop, {len(between)} instructions between"
    if why:
        return "FAIL", f"{msg}; " + "; ".join(why)
    return "PASS", msg


def main(argv):
    if not argv:
        print("usage: check_elf_e180.py <objdump -d listing> [--also-160]")
        return 2
    ins = parse(argv[0])
    specs = [(261, MODES[261]), (262, MODES[262])] + ([(160, M160)] if "--also-160" in argv else [])
    res = []
    for mode, spec in specs:
        v, msg = walk(ins, mode, spec)
        res.append(v)
        print(f"{v} {msg}")
    print(f"ELFCHECK-E180: {res.count('PASS')} PASS, {res.count('FAIL')} FAIL, {res.count('UNREAD')} UNREAD "
          f"(of {len(res)}; {len(ins)} instructions parsed)")
    return 1 if "FAIL" in res else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
