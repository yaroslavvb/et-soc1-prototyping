#!/usr/bin/env python3
"""E214 (reg-e214, Q220) desk: which of E214's arms repeat a configuration already committed on the card its schedules put it on - LABELS ONLY,
nothing dropped (E214's arms are the model session's, registered by its post; the lab only labels them). E213's never-run scan
(tools/claims-v3/e213/desk/neverrun_e213.py) in form, with a configuration-level reading added. Reads files only; writes only its outputs.

    python3 -I -B neverrun_e214.py scan --lab <the lab at GitHub main> --lanes <W/out> --out <dir>
        THE SHAPE-LEVEL SCAN, E213's: every file under the lab's committed data folders (docs/reports/data), E212's and E208's committed
        schedules and arms, and the round's card and data lane folders under W/out (names starting card-, data-, a1, a2, a3), gzip read
        through; a token gemmL<MB>x<NB>x<KB> (also gemmLn/gemmLnc) matched whole; each hit classed by the folder it sits in (E213's
        folder_card rule): COUNTED for a card (a folder naming that card, naming no card, or naming aifoundry1 without a card), OTHER
        CARD, SUBTRACTED (E214's own folders: a data folder holding '-e214-', the lanes data-e214, verify-e214d, fix-e214d; and the lane
        card-e213b, E213 arm B's first card lane, stopped at its step 4 before any card command, whose files hold planned points only). Writes
        <dir>/scan-e214.json.
    python3 -I -B neverrun_e214.py configs --lab <the lab at GitHub main> --out <dir>
        THE CONFIGURATION INDEX of committed runs, by card: (1) every run record ('ran' true; roles arm, time, anchor) of every committed
        session of the model session's sweeps E208 and E212 (docs/reports/data/*-e208-mmsweep-*, *-e212-mmsweep2-*: data-*.json), its
        'values' and 'shires' resolved against that sweep's registered tiles; (2) MM1-v3's vendored measured time points (its data
        loader, tools/matmul/mm1/v3/data_v3.py: E105-E212 as committed when MM1-v3 landed; one record a card and case); (3) E213's
        registered points (tools/claims-v3/e213/points-e213.json): arm A RAN on aifoundry3 card 0 (data c69a12aa); arm B is registered
        for aifoundry1 card 1 and NOT RUN at the time of this index (its rerun is booked before E214's first session): PLANNED, REPORTED.
        Writes <dir>/configs-e214.json. Needs numpy (MM1-v3's loader): run single-threaded inside the round's CPU slot.
    python3 -I -B neverrun_e214.py report --scan <scan-e214.json> --configs <configs-e214.json> --src <E214's src/> --out <dir>
        writes <dir>/neverrun-e214.json and <dir>/neverrun-e214.txt: per arm and per card its sessions put it on, the label.

THE CONFIGURATION of an arm is (kernel rgm136, the shape token, the format, the data, the shire mask): the data is 'random' (the host's randn
generator over the lab's random tile), 'zeros' or 'ones' (the lab's kinds tiles, by bytes), 'sparse50' (the host's drawn pool over the lab's
sparse50 tile, by bytes) or 'tile:<sha256 of the 2,048-byte file>' for any other tile; MM1-v3's records name kinds, read as random, zeros,
ones, sparse50, or 'kind:<its name>' (never equal to a tile key: conservative toward 'not a repeat' only for pattern tiles, which the
direct E212 read covers byte for byte). The process arguments the kit fixes (--per-shire 32 --seconds 6 --budget 7.5 --seed 1) are equal
across E208, E212 and E214 by their registered mms_common.host_argv, so they are not part of the key; the smoke's 2 s processes are not runs.
THE LABELS (per arm and card; nothing is dropped, every arm keeps its place in its schedule). The label is read from THE CONFIGURATION
INDEX (committed runs only); E213's shape-level token scan is reported beside it as the strictest reading:
  REPEAT          its configuration has a committed run on that card (the experiments and sessions are named);
  SHAPE-ONLY      its shape has a committed run on that card in another configuration (format, data or mask), none in its own;
  NEVER           no committed run of its shape on that card in the index, and no COUNTED token hit for that card in E213's scan;
  NEVER-BY-INDEX  no committed run of its shape on that card in the index, but E213's scan finds its token in files it classes to that
                  card (folders naming no card count for every card; kit copies, schedules and other scans' records count too: the
                  files are listed so the reader can see which they are);
  and, REPORTED beside: the configuration's committed runs on other cards; E213 arm B's registered points on card 1 with the same
  configuration or shape (planned to run before E214's first session; a label for the data lane to re-read once arm B's data exist).
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
    # E214's own folders; and the lane card-e213b, E213 arm B's first card lane, which stopped at its step 4 before any card command
    # (Wed 18 Nov 2026 06:39:56 PST): its files hold arm B's planned points, never a run (arm B's rerun is the lane card-e213b2)
    return ('-e214-' in rel) or rel.startswith(('W/out/data-e214/', 'W/out/verify-e214d/', 'W/out/fix-e214d/', 'W/out/card-e213b/'))


def lane_card(rel):
    if rel.startswith('W/out/card-e206a/'):
        return A3
    if rel.startswith('W/out/card-e206b'):
        return C1
    if rel.startswith('W/out/card-e213a/'):
        return A3
    if rel.startswith('W/out/card-e213b'):
        return C1
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
    roots = [os.path.join(lab, 'docs', 'reports', 'data'), os.path.join(lab, 'tools', 'claims-v3', 'e212', 'proposal', 'src', 'sched'),
             os.path.join(lab, 'tools', 'claims-v3', 'e208', 'proposal', 'src')]
    lane_roots = sorted(os.path.join(lanes, d) for d in os.listdir(lanes) if d.startswith(('card-', 'data-', 'a1', 'a2', 'a3')))
    hits = {}
    nfiles, skipped_big, unreadable, git_dirs = 0, [], 0, 0
    for top in roots + lane_roots:
        for dp, dn, fns in os.walk(top):
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
    rec = {'what': "E214's shape-level scan (shape tokens, by card; E213's form)", 'started': t0, 'ended': now(), 'files_read': nfiles,
           'roots': [os.path.relpath(r, lab) for r in roots], 'lane_roots': ['W/out/' + os.path.basename(r) for r in lane_roots],
           'over_400MB_not_read': [os.path.relpath(p, lanes) if p.startswith(lanes) else os.path.relpath(p, lab) for p in skipped_big],
           'unreadable': unreadable, 'git_dirs_not_read': git_dirs,
           'tokens': {t: {c: {'n': len(v), 'files': sorted(set(v))[:8]} for c, v in sorted(cs.items())} for t, cs in sorted(hits.items())}}
    os.makedirs(out, exist_ok=True)
    json.dump(rec, open(os.path.join(out, 'scan-e214.json'), 'w'), indent=1, sort_keys=True)
    print(f"scan: {nfiles} files read, {len(hits)} distinct tokens, {len(lane_roots)} lane folders, {len(skipped_big)} over 400 MB not read, "
          f"{unreadable} unreadable, {git_dirs} scratch clones not read; {t0} - {rec['ended']}")


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
    # (1) the committed E208 and E212 sessions, run by run
    for d in sorted(os.listdir(ddir)):
        m = re.match(r'\d{4}-\d\d-\d\d-(e208)-mmsweep-(a\dc\d)-(S\d+r?)$', d) or re.match(r'\d{4}-\d\d-\d\d-(e212)-mmsweep2-(a\dc\d)-(S\d+)$', d)
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
    # (2) MM1-v3's vendored measured time points
    v3 = os.path.join(lab, 'tools', 'matmul', 'mm1', 'v3')
    n_v3 = 0
    if os.path.isdir(v3):
        sys.path.insert(0, v3)
        try:
            import data_v3 as D3  # noqa: E402
            for p in D3.time_points():
                k = p['kind']
                data = {'random': 'random', 'zeros': 'zeros', 'ones': 'ones', 'sparse50': 'sparse50'}.get(k, f'kind:{k}')
                recs.append({'exp': p['exp'], 'source': f"MM1-v3 vendored point {p['id']}", 'session': '', 'card': p['card'],
                             'kernel': p['kernel'], 'token': p['arm'], 'fmt': p['fmt'], 'data': data, 'mask': p['mask'],
                             'arm_id': '', 'role': 'point', 'status': 'RAN (committed; MM1-v3 vendored)'})
                n_v3 += 1
        finally:
            sys.path.pop(0)
    # (3) E213's registered points: arm A ran (aifoundry3), arm B registered for card 1, not run at this index
    pj = os.path.join(lab, 'tools', 'claims-v3', 'e213', 'points-e213.json')
    n_e213 = 0
    if os.path.exists(pj):
        P = json.load(open(pj))
        for arm, card, status in (('A', A3, 'RAN (committed: E213 arm A data)'), ('B', C1, 'PLANNED (E213 arm B, registered; not run at this index)')):
            for p in P['arms'][arm]['points']:
                tok, gen, f = parse_values(p.get('values', p['arm'] + '::'))
                tsha = sha(os.path.join(lab, f)) if f and os.path.exists(os.path.join(lab, f)) else ''
                data = K.data_key(gen, tsha) if gen else {'random': 'random', 'zeros': 'zeros', 'ones': 'ones'}.get(p.get('kind', ''), 'kind:' + str(p.get('kind')))
                recs.append({'exp': 'E213', 'source': f"tools/claims-v3/e213/points-e213.json arm {arm} {p['id']}", 'session': f'arm {arm}',
                             'card': card, 'kernel': p.get('kernel', 'rgm136'), 'token': p['arm'], 'fmt': p.get('format', p.get('fmt')),
                             'data': data, 'mask': p.get('shire_mask', p.get('mask')), 'arm_id': p['id'], 'role': p.get('role', 'point'),
                             'status': status})
                n_e213 += 1
    rec = {'what': "E214's configuration index of committed runs (and E213 arm B's registered points)", 'started': t0, 'ended': now(),
           'n_direct_e208_e212_runs': n_direct, 'n_mm1v3_points': n_v3, 'n_e213_points': n_e213, 'kinds_tiles': K.map, 'records': recs}
    os.makedirs(out, exist_ok=True)
    json.dump(rec, open(os.path.join(out, 'configs-e214.json'), 'w'), indent=1, sort_keys=True)
    print(f'configs: {n_direct} committed E208/E212 run records, {n_v3} MM1-v3 points, {n_e213} E213 registered points; {t0} - {rec["ended"]}')


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
    by_key, by_shape = {}, {}
    for r in recs:
        by_key.setdefault((r['kernel'], r['token'], r['fmt'], r['data'], r['mask']), []).append(r)
        by_shape.setdefault((r['kernel'], r['token']), []).append(r)
    rows, lines = [], []
    tally = {}
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
            rows.append({'arm': a['id'], 'card': card, 'sessions': sorted(sess), 'token': tok, 'fmt': a['type'], 'data': data,
                         'mask': a['shires'], 'families': a['families'], 'label': label,
                         'config_committed_on_card': ran_here, 'shape_committed_on_card': shape_here,
                         'config_committed_other_cards': other, 'e213_scan_counted_hits': tok_here,
                         'e213_scan_counted_files_sample': tok_files,
                         'e213_scan_never_run': not tok_here,
                         'e213b_planned_same_config': planned_here, 'e213b_planned_same_shape': planned_shape})
            lines.append(f"{label:14s} {card:18s} {a['id']:34s} {','.join(sorted(sess)):12s} config={ran_here} shape={shape_here} "
                         f"e213-scan={'never' if not tok_here else tok_here} e213b-plan={planned_here or planned_shape} other={other}")
    res = {'what': "E214's never-run labels per arm and card (desk/neverrun_e214.py report); labels only, nothing dropped",
           'scan_sha256': sha(scan_path), 'configs_sha256': sha(configs_path), 'arms_sha256': sha(os.path.join(src, 'arms.json')),
           'scan_window': [S['started'], S['ended']], 'files_read': S['files_read'], 'rows': rows,
           'tally': {f'{c} {l}': n for (c, l), n in sorted(tally.items())}}
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, 'neverrun-e214.json'), 'w'), indent=1, sort_keys=True)
    head = [f"E214 never-run labels; scan {res['scan_sha256'][:16]} ({S['files_read']} files, {S['started']} - {S['ended']}); "
            f"configs {res['configs_sha256'][:16]}; arms {res['arms_sha256'][:16]}",
            'tally (arm x card): ' + '; '.join(f'{k} {v}' for k, v in res['tally'].items())]
    open(os.path.join(out, 'neverrun-e214.txt'), 'w').write('\n'.join(head + lines) + '\n')
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
