#!/usr/bin/env python3
"""MM1-v3.2: write README.md from the final run's records (out/decisions_v32.json, holdout_v32.json, identification_v32.json, reported_v32.json,
selfcheck_v32.json, mm1_v32_params.json, out/e218/choice-e218.json) and the lane's notes (a JSON of named readings, departures and gaps).

    /usr/bin/python3 -I -B readme_v32.py --out <run dir> --e218 <e218 dir> --notes <notes.json> --readme <README.md>
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os


def f2(x, d=3):
    if x is None:
        return 'NOT RUN'
    if isinstance(x, dict):
        return f2(x.get('rms_pct'), d)
    return ('%.' + str(d) + 'f') % x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--e218', required=True)
    ap.add_argument('--notes', required=True)
    ap.add_argument('--readme', required=True)
    a = ap.parse_args()
    J = lambda n: json.load(open(os.path.join(a.out, n)))  # noqa: E731
    dec, H, ident, rep, sc, P = (J('decisions_v32.json'), J('holdout_v32.json'), J('identification_v32.json'), J('reported_v32.json'),
                                 J('selfcheck_v32.json'), J('mm1_v32_params.json'))
    ch = json.load(open(os.path.join(a.e218, 'choice-e218.json')))
    notes = json.load(open(a.notes))
    s0, s1, s2, s3, s4 = (dec['steps'][k] for k in ('step0', 'step1', 'step2', 'step3', 'step4'))
    acc = s4['acceptance']
    L = []
    A = L.append
    lay = ('and no layout term (its declared rule chose none)' if s2['enters'] == 'none'
           else f"and the layout term its declared rule chose ({s2['enters']})")
    A('# MM1-v3.2: the matmul model refitted on every committed matmul point through E215 and E214, with the gemmLnc energy term F3 '
      f'{lay}, fitted exactly by its declaration')
    A('')
    A(f"*{notes['written']}. Desk only: no card, no simulator. Interpreter for every number: {s0['interpreter']}, scipy {s0.get('scipy')}, "
      "`-I -B`, single-threaded (OMP_NUM_THREADS = OPENBLAS_NUM_THREADS = MKL_NUM_THREADS = NUMEXPR_NUM_THREADS = 1), every fit inside the "
      "round's CPU slots, one slot job at a time.*")
    A('')
    A("The owner's words that started the matmul model (Mon 16 Nov 2026; a voice transcription in which \"matte mold\" is the matmul): \"I want "
      "you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches "
      "and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See check how well the timing "
      "simulation for the matte mold matches reality and the energy.\" The checkpoint's step 5: fix what the blind day names, then test the fix "
      "in one card session (E218, section 7).")
    A('')
    A('**Labels.** *Registered*: declared in `DECLARED-v32.md` before any fit. *Post hoc*: every constant here (fitted after its data existed). '
      '*Held out*: left out of the fit that scores it (not blind). *Blind*: scored on data that did not exist when the forecast was frozen. '
      '*REPORTED*: printed beside a rule, never deciding it. *NOT RUN*: a check that did not run. Error = forecast / measured - 1; rms and bias in %.')
    A('')
    A('## 0. On one screen')
    A('')
    A('| item | declared (DECLARED-v32.md) | decided here | by |')
    A('|---|---|---|---|')
    A(f"| time | T5r+G0+n32 refitted, no v3.1 item reopened | T5r+G0+n32 at its refitted constants ({len(P['time']['free'])} free) | fixed (section 1.1) |")
    A(f"| layout term | at most one of N3, N1+N2, G1, G1+N1, F1, fresh24 | **{s2['enters']}** (rule winner: {s2['rule_winner']}) | `layout_rule_v32.py` (section 3) |")
    A(f"| energy | E1t + F3 (c1, c2 in [0, 10,000] pJ) | E1t + F3: c1 = {f2(P['energy']['theta'].get('c1'), 1)} pJ, c2 = {f2(P['energy']['theta'].get('c2'), 1)} pJ (all data) | fixed; F3's pin rule |")
    A(f"| data | MM1-v3.1's points + E214 + E215 | {s0['n_time_points']} time, {s0['n_energy_points']} energy points ({s0['energy_usable']} priced) | section 4 |")
    fr = acc['failed_rules']
    A(f"| acceptance | rules 1-3, 4(a)-4(d), 5 against MM1-v3 refitted | **{'ACCEPTED' if acc['accepted'] else 'NOT ACCEPTED: ' + ('rule ' if len(fr) == 1 else 'rules ') + ', '.join(fr) + (' fails' if len(fr) == 1 else ' fail')}** | section 7 |")
    A(f"| E218 | about 54 points on aifoundry3 card 0 | {ch['n_points']} points: {ch['by_family']} | section 9's point rule |")
    A('')
    t = H['time']['LOEO (20 folds)']
    e = H['energy']['LOEO (20 folds + E210)']
    A('**Held out, without twins, MM1-v3.2 against MM1-v3 refitted on the same points and folds:**')
    A('')
    A('| quantity | MM1-v3.2 | MM1-v3 refitted |')
    A('|---|---|---|')
    A(f"| LOEO wall cycles (n {t['v32']['no_twins']['n']}) | {f2(t['v32']['no_twins'])}% | {f2(t['v3_refitted']['no_twins'])}% |")
    A(f"| LOEO W over idle given t (>= 3 W) | {f2(e['v32']['no_twins']['W given t (>= 3 W)'])}% | {f2(e['v3_refitted']['no_twins']['W given t (>= 3 W)'])}% |")
    A(f"| LOEO J over idle with t forecast | {f2(e['v32']['no_twins']['J over idle t forecast (>= 3 W)'])}% | {f2(e['v3_refitted']['no_twins']['J over idle t forecast (>= 3 W)'])}% |")
    A(f"| LOEO J at rest given t | {f2(e['v32']['no_twins']['J at rest given t'])}% | {f2(e['v3_refitted']['no_twins']['J at rest given t'])}% |")
    A(f"| LOCO wall cycles (every point) | {f2(acc['2']['LOCO wall (every point)']['v32'])}% | {f2(acc['2']['LOCO wall (every point)']['v3_refitted'])}% |")
    k2 = 'LOCO W given t (fallback route, every point both price, >= 3 W)'
    A(f"| LOCO W over idle given t (fallback route) | {f2(acc['2'][k2]['v32'])}% | {f2(acc['2'][k2]['v3_refitted'])}% |")
    k5 = 'LOEO W given t over gemmLnc points (no twin, >= 3 W)'
    A(f"| LOEO W over idle given t at the gemmLnc points (n {acc['5'][k5]['n']}) | {f2(acc['5'][k5]['v32'])}% | {f2(acc['5'][k5]['v3_refitted'])}% |")
    A('')
    A('## 1. The data (section 4)')
    A('')
    A(f"- GitHub main at the fit's start: `{s0['repo_head']}` ({s0['repo_head_date']}); the gate: **{s0['gate'].get('verdict')}** "
      f"({len(s0['gate'].get('files') or {})} E215 scores files on main: " + '; '.join(f"`{k}` {v['commit'][:10]}" for k, v in sorted((s0['gate'].get('files') or {}).items())) + ').')
    A(f"- Time points by experiment: {s0['time_points_by_exp']}.")
    A(f"- Energy points by experiment: {s0['energy_points_by_exp']}; not priced: {len(s0['energy_not_forecast'])}.")
    A(f"- Frozen inputs: {len(s0['frozen_files'])} files equal to the declaration's sha256; {s0['vendored_inputs_checked']} vendored inputs of "
      f"MM1-v3 and MM1-v3.1 equal to their SOURCES.tsv; counts SHA256SUMS `{s0['counts_SHA256SUMS'][:16]}...` and counts-e214 "
      f"`{s0['counts-e214_SHA256SUMS'][:16]}...` (`sha256sum -c` rc {s0['counts_check_rc']} / {s0['counts-e214_check_rc']}).")
    A('- E214 (seven sessions, the model session\'s third sweep), vendored under `inputs/e214/`:')
    A('')
    A('| session | sha256 | data commit | ancestor of the fit\'s main |')
    A('|---|---|---|---|')
    for k, v in sorted(s0['e214'].items()):
        A(f"| {k} | `{v['sha256']}` | {v['data_commit'][:10]} | {v['ancestor_of_head']} |")
    A('')
    A('- E215 (MM1-v3.1\'s blind day), vendored under `inputs/e215/` after the gate, each checked by `git hash-object` against the declared blob id:')
    A('')
    A('| arm | git hash-object = declared blob | sha256 | data commit | kept runs | set aside | the two record readings keep the same runs |')
    A('|---|---|---|---|---|---|---|')
    for k, v in sorted(s0['e215'].items()):
        if v.get('vendored'):
            A(f"| {k} | {v['blob_equal']} (`{v['git_hash_object'][:12]}`) | `{v['sha256']}` | {v['data_commit'][:10]} | {v['kept_runs']} | "
              f"{len(v['set_aside'])} | {v['string_and_number_readings_keep_the_same_runs']} |")
    A('')
    A('## 2. Time (sections 1.1, 2, 5)')
    A('')
    A(f"MM1-v3.1's chosen form T5r+G0+n32 (`../v3.1/time_v31.py`, unchanged) refitted by `../v3.1/fit_v31.py` `fit_time` and `run_time` unchanged "
      f"(18 starts, phase 2, the tie rule) with v3.1's pin rule plus the eta pin; {s1['n_folds']} folds and the all-data fit. eta was pinned at 0 "
      f"in: {[k for k, v in s1['eta_pinned_by_fold'].items() if v] or 'no fold'}.")
    A('')
    A('| fold | n | MM1-v3.2 rms (bias) | without twins | twins | winner start | pins |')
    A('|---|---|---|---|---|---|---|')
    for fn, v in H['time']['by_fold'].items():
        A(f"| {fn} | {v['n']} | {f2(v['v32'])} ({f2((v['v32'] or {}).get('bias_pct'))}) | {f2(v['v32_no_twins'])} | {v['n_twins']} | S{v['winner_start']} | {', '.join(v['pins']) or '-'} |")
    A('')
    A('## 3. The layout term (section 3, `layout_rule_v32.py`)')
    A('')
    A(f"Features by verify-lay's `v01_map.py` functions at every subset configuration of rgm136 gemmL in the data ({s2['n_subset_points']} subset points; "
      f"sources {s2['features_sources']}); F1's check against lay-contention's frozen Phi_fresh: {s2['f1_check']['n_configs']} configurations, "
      f"worst |difference| {s2['f1_check']['worst_abs_diff']:.3g}, {len(s2['f1_check']['fails'])} failing.")
    A('')
    A('| candidate | LOEO no twin | LOLO | LOCO by card | all-data constants | eligible | conditions |')
    A('|---|---|---|---|---|---|---|')
    for c, x in s2['candidates_summary'].items():
        el = s2['eligibility'].get(c, {})
        A(f"| {c} | {f2(x['LOEO_nt'], 4)} | {f2(x['LOLO'], 4)} | " + ', '.join(f"{k} {f2(v, 2)}" for k, v in x['LOCO_sub'].items()) +
          f" | {['%.6g' % q for q in x['a_all']]} | {el.get('eligible', '-')} | {el.get('conditions', '-')} |")
    A('')
    A(f"Rule winner: **{s2['rule_winner']}**; the selection placebo: {s2.get('placebo')}; **enters: {s2['enters']}**."
      + (f" Label: {s2.get('label')}." if s2.get('label') else ''))
    A('')
    A('## 4. Energy (sections 1.2-1.4)')
    A('')
    A("E1t (`../v3.1/energy_v31.py`, unchanged) plus F3 (`energy_v32.py`), fitted by `fit_v32.fit_energy` (v3.1's procedure line for line: nine "
      "starts, the linear solve with c1 and c2 among the linear constants, clipped into [0, 10,000] pJ, least squares at 1e-12); MM1-v3 refitted's E1u "
      "by `fit_v31.fit_energy` unchanged; each energy fold on its own time fold.")
    A('')
    A('| fold | MM1-v3.2 W given t (>= 3 W) | MM1-v3 refitted | c1 (pJ) | c2 (pJ) | F3 pins |')
    A('|---|---|---|---|---|---|')
    for fn, v in H['energy']['by_fold'].items():
        A(f"| {fn} | {f2(v['v32 W given t'])} | {f2(v['v3_refitted W given t'])} | {f2(v['F3']['c1'], 1)} | {f2(v['F3']['c2'], 1)} | {v['F3']['pins']} |")
    A('')
    A('## 5. Acceptance (section 7, against MM1-v3 refitted on the same points and folds)')
    A('')
    A('| rule | MM1-v3.2 | MM1-v3 refitted / the predecessor | verdict |')
    A('|---|---|---|---|')
    r1 = acc['1']
    A(f"| 1 LOEO wall, no twin | {f2(r1['LOEO wall no twin']['v32'])}% | {f2(r1['LOEO wall no twin']['v3_refitted'])}% | {r1['LOEO wall no twin']['reading']} |")
    k1 = 'LOEO W given t no twin (>= 3 W, both price)'
    A(f"| 1 LOEO W given t, no twin | {f2(r1[k1]['v32'])}% | {f2(r1[k1]['v3_refitted'])}% | rule 1 **{'PASS' if r1['pass'] else 'FAIL'}** |")
    r2 = acc['2']
    A(f"| 2 LOCO wall | {f2(r2['LOCO wall (every point)']['v32'])}% | {f2(r2['LOCO wall (every point)']['v3_refitted'])}% | |")
    A(f"| 2 LOCO W given t (fallback) | {f2(r2[k2]['v32'])}% | {f2(r2[k2]['v3_refitted'])}% | rule 2 **{'PASS' if r2['pass'] else 'FAIL'}** "
      f"(without the anchor points, REPORTED: {'PASS' if r2['pass_on_the_no_anchor_reading_REPORTED'] else 'FAIL'}) |")
    r3 = acc['3']
    A(f"| 3 leave rgm211 out | {f2(r3['leave rgm211 out wall rms'])}%, {r3['E211 W pairs']['inside_0.05']} of {r3['E211 W pairs']['n']} pairs | <= 8.0%, >= 7 | **{'PASS' if r3['pass'] else 'FAIL'}** |")
    r4a = acc['4a']
    A(f"| 4(a) E212 fold vs MM1-v2 unread (comparator_4a_v31.py) | wall {f2((r4a.get('wall') or {}).get('v31'))}%, W {f2((r4a.get('W_given_t_ge3W') or {}).get('v31'))}% | "
      f"wall {f2((r4a.get('wall') or {}).get('v2_unread'))}%, W {f2((r4a.get('W_given_t_ge3W') or {}).get('v2_unread'))}% | **{'PASS' if r4a['pass'] else 'FAIL'}** |")
    r4b = acc['4b']['pooled']
    A(f"| 4(b) E213 fold vs MM1-v3 blind | wall {f2(r4b['wall_cases']['v32'])}%, W {f2(r4b['W_given_t_points']['v32'])}% | wall {f2(r4b['wall_cases']['v3_blind'])}%, W {f2(r4b['W_given_t_points']['v3_blind'])}% | **{'PASS' if acc['4b']['pass'] else 'FAIL'}** |")
    for k, lab in (('4c', 'E214 fold vs MM1-v3.1 unread'), ('4d', 'E215 fold vs MM1-v3.1 blind')):
        r = acc[k]
        if 'time_cases' in r:
            A(f"| {k[0]}({k[1]}) {lab} | wall {f2(r['time_cases']['v32'])}%, W {f2(r['W_given_t_points']['v32'])}% | wall {f2(r['time_cases']['v31'])}%, W {f2(r['W_given_t_points']['v31'])}% | **{'PASS' if r['pass'] else 'FAIL'}** |")
        else:
            A(f"| {k[0]}({k[1]}) {lab} | - | - | {r.get('note')} |")
    r5 = acc['5'][k5]
    A(f"| 5 gemmLnc points, LOEO W given t | {f2(r5['v32'])}% (n {r5['n']}) | {f2(r5['v3_refitted'])}% | **{'PASS' if acc['5']['pass'] else 'FAIL'}** |")
    A('')
    A(f"**Verdict: {'ACCEPTED' if acc['accepted'] else 'NOT ACCEPTED (' + ('rule ' if len(fr) == 1 else 'rules ') + ', '.join(fr) + ')'}.** As declared, MM1-v3.2 is "
      "frozen as built either way and E218 runs either way.")
    A('')
    A('## 6. REPORTED (section 8, never deciding)')
    A('')
    A(f"- The predictor's self-check: {sc}.")
    A(f"- Identification of the all-data constants (Jacobian rse above 100%: not identified): {ident.get('not_identified')}.")
    if isinstance(rep.get('E215_by_family_per_point'), dict):
        A('- E215 per point by family (MM1-v3.2: its E215 fold, held out; the others: their frozen blind forecasts):')
        A('')
        A('| family | quantity | n | rms % | bias % |')
        A('|---|---|---|---|---|')
        for fam, d in rep['E215_by_family_per_point'].items():
            for q, v in d.items():
                if v:
                    A(f"| {fam} | {q} | {v['n']} | {f2(v['rms_pct'], 2)} | {f2(v['bias_pct'], 2)} |")
        A('')
    ar = rep.get('anchor_route_LOCO') or {}
    A(f"- The anchor route's LOCO W given t without the anchor points (REPORTED; the fallback decides): MM1-v3.2 "
      f"{f2((ar.get('v32') or {}).get('v32'))}%, MM1-v3 refitted {f2(ar.get('v3_refitted'))}%; the anchor kc by card: "
      + ', '.join(f"{k} {v:.4f}" for k, v in (ar.get('kc_by_card_v32') or {}).items() if v is not None) + '.')
    A(f"- The layout term refitted jointly: {rep.get('layout_joint_refit')}.")
    A('')
    A('## 7. E218, MM1-v3.2\'s blind day (section 9)')
    A('')
    A(f"Points by section 9's rule on the landed constants, with the never-run scan (`e218_v32.py scan`): {ch['by_family']}; G "
      f"{ch['G']}; Y {ch['Y']}; F {ch['F']}. The order (REPORTED for the kit): {ch['order']['runs']} runs and 2 smoke processes, "
      f"{ch['order']['card_minutes_planned_at_24.47_s']} card-minutes at E213 arm A's 24.47 s a run.")
    A('')
    if notes.get('e218_status'):
        A(notes['e218_status'])
        A('')
    A('The readings this file applies where section 9 leaves one open:')
    A('')
    for r in ch['readings']:
        A(f'- {r}')
    A('')
    A("Every declared model's forecasts are in `out/e218/forecasts-e218.csv` and `.json` (MM1-v3.2, MM1-v3.1, MM1-v3, MM1-v2, 'v3.1 + gemmLnc term', "
      "'v3.1 + contention', verify-lay's controls; REPORTED: 'v3.1 + both terms', 'v3.1 with T7', MM1-v3 refitted"
      + (", MM1-v3.2 without its layout term" if s2['enters'] != 'none' else '') + "). Their sha256 are in `out/e218/E218-FROZEN.txt`; "
      "the land's push is their freeze line.")
    A('')
    A('## 8. Named readings, departures and gaps')
    A('')
    for r in notes['readings']:
        A(f'- {r}')
    A('')
    A('## 9. Files, and how to re-run')
    A('')
    for r in notes['files']:
        A(f'- {r}')
    A('')
    A('## 10. NOT RUN')
    A('')
    for r in notes['not_run']:
        A(f'- {r}')
    A('')
    open(a.readme, 'w').write('\n'.join(L) + '\n')
    print('README written', len(L), 'lines')


if __name__ == '__main__':
    main()
