#!/usr/bin/env python3
"""MM1-v2, the lab's matmul model: the predictor. From a matmul's size, format, data kind, shire mask, card and clock it gives the clock cycles
(the slowest minion's and the counter's mean), the seconds, the joules over idle and with the card at rest, the transistor switches (MM1-v1's
estimate, carried unchanged) and the timing simulation's two columns beside them. Desk; numpy. The equations are mm1_core_v2.py's; the
constants are mm1_v2_params.json's (fit_v2.py, governor_v2.py, rest_v2.py).

    import mm1_v2; M = mm1_v2.Model(params); M.predict(card, arm, fmt, kind, mask, f_mhz, V=None, ...)

THE CLOCK is an input. On a pinned card it is the card's clock (600 MHz). On a governed card (aifoundry2 card 0; aifoundry1 card 0) it is the
clock the run measured in its scored window ('given the measured clock'), or the clock the governor model forecasts for the run
(governor_v2.py, 'with the clock forecast'). The volts and the governed base follow from the clock (mm1_core_v2.volts, G_of_f) unless the
caller gives the measured volts.
Scope: mm1_core_v2.SCOPE. Labels: every constant is a desk fit made after its data existed (post hoc as an act); a forecast for a never-run
point is blind only once frozen by sha256 before that point's first datum.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kinds_v2 as K  # noqa: E402
import mm1_core_v2 as C  # noqa: E402

SW_TABLE = json.load(open(os.path.join(HERE, 'inputs', 'v1', 'switch_table.json')))['rows']
CKEY = {'aifoundry3 card 0': 'a3', 'aifoundry2 card 0': 'a2', 'aifoundry1 card 1': 'c1', 'aifoundry1 card 0': 'c0'}
BENCH_RESIDENT = {'fp32': 546.0, 'fp16': 546.0, 'int8': 318.0}   # the RTL bench (+7.75), A and B resident (simulated)
GOVERNED = ('aifoundry2 card 0', 'aifoundry1 card 0')


def imbalance_mean(mi, MB, imb):
    """the counter's mean under a subset holding every column group but under 4 of 8 row groups (MM1-v1's term, fitted on E206's gemmL4x8x4
    at 0xf and 0xff); v2 applies it only when MB >= 2: E208's gemmL1x1x1 / 1x1x4 at 0xf (R = 1) read wall / mean 1.001-1.08, not 1.21"""
    if imb is None or mi['full'] or mi['C'] < 4 or mi['R'] >= 4 or MB < 2:
        return 1.0
    return 1.0 + imb['eta_m'] * ((4.0 - mi['R']) / 3.0) ** imb['gamma']


class Model:
    def __init__(self, params):
        self.P = params
        self.th = params['time']['theta']
        self.E = params['energy']['theta']
        self._shapes = {}

    def shape(self, arm, mask):
        k = (arm, mask)
        if k not in self._shapes:
            self._shapes[k] = C.Shape(arm, mask, masked_map=False)
        return self._shapes[k]

    def resident(self, card, fmt, kind, e_res_spec=None, phi_spec=None):
        """(e_res nJ an op at 600 MHz incl. k_res, phi, source text) or (None, None, why)"""
        ck = CKEY[card]
        src = 'a2' if ck == 'c0' else ck
        E = self.E
        kk = 'kres|%s|%s' % (card, fmt)
        k = E.get(kk, 1.0) if kk in E else 1.0
        z = K.LV2['zeros_anchor'][fmt][src]
        Z, R = z['Z_w'], z['rate_ops_per_s']
        if kind == 'ones':
            D1 = E.get('Dones|' + fmt)
            if D1 is None:
                return None, None, 'no ones price'
            phi, _ = K.phi(fmt, {'tiles': [f'../tiles/ones__{fmt}.bin']})
            return (k * Z + D1) / R * 1e9, phi, f'ones: (k_res {k:.4f} x Z {Z:.4f} W + D_ones {D1:.4f} W) / R {R:.4e} ops/s ({src} anchor)'
        if kind in ('zeros', 'random'):
            key = fmt + '.zeros' if kind == 'zeros' else (fmt + ('.full' if fmt == 'int8' else '.randn'))
            Dw = K.LV2['kinds'][key][src]['D_w']
            return k * (Z + Dw) / R * 1e9, (0.0 if kind == 'zeros' else 1.0), f'ledger v2 {key} on {src} x k_res {k:.4f}'
        if kind == 'real' or (e_res_spec or {}).get('source') == 'ledger':
            # a kind with ledger rows on aifoundry3 only, carried to another card by that card's own random / aifoundry3 random ratio
            keys = e_res_spec['keys']
            Ds = []
            for kk2 in keys:
                row = K.LV2['kinds'].get(kk2, {})
                if src in row:
                    Ds.append(row[src]['D_w'])
                elif 'a3' in row:
                    rk = fmt + ('.full' if fmt == 'int8' else '.randn')
                    Ds.append(row['a3']['D_w'] * K.LV2['kinds'][rk][src]['D_w'] / K.LV2['kinds'][rk]['a3']['D_w'])
                else:
                    return None, None, f'no ledger row {kk2}'
            Dm = sum(Ds) / len(Ds)
            phi, _ = K.phi(fmt, phi_spec)
            return k * (Z + Dm) / R * 1e9, phi, f'ledger v2 kind rows {keys} (aifoundry3 rows x the card/aifoundry3 random ratio where the card has none) x k_res {k:.4f}'
        return None, None, 'no resident price source for this kind on this card: energy NOT FORECAST'

    def predict(self, card, arm, fmt, kind, mask='0xffffffff', f=600.0, V=None, ops=None, minions=None, t0_c=None, e_res_spec=None,
                phi_spec=None, G=None):
        th = self.th
        sh = self.shape(arm, mask)
        mi = sh.mi
        n = minions if minions is not None else 32 * mi['n']
        t, Q0, Q1 = C.t_op_v2(sh, fmt, f, th, 'r1')
        Q = 0.5 * (Q0 + Q1)
        n2, n3, nF = C.lines(Q)
        MB = sh.blocks[0] if sh.blocks else 1
        rho = C.rho_mean(sh, n2) * C.rho_sub(mi, th) * imbalance_mean(mi, MB, self.P['time'].get('imbalance_mean'))
        ops = ops if ops is not None else sh.ops
        out = {'scope': C.SCOPE, 'card': card, 'f_mhz': f, 'T_op_us': t, 'cycles_per_op_wall': t * f, 'cycles_per_op_mean': t * f / rho,
               'rho_wall_over_mean': rho, 'lines_L2_L3_F': [n2, n3, nF], 'footprint_MB': sh.F_full, 'power_of_two_NB': sh.p2,
               'floor_cycles_measured_tenb': C.FLOOR[fmt], 'bench_resident_cycles_simulated': BENCH_RESIDENT[fmt],
               'sim_steps_per_minion_per_gemm': C.sim_steps(sh), 'ops_per_minion_per_gemm': ops, 'minions': n}
        if ops:
            out['cycles_per_gemm_wall'] = ops * t * f
            out['seconds_per_gemm'] = ops * t * 1e-6
        er, phi, txt = self.resident(card, fmt, kind, e_res_spec, phi_spec)
        if er is None:
            out['energy'] = 'NOT FORECAST: ' + txt
            return out
        Vv = V if V is not None else C.volts(card, f)
        s = (Vv / 0.517) ** 2
        Gv = G if G is not None else C.G_of_f(card, f)
        E = self.E
        u = (n3 + nF) / 192.0
        A = E['Pmin|' + card] * n / 1024.0 + E['Pmem'] * u + E['g'] * Gv
        Bc = n * s * (er * 1e-9 + 1e-12 * (n2 / 32.0 * (E['b2'] + E['d2'] * phi) + n3 / 32.0 * (E['b3'] + E['d3'] * phi)
                                            + nF / 32.0 * (E['bF'] + E['dF'] * phi)))
        W = A + Bc / (t * 1e-6)
        out.update({'V': Vv, 's_V': s, 'G_W': Gv, 'e_res_nJ': er, 'e_res_source': txt, 'phi': phi, 'W_over_idle': W,
                    'W_affine': {'A_W': A, 'B_W_us': Bc * 1e6, 'how': 'W over idle at a measured op time t_us (the slowest minion) = A + B / t_us, at this clock'}})
        if ops:
            tg = out['seconds_per_gemm']
            out['J_over_idle_per_gemm'] = W * tg
            rs = n / (t * 1e-6) * s
            PJ = 1e-12
            terms = {'awake_minions': E['Pmin|' + card] * n / 1024.0, 'awake_memory_path': E['Pmem'] * u, 'governed_base': E['g'] * Gv,
                     'resident_op': rs * er * 1e-9, 'lines_L2': rs * PJ * n2 / 32.0 * (E['b2'] + E['d2'] * phi),
                     'lines_L3': rs * PJ * n3 / 32.0 * (E['b3'] + E['d3'] * phi), 'lines_fresh': rs * PJ * nF / 32.0 * (E['bF'] + E['dF'] * phi)}
            Jt = {k2: v * tg for k2, v in terms.items()}
            out['J_over_idle_by_class'] = Jt
            kk = fmt + ('.zeros' if kind == 'zeros' else ('.full' if fmt == 'int8' else '.randn')) if kind in ('zeros', 'random') else None
            swc = 'aifoundry2 card 0' if card == 'aifoundry1 card 0' else card
            out['switches'] = C.switches(Jt, tg, W, swc, s, ops * n, fmt, kk, SW_TABLE)
            if kk is None:
                out['switches']['counted_note'] = 'no counted netlist row for this kind: the counted part is NOT FORECAST; the estimated part covers the die'
            rl = (self.P.get('rest_law') or {}).get(card)
            if rl:
                T0 = t0_c if t0_c is not None else rl['T0_forecast_c']
                Pr = rl['a'] * T0 * T0 + rl['b'] * T0 + rl['c']
                out['rest_law'] = {'P_rest_W': Pr, 'T0_c': T0, 'J_at_rest_per_gemm_REPORTED': (Pr + W) * tg, 'source': rl['source']}
        return out
