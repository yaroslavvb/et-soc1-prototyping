#!/usr/bin/env python3
"""Build cards.json: every interval in which one of the four ET-SoC-1 cards was held by a measurement.

Sources, in order of authority:
  1. host logs (claims-v3 queue logs, gs queues, smoke logs) copied to $TIMELINE_DIR/hostlogs/<host>/
                                                                                            -> pass-level intervals
  2. claims-v3 raw block.json (t0_ms, t1_ms) and queue-state.jsonl                          -> cross-check / fill
  3. earlier experiments (18-24 Sep): telemetry/runs/starts/marks/sweep jsonl(.gz) under docs/reports/data/*/
     first and last timestamp per session file, files of one experiment on one card merged when < 2 min apart
  4. docs/findings/03-experiments.md stated times                                          -> cross-check, and
     the only source for a few short read-only or unrecorded holds (flagged approx)
  5. 27-28 Sep: the heat-placement (hp) queue logs of aifoundry3 and aifoundry1 card 1 (source 1), aifoundry2's two hp
     sessions (their block.json, committed under docs/reports/data/2026-09-28-heat-placement/raw/aifoundry2/hp/a2,
     $TIMELINE_HP_BUILD), the DV2 night on aifoundry2 (its queue log, source 1, and the committed block.json of
     docs/reports/data/2026-09-28-dvfs2-aifoundry2/raw), E50's PCIe runs (hosts.<card>.run_times_ms of
     docs/reports/data/2026-09-27-pcie/pcie.json), E53's overheating queues on aifoundry3 and aifoundry1 card 1 (their
     oh queue and smoke logs, source 1), and the DV2 validation on aifoundry2 from 28 Sep 20:45 (its dv2v block.json
     files in a claims-v3 build folder, $TIMELINE_DV2V_BUILD, until they are committed; its queue log, source 1, adds the
     replication sessions' own lines)
  6. 28-29 Sep, the major pass: E55 pcie2, E56 nocr, E57 memp2 and E58 tau, development on aifoundry1 card 1 and
     validation on aifoundry3, from their queue and series logs (source 1; their smoke passes count with them)
A queue that is still running at the snapshot ($TIMELINE_CUTOFF, else now) has its open pass closed at the snapshot;
a block that began after the snapshot is left out.
All times: log lines are the lab machines' local time (UTC-7, PDT); epoch ms elsewhere. Output in PDT.
"""
import collections, datetime, glob, gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths  # noqa: E402

TL = paths.TL
HOSTLOGS = os.path.join(TL, 'hostlogs')
REPO = paths.REPO
# aifoundry2's two heat-placement sessions left no queue log, only block.json files (tools/claims-v3/hp/run_a2.sh);
# they are committed under the heat-placement data's raw/aifoundry2/hp/a2/ ($TIMELINE_HP_BUILD: another claims-v3
# build folder to read hp blocks from instead)
HP_BUILD = os.environ.get('TIMELINE_HP_BUILD',
                          os.path.join(REPO, 'docs', 'reports', 'data', '2026-09-28-heat-placement', 'raw'))
# claims-v3 build folders whose DV2 validation blocks (dv2v) are not committed yet ($TIMELINE_DV2V_BUILD,
# os.pathsep-separated; default: this checkout's own build/claims-v3)
DV2V_BUILDS = [p for p in os.environ.get('TIMELINE_DV2V_BUILD', os.path.join(REPO, 'build', 'claims-v3')).split(os.pathsep) if p]
SNAP_MS = (datetime.datetime.fromisoformat(os.environ['TIMELINE_CUTOFF'].replace('Z', '+00:00')).timestamp() * 1000
           if os.environ.get('TIMELINE_CUTOFF') else datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)
DATA = os.path.join(REPO, 'docs/reports/data')
V3RAW = os.path.join(DATA, '2026-09-25-claims-v3/raw')
EXPDOC = os.path.join(REPO, 'docs/findings/03-experiments.md')
PDT = datetime.timezone(datetime.timedelta(hours=-7))
CARDS = ['aifoundry2', 'aifoundry3', 'aifoundry1-c0', 'aifoundry1-c1']
GAP_MS = 120 * 1000  # merge rule: holds closer than 2 min are one hold

SESSION_START_MS = datetime.datetime(2026, 9, 19, 16, 19, tzinfo=datetime.timezone.utc).timestamp() * 1000

V3_E = {'mem': 'E35', 'lat': 'E36', 'mmb': 'E37', 'abla': 'E38', 'ablb': 'E39', 'x5': 'E40', 'tel': 'E41',
        'wire': 'E42', 'rl': 'E43', 'idle': 'E44', 'cat': 'E45', 'catfull': 'E46', 'gs': 'E48', 'dv2': 'E51', 'dv2v': 'E51', 'hp': 'E52', 'oh': 'E53',
        'pcie2': 'E55', 'nocr': 'E56', 'memp2': 'E57', 'tau': 'E58'}
# the major pass's four experiments (28-29 Sep): development on aifoundry1 card 1, validation on aifoundry3
MP = ('pcie2', 'nocr', 'memp2', 'tau')
MP_ROLE = {'aifoundry1-c1': 'development', 'aifoundry3': 'validation'}
V3_NAME = {'mem': 'V3-MEM memory anatomy, cycle window, wake-up probe', 'lat': 'V3-LAT latency and bandwidth sweeps',
           'mmb': 'V3-MMB matmul benchmark', 'abla': 'V3-ABL-A tensor-unit energy', 'ablb': 'V3-ABL-B sparse compute',
           'x5': 'V3-X5 two launch temperatures', 'tel': 'V3-TEL meter chain', 'wire': 'V3-WIRE heat per mm',
           'rl': 'V3-RL rings, levels, relay', 'idle': 'V3-IDLE idle heat/cool cycles',
           'cat': 'V3-CAT catalogue temperature panel', 'catfull': 'V3-CATFULL full catalogue',
           'gs': 'GS gathers and scatters', 'hp': 'V3-HP heat placement and the thermal governor',
           'dv2': 'DV2 what the governor compares (development)', 'pcie': 'The host link and the launch path',
           'dv2v': 'DV2 what the governor compares (the frozen validation)',
           'oh': 'E53 the effect of overheating: hottest against mean, correctness and timing against temperature',
           'pcie2': 'E55 pcie2: two host-to-card copies at once, and where a host write lands',
           'nocr': 'E56 nocr: the mesh’s routing order and where the master and memory shires sit',
           'memp2': 'E57 memp2: the DRAM address map, the tensor reload, the 128 B cap, stride-256 energy',
           'tau': 'E58 tau: the rails’ one-second filter, per card and rail'}

FAMILY = {}
for e in ['matmul-18sep', 'sparsity-18sep', 'E33', 'E34', 'E1', 'E3']:
    FAMILY[e] = 'First measurements: matmul, sparsity, memory, NoC (18-20 Sep)'
for e in ['E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E12', 'E15', 'E16', 'E20']:
    FAMILY[e] = 'Power, temperature and Horace (20-22 Sep)'
for e in ['E18', 'E19', 'E21']:
    FAMILY[e] = 'DVFS, leakage, governor (22 Sep)'
for e in ['E22', 'E23', 'E22/E23', 'E24', 'E25', 'E24/E25']:
    FAMILY[e] = 'Hot line and on-chip relay (22 Sep)'
for e in ['E26', 'E27', 'E28', 'E29']:
    FAMILY[e] = 'Energy manual catalogue and reruns (23 Sep)'
for e in ['E31', 'E32']:
    FAMILY[e] = 'Heat per millimetre (24 Sep)'


def v3_family(phase):
    return {'smoke': 'Claims check v3: smoke tests (25-26 Sep)',
            'pre-reboot': 'Claims check v3: pre-reboot campaign (25 Sep 10:00-16:19)',
            'campaign': 'Claims check v3: campaign after the fixes (25-26 Sep)',
            'gs-queue': 'Gathers and scatters, E48 (26 Sep)',
            'pcie': 'The host link, E50 (27 Sep)',
            'hp': 'Heat placement: development and validation (27-28 Sep)',
            'dv2': 'DV2: the governor and heat, development (28 Sep)',
            'dv2v': 'DV2: the governor and heat, validation (28-29 Sep)',
            'oh': 'The effect of overheating, E53 (28 Sep)',
            'mp': 'The major pass: E55-E58 (28-29 Sep)'}[phase]


def iso(ms):
    return datetime.datetime.fromtimestamp(ms / 1000, PDT).isoformat(timespec='seconds')


def parse_local(s):
    s = s[:19]
    return datetime.datetime.fromisoformat(s).replace(tzinfo=PDT).timestamp() * 1000


# ---------------------------------------------------------------- 1. host logs
LINE = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:[-+]\d{2}:\d{2})?\s+\[([\w-]+)\]\s+(.*)$')
BEG = re.compile(r'^([\w-]+) p(\d+)(?: \([\w ]+\))? begins(?: \(die (\d+) C\))?')   # pcie2: 'p101 (development) begins'
END = re.compile(r'^([\w-]+) p(\d+) ends:?\s*(.*)$')
FAIL = re.compile(r'^([\w-]+) p(\d+) failed \(rc (\d+)\)')
PRE_REBOOT_END = parse_local('2026-09-25T16:20:00')

log_intervals = []
queue_segments = []
problems = []
for path in sorted(glob.glob(os.path.join(HOSTLOGS, '*', '*.log'))):
    host = os.path.basename(os.path.dirname(path))
    fname = os.path.basename(path)
    open_ = {}
    last_closed = {}
    qopen = {}
    last_ts = {}
    for raw in open(path, errors='replace'):
        m = LINE.match(raw.rstrip('\n'))
        if not m:
            continue
        ts = parse_local(m.group(1))
        card, msg = m.group(2), m.group(3)
        last_ts[card] = ts
        if msg.startswith('queue starts'):
            qopen[card] = (ts, msg.split(':', 1)[1].strip())
            continue
        if msg.startswith('queue ends'):
            if card in qopen:
                t0, sched = qopen.pop(card)
                queue_segments.append({'card': card, 'start_ms': t0, 'end_ms': ts, 'schedule': sched, 'log': f'{host}/{fname}'})
            continue
        if msg.startswith('STOP file present'):
            if card in qopen:
                queue_segments.append({'card': card, 'start_ms': qopen[card][0], 'end_ms': ts,
                                       'schedule': qopen[card][1], 'log': f'{host}/{fname}', 'stopped': True})
                qopen.pop(card)
            continue
        b = BEG.match(msg)
        if b:
            key = (card, b.group(1), int(b.group(2)))
            if key in open_:
                problems.append(f'{host}/{fname}: {key} begins twice; first closed at the second begin')
                t0, die = open_.pop(key)
                log_intervals.append(dict(card=card, exp=key[1], pass_=key[2], start_ms=t0, end_ms=ts, status='unclosed',
                                          die_c=die, source=f'hostlogs/{host}/{fname}'))
            open_[key] = (ts, int(b.group(3)) if b.group(3) else None)
            continue
        f = FAIL.match(msg)
        if f:
            key = (card, f.group(1), int(f.group(2)))
            if key not in open_ and key in last_closed and abs(last_closed[key]['end_ms'] - ts) < 5000:
                last_closed[key]['status'] = f'failed rc {f.group(3)} ({last_closed[key]["status"]})'
                continue
            if key in open_:
                t0, die = open_.pop(key)
                log_intervals.append(dict(card=card, exp=key[1], pass_=key[2], start_ms=t0, end_ms=ts,
                                          status=f'failed rc {f.group(3)}', die_c=die, source=f'hostlogs/{host}/{fname}'))
            continue
        e = END.match(msg)
        if e:
            key = (card, e.group(1), int(e.group(2)))
            if key in open_:
                t0, die = open_.pop(key)
                rest = e.group(3)
                st = 'ok' if rest.startswith('ok') else (rest.split()[0] if rest else 'ended')
                log_intervals.append(dict(card=card, exp=key[1], pass_=key[2], start_ms=t0, end_ms=ts, status=st,
                                          die_c=die, source=f'hostlogs/{host}/{fname}', result=rest[:160]))
                last_closed[key] = log_intervals[-1]
    for key, (t0, die) in open_.items():
        running = key[0] in qopen and SNAP_MS - last_ts.get(key[0], t0) < 30 * 60 * 1000
        if running:
            problems.append(f'{host}/{fname}: {key} still running; closed at the snapshot')
        else:
            problems.append(f'{host}/{fname}: {key} begins with no end; closed at the log\'s last line')
        log_intervals.append(dict(card=key[0], exp=key[1], pass_=key[2], start_ms=t0,
                                  end_ms=SNAP_MS if running else last_ts.get(key[0], t0),
                                  status='running' if running else 'unclosed', die_c=die, source=f'hostlogs/{host}/{fname}'))
        if running:
            last_ts[key[0]] = SNAP_MS
    for card, (t0, sched) in qopen.items():
        queue_segments.append({'card': card, 'start_ms': t0, 'end_ms': last_ts.get(card, t0), 'schedule': sched,
                               'log': f'{host}/{fname}', 'unclosed': True})

# dedupe identical (card, exp, pass, start) from overlapping log copies
seen = set()
ded = []
for iv in sorted(log_intervals, key=lambda x: (x['card'], x['start_ms'])):
    k = (iv['card'], iv['exp'], iv['pass_'], iv['start_ms'])
    if k in seen:
        continue
    seen.add(k)
    ded.append(iv)
log_intervals = ded

for iv in log_intervals:
    base = iv['exp'][:-len('-smoke')] if iv['exp'].endswith('-smoke') else iv['exp']
    if base in MP:
        phase = 'mp'          # its smoke passes too: they belong to the experiment, not to the 25-26 Sep smoke tests
    elif iv['exp'].endswith('-smoke'):
        phase = 'smoke'
    elif base in ('hp', 'dv2', 'dv2v', 'oh'):
        phase = base
    elif base == 'gs':
        phase = 'gs-queue'
    elif iv['start_ms'] < PRE_REBOOT_END:
        phase = 'pre-reboot'
    else:
        phase = 'campaign'
    iv['phase'] = phase
    iv['exp_short'] = base
    iv['E'] = V3_E.get(base)
    iv['label'] = (f"HP p{iv['pass_']}" if base == 'hp' else
                   f"{V3_E[base]} {iv['exp']} p{iv['pass_']} ({MP_ROLE.get(iv['card'], '?')})" if phase == 'mp' else
                   f"{V3_E.get(base, '?')} {base}{'-smoke' if phase == 'smoke' else ''} p{iv['pass_']}")
    iv['name'] = V3_NAME.get(base, base)
    iv['family'] = v3_family(phase)

# ---------------------------------------------------------------- 2. block.json and queue-state.jsonl
blocks = []
BLOCK_ROOTS = [V3RAW, os.path.join(DATA, '2026-09-28-dvfs2-aifoundry2', 'raw'), HP_BUILD] + DV2V_BUILDS
seen_blocks = set()
for p in sorted({q for r in BLOCK_ROOTS for q in glob.glob(os.path.join(r, '*', '**', 'block.json'), recursive=True)}):
    top = next(r for r in BLOCK_ROOTS if p.startswith(os.path.join(r, '')))
    if top == HP_BUILD and '/hp/a2/' not in p:
        continue          # the other hp blocks have queue logs (source 1)
    if top in DV2V_BUILDS and '/dv2v/' not in p:
        continue
    try:
        d = json.load(open(p))
    except Exception as ex:
        problems.append(f'unreadable {os.path.relpath(p, top)}: {ex}')
        continue
    rel = os.path.relpath(p, top)
    if d.get('exp') == 'hp/a2':          # aifoundry2's two hp sessions (tools/claims-v3/hp/run_a2.sh): no queue log
        d['exp'] = 'hp'
    if d.get('t0_ms') and d['t0_ms'] > SNAP_MS:
        continue          # began after the snapshot
    key = (d.get('card') or rel.split('/')[0], d.get('exp'), d.get('pass'), d.get('t0_ms'))
    if key in seen_blocks:
        continue          # the same block in a build folder and in the committed data
    seen_blocks.add(key)
    blocks.append(dict(card=key[0], exp=d.get('exp'), pass_=d.get('pass'),
                       t0=d.get('t0_ms'), t1=d.get('t1_ms'), status=d.get('status'), file=rel))
qstate = []
for p in sorted(glob.glob(os.path.join(V3RAW, '*', 'queue-state.jsonl'))):
    card = os.path.basename(os.path.dirname(p))
    for line in open(p):
        try:
            d = json.loads(line)
        except Exception:
            continue
        qstate.append(dict(card=card, **d))

idx = collections.defaultdict(list)
for iv in log_intervals:
    idx[(iv['card'], iv['exp'], iv['pass_'])].append(iv)
block_unmatched = []
deltas = []
for b in blocks:
    cands = idx.get((b['card'], b['exp'], b['pass_']), [])
    best = None
    for iv in cands:
        if b['t0'] is None:
            continue
        dt = abs(iv['start_ms'] - b['t0'])
        if dt < 10 * 60 * 1000 and (best is None or dt < abs(best['start_ms'] - b['t0'])):
            best = iv
    if best is None:
        block_unmatched.append(b)
        continue
    best['block_json'] = {'t0_ms': b['t0'], 't1_ms': b['t1'], 'status': b['status']}
    deltas.append(((b['t0'] - best['start_ms']) / 1000, ((b['t1'] or b['t0']) - best['end_ms']) / 1000))

# blocks with no log line become intervals of their own
for b in block_unmatched:
    if not b['t0'] or not b['t1']:
        continue
    phase = ('gs-queue' if b['exp'] == 'gs' else b['exp'] if b['exp'] in ('hp', 'dv2', 'dv2v', 'oh') else
             'pre-reboot' if b['t0'] < PRE_REBOOT_END else 'campaign')
    log_intervals.append(dict(card=b['card'], exp=b['exp'], exp_short=b['exp'], pass_=b['pass_'], start_ms=b['t0'],
                              end_ms=b['t1'], status=b['status'], source='block.json ' + b['file'], phase=phase,
                              E=V3_E.get(b['exp']),
                              label=(f"HP a2 p{b['pass_']}" if b['exp'] == 'hp' else f"{V3_E.get(b['exp'], '?')} {b['exp']} p{b['pass_']}"),
                              name=V3_NAME.get(b['exp'], b['exp']), family=v3_family(phase)))

# queue-state cross-check (count only)
qs_unmatched = 0
for q in qstate:
    if not any(abs(iv['start_ms'] - q['t0_ms']) < 10 * 60 * 1000 for iv in idx.get((q['card'], q['exp'], q['pass']), [])):
        qs_unmatched += 1

# ---------------------------------------------------------------- 5b. E50, the PCIe runs (27 Sep): one interval per run,
# the card's lock held for a whole run of six processes (pcie.json hosts.<card>.run_times_ms)
PCIE = os.path.join(DATA, '2026-09-27-pcie', 'pcie.json')
if os.path.exists(PCIE):
    for c, h in json.load(open(PCIE)).get('hosts', {}).items():
        for i, (a, b) in enumerate(h.get('run_times_ms') or [], 1):
            log_intervals.append(dict(card=c, exp='pcie', exp_short='pcie', pass_=i, start_ms=a, end_ms=b, status='ok',
                                      source='2026-09-27-pcie/pcie.json hosts.run_times_ms', phase='pcie', E='E50',
                                      label=f'E50 pcie run {i}', name=V3_NAME['pcie'], family=v3_family('pcie')))
else:
    problems.append(f'no {PCIE}: E50 left out')

# ---------------------------------------------------------------- 3. earlier experiments (18-24 Sep)
DIR_E = {
    '2026-09-18-aifoundry2': ('matmul-18sep', 'Matmul efficiency session (18 Sep, before the register)'),
    '2026-09-18-memhier-aifoundry2': ('E33', 'Memory hierarchy: latency, bandwidth, scratchpad distance'),
    '2026-09-18-nocbench-aifoundry2': ('E34', 'On-chip communication and its energy'),
    '2026-09-18-sparsity-aifoundry3': ('sparsity-18sep', 'Sparse compute session (18 Sep, before the register)'),
    '2026-09-19-memprobe-aifoundry2': ('E1', 'One memory access taken apart'),
    '2026-09-20-traceprof-aifoundry2': ('E3', 'Device flame graphs'),
    '2026-09-21-horace-aifoundry2/strict': ('E9', 'Horace, strict protocol, 14 patterns'),
    '2026-09-21-horace-aifoundry2/cold1': ('E10', 'Cool-start runs: the clock governor'),
    '2026-09-21-horace-aifoundry2/cold2': ('E10', 'Cool-start runs: the clock governor'),
    '2026-09-21-horace-aifoundry2/long': ('E12', 'Long runs: minutes instead of seconds'),
    '2026-09-21-horace-aifoundry2/ablation': ('E15', 'Ablations and structured matrices, 7 s each'),
    '2026-09-21-horace-aifoundry2/long2': ('E16', 'Long runs of structured matrices'),
    '2026-09-22-dvfs-aifoundry2': ('E19', 'Idle power after 20 hours'),
    '2026-09-22-horace-aifoundry3': ('E20', 'The strict protocol on a second card'),
    '2026-09-22-hotline-aifoundry2': ('E22/E23', 'Hot line: contention sweeps and host-shire power'),
    '2026-09-22-hotline-aifoundry3': ('E22/E23', 'Hot line: contention sweeps'),
    '2026-09-22-onchip-aifoundry2': ('E24/E25', 'Scratchpad probe and on-chip relay vs DRAM'),
    '2026-09-22-onchip-aifoundry3': ('E24/E25', 'Scratchpad probe and on-chip relay vs DRAM'),
    '2026-09-23-enercat-aifoundry2': ('E26', 'Instruction and byte energy catalogue'),
    '2026-09-23-enercat-aifoundry3': ('E26', 'Instruction and byte energy catalogue'),
    '2026-09-23-catalogue-aifoundry2': ('E27', 'Comprehensive instruction and memory catalogue'),
    '2026-09-23-catalogue-aifoundry3': ('E27', 'Comprehensive instruction and memory catalogue'),
    '2026-09-23-catalogue-aifoundry2-rows': ('E28', 'DRAM row hits against row misses'),
    '2026-09-23-reruns-aifoundry2': ('E29', 'Confidence-bar reruns (cool card, discarded set)'),
    '2026-09-23-reruns-aifoundry2-warm': ('E29', 'Confidence-bar reruns: relay, hot line, rings, levels'),
    '2026-09-23-reruns-aifoundry3': ('E29', 'Confidence-bar reruns: relay, hot line, rings, levels'),
    '2026-09-24-wire-aifoundry2': ('E31', 'Heat per mm, first run'),
    '2026-09-24-wire-aifoundry3': ('E31', 'Heat per mm, first run'),
    '2026-09-24-wire2-aifoundry2': ('E32', 'Heat per mm, second run'),
    '2026-09-24-wire2-aifoundry3': ('E32', 'Heat per mm, second run'),
}
POWER_FILES = {'thermal-telemetry.jsonl': ('E5', 'Load step: power, temperature, rails'),
               'thermal-phases.jsonl': ('E5', 'Load step: power, temperature, rails'),
               'horace-telemetry.jsonl': ('E7', 'Horace, first version (uncontrolled)'),
               'horace-runs.jsonl': ('E7', 'Horace, first version (uncontrolled)'),
               'horace2-telemetry.jsonl': ('E8', 'Horace, second version (each run from 80 C)'),
               'horace2-runs.jsonl': ('E8', 'Horace, second version (each run from 80 C)'),
               'horace2-starts.jsonl': ('E8', 'Horace, second version (each run from 80 C)')}
TKEYS = ('t_ms', 't_start_ms', 't_end_ms', 't0_ms', 't1_ms', 'ts_ms', 'time_ms')


def epoch_ms(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if 1.6e12 < v < 2.2e12:
            return float(v)
        if 1.6e9 < v < 2.2e9:
            return float(v) * 1000
    return None


def file_range(p):
    op = gzip.open if p.endswith('.gz') else open
    lo = hi = None
    n = 0
    hosts = collections.Counter()
    with op(p, 'rt', errors='replace') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            for k in TKEYS:
                if k in d:
                    m = epoch_ms(d[k])
                    if m:
                        n += 1
                        lo = m if lo is None else min(lo, m)
                        hi = m if hi is None else max(hi, m)
            if isinstance(d.get('host'), str):
                hosts[d['host']] += 1
    return lo, hi, n, hosts


def card_of(rel, hosts):
    if hosts:
        h = hosts.most_common(1)[0][0]
        if h in CARDS:
            return h
    top = rel.split('/')[0]
    if 'aifoundry3' in top:
        return 'aifoundry3'
    if 'aifoundry2' in top:
        return 'aifoundry2'
    return None


early_files = []
for p in sorted(glob.glob(os.path.join(DATA, '*', '**', '*.jsonl*'), recursive=True)):
    rel = os.path.relpath(p, DATA)
    if rel.startswith(('2026-09-25-claims-v3/', '2026-09-26-', '2026-09-27-', '2026-09-28-', '2026-09-29-')):
        continue   # sources 1, 2, 5 and 6
    base = os.path.basename(p)
    if not re.search(r'(telemetry|runs|starts|marks|sweep|idle_20h|phases)', base):
        continue
    lo, hi, n, hosts = file_range(p)
    if lo is None:
        continue
    card = card_of(rel, hosts)
    lab = None
    if base in POWER_FILES and rel.startswith('2026-09-20-power-aifoundry2'):
        lab = POWER_FILES[base]
    else:
        parts = rel.split('/')
        for k in (('/'.join(parts[:2])), parts[0]):
            if k in DIR_E:
                lab = DIR_E[k]
                break
    if lab is None:
        problems.append(f'no experiment label for {rel}')
        continue
    early_files.append(dict(file=rel, card=card, E=lab[0], name=lab[1], start_ms=lo, end_ms=hi, n=n))

# cool2.log (E21): "<epoch s> {json}" lines, a governor-input poll on aifoundry2 (518 mV)
cool = os.path.join(DATA, '2026-09-22-cards/cool2.log')
ts = [int(l.split()[0]) * 1000 for l in open(cool) if re.match(r'^\d{10} ', l)]
if ts:
    early_files.append(dict(file='2026-09-22-cards/cool2.log', card='aifoundry2', E='E21',
                            name="The governor's inputs (config poll while cooling)", start_ms=min(ts), end_ms=max(ts), n=len(ts)))

# merge files of one (card, E) closer than 2 min
early_intervals = []
grp = collections.defaultdict(list)
for f in early_files:
    grp[(f['card'], f['E'])].append(f)
for (card, E), fs in grp.items():
    fs.sort(key=lambda x: x['start_ms'])
    cur = None
    for f in fs:
        if cur and f['start_ms'] - cur['end_ms'] < GAP_MS:
            cur['end_ms'] = max(cur['end_ms'], f['end_ms'])
            cur['files'].append(f['file'])
            continue
        if cur:
            early_intervals.append(cur)
        cur = dict(card=card, E=E, name=f['name'], start_ms=f['start_ms'], end_ms=f['end_ms'], files=[f['file']])
    if cur:
        early_intervals.append(cur)

# ---------------------------------------------------------------- 4. 03-experiments.md stated times
HDR = re.compile(r'^## (E\d+) — (.*)$')
doc = {}
for line in open(EXPDOC):
    m = HDR.match(line.rstrip())
    if not m:
        continue
    E, rest = m.group(1), m.group(2)
    pm = re.search(r'\(([^()]*\d{4}-\d{2}-\d{2}[^()]*)\)\s*$', rest)
    title = rest[:pm.start()].strip() if pm else rest
    entry = {'title': title, 'paren': pm.group(1) if pm else None}
    if pm:
        s = pm.group(1)
        dm = re.search(r'(\d{4})-(\d{2})-(\d{2})', s)
        after = s[dm.end():]
        tm = re.search(r'(\d{2}):(\d{2})(?:\s*[–-]\s*(?:(\d{2})-(\d{2})\s+)?(\d{2}):(\d{2}))?', after)
        if tm:
            y, mo, d = int(dm.group(1)), int(dm.group(2)), int(dm.group(3))
            t0 = datetime.datetime(y, mo, d, int(tm.group(1)), int(tm.group(2)), tzinfo=PDT)
            if tm.group(5):
                mo2, d2 = (int(tm.group(3)), int(tm.group(4))) if tm.group(3) else (mo, d)
                t1 = datetime.datetime(y, mo2, d2, int(tm.group(5)), int(tm.group(6)), tzinfo=PDT)
            else:
                t1 = t0
            entry['start_ms'] = t0.timestamp() * 1000
            entry['end_ms'] = t1.timestamp() * 1000
        entry['date'] = dm.group(0)
        low = s.lower()
        entry['cards_text'] = ('three cards' if 'three cards' in low else 'both cards' if 'both' in low else
                               'aifoundry3' if 'aifoundry3' in low else 'aifoundry2' if 'aifoundry2' in low else None)
        entry['offline'] = 'offline' in low
    doc[E] = entry

NO_CARD = {'E2': 'RTL simulation of the cycle-counter carry (no card)',
           'E4': 'counter-select syscall, simulator only (never run on a card)',
           'E11': 'RTL toggle simulation of the multiply-add unit (no card)',
           'E13': 'RTL toggle simulation of structured matrices (no card)',
           'E14': 'predictions recorded before the matrices ran (no card time)',
           'E17': 'flips-to-temperature model fitted offline (no card time)',
           'E30': 'analysis of E27 and E28 (no card time)',
           'E47': 'registered, not run',
           'E49': "runtime log-level race reproduced on aifoundry2's CPU, without a card"}

# doc-only holds: short or unrecorded card use, from the stated times (approximate)
doc_only = [
    dict(card='aifoundry2', E='E18', name='Wake-up probe (single hart, 4.9 s)',
         start_ms=datetime.datetime(2026, 9, 22, 11, 39, tzinfo=PDT).timestamp() * 1000, dur_s=60,
         note='03-experiments.md: 11:39, a 4.9 s single-hart probe; wakeup.json has no timestamps; drawn as one minute'),
    dict(card='aifoundry2', E='E21', name="The governor's inputs (read-only queries)",
         start_ms=datetime.datetime(2026, 9, 22, 12, 42, tzinfo=PDT).timestamp() * 1000,
         end_ms=datetime.datetime(2026, 9, 22, 12, 47, tzinfo=PDT).timestamp() * 1000,
         note='03-experiments.md: 12:42-12:47, read-only config and log-buffer queries'),
    dict(card='aifoundry3', E='E21', name="The governor's inputs (read-only queries)",
         start_ms=datetime.datetime(2026, 9, 22, 12, 42, tzinfo=PDT).timestamp() * 1000,
         end_ms=datetime.datetime(2026, 9, 22, 12, 47, tzinfo=PDT).timestamp() * 1000,
         note='03-experiments.md: 12:42-12:47, read-only config and log-buffer queries'),
]
for E, what in (('E33', 'Memory hierarchy: latency, bandwidth, scratchpad distance'),
                ('E34', 'On-chip communication and its energy')):
    ent = doc.get(E, {})
    if 'start_ms' in ent:
        doc_only.append(dict(card='aifoundry2', E=E, name=what, start_ms=ent['start_ms'], end_ms=ent['end_ms'],
                             note='03-experiments.md stated range; the probe files before the energy runs carry no timestamps'))
for d in doc_only:
    if 'end_ms' not in d:
        d['end_ms'] = d['start_ms'] + d.pop('dur_s') * 1000

# ---------------------------------------------------------------- assemble
intervals = []
for iv in log_intervals:
    o = dict(card=iv['card'], start=iso(iv['start_ms']), end=iso(iv['end_ms']), start_ms=int(iv['start_ms']),
             end_ms=int(iv['end_ms']), minutes=round((iv['end_ms'] - iv['start_ms']) / 60000, 2), E=iv.get('E'),
             exp=iv['exp_short'], pass_n=iv['pass_'], label=iv['label'], name=iv['name'], phase=iv['phase'],
             family=iv['family'], status=iv.get('status'), source=iv['source'])
    if iv.get('die_c') is not None:
        o['die_c_start'] = iv['die_c']
    if iv.get('block_json'):
        bj = iv['block_json']
        o['block_json'] = {'start': iso(bj['t0_ms']) if bj['t0_ms'] else None, 'end': iso(bj['t1_ms']) if bj['t1_ms'] else None,
                           'status': bj['status']}
    intervals.append(o)
for iv in early_intervals:
    isE = iv['E'].startswith('E')
    intervals.append(dict(card=iv['card'], start=iso(iv['start_ms']), end=iso(iv['end_ms']), start_ms=int(iv['start_ms']),
                          end_ms=int(iv['end_ms']), minutes=round((iv['end_ms'] - iv['start_ms']) / 60000, 2),
                          E=iv['E'] if isE else None, exp=iv['E'],
                          label=f"{iv['E']} {iv['name']}" if isE else iv['name'], name=iv['name'], phase='early',
                          family=FAMILY.get(iv['E'], 'Other'), status='data', source='data files: ' + ', '.join(iv['files'][:6]) +
                          (f' (+{len(iv["files"]) - 6} more)' if len(iv['files']) > 6 else ''),
                          n_files=len(iv['files'])))
for iv in doc_only:
    intervals.append(dict(card=iv['card'], start=iso(iv['start_ms']), end=iso(iv['end_ms']), start_ms=int(iv['start_ms']),
                          end_ms=int(iv['end_ms']), minutes=round((iv['end_ms'] - iv['start_ms']) / 60000, 2), E=iv['E'],
                          exp=iv['E'], label=f"{iv['E']} {iv['name']}", name=iv['name'], phase='early',
                          family=FAMILY.get(iv['E'], 'Other'), status='stated', source='03-experiments.md (approx.)',
                          approx=True, note=iv['note']))
intervals.sort(key=lambda x: (x['start_ms'], x['card']))
for i, iv in enumerate(intervals):
    iv['id'] = i
    iv['before_session'] = iv['end_ms'] <= SESSION_START_MS


def union(ivs, gap=0):
    ivs = sorted((a, b) for a, b in ivs)
    out = []
    for a, b in ivs:
        if out and (a - out[-1][1] < gap or a <= out[-1][1]):   # a gap under 2 min (the rule), or an overlap
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def hours(u):
    return sum(b - a for a, b in u) / 3.6e6


per_card = {}
holds = {}
for c in CARDS:
    ivs = [(x['start_ms'], x['end_ms']) for x in intervals if x['card'] == c]
    u0 = union(ivs, 0)
    u2 = union(ivs, GAP_MS)
    holds[c] = u2
    in_week = [(max(a, SESSION_START_MS), b) for a, b in u2 if b > SESSION_START_MS]
    per_card[c] = {'card_hours_held': round(hours(u2), 2), 'card_hours_busy': round(hours(u0), 2),
                   'card_hours_held_since_session_start': round(hours(in_week), 2),
                   'intervals': sum(1 for x in intervals if x['card'] == c), 'holds_merged_2min': len(u2)}

by_family = collections.defaultdict(float)
by_E = collections.defaultdict(float)
by_phase = collections.defaultdict(float)
for key, bucket in (('family', by_family), ('E', by_E), ('phase', by_phase)):
    g = collections.defaultdict(list)
    for x in intervals:
        g[(x[key] or x['exp'], x['card'])].append((x['start_ms'], x['end_ms']))
    for (k, c), ivs in g.items():
        bucket[k] += hours(union(ivs, GAP_MS))
round_d = lambda d: {k: round(v, 2) for k, v in sorted(d.items(), key=lambda kv: -kv[1])}

# holds: merged spans per card with their labels (for drawing lanes)
hold_list = []
for c in CARDS:
    for a, b in holds[c]:
        labs = collections.OrderedDict()
        for x in intervals:
            if x['card'] == c and x['start_ms'] < b and x['end_ms'] > a:
                labs[x['E'] or x['exp']] = 1
        hold_list.append(dict(card=c, start=iso(a), end=iso(b), start_ms=int(a), end_ms=int(b),
                              minutes=round((b - a) / 60000, 1), experiments=list(labs)))
hold_list.sort(key=lambda x: (x['start_ms'], x['card']))

# series: cards in use per minute
t_first = min(x['start_ms'] for x in intervals)
t_last = max(x['end_ms'] for x in intervals)
day0 = datetime.datetime.fromtimestamp(t_first / 1000, PDT).replace(hour=0, minute=0, second=0, microsecond=0)
day1 = datetime.datetime.fromtimestamp(t_last / 1000, PDT).replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
s0 = day0.timestamp() * 1000
nmin = int((day1.timestamp() * 1000 - s0) // 60000)
busy = {c: bytearray(nmin) for c in CARDS}
for c in CARDS:
    for x in intervals:
        if x['card'] != c:
            continue
        i0 = int((x['start_ms'] - s0) // 60000)
        i1 = int((x['end_ms'] - s0 - 1) // 60000)
        for i in range(max(i0, 0), min(i1, nmin - 1) + 1):
            busy[c][i] = 1
counts = [sum(busy[c][i] for c in CARDS) for i in range(nmin)]
runs = []
for i, v in enumerate(counts):
    if runs and runs[-1][2] == v:
        runs[-1][1] = i + 1
    else:
        runs.append([i, i + 1, v])
series = {'start': day0.isoformat(), 'step_minutes': 1, 'n': nmin,
          'note': 'value = number of the four cards held by a measurement during that minute (0-4)',
          'values': counts,
          'runs': [{'start': iso(s0 + a * 60000), 'end': iso(s0 + b * 60000), 'cards': v} for a, b, v in runs if v > 0],
          'max': max(counts), 'minutes_with': {str(k): counts.count(k) for k in range(5)}}

# cross-check against 03-experiments.md
cross = []
for E, ent in sorted(doc.items(), key=lambda kv: int(kv[0][1:])):
    xs = [x for x in intervals if x['E'] and (x['E'] == E or E in x['E'].split('/')) and not x.get('approx')
          and x['phase'] in ('early', 'campaign', 'gs-queue', 'pcie', 'dv2', 'oh', 'mp')]
    row = {'E': E, 'title': ent['title'], 'stated': ent.get('paren')}
    if xs:
        a = min(x['start_ms'] for x in xs)
        b = max(x['end_ms'] for x in xs)
        row['data_start'] = iso(a)
        row['data_end'] = iso(b)
        row['cards'] = sorted({x['card'] for x in xs})
        pre = [x for x in intervals if x['E'] == E and x['phase'] in ('smoke', 'pre-reboot')]
        if pre:
            row['also_smoke_or_pre_reboot'] = f"{len(pre)} intervals from {iso(min(x['start_ms'] for x in pre))} (not in the stated range)"
        if 'start_ms' in ent:
            row['start_diff_min'] = round((a - ent['start_ms']) / 60000, 1)
            row['end_diff_min'] = round((b - ent['end_ms']) / 60000, 1) if ent['end_ms'] != ent['start_ms'] else None
    elif E in NO_CARD:
        row['no_card_time'] = NO_CARD[E]
    elif any(x['E'] == E for x in intervals):
        row['approx_from_doc_only'] = True
    else:
        row['undated'] = True
    cross.append(row)

undated = [
    {'E': 'E3', 'what': 'Device flame graphs on aifoundry2 (20 Sep); events.jsonl has device cycles only, about 0.15 s of card time'},
    {'E': 'E6', 'what': 'Per-shire on-die voltage map on aifoundry2 (20 Sep); SP trace dumps carry no wall-clock time'},
    {'E': 'E24', 'what': "the scratchpad-probe rows carry no timestamps; E24/E25 is dated by the relay rows of the same sweeps (15:57-15:59, 22 Sep)"},
    {'E': 'E18', 'what': 'wake-up probe: no timestamps in wakeup.json; drawn from the stated 11:39 (22 Sep) as one minute (approx)'},
    {'E': 'E21', 'what': "read-only governor queries: stated 12:42-12:47 (22 Sep) on both cards (approx); aifoundry2's cooling poll (cool2.log) is dated 12:46-12:59"},
    {'E': 'E33, E34', 'what': 'the chase and pair probes carry no timestamps; the stated ranges (17:44-17:52, 19:14-19:28 on 18 Sep) are added as approx intervals around the dated energy runs'},
    {'E': 'lab repair work', 'what': 'card use while fixing aifoundry1 and debugging on 24-25 Sep is not a measurement and has no data files'},
]

# card events that are not holds: the Master Minion hang that ended the DV2 night (the queue's own alert record)
events = []
for ap in sorted(glob.glob(os.path.join(DATA, '2026-09-28-dvfs2-aifoundry2', 'raw', 'ALERT-*.json'))):
    al = json.load(open(ap))
    events.append({'card': al['card'], 't': iso(al['t_ms']), 't_ms': al['t_ms'], 'kind': al['kind'], 'pass': al.get('pass'),
                   'source': os.path.relpath(ap, DATA)})

out = {
    'generated': datetime.datetime.now(PDT).isoformat(timespec='seconds'),
    'timezone': 'America/Los_Angeles (PDT, UTC-7); all times below are PDT',
    'session_start': iso(SESSION_START_MS),
    'rules': {'merge_gap_minutes': 2,
              'card_hours_held': 'union of a card\'s intervals, bridging gaps under 2 min (a queue keeps the card between passes)',
              'card_hours_busy': 'exact union of the intervals, no bridging',
              'sources': ['claims-v3 host logs: "<exp> p<N> begins ... ends/failed" lines (lab-local time = PDT)',
                          'claims-v3 raw block.json t0_ms/t1_ms (cross-check; fills passes with no log line)',
                          'earlier data: first/last timestamp (t_ms, t_start_ms, t_end_ms) of every telemetry/runs/starts/marks/sweep file, merged per card and experiment when < 2 min apart',
                          '03-experiments.md stated times (cross-check; the only source for E18 and E21, flagged approx)'],
              'phases': {'early': 'E1-E34 and the 18 Sep sessions (18-24 Sep)',
                         'smoke': 'claims-v3 smoke tests (25 Sep 10:51-11:00 on aifoundry2/3; 17:13-17:45 on all four cards; gs smoke 26 Sep)',
                         'pre-reboot': 'claims-v3 passes run before the machine fixes, 25 Sep 10:00-16:19 (kept as a pre-fix set)',
                         'campaign': 'claims-v3 campaign after the fixes, 25 Sep 17:23 - 26 Sep 06:55',
                         'gs-queue': 'E48 gathers and scatters, 26 Sep 03:19-09:22',
                         'pcie': 'E50 the host link, 27 Sep 14:24-15:13, five runs of about 14 s per card',
                         'hp': 'V3-HP heat placement: development on aifoundry3, validation on aifoundry1 card 1, '
                               "aifoundry2's two sessions (27-28 Sep)",
                         'dv2': 'E51 DV2 development night on aifoundry2, 28 Sep 00:40-02:54 (ended by the Master Minion hang)',
                         'dv2v': 'E51 DV2 validation on aifoundry2 under the frozen plan, from 28 Sep 20:45 (its read-only '
                                 'VZ readings every 3 min; a session starts only below the plan\'s temperature: three '
                                 'NAT-4 sessions ran, 22:13-23:56)',
                         'mp': 'the major pass, 28 Sep 23:47 - 29 Sep 01:06: E55 pcie2, E56 nocr, E57 memp2 and E58 tau, '
                               'development on aifoundry1 card 1, then validation on aifoundry3 (with their smoke passes)',
                         'oh': 'E53 the effect of overheating on aifoundry3 and aifoundry1 card 1, 28 Sep 10:11-12:05 (two pre-registered experiments)'}},
    'cards': [{'id': c, 'host': c.split('-')[0], 'label': {'aifoundry2': 'aifoundry2', 'aifoundry3': 'aifoundry3',
                                                            'aifoundry1-c0': 'aifoundry1 card 0', 'aifoundry1-c1': 'aifoundry1 card 1'}[c],
               **per_card[c]} for c in CARDS],
    'totals': {'card_hours_held_all_cards': round(sum(per_card[c]['card_hours_held'] for c in CARDS), 2),
               'card_hours_busy_all_cards': round(sum(per_card[c]['card_hours_busy'] for c in CARDS), 2),
               'card_hours_by_family': round_d(by_family), 'card_hours_by_experiment': round_d(by_E),
               'card_hours_by_phase': round_d(by_phase), 'intervals': len(intervals)},
    'queue_segments': [dict(card=q['card'], start=iso(q['start_ms']), end=iso(q['end_ms']),
                            schedule=re.sub(r'^.*?(?=tools/claims-v3/)', '', q['schedule']),
                            log=q['log'], stopped=q.get('stopped', False), unclosed=q.get('unclosed', False))
                       for q in sorted(queue_segments, key=lambda q: q['start_ms'])],
    'holds': hold_list,
    'intervals': intervals,
    'series': series,
    'crosscheck_03_experiments': cross,
    'crosscheck_block_json': {'blocks': len(blocks), 'matched_to_log': len(blocks) - len(block_unmatched),
                              'unmatched_added_as_intervals': [b['file'] for b in block_unmatched],
                              'median_start_delta_s': sorted(d[0] for d in deltas)[len(deltas) // 2] if deltas else None,
                              'median_end_delta_s': sorted(d[1] for d in deltas)[len(deltas) // 2] if deltas else None,
                              'max_abs_start_delta_s': max((abs(d[0]) for d in deltas), default=None),
                              'queue_state_rows': len(qstate), 'queue_state_rows_without_log_match': qs_unmatched},
    'undated': undated,
    'events': events,
    'problems': problems,
}
json.dump(out, open(os.path.join(TL, 'cards.json'), 'w'), indent=1, ensure_ascii=False)

# ---------------------------------------------------------------- report
print('intervals', len(intervals), 'holds', len(hold_list))
for c in CARDS:
    print(c, per_card[c])
print('by family'); [print('  ', k, v) for k, v in round_d(by_family).items()]
print('by phase', round_d(by_phase))
print('series max', series['max'], series['minutes_with'], 'start', series['start'], 'n', nmin)
print('block.json', out['crosscheck_block_json'] | {'unmatched_added_as_intervals': len(block_unmatched)})
print('queue segments')
for q in out['queue_segments']:
    print('  ', q['card'], q['start'], q['end'], q['schedule'].split('/')[-1], 'STOP' if q['stopped'] else '', 'UNCLOSED' if q['unclosed'] else '')
print('problems', len(problems)); [print('  ', p) for p in problems[:20]]
print('crosscheck')
for r in cross:
    print('  ', r['E'], (r.get('stated') or '')[:45], '|', r.get('data_start', '')[5:16], r.get('data_end', '')[5:16], r.get('cards', ''),
          'd0', r.get('start_diff_min'), 'd1', r.get('end_diff_min'), r.get('no_card_time', '')[:30], 'UNDATED' if r.get('undated') else '')
