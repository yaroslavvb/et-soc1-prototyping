#!/usr/bin/env python3
"""E210 (Q202): the points, the cases and the registered run order (chained A B B A blocks in six passes), with every run's host argv.

    /usr/bin/python3 -I -B tools/claims-v3/e210/points_e210.py <lab top>            writes points-e210.json and points-e210.csv
    /usr/bin/python3 -I -B tools/claims-v3/e210/points_e210.py <lab top> --check    recomputes and compares byte for byte (exit 0 PASS, 4 FAIL)

THE SHAPES: S1 = gemmL1x1x1 fp32 (1,024 x 512 x 512; 268,435,456 multiply-adds a GEMM; the C tile accumulated over 32 ops), S2 = gemmL1x1x4
fp32 (1,024 x 512 x 2,048; 1,073,741,824 multiply-adds; 128 ops an accumulation), the full chip (0xffffffff, 32 minions a shire). rgm136
unchanged (E206's build and host flags): `--test fma --type fp32 --pattern none --values <arm>:<gen>:<files> --shires 0xffffffff
--per-shire 32 --seconds 6 --budget 7.5 --seed 1`.
THE KINDS: random (gen randn, pair 0 = kinds/tiles/fp32/randn.bin: E206's exact string), the reference in every block; controls zeros, ones
(tiles of the lab's kinds tiles) and sparse50 (gen sparse50, pair 0 = kinds/tiles/fp32/sparse50.bin); E210's patterns, gen tiles of their
committed files (tiles/fp32/<p>/<p>_00 .. _60.bin, 61 files; negzero one file), the pool cycling them.
THE ORDER: a pass is R K1 K1 R K2 K2 R ... Kn Kn R (every random run shared by its two neighbouring blocks; a block of Ki is R, Ki, Ki, R);
passes: 1 S1 every kind of S1 in a seeded order; 2 S2 every kind of S2 in a seeded order; 3 S1 pass 1 reversed; 4 S2 pass 2 reversed;
5 S1 the test and reported patterns in a new seeded order; 6 S2 the test patterns in a new seeded order. Seeds random.Random("E210|<S>|pass<k>").
Tests get three blocks, controls two. The opening (rest, smoke, probe, stop-path test, two warm-up ties) and the closing tie are the plan's.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import io
import json
import os
import random
import sys

SHAPES = {
    'S1': {'arm': 'gemmL1x1x1', 'M': 1024, 'N': 512, 'K': 512, 'macs_per_gemm': 1024 * 512 * 512, 'ops_per_minion_per_gemm': 64,
           'ops_per_accumulation': 32, 'footprint_MB': 5.0},
    'S2': {'arm': 'gemmL1x1x4', 'M': 1024, 'N': 512, 'K': 2048, 'macs_per_gemm': 1024 * 512 * 2048, 'ops_per_minion_per_gemm': 256,
           'ops_per_accumulation': 128, 'footprint_MB': 14.0},
}
TESTS = {'S1': ['negzero', 'signs', 'lowmant8', 'highmant8', 'bhalfeq', 'badjeq', 'hd4'],
         'S2': ['negzero', 'lowmant8', 'highmant8', 'bhalfeq', 'hd4', 'maxalte']}
REPORTED = {'S1': ['arow50'], 'S2': []}
CONTROLS = {'S1': ['zeros', 'ones', 'sparse50'], 'S2': ['zeros', 'ones', 'sparse50']}
PROBE = ['maxalte@S2']          # a pattern that runs only after its probe in the opening (E210.md section 6)
KT = 'tools/claims-v3/kinds/tiles/fp32/'
PAT = 'tools/claims-v3/e210/tiles/fp32/'
LAWS = {
    'negzero': 'every word 0x80000000 (-0.0): every lane valid (the gate tests the all-zero word), nothing moves',
    'signs': '0x3F800000 with a random sign bit (+-1.0)',
    'lowmant8': '0x3F800000 OR 8 random bits in mantissa bits 0-7',
    'highmant8': '0x3F800000 OR 8 random bits in mantissa bits 15-22',
    'bhalfeq': 'A random normal; each B row 8 random normal words at columns l and l+8 (B[k][l+8] = B[k][l])',
    'badjeq': "bhalfeq's law with B's equal pairs in adjacent columns (2m, 2m+1)",
    'hd4': 'A: each column a random normal word, each next row = the previous xor 4 distinct random mantissa bits; B[k][l] random normal, '
           'B[k][l+8] = B[k][l] xor 4 random mantissa bits',
    'maxalte': 'A: each column a, a xor F, a, ... down the rows; B[k][l+8] = B[k][l] xor F; F = 0x83FFFFFF; a, B[k][l] random normal with '
               'exponent field 8-247',
    'arow50': "A's odd rows +0.0, every other A word and every B word random normal",
    'random': 'normal(0, 1), every element drawn by the host (gen randn, seed 1; pair 0 = randn.bin)',
    'zeros': 'every word +0.0 (zeros.bin)', 'ones': 'every word 1.0 (ones.bin)',
    'sparse50': 'normal(0, 1) with half the elements +0.0, drawn by the host (gen sparse50, seed 1; pair 0 = sparse50.bin)',
}


def values(kind, arm, top):
    if kind == 'random':
        return f'{arm}:randn:{KT}randn.bin'
    if kind == 'sparse50':
        return f'{arm}:sparse50:{KT}sparse50.bin'
    if kind in ('zeros', 'ones'):
        return f'{arm}:tiles:{KT}{kind}.bin'
    n = 1 if kind == 'negzero' else 61
    files = [f'{PAT}{kind}/{kind}_{i:02d}.bin' for i in range(n)]
    for f in files:
        assert os.path.isfile(os.path.join(top, f)), f
    return f'{arm}:tiles:' + ','.join(files)


def argv(v):
    return ['--test', 'fma', '--type', 'fp32', '--pattern', 'none', '--values', v, '--shires', '0xffffffff', '--per-shire', '32',
            '--seconds', '6', '--budget', '7.5', '--seed', '1']


def role(kind, s):
    if kind == 'random':
        return 'reference'
    if kind in TESTS[s]:
        return 'test'
    if kind in REPORTED[s]:
        return 'reported'
    return 'control'


def chain(kinds, s, pname, runs, blocks):
    """R K K R K K R ...: appends runs and blocks; every block names its four runs"""
    prev_r = len(runs)
    runs.append({'pass': pname, 'shape': s, 'kind': 'random', 'role': 'R'})
    for k in kinds:
        i1 = len(runs)
        runs.append({'pass': pname, 'shape': s, 'kind': k, 'role': 'P'})
        runs.append({'pass': pname, 'shape': s, 'kind': k, 'role': 'P'})
        r2 = len(runs)
        runs.append({'pass': pname, 'shape': s, 'kind': 'random', 'role': 'R'})
        blocks.append({'block': f'{pname}:{s}:{k}', 'pass': pname, 'shape': s, 'kind': k, 'runs': [prev_r, i1, i1 + 1, r2]})
        prev_r = r2


def build(top):
    cases = []
    for s in SHAPES:
        for k in ['random'] + CONTROLS[s] + TESTS[s] + REPORTED[s]:
            cases.append({'case': f'{k}@{s}', 'kind': k, 'shape': s, 'arm': SHAPES[s]['arm'], 'role': role(k, s), 'law': LAWS[k],
                          'values': values(k, SHAPES[s]['arm'], top), 'probe_first': f'{k}@{s}' in PROBE})
    order = {}
    for s in SHAPES:
        allk = CONTROLS[s] + TESTS[s] + REPORTED[s]
        r = random.Random(f'E210|{s}|pass1')
        p1 = list(allk)
        r.shuffle(p1)
        order[(s, 1)] = p1
        order[(s, 3)] = list(reversed(p1))
        tk = TESTS[s] + REPORTED[s]
        r5 = random.Random(f'E210|{s}|pass{"5" if s == "S1" else "6"}')
        p5 = list(tk)
        r5.shuffle(p5)
        order[(s, 5)] = p5
    runs, blocks = [], []
    seq = [('pass1', 'S1', order[('S1', 1)]), ('pass2', 'S2', order[('S2', 1)]), ('pass3', 'S1', order[('S1', 3)]),
           ('pass4', 'S2', order[('S2', 3)]), ('pass5', 'S1', order[('S1', 5)]), ('pass6', 'S2', order[('S2', 5)])]
    opening = [{'pass': 'open', 'shape': 'S1', 'kind': 'random', 'role': 'tie'}, {'pass': 'open', 'shape': 'S1', 'kind': 'random', 'role': 'tie'}]
    runs.extend(opening)
    for pname, s, kinds in seq:
        chain(kinds, s, pname, runs, blocks)
    runs.append({'pass': 'close', 'shape': 'S1', 'kind': 'random', 'role': 'tie'})
    cmap = {c['case']: c for c in cases}
    for i, r in enumerate(runs):
        r['n'] = i + 1
        r['run'] = f"{i + 1:03d}-{r['pass']}-{r['kind']}-{r['shape']}"
        r['case'] = f"{r['kind']}@{r['shape']}"
        r['host_args'] = argv(cmap[r['case']]['values'])
    for b in blocks:
        b['runs'] = [runs[j]['run'] for j in b['runs']]
    nb = {}
    for b in blocks:
        nb[(b['kind'], b['shape'])] = nb.get((b['kind'], b['shape']), 0) + 1
    for c in cases:
        c['blocks_planned'] = nb.get((c['kind'], c['shape']), 0)
    plan_s = {'S1': 26.0, 'S2': 22.5}
    opening_s = 60 + 3 * 30 + 30 + 30          # 60 s at rest; the smoke (3 checked 2 s processes, about 30 s each with gates and rests); the probe; the stop-path test
    run_s = sum(plan_s[r['shape']] for r in runs)
    cut = [r for r in runs if r['pass'] in ('open', 'pass1', 'pass2', 'pass3', 'pass4')]
    plan = {'planned_seconds_a_run': plan_s, 'planned_from': "E206 arm A's pace on this card (21.97 s a run on average; 8-14 s die-gate waits after a 59 W run), sw-design-b",
            'opening_seconds': opening_s, 'runs_seconds': run_s, 'card_minutes_planned': (opening_s + run_s) / 60.0,
            'cut_subset': 'the opening and passes 1-4 (every kind twice at both shapes)', 'cut_subset_runs': len(cut),
            'cut_subset_card_minutes': (opening_s + sum(plan_s[r['shape']] for r in cut)) / 60.0,
            'no_run_starts_after_card_minutes': 85, 'session_ends_by_card_minutes': 95, 'round_cap_card_minutes': 100}
    return {'experiment': 'E210', 'what': 'the switch test: points, cases and the registered run order', 'plan': plan, 'shapes': SHAPES, 'tests': TESTS,
            'reported': REPORTED, 'controls': CONTROLS, 'probe_first': PROBE, 'cases': cases, 'runs': runs, 'blocks': blocks,
            'seeds': {f'{s}|pass{k}': f'E210|{s}|pass{k}' for s in SHAPES for k in (1, 5 if s == 'S1' else 6)},
            'n_runs': len(runs), 'n_blocks': len(blocks)}


def csv_text(d):
    f = io.StringIO()
    w = csv.writer(f, lineterminator='\n')
    w.writerow(['case', 'kind', 'shape', 'arm', 'M', 'N', 'K', 'format', 'role', 'blocks_planned', 'law', 'values'])
    for c in d['cases']:
        sh = SHAPES[c['shape']]
        w.writerow([c['case'], c['kind'], c['shape'], c['arm'], sh['M'], sh['N'], sh['K'], 'fp32', c['role'], c['blocks_planned'], c['law'],
                    c['values'] if len(c['values']) < 120 else c['values'][:c['values'].index(':tiles:') + 7] + f"<{c['values'].count(',') + 1} files>"])
    return f.getvalue()


def main():
    top = os.path.abspath(sys.argv[1])
    here = os.path.join(top, 'tools/claims-v3/e210')
    d = build(top)
    js = json.dumps(d, indent=1, sort_keys=True) + '\n'
    cs = csv_text(d)
    if '--check' in sys.argv:
        ok = open(os.path.join(here, 'points-e210.json')).read() == js and open(os.path.join(here, 'points-e210.csv')).read() == cs
        print('points_e210 --check', 'PASS' if ok else 'FAIL')
        return 0 if ok else 4
    open(os.path.join(here, 'points-e210.json'), 'w').write(js)
    open(os.path.join(here, 'points-e210.csv'), 'w').write(cs)
    print(f"cases {len(d['cases'])}, runs {d['n_runs']}, blocks {d['n_blocks']}; planned {d['plan']['card_minutes_planned']:.1f} card-minutes "
          f"(cut subset {d['plan']['cut_subset_card_minutes']:.1f})")
    for c in d['cases']:
        print(f"  {c['case']:16s} {c['role']:9s} blocks {c['blocks_planned']}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
