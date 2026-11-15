"""E192 (reg-e192, Q176): the run order the proposal's run_block.py draws for each pass on a host named aifoundry3, written
out before any datum (run_block.py: arms = every non-anchor line of arms.txt, then random.Random("<hostname>|<pass>").shuffle).
A desk computation of code: Python's random.Random seeded with a str uses its SHA-512 (seeding version 2, Python 3.2 and later),
so the order depends only on the string and arms.txt's lines.

    /usr/bin/python3 -I -B order_e192.py <arms.txt> [hostname] [passes]
"""
import random
import sys

arms_txt = sys.argv[1]
host = sys.argv[2] if len(sys.argv) > 2 else 'aifoundry3'
passes = int(sys.argv[3]) if len(sys.argv) > 3 else 9
lines = [l.split() for l in open(arms_txt) if l.strip() and not l.startswith('#')]
anchor = [x[1] for x in lines if x[0] == 'anchor'][0]
base = [x[0] for x in lines if x[0] != 'anchor']
print('host %r; anchor %s; %d arms shuffled a pass (the anchor\'s arm among them: %s); %d runs a pass with the two burn-ins '
      'and the two anchors' % (host, anchor, len(base), anchor in base, len(base) + 4))
print('smoke block (pass -1): nop, add.a.f2, add.cr.l31 (run_block.py SMOKE_ARMS; 2 s each; no burn-in, no anchor)')
for p in range(passes):
    arms = list(base)
    random.Random('%s|%d' % (host, p)).shuffle(arms)
    seq = ['burnin:' + anchor, 'burnin:' + anchor, 'anchor_first:' + anchor] + arms + ['anchor_last:' + anchor]
    print('pass %d%s: %s' % (p, ' (the registered warm-up)' if p == 0 else '', ' '.join(seq)))
