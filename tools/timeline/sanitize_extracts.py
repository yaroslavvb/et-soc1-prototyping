#!/usr/bin/env python3
"""Remove from the timeline's extracts what the public page withholds, and check that nothing private is left.

    tools/timeline/sanitize_extracts.py [data_dir]

The extraction scripts write their extracts to $TIMELINE_DIR; the copies in data_dir
(default docs/reports/data/2026-09-27-session-timeline) are public, so this script rewrites them in place with the
page's own redactions, and build_timeline_data.py applies the same functions again to what it reads and to the
timeline.json it writes:

  every file      the privacy table's "sanitize" rules are applied to every string (summaries, labels, names,
                  subjects, captions); a "source" or "file" field that holds an absolute path keeps only its basename
  artifacts.json  commit subjects that mention the report for the lab lead become a neutral line (commits[] and
                  deploys_not_in_transcripts.commits[]); spaces outside the report set that are not listed on the page
                  (a lab-accounts space) lose their title, slug and uuid; deploys of private pages lose uuid and message
  agents.json     the agents of the report for the lab lead lose their labels, descriptions and phases, and its
                  workflows their summaries and phases

Then every file in data_dir is scanned: for the patterns of the local privacy table ($TIMELINE_PRIVATE, never
committed; see paths.py), for the FORBIDDEN list (privilege words, addresses, keys, e-mail addresses, local paths), and
for any space uuid (in a uuid field, an address or a --space argument) that docs/reports/MIRROR.md does
not list as public; any hit is printed and the script
exits with status 1. It is idempotent: a second run changes nothing.

The rule (AGENT.md, section 10, "the repository is public"): the page and its data never say which account has which
privilege or how the machines are reached, never name other people beyond the few already public, and never link a
private page. The owner-message summaries are written that way at the source (extract_main.py, SUMMARIES); the
rewrite rules for other strings are read from the privacy table, because they would name what they remove.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402

ROOT = paths.REPO
PRIVATE = 'a report for the lab lead'
NEUTRAL_SUBJECT = 'A change to the handling of the report for the lab lead (subject withheld)'
UNLISTED = {'aifoundry-lab-accounts'}   # public spaces outside the report set that the page does not list

# (pattern, replacement) pairs from the privacy table, applied in order to every string the page shows and every
# string of the committed data
SANITIZE = [tuple(x) for x in paths.private().get('sanitize', [])]
_SAN = [(re.compile(p), r) for p, r in SANITIZE]


def clean(s):
    """A string as the page may show it."""
    if not isinstance(s, str):
        return s
    for rx, rep in _SAN:
        s = rx.sub(rep, s)
    return s


def sanitize_tree(o, key=None):
    """The sanitize rules applied to every string of a JSON tree, in place; an absolute path in a 'source' or 'file' field
    keeps only its basename. Returns the tree."""
    if isinstance(o, dict):
        for k, v in list(o.items()):
            if k in ('source', 'file') and isinstance(v, str) and v.startswith('/'):
                o[k] = os.path.basename(v)
            else:
                o[k] = sanitize_tree(v, k)
        return o
    if isinstance(o, list):
        for i, v in enumerate(o):
            o[i] = sanitize_tree(v)
        return o
    return clean(o)


def subject(s):
    """A commit subject as the page may show it."""
    if re.search(r'lab lead', s or '', re.I) and 'troubleshooting report' not in s:
        return NEUTRAL_SUBJECT
    return clean(s)


def summary(s):
    """A workflow summary as the page may show it."""
    return clean(s or '')


def sanitize_artifacts(R):
    for c in R.get('commits', []) + R.get('deploys_not_in_transcripts', {}).get('commits', []):
        c['subject'] = subject(c['subject'])
    other = {}
    for p in R.get('pages', []):
        if p['key'] in UNLISTED or p['key'].startswith('other-'):
            k = other.setdefault(p['key'], p['key'] if p['key'].startswith('other-') else f'other-{len(other) + 1}')
            p.update({'key': k, 'title': 'a page outside the report set', 'slug': None, 'uuid': None, 'repo_file': None,
                      'private': True, 'group': 'outside the report set'})
            for v in p.get('visibility_changes') or []:
                v.update({'page': k, 'title': 'a page outside the report set'})
    for lst in ('visibility_changes', 'shares', 'deploys'):
        for v in R.get(lst, []):
            if v.get('page') in other:
                v.update({'page': other[v['page']], 'title': 'a page outside the report set'})
    priv = {p['key'] for p in R.get('pages', []) if p.get('private')}
    for d in R.get('deploys', []):
        if d.get('page') in priv:
            d['uuid'] = None
            d['message'] = None
    tot = R.get('totals', {}).get('deploys_per_page')
    if tot:
        for old, new in other.items():
            if old in tot:
                tot[new] = tot.pop(old)
    return sanitize_tree(R)


def sanitize_agents(A):
    priv = {w['run_id'] for w in A.get('workflows', []) if w.get('private')}
    for w in A.get('workflows', []):
        w['summary'] = '' if w.get('private') else summary(w.get('summary'))
        if w.get('private'):
            w['phases'] = []
    for a in A.get('agents', []):
        if a.get('workflow_run') in priv:
            a['label'] = f'agent of {PRIVATE}'
            a['description'] = f'agent of {PRIVATE}'
            a['phase'] = None
    return sanitize_tree(A)


# must not appear in any public extract (any case)
FORBIDDEN = [
    r'\broot\b(?![\s-]+(?:caus|port|complex))', r'\broot@', r'\bsudo', r'nopasswd', r'visudo', r'authorized_keys', r'\bacl\b',
    r'tailscale|tailnet', r'\btag:[a-z]', r'\bssh\s+(?:-\S+\s+)*root\b',
    r'\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3}\b', r'\b192\.168\.\d', r'\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    r'\bsst_[A-Za-z0-9]', r'\bss_[A-Za-z0-9]{6,}', r'[\w.+-]+@[\w-]+\.[a-z]{2,}\b',
    r'/home/', r'/tmp/claude', r'\.claude/projects', r'\bhas (?:root|sudo|admin)', r'\b\w+-authorized\b',
    r'lab[- ]machine accounts', r'aifoundry-lab-accounts',
]
UUID = re.compile(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b')
_U = r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
# a uuid where it names a spacesheep space (a field, an address or a --space argument); message ids and session ids
# are uuids too, and are not checked
SPACE_UUID = re.compile(r'(?:"(?:uuid|space|space_uuid|_uuid)"\s*:\s*"|spacesheep\.dev/space/|--space[ =]"?|https://)' + _U +
                        r'|' + _U + r'\.spacesheep\.app')


def public_spaces():
    """The space uuids docs/reports/MIRROR.md lists as public (plus the two session ids the extracts name)."""
    ok = {paths.SID, paths.PRE_SID}
    try:
        txt = open(os.path.join(ROOT, 'docs', 'reports', 'MIRROR.md'), encoding='utf-8').read()
    except OSError:
        return ok
    a, b = txt.find('<!-- mirror:begin -->'), txt.find('<!-- mirror:end -->')
    for line in txt[a:b].splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 3 and re.match(r'public\b', cells[2]):   # 'public', or 'public (deployed private at ..., made public ...)'
            ok.update(UUID.findall(cells[1]))
    return ok


def private_patterns():
    """The privacy table's patterns as (pattern, flags): the names it redacts and the private report's identifiers
    (case-sensitive), and its "forbidden" list (any case)."""
    P = paths.private()
    if not P:
        print(f'warning: no privacy table at {paths.PRIVATE_TABLE}: only the fixed list is checked', file=sys.stderr)
        return []
    pats = [x[0] for x in P.get('agent_name_redactions', []) + P.get('artifact_name_redactions', [])]
    pats += [re.escape(w) for w in (P.get('lab_report_slug_prefix'), P.get('lab_report_title_words'),
                                    P.get('lab_report_file_word')) if w]
    pats += [re.escape(n) for n in P.get('private_workflows', {})]
    return [(p, 0) for p in pats] + [(p, re.I) for p in P.get('forbidden', [])]


def scan_text(name, s, pats, public):
    bad = 0
    for p, rx in pats:
        for m in rx.finditer(s):
            bad += 1
            print(f'{name}: /{p}/ matches ...{s[max(0, m.start() - 40):m.end() + 40]!r}...')
    for m in SPACE_UUID.finditer(s):
        u = m.group(1) or m.group(2)
        if u not in public:
            bad += 1
            print(f'{name}: a space that MIRROR.md does not list as public: ...{s[max(0, m.start() - 60):m.end() + 20]!r}...')
    return bad


def compiled():
    return [(p, re.compile(p, fl)) for p, fl in private_patterns()] + [(p, re.compile(p, re.I)) for p in FORBIDDEN]


def scan(dd):
    pats, public = compiled(), public_spaces()
    return sum(scan_text(f, open(os.path.join(dd, f), encoding='utf-8').read(), pats, public)
               for f in sorted(os.listdir(dd)) if f.endswith('.json'))


FIXERS = {'artifacts.json': sanitize_artifacts, 'agents.json': sanitize_agents}

if __name__ == '__main__':
    dd = sys.argv[1] if len(sys.argv) > 1 else paths.DATA_DIR
    for f in sorted(os.listdir(dd)):
        if not f.endswith('.json'):
            continue
        p = os.path.join(dd, f)
        raw = open(p, encoding='utf-8').read()
        d = FIXERS.get(f, sanitize_tree)(json.loads(raw))
        compact = not raw.lstrip().startswith('{\n')
        new = json.dumps(d, ensure_ascii=False, separators=(',', ':')) if compact else json.dumps(d, ensure_ascii=False, indent=1)
        if new != raw:
            open(p, 'w', encoding='utf-8').write(new)
            print('rewrote', p)
    n = scan(dd)
    print('privacy scan:', 'clean' if not n else f'{n} hits')
    sys.exit(1 if n else 0)
