#!/usr/bin/env python3
"""Prove the built DF kernel holds exactly the generated blocks (README "Proof before the first measured pass", step 3).

    objdump -d build/enercat-df/kernel/enercat.elf > dis.txt
    python3 tools/claims-v3/dtf/check_elf.py dis.txt workloads/enercat/enercat_df_modes.json

For every DF mode it finds the RUN loop - the block repeated eight times, nothing but the block's own vector ops in it -
and checks: the op sequence and registers, the eight repetitions (ops_per_iter = 8 x block), that no other f-register
instruction sits inside the loop, and for the addr modes that the f30/f31 prologue runs once BEFORE the loop and that
nothing writes f30 or f31 inside it. Exit 0 only if every mode passes.
"""
import json
import re
import sys

ABI = {**{f"ft{i}": i for i in range(8)}, "fs0": 8, "fs1": 9, **{f"fa{i}": 10 + i for i in range(8)},
       **{f"fs{i}": 16 + i for i in range(2, 12)}, **{f"ft{i}": 20 + i for i in range(8, 12)}}


def freg(tok):
    tok = tok.strip()
    if re.fullmatch(r"f\d+", tok):
        return int(tok[1:])
    return ABI.get(tok)


def parse(path):
    out = []
    for line in open(path):
        m = re.match(r"\s*([0-9a-f]+):\s+[0-9a-f]+\s+(\S+)\s*(.*)", line)
        if m:
            out.append((int(m.group(1), 16), m.group(2), [t.strip() for t in m.group(3).split("#")[0].split(",") if t.strip()]))
    return out


def norm(op):
    mn, rest = op.split(None, 1)
    return mn, [freg(t) for t in rest.split(",")]


def is_f(ins):
    return any(freg(t) is not None for t in ins[2])


def main():
    ins = parse(sys.argv[1])
    modes = json.load(open(sys.argv[2]))["modes"]
    bad = 0
    for m in modes:
        block = [norm(o) for o in m["ops"]]
        want = block * 8
        hits = []
        for i in range(len(ins) - len(want) + 1):
            if all(ins[i + k][1] == want[k][0] and [freg(t) for t in ins[i + k][2]] == want[k][1] for k in range(len(want))):
                hits.append(i)
        ok = len(hits) == 1
        msg = f"{m['name']:14s} mode {m['mode']}: RUN body of {len(want)} ops found {len(hits)} time(s)"
        if ok:
            i = hits[0]
            j = i + len(want)
            # the loop closes with ++iters, cycles() and a backward branch to the body start: no f-register op before it
            tail = ins[j:j + 30]
            br = next((k for k, t in enumerate(tail) if t[1].startswith("b") and t[2] and re.fullmatch(r"[0-9a-f]+", t[2][-1].split()[0])
                       and int(t[2][-1].split()[0], 16) <= ins[i][0]), None)
            if br is None:
                ok = False; msg += "; no backward branch to the body within 30 instructions"
            elif any(is_f(t) for t in tail[:br]):
                ok = False; msg += "; an f-register instruction between the body and the loop branch"
            target = int(tail[br][2][-1].split()[0], 16) if br is not None else None
            head = [t for t in ins[:i] if target is not None and t[0] >= target]
            if any(is_f(t) for t in head):
                ok = False; msg += "; an f-register instruction between the loop head and the body"
            if m["prologue"]:
                pro = [norm(o) for o in m["prologue"]]
                k0 = next((k for k in range(i - 1, max(0, i - 80), -1)
                           if all(ins[k + q][1] == pro[q][0] and [freg(t) for t in ins[k + q][2]] == pro[q][1] for q in range(len(pro)))), None)
                if k0 is None:
                    ok = False; msg += "; prologue not found before the loop"
                elif target is not None and ins[k0][0] >= target:
                    ok = False; msg += "; prologue INSIDE the loop"
                else:
                    msg += f"; prologue {len(ins[i][0:1]) and (ins[i][0] - ins[k0][0])} bytes before the body, outside the loop"
                inside = [t for t in ins[i:j] if t[2] and freg(t[2][0]) in (30, 31)]
                if inside:
                    ok = False; msg += "; f30/f31 written inside the loop"
            msg += f"; ops_per_iter {len(want)} (table says {m['ops_per_iter']})"
            if len(want) != m["ops_per_iter"]:
                ok = False
        print(("PASS " if ok else "FAIL ") + msg)
        bad += not ok
    print(f"{len(modes) - bad} of {len(modes)} DF modes pass")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
