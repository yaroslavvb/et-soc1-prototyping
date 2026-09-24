"""Arithmetic/units re-check of the heat-per-mm report numbers (reads report.json and wire.json only)."""
import json, math, numpy as np
R = json.load(open('/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/data/2026-09-24-wire-energy/report.json'))
W = R['wire']; H = R['headline']; IN = R['inputs']; X = R['context']
L = IN['hop_mm']['value']; s09 = R['scaled']['0.9']
print('V^2 factor (0.9/0.485)^2 =', round((0.9/0.485)**2, 4), 'report', round(s09, 4))
print('hop sqrt(3.73*3.70) =', round(math.sqrt(3.73*3.70), 4), '; pitch.json cases A/B/C 3.735/3.711/3.637')
# pJ/B/hop -> fJ/bit/hop -> fJ/bit/mm
for k in ('v2/noc_rail', 'v2/board', 'v1/noc_rail', 'v1/board'):
    m = W['model'][k.split('/')[0]][k.split('/')[1]]
    a, b, s0 = m['toggle_fj_per_bit_transition_hop']['mean'], m['ones_fj_per_one_bit_hop']['mean'], m['s0_pj_per_byte_hop']['mean']
    print(f"{k:12s} a {a:6.1f} b {b:6.1f} fJ/bit/hop; s0 {s0:.4f} pJ/B/hop = {s0*125:.1f} fJ/bit/hop; random data 0.5a+0.5b {0.5*a+0.5*b:.1f}; per mm: a {a/L:.1f} b {b/L:.1f} data {(0.5*a+0.5*b)/L:.1f} fixed {s0*125/L:.1f} total {(0.5*a+0.5*b+s0*125)/L:.1f}; rms {m['rms_pj_per_byte_hop']['mean']:.4f}")
UN, UB, HN, HB = H['uncontended/noc_rail'], H['uncontended/board'], H['v2/noc_rail'], H['v2/board']
print('uncontended NoC  data+fixed per mm %.2f + %.2f = %.2f' % (UN['random_bit_data']['mean'], UN['fixed_per_bit']['mean'], UN['random_bit_total']['mean']))
print('uncontended board data+fixed per mm %.2f + %.2f = %.2f' % (UB['random_bit_data']['mean'], UB['fixed_per_bit']['mean'], UB['random_bit_total']['mean']))
print('loaded NoC %.2f + %.2f = %.2f ; loaded board %.2f + %.2f = %.2f' % (HN['random_bit_data']['mean'], HN['fixed_per_bit']['mean'], HN['random_bit_total']['mean'], HB['random_bit_data']['mean'], HB['fixed_per_bit']['mean'], HB['random_bit_total']['mean']))
print('contention ratio loaded/free, NoC %.2f board %.2f; share of loaded cost NoC %.2f board %.2f' % (HN['random_bit_total']['mean']/UN['random_bit_total']['mean'], HB['random_bit_total']['mean']/UB['random_bit_total']['mean'], 1-UN['random_bit_total']['mean']/HN['random_bit_total']['mean'], 1-UB['random_bit_total']['mean']/HB['random_bit_total']['mean']))
dj = W['disjoint_flows']
for key in ('noc_pj_per_byte', 'pj_per_byte'):
    s, u, s4 = dj[key]['wsep'], dj[key]['wu'], dj[key]['wsep_d1_4']
    print(key, 'wsep d1-5 data %.1f zeros %.1f | wsep d1-4 data %.1f zeros %.1f | wu d1-4 data %.1f zeros %.1f | total ratio wu/wsep %.2f' % (
        s['random_minus_zeros_fj_per_bit_hop']['mean'], s['zeros_fj_per_bit_hop']['mean'], s4['random_minus_zeros_fj_per_bit_hop']['mean'], s4['zeros_fj_per_bit_hop']['mean'],
        u['random_minus_zeros_fj_per_bit_hop']['mean'], u['zeros_fj_per_bit_hop']['mean'], u['random_fj_per_bit_hop']['mean']/s['random_fj_per_bit_hop']['mean']))
print('scaled to 0.9 V data: free NoC %.1f, free board %.1f, loaded NoC %.1f, loaded board %.1f; loaded NoC total %.1f' % tuple(v*s09 for v in (UN['random_bit_data']['mean'], UB['random_bit_data']['mean'], HN['random_bit_data']['mean'], HB['random_bit_data']['mean'], HN['random_bit_total']['mean'])))
print('per transition at 0.9 V: NoC %.1f board %.1f  (Keckler 240 per transition)' % (HN['per_transition']['mean']*s09, HB['per_transition']['mean']*s09))
V = 0.485
print('C_eff per transition (2E/V^2) fF/mm: NoC %.0f board %.0f; per random bit (4E/V^2): free NoC %.0f loaded board %.0f; Keckler per random bit 4*121/0.81 = %.0f, per transition 2*240/0.81 = %.0f' % (
    2*HN['per_transition']['mean']/V**2, 2*HB['per_transition']['mean']/V**2, 4*UN['random_bit_data']['mean']/V**2, 4*HB['random_bit_data']['mean']/V**2, 4*121/0.81, 2*240/0.81))
# literature arithmetic
print('Keckler 310 pJ/(256*10) = %.1f fJ; Yale75 174/(2560) = %.1f; CACM22 77pJ/(64*40) = %.1f, 1.9pJ/64 = %.1f; Ho 9.84pJ/10mm = %.0f per transition' % (310e3/2560, 174e3/2560, 77e3/(64*40), 1.9e3/64, 9840/10))
fp = R['first_principles']
print('first principles 0.485 V per random bit', [round(x, 1) for x in fp['at_0485']['per_random_bit_fj_mm']], '; with 222-374 fF/mm:', round(222*V**2/4, 1), round(374*V**2/4, 1))
# practical
perB, perBb = HN['random_bit_total']['mean']*8*L/1000, HB['random_bit_total']['mean']*8*L/1000
dram = X['dram_read_pj_per_byte']
print('per hop pJ/B: %.3f - %.3f ; 10 hops line nJ: %.3f - %.3f ; DRAM line %.3f nJ ; ratio %.2f - %.2f' % (perB, perBb, 64*perB*10/1000, 64*perBb*10/1000, 64*dram/1000, dram/(perBb*10), dram/(perB*10)))
C = W['configs']
def line(pre, key, ds=(1, 2, 3, 4, 6)):
    xs = [d for d in ds if C.get(pre+str(d))]; ys = [C[pre+str(d)][key]['mean'] for d in xs]
    s, i = np.polyfit(xs, ys, 1); return s, i, C[pre+'0'][key]['mean'] if C.get(pre+'0') else None
s, i, e0 = line('wu/p0.5/hop', 'pj_per_byte')
print('board wu P=.5 line: slope %.3f int %.3f d0 %.3f; E(10) %.2f pJ/B -> DRAM ratio full path %.2f; exit hops %.2f' % (s, i, e0, i+10*s, dram/(i+10*s), (i-e0)/s))
for pre in ('wu/p0.5/hop', 'wu/p0/hop', 'wu/p1/hop'):
    s, i, e0 = line(pre, 'noc_pj_per_byte'); print('  NoC exit hops', pre, round((i-e0)/s, 2))
print('fadd lane %.2f pJ; 32-bit operand one hop NoC %.2f board %.2f; board ratio %.2f; hop fraction worth one fadd lane (board) %.2f' % (X['fadd_ps_random_pj']/8, 32*HN['random_bit_total']['mean']*L/1000, 32*HB['random_bit_total']['mean']*L/1000, 32*HB['random_bit_total']['mean']*L/1000/(X['fadd_ps_random_pj']/8), (X['fadd_ps_random_pj']/8)/(32*HB['random_bit_total']['mean']*L/1000)))
print('hop / own scratchpad: %.2f - %.2f (own scp %.2f; this experiment d=0 wu board %.2f)' % (perB/X['own_scratchpad_pj_per_byte'], perBb/X['own_scratchpad_pj_per_byte'], X['own_scratchpad_pj_per_byte'], C['wu/p0.5/hop0']['pj_per_byte']['mean']))
A = W['axes']
xa, ya = A['x/noc_pj_per_byte/random_bit_fj_per_bit_hop_d1_3'], A['y/noc_pj_per_byte/random_bit_fj_per_bit_hop_d1_3']
print('axis NoC x %.1f (af3 %.1f) y %.1f (af3 only) -> pooled diff %.1f%%, af3 same-card diff %.1f%%' % (xa['mean'], xa['per_card']['aifoundry3']['mean'], ya['mean'], 100*(ya['mean']/xa['mean']-1), 100*(ya['mean']/xa['per_card']['aifoundry3']['mean']-1)))
xb, yb = A['x/pj_per_byte/random_bit_fj_per_bit_hop_d1_3'], A['y/pj_per_byte/random_bit_fj_per_bit_hop_d1_3']
print('axis board af3 x %.1f y %.1f diff %.1f%%' % (xb['per_card']['aifoundry3']['mean'], yb['mean'], 100*(yb['mean']/xb['per_card']['aifoundry3']['mean']-1)))
