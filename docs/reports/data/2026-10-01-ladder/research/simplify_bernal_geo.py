#!/usr/bin/env python3
"""Write bernal-geo.json, the small map of Bernal Heights and 29th Street the ladder draws (1 Oct 2026).

    simplify_bernal_geo.py RAWDIR

RAWDIR holds what make_bernal_geo.py and the two EPQS scripts wrote (they read DataSF and USGS; not committed):
bernal-geo-full.json (299 KB of outlines), st29.json (the 29th Street centrelines from DataSF) and epqs_29th.out
(the street's elevation profile). This script clips every outline to the frame the ladder's Bernal Heights level
draws, simplifies it (Douglas-Peucker, 4 m) and rounds it to the metre, and adds the street's profile and the
distances of its cross streets along it.

Units: km on the San Francisco map's projection (outside-geo.json "sf": equirectangular at 37.76 N, 122.44 W),
x east, y south. Privacy: outlines and the whole street only; the one point is the hill's summit (a public landmark,
GNIS 1658039). No address range, block or point of the studio is read into the output: from st29.json only the
segments' cross-street names and lengths are used.
"""
import json
import math
import os
import re
import sys

RAW = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('LADDER_RAW', '')
HERE = os.path.dirname(os.path.abspath(__file__))
FULL = json.load(open(os.path.join(RAW, 'bernal-geo-full.json')))
CLIP = (-0.35, 0.35, 4.05, 3.85)      # the box every outline is clipped to (km): the Bernal level's frame and a margin
TOL = 0.004                          # km: Douglas-Peucker tolerance (4 m)


def parse(d):
    """SVG path data of M/L/Z into rings: [[(x, y), ...], closed?]"""
    out, cur = [], None
    for tok in re.findall(r'[MLZ]|-?[\d.]+,-?[\d.]+', d):
        if tok == 'M':
            cur = []; out.append([cur, False])
        elif tok == 'L':
            continue
        elif tok == 'Z':
            out[-1][1] = True
        else:
            x, y = map(float, tok.split(',')); cur.append((x, y))
    return out


def dp(pts, tol):
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    best, bi = -1, 0
    for i in range(1, len(pts) - 1):
        p = pts[i]
        d = abs(dy * (p[0] - a[0]) - dx * (p[1] - a[1])) / L if L > 1e-12 else math.hypot(p[0] - a[0], p[1] - a[1])
        if d > best:
            best, bi = d, i
    if best <= tol:
        return [a, b]
    return dp(pts[:bi + 1], tol)[:-1] + dp(pts[bi:], tol)


def clip_poly(pts):
    """Sutherland-Hodgman against the CLIP box"""
    x0, y0, x1, y1 = CLIP
    edges = [(lambda p: p[0] >= x0, lambda p, q: (x0, p[1] + (q[1] - p[1]) * (x0 - p[0]) / (q[0] - p[0]))),
             (lambda p: p[0] <= x1, lambda p, q: (x1, p[1] + (q[1] - p[1]) * (x1 - p[0]) / (q[0] - p[0]))),
             (lambda p: p[1] >= y0, lambda p, q: (p[0] + (q[0] - p[0]) * (y0 - p[1]) / (q[1] - p[1]), y0)),
             (lambda p: p[1] <= y1, lambda p, q: (p[0] + (q[0] - p[0]) * (y1 - p[1]) / (q[1] - p[1]), y1))]
    for inside, cut in edges:
        if not pts:
            break
        out = []
        for i, q in enumerate(pts):
            p = pts[i - 1]
            if inside(q):
                if not inside(p):
                    out.append(cut(p, q))
                out.append(q)
            elif inside(p):
                out.append(cut(p, q))
        pts = out
    return pts


def clip_line(pts):
    """the pieces of a polyline inside the CLIP box (segments with an end outside are cut at the box)"""
    x0, y0, x1, y1 = CLIP
    ins = lambda p: x0 <= p[0] <= x1 and y0 <= p[1] <= y1
    pieces, cur = [], []
    for i, p in enumerate(pts):
        if ins(p):
            cur.append(p)
        else:
            if cur:
                pieces.append(cur); cur = []
    if cur:
        pieces.append(cur)
    return [c for c in pieces if len(c) >= 2]


f3 = lambda v: ('%.3f' % v).rstrip('0').rstrip('.').replace('-0', '0') if abs(v) >= 0.0005 else '0'


def path(rings):
    return ''.join('M' + 'L'.join(f3(x) + ',' + f3(y) for x, y in pts) + ('Z' if closed else '') for pts, closed in rings)


def poly(d):
    out = []
    for pts, closed in parse(d):
        c = clip_poly(pts)
        c = dp(c + [c[0]], TOL)[:-1] if len(c) >= 3 else []
        if len(c) >= 3:
            out.append((c, True))
    return out


def line(d):
    out = []
    for pts, _ in parse(d):
        for piece in clip_line(pts):
            s = dp(piece, TOL)
            if len(s) >= 2:
                out.append((s, False))
    # join pieces that continue one another (the centrelines come as one segment per block)
    j = []
    for pts, c in out:
        if j and math.hypot(j[-1][0][-1][0] - pts[0][0], j[-1][0][-1][1] - pts[0][1]) < 1e-6:
            j[-1] = (j[-1][0] + pts[1:], False)
        else:
            j.append((pts, c))
    return j


def centroid(rings):
    a = cx = cy = 0
    for pts, _ in rings:
        for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
            k = x1 * y2 - x2 * y1; a += k; cx += (x1 + x2) * k; cy += (y1 + y2) * k
    return [round(cx / (3 * a), 3), round(cy / (3 * a), 3)] if abs(a) > 1e-9 else None


out = {'meta': {'projection': FULL['meta']['projection'], 'sources': FULL['meta']['sources'],
                'privacy': 'Outlines and the whole of 29th Street only; the one point is the hill\'s summit, a public landmark. No address, block or point of the studio.',
                'simplified': f'clipped to x {CLIP[0]}..{CLIP[2]}, y {CLIP[1]}..{CLIP[3]} km; Douglas-Peucker {TOL * 1000:.0f} m; rounded to 1 m (simplify_bernal_geo.py)'}}
b = poly(FULL['bernal']['path'])
out['bernal'] = {'path': path(b), 'bbox_km': FULL['bernal']['bbox_km'], 'size_km': FULL['bernal']['size_km'], 'area_km2': FULL['bernal']['area_km2']}
out['neighbours'] = {}
for name, d in FULL['neighbours'].items():
    r = poly(d)
    if r:
        out['neighbours'][name] = {'path': path(r), 'c': centroid(r)}
out['park'] = {'path': path(poly(FULL['park']['path'])), 'acres': FULL['park']['acres'], 'ha': FULL['park']['ha']}
out['summit'] = FULL['summit']
KEEP = {'CESAR CHAVEZ ST': 'Cesar Chavez St', 'SAN JOSE AVE': 'San Jose Ave', 'HWY 101 NORTHBOUND': 'US 101', 'I-280 NORTHBOUND': 'I-280',
        'MISSION ST': 'Mission St', 'CORTLAND AVE': 'Cortland Ave', 'BERNAL HEIGHTS BLVD': 'Bernal Heights Blvd'}
out['roads'] = {lab: path(line(FULL['roads'][k])) for k, lab in KEEP.items() if k in FULL['roads']}
# 29th Street: the whole street, its profile and its cross streets (names and distances only)
st = json.load(open(os.path.join(RAW, 'st29.json')))
lat0 = 37.75; mx = 111320 * math.cos(math.radians(lat0)); my = 111320
segs = sorted(st, key=lambda s: sum(p[0] for p in s['line']['coordinates']) / len(s['line']['coordinates']))
cross, dist = [], 0.0
for s in segs:
    c = s['line']['coordinates']
    west, east = (s['f_st'], s['t_st']) if c[0][0] <= c[-1][0] else (s['t_st'], s['f_st'])
    if not cross:
        cross.append({'name': west.title().replace(' St', ' St').replace(' Ave', ' Ave').replace(' Pl', ' Pl'), 'd_m': 0})
    dist += sum(math.hypot((b2[0] - a2[0]) * mx, (b2[1] - a2[1]) * my) for a2, b2 in zip(c, c[1:]))
    cross.append({'name': east.title(), 'd_m': round(dist)})
prof = None
for ln in open(os.path.join(RAW, 'epqs_29th.out')):
    if ln.startswith('[('):
        prof = [[d, h] for d, h in eval(ln)]
out['st29'] = {'path': path(line(FULL['st29']['path'])), 'length_km': FULL['st29']['length_km'], 'profile_m': prof, 'cross': cross}
s = json.dumps(out, separators=(',', ':'), ensure_ascii=False)
assert not re.search(r'\b941\d\d\b|_fadd|_toadd|\bcnn\b', s), 'an address field leaked into the output'
open(os.path.join(HERE, 'bernal-geo.json'), 'w').write(s)
print('wrote bernal-geo.json', len(s), 'bytes;', 'neighbours', sorted(out['neighbours']), 'roads', sorted(out['roads']))
print('cross streets', cross)
