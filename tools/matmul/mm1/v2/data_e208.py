#!/usr/bin/env python3
"""MM1-v2: E208's measured runs, read from the vendored session data (inputs/e208/, byte for byte the lab's data commits). Desk; numpy only.

E208 is the model session's matmul sweep 1116-mmsweep (rgm136 unchanged, kernel ELF aace138c...), registered by its post (#10, 18:25:03 PST
Mon 16 Nov 2026), run by the model session on aifoundry2 card 0 (under its governor), aifoundry1 card 1 (600 MHz) and aifoundry1 card 0 (under
its governor, low power only) and committed by the lab (Q200's data-e208). Every figure here is the registered reducer's (reduce_mms.py,
b9e32618...), read from its per-session output data-e208-<session>.json:
  - the run's primary view (win on the governed cards: the 800 MHz launches 1.0-3.5 s into each process; band600 on card 1);
  - time: cycles an op, the slowest minion (cyc_op_max, the wall basis) and the counter's mean (cyc_op_mean), the view's kernel clock
    (kclock_mhz = cycles max / wall, launch by launch), the op time T_op_us (wall basis) and the seconds a GEMM (t_pass_s; a pass is one GEMM);
  - energy: power over idle dP_w by the registered primary baseline (line in burst, bracket in sus3), the board mean p_mean_w, the rest
    p_mean_w - dP_w, J over idle a GEMM (J_pass_over = dP x t_pass), J with the card at rest (J_pass_with = board mean x t_pass); a capped run
    (governed cards: under 80% of the launches after 1.0 s in the 800 MHz band) and a 'time' run carry no energy (the reducer's rule);
  - the minion volts from the view's minion rail (rails.minion.mV), the die at the run's start (the rest's last 5 s), in the view and at most.
Null runs are left out. Kinds: rnd -> random (the host's generator), zeros and ones (a repeated tile). Masks: the run's 'shires'.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.join(HERE, 'inputs', 'e208')
CARDS = {'a2c0': 'aifoundry2 card 0', 'a1c1': 'aifoundry1 card 1', 'a1c0': 'aifoundry1 card 0'}
KIND = {'rnd': 'random', 'zeros': 'zeros', 'ones': 'ones'}


def sessions():
    out = []
    for p in sorted(glob.glob(os.path.join(INP, '*__data-e208-*.json'))):
        sess = os.path.basename(p).split('__')[0]
        out.append((sess, p))
    return out


def footprint(MB, NB, KB):
    return 2.0 * MB * KB + NB * KB + 2.0 * MB * NB


def shape_class(MB, NB, KB, fmt):
    F = footprint(MB, NB, KB)
    if KB == 1:
        return 'one K block'
    if F <= 32.0:
        return 'inside the L3 (<= 32 MB)'
    if F <= 48.0:
        return 'the knee (32-48 MB)'
    return 'past the L3 (> 48 MB)'


def sched_est():
    """the schedules' planning estimates (est_peak_w, est_s) by (session, run index): registered planning figures, not forecasts"""
    out = {}
    for p in glob.glob(os.path.join(INP, 'src__sched__*.json')):
        s = json.load(open(p))
        sess = os.path.basename(p)[len('src__sched__'):-5]
        for r in s['runs']:
            out[(sess, r['i'])] = {'est_peak_w': r.get('est_peak_w'), 'est_s': r.get('est_s'), 'unit': r.get('unit')}
    return out


def arms_meta():
    a = json.load(open(os.path.join(INP, 'src__arms.json')))
    return {x['id']: x for x in a['arms']}


def runs(include_null=False):
    """one record a run of every committed session (null runs left out unless asked)"""
    est = sched_est()
    meta = arms_meta()
    out = []
    for sess, path in sessions():
        D = json.load(open(path))
        ck = sess.split('-')[0]
        card = CARDS[ck]
        for r in D['runs']:
            if r['role'] == 'null' and not include_null:
                continue
            arm = r['arm']
            m = re.fullmatch(r'(\d+)x(\d+)x(\d+)-(fp32|fp16|int8)-(rnd|zeros|ones)(?:-s(\d+))?', arm)
            if not m:
                continue
            MB, NB, KB = int(m.group(1)), int(m.group(2)), int(m.group(3))
            fmt, kind = m.group(4), KIND[m.group(5)]
            mask = r['shires']
            nsh = bin(int(mask, 16)).count('1')
            pv = r.get('primary_view')
            v = r['views'].get(pv) or {}
            rec = {'id': f"E208|{sess}|{r['run']}", 'exp': 'E208', 'session': sess, 'card': card, 'card_key': ck, 'i': r['i'], 'run': r['run'],
                   'arm_e208': arm, 'role': r['role'], 'form': r['form'], 'block': r.get('block'), 'fmt': fmt, 'kind': kind, 'mask': mask,
                   'shires': nsh, 'minions': int(r.get('minions') or 32 * nsh), 'MB': MB, 'NB': NB, 'KB': KB, 'arm': f'gemmL{MB}x{NB}x{KB}',
                   'ops': 64 * MB * NB * KB, 'footprint_MB': footprint(MB, NB, KB), 'shape_class': shape_class(MB, NB, KB, fmt),
                   'families': (meta.get(arm) or {}).get('families'), 'case': f'gemmL{MB}x{NB}x{KB}|{fmt}|{kind}|{mask}',
                   'view': pv, 'capped': bool(r.get('capped')), 'flags': r.get('flags') or [], 'checks': r.get('checks'),
                   'frac_800': r.get('frac_800'), 'frac_800_after_step': r.get('frac_800_after_step'), 'die_start_c': r.get('die_start_c'),
                   'p_rest_plain_w': r.get('p_rest_plain_w'), 'est': est.get((sess, r['i']), {})}
            if v.get('T_op_us') and v.get('cyc_op_max') and v.get('n_launch', 0) >= 1:
                rec.update({'f': float(v['kclock_mhz']), 'T': float(v['T_op_us']), 'cyc_wall': float(v['cyc_op_max']), 'cyc_mean': float(v['cyc_op_mean']),
                            't_gemm': float(v['t_pass_s']), 'n_launch_view': v.get('n_launch')})
            if v.get('dP_w') is not None and v.get('p_mean_w') and not r.get('capped') and r['role'] != 'time':
                mv = ((v.get('rails') or {}).get('minion') or {}).get('mV')
                rec.update({'w': float(v['dP_w']), 'w_corr': v.get('dP_corr_w'), 'p_mean': float(v['p_mean_w']), 'p_rest': float(v['p_mean_w']) - float(v['dP_w']),
                            'J_over': float(v['J_pass_over']), 'J_rest': float(v['J_pass_with']), 'V_mv': (float(mv) if mv is not None else None),
                            'die_win_c': v.get('die_win_c'), 'die_max_c': v.get('die_max_c'), 'baseline_rule': v.get('baseline_rule'),
                            'w_other': {k: v.get(k) for k in ('dP_line', 'dP_plain', 'dP_bracket')}})
            b = r['views'].get('burst') or {}
            rec['burst'] = {'kclock_mhz': b.get('kclock_mhz'), 'clock_hist_10mhz': b.get('clock_hist_10mhz'), 'p_mean_w': b.get('p_mean_w'),
                            'die_max_c': b.get('die_max_c'), 'launches': [{k: L.get(k) for k in ('kclock_mhz', 'board_w', 'wall_s', 'proc', 'launch', 't_start_ms', 't_end_ms')}
                                                                          for L in (b.get('launches') or [])],
                            'T_op_us': b.get('T_op_us'), 'cyc_op_max': b.get('cyc_op_max')}
            out.append(rec)
    return out


def telemetry(sess):
    """aifoundry2's 10 Hz samples of a session (vendored telemetry.jsonl.gz): t_ms, board W, minion MHz, minion mV, the shires' mean die C
    (temp_c.minshire[0]) and its hottest sensor (temp_c.minshire[2])"""
    p = os.path.join(INP, f'{sess}__telemetry.jsonl.gz')
    out = []
    with gzip.open(p, 'rt') as fh:
        for ln in fh:
            try:
                s = json.loads(ln)
            except ValueError:
                continue
            ms = (s.get('temp_c') or {}).get('minshire') or [None, None, None]
            out.append({'t_ms': s.get('t_ms'), 'board_w': s.get('board_w'), 'mhz': (s.get('mhz') or {}).get('minion'),
                        'mv': (s.get('die_mv') or {}).get('minion'), 'die_c': ms[0], 'hot_c': ms[2], 'took_ms': s.get('took_ms')})
    return out


if __name__ == '__main__':
    import collections
    R = runs()
    print('runs', len(R), collections.Counter(r['session'] for r in R))
    print('with time', sum('T' in r for r in R), 'with energy', sum('w' in r for r in R))
    print(collections.Counter((r['card_key'], r['kind'], r['fmt']) for r in R if 'w' in r))
