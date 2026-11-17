#!/usr/bin/env python3
"""MM1-v1, the lab's matmul model: the predictor. From a matmul's size, format, data kind, shire mask, card and clock it gives the clock cycles
(the slowest minion's and the counter's mean), the seconds, the joules over idle and with the card at rest, the transistor switches, and the timing
simulation's two columns beside them. Desk; numpy. The equations are mm1_core.py's; the constants are mm1_v1_params.json's (fit_v1.py).

    /usr/bin/python3 -I -B mm1_v1.py --params mm1_v1_params.json --points points.csv --out forecasts.csv     (columns below)
    import mm1_v1; mm1_v1.Model(params).predict(card, arm, fmt, kind, mask, f_mhz, V, G=0.0, e_res_spec=None, phi_spec=None)

Scope: mm1_core.SCOPE. Labels: every constant is a desk fit made after its data existed (post hoc as an act); a forecast for a never-run point is
blind only once frozen by sha256 before that point's first datum.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mm1_core as C  # noqa: E402
import kinds_v1 as K  # noqa: E402

SW_TABLE = json.load(open(os.path.join(HERE, 'inputs', 'switch_table.json')))['rows']
CARD_KEY = {'aifoundry3 card 0': 'a3', 'aifoundry2 card 0': 'a2', 'aifoundry1 card 1': 'c1'}
BENCH_RESIDENT = {'fp32': 546.0, 'fp16': 546.0, 'int8': 318.0}   # the RTL bench (+7.75), A and B resident: exact, 306 points blind (simulated)


class Model:
    def __init__(self, params):
        self.P = params
        self.th = params['time']['theta']
        self.rule = params['time']['rule']
        self.masked_map = params['time']['masked_map']
        self.E = params['energy']['theta']
        self._shapes = {}

    def shape(self, arm, mask):
        k = (arm, mask)
        if k not in self._shapes:
            self._shapes[k] = C.Shape(arm, mask, masked_map=self.masked_map)
        return self._shapes[k]

    def t_op(self, sh, fmt, f):
        """us an op, the slowest minion: the two row halves apart (the stride term on B_r0's fresh lines), the L2 time in the gemmL loop"""
        th = self.th
        mi = sh.mi
        Q0, Q1 = sh.Qhalves(th['x50'], th['s'], th['zeta'], self.rule)
        X = 1.0 if mi['full'] else max(1.0 - th['chi'] * (1.0 - mi['n'] / 32.0), 0.05)
        t2 = (th['F2'] / f + th['T2']) if sh.kernel == 'gemmL' else 0.0
        tauA = [t2, th['c3'] / f + th['m3'] * X, th['cF'] / f + th['mF'] * X]
        assert th.get('piF', 0.0) == 0.0 and th.get('pi3', 0.0) == 0.0 and th.get('F2', 0.0) == 0.0, 'the frozen form uses piF0, T2 and zeta only'
        tauB1 = list(tauA)
        tauB0 = list(tauA)
        tauB0[2] = tauA[2] * (1.0 + th['piF0'] * (1.0 if sh.p2 else 0.0))
        tc = C.Tc(fmt, f)
        T = 0.0
        for a in range(3):
            base = max(tc, th['kA'] * tauA[a])
            for b in range(3):
                T += 0.5 * Q0[a, b] * max(base, tauB0[b]) + 0.5 * Q1[a, b] * max(base, tauB1[b])
        return T * C.rho_sub(mi, th), Q0, Q1

    def predict(self, card, arm, fmt, kind, mask='0xffffffff', f=600.0, V=0.522, G=0.0, e_res_spec=None, phi_spec=None, ops=None, t0_c=None,
                minions=None):
        sh = self.shape(arm, mask)
        mi = sh.mi
        n = minions if minions is not None else 32 * mi['n']      # active minions (a row mask inside the shires can halve them: E105's 'half' arms)
        t, Q0, Q1 = self.t_op(sh, fmt, f)
        Q = 0.5 * (Q0 + Q1)
        n2, n3, nF = C.lines(Q)
        rho = C.rho_mean(sh, n2) * C.rho_sub(mi, self.th) * C.rho_imbalance(mi, self.P['time'].get('imbalance_mean'))
        ops = ops if ops is not None else sh.ops
        out = {'scope': C.SCOPE, 'T_op_us': t, 'cycles_per_op_wall': t * f, 'cycles_per_op_mean': t * f / rho, 'rho_wall_over_mean': rho,
               'lines_L2_L3_F': [n2, n3, nF], 'footprint_MB': sh.F_full, 'footprint_masked_MB': sh.F, 'power_of_two_NB': sh.p2,
               'floor_cycles_measured_tenb': C.FLOOR[fmt], 'bench_resident_cycles_simulated': BENCH_RESIDENT[fmt],
               'sim_steps_per_minion_per_gemm': C.sim_steps(sh), 'ops_per_minion_per_gemm': ops, 'minions': n}
        if ops:
            out['cycles_per_gemm_wall'] = ops * t * f
            out['seconds_per_gemm'] = ops * t * 1e-6
        # ---- energy: W(t_op) = A + B / t_op (the affine form the given-seconds score uses)
        ck = CARD_KEY[card]
        if e_res_spec is None:
            kk = 'zeros' if kind == 'zeros' else 'random'
            e_res_spec = {'source': 'ledger', 'keys': [fmt + '.zeros' if kk == 'zeros' else (fmt + ('.full' if fmt == 'int8' else '.randn'))]}
            phi_spec = {'gen': 'zeros'} if kk == 'zeros' else {'gen': 'randn'}
        er, er_txt = K.e_res(card, fmt, e_res_spec)
        if er is None:
            out['energy'] = 'NOT FORECAST: ' + er_txt
            return out
        phi, phi_txt = K.phi(fmt, phi_spec)
        s = (V / 0.517) ** 2
        E = self.E
        u = (n3 + nF) / 192.0
        A = E['Pmin|' + card] * n / 1024.0 + E['Pmem|' + card] * u + E['g'] * G
        Bc = n * s * (er * 1e-9 + 1e-12 * (n2 / 32.0 * (E['b2'] + E['d2'] * phi) + n3 / 32.0 * (E['b3'] + E['d3'] * phi)
                                            + nF / 32.0 * (E['bF'] + E['dF'] * phi)))          # W x us: B / t_op(us) x 1e6
        W = A + Bc / (t * 1e-6)
        out.update({'e_res_nJ': er, 'e_res_source': er_txt, 'phi': phi, 'phi_source': phi_txt, 'W_over_idle': W,
                    'W_affine': {'A_W': A, 'B_W_us': Bc * 1e6, 'how': 'W over idle at a measured op time t_us (the slowest minion) = A + B / t_us'}})
        if ops:
            tg = out['seconds_per_gemm']
            J = W * tg
            out['J_over_idle_per_gemm'] = J
            terms = C.w_terms(E, card, n, t, s, er, Q, phi, G)
            Jt = {k: v * tg for k, v in terms.items()}
            out['J_over_idle_by_class'] = Jt
            kk = fmt + ('.zeros' if kind == 'zeros' else ('.full' if fmt == 'int8' else '.randn')) if kind in ('zeros', 'random') else None
            out['switches'] = C.switches(Jt, tg, W, card, s, ops * n, fmt, kk, SW_TABLE)
            if kk is None:
                out['switches']['counted_note'] = 'no counted netlist row for this kind: the counted part is NOT FORECAST; the estimated part covers the die'
            rl = self.P['rest_law']
            q = rl.get(ck + '_quad') or (rl['aifoundry3_quad'] if ck == 'a3' else None)
            if q is not None:
                T0 = t0_c if t0_c is not None else rl['T0_forecast_c']
                Pr = q['a'] * T0 * T0 + q['b'] * T0 + q['c']
                out['rest_law'] = {'P_rest_W': Pr, 'T0_c': T0, 'J_at_rest_per_gemm_REPORTED': (Pr + W) * tg}
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--params', default=os.path.join(HERE, 'mm1_v1_params.json'))
    ap.add_argument('--points', required=True, help='CSV with card, arm, fmt, kind, mask, f_mhz, V[, e_res_source, e_res_keys, phi_gen, phi_tiles]')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    M = Model(json.load(open(a.params)))
    rows = list(csv.DictReader(open(a.points)))
    outr = []
    for r in rows:
        es = {'source': r['e_res_source'], 'keys': r['e_res_keys'].split(';')} if r.get('e_res_source') else None
        ps = ({'tiles': r['phi_tiles'].split(';')} if r.get('phi_tiles') else ({'gen': r['phi_gen']} if r.get('phi_gen') else None))
        p = M.predict(r['card'], r['arm'], r['fmt'], r['kind'], r.get('mask') or '0xffffffff', float(r.get('f_mhz') or 600), float(r.get('V') or 0.522),
                      e_res_spec=es, phi_spec=ps)
        outr.append({'id': r.get('id', ''), 'cycles_per_op_wall': p['cycles_per_op_wall'], 'cycles_per_op_mean': p['cycles_per_op_mean'],
                     'seconds_per_gemm': p.get('seconds_per_gemm'), 'W_over_idle': p.get('W_over_idle'), 'J_over_idle_per_gemm': p.get('J_over_idle_per_gemm')})
    with open(a.out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(outr[0]))
        w.writeheader()
        for r in outr:
            w.writerow(r)


if __name__ == '__main__':
    main()
