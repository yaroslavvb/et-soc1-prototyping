#!/usr/bin/env python3
"""E210 (Q202) desk: each kind's counted transistor switches a multiply-add at each shape, in MM1-v1's units, from the bench's raw counts.

MM1-v1's switch definition (README section 7; its counted class as its predictor computes it from inputs/switch_table.json, design C's
switch_table.py): one switch is one fin charged or discharged by a net transition; the counted class is the vector unit's nets at gate level
(the multiply-add unit at gate level, the rest of the VPU by the same gate/RTL ratio) plus its clock nets:
    fin edges a MAC = (VPU nets_map x k_sig + clock-net toggles x k_clk) / 4,096,
    k_sig = g x 14.5 fins a signal-net toggle, g the gate toggles an RTL toggle (zero delay = the low column, timed = the high column),
    k_clk = 39.8 fins a clock-net toggle.
The three constants are read off MM1-v1's frozen table itself (its fp32 randn row: fin_edges_per_op over rtl_vpu_net_toggles and
clock_net_toggles), so the definition is MM1-v1's to the last digit. The counts are the bench's at a GEMM's accumulator states (count_e210.py).
Also written: the multiply-add unit's nets_hier a MAC (the figure the fma_toggle README asks to quote), valid lane slots, clocked register bits.

    /usr/bin/python3 -I -B switch_counts_e210.py <lab top> <counts S1 json> <counts S2 json> <out json> <out txt> [<calib json>]
The optional calib json (run_kinds.py at the harness's own launch points, counts_e210.sh step 3) is compared with the committed counts-v2.json
(docs/reports/data/2026-11-01-q132-rtl-bench, the counts MM1-v1's table was made from): this build over the committed, per kind and count.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

MACS = 4096
ORDER = ['negzero', 'signs', 'lowmant8', 'highmant8', 'bhalfeq', 'badjeq', 'hd4', 'maxalte', 'arow50', 'randn', 'zeros', 'ones', 'sparse50', 'real']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    top, c1, c2, oj, ot = sys.argv[1:6]
    stp = os.path.join(top, 'tools/matmul/mm1/v1/inputs/switch_table.json')
    st = json.load(open(stp))['rows']['fp32.randn']
    k_lo = st['fin_edges_per_op']['signal_lo_zero_delay'] / st['rtl_vpu_net_toggles']
    k_hi = st['fin_edges_per_op']['signal_hi_timed'] / st['rtl_vpu_net_toggles']
    k_clk = st['fin_edges_per_op']['clock'] / st['clock_net_toggles']
    out = {'what': 'E210 desk switch counts (MM1-v1 units) at GEMM accumulator states; desk inputs, not measurements',
           'definition': 'fin edges a MAC = (VPU nets_map x k_sig + clock-net toggles x k_clk) / 4096; k from MM1-v1 inputs/switch_table.json fp32.randn',
           'k_sig_lo': k_lo, 'k_sig_hi': k_hi, 'k_clk': k_clk, 'python': sys.version.split()[0],
           'inputs_sha256': {'tools/matmul/mm1/v1/inputs/switch_table.json': sha(stp), os.path.basename(c1): sha(c1), os.path.basename(c2): sha(c2)},
           'shapes': {}}
    lines = ['E210 desk switch counts a multiply-add (MM1-v1 units; the bench at GEMM accumulator states; desk)',
             f'k_sig lo {k_lo:.4f}, hi {k_hi:.4f} fin edges a VPU net toggle; k_clk {k_clk:.4f} a clock-net toggle (MM1-v1 switch_table.json)', '']
    for sname, cp in (('S1', c1), ('S2', c2)):
        cj = json.load(open(cp))
        if cj.get('incomplete'):
            print(f'REFUSED: {cp} is incomplete: {cj["incomplete"]}')
            sys.exit(6)
        rows = cj['rows']
        get = lambda k: rows.get(k) or rows.get('fp32.' + k)  # noqa: E731
        rr = {}
        r0 = get('randn')['mean']
        for k in ORDER:
            r = get(k)
            if r is None:
                continue
            m = r['mean']
            vpu = m['vpu']['nets_map'] / MACS
            clk = m['clock_nets_cov'] / MACS
            sig_lo, sig_hi, c = vpu * k_lo, vpu * k_hi, clk * k_clk
            pts = r['points']
            rr[k] = {'n_points': len(pts), 'check_mismatch_max': max(p['check_mismatch'] for p in pts),
                     'fin_edges_lo': sig_lo + c, 'fin_edges_hi': sig_hi + c, 'signal_lo': sig_lo, 'signal_hi': sig_hi, 'clock': c,
                     'vpu_nets_map': vpu, 'clock_nets': clk, 'unit_nets_hier': m['unit']['nets_hier'] / MACS,
                     'unit_nets_map': m['unit']['nets_map'] / MACS, 'valid_slots': m['valid_slots'] / MACS,
                     'clocked_bits': m['ff']['all']['clocked'] / MACS,
                     'vpu_nets_map_min_max': [min(p['vpu']['nets_map'] for p in pts) / MACS, max(p['vpu']['nets_map'] for p in pts) / MACS]}
        rnd = rr['randn']
        for k, v in rr.items():
            v['minus_randn_lo'] = v['fin_edges_lo'] - rnd['fin_edges_lo']
            v['minus_randn_hi'] = v['fin_edges_hi'] - rnd['fin_edges_hi']
        out['shapes'][sname] = rr
        lines.append(f'{sname}: kind, points, check mismatches, fin edges lo / hi, minus random (lo), signal lo, clock, VPU nets_map, unit nets_hier, valid, clocked bits')
        for k, v in rr.items():
            lines.append(f"  {k:10s} {v['n_points']:2d} {v['check_mismatch_max']:3d} {v['fin_edges_lo']:9,.0f} / {v['fin_edges_hi']:9,.0f} {v['minus_randn_lo']:+9,.0f} "
                         f"{v['signal_lo']:9,.0f} {v['clock']:7,.0f} {v['vpu_nets_map']:8.1f} {v['unit_nets_hier']:8.1f} {v['valid_slots']:5.3f} {v['clocked_bits']:7.1f}")
        lines.append('')
    if len(sys.argv) > 6:
        cp = sys.argv[6]
        c2p = os.path.join(top, 'docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json')
        ours, comm = json.load(open(cp))['rows'], json.load(open(c2p))['rows']
        out['inputs_sha256'][os.path.basename(cp)] = sha(cp)
        out['inputs_sha256']['docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json'] = sha(c2p)
        cal = {}
        lines.append('this build at the harness launch points against the committed counts-v2.json (ours / committed, a MAC):')
        for key in ('fp32.randn', 'fp32.zeros', 'fp32.ones', 'fp32.sparse50'):
            if key not in ours or key not in comm:
                continue
            a, b = ours[key]['mean'], comm[key]['mean']
            d = {}
            for nm, fa, fb in (('unit_nets_hier', a['unit']['nets_hier'], b['unit']['nets_hier']), ('unit_nets_map', a['unit']['nets_map'], b['unit']['nets_map']),
                               ('vpu_nets_map', a['vpu']['nets_map'], b['vpu']['nets_map']), ('clock_nets', a['clock_nets_cov'], b['clock_nets_cov']),
                               ('clocked_bits', a['ff']['all']['clocked'], b['ff']['all']['clocked'])):
                d[nm] = {'ours': fa / MACS, 'committed': fb / MACS, 'ratio': (fa / fb) if fb else None}
            d['check_mismatch_ours'] = a['check_mismatch']
            cal[key] = d
            lines.append(f"  {key:14s} " + ', '.join(f"{nm} {v['ours']:.1f} / {v['committed']:.1f}" + (f" ({v['ratio']:.4f})" if v['ratio'] else '')
                                                    for nm, v in d.items() if isinstance(v, dict)) + f"; check mismatches {d['check_mismatch_ours']:.0f}")
        out['build_against_committed_counts_v2'] = cal
        lines.append('')
    json.dump(out, open(oj, 'w'), indent=1, sort_keys=True)
    open(ot, 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
