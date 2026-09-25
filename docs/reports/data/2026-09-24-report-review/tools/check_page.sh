#!/usr/bin/env bash
# check_page.sh <page.html> : render a report at 1280 and 390 px after its scripts run, and print problems.
# Reports: JS errors, empty computed fields, sideways overflow, in-page links to missing ids, h2/h3 without ids,
# whether a contents list, a "Related reports" heading and a link back to the hub exist.
set -e
f=$(readlink -f "$1"); A=${AUDIT_DIR:-/tmp/report-review}
HS=~/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
t=$(mktemp -d); cp "$f" $t/page.html; d=$(dirname "$f"); for g in "$d"/*.gif; do [ -e "$g" ] && cp "$g" $t/; done
python3 - $t/page.html <<'PY'
import sys
p=sys.argv[1]; s=open(p,encoding='utf-8',errors='replace').read()
js="""<script>window.__errs=[];window.addEventListener('error',e=>{window.__errs.push(String(e.message)+' @'+e.lineno)});
window.addEventListener('load',()=>setTimeout(()=>{const o={errs:window.__errs,sw:document.documentElement.scrollWidth,iw:innerWidth};
const ids=new Set([...document.querySelectorAll('[id]')].map(e=>e.id));
o.badAnchors=[...document.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute('href').slice(1)).filter(h=>h&&!ids.has(h));
o.noIdHeadings=[...document.querySelectorAll('h2,h3')].filter(h=>!h.id).map(h=>h.textContent.trim().slice(0,50));
o.empty=[...document.querySelectorAll('p[id],span[id],b[id],td[id]')].filter(e=>!e.textContent.trim()).map(e=>e.id);
o.hasContents=!!document.querySelector('#toclist, nav ol, nav ul');
o.related=[...document.querySelectorAll('h2,h3')].some(h=>/related/i.test(h.textContent));
o.hubLinks=[...document.querySelectorAll('a[href*="et-soc1-limits-of-observability"]')].length;
o.brokenImgs=[...document.querySelectorAll('img')].filter(i=>!(i.complete&&i.naturalWidth>0)).map(i=>i.getAttribute('src'));
o.h2=[...document.querySelectorAll('h2')].map(h=>h.id);
const pre=document.createElement('pre');pre.id='__probe';pre.textContent=JSON.stringify(o);document.body.appendChild(pre);},800));</script>"""
i=s.rfind('</body>'); s=s[:i]+js+s[i:] if i>=0 else s+js
open(p,'w').write(s)
PY
for w in 1280 390; do
  timeout 120 $HS --headless --no-sandbox --disable-gpu --virtual-time-budget=6000 --window-size=$w,900 --dump-dom file://$t/page.html 2>/dev/null > $t/dom.$w
  python3 - $t/dom.$w $w <<'PY'
import sys,re,html,json
s=open(sys.argv[1],encoding='utf-8',errors='replace').read(); m=re.search(r'<pre id="__probe">(.*?)</pre>',s,re.S)
if not m: print(sys.argv[2],'NO PROBE OUTPUT (page did not load?)'); sys.exit()
o=json.loads(html.unescape(m.group(1))); w=sys.argv[2]
ok = not o['errs'] and not o['badAnchors'] and not o['empty'] and o['sw']<=o['iw'] and not o['brokenImgs']
print(f"{w}px: {'OK' if ok else 'PROBLEMS'} overflow={o['sw']}/{o['iw']} errs={o['errs']} badAnchors={o['badAnchors']} empty={o['empty']} brokenImgs={o['brokenImgs']}")
if w=='1280': print(f"  headings without id={o['noIdHeadings']} contents={o['hasContents']} relatedSection={o['related']} hubLinks={o['hubLinks']}\n  h2 ids={o['h2']}")
PY
done
rm -rf $t
