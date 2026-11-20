#!/usr/bin/env python3
"""MM1-v3.2's blind day E218 (DECLARED-v32.md section 9): the never-run scan, the point rule (families G with its twins Gt, Y, F) on the
landed MM1-v3.2, and every declared model's forecasts of the chosen points, hashed. aifoundry3 card 0 at its pinned 600 MHz. Desk; no card.

    /usr/bin/python3 -I -B e218_v32.py scan --lab <the lab at GitHub main> --lanes <W/out> --out <dir> [--e216-points <points-e216.csv>]
    /usr/bin/python3 -I -B e218_v32.py choose --scan <scan-e218.json> --fit <the fit's out dir> --out <dir>

THE SCAN: E215's scanner's scan (tools/claims-v3/e215/desk/neverrun_e215.py, with E213's neverrun_e213.py imported at its pin: its token rule,
  roots, folder classes and reader) with three named changes: (1) E218's own folders subtracted ('-e218-', W/out/card-e218*) in place of
  E215's (E215 has run: its folders count); (2) the measured points are MM1-v3.2's (data_v32: every point MM1-v3.2 read, E214 and E215
  among them); (3) THIS LANE OPENS NO E216 OR E217 DATA FILE (DECLARED-v32.md section 4): their committed data folders ('-e216-', '-e217-')
  and round lane folders (card-/data- lanes naming e216 or e217) are not read; in their place what their committed registrations name is
  counted as run: E216's registered points on aifoundry2 card 0 (the class the scanner's folder rule gives E216's data folder and its card
  lane at GitHub main, both naming that card), and every shape token E217's registered schedules and arms name on EVERY card at EVERY mask
  (class 'no card named', mask 'any': the scanner counts a lane file whose path names no card for every card, and W/out/data-e217 holds
  such files). Fixed by fix-fit-v32 after verify-fit-v32's finding: fit-v32 counted E217's registration on aifoundry1 only, which is not
  a superset of the literal scan's reading. Even so this is a stand-in, not the literal scan: it covers what the two registrations name,
  not any other token those unread folders may name. The S-family tile reading of E215's scanner is not made (E218 has no S family).
  E218's registration re-runs the declared scan literally (DECLARED-v32.md sections 9.1 and 10: E218's points are decided there), and the
  card lane repeats it (step 6n).
THE POINT RULE: section 9 (its docstring is in DECLARED-v32.md); the readings this file applies where the text leaves one open are named in
  choose()'s output ('readings').
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import ast
import collections
import copy
import csv
import datetime
import hashlib
import importlib.util
import json
import math
import os
import random
import re
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
V31 = os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3.1')
V3 = os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3')
TERMS = os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3.2-terms')
A3 = 'aifoundry3 card 0'
FULLM = '0xffffffff'
FULL = 0xFFFFFFFF
F_MHZ = 600.0
LINE = 67.0
KBLK = {'fp32': 512, 'fp16': 1024, 'int8': 2048}
G_MB = tuple(range(1, 9))
G_NB = (1, 2, 3, 5, 6, 12, 13, 14, 15)
G_KB = (1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48)
G_QUOTA = {'L2': 2, 'NB1-3': 4, 'NB5-6': 3, 'NB12-15': 3}
G_ORDER = ('L2', 'NB5-6', 'NB12-15', 'NB1-3')
Y_MB, Y_NB, Y_KB = (1, 2, 4), (2, 4, 8, 16), (4, 8, 12, 16, 24)
Y_MASKS = {2: ('0x3', '0x5', '0x11', '0x101', '0x10001', '0x1000001'), 4: ('0xf', '0x33', '0x1111', '0x3030', '0xf000', '0x1010101'),
           8: ('0xff', '0xf0f', '0x3333', '0x5555', '0xff0000', '0x11111111'),
           16: ('0xffff', '0xff00ff', '0xf0f0f0f', '0x33333333', '0x55555555', '0xffff0000')}
F_MB, F_NB, F_KB = tuple(range(1, 17)), tuple(range(1, 17)), (1, 2, 3, 4, 6, 8, 12, 16, 24, 32)
F_QUOTA = (('fp32', 4), ('fp16', 5), ('int8', 5))
LAYOUT_CANDS = ('none', 'N3', 'N1+N2', 'G1', 'G1+N1', 'F1', 'fresh24')
LAYOUT_COLS = {'none': [], 'N3': ['N3'], 'N1+N2': ['N1', 'N2'], 'G1': ['G1'], 'G1+N1': ['G1', 'N1'], 'F1': ['fresh32'], 'fresh24': ['fresh24']}
A_FRESH_POSTED = -0.08316593007433395
SHAPE = re.compile(r'^gemmL(?:nc|n)?(\d+)x(\d+)x(\d+)$')
TIE_REL = 1e-12


def now():
    return datetime.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tok(pre, s):
    return '%s%dx%dx%d' % (pre, s[0], s[1], s[2])


def shape_of(arm):
    m = SHAPE.match(arm)
    return tuple(int(x) for x in m.groups()) if m else None


def wait_load(limit=6.0):
    """THE CPU RULE: wait in bounded 30 s chunks while the 1-minute load is above 6"""
    while True:
        try:
            if float(open('/proc/loadavg').read().split()[0]) <= limit:
                return
        except OSError:
            return
        time.sleep(30)


# ================================================================================================ the scan
def e216_e217_named(rel):
    """a data folder or round lane folder of E216 or E217 (not read by this lane: DECLARED-v32.md section 4)"""
    return bool(re.search(r'-e21[67]-', rel) or re.match(r'W/out/[^/]*e21[67]', rel))


def scan(lab, lanes, out, e216_points=None):
    NR = load_module('neverrun_e215_frozen', os.path.join(lab, 'tools', 'claims-v3', 'e215', 'desk', 'neverrun_e215.py'))
    N = NR.e213_module()
    t0 = now()
    expmap = N.exp_cards(lab)
    roots = [os.path.join(lab, 'docs', 'reports', 'data'), os.path.join(lab, 'tools', 'claims-v3', 'e212', 'proposal', 'src', 'sched'),
             os.path.join(lab, 'tools', 'claims-v3', 'e208', 'proposal', 'src')]
    lane_roots = sorted(os.path.join(lanes, d) for d in os.listdir(lanes) if d.startswith(('card-', 'data-', 'a1', 'a2', 'a3')))
    hits, masks = {}, {}
    nfiles, big, unreadable, git_dirs, not_read = 0, [], 0, 0, collections.Counter()

    def subtracted(rel):
        return ('-e218-' in rel) or rel.startswith('W/out/card-e218')

    def add(txt, rel, c):
        found = set(N.RX.findall(txt))
        if not found:
            return
        fm = sorted({'0x%x' % int(m, 16) for m in NR.MRX.findall(txt)})
        for t in found:
            hits.setdefault(t, {}).setdefault(c, []).append(rel)
            masks.setdefault(t, {}).setdefault(c, set()).update(fm)
    for top in roots + lane_roots:
        for dp, dn, fns in os.walk(top):
            if '.git' in dn or '.git' in fns:
                dn[:] = []
                git_dirs += 1
                continue
            dn.sort()
            reld = os.path.relpath(dp, lab) if dp.startswith(lab + os.sep) else 'W/out/' + os.path.relpath(dp, lanes)
            if e216_e217_named(reld + '/'):
                not_read[reld.split('/')[3] if reld.startswith('docs/reports/data/') else reld.split('/')[2]] += len(fns)
                continue
            for fn in sorted(fns):
                p = os.path.join(dp, fn)
                if fn.endswith(N.SKIP_EXT) or os.path.islink(p):
                    continue
                try:
                    if os.path.getsize(p) > N.MAX_BYTES:
                        big.append(p)
                        continue
                    txt = N.read_text(p)
                except (OSError, EOFError):
                    unreadable += 1
                    continue
                nfiles += 1
                rel = os.path.relpath(p, lab) if p.startswith(lab + os.sep) else 'W/out/' + os.path.relpath(p, lanes)
                c = 'SUBTRACTED' if subtracted(rel) else (N.lane_card(rel) or N.folder_card(rel, expmap) or N.NONE)
                add(txt, rel, c)
    # E216's and E217's registered configurations, counted as run on their cards (conservative), never their data
    reg = {'E216': [], 'E217': []}
    if e216_points and os.path.exists(e216_points):
        rows = list(csv.DictReader(open(e216_points)))
        for r in rows:
            arm = r.get('arm') or r.get('arm_token')
            mk = r.get('mask') or r.get('shire_mask') or FULLM
            txt = f'{arm}:{mk}'
            add(f'{arm} {mk}', 'E216 registration: ' + os.path.basename(e216_points), 'aifoundry2 card 0')
            reg['E216'].append(txt)
        relp = (os.path.relpath(e216_points, lab) if os.path.abspath(e216_points).startswith(lab + os.sep)
                else 'W/out/' + os.path.relpath(e216_points, lanes))
        reg['E216_source'] = {'path': relp, 'sha256': sha(e216_points), 'rows': len(rows)}
    else:
        reg['E216_source'] = {'path': None, 'present': False}
    e217 = os.path.join(lab, 'tools', 'claims-v3', 'e217', 'proposal', 'src')
    if os.path.isdir(e217):
        files = []
        e217_tokens = set()
        for dp, dn, fns in os.walk(e217):
            dn.sort()
            for fn in sorted(fns):
                if fn.endswith('.json'):
                    p = os.path.join(dp, fn)
                    txt = N.read_text(p)
                    rel = os.path.relpath(p, lab)
                    # fix-fit-v32: every token E217's registration names counts for every card ('no card named') at every mask ('any')
                    for t in set(N.RX.findall(txt)):
                        hits.setdefault(t, {}).setdefault(N.NONE, []).append(rel)
                        masks.setdefault(t, {}).setdefault(N.NONE, set()).add('any')
                        e217_tokens.add(t)
                    files.append(rel)
        reg['E217_source'] = {'files': files, 'n': len(files), 'tokens': len(e217_tokens),
                              'counted_as': "run on every card ('no card named') at every mask ('any')"}
    sys.path.insert(0, HERE)
    import data_v32 as DV  # noqa: E402
    meas_tok, meas_cfg = {}, {}
    for p in DV.time_points() + DV.energy_points():
        meas_tok.setdefault(p['arm'], set()).add((p['kernel'], p['card']))
        meas_cfg.setdefault(p['arm'], {}).setdefault(p['card'], set()).add('0x%x' % int(p['mask'], 16))
    rec = {'what': ("E218's never-run scan: E215's scanner's scan (E213's token rule, roots, folder classes and reader, imported at its pin) "
                    "with E218's own folders subtracted, MM1-v3.2's measured points, and E216's and E217's data unread (in their place E216's "
                    "registered points counted as run on aifoundry2 card 0 and every token E217's registration names counted as run on every "
                    "card at every mask: a stand-in for the literal scan, which E218's registration runs)"),
           'neverrun_e215_sha256': sha(os.path.join(lab, 'tools', 'claims-v3', 'e215', 'desk', 'neverrun_e215.py')),
           'neverrun_e213_sha256': NR.E213_SCAN[1], 'started': t0, 'ended': now(), 'files_read': nfiles,
           'roots': [os.path.relpath(r, lab) for r in roots], 'lane_roots': ['W/out/' + os.path.basename(r) for r in lane_roots],
           'not_read_e216_e217_files_by_folder': dict(not_read), 'registrations_counted': reg,
           'over_400MB_not_read': [os.path.relpath(p, lanes) if p.startswith(lanes) else os.path.relpath(p, lab) for p in big],
           'unreadable': unreadable, 'git_dirs_not_read': git_dirs,
           'tokens': {t: {c: {'n': len(v), 'files': sorted(set(v))[:6]} for c, v in sorted(cs.items())} for t, cs in sorted(hits.items())},
           'masks_by_card': {t: {c: sorted(v) for c, v in sorted(cs.items())} for t, cs in sorted(masks.items())},
           'mm1_v32_measured_tokens': {t: sorted(f'{k} on {c}' for k, c in v) for t, v in sorted(meas_tok.items())},
           'mm1_v32_measured_masks': {t: {c: sorted(v) for c, v in sorted(cs.items())} for t, cs in sorted(meas_cfg.items())},
           'data_v32_sha256': sha(os.path.join(HERE, 'data_v32.py'))}
    os.makedirs(out, exist_ok=True)
    pth = os.path.join(out, 'scan-e218.json')
    json.dump(rec, open(pth, 'w'), indent=1, sort_keys=True)
    print(f"scan: {nfiles} files read, {len(hits)} distinct tokens, E216/E217 files not read {sum(not_read.values())}, "
          f"{len(big)} over 400 MB, {unreadable} unreadable, {git_dirs} git dirs; {t0} - {rec['ended']}; scan-e218.json {sha(pth)}")
    return pth


def counted_for(card, c):
    """E213's classes (neverrun_e215.counted_for): a folder naming that card, or naming no card"""
    if c == card or c == 'no card named':
        return True
    if card in ('aifoundry1 card 1', 'aifoundry1 card 0') and c == 'aifoundry1 (card not named)':
        return True
    return False


class Never:
    def __init__(self, S):
        self.S = S

    def token_any(self, token):
        """F: (never ran on any card, evidence)"""
        T = {c: v['n'] for c, v in self.S['tokens'].get(token, {}).items() if c != 'SUBTRACTED'}
        meas = self.S['mm1_v32_measured_tokens'].get(token, [])
        return (not T and not meas), {'hits': T, 'measured': meas}

    def token_a3(self, token):
        """G, Gt: (never ran on aifoundry3 card 0, evidence)"""
        T = {c: v['n'] for c, v in self.S['tokens'].get(token, {}).items() if c != 'SUBTRACTED' and counted_for(A3, c)}
        meas = [m for m in self.S['mm1_v32_measured_tokens'].get(token, []) if m.endswith(A3)]
        return (not T and not meas), {'hits_counted_for_a3': T, 'measured_on_a3': meas}

    def config_a3(self, token, mask):
        """Y: (the configuration (shape, mask) never ran on aifoundry3 card 0, evidence): E215's post hoc L reading on this card"""
        m = '0x%x' % int(mask, 16)
        Mb = self.S['masks_by_card'].get(token, {})
        named = sorted(c for c, ms in Mb.items() if c != 'SUBTRACTED' and counted_for(A3, c) and (m in ms or 'any' in ms))
        Mm = self.S['mm1_v32_measured_masks'].get(token, {})
        mpt = sorted(c for c, ms in Mm.items() if c == A3 and m in ms)
        return (not named and not mpt), {'mask_named_in_files_counted_for_a3': named, 'mask_in_mm1_v32_points_on_a3': mpt}


# ================================================================================================ the models (section 9.6)
def lnc_maker():
    """the gemmLnc term maker's own functions, run unchanged (E216's models_e216.lnc_maker form): FORMS, LAM, shape(), feats(), term_W()"""
    src = open(os.path.join(TERMS, 'gemmlnc', 's05_freeze.py')).read()
    tree = ast.parse(src)
    keep = []
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name in ('shape', 'feats', 'term_W'):
            keep.append(n)
        elif isinstance(n, ast.Assign) and any(getattr(t, 'id', None) in ('FORMS', 'LAM') for t in n.targets):
            keep.append(n)
    ns = {'np': np}
    exec(compile(ast.Module(body=keep, type_ignores=[]), 's05_freeze.py', 'exec'), ns)
    return ns


class Models:
    """every declared forecaster, called as section 9.6 says: card aifoundry3 card 0, the arm token, format, kind 'random', mask, f 600.0,
    kernel 'rgm136'; volts, the governed base and the start die not given"""

    def __init__(self, fit_dir, feature_cache):
        sys.path.insert(0, HERE)
        import mm1_v32  # noqa: E402
        import mm1_v31  # noqa: E402
        self.p32_path = os.path.join(fit_dir, 'mm1_v32_params.json')
        self.p32 = json.load(open(self.p32_path))
        self.M32 = mm1_v32.Model(self.p32, feature_cache=feature_cache)
        self.P31 = json.load(open(os.path.join(V31, 'out', 'mm1_v31_params.json')))
        self.M31 = mm1_v31.Model(self.P31)
        T7 = json.load(open(os.path.join(V31, 'out', 'fits', 'time_T5r+G0+T7.json')))
        P7 = copy.deepcopy(self.P31)
        P7['time']['theta'] = dict(T7['theta_all'])
        P7['time']['form'] = dict(T7['form'])
        self.M7 = mm1_v31.Model(P7)
        # MM1-v3 refitted (the acceptance baseline at its all-data constants), REPORTED: MM1-v3.1's predictor code with E1u
        Pv = copy.deepcopy(self.P31)
        Pv['time']['theta'] = dict(self.p32['time']['theta'])
        Pv['energy']['form'] = 'E1u'
        Pv['energy']['theta'] = dict(self.p32['baseline_v3_refitted']['energy_theta'])
        self.Mv3r = mm1_v31.Model(Pv)
        self.Mnolay = None
        if self.p32['time'].get('layout_term', {}).get('enters', 'none') != 'none':
            Pn = copy.deepcopy(self.p32)
            Pn['time']['layout_term'] = {'enters': 'none'}
            self.Mnolay = mm1_v32.Model(Pn)
        rc = os.system(f'cd {V3} && sha256sum -c --quiet SHA256SUMS > /dev/null 2>&1')
        assert rc == 0, 'MM1-v3 SHA256SUMS check failed'
        sys.path.insert(0, V3)
        import mm1_v3  # noqa: E402
        import e213_v3  # noqa: E402
        self.M3 = mm1_v3.Model(json.load(open(os.path.join(V3, 'out', 'mm1_v3_params.json'))))
        M2 = e213_v3.v2_model()
        self.M2 = M2[0] if isinstance(M2, tuple) else M2
        self.L = lnc_maker()
        self.TERM = json.load(open(os.path.join(TERMS, 'gemmlnc', 'term-gemmlnc.json')))
        self.c_lnc = list(self.TERM['constants_pJ_per_line'])
        self.XI = self.P31['energy']['theta']['xi']
        self.EL = load_module('eval_layout_frozen', os.path.join(TERMS, 'layout', 'eval_layout.py'))
        self.FL = load_module('features_layout_frozen', os.path.join(TERMS, 'layout', 'features_layout.py'))
        meta = json.load(open(os.path.join(TERMS, 'layout', 'forecast-e215-v31-layout.json')))['meta']
        self.a_fresh = float(meta['a_fresh'])
        assert self.a_fresh == A_FRESH_POSTED
        self.walk_new = {}
        self.CONST = json.load(open(os.path.join(TERMS, 'layout', 'controls-e216', 'constants-verify-lay.json')))
        self.CE = load_module('controls_e216_frozen', os.path.join(TERMS, 'layout', 'controls-e216', 'controls_e216.py'))
        import layout_v32 as LY  # noqa: E402
        self.LY = LY
        self.store = LY.FeatureStore(feature_cache)
        self.M32._store = self.store                      # one feature store (one cache file) for the predictor and the Y family
        if self.Mnolay is not None:
            self.Mnolay._store = self.store
        rl = self.p32['rest_law'][A3]
        self.rest_T0 = rl['T0_forecast_c']
        self.rest_W = rl['a'] * self.rest_T0 ** 2 + rl['b'] * self.rest_T0 + rl['c']

    @staticmethod
    def spec(arm, fmt, mask):
        return {'card': A3, 'arm': arm, 'fmt': fmt, 'kind': 'random', 'mask': mask, 'f': F_MHZ, 'kernel': 'rgm136'}

    @staticmethod
    def fields(p, note=''):
        if p is None:
            return None
        o = {'T_op_us': p['T_op_us'], 'cycles_per_op_wall': p['cycles_per_op_wall'], 'cycles_per_op_mean': p.get('cycles_per_op_mean'),
             'seconds_per_gemm': p.get('seconds_per_gemm'), 'ops_per_minion_per_gemm': p.get('ops_per_minion_per_gemm'),
             'minions': p.get('minions'), 'note': note}
        if 'W_over_idle' in p:
            o.update({'W_over_idle': p['W_over_idle'], 'A_W': p['W_affine']['A_W'], 'B_W_us': p['W_affine']['B_W_us'],
                      'J_over_idle_per_gemm': p.get('J_over_idle_per_gemm'), 'V': p.get('V'), 's_V': p.get('s_V'), 'die_start_c': p.get('die_start_c')})
            rl = p.get('rest_law')
            if rl:
                o['rest_law_W'] = rl['P_rest_W']
                o['rest_law_T0_c'] = rl['T0_c']
                o['J_at_rest_per_gemm'] = rl['J_at_rest_per_gemm_REPORTED']
        else:
            o['energy'] = p.get('energy', 'NOT FORECAST')
        for k in ('layout_factor', 'F3_first', 'F3_dup', 'F3_W_at_own_t'):
            if k in p:
                o[k] = p[k]
        return o

    def lnc_term(self, p, arm):
        t = p['T_op_us']
        Q = 0.5 * (np.array(p['Q0']) + np.array(p['Q1']))
        fe = self.L['feats'](arm, Q)
        D = 1.0 + self.L['LAM'] * (p['die_start_c'] - 50.0)
        sL = 1.0 + self.XI * (p['s_V'] - 1.0)
        rate = p['minions'] / (t * 1e-6)
        dW, E = self.L['term_W']('F3', self.c_lnc, fe, rate, D, sL)
        return {'dW': float(dW), 'E_pJ_per_minion_op': float(E), 'dup': fe['dup'], 'beyond': fe['beyond'], 'first': fe['first'], 'NB': fe['NB'],
                'D': D, 'sL': sL, 'dB_W_us': float(dW) * t}

    def contention(self, arm, mask, exact=True):
        """(factor, Phi_fresh, key): 'v3.1 + contention''s factor clip(1 + a Phi_fresh, 0.3, 3.0); exact=False gives the factor's bounds only"""
        m = int(mask, 16)
        if m == FULL:
            return 1.0, 0.0, None
        if not exact:
            return None, None, None
        MB, NB, KB = shape_of(arm)
        for mm in (m, FULL):
            key = 'rgm136.gemmL|%dx%dx%d|0x%x' % (MB, NB, KB, mm)
            if key not in self.EL.FEATS:
                f = self.FL.walk_feats('rgm136.gemmL', (MB, NB, KB), mm)
                f.update({'mesh_' + q: v for q, v in self.FL.mesh_feats(mm).items() if q != 'n'})
                self.EL.FEATS[key] = f
                self.walk_new[key] = f
        ph, key = self.EL.phi_of('rgm136 gemmL', arm, mask)
        return float(np.clip(1.0 + self.a_fresh * ph[0], 0.3, 3.0)), float(ph[0]), key

    def composed(self, base, lnc, g, name, phi=None, key=None):
        t = base['T_op_us'] * g
        o = {'T_op_us': t, 'cycles_per_op_wall': base['cycles_per_op_wall'] * g, 'cycles_per_op_mean': base['cycles_per_op_mean'] * g,
             'seconds_per_gemm': base['seconds_per_gemm'] * g, 'ops_per_minion_per_gemm': base['ops_per_minion_per_gemm'],
             'minions': base['minions'], 'layout_factor': g, 'phi_fresh': phi, 'walk_key': key, 'note': name}
        if 'W_over_idle' not in base:
            o['energy'] = 'NOT FORECAST'
            return o
        A = base['W_affine']['A_W']
        B = base['W_affine']['B_W_us'] + (lnc['dB_W_us'] if lnc else 0.0)
        W = A + B / t
        o.update({'W_over_idle': W, 'A_W': A, 'B_W_us': B, 'J_over_idle_per_gemm': W * o['seconds_per_gemm'],
                  'lnc_dW_at_v31_t': (lnc['dW'] if lnc else 0.0), 'lnc': lnc})
        rl = base.get('rest_law')
        if rl:
            o['rest_law_W'] = rl['P_rest_W']
            o['rest_law_T0_c'] = rl['T0_c']
            o['J_at_rest_per_gemm'] = (rl['P_rest_W'] + W) * o['seconds_per_gemm']
        return o

    def controls(self, base31, arm, mask):
        """verify-lay's five controls (Q229's controls_e216.py method: its feat_row and control_value on v01_map's features), REPORTED"""
        m = int(mask, 16)
        out = {}
        if m == FULL:
            fr = {c: 0.0 for c in self.CE.COLS}
        else:
            shp = shape_of(arm)
            f, _ = self.store.get(shp, m, caps=(24, 32), check=False)
            g, _ = self.store.get(shp, FULL, caps=(24, 32), check=False)
            V1 = {self.CE.key_of(arm, m): f, self.CE.key_of(arm, FULL): g}
            fr = self.CE.feat_row(arm, m, V1)
        for fm in self.CE.CTRL_FORMS:
            fac = self.CE.control_factor(fr, fm, self.CONST)
            out[fm] = {'factor': fac, 'cycles_per_op_wall': self.CE.control_value(base31['cycles_per_op_wall'], fr, fm, self.CONST),
                       'seconds_per_gemm': base31['seconds_per_gemm'] * fac, 'features': {c: fr.get(c) for c in self.CONST['forms'][fm]['features']}}
        return out

    def energy_peaks(self, pts):
        """W over idle at its own seconds by the six planning models (each where it prices): for PP; contention by its factor's bounds"""
        specs = [self.spec(p['arm'], p['fmt'], p['mask']) for p in pts]
        r32 = self.M32.predict_many(specs)
        r31 = self.M31.predict_many(specs)
        out = []
        for j, p in enumerate(pts):
            o = {'v32': r32[j], 'v31': r31[j]}
            o['v3'] = self.M3.predict(A3, p['arm'], p['fmt'], 'random', p['mask'], F_MHZ, kernel='rgm136', t0_c=None)
            arm2 = p['arm'].replace('gemmLnc', 'gemmL')
            o['v2'] = self.M2.predict(A3, arm2, p['fmt'], 'random', p['mask'], F_MHZ, V=None, t0_c=None)
            lnc = self.lnc_term(r31[j], p['arm']) if 'W_over_idle' in r31[j] else None
            o['lnc'] = self.composed(r31[j], lnc, 1.0, 'v3.1+lnc') if lnc else None
            out.append(o)
        return out

    def pp(self, o, mask, eps_g=None, exact_contention=False):
        """the planning peak (section 9.1): max W over idle at own seconds over MM1-v3.2 (x (1 + 2 eps_G) at a G point), MM1-v3.1, MM1-v3,
        MM1-v2, 'v3.1 + gemmLnc term', 'v3.1 + contention' (each where it prices) + the rest law at T0 + 2 W"""
        ws = []
        if 'W_over_idle' not in o['v32']:
            return None, 'MM1-v3.2 does not price it', None
        w32 = o['v32']['W_over_idle'] * ((1.0 + 2.0 * eps_g) if eps_g is not None else 1.0)
        ws.append((w32, 'MM1-v3.2' + (' x (1 + 2 eps_G)' if eps_g is not None else '')))
        for k, nm in (('v31', 'MM1-v3.1'), ('v3', 'MM1-v3'), ('v2', 'MM1-v2')):
            if isinstance(o.get(k), dict) and 'W_over_idle' in o[k]:
                ws.append((o[k]['W_over_idle'], nm))
        if o.get('lnc') and 'W_over_idle' in o['lnc']:
            ws.append((o['lnc']['W_over_idle'], 'v3.1+lnc'))
        b31 = o['v31']
        how = 'exact'
        if 'W_over_idle' in b31:
            if int(mask, 16) == FULL:
                ws.append((b31['W_over_idle'], 'v3.1+contention (= MM1-v3.1 at the full chip)'))
            else:
                A, B, t = b31['W_affine']['A_W'], b31['W_affine']['B_W_us'], b31['T_op_us']
                if exact_contention:
                    g, phi, key = self.contention(b31['arm'], mask)
                    ws.append((A + B / (t * g), 'v3.1+contention'))
                else:
                    gmin, gmax = 1.0 - abs(self.a_fresh), 1.0 + abs(self.a_fresh)
                    ub = max(A + B / (t * gmin), A + B / (t * gmax))
                    ws.append((ub, 'v3.1+contention (upper bound over its factor range)'))
                    how = 'bound'
        w, m = max(ws)
        return w + self.rest_W + 2.0, m, how

    def forecast_all(self, pts):
        """section 9.6's columns for the chosen points"""
        specs = [self.spec(p['arm'], p['fmt'], p['mask']) for p in pts]
        r32 = self.M32.predict_many(specs)
        r31 = self.M31.predict_many(specs)
        r7 = self.M7.predict_many(specs)
        rv3r = self.Mv3r.predict_many(specs)
        rnl = self.Mnolay.predict_many(specs) if self.Mnolay else [None] * len(pts)
        out = {}
        for j, p in enumerate(pts):
            o = {}
            o['MM1-v3.2'] = self.fields(r32[j])
            o['MM1-v3.1'] = self.fields(r31[j])
            o['MM1-v3'] = self.fields(self.M3.predict(A3, p['arm'], p['fmt'], 'random', p['mask'], F_MHZ, kernel='rgm136', t0_c=None))
            arm2 = p['arm'].replace('gemmLnc', 'gemmL')
            o['MM1-v2'] = self.fields(self.M2.predict(A3, arm2, p['fmt'], 'random', p['mask'], F_MHZ, V=None, t0_c=None),
                                      note=('MM1-v2 has no code-path term: its rgm136 gemmL twin, literally' if arm2 != p['arm'] else ''))
            lnc = self.lnc_term(r31[j], p['arm'])
            g, phi, key = self.contention(p['arm'], p['mask'])
            o['v3.1 + gemmLnc term'] = self.composed(r31[j], lnc, 1.0, 'v3.1+lnc')
            o['v3.1 + contention'] = self.composed(r31[j], None, g, 'v3.1+contention', phi, key)
            o['verify-lay controls'] = self.controls(r31[j], p['arm'], p['mask'])
            o['REPORTED v3.1 + both terms'] = self.composed(r31[j], lnc, g, 'v3.1+both', phi, key)
            o['REPORTED v3.1 with T7'] = self.fields(r7[j])
            o['REPORTED MM1-v3 refitted'] = self.fields(rv3r[j])
            if rnl[j] is not None:
                o['REPORTED MM1-v3.2 without its layout term'] = self.fields(rnl[j])
            out[p['id']] = o
        return out


# ================================================================================================ the point rule
def rank(cands, key_s, desc=True):
    """sorted by score with section 9.1's ties: scores within 1e-12 relative are one tie, broken by the sorted string"""
    s = sorted(cands, key=lambda c: (-c[key_s] if desc else c[key_s], c['string']))
    out, i = [], 0
    while i < len(s):
        j = i + 1
        while j < len(s) and abs(s[j][key_s] - s[i][key_s]) <= TIE_REL * max(abs(s[i][key_s]), 1e-300):
            j += 1
        out += sorted(s[i:j], key=lambda c: c['string'])
        i = j
    return out


class Rule:
    def __init__(self, scan_path, fit_dir, out):
        self.S = json.load(open(scan_path))
        self.NV = Never(self.S)
        self.out = out
        self.M = Models(fit_dir, os.path.join(out, 'features-e218-candidates.json'))
        self.dec = json.load(open(os.path.join(fit_dir, 'decisions_v32.json')))
        acc = self.dec['steps']['step4']['acceptance']
        e5 = acc['5']['LOEO W given t over gemmLnc points (no twin, >= 3 W)']['v32']
        self.eps_g = e5 / 100.0
        self.layout = self.dec['steps']['step2']
        self.a_all = {c: self.layout['candidates_summary'][c]['a_all'] for c in LAYOUT_CANDS}
        self.shapes = set()
        self.points = []
        self.logs = {'G': [], 'Y': [], 'F': []}
        self.rngs = {}
        self.readings = []

    def rng(self, fam, stratum):
        k = (fam, stratum)
        if k not in self.rngs:
            self.rngs[k] = random.Random(f'v3.2-blind|E218|{fam}|{stratum}')
        return self.rngs[k]

    @staticmethod
    def string(loop, token, fmt, mask):
        return f'{loop}|{token}|{fmt}|random|{mask}'

    # ------------------------------------------------------------ G and Gt
    def family_g(self):
        wait_load()
        t0 = time.time()
        pts = []
        for fmt in ('fp32', 'int8'):
            for MB in G_MB:
                for NB in G_NB:
                    for KB in G_KB:
                        pts.append({'arm': tok('gemmLnc', (MB, NB, KB)), 'fmt': fmt, 'mask': FULLM, 'shape': (MB, NB, KB)})
        specs = [Models.spec(p['arm'], p['fmt'], FULLM) for p in pts]
        r32 = self.M.M32.predict_many(specs)
        r31 = self.M.M31.predict_many(specs)
        cands = []
        for p, a, b in zip(pts, r32, r31):
            Q = 0.5 * (np.array(a['Q0']) + np.array(a['Q1']))
            beyond = 14.0 * (1.0 - Q[0, :].sum()) + 12.0 * (1.0 - Q[:, 0].sum())
            NB = p['shape'][1]
            if beyond < 2.6:
                reg = 'L2'
            elif NB <= 3:
                reg = 'NB1-3'
            elif NB in (5, 6):
                reg = 'NB5-6'
            elif 12 <= NB <= 15:
                reg = 'NB12-15'
            else:
                reg = None
            if reg is None or (p['fmt'] == 'int8' and reg != 'L2'):
                continue
            if 'W_over_idle' not in a or 'W_over_idle' not in b:
                continue
            cands.append({'token': p['arm'], 'fmt': p['fmt'], 'shape': p['shape'], 'regime': reg, 'beyond': float(beyond),
                          's': abs(math.log(a['W_over_idle'] / b['W_over_idle'])), 'W_v32': a['W_over_idle'], 'W_v31': b['W_over_idle'],
                          'string': self.string('rgm136 gemmLnc', p['arm'], p['fmt'], FULLM)})
        by = {r: [c for c in cands if c['regime'] == r] for r in G_ORDER}
        self.g_cands = {r: len(v) for r, v in by.items()}
        drawn = []
        nbkb = set()
        cache = {}

        def qualifies(c):
            if c['shape'] in self.shapes or (c['shape'][1], c['shape'][2], c['fmt']) in nbkb:
                return False, 'shape or (NB, KB, format) already drawn'
            k = (c['token'], c['fmt'])
            if k not in cache:
                twin = tok('gemmL', c['shape'])
                n1, ev1 = self.NV.token_a3(c['token'])
                n2, ev2 = self.NV.token_a3(twin)
                rec = {'never_G': n1, 'never_Gt': n2, 'ev_G': ev1, 'ev_Gt': ev2}
                if n1 and n2:
                    o = self.M.energy_peaks([{'arm': c['token'], 'fmt': c['fmt'], 'mask': FULLM}, {'arm': twin, 'fmt': c['fmt'], 'mask': FULLM}])
                    ppg, byg, _ = self.M.pp(o[0], FULLM, eps_g=self.eps_g)
                    ppt, byt, _ = self.M.pp(o[1], FULLM)
                    rec.update({'PP_G': ppg, 'PP_G_by': byg, 'PP_Gt': ppt, 'PP_Gt_by': byt})
                cache[k] = rec
            r = cache[k]
            if not r['never_G'] or not r['never_Gt']:
                return False, 'ran on aifoundry3 card 0'
            if r.get('PP_G') is None or r.get('PP_Gt') is None:
                return False, 'energy not priced by MM1-v3.2'
            if r['PP_G'] >= LINE or r['PP_Gt'] >= LINE:
                return False, 'planning peak at or above 67.0 W'
            return True, 'qualifies'

        def accept(c, how, stratum):
            r = cache[(c['token'], c['fmt'])]
            x = dict(c, how=how, stratum=stratum, **{k: r[k] for k in ('PP_G', 'PP_G_by', 'PP_Gt', 'PP_Gt_by')})
            drawn.append(x)
            self.shapes.add(c['shape'])
            nbkb.add((c['shape'][1], c['shape'][2], c['fmt']))
            self.logs['G'].append({'string': c['string'], 'verdict': 'DRAWN (%s)' % how, 'stratum': stratum, 's': c['s']})

        def take(reg, q):
            if q <= 0:
                return 0
            k_score = math.ceil(q / 2)
            got = 0
            for c in rank(by[reg], 's'):
                if got >= k_score:
                    break
                if any(d['token'] == c['token'] and d['fmt'] == c['fmt'] for d in drawn):
                    continue
                ok, why = qualifies(c)
                if ok:
                    accept(c, 'score', reg)
                    got += 1
                else:
                    self.logs['G'].append({'string': c['string'], 'verdict': why, 'stratum': reg, 's': c['s']})
            k_draw = q - got
            got_d = 0
            rng = self.rng('G', reg)
            while got_d < k_draw:
                rem = sorted([c for c in by[reg] if not any(d['token'] == c['token'] and d['fmt'] == c['fmt'] for d in drawn)
                              and qualifies(c)[0]], key=lambda c: c['string'])
                if not rem:
                    break
                picks = rng.sample(rem, min(k_draw - got_d, len(rem)))
                progressed = False
                for c in picks:
                    if got_d >= k_draw:
                        break
                    ok, why = qualifies(c)
                    if ok:
                        accept(c, 'draw', reg)
                        got_d += 1
                        progressed = True
                    else:
                        self.logs['G'].append({'string': c['string'], 'verdict': 'drawn but ' + why + ' (re-drawn)', 'stratum': reg})
                if not progressed:
                    break
            return got + got_d
        carry = 0
        for reg in G_ORDER:
            q = G_QUOTA[reg] + carry
            got = take(reg, q)
            carry = q - got
        if carry > 0:
            got = take('L2', carry)
            carry -= got
        self.g_short = carry
        for n, x in enumerate(drawn, 1):
            self.add(id=f'g{n:02d}', family='G', regime=x['regime'], how=x['how'], arm=x['token'], fmt=x['fmt'], mask=FULLM, score=x['s'],
                     PP=x['PP_G'], PP_by=x['PP_G_by'], beyond=x['beyond'], twin=f'g{n:02d}t')
        for n, x in enumerate(drawn, 1):
            self.add(id=f'g{n:02d}t', family='Gt', regime=x['regime'], how='twin', arm=tok('gemmL', x['shape']), fmt=x['fmt'], mask=FULLM,
                     PP=x['PP_Gt'], PP_by=x['PP_Gt_by'], twin_of=f'g{n:02d}')
        self.g_summary = {'candidates_by_regime': self.g_cands, 'drawn': len(drawn), 'short_by': carry,
                          'short': len(drawn) < 9, 'eps_G': self.eps_g, 'secs': round(time.time() - t0, 1)}

    # ------------------------------------------------------------ Y
    def family_y(self):
        wait_load()
        t0 = time.time()
        LY = self.M.LY
        p32 = self.M.p32
        import time_v31 as TV  # noqa: E402
        cand_pts, keys = [], []
        for MB in Y_MB:
            for NB in Y_NB:
                for KB in Y_KB:
                    s = (MB, NB, KB)
                    for n, ms in Y_MASKS.items():
                        for m in ms:
                            cand_pts.append({'arm': tok('gemmL', s), 'kernel': 'rgm136', 'fmt': 'fp32', 'mask': m, 'f': F_MHZ, 'shape': s, 'n': n})
        en = TV.Engine31(cand_pts)
        form = p32['time']['form']
        Tb = en.predict(p32['time']['theta'], form)
        feats = []
        for j, p in enumerate(cand_pts):
            r, _ = LY.feat_row(p['arm'], int(p['mask'], 16), self.M.store, caps=(24, 32), check=False)
            feats.append(r)
            if j % 100 == 0:
                self.M.store.save()
        self.M.store.save()
        T = {}
        for c in LAYOUT_CANDS:
            cols = LAYOUT_COLS[c]
            a = np.asarray(self.a_all[c], float)
            v = []
            for j, p in enumerate(cand_pts):
                x = np.array([feats[j][k] for k in cols], float)
                v.append(Tb[j] * (float(np.clip(1.0 + x @ a, 0.3, 3.0)) if len(cols) else 1.0))
            T[c] = np.array(v)
        idx = {(p['shape'], p['mask']): j for j, p in enumerate(cand_pts)}
        pairs = []
        for MB in Y_MB:
            for NB in Y_NB:
                for KB in Y_KB:
                    s = (MB, NB, KB)
                    for n, ms in Y_MASKS.items():
                        msorted = sorted(ms, key=lambda m: int(m, 16))
                        for i1 in range(len(msorted)):
                            for i2 in range(i1 + 1, len(msorted)):
                                ma, mb = msorted[i1], msorted[i2]
                                ja, jb = idx[(s, ma)], idx[(s, mb)]
                                d = {c: math.log(T[c][ja] / T[c][jb]) for c in LAYOUT_CANDS}
                                Dp = max(d.values()) - min(d.values())
                                pairs.append({'shape': s, 'n': n, 'mask_a': ma, 'mask_b': mb, 'token': tok('gemmL', s), 'D': Dp, 'd': d,
                                              'd_none': d['none'], 'ja': ja, 'jb': jb,
                                              'string': self.string('rgm136 gemmL', tok('gemmL', s), 'fp32', ma) + '+' + mb})
        self.y_pairs_n = len(pairs)
        cache = {}

        def point_ok(token, mask):
            k = (token, mask)
            if k not in cache:
                nv, ev = self.NV.config_a3(token, mask)
                rec = {'never': nv, 'ev': ev}
                if nv:
                    o = self.M.energy_peaks([{'arm': token, 'fmt': 'fp32', 'mask': mask}])[0]
                    pp, by, how = self.M.pp(o, mask)
                    if pp is not None and pp >= LINE and how == 'bound':
                        pp, by, how = self.M.pp(o, mask, exact_contention=True)
                    rec.update({'PP': pp, 'PP_by': by, 'PP_how': how})
                cache[k] = rec
            r = cache[k]
            if not r['never']:
                return False, 'configuration ran on aifoundry3 card 0', r
            if r.get('PP') is None:
                return False, 'energy not priced by MM1-v3.2', r
            if r['PP'] >= LINE:
                return False, 'planning peak at or above 67.0 W', r
            return True, 'qualifies', r

        chosen = []

        def pair_ok(p):
            if p['shape'] in self.shapes or any(c['shape'] == p['shape'] for c in chosen):
                return False, 'shape already in E218'
            oa, wa, ra = point_ok(p['token'], p['mask_a'])
            if not oa:
                return False, 'mask a: ' + wa
            ob, wb, rb = point_ok(p['token'], p['mask_b'])
            if not ob:
                return False, 'mask b: ' + wb
            return True, 'qualifies'
        for p in rank(pairs, 'D'):
            if len(chosen) >= 6:
                break
            ok, why = pair_ok(p)
            if ok:
                chosen.append(dict(p, how='D rank'))
                self.logs['Y'].append({'string': p['string'], 'D': p['D'], 'verdict': 'DRAWN (rank)'})
            elif len(self.logs['Y']) < 400:
                self.logs['Y'].append({'string': p['string'], 'D': p['D'], 'verdict': why})
        ctrl = [p for p in pairs if abs(p['d_none']) <= 0.0005]
        self.y_ctrl_n = len(ctrl)
        nctrl = 0
        for p in rank(ctrl, 'D', desc=False):
            if nctrl >= 2:
                break
            ok, why = pair_ok(p)
            if ok:
                chosen.append(dict(p, how='control'))
                nctrl += 1
                self.logs['Y'].append({'string': p['string'], 'D': p['D'], 'verdict': 'DRAWN (control)'})
        for n, p in enumerate(chosen, 1):
            self.shapes.add(p['shape'])
            for half, m in (('a', p['mask_a']), ('b', p['mask_b'])):
                r = cache[(p['token'], m)]
                self.add(id=f'y{n:02d}{half}', family='Y', how=p['how'], arm=p['token'], fmt='fp32', mask=m, score=p['D'],
                         pair=f'y{n:02d}', pair_d_by_candidate=p['d'], PP=r['PP'], PP_by=r['PP_by'], PP_how=r['PP_how'])
        self.y_summary = {'pairs': len(pairs), 'control_pool': len(ctrl), 'drawn': len(chosen), 'short': len(chosen) < 8,
                          'feature_records_made': self.M.store.made, 'secs': round(time.time() - t0, 1)}

    # ------------------------------------------------------------ F
    def family_f(self):
        wait_load()
        t0 = time.time()
        drawn = []
        for fmt, q in F_QUOTA:
            pts = []
            for MB in F_MB:
                for NB in F_NB:
                    for KB in F_KB:
                        s = (MB, NB, KB)
                        t = tok('gemmL', s)
                        nv, _ = self.NV.token_any(t)
                        if nv:
                            pts.append({'arm': t, 'fmt': fmt, 'mask': FULLM, 'shape': s})
            specs = [Models.spec(p['arm'], p['fmt'], FULLM) for p in pts]
            r32 = self.M.M32.predict_many(specs) if specs else []
            r31 = self.M.M31.predict_many(specs) if specs else []
            cands = [{'token': p['arm'], 'fmt': fmt, 'shape': p['shape'], 's': abs(math.log(a['cycles_per_op_wall'] / b['cycles_per_op_wall'])),
                      'string': self.string('rgm136 gemmL', p['arm'], fmt, FULLM)} for p, a, b in zip(pts, r32, r31)]
            cache = {}

            def qualifies(c):
                if c['shape'] in self.shapes:
                    return False, 'shape already in E218'
                k = (c['token'], c['fmt'])
                if k not in cache:
                    o = self.M.energy_peaks([{'arm': c['token'], 'fmt': c['fmt'], 'mask': FULLM}])[0]
                    pp, by, _ = self.M.pp(o, FULLM)
                    cache[k] = {'PP': pp, 'PP_by': by}
                r = cache[k]
                if r['PP'] is None:
                    return False, 'energy not priced by MM1-v3.2'
                if r['PP'] >= LINE:
                    return False, 'planning peak at or above 67.0 W'
                return True, 'qualifies'

            def accept(c, how):
                r = cache[(c['token'], c['fmt'])]
                drawn.append(dict(c, how=how, PP=r['PP'], PP_by=r['PP_by']))
                self.shapes.add(c['shape'])
                self.logs['F'].append({'string': c['string'], 'verdict': 'DRAWN (%s)' % how, 's': c['s']})
            k_score = math.ceil(q / 2)
            got = 0
            for c in rank(cands, 's'):
                if got >= k_score:
                    break
                ok, why = qualifies(c)
                if ok:
                    accept(c, 'score')
                    got += 1
                else:
                    self.logs['F'].append({'string': c['string'], 'verdict': why, 's': c['s']})
            k_draw = q - got
            got_d = 0
            rng = self.rng('F', fmt)
            while got_d < k_draw:
                rem = sorted([c for c in cands if not any(d['token'] == c['token'] and d['fmt'] == c['fmt'] for d in drawn)
                              and qualifies(c)[0]], key=lambda c: c['string'])
                if not rem:
                    break
                picks = rng.sample(rem, min(k_draw - got_d, len(rem)))
                progressed = False
                for c in picks:
                    if got_d >= k_draw:
                        break
                    ok, why = qualifies(c)
                    if ok:
                        accept(c, 'draw')
                        got_d += 1
                        progressed = True
                    else:
                        self.logs['F'].append({'string': c['string'], 'verdict': 'drawn but ' + why + ' (re-drawn)'})
                if not progressed:
                    break
        for n, x in enumerate(drawn, 1):
            self.add(id=f'f{n:02d}', family='F', how=x['how'], arm=x['token'], fmt=x['fmt'], mask=FULLM, score=x['s'], PP=x['PP'], PP_by=x['PP_by'])
        self.f_summary = {'drawn': len(drawn), 'short': len(drawn) < 14, 'by_format': dict(collections.Counter(x['fmt'] for x in drawn)),
                          'secs': round(time.time() - t0, 1)}

    def add(self, **kw):
        s = shape_of(kw['arm'])
        kw.update({'MB': s[0], 'NB': s[1], 'KB': s[2], 'M': 1024 * s[0], 'N': 512 * s[1], 'K': KBLK[kw['fmt']] * s[2],
                   'ops_per_minion_per_gemm': 64 * s[0] * s[1] * s[2], 'shires': bin(int(kw['mask'], 16)).count('1'),
                   'minions': 32 * bin(int(kw['mask'], 16)).count('1'), 'kernel': 'rgm136', 'kind': 'random', 'card': A3, 'f_mhz': F_MHZ,
                   'loop': 'rgm136 gemmLnc' if kw['arm'].startswith('gemmLnc') else 'rgm136 gemmL'})
        self.points.append(kw)

    def order(self):
        """section 9.5's order (REPORTED for E218's kit): s01; t01; pass 1 (Gt, Y, F shuffled); tie; pass 2 (reversed); tie; s03, G by PP up, then down"""
        p1 = sorted(p['id'] for p in self.points if p['family'] in ('Gt', 'Y', 'F'))
        random.Random('E218|A|pass1').shuffle(p1)
        g = [p for p in self.points if p['family'] == 'G']
        gb = [p['id'] for p in sorted(g, key=lambda p: (p['PP'], p['id']))]
        seq = ['s01 (smoke, gemmL2x2x2 fp32)', 't01 (tie, gemmL2x4x4 fp32 random, the full chip)'] + p1 + ['t01'] + list(reversed(p1)) + ['t01'] + \
              ['s03 (smoke, gemmLnc2x2x2 fp32)'] + gb + list(reversed(gb))
        runs = len(p1) * 2 + len(gb) * 2 + 3
        return {'sequence': seq, 'runs': runs, 'smoke_processes': 2,
                'card_minutes_planned_at_24.47_s': round(runs * 24.47 / 60.0, 1)}


def write_outputs(R, fc, out):
    os.makedirs(out, exist_ok=True)
    pts = R.points
    cols = ['id', 'family', 'regime', 'how', 'pair', 'twin', 'twin_of', 'loop', 'kernel', 'arm', 'fmt', 'kind', 'mask', 'shires', 'minions', 'MB',
            'NB', 'KB', 'M', 'N', 'K', 'ops_per_minion_per_gemm', 'card', 'f_mhz', 'score', 'PP', 'PP_by']
    with open(os.path.join(out, 'points-e218.csv'), 'w', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(cols)
        for p in pts:
            w.writerow([repr(p.get(c)) if isinstance(p.get(c), float) else ('' if p.get(c) is None else p.get(c)) for c in cols])
    models = ['MM1-v3.2', 'MM1-v3.1', 'MM1-v3', 'MM1-v2', 'v3.1 + gemmLnc term', 'v3.1 + contention']
    fcols = ['cycles_per_op_wall', 'cycles_per_op_mean', 'T_op_us', 'seconds_per_gemm', 'W_over_idle', 'A_W', 'B_W_us', 'J_over_idle_per_gemm',
             'J_at_rest_per_gemm']
    with open(os.path.join(out, 'forecasts-e218.csv'), 'w', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        hdr = ['id', 'family', 'arm', 'fmt', 'mask']
        for m in models:
            hdr += [f'{m}|{c}' for c in fcols]
        for fm in ('N3', 'N1+N2', 'G1', 'G1+N1', 'fresh24'):
            hdr += [f'verify-lay {fm}|cycles_per_op_wall', f'verify-lay {fm}|seconds_per_gemm']
        w.writerow(hdr)
        for p in pts:
            o = fc[p['id']]
            row = [p['id'], p['family'], p['arm'], p['fmt'], p['mask']]
            for m in models:
                x = o.get(m) or {}
                row += [repr(x[c]) if isinstance(x.get(c), (float, int)) and not isinstance(x.get(c), bool) else ('' if x.get(c) is None else x.get(c))
                        for c in fcols]
            for fm in ('N3', 'N1+N2', 'G1', 'G1+N1', 'fresh24'):
                x = o['verify-lay controls'][fm]
                row += [repr(x['cycles_per_op_wall']), repr(x['seconds_per_gemm'])]
            w.writerow(row)
    json.dump({'what': "E218's points by DECLARED-v32.md section 9's point rule and every declared model's forecasts (section 9.6), before any E218 datum",
               'made': now(), 'interpreter': '/usr/bin/python3 ' + sys.version.split()[0], 'numpy': np.__version__, 'points': pts, 'forecasts': fc},
              open(os.path.join(out, 'forecasts-e218.json'), 'w'), indent=1, sort_keys=True, default=float)


def choose(scan_path, fit_dir, out):
    t0 = now()
    R = Rule(scan_path, fit_dir, out)
    R.family_g()
    R.family_y()
    R.family_f()
    fc = R.M.forecast_all(R.points)
    write_outputs(R, fc, out)
    order = R.order()
    readings = [
        "draws: random.Random('v3.2-blind|E218|<family>|<stratum>') is made once a stratum and its .sample(remaining qualifying, k) taken in "
        "its returned order; a pick that no longer qualifies given the points accepted before it (a shape or (NB, KB, format) clash) is "
        "skipped and the shortfall re-drawn from the then-remaining qualifying candidates with the same generator",
        "G's quotas: regimes processed in the pass-on order L2, NB5-6, NB12-15, NB1-3, each at its quota plus the shortfall passed on to it, "
        "then L2 again with any shortfall left; ceil(q / 2) by score and the rest by draw at each regime's effective quota q",
        "ties: within 1e-12 relative of the group's first score, broken by the string loop|token|format|kind|mask (a Y pair's string: the lower "
        "mask's point string + '+' + the higher mask)",
        "Y's planning peak uses an upper bound of 'v3.1 + contention''s W over its factor's range [1 - |a|, 1 + |a|] (|Phi_fresh| <= 1); the "
        "exact walk feature is made only where the bound reaches 67.0 W; the chosen points' contention forecasts are exact",
        "Y's d_c: every candidate at the layout rule's all-data two-stage constants (its output's candidates > a_all) on MM1-v3.2's base op time "
        "(the refitted T5r+G0+n32 at its all-data constants), the factor clipped to [0.3, 3.0]",
        "the scan's three named changes (module docstring): E218's folders subtracted, MM1-v3.2's points, E216 and E217 unread (E216's "
        "registered points counted as run on aifoundry2 card 0; every token E217's registration names counted as run on every card at every "
        "mask, as the scanner counts a lane file naming no card; a stand-in, not the literal scan)"]
    summ = {'started': t0, 'ended': now(), 'G': R.g_summary, 'Y': R.y_summary, 'F': R.f_summary, 'n_points': len(R.points),
            'by_family': dict(collections.Counter(p['family'] for p in R.points)), 'order': order, 'readings': readings,
            'scan_sha256': sha(scan_path), 'params_sha256': sha(R.M.p32_path),
            'walk_records_made_for_contention': sorted(R.M.walk_new), 'eps_G': R.eps_g, 'rest_law_W_at_T0': R.M.rest_W,
            'logs': {k: v[:300] for k, v in R.logs.items()}}
    json.dump(summ, open(os.path.join(out, 'choice-e218.json'), 'w'), indent=1, sort_keys=True, default=float)
    json.dump(R.M.walk_new, open(os.path.join(out, 'walk-records-e218.json'), 'w'), indent=0, sort_keys=True)
    R.M.store.save()
    print('E218:', summ['by_family'], 'G', R.g_summary, 'Y', R.y_summary, 'F', R.f_summary)
    lines = [f"# E218's points and every declared model's forecasts, frozen by fix-fit-v32 (round Q230; fit-v32's draw re-drawn after "
             f"verify-fit-v32's finding) at {now()}, before any E218 datum (no E218 run exists); their freeze line is the push of the commit "
             "that lands this folder; E218's registration re-runs the declared scan literally and decides the points (DECLARED-v32.md section 10)",
             '# sha256 (paths relative to out/e218/):']
    for f in ('points-e218.csv', 'forecasts-e218.csv', 'forecasts-e218.json', 'choice-e218.json', 'scan-e218.json'):
        lines.append(f'{sha(os.path.join(out, f))}  {f}')
        print(lines[-1])
    lines.append(f"# the constants: {sha(R.M.p32_path)}  ../mm1_v32_params.json")
    open(os.path.join(out, 'E218-FROZEN.txt'), 'w').write('\n'.join(lines) + '\n')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd')
    a1 = sub.add_parser('scan')
    a1.add_argument('--lab', required=True)
    a1.add_argument('--lanes', required=True)
    a1.add_argument('--out', required=True)
    a1.add_argument('--e216-points', default=None)
    a2 = sub.add_parser('choose')
    a2.add_argument('--scan', required=True)
    a2.add_argument('--fit', required=True)
    a2.add_argument('--out', required=True)
    a = ap.parse_args()
    if a.cmd == 'scan':
        scan(a.lab, a.lanes, a.out, a.e216_points)
    elif a.cmd == 'choose':
        choose(a.scan, a.fit, a.out)
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
