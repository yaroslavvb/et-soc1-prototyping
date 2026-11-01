#!/usr/bin/env python3
"""Fetch the public-domain input images for Q132(r): NASA's image library (images-api.nasa.gov), NASA media are not
copyrighted under US law (NASA Media Usage Guidelines). Writes <dir>/<nasa_id>.jpg and <dir>/manifest-images.json."""
import hashlib, json, os, subprocess, sys, urllib.request
OUT = sys.argv[1]
IDS = ["KSC-20200914-PH-JBS01_0019", "KSC-06pd0814", "KSC-20210121-PH-JBS01_0143", "KSC-04pd0049", "KSC-04pd0044",
       "KSC-03pd2984", "KSC-03pd2363", "201102240008HQ", "201002060005HQ", "KSC-20170424-PH_SWW01_0007", "9906393",
       "KSC-20210226-PH-CMS01_0072", "KSC-20210226-PH-JBS01_0081", "KSC-2014-1790", "KSC-2014-1792", "05pd1821",
       "KSC-08pd2105", "KSC-08pd4026", "KSC-2013-3232", "AFRC2018-0067-24", "KSC-20190823-PH_CSH01_0010",
       "KSC-20190823-PH_CSH01_0004", "KSC-20190330-PH_JBS01_0063", "KSC-20190330-PH_JBS01_0048",
       "KSC-20190710-PH_KLS02_0051", "NHQ201805030036", "PIA03880", "PIA03462",
       "KSC-20170412-PH_SWW01_0055", "KSC-20201013-PH-JBS02_0017", "KSC-20200827-PH-JBS01_0035", "KSC-20220516-PH-JBS01_0072"]
os.makedirs(OUT, exist_ok=True)
man = {}
for i in IDS:
    assets = json.load(urllib.request.urlopen(f"https://images-api.nasa.gov/asset/{i}", timeout=60))
    hrefs = [x["href"] for x in assets["collection"]["items"]]
    pick = None
    for suffix in ("~medium.jpg", "~large.jpg", "~orig.jpg", "~small.jpg"):
        c = [h for h in hrefs if h.lower().endswith(suffix)]
        if c:
            pick = c[0].replace("http://", "https://")
            break
    if pick is None:
        print("no jpg for", i, hrefs[:4], flush=True)
        continue
    pick = pick.replace(" ", "%20")
    out = os.path.join(OUT, i + ".jpg")
    if not os.path.exists(out):
        subprocess.run(["curl", "-sS", "-L", "--fail", "--retry", "3", "--max-time", "180", "-o", out, pick], check=True)
    d = open(out, "rb").read()
    meta = json.load(urllib.request.urlopen(f"https://images-api.nasa.gov/search?nasa_id={i}", timeout=60))["collection"]["items"]
    m = meta[0]["data"][0] if meta else {}
    man[i] = {"url": pick, "bytes": len(d), "sha256": hashlib.sha256(d).hexdigest(), "title": m.get("title"),
              "center": m.get("center"), "date_created": m.get("date_created")}
    print(i, len(d), man[i]["sha256"][:12], pick.rsplit("/", 1)[1], flush=True)
json.dump({"licence": "NASA images: not copyrighted under US law (NASA Media Usage Guidelines, nasa.gov/nasa-brand-center/images-and-media); fetched from images-assets.nasa.gov", "images": man},
          open(os.path.join(OUT, "manifest-images.json"), "w"), indent=1)
print("DONE images", len(man))
