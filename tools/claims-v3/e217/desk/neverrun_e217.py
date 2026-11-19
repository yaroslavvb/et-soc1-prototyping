#!/usr/bin/env python3
"""E217 (reg-e217, Q228) desk: which of E217's arms repeat a configuration already committed on the card its schedules put it on - LABELS ONLY,
nothing dropped (E217's arms are the model session's, registered by its post; the lab only labels them). E214's never-run labels
(tools/claims-v3/e214/desk/neverrun_e214.py, itself E213's scan in form) with this sweep's names, E214's seven committed sessions read run by
run, MM1-v3.1's vendored points in place of MM1-v3's, E215's registered points in place of E213 arm B's, and each arm's shire mask read
against the masks already run on its card. Reads files only; writes only its outputs.

    python3 -I -B neverrun_e217.py scan --lab <the lab at GitHub main> --lanes <W/out> --out <dir>
        THE SHAPE-LEVEL SCAN, E213's: every file under the lab's committed data folders (docs/reports/data), E214's, E212's and E208's
        committed schedules and arms, and the round's card and data lane folders under W/out (names starting card-, data-, a1, a2, a3),
        gzip read through; a token gemmL<MB>x<NB>x<KB> (also gemmLn/gemmLnc) matched whole; each hit classed by the folder it sits in
        (E213's folder_card rule): COUNTED for a card (a folder naming that card, naming no card, or naming aifoundry1 without a card),
        OTHER CARD, SUBTRACTED (E217's own folders: a data folder holding '-e217-', the lanes data-e217, verify-e217d, fix-e217d; the lane
        card-e213b, E213 arm B's first card lane, stopped at its step 4 before any card command, whose files hold planned points only, as
        E214's scan read it; and E215's card lanes card-e215a and card-e215b, which at this scan had made no card command (both waiting at
        their queue step behind the orchestrator's hold), so their files hold E215's planned points only: E215 enters the index below as
        PLANNED). Writes <dir>/scan-e217.json.
    python3 -I -B neverrun_e217.py configs --lab <the lab at GitHub main> --out <dir>
        THE CONFIGURATION INDEX of committed runs, by card: (1) every run record ('ran' true; roles arm, time, anchor) of every committed
        session of the model session's sweeps E208, E212 and E214 (docs/reports/data/*-e208-mmsweep-*, *-e212-mmsweep2-*,
        *-e214-mmsweep3-*: data-*.json), its 'values' and 'shires' resolved against that sweep's registered tiles; (2) MM1-v3.1's vendored
        measured time points (its data loader, tools/matmul/mm1/v3.1/data_v31.py: E105-E213 as committed when MM1-v3.1 landed, E213's both
        arms among them; one record a card and case); (3) E215's registered points and references (tools/claims-v3/e215/points-e215.json):
        arm A for aifoundry3 card 0 and arm B for aifoundry1 card 1, NOT RUN at the time of this index (both arms held before their first
        card command; arm B is planned to run on card 1 before E217's first session): PLANNED, REPORTED. Writes <dir>/configs-e217.json.
        Needs numpy (MM1-v3.1's loader): run single-threaded inside the round's CPU slot.
    python3 -I -B neverrun_e217.py report --scan <scan-e217.json> --configs <configs-e217.json> --src <E217's src/> --out <dir>
        writes <dir>/neverrun-e217.json and <dir>/neverrun-e217.txt: per arm and per card its sessions put it on, the label.

THE CONFIGURATION of an arm is (kernel rgm136, the shape token, the format, the data, the shire mask): the data is 'random' (the host's randn
generator over the lab's random tile), 'zeros' or 'ones' (the lab's kinds tiles, by bytes), 'sparse50' (the host's drawn pool over the lab's
sparse50 tile, by bytes) or 'tile:<sha256 of the 2,048-byte file>' for any other tile; MM1-v3.1's records name kinds, read as random, zeros,
ones, sparse50, or 'kind:<its name>' (never equal to a tile key: conservative toward 'not a repeat' only for pattern tiles, which the
direct E212 and E214 reads cover byte for byte). The process arguments the kit fixes (--per-shire 32 --seconds 6 --budget 7.5 --seed 1)
are equal across E208, E212, E214 and E217 by their registered mms_common.host_argv, so they are not part of the key; the smoke's 2 s
processes are not runs.
THE LABELS (per arm and card; nothing is dropped, every arm keeps its place in its schedule). The label is read from THE CONFIGURATION
INDEX (committed runs only); E213's shape-level token scan is reported beside it as the strictest reading:
  REPEAT          its configuration has a committed run on that card (the experiments and sessions are named);
  SHAPE-ONLY      its shape has a committed run on that card in another configuration (format, data or mask), none in its own;
  NEVER           no committed run of its shape on that card in the index, and no COUNTED token hit for that card in E213's scan;
  NEVER-BY-INDEX  no committed run of its shape on that card in the index, but E213's scan finds its token in files it classes to that
                  card (folders naming no card count for every card; kit copies, schedules and other scans' records count too: the
                  files are listed so the reader can see which they are);
  and, REPORTED beside: the configuration's committed runs on other cards; whether the arm's shire mask has any committed run on that
  card (any shape, format or data); E215 arm B's registered points on card 1 with the same configuration or shape (planned to run before
  E217's first session; a label for the data lane to re-read once arm B's data exist).
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
RX = re.compile(r'(gemmL(?:n|nc)?\d+x\d+x\d+)(?![0-9x])')
SKIP_EXT = ('.bin', '.npz', '.npy', '.png', '.pdf', '.elf', '.o', '.a', '.so', '.zip', '.xz', '.zst', '.gguf')
MAX_BYTES = 400_000_000
KINDS_TILES = 'tools/claims-v3/kinds/tiles'


def now():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')


def sha(p):
    with open(p, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


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
    # E217's own folders; the lane card-e213b, E213 arm B's first card lane, which stopped at its step 4 before any card command
    # (Wed 18 Nov 2026 06:39:56 PST): its files hold arm B's planned points, never a run (E214's scan subtracted it too); and E215's card
    # lanes card-e215a and card-e215b, which had made no card command when this scan ran (their files hold E215's planned points only;
    # E215 is in the configuration index as PLANNED)
    return ('-e217-' in rel) or rel.startswith(('W/out/data-e217/', 'W/out/verify-e217d/', 'W/out/fix-e217d/', 'W/out/card-e213b/',
                                                'W/out/card-e215a/', 'W/out/card-e215b/'))


def lane_card(rel):
    if rel.startswith('W/out/card-e206a/'):
        return A3
    if rel.startswith('W/out/card-e206b'):
        return C1
    if rel.startswith('W/out/card-e213a/'):
        return A3
    if rel.startswith('W/out/card-e213b'):
        return C1
    if rel.startswith('W/out/card-e215a'):
        return A3
    if rel.startswith('W/out/card-e215b'):
        return C1
    if rel.startswith('W/out/card-e216'):
        return A2
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
    roots = [os.path.join(lab, 'docs', 'reports', 'data'), os.path.join(lab, 'tools', 'claims-v3', 'e214', 'proposal', 'src', 'sched'),
             os.path.join(lab, 'tools', 'claims-v3', 'e214', 'proposal', 'src', 'arms.json'),
             os.path.join(lab, 'tools', 'claims-v3', 'e212', 'proposal', 'src', 'sched'),
             os.path.join(lab, 'tools', 'claims-v3', 'e208', 'proposal', 'src')]
    lane_roots = sorted(os.path.join(lanes, d) for d in os.listdir(lanes) if d.startswith(('card-', 'data-', 'a1', 'a2', 'a3')))
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
            dn.sort()
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
    rec = {'what': "E217's shape-level scan (shape tokens, by card; E213's form, as E214's)", 'started': t0, 'ended': now(),
           'files_read': nfiles, 'roots': [os.path.relpath(r, lab) for r in roots],
           'lane_roots': ['W/out/' + os.path.basename(r) for r in lane_roots],
           'lane_roots_that_are_files_read_as_files': ['W/out/' + os.path.basename(r) for r in lane_files],
           'over_400MB_not_read': [os.path.relpath(p, lanes) if p.startswith(lanes) else os.path.relpath(p, lab) for p in skipped_big],
           'unreadable': unreadable, 'git_dirs_not_read': git_dirs,
           'tokens': {t: {c: {'n': len(v), 'files': sorted(set(v))[:8]} for c, v in sorted(cs.items())} for t, cs in sorted(hits.items())}}
    os.makedirs(out, exist_ok=True)
    json.dump(rec, open(os.path.join(out, 'scan-e217.json'), 'w'), indent=1, sort_keys=True)
    print(f"scan: {nfiles} files read, {len(hits)} distinct tokens, {len(lane_roots)} lane roots ({len(lane_files)} of them files), "
          f"{len(skipped_big)} over 400 MB not read, {unreadable} unreadable, {git_dirs} scratch clones not read; {t0} - {rec['ended']}")


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
            return f'tile:{tile_sha}'
        return f'gen-{gen}:{tile_sha}'


def parse_values(v):
    parts = v.split(':')
    return parts[0], (parts[1] if len(parts) > 1 else ''), (parts[2] if len(parts) > 2 else '')


def kit_tile_sha(kit_root, f, cache):
    if not f:
        return ''
    p = os.path.join(kit_root, f)
    if p not in cache:
        cache[p] = sha(p) if os.path.exists(p) else 'MISSING:' + f
    return cache[p]


def configs(lab, out):
    t0 = now()
    K = Kinds(lab)
    recs = []
    cache = {}
    ddir = os.path.join(lab, 'docs', 'reports', 'data')
    # (1) the committed E208, E212 and E214 sessions, run by run
    for d in sorted(os.listdir(ddir)):
        m = re.match(r'\d{4}-\d\d-\d\d-(e208)-mmsweep-(a\dc\d)-(S\d+r?)$', d) or re.match(r'\d{4}-\d\d-\d\d-(e212)-mmsweep2-(a\dc\d)-(S\d+)$', d) \
            or re.match(r'\d{4}-\d\d-\d\d-(e214)-mmsweep3-(a\dc\d)-(S\d+)$', d)
        if not m:
            continue
        exp, ck, sess = m.group(1).upper(), m.group(2), m.group(3)
        kit = os.path.join(lab, 'tools', 'claims-v3', m.group(1), 'proposal')
        dj = [f for f in os.listdir(os.path.join(ddir, d)) if f.startswith('data-') and f.endswith('.json')]
        if len(dj) != 1:
            recs.append({'source': f'{d}: data JSON not found ({dj})', 'error': True})
            continue
        D = json.load(open(os.path.join(ddir, d, dj[0])))
        for r in D['runs']:
            if r.get('role') not in ('arm', 'time', 'anchor') or not r.get('ran'):
                continue
            tok, gen, f = parse_values(r['values'])
            recs.append({'exp': exp, 'source': f'docs/reports/data/{d} run {r["run"]}', 'session': f'{ck}-{sess}', 'card': SESS_CARD[ck],
                         'kernel': 'rgm136', 'token': tok, 'fmt': r['type'], 'data': K.data_key(gen, kit_tile_sha(kit, f, cache)),
                         'mask': r['shires'], 'arm_id': r['arm'], 'role': r['role'], 'status': 'RAN (committed)'})
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
                             'kernel': p['kernel'], 'token': p['arm'], 'fmt': p['fmt'], 'data': data, 'mask': p['mask'],
                             'arm_id': '', 'role': 'point', 'status': 'RAN (committed; MM1-v3.1 vendored)'})
                n_v31 += 1
        finally:
            sys.path.pop(0)
    # (3) E215's registered points and references: neither arm had run at this index
    pj = os.path.join(lab, 'tools', 'claims-v3', 'e215', 'points-e215.json')
    n_e215 = 0
    if os.path.exists(pj):
        P = json.load(open(pj))
        for arm, card in (('A', A3), ('B', C1)):
            for grp in ('points', 'references'):
                for p in P['arms'][arm].get(grp, []):
                    tok, gen, f = parse_values(p.get('values', p['arm'] + '::'))
                    tsha = sha(os.path.join(lab, f)) if f and os.path.exists(os.path.join(lab, f)) else ''
                    data = K.data_key(gen, tsha) if gen else {'random': 'random', 'zeros': 'zeros', 'ones': 'ones'}.get(
                        p.get('kind', ''), 'kind:' + str(p.get('kind')))
                    recs.append({'exp': 'E215', 'source': f"tools/claims-v3/e215/points-e215.json arm {arm} {grp} {p['id']}",
                                 'session': f'arm {arm}', 'card': card, 'kernel': p.get('kernel', 'rgm136'), 'token': p['arm'],
                                 'fmt': p.get('format', p.get('fmt')), 'data': data, 'mask': p.get('shire_mask', p.get('mask')),
                                 'arm_id': p['id'], 'role': p.get('role', grp[:-1]),
                                 'status': f'PLANNED (E215 arm {arm}, registered; not run at this index)'})
                    n_e215 += 1
    rec = {'what': "E217's configuration index of committed runs (and E215's registered points)", 'started': t0, 'ended': now(),
           'n_direct_e208_e212_e214_runs': n_direct, 'n_mm1v31_points': n_v31, 'n_e215_points': n_e215, 'kinds_tiles': K.map,
           'records': recs}
    os.makedirs(out, exist_ok=True)
    json.dump(rec, open(os.path.join(out, 'configs-e217.json'), 'w'), indent=1, sort_keys=True)
    print(f'configs: {n_direct} committed E208/E212/E214 run records, {n_v31} MM1-v3.1 points, {n_e215} E215 registered points; '
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
    cache = {}
    on = {}
    for fn in sorted(os.listdir(os.path.join(src, 'sched'))):
        s = json.load(open(os.path.join(src, 'sched', fn)))
        ck = s.get('card') or fn.split('-')[0]
        card = SESS_CARD.get(ck, ck)
        for r in s['runs']:
            if r['role'] in ('arm', 'time', 'anchor'):
                on.setdefault(r['arm'], {}).setdefault(card, set()).add(s.get('session', fn))
    recs = [r for r in CF['records'] if not r.get('error')]
    by_key, by_shape, masks_ran = {}, {}, {}
    for r in recs:
        by_key.setdefault((r['kernel'], r['token'], r['fmt'], r['data'], r['mask']), []).append(r)
        by_shape.setdefault((r['kernel'], r['token']), []).append(r)
        if r['status'].startswith('RAN'):
            masks_ran.setdefault(r['card'], set()).add(r['mask'])
    rows, lines = [], []
    tally, mtally = {}, {}
    for a in arms['arms']:
        tok, gen, f = parse_values(a['values'])
        data = K.data_key(gen, kit_tile_sha(kit_root, f, cache))
        same = by_key.get(('rgm136', tok, a['type'], data, a['shires']), [])
        shp = by_shape.get(('rgm136', tok), [])
        for card, sess in sorted(on.get(a['id'], {}).items()):
            ran_here = sorted({f"{r['exp']} {r['session']}".strip() for r in same if r['card'] == card and r['status'].startswith('RAN')})
            shape_here = sorted({r['exp'] for r in shp if r['card'] == card and r['status'].startswith('RAN')})
            planned_here = sorted({f"{r['exp']} {r['arm_id']}" for r in same if r['card'] == card and r['status'].startswith('PLANNED')})
            planned_shape = sorted({f"{r['exp']} {r['arm_id']}" for r in shp if r['card'] == card and r['status'].startswith('PLANNED')})
            other = sorted({f"{r['exp']} on {r['card']}" for r in same if r['card'] != card and r['status'].startswith('RAN')})
            mask_seen = a['shires'] in masks_ran.get(card, set())
            cs = T.get(tok, {})
            tok_here = {c: v['n'] for c, v in cs.items() if c != 'SUBTRACTED' and counted_for(card, c)}
            tok_files = sorted({x for c, v in cs.items() if c != 'SUBTRACTED' and counted_for(card, c) for x in v['files']})[:6]
            if ran_here:
                label = 'REPEAT'
            elif shape_here:
                label = 'SHAPE-ONLY'
            elif tok_here:
                label = 'NEVER-BY-INDEX'
            else:
                label = 'NEVER'
            tally[(card, label)] = tally.get((card, label), 0) + 1
            mtally[(card, 'mask run before on the card' if mask_seen else 'mask new on the card')] = \
                mtally.get((card, 'mask run before on the card' if mask_seen else 'mask new on the card'), 0) + 1
            rows.append({'arm': a['id'], 'card': card, 'sessions': sorted(sess), 'token': tok, 'fmt': a['type'], 'data': data,
                         'mask': a['shires'], 'families': a['families'], 'label': label,
                         'config_committed_on_card': ran_here, 'shape_committed_on_card': shape_here,
                         'config_committed_other_cards': other, 'mask_committed_on_card': mask_seen,
                         'e213_scan_counted_hits': tok_here, 'e213_scan_counted_files_sample': tok_files,
                         'e213_scan_never_run': not tok_here,
                         'e215b_planned_same_config': planned_here, 'e215b_planned_same_shape': planned_shape})
            lines.append(f"{label:14s} {card:18s} {a['id']:36s} {','.join(sorted(sess)):12s} config={ran_here} shape={shape_here} "
                         f"mask={'seen' if mask_seen else 'new'} e213-scan={'never' if not tok_here else tok_here} "
                         f"e215-plan={planned_here or planned_shape} other={other}")
    res = {'what': "E217's never-run labels per arm and card (desk/neverrun_e217.py report); labels only, nothing dropped",
           'scan_sha256': sha(scan_path), 'configs_sha256': sha(configs_path), 'arms_sha256': sha(os.path.join(src, 'arms.json')),
           'scan_window': [S['started'], S['ended']], 'files_read': S['files_read'], 'rows': rows,
           'tally': {f'{c} {l}': n for (c, l), n in sorted(tally.items())},
           'mask_tally': {f'{c} {l}': n for (c, l), n in sorted(mtally.items())},
           'masks_committed_by_card': {c: sorted(v) for c, v in sorted(masks_ran.items())}}
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, 'neverrun-e217.json'), 'w'), indent=1, sort_keys=True)
    head = [f"E217 never-run labels; scan {res['scan_sha256'][:16]} ({S['files_read']} files, {S['started']} - {S['ended']}); "
            f"configs {res['configs_sha256'][:16]}; arms {res['arms_sha256'][:16]}",
            'tally (arm x card): ' + '; '.join(f'{k} {v}' for k, v in res['tally'].items()),
            'masks (arm x card): ' + '; '.join(f'{k} {v}' for k, v in res['mask_tally'].items())]
    open(os.path.join(out, 'neverrun-e217.txt'), 'w').write('\n'.join(head + lines) + '\n')
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
