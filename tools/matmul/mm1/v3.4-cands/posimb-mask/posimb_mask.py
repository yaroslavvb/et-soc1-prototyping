#!/usr/bin/env python3
"""'MM1-v3.2 + posimb-mask' (a v3.4 candidate, round Q238, lane mask-posimb): the predictor, frozen with its constants
(params-posimb-mask.json), as DECLARED-posimb-mask.md (sha256 b59f1c4d...) declares it.

    import posimb_mask; M = posimb_mask.Model()
    M.predict_many([{'card': ..., 'arm': 'gemmL2x6x10', 'fmt': 'fp32', 'kind': 'zeros', 'mask': '0x4000', 'f': 600.0, 'kernel': 'rgm136'}, ...])
    M.predict_many_with_af4([...])      # 'MM1-v3.2 + AF4 + posimb-mask', by construction, no refit

THE BASE is MM1-v3.2 (../../v3.2/mm1_v32.py at its out/mm1_v32_params.json), unchanged. THE TERM acts only at the subset points of rgm136's
cooperative gemmL loop (mask not 0xffffffff, kernel rgm136, arm gemmL<MB>x<NB>x<KB>); everywhere else every number is MM1-v3.2's:
    wall:  T = T_v32 x clip(1 + a_hop e G1core + a_lag e LAGcore + a_al e A1, 0.3, 3.0)
    mean:  MM1-v3.2's counter mean x clip(1 + a_hop e G1core + a_al e A1, 0.3, 3.0)
    energy: MM1-v3.2's W over idle A_W + B_W / t at the term's op time t; J over idle = W x seconds; J at rest = (P_rest + W) x seconds
with G1core = Lmean_act / Lmean_full - 1 and LAGcore = ((Lmax_act - Lmean_act) / Lmean_full) x Fp / (Fp + Fs) (posimb's two features, by the
same code as tools/matmul/mm1/v3.3-cands/posimb/scripts/f02_private.py: L(s) = 110 + 12 x shire s's mean hop to the 32 L3 homes on the MARTY
map; Fp, Fs the walk's private and shared DRAM-served request shares at a strict-LRU 32 MB L3), A1 = 1 when no active shire s has
(s >> 2) & 3 == s & 3 (the kernel's row group and column group), else 0; e = MM1-v3.2's elasticity of its op time to its four mesh-served
memory constants (c3, m3, cF, mF scaled by 1.01). AF4 (tools/matmul/mm1/v3.3-cands/gemmlnc-af4/) acts only at gemmLnc points (energy), by
its frozen per-row form as tools/claims-v3/e222/desk/models_e222.py applies it: the two scopes are disjoint, so a composed row is the one
term's row that acts (exit 5 otherwise).
Desk; /usr/bin/python3 3.12.3, numpy; single-threaded. Labels: the constants are a post hoc desk fit (made after their data existed); a
forecast for a never-run point is blind only once its sha256 is in a pushed commit before that point's first datum.
SPDX-License-Identifier: Apache-2.0
"""
import collections
import importlib.util
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
MM1 = os.path.join(REPO, 'tools', 'matmul', 'mm1')
V32 = os.path.join(MM1, 'v3.2')
V31 = os.path.join(MM1, 'v3.1')
V3 = os.path.join(MM1, 'v3')
C215 = os.path.join(MM1, 'v3.2-terms', 'layout', 'controls-e215')
AF4_DIR = os.path.join(MM1, 'v3.3-cands', 'gemmlnc-af4')
PARAMS = os.path.join(HERE, 'params-posimb-mask.json')
FEATURES = os.path.join(HERE, 'out', 'private_shared.json')
SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
SHAPE_ANY = re.compile(r'^gemmL(?:nc|n)?(\d+)x(\d+)x(\d+)$')
FULL = 0xFFFFFFFF
MEMK = ('c3', 'm3', 'cF', 'mF')
LABEL = 'MM1-v3.2 + posimb-mask'
LABEL_AF4 = 'MM1-v3.2 + AF4 + posimb-mask'
KEYS = ('T_op_us', 'cycles_per_op_wall', 'cycles_per_op_mean', 'seconds_per_gemm', 'W_over_idle', 'A_W', 'B_W_us', 'J_over_idle_per_gemm',
        'J_at_rest_per_gemm')

for p in (V32, V31):
    if p not in sys.path:
        sys.path.insert(0, p)
os.environ.setdefault('ET_LAB', REPO)
_spec = importlib.util.spec_from_file_location('v01_map_committed', os.path.join(C215, 'v01_map.py'))
V01 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V01)

# ---------------------------------------------------------------------------------------------------------------- posimb's features
# (f02_private.py's MARTY map, hop law, private/shared split and mesh latencies, verbatim)
CAP_TILES = 32 * 1024
MARTY = {
    0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0),
    8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1), 10: (4, 1), 19: (5, 1),
    3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2),
    12: (1, 3), 21: (2, 3), 22: (3, 3), 26: (4, 3),
    20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4),
    28: (1, 5), 5: (2, 5), 6: (3, 5), 7: (4, 5), 31: (5, 5),
}


def hp(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


HBAR = {s: float(np.mean([hp(MARTY[s], MARTY[h]) for h in range(32)])) for s in range(32)}
LAT = {s: 110.0 + 12.0 * HBAR[s] for s in range(32)}
LMEAN_FULL = float(np.mean([LAT[s] for s in range(32)]))


def mesh_lat(mask):
    sh = [s for s in range(32) if (mask >> s) & 1]
    L = np.array([LAT[s] for s in sh])
    return {'Lmean_act': float(L.mean()), 'Lmax_act': float(L.max()), 'Lmean_full': LMEAN_FULL, 'n': len(sh)}


def private_shared(MB, NB, KB, mask):
    seq = list(V01.my_steps(MB, NB, KB, mask))
    od = collections.OrderedDict()
    nsteps = 0
    priv = shared = req = 0
    for p in range(2):
        rec = p == 1
        for st in seq:
            if st[0] == 'store':
                for a in st[1]:
                    t = a >> 10
                    if t in od:
                        od.move_to_end(t)
                    else:
                        od[t] = None
                        if len(od) > CAP_TILES:
                            od.popitem(last=False)
                continue
            if rec:
                nsteps += 1
            for lst in (st[1], st[2]):
                for a, sharers in lst:
                    k = len(sharers)
                    if rec:
                        req += k
                    t = a >> 10
                    if t in od:
                        od.move_to_end(t)
                    else:
                        od[t] = None
                        if len(od) > CAP_TILES:
                            od.popitem(last=False)
                        if rec:
                            if k == 1:
                                priv += 1
                            else:
                                shared += k
    return {'Fp': priv / req, 'Fs': shared / req, 'req_tiles': req, 'steps': nsteps}


def A1_of(mask):
    """1 when no active shire s has (s >> 2) & 3 == s & 3 (the kernel's row group mod 4 equal to its column group), else 0"""
    m = int(mask, 16) if isinstance(mask, str) else int(mask)
    return int(not any(((s >> 2) & 3) == (s & 3) for s in range(32) if (m >> s) & 1))


def in_scope(arm, mask, kernel):
    return int(mask, 16) != FULL and kernel == 'rgm136' and SHAPE.match(arm) is not None


def kernel_of(arm, hint='rgm136'):
    if arm.startswith('gemmLn') and not arm.startswith('gemmLnc'):
        return 'rgm211'
    if not arm.startswith('gemmL'):
        return 'run_gemm'
    return hint


class Model:
    def __init__(self, params_path=PARAMS, features_path=FEATURES):
        import mm1_v32  # noqa: E402
        import time_v31 as TV  # noqa: E402
        self.TV = TV
        self.par = json.load(open(params_path))
        self.a = np.array([self.par['constants']['a_hop'], self.par['constants']['a_lag'], self.par['constants']['a_al']], float)
        self.P32 = json.load(open(os.path.join(V32, 'out', 'mm1_v32_params.json')))
        self.M32 = mm1_v32.Model(self.P32)
        self.th = self.P32['time']['theta']
        self.form = self.P32['time']['form']
        self.ths = dict(self.th)
        for k in MEMK:
            self.ths[k] = self.th[k] * 1.01
        self.PS = json.load(open(features_path)) if os.path.exists(features_path) else {}
        self.PS_made = {}
        self._af4 = None

    def features(self, arm, mask):
        """posimb's features and A1 at one in-scope configuration (the cached record if any, else made by the walk)"""
        m = int(mask, 16)
        key = '%s|0x%x' % (arm, m)
        if key not in self.PS:
            MB, NB, KB = (int(x) for x in SHAPE.match(arm).groups())
            r = private_shared(MB, NB, KB, m)
            r.update(mesh_lat(m))
            self.PS[key] = r
            self.PS_made[key] = r
        r = self.PS[key]
        F = r['Fp'] + r['Fs']
        return {'G1core': r['Lmean_act'] / r['Lmean_full'] - 1.0,
                'LAGcore': ((r['Lmax_act'] - r['Lmean_act']) / r['Lmean_full']) * (r['Fp'] / F if F > 0 else 0.0),
                'A1': A1_of(m), 'Fp': r['Fp'], 'Fs': r['Fs'], 'Lmean_act': r['Lmean_act'], 'Lmax_act': r['Lmax_act']}

    def elasticity(self, specs):
        pts = [{'arm': s['arm'], 'kernel': kernel_of(s['arm'], s.get('kernel', 'rgm136')), 'fmt': s['fmt'], 'mask': s.get('mask', '0xffffffff'),
                'f': float(s.get('f', 600.0))} for s in specs]
        en = self.TV.Engine31(pts)
        T0 = en.predict(self.th, self.form)
        T1 = en.predict(self.ths, self.form)
        return T0, np.log(T1 / T0) / np.log(1.01), pts

    @staticmethod
    def base_fields(p):
        o = {'cycles_per_op_wall': p['cycles_per_op_wall'], 'cycles_per_op_mean': p.get('cycles_per_op_mean'), 'T_op_us': p['T_op_us'],
             'seconds_per_gemm': p.get('seconds_per_gemm')}
        if 'W_over_idle' in p:
            o.update({'W_over_idle': p['W_over_idle'], 'A_W': p['W_affine']['A_W'], 'B_W_us': p['W_affine']['B_W_us'],
                      'J_over_idle_per_gemm': p.get('J_over_idle_per_gemm')})
            rl = p.get('rest_law')
            o['J_at_rest_per_gemm'] = rl['J_at_rest_per_gemm_REPORTED'] if rl else None
            o['_P_rest'] = rl['P_rest_W'] if rl else None
        return o

    @staticmethod
    def compose(b, gw, gm):
        """posimb's h01_freeze.compose: the term's factors on MM1-v3.2's fields, energy MM1-v3.2's affine at the new op time"""
        o = {'cycles_per_op_wall': b['cycles_per_op_wall'] * gw,
             'cycles_per_op_mean': (b['cycles_per_op_mean'] * gm if b['cycles_per_op_mean'] is not None else None),
             'T_op_us': b['T_op_us'] * gw, 'seconds_per_gemm': (b['seconds_per_gemm'] * gw if b['seconds_per_gemm'] is not None else None)}
        if 'A_W' in b:
            A, B = b['A_W'], b['B_W_us']
            W = A + B / o['T_op_us']
            o.update({'W_over_idle': W, 'A_W': A, 'B_W_us': B, 'J_over_idle_per_gemm': W * o['seconds_per_gemm']})
            o['J_at_rest_per_gemm'] = (b['_P_rest'] + W) * o['seconds_per_gemm'] if b.get('_P_rest') is not None else None
        return o

    def predict_many(self, specs, base=None):
        """rows {'MM1-v3.2': MM1-v3.2's fields, LABEL: the term's fields, 'term': the factors and features, 'in_scope'}"""
        base = self.M32.predict_many(specs) if base is None else base
        T0, e, pts = self.elasticity(specs)
        out = []
        for j, (s, bp, pt) in enumerate(zip(specs, base, pts)):
            assert abs(T0[j] / bp['T_op_us'] - 1) < 1e-12, 'engine and predictor differ'
            bf = self.base_fields(bp)
            sc = in_scope(pt['arm'], pt['mask'], pt['kernel'])
            if sc:
                ft = self.features(pt['arm'], pt['mask'])
                phi = np.array([e[j] * ft['G1core'], e[j] * ft['LAGcore'], e[j] * ft['A1']])
                gw = float(np.clip(1.0 + phi @ self.a, 0.3, 3.0))
                gm = float(np.clip(1.0 + self.a[0] * phi[0] + self.a[2] * phi[2], 0.3, 3.0))
            else:
                ft, phi, gw, gm = {}, np.zeros(3), 1.0, 1.0
            cf = self.compose(bf, gw, gm) if sc else {k: bf.get(k) for k in KEYS}
            cf['rest_law_W'] = bf.get('_P_rest')
            out.append({'MM1-v3.2': {k: bf.get(k) for k in KEYS} | {'rest_law_W': bf.get('_P_rest')}, LABEL: cf, 'in_scope': bool(sc),
                        'term': {'e': float(e[j]), 'Phi_hop': float(phi[0]), 'Phi_lag': float(phi[1]), 'Phi_al': float(phi[2]), 'g_wall': gw,
                                 'g_mean': gm, **ft}, '_base': bp})
        return out

    # ------------------------------------------------------------------------------------------------ AF4 (models_e222.af4_rows' form)
    def _load_af4(self):
        sys.path.insert(0, V3)
        import mm1_core_v3  # noqa: E402
        src = open(os.path.join(AF4_DIR, 'scripts', 's02_fit.py')).read()
        ns = {'np': np, 'C': mm1_core_v3, 'X1': float(self.th['x1'])}
        exec(src[src.index('def feats('):src.index('FORMS = {')], ns)
        FIT = json.load(open(os.path.join(AF4_DIR, 'data', 'fit-record.json')))
        assert FIT['choice']['form'] == 'AF4' and FIT['choice']['status'] == 'KEPT', FIT['choice']
        self._af4 = {'feats': ns['feats'], 'const': FIT['forms']['AF4']['constants_all_data_pJ'],
                     'c1v': self.P32['energy']['F3']['c1_pJ'], 'c2v': self.P32['energy']['F3']['c2_pJ']}

    def af4_row(self, s, o):
        """AF4's frozen per-row form at one point (MM1-v3.2's output o): F3 removed, AF4's term added at MM1-v3.2's op time; time MM1-v3.2's"""
        if self._af4 is None:
            self._load_af4()
        A = self._af4
        lnc = s['arm'].startswith('gemmLnc')
        if 'W_affine' not in o:
            # MM1-v3.2 prices no energy here (a data kind it has no count for): AF4 cannot act; time only, energy None
            assert not lnc, ('AF4 needs MM1-v3.2 energy at a gemmLnc point', s['arm'], s['kind'])
            return {'T_op_us': o['T_op_us'], 'cycles_per_op_wall': o['cycles_per_op_wall'], 'cycles_per_op_mean': o.get('cycles_per_op_mean'),
                    'seconds_per_gemm': o.get('seconds_per_gemm'), 'W_over_idle': None, 'A_W': None, 'B_W_us': None,
                    'J_over_idle_per_gemm': None, 'J_at_rest_per_gemm': None, 'rest_law_W': None, 'in_scope': False}
        A_, B_ = o['W_affine']['A_W'], o['W_affine']['B_W_us']
        t = o['T_op_us']
        Wv = A_ + B_ / t
        f3 = o['F3_W_at_own_t']
        rl = o.get('rest_law') or {}
        sec = o['seconds_per_gemm']
        if lnc:
            assert abs(o['F3_dup'] - 26.0) < 1e-12
            S_own = f3 / (A['c1v'] * 26.0 + A['c2v'] * o['F3_first'])
            Q = 0.5 * (np.array(o['Q0']) + np.array(o['Q1']))
            sh = tuple(int(x) for x in SHAPE_ANY.match(s['arm']).groups())
            ft = A['feats'](sh, s['fmt'], Q.sum(axis=1).tolist(), Q.sum(axis=0).tolist(), s['mask'])
            dW = S_own * float(np.dot(A['const'], [ft['dup'], ft['R4']]))
        else:
            assert f3 == 0.0, (s['arm'], f3)
            dW = 0.0
        Wn = Wv - f3 + dW
        Bn = B_ - f3 * t + dW * t
        return {'T_op_us': t, 'cycles_per_op_wall': o['cycles_per_op_wall'], 'cycles_per_op_mean': o.get('cycles_per_op_mean'), 'seconds_per_gemm': sec,
                'W_over_idle': Wn, 'A_W': A_, 'B_W_us': Bn, 'J_over_idle_per_gemm': Wn * sec,
                'J_at_rest_per_gemm': ((rl['P_rest_W'] + Wn) * sec) if rl else None, 'rest_law_W': rl.get('P_rest_W'), 'in_scope': lnc}

    def predict_many_with_af4(self, specs):
        """'MM1-v3.2 + AF4 + posimb-mask' by construction: per row the one term that acts (exit 5 if both, or if a term moved a row outside
        its scope beyond 1e-12 relative)"""
        rows = self.predict_many(specs)
        for s, r in zip(specs, rows):
            b = r['MM1-v3.2']
            af = self.af4_row(s, r['_base'])
            r['MM1-v3.2 + AF4'] = af
            if r['in_scope'] and af['in_scope']:
                print('posimb_mask: REFUSED at %s %s: both terms in scope' % (s['arm'], s['mask']))
                sys.exit(5)
            for nm, sc, x in (('posimb-mask', r['in_scope'], r[LABEL]), ('AF4', af['in_scope'], af)):
                if not sc and not close(x, b):
                    print('posimb_mask: REFUSED at %s %s: %s moved a row outside its scope' % (s['arm'], s['mask'], nm))
                    sys.exit(5)
            if r['in_scope']:
                c, how = {k: r[LABEL].get(k) for k in KEYS}, 'posimb-mask alone (AF4 equals MM1-v3.2 here)'
            elif af['in_scope']:
                c, how = {k: af.get(k) for k in KEYS}, 'AF4 alone (posimb-mask equals MM1-v3.2 here)'
            else:
                c, how = {k: b.get(k) for k in KEYS}, 'MM1-v3.2 (no term acts)'
            c['rest_law_W'] = b.get('rest_law_W')
            c['how'] = how
            r[LABEL_AF4] = c
        return rows


def close(x, y, tol=1e-12):
    for k in KEYS:
        a, b = x.get(k), y.get(k)
        if a is None and b is None:
            continue
        if a is None or b is None or abs(a - b) > tol * max(abs(a), abs(b), 1e-300):
            return False
    return True


if __name__ == '__main__':
    M = Model()
    r = M.predict_many_with_af4([{'card': 'aifoundry3 card 0', 'arm': 'gemmL2x6x10', 'fmt': 'fp32', 'kind': 'zeros', 'mask': '0x4000', 'f': 600.0,
                                  'kernel': 'rgm136'}])[0]
    print(json.dumps({k: r[k] for k in ('MM1-v3.2', LABEL, LABEL_AF4, 'term', 'in_scope')}, indent=1, default=float))
