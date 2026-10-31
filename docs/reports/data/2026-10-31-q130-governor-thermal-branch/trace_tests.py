#!/usr/bin/env python3
"""Q130(d) — the BL2 0.22.0 thermal branch, tested against the committed E64/E69
service-processor rings on aifoundry2.  Read-only; writes one JSON.

Predicates (each one a line of the 0.22.0 source, listed in the README):
  T1  the printed temperature at a thermal step is never <= the threshold      (tpm:884, strict >)
  T2  a thermal step is exactly one VMIN point                                (tpm:1888-1906 + flashfs:2384-2399)
  T3  no thermal step is ever taken at the VMIN floor                         (tpm:886 guard)
  T4  a thermal step writes throttle_state 2 (POWER_DOWN), never a 4+         (tpm:894 + api spec:280-283)
  T5  no 'Thermal idle state event' line exists                               (0.22.0 has no thermal loop)
  T6  'Power idle state event' carries no numbers                             (tpm:3117, INFO, no args)
  T7  the step rate is bounded by the DM pass                                 (dm_task.c:267,275)
  T8  the ratchet: thermal gives one point back per trip, power takes them
      back one point per pass, so the sustained clock is a duty cycle
"""
import json, re, os, statistics, collections, argparse

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
SRC = {
    'E64': f'{REPO}/docs/reports/data/2026-10-23-e64-horace-power-limit/results.json',
    'E69': f'{REPO}/docs/reports/data/2026-10-27-e69-governor-knob/results_hpl.json',
}
DEC = ('thermal_down', 'power_down', 'power_up', 'power_idle')


def thr_of(n, d=65):
    m = re.search(r'thr(\d+)', n)
    return int(m.group(1)) if m else d


def summ(xs, r=3):
    if not xs:
        return None
    xs = sorted(xs)
    return {'n': len(xs), 'min': xs[0], 'p50': statistics.median(xs),
            'mean': round(statistics.fmean(xs), r), 'max': xs[-1]}


def main(out_path):
    kinds = collections.Counter()
    T_by_thr = collections.defaultdict(collections.Counter)
    step = collections.Counter()
    at_floor = []
    st_after = collections.defaultdict(collections.Counter)
    idle_with_numbers = 0
    idle_without = 0
    sp_c_at_thermal_step = []
    sp_c_at_power_up_step = []
    gap_dec = []
    gap_same_kind_thermal = []
    ratchet = collections.Counter()      # (previous decision, this decision)
    per_run = []

    for tag in ('E64', 'E69'):
        for r in json.load(open(SRC[tag]))['runs']:
            name = r.get('run', '')
            thr = thr_of(name)
            el = r.get('event_list') or []
            if not el:
                continue
            cur = None
            pending = None
            last_dec_t = None
            last_dec_kind = None
            last_therm_t = None
            n_th = n_pd = n_pu = 0
            for e in el:
                k, t = e.get('kind'), e.get('t_s')
                kinds[k] += 1
                if k == 'pstat':
                    st, c = e.get('state'), e.get('sp_c')
                    if pending:
                        pk, pt = pending
                        st_after[pk][st] += 1
                        if pk == 'thermal_down':
                            if cur is not None and e.get('mhz') is not None:
                                step[(cur, e['mhz'])] += 1
                            if c is not None:
                                sp_c_at_thermal_step.append(c)
                        elif pk == 'power_up' and c is not None:
                            sp_c_at_power_up_step.append(c)
                        pending = None
                    if e.get('mhz') is not None:
                        cur = e['mhz']
                elif k == 'new_op' and e.get('mhz') is not None:
                    cur = e['mhz']
                elif k in DEC:
                    if k == 'thermal_down':
                        n_th += 1
                        T = e.get('T')
                        if T is not None:
                            T_by_thr[thr][T] += 1
                        if cur == 600:
                            at_floor.append({'run': name, 't_s': t, 'T': e.get('T')})
                        if last_therm_t is not None and t is not None:
                            gap_same_kind_thermal.append(round(t - last_therm_t, 3))
                        last_therm_t = t
                    elif k == 'power_down':
                        n_pd += 1
                    elif k == 'power_up':
                        n_pu += 1
                    elif k == 'power_idle':
                        if e.get('pwr_mw') is None:
                            idle_without += 1
                        else:
                            idle_with_numbers += 1
                    if last_dec_t is not None and t is not None:
                        gap_dec.append(round(t - last_dec_t, 3))
                    if last_dec_kind:
                        ratchet[(last_dec_kind, k)] += 1
                    last_dec_t, last_dec_kind = t, k
                    pending = (k, t)
            per_run.append({'exp': tag, 'run': name, 'block': r.get('block'),
                            'type': r.get('type'), 'values': r.get('values'),
                            'threshold_c': thr,
                            'mhz_mean': r.get('mhz_mean'), 'share_800': r.get('mhz_800'),
                            'share_700': r.get('mhz_700'), 'share_600': r.get('mhz_600'),
                            'die_start': r.get('die_start'), 'die_max': r.get('die_max'),
                            'p800_w': r.get('p800_w'),
                            'thermal_down': n_th, 'power_down': n_pd, 'power_up': n_pu})

    res = {
        'entry_kinds': dict(sorted(kinds.items())),
        'T1_printed_T_by_threshold': {str(k): {str(a): b for a, b in sorted(v.items())}
                                      for k, v in sorted(T_by_thr.items())},
        'T2_thermal_step_mhz': {f'{a}->{b}': n for (a, b), n in sorted(step.items())},
        'T3_thermal_step_at_600MHz': at_floor,
        'T4_state_written_after': {k: {str(a): b for a, b in sorted(v.items())}
                                   for k, v in sorted(st_after.items())},
        'T5_thermal_idle_lines': kinds.get('thermal_idle', 0),
        'T6_power_idle_with_numbers': idle_with_numbers,
        'T6_power_idle_without_numbers': idle_without,
        'T7_seconds_between_governor_decisions': summ(gap_dec),
        'T7_seconds_between_consecutive_thermal_steps': summ(gap_same_kind_thermal),
        'mean_C_in_the_record_of_a_thermal_step': summ(sp_c_at_thermal_step, 2),
        'mean_C_in_the_record_of_a_power_up_step': summ(sp_c_at_power_up_step, 2),
        'T8_decision_pairs': {f'{a}->{b}': n for (a, b), n in sorted(ratchet.items())},
        'per_run': per_run,
    }
    open(out_path, 'w').write(json.dumps(res, indent=1) + '\n')
    pr = dict(res)
    pr['per_run'] = f'<{len(per_run)} runs, in the file>'
    print(json.dumps(pr, indent=1))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    main(ap.parse_args().out)
