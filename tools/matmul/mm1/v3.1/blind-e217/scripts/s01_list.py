#!/usr/bin/env python3
"""decl-e217 (Q228) step 1a: E217's runs, listed by id from the registered kit's schedules and arms only (the orchestrator's copy of
EE/src, out/orch/e217-src, SRC-SHA256SUMS.txt 854bd075...). NO measurement exists or is opened: E217 has not run; this reads
src/sched/<card>-<S>.json and src/arms.json only. Each run's model inputs (arm, format, kind, mask, card) come from arms.json; its kind by
MM1-v3's own data_v3.e212_kind regex (the arm's name: rnd -> random, zeros, ones, any other -> 'pattern:<name>'), its energy kind as
MM1-v3.1's data_v31 prices it (pattern:sparse50f / sparse50h / sparse50i -> sparse50: unread-e214's declared alias; E217's three sparse50
pool files are byte-equal to E214's). The run id is E217|<card>-<S>|<i:03d>-<arm>, the kit's own run key (run_mms.py: f"{i:03d}-{arm}").
Groups (from arms.json alone): X1 the 1x1x1 cells; MG the new core-group masks (the plan's tag 'P1-sim'); SUB the other subset masks;
FULL the full chip; S the 21 new operand-pattern kinds (no committed count); C the sparse50 pools; K the lab's kinds (zeros, ones, random).
Desk; no device. Run: /usr/bin/python3 -I -B s01_list.py <lane dir>
"""
import collections
import hashlib
import json
import os
import re
import sys

L = os.path.abspath(sys.argv[1])
SRC = os.path.join(L, 'work', 'e217-src', 'src')
OUTD = os.path.join(L, 'work', 'step1')
os.makedirs(OUTD, exist_ok=True)
CARDS = {'a1c1': 'aifoundry1 card 1', 'a1c0': 'aifoundry1 card 0'}
PRIMARY_VIEW = {'a1c1': 'band600', 'a1c0': 'win'}     # reduce_mms.py: "win" on the governed cards, else "band600"
E212_KIND = {'rnd': 'random', 'zeros': 'zeros', 'ones': 'ones'}
SPARSE_GEN = {'pattern:sparse50f': 'sparse50', 'pattern:sparse50i': 'sparse50', 'pattern:sparse50h': 'sparse50'}
FULL = '0xffffffff'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def e212_kind(arm):
    """MM1-v3's data_v3.e212_kind, the same regex"""
    m = re.fullmatch(r'\d+x\d+x\d+-(?:fp32|fp16|int8)-([A-Za-z0-9_]+?)(?:-(?:s\d+|m[0-9a-f]+))?', arm)
    if not m:
        return None
    k = m.group(1)
    return E212_KIND.get(k, 'pattern:' + k)


ARMSJ = json.load(open(os.path.join(SRC, 'arms.json')))
ARMS = {a['id']: a for a in ARMSJ['arms']}
TILES = ARMSJ['tiles']
out = {'what': 'decl-e217 step 1a: E217 runs from the registered schedules and arms.json (no measurement exists)',
       'python': sys.version.split()[0], 'runs': [], 'sessions': {}, 'arms_json_sha256': sha(os.path.join(SRC, 'arms.json'))}
for ck, ss in ARMSJ['sessions'].items():
    for S in ss:
        s = f'{ck}-{S}'
        p = os.path.join(SRC, 'sched', f'{s}.json')
        sched = json.load(open(p))
        assert sched['card'] == ck and sched['session'] == S, s
        out['sessions'][s] = {'card': CARDS[ck], 'card_key': ck, 'sched_sha256': sha(p), 'n_sched': len(sched['runs']),
                              'roles': dict(collections.Counter(r['role'] for r in sched['runs'])), 'planned_min': sched['planned_min'],
                              'line_w': sched['line_w'], 'primary_view': PRIMARY_VIEW[ck],
                              'smoke': [x['arm'] for x in sched.get('smoke', [])]}
        for r in sched['runs']:
            if r['role'] in (None, 'null') or r['arm'] is None or str(r['arm']).startswith('null'):
                continue
            a = ARMS[r['arm']]
            assert a['values'] == r['values'] and a['shires'] == r['shires'] and a['type'] == r['type'], (s, r['arm'])
            m = re.match(r'gemmL(\d+)x(\d+)x(\d+):([a-z0-9]+):(\S+)$', a['values'])
            MB, NB, KB = (int(x) for x in m.groups()[:3])
            gen, tfile = m.group(4), m.group(5)
            kind = e212_kind(r['arm'])
            tname = os.path.splitext(os.path.basename(tfile))[0]
            fam = a.get('families', [])
            mask = a['shires'].lower()
            if (MB, NB, KB) == (1, 1, 1):
                gshape = 'X1'
            else:
                gshape = 'notX1'
            if mask == FULL:
                gmask = 'FULL'
            elif 'P1-sim' in fam:
                gmask = 'MG'
            else:
                gmask = 'SUB'
            if kind in ('zeros', 'ones', 'random'):
                gkind = 'K'
            elif kind in SPARSE_GEN:
                gkind = 'C'
            else:
                gkind = 'S'
            key = f"{r['i']:03d}-{r['arm']}"
            rec = {'id': f"E217|{s}|{key}", 'session': s, 'card': CARDS[ck], 'card_key': ck, 'i': r['i'], 'run': key, 'block': r['block'],
                   'role': r['role'], 'arm_label': r['arm'], 'arm': f'gemmL{MB}x{NB}x{KB}', 'MB': MB, 'NB': NB, 'KB': KB, 'kernel': 'rgm136',
                   'fmt': a['type'], 'kind': kind, 'kind_energy': SPARSE_GEN.get(kind, kind), 'mask': mask,
                   'n_shires': bin(int(mask, 16)).count('1'), 'minions': 32 * bin(int(mask, 16)).count('1'),
                   'ops_per_minion_pass': a['ops_per_minion_pass'], 'values': a['values'], 'gen': gen, 'tile_file': tfile,
                   'tile_name': tname, 'families': fam, 'priority': a.get('priority'), 'form': r.get('form'), 'unit': r.get('unit'),
                   'est_peak_w': r.get('est_peak_w'), 'est_s': r.get('est_s'), 'group_shape': gshape, 'group_mask': gmask,
                   'group_kind': gkind, 'case': f"{CARDS[ck]}|gemmL{MB}x{NB}x{KB}|{a['type']}|{kind}|{mask}"}
            assert rec['ops_per_minion_pass'] == MB * NB * 2 * KB * 32, rec['arm_label']
            out['runs'].append(rec)
R = out['runs']
cases = collections.OrderedDict()
for r in R:
    c = cases.setdefault(r['case'], {'case': r['case'], 'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'],
                                     'kind_energy': r['kind_energy'], 'mask': r['mask'], 'arm_label': r['arm_label'], 'runs': [],
                                     'group_shape': r['group_shape'], 'group_mask': r['group_mask'], 'group_kind': r['group_kind'],
                                     'families': r['families'], 'MB': r['MB'], 'NB': r['NB'], 'KB': r['KB'], 'n_shires': r['n_shires']})
    c['runs'].append(r['id'])
out['cases'] = list(cases.values())
out['counts'] = {'listed_runs (arm and anchor; nulls left out)': len(R), 'cases': len(cases),
                 'by_card': dict(collections.Counter(r['card'] for r in R)), 'by_fmt': dict(collections.Counter(r['fmt'] for r in R)),
                 'by_role': dict(collections.Counter(r['role'] for r in R)),
                 'by_group_shape': dict(collections.Counter(r['group_shape'] for r in R)),
                 'by_group_mask': dict(collections.Counter(r['group_mask'] for r in R)),
                 'by_group_kind': dict(collections.Counter(r['group_kind'] for r in R)),
                 'cases_by_card': dict(collections.Counter(c['card'] for c in cases.values())),
                 'cases_by_group_mask': dict(collections.Counter(c['group_mask'] for c in cases.values())),
                 'cases_by_group_shape': dict(collections.Counter(c['group_shape'] for c in cases.values())),
                 'cases_by_group_kind': dict(collections.Counter(c['group_kind'] for c in cases.values())),
                 'arms_listed': len({r['arm_label'] for r in R}), 'new_kinds': sorted({r['kind'] for r in R if r['group_kind'] == 'S'}),
                 'mg_masks_by_card': {cd: sorted({r['mask'] for r in R if r['group_mask'] == 'MG' and r['card'] == cd}) for cd in CARDS.values()}}
json.dump(out, open(os.path.join(OUTD, 'runs-listed.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps(out['counts'], indent=1, sort_keys=True)[:4000])
print(json.dumps({s: {k: v for k, v in d.items() if k in ('n_sched', 'roles', 'planned_min')} for s, d in out['sessions'].items()}))
print(sha(os.path.join(OUTD, 'runs-listed.json')), 'work/step1/runs-listed.json')
