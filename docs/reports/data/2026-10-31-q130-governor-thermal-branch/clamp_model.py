#!/usr/bin/env python3
"""Q130(d) — the BL2 0.22.0 thermal arm read as a constant-POWER clamp.

The 0.22.0 thermal arm is bang-bang on one integer (thermal_pwr_mgmt.c:884-895):
it gives one VMIN point back whenever the 34-sensor integer mean reads
threshold+1, and the power arm (`:898-920`, reached only when the thermal test is
false) takes a point back on any pass where the mean is at or below the
threshold.  In the steady state the die therefore dithers ON the trip, so the
board power sits wherever E64's die line puts the trip:

    die_C = a_C + k * board_W                      (E64 surface.txt:27)
 => board_W(trip) = (trip_C - a_C) / k

The trip in whole degrees is a BAND, not a number: 65 is the last reading the
arm lets pass, 66 the first that trips.  So the clamp is a band of board power.
A kind whose 800 MHz power is under the band never trips and keeps 800 MHz; a
kind whose 600 MHz power is over the band pins at the VMIN floor and the die
floats above the trip, because at the floor the arm has no step left (`:886`)
while the `else if` chain still swallows the pass, so the power arm is reached
only on a pass whose mean happens to read at or below the trip.

For the kinds in between, each one's own two measured board powers (the medians
at 600 and at 800 MHz) give a clock bracket: the clock at which that kind's
power crosses the band.

TWO BOUNDS ON THE BAND, both computed here and both reported:

  (1) WITHIN E64.  The die line is a fit, not an identity.  Its residuals over
      E64's own nine sustained points are +-0.31 C rms = 0.65 W per band edge
      (max 0.52 C = 1.10 W), against a band only 2.13 W wide.  So each edge
      carries +-0.65 W and a cell's regime is only decided when its margin to
      the nearer edge exceeds that.

  (2) ACROSS SESSIONS.  E69's registered drift check FAILED (E69 README:101-118):
      the same cell (fp32 sustained ones, TDP 65 / thr 65) read 49.38 W at
      65.4 C on 23 Oct and 51.89 W at 65.2 C on 27 Oct -- +2.51 W at the same
      die temperature, more than the band's whole width, and 51.89 W is ABOVE
      this band's 51.36 W top.  Against E69's four SUS cells E64's line is off
      by -1.05 to -5.15 C (-2.2 to -11.0 W), all in the same direction.  The
      band is therefore an E64-SESSION quantity, not a card constant.

Every number here comes from committed E64/E69 files; nothing is fitted.
"""
import json, argparse, math, statistics

A_C, K_C_PER_W = 41.88, 0.4696          # surface.txt:27 (thermal line, SUS last 40 s)
PTS = [(600, 0.517), (700, 0.568), (800, 0.618)]   # the three VMIN minion points

# From the committed E64 run records (results.json, block SUS, 1024 minions):
#   W600/W800  p600_med_w / p800_med_w   — this run's median board power at each point
#   Wsus/die   surface.txt:27 "points"   — the last-40 s sustained board W and die C
#   MHz/s800   README.md:88-98           — the sustained mean clock and share of samples at 800
#   ramp       README.md:88-98 "ramp"    — share of the window still ramping (not clamped)
#   r800/rsus  README.md:88-98           — rate at 800 MHz and sustained (kernel) rate, TFLOPS/TOPS
SUS = [
    # type   kind    W600    W800    Wsus   die   MHz  s800  ramp  r800  rsus
    ('fp32', 'zeros', 27.035, 36.41, 36.36, 59.0, 800, 1.00, 0.00, 12.3, 12.3),
    ('fp16', 'zeros', 27.375, 36.42, 36.09, 59.0, 794, 0.97, 0.03, 24.6, 24.4),
    ('int8', 'zeros', 27.880, 37.59, 37.56, 59.0, 800, 1.00, 0.00, 84.4, 84.3),
    ('int8', 'ones',  29.890, 41.72, 41.76, 61.7, 800, 1.00, 0.00, 84.4, 84.3),
    ('fp16', 'ones',  45.360, 54.57, 49.28, 65.4, 737, 0.48, 0.00, 24.6, 22.3),
    ('fp32', 'ones',  45.185, 54.43, 49.38, 65.4, 738, 0.48, 0.00, 12.3, 11.1),
    ('int8', 'randn', 44.420, 53.17, 50.67, 65.3, 763, 0.66, 0.00, 84.4, 79.5),
    ('fp16', 'randn', 51.470, 63.87, 51.34, 66.1, 600.5, 0.00, 0.00, 24.6, 18.4),
    ('fp32', 'randn', 54.270, 67.77, 54.36, 67.1, 600, 0.00, 0.00, 12.3, 9.2),
]
FLOOR, CEIL = 600, 800

# E69's four sustained cells (README:63-79), all fp32 ones, 27 Oct.  Used ONLY to
# bound the transfer of E64's die line to another session: measured board W, measured
# die C, measured sustained MHz, and E69's own verdict on that cell.
E69_SUS = [
    # label                      TDP thr   W      die    MHz   predicted_MHz  verdict
    ('control: TDP 65 / thr 65',  65, 65, 51.89, 65.2, 763.4, 736.5,
     'in the clamp, 11 thermal steps / 0 power steps; but 51.89 W is ABOVE E64 band top 51.36'),
    ('TDP 65 / thr 70',           65, 70, 54.71, 64.2, 800.0, 800.0,
     'clamp gone: 0 thermal steps, share at 800 = 1.00; 800.0 is a CEILING artefact'),
    ('TDP 65 / thr 62',           65, 62, 52.11, 61.2, 790.3, 649.8,
     'E69 reports INCONCLUSIVE, not a result: the die was still climbing 59->62 C at 76 s, '
     'so the cell never equilibrated against its own threshold and the die ended BELOW it'),
    ('TDP 50 / thr 65',           50, 65, 49.95, 61.2, 769.6, 700.0,
     'limiter switched heat->power: 0 thermal steps / 11 power steps; E69 reports its own '
     'speed prediction REFUTED by 70 MHz'),
]


def w_at_die(die_c):
    return (die_c - A_C) / K_C_PER_W


def clock_for(w_target, w600, w800):
    """The clock at which this kind's board power reaches w_target, linear in f
    between its own two measured points, clipped to the VMIN range.

    The interpolation is LINEAR in f while the real P(f) is convex (voltage rises
    with frequency too), so a bracket built this way reads LOW by construction:
    its error is a one-sided bias, not a two-sided uncertainty."""
    if w800 <= w600:
        return None
    f = FLOOR + (CEIL - FLOOR) * (w_target - w600) / (w800 - w600)
    return round(min(max(f, FLOOR), CEIL), 1)


def die_line_residuals():
    """E64's own die line against the nine points it was fitted to (surface.txt:27)."""
    rs = [die - (A_C + K_C_PER_W * wsus) for _, _, _, _, wsus, die, *_ in SUS]
    rms = math.sqrt(sum(r * r for r in rs) / len(rs))
    mx = max(abs(r) for r in rs)
    return {'residual_C': [round(r, 2) for r in rs],
            'rms_C': round(rms, 3), 'rms_W_per_edge': round(rms / K_C_PER_W, 2),
            'max_abs_C': round(mx, 3), 'max_abs_W_per_edge': round(mx / K_C_PER_W, 2)}


def main(out):
    lo, hi = w_at_die(65.0), w_at_die(66.0)
    unc = die_line_residuals()
    e = unc['rms_W_per_edge']
    rows = []
    for ty, kind, w600, w800, wsus, die, mhz, s800, ramp, r800, rsus in SUS:
        f_lo, f_hi = clock_for(lo, w600, w800), clock_for(hi, w600, w800)
        if w800 < lo:
            regime, margin = 'never trips: 800 MHz power is under the band', lo - w800
        elif w600 > hi:
            regime, margin = 'pinned at the 600 MHz floor: even the floor is over the band', w600 - hi
        else:
            regime, margin = 'in the clamp: the band falls inside the VMIN range', None
        row = {
            'type': ty, 'kind': kind,
            'board_W_at_600': w600, 'board_W_at_800': w800,
            'sustained_board_W': wsus, 'sustained_die_C': die,
            'sustained_mean_MHz': mhz, 'share_at_800': s800, 'ramp_share': ramp,
            'regime': regime,
            # how far this cell's DECIDING power is from the nearer band edge, and
            # whether that margin survives the die line's own +-e W per edge
            'regime_margin_W': None if margin is None else round(margin, 2),
            'regime_decided_within_uncertainty': None if margin is None else bool(margin > e),
            # THE POWER FORM of the claim: is the measured sustained board power in the band?
            'sustained_W_in_band': bool(lo <= wsus <= hi),
            'sustained_W_vs_band_W': 0.0 if lo <= wsus <= hi else round(wsus - hi if wsus > hi else wsus - lo, 2),
            # THE CLOCK FORM: a modelled bracket, one-sided low by construction
            'modelled_MHz_bracket': [f_lo, f_hi],
            'bracket_bias_MHz': None if f_hi is None else round(mhz - f_hi, 1),
            'rate_at_800': r800, 'rate_sustained': rsus,
            'speed_kept': round(rsus / r800, 3),
        }
        if ty == 'fp16' and kind == 'zeros':
            row['note'] = ('sustained mean 794 MHz, not 800: thermal share is 0.00 (it never trips) '
                           'and the 6 MHz is E64\'s own ramp share of 0.03 (README.md:92)')
        if ty == 'fp16' and kind == 'randn':
            row['note'] = ('the marginal cell: its 600 MHz power is only %.2f W over the band top, '
                           'inside the die line\'s own +-%.2f W, so the band arithmetic does NOT decide '
                           'its regime -- the card does: sustained mean 600.5 MHz, 600 in every one of '
                           'the last twenty 2 s bins but one (611.1 MHz at t=50 s)' % (w600 - hi, e))
        if ty == 'fp32' and kind == 'randn':
            row['note'] = ('the deeply-over-trip cell: %.2f W over the band top, %.1fx the die line\'s '
                           'own uncertainty; exactly 600 MHz in every sustained bin, and its ring holds '
                           'no governor decision at all after t=24.65 s' % (w600 - hi, (w600 - hi) / e))
        rows.append(row)

    disc = [r for r in rows if r['modelled_MHz_bracket'][1] not in (None,)
            and FLOOR < r['modelled_MHz_bracket'][1] < CEIL]
    biases = [r['bracket_bias_MHz'] for r in disc]
    in_band = [r for r in rows if r['sustained_W_in_band']]

    e69 = []
    for lbl, tdp, thr, w, die, mhz, pred, verdict in E69_SUS:
        pdie = A_C + K_C_PER_W * w
        e69.append({'cell': lbl, 'tdp_w': tdp, 'threshold_c': thr,
                    'measured_board_W': w, 'measured_die_C': die,
                    'E64_line_predicts_die_C': round(pdie, 2),
                    'residual_C': round(die - pdie, 2),
                    'residual_W': round((die - pdie) / K_C_PER_W, 2),
                    'measured_sustained_MHz': mhz, 'E69_registered_prediction_MHz': pred,
                    'E69_verdict': verdict})

    res = {
        'what': 'the 0.22.0 thermal arm as a constant-power clamp, on committed E64 numbers',
        'die_line': {'a_C': A_C, 'k_C_per_W': K_C_PER_W,
                     'source': 'docs/reports/data/2026-10-23-e64-horace-power-limit/surface.txt:27'},
        'die_line_uncertainty': unc,
        'trip_semantics': {'test': 'temperature_C > temperature_threshold_C',
                           'source': 'et-platform 836a4ab '
                                     'device-bootloaders/src/ServiceProcessorBL2/services/thermal_pwr_mgmt.c:884',
                           'last_passing_reading_C': 65, 'first_tripping_reading_C': 66},
        'clamp_band_board_W': {
            'at_65C': round(lo, 2), 'at_66C': round(hi, 2), 'width_W': round(hi - lo, 2),
            'uncertainty_per_edge_W_rms': e, 'uncertainty_per_edge_W_max': unc['max_abs_W_per_edge'],
            'quote_as': '49.2 +- 0.7 to 51.4 +- 0.7 W',
            'scope': 'an E64-SESSION quantity (23 Oct 2026, aifoundry2), NOT a card constant: '
                     'see transfer_bound_E69',
            'at_a_70C_threshold': [round(w_at_die(70.0), 2), round(w_at_die(71.0), 2)],
        },
        'transfer_bound_E69': {
            'what': "E69's registered drift check FAILED (E69 README:101-118): the same cell read "
                    "49.38 W at 65.4 C on 23 Oct and 51.89 W at 65.2 C on 27 Oct, +2.51 W at the same "
                    "die temperature -- more than the band's whole 2.13 W width, and 51.89 W is above "
                    "the band's 51.36 W top. E69 reads it as a thermal-path change, not a governor change.",
            'E64_line_vs_E69_cells': e69,
            'residual_W_range': [min(r['residual_W'] for r in e69), max(r['residual_W'] for r in e69)],
            'consequence': "any cross-session use of this band carries at least this offset; the "
                           "outcome claim (the clamp vanishes at a 70 C threshold) rests on E69's "
                           "DIRECT measurement -- 0 thermal steps, share at 800 = 1.00 -- and needs "
                           "no band arithmetic at all",
        },
        'agreement': {
            'power_form': {
                'claim': 'a thermally clamped cell\'s measured sustained board power lies in the band',
                'n_in_band': len(in_band),
                'cells_in_band': [f"{r['type']}/{r['kind']} {r['sustained_board_W']} W" for r in in_band],
                'of_the_three_discriminating_cells': sum(1 for r in disc if r['sustained_W_in_band']),
            },
            'clock_form': {
                'claim': 'the modelled bracket contains the measured sustained clock',
                'n_discriminating_cells': len(disc),
                'measured_above_bracket_top': sum(1 for b in biases if b > 0),
                'bias_MHz': {'values': biases, 'mean': round(statistics.fmean(biases), 1),
                             'min': min(biases), 'max': max(biases)},
                'why_one_sided': 'linear-in-f interpolation under a convex P(f) must read low, so this '
                                 'is a BIAS, not an rms error; the bracket is a modelled column, not a '
                                 'measurement, and it is in-sample (each cell uses its own 600 and '
                                 '800 MHz board powers)',
                'honest_accuracy_number': "E64-T1's out-of-sample 4.8-9.6 MHz "
                                          "(docs/reports/data/2026-10-27-q129-governor-temperature/README.md:76-87)",
            },
        },
        'vmin_points_MHz_V': PTS,
        'rows': rows,
    }
    open(out, 'w').write(json.dumps(res, indent=1) + '\n')
    print(f'clamp band {lo:.2f}-{hi:.2f} W board power (trip 65 -> 66 C), width {hi-lo:.2f} W, '
          f'+-{e:.2f} W per edge (die-line rms {unc["rms_C"]:.3f} C; max {unc["max_abs_W_per_edge"]:.2f} W)')
    print(f'E64-session scope only: E69 transfer residuals {res["transfer_bound_E69"]["residual_W_range"][0]:+.1f} '
          f'to {res["transfer_bound_E69"]["residual_W_range"][1]:+.1f} W (its drift check FAILED)')
    print(f"{'cell':12} {'W600':>6} {'W800':>6} {'Wsus':>6} {'in band':>7} {'die':>5} {'MHz':>6} "
          f"{'s800':>5} {'bracket':>13} {'bias':>5} {'kept':>5}  regime")
    for r in rows:
        b = r['modelled_MHz_bracket']
        print(f"{r['type']+'/'+r['kind']:12} {r['board_W_at_600']:6.2f} {r['board_W_at_800']:6.2f} "
              f"{r['sustained_board_W']:6.2f} {('YES' if r['sustained_W_in_band'] else 'no'):>7} "
              f"{r['sustained_die_C']:5.1f} {r['sustained_mean_MHz']:6} "
              f"{r['share_at_800']:5.2f} {str(b[0])+'-'+str(b[1]):>13} "
              f"{str(r['bracket_bias_MHz']):>5} {r['speed_kept']:5.2f}  {r['regime']}")
    print(f"power form: measured sustained board W inside the band for "
          f"{res['agreement']['power_form']['of_the_three_discriminating_cells']} of the 3 discriminating cells")
    print(f"clock form: measured ABOVE the bracket top in "
          f"{res['agreement']['clock_form']['measured_above_bracket_top']} of {len(disc)} "
          f"(bias {res['agreement']['clock_form']['bias_MHz']['mean']:+.1f} MHz, one-sided by construction)")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True)
    main(ap.parse_args().out)
