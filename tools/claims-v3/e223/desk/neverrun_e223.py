#!/usr/bin/env python3
"""E223 (reg-e223, Q239) desk: which of E223's arms repeat a configuration already committed on the card its schedules put it on - LABELS
ONLY, nothing dropped (E223's arms are the model session's, registered by its post; the lab only labels them). E221's never-run labels
(tools/claims-v3/e221/desk/neverrun_e221.py, itself E219's, E217's, E214's and E213's scan in form), with this sweep's names and three
cards (aifoundry1 card 1, card 0 and aifoundry2 card 0), and three changes: (a) E223's own folders are NOT READ at all (W/out/data-e223,
decl-e223, verify-e223d, fix-e223d, blind-e223, any card-e223 lane, this lane's own folder, any committed '-e223-' data folder: no lane
opens an E223 datum before the lab's freeze); (b) as E221's, a tile path a committed run names that resolves neither against the lab's
top nor against its experiment's proposal/ copy is resolved by that experiment's registered lists (now also an arm's box list,
box/SRC-SHA256SUMS-e<N>a or -e<N>b, as E220's and E224's aifoundry2 arms name theirs); and (c) THE LABELS ARE READ IN E220's
DATED NOTE 1 FORM (the orchestrator's ruling of Fri 20 Nov 2026 10:5x PST, tools/claims-v3/e220/KIT.md F1): a configuration or a shape
counts as run on a card only by a SESSION RECORD ON THAT CARD - a committed run record (the configuration index below) or a session's own
file in a folder naming the card (a committed data file, or a session file of a lane folder, never under a /dry/ folder); a folder naming
no card (desk copies in card-less lane folders, registrations, plans) never counts. E221's NEVER-BY-INDEX reading (any counted token hit,
card-less folders included) is REPORTED beside as the literal reading, never a label. To decide that exactly from the scan, each token's
hits a folder class now also count the session-record files among them (n_rec, with up to eight listed). Reads files only; writes only
its outputs.

    python3 -I -B neverrun_e223.py scan --lab <the lab at GitHub main> --lanes <W/out> --out <dir>
        THE SHAPE-LEVEL SCAN, E213's: every file under the lab's committed data folders (docs/reports/data), the committed schedules and
        arms of the model session's earlier sweeps (E208, E212, E214, E217, E219, E221), and the round's card and data lane folders under
        W/out (names starting card-, data-, a1, a2, a3), gzip read through; a token matched whole (no letter, digit or underscore on either
        side): gemmL<MB>x<NB>x<KB> (also gemmLn, gemmLnc), gemm<B>, gemmc<B>, gemmh<B>, gemmv<B>, gemmnc<B> (each with r<R> and s), mm<N>,
        mmp<N> and tenb; each hit classed by the folder it sits in (E213's folder_card rule, with the round's later card lanes named):
        COUNTED for a card (a folder naming that card, naming no card, or naming aifoundry1 without a card), OTHER CARD, SUBTRACTED (the
        lane card-e213b, E213 arm B's first card lane, stopped at its step 4 before any card command, whose files hold planned points
        only, as E214's-E221's scans read it); E223's own folders (above) are not read. Writes <dir>/scan-e223.json.
    python3 -I -B neverrun_e223.py configs --lab <the lab at GitHub main> --out <dir>
        THE CONFIGURATION INDEX of committed runs, by card: (1) every committed session folder under docs/reports/data that holds run
        records (runs/*/run.json, with or without a session/ level: E190 to E224's kits, E221's nine sessions among them), every device
        process of every run that ran, by its own argv (the host's --values token, --type, --shires; the kernel rgm211 when the host's
        path names it, else rgm136), its tile resolved by bytes (the path read against the lab's top, then against that experiment's
        registered kit tools/claims-v3/e<N>/proposal/, then by that experiment's registered lists (above); a pool of several files by
        each file's bytes); the card by the folder's name (a folder that names no card holds no card run: listed, never a label);
        (2) MM1-v3.1's vendored measured time points (its data loader, tools/matmul/mm1/v3.1/data_v31.py: E105 to E213 as committed
        when MM1-v3.1 landed; one record a card and case; MM1-v3.2's added points, E214's and E215's, are committed session folders
        read in (1)). Writes <dir>/configs-e223.json. Needs numpy (MM1-v3.1's loader): run single-threaded inside the round's CPU slot.
    python3 -I -B neverrun_e223.py report --scan <scan-e223.json> --configs <configs-e223.json> --src <E223's src/> --out <dir>
        writes <dir>/neverrun-e223.json and <dir>/neverrun-e223.txt: per arm and per card its sessions put it on, the label.

THE CONFIGURATION of an arm is (kernel rgm136, the host's arm token, the format, the data, the shire mask): the data is 'random' (the host's
randn generator over the lab's random tile), 'zeros' or 'ones' (the lab's kinds tiles, by bytes), 'sparse50' (the host's drawn pool over the
lab's sparse50 tile, by bytes), 'tile:<sha256>' for any other tile; tenb's 'rnd' arm holds the lab's random file (gen tiles) and is
'held:<sha256 of the lab's random tile>' (the held pair), never equal to the drawn 'random'. MM1-v3.1's records name kinds, read as random,
zeros, ones, sparse50, or 'kind:<its name>'. The process arguments the kits fix (--per-shire 32 --seconds 6 --budget 7.5 --seed 1) are
equal across E190 to E223, so they are not part of the key; the smoke's 2 s processes (session/smoke/) are not runs.
THE LABELS (per arm and card; nothing is dropped, every arm keeps its place in its schedule), in E220's note-1 form (session records only):
  REPEAT          its configuration has a committed run on that card (the experiments and sessions are named);
  SHAPE-ONLY      its token (shape) has a committed run on that card in another configuration (format, data or mask), none in its own;
  IN-RECORD       no committed run of its token on that card in the index, but the scan finds its token in a session record on that card
                  (a committed data file, or a lane folder's session file outside /dry/, in a folder naming the card; for aifoundry1's
                  cards also a folder naming aifoundry1 but no card: the conservative side): the files are listed;
  NEVER           no session record of its token on that card, in the index or in the scan;
  and, REPORTED beside: the literal reading (E221's NEVER-BY-INDEX: the scan's COUNTED hits for that card, card-less folders included,
  with up to six files); the configuration's committed runs on other cards; whether the arm's shire mask has any committed run on that
  card (any token, format or data); the same host family's committed runs on that card (block, stream and TenB arms only).
Not read: the model session's uncommitted folders (the orchestrator's rule of 23:18:35 PST Mon 16 Nov 2026); aifoundry1's own disk.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
import re
import sys

A3 = 'aifoundry3 card 0'
A2 = 'aifoundry2 card 0'
C1 = 'aifoundry1 card 1'
C0 = 'aifoundry1 card 0'
A1U = 'aifoundry1 (card not named)'
NONE = 'no card named'
SESS_CARD = {'a1c1': C1, 'a1c0': C0, 'a2c0': A2, 'a3c0': A3}
TOKEN = r'(?:gemmL(?:n|nc)?\d+x\d+x\d+|gemm(?:nc|c|v|h)?\d+(?:r\d+)?s?|mmp?\d+|tenb)'
RX = re.compile(r'(?<![A-Za-z0-9_])(' + TOKEN + r')(?![A-Za-z0-9_])')
SKIP_EXT = ('.bin', '.npz', '.npy', '.png', '.pdf', '.elf', '.o', '.a', '.so', '.zip', '.xz', '.zst', '.gguf')
MAX_BYTES = 400_000_000
KINDS_TILES = 'tools/claims-v3/kinds/tiles'


def now():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')


def sha(p):
    with open(p, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def family(tok):
    m = re.match(r'(gemmL(?:nc|n)?|gemmnc|gemmc|gemmv|gemmh|gemm|mmp|mm|tenb)', tok or '')
    return m.group(1) if m else None


# ---------------------------------------------------------------- the shape-level scan (E213's form)
def folder_card(path, expmap):
    q = '/' + path
    for keys, c in ((('aifoundry3', '/a3-', 'card-a3-', '-a3-'), A3),
                    (('aifoundry1-c1', '/a1c1-', 'card-a1c1-', 'a1c1', '-card1'), C1),
                    (('aifoundry1-card0', '/a1c0-', 'card-a1c0-', 'a1c0', '-card0'), C0),
                    (('aifoundry2', '/a2-', 'card-a2-', 'a2c0'), A2),
                    (('aifoundry1', '/a1-', 'card-a1-'), A1U)):
        if any(k in q for k in keys):
            return c
    e = re.search(r'card-e(\d{2,3})', q)
    if e:
        return expmap.get(e.group(1))
    return None


def exp_cards(lab):
    m = {}
    for d in sorted(os.listdir(os.path.join(lab, 'docs', 'reports', 'data'))):
        e = re.search(r'-e(\d{2,3})-', d)
        c = folder_card(d, {})
        if e and c:
            m.setdefault(e.group(1), c)
    m.update({'206': None})
    return m


def subtracted(rel):
    # the lane card-e213b, E213 arm B's first card lane, which stopped at its step 4 before any card command (Wed 18 Nov 2026
    # 06:39:56 PST): its files hold arm B's planned points, never a run (E214's, E217's and E219's scans subtracted it too)
    return rel.startswith('W/out/card-e213b/')


def e223_own(name):
    # E223's own folders are never read (no lane opens an E223 datum before the lab's freeze: the round's rule)
    return (('-e223-' in name) or ('-e223' == name[-5:]) or ('mmsweep7' in name) or
            name.startswith(('data-e223', 'decl-e223', 'verify-e223d', 'fix-e223d', 'card-e223', 'blind-e223', 'reg-e223',
                             'verify-reg-e223', 'land-reg-e223', 'verify-blind-e223', 'land-blind-e223')))


SESSION_FILE = re.compile(r'/(session|sessions|runs|smoke)/|(^|/)(proc[-0-9]*\.(out|err)|run\.json|smoke\.json|queue\.json|session\.log)$')


def session_record(rel):
    # E220's dated note 1: a committed data file, or a session's own file in a lane folder (never under a /dry/ folder)
    return rel.startswith('docs/reports/data/') or (bool(SESSION_FILE.search(rel)) and '/dry/' not in rel)


def lane_card(rel):
    for pre, c in (('W/out/card-e206a/', A3), ('W/out/card-e206b', C1), ('W/out/card-e213a/', A3), ('W/out/card-e213b', C1),
                   ('W/out/card-e215a', A3), ('W/out/card-e215b', C1), ('W/out/card-e216', A2), ('W/out/card-e218', A3),
                   ('W/out/card-e220a', C1), ('W/out/card-e220b', A2), ('W/out/card-e222', A3), ('W/out/card-e224a', C1),
                   ('W/out/card-e224b', A2)):
        if rel.startswith(pre):
            return c
    return None


def read_text(p):
    if p.endswith('.gz'):
        with gzip.open(p, 'rb') as fh:
            return fh.read().decode('utf-8', 'ignore')
    with open(p, 'rb') as fh:
        return fh.read().decode('utf-8', 'ignore')


def scan(lab, lanes, out):
    t0 = now()
    expmap = exp_cards(lab)
    roots = [os.path.join(lab, 'docs', 'reports', 'data')]
    for e in ('e208', 'e212', 'e214', 'e217', 'e219', 'e221'):
        roots += [os.path.join(lab, 'tools', 'claims-v3', e, 'proposal', 'src', 'sched'),
                  os.path.join(lab, 'tools', 'claims-v3', e, 'proposal', 'src', 'arms.json')]
    roots = [r for r in roots if os.path.exists(r)]
    lane_roots = sorted(os.path.join(lanes, d) for d in os.listdir(lanes) if d.startswith(('card-', 'data-', 'a1', 'a2', 'a3'))
                        and not e223_own(d))
    not_read = sorted(['W/out/' + d for d in os.listdir(lanes) if e223_own(d)] +
                      [os.path.join('docs', 'reports', 'data', d) for d in os.listdir(os.path.join(lab, 'docs', 'reports', 'data'))
                       if e223_own(d)])
    lane_files = [r for r in lane_roots if not os.path.isdir(r)]
    hits = {}
    nfiles, skipped_big, unreadable, git_dirs = 0, [], 0, 0

    def walk(top):
        if os.path.isfile(top):
            yield os.path.dirname(top), [], [os.path.basename(top)]
            return
        for dp, dn, fns in os.walk(top):
            yield dp, dn, fns

    for top in roots + lane_roots:
        for dp, dn, fns in walk(top):
            if '.git' in dn or '.git' in fns:
                dn[:] = []
                git_dirs += 1
                continue
            dn[:] = sorted(d for d in dn if not e223_own(d))
            for fn in sorted(fns):
                p = os.path.join(dp, fn)
                if fn.endswith(SKIP_EXT) or os.path.islink(p):
                    continue
                try:
                    if os.path.getsize(p) > MAX_BYTES:
                        skipped_big.append(p)
                        continue
                    txt = read_text(p)
                except (OSError, EOFError):
                    unreadable += 1
                    continue
                nfiles += 1
                found = set(RX.findall(txt))
                if not found:
                    continue
                rel = os.path.relpath(p, lab) if p.startswith(lab + os.sep) else 'W/out/' + os.path.relpath(p, lanes)
                if subtracted(rel):
                    c = 'SUBTRACTED'
                else:
                    c = lane_card(rel) or folder_card(rel, expmap) or NONE
                for t in found:
                    hits.setdefault(t, {}).setdefault(c, []).append(rel)
    rec = {'what': "E223's shape-level scan (arm tokens of rgm136's host grammar, by card; E213's form, as E214's-E221's; with each "
                   "class's session-record files counted for E220's note-1 reading)",
           'not_read_e223_own': not_read,
           'started': t0, 'ended': now(), 'token_pattern': RX.pattern,
           'files_read': nfiles, 'roots': [os.path.relpath(r, lab) for r in roots],
           'lane_roots': ['W/out/' + os.path.basename(r) for r in lane_roots],
           'lane_roots_that_are_files_read_as_files': ['W/out/' + os.path.basename(r) for r in lane_files],
           'over_400MB_not_read': [os.path.relpath(p, lanes) if p.startswith(lanes) else os.path.relpath(p, lab) for p in skipped_big],
           'unreadable': unreadable, 'git_dirs_not_read': git_dirs,
           'tokens': {t: {c: {'n': len(v), 'files': sorted(set(v))[:8], 'n_rec': len({x for x in v if session_record(x)}),
                              'rec_files': sorted({x for x in v if session_record(x)})[:8]}
                          for c, v in sorted(cs.items())} for t, cs in sorted(hits.items())}}
    os.makedirs(out, exist_ok=True)
    json.dump(rec, open(os.path.join(out, 'scan-e223.json'), 'w'), indent=1, sort_keys=True)
    print(f"not read (E223's own): {', '.join(not_read) or 'none'}")
    print(f"scan: {nfiles} files read, {len(hits)} distinct tokens, {len(roots)} lab roots, {len(lane_roots)} lane roots "
          f"({len(lane_files)} of them files), {len(skipped_big)} over 400 MB not read, {unreadable} unreadable, {git_dirs} scratch clones "
          f"not read; {t0} - {rec['ended']}")


# ---------------------------------------------------------------- the configuration index
class Kinds:
    """the lab's kinds tiles by sha256 -> data key"""

    def __init__(self, lab):
        self.map = {}
        for t, names in (('fp32', ('randn', 'zeros', 'ones', 'sparse50')), ('fp16', ('randn', 'zeros', 'ones', 'sparse50')),
                         ('int8', ('full', 'zeros', 'ones', 'sparse50'))):
            for n in names:
                p = os.path.join(lab, KINDS_TILES, t, n + '.bin')
                if os.path.exists(p):
                    self.map[sha(p)] = {'randn': 'random', 'full': 'random'}.get(n, n)

    def data_key(self, gen, tile_sha):
        lab = self.map.get(tile_sha)
        if gen == 'randn':
            return 'random' if lab == 'random' else f'randn-over:{tile_sha}'
        if gen == 'sparse50':
            return 'sparse50' if lab == 'sparse50' else f'sparse50-over:{tile_sha}'
        if gen == 'tiles':
            if lab in ('zeros', 'ones'):
                return lab
            if lab == 'random':
                return f'held:{tile_sha}'
            return f'tile:{tile_sha}'
        return f'gen-{gen}:{tile_sha}'


def parse_values(v):
    parts = (v or '').split(':')
    return parts[0], (parts[1] if len(parts) > 1 else ''), (parts[2] if len(parts) > 2 else '')


def argval(argv, k):
    return argv[argv.index(k) + 1] if k in argv else None


def registered_lists(lab, e):
    """{path: sha256} from experiment e<N>'s registered lists (box/SRC-SHA256SUMS-e<N>, and, new here, box/SRC-SHA256SUMS-e<N>a and
    -e<N>b, an arm's box list, as E220's and E224's aifoundry2 arms name theirs; proposal/src/SRC-SHA256SUMS with src/ prefixed as the
    kit names it, points-e<N>.json's tiles_sha256); empty if none."""
    m = {}
    base = os.path.join(lab, 'tools', 'claims-v3', 'e' + e)
    for p, pre in ((os.path.join(base, 'box', 'SRC-SHA256SUMS-e' + e), ''), (os.path.join(base, 'box', 'SRC-SHA256SUMS-e' + e + 'a'), ''),
                   (os.path.join(base, 'box', 'SRC-SHA256SUMS-e' + e + 'b'), ''),
                   (os.path.join(base, 'proposal', 'src', 'SRC-SHA256SUMS'), '')):
        if os.path.exists(p):
            for ln in open(p):
                f = ln.split()
                if len(f) == 2 and re.fullmatch(r'[0-9a-f]{64}', f[0]):
                    m.setdefault(pre + f[1].lstrip('./'), f[0])
    pj = os.path.join(base, 'points-e' + e + '.json')
    if os.path.exists(pj):
        try:
            for k, v in (json.load(open(pj)).get('tiles_sha256') or {}).items():
                m.setdefault(k, v)
        except (ValueError, AttributeError):
            pass
    return m


def configs(lab, out):
    t0 = now()
    K = Kinds(lab)
    recs = []
    cache = {}
    reg_cache = {}
    n_by_list, n_missing = 0, 0
    ddir = os.path.join(lab, 'docs', 'reports', 'data')
    expmap = exp_cards(lab)
    n_runs_files = 0
    sessions = []
    # (1) every committed session folder with run records, every device process by its own argv
    for d in sorted(os.listdir(ddir)):
        top = os.path.join(ddir, d)
        if not os.path.isdir(top) or e223_own(d):
            continue
        em = re.search(r'-e(\d{2,3})-', d)
        for dp, dn, fns in os.walk(top):
            dn.sort()
            if os.path.basename(dp) != 'runs':
                continue
            rel_sess = os.path.relpath(os.path.dirname(dp), ddir)
            card = folder_card(rel_sess, expmap)
            if card in (None, A1U):
                card = card or NONE
            exp = 'E' + em.group(1) if em else d
            sm = re.search(r'-(a\dc\d)-(S\d+r?)', d)
            sess = f'{sm.group(1)}-{sm.group(2)}' if sm else ('arm B' if card == C1 and exp in ('E190', 'E206', 'E213', 'E215') else
                                                               'arm A' if card == C1 and exp in ('E220', 'E224') else
                                                               'arm B' if card == A2 and exp in ('E220', 'E224')
                                                               else os.path.basename(os.path.dirname(dp)))
            nrec = 0
            for rn in sorted(dn):
                rj = os.path.join(dp, rn, 'run.json')
                if not os.path.exists(rj):
                    continue
                n_runs_files += 1
                try:
                    R = json.load(open(rj))
                except ValueError:
                    recs.append({'source': f'docs/reports/data/{rel_sess}/runs/{rn}: unreadable', 'error': True})
                    continue
                if R.get('ran') is False:
                    continue
                for pr in R.get('procs') or []:
                    argv = pr.get('argv') or []
                    v = argval(argv, '--values')
                    if not v:
                        continue
                    tok, gen, f = parse_values(v)
                    host = argv[0] if argv else ''
                    kernel = 'rgm211' if 'rgm211' in host or 'rgm211' in (argval(argv, '--kernel') or '') else 'rgm136'
                    shas = []
                    for one in (f.split(',') if f else []):    # a pool of several files (gen tiles): each by its bytes
                        cands = [os.path.join(lab, one)]
                        if em:
                            cands.append(os.path.join(lab, 'tools', 'claims-v3', 'e' + em.group(1), 'proposal', one))
                        for cpath in cands:
                            if os.path.exists(cpath):
                                if cpath not in cache:
                                    cache[cpath] = sha(cpath)
                                shas.append(cache[cpath])
                                break
                        else:
                            if em and em.group(1) not in reg_cache:
                                reg_cache[em.group(1)] = registered_lists(lab, em.group(1))
                            rs = reg_cache.get(em.group(1), {}).get(one) if em else None
                            if rs:
                                shas.append(rs)
                                n_by_list += 1
                            else:
                                shas.append('MISSING:' + one)
                                n_missing += 1
                    tsha = ','.join(shas)
                    recs.append({'exp': exp, 'source': f'docs/reports/data/{rel_sess}/runs/{rn}', 'session': sess, 'card': card,
                                 'kernel': kernel, 'token': tok, 'family': family(tok), 'fmt': argval(argv, '--type'),
                                 'data': K.data_key(gen, tsha), 'mask': argval(argv, '--shires'), 'arm_id': R.get('arm', ''),
                                 'rc': pr.get('rc'), 'status': 'RAN (committed)'})
                    nrec += 1
            sessions.append({'folder': rel_sess, 'exp': exp, 'card': card, 'session': sess, 'process_records': nrec})
    n_direct = len(recs)
    # (2) MM1-v3.1's vendored measured time points
    v31 = os.path.join(lab, 'tools', 'matmul', 'mm1', 'v3.1')
    n_v31 = 0
    if os.path.isdir(v31):
        sys.path.insert(0, v31)
        try:
            import data_v31 as D31  # noqa: E402
            for p in D31.time_points():
                k = p['kind']
                data = {'random': 'random', 'zeros': 'zeros', 'ones': 'ones', 'sparse50': 'sparse50'}.get(k, f'kind:{k}')
                recs.append({'exp': p['exp'], 'source': f"MM1-v3.1 vendored point {p['id']}", 'session': '', 'card': p['card'],
                             'kernel': p['kernel'], 'token': p['arm'], 'family': family(p['arm']), 'fmt': p['fmt'], 'data': data,
                             'mask': p['mask'], 'arm_id': '', 'rc': None, 'status': 'RAN (committed; MM1-v3.1 vendored)'})
                n_v31 += 1
        finally:
            sys.path.pop(0)
    rec = {'what': "E223's configuration index of committed runs (every committed session's run records by argv, and MM1-v3.1's points)",
           'started': t0, 'ended': now(), 'n_run_files': n_runs_files, 'n_direct_process_records': n_direct,
           'n_tile_paths_resolved_by_registered_list': n_by_list, 'n_tile_paths_missing': n_missing,
           'n_mm1v31_points': n_v31, 'sessions': sessions, 'kinds_tiles': K.map, 'records': recs}
    os.makedirs(out, exist_ok=True)
    json.dump(rec, open(os.path.join(out, 'configs-e223.json'), 'w'), indent=1, sort_keys=True)
    print(f'configs: {n_runs_files} run files in {len(sessions)} committed session folders, {n_direct} process records, '
          f'{n_v31} MM1-v3.1 points; tile paths resolved by a registered list {n_by_list}, missing {n_missing}; '
          f'{t0} - {rec["ended"]}')


# ---------------------------------------------------------------- the report
def counted_for(card, c):
    if c == card or c == NONE:
        return True
    if card in (C1, C0) and c == A1U:
        return True
    return False


def report(scan_path, configs_path, src, out):
    S = json.load(open(scan_path))
    CF = json.load(open(configs_path))
    T = S['tokens']
    K = Kinds.__new__(Kinds)
    K.map = CF['kinds_tiles']
    arms = json.load(open(os.path.join(src, 'arms.json')))
    kit_root = os.path.dirname(os.path.abspath(src))
    on = {}
    for fn in sorted(os.listdir(os.path.join(src, 'sched'))):
        s = json.load(open(os.path.join(src, 'sched', fn)))
        ck = s.get('card') or fn.split('-')[0]
        card = SESS_CARD.get(ck, ck)
        for r in s['runs']:
            if r['role'] in ('arm', 'time', 'anchor'):
                on.setdefault(r['arm'], {}).setdefault(card, set()).add(s.get('session', fn))
    recs = [r for r in CF['records'] if not r.get('error')]
    by_key, by_tok, by_fam, masks_ran = {}, {}, {}, {}
    for r in recs:
        by_key.setdefault((r['kernel'], r['token'], r['fmt'], r['data'], r['mask']), []).append(r)
        by_tok.setdefault((r['kernel'], r['token']), []).append(r)
        by_fam.setdefault((r['kernel'], r['family']), []).append(r)
        masks_ran.setdefault(r['card'], set()).add(r['mask'])
    rows, lines = [], []
    tally, mtally, ltally = {}, {}, {}
    cache = {}
    for a in arms['arms']:
        tok, gen, f = parse_values(a['values'])
        p = os.path.join(kit_root, f)
        if p not in cache:
            cache[p] = sha(p) if os.path.exists(p) else 'MISSING:' + f
        data = K.data_key(gen, cache[p])
        fam = family(tok)
        same = by_key.get(('rgm136', tok, a['type'], data, a['shires']), [])
        shp = by_tok.get(('rgm136', tok), [])
        fm = by_fam.get(('rgm136', fam), [])
        for card, sess in sorted(on.get(a['id'], {}).items()):
            ran_here = sorted({f"{r['exp']} {r['session']}".strip() for r in same if r['card'] == card})
            shape_here = sorted({r['exp'] for r in shp if r['card'] == card})
            other = sorted({f"{r['exp']} on {r['card']}" for r in same if r['card'] != card})
            fam_here = sorted({f"{r['token']} {r['fmt']} {r['data'] if not r['data'].startswith(('tile:', 'held:')) else r['data'][:9]}"
                               f" ({r['exp']})" for r in fm if r['card'] == card}) if fam != 'gemmL' else []
            mask_seen = a['shires'] in masks_ran.get(card, set())
            cs = T.get(tok, {})
            tok_here = {c: v['n'] for c, v in cs.items() if c != 'SUBTRACTED' and counted_for(card, c)}
            tok_files = sorted({x for c, v in cs.items() if c != 'SUBTRACTED' and counted_for(card, c) for x in v['files']})[:6]
            ok_cls = {card} | ({A1U} if card in (C1, C0) else set())
            rec_here = {c: v.get('n_rec', 0) for c, v in cs.items() if c in ok_cls and v.get('n_rec')}
            rec_files = sorted({x for c, v in cs.items() if c in ok_cls for x in v.get('rec_files', [])})[:6]
            if ran_here:
                label = 'REPEAT'
            elif shape_here:
                label = 'SHAPE-ONLY'
            elif rec_here:
                label = 'IN-RECORD'
            else:
                label = 'NEVER'
            literal = 'REPEAT' if ran_here else 'SHAPE-ONLY' if shape_here else 'NEVER-BY-INDEX' if tok_here else 'NEVER'
            tally[(card, label)] = tally.get((card, label), 0) + 1
            ltally[(card, literal)] = ltally.get((card, literal), 0) + 1
            mk = 'mask run before on the card' if mask_seen else 'mask new on the card'
            mtally[(card, mk)] = mtally.get((card, mk), 0) + 1
            rows.append({'arm': a['id'], 'card': card, 'sessions': sorted(sess), 'token': tok, 'family': fam, 'fmt': a['type'],
                         'data': data, 'mask': a['shires'], 'families': a['families'], 'label': label,
                         'config_committed_on_card': ran_here, 'token_committed_on_card': shape_here,
                         'config_committed_other_cards': other, 'family_committed_on_card': fam_here[:12],
                         'mask_committed_on_card': mask_seen, 'scan_session_record_hits_on_card': rec_here,
                         'scan_session_record_files_sample': rec_files, 'literal_reading_REPORTED': literal,
                         'e213_scan_counted_hits': tok_here, 'e213_scan_counted_files_sample': tok_files,
                         'e213_scan_never_run': not tok_here})
            lines.append(f"{label:10s} {card:18s} {a['id']:28s} {','.join(sorted(sess)):6s} config={ran_here} token={shape_here} "
                         f"mask={'seen' if mask_seen else 'new'} records={rec_here or 'none'} literal={literal} "
                         f"e213-scan={'never' if not tok_here else tok_here} other={other}"
                         + (f" family-on-card={len(fam_here)}" if fam != 'gemmL' else ''))
    res = {'what': "E223's never-run labels per arm and card (desk/neverrun_e223.py report) in E220's dated note 1 form (session records "
                   "only); labels only, nothing dropped; E221's literal reading REPORTED beside",
           'scan_sha256': sha(scan_path), 'configs_sha256': sha(configs_path), 'arms_sha256': sha(os.path.join(src, 'arms.json')),
           'scan_window': [S['started'], S['ended']], 'files_read': S['files_read'], 'rows': rows,
           'tally': {f'{c} {l}': n for (c, l), n in sorted(tally.items())},
           'mask_tally': {f'{c} {l}': n for (c, l), n in sorted(mtally.items())},
           'literal_tally_REPORTED': {f'{c} {l}': n for (c, l), n in sorted(ltally.items())},
           'masks_committed_by_card': {c: sorted(v) for c, v in sorted(masks_ran.items())}}
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, 'neverrun-e223.json'), 'w'), indent=1, sort_keys=True)
    head = [f"E223 never-run labels (E220's note-1 form: session records only); scan {res['scan_sha256'][:16]} ({S['files_read']} files, "
            f"{S['started']} - {S['ended']}); configs {res['configs_sha256'][:16]}; arms {res['arms_sha256'][:16]}",
            'tally (arm x card): ' + '; '.join(f'{k} {v}' for k, v in res['tally'].items()),
            'masks (arm x card): ' + '; '.join(f'{k} {v}' for k, v in res['mask_tally'].items()),
            "the literal reading (E221's form, REPORTED, not a label): " + '; '.join(f'{k} {v}' for k, v in res['literal_tally_REPORTED'].items())]
    open(os.path.join(out, 'neverrun-e223.txt'), 'w').write('\n'.join(head + lines) + '\n')
    print('\n'.join(head))


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    a1 = sp.add_parser('scan')
    a1.add_argument('--lab', required=True)
    a1.add_argument('--lanes', required=True)
    a1.add_argument('--out', required=True)
    a2 = sp.add_parser('configs')
    a2.add_argument('--lab', required=True)
    a2.add_argument('--out', required=True)
    a3 = sp.add_parser('report')
    a3.add_argument('--scan', required=True)
    a3.add_argument('--configs', required=True)
    a3.add_argument('--src', required=True)
    a3.add_argument('--out', required=True)
    a = ap.parse_args()
    if a.cmd == 'scan':
        scan(os.path.abspath(a.lab), os.path.abspath(a.lanes), a.out)
    elif a.cmd == 'configs':
        configs(os.path.abspath(a.lab), a.out)
    else:
        report(a.scan, a.configs, a.src, a.out)


if __name__ == '__main__':
    main()
