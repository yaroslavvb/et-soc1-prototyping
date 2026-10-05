#!/usr/bin/env python3
"""Join the session extracts into the data of the session-timeline page.

    tools/timeline/build_timeline_data.py [data_dir]

data_dir (default docs/reports/data/2026-09-27-session-timeline) holds the seven extracts, copied there from
$TIMELINE_DIR, where the extraction scripts of this folder wrote them (then sanitize_extracts.py removes from them
what the page withholds; README.md gives the whole pipeline):

  human.json          extract_main.py      the owner's inputs (123 at the 29 Sep 02:14 snapshot, 5 of them from a page's
                                           Talk tab): time, category, a hand-written summary of at most 12 words (never
                                           the text), estimated reading + typing time; engagement sessions
  main_agent.json     extract_main.py      the main agent's busy intervals, tokens per message, compactions, limits,
                                           and the gaps it spent only watching its own workflows (idle)
  agents.json         extract_agents.py    every subagent transcript (workflow agents, Agent-tool agents, forks), the
                                           workflow runs, and per-minute counts of busy agents
  cards.json          build_cards.py       every interval in which a card was held by a measurement (host queue logs,
                                           claims-v3 block records, the earlier experiments' data files)
  artifacts.json      scan_spacesheep.py + build_artifacts.py: every spacesheep deploy and every commit
  tokens_by_time.json tokens_by_time.py    tokens per PDT day, main agent vs subagents (by kind)
  card_calls.json     extract_card_calls.py the main agent's own commands that ran a program on a card (development
                                           and debug runs, which left no timestamped data file)
  neighbors.json      extract_neighbors.py  the neighbor sessions (other Claude sessions on the lab's machine, from 30 Sep):
                                           their busy time, the owner's messages to them (summaries), their key events,
                                           and the hosts down (the link-retrain hang and the power cycle); optional

agents.json's own 'main' block was computed from an earlier main_agent.json, before loops that only watched the
agent's workflows counted as idle: the page takes the main agent's busy intervals from main_agent.json (and only the
strict 3-minute intervals, which that rule does not change, from agents.json).

The extraction scripts read the session's transcripts and the lab machines' logs, which are not in the repository;
this generator needs only the seven extracts, so the page rebuilds from committed inputs. It writes timeline.json in
data_dir. Times in timeline.json are seconds since 19 Sep 2026 00:00 PDT (UTC-7; no DST change in the week).

Privacy (the page is public): the owner's messages appear only as the extract's summaries; the report for the lab
lead's workflows, agents and deploys are unnamed and unlinked ("a report for the lab lead"); private and outside pages
are grouped without titles; commit subjects that mention that report are replaced by a neutral line; the privacy
table's sanitize rules apply to every string read and written, and timeline.json is not written if the scan finds
anything (sanitize_extracts.py, applied here again to what is read; tools/timeline/README.md, "The sanitize rule").
"""
import collections, datetime, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402
from sanitize_extracts import (PRIVATE, compiled, public_spaces, sanitize_agents, sanitize_artifacts,  # noqa: E402
                               sanitize_tree, scan_text, subject as subj)

DD = sys.argv[1] if len(sys.argv) > 1 else paths.DATA_DIR
L = lambda f: sanitize_tree(json.load(open(os.path.join(DD, f))))
H, M, A, C, R, TK, CC = (L('human.json'), L('main_agent.json'), L('agents.json'), L('cards.json'), L('artifacts.json'),
                         L('tokens_by_time.json'), L('card_calls.json'))
N = L('neighbors.json') if os.path.exists(os.path.join(DD, 'neighbors.json')) else {'sessions': [], 'hosts': []}
sanitize_agents(A)
sanitize_artifacts(R)

PDT = datetime.timezone(datetime.timedelta(hours=-7))
T0 = datetime.datetime(2026, 9, 19, 0, 0, tzinfo=PDT)
T0MS = int(T0.timestamp() * 1000)
DAY = 86400
# the whole-week view: Sat 19 Sep 06:00 PDT to the hour after the snapshot (the main transcript's last line, or the
# subagents' extraction when that is later: their transcripts go on while the main agent waits on them)
_SNAP = max(datetime.datetime.fromisoformat(H['transcript_last_ts'].replace('Z', '+00:00')),
            datetime.datetime.fromisoformat(A['generated'].replace('Z', '+00:00')))
FULL = [6 * 3600, (int((_SNAP - T0).total_seconds() // 3600) + 1) * 3600]
DAYS = [(T0 + datetime.timedelta(days=d)).strftime('%a ') + str((T0 + datetime.timedelta(days=d)).day)
        for d in range(-(-FULL[1] // DAY))]


def rel(ts):
    """ISO time (Z or offset) or epoch ms -> seconds since T0, one decimal."""
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return round((ts - T0MS) / 1000, 1)
    d = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
    return round((d - T0).total_seconds(), 1)


def clock(t):
    d = int(t // DAY)
    s = int(t % DAY)
    mon = (T0 + datetime.timedelta(days=d)).strftime('%b')   # Sep, and Oct from day 12 (1 October)
    return f'{DAYS[d] if 0 <= d < len(DAYS) else "?"} {mon} {s // 3600:02d}:{s % 3600 // 60:02d}'


def union(iv):
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def overlap(iv, a, b):
    return sum(max(0, min(e, b) - max(s, a)) for s, e in iv)


def rle(arr):
    out = []
    for v in arr:
        if out and out[-1][0] == v:
            out[-1][1] += 1
        else:
            out.append([v, 1])
    return out


out = {'meta': {
    't0_utc': T0.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'tz': 'America/Los_Angeles (PDT, UTC-7)',
    'full': FULL, 'days': DAYS,
    'session_start': rel(H['transcript_first_ts']),
    'snapshot_end': rel(_SNAP.isoformat()),
    'agents_snapshot': rel(A['generated']),
    'generated': {'human': H['generated_utc'], 'main': M['generated_utc'], 'agents': A['generated'],
                  'cards': C['generated'], 'artifacts': R['generated'], 'tokens': TK['generated'],
                  'card_calls': CC['generated'], 'neighbors': N.get('generated')},
}}

# ------------------------------------------------------------------ human
CATS = ['request', 'correction', 'approval/answer', 'question', 'status']
KINDS = ['prompt', 'midturn', 'slash-command', 'question-answer', 'interrupt', 'talk']
msgs = []
for m in H['messages']:
    msgs.append([rel(m['ts']), round(m['active_s'], 1), round(m['active_s_paste_adjusted'], 1), CATS.index(m['category']),
                 KINDS.index(m['kind']), m['summary'], m['request_id'], m['chars'], round(m['read_s'], 1),
                 round(m['type_s'], 1), 1 if m['likely_paste'] else 0, m.get('text'), m.get('removed') or [],
                 m.get('images') or 0])
sessions = [[rel(s['start_est']), rel(s['end']), s['n'], round(s['active_s'], 1), round(s['active_s_paste_adjusted'], 1)]
            for s in H['engagement_sessions']]
ht = H['totals']
out['human'] = {
    'cats': CATS, 'kinds': KINDS,
    'cols': ['t', 'active_s', 'active_paste_s', 'cat', 'kind', 'summary', 'request', 'chars', 'read_s', 'type_s', 'paste',
             'text', 'removed', 'images'],
    'msgs': msgs, 'sessions': sessions,
    'totals': {'n': H['counts']['inputs'], 'chars': ht['chars'], 'active_h': round(ht['active_s'] / 3600, 2),
               'active_paste_h': round(ht['active_s_paste_adjusted'] / 3600, 2),
               'read_h': round(ht['read_s'] / 3600, 2), 'type_h': round(ht['type_s'] / 3600, 2),
               'engagement_h': round(ht['engagement_span_s'] / 3600, 2), 'sessions': len(sessions),
               'by_category': H['counts']['by_category'], 'by_kind': H['counts']['by_kind']},
    'rules': {k: H['rules'][k] for k in ('typing_s', 'read_s', 'active_s', 'active_s_paste_adjusted', 'engagement_sessions')},
}

# ------------------------------------------------------------------ main agent
TRIG = ['human', 'task-notification', 'agent-message', 'compact-continuation', 'interrupt', 'continuation', 'watch-loop']
busy = []
for b in M['busy_intervals']:
    busy.append([rel(b['start']), rel(b['end']), TRIG.index(b['trigger']) if b['trigger'] in TRIG else 5,
                 b['tokens_total'], b['n_tool_calls'], b['n_assistant_messages'], round(b['active_s']),
                 round(b['tool_wait_s']), round(b['model_wait_s'] + b['compaction_s']), round(b['tool_wait_lab_s'])])
strict = [[rel(a), rel(b)] for a, b in A['main']['busy_strict']]
mt = M['totals']
out['main'] = {
    'triggers': TRIG,
    'cols': ['s', 'e', 'trigger', 'tokens', 'tool_calls', 'messages', 'active_s', 'tool_wait_s', 'other_wait_s', 'tool_wait_lab_s'],
    'busy': busy, 'strict': strict,
    'watch': [[rel(a), rel(b)] for a, b in M['watch_waits']],
    'compactions': [rel(c['ts']) for c in M['compactions']],
    'limits': [[rel(r['ts']), 'weekly limit' if 'weekly' in r['message'] else 'session limit'] for r in M['rate_limit_stops']],
    'totals': {'busy_h': round(mt['busy_s'] / 3600, 2), 'strict_h': round(A['main']['busy_strict_min'] / 60, 2),
               'tool_wait_h': round(mt['tool_wait_s'] / 3600, 2), 'tool_wait_lab_h': round(mt['tool_wait_lab_s'] / 3600, 2),
               'watch_h': round(mt['watch_wait_s'] / 3600, 2), 'messages': mt['messages'],
               'tool_calls': M['counts']['tool_calls'], 'intervals': len(busy), 'compactions': len(M['compactions'])},
    'rules': {'busy': M['rules']['busy_interval'], 'strict': A['busy_rule'], 'tool_class': M['rules']['tool_class']},
}

# ------------------------------------------------------------------ subagents and workflows
cc = A['concurrency']
c0 = rel(cc['start'])
# the same per-minute count split three ways: agents that ended on an error or failed (most of them starts that hit a
# usage limit within their first minute), and the other workflow and Agent-tool agents; the three add up to wf + tool
g0 = datetime.datetime.fromisoformat(cc['start'].replace('Z', '+00:00'))
okwf, oktool, fail = [0] * cc['n'], [0] * cc['n'], [0] * cc['n']
for a in A['agents']:
    arr = fail if (a['error_kind'] or a['status'] in ('failed', 'error')) else okwf if a['kind'] == 'workflow' else oktool
    seen = set()
    for s_, e_ in a['busy']:
        i0 = int((datetime.datetime.fromisoformat(s_.replace('Z', '+00:00')) - g0).total_seconds() // 60)
        i1 = int((datetime.datetime.fromisoformat(e_.replace('Z', '+00:00')) - g0).total_seconds() // 60)
        seen.update(range(max(0, i0), min(cc['n'] - 1, i1) + 1))
    for i in seen:
        arr[i] += 1
assert all(okwf[i] + oktool[i] + fail[i] == cc['workflow_busy'][i] + cc['agent_tool_busy'][i] for i in range(cc['n'])), \
    'the split does not add up to the concurrency series'
assert max(o + t for o, t in zip(okwf, oktool)) == A['peak']['subagents_excluding_errored']['value']
out['conc'] = {'start': c0, 'step': cc['step_s'], 'n': cc['n'],
               'wf': rle(cc['workflow_busy']), 'tool': rle(cc['agent_tool_busy']),
               'okwf': rle(okwf), 'oktool': rle(oktool), 'fail': rle(fail),
               'note': cc['note'] + '; wf = workflow agents, tool = Agent-tool agents and forks (both counting every '
                                    'agent); okwf, oktool = the same without the agents that failed or ended on an error, '
                                    'fail = those (okwf + oktool + fail = wf + tool)'}
WF = []
wf_index = {}
for w in sorted(A['workflows'], key=lambda w: w['first_event']):
    wf_index[w['run_id']] = len(WF)
    summary = w.get('summary') or ''
    WF.append({'name': w['name'], 'private': w['private'], 'status': w['status'], 'resumed': w['resumed'],
               's': rel(w['first_event']), 'e': rel(w['last_event']), 'launches': [rel(t) for t in w['launches']],
               'agents': w['agents'], 'states': w['agent_states'], 'busy_min': w['busy_agent_min'],
               'tokens': w['tokens'], 'tool_calls': w['tool_calls'], 'summary': '' if w['private'] else summary,
               'phases': [] if w['private'] else w['phases']})
STAT = ['done', 'running', 'failed', 'error', 'killed']
AK = ['workflow', 'agent', 'fork']
groups = collections.OrderedDict()
agents = []
for a in sorted(A['agents'], key=lambda a: (a['start'] or '', a['id'])):
    if not a['start']:
        continue
    g = a['workflow_run'] if a['workflow_run'] in wf_index else ('tool' if a['kind'] != 'workflow' else 'unknown')
    wi = wf_index.get(a['workflow_run'], -1)
    priv = wi >= 0 and WF[wi]['private']
    label = f'agent of {PRIVATE}' if priv else (a['label'] or a['description'] or a['id'])
    iv = [[rel(s), rel(e)] for s, e in a['busy']]
    agents.append({'g': g, 's': rel(a['start']), 'e': rel(a['end']), 'wf': wi, 'label': label,
                   'phase': None if priv else a['phase'], 'status': STAT.index(a['status']) if a['status'] in STAT else 2,
                   'kind': AK.index(a['kind']), 'busy_min': a['busy_min'], 'tokens': a['tokens']['total'],
                   'out_tokens': a['tokens']['output'], 'tools': a['tool_calls'], 'iv': iv,
                   'err': a.get('error_kind')})
# lanes: greedy packing inside each group (an agent takes the first lane free at its start)
for a in agents:
    groups.setdefault(a['g'], []).append(a)
G = []
for gk, lst in groups.items():
    ends = []
    for a in sorted(lst, key=lambda a: a['s']):
        for k, e in enumerate(ends):
            if e <= a['s'] - 30:
                ends[k] = a['e']
                a['lane'] = k
                break
        else:
            a['lane'] = len(ends)
            ends.append(a['e'])
    if gk == 'tool':
        name, wi = 'Agent tool: agents and forks', -1
    else:
        wi = wf_index.get(gk, -1)
        name = WF[wi]['name'] if wi >= 0 else 'unknown workflow'
    G.append({'key': gk, 'name': name, 'wf': wi, 'lanes': len(ends), 's': min(a['s'] for a in lst),
              'e': max(a['e'] for a in lst), 'n': len(lst)})
G.sort(key=lambda g: g['s'])
gidx = {g['key']: i for i, g in enumerate(G)}
out['agents'] = {
    'status': STAT, 'kinds': AK,
    'cols': ['s', 'e', 'group', 'lane', 'wf', 'label', 'phase', 'status', 'kind', 'busy_min', 'tokens', 'out_tokens',
             'tool_calls', 'busy (flat s,e,...)'],
    'rows': [[a['s'], a['e'], gidx[a['g']], a['lane'], a['wf'], a['label'], a['phase'], a['status'], a['kind'],
              a['busy_min'], a['tokens'], a['out_tokens'], a['tools'], [x for p in a['iv'] for x in p]] for a in agents],
    'groups': G, 'workflows': WF,
    'peak': {k: {'value': v['value'], 't': rel(v['first_minute'])} for k, v in A['peak'].items()},
}
at = A['totals']
out['agents']['totals'] = {
    'agents': at['agents'], 'by_kind': at['agents_by_kind'], 'workflow_runs': at['workflow_runs'],
    'workflow_launch_calls': at['workflow_launch_calls'], 'agent_tool_calls_in_main': at['agent_tool_calls_in_main'],
    'busy_agent_h': at['busy_agent_hours_subagents'], 'tool_calls': at['tool_calls_subagents'],
    'status': dict(collections.Counter(a['status'] for a in A['agents'])),
    'running_workflows': [w['name'] for w in A['workflows'] if w['status'] == 'running'],
}

# ------------------------------------------------------------------ tokens
def tk(d):
    return {k: d.get(k, 0) for k in ('input', 'cache_creation', 'cache_read', 'output', 'total')}
per_day = {}
for day, v in TK['per_day_pdt'].items():
    per_day[day] = {cls: tk(x) for cls, x in v.items()}
out['tokens'] = {
    'totals': {'main': tk(at['tokens_main']), 'subagents': tk(at['tokens_subagents']), 'all': tk(at['tokens_all']),
               'workflow': tk(at['tokens_subagents_by_kind']['workflow']), 'agent': tk(at['tokens_subagents_by_kind']['agent']),
               'fork': tk(at['tokens_subagents_by_kind']['fork'])},
    'per_day': per_day,
    'per_day_check': {'subagents_sum_per_day': TK['check']['subagents_total_here'],
                      'subagents_total': TK['check']['subagents_total_agents_json']},
    'rule': A['token_rule'] + '; the input, cache-write, cache-read and output counts are the usage fields that the API '
            'returned with each assistant message, as the transcripts record them. Per day: ' + TK['rule'],
}

# ------------------------------------------------------------------ cards
CARD_IDS = ['aifoundry2', 'aifoundry3', 'aifoundry1-c1', 'aifoundry1-c0']
FAMS = [  # family groups, in time order; members are cards.json families; 'dev' comes from card_calls.json
    ('early', 'Experiments 19–22 Sep: first measurements, power and the Horace experiment, DVFS, hot line, relay',
     ['First measurements: matmul, sparsity, memory, NoC (18-20 Sep)', 'Power, temperature and Horace (20-22 Sep)',
      'DVFS, leakage, governor (22 Sep)', 'Hot line and on-chip relay (22 Sep)']),
    ('energy', 'Energy manual: catalogue and reruns (23 Sep)', ['Energy manual catalogue and reruns (23 Sep)']),
    ('heat', 'Heat per millimetre (24 Sep)', ['Heat per millimetre (24 Sep)']),
    ('pre', 'Claims check v3: the passes before the fixes (25 Sep)', ['Claims check v3: pre-reboot campaign (25 Sep 10:00-16:19)']),
    ('campaign', 'Claims check v3: the campaign after the fixes (25–26 Sep)', ['Claims check v3: campaign after the fixes (25-26 Sep)']),
    ('gs', 'Gathers and scatters, E48 (26 Sep)', ['Gathers and scatters, E48 (26 Sep)']),
    ('pcie', 'The host link, E50 (27 Sep)', ['The host link, E50 (27 Sep)']),
    ('hp', 'Heat placement: development on aifoundry3, then aifoundry1 card 1 and aifoundry2 (27–28 Sep)',
     ['Heat placement: development and validation (27-28 Sep)']),
    ('dv2', 'DV2: the governor and heat, development on aifoundry2 (28 Sep)', ['DV2: the governor and heat, development (28 Sep)']),
    ('oh', 'The effect of overheating, E53, on aifoundry3 and aifoundry1 card 1 (28 Sep)', ['The effect of overheating, E53 (28 Sep)']),
    ('dv2v', 'DV2: the validation on aifoundry2 under the frozen plan (28–29 Sep)', ['DV2: the governor and heat, validation (28-29 Sep)']),
    ('mp', 'The major pass: E55–E58, development on aifoundry1 card 1, validation on aifoundry3 (28–29 Sep); E55–E57 on aifoundry2, the third card (29 Sep)',
     ['The major pass: E55-E58 (28-29 Sep)']),
    ('smoke', 'Claims check v3: smoke tests', ['Claims check v3: smoke tests (25-26 Sep)']),
    ('dev', 'Development and debug runs, from the transcripts (no data file)', []),
]
FAM_SHORT = {'early': '19–22 Sep experiments', 'energy': 'Energy manual (23 Sep)', 'heat': 'Heat per mm (24 Sep)',
             'pre': 'v3, before the fixes', 'campaign': 'v3 campaign after the fixes', 'gs': 'E48 gathers and scatters',
             'pcie': 'E50 host link', 'hp': 'heat placement', 'dv2': 'E51 DV2 development', 'oh': 'E53 overheating',
             'dv2v': 'E51 DV2 validation', 'mp': 'E55–E58, the major pass',
             'smoke': 'v3 smoke tests', 'dev': 'development runs (transcripts)'}
DEV = [k for k, _, _ in FAMS].index('dev')
fam_of = {m: i for i, (_, _, ms) in enumerate(FAMS) for m in ms}
missing = sorted({iv['family'] for iv in C['intervals']} - set(fam_of))
if missing:
    raise SystemExit(f'families without a group: {missing}')
sess0 = out['meta']['session_start']
sess0_ms = T0MS + int(sess0 * 1000)


def hours(ivs, bridge=0):
    u = []
    for a, b in sorted(ivs):
        if u and a - u[-1][1] < bridge:
            u[-1][1] = max(u[-1][1], b)
        else:
            u.append([a, b])
    return u


def minus(a, b, cover):
    """the parts of [a, b] that no interval of cover (sorted, disjoint) covers"""
    parts, cur = [], a
    for x, y in cover:
        if y <= cur or x >= b:
            continue
        if x > cur:
            parts.append([cur, x])
        cur = max(cur, y)
    if cur < b:
        parts.append([cur, b])
    return parts


civ = []
ms_iv = collections.defaultdict(list)   # card -> [start_ms, end_ms] of every interval (the in-use series)
for iv in C['intervals']:
    s, e = rel(iv['start_ms']), rel(iv['end_ms'])
    if e <= sess0:
        continue  # 18 September: before the session
    k = CARD_IDS.index(iv['card'])
    civ.append([k, max(s, sess0), e, fam_of[iv['family']], iv['E'], iv['label'], iv['name'], iv['status'], iv.get('die_c_start')])
    ms_iv[k].append([max(iv['start_ms'], sess0_ms), iv['end_ms']])
# development and debug runs: the main agent's own commands on a card (card_calls.json), less what a data file or a
# queue log already covers on that card; exact pieces count as busy, and pieces under 2 min apart form one run (held)
dev_pieces = collections.defaultdict(list)
calls_by_card = collections.defaultdict(list)
for c_s, c_e, card, prog in CC['calls']:
    calls_by_card[CARD_IDS.index(card)].append((rel(c_s), rel(c_e), prog, c_s, c_e))
dev_n = 0
for k, calls in calls_by_card.items():
    cover = hours([[r[1], r[2]] for r in civ if r[0] == k], 0)
    raw = hours([[a, b] for a, b, _, _, _ in calls], 0)
    pieces = [p for a, b in raw for p in minus(a, b, cover) if p[1] - p[0] >= 1]
    dev_pieces[k] = pieces
    for a, b in hours(pieces, 120):
        inside = [x for x in calls if x[0] < b and x[1] > a]
        progs = collections.Counter(x[2] for x in inside).most_common()
        busy_s = sum(min(y, b) - max(x, a) for x, y in pieces if x < b and y > a)
        name = f'{len(inside)} command{"s" if len(inside) > 1 else ""}: ' + ', '.join(
            f'{p} ×{n}' if n > 1 else p for p, n in progs[:4]) + (', …' if len(progs) > 4 else '')
        civ.append([k, round(a, 1), round(b, 1), DEV, 'dev', 'Development or debug run (from the transcript)', name,
                    f'the tool calls took {round(busy_s)} s', None])
        dev_n += 1
    for x in pieces:   # the in-use series counts the exact pieces
        ms_iv[k].append([T0MS + int(x[0] * 1000), T0MS + int(x[1] * 1000)])
civ.sort(key=lambda r: (r[0], r[1]))
# card-hours from the intervals, since the session started: busy = exact union (a development run counts only its
# commands' own time); held = union bridging gaps < 2 min
per_card = []
for k, cid in enumerate(CARD_IDS):
    mine = [[r[1], r[2]] for r in civ if r[0] == k]
    exact = [[r[1], r[2]] for r in civ if r[0] == k and r[3] != DEV] + dev_pieces.get(k, [])
    held = hours(mine, 120)
    busy_u = hours(exact, 0)
    fam_h = [round(sum(max(0, e - s) for s, e in hours(dev_pieces.get(k, []) if f == DEV else
                                                      [[r[1], r[2]] for r in civ if r[0] == k and r[3] == f], 0)) / 3600, 3)
             for f in range(len(FAMS))]
    held_nodev = hours([[r[1], r[2]] for r in civ if r[0] == k and r[3] != DEV], 120)
    src = next(c for c in C['cards'] if c['id'] == cid)
    per_card.append({'id': cid, 'held_h': round(sum(e - s for s, e in held) / 3600, 2),
                     'busy_h': round(sum(e - s for s, e in busy_u) / 3600, 2), 'family_h': fam_h,
                     'held_h_without_dev': round(sum(e - s for s, e in held_nodev) / 3600, 2),
                     'intervals': len(mine), 'held_h_cards_json': src['card_hours_held_since_session_start']})
    assert abs(per_card[-1]['held_h_without_dev'] - src['card_hours_held_since_session_start']) < 0.011, per_card[-1]
# cards in use per minute, from the session start: cards.json's rule (a card counts in a minute that any of its
# intervals overlaps), with the development runs' exact pieces added; run-length encoded
ser = C['series']
s0_ms = int(datetime.datetime.fromisoformat(ser['start']).timestamp() * 1000)
first_min = int((sess0_ms - s0_ms) // 60000)
nmin = ser['n']


def in_use(ivs):
    busy_m = {k: bytearray(nmin) for k in range(len(CARD_IDS))}
    for k, lst in ivs.items():
        for a, b in lst:
            for i in range(max(int((a - s0_ms) // 60000), 0), min(int((b - s0_ms - 1) // 60000), nmin - 1) + 1):
                busy_m[k][i] = 1
    return [sum(busy_m[k][i] for k in busy_m) for i in range(nmin)]


# the rule reproduces cards.json's series from its own intervals (after the session start)
base = in_use({k: [[max(iv['start_ms'], sess0_ms), iv['end_ms']] for iv in C['intervals']
                   if CARD_IDS.index(iv['card']) == k and iv['end_ms'] > sess0_ms] for k in range(len(CARD_IDS))})
assert base[first_min:] == ser['values'][first_min:], 'in-use series differs from cards.json'
vals = in_use(ms_iv)[first_min:]
out['cards'] = {
    'ids': CARD_IDS, 'families': [{'key': k, 'label': lab, 'short': FAM_SHORT[k], 'members': ms} for k, lab, ms in FAMS],
    'dev': DEV,
    'cols': ['card', 's', 'e', 'family', 'E', 'label', 'name', 'status', 'die_c_start'],
    'intervals': civ, 'per_card': per_card,
    'inuse': {'start': rel(s0_ms) + first_min * 60, 'step': 60, 'rle': rle(vals),
              'minutes_with': collections.Counter(vals).most_common()},
    'totals': {'held_h': round(sum(p['held_h'] for p in per_card), 2), 'busy_h': round(sum(p['busy_h'] for p in per_card), 2),
               'held_h_without_dev': round(sum(p['held_h_without_dev'] for p in per_card), 2),
               'dev_runs': dev_n, 'dev_calls': len(CC['calls']),
               'dev_busy_h': round(sum(sum(b - a for a, b in v) for v in dev_pieces.values()) / 3600, 2),
               'held_h_incl_18sep': C['totals']['card_hours_held_all_cards'],
               'minutes_by_count': {str(k): v for k, v in sorted(collections.Counter(vals).items())}},
    'rules': {'held': C['rules']['card_hours_held'], 'busy': C['rules']['card_hours_busy'], 'sources': C['rules']['sources'],
              'dev': CC['rule'] + ' The page keeps the parts of these calls that no other interval covers on that card.',
              'note': 'intervals before the session started (18 September) are left out; one that began before it is cut at its start'},
    'first_use': min(r[1] for r in civ),
    'undated': C['undated'],
}

# ------------------------------------------------------------------ artifacts
pages = []
pidx = {}
def page_key(p):
    return 'outside' if p['key'].startswith('outside-') else p['key']
for p in sorted([p for p in R['pages'] if p['deploys']], key=lambda p: p['first_deploy']):
    k = page_key(p)
    if k in pidx:
        pages[pidx[k]]['deploys'] += p['deploys']
        continue
    pidx[k] = len(pages)
    if k == 'outside':
        title, short = 'pages outside the ET-SoC-1 report set (tool debugging)', 'outside the set'
    elif k == 'lab-report':
        title, short = PRIVATE, 'lab-lead report'
    else:
        title = p['title']
        short = re.sub(r'^(\d{4}-\d{2}-\d{2}-)?et-soc1-', '', p.get('slug') or k)
    pages.append({'key': k, 'short': short, 'title': title, 'private': bool(p.get('private')), 'group': p['group'],
                  'deploys': p['deploys'], 'first': rel(p['first_deploy'])})
# a deploy the tool's output did not confirm, followed within 10 minutes by a first publish of the same page, is a
# failed attempt, not counted (on 25 Sep 16:34 the CLI's --json output was empty, and on 28 Sep 09:05 and 09:06 it
# could not reach the host; each space was then created fresh); a page's first deploy is its first counted one
failed = []
deploys = []
for d in R['deploys']:
    t = rel(d['ts'])
    if not d['confirmed'] and any(x['page'] == d['page'] and x['new_space'] and 0 < rel(x['ts']) - t < 600 for x in R['deploys']):
        failed.append([t, pidx[page_key({'key': d['page']})]])
        continue
    deploys.append([t, pidx[page_key({'key': d['page']})], 1 if d['new_space'] else 0, 1 if d['confirmed'] else 0])
for k, pg in enumerate(pages):
    pg['deploys'] = sum(1 for x in deploys if x[1] == k)
    pg['first'] = min((x[0] for x in deploys if x[1] == k), default=pg['first'])
SESS = ['this session', 'another session', 'none recorded', 'the neighbor session']
NB_SHAS = {sha for n in N['sessions'] for sha in n.get('commits', [])}
commits = []
for c in R['commits']:
    sess = 'this session' if c['claude_session'] == 'this session' else ('another session' if 'another' in c['claude_session'] else 'none recorded')
    if c['sha'] in NB_SHAS:
        sess = 'the neighbor session'
    br = next((b for b in ('main', 'origin/main') if b in c['branches']), c['branches'][0] if c['branches'] else '')
    br = 'another session’s branch' if br.startswith('other-session') else br
    commits.append([rel(c['ts']), c['sha'], subj(c['subject']), SESS.index(sess), br, c['files']])
out['artifacts'] = {
    'pages': pages, 'deploy_cols': ['t', 'page', 'new_space', 'confirmed'], 'deploys': deploys,
    'sessions': SESS, 'commit_cols': ['t', 'sha', 'subject', 'session', 'branch', 'files'], 'commits': commits,
    'failed_attempts': failed,
    'totals': {'deploys': len(deploys), 'new_spaces': sum(x[2] for x in deploys), 'pages': R['totals']['pages_deployed'],
               'commits': R['totals']['commits'], 'confirmed': sum(x[3] for x in deploys), 'failed_attempts': len(failed)},
    'rules': R['rules']['deploy'] + '; an unconfirmed deploy followed within 10 min by a first publish of the same page is '
                                    'a failed attempt and is not counted',
    'note': R['deploys_not_in_transcripts']['note'],
}

# ------------------------------------------------------------------ the neighbor sessions and the hosts down
out['neighbors'] = {
    'cols': {'msgs': ['t', 'category', 'kind', 'summary', 'text', 'removed', 'lost', 'session', 'chars'],
             'events': ['t', 'e', 'kind', 'title', 'text'],
             'hosts': ['cards', 's', 'e', 'kind', 'title', 'text']},
    'sessions': [{'id': n['id'], 'n': len(n.get('ids') or [n['id']]), 'lane': n.get('lane') or 'neighbor', 'name': n['name'],
                  'title': n['title'],
                  's': rel(n['first']), 'e': rel(n['last']),
                  'busy': [[rel(a), rel(b)] for a, b in n['busy']], 'sub': [[rel(a), rel(b)] for a, b in n['sub']],
                  'busy_h': n['busy_h'], 'agent_h': n['agent_h'], 'agents': n['agents'], 'workflow_runs': n['workflow_runs'],
                  'tokens': n['tokens']['total'], 'deploys': n['deploys'], 'commits': n['commits'],
                  'msgs': [[rel(m['ts']), CATS.index(m['category']), KINDS.index(m['kind']), m['summary'], m.get('text'),
                            m.get('removed') or [], 1 if m.get('lost') else 0, m.get('session') or n['id'], m.get('chars', 0)]
                           for m in n['messages']],
                  'events': [[rel(e['t']), rel(e['e'] or e['t']), e['kind'], e['title'], e['text']] for e in n['events']]}
                 for n in N['sessions']],
    'hosts': [[[CARD_IDS.index(c) for c in h['cards']], rel(h['s']), rel(h['e']), h['kind'], h['title'], h['text']] for h in N['hosts']],
    'rule': N.get('rule', ''),
}

# ------------------------------------------------------------------ per day
def day_of(t):
    return int(t // DAY)
perday = []
conc_wf = [v for v, n in out['conc']['wf'] for _ in range(n)]
conc_tool = [v for v, n in out['conc']['tool'] for _ in range(n)]
conc_ok = [a + b for a, b in zip(okwf, oktool)]
for d in range(len(DAYS)):
    a, b = d * DAY, (d + 1) * DAY
    key = (T0 + datetime.timedelta(days=d)).strftime('%Y-%m-%d')
    hm = [m for m in msgs if a <= m[0] < b]
    eng = sum(overlap([[s[0], s[1]]], a, b) for s in sessions)
    i0, i1 = int(max(0, (a - c0) // 60)), int(max(0, (b - c0) // 60))
    tot = [conc_wf[i] + conc_tool[i] for i in range(i0, min(i1, len(conc_wf)))]
    tok_ = conc_ok[i0:min(i1, len(conc_ok))]
    card_h = sum(overlap(hours([[r[1], r[2]] for r in civ if r[0] == k], 120), a, b) for k in range(4)) / 3600
    tday = per_day.get(key, {})
    perday.append({
        'day': d, 'label': DAYS[d], 'date': key,
        'human_n': len(hm), 'human_active_min': round(sum(m[1] for m in hm) / 60, 1),
        'human_active_paste_min': round(sum(m[2] for m in hm) / 60, 1), 'engagement_h': round(eng / 3600, 2),
        'main_busy_h': round(overlap([[x[0], x[1]] for x in busy], a, b) / 3600, 2),
        'main_strict_h': round(overlap(strict, a, b) / 3600, 2),
        'sub_agent_h': round(sum(overlap([[r['iv'][i][0], r['iv'][i][1]] for i in range(len(r['iv']))], a, b) for r in agents) / 3600, 2),
        'peak_sub': max(tot) if tot else 0, 'peak_sub_ok': max(tok_) if tok_ else 0,
        'card_h': round(card_h, 2),
        'deploys': sum(1 for x in deploys if a <= x[0] < b), 'commits': sum(1 for x in commits if a <= x[0] < b),
        'tokens_main': tday.get('main', {}).get('total', 0),
        'tokens_sub': sum(v['total'] for k, v in tday.items() if k != 'main'),
        'out_main': tday.get('main', {}).get('output', 0),
        'out_sub': sum(v['output'] for k, v in tday.items() if k != 'main'),
    })
out['perday'] = perday

# ------------------------------------------------------------------ highlights
def T(day, hm):
    h, m = map(int, hm.split(':'))
    return (day - 19) * DAY + h * 3600 + m * 60
def n_agents(a, b, kinds):
    return sum(1 for r in agents if a <= r['s'] <= b and AK[r['kind']] in kinds)
def card_h_between(a, b, fam=None):
    """held card-hours (gaps under 2 min bridged, as cards.json counts them) inside [a, b]; for a whole family,
    cards.json's own family total"""
    if fam is not None:
        return sum(C['totals']['card_hours_by_family'][m] for m in FAMS[fam][2])
    return sum(overlap(hours([[r[1], r[2]] for r in civ if r[0] == k], 120), a, b) for k in range(4)) / 3600
lo = next(w for w in WF if w['name'] == 'limits-of-observability')
camp = [r for r in civ if FAMS[r[3]][0] == 'campaign']
camp_s, camp_e = min(r[1] for r in camp), max(r[2] for r in camp)
gs = [r for r in civ if FAMS[r[3]][0] == 'gs']
gs_s, gs_e = min(r[1] for r in gs), max(r[2] for r in gs)
peak = A['peak']['subagents']
peak_t = rel(peak['first_minute'])
viz_a, viz_f = n_agents(T(25, '23:20'), T(26, '00:10'), ['agent']), n_agents(T(25, '23:20'), T(26, '00:10'), ['fork'])
v3_a, v3_f = n_agents(T(26, '07:00'), T(26, '08:45'), ['agent']), n_agents(T(26, '07:00'), T(26, '08:45'), ['fork'])
review = [w for w in WF if w['name'] in ('audit-measurement-reports', 'fix-measurement-reports', 'fix-reports-round2', 'fix-reports-round3')]
night = [w for w in WF if w['name'] in ('validate-reports-v2', 'implement-plan2', 'finish-plan2', 'polish-reports')]
peak_in = lambda a, b: max([conc_wf[i] + conc_tool[i] for i in range(int((a - c0) // 60), int((b - c0) // 60))] or [0])
e1 = next(r for r in civ if r[4] == 'E1')
e20 = next(r for r in civ if r[4] == 'E20')
calls_t = [(rel(c[0]), c[3]) for c in CC['calls']]
first_call = calls_t[0][0]
first_probe = next(t for t, prog in calls_t if prog == 'memprobe_host')
a3_first = min(r[1] for r in civ if CARD_IDS[r[0]] == 'aifoundry3')
page_first = {pg['key']: pg['first'] for pg in pages}
# the minute of the peak: how many of its agents started in it, and how many failed
pk_m0 = datetime.datetime.fromisoformat(A['peak']['subagents']['first_minute'].replace('Z', '+00:00'))
pk_ag = [a for a in A['agents'] if any(datetime.datetime.fromisoformat(x.replace('Z', '+00:00')) < pk_m0 + datetime.timedelta(minutes=1)
                                       and datetime.datetime.fromisoformat(y.replace('Z', '+00:00')) >= pk_m0 for x, y in a['busy'])]
pk_started = sum(1 for a in pk_ag if datetime.datetime.fromisoformat(a['start'].replace('Z', '+00:00')) >= pk_m0)
pk_failed = sum(1 for a in pk_ag if a['error_kind'] or a['status'] in ('failed', 'error'))
assert len(pk_ag) == A['peak']['subagents']['value'], (len(pk_ag), A['peak']['subagents']['value'])
out['agents']['peak_minute'] = {'n': len(pk_ag), 'started_in_it': pk_started, 'failed': pk_failed}
four_runs = []
for i, n in enumerate(vals):
    if n == 4:
        t = out['cards']['inuse']['start'] + i * 60
        if four_runs and four_runs[-1][1] == t:
            four_runs[-1][1] = t + 60
        else:
            four_runs.append([t, t + 60])
lim = [l for l in out['main']['limits'] if l[1] == 'weekly limit']
lim_t = next(l[0] for l in lim if day_of(l[0]) == 7)   # the first weekly limit of 26 Sep (another hit on 29 Sep: below)
pause_end = T(27, '11:00')
pause_cards = max(r[2] for r in civ if lim_t <= r[2] <= pause_end)
pause_other = sorted(c[0] for c in commits if lim_t <= c[0] <= pause_end and c[3] == SESS.index('another session'))
# 27-28 September
FAMK = [k for k, _, _ in FAMS]
wf27 = sorted([w for w in WF if T(27, '11:00') <= w['s'] <= T(27, '11:30')], key=lambda w: w['s'])
wfs = lambda names: [w for w in WF if w['name'] in names]
n_wf_agents = lambda names: sum(w['agents'] for w in wfs(names))
msg_of = lambda rx: [m for m in msgs if m[5] and re.search(rx, m[5])]
def commit_t(prefix):
    return min(c[0] for c in commits if c[2].startswith(prefix))
q58 = next(m for m in msgs if m[6] == 'Q58')
q59 = next(m for m in msgs if m[6] == 'Q59')
pcie = [r for r in civ if FAMK[r[3]] == 'pcie']
pcie_s, pcie_e = min(r[1] for r in pcie), max(r[2] for r in pcie)
n_pcie = len(pcie)
pcie_run_s = sum(r[2] - r[1] for r in pcie) / n_pcie
hp = [r for r in civ if FAMK[r[3]] == 'hp']
hp_s = min(r[1] for r in hp)
hp_a3_s = min(r[1] for r in hp if CARD_IDS[r[0]] == 'aifoundry3')
hp_a3_e = max(r[2] for r in hp if CARD_IDS[r[0]] == 'aifoundry3')
hp_a1_s = min(r[1] for r in hp if CARD_IDS[r[0]] == 'aifoundry1-c1')
hp_val_s = min(r[1] for r in hp if re.fullmatch(r'HP p9\d{3}', r[5]))
n_hp_a2 = len([r for r in hp if CARD_IDS[r[0]] == 'aifoundry2'])
n_hp_wf = len(wfs(['heat-placement-design', 'heat-placement-build', 'heat-placement-fix']))
hp_dec = msg_of(r'^Heat placement: allows')[0][0]
dv2 = [r for r in civ if FAMK[r[3]] == 'dv2']
dv2_s, dv2_e = min(r[1] for r in dv2), max(r[2] for r in dv2)
dv2_pass = lambda r: int(r[5].rsplit('p', 1)[1])
ran = [r for r in dv2 if r[7] != 'skipped']          # a pass skipped by its own rule never held the card
n_z1 = len([r for r in ran if 1000 <= dv2_pass(r) < 2000])
n_dv2_sess = len([r for r in ran if 6000 <= dv2_pass(r) < 7000])
n_dv2_smoke = len([r for r in ran if 4000 <= dv2_pass(r) < 5000])
ev = next(e for e in C['events'] if e['kind'] == 'MM-HANG')
hang = next(r for r in dv2 if dv2_pass(r) == ev['pass'])
hang_q_end = max(rel(q['end']) for q in C['queue_segments'] if q['card'] == ev['card'] and q.get('stopped')
                 and rel(q['start']) <= hang[1] <= rel(q['end']))
polish_req = msg_of(r'^Polish the diagram walkthroughs')[0][0]
zoom_req = msg_of(r'^Chip diagram zoom still jumps')[0][0]
poli_t = commit_t('Chip diagram: polish')
zoom_t = commit_t('Chip diagram: smooth zoom')
n_poli = n_wf_agents(['chip-diagram-polish'])
n_pp = n_wf_agents(['pages-viz-and-correctness'])
n_zoom = n_wf_agents(['chip-zoom-smoothness-diagnose'])
mem_req = msg_of(r'^Interactive diagrams for each memory level')[0][0]
n_mem = n_wf_agents(['memory-levels-interactive', 'memory-levels-integrate'])
stat_t = msg_of(r'^Asks for the status; finish every task')[0][0]
fin = next(w for w in WF if w['name'] == 'finish-everything')
fin_s, fin_e, n_fin = fin['s'], fin['e'], fin['agents']
hp_val = [r for r in hp if re.fullmatch(r'HP p9\d{3}', r[5])]
hp_val_e = max(r[2] for r in hp_val)
n_hp_val = len({r[5] for r in hp_val if r[7] not in ('failed', 'skipped')})
fix_t = msg_of(r'^Fix every lab problem that does not need')[0][0]
ok_sysfs = msg_of(r'^Approves resetting the hung card')[0][0]
ok_mgmt = msg_of(r'^Approves trying the management reset')[0][0]
req_t = msg_of(r'^Requests for the lab lead keep only')[0][0]
n_fix = n_wf_agents(['lab-host-fixes'])
n_req = n_wf_agents(['lab-report-requests'])
dev28 = [r for r in civ if r[3] == DEV and CARD_IDS[r[0]] == 'aifoundry2' and ok_sysfs - 600 <= r[1] <= ok_mgmt + 3600]
back_t = max(r[1] for r in dev28)                       # the management reset and the test kernel after it
oh = [r for r in civ if FAMK[r[3]] == 'oh']
oh_s, oh_e = min(r[1] for r in oh), max(r[2] for r in oh)
oh_req = msg_of(r'^Research overheating')[0][0]
n_oh = n_wf_agents(['effect-of-overheating'])
mob_req = msg_of(r'^The walkthrough is cut off on phones')[0][0]
n_mob = n_wf_agents(['mobile-walkthrough'])
mob_t = commit_t('Chip diagram and memory levels on phones')
ref_t = msg_of(r'^Refresh the session timeline')[0][0]
# 28 September, afternoon and evening
TALK = KINDS.index('talk')
talk_t = [m[0] for m in msgs if m[4] == TALK]
listen_t = msg_of(r'^Asks the agent to listen for messages')[0][0]
q62 = next(m for m in msgs if m[6] == 'Q62')[0]
q63 = next(m for m in msgs if m[6] == 'Q63')[0]
tints_t = commit_t('Memory levels: light tints')
bc_t = commit_t('Chip diagram: flow B, Broadcast')


def deploys_of(slug, after):
    k = pidx.get(slug)
    return sorted(x[0] for x in deploys if x[1] == k and x[0] >= after) if k is not None else []


bc_dep = deploys_of('et-soc1-chip-diagram', bc_t)[0]
sup_req = msg_of(r'^Pages still say energies superseded')[0][0]
sup_t = commit_t('Superseded energies folded into the pages')
sup_t2 = commit_t("Sparse compute's power from three cards")
n_sup = sum(1 for r in agents if sup_req <= r['s'] <= sup_t2 and re.match(r'(Fold newer energies|Sparse compute power)', r['label']))
sup_dep_t = deploys_of('et-soc1-memory-anatomy', sup_t)[0]
n_sup_dep = sum(1 for x in deploys if x[0] == sup_dep_t)
q63_t = commit_t('Heat per mm (Q63)')
q63_dep = deploys_of('et-soc1-heat-per-mm', q63_t)[0]
n_q63 = sum(1 for r in agents if q63 <= r['s'] <= q63 + 900 and AK[r['kind']] in ('agent', 'fork'))
cyan_req = msg_of(r'^Heat per mm: a light cyan background')[0][0]
cyan_dep = deploys_of('et-soc1-heat-per-mm', cyan_req)[0]
tl_notes = [msg_of(r'^Timeline: lead with what each message asked')[0][0], msg_of(r'^Timeline highlights should link')[0][0]]
major_t = msg_of(r'^Asks for a major pass')[0][0]
tl_dep = [x for x in deploys_of('et-soc1-session-timeline', ref_t) if x < major_t]   # the refresh and the owner's two notes
parity = msg_of(r'^Next: prototype a sparse-parity solver')
dv2v = [r for r in civ if FAMK[r[3]] == 'dv2v']
dv2v_read = [r for r in dv2v if r[2] - r[1] < 30]   # the plan's read-only temperature readings (about 1 s each)
lab_wf = next(w for w in WF if w['name'] == 'lab-pass-and-noc-design')
LAB_WHAT = {'NoC voltage control': 'the NoC’s voltage control', 'wire benchmark': 'a wire benchmark',
            'lab-wide audit': 'a lab-wide audit', 'lab tools': 'the lab tools'}
_lab_rows = [re.sub(r'^[A-Z]\d+\s+', '', r['label']) for r in sorted(agents, key=lambda r: r['label'])
             if r['wf'] >= 0 and WF[r['wf']] is lab_wf]
lab_labels = [LAB_WHAT[x] for x in _lab_rows if x in LAB_WHAT]            # the Understand phase, in order
lab_next = (', then designs the NoC-voltage experiment and its runner' if any(re.match(r'NV design', x) for x in _lab_rows)
            else ', then goes on' if len(lab_labels) < len(_lab_rows) else '')
snap_all = out['meta']['snapshot_end']
# 28-29 September: the major pass
tl_wf = next(w for w in WF if w['name'] == 'session-timeline-into-repo')
tl_repo_t = commit_t('The session timeline in the repository')
tl_repo_dep = deploys_of('et-soc1-session-timeline', major_t)
dv2v_nat = sorted([r for r in dv2v if r[2] - r[1] >= 30], key=lambda r: r[1])   # the replication sessions (17-38 min)
dv2v_red = next((c[0] for c in commits if c[2].startswith('E51 DV2 validation reduced')), None)
nv_t = commit_t('NV (the owner')
# a call's end: when its readings were in (the probe 22:53:45-22:54:02, the PCIe runner 23:55:35-23:56:09)
nv_probe = min(rel(c[1]) for c in CC['calls'] if c[2] == 'aifoundry3' and c[3] == 'dev_mngt_service' and rel(c[0]) >= major_t)
mp_all = [r for r in civ if FAMK[r[3]] == 'mp']
mp = [r for r in mp_all if CARD_IDS[r[0]] != 'aifoundry2']        # the night of 28-29 Sep
mp3 = [r for r in mp_all if CARD_IDS[r[0]] == 'aifoundry2']       # the third card, 29 Sep after DV2
mp_dev = [r for r in mp if CARD_IDS[r[0]] == 'aifoundry1-c1']
mp_val = [r for r in mp if CARD_IDS[r[0]] == 'aifoundry3']
mp_built = commit_t("The major pass's lab experiments")
n_mp_build = n_wf_agents(['lab-experiments-build'])
pcie_fix_run = min(rel(c[1]) for c in CC['calls'] if c[3] == 'run_pcie.sh' and rel(c[0]) >= major_t)
sp_req = parity[0][0] if parity else None
sp_res = next((w for w in WF if w['name'] == 'sparse-parity-research'), None)
sp_build = next((w for w in WF if w['name'] == 'sparse-parity-build'), None)
HL = [
    dict(t=out['meta']['session_start'], a=out['meta']['session_start'], b=T(19, '10:30'), track='human', title='The session starts',
         caption='Remote control on, the repository cloned, spacesheep set up; at 09:26 the first research request: '
                 'fine-grained power and latency observability.'),
    dict(t=first_call, a=out['meta']['session_start'], b=T(19, '10:30'), track='cards', title='The first card use',
         caption=f'At {clock(first_call)[-5:]} a code-loading test and hello world on aifoundry2; the first memory '
                 f'measurements at {clock(first_probe)[-5:]}; E1 at {clock(e1[1])[-5:]}, one memory access taken apart by '
                 f'stage and power rail. The first report, Anatomy of a memory access, went out at '
                 f'{clock(page_first["et-soc1-memory-anatomy"])[-5:]}.'),
    dict(t=peak_t, a=lo['s'] - 600, b=lo['e'] + 600, track='agents', title=f'{lo["agents"]} agents and a usage limit',
         caption=f'The limits-of-observability workflow started {lo["agents"]} agents, 10 to 15 at a time. At '
                 f'{clock(peak_t)[-5:]}, as the weekly usage limit hit, the count jumped to {peak["value"]} for one minute: '
                 f'{pk_started} agents started in that minute and {pk_failed} of the {peak["value"]} failed. '
                 'The run resumed at 11:04, after the reset, and stopped at the '
                 f'session limit at 11:36: {lo["states"].get("failed", 0) + lo["states"].get("error", 0)} of the '
                 f'{lo["agents"]} starts failed. The hub went live at 12:55.'),
    dict(t=T(21, '08:44'), a=T(20, '20:50'), b=T(21, '16:00'), track='cards', title='The Horace experiment',
         caption='A blog post’s random-matrix power experiment reproduced on the chip, rerun at one start temperature '
                 'and then with strict control; from 08:44 on 21 Sep runs of up to 10 minutes were allowed. '
                 f'{card_h_between(T(20, "20:50"), T(21, "16:00")):.1f} card-hours.'),
    dict(t=a3_first, a=T(22, '11:00'), b=T(22, '16:30'), track='cards', title='A second card',
         caption=f'aifoundry3 joins at {clock(a3_first)[-5:]} with checks of its clock governor; at {clock(e20[1])[-5:]} '
                 f'E20 repeats the strict protocol on it. The DVFS brief went out at '
                 f'{clock(page_first["et-soc1-dvfs-leakage"])[-5:]}; One hot line stops a shire '
                 f'({clock(page_first["et-soc1-hot-line"])[-5:]}) and the on-chip relay page '
                 f'({clock(page_first["et-soc1-on-chip-relay"])[-5:]}) followed that afternoon.'),
    dict(t=T(23, '08:17'), a=T(23, '07:30'), b=T(23, '16:10'), track='artifacts', title='The energy manual',
         caption='A hierarchical catalogue of what each operation costs: first edition 08:17, every instruction on two '
                 'cards by 11:28, confidence bars from reruns and cards by 13:50. '
                 f'{card_h_between(T(23, "07:30"), T(23, "16:10")):.1f} card-hours.'),
    dict(t=T(24, '16:11'), a=T(24, '13:00'), b=T(24, '16:30'), track='artifacts', title='Heat per millimetre',
         caption='Two workflows research the wire-energy question and try to refute the measurement; the report on '
                 'the mesh’s energy per bit·mm went live at 16:11.'),
    dict(t=T(24, '20:41'), a=min(w['s'] for w in review) - 600, b=T(24, '20:50'), track='agents', title='The report review',
         caption=f'An audit, a fix pass and two more fix rounds, {sum(w["agents"] for w in review)} workflow agents in all '
                 f'(up to {peak_in(T(24, "17:00"), T(24, "20:50"))} at once); 18 pages redeployed at 20:41 and again at 20:43.'),
    dict(t=T(25, '07:18'), a=min(w['s'] for w in night) - 600, b=T(25, '07:30'), track='agents', title='Validation overnight',
         caption='Every analysis re-run from raw data, then PLAN2: a shared chart toolkit, data regenerated and '
                 f'interactive charts, {sum(w["agents"] for w in night)} workflow agents through the night; 18 pages redeployed at 07:18.'),
    dict(t=T(25, '10:01'), a=T(25, '08:50'), b=T(25, '16:30'), track='cards', title='Claims check v3 begins',
         caption='Version 3 of the claims check, pre-registered at 09:08; its first passes ran on aifoundry2 and '
                 f'aifoundry3 from 10:01 ({card_h_between(0, 0, 3):.1f} card-hours before the '
                 'machine fixes, kept as a separate set).'),
    dict(t=T(25, '15:05'), a=T(25, '12:45'), b=T(25, '15:30'), track='artifacts', title='aifoundry1 fixed',
         caption='The broken lab machine troubleshot read-only from 12:56, a report at 14:16; fixed and its fix log '
                 'published at 15:05, made public at 15:12.'),
    dict(t=four_runs[0][0], a=T(25, '17:05'), b=T(25, '18:05'), track='cards', title='Four cards, then three',
         caption='aifoundry1’s two cards join at 17:12 (amendment A2). All four cards were in use at once for '
                 f'{round(sum(b - a for a, b in four_runs) / 60)} minutes in all ('
                 + ', '.join(clock(a)[-5:] + ('' if b - a <= 60 else '–' + clock(b)[-5:]) for a, b in four_runs[:-1])
                 + (' and ' if len(four_runs) > 1 else '') + clock(four_runs[-1][0])[-5:] +
                 '), in smoke tests and a temperature check of card 0; at 17:56 card 0 was excluded because it '
                 'overheats under load (A4).'),
    dict(t=camp_s, a=camp_s - 1800, b=camp_e + 1800, track='cards', title='The v3 campaign on three cards',
         caption=f'{clock(camp_s)[-5:]} on 25 Sep to {clock(camp_e)[-5:]} on 26 Sep: aifoundry2, aifoundry3 and '
                 f'aifoundry1 card 1 through the night, {card_h_between(0, 0, 4):.1f} card-hours of '
                 'pre-registered passes.'),
    dict(t=T(25, '23:15'), a=T(25, '22:45'), b=T(25, '23:45'), track='artifacts', title='The crash root cause',
         caption='aifoundry3’s host crashes traced to a log-level race in the runtime, reproduced without a card '
                 '(E49) and fixed at 23:15. At 06:16 on 26 Sep, 641 host processes of the fixed build ran on the '
                 'card without a crash.'),
    dict(t=T(26, '00:08'), a=T(25, '23:15'), b=T(26, '00:20'), track='agents', title='The visualization pass',
         caption=f'{viz_a} agents and {viz_f} forks survey the pages and add interactive charts (a card selector, '
                 'calculators, a claim scoreboard); 19 pages redeployed at 00:08.'),
    dict(t=gs_s, a=gs_s - 1200, b=gs_e + 1200, track='cards', title='Gathers and scatters (E48)',
         caption=f'Queued behind the campaign on three cards, {clock(gs_s)[-5:]} to {clock(gs_e)[-5:]} on 26 Sep: '
                 f'{card_h_between(0, 0, 5):.1f} card-hours.'),
    dict(t=T(26, '08:37'), a=T(26, '06:55'), b=T(26, '08:50'), track='agents', title='The three-card page updates',
         caption=f'{v3_a} agents and {v3_f} forks fold the campaign’s results into every page; ten commits at 08:37 '
                 'on the pages branch.'),
    dict(t=lim_t, a=T(26, '08:00'), b=T(27, '12:00'), track='agents', title='The weekly limit',
         caption=f'At {clock(lim_t)[-5:]} on 26 Sep the account reached its weekly usage limit, and this session’s agents '
                 f'paused until it reset at 11:00 on 27 Sep. The cards finished their queues by {clock(pause_cards)[-5:]}, '
                 f'and another Claude session made {len(pause_other)} commits that evening, '
                 f'{clock(pause_other[0])[-5:]} to {clock(pause_other[-1])[-5:]}.'),
    dict(t=T(27, '11:11'), a=T(27, '11:00'), b=T(27, '11:30'), track='human', title='Chip diagram and this timeline',
         caption='The owner asks for an interactive chip diagram for a talk, this timeline and experiments on heat '
                 f'placement; {len(wf27)} workflows start by {clock(wf27[-1]["s"])[-5:]}.'),
    dict(t=page_first['et-soc1-chip-diagram'], a=T(27, '11:10'), b=page_first['et-soc1-pcie-link'] + 900, track='artifacts',
         title='The chip diagram and the PCIe link',
         caption=f'An animated chip schematic for the talk went out at {clock(page_first["et-soc1-chip-diagram"])[-5:]}. '
                 f'The owner’s feedback at {clock(q58[0])[-5:]} asked, among other things, to measure the PCIe link it '
                 f'called “not measured”: E50 measured it on three cards, {clock(pcie_s)[-5:]} to {clock(pcie_e)[-5:]} '
                 f'({n_pcie} runs of about {pcie_run_s:.0f} s), and its page went out at {clock(page_first["et-soc1-pcie-link"])[-5:]} '
                 f'with the diagram’s second version (commit {clock(commit_t("Chip diagram v2"))[-5:]}).'),
    dict(t=hp_s, a=hp_s - 1800, b=hp_val_e + 1800, track='cards', title='Heat placement',
         caption='Does the thermal throttle follow the mean of the die’s sensors or one hot shire, and does the same work '
                 'placed at the die’s edges run longer before it? '
                 f'Designed, critiqued and pre-registered by {n_hp_wf} workflows; the owner’s decisions at '
                 f'{clock(hp_dec)[-5:]}. Development on aifoundry3 from {clock(hp_a3_s)[-5:]} to {clock(hp_a3_e)[-5:]}, '
                 f'then aifoundry1 card 1 from {clock(hp_a1_s)[-5:]}, its validation passes from {clock(hp_val_s)[-5:]} '
                 f'to {clock(hp_val_e)[-5:]}; aifoundry2 ran {n_hp_a2} short sessions, the first at {clock(hp_s)[-5:]}. '
                 f'{card_h_between(0, 0, FAMK.index("hp")):.1f} card-hours in all.'),
    dict(t=poli_t, a=T(27, '20:10'), b=zoom_t + 900, track='artifacts', title='The chip diagram polished',
         caption=f'At {clock(polish_req)[-5:]} the owner asks for a more professional walkthrough and zoom, then another '
                 f'pass over the pages: {n_poli} agents polish the diagram (motion, a visual system, the tour; commit '
                 f'{clock(poli_t)[-5:]}) while {n_pp} agents add charts and fix correctness across the observability '
                 f'pages (commit {clock(commit_t("Page pass"))[-5:]}). At {clock(zoom_req)[-5:]} the zoom still jumps; '
                 f'{n_zoom} agents trace it to the page’s own drawing, and the smooth zoom goes out at {clock(zoom_t)[-5:]}.'),
    dict(t=dv2_s, a=q59[0] - 600, b=hang_q_end + 1200, track='cards', title='DV2: the governor and heat',
         caption=f'At {clock(q59[0])[-5:]} the owner asks for another set of DVFS and heat experiments. Theories, a design '
                 f'and its critique came before any card work; the development night on aifoundry2 ran '
                 f'{clock(dv2_s)[-5:]} to {clock(dv2_e)[-5:]}: {n_z1} read-only watch cycles, {n_dv2_sess} sessions and '
                 f'{n_dv2_smoke} smoke launch{"es" if n_dv2_smoke > 1 else ""}, '
                 f'{card_h_between(0, 0, FAMK.index("dv2")):.1f} card-hours. Development only: the validation plan was '
                 'frozen afterwards'
                 + (f'; its queue started at {clock(min(r[1] for r in dv2v))[-5:]} on {DAYS[day_of(min(r[1] for r in dv2v))]} '
                    'Sep (the last highlight).' if dv2v else ' and has not run.')),
    dict(t=hang[2], a=hang[1] - 1200, b=hang_q_end + 1200, track='cards', title='aifoundry2 hangs',
         caption=f'In the DV2 session that began at {clock(hang[1])[-5:]}, aifoundry2’s Master Minion stopped taking '
                 'work: the second launch never started its kernel, and the next could not reach the command queue. '
                 f'The queue stopped at {clock(hang_q_end)[-5:]}. No reset was attempted then, by the lab’s rules; the '
                 f'card came back at {clock(back_t)[-5:]}, after the owner approved a reset (below).'),
    dict(t=page_first['et-soc1-memory-levels'], a=mem_req - 600, b=page_first['et-soc1-memory-levels'] + 900,
         track='artifacts', title='Memory levels, interactively',
         caption=f'At {clock(mem_req)[-5:]} the owner asks for an interactive diagram of each memory level, down to '
                 f'the transistors, with what nobody knows added to the asks for the team. {n_mem} agents in two workflows '
                 f'built them; the page went out at {clock(page_first["et-soc1-memory-levels"])[-5:]}, with the hub and '
                 'the chip diagram updated a minute later.'),
    dict(t=stat_t, a=stat_t - 600, b=fin_e + 600, track='human', title='The status, and every task at once',
         caption=f'At {clock(stat_t)[-5:]} the owner asks for the status and for parallel agents to finish every open '
                 f'task: a workflow of {n_fin} agents runs from {clock(fin_s)[-5:]} to {clock(fin_e)[-5:]} (the heat '
                 'report and its verdicts, a sweep of the review’s open items, an earlier refresh of this timeline, and '
                 'a rebuild on aifoundry1).'),
    dict(t=fix_t, a=fix_t - 600, b=back_t + 1200, track='human', title='Machine fixes, and aifoundry2 back',
         caption=f'At {clock(fix_t)[-5:]} the owner lets the machine-level fixes that were waiting go ahead: {n_fix} agents '
                 'export aifoundry3’s system log and raise its size cap, install the new card-holder and health-check '
                 'tools on the three machines, free 2.4 GB on aifoundry1 and stop orphaned browsers. The owner approves '
                 f'resetting the hung card at {clock(ok_sysfs)[-5:]}: the per-card sysfs reset re-attaches it but the '
                 f'Master Minion stays hung; after a second approval at {clock(ok_mgmt)[-5:]} the management reset brings '
                 f'it back at {clock(back_t)[-5:]}, and a test kernel runs cleanly. At {clock(req_t)[-5:]} the owner asks that the '
                 f'requests for the lab lead keep only what needs the team ({n_req} agents).'),
    dict(t=hp_val_e, a=hp_val_s - 1800, b=page_first['et-soc1-heat-placement'] + 1200, track='cards',
         title='Heat placement: the verdicts',
         caption=f'The validation on aifoundry1 card 1 ends at {clock(hp_val_e)[-5:]}: {n_hp_val} blocks, all valid. Short '
                 'bursts pass (the same work on the perimeter took 2.04 times as long to heat the die as in the '
                 'interior, 5 of 5 blocks); the primary sustained test is inconclusive (7 of its 10 runs met the 150 s '
                 'cap), so under the frozen rules no theory survived and none was refuted. The report goes out at '
                 f'{clock(page_first["et-soc1-heat-placement"])[-5:]}.'),
    dict(t=oh_s, a=oh_req - 600, b=page_first['et-soc1-effect-of-overheating'] + 1200, track='cards',
         title='The effect of overheating',
         caption=f'At {clock(oh_req)[-5:]} the owner asks what temperatures processors are built for, whether a limit '
                 'should watch the average or the hottest spot, what heat does to switching speed, and why a hot chip '
                 f'stops and then recovers. {n_oh} agents research it (69 sources, 60 of them outside), test it and write it up; E53 ran on aifoundry3 and '
                 f'aifoundry1 card 1 from {clock(oh_s)[-5:]} to {clock(oh_e)[-5:]} '
                 f'({card_h_between(0, 0, FAMK.index("oh")):.1f} card-hours): the hottest sensor ran 1–3 °C above the '
                 'mean, and 663 checked launches up to an 81 °C mean computed nothing wrong. The page goes out at '
                 f'{clock(page_first["et-soc1-effect-of-overheating"])[-5:]}.'),
    dict(t=mob_t, a=mob_req - 600, b=mob_t + 900, track='artifacts', title='The walkthrough on phones',
         caption=f'At {clock(mob_req)[-5:]} the owner reports the chip diagram cut off on a phone. {n_mob} agents find '
                 'the cause in the page itself (a minimum width, and a scroll to the middle of the canvas), not in the '
                 f'host; the phone layout, the whole die in the width, goes out at {clock(mob_t)[-5:]}, and the '
                 'host’s comment tab over the page’s left edge is reported to its team.'),
    dict(t=ref_t, a=ref_t - 600, b=(tl_dep[-1] if tl_dep else ref_t) + 600, track='human', title='The timeline refreshed',
         caption=f'At {clock(ref_t)[-5:]} the owner asks to bring this timeline up to date with the latest experiments'
                 + (f'; the refresh goes out at {clock(tl_dep[0])[-5:]}' if tl_dep else '')
                 + (f', and again at {clock(tl_dep[1])[-5:]} and {clock(tl_dep[2])[-5:]} after the owner’s two notes on it '
                    f'({clock(tl_notes[0])[-5:]}: lead each message with what it asked, the timing in small print; '
                    f'{clock(tl_notes[1])[-5:]}: link the pages each highlight produced).' if len(tl_dep) >= 3 else '.')),
    dict(t=talk_t[0], a=listen_t - 600, b=bc_dep + 900, track='human', title='Requests from the pages themselves',
         caption=f'At {clock(listen_t)[-5:]} the owner has the session listen for messages written on the published '
                 f'pages, in their Talk tab: {len(talk_t)} arrive by the snapshot. The memory levels get light tints '
                 f'instead of dotted and striped backgrounds (commit {clock(tints_t)[-5:]}); the chip diagram gets an '
                 f'eleventh data flow, B, Broadcast (Q62, asked at {clock(q62)[-5:]}, live at {clock(bc_dep)[-5:]}); '
                 'one message is feedback meant for the spacesheep team.'),
    dict(t=sup_t, a=sup_req - 600, b=sup_dep_t + 900, track='artifacts', title='The superseded energies folded in',
         caption=f'At {clock(sup_req)[-5:]} the owner points out the sections still marked “energies superseded”. '
                 f'{n_sup} agents fold the newer energies into the memory anatomy, memory hierarchy, on-chip '
                 f'communication and matmul pages (commit {clock(sup_t)[-5:]}), then sparse compute’s power from three '
                 f'cards and the first pass’s leftovers (commit {clock(sup_t2)[-5:]}); {n_sup_dep} pages go out at '
                 f'{clock(sup_dep_t)[-5:]}.'),
    dict(t=q63_t, a=q63 - 600, b=cyan_dep + 900, track='artifacts', title='Heat per mm: the 2× gap (Q63)',
         caption=f'At {clock(q63)[-5:]} the owner asks, from the heat-per-mm page, which process node the cited '
                 'wire-energy figure is for and whether a 2× gap between it and the measurement is expected. '
                 f'{n_q63} agents and forks read the figure’s papers, talks and interviews and the NoC energies measured '
                 f'on other chips; the answer is committed at {clock(q63_t)[-5:]} and live at {clock(q63_dep)[-5:]}. At '
                 f'{clock(cyan_req)[-5:]} the owner asks for a light cyan background: live at {clock(cyan_dep)[-5:]}.'),
    dict(t=major_t, a=major_t - 900, b=tl_repo_dep[0] + 900, track='human', title='A major pass, and this timeline in the repository',
         caption=f'At {clock(major_t)[-5:]} the owner asks for a major pass now that the lab works again: every '
                 'remaining lab fix and check, the NoC validation, the to-do list, and this timeline committed to the '
                 'repository. At 20:51 four of the lab report’s host fixes go in on aifoundry1, owner-approved (among them '
                 'a headless default and unused desktop services turned off); the rest, on all three machines, wait for '
                 'the owner, since the session’s permission check refused them. '
                 f'A workflow of {lab_wf["agents"]} agents studies ' + ', '.join(lab_labels[:-1])
                 + f' and {lab_labels[-1]}{lab_next}; another of {tl_wf["agents"]} moves this page and its tools into the '
                 f'repository, with a privacy scan of its data (commit {clock(tl_repo_t)[-5:]}, live at '
                 f'{clock(tl_repo_dep[0])[-5:]}).'),
    dict(t=dv2v_nat[0][1], a=min(r[1] for r in dv2v) - 600, b=(dv2v_red if dv2v_red else snap_all) + 600, track='cards',
         title='DV2 validation: sessions and verdicts',
         caption=f'The DV2 validation on aifoundry2 ran under its frozen plan from {clock(min(r[1] for r in dv2v))[-5:]} on 28 Sep: '
                 'a read-only temperature reading every 3 minutes, and a heating session only when the card was cool enough. '
                 f'{len(dv2v_nat)} replication sessions ran, '
                 + ', '.join(f'{clock(r[1])[-5:]}–{clock(r[2])[-5:]}' for r in dv2v_nat[:-1])
                 + f' and {clock(dv2v_nat[-1][1])[-5:]}–{clock(dv2v_nat[-1][2])[-5:]} on 28 Sep, each starting at 59–60 °C, with '
                 '1, 2 and 4 complete test blocks; the Master Minion, which hung on the development night, kept taking work. '
                 f'No session started after that; the readings ({len(dv2v_read)}) went on until the plan’s 20-hour window closed '
                 f'at {clock(max(r[2] for r in dv2v))[-5:]} on {DAYS[day_of(max(r[2] for r in dv2v))]} Sep.'
                 + (f' Reduced at {clock(dv2v_red)[-5:]}: TH3, TH4 and TH8 survived and TH7 fell (1 of 52); TH1, TH2 and Q2 '
                    'stayed untested, with no run that fits the hottest shire.' if dv2v_red else '')),
    dict(t=nv_t, a=nv_probe - 600, b=nv_t + 900, track='artifacts', title='NV: the NoC validation, frozen and waiting',
         caption=f'The NoC validation the owner asked for (E54): does the mesh’s energy per bit·mm follow its 0.485 V '
                 'supply, as heat per mm’s answer to Q63 assumed? A read-only probe of aifoundry3 at '
                 f'{clock(nv_probe)[-5:]} finds the NoC rail at 485 mV and 400 MHz; at {clock(nv_t)[-5:]} the '
                 'predictions are frozen and the experiment registered, before any card write. The first voltage '
                 'write, 540 then 600 mV and back, did not start: the session’s permission check refused a command that '
                 'changes a shared card’s state, so it waits for the owner. The validation is planned on aifoundry2 '
                 'after DV2.'),
    dict(t=min(r[1] for r in mp), a=mp_built - 600, b=max(r[2] for r in mp) + 900, track='cards',
         title='Four experiments, developed and validated',
         caption=f'{n_mp_build} agents build and pre-register four experiments on the hub’s open questions (commit '
                 f'{clock(mp_built)[-5:]}). Each is developed on aifoundry1 card 1 '
                 f'({clock(min(r[1] for r in mp_dev))[-5:]}–{clock(max(r[2] for r in mp_dev))[-5:]}), frozen, then '
                 f'validated on aifoundry3 ({clock(min(r[1] for r in mp_val))[-5:]}–{clock(max(r[2] for r in mp_val))[-5:]}), '
                 f'{card_h_between(0, 0, FAMK.index("mp")):.1f} card-hours in all. E55: two host-to-card copies in flight '
                 'in one stream move 0.49 of what one moves at 64 MB, while one in each of two streams loses nothing, '
                 'and a host write lands in the L3. E56: read replies go y first and write requests x first on both cards, where the chip '
                 'diagram assumed x first for every route; a link saturates near 92 GB/s. E57: the DRAM bank and row map '
                 'and per-controller refresh hold on aifoundry3, the L2 keeps TensorLoad lines, and stride-256 runs at '
                 '0.665 of the bandwidth; no theory of the 128 B per cycle cap survives. E58: the rails’ meters filter '
                 'with a time constant of 1.01–1.06 s on every rail of aifoundry3 (0.54 s on card 1’s SRAM rail). The '
                 f'PCIe runner’s first card run since its lock fix, at {clock(pcie_fix_run)[-5:]}, exits cleanly.'),
]
def commit_at(prefix):
    """the time of the first commit whose subject starts with prefix, or None"""
    return next((c[0] for c in commits if c[2].startswith(prefix)), None)


def msg_at(rx):
    m = msg_of(rx)
    return m[0][0] if m else None


def wf_named(rx):
    return [w for w in WF if re.search(rx, w['name'])]


def page_at(slug, after=0):
    return next((x[0] for x in sorted(deploys) if x[1] == pidx.get(slug, -1) and x[0] >= after), None)


hm_ = lambda t: clock(t)[-5:]
if sp_req is not None and sp_res is not None:
    sp_wfs = wf_named(r'^sparse-parity-')
    sp_m1, sp_m4, sp_m5 = (commit_at('Sparse parity on the card: M1'), commit_at('Sparse parity M4 on the card'),
                           commit_at('Sparse parity M5 on the card'))
    sp_pub = commit_at('The sparse parity page is public')
    sp_page = page_first.get('et-soc1-sparse-parity')
    sp_end = max([t for t in (sp_pub, sp_page, sp_wfs[-1]['e'] if sp_wfs else None) if t] or [snap_all])
    HL.append(dict(
        t=sp_build['s'] if sp_build else sp_res['s'], a=sp_req - 300, b=sp_end + 600, track='agents',
        title='Sparse parity: from research to the card',
        caption=f'At {hm_(sp_req)} on 28 Sep the owner queues the next task: a sparse-parity solver that uses the chip’s '
                'thousand cores, prototyped at toy sizes first and then scaled to the whole chip. A workflow of '
                f'{sp_res["agents"]} agents ({hm_(sp_res["s"])}–{hm_(sp_res["e"])}, no card) surveys the literature, maps the '
                'problem onto the chip and designs it: a noisy sparse parity found by exhaustive correlation, computed as int8 '
                f'tensor products. {len(sp_wfs) - 1} more workflows ({sum(w["agents"] for w in sp_wfs[1:])} agents) build and tune it'
                + (f'. On the card, M1 at {hm_(sp_m1)} on 29 Sep solves L1 and L2 with exact checksums, about 5× one CPU core' if sp_m1 else '')
                + (f'; M4 at {hm_(sp_m4)} runs 8–9× one core and 1.0–1.6× six tuned AVX-512 threads' if sp_m4 else '')
                + (f'; M5 at {hm_(sp_m5)}, a two-stage screen, solves L2 in 0.323 s and (256,5) in 1.52 s (1.6× and 1.2× six tuned '
                   'threads at equal loss), at 5.0, 16.6 and 89 J a solve, 2.5–7.7× below the CPU package’s assumed energy' if sp_m5 else '')
                + (f'. The page went out at {hm_(sp_page)} and was made public at {hm_(sp_pub)} (Q67).' if sp_page and sp_pub else '.')))
# 29 September, afternoon: the DV2 validation's end (above), then a third card
if mp3:
    third_t = commit_at('Third card')
    HL.append(dict(
        t=min(r[1] for r in mp3), a=min(r[1] for r in mp3) - 900, b=(third_t or max(r[2] for r in mp3)) + 900, track='cards',
        title='A third card for E55–E57',
        caption=f'With the DV2 validation over, aifoundry2 ran three of the major pass’s experiments as a third card, '
                f'{hm_(min(r[1] for r in mp3))}–{hm_(max(r[2] for r in mp3))} on 29 Sep ({len(mp3)} passes, smoke tests first): '
                'E55 pcie2, E57 memp2 and E56 nocr, under the frozen plans. The two-copy results held (T35-S, T34-A), read '
                'replies go y first there too, the tensor reload and per-controller refresh hold, and the DRAM map misses one '
                'condition on this card' + (f' (commit {hm_(third_t)}).' if third_t else '.') + ' E58 tau was not repeated on it.'))
# 29 September evening to 30 September: the weekly limit, then a new account
lim29 = [l for l in out['main']['limits'] if l[1] == 'weekly limit' and day_of(l[0]) == 10]
resume_t = msg_at(r'^Asks the session to continue')
if lim29 and resume_t:
    HL.append(dict(
        t=lim29[0][0], a=lim29[0][0] - 900, b=resume_t + 900, track='agents', title='The weekly limit, again',
        caption=f'At {hm_(lim29[0][0])} on 29 Sep the account reached its weekly usage limit again, which would reset on '
                f'4 October: the agents stopped mid-task. The session stood still until {hm_(resume_t)} on 30 Sep, when the '
                'owner continued it on a new account and asked for the unfinished work to go on with agents in parallel.'))
q70 = next((m[0] for m in msgs if m[6] == 'Q70'), None)
hs_page = page_first.get('et-soc1-without-heatsink')
if q70 and hs_page:
    hs_wf = wf_named(r'^no-heatsink-')
    HL.append(dict(
        t=hs_page, a=q70 - 600, b=hs_page + 900, track='artifacts', title='Running without the heatsink (Q70)',
        caption=f'At {hm_(q70)} on 29 Sep the owner asks whether a card can run without its heatsink, with a sensor or '
                'a thermal camera pointed at the chip. Two research agents start at once and stop at the weekly limit; on '
                f'30 Sep {len(hs_wf)} workflows ({sum(w["agents"] for w in hs_wf)} agents) build, review and finish the report: '
                'a model on the record (leakage, the fitted heatsink, a Monte Carlo of the bare package, card 0’s guard '
                'samples) and 43 outside sources. A bare card at 600 MHz almost never settles (1 of 3,600 draws), a sensor '
                'would see a plated lid at nearly one temperature, and a thermocouple taped to the heatsink’s base is the '
                f'safe way to read the package. The page goes out at {hm_(hs_page)}, cross-linked from four others.'))
q71 = next((m[0] for m in msgs if m[6] == 'Q71'), None)
dash_wf = wf_named(r'^lab-dashboard$')
if q71 and dash_wf:
    dash_t = commit_at('The AI Foundry lab dashboard')
    d_all = msg_at(r'^Dashboard for everyone')
    d_down = msg_at(r'^aifoundry1 is down but the dashboard')
    HL.append(dict(
        t=dash_t or dash_wf[0]['e'], a=q71 - 600, b=max(t for t in (dash_t, d_down, dash_wf[0]['e']) if t) + 900, track='artifacts',
        title='The lab dashboard',
        caption=f'At {hm_(q71)} the owner asks for a live view of the lab: the three machines, the four cards and the people '
                f'using them. {dash_wf[0]["agents"]} agents build a collector (the lab tools, who is logged in, their Claude '
                'and spacesheep sessions, and a card sample that is off by default) and an updater that republishes the page '
                'on every change and every 10 minutes' + (f' (commit {hm_(dash_t)})' if dash_t else '') + '. The page was '
                'published private, and made public that afternoon (below).'
                + (f' At {hm_(d_all)} the owner asks for a view for everyone, with each card’s use over 24 hours' if d_all else '')
                + (f', and at {hm_(d_down)} for each machine’s own state, since aifoundry1 was down and the page did not show it.' if d_down else '.')))
q72 = next((m[0] for m in msgs if m[6] == 'Q72'), None)
ls_page = page_first.get('aifoundry-lab-start')
if q72 and ls_page:
    ls_wf = wf_named(r'^lab-onboarding-page$')
    q73 = next((m[0] for m in msgs if m[6] == 'Q73'), None)
    again = msg_at(r'^New-user page again')
    ls_4 = commit_at('New user? Start now, fourth edition')
    HL.append(dict(
        t=ls_page, a=q72 - 600, b=max(t for t in (ls_page, again, ls_4) if t) + 900, track='artifacts', title='New user? Start now',
        caption=f'At {hm_(q72)} the owner asks for a “New user? Start now” page: self-contained instructions a newcomer hands '
                'to their coding agent, from the week’s lessons. '
                + (f'{ls_wf[0]["agents"]} agents write it; ' if ls_wf else '')
                + f'it goes out public at {hm_(ls_page)}.'
                + (f' At {hm_(q73)} the owner asks for it much shorter: only what the person must do, and a diagram of the three '
                   'machines and four cards' if q73 else '')
                + (f'; at {hm_(again)}, for one prompt with only a name to fill in' if again else '')
                + (f'. The fourth edition, with an onboarding script a new user runs as themselves, is committed at {hm_(ls_4)}.' if ls_4 else '.')))
use_t = msg_at(r'^Dashboard for everyone')
use_ag = [r for r in agents if re.search(r'usage logger', r['label'] or '')]
if use_t and use_ag:
    use_wf = wf_named(r'^et-usage')
    HL.append(dict(
        t=use_ag[0]['s'], a=use_t - 600, b=max([r['e'] for r in use_ag] + [w['e'] for w in use_wf]) + 600, track='agents',
        title='Logging who uses the cards',
        caption=f'At {hm_(use_t)} the owner asks to log who uses each card, for every user old and new, so that the dashboard '
                'can show the last 24 hours: an agent builds a card-usage logger '
                f'({hm_(use_ag[0]["s"])}–{hm_(use_ag[0]["e"])})'
                + (f', and a workflow of {use_wf[0]["agents"]} agents reviews it and its installation on the machines '
                   + (f'from {hm_(use_wf[0]["s"])} (still running at the snapshot).' if use_wf[0]['status'] == 'running'
                      else f'({hm_(use_wf[0]["s"])}–{hm_(use_wf[0]["e"])}).')
                   if use_wf else '.')))
low_t = msg_at(r'^Heatsink: how low can the clock go')
low_wf = wf_named(r'^heatsink-low-clock')
if low_t and low_wf:
    low_c = commit_at("The heatsink page's low-clock envelope")
    low_dep = page_at('et-soc1-without-heatsink', low_c - 300) if low_c else None
    HL.append(dict(
        t=low_dep or low_wf[0]['s'], a=low_t - 300, b=max(low_dep or 0, low_wf[0]['e'], low_t) + 600, track='artifacts',
        title='How low can the clock go? (Q81)',
        caption=f'At {hm_(low_t)} on 30 Sep the owner asks how far down the clock can go, 100 MHz or even 10 MHz, to run a '
                'card without its heatsink under the thermal camera: the envelope of what is possible. A workflow of '
                f'{low_wf[0]["agents"]} agents studies it '
                + (f'from {hm_(low_wf[0]["s"])} (still running at the snapshot).' if low_wf[0]['status'] == 'running' else
                   f'({hm_(low_wf[0]["s"])}–{hm_(low_wf[0]["e"])}): notes on the firmware’s clocks, outside sources, '
                   'a power and imaging model, reviewed for physics, sources and the reader.')
                + (f' The answer is in the heatsink page at {hm_(low_dep)}: 100 MHz is the lowest clock the firmware can set '
                   '(10 MHz cannot be set), and at 100 MHz a card still idles at 19–24 W, so a bare card settles only with a '
                   'fan or a blower, and only from some cold starts. A camera through a taped lid would see a coarse pattern '
                   'with lock-in; the recommended route keeps the heatsink and reads the chip’s own sensor with lock-in. The '
                   'measurement plan is pre-registered, not run.' if low_dep else '')))
# 30 September, evening, to 1 October: the logger installed and the dashboard public; the driver race reported; a departed
# user's checkpoints deleted; the memory levels' level tabs; the chip diagram's powers of ten
inst_t = commit_at('The card-usage logger, installed on all three hosts')
dash2_t = commit_at("Lab dashboard: the card-use logger's final format")
if inst_t and dash2_t:
    _inst = next(c[2] for c in commits if c[2].startswith('The card-usage logger, installed on all three hosts'))
    _m = re.search(r'\((\d+) Sep (\d\d):(\d\d)\)', _inst)   # the install's own time, in the subject (30 Sep 20:54)
    inst_at = T(int(_m.group(1)), f'{_m.group(2)}:{_m.group(3)}') if _m else inst_t
    use_rev, dash_rev = wf_named(r'^et-usage-review$'), wf_named(r'^dashboard-v2-review$')
    dash_live = page_at('aifoundry-lab-dashboard', dash2_t)
    nb_public = next((m[0] for n in out['neighbors']['sessions'] for m in n['msgs'] if m[3].startswith('Asks for public lab pages')), None)
    nb_fix = next((e for n in out['neighbors']['sessions'] for e in n['events'] if e[2] == 'fix' and 'dashboard' in e[3]), None)
    HL.append(dict(
        t=inst_at, a=inst_at - 900, b=(dash_live or dash2_t) + 900, track='artifacts',
        title='The logger installed, the dashboard public',
        caption=f'At {hm_(inst_at)} on 30 Sep the card-usage logger goes onto all three machines'
                + (f', after {use_rev[0]["agents"]} agents reviewed it for security, card safety and correctness '
                   f'({hm_(use_rev[0]["s"])}–{hm_(use_rev[0]["e"])})' if use_rev else '')
                + ': a small service that records which user’s program holds each card, so that the dashboard can draw each '
                'card’s use over 24 hours. The dashboard’s rewrite'
                + (f', reviewed by {dash_rev[0]["agents"]} agents for privacy, the machines’ liveness, the card-use data and '
                   'the reader,' if dash_rev else '')
                + f' is committed at {hm_(dash2_t)}' + (f' and live at {hm_(dash_live)}' if dash_live else '')
                + ': the same view for everyone, who is logged in and doing what, each card’s use and each machine’s own state. '
                'It is public'
                + (f', as the owner told the neighbor session at {hm_(nb_public)}' if nb_public else '')
                + (f'; at {hm_(nb_fix[0])} the neighbor had stopped its updater from making the page private again.' if nb_fix else '.')))
race_t = msg_at(r'^Limits reset: continue')
race_ag = [r for r in agents if re.match(r'Driver race', r['label'] or '')]
if race_t and race_ag:
    lim30 = [l[0] for l in out['main']['limits'] if l[1] == 'session limit' and day_of(l[0]) == 11 and l[0] < race_t]
    race_dep = page_at('lab-report', race_ag[0]['s'])
    HL.append(dict(
        t=race_ag[0]['s'], a=(lim30[0] if lim30 else race_t) - 600, b=max(race_ag[0]['e'], race_dep or 0) + 600, track='agents',
        title='The driver race reported (Q86)',
        caption=(f'At {hm_(lim30[0])} on 30 Sep the account reached its session limit, and the agents stopped mid-task. ' if lim30 else '')
                + f'At {hm_(race_t)}, after the reset, the owner continues the session with many agents in parallel, and asks for '
                'the driver race that the logger’s review had found to be reported upstream and in the report for the lab lead: '
                'the card’s queue counters, which any user can read, are walked without a lock, so a read during a card reset can '
                f'return garbage. An agent ({hm_(race_ag[0]["s"])}–{hm_(race_ag[0]["e"])}) adds it to that report’s requests'
                + (f' (republished at {hm_(race_dep)})' if race_dep else '')
                + ' and drafts the upstream issue for the owner to file: a public version, and the full analysis with a patch to '
                'send to the driver’s maintainers privately.'))
ck_t = msg_at(r"^Free aifoundry1's disk")
ck_c = commit_at("aifoundry1's disk is no longer full")
if ck_t and ck_c:
    ck_ag = [r for r in agents if re.match(r'Update texts after the aifoundry1 cleanup', r['label'] or '')]
    ck_dep = page_at('aifoundry-lab-start', ck_t)
    HL.append(dict(
        t=ck_t + 120, a=ck_t - 600, b=max(ck_c, ck_dep or 0) + 600, track='human',
        title='A departed user’s checkpoints deleted (Q87)',
        caption=f'At {hm_(ck_t)} on 30 Sep the owner asks to free aifoundry1’s disk, which was nearly full, by deleting a '
                'departed user’s large public model checkpoints, which can be downloaded again. After a dry run, at 22:25 the '
                '27 checkpoints of 1 GB or more are deleted (118 GB of public models): /home goes from 99% to 72% full, and '
                'the pool from 95% to 71%.'
                + (f' An agent updates the texts that still called the disk nearly full ({hm_(ck_ag[0]["s"])}–{hm_(ck_ag[0]["e"])})'
                   if ck_ag else ' The texts that still called the disk nearly full are updated')
                + (f', the New user page is republished at {hm_(ck_dep)}' if ck_dep else '')
                + f', and the record is committed at {hm_(ck_c)}.'))
ml_t = msg_at(r'^Memory levels: smooth zoom in and out')
ml_c1 = commit_at('Memory levels: level tabs and taps zoom smoothly')
ml_c2 = commit_at('Memory levels: the three reviews of the smooth level moves fixed')
ml_dep = page_at('et-soc1-memory-levels', ml_c2 - 300) if ml_c2 else None
if ml_t and ml_dep:
    ml_wf1, ml_wf2 = wf_named(r'^memory-levels-smooth-zoom$'), wf_named(r'^memory-levels-tabs-port$')
    HL.append(dict(
        t=ml_dep, a=ml_t - 600, b=ml_dep + 900, track='artifacts', title='Memory levels: the level tabs zoom (Q82)',
        caption=f'At {hm_(ml_t)} on 30 Sep the owner asks the memory-levels page to zoom smoothly, out and back in, when a '
                'level tab or a part is tapped, on phones too, as the arrow keys do on a desktop.'
                + (f' A first build ({hm_(ml_wf1[0]["s"])}–{hm_(ml_wf1[0]["e"])}) is redone on the smoother camera that had '
                   'just replaced the page’s own' if ml_wf1 else '')
                + (f': from {hm_(ml_wf2[0]["s"])} a workflow of {ml_wf2[0]["agents"]} agents ports it' if ml_wf2 else '')
                + (f' (commit {hm_(ml_c1)})' if ml_c1 else '')
                + f', reviews it on a phone, on a desktop for the keyboard and screen readers, and in code, and fixes what the '
                f'reviews found ({hm_(ml_c2)} on 1 Oct). Live at {hm_(ml_dep)}: a level tab or a tap glides out to the common '
                'scale and back in to the chosen level.'))
cz_t = msg_at(r'^Chip diagram: double-click anything to zoom in')
cz_m = commit_at("Merge the chip diagram's deep zoom")
cz_dep = page_at('et-soc1-chip-diagram', cz_m - 300) if cz_m else None
if cz_t and cz_dep:
    cz_wf = [w for w in wf_named(r'^chip-diagram-powers-of-ten$') if w['status'] != 'killed']
    cz_1a, cz_1b, cz_23 = (commit_at('Chip diagram: the path camera'), commit_at('Chip diagram: the Up bar'),
                           commit_at('Chip diagram: the deep zoom, from beyond'))
    HL.append(dict(
        t=cz_dep, a=cz_t - 600, b=cz_dep + 900, track='artifacts', title='The chip diagram’s powers of ten (Q85)',
        caption=f'At {hm_(cz_t)} on 30 Sep, with a photo of the lab’s rack, the owner asks the chip diagram to zoom like the '
                'powers of ten: double-click any part to zoom in, a wide button to go up, out past the card to the rack, the '
                'city, the Earth and the galaxies, and in to the circuits.'
                + (f' A workflow of {cz_wf[0]["agents"]} agents ({hm_(cz_wf[0]["s"])}–{hm_(cz_wf[0]["e"])}) builds it in phases' if cz_wf else ' It is built in phases')
                + (f' (a path camera at {hm_(cz_1a)}' if cz_1a else ' (')
                + (f', the Up bar and glides between shires at {hm_(cz_1b)}' if cz_1b else '')
                + (f', the outer and inner scales at {hm_(cz_23)} on 1 Oct' if cz_23 else '')
                + '), then reviews it for facts, interaction, visuals and code and fixes what the reviews found. Merged and live '
                f'at {hm_(cz_dep)}: a ladder of 33 scales, from beyond the observable universe through the Local Group, the '
                'Earth, San Francisco, the lab, the rack and the card to the die, and inside it to the 6T cell, the latch, the '
                'full adder, the FinFET and the silicon crystal; 131 of 131 tours pass on a desktop and a phone.'))
# 30 September, 14:41-15:24: the link retrain hang and the power cycle (the neighbor session's lane)
NBEV = {e[2]: e for n in out['neighbors']['sessions'] for e in n['events'] if e[2] in ('test', 'power', 'probe')}
nb_page = next((e for n in out['neighbors']['sessions'] for e in n['events'] if e[2] == 'page' and 'retrain' in e[3]), None)
nb_commit = next((e for n in out['neighbors']['sessions'] for e in n['events'] if e[2] == 'commit'), None)
if 'test' in NBEV and 'power' in NBEV:
    t_test, t_pow = NBEV['test'][0], NBEV['power'][0]
    HL.append(dict(
        t=t_test, a=t_test - 900, b=(nb_commit[0] if nb_commit else NBEV['power'][1]) + 900, track='cards',
        title='The link retrain hang and the power cycle',
        caption=f'At {hm_(t_test)} on 30 Sep the owner’s session (the neighbor session, in a lane of its own) ran the link '
                'test from the lab report on aifoundry1 card 0: a retrain of its PCIe link at 8 GT/s. The whole host hung, '
                f'both cards with it, until the lab lead power-cycled all three machines at about {hm_(t_pow + 30)}. The '
                'reboot of aifoundry2 stopped this session and the neighbor and cleared /tmp there: about 19 GB of working '
                'files, this timeline’s working folder among them, so working files now stay out of /tmp.'
                + (f' Back at {hm_(NBEV["probe"][0])}, the neighbor read the boot records and the link’s counters (a hard hang, not '
                   'a panic)' if 'probe' in NBEV else '')
                + (f', published the incident page at {hm_(nb_page[0])}' if nb_page else '')
                + (f' and committed the lesson at {hm_(nb_commit[0])}: never retrain or re-speed a card’s link on a running host.'
                   if nb_commit else '.')))
# 1-5 October (the refresh of 5 Oct): the chip diagram's loop of scales; aifoundry2's card off the bus; the lab day of
# 2 Oct (the maintenance session); 4 Oct, the audit session and the Antigravity session; the checkpoint and this refresh
TO = lambda d, hm: T(30 + d, hm)   # a day of October
nb_by = {n['id']: n for n in out['neighbors']['sessions']}
def nb_ev(sid, rx):
    return next((e for e in (nb_by.get(sid) or {}).get('events', []) if re.search(rx, e[3])), None)
def nb_msg(sid, rx):
    return next((m[0] for m in (nb_by.get(sid) or {}).get('msgs', []) if re.search(rx, m[3])), None)
q88 = msg_at(r'^Chip diagram and memory levels: one consistent zoom loop')
l6 = commit_at('Ladder (6)')
if q88 and l6:
    lk, sp, lp, ghp = (commit_at('Links (1 Oct)'), commit_at('Speed (1 Oct)'), commit_at('Loop (1 Oct, evening)'),
                       commit_at('GitHub Pages mirror of the two interactive pages'))
    cd_dep = page_at('et-soc1-chip-diagram', l6 - 900)
    HL.append(dict(
        t=cd_dep or l6, a=q88 - 900, b=max(cd_dep or 0, l6) + 900, track='artifacts',
        title='The chip diagram’s loop of scales (Q88–Q94)',
        caption=f'From {hm_(q88)} on 1 Oct the owner asks the chip diagram and the memory levels to share one ladder of '
                'scales: a way back from every view, every path down to transistors and atoms, a hidden way out past the rack, '
                'and zooming out past the universe looping back to an atom. Built and checked in six steps through the day'
                + (f': an address for every flow, slide and scale at {hm_(lk)}' if lk else '')
                + (f', a 1×/2× replay at {hm_(sp)}' if sp else '')
                + (f', the one-way loop from the Planck length at {hm_(lp)}' if lp else '')
                + (f'; mirrored to GitHub Pages at {hm_(ghp)}' if ghp else '')
                + f'; the last check at {hm_(l6)} on 2 Oct.'))
off1 = next((h for h in out['neighbors']['hosts'] if h[3] == 'hang' and 'off the bus' in h[4] and h[1] < TO(2, '06:00')), None)
oos = next((h for h in out['neighbors']['hosts'] if 'out of service' in h[4]), None)
if off1 and oos:
    HL.append(dict(
        t=off1[1], a=off1[1] - 1800, b=oos[1] + 1800, track='cards', title='aifoundry2’s card falls off the bus',
        caption=f'At {hm_(off1[1])} on 1 Oct aifoundry2’s card stops answering on PCIe while idle: its cooling follows the '
                'host’s fans, which slow down when the host is idle. A full-reset reboot at 06:45 on 2 Oct brings it back, but '
                'idle it runs away again (126 °C at 07:42); a plain reboot at 10:47 leaves it off, a full reset at 10:53 brings '
                f'it back, and at {hm_(oos[1])} it falls off for good after heating from 45 °C to a 138 °C mean and 134 W. Out '
                'of service since: the air that reaches it is too warm, a fix of the fan settings on site.'))
live = nb_ev('97db24ee', r'^The live dashboard')
lab2 = page_at('aifoundry-lab-2-october') or (nb_ev('97db24ee', r'^Published: AI Foundry lab, 2 October') or [None])[0]
c0 = nb_ev('97db24ee', r'card 0 back in service')
if live and c0:
    HL.append(dict(
        t=lab2 or c0[0], a=live[0] - 900, b=max(lab2 or 0, c0[0]) + 1800, track='artifacts',
        title='The lab day: a live dashboard, card 0 back, new users',
        caption=f'On 2 Oct the maintenance session (a lane of its own) makes the lab dashboard live at {hm_(live[0])}: each '
                'machine streams a reading every second, each card’s temperature included, and a history page keeps hour, '
                f'day and week graphs. aifoundry1’s card 0 is back in service at {hm_(c0[0])} after its fan was replaced (49 °C '
                'idle, 65 °C before). The new-user instructions go through five editions for three new lab users that '
                'afternoon, card use is shown live, each second'
                + (f', and the day’s report goes out at {hm_(lab2)}.' if lab2 else '.')))
race = nb_ev('93af8ad7', r'driver race filed upstream')
rep_ev = nb_ev('93af8ad7', r'report for the lab lead re-checked')
if race and rep_ev:
    HL.append(dict(
        t=race[0], a=rep_ev[0] - 5400, b=race[0] + 900, track='artifacts',
        title='The lab lead’s report checked; the driver race filed upstream',
        caption=f'On 4 Oct a session on the owner’s second Claude account goes through the report for the lab lead item by '
                f'item: what a 2 Oct rebuild had dropped comes back at {hm_(rep_ev[0])}, the live monitor reads the cards more '
                'gently, a card-open logger goes onto aifoundry1, and card 0 is counted again once fixed. At '
                f'{hm_(race[0])} the driver race of 30 Sep is filed publicly as issue 136 of aifoundry-org/et-platform: the chips '
                'are end-of-life, so nothing needs holding back. It also prepares the two-account Claude setup for '
                'aifoundry1 and aifoundry3.'))
ag = nb_ev('c42b457d', r'^Antigravity on aifoundry2')
turbo = nb_ev('c42b457d', r'^Turbo mode')
ag_ask = nb_msg('c42b457d', r'^Install the Antigravity CLI')
if ag and turbo and ag_ask:
    HL.append(dict(
        t=ag[0], a=ag_ask - 600, b=turbo[0] + 900, track='artifacts', title='Antigravity on the lab machines',
        caption=f'At {hm_(ag_ask)} on 4 Oct the owner asks for Google’s Antigravity CLI on the lab machines, reachable from '
                f'its web dashboard. By {hm_(ag[0])} it runs on aifoundry2 with its remote-control daemon, one Google account '
                'per machine, kept up by a watchdog. The dashboard cannot switch the agents to turbo mode; at '
                f'{hm_(turbo[0])} the session finds the two settings files that do, from the program’s own message '
                'definitions, and writes a tool that sets both and a script for aifoundry1 and aifoundry3.'))
ck = nb_ev('1f1f61cb', r'^The agent setup checkpointed')
ck_ask = nb_msg('1f1f61cb', r'^Checkpoint the machine')
rf_ask = nb_msg('1f1f61cb', r'^Refresh this timeline')
if ck and ck_ask:
    HL.append(dict(
        t=rf_ask or ck[0], a=(nb_msg('1f1f61cb', r'^Asks why two app settings') or ck_ask) - 600,
        b=(rf_ask or ck[0]) + 900, track='human', title='The setup checkpointed, and this page',
        caption=f'At {hm_(ck_ask)} on 4 Oct the owner asks for the machine’s whole agent setup, two Claude accounts with '
                'remote control and the Antigravity daemon, with its lessons, to be kept in GitHub, so that the machine can be '
                f'rebuilt if it is wiped: a private repository with a rebuild guide, committed at {hm_(ck[0])}.'
                + (f' At {hm_(rf_ask)} on 5 Oct the owner asks for this refresh: every session of the two weeks, on both '
                   'accounts, and the owner’s own words behind every summary.' if rf_ask else '')))
HL.sort(key=lambda h: h['t'])
# the published pages each highlight produced or changed (slug, then an optional #anchor); only pages the page list shows
# as public: the report for the lab lead and the pages outside the set are never linked
HL_LINKS = {
    'The first card use': ['et-soc1-memory-anatomy'],
    '179 agents and a usage limit': ['et-soc1-limits-of-observability'],
    'The Horace experiment': ['et-soc1-horace-experiment', 'et-soc1-power-temperature', 'et-soc1-why-low-power'],
    'A second card': ['et-soc1-dvfs-leakage', 'et-soc1-hot-line', 'et-soc1-on-chip-relay'],
    'The energy manual': ['et-soc1-energy-manual'],
    'Heat per millimetre': ['et-soc1-heat-per-mm'],
    'The report review': ['et-soc1-limits-of-observability'],
    'Validation overnight': ['et-soc1-limits-of-observability'],
    'Claims check v3 begins': ['et-soc1-limits-of-observability#claims'],
    'aifoundry1 fixed': ['aifoundry1-troubleshooting', 'aifoundry1-fix'],
    'The v3 campaign on three cards': ['et-soc1-limits-of-observability#claims'],
    'The visualization pass': ['et-soc1-limits-of-observability'],
    'Gathers and scatters (E48)': ['et-soc1-memory-hierarchy', 'et-soc1-chip-diagram'],
    'The three-card page updates': ['et-soc1-limits-of-observability#claims'],
    'Chip diagram and this timeline': ['et-soc1-chip-diagram'],
    'The chip diagram and the PCIe link': ['et-soc1-chip-diagram', 'et-soc1-pcie-link'],
    'Heat placement': ['et-soc1-heat-placement'],
    'The chip diagram polished': ['et-soc1-chip-diagram'],
    'DV2: the governor and heat': ['et-soc1-dvfs-leakage#what-triggers-a-step-down-and-does-placement-delay-it'],
    'aifoundry2 hangs': ['et-soc1-dvfs-leakage#what-triggers-a-step-down-and-does-placement-delay-it'],
    'Memory levels, interactively': ['et-soc1-memory-levels', 'et-soc1-memory-anatomy'],
    'The status, and every task at once': ['et-soc1-heat-placement', 'et-soc1-review-todo'],
    'Heat placement: the verdicts': ['et-soc1-heat-placement#verdicts'],
    'The effect of overheating': ['et-soc1-effect-of-overheating'],
    'The walkthrough on phones': ['et-soc1-chip-diagram', 'et-soc1-memory-levels'],
    'Requests from the pages themselves': ['et-soc1-memory-levels', 'et-soc1-chip-diagram'],
    'The superseded energies folded in': ['et-soc1-memory-anatomy', 'et-soc1-memory-hierarchy', 'et-soc1-on-chip-communication',
                                          'et-soc1-matmul-efficiency', 'et-soc1-sparse-compute'],
    'Heat per mm: the 2× gap (Q63)': ['et-soc1-heat-per-mm#dally-node'],
    'A major pass, and this timeline in the repository': ['et-soc1-review-todo'],
    'DV2 validation: sessions and verdicts': ['et-soc1-dvfs-leakage#what-triggers-a-step-down-and-does-placement-delay-it'],
    'NV: the NoC validation, frozen and waiting': ['et-soc1-heat-per-mm#dally-node'],
    'Four experiments, developed and validated': ['et-soc1-limits-of-observability#improve', 'et-soc1-pcie-link',
                                                  'et-soc1-chip-diagram'],
    'Sparse parity: from research to the card': ['et-soc1-sparse-parity'],
    'A third card for E55–E57': ['et-soc1-pcie-link', 'et-soc1-chip-diagram', 'et-soc1-memory-levels'],
    'Running without the heatsink (Q70)': ['et-soc1-without-heatsink'],
    'New user? Start now': ['aifoundry-lab-start'],
    'How low can the clock go? (Q81)': ['et-soc1-without-heatsink'],
    'The link retrain hang and the power cycle': ['aifoundry1-link-retrain-hang'],
    'The lab dashboard': ['aifoundry-lab-dashboard'],
    'The logger installed, the dashboard public': ['aifoundry-lab-dashboard'],
    'A departed user’s checkpoints deleted (Q87)': ['aifoundry-lab-start'],
    'Memory levels: the level tabs zoom (Q82)': ['et-soc1-memory-levels'],
    'The chip diagram’s powers of ten (Q85)': ['et-soc1-chip-diagram'],
    'The chip diagram’s loop of scales (Q88–Q94)': ['et-soc1-chip-diagram', 'et-soc1-memory-levels'],
    'aifoundry2’s card falls off the bus': ['aifoundry-lab-2-october'],
    'The lab day: a live dashboard, card 0 back, new users': ['aifoundry-lab-dashboard', 'aifoundry-lab-history',
                                                              'aifoundry-lab-2-october', 'aifoundry-lab-start'],
    # the dashboard is linked since it became public (30 Sep, the owner's word; MIRROR.md lists it public); the report for
    # the lab lead is never linked, so the driver race's highlight has no link
}
_pub = {pg['key']: pg['title'] for pg in pages if not pg['private']}
for pg in R['pages']:   # the public pages MIRROR.md lists that this session did not deploy (a neighbor's incident page)
    if pg.get('in_mirror') and not pg.get('private') and pg.get('slug') and pg['key'] == pg['slug'] and pg['key'] not in _pub \
            and pg.get('visibility_now', 'public') == 'public' and not pg['key'].startswith(('outside', 'other-', 'lab-report')):
        _pub[pg['key']] = pg['title']
_unknown = sorted(set(HL_LINKS) - {h['title'] for h in HL})
if _unknown:
    raise SystemExit(f'HL_LINKS names highlights that do not exist: {_unknown}')
for h in HL:
    links = []
    for spec in HL_LINKS.get(h['title'], []):
        slug, _, frag = spec.partition('#')
        if slug not in _pub:
            raise SystemExit(f'highlight {h["title"]!r} links {slug!r}, which is not a public page in the page list')
        links.append([_pub[slug], f'https://spacesheep.dev/@yaroslavvb/{slug}' + (f'#{frag}' if frag else '')])
    if links:
        h['links'] = links
out['highlights'] = [{k: (round(v, 1) if isinstance(v, float) else v) for k, v in h.items()} for h in HL]

# ------------------------------------------------------------------ who did the time
out['who'] = {
    'human_active_h': out['human']['totals']['active_h'], 'human_active_paste_h': out['human']['totals']['active_paste_h'],
    'human_engagement_h': out['human']['totals']['engagement_h'],
    'main_busy_h': out['main']['totals']['busy_h'], 'main_strict_h': out['main']['totals']['strict_h'],
    'main_tool_wait_h': out['main']['totals']['tool_wait_h'], 'main_tool_wait_lab_h': out['main']['totals']['tool_wait_lab_h'],
    'main_watch_h': out['main']['totals']['watch_h'],
    'sub_agent_h': out['agents']['totals']['busy_agent_h'],
    'card_held_h': out['cards']['totals']['held_h'], 'card_busy_h': out['cards']['totals']['busy_h'],
    'wall_h': round((out['meta']['snapshot_end'] - out['meta']['session_start']) / 3600, 2),
}

# the page's data passes the same sanitize rules and the same scan as the extracts (AGENT.md section 10)
sanitize_tree(out)
_txt = json.dumps(out, separators=(',', ':'), ensure_ascii=False)
if scan_text('timeline.json', _txt, compiled(), public_spaces()):
    raise SystemExit('timeline.json would carry something private (above): add a sanitize rule to the privacy table')
dst = os.path.join(DD, 'timeline.json')
open(dst, 'w', encoding='utf-8').write(_txt)
print('wrote', dst, os.path.getsize(dst), 'bytes')
print('human', out['human']['totals'])
print('main', out['main']['totals'])
print('agents', out['agents']['totals'], 'groups', len(G), 'lanes', sum(g['lanes'] for g in G))
print('cards', out['cards']['totals'], [(p['id'], p['held_h'], p['held_h_cards_json']) for p in per_card])
print('tokens', out['tokens']['totals']['all'])
print('who', out['who'])
for h in out['highlights']:
    print(clock(h['t']), h['title'], '|', h['caption'][:110])
