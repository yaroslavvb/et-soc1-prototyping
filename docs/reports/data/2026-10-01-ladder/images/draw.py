#!/usr/bin/env python3
"""draw.py: draw the deep zoom's pictures with Antigravity (`agy -p`) from prompts.json (31 Oct 2026).

    python3 draw.py                      # every picture not yet drawn
    python3 draw.py --only universe      # just one (comma-separate several)
    python3 draw.py --only proton --force --tag b   # draw again, keeping the earlier take as <id>.png

Each picture lands, full size, in ~/.cache/agy-raw/ladder-img/<id>[-<tag>].png (out of git and Dropbox); make_webp.py
turns the chosen take into the page's WebP. agy must be signed in on this machine (flush-util `agy_signin --check`).
One picture at a time: agy's own output folder is shared, and the fallback below takes the newest picture in it.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRAIN = Path.home() / '.gemini' / 'antigravity-cli' / 'brain'
RAW = Path.home() / '.cache' / 'agy-raw' / 'ladder-img'
IMG_EXT = {'.png', '.jpg', '.jpeg', '.webp'}


def images_since(t0):
    found = [p for p in BRAIN.rglob('*') if p.suffix.lower() in IMG_EXT and p.is_file() and p.stat().st_mtime >= t0]
    return sorted(found, key=lambda p: p.stat().st_mtime)


def draw(item, style, raw):
    raw.unlink(missing_ok=True)
    ref = ''
    if item.get('ref'):
        ref = (f' Reference image: pass the local file {HERE / item["ref"]} to the image generator as the reference picture, '
               'and follow its geometry exactly.')
    ask = ('Use your image generation tool (the image-generator subagent, with model pro) to create exactly one image, then '
           f'save it as a PNG file at {raw} . Do not ask questions, do not create any other files, and reply with only the '
           f'saved path. Image description: {item["prompt"]} Style: {style}{ref}')
    t0 = time.time()
    run = subprocess.run(['agy', '-p', ask, '--print-timeout', '300s'], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=420)
    took = time.time() - t0
    if raw.exists():
        return raw, took, run
    fresh = images_since(t0)
    if fresh:
        raw.write_bytes(fresh[-1].read_bytes())
        return raw, took, run
    return None, took, run


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', help='comma-separated picture ids')
    ap.add_argument('--force', action='store_true', help='draw again even if a take exists')
    ap.add_argument('--tag', default='', help='a suffix for this take (keeps earlier takes)')
    args = ap.parse_args()
    spec = json.loads((HERE / 'prompts.json').read_text())
    wanted = set(args.only.split(',')) if args.only else None
    RAW.mkdir(parents=True, exist_ok=True)
    failed = 0
    for item in spec['images']:
        if wanted and item['id'] not in wanted:
            continue
        tag = args.tag or item.get('take', '')   # (prompts.json's "take" names the chosen take, as make_webp.py reads it)
        raw = RAW / (item['id'] + (f'-{tag}' if tag else '') + '.png')
        if raw.exists() and not args.force:
            print(f'{item["id"]}: already drawn ({raw})', flush=True)
            continue
        src, took, run = draw(item, spec['style'][item['style']], raw)
        if not src:
            failed += 1
            print(f'{item["id"]}: NO IMAGE after {took:.0f} s (agy exit {run.returncode})', flush=True)
            print('  stdout:', run.stdout.strip()[-400:], flush=True)
            print('  stderr:', run.stderr.strip()[-400:], flush=True)
            continue
        print(f'{item["id"]}: drawn in {took:.0f} s -> {src}', flush=True)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
