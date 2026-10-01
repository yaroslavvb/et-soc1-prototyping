#!/usr/bin/env python3
"""Make the page copy of the owner's rack photo (30 Sep 2026).

rack-photo-original.webp (1500x1429, no EXIF/GPS, sRGB ICC; outside the repository) -> docs/reports/chip-diagram-img/rack.webp:
  1. redact the machines' tape labels (ten since 1 Oct) (host names and what look like LAN IP addresses; AGENT.md section 10 keeps
     IPs and access details out of public pages): each box is pixelated and blurred so no character survives;
  2. crop the 53-px black band on the left edge;
  3. resize to 1000 px wide (Lanczos), a light 0.5-px Gaussian blur (the carpet's texture is what costs bytes);
  4. WebP q70, method 6, written with no EXIF, XMP or ICC (the source's ICC was plain sRGB).
"""
from PIL import Image, ImageFilter
import hashlib
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
# the original is not in the repository (it shows the labels this script blurs): its path comes from the environment
SRC = os.environ.get('RACK_ORIGINAL') or sys.exit('set RACK_ORIGINAL to the original photo (kept outside the repository)')
OUT = os.path.join(HERE, '..', '..', '..', 'chip-diagram-img', 'rack.webp')
# label boxes in the original's pixel coordinates (x0, y0, x1, y1), found by inspection
LABELS = [
    (165, 215, 222, 318),    # left upright of the upper shelf: name + address
    (593, 238, 648, 332),    # two labels on the black box behind the MSI supply
    (603, 352, 702, 452),    # diagonal label by the MSI supply: name + address
    (878, 238, 932, 292),    # small label on the second black box
    (1203, 258, 1302, 347),  # label on the machine behind supply 4
    (1453, 203, 1500, 238),  # small label on the far-right cooler
    (276, 853, 330, 968),    # lower shelf, left upright: name + address
    (810, 733, 897, 848),    # lower shelf: frame name
    (1050, 925, 1120, 978),  # lower shelf's front rail, under the 650 GS supply: a host-name strip (added 30 Sep, the
                             # design's review: legible in the original, only blurred by the downscale in the first copy)
    (50, 672, 118, 708),     # upper shelf, front left: a "KVM #" port label (added 1 Oct, the final check: legible in the
                             # page copy, and the page says the machine labels are blurred)
]


def redact(im, box):
    x0, y0, x1, y1 = box
    reg = im.crop(box)
    w, h = reg.size
    small = reg.resize((max(1, w // 8), max(1, h // 8)), Image.BILINEAR)
    reg = small.resize((w, h), Image.NEAREST).filter(ImageFilter.GaussianBlur(4))
    im.paste(reg, (x0, y0))


im = Image.open(SRC).convert('RGB')
for b in LABELS:
    redact(im, b)
im = im.crop((53, 0, im.width, im.height))
W = 1000
H = round(im.height * W / im.width)
im = im.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.5))
im.save(OUT, 'WEBP', quality=70, method=6)
print(OUT, im.size, os.path.getsize(OUT), 'sha256', hashlib.sha256(open(OUT, 'rb').read()).hexdigest())
