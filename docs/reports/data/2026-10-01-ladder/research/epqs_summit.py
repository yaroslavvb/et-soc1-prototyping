# Sample the USGS 3DEP 1 m DEM (EPQS) around the GNIS summit point of Bernal Heights to find its highest ground.
import json, math, urllib.request, concurrent.futures as cf
lat0, lon0 = 37.7429861, -122.4158042   # GNIS 1658039 (the hill's summit, public)
def q(lat, lon):
    u = f"https://epqs.nationalmap.gov/v1/json?x={lon:.7f}&y={lat:.7f}&units=Meters&wkid=4326"
    for _ in range(3):
        try:
            return float(json.load(urllib.request.urlopen(u, timeout=30))["value"])
        except Exception:
            pass
    return float("nan")
def grid(lat0, lon0, half, step):
    mlat = 111320.0; mlon = 111320.0*math.cos(math.radians(lat0))
    pts = []
    n = int(half/step)
    for i in range(-n, n+1):
        for j in range(-n, n+1):
            pts.append((i*step, j*step, lat0 + i*step/mlat, lon0 + j*step/mlon))
    with cf.ThreadPoolExecutor(8) as ex:
        vals = list(ex.map(lambda p: q(p[2], p[3]), pts))
    return sorted(zip(vals, pts), key=lambda t: -t[0] if t[0]==t[0] else 1e9)
r = grid(lat0, lon0, 80, 10)
print("coarse top 5:", [(round(v,2), p[0], p[1]) for v,p in r[:5]])
v, p = r[0]
r2 = grid(p[2], p[3], 8, 2)
print("fine top 5:", [(round(v,2), p[0], p[1]) for v,p in r2[:5]])
print("max ground (m):", round(r2[0][0],2), "ft:", round(r2[0][0]/0.3048,1))
