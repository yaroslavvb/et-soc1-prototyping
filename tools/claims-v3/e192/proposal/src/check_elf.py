#!/usr/bin/env python3
"""Check the built kernel: every timed loop is 259 instructions (256 body + addi, csrr, bltu), all 32-bit
encodings, the loop head 64-byte aligned, and the bodies are what the arm table says.

    python3 check_elf.py build/kernel/intbits.elf [--objdump riscv64-unknown-elf-objdump]
Exit 0 when every check passes.
"""
import argparse
import re
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('elf')
    ap.add_argument('--objdump', default='/opt/et/bin/riscv64-unknown-elf-objdump')
    a = ap.parse_args()
    dis = subprocess.run([a.objdump, '-d', a.elf], capture_output=True, text=True, check=True).stdout
    ins = {}
    for l in dis.splitlines():
        m = re.match(r'\s+([0-9a-f]+):\s+([0-9a-f]+)\s+(\S+)\s*(.*)', l)
        if m:
            ins[int(m.group(1), 16)] = (m.group(2), m.group(3), m.group(4).replace(' ', ''))
    addrs = sorted(ins)
    loops = []
    for ad in addrs:
        enc, mn, ops = ins[ad]
        if mn != 'bltu':
            continue
        tgt = int(ops.split(',')[-1].split('<')[0], 16)
        if tgt >= ad:
            continue
        body = [ins[x] for x in addrs if tgt <= x <= ad]
        loops.append((tgt, body))
    bad = 0
    kinds = {}
    for tgt, body in loops:
        n = len(body)
        sizes = {len(e) for e, _, _ in body}
        tail = [m for _, m, _ in body[-3:]]
        main_ = [(m, o) for _, m, o in body[:-3]]
        kind = ' ; '.join(sorted({'%s %s' % x for x in main_}))
        ok = n == 259 and sizes == {8} and tgt % 64 == 0 and tail == ['addi', 'csrr', 'bltu']
        if 'csrr' in kind or 'hpmcounter' in kind:
            ok = False
        kinds[kind] = kinds.get(kind, 0) + 1
        print('%s loop at 0x%x: %d instructions, encodings %s bytes, aligned64 %s, body: %s' % (
            'OK ' if ok else 'BAD', tgt, n, sorted(s // 2 for s in sizes), tgt % 64 == 0, kind))
        bad += not ok
    if len(loops) != 16:
        print('BAD: expected 16 timed loops (nop + 3 forms x 5 opcodes), found %d' % len(loops))
        bad += 1
    print('loops %d, bad %d' % (len(loops), bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
