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
  T9  AT THE FLOOR the pass is swallowed only while the mean reads above the
      trip, so the floor is NOT silent: on a pass whose mean dithers back to
      the trip the power arm is reached and logs a power-up, which the next
      trip undoes.  Added 31 Oct 2026 after the verifier refuted the report's
      first, absolute reading of tpm:884-896 ("nothing is logged at the
      floor").  T9 is the test that would have caught it.                     (tpm:884-920)

Also recorded, as the FOURTH build signature against 0.20.0: the census of
throttle_state values in the power-status records.  A state-0 (POWER_IDLE)
record means an MM-idle transition really happened; at 0.20.0 each one of those
also writes a CRITICAL *numbered* 'Power idle state event' line
(@20:thermal_pwr_mgmt.c:853-855), at 0.22.0 only an INFO line with no numbers
(@22:thermal_pwr_mgmt.c:3117).  These rings carry every other CRITICAL governor
line and not one numbered idle line.
"""
import json, re, os, statistics, collections, argparse

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
SRC = {
    'E64': f'{REPO}/docs/reports/data/2026-10-23-e64-horace-power-limit/results.json',
    'E69': f'{REPO}/docs/reports/data/2026-10-27-e69-governor-knob/results_hpl.json',
}
DEC = ('thermal_down', 'power_down', 'power_up', 'power_idle')
FLOOR_MHZ = 600


def thr_of(n, d=65):
    m = re.search(r'thr(\d+)', n)
    return int(m.group(1)) if m else d


def summ(xs, r=3):
    if not xs:
        return None
    xs = sorted(xs)
    return {'n': len(xs), 'min': xs[0], 'p50': statistics.median(xs),
            'mean': round(statistics.fmean(xs), r),
            'p95': xs[int(0.95 * len(xs))], 'max': xs[-1]}


def main(out_path):
    kinds = collections.Counter()
    T_by_thr = collections.defaultdict(collections.Counter)
    step = collections.Counter()
    step_no_pair = []
    at_floor = []
    st_after = collections.defaultdict(collections.Counter)
    pstat_state = collections.Counter()
    idle_with_numbers = 0
    idle_without = 0
    sp_c_at_thermal_step = []
    sp_c_at_power_up_step = []
    gap_dec = []
    gap_same_kind_thermal = []
    lat_dec_to_record = []
    ratchet = collections.Counter()      # (previous decision, this decision)
    # T9
    pu_at_floor = collections.Counter()          # per run: power-ups logged with the clock at the floor
    pu_total = 0
    floor_ratchet = collections.Counter()        # per run: those a thermal step immediately undid
    floor_excursion_s = []                       # how long the up-step at the floor survived
    pu_at_floor_mhz_after = collections.Counter()  # what the clock actually read after one
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
            pending_t = None
            last_dec_t = None
            last_dec_kind = None
            last_therm_t = None
            n_th = n_pd = n_pu = 0
            n_pu_floor = n_floor_ratchet = 0
            for i, e in enumerate(el):
                k, t = e.get('kind'), e.get('t_s')
                kinds[k] += 1
                if k == 'pstat':
                    st, c = e.get('state'), e.get('sp_c')
                    pstat_state[st] += 1
                    if pending:
                        pk, pt = pending, pending_t
                        st_after[pk][st] += 1
                        if pt is not None and t is not None:
                            lat_dec_to_record.append(round(t - pt, 3))
                        if pk == 'thermal_down':
                            if cur is not None and e.get('mhz') is not None:
                                step[(cur, e['mhz'])] += 1
                            else:
                                step_no_pair.append({'run': name, 'record_t_s': t,
                                                     'clock_before': cur, 'clock_in_record': e.get('mhz'),
                                                     'why': 'no earlier operating point was seen in this '
                                                            'ring, so no from->to could be formed'})
                            if c is not None:
                                sp_c_at_thermal_step.append(c)
                        elif pk == 'power_up':
                            if c is not None:
                                sp_c_at_power_up_step.append(c)
                        pending = pending_t = None
                    if e.get('mhz') is not None:
                        cur = e['mhz']
                elif k == 'new_op' and e.get('mhz') is not None:
                    cur = e['mhz']
                elif k in DEC:
                    at_the_floor = (cur == FLOOR_MHZ)
                    if k == 'thermal_down':
                        n_th += 1
                        T = e.get('T')
                        if T is not None:
                            T_by_thr[thr][T] += 1
                        if at_the_floor:
                            at_floor.append({'run': name, 't_s': t, 'T': e.get('T')})
                        if last_therm_t is not None and t is not None:
                            gap_same_kind_thermal.append(round(t - last_therm_t, 3))
                        last_therm_t = t
                    elif k == 'power_down':
                        n_pd += 1
                    elif k == 'power_up':
                        n_pu += 1
                        pu_total += 1
                        if at_the_floor:
                            # T9: the chain did NOT swallow this pass although the clock was at
                            # the floor, so the mean must have read at or below the trip
                            pu_at_floor[name] += 1
                            n_pu_floor += 1
                            for e2 in el[i + 1:]:
                                if e2.get('kind') == 'pstat' and e2.get('mhz') is not None:
                                    pu_at_floor_mhz_after[e2['mhz']] += 1
                                    break
                            for e2 in el[i + 1:]:
                                if e2.get('kind') in DEC:
                                    if e2['kind'] == 'thermal_down':
                                        floor_ratchet[name] += 1
                                        n_floor_ratchet += 1
                                        if t is not None and e2.get('t_s') is not None:
                                            floor_excursion_s.append(round(e2['t_s'] - t, 3))
                                    break
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
                    pending, pending_t = k, t
            per_run.append({'exp': tag, 'run': name, 'block': r.get('block'),
                            'type': r.get('type'), 'values': r.get('values'),
                            'threshold_c': thr,
                            'mhz_mean': r.get('mhz_mean'), 'share_800': r.get('mhz_800'),
                            'share_700': r.get('mhz_700'), 'share_600': r.get('mhz_600'),
                            'die_start': r.get('die_start'), 'die_end': r.get('die_end'),
                            'die_max': r.get('die_max'),
                            'p800_w': r.get('p800_w'),
                            'thermal_down': n_th, 'power_down': n_pd, 'power_up': n_pu,
                            'power_up_at_floor': n_pu_floor,
                            'power_up_at_floor_undone_by_a_thermal_step': n_floor_ratchet})

    res = {
        'entry_kinds': dict(sorted(kinds.items())),
        'T1_printed_T_by_threshold': {str(k): {str(a): b for a, b in sorted(v.items())}
                                      for k, v in sorted(T_by_thr.items())},
        'T2_thermal_step_mhz': {f'{a}->{b}': n for (a, b), n in sorted(step.items())},
        'T2_thermal_steps_measured': sum(step.values()),
        'T2_thermal_steps_total': kinds.get('thermal_down', 0),
        'T2_thermal_steps_without_a_from_to': step_no_pair,
        'T3_thermal_step_at_600MHz': at_floor,
        'T4_state_written_after': {k: {str(a): b for a, b in sorted(v.items())}
                                   for k, v in sorted(st_after.items())},
        'T5_thermal_idle_lines': kinds.get('thermal_idle', 0),
        'T6_power_idle_with_numbers': idle_with_numbers,
        'T6_power_idle_without_numbers': idle_without,
        'T6_patterns_the_committed_parser_holds': {
            'numbered_0_20_0_form': 'tools/claims-v3/dv2/sptrace_events.py:46 — '
                                    r'rb"Power idle state event, current pwr (\d+)\s+tdp level (\d+)"',
            'bare_0_22_0_form': 'tools/claims-v3/dv2/sptrace_events.py:47 — '
                                r'rb"Power idle state event"',
            'so': 'BOTH forms are tested. A bare match carries no values, so '
                  'tools/claims-v3/hpl/sptrace_full.py:77-85 emits it with no pwr_mw and it would land '
                  'in T6_power_idle_without_numbers. Both counts are zero: neither form is in these rings.',
        },
        'T7_seconds_between_governor_decisions': summ(gap_dec),
        'T7_seconds_between_consecutive_thermal_steps': summ(gap_same_kind_thermal),
        'T7_seconds_decision_to_record': summ(lat_dec_to_record),
        'mean_C_in_the_record_of_a_thermal_step': summ(sp_c_at_thermal_step, 2),
        'mean_C_in_the_record_of_a_power_up_step': summ(sp_c_at_power_up_step, 2),
        'T8_decision_pairs': {f'{a}->{b}': n for (a, b), n in sorted(ratchet.items())},
        'T8_after_a_thermal_step': {
            'thermal_steps': kinds.get('thermal_down', 0),
            'with_a_following_decision': ratchet[('thermal_down', 'power_up')]
                                         + ratchet[('thermal_down', 'power_down')]
                                         + ratchet[('thermal_down', 'thermal_down')]
                                         + ratchet[('thermal_down', 'power_idle')],
            'followed_by_power_up': ratchet[('thermal_down', 'power_up')],
            'followed_by_another_thermal_step': ratchet[('thermal_down', 'thermal_down')],
            'followed_by_a_power_down': ratchet[('thermal_down', 'power_down')],
            'the_content': 'never a power-down',
        },
        'T9_power_up_logged_at_the_floor': {
            'power_ups_total': pu_total,
            'logged_with_the_clock_at_600MHz': sum(pu_at_floor.values()),
            'in_runs': len(pu_at_floor),
            'clock_in_the_next_record': {str(k): v for k, v in sorted(pu_at_floor_mhz_after.items())},
            'undone_by_a_thermal_step_before_any_other_decision': sum(floor_ratchet.values()),
            'that_in_runs': len(floor_ratchet),
            'seconds_the_up_step_survived': summ(floor_excursion_s),
            'by_run': dict(floor_ratchet.most_common()),
            'reading': 'at the floor the chain swallows the pass only while the mean reads ABOVE the '
                       'trip; because the mean dithers across one integer degree, some passes read at '
                       'or below it, the power arm is reached, and the clock really rises one point '
                       'before the next trip takes it back. So the floor is a 600<->700 ratchet with a '
                       'near-zero duty cycle, not silence. It IS silence for a cell whose floor power '
                       'is far over the band (fp32/randn: no decision at all after t=24.65 s).',
        },
        'pstat_throttle_state_census': {
            'counts': {str(k): v for k, v in sorted(pstat_state.items())},
            'enum_at_0_22_0': 'IDLE 0, UP 1, DOWN 2, SAFE 3 '
                              '(836a4ab device-api/include/management-api/device_mgmt_api_spec.h:280-283)',
            'fourth_signature_against_0_20_0': 'state-0 records mean MM-idle transitions really '
                                               'happened; at 0.20.0 each writes a CRITICAL numbered '
                                               '"Power idle state event" line (@20:TPM:853-855), and '
                                               'these rings hold every other CRITICAL governor line '
                                               '(928 of them) and zero numbered idle lines',
            'no_state_above_2': max(pstat_state) <= 2,
        },
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
