#!/usr/bin/env python3
"""Q130(d) — the BL2 0.22.0 thermal arm read as a constant-POWER clamp.

The 0.22.0 thermal arm is bang-bang on one integer (thermal_pwr_mgmt.c:884-895):
it gives one VMIN point back whenever the 34-sensor integer mean reads
threshold+1, and the power arm (`:898-920`, reached only when the thermal test is
false) takes a point back on any pass where the mean is at or below the
threshold.  In the steady state the die therefore sits ON the trip, so the
board power sits wherever E64's die line puts the trip:

    die_C = a_C + k * board_W                      (E64 surface.txt:27)
 => board_W(trip) = (trip_C - a_C) / k

The trip in whole degrees is a BAND, not a number: 65 is the last reading the
arm lets pass, 66 the first that trips.  So the clamp is a band of board power.
A kind whose 800 MHz power is under the band never trips and keeps 800 MHz; a
kind whose 600 MHz power is over the band pins at the VMIN floor and the die
floats above the trip, because at the floor the arm has no step left
(`:886`) and the `else if` chain still swallows the pass, so the power arm
cannot lift the clock either.

For the kinds in between, each one's own two measured board powers (the medians
at 600 and at 800 MHz) give a clock bracket: the clock at which that kind's
power crosses the band.

Every number here comes from committed E64 files; nothing is fitted.
"""
import json, argparse

A_C, K_C_PER_W = 41.88, 0.4696          # surface.txt:27 (thermal line, SUS last 40 s)
PTS = [(600, 0.517), (700, 0.568), (800, 0.618)]   # the three VMIN minion points

# From the committed E64 run records (results.json, block SUS, 1024 minions):
#   W600/W800  p600_med_w / p800_med_w   — this run's median board power at each point
#   Wsus/die   surface.txt:27 "points"   — the last-40 s sustained board W and die C
#   MHz/s800   README.md:88-98           — the sustained mean clock and share of samples at 800
#   r800/rsus  README.md:88-98           — rate at 800 MHz and sustained (kernel) rate, TFLOPS/TOPS
SUS = [
    # type   kind    W600    W800    Wsus   die   MHz  s800  r800  rsus
    ('fp32', 'zeros', 27.035, 36.41, 36.36, 59.0, 800, 1.00, 12.3, 12.3),
    ('fp16', 'zeros', 27.375, 36.42, 36.09, 59.0, 794, 0.97, 24.6, 24.4),
    ('int8', 'zeros', 27.880, 37.59, 37.56, 59.0, 800, 1.00, 84.4, 84.3),
    ('int8', 'ones',  29.890, 41.72, 41.76, 61.7, 800, 1.00, 84.4, 84.3),
    ('fp16', 'ones',  45.360, 54.57, 49.28, 65.4, 737, 0.48, 24.6, 22.3),
    ('fp32', 'ones',  45.185, 54.43, 49.38, 65.4, 738, 0.48, 12.3, 11.1),
    ('int8', 'randn', 44.420, 53.17, 50.67, 65.3, 763, 0.66, 84.4, 79.5),
    ('fp16', 'randn', 51.470, 63.87, 51.34, 66.1, 600, 0.00, 24.6, 18.4),
    ('fp32', 'randn', 54.270, 67.77, 54.36, 67.1, 600, 0.00, 12.3, 9.2),
]
FLOOR, CEIL = 600, 800


def w_at_die(die_c):
    return (die_c - A_C) / K_C_PER_W


def clock_for(w_target, w600, w800):
    """The clock at which this kind's board power reaches w_target, linear in f
    between its own two measured points, clipped to the VMIN range."""
    if w800 <= w600:
        return None
    f = FLOOR + (CEIL - FLOOR) * (w_target - w600) / (w800 - w600)
    return round(min(max(f, FLOOR), CEIL), 1)


def main(out):
    lo, hi = w_at_die(65.0), w_at_die(66.0)
    rows = []
    for ty, kind, w600, w800, wsus, die, mhz, s800, r800, rsus in SUS:
        f_lo, f_hi = clock_for(lo, w600, w800), clock_for(hi, w600, w800)
        if w800 < lo:
            regime = 'never trips: 800 MHz power is under the band'
        elif w600 > hi:
            regime = 'pinned at the 600 MHz floor: even the floor is over the band'
        else:
            regime = 'in the clamp: the band falls inside the VMIN range'
        rows.append({
            'type': ty, 'kind': kind,
            'board_W_at_600': w600, 'board_W_at_800': w800,
            'sustained_board_W': wsus, 'sustained_die_C': die,
            'sustained_mean_MHz': mhz, 'share_at_800': s800,
            'regime': regime,
            'predicted_MHz_band': [f_lo, f_hi],
            'residual_MHz_vs_band_top': None if f_hi is None else round(mhz - f_hi, 1),
            'rate_at_800': r800, 'rate_sustained': rsus,
            'speed_kept': round(rsus / r800, 3),
        })
    res = {
        'what': 'the 0.22.0 thermal arm as a constant-power clamp, on committed E64 numbers',
        'die_line': {'a_C': A_C, 'k_C_per_W': K_C_PER_W,
                     'source': 'docs/reports/data/2026-10-23-e64-horace-power-limit/surface.txt:27'},
        'trip_semantics': {'test': 'temperature_C > temperature_threshold_C',
                           'source': 'et-platform 836a4ab '
                                     'device-bootloaders/src/ServiceProcessorBL2/services/thermal_pwr_mgmt.c:884',
                           'last_passing_reading_C': 65, 'first_tripping_reading_C': 66},
        'clamp_band_board_W': {'at_65C': round(lo, 2), 'at_66C': round(hi, 2),
                               'width_W': round(hi - lo, 2)},
        'vmin_points_MHz_V': PTS,
        'rows': rows,
    }
    open(out, 'w').write(json.dumps(res, indent=1) + '\n')
    print(f'clamp band {lo:.2f}-{hi:.2f} W board power (trip 65 -> 66 C), width {hi-lo:.2f} W')
    print(f"{'cell':12} {'W600':>6} {'W800':>6} {'Wsus':>6} {'die':>5} {'MHz':>5} "
          f"{'s800':>5} {'pred MHz':>13} {'resid':>6} {'kept':>5}  regime")
    for r in rows:
        b = r['predicted_MHz_band']
        print(f"{r['type']+'/'+r['kind']:12} {r['board_W_at_600']:6.2f} {r['board_W_at_800']:6.2f} "
              f"{r['sustained_board_W']:6.2f} {r['sustained_die_C']:5.1f} {r['sustained_mean_MHz']:5} "
              f"{r['share_at_800']:5.2f} {str(b[0])+'-'+str(b[1]):>13} "
              f"{str(r['residual_MHz_vs_band_top']):>6} {r['speed_kept']:5.2f}  {r['regime']}")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True)
    main(ap.parse_args().out)
