#!/usr/bin/env python3
"""MM1-v3.2, the lab's matmul model: the predictor, frozen with its constants (out/mm1_v32_params.json). From a matmul's size, format, data
kind, shire mask, card, clock and THE OPERATIONS ITS KERNEL CONTAINS (the census, ../v3.1/inputs/census/census-v3.1.json) it gives the clock
cycles (the slowest minion's and the counter's mean), the seconds, the joules over idle and with the card at rest, and the transistor
switches in MM1-v3's classes. Desk; numpy. MM1-v3.1's predictor (../v3.1/mm1_v31.py) line for line with DECLARED-v32.md's two changes:
  - time: MM1-v3.1's op time (time_v31.Engine31, T5r+G0+n32) at MM1-v3.2's refitted constants, times the layout factor
    clip(1 + sum a_i x_i, 0.3, 3.0) at the subset points of rgm136's gemmL loop when section 3's rule chose a term (out/mm1_v32_params.json
    > time > layout_term; 'none': no factor), the features by layout_v32 (v01_map's functions);
  - energy: E1t plus the gemmLnc term F3 (energy_v32.W32: dW = D sL (n / t_op) 1e-12 (c1 dup + c2 first)), at MM1-v3.2's refitted
    constants; F3 is exactly 0 at every cooperative loop. W over idle at a measured op time t (us) = A + B / t, as MM1-v3.1's W_affine.

    import mm1_v32; M = mm1_v32.Model(json.load(open('out/mm1_v32_params.json')))
    M.predict_many([{'card': ..., 'arm': ..., 'fmt': ..., 'kind': ..., 'mask': ..., 'f': ..., 'kernel': ...}, ...])

Labels: every constant is a desk fit made after its data existed (post hoc as an act); a forecast for a never-run point is blind only once
its sha256 is in a pushed commit before that point's first datum.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
V31 = os.path.normpath(os.path.join(HERE, '..', 'v3.1'))
sys.path.insert(0, HERE)
if V31 not in sys.path:
    sys.path.insert(1, V31)
import time_v31 as TV  # noqa: E402  (first: T7's load of engine_v3 at its pins)
import energy_v32 as EV  # noqa: E402
import mm1_v31 as M31  # noqa: E402

E = TV.E
C = TV.C
BENCH_RESIDENT = M31.BENCH_RESIDENT
COUNT_FOOTING = M31.COUNT_FOOTING
imbalance_mean = M31.imbalance_mean
LAYOUT_COLS = {'none': [], 'N3': ['N3'], 'N1+N2': ['N1', 'N2'], 'G1': ['G1'], 'G1+N1': ['G1', 'N1'], 'F1': ['fresh32'], 'fresh24': ['fresh24']}


class Model:
    def __init__(self, params, t7_cache_dir=None, feature_cache=None):
        self.P = params
        self.th = params['time']['theta']
        self.form = params['time']['form']
        self.Ep = params['energy']['theta']
        self.eform = params['energy']['form']
        assert self.eform == 'E1t+F3', self.eform
        self.layout = params['time'].get('layout_term') or {'enters': 'none'}
        self.t7_cache_dir = t7_cache_dir
        self.feature_cache = feature_cache
        self._store = None

    # ---------------------------------------------------------------- the layout factor
    def layout_factor(self, pts):
        name = self.layout.get('enters', 'none')
        if name == 'none':
            return np.ones(len(pts)), [None] * len(pts)
        import layout_v32 as LY
        cols = LAYOUT_COLS[name]
        a = np.asarray(self.layout['a_all'], float)
        if self._store is None:
            self._store = LY.FeatureStore(self.feature_cache or os.path.join(HERE, 'out', 'layout', 'features-v32.json'))
        caps = tuple(sorted({int(c[5:]) for c in cols if c.startswith('fresh')})) or (32,)
        out, rows = np.ones(len(pts)), []
        for j, p in enumerate(pts):
            if not LY.is_layout_point(p):
                rows.append(None)
                continue
            r, _ = LY.feat_row(p['arm'], LY.mask_int(p['mask']), self._store, caps=caps, check=False)
            x = np.array([r[c] for c in cols], float)
            out[j] = float(np.clip(1.0 + x @ a, 0.3, 3.0))
            rows.append({c: r[c] for c in cols})
        return out, rows

    def time_many(self, pts):
        en = TV.Engine31(pts, t7_cache_dir=self.t7_cache_dir)
        T, Q0, Q1 = en.predict(self.th, self.form, return_q=True)
        fac, rows = self.layout_factor(pts)
        return T * fac, Q0, Q1, en, fac, rows

    def predict_many(self, specs):
        pts = []
        for s in specs:
            pre, b = E.arm_parts(s['arm'])
            kernel = s.get('kernel', 'rgm136')
            if pre == 'gemmLn':
                kernel = 'rgm211'
            if pre is None:
                kernel = 'run_gemm'
            pts.append({'arm': s['arm'], 'kernel': kernel, 'fmt': s['fmt'], 'mask': s.get('mask', '0xffffffff'), 'f': float(s.get('f', 600.0))})
        T, Q0, Q1, en, fac, rows = self.time_many(pts)
        return [self._one(s, pt, float(T[j]), Q0[j], Q1[j], en, j, float(fac[j]), rows[j]) for j, (s, pt) in enumerate(zip(specs, pts))]

    def predict(self, card, arm, fmt, kind, mask='0xffffffff', f=600.0, kernel='rgm136', **kw):
        d = {'card': card, 'arm': arm, 'fmt': fmt, 'kind': kind, 'mask': mask, 'f': f, 'kernel': kernel}
        d.update(kw)
        return self.predict_many([d])[0]

    def _one(self, s, pt, t, Q0, Q1, en, j, fac, frow):
        card, arm, fmt, kind, mask, f, kernel = s['card'], pt['arm'], pt['fmt'], s['kind'], pt['mask'], pt['f'], pt['kernel']
        pre, b = E.arm_parts(arm)
        mi = C.mask_info(mask)
        n = s.get('minions') if s.get('minions') is not None else 32 * mi['n']
        Q = 0.5 * (Q0 + Q1)
        n2, n3, nF = (float(x) for x in C.lines(Q))
        MB = b[0] if b else 1
        sh = C.Shape('gemmL%dx%dx%d' % b if pre is not None else arm, C.FULL, masked_map=False)
        rho = C.rho_mean(sh, n2) * C.rho_sub(mi, self.th) * imbalance_mean(mi, MB, self.P['time'].get('imbalance_mean'))
        ops = s.get('ops') if s.get('ops') is not None else (64 * b[0] * b[1] * b[2] if b else None)
        loop = E.loop_of(arm, kernel)
        DA, DB = en.D_classes(self.th, self.form, en.eng.f)
        out = {'model': 'MM1-v3.2', 'card': card, 'arm': arm, 'kernel': kernel, 'loop': loop, 'fmt': fmt, 'kind': kind, 'mask': mask,
               'f_mhz': f, 'T_op_us': t, 'cycles_per_op_wall': t * f, 'cycles_per_op_mean': t * f / rho, 'rho_wall_over_mean': rho,
               'layout_factor': fac, 'layout_term': self.layout.get('enters', 'none'), 'layout_features': frow,
               'lines_L2_L3_F_per_shire_op': [n2, n3, nF], 'Q0': Q0.tolist(), 'Q1': Q1.tolist(),
               'footprint_MB': (C.footprint(*b) if b else None), 'minions': n, 'ops_per_minion_per_gemm': ops,
               'census_path_D_cycles_by_place': {'D_A': [float(x * f) for x in DA[j]], 'D_B': [float(x * f) for x in DB[j]],
                                                 'places': ['L2', 'L3', 'fresh']},
               'floor_cycles_measured_tenb': C.FLOOR[fmt], 'bench_resident_cycles_simulated': BENCH_RESIDENT[fmt],
               'census_instructions_per_op': (EV.EV.CENSUS31['loops'][loop]['instructions_per_op'] if loop else None)}
        if ops:
            out['cycles_per_gemm_wall'] = ops * t * f
            out['seconds_per_gemm'] = ops * t * 1e-6
        V = s.get('V') if s.get('V') is not None else C.volts(card, f)
        EPt = [{'card': card, 'fmt': fmt, 'kind': kind, 'arm': arm, 'kernel': kernel, 'minions': n, 'mask': mask, 'f': f, 'T': t,
                'w': 0.0, 'idle_w': None, 'G': (s['G'] if s.get('G') is not None else C.G_of_f(card, f)), 'die_start': s.get('t0_c'),
                's': (V / 0.517) ** 2}]
        X = EV.Features32(EPt)
        if not bool(X.usable3[0]):
            out['energy'] = 'NOT FORECAST: no committed switch count or no phi by DECLARED-v32.md section 1.2 for this kind and format'
            return out
        i = np.array([0])
        rC = EV.rC_of(X.Ffull, self.th, self.form)
        a2, a3, aF = np.array([n2]), np.array([n3]), np.array([nF])
        first = EV.first_of(Q[None, :, :], X)
        p = self.Ep
        W1 = float(EV.W32(p, X, i, a2, a3, aF, np.array([1.0]), rC, self.eform, first)[0])
        W2 = float(EV.W32(p, X, i, a2, a3, aF, np.array([2.0]), rC, self.eform, first)[0])
        Bd = 2.0 * (W1 - W2)
        Ad = W1 - Bd
        W = Ad + Bd / t
        f3 = float(EV.f3_W(p, X, i, np.array([t]), first)[0])
        out.update({'V': V, 's_V': float(X.s[0]), 'G_W': float(X.G[0]), 'die_start_c': float(X.T0[0]), 'phi': float(X.phi[0]),
                    'phi_rule': X.phi_rule[0], 'W_over_idle': W, 'F3_dup': float(X.dup[0]), 'F3_first': float(first[0]), 'F3_W_at_own_t': f3,
                    'W_affine': {'A_W': Ad, 'B_W_us': Bd, 'how': 'W over idle at a measured op time t_us (the slowest minion) = A + B / t_us, at this clock and die'}})
        if ops:
            tg = out['seconds_per_gemm']
            out['J_over_idle_per_gemm'] = W * tg
            terms, die = EV.terms32(p, X, i, a2, a3, aF, np.array([t]), rC, self.eform, first)
            Jt = {k: float(v[0] * die[0] * tg) for k, v in terms.items()}
            out['J_over_idle_by_class'] = Jt
            out['switches'] = self.switches(Jt, fmt, kind, b[2] if b else 1, ops * n, p)
            rl = (self.P.get('rest_law') or {}).get(card)
            if rl:
                T0 = s.get('t0_c') if s.get('t0_c') is not None else rl['T0_forecast_c']
                Pr = rl['a'] * T0 * T0 + rl['b'] * T0 + rl['c']
                out['rest_law'] = {'P_rest_W': Pr, 'T0_c': T0, 'J_at_rest_per_gemm_REPORTED': (Pr + W) * tg, 'source': rl['source']}
        return out

    def switches(self, Jt, fmt, kind, KB, N_op, p):
        """MM1-v3.1's classes (M31.Model.switches), with F3's duplicate-line joules among the lines (estimated, the wide band)"""
        Jt2 = dict(Jt)
        dup = Jt2.pop('gemmLnc_duplicate_lines', 0.0)
        out = M31.Model.switches(self, Jt2, fmt, kind, KB, N_op, p)
        kappa = out['kappa_fin_edges_per_J_board']
        out['lines']['gemmLnc_duplicate_lines_energy_J'] = dup
        Jl = out['lines']['energy_J'] + dup
        out['lines'].update({'energy_J': Jl, 'count_estimated': Jl * kappa, 'band': [0.5 * Jl * kappa, 2.0 * Jl * kappa],
                             'label': 'estimated, wide band (x0.5 to x2): the line, C-store and gemmLnc duplicate-line joules x kappa'})
        return out
