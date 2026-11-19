#!/usr/bin/env python3
"""blind-v3-e212s3 step 4: the land's README.md from the score (s03_score.py's JSON and cases CSV), the order check (s02_order.py's JSON),
the lane's hash-and-time records (a JSON list written by the land builder) and a hand-written summary (markdown). Desk; reads only.

    /usr/bin/python3 -I -B s04_readme.py --score <blind_v3_e212s3.json> --cases <blind_v3_e212s3_cases.csv> --order <order-s3.json>
                                         --hashes <hash-order.json> --summary <summary.md> --tail <tail.md>
                                         --arms <s3-arms-twins.json> --out <README.md>
"""
import argparse
import csv
import json


def f(s, unit='%'):
    if not s:
        return '-'
    if 'rms_W' in s:
        return f"{s['rms_W']:.3f} W ({s['bias_W']:+.3f} W), {s['n']}"
    return f"{s['rms_pct']:.2f}% ({s['bias_pct']:+.2f})"


def n_of(*ss):
    for s in ss:
        if s:
            return s['n']
    return 0


def main():
    ap = argparse.ArgumentParser()
    for k in ('score', 'cases', 'order', 'hashes', 'summary', 'tail', 'out', 'arms'):
        ap.add_argument('--' + k, required=True)
    a = ap.parse_args()
    ARMS = json.load(open(a.arms))['arms']
    S = json.load(open(a.score))
    O = json.load(open(a.order))
    H = json.load(open(a.hashes))
    C = list(csv.DictReader(open(a.cases)))
    lab = S['label']
    pc, pr, lit, tw = S['per_case'], S['per_run'], S['literal_frozen_799MHz_per_case'], S['twins']
    o = []
    o.append(f"# MM1-v3 scored {lab} on E212 aifoundry2 card 0 S3, the re-run of Wed 18 Nov 2026 (round Q223, lane blind-v3-e212s3)")
    o.append('')
    o.append(open(a.summary).read().rstrip('\n'))
    o.append('')
    o.append('## 0. The order of the hashes and the times (Pacific)')
    o.append('')
    o.append('| when (PST) | what | sha256 |')
    o.append('|---|---|---|')
    for h in H:
        o.append(f"| {h['when']} | {h['what']} | {h.get('sha256', '')} |")
    o.append('')
    ck = O.get('checks', {})
    o.append(f"The order check (`order-s3.json`): b1493082's push before the re-run's first card command **{ck.get('push_before_first_card_command')}**; "
             f"the declaration's logged time before it **{ck.get('declared_before_first_card_command')}**; both before the session start "
             f"(T0) **{ck.get('push_before_T0')}** / **{ck.get('declared_before_T0')}**; no session-log line older than b1493082's push "
             f"**{ck.get('no_session_line_older_than_push')}**. Label: **{O.get('label')}**.")
    o.append('')
    o.append(f"## 1. The scores ({lab}; REPORTED: no pass rule is registered for S3)")
    o.append('')
    o.append('Each model called at the run\'s measured kernel clock, minion volts and die at start (MM1-v3\'s README section 5 form). Error = '
             'forecast / measured - 1; rms in %, the signed mean in brackets; W over idle and J over idle scored at 3 W and above.')
    o.append('')
    o.append(f"| E212 a2c0-S3, {lab} | MM1-v3 (frozen, b1493082) | MM1-v2 (frozen, 3ca4b717) | v2form (refitted, all data; beside) |")
    o.append('|---|---|---|---|')
    o.append(f"| wall cycles, {n_of(pc['v3']['wall'])} cases | **{f(pc['v3']['wall'])}** | {f(pc['v2']['wall'])} | {f(pc['v2form']['wall'])} |")
    o.append(f"| counter mean, {n_of(pc['v3']['counter_mean'])} cases | **{f(pc['v3']['counter_mean'])}** | {f(pc['v2']['counter_mean'])} | - |")
    o.append(f"| W over idle given t, {n_of(pc['v3']['W_given_t_ge3W'])} cases | **{f(pc['v3']['W_given_t_ge3W'])}** | {f(pc['v2']['W_given_t_ge3W'])} | {f(pc['v2form']['W_given_t_ge3W'])} |")
    if pc['v3'].get('W_under_3W_watts'):
        o.append(f"| W over idle under 3 W (watts, cases) | {f(pc['v3']['W_under_3W_watts'])} | {f(pc['v2']['W_under_3W_watts'])} | {f(pc['v2form']['W_under_3W_watts'])} |")
    o.append(f"| J over idle with t forecast, {n_of(pc['v3']['J_over_idle_t_forecast_ge3W'])} cases | **{f(pc['v3']['J_over_idle_t_forecast_ge3W'])}** | {f(pc['v2']['J_over_idle_t_forecast_ge3W'])} | {f(pc['v2form']['J_over_idle_t_forecast_ge3W'])} |")
    o.append(f"| J at rest given t, {n_of(pc['v3']['J_at_rest_given_t'])} cases | {f(pc['v3']['J_at_rest_given_t'])} | {f(pc['v2']['J_at_rest_given_t'])} | - |")
    o.append(f"| J at rest with t forecast, {n_of(pc['v3']['J_at_rest_t_forecast'])} cases | {f(pc['v3']['J_at_rest_t_forecast'])} | {f(pc['v2']['J_at_rest_t_forecast'])} | - |")
    nr = n_of(pr['v3']['wall'])
    ne = n_of(pr['v3']['J_at_rest_given_t'])
    o.append(f"| per run ({nr} runs; {ne} with energy): wall / counter mean / W given t / J at rest given t / J at rest t forecast | "
             f"{' / '.join(f(pr['v3'][k]) for k in ('wall', 'counter_mean', 'W_given_t_ge3W', 'J_at_rest_given_t', 'J_at_rest_t_forecast'))} | "
             f"{' / '.join(f(pr['v2'][k]) for k in ('wall', 'counter_mean', 'W_given_t_ge3W', 'J_at_rest_given_t', 'J_at_rest_t_forecast'))} | - |")
    h = S['head_to_head_per_case_v3_vs_v2']
    o.append(f"| per case, closer to measured (ties within 0.5% in cycles, 1% in W) | v3 {h['e_wall']['v3_closer']}, v2 {h['e_wall']['v2_closer']}, ties {h['e_wall']['ties']} (cycles); "
             f"v3 {h['e_w_given_t']['v3_closer']}, v2 {h['e_w_given_t']['v2_closer']}, ties {h['e_w_given_t']['ties']} (W) | | |")
    o.append('')
    o.append(f"MM1-v3's predictor equals its fit code on every case (op time max relative difference {S['v3_predictor_equals_fit_code']['max_rel_diff_T_op']:.1e}; "
             f"W {S['v3_predictor_equals_fit_code']['max_abs_diff_W_given_t_W']:.1e} W).")
    o.append('')
    o.append('**Configuration twins** (MM1-v3\'s postcheck rule, against its all-data fit set; clock to 25 MHz at the case\'s measured clock):')
    o.append('')
    o.append('| split | cases | MM1-v3 | MM1-v2 | v2form | closer v3 / v2 / ties |')
    o.append('|---|---|---|---|---|---|')
    for labx, key in (('wall cycles', 'wall cycles (time configuration)'), ('W given t (time configuration)', 'W given t (time configuration)'),
                      ('W given t (configuration and kind)', 'W given t (energy configuration, with the kind)')):
        for side, nm in (('twin', 'in the fit data'), ('no_twin', 'new')):
            d = tw[key][side]
            cl = tw[key]['closer_v3_v2_ties'][side]
            o.append(f"| {labx}, {nm} | {n_of(d['v3'])} | {f(d['v3'])} | {f(d['v2'])} | {f(d['v2form'])} | {cl[0]} / {cl[1]} / {cl[2]} |")
    o.append('')
    o.append('**The literal frozen numbers** of `out/mm1_v3_e212_s3s4.csv` (799 MHz given), against the same cases:')
    o.append('')
    o.append('| literal, 799 MHz given | MM1-v3 | MM1-v2 |')
    o.append('|---|---|---|')
    o.append(f"| wall cycles, {n_of(lit['v3']['wall'])} cases | {f(lit['v3']['wall'])} | {f(lit['v2']['wall'])} |")
    o.append(f"| counter mean, {n_of(lit['v3']['counter_mean'])} cases | {f(lit['v3']['counter_mean'])} | {f(lit['v2']['counter_mean'])} |")
    o.append(f"| W given t (the CSV's A + B / t_meas), {n_of(lit['v3']['W_given_t_ge3W'])} cases | {f(lit['v3']['W_given_t_ge3W'])} | {f(lit['v2']['W_given_t_ge3W'])} |")
    o.append('')
    scored = set()
    for r in C:
        scored.update(r['arm_labels'].split('+'))
    missing = [x['arm_label'] for x in ARMS if x['arm_label'] not in scored]
    extra = sorted(scored - {x['arm_label'] for x in ARMS})
    o.append(f"**Coverage:** {len(ARMS) - len(missing)} of the {len(ARMS)} declared arms have a scored case ({S['n_cases']} cases, "
             f"{S['n_runs_scored']} runs scored; {S['n_cases_energy']} cases with energy). Arms with no scored run (NOT RUN or left out by the "
             f"loader): {', '.join(missing) if missing else 'none'}. Scored labels outside the declared arms: {', '.join(extra) if extra else 'none'}. "
             f"Cases without a literal frozen row: {', '.join(S['cases_without_literal_forecast']) or 'none'}.")
    o.append('')
    o.append('**Every case** (errors in %; twin = time configuration in the fit data):')
    o.append('')
    o.append('| case | kind | mask | runs | MHz | twin | measured cycles | v3 cycles | v2 cycles | v3 W given t | v2 W given t |')
    o.append('|---|---|---|---|---|---|---|---|---|---|---|')

    def pct(x):
        return '-' if x in ('', None) else f"{100 * float(x):+.2f}"
    for r in C:
        o.append(f"| {r['arm_labels']} | {r['kind']} | {r['mask']} | {r['n_runs']} | {float(r['f_mhz']):.1f} | {'yes' if r['twin_time'] == 'True' else 'no'} | "
                 f"{float(r['meas_cyc_wall']):.1f} | {pct(r['v3_e_wall'])} | {pct(r['v2_e_wall'])} | {pct(r.get('v3_e_w_given_t'))} | {pct(r.get('v2_e_w_given_t'))} |")
    o.append('')
    o.append(open(a.tail).read().rstrip('\n'))
    o.append('')
    open(a.out, 'w').write('\n'.join(o))
    print('README lines', len(o))


if __name__ == '__main__':
    main()
