#!/usr/bin/env python3
"""decl-e219 (Q232) step 1a: E219's runs, listed by id from the registered kit's schedules and arms only (the orchestrator's copy of
EE/src, out/orch/e219-src, SRC-SHA256SUMS.txt 247456da...). NO measurement exists or is opened: E219 has not run; this reads
src/sched/<card>-<S>.json and src/arms.json only. The run id is E219|<card>-<S>|<i:03d>-<arm>, the kit's own run key (run_mms.py:
f"{i:03d}-{arm}"). Each run's arm token is the first field of its --values string (the host's grammar, mms_common.arm_of: gemmL<MB>x<NB>x<KB>,
gemm<B>[r<R>][s], gemmc<B>[r<R>][s], gemmh<B>[r<R>][s], mm<N>, tenb); its kind as the arm id spells it (rnd -> random, zeros, ones: the
lab's kinds only; E219 designs no tile).
MM1'S DOMAIN (read from the frozen models' code and probed by calling them, p01): a run is IN DOMAIN when its token is one a frozen MM1
forecasts: rgm136's gemmL<MB>x<NB>x<KB> loop, or one of run_gemm's calibrating c-arms in the models' table (mm1_core carm_classes /
carm_halves: gemmc1, gemmc4s, gemmc8s, gemmc8, gemmc16, gemmc16s, and gemmc16r<R> by the regex gemmc16r(\\d+), whole token); every other
token is OUT OF DOMAIN (the models raise KeyError on it: no form), listed by class with what it measures and never forecast.
Classes: gemmL: CTRL (the gemmL 1x1x1 controls that tie E219 to E217, family 'control'), GAP (the gap cells), ANCHOR (4x8x8 int8 random);
in-domain c-arms: CTAB (the table's six arms), C16R (gemmc16r<R>, the R ladder); out of domain: OUT-gemmc (other B, R or shared C),
OUT-gemmh, OUT-gemm (B packed by k), OUT-mm, OUT-tenb. Masks: FULL or SUB (only the gemmL controls run masks: the kit allows none on the
block arms). Desk; no device. Run: /usr/bin/python3 -I -B s01_list.py <lane dir>
"""
import collections
import hashlib
import json
import os
import re
import sys

L = os.path.abspath(sys.argv[1])
SRC = os.path.join(L, 'work', 'e219-src', 'src')
OUTD = os.path.join(L, 'work', 'step1')
os.makedirs(OUTD, exist_ok=True)
CARDS = {'a1c1': 'aifoundry1 card 1', 'a1c0': 'aifoundry1 card 0'}
PRIMARY_VIEW = {'a1c1': 'band600', 'a1c0': 'win'}     # reduce_mms.py: "win" on the governed cards, else "band600"
KIND = {'rnd': 'random', 'zeros': 'zeros', 'ones': 'ones'}
FULL = '0xffffffff'
CTAB = ('gemmc1', 'gemmc4s', 'gemmc8s', 'gemmc8', 'gemmc16', 'gemmc16s')      # mm1_core CARMS (v1, v2, v3, v3.1 alike)
C16R = re.compile(r'gemmc16r(\d+)')                                            # carm_classes / carm_halves: re.fullmatch
GEMML = re.compile(r'gemmL([1-9][0-9]*)x([1-9][0-9]*)x([1-9][0-9]*)$')
BLOCK = re.compile(r'(gemmnc|gemmc|gemmv|gemmh|gemm)([1-9][0-9]*)(?:r([1-9][0-9]*))?(s?)$')
MM = re.compile(r'(mmp|mm)([1-9][0-9]*)$')
KT = {'gemmc': 32, 'gemmh': 16, 'gemm': 32, 'gemmv': 32, 'gemmnc': 32}
MEASURES = {
    'OUT-gemmc': ("run_gemm's block walk (E105/E107): B blocks of C (1,024 x 512) = A (1,024 x K) x B (K x 512), B packed by column, "
                  "cooperative loads, each block R times before the walk moves on, C per block or (s) shared; 64 B R ops a minion a pass. "
                  "MM1's c-arm table holds B = 1, 4s, 8, 8s, 16, 16s and B = 16 with r<R> only: no class assignment for this B, R or "
                  "shared-C combination"),
    'OUT-gemmh': ("gemmh: gemmc's walk with half the K (16 k tiles a block), 32 B R ops a minion a pass; MM1 has no gemmh form"),
    'OUT-gemm': ("gemm: the block walk with B packed by k (E101's layout), cooperative loads, 64 B R ops a minion a pass; MM1 has no form "
                 "for this layout"),
    'OUT-mm': ("mm<N>: the stream loop: a shared pool of N tile pairs, A into the core's scratchpad and B through TenB, N ops a minion a "
               "pass; MM1 has no stream form"),
    'OUT-tenb': ("tenb: A held in the core, one B tile streamed through TenB every op, 1 op a pass; MM1 has no tenb form (its fp32/int8 "
                 "floor constants 529/270 cycles were measured on E101's tenb loop, but no predictor maps the tenb arm)"),
}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def classify(tok, a):
    """(domain, class, model arm, shape dict, ops a minion a pass by the host's grammar)"""
    m = GEMML.match(tok)
    if m:
        MB, NB, KB = (int(x) for x in m.groups())
        fam = a.get('families', [])
        if 'anchor' in fam:
            cl = 'ANCHOR'
        elif 'control' in fam:
            cl = 'CTRL'
        else:
            cl = 'GAP'
        return 'IN', cl, tok, {'MB': MB, 'NB': NB, 'KB': KB}, MB * NB * 2 * KB * 32
    m = BLOCK.match(tok)
    if m:
        fam, B, R, s = m.group(1), int(m.group(2)), int(m.group(3) or 1), m.group(4) == 's'
        ops = B * R * 2 * KT[fam]
        shape = {'family': fam, 'B': B, 'R': R, 'c_shared': s}
        if fam == 'gemmc' and tok in CTAB:
            return 'IN', 'CTAB', tok, shape, ops
        if fam == 'gemmc' and C16R.fullmatch(tok):
            return 'IN', 'C16R', tok, shape, ops
        return 'OUT', 'OUT-' + fam, None, shape, ops
    m = MM.match(tok)
    if m:
        return 'OUT', 'OUT-mm', None, {'family': m.group(1), 'N': int(m.group(2))}, int(m.group(2))
    if tok == 'tenb':
        return 'OUT', 'OUT-tenb', None, {'family': 'tenb'}, 1
    raise SystemExit(f'unknown token {tok}')


ARMSJ = json.load(open(os.path.join(SRC, 'arms.json')))
ARMS = {a['id']: a for a in ARMSJ['arms']}
assert ARMSJ['tiles'] == {} or not ARMSJ['tiles'], 'E219 designs no tile: arms.json tiles must be empty'
out = {'what': 'decl-e219 step 1a: E219 runs from the registered schedules and arms.json (no measurement exists)',
       'python': sys.version.split()[0], 'runs': [], 'sessions': {}, 'arms_json_sha256': sha(os.path.join(SRC, 'arms.json')),
       'designed_tiles': len(ARMSJ['tiles'])}
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
            tok, gen, tfile = a['values'].split(':', 2)
            dom, cl, marm, shape, ops = classify(tok, a)
            assert ops == a['ops_per_minion_pass'], (r['arm'], ops, a['ops_per_minion_pass'])
            kind = KIND[a['kind']]
            mask = a['shires'].lower()
            assert dom == 'IN' or mask == FULL, r['arm']
            tname = os.path.splitext(os.path.basename(tfile))[0]
            assert tname in ('randn', 'zeros', 'ones', 'full'), (r['arm'], tfile)
            key = f"{r['i']:03d}-{r['arm']}"
            rec = {'id': f"E219|{s}|{key}", 'session': s, 'card': CARDS[ck], 'card_key': ck, 'i': r['i'], 'run': key, 'block': r['block'],
                   'role': r['role'], 'arm_label': r['arm'], 'token': tok, 'domain': dom, 'class': cl, 'arm': marm,
                   'kernel': ('rgm136' if cl in ('CTRL', 'GAP', 'ANCHOR') else ('run_gemm' if dom == 'IN' else a.get('kernel'))),
                   'shape': shape, 'fmt': a['type'], 'kind': kind, 'kind_energy': kind, 'mask': mask,
                   'n_shires': bin(int(mask, 16)).count('1'), 'minions': 32 * bin(int(mask, 16)).count('1'),
                   'ops_per_minion_pass': a['ops_per_minion_pass'], 'values': a['values'], 'gen': gen, 'tile_file': tfile,
                   'tile_name': tname, 'families': a.get('families', []), 'family': a.get('family'), 'priority': a.get('priority'),
                   'form': r.get('form'), 'unit': r.get('unit'), 'est_peak_w': r.get('est_peak_w'), 'est_s': r.get('est_s'),
                   'group_mask': 'FULL' if mask == FULL else 'SUB',
                   'case': f"{CARDS[ck]}|{marm if marm else tok}|{a['type']}|{kind}|{mask}"}
            if cl in ('CTRL', 'GAP', 'ANCHOR'):
                rec.update(MB=shape['MB'], NB=shape['NB'], KB=shape['KB'])
            if dom == 'OUT':
                rec['out_of_domain_measures'] = MEASURES[cl]
            out['runs'].append(rec)
R = out['runs']
cases = collections.OrderedDict()
for r in R:
    c = cases.setdefault(r['case'], {'case': r['case'], 'card': r['card'], 'arm': r['arm'], 'token': r['token'], 'fmt': r['fmt'],
                                     'kind': r['kind'], 'kind_energy': r['kind_energy'], 'mask': r['mask'], 'arm_label': r['arm_label'],
                                     'runs': [], 'domain': r['domain'], 'class': r['class'], 'group_mask': r['group_mask'],
                                     'families': r['families'], 'shape': r['shape'], 'kernel': r['kernel'],
                                     'ops_per_minion_pass': r['ops_per_minion_pass'], 'n_shires': r['n_shires']})
    if 'MB' in r:
        c.update(MB=r['MB'], NB=r['NB'], KB=r['KB'])
    assert c['ops_per_minion_pass'] == r['ops_per_minion_pass']
    c['runs'].append(r['id'])
out['cases'] = list(cases.values())
CC = out['cases']
out['counts'] = {'listed_runs (arm and anchor; nulls and smoke left out)': len(R), 'cases': len(cases),
                 'by_card': dict(collections.Counter(r['card'] for r in R)), 'by_fmt': dict(collections.Counter(r['fmt'] for r in R)),
                 'by_role': dict(collections.Counter(r['role'] for r in R)),
                 'by_domain': dict(collections.Counter(r['domain'] for r in R)),
                 'by_class': dict(collections.Counter(r['class'] for r in R)),
                 'by_kind': dict(collections.Counter(r['kind'] for r in R)),
                 'cases_by_card': dict(collections.Counter(c['card'] for c in CC)),
                 'cases_by_domain': dict(collections.Counter(c['domain'] for c in CC)),
                 'cases_by_class': dict(collections.Counter(c['class'] for c in CC)),
                 'cases_by_domain_card': dict(collections.Counter(f"{c['domain']}|{c['card']}" for c in CC)),
                 'cases_by_class_card': dict(collections.Counter(f"{c['class']}|{c['card']}" for c in CC)),
                 'cases_by_group_mask': dict(collections.Counter(c['group_mask'] for c in CC)),
                 'arms_listed': len({r['arm_label'] for r in R}), 'arms_in_arms_json': len(ARMS),
                 'tokens_in_domain': sorted({r['token'] for r in R if r['domain'] == 'IN' and r['class'] in ('CTAB', 'C16R')}),
                 'tokens_out_of_domain': sorted({r['token'] for r in R if r['domain'] == 'OUT'})}
out['arms_never_scheduled'] = sorted(set(ARMS) - {r['arm_label'] for r in R})
json.dump(out, open(os.path.join(OUTD, 'runs-listed.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps(out['counts'], indent=1, sort_keys=True)[:6000])
print('arms never scheduled (anchor/smoke-only or not run):', out['arms_never_scheduled'])
print(json.dumps({s: {k: v for k, v in d.items() if k in ('n_sched', 'roles', 'planned_min')} for s, d in out['sessions'].items()}))
print(sha(os.path.join(OUTD, 'runs-listed.json')), 'work/step1/runs-listed.json')
