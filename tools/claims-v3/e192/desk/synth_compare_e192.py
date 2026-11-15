"""E192 desk check of code (reg-e192, Q176): set the registered reducer's output for a SYNTHETIC session (synth_session_e192.py)
beside the values injected into it. Nothing here is measured or forecast; the injected values are arbitrary test values.

    /usr/bin/python3 -I -B synth_compare_e192.py OUTDIR/injected.json OUTDIR/intbits.json [--exact]
Prints the per-arm energies and contrasts, the ladders (board; rail over its synthetic 0.79 share), the fitted temperature
slope, the per-run fields the registered sanity checks read, and a line per ladder: reduced - injected (in SE units).
Exit 0 when every ladder of both meters is within its tolerance of the injected value: --exact (a noise-free session):
0.5 fJ, or 0.005 pJ for the pJ items; otherwise 5 SE + 0.5 fJ (0.02 pJ), and the count beyond 3 SE is printed.
"""
import json
import math
import sys

inj = json.load(open(sys.argv[1]))
red = json.load(open(sys.argv[2]))
EXACT = '--exact' in sys.argv
E = inj['E_arm_pJ']
share = inj['rail_share']
print('synthetic session: pvt codes %s; passes %s (warm-up %s)' % (inj['pvt'], red['passes'], red['warmup']))
runs = red['runs']
used = [r for r in runs if [r['host'], r['pass']] != red['warmup']]
print('runs reduced: %d (%d ok); roles %s' % (len(runs), sum(r['ok'] for r in runs),
                                              sorted({r['role'] for r in runs})))
rates = [r['rate'] for r in used if r['role'] == 'arm']
rob = [r['ret_over_body'] for r in used]
print('per-run fields the registered sanity checks read (used passes): rate spread across arm runs %.4f%%; retired/body %.6f-%.6f '
      '(259/256 = %.6f); l1d_miss total %d; icache_miss per run %s; mhz %s; V_rail %.4f-%.4f V; board dips %d; off-protocol %d' % (
          100 * (max(rates) / min(rates) - 1), min(rob), max(rob), 259 / 256, sum(r['l1d_miss'] for r in used),
          sorted({r['icache_miss'] for r in used}), sorted({r['mhz'] for r in used}), min(r['V_rail'] for r in used),
          max(r['V_rail'] for r in used), sum(r['board_dips'] for r in used),
          sum(1 for r in used if r['approach_on_protocol'] is False)))
print('beta (W per C), fitted: board %.4f, rail %.4f; injected slope %.3f (rail x %.2f)' % (
    red['beta_W_per_C']['board'], red['beta_W_per_C']['rail'], inj['K_T_W_per_C'], share))
print()
print('%-12s %8s | %16s %16s | %-11s %8s %16s' % ('arm', 'inj pJ', 'board pJ/idle', 'rail/0.79', 'control', 'inj d', 'contrast (corr)'))
for a in sorted(red['arms']):
    rec = red['arms'][a]
    b, r = rec['pJ_board_over_idle'], rec['pJ_rail_over_idle']
    c = rec.get('contrast_pJ_board')
    ctl = rec.get('control', '-')
    print('%-12s %8.4f | %8.4f +- %5.4f %8.4f +- %5.4f | %-11s %8s %16s' % (
        a, E[a], b['mean'], b['se'], r['mean'] / share, r['se'] / share, ctl,
        '%.4f' % (E[a] - E[ctl]) if ctl != '-' else '-',
        '%.4f +- %.4f' % (c['mean'], c['se']) if c else '-'))
print()
bad = beyond3 = 0
for meter, scale in (('board', 1.0), ('rail', share)):
    print('ladders, %s%s (registered names; corrected to the control chain\'s temperature, the primary):' % (
        meter, '' if scale == 1.0 else ' / %.2f' % share))
    for k, want in sorted(inj['expected_ladders_fJ'].items()):
        v = red['ladders'][meter].get(k)
        if not v:
            print('  %-36s  (none)' % k)
            continue
        m, se = v['mean'] / scale, (v['se'] or 0.0) / scale
        if EXACT:
            tol = 0.005 if k.endswith('_pJ') else 0.5
        else:
            tol = 5 * se + (0.02 if k.endswith('_pJ') else 0.5)
            beyond3 += bool(se) and abs(m - want) > 3 * se
        ok = abs(m - want) <= tol
        bad += not ok
        print('  %-36s  injected %9.4f  reduced %9.4f +- %7.4f  diff %+8.4f (%+.1f SE)  %s  [%s]' % (
            k, want, m, se, m - want, (m - want) / se if se else float('nan'), 'ok' if ok else 'OFF', v.get('reading', '')))
print()
print('SYNTH CHECK (%s): %s (%d ladder values outside the tolerance%s)' % (
    'noise-free, exact to 0.5 fJ / 0.005 pJ' if EXACT else '5 SE + 0.5 fJ / 0.02 pJ', 'CONSISTENT' if bad == 0 else 'INCONSISTENT',
    bad, '' if EXACT else '; %d beyond 3 SE of 48' % beyond3))
sys.exit(1 if bad else 0)
