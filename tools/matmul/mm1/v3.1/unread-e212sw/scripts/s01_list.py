#!/usr/bin/env python3
"""unread-e212sw (Q218) step 1a: the runs, listed from committed schedules, queues and registration point files only.
NO measurement column is opened: per E212 session it reads the registered schedule (tools/claims-v3/e212/proposal/src/sched/<s>.json),
the registered arms (arms.json) and the committed session/queue.json (fields i, block, role, arm, run, form, ran, rc, check, flags);
for E206 and E207 the registration point files vendored in MM1-v3 (points-e206.json, points-e207.json) and each committed data folder's
session/queue.json (fields n, block, id, name, arm, run, ran, n_procs, rcs, flags). MM1-v3's counts() and phi_of() (work copy of GitHub main,
unchanged since b1493082) say which kinds it could not price; the frozen counts (work/counts, SHA256SUMS c74c2d49...) say which now have a row.
Desk; no device. Run: /usr/bin/python3 -I -B s01_list.py <lane dir>
"""
import json
import os
import re
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
LAB = '<LAB>'
COMMIT = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
V3 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v3')
E212 = os.path.join(L, 'work', 'lab', 'tools', 'claims-v3', 'e212', 'proposal', 'src')
CNT = os.path.join(L, 'work', 'counts')
sys.path.insert(0, V3)
import energy_v3 as EN  # noqa: E402

ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')
SESSIONS = ['a1c0-S1', 'a1c0-S2', 'a1c1-S1', 'a1c1-S2', 'a1c1-S3', 'a1c1-S4', 'a2c0-S1', 'a2c0-S2', 'a2c0-S4']   # the nine committed
CARDS = {'a1c1': 'aifoundry1 card 1', 'a1c0': 'aifoundry1 card 0', 'a2c0': 'aifoundry2 card 0', 'a3': 'aifoundry3 card 0'}
E212_KIND = {'rnd': 'random', 'zeros': 'zeros', 'ones': 'ones'}
C32 = json.load(open(os.path.join(CNT, 'counts-fp32-gemm-states.json')))['shapes']
C16 = json.load(open(os.path.join(CNT, 'counts-fp16-int8-launch.json')))['rows']


def gshow(path):
    return subprocess.run(['git', '-C', LAB, 'show', f'{COMMIT}:{path}'], check=True, capture_output=True, env=ENV).stdout


def e212_kind(arm):
    """MM1-v3's data_v3.e212_kind, the same regex"""
    m = re.fullmatch(r'\d+x\d+x\d+-(?:fp32|fp16|int8)-([A-Za-z0-9_]+?)(?:-(?:s\d+|m[0-9a-f]+))?', arm)
    if not m:
        return None
    k = m.group(1)
    return E212_KIND.get(k, 'pattern:' + k)


def new_row(fmt, kind, KB):
    if fmt == 'fp32':
        return kind in C32['S1' if KB == 1 else 'S2']
    return f'{fmt}.{kind}' in C16


def v3_status(fmt, kind, KB):
    c = EN.counts(fmt, kind, KB)
    p = EN.phi_of(fmt, kind, KB)
    return {'v3_count': c is not None, 'v3_phi': p is not None}


ARMS = {a['id']: a for a in json.load(open(os.path.join(E212, 'arms.json')))['arms']}
out = {'what': 'unread-e212sw step 1a: the runs (from schedules, queues and point files; no measurement column opened)',
       'lab_commit': COMMIT, 'python': sys.version.split()[0], 'e212': [], 'e212_refs': [], 'e206_e207': [], 'notes': []}
seen_kinds = {}
for s in SESSIONS:
    ck = s.split('-')[0]
    sched = json.load(open(os.path.join(E212, 'sched', f'{s}.json')))
    folder = f'docs/reports/data/2026-11-17-e212-mmsweep2-{s}'
    q = json.loads(gshow(f'{folder}/session/queue.json'))
    assert q['card'] == ck, (s, q['card'])
    byrun = {e['run']: e for e in q['queue']}
    sr = {r['i']: r for r in sched['runs']}
    cfg_runs = {}
    for e in q['queue']:
        if e['arm'] is None or str(e['arm']).startswith('null') or e.get('role') in (None, 'null'):
            continue
        a = ARMS.get(e['arm'])
        r = sr.get(e['i'])
        assert r is not None and r['arm'] == e['arm'], (s, e['i'], e['arm'])
        m = re.match(r'gemmL(\d+)x(\d+)x(\d+):', a['values'])
        MB, NB, KB = (int(x) for x in m.groups())
        kind = e212_kind(e['arm'])
        rec = {'session': s, 'card': CARDS[ck], 'card_key': ck, 'i': e['i'], 'run': e['run'], 'arm_label': e['arm'], 'arm': f'gemmL{MB}x{NB}x{KB}',
               'KB': KB, 'fmt': a['type'], 'kind': kind, 'mask': a['shires'], 'role': e['role'], 'block': e['block'], 'form': e['form'],
               'ran': bool(e['ran']), 'rc': e['rc'], 'check': e['check'], 'flags': e['flags'], 'values': a['values']}
        cfg = (rec['arm'], rec['fmt'], rec['mask'])
        cfg_runs.setdefault(cfg, []).append(rec)
        if kind and kind.startswith('pattern:'):
            name = kind.split(':', 1)[1]
            st = v3_status(rec['fmt'], kind, KB)
            if name in ('sparse50f', 'sparse50i'):
                grp = 'C'   # E212's gen sparse50 arms: the committed sparse50 kind (the counts lane's reading); v3 read them for time only
                rec['priced_as'] = 'sparse50'
            elif new_row(rec['fmt'], kind, KB):
                grp = 'A'
                rec['priced_as'] = kind
            else:
                grp = 'none'
                rec['priced_as'] = None
            rec.update(st)
            rec['group'] = grp
            rec['new_count_row'] = new_row(rec['fmt'], kind, KB)
            out['e212'].append(rec)
            seen_kinds[(rec['fmt'], kind)] = grp
    # the references at each test configuration in this session: random, zeros, ones
    tcfg = {(r['arm'], r['fmt'], r['mask']) for r in out['e212'] if r['session'] == s}
    for cfg in sorted(tcfg):
        for rec in cfg_runs.get(cfg, []):
            if rec['kind'] in ('random', 'zeros', 'ones'):
                out['e212_refs'].append(rec)

# E206 (arm A aifoundry3, arm B aifoundry1 card 1) and E207 (aifoundry3): the points MM1-v3 left unpriced in energy
P206 = {p['id']: p for p in json.load(open(os.path.join(V3, 'inputs', 'v2', 'v1', 'points-e206.json')))['points']}
P207 = {p['id']: p for p in json.load(open(os.path.join(V3, 'inputs', 'e207', 'points-e207.json')))['points']}
FOLD = {('E206', 'A'): ('2026-11-16-e206-matmul-sweep-aifoundry3', 'a3', P206),
        ('E206', 'B'): ('2026-11-17-e206-matmul-sweep-aifoundry1-c1', 'a1c1', P206),
        ('E207', 'A'): ('2026-11-17-e207-blind-matmul-aifoundry3', 'a3', P207)}
for (exp, arm), (folder, ck, P) in FOLD.items():
    q = json.loads(gshow(f'docs/reports/data/{folder}/session/queue.json'))
    runs = {}
    for e in q['queue']:
        runs.setdefault(e['id'], []).append({'run': e['run'], 'block': e['block'], 'ran': str(e['ran']) == 'True', 'rcs': e['rcs'],
                                             'name': e['name'], 'flags': e['flags']})
    for pid, p in sorted(P.items()):
        if exp == 'E206' and not (p.get('on_arm') or {}).get(arm):
            continue
        if p['kind'] in ('random', 'zeros', 'ones', 'sparse50'):
            continue
        m = re.fullmatch(r'gemmL(\d+)x(\d+)x(\d+)', p['arm'])
        KB = int(m.group(3))
        st = v3_status(p['format'], p['kind'], KB)
        if st['v3_count'] and st['v3_phi']:
            continue
        nr = new_row(p['format'], p['kind'], KB)
        grp = 'A' if (not st['v3_count'] and nr) else ('B' if (st['v3_count'] and not st['v3_phi']) else 'none')
        refs = {}
        for rid, rp in P.items():
            if exp == 'E206' and not (rp.get('on_arm') or {}).get(arm):
                continue
            if (rp['arm'], rp['format'], rp['shire_mask']) == (p['arm'], p['format'], p['shire_mask']) and rp['kind'] in ('random', 'zeros', 'ones'):
                refs.setdefault(rp['kind'], []).append(rid)
        out['e206_e207'].append({'exp': exp, 'exp_arm': arm, 'card': CARDS[ck], 'point': pid, 'arm': p['arm'], 'KB': KB, 'fmt': p['format'],
                                 'kind': p['kind'], 'mask': p['shire_mask'], 'minions': p['minions'], 'values': p['values'], 'group': grp,
                                 'new_count_row': nr, **st, 'runs': runs.get(pid, []), 'refs': refs,
                                 'ref_runs': {k: {rid: runs.get(rid, []) for rid in v} for k, v in refs.items()}})

# summaries
def cnt(rs, key):
    d = {}
    for r in rs:
        d[r[key]] = d.get(r[key], 0) + 1
    return d


A = [r for r in out['e212'] if r['group'] == 'A']
C = [r for r in out['e212'] if r['group'] == 'C']
out['summary'] = {
    'e212_pattern_runs_scheduled_in_committed_sessions': len(out['e212']),
    'e212_group_A_runs': len(A), 'e212_group_A_ran': sum(r['ran'] for r in A),
    'e212_group_A_by_session': cnt(A, 'session'), 'e212_group_A_by_role': cnt(A, 'role'),
    'e212_group_C_runs': len(C), 'e212_group_C_ran': sum(r['ran'] for r in C),
    'e212_kinds': {f'{k[0]} {k[1]}': g for k, g in sorted(seen_kinds.items())},
    'e212_none_group': [r['run'] for r in out['e212'] if r['group'] == 'none'],
    'e212_any_v3_count': [r['run'] for r in out['e212'] if r['v3_count']],
    'e206_e207_points': {g: [f"{x['exp']}{x['exp_arm']}|{x['point']}" for x in out['e206_e207'] if x['group'] == g] for g in ('A', 'B', 'none')},
    'e212_refs': len(out['e212_refs'])}
json.dump(out, open(os.path.join(L, 'work', 'step1', 'runs-listed.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps(out['summary'], indent=1, sort_keys=True))
