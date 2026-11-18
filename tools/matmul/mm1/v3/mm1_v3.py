#!/usr/bin/env python3
"""MM1-v3, the lab's matmul model: the predictor. From a matmul's size, format, data kind, shire mask, card, clock and THE OPERATIONS ITS
KERNEL CONTAINS (the kernel's census: inputs/census/census-v3.json) it gives the clock cycles (the slowest minion's and the counter's mean), the
seconds, the joules over idle and with the card at rest, the transistor switches in the spec's six classes, and the timing simulation's
columns beside them. Desk; numpy. The equations are engine_v3.py's (time) and energy_v3.py's (energy); the constants out/mm1_v3_params.json's.

    import mm1_v3; M = mm1_v3.Model(params); M.predict(card, arm, fmt, kind, mask, f_mhz, kernel='rgm136', V=None, t0_c=None, ...)

arm: gemmL<MB>x<NB>x<KB> (rgm136's gemmL loop, or rgm211's own gemmL copy with kernel='rgm211'), gemmLn<..> (rgm211's swapped walk),
gemmLnc<..> (rgm136's non-cooperative loads), or a run_gemm c-arm. kind: zeros, ones, random, sparse50, or E210's nine fp32 patterns
(negzero, signs, lowmant8, highmant8, bhalfeq, badjeq, hd4, maxalte, arow50): the kinds with a committed switch count; any other kind's
energy is NOT FORECAST (its time is). THE CLOCK is an input: the card's pinned 600 MHz, or a governed card's measured clock; the volts and
the governed base follow from it (mm1_core_v3.volts, G_of_f) unless given.
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
import energy_v3 as EN  # noqa: E402
import engine_v3 as E  # noqa: E402
import mm1_core_v3 as C  # noqa: E402

BENCH_RESIDENT = {'fp32': 546.0, 'fp16': 546.0, 'int8': 318.0}   # the RTL bench (+7.75), A and B resident (simulated)
SIGNAL_HI_OVER_LO = {}


def imbalance_mean(mi, MB, imb):
    """MM1-v2's counter-mean imbalance (only when MB >= 2; its constants refitted on the same four E206 points: identical)"""
    if imb is None or mi['full'] or mi['C'] < 4 or mi['R'] >= 4 or MB < 2:
        return 1.0
    return 1.0 + imb['eta_m'] * ((4.0 - mi['R']) / 3.0) ** imb['gamma']


def counts_full(fmt, kind, KB):
    """the committed desk counts an op: signal lo / hi fin edges and clock fin edges, and the ungated kind's clock (for the gate)"""
    if fmt == 'fp32':
        key = {'random': 'randn'}.get(kind, kind)
        sh = EN.E210C['S1' if KB == 1 else 'S2']
        if key not in sh:
            return None
        r, ru = sh[key], sh['ones']
        m = EN.MACS[fmt]
        return {'signal_lo': r['signal_lo'] * m, 'signal_hi': r['signal_hi'] * m, 'clock': r['clock'] * m, 'clock_ungated': ru['clock'] * m,
                'source': f"E210's desk counts at GEMM states ({'S1, KB = 1' if KB == 1 else 'S2, KB >= 2'}), switch-counts-e210.json",
                'footing': COUNT_FOOTING['fp32']}
    key = {'random': 'randn' if fmt == 'fp16' else 'full'}.get(kind, kind)
    rk = f'{fmt}.{key}'
    if rk not in EN.SWT:
        return None
    r, ru = EN.SWT[rk]['fin_edges_per_op'], EN.SWT[f'{fmt}.ones']['fin_edges_per_op']
    return {'signal_lo': r['signal_lo_zero_delay'], 'signal_hi': r['signal_hi_timed'], 'clock': r['clock'], 'clock_ungated': ru['clock'],
            'source': "MM1-v1's switch table at the harness launch points (switch_table.json)", 'footing': COUNT_FOOTING[fmt]}


# what each format's signal count covers (the count files' own footings; corrected after verify-mm1v3's finding 4, fix-mm1v3)
COUNT_FOOTING = {
    'fp32': ("counted (desk): the gate-level bench's VPU net toggles a MAC at GEMM states x the fin edges a toggle calibrated on the fp32 "
             "unit's gate-level run (E210, MM1-v1 units)"),
    'fp16': ("estimated (desk), not counted: fp16's RTL toggles x the fp32 gate/RTL ratio (no fp16 gate-level run; MM1-v1's switch table "
             "footing)"),
    'int8': ("counted (desk) around the arithmetic only: the behavioural RTL has no nets inside the int8 multiply, product sum and add, so "
             "the count is the VPU around them (MM1-v1's switch table footing); m_int8 scales it to the data term the card shows"),
}


class Model:
    def __init__(self, params):
        self.P = params
        self.th = params['time']['theta']
        self.form = params['time']['form']
        self.Ep = params['energy']['theta']
        self.eform = params['energy']['form']

    def time(self, arm, kernel, fmt, mask, f):
        pt = {'arm': arm, 'kernel': kernel, 'fmt': fmt, 'mask': mask, 'f': float(f)}
        eng = E.TimeEngine([pt])
        T, Q0, Q1 = eng.predict(self.th, self.form, return_q=True)
        return float(T[0]), Q0[0], Q1[0], eng

    def predict(self, card, arm, fmt, kind, mask='0xffffffff', f=600.0, kernel='rgm136', V=None, ops=None, minions=None, t0_c=None, G=None):
        pre, b = E.arm_parts(arm)
        if pre == 'gemmLn':
            kernel = 'rgm211'
        if pre is None:
            kernel = 'run_gemm'
        t, Q0, Q1, eng = self.time(arm, kernel, fmt, mask, f)
        mi = C.mask_info(mask)
        n = minions if minions is not None else 32 * mi['n']
        Q = 0.5 * (Q0 + Q1)
        n2, n3, nF = (float(x) for x in C.lines(Q))
        MB = b[0] if b else 1
        if pre is not None:
            sh = C.Shape('gemmL%dx%dx%d' % b, C.FULL, masked_map=False)
        else:
            sh = C.Shape(arm, C.FULL, masked_map=False)
        rho = C.rho_mean(sh, n2) * C.rho_sub(mi, self.th) * imbalance_mean(mi, MB, self.P['time'].get('imbalance_mean'))
        ops = ops if ops is not None else (64 * b[0] * b[1] * b[2] if b else None)
        loop = E.loop_of(arm, kernel)
        out = {'model': 'MM1-v3', 'card': card, 'arm': arm, 'kernel': kernel, 'loop': loop, 'fmt': fmt, 'kind': kind, 'mask': mask, 'f_mhz': f,
               'T_op_us': t, 'cycles_per_op_wall': t * f, 'cycles_per_op_mean': t * f / rho, 'rho_wall_over_mean': rho,
               'lines_L2_L3_F_per_shire_op': [n2, n3, nF], 'Q0': Q0.tolist(), 'Q1': Q1.tolist(),
               'footprint_MB': (C.footprint(*b) if b else None), 'minions': n, 'ops_per_minion_per_gemm': ops,
               'census_path_D_cycles': dict(zip(('D_A', 'D_B'), E.path_D(loop))),
               'floor_cycles_measured_tenb': C.FLOOR[fmt], 'bench_resident_cycles_simulated': BENCH_RESIDENT[fmt],
               'sim_steps_per_minion_per_gemm': (C.sim_steps(sh) if loop == 'rgm136 gemmL' else None),
               'census_instructions_per_op': (E.CENSUS['loops'][loop]['instructions_per_op'] if loop else None)}
        if ops:
            out['cycles_per_gemm_wall'] = ops * t * f
            out['seconds_per_gemm'] = ops * t * 1e-6
        # energy
        EP = [{'card': card, 'fmt': fmt, 'kind': kind, 'arm': arm, 'kernel': kernel, 'minions': n, 'mask': mask, 'f': f, 'T': t,
               'w': 0.0, 'idle_w': None, 'G': (G if G is not None else C.G_of_f(card, f)), 'die_start': t0_c,
               's': ((V if V is not None else C.volts(card, f)) / 0.517) ** 2}]
        X = EN.Features(EP)
        ok = bool(X.usable3[0]) if self.eform == 'v3' else bool(X.usable2[0])
        if not ok:
            out['energy'] = 'NOT FORECAST: no committed switch count (or ledger row) for this kind and format'
            return out
        i = np.array([0])
        rC = EN.rC_of(X.Ffull, self.th, self.form)
        a_n2, a_n3, a_nF = np.array([n2]), np.array([n3]), np.array([nF])
        p = self.Ep
        # W = (A + B / t) x die: A from W at t -> infinity's constant part; B by two evaluations
        W1 = float(EN.W_v3(p, X, i, a_n2, a_n3, a_nF, np.array([1.0]), rC, self.eform)[0])
        W2 = float(EN.W_v3(p, X, i, a_n2, a_n3, a_nF, np.array([2.0]), rC, self.eform)[0])
        Bd = 2.0 * (W1 - W2)
        Ad = W1 - Bd
        W = Ad + Bd / t
        out.update({'V': (V if V is not None else C.volts(card, f)), 's_V': X.s[0], 'G_W': X.G[0], 'die_start_c': X.T0[0],
                    'W_over_idle': W, 'W_affine': {'A_W': Ad, 'B_W_us': Bd,
                                                   'how': 'W over idle at a measured op time t_us (the slowest minion) = A + B / t_us, at this clock and die'}})
        if ops:
            tg = out['seconds_per_gemm']
            out['J_over_idle_per_gemm'] = W * tg
            if self.eform == 'v3':
                terms, die = EN.terms_v3(p, X, i, a_n2, a_n3, a_nF, np.array([t]), rC)
                Jt = {k: float(v[0] * die[0] * tg) for k, v in terms.items()}
                out['J_over_idle_by_class'] = Jt
                out['switches'] = self.switches(Jt, fmt, kind, b[2] if b else 1, ops * n, p)
            rl = (self.P.get('rest_law') or {}).get(card)
            if rl:
                T0 = t0_c if t0_c is not None else rl['T0_forecast_c']
                Pr = rl['a'] * T0 * T0 + rl['b'] * T0 + rl['c']
                out['rest_law'] = {'P_rest_W': Pr, 'T0_c': T0, 'J_at_rest_per_gemm_REPORTED': (Pr + W) * tg, 'source': rl['source']}
        return out

    def switches(self, Jt, fmt, kind, KB, N_op, p):
        """the spec's six classes (section 7), each labelled; N_op = tensor ops a GEMM (all minions)"""
        c = counts_full(fmt, kind, KB)
        kappa = 1.0 / (p['b0'] * 1e-17)            # fin edges a joule (board), the fitted data constant
        m = {'fp32': 1.0, 'fp16': p['m|fp16'], 'int8': p['m|int8']}[fmt]
        out = {'kappa_fin_edges_per_J_board': kappa, 'm_fmt': m, 'counts_source': c['source'] if c else None,
               'counts_footing': c['footing'] if c else None}
        if c:
            out['counted_signal_fin_edges'] = {'lo_zero_delay': c['signal_lo'] * N_op, 'hi_timed': c['signal_hi'] * N_op,
                                               'label': c['footing'] + '; a MAC x MACs an op x ops'}
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
                               'bench_clock_count_beside': out.get('counted_clock_fin_edges', {}).get('value'),
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
