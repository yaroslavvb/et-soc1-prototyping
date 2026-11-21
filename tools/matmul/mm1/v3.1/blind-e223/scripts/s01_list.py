#!/usr/bin/env python3
"""decl-e223 (Q239) step 1a: E223's runs, listed by id from the registered kit's schedules and arms only (the orchestrator's copy of
EE/src, out/orch/e223-src, SRC-SHA256SUMS.txt 627b622e...). NO measurement exists or is opened: this reads src/sched/<card>-<S>.json and
src/arms.json only. decl-e221's s01_list.py in form. The run id is E223|<card>-<S>|<i:03d>-<arm>, the kit's own run key (run_mms.py:
f"{i:03d}-{arm}"). Each run's arm token is the first field of its --values string (the host's grammar, mms_common.arm_of); E223's are
all gemmL<MB>x<NB>x<KB> (rgm136's cooperative gemmL loop; no gemmLnc, no block, stream or TenB arm: checked); its kind as the arm id
spells it (rnd -> random, zeros, ones: the lab's kinds only; E223 designs no tile).
ARM CLASSES (one class a run, from arms.json's family codes, by this precedence, the proposal's order: "the core-group placement law
first ..., then the held-walk edge, the L3 region, the wide-B wait and the masked energy terms"): ANCHOR (the anchor, 4x8x8 int8
random); PLACE (family 'place': one shape placed on shire groups, every placement a subset mask: PL and its subfamilies, KW, G111/K111,
CNT, I8, MIX/COL/ROW, FEED, TYPE, D1/D2/D4, ...); EDGE (EDG, EDG2, EDGR, HO-EDGE: the held-walk edge, whole chip); L3 (L3R, L3R2, HO-L3,
e220-4: the L3 region); WIDE (WID, WID2, HO-WIDE: the wide-B wait); GATE (GATE, GAT, HO-GATE, medium-2, TW, HO-TW not already PLACE: the
masked energy cases at the whole chip and at masks outside 'place'); KIND (KND, KND2, N3, N4, HO-KIND, CW, v37-18: kinds at the whole chip
and at 26 shires); CELL111 (G111, G11, v37-6, HO-111, K111 not already PLACE: the 1x1x1 cells); SHAPE (SHAPE, SH2, syn: the two shape
probes and their masks).
TAGS (not exclusive): the HELD-OUT SETS (the 15 families HO-<x> the proposal names its held-out placements by; an arm may be in two);
GATESET (every arm of family GATE, its masked energy cases in whichever class); MASKE221 (blind-e221's MASK class by its own definition:
decl-e221's precedence ANCHOR, L2I8 (family L2I8), CELL1 (families CLK, PLS), then MASK = family PL: E223's arms.json has no L2I8, CLK or
PLS code, so MASKE221 = every non-anchor arm of family PL); group_mask FULL / SUB.
MM1's domain is decided in step 1b/p01 by calling each frozen predictor (no form, no forecast).
Run: /usr/bin/python3 -I -B s01_list.py <lane dir>
"""
import collections
import hashlib
import json
import os
import re
import sys

L = os.path.abspath(sys.argv[1])
SRC = os.path.join(L, 'work', 'e223-src', 'src')
OUTD = os.path.join(L, 'work', 'step1')
os.makedirs(OUTD, exist_ok=True)
CARDS = {'a1c1': 'aifoundry1 card 1', 'a1c0': 'aifoundry1 card 0', 'a2c0': 'aifoundry2 card 0'}
PRIMARY_VIEW = {'a1c1': 'band600', 'a1c0': 'win', 'a2c0': 'win'}     # reduce_mms.py: "win" on the governed cards, else "band 600"
KIND = {'rnd': 'random', 'zeros': 'zeros', 'ones': 'ones'}
FULL = '0xffffffff'
GEMML = re.compile(r'gemmL([1-9][0-9]*)x([1-9][0-9]*)x([1-9][0-9]*)$')
PREC = (('ANCHOR', ('anchor',)), ('PLACE', ('place',)), ('EDGE', ('EDG', 'EDG2', 'EDGR', 'HO-EDGE')),
        ('L3', ('L3R', 'L3R2', 'HO-L3', 'e220-4')), ('WIDE', ('WID', 'WID2', 'HO-WIDE')),
        ('GATE', ('GATE', 'GAT', 'HO-GATE', 'medium-2', 'TW', 'HO-TW')), ('KIND', ('KND', 'KND2', 'N3', 'N4', 'HO-KIND', 'CW', 'v37-18')),
        ('CELL111', ('G111', 'G11', 'v37-6', 'HO-111', 'K111')), ('SHAPE', ('SHAPE', 'SH2', 'syn')))
CLASSES = tuple(c for c, _ in PREC)
WHAT = {'ANCHOR': 'the anchor (4x8x8 int8 random, whole chip): first, between blocks and last in each session',
        'PLACE': "the core-group placements (family 'place'): 11 gemmL shapes (MB 1-4, NB 1-16, KB 1-24; fp32, fp16, int8) placed on "
                 "shire groups at subset masks of 1 to 28 shires (PL with its subfamilies PL1, P34, G10, G14, FLOOR, ND1/ND2/ND34, D1/D2/D4, "
                 "CNT/CNT3, TYPE; KW, G111/K111, I8, MIX/COL/ROW, FEED); the proposal's placement law, its held-out placements in the HO sets",
        'EDGE': 'the held-walk edge (EDG, EDG2, EDGR, HO-EDGE): 20 gemmL shapes at MB 2-16, NB 6-10, KB 1-2 (fp32, int8), whole chip',
        'L3': "the L3 region (L3R, L3R2, HO-L3, e220-4; the proposal's words): 13 narrow-N gemmL shapes at MB 2-8, NB 1-2, KB 1-6, whole chip",
        'WIDE': 'the wide-B wait (WID, WID2, HO-WIDE): 18 wide-N deep-K gemmL shapes at MB 1-6, NB 9-24, KB 16-32 (fp32), whole chip',
        'GATE': 'the masked energy cases outside PLACE (GATE, GAT, HO-GATE, medium-2, TW, HO-TW): fp32 zeros of 1x12x8 and 2x6x10 at the '
                'whole chip and at gate masks of 5, 8 and 16 shires',
        'KIND': 'the kinds (KND, KND2, N3, N4, HO-KIND, CW, v37-18): five gemmL shapes (1x12x8, 1x1x1, 2x1x16, 2x2x3, 2x6x10) at zeros, ones '
                'and random, at the whole chip and at 26 shires',
        'CELL111': 'the 1x1x1 cells outside PLACE (G111, G11, v37-6, HO-111): gemmL 1x1x1 fp32 zeros at single shires',
        'SHAPE': 'the shape probes (SHAPE, SH2, syn): gemmL 1x10x10 and 2x8x8 fp32 zeros at the whole chip and at single shires'}


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
assert not ARMSJ['tiles'], 'E223 designs no tile: arms.json tiles must be empty'
out = {'what': 'decl-e223 step 1a: E223 runs from the registered schedules and arms.json (no measurement exists)',
       'python': sys.version.split()[0], 'runs': [], 'sessions': {}, 'arms_json_sha256': sha(os.path.join(SRC, 'arms.json')),
       'designed_tiles': len(ARMSJ['tiles']), 'class_what': WHAT, 'classes': list(CLASSES), 'precedence': [[c, list(f)] for c, f in PREC]}
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
            ho = sorted(f for f in fam if f.startswith('HO-'))
            sub = sorted(f for f in fam if f.startswith('PL') and f != 'PL')
            rec = {'id': f"E223|{s}|{key}", 'session': s, 'card': CARDS[ck], 'card_key': ck, 'i': r['i'], 'run': key, 'block': r.get('block'),
                   'role': r['role'], 'arm_label': r['arm'], 'token': tok, 'class': cl, 'ho_sets': ho, 'gateset': 'GATE' in fam,
                   'maske221': ('PL' in fam and cl != 'ANCHOR'), 'subfamily': '+'.join(sub) if sub else None,
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
                                     'ho_sets': list(r['ho_sets']), 'gateset': r['gateset'], 'maske221': r['maske221'],
                                     'group_mask': r['group_mask'], 'families': r['families'], 'kernel': r['kernel'],
                                     'MB': r['MB'], 'NB': r['NB'], 'KB': r['KB'],
                                     'ops_per_minion_pass': r['ops_per_minion_pass'], 'n_shires': r['n_shires']})
    assert c['ops_per_minion_pass'] == r['ops_per_minion_pass']
    assert c['arm_label'] == r['arm_label'], (c['case'], c['arm_label'], r['arm_label'])
    c['runs'].append(r['id'])
    if r['class'] not in c['classes_of_runs']:
        c['classes_of_runs'].append(r['class'])
out['cases'] = list(cases.values())
CC = out['cases']
multi = [c['case'] for c in CC if len(c['classes_of_runs']) > 1]
out['cases_with_runs_of_two_classes'] = multi
hoc = collections.Counter(h for c in CC for h in c['ho_sets'])
hor = collections.Counter(h for r in R for h in r['ho_sets'])
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
                 'ho_sets': len(hoc), 'ho_cases_by_set': dict(sorted(hoc.items())), 'ho_runs_by_set': dict(sorted(hor.items())),
                 'ho_cases_any': sum(1 for c in CC if c['ho_sets']), 'ho_runs_any': sum(1 for r in R if r['ho_sets']),
                 'gateset_cases': sum(1 for c in CC if c['gateset']), 'maske221_cases': sum(1 for c in CC if c['maske221']),
                 'maske221_runs': sum(1 for r in R if r['maske221']),
                 'arms_listed': len({r['arm_label'] for r in R}), 'arms_in_arms_json': len(ARMS),
                 'distinct_masks': len({r['mask'] for r in R}),
                 'subset_configurations (shape, mask)': len({(r['MB'], r['NB'], r['KB'], r['mask']) for r in R if r['mask'] != FULL})}
out['arms_never_scheduled'] = sorted(set(ARMS) - {r['arm_label'] for r in R})
json.dump(out, open(os.path.join(OUTD, 'runs-listed.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps(out['counts'], indent=1, sort_keys=True)[:7000])
print('arms never scheduled (anchor/smoke-only or not run):', out['arms_never_scheduled'][:20], len(out['arms_never_scheduled']))
print('cases with runs of two classes:', multi[:10], len(multi))
print(json.dumps({s: {k: v for k, v in d.items() if k in ('n_sched', 'roles', 'planned_min')} for s, d in out['sessions'].items()}))
print(sha(os.path.join(OUTD, 'runs-listed.json')), 'work/step1/runs-listed.json')
