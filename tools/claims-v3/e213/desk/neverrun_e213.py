#!/usr/bin/env python3
"""E213 (Q216) desk: which of E213's points never ran, per arm and card - arm A on aifoundry3 card 0, arm B on aifoundry1 card 1. Standard library
only; reads files, writes only its report.

    python3 -I -B tools/claims-v3/e213/desk/neverrun_e213.py scan --lab <the lab at GitHub main> --lanes <W/out> --out <dir>
        reads every file under the lab's committed data folders (docs/reports/data), E212's and E208's committed schedules and arms
        (tools/claims-v3/e212/proposal/src/sched, tools/claims-v3/e208/proposal/src), MM1-v3's vendored measured points (its data loader), and
        the round's card and data lane folders under W/out (names starting card-, data-, a1, a2, a3), gzip read through; writes <dir>/scan-e213.json
    python3 -I -B tools/claims-v3/e213/desk/neverrun_e213.py report --scan <scan-e213.json> --points <points list JSON> --out <dir>
        writes <dir>/neverrun-e213.json and <dir>/neverrun-e213.txt (the per-point verdicts)

THE TOKEN of a point is its arm as the lab's host spells it: gemmL<MB>x<NB>x<KB> (rgm136's gemmL loop, and rgm211's own gemmL copy, which the
host spells the same), gemmLn<..> (rgm211's swapped walk) or gemmLnc<..> (rgm136's non-cooperative loads), matched as a whole token (not followed
by a digit or 'x'). A shape token found in a run record names that shape in SOME format, data kind and mask: the scan is SHAPE-LEVEL, the strictest
reading (MM1-v3's own scan rule, e213_v3.py).
EACH HIT IS CLASSED BY WHERE IT SITS (the folder names in its path, MM1-v3's folder_card rule widened by the forms '-card1' and 'aifoundry1-c1'):
  COUNTED for a card     a data or lane folder naming that card, naming no card (conservative: it may be any card's), or naming aifoundry1
                         without a card (for either aifoundry1 card); E212's and E208's schedules count for the card their file names;
  OTHER CARD (REPORTED)  a folder naming another card;
  SUBTRACTED             E213's own folders: a data folder whose name holds '-e213-', the lanes card-e213a and card-e213b.
DESK folders (registrations, models, kits, verifiers and their stand-in doubles) are not read: verify-e207 showed a scanner must not count them;
nor is a scratch clone of the lab inside a lane folder (a directory holding a .git entry: the lab is read at its source, GitHub main).
THE RULES (E213.md section 4): arm A keeps a never-run point of MM1-v3's frozen list only if its token has no hit on ANY card (Q216's brief:
'drop any point that ran anywhere since', since MM1-v3's own scan found none of the 123 anywhere); its three declared references (MM1-v3's
'ran before' rows) stay references. Arm B keeps a point only if its token has no COUNTED hit for aifoundry1 card 1; hits on other cards are
REPORTED. A reference (k41) is listed as one. Not read: the model session's uncommitted folders on its boxes (the orchestrator's rule of 23:18:35
PST Mon 16 Nov 2026: no lab lane reads them; every session of theirs on card 1 and aifoundry2 is committed and read here); aifoundry1's and
aifoundry3's own disks (the round's card lanes copy their run folders back to W/out, read here).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import datetime
import gzip
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
RX = re.compile(r'(gemmL(?:n|nc)?\d+x\d+x\d+)(?![0-9x])')
SKIP_EXT = ('.bin', '.npz', '.npy', '.png', '.pdf', '.elf', '.o', '.a', '.so', '.zip', '.xz', '.zst', '.gguf')
MAX_BYTES = 400_000_000


def now():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')


def folder_card(path, expmap):
    """the card a data or lane folder's path names, or None (no card named)"""
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
    # the round's card lanes whose folder names carry an experiment but no card (card-e206b2 ran arm B on card 1, card-e206a arm A on aifoundry3)
    m.update({'206': None})
    return m


def subtracted(rel):
    return ('-e213-' in rel) or rel.startswith('W/out/card-e213a/') or rel.startswith('W/out/card-e213b/')


def read_text(p):
    if p.endswith('.gz'):
        with gzip.open(p, 'rb') as fh:
            return fh.read().decode('utf-8', 'ignore')
    with open(p, 'rb') as fh:
        return fh.read().decode('utf-8', 'ignore')


def lane_card(rel):
    """a lane folder of the round: card-e206a ran on aifoundry3, card-e206b2 on card 1; others by name"""
    if rel.startswith('W/out/card-e206a/'):
        return A3
    if rel.startswith('W/out/card-e206b'):
        return C1
    return None


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
                # a scratch clone of the lab inside a lane folder: not read (the lab is read at its source, GitHub main)
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
    # MM1-v3's vendored measured points (its own data loader; every one is a committed run)
    measured = {}
    v3 = os.path.join(lab, 'tools', 'matmul', 'mm1', 'v3')
    if os.path.isdir(v3):
        sys.path.insert(0, v3)
        try:
            import data_v3 as D  # noqa: E402
            for p in D.time_points():
                measured.setdefault(p['arm'], set()).add((p['kernel'], p['card']))
        finally:
            sys.path.pop(0)
    rec = {'what': "E213's never-run scan (shape tokens, by card)", 'started': t0, 'ended': now(), 'files_read': nfiles,
           'roots': [os.path.relpath(r, lab) for r in roots], 'lane_roots': ['W/out/' + os.path.basename(r) for r in lane_roots],
           'over_400MB_not_read': [os.path.relpath(p, lanes) if p.startswith(lanes) else os.path.relpath(p, lab) for p in skipped_big],
           'unreadable': unreadable, 'git_dirs_not_read': git_dirs,
           'tokens': {t: {c: {'n': len(v), 'files': sorted(set(v))[:8]} for c, v in sorted(cs.items())} for t, cs in sorted(hits.items())},
           'mm1_v3_measured_points': {t: sorted(f'{k} on {c}' for k, c in v) for t, v in sorted(measured.items())}}
    os.makedirs(out, exist_ok=True)
    json.dump(rec, open(os.path.join(out, 'scan-e213.json'), 'w'), indent=1, sort_keys=True)
    print(f"scan: {nfiles} files read, {len(hits)} distinct tokens, {len(skipped_big)} over 400 MB not read, {unreadable} unreadable; {t0} - {rec['ended']}")


def counted_for(card, c):
    if c == card or c == NONE:
        return True
    if card in (C1, C0) and c == A1U:
        return True
    return False


def report(scan_path, points_path, out):
    S = json.load(open(scan_path))
    P = json.load(open(points_path))
    T = S['tokens']
    M = S.get('mm1_v3_measured_points', {})
    import hashlib
    res = {'what': "E213's never-run verdicts per point (desk/neverrun_e213.py report)", 'arms': {},
           'scan_sha256': hashlib.sha256(open(scan_path, 'rb').read()).hexdigest(),
           'candidates_sha256': hashlib.sha256(open(points_path, 'rb').read()).hexdigest()}
    res['scan_window'] = [S['started'], S['ended']]
    res['files_read'] = S['files_read']
    lines = []
    for arm in ('A', 'B'):
        card = A3 if arm == 'A' else C1
        rows = []
        for p in P['arms'][arm]:
            tok = p['arm']
            cs = T.get(tok, {})
            on_card = {c: v['n'] for c, v in cs.items() if c != 'SUBTRACTED' and counted_for(card, c)}
            other = {c: v['n'] for c, v in cs.items() if c != 'SUBTRACTED' and not counted_for(card, c)}
            sub = cs.get('SUBTRACTED', {}).get('n', 0)
            meas = [m for m in M.get(tok, []) if (p['kernel'] in m)]
            meas_here = [m for m in meas if m.endswith(card)]
            ref = p.get('role') == 'reference'
            if p['kernel'] == 'rgm211' and tok.startswith('gemmL') and not tok.startswith('gemmLn'):
                # rgm211's own gemmL copy: the token names rgm136's runs; rgm211's ELF never ran its gemmL loop on any card (E211 ran gemmLn only)
                kernel_note = "rgm211's own gemmL loop: its token is rgm136's; read as rgm136's hits"
            else:
                kernel_note = ''
            if arm == 'A':
                never = not (on_card or other or meas)
            else:
                never = not (on_card or meas_here)
            rows.append({'id': p['id'], 'token': tok, 'kernel': p['kernel'], 'role': p.get('role', 'point'), 'never_run': never,
                         'counted_hits_on_card': on_card, 'other_card_hits': other, 'subtracted_hits': sub, 'mm1_v3_measured': meas,
                         'note': kernel_note})
            lines.append(f"{arm} {p['id']:5s} {tok:16s} {p['kernel']:7s} {p.get('role', 'point'):9s} never_run={never} on_card={on_card} "
                         f"other={other} measured={meas}")
        n_pts = [r for r in rows if r['role'] != 'reference']
        res['arms'][arm] = {'card': card, 'rule': ('no hit on any card (ran anywhere since: dropped)' if arm == 'A'
                                                   else 'no counted hit for aifoundry1 card 1'),
                            'points': rows, 'n_points': len(n_pts), 'n_never_run': sum(1 for r in n_pts if r['never_run']),
                            'dropped': [r['id'] for r in n_pts if not r['never_run']],
                            'references': [r['id'] for r in rows if r['role'] == 'reference']}
    json.dump(res, open(os.path.join(out, 'neverrun-e213.json'), 'w'), indent=1, sort_keys=True)
    head = [f"E213 never-run report; scan {res['scan_sha256'][:16]} ({S['files_read']} files, {S['started']} - {S['ended']})"]
    for arm in ('A', 'B'):
        a = res['arms'][arm]
        head.append(f"arm {arm} ({a['card']}; rule: {a['rule']}): {a['n_never_run']} of {a['n_points']} points never ran; dropped {a['dropped']}; "
                    f"references {a['references']}")
    open(os.path.join(out, 'neverrun-e213.txt'), 'w').write('\n'.join(head + lines) + '\n')
    print('\n'.join(head))


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    a1 = sp.add_parser('scan')
    a1.add_argument('--lab', required=True)
    a1.add_argument('--lanes', required=True)
    a1.add_argument('--out', required=True)
    a2 = sp.add_parser('report')
    a2.add_argument('--scan', required=True)
    a2.add_argument('--points', required=True)
    a2.add_argument('--out', required=True)
    a = ap.parse_args()
    if a.cmd == 'scan':
        scan(os.path.abspath(a.lab), os.path.abspath(a.lanes), a.out)
    else:
        report(a.scan, a.points, a.out)


if __name__ == '__main__':
    main()
