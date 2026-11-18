#!/usr/bin/env python3
"""fix-unread-e212sw (Q218), ADDENDUM 1, step A1: THE ADDENDUM'S DECLARATION, POST HOC (after the unread lane's read, after the verifier scored
these points), written before this lane opens any measurement of them.

verify-unread-e212sw's finding 1: by the declaration's own rule (section a: committed runs whose kind MM1-v3 left NOT FORECAST in energy for
want of a count, and which now have one; group B: count committed, phi missing), E209's three real points belong in the test: e35 (int8) and
e36 (fp16) in group A, e34 (fp32) in group B. They ran on aifoundry2 card 0 under its governor with E206's real2 tiles. This script lists them
from the registration alone (MM1-v3's vendored e209_points.csv, E209's registered schedule box/a2c0-E209.json, the tile files), checks what
MM1-v3 as landed returns for their kind, checks their tile bytes against the files the declared phi rule and the frozen counts read, names the
references the share of D would need, and writes the addendum's rule. No data file of E209 is opened here.
Run: /usr/bin/python3 -I -B a01_declare_e209.py
"""
import csv
import hashlib
import json
import os
import sys
import time

W = '<W>'
ME = os.path.join(W, 'out', 'fix-unread-e212sw')
WL = os.path.join(ME, 'work', 'lab')
V3 = os.path.join(WL, 'tools', 'matmul', 'mm1', 'v3')
CNT = os.path.join(WL, 'tools', 'matmul', 'mm1', 'v3.1', 'counts')
LANDU = os.path.join(W, 'out', 'unread-e212sw', 'land', 'tools', 'matmul', 'mm1', 'v3.1', 'unread-e212sw')
OUTD = os.path.join(ME, 'work', 'addendum')
os.makedirs(OUTD, exist_ok=True)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def ts():
    return time.strftime('%a %d %b %Y %H:%M:%S %Z', time.localtime())


DECL_P = os.path.join(LANDU, 'declared-unread.json')
assert sha(DECL_P) == '5eb2c93d2d60640347bdd6f827f2800cccb6bfd96ea6744f8e5036839a4c03cc'
assert sha(os.path.join(CNT, 'SHA256SUMS')) == 'c74c2d49c336159f6ca63aad2652601a10e22d6a8b5db00d46c66bfb1cf8aa7f'
DECL = json.load(open(DECL_P))
PHI = DECL['e_phi']['values']
sys.path.insert(0, V3)
import energy_v3 as EN  # noqa: E402
import engine_v3 as E  # noqa: E402
import kinds_v3 as K  # noqa: E402

PTS = {r['id']: r for r in csv.DictReader(open(os.path.join(V3, 'inputs', 'e209', 'e209_points.csv')))}
REGP = {r['id']: r for r in csv.DictReader(open(os.path.join(WL, 'tools', 'claims-v3', 'e209', 'points-e209.csv')))}
SCHED = json.load(open(os.path.join(WL, 'tools', 'claims-v3', 'e209', 'box', 'a2c0-E209.json')))
C32 = json.load(open(os.path.join(CNT, 'counts-fp32-gemm-states.json')))['shapes']
C16 = json.load(open(os.path.join(CNT, 'counts-fp16-int8-launch.json')))['rows']
card = 'aifoundry2 card 0'
points = []
for pid in ('e34', 'e35', 'e36'):
    p = PTS[pid]
    assert p['kind'] == 'real' and p['mask'] == '0xffffffff', p
    fmt, arm = p['fmt'], p['arm']
    KB = E.arm_parts(arm)[1][2]
    # what MM1-v3 as landed returns for the kind (before any row is added)
    cnt0 = EN.counts(fmt, 'real', KB)
    phi0 = EN.phi_of(fmt, 'real', KB)
    group = 'A' if cnt0 is None else ('B' if phi0 is None else 'out of scope (priced by MM1-v3 as landed)')
    # the registered tiles: E209's values string against E206's real2 files (the files the declared phi rule and the counts read)
    tiles = p['values'].split(':tiles:')[1].split(',')
    names = [os.path.basename(t)[:-4] for t in tiles]
    assert names == K.E206_REAL[fmt], (pid, names, K.E206_REAL[fmt])
    tsha = {}
    for t, nm in zip(tiles, names):
        a = sha(os.path.join(WL, t))
        b = sha(os.path.join(K.INP, 'tiles', f'real2__{fmt}__{nm}.bin'))   # the folder kinds_v3.phi reads (inputs/v2/v1)
        tsha[nm] = {'e209_registered_file': a, 'mm1_v3_vendored_real2_file': b, 'equal': a == b}
        if fmt in ('fp16', 'int8'):
            tsha[nm]['frozen_counts_row_' + f'{fmt}.real'] = C16[f'{fmt}.real']['tiles_sha256'][nm + '.bin']
            tsha[nm]['equal_to_counts'] = C16[f'{fmt}.real']['tiles_sha256'][nm + '.bin'] == a
    assert all(v['equal'] for v in tsha.values()), tsha
    assert all(v.get('equal_to_counts', True) for v in tsha.values()), tsha
    # the frozen counts' row for the kind (fp16/int8: the launch-point row; fp32: E210's committed 'real' row, already in MM1-v3)
    if fmt == 'fp32':
        row_src = 'E210C (committed with MM1-v3: E210\'s calibration kind real)'
        assert cnt0 is not None
    else:
        row_src = f'frozen counts (c74c2d49) counts-fp16-int8-launch.json rows[{fmt}.real]'
        assert f'{fmt}.real' in C16
    runs = [{'i': r['i'], 'arm_label': r['arm'], 'role': r['role'], 'type': r['type'], 'shires': r['shires'], 'values': r['values']}
            for r in SCHED['runs'] if r['arm'] == pid]
    assert len(runs) == int(p['runs_planned']), (pid, len(runs))
    assert all(r['values'] == p['values'] for r in runs)
    refs = {k: sorted(q['id'] for q in PTS.values() if (q['arm'], q['fmt'], q['mask']) == (arm, fmt, p['mask']) and q['kind'] == k)
            for k in ('random', 'zeros')}
    points.append({'id': f'E209|{pid}', 'point': pid, 'card': card, 'arm': arm, 'KB': KB, 'fmt': fmt, 'kind': 'real', 'priced_as': 'real',
                   'mask': p['mask'], 'family': p['family'], 'runs_registered': runs, 'group': group,
                   'mm1_v3_as_landed': {'counts': None if cnt0 is None else list(cnt0), 'phi_of': phi0},
                   'count_row': row_src, 'phi_rule_value': float(PHI[f'{fmt}|real']), 'tiles_sha256': tsha,
                   'refs_same_configuration_in_E209': refs,
                   'share_of_D': 'NOT SCORED (no zeros point at this configuration in E209)' if not refs['zeros'] else 'scored'})
    assert REGP[pid]['arm'] == arm and REGP[pid]['fmt'] == fmt

decl = {
    'what': ('fix-unread-e212sw ADDENDUM 1 (POST HOC), step A1: E209\'s three real points, missed by the declared run list (verify-unread-e212sw '
             'finding 1), declared before this lane opens any E209 measurement'),
    'made_pst': ts(), 'interpreter': sys.version.split()[0],
    'label': ('POST HOC and UNREAD: added after the unread lane\'s read (06:59:15 PST) and after verify-unread-e212sw scored these points (its '
              'v06_e209.py, about 07:30 PST); MM1-v3 (b1493082) and the counts (c74c2d49) were frozen before any lane read these runs for this '
              'test. Not blind: E209\'s data, verify and scoring lanes read them, MM1-v3\'s design lane v3-design-a tabulated MM1-v2\'s J-over-idle '
              'error at all 45 E209 points (these three included), and this round\'s verifier scored them first.'),
    'declaration_of_record': {'DECLARED-unread.md': 'f1daf832cc0078ef8fe90d108ce646cd3d656ca96634928deb2cfe6787aae44f',
                              'declared-unread.json': '5eb2c93d2d60640347bdd6f827f2800cccb6bfd96ea6744f8e5036839a4c03cc',
                              'unchanged': True},
    'rule': ('The declaration\'s rules apply unchanged (sections b-f): Q1 W over idle given the measured seconds at the run\'s measured clock, '
             'minion volts (else volts(card, f)), governed base G_of_f and die at start (50 C when absent), error = W_fc / W_meas - 1 at '
             'W_meas >= 3 W; Q2 the share of D needs in-session random and zeros at the same (arm, format, mask): none of the three has a zeros point '
             'in E209, so Q2 is NOT SCORED; Q3 (J at rest given t) and Q4 (J over idle with the seconds forecast) REPORTED. Energy inclusion: '
             'data_v3.mms_runs\'s own rule (the run ran, has a role, the primary view has T_op_us, cyc_op_max, n_launch >= 1; energy when dP_w and '
             'p_mean_w are present, not capped, role not time), the energy condition widened to these runs. The case is the point (the mean of its '
             'runs\' errors). Models: V3 (MM1-v3 unchanged, the frozen counts as table rows, phi by rule e), N, N2, V3phi1, as declared; V1 not '
             'computed (a governed card: no V1 test point there, as the declaration did for aifoundry2). Groups by the declaration\'s own rule: '
             'e35 and e36 in group A (no count in MM1-v3 as landed, a count now), e34 in group B (count committed, no phi).'),
    'verdict_of_record': ('PASS, decided by scripts/s03_score.py on the declared list (59 entries; P1-P4 against N). This addendum changes no '
                          'declared number. It REPORTS, post hoc, the pass rule\'s Q1 conditions (P1, P2) re-run with e35 and e36 added to group '
                          'A\'s 42 Q1 cases (Q2\'s 29 cases are unchanged: no E209 case has a share of D), and group B with e34 added.'),
    'points': points,
}
p = os.path.join(OUTD, 'addendum-declared-e209.json')
json.dump(decl, open(p, 'w'), indent=1, sort_keys=True)
print('A1 written', decl['made_pst'], 'addendum-declared-e209.json', sha(p))
for q in points:
    print(q['id'], q['fmt'], q['arm'], 'KB', q['KB'], 'group', q['group'], 'MM1-v3 counts', 'none' if q['mm1_v3_as_landed']['counts'] is None else 'yes',
          'phi_of', q['mm1_v3_as_landed']['phi_of'], 'phi rule', q['phi_rule_value'], 'runs i', [r['i'] for r in q['runs_registered']],
          'refs', q['refs_same_configuration_in_E209'], 'tiles equal', all(v['equal'] for v in q['tiles_sha256'].values()))
