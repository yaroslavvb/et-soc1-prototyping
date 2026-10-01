# Elevation profile of 29th Street (the whole street, west end to east end) from the USGS 3DEP 1 m DEM (EPQS).
# Prints only distances along the street and elevations, no coordinates.
import os, json, math, urllib.request, concurrent.futures as cf
st = json.load(open(os.path.join(os.environ.get('LADDER_RAW', '.'), 'st29.json')))
segs = [s['line']['coordinates'] for s in st]
pts = []
for s in segs: pts += s
lat0 = 37.75; mx = 111320*math.cos(math.radians(lat0)); my = 111320
# order segments west to east by their mean longitude, orient each west->east
segs = sorted(segs, key=lambda s: sum(p[0] for p in s)/len(s))
segs = [s if s[0][0] <= s[-1][0] else s[::-1] for s in segs]
samples = []; dist = 0.0
for s in segs:
    for a, b in zip(s, s[1:]):
        L = math.hypot((b[0]-a[0])*mx, (b[1]-a[1])*my)
        n = max(1, int(L // 40))
        for k in range(n):
            t = k/n
            samples.append((dist + t*L, a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])))
        dist += L
samples.append((dist, segs[-1][-1][0], segs[-1][-1][1]))
def q(p):
    u = f"https://epqs.nationalmap.gov/v1/json?x={p[1]:.7f}&y={p[2]:.7f}&units=Meters&wkid=4326"
    for _ in range(3):
        try: return float(json.load(urllib.request.urlopen(u, timeout=30))['value'])
        except Exception: pass
    return float('nan')
with cf.ThreadPoolExecutor(8) as ex: z = list(ex.map(q, samples))
prof = [(round(d), round(e, 1)) for (d, _, _), e in zip(samples, z)]
print('length m', round(dist), 'samples', len(prof))
print('west end m', prof[0][1], 'east end m', prof[-1][1], 'max', max(e for _, e in prof), 'min', min(e for _, e in prof))
print(prof)
