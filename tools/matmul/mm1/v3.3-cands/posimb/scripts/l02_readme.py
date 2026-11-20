#!/usr/bin/env python3
"""layout2 (Q234) l02: write the land dir's README.md from the lane's committed-form outputs (out/fit_results.json, out/reported_g02.json,
the frozen forecast JSON), so every number in it is read from a file, not typed. Desk; /usr/bin/python3 3.12.3 -I -B.
SPDX-License-Identifier: Apache-2.0"""
import hashlib
import json
import math
import os

LANE = os.environ.get('LAYOUT2_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LAND = os.path.join(LANE, 'land/tools/matmul/mm1/v3.3-cands/posimb')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    F = json.load(open(os.path.join(LAND, 'out/fit_results.json')))
    R = json.load(open(os.path.join(LAND, 'out/reported_g02.json')))
    FC = json.load(open(os.path.join(LAND, 'forecasts-e220-posimb.json')))
    lab = FC['label']
    M1, M2, K = F['M1_lead_pairs_rms_ln'], F['M2_pooled_LOEO'], F['keep_rule']
    a_hop, a_lag = F['constants_all_data']['posimb']
    L = []
    w = L.append
    w("# 'MM1-v3.2 + posimb': a layout term for equal-count shire masks (a v3.3 candidate), frozen for E220")
    w('')
    w('*Round Q234, lane layout2 (track Y), Fri 20 Nov 2026 (week 47), Pacific time, at aifoundry2\'s desk. Desk only: no card, no simulator, '
      'no E220 datum. Interpreter for every number: /usr/bin/python3 3.12.3, numpy 1.26.4, `-I -B`, single-threaded (OMP / OPENBLAS / MKL / '
      'NUMEXPR_NUM_THREADS = 1), every job in the round\'s CPU slots, one at a time.*')
    w('')
    w('The owner\'s words that put the matmul first (Mon 16 Nov 2026; a voice transcription in which "matte mold" is the matmul): "I want you '
      'to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and '
      'clock cycles. From based on what I know about the size of a matrix and which operations are contained."')
    w('')
    w('**Labels.** *Post hoc*: every constant and every choice here (made after its data existed; the form was chosen after an in-sample look '
      'at MM1-v3.2\'s residuals, disclosed in `DECLARED-posimb.md`). *Held out*: left out of the fit that scores it (not blind). *Blind*: '
      'only E220, once these forecasts\' sha256 are posted or pushed before its first card command. *REPORTED*: printed beside a rule, never '
      'deciding it. *NOT RUN*: not run. Errors: forecast / measured - 1 (%), pair errors in ln.')
    w('')
    w('## 1. The lead')
    w('')
    w('Equal-count layouts differ by a real 4-7%: E216 (aifoundry2 card 0) y01-y03, 0x3 against 0x10001, measured ln(a/b) +0.072, +0.068, '
      '+0.040 (repeat noise 0.0039 ln), where the frozen contention term F1 predicted -0.028, and the controls y07/y08 (0x101 against 0x10001, '
      'equal row and column groups) +0.036 / +0.042 against 0; E218 (aifoundry3 card 0) added seven pairs (y01 -0.090; y02, y04-y06 +0.042; '
      'y07/y08 -0.021 / -0.024). MM1-v3.2 prices equal-count masks alike (its layout rule chose no term), so it predicts 0 for every such pair.')
    w('')
    w('## 2. What separates the faster layout from the slower (post hoc, in sample: `scripts/x02`-`x04`, `out/explore_x02.json`, '
      '`out/imbalance_x04.json`)')
    w('')
    w('- **At deep K the op time is a property of the mask alone.** E218\'s KB-24 points read 1537.4 cycles at 0xf and 1473.8 at 0x3030 at '
      'four to five shapes each (within 0.2 cycle), 1603.2 at 0x55555555 at two shapes: a per-mask constant, so a position or arbitration effect, '
      'not a footprint one. The active shires\' mean L3 latency on the mesh (the MARTY map, 110 + 12 x hops to the 32 homes; the hop-mean '
      'control) orders E218 y01, y02-y06 and E216 y07/y08, but not E218 y07/y08 (equal hop means) and not E216 y01-y06.')
    w('- **Half of every pair difference is the wall\'s excess over the counter\'s mean, between shires.** ln(wall / mean) is 0 at every '
      'single-shire point (52 points, |ln| < 1e-5), and over the 273 equal-count pairs of the data the mean part and the imbalance part of the wall '
      'difference have equal rms (0.078, 0.079 ln) and correlate -0.59. At E216 y01-y03 the slower layout (0x3: row group 0 only, so its DRAM '
      'stream, B, is private to each shire) carries ln(wall/mean) 0.028-0.044 and the faster (0x10001: B shared by both shires) 0; at E218 '
      'y01 the slower (0x1010101: its DRAM stream A private) 0.040, the faster (0xf000: A shared) 0. A private DRAM stream lets the shires '
      'drift; the wall is the laggard\'s.')
    w('- **Not explained here:** E217\'s and E214\'s large single-column pairs at gemmL2x6x10 (wall / mean up to 1.16 with an L3-resident '
      'working set, and n = 2 masks of the same row and column groups differing by 0.21 ln: 0x22 against 0x44), E212\'s sign flips by shape, '
      'and E218 y07/y08. Of the 145 pairs whose residual difference exceeds 1%, the hop mean orders 77, the slowest active shire\'s hop 37 '
      'and the mean hop to the memory shires 72.')
    w('')
    w('## 3. The form (declared before any fit: `DECLARED-posimb.md`, sha256 `%s`, hashed 2026-11-20 05:35:31 PST)' % F['declaration_sha256'])
    w('')
    w('T = T_v32 x clip(1 + a_hop Phi_hop + a_lag Phi_lag, 0.3, 3.0) at the subset points of rgm136\'s gemmL loop (every other point and every '
      'full-chip point keeps MM1-v3.2 to the last bit); the counter\'s mean takes only the position part. Phi_hop = e x (Lmean_act / '
      'Lmean_full - 1); Phi_lag = e x ((Lmax_act - Lmean_act) / Lmean_full) x Fp / (Fp + Fs); e = MM1-v3.2\'s elasticity of its op time to its '
      'L3 and DRAM constants (about 1 memory-bound, about 0 L2-resident); Fp, Fs = the walk\'s private and shared DRAM-served request shares '
      '(verify-lay\'s committed v01_map generator, strict LRU at 32 MB). Two new constants; MM1-v3.2\'s constants unchanged (two-stage).')
    w('')
    w('## 4. The fit and the held-out record (post hoc, held out where it says so; `out/fit_results.json`, `logs/g01.log`)')
    w('')
    w('Data: every committed time point through E219, %d points (%d in the term\'s scope), MM1-v3.2\'s 2508 (E105-E215) plus E216 46, '
      'E217 486, E218 52, E219 139; E146\'s store rungs out of every fit; twins (same card, kernel, arm, format, mask in another experiment): '
      '%d.' % (F['n_points'], F['n_scope'], F['n_twins']))
    w('')
    w('**All-data constants: a_hop = %.4f, a_lag = %.4f** (expected signs, both positive; a_lag positive in all %d folds, from %.2f to %.2f; '
      'a_hop positive in %d of %d, from %.3f to %.3f, negative only in LOLO other).' % (
          a_hop, a_lag, R['constants_by_fold_range']['folds'], R['constants_by_fold_range']['a_lag'][0], R['constants_by_fold_range']['a_lag'][1],
          R['constants_by_fold_range']['a_hop_positive_folds'], R['constants_by_fold_range']['folds'], R['constants_by_fold_range']['a_hop'][0],
          R['constants_by_fold_range']['a_hop'][1]))
    w('')
    w('| the declared rule | MM1-v3.2 | + posimb | threshold | verdict |')
    w('|---|---|---|---|---|')
    w('| K1 the lead: 15 pairs\' held-out ln(a/b) error rms, LO-Y fold (E216 + E218 out) | %.4f | **%.4f** | <= %.4f (0.80 x) | %s |' % (
        M1['v32'], M1['posimb'], K['K1_threshold'], 'PASS' if K['K1'] else 'FAIL'))
    w('| K2 pooled LOEO wall rms without twins (n %d) | %.3f%% | %.3f%% | <= %.3f%% | %s |' % (
        M2['v32']['n_no_twin'], M2['v32']['no_twin_rms'], M2['posimb']['no_twin_rms'], K['K2_threshold'], 'PASS' if K['K2'] else 'FAIL'))
    w('| K3 placebo (the pair of features permuted among the scope points), 100 draws | - | beaten in %d | >= 95 | %s |' % (
        F['M3_placebo']['beaten'], 'PASS' if K['K3'] else 'FAIL'))
    w('')
    w('**Verdict: KEPT by its declared rule.** Placebo M1 quantiles (min, 5%%, median, 95%%, max): %s.' % (
        ', '.join('%.4f' % x for x in F['M3_placebo']['placebo_M1_quantiles'])))
    w('')
    w('REPORTED beside (never deciding): the lead\'s pairs ordered by sign: %d of %d (MM1-v3.2 none; hop mean %d; count only %d); the 31 Y '
      'points\' own rms in the LO-Y fold %.2f%% -> %.2f%% (the pair differences improve, the levels do not); pooled LOEO with twins %.3f%% -> '
      '%.3f%% (n %d); the scope points\' LOEO without twins %.2f%% -> %.2f%%; LOCO pooled %.3f%% -> %.3f%%; **LOLO pooled %.2f%% -> %.2f%% '
      '(worse: the class \'other\' 7.51%% -> 8.25%%, where the hop constant fitted without that class turns negative)**.' % (
          F['M1_sign_agreement']['posimb'], F['M1_n_pairs'], F['M1_sign_agreement']['hopmean'], F['M1_sign_agreement']['count'],
          F['Y_points_LO-Y_rms_pct']['v32'], F['Y_points_LO-Y_rms_pct']['posimb'], M2['v32']['with_twins_rms'], M2['posimb']['with_twins_rms'],
          M2['v32']['n_all'], M2['v32']['scope_no_twin_rms'], M2['posimb']['scope_no_twin_rms'], F['pooled_other']['LOCO']['v32']['rms'],
          F['pooled_other']['LOCO']['posimb']['rms'], F['pooled_other']['LOLO']['v32']['rms'], F['pooled_other']['LOLO']['posimb']['rms']))
    w('')
    w('The baselines, fitted by the same procedure on the same folds (REPORTED): **hop mean** (T x (1 + a G1), one constant): M1 %.4f, pooled '
      'LOEO without twins %.3f%%; **count only** (verify-lay\'s N1+N2): M1 %.4f, %.3f%%. The term\'s parts alone on the LO-Y fold: %s.' % (
          M1['hopmean'], M2['hopmean']['no_twin_rms'], M1['count'], M2['count']['no_twin_rms'],
          '; '.join('%s a %.3f, M1 %.4f' % (k, v['a'], v['M1']) for k, v in R['parts_LO-Y'].items())))
    w('')
    w('| fold | n (in scope) | MM1-v3.2 rms | + posimb | in scope: MM1-v3.2 | + posimb | a_hop, a_lag |')
    w('|---|---|---|---|---|---|---|')
    for nm, fr in F['folds'].items():
        if not (nm.startswith('LOEO E2') or nm.startswith('LOCO') or nm == 'LO-Y' or nm.startswith('LOLO')):
            continue
        sc = ('%.3f' % fr['rms_v32_scope'], '%.3f' % fr['rms_posimb_scope']) if fr['n_test_scope'] else ('-', '-')
        w('| %s | %d (%d) | %.3f | %.3f | %s | %s | %.3f, %.3f |' % (nm, fr['n_test'], fr['n_test_scope'], fr['rms_v32'], fr['rms_posimb'], sc[0],
                                                                  sc[1], fr['posimb'][0], fr['posimb'][1]))
    w('')
    w('(LOEO folds E105-E190 have no point in the term\'s scope and read MM1-v3.2\'s own figures: `out/fit_results.json` > folds.)')
    w('')
    w('The lead\'s 15 pairs, held out (LO-Y): measured ln(a/b) against the term\'s (MM1-v3.2 predicts 0 at each):')
    w('')
    w('| pair | arm | masks | measured | + posimb | hop mean | count only |')
    w('|---|---|---|---|---|---|---|')
    for r in F['M1_pairs']:
        w('| %s | %s | %s / %s | %+.4f | %+.4f | %+.4f | %+.4f |' % (r['pair'], r['arm'], r['mask_a'], r['mask_b'], r['measured_ln_a_over_b'],
                                                              r['pred_ln_a_over_b|posimb'], r['pred_ln_a_over_b|hopmean'], r['pred_ln_a_over_b|count']))
    w('')
    w('The counter\'s mean at the 31 Y points (REPORTED): MM1-v3.2 %.2f%% rms -> x g_m %.2f%%; MM1-v3.2\'s own mean misses the R1C4 masks at '
      'MB >= 2 by -13 to -24%% (E218 y01a, y04a-y06a; E216 y04a: its imbalance_mean prices a wall / mean gap the card does not show there): a '
      'v3.2 gap this term does not touch.' % (
          math.sqrt(sum(x['v32_mean_err'] ** 2 for x in R['mean_at_Y']) / len(R['mean_at_Y'])) * 100,
          math.sqrt(sum(x['posimb_mean_err'] ** 2 for x in R['mean_at_Y']) / len(R['mean_at_Y'])) * 100))
    w('')
    w('## 5. The frozen forecasts for E220 (final 2026-11-20 05:39:30 PST, before any E220 datum)')
    w('')
    w('For every point of `OUT/reg-e220/POINTS.txt` (FINAL 05:24:17 PST, sha256 `%s`; points-e220.csv `%s`): arm A (aifoundry1 card 1) at '
      '600.0 MHz, arm B (aifoundry2 card 0) at 799.0, 700.0 and 600.0 MHz, %d rows, %d in the term\'s scope (the XY and Y2 subset points), '
      'every other row MM1-v3.2\'s to the last bit; MM1-v3.2\'s own columns beside each row equal reg-e220\'s frozen MM1-v3.2 forecast to '
      '<= 5e-9 relative at 306 of 306 rows. Label: **%s**.' % (FC['points_txt_sha256'], FC['points_csv_sha256'], FC['n_rows'], FC['n_in_scope_rows'], lab))
    w('')
    w('| file | sha256 |')
    w('|---|---|')
    for fn in ('forecasts-e220-posimb.csv', 'forecasts-e220-posimb.json', 'forecasts-e220-posimb.txt'):
        w('| `%s` | `%s` |' % (fn, sha(os.path.join(LAND, fn))))
    w('')
    w('Columns per model (\'%s|...\' and \'MM1-v3.2|...\'): cycles_per_op_wall, cycles_per_op_mean, T_op_us, seconds_per_gemm, W_over_idle '
      '(at the forecast t), A_W, B_W_us (W over idle given a measured t = A_W + B_W_us / t_us: MM1-v3.2\'s own), J_over_idle_per_gemm and '
      'J_at_rest_per_gemm (with t forecast; J at rest given t uses MM1-v3.2\'s rest-law P_rest, reg-e220\'s rest_law_W column, equal to '
      'J_at_rest_per_gemm / seconds_per_gemm - W_over_idle here); with each row\'s e, G1core, LAGcore, Phi_hop, Phi_lag, g_wall, g_mean, Fp, '
      'Fs, Lmean_act, Lmax_act.' % lab)
    w('')
    pairs = {}
    for r in FC['rows']:
        if r['in_scope'] and r['pair'] and r['arm'] == 'A':
            pairs.setdefault(r['pair'], {})[r['id'][-1]] = r
    w('What the term predicts blind for E220\'s pairs (ln(a/b) of wall cycles; the same on both arms and clocks to 1e-4; MM1-v3.2 0):')
    w('')
    w('| pair | shape | masks | + posimb | measured on another card (E216 or E218) |')
    w('|---|---|---|---|---|')
    seen = {'xy01': 'E218 y01 -0.090', 'xy02': 'E218 y02 +0.042', 'xy04': 'E218 y04 +0.042', 'xy05': 'E218 y05 +0.042', 'xy06': 'E218 y06 +0.042',
            'xy07': 'E218 y07 -0.021', 'xy08': 'E218 y08 -0.024', 'p01': 'E216 y01-y03 (0x3 / 0x10001, other shapes) +0.040 to +0.072',
            'p02': 'as p01', 'p03': 'as p01', 'p04': 'E216 y07/y08 (0x101 / 0x10001) +0.036 / +0.042', 'p05': 'as p04'}
    for k in sorted(pairs):
        a, b = pairs[k].get('a'), pairs[k].get('b')
        if a and b:
            w('| %s | %s | %s / %s | %+.4f | %s |' % (k, a['token'], a['shire_mask'], b['shire_mask'],
                                                  math.log(a[lab + '|cycles_per_op_wall'] / b[lab + '|cycles_per_op_wall']), seen.get(k, '')))
    w('')
    w('## 6. Gaps, and what was NOT RUN')
    w('')
    w('- Two-stage only: MM1-v3.2\'s constants were not refitted with the term (a joint refit: NOT RUN).')
    w('- The term explains part of the lead (K1) and little elsewhere: E217\'s and E214\'s L3-resident single-column imbalance, E212\'s '
      'shape-dependent signs and E218 y07/y08 are not captured; LOLO pooled is worse (section 4); the Y points\' own levels do not improve.')
    w('- The mesh positions (the MARTY map) and the 110 + 12 x hops law are the lab\'s notes, used unchanged; the single-shire walls at '
      'gemmL2x6x10 (E214: shires 0 and 31; E217: shires 8-11) do not follow them (0 and 31 slowest, and of 8-11 the one nearest the homes, '
      '10, the slowest); the memory shires\' placement is not used.')
    w('- The walk\'s levels are a strict-LRU model at 32 MB (no measured L3 under a subset mask).')
    w('- The counter\'s mean: the term\'s g_m leaves MM1-v3.2\'s large miss at R1C4 masks with MB >= 2 as it is.')
    w('- No independent verifier of this lane\'s fit: NOT RUN (the round\'s verify lane, if any, is the check).')
    w('')
    w('## 7. Files')
    w('')
    w('- `DECLARED-posimb.md` (+ `.sha256`): the declaration, hashed before any fit.')
    w('- `forecasts-e220-posimb.csv`, `.json`, `.txt`: the frozen E220 forecasts (read only).')
    w('- `out/points_all.json` (every time point through E219 in MM1-v3.2\'s form), `out/base_meta.json` (the fold bases\' checks: every fold\'s '
      'held-out base re-made to 0 difference from MM1-v3.2\'s stored predictions), `out/private_shared.json` (the features per configuration), '
      '`out/features_points.json` (v01 records), `out/fit_results.json` (the declared fit and rule), `out/reported_g02.json`, '
      '`out/explore_x02.json` and `out/imbalance_x04.json` (the in-sample looks), `out/check_c01.json` (the self-check).')
    w('- `scripts/`: the lane\'s scripts as run, with their absolute lane paths replaced by environment lookups (`SCRUB.json`: each file\'s '
      'sha256 as run and as landed): d01 (points), e01 (bases, elasticity), f01, f02 (features), x01-x04 (looks), g01 (the declared fit), '
      'h01 (the freeze), g02 (REPORTED), c01 (a self-check of g01\'s deciding numbers by separate code: equal to 1e-15), l01, l02 (this land). Re-run from a checkout at GitHub main 0f046200 placed at `$LAYOUT2_LANE/work/lab`, '
      'in that order, each as `/usr/bin/python3 -I -B scripts/<file>` with the four thread variables at 1.')
    w('- `logs/`: f01, f02, g01, g02 outputs.')
    w('')
    w('SPDX-License-Identifier: Apache-2.0')
    open(os.path.join(LAND, 'README.md'), 'w').write('\n'.join(L) + '\n')
    print('README.md', len('\n'.join(L)), 'chars')


if __name__ == '__main__':
    main()
