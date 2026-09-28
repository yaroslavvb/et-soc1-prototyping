#!/usr/bin/env python3
"""Derived numbers for the page "The effect of overheating": arithmetic on cited inputs, no new measurement.

Every input is either a formula from a cited source, a value from a cited outside source (named beside it), or a
number read from this repository's data (the file named beside it). Kind on the page: derived (D), and assumed (A)
where an input is an assumption (the lognormal sigmas). Writes
docs/reports/data/2026-09-28-overheating/analysis/derived.json. Run from the repository root:

    python3 docs/reports/data/2026-09-28-overheating/scripts/derived.py

1. Arrhenius acceleration AF(T1 -> T2) = exp(Ea/k (1/T1 - 1/T2)) (JESD47I Table 1 note a; TI SPRABX4B 4.1), checked
   against JESD47's worked example (0.7 eV, 55 -> 125 C: 78.6) and Renesas' (0.5 eV, 65 -> 150 C: about 31.5).
2. The rise that halves life at a temperature, per activation energy (0.5 eV: Renesas' worked example; 0.7 eV: JEDEC's
   and TI's working value; 0.9 eV: copper electromigration in RAMP; 1.2 eV: the top of the 0.8-1.2 eV copper range in
   Babu et al. 2025).
3. Mean or hottest for summed wear-out (RAMP's sum-of-failure-rates model, Ea 0.9 eV for copper electromigration):
   the soft-maximum width kT^2/Ea, the effective temperature of 34 regions with one hotter, the dilution bound of a
   mean over 34 sensors, and a lognormal-lifetime tail illustration (sigma 0.3 and 0.5 ASSUMED, 0.1 % design failures
   ASSUMED).
4. TI's guard-banded derating above 105 C as an equivalent activation energy.
5. Leakage doubling: Xilinx WP221's 5x from 25 to 85 C; the SRAM rail's idle power (energy manual 04a).
6. DRAM retention scaled from Liu et al. (ISCA 2013) fits: exp(-0.0498 T) typical, exp(-0.0625 T) worst cells.
7. The power-limit arithmetic of the ~120 C stop: card 0's idle 66-71 W at 115-117 C (14-card-behaviour.md) plus the
   27.2 W flip-count estimate of a random fp32 matmul on 1,024 minions (12-heat-management.md) against the card's 88 W
   12 V input (docs/research/power-telemetry.md); aifoundry2's hottest-pass peak board power from its telemetry.
8. Thermal cycling: RAMP's Coffin-Manson form for the package, cycles to failure proportional to dT^-2.35 (RAMP §3.4),
   and JESD47I Annex A's solder-joint exponent 2: the damage of one swing to 120 C against one to 65 C, both from 25 C.
"""
import gzip
import json
import math
import os
from statistics import NormalDist

K = 8.617333e-5  # Boltzmann constant, eV/K
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'analysis', 'derived.json')
DATA = os.path.join(HERE, '..', '..')  # docs/reports/data


def af(ea, t1c, t2c):
    """Acceleration of t2c over t1c (both in C)."""
    return math.exp(ea / K * (1 / (t1c + 273.15) - 1 / (t2c + 273.15)))


def halving_rise(ea, tc):
    t1 = tc + 273.15
    return 1 / (1 / t1 - K * math.log(2) / ea) - t1


J = {'k_eV_per_K': K}
# 1. checks against the sources' worked examples
J['check_jesd47_0.7eV_55_125'] = round(af(0.7, 55, 125), 1)          # JESD47: 78.6 (rounded constants)
J['check_renesas_0.5eV_65_150'] = round(af(0.5, 65, 150), 1)         # Renesas handbook p. 160: about 31.5
EAS = [0.5, 0.7, 0.9, 1.2]
J['ea_list'] = EAS
# 2. per +10 C and the halving rise
J['per10'] = {str(ea): {f'{a}->{a + 10}': round(af(ea, a, a + 10), 2) for a in (60, 85, 100, 110)} for ea in EAS}
J['halving_rise_C'] = {str(ea): {str(a): round(halving_rise(ea, a), 1) for a in (60, 85, 100, 110)} for ea in EAS}
# the page's pairs
PAIRS = [(65, 85), (85, 105), (85, 117), (65, 117), (65, 119), (65, 106), (65, 103), (95, 105), (105, 120), (90, 105),
         (103, 106), (66, 69)]
J['af_pairs'] = {str(ea): {f'{a}->{b}': round(af(ea, a, b), 2) for a, b in PAIRS} for ea in (0.5, 0.7, 0.9)}
# the curve for the chart: AF relative to 65 C (the governor's threshold) from 40 to 130 C
J['af_curve_ref_c'] = 65
J['af_curve'] = {str(ea): [[t, round(af(ea, 65, t), 5)] for t in range(40, 131, 2)] for ea in EAS}

# 3. mean or hottest
N = 34
J['softmax_width_C'] = {str(ea): round(K * 363.15 ** 2 / ea, 1) for ea in (0.7, 0.9)}   # at 90 C


def teff(temps, ea=0.9):
    s = sum(math.exp(-ea / (K * (t + 273.15))) for t in temps) / len(temps)
    return -ea / (K * math.log(s)) - 273.15


J['teff_34_regions_at_90C'] = [{'hot_by': d, 'mean': round((90 * 33 + 90 + d) / 34, 1), 'max': 90 + d,
                                'effective': round(teff([90] * 33 + [90 + d]), 1)} for d in (3, 10, 30, 45)]
J['half_share_rise_C'] = round(K * 363.15 ** 2 / 0.9 * math.log(N - 1), 0)
J['dilution_local_rise_per_1C_of_mean'] = {str(k): round(N / k, 1) for k in (1, 4, 16, 34)}
nd = NormalDist()
target = 0.001
p_region = 1 - (1 - target) ** (1 / N)
z0 = nd.inv_cdf(p_region)
tail = []
for sigma in (0.3, 0.5):
    for dT in (3, 10):
        a = af(0.9, 90, 90 + dT)
        p_hot = nd.cdf(z0 + math.log(a) / sigma)
        chip = 1 - (1 - p_region) ** (N - 1) * (1 - p_hot)
        tail.append({'sigma': sigma, 'hot_by': dT, 'af': round(a, 2), 'times_design': round(chip / target, 1),
                     'hot_share': round(p_hot / (p_hot + (N - 1) * p_region), 2)})
J['lognormal_tail'] = {'assumed': 'sigma 0.3 and 0.5; the chip designed for 0.1 % failures at its design life; 34 regions at 90 C; Ea 0.9 eV',
                       'rows': tail}

# 4. TI SPRABX4B Table 1: 0.30 of the 105 C life at 120 C, 0.20 at 125 C -> equivalent Ea
J['ti_equiv_Ea_eV'] = {'120': round(math.log(1 / 0.30) * K / (1 / 378.15 - 1 / 393.15), 2),
                       '125': round(math.log(1 / 0.20) * K / (1 / 378.15 - 1 / 398.15), 2)}
J['ti_120_rate_vs_105'] = round(1 / 0.30, 1)

# 5. leakage doubling
J['wp221_doubling_C'] = round(60 * math.log(2) / math.log(5), 1)       # Xilinx WP221: x5 from 25 to 85 C
J['sram_rail_idle'] = {'w_67C': 1.70, 'w_91C': 3.47, 'ratio': round(3.47 / 1.70, 2),
                       'doubling_C': round(24 * math.log(2) / math.log(3.47 / 1.70), 1),
                       'source': 'docs/energy-manual/04a-fine-grain.md (aifoundry2, idle)'}

# 6. DRAM retention scaled from 85 C
J['dram_retention_fraction_from_85C'] = {name: {str(t): round(math.exp(-b * (t - 85)), 2) for t in (95, 105, 117)}
                                         for name, b in (('typical', 0.0498), ('worst', 0.0625))}
J['dram_retention_per_10C'] = {'typical': round(1 - math.exp(-0.498), 3), 'worst': round(1 - math.exp(-0.625), 3)}

# 8. thermal cycling (Coffin-Manson): damage per cycle grows as dT^q; q 2.35 (RAMP, the package), 2 (JESD47I Annex A)
CM_FROM, CM_HOT, CM_REF = 25, 120, 65
J['coffin_manson'] = {'from_c': CM_FROM, 'hot_c': CM_HOT, 'ref_c': CM_REF,
                      'damage_ratio': {str(q): round(((CM_HOT - CM_FROM) / (CM_REF - CM_FROM)) ** q, 1) for q in (2, 2.35)},
                      'source': 'RAMP (ISCA 2004) §3.4, q = 2.35 for the package; JESD47I Annex A, n = 2 for solder joints'}

# 7. the power-limit arithmetic, and aifoundry2's hottest pass
J['hot_idle_plus_matmul_w'] = [round(66 + 27.2, 1), round(71 + 27.2, 1)]
J['card_input_max_w'] = 88
p11 = os.path.join(DATA, '2026-09-25-claims-v3', 'raw', 'aifoundry2', 'cat', 'p11', 'telemetry.jsonl.gz')
rows = [json.loads(line) for line in gzip.open(p11, 'rt')]
pk = max(rows, key=lambda r: r['board_w'])
J['a2_p11'] = {'samples': len(rows), 'peak_board_w': pk['board_w'], 'mean_c_at_peak': pk['temp_c']['minshire'][0],
               'hottest_c_at_peak': pk['temp_c']['minshire'][2],
               'max_mean_c': max(r['temp_c']['minshire'][0] for r in rows),
               'max_hottest_c': max(r['temp_c']['minshire'][2] for r in rows),
               'file': 'docs/reports/data/2026-09-25-claims-v3/raw/aifoundry2/cat/p11/telemetry.jsonl.gz'}
# minion+SRAM+NoC rail power at that sample over the 570 mm2 die (the power density of the hottest moment)
sp = pk.get('sp') or {}
rails = [sp.get(k) for k in ('minion_w', 'sram_w', 'noc_w')]
if all(isinstance(r, list) and r for r in rails):
    J['a2_p11']['rails_w'] = round(sum(r[0] for r in rails), 1)
    J['a2_p11']['rails_w_per_mm2'] = round(sum(r[0] for r in rails) / 570, 3)

json.dump(J, open(OUT, 'w'), indent=1, sort_keys=True)
print(json.dumps({k: v for k, v in J.items() if k != 'af_curve'}, indent=1))
