#!/usr/bin/env python3
"""E200 registration desk check (reg-e200, Q192): the predicted peak on aifoundry2 card 0 (E200.md section 9). Desk arithmetic of
committed records only: a safety estimate for the stops, not a forecast of any price (E200's forecast is sealed; no number of it is
known to the lab or used here).

    python3 -I -B tools/claims-v3/e200/desk/peaks_e200.py [TOP] > tools/claims-v3/e200/desk/peaks-e200.txt

The arithmetic: E197's aifoundry3 peak over idle (E197.md 9: E192's busiest scalar arm, 8.912 pJ over idle at 2.34 x 10^11
instructions a second, at 2.4 times that rate: about 5 W; its bound, a board under 35 W over an idle near 24 W) is moved to 800 MHz
by the frozen ledger's own rule (every per-instruction price x v2(800) = (V800 / V600)^2 from aifoundry2's frozen volts) and by the
rate (the loop is cycle-bound: 4/3 the instructions a second at 800 MHz), carried to aifoundry2 by E38's card scale, and set on
aifoundry2's own idle (the frozen ledger's footing law), with and without E136's busy base at 800 MHz, which the frozen ledger does
not hold. The die from the card's sustained line (14-card-behaviour.md) and E190 arm A's measured sustained cells, REPORTED.
Each input is read from its committed file, the file's sha256 printed. Standard library only.
"""
import hashlib
import json
import os
import re
import sys

TOP = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
F = {
    'e197': 'tools/claims-v3/e197/E197.md',
    'frozen': 'docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json',
    'e136': 'tools/claims-v3/e136/predictions-e136.json',
    'scale': 'tools/ledger/freeze_ledger_v2.py',
    'card': 'docs/findings/14-card-behaviour.md',
    'e190': 'tools/claims-v3/e190/E190.md',
    'e190data': 'docs/reports/data/2026-11-13-e190-large-gemm/README.md',
    'climb': 'tools/claims-v3/e194/desk/climb-e190.txt',
}
txt = {}
print('E200 desk check: the predicted peak on aifoundry2 card 0 (desk arithmetic of committed records; a safety estimate, not a forecast)')
print('interpreter: %s %s' % (sys.executable, sys.version.split()[0]))
for k, p in F.items():
    b = open(os.path.join(TOP, p), 'rb').read()
    txt[k] = b.decode()
    print('  %s  %s' % (hashlib.sha256(b).hexdigest(), p))


def need(k, pat):
    m = re.search(pat, txt[k], re.S)
    if not m:
        sys.exit('REFUSED: %s does not read as expected (%s)' % (F[k], pat))
    return m


# E197.md 9, quoted
need('e197', r"busiest arm read 2\.09 W over idle on this card\s+\(E192's `add\.a\.all`, 8\.912 pJ over idle at its 2\.34 x 10\^11 instructions a second\); at 2\.4 times that rate")
need('e197', r"E197's peak: about 30 W on the board, under 35 W")
need('e197', r"aifoundry3 idles near 24 W")
pj, rate, k = 8.912e-12, 2.34e11, 2.4
w3 = pj * rate * k
w3_top = 35.0 - 24.0
# the frozen ledger: aifoundry2's volts and idle law
fz = json.loads(txt['frozen'])
v600, v800 = fz['volts']['aifoundry2']['600'], fz['volts']['aifoundry2']['800']
v2 = (v800 / v600) ** 2
q = fz['idle_laws']['aifoundry2']['quad']
band = fz['idle_laws']['aifoundry2']['quad_band_c']
rest_band = fz['idle_laws']['aifoundry2']['rest_band_w']


def idle(t):
    return q['a'] * t * t + q['b'] * t + q['c']


# E136's busy base, relation B
rb = json.loads(txt['e136'])['relation']['B']
base = rb['800'] - rb['600']
# E38's card scale
need('scale', r'aifoundry2 = aifoundry3 / 0\.963 \(E38\'s card scale, band 0\.958-0\.969\)')
cs, cs_top = 1 / 0.963, 1 / 0.958
# the card's lines
need('e190', r'at most 82 W predicted board peak')
need('card', r'the line through the nine runs\' last 40 s reads 65\.5 °C at 50\.3 W of board power \(0\.47 °C per W\)')
rest = need('climb', r"the smoke's 30 s rest: board median ([0-9.]+) W, die median ([0-9]+) C")
sus = re.findall(r'\| A (fp32|fp16|int8) \| 2 \| \*\*[0-9.]+\*\* \([^|]*\) \| [^|]* \| [^|]* \| ([0-9.]+) / ([0-9.]+) \| [^|]* \| ([0-9.]+) → ([0-9.]+) \|', txt['e190data'])

f = v2 * 4.0 / 3.0
print()
print('E197.md 9 (quoted): E192\'s busiest scalar arm on aifoundry3, 8.912 pJ over idle at 2.34e11 instructions a second, at 2.4 times that '
      'rate: %.4f W over idle ("about 5 W"); its bound: a board under 35 W over an idle near 24 W, %.1f W over idle' % (w3, w3_top))
print('v2(800) = (V800 / V600)^2 = (%.10g / %.10g)^2 = %.6f (the frozen ledger\'s aifoundry2 volts); the rate x 4/3 at 800 MHz (cycle-bound '
      'loop): W over idle x %.6f' % (v800, v600, v2, f))
print('E38\'s card scale (aifoundry3 switches 0.958-0.969 of aifoundry2): x %.4f at its point (1/0.963), x %.4f at its band\'s end (1/0.958)' % (cs, cs_top))
print('aifoundry2\'s idle (the frozen footing law, %d-%d C, rest band +-%.1f W): %.3f W at 55 C, %.3f W at %d C; E190 arm A\'s measured rest '
      '%s W at a die of %s C' % (band[0], band[1], rest_band, idle(55), idle(band[1]), band[1], rest.group(1), rest.group(2)))
print('E136\'s busy base on this card (relation B): %.3f W at 600 MHz, %.3f W at 800 MHz: %.3f W the frozen ledger does not hold' % (
    rb['600'], rb['800'], base))
pts = []
w_point = w3 * f
w_point_cs = w_point * cs
w_top = w3_top * f * cs_top
for label, over, idle_t, add_rest, add_base in (
        ('the point', w_point, 55, 0.0, 0.0), ('the point with the card scale', w_point_cs, 55, 0.0, 0.0),
        ('the point with E136\'s base', w_point_cs, 55, 0.0, base),
        ('the top: E197\'s bound, the scale\'s end, the idle at 62 C plus its band, E136\'s base', w_top, band[1], rest_band, base)):
    P = idle(idle_t) + add_rest + over + add_base
    die = 65.5 + 0.47 * (P - 50.3)
    pts.append((label, P, die))
    print('  %-86s %6.2f W over idle -> board %6.2f W; die by the sustained line about %4.1f C' % (label, over + add_base, P, die))
print('All under E189\'s 65 W line (margin %.1f W at the top), aifoundry2\'s 82 W predicted-peak line (E190.md 3) and its 85 W stop. The die at '
      'the points stays under the governor\'s 65 C thermal test; only the stacked top passes it (%.1f C), where THE CLOCK RULE sets the '
      'stepped processes aside, under the 70 C stop.' % (65.0 - pts[-1][1], pts[-1][2]))
print('E190 arm A\'s measured sustained cells on this card (README, REPORTED): %s' % '; '.join(
    '%s board %s W over a %s W rest, die %s -> %s C (last 40 s of 95 s)' % (fmt, b, r, d0, d1) for fmt, b, r, d0, d1 in sus))
ok = all(P < 65.0 for _, P, _ in pts) and all(P < 82.0 for _, P, _ in pts)
print()
print('PEAKS %s' % ('UNDER THE LINES' if ok else 'OVER A LINE'))
