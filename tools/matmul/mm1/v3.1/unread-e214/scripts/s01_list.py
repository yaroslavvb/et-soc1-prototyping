#!/usr/bin/env python3
"""unread-e214 (Q225) step 1a: E214's runs, listed from committed schedules, queues and the registered arms only.
NO measurement column is opened: per session it reads the registered schedule (tools/claims-v3/e214/proposal/src/sched/<s>.json), the
registered arms (arms.json) and, from GitHub main by `git show`, the committed session/queue.json (fields read: card, sched_sha256 and per
entry i, block, role, arm, run, form, ran, rc, check, checks, flags) and meta-e214-<s>.json (fields read: sid, card, schedule). No
data-e214-*.json, README, reduce, check or window file of E214 is opened here. Each run's model inputs (arm, format, kind, mask, card) come
from arms.json; its kind by MM1-v3's own data_v3.e212_kind regex (the arm's name), its energy kind as MM1-v3.1's data_v31 prices it
(pattern:sparse50f / pattern:sparse50i -> sparse50, and pattern:sparse50h too: counts-e214's finding 2, verify-counts-e214's fix).
Desk; no device. Run: /usr/bin/python3 -I -B s01_list.py <lane dir>
"""
import collections
import hashlib
import json
import os
import re
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
LAB = '<LAB>'
COMMIT = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
E214 = os.path.join(L, 'work', 'lab', 'tools', 'claims-v3', 'e214', 'proposal', 'src')
OUTD = os.path.join(L, 'work', 'step1')
os.makedirs(OUTD, exist_ok=True)
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')
SESSIONS = ['a1c0-S1', 'a1c0-S2', 'a1c0-S3', 'a1c1-S1', 'a1c1-S2', 'a1c1-S3', 'a1c1-S4']
CARDS = {'a1c1': 'aifoundry1 card 1', 'a1c0': 'aifoundry1 card 0'}
PRIMARY_VIEW = {'a1c1': 'band600', 'a1c0': 'win'}     # reduce_mms.py: "win" if the card is governed else "band600"
E212_KIND = {'rnd': 'random', 'zeros': 'zeros', 'ones': 'ones'}
SPARSE_GEN = {'pattern:sparse50f': 'sparse50', 'pattern:sparse50i': 'sparse50', 'pattern:sparse50h': 'sparse50'}


def gshow(path):
    return subprocess.run(['git', '-C', LAB, 'show', f'{COMMIT}:{path}'], check=True, capture_output=True, env=ENV).stdout


def e212_kind(arm):
    """MM1-v3's data_v3.e212_kind, the same regex"""
    m = re.fullmatch(r'\d+x\d+x\d+-(?:fp32|fp16|int8)-([A-Za-z0-9_]+?)(?:-(?:s\d+|m[0-9a-f]+))?', arm)
    if not m:
        return None
    k = m.group(1)
    return E212_KIND.get(k, 'pattern:' + k)


ARMSJ = json.load(open(os.path.join(E214, 'arms.json')))
ARMS = {a['id']: a for a in ARMSJ['arms']}
TILES = ARMSJ['tiles']
out = {'what': 'unread-e214 step 1a: E214 runs (schedules, queues, arms.json; no measurement column opened)', 'lab_commit': COMMIT,
       'python': sys.version.split()[0], 'runs': [], 'sessions': {}, 'notes': []}
nq = collections.Counter()
for s in SESSIONS:
    ck = s.split('-')[0]
    sched = json.load(open(os.path.join(E214, 'sched', f'{s}.json')))
    folder = f'docs/reports/data/2026-11-18-e214-mmsweep3-{s}'
    qraw = gshow(f'{folder}/session/queue.json')
    q = json.loads(qraw)
    meta = json.loads(gshow(f'{folder}/meta-e214-{s}.json'))
    assert q['card'] == ck, (s, q['card'])
    sched_bytes = open(os.path.join(E214, 'sched', f'{s}.json'), 'rb').read()
    sh = hashlib.sha256(sched_bytes).hexdigest()
    sr = {r['i']: r for r in sched['runs']}
    out['sessions'][s] = {'card': CARDS[ck], 'card_key': ck, 'folder': folder, 'sid': meta.get('sid'), 'meta_card': meta.get('card'),
                          'meta_schedule': meta.get('schedule'), 'queue_sched_sha256': q.get('sched_sha256'),
                          'registered_sched_sha256': sh, 'sched_equal': q.get('sched_sha256') == sh,
                          'queue_sha256': hashlib.sha256(qraw).hexdigest(), 'n_queue': len(q['queue']), 'n_sched': len(sched['runs']),
                          'primary_view': PRIMARY_VIEW[ck]}
    for e in q['queue']:
        nq[(s, e.get('role'))] += 1
        r = sr.get(e['i'])
        assert r is not None and r['arm'] == e['arm'] and r['role'] == e['role'], (s, e['i'], e['arm'])
        if e['arm'] is None or str(e['arm']).startswith('null') or e.get('role') in (None, 'null'):
            continue
        a = ARMS[e['arm']]
        assert a['values'] == r['values'] and a['shires'] == r['shires'] and a['type'] == r['type'], (s, e['arm'])
        m = re.match(r'gemmL(\d+)x(\d+)x(\d+):([a-z0-9]+):(\S+)$', a['values'])
        MB, NB, KB = (int(x) for x in m.groups()[:3])
        gen, tfile = m.group(4), m.group(5)
        kind = e212_kind(e['arm'])
        tname = os.path.splitext(os.path.basename(tfile))[0]
        rec = {'id': f"E214|{s}|{e['run']}", 'session': s, 'card': CARDS[ck], 'card_key': ck, 'i': e['i'], 'run': e['run'], 'block': e['block'],
               'role': e['role'], 'arm_label': e['arm'], 'arm': f'gemmL{MB}x{NB}x{KB}', 'MB': MB, 'NB': NB, 'KB': KB, 'kernel': 'rgm136',
               'fmt': a['type'], 'kind': kind, 'kind_energy': SPARSE_GEN.get(kind, kind), 'mask': a['shires'],
               'minions': 32 * bin(int(a['shires'], 16)).count('1'), 'ops_per_minion_pass': a['ops_per_minion_pass'],
               'values': a['values'], 'gen': gen, 'tile_file': tfile, 'tile_name': tname, 'families': a.get('families', []),
               'priority': a.get('priority'), 'form': e.get('form'), 'ran': e.get('ran'), 'rc': e.get('rc'), 'check': e.get('check'),
               'checks': e.get('checks'), 'flags': e.get('flags'), 'case': f"{CARDS[ck]}|gemmL{MB}x{NB}x{KB}|{a['type']}|{kind}|{a['shires']}"}
        assert rec['ops_per_minion_pass'] == MB * NB * 2 * KB * 32, rec['arm_label']
        out['runs'].append(rec)
R = out['runs']
out['counts'] = {'queue_entries_by_session_role': {f'{k[0]} {k[1]}': v for k, v in sorted(nq.items())},
                 'listed_runs (arm and anchor; nulls left out)': len(R), 'ran': sum(1 for r in R if r['ran']),
                 'not_ran': [r['id'] for r in R if not r['ran']], 'rc_nonzero': [r['id'] for r in R if r['ran'] and r['rc'] not in (0, None)],
                 'check_not_exact_or_approx': [r['id'] for r in R if r['ran'] and r['check'] not in ('exact', 'approx')],
                 'flags_nonempty': {r['id']: r['flags'] for r in R if r['flags']},
                 'by_card': dict(collections.Counter(r['card'] for r in R)), 'by_fmt': dict(collections.Counter(r['fmt'] for r in R)),
                 'by_kind': dict(collections.Counter(r['kind'] for r in R)), 'by_role': dict(collections.Counter(r['role'] for r in R)),
                 'arms_listed': len({r['arm_label'] for r in R}), 'cases': len({r['case'] for r in R})}
json.dump(out, open(os.path.join(OUTD, 'runs-listed.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps(out['counts'], indent=1, sort_keys=True)[:3000])
print(json.dumps({s: {k: v for k, v in d.items() if k in ('sid', 'sched_equal', 'n_queue', 'n_sched', 'meta_card')} for s, d in out['sessions'].items()}))
print(hashlib.sha256(open(os.path.join(OUTD, 'runs-listed.json'), 'rb').read()).hexdigest(), 'work/step1/runs-listed.json')
