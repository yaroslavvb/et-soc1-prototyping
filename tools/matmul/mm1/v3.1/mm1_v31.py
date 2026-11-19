#!/usr/bin/env python3
"""MM1-v3.1, the lab's matmul model: the predictor, frozen with its constants (out/mm1_v31_params.json). From a matmul's size, format, data
kind, shire mask, card, clock and THE OPERATIONS ITS KERNEL CONTAINS (the census, inputs/census/census-v3.1.json) it gives the clock cycles
(the slowest minion's and the counter's mean), the seconds, the joules over idle and with the card at rest, and the transistor switches in
MM1-v3's six classes. Desk; numpy. The equations are time_v31.py's (MM1-v3's op time with DECLARED-v31.md items 3, 4 and 8 as its fit chose
them) and energy_v31.py's (MM1-v3's switch route with items 1, 2, 6 and 7); the constants out/mm1_v31_params.json's.

    import mm1_v31; M = mm1_v31.Model(json.load(open('out/mm1_v31_params.json')))
    M.predict_many([{'card': ..., 'arm': ..., 'fmt': ..., 'kind': ..., 'mask': ..., 'f': ..., 'kernel': ...}, ...])

arm: gemmL<MB>x<NB>x<KB> (rgm136's gemmL loop, or rgm211's own gemmL copy with kernel='rgm211'), gemmLn<..> (rgm211's swapped walk),
gemmLnc<..> (rgm136's non-cooperative loads), or a run_gemm c-arm. kind: a kind with a committed switch count and a phi by item 7's rule
(zeros, ones, random, sparse50, E210's nine fp32 patterns, and v31-counts' kinds: E212's plan tiles, E206's real tiles, E207's real:blind4,
blind3 and e37); any other kind's energy is NOT FORECAST (its time is). The clock is an input (the pinned cards' 600 MHz, or a governed
card's measured clock); the volts and the governed base follow from it (mm1_core_v3.volts, G_of_f) unless given.
Labels: every constant is a desk fit made after its data existed (post hoc as an act); a forecast for a never-run point is blind only once
its sha256 is in a pushed commit before that point's first datum.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import time_v31 as TV  # noqa: E402  (first: T7's load of engine_v3 at its pins)
import energy_v31 as EV  # noqa: E402

E = TV.E
C = TV.C
BENCH_RESIDENT = {'fp32': 546.0, 'fp16': 546.0, 'int8': 318.0}
COUNT_FOOTING = {
    'fp32': ("counted (desk): the gate-level bench's VPU net toggles a MAC at GEMM states x the fin edges a toggle calibrated on the fp32 "
             "unit's gate-level run (E210's and v31-counts' rows, MM1-v1 units)"),
    'fp16': ("estimated (desk), not counted: fp16's RTL toggles x the fp32 gate/RTL ratio (no fp16 gate-level run; MM1-v1's switch table "
             "footing)"),
    'int8': ("counted (desk) around the arithmetic only: the behavioural RTL has no nets inside the int8 multiply, product sum and add, so "
             "the count is the VPU around them (MM1-v1's switch table footing); m_int8 scales it to the data term the card shows"),
}


def imbalance_mean(mi, MB, imb):
    """MM1-v2's counter-mean imbalance (only when MB >= 2), as MM1-v3 carries it"""
    if imb is None or mi['full'] or mi['C'] < 4 or mi['R'] >= 4 or MB < 2:
        return 1.0
    return 1.0 + imb['eta_m'] * ((4.0 - mi['R']) / 3.0) ** imb['gamma']


class Model:
    def __init__(self, params, t7_cache_dir=None):
        self.P = params
        self.th = params['time']['theta']
        self.form = params['time']['form']
        self.Ep = params['energy']['theta']
        self.eform = params['energy']['form']
        self.t7_cache_dir = t7_cache_dir

    def time_many(self, pts):
        en = TV.Engine31(pts, t7_cache_dir=self.t7_cache_dir)
        T, Q0, Q1 = en.predict(self.th, self.form, return_q=True)
        return T, Q0, Q1, en

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
        T, Q0, Q1, en = self.time_many(pts)
        out = []
        for j, (s, pt) in enumerate(zip(specs, pts)):
            out.append(self._one(s, pt, float(T[j]), Q0[j], Q1[j], en, j))
        return out

    def predict(self, card, arm, fmt, kind, mask='0xffffffff', f=600.0, kernel='rgm136', **kw):
        d = {'card': card, 'arm': arm, 'fmt': fmt, 'kind': kind, 'mask': mask, 'f': f, 'kernel': kernel}
        d.update(kw)
        return self.predict_many([d])[0]

    def _one(self, s, pt, t, Q0, Q1, en, j):
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
        out = {'model': 'MM1-v3.1', 'card': card, 'arm': arm, 'kernel': kernel, 'loop': loop, 'fmt': fmt, 'kind': kind, 'mask': mask,
               'f_mhz': f, 'T_op_us': t, 'cycles_per_op_wall': t * f, 'cycles_per_op_mean': t * f / rho, 'rho_wall_over_mean': rho,
               'lines_L2_L3_F_per_shire_op': [n2, n3, nF], 'Q0': Q0.tolist(), 'Q1': Q1.tolist(),
               'footprint_MB': (C.footprint(*b) if b else None), 'minions': n, 'ops_per_minion_per_gemm': ops,
               'census_path_D_cycles_by_place': {'D_A': [float(x * f) for x in DA[j]], 'D_B': [float(x * f) for x in DB[j]],
                                                 'places': ['L2', 'L3', 'fresh']},
               't7_mapped': bool(self.form.get('layout') == 'T7' and TV.T7.applies(pt)),
               'floor_cycles_measured_tenb': C.FLOOR[fmt], 'bench_resident_cycles_simulated': BENCH_RESIDENT[fmt],
               'census_instructions_per_op': (EV.CENSUS31['loops'][loop]['instructions_per_op'] if loop else None)}
        if ops:
            out['cycles_per_gemm_wall'] = ops * t * f
            out['seconds_per_gemm'] = ops * t * 1e-6
        V = s.get('V') if s.get('V') is not None else C.volts(card, f)
        EP = [{'card': card, 'fmt': fmt, 'kind': kind, 'arm': arm, 'kernel': kernel, 'minions': n, 'mask': mask, 'f': f, 'T': t,
               'w': 0.0, 'idle_w': None, 'G': (s['G'] if s.get('G') is not None else C.G_of_f(card, f)), 'die_start': s.get('t0_c'),
               's': (V / 0.517) ** 2}]
        X = EV.Features31(EP)
        if not bool(X.usable3[0]):
            out['energy'] = 'NOT FORECAST: no committed switch count or no phi by DECLARED-v31.md item 7 for this kind and format'
            return out
        i = np.array([0])
        rC = EV.rC_of(X.Ffull, self.th, self.form)
        a2, a3, aF = np.array([n2]), np.array([n3]), np.array([nF])
        p = self.Ep
        W1 = float(EV.W31(p, X, i, a2, a3, aF, np.array([1.0]), rC, self.eform)[0])
        W2 = float(EV.W31(p, X, i, a2, a3, aF, np.array([2.0]), rC, self.eform)[0])
        Bd = 2.0 * (W1 - W2)
        Ad = W1 - Bd
        W = Ad + Bd / t
        out.update({'V': V, 's_V': float(X.s[0]), 'G_W': float(X.G[0]), 'die_start_c': float(X.T0[0]), 'phi': float(X.phi[0]),
                    'phi_rule': X.phi_rule[0], 'W_over_idle': W,
                    'W_affine': {'A_W': Ad, 'B_W_us': Bd, 'how': 'W over idle at a measured op time t_us (the slowest minion) = A + B / t_us, at this clock and die'}})
        if ops:
            tg = out['seconds_per_gemm']
            out['J_over_idle_per_gemm'] = W * tg
            terms, die = EV.terms31(p, X, i, a2, a3, aF, np.array([t]), rC, self.eform)
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
        """MM1-v3's six classes, each labelled; N_op = tensor ops a GEMM (all minions)"""
        c = EV.counts_full31(fmt, kind, KB)
        kappa = 1.0 / (p['b0'] * 1e-17)
        m = {'fp32': 1.0, 'fp16': p['m|fp16'], 'int8': p['m|int8']}[fmt]
        out = {'kappa_fin_edges_per_J_board': kappa, 'm_fmt': m, 'counts_source': c['source'] if c else None,
               'counts_footing': COUNT_FOOTING[fmt] if c else None}
        if c:
            out['counted_signal_fin_edges'] = {'lo_zero_delay': c['signal_lo'] * N_op, 'hi_timed': c['signal_hi'] * N_op,
                                               'label': COUNT_FOOTING[fmt] + '; a MAC x MACs an op x ops'}
            out['counted_clock_fin_edges'] = {'value': c['clock'] * N_op, 'label': 'counted (desk): the bench clock nets x 39.8 fins a toggle'}
            out['gate_counted_clock_fin_edges_removed'] = {'value': (c['clock_ungated'] - c['clock']) * N_op,
                                                           'energy_saved_J': -Jt['zero_gate_saving'],
                                                           'label': 'counted (desk) and estimated (the fitted gate energy)'}
        out['data_term_energy_equivalent'] = {'value': Jt['data_switches'] * kappa,
                                              'label': ('estimated, energy-calibrated: the data term joules x kappa = s_V x kc x m x the die '
                                                        'factor x the counted signal fin edges (lo); it equals the counted edges only where '
                                                        'all four factors are 1 (fp32 on aifoundry3 at 0.517 V and 50 C)')}
        if c and c['signal_lo'] > 0:
            out['data_term_energy_equivalent']['factor_over_counted_signal_lo'] = Jt['data_switches'] * kappa / (c['signal_lo'] * N_op)
        out['ungated_base'] = {'energy_J': Jt['ungated_base'], 'count_estimated': Jt['ungated_base'] * kappa,
                               'label': 'measured energy (fitted); its count estimated at kappa, never merged with the bench clock count'}
        Jl = Jt['lines_L2'] + Jt['lines_L3'] + Jt['lines_fresh'] + Jt['C_stores']
        out['lines'] = {'energy_J': Jl, 'count_estimated': Jl * kappa, 'band': [0.5 * Jl * kappa, 2.0 * Jl * kappa],
                        'label': 'estimated, wide band (x0.5 to x2): the line and C-store joules x kappa'}
        out['not_converted_J'] = {'awake_minions': Jt['awake_minions'], 'awake_memory_path': Jt['awake_memory_path'],
                                  'governed_base': Jt['governed_base'], 'instructions_vs_rgm136': Jt['instructions_vs_rgm136'],
                                  'label': 'modelled energy, joules only (awake, memory path awake, governed base, leakage in the die term)'}
        out['scope'] = ('scorable through energy only: count differences at a fixed shape, format and mask (E210 R1 form); not scorable: any '
                        'absolute count, the ungated base count, the lines count, the split inside a rail')
        return out
