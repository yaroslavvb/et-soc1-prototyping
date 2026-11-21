#!/usr/bin/env python3
"""amend-e223 (Q239a) step 2: DATED AMENDMENT 1 to decl-e223's frozen declaration of the lab's blind test of E223, written as NEW files beside
it (DECLARED-blind-e223-amendment-1.md and .json at this lane's root), before any E223 datum: 'MM1-v3.2 + mesh' and 'MM1-v3.2 + AF4 + mesh'
as REPORTED models and 'MM1-v3.2 + mask-ceiling' as a REPORTED reference, scored exactly as the declaration scores its REPORTED mask
candidate 'MM1-v3.2 + posimb-mask'. Also the twin keys of the three columns by the declaration's own rule (work/step2/twin-keys-amend1.json).
Reads no E223 datum (the case list is the declaration's). Run: /usr/bin/python3 -I -B s02_amend.py <lane dir>"""
import collections
import hashlib
import json
import os
import re
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
OUT = os.path.dirname(L)
W = os.path.dirname(OUT)
DECL = os.path.join(OUT, 'decl-e223')
LAB = os.path.join(L, 'work', 'lab')
MM1 = os.path.join(LAB, 'tools', 'matmul', 'mm1')
S2 = os.path.join(L, 'work', 'step2')
os.makedirs(S2, exist_ok=True)
TZ = dict(os.environ, TZ='America/Los_Angeles')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def pst():
    return subprocess.run(['date', '+%a %d %b %Y %H:%M:%S %Z'], capture_output=True, text=True, env=TZ).stdout.strip()


WRITTEN = pst()
CHK = json.load(open(os.path.join(L, 'work', 'step1', 'frozen-checks.json')))
RL = json.load(open(os.path.join(DECL, 'work', 'step1', 'runs-listed.json')))
assert sha(os.path.join(DECL, 'work', 'step1', 'runs-listed.json')) == 'ed4595b10697daa0d1923d3fcaca2a04b295e6ccdd0dc2e87e5f77448330004d'
CASES = RL['cases']
FULL = '0xffffffff'


def mh(m):
    return '0x%x' % int(str(m), 16)


sub = [c for c in CASES if mh(c['mask']) != FULL]
n_sub = len(sub)
n_place = sum(1 for c in CASES if c['class'] == 'PLACE')
n_m221 = sum(1 for c in CASES if c['maske221'])
n_ceil = sum(1 for c in sub if c['MB'] * c['NB'] >= 2)
by_ho = collections.Counter(h for c in CASES for h in c['ho_sets'])
assert n_sub == 513 and n_place == 421 and n_m221 == 353, (n_sub, n_place, n_m221)

# ------------------------------------------------------------------ the twin keys, by the declaration's rule (s01b_models.py section 2)
TW = json.load(open(os.path.join(DECL, 'work', 'step1', 'twin-keys.json')))
assert sha(os.path.join(DECL, 'work', 'step1', 'twin-keys.json')) == '8e90e2c44a8846f5ab13f26b69982d78031db8cba22328ac2c7af951387c1a41'


def f25(f):
    return int(round(float(f) / 25.0) * 25)


def arm_kernel(arm):
    if arm.startswith('gemmLnc'):
        return 'rgm136'
    if arm.startswith('gemmLn'):
        return 'rgm211'
    if arm.startswith('gemmL'):
        return 'rgm136'
    return 'run_gemm'


TERM_POINTS = {'mesh': 'v3.4-cands/mesh/out/points-mesh.json', 'mask-ceiling': 'v3.4-cands/mask-ceiling/inputs/points_all.json',
               'AF4': 'v3.3-cands/gemmlnc-af4/data/s01_points.json'}
TOK = re.compile(r'E223|mmsweep7|1121-mmsweep7')
TK, INC = {}, {}
for t, f in TERM_POINTS.items():
    d = json.load(open(os.path.join(MM1, f)))
    pts = d['points'] if isinstance(d, dict) else d
    tk, ek = set(), set()
    for p in pts:
        k = p.get('kernel') or arm_kernel(p['arm'])
        if not p['arm'].startswith('gemmL'):
            k = 'run_gemm'
        key = (p['card'], k, p['arm'], p['fmt'], str(p['mask']).lower(), f25(p['f']))
        tk.add(key)
        ek.add(key + (p.get('kind'),))
    TK[t] = (tk, ek)
    INC[t] = {'file': f, 'sha256': sha(os.path.join(MM1, f)), 'points': len(pts),
              'e223_ids': [p['id'] for p in pts if TOK.search(str(p.get('id'))) or p.get('exp') == 'E223']}
    assert not INC[t]['e223_ids'], t
TERMED = {'MM1-v3.2 + mesh': ('mesh',), 'MM1-v3.2 + AF4 + mesh': ('AF4', 'mesh'), 'MM1-v3.2 + mask-ceiling': ('mask-ceiling',)}
base_t = {tuple(x) for x in TW['MM1-v3.2']['time_keys']}
base_e = {tuple(x) for x in TW['MM1-v3.2']['energy_keys']}
tw = {}
for mdl, terms in TERMED.items():
    tk, ek = set(base_t), set(base_e)
    for t in terms:
        tk |= TK[t][0]
        ek |= TK[t][1]
    tw[mdl] = {'time_keys': sorted(list(x) for x in tk), 'energy_keys': sorted(list(x) for x in ek), 'base': 'MM1-v3.2', 'terms': list(terms),
               'sources': {TERM_POINTS[t]: INC[t]['sha256'] for t in terms}, 'base_keys_from': 'decl-e223 work/step1/twin-keys.json 8e90e2c4'}
TWF = os.path.join(S2, 'twin-keys-amend1.json')
json.dump(tw, open(TWF, 'w'), sort_keys=True)
NOMF = {'aifoundry1 card 1': 600, 'aifoundry1 card 0': 800, 'aifoundry2 card 0': 800}
prev = {}
for mdl in TERMED:
    tk = {tuple(x) for x in tw[mdl]['time_keys']}
    ek = {tuple(x) for x in tw[mdl]['energy_keys']}
    nt = ne = 0
    for c in CASES:
        kt = (c['card'], 'rgm136', c['arm'], c['fmt'], mh(c['mask']), NOMF[c['card']])
        nt += kt in tk
        ne += (kt + (c['kind_energy'],)) in ek
    prev[mdl] = [nt, ne]

# ------------------------------------------------------------------ the state
Q = os.path.join(L, 'work', 'step1', 'q238-frozen-posts-at-amendment.txt')
REL = os.path.join(W, 'out', 'orch', 'e223-releases.txt')
rel_lines = [x.rstrip('\n') for x in open(REL) if x.strip() and not x.startswith('# ')]
claims = sorted(f for f in os.listdir(os.path.join(W, 'out', 'orch')) if f.startswith('claim-'))
MESH_FZ = CHK['mesh']['FROZEN_sha256']
CEIL_FZ = CHK['ceiling']['posted_FROZEN_sha256']
CEIL_DISK = CHK['ceiling']['disk_FROZEN_sha256']
MP = json.load(open(os.path.join(MM1, 'v3.4-cands', 'mesh', 'out', 'params-mesh.json')))
CP = json.load(open(os.path.join(MM1, 'v3.4-cands', 'mask-ceiling', 'params-mask-ceiling.json')))
cset = CP.get('settings', {})
HO = ', '.join(f'{h} ({by_ho[h]})' for h in sorted(by_ho))
J = {
    'what': "decl-e223 AMENDMENT 1 (dated): 'MM1-v3.2 + mesh' and 'MM1-v3.2 + AF4 + mesh' (REPORTED models) and 'MM1-v3.2 + mask-ceiling' "
            "(a REPORTED reference, never a model candidate) join the lab's blind test of E223, before any E223 datum",
    'lane': 'amend-e223 (round Q239a)', 'written_pst': WRITTEN, 'python': sys.version.split()[0] + ' (/usr/bin/python3 -I -B)',
    'amends': {'declaration': 'OUT/decl-e223 (land tools/matmul/mm1/v3.1/blind-e223/)', 'FROZEN_txt_sha256': CHK['decl_e223_FROZEN_sha256'],
               'frozen_at': 'Sat 21 Nov 2026 02:22:09 PST', 'posted': '#16 02:23:46 PST',
               'files_unchanged': {'DECLARED-blind-e223.md': 'f2795ec352ca6244e8af2167b5b9742e1c2dad7fa6e844eb6035957b8398b3c7',
                                   'DECLARED-blind-e223.json': 'c74dc54746780a8d9a952e871a81510913b5e33c6934bdf6a23ee5124ee76e02',
                                   'forecasts-nominal-e223.csv': 'dc47385df5af5db0bf6ba4dcdc49f453506f8df88eb07ee488e3527d3bd32082',
                                   'forecasts-nominal-e223.json': 'aeb174a7ea93a73b0baeac3d404fe57013694118dfb39e2963fe1fc388aa424f'},
               'the_rule_used': "the declaration's Q238_read: 'A Q238 candidate that qualifies only after this read is not in this freeze: it can be "
                                "scored on E223 only by a dated amendment hashed before E223's first datum, else as UNREAD'"},
    'qualification': {
        'q238_posts_read': CHK['q238_posts'],
        'mask-mesh': {'FROZEN_txt_sha256': MESH_FZ, 'frozen_final': 'Sat 21 Nov 2026 02:03:37 PST',
                      'posted': '#1.30.1.2.1.1.1.1.1.1.2 2026-11-21 02:23:42 PST (the CORRECTION: the final freeze line; the 02:03:18 post named the '
                                'superseded first write 3d4942fa)', 'on_disk_equal_posted': True, 'land_FROZEN_equal': CHK['mesh']['land_FROZEN_equal'],
                      'lane_files_equal': CHK['mesh']['lane_files'], 'land_SHA256SUMS': CHK['mesh']['land_SHA256SUMS']},
        'mask-ceiling': {'FROZEN_txt_sha256_posted': CEIL_FZ, 'posted': '#1.30.1.2.1.1.1.1.1.1.1 2026-11-21 02:21:44 PST',
                         'posted_file': 'OUT/mask-ceiling/FROZEN.txt.superseded-022113 (written 02:21:13 PST)',
                         'on_disk_FROZEN_txt_sha256': CEIL_DISK, 'on_disk_written': '02:22:21 PST (not posted at the read)',
                         'posted_vs_on_disk_differ_only': CHK['ceiling']['posted_vs_disk_differ_only'],
                         'called_files_equal_under_both': CHK['ceiling']['called_files_equal_at_both'],
                         'land_SHA256SUMS': CHK['ceiling']['land_SHA256SUMS']}},
    'domain': {'every_case_in_domain': True, 'n_cases': len(CASES), 'n_runs': sum(len(c['runs']) for c in CASES),
               'mesh_in_scope': f'{n_sub} cases (every subset-mask case of rgm136 gemmL); MM1-v3.2 to the last bit at the {len(CASES) - n_sub} full-chip cases',
               'mask_ceiling_in_scope': f'{n_ceil} cases (rgm136 gemmL, MB x NB >= 2, a shire subset); factor exactly 1 at the other {len(CASES) - n_ceil}',
               'AF4': 'acts at no E223 case (no gemmLnc arm): MM1-v3.2 + AF4 + mesh = MM1-v3.2 + mesh at every case, declared now (checked to 1e-12 at '
                      'the nominal footing)', 'out_of_domain': 'none'},
    'models_added': {
        'MM1-v3.2 + mesh': {'label': 'REPORTED', 'source': 'Q238 mask-mesh (track M), KEPT by its declared rule, FROZEN.txt ' + MESH_FZ,
                            'land_copy': 'work/lab/tools/matmul/mm1/v3.4-cands/mesh/ (copied unchanged)', 'constants': MP['constants'],
                            'variant': MP.get('variant'), 'base': 'MM1-v3.2 4e386f75 unchanged (params c991de16)',
                            'call': "mesh_term.Model(json.load(open('out/params-mesh.json')), 'out/features-mesh.json').time_many([{arm, kernel "
                                    "'rgm136', fmt, mask, f}]) with MASK_MESH_REPO = the lab copy (README section 6)",
                            'record': 'T = time_many; cycles an op = T x f; counter mean = cycles / MM1-v3.2 rho; seconds a pass = ops x T; W over '
                                      'idle at a measured t = MM1-v3.2 A + B / t (E1 = MM1-v3.2 by construction); with t forecast at this T (E2, E4, H5)',
                            'features': 'configuration only (arm, mask: the walk sets and latencies); a configuration missing from the frozen cache is made '
                                        'by its own mesh_l3.simulate (no constant)'},
        'MM1-v3.2 + AF4 + mesh': {'label': 'REPORTED (by construction, no refit)',
                                  'call': 'scripts/compose_af4.py composed(specs, mesh) unchanged (README section 6)',
                                  'at_e223': "equal to 'MM1-v3.2 + mesh' at every case (AF4 acts at no E223 case): its tests repeat mesh's"},
        'MM1-v3.2 + mask-ceiling': {'label': 'REFERENCE, REPORTED; never a model candidate', 'source': 'Q238 mask-ceiling (track C), posted FROZEN.txt '
                                    + CEIL_FZ, 'land_copy': 'work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/ (copied unchanged)',
                                    'forest': {'trees': 200, 'settings': cset, 'params_sha256': 'f991b63787a4b3990328a8d1f232413f3b91ae0005df011d8a3a9c03c2fbe1d8'},
                                    'call': 'python3 -I -B mask_ceiling.py --points <points.json> --out <factors.json> (README section 7)',
                                    'record': "MM1-v3.2's own row with T_op_us, cycles_per_op_wall and seconds_per_gemm times the factor; the counter's "
                                              "mean MM1-v3.2's (the reference forecasts none); W over idle at a measured t = MM1-v3.2 A + B / t; with t "
                                              "forecast at the new T", 'features': 'configuration only (arm, mask, format) and the clock f'}},
    'procedure': {
        'footing_1_measured': "the declaration's: each frozen predictor unchanged at each run's measured conditions from the start-of-run records "
                              "only (kclock_mhz; card 1 0.517 V, the governed cards rails.minion.mV / 1000; die_start_c, 50 C when absent); the "
                              "callers: this lane's scripts/s03_forecast.py forecast_amend1(cases, cond) (the same code that makes the amendment's "
                              "nominal forecasts; cond per run {'f', 'V', 't0_c'}), each term on MM1-v3.2's forecast at the same conditions",
        'fields_read_before_scoring': "the declaration's, unchanged", 'footing_2_nominal': 'forecasts-nominal-e223-amend1.csv and .json, frozen with '
        'this amendment (section h)', 'order': "the declaration's: after the data, the conditions read, the measured-conditions forecasts of every "
        "column (the amended three with them) hashed, the scorer hashed, then the read and the scores"},
    'metric': {'error': "the declaration's: forecast / measured - 1; rms and bias %; watts cases in W", 'case': 'the mean of its runs',
               'twins': "per model by the declaration's rule: MM1-v3.2's keys UNION every point its term's fit read (mesh: out/points-mesh.json; "
                        "mask-ceiling: inputs/points_all.json; AF4 + mesh: AF4's data/s01_points.json too), time and (with the kind) energy alike, a "
                        "conservative twin: work/step2/twin-keys-amend1.json", 'twin_preview_at_nominal_clocks_time_energy': prev},
    'comparisons': {
        'D3a_masks_REPORTED': f"deciding nothing, the declaration's D3 form: on THE PLACEMENT CLASS (PLACE, {n_place} cases) each of 'MM1-v3.2 + "
                              f"mesh', 'MM1-v3.2 + AF4 + mesh' and the reference 'MM1-v3.2 + mask-ceiling' vs MM1-v3.2 on H1 (wall), H2 (counter "
                              f"mean), H3 (seconds) and H5 (J over idle with t forecast), per card and pooled, by the exact two-sided sign test; the "
                              f"same on every subset-mask case ({n_sub}), on MASKE221 ({n_m221}) and on each held-out set, REPORTED",
        'D3b_beside_REPORTED': "'MM1-v3.2 + mesh' vs 'MM1-v3.2 + posimb-mask' and vs 'MM1-v3.2 + posimb'; the reference vs 'MM1-v3.2 + mesh' and vs "
                               "'MM1-v3.2 + posimb-mask'; on the same cases, quantities and test",
        'test': "the declaration's: exact two-sided sign test (binomial at 1/2) on the untied cases, alpha 0.05; A BETTER, B BETTER, NOT DECIDED, "
                "TOO FEW under 10 untied cases, NO DATA with none; d = |ln(1 + e_B)| - |ln(1 + e_A)| (watts cases |dW_B| - |dW_A| in W); ties by "
                "E215's rule on the declaration's floors (work/step1/bands.json 526e6c8b); over every case both price (twins included), REPORTED "
                "beside over the cases that are twins for neither",
        'by_construction_declared_now': ["'MM1-v3.2 + AF4 + mesh' = 'MM1-v3.2 + mesh' at every E223 case: its tests repeat mesh's",
                                         "the reference's H2 is MM1-v3.2's counter mean: its H2 test vs MM1-v3.2 reads NO DATA (no untied case)",
                                         "E1 (W given t) equals MM1-v3.2's for all three columns: no E1 comparison is made for them",
                                         "at the full-chip cases mesh is MM1-v3.2 to the last bit, and the reference is MM1-v3.2 wherever it is out of scope: "
                                         "those cases tie"],
        'verdicts': 'each comparison a verdict of its own, never part of PASS; the reference never a candidate'},
    'reported_beside': "the declaration's section e (classes, held-out sets, MASKE221 with part A's cells on it alone and outside it, mask ladders: "
                       "measured and forecast subset/full ratios, the governed clock) with the three columns in each, REPORTED",
    'pass_rule': "unchanged (part A on MM1-v3.2, the declaration's bands); part_A_others_REPORTED gains the three columns, REPORTED, deciding nothing",
    'label_rule': "the declaration's section g with this amendment's FROZEN.txt for the three columns: a session is BLIND for them when the "
                  "amendment's FROZEN.txt sha256 lines were posted on #16 before the session's first datum; UNREAD if its first datum precedes that "
                  "post and no lab lane read its data before it; else POST-READ. If the amendment is not posted before E223's first datum it lapses: "
                  "the three columns are scored post hoc, labelled so",
    'nominal': {'conditions': "the declaration's section h unchanged: aifoundry1 card 1 600 MHz, 0.517 V, 60 C; aifoundry1 card 0 and aifoundry2 "
                              "card 0 800 MHz, the model's own volts at f, 55 C",
                'files': 'forecasts-nominal-e223-amend1.csv and .json: one forecast a case and model for every case, the three amended columns; '
                         "MM1-v3.2's column is the declaration's frozen one (re-made and checked equal at every case)"},
    'earlier_reads': {
        'E223_data': 'none read: no EE/sessions/ on any box, no ssh call, no data folder named for E223',
        'e223_releases_at_amendment': {'sha256': sha(REL), 'lines': rel_lines, 'claim_files': claims},
        'this_lane': "the frozen declaration, its scripts and work copy; mask-mesh's and mask-ceiling's frozen files, READMEs, lane logs and "
                     "results; probe p01 (the walk's and the ceiling's feature times at 5 E223 configurations, no forecast) and probe p02 (a code "
                     "test of s03_forecast.py on 31 of the 695 cases: only its checks, scopes and factor ranges printed, its output deleted) ran "
                     "before this amendment and chose nothing in it",
        'mask_ceiling_readme': "the posted FROZEN.txt's README bytes (66297333) are not on disk: the land carries the 02:22:21 text (4a575a33; its "
                               "lane's log: section 3b added, no number changed); the call form is read from it and from mask_ceiling.py's own "
                               "docstring (equal under both lines)",
        'mesh_cache': f"{CHK.get('mesh_cfg_missing', 119)} of E223's 162 mesh configurations (arm, mask, with their full-chip references) are not in "
                      "features-mesh.json's 600: the frozen walk makes them at forecast time, as its README says; the walk re-makes cached "
                      "configurations' features bit for bit (checked in p02 and in the run)",
        'fit_inclusion': {t: {'file': v['file'], 'sha256': v['sha256'], 'points': v['points'], 'e223_ids': len(v['e223_ids'])} for t, v in INC.items()}},
}
md = f"""# decl-e223 AMENDMENT 1 (dated): mesh and the mask ceiling join the lab's blind test of E223 as REPORTED, before any E223 datum

*Lane amend-e223 (round Q239a), aifoundry2's desk; written {WRITTEN}, Pacific time. Desk only: no card, no ssh, no simulator, no commit.
Interpreter: /usr/bin/python3 3.12.3, -I -B, single-threaded, every numerical step one slot job. New files beside the frozen declaration
(decl-e223's FROZEN.txt {CHK['decl_e223_FROZEN_sha256'][:8]}..., frozen 02:22:09 PST, posted on #16 at 02:23:46 PST): no frozen file is
edited. Labels as the declaration's: registered (this file), measured, desk, post hoc, held out, blind; REPORTED = printed beside, deciding
nothing.*

**Why an amendment.** The declaration's own rule (its Q238_read): "A Q238 candidate that qualifies only after this read is not in this
freeze: it can be scored on E223 only by a dated amendment hashed before E223's first datum, else as UNREAD". Two Q238 freezes qualified
after its 02:19:24 PST read. W/out/orch/q238-frozen-posts.txt read again at {CHK['q238_posts']['read_at']} (sha256 {CHK['q238_posts']['sha256'][:16]}...):
- **mask-mesh** 'MM1-v3.2 + mesh' (track M, KEPT by its declared rule): FROZEN.txt `{MESH_FZ}`, final 02:03:37 PST; its correct freeze
  line posted at 02:23:42 PST (#1.30.1.2.1.1.1.1.1.1.2, the correction: the 02:03:18 post named the superseded first write 3d4942fa). On
  disk = posted = the land's FROZEN.txt; all {CHK['mesh']['lane_files']['n']} files it lists re-hashed equal; the land's SHA256SUMS
  {CHK['mesh']['land_SHA256SUMS']['ok']}/{CHK['mesh']['land_SHA256SUMS']['ok']} OK; every file this amendment calls (mesh_term.py,
  mesh_l3.py, compose_af4.py, params-mesh.json, features-mesh.json) equal to FROZEN.txt as run.
- **mask-ceiling** 'MM1-v3.2 + mask-ceiling' (track C, a nonparametric REFERENCE, REPORTED, never a model candidate): the posted freeze line
  (#1.30.1.2.1.1.1.1.1.1.1, 02:21:44 PST) names FROZEN.txt `{CEIL_FZ}` (its 02:21:13 write, kept as FROZEN.txt.superseded-022113). Its
  lane rewrote FROZEN.txt at 02:22:21 PST (`{CEIL_DISK[:16]}...`, not posted at this read), changing only
  {', '.join(CHK['ceiling']['posted_vs_disk_differ_only'])}; every file this amendment calls (mask_ceiling.py, params-mask-ceiling.json,
  scripts/r_common.py, rf_core.py, f01_features.py) is equal under both lines, so its forecasts are the same under either. This amendment
  names the posted line.

## 0. What changes, and what does not

- **Added: three REPORTED columns, deciding nothing:** 'MM1-v3.2 + mesh', 'MM1-v3.2 + AF4 + mesh' (by construction, no refit) and the
  reference 'MM1-v3.2 + mask-ceiling'. Unchanged: the pass rule (part A on MM1-v3.2), the bands and ties, D0-D2, D4, D5, the label rule for
  every declared column, the nominal conditions, the case list (695 cases, 803 runs; decl-e223 work/step1/runs-listed.json ed4595b1...)
  and every model the declaration names.
- **MM1's domain:** every E223 case is in each added column's domain: mesh acts at the {n_sub} subset-mask cases of rgm136 gemmL and is
  MM1-v3.2 to the last bit at the {len(CASES) - n_sub} full-chip cases; the reference acts at {n_ceil} cases (rgm136 gemmL with MB x NB >= 2
  at a shire subset) and its factor is exactly 1 at the other {len(CASES) - n_ceil}; AF4 acts at no E223 case (no gemmLnc arm). OUT OF
  DOMAIN: none.

## The added models

- **MM1-v3.2 + mesh (REPORTED)**: Q238's mask-mesh, its land folder copied unchanged to work/lab/tools/matmul/mm1/v3.4-cands/mesh/, at
  its frozen constants {json.dumps(MP['constants'])} (variant '{MP.get('variant')}') on MM1-v3.2 4e386f75 unchanged, called as its README's
  section 6 says: `mesh_term.Model(json.load(open('out/params-mesh.json')), 'out/features-mesh.json').time_many(points)` with
  MASK_MESH_REPO = the lab copy, points {{arm, kernel 'rgm136', fmt, mask, f}}. The record: T = time_many's op time; cycles an op = T x f;
  the counter's mean = cycles / MM1-v3.2's rho; seconds a pass = ops x T; W over idle at a measured t = MM1-v3.2's A + B / t (so E1 is
  MM1-v3.2's); with t forecast at this T (E2, E4, H5). Its features are configuration-only (arm and mask: the walk's sets and latencies); a
  configuration missing from its frozen features cache is made by its own mesh_l3.simulate (no constant), as the README says.
- **MM1-v3.2 + AF4 + mesh (REPORTED, by construction, no refit)**: `scripts/compose_af4.py composed(specs, mesh)` unchanged (README
  section 6). AF4 acts at no E223 case, so it equals 'MM1-v3.2 + mesh' at every case (checked to 1e-12 at the nominal footing): declared now,
  its tests repeat mesh's.
- **MM1-v3.2 + mask-ceiling (a REFERENCE, REPORTED, never a model candidate)**: Q238's mask-ceiling, its land folder copied unchanged to
  work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/ (the all-data forest, params-mask-ceiling.json f991b637...), called as its README's
  section 7 says: `python3 -I -B mask_ceiling.py --points <points.json> --out <factors.json>`: the factor (1 off its scope); the forecast is
  MM1-v3.2's own row with T_op_us, cycles_per_op_wall and seconds_per_gemm times the factor, the counter's mean MM1-v3.2's (the reference
  forecasts none), W over idle at a measured t = MM1-v3.2's A + B / t, with t forecast at the new T. Its features: the configuration (arm,
  mask, format) and the clock f.

## The forecast procedure

- **footing_1_measured** (the primary footing): the declaration's, unchanged: each frozen predictor at each run's measured conditions,
  read from the data's start-of-run records only (the primary view's kclock_mhz; card 1 0.517 V, the governed cards rails.minion.mV /
  1000; die_start_c, 50 C when absent). The callers: this lane's `scripts/s03_forecast.py` `forecast_amend1(cases, cond)`, the same code
  that makes this amendment's nominal forecasts (cond per run {{'f', 'V', 't0_c'}}), each term on MM1-v3.2's forecast at the same conditions.
- **fields read before scoring** and **order**: the declaration's: after the data, the conditions read, then the measured-conditions
  forecasts of every column (these three with them) hashed, then the scorer hashed, then the read and the scores.
- **footing_2_nominal**: forecasts-nominal-e223-amend1.csv and .json, frozen with this amendment (section h).

## c. The metric

- The declaration's: error = forecast / measured - 1; rms % and signed mean (bias) %; watts cases rms and mean in W; a case's error = the
  mean of its runs' errors.
- **twins**: per column by the declaration's own rule: MM1-v3.2's keys UNION every point its term's fit read (mesh: out/points-mesh.json,
  {INC['mesh']['points']} points, {INC['mesh']['sha256'][:8]}...; the reference: inputs/points_all.json, {INC['mask-ceiling']['points']} points,
  {INC['mask-ceiling']['sha256'][:8]}...; 'MM1-v3.2 + AF4 + mesh' AF4's data/s01_points.json too), time and (with the kind) energy alike,
  a conservative twin: work/step2/twin-keys-amend1.json. At the nominal clocks (a preview; the measured clock decides), time / energy twins
  of 695: {'; '.join(f'{m} {v[0]} / {v[1]}' for m, v in prev.items())}. No E223 point is in any fit (0 E223 ids in either points file).

## d. The comparisons

- **D3a_masks_REPORTED** (deciding nothing; the declaration's D3_masks_REPORTED form exactly): on THE PLACEMENT CLASS (PLACE, {n_place}
  cases), each of 'MM1-v3.2 + mesh', 'MM1-v3.2 + AF4 + mesh' and the reference 'MM1-v3.2 + mask-ceiling' vs MM1-v3.2 on H1 (wall), H2
  (counter mean), H3 (seconds) and H5 (J over idle with t forecast), per card and pooled; the same on every subset-mask case ({n_sub}), on
  MASKE221 ({n_m221}) and on each held-out set ({HO}), REPORTED.
- **D3b_beside_REPORTED**: 'MM1-v3.2 + mesh' vs 'MM1-v3.2 + posimb-mask' and vs 'MM1-v3.2 + posimb'; the reference vs 'MM1-v3.2 + mesh' and
  vs 'MM1-v3.2 + posimb-mask'; the same cases, quantities and test.
- **test**: the declaration's: the exact two-sided sign test (binomial at 1/2) on the untied cases, alpha 0.05: A BETTER if p < 0.05 and A is
  closer in more cases, B BETTER the other way, NOT DECIDED otherwise, TOO FEW under 10 untied cases, NO DATA with none; per case d =
  |ln(1 + e_B)| - |ln(1 + e_A)| (at a watts case |dW_B| - |dW_A| in W); ties by E215's rule on the declaration's floors (work/step1/bands.json
  526e6c8b); over every case both price (twins included), REPORTED beside over the cases that are twins for neither.
- **declared now, by construction**: 'MM1-v3.2 + AF4 + mesh' = 'MM1-v3.2 + mesh' at every E223 case, so its tests repeat mesh's; the
  reference's H2 is MM1-v3.2's counter mean, so its H2 test vs MM1-v3.2 reads NO DATA (no untied case); E1 (W given t) is MM1-v3.2's for all
  three columns, so no E1 comparison is made for them; at the full-chip cases mesh is MM1-v3.2 to the last bit, and the reference is
  MM1-v3.2 wherever it is out of scope: those cases tie.
- **verdicts**: each comparison a verdict of its own, never part of PASS; the reference is never a candidate: its rows bound what a mask
  term built from its features reaches, printed as a reference.

## e. Reported beside (deciding nothing)

- The declaration's section e with the three columns in each: the classes (the placements first), the 15 held-out sets, MASKE221 (part A's
  cells on it alone and on every case outside it), the mask ladders (measured and forecast subset/full ratios per model) and the governed
  clock, REPORTED.

## f. The pass rule

- Unchanged: part A on MM1-v3.2 by the declaration's rule form and bands decides PASS / FAIL / NOT DECIDED. part_A_others_REPORTED gains
  the three columns (the same rules, REPORTED, deciding nothing).

## g. The label rule

- The declaration's, with this amendment's FROZEN.txt for the three columns: a session is BLIND for them when this amendment's FROZEN.txt
  sha256 lines were posted on #16 before the session's first datum (its first card command, the session's own log); UNREAD when its first
  datum precedes that post and no lab lane read its data before the post; else POST-READ (REPORTED). If this amendment is not posted before
  E223's first datum it lapses, and the three columns are scored post hoc, labelled so.

## h. The nominal footing

- The declaration's section h conditions, unchanged: aifoundry1 card 1 600 MHz, 0.517 V, die at start 60 C; aifoundry1 card 0 and
  aifoundry2 card 0 800 MHz, the model's own volts at f, 55 C.
- **files**: forecasts-nominal-e223-amend1.csv and .json: one forecast a case and model for every case (every run of a case at the same
  nominal conditions), the three added columns, each by its frozen code unchanged; MM1-v3.2's column stays the declaration's frozen one
  (re-made by mm1_v32.Model.predict_many at the declaration's specs and checked equal at every case before any output).

## i. Earlier reads, disclosed

- **E223 data**: none read: this lane opened no EE/sessions/ folder on any box, made no ssh call and opened no data folder named for E223.
  W/out/orch/e223-releases.txt at this amendment ({sha(REL)[:16]}...) holds the proposal (#16 01:25:49) and aifoundry2's push (#16.1.1
  01:55:59, "no session sends a card command before the lab's E223 freeze post"), no claim and no release; claim files: {claims or 'none'}.
- **this lane**: read the frozen declaration, its scripts and its work copy (copied to work/lab); mask-mesh's and mask-ceiling's frozen
  files, READMEs, lane logs and results; probe p01 (the walk's and the ceiling's feature-making times at 5 E223 configurations, no forecast)
  and probe p02 (a code test of scripts/s03_forecast.py on 31 of the 695 cases: only its checks, scopes and factor ranges printed, its
  output deleted) ran before this amendment and chose nothing in it.
- **mask-ceiling's README**: the posted FROZEN.txt's README bytes (66297333...) are not on disk: the land carries the 02:22:21 text
  (4a575a33...; its lane's log: section 3b added, no number changed); the call form is read from it and from mask_ceiling.py's own
  docstring, which is equal under both lines.
- **mesh's features cache**: 119 of E223's 162 mesh configurations (arm and mask, with their full-chip references) are not among
  features-mesh.json's 600: the frozen walk makes them at forecast time, as its README says; the walk re-makes cached configurations'
  features bit for bit (checked in p02 and in the run).

## The inputs, by sha256

"""
INPUTS = ['work/step1/frozen-checks.json', 'work/step1/decl-e223-FROZEN.txt', 'work/step1/mask-mesh-FROZEN.txt',
          'work/step1/mask-ceiling-FROZEN-posted-1649ba5b.txt', 'work/step1/mask-ceiling-FROZEN-disk.txt',
          'work/step1/q238-frozen-posts-at-amendment.txt', 'work/step2/twin-keys-amend1.json',
          'work/lab/tools/matmul/mm1/v3.4-cands/mesh/FROZEN.txt', 'work/lab/tools/matmul/mm1/v3.4-cands/mesh/SHA256SUMS',
          'work/lab/tools/matmul/mm1/v3.4-cands/mesh/README.md', 'work/lab/tools/matmul/mm1/v3.4-cands/mesh/scripts/mesh_term.py',
          'work/lab/tools/matmul/mm1/v3.4-cands/mesh/scripts/mesh_l3.py', 'work/lab/tools/matmul/mm1/v3.4-cands/mesh/scripts/compose_af4.py',
          'work/lab/tools/matmul/mm1/v3.4-cands/mesh/out/params-mesh.json', 'work/lab/tools/matmul/mm1/v3.4-cands/mesh/out/features-mesh.json',
          'work/lab/tools/matmul/mm1/v3.4-cands/mesh/out/points-mesh.json',
          'work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/FROZEN.txt', 'work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/SHA256SUMS',
          'work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/README.md', 'work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/mask_ceiling.py',
          'work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/params-mask-ceiling.json',
          'work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/scripts/r_common.py', 'work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/scripts/rf_core.py',
          'work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/scripts/f01_features.py',
          'work/lab/tools/matmul/mm1/v3.4-cands/mask-ceiling/inputs/points_all.json',
          'work/lab/tools/matmul/mm1/v3.2/SHA256SUMS', 'work/lab/tools/matmul/mm1/v3.2/out/mm1_v32_params.json', 'work/lab/tools/matmul/mm1/v3.2/mm1_v32.py',
          'work/lab/tools/matmul/mm1/v3.3-cands/gemmlnc-af4/SHA256SUMS',
          'scripts/p01_time.py', 'scripts/s01_check.py', 'scripts/s02_amend.py', 'scripts/s03_forecast.py']
J['inputs_sha256'] = {p: sha(os.path.join(L, p)) for p in INPUTS}
J['inputs_sha256_outside_lane'] = {'OUT/decl-e223/work/step1/runs-listed.json': sha(os.path.join(DECL, 'work', 'step1', 'runs-listed.json')),
                                   'OUT/decl-e223/work/step1/twin-keys.json': sha(os.path.join(DECL, 'work', 'step1', 'twin-keys.json')),
                                   'OUT/decl-e223/work/step1/bands.json': sha(os.path.join(DECL, 'work', 'step1', 'bands.json')),
                                   'W/out/orch/e223-releases.txt': sha(REL)}
md += ''.join(f'- `{v}`  {k}\n' for k, v in J['inputs_sha256'].items())
md += ''.join(f'- `{v}`  {k}\n' for k, v in J['inputs_sha256_outside_lane'].items())
md += '\nSPDX-License-Identifier: Apache-2.0\n'
MDF = os.path.join(L, 'DECLARED-blind-e223-amendment-1.md')
JF = os.path.join(L, 'DECLARED-blind-e223-amendment-1.json')
assert not os.path.exists(MDF) and not os.path.exists(JF), 'the amendment exists already: never rewritten'
open(MDF, 'w').write(md)
json.dump(J, open(JF, 'w'), indent=1, sort_keys=True)
os.chmod(MDF, 0o444)
os.chmod(JF, 0o444)
print('twin preview', json.dumps(prev), 'scope mesh', n_sub, 'ceiling', n_ceil, 'PLACE', n_place, 'MASKE221', n_m221)
print(sha(TWF), 'work/step2/twin-keys-amend1.json')
print(sha(MDF), 'DECLARED-blind-e223-amendment-1.md')
print(sha(JF), 'DECLARED-blind-e223-amendment-1.json')
print('written', WRITTEN)
