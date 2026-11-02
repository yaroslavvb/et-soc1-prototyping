#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pillow", "numpy"]
# ///
"""make_webp.py: the generated pictures as the page's WebP files (31 Oct 2026).

    ./make_webp.py                  # every picture of prompts.json whose take exists
    ./make_webp.py --only stars     # one (comma-separate several)
    ./make_webp.py --measure universe   # print where the light is: centroid, and radii holding 50/90/98% of it

Each take (~/.cache/agy-raw/ladder-img/<id>.png, or <id>-<take>.png when prompts.json names a "take") is put on the
page's night sky: screen-blended over #070b17, the colour of the space levels' backdrop and of the particle scenes'
window, so its black edges are exactly the sky's and no seam shows; then scaled to its "width" and written to
docs/reports/ladder-img/<file> as WebP (quality "q", default 70), with no EXIF, XMP or ICC (zoom_static.py T10).
"""
import argparse
import json
import os
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
RAW = Path.home() / '.cache' / 'agy-raw' / 'ladder-img'
OUT = HERE.parent.parent.parent / 'ladder-img'
SKY = np.array([7, 11, 23], dtype=np.float32) / 255


def take_of(item):
    return RAW / (item['id'] + (f'-{item["take"]}' if item.get('take') else '') + '.png')


def on_sky(im):
    a = np.asarray(im.convert('RGB'), dtype=np.float32) / 255
    out = 1 - (1 - a) * (1 - SKY)
    return Image.fromarray(np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))


def measure(item):
    im = Image.open(take_of(item)).convert('L')
    a = np.asarray(im, dtype=np.float64)
    a = np.clip(a - np.percentile(a, 5), 0, None)
    h, w = a.shape
    ys, xs = np.mgrid[0:h, 0:w]
    s = a.sum()
    cx, cy = (a * xs).sum() / s, (a * ys).sum() / s
    r = np.hypot(xs - cx, ys - cy).ravel()
    order = np.argsort(r)
    cum = np.cumsum(a.ravel()[order]) / s
    rad = {p: r[order][np.searchsorted(cum, p / 100)] for p in (50, 90, 98)}
    print(f'{item["id"]}: {w}x{h}, light centroid ({cx / w:.3f}, {cy / h:.3f}) of the frame; radii holding 50/90/98% of the light: '
          + ', '.join(f'{rad[p] / w:.3f}' for p in (50, 90, 98)) + ' of the width')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only')
    ap.add_argument('--measure')
    args = ap.parse_args()
    spec = json.loads((HERE / 'prompts.json').read_text())
    items = {i['id']: i for i in spec['images']}
    if args.measure:
        for k in args.measure.split(','):
            measure(items[k])
        return
    wanted = set(args.only.split(',')) if args.only else None
    for item in spec['images']:
        if wanted and item['id'] not in wanted:
            continue
        src = take_of(item)
        if not src.exists():
            print(f'{item["id"]}: no take yet ({src})')
            continue
        im = Image.open(src)
        if item.get('crop'):
            x0, y0, x1, y1 = item['crop']
            im = im.crop((round(x0 * im.width), round(y0 * im.height), round(x1 * im.width), round(y1 * im.height)))
        im = on_sky(im)
        w = item.get('width', 900)
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        dst = OUT / item['file']
        im.save(dst, 'WEBP', quality=item.get('q', 70), method=6)
        print(f'{item["id"]}: {src.name} -> {dst.name} {im.width}x{im.height}, {os.path.getsize(dst) / 1000:.0f} KB')


if __name__ == '__main__':
    main()
