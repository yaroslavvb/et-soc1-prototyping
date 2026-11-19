#!/usr/bin/env python3
"""MM1-v3.1: the declared order of decisions (DECLARED-v31.md section 11), each by its rule, from fit_v31.py's fits. Desk; post hoc as a fit.

    /usr/bin/python3 -I -B run_v31.py --out <dir> --tag <rehearsal | final> [--e213-scores-B <scores-e213-B.json>]
        step 0: the data set, the inputs' sha256, T7's desk precondition (t7_v31.py --check with every subset shape of the data), the census
                paths' check (section 11's deferred item);
        step 1: item 8 (T5r or tC) from the frozen forecasts and E213's measured family C (arm A) and BK (arm B), no fit;
        step 2: item 4's trace check (PASS, FAIL or NOT RUN), read from the lanes that made it;
        step 3: item 3 (G0, Gplace, Goperand, Gcoop), LOEO;
        step 4: item 4 (T7, T7L, n/32), LOEO and LOLO; item 8's step 3 if step 1 was NOT DECIDED;
        step 5: the final time form on every fold, MM1-v3 refitted (T5r + G0 + n/32) beside;
        step 6: item 1 (E1u, E1b, E1t, E1m) on the final time form's folds; v3-ledger (REPORTED); MM1-v3 refitted's energy (E1u);
        step 7: item 2's two LOCO routes and the acceptance rules (section 9).
    Every step writes <dir>/decisions_v31.json as it goes; every fit is resumable (fit_v31.run_time / run_energy keep partial records).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import csv
import hashlib
import json
import math
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_v31 as F  # noqa: E402

TV, DV, EV, E, C = F.TV, F.DV, F.EV, F.E, F.C
REPO = TV.REPO
LOW = 3.0
G_NCONST = {'G0': 0, 'Gcoop': 3, 'Gplace': 5, 'Goperand': 5}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def now():
    return time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())


def rms(e):
    e = np.asarray([x for x in e if x is not None and not (isinstance(x, float) and math.isnan(x))], float)
    return float(np.sqrt(np.mean(e ** 2))) * 100 if len(e) else None


def stat(e):
    return F.stat(e)


class Run:
    def __init__(self, out, tag, log):
        self.out = out
        self.fits = os.path.join(out, 'fits')
        os.makedirs(self.fits, exist_ok=True)
        self.tag = tag
        self.log = log
        self.dec_path = os.path.join(out, 'decisions_v31.json')
        self.dec = json.load(open(self.dec_path)) if os.path.exists(self.dec_path) else {'tag': tag, 'steps': {}}
        self.P = DV.time_points()
        self.Tm = np.array([p['T'] for p in self.P])
        self.rung = F.rung_mask(self.P)
        self.en = TV.Engine31(self.P, t7_cache_dir=os.path.join(out, 'cache'))
        self.EP = DV.energy_points()
        self.X = EV.Features31(self.EP)
        self.enE = TV.Engine31(self.EP, t7_cache_dir=os.path.join(out, 'cache'))
        self.erung = F.rung_mask(self.EP)
        self.TR = {}

    def save(self):
        json.dump(self.dec, open(self.dec_path + '.tmp', 'w'), indent=1, sort_keys=True, default=float)
        os.replace(self.dec_path + '.tmp', self.dec_path)

    def time(self, name, which):
        t0 = time.time()
        self.log(f'{now()} time {name} folds {which}')
        r = F.run_time(name, which, self.fits, P=self.P, en=self.en, log=self.log, tag=self.tag)
        self.TR[name] = r
        self.log(f'{now()} time {name} done ({time.time() - t0:.0f} s)')
        return r

    # ---------------------------------------------------------------- per-point held-out predictions and twins
    def loeo_pred(self, TR):
        N = len(self.P)
        pr = np.full(N, np.nan)
        tw = np.zeros(N, bool)
        for name, fd in TR['folds'].items():
            if not (name.startswith('LOEO ') and name[5:] in F.LOEO_EXPS):
                continue
            te = np.array(fd['test_idx'])
            pr[te] = fd['pred_test']
            m = np.zeros(N, bool)
            m[te] = True
            trc = {F.cfg_t(self.P[i]) for i in range(N) if not m[i] and not self.rung[i]}
            for i in te:
                tw[i] = F.cfg_t(self.P[i]) in trc
        return pr, tw

    def fam_pred(self, TR, prefix):
        N = len(self.P)
        pr = np.full(N, np.nan)
        for name, fd in TR['folds'].items():
            if name.startswith(prefix):
                pr[np.array(fd['test_idx'])] = fd['pred_test']
        return pr

    def err(self, pr, sel):
        return [pr[i] / self.Tm[i] - 1 for i in range(len(self.P)) if sel[i] and not math.isnan(pr[i])]

    # ---------------------------------------------------------------- step 0
    def step0(self):
        if 'step0' in self.dec['steps']:
            return
        s = {'when': now(), 'interpreter': '/usr/bin/python3 %s, numpy %s' % (sys.version.split()[0], np.__version__)}
        git = lambda *a: subprocess.run(['git', '-C', REPO] + list(a), capture_output=True, text=True).stdout.strip()  # noqa: E731
        s['repo_head'] = git('rev-parse', 'HEAD')
        s['repo_status_lines'] = len([x for x in git('status', '--porcelain', '--untracked-files=no').splitlines() if x.strip()])
        s['n_time_points'] = len(self.P)
        s['time_points_by_exp'] = dict(sorted(collections.Counter(p['exp'] for p in self.P).items()))
        s['n_energy_points'] = len(self.EP)
        s['energy_points_by_exp'] = dict(sorted(collections.Counter(e['exp'] for e in self.EP).items()))
        s['energy_usable_v31'] = int(self.X.usable3.sum())
        s['e213_arms'] = DV.e213_available()
        s['store_rungs'] = int(self.rung.sum())
        frozen = {'DECLARED-v31.md': 'd58601fa0696cdf42611a3e7a179179eedb3fc4f7015e8638e608fa99e3d0860',
                  'declared-v31.json': '26c3fedb2c0a2623d2a02fd0acb2add306259ca4042433fed92d8c9c56d3365c',
                  't7_v31.py': '893ae962174678fcd1560dfc423722361e706319a188687f8f572a4e3ca89242',
                  'comparator_4a_v31.py': '17b336e10b9f4b0a521c0cb83630575f9f54b5d1d993436677aedefdcf38f960'}
        s['frozen_files'] = {k: {'want': v, 'got': sha(os.path.join(HERE, k)), 'equal': sha(os.path.join(HERE, k)) == v} for k, v in frozen.items()}
        assert all(v['equal'] for v in s['frozen_files'].values()), s['frozen_files']
        cs = os.path.join(HERE, 'counts', 'SHA256SUMS')
        s['counts_SHA256SUMS'] = sha(cs)
        s['counts_check'] = subprocess.run(['sha256sum', '-c', '--quiet', 'SHA256SUMS'], cwd=os.path.join(HERE, 'counts'),
                                           capture_output=True, text=True).returncode
        s['census_v31_sha256'] = sha(EV.CENSUS31_PATH)
        s['inputs'] = {os.path.relpath(os.path.join(dp, fn), HERE): sha(os.path.join(dp, fn))
                       for dp, _, fns in os.walk(os.path.join(HERE, 'inputs')) for fn in sorted(fns)}
        # T7's desk precondition with every subset shape of the data
        shapes = sorted({'%dx%dx%d' % E.arm_parts(p['arm'])[1] for p in self.P + self.EP if TV.T7.applies(p)})
        outj = os.path.join(self.out, 't7_check.json')
        r = subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, 't7_v31.py'), '--check', '--repo', REPO, '--out', outj,
                            '--extra-shapes', ','.join(shapes)], capture_output=True, text=True)
        s['t7_check'] = {'rc': r.returncode, 'stdout_tail': r.stdout.strip().splitlines()[-3:], 'extra_shapes': shapes,
                         'record_sha256': sha(outj) if os.path.exists(outj) else None}
        s['t7_precondition_pass'] = (r.returncode == 0)
        # section 11's deferred census-path check: a committed counted simulator run of gemmLnc, rgm211 gemmL or rgm211 gemmLn
        s['census_path_check'] = {
            'rule': ("the PCs hart 0 ran at least 60 times in a committed counted simulator run of the loop against the census's steady path "
                     "(census-v3.json check_against_counted_run); no such run at the fit's start: the census entry stands"),
            'searched': 'every file under tools/ and docs/ at the fit start for counted-run records (pc_counts, steady_pcs, executed_ge60)',
            'found': [x for x in git('grep', '-l', '-e', 'steady_pcs_executed', '--', 'tools', 'docs').splitlines()],
            'reading': ("only census-v3.json's own rgm136 gemmL check holds such a record; E211's dated correction 1 "
                        "(tools/claims-v3/e211-notes/E211.md.A1-correction-1.md, its item 6) lists a counted run of any rgm211 loop or of "
                        "gemmLnc's as NOT RUN: no committed counted run of those loops, so their census entries stand (v3.1 README)")}
        self.dec['steps']['step0'] = s
        self.save()
        self.log(f'{now()} step 0: {len(self.P)} time points, {len(self.EP)} energy points, E213 arms {s["e213_arms"]}, '
                 f'T7 precondition {"PASS" if s["t7_precondition_pass"] else "FAIL"}')

    # ---------------------------------------------------------------- step 1: item 8 (no fit)
    def step1(self, scores_paths):
        if 'step1' in self.dec['steps']:
            return self.dec['steps']['step1']['form']
        it8 = F.DECL['items'][7]
        wc = it8['frozen_forecasts']['wall_cycles']
        reg = {r['id']: r for r in DV.e213_registry()}
        meas = {}
        src = {}
        for arm, pth in scores_paths.items():
            if not pth or not os.path.exists(pth):
                continue
            S = json.load(open(pth))
            A = S['arms'].get(arm) or {}
            for c in (A.get('cells') or {}).get('T1', []):
                meas[(arm, c['case'])] = c['measured']
            src[arm] = {'path': os.path.relpath(pth, REPO) if pth.startswith(REPO) else pth, 'sha256': sha(pth)}
        rows = []
        for cid in it8['frozen_forecasts']['cases']:
            r = reg[cid]
            arm = r['arm']
            m = meas.get((arm, r['case']))
            row = {'case_id': cid, 'arm': arm, 'case': r['case'], 'T5r': wc[cid]['T5r'], 'tC': wc[cid]['tC'], 'measured': m}
            if m is not None:
                d = abs(math.log(m / wc[cid]['T5r'])) - abs(math.log(m / wc[cid]['tC']))
                row['d'] = d
                row['tie'] = abs(d) <= 0.005
            rows.append(row)
        scored = [r for r in rows if r.get('d') is not None]
        untied = [r for r in scored if not r['tie']]
        k_tc = sum(1 for r in untied if r['d'] > 0)
        k_t5 = sum(1 for r in untied if r['d'] < 0)
        n = len(untied)
        p = None
        if n:
            from math import comb
            lo = sum(comb(n, i) for i in range(0, min(k_tc, k_t5) + 1)) / 2 ** n
            p = min(1.0, 2 * lo)
        if n < 10:
            verdict = 'NOT DECIDED (fewer than 10 untied cases)'
        elif p < 0.05:
            verdict = 'tC' if k_tc > k_t5 else 'T5r'
        else:
            verdict = 'NOT DECIDED'
        st1 = {'when': now(), 'rule': it8['rule'], 'sources': src, 'cases': rows, 'n_scored': len(scored), 'n_untied': n,
               'tC_closer': k_tc, 'T5r_closer': k_t5, 'ties': len(scored) - n, 'p_two_sided': p, 'verdict': verdict,
               'form': ('tC' if verdict == 'tC' else ('T5r' if verdict == 'T5r' else 'T5r (NOT DECIDED: item 8 step 3 at step 4)')),
               'decided': verdict in ('tC', 'T5r')}
        st1['tc'] = 'tC' if verdict == 'tC' else 'r2'
        self.dec['steps']['step1'] = st1
        self.save()
        self.log(f'{now()} step 1 (item 8): {n} untied of {len(scored)} scored; tC closer {k_tc}, T5r closer {k_t5}, p {p}: {verdict}')
        return st1['form']

    # ---------------------------------------------------------------- step 2: the trace check
    def step2(self, lanes):
        if 'step2' in self.dec['steps']:
            return self.dec['steps']['step2']['verdict']
        rd = {}
        for nm in ('v31-trace', 'verify-v31trace', 't7-0xf', 'verify-t7-0xf', 'land-walk-v31'):
            p = os.path.join(lanes, nm, 'result.json')
            if os.path.exists(p):
                j = json.load(open(p))
                rd[nm] = {'verdict': j.get('verdict'), 'result_sha256': sha(p)}
        walk = os.path.join(HERE, 'walk')
        pre = self.dec['steps']['step0']['t7_precondition_pass']
        chk = str(rd.get('t7-0xf', {}).get('verdict', ''))
        vf = os.path.join(walk, 'T7-TRACE-CHECK.json')
        if os.path.exists(vf):
            # the committed verdict (Q221's land at GitHub main) is the record the rule reads; the lanes' results beside
            V = json.load(open(vf))
            rd['committed T7-TRACE-CHECK.json'] = {'verdict': V.get('verdict'), 'sha256': sha(vf), 'criteria_by_mask': V.get('criteria_by_mask'),
                                                   'verify_v31trace': (V.get('verify_v31trace') or {}).get('verdict'),
                                                   'verify_t7_0xf': (V.get('verify_t7_0xf') or {}).get('verdict')}
            chk = str(V.get('verdict', chk))
        vt = str(rd.get('verify-t7-0xf', {}).get('verdict', ''))
        vv = str(rd.get('verify-v31trace', {}).get('verdict', ''))
        holds = vt.startswith('HOLDS') and vv.startswith('HOLDS')
        if not pre:
            verdict = 'NOT RUN'          # a failed desk precondition makes the trace check NOT RUN
        elif chk == 'PASS' and holds:
            verdict = 'PASS'
        elif chk.startswith('FAIL'):
            verdict = 'FAIL'
        else:
            verdict = 'NOT RUN'
        st = {'when': now(), 'lanes': rd, 'walk_folder_at_main': os.path.isdir(walk), 'desk_precondition_pass': pre, 'verdict': verdict,
              'reading': ("PASS = (a), (b) and (c) at both masks (t7-0xf's u2 at 0xf with verify-v31trace's u1 at 0x1111: the minimum log set "
                          "met at both masks), verify-v31trace HOLDS WITH FIXES with its fix (the 0xf run) applied and the check re-run, "
                          "verify-t7-0xf HOLDS WITH FIXES (wording), and the desk precondition re-run here (step 0)")}
        self.dec['steps']['step2'] = st
        self.save()
        self.log(f'{now()} step 2 (item 4 trace check): {verdict} ({rd})')
        return verdict

    # ---------------------------------------------------------------- step 3: item 3
    def step3(self):
        if 'step3' in self.dec['steps'] and 'winner' in self.dec['steps']['step3']:
            return self.dec['steps']['step3']['winner']
        tc = self.dec['steps']['step1']['tc']
        tcs = 'T5r' if tc == 'r2' else 'tC'
        recs = {}
        for G in ('G0', 'Gplace', 'Goperand', 'Gcoop'):
            name = f'{tcs}+{G}+n32'
            TR = self.time(name, 'loeo')
            pr, tw = self.loeo_pred(TR)
            touched = np.array([F._loop(p) in F.TOUCHED for p in self.P])
            sc = rms(self.err(pr, touched & ~tw))
            pool = rms(self.err(pr, np.ones(len(self.P), bool)))
            th = TR['theta_all']
            recs[G] = {'form': name, 'score_touched_no_twin': sc, 'n_touched_no_twin': int((touched & ~tw & ~np.isnan(pr)).sum()),
                       'score_touched_with_twins': rms(self.err(pr, touched)), 'pooled_LOEO_all': pool,
                       'constants': G_NCONST[G], 'all_data': {k: th.get(k) for k in TV.G_CONST[G]},
                       'per_fold_constants': {fn: {k: fd['theta'].get(k) for k in TV.G_CONST[G]} for fn, fd in TR['folds'].items()},
                       'per_fold_pins': {fn: sorted(k for k in fd['fit']['pins'] if k in TV.G_CONST[G]) for fn, fd in TR['folds'].items()}}
        best = min(recs[g]['score_touched_no_twin'] for g in recs)
        cands = [g for g in recs if recs[g]['score_touched_no_twin'] <= best + 0.25]
        order = {'G0': 0, 'Gcoop': 1, 'Gplace': 2, 'Goperand': 3}
        win = sorted(cands, key=lambda g: (recs[g]['constants'], order[g]))[0]
        guard = recs[win]['pooled_LOEO_all'] <= recs['G0']['pooled_LOEO_all'] + 0.05
        final = win if guard else 'G0'
        nw = None
        if final != 'G0':
            nw = all(abs(recs[final]['all_data'][k]) <= 0.01 * max(1.0, abs(BOXN(k))) for k in TV.G_CONST[final])
        st = {'when': now(), 'rule': F.DECL['items'][2]['rule'], 'forms': recs, 'lowest_score': best, 'candidates_within_0.25': cands,
              'rule_winner': win, 'guard_pass': guard, 'winner': final,
              'not_wanted': (final == 'G0') or bool(nw),
              'not_identified_all_constants_within_1pct_of_0': nw}
        self.dec['steps']['step3'] = st
        self.save()
        self.log(f'{now()} step 3 (item 3): scores {[(g, round(recs[g]["score_touched_no_twin"], 3)) for g in recs]}; winner {final} '
                 f'(rule {win}, guard {guard})')
        return final

    # ---------------------------------------------------------------- step 4: item 4 (and item 8 step 3)
    def lolo_and_loeo(self, TR):
        pr_lolo = self.fam_pred(TR, 'LOLO ')
        sub = np.array([F.lolo_class(p['mask']) is not None for p in self.P])
        pr_loeo, _ = self.loeo_pred(TR)
        by = {lc: rms(self.err(pr_lolo, np.array([F.lolo_class(p['mask']) == lc for p in self.P]))) for lc in ('compact', 'spread', 'other')}
        return rms(self.err(pr_lolo, sub)), rms(self.err(pr_loeo, np.ones(len(self.P), bool))), by

    def step4(self, trace):
        st = self.dec['steps'].get('step4') or {}
        if 'layout' not in st:
            tc = self.dec['steps']['step1']['tc']
            tcs = 'T5r' if tc == 'r2' else 'tC'
            G = self.dec['steps']['step3']['winner']
            recs = {}
            lays = ('T7', 'demand', 'n32') if trace == 'PASS' else ('demand', 'n32')
            for lay in lays:
                name = f'{tcs}+{G}+{lay}'
                TR = self.time(name, 'loeo,lolo')
                lolo, loeo, by = self.lolo_and_loeo(TR)
                recs[lay] = {'form': name, 'LOLO_subset_rms': lolo, 'LOLO_by_class': by, 'pooled_LOEO_all': loeo}
            if trace == 'PASS':
                best_loeo = min(recs[l]['pooled_LOEO_all'] for l in recs)
                t7_in = (recs['T7']['LOLO_subset_rms'] < recs['demand']['LOLO_subset_rms'] and recs['T7']['LOLO_subset_rms'] < recs['n32']['LOLO_subset_rms']
                         and recs['T7']['pooled_LOEO_all'] <= best_loeo + 0.05)
            else:
                t7_in = False
            if t7_in:
                lay = 'T7'
                how = 'T7 enters (step 1 of the rule)'
            else:
                a, b = recs['demand']['pooled_LOEO_all'], recs['n32']['pooled_LOEO_all']
                lay = 'demand' if a < b - 0.05 else 'n32'
                how = "T7 stays out; T7L against n/32 by v3's declared time rule"
            st.update({'when': now(), 'trace_check': trace, 'forms': recs, 'T7_enters': t7_in, 'layout': lay, 'how': how,
                       'rule': F.DECL['items'][3]['rule']})
            self.dec['steps']['step4'] = st
            self.save()
            self.log(f'{now()} step 4 (item 4): {[(l, round(recs[l]["LOLO_subset_rms"], 3), round(recs[l]["pooled_LOEO_all"], 3)) for l in recs]} -> {lay}')
        if not self.dec['steps']['step1']['decided'] and 'item8_step3' not in st:
            G = self.dec['steps']['step3']['winner']
            lay = st['layout']
            res = {}
            for tcs in ('T5r', 'tC'):
                TR = self.time(f'{tcs}+{G}+{lay}', 'loeo')
                pr, _ = self.loeo_pred(TR)
                res[tcs] = rms(self.err(pr, np.ones(len(self.P), bool)))
            win = 'tC' if res['tC'] < res['T5r'] - 0.05 else 'T5r'
            st['item8_step3'] = {'pooled_LOEO_all': res, 'winner': win, 'rule': 'the lower pooled LOEO wall rms over all points; within 0.05 points T5r'}
            self.dec['steps']['step1']['tc'] = 'tC' if win == 'tC' else 'r2'
            self.dec['steps']['step1']['form'] = win + ' (item 8 step 3)'
            self.dec['steps']['step4'] = st
            self.save()
            self.log(f'{now()} item 8 step 3: {res} -> {win}')
        tcs = 'T5r' if self.dec['steps']['step1']['tc'] == 'r2' else 'tC'
        final = f"{tcs}+{self.dec['steps']['step3']['winner']}+{st['layout']}"
        self.dec['final_time_form'] = final
        self.save()
        return final

    # ---------------------------------------------------------------- step 5
    def step5(self, final):
        self.time(final, 'all')
        self.time('T5r+G0+n32', 'all')
        self.dec['steps']['step5'] = {'when': now(), 'final_time_form': final, 'v3_refitted': 'T5r+G0+n32'}
        self.save()

    # ---------------------------------------------------------------- step 6: item 1
    def energy(self, tname, eforms, which):
        TR = self.TR.get(tname) or json.load(open(os.path.join(self.fits, f'time_{tname}.json')))
        t0 = time.time()
        self.log(f'{now()} energy {eforms} on {tname} folds {which}')
        r = F.run_energy(TR, eforms, self.fits, EP=self.EP, X=self.X, en=self.enE, which=which, log=self.log, tag=self.tag)
        self.log(f'{now()} energy done ({time.time() - t0:.0f} s)')
        return r

    def e_loeo(self, ER, ef):
        """per energy point: the LOEO (and E210) fold's W given t, W with t forecast, T forecast, and the twin flag (kind included)"""
        N = len(self.EP)
        g, f_, tf = np.full(N, np.nan), np.full(N, np.nan), np.full(N, np.nan)
        tw = np.zeros(N, bool)
        use = self.X.usable3
        for name, fd in ER['forms'][ef]['folds'].items():
            if not (name.startswith('LOEO ') and (name[5:] in F.LOEO_EXPS or name == 'LOEO E210')):
                continue
            te = np.array(fd['test_idx'])
            g[te], f_[te], tf[te] = fd['W_given_t'], fd['W_forecast_t'], fd['T_forecast']
            m = np.zeros(N, bool)
            m[te] = True
            trc = {F.cfg_e(self.EP[i]) for i in range(N) if not m[i] and use[i] and not self.erung[i]}
            for i in te:
                tw[i] = F.cfg_e(self.EP[i]) in trc
        return g, f_, tf, tw

    def escores(self, g, f_, tf, sel):
        w, t, idle = self.X.w, self.X.t, self.X.idle
        ii = np.array([i for i in range(len(self.EP)) if sel[i] and not math.isnan(g[i])], int)
        hi = ii[w[ii] >= LOW]
        lo = ii[w[ii] < LOW]
        return {'W given t (>= 3 W)': stat(g[hi] / w[hi] - 1),
                'J over idle t forecast (>= 3 W)': stat(f_[hi] * tf[hi] / (w[hi] * t[hi]) - 1),
                'J at rest given t': stat([(idle[i] + g[i]) / (idle[i] + w[i]) - 1 for i in ii if not math.isnan(idle[i])]),
                'J at rest t forecast': stat([(idle[i] + f_[i]) * tf[i] / ((idle[i] + w[i]) * t[i]) - 1 for i in ii if not math.isnan(idle[i])]),
                'W under 3 W, watts': ({'n': int(len(lo)), 'rms_W': float(np.sqrt(np.mean((g[lo] - w[lo]) ** 2)))} if len(lo) else None)}

    def step6(self, final):
        st = self.dec['steps'].get('step6') or {}
        if 'winner' not in st:
            ER = self.energy(final, ['E1u', 'E1b', 'E1t', 'E1m'], 'loeo,loco')
            preds = {ef: self.e_loeo(ER, ef) for ef in ('E1u', 'E1b', 'E1t', 'E1m')}
            both = self.X.usable3.copy()
            for ef, (g, f_, tf, tw) in preds.items():
                both &= ~np.isnan(g)
            tw_any = preds['E1u'][3]
            sc = {}
            for ef, (g, f_, tf, tw) in preds.items():
                sel = both & ~tw_any & (self.X.w >= LOW)
                sc[ef] = {'score_LOEO_W_given_t_no_twin': rms([g[i] / self.X.w[i] - 1 for i in range(len(self.EP)) if sel[i]]),
                          'n': int(sel.sum()), 'with_twins': self.escores(g, f_, tf, both),
                          'no_twins': self.escores(g, f_, tf, both & ~tw_any),
                          'all_data': {k: ER['forms'][ef]['theta_all'].get(k) for k in ('b2', 'd2', 'xi', 'b3', 'd3')},
                          'per_fold_b2_d2_xi': {fn: {k: fd['theta'].get(k) for k in ('b2', 'd2', 'xi')} for fn, fd in ER['forms'][ef]['folds'].items()}}
            three = ['E1b', 'E1t', 'E1m']
            lowest = min(sc[e]['score_LOEO_W_given_t_no_twin'] for e in three)
            cands = [e for e in three if sc[e]['score_LOEO_W_given_t_no_twin'] <= lowest + 0.10]
            nconst = {'E1b': 26, 'E1t': 24, 'E1m': 24}
            order = {'E1t': 0, 'E1m': 1, 'E1b': 2}
            win3 = sorted(cands, key=lambda e: (nconst[e], order[e]))[0]
            u = sc['E1u']['score_LOEO_W_given_t_no_twin']
            winner = 'E1u' if u < sc[win3]['score_LOEO_W_given_t_no_twin'] - 0.30 else win3
            b2, d2 = ER['forms']['E1b']['theta_all']['b2'], ER['forms']['E1b']['theta_all']['d2']
            st.update({'when': now(), 'rule': F.DECL['items'][0]['rule'], 'forms': sc, 'lowest_of_three': lowest, 'candidates_within_0.10': cands,
                       'winner_of_three': win3, 'winner': winner, 'split_identified': winner != 'E1u',
                       'E1b_all_data_b2_d2_at_bound': bool(abs(b2) < 1e-9 and abs(d2) < 1e-9)})
            self.dec['steps']['step6'] = st
            self.dec['final_energy_form'] = winner
            self.save()
            self.log(f'{now()} step 6 (item 1): {[(e, round(sc[e]["score_LOEO_W_given_t_no_twin"], 3)) for e in sc]} -> {winner}')
        winner = st['winner']
        self.energy(final, [winner], 'all')
        self.energy(final, ['ledger'], 'loeo,loko')
        self.energy('T5r+G0+n32', ['E1u'], 'all')
        return winner

    # ---------------------------------------------------------------- step 7: item 2 and the acceptance rules
    def loco_energy(self, ER, ef):
        N = len(self.EP)
        out = {}
        for route in ('anchor', 'fallback'):
            g = np.full(N, np.nan)
            excl = np.zeros(N, bool)
            per = {}
            for name, fd in ER['forms'][ef]['folds'].items():
                if not name.startswith('LOCO '):
                    continue
                te = np.array(fd['test_idx'])
                g[te] = fd['W_given_t_' + route]
                card = name[5:]
                for i in F.anchor_points(self.EP, card):
                    excl[i] = True
                per[card] = {'kc_anchor': fd['anchor'].get('kc'), 'valid': fd['anchor'].get('valid'), 'route_used': fd['anchor_route_used'],
                             'share_kc_term': fd['anchor'].get('share_kc_term'), 'anchor_points': fd['anchor'].get('anchor_points'),
                             'anchor_residuals': fd['anchor'].get('anchor_residuals'),
                             'kc_fallback': (fd['theta'].get('kc|' + card, 1.0) if card != EV.CARDS[0] else 1.0)}
            sel = self.X.usable3 & ~np.isnan(g) & (self.X.w >= LOW)
            out[route] = {'pooled_no_anchor_points': stat([g[i] / self.X.w[i] - 1 for i in range(N) if sel[i] and not excl[i]]),
                          'pooled_with_anchor_points_REPORTED': stat([g[i] / self.X.w[i] - 1 for i in range(N) if sel[i]]),
                          'per_card': {c: stat([g[i] / self.X.w[i] - 1 for i in range(N) if sel[i] and not excl[i] and self.EP[i]['card'] == c])
                                       for c in EV.CARDS}, 'folds': per}
        return out

    def step7(self, final, ef):
        TR31 = self.TR.get(final) or json.load(open(os.path.join(self.fits, f'time_{final}.json')))
        TRv3 = self.TR.get('T5r+G0+n32') or json.load(open(os.path.join(self.fits, 'time_T5r+G0+n32.json')))
        ER31 = json.load(open(os.path.join(self.fits, f'energy_{final}.json')))
        ERv3 = json.load(open(os.path.join(self.fits, 'energy_T5r+G0+n32.json')))
        acc = {}
        p31, tw31 = self.loeo_pred(TR31)
        pv3, twv3 = self.loeo_pred(TRv3)
        allp = np.ones(len(self.P), bool)
        g31, f31, tf31, etw = self.e_loeo(ER31, ef)
        gv3, fv3, tfv3, _ = self.e_loeo(ERv3, 'E1u')
        both = self.X.usable3 & ~np.isnan(g31) & ~np.isnan(gv3) & (self.X.w >= LOW)
        e31 = rms([g31[i] / self.X.w[i] - 1 for i in range(len(self.EP)) if both[i] and not etw[i]])
        ev3 = rms([gv3[i] / self.X.w[i] - 1 for i in range(len(self.EP)) if both[i] and not etw[i]])
        w31 = rms(self.err(p31, ~tw31))
        wv3 = rms(self.err(pv3, ~tw31))
        acc['1'] = {'LOEO wall no twin': {'v31': w31, 'v3_refitted': wv3}, 'LOEO W given t no twin (>= 3 W, both price)': {'v31': e31, 'v3_refitted': ev3},
                    'with_twins_beside': {'wall': {'v31': rms(self.err(p31, allp)), 'v3_refitted': rms(self.err(pv3, allp))}},
                    'pass': bool(w31 < wv3 and e31 < ev3)}
        l31 = rms(self.err(self.fam_pred(TR31, 'LOCO '), allp))
        lv3 = rms(self.err(self.fam_pred(TRv3, 'LOCO '), allp))
        lc31 = self.loco_energy(ER31, ef)
        lcv3 = self.loco_energy(ERv3, 'E1u')
        ea, eb = lc31['anchor']['pooled_no_anchor_points']['rms_pct'], lcv3['anchor']['pooled_no_anchor_points']['rms_pct']
        acc['2'] = {'LOCO wall (every point)': {'v31': l31, 'v3_refitted': lv3}, 'LOCO W given t (anchor route)': {'v31': ea, 'v3_refitted': eb},
                    'fallback_route_beside': {'v31': lc31['fallback']['pooled_no_anchor_points'], 'v3_refitted': lcv3['fallback']['pooled_no_anchor_points']},
                    'v31_routes': lc31, 'v3_refitted_routes': lcv3,
                    'not_wanted_anchor_above_fallback_v31': bool(ea > lc31['fallback']['pooled_no_anchor_points']['rms_pct']),
                    'pass': bool(l31 <= lv3 + 0.30 and ea <= eb + 0.30)}
        fk = TR31['folds'].get('LEAVE rgm211 out')
        rg = np.array([p['kernel'] == 'rgm211' for p in self.P])
        lw = rms(self.err(self.fam_pred(TR31, 'LEAVE rgm211'), rg))
        wp = self.w_pairs(self.en.predict(fk['theta'], F.parse_form_name(final)[0]))
        wpv3 = self.w_pairs(self.en.predict(TRv3['folds']['LEAVE rgm211 out']['theta'], F.parse_form_name('T5r+G0+n32')[0]))
        acc['3'] = {'leave rgm211 out wall rms': lw, 'n': int(rg.sum()), 'E211 W pairs': wp, 'v3_refitted_beside': {
            'wall': rms(self.err(self.fam_pred(TRv3, 'LEAVE rgm211'), rg)), 'pairs': wpv3},
            'E213_rgm211_rgm136_pairs_REPORTED': self.e213_pairs(self.en.predict(fk['theta'], F.parse_form_name(final)[0])),
            'pass': bool(lw <= 8.0 and wp['inside_0.05'] >= 7)}
        acc['4a'] = self.rule4a(TR31, ER31, ef)
        acc['4b'] = self.rule4b(TR31, ER31, ef)
        acc['accepted'] = all(acc[k]['pass'] for k in ('1', '2', '3', '4a', '4b') if isinstance(acc[k], dict) and 'pass' in acc[k])
        self.dec['steps']['step7'] = {'when': now(), 'acceptance': acc}
        self.save()
        self.log(f'{now()} step 7: acceptance ' + json.dumps({k: (v.get('pass') if isinstance(v, dict) else v) for k, v in acc.items()}))
        return acc

    def w_pairs(self, pred):
        by = {}
        for i, p in enumerate(self.P):
            if p['exp'] == 'E211' and (p.get('pair') or '').startswith('w'):
                by.setdefault(p['pair'], {})['n' if p['kernel'] == 'rgm211' else 'm'] = i
        lns = {}
        for k, q in sorted(by.items()):
            if 'n' in q and 'm' in q:
                mr = self.P[q['n']]['T'] / self.P[q['m']]['T']
                fr = pred[q['n']] / pred[q['m']]
                lns[k] = round(float(math.log(fr / mr)), 5)
        v = list(lns.values())
        return {'pairs': lns, 'inside_0.05': int(sum(abs(x) <= 0.05 for x in v)), 'n': len(v),
                'rms_ln': (round(float(np.sqrt(np.mean(np.square(v)))), 5) if v else None)}

    def e213_pairs(self, pred):
        """E213's rgm211 / rgm136 pairs at one shape (family P): ln of the forecast ratio over the measured, per loop against rgm136 gemmL"""
        by = collections.defaultdict(dict)
        for i, p in enumerate(self.P):
            if p['exp'] == 'E213':
                by[(p['card'], E.arm_parts(p['arm'])[1], p['fmt'])][F._loop(p)] = i
        out = {}
        for (card, b, fmt), d in sorted(by.items(), key=lambda x: str(x[0])):
            if 'rgm136 gemmL' not in d:
                continue
            m = d['rgm136 gemmL']
            for lp, i in d.items():
                if lp == 'rgm136 gemmL':
                    continue
                out[f'{card} {b} {fmt} {lp}'] = round(float(math.log((pred[i] / pred[m]) / (self.P[i]['T'] / self.P[m]['T']))), 5)
        return out

    def rule4a(self, TR31, ER31, ef):
        fd = TR31['folds']['LOEO E212']
        te = np.array(fd['test_idx'])
        N = len(self.P)
        m = np.zeros(N, bool)
        m[te] = True
        trc = {F.cfg_t(self.P[i]) for i in range(N) if not m[i] and not self.rung[i]}
        efd = ER31['forms'][ef]['folds'].get('LOEO E212')
        eidx = {self.EP[i]['id']: (k, i) for k, i in enumerate(efd['test_idx'])} if efd else {}
        path = os.path.join(self.out, 'v31-e212-fold.csv')
        with open(path, 'w', newline='') as fh:
            w = csv.writer(fh, lineterminator='\n')
            w.writerow(['id', 'meas_cyc_wall', 'e_wall', 'meas_w', 'e_w_given_t', 'is_twin'])
            for k, i in enumerate(te):
                p = self.P[i]
                row = [p['id'], repr(p['cw']), repr(fd['pred_test'][k] / self.Tm[i] - 1)]
                ew = eidx.get(p['id'])
                if ew is not None:
                    kk, ii = ew
                    mw = self.X.w[ii]
                    row += [repr(mw), repr(efd['W_given_t'][kk] / mw - 1) if mw >= LOW else '']
                else:
                    row += ['', '']
                row.append('1' if F.cfg_t(p) in trc else '0')
                w.writerow(row)
        outj = os.path.join(self.out, 'rule4a_v31.json')
        r = subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, 'comparator_4a_v31.py'), '--score', path, '--repo', REPO, '--out', outj],
                           capture_output=True, text=True)
        res = json.load(open(outj))['score'] if os.path.exists(outj) else {'error': r.stderr[-2000:]}
        res['comparator_rc'] = r.returncode
        res['pass'] = res.get('rule_4a') == 'PASS'
        res['csv_sha256'] = sha(path)
        return res

    def rule4b(self, TR31, ER31, ef):
        """the E213 fold (both arms) under MM1-v3's blind error on the same E213 points (scores-e213's committed cells)"""
        res = {'arms': {}}
        fd = TR31['folds'].get('LOEO E213')
        efd = ER31['forms'][ef]['folds'].get('LOEO E213')
        if fd is None:
            return {'pass': False, 'note': 'no E213 fold'}
        tpred = {self.P[i]['id']: fd['pred_test'][k] for k, i in enumerate(fd['test_idx'])}
        epred = {self.EP[i]['id']: (efd['W_given_t'][k], i) for k, i in enumerate(efd['test_idx'])} if efd else {}
        t31, tv3, w31, wv3 = [], [], [], []
        for arm, pth in self.scores_paths.items():
            if not pth or not os.path.exists(pth):
                continue
            A = json.load(open(pth))['arms'].get(arm) or {}
            cells = A.get('cells') or {}
            ck = 'a3' if arm == 'A' else 'c1'
            reg = {r['id']: r for r in DV.e213_registry() if r['arm'] == arm}
            ta, tb, wa, wb = [], [], [], []
            for c in cells.get('T1', []):
                pid = f"E213|{ck}|{c['case']}"
                if pid not in tpred:
                    continue
                ta.append(tpred[pid] * 600.0 / c['measured'] - 1)
                tb.append(c['err'])
            for c in cells.get('E1', []):
                if c.get('watts'):
                    continue
                r = reg.get(c['point'])
                if r is None or r['role'] != 'point':
                    continue
                eid = f"E213|{ck}|{c['point']}"
                if eid not in epred:
                    continue
                Wg, i = epred[eid]
                wa.append(Wg / self.X.w[i] - 1)
                wb.append(c['err'])
            res['arms'][arm] = {'wall_cases': {'v31': stat(ta), 'v3_blind': stat(tb)}, 'W_given_t_points': {'v31': stat(wa), 'v3_blind': stat(wb)}}
            t31 += ta
            tv3 += tb
            w31 += wa
            wv3 += wb
        res['pooled'] = {'wall_cases': {'v31': stat(t31), 'v3_blind': stat(tv3)}, 'W_given_t_points': {'v31': stat(w31), 'v3_blind': stat(wv3)}}
        refs = {}
        for i in fd['test_idx']:
            p = self.P[i]
            if p['exp'] == 'E213' and p.get('role') == 'reference':
                refs[p['id']] = {'v31_E213_fold_err_wall': tpred[p['id']] / self.Tm[i] - 1, 'pids': p.get('pids')}
        res['references_REPORTED'] = refs
        ok = bool(t31 and w31 and rms(t31) < rms(tv3) and rms(w31) < rms(wv3))
        res['pass'] = ok
        res['note'] = ("v3.1's E213 fold (E213 held out; post hoc for the forms E213 helped choose) against MM1-v3's blind E213 error "
                       "(scores-e213's cells T1 per case, E1 per point at 3 W and above); references excluded")
        return res


def BOXN(k):
    return F.BOX.get(k, {}).get('neutral') or 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--lanes', default=os.environ.get('W_OUT', ''), help="the round's lane folders (W/out), where the trace-check lanes' results are")
    ap.add_argument('--scores-A', default=os.path.join(REPO, 'docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/scores-e213-A.json'))
    ap.add_argument('--scores-B', default='')
    ap.add_argument('--until', default='7')
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    logf = open(os.path.join(out, 'run.log'), 'a')

    def log(s):
        print(s, flush=True)
        logf.write(s + '\n')
        logf.flush()
    log(f'{now()} run_v31 start, tag {a.tag}, python {sys.version.split()[0]}, numpy {np.__version__}')
    R = Run(out, a.tag, log)
    R.scores_paths = {'A': a.scores_A, 'B': a.scores_B}
    R.step0()
    R.step1(R.scores_paths)
    trace = R.step2(a.lanes)
    if a.until == '2':
        return
    R.step3()
    final = R.step4(trace)
    R.step5(final)
    ef = R.step6(final)
    R.step7(final, ef)
    log(f'{now()} run_v31 end: final time form {final}, energy form {ef}')


if __name__ == '__main__':
    main()
