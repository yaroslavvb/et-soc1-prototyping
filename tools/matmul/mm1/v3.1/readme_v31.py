#!/usr/bin/env python3
"""MM1-v3.1: README.md written from the final run's records (every number read from out/; nothing typed by hand but the prose). Desk.

    /usr/bin/python3 -I -B readme_v31.py --out <run dir> --readme <path of README.md> [--extra <json with the lane's context lines>]

Lane fix-fit-v31 (Q222) added, each printed only when its input exists (so fit-v31's records still give fit-v31's README byte for byte): item 3's
identification labels (decisions step3 `identification_post_hoc` and each form's `scores_identified`, from item3_flat_v31.py) and the --extra
keys 'item3_notes' (section 3), 'section4' (section 4) and 'e215_notes' (section 7).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def J(p):
    return json.load(open(p)) if os.path.exists(p) else {}


def pct(s, key='rms_pct'):
    if not s:
        return 'NOT RUN'
    v = s.get(key)
    if v is None:
        return 'NOT RUN'
    b = s.get('bias_pct')
    return f"{v:.2f}%" + (f" ({b:+.2f})" if b is not None and key == 'rms_pct' else '') + (f", n {s['n']}" if s.get('n') is not None else '')


def f2(x, nd=2):
    return 'NOT RUN' if x is None else f'{x:.{nd}f}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--readme', required=True)
    ap.add_argument('--extra', default='')
    a = ap.parse_args()
    O = a.out
    D = J(os.path.join(O, 'decisions_v31.json'))
    H = J(os.path.join(O, 'holdout_v31.json'))
    I = J(os.path.join(O, 'identification_v31.json'))
    R = J(os.path.join(O, 'reported_v31.json'))
    S = J(os.path.join(O, 'summary_v31.json'))
    PR = J(os.path.join(O, 'mm1_v31_params.json'))
    ST = J(os.path.join(O, 'starts_check_v31.json'))
    E5 = J(os.path.join(O, 'e215', 'e215_choice.json'))
    X = J(a.extra) if a.extra else {}
    s = D.get('steps', {})
    s0, s1, s2, s3, s4, s6, s7 = (s.get(k, {}) for k in ('step0', 'step1', 'step2', 'step3', 'step4', 'step6', 'step7'))
    acc = s7.get('acceptance', {})
    final = D.get('final_time_form')
    ef = D.get('final_energy_form')
    tv = H.get('time', {}).get('v3.1', {})
    t3 = H.get('time', {}).get('v3 refitted', {})
    ev = H.get('energy', {}).get('v3.1', {})
    e3 = H.get('energy', {}).get('v3 refitted', {})

    def tg(tab, fam, grp='all', which='no_twin'):
        return ((tab.get(fam) or {}).get(grp) or {}).get(which)

    def eg(tab, fam, grp='all', which='no_twin', q='W given t (>= 3 W)'):
        return (((tab.get(fam) or {}).get(grp) or {}).get(which) or {}).get(q)
    L = []
    w = L.append
    w(f"# MM1-v3.1: the lab's matmul model fitted exactly by its declaration on every committed matmul point through E213, frozen for its blind day E215")
    w('')
    w(f"MM1-v3.1 predicts a matmul's clock cycles, seconds, joules (over idle and with the card at rest) and transistor switches on the ET-SoC-1 "
      f"cards from the matrix size, the format, the data kind, the shire mask, the card, the clock and the operations the kernel contains. It is "
      f"MM1-v3 (`../v3/`, landed b1493082) with the changes its declaration (`DECLARED-v31.md`, `declared-v31.json`, `t7_v31.py`, "
      f"`comparator_4a_v31.py`; landed 7375bc9c, frozen by their sha256 before any E213 datum) declares, each decided by the declaration's own "
      f"rule in its declared order. It was fitted at the lab box aifoundry2's desk (round Q222, lane fit-v31) on everything committed at "
      f"GitHub main **{s0.get('repo_head', '?')[:8]}** when the fit started ({s0.get('when', '?')}): {s0.get('n_time_points')} time points and "
      f"{s0.get('n_energy_points')} energy points, E213's arms {', '.join(s0.get('e213_arms', []))}. Desk only: this commit measured nothing.")
    w('')
    if X.get('lead'):
        for ln in X['lead']:
            w(ln)
            w('')
    w("The owner's words that started the matmul model (Mon 16 Nov 2026, at or before 09:48:24 PST; a voice transcription in which \"matte mold\" "
      "is the matmul): \"I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of "
      "transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See check how "
      "well the timing simulation for the matte mold matches reality and the energy.\"")
    w('')
    idp = s3.get('identification_post_hoc')
    w("**Labels.** *Registered*: declared before any E213 datum (`DECLARED-v31.md`). *Desk*: computed at a desk from committed files. *Post hoc*: "
      "fitted or read after its data existed (every constant of v3.1 is). *Held out*: left out of the fit that scores it (not blind). *Blind*: scored "
      "on data that did not exist when the forecast was frozen. *REPORTED*: printed beside a rule, never deciding it. *NOT RUN*: a check that did not "
      "run. "
      + ("*Unidentified*: read from a fold in which a fitted constant moves no training prediction at all (the fold's training cost is flat along "
         "it), so the figure is where the optimizer stopped; printed with its range over the constant's declared bounds (section 3). " if idp else '')
      + "Error = forecast / measured - 1; rms and bias in %. **Headline held-out figures exclude configuration twins** (a scored point whose card, "
      "kernel, arm, format, mask and clock to 25 MHz, and for energy the kind, are in the training set that priced it); the figures with them are "
      "beside. Interpreter: `/usr/bin/python3` 3.12.3, numpy 1.26.4, scipy 1.11.4, `-I -B`, single-threaded, in the round's CPU slots.")
    w('')
    w('## 0. On one screen')
    w('')
    w('| declared step | the rule\'s inputs | outcome |')
    w('|---|---|---|')
    w(f"| 1. item 8, T5r or tC (no fit) | E213's measured wall cycles at family C (arm A) and BK (arm B): {s1.get('n_untied')} untied of "
      f"{s1.get('n_scored')} cases, tC closer {s1.get('tC_closer')}, T5r closer {s1.get('T5r_closer')}, exact sign test p {f2(s1.get('p_two_sided'), 4)} | "
      f"**{s1.get('verdict')}** |")
    w(f"| 2. item 4, the trace check | the committed verdict (walk/T7-TRACE-CHECK.json) and T7's desk precondition re-run with every subset shape "
      f"of the data | **{s2.get('verdict')}** |")
    f3 = s3.get('forms', {})

    def unid(g):
        r = f3[g]
        if r.get('scores_identified') is False and r.get('score_touched_no_twin_range_post_hoc'):
            lo, hi = r['score_touched_no_twin_range_post_hoc']
            return f" (unidentified: {lo:.2f}-{hi:.2f}%)"
        return ''
    flat_where = ', '.join(sorted({f"`{x['constant']}` in the {x['fold']} fold" for x in (idp or {}).get('flat_constants', [])}))
    w(f"| 3. item 3, G0 / Gplace / Goperand / Gcoop | LOEO wall rms over the touched points (rgm211's two loops and gemmLnc), no twins: "
      + ', '.join(f"{g} {f2(f3[g]['score_touched_no_twin'])}%{unid(g)}" for g in ('G0', 'Gplace', 'Goperand', 'Gcoop') if g in f3)
      + f"; guard (pooled LOEO within 0.05 of G0's) {s3.get('guard_pass')}"
      + (f"; the unidentified scores read {flat_where}, where the training cost is flat (post hoc, section 3)" if flat_where else '')
      + f" | **{s3.get('winner')}**"
      + (" (at every value of the flat constant)" if idp and idp.get('decision_G0_at_every_combination') else '') + " |")
    f4 = s4.get('forms', {})
    w(f"| 4. item 4, T7 / T7L / n/32 | LOLO wall rms over subset points / pooled LOEO wall rms: "
      + ', '.join(f"{k} {f2(v['LOLO_subset_rms'])}% / {f2(v['pooled_LOEO_all'])}%" for k, v in f4.items())
      + f" | **{s4.get('layout')}** ({s4.get('how')}) |")
    if s4.get('item8_step3'):
        q = s4['item8_step3']
        w(f"| 4b. item 8's step 3 | pooled LOEO wall rms: T5r {f2(q['pooled_LOEO_all'].get('T5r'))}%, tC {f2(q['pooled_LOEO_all'].get('tC'))}% | **{q['winner']}** |")
    w(f"| 5. the final time form | every fold, MM1-v3 refitted beside | **{final}** |")
    f6 = s6.get('forms', {})
    w(f"| 6. item 1, the energy split | LOEO W over idle given t, no twins, >= 3 W: "
      + ', '.join(f"{e} {f2(f6[e]['score_LOEO_W_given_t_no_twin'])}%" for e in ('E1u', 'E1b', 'E1t', 'E1m') if e in f6)
      + f" | **{s6.get('winner')}** |")
    a2 = acc.get('2', {})
    w(f"| 7. item 2, a card left out | pooled LOCO W given t (held-out cards' anchor points out): anchor route {pct((a2.get('v31_routes') or {}).get('anchor', {}).get('pooled_no_anchor_points'))}, "
      f"fallback {pct((a2.get('v31_routes') or {}).get('fallback', {}).get('pooled_no_anchor_points'))} | the anchor route (declared) |")
    w('')
    w("Form names: `T5r+G0+n32` = item 8's T5r, item 3's G0, item 4's n/32 (MM1-v3's own form); T7L appears as `demand` (engine_v3's name for it). "
      "The LOLO figures of n/32 and T7L read the compact class with an unidentified eta (the finding above).")
    w('')
    w('**Held out, the same points and folds for MM1-v3.1 and MM1-v3 refitted on exactly v3.1\'s inputs** (wall cycles; energy W over idle given '
      'the measured seconds at 3 W and above):')
    w('')
    w('| set | MM1-v3.1 | MM1-v3 refitted | with twins (v3.1 / v3 refitted) |')
    w('|---|---|---|---|')
    for lab, fam, grp in (('LOEO, all points', 'LOEO', 'all'), ('LOCO', 'LOCO', 'all'), ('leave rgm211 out', 'LEAVE rgm211', 'all'),
                          ('the E212 fold', 'LOEO', 'exp E212'), ('the E213 fold', 'LOEO', 'exp E213'), ('subsets (LOEO)', 'LOEO', 'subsets')):
        w(f"| {lab} | {pct(tg(tv, fam, grp))} | {pct(tg(t3, fam, grp))} | {pct(tg(tv, fam, grp, 'all'))} / {pct(tg(t3, fam, grp, 'all'))} |")
    for lab, fam, grp in (('energy LOEO', 'LOEO', 'all'), ('energy LOCO (anchor route)', 'LOCO (anchor route)', 'all'),
                          ('energy LOCO (fallback)', 'LOCO (fallback route)', 'all'), ('energy, the newly counted kinds (LOEO)', 'LOEO', 'kinds newly counted (v31-counts)')):
        w(f"| {lab} | {pct(eg(ev, fam, grp))} | {pct(eg(e3, fam, grp))} | {pct(eg(ev, fam, grp, 'all'))} / {pct(eg(e3, fam, grp, 'all'))} |")
    w('')
    w('**Acceptance** (MM1-v3\'s four rules restated in the declaration\'s section 9, against MM1-v3 refitted on the same points and folds): ' +
      '; '.join(f"rule {k} {'PASS' if (acc.get(k) or {}).get('pass') else 'FAIL'}" for k in ('1', '2', '3', '4a', '4b')) +
      f"; **accepted: {acc.get('accepted')}**.")
    w('')
    if E5:
        fams = E5.get('families', {})
        w('**E215, v3.1\'s blind day (arm A, aifoundry3 card 0 at 600 MHz)**: by item 10\'s point rule on both frozen models and a never-run scan in '
          'E213\'s form: ' + '; '.join(f"{k} {len(v.get('literal_chosen') or [])} of {E5.get('quota_A', {}).get(k)}"
                                     + (f" (post hoc reading: {len(v.get('posthoc_chosen') or [])})" if 'posthoc_chosen' in v else '')
                                     for k, v in fams.items()) + '. Forecasts in `out/e215/mm1_v31_e215.csv` and `.json` (section 7).')
        w('')
    # ---- 1. data and inputs
    w('## 1. The data and the inputs')
    w('')
    w(f"Time points by experiment: {s0.get('time_points_by_exp')}. Energy points: {s0.get('energy_points_by_exp')} ({s0.get('energy_usable_v31')} "
      f"priced by v3.1's counts and phi). E146's {s0.get('store_rungs')} store-cadence rungs are in no training set and are scored apart (as MM1-v3). "
      "E212's cases are re-made over every committed session (ten: MM1-v3's eight, a2c0-S4 and the re-run a2c0-S3; a case run in two sessions is one record, as `comparator_4a_v31.py` makes them for its nine; the records the re-run S3 changes leave rule 4(a)'s comparison and are listed); "
      "E213's time points are one a (card, case), the mean of its runs, and its energy points one a (card, configuration, kind).")
    w('')
    w('| input | sha256 |')
    w('|---|---|')
    for k, v in sorted((s0.get('frozen_files') or {}).items()):
        w(f"| `{k}` (frozen, posted before any E213 datum) | `{v.get('got')}` |")
    w(f"| `counts/SHA256SUMS` (v31-counts, landed 3e8991d0; posted #2.7.2.1.1) | `{s0.get('counts_SHA256SUMS')}` (sha256sum -c rc {s0.get('counts_check')}) |")
    w(f"| `inputs/census/census-v3.1.json` (item 6) | `{s0.get('census_v31_sha256')}` |")
    for k, v in sorted((s0.get('inputs') or {}).items()):
        if 'e212tiles' in k:
            continue
        w(f"| `{k}` | `{v}` |")
    w('')
    w(f"**The census paths' check** (the declaration's deferred item, made first): {(s0.get('census_path_check') or {}).get('reading')}.")
    w('')
    w(f"**T7's desk precondition**, re-run at the fit's start with every subset shape of the data ({len((s0.get('t7_check') or {}).get('extra_shapes', []))} "
      f"shapes): {' '.join((s0.get('t7_check') or {}).get('stdout_tail', []))} (record `out/t7_check.json`).")
    w('')
    w(f"**The declared starts** (`check_starts_v31.py`): S0-S5 equal MM1-v3's `fit_v3.STARTS` and the declared new-name values; S6-S17 and the "
      f"energy draws re-drawn from their seeds: {'PASS' if ST.get('pass') else 'NOT RUN or FAIL'}.")
    w('')
    # ---- 2. constants
    w('## 2. What MM1-v3.1 computes: the frozen constants')
    w('')
    w(f"Time form **{final}** (`time_v31.py`; `mm1_v31_params.json` holds every constant), energy form **{ef}** (`energy_v31.py`). Every constant's "
      "all-data value, its bound activity and its relative standard error from the Jacobian at the all-data fit (above 100%: not identified, "
      "the fit unchanged):")
    w('')
    w('| constant | value | rse | bound | | constant | value | rse | bound |')
    w('|---|---|---|---|---|---|---|---|---|')
    tc = list((I.get('time') or {}).get('constants', {}).items())
    ec = list((I.get('energy') or {}).get('constants', {}).items())
    rows = max(len(tc), len(ec))
    for i in range(rows):
        cells = []
        for lst in (tc, ec):
            if i < len(lst):
                k, v = lst[i]
                b = 'lower' if v.get('at_lower_bound') else ('upper' if v.get('at_upper_bound') else '')
                if abs(v['value']) < 1e-12 and b:
                    rs = f'- (at its {b} bound, not identified)'
                else:
                    rs = f"{v['rse_pct']:.1f}%{' (not identified)' if v.get('not_identified_rse_over_100pct') else ''}"
                kk = k.replace('|', '\\|')
                cells.append(f"{kk} | {v['value']:.6g} | {rs} | {b}")
            else:
                cells.append(' | | | ')
        w('| ' + cells[0] + ' | | ' + cells[1] + ' |')
    w('')
    # ---- 3. decisions
    w('## 3. The decisions, in the declared order (`out/decisions_v31.json`)')
    w('')
    w(f"**Step 1, item 8** (T5r against tC from their frozen forecasts, no fit): sources {s1.get('sources')}. Cases (measured wall cycles an op as "
      "E213's frozen scorer reports them; d = |ln(m / F_T5r)| - |ln(m / F_tC)|, a tie at |d| <= 0.005):")
    w('')
    w('| case | arm | measured | T5r | tC | d |')
    w('|---|---|---|---|---|---|')
    for r in s1.get('cases', []):
        w(f"| {r['case_id']} | {r['arm']} | {f2(r.get('measured'), 1)} | {r['T5r']:.1f} | {r['tC']:.1f} | {f2(r.get('d'), 4)}{' (tie)' if r.get('tie') else ''} |")
    w('')
    w(f"Verdict: **{s1.get('verdict')}**.")
    w('')
    w(f"**Step 2, item 4's trace check: {s2.get('verdict')}** ({s2.get('reading')}).")
    w('')
    w(f"**Step 3, item 3**: rule winner {s3.get('rule_winner')}, guard {s3.get('guard_pass')}, **{s3.get('winner')}**; not wanted (G0 wins, or "
      f"every constant within 1% of 0): {s3.get('not_wanted')}. Each form's all-data constants: "
      + '; '.join(f"{g} {json.dumps({k: round(v, 4) for k, v in (r.get('all_data') or {}).items()})}" for g, r in f3.items()) + ". Per fold: `out/decisions_v31.json`.")
    w('')
    if idp:
        I3 = J(os.path.join(O, 'item3_flat_v31.json'))
        scr = I3.get('screen', [])
        fl = idp.get('flat_constants', [])
        g0r = idp.get('G0_reference') or {}
        pin_ids = sorted({i for x in scr if x.get('flat') for i in x.get('pin_set_training_ids', [])})
        rep = I3.get('replication_of_step3_scores') or {}
        w("**Item 3's scores checked for identification** (post hoc, REPORTED; `item3_flat_v31.py`, `out/item3_flat_v31.json`; "
          f"{idp.get('by')}): with step 3's scores re-made first ({'equal to the stored ones' if rep and all(v.get('equal') for v in rep.values()) else 'NOT equal to the stored ones'}), every free "
          f"item 3 constant of Gplace, Goperand and Gcoop was moved alone to its two declared bounds in every LOEO fold, the fold's other constants "
          f"held: {len(scr)} (form, fold, constant) checked, {sum(1 for x in scr if x.get('flat'))} flat (no training prediction moves at all): "
          + '; '.join(f"{x['form']}'s `{x['constant']}` in the {x['fold']} fold (fitted {x['fitted_value']:.5g})" for x in fl)
          + f". In that fold the constant's pin set holds {', '.join(pin_ids)} alone, whose op time does not depend on it, so the declared pin rule "
          "(a constant is pinned only when its set is empty) leaves it where the optimizer stopped, and the fold's held-out predictions move with "
          "it. Over the bounds, every other fold as stored: "
          + '; '.join(f"{x['form']} touched (no twin) {x['touched_no_twin_range_pct'][0]:.2f}-{x['touched_no_twin_range_pct'][1]:.2f}%, pooled LOEO "
                      f"{x['pooled_LOEO_all_range_pct'][0]:.3f}-{x['pooled_LOEO_all_range_pct'][1]:.3f}% (training cost span "
                      f"{x['train_cost_span_over_bounds']:g})" for x in fl)
          + ". So those forms' item 3 scores above, and their pooled LOEO, are **unidentified**: labelled so in `out/decisions_v31.json` "
          "(step3: `identification_post_hoc`, and each form's `scores_identified`). **The decision holds:** G0 "
          f"({f2(g0r.get('touched_no_twin'))}%, no constant) is lower than every form at every value, so item 3's rule gives G0 at every value and "
          f"every combination of values{'' if idp.get('decision_G0_at_every_combination') else ' (NOT shown)'}; a rule win would also fail the guard, the pooled LOEO being "
          f"at least {min(x['pooled_LOEO_all_range_pct'][0] for x in fl):.3f}% at every value against G0's {g0r.get('pooled_LOEO_all', 0):.3f}% + 0.05. "
          "A later declaration could pin any constant whose training Jacobian column is zero in a fold.")
        w('')
        for ln in X.get('item3_notes', []):
            w(ln)
            w('')
    w(f"**Step 4, item 4**: {s4.get('how')}: **{s4.get('layout')}**. LOLO by class (each form): "
      + '; '.join(f"{k} {json.dumps({c: (round(x, 3) if x is not None else None) for c, x in (v.get('LOLO_by_class') or {}).items()})}" for k, v in f4.items()) + '.')
    w('')
    w(f"**Step 6, item 1**: candidates within 0.10 points of the lowest of E1b / E1t / E1m: {s6.get('candidates_within_0.10')}; winner of the three "
      f"{s6.get('winner_of_three')}; E1u lower by more than 0.30 points: {s6.get('winner') == 'E1u'}: **{s6.get('winner')}**; E1b's all-data b2, d2 at "
      f"their bound 0: {s6.get('E1b_all_data_b2_d2_at_bound')}.")
    w('')
    # ---- 4. held out
    w('## 4. Held out, beside MM1-v3 refitted (`out/holdout_v31.json`, `out/points_time_v31.csv`, `out/points_energy_v31.csv`)')
    w('')
    w('| wall cycles, held out (no twin) | MM1-v3.1 | MM1-v3 refitted |')
    w('|---|---|---|')
    for fam in ('LOEO', 'LOCO', 'LOKO', 'LEAVE rgm211', 'LOLO', 'LOEO sub'):
        for grp, row in (tv.get(fam) or {}).items():
            if fam != 'LOEO' and grp != 'all' and not grp.startswith(('aifoundry', 'loop', 'E212 ', 'E213 arm', 'layout')):
                continue
            w(f"| {fam} {grp} | {pct((row or {}).get('no_twin'))} | {pct(((t3.get(fam) or {}).get(grp) or {}).get('no_twin'))} |")
    w(f"| LOEO counter mean (all / no twin) | {pct((tv.get('LOEO counter mean') or {}).get('all'))} / {pct((tv.get('LOEO counter mean') or {}).get('no_twin'))} | "
      f"{pct((t3.get('LOEO counter mean') or {}).get('all'))} / {pct((t3.get('LOEO counter mean') or {}).get('no_twin'))} |")
    w('')
    w("v3.1's time form is MM1-v3 refitted's (the decisions above), so the two time columns are the same fits. The LOLO rows carry the compact "
      "fold's unidentified eta (the finding above; `out/reported_v31.json`, item4_LOLO_compact_eta_not_identified_post_hoc).")
    w('')
    w('| energy, held out (no twin) | quantity | MM1-v3.1 | MM1-v3 refitted |')
    w('|---|---|---|---|')
    for fam in ('LOEO', 'LOCO (anchor route)', 'LOCO (fallback route)', 'LOKO', 'LEAVE rgm211', 'LOLO'):
        for grp in ('all', 'aifoundry3 card 0', 'aifoundry1 card 1', 'aifoundry2 card 0', 'aifoundry1 card 0', 'exp E210', 'exp E212', 'exp E213',
                    'kinds newly counted (v31-counts)', 'zeros on card 1'):
            if grp not in (ev.get(fam) or {}):
                continue
            for q in ('W given t (>= 3 W)', 'J over idle t forecast (>= 3 W)', 'J at rest given t', 'J at rest t forecast'):
                if fam != 'LOEO' and q != 'W given t (>= 3 W)':
                    continue
                if grp != 'all' and q != 'W given t (>= 3 W)':
                    continue
                w(f"| {fam} {grp} | {q} | {pct(eg(ev, fam, grp, 'no_twin', q))} | {pct(eg(e3, fam, grp, 'no_twin', q))} |")
    w('')
    for ln in X.get('section4', []):
        w(ln)
        w('')
    # ---- 5. acceptance
    w('## 5. The acceptance rules (`out/decisions_v31.json` step7)')
    w('')
    a1 = acc.get('1', {})
    w(f"1. LOEO wall (no twin) v3.1 {f2((a1.get('LOEO wall no twin') or {}).get('v31'), 3)}% against v3 refitted {f2((a1.get('LOEO wall no twin') or {}).get('v3_refitted'), 3)}%; "
      f"LOEO W given t (no twin, >= 3 W) {f2((a1.get('LOEO W given t no twin (>= 3 W, both price)') or {}).get('v31'), 3)}% against "
      f"{f2((a1.get('LOEO W given t no twin (>= 3 W, both price)') or {}).get('v3_refitted'), 3)}%: **{'PASS' if a1.get('pass') else 'FAIL'}**.")
    w(f"2. LOCO wall {f2((a2.get('LOCO wall (every point)') or {}).get('v31'), 3)}% against {f2((a2.get('LOCO wall (every point)') or {}).get('v3_refitted'), 3)}%; "
      f"LOCO W given t (anchor route) {f2((a2.get('LOCO W given t (anchor route)') or {}).get('v31'), 3)}% against "
      f"{f2((a2.get('LOCO W given t (anchor route)') or {}).get('v3_refitted'), 3)}% (bar: 0.30 points): **{'PASS' if a2.get('pass') else 'FAIL'}**; the fallback route "
      f"beside: {pct(((a2.get('fallback_route_beside') or {}).get('v31')))} against {pct(((a2.get('fallback_route_beside') or {}).get('v3_refitted')))}.")
    a3 = acc.get('3', {})
    w(f"3. Leave rgm211 out: wall {f2(a3.get('leave rgm211 out wall rms'), 3)}% over {a3.get('n')} points (bar 8.0%), E211's W pairs inside 0.05: "
      f"{(a3.get('E211 W pairs') or {}).get('inside_0.05')} of {(a3.get('E211 W pairs') or {}).get('n')} (bar 7): **{'PASS' if a3.get('pass') else 'FAIL'}**.")
    a4 = acc.get('4a', {})
    w(f"4. (a) The E212 fold against MM1-v2's unread error on the same records (`comparator_4a_v31.py`): wall v3.1 {pct((a4.get('wall') or {}).get('v31'))} against "
      f"{pct((a4.get('wall') or {}).get('v2_unread'))}; W given t {pct((a4.get('W_given_t_ge3W') or {}).get('v31'))} against "
      f"{pct((a4.get('W_given_t_ge3W') or {}).get('v2_unread'))}: **{a4.get('rule_4a')}**.")
    b4 = acc.get('4b', {})
    w(f"   (b) The E213 fold against MM1-v3's blind error on the same points: wall per case v3.1 {pct(((b4.get('pooled') or {}).get('wall_cases') or {}).get('v31'))} "
      f"against {pct(((b4.get('pooled') or {}).get('wall_cases') or {}).get('v3_blind'))}; W given t per point {pct(((b4.get('pooled') or {}).get('W_given_t_points') or {}).get('v31'))} "
      f"against {pct(((b4.get('pooled') or {}).get('W_given_t_points') or {}).get('v3_blind'))}: **{'PASS' if b4.get('pass') else 'FAIL'}**. The E213 fold is held "
      "out for every constant and post hoc for the forms E213 helped choose (items 8, 1, 3 and 4).")
    w('')
    w(f"**Accepted: {acc.get('accepted')}.** If a rule fails v3.1 is still frozen as built (the declaration's rule) and the failing rule is named.")
    w('')
    # ---- 6. reported
    w('## 6. REPORTED (`out/reported_v31.json`; never deciding a rule)')
    w('')
    w(f"- Item 8: family C by format under both frozen forms: {json.dumps(R.get('item8_family_C_by_format_frozen_forms'))}; E146's store rungs under both "
      f"forms: {json.dumps(R.get('item8_E146_store_rungs_both_forms'))}.")
    w(f"- Item 2 per LOCO fold (kc from the anchor, the fallback's kc, validity, the anchor points' residuals): see step7 `v31_routes` in "
      "`out/decisions_v31.json`; not wanted (the anchor route's pooled LOCO above the fallback's): "
      f"{a2.get('not_wanted_anchor_above_fallback_v31')}.")
    w(f"- Item 1: b2, d2 and xi per fold and their bound activity in step6; the joules by class at E213's points: "
      f"{json.dumps(R.get('item1_joules_by_class_E213'))}.")
    w(f"- v3-ledger (never chosen): {json.dumps(R.get('v3_ledger_REPORTED'))}.")
    w(f"- E213's rgm211 / rgm136 pairs under leave rgm211 out: {json.dumps(a3.get('E213_rgm211_rgm136_pairs_REPORTED'))}.")
    w(f"- MM1-v3's blind E213 score as committed: {json.dumps(R.get('mm1_v3_blind_E213_committed'))}.")
    w('')
    # ---- 7. E215
    if E5:
        w('## 7. E215: the points and the forecasts (`e215_v31.py`, `out/e215/`)')
        w('')
        w(f"Arm A only: aifoundry3 card 0 at 600 MHz (the round's brief). The never-run scan in E213's form (`out/e215/scan-e215.json`, sha256 "
          f"`{E5.get('scan_sha256')}`), the point rule of item 10 on v3.1's frozen predictor (params sha256 `{E5.get('params_sha256')}`) and MM1-v3's.")
        w('')
        w('| family | grid | never-run candidates (literal) | chosen | post hoc reading: candidates / chosen |')
        w('|---|---|---|---|---|')
        for k, v in E5.get('families', {}).items():
            w(f"| {k} | {v.get('grid_n')} | {v.get('literal_candidates_n')} | {len(v.get('literal_chosen') or [])} of {E5.get('quota_A', {}).get(k)} | "
              f"{v.get('posthoc_candidates_n', '-')} / {len(v.get('posthoc_chosen') or []) if 'posthoc_chosen' in v else '-'} |")
        w('')
        w(f"Card time, desk estimate in E213's run form: {json.dumps(E5.get('card_time_desk'))}.")
        w('')
        import csv as _csv
        cp = os.path.join(O, 'e215', 'mm1_v31_e215.csv')
        if os.path.exists(cp):
            w('| family | reading | how | point (loop, arm, format, kind, mask) | score | v3.1 cycles (wall) | v3 cycles (wall) | v3.1 W over idle | v3 W over idle |')
            w('|---|---|---|---|---|---|---|---|---|')
            for r in _csv.DictReader(open(cp)):
                w(f"| {r['family']} | {r['reading']} | {r['how']} | {r['loop']}, {r['arm']}, {r['fmt']}, {r['kind']}, {r['mask']} | {r['score_abs_ln_v31_over_v3']} | "
                  f"{r['v31_cycles_wall']} | {r['v3_cycles_wall']} | {r['v31_W_over_idle']} | {r['v3_W_over_idle']} |")
            w('')
        for fn in ('mm1_v31_e215.csv', 'mm1_v31_e215.json', 'e215_choice.json'):
            p = os.path.join(O, 'e215', fn)
            if os.path.exists(p):
                w(f"- `out/e215/{fn}`: sha256 `{sha(p)}`")
        w('')
        for ln in X.get('e215_notes', []):
            w(ln)
            w('')
    # ---- 8. departures and NOT RUN
    w('## 8. Departures, gaps and NOT RUN')
    w('')
    for ln in X.get('departures', []):
        w(f"- {ln}")
    w('')
    # ---- 9. files
    w('## 9. Files and how to reproduce')
    w('')
    has3 = os.path.exists(os.path.join(O, 'item3_flat_v31.json'))
    w("Code: `data_v31.py` (the points), `energy_v31.py`, `time_v31.py` (imports `t7_v31.py` unchanged), `fit_v31.py` (the fits and folds), `run_v31.py` "
      "(the declared order of decisions), `summary_v31.py`, `reported_v31.py`, `check_starts_v31.py`, `mm1_v31.py` (the predictor), `e215_v31.py` (the "
      "blind day's points and forecasts), "
      + ("`item3_flat_v31.py` (item 3's identification check and labels, post hoc), " if has3 else '')
      + "`readme_v31.py` (this file). Inputs: `inputs/` (E213's committed data and registered points, census-v3.1, "
      "E212's plan tiles for phi; `inputs/SOURCES.tsv`) and MM1-v3's (`../v3/inputs/`, read in place). Outputs: `out/` (fits in `out/fits/`, E215 in "
      "`out/e215/`). `SHA256SUMS`: every file this commit adds but itself (`sha256sum -c SHA256SUMS` from this folder; the four frozen declaration files' sha256 are in section 1).")
    w('')
    w("From this folder, single-threaded (OMP_NUM_THREADS=1 and the like), each with `/usr/bin/python3 -I -B`: `run_v31.py --out out --tag final "
      "--lanes <the round's lane folders> --scores-A <E213 arm A scores> --scores-B <arm B scores>`; `summary_v31.py --out out`; `reported_v31.py --out "
      "out --scores A=... --scores B=...`; `check_starts_v31.py out`; `e215_v31.py scan --lab <the lab> --lanes <lane folders> --out out/e215`; "
      "`e215_v31.py choose --scan out/e215/scan-e215.json --params out/mm1_v31_params.json --out out/e215`"
      + ("; then `item3_flat_v31.py --out out --label` (post hoc: `out/item3_flat_v31.json` and the labels in `out/decisions_v31.json`'s step3, "
         "new keys only); `readme_v31.py --out out --readme README.md --extra <the lanes' lines>` writes this file" if has3 else '')
      + ".")
    w('')
    open(a.readme, 'w').write('\n'.join(L) + '\n')
    print('README written', len(L), 'lines')


if __name__ == '__main__':
    main()
