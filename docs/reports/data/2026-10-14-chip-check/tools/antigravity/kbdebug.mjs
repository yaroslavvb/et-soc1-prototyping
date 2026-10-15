// kbdebug.mjs BASE id text : the shapes under a label's centre (document order), their fills, and the label's --kb
import { open, sleep } from '/home/yaroslavvb/claude/et-soc1-prototyping/tools/pagemotion/cdp.mjs';
const [BASE, ID, TXT] = process.argv.slice(2);
const b = await open({w: 1440, h: 900, dpr: 1, reduced: true});
await b.load(BASE, '', 6000); await b.idle(20000);
const graph = await b.ev('window.__chipTest.graph()');
const g = graph.find(x => x.id === ID);
await b.ev(`(() => { location.hash = ${JSON.stringify('#at=' + g.path.replace(/:/g, '%3A'))}; return 1; })()`);
await sleep(400); await b.idle(15000); await sleep(300);
const r = await b.ev(`(() => {
  const st = window.__chipState(), svg = document.getElementById('chip');
  const L = [...svg.querySelectorAll(':scope > g.lay')].find(l => l._key === st.path);
  const t = [...L.querySelectorAll('text')].find(x => x.textContent.startsWith(${JSON.stringify(TXT)}));
  if (!t) return 'no text';
  const bb = t.getBBox(), cx = bb.x + bb.width / 2, cy = bb.y + bb.height / 2;
  const out = {kbOwn: t.style.getPropertyValue('--kb'), kbComputed: getComputedStyle(t).getPropertyValue('--kb'), stroke: getComputedStyle(t).stroke, center: [cx, cy], shapes: []};
  L.querySelectorAll('rect, path, circle, ellipse, polygon').forEach(e => {
    let b2; try { b2 = e.getBBox(); } catch (_) { return; }
    if (!(cx >= b2.x && cx <= b2.x + b2.width && cy >= b2.y && cy <= b2.y + b2.height)) return;
    if (!(e.compareDocumentPosition(t) & Node.DOCUMENT_POSITION_FOLLOWING)) return;
    const cs = getComputedStyle(e);
    out.shapes.push({tag: e.tagName, cls: e.getAttribute('class'), styleFill: e.style.fill, styleFO: e.style.fillOpacity, compFill: cs.fill, compFO: cs.fillOpacity, op: cs.opacity, inFill: e.isPointInFill ? e.isPointInFill(new DOMPoint(cx, cy)) : null, parentCls: e.parentNode.getAttribute('class')});
  });
  return out; })()`);
console.log(JSON.stringify(r, null, 1));
await b.close();
