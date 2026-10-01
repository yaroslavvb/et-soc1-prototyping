#!/usr/bin/env python3
"""zoom_static.py PAGE.html : the chip diagram's size and privacy checks (DESIGN §6.2 T9 and T10; the ladder's DESIGN
§5.1 and §5.4 T9, T10, since 1 Oct 2026), on the built page and its folder (ladder-img/ beside it: the images and the
lazily fetched data). Prints PASS or FAIL lines; the exit code is the number of failures.
  T9  the built HTML at most 1.5 MB, its script at most 900 KB (700 before the ladder's inner scales, the ring and the
      two-state electronics; 780 before the owner's second update of 1 Oct, whose textbook constructions, so that every
      part reaches a transistor, add about 36 KB of drawing code; 840 before part 1b's nine scenes for the last dead ends,
      a PCIe lane, a differential pair, a crossbar, rounding, copper wiring, a copper atom, a buck converter, a power
      transistor and a boot pin, and the path-by-path walk the tests read, about 46 KB), its embedded data at most 600 KB, the lazy data (ladder-img/ladder-data.json) at most
      400 KB and as the page's manifest says, the images at most 300 KB in all, each WebP at most 1000 px wide
  T10 no IPv4-like string in the page or the image manifest; no street address, house number, ZIP code or listing link
      for Studio 45, in the page or its data; no latitude or longitude; the rack photo's sha256 equals the manifest's
      (from make_rack_photo.py, ten labels blurred); no EXIF, XMP or ICC in any image; the maps mark no point but the
      usual city centres and the hill's summit; the AI Plumbers event (asked of the owner) is not on the page
  T14 the easter egg (the owner, 1 Oct 2026, 07:25): no level above the rack is named in the page's static text (its
      markup outside scripts and styles) or its description"""
import hashlib
import json
import os
import re
import sys

page = sys.argv[1]
html = open(page, encoding='utf-8').read()
img_dir = os.path.join(os.path.dirname(os.path.abspath(page)), 'ladder-img')
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
ok(len(script.encode()) <= 900e3, f'T9 its script is {len(script.encode()) / 1e3:.0f} KB (at most 900)')
ok(len(data.encode()) <= 600e3, f'T9 its data is {len(data.encode()) / 1e3:.0f} KB (at most 600)')
lz_path = os.path.join(img_dir, 'ladder-data.json')
lz = open(lz_path, encoding='utf-8').read() if os.path.exists(lz_path) else ''
ok(bool(lz) and len(lz.encode()) <= 400e3, f'T9 the lazy data is {len(lz.encode()) / 1e3:.0f} KB (at most 400)')
if D.get('lazy'):
    ok(hashlib.sha256(lz.encode()).hexdigest() == D['lazy'].get('sha256'), 'T9 the lazy data is the build\'s (sha256 as the page says)')
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
links = re.findall(r'(?:https?://)?[^\s"\'<>)]*(?:sfstation|coworkingcafe|lu\.ma|luma\.com|globenewswire|workatthestudio)[^\s"\'<>)]*', html + lz, re.I)
ok(not links, 'T10 no link to a listing or release that shows the address', ' '.join(links[:3]))
both = html + lz
hn = re.findall(r'.{0,40}\b\d{1,5}\s+29th\b.{0,20}', both, re.I)
ok(not hn, 'T10 no house number before 29th', hn[0] if hn else '')
zp = re.findall(r'\b941\d\d(?:-\d{4})?\b', both)
ok(not zp, 'T10 no San Francisco ZIP code', ' '.join(zp[:3]))
# (the usual city centre of San Francisco, which the coast-to-coast fibre example names, is not the lab's)
ll = sorted(set(m.group(0) for m in re.finditer(r'(?<![\d.])-?(?:3[67]|12[12])\.\d{4,}', both)) - {'37.7749', '122.4194'})
ok(not ll, 'T10 no latitude or longitude but the usual city centre', ' '.join(ll[:5]))
ok(not re.search(r'Plumbers', both), 'T10 the AI Plumbers event is not on the page (it waits for the owner)')
# the rack photo is the ten-label copy (since 1 Oct)
man = D.get('img', {})
for f in imgs:
    h = hashlib.sha256(open(os.path.join(img_dir, f), 'rb').read()).hexdigest()
    ok(man.get(f, {}).get('sha256') == h, f'T10 {f}: sha256 matches the manifest', h[:16])
# the San Francisco map: its only point is the usual city centre (the camera arrives at the city's centre)
geo = D.get('geo', {})
pts = {k: v for k, v in geo.get('sf', {}).items() if isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v)}
ok(not pts, 'T10 the city map carries no point of its own', json.dumps(pts))
ok(all(k in ('sf_centre_km', 'nyc_centre_km') for g in geo.values() if isinstance(g, dict) for k in g if k.endswith('centre_km')), 'T10 the maps mark only the two city centres')
bern = geo.get('bernal', {})
bp = [k for k, v in bern.items() if isinstance(v, dict) and 'xy_km' in v]
ok(bp == ['summit'], 'T10 the Bernal Heights map marks one point, the hill\'s summit', ','.join(bp))
ok(not re.search(r'studio', json.dumps(bern), re.I) or 'of the studio' in json.dumps(bern), 'T10 the Bernal Heights map has nothing called a studio')
# T14: the easter egg: the static text (markup outside scripts and styles) and the description
body = re.sub(r'<script\b.*?</script>|<style\b.*?</style>', ' ', html, flags=re.S)
txt = re.sub(r'<[^>]+>', ' ', body)
desc = (re.search(r'<meta name="description" content="([^"]*)"', html) or [None, ''])[1]
HIDDEN = ['Studio 45', 'San Francisco', 'Bernal', '29th Street', 'Bay Area', 'California', 'United States', 'Earth', 'Solar System', 'Milky Way', 'Local Group',
          'Laniakea', 'observable universe', 'Beyond what we can see', 'Ring of sizes', 'Andromeda', 'nearest stars', 'meta universe']
hits = [h for h in HIDDEN if h in txt or h in desc]
ok(not hits, 'T14 no level above the rack is named in the static text or the description', ', '.join(hits))
print(f'{fails} failed')
sys.exit(fails)
