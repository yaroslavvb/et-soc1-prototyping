#!/usr/bin/env python3
"""zoom_static.py PAGE.html : the chip diagram's size and privacy checks (DESIGN §6.2 T9 and T10), on the built page
and its images folder (chip-diagram-img/ beside it). Prints PASS or FAIL lines; the exit code is the number of
failures.
  T9  the built HTML at most 1.5 MB, its script at most 650 KB, its embedded data at most 750 KB, the images at most
      300 KB in all, each WebP at most 1000 px wide
  T10 no IPv4-like string in the page or the image manifest; no street address or listing link for Studio 45; the
      rack photo's sha256 equals the manifest's (from make_rack_photo.py, nine labels blurred); no EXIF, XMP or ICC
      in any image; the San Francisco map marks no point but the usual city centre"""
import hashlib
import json
import os
import re
import sys

page = sys.argv[1]
html = open(page, encoding='utf-8').read()
img_dir = os.path.join(os.path.dirname(os.path.abspath(page)), 'chip-diagram-img')
fails = 0


def ok(c, what, extra=''):
    global fails
    fails += 0 if c else 1
    print(('PASS ' if c else 'FAIL ') + what + ('  ' + extra if extra else ''))


m = re.search(r'const D = (\{.*?\});\n', html, re.S)
data = m.group(1)
D = json.loads(data)
script = html[m.end():html.index('</script>', m.end())]
ok(len(html.encode()) <= 1.5e6, f'T9 the page is {len(html.encode()) / 1e6:.2f} MB (at most 1.5)')
ok(len(script.encode()) <= 650e3, f'T9 its script is {len(script.encode()) / 1e3:.0f} KB (at most 650)')
ok(len(data.encode()) <= 750e3, f'T9 its data is {len(data.encode()) / 1e3:.0f} KB (at most 750)')
imgs = sorted(f for f in os.listdir(img_dir) if f.endswith('.webp'))
tot = sum(os.path.getsize(os.path.join(img_dir, f)) for f in imgs)
ok(tot <= 300e3, f'T9 {len(imgs)} images, {tot / 1e3:.0f} KB (at most 300)')
try:
    from PIL import Image
    for f in imgs:
        im = Image.open(os.path.join(img_dir, f))
        meta = [k for k in ('exif', 'icc_profile', 'xmp', 'XML:com.adobe.xmp') if k in im.info]
        ok(im.width <= 1000 and not meta, f'T9/T10 {f}: {im.width} px wide, no metadata', ','.join(meta))
except ImportError:
    ok(False, 'T10 Pillow is needed to read the images\' metadata')
# no IPv4-like strings (version strings like 1.2.3.4 would be listed: none are expected)
# (a manual's section numbers, "\u00a72.1.3.1" in the data, are not addresses)
ips = sorted(set(m.group(0) for m in re.finditer(r'(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])', html)
                 if not re.search(r'(u00a7|§|section |sec\. )\d?$', html[max(0, m.start() - 8):m.start() + 1])))
ok(not ips, 'T10 no IPv4-like string in the page', ' '.join(ips[:8]))
ok(not re.search(r'\b10\.\d+\.\d+\.\d+\b|\b192\.168\.\d+\.\d+\b|\b100\.(6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d+\.\d+\b', html), 'T10 no private or Tailscale address')
# Studio 45: no street address, no links to its listings
s45 = re.findall(r'.{0,120}Studio 45.{0,160}', html)
addr = [x for x in s45 if re.search(r'\b\d{2,5}\s+[A-Z][a-z]+\s+(St|Street|Ave|Avenue|Blvd|Rd|Road|Way)\b', x)]
ok(not addr, 'T10 no street address beside Studio 45', addr[0][:120] if addr else '')
links = re.findall(r'https?://[^\s"\'<>)]*(?:sfstation|coworkingcafe|lu\.ma|luma)[^\s"\'<>)]*', html, re.I)
ok(not links, 'T10 no link to a listing that shows the address', ' '.join(links[:3]))
# the rack photo is the nine-label copy
man = D.get('img', {})
for f in imgs:
    h = hashlib.sha256(open(os.path.join(img_dir, f), 'rb').read()).hexdigest()
    ok(man.get(f, {}).get('sha256') == h, f'T10 {f}: sha256 matches the manifest', h[:16])
# the San Francisco map: its only point is the usual city centre (the camera arrives at the city's centre)
geo = D.get('geo', {})
pts = {k: v for k, v in geo.get('sf', {}).items() if isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v)}
ok(not pts, 'T10 the city map carries no point of its own', json.dumps(pts))
ok(all(k in ('sf_centre_km', 'nyc_centre_km') for g in geo.values() if isinstance(g, dict) for k in g if k.endswith('centre_km')), 'T10 the maps mark only the two city centres')
print(f'{fails} failed')
sys.exit(fails)
