#!/usr/bin/env python3
"""controls-e216 (round Q229): verify-lay's REPORTED layout controls for every E216 point, made by the same function that made
verify-lay's v02_e215_controls.csv (posted #1.29.1.1, committed 595fcb59 in tools/matmul/mm1/v3.2-terms/layout/controls-e215/).

The controls are never a registered rule of E216: they are REPORTED forecasts, made before any E216 datum.

What is "the same function" (copied, not rewritten):
  - the features of one configuration: v01_map.py's own functions (the committed copy in ../controls-e215/, IMPORTED, not copied):
    my_steps (the request generator, from rgm136's run_gemm_large), lru_fresh (the OrderedDict strict-LRU L3 over 1 KiB tiles, two passes,
    the second counted) at the capacities 16, 24, 32, 48, 64 MB, groups and mesh (the hop mean from the mesh map), assembled exactly as
    v01_map.main assembles a record (its 'loads' diagnostics are not made: no control reads them);
  - feat_row and the control formula: v02_fits.py's own lines (its E215 block), copied verbatim below;
      x = the features (zero at the full mask), control = T_v31 x (1 + sum a_i x_i), no clip, printed '%.4f';
  - the constants: verify-lay's all-data two-stage constants as its v02_fits.json holds them (nothing refitted here).

Subcommands (each prints what it did; outputs under $CONTROLS_WORK, default ./work next to this file):
  constants <v02_fits.json>   extract the five forms' features and constants (exact float reprs) -> constants-verify-lay.json
  e215 committed|remade       E215's 94 rows from the committed v01_map.json, or from features re-made here (features-e215.json)
                              -> e215-<which>.csv, to compare byte for byte with ../controls-e215/v02_e215_controls.csv
  features e215|e216          the feature records of E215's or E216's subset configurations and their full-chip references, by
                              v01_map.py's functions; for E216 also the masked walk's own numbers (walk_v31.summary at 32 and 24 MB) and
                              the E216 registration's frozen walk features, as cross-checks -> features-<which>.json
  e216                        E216's 46 points x the three frozen clocks (799.0, 700, 600 MHz) -> controls-e216.csv, controls-e216.json,
                              with F1's own column checked against E216's frozen 'v3.1+contention' forecasts

Paths: the lab from this file's place (six folders up) or $ET_LAB; E216's registration from $E216_REG (default the lab's
tools/claims-v3/e216); constants from $CONTROLS_CONSTANTS (default constants-verify-lay.json next to this file).
/usr/bin/python3 3.12.3 with numpy 1.26.4, run as -I -B, single-threaded (OMP_NUM_THREADS=1 and the like). Reads no E216 datum: E216's
registration files only (points-e216.csv, forecast-e216.json, desk/candidates-e216.json, terms/layout/out/features_layout.json)."""
import csv
import hashlib
import importlib.util
import json
import math
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.environ.get('ET_LAB') or os.path.abspath(os.path.join(HERE, *['..'] * 6))
LAYOUT = os.path.join(LAB, 'tools/matmul/mm1/v3.2-terms/layout')
C215 = os.path.join(LAYOUT, 'controls-e215')
REG = os.environ.get('E216_REG') or os.path.join(LAB, 'tools/claims-v3/e216')
WORK = os.environ.get('CONTROLS_WORK') or os.path.join(HERE, 'work')
CONSTS = os.environ.get('CONTROLS_CONSTANTS') or os.path.join(HERE, 'constants-verify-lay.json')
FULL = 0xFFFFFFFF
SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
CTRL_FORMS = ['N3', 'N1+N2', 'G1', 'G1+N1', 'fresh24']          # v02_fits.py's ctrl_forms, in its order
FORM_FEATURES = {'N3': ['N3'], 'N1+N2': ['N1', 'N2'], 'G1': ['G1'], 'G1+N1': ['G1', 'N1'], 'fresh24': ['fresh24']}
COLS = ['fresh32', 'fresh16', 'fresh24', 'fresh48', 'fresh64', 'distinct', 'G1', 'F3', 'N1', 'N2', 'N3', 'N4', 'Rf', 'Cf',
        'link', 'fan']                                         # v02_fits.py's cols (feat_row returns zeros for all at the full mask)
E216_CLOCKS = ['799.0', '700.0', '600.0']                      # route c's registered column first, then route m's two
A_FRESH_F1_FROZEN = -0.08316593007433395                       # the frozen F1 constant (forecast-e215-v31-layout.json meta, post #1.29.1)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------------------------------------ v02_fits.py's lines, verbatim
def key_of(arm, mask):
    MB, NB, KB = (int(x) for x in SHAPE.match(arm).groups())
    return 'rgm136.gemmL|%dx%dx%d|0x%x' % (MB, NB, KB, mask)


def feat_row(arm_token, m, V1):
    if m == FULL:
        return {c: 0.0 for c in COLS}
    k = key_of(arm_token, m)
    kf = key_of(arm_token, FULL)
    f, g = V1[k], V1[kf]
    n = f['n']
    return {'fresh32': f['fresh_lines_step']['32'] / f['req_lines_step'] - g['fresh_lines_step']['32'] / g['req_lines_step'],
            'fresh24': f['fresh_lines_step']['24'] / f['req_lines_step'] - g['fresh_lines_step']['24'] / g['req_lines_step'],
            'G1': (110 + 12 * f['hop_mean']) / (110 + 12 * g['hop_mean']) - 1, 'N1': 1 - n / 32.0, 'N2': (1 - n / 32.0) ** 2,
            'N3': 32.0 / n - 1}


def control_value(v31, fr_, fm, CONST):
    cs = CONST['forms'][fm]['features']
    a = CONST['forms'][fm]['a_all']
    return v31 * (1.0 + sum(ai * fr_.get(c, 0.0) for ai, c in zip(a, cs)))


def control_factor(fr_, fm, CONST):
    cs = CONST['forms'][fm]['features']
    a = CONST['forms'][fm]['a_all']
    return 1.0 + sum(ai * fr_.get(c, 0.0) for ai, c in zip(a, cs))


def write_e215_csv(path, ctrl):
    with open(path, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['id', 'mask', 'arm', 'v31_cycles_per_op_wall', 'F1_frozen_cycles_per_op_wall'] + ['REPORTED_%s_cycles_per_op_wall' % fm for fm in CTRL_FORMS])
        for row in ctrl:
            w.writerow([row['id'], row['mask'], row['arm'], '%.4f' % row['v31_cycles_per_op_wall'], '%.4f' % row['F1_frozen_cycles_per_op_wall']] + ['%.4f' % row[fm] for fm in CTRL_FORMS])


# ------------------------------------------------------------------------------------------------ constants
def cmd_constants(v02_json):
    d = json.load(open(v02_json))
    e = d['e215_control_columns']
    out = {'what': "verify-lay's all-data two-stage constants of its five REPORTED control forms, as its v02_fits.json holds them "
                   "(e215_control_columns.forms); nothing refitted",
           'source': {'file': 'OUT/verify-lay/work/v02_fits.json (verify-lay, round Q225 track C)', 'sha256': sha(v02_json),
                      'made_at': e['made_at']},
           'form_order': CTRL_FORMS, 'forms': {}}
    for fm in CTRL_FORMS:
        f = e['forms'][fm]
        assert f['features'] == FORM_FEATURES[fm], (fm, f['features'])
        assert f['a_all'] == d['forms'][fm]['a_all'], fm         # the same numbers in the fit table
        out['forms'][fm] = {'features': f['features'], 'a_all': f['a_all'], 'a_all_repr': [repr(x) for x in f['a_all']],
                            'held_out_verify_lay': {k: d['forms'][fm][k] for k in ('LOLO_b', 'LOEO_nt', 'LOLO_a', 'LOCO')}}
    out['F1_reference'] = {'frozen_a_fresh': A_FRESH_F1_FROZEN, 'verify_lay_refit_a_fresh32': d['forms']['fresh32']['a_all'][0],
                           'note': "F1's column is E216's frozen 'v3.1+contention' forecast; the caller's own F1 (frozen constant, the "
                                   "features made here) is its check"}
    os.makedirs(os.path.dirname(os.path.abspath(CONSTS)), exist_ok=True)
    with open(CONSTS, 'w') as fh:
        json.dump(out, fh, indent=1)
        fh.write('\n')
    print('constants written', CONSTS, sha(CONSTS))
    for fm in CTRL_FORMS:
        print(' ', fm, out['forms'][fm]['features'], out['forms'][fm]['a_all_repr'])
    return 0


def load_consts():
    C = json.load(open(CONSTS))
    for fm in CTRL_FORMS:
        assert C['forms'][fm]['features'] == FORM_FEATURES[fm]
        assert [repr(x) for x in C['forms'][fm]['a_all']] == C['forms'][fm]['a_all_repr']
    return C


# ------------------------------------------------------------------------------------------------ features (v01_map.py's functions)
def v01_module():
    return load_module('v01_map_committed', os.path.join(C215, 'v01_map.py'))


def walk_module():
    return load_module('walk_v31_ro', os.path.join(LAB, 'tools/matmul/mm1/v3.1/walk/walk/walk_v31.py'))


def v01_record(V01, WK, shp, m):
    """one configuration's record, assembled as v01_map.main assembles it (without its 'loads' diagnostics)"""
    MB, NB, KB = shp
    seq = list(V01.my_steps(MB, NB, KB, m))
    wseq = list(WK.chip_steps('rgm136.gemmL', MB, NB, KB, m))
    same = len(seq) == len(wseq)
    if same:
        for a, b in zip(seq, wseq):
            if a[0] != b[0]:
                same = False
                break
            if a[0] == 'op':
                if [(x >> 10, w) for x, w in a[1]] != [(t, w) for t, w in b[2]] or [(x >> 10, w) for x, w in a[2]] != [(t, w) for t, w in b[3]]:
                    same = False
                    break
            else:
                if [x >> 10 for x in a[1]] != list(b[2]):
                    same = False
                    break
    del wseq
    act, rows, cols = V01.groups(m)
    n, R, C = len(act), len(rows), len(cols)
    nsteps = MB * NB * 2 * KB * V01.KT
    req_lines = 16 * 12 * n
    dis_lines = 16 * (4 * R + 8 * C)
    rec = {'n': n, 'R': R, 'C': C, 'steps': nsteps, 'req_lines_step': req_lines, 'distinct_lines_step': dis_lines,
           'generator_equals_walk': same}
    fr = {}
    for cap in V01.CAPS:
        f = V01.lru_fresh(seq, cap * 1024, nsteps)
        fr[str(cap)] = 16.0 * sum(len(a) + len(b) for a, b in f) / nsteps
    rec['fresh_lines_step'] = fr
    hm, hx = V01.mesh(m)
    rec['hop_mean'], rec['hop_max'] = hm, hx
    return rec


def e215_configs():
    need = set()
    for r in csv.DictReader(open(os.path.join(LAB, 'tools/claims-v3/e215/points-e215.csv'))):
        m = int(r['shire_mask'], 16)
        if m != FULL:
            assert r['loop'] == 'rgm136 gemmL'
            shp = tuple(int(x) for x in SHAPE.match(r['arm_token']).groups())
            need.add((shp, m))
            need.add((shp, FULL))
    return sorted(need)


def e216_points():
    return list(csv.DictReader(open(os.path.join(REG, 'points-e216.csv'))))


def e216_configs():
    need = set()
    for r in e216_points():
        m = int(r['mask'], 16)
        if m != FULL:
            assert r['loop'] == 'rgm136 gemmL' and r['kernel'] == 'rgm136' and SHAPE.match(r['arm']), (r['id'], r['loop'], r['arm'])
            shp = tuple(int(x) for x in SHAPE.match(r['arm']).groups())
            need.add((shp, m))
            need.add((shp, FULL))
    return sorted(need)


def cmd_features(which):
    t0 = time.time()
    V01 = v01_module()
    WK = walk_module()
    need = e215_configs() if which == 'e215' else e216_configs()
    print('configurations', len(need), flush=True)
    out = {'what': "feature records by v01_map.py's own functions (committed copy, imported), as v01_map.main assembles them, without "
                   "its 'loads' diagnostics", 'which': which, 'interpreter': sys.version.split()[0], 'caps_MB': V01.CAPS,
           'inputs_sha256': {'v01_map.py': sha(os.path.join(C215, 'v01_map.py')),
                             'walk_v31.py': sha(os.path.join(LAB, 'tools/matmul/mm1/v3.1/walk/walk/walk_v31.py')),
                             'nocbench/analyze.py': sha(os.path.join(LAB, 'workloads/nocbench/analyze.py'))},
           'configs': {}}
    if which == 'e216':
        frozen = {}
        frozen.update(json.load(open(os.path.join(REG, 'terms/layout/out/features_layout.json'))))
        cand = json.load(open(os.path.join(REG, 'desk/candidates-e216.json')))['walk_configs_new']
        for k, v in cand.items():
            frozen.setdefault(k, v)
        out['walk_check'] = {}
    for i, (shp, m) in enumerate(need):
        MB, NB, KB = shp
        key = 'rgm136.gemmL|%dx%dx%d|0x%x' % (MB, NB, KB, m)
        t1 = time.time()
        rec = v01_record(V01, WK, shp, m)
        out['configs'][key] = rec
        if which == 'e216':
            # the masked walk's own strict-LRU numbers at 32 and 24 MB, and the registration's frozen walk features
            s32 = WK.summary('rgm136.gemmL', MB, NB, KB, m, l3_cap_mb=32.0)
            s24 = WK.summary('rgm136.gemmL', MB, NB, KB, m, l3_cap_mb=24.0)
            fz = frozen.get(key)
            out['walk_check'][key] = {
                'walk_fresh_lines_step_32': s32['l3_strict']['chip_fresh_lines_per_step'],
                'walk_fresh_lines_step_24': s24['l3_strict']['chip_fresh_lines_per_step'], 'walk_n': s32['n'],
                'walk_lines_req_step': 16 * s32['n'] * (s32['per_shire_step']['A_reads'] + s32['per_shire_step']['B_reads']),
                'frozen_present': fz is not None,
                'frozen_fresh_lines_step_32': fz['fresh_lines_step'] if fz else None,
                'frozen_lines_req_step': fz['lines_req_step'] if fz else None, 'frozen_n': fz['n'] if fz else None,
                'frozen_mesh_hop_mean': fz['mesh_hop_mean'] if fz else None, 'frozen_mesh_hop_max': fz['mesh_hop_max'] if fz else None}
        print(f'  {i + 1}/{len(need)} {key} same={rec["generator_equals_walk"]} fresh32={rec["fresh_lines_step"]["32"]:.6f} '
              f'fresh24={rec["fresh_lines_step"]["24"]:.6f} hop_mean={rec["hop_mean"]:.6f} ({time.time() - t1:.1f} s)', flush=True)
    out['n_configs'] = len(need)
    out['generator_mismatch_configs'] = sum(0 if r['generator_equals_walk'] else 1 for r in out['configs'].values())
    os.makedirs(WORK, exist_ok=True)
    fn = os.path.join(WORK, 'features-%s.json' % which)
    with open(fn, 'w') as fh:   # no run time in the file, so that a re-run makes it byte for byte
        json.dump(out, fh, indent=0)
        fh.write('\n')
    print('done', len(need), 'configs; generator mismatches', out['generator_mismatch_configs'], '; secs', round(time.time() - t0, 1),
          '->', fn, sha(fn))
    return 0


# ------------------------------------------------------------------------------------------------ E215 (the proof)
def cmd_e215(which):
    CONST = load_consts()
    if which == 'committed':
        V1 = json.load(open(os.path.join(C215, 'work/v01_map.json')))['configs']
    else:
        V1 = json.load(open(os.path.join(WORK, 'features-e215.json')))['configs']
        # the re-made records against the committed ones, every field the re-make carries
        C1 = json.load(open(os.path.join(C215, 'work/v01_map.json')))['configs']
        bad = 0
        for k, r in V1.items():
            for fld in ('n', 'R', 'C', 'steps', 'req_lines_step', 'distinct_lines_step', 'generator_equals_walk', 'fresh_lines_step',
                        'hop_mean', 'hop_max'):
                if r[fld] != C1[k][fld]:
                    bad += 1
                    print('  DIFFERS', k, fld, r[fld], C1[k][fld])
        print('re-made feature records vs the committed v01_map.json:', len(V1), 'configurations,', bad, 'differing fields')
    lane_rows = list(csv.DictReader(open(os.path.join(LAYOUT, 'forecast-e215-v31-layout.csv'))))
    reg = {r['id']: r for r in csv.DictReader(open(os.path.join(LAB, 'tools/claims-v3/e215/points-e215.csv')))}
    ctrl = []
    for r in lane_rows:
        rg_ = reg[r['id']]
        m = int(rg_['shire_mask'], 16)
        fr_ = feat_row(rg_['arm_token'], m, V1)
        v31 = float(r['v31_cycles_per_op_wall'])
        row = {'id': r['id'], 'mask': rg_['shire_mask'], 'arm': rg_['arm_token'], 'v31_cycles_per_op_wall': v31,
               'F1_frozen_cycles_per_op_wall': float(r['v31c_cycles_per_op_wall'])}
        for fm in CTRL_FORMS:
            row[fm] = control_value(v31, fr_, fm, CONST)
        ctrl.append(row)
    os.makedirs(WORK, exist_ok=True)
    fn = os.path.join(WORK, 'e215-%s.csv' % which)
    write_e215_csv(fn, ctrl)
    ref = os.path.join(C215, 'v02_e215_controls.csv')
    same = open(fn, 'rb').read() == open(ref, 'rb').read()
    print('E215 re-made from the %s features:' % which, fn, sha(fn), '| committed', sha(ref), '| BYTE FOR BYTE' if same else '| DIFFERENT')
    # unrounded: against verify-lay's own unrounded rows (v02_fits.json > e215_control_columns > rows), when given
    vj = os.environ.get('VERIFY_LAY_V02_JSON')
    unr = None
    if vj:
        rows = {x['id']: x for x in json.load(open(vj))['e215_control_columns']['rows']}
        eq = ne = 0
        worst = 0.0
        for row in ctrl:
            for fm in CTRL_FORMS:
                a, b = row[fm], rows[row['id']][fm]
                if a == b:
                    eq += 1
                else:
                    ne += 1
                    worst = max(worst, abs(a / b - 1))
        unr = {'fields_bit_equal': eq, 'fields_not_bit_equal': ne, 'worst_rel_diff': worst}
        print('unrounded against verify-lay v02_fits.json rows:', unr)
    fields_diff = None
    if not same:
        A = list(csv.reader(open(fn, newline='')))
        B = list(csv.reader(open(ref, newline='')))
        fields_diff = sum(1 for x, y in zip(A, B) for u, v in zip(x, y) if u != v) + abs(len(A) - len(B))
        print('fields differing at the printed digits:', fields_diff)
    res = {'which': which, 'csv': fn, 'sha256': sha(fn), 'committed_sha256': sha(ref), 'byte_for_byte': same,
           'fields_differing_printed': fields_diff, 'unrounded_vs_verify_lay_rows': unr, 'rows': len(ctrl)}
    with open(os.path.join(WORK, 'e215-%s-check.json' % which), 'w') as fh:
        json.dump(res, fh, indent=1)
        fh.write('\n')
    return 0 if same else 1


# ------------------------------------------------------------------------------------------------ E216
def sig_digits(rel):
    """agreement in significant digits from a relative difference ('bit-equal' when there is none)"""
    return 'bit-equal' if rel == 0 else math.floor(-math.log10(rel))


def cmd_e216():
    CONST = load_consts()
    FE = json.load(open(os.path.join(WORK, 'features-e216.json')))
    V1 = FE['configs']
    pts = e216_points()
    assert len(pts) == 46, len(pts)
    FC = json.load(open(os.path.join(REG, 'forecast-e216.json')))
    assert abs(FC['meta']['a_fresh'] - A_FRESH_F1_FROZEN) == 0.0
    rows_csv = []
    pts_json = {}
    f1chk = {'rows': 0, 'rows_subset': 0, 'max_rel_diff_all': 0.0, 'max_rel_diff_subset': 0.0, 'printed_4dp_equal': 0,
             'printed_9g_equal': 0, 'phi_walk_vs_frozen_bit_equal': 0, 'phi_walk_vs_frozen_rows': 0, 'max_abs_phi_v01_minus_frozen': 0.0,
             'max_rel_factor_v01_vs_frozen': 0.0}
    for p in pts:
        m = int(p['mask'], 16)
        fr_ = feat_row(p['arm'], m, V1)
        fac = {fm: control_factor(fr_, fm, CONST) for fm in CTRL_FORMS}
        fac_f1_caller = 1.0 + A_FRESH_F1_FROZEN * fr_['fresh32']
        # the frozen walk feature's Phi (the layout term's own expression over the registration's walk features)
        wkey = None
        phi_w = 0.0
        if m != FULL:
            wkey = key_of(p['arm'], m)
            wc, wcf = FE['walk_check'][wkey], FE['walk_check'][key_of(p['arm'], FULL)]
            phi_w = wc['frozen_fresh_lines_step_32'] / wc['frozen_lines_req_step'] - wcf['frozen_fresh_lines_step_32'] / wcf['frozen_lines_req_step']
        pj = {'family': p['family'], 'pair': p['pair'], 'pair_role': p['pair_role'], 'regime': p['regime'], 'subfamily': p['subfamily'],
              'twin_of': p['twin_of'], 'e215_twin': p['e215_twin'], 'loop': p['loop'], 'arm': p['arm'], 'fmt': p['fmt'], 'kind': p['kind'],
              'mask': p['mask'], 'n_shires': int(p['shires']), 'features': ({c: fr_[c] for c in ('N1', 'N2', 'N3', 'G1', 'fresh24', 'fresh32')}
                                                                            if m != FULL else 'zero at the full mask'),
              'factors': fac, 'factor_F1_caller': fac_f1_caller, 'phi_fresh_walk_frozen_features': phi_w, 'walk_key': wkey, 'by_clock': {}}
        for fk in E216_CLOCKS:
            fo = FC['points'][p['id']][fk]['forecasts']
            v31 = fo['MM1-v3.1']['cycles_per_op_wall']
            f1f = fo['v3.1+contention']['cycles_per_op_wall']
            ctl = {fm: control_value(v31, fr_, fm, CONST) for fm in CTRL_FORMS}
            f1c = v31 * fac_f1_caller
            rel = abs(f1c / f1f - 1)
            f1chk['rows'] += 1
            f1chk['max_rel_diff_all'] = max(f1chk['max_rel_diff_all'], rel)
            if m != FULL:
                f1chk['rows_subset'] += 1
                f1chk['max_rel_diff_subset'] = max(f1chk['max_rel_diff_subset'], rel)
                phi_frozen = fo['v3.1+contention']['phi_fresh']
                f1chk['phi_walk_vs_frozen_rows'] += 1
                f1chk['phi_walk_vs_frozen_bit_equal'] += int(phi_w == phi_frozen)
                f1chk['max_abs_phi_v01_minus_frozen'] = max(f1chk['max_abs_phi_v01_minus_frozen'], abs(fr_['fresh32'] - phi_frozen))
                f1chk['max_rel_factor_v01_vs_frozen'] = max(f1chk['max_rel_factor_v01_vs_frozen'],
                                                            abs(fac_f1_caller / fo['v3.1+contention']['layout_factor'] - 1))
            else:
                assert fo['v3.1+contention']['layout_factor'] == 1.0 and f1f == v31
            f1chk['printed_4dp_equal'] += int('%.4f' % f1c == '%.4f' % f1f)
            f1chk['printed_9g_equal'] += int('%.9g' % f1c == '%.9g' % f1f)
            pj['by_clock'][fk] = {'v31_cycles_per_op_wall': v31, 'F1_frozen_cycles_per_op_wall': f1f, 'F1_caller_cycles_per_op_wall': f1c,
                                  'REPORTED': ctl}
            rows_csv.append([p['id'], p['family'], p['pair'], p['pair_role'], p['mask'], p['arm'], p['fmt'], fk, '%.4f' % v31, '%.4f' % f1f]
                            + ['%.4f' % ctl[fm] for fm in CTRL_FORMS])
        pts_json[p['id']] = pj
    f1chk['digits_all'] = sig_digits(f1chk['max_rel_diff_all'])
    f1chk['digits_subset'] = sig_digits(f1chk['max_rel_diff_subset'])
    # the Y pairs: each control's within-pair ln difference (a minus b), clock-free (the factors carry no clock)
    pairs = {}
    for pid in sorted({p['pair'] for p in pts if p['pair']}):
        a = [p for p in pts if p['pair'] == pid]
        assert len(a) == 2
        a.sort(key=lambda p: p['id'])
        pa, pb = pts_json[a[0]['id']], pts_json[a[1]['id']]
        pairs[pid] = {'a': a[0]['id'], 'b': a[1]['id'], 'masks': [a[0]['mask'], a[1]['mask']], 'arm': a[0]['arm'], 'role': a[0]['pair_role'],
                      'ln_a_over_b': {fm: math.log(pa['factors'][fm] / pb['factors'][fm]) for fm in CTRL_FORMS},
                      'ln_a_over_b_F1_frozen': math.log(FC['points'][a[0]['id']]['799.0']['forecasts']['v3.1+contention']['layout_factor'] /
                                                        FC['points'][a[1]['id']]['799.0']['forecasts']['v3.1+contention']['layout_factor'])}
    # the walk cross-checks of the features made here
    wchk = {'configs': 0, 'n_equal': 0, 'req_equal': 0, 'fresh32_vs_walk_max_abs': 0.0, 'fresh24_vs_walk_max_abs': 0.0,
            'frozen_present': 0, 'fresh32_vs_frozen_max_abs': 0.0, 'hop_mean_vs_frozen_equal': 0, 'hop_max_vs_frozen_equal': 0}
    for k, wc in FE['walk_check'].items():
        r = V1[k]
        wchk['configs'] += 1
        wchk['n_equal'] += int(wc['walk_n'] == r['n'])
        wchk['req_equal'] += int(wc['walk_lines_req_step'] == r['req_lines_step'])
        wchk['fresh32_vs_walk_max_abs'] = max(wchk['fresh32_vs_walk_max_abs'], abs(wc['walk_fresh_lines_step_32'] - r['fresh_lines_step']['32']))
        wchk['fresh24_vs_walk_max_abs'] = max(wchk['fresh24_vs_walk_max_abs'], abs(wc['walk_fresh_lines_step_24'] - r['fresh_lines_step']['24']))
        if wc['frozen_present']:
            wchk['frozen_present'] += 1
            wchk['fresh32_vs_frozen_max_abs'] = max(wchk['fresh32_vs_frozen_max_abs'], abs(wc['frozen_fresh_lines_step_32'] - r['fresh_lines_step']['32']))
            wchk['hop_mean_vs_frozen_equal'] += int(wc['frozen_mesh_hop_mean'] == r['hop_mean'])
            wchk['hop_max_vs_frozen_equal'] += int(wc['frozen_mesh_hop_max'] == r['hop_max'])
    sub_fac = {fm: [pts_json[i]['factors'][fm] for i in pts_json if pts_json[i]['features'] != 'zero at the full mask'] for fm in CTRL_FORMS}
    os.makedirs(WORK, exist_ok=True)
    fcsv = os.path.join(WORK, 'controls-e216.csv')
    with open(fcsv, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['id', 'family', 'pair', 'pair_role', 'mask', 'arm', 'fmt', 'f_mhz', 'v31_cycles_per_op_wall', 'F1_frozen_cycles_per_op_wall']
                   + ['REPORTED_%s_cycles_per_op_wall' % fm for fm in CTRL_FORMS])
        for r in rows_csv:
            w.writerow(r)
    meta = {'what': "verify-lay's REPORTED layout controls for E216's 46 registered points at the three frozen clocks: T = T_v31 x "
                    "(1 + sum a_i x_i), x zero at the full mask; verify-lay's constants, nothing refitted; never a registered rule",
            'label': 'REPORTED (desk forecasts made before any E216 datum; never a registered rule of E216)',
            'columns': {'v31_cycles_per_op_wall': "MM1-v3.1's frozen E216 forecast (forecast-e216.json, cycles_per_op_wall)",
                        'F1_frozen_cycles_per_op_wall': "E216's frozen 'v3.1+contention' forecast (forecast-e216.json)",
                        'REPORTED_*': "the five controls, v02_fits.py's formula, verify-lay's constants"},
            'clocks_MHz': E216_CLOCKS, 'route': "799.0 is route c's registered column; 700 and 600 the route m columns (REPORTED)",
            'constants': {fm: {'features': CONST['forms'][fm]['features'], 'a_all': CONST['forms'][fm]['a_all']} for fm in CTRL_FORMS},
            'constants_source': CONST['source'], 'constants_file_sha256': sha(CONSTS),
            'subset_factor_range': {fm: [min(v), max(v)] for fm, v in sub_fac.items()},
            'clip_0.3_3.0_would_bind': any(x < 0.3 or x > 3.0 for v in sub_fac.values() for x in v),
            'F1_check': f1chk, 'walk_cross_check': wchk, 'pairs': pairs,
            'inputs_sha256': {'points-e216.csv': sha(os.path.join(REG, 'points-e216.csv')),
                              'forecast-e216.json': sha(os.path.join(REG, 'forecast-e216.json')),
                              'desk/candidates-e216.json': sha(os.path.join(REG, 'desk/candidates-e216.json')),
                              'terms/layout/out/features_layout.json': sha(os.path.join(REG, 'terms/layout/out/features_layout.json')),
                              'features-e216.json': sha(os.path.join(WORK, 'features-e216.json')),
                              'v01_map.py (committed)': sha(os.path.join(C215, 'v01_map.py'))},
            'interpreter': sys.version.split()[0]}   # no time stamp in the file (FROZEN.txt holds the time), so a re-run is byte for byte
    fj = os.path.join(WORK, 'controls-e216.json')
    with open(fj, 'w') as fh:
        json.dump({'meta': meta, 'points': pts_json}, fh, indent=1, sort_keys=False)
        fh.write('\n')
    print('E216 controls:', len(pts), 'points x', len(E216_CLOCKS), 'clocks =', len(rows_csv), 'rows ->', fcsv, sha(fcsv))
    print('json ->', fj, sha(fj))
    print('F1 check:', json.dumps(f1chk))
    print('walk cross-check:', json.dumps(wchk))
    print('subset factor ranges:', json.dumps(meta['subset_factor_range']))
    for pid, v in pairs.items():
        print(' ', pid, v['role'], v['arm'], v['masks'], {k: round(x, 6) for k, x in v['ln_a_over_b'].items()}, 'F1', round(v['ln_a_over_b_F1_frozen'], 6))
    ok = (f1chk['printed_4dp_equal'] == f1chk['rows'] and f1chk['phi_walk_vs_frozen_bit_equal'] == f1chk['phi_walk_vs_frozen_rows']
          and wchk['n_equal'] == wchk['configs'] and wchk['req_equal'] == wchk['configs'] and FE['generator_mismatch_configs'] == 0)
    print('E216 checks', 'PASS' if ok else 'NOT ALL PASS')
    return 0 if ok else 1


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    c = argv[1]
    if c == 'constants':
        return cmd_constants(argv[2])
    if c == 'features':
        return cmd_features(argv[2])
    if c == 'e215':
        return cmd_e215(argv[2])
    if c == 'e216':
        return cmd_e216()
    print('unknown subcommand', c)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
