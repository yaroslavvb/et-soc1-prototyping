#!/usr/bin/env python3
"""Imaging physics: how much thermal contrast does "the arrangement of the computation" make on the ET-SoC-1, where
could a camera or the on-die sensors see it, and how does it scale with the clock?

The owner's question of 30 September 2026 (~15:45 PDT): run the chip much slower (100 MHz, even 10 MHz), without the
heatsink, and point the thermal camera at it to see how the computation is arranged.  This script answers the imaging
half: the contrast a pattern of active shires makes on (a) a delidded die, (b) the lid top, (c) the 34 on-die sensors
with the heatsink on, for switching power scaled as f*V^2 from 600 MHz down to 10 MHz; then the camera's noise, and
the least power per shire (so the least clock) at which a pattern is visible, with and without lock-in, and how long
it takes.  Whether a bare card survives at those clocks is not computed here (nohs_calc.py, section D, and its
successors).

Every input names its source (paths relative to the repository root) or is marked ASSUMED / ESTIMATE.  Uncertain
inputs are drawn in a Monte Carlo (uniform; log-uniform where written LU), seed 20260930; outputs are 5th / 50th /
95th percentiles unless a line says otherwise.  Pure arithmetic: no card is touched.

THE MODEL (section B).  Heat conduction, steady and periodic in time, in a stack of laterally uniform layers
(thermal quadrupoles / transfer matrices, e.g. Maillet et al., "Thermal Quadrupoles", Wiley 2000).  For each lateral
Fourier mode q of the power map and each Laplace variable s (0: steady; i*2*pi*f: lock-in at f; real: a step, inverted
by Stehfest's method), each layer (thickness d, conductivities k_xy, k_z, volumetric heat capacity rho*c) has
gamma = sqrt((k_xy q^2 + rho c s) / k_z), and a layer maps the admittance Y = flux/temperature on its far face to its
near face:  Y_near = (k_z gamma tanh(gamma d) + Y_far) / (1 + Y_far tanh(gamma d) / (k_z gamma)).  The power map is
injected at one plane (the transistors); temperature there is S / (Y_up + Y_down), and on any face above it follows
from the layer ratios  theta_far / theta_near = sech(gamma d) / (1 + Y_far tanh(gamma d) / (k_z gamma)).
Assumptions:
  1. Layers are laterally uniform and infinite (no die, lid or substrate edges); the lateral period is 24 shire
     pitches (89 mm), so neighbouring images of the pattern sit 89 mm away.  Edge shires of the real die sit near its
     edge, which this does not model; the patterns' contrasts are taken on interior shires where it can.
  2. Heat is made in one plane at the die's face on the substrate side (flip chip), uniformly over each active
     shire's 3.72 x 3.72 mm tile.  A shire's sensor is taken at its tile's centre (ASSUMED; its place is not known).
  3. Linear: contrast scales with power per shire.  Leakage feedback on local temperature is left out: the die's
     leakage slope, 0.65 W/C at 80 C over 34 shires (11-thermal-model.md), is 0.02 W/C per shire, against local
     resistances of well under 1 C/W per shire here, so it changes a contrast by at most a few per cent.
  4. Each open surface loses heat through one linearised coefficient h (convection + radiation).  The heatsink is a
     spreading base plate with its fins lumped into h at the base top.
  5. The camera sees emissivity x surface temperature; the room's reflection is not modulated and cancels in a
     difference or lock-in image.  A semi-transparent bare silicon die would show some of the transistor plane too;
     the die top is used (the lower contrast).
  6. Switching power per shire scales as f * V^2 (activity per cycle unchanged).  The idle (leakage) power does not
     enter a contrast; it sets the die's mean temperature, which only the camera's NETD depends on here.

Sections:  A inputs     B the conduction model, its checks     C contrast per watt per shire, steady
           D lock-in (periodic) response     E a transient check against the heat-placement measurement (MAP)
           F camera and sensor noise     G least power per shire and least clock; time to see each pattern
"""
import argparse
import json
import math
import os

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('--draws', type=int, default=240, help='Monte Carlo draws (default 240)')
ap.add_argument('--map-draws', type=int, default=120, help='draws for the transient check (default 120)')
ap.add_argument('--json', default=None, help='also write the summary numbers to this JSON file')
args = ap.parse_args()

SEED = 20260930
rng = np.random.default_rng(SEED)
N = args.draws


def U(lo, hi, n=N):
    return rng.uniform(lo, hi, n)


def LU(lo, hi, n=N):
    return np.exp(rng.uniform(math.log(lo), math.log(hi), n))


def pct(x, p=(5, 50, 95), scale=1.0, fmt='{:.3g}'):
    x = np.asarray(x, dtype=float) * scale
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return 'n/a'
    return ' / '.join(fmt.format(v) for v in np.percentile(x, p))


def hdr(t):
    print()
    print('=' * 110)
    print(t)
    print('=' * 110)


OUT = {'seed': SEED, 'draws': N}

hdr('A. Inputs')
# ---- die and grid --------------------------------------------------------------------------------------------------
# Shire pitch 3.73 mm E-W, 3.70 N-S, one mesh hop 3.72 mm (inferred from the die plot scaled to 570 mm2):
#   docs/reports/data/2026-09-27-chip-diagram/facts.json facts["chip.hop-pitch"]; docs/findings/05-claims.md:340.
PITCH = 3.72e-3
# Die 25.6 x 22.2 mm, 570 mm2 (facts.json chip.die-area, chip.die-dims; nohs_calc.py section A)
A_DIE = 25.6e-3 * 22.2e-3
# The 6 x 6 grid in the latency map's (logical) orientation, the die turned a quarter (facts.json mesh.orientation):
#   docs/reports/data/2026-09-28-heat-placement/heat.json placements.grid.  "M/S" = master or spare shire (idle here),
#   "IO/PCIe" = the I/O and PCIe shires; the I/O shire's sensor (TS34) sits in one of the two (not known which).
GRID = [["S0", "S8", "S3", "M/S", "IO/PCIe", "IO/PCIe"],
        ["S24", "S16", "S4", "S12", "S20", "S28"],
        ["S9", "S1", "S13", "S21", "S29", "S5"],
        ["S25", "S17", "S14", "S22", "S30", "S6"],
        ["S2", "S10", "S18", "S26", "S15", "S7"],
        ["S11", "S19", "S27", "M/S", "S23", "S31"]]
COMPUTE = {(r, c) for r in range(6) for c in range(6) if GRID[r][c].startswith('S') and GRID[r][c] != 'S'}
assert len(COMPUTE) == 32
_hp = 'docs/reports/data/2026-09-28-heat-placement/heat.json'
if os.path.exists(_hp):
    assert json.load(open(_hp))['placements']['grid'] == GRID, 'grid differs from heat.json'
    print('grid: matches', _hp)

# ---- layers (thicknesses, conductivities) ---------------------------------------------------------------------------
t_die = U(0.45e-3, 0.775e-3)          # ASSUMED as nohs_calc.py A: thinned 0.45 mm .. full 300 mm wafer 0.775 mm
k_si = U(110.0, 150.0)                # W/mK at 50-90 C, as nohs_calc.py G
RHOC_SI = 2330 * 705                  # as nohs_calc.py A
t_bump = U(0.06e-3, 0.10e-3)          # ASSUMED: C4 bumps + underfill
kz_bump = U(5.0, 15.0)                # ESTIMATE: >30,000 bumps on 570 mm2 (Hot Chips 33, page ref [3]) = 0.14 mm pitch;
#                                       ~0.08 mm bumps fill ~26 % of the area with solder/Cu (k ~50) in underfill (~0.6)
KXY_BUMP = 0.7                        # ASSUMED: underfill-dominated in-plane
t_tim1 = U(0.03e-3, 0.15e-3)          # ASSUMED as nohs_calc.py A (bumps + TIM1 there 0.10-0.25 mm)
Rpp_tim1 = U(0.5e-5, 3e-5)            # m2K/W, 0.05-0.3 K cm2/W, as nohs_calc.py G
H_LID_REF = 1.91e-3                   # lid top to substrate top, datasheet Fig. 9-1 (nohs_calc.py A)
t_lid = np.clip(H_LID_REF - t_die - t_bump - t_tim1, 0.6e-3, 1.4e-3)   # DERIVED as nohs_calc.py A
K_CU, RHOC_CU = 390.0, 8960 * 385
t_sub = U(1.0e-3, 1.61e-3)            # ASSUMED: up to the 1.61 mm max stack of nohs_calc.py A
kxy_sub = U(20.0, 60.0)               # ESTIMATE: organic build-up substrate with Cu planes, in-plane
kz_sub = U(1.0, 4.0)                  # ESTIMATE: through-plane with thermal vias under the die
rhoc_sub = U(1.9e6, 2.4e6)            # ESTIMATE as nohs_calc.py A
Rpp_rest = LU(1e-4, 1.5e-3)           # ASSUMED: balls + board below the substrate as one film, chosen so that the
#                                       whole down path matches nohs_calc.py G's R"_down 5-20 K cm2/W (printed below)
Rpp_tim2 = U(1e-5, 5e-5)              # 0.1-0.5 K cm2/W, as nohs_calc.py G
t_base = U(3e-3, 8e-3)                # ASSUMED: heatsink base plate, aluminium
K_AL, RHOC_AL = 200.0, 2700 * 897
RHOC_TIM = 2.0e6                      # ASSUMED; thin layers, immaterial
T_TIM2 = 50e-6                        # ASSUMED
# ---- surface heat-transfer coefficients (W/m2K) ---------------------------------------------------------------------
h_still = U(8.0, 23.0)                # still air 8-15 (nohs_calc.py G) + up to 8 of radiation from a black-coated face
h_fan = U(29.0, 60.0)                 # 1-2.5 m/s fan: nohs_calc.out B lid 29 / 40 / 54, + radiation
h_win = LU(5e3, 2e4)                  # delidded die under an IR-window liquid cooler, as nohs_calc.py G
h_hs = LU(60.0, 300.0)                # ESTIMATE: fins referred to the base; ~1.3 C/W sink-to-air (11-thermal-model.md
#                                       stages 3-6) over a ~0.008 m2 base = ~100 W/m2K.  Immaterial to contrast.

Rdown = t_bump / kz_bump + t_sub / kz_sub + Rpp_rest
print(f'lid plate mm {pct(t_lid, scale=1e3)}; die mm {pct(t_die, scale=1e3)}')
print(f'down path R" (bumps + substrate + board film) K cm2/W: {pct(Rdown, scale=1e4)}   (nohs_calc.py G: 5-20)')
R1d = (t_die / k_si + Rpp_tim1 + t_lid / K_CU + Rpp_tim2) / A_DIE
print(f'1-D die-to-heatsink-base resistance over the die area, C/W: {pct(R1d)}   (the fitted Foster chain\'s two fast '
      f'stages, which sit between die and base: R1+R2 = 0.156 C/W, 11-thermal-model.md:29-31; the rest of the '
      f'difference is spreading, which the spectral model has)')

# ---- per-shire switching power at 600 MHz --------------------------------------------------------------------------
# fp32 random-normal TensorFMA on all 32 minions of a shire (the hottest kernel in the record):
#   +27.1 W board over idle on 1,024 minions, aifoundry2 80 C = 0.85 W per shire (10-data-dependent-power.md:39,41);
#   heat-placement 4-shire blocks (B4NE/B4SW, 128 minions): 2.87-3.11 W board on aifoundry3 (reductions/dev-r3.json),
#   2.45-2.77 W on aifoundry1 card 1 (val.json) = 0.61-0.78 W per shire; 512 minions on 16 shires 12.5-13.9 W.
#   An eighth to a sixth of arithmetic's added watts is off-die, in the regulators (19-observability...md:64-66).
#   So on the die: 0.51-0.76 W per shire.  Drawn U(0.60, 0.76) (revised 30 Sep, review): aifoundry3's 4-shire blocks
#   (0.60-0.68) to aifoundry2's 16- and 32-shire runs (0.65-0.76, 0.71-0.75); card 1's blocks (0.51-0.61) are left
#   out, since card 1 is not a candidate for any of these views.  (Was U(0.55, 0.75), 8-10 % below aifoundry2's runs.)
P600 = U(0.60, 0.76)
V600, VFLOOR = 0.517, 0.398           # 600 MHz at 0.517 V (16-dvfs-and-leakage.md, aifoundry2); firmware's minion-rail
#                                       floor 400 mV (facts.json volt.minion: limits 400-620 mV), which reads 398 mV on
#                                       the die (card 0 runs 300 MHz there, 14-card-behaviour.md:148-149); 398 mV as
#                                       lowclock_calc.py (was 400 mV here)
CLOCKS = [600, 300, 100, 50, 25, 10]


def vfloor(f):
    """V at clock f when the voltage is lowered with it: floor 0.398 V at and below 300 MHz, linear to 0.517 V at 600
    (ASSUMED shape between the two measured points)."""
    f = np.asarray(f, dtype=float)
    return np.where(f <= 300, VFLOOR, VFLOOR + (V600 - VFLOOR) * (f - 300) / 300)


def pscale(f, mode):
    """switching power at clock f relative to 600 MHz / 0.517 V; mode 'floor' (V lowered) or 'fixed' (only the
    clock changed: SET_FREQUENCY programs the PLL, no voltage change, review-governor.md)"""
    f = np.asarray(f, dtype=float)
    v = vfloor(f) if mode == 'floor' else V600
    return (f / 600.0) * (v / V600) ** 2


print('switching power per shire on die at 600 MHz, fp32 randn TensorFMA, W:', pct(P600))
for m in ('floor', 'fixed'):
    print(f'  x f*V^2, voltage {m:5s}: ' + ', '.join(f'{f} MHz {float(pscale(f, m)):.4f}' for f in CLOCKS))
print('other kernels per shire at 600 MHz (x of fp32 randn): int8 randn 0.37, fp32 ones 0.39, zeros 0.07 '
      '(+9.98, +10.7, +1.9 W of +27.1: camera plan table 2e; 12-heat-management.md)')

# ---- camera (the lab's Thermal Master P3; the owner's plan, section 2a-2c) ----------------------------------------
NETD = U(0.024, 0.035)                # K: < 35 mK at 25 C (vendor); 23-24 mK on an 80 C target (plan 2a, computed)
FPS = 25.0                            # free-running 25 Hz (plan 2a)
DUTY = 88.0 / 90.0                    # ASSUMED: 2 s masked around each ~90 s shutter (plan section 1)
IFOV = U(2.73e-3, 2.79e-3)            # rad (plan 2a: f = 4.3 mm, 12 um pixels)
DIST = 0.060                          # m: the whole 45 mm package in frame, 0.16-0.17 mm/px (plan 2b)
PX = DIST * IFOV
ROI = 0.5 * PITCH                     # the central half of a shire's tile, each way
NPX = (ROI / PX) ** 2
F_DRIFT = 4.0                         # the plan's x4 drift allowance on an ROI mean until E-T8 measures it (plan 2c)
print(f'camera at {DIST*1e3:.0f} mm: {pct(PX, scale=1e3)} mm/px; a shire is {pct(PITCH/PX)} px across; ROI '
      f'{ROI*1e3:.2f} mm = {pct(NPX)} px; NETD {pct(NETD, scale=1e3)} mK; 25 Hz; drift allowance x{F_DRIFT:.0f}')
print(f'check against the plan 2c: sigma per quadrature per pixel, 35 mK, 1,800 s = '
      f'{35*math.sqrt(2/45000):.3f} mK (plan: 0.233)')
EPS = {  # emissivity of each viewed face
    'die, black paint or tape': U(0.90, 0.95),   # masking tape 0.92 (KIT, page ref [8]); flat black paint ~0.95 ASSUMED
    'die, bare silicon': LU(0.1, 0.7),           # ASSUMED: lightly doped Si is partly transparent at 8-14 um (page refs
    #                                              [27]-[29]); a die with a backside metal for a solder TIM1 would be
    #                                              as bad as the lid (not known which TIM1 this package has)
    'lid, polyimide or masking tape': U(0.74, 0.92),  # 1 mil polyimide 0.74-0.90 (plan section 4, shopping list), masking tape 0.92 [8]
    'lid, bare plating': LU(0.01, 0.1),          # a metal package ~0.01 (KIT, [8]); 0.05-0.1 the owner's brief
}
# ---- on-die sensors -------------------------------------------------------------------------------------------------
# 12-bit codes, 0.061 C a count in hardware; the firmware truncates each to whole degrees and sends the host only the
# 34-sensor mean, an anonymous peak-hold high/low and the I/O shire's own sensor (the spatial brief; 14-card-
# behaviour.md:106,268).  A per-shire readout needs a rebuilt, signed BL2 (untested whether the cards accept one).
RATE = U(1 / 0.224, 1 / 0.133)        # readings a second: one per service-processor pass, 133-224 ms (E41)
SIG_RAW = LU(0.018, 0.1)              # C per raw reading: 0.061/sqrt(12) (dithered quantisation) .. 0.1, ASSUMED
SIG_DEG = 1 / math.sqrt(12)           # whole degrees, dithered: 0.289 C (plan section 1, free win (a))
print(f'sensors: {pct(RATE)} readings/s; raw-code noise {pct(SIG_RAW)} C (ASSUMED); whole degrees {SIG_DEG:.3f} C')

# ======================================================================================================================
hdr('B. The layered conduction model')
SUB, NCELL = 12, 24                   # samples per pitch; lateral period in pitches
NG = SUB * NCELL
DX = PITCH / SUB
ky = 2 * np.pi * np.fft.fftfreq(NG, d=DX)
kx = 2 * np.pi * np.fft.rfftfreq(NG, d=DX)
Q2 = ky[:, None] ** 2 + kx[None, :] ** 2
print(f'lateral period {NCELL} pitches = {NCELL*PITCH*1e3:.1f} mm, {NG} x {NG} samples of {DX*1e3:.3f} mm')


def cell0(r, c):
    return NG // 2 - 3 * SUB + r * SUB, NG // 2 - 3 * SUB + c * SUB


def roi_mean(field, r, c, kind):
    y0, x0 = cell0(r, c)
    if kind == 'roi':      # central half of the tile (camera ROI)
        a, b = SUB // 4, SUB - SUB // 4
    else:                  # 'pt': the tile's centre (a sensor)
        a, b = SUB // 2 - 1, SUB // 2 + 1
    return field[..., y0 + a:y0 + b, x0 + a:x0 + b].mean(axis=(-1, -2))


def source(cells):
    S = np.zeros((NG, NG))
    for (r, c) in cells:
        y0, x0 = cell0(r, c)
        S[y0:y0 + SUB, x0:x0 + SUB] = 1.0 / PITCH ** 2      # W/m2 for 1 W per shire
    return S


def nbrs(r, c):
    return [(r + dr, c + dc) for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)) if 0 <= r + dr < 6 and 0 <= c + dc < 6]


# ---- patterns: state A, state B (B = idle for on/off), and the (on cell, reference cells) pairs a contrast averages
CHK_A = sorted(p for p in COMPUTE if (p[0] + p[1]) % 2 == 0)
CHK_B = sorted(p for p in COMPUTE if (p[0] + p[1]) % 2 == 1)
NE = [(1, 4), (1, 5), (2, 4), (2, 5)]           # B4NE: S20, S28, S29, S5 (heat-placement mask 0x30100020)
SW = [(4, 0), (4, 1), (5, 0), (5, 1)]           # B4SW: S2, S10, S11, S19 (mask 0x00080c04)
RING = [(0, 4), (0, 5), (1, 3), (2, 3), (3, 4), (3, 5)]
PATTERNS = {
    'checkerboard': dict(A=CHK_A, B=CHK_B, how='commutated with its complement',
                         pairs=[(p, [q for q in nbrs(*p) if q in COMPUTE]) for p in CHK_A
                                if 1 <= p[0] <= 4 and 1 <= p[1] <= 4]),
    'one shire': dict(A=[(2, 3)], B=[], how='S21 on/off',
                      pairs=[((2, 3), nbrs(2, 3))]),
    '2x2 block moving': dict(A=NE, B=SW, how='NE block <-> SW block, commutated (the MAP pair)',
                             pairs=[(p, RING) for p in NE]),
    'half die': dict(A=sorted(p for p in COMPUTE if p[1] <= 2), B=sorted(p for p in COMPUTE if p[1] >= 3),
                     how='west half <-> east half, commutated',
                     pairs=[((r, 1), [(r, 4)]) for r in range(1, 6) if (r, 1) in COMPUTE and (r, 4) in COMPUTE]),
}
for k, p in PATTERNS.items():
    assert all(q in COMPUTE for q in p['A'] + p['B'])
    print(f'{k:17s}: {len(p["A"])} shires vs {len(p["B"])}; {p["how"]}; contrast = on ROI minus its reference ROIs, '
          f'averaged over {len(p["pairs"])} pair(s)')
for k, p in PATTERNS.items():
    p['FA'] = np.fft.rfft2(source(p['A']))
    p['FD'] = np.fft.rfft2(source(p['A']) - source(p['B']))


def contrast(field, pairs, kind):
    vals = []
    for on, refs in pairs:
        vals.append(roi_mean(field, *on, kind) - np.mean([roi_mean(field, *q, kind) for q in refs], axis=0))
    return np.mean(vals, axis=0)


def layers_for(i):
    die = (t_die[i], k_si[i], k_si[i], RHOC_SI)
    tim1 = (t_tim1[i], t_tim1[i] / Rpp_tim1[i], t_tim1[i] / Rpp_tim1[i], RHOC_TIM)
    lid = (t_lid[i], K_CU, K_CU, RHOC_CU)
    tim2 = (T_TIM2, T_TIM2 / Rpp_tim2[i], T_TIM2 / Rpp_tim2[i], RHOC_TIM)
    base = (t_base[i], K_AL, K_AL, RHOC_AL)
    bump = (t_bump[i], KXY_BUMP, kz_bump[i], RHOC_TIM)
    sub = (t_sub[i], kxy_sub[i], kz_sub[i], rhoc_sub[i])
    down = ([bump, sub], 1.0 / Rpp_rest[i])
    views = {
        'a_still': ([die], h_still[i]),
        'a_fan': ([die], h_fan[i]),
        'a_win': ([die], h_win[i]),
        'b_still': ([die, tim1, lid], h_still[i]),
        'b_fan': ([die, tim1, lid], h_fan[i]),
        'c_hs': ([die, tim1, lid, tim2, base], h_hs[i]),
    }
    return views, down


def stack(layers, h_end, q2, s):
    """admittance at the source-side face of a stack (layers listed outward from the source), and the product of the
    temperature ratios through all of it (far face / source face)"""
    Y = np.full(q2.shape, complex(h_end))
    ratio = np.ones(q2.shape, dtype=complex)
    for (d, kxy, kz, rhoc) in reversed(layers):
        g2 = (kxy * q2 + rhoc * s) / kz
        g = np.sqrt(g2.astype(complex))
        gd = g * d
        small = np.abs(gd) < 1e-9
        th = np.tanh(gd)
        gs = np.where(small, 1.0, g)
        A = np.where(small, kz * g2 * d, kz * g * th)
        B = np.where(small, d / kz, th / (kz * gs))
        e = np.exp(-gd)
        sech = 2 * e / (1 + e * e)
        ratio = ratio * sech / (1 + Y * B)
        Y = (A + Y) / (1 + Y * B)
    return Y, ratio


def transfer(view, down, s):
    """(G at the source plane, G at the top face of the up stack), K per (W/m2) of each Fourier mode"""
    Yu, ru = stack(view[0], view[1], Q2, s)
    Yd, _ = stack(down[0], down[1], Q2, s)
    Gj = 1.0 / (Yu + Yd)
    return Gj, Gj * ru


def field(F, G):
    """real-space field of the power map F (rfft2) through the transfer G; complex when G is"""
    re = np.fft.irfft2(F * G.real, s=(NG, NG))
    if np.iscomplexobj(G) and np.abs(G.imag).max() > 0:
        return re + 1j * np.fft.irfft2(F * G.imag, s=(NG, NG))
    return re


# self-checks on draw 0: s -> 0 limit of the periodic response, and a 1-D stack against its series resistance
_v, _d = layers_for(0)
Gj0, Gt0 = transfer(_v['b_still'], _d, 0.0)
Gj1, Gt1 = transfer(_v['b_still'], _d, 2j * np.pi * 1e-6)
assert np.allclose(Gj0, Gj1, rtol=1e-3, atol=1e-12)
Ru = t_die[0] / k_si[0] + Rpp_tim1[0] + t_lid[0] / K_CU + 1 / h_still[0]
Rd = t_bump[0] / kz_bump[0] + t_sub[0] / kz_sub[0] + Rpp_rest[0]
assert abs(Gj0[0, 0].real - 1 / (1 / Ru + 1 / Rd)) < 1e-9 * Ru
print('self-checks: q = 0 mode equals the series-parallel resistances; f -> 0 equals steady state: ok')

VIEWS = ['a_still', 'a_fan', 'a_win', 'b_still', 'b_fan', 'c_hs']
VIEW_LABEL = {
    'a_still': '(a) delidded die, air above (still), cooled through the board',
    'a_fan': '(a) delidded die, fan air above, cooled through the board',
    'a_win': '(a) delidded die under an IR-window liquid cooler (reference: mid-wave or Ge/ZnSe + a LWIR coolant)',
    'b_still': '(b) lid top, heatsink off, still air',
    'b_fan': '(b) lid top, heatsink off, fan',
    'c_hs': '(c) transistor plane = the 34 sensors, heatsink on',
}
FMODS = [0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
PN = list(PATTERNS)

# ---- the Monte Carlo over the model --------------------------------------------------------------------------------
# g[view][obs][pattern] = contrast per W per shire (K/W); obs 'top' = the view's surface (camera ROI), 'jn' = the
# transistor plane at the sensors' points; 'state' = one state's own image; ac[...][f] = complex amplitude of the
# difference image at each f_mod (the fundamental's factor 2/pi applied in section G).
g_dc = {v: {o: {p: np.zeros(N) for p in PN} for o in ('top', 'jn')} for v in VIEWS}
g_ac = {v: {o: {p: np.zeros((N, len(FMODS))) for p in PN} for o in ('top', 'jn')} for v in VIEWS}
io_dc = np.zeros((N, 2))
one_profile = {v: np.zeros((N, 4)) for v in ('a_still', 'b_still', 'c_hs')}
PROF_R = [2e-3, 10e-3, 20e-3, 40e-3]
for i in range(N):
    views, down = layers_for(i)
    for v in VIEWS:
        Gj, Gt = transfer(views[v], down, 0.0)
        for p in PN:
            P = PATTERNS[p]
            for o, G in (('top', Gt), ('jn', Gj)):
                kind = 'pt' if o == 'jn' else 'roi'
                D = field(P['FD'], G)
                g_dc[v][o][p][i] = contrast(D, P['pairs'], kind)
                if v == 'c_hs' and o == 'jn' and p == '2x2 block moving':
                    io_dc[i] = [roi_mean(D, 0, 4, 'pt'), roi_mean(D, 0, 5, 'pt')]
                if p == 'one shire' and o == 'jn' and v in one_profile:
                    y0, x0 = cell0(2, 3)
                    yc, xc = y0 + SUB // 2, x0 + SUB // 2
                    F1 = field(P['FA'], G)
                    one_profile[v][i] = [F1[yc, min(xc + int(round(r / DX)), NG - 1)] for r in PROF_R]
        for j, fm in enumerate(FMODS):
            Gj, Gt = transfer(views[v], down, 2j * np.pi * fm)
            for p in PN:
                P = PATTERNS[p]
                for o, G in (('top', Gt), ('jn', Gj)):
                    if o == 'top' and v == 'c_hs':
                        continue
                    kind = 'pt' if o == 'jn' else 'roi'
                    g_ac[v][o][p][i, j] = abs(contrast(field(P['FD'], G), P['pairs'], kind))

print('single 1 W shire, steady, excess at the transistor plane at r = 2 / 10 / 20 mm over that at 40 mm (C):')
for v in one_profile:
    pr = one_profile[v]
    print(f'  {VIEW_LABEL[v][:60]:60s} ' + ' | '.join(f'{r*1e3:.0f} mm {pct(pr[:, k] - pr[:, 3])}'
                                                        for k, r in enumerate(PROF_R[:3])))
from scipy.special import k0 as _k0
_G = K_CU * t_lid + k_si * t_die
_lam = np.sqrt(_G * Rdown)
print(f'  nohs_calc.py G\'s thin-sheet K0 model on the same draws (heatsink off, die + lid over the down path, decay '
      f'{pct(_lam, scale=1e3)} mm), also over 40 mm: ' + ' | '.join(
          f'{r*1e3:.0f} mm {pct((_k0(r/_lam) - _k0(0.04/_lam))/(2*np.pi*_G))}' for r in PROF_R[:3]))

# ======================================================================================================================
hdr('C. Contrast per watt per shire, steady (mK per W per shire; difference image unless "state")')
print('Contrast = mean over the pattern\'s pairs of (ROI of an active shire - mean ROI of its reference shires).')
print('For a commutated pattern the difference image (state A - state B) has twice one state\'s contrast.')
print(f'{"view":62s} {"observed":8s} ' + ' '.join(f'{p:>24s}' for p in PN))
for v in VIEWS:
    for o in (('top', 'jn') if v != 'c_hs' else ('jn',)):
        lab = 'surface' if o == 'top' else 'sensors'
        print(f'{VIEW_LABEL[v][:62]:62s} {lab:8s} ' + ' '.join(f'{pct(g_dc[v][o][p], scale=1e3):>24s}' for p in PN))
# One live frame shows the pattern as a ripple on the chip-wide heat bump (15-21 K per W per shire at the transistors
# of a delidded die, curved over the grid).  For a commutated pattern that ripple is half the difference image's
# contrast (each state holds half of it); for the one shire switched on and off it is the whole of it.
LIVE_FACTOR = {p: (1.0 if PATTERNS[p]['B'] == [] else 0.5) for p in PN}
print('a single live frame shows ' + ', '.join(f'{p} x{LIVE_FACTOR[p]:g}' for p in PN) + ' of these (the ripple on the '
      'chip-wide bump, which the difference image removes)')

hdr('D. Lock-in: the difference image\'s amplitude at f_mod over its steady value (medians; 5th-95th for 1 Hz)')
print(f'{"view":62s} {"pattern":17s} ' + ' '.join(f'{f:>7g} Hz' for f in FMODS) + '   1 Hz 5-95')
for v in VIEWS:
    o = 'jn' if v == 'c_hs' else 'top'
    for p in PN:
        r = g_ac[v][o][p] / g_dc[v][o][p][:, None]
        print(f'{VIEW_LABEL[v][:62]:62s} {p:17s} ' + ' '.join(f'{np.median(r[:, j]):10.3f}' for j in range(len(FMODS)))
              + f'   {pct(r[:, FMODS.index(1.0)])}')
alpha_si = k_si / RHOC_SI
print('thermal diffusion length sqrt(alpha/(pi f)), mm: ' + '; '.join(
    f'{f:g} Hz Si {pct(np.sqrt(alpha_si/(np.pi*f)), scale=1e3)} Cu {math.sqrt(K_CU/RHOC_CU/(math.pi*f))*1e3:.2g}'
    for f in (0.1, 1.0, 5.0)))

# ======================================================================================================================
hdr('E. Transient check against the heat-placement MAP measurement (heatsink on)')
# MAP = iota_io(B4NE) - iota_io(B4SW): the rise of the I/O shire's own whole-degree sensor over a 7 s launch on four
# shires beside it, minus the same launch in the far corner.  aifoundry3 development: 0.667 C [0.366, 0.967] (6 blocks,
# 99 % CI; heat.json dev.items.MAP); aifoundry1 card 1 validation: 0.967 C [0.519, 1.414] (5 blocks; val.json
# validation.items.MAP.value).  Blocks drew 2.87-3.11 W (a3) and 2.45-2.77 W (a1c1) of board switching.
MAP_MEAS = {'aifoundry3 (dev)': (0.667, 0.366, 0.967), 'aifoundry1 card 1 (val)': (0.967, 0.519, 1.414)}
for _f, _key in (('docs/reports/data/2026-09-28-heat-placement/heat.json', 'dev'),
                 ('docs/reports/data/2026-09-28-heat-placement/val.json', 'val')):
    if os.path.exists(_f):
        _d = json.load(open(_f))
        _m = _d['dev']['items']['MAP']['ci99'] if _key == 'dev' else _d['validation']['items']['MAP']['value']
        _ref = MAP_MEAS['aifoundry3 (dev)' if _key == 'dev' else 'aifoundry1 card 1 (val)']
        assert abs(_m['mean'] - _ref[0]) < 1e-3 and abs(_m['lo'] - _ref[1]) < 1e-3, (_f, _m)
        print('MAP value matches', _f)


def stehfest_v(n):
    v = []
    for k in range(1, n + 1):
        acc = 0.0
        for j in range((k + 1) // 2, min(k, n // 2) + 1):
            acc += (j ** (n // 2) * math.factorial(2 * j)) / (
                math.factorial(n // 2 - j) * math.factorial(j) * math.factorial(j - 1) * math.factorial(k - j)
                * math.factorial(2 * j - k))
        v.append((-1) ** (k + n // 2) * acc)
    return v


SV = stehfest_v(14)
TS = [4.5, 5.5, 6.5]                   # s after the launch: the last three ~1 s windows of a 7 s launch
NM = min(args.map_draws, N)
P_B4 = U(0.51, 0.68, NM)               # W per shire on die: 2.45-3.11 W board / 4 x (0.83-0.88)
map_t = np.zeros((NM, 2))
map_ss = np.zeros((NM, 2))
map_pos = np.zeros((NM, 2, 3))         # steady, sensor at the I/O tile's centre, 3/4 of the way to the block, its edge
PB = PATTERNS['2x2 block moving']
for i in range(NM):
    views, down = layers_for(i)
    acc = np.zeros(2)
    for t in TS:
        tot = np.zeros(2)
        for k, vk in enumerate(SV, start=1):
            s = k * math.log(2) / t
            Gj, _ = transfer(views['c_hs'], down, s)
            D = field(PB['FD'], Gj.real)
            tot += vk * np.array([roi_mean(D, 0, 4, 'pt'), roi_mean(D, 0, 5, 'pt')]) / s
        acc += tot * math.log(2) / t
    map_t[i] = acc / len(TS) * P_B4[i]
    map_ss[i] = io_dc[i] * P_B4[i]
    Gj, _ = transfer(views['c_hs'], down, 0.0)
    D = field(PB['FD'], Gj)
    for j, c in enumerate((4, 5)):
        y0, x0 = cell0(0, c)
        xc = x0 + SUB // 2
        map_pos[i, j] = [D[y0 + k, xc - 1:xc + 1].mean() * P_B4[i] for k in (SUB // 2, 3 * SUB // 4, SUB - 1)]
# Stehfest check: a long time must give the steady value
views, down = layers_for(0)
tot = 0.0
for k, vk in enumerate(SV, start=1):
    s = k * math.log(2) / 1e5
    Gj, _ = transfer(views['c_hs'], down, s)
    tot += vk * roi_mean(field(PB['FD'], Gj.real), 0, 4, 'pt') / s
assert abs(tot * math.log(2) / 1e5 - io_dc[0, 0]) < 0.02 * abs(io_dc[0, 0]) + 1e-6, (tot * math.log(2) / 1e5, io_dc[0, 0])
print('Stehfest inversion (N = 14) reproduces the steady state at t = 1e5 s: ok')
for j, where in enumerate(('I/O at (0,4)', 'I/O at (0,5)')):
    print(f'model, {where}: 4 shires at {pct(P_B4)} W on die, NE minus SW at 4.5-6.5 s after the step: '
          f'{pct(map_t[:, j])} C (steady: {pct(map_ss[:, j])} C)')
for k, (m, lo, hi) in MAP_MEAS.items():
    print(f'measured, {k}: {m:.2f} C [{lo:.2f}, {hi:.2f}] (99 % CI, whole-degree readings)')
print('where the I/O sensor sits in its tile is not known; steady model with it at the tile\'s centre / 3/4 of the way '
      'toward the block / at the tile\'s edge next to the block:')
for j, where in enumerate(('(0,4)', '(0,5)')):
    print(f'  I/O at {where}: ' + ' / '.join(pct(map_pos[:, j, k], p=(50,)) for k in range(3)) + ' C (medians); '
          f'5-95 % at the edge {pct(map_pos[:, j, 2])}')
_lo = Rpp_tim1[:NM] <= np.percentile(Rpp_tim1[:NM], 33)
_hi = Rpp_tim1[:NM] >= np.percentile(Rpp_tim1[:NM], 67)
print(f'  and with TIM1 in the lowest / highest third of its range ({pct(Rpp_tim1[:NM][_lo], p=(50,), scale=1e4)} / '
      f'{pct(Rpp_tim1[:NM][_hi], p=(50,), scale=1e4)} K cm2/W), sensor at the centre of (0,4): '
      f'{pct(map_ss[_lo, 0], p=(50,))} / {pct(map_ss[_hi, 0], p=(50,))} C (medians)')
print('  The measurement sits at or above the model: the model\'s contrasts with the heatsink on are, if anything, low.')
OUT['map_check'] = {'model_io04_C': list(np.percentile(map_t[:, 0], [5, 50, 95])),
                    'model_io_edge_C': [list(np.percentile(map_pos[:, j, 2], [5, 50, 95])) for j in range(2)],
                    'model_io05_C': list(np.percentile(map_t[:, 1], [5, 50, 95])),
                    'measured': MAP_MEAS}

# ======================================================================================================================
hdr('F. Noise: what a shire\'s contrast must beat')
K_SNR = 3.0
# camera, per ROI: difference image with 1 s per state (25 frames each); lock-in sigma per quadrature NETD*sqrt(2/M)
sig_diff_roi = NETD * math.sqrt(2 / 25.0) / np.sqrt(NPX) * F_DRIFT
print(f'camera, one frame per pixel (live view): NETD {pct(NETD, scale=1e3)} mK')
print(f'camera, difference image 1 s per state, shire ROI: {pct(sig_diff_roi, scale=1e3)} mK')
for T in (60, 600, 3600):
    M = FPS * DUTY * T
    print(f'camera, lock-in {T:5d} s, per quadrature, shire ROI: {pct(NETD*np.sqrt(2/M)/np.sqrt(NPX)*F_DRIFT, scale=1e3)} mK')
for T in (60, 600, 3600):
    print(f'sensor raw codes, lock-in {T:5d} s, per quadrature: {pct(SIG_RAW*np.sqrt(2/(RATE*T)), scale=1e3)} mK;'
          f' whole degrees: {pct(SIG_DEG*np.sqrt(2/(RATE*T)), scale=1e3)} mK')
print(f'criterion: a shire is seen when its contrast is {K_SNR:.0f} times the noise of an ROI pair (sqrt 2 x one ROI); '
      f'SNR 5 instead takes {(5/3)**2:.1f} times as long')
# the thresholds themselves (what a camera-read contrast must exceed), median over the draws: for the 1 s-per-state
# difference image against the settled contrast x emissivity; for lock-in against the modulated amplitude of the
# fundamental, (2/pi) x the difference image's amplitude at f_mod (section D's ratio), x emissivity
THR = {'diff 1 s/state': K_SNR * math.sqrt(2) * sig_diff_roi}
for T in (60, 600, 3600):
    THR[f'lock-in {T} s'] = K_SNR * math.sqrt(2) * NETD * np.sqrt(2 / (FPS * DUTY * T)) / np.sqrt(NPX) * F_DRIFT
print('camera thresholds, K x sqrt 2 x the ROI noise above, mK (median [5-95]): ' + '; '.join(
    f'{k} {np.median(v)*1e3:.2g} [{np.percentile(v, 5)*1e3:.2g}-{np.percentile(v, 95)*1e3:.2g}]' for k, v in THR.items())
      + '; the 1 s threshold applies to the settled contrast, the lock-in ones to the fundamental\'s amplitude, (2/pi) '
      'x the difference image\'s amplitude at f_mod (section D), which is a fraction of the settled contrast')
OUT['camera_threshold_mK'] = {k: list(np.percentile(v * 1e3, [5, 50, 95])) for k, v in THR.items()}

# ======================================================================================================================
hdr('G. Least power per shire, least clock, and the time to see each pattern')
FGRID = np.logspace(-2, math.log10(600.0), 6000)   # MHz; the least clock is the envelope, not a PLL setting


def fmin_for(pmin, p600, mode):
    """least clock (MHz) at which p600 * pscale(f) >= pmin; inf if not even at 600 MHz"""
    ps = pscale(FGRID, mode)
    out = np.full(np.shape(pmin), np.inf)
    for i in range(len(pmin)):
        ok = np.nonzero(p600[i] * ps >= pmin[i])[0]
        if len(ok):
            out[i] = FGRID[ok[0]]
    return out


def lockin_time(g_amp, eps, netd, npx, p):
    """seconds of recording for SNR K at each f_mod (g_amp: (N, nf) K/W), best over f_mod, at least 20 periods"""
    a = eps[:, None] * (2 / np.pi) * g_amp * p[:, None]
    M = 2 * (K_SNR * math.sqrt(2) * netd[:, None] * F_DRIFT / (np.sqrt(npx)[:, None] * a)) ** 2
    T = np.maximum(np.maximum(M / (FPS * DUTY), 20.0 / np.array(FMODS)[None, :]), 10.0)   # >= 20 periods, >= 10 s
    j = np.argmin(T, axis=1)
    return T[np.arange(len(T)), j], np.array(FMODS)[j]


def pmin_lockin(g_amp, eps, netd, npx, T):
    """least power per shire for SNR K within T seconds (f_mod chosen with >= 20 periods in T)"""
    M = FPS * DUTY * T
    sig = netd * math.sqrt(2 / M) / np.sqrt(npx) * F_DRIFT
    okf = np.array([T >= 20.0 / f for f in FMODS])
    best = np.where(okf[None, :], g_amp, 0).max(axis=1)
    return K_SNR * math.sqrt(2) * sig / (eps * (2 / np.pi) * best)


# Through an IR-window cooler the camera reads the coated die through the window and the coolant film: the apparent
# contrast is emissivity x their transmission (added 30 Sep, review).  ASSUMED: an anti-reflection-coated germanium or
# zinc-selenide window 0.85-0.95 (uncoated germanium loses 53 % to reflection, page ref [17]); a thin mineral-oil film
# 0.6-0.95 (its 13.9 um band lies inside the camera's 8-14 um, page refs [32]-[33]; the film's transmission is not
# measured).  Drawn here, after every other draw, so that nothing above changes.
TAU_WIN = U(0.85, 0.95) * U(0.6, 0.95)
EPS['die, black, through an IR window and an oil film'] = EPS['die, black paint or tape'] * TAU_WIN
print(f'IR-window cooler: window x oil-film transmission {pct(TAU_WIN)} (ASSUMED), so the coated die reads at '
      f'{pct(EPS["die, black, through an IR window and an oil film"])} of its contrast')
SURFACES = [  # (label, view, emissivity key)
    ('(a) delidded die, black-coated, still air', 'a_still', 'die, black paint or tape'),
    ('(a) delidded die, black-coated, fan', 'a_fan', 'die, black paint or tape'),
    ('(a) delidded die, bare silicon, fan', 'a_fan', 'die, bare silicon'),
    ('(a) delidded die, black-coated, IR-window cooler', 'a_win', 'die, black, through an IR window and an oil film'),
    ('(b) lid top, taped, still air', 'b_still', 'lid, polyimide or masking tape'),
    ('(b) lid top, taped, fan', 'b_fan', 'lid, polyimide or masking tape'),
    ('(b) lid top, bare plating, fan', 'b_fan', 'lid, bare plating'),
]
TLIST = [60, 600, 3600]
res = {}
print('Least switching power per shire (mW), 5 / 50 / 95 %; and the least clock (MHz, median) for fp32 randn '
      'TensorFMA with the voltage lowered to its floor | clock only')
for lab, v, ek in SURFACES:
    eps = EPS[ek]
    print(f'-- {lab}')
    for p in PN:
        rows = {}
        rows['live frame'] = K_SNR * NETD / (eps * LIVE_FACTOR[p] * np.abs(g_dc[v]['top'][p]))
        rows['diff 1 s/state'] = K_SNR * math.sqrt(2) * sig_diff_roi / (eps * np.abs(g_dc[v]['top'][p]))
        for T in TLIST:
            rows[f'lock-in {T} s'] = pmin_lockin(g_ac[v]['top'][p], eps, NETD, NPX, T)
        line = []
        res.setdefault(lab, {})[p] = {}
        for k, pm in rows.items():
            f1 = fmin_for(pm, P600, 'floor')
            f2 = fmin_for(pm, P600, 'fixed')
            med1, med2 = np.median(f1), np.median(f2)
            res[lab][p][k] = {'pmin_mW': list(np.percentile(pm * 1e3, [5, 50, 95])),
                              'fmin_MHz_floor_median': float(med1), 'fmin_MHz_fixed_median': float(med2),
                              'fmin_MHz_floor_p5_p95': list(np.percentile(np.where(np.isfinite(f1), f1, 1e9), [5, 95])),
                              'frac_invisible_at_600': float(np.mean(~np.isfinite(f1)))}
            fm = (lambda x: '>600' if not np.isfinite(x) else ('<0.01' if x <= FGRID[0] else f'{x:.3g}'))
            line.append(f'{k}: {pct(pm, scale=1e3)} mW -> {fm(med1)} | {fm(med2)} MHz')
        print(f'   {p}:')
        for ln in line:
            print(f'      {ln}')

print()
print('Lock-in time to see each shire (SNR 3), fp32 randn TensorFMA, median [5-95 %] seconds, best f_mod, at least '
      '20 periods and 10 s ("10" = 10 s or less); voltage at its floor (clock only in brackets for 100 and 10 MHz)')
times = {}
for lab, v, ek in SURFACES:
    eps = EPS[ek]
    print(f'-- {lab}')
    for p in PN:
        cells = []
        for f in CLOCKS:
            T, fbest = lockin_time(g_ac[v]['top'][p], eps, NETD, NPX, P600 * float(pscale(f, 'floor')))
            times.setdefault(lab, {}).setdefault(p, {})[f] = list(np.percentile(T, [5, 50, 95]))
            cell = f'{f}: {np.median(T):.3g} [{np.percentile(T, 5):.2g}-{np.percentile(T, 95):.2g}]'
            if f in (100, 10):
                T2, _ = lockin_time(g_ac[v]['top'][p], eps, NETD, NPX, P600 * float(pscale(f, 'fixed')))
                cell += f' ({np.median(T2):.3g})'
            cells.append(cell)
        print(f'   {p:17s} ' + ' | '.join(cells))

print()
print('Contrast in a 1 s-per-state difference image, fp32 randn, median mK x emissivity (what the camera reads), '
      'voltage at its floor:')
for lab, v, ek in SURFACES:
    eps = EPS[ek]
    print(f'   {lab:52s} ' + ' | '.join(
        f'{p}: ' + ' '.join(f'{np.median(eps*np.abs(g_dc[v]["top"][p])*P600*float(pscale(f, "floor")))*1e3:.3g}'
                            for f in (600, 100, 10)) for p in PN) + '   (600 / 100 / 10 MHz)')

# ---- (c) the sensors ------------------------------------------------------------------------------------------------
print()
print('(c) The on-die sensors.  Contrast at the transistor plane per W per shire (mK/W); least power per shire (mW) '
      'and least clock (MHz, median, voltage at its floor) with per-shire raw codes (a rebuilt BL2): settled states '
      '1 s each | lock-in 1 min | 10 min | 1 h')
sens = {}
for v in ('c_hs', 'b_fan', 'a_fan'):
    for p in PN:
        g = np.abs(g_dc[v]['jn'][p])
        n1 = RATE * 1.0
        pms = [K_SNR * math.sqrt(2) * (SIG_RAW * np.sqrt(2 / n1)) / g]
        for T in (60.0, 600.0, 3600.0):
            M = RATE * T
            okf = np.array([T >= 20.0 / f for f in FMODS])
            best = np.where(okf[None, :], g_ac[v]['jn'][p], 0).max(axis=1)
            pms.append(K_SNR * math.sqrt(2) * (SIG_RAW * np.sqrt(2 / M)) / ((2 / np.pi) * best))
        fms = [fmin_for(pm, P600, 'floor') for pm in pms]
        sens[(v, p)] = (g, pms, fms)
        print(f'   {VIEW_LABEL[v][:44]:44s} {p:17s} {pct(g, scale=1e3):>20s} mK/W | ' + ' | '.join(
            f'{np.median(pm)*1e3:.3g} mW {np.median(fm):.3g} MHz' for pm, fm in zip(pms, fms)))
# stock firmware: the I/O shire's whole-degree sensor, the moving block beside it (commutated: the mean stays put)
stock = {}
for j, where in enumerate(('(0,4)', '(0,5)')):
    g_io = np.abs(io_dc[:, j])
    for T in (60, 600, 3600):
        M = RATE * T
        pm = K_SNR * SIG_DEG * np.sqrt(2 / M) / ((2 / np.pi) * g_io)   # steady amplitude: f_mod <= 0.5 Hz, ASSUMED
        f_io = fmin_for(pm, P600, 'floor')
        stock[(where, T)] = (pm, f_io)
        print(f'   stock firmware, I/O sensor at {where}, block beside it vs far corner, lock-in {T:4d} s: '
              f'{pct(pm, scale=1e3)} mW per shire -> {np.median(f_io):.3g} MHz (floor)')
print('   (whole-degree readings average below one degree only while the die wanders across degree steps; a steady die '
      'needs a deliberate slow dither of the chip\'s power)')
# ---- the quantiser, simulated (added 30 Sep, review) ----------------------------------------------------------------
# The lines above score whole-degree readings as white noise of 1/sqrt(12) C, which holds only while the die's
# temperature wanders across degree steps.  Simulated here for the I/O sensor and the block beside it (median draw):
# reading = floor(T), T = a mean position within a degree + the block's square-wave swing + raw sensor noise before
# truncation (ASSUMED 0.02 or 0.09 C, the ends of SIG_RAW), on a steady die or with a slow triangle dither of the die's
# temperature over 2 C peak to peak (two whole steps, so every position is visited alike; ASSUMED protocol: a few
# shires' load ramped slowly), its period 18 / f_mod (73 s), so that f_mod falls midway between the 4th and 5th
# harmonics of the rate at which the die crosses degree steps (the rounding error's sawtooth); the run then lasts at
# least two periods; f_mod = rate / 24 (12 readings a state, about 0.25 Hz); a running mean over one modulation period
# removes the slow part, and the fundamental's
# amplitude is demodulated.  The steady-die run is as long as the white-noise model needs for SNR 3 (at least 10 s).
# Over 40 noise draws per mean position: gain = the recovered amplitude's median over the true one; effective SNR =
# its mean over its spread; "seen" = effective SNR >= 3.  The raw codes' case: a 9 mK swing on 0.061 C steps.
QRNG = np.random.default_rng(SEED + 1)        # a separate stream: nothing above changes
_rate, _gio, _p6 = float(np.median(RATE)), float(np.median(np.abs(io_dc[:, 0]))), float(np.median(P600))
NREP, NPOS, HALF = 40, 50, 12
DPER = 18.0 / (_rate / (2 * HALF))       # s
QOUT = {}
QCASES = [('stock, 600 MHz', _gio * _p6, 1.0, None),
          ('stock, 100 MHz, floor', _gio * _p6 * float(pscale(100, 'floor')), 1.0, None),
          ('raw codes, a 9 mK swing', 0.009, 0.061, 600.0)]
for qlab, A, qstep, Trun in QCASES:
    Twn = Trun or max(10.0, 2 * (K_SNR * SIG_DEG / ((2 / np.pi) * A)) ** 2 / _rate)
    dith = (('steady die', 0.0, Twn), ('2 C dither', 2.0, max(Twn, 2 * DPER))) if qstep == 1.0 else (('steady die', 0.0, Twn),)
    for dlab, D, Tq in dith:
        n = int(round(_rate * Tq / (2 * HALF))) * 2 * HALF
        k = np.arange(n)
        sq = np.where((k // HALF) % 2 == 0, 1.0, -1.0)
        ref = np.sin(2 * np.pi * (k + 0.5) / (2 * HALF))
        t = k / _rate

        def demod(x):
            c = np.cumsum(np.concatenate([np.zeros(x.shape[:-1] + (1,)), x], axis=-1), axis=-1)
            ma = (c[..., 2 * HALF:] - c[..., :-2 * HALF]) / (2 * HALF)       # mean over [i-12, i+12)
            xs = x[..., HALF:n - HALF + 1] - ma
            return 2 * np.mean(xs * ref[HALF:n - HALF + 1], axis=-1)

        I0 = float(demod((0.5 * A * sq)[None, :])[0])                        # the true fundamental: no noise, no rounding
        pos = (np.arange(NPOS) + 0.5) / NPOS * qstep
        for sraw in (0.02, 0.09):
            ph = QRNG.uniform(0, 1, (NPOS, NREP, 1))
            tri = D * (np.abs(((t[None, None, :] / DPER + ph) % 1.0) - 0.5) * 2 - 0.5)
            T_ = 60.0 + pos[:, None, None] + 0.5 * A * sq[None, None, :] + tri + QRNG.normal(0, sraw, (NPOS, NREP, n))
            I = demod(np.floor(T_ / qstep) * qstep)
            del T_
            gain = np.median(I, axis=1) / I0
            sd = I.std(axis=1)
            esnr = np.where(sd > 0, I.mean(axis=1) / np.where(sd > 0, sd, 1.0), 0.0)
            seen = float(np.mean(esnr >= K_SNR))
            ok = float(np.mean(np.abs(gain - 1) <= 0.25))
            QOUT[f'{qlab}|{sraw}|{dlab}'] = {'T_s': Tq, 'swing_C': A, 'step_C': qstep, 'frac_seen': seen,
                                            'gain_p10_50_90': list(np.percentile(gain, [10, 50, 90])),
                                            'frac_gain_within_25pct': ok, 'esnr_p10_50_90': list(np.percentile(esnr, [10, 50, 90]))}
            print(f'   quantiser, {qlab}, {dlab}: swing {A*1e3:.0f} mK p-p on {qstep*1e3:.0f} mK steps, run {Tq:.0f} s, raw '
                  f'noise {sraw*1e3:.0f} mK: seen (effective SNR >= 3) at {seen*100:.0f} % of mean positions; effective SNR '
                  f'10/50/90 % {" / ".join(f"{v:.1f}" for v in np.percentile(esnr, [10, 50, 90]))}; gain 10/50/90 % '
                  f'{" / ".join(f"{v:.2f}" for v in np.percentile(gain, [10, 50, 90]))}, within 25 % at {ok*100:.0f} % [model]')
OUT['stock_quantiser'] = QOUT
OUT['eps_median'] = {lab: float(np.median(EPS[ek])) for lab, v, ek in SURFACES}
print('   (the stock firmware\'s mean cannot see a commutated pattern at all, and its high is anonymous)')

# ======================================================================================================================
hdr('H. Summary: least clock (MHz, median over draws) for fp32 randn TensorFMA, voltage at its floor | clock only')
print('Columns: one live frame; a difference image of two settled states, 1 s (25 frames) of each; lock-in 1 min, '
      '10 min, 1 h.  "<0.01" = below 10 kHz; ">600" = not at 600 MHz.  Other kernels need 1/x the power: '
      'int8 randn or fp32 ones x0.37-0.39, so about 2.6 times the clock.  Only the mean switching power per shire '
      'counts, so "clock only" is also a duty cycle at 600 MHz: x MHz = the kernel busy x/600 of the time.')
fmt = (lambda x: '>600' if not np.isfinite(x) else ('<0.01' if x <= FGRID[0] else f'{x:.3g}'))
KEYS = ['live frame', 'diff 1 s/state', 'lock-in 60 s', 'lock-in 600 s', 'lock-in 3600 s']
print(f'{"surface":52s} {"pattern":17s} ' + ' '.join(f'{k:>16s}' for k in KEYS))
for lab, v, ek in SURFACES:
    for p in PN:
        r = res[lab][p]
        print(f'{lab:52s} {p:17s} ' + ' '.join(
            f'{fmt(r[k]["fmin_MHz_floor_median"]) + "|" + fmt(r[k]["fmin_MHz_fixed_median"]):>16s}' for k in KEYS))
for (v, p), sv in sens.items():
    if v != 'c_hs':
        continue
    print(f'{"(c) sensors, heatsink on, raw codes (new BL2)":52s} {p:17s} {"":>16s} ' +
          ' '.join(f'{fmt(np.median(fm)):>16s}' for fm in sv[2]))
for where in ('(0,4)', '(0,5)'):
    print(f'{"(c) stock firmware, I/O sensor at " + where:52s} {"2x2 block moving":17s} {"":>16s} {"":>16s} ' +
          ' '.join(f'{fmt(np.median(stock[(where, T)][1])):>16s}' for T in (60, 600, 3600)))

# ---- summary for the JSON -------------------------------------------------------------------------------------------
OUT['contrast_mK_per_W'] = {v: {o: {p: list(np.percentile(np.abs(g_dc[v][o][p]) * 1e3, [5, 50, 95])) for p in PN}
                                for o in ('top', 'jn')} for v in VIEWS}
OUT['least_power'] = res
OUT['lockin_time_s_floor'] = times
OUT['sensors'] = {f'{v}|{p}': {'mK_per_W': list(np.percentile(sv[0] * 1e3, [5, 50, 95])),
                                'pmin_mW_median': [float(np.median(pm) * 1e3) for pm in sv[1]],
                                'fmin_MHz_floor_median': [float(np.median(fm)) for fm in sv[2]],
                                'columns': ['1 s per state', 'lock-in 60 s', 'lock-in 600 s', 'lock-in 3600 s']}
                  for (v, p), sv in sens.items()}
OUT['stock_io'] = {f'{w}|{T}': {'pmin_mW': list(np.percentile(pm * 1e3, [5, 50, 95])),
                                'fmin_MHz_floor_median': float(np.median(fm))} for (w, T), (pm, fm) in stock.items()}
if args.json:
    with open(args.json, 'w') as fh:
        json.dump(OUT, fh, indent=1, default=float)
    print('\nwrote', args.json)
