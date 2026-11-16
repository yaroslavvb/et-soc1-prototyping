#!/usr/bin/env python3
"""E197 registration desk check (reg-e197, Q185): the trains, kinds and plan, cell by cell, in request.md, trains.tsv, the built
host's kind table (`regfile_host --list --json`), the reducer's derived prices, and the reference session's dry listings.

    python3 -I -B compare_trains_e197.py REQUEST.md HOST-LIST.jsonl TRAINS.tsv REDUCE_REGFILE.py DRY_FULL DRY_SHORT DRY_EXT

Reads files only; imports nothing from the proposal (the reducer's DERIVED table is read with ast). Prints every comparison and
ends with "TRAINS CHECK PASS" or "TRAINS CHECK FAIL (n)". A desk check of code: nothing measured, no device.

1. request.md section 2's train table against trains.tsv: train, F, S, processes (first sitting; the second sitting's T1 and its
   T7, T14), and each row's block and short flag against section 2's "Blocks" paragraph.
2. Each train's designed changes, F - S per instruction, from the host's own table, against request.md's "changes" cell: every
   count the cell names equals F - S; every count it does not name is 0, except the encoding count `enc`, which is reported
   beside (it follows from the field counts i1, i2, iw: a changed field is changed encoding bits) and must equal their sum.
3. The host's table holds the 34 kinds of request.md section 6's emulator table, and every kind a train names.
4. The reducer's DERIVED table against request.md section 4's derived prices (name, trains, coefficients, divisor) and its
   BOUNDED list against section 4's five zero-by-design prices.
5. The dry listings (DRY=1 run_session.sh OUT full|short|ext): the smoke (5 s idle; the three anchors as 1 s bursts after 4.5 s
   idles; two T8 processes, SFFS then FSSF); then per block of the plan: 10 s idle, the anchors as 3 s bursts, the block's trains
   in trains.tsv order with their process counts, orientations alternating from the train's first, every process 13 launches of
   240,000,000 cycles with the stop file, the anchors in reverse, 10 s idle; the device-call counts 429, 331 and 277 (request.md
   section 8); every device call under one timeout form.
"""
import ast
import json
import re
import sys

KEYS = ['f1', 'f2', 'a1', 'a2', 'res', 'cell', 'i1', 'i2', 'iw', 'enc', 'h1', 'h2', 'writes']
bad = 0


def fail(msg):
    global bad
    bad += 1
    print('FAIL: ' + msg)


def table_rows(text, header_start):
    """rows (lists of cells) of the first markdown table whose header line starts with header_start"""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith(header_start):
            out = []
            for row in lines[i + 2:]:
                if not row.startswith('|'):
                    break
                out.append([c.strip() for c in row.strip().strip('|').split('|')])
            return out
    return []


def bare(c):
    return c.replace('`', '').strip()


def main():
    req, hostj, tsv, red, dry_full, dry_short, dry_ext = sys.argv[1:8]
    text = open(req, encoding='utf-8').read()
    # ---------------------------------------------------------------- 1. request.md's train table against trains.tsv
    rows = table_rows(text, '| train | F | S | processes |')
    print('1. request.md section 2 train table: %d rows' % len(rows))
    reqt = {}
    for r in rows:
        tr, F, S, n, changes, role = r[0], bare(r[1]), bare(r[2]), r[3], r[4], r[5]
        m = re.match(r'(\d+)(?: \(\+(\d+) in the second sitting\))?(, second sitting)?$', n)
        if not m:
            fail('processes cell not understood: %r' % n)
            continue
        reqt[tr] = {'F': F, 'S': S, 'n_first': 0 if m.group(3) else int(m.group(1)),
                    'n_second': int(m.group(2)) if m.group(2) else (int(m.group(1)) if m.group(3) else 0),
                    'changes': changes, 'role': role}
    plan = []
    for ln in open(tsv, encoding='utf-8'):
        if ln.strip() and not ln.startswith('#'):
            b, tr, F, S, n, first, short, role = ln.rstrip('\n').split('\t')
            plan.append({'block': b, 'train': tr, 'F': F, 'S': S, 'n': int(n), 'first': first, 'short': short == '1'})
    print('   trains.tsv: %d rows' % len(plan))
    cells = ok = 0
    for tr, q in reqt.items():
        p1 = [p for p in plan if p['train'] == tr and p['block'] != 'E']
        p2 = [p for p in plan if p['train'] == tr and p['block'] == 'E']
        n_first = sum(p['n'] for p in p1)
        n_second = sum(p['n'] for p in p2)
        pf = (p1 or p2)[0] if (p1 or p2) else None
        for what, a, b in (('F', q['F'], pf and pf['F']), ('S', q['S'], pf and pf['S']), ('first-sitting processes', q['n_first'], n_first),
                           ('second-sitting processes', q['n_second'], n_second)):
            cells += 1
            if a == b:
                ok += 1
            else:
                fail('%s %s: request.md %r, trains.tsv %r' % (tr, what, a, b))
        print('   %-4s F %-9s S %-9s processes %3d + %3d (second sitting)  block(s) %s  first %s  short %s' % (
            tr, q['F'], q['S'], n_first, n_second, ','.join(p['block'] for p in p1 + p2), ','.join(p['first'] for p in p1 + p2),
            ','.join('1' if p['short'] else '0' for p in p1 + p2)))
    blocks_req = {'A': ['T2', 'T1'], 'B': ['T3', 'T5', 'T6', 'T4'], 'C': ['T8', 'T10', 'T9', 'T11'], 'D': ['T13', 'T12', 'T15'],
                  'E': ['T1', 'T7', 'T14']}   # request.md section 2, "Blocks" (E: "230 more processes of T1, then T7 and T14")
    short_req = {'T1', 'T2', 'T3', 'T5', 'T8', 'T10', 'T12', 'T13'}   # "The short plan ... keeps T1, T2, T3, T5, T8, T10, T12, T13"
    for b, trs in blocks_req.items():
        cells += 1
        got = [p['train'] for p in plan if p['block'] == b]
        if got == trs:
            ok += 1
        else:
            fail('block %s: request.md %s, trains.tsv %s' % (b, trs, got))
    for p in plan:
        if p['block'] == 'E':
            continue
        cells += 1
        if p['short'] == (p['train'] in short_req):
            ok += 1
        else:
            fail('%s short flag %s against request.md\'s short plan' % (p['train'], p['short']))
    print('   blocks and order (A, B, C, D; E), short flags: checked; request.md against trains.tsv: %d of %d cells equal' % (ok, cells))
    # ---------------------------------------------------------------- 2. designed changes F - S from the host's own table
    kinds = {}
    for ln in open(hostj, encoding='utf-8'):
        if ln.strip():
            d = json.loads(ln)
            kinds[d['kind']] = d['per_instr']
    print('2. the host\'s kind table: %d kinds' % len(kinds))
    c_ok = c_n = 0
    for tr, q in reqt.items():
        F, S = kinds.get(q['F']), kinds.get(q['S'])
        if F is None or S is None:
            fail('%s: a kind is not in the host table' % tr)
            continue
        diff = {k: round(F[k] - S[k], 6) for k in KEYS}
        ch = q['changes']
        named = {m.group(1): float(m.group(2)) for m in re.finditer(r'\b(f1|f2|a1|a2|res|cell|i1|i2|iw|h1|h2)\s+([+-]?\d+)', ch)}
        if ch.startswith('one write'):
            named = {'writes': 1.0}
        elif ch.startswith('none') or ch.startswith('0 '):
            named = {}
        good = True
        for k, v in named.items():
            if abs(diff[k] - v) > 1e-9:
                good = False
                fail('%s: request.md names %s %+g, the host table gives %+g' % (tr, k, v, diff[k]))
        fields = diff['i1'] + diff['i2'] + diff['iw']
        for k in KEYS:
            if k in named:
                continue
            if k == 'enc':
                if abs(diff['enc'] - fields) > 1e-9:
                    good = False
                    fail('%s: enc %+g is not the sum of the field counts %+g' % (tr, diff['enc'], fields))
                continue
            if abs(diff[k]) > 1e-9:
                good = False
                fail('%s: %s differs by %+g, which request.md\'s cell does not name' % (tr, k, diff[k]))
        c_n += 1
        c_ok += good
        nz = ', '.join('%s %+g' % (k, diff[k]) for k in KEYS if abs(diff[k]) > 1e-9) or 'none'
        print('   %-4s %-9s - %-9s F - S: %-34s request.md: %s  %s' % (tr, q['F'], q['S'], nz, ch, 'EQUAL' if good else 'DIFFERS'))
    print('   designed changes: %d of %d trains as request.md says (enc reported beside: it equals the field counts\' sum)' % (c_ok, c_n))
    # ---------------------------------------------------------------- 3. the kinds
    emu = table_rows(text, '| kind | iterations | body |')
    emu_kinds = set()
    for r in emu:
        emu_kinds.add(bare(r[0]))
        if len(r) > 6:
            emu_kinds.add(bare(r[6]))
    print('3. request.md section 6 lists %d kinds; the host table %d; the same set: %s' % (
        len(emu_kinds), len(kinds), emu_kinds == set(kinds)))
    if emu_kinds != set(kinds):
        fail('kind sets differ: only in request.md %s, only in the host %s' % (sorted(emu_kinds - set(kinds)), sorted(set(kinds) - emu_kinds)))
    used = {p['F'] for p in plan} | {p['S'] for p in plan} | {'nop.z', 'res.k0', 'res.k64'}
    print('   kinds the plan and the anchors use: %d, all in the host table: %s' % (len(used), used <= set(kinds)))
    if not used <= set(kinds):
        fail('kinds not in the host table: %s' % sorted(used - set(kinds)))
    # ---------------------------------------------------------------- 4. the reducer's derived prices
    tree = ast.parse(open(red, encoding='utf-8').read())
    derived = bounded = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id == 'DERIVED':
                derived = ast.literal_eval(node.value)
            if node.targets[0].id == 'BOUNDED':
                bounded = ast.literal_eval(node.value)
    m = re.search(r'- Derived prices \(each a combination of independent trains\): (.*?)\n- \*\*Verdicts', text, re.S)
    req_d = {}
    for item in re.finditer(r'`([a-z0-9_]+)`\s*=\s*([^;`]*)', m.group(1).replace('\n', ' ')):
        req_d[item.group(1)] = item.group(2).strip().rstrip('.,').strip()

    def parse(expr):
        e = expr.replace(' ', '')
        mp = re.match(r'^\((.*)\)/(\d+)$', e)
        m1 = re.match(r'^(T\d+)/(\d+)$', e)
        if mp:
            body, div = mp.group(1), int(mp.group(2))
        elif m1:
            body, div = m1.group(1), int(m1.group(2))
        else:
            body, div = e, 1
        terms = []
        for sgn, tr, frac in re.findall(r'([+-]?)(T\d+)(?:/(\d+))?', body):
            c = (-1.0 if sgn == '-' else 1.0) / (float(frac) if frac else 1.0)
            terms.append((tr, c))
        return sorted(terms), div
    d_ok = 0
    for name, expr in req_d.items():
        if name not in derived:
            fail('derived %s (request.md) not in the reducer' % name)
            continue
        terms, div = parse(expr)
        rt, rk, _ = derived[name]
        same = sorted((t, float(c)) for t, c in rt) == terms and rk == div
        d_ok += same
        if not same:
            fail('derived %s: request.md %s -> %s / %d; reducer %s / %d' % (name, expr, terms, div, rt, rk))
    print('4. derived prices: request.md %d, the reducer %d; equal %d of %d; only in the reducer: %s' % (
        len(req_d), len(derived), d_ok, len(req_d), sorted(set(derived) - set(req_d)) or 'none'))
    req_b = ('order', 'lin_result', 'lin_field', 'dest_n8', 'read_n8')   # request.md section 4, "Verdicts"
    print('   BOUNDED prices: reducer %s; request.md %s; equal %s' % (bounded, req_b, tuple(bounded) == req_b))
    if tuple(bounded) != req_b:
        fail('BOUNDED list differs')
    # ---------------------------------------------------------------- 5. the dry listings
    want_calls = {'full': 429, 'short': 331, 'ext': 277}
    for pl, path in (('full', dry_full), ('short', dry_short), ('ext', dry_ext)):
        lines = [ln.rstrip('\n') for ln in open(path, encoding='utf-8')]
        calls = [ln for ln in lines if ln.startswith('DRY: timeout')]
        forms = sorted({re.match(r'DRY: (timeout( -k \d+)? \d+) ', ln).group(1) for ln in calls})
        exp = []   # the expected sequence of events: ('idle', secs, label) or ('kind', name, secs) or ('train', F, S, orient)
        exp += [('idle', '5', 'before')]
        for k in ('nop.z', 'res.k0', 'res.k64'):
            exp += [('idle', '4.5', 'before ' + k), ('kind', k, '1')]
        t8 = [p for p in plan if p['train'] == 'T8'][0]
        oth = {'SFFS': 'FSSF', 'FSSF': 'SFFS'}
        exp += [('train', t8['F'], t8['S'], t8['first']), ('train', t8['F'], t8['S'], oth[t8['first']])]
        blocks = ['E'] if pl == 'ext' else ['A', 'B', 'C', 'D']
        for b in blocks:
            exp += [('idle', '10', 'before')]
            for k in ('nop.z', 'res.k0', 'res.k64'):
                exp += [('idle', '4.5', 'before ' + k), ('kind', k, '3')]
            for p in plan:
                if p['block'] != b or (pl == 'short' and not p['short']):
                    continue
                o = p['first']
                for j in range(p['n']):
                    exp += [('train', p['F'], p['S'], o)]
                    o = oth[o]
            for k in ('res.k64', 'res.k0', 'nop.z'):
                exp += [('idle', '4.5', 'before ' + k), ('kind', k, '3')]
            exp += [('idle', '10', 'after')]
        got = []
        badline = 0
        for ln in lines:
            mi = re.match(r'DRY: idle (\S+) s \((.*)\)$', ln)
            mk = re.match(r'DRY: timeout( -k \d+)? \d+ (\S+) --kind (\S+) --seconds (\S+) --window 240000000 --stop-file (\S+)$', ln)
            mt = re.match(r'DRY: timeout( -k \d+)? \d+ (\S+) --train ([^,]+),(\S+) --orient (SFFS|FSSF) --launches 13 '
                          r'--window 240000000 --stop-file (\S+)$', ln)
            if mi:
                got.append(('idle', mi.group(1), mi.group(2)))
            elif mk:
                got.append(('kind', mk.group(3), mk.group(4)))
                badline += not mk.group(5).endswith('/STOP')
            elif mt:
                got.append(('train', mt.group(3), mt.group(4), mt.group(5)))
                badline += not mt.group(6).endswith('/STOP')
            elif ln.startswith('DRY: timeout'):
                badline += 1
        same = got == exp
        print('5. dry %-5s: %d device calls (request.md %d), timeout form(s) %s, events %d expected %d, sequence %s, calls '
              'without the registered window or stop file %d' % (pl, len(calls), want_calls[pl], forms, len(got), len(exp),
                                                                   'SAME' if same else 'DIFFERENT', badline))
        if len(calls) != want_calls[pl] or not same or badline or len(forms) != 1:
            fail('dry %s listing' % pl)
            for i, (x, y) in enumerate(zip(got, exp)):
                if x != y:
                    print('   first difference at event %d: listing %s, expected %s' % (i, x, y))
                    break
    print('TRAINS CHECK %s' % ('PASS' if not bad else 'FAIL (%d)' % bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
