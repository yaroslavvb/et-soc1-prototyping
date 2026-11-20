#!/usr/bin/env python3
"""layout2 x01 (exploration, post hoc): mesh distances of masks named in the leads (E216 Y, E218 Y). Desk; stdlib + numpy."""
import numpy as np
MARTY = {
    0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0),
    8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1), 10: (4, 1), 19: (5, 1),
    3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2),
    12: (1, 3), 21: (2, 3), 22: (3, 3), 26: (4, 3),
    20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4),
    28: (1, 5), 5: (2, 5), 6: (3, 5), 7: (4, 5), 31: (5, 5),
}
MEM = {m: (1 + (m % 4), -1 if m < 4 else 6) for m in range(8)}
def h(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
homes = [MARTY[s] for s in range(32)]
def per_shire(s):
    p = MARTY[s]
    return np.mean([h(p, q) for q in homes]), np.mean([h(p, MEM[m]) for m in range(8)])
full_home = np.mean([per_shire(s)[0] for s in range(32)])
full_mem = np.mean([per_shire(s)[1] for s in range(32)])
print('full chip mean hop to homes %.4f, to mem %.4f' % (full_home, full_mem))
for s in range(32):
    a, b = per_shire(s)
    print('shire %2d at %s: hop_home %.3f hop_mem %.3f  rg %d cg %d' % (s, MARTY[s], a, b, s >> 2, s & 3))
def feats(mask):
    sh = [s for s in range(32) if (mask >> s) & 1]
    H = [per_shire(s)[0] for s in sh]; M = [per_shire(s)[1] for s in sh]
    R = len({s >> 2 for s in sh}); C = len({s & 3 for s in sh})
    return dict(n=len(sh), R=R, C=C, hmean=np.mean(H), hmax=np.max(H), mmean=np.mean(M), mmax=np.max(M))
pairs = [('E216 y01-03', 0x3, 0x10001, '+0.072 +0.068 +0.040'), ('E216 y04', 0xf, 0x33, '-0.046'),
         ('E216 y05/06', 0x5555, 0x11111111, '+0.003 +0.004'), ('E216 y07/08 ctl', 0x101, 0x10001, '+0.036 +0.042'),
         ('E218 y01', 0xf000, 0x1010101, '-0.090'), ('E218 y02-06', 0xf, 0x3030, '+0.042 x4'),
         ('E218 y07/08 ctl', 0x55555555, 0xffff0000, '-0.021 -0.024')]
for name, a, b, meas in pairs:
    fa, fb = feats(a), feats(b)
    print('%-16s %-10s vs %-10s meas ln(a/b) %-20s | a: R%d C%d hmean %.3f hmax %.3f mmean %.3f mmax %.3f | b: R%d C%d hmean %.3f hmax %.3f mmean %.3f mmax %.3f' % (
        name, hex(a), hex(b), meas, fa['R'], fa['C'], fa['hmean'], fa['hmax'], fa['mmean'], fa['mmax'], fb['R'], fb['C'], fb['hmean'], fb['hmax'], fb['mmean'], fb['mmax']))
