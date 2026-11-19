#!/usr/bin/env python3
"""MM1-v3.1: the held-out record beside MM1-v3 refitted, the REPORTED readings, the identification report and the frozen parameter file,
from run_v31.py's decisions and fits. Desk. /usr/bin/python3 3.12.3, numpy 1.26.4, scipy 1.11.4, -I -B, single-threaded.

    /usr/bin/python3 -I -B summary_v31.py --out <dir>
        writes <dir>/holdout_v31.json, points_time_v31.csv, points_energy_v31.csv, identification_v31.json, reported_v31.json,
        mm1_v31_params.json, summary_v31.json

Error = forecast / measured - 1; rms and bias in %; J over idle at 3 W and above, watts below. Headline figures exclude configuration twins
(a scored point whose card, kernel, arm, format, mask and clock to 25 MHz, and for energy the kind, are in the training set that priced it);
the figures with them are beside. A point's LOEO forecast comes from the fold of its experiment (DECLARED-v31.md section 9's 18).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import csv
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_v31 as F  # noqa: E402

TV, DV, EV, E, C = F.TV, F.DV, F.EV, F.E, F.C
LOW = 3.0
V3R = 'T5r+G0+n32'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def st(e):
    return F.stat(e)


class S:
    def __init__(self, out):
        self.out = out
        self.fits = os.path.join(out, 'fits')
        self.dec = json.load(open(os.path.join(out, 'decisions_v31.json')))
        self.final = self.dec['final_time_form']
        self.ef = self.dec['final_energy_form']
        self.P = DV.time_points()
        self.N = len(self.P)
        self.Tm = np.array([p['T'] for p in self.P])
        self.rung = F.rung_mask(self.P)
        self.EP = DV.energy_points()
        self.X = EV.Features31(self.EP)
        self.erung = F.rung_mask(self.EP)
        self.en = TV.Engine31(self.P, t7_cache_dir=os.path.join(out, 'cache'))
        self.enE = TV.Engine31(self.EP, t7_cache_dir=os.path.join(out, 'cache'))
        self.TR = {n: json.load(open(os.path.join(self.fits, f'time_{n}.json'))) for n in (self.final, V3R)}
        self.ER = {self.final: json.load(open(os.path.join(self.fits, f'energy_{self.final}.json'))),
                   V3R: json.load(open(os.path.join(self.fits, f'energy_{V3R}.json')))}
        for TR in self.TR.values():
            assert TR['ids'] == [p['id'] for p in self.P]

    # ------------------------------------------------------------------ time
    def tpreds(self, TR, fam):
        """per point: the held-out forecast of a fold family and its twin flag"""
        pr = np.full(self.N, np.nan)
        tw = np.zeros(self.N, bool)
        for name, fd in TR['folds'].items():
            if fam == 'LOEO':
                ok = name.startswith('LOEO ') and name[5:] in F.LOEO_EXPS
            elif fam == 'LOEO sub':
                ok = name.startswith('LOEO E212 ') or name.startswith('LOEO E213 ')
            else:
                ok = name.startswith(fam)
            if not ok:
                continue
            te = np.array(fd['test_idx'])
            pr[te] = fd['pred_test']
            m = np.zeros(self.N, bool)
            m[te] = True
            trc = {F.cfg_t(self.P[i]) for i in range(self.N) if not m[i] and not self.rung[i]}
            for i in te:
                tw[i] = F.cfg_t(self.P[i]) in trc
        return pr, tw

    def tgroups(self):
        g = collections.OrderedDict()
        g['all'] = lambda p: True
        for c in EV.CARDS:
            g[c] = (lambda c: lambda p: p['card'] == c)(c)
        for e in F.LOEO_EXPS:
            g['exp ' + e] = (lambda e: lambda p: p['exp'] == e)(e)
        g['subsets'] = lambda p: p['mask'].lower() != '0xffffffff'
        for lc in ('compact', 'spread', 'other'):
            g['layout ' + lc] = (lambda lc: lambda p: F.lolo_class(p['mask']) == lc)(lc)
        for fm in EV.FMTS:
            g[fm] = (lambda fm: lambda p: p['fmt'] == fm)(fm)
        for lp in ('rgm136 gemmL', 'rgm211 gemmLn', 'rgm211 gemmL', 'rgm136 gemmLnc'):
            g['loop ' + lp] = (lambda lp: lambda p: F._loop(p) == lp)(lp)
        g['run_gemm'] = lambda p: p['kernel'] == 'run_gemm'
        g['E146 store rungs (never trained)'] = lambda p: p['exp'] == 'E146' and bool(F.STORE_RUNG.search(p['id']))
        g['E212 a1c1'] = lambda p: p['exp'] == 'E212' and p['card'] == 'aifoundry1 card 1'
        g['E212 a1c0'] = lambda p: p['exp'] == 'E212' and p['card'] == 'aifoundry1 card 0'
        g['E212 a2c0'] = lambda p: p['exp'] == 'E212' and p['card'] == 'aifoundry2 card 0'
        g['E213 arm A'] = lambda p: p['exp'] == 'E213' and p['card'] == 'aifoundry3 card 0'
        g['E213 arm B'] = lambda p: p['exp'] == 'E213' and p['card'] == 'aifoundry1 card 1'
        g['E213 points (no reference)'] = lambda p: p['exp'] == 'E213' and p.get('role') == 'point'
        for fam in ('A:I', 'A:R', 'A:C', 'A:M', 'A:P', 'A:E'):
            g['E213 family ' + fam] = (lambda fam: lambda p: p['exp'] == 'E213' and str(p.get('family', '')).startswith(fam))(fam)
        return g

    def ttable(self, TR):
        G = self.tgroups()
        res = {}
        in_ = np.array(TR['pred_all'])
        res['in sample (training points)'] = st(in_[~self.rung] / self.Tm[~self.rung] - 1)
        for fam in ('LOEO', 'LOCO', 'LOKO', 'LEAVE rgm211', 'LOLO', 'LOEO sub'):
            pr, tw = self.tpreds(TR, fam)
            r = {}
            for gn, fn in G.items():
                idx = [i for i, p in enumerate(self.P) if fn(p) and not math.isnan(pr[i])]
                if not idx:
                    continue
                e = pr[idx] / self.Tm[idx] - 1
                t = tw[idx]
                r[gn] = {'all': st(e), 'no_twin': st(e[~t]), 'twin': st(e[t])}
            res[fam] = r
        return res

    def counter_mean(self, TR, form):
        """LOEO counter-mean forecasts (the wall / rho, MM1-v3's rho) against the measured counter mean"""
        out = np.full(self.N, np.nan)
        imb = json.load(open(os.path.join(HERE, '..', 'v3', 'out', 'mm1_v3_params.json')))['time']['imbalance_mean']
        import mm1_v31 as M31
        for name, fd in TR['folds'].items():
            if not (name.startswith('LOEO ') and name[5:] in F.LOEO_EXPS):
                continue
            th = fd['theta']
            T, Q0, Q1 = self.en.predict(th, form, return_q=True)
            for i in fd['test_idx']:
                p = self.P[i]
                pre, b = E.arm_parts(p['arm'])
                mi = C.mask_info(p['mask'])
                n2 = float(C.lines(0.5 * (Q0[i] + Q1[i]))[0])
                sh = C.Shape('gemmL%dx%dx%d' % b if pre is not None else p['arm'], C.FULL, masked_map=False)
                rho = C.rho_mean(sh, n2) * C.rho_sub(mi, th) * M31.imbalance_mean(mi, b[0] if b else 1, imb)
                out[i] = T[i] * p['f'] / rho
        return out

    # ------------------------------------------------------------------ energy
    def epreds(self, ER, ef, fam, route=None):
        N = len(self.EP)
        g, f_, tf = np.full(N, np.nan), np.full(N, np.nan), np.full(N, np.nan)
        tw = np.zeros(N, bool)
        use = self.X.usable3
        for name, fd in ER['forms'][ef]['folds'].items():
            if fam == 'LOEO':
                ok = name.startswith('LOEO ') and (name[5:] in F.LOEO_EXPS or name == 'LOEO E210')
            else:
                ok = name.startswith(fam)
            if not ok:
                continue
            te = np.array(fd['test_idx'])
            kg = 'W_given_t' + (('_' + route) if route and ('W_given_t_' + route) in fd else '')
            kf = 'W_forecast_t' + (('_' + route) if route and ('W_forecast_t_' + route) in fd else '')
            g[te], f_[te], tf[te] = fd[kg], fd[kf], fd['T_forecast']
            m = np.zeros(N, bool)
            m[te] = True
            trc = {F.cfg_e(self.EP[i]) for i in range(N) if not m[i] and use[i] and not self.erung[i]}
            for i in te:
                tw[i] = F.cfg_e(self.EP[i]) in trc
        return g, f_, tf, tw

    def eq(self, g, f_, tf, ii):
        w, t, idle = self.X.w, self.X.t, self.X.idle
        ii = np.array([i for i in ii if not math.isnan(g[i])], int)
        if not len(ii):
            return None
        hi = ii[w[ii] >= LOW]
        lo = ii[w[ii] < LOW]
        out = {'W given t (>= 3 W)': st(g[hi] / w[hi] - 1), 'J over idle t forecast (>= 3 W)': st(f_[hi] * tf[hi] / (w[hi] * t[hi]) - 1),
               'J at rest given t': st([(idle[i] + g[i]) / (idle[i] + w[i]) - 1 for i in ii if not math.isnan(idle[i])]),
               'J at rest t forecast': st([(idle[i] + f_[i]) * tf[i] / ((idle[i] + w[i]) * t[i]) - 1 for i in ii if not math.isnan(idle[i])])}
        if len(lo):
            out['W under 3 W, watts'] = {'n': int(len(lo)), 'rms_W': round(float(np.sqrt(np.mean((g[lo] - w[lo]) ** 2))), 4),
                                         'bias_W': round(float(np.mean(g[lo] - w[lo])), 4)}
        sec = [(self.EP[i]['ops'] * tf[i] * 1e-6) / self.EP[i]['t_meas'] - 1 for i in ii
               if self.EP[i].get('t_meas') and self.EP[i].get('ops') and not math.isnan(tf[i])]
        out['seconds a GEMM (t forecast against the measured seconds, where measured)'] = st(sec)
        return out

    def egroups(self):
        g = collections.OrderedDict()
        g['all'] = lambda e: True
        for c in EV.CARDS:
            g[c] = (lambda c: lambda e: e['card'] == c)(c)
        for x in F.LOEO_EXPS + ['E210']:
            g['exp ' + x] = (lambda x: lambda e: e['exp'] == x)(x)
        for k in ('zeros', 'random', 'ones', 'sparse50'):
            g['kind ' + k] = (lambda k: lambda e: e['kind'] == k)(k)
        g['kinds newly counted (v31-counts)'] = lambda e: (e['kind'].startswith('pattern:') or e['kind'] in ('real', 'real:blind4', 'e37')
                                                          or e['kind'].startswith('designed:'))
        g['zeros on card 1'] = lambda e: e['kind'] == 'zeros' and e['card'] == 'aifoundry1 card 1'
        g['subsets'] = lambda e: e['mask'].lower() != '0xffffffff'
        for lp in ('rgm211 gemmLn', 'rgm211 gemmL', 'rgm136 gemmLnc'):
            g['loop ' + lp] = (lambda lp: lambda e: F._loop(e) == lp)(lp)
        g['E213 points (no reference)'] = lambda e: e['exp'] == 'E213' and e.get('role') == 'point'
        return g

    def etable(self, ER, ef):
        G = self.egroups()
        use = self.X.usable3
        res = {}
        gi = np.array(ER['forms'][ef]['W_all_given_t'])
        hi = np.array([i for i in range(len(self.EP)) if use[i] and not self.erung[i] and self.X.w[i] >= LOW])
        res['in sample W given t (>= 3 W)'] = st(gi[hi] / self.X.w[hi] - 1)
        fams = [('LOEO', None), ('LOCO', 'anchor'), ('LOCO', 'fallback'), ('LOKO', None), ('LEAVE rgm211', None), ('LOLO', None)]
        for fam, route in fams:
            g, f_, tf, tw = self.epreds(ER, ef, fam, route)
            key = fam + ((' (' + route + ' route)') if route else '')
            r = {}
            anchors = set()
            if fam == 'LOCO':
                for c in EV.CARDS:
                    anchors |= set(F.anchor_points(self.EP, c))
            for gn, fn in G.items():
                ii = [i for i, e in enumerate(self.EP) if fn(e) and use[i] and i not in anchors]
                if not ii:
                    continue
                ent = {'all': self.eq(g, f_, tf, ii), 'no_twin': self.eq(g, f_, tf, [i for i in ii if not tw[i]])}
                if ent['all'] is None:
                    continue
                r[gn] = ent
            if fam == 'LOCO':
                r['note'] = "the held-out card's anchor points excluded (item 2), the same points under both routes"
            res[key] = r
        return res

    # ------------------------------------------------------------------ identification (item 9)
    def ident_time(self, TR, form):
        th = TR['theta_all']
        free = TR['fit_all']['free']
        pins = TR['fit_all']['pins']
        tr = np.arange(self.N)[~self.rung]
        x = np.array([th[k] for k in free])

        def res(xx):
            return self.en.predict(F.theta_full(free, xx, pins), form)[tr] / self.Tm[tr] - 1.0
        return self._ident(res, x, free, [F.LO[k] for k in free], [F.HI[k] for k in free])

    def ident_energy(self, ER, ef, TR, form):
        rec = ER['forms'][ef]
        p = rec['theta_all']
        free = rec['fit_all']['free']
        T, Q0, Q1 = self.enE.predict(TR['theta_all'], form, return_q=True)
        n2, n3, nF = EV.lines_of(0.5 * (Q0 + Q1))
        rC = EV.rC_of(self.X.Ffull, TR['theta_all'], form)
        use = self.X.usable3
        tr = np.arange(len(self.EP))[use & ~self.erung]
        wm = self.X.w[tr]
        wt = 1.0 / np.maximum(wm, LOW)
        base = dict(p)

        def res(xx):
            q = dict(base)
            q.update(dict(zip(free, xx)))
            return (EV.W31(q, self.X, tr, n2[tr], n3[tr], nF[tr], self.X.t[tr], rC[tr], ef) - wm) * wt
        lo = [(0.5 if k.startswith('kc|') else F.EBOUND.get(k, (-np.inf, np.inf))[0]) for k in free]
        hi = [(2.0 if k.startswith('kc|') else F.EBOUND.get(k, (-np.inf, np.inf))[1]) for k in free]
        if ef == 'E1b':
            lo = [0.0 if k in ('b2', 'd2') else v for k, v in zip(free, lo)]
        return self._ident(res, np.array([p[k] for k in free]), free, lo, hi)

    def _ident(self, res, x, free, lo, hi):
        r0 = res(x)
        J = np.zeros((len(r0), len(x)))
        for k in range(len(x)):
            h = 1e-5 * max(abs(x[k]), 1e-3)
            xp, xm = x.copy(), x.copy()
            xp[k] += h
            xm[k] -= h
            J[:, k] = (res(xp) - res(xm)) / (2 * h)
        n, pdim = len(r0), len(x)
        s2 = float(np.sum(r0 ** 2)) / max(n - pdim, 1)
        try:
            cov = s2 * np.linalg.pinv(J.T @ J)
            se = np.sqrt(np.maximum(np.diag(cov), 0))
        except np.linalg.LinAlgError:
            se = np.full(pdim, np.nan)
        out = {}
        for k, name in enumerate(free):
            rng = (hi[k] - lo[k]) if np.isfinite(hi[k]) and np.isfinite(lo[k]) else None
            at_lo = np.isfinite(lo[k]) and abs(x[k] - lo[k]) <= 1e-6 * (rng or max(1.0, abs(lo[k])))
            at_hi = np.isfinite(hi[k]) and abs(x[k] - hi[k]) <= 1e-6 * (rng or max(1.0, abs(hi[k])))
            rse = float(se[k] / abs(x[k])) if x[k] != 0 else float('inf')
            out[name] = {'value': float(x[k]), 'se': float(se[k]), 'rse_pct': round(100 * rse, 2), 'at_lower_bound': bool(at_lo),
                         'at_upper_bound': bool(at_hi), 'not_identified_rse_over_100pct': bool(rse > 1.0)}
        return {'n': n, 'p': pdim, 's2': s2, 'constants': out,
                'how': 'central differences (h = 1e-5 max(|x|, 1e-3)) of the training residuals at the all-data fit; cov = s2 pinv(J^T J)'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    t0 = time.time()
    R = S(out)
    form31 = F.parse_form_name(R.final)[0]
    formv3 = F.parse_form_name(V3R)[0]
    hold = {'final_time_form': R.final, 'final_energy_form': R.ef, 'v3_refitted': {'time': V3R, 'energy': 'E1u'},
            'time': {'v3.1': R.ttable(R.TR[R.final]), 'v3 refitted': R.ttable(R.TR[V3R])},
            'energy': {'v3.1': R.etable(R.ER[R.final], R.ef), 'v3 refitted': R.etable(R.ER[V3R], 'E1u')}}
    cm31 = R.counter_mean(R.TR[R.final], form31)
    cmv3 = R.counter_mean(R.TR[V3R], formv3)
    meas_cm = np.array([p.get('cyc_mean') or np.nan for p in R.P], float)
    for lab, cm in (('v3.1', cm31), ('v3 refitted', cmv3)):
        ok = ~np.isnan(cm) & ~np.isnan(meas_cm)
        _, tw = R.tpreds(R.TR[R.final], 'LOEO')
        hold['time'][lab]['LOEO counter mean'] = {'all': st(cm[ok] / meas_cm[ok] - 1), 'no_twin': st(cm[ok & ~tw] / meas_cm[ok & ~tw] - 1)}
    json.dump(hold, open(os.path.join(out, 'holdout_v31.json'), 'w'), indent=1, sort_keys=True, default=float)
    # identification
    ide = {'time': R.ident_time(R.TR[R.final], form31),
           'energy': R.ident_energy(R.ER[R.final], R.ef, R.TR[R.final], form31)}
    json.dump(ide, open(os.path.join(out, 'identification_v31.json'), 'w'), indent=1, sort_keys=True, default=float)
    # per point files
    p31, tw31 = R.tpreds(R.TR[R.final], 'LOEO')
    pv3, _ = R.tpreds(R.TR[V3R], 'LOEO')
    l31, _ = R.tpreds(R.TR[R.final], 'LOCO')
    lv3, _ = R.tpreds(R.TR[V3R], 'LOCO')
    with open(os.path.join(out, 'points_time_v31.csv'), 'w', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        # meas_T_x_f: the measured op time T times the point's mean clock f (cycles an op), the quantity every prediction column is compared
        # with; it is not the mean of the runs' wall cycles (fix-fit-v31, Q222: relabelled from 'meas_cyc_wall', verify-fit-v31's nit 4)
        w.writerow(['id', 'exp', 'arm', 'kernel', 'fmt', 'kind', 'mask', 'card', 'f_mhz', 'meas_T_x_f', 'twin_LOEO', 'v31_in', 'v31_LOEO',
                    'v31_LOCO', 'v3r_in', 'v3r_LOEO', 'v3r_LOCO'])
        i31 = np.array(R.TR[R.final]['pred_all'])
        iv3 = np.array(R.TR[V3R]['pred_all'])
        for i, p in enumerate(R.P):
            f = p['f']
            fmt = lambda v: '' if math.isnan(v) else round(float(v) * f, 3)  # noqa: E731
            w.writerow([p['id'], p['exp'], p['arm'], p['kernel'], p['fmt'], p.get('kind', ''), p['mask'], p['card'], round(f, 3),
                        round(R.Tm[i] * f, 3), int(tw31[i]), fmt(i31[i]), fmt(p31[i]), fmt(l31[i]), fmt(iv3[i]), fmt(pv3[i]), fmt(lv3[i])])
    with open(os.path.join(out, 'points_energy_v31.csv'), 'w', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(['id', 'exp', 'arm', 'kernel', 'fmt', 'kind', 'mask', 'card', 'w_meas', 'idle_w', 'phi', 'phi_rule', 'twin_LOEO',
                    'v31_in_wg', 'v31_LOEO_wg', 'v31_LOEO_wf', 'v31_LOCO_wg_anchor', 'v31_LOCO_wg_fallback', 'v3r_in_wg', 'v3r_LOEO_wg', 'v3r_LOCO_wg_anchor'])
        g31, f31, _, etw = R.epreds(R.ER[R.final], R.ef, 'LOEO')
        gv3, _, _, _ = R.epreds(R.ER[V3R], 'E1u', 'LOEO')
        la, _, _, _ = R.epreds(R.ER[R.final], R.ef, 'LOCO', 'anchor')
        lf, _, _, _ = R.epreds(R.ER[R.final], R.ef, 'LOCO', 'fallback')
        lva, _, _, _ = R.epreds(R.ER[V3R], 'E1u', 'LOCO', 'anchor')
        i31 = np.array(R.ER[R.final]['forms'][R.ef]['W_all_given_t'])
        iv3 = np.array(R.ER[V3R]['forms']['E1u']['W_all_given_t'])
        r5 = lambda v: '' if math.isnan(v) else round(float(v), 5)  # noqa: E731
        for i, e in enumerate(R.EP):
            w.writerow([e['id'], e['exp'], e['arm'], e['kernel'], e['fmt'], e['kind'], e['mask'], e['card'], round(e['w'], 4),
                        ('' if math.isnan(R.X.idle[i]) else round(R.X.idle[i], 4)), round(float(R.X.phi[i]), 6), R.X.phi_rule[i], int(etw[i]),
                        r5(i31[i]), r5(g31[i]), r5(f31[i]), r5(la[i]), r5(lf[i]), r5(iv3[i]), r5(gv3[i]), r5(lva[i])])
    # the frozen parameter file
    v3p = json.load(open(os.path.join(HERE, '..', 'v3', 'out', 'mm1_v3_params.json')))
    TRf = R.TR[R.final]
    ERf = R.ER[R.final]['forms'][R.ef]
    params = {'model': 'MM1-v3.1', 'what': ("MM1-v3.1: MM1-v3 with DECLARED-v31.md's items as its declared rules chose them, fitted on every committed "
                                            "matmul point through E213 (desk fits; post hoc as an act)"),
              'interpreter': '/usr/bin/python3 %s, numpy %s' % (sys.version.split()[0], np.__version__),
              'data_commit': R.dec['steps']['step0']['repo_head'], 'tag': R.dec.get('tag'),
              'time': {'form_name': R.final, 'form': form31, 'theta': TRf['theta_all'], 'free': TRf['free'], 'pins_all_data': TRf['fit_all']['pins'],
                       'units': 'c3, cF, F2, tC, Tcoop_*: cycles (tC a line); m3, mF, T2: us; x1, w1, x2, w2: MB; others dimensionless',
                       'imbalance_mean': v3p['time']['imbalance_mean'], 'floor_cycles': v3p['time']['floor_cycles'], 'c1_law': v3p['time']['c1_law'],
                       'rho_wall_over_mean': v3p['time']['rho_wall_over_mean'], 'census_sha256': sha(EV.CENSUS31_PATH),
                       't7_v31_sha256': TV.t7_sha()},
              'energy': {'form': R.ef, 'theta': ERf['theta_all'], 'lambda_per_C': EV.LAM, 'r_L2': EV.R_L2,
                         'units': v3p['energy']['units'], 'volts': v3p['energy']['volts'], 'governed_base_w': v3p['energy']['governed_base_w'],
                         'counts_SHA256SUMS': sha(os.path.join(HERE, 'counts', 'SHA256SUMS'))},
              'rest_law': v3p['rest_law'], 'rest_law_source': "MM1-v2's rest law per card as MM1-v3 carries it (../v3/out/mm1_v3_params.json; REPORTED)",
              'imbalance_source': "MM1-v2's counter-mean imbalance as MM1-v3 carries it"}
    pp = os.path.join(out, 'mm1_v31_params.json')
    json.dump(params, open(pp, 'w'), indent=1, sort_keys=True, default=float)
    # the predictor reproduces the fit (time at every point, energy at every energy point)
    import mm1_v31 as M31
    M = M31.Model(params, t7_cache_dir=os.path.join(out, 'cache'))
    Tp, _, _, _ = M.time_many([{'arm': p['arm'], 'kernel': p['kernel'], 'fmt': p['fmt'], 'mask': p['mask'], 'f': p['f']} for p in R.P])
    dt = float(np.max(np.abs(Tp / np.array(TRf['pred_all']) - 1)))
    S_ = {'final_time_form': R.final, 'final_energy_form': R.ef, 'tag': R.dec.get('tag'), 'decisions': {k: v.get('verdict', v.get('winner', v.get('layout')))
          for k, v in R.dec['steps'].items() if isinstance(v, dict)}, 'acceptance': R.dec['steps'].get('step7', {}).get('acceptance'),
          'predictor_time_equals_fit_max_rel_diff': dt, 'secs': round(time.time() - t0, 1)}
    json.dump(S_, open(os.path.join(out, 'summary_v31.json'), 'w'), indent=1, sort_keys=True, default=float)
    for f in ('holdout_v31.json', 'identification_v31.json', 'points_time_v31.csv', 'points_energy_v31.csv', 'mm1_v31_params.json', 'summary_v31.json'):
        print(sha(os.path.join(out, f)), f)
    print('predictor = fit (time) max rel diff', dt)


if __name__ == '__main__':
    main()
