#!/usr/bin/env python3
"""E211, Amendment A1, clause 3: dated correction 1 (records-e211a1, round Q216, Tue 17 Nov 2026). Post hoc and desk only.

The per-op instruction census of every inner TensorFMA loop of a kernel ELF, read from its disassembly (`objdump -d`), with an
optional counted simulator run's per-PC executions laid over it. Standard library only; reads its inputs, writes only --json.

Usage:
  python3 a1_census_e211.py --dis rgm136=rgm136.dis --dis rgm211=rgm211.dis \
      [--counted rgm136=counts-log.json] [--json census.json]
  where rgm136.dis and rgm211.dis are `riscv64-unknown-elf-objdump -d <ELF>` of the two kernels at E211's pins
  (tools/claims-v3/e211/kernel-e211.json), and counts-log.json is a record of tools/counter/count_kernel.py in log mode
  (schema ledger-counts/1) over a simulator run of the first kernel.

Method (no fitted constant and no branch-direction rule):
  1. An inner TensorFMA loop is a backward conditional branch whose address range [target, branch] holds exactly one
     `csrw tensor_fma`, two `csrw tensor_load` and one `csrw tensor_wait`; of several such branches to one target, the shortest;
     and of such ranges, only those that hold no other one.
  2. Its once-round paths are the simple paths of the control-flow graph restricted to that range, from the instruction after
     its `csrw tensor_wait` back to that write (an edge that leaves the range is cut). A path with no `csrw tensor_store` is a
     steady op (no finished C tile to store); a path with one is the op that also stores a tile.
  3. A path's census: its instructions; its stack loads (ld/lw/lwu/lh/lhu/lb/lbu/flw/fld off sp; and how many come before
     the first and the second tensor load); its stack stores (sd/sw/sh/sb/fsw/fsd off sp); its taken branches and jumps; its
     tensor CSR writes; the position (counted from the instruction after the wait) of the FMA, of the first and second tensor
     loads and of the next wait; and the source of x31 (t6), which holds each tensor load's and store's stride, at each of
     those writes: an `li` constant or a register.
  4. With --counted: every logged hart's instructions against its cycles_span (the simulator's steps), and hart 0's per-PC
     executions over each loop and over each path's PCs (min and max).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import re
import sys

RX = re.compile(r'^\s+([0-9a-f]+):\s+([0-9a-f]+)\s+(\S+)\s*(.*)$')
COND = {'beq', 'bne', 'blt', 'bge', 'bltu', 'bgeu', 'beqz', 'bnez', 'blez', 'bgez', 'bltz', 'bgtz', 'bgt', 'ble', 'bgtu', 'bleu'}
LOADS = {'ld', 'lw', 'lwu', 'lh', 'lhu', 'lb', 'lbu', 'flw', 'fld'}
STORES = {'sd', 'sw', 'sh', 'sb', 'fsw', 'fsd'}


def parse(path):
    """The .text instructions of an `objdump -d` listing: [(address, mnemonic, operands)] in address order."""
    ins, sec = [], None
    for ln in open(path, encoding='utf-8'):
        if ln.startswith('Disassembly of section '):
            sec = ln.split()[-1].rstrip(':')
            continue
        m = RX.match(ln.rstrip('\n'))
        if m and sec == '.text':
            ops = re.sub(r'<[^>]*>', '', m.group(4).split('#')[0]).strip()
            ins.append((int(m.group(1), 16), m.group(3), ops))
    ins.sort()
    return ins


def target(ops):
    return int(ops.split(',')[-1].strip().split()[0], 16)


def csr(mn, ops):
    return ops.split(',')[0].strip() if mn == 'csrw' else None


def inner_loops(ins):
    best = {}
    for a, mn, ops in ins:
        if mn not in COND:
            continue
        t = target(ops)
        if t >= a:
            continue
        body = [x for x in ins if t <= x[0] <= a]
        kinds = [csr(x[1], x[2]) for x in body]
        if kinds.count('tensor_fma') == 1 and kinds.count('tensor_load') == 2 and kinds.count('tensor_wait') == 1:
            if t not in best or a < best[t][1]:
                best[t] = (t, a)
    rng = sorted(best.values())
    # innermost only: drop a range that holds another one (an outer loop round the same FMA)
    return [r for r in rng if not any(o != r and r[0] <= o[0] and o[1] <= r[1] for o in rng)]


def paths(ins, lo, hi):
    """Every simple path once round the loop [lo, hi], from the instruction after its tensor_wait back to the wait."""
    body = [x for x in ins if lo <= x[0] <= hi]
    idx = {x[0]: i for i, x in enumerate(body)}
    nxt = {x[0]: (body[i + 1][0] if i + 1 < len(body) else None) for i, x in enumerate(body)}

    def succ(a, mn, ops):
        if mn in COND:
            s = [target(ops), nxt[a]]
        elif mn in ('j', 'jal') and (mn == 'j' or ops.startswith('zero')):
            s = [target(ops)]
        elif mn in ('jr', 'jalr', 'ret', 'mret', 'sret', 'ecall', 'ebreak'):
            s = []
        else:
            s = [nxt[a]]
        return [x for x in s if x is not None and lo <= x <= hi]

    wait = [x[0] for x in body if csr(x[1], x[2]) == 'tensor_wait'][0]
    out = []

    def dfs(a, seen, acc):
        if a == wait:
            out.append(acc + [a])
            return
        if a in seen:
            return
        x = body[idx[a]]
        for s in succ(*x):
            dfs(s, seen | {a}, acc + [a])

    for s in succ(*body[idx[wait]]):
        dfs(s, set(), [])
    return body, idx, out


def census(body, idx, path):
    seq = [body[idx[a]] for a in path]
    n = len(seq)
    kinds = [csr(mn, ops) for _, mn, ops in seq]
    pos = {'fma': None, 'load1': None, 'load2': None, 'wait': None}
    for i, k in enumerate(kinds, 1):
        if k == 'tensor_fma' and pos['fma'] is None:
            pos['fma'] = i
        elif k == 'tensor_load':
            pos['load1' if pos['load1'] is None else 'load2'] = i
        elif k == 'tensor_wait':
            pos['wait'] = i
    taken = 0
    for i, (a, mn, ops) in enumerate(seq):
        b = seq[(i + 1) % n][0]
        if mn == 'j' or (mn in COND and b == target(ops)):
            taken += 1
    strides = []
    for i, k in enumerate(kinds):
        if k in ('tensor_load', 'tensor_store'):
            src = None
            for j in range(1, n + 1):
                a, mn, ops = seq[(i - j) % n]
                rd = ops.split(',')[0].strip() if ops else ''
                if rd == 't6' and mn not in STORES and mn not in COND and mn != 'csrw':
                    src = f'{mn} {ops}'
                    break
            strides.append(f'{k}: x31 <- {src}')
    tensor = {}
    for k in kinds:
        if k and k.startswith('tensor'):
            tensor[k] = tensor.get(k, 0) + 1
    sl = [i for i, (_, mn, ops) in enumerate(seq, 1) if mn in LOADS and '(sp)' in ops]
    return {
        'instructions': n,
        'stack_loads': len(sl),
        'stack_loads_before_load1_load2': [sum(1 for i in sl if i < pos['load1']), sum(1 for i in sl if i < pos['load2'])],
        'stack_stores': sum(1 for _, mn, ops in seq if mn in STORES and '(sp)' in ops),
        'taken_branches_and_jumps': taken,
        'tensor_csr_writes': tensor,
        'positions_after_the_wait': pos,
        'stride_sources': strides,
        'store_path': 'tensor_store' in kinds,
        'pcs': [f'{a:#x}' for a in path],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--dis', action='append', required=True, help='NAME=objdump -d listing')
    ap.add_argument('--counted', action='append', default=[], help='NAME=count_kernel.py log-mode record')
    ap.add_argument('--json', help='write the census here')
    a = ap.parse_args()
    counted = {}
    for c in a.counted:
        k, p = c.split('=', 1)
        counted[k] = json.load(open(p, encoding='utf-8'))
    res = {}
    for d in a.dis:
        name, p = d.split('=', 1)
        ins = parse(p)
        rec = counted.get(name)
        pc = {}
        if rec:
            pc = {int(k, 16): v[0] for k, v in rec['harts']['0']['per_pc'].items()}
            hs = rec['harts']
            eq = sum(1 for h in hs.values() if h['instructions'] == h['cycles_span'])
            tot0 = sum(pc.values())
            print(f'{name} counted run ({rec.get("label")}, {rec.get("tool")}, mode {rec["inputs"]["mode"]}): {len(hs)} harts; '
                  f'instructions = cycles_span on {eq} of {len(hs)}; hart 0 {hs["0"]["instructions"]} instructions, cycles_span '
                  f'{hs["0"]["cycles_span"]}, per-PC executions summed {tot0}; '
                  f'tensor_fma writes on hart 0 {hs["0"]["by_csr"].get("csrw tensor_fma")}')
        print(f'{name}: {len(ins)} .text instructions; inner TensorFMA loops:')
        loops = []
        for lo, hi in inner_loops(ins):
            body, idx, ps = paths(ins, lo, hi)
            kinds = [csr(x[1], x[2]) for x in body]
            L = {'range': f'{lo:#x}-{hi:#x}', 'static_instructions': len(body),
                 'tensor_coop_writes': kinds.count('tensor_coop'), 'tensor_store_writes': kinds.count('tensor_store'),
                 'paths': []}
            if rec:
                L['counted_executions_hart0'] = sum(pc.get(x[0], 0) for x in body)
            line = (f'  loop {L["range"]}: {len(body)} static instructions, tensor_coop writes {L["tensor_coop_writes"]}, '
                    f'tensor_store writes {L["tensor_store_writes"]}')
            if rec:
                line += f'; counted executions over the range (hart 0) {L["counted_executions_hart0"]}'
            print(line)
            for p in sorted(ps, key=len):
                c = census(body, idx, p)
                if rec:
                    ex = [pc.get(int(x, 16), 0) for x in c['pcs']]
                    c['counted_executions_hart0_min_max'] = [min(ex), max(ex)]
                pp = c['positions_after_the_wait']
                bl = c['stack_loads_before_load1_load2']
                print(f'    path ({"stores a tile" if c["store_path"] else "steady op"}): {c["instructions"]} instructions, '
                      f'stack loads {c["stack_loads"]} ({bl[0]} before the first tensor load, {bl[1]} before the second), '
                      f'stack stores {c["stack_stores"]}, taken branches and jumps '
                      f'{c["taken_branches_and_jumps"]}, tensor writes {c["tensor_csr_writes"]}; after the wait: FMA {pp["fma"]}, '
                      f'loads {pp["load1"]} and {pp["load2"]}, wait {pp["wait"]}'
                      + (f'; counted executions of its PCs (hart 0) min {c["counted_executions_hart0_min_max"][0]}, '
                         f'max {c["counted_executions_hart0_min_max"][1]}' if rec else ''))
                print(f'      strides: {"; ".join(c["stride_sources"])}')
                L['paths'].append(c)
            loops.append(L)
        res[name] = loops
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(res, f, indent=1, sort_keys=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
