#!/usr/bin/env python3
"""Bernal Heights and 29th Street, for the chip diagram's outside levels between San Francisco and Studio 45.

Writes bernal-geo-full.json into the raw directory (LADDER_RAW, or the first argument; not committed: 299 KB), which
simplify_bernal_geo.py clips and simplifies into the committed bernal-geo.json. It needs the Analysis Neighborhoods
download (analysis-neighborhoods.geojson, DataSF j2bu-swwd) in that directory, and the network for the rest. SVG path
data in km, the same projection and origin as outside-geo.json's "sf" map: local
equirectangular at 37.76 N, 122.44 W, x east, y SOUTH) and preview-bernal.png.

Sources (all public domain, Open Data Commons PDDL, City and County of San Francisco, DataSF):
  - Analysis Neighborhoods (j2bu-swwd): the 41 neighbourhoods the city's Department of Public Health and Mayor's
    Office of Housing built from 2010 census tracts, with Planning's support ("NOT an official map").
  - Streets - Active and Retired (3psu-pn9h): Public Works street centrelines.
  - Recreation and Parks Properties (gtr9-ntp6): Bernal Heights Park's outline and acreage.
  - USGS GNIS 1658039 (Bernal Heights, the hill's summit point) and USGS 3DEP 1 m DEM via the Elevation Point Query
    Service (epqs_summit.py): the summit's ground elevation.

Privacy (AGENT.md; the owner's words of 1 Oct 2026 give only "29th Street, in Bernal Heights"): this file draws the
whole of 29th Street and the neighbourhood outlines. It never marks the studio, a block, a house number or a point
on the street. The hill's summit is a public landmark, not the lab.
"""
import json
import math
import os
import urllib.parse
import urllib.request

import sys
HERE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('LADDER_RAW', '.')
R = 6371.0
LAT0, LON0 = 37.76, -122.44          # outside-geo.json's "sf" projection origin (make_geo.py)
C = math.cos(math.radians(LAT0))


def pj(lon, lat):
    return (R * C * math.radians(lon - LON0), -R * math.radians(lat - LAT0))


def soql(dataset, where, select=None, limit=2000):
    q = {'$where': where, '$limit': limit}
    if select:
        q['$select'] = select
    u = f'https://data.sf.gov/resource/{dataset}.json?' + urllib.parse.urlencode(q)
    return json.load(urllib.request.urlopen(u, timeout=120))


def ring_area(r):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(r, r[1:] + r[:1]))) / 2


def fmt(v):
    t = '%.3f' % v
    t = t.rstrip('0').rstrip('.')
    return '0' if t in ('-0', '') else t


def poly_path(rings):
    out = []
    for ring in rings:
        pts = [pj(*p) for p in ring]
        if pts[0] == pts[-1]:
            pts = pts[:-1]
        out.append('M' + 'L'.join(fmt(x) + ',' + fmt(y) for x, y in pts) + 'Z')
    return ''.join(out)


def line_path(coords):
    pts = [pj(*p) for p in coords]
    return 'M' + 'L'.join(fmt(x) + ',' + fmt(y) for x, y in pts)


def line_len_km(coords):
    pts = [pj(*p) for p in coords]
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def rings_of(geom):
    polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    return polys


# ---------------------------------------------------------------- neighbourhoods
an = json.load(open(os.path.join(HERE, 'analysis-neighborhoods.geojson')))
by = {f['properties']['nhood']: f['geometry'] for f in an['features']}
bern = rings_of(by['Bernal Heights'])
b_area = sum(ring_area([pj(*p) for p in poly[0]]) - sum(ring_area([pj(*p) for p in h]) for h in poly[1:]) for poly in bern)
bx = [pj(*p)[0] for poly in bern for p in poly[0]]
byy = [pj(*p)[1] for poly in bern for p in poly[0]]
bbox = [min(bx), min(byy), max(bx), max(byy)]
lon_b = [p[0] for poly in bern for p in poly[0]]
lat_b = [p[1] for poly in bern for p in poly[0]]
pad = 0.012   # degrees, about 1 km: the frame around the neighbourhood
nw = (max(lat_b) + pad, min(lon_b) - pad * 1.3)
se = (min(lat_b) - pad, max(lon_b) + pad * 1.3)

neigh = {}
for name, g in by.items():
    pts = [p for poly in rings_of(g) for p in poly[0]]
    if any(se[0] <= la <= nw[0] and nw[1] <= lo <= se[1] for lo, la in pts):
        neigh[name] = poly_path([poly[0] for poly in rings_of(g)])

# ---------------------------------------------------------------- streets
box = f'within_box(line, {nw[0]}, {nw[1]}, {se[0]}, {se[1]})'
major = soql('3psu-pn9h', f"active=true AND classcode in ('1','2','3') AND {box}", select='streetname,classcode,line')
named = soql('3psu-pn9h', f"active=true AND streetname in ('CORTLAND AVE','BERNAL HEIGHTS BLVD') AND {box}",
             select='streetname,classcode,line')
st29 = soql('3psu-pn9h', "active=true AND street='29TH' AND st_type='ST'",
            select='streetname,analysis_neighborhood,line')
roads = {}
for s in major + named:
    roads.setdefault(s['streetname'], []).append(line_path(s['line']['coordinates']))
st29_len = sum(line_len_km(s['line']['coordinates']) for s in st29)
st29_by = {}
for s in st29:
    k = s.get('analysis_neighborhood')
    st29_by[k] = st29_by.get(k, 0) + line_len_km(s['line']['coordinates'])

# ---------------------------------------------------------------- the park and the summit
park = soql('gtr9-ntp6', "property_name='Bernal Heights Park'")[0]
park_path = poly_path([poly[0] for poly in rings_of(park['shape'])])
SUMMIT = (-122.4158042, 37.7429861)   # USGS GNIS 1658039, "Bernal Heights" (summit), a public landmark
sx, sy = pj(*SUMMIT)

out = {
    'meta': {
        'projection': 'local equirectangular at 37.76 N, 122.44 W, km, x east, y south (as outside-geo.json "sf")',
        'sources': [
            'DataSF Analysis Neighborhoods (j2bu-swwd), ODC-PDDL',
            'DataSF Streets - Active and Retired (3psu-pn9h), ODC-PDDL',
            'DataSF Recreation and Parks Properties (gtr9-ntp6), ODC-PDDL',
            'USGS GNIS 1658039; USGS 3DEP 1 m DEM (EPQS), lidar of 4 Mar 2023',
        ],
        'privacy': 'No point, block or address of the studio: the whole of 29th Street and the outlines only.',
    },
    'bernal': {'path': poly_path([poly[0] for poly in bern]), 'area_km2': round(b_area, 3),
               'bbox_km': [round(v, 3) for v in bbox],
               'size_km': [round(bbox[2] - bbox[0], 2), round(bbox[3] - bbox[1], 2)]},
    'neighbours': neigh,
    'park': {'path': park_path, 'acres': round(float(park['acres']), 1),
             'ha': round(float(park['acres']) * 0.40468564224, 2)},
    'summit': {'xy_km': [round(sx, 3), round(sy, 3)], 'ground_m': 142.0, 'ground_ft': 466},
    'st29': {'path': ''.join(line_path(s['line']['coordinates']) for s in st29), 'length_km': round(st29_len, 3),
             'length_by_analysis_neighbourhood_km': {k: round(v, 3) for k, v in st29_by.items()}},
    'roads': {k: ''.join(v) for k, v in roads.items()},
}
with open(os.path.join(HERE, 'bernal-geo-full.json'), 'w') as f:
    json.dump(out, f, separators=(',', ':'))
print('bernal area km2', out['bernal']['area_km2'], 'size km', out['bernal']['size_km'])
print('29th St km', out['st29']['length_km'], out['st29']['length_by_analysis_neighbourhood_km'])
print('park acres', out['park']['acres'], 'ha', out['park']['ha'])
print('neighbours', sorted(neigh))
print('roads', sorted(roads))
print('bytes', os.path.getsize(os.path.join(HERE, 'bernal-geo-full.json')))

# ---------------------------------------------------------------- preview (optional)
if os.environ.get('PREVIEW') != '1':
    sys.exit(0)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch


def mpath(d):
    verts, codes = [], []
    for seg in d.replace('Z', ' Z ').replace('M', ' M ').replace('L', ' L ').split():
        if seg in ('M', 'L'):
            cur = MPath.MOVETO if seg == 'M' else MPath.LINETO
        elif seg == 'Z':
            verts.append(verts[-1]); codes.append(MPath.CLOSEPOLY)
        else:
            x, y = map(float, seg.split(','))
            verts.append((x, -y)); codes.append(cur)
    return MPath(verts, codes)


fig, ax = plt.subplots(figsize=(8, 8))
for name, d in neigh.items():
    ax.add_patch(PathPatch(mpath(d), fc='none', ec='#999', lw=0.6))
ax.add_patch(PathPatch(mpath(out['bernal']['path']), fc='#f3e3c8', ec='#a0522d', lw=1.5))
ax.add_patch(PathPatch(mpath(park_path), fc='#cfe3c0', ec='#4a7a32', lw=0.8))
for k, d in out['roads'].items():
    ax.add_patch(PathPatch(mpath(d), fc='none', ec='#555', lw=1.0 if 'HWY' in k or 'I-280' in k else 0.7))
ax.add_patch(PathPatch(mpath(out['st29']['path']), fc='none', ec='#c0392b', lw=2.2))
ax.plot([sx], [-sy], '^', color='#4a7a32')
ax.set_xlim(bbox[0] - 1.2, bbox[2] + 0.6)
ax.set_ylim(-bbox[3] - 0.6, -bbox[1] + 0.8)
ax.set_aspect('equal')
ax.set_title('Bernal Heights (fill), its park, 29th Street (red, whole street); km')
fig.savefig(os.path.join(HERE, 'preview-bernal.png'), dpi=90)
