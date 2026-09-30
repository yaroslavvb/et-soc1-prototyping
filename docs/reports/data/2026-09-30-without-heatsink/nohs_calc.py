#!/usr/bin/env python3
"""Can an ET-SoC-1 card run without its heatsink?  Feasibility arithmetic for the owner's question of 29 Sep 2026.

Every input carries its source (paths relative to the repository root) or is marked
ASSUMED / ESTIMATE.  Ranges are sampled uniformly (log-uniform for h and thetas) in a Monte Carlo; outputs are
5th / 50th / 95th percentiles.  No card access; pure arithmetic.

Sections:  A package geometry and heat capacities
           B junction-to-ambient resistance of the bare lidded package on this board (still air, fan)
           C idle power laws per card, the SoC's share, slopes
           D steady state and the leakage runaway condition (theta * dP/dT < 1)
           E transients: time to 90 / 120 C, cold start and hot start, idle and load; the host-boot window
           F lid thermocouple in a heatsink groove: error budget
           G lateral decay lengths: bare lid, heatsink-on lid, delidded die (IR window), lock-in diffusion lengths
"""
import math
import numpy as np
from scipy.special import iv, kv
from scipy.integrate import solve_ivp

rng = np.random.default_rng(20260929)
N = 4000
SIGMA = 5.670e-8


def U(lo, hi, n=N):
    return rng.uniform(lo, hi, n)


def LU(lo, hi, n=N):
    return np.exp(rng.uniform(math.log(lo), math.log(hi), n))


def pct(x, p=(5, 50, 95)):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return 'n/a'
    return ' / '.join(f'{v:.3g}' for v in np.percentile(x, p))


print('=' * 100)
print('A. Package geometry and heat capacities')
print('=' * 100)
# Datasheet Fig. 9-1 (external/et-man/ET Preliminary Datasheet Rev 1.0.pdf p.33; text: txt line 1438-1445):
#   45.0 x 45.0 mm body, (44.8) lid, 2494 balls, ball dia 0.50+-0.05, standoff 0.27 min (0.43 nom), 3.95 max total,
#   (1.91) reference = lid top to substrate top.  Sec 9.1 "Package Thermal Information" is a placeholder (txt:1407-1408).
L_SUB, L_LID, H_LID_REF, H_MAX, STANDOFF = 45.0e-3, 44.8e-3, 1.91e-3, 3.95e-3, 0.43e-3
A_LID = L_LID ** 2
# Die: 570 mm^2, 25.6 x 22.2 mm (docs/reports/data/2026-09-27-chip-diagram/research/facts-numbers.json:1356)
A_DIE = 25.6e-3 * 22.2e-3
t_die = U(0.45e-3, 0.775e-3)                    # ASSUMED: thinned 0.45 mm .. full 300 mm wafer 0.775 mm
t_bump_tim1 = U(0.10e-3, 0.25e-3)               # ASSUMED: C4 + underfill ~0.08, TIM1 0.03-0.15
t_lid = np.clip(H_LID_REF - t_die - t_bump_tim1, 0.6e-3, 1.4e-3)   # DERIVED from the (1.91) reference height
t_sub = H_MAX - H_LID_REF - STANDOFF                               # ~1.61 mm max-stack substrate
RHOC_CU, RHOC_SI, K_CU = 8960 * 385, 2330 * 705, 390.0
rhoc_sub = U(1.9e6, 2.4e6)                      # ESTIMATE: organic build-up + Cu
C_die = RHOC_SI * A_DIE * t_die
C_lid = RHOC_CU * (A_LID * t_lid + 4 * L_LID * 2e-3 * (H_LID_REF - t_lid))   # plate + 2 mm wall ring
C_sub_all = rhoc_sub * L_SUB ** 2 * t_sub
f_sub_fast = U(0.4, 1.0)                        # ESTIMATE: share of the substrate that follows the die within seconds
C_balls = 2494 * (math.pi / 6 * 0.5e-3 ** 3) * 7400 * 230
C_J = C_die + C_lid + f_sub_fast * C_sub_all + C_balls
print(f'lid plate thickness (derived) mm: {pct(t_lid*1e3)}; substrate {t_sub*1e3:.2f} mm')
print(f'C_die J/K {pct(C_die)} | C_lid {pct(C_lid)} | C_substrate(all) {pct(C_sub_all)} | balls {C_balls:.2f}')
print(f'C_J (die+lid+fast substrate) J/K: {pct(C_J)}')
# Foster stages (docs/findings/11-thermal-model.md:29-31): C = tau/R
taus = [1.5, 4, 60, 150, 400, 2500]
Rs = [0.106, 0.050, 0.234, 0.136, 0.860, 0.081]
print('Foster stages C = tau/R (J/K): ' + ', '.join(f'{t:g}s:{t/r:.1f}' for t, r in zip(taus, Rs)),
      f'| R1+R2 = {Rs[0]+Rs[1]:.3f} C/W, total {sum(Rs):.2f} C/W')
# Board (dev card V3 167.6 x 111.8 mm per the plan Q5; 6.6 x 4.4 in on the assembly drawing, ET-PCIe-Dev-Card-V3.pdf p.3)
A_BOARD = 0.1676 * 0.1118
t_pcb = U(1.6e-3, 2.4e-3)                       # ASSUMED
C_board_all = U(2.0e6, 2.3e6) * A_BOARD * t_pcb + U(10, 30)        # + components (DRAM, VRM, inductors), ESTIMATE
f_board_near = U(0.4, 0.8)                      # share within ~one fin length of the package, ESTIMATE
C_B = f_board_near * C_board_all
print(f'C_board(all) J/K {pct(C_board_all)}; C_B (near package) {pct(C_B)}')

print()
print('=' * 100)
print('B. theta_JA of the bare lidded package on this board')
print('=' * 100)
AIR_K, AIR_NU, PR = 0.028, 1.75e-5, 0.71


def h_nat(dT, L):
    """vertical plate, laminar natural convection (Churchill-Chu simplified): h = 1.42 (dT/L)^0.25"""
    return 1.42 * (np.maximum(dT, 1.0) / L) ** 0.25


def h_forced(u, L, boost):
    """flat plate laminar + a turbulence/impingement boost factor for a fan"""
    Re = u * L / AIR_NU
    return boost * 0.664 * AIR_K / L * Re ** 0.5 * PR ** (1 / 3)


def h_rad(eps, T_s, T_a):
    Ts, Ta = T_s + 273.15, T_a + 273.15
    return eps * SIGMA * (Ts ** 2 + Ta ** 2) * (Ts + Ta)


def annular_fin_R(h, kt, r1, r2):
    """thermal resistance of an annular fin (both faces convecting with h) from r1 to r2; kt = in-plane sheet
    conductance (W/K); tip adiabatic.  Standard Bessel solution."""
    m = np.sqrt(2 * h / kt)
    num = kv(1, m * r1) * iv(1, m * r2) - iv(1, m * r1) * kv(1, m * r2)
    den = kv(0, m * r1) * iv(1, m * r2) + iv(0, m * r1) * kv(1, m * r2)
    Q_per_theta = 2 * np.pi * r1 * kt * m * num / den
    return 1.0 / Q_per_theta, 1.0 / m


r1 = L_SUB / math.sqrt(math.pi)                 # 25.4 mm, the footprint's equivalent radius
r2 = math.sqrt(A_BOARD / math.pi)               # 77 mm, the board's equivalent radius
kt_board = LU(0.05, 0.25)                       # ASSUMED: 3-15 x 1 oz planes (35 um Cu, 390 W/mK) in a ~12-layer 88 W card
theta_JB = LU(1.0, 3.0)                         # ASSUMED: junction->board through bumps, substrate, balls (45 mm lidded FCBGA)
theta_JC = U(0.03, 0.10)                        # ASSUMED: junction->lid top, 570 mm^2 die, TIM1 + lid
eps_lid = U(0.05, 0.3)                          # Ni/Au-plated lid (vendor photo, dev-card PDF p.2), unless taped
eps_pcb = U(0.8, 0.9) * U(0.5, 1.0)             # solder mask, times a view factor to neighbours in a rig
Ta_s = U(22.0, 30.0)                            # lab ambient; fitted intercepts 22.8 and 28.0 C (11-thermal-model.md:33)
# still air: surfaces at 60-100 C
Tlid_s, Tpcb_s = U(60, 100), U(45, 75)
h_lid_still = h_nat(Tlid_s - Ta_s, 0.045) + h_rad(eps_lid, Tlid_s, Ta_s)
h_pcb_still = 0.75 * h_nat(Tpcb_s - Ta_s, 0.11) + h_rad(eps_pcb, Tpcb_s, Ta_s)  # 0.75: underside/horizontal penalty
# fan: 1-2.5 m/s, boost 1.2-2 for turbulence / impingement
u = U(1.0, 2.5)
boost = U(1.2, 2.0)
h_lid_fan = h_forced(u, 0.045, boost) + h_rad(eps_lid, Tlid_s, Ta_s)
h_pcb_fan = h_forced(u, 0.17, boost) + h_rad(eps_pcb, Tpcb_s, Ta_s)


def theta_JA(h_lid, h_pcb):
    R_lid = 1.0 / (h_lid * A_LID)
    R_BA, lam = annular_fin_R(h_pcb, kt_board, r1, r2)
    # the package's own footprint also convects from the board's far side; small, folded into the fin
    th = 1.0 / (1.0 / (theta_JC + R_lid) + 1.0 / (theta_JB + R_BA))
    return th, R_lid, R_BA, lam


th_still, Rlid_still, RBA_still, lam_still = theta_JA(h_lid_still, h_pcb_still)
th_fan, Rlid_fan, RBA_fan, lam_fan = theta_JA(h_lid_fan, h_pcb_fan)
print(f'h still air: lid {pct(h_lid_still)} W/m2K, board {pct(h_pcb_still)}; fan 1-2.5 m/s: lid {pct(h_lid_fan)}, board {pct(h_pcb_fan)}')
print(f'R lid-top->air: still {pct(Rlid_still)} C/W, fan {pct(Rlid_fan)}')
print(f'board fin: decay length 1/m still {pct(lam_still*1e3)} mm; R_BA still {pct(RBA_still)} C/W, fan {pct(RBA_fan)}')
print(f'theta_JA bare, STILL AIR: {pct(th_still)} C/W   (cross-check: AMD UG575 lidded 40-47.5 mm, no heatsink, 5.4-7.9 C/W)')
print(f'theta_JA bare, FAN 1-2.5 m/s: {pct(th_fan)} C/W   (cross-check: AMD 1.3-2.5 m/s 2.7-4.8, Microchip 35 mm 4.98-5.80 C/W)')
print('share of heat through the lid top (still):', pct((theta_JB + RBA_still) / ((theta_JB + RBA_still) + (theta_JC + Rlid_still))))
# a blended theta range for the runaway and transient sections: our physics range widened to cover the vendor tables
TH_STILL = (4.0, 12.0)
TH_FAN = (2.0, 7.0)
print(f'ranges carried forward: still {TH_STILL}, fan {TH_FAN} C/W')

print()
print('=' * 100)
print('C. Idle power laws, SoC share, slopes')
print('=' * 100)
# Board-power idle laws, docs/reports/data/2026-09-28-overheating/analysis/idle_vs_temp.txt:4,13,21 (E44 cycles)
LAWS = {
    'aifoundry2': (12.24, 23.71, 36.0),
    'aifoundry3': (15.45, 21.89, 30.0),
    'aifoundry1-c1': (18.45, 30.50, 30.0),
}
# Card 0 at 300 MHz / 399 mV (firmware 1.4.1): 17.97 W at 62 C, slope 0.207 W/C over 60-64 C,
# metered rails 7.75 W (minion 4.11, SRAM 0.88, NoC 2.75), rails slope 0.180 W/C.
# Source: card0_guard.py over the 21 guard.jsonl.gz files (12,035 samples) under docs/reports/data/.
C0_P62, C0_S62 = 17.97, 0.207


def P_board(card, T, TL_c0=30.0):
    if card == 'aifoundry1-c0@300':
        A = C0_S62 * TL_c0
        return (C0_P62 - A) + A * np.exp((T - 62.0) / TL_c0)
    Pf, A, TL = LAWS[card]
    return Pf + A * np.exp((T - 80.0) / TL)


def dP_board(card, T, TL_c0=30.0):
    if card == 'aifoundry1-c0@300':
        return C0_S62 * np.exp((T - 62.0) / TL_c0)
    Pf, A, TL = LAWS[card]
    return A / TL * np.exp((T - 80.0) / TL)


# Measured idle points (the card table, docs/findings/14-card-behaviour.md:325; E19 16-dvfs-and-leakage.md:170-174)
IDLE_PT = {'aifoundry2': 73.0, 'aifoundry3': 56.0, 'aifoundry1-c1': 60.0, 'aifoundry1-c0@300': 62.0}
# Off-die share of idle board power (ESTIMATE): minion/NoC VRM loss (fitted 0.19 of the minion rail, 0.29 of NoC,
# 19-observability:36-38,67; tree says 80 % efficiency), SRAM regulator, DRAM (4 LPDDR4X, tree budget <=3.2 W max),
# 3.3/1.8 V misc (tree: 0.70 W PCIe buffer+eMMC, eMMC, flash, uC), FS1406 losses (88 %).
P_OFF = {'aifoundry2': (5.0, 8.2), 'aifoundry3': (4.5, 7.5), 'aifoundry1-c1': (5.5, 9.0), 'aifoundry1-c0@300': (3.8, 6.0)}
F_SLOPE = (0.80, 0.95)   # share of the idle slope on the die: rails 0.525/(0.525+0.100) a2, 0.767/0.929 c1, 0.180/0.207 c0
RAILS = {'aifoundry2': (73, 16.68, 31.73), 'aifoundry1-c1': (73, 24.83, 42.6), 'aifoundry3': (70, 17.4, 31.1),
         'aifoundry1-c0@300': (62, 7.75, 17.97)}
for card, (T, rails, board) in RAILS.items():
    lo, hi = P_OFF[card]
    print(f'{card:18s} at {T} C: board {board:.2f} W, metered rails {rails:.2f} W ({rails/board:.0%}), unmetered '
          f'{board-rails:.2f} W; SoC = board - off-die({lo}-{hi}) = {board-hi:.1f}-{board-lo:.1f} W '
          f'({(board-hi)/board:.0%}-{(board-lo)/board:.0%})')
for card in ['aifoundry2', 'aifoundry3', 'aifoundry1-c1', 'aifoundry1-c0@300']:
    T0 = IDLE_PT[card]
    s = ', '.join(f'{T}C {dP_board(card, T):.2f}' for T in (40, 50, 60, 70, 80, 90, 100, 110, 120))
    print(f'{card:18s} idle board at {T0:.0f} C = {P_board(card, T0):.1f} W; dP/dT (W/C): {s}')
# With-heatsink effective thetas (board-power basis) from the idle points, Ta 22-28 C
for card in ['aifoundry2', 'aifoundry3', 'aifoundry1-c1', 'aifoundry1-c0@300']:
    T0 = IDLE_PT[card]
    print(f'{card:18s} effective theta with its cooler (board basis) {(T0-28)/P_board(card,T0):.2f}-{(T0-22)/P_board(card,T0):.2f} C/W')
print('aifoundry2 fitted network: 1.47 C/W (11-thermal-model.md:31); runaway.txt: loop gain 1 at 81.9 C, '
      'rest 62.1 C / threshold 98.7 C at Ta 22.8, no equilibrium at Ta 28')

print()
print('=' * 100)
print('D. Steady state and the runaway condition theta * dP/dT < 1')
print('=' * 100)


def soc_power(card, T, Poff, fs, TL_c0=30.0):
    """P_SoC(T) = board(T0) - Poff + fs * (board(T) - board(T0)), anchored at the card's measured idle point"""
    T0 = IDLE_PT[card]
    return P_board(card, T0, TL_c0) - Poff + fs * (P_board(card, T, TL_c0) - P_board(card, T0, TL_c0))


def equilibria(card, theta, Ta, Poff, fs, extra=0.0, TL_c0=30.0):
    """roots of g(T) = Ta + theta * (P_SoC(T) + extra) - T on 20..250 C; returns (stable, threshold) or (None, None)"""
    T = np.linspace(Ta + 0.01, 250, 4000)
    g = Ta + theta * (np.maximum(soc_power(card, T, Poff, fs, TL_c0), 0) + extra) - T
    sgn = np.sign(g)
    idx = np.where(np.diff(sgn) != 0)[0]
    if len(idx) == 0:
        return None, None
    stable = T[idx[0]]
    thr = T[idx[1]] if len(idx) > 1 else None
    return stable, thr


def theta_max(card, Ta, Poff, fs, extra=0.0, TL_c0=30.0):
    lo, hi = 0.05, 30.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        s, _ = equilibria(card, mid, Ta, Poff, fs, extra, TL_c0)
        if s is not None:
            lo = mid
        else:
            hi = mid
    return lo


for card in ['aifoundry2', 'aifoundry3', 'aifoundry1-c1', 'aifoundry1-c0@300']:
    lo, hi = P_OFF[card]
    tms = []
    for Ta, Poff, fs in [(22, hi, 0.80), (25, 0.5*(lo+hi), 0.875), (30, lo, 0.95)]:
        tms.append(theta_max(card, Ta, Poff, fs))
    gains = []
    for T in (50, 60, 70, 80):
        g_lo = TH_FAN[0] * F_SLOPE[0] * dP_board(card, T)
        g_hi = TH_STILL[1] * F_SLOPE[1] * dP_board(card, T)
        g_still_lo = TH_STILL[0] * F_SLOPE[0] * dP_board(card, T)
        gains.append(f'{T}C: fan {g_lo:.2f}.. still {g_still_lo:.2f}-{g_hi:.2f}')
    print(f'{card:18s} largest theta (SoC basis) with ANY idle equilibrium: {min(tms):.2f}-{max(tms):.2f} C/W '
          f'(best case Ta 22 .. worst Ta 30)')
    print(f'{"":18s} bare loop gain theta*dP_SoC/dT  ' + ' | '.join(gains))
    # open-loop rise (no leakage feedback) at the idle point's SoC power
    Psoc0 = P_board(card, IDLE_PT[card]) - np.array([hi, lo])
    print(f'{"":18s} open-loop rise at idle SoC power {Psoc0[0]:.1f}-{Psoc0[1]:.1f} W: still {Psoc0[0]*TH_STILL[0]:.0f}-'
          f'{Psoc0[1]*TH_STILL[1]:.0f} C, fan {Psoc0[0]*TH_FAN[0]:.0f}-{Psoc0[1]*TH_FAN[1]:.0f} C above ambient')
# Monte Carlo: fraction of draws with any equilibrium below 90 C
print('Monte Carlo (theta log-uniform in the range, Ta 22-30, Poff and slope share in range): fraction with a stable '
      'idle equilibrium, and its temperature')
for card in ['aifoundry2', 'aifoundry3', 'aifoundry1-c1', 'aifoundry1-c0@300']:
    for label, rngth in (('still', TH_STILL), ('fan', TH_FAN)):
        n = 600
        th = LU(*rngth, n)
        Ta = U(22, 30, n)
        Poff = U(*P_OFF[card], n)
        fs = U(*F_SLOPE, n)
        TLc0 = U(25, 36, n)
        st = []
        for i in range(n):
            s, _ = equilibria(card, th[i], Ta[i], Poff[i], fs[i], 0.0, TLc0[i])
            st.append(np.nan if s is None else s)
        st = np.array(st)
        ok = np.isfinite(st)
        print(f'  {card:18s} {label:5s}: equilibrium in {ok.mean():.0%} of draws ({ok.sum()} of {n}); below 90 C in {(st<90).mean():.0%}; '
              f'T_eq {pct(st[ok]) if ok.any() else "none"}')
# with the heatsink, for reference (board basis, aifoundry2 model 12.63 + 23.26 e^((T-80)/36), R 1.467)
print('with the heatsink (a2 model): loop gain at 80 C = 1.467 * 23.26/36 = %.3f' % (1.467 * 23.26 / 36))

print()
print('=' * 100)
print('E. Transients: 2-node model (package node C_J, board node C_B)')
print('=' * 100)


def simulate(card, th_JB, R_lid, R_BA, CJ, CB, Ta, Poff, fs, phi, extra_soc, TJ0, TB0, t_end=900.0, TL_c0=30.0):
    """C_J dTJ/dt = P_SoC(TJ) + extra - (TJ-TB)/th_JB - (TJ-Ta)/R_lid
       C_B dTB/dt = phi*Poff + (TJ-TB)/th_JB - (TB-Ta)/R_BA"""
    def f(t, y):
        TJ, TB = y
        P = max(soc_power(card, TJ, Poff, fs, TL_c0), 0.0) + extra_soc
        q = (TJ - TB) / th_JB
        return [(P - q - (TJ - Ta) / R_lid) / CJ, (phi * Poff + q - (TB - Ta) / R_BA) / CB]

    def hit(level):
        def ev(t, y):
            return y[0] - level
        ev.terminal = False
        ev.direction = 1
        return ev
    e90, e120, e150 = hit(90.0), hit(120.0), hit(150.0)
    e150.terminal = True
    sol = solve_ivp(f, (0, t_end), [TJ0, TB0], events=[e90, e120, e150], max_step=0.5, dense_output=True)
    t90 = sol.t_events[0][0] if len(sol.t_events[0]) else np.inf
    t120 = sol.t_events[1][0] if len(sol.t_events[1]) else np.inf
    Tat = [float(sol.sol(min(tt, sol.t[-1]))[0]) if tt <= sol.t[-1] else 150.0 for tt in (30, 60, 90)]
    return t90, t120, Tat


def mc_transient(card, air, extra_soc, start, n=500):
    thJB = LU(1.0, 3.0, n)
    if air == 'still':
        Rlid = 1.0 / (U(8, 15, n) * A_LID) + U(0.03, 0.10, n)
        RBA = LU(2.5, 8.0, n)
    else:
        Rlid = 1.0 / (U(20, 50, n) * A_LID) + U(0.03, 0.10, n)
        RBA = LU(0.8, 3.0, n)
    CJ = U(9.0, 18.0, n)
    CB = U(30.0, 80.0, n)
    Ta = U(22.0, 30.0, n)
    Poff = U(*P_OFF[card], n)
    fs = U(*F_SLOPE, n)
    phi = U(0.3, 1.0, n)
    TLc0 = U(25, 36, n)
    out = []
    for i in range(n):
        if start == 'cold':
            TJ0, TB0 = Ta[i], Ta[i]
        else:  # the card's idle state with its cooler, then the cooler is gone (e.g. a2 at 73 C, board ~50 C)
            TJ0 = IDLE_PT[card]
            TB0 = Ta[i] + 0.5 * (IDLE_PT[card] - Ta[i])
        out.append(simulate(card, thJB[i], Rlid[i], RBA[i], CJ[i], CB[i], Ta[i], Poff[i], fs[i], phi[i], extra_soc,
                            TJ0, TB0, TL_c0=TLc0[i]))
    t90 = np.array([o[0] for o in out])
    t120 = np.array([o[1] for o in out])
    T30 = np.array([o[2][0] for o in out])
    T60 = np.array([o[2][1] for o in out])
    T90 = np.array([o[2][2] for o in out])
    th_eff = 1.0 / (1.0 / Rlid + 1.0 / (thJB + RBA))
    return t90, t120, T30, T60, T90, th_eff


# SoC share of a full random fp32 matmul on 1,024 minions at 600 MHz: +27.2 W switching (12-heat-management.md:20),
# of which 12-17 % is off-rail (19-observability:64-67) -> +22.6..23.9 W on the die.  Mid load: ones, +10.7 W (-> ~9 W).
LOADS = [('idle', 0.0), ('+9 W (ones, 1,024)', 9.0), ('+23 W (randn, 1,024)', 23.0)]
print('columns: time to 90 C | time to 120 C | T_J at 30 / 60 / 90 s after power-on (5th/50th/95th pct; inf = never)')
for card in ['aifoundry2', 'aifoundry3', 'aifoundry1-c1', 'aifoundry1-c0@300']:
    for air in ('still', 'fan'):
        for lab, extra in LOADS:
            if card == 'aifoundry1-c0@300' and extra > 0:
                continue   # any kernel takes card 0 to 600 MHz (14-card-behaviour.md:137-140)
            t90, t120, T30, T60, T90, th_eff = mc_transient(card, air, extra, 'cold', n=300)
            print(f'COLD {card:18s} {air:5s} {lab:22s} t90 {pct(np.where(np.isinf(t90), 1e9, t90))} s | '
                  f't120 {pct(np.where(np.isinf(t120), 1e9, t120))} s | T@30s {pct(T30)} | T@60s {pct(T60)} | '
                  f'T@90s {pct(T90)} C | never 90: {np.isinf(t90).mean():.0%}')
    if card == 'aifoundry2':
        t90, t120, T30, T60, T90, th_eff = mc_transient(card, 'still', 0.0, 'hot', n=300)
        print(f'HOT  {card:18s} still idle, cooler removed at 73 C: t90 {pct(t90)} s, t120 {pct(np.where(np.isinf(t120), 1e9, t120))} s')
        t90, t120, T30, T60, T90, th_eff = mc_transient(card, 'still', 23.0, 'hot', n=300)
        print(f'HOT  {card:18s} still +23 W, cooler removed at 73 C: t90 {pct(t90)} s, t120 {pct(np.where(np.isinf(t120), 1e9, t120))} s')
# adiabatic initial rates
P_idle_soc = U(20, 27)
print(f'adiabatic initial heating rate, idle SoC 20-27 W over C_J: {pct(P_idle_soc / C_J)} C/s; '
      f'+23 W load: {pct((P_idle_soc + 23) / C_J)} C/s')
print('with the heatsink (measured): a2 randn 1,024 from 80 C: 90 C in 19-26 s; ones 107-167 s (12-heat-management.md:20,28); '
      'a3 55 -> 88 C in 150 two-second launches (14-card-behaviour.md:465)')
print('host power-on to first telemetry: ASSUMED 30-90 s (desktop POST 10-40 s + Ubuntu boot + driver); not recorded in the repo')


def mc_boot_then_burst(card, air, extra_soc, n=300):
    """power on cold; the card idles while the host boots (t_boot 30-90 s, ASSUMED); then a load step of extra_soc.
    Returns T_J at t_boot and the seconds from t_boot to 90 C (the usable window)."""
    thJB = LU(1.0, 3.0, n)
    if air == 'still':
        Rlid = 1.0 / (U(8, 15, n) * A_LID) + U(0.03, 0.10, n)
        RBA = LU(2.5, 8.0, n)
    else:
        Rlid = 1.0 / (U(20, 50, n) * A_LID) + U(0.03, 0.10, n)
        RBA = LU(0.8, 3.0, n)
    CJ, CB, Ta = U(9.0, 18.0, n), U(30.0, 80.0, n), U(22.0, 30.0, n)
    Poff, fs, phi, tb = U(*P_OFF[card], n), U(*F_SLOPE, n), U(0.3, 1.0, n), U(30.0, 90.0, n)
    Tb, win = [], []
    for i in range(n):
        def f(t, y, extra):
            TJ, TB = y
            P = max(soc_power(card, TJ, Poff[i], fs[i]), 0.0) + extra
            q = (TJ - TB) / thJB[i]
            return [(P - q - (TJ - Ta[i]) / Rlid[i]) / CJ[i], (phi[i] * Poff[i] + q - (TB - Ta[i]) / RBA[i]) / CB[i]]
        cap = lambda t, y: y[0] - 150.0
        cap.terminal, cap.direction = True, 1
        s1 = solve_ivp(lambda t, y: f(t, y, 0.0), (0, tb[i]), [Ta[i], Ta[i]], events=[cap], max_step=0.5)
        y1 = s1.y[:, -1]
        Tb.append(min(y1[0], 150.0))   # 150 = ran away past 150 C before the host was up
        if y1[0] >= 90:
            win.append(0.0)
            continue
        ev = lambda t, y: y[0] - 90.0
        ev.terminal, ev.direction = True, 1
        s2 = solve_ivp(lambda t, y: f(t, y, extra_soc), (0, 1800), y1, events=[ev], max_step=0.5)
        win.append(s2.t_events[0][0] if len(s2.t_events[0]) else np.inf)
    return np.array(Tb), np.array(win)


print('BOOT THEN BURST: die at the end of the host boot, and seconds from then to 90 C (the usable window)')
for card in ['aifoundry2', 'aifoundry3', 'aifoundry1-c1']:
    for air in ('still', 'fan'):
        for lab, extra in LOADS:
            Tb, win = mc_boot_then_burst(card, air, extra)
            print(f'  {card:14s} {air:5s} {lab:22s} T_J at boot end {pct(Tb)} C | window to 90 C '
                  f'{pct(np.where(np.isinf(win), 1e9, win))} s | already >=90 at boot: {(win==0).mean():.0%}')

print()
print('=' * 100)
print("F. Thermocouple in a heatsink-base groove on the lid (a variant of Intel's grooved-lid Tcase): error budget")
print('=' * 100)
A_TIM2 = A_LID
Rpp_tim2 = U(0.1e-4, 0.5e-4, N)             # m2K/W, paste 0.1-0.5 K cm2/W (ESTIMATE)
R_tim2 = Rpp_tim2 / A_TIM2
theta_jc = U(0.03, 0.10)
Pidle, Pload = U(20, 27), U(43, 50)
frac_in_tim = U(0.2, 0.8)                     # where the bead sits within the TIM2 gradient
bias_tim = frac_in_tim * R_tim2 * Pidle
groove_bias = U(0.1, 0.5)                     # local loss of heatsink contact over ~11 mm2 of 2007 mm2 (ESTIMATE)
tc_tol = U(0.3, 1.0)                          # type T 0.5 C special limits / after a 2-point calibration
cjc = U(0.2, 0.7)
abs_err = np.sqrt(bias_tim ** 2 + groove_bias ** 2 + tc_tol ** 2 + cjc ** 2)
print(f'TIM2 dT at idle {pct(R_tim2*Pidle)} C; bead bias {pct(bias_tim)} C; absolute error (rss) {pct(abs_err)} C')
print(f'die mean - lid centre (theta_JC * P): idle {pct(theta_jc*Pidle)} C, under +23 W load {pct(theta_jc*Pload)} C')
print('relative (step) resolution with a 24-bit logger: 0.02-0.1 C; bead time constant 0.1-0.5 s (36-40 AWG)')
print('on-die reading to the host: whole degrees, mean of 34 sensors + anonymous peak-hold (14-card-behaviour.md:254; '
      '05-claims.md:652-653); step-time trick 0.03 C on repeats (14-card-behaviour.md:274-283)')

print()
print('=' * 100)
print('G. Lateral decay lengths and what an IR camera could see')
print('=' * 100)
tl = U(0.5e-3, 1.3e-3)
kt_lid = K_CU * tl
h_still = U(8, 15)
lam_lid_fin = np.sqrt(kt_lid / h_still)
print(f'bare lid as a convectively cooled fin, sqrt(k t / h), t 0.5-1.3 mm, h 8-15: {pct(lam_lid_fin*1e3)} mm  '
      f'(plan: ~200 mm; t=1 mm, h=10 gives {math.sqrt(390*1e-3/10)*1e3:.0f} mm)')
Rpp2 = U(1e-5, 5e-5)
lam_on = np.sqrt(kt_lid * Rpp2)
print(f'lid with the heatsink on, sqrt(k t R"_TIM2), R" 0.1-0.5 K cm2/W: {pct(lam_on*1e3)} mm (plan: ~3.7 mm)')
kt_si = U(110, 150) * U(0.45e-3, 0.775e-3)
Rpp_down = U(0.5e-3, 2.0e-3)                  # heatsink off: heat forced down through substrate (theta_JB x A_die ~ 1e-3)
lam_off_comp = np.sqrt((kt_lid + kt_si) * Rpp_down)
print(f'heatsink OFF, die+lid composite over the substrate, sqrt((kt_lid+kt_si) R"_down), R"_down 5-20 K cm2/W: '
      f'{pct(lam_off_comp*1e3)} mm  -> die ~22-26 mm wide: near-isothermal at shire scale (3.7 mm)')
# a 1 W hot shire on the bare composite: excess ~ P/(2 pi G) K0(r/lam)
G = kt_lid + kt_si
for r in (2e-3, 10e-3, 20e-3):
    print(f'  1 W concentrated (one shire), heatsink off: excess at r = {r*1e3:.0f} mm: {pct(1/(2*np.pi*G)*kv(0, r/lam_off_comp))} C')
Rpp_tim1 = U(0.5e-5, 3e-5)
lam_tim1 = np.sqrt(kt_lid * Rpp_tim1)
print(f'lid following the die through TIM1, sqrt(k t R"_TIM1): {pct(lam_tim1*1e3)} mm')
h_win = LU(5e3, 2e4)
lam_delid = np.sqrt(kt_si / h_win)
print(f'delidded die under an IR-window liquid cooler (h 5e3-2e4 W/m2K), sqrt(k_Si t / h): {pct(lam_delid*1e3)} mm')
alpha_si = U(7e-5, 9e-5)
for f in (1, 5, 10):
    print(f'  lock-in diffusion length in Si at {f} Hz, sqrt(alpha/(pi f)): {pct(np.sqrt(alpha_si/(np.pi*f))*1e3)} mm')
print('shire pitch 3.7 mm (facts-numbers.json:1356); the P3 camera is LWIR 8-14 um, 25 Hz (plan 2a); sapphire is opaque '
      'there, so an IR-window cooler for it needs Ge/ZnSe and a LWIR-transparent coolant (none common): an MWIR camera job')
