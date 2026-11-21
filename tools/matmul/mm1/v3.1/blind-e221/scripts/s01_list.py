#!/usr/bin/env python3
"""decl-e221 (Q235) step 1a: E221's runs, listed by id from the registered kit's schedules and arms only (the orchestrator's copy of
EE/src, out/orch/e221-src, SRC-SHA256SUMS.txt 5680112f...). NO measurement exists or is opened: this reads src/sched/<card>-<S>.json and
src/arms.json only. decl-e219's s01_list.py in form. The run id is E221|<card>-<S>|<i:03d>-<arm>, the kit's own run key (run_mms.py:
f"{i:03d}-{arm}"). Each run's arm token is the first field of its --values string (the host's grammar, mms_common.arm_of); E221's are
all gemmL<MB>x<NB>x<KB> (rgm136's cooperative gemmL loop; no gemmLnc, no block, stream or TenB arm: checked); its kind as the arm id
spells it (rnd -> random, zeros, ones: the lab's kinds only; E221 designs no tile).
ARM CLASSES (from arms.json's family codes; one class a run, by this precedence): ANCHOR (the anchor, 4x8x8 int8 random), L2I8 (the int8
L2 point: gemmL 1x1xK int8 at masks and the whole chip, with its fp32 pair), CELL1 (the 1x1x1 cells at new masks: families CLK and PLS),
MASK (the core-group masks: family PL, its subfamilies PLA, PLB, PLC, PLD, PLE, PLH, PLK, PLK3, PLL, PLM, PLN, PLX, with their
whole-chip twins), KB1 (KB = 1), DK (deep K), HLD (the held walks), MQ3 (the MB = 3 ladders), NB1 (NB = 1), BW (the three BW shapes at
every kind). MM1's domain is decided in step 1b/p01 by calling each frozen predictor (no form, no forecast).
Run: /usr/bin/python3 -I -B s01_list.py <lane dir>
"""
import collections
import hashlib
import json
import os
import re
import sys

L = os.path.abspath(sys.argv[1])
SRC = os.path.join(L, 'work', 'e221-src', 'src')
OUTD = os.path.join(L, 'work', 'step1')
os.makedirs(OUTD, exist_ok=True)
CARDS = {'a1c1': 'aifoundry1 card 1', 'a1c0': 'aifoundry1 card 0', 'a2c0': 'aifoundry2 card 0'}
PRIMARY_VIEW = {'a1c1': 'band600', 'a1c0': 'win', 'a2c0': 'win'}     # reduce_mms.py: "win" on the governed cards, else "band 600"
KIND = {'rnd': 'random', 'zeros': 'zeros', 'ones': 'ones'}
FULL = '0xffffffff'
GEMML = re.compile(r'gemmL([1-9][0-9]*)x([1-9][0-9]*)x([1-9][0-9]*)$')
PREC = (('ANCHOR', ('anchor',)), ('L2I8', ('L2I8',)), ('CELL1', ('CLK', 'PLS')), ('MASK', ('PL',)), ('KB1', ('KB1',)), ('DK', ('DK',)),
        ('HLD', ('HLD',)), ('MQ3', ('MQ3',)), ('NB1', ('NB1',)), ('BW', ('BW',)))
WHAT = {'ANCHOR': 'the anchor (4x8x8 int8 random, whole chip): first, between blocks and last in each session',
        'L2I8': 'the int8 L2 point: gemmL 1x1xK int8 (K blocks 1-13) at the whole chip and at masks, with two fp32 zeros pairs',
        'CELL1': 'the 1x1x1 cells at new masks (families CLK and PLS): gemmL 1x1x1 at shire masks never run before, fp32 and fp16',
        'MASK': 'the core-group masks (family PL: placement of one shape on shire groups, PLA/PLB/PLC/PLD/PLE/PLH/PLK/PLK3/PLL/PLM/PLN/PLX), '
                'each with its whole-chip twin',
        'KB1': 'KB = 1: gemmL MBxNBx1 at the whole chip (fp32 random and zeros, fp16 ones and zeros)',
        'DK': 'deep K: gemmL at KB 16-32, the whole chip',
        'HLD': 'the held walks: small gemmL shapes (2x3x3, 2x6x2, 2x7x2, 3x3x2, 3x5x2), the whole chip',
        'MQ3': 'the MB = 3 ladders: gemmL 3xNBxKB, the whole chip',
        'NB1': 'NB = 1: gemmL 2x1x7, 9x1x1, 9x1x2, the whole chip',
        'BW': 'the BW shapes: gemmL 2x12x4, 5x12x2, 6x5x3 at every kind, the whole chip'}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def classify(a):
    fam = set(a.get('families', []))
    for cl, codes in PREC:
        if fam & set(codes):
            return cl
    raise SystemExit(f"no class for {a['id']}: {sorted(fam)}")


ARMSJ = json.load(open(os.path.join(SRC, 'arms.json')))
ARMS = {a['id']: a for a in ARMSJ['arms']}
assert not ARMSJ['tiles'], 'E221 designs no tile: arms.json tiles must be empty'
out = {'what': 'decl-e221 step 1a: E221 runs from the registered schedules and arms.json (no measurement exists)',
       'python': sys.version.split()[0], 'runs': [], 'sessions': {}, 'arms_json_sha256': sha(os.path.join(SRC, 'arms.json')),
       'designed_tiles': len(ARMSJ['tiles']), 'class_what': WHAT}
for ck, ss in ARMSJ['sessions'].items():
    for S in ss:
        s = f'{ck}-{S}'
        p = os.path.join(SRC, 'sched', f'{s}.json')
        sched = json.load(open(p))
        assert sched['card'] == ck and sched['session'] == S, s
        out['sessions'][s] = {'card': CARDS[ck], 'card_key': ck, 'sched_sha256': sha(p), 'n_sched': len(sched['runs']),
                              'roles': dict(collections.Counter(r['role'] for r in sched['runs'])), 'planned_min': sched['planned_min'],
                              'line_w': sched.get('line_w'), 'primary_view': PRIMARY_VIEW[ck],
                              'smoke': [x['arm'] for x in sched.get('smoke', [])]}
        for r in sched['runs']:
            if r['role'] in (None, 'null') or r['arm'] is None or str(r['arm']).startswith('null'):
                continue
            a = ARMS[r['arm']]
            assert a['values'] == r['values'] and a['shires'] == r['shires'] and a['type'] == r['type'], (s, r['arm'])
            tok, gen, tfile = a['values'].split(':', 2)
            m = GEMML.match(tok)
            assert m, (r['arm'], tok)
            MB, NB, KB = (int(x) for x in m.groups())
            assert (MB, NB, KB) == (a['mb'], a['nb'], a['kb']), r['arm']
            ops = MB * NB * 2 * KB * 32
            assert ops == a['ops_per_minion_pass'], (r['arm'], ops, a['ops_per_minion_pass'])
            cl = classify(a)
            kind = KIND[a['kind']]
            mask = a['shires'].lower()
            tname = os.path.splitext(os.path.basename(tfile))[0]
            assert tname in ('randn', 'zeros', 'ones', 'full'), (r['arm'], tfile)
            key = f"{r['i']:03d}-{r['arm']}"
            fam = a.get('families', [])
            sub = sorted(f for f in fam if f.startswith('PL') and f != 'PL')
            rec = {'id': f"E221|{s}|{key}", 'session': s, 'card': CARDS[ck], 'card_key': ck, 'i': r['i'], 'run': key, 'block': r.get('block'),
                   'role': r['role'], 'arm_label': r['arm'], 'token': tok, 'class': cl, 'subfamily': '+'.join(sub) if sub else None,
                   'arm': tok, 'kernel': 'rgm136', 'MB': MB, 'NB': NB, 'KB': KB, 'fmt': a['type'], 'kind': kind, 'kind_energy': kind,
                   'mask': mask, 'n_shires': bin(int(mask, 16)).count('1'), 'minions': 32 * bin(int(mask, 16)).count('1'),
                   'ops_per_minion_pass': a['ops_per_minion_pass'], 'values': a['values'], 'gen': gen, 'tile_file': tfile,
                   'tile_name': tname, 'families': fam, 'priority': a.get('priority'), 'form': r.get('form'), 'unit': r.get('unit'),
                   'est_peak_w': r.get('est_peak_w'), 'est_s': r.get('est_s'), 'group_mask': 'FULL' if mask == FULL else 'SUB',
                   'case': f"{CARDS[ck]}|{tok}|{a['type']}|{kind}|{mask}"}
            out['runs'].append(rec)
R = out['runs']
cases = collections.OrderedDict()
for r in R:
    c = cases.setdefault(r['case'], {'case': r['case'], 'card': r['card'], 'arm': r['arm'], 'token': r['token'], 'fmt': r['fmt'],
                                     'kind': r['kind'], 'kind_energy': r['kind_energy'], 'mask': r['mask'], 'arm_label': r['arm_label'],
                                     'runs': [], 'class': r['class'], 'classes_of_runs': [], 'subfamily': r['subfamily'],
                                     'group_mask': r['group_mask'], 'families': r['families'], 'kernel': r['kernel'],
                                     'MB': r['MB'], 'NB': r['NB'], 'KB': r['KB'],
                                     'ops_per_minion_pass': r['ops_per_minion_pass'], 'n_shires': r['n_shires']})
    assert c['ops_per_minion_pass'] == r['ops_per_minion_pass']
    c['runs'].append(r['id'])
    if r['class'] not in c['classes_of_runs']:
        c['classes_of_runs'].append(r['class'])
out['cases'] = list(cases.values())
CC = out['cases']
multi = [c['case'] for c in CC if len(c['classes_of_runs']) > 1]
out['cases_with_runs_of_two_classes'] = multi
out['counts'] = {'listed_runs (arm and anchor; nulls and smoke left out)': len(R), 'cases': len(cases),
                 'by_card': dict(collections.Counter(r['card'] for r in R)), 'by_fmt': dict(collections.Counter(r['fmt'] for r in R)),
                 'by_role': dict(collections.Counter(r['role'] for r in R)),
                 'by_class': dict(collections.Counter(r['class'] for r in R)),
                 'by_kind': dict(collections.Counter(r['kind'] for r in R)),
                 'by_session': dict(collections.Counter(r['session'] for r in R)),
                 'cases_by_card': dict(collections.Counter(c['card'] for c in CC)),
                 'cases_by_class': dict(collections.Counter(c['class'] for c in CC)),
                 'cases_by_class_card': dict(collections.Counter(f"{c['class']}|{c['card']}" for c in CC)),
                 'cases_by_group_mask': dict(collections.Counter(c['group_mask'] for c in CC)),
                 'arms_listed': len({r['arm_label'] for r in R}), 'arms_in_arms_json': len(ARMS),
                 'distinct_masks': len({r['mask'] for r in R}),
                 'subset_configurations (shape, mask)': len({(r['MB'], r['NB'], r['KB'], r['mask']) for r in R if r['mask'] != FULL})}
out['arms_never_scheduled'] = sorted(set(ARMS) - {r['arm_label'] for r in R})
json.dump(out, open(os.path.join(OUTD, 'runs-listed.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps(out['counts'], indent=1, sort_keys=True)[:6000])
print('arms never scheduled (anchor/smoke-only or not run):', out['arms_never_scheduled'][:20], len(out['arms_never_scheduled']))
print('cases with runs of two classes:', multi[:10], len(multi))
print(json.dumps({s: {k: v for k, v in d.items() if k in ('n_sched', 'roles', 'planned_min')} for s, d in out['sessions'].items()}))
print(sha(os.path.join(OUTD, 'runs-listed.json')), 'work/step1/runs-listed.json')
