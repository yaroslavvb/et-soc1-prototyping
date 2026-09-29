#!/usr/bin/env python3
"""Stream every transcript (main, earlier session, subagents, workflow agents) line by line and
collect each Bash tool_use whose command mentions spacesheep, with its tool_result (truncated).
Output: work/spacesheep_calls.jsonl (one row per call). Never loads a transcript whole."""
import json, os, glob, sys, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402

P = paths.PROJ
MAIN = paths.SID
OUT = os.path.join(paths.ensure_tl(), 'work')
os.makedirs(OUT, exist_ok=True)

files = [paths.MAIN, paths.PRE]
files += sorted(glob.glob(os.path.join(P, MAIN, 'subagents', '*.jsonl')))
# skip the timeline's own runs, whose commands only search for spacesheep calls: the first build's workflow and, in
# $TIMELINE_SKIP (comma-separated parts of a path), a later refresh's own transcripts
SKIP = ['wf_e5cc1787-8ed'] + [x for x in os.environ.get('TIMELINE_SKIP', '').split(',') if x]
files += [f for f in sorted(glob.glob(os.path.join(P, MAIN, 'subagents', 'workflows', '**', '*.jsonl'), recursive=True))
          if not any(k in f for k in SKIP)]
CUTOFF = paths.CUTOFF   # ISO time: calls after it are left out (the page's snapshot)


def result_text(c):
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        out = []
        for x in c:
            if isinstance(x, dict) and x.get('type') == 'text':
                out.append(x.get('text', ''))
        return '\n'.join(out)
    return ''


def src_label(f):
    r = os.path.relpath(f, P)
    if r.startswith(MAIN + '.jsonl'):
        return 'main'
    if r.startswith('2e4feded'):
        return 'earlier-session'
    return r.replace(MAIN + '/', '')


rows = []
nfiles = 0
for f in files:
    nfiles += 1
    pending = {}
    anyb = {}
    meta = None
    mp = f[:-len('.jsonl')] + '.meta.json'
    if os.path.exists(mp):
        try:
            meta = json.load(open(mp))
        except Exception:
            meta = None
    with open(f, 'rb') as fh:
        for line in fh:
            if b'spacesheep' not in line and b'tool_result' not in line and b'"Bash"' not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            msg = d.get('message') or {}
            content = msg.get('content')
            if not isinstance(content, list):
                continue
            ts = d.get('timestamp')
            if CUTOFF and ts and ts > CUTOFF:
                continue
            for c in content:
                if not isinstance(c, dict):
                    continue
                if c.get('type') == 'tool_use' and c.get('name') == 'Bash':
                    cmd = (c.get('input') or {}).get('command', '')
                    if 'spacesheep' in cmd or re.search(r'deploy[\w-]*\.sh', cmd):
                        row = {'file': src_label(f), 'ts': ts, 'id': c.get('id'), 'cmd': cmd,
                               'desc': (c.get('input') or {}).get('description', ''),
                               'agent': (meta or {}).get('agentType') if meta else None}
                        pending[c.get('id')] = row
                        rows.append(row)
                elif c.get('type') == 'tool_use' and c.get('name') == 'Bash':
                    pass
                if c.get('type') == 'tool_use' and c.get('name') == 'Bash' and c.get('id') not in pending:
                    anyb[c.get('id')] = (ts, (c.get('input') or {}).get('command', ''), (c.get('input') or {}).get('description', ''))
                if c.get('type') == 'tool_result' and c.get('tool_use_id') not in pending and c.get('tool_use_id') in anyb:
                    txt = result_text(c.get('content'))
                    if re.search(r'✓ (Created|Updated)|"is_update"|is_update:|visibility set to', txt):
                        t0, cmd, desc = anyb[c.get('tool_use_id')]
                        rows.append({'file': src_label(f), 'ts': t0, 'id': c.get('tool_use_id'), 'cmd': cmd, 'desc': desc,
                                     'agent': None, 'by_result': True, 'result_ts': ts,
                                     'is_error': bool(c.get('is_error')), 'result': txt[:60000], 'result_len': len(txt)})
                elif c.get('type') == 'tool_result' and c.get('tool_use_id') in pending:
                    row = pending.pop(c.get('tool_use_id'))
                    txt = result_text(c.get('content'))
                    row['result_ts'] = ts
                    row['is_error'] = bool(c.get('is_error'))
                    row['result'] = txt[:60000]
                    row['result_len'] = len(txt)

with open(os.path.join(OUT, 'spacesheep_calls.jsonl'), 'w') as o:
    for r in rows:
        o.write(json.dumps(r) + '\n')
print('files scanned', nfiles, 'spacesheep bash calls', len(rows))
print('with deploy', sum(1 for r in rows if 'deploy' in r['cmd']))
