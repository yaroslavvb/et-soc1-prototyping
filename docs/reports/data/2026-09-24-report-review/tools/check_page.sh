#!/usr/bin/env bash
# check_page.sh <page.html> : render a report at 1280 and 390 px after its scripts run, and print problems.
# Reports: JS errors (including those thrown while the page loads: the listener is installed right after <head>,
# before any page script), empty computed fields, sideways overflow, in-page links to missing ids, broken images,
# h2/h3 without ids, and whether a contents list, a "Related reports" heading and a link back to the hub exist.
# The OK/PROBLEMS verdict counts only errors, bad anchors, empty fields, overflow and broken images.
# An "info" line per width adds what the visualisation standard asks for but does not fail the page:
#   smallSvgText  SVG text rendered below 11 px, by the nearest element with an id (the chart host)
#   hScroll       elements holding a chart or table that scroll sideways at this width
#   lowContrast   SVG text whose fill has contrast < 3:1 against what is behind it (a rect/circle under it, else the page)
#   svgFocusable  charts (svg) with at least one keyboard-focusable element / all rendered charts
#   warnings      console.error calls and the browser's benign ResizeObserver loop notice
# DARK=1 renders with data-theme="dark"; DARK=os emulates the OS dark preference instead.
# CHROME_HEADLESS overrides the browser (default: Playwright's chrome-headless-shell).
set -e
f=$(readlink -f "$1")
HS=${CHROME_HEADLESS:-$HOME/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell}
FLAGS=(); [ "${DARK:-}" = os ] && FLAGS=(--blink-settings=preferredColorScheme=0)
t=$(mktemp -d); trap 'rm -rf "$t"' EXIT
cp "$f" $t/page.html; d=$(dirname "$f"); for g in "$d"/*.gif; do [ -e "$g" ] && cp "$g" $t/; done
python3 - $t/page.html <<'PY'
import os, re, sys
p = sys.argv[1]; s = open(p, encoding='utf-8', errors='replace').read()
theme = "document.documentElement.dataset.theme='dark';" if os.environ.get('DARK', '') not in ('', 'os', '0') else ''
early = ("<script>" + theme + "window.__errs=[];window.__warn=[];"
  "window.addEventListener('error',e=>{if(e instanceof ErrorEvent){const m=String(e.message);"
  "if(/ResizeObserver loop/.test(m))window.__warn.push(m);else window.__errs.push(m+' @'+e.lineno)}"
  "else{const x=e.target||{};window.__errs.push('failed to load: '+((x.getAttribute&&(x.getAttribute('src')||x.getAttribute('href')))||x.tagName||'?'))}},true);"
  "window.addEventListener('unhandledrejection',e=>{window.__errs.push('unhandled rejection: '+String(e.reason))});"
  "(()=>{const ce=console.error;console.error=function(...a){window.__warn.push('console.error: '+a.map(String).join(' ').slice(0,200));"
  "return ce.apply(this,a)}})();</script>")
m = re.search(r'<head(?:\s[^>]*)?>', s, re.I)
s = s[:m.end()] + early + s[m.end():] if m else early + s
js = r"""<script>
window.addEventListener('load',()=>setTimeout(()=>{const o={errs:window.__errs,warn:window.__warn,sw:document.documentElement.scrollWidth,iw:innerWidth};
const ids=new Set([...document.querySelectorAll('[id]')].map(e=>e.id));
o.badAnchors=[...document.querySelectorAll('a[href^="#"]')].map(a=>a.getAttribute('href').slice(1)).filter(h=>h&&!ids.has(h));
o.noIdHeadings=[...document.querySelectorAll('h2,h3')].filter(h=>!h.id).map(h=>h.textContent.trim().slice(0,50));
o.empty=[...document.querySelectorAll('p[id],span[id],b[id],td[id]')].filter(e=>!e.textContent.trim()).map(e=>e.id);
o.hasContents=!!document.querySelector('#toclist, nav ol, nav ul');
o.related=[...document.querySelectorAll('h2,h3')].some(h=>/related/i.test(h.textContent));
o.hubLinks=[...document.querySelectorAll('a[href*="et-soc1-limits-of-observability"]')].length;
o.brokenImgs=[...document.querySelectorAll('img')].filter(i=>!(i.complete&&i.naturalWidth>0)).map(i=>i.getAttribute('src'));
o.h2=[...document.querySelectorAll('h2')].map(h=>h.id);
// informational probes
const heads=[...document.querySelectorAll('h2[id],h3[id]')];
const host=e=>{let x=e;while(x&&!x.id)x=x.parentElement;if(x&&x!==document.body)return x.id;let h=null;for(const g of heads)if(g.compareDocumentPosition(e)&Node.DOCUMENT_POSITION_FOLLOWING)h=g;return e.tagName.toLowerCase()+' in #'+(h?h.id:'top')};
const shown=e=>e.getClientRects().length>0;
const bump=(m,k)=>{m[k]=(m[k]||0)+1};
const rgb=c=>{let m=/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)/.exec(c);
  if(m)return[+m[1],+m[2],+m[3],m[4]===undefined?1:+m[4]];
  m=/color\(srgb\s+([-\d.e]+)\s+([-\d.e]+)\s+([-\d.e]+)(?:\s*\/\s*([\d.]+))?\)/.exec(c);
  if(m)return[m[1]*255,m[2]*255,m[3]*255,m[4]===undefined?1:+m[4]];return null};
const lum=c=>{const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)};return 0.2126*f(c[0])+0.7152*f(c[1])+0.0722*f(c[2])};
const bg=e=>{for(let x=e;x;x=x.parentElement){const c=rgb(getComputedStyle(x).backgroundColor);if(c&&c[3]>0.5)return c}return[255,255,255,1]};
o.small={};o.lowc={};
const svgs=[...document.querySelectorAll('svg')].filter(v=>shown(v)&&!v.closest('.math-inline,.math-display')&&v.getBoundingClientRect().width>=120);
for(const v of svgs){const b=bg(v),shapes=[...v.querySelectorAll('rect,circle,ellipse')].filter(shown);
  for(const t of v.querySelectorAll('text')){if(!shown(t)||!t.textContent.trim())continue;const cs=getComputedStyle(t);
    if(cs.visibility==='hidden'||+cs.opacity===0)continue;
    const ctm=t.getScreenCTM(),k=ctm?Math.hypot(ctm.a,ctm.b):1,px=parseFloat(cs.fontSize)*k;
    if(px<10.95)bump(o.small,host(v));
    const c=rgb(cs.fill);if(c&&c[3]>0.5){let u=b;const q=t.getBoundingClientRect(),cx=q.x+q.width/2,cy=q.y+q.height/2;
      for(const sh of shapes)if(sh.compareDocumentPosition(t)&Node.DOCUMENT_POSITION_FOLLOWING){const r2=sh.getBoundingClientRect();
        if(cx>=r2.left&&cx<=r2.right&&cy>=r2.top&&cy<=r2.bottom){const ss=getComputedStyle(sh),sc=rgb(ss.fill);
          const a=sc?sc[3]*(+ss.fillOpacity)*(+ss.opacity):0;if(a>0)u=[0,1,2].map(i=>sc[i]*a+u[i]*(1-a))}}
      const l=lum(c),lu=lum(u),r=(Math.max(l,lu)+0.05)/(Math.min(l,lu)+0.05);if(r<3){const k=host(v);if(!o.lowc[k])o.lowc[k]={n:0,eg:t.textContent.trim().slice(0,24)+' '+r.toFixed(1)+':1'};o.lowc[k].n++}}}}
o.svgN=svgs.length;o.svgFoc=svgs.filter(v=>v.matches('[tabindex]:not([tabindex="-1"])')||v.querySelector('[tabindex]:not([tabindex="-1"]),a[href],button,input')).length;
o.hScroll=[...document.querySelectorAll('body *')].filter(e=>{if(e.closest('pre'))return false;const ox=getComputedStyle(e).overflowX;
  return (ox==='auto'||ox==='scroll')&&e.scrollWidth>e.clientWidth+1&&e.querySelector('svg,table')}).map(e=>e.matches('.math-display,.math-inline')?'math '+host(e):host(e));
const pre=document.createElement('pre');pre.id='__probe';pre.textContent=JSON.stringify(o);document.body.appendChild(pre);},800));</script>"""
i = s.rfind('</body>'); s = s[:i] + js + s[i:] if i >= 0 else s + js
open(p, 'w').write(s)
PY
for w in 1280 390; do
  timeout 120 "$HS" --headless --no-sandbox --disable-gpu "${FLAGS[@]}" --virtual-time-budget=6000 --window-size=$w,900 --dump-dom file://$t/page.html 2>/dev/null > $t/dom.$w || true
  python3 - $t/dom.$w $w <<'PY'
import sys,re,html,json
s=open(sys.argv[1],encoding='utf-8',errors='replace').read(); m=re.search(r'<pre id="__probe">(.*?)</pre>',s,re.S)
if not m: print(sys.argv[2]+'px: NO PROBE OUTPUT (page did not load?)'); sys.exit()
o=json.loads(html.unescape(m.group(1))); w=sys.argv[2]
ok = not o['errs'] and not o['badAnchors'] and not o['empty'] and o['sw']<=o['iw'] and not o['brokenImgs']
print(f"{w}px: {'OK' if ok else 'PROBLEMS'} overflow={o['sw']}/{o['iw']} errs={o['errs']} badAnchors={o['badAnchors']} empty={o['empty']} brokenImgs={o['brokenImgs']}")
if w=='1280': print(f"  headings without id={o['noIdHeadings']} contents={o['hasContents']} relatedSection={o['related']} hubLinks={o['hubLinks']}\n  h2 ids={o['h2']}")
hs=sorted(set(o['hScroll'])); lc=dict((k, '%d (e.g. %s)' % (v['n'], v['eg'])) for k, v in o['lowc'].items())
print(f"  info: smallSvgText={o['small']} hScroll={hs} lowContrast={lc} svgFocusable={o['svgFoc']}/{o['svgN']}"
      + (f" warnings={o['warn']}" if o['warn'] else ""))
PY
done
