#!/usr/bin/env python3
"""Build artifacts.json: every spacesheep deploy, share and visibility change in the session's transcripts,
mapped to the published pages (MIRROR.md), plus every git commit of et-soc1-prototyping.

Input: work/spacesheep_calls.jsonl written by scan_spacesheep.py (Bash calls that mention spacesheep or run a
deploy*.sh wrapper, with their results). Deploys are counted from what the CLI printed (Created/Updated lines,
--json fields, the wrappers' per-page lines); when a command filtered that output away, from the command itself.
Privacy: private pages are 'a private page' (no title, slug, uuid or message); the report for the lab lead is
'a report for the lab lead', unlinked; e-mail addresses are never copied; people's names are scrubbed from text.
"""
import collections, datetime, json, os, re, shlex, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths  # noqa: E402

# Privacy tables (people's names, the lab-lead report's identifiers) are not in this public file: they are read from
# a local JSON file that is never committed, $TIMELINE_PRIVATE (default ~/.config/et-soc1-timeline/private.json).
# Without it the script stops, unless TIMELINE_PRIVATE=none asks for a run with no redactions; check such output before
# publishing anything.
_P = paths.private()
if not _P and os.environ.get('TIMELINE_PRIVATE') != 'none':
    sys.exit(f'no privacy table at {paths.PRIVATE_TABLE}; set TIMELINE_PRIVATE=none to run without redactions')

TL = paths.TL
PDT = datetime.timezone(datetime.timedelta(hours=-7))
REPO = paths.REPO
# the repository's MIRROR.md, then any other checkouts' copies in $TIMELINE_EXTRA_MIRRORS (os.pathsep-separated; a
# branch's MIRROR.md that lists pages main does not yet list); the first listing of a space wins
MIRRORS = [os.path.join(REPO, 'docs', 'reports', 'MIRROR.md')] + \
    [m for m in os.environ.get('TIMELINE_EXTRA_MIRRORS', '').split(os.pathsep) if m]
UUID = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
SLUGURL = r'https://spacesheep\.dev/@yaroslavvb/([\w.-]+)'
LAB_REPORT = 'a report for the lab lead'

NAMES = [tuple(x) for x in _P.get('artifact_name_redactions', [])]


def scrub(s):
    if s is None:
        return None
    for a, b in NAMES:
        s = re.sub(a, b, s)
    return s


def pdt(ts):
    if ts is None:
        return None
    d = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
    return d.astimezone(PDT).isoformat(timespec='seconds')


# ------------------------------------------------------------------ MIRROR
mirror = {}          # uuid -> page
mirror_by_slug = {}
mirror_by_file = {}
private_noid = []
for mp in MIRRORS:
    if not os.path.exists(mp):
        continue
    txt = open(mp).read()
    a, b = txt.find('<!-- mirror:begin -->'), txt.find('<!-- mirror:end -->')
    section = None
    for line in txt[a:b].splitlines():
        if line.startswith('### '):
            section = line[4:].strip()
            continue
        if not line.startswith('|') or line.startswith('|---') or line.startswith('| Page'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 4:
            continue
        m = re.match(r'\[(.*?)\]\((https://spacesheep\.dev/@yaroslavvb/([\w.-]+))\)\s*(.*)', cells[0])
        title = m.group(1) if m else cells[0]
        slug = m.group(3) if m else None
        um = re.search(UUID, cells[1])
        uuid = um.group(0) if um else None
        vis = cells[2]
        fm = re.search(r'`([^`]+)`', cells[3])
        rfile = fm.group(1) if fm else None
        page = dict(uuid=uuid, slug=slug, title=title, visibility=vis, repo_file=rfile, section=section, in_mirror=True)
        if vis == 'private':
            page['private'] = True
        if _P.get('lab_report_title_words') and _P['lab_report_title_words'] in title.lower():
            page['lab_report'] = True
        if uuid:
            mirror.setdefault(uuid, page)
            if slug:
                mirror_by_slug.setdefault(slug, uuid)
            if rfile:
                mirror_by_file.setdefault(os.path.basename(rfile), uuid)
        else:
            private_noid.append(page)

# ------------------------------------------------------------------ transcript rows
rows = [json.loads(l) for l in open(os.path.join(TL, 'work', 'spacesheep_calls.jsonl'))]
rows.sort(key=lambda r: r['ts'] or '')


def strip_heredoc(cmd):
    out, lines, i = [], cmd.split('\n'), 0
    while i < len(lines):
        l = lines[i]
        out.append(l)
        m = re.search(r"<<-?\s*['\"]?(\w+)['\"]?", l)
        if m:
            tag = m.group(1)
            i += 1
            while i < len(lines) and lines[i].strip() != tag:
                i += 1
        i += 1
    return '\n'.join(out)


DEPLOY = re.compile(r"(?:spacesheep(?:\.js)?|\$\{?SS\}?|NODE_SS)[\"']?\s+deploy\b")
SHARE = re.compile(r"(?:spacesheep(?:\.js)?|\$\{?SS\}?)[\"']?\s+share\b")


def segment_after(s, pos):
    """text from pos to the next unquoted ; && || | or newline"""
    q = None
    i = pos
    while i < len(s):
        ch = s[i]
        if q:
            if ch == '\\' and q == '"':
                i += 2
                continue
            if ch == q:
                q = None
        elif ch in '"\'':
            q = ch
        elif ch in ';|\n' or s.startswith('&&', i):
            break
        i += 1
    return s[pos:i]


def in_quotes(s, pos):
    """True when pos sits inside a quoted string (e.g. a grep pattern naming the command)"""
    q = None
    i = 0
    while i < pos:
        ch = s[i]
        if q:
            if ch == '\\' and q == '"':
                i += 2
                continue
            if ch == q:
                q = None
        elif ch == '\\':
            i += 2
            continue
        elif ch in '"\'':
            q = ch
        elif ch == '\n':
            q = None
        i += 1
    return q is not None


def parse_invocation(seg):
    try:
        toks = shlex.split(seg, posix=True)
    except ValueError:
        toks = seg.split()
    args = {'target': None}
    i = 1  # toks[0] == 'deploy'
    while i < len(toks):
        t = toks[i]
        if t in ('--space', '--slug', '--title', '--visibility', '-m', '--message', '--emoji', '--description', '--org'):
            args[t.lstrip('-')] = toks[i + 1] if i + 1 < len(toks) else None
            i += 2
            continue
        if t.startswith('--') or t.startswith('2>') or t == '>':
            if t == '>':
                i += 2
                continue
            i += 1
            continue
        if args['target'] is None:
            args['target'] = t
        i += 1
    if 'm' in args:
        args['message'] = args.pop('m')
    return args


def result_events(res):
    """ordered deploy outcomes printed by the CLI or a wrapper"""
    ev = []
    cur = None
    prev_line = ''
    for line in res.splitlines():
        m = re.search(r'✓ (Created|Updated) ' + SLUGURL, line)
        if m:
            ev.append({'kind': 'created' if m.group(1) == 'Created' else 'updated', 'slug': m.group(2), 'how': 'cli-line'})
            prev_line = line
            continue
        m = re.match(r'^([\w.-]+) \| live=', line)
        if m:
            cur = {'slug': m.group(1), 'how': 'wrapper'}
            m2 = re.search(r'"is_update":(true|false),"visibility":"(\w+)"', line)
            if m2:
                cur['kind'] = 'updated' if m2.group(1) == 'true' else 'created'
                cur['visibility'] = m2.group(2)
                ev.append(cur)
                cur = None
            prev_line = line
            continue
        m = re.match(r'^\s*"is_update":(true|false),"visibility":"(\w+)"', line)
        if m and cur is not None and cur.get('how') == 'wrapper':
            cur['kind'] = 'updated' if m.group(1) == 'true' else 'created'
            cur['visibility'] = m.group(2)
            ev.append(cur)
            cur = None
            continue
        m = re.match(r'^(\S+\.html) is_update:(true|false) visibility:(\w+)', line)
        if m:
            ev.append({'file': m.group(1), 'kind': 'updated' if m.group(2) == 'true' else 'created',
                       'visibility': m.group(3), 'how': 'loop-line'})
            continue
        m = re.match(r'^([\w.-]+) -> "url": "' + SLUGURL, line)
        if m:
            ev.append({'slug': m.group(2), 'kind': 'updated', 'how': 'loop-url', 'requested_slug': m.group(1)})
            continue
        m = re.match(r'^ {0,2}"(uuid|url|is_update|visibility)": (.*?),?$', line)
        if m:
            k, v = m.group(1), m.group(2).strip().strip('"')
            if cur is None or cur.get('how') != 'json' or k in cur['_keys']:
                if cur is not None and cur.get('how') == 'json':
                    ev.append(cur)
                cur = {'how': 'json', '_keys': set()}
            cur['_keys'].add(k)
            if k == 'url':
                sm = re.search(SLUGURL, v)
                cur['slug'] = sm.group(1) if sm else None
            elif k == 'uuid':
                cur['uuid'] = v
            elif k == 'is_update':
                cur['kind'] = 'updated' if v == 'true' else 'created'
            elif k == 'visibility':
                cur['visibility'] = v
            continue
        prev_line = line
    if cur is not None and cur.get('how') == 'json':
        ev.append(cur)
    return ev


# ---- slug <-> uuid aliases seen anywhere in the spacesheep output
alias = dict(mirror_by_slug)
alias_src = collections.defaultdict(set)
for r in rows:
    res = r.get('result') or ''
    cmd = r['cmd']
    for m in re.finditer(r'"(?:uuid|space|id)": "(' + UUID + r')",?\s*\n\s*"url": "' + SLUGURL, res):
        alias_src[m.group(2)].add(m.group(1))
    for m in re.finditer(r'^([\w.-]+) (' + UUID + r')$', res, re.M):
        alias_src[m.group(1)].add(m.group(2))
    for m in re.finditer(r'"id": "(' + UUID + r')",\s*\n\s*"title": "[^"]*",\s*\n\s*"slug": "([\w.-]+)"', res):
        alias_src[m.group(2)].add(m.group(1))
    for m in re.finditer(r"\('([\w.-]+)', '(?:public|private)', '[^']*'\)\]", res):
        pass
    s = strip_heredoc(cmd)
    lk = re.findall(r"s(?:\.get\('slug'\)|\['slug'\])==['\"]([\w.-]+)['\"]", s)
    if len(set(lk)) == 1:
        um = re.search(r'^(?:uuid )?(' + UUID + r')$', res, re.M)
        if um:
            alias_src[lk[0]].add(um.group(1))
        for m in re.finditer(r'Shared space (' + UUID + r')|Space (' + UUID + r') visibility set', res):
            alias_src[lk[0]].add(m.group(1) or m.group(2))
    for dm in DEPLOY.finditer(s):
        a = parse_invocation(segment_after(s, dm.end() - len('deploy')))
        sp, sl = a.get('space'), a.get('slug')
        if sp and re.fullmatch(UUID, sp) and sl and re.fullmatch(r'[\w.-]+', sl):
            alias_src[sl].add(sp)
    # "uuid <u>" printed after a deploy of a known slug, "Space <u> visibility set" after a slug deploy
alias_src.pop('uuid', None)
for sl, us in alias_src.items():
    if len(us) == 1:
        alias.setdefault(sl, next(iter(us)))
# known re-slugs, verified in the transcript
alias.setdefault('hotline-deploy', 'ac439287-4503-42c7-88e7-b5d3e3b64b06')   # created by a folder deploy, re-slugged to et-soc1-hot-line
conflicts = {sl: sorted(us) for sl, us in alias_src.items() if len(us) > 1}

# ------------------------------------------------------------------ walk the rows
deploys = []
vis_obs = []   # (ts, uuid or slug, visibility, source)
shares = []
unresolved = []
for r in rows:
    cmd = r['cmd']
    s = strip_heredoc(cmd)
    res = r.get('result') or ''
    ts = r['ts']
    session = 'main' if r['file'] == 'main' else ('earlier session' if r['file'] == 'earlier-session' else 'subagent')

    # visibility observations from list output, anywhere
    for m in re.finditer(r'^\S+\s+(.*?)\s+(public|private|unlisted|signedin)\s+' + SLUGURL, res, re.M):
        if ts.startswith('2026-09-20T19:55:19'):
            continue  # this listing shows the memory-anatomy space under the observability slug (stale pin)
        vis_obs.append(dict(ts=ts, slug=m.group(3), visibility=m.group(2), source='spacesheep list'))
    for m in re.finditer(r"\('([\w.-]+)', '(public|private)', '[^']*'\)", res):
        vis_obs.append(dict(ts=ts, slug=m.group(1), visibility=m.group(2), source='spacesheep list --json'))
    # share results
    for m in re.finditer(r"Space (" + UUID + r") visibility set to '(\w+)'", res):
        shares.append(dict(ts=ts, uuid=m.group(1), action=f'visibility set to {m.group(2)}', session=session))
        vis_obs.append(dict(ts=ts, uuid=m.group(1), visibility=m.group(2), source='spacesheep share'))
    for m in re.finditer(r'Shared space (' + UUID + r') with: (.+)', res):
        n = len([x for x in m.group(2).split(',') if x.strip()])
        shares.append(dict(ts=ts, uuid=m.group(1), action=f'shared with {n} named person' + ('s' if n > 1 else ''), session=session))

    is_help = bool(re.search(r'deploy --help', s)) and not re.search(r'deploy (?!--help)\S', s.replace('deploy --help', ''))
    invs = []
    for dm in DEPLOY.finditer(s):
        seg = segment_after(s, dm.end() - len('deploy'))
        if '--help' in seg or in_quotes(s, dm.start()):
            continue
        invs.append(parse_invocation(seg))
    wrapper = bool(re.search(r'deploy_all\.sh', s))
    evs = result_events(res)
    if not invs and not (wrapper and evs):
        continue
    loop = wrapper or bool(re.search(r'\b(for|while)\b[^\n]*\b(do)\b', s)) and bool(invs) and \
        any(re.search(r'\bdo\b[^\n]*' + re.escape('deploy'), l) or 'while' in l for l in s.split('\n') if 'deploy' in l)
    via = ('wrapper deploy_all.sh' if wrapper else 'node spacesheep.js' if ('spacesheep.js' in s or 'NODE_SS' in s)
           else 'npx spacesheep' if 'npx' in s else 'spacesheep CLI')

    # resolve each invocation's source file (cp X.html DIR/index.html) and space
    cps = re.findall(r'cp\s+"?(\S+?\.html)"?\s+"?(\S+?)/index\.html"?', s)

    def inv_file(a):
        t = (a.get('target') or '').rstrip('/')
        if t.endswith('.html'):
            return os.path.basename(t)
        for src, dst in cps:
            if dst.rstrip('/') == t or dst.split('/')[-1] == t.split('/')[-1]:
                return os.path.basename(src)
        return None

    records = []
    if loop or not invs:
        for e in evs:
            records.append(dict(event=e, inv={}, confirmed=True))
    else:
        if len(evs) >= len(invs):
            for a, e in zip(invs, evs[:len(invs)]):
                records.append(dict(event=e, inv=a, confirmed=True))
        else:
            ones = sum(1 for l in res.splitlines() if l.strip() == '1') if 'grep -c Updated' in s else 0
            for k, a in enumerate(invs):
                e = evs[k] if k < len(evs) else {}
                conf = bool(e) or k < len(evs) + ones
                records.append(dict(event=e, inv=a, confirmed=conf))

    for rec in records:
        e, a = rec['event'], rec['inv']
        slug = e.get('slug') or (a.get('slug') if a.get('slug') and '$' not in a.get('slug') else None)
        uuid = e.get('uuid')
        sp = a.get('space')
        if not uuid and sp and re.fullmatch(UUID, sp):
            uuid = sp
        if not uuid and sp and sp.startswith('https://'):
            m = re.search(SLUGURL, sp)
            if m and m.group(1) in alias:
                uuid = alias[m.group(1)]
        if not uuid and slug and slug in alias:
            uuid = alias[slug]
        f = e.get('file') or inv_file(a)
        if not uuid and f and f in mirror_by_file:
            uuid = mirror_by_file[f]
        if not uuid and _P.get('lab_report_file_word') and _P['lab_report_file_word'] in (f or ''):
            uuid = 'LAB-REPORT'
        note = None
        if ts.startswith('2026-09-20T19:55:19') and slug == 'et-soc1-limits-of-observability':
            uuid = '2bf74fd1-fd7f-4e19-8e35-6168ae42657c'
            note = 'stale pin file: the observability page went to the memory-anatomy space (re-slugged); restored 33 s later'
        if ts.startswith('2026-09-22T20:26:33') and slug == 'et-soc1-dvfs-leakage':
            note = 'stale pin file: the hot-line page went to the DVFS space; restored 18 s later'
        new = e.get('kind') == 'created' if e.get('kind') else (sp is None and bool(a.get('title')))
        if not rec['confirmed']:
            new = False
        d = dict(ts=ts, ts_pdt=pdt(ts), uuid=uuid, slug=slug, file=f, new_space=bool(new),
                 confirmed=rec['confirmed'], visibility_after=e.get('visibility'), visibility_flag=a.get('visibility'),
                 message=a.get('message'), via=via, session=session, transcript=r['file'], how=e.get('how', 'command'),
                 note=note)
        deploys.append(d)
        if d['visibility_after']:
            vis_obs.append(dict(ts=ts, dep=d, visibility=d['visibility_after'], source='deploy output'))
        if d['new_space'] and a.get('visibility'):
            vis_obs.append(dict(ts=ts, dep=d, visibility=a['visibility'], source='created with --visibility'))

# resolve the lab report and other non-MIRROR spaces
LAB_UUIDS = set()
for sl, u in alias.items():
    if _P.get('lab_report_slug_prefix') and sl.startswith(_P['lab_report_slug_prefix']):
        LAB_UUIDS.add(u)
for d in deploys:
    if d['uuid'] == 'LAB-REPORT' or (_P.get('lab_report_slug_prefix') and (d['slug'] or '').startswith(_P['lab_report_slug_prefix'])) or (_P.get('lab_report_file_word') and _P['lab_report_file_word'] in (d['file'] or '')):
        d['uuid'] = next(iter(LAB_UUIDS)) if LAB_UUIDS else 'lab-report'
        LAB_UUIDS.add(d['uuid'])
    if not d['uuid'] and d['slug']:
        d['uuid'] = 'slug:' + d['slug']
    if not d['uuid']:
        unresolved.append(dict(ts=d['ts_pdt'], file=d['file'], how=d['how']))
for o in vis_obs:
    if 'dep' in o:
        o['uuid'] = o.pop('dep')['uuid']
    elif 'uuid' not in o:
        o['uuid'] = alias.get(o['slug'])
keep_uuids = set(mirror) | {d['uuid'] for d in deploys if d['uuid']} | {s['uuid'] for s in shares}

# ------------------------------------------------------------------ pages
uuid_slugs = collections.defaultdict(set)
for sl, u in alias.items():
    uuid_slugs[u].add(sl)
pages = {}
priv_n = 0
outside_n = 0


def page_for(u):
    global priv_n, outside_n
    if u in pages:
        return pages[u]
    if u in LAB_UUIDS or (u in mirror and mirror[u].get('lab_report')):
        p = dict(key='lab-report', title=LAB_REPORT, private=True, in_mirror=True, group='private')
    elif u in mirror:
        mp = mirror[u]
        if mp.get('private'):
            priv_n += 1
            p = dict(key=f'private-{priv_n}', title='a private page', private=True, in_mirror=True, group='private')
        else:
            p = dict(key=mp['slug'], title=mp['title'], slug=mp['slug'], uuid=u, visibility_now=mp['visibility'],
                     repo_file=mp['repo_file'], in_mirror=True, group=mp['section'])
    else:
        outside_n += 1
        p = dict(key=f'outside-{outside_n}', title='a page outside the ET-SoC-1 report set (tool debugging)',
                 private=True, in_mirror=False, group='outside the report set')
    p['_uuid'] = u
    pages[u] = p
    return p


out_deploys = []
for d in deploys:
    u = d['uuid']
    if not u:
        continue
    p = page_for(u)
    o = dict(ts=d['ts_pdt'], page=p['key'], title=p['title'], new_space=d['new_space'], confirmed=d['confirmed'],
             via=d['via'], session=d['session'])
    if d.get('note'):
        o['note'] = d['note']
    if not p.get('private'):
        o['uuid'] = u
        o['message'] = scrub(d['message'])
        o['visibility_after'] = d['visibility_after']
        if d['slug'] and d['slug'] != p.get('slug'):
            o['slug_at_the_time'] = d['slug']
    out_deploys.append(o)

# ------------------------------------------------------------------ the spaces' version history
# A deploy whose output the command filtered away (a loop that printed only its failures, or only the CLI's update
# notice) left no Created/Updated line in the transcripts. spacesheep keeps every version of a space
# (`spacesheep versions <uuid>`: id, UTC minute, message), so each version of a MIRROR page from VERS_FROM on with no
# transcript deploy of that page within 3 minutes is added from the history (via 'version history'). Before VERS_FROM
# the transcripts are complete, and another session also deployed (26 Sep), which the history cannot tell apart.
# The histories are cached in work/versions/ ($TIMELINE_VERSIONS_FETCH=0 reuses the cache without the network).
VERS_DIR = os.path.join(TL, 'work', 'versions')
VERS_FROM = datetime.datetime(2026, 9, 27, 12, 0, tzinfo=PDT)
# pages a cron job on aifoundry2 republishes on its own (the dashboard every 10 minutes since 30 Sep, the history page every
# 5 minutes since 2 Oct): their version histories are mostly the job's, and `spacesheep versions` lists only the latest
# ones, so only a session's own deploys of them (from its transcript) are counted
AUTO_PAGES = {'aifoundry-lab-dashboard', 'aifoundry-lab-history'}
VERS_TO = (datetime.datetime.fromisoformat(os.environ['TIMELINE_CUTOFF'].replace('Z', '+00:00'))
           if os.environ.get('TIMELINE_CUTOFF') else datetime.datetime.now(datetime.timezone.utc))


def space_versions(u):
    f = os.path.join(VERS_DIR, u + '.txt')
    if os.environ.get('TIMELINE_VERSIONS_FETCH', '1') == '1':
        try:
            r = subprocess.run(['spacesheep', 'versions', u], capture_output=True, text=True, timeout=120)
            if r.returncode == 0 and re.search(r'^[0-9a-f]{12}\s', r.stdout, re.M):
                os.makedirs(VERS_DIR, exist_ok=True)
                open(f, 'w').write(r.stdout)
        except (OSError, subprocess.SubprocessError):
            pass
    try:
        txt = open(f).read()
    except OSError:
        return []
    rows = []
    for line in txt.splitlines():
        m = re.match(r'^([0-9a-f]{12})\s+(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})\s+(.*)$', line)
        if m:
            t = datetime.datetime.fromisoformat(m.group(2) + ':00+00:00')
            rows.append((t, m.group(1), m.group(3).strip()))
    return sorted(rows)


# the neighbor sessions' own deploys (extract_neighbors.py): their versions are not this session's
try:
    NEIGHBOR_DEPLOYS = [(d['uuid'], datetime.datetime.fromisoformat(d['ts'].replace('Z', '+00:00')))
                        for d in json.load(open(os.path.join(TL, 'work', 'neighbor_deploys.json'))) if d.get('uuid')]
except (OSError, ValueError):
    NEIGHBOR_DEPLOYS = []
vers_added, vers_neighbor = [], 0
for u in sorted(mirror):
    vs = space_versions(u)
    if not vs:
        continue
    p = page_for(u)
    have = [datetime.datetime.fromisoformat(o['ts']) for o in out_deploys if o['page'] == p['key']]
    have += [t for nu, t in NEIGHBOR_DEPLOYS if nu == u]
    vers_neighbor += sum(1 for t, _, _ in vs if VERS_FROM <= t <= VERS_TO and any(nu == u and abs((t - nt).total_seconds()) <= 180
                                                                              for nu, nt in NEIGHBOR_DEPLOYS))
    if (p.get('slug') or p['key']) in AUTO_PAGES:   # republished by its own cron job: those versions are not a session's
        continue
    for i, (t, vid, msg) in enumerate(vs):
        if not (VERS_FROM <= t <= VERS_TO):
            continue
        if any(abs((t - h).total_seconds()) <= 180 for h in have):
            continue
        o = dict(ts=t.astimezone(PDT).isoformat(timespec='seconds'), page=p['key'], title=p['title'], new_space=(i == 0),
                 confirmed=True, via='version history', session='version history')
        if not p.get('private'):
            o['uuid'] = u
            o['message'] = scrub(msg)
        out_deploys.append(o)
        vers_added.append(o)
out_deploys.sort(key=lambda o: o['ts'])
print(f'version history: {len(vers_added)} deploys added (no transcript deploy within 3 min); {vers_neighbor} left out '
      f'as a neighbor session\'s (work/neighbor_deploys.json)', file=sys.stderr)

# visibility timeline per page: record changes only
vis_changes = []
last = {}
for o in sorted(vis_obs, key=lambda x: x['ts']):
    u = o.get('uuid')
    if not u or u not in keep_uuids:
        continue
    p = page_for(u)
    v = o['visibility']
    if last.get(u) != v:
        vis_changes.append(dict(ts=pdt(o['ts']), page=p['key'], title=p['title'], visibility=v,
                                previous=last.get(u), seen_via=o['source']))
        last[u] = v
out_shares = []
for s in shares:
    p = page_for(s['uuid'])
    out_shares.append(dict(ts=pdt(s['ts']), page=p['key'], title=p['title'], action=s['action'], session=s['session']))

per_page = collections.Counter(o['page'] for o in out_deploys if o['confirmed'])
per_page_conf = collections.Counter(o['page'] for o in out_deploys if o['confirmed'])
page_list = []
for u, p in pages.items():
    k = p['key']
    ds = [o for o in out_deploys if o['page'] == k]
    q = {kk: vv for kk, vv in p.items() if not kk.startswith('_')}
    q.update(deploys=len(ds), deploys_confirmed=sum(1 for o in ds if o['confirmed']),
             first_deploy=min((o['ts'] for o in ds), default=None), last_deploy=max((o['ts'] for o in ds), default=None),
             created_in_session=next((o['ts'] for o in ds if o['new_space']), None),
             visibility_changes=[{'ts': v['ts'], 'visibility': v['visibility'], 'previous': v['previous'], 'seen_via': v['seen_via']}
                                 for v in vis_changes if v['page'] == k])
    if not p.get('private'):
        q['other_slugs_seen'] = sorted(uuid_slugs.get(u, set()) - {p.get('slug')})
    page_list.append(q)
# MIRROR pages never deployed in the transcripts
for u, mp in mirror.items():
    if u not in pages and not mp.get('private'):
        page_list.append(dict(key=mp['slug'], title=mp['title'], slug=mp['slug'], uuid=u, visibility_now=mp['visibility'],
                              repo_file=mp['repo_file'], in_mirror=True, group=mp['section'], deploys=0, deploys_confirmed=0,
                              note='no deploy of this space in the transcripts'))
page_list.sort(key=lambda p: -p['deploys'])

# ------------------------------------------------------------------ git commits
fmt = '%x1e%H%x1f%aI%x1f%s%x1f%(trailers:key=Claude-Session,valueonly,separator=%x2c)'
log = subprocess.run(['git', '-C', REPO, 'log', '--all', '--name-only', '--format=' + fmt], capture_output=True, text=True).stdout
branches = subprocess.run(['git', '-C', REPO, 'branch', '-a', '--format=%(refname:short)'], capture_output=True, text=True).stdout.split()
branch_sets = {}
for br in branches:
    if br.endswith('/HEAD') or br == 'origin':
        continue
    shas = subprocess.run(['git', '-C', REPO, 'rev-list', br], capture_output=True, text=True).stdout.split()
    branch_sets[br] = set(shas)
# the session's Claude-Session trailers: its first account, then the account it continued on from 30 September 12:41
THIS_SESSION = ('session_01Hcd8Dn7o898BaSoSKpTor4', 'session_01PPEsvPNUJPL3VFGFH5ERdD')
commits = []
file2title = {os.path.basename(mp['repo_file']): (mp['slug'], mp['title']) for mp in mirror.values()
              if mp.get('repo_file') and not mp.get('private')}
for chunk in log.split('\x1e')[1:]:
    head, _, files = chunk.partition('\n')
    sha, date, subj, sess = head.split('\x1f')
    fl = [f for f in files.strip().split('\n') if f]
    pagefiles = [f for f in fl if re.fullmatch(r'docs/reports/[^/]+\.html', f) or f == 'docs/report/index.html']
    d = datetime.datetime.fromisoformat(date).astimezone(PDT)
    short = scrub(subj)
    if len(short) > 110:
        short = short[:107].rstrip() + '...'
    sess = sess.strip()
    commits.append(dict(sha=sha[:7], ts=d.isoformat(timespec='seconds'), subject=short, files=len(fl),
                        branches=sorted(br.replace('origin/claude/', 'other-session-branch:') for br, ss in branch_sets.items() if sha in ss),
                        claude_session=('this session' if any(k in sess for k in THIS_SESSION) else 'another session' if sess else 'none recorded'),
                        touches_page=bool(pagefiles),
                        pages=[file2title.get(os.path.basename(f), (None, os.path.basename(f)))[0] or os.path.basename(f) for f in pagefiles]))
commits.sort(key=lambda c: c['ts'])
cont = subprocess.run(['git', '-C', REPO, 'branch', '-a', '--contains', commits[0]['sha']], capture_output=True, text=True).stdout if commits else ''

out = {
    'generated': datetime.datetime.now(PDT).isoformat(timespec='seconds'),
    'timezone': 'America/Los_Angeles (PDT, UTC-7)',
    'sources': {'transcripts': 'main session, the 19 Sep earlier session and every subagent / workflow agent transcript '
                               '(this timeline run excluded), Bash calls only',
                'mirror': ['docs/reports/MIRROR.md' if m == MIRRORS[0] else 'MIRROR.md of another checkout'
                           for m in MIRRORS if os.path.exists(m)],
                'repo': 'et-soc1-prototyping (git log --all; branches: ' + ', '.join(branches) + ')'},
    'rules': {'deploy': 'one publish of one page: a "✓ Created/Updated" line, a --json result, or a wrapper\'s per-page line; '
                        'when output was filtered away, one per deploy invocation in the command (confirmed=false unless a count of '
                        'Updated lines shows it)',
              'version_history': 'from 27 Sep 12:00 PDT on, each version in a MIRROR page\'s spacesheep history with no transcript '
                                 'deploy of that page within 3 min is added (via "version history"): deploys whose output a '
                                 'command filtered away',
              'new_space': 'the CLI said Created / is_update false',
              'private': 'pages MIRROR lists as private, the report for the lab lead and spaces outside the report set are shown '
                         'without title, slug, uuid or message'},
    'totals': {'deploys': len(out_deploys), 'deploys_confirmed': sum(1 for o in out_deploys if o['confirmed']),
               'new_spaces': sum(1 for o in out_deploys if o['new_space']),
               'pages_deployed': len(per_page), 'deploys_per_page': dict(per_page.most_common()),
               'shares': len(out_shares), 'visibility_changes': len(vis_changes),
               'commits': len(commits), 'commits_touching_pages': sum(1 for c in commits if c['touches_page']),
               'deploys_by_session': dict(collections.Counter(o['session'] for o in out_deploys))},
    'pages': page_list,
    'deploys': out_deploys,
    'shares': out_shares,
    'visibility_changes': vis_changes,
    'commits': commits,
    'unresolved_deploys': unresolved,
    'deploys_not_in_transcripts': {
        'note': 'Commits from another Claude session (branch claude/modest-pascal-x285lv, the evening of 26 September PDT) record deploys and '
                'visibility changes that do not appear in these transcripts; they are listed here from the commits only.',
        'commits': [dict(sha=c['sha'], ts=c['ts'], subject=c['subject']) for c in commits
                    if c['claude_session'] == 'another session' and re.search(r'MIRROR|deploy|public|live equals', c['subject'])]},
    'slug_conflicts': {k: len(v) for k, v in conflicts.items()},
}
json.dump(out, open(os.path.join(TL, 'artifacts.json'), 'w'), indent=1, ensure_ascii=False)

print(json.dumps(out['totals'], indent=1, ensure_ascii=False))
print('unresolved', unresolved)
print('conflicts', conflicts)
for p in page_list:
    print(f"{p['deploys']:3d} ({p.get('deploys_confirmed')}) {p['key'][:44]:44s} {p['title'][:50]:50s} created={p.get('created_in_session')}")
