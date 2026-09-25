#!/usr/bin/env bash
# shot.sh <page.html> <out-prefix> [width=1280] : full-page screenshot after scripts run, cut into <out-prefix>-N.png
# pieces of at most 1400 px tall (so each can be viewed); prints the piece names. Interaction states are not
# supported; use a copy of the page with a small script for those.
# DARK=1 renders with document.documentElement.dataset.theme='dark'; DARK=os emulates the OS dark preference
# (prefers-color-scheme: dark) instead, which checks the page's @media rules.
# CHROME_HEADLESS overrides the browser (default: Playwright's chrome-headless-shell).
set -e
f=$(readlink -f "$1"); out="$2"; w=${3:-1280}
HS=${CHROME_HEADLESS:-$HOME/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell}
FLAGS=(); [ "${DARK:-}" = os ] && FLAGS=(--blink-settings=preferredColorScheme=0)
t=$(mktemp -d); trap 'rm -rf "$t"' EXIT
cp "$f" $t/page.html; for g in "$(dirname "$f")"/*.gif; do [ -e "$g" ] && cp "$g" $t/; done
python3 - $t/page.html <<'PY'
import os, re, sys
p = sys.argv[1]; s = open(p, encoding='utf-8', errors='replace').read()
if os.environ.get('DARK', '') not in ('', 'os', '0'):
    m = re.search(r'<head(?:\s[^>]*)?>', s, re.I)
    dk = "<script>document.documentElement.dataset.theme='dark'</script>"
    s = s[:m.end()] + dk + s[m.end():] if m else dk + s
js = "<script>window.addEventListener('load',()=>setTimeout(()=>{document.title='H='+document.documentElement.scrollHeight},900));</script>"
i = s.rfind('</body>'); s = s[:i] + js + s[i:] if i >= 0 else s + js
open(p, 'w').write(s)
PY
H=$(timeout 120 "$HS" --headless --no-sandbox --disable-gpu "${FLAGS[@]}" --virtual-time-budget=6000 --window-size=$w,900 --dump-dom file://$t/page.html 2>/dev/null | grep -o '<title>H=[0-9]*' | grep -o '[0-9]*$' || true)
H=${H:-4000}; [ $H -gt 30000 ] && H=30000
timeout 180 "$HS" --headless --no-sandbox --disable-gpu --hide-scrollbars "${FLAGS[@]}" --virtual-time-budget=6000 --window-size=$w,$((H+40)) --screenshot=$t/full.png file://$t/page.html >/dev/null 2>&1
python3 - $t/full.png "$out" <<'PY'
import sys
from PIL import Image
im = Image.open(sys.argv[1]); W, H = im.size; n = 0
for y in range(0, H, 1400):
    im.crop((0, y, W, min(H, y + 1400))).save(f"{sys.argv[2]}-{n}.png"); print(f"{sys.argv[2]}-{n}.png"); n += 1
PY
