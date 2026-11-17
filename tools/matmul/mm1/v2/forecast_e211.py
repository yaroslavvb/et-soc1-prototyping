#!/usr/bin/env python3
"""MM1-v2's forecasts for E211, THE SECOND KERNEL (rgm211 = rgm136 with its C-block walk swapped, and gemmLnc, rgm136's non-cooperative loads),
made by the predictor in this folder UNCHANGED through E211's committed desk map, before any E211 datum (Q206, lane mm1v2-e211). Desk; numpy.

    /usr/bin/python3 -I -B tools/matmul/mm1/v2/forecast_e211.py --out <dir>
        writes <dir>/map-e211-v2.json (the map at MM1-v2's retention), <dir>/forecasts-e211.json (every point, pair and family C record) and
        <dir>/forecasts-e211.csv (one row a point); refuses to overwrite any of them
    /usr/bin/python3 -I -B tools/matmul/mm1/v2/forecast_e211.py --check
        re-makes all three in memory and compares them byte for byte with the files beside this script (exit 0 = PASS)

WHAT RUNS, UNCHANGED (every input pinned by sha256 in PINS; the run stops on any difference, and on any line of this folder's SHA256SUMS that
fails):
  - MM1-v2 as landed: mm1_v2.Model(out/mm1_v2_params.json).predict, mm1_core_v2's equations, kinds_v2. No refit, no new constant, no edit.
  - E211's desk-map tool as committed (tools/claims-v3/e211/desk/map_e211.py, imported from its path, never edited): its exact LRU stack
    distances over each walk's chip-wide request stream, its L2 model and its analysis, for its own shape list (E211_SHAPES, both walks).
    E211's registration lane (reg-e211, Q204) recorded that a v2 forecast needs the map re-run with v2's retention (its x50 and s differ from
    MM1-v1's), and E211.md section 0 (A1's dated clause) names these files MM1-v2's E211 column, outside E211's pinned folder and never read by
    its rules or scorer: the tool's analysis is run at MM1-v2's own L3 retention (x50, s and zeta of out/mm1_v2_params.json) beside MM1-v1's.
    THE REMAKE CHECK, every run: at MM1-v1's retention (the
    tool's own params(), sha256-pinned there) the tool re-makes E211's committed desk/map-e211.json number for number at every shape and walk,
    or nothing is written. Only the analysis's logistic section depends on the retention; its key keeps the tool's name ('mm1v1_logistic')
    and records the retention it was made at (x50_MB, s_MB, zeta: MM1-v2's here). The F1 anchors are not re-made (F1 is not MM1-v2's).
  - E211's points (points-e211.json); and, read only for what E211 registered beside its MM1 column: forecast-e211.json's MM1-v1 ratios
    (shown beside v2's), its family C rule C1 (e101_rule: E101's measured one-block cooperation) and the sharing-aware rule's form.
THE CARD: aifoundry3 card 0 at its pinned 600 MHz, the full chip (1,024 minions), with MM1-v2's own defaults for that card (mm1_core_v2.volts:
  0.522 V; G_of_f: no governed base on a pinned card) - the footing E211 used for MM1-v1.
THE COLUMNS (E211.md section 6's, with MM1-v2 in MM1-v1's place):
  v2    MM1-v2 through the map: the point's walk's op classes (Q0, Q1) from the map at v2's retention in place of v2's closed form (the map's
        shape object handed to v2's own Model.predict); v2's stride rule r1 carried LITERALLY in both walks, as E211 registered it for MM1-v1
        (B's second-use retention x zeta where NB is a power of two >= 4 and the footprint passes 32 MB; piF0 on B's first-use fresh stream
        where NB is a power of two >= 4: of E211's shapes only 2x8x4). Cycles an op (the wall: the slowest minion; the counter's mean), seconds
        and cycles a GEMM, W over idle with its affine form W = A + B / t_us (to score given the measured op time), J over idle, J with the card
        at rest by v2's rest law for aifoundry3 (REPORTED), transistor switches (MM1-v1's estimate as v2 carries it; never scorable), the timing
        simulation's two columns (v2's own, rgm136's gemmL step law: at a gemmLn or gemmLnc point not a count of the loop that runs; REPORTED).
  v2S   E211's sharing-aware rule MM1-S applied to v2 (forecast_e211.sharing_aware's form): A's fresh lines a shire-op priced twice
        (B += n s_V (A's fresh lines / 32)(bF + dF phi), v2's bF and dF); time and every other term v2's.
  v2cf  MM1-v2's own closed form (its Shape) at the gemmL points: REPORTED beside, never a forecast of E211.
  family C (gemmLnc): v2-C0 = MM1-v2 literally (it has no term for the load mode: gemmLnc is its twin, rgm136's walk on the same shape);
        v2-C1 = E211's REGISTERED rule C1 carried on v2's twin (the wall x r_wall, the counter's mean x r_mean, the wall over the mean x
        rho_factor, and N dE_J_per_minion_op added to v2's B: forecast-e211.json's e101_rule numbers); v2-C2 = mm-kernel2's draft rule with
        v2's b2 and d2 (REPORTED).
  pairs (rgm211 / rgm136 at the same shape): v2's wall, counter's mean, seconds, W and J over idle; v2S's J; the four stride readings with v2
        (literal r1; no stride term: Q0 and Q1 with piF0 = 0; zeta on both halves; the stride on rgm136's walk only); and MM1-v1's FROZEN
        ratios beside, read from E211's forecast-e211.json (its MM1 wall, mean and J over idle ratios).
No rule of E211 scores these numbers: E211 registered no MM1-v2 forecast and its head-to-head H7 (v2 against v1) is NOT REGISTERED (E211.md
sections 0 and 7). They are frozen here, before E211's first card command, so that any later reading of MM1-v2 on E211 is blind.
Labels: every constant of MM1-v2 is a desk fit made after its own data existed (post hoc as an act); the map is a desk model of the kernels'
addresses, never measured; E101's numbers in v2-C1 are measured (E211 carries them); nothing here is a measurement of E211.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import csv
import hashlib
import importlib.util
import io
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
V2 = 'tools/matmul/mm1/v2'
E211 = 'tools/claims-v3/e211'
PINS = {
    f'{V2}/mm1_v2.py': '5abf3a0a49757e15a776f3a1b5cdb4f7fa90943de2e016fe8b26aa4bf5324c08',
    f'{V2}/mm1_core_v2.py': 'f78c21b4f8b4c43a9a6c7319f12092937e9e92c69d3e7dc036f0e1f92b9d7e08',
    f'{V2}/kinds_v2.py': '14c72c298956c551439a6eddb77f9d75a7b7fe3414cbb78cfbd0ad5a70ed686d',
    f'{V2}/out/mm1_v2_params.json': '9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5',
    f'{V2}/SHA256SUMS': 'eafb6558c4eaa053e4e33b8a4d6b2a644175f325df9e9ba56a1b6373b556f2f2',
    f'{E211}/desk/map_e211.py': '36319654d3e8a7954baabfafb5932dedbb46026a9b3998b49ce2f1d2b13bd01b',
    f'{E211}/desk/map-e211.json': '02675c8f3bacb21d880e6d88b3433571950a0ac01b49b699fcf0e7641f7eec91',
    f'{E211}/points-e211.json': '234b496a9488eb078734e0c26ff833fe56ab5b4194e4ddc7f7f9d20141f5a537',
    f'{E211}/forecast-e211.json': '90e8d1ae4c68c162eab687624f72bf15599ae26d2050012c3381f179453108f5',
    f'{E211}/SHA256SUMS-e211-registration': '477fb113cd6a6b6cd3cea12b1ff7ca6264e55a7b1e2fb5a40e9aeb3a99bac166',
}
NAMES = {'map': 'map-e211-v2.json', 'json': 'forecasts-e211.json', 'csv': 'forecasts-e211.csv'}
CARD, F_MHZ, MASK, N = 'aifoundry3 card 0', 600.0, '0xffffffff', 1024
# E211's planning form for a peak (forecast-e211.json > peaks > how: "26.0 W high-side rest + 1.10 x W over idle + 1 W"): REPORTED only; E211's
# card plan (plan-e211.json, MM1-v1's) is not changed by anything here
REST_HIGH_W, PLAN_K, PLAN_PLUS_W = 26.0, 1.10, 1.0


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), 'rb').read()).hexdigest()


def check_pins():
    for rel, want in PINS.items():
        got = sha_rel(rel) if os.path.isfile(os.path.join(REPO, rel)) else 'missing'
        if got != want:
            sys.exit(f'forecast_e211 (MM1-v2): REFUSED, {rel} is {got}, pinned {want}')
    n, bad = 0, []
    for ln in open(os.path.join(HERE, 'SHA256SUMS')):
        if not ln.strip():
            continue
        h, p = ln.rstrip('\n').split('  ', 1)
        n += 1
        fp = os.path.join(HERE, p)
        if not os.path.isfile(fp) or hashlib.sha256(open(fp, 'rb').read()).hexdigest() != h:
            bad.append(p)
    if bad:
        sys.exit(f'forecast_e211 (MM1-v2): REFUSED, {len(bad)} of {n} SHA256SUMS lines differ: {bad[:5]}')
    return n


N_SUMS = check_pins()
sys.path.insert(0, HERE)
import mm1_core_v2 as C2  # noqa: E402
import mm1_v2 as M2  # noqa: E402

_spec = importlib.util.spec_from_file_location('map_e211', os.path.join(REPO, E211, 'desk', 'map_e211.py'))
MAPT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MAPT)

P2 = json.load(open(os.path.join(HERE, 'out', 'mm1_v2_params.json')))
TH2 = P2['time']['theta']
RET2 = {'x50': TH2['x50'], 's': TH2['s'], 'zeta': TH2['zeta']}
assert P2['time']['rule'] == 'r1' and P2['time']['halves'] is True and P2['time']['masked_map'] is False
MAP1 = json.load(open(os.path.join(REPO, E211, 'desk', 'map-e211.json')))
PTS = json.load(open(os.path.join(REPO, E211, 'points-e211.json')))
F211 = json.load(open(os.path.join(REPO, E211, 'forecast-e211.json')))


def r(x, n=8):
    if x is None:
        return None
    return float(f'{float(x):.{n}g}')


def py(x):
    """numpy scalars and arrays to plain Python, for JSON"""
    if isinstance(x, dict):
        return {k: py(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [py(v) for v in x]
    if isinstance(x, np.ndarray):
        return py(x.tolist())
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return float(x)
    return x


def dumps(obj):
    return json.dumps(obj, indent=1, sort_keys=True) + '\n'


# ------------------------------------------------------------------ the map at MM1-v2's retention, with the remake check at MM1-v1's
def build_map():
    """E211's tool (stack distances, L2 model, analysis), per shape and walk: the analysis at MM1-v1's retention must equal the committed map
    exactly; the analysis at MM1-v2's retention is this map"""
    th1 = MAPT.params()                      # MM1-v1's theta, the sha256 pinned by the tool itself
    out = {'what': "E211's desk map (tools/claims-v3/e211/desk/map_e211.py, unchanged) re-run at MM1-v2's own L3 retention for MM1-v2's "
                   "E211 forecasts; every number desk. The analysis's logistic section keeps the tool's key name ('mm1v1_logistic'); its "
                   "numbers are at the retention it records (MM1-v2's). Every other section does not depend on the retention and equals E211's "
                   "committed map. No F1 anchor (F1 is not MM1-v2's).",
           'interpreter': '/usr/bin/python3 %s, numpy %s' % (sys.version.split()[0], np.__version__),
           'tool': f'{E211}/desk/map_e211.py', 'tool_sha256': PINS[f'{E211}/desk/map_e211.py'],
           'inputs_sha256': {f'{V2}/out/mm1_v2_params.json': PINS[f'{V2}/out/mm1_v2_params.json'],
                             MAPT.PARAMS_REL: MAPT.PARAMS_SHA, f'{E211}/desk/map-e211.json': PINS[f'{E211}/desk/map-e211.json']},
           'caps_MB': list(MAPT.CAPS),
           'mm1v2_retention': {'x50_MB': RET2['x50'], 's_MB': RET2['s'], 'zeta': RET2['zeta']},
           'mm1v1_retention': {'x50_MB': th1['x50'], 's_MB': th1['s'], 'zeta': th1['zeta']},
           'shapes': {}}
    remade, differ = 0, []
    for sh in MAPT.E211_SHAPES:
        MB, NB, KB = (int(x) for x in sh.split('x'))
        out['shapes'][sh] = {}
        for w in ('mn', 'nm'):
            dA, dB, R = MAPT.stack_distances(w, MB, NB, KB)
            l2 = MAPT.l2_model(w, MB, NB, KB)
            res1 = MAPT.analyse(w, MB, NB, KB, dA, dB, R, l2, th1)
            res2 = MAPT.analyse(w, MB, NB, KB, dA, dB, R, l2, RET2)
            if json.dumps(res1, sort_keys=True) == json.dumps(MAP1['shapes'][sh][w], sort_keys=True):
                remade += 1
            else:
                differ.append(f'{sh}-{w}')
            free1 = {k: v for k, v in res1.items() if k != 'mm1v1_logistic'}
            free2 = {k: v for k, v in res2.items() if k != 'mm1v1_logistic'}
            assert json.dumps(free1, sort_keys=True) == json.dumps(free2, sort_keys=True)
            out['shapes'][sh][w] = res2
    n = 2 * len(MAPT.E211_SHAPES)
    if differ:
        sys.exit(f'forecast_e211 (MM1-v2): REFUSED, the tool at MM1-v1\'s retention does not re-make E211\'s committed map at {differ}')
    out['remake_check'] = (f"PASS: at MM1-v1's retention the tool re-made desk/map-e211.json's entry number for number at {remade} of {n} "
                           f"shape-walks ({len(MAPT.E211_SHAPES)} shapes, both walks); every section but the logistic one is retention-free "
                           f"and equal at both retentions")
    return out


MAP_TEXT = None          # set by main(): the map's file text, and MAP2 the same read back, so every forecast reads exactly what the file holds
MAP2 = None


# ------------------------------------------------------------------ MM1-v2 through the map
class MapShapeV2:
    """a gemmL point's map skeleton for MM1-v2's Model: the desk map's op classes at v2's retention in place of v2's closed form (full chip).
    variant: 'r1' (v2's frozen rule, carried literally), 'none' (no stride term), 'both' (zeta on both halves' B)."""

    def __init__(self, sh, walk, variant='r1'):
        MB, NB, KB = (int(x) for x in sh.split('x'))
        self.arm = f'map:{walk}:{sh}:{variant}'
        self.mi = C2.mask_info(MASK)
        self.blocks = (MB, NB, KB)
        self.kernel = 'gemmL'
        self.masked_map = False
        self.F = self.F_full = C2.footprint(MB, NB, KB)
        self.p2 = C2.is_pow2(NB) and NB >= 4
        self.ops = 64 * MB * NB * KB
        lg = MAP2['shapes'][sh][walk]['mm1v1_logistic']      # the tool's key; its numbers at the retention it records (MM1-v2's)
        assert (lg['x50_MB'], lg['s_MB'], lg['zeta']) == (TH2['x50'], TH2['s'], TH2['zeta'])
        assert lg['r1_rule_applies'] == (self.p2 and self.F > 32.0)
        self.q = {k: np.array([[float(v) for v in row] for row in lg[k]]) for k in ('Q0', 'Q1', 'Q0z', 'Q1z')}
        self.variant = variant
        self.applies = lg['r1_rule_applies']

    def Qhalves(self, x50, s, zeta=1.0, rule='v1'):
        assert rule == 'r1' and (x50, s, zeta) == (TH2['x50'], TH2['s'], TH2['zeta']), "the map was made at MM1-v2's frozen retention"
        if self.variant == 'none' or not self.applies:
            return self.q['Q0'], self.q['Q1']
        if self.variant == 'both':
            return self.q['Q0z'], self.q['Q1z']
        return self.q['Q0'], self.q['Q1z']


def model(piF0=None):
    P = copy.deepcopy(P2)
    if piF0 is not None:
        P['time']['theta']['piF0'] = piF0
    return M2.Model(P)


M_FROZEN = model()
M_NOPI = model(0.0)
M_CF = model()            # the closed form's own model (its own Shape objects), apart from the map's


def v2_on_map(sh, walk, fmt, variant='r1'):
    m = M_NOPI if variant == 'none' else M_FROZEN
    shp = MapShapeV2(sh, walk, variant)
    m._shapes[(shp.arm, MASK)] = shp
    return m.predict(CARD, shp.arm, fmt, 'random', MASK, F_MHZ)


def sharing_aware(pred, sh, walk):
    """E211's MM1-S form on MM1-v2: A's fresh lines a shire-op priced twice"""
    E = P2['energy']['theta']
    lg = MAP2['shapes'][sh][walk]['mm1v1_logistic']['frozen_rule_r1']
    nFA = lg['A_lines_L2_L3_F_per_shire_op'][2]
    add = N * pred['s_V'] * 1e-12 * nFA / 32.0 * (E['bF'] + E['dF'] * pred['phi']) * 1e6
    A = pred['W_affine']['A_W']
    B = pred['W_affine']['B_W_us'] + add
    W = A + B / pred['T_op_us']
    return {'A_W': A, 'B_W_us': B, 'W_over_idle': W, 'J_over_idle_per_gemm': W * pred['seconds_per_gemm'],
            'A_fresh_lines_per_shire_op': nFA, 'B_added_W_us': add}


def family_c(twin):
    """v2-C0, v2-C1 (E211's registered C1 on v2's twin) and v2-C2 (REPORTED) from v2's twin forecast (rgm136's walk on the same shape)"""
    E = P2['energy']['theta']
    R1 = F211['e101_rule']
    A, B = twin['W_affine']['A_W'], twin['W_affine']['B_W_us']
    t_us, tg = twin['T_op_us'], twin['seconds_per_gemm']
    c1t = t_us * R1['r_wall']
    B1 = B + N * R1['dE_J_per_minion_op'] * 1e6
    W1 = A + B1 / c1t
    tg1 = tg * R1['r_wall']
    B2 = B + N * twin['s_V'] * 1e-12 * 832.0 / 32.0 * (E['b2'] + E['d2'] * twin['phi']) * 1e6
    W2 = A + B2 / t_us
    rl = twin.get('rest_law', {}).get('P_rest_W')
    return {'C1': {'cycles_per_op_wall': twin['cycles_per_op_wall'] * R1['r_wall'], 'cycles_per_op_mean': twin['cycles_per_op_mean'] * R1['r_mean'],
                   'rho_wall_over_mean': twin['rho_wall_over_mean'] * R1['rho_factor'], 'seconds_per_gemm': tg1, 'T_op_us': c1t,
                   'W_affine': {'A_W': A, 'B_W_us': B1}, 'W_over_idle': W1, 'J_over_idle_per_gemm': W1 * tg1,
                   'J_at_rest_per_gemm_REPORTED': (rl + W1) * tg1 if rl is not None else None,
                   'rule': "E211's registered C1 (forecast-e211.json > e101_rule: r_wall, r_mean, rho_factor, dE_J_per_minion_op) on v2's twin"},
            'C0': {'cycles_per_op_wall': twin['cycles_per_op_wall'], 'cycles_per_op_mean': twin['cycles_per_op_mean'], 'seconds_per_gemm': tg,
                   'W_affine': {'A_W': A, 'B_W_us': B}, 'W_over_idle': twin['W_over_idle'], 'J_over_idle_per_gemm': twin['J_over_idle_per_gemm'],
                   'rule': 'MM1-v2 literally: no term for the load mode, so gemmLnc = its twin'},
            'C2_REPORTED': {'cycles_per_op_wall': twin['cycles_per_op_wall'], 'seconds_per_gemm': tg, 'W_affine': {'A_W': A, 'B_W_us': B2},
                            'W_over_idle': W2, 'J_over_idle_per_gemm': W2 * tg,
                            'rule': "mm-kernel2's draft rule (+832 L2 lines a shire-op at b2 + d2 phi, time unchanged) with v2's b2 and d2"}}


def v2_record(pred):
    """every quantity MM1-v2's predict returns (numpy to plain Python), plus E211's planning form (REPORTED)"""
    rec = py(pred)
    rec['planning_peak_W_REPORTED'] = REST_HIGH_W + PLAN_K * pred['W_over_idle'] + PLAN_PLUS_W
    return rec


def build():
    pts = {p['id']: p for p in PTS['points'] + PTS['smoke']}
    out = {'experiment': 'E211', 'model': 'MM1-v2', 'request': 'Q206', 'lane': 'mm1v2-e211',
           'what': "MM1-v2's forecasts for E211's points, made before any E211 datum by MM1-v2 as landed, unchanged, through E211's committed desk "
                   "map re-run at MM1-v2's own retention (v2); E211's sharing-aware rule on v2 (v2S); v2's closed form at the gemmL points "
                   "(v2cf, REPORTED); family C's v2-C0, v2-C1 (E211's registered C1 on v2's twin) and v2-C2 (REPORTED); the ratios per pair "
                   "with MM1-v1's frozen ratios beside. No rule of E211 scores them (H7 NOT REGISTERED).",
           'card': {'card': CARD, 'f_MHz': F_MHZ, 'V': C2.volts(CARD, F_MHZ), 'G_W': C2.G_of_f(CARD, F_MHZ), 'minions': N, 'mask': MASK,
                    'how': "MM1-v2's own defaults for this card (mm1_core_v2.volts, G_of_f)"},
           'interpreter': '/usr/bin/python3 %s, numpy %s' % (sys.version.split()[0], np.__version__),
           'inputs_sha256': dict(PINS, **{MAPT.PARAMS_REL: MAPT.PARAMS_SHA}),
           'mm1v2_sha256sums_checked': f'{N_SUMS} of {N_SUMS} OK',
           'map': {'file': NAMES['map'], 'sha256': hashlib.sha256(MAP_TEXT.encode()).hexdigest(), 'remake_check': MAP2['remake_check'],
                   'mm1v2_retention': MAP2['mm1v2_retention'], 'mm1v1_retention': MAP2['mm1v1_retention']},
           'labels': {'v2': "forecast of code (desk); MM1-v2's constants post hoc as an act; blind for E211 once in a pushed commit before E211's "
                            "first card command", 'map': 'desk model of the kernels\' addresses, never measured',
                      'v2-C1': "E211's registered rule: E101's measured one-block figures carried on v2's twin", 'REPORTED': 'never a forecast to score'},
           'scored_by_E211': 'NO: E211 registered no MM1-v2 forecast; H7 (v2 against v1) NOT REGISTERED (E211.md sections 0 and 7)',
           'points': {}, 'pairs': {}, 'family_C': {}}
    mm = {}
    for pid, p in pts.items():
        sh, fmt, walk = p['shape'], p['format'], p['walk']
        pred = v2_on_map(sh, walk, fmt)
        rec = {'arm': p['arm'], 'arm_family': p['arm_family'], 'family': p['family'], 'shape': sh, 'format': fmt, 'walk': walk,
               'coop': p['coop'], 'kernel': p['kernel'], 'host': p['host'], 'ops_per_minion_per_gemm': p['ops_per_minion_per_gemm']}
        assert pred['ops_per_minion_per_gemm'] == p['ops_per_minion_per_gemm'] and pred['minions'] == p['minions'] == N
        rec['v2'] = v2_record(pred)
        rec['v2']['how'] = ("MM1-v2 as landed, its frozen equations and constants, on the desk map of the point's walk at MM1-v2's retention "
                            f"({NAMES['map']}); the stride rule r1 carried literally")
        rec['v2S'] = sharing_aware(pred, sh, walk)
        if p['arm_family'] == 'gemmL':
            cf = M_CF.predict(CARD, p['arm'], fmt, 'random', MASK, F_MHZ)
            rec['v2cf_REPORTED'] = {'cycles_per_op_wall': cf['cycles_per_op_wall'], 'cycles_per_op_mean': cf['cycles_per_op_mean'],
                                    'seconds_per_gemm': cf['seconds_per_gemm'], 'W_over_idle': cf['W_over_idle'],
                                    'J_over_idle_per_gemm': cf['J_over_idle_per_gemm'], 'lines_L2_L3_F': py(cf['lines_L2_L3_F']),
                                    'map_over_closed_form_cycles_minus_1': pred['cycles_per_op_wall'] / cf['cycles_per_op_wall'] - 1.0}
        rec['scored_in_watts_E211_form'] = bool(pred['W_over_idle'] < 3.0)
        rec['timing_simulation_columns'] = (
            "v2's own (sim_steps_per_minion_per_gemm: mm1_core_v2.sim_steps, rgm136's cooperative gemmL step law; the floors): REPORTED, "
            "never scored" + ("" if p['arm_family'] == 'gemmL' else
                              f"; at this {p['arm_family']} point the count is still rgm136's gemmL law, not a count of the loop that runs "
                              "(rgm211's walk or rgm136's non-cooperative branch): E211's own record of its simulator runs holds those"))
        mm[pid] = pred
        out['points'][pid] = rec
    for pid, p in pts.items():
        if p['arm_family'] != 'gemmLnc':
            continue
        fc = py(family_c(mm[pid]))       # the gemmLnc point's own v2 forecast IS its twin's (rgm136's walk on the same shape)
        out['points'][pid]['C'] = fc
        twin = mm[pid]
        out['family_C'][p['pair'] or pid] = {
            'point': pid, 'twin': p['twin_of'], 'ratio_v2C0': 1.0,
            'ratio_v2C1_wall': fc['C1']['cycles_per_op_wall'] / twin['cycles_per_op_wall'],
            'ratio_v2C1_mean': fc['C1']['cycles_per_op_mean'] / twin['cycles_per_op_mean'],
            'ratio_v2C1_J_over_idle': fc['C1']['J_over_idle_per_gemm'] / twin['J_over_idle_per_gemm'],
            'ratio_v2C2_J_over_idle_REPORTED': fc['C2_REPORTED']['J_over_idle_per_gemm'] / twin['J_over_idle_per_gemm'],
            'MM1v1_frozen_E211': F211['family_C'][p['pair'] or pid]}
    for p in PTS['points']:
        if p['arm_family'] != 'gemmLn':
            continue
        pair = p['pair']
        m_id, n_id = pair + 'm', pair + 'n'
        mrec, nrec = out['points'][m_id], out['points'][n_id]
        sh, fmt = p['shape'], p['format']
        rd = {}
        for var in ('r1', 'none', 'both'):
            rd[var] = v2_on_map(sh, 'nm', fmt, var)['cycles_per_op_wall'] / v2_on_map(sh, 'mn', fmt, var)['cycles_per_op_wall']
        rd['rgm136_only'] = v2_on_map(sh, 'nm', fmt, 'none')['cycles_per_op_wall'] / v2_on_map(sh, 'mn', fmt, 'r1')['cycles_per_op_wall']
        f1 = F211['pairs'][pair]
        v2m, v2n = mrec['v2'], nrec['v2']
        out['pairs'][pair] = {
            'family': p['family'], 'shape': sh, 'format': fmt, 'twin': m_id, 'second': n_id,
            'ratio_wall': {'v2': v2n['cycles_per_op_wall'] / v2m['cycles_per_op_wall'], 'MM1v1_frozen_E211': f1['ratio_wall']['MM1']},
            'ratio_mean': {'v2': v2n['cycles_per_op_mean'] / v2m['cycles_per_op_mean'], 'MM1v1_frozen_E211': f1['ratio_mean']['MM1']},
            'ratio_seconds': {'v2': v2n['seconds_per_gemm'] / v2m['seconds_per_gemm']},
            'ratio_W_over_idle': {'v2': v2n['W_over_idle'] / v2m['W_over_idle']},
            'ratio_J_over_idle': {'v2': v2n['J_over_idle_per_gemm'] / v2m['J_over_idle_per_gemm'],
                                  'v2S': nrec['v2S']['J_over_idle_per_gemm'] / mrec['v2S']['J_over_idle_per_gemm'],
                                  'MM1v1_frozen_E211': f1['ratio_J_over_idle']['MM1'], 'MM1S_v1_frozen_E211': f1['ratio_J_over_idle']['MM1_S']},
            'ln_v2_over_v1_wall_ratio': float(np.log((v2n['cycles_per_op_wall'] / v2m['cycles_per_op_wall']) / f1['ratio_wall']['MM1'])),
            'stride_readings_ratio_wall_v2': {'literal_r1 (v2)': rd['r1'], 'no_stride_term': rd['none'], 'zeta_both_halves': rd['both'],
                                              'stride_on_rgm136_only': rd['rgm136_only']},
            'chip_DRAM_lines_per_step_v2_retention': {w: MAP2['shapes'][sh][w]['mm1v1_logistic']['frozen_rule_r1']['chip_distinct_lines_per_step']['DRAM_lines']
                                                      for w in ('mn', 'nm')},
            'fresh_lines_per_shire_op_v2_retention': {w: MAP2['shapes'][sh][w]['mm1v1_logistic']['frozen_rule_r1']['lines_L2_L3_F_per_shire_op'][2]
                                                      for w in ('mn', 'nm')}}
    peaks = {}
    for pid, rec in out['points'].items():
        cand = [('v2', rec['v2']['planning_peak_W_REPORTED'])]
        if rec.get('C'):
            cand += [('v2-C1', REST_HIGH_W + PLAN_K * rec['C']['C1']['W_over_idle'] + PLAN_PLUS_W),
                     ('v2-C2', REST_HIGH_W + PLAN_K * rec['C']['C2_REPORTED']['W_over_idle'] + PLAN_PLUS_W)]
        for col, w in cand:
            if col not in peaks or w > peaks[col]['planning_W']:
                peaks[col] = {'id': pid, 'planning_W': w}
    peaks['how'] = ("E211's planning form (26.0 W high-side rest + 1.10 x W over idle + 1 W) on each column's W over idle, the largest point "
                    "of each: REPORTED only; E211's card plan (plan-e211.json, made with MM1-v1) is unchanged")
    out['peak_REPORTED'] = peaks
    return py(out)


def flat(out):
    rows = []
    for pid, rec in out['points'].items():
        m, s = rec['v2'], rec['v2S']
        row = {'id': pid, 'arm': rec['arm'], 'arm_family': rec['arm_family'], 'family': rec['family'], 'format': rec['format'],
               'walk': rec['walk'], 'coop': rec['coop'], 'kernel': rec['kernel'], 'host': rec['host'],
               'ops_per_minion_per_gemm': rec['ops_per_minion_per_gemm'],
               'v2_cycles_per_op_wall': r(m['cycles_per_op_wall']), 'v2_cycles_per_op_mean': r(m['cycles_per_op_mean']),
               'v2_seconds_per_gemm': r(m['seconds_per_gemm']), 'v2_W_over_idle': r(m['W_over_idle']),
               'v2_A_W': r(m['W_affine']['A_W'], 10), 'v2_B_W_us': r(m['W_affine']['B_W_us'], 10),
               'v2_J_over_idle_per_gemm': r(m['J_over_idle_per_gemm']), 'v2_rest_law_P_W': r(m['rest_law']['P_rest_W']),
               'v2_J_at_rest_rest_law_REPORTED': r(m['rest_law']['J_at_rest_per_gemm_REPORTED']),
               'v2S_B_W_us': r(s['B_W_us'], 10), 'v2S_J_over_idle_per_gemm': r(s['J_over_idle_per_gemm']),
               'v2cf_cycles_per_op_wall_REPORTED': r(rec['v2cf_REPORTED']['cycles_per_op_wall']) if rec.get('v2cf_REPORTED') else None}
        if rec.get('C'):
            c1 = rec['C']['C1']
            row.update({'v2C1_cycles_per_op_wall': r(c1['cycles_per_op_wall']), 'v2C1_cycles_per_op_mean': r(c1['cycles_per_op_mean']),
                        'v2C1_seconds_per_gemm': r(c1['seconds_per_gemm']), 'v2C1_B_W_us': r(c1['W_affine']['B_W_us'], 10),
                        'v2C1_W_over_idle': r(c1['W_over_idle']), 'v2C1_J_over_idle_per_gemm': r(c1['J_over_idle_per_gemm'])})
        rows.append(row)
    keys = []
    for row in rows:
        for k in row:
            if k not in keys:
                keys.append(k)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=keys, lineterminator='\n')
    w.writeheader()
    for row in rows:
        w.writerow(row)
    return buf.getvalue()


def main():
    global MAP_TEXT, MAP2
    ap = argparse.ArgumentParser()
    ap.add_argument('--out')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    if not a.check:
        if not a.out:
            ap.error('--out <dir> or --check')
        for name in NAMES.values():
            if os.path.exists(os.path.join(a.out, name)):
                sys.exit(f'forecast_e211 (MM1-v2): REFUSED, {name} exists in {a.out} (never overwritten)')
    MAP_TEXT = dumps(py(build_map()))
    MAP2 = json.loads(MAP_TEXT)
    out = build()
    texts = {'map': MAP_TEXT, 'json': dumps(out), 'csv': flat(out)}
    if a.check:
        res = []
        for k, name in NAMES.items():
            p = os.path.join(HERE, name)
            res.append((name, os.path.isfile(p) and open(p).read() == texts[k]))
        print('forecast_e211 (MM1-v2) --check: ' + ', '.join(f"{n} {'SAME' if ok else 'DIFFERS'}" for n, ok in res))
        print('CHECK PASS' if all(ok for _, ok in res) else 'CHECK FAILED')
        return 0 if all(ok for _, ok in res) else 1
    os.makedirs(a.out, exist_ok=True)
    for k, name in NAMES.items():
        with open(os.path.join(a.out, name), 'w') as f:
            f.write(texts[k])
    print(f"forecast_e211 (MM1-v2): wrote {', '.join(NAMES.values())} to {a.out}; {out['map']['remake_check']}; MM1-v2 SHA256SUMS "
          f"{out['mm1v2_sha256sums_checked']}")
    for pair, x in out['pairs'].items():
        print(f"  {pair} {x['shape']} {x['format']}: wall ratio v2 {x['ratio_wall']['v2']:.4f} (MM1-v1 frozen {x['ratio_wall']['MM1v1_frozen_E211']:.4f}); "
              f"J over idle ratio v2 {x['ratio_J_over_idle']['v2']:.4f} (v1 {x['ratio_J_over_idle']['MM1v1_frozen_E211']:.4f})")
    return 0


if __name__ == '__main__':
    sys.exit(main())
