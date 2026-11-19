#!/usr/bin/env python3
"""blind-v3-e212s3 step 1: the machine-readable declaration DECLARED-blind-s3.json, built beside DECLARED-blind-s3.md before any datum of
E212 a2c0-S3's re-run exists. Reads only frozen files (the archive of b1493082, E212's registration) and this lane's desk records.

    /usr/bin/python3 -I -B s01d_declare.py --lane <lane folder>
"""
import argparse
import hashlib
import json
import os
import sys


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lane', required=True)
    a = ap.parse_args()
    L = os.path.abspath(a.lane)
    V3 = os.path.join(L, 'work', 'lab-b149', 'tools', 'matmul', 'mm1', 'v3')
    REG = os.path.join(L, 'work', 'lab-head', 'tools', 'claims-v3', 'e212')
    tw = json.load(open(os.path.join(L, 'work', 's3-arms-twins.json')))
    t4 = json.load(open(os.path.join(L, 'work', 'test-s4', 'blind_v3_e212s4.json')))
    frozen = {}
    for rel in ('out/mm1_v3_e212_s3s4.csv', 'out/mm1_v3_params.json', 'mm1_v3.py', 'engine_v3.py', 'energy_v3.py', 'mm1_core_v3.py', 'kinds_v3.py',
                'inputs/census/census-v3.json', 'data_v3.py', 'unread_v2_e212.py', 'out/holdout_v3.json', 'fit_v3.py', 'postcheck_v3.py',
                'inputs/e212/sched__a2c0-S3.json', 'SHA256SUMS'):
        frozen['tools/matmul/mm1/v3/' + rel] = sha(os.path.join(V3, rel))
    frozen['tools/matmul/mm1/v2/SHA256SUMS'] = sha(os.path.join(V3, '..', 'v2', 'SHA256SUMS'))
    D = {
        'what': 'blind-v3-e212s3 (Q223): the declaration, before any datum of E212 aifoundry2 card 0 S3\'s re-run (Wed 18 Nov 2026), of the blind score of MM1-v3\'s frozen S3 forecasts against MM1-v2\'s',
        'companion_md': 'DECLARED-blind-s3.md', 'companion_md_sha256': sha(os.path.join(L, 'DECLARED-blind-s3.md')),
        'interpreter': '/usr/bin/python3 ' + sys.version.split()[0],
        'frozen_in': {'commit': 'b149308280a73396516937304037af57a5563c16', 'committed': '2026-11-17 20:52:46 PST', 'pushed': '2026-11-17 20:52:51 PST',
                      'ancestor_of_main_at_declaration': 'fcbf60c4fa590b5a88b8e35ba8a105a81854465d',
                      'v3_sha256sums_ok': '170/170', 'v2_sha256sums_ok': '114/114', 'files_sha256': frozen},
        'forecast_file': {'path': 'tools/matmul/mm1/v3/out/mm1_v3_e212_s3s4.csv', 'sha256': frozen['tools/matmul/mm1/v3/out/mm1_v3_e212_s3s4.csv'],
                          'readme_section_6_sha256': '002226651404b291739894cc187d528e68b741d4e4df8b8d53d37172f4933faf', 's3_rows': 46, 'clock': '799 MHz given'},
        'registered_schedule': {'path': 'tools/claims-v3/e212/proposal/src/sched/a2c0-S3.json',
                                'sha256': sha(os.path.join(REG, 'proposal', 'src', 'sched', 'a2c0-S3.json')),
                                'registration_commit': 'c83a29d1', 'registration_sums_ok_at_main_fcbf60c4': '87/87',
                                'runs': tw['n_runs'], 'arm_runs': tw['n_arm_runs'], 'anchor_runs': tw['n_anchor_runs'], 'nulls': tw['n_null'],
                                'non_null_arms': tw['n_arms_nonnull']},
        'arms_against_forecasts': {'arms_without_forecast': tw['arms_without_forecast'], 'forecasts_without_arm': tw['forecasts_without_arm'],
                                   'rows_not_matching_key': tw['rows_not_matching_key'], 'energy_forecast_arms': tw['n_energy_forecast'],
                                   'time_only_arms': tw['n_arms_nonnull'] - tw['n_energy_forecast'],
                                   'desk_record': 's3-arms-twins.json', 'desk_record_sha256': sha(os.path.join(L, 'work', 's3-arms-twins.json'))},
        'arms': [{k: r[k] for k in ('first_i', 'arm_label', 'role', 'n_runs', 'arm', 'fmt', 'kind', 'mask', 'block', 'twin_time_800', 'twin_energy_800',
                                    'energy_forecast', 'frozen_v3_cycles_per_op_wall', 'frozen_v3_cycles_per_op_mean', 'frozen_v3_A_W', 'frozen_v3_B_W_us',
                                    'frozen_v3_W_over_idle', 'frozen_v2_cycles_per_op_wall', 'frozen_v2_cycles_per_op_mean', 'frozen_v2_A_W',
                                    'frozen_v2_B_W_us', 'frozen_v2_W_over_idle')} for r in tw['arms']],
        'quantities': {'form': 'MM1-v3 README section 5 (E212 a2c0-S4), unread_v3_e212s4.py\'s code',
                       'loader': 'data_v3.mms_runs with data_v3.e212_kind on the committed data file: one record a run, nulls out, primary view win; no run removed by hand',
                       'call': 'each model at the run\'s measured kernel clock, the view\'s measured minion volts, the run\'s die at start; MM1-v3 by mm1_v3.Model (= its fit code, checked); MM1-v2 by unread_v2_e212.call',
                       'list': ['wall cycles an op', 'counter mean cycles an op', 'W over idle given measured seconds (A + B / t_meas), at >= 3 W; watts below',
                                'J over idle with t forecast (>= 3 W)', 'J at rest given t', 'J at rest with t forecast'],
                       'granularity': ['per run', 'per case (card, arm, format, kind, mask; mean of its runs)'],
                       'energy_kinds': ['random', 'zeros', 'ones']},
        'metric': {'error': 'forecast / measured - 1', 'stats': ['rms %', 'signed mean %', 'watts rms and bias below 3 W'],
                   'per_case_table': True, 'head_to_head': {'ties_cycles': 0.005, 'ties_W': 0.01},
                   'twins': {'rule': 'postcheck_v3.cfg_t (card, kernel, arm, format, mask, clock to 25 MHz; kind-blind) and cfg_e (adds the kind) against MM1-v3\'s all-data fit set; decided at the case\'s measured clock',
                             'at_800MHz_expected': {'time_twin_cases': tw['twin_time_800_cases'], 'cases': tw['n_arms_nonnull'],
                                                    'time_twin_configurations': tw['twin_time_800_distinct_configurations'],
                                                    'distinct_configurations': tw['distinct_time_configurations_kind_blind'],
                                                    'energy_twin_cases_with_energy_forecast': tw['twin_energy_800_cases_with_energy_forecast']},
                             'splits': ['wall cycles (time configuration)', 'W given t (time configuration)', 'W given t (energy configuration, with the kind)']}},
        'comparisons': {'primary': 'MM1-v2 as frozen (tools/matmul/mm1/v2 at 3ca4b717, pins in unread_v2_e212.py)', 'beside': ['v2form (all-data constants, holdout_v3.json)',
                        'the literal frozen CSV numbers at 799 MHz given (MM1-v3 and MM1-v2): wall, counter mean, W given t']},
        'reported': {'pass_rule': None, 'figures': 'REPORTED',
                     'label_rule': 'BLIND if b1493082\'s push (2026-11-17 20:52:51 PST) and this declaration\'s logged sha256 both precede the re-run\'s first card command (the session log\'s first line touching the card at or after its session start; T0 the conservative bound); else REPORTED, not blind'},
        'data': {'read_only_after': 'data-e212s3\'s data commit is on GitHub main',
                 'path': 'docs/reports/data/2026-11-18-e212-mmsweep2-a2c0-S3/data-e212-a2c0-S3.json',
                 'fallback': 'the folder\'s single data-e212-*S3*.json, the difference recorded',
                 'gaps': 'an arm with no scored run is NOT RUN; any missing -> SCORED WITH GAPS; no data commit by 2026-11-19 14:00 PST -> NOT SCORED'},
        'scorer': {'file': 's03_score.py', 'sha256': sha(os.path.join(L, 'scripts', 's03_score.py')),
                   'run': '/usr/bin/python3 -I -B s03_score.py --v3 <archive of b1493082>/tools/matmul/mm1/v3 --data <the committed file> --session a2c0-S3 --label BLIND|REPORTED --out <dir>',
                   'desk_test_on_S4': {'label': t4['label'], 'data_sha256': t4['data_sha256'], 'per_case': t4['per_case'], 'per_run': t4['per_run'],
                                       'head_to_head': t4['head_to_head_per_case_v3_vs_v2'], 'twins_wall_time_config': t4['twins']['wall cycles (time configuration)'],
                                       'predictor_equals_fit_code': t4['v3_predictor_equals_fit_code'],
                                       'outputs_sha256': {fn: sha(os.path.join(L, 'work', 'test-s4', fn)) for fn in sorted(os.listdir(os.path.join(L, 'work', 'test-s4')))}}},
        'no_sealed_number': 'the model session\'s sealed S3 forecasts (E212 freeze lines; v3.3 seal 6842eca5..., registered fcbf60c4) are known by sha256 only and are not used',
    }
    p = os.path.join(L, 'DECLARED-blind-s3.json')
    json.dump(D, open(p, 'w'), indent=1, sort_keys=True)
    print(sha(p), 'DECLARED-blind-s3.json')
    print(D['companion_md_sha256'], 'DECLARED-blind-s3.md')


if __name__ == '__main__':
    main()
