#!/usr/bin/env python3
"""unread-e214 (Q225) step 2a: each listed run's CONDITIONS, the models' inputs, from the committed data-e214-<s>.json (GitHub main 8bde0182,
by `git show`). Reads ONLY (the declaration, section b): the top-level card, session and primary_view, and per run: run, i, ran, role, arm,
values, type, shires, minions, die_start_c, and the primary view's kclock_mhz and rails.minion.mV. No time, cycles, power, energy or seconds
field is read, printed or stored; each file's object is dropped after the extraction. Writes work/step2/conditions-e214.json.
Desk; no device. Run: /usr/bin/python3 -I -B s02a_conditions.py <lane dir>
"""
import hashlib
import json
import os
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
LAB = '<LAB>'
COMMIT = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')
OUTD = os.path.join(L, 'work', 'step2')
os.makedirs(OUTD, exist_ok=True)
RL = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
TOP = ('card', 'session', 'primary_view')
RUNF = ('run', 'i', 'ran', 'role', 'arm', 'values', 'type', 'shires', 'minions', 'die_start_c')
out = {'what': 'unread-e214 step 2a: conditions only (clock, minion volts, die at start) and identity fields', 'lab_commit': COMMIT,
       'fields_read': {'top': list(TOP), 'run': list(RUNF), 'primary_view': ['kclock_mhz', 'rails.minion.mV']}, 'sessions': {}, 'runs': {}}
by_s = {}
for r in RL['runs']:
    by_s.setdefault(r['session'], []).append(r)
for s, rs in sorted(by_s.items()):
    path = f"{RL['sessions'][s]['folder']}/data-e214-{s}.json"
    raw = subprocess.run(['git', '-C', LAB, 'show', f'{COMMIT}:{path}'], check=True, capture_output=True, env=ENV).stdout
    h = hashlib.sha256(raw).hexdigest()
    Dj = json.loads(raw)
    del raw
    top = {k: Dj.get(k) for k in TOP}
    pv = top['primary_view']
    ext = {}
    for r in Dj['runs']:
        rec = {k: r.get(k) for k in RUNF}
        v = (r.get('views') or {}).get(pv) or {}
        rec['kclock_mhz'] = v.get('kclock_mhz')
        rec['minion_mV'] = ((v.get('rails') or {}).get('minion') or {}).get('mV')
        rec['has_primary_view'] = bool(v)
        assert rec['run'] not in ext, (s, rec['run'])
        ext[rec['run']] = rec
    del Dj
    out['sessions'][s] = {'file': path, 'sha256': h, **top, 'expected_primary_view': RL['sessions'][s]['primary_view'],
                          'n_runs_in_file': len(ext)}
    assert pv == RL['sessions'][s]['primary_view'], (s, pv)
    assert top['card'] == RL['sessions'][s]['card_key'], (s, top['card'])
    for r in rs:
        c = ext.get(r['run'])
        assert c is not None, (s, r['run'])
        assert c['arm'] == r['arm_label'] and c['values'] == r['values'] and c['type'] == r['fmt'] and c['shires'] == r['mask'], (s, r['run'])
        assert c['role'] == r['role'], (s, r['run'])
        out['runs'][r['id']] = {'kclock_mhz': c['kclock_mhz'], 'minion_mV': c['minion_mV'], 'die_start_c': c['die_start_c'],
                                'ran': c['ran'], 'minions': c['minions'], 'has_primary_view': c['has_primary_view'], 'session_label': top['session']}
miss = [k for k, v in out['runs'].items() if v['kclock_mhz'] is None]
out['summary'] = {'runs': len(out['runs']), 'without_a_clock': miss, 'without_minion_mV': [k for k, v in out['runs'].items() if v['minion_mV'] is None],
                  'without_die_start': [k for k, v in out['runs'].items() if v['die_start_c'] is None]}
json.dump(out, open(os.path.join(OUTD, 'conditions-e214.json'), 'w'), indent=1, sort_keys=True)
print(json.dumps({s: {k: v for k, v in d.items() if k != 'file'} for s, d in out['sessions'].items()}))
print('runs', len(out['runs']), 'without a clock', len(miss), 'without minion mV', len(out['summary']['without_minion_mV']),
      'without die start', len(out['summary']['without_die_start']))
print(hashlib.sha256(open(os.path.join(OUTD, 'conditions-e214.json'), 'rb').read()).hexdigest(), 'work/step2/conditions-e214.json')
