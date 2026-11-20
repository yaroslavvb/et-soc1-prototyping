#!/usr/bin/env python3
"""MM1-v3.2: the declared order of decisions (DECLARED-v32.md section 10), each by its rule, from fit_v32.py's fits. Desk; post hoc as a fit.

    /usr/bin/python3 -I -B run_v32.py --out <dir> --tag <rehearsal | final> --scores-e215 <dir with E215's committed scores or ''>
        step 0: every input's sha256 (sections 1, 4), E215's blob ids and sha256, the gate (E215's blind scores on GitHub main), the
                E215 reader's two record readings, the census-path record as v3.1 left it;
        step 1: time: T5r+G0+n32 on every fold (section 2, the eta pin): MM1-v3.2's base and MM1-v3 refitted's time;
        step 2: the layout term: features (v01_map), F1's check, the bundle from step 1's fits, layout_rule_v32.py decide (the frozen code,
                run as a subprocess) -> the term or none;
        step 3: energy: E1t+F3 on every fold (F3's pins) and E1u (MM1-v3 refitted) on every fold, each on its time fold; the ledger REPORTED;
        step 4: the acceptance rules (section 7).
    Every step writes <dir>/decisions_v32.json as it goes; every fit is resumable (fit_v31.run_time and fit_v32.run_energy keep partial
    records).
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
import fit_v32 as FV  # noqa: E402

F = FV.F
TV, DV, EV, E, C = FV.TV, FV.DV, FV.EV, FV.E, FV.C
import layout_v32 as LY  # noqa: E402

REPO = TV.REPO
V31 = os.path.join(REPO, 'tools/matmul/mm1/v3.1')
LOW = 3.0
DECL = FV.DECL
FORM = 'T5r+G0+n32'
EFORM = 'E1t+F3'
GIT_ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def now():
    return time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())


def rms(e):
    e = np.asarray([x for x in e if x is not None and not (isinstance(x, float) and math.isnan(x))], float)
    return float(np.sqrt(np.mean(e ** 2))) * 100 if len(e) else None


def stat(e):
    return F.stat(e)


def git(*a):
    return subprocess.run(['git', '-C', REPO] + list(a), capture_output=True, text=True, env=GIT_ENV).stdout.strip()


class Run:
    def __init__(self, out, tag, log):
        self.out = out
        self.fits = os.path.join(out, 'fits')
        os.makedirs(self.fits, exist_ok=True)
        self.tag = tag
        self.log = log
        self.dec_path = os.path.join(out, 'decisions_v32.json')
        self.dec = json.load(open(self.dec_path)) if os.path.exists(self.dec_path) else {'tag': tag, 'steps': {}}
        self.P = DV.time_points()
        self.Tm = np.array([p['T'] for p in self.P])
        self.rung = F.rung_mask(self.P)
        self.en = TV.Engine31(self.P, t7_cache_dir=os.path.join(out, 'cache'))
        self.EP = DV.energy_points()
        self.X = EV.Features32(self.EP)
        self.enE = TV.Engine31(self.EP, t7_cache_dir=os.path.join(out, 'cache'))
        self.erung = F.rung_mask(self.EP)
        self.TR = None
        self.layout = None

    def save(self):
        json.dump(self.dec, open(self.dec_path + '.tmp', 'w'), indent=1, sort_keys=True, default=float)
        os.replace(self.dec_path + '.tmp', self.dec_path)

    # ---------------------------------------------------------------- helpers: held-out predictions and twins
    def loeo_twins(self, TR):
        """(pred (N,), twin (N,)) over the 20 main LOEO folds (the sub-folds apart)"""
        N = len(self.P)
        pr = np.full(N, np.nan)
        tw = np.zeros(N, bool)
        for name, fd in TR['folds'].items():
            if not (name.startswith('LOEO ') and name[5:] in FV.LOEO_EXPS):
                continue
            te = np.array(fd['test_idx'])
            pr[te] = fd['pred_test']
            m = np.zeros(N, bool)
            m[te] = True
            trc = {F.cfg_t(self.P[i]) for i in range(N) if not m[i] and not self.rung[i]}
            for i in te:
                tw[i] = F.cfg_t(self.P[i]) in trc
        return pr, tw

    def fam_pred(self, TR, prefix, layout=False):
        N = len(self.P)
        pr = np.full(N, np.nan)
        for name, fd in TR['folds'].items():
            if name.startswith(prefix):
                te = np.array(fd['test_idx'])
                v = np.array(fd['pred_test'])
                if layout:
                    v = v * self.tfactor(name)[te]
                pr[te] = v
        return pr

    def tfactor(self, fold):
        """the chosen layout term's factor over the time points in a fold (1 everywhere when none entered)"""
        L = self.layout
        if L is None or L['enters'] == 'none':
            return np.ones(len(self.P))
        return L['factor_time'][fold]

    def err(self, pr, sel):
        return [pr[i] / self.Tm[i] - 1 for i in range(len(self.P)) if sel[i] and not math.isnan(pr[i])]

    # ---------------------------------------------------------------- step 0
    def step0(self, scores_dir):
        if 'step0' in self.dec['steps']:
            return
        s = {'when': now(), 'interpreter': '/usr/bin/python3 %s, numpy %s' % (sys.version.split()[0], np.__version__)}
        import scipy
        s['scipy'] = scipy.__version__
        s['repo_head'] = git('rev-parse', 'HEAD')
        s['repo_head_date'] = git('log', '-1', '--format=%cd', '--date=iso')
        s['repo_status_lines_tracked'] = len([x for x in git('status', '--porcelain', '--untracked-files=no').splitlines() if x.strip()])
        s['threads'] = {k: os.environ.get(k) for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')}
        s['n_time_points'] = len(self.P)
        s['time_points_by_exp'] = dict(sorted(collections.Counter(p['exp'] for p in self.P).items()))
        s['n_energy_points'] = len(self.EP)
        s['energy_points_by_exp'] = dict(sorted(collections.Counter(e['exp'] for e in self.EP).items()))
        s['energy_usable'] = int(self.X.usable3.sum())
        s['energy_not_forecast'] = [self.EP[i]['id'] for i in range(len(self.EP)) if not self.X.usable3[i]]
        s['store_rungs'] = int(self.rung.sum())
        s['e215_arms'] = DV.e215_available()
        # the frozen files (sha256 equal to DECLARED-v32.sha256 and the declaration's builds_on table)
        want = {}
        for line in open(os.path.join(HERE, 'DECLARED-v32.sha256')):
            h, p = line.split()
            want[p] = h
        chk = {}
        for p, h in want.items():
            g = sha(os.path.join(HERE, p))
            chk['v3.2/' + p] = {'want': h, 'got': g, 'equal': g == h}
        b = DECL['builds_on']
        v31 = b['mm1_v31']
        for k, rel in (('DECLARED-v31.md', 'DECLARED-v31.md'), ('declared-v31.json', 'declared-v31.json'), ('SHA256SUMS', 'SHA256SUMS'),
                       ('time_v31.py', 'time_v31.py'), ('energy_v31.py', 'energy_v31.py'), ('fit_v31.py', 'fit_v31.py'),
                       ('data_v31.py', 'data_v31.py'), ('mm1_v31.py', 'mm1_v31.py'), ('params', 'out/mm1_v31_params.json'),
                       ('time_fit_record', 'out/fits/time_T5r+G0+n32.json'), ('census-v3.1.json', 'inputs/census/census-v3.1.json'),
                       ('comparator_4a_v31.py', 'comparator_4a_v31.py')):
            g = sha(os.path.join(V31, rel))
            chk['v3.1/' + rel] = {'want': v31[k], 'got': g, 'equal': g == v31[k]}
        for k, rel in (('SHA256SUMS', 'SHA256SUMS'), ('mm1_v3.py', 'mm1_v3.py'), ('params', 'out/mm1_v3_params.json'),
                       ('inputs_SOURCES.tsv', 'inputs/SOURCES.tsv')):
            g = sha(os.path.join(REPO, 'tools/matmul/mm1/v3', rel))
            chk['v3/' + rel] = {'want': b['mm1_v3'][k], 'got': g, 'equal': g == b['mm1_v3'][k]}
        for k, rel in (('SHA256SUMS', 'SHA256SUMS'), ('mm1_v2.py', 'mm1_v2.py'), ('params', 'out/mm1_v2_params.json')):
            g = sha(os.path.join(REPO, 'tools/matmul/mm1/v2', rel))
            chk['v2/' + rel] = {'want': b['mm1_v2'][k], 'got': g, 'equal': g == b['mm1_v2'][k]}
        tg = b['term_gemmlnc_F3']
        for k in ('term-gemmlnc.json', 'forecasts-gemmlnc-e215.csv', 'forecasts-gemmlnc-e215.json', 's05_freeze.py', 'README.md.dated-note-1.md'):
            g = sha(os.path.join(REPO, tg['path'], k))
            chk['gemmlnc/' + k] = {'want': tg[k], 'got': g, 'equal': g == tg[k]}
        tl = b['term_layout_F1_and_controls']
        for k in ('DECLARED-layout.md', 'DECLARED-layout-addendum-1.md', 'features_layout.py', 'eval_layout.py', 'forecast-e215-v31-layout.csv',
                  'controls-e215/v01_map.py', 'controls-e215/v02_fits.py', 'controls-e215/v02_e215_controls.csv', 'controls-e215/work/v01_map.json',
                  'README.md.dated-note-1.md'):
            g = sha(os.path.join(REPO, tl['path'], k))
            chk['layout/' + k] = {'want': tl[k], 'got': g, 'equal': g == tl[k]}
        er = b['e215_registration']
        for k in ('E215.md', 'points-e215.csv', 'score_e215.py'):
            g = sha(os.path.join(REPO, 'tools/claims-v3/e215', k))
            chk['e215/' + k] = {'want': er[k], 'got': g, 'equal': g == er[k]}
        for k in ('neverrun_e215.py',):
            g = sha(os.path.join(REPO, 'tools/claims-v3/e215/desk', k))
            chk['e215/desk/' + k] = {'want': er[k], 'got': g, 'equal': g == er[k]}
        ue = b['unread_e214']
        for k, v in ue.items():
            if k.endswith(('.md', '.json', '.csv')) and os.path.exists(os.path.join(REPO, ue['path'], k)):
                g = sha(os.path.join(REPO, ue['path'], k))
                chk['unread-e214/' + k] = {'want': v, 'got': g, 'equal': g == v}
        s['frozen_files'] = chk
        s['frozen_files_all_equal'] = all(v['equal'] for v in chk.values())
        assert s['frozen_files_all_equal'], {k: v for k, v in chk.items() if not v['equal']}
        # the counts
        for nm in ('counts', 'counts-e214'):
            d = os.path.join(V31, nm)
            s[nm + '_SHA256SUMS'] = sha(os.path.join(d, 'SHA256SUMS'))
            s[nm + '_check_rc'] = subprocess.run(['sha256sum', '-c', '--quiet', 'SHA256SUMS'], cwd=d, capture_output=True, text=True).returncode
        assert s['counts_SHA256SUMS'] == DECL['items']['E']['counts']['counts/']['SHA256SUMS']
        assert s['counts-e214_SHA256SUMS'] == DECL['items']['E']['counts']['counts-e214/']['SHA256SUMS']
        assert s['counts_check_rc'] == 0 and s['counts-e214_check_rc'] == 0
        s['energy_inputs_merge'] = {k: (v if k != 'rows_added' else len(v)) for k, v in EV.MERGE.items()}
        # every vendored input of MM1-v3 and MM1-v3.1 against its SOURCES.tsv
        bad = []
        nfile = 0
        for d in ('v3', 'v3.1'):
            base = os.path.join(REPO, 'tools/matmul/mm1', d)
            for row in csv.DictReader(open(os.path.join(base, 'inputs', 'SOURCES.tsv')), delimiter='\t'):
                p = os.path.join(base, row[d + '_path'])
                nfile += 1
                if not os.path.exists(p) or sha(p) != row['sha256']:
                    bad.append(row[d + '_path'])
        s['vendored_inputs_checked'] = nfile
        s['vendored_inputs_mismatch'] = bad
        assert not bad, bad
        # E214's reductions
        e14 = {}
        for r in DECL['data']['e214']:
            p = os.path.join(HERE, 'inputs', 'e214', '%s__%s' % (r['session'], os.path.basename(r['reduction'])))
            g = sha(p)
            e14[r['session']] = {'vendored': os.path.relpath(p, HERE), 'sha256': g, 'equal': g == r['sha256'],
                                 'data_commit': r['data_commit'],
                                 'ancestor_of_head': subprocess.run(['git', '-C', REPO, 'merge-base', '--is-ancestor', r['data_commit'], 'HEAD']).returncode == 0}
        s['e214'] = e14
        assert all(v['equal'] and v['ancestor_of_head'] for v in e14.values()), e14
        # E215: blob ids, sha256, ancestry, and the gate
        e15 = {}
        for r in DECL['data']['e215']:
            fn = os.path.join(HERE, 'inputs', 'e215', 'data-e215-%s.json' % r['arm'])
            if not os.path.exists(fn):
                e15[r['arm']] = {'vendored': False}
                continue
            blob = subprocess.run(['git', 'hash-object', fn], capture_output=True, text=True).stdout.strip()
            src = os.path.join(REPO, r['data_dir'], 'data-e215.json')
            e15[r['arm']] = {'vendored': True, 'git_hash_object': blob, 'declared_blob_id': r['data_e215_json_blob_id'],
                             'blob_equal': blob == r['data_e215_json_blob_id'], 'sha256': sha(fn), 'source': r['data_dir'] + '/data-e215.json',
                             'source_sha256_equal': sha(src) == sha(fn), 'data_commit': r['data_commit'],
                             'ancestor_of_head': subprocess.run(['git', '-C', REPO, 'merge-base', '--is-ancestor', r['data_commit'], 'HEAD']).returncode == 0,
                             'tree_id_at_commit': git('rev-parse', r['data_commit'] + ':' + r['data_dir']),
                             'declared_tree_id': r['tree_id']}
            assert e15[r['arm']]['blob_equal'] and e15[r['arm']]['ancestor_of_head'], e15[r['arm']]
            Rn, An = DV.e215_runs(r['arm'], 'number')
            Rs, As = DV.e215_runs(r['arm'], 'string')
            e15[r['arm']]['kept_runs'] = len(Rn)
            e15[r['arm']]['set_aside'] = An
            e15[r['arm']]['string_and_number_readings_keep_the_same_runs'] = ([(x['pid'], x['n']) for x in Rn] == [(x['pid'], x['n']) for x in Rs])
        s['e215'] = e15
        s['gate'] = self.gate(scores_dir)
        s['census_path_check'] = {'rule': "v3.1's: the census entries of gemmLnc and rgm211's loops stand (no committed counted run of those loops)",
                                  'found': [x for x in git('grep', '-l', '-e', 'steady_pcs_executed', '--', 'tools', 'docs').splitlines()]}
        # the eta pin's flag and term, REPORTED
        s['rowimb_flag_points'] = int(sum(FV.rowimb_flag(p) for p in self.P))
        s['rowimb_term_positive_points'] = int(sum(FV.rowimb_term_positive(p) for p in self.P))
        self.dec['steps']['step0'] = s
        self.save()
        self.log(f"{now()} step 0: {len(self.P)} time points, {len(self.EP)} energy points ({s['energy_usable']} priced), E215 arms "
                 f"{s['e215_arms']}, frozen files {len(chk)} equal, vendored inputs {nfile} equal, gate {s['gate'].get('verdict')}")

    def gate(self, scores_dir):
        """the gate (section 4): E215's blind scores (arm A, arm B, pooled) committed on GitHub main"""
        g = {'rule': DECL['data']['gate'], 'scores_dir': scores_dir}
        if not scores_dir:
            g['verdict'] = 'NO E215 (rehearsal)' if not DV.e215_available() else 'NOT CHECKED'
            return g
        files = {}
        for dp, _, fns in os.walk(os.path.join(REPO, scores_dir)):
            for fn in fns:
                if fn.startswith('scores-e215') and fn.endswith('.json'):
                    p = os.path.join(dp, fn)
                    files[os.path.relpath(p, REPO)] = {'sha256': sha(p), 'commit': git('log', '-1', '--format=%H %cd', '--date=iso', '--', os.path.relpath(p, REPO))}
        g['files'] = files
        g['verdict'] = 'OPEN' if files else 'CLOSED'
        return g

    # ---------------------------------------------------------------- step 1: time
    def step1(self):
        t0 = time.time()
        self.log(f'{now()} step 1: time {FORM} on every fold')
        self.TR = F.run_time(FORM, 'all', self.fits, P=self.P, en=self.en, log=self.log, tag=self.tag)
        pins = {fn: sorted(fd['fit']['pins']) for fn, fd in self.TR['folds'].items()}
        eta = {fn: ('eta' in fd['fit']['pins']) for fn, fd in self.TR['folds'].items()}
        N = len(self.P)
        flags = {}
        for fn, fd in self.TR['folds'].items():
            m = np.zeros(N, bool)
            m[np.array(fd['test_idx'])] = True
            tr = [i for i in range(N) if not m[i] and not self.rung[i]]
            flags[fn] = {'flag': int(sum(FV.rowimb_flag(self.P[i]) for i in tr)), 'term_positive': int(sum(FV.rowimb_term_positive(self.P[i]) for i in tr))}
        self.dec['steps']['step1'] = {'when': now(), 'form': FORM, 'n_folds': len(self.TR['folds']), 'pins_by_fold': pins,
                                      'eta_pinned_by_fold': eta, 'rowimb_training_points_by_fold_REPORTED': flags,
                                      'all_data_pins': sorted(self.TR['fit_all']['pins']), 'secs': round(time.time() - t0, 1)}
        self.save()
        self.log(f"{now()} step 1 done: {len(self.TR['folds'])} folds; eta pinned in {[k for k, v in eta.items() if v]}")

    # ---------------------------------------------------------------- step 2: the layout term
    def step2(self):
        st = self.dec['steps'].get('step2') or {}
        TR = self.TR
        form, _ = F.parse_form_name(FORM)
        store = LY.FeatureStore(os.path.join(self.out, 'layout', 'features-v32.json'))
        feats, sub, src = LY.data_features(self.P, store, log=self.log)
        chk, EL = LY.f1_check(self.P, sub, feats, os.path.join(self.out, 'layout', 'lay-contention-records-v32.json'), log=self.log)
        feats = LY.apply_f1_fallback(self.P, sub, feats, chk)
        _, tw = self.loeo_twins(TR)
        names = [f'LOEO {e}' for e in FV.LOEO_EXPS if f'LOEO {e}' in TR['folds']] + ['LOLO compact', 'LOLO spread', 'LOLO other'] + \
                [f'LOCO {c}' for c in FV.CARDS]
        z = {'T': self.Tm, 'sub': sub, 'twin': tw, 'rung': self.rung, 'card': np.array([p['card'] for p in self.P]),
             'lolo': np.array([F.lolo_class(p['mask']) or '' for p in self.P]), 'base_all': np.array(TR['pred_all']),
             'fold_names': np.array(names), 'arm': np.array([p['arm'] for p in self.P])}
        for f in LY.FEATURES:
            v = feats[f].copy()
            assert np.all(np.isfinite(v)), f
            z['feat_' + f] = v
        bases = {}
        for nm in names:
            b = self.en.predict(TR['folds'][nm]['theta'], form)
            te = np.array(TR['folds'][nm]['test_idx'])
            assert np.max(np.abs(b[te] / np.array(TR['folds'][nm]['pred_test']) - 1)) < 1e-12, nm
            z['base_' + nm] = b
            z['test_' + nm] = te
            bases[nm] = b
        bpath = os.path.join(self.out, 'layout', 'bundle-v32.npz')
        np.savez(bpath, **z)
        rpath = os.path.join(self.out, 'layout', 'layout-rule-v32.json')
        t0 = time.time()
        r = subprocess.run([sys.executable, '-I', '-B', os.path.join(HERE, 'layout_rule_v32.py'), 'decide', bpath, rpath],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-3000:]
        res = json.load(open(rpath))
        enters = res['enters']
        cols = {'none': [], 'N3': ['N3'], 'N1+N2': ['N1', 'N2'], 'G1': ['G1'], 'G1+N1': ['G1', 'N1'], 'F1': ['fresh32'], 'fresh24': ['fresh24']}
        L = {'enters': enters, 'cols': cols[enters]}
        if enters != 'none':
            # the chosen term's constants and factor in every time fold (two-stage on each fold's base) and all-data
            M = LY.matrix(feats, cols[enters])
            fac = {}
            consts = {}
            N = len(self.P)
            for fn, fd in TR['folds'].items():
                b = self.en.predict(fd['theta'], form)
                m = np.zeros(N, bool)
                m[np.array(fd['test_idx'])] = True
                trs = np.where((~m) & (~self.rung) & sub)[0]
                a = LY.fold_consts(b, self.Tm, M, trs)
                consts[fn] = [float(x) for x in a]
                fac[fn] = LY.factor(M, a, sub)
            a_all = res['candidates'][enters]['a_all']
            fac['all'] = LY.factor(M, a_all, sub)
            consts['all'] = a_all
            for nm in names:
                if nm in res['candidates'][enters]['LOCO_consts']:
                    assert np.allclose(consts[nm], res['candidates'][enters]['LOCO_consts'][nm], rtol=1e-9, atol=1e-12), nm
            L.update({'consts_by_fold': consts, 'factor_time': fac, 'a_all': a_all})
            ident = bool(np.max(np.abs(fac['all'][sub] - 1.0)) <= 0.01)
            L['not_identified_within_1pct'] = ident
        self.layout = L
        st.update({'when': now(), 'features_sources': dict(src), 'n_subset_points': int(sub.sum()), 'f1_check': {k: v for k, v in chk.items() if k != 'configs'},
                   'f1_check_configs_sha256': hashlib.sha256(json.dumps(chk['configs'], sort_keys=True).encode()).hexdigest(),
                   'bundle': os.path.relpath(bpath, self.out), 'bundle_sha256': sha(bpath), 'rule_output': os.path.relpath(rpath, self.out),
                   'rule_output_sha256': sha(rpath), 'rule_stdout': r.stdout.strip().splitlines()[-3:], 'rule_secs': round(time.time() - t0, 1),
                   'rule_winner': res['rule_winner'], 'enters': enters, 'placebo': res.get('placebo'),
                   'candidates_summary': {c: {k: v for k, v in x.items() if k in ('LOEO_nt', 'LOLO', 'LOCO_sub', 'a_all', 'n_LOEO_nt', 'n_LOLO')}
                                          for c, x in res['candidates'].items()},
                   'eligibility': res['eligibility'], 'fresh_signs_all_data': res.get('fresh_signs_all_data'),
                   'label': res.get('label') or res.get('label_check_REPORTED'),
                   'consts_by_fold': L.get('consts_by_fold'), 'a_all': L.get('a_all'),
                   'not_identified_within_1pct': L.get('not_identified_within_1pct')})
        self.dec['steps']['step2'] = st
        self.dec['layout_term'] = enters
        self.save()
        np.savez(os.path.join(self.out, 'layout', 'data-features-v32.npz'), sub=sub, **{'feat_' + k: v for k, v in feats.items()})
        self.feats, self.sub = feats, sub
        self.log(f"{now()} step 2 (layout): rule winner {res['rule_winner']}, enters {enters}, placebo {res.get('placebo')}")
        return enters

    # ---------------------------------------------------------------- step 3: energy
    def energy_tmult(self):
        """the layout factor of each time fold carried to the energy points (by configuration), or None"""
        L = self.layout
        if L is None or L['enters'] == 'none':
            return None
        Pidx = {}
        for j, p in enumerate(self.P):
            Pidx.setdefault(F.cfg_t(p), j)
        out = {}
        for fn, fac in L['factor_time'].items():
            v = np.ones(len(self.EP))
            for i, e in enumerate(self.EP):
                j = Pidx.get(F.cfg_t(e))
                if j is not None:
                    v[i] = fac[j]
            out[fn] = v
        return out

    def step3(self):
        t0 = time.time()
        tm = self.energy_tmult()
        self.log(f'{now()} step 3: energy {EFORM} and E1u on every fold of {FORM}')
        os.makedirs(os.path.join(self.fits, 'v32'), exist_ok=True)
        os.makedirs(os.path.join(self.fits, 'v3refit'), exist_ok=True)
        ER = FV.run_energy(self.TR, [EFORM], os.path.join(self.fits, 'v32'), EP=self.EP, X=self.X, en=self.enE, which='all', log=self.log,
                           tag=self.tag, tmult=tm)
        ERu = FV.run_energy(self.TR, ['E1u'], os.path.join(self.fits, 'v3refit'), EP=self.EP, X=self.X, en=self.enE, which='all',
                            log=self.log, tag=self.tag, tmult=None)
        ERl = FV.run_energy(self.TR, ['ledger'], os.path.join(self.fits, 'v3refit'), EP=self.EP, X=self.X, en=self.enE, which='loeo,loko',
                            log=self.log, tag=self.tag, tmult=None)
        f3 = {fn: {'pins': fd['fit'].get('f3_pins'), 'c1': fd['theta'].get('c1'), 'c2': fd['theta'].get('c2')}
              for fn, fd in ER['forms'][EFORM]['folds'].items()}
        f3['all'] = {'pins': ER['forms'][EFORM]['fit_all'].get('f3_pins'), 'c1': ER['forms'][EFORM]['theta_all'].get('c1'),
                     'c2': ER['forms'][EFORM]['theta_all'].get('c2')}
        self.dec['steps']['step3'] = {'when': now(), 'secs': round(time.time() - t0, 1), 'F3_by_fold': f3,
                                      'layout_factor_on_forecast_t': tm is not None}
        self.save()
        self.ER, self.ERu, self.ERl = ER, ERu, ERl
        self.log(f"{now()} step 3 done: F3 all-data c1 {f3['all']['c1']} c2 {f3['all']['c2']} ({f3['all']['pins'].get('why')})")

    # ---------------------------------------------------------------- energy helpers
    def e_loeo(self, ER, ef):
        """per energy point: the 20 LOEO folds' and E210's W given t, W with t forecast, T forecast, and the twin flag (kind included)"""
        N = len(self.EP)
        g, f_, tf = np.full(N, np.nan), np.full(N, np.nan), np.full(N, np.nan)
        tw = np.zeros(N, bool)
        use = self.X.usable3
        for name, fd in ER['forms'][ef]['folds'].items():
            if not (name.startswith('LOEO ') and (name[5:] in FV.LOEO_EXPS or name == 'LOEO E210')):
                continue
            te = np.array(fd['test_idx'])
            g[te], f_[te], tf[te] = fd['W_given_t'], fd['W_forecast_t'], fd['T_forecast']
            m = np.zeros(N, bool)
            m[te] = True
            trc = {F.cfg_e(self.EP[i]) for i in range(N) if not m[i] and use[i] and not self.erung[i]}
            for i in te:
                tw[i] = F.cfg_e(self.EP[i]) in trc
        return g, f_, tf, tw

    def e_fold(self, ER, ef, prefix, key='W_given_t'):
        N = len(self.EP)
        g = np.full(N, np.nan)
        for name, fd in ER['forms'][ef]['folds'].items():
            if name.startswith(prefix):
                g[np.array(fd['test_idx'])] = fd[key]
        return g

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

    # ---------------------------------------------------------------- step 4: acceptance
    def step4(self):
        TR = self.TR
        ER, ERu = self.ER, self.ERu
        acc = {}
        N = len(self.P)
        allp = np.ones(N, bool)
        pb, tw = self.loeo_twins(TR)
        p32 = pb * self.loeo_factor()
        enters = self.layout['enters']
        g32, f32, tf32, etw = self.e_loeo(ER, EFORM)
        gv3, fv3, tfv3, _ = self.e_loeo(ERu, 'E1u')
        W = self.X.w
        both = self.X.usable3 & ~np.isnan(g32) & ~np.isnan(gv3) & (W >= LOW)
        e32 = rms([g32[i] / W[i] - 1 for i in range(len(self.EP)) if both[i] and not etw[i]])
        ev3 = rms([gv3[i] / W[i] - 1 for i in range(len(self.EP)) if both[i] and not etw[i]])
        w32 = rms(self.err(p32, ~tw))
        wv3 = rms(self.err(pb, ~tw))
        if enters == 'none':
            tpass = True
            tread = 'EQUAL BY CONSTRUCTION (the layout rule chose none: MM1-v3.2 time = MM1-v3 refitted time): PASS'
        else:
            tpass = bool(w32 < wv3)
            tread = 'lower' if tpass else 'not lower'
        acc['1'] = {'LOEO wall no twin': {'v32': w32, 'v3_refitted': wv3, 'n': int(((~tw) & ~np.isnan(pb)).sum()), 'reading': tread},
                    'LOEO W given t no twin (>= 3 W, both price)': {'v32': e32, 'v3_refitted': ev3, 'n': int((both & ~etw).sum())},
                    'with_twins_beside': {'wall': {'v32': rms(self.err(p32, allp)), 'v3_refitted': rms(self.err(pb, allp))},
                                          'W': {'v32': rms([g32[i] / W[i] - 1 for i in range(len(self.EP)) if both[i]]),
                                                'v3_refitted': rms([gv3[i] / W[i] - 1 for i in range(len(self.EP)) if both[i]])}},
                    'pass': bool(tpass and e32 < ev3)}
        # rule 2: LOCO (the fallback route decides; the anchor route beside)
        l32 = rms(self.err(self.fam_pred(TR, 'LOCO ', layout=True), allp))
        lv3 = rms(self.err(self.fam_pred(TR, 'LOCO '), allp))
        lc32 = self.loco_energy(ER, EFORM)
        lcv3 = self.loco_energy(ERu, 'E1u')
        ea, eb = lc32['fallback']['pooled_every_point']['rms_pct'], lcv3['fallback']['pooled_every_point']['rms_pct']
        acc['2'] = {'LOCO wall (every point)': {'v32': l32, 'v3_refitted': lv3},
                    'LOCO W given t (fallback route, every point both price, >= 3 W)': {'v32': ea, 'v3_refitted': eb},
                    'fallback_without_anchor_points_REPORTED': {'v32': lc32['fallback']['pooled_no_anchor_points'],
                                                                'v3_refitted': lcv3['fallback']['pooled_no_anchor_points']},
                    'anchor_route_REPORTED': {'v32': lc32['anchor']['pooled_no_anchor_points'], 'v3_refitted': lcv3['anchor']['pooled_no_anchor_points']},
                    'v32_routes': lc32, 'v3_refitted_routes': lcv3,
                    'pass': bool(l32 <= lv3 + 0.30 and ea <= eb + 0.30),
                    'pass_on_the_no_anchor_reading_REPORTED': bool(l32 <= lv3 + 0.30 and lc32['fallback']['pooled_no_anchor_points']['rms_pct']
                                                                   <= lcv3['fallback']['pooled_no_anchor_points']['rms_pct'] + 0.30)}
        # rule 3: leave rgm211 out
        fk = TR['folds'].get('LEAVE rgm211 out')
        form, _ = F.parse_form_name(FORM)
        rg = np.array([p['kernel'] == 'rgm211' for p in self.P])
        lw = rms(self.err(self.fam_pred(TR, 'LEAVE rgm211', layout=True), rg))
        wp = self.w_pairs(self.en.predict(fk['theta'], form) * self.tfactor('LEAVE rgm211 out'))
        acc['3'] = {'leave rgm211 out wall rms': lw, 'n': int(rg.sum()), 'E211 W pairs': wp,
                    'v3_refitted_beside': {'wall': rms(self.err(self.fam_pred(TR, 'LEAVE rgm211'), rg)),
                                           'pairs': self.w_pairs(self.en.predict(fk['theta'], form))},
                    'pass': bool(lw <= 8.0 and wp['inside_0.05'] >= 7)}
        acc['4a'] = self.rule4a(TR, ER)
        acc['4b'] = self.rule4b(TR, ER)
        acc['4c'] = self.rule4c(TR, ER)
        acc['4d'] = self.rule4d(TR, ER)
        # rule 5: the gemmLnc points
        lnc = self.X.lnc & both
        e5 = rms([g32[i] / W[i] - 1 for i in range(len(self.EP)) if lnc[i] and not etw[i]])
        e5u = rms([gv3[i] / W[i] - 1 for i in range(len(self.EP)) if lnc[i] and not etw[i]])
        acc['5'] = {'LOEO W given t over gemmLnc points (no twin, >= 3 W)': {'v32': e5, 'v3_refitted': e5u,
                                                                             'n': int((lnc & ~etw).sum()),
                                                                             'ids': [self.EP[i]['id'] for i in range(len(self.EP)) if lnc[i] and not etw[i]],
                                                                             'per_point': {self.EP[i]['id']: {'v32': g32[i] / W[i] - 1, 'v3_refitted': gv3[i] / W[i] - 1}
                                                                                           for i in range(len(self.EP)) if lnc[i]}},
                    'pass': bool(e5 is not None and e5u is not None and e5 <= 0.5 * e5u and e5 <= 15.0)}
        acc['accepted'] = all(acc[k]['pass'] for k in ('1', '2', '3', '4a', '4b', '4c', '4d', '5') if isinstance(acc[k], dict) and 'pass' in acc[k])
        acc['failed_rules'] = [k for k in ('1', '2', '3', '4a', '4b', '4c', '4d', '5') if isinstance(acc[k], dict) and not acc[k].get('pass')]
        self.dec['steps']['step4'] = {'when': now(), 'acceptance': acc}
        self.save()
        self.log(f'{now()} step 4: acceptance ' + json.dumps({k: (v.get('pass') if isinstance(v, dict) else v) for k, v in acc.items()}))
        return acc

    def loeo_factor(self):
        N = len(self.P)
        v = np.ones(N)
        if self.layout['enters'] == 'none':
            return v
        for name, fd in self.TR['folds'].items():
            if name.startswith('LOEO ') and name[5:] in FV.LOEO_EXPS:
                te = np.array(fd['test_idx'])
                v[te] = self.tfactor(name)[te]
        return v

    def loco_energy(self, ER, ef):
        N = len(self.EP)
        out = {}
        for route in ('fallback', 'anchor'):
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
                per[card] = {'kc_anchor': fd['anchor'].get('kc'), 'valid': fd['anchor'].get('valid'),
                             'route_if_anchor_decided_REPORTED': fd.get('anchor_route_used_REPORTED'),
                             'share_kc_term': fd['anchor'].get('share_kc_term'), 'anchor_points': fd['anchor'].get('anchor_points'),
                             'kc_fallback': (fd['theta'].get('kc|' + card, 1.0) if card != EV.CARDS[0] else 1.0)}
            sel = self.X.usable3 & ~np.isnan(g) & (self.X.w >= LOW)
            out[route] = {'pooled_every_point': stat([g[i] / self.X.w[i] - 1 for i in range(N) if sel[i]]),
                          'pooled_no_anchor_points': stat([g[i] / self.X.w[i] - 1 for i in range(N) if sel[i] and not excl[i]]),
                          'per_card': {c: stat([g[i] / self.X.w[i] - 1 for i in range(N) if sel[i] and self.EP[i]['card'] == c]) for c in EV.CARDS},
                          'folds': per}
        return out

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

    def rule4a(self, TR, ER):
        fd = TR['folds']['LOEO E212']
        te = np.array(fd['test_idx'])
        N = len(self.P)
        m = np.zeros(N, bool)
        m[te] = True
        trc = {F.cfg_t(self.P[i]) for i in range(N) if not m[i] and not self.rung[i]}
        efd = ER['forms'][EFORM]['folds'].get('LOEO E212')
        eidx = {self.EP[i]['id']: (k, i) for k, i in enumerate(efd['test_idx'])} if efd else {}
        fac = self.tfactor('LOEO E212')
        path = os.path.join(self.out, 'v32-e212-fold.csv')
        with open(path, 'w', newline='') as fh:
            w = csv.writer(fh, lineterminator='\n')
            w.writerow(['id', 'meas_cyc_wall', 'e_wall', 'meas_w', 'e_w_given_t', 'is_twin'])
            for k, i in enumerate(te):
                p = self.P[i]
                row = [p['id'], repr(p['cw']), repr(fd['pred_test'][k] * fac[i] / self.Tm[i] - 1)]
                ew = eidx.get(p['id'])
                if ew is not None:
                    kk, ii = ew
                    mw = self.X.w[ii]
                    row += [repr(mw), repr(efd['W_given_t'][kk] / mw - 1) if mw >= LOW else '']
                else:
                    row += ['', '']
                row.append('1' if F.cfg_t(p) in trc else '0')
                w.writerow(row)
        outj = os.path.join(self.out, 'rule4a_v32.json')
        r = subprocess.run([sys.executable, '-I', '-B', os.path.join(V31, 'comparator_4a_v31.py'), '--score', path, '--repo', REPO, '--out', outj],
                           capture_output=True, text=True)
        res = json.load(open(outj))['score'] if os.path.exists(outj) else {'error': r.stderr[-2000:]}
        res['comparator_rc'] = r.returncode
        res['pass'] = res.get('rule_4a') == 'PASS'
        res['csv_sha256'] = sha(path)
        return res

    def rule4b(self, TR, ER):
        """the E213 fold (both arms) against MM1-v3's blind error on the same E213 points (scores-e213's committed cells)"""
        res = {'arms': {}}
        fd = TR['folds'].get('LOEO E213')
        efd = ER['forms'][EFORM]['folds'].get('LOEO E213')
        fac = self.tfactor('LOEO E213')
        tpred = {self.P[i]['id']: fd['pred_test'][k] * fac[i] for k, i in enumerate(fd['test_idx'])}
        epred = {self.EP[i]['id']: (efd['W_given_t'][k], i) for k, i in enumerate(efd['test_idx'])} if efd else {}
        paths = {'A': os.path.join(REPO, 'docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/scores-e213-A.json'),
                 'B': os.path.join(REPO, 'docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/scores-e213-B.json')}
        reg = {(r['arm'], r['id']): r for r in DV.DV.e213_registry()}
        t32, tv3, w32, wv3 = [], [], [], []
        for arm, pth in paths.items():
            A = json.load(open(pth))['arms'].get(arm) or {}
            cells = A.get('cells') or {}
            ck = 'a3' if arm == 'A' else 'c1'
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
                r = reg.get((arm, c['point']))
                if r is None or r['role'] != 'point':
                    continue
                eid = f"E213|{ck}|{c['point']}"
                if eid not in epred:
                    continue
                Wg, i = epred[eid]
                wa.append(Wg / self.X.w[i] - 1)
                wb.append(c['err'])
            res['arms'][arm] = {'source': os.path.relpath(pth, REPO), 'sha256': sha(pth), 'wall_cases': {'v32': stat(ta), 'v3_blind': stat(tb)},
                                'W_given_t_points': {'v32': stat(wa), 'v3_blind': stat(wb)}}
            t32 += ta
            tv3 += tb
            w32 += wa
            wv3 += wb
        res['pooled'] = {'wall_cases': {'v32': stat(t32), 'v3_blind': stat(tv3)}, 'W_given_t_points': {'v32': stat(w32), 'v3_blind': stat(wv3)}}
        res['pass'] = bool(t32 and w32 and rms(t32) < rms(tv3) and rms(w32) < rms(wv3))
        res['note'] = "v3.1's rule 4(b) unchanged: the E213 fold against MM1-v3's blind E213 error (scores-e213's cells T1 per case, E1 per point at 3 W and above); references excluded"
        return res

    # ---------------------------------------------------------------- MM1-v3.1's frozen predictor at MM1-v3.2's points (rules 4c, 4d)
    def v31_model(self):
        if getattr(self, '_m31', None) is None:
            import mm1_v31
            self._m31 = mm1_v31.Model(json.load(open(os.path.join(V31, 'out/mm1_v31_params.json'))))
        return self._m31

    def v31_at(self, tidx, eidx):
        """MM1-v3.1's op time (us) at time points tidx and W over idle given the measured op time at energy points eidx, each called with
        the inputs that point's fold prediction is given (card, arm, format, kind, mask, its mean clock, volts and die as the reader gives)"""
        M = self.v31_model()
        T = {}
        specs = [{'card': self.P[i]['card'], 'arm': self.P[i]['arm'], 'fmt': self.P[i]['fmt'], 'kind': 'random', 'mask': self.P[i]['mask'],
                  'f': float(self.P[i]['f']), 'kernel': self.P[i]['kernel']} for i in tidx]
        for i, o in zip(tidx, M.predict_many(specs) if specs else []):
            T[i] = o['T_op_us']
        Wg = {}
        for i in eidx:
            e = self.EP[i]
            o = M.predict_many([{'card': e['card'], 'arm': e['arm'], 'fmt': e['fmt'], 'kind': e['kind'], 'mask': e['mask'], 'f': float(e['f']),
                                 'kernel': e['kernel'], 'V': e.get('V'), 'G': e.get('G'), 't0_c': e.get('die_start'),
                                 'minions': e.get('minions')}])[0]
            if isinstance(o.get('W_affine'), dict):
                Wg[i] = o['W_affine']['A_W'] + o['W_affine']['B_W_us'] / self.X.t[i]
        return T, Wg

    def newest_fold(self, TR, ER, exp, exclude_roles=(), time_families=None):
        """time_families: a time case enters only when one of its points is of these families (E215: P, C, R, L; family S shares its
        case with its reference and is scored in energy only, E215's form)"""
        fd = TR['folds'][f'LOEO {exp}']
        efd = ER['forms'][EFORM]['folds'][f'LOEO {exp}']
        fac = self.tfactor(f'LOEO {exp}')
        N, NE = len(self.P), len(self.EP)
        m = np.zeros(N, bool)
        m[np.array(fd['test_idx'])] = True
        trc = {F.cfg_t(self.P[i]) for i in range(N) if not m[i] and not self.rung[i]}
        me = np.zeros(NE, bool)
        me[np.array(efd['test_idx'])] = True
        trce = {F.cfg_e(self.EP[i]) for i in range(NE) if not me[i] and self.X.usable3[i] and not self.erung[i]}
        tidx = [i for i in fd['test_idx'] if self.P[i].get('role') not in exclude_roles
                and (time_families is None or set(str(self.P[i].get('family', '')).split('+')) & set(time_families))]
        tp = {i: fd['pred_test'][k] * fac[i] for k, i in enumerate(fd['test_idx'])}
        eidx = [i for k, i in enumerate(efd['test_idx']) if self.EP[i].get('role') not in exclude_roles and self.X.w[i] >= LOW]
        ep = {i: efd['W_given_t'][k] for k, i in enumerate(efd['test_idx'])}
        T31, W31 = self.v31_at(tidx, eidx)
        rows_t = [{'id': self.P[i]['id'], 'v32': tp[i] / self.Tm[i] - 1, 'v31': T31[i] / self.Tm[i] - 1,
                   'twin': F.cfg_t(self.P[i]) in trc} for i in tidx]
        rows_e = [{'id': self.EP[i]['id'], 'v32': ep[i] / self.X.w[i] - 1, 'v31': W31[i] / self.X.w[i] - 1,
                   'twin': F.cfg_e(self.EP[i]) in trce} for i in eidx if i in W31]
        out = {'time_cases': {'v32': stat([r['v32'] for r in rows_t]), 'v31': stat([r['v31'] for r in rows_t])},
               'W_given_t_points': {'v32': stat([r['v32'] for r in rows_e]), 'v31': stat([r['v31'] for r in rows_e])},
               'no_twins_REPORTED': {'time_cases': {'v32': stat([r['v32'] for r in rows_t if not r['twin']]),
                                                    'v31': stat([r['v31'] for r in rows_t if not r['twin']])},
                                     'W_given_t_points': {'v32': stat([r['v32'] for r in rows_e if not r['twin']]),
                                                          'v31': stat([r['v31'] for r in rows_e if not r['twin']])}},
               'n_energy_points_v31_prices': len(rows_e), 'n_energy_points_v32_prices': len(eidx)}
        out['pass'] = bool(rows_t and rows_e and out['time_cases']['v32']['rms_pct'] < out['time_cases']['v31']['rms_pct']
                           and out['W_given_t_points']['v32']['rms_pct'] < out['W_given_t_points']['v31']['rms_pct'])
        path = os.path.join(self.out, f'rule4-{exp.lower()}-rows.json')
        json.dump({'time': rows_t, 'energy': rows_e}, open(path, 'w'), indent=0)
        out['rows_file'] = os.path.relpath(path, self.out)
        return out, rows_t, rows_e

    def rule4c(self, TR, ER):
        if 'LOEO E214' not in TR['folds']:
            return {'pass': False, 'note': 'no E214 fold'}
        out, rows_t, rows_e = self.newest_fold(TR, ER, 'E214')
        # the check of the call: unread-e214's committed per-case MM1-v3.1 errors beside (REPORTED)
        p = os.path.join(V31, 'unread-e214', 'scores-unread-e214-cases.csv')
        out['unread_e214_cases_csv_sha256'] = sha(p)
        try:
            rows = list(csv.DictReader(open(p)))
            out['unread_e214_cases_n'] = len(rows)
            byc = {r['case']: r for r in rows}
            pid = {p_['id']: p_ for p_ in self.P}
            d = []
            for r in rows_t:
                q = pid[r['id']]
                u = byc.get(f"{q['card']}|{q['arm']}|{q['fmt']}|{q['kind']}|{q['mask']}")
                if u and u.get('v31_e_wall') not in (None, ''):
                    d.append(r['v31'] - float(u['v31_e_wall']))
            out['check_of_the_call_REPORTED'] = {
                'what': ("MM1-v3.1's wall error here (one call a case at the case's mean clock) minus unread-e214's committed v31_e_wall (the mean "
                         "of its runs' errors, each at its run's clock): the two methods differ only where a case's runs differ in clock"),
                'n_matched': len(d), 'rms_diff_pct_points': (float(np.sqrt(np.mean(np.square(d)))) * 100 if d else None),
                'max_abs_diff_pct_points': (float(np.max(np.abs(d))) * 100 if d else None)}
        except Exception as ex:  # noqa: BLE001
            out['unread_e214_cases_read_error'] = str(ex)
        out['note'] = ("the E214 fold against MM1-v3.1's UNREAD error by its frozen predictor called at each of MM1-v3.2's E214 points with the "
                       "inputs that point's fold prediction is given; twins included (as MM1-v3's rule 4), without twins REPORTED")
        return out

    def rule4d(self, TR, ER):
        if 'LOEO E215' not in TR['folds']:
            return {'pass': False, 'note': 'no E215 fold (E215 not in the data)'}
        out, rows_t, rows_e = self.newest_fold(TR, ER, 'E215', exclude_roles=('reference', 'tie'), time_families=('P', 'C', 'R', 'L'))
        out['note'] = ("the E215 fold (both arms, every registered and post hoc point; references and ties excluded) against MM1-v3.1's BLIND "
                       "error by the same call at MM1-v3.2's E215 points; E215's registered scorer figures REPORTED beside (summary)")
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--scores-e215', default='')
    ap.add_argument('--until', default='4')
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    logf = open(os.path.join(out, 'run.log'), 'a')

    def log(s):
        print(s, flush=True)
        logf.write(s + '\n')
        logf.flush()
    log(f'{now()} run_v32 start, tag {a.tag}, python {sys.version.split()[0]}, numpy {np.__version__}')
    R = Run(out, a.tag, log)
    R.step0(a.scores_e215)
    if a.until == '0':
        return
    R.step1()
    if a.until == '1':
        return
    R.step2()
    if a.until == '2':
        return
    R.step3()
    if a.until == '3':
        return
    R.step4()
    log(f"{now()} run_v32 end: layout term {R.layout['enters']}, energy {EFORM}")


if __name__ == '__main__':
    main()
