#!/usr/bin/env python3
"""Build timeline.json for the transistor-heat timeline page.

Usage:  build_transistor_timeline.py <data dir>

The data dir holds the curated inputs - config.json, questions.json, sessions.json, documents.json,
experiments.json, highlights.json - and gets timeline.json written into it. Unlike the session
timeline's builder, nothing here reads a transcript: the inputs are assembled from the lab
repository's own ledgers (docs/findings/02-requests.md, 03-experiments.md, 04-artifacts.md,
docs/reports/MIRROR.md and the committed block.json / session.json files) and from the project's
hub, and every one of them is committed beside the page.

The output obeys the same contract as tools/timeline/build_timeline_data.py, so the page script is
the session timeline's with the changes listed in its header. Three blocks are reinterpreted:
`human` is the questions lane, `cards` is the experiments lane, `artifacts` is the documents lane.

It refuses to write if the serialised output still carries anything a public page must not: a link
on a private network, a session link, an address, a home path, a word about machine access, a
spacesheep page that is not public, a name that is not a published author of cited work, or any
mention of the private design archive beyond the fact that a study happened.

A second gate reads the curated asks instead of the output, for the two faults the first cannot
see because the same string is legitimate elsewhere on the page: a host named inside his quoted
words in a spelling he dictated, and a role substitution glued into a compound. See ASK_ONLY.
"""
import json, os, re, sys, math, datetime, collections

TZ = datetime.timedelta(hours=-7)


def P(s):
    d = datetime.datetime.fromisoformat(s)
    if d.tzinfo is None:
        raise SystemExit('every time needs an offset: ' + s)
    return d


# ----------------------------------------------------------------- the gate
FORBIDDEN = [
    (r'https?://(intel|m5|mini|localhost)[:/]', 'a link on a private network'),
    (r'\bhttps?://[\w.-]*aifoundry[123]\b[:/]', 'a link on the lab network'),
    (r'\b(?<!\.)\b(100|10|192\.168|172\.(1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}(\.\d{1,3})?\b', 'a private address'),
    (r'claude\.ai/', 'a session link'),
    (r'(?<![\w/@.-])/(Users|home)/', 'a home path'),
    (r'(?<![\w/])[\w.+-]+@[\w-]+\.(com|org|net|dev|ai|io)\b', 'an e-mail address'),
    (r'\bmordast\b|\bnekko\b|\bainekko\b', 'the private archive or the company'),
    (r'\b(tsmc|n7\b|n5\b|pdk\b)', 'a foundry identifier'),
    (r'\bL0[0-9]_|\bL1[0-9]_', 'a foundry cell-library prefix'),
    (r'\b(ssh |scp |sudo |root@|tailscale|tailnet|api[ -]?key|password|passphrase)', 'machine access'),
    (r'\b(recording|transcript of (the|our) meeting|voice note|tape of)\b', 'a recording'),
]
# the only people a page of this kind names: published authors whose work the public reports cite
PEOPLE_OK = {'horace he', 'horace', 'bill dally', 'dally', 'horowitz', 'mark horowitz', 'jeff dean',
             'yaroslav bulatov', 'yaroslavvb', 'horace hay', 'build daily'}   # published authors of cited work
PEOPLE_BAD = re.compile(r'\b(roman|shaposhnik|tanya|dadasheva|padgett|kanter|tondwalkar|glick|saquib|misha|'
                        r'ivan|nahmias|mitchell)\b', re.I)

# ------------------------------------------------------- the curation gate
# A second gate, over the curated inputs rather than the serialised output. It exists because the
# first two builds shipped three faults the gate above cannot see, each of them a legitimate string
# somewhere else on the page:
#   - a card host named inside one of his quoted asks in a spelling he dictated ("AI Foundry2",
#     "aistudio2"), while the asks on either side had it replaced by "[a card host]". FORBIDDEN
#     cannot simply ban the name: the machine keys, session titles, commit subjects and public page
#     slugs carry "aifoundry2" legitimately more than 950 times;
#   - the private archive host dictated as "MoreDesk", which FORBIDDEN's \bmordast\b cannot match,
#     on a page whose §5 promises the archive appears only as dates and spans.
# Both are only ever wrong inside a quoted ask, so that is where this looks. A phonetic list can
# never be complete; it catches the spellings that have actually appeared, and the asks still have
# to be read.
ASK_ONLY = [
    (r'\bai[ -]?(?:foundry|studio)[ -]?[0-9]\b', 'a card host named in an ask - use "[a card host]"'),
    (r'\bmore[ -]?desk\b|\bmor[ea][ -]?das[kt]\b|\bmordas\w*|\bnekko\b|\bainekko\b',
     'the private archive host in an ask - use "[a host]"'),
]
# A role stands in for a name ("a lab user", "the lab's admin"). Glued into a hyphenated compound or
# a possessive, that substitution silently rewrites a technical term instead: E60's registered
# "max-flip order" shipped as "a lab user-flip order", because Max is also a lab user's name.
GLUED_ROLE = re.compile(r"\w-(?:a lab user|the lab's admin)|(?:a lab user|the lab's admin)-\w", re.I)


def scan_curation(QS, blob):
    hits = []
    for q in QS['questions']:
        for fld in ('summary', 'text'):
            v = q.get(fld) or ''
            for pat, why in ASK_ONLY:
                m = re.search(pat, v, re.I)
                if m:
                    hits.append((why, '%s.%s: %s' % (q['id'], fld,
                                                     v[max(0, m.start() - 40):m.end() + 40])))
    for m in GLUED_ROLE.finditer(blob):
        hits.append(('a role glued into a compound, rewriting a word',
                     blob[max(0, m.start() - 60):m.end() + 60]))
    return hits


def scan(text, public_slugs):
    hits = []
    for pat, why in FORBIDDEN:
        for m in re.finditer(pat, text, re.I):
            hits.append((why, text[max(0, m.start() - 40):m.end() + 40].replace('\n', ' ')))
            break
    for m in PEOPLE_BAD.finditer(text):
        hits.append(('a person who is not a published author of cited work',
                     text[max(0, m.start() - 50):m.end() + 50].replace('\n', ' ')))
        break
    for m in re.finditer(r'spacesheep\.dev/@[\w-]+/([\w.-]+)', text):
        if m.group(1) not in public_slugs:
            hits.append(('a spacesheep page that is not public: ' + m.group(1), m.group(0)))
    for m in re.finditer(r'\b([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b', text):
        hits.append(('a space uuid', m.group(1)))
        break
    return hits


def main(ddir):
    L = lambda n: json.load(open(os.path.join(ddir, n + '.json')))
    CFG, QS, SS, DOC, EX, HLS = (L('config'), L('questions'), L('sessions'), L('documents'),
                                 L('experiments'), L('highlights'))
    PUBLIC = set(CFG['public_slugs'])
    T0 = P(CFG['t0'])
    DAY = 86400
    rel = lambda s: round((P(s) - T0).total_seconds(), 1)
    SNAP = rel(CFG['snapshot'])
    START = min([rel(q['t']) for q in QS['questions']] + [rel(r['s']) for r in EX['runs']])
    FULL = [0.0, float(math.ceil(SNAP / 3600) * 3600)]
    NDAYS = int(math.ceil(FULL[1] / DAY))
    WD = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    days, day_iso, day_week = [], [], []
    for d in range(NDAYS):
        dt = T0 + datetime.timedelta(days=d)
        days.append('%s %d' % (WD[dt.weekday()], dt.day))
        day_iso.append(dt.strftime('%Y-%m-%d'))
        day_week.append(dt.isocalendar()[1])
    weeks = []
    for w in sorted(set(day_week), key=lambda w: day_week.index(w)):
        ds = [d for d in range(NDAYS) if day_week[d] == w]
        weeks.append({'label': 'W%d' % w, 'w': w, 's': ds[0] * DAY, 'e': min(FULL[1], (ds[-1] + 1) * DAY),
                      'title': 'week %d, %s to %s' % (w, day_iso[ds[0]], day_iso[ds[-1]])})

    def union(iv, bridge=0.0):
        u = []
        for a, b in sorted(iv):
            if u and a - u[-1][1] <= bridge:
                u[-1][1] = max(u[-1][1], b)
            else:
                u.append([a, b])
        return u

    # ---------------------------------------------------------- human = the questions
    cats, kinds = QS['cats'], QS['kinds']
    msgs = []
    for q in QS['questions']:
        t = rel(q['t'])
        a = float(q.get('active_s') or 0)
        msgs.append([t, a, a, cats.index(q['category']), kinds.index(q['kind']), q['summary'],
                     q.get('request'), q.get('chars') or 0, 0.0, a, 0, q.get('text'),
                     q.get('removed') or [], 0, q.get('to')])
    msgs.sort(key=lambda m: m[0])
    GAP = 3600.0
    sits = []
    for m in msgs:
        s = m[0] - m[1]
        if sits and s - sits[-1][1] < GAP:
            sits[-1][1] = max(sits[-1][1], m[0])
            sits[-1][2] += 1
            sits[-1][3] += m[1]
            sits[-1][4] += m[1]
        else:
            sits.append([s, m[0], 1, m[1], m[1]])
    byc = collections.Counter(cats[m[3]] for m in msgs)
    byk = collections.Counter(kinds[m[4]] for m in msgs)
    act_h = sum(m[1] for m in msgs) / 3600
    HUMAN = {
        'cats': cats, 'kinds': kinds,
        'cols': ['t', 'active_s', 'active_paste_s', 'cat', 'kind', 'summary', 'request', 'chars',
                 'read_s', 'type_s', 'paste', 'text', 'removed', 'images', 'to'],
        'msgs': msgs, 'sessions': sits,
        'totals': {'n': len(msgs), 'chars': sum(m[7] for m in msgs), 'active_h': act_h,
                   'active_paste_h': act_h, 'read_h': 0.0, 'type_h': act_h,
                   'engagement_h': sum(s[1] - s[0] for s in sits) / 3600, 'sessions': len(sits),
                   'by_category': {c: byc.get(c, 0) for c in cats},
                   'by_kind': {k: byk.get(k, 0) for k in kinds}},
        'rules': QS['rule'],
    }

    # ---------------------------------------------------------- sessions
    ALL = SS['all']
    HEAD = SS['sessions']
    machines = CFG['machines']
    mkey = [m['key'] for m in machines]
    for s in ALL:
        s['_busy'] = [[rel(a), rel(b)] for a, b in s['busy']]
        s['_s'], s['_e'] = rel(s['first']), rel(s['last'])
    spine = union([iv for s in ALL for iv in s['_busy']], 0.0)
    MAIN = {
        'triggers': ['work on the thread'],
        'cols': ['s', 'e', 'trigger', 'tokens', 'tool_calls', 'messages', 'active_s', 'tool_wait_s',
                 'other_wait_s', 'tool_wait_lab_s'],
        'busy': [[a, b, 0, 0, 0, 0, round(b - a, 1), 0, 0, 0] for a, b in spine],
        'strict': [[a, b] for a, b in spine], 'watch': [], 'compactions': [], 'limits': [],
        'totals': {'busy_h': sum(b - a for a, b in spine) / 3600,
                   'strict_h': sum(b - a for a, b in spine) / 3600,
                   'tool_wait_h': 0.0, 'tool_wait_lab_h': 0.0, 'watch_h': 0.0,
                   'messages': 0, 'tool_calls': 0, 'intervals': len(spine), 'compactions': 0},
        'rules': {'busy': SS['rule'], 'strict': SS['rule'], 'tool_class': ''},
    }

    # conc: how many sessions were busy in each minute, split by harness
    n = int(math.ceil(FULL[1] / 60))
    cc = {'cc': [0] * n, 'other': [0] * n, 'fail': [0] * n}
    for s in ALL:
        k = 'fail' if s.get('status') == 'abandoned' else ('cc' if s['harness'] == 'claude-code' else 'other')
        for a, b in s['_busy']:
            for j in range(max(0, int(a // 60)), min(n, int(math.ceil(b / 60)))):
                cc[k][j] += 1

    def rle(a):
        o = []
        for v in a:
            if o and o[-1][0] == v:
                o[-1][1] += 1
            else:
                o.append([v, 1])
        return o

    tot = [cc['cc'][i] + cc['other'][i] + cc['fail'][i] for i in range(n)]
    CONC = {'start': 0.0, 'step': 60, 'n': n,
            'wf': rle(cc['cc']), 'tool': rle(cc['other']),
            'okwf': rle(cc['cc']), 'oktool': rle(cc['other']), 'fail': rle(cc['fail']),
            'note': 'A session counts in a minute when any of its busy time falls in it.'}
    PEAK_ALL = max(tot) if tot else 0
    PEAK_OK = max((cc['cc'][i] + cc['other'][i] for i in range(n)), default=0)
    PEAK_AT = (tot.index(PEAK_ALL) * 60.0) if tot else 0.0

    # agents: every session, one row, grouped by machine and packed into lanes
    HARN = ['claude-code', 'codex', 'antigravity']
    STATUS = ['done', 'running', 'abandoned']
    groups, rows = [], []
    for gi, m in enumerate(machines):
        mine = sorted([s for s in ALL if s['machine'] == m['key']], key=lambda s: (s['_s'], s['id']))
        if not mine:
            continue
        ends = []
        for s in mine:
            lane = next((i for i, e in enumerate(ends) if e + 30 <= s['_s']), len(ends))
            if lane == len(ends):
                ends.append(0.0)
            ends[lane] = s['_e']
            busy = [v for iv in s['_busy'] for v in iv]
            rows.append([s['_s'], s['_e'], len(groups), lane, -1,
                         (s['title'] or s['id'])[:90], s.get('relevance') or '',
                         STATUS.index(s.get('status', 'done')), HARN.index(s['harness']),
                         round(sum(b - a for a, b in s['_busy']) / 60, 1), 0, 0, 0, busy])
        groups.append({'key': m['key'], 'name': m['label'], 'wf': -1, 'lanes': len(ends),
                       's': min(s['_s'] for s in mine), 'e': max(s['_e'] for s in mine), 'n': len(mine)})
    rows.sort(key=lambda r: (r[2], r[0]))
    busy_h = sum(r[9] for r in rows) / 60
    AGENTS = {
        'status': STATUS, 'kinds': HARN,
        'cols': ['s', 'e', 'group', 'lane', 'wf', 'label', 'phase', 'status', 'kind', 'busy_min',
                 'tokens', 'out_tokens', 'tool_calls', 'busy'],
        'rows': rows, 'groups': groups, 'workflows': [],
        'peak': {'subagents': {'value': PEAK_ALL, 't': PEAK_AT},
                 'subagents_excluding_errored': {'value': PEAK_OK, 't': PEAK_AT},
                 'subagents_plus_main': {'value': PEAK_ALL, 't': PEAK_AT},
                 'alive_subagents': {'value': PEAK_ALL, 't': PEAK_AT},
                 'subagents_incl_tool_waits': {'value': PEAK_ALL, 't': PEAK_AT},
                 'subagents_sustained_10min': {'value': PEAK_OK, 't': PEAK_AT}},
        'peak_minute': {'n': PEAK_ALL, 'started_in_it': 0, 'failed': 0},
        'totals': {'agents': len(rows), 'by_kind': {h: sum(1 for s in ALL if s['harness'] == h) for h in HARN},
                   'workflow_runs': 0, 'workflow_launch_calls': 0, 'agent_tool_calls_in_main': 0,
                   'busy_agent_h': busy_h, 'tool_calls': 0,
                   'status': {s: sum(1 for x in ALL if x.get('status', 'done') == s) for s in STATUS},
                   'running_workflows': []},
    }

    # ---------------------------------------------------------- cards = the experiments
    IDS = CFG['cards']
    fams = EX['families']
    fkey = [f['key'] for f in fams]
    civ = []
    for r in EX['runs']:
        if r['family'] not in fkey:
            raise SystemExit('run in an unknown family: ' + r['family'])
        if r['card'] not in IDS:
            raise SystemExit('run on an unknown card: ' + r['card'])
        civ.append([IDS.index(r['card']), rel(r['s']), rel(r['e']), fkey.index(r['family']),
                    r.get('E'), r['label'], r.get('name') or r['label'], r.get('status') or 'data',
                    r.get('die')])
    civ.sort(key=lambda q: (q[1], q[0]))
    per_card, held_total, busy_total = [], 0.0, 0.0
    for k, cid in enumerate(IDS):
        mine = [q for q in civ if q[0] == k]
        held = union([[q[1], q[2]] for q in mine], 120)
        busy = union([[q[1], q[2]] for q in mine], 0)
        fh = []
        for fi in range(len(fams)):
            fh.append(sum(b - a for a, b in union([[q[1], q[2]] for q in mine if q[3] == fi], 0)) / 3600)
        hh = sum(b - a for a, b in held) / 3600
        bh = sum(b - a for a, b in busy) / 3600
        held_total += hh
        busy_total += bh
        per_card.append({'id': cid, 'held_h': hh, 'busy_h': bh, 'family_h': fh,
                         'held_h_without_dev': hh, 'intervals': len(mine), 'held_h_cards_json': hh})
    inuse = [0] * n
    for k in range(len(IDS)):
        for a, b in union([[q[1], q[2]] for q in civ if q[0] == k], 120):
            for j in range(max(0, int(a // 60)), min(n, int(math.ceil(b / 60)))):
                inuse[j] += 1
    minutes_by_count = collections.Counter(inuse)
    CARDS = {
        'ids': IDS, 'families': fams, 'dev': -1,
        'cols': ['card', 's', 'e', 'family', 'E', 'label', 'name', 'status', 'die_c_start'],
        'intervals': civ, 'per_card': per_card,
        'inuse': {'start': 0.0, 'step': 60, 'rle': rle(inuse),
                  'minutes_with': [[c, minutes_by_count[c]] for c in sorted(minutes_by_count) if c]},
        'totals': {'held_h': held_total, 'busy_h': busy_total, 'held_h_without_dev': held_total,
                   'dev_runs': 0, 'dev_calls': 0, 'dev_busy_h': 0.0, 'held_h_incl_18sep': held_total,
                   'intervals': len(civ),
                   'minutes_by_count': {str(c): minutes_by_count[c] for c in sorted(minutes_by_count) if c}},
        'rules': {'held': 'A card is held from the start of a measurement to its end, with gaps under two minutes '
                          'counted as held, because a queue keeps the card between passes.',
                  'busy': 'Busy is the exact union of the intervals.',
                  'sources': ['the committed block.json and session.json of each experiment',
                              'the times stated in docs/findings/03-experiments.md'],
                  'dev': '', 'note': EX['source']},
        'first_use': civ[0][1] if civ else 0.0,
        'undated': EX.get('undated', []),
    }

    # ---------------------------------------------------------- artifacts = the documents
    docs = sorted(DOC['documents'], key=lambda d: d['versions'][0]['t'])
    pages, deploys = [], []
    for i, d in enumerate(docs):
        vs = sorted(d['versions'], key=lambda v: v['t'])
        if d.get('public') and not d.get('url'):
            raise SystemExit('a public document with no url: ' + d['key'])
        if not d.get('public') and d.get('url'):
            raise SystemExit('a document that is not public must carry no url: ' + d['key'])
        if d.get('url') and d['url'].rsplit('/', 1)[-1] not in PUBLIC and 'github.com' not in d['url']:
            raise SystemExit('a document links a page that is not public: ' + d['url'])
        pages.append({'key': d['key'], 'short': d['short'], 'title': d['title'],
                      'private': not d.get('public'), 'group': d.get('group') or '',
                      'deploys': len(vs), 'first': rel(vs[0]['t']), 'url': d.get('url'),
                      'kind': d.get('kind') or 'page', 'summary': d.get('summary') or ''})
        for v in vs:
            deploys.append([rel(v['t']), i, 1 if v.get('new') else 0, 1])
    deploys.sort()
    coms = sorted(DOC.get('commits', []), key=lambda c: c['t'])
    REPOS = sorted({c.get('repo') or 'et-soc1-prototyping' for c in coms})
    commits = [[rel(c['t']), c['sha'], c['subject'], REPOS.index(c.get('repo') or 'et-soc1-prototyping'),
                c.get('branch') or 'main', c.get('files') or 0] for c in coms]
    ART = {'pages': pages,
           'deploy_cols': ['t', 'page', 'new_space', 'confirmed'], 'deploys': deploys,
           'sessions': REPOS,
           'commit_cols': ['t', 'sha', 'subject', 'session', 'branch', 'files'], 'commits': commits,
           'failed_attempts': [],
           'totals': {'deploys': len(deploys), 'confirmed': len(deploys),
                      'new_spaces': sum(1 for d in deploys if d[2]), 'commits': len(commits),
                      'pages': len(pages), 'public': sum(1 for p in pages if not p['private'])},
           'rules': {'deploy': 'One row per version of a document, from the project hub and the repository.'},
           'note': ''}

    # ---------------------------------------------------------- neighbors = the lanes
    NBS = []
    for s in HEAD:
        busy = union([[rel(a), rel(b)] for a, b in s['busy']], 0)
        ev = [[rel(e['t']), rel(e.get('e') or e['t']), e['kind'], e['title'], e['text']]
              for e in s.get('events', [])]
        ev.sort()
        NBS.append({'id': s['id'], 'n': s.get('members', 1), 'lane': s['lane'], 'name': s['name'],
                    'title': s['title'], 's': rel(s['first']), 'e': rel(s['last']),
                    'busy': busy, 'sub': [[rel(a), rel(b)] for a, b in s.get('sub', [])],
                    'busy_h': sum(b - a for a, b in busy) / 3600, 'agent_h': 0.0, 'agents': 0,
                    'workflow_runs': 0, 'tokens': 0, 'machine': s['machine'],
                    'asks': sum(1 for m in msgs if m[14] == s['id']),
                    'deploys': {'public': 0, 'other': 0}, 'commits': [], 'msgs': [], 'events': ev})
    hosts = [[[IDS.index(c) for c in o['cards'] if c in IDS], rel(o['s']), rel(o['e']), o['kind'],
              o['title'], o['text']] for o in SS.get('outages', [])]
    NEIGH = {'cols': {'msgs': ['t', 'category', 'kind', 'summary', 'text', 'removed', 'lost', 'session', 'chars'],
                      'events': ['t', 'e', 'kind', 'title', 'text'],
                      'hosts': ['cards', 's', 'e', 'kind', 'title', 'text']},
             'sessions': NBS, 'hosts': hosts,
             'rule': 'Ten lanes, each one strand of the thread; a strand may be more than one session.'}

    # ---------------------------------------------------------- per day and per week
    def ov(iv, a, b):
        return sum(max(0.0, min(q[1], b) - max(q[0], a)) for q in iv)

    perday = []
    for d in range(NDAYS):
        a, b = d * DAY, (d + 1) * DAY
        md = [m for m in msgs if a <= m[0] < b]
        pk = max((tot[j] for j in range(max(0, a // 60), min(n, b // 60))), default=0)
        pko = max((cc['cc'][j] + cc['other'][j] for j in range(max(0, a // 60), min(n, b // 60))), default=0)
        perday.append({'day': d, 'label': days[d], 'date': day_iso[d], 'week': day_week[d],
                       'human_n': len(md), 'human_active_min': sum(m[1] for m in md) / 60,
                       'human_active_paste_min': sum(m[1] for m in md) / 60,
                       'engagement_h': ov([[s[0], s[1]] for s in sits], a, b) / 3600,
                       'main_busy_h': ov(spine, a, b) / 3600, 'main_strict_h': ov(spine, a, b) / 3600,
                       'sub_agent_h': sum(ov(s['_busy'], a, b) for s in ALL) / 3600,
                       'peak_sub': pk, 'peak_sub_ok': pko,
                       'card_h': sum(ov(union([[q[1], q[2]] for q in civ if q[0] == k], 120), a, b)
                                     for k in range(len(IDS))) / 3600,
                       'deploys': sum(1 for x in deploys if a <= x[0] < b),
                       'commits': sum(1 for c in commits if a <= c[0] < b),
                       'tokens_main': 0, 'tokens_sub': 0, 'out_main': 0, 'out_sub': 0})
    perweek = []
    for w in weeks:
        rows_w = [p for p in perday if p['day'] * DAY >= w['s'] and p['day'] * DAY < w['e']]
        agg = {'label': w['label'], 'title': w['title'], 's': w['s'], 'e': w['e'],
               'days': len(rows_w), 'date': rows_w[0]['date'] if rows_w else ''}
        for k in ('human_n', 'human_active_min', 'main_busy_h', 'sub_agent_h', 'card_h', 'deploys', 'commits'):
            agg[k] = sum(p[k] for p in rows_w)
        agg['peak_sub_ok'] = max((p['peak_sub_ok'] for p in rows_w), default=0)
        perweek.append(agg)

    # ---------------------------------------------------------- highlights
    HL = []
    for h in HLS['highlights']:
        for ti, u in (h.get('links') or []):
            slug = u.rsplit('/', 1)[-1].split('#')[0]
            if 'spacesheep.dev' in u and slug not in PUBLIC:
                raise SystemExit('a highlight links a page that is not public: ' + u)
        HL.append({'t': rel(h['t']), 'a': rel(h['a']), 'b': rel(h['b']), 'track': h['track'],
                   'title': h['title'], 'caption': h['caption'], 'links': h.get('links') or []})
    HL.sort(key=lambda h: h['t'])
    for h in HL:
        if not (h['a'] <= h['t'] <= h['b']):
            raise SystemExit('a highlight sits outside its own span: ' + h['title'])

    WHO = {'human_active_h': act_h, 'human_active_paste_h': act_h,
           'human_engagement_h': HUMAN['totals']['engagement_h'],
           'main_busy_h': MAIN['totals']['busy_h'], 'main_strict_h': MAIN['totals']['strict_h'],
           'main_tool_wait_h': 0.0, 'main_tool_wait_lab_h': 0.0, 'main_watch_h': 0.0,
           'sub_agent_h': busy_h, 'card_held_h': held_total, 'card_busy_h': busy_total,
           'wall_h': (FULL[1] - FULL[0]) / 3600}

    out = {
        'meta': {'t0_utc': CFG['t0'], 'tz': CFG['tz'], 'full': FULL, 'days': days, 'day_iso': day_iso,
                 'day_week': day_week, 'weeks': weeks, 'session_start': START, 'snapshot_end': SNAP,
                 'title': CFG['title'], 'subtitle': CFG['subtitle'],
                 'generated': datetime.datetime.now(datetime.timezone(TZ)).replace(microsecond=0).isoformat(),
                 'sources': CFG['sources']},
        'human': HUMAN, 'main': MAIN, 'conc': CONC, 'agents': AGENTS, 'cards': CARDS,
        'artifacts': ART, 'neighbors': NEIGH, 'perday': perday, 'perweek': perweek,
        'highlights': HL, 'who': WHO,
    }

    blob = json.dumps(out, ensure_ascii=False)
    hits = scan(blob, PUBLIC)
    if hits:
        for why, ctx in hits[:40]:
            print('PRIVATE: %-56s %s' % (why, ctx[:140]), file=sys.stderr)
        raise SystemExit('%d things a public page must not carry; nothing written' % len(hits))
    bad = scan_curation(QS, blob)
    if bad:
        for why, ctx in bad[:40]:
            print('CURATION: %-56s %s' % (why, ctx[:140]), file=sys.stderr)
        raise SystemExit('%d curated inputs disagree with the page\'s own rule; nothing written'
                         % len(bad))
    with open(os.path.join(ddir, 'timeline.json'), 'w') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    print('timeline.json: %d questions, %d sessions in %d lanes, %d experiment runs on %d cards, '
          '%d documents (%d public), %d commits, %d highlights, %d days in %d weeks'
          % (len(msgs), len(ALL), len(NBS), len(civ), len(IDS), len(pages),
             ART['totals']['public'], len(commits), len(HL), NDAYS, len(weeks)))
    print('coverage: experiments %d of %d in the register have a card interval; %d are recorded undated'
          % (len({q[4] for q in civ}), len({q[4] for q in civ}) + len(CARDS['undated']), len(CARDS['undated'])))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
