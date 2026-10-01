#!/usr/bin/env python3
"""Extract the neighbor sessions: other Claude Code sessions on the lab's machine whose work the page shows in a lane of
its own (on 30 September, the session that ran the link test that hung aifoundry1, then investigated it).

    TIMELINE_NEIGHBORS=97db24ee-042f-547a-86c0-e1444e260a06 tools/timeline/extract_neighbors.py

For each session id in $TIMELINE_NEIGHBORS (paths.py; none for no lane) it streams the session's transcript and its
subagents' (the same project folder as the main session) and writes $TIMELINE_DIR/neighbors.json:

  sessions[]  per neighbor: its busy intervals (its main agent's events under 3 min apart, joined across a tool call
              that took longer, as extract_agents.py counts them), its subagents' busy intervals (their union) and
              agent-hours, its tokens (usage per message id, counted once), the owner's messages to it (time, kind,
              length and a hand-written summary from NEIGHBOR_SUMMARIES, never the text), its key events (EVENTS,
              written from its transcript, the hosts' boot records and docs/findings/14-card-behaviour.md, plus each
              deploy of a public page and each commit it made, found in its transcripts), and how many other deploys
  hosts[]     the hosts down (HOSTS): aifoundry1 hung by the link retrain, then the power cycle of all three machines

and $TIMELINE_DIR/work/neighbor_deploys.json: every deploy the neighbors made (time and space, private ones too), which
build_artifacts.py reads so that their versions in a page's history are not counted as this session's deploys. That file
names private spaces, so it stays in the working folder and is never copied to the data folder.

Privacy (the page is public, AGENT.md section 10): the extract carries no message text, no workflow or agent names of the
neighbor (its workflows served the report for the lab lead and host fixes), no private page's name, slug or space, and
no word about who holds which privilege: the link test is "the owner's session ran the link test". sanitize_extracts.py
and build_timeline_data.py scan it with the others. $TIMELINE_CUTOFF ends the transcripts there.
"""
import collections, glob, json, os, re, subprocess, sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402
import extract_agents as X  # noqa: E402  (its scan(), busy_intervals() and merge_waits(); it needs the privacy table)

CUT = datetime.fromisoformat(paths.CUTOFF.replace('Z', '+00:00')) if paths.CUTOFF else None
PDT = timezone(timedelta(hours=-7))
T = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00'))
iso = lambda d: d.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
L = lambda s: datetime.fromisoformat(s).replace(tzinfo=PDT)   # a PDT wall time, as the tables below give it

# The owner's messages to a neighbor: (first 8 characters of the session id, the UTC second it was sent) -> (a summary of
# at most 12 words, third person, never quoting; category). A message missing here is left off the page and printed.
NEIGHBOR_SUMMARIES = {
    ('97db24ee', '2026-09-30T21:04:45'): ("Checks that the new session responds.", 'status'),
    ('97db24ee', '2026-09-30T21:04:49'): ("Picks the session's model.", 'status'),
    ('97db24ee', '2026-09-30T21:11:16'): ("Asks to tidy the lab lead's report and fix the open problems.", 'request'),
    ('97db24ee', '2026-09-30T21:31:46'): ("Asks for commands the owner can run for the host fixes.", 'request'),
    ('97db24ee', '2026-09-30T21:41:21'): ("Reports the fixes ran, aifoundry1's still running; asks to verify them.", 'request'),
    ('97db24ee', '2026-09-30T21:47:16'): ("Reports aifoundry1 seems dead, with the last commands it ran.", 'status'),
    ('97db24ee', '2026-09-30T22:18:15'): None,   # four messages delivered in one second after the restart: by length below
    ('97db24ee', '2026-09-30T22:27:58'): ("Asks to retitle the lab lead's report and hide solved issues.", 'request'),
    ('97db24ee', '2026-09-30T22:29:20'): ("Asks for sortable columns in the report's problem table.", 'request'),
    ('97db24ee', '2026-09-30T22:32:54'): ("Asks to fix what it can and detail steps for the Nekko team.", 'request'),
    ('97db24ee', '2026-09-30T22:55:40'): ("Asks for public lab pages, and one way on the new-user page.", 'request'),
}
# messages sent in the same second, told apart by their length in characters
NEIGHBOR_SUMMARIES_BY_LEN = {
    ('97db24ee', '2026-09-30T22:18:15', 1418): ("Sends the report that aifoundry1 is down again, after the restart.", 'status'),
    ('97db24ee', '2026-09-30T22:18:15', 169): ("Says the lab lead power-cycled; asks to troubleshoot and record the lesson.", 'request'),
    ('97db24ee', '2026-09-30T22:18:15', 47): ("Corrects which machine was power-cycled.", 'correction'),
    ('97db24ee', '2026-09-30T22:18:15', 183): ("If it stays down, asks for a report of likely causes.", 'request'),
}

# Key events of a neighbor, from its transcript and 14-card-behaviour.md (PDT wall times; end None for an instant).
# Kinds: test, hang, power (drawn red), back, probe, page, commit, fix.
EVENTS = {
    '97db24ee': [
        ('2026-09-30T14:41:21', None, 'test', 'The link test on aifoundry1 card 0',
         'The owner’s session ran the link test from the lab report (U25): two readings of card 0’s corrected link errors '
         'at 16 GT/s, a minute apart, then a retrain of the link at 8 GT/s, with the card idle and locked. The plan said a '
         'failed retrain would drop only card 0.'),
        ('2026-09-30T14:41:21', '2026-09-30T15:06:35', 'hang', 'aifoundry1 hung',
         'At the retrain the whole host stopped: no more output, no network. The neighbor’s read-only check found it gone '
         'at 14:42, watched for it from 14:45 and confirmed it dead at 14:48; the owner reported it at 14:47.'),
        ('2026-09-30T15:06:35', '2026-09-30T15:07:35', 'power', 'The power cycle',
         'The lab lead switched all three machines off and on at about 15:07 (boots at 15:07:10–15:07:35). The reboot of '
         'aifoundry2 stopped both sessions there until 15:18 and 15:22 and cleared its /tmp: about 19 GB of working files, '
         'this timeline’s working folder among them.'),
        ('2026-09-30T15:18:15', '2026-09-30T15:21:01', 'probe', 'The investigation',
         'Back at 15:18, the neighbor reads the three hosts’ boot records, card 0’s link counters (16 GT/s x8 again, no '
         'corrected errors where there had been about one a second for twelve days) and the crash store (empty: a hard hang, '
         'not a panic), and what the power cycle cleared.'),
        ('2026-09-30T15:57:25', '2026-09-30T16:03:46', 'fix', 'The dashboard kept public',
         'At the owner’s word that the AI Foundry pages are public, the neighbor changed the lab dashboard’s updater, which '
         'had set the page private again on each run: it now keeps it public. The 16:02 run confirmed it.'),
    ],
}
# The hosts down: (host, its cards on the page, start, end, kind, title, text). The boot times are each host's own
# record (uptime -s, last -x), read on 30 Sep at 15:55; the power went off after 15:06:33, the last line either session
# on aifoundry2 wrote before its boot.
HOSTS = [
    ('aifoundry1', ['aifoundry1-c0', 'aifoundry1-c1'], '2026-09-30T14:41:21', '2026-09-30T15:06:35', 'hang', 'aifoundry1 hung',
     'The retrain of card 0’s link at 14:41:21 stopped the whole host, both cards with it, until the power cycle.'),
    ('aifoundry1', ['aifoundry1-c0', 'aifoundry1-c1'], '2026-09-30T15:06:35', '2026-09-30T15:07:35', 'power', 'aifoundry1 power-cycled',
     'The lab lead switched the machine off and on; it booted at 15:07:35, and card 0’s link trained at 16 GT/s again.'),
    ('aifoundry2', ['aifoundry2'], '2026-09-30T15:06:35', '2026-09-30T15:07:11', 'power', 'aifoundry2 power-cycled',
     'Switched off and on with the others; it booted at 15:07:11. The sessions on it stopped until 15:08–15:22, and its '
     '/tmp was cleared.'),
    ('aifoundry3', ['aifoundry3'], '2026-09-30T15:06:35', '2026-09-30T15:07:10', 'power', 'aifoundry3 power-cycled',
     'Switched off and on with the others; it booted at 15:07:10.'),
]

MIRROR = os.path.join(paths.REPO, 'docs', 'reports', 'MIRROR.md')
UUID = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'


def mirror_pages():
    """uuid -> (slug, title, public?) of every page MIRROR.md lists"""
    out, txt = {}, open(MIRROR, encoding='utf-8').read()
    a, b = txt.find('<!-- mirror:begin -->'), txt.find('<!-- mirror:end -->')
    for line in txt[a:b].splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 3:
            continue
        m, u = re.match(r'\[(.*?)\]\(https://spacesheep\.dev/@yaroslavvb/([\w.-]+)\)', cells[0]), re.search(UUID, cells[1])
        if m and u:
            out[u.group(0)] = (m.group(2), m.group(1), bool(re.match(r'public\b', cells[2])))
    return out


def text_of(c):
    if isinstance(c, str):
        return c
    return '\n'.join(x.get('text', '') for x in c or [] if isinstance(x, dict) and x.get('type') == 'text')


def before_cut(ts):
    return ts and (CUT is None or T(ts) <= CUT)


def owner_messages(path, sid8):
    """the owner's inputs to a session: prompts, messages sent while it worked, slash commands (no text kept)"""
    enq, out = {}, []
    for line in open(path, encoding='utf-8', errors='replace'):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        ts, t = e.get('timestamp'), e.get('type')
        if not before_cut(ts):
            continue
        if t == 'queue-operation' and e.get('operation') == 'enqueue' and isinstance(e.get('content'), str):
            enq[e['content'][:200]] = ts
        elif t == 'user' and (e.get('origin') or {}).get('kind') == 'human':
            s = text_of((e.get('message') or {}).get('content'))
            sent = enq.get(s[:200]) if e.get('promptSource') == 'queued' else None
            out.append((sent or ts, 'prompt', len(s)))
        elif t == 'user' and text_of((e.get('message') or {}).get('content')).startswith('<command-name>'):
            out.append((ts, 'slash-command', 0))
        elif t == 'system' and e.get('subtype') == 'local_command' and (e.get('content') or '').startswith('<command-name>'):
            out.append((ts, 'slash-command', 0))
        elif t == 'attachment' and (e.get('attachment') or {}).get('type') == 'queued_command':
            a = e['attachment']
            if (a.get('origin') or {}).get('kind') == 'human':
                out.append((a.get('timestamp') or ts, 'midturn', len(text_of(a.get('prompt')))))
    msgs, unsummarised = [], []
    for ts, kind, n in sorted(out):
        key = T(ts).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
        sm = NEIGHBOR_SUMMARIES.get((sid8, key)) or NEIGHBOR_SUMMARIES_BY_LEN.get((sid8, key, n))
        if not sm:
            unsummarised.append(f'{key} ({kind}, {n} characters)')
            continue
        msgs.append({'ts': iso(T(ts)), 'kind': kind, 'chars': n, 'summary': sm[0], 'category': sm[1]})
    return msgs, unsummarised


def deploys_and_commits(files, mirror):
    """every spacesheep deploy (its time, and the space from the CLI's output or the command) and every commit a session
    made (the '[branch sha]' line git prints), from its transcripts"""
    deps, shas = [], set()
    slug_uuid = {v[0]: u for u, v in mirror.items()}
    for f in files:
        pend = {}
        for line in open(f, encoding='utf-8', errors='replace'):
            if 'tool_use' not in line and 'tool_result' not in line:
                continue
            try:
                e = json.loads(line)
            except ValueError:
                continue
            ts = e.get('timestamp')
            if not before_cut(ts):
                continue
            for c in (e.get('message') or {}).get('content') or []:
                if not isinstance(c, dict):
                    continue
                if c.get('type') == 'tool_use' and c.get('name') == 'Bash':
                    cmd = (c.get('input') or {}).get('command') or ''
                    if re.search(r'spacesheep(?:\.js)?\S*\s+deploy\b', cmd) or 'git commit' in cmd:
                        pend[c.get('id')] = (ts, cmd)
                elif c.get('type') == 'tool_result' and c.get('tool_use_id') in pend:
                    ts0, cmd = pend.pop(c['tool_use_id'])
                    res = text_of(c.get('content')) if not isinstance(c.get('content'), str) else c['content']
                    if 'git commit' in cmd:   # '[main abc1234] ...', or a log line after a quiet commit; kept if made then
                        for sha in set(re.findall(r'^\[[\w./-]+ ([0-9a-f]{7,})\]', res, re.M) + re.findall(r'^([0-9a-f]{7,12}) ', res, re.M)):
                            shas.add((sha, ts0, ts))
                    if not re.search(r'spacesheep(?:\.js)?\S*\s+deploy\b', cmd):
                        continue
                    for kind, slug in re.findall(r'✓ (Created|Updated) https://spacesheep\.dev/@yaroslavvb/([\w.-]+)', res):
                        deps.append({'ts': ts0, 'uuid': slug_uuid.get(slug), 'slug': slug, 'created': kind == 'Created'})
                    if not re.search(r'✓ (Created|Updated)', res):
                        m = re.search(r'--space[ =]"?(' + UUID + ')', cmd)
                        if m:
                            deps.append({'ts': ts0, 'uuid': m.group(1), 'slug': (mirror.get(m.group(1)) or (None,))[0],
                                         'created': False, 'unconfirmed': True})
    return deps, shas


def commit_rows(shas):
    """the commits a session made: a sha its commit command printed, whose commit time falls within that command"""
    rows = {}
    for sha, t0, t1 in sorted(shas):
        r = subprocess.run(['git', '-C', paths.REPO, 'log', '-1', '--format=%H%x1f%aI%x1f%cI%x1f%s', sha], capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            continue
        h, d, cd, s = r.stdout.strip().split('\x1f', 3)
        if T(t0) - timedelta(seconds=60) <= datetime.fromisoformat(cd) <= T(t1) + timedelta(seconds=60):
            rows[h[:7]] = {'sha': h[:7], 'ts': iso(datetime.fromisoformat(d)), 'subject': s}
    return sorted(rows.values(), key=lambda c: c['ts'])


def scrub(s):
    """the privacy table's name redactions, then its sanitize rules (as build_artifacts.py and sanitize_extracts.py)"""
    P = paths.private()
    for a, b in P.get('artifact_name_redactions', []) + P.get('sanitize', []):
        s = re.sub(a, b, s)
    return s


def shown(d, mirror):
    """a deploy the page may name: of a page MIRROR.md lists as public, other than the report for the lab lead (which the
    page never names) and the spaces it never lists"""
    if d['uuid'] not in mirror or not mirror[d['uuid']][2]:
        return False
    slug, pre = mirror[d['uuid']][0], paths.private().get('lab_report_slug_prefix')
    return not (pre and slug.startswith(pre)) and slug not in ('aifoundry-lab-accounts',)


def one(sid, mirror):
    sid8 = sid[:8]
    main = os.path.join(paths.PROJ, sid + '.jsonl')
    if not os.path.exists(main):
        print(f'{sid8}: no transcript at {main}; left out', file=sys.stderr)
        return None, []
    ms = X.scan(main)
    times = [t for t in ms['times'] if CUT is None or t <= CUT]
    waits = [w for w in ms['long_tool_waits'] if before_cut(w[1])]
    busy = X.merge_waits(X.busy_intervals(times), waits)
    # its subagents: every agent transcript once (a workflow's copy before a top-level one of the same agent)
    files = {}
    for f in sorted(glob.glob(os.path.join(paths.PROJ, sid, 'subagents', '**', 'agent-*.jsonl'), recursive=True),
                    key=lambda f: ('/workflows/' not in f, f)):
        files.setdefault(os.path.basename(f), f)
    sub, agent_s, msgs_usage = [], 0.0, {}
    for mid, rec in ms['msgs'].items():
        if rec['ts'] and before_cut(iso(rec['ts'])):
            msgs_usage[mid] = dict(rec['usage'])
    workflows = set()
    for f in files.values():
        sc = X.scan(f)
        ts_ = [t for t in sc['times'] if CUT is None or t <= CUT]
        if not ts_:
            continue
        if '/workflows/' in f:
            workflows.add(f.split('/workflows/')[1].split('/')[0])
        b = X.busy_intervals(ts_)
        sub += b
        agent_s += sum((y - x).total_seconds() for x, y in b)
        for mid, rec in sc['msgs'].items():
            if rec['ts'] and before_cut(iso(rec['ts'])):
                u = msgs_usage.setdefault(mid, {})
                for k, v in rec['usage'].items():
                    u[k] = max(u.get(k, 0), v)
    sub.sort()
    su = []
    for a, b in sub:
        if su and a <= su[-1][1]:
            su[-1][1] = max(su[-1][1], b)
        else:
            su.append([a, b])
    tok = collections.Counter()
    for u in msgs_usage.values():
        for k in ('input_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens'):
            tok[k] += int(u.get(k) or 0)
    owner, unsum = owner_messages(main, sid8)
    deps, shas = deploys_and_commits([main] + list(files.values()), mirror)
    commits = [c for c in commit_rows(shas) if before_cut(c['ts'])]
    events = [{'t': iso(L(a)), 'e': iso(L(b)) if b else None, 'kind': k, 'title': ti, 'text': tx}
              for a, b, k, ti, tx in EVENTS.get(sid8, []) if before_cut(iso(L(a)))]
    public = [d for d in deps if shown(d, mirror)]
    for d in public:   # a deploy of a public page: an event of its own
        slug, title = mirror[d['uuid']][:2]
        events.append({'t': iso(T(d['ts'])), 'e': None, 'kind': 'page', 'title': ('Published: ' if d['created'] else 'Updated: ') + title,
                       'text': f'A deploy of the public page {title} (spacesheep.dev/@yaroslavvb/{slug}).'})
    for c in commits:
        events.append({'t': c['ts'], 'e': None, 'kind': 'commit', 'title': 'A commit: ' + c['sha'], 'text': scrub(c['subject'])})
    events.sort(key=lambda e: e['t'])
    row = {
        'id': sid8, 'name': 'the neighbor session',
        'title': 'another Claude Code session on aifoundry2, started by the owner on 30 September',
        'first': iso(times[0]) if times else None, 'last': iso(times[-1]) if times else None,
        'busy': [[iso(a), iso(b)] for a, b in busy], 'busy_h': round(sum((b - a).total_seconds() for a, b in busy) / 3600, 2),
        'sub': [[iso(a), iso(b)] for a, b in su], 'agents': len(files), 'workflow_runs': len(workflows),
        'agent_h': round(agent_s / 3600, 2),
        'tokens': {'input': tok['input_tokens'], 'cache_creation': tok['cache_creation_input_tokens'],
                   'cache_read': tok['cache_read_input_tokens'], 'output': tok['output_tokens'], 'total': sum(tok.values())},
        'messages': owner, 'unsummarised': unsum, 'events': events,
        'deploys': {'public': len(public), 'other': len(deps) - len(public)},
        'commits': [c['sha'] for c in commits],
    }
    return row, deps


def main():
    mirror = mirror_pages()
    sessions, all_deps = [], []
    for sid in paths.NEIGHBORS:
        row, deps = one(sid, mirror)
        if row:
            sessions.append(row)
            all_deps += [dict(d, session=sid[:8]) for d in deps]
    hosts = [{'host': h, 'cards': cards, 's': iso(L(a)), 'e': iso(L(b)), 'kind': k, 'title': ti, 'text': tx}
             for h, cards, a, b, k, ti, tx in HOSTS if before_cut(iso(L(a)))] if sessions else []
    out = {'generated': iso(datetime.now(timezone.utc)), 'cutoff': paths.CUTOFF,
           'rule': ' '.join(__doc__.split('\n\n')[1].split()),
           'sessions': sessions, 'hosts': hosts}
    tl = paths.ensure_tl()
    json.dump(out, open(os.path.join(tl, 'neighbors.json'), 'w'), indent=1, ensure_ascii=False)
    os.makedirs(os.path.join(tl, 'work'), exist_ok=True)
    json.dump(all_deps, open(os.path.join(tl, 'work', 'neighbor_deploys.json'), 'w'), indent=1)
    for s in sessions:
        print(s['id'], s['first'], s['last'], 'busy', s['busy_h'], 'h in', len(s['busy']), 'intervals; subagents', s['agents'],
              'in', s['workflow_runs'], 'workflows,', s['agent_h'], 'agent-h; tokens', s['tokens']['total'])
        print('  messages', len(s['messages']), 'unsummarised', s['unsummarised'])
        print('  deploys', s['deploys'], 'commits', s['commits'])
        for e in s['events']:
            print('  ', e['t'], e['kind'], e['title'])
    print('hosts', [(h['host'], h['kind'], h['s'], h['e']) for h in hosts])
    print('neighbor deploys (work/neighbor_deploys.json):', len(all_deps))


if __name__ == '__main__':
    main()
