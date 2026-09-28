#!/usr/bin/env python3
"""Write overheat.json, the data of the page "The effect of overheating" (docs/reports/sources/effect-of-overheating.*).

    python3 docs/reports/data/2026-09-28-overheating/build_overheat_data.py

Run from the repository root after the reductions and the analyses exist:
  reductions/*.json   tools/claims-v3/oh/reduce.py --all (E53's registered verdicts) and extras.py (descriptive)
  analysis/*.json     scripts/*.py over docs/reports/data (the existing record) and scripts/derived.py (arithmetic)
  sources.json        the page's numbered sources
Every ET number on the page comes from this file; the few read from the firmware source are in FW below, each with
its source key. The outside rows of the two ladders (LIMITS, MECH) are the sources' own numbers, each with its key.
The temperature-inversion curves are an ILLUSTRATION (INV below says so and gives the parameters), not a model of
this chip. The build refuses to write when the page cites a source key that sources.json lacks.
"""
import collections
import glob
import gzip
import json
import math
import os
import re
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
DATA = os.path.join(ROOT, 'docs', 'reports', 'data')
BODY = os.path.join(ROOT, 'docs', 'reports', 'sources', 'effect-of-overheating.body.html')
SCRIPT = os.path.join(ROOT, 'docs', 'reports', 'sources', 'effect-of-overheating.script.js')


def J(*p):
    return json.load(open(os.path.join(HERE, *p)))


RED = {k: J('reductions', k + '.json') for k in ('verdicts', 'oh1', 'oh2', 'oh2-aborted', 'oh3', 'extras')}
AN = {k: J('analysis', k + '.json') for k in ('max_temps', 'correct_vs_temp', 'timing_vs_temp', 'hot_minus_mean',
                                              'idle_vs_temp', 'runaway', 'events_vs_temp', 'derived')}
SRC = J('sources.json')['sources']
OHCARDS = ['aifoundry3', 'aifoundry1-c1']
out = {}

# ---------------------------------------------------------------- sources, checked against the page's citations
keys = {s['key'] for s in SRC}
cited = set()
for f in (BODY, SCRIPT):
    if os.path.exists(f):
        for m in re.finditer(r'data-s="([^"$]+)"', open(f).read()):
            cited.update(k.strip() for k in m.group(1).split(','))
        for m in re.finditer(r"cite\('([^']+)'", open(f).read()):
            cited.update(k.strip() for k in m.group(1).split(','))

# ---------------------------------------------------------------- the firmware's numbers (read from source)
dfi = 3616                     # RFSHTMG t_rfc_nom_x1_x32 = 0x71, x32 (et-ddr 4441-4443)
out['fw'] = {'threshold_c': 65, 'acts_at_c': 66, 'sensors': 34, 'sensors_all': 35, 'safe_mhz': 300, 'pmic_c': 75,
             'pmic_w': 75, 'pmic_range_c': [55, 75], 'default_reset_c': 52, 'build': '0.20.0', 'commit': 'ffca4cbb4',
             'refresh_dfi_clocks': dfi, 'ddr_dfi_mhz': 933, 'refresh_us': round(dfi / 933.0, 4),
             'refresh_cycles_600': round(dfi / 933.0 * 600, 1), 'mv_800': 618, 'mv_700': 568, 'mv_600_a2': 517,
             'src': {'threshold_c': 'et-thermal-h', 'sensors': 'et-pvt', 'safe_mhz': 'et-thermal-h', 'pmic_c': 'et-pmic',
                     'refresh_dfi_clocks': 'et-ddr', 'mv_800': 'docs/findings/16-dvfs-and-leakage.md'}}

# each card's firmware build and what its governor does (docs/findings/14-card-behaviour.md, "The clock governor, by
# firmware build" and the card table), and the service processor's own readouts over the three-card check (the DVFS
# page's data: docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json v3.sp_readouts)
out['builds'] = {'aifoundry2': {'release': '1.3.1', 'bl2': '0.20.0', 'governor': 'acts'},
                 'aifoundry3': {'release': '1.3.1', 'bl2': '0.20.0', 'governor': 'latched'},
                 'aifoundry1-c1': {'release': '1.2.0', 'bl2': '0.18.0', 'governor': 'never moves the clock'},
                 'aifoundry1-c0': {'release': '1.4.1', 'bl2': '0.21.2', 'governor': 'acts only while a kernel runs; idles at 300 MHz'},
                 'src': 'docs/findings/14-card-behaviour.md'}
spr = json.load(open(os.path.join(DATA, '2026-09-22-dvfs-aifoundry2', 'dvfs.json')))['v3']['sp_readouts']
out['sp_readouts'] = {c: {k: v[k] for k in ('samples', 'sp_mhz_min', 'sp_mhz_max', 'pmic_temp_nonzero', 'pmic_temp_samples',
                                          'die_mean_max', 'mhz_at_die_mean_max')} for c, v in spr.items()}

# ---------------------------------------------------------------- the highest readings on record, per card
mt = AN['max_temps']
# the highest mean is the larger of the host's readings and the service processor's own maximum of the mean (card 0's
# 119 C is only in the latter, which has not been reset since its September fault)
out['peaks'] = {c: {'mean': max(v['mean']['value'], v['sp_max']['value']), 'high': v['high']['value'], 'io': v['io_hi']['value'],
                    'sp_max': v['sp_max']['value'], 'board_w': v['board_w']['value'], 'samples': v['samples'],
                    'files': v['files'], 'high_file': v['high']['file'], 'mean_file': v['mean']['file']}
                for c, v in mt.items() if c in ('aifoundry2', 'aifoundry3', 'aifoundry1-c1', 'aifoundry1-c0')}
# card 0: the host's own readings are the guard's; its SP statistics stand unreset
g = []
for f in sorted(glob.glob(os.path.join(HERE, 'raw', 'aifoundry1-c1', 'oh', 'p*', 'guard.jsonl.gz'))):
    for line in gzip.open(f, 'rt'):
        try:
            g.append(json.loads(line))
        except ValueError:
            pass
g = [s for s in g if (s.get('temp_c') or {}).get('minshire')]
out['card0'] = {'guard_samples': len(g),
                'mean_range': [min(s['temp_c']['minshire'][0] for s in g), max(s['temp_c']['minshire'][0] for s in g)],
                'board_w_range': [min(s['board_w'] for s in g), max(s['board_w'] for s in g)],
                'board_w_median': round(st.median(s['board_w'] for s in g), 1),
                'mhz': sorted({s['mhz']['minion'] for s in g}),
                'minion_mv': sorted({s['die_mv']['minion'] for s in g}),
                'sp_mean_max': max(s['sp']['minion_c'][2] for s in g),
                'sensor_peak_hold': max(s['temp_c']['minshire'][2] for s in g),
                'io_peak_hold': max(s['temp_c']['ioshire'][2] for s in g),
                'sp_board_max_w': max(s['sp']['board_max_w'] for s in g),
                'system_c': sorted({x for s in g for x in s['sp']['system_c']}),
                'reported_25sep': {'idle_w': [18.6, 18.8], 'hot_c': [115, 117], 'hot_idle_w': [66, 71],
                                   'src': 'docs/findings/14-card-behaviour.md'}}

# ---------------------------------------------------------------- E53 (OH): verdicts, flattened per item and card
V = RED['verdicts']


def agg(words):
    words = [w for w in words if w is not None]
    if not words:
        return None
    if any(w == 'FAIL' for w in words):
        return 'FAIL'
    if any(w == 'INSUFFICIENT' for w in words):
        return 'INSUFFICIENT'
    return 'PASS'


def per_card(item):
    v = V[item]
    if isinstance(v, str):
        return {c: v for c in OHCARDS}
    r = {}
    for c in OHCARDS:
        ws = [w for k, w in v.items() if k == c or k.startswith(c + ' ')]
        r[c] = agg(ws)
    return r


RULES = {
    'OH1-a': ('in every analysed 1 s window, the hottest sensor is at most 4 °C above the mean', 'OH-1'),
    'OH1-b': ('one shire at full load does not widen the gap beyond a central 2 × 2 block (median, per block)', 'OH-1'),
    'OH1-c': ('each load’s median gap is within ±1 °C of idle’s', 'OH-1'),
    'OH2-a': ('no wrong result, tensor error or failed launch among the checked launches, at any temperature', 'OH-2'),
    'OH2-b': ('each kernel’s cycles at a mean of 80–85 °C within 0.1% of rest', 'OH-2'),
    'OH2-c': ('the heater’s implied clock 0.5994–0.5995 GHz in every 5 °C band', 'OH-2'),
    'OH2-d max': ('under the whole-chip heater, the gap at most +4 °C in every band', 'OH-2'),
    'OH2-d growth': ('the gap’s median grows by 0 or +1 °C from 60–70 to 80–85 °C', 'OH-2'),
    'OH2-e': ('the DRAM refresh period stays 2,325.4 ± 0.1 minion cycles when hot', 'OH-2'),
    'OH3-a': ('idle board power within ±1.5 W of the card’s September idle law, per degree', 'OH-3'),
    'OH3-b': ('the refitted leakage doubling interval 17–25 °C', 'OH-3'),
}
rows = []
for item in ('OH1-a', 'OH1-b', 'OH1-c', 'OH2-a', 'OH2-b', 'OH2-c'):
    rows.append({'item': item, 'rule': RULES[item][0], 'exp': RULES[item][1], 'cards': per_card(item)})
d = V['OH2-d']
rows.append({'item': 'OH2-d max', 'rule': RULES['OH2-d max'][0], 'exp': 'OH-2', 'cards': {c: d[c]['max'] for c in OHCARDS}})
rows.append({'item': 'OH2-d growth', 'rule': RULES['OH2-d growth'][0], 'exp': 'OH-2', 'cards': {c: d[c]['growth'] for c in OHCARDS}})
for item in ('OH2-e', 'OH3-a', 'OH3-b'):
    rows.append({'item': item, 'rule': RULES[item][0], 'exp': RULES[item][1], 'cards': per_card(item)})
words = [w for r in rows for w in r['cards'].values()]
out['verdicts'] = {'rows': rows, 'n_registered': sum(w is not None for w in words),
                   'n_pass': sum(w == 'PASS' for w in words), 'n_insufficient': sum(w == 'INSUFFICIENT' for w in words),
                   'n_fail': sum(w == 'FAIL' for w in words), 'n_not_testable': sum(w is None for w in words),
                   'cards': OHCARDS}

# the registration and its amendments (tools/claims-v3/oh/prereg/)
out['prereg'] = {'orig': {'sha': '8d620b64dc60239a104c59e3d9bd8c42cf1b4adb9e482460499dedc836f36661', 'time': '10:11'},
                 'a1': {'sha': '067a32b41014fdc65d0880008d090d022075b812c63e360d8dc831c4222ad22e', 'time': '10:39',
                        'why': 'a bug in the heating loop held the die at its target until the time cap; the first OH-2 attempts were stopped at 10:33'},
                 'a2': {'sha': '1b34d189b5d9eb3d08d245da6dfacf042b255b9e606c9d1054b0e2d0622c7bb1', 'time': '11:06',
                        'why': 'the upper bands were above what the heater reaches within the 150 s chain limit; the second attempts were stopped at 10:59; band heating capped at 300 s, holds at 30 s, and a card that cannot reach a band is held just below the highest mean it reached'}}
cur = open(os.path.join(ROOT, 'tools', 'claims-v3', 'oh', 'prereg', 'PREREG.sha256')).read().split()[0] \
    if os.path.exists(os.path.join(ROOT, 'tools', 'claims-v3', 'oh', 'prereg', 'PREREG.sha256')) else None
out['prereg']['current_file_sha'] = cur

# card time per card: block.json t0..t1 over every block, stopped attempts included
ct = collections.defaultdict(float)
ct_ab = collections.defaultdict(float)
blocks = []
for bj in sorted(glob.glob(os.path.join(HERE, 'raw', '*', 'oh', 'p*', 'block.json'))):
    b = json.load(open(bj))
    card = bj.split('/raw/')[1].split('/')[0]
    t0 = b['t0_ms']
    if t0 is None:  # a stopped attempt, finalised by hand: its first mark
        t0 = min(json.loads(l)['t_ms'] for l in open(os.path.join(os.path.dirname(bj), 'marks.jsonl')) if l.strip())
    mins = (b['t1_ms'] - t0) / 60000
    ct[card] += mins
    if b.get('status') == 'aborted':
        ct_ab[card] += mins
    blocks.append({'card': card, 'dir': os.path.basename(os.path.dirname(bj)), 'status': b.get('status'),
                   'minutes': round(mins, 1), 'die_c_start': b.get('die_c_start'), 'die_c_end': b.get('die_c_end')})
bd = {x['block']: x for x in RED['extras']['blocks_detail']}
for b in blocks:
    x = bd.get('raw/%s/oh/%s' % (b['card'], b['dir'])) or {}
    b.update({k: x.get(k) for k in ('launches', 'mean_max', 'high_max', 'board_max_w')})
out['oh_blocks'] = blocks
out['card_time_min'] = {c: round(ct[c]) for c in OHCARDS}
out['card_time_aborted_min'] = {c: round(ct_ab[c]) for c in OHCARDS}
out['oh_max'] = {c: {'mean': max(b['mean_max'] for b in blocks if b['card'] == c),
                     'high': max(b['high_max'] for b in blocks if b['card'] == c),
                     'board_w': max(b['board_max_w'] for b in blocks if b['card'] == c)} for c in OHCARDS}

# ---------------------------------------------------------------- mean against hottest
o1 = RED['oh1']
o2 = RED['oh2']
ex = RED['extras']
LOADN = {'IDLE': 'idle', 'ONE-C': 'one central shire', 'ONE-NE': 'one shire by the I/O corner', 'B4C': 'central 2 × 2 block'}
gap_load = []
for c in OHCARDS:
    for cond in ('IDLE', 'ONE-C', 'ONE-NE', 'B4C'):
        x = o1['by_card_cond']['%s %s' % (c, cond)]
        gap_load.append({'card': c, 'load': LOADN[cond], 'code': cond, 'n': x['n'], 'median': x['dhot_median'],
                         'max': x['dhot_max'], 'dist': x['dhot_dist'], 'mean_range': x['mean_range'],
                         'board_w': x['board_w_median'], 'src': 'OH-1'})
    # the whole-chip heater (OH-2 windows inside heater launches), pooled over bands
    hs = collections.Counter()
    for k, v in ex['window_gap_by_load'].items():
        cc, load, band = [s.strip() for s in k.split('|')]
        if cc == c and load == 'whole-chip heater':
            hs.update({int(a): b for a, b in v['dist'].items()})
    vals = [g_ for g_, n in hs.items() for _ in range(n)]
    gap_load.append({'card': c, 'load': 'whole-chip heater', 'code': 'HEAT', 'n': sum(hs.values()),
                     'median': st.median(vals), 'max': max(vals), 'dist': {str(k): hs[k] for k in sorted(hs)},
                     'src': 'OH-2'})
gap_temp = []
for k, v in o2['dhot_all_windows'].items():
    c, band = k.split(' ')
    gap_temp.append({'card': c, 'band': band, 'lo': int(band.split('-')[0]), 'n': v['n'], 'median': v['median'],
                     'max': v['max'], 'dist': v['dist']})
gap_temp.sort(key=lambda r: (r['card'], r['lo']))
near = []
for k, v in ex['near_65'].items():
    m = re.match(r'(\S+) mean (\d+)', k)
    near.append({'card': m.group(1), 'mean': int(m.group(2)), 'n': v['n'], 'dist': v['hottest_dist'],
                 'median': v['hottest_median'], 'min': min(int(a) for a in v['hottest_dist']),
                 'max': max(int(a) for a in v['hottest_dist'])})
n4 = {c: sum(v['dist'].get('4', 0) for k, v in o2['dhot_all_windows'].items() if k.startswith(c + ' ')) for c in OHCARDS}
n5 = sum(v['dist'].get(str(x), 0) for v in o2['dhot_all_windows'].values() for x in range(5, 20))
hm = AN['hot_minus_mean']
e52 = [r for r in hm['e52_by_placement'] if r['state'] == 'load']
e51 = collections.defaultdict(list)
for r in hm['e51_runs']:
    e51[r['placement']].append(r['dhot'])
dv = AN['derived']
out['gap'] = {'load': gap_load, 'temp': gap_temp, 'near65': near,
              'n4': n4, 'n4_total': sum(n4.values()), 'n5': n5,
              'oh1_windows': o1['OH1-a']['n'], 'oh1_max': o1['OH1-a']['max_dhot'],
              'near65_windows': sum(r['n'] for r in near if r['mean'] in (65, 66)),
              'near65_windows_all': sum(r['n'] for r in near),
              'e52_load': [{'card': r['card'], 'placement': r['placement'], 'n': r['n'], 'median': r['median'],
                            'max': r['max']} for r in e52],
              'e52_max': max(r['max'] for r in hm['e52_by_placement']),
              'e51': {k: {'n': len(v), 'min': min(v), 'max': max(v)} for k, v in e51.items()},
              'a2_p11': dv['a2_p11'],
              'oh2d': {c: {'max': o2['OH2-d']['cards'][c]['max'], 'growth': o2['OH2-d']['cards'][c]['growth_80_85_minus_60_70'],
                           'bands': o2['OH2-d']['cards'][c]['bands']} for c in OHCARDS}}

# ---------------------------------------------------------------- correctness against temperature
cv = AN['correct_vs_temp']
BIN10 = ['0-60', '60-70', '70-80', '80-90', '90-100', '100-130']


def bin10(lo):
    return '0-60' if lo < 60 else ('100-130' if lo >= 100 else '%d-%d' % (lo // 10 * 10, lo // 10 * 10 + 10))


corr = collections.defaultdict(lambda: {'prior_checked': 0, 'prior_bad': 0, 'prior_launches': 0, 'oh_checked': 0, 'oh_bad': 0})
for r in cv['bins']:
    if r['bin'] == 'no-tel':
        continue
    x = corr[(r['card'], r['bin'])]
    x['prior_checked'] += r['checked']
    x['prior_bad'] += r['wrong'] + (r['tensor_err'] if r['wrong'] == 0 else 0)
    x['prior_launches'] += r['launches']
for src in (o2, RED['oh2-aborted']):
    for k, v in src['by_bin'].items():
        c, band = k.split(' ')
        x = corr[(c, bin10(int(band.split('-')[0])))]
        x['oh_checked'] += v['checked']
        x['oh_bad'] += v['bad']
out['correct'] = {'bins': BIN10,
                  'cells': [{'card': c, 'bin': b, **v} for (c, b), v in sorted(corr.items())],
                  'prior_records': cv['launch_records'], 'prior_bad': cv['bad'],
                  'prior_notel': {r['card']: {'launches': r['launches'], 'checked': r['checked']} for r in cv['bins'] if r['bin'] == 'no-tel'},
                  'prior_hottest': {c: {'mean_c': v['mean_c'], 'kind': v['kind']} for c, v in cv['hottest_checked'].items()},
                  'prior_checked_total': sum(r['checked'] for r in cv['bins']),
                  'oh_hottest': {c: {'mean_c': o2['hottest_checked'][c][0], 'high_c': o2['hottest_checked'][c][1],
                                     'kind': o2['hottest_checked'][c][2]} for c in OHCARDS},
                  'oh_totals': ex['totals'],
                  'oh_checked': sum(v['checked_launches'] for v in ex['totals'].values()),
                  'oh_records': sum(v['checked_records'] for v in ex['totals'].values()),
                  'oh_bad': sum(v['bad'] for v in ex['totals'].values()),
                  'oh_verdict_checked': o2['OH2-a']['checked'], 'oh_aborted_checked': RED['oh2-aborted']['OH2-a']['checked'],
                  'oh_8085': {c: o2['by_bin'].get('%s 80-85' % c) for c in OHCARDS},
                  'events': AN['events_vs_temp']}
out['correct']['prior_launches_telemetry'] = sum(r['launches'] for r in cv['bins'] if r['bin'] != 'no-tel')

# ---------------------------------------------------------------- work per cycle, the clock, droop, refresh
tv = AN['timing_vs_temp']
b_items = o2['OH2-b']['items']
a3b = {k.split(' ', 1)[1]: v for k, v in b_items.items() if k.startswith('aifoundry3 ')}
out['timing'] = {'heater_prior': tv['heater'], 'catalogue': {k: v for k, v in tv['catalogue'].items() if k != 'rows'},
                 'oh2b_a3': a3b, 'oh2b_a3_max_abs': max(abs(v['diff_pct']) for v in a3b.values()),
                 'oh2b_a3_n': len(a3b),
                 'oh2c': {k: v for k, v in o2['OH2-c']['items'].items()},
                 'c1_warm': ex['warm_vs_rest']['aifoundry1-c1'], 'a3_warm': ex['warm_vs_rest']['aifoundry3'],
                 'heater_prior_cpo': [min(r['cycles_per_op_min'] for r in tv['heater']), max(r['cycles_per_op_max'] for r in tv['heater'])],
                 'heater_prior_ghz': [min(r['ghz_median'] for r in tv['heater']), max(r['ghz_median'] for r in tv['heater'])],
                 'heater_prior_range_c': [min(int(r['bin'].split('-')[0]) for r in tv['heater']), max(int(r['bin'].split('-')[1]) for r in tv['heater'])],
                 'heater_prior_cards': sorted({r['card'] for r in tv['heater']})}
out['droop'] = o2['die_mv_by_band']
out['refresh'] = o2['OH2-e']['items']

# ---------------------------------------------------------------- idle power: the September laws (E44) and E53's tails
iv = AN['idle_vs_temp']
o3 = RED['oh3']
idle = {}
for c in ('aifoundry2', 'aifoundry3', 'aifoundry1-c1'):
    x = iv[c]
    f = x['fit']
    T88 = None
    # the die mean at which the idle law plus a full random fp32 matmul (27.2 W) reaches the card's 88 W input
    need = dv['card_input_max_w'] - 27.2 - f['P_fix']
    if need > 0:
        T88 = round(80 + f['T_L'] * math.log(need / f['A']), 1)
    idle[c] = {'e44': {'bins': x['bins'], 'fit': f, 'doubling_range_C': x['doubling_range_C'],
                       'extrapolated_w': x['extrapolated_w'], 'range': [x['bins'][0]['T'], x['bins'][-1]['T']]},
               't_matmul_88w': T88}
    if c in o3:
        y = o3[c]
        idle[c]['oh3'] = {'bins': y['bins'], 'samples': y['samples'], 'a': y['OH3-a'], 'b': y['OH3-b']}
out['idle'] = idle
out['runaway'] = AN['runaway']

# ---------------------------------------------------------------- derived arithmetic (Arrhenius, mean vs max, DRAM)
out['derived'] = dv

# ---------------------------------------------------------------- the rails, and the inversion illustration
rails = {}
for c in ('aifoundry2', 'aifoundry3', 'aifoundry1-c1'):
    vals = collections.defaultdict(list)
    for p in sorted(glob.glob(os.path.join(DATA, '2026-09-25-claims-v3', 'raw', c, 'idle', 'p*', 'telemetry.jsonl.gz'))):
        for line in gzip.open(p, 'rt'):
            s = json.loads(line)
            if (s.get('mhz') or {}).get('minion') != 600:
                continue
            for k in ('minion', 'sram', 'noc'):
                vals[k].append(s['die_mv'][k])
    rails[c] = {k: {'median': st.median(v), 'min': min(v), 'max': max(v), 'n': len(v)} for k, v in vals.items()}
out['rails'] = rails
INV = {'m': 1.2, 'alpha': 1.3, 'kappa_mV_per_K': 0.4, 'vth0_V': 0.40, 'T0_K': 300.0,
       'note': 'illustration: the alpha-power law with mobility falling as T^-1.2 and a threshold voltage falling 0.4 mV per kelvin (the forms of Dasdan and Hom, and of Salamin et al.); the parameters are chosen, not fitted, to put the crossover near 0.53 V, the value Salamin et al. simulate for a whole 7 nm FinFET processor'}


def delay(v, tc):
    tk = tc + 273.15
    vth = INV['vth0_V'] - INV['kappa_mV_per_K'] / 1000 * (tk - INV['T0_K'])
    return v / ((tk / INV['T0_K']) ** -INV['m'] * (v - vth) ** INV['alpha'])


def ztc(tc):
    tk = tc + 273.15
    vth = INV['vth0_V'] - INV['kappa_mV_per_K'] / 1000 * (tk - INV['T0_K'])
    return vth + INV['alpha'] * INV['kappa_mV_per_K'] / 1000 * tk / INV['m']


INV['ztc_V'] = {str(t): round(ztc(t), 3) for t in (25, 60, 100)}
volts = sorted({round(rails[c][k]['median']) for c in rails for k in ('minion', 'sram', 'noc')} | {out['fw']['mv_800']})
INV['curves'] = {str(v): [[t, round(delay(v / 1000, t) / delay(v / 1000, 25), 4)] for t in range(0, 126, 5)] for v in volts}
out['inversion'] = INV

# ---------------------------------------------------------------- the ladder of limits (outside, cited) and the ET row
out['limits'] = [
    {'name': 'NXP i.MX 8M Plus, consumer', 'short': 'i.MX 8M Plus, consumer', 'marks': [{'t': 'rating', 'lo': 0, 'hi': 95, 'what': 'rated junction range 0 to 95 °C'}], 'src': 'nxp-consumer'},
    {'name': 'NXP i.MX 8M Plus, industrial', 'short': 'i.MX 8M Plus, industrial', 'marks': [{'t': 'rating', 'lo': -40, 'hi': 105, 'what': 'rated junction range −40 to 105 °C'}], 'src': 'nxp-industrial'},
    {'name': 'AMD Ryzen 7000 (desktop CPU)', 'short': 'Ryzen 7000', 'marks': [{'t': 'throttle', 'at': 95, 'what': 'Tj,max 95 °C, "designed for a lifetime at 95°C"'}], 'src': 'amd-ryzen95'},
    {'name': 'Intel Core i9-13900K (desktop CPU)', 'short': 'Core i9-13900K', 'marks': [{'t': 'throttle', 'at': 100, 'what': 'TjMAX 100 °C: any sensor there starts the thermal control circuit'}], 'src': 'intel-13900k,intel-atm'},
    {'name': 'Intel Atom S1200 (microserver)', 'short': 'Atom S1200', 'marks': [{'t': 'throttle', 'lo': 90, 'hi': 102, 'what': 'Tj,max 90–102 °C by part: clock and voltage cut'}, {'t': 'shutdown', 'at': 125, 'what': 'THERMTRIP near 125 °C, calibrated per part; power must be removed'}], 'src': 'intel-atom'},
    {'name': 'NVIDIA Jetson Orin (SoC)', 'short': 'Jetson Orin', 'marks': [{'t': 'throttle', 'at': 99, 'what': 'software throttle 99 °C'}, {'t': 'throttle', 'at': 103, 'what': 'hardware throttle 103 °C: clocks cut 50–87.5%'}, {'t': 'shutdown', 'at': 104.5, 'what': 'software shutdown 104.5 °C'}, {'t': 'shutdown', 'at': 105, 'what': 'hardware shutdown 105 °C'}], 'src': 'jetson'},
    {'name': 'AMD Radeon RX 5700 (GPU)', 'short': 'Radeon RX 5700', 'marks': [{'t': 'throttle', 'at': 110, 'what': 'junction (hottest of many sensors) 110 °C'}], 'src': 'amd-rx5700'},
    {'name': 'AMD Versal AI Core (7 nm)', 'short': 'Versal AI Core (7 nm)', 'marks': [{'t': 'rating', 'lo': 0, 'hi': 100, 'what': 'rated 0 to 100 °C (extended grade)'}, {'t': 'budget', 'lo': 100, 'hi': 110, 'what': '100–110 °C allowed for at most 3% of the device’s life'}], 'src': 'versal'},
    {'name': 'TI embedded processors', 'short': 'TI embedded', 'marks': [{'t': 'rating', 'lo': 40, 'hi': 105, 'what': 'designed for 10 years at 105 °C, always on'}, {'t': 'budget', 'lo': 105, 'hi': 125, 'what': 'above 105 °C life is derated: 0.50, 0.40, 0.30, 0.20 of it at 110, 115, 120, 125 °C'}], 'src': 'ti-lifetime'},
    {'name': 'AEC-Q100 grade 1 (automotive)', 'short': 'AEC-Q100 grade 1', 'marks': [{'t': 'rating', 'lo': -40, 'hi': 125, 'what': 'ambient −40 to 125 °C (the junction runs hotter)'}], 'src': 'aecq100'},
    {'name': 'JEDEC JESD47 qualification', 'short': 'JESD47 qualification', 'marks': [{'t': 'qual', 'at': 125, 'what': 'powered 1,000 h at a junction of at least 125 °C, 0 of 231 parts may fail'}], 'src': 'jesd47'},
    {'name': 'LPDDR4X DRAM, standard grade', 'short': 'LPDDR4X, standard', 'marks': [{'t': 'rating', 'lo': -25, 'hi': 85, 'what': 'case −25 to 85 °C at 1× refresh'}, {'t': 'budget', 'lo': 85, 'hi': 105, 'what': 'above 85 °C: refresh 2× then 4× as often (elevated and automotive grades)'}], 'src': 'micron-lpddr4x'},
]
out['limits_et'] = {'throttle_mean_c': 66, 'pmic_c': 75}

# ---------------------------------------------------------------- what heat does, by temperature, and whether it reverses
t88 = [idle[c]['t_matmul_88w'] for c in idle if idle[c]['t_matmul_88w']]
out['mech'] = [
    {'what': 'Wear-out (electromigration, BTI, oxide) runs faster', 'short': 'Wear-out runs faster', 'lo': 40, 'hi': 160, 'cls': 'permanent', 'grad': True,
     'note': 'every degree counts: about 1.8–2.1 times as fast per 10 °C near 100 °C at 0.7–0.9 eV', 'src': 'ramp,jesd47,ti-lifetime'},
    {'what': 'Package fatigue: each large swing cracks solder and bumps a little more', 'short': 'Package fatigue per swing', 'lo': 40, 'hi': 160, 'cls': 'permanent', 'grad': True,
     'note': 'damage accumulates with every large temperature cycle, most at solder joints; a cracked joint can open when hot and close when cool, so the fault comes and goes although the damage stays', 'src': 'ramp,jesd47,pecht'},
    {'what': 'Leakage current and idle power rise', 'short': 'Leakage and idle power rise', 'lo': 40, 'hi': 160, 'cls': 'reversible', 'grad': True,
     'note': 'exponential in temperature; back to normal when it cools', 'src': 'kim-leakage,wp221'},
    {'what': 'Timing margin moves (setup where hot is slow, hold where hot is fast)', 'short': 'Timing margin moves', 'lo': 40, 'hi': 160, 'cls': 'reversible', 'grad': True,
     'note': 'fails only outside the corners the design was signed off for; recovers on cooling', 'src': 'dasdan,pedroso-hold'},
    {'what': 'Latch-up gets easier', 'short': 'Latch-up gets easier', 'lo': 40, 'hi': 160, 'cls': 'reset', 'grad': True,
     'note': 'once triggered it persists until the supply is removed, and can destroy the part', 'src': 'ti-latchup'},
    {'what': 'LPDDR4X past its 1× refresh limit: weak cells can lose data', 'short': 'DRAM past 1× refresh: data can decay', 'lo': 85, 'hi': 160, 'cls': 'reset',
     'note': '85 °C case; retention falls 39–47% per 10 °C; the cells recover, lost data does not', 'src': 'micron-lpddr4x,liu-retention'},
    {'what': 'Vendors’ throttle points', 'short': 'Vendors’ throttle points', 'lo': 95, 'hi': 110, 'cls': 'design',
     'note': 'the chip slows itself; full speed again when it cools', 'src': 'amd-ryzen95,intel-13900k,jetson,amd-rx5700'},
    {'what': 'ET-SoC-1: idle leakage plus a full random matmul reach the card’s 88 W input (derived, extrapolated)', 'short': 'ET-SoC-1: leakage + matmul hit 88 W (derived)', 'lo': min(t88), 'hi': max(t88), 'cls': 'reversible', 'et': True,
     'note': 'the card’s September idle laws plus a 27.2 W flip-count estimate; what the card does at that limit is not established', 'src': ''},
    {'what': 'Protective shutdown (thermal trip)', 'short': 'Protective shutdown', 'lo': 104.5, 'hi': 125, 'cls': 'reset',
     'note': 'Jetson at 105 °C, Intel near 125 °C: the chip is switched off before damage; cool it and reset', 'src': 'jetson,intel-atom,amd-bkdg'},
    {'what': 'Qualification: powered 1,000 h at a junction of 125 °C or more', 'short': 'Qualification, 1,000 h powered', 'lo': 125, 'hi': 160, 'cls': 'qual',
     'note': 'the normal qualification stress: 0 of 231 parts may fail', 'src': 'jesd47'},
    {'what': 'Unpowered storage qualification', 'short': 'Storage qualification', 'lo': 150, 'hi': 160, 'cls': 'qual',
     'note': '1,000 h at 150 °C; solder melts only at 217 °C, reflow peaks at 260 °C', 'src': 'jesd47,sac305,jstd020'},
]

# the sources: the page's citations plus the ladders' own keys; refuse a key sources.json lacks
for r in out['limits'] + out['mech']:
    cited.update(k for k in (r.get('src') or '').split(',') if k)
missing = sorted(cited - keys)
if missing:
    raise SystemExit('the page cites keys that sources.json lacks: ' + ', '.join(missing))
out['sources'] = [s for s in SRC if s['key'] in cited]
out['sources_unused'] = sorted(keys - cited)

out['written'] = '2026-09-28'
json.dump(out, open(os.path.join(HERE, 'overheat.json'), 'w'), separators=(',', ':'), sort_keys=True)
print('wrote overheat.json: %d sources cited, %d unused; %d of %d registered verdicts PASS, %d INSUFFICIENT, %d not testable'
      % (len(out['sources']), len(out['sources_unused']), out['verdicts']['n_pass'], out['verdicts']['n_registered'],
         out['verdicts']['n_insufficient'], out['verdicts']['n_not_testable']))
