#!/usr/bin/env python3
"""Check the built kernel: every timed loop is 131 instructions (128 body + addi, csrr, bltu), all 32-bit encodings,
the loop head 64-byte aligned; each loop's 128 body encodings equal, word for word, what make_images.py encodes for
one form; the loop's three tail words and the 29 words after the branch equal, word for word, make_images.py's frame
(the same in every loop: the loop's own registers fixed, then the padding instruction); every form appears exactly once.

    python3 check_elf.py build/kernel/regfile.elf [--objdump riscv64-unknown-elf-objdump]
Exit 0 when every check passes. Run it on the box's own build too: the box's toolchain may lay the code out
differently, and this check, not the ELF's hash, is what says that every loop is the registered one.
"""
import argparse
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_images as mi  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('elf')
    parser.add_argument('--objdump', default='/opt/et/bin/riscv64-unknown-elf-objdump')
    a = parser.parse_args()
    dis = subprocess.run([a.objdump, '-d', a.elf], capture_output=True, text=True, check=True).stdout
    ins = {}
    for line in dis.splitlines():
        m = re.match(r'\s+([0-9a-f]+):\s+([0-9a-f]+)\s+(\S+)\s*(.*)', line)
        if m:
            ins[int(m.group(1), 16)] = (m.group(2), m.group(3), m.group(4).replace(' ', ''))
    addrs = sorted(ins)
    want = {f: [mi.encode(x) for x in mi.body(f)] for f in mi.FORMS}
    frame = mi.tail_words()
    loops = []
    for ad in addrs:
        enc, mn, ops = ins[ad]
        if mn != 'bltu':
            continue
        tgt = int(ops.split(',')[-1].split('<')[0], 16)
        if tgt >= ad:
            continue
        loops.append((tgt, ad, [ins[x] for x in addrs if tgt <= x <= ad]))
    bad = 0
    seen = {}
    for tgt, br, body in loops:
        n = len(body)
        sizes = {len(e) for e, _, _ in body}
        words = [int(e, 16) for e, _, _ in body[:-3]] if sizes == {8} else []
        tail = [int(e, 16) for e, _, _ in body[-3:]] if sizes == {8} else []
        after = [int(ins[br + 4 * (k + 1)][0], 16) if (br + 4 * (k + 1)) in ins and len(ins[br + 4 * (k + 1)][0]) == 8
                 else None for k in range(mi.PAD)]
        form = [f for f, w in want.items() if w == words]
        frame_ok = tail == frame[:3] and after == frame[3:]
        ok = n == mi.BODY + 3 and sizes == {8} and tgt % 64 == 0 and len(form) == 1 and frame_ok
        name = form[0] if form else '?'
        seen[name] = seen.get(name, 0) + 1
        print('%s loop at 0x%x: %d instructions, encodings %s bytes, aligned64 %s, form %s, tail and %d words after '
              'the branch as registered %s' % ('OK ' if ok else 'BAD', tgt, n, sorted(s // 2 for s in sizes),
                                                tgt % 64 == 0, name, mi.PAD, frame_ok))
        bad += not ok
    for f in mi.FORMS:
        if seen.get(f, 0) != 1:
            print('BAD: form %s found %d times' % (f, seen.get(f, 0)))
            bad += 1
    print('loops %d (forms %d), frame %s, bad %d' % (len(loops), len(mi.FORMS), ' '.join('%08x' % w for w in frame[:3]),
                                                       bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
