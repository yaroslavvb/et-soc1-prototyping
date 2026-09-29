#!/usr/bin/env python3
"""Tokens by PDT day and hour, main agent vs subagents (by kind), for the session timeline.

agents.json gives token totals per agent but not per day; an agent's messages can cross midnight (the overnight
workflows do). This script re-streams the same transcripts with the same rules as extract_agents.py (it imports
its scan(), uuids_of() and file discovery): usage per message.id = per-field max over its lines, each message.id
owned by the shallowest transcript (main < depth-1 agent < depth-2 fork), fork lines copied from the parent
skipped. Each owned message is then counted in the PDT day and hour of its first line.

Only messages whose first line is at or before agents.json's `generated` time are counted, so the totals equal
agents.json's (the session is live and its transcripts keep growing). Writes ../tokens_by_time.json.
"""
import collections, json, os, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract_agents as X  # noqa: E402

TL = X.paths.TL
OUT = os.path.join(TL, 'tokens_by_time.json')
AG = json.load(open(os.path.join(TL, 'agents.json')))
CUTOFF = datetime.fromisoformat(AG['generated'].replace('Z', '+00:00'))
FIELDS = ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens')
SHORT = {'input_tokens': 'input', 'cache_creation_input_tokens': 'cache_creation',
         'cache_read_input_tokens': 'cache_read', 'output_tokens': 'output'}


def main():
    import glob
    rows = []
    for f in sorted(glob.glob(f'{X.SUB}/agent-*.jsonl')):
        rows.append({'path': f, 'wf': None})
    for d in sorted(glob.glob(f'{X.SUB}/workflows/wf_*')):
        for f in sorted(glob.glob(f'{d}/agent-*.jsonl')):
            rows.append({'path': f, 'wf': os.path.basename(d)})
    path_by_id = {}
    for r in rows:
        r['id'] = os.path.basename(r['path'])[len('agent-'):-len('.jsonl')]
        mp = r['path'][:-len('.jsonl')] + '.meta.json'
        r['meta'] = json.load(open(mp)) if os.path.exists(mp) else {}
        path_by_id[r['id']] = r['path']
    kind_of = {a['id']: a['kind'] for a in AG['agents']}

    print('scanning main ...', file=sys.stderr)
    main_scan = X.scan(X.MAIN)
    depth = lambda r: r['meta'].get('spawnDepth') or 1
    rows.sort(key=lambda r: (depth(r), r['id']))
    uuid_cache = {}
    for i, r in enumerate(rows):
        parent = r['meta'].get('parentAgentId')
        skip = None
        if parent and parent in path_by_id:
            if parent not in uuid_cache:
                uuid_cache[parent] = X.uuids_of(path_by_id[parent])
            skip = uuid_cache[parent]
        r['scan'] = X.scan(r['path'], skip)
        if (i + 1) % 100 == 0:
            print(f'  scanned {i+1}/{len(rows)}', file=sys.stderr)

    now = datetime.now(timezone.utc)
    owners = {}
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

    day = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.Counter()))
    hour = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.Counter()))
    tot = collections.defaultdict(collections.Counter)
    skipped_after = collections.Counter()

    def add(scanres, key, cls):
        for mid, rec in scanres['msgs'].items():
            if owners[mid][2] != key:
                continue
            ts = rec['ts']
            if ts is None:
                continue
            u = rec['usage']
            if ts > CUTOFF:
                skipped_after[cls] += sum(u.get(k, 0) for k in FIELDS)
                continue
            p = ts.astimezone(X.PT)
            dk, hk = p.strftime('%Y-%m-%d'), p.strftime('%Y-%m-%dT%H')
            for k in FIELDS:
                v = u.get(k, 0)
                day[dk][cls][SHORT[k]] += v
                hour[hk][cls][SHORT[k]] += v
                tot[cls][SHORT[k]] += v
            day[dk][cls]['messages'] += 1
            hour[hk][cls]['messages'] += 1
            tot[cls]['messages'] += 1

    add(main_scan, 'main', 'main')
    for r in rows:
        add(r['scan'], r['id'], kind_of.get(r['id'], 'workflow' if r['wf'] else 'agent'))

    def fin(d):
        out = {}
        for k in sorted(d):
            out[k] = {}
            for cls, c in d[k].items():
                c = dict(c)
                c['total'] = sum(c.get(SHORT[f], 0) for f in FIELDS)
                out[k][cls] = c
        return out
    totals = {cls: dict(c, total=sum(c.get(SHORT[f], 0) for f in FIELDS)) for cls, c in tot.items()}
    sub_total = sum(v['total'] for k, v in totals.items() if k != 'main')
    json.dump({
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'cutoff_utc': AG['generated'],
        'rule': ('extract_agents.py rules (usage per message.id = per-field max over its lines; each message.id owned '
                 'by the shallowest transcript); a message counts in the PDT day and hour of its first line; only '
                 'messages whose first line is at or before cutoff_utc (agents.json generated time)'),
        'classes': 'main = the main agent; workflow, agent, fork = subagent kinds as in agents.json',
        'totals': totals,
        'check': {'subagents_total_here': sub_total,
                  'subagents_total_agents_json': AG['totals']['tokens_subagents']['total'],
                  'main_total_here': totals.get('main', {}).get('total'),
                  'main_total_agents_json': AG['totals']['tokens_main']['total'],
                  'tokens_after_cutoff_skipped': dict(skipped_after)},
        'per_day_pdt': fin(day),
        'per_hour_pdt': fin(hour),
    }, open(OUT, 'w'), indent=1)
    print('wrote', OUT, file=sys.stderr)
    print(json.dumps({'sub_here': sub_total, 'sub_json': AG['totals']['tokens_subagents']['total'],
                      'main_here': totals.get('main', {}).get('total'),
                      'main_json': AG['totals']['tokens_main']['total'], 'after': dict(skipped_after)}))


if __name__ == '__main__':
    main()
