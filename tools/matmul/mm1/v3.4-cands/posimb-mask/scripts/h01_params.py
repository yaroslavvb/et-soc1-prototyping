#!/usr/bin/env python3
"""mask-posimb (Q238) h01: the term's parameters and outputs into the land folder (new files): params-posimb-mask.json (the all-data
constants of the declared fit, work/fit_results.json, with the declaration's and the inputs' sha256 and MM1-v3.2's pins), and out/ (the
features, the fit record, the held-out record, the points, the bases' check record). Desk; stdlib. No number is re-fitted here."""
import hashlib
import json
import os
import shutil

LANE = os.environ['MASKPOS_LANE']
LAB = os.path.join(LANE, 'work/lab')
LAND = os.path.join(LANE, 'land/tools/matmul/mm1/v3.4-cands/posimb-mask')
DECL_SHA = 'b59f1c4dc5ff1b67483face805216585cfca94b2fe709700c458ff2ca4714f40'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    assert sha(os.path.join(LAND, 'DECLARED-posimb-mask.md')) == DECL_SHA
    F = json.load(open(os.path.join(LANE, 'work/fit_results.json')))
    assert F['declaration_sha256'] == DECL_SHA
    a = F['constants_all_data']['cand']
    kept = bool(F['keep_rule']['KEPT'])
    par = {'label': 'MM1-v3.2 + posimb-mask' if kept else 'MM1-v3.2 + posimb-mask (rejected candidate)', 'kept_by_declared_rule': kept,
           'constants': {'a_hop': a[0], 'a_lag': a[1], 'a_al': a[2]},
           'form': 'T = T_v32 x clip(1 + a_hop e G1core + a_lag e LAGcore + a_al e A1, 0.3, 3.0) at rgm136 gemmL subset points; mean x clip(1 + '
                   'a_hop e G1core + a_al e A1, 0.3, 3.0); energy MM1-v3.2 affine at the term op time; MM1-v3.2 elsewhere',
           'fit': 'two-stage on MM1-v3.2 all-data base (its constants unchanged): posimb fit_consts (linear least squares of rho (1 + Phi a) - 1) '
                  'over every point through E224 but E146 store rungs (work/points_all.json, 4311 points)',
           'declaration_sha256': DECL_SHA, 'fit_results_sha256': sha(os.path.join(LANE, 'work/fit_results.json')),
           'inputs_sha256': F['inputs'],
           'base_model': {'MM1-v3.2': 'tools/matmul/mm1/v3.2 (declaration f8e00a57, model 4e386f75)',
                          'mm1_v32_params.json_sha256': sha(os.path.join(LAB, 'tools/matmul/mm1/v3.2/out/mm1_v32_params.json')),
                          'time_fit_record_sha256': sha(os.path.join(LAB, 'tools/matmul/mm1/v3.2/out/fits/time_T5r+G0+n32.json'))},
           'features': {'posimb': 'tools/matmul/mm1/v3.3-cands/posimb/scripts/f02_private.py (landed 183a354a, as run 1594dd8b)',
                        'A1': '1 when no active shire s has (s >> 2) & 3 == s & 3, else 0'},
           'af4': {'folder': 'tools/matmul/mm1/v3.3-cands/gemmlnc-af4',
                   'fit_record_sha256': sha(os.path.join(LAB, 'tools/matmul/mm1/v3.3-cands/gemmlnc-af4/data/fit-record.json')),
                   's02_fit.py_sha256': sha(os.path.join(LAB, 'tools/matmul/mm1/v3.3-cands/gemmlnc-af4/scripts/s02_fit.py'))},
           'interpreter': F['interpreter'], 'numpy': F['numpy']}
    json.dump(par, open(os.path.join(LAND, 'params-posimb-mask.json'), 'w'), indent=1)
    os.makedirs(os.path.join(LAND, 'out'), exist_ok=True)
    for fn in ('private_shared.json', 'fit_results.json', 'heldout_points.csv', 'points_all.json', 'base_meta.json'):
        shutil.copyfile(os.path.join(LANE, 'work', fn), os.path.join(LAND, 'out', fn))
    print(json.dumps(par, indent=1))
    for fn in sorted(os.listdir(os.path.join(LAND, 'out'))):
        print(sha(os.path.join(LAND, 'out', fn)), 'out/' + fn)
    print(sha(os.path.join(LAND, 'params-posimb-mask.json')), 'params-posimb-mask.json')


if __name__ == '__main__':
    main()
