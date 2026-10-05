"""The owner's prompts as the public page may show them (since 5 Oct 2026 the page shows each message's own words, at the
owner's request, not only a summary). AGENT.md section 10 still holds, so a prompt is shown with these parts removed,
each replaced by a visible marker "[removed: <what>]":

  a sentence about machine access   any sentence (or line) that mentions root, sudo, ssh or scp, Tailscale, keys or
                                    passwords, ACLs, or who may log in where: how the machines are reached is withheld
  a permission setting              the agents' permission mode
  an address, an e-mail address     IP addresses and e-mail addresses
  a path                            absolute paths on the machines
  a private page, a session page    spacesheep links to pages that docs/reports/MIRROR.md does not list as public, and
                                    links to the owner's sessions; the report for the lab lead is never named (its links
                                    and its name become "the report for the lab lead", as everywhere on the page)
  a name, a place                   other people's names and places, from the privacy table ("prompt_redactions",
                                    "artifact_name_redactions" and "agent_name_redactions", applied in any case), because
                                    a public rule would itself name them

Then the result must pass sanitize_extracts.py's scan (FORBIDDEN, the privacy table's patterns and space uuids); any
sentence that still matches is removed whole. redact() returns the shown text and the list of what was removed.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paths  # noqa: E402

UUID = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
ACCESS = re.compile(r'\broot\b(?![\s-]+(?:caus|port|complex|of|level))|\bsudo|\bssh\b|\bscp\b|tailscale|tailnet|authorized_keys|'
                    r'passwordless|password|passwd|nopasswd|\bacl\b|\bprivate key|\bkeypair|\bsu -|\bas admin\b|'
                    r'\badmin(?:istrator)? access|log(?:s|ged)? ?in as\b|\bpermission to log', re.I)
SENTENCE = re.compile(r'[^.!?\n]*(?:[.!?]+(?=\s|$)|\n|$)')


def _mirror():
    """slug -> uuid of every page MIRROR.md lists as public"""
    out = {}
    try:
        txt = open(os.path.join(paths.REPO, 'docs', 'reports', 'MIRROR.md'), encoding='utf-8').read()
    except OSError:
        return out
    a, b = txt.find('<!-- mirror:begin -->'), txt.find('<!-- mirror:end -->')
    for line in txt[a:b].splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 3 or not re.match(r'public\b', cells[2]):
            continue
        m, u = re.search(r'\(https://spacesheep\.dev/@yaroslavvb/([\w.-]+)\)', cells[0]), re.search(UUID, cells[1])
        if m and u:
            out[m.group(1)] = u.group(0)
    return out


_P = None


def _table():
    global _P
    if _P is None:
        P = paths.private()
        names = [tuple(x) for x in P.get('prompt_redactions', [])]
        names += [tuple(x) for x in P.get('artifact_name_redactions', []) + P.get('agent_name_redactions', [])]
        import sanitize_extracts as SX   # its fixed FORBIDDEN list: a sentence that matches one is removed whole
        _P = {'names': [(re.compile(p, re.I), r) for p, r in names],
              'forbidden': [re.compile(p, re.I) for p in P.get('forbidden', []) + SX.FORBIDDEN],
              'lab_slug': P.get('lab_report_slug_prefix') or '\x00',
              'mirror': _mirror()}
    return _P


def _url(url, removed):
    """one link as the page may show it"""
    P = _table()
    if re.search(r'spacesheep\.(?:dev|app)', url):
        if '/sessions' in url:
            removed.append('a session page')
            return '[removed: a link to a session page]'
        sl = re.search(r'spacesheep\.dev/@yaroslavvb/([\w.-]+)', url)
        if sl and sl.group(1).startswith(P['lab_slug']):
            removed.append('the report for the lab lead')
            return '[the report for the lab lead]'
        if sl and sl.group(1) in P['mirror']:
            base, _, frag = url.partition('#')
            if frag and (ACCESS.search(frag) or any(rx.search(frag) for rx in P['forbidden'])):
                return base   # an anchor that names access is dropped, the page link kept
            return url
        removed.append('a private page')
        return '[removed: a link to a page that is not public]'
    if re.search(r'claude\.ai/code/session|/sessions?/|login\.|auth|token|key=', url, re.I) or ACCESS.search(url) \
            or any(rx.search(url) for rx in P['forbidden']):
        removed.append('a private link')
        return '[removed: a private link]'
    if re.match(r'https?://github\.com/yaroslavvb/(?!et-soc1-prototyping\b)', url):
        removed.append('a private link')
        return '[removed: a private link]'
    return url


def redact(text):
    """(the prompt as the page shows it, [what was removed])"""
    if not text:
        return text, []
    removed, P, keep = [], _table(), []
    s = text.replace('\r\n', '\n')

    def stash(x):   # a kept span, out of the sentence rule's sight until the end
        keep.append(x)
        return f'\x00{len(keep) - 1}\x00'
    # links first: each judged whole, so a sentence rule never sees a URL's parts
    s = re.sub(r'(?:https?://|www\.)[^\s<>()\[\]"\'`]+', lambda m: stash(_url(m.group(0).rstrip('.,;:'), removed)) +
               m.group(0)[len(m.group(0).rstrip('.,;:')):], s)
    s = re.sub(r'[\w.+-]+@[\w-]+\.[\w.-]*[a-z]', lambda m: (removed.append('an e-mail address'), stash('[removed: an e-mail address]'))[1], s)
    s = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', lambda m: (removed.append('an address'), stash('[removed: an address]'))[1], s)
    s = re.sub(r'(?<![\w.])(?:/(?:home|root|tmp|etc|usr|var|opt|run|Users)/|~/git\w*/)[\w./@~+-]*',
               lambda m: (removed.append('a path'), stash('[removed: a path]'))[1], s)
    s = re.sub(r'--space[ =]"?(' + UUID + ')', lambda m: m.group(0) if m.group(1) in P['mirror'].values() else
               (removed.append('a private page'), stash('--space [removed: a page id]'))[1], s)
    s = re.sub(r'\bbypass[- ]?per\w*', lambda m: (removed.append('a permission setting'), stash('[removed: a permission setting]'))[1], s, flags=re.I)
    for rx, rep in P['names']:
        if rx.search(s):
            removed.append('a name or place')
            s = rx.sub(lambda m, rep=rep: stash(rep) if rep.startswith('[') else rep, s)
    # every character of the text belongs to exactly one sentence: a run up to . ! or ? before a space, a line end, or
    # the text's end; a sentence that names machine access (or a forbidden pattern) is removed whole
    parts = re.findall(r'[^\n]*?(?:[.!?]+(?=\s)|\n|$)', s)
    assert ''.join(parts) == s, 'sentence split lost text'
    out = []
    for x in parts:
        if x and (ACCESS.search(x) or any(rx.search(x) for rx in P['forbidden'])):
            removed.append('a sentence about machine access')
            lead = re.match(r'[ \t]*', x).group(0) or (' ' if out and out[-1] and not out[-1][-1].isspace() else '')
            out.append(lead + '[removed: a sentence about machine access]' + ('\n' if x.endswith('\n') else ''))
        else:
            out.append(x)
    s = ''.join(out)
    s = re.sub(r'(?:\[removed: a sentence about machine access\][ \t]*){2,}', '[removed: sentences about machine access] ', s)
    s = re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], s)
    return s.strip(), removed
