#!/usr/bin/env bash
# render_text.sh <page.html> <out-prefix> : write <out-prefix>.txt (visible text after scripts run) and <out-prefix>.json (headings, ids, links)
# CHROME_HEADLESS overrides the browser (default: Playwright's chrome-headless-shell).
set -e
f=$(readlink -f "$1"); out="$2"
HS=${CHROME_HEADLESS:-$HOME/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell}
t=$(mktemp -d); trap 'rm -rf "$t"' EXIT; cp "$f" $t/page.html
python3 - $t/page.html <<'PY'
import sys
p=sys.argv[1]; s=open(p,encoding='utf-8',errors='replace').read()
js="""<script>window.addEventListener('load',()=>setTimeout(()=>{const o={title:document.title};
o.ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
o.headings=[...document.querySelectorAll('h1,h2,h3')].map(h=>({tag:h.tagName,id:h.id,text:h.textContent.replace(/#$/,'').trim()}));
o.links=[...document.querySelectorAll('a[href]')].map(a=>({href:a.getAttribute('href'),text:a.textContent.trim().slice(0,120)}));
const pre=document.createElement('pre');pre.id='__probe';pre.textContent=JSON.stringify(o);document.body.appendChild(pre);
const t=document.createElement('pre');t.id='__text';t.textContent=document.body.innerText;document.body.appendChild(t);},800));</script>"""
i=s.rfind('</body>'); s=s[:i]+js+s[i:] if i>=0 else s+js
open(p,'w').write(s)
PY
timeout 120 "$HS" --headless --no-sandbox --disable-gpu --virtual-time-budget=6000 --window-size=1280,900 --dump-dom file://$t/page.html 2>/dev/null > $t/dom
python3 - $t/dom "$out" <<'PY'
import sys,re,html
s=open(sys.argv[1],encoding='utf-8',errors='replace').read()
g=lambda i:(lambda m: html.unescape(m.group(1)) if m else '')(re.search(r'<pre id="%s">(.*?)</pre>'%i,s,re.S))
open(sys.argv[2]+'.json','w').write(g('__probe')); open(sys.argv[2]+'.txt','w').write(g('__text'))
PY
