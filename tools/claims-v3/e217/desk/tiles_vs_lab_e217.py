"""E217 (reg-e217, Q228): every tile file of the proposal's src/tiles against every 2,048-byte .bin file in the lab tree (tools/ and
docs/reports/data/), by sha256 (reads only; Python's own modules). It names, for each of E217's 33 tile files, how many lab files hold
the same bytes and up to six of their paths (E217's own folder left out), and counts the tiles new to the lab.

    /usr/bin/python3 -I -B tiles_vs_lab_e217.py <the proposal's src dir> <the lab tree>
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import os
import sys

src, lab = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])


def sha(p):
    with open(p, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


have = {}
n = 0
for top in (os.path.join(lab, 'tools'), os.path.join(lab, 'docs', 'reports', 'data')):
    for dp, dn, fns in os.walk(top):
        dn[:] = sorted(d for d in dn if d != '.git')
        rel_dp = os.path.relpath(dp, lab)
        if rel_dp.startswith(os.path.join('tools', 'claims-v3', 'e217')):
            dn[:] = []
            continue
        for f in sorted(fns):
            p = os.path.join(dp, f)
            if f.endswith('.bin') and not os.path.islink(p) and os.path.getsize(p) == 2048:
                have.setdefault(sha(p), []).append(os.path.relpath(p, lab))
                n += 1
print('# E217: its tile files against the lab tree, by sha256')
print('lab tree: %d files of 2,048 bytes named *.bin under tools/ and docs/reports/data/ (E217\'s own folder left out), %d distinct' % (n, len(have)))
new = 0
tiles = []
for dp, dn, fns in os.walk(os.path.join(src, 'tiles')):
    dn.sort()
    for f in sorted(fns):
        tiles.append(os.path.join(dp, f))
for p in sorted(tiles):
    s = sha(p)
    hits = sorted(have.get(s, []))
    new += not hits
    print('%s %s: %d lab file(s)%s' % (os.path.relpath(p, os.path.dirname(src)), s, len(hits),
                                       (': ' + ', '.join(hits[:6]) + (' ...' if len(hits) > 6 else '')) if hits else ' (new to the lab)'))
print('tile files: %d; equal to a lab file: %d; new to the lab: %d' % (len(tiles), len(tiles) - new, new))
