"""reg-e192 (Q176): the built host's arm table (`intbits_host --list --json`, run inside the no-device sandbox) against
request.md revision 1's table, cell by cell; against arms.txt and the reducer's control map; and the host's source values
against an independent re-derivation (this file's own mt19937_64, seed 1, and request.md section 2's construction), with
the design claims of section 2 checked on the values. A desk check of code: nothing is measured.

    /usr/bin/python3 -I -B compare_arms_e192.py <request.md> <list.jsonl> <arms.txt> <reduce_intbits.py>
Exit 0 when every comparison and claim holds.
"""
import importlib.util
import json
import re
import sys

req, lst, armsf, redf = sys.argv[1:5]
M64 = (1 << 64) - 1
bad = 0


def say(ok, msg):
    global bad
    bad += not ok
    print(('OK   ' if ok else 'FAIL ') + msg)


# 1. request.md's table (section 2)
rows = {}
order_req = []
for ln in open(req, encoding='utf-8'):
    m = re.match(r'^\| `([a-z0-9.]+)` \| (\w+) (\w+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (`[a-z0-9.]+`|-) \| (.*) \|$', ln.rstrip('\n'))
    if m:
        a = m.group(1)
        rows[a] = dict(form=m.group(2), op=m.group(3), pa=int(m.group(4)), pb=int(m.group(5)), res=int(m.group(6)),
                       carry=int(m.group(7)), enc=int(m.group(8)), control=m.group(9).strip('`'), role=m.group(10))
        order_req.append(a)
print('request.md table rows parsed: %d' % len(rows))

# 2. the host's list
host = [json.loads(l) for l in open(lst) if l.startswith('{')]
H = {h['arm']: h for h in host}
print('host --list --json arms: %d' % len(H))
say(order_req == [h['arm'] for h in host], 'the same 32 arms in the same order (request.md table vs host list)')

cells = 0
for a in order_req:
    r, h = rows[a], H.get(a)
    if h is None:
        say(False, '%s: not in the host list' % a)
        continue
    form_op = (h['form'], h['op'])
    pairs = [('form', r['form'], h['form']), ('op', r['op'], h['op']), ('port A', r['pa'], h['n_port_a']),
             ('port B', r['pb'], h['n_port_b']), ('result', r['res'], h['n_result']), ('carry', r['carry'], h['n_carry']),
             ('enc', r['enc'], h['n_enc'])]
    diffs = [(k, x, y) for k, x, y in pairs if x != y]
    cells += len(pairs)
    say(not diffs, '%-12s %s %s  A %2d B %2d R %2d C %2d enc %d%s' % (
        a, h['form'], h['op'], h['n_port_a'], h['n_port_b'], h['n_result'], h['n_carry'], h['n_enc'],
        '' if not diffs else '  DIFF ' + str(diffs)))
print('cells compared: %d (7 a row: form, op, port A, port B, result, carry, enc)' % cells)

# 3. arms.txt and the reducer's control map
lines = [l.split() for l in open(armsf) if l.strip() and not l.startswith('#')]
anchor = [x[1] for x in lines if x[0] == 'anchor']
arms = [x[0] for x in lines if x[0] != 'anchor']
say(anchor == ['add.a.f2'], 'arms.txt anchor is add.a.f2 (%s)' % anchor)
say(sorted(arms) == sorted(order_req) and len(arms) == 32, 'arms.txt lists the 32 arms of the table (%d)' % len(arms))
spec = importlib.util.spec_from_file_location('reduce_intbits_copy', redf)
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
ctl_bad = [(a, rows[a]['control'], R.control_of(a) or '-') for a in order_req if (R.control_of(a) or '-') != rows[a]['control']]
say(not ctl_bad, 'the reducer control_of() equals request.md control column for all 32 arms%s' % (
    '' if not ctl_bad else ': ' + str(ctl_bad)))


# 4. an independent mt19937_64 and the construction of section 2
class MT64:
    def __init__(self, seed):
        self.mt = [0] * 312
        self.mt[0] = seed & M64
        for i in range(1, 312):
            self.mt[i] = (6364136223846793005 * (self.mt[i - 1] ^ (self.mt[i - 1] >> 62)) + i) & M64
        self.i = 312

    def __call__(self):
        if self.i >= 312:
            for k in range(312):
                y = (self.mt[k] & 0xFFFFFFFF80000000) | (self.mt[(k + 1) % 312] & 0x7FFFFFFF)
                v = self.mt[(k + 156) % 312] ^ (y >> 1)
                if y & 1:
                    v ^= 0xB5026F5AA96619E9
                self.mt[k] = v
            self.i = 0
        x = self.mt[self.i]
        self.i += 1
        x ^= (x >> 29) & 0x5555555555555555
        x ^= (x << 17) & 0x71D67FFFEDA60000
        x ^= (x << 37) & 0xFFF7EEE000000000
        x ^= x >> 43
        return x & M64


g = MT64(5489)
outs = [g() for _ in range(10000)]
say(outs[-1] == 9981545732273789042,
    'this mt19937_64 gives the C++ standard\'s 10000th output for the default seed 5489 (9981545732273789042)')
g = MT64(1)
X = g()
Y = g() & ~X & M64


def field(f):
    return (0xFFFF << (16 * f)) & M64


exp = {}
exp['nop'] = (0, 0, 0, 0)
exp['add.same'] = (X, Y, X, Y)
for n in ('add.z', 'xor.z', 'and.z'):
    exp[n] = (X, Y, X, Y)


def shapeA(n, Msk):
    a, b = X & ~Msk & M64, Y & ~Msk & M64
    exp[n] = (a, b, a | Msk, b)


def shapeB(n, Msk):
    a, b = X & ~Msk & M64, Y & ~Msk & M64
    exp[n] = (a, b, a, b | Msk)


def shapeS(n, Msk):
    a, b = X & ~Msk & M64, Y & ~Msk & M64
    exp[n] = (a | Msk, b, a, b | Msk)


for f in range(4):
    shapeA('add.a.f%d' % f, field(f))
shapeA('add.a.f2.k4', 0xF << 32)
shapeA('add.a.f2.k8', 0xFF << 32)
shapeA('add.a.f12', field(1) | field(2))
shapeA('add.a.all', M64)
shapeB('add.b.f0', field(0))
shapeB('add.b.f2', field(2))
shapeS('add.s.f0', field(0))
shapeS('add.s.f2', field(2))
shapeA('xor.a.f2', field(2))
for f in (1, 2, 3):
    shapeA('and.a.f%d' % f, field(f))
for L in (0, 8, 16, 24, 31):
    span = ((1 << (L + 1)) - 1) << 16
    a, b = X & ~span & M64, Y & ~span & M64
    run = ((1 << L) - 1) << 16 if L else 0
    exp['add.cr.l%d' % L] = (a | run, b | (1 << 16), a | (1 << (16 + L)), b)
    exp['add.crb.l%d' % L] = (a | run, b, a | run, b | (1 << 16))
exp['add.ripple'] = (M64, 0, M64, 1)
vals_bad = [a for a in order_req if tuple(int(H[a][k], 16) for k in ('a0', 'b0', 'a1', 'b1')) != exp.get(a)]
say(not vals_bad and len(exp) == 32, 'every arm\'s four source values re-derived independently (mt19937_64 seed 1; section 2): %d of 32 equal%s' % (
    32 - len(vals_bad), '' if not vals_bad else ' DIFF ' + str(vals_bad)))
print('background (seed 1): X = 0x%016x, Y = 0x%016x (Y = second draw & ~X), popcount X %d, Y %d' % (X, Y, bin(X).count('1'), bin(Y).count('1')))

# 5. section 2's design claims, on the host's values
OPS = {'add': lambda a, b: (a + b) & M64, 'xor': lambda a, b: a ^ b, 'and': lambda a, b: a & b, 'nop': lambda a, b: 0}
pc = lambda x: bin(x).count('1')
carry_arms = {a for a in order_req if a.startswith('add.cr') or a == 'add.ripple'}
for a in order_req:
    h = H[a]
    a0, b0, a1, b1 = (int(h[k], 16) for k in ('a0', 'b0', 'a1', 'b1'))
    op = h['op']
    r0, r1 = OPS[op](a0, b0), OPS[op](a1, b1)
    if h['form'] == 'same':
        a1, b1, r1 = a0, b0, r0
    ok = (r0, r1) == (int(h['r0'], 16), int(h['r1'], 16))
    cv = lambda x, y: ((x + y) & M64) ^ x ^ y
    if h['form'] != 'nop':
        ok = ok and pc(a0 ^ a1) == h['n_port_a'] and pc(b0 ^ b1) == h['n_port_b'] and pc(r0 ^ r1) == h['n_result']
        ok = ok and (h['n_carry'] == (pc(cv(a0, b0) ^ cv(a1, b1)) if op == 'add' else 0))
    if a not in carry_arms and h['form'] != 'nop':
        ok = ok and (a0 & b0) == 0 and (a1 & b1) == 0          # disjoint ones: no carries; add == xor == or; and == 0
    if a.startswith('add.cr.') or a.startswith('add.crb.'):
        ok = ok and ((a0 ^ a1) | (b0 ^ b1) | (r0 ^ r1)) & ~0x0000FFFFFFFF0000 == 0   # inside bits 16-47
    if a.startswith('add.cr.'):
        ok = ok and r0 == r1
    if a.startswith('add.crb.'):
        ok = ok and a0 == a1
    if not ok:
        say(False, 'design claim fails for %s' % a)
say(True, 'design claims checked on all 32 arms: r0/r1 and the four counts recomputed from the values; outside the carry arms the two '
          'sources\' ones are disjoint in both instructions (so add = xor and the and is 0); carry arms move only bits 16-47; '
          'cr arms hold the result, crb arms hold port A')
k4 = int(H['add.a.f2.k4']['a0'], 16) ^ int(H['add.a.f2.k4']['a1'], 16)
k8 = int(H['add.a.f2.k8']['a0'], 16) ^ int(H['add.a.f2.k8']['a1'], 16)
f12 = int(H['add.a.f12']['a0'], 16) ^ int(H['add.a.f12']['a1'], 16)
say(k4 == 0xF << 32 and k8 == 0xFF << 32 and f12 == 0xFFFFFFFF << 16,
    'add.a.f2.k4 flips bits 32-35, .k8 bits 32-39, add.a.f12 bits 16-47 (section 2)')
print('RESULT: %s (%d failing checks)' % ('ALL HOLD' if bad == 0 else 'FAILURES', bad))
sys.exit(1 if bad else 0)
