"""reg-e192 (Q176): this lane's own desk check of the built kernel's 16 timed loops, from an objdump listing.

For every backward bltu (a loop), the instructions from its target to it, in order: 259 of them; the last three addi, csrr
(hpmcounter3), bltu; and the 256-instruction body exactly one of the designed forms of request.md section 2 and intbits.c:
  nop   : 'nop' x 256
  same  : 'OP x5,x6,x7' x 256 (actually t0,t1,t2 in objdump's ABI names)
  pair  : ('OP x5,x6,x7', 'OP x5,x28,x29') x 128      (t0,t1,t2 / t0,t3,t4)
  split : ('OP x5,x6,x7', 'OP x30,x28,x29') x 128     (t0,t1,t2 / t5,t3,t4)
for OP in add, xor, sub, and, or; every encoding 4 bytes; every loop head 64-byte aligned. Prints one line per loop and a
summary; exit 0 when the 16 expected (form, op) loops are each present exactly once and every check passes.
    /usr/bin/python3 -I -B loop_order_e192.py intbits.dis.txt
"""
import re
import sys

ins = {}
for line in open(sys.argv[1]):
    m = re.match(r'\s+([0-9a-f]+):\s+([0-9a-f]+)\s+(\S+)\s*(.*)', line)
    if m:
        ins[int(m.group(1), 16)] = (m.group(2), m.group(3), m.group(4).replace(' ', '').split('#')[0].split('<')[0])
addrs = sorted(ins)
A, B, B2 = 't0,t1,t2', 't0,t3,t4', 't5,t3,t4'
want = {('nop', 'nop')} | {(f, op) for f in ('same', 'pair', 'split') for op in ('add', 'xor', 'sub', 'and', 'or')}
seen = {}
bad = 0
for ad in addrs:
    enc, mn, ops = ins[ad]
    if mn != 'bltu':
        continue
    tgt = int(ops.split(',')[-1], 16)
    if tgt >= ad:
        continue
    body = [ins[x] for x in addrs if tgt <= x <= ad]
    n = len(body)
    tail = body[-3:]
    core = body[:-3]
    ok = n == 259 and all(len(e) == 8 for e, _, _ in body) and tgt % 64 == 0
    ok = ok and tail[0][1] == 'addi' and tail[1][1] == 'csrr' and 'hpmcounter3' in tail[1][2] and tail[2][1] == 'bltu'
    form = op = '?'
    mns = {m for _, m, _ in core}
    if mns == {'nop'} and len(core) == 256:
        form, op = 'nop', 'nop'
    elif len(mns) == 1 and len(core) == 256:
        op = mns.pop()
        seq = [o for _, _, o in core]
        if all(o == A for o in seq):
            form = 'same'
        elif all(o == (A if i % 2 == 0 else B) for i, o in enumerate(seq)):
            form = 'pair'
        elif all(o == (A if i % 2 == 0 else B2) for i, o in enumerate(seq)):
            form = 'split'
    ok = ok and form != '?'
    seen[(form, op)] = seen.get((form, op), 0) + 1
    bad += not ok
    print('%s loop at 0x%x: %d instructions, form %s, op %s, head mod 64 = %d' % ('OK ' if ok else 'BAD', tgt, n, form, op, tgt % 64))
missing = sorted(want - set(seen))
dups = sorted(k for k, v in seen.items() if v > 1)
extra = sorted(set(seen) - want)
print('loops %d; forms x ops found %d of %d; missing %s; duplicated %s; unexpected %s; bad %d' % (
    sum(seen.values()), len(set(seen) & want), len(want), missing or 'none', dups or 'none', extra or 'none', bad))
sys.exit(0 if (not bad and not missing and not dups and not extra) else 1)
