#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pillow"]
# ///
"""make_refs.py: the reference pictures that pin a generated picture's geometry (31 Oct 2026).

    ./make_refs.py      # writes refs/earth-ref.png

refs/earth-ref.png is the chip diagram's own globe (Natural Earth 1:110m land, orthographic at 38 N 100 W: the chip
diagram's research/outside-geo.json "earth", which the page drew until 31 Oct 2026), green land on a blue disc on black,
the disc 88% of a 1024 px square. Antigravity is asked to paint Earth over exactly this map, so that the globe the page shows
still lines up with the United States map the camera zooms into (the zoom nests the US map in the globe's US box).
"""
import json
import os
import re

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = os.path.join(HERE, '..', '..', '2026-09-27-chip-diagram', 'research', 'outside-geo.json')
N, FRAC = 1024, 0.88


def main():
    g = json.load(open(GEO))['earth']
    R = g['radius_km']
    k = N * FRAC / 2 / R
    im = Image.new('RGB', (N, N), (0, 0, 0))
    d = ImageDraw.Draw(im)
    c = N / 2
    d.ellipse([c - R * k, c - R * k, c + R * k, c + R * k], fill=(31, 78, 140))
    for sub in re.findall(r'M[^M]+', g['path']):
        pts = [(c + float(x) * k, c + float(y) * k) for x, y in re.findall(r'(-?[\d.]+),(-?[\d.]+)', sub)]
        if len(pts) >= 3:
            d.polygon(pts, fill=(58, 125, 68))
    os.makedirs(os.path.join(HERE, 'refs'), exist_ok=True)
    out = os.path.join(HERE, 'refs', 'earth-ref.png')
    im.save(out)
    print(out, f'disc radius {R * k:.1f} px of {N}')


if __name__ == '__main__':
    main()
