#!/usr/bin/env python3
"""Task B: subagents and workflows of session ed6d06d5.

Streams every transcript line by line (the 124 MB main transcript included)
and writes ../agents.json with:
  agents[]      one row per subagent transcript (Agent-tool agents, forks and
                workflow agents): ids, labels, workflow, start/end, busy
                intervals (gap < 3 min), tool calls, tokens deduped by
                message.id, models, status
  workflows[]   one row per workflow run (name, launches, status, agents, tokens)
  main          main-agent busy intervals, tokens, tool calls, models
  concurrency   per-minute busy counts from 2026-09-19 16:00 UTC to the last event
  peak          peak concurrency and when
  totals, anomalies

Token dedupe: an assistant message is streamed as several lines with the same
message.id (usage grows as output streams), and forks start with a copy of
their parent's history (same uuids, same message ids).  Usage is therefore
taken as the per-field max over lines of one message.id, and each message.id
is attributed to exactly one owner: the shallowest transcript that has it
(main < depth-1 agent < depth-2 fork), ties to the earliest timestamp.
Fork transcripts also skip events whose uuid appears in the parent transcript,
so a fork's start time is its spawn time, not the start of the copied history.
"""
import json, glob, os, re, sys, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402

# Privacy tables (people's names, the lab-lead report's identifiers) are not in this public file: they are read from
# a local JSON file that is never committed, $TIMELINE_PRIVATE (default ~/.config/et-soc1-timeline/private.json).
# Without it the script stops, unless TIMELINE_PRIVATE=none asks for a run with no redactions; check such output before
# publishing anything (sanitize_extracts.py does, and applies the table's sanitize rules to every string).
_P = paths.private()
if not _P and os.environ.get('TIMELINE_PRIVATE') != 'none':
    sys.exit(f'no privacy table at {paths.PRIVATE_TABLE}; set TIMELINE_PRIVATE=none to run without redactions')
from datetime import datetime, timezone, timedelta

try:
    from zoneinfo import ZoneInfo
    PT = ZoneInfo('America/Los_Angeles')
except Exception:  # pragma: no cover
    PT = timezone(timedelta(hours=-7))

PROJ = paths.PROJ
SID = paths.SID
MAIN = paths.MAIN
SUB = paths.SUB
WFJSON = paths.WFJSON
OUTDIR = paths.TL
OUT = f'{OUTDIR}/agents.json'
MAIN_AGENT_JSON = f'{OUTDIR}/main_agent.json'

GAP = 180.0            # seconds: gaps shorter than this are "busy"
GRID_START = datetime(2026, 9, 19, 16, 0, tzinfo=timezone.utc)
ACTIVITY_TYPES = {'user', 'assistant', 'attachment', 'system'}
# events that can fire while the agent is idle; they do not mark activity
IDLE_SYSTEM_SUBTYPES = {'away_summary', 'bridge_status', 'informational'}
IDLE_ATTACHMENT_TYPES = {'remote_session_change'}

# Privacy: the report for the lab lead stays unnamed on the page.
PRIVATE_WF = _P.get('private_workflows', {})
# Privacy: no names of other people in text meant for the page.
NAME_REDACTIONS = [tuple(x) for x in _P.get('agent_name_redactions', [])]


def redact(text):
    for pat, rep in NAME_REDACTIONS:
        text = re.sub(pat, rep, text or '')
    return text


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00'))
    except Exception:
        return None


def iso(dt):
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') if dt else None


def pdt(dt):
    return dt.astimezone(PT).strftime('%a %b %d %H:%M') if dt else None


def busy_intervals(times, gap=GAP):
    """times sorted list of datetimes -> [[start, end], ...] merging gaps < gap."""
    out = []
    for t in times:
        if out and (t - out[-1][1]).total_seconds() < gap:
            if t > out[-1][1]:
                out[-1][1] = t
        else:
            out.append([t, t])
    return out


def merge_waits(busy, waits, gap=GAP):
    """busy intervals plus [tool_use, tool_result] spans of long tool calls, merged."""
    iv = [[a, b] for a, b in busy] + [[parse_ts(w[0]), parse_ts(w[1])] for w in waits]
    iv.sort()
    out = []
    for a, b in iv:
        if out and (a - out[-1][1]).total_seconds() < gap:
            if b > out[-1][1]:
                out[-1][1] = b
        else:
            out.append([a, b])
    return out


def usage_add(acc, u):
    for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens'):
        acc[k] = acc.get(k, 0) + int(u.get(k) or 0)


def scan(path, skip_uuids=None):
    """Stream one transcript.  Returns dict with activity times, message usages,
    tool calls, models, long tool waits, errors."""
    times = []
    msgs = {}            # message.id -> {'usage': {..max..}, 'model':, 'ts':}
    tool_ids = {}        # tool_use id -> (name, ts)
    tool_results = {}    # tool_use id -> ts
    n_events = 0
    n_skipped = 0
    bad = 0
    api_errors = []
    last_text = None
    for line in open(path, encoding='utf-8', errors='replace'):
        try:
            o = json.loads(line)
        except Exception:
            bad += 1
            continue
        if skip_uuids is not None and o.get('uuid') in skip_uuids:
            n_skipped += 1
            continue
        t = o.get('type')
        ts = parse_ts(o.get('timestamp'))
        idle = ((t == 'system' and o.get('subtype') in IDLE_SYSTEM_SUBTYPES) or
                (t == 'attachment' and (o.get('attachment') or {}).get('type') in IDLE_ATTACHMENT_TYPES))
        if t in ACTIVITY_TYPES and ts and not idle:
            times.append(ts)
            n_events += 1
        m = o.get('message') if isinstance(o.get('message'), dict) else None
        if t == 'assistant' and m:
            mid = m.get('id') or o.get('uuid')
            u = m.get('usage') or {}
            rec = msgs.setdefault(mid, {'usage': {}, 'model': m.get('model'), 'ts': ts})
            for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens'):
                v = int(u.get(k) or 0)
                if v > rec['usage'].get(k, 0):
                    rec['usage'][k] = v
            if ts and (rec['ts'] is None or ts < rec['ts']):
                rec['ts'] = ts
            if o.get('isApiErrorMessage') or m.get('model') == '<synthetic>':
                txt = ''
                for b in m.get('content') or []:
                    if isinstance(b, dict) and b.get('type') == 'text':
                        txt += b.get('text', '')
                if txt and not txt.startswith('No response requested'):
                    if 'safeguards flagged' in txt or '/legal/aup' in txt:
                        txt = 'API error (usage-policy filter)'   # the category, not the message
                    api_errors.append((iso(ts), txt[:120]))
            for b in m.get('content') or []:
                if isinstance(b, dict) and b.get('type') == 'tool_use':
                    tool_ids.setdefault(b.get('id'), (b.get('name'), ts))
        if t == 'user' and m and isinstance(m.get('content'), list):
            for b in m['content']:
                if isinstance(b, dict) and b.get('type') == 'tool_result':
                    tool_results.setdefault(b.get('tool_use_id'), ts)
    times.sort()
    # long tool waits: gaps >= GAP that sit between a tool_use and its result
    waits = []
    for tid, (name, ts0) in tool_ids.items():
        ts1 = tool_results.get(tid)
        if ts0 and ts1 and (ts1 - ts0).total_seconds() >= GAP:
            waits.append([iso(ts0), iso(ts1), name, round((ts1 - ts0).total_seconds() / 60, 1)])
    waits.sort()
    pending = [tid for tid in tool_ids if tid not in tool_results]
    return {'times': times, 'msgs': msgs, 'tools': tool_ids, 'n_events': n_events,
            'n_skipped': n_skipped, 'bad_lines': bad, 'api_errors': api_errors,
            'long_tool_waits': waits, 'pending_tools': len(pending)}


def uuids_of(path):
    s = set()
    for line in open(path, encoding='utf-8', errors='replace'):
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get('uuid'):
            s.add(o['uuid'])
    return s


# ---------------------------------------------------------------- workflows
def load_workflow_launches():
    """Workflow tool calls in the main transcript -> run id, name, launch ts, task id."""
    uses = {}
    order = []
    for line in open(MAIN, encoding='utf-8', errors='replace'):
        if '"Workflow"' not in line and 'Workflow launched' not in line and 'tool_use_error' not in line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        m = o.get('message') if isinstance(o.get('message'), dict) else None
        if not m or not isinstance(m.get('content'), list):
            continue
        for b in m['content']:
            if not isinstance(b, dict):
                continue
            if b.get('type') == 'tool_use' and b.get('name') == 'Workflow':
                inp = b.get('input') or {}
                uses[b['id']] = {'ts': o.get('timestamp'), 'resume': inp.get('resumeFromRunId'), 'res': None}
                order.append(b['id'])
            elif b.get('type') == 'tool_result' and b.get('tool_use_id') in uses:
                c = b.get('content')
                if isinstance(c, list):
                    c = ' '.join(x.get('text', '') for x in c if isinstance(x, dict))
                uses[b['tool_use_id']]['res'] = str(c)
    launches = []
    for i in order:
        u = uses[i]
        txt = u['res'] or ''
        ok = 'Workflow launched' in txt
        d = re.search(r'Transcript dir: \S*/(wf_[0-9a-f]{8}-[0-9a-f]{3})', txt)
        s = re.search(r'Script file: \S*/scripts/([\w.-]+?)-(wf_[0-9a-f]{8}-[0-9a-f]{3})\.js', txt)
        tid = re.search(r'Task ID: (\w+)', txt)
        launches.append({'ts': u['ts'], 'ok': ok, 'resume_of': u['resume'],
                         'run_id': d.group(1) if d else (u['resume'] if not ok else None),
                         'name': s.group(1) if s else None,
                         'task_id': tid.group(1) if tid else None,
                         'error': None if ok else txt[:100]})
    return launches


def main():
    now = datetime.now(timezone.utc)
    anomalies = []

    # ---------------- inventory of subagent transcripts
    rows = []
    for f in sorted(glob.glob(f'{SUB}/agent-*.jsonl')):
        rows.append({'path': f, 'wf': None})
    wf_dirs = sorted(glob.glob(f'{SUB}/workflows/wf_*'))
    for d in wf_dirs:
        for f in sorted(glob.glob(f'{d}/agent-*.jsonl')):
            rows.append({'path': f, 'wf': os.path.basename(d)})
    path_by_id = {}
    for r in rows:
        r['id'] = os.path.basename(r['path'])[len('agent-'):-len('.jsonl')]
        mp = r['path'][:-len('.jsonl')] + '.meta.json'
        r['meta'] = json.load(open(mp)) if os.path.exists(mp) else {}
        if not r['meta']:
            anomalies.append(f"agent {r['id']}: no .meta.json")
        path_by_id[r['id']] = r['path']

    # ---------------- workflow metadata
    launches = load_workflow_launches()
    wf_names = {}
    for L in launches:
        if L['run_id'] and L['name']:
            wf_names.setdefault(L['run_id'], L['name'])
    wf_info = {}
    for d in wf_dirs:
        run = os.path.basename(d)
        info = {'run_id': run, 'name': wf_names.get(run), 'json': False, 'journal': {},
                'progress': {}}
        jf = f'{WFJSON}/{run}.json'
        if os.path.exists(jf):
            j = json.load(open(jf))
            info.update(json=True, name=j.get('workflowName') or info['name'], status=j.get('status'),
                        json_agent_count=j.get('agentCount'), json_total_tokens=j.get('totalTokens'),
                        json_total_tool_calls=j.get('totalToolCalls'), json_duration_ms=j.get('durationMs'),
                        json_start=iso(datetime.fromtimestamp(j['startTime'] / 1000, timezone.utc)) if j.get('startTime') else None,
                        default_model=j.get('defaultModel'),
                        summary=(j.get('summary') or '')[:160],
                        phases=[p.get('title') for p in j.get('phases') or []])
            for a in j.get('workflowProgress') or []:
                if a.get('type') == 'workflow_agent' and a.get('agentId'):
                    info['progress'][a['agentId']] = {'state': a.get('state'), 'label': a.get('label'),
                                                      'model': a.get('model'), 'error': a.get('error'),
                                                      'attempt': a.get('attempt')}
        else:
            info['status'] = 'running' if any(L['run_id'] == run for L in launches) else 'unknown'
        jr = f'{d}/journal.jsonl'
        if os.path.exists(jr):
            cnt = collections.Counter()
            for line in open(jr):
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                cnt[o.get('type')] += 1
                aid = o.get('agentId')
                if aid:
                    e = info['journal'].setdefault(aid, {})
                    if o['type'] == 'started':
                        e.update(label=o.get('label'), phase=o.get('phase'), state='started')
                    elif o['type'] in ('result', 'failed'):
                        e['state'] = 'done' if o['type'] == 'result' else 'failed'
            info['journal_counts'] = dict(cnt)
        wf_info[run] = info

    # ---------------- scan main
    print('scanning main ...', file=sys.stderr)
    main_scan = scan(MAIN)

    # ---------------- scan agents (parents before forks for uuid skipping)
    depth = lambda r: r['meta'].get('spawnDepth') or 1
    rows.sort(key=lambda r: (depth(r), r['id']))
    uuid_cache = {}
    for i, r in enumerate(rows):
        parent = r['meta'].get('parentAgentId')
        skip = None
        if parent and parent in path_by_id:
            if parent not in uuid_cache:
                uuid_cache[parent] = uuids_of(path_by_id[parent])
            skip = uuid_cache[parent]
        elif parent:
            anomalies.append(f"agent {r['id']}: parent {parent} transcript not found")
        r['scan'] = scan(r['path'], skip)
        if (i + 1) % 100 == 0:
            print(f'  scanned {i+1}/{len(rows)}', file=sys.stderr)

    # ---------------- attribute message ids to one owner
    owners = {}   # mid -> (depth, ts, owner_key)
    def claim(mid, d, ts, key):
        cur = owners.get(mid)
        tsv = ts or now
        if cur is None or (d, tsv) < (cur[0], cur[1]):
            owners[mid] = (d, tsv, key)
    for mid, rec in main_scan['msgs'].items():
        claim(mid, 0, rec['ts'], 'main')
    for r in rows:
        for mid, rec in r['scan']['msgs'].items():
            claim(mid, depth(r), rec['ts'], r['id'])
    dup_ids = 0

    def tally(scanres, key):
        nonlocal dup_ids
        tok = {}
        models = collections.Counter()
        n = 0
        for mid, rec in scanres['msgs'].items():
            if owners[mid][2] != key:
                dup_ids += 1
                continue
            n += 1
            usage_add(tok, rec['usage'])
            if rec['model'] and rec['model'] != '<synthetic>':
                models[rec['model']] += 1
        tok = {'input': tok.get('input_tokens', 0), 'cache_creation': tok.get('cache_creation_input_tokens', 0),
               'cache_read': tok.get('cache_read_input_tokens', 0), 'output': tok.get('output_tokens', 0)}
        tok['total'] = sum(tok.values())
        return tok, dict(models.most_common()), n

    # ---------------- build agent rows
    agents = []
    for r in rows:
        s = r['scan']
        m = r['meta']
        tok, models, nmsg = tally(s, r['id'])
        times = s['times']
        start = times[0] if times else None
        end = times[-1] if times else None
        busy = busy_intervals(times)
        wf = r['wf']
        wi = wf_info.get(wf) if wf else None
        jrec = (wi or {}).get('journal', {}).get(r['id'], {})
        prec = (wi or {}).get('progress', {}).get(r['id'], {})
        if wf:
            kind = 'workflow'
        elif m.get('isFork') or m.get('agentType') == 'fork':
            kind = 'fork'
        else:
            kind = 'agent'
        # status
        if wf:
            status = prec.get('state') or jrec.get('state') or 'unknown'
            if status in ('started', 'progress', 'start'):
                status = 'running' if wi.get('status') == 'running' else (
                    'killed' if wi.get('status') == 'killed' else status)
            if jrec.get('state') == 'failed' and status == 'done':
                status = 'failed'
        else:
            status = 'done'
        err = prec.get('error')
        if not err and s['api_errors']:
            err = s['api_errors'][-1][1]
        lim = re.search(r'(session|weekly|usage|rate) limit', err or '', re.I)
        if lim:
            err_kind = lim.group(1).lower() + '-limit'
        elif err:
            err_kind = 'error'
        else:
            err_kind = None
        if wf and jrec.get('state') == 'failed' and status not in ('failed', 'error'):
            status = 'failed'
        in_progress = bool(end and (now - end).total_seconds() < 900 and wf and wi.get('status') == 'running')
        if in_progress:
            status = 'running'
        label = jrec.get('label') or prec.get('label') or m.get('description')
        wf_name = wi.get('name') if wi else None
        private = wf_name in PRIVATE_WF
        tools = collections.Counter(n for (n, _) in s['tools'].values())
        agents.append({
            'id': r['id'],
            'kind': kind,
            'label': redact(label),
            'description': redact(m.get('description')),
            'agent_type': m.get('agentType'),
            'workflow_run': wf,
            'workflow': (PRIVATE_WF[wf_name] if private else wf_name) if wf else None,
            'phase': jrec.get('phase') or m.get('workflowPhase'),
            'parent': m.get('parentAgentId'),
            'spawn_depth': m.get('spawnDepth'),
            'request_shape': m.get('requestShape'),
            'spawn_tool_use_id': m.get('toolUseId'),
            'start': iso(start), 'end': iso(end),
            'start_pdt': pdt(start), 'end_pdt': pdt(end),
            'span_min': round((end - start).total_seconds() / 60, 1) if start else 0,
            'busy_min': round(sum((b - a).total_seconds() for a, b in busy) / 60, 1),
            'busy': [[iso(a), iso(b)] for a, b in busy],
            'busy_incl_tool_waits': [[iso(a), iso(b)] for a, b in merge_waits(busy, s['long_tool_waits'])],
            'tool_calls': len(s['tools']),
            'tools': dict(tools.most_common(8)),
            'assistant_messages': nmsg,
            'tokens': tok,
            'model': next(iter(models), None),
            'models': models,
            'status': status,
            'error_kind': err_kind,
            'error_at': s['api_errors'][-1][0] if s['api_errors'] else None,
            'events': s['n_events'],
            'copied_parent_events_skipped': s['n_skipped'],
            'long_tool_waits': s['long_tool_waits'],
        })
        if s['bad_lines']:
            anomalies.append(f"agent {r['id']}: {s['bad_lines']} unparseable lines")
        if not times:
            anomalies.append(f"agent {r['id']} ({label}): transcript has no timestamped events")

    # ---------------- main agent
    main_tok, main_models, main_nmsg = tally(main_scan, 'main')
    main_busy = busy_intervals(main_scan['times'])
    main_busy_strict = main_busy
    main_source = 'computed from main transcript (gap < 3 min over user/assistant/attachment/system events)'
    if os.path.exists(MAIN_AGENT_JSON):
        try:
            mj = json.load(open(MAIN_AGENT_JSON))
            cand = None
            for k in ('busy', 'busy_intervals', 'main_busy', 'intervals'):
                v = mj.get(k) if isinstance(mj, dict) else None
                if v is None and isinstance(mj, dict) and isinstance(mj.get('main'), dict):
                    v = mj['main'].get(k)
                if isinstance(v, list) and v:
                    cand = v
                    break
            parsed = []
            for x in cand or []:
                a, b = (x[0], x[1]) if isinstance(x, (list, tuple)) else (x.get('start'), x.get('end'))
                pa, pb = parse_ts(a), parse_ts(b)
                if pa and pb:
                    parsed.append([pa, pb])
            if parsed:
                main_busy = parsed
                main_source = 'main_agent.json'
        except Exception as e:
            anomalies.append(f'main_agent.json present but unreadable: {e}')
    main_start = main_scan['times'][0]
    main_end = main_scan['times'][-1]
    main_row = {
        'start': iso(main_start), 'end': iso(main_end),
        'start_pdt': pdt(main_start), 'end_pdt': pdt(main_end),
        'busy_source': main_source,
        'busy_min': round(sum((b - a).total_seconds() for a, b in main_busy) / 60, 1),
        'busy': [[iso(a), iso(b)] for a, b in main_busy],
        'busy_incl_tool_waits': [[iso(a), iso(b)] for a, b in merge_waits(main_busy, main_scan['long_tool_waits'])],
        'busy_strict_min': round(sum((b - a).total_seconds() for a, b in main_busy_strict) / 60, 1),
        'busy_strict': [[iso(a), iso(b)] for a, b in main_busy_strict],
        'tool_calls': len(main_scan['tools']),
        'tools': dict(collections.Counter(n for (n, _) in main_scan['tools'].values()).most_common(12)),
        'assistant_messages': main_nmsg,
        'tokens': main_tok,
        'models': main_models,
        'long_tool_waits': main_scan['long_tool_waits'],
    }
    if main_scan['api_errors']:
        main_row['api_errors'] = main_scan['api_errors'][:20]

    # ---------------- workflows table
    workflows = []
    by_wf = collections.defaultdict(list)
    for a in agents:
        if a['workflow_run']:
            by_wf[a['workflow_run']].append(a)
    for run, wi in sorted(wf_info.items(), key=lambda kv: min([a['start'] for a in by_wf[kv[0]] if a['start']] or ['9'])):
        ags = by_wf[run]
        tok = collections.Counter()
        for a in ags:
            tok.update(a['tokens'])
        starts = [a['start'] for a in ags if a['start']]
        ends = [a['end'] for a in ags if a['end']]
        lts = [L for L in launches if L['run_id'] == run and L['ok']]
        name = wi.get('name')
        private = name in PRIVATE_WF
        states = collections.Counter(a['status'] for a in ags)
        row = {
            'run_id': run,
            'name': PRIVATE_WF[name] if private else name,
            'private': private,
            'status': wi.get('status'),
            'launches': [L['ts'] for L in lts],
            'launches_pdt': [pdt(parse_ts(L['ts'])) for L in lts],
            'resumed': any(L['resume_of'] == run for L in lts),
            'first_event': min(starts) if starts else None,
            'last_event': max(ends) if ends else None,
            'first_event_pdt': pdt(parse_ts(min(starts))) if starts else None,
            'last_event_pdt': pdt(parse_ts(max(ends))) if ends else None,
            'agents': len(ags),
            'agent_states': dict(states),
            'phases': [] if private else wi.get('phases', []),
            'summary': '' if private else redact(wi.get('summary', '')),
            'tool_calls': sum(a['tool_calls'] for a in ags),
            'tokens': dict(tok),
            'busy_agent_min': round(sum(a['busy_min'] for a in ags), 1),
            'json_agent_count': wi.get('json_agent_count'),
            'json_total_tokens': wi.get('json_total_tokens'),
            'json_total_tool_calls': wi.get('json_total_tool_calls'),
            'journal_counts': wi.get('journal_counts'),
        }
        workflows.append(row)

    # ---------------- concurrency grid
    last = max([main_end] + [parse_ts(a['end']) for a in agents if a['end']])
    nmin = int((last - GRID_START).total_seconds() // 60) + 1
    sub = [0] * nmin
    wfb = [0] * nmin
    agb = [0] * nmin
    alive = [0] * nmin
    mainb = [0] * nmin
    busy_sets = [None] * nmin

    def mark(arr, a, b, ident=None):
        i0 = max(0, int((a - GRID_START).total_seconds() // 60))
        i1 = min(nmin - 1, int((b - GRID_START).total_seconds() // 60))
        for i in range(i0, i1 + 1):
            arr[i] += 1
            if ident is not None:
                if busy_sets[i] is None:
                    busy_sets[i] = []
                busy_sets[i].append(ident)

    for a in agents:
        seen_min = set()
        for s_, e_ in a['busy']:
            pa, pb = parse_ts(s_), parse_ts(e_)
            i0 = max(0, int((pa - GRID_START).total_seconds() // 60))
            i1 = min(nmin - 1, int((pb - GRID_START).total_seconds() // 60))
            for i in range(i0, i1 + 1):
                if i in seen_min:
                    continue
                seen_min.add(i)
                sub[i] += 1
                (wfb if a['kind'] == 'workflow' else agb)[i] += 1
                if busy_sets[i] is None:
                    busy_sets[i] = []
                busy_sets[i].append(a['id'])
        if a['start']:
            mark(alive, parse_ts(a['start']), parse_ts(a['end']))
    for s_, e_ in main_busy:
        i0 = max(0, int((s_ - GRID_START).total_seconds() // 60))
        i1 = min(nmin - 1, int((e_ - GRID_START).total_seconds() // 60))
        for i in range(i0, i1 + 1):
            mainb[i] = 1
    total = [sub[i] + mainb[i] for i in range(nmin)]
    # variant: a pending long tool call (>= 3 min) counts as busy
    subw = [0] * nmin
    mainw = [0] * nmin
    for a in agents:
        seen_min = set()
        for s_, e_ in a['busy_incl_tool_waits']:
            pa, pb = parse_ts(s_), parse_ts(e_)
            for i in range(max(0, int((pa - GRID_START).total_seconds() // 60)),
                           min(nmin - 1, int((pb - GRID_START).total_seconds() // 60)) + 1):
                if i not in seen_min:
                    seen_min.add(i)
                    subw[i] += 1
    for s_, e_ in main_row['busy_incl_tool_waits']:
        pa, pb = parse_ts(s_), parse_ts(e_)
        for i in range(max(0, int((pa - GRID_START).total_seconds() // 60)),
                       min(nmin - 1, int((pb - GRID_START).total_seconds() // 60)) + 1):
            mainw[i] = 1
    mains = [0] * nmin
    for s_, e_ in main_busy_strict:
        for i in range(max(0, int((s_ - GRID_START).total_seconds() // 60)),
                       min(nmin - 1, int((e_ - GRID_START).total_seconds() // 60)) + 1):
            mains[i] = 1
    main_row['busy_incl_tool_waits_min'] = round(sum((parse_ts(b) - parse_ts(a)).total_seconds()
                                                     for a, b in main_row['busy_incl_tool_waits']) / 60, 1)

    def peak_of(arr):
        mx = max(arr)
        idx = [i for i, v in enumerate(arr) if v == mx]
        spans = []
        for i in idx:
            if spans and spans[-1][1] == i - 1:
                spans[-1][1] = i
            else:
                spans.append([i, i])
        t = lambda i: GRID_START + timedelta(minutes=i)
        return {'value': mx, 'first_minute': iso(t(idx[0])), 'first_minute_pdt': pdt(t(idx[0])),
                'minutes_at_peak': len(idx),
                'spans': [[iso(t(a)), iso(t(b) + timedelta(seconds=59)), pdt(t(a)), pdt(t(b))] for a, b in spans[:20]]}

    pk_sub = peak_of(sub)
    pk_tot = peak_of(total)
    i_pk = int((parse_ts(pk_sub['first_minute']) - GRID_START).total_seconds() // 60)
    at_peak = collections.Counter()
    amap = {a['id']: a for a in agents}
    for aid in busy_sets[i_pk] or []:
        a = amap[aid]
        at_peak[a['workflow'] or ('fork' if a['kind'] == 'fork' else 'Agent tool')] += 1
    pk_sub['busy_by_source'] = dict(at_peak)
    # peak of 'alive' too
    pk_alive = peak_of(alive)
    pk_subw = peak_of(subw)
    # peak without agents that ended on an error (limit hits make many agents 'busy' in one minute)
    ok = [0] * nmin
    for a in agents:
        if a['error_kind'] or a['status'] in ('failed', 'error'):
            continue
        seen_min = set()
        for s_, e_ in a['busy']:
            pa, pb = parse_ts(s_), parse_ts(e_)
            for i in range(max(0, int((pa - GRID_START).total_seconds() // 60)),
                           min(nmin - 1, int((pb - GRID_START).total_seconds() // 60)) + 1):
                if i not in seen_min:
                    seen_min.add(i)
                    ok[i] += 1
    pk_ok = peak_of(ok)
    # highest level held for >= 10 consecutive minutes
    def sustained(arr, width=10):
        best, at = 0, None
        for i in range(0, len(arr) - width + 1):
            v = min(arr[i:i + width])
            if v > best:
                best, at = v, i
        t = GRID_START + timedelta(minutes=at) if at is not None else None
        return {'value': best, 'window_minutes': width, 'first_minute': iso(t), 'first_minute_pdt': pdt(t)}
    pk_sus = sustained(sub)

    # hourly summary (PDT) for convenience
    hourly = collections.OrderedDict()
    for i in range(nmin):
        t = (GRID_START + timedelta(minutes=i)).astimezone(PT)
        key = t.strftime('%Y-%m-%d %H:00')
        h = hourly.setdefault(key, {'sub_busy_agent_min': 0, 'main_busy_min': 0, 'max_sub': 0})
        h['sub_busy_agent_min'] += sub[i]
        h['main_busy_min'] += mainb[i]
        h['max_sub'] = max(h['max_sub'], sub[i])

    daily = collections.OrderedDict()
    for i in range(nmin):
        t = (GRID_START + timedelta(minutes=i)).astimezone(PT)
        key = t.strftime('%Y-%m-%d')
        dd = daily.setdefault(key, {'max_sub': 0, 'max_sub_at_pdt': None, 'sub_busy_agent_h': 0,
                                    'main_busy_h': 0, 'main_busy_incl_tool_waits_h': 0})
        if sub[i] > dd['max_sub']:
            dd['max_sub'] = sub[i]
            dd['max_sub_at_pdt'] = t.strftime('%H:%M')
        dd['sub_busy_agent_h'] += sub[i] / 60
        dd['main_busy_h'] += mainb[i] / 60
        dd['main_busy_incl_tool_waits_h'] += mainw[i] / 60
        dd['main_busy_strict_h'] = dd.get('main_busy_strict_h', 0) + mains[i] / 60
    for dd in daily.values():
        for k in ('sub_busy_agent_h', 'main_busy_h', 'main_busy_incl_tool_waits_h', 'main_busy_strict_h'):
            dd[k] = round(dd[k], 1)

    concurrency = {
        'start': iso(GRID_START), 'step_s': 60, 'n': nmin, 'end': iso(GRID_START + timedelta(minutes=nmin - 1)),
        'note': 'value i covers minute [start + i min, +60 s); an agent counts once per minute if any busy interval overlaps it',
        'sub_busy': sub, 'workflow_busy': wfb, 'agent_tool_busy': agb, 'main_busy': mainb,
        'total_busy': total, 'alive': alive,
        'sub_busy_incl_tool_waits': subw, 'main_busy_incl_tool_waits': mainw,
        'main_busy_strict': mains,
        'main_busy_source': main_source,
    }

    # ---------------- totals
    sub_tok = collections.Counter()
    for a in agents:
        sub_tok.update(a['tokens'])
    by_kind = collections.defaultdict(collections.Counter)
    for a in agents:
        by_kind[a['kind']].update(a['tokens'])
    model_tok = collections.defaultdict(collections.Counter)
    # per-model tokens: recompute from owners
    for mid, (d, ts, key) in owners.items():
        pass
    def add_models(scanres, key):
        for mid, rec in scanres['msgs'].items():
            if owners[mid][2] != key or not rec['model'] or rec['model'] == '<synthetic>':
                continue
            u = rec['usage']
            model_tok[rec['model']]['output'] += u.get('output_tokens', 0)
            model_tok[rec['model']]['input_all'] += (u.get('input_tokens', 0) + u.get('cache_creation_input_tokens', 0)
                                                     + u.get('cache_read_input_tokens', 0))
            model_tok[rec['model']]['messages'] += 1
            model_tok[rec['model']]['main' if key == 'main' else 'sub_messages'] += 1
    add_models(main_scan, 'main')
    for r in rows:
        add_models(r['scan'], r['id'])

    totals = {
        'agents': len(agents),
        'agents_by_kind': dict(collections.Counter(a['kind'] for a in agents)),
        'workflow_runs': len(workflows),
        'workflow_launch_calls': len(launches),
        'workflow_launch_calls_ok': sum(1 for L in launches if L['ok']),
        'agent_tool_calls_in_main': main_row['tools'].get('Agent', 0),
        'tokens_subagents': dict(sub_tok),
        'tokens_subagents_by_kind': {k: dict(v) for k, v in by_kind.items()},
        'tokens_main': main_tok,
        'tokens_all': dict(sub_tok + collections.Counter(main_tok)),
        'tool_calls_subagents': sum(a['tool_calls'] for a in agents),
        'tool_calls_main': main_row['tool_calls'],
        'busy_agent_hours_subagents': round(sum(a['busy_min'] for a in agents) / 60, 1),
        'busy_hours_main': round(main_row['busy_min'] / 60, 1),
        'busy_hours_main_strict_gap_rule': round(main_row['busy_strict_min'] / 60, 1),
        'busy_hours_main_incl_tool_waits': round(main_row['busy_incl_tool_waits_min'] / 60, 1),
        'by_model': {k: dict(v) for k, v in model_tok.items()},
        'duplicate_message_ids_skipped': dup_ids,
    }

    # ---------------- anomalies
    for w in workflows:
        jc = w.get('journal_counts') or {}
        if jc.get('failed'):
            ul = collections.Counter(a['error_kind'] for a in by_wf[w['run_id']] if a['error_kind'])
            anomalies.append(f"workflow {w['name']} ({w['run_id']}): {jc.get('failed')} failed agent starts "
                             f"of {jc.get('started')} (transcripts ending on errors: {dict(ul)}); status {w['status']}")
        if w['status'] == 'killed':
            anomalies.append(f"workflow {w['name']} ({w['run_id']}) was killed; agent states {w['agent_states']}")
        if w['resumed']:
            anomalies.append(f"workflow {w['name']} ({w['run_id']}) was resumed (launches at {', '.join(w['launches_pdt'])} PDT)")
        if w['status'] == 'running':
            anomalies.append(f"workflow {w['name']} ({w['run_id']}) still running at extraction; numbers partial")
        if w['json_total_tokens'] and w['tokens'].get('total'):
            ratio = w['tokens']['total'] / w['json_total_tokens']
            w['tokens_vs_json_ratio'] = round(ratio, 2)
    for L in launches:
        if not L['ok']:
            anomalies.append(f"Workflow call at {pdt(parse_ts(L['ts']))} PDT failed to launch: {L['error'][:80]}")
    names = collections.Counter(w['name'] for w in workflows)
    for n, c in names.items():
        if c > 1:
            anomalies.append(f"workflow name {n} used by {c} runs")
    for kind in sorted({a['error_kind'] for a in agents if a['error_kind'] and a['error_kind'].endswith('-limit')}):
        ul_agents = [a for a in agents if a['error_kind'] == kind]
        ts = sorted(a['error_at'] or a['end'] for a in ul_agents if a['end'])
        wfs = collections.Counter(a['workflow'] or a['kind'] for a in ul_agents)
        anomalies.append(f"{len(ul_agents)} agents ended on a {kind} error, between {pdt(parse_ts(ts[0]))} and "
                         f"{pdt(parse_ts(ts[-1]))} PDT ({dict(wfs)})")
    if main_scan['api_errors']:
        anomalies.append(f"main agent: {len(main_scan['api_errors'])} API error messages, e.g. "
                         + '; '.join(f"{pdt(parse_ts(t))} PDT: {x[:60]}" for t, x in main_scan['api_errors'][:4]))
    anomalies.append('workflow JSON totalTokens uses a different metric than transcript usage (it is neither the sum '
                     'with nor without cache reads); tool-call counts match exactly for completed runs')
    forks = [a for a in agents if a['copied_parent_events_skipped']]
    if forks:
        anomalies.append(f"{len(forks)} fork transcripts begin with a copy of their parent's history "
                         f"({sum(a['copied_parent_events_skipped'] for a in forks)} events skipped; "
                         f"{dup_ids} duplicate message ids not double counted)")
    lw = sorted(((w[3], a['id'], a['label'], w[2]) for a in agents for w in a['long_tool_waits']), reverse=True)
    if lw:
        anomalies.append(f"{len(lw)} tool calls in subagents took >= 3 min (idle by the gap rule while waiting); longest {lw[0][0]} min "
                         f"({lw[0][3]} in {lw[0][2]})")
    if main_row['long_tool_waits']:
        mw = sorted(main_row['long_tool_waits'], key=lambda x: -x[3])
        anomalies.append(f"main agent: {len(mw)} tool calls took >= 3 min; longest {mw[0][3]} min ({mw[0][2]} at {pdt(parse_ts(mw[0][0]))} PDT)")
    other = paths.PRE
    if os.path.exists(other):
        tso = []
        n = 0
        for line in open(other, encoding='utf-8', errors='replace'):
            n += 1
            try:
                o = json.loads(line)
            except Exception:
                continue
            if o.get('timestamp'):
                tso.append(o['timestamp'])
        if tso:
            anomalies.append(f"separate session 2e4feded: {n} lines, {min(tso)} .. {max(tso)} (a few seconds, just before the main session; not counted)")
    if len(main_models) > 1:
        anomalies.append(f"main agent used several models: {main_models}")

    out = {
        'generated': iso(now),
        'session': SID,
        'timezone_display': 'America/Los_Angeles',
        'busy_rule': 'events merged into one busy interval when consecutive timestamps are < 3 min apart',
        'token_rule': 'usage per message.id = per-field max over its lines; each message.id counted once, owned by the shallowest transcript',
        'totals': totals,
        'peak': {'subagents': pk_sub, 'subagents_plus_main': pk_tot, 'alive_subagents': pk_alive,
                 'subagents_incl_tool_waits': pk_subw,
                 'subagents_excluding_errored': pk_ok,
                 'subagents_sustained_10min': pk_sus},
        'main': main_row,
        'workflows': workflows,
        'workflow_launches': [{k: v for k, v in L.items() if k != 'error'} | {'ts_pdt': pdt(parse_ts(L['ts'])),
                               'name': PRIVATE_WF.get(L['name'], L['name'])} for L in launches],
        'agents': sorted(agents, key=lambda a: a['start'] or '9'),
        'daily_pdt': daily,
        'hourly_pdt': hourly,
        'concurrency': concurrency,
        'anomalies': anomalies,
    }
    paths.ensure_tl()
    with open(OUT, 'w') as fh:
        json.dump(out, fh, separators=(',', ':'))
    print(json.dumps({'out': OUT, 'size': os.path.getsize(OUT), 'totals': totals, 'peak_sub': pk_sub,
                      'peak_total': {k: pk_tot[k] for k in ('value', 'first_minute_pdt', 'minutes_at_peak')},
                      'peak_alive': {k: pk_alive[k] for k in ('value', 'first_minute_pdt')},
                      'main': {k: main_row[k] for k in ('start_pdt', 'end_pdt', 'busy_min', 'busy_strict_min', 'busy_incl_tool_waits_min', 'tool_calls', 'tokens', 'models', 'busy_source')},
                      'peak_sub_incl_waits': {k: pk_subw[k] for k in ('value', 'first_minute_pdt')},
                      'peak_sub_excl_errored': {k: pk_ok[k] for k in ('value', 'first_minute_pdt', 'minutes_at_peak', 'spans')},
                      'peak_sub_sustained_10min': pk_sus,
                      'anomalies': anomalies}, indent=1, default=str))


if __name__ == '__main__':
    main()
