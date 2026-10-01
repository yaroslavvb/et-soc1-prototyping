#!/usr/bin/env python3
"""Map outlines for the chip diagram's outside levels (San Francisco, the Bay Area, California, the United States,
Earth), as SVG path data in kilometres, so the page can draw them with true scale bars.

Sources (all public domain):
  - US Census Bureau, 2023 Cartographic Boundary Files: cb_2023_us_county_500k (1:500,000) and cb_2023_us_state_5m
    (1:5,000,000), https://www2.census.gov/geo/tiger/GENZ2023/shp/ (a work of the US Government, public domain).
  - Natural Earth 1:110m land, ne_110m_land.geojson (naturalearthdata.com; "All versions of Natural Earth raster +
    vector map data found on this website are in the public domain"), from github.com/nvkelso/natural-earth-vector.

Output: ../outside-geo.json, and preview PNGs in ./geo/preview-*.png.
Units: kilometres on the projection plane, x east, y SOUTH (SVG's y runs down), origin at each map's centre.
No point on these maps marks the lab or any street address: only the outlines and two city centres (SF, NYC).
"""
import json
import math
import os
import struct
import sys
sys.setrecursionlimit(100000)

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.join(HERE, 'geo')
R = 6371.0  # km, NASA's volumetric mean radius (nssdc Earth fact sheet)


# ---------------------------------------------------------------- readers
def read_shp(path):
    """Polygons of a type-5 shapefile: a list (one per record) of rings [(lon, lat), ...]."""
    out = []
    with open(path, 'rb') as f:
        data = f.read()
    p = 100
    while p < len(data):
        _, clen = struct.unpack('>ii', data[p:p + 8])
        rec = data[p + 8:p + 8 + clen * 2]
        p += 8 + clen * 2
        st = struct.unpack('<i', rec[:4])[0]
        if st != 5:
            out.append([])
            continue
        nparts, npts = struct.unpack('<ii', rec[36:44])
        parts = list(struct.unpack('<%di' % nparts, rec[44:44 + 4 * nparts])) + [npts]
        pts = struct.unpack('<%dd' % (2 * npts), rec[44 + 4 * nparts:44 + 4 * nparts + 16 * npts])
        rings = []
        for a, b in zip(parts[:-1], parts[1:]):
            rings.append([(pts[2 * i], pts[2 * i + 1]) for i in range(a, b)])
        out.append(rings)
    return out


def read_dbf(path):
    with open(path, 'rb') as f:
        data = f.read()
    nrec, hlen, rlen = struct.unpack('<IHH', data[4:12])
    fields, p = [], 32
    while data[p] != 0x0D:
        name = data[p:p + 11].split(b'\0')[0].decode()
        flen = data[p + 16]
        fields.append((name, flen))
        p += 32
    rows = []
    for i in range(nrec):
        r = data[hlen + i * rlen + 1: hlen + (i + 1) * rlen]
        d, q = {}, 0
        for name, flen in fields:
            d[name] = r[q:q + flen].decode('utf-8', 'replace').strip()
            q += flen
        rows.append(d)
    return rows


# ---------------------------------------------------------------- projections
def local(lat0, lon0):
    c = math.cos(math.radians(lat0))
    return lambda lon, lat: (R * c * math.radians(lon - lon0), -R * math.radians(lat - lat0))


def albers(lat1, lat2, lat0, lon0):
    """Spherical Albers equal-area conic (Snyder 1987, eqs. 14-1 to 14-6)."""
    p1, p2, p0 = map(math.radians, (lat1, lat2, lat0))
    n = (math.sin(p1) + math.sin(p2)) / 2
    C = math.cos(p1) ** 2 + 2 * n * math.sin(p1)
    rho0 = R * math.sqrt(C - 2 * n * math.sin(p0)) / n

    def f(lon, lat):
        th = n * math.radians(lon - lon0)
        rho = R * math.sqrt(C - 2 * n * math.sin(math.radians(lat))) / n
        return (rho * math.sin(th), -(rho0 - rho * math.cos(th)))
    return f


def ortho(lat0, lon0):
    """Orthographic (a globe seen from far away); points on the far side are pulled onto the limb."""
    p0, l0 = math.radians(lat0), math.radians(lon0)

    def f(lon, lat):
        p, l = math.radians(lat), math.radians(lon)
        cosc = math.sin(p0) * math.sin(p) + math.cos(p0) * math.cos(p) * math.cos(l - l0)
        x = R * math.cos(p) * math.sin(l - l0)
        y = R * (math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(l - l0))
        if cosc < 0:
            k = R / max(1e-9, math.hypot(x, y))
            x, y = x * k, y * k
        return (x, -y)
    return f


# ---------------------------------------------------------------- geometry
def dp(pts, tol):
    """Douglas-Peucker on a closed ring (the ring is split at its first point and at its farthest point)."""
    if len(pts) < 4:
        return pts

    def rec(a, b):
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1e-12
        best, bi = -1, -1
        for i in range(a + 1, b):
            x, y = pts[i]
            d = abs(dy * (x - x1) - dx * (y - y1)) / L
            if d > best:
                best, bi = d, i
        if best > tol:
            return rec(a, bi)[:-1] + rec(bi, b)
        return [pts[a], pts[b]]
    far = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2)
    return rec(0, far)[:-1] + rec(far, len(pts) - 1)


def area(r):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(r, r[1:] + r[:1]))) / 2


def num(v, nd):
    t = ('%.' + str(nd) + 'f') % v
    if '.' in t:
        t = t.rstrip('0').rstrip('.')
    return '0' if t in ('-0', '') else t


def path(rings, proj, tol, min_area, nd):
    parts, n = [], 0
    for ring in rings:
        pr = [proj(lo, la) for lo, la in ring]
        if pr[0] == pr[-1]:
            pr = pr[:-1]
        if area(pr) < min_area:
            continue
        s = dp(pr, tol)
        if len(s) < 3:
            continue
        # drop consecutive duplicates after rounding
        q = []
        for x, y in s:
            t = (round(x, nd), round(y, nd))
            if not q or t != q[-1]:
                q.append(t)
        parts.append('M' + 'L'.join(num(x, nd) + ',' + num(y, nd) for x, y in q) + 'Z')
        n += len(q)
    return ''.join(parts), n


def bbox(rings, proj):
    xs, ys = [], []
    for ring in rings:
        for lo, la in ring:
            x, y = proj(lo, la)
            xs.append(x)
            ys.append(y)
    return [round(min(xs), 2), round(min(ys), 2), round(max(xs), 2), round(max(ys), 2)]


# ---------------------------------------------------------------- data
cshp = read_shp(os.path.join(GEO, 'cb_2023_us_county_500k', 'cb_2023_us_county_500k.shp'))
cdbf = read_dbf(os.path.join(GEO, 'cb_2023_us_county_500k', 'cb_2023_us_county_500k.dbf'))
sshp = read_shp(os.path.join(GEO, 'cb_2023_us_state_5m', 'cb_2023_us_state_5m.shp'))
sdbf = read_dbf(os.path.join(GEO, 'cb_2023_us_state_5m', 'cb_2023_us_state_5m.dbf'))
county = {(d['STATEFP'], d['COUNTYFP']): (d['NAME'], g) for d, g in zip(cdbf, cshp)}
state = {d['STATEFP']: (d['NAME'], g) for d, g in zip(sdbf, sshp)}

BAY = [('001', 'Alameda'), ('013', 'Contra Costa'), ('041', 'Marin'), ('055', 'Napa'), ('075', 'San Francisco'),
       ('081', 'San Mateo'), ('085', 'Santa Clara'), ('095', 'Solano'), ('097', 'Sonoma')]
SF_C = (-122.4194, 37.7749)   # San Francisco's city centre as usually given (City Hall area); a city, not the lab
NYC_C = (-74.0060, 40.7128)   # New York City's usual centre point

out = {'meta': {
    'units': 'km on the projection plane; x east, y south (SVG y down); origin at each map\'s projection centre',
    'sources': {
        'census': 'US Census Bureau, 2023 Cartographic Boundary Files (cb_2023_us_county_500k, cb_2023_us_state_5m), '
                  'https://www2.census.gov/geo/tiger/GENZ2023/shp/ - US Government work, public domain',
        'naturalearth': 'Natural Earth 1:110m land (ne_110m_land), naturalearthdata.com - public domain',
    },
    'privacy': 'Outlines only. The lab\'s position is never marked; the two points are the usual city centres of '
               'San Francisco and New York, used for the coast-to-coast latency example.',
    'built_by': 'make_geo.py'}}

# San Francisco: the county (= the city), without the Farallon Islands 43 km offshore
name, rings = county[('06', '075')]
sf_rings = [r for r in rings if min(lo for lo, _ in r) > -122.56]
pj = local(37.76, -122.44)
p, n = path(sf_rings, pj, 0.008, 0.001, 3)
out['sf'] = {'name': 'San Francisco (city and county; Farallon Islands left out)', 'projection':
             'local equirectangular at 37.76 N, 122.44 W (distortion < 0.1% over the city)',
             'simplify_km': 0.008, 'points': n, 'bbox_km': bbox(sf_rings, pj), 'path': p}

# the Bay Area: nine counties, each its own path; SF flagged
pj = local(37.9, -122.2)
bay = []
for fips, nm in BAY:
    _, rings = county[('06', fips)]
    if fips == '075':
        rings = [r for r in rings if min(lo for lo, _ in r) > -122.56]
    p, n = path(rings, pj, 0.4, 0.05, 2)
    bay.append({'county': nm, 'fips': '06' + fips, 'points': n, 'path': p})
allr = [r for fips, _ in BAY for r in county[('06', fips)][1] if fips != '075' or min(lo for lo, _ in r) > -122.56]
out['bayarea'] = {'name': 'The San Francisco Bay Area: the nine counties', 'projection':
                  'local equirectangular at 37.9 N, 122.2 W (distortion < 0.3% over the region)',
                  'simplify_km': 0.4, 'bbox_km': bbox(allr, pj), 'counties': bay,
                  'sf_centre_km': [round(v, 2) for v in pj(*SF_C)], 'sf_bbox_km': bbox(sf_rings, pj)}

# California, with the Bay Area's frame for the zoom
pj = albers(34.0, 40.5, 37.2, -119.5)   # California (Teale) Albers standard parallels; origin near the state's middle
_, rings = state['06']
p, n = path(rings, pj, 1.5, 5.0, 1)
bb = bbox(allr, pj)
out['california'] = {'name': 'California', 'projection': 'Albers equal-area conic, standard parallels 34 and 40.5 N, '
                     'origin 37.2 N 119.5 W (Teale parallels), spherical', 'simplify_km': 1.5, 'points': n,
                     'bbox_km': bbox(rings, pj), 'path': p, 'bayarea_bbox_km': bb,
                     'sf_centre_km': [round(v, 1) for v in pj(*SF_C)]}

# the contiguous United States, one path per state (California flagged)
pj = albers(29.5, 45.5, 23.0, -96.0)   # the USGS standard for the lower 48
skip = {'02', '15', '60', '66', '69', '72', '78'}
states, allst = [], []
for fp, (nm, rings) in sorted(state.items()):
    if fp in skip:
        continue
    p, n = path(rings, pj, 9.0, 40.0, 0)
    states.append({'state': nm, 'fips': fp, 'points': n, 'path': p})
    allst += rings
sx, sy = pj(*SF_C)
nx, ny = pj(*NYC_C)
out['us'] = {'name': 'The contiguous United States (the lower 48 and DC)', 'projection':
             'Albers equal-area conic, standard parallels 29.5 and 45.5 N, origin 23 N 96 W (USGS), spherical',
             'simplify_km': 9.0, 'bbox_km': bbox(allst, pj), 'states': states,
             'sf_centre_km': [round(sx), round(sy)], 'nyc_centre_km': [round(nx), round(ny)],
             'california_bbox_km': bbox(state['06'][1], pj)}

# Earth: Natural Earth 110m land on an orthographic globe centred over the United States
with open(os.path.join(GEO, 'ne_110m_land.geojson')) as f:
    land = json.load(f)
pj = ortho(38.0, -100.0)
lr = []
for ft in land['features']:
    g = ft['geometry']
    polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    for poly in polys:
        lr.append([tuple(c) for c in poly[0]])
p, n = path(lr, pj, 40.0, 3000.0, 0)
sx, sy = pj(*SF_C)
out['earth'] = {'name': 'Earth, land (Natural Earth 1:110m)', 'projection': 'orthographic centred on 38 N, 100 W; '
                'far-side points pulled onto the limb; radius %.0f km (NASA mean radius)' % R, 'simplify_km': 40.0,
                'points': n, 'radius_km': R, 'path': p, 'sf_centre_km': [round(sx), round(sy)],
                'us_bbox_km': bbox(allst, pj)}

# great-circle SF - NYC, for the latency example
def gc(a, b):
    (l1, p1), (l2, p2) = [(math.radians(x), math.radians(y)) for x, y in (a, b)]
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin((l2 - l1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))
out['meta']['sf_nyc_great_circle_km'] = round(gc(SF_C, NYC_C), 1)

with open(os.path.join(HERE, '..', 'outside-geo.json'), 'w') as f:
    json.dump(out, f, separators=(',', ':'))
for k in ('sf', 'bayarea', 'california', 'us', 'earth'):
    v = out[k]
    L = len(v.get('path', '')) + sum(len(x['path']) for x in v.get('counties', []) + v.get('states', []))
    print(k, 'path chars', L, 'bbox', v.get('bbox_km'))
print('SF-NYC great circle km', out['meta']['sf_nyc_great_circle_km'])
print('file bytes', os.path.getsize(os.path.join(HERE, '..', 'outside-geo.json')))
