"""What the uncontended headline and derived sentences become if build_wire_report.py uses wsep_d1_4 (same d as wu)."""
import json
B='/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/data/2026-09-24-wire-energy/'
R=json.load(open(B+'report.json')); W=R['wire']; H=R['headline']; s09=R['scaled']['0.9']; s05=R['scaled']['0.5']
L=3.72; Llo,Lhi=3.64,3.76
dj=W['disjoint_flows']
for src,key in (('board','pj_per_byte'),('noc_rail','noc_pj_per_byte')):
    for fam in ('wsep','wsep_d1_4'):
        d_,z_=dj[key][fam]['random_minus_zeros_fj_per_bit_hop'],dj[key][fam]['zeros_fj_per_bit_hop']
        tot=(d_['mean']+z_['mean'])/L
        print(f"{src:8s} {fam:9s} data {d_['mean']/L:5.2f} [{d_['lo']/Lhi:.1f}-{d_['hi']/Llo:.1f}]  fixed {z_['mean']/L:5.2f} [{z_['lo']/Lhi:.1f}-{z_['hi']/Llo:.1f}]  total {tot:5.2f} [{(d_['lo']+z_['lo'])/Lhi:.1f}-{(d_['hi']+z_['hi'])/Llo:.1f}]  data@0.9V {d_['mean']/L*s09:.1f}  per hop data {d_['mean']:.1f} zeros {z_['mean']:.1f}")
HN,HB=H['v2/noc_rail'],H['v2/board']
print('loaded totals NoC %.2f board %.2f; data NoC %.2f board %.2f' % (HN['random_bit_total']['mean'],HB['random_bit_total']['mean'],HN['random_bit_data']['mean'],HB['random_bit_data']['mean']))
for fam in ('wsep','wsep_d1_4'):
    un=(dj['noc_pj_per_byte'][fam]['random_minus_zeros_fj_per_bit_hop']['mean']+dj['noc_pj_per_byte'][fam]['zeros_fj_per_bit_hop']['mean'])/L
    ub=(dj['pj_per_byte'][fam]['random_minus_zeros_fj_per_bit_hop']['mean']+dj['pj_per_byte'][fam]['zeros_fj_per_bit_hop']['mean'])/L
    print(f"{fam}: loaded/free NoC {HN['random_bit_total']['mean']/un:.2f}  board {HB['random_bit_total']['mean']/ub:.2f}")
# like-for-like d=1-4 per-hop random totals
for key in ('noc_pj_per_byte','pj_per_byte'):
    u=dj[key]['wu']['random_fj_per_bit_hop']['mean']; s=dj[key]['wsep_d1_4']['random_fj_per_bit_hop']['mean']; s5=dj[key]['wsep']['random_fj_per_bit_hop']['mean']
    print(f"{key}: wu d1-4 random {u:.1f} / wsep d1-4 {s:.1f} = {u/s:.2f}; / wsep d1-5 {s5:.1f} = {u/s5:.2f}")
print('0.5 V factor %.4f; data at 0.5V: free NoC %.1f loaded NoC %.1f loaded board %.1f; totals %.1f %.1f %.1f' % (s05, 24.56*s05, HN['random_bit_data']['mean']*s05, HB['random_bit_data']['mean']*s05, 36.2*s05, HN['random_bit_total']['mean']*s05, HB['random_bit_total']['mean']*s05))
print('Keckler 121 at 0.485 V = %.1f; mesh rail data free/loaded as fraction: %.2f %.2f' % (121/s09, 24.56/(121/s09), HN['random_bit_data']['mean']/(121/s09)))
# bus inversion numbers (loaded NoC model)
M=W['model']['v2']['noc_rail']; a=M['toggle_fj_per_bit_transition_hop']['mean']; b=M['ones_fj_per_one_bit_hop']['mean']; s0=M['s0_pj_per_byte_hop']['mean']*125
print('loaded NoC per hop: zeros %.1f, random %.1f, all-ones %.1f; zeros/all-ones %.2f zeros/random %.2f' % (s0, s0+0.5*a+0.5*b, s0+b, s0/(s0+b), s0/(s0+0.5*a+0.5*b)))
f=2*a/(2*a+b); print('idle-to-zero reading: f = %.3f, E_t = a/f = %.0f fJ per transition per hop = %.1f fJ per transition-mm, C = 2E/V^2 = %.0f fF/mm' % (f, a/f, a/f/L, 2*(a/f/L)/0.485**2))
# practical
X=R['context']; perB=HN['random_bit_total']['mean']*8*L/1000; perBb=HB['random_bit_total']['mean']*8*L/1000
print('hop pJ/B %.2f-%.2f; 10-hop line %.2f-%.2f nJ; DRAM %.2f nJ; ratios %.1f-%.1f' % (perB, perBb, 0.64*perB*10, 0.64*perBb*10, 0.064*X['dram_read_pj_per_byte'], X['dram_read_pj_per_byte']/(10*perBb), X['dram_read_pj_per_byte']/(10*perB)))
