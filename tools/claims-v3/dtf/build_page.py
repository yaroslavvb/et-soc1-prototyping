#!/usr/bin/env python3
"""V3-DTF (E61) report page: docs/reports/2026-10-21-verifying-transistor-flips/index.html.

    python3 tools/claims-v3/dtf/build_page.py --dtf <dtf.json> --cam <cam.json> --images <png dir> --out <index.html>

One command. The prose comes from page_text.build(dtf, cam) — every number and every verdict in it is read from those
two files — and the charts below are inline SVG drawn here from the same two files, in E60's palette, light and dark,
each with a hover tooltip and a table of its own numbers. The camera PNGs are embedded as data: URIs so the page is a
single file (--copy-images writes them beside index.html instead).
"""
import argparse
import base64
import html
import json
import math
import mimetypes
import os
import re
import shutil

import page_text
from page_text import sig, pm, g

CSS = """
:root{color-scheme:light;--bg:#f4f6f9;--card:#ffffff;--surface:#fcfcfb;--line:#dfe4ec;--ink:#18202b;--muted:#4a5462;--faint:#7a8494;
--accent:#1f4e8c;--grid:#e6e9ee;--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--s5:#8a63d2;--code:#eef1f6;
--ok:#1baf7a;--bad:#d4452a;--open:#b47600;--thin:#7a8494;
--font-head:Charter,'Bitstream Charter','Sitka Text',Cambria,serif;--font-body:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,Roboto,sans-serif;
--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){color-scheme:dark;--bg:#12161c;--card:#1a2029;--surface:#1a1a19;--line:#2e3846;
--ink:#e8edf3;--muted:#b6c0cc;--faint:#8c97a6;--accent:#8ab8f2;--grid:#2a2f37;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#9b7ae0;--code:#0e1217;
--ok:#3fc495;--bad:#ff7a5c;--open:#e0a235;--thin:#9aa5b4}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#12161c;--card:#1a2029;--surface:#1a1a19;--line:#2e3846;--ink:#e8edf3;--muted:#b6c0cc;--faint:#8c97a6;
--accent:#8ab8f2;--grid:#2a2f37;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#9b7ae0;--code:#0e1217;
--ok:#3fc495;--bad:#ff7a5c;--open:#e0a235;--thin:#9aa5b4}
*{box-sizing:border-box}html,body{background:var(--bg);color:var(--ink);font-family:var(--font-body)}
body{margin:0;font-size:18px;line-height:1.6;-webkit-text-size-adjust:100%}
main{max-width:46rem;margin:0 auto;padding:0 16px 4rem;overflow-wrap:break-word}a,code{overflow-wrap:anywhere}figure{overflow:hidden}
h1,h2,h3{font-family:var(--font-head);line-height:1.25}h1{font-size:2rem;margin:1.2rem 0 .4rem}h2{font-size:1.45rem;margin:2.4rem 0 .6rem}
h3{font-size:1.12rem;margin:1.6rem 0 .4rem}a{color:var(--accent)}p,li{color:var(--ink)}.muted{color:var(--muted)}
.nav{font-size:.92rem;margin:1rem 0 0}.lede{font-size:1.08rem}.byline{color:var(--muted);font-size:.92rem;margin:.2rem 0 1rem}
code{font-family:var(--mono);font-size:.86em;background:var(--code);padding:.05em .3em;border-radius:4px}
table{border-collapse:collapse;width:100%;font-size:.88rem;margin:.6rem 0}th,td{border-bottom:1px solid var(--line);padding:.35rem .4rem;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600}td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
.tablewrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
.tablewrap table{min-width:34rem}
figure{margin:1.2rem 0;background:var(--card);border:1px solid var(--line);border-radius:6px;padding:12px}
figcaption{font-size:.9rem;color:var(--muted);margin-top:.4rem}.chart{width:100%;height:auto;display:block}
.chart.small{max-width:540px;margin:0 auto}
.chart text{font-family:var(--font-body);fill:var(--muted);font-size:15px}.chart .lab{fill:var(--ink);font-size:15px}
.chart .axis{stroke:var(--faint);stroke-width:1}.chart .grid{stroke:var(--grid);stroke-width:1}
.chart [data-tip]{cursor:default}.chart [data-tip]:focus{outline:2px solid var(--accent)}
.legend{display:flex;flex-wrap:wrap;gap:.3rem 1rem;font-size:.85rem;color:var(--muted);margin:.2rem 0 .4rem}
.legend i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:.35rem;vertical-align:-1px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(12rem,1fr));gap:10px;margin:1rem 0}
.stat{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:10px 12px}
.stat b{display:block;font-family:var(--font-head);font-size:1.3rem;color:var(--ink);line-height:1.2}.stat span{font-size:.85rem;color:var(--muted)}
details{margin:.4rem 0}summary{cursor:pointer;color:var(--muted);font-size:.9rem}
#tip{position:fixed;pointer-events:none;background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:.3rem .5rem;
font-size:.82rem;box-shadow:0 2px 8px rgba(0,0,0,.18);display:none;z-index:9;max-width:18rem}
.note{border:1px solid var(--line);border-radius:6px;padding:.5rem .8rem;color:var(--muted);font-size:.95rem}
.v{font-weight:600;white-space:nowrap}.v-ok{color:var(--ok)}.v-bad{color:var(--bad)}.v-open{color:var(--open)}.v-thin{color:var(--thin)}
.v::before{content:"";display:inline-block;width:.5rem;height:.5rem;border-radius:50%;background:currentColor;margin-right:.35rem;vertical-align:.05em}
.imgs{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:10px}
.imgs img{width:100%;height:auto;display:block;border-radius:4px;background:var(--code)}
.imgs figcaption{margin-top:.3rem}
@media (min-width:880px){.tablewrap.wide{width:min(94vw,1060px);margin-left:calc(50% - min(47vw,530px))}
.tablewrap.wide td:nth-child(2){min-width:10rem}.tablewrap.wide td:last-child{min-width:19rem}}
@media (max-width:640px){
table.cards{min-width:0}table.cards thead{display:none}
table.cards tr{display:block;border-bottom:1px solid var(--line);padding:.45rem 0}
table.cards td{display:block;border:0;padding:.05rem 0;text-align:left}
table.cards td:empty{display:none}
table.cards td::before{content:attr(data-label) ": ";color:var(--muted)}
table.cards td:first-child{font-family:var(--font-head);font-size:1.05rem;color:var(--ink)}
table.cards td:first-child::before{content:none}
.tablewrap:has(table.cards){overflow-x:visible}}
"""
JS = """
(function(){var t=document.getElementById('tip');function show(e){var el=e.target.closest('[data-tip]');if(!el){t.style.display='none';return}
t.textContent=el.getAttribute('data-tip');t.style.display='block';var r=el.getBoundingClientRect();var x=(e.clientX||r.left+r.width/2)+12,y=(e.clientY||r.top)+12;
if(x+t.offsetWidth>innerWidth-8)x=innerWidth-t.offsetWidth-8;if(y+t.offsetHeight>innerHeight-8)y=y-t.offsetHeight-24;t.style.left=x+'px';t.style.top=y+'px'}
document.addEventListener('mouseover',show);document.addEventListener('mousemove',function(e){if(t.style.display==='block')show(e)});
document.addEventListener('focusin',show);document.addEventListener('focusout',function(){t.style.display='none'});
document.addEventListener('mouseleave',function(){t.style.display='none'})})();
"""


def esc(s):
    return html.escape(str(s), quote=True)


def nice_ticks(lo, hi, n=5):
    if hi <= lo:
        hi = lo + 1
    span = hi - lo
    step = 10 ** math.floor(math.log10(span / n))
    for m in (1, 2, 2.5, 5, 10):
        if span / (step * m) <= n:
            step *= m
            break
    out, v = [], math.floor(lo / step) * step
    while v <= hi + step * 1e-9:
        out.append(round(v, 10))
        v += step
    return out


class Plot:
    """A small scatter/line/bar plotter writing SVG, with error bars, bands, dashed reference lines and tooltips."""

    def __init__(self, xlo, xhi, ylo, yhi, w=620, h=380, ml=66, mr=18, mt=18, mb=58, xlabel="", ylabel="",
                 xticks=None, yticks=None, xfmt="{:g}", yfmt="{:g}", xcat=None, rotate=False):
        self.w, self.h, self.ml, self.mr, self.mt, self.mb = w, h, ml, mr, mt, mb
        self.xlo, self.xhi, self.ylo, self.yhi = xlo, xhi, ylo, yhi
        self.parts, self.xcat = [], xcat
        yt = yticks or nice_ticks(ylo, yhi)
        self.ylo, self.yhi = min(ylo, yt[0]), max(yhi, yt[-1])
        for v in yt:
            y = self.Y(v)
            self.parts.append(f'<line class="grid" x1="{ml}" x2="{w - mr}" y1="{y:.1f}" y2="{y:.1f}"/>'
                              f'<text x="{ml - 6}" y="{y + 5:.1f}" text-anchor="end">{esc(yfmt.format(v))}</text>')
        if xcat:
            for i, c in enumerate(xcat):
                x = self.X(i)
                if rotate:
                    self.parts.append(f'<text x="{x:.1f}" y="{h - mb + 14}" text-anchor="end" '
                                      f'transform="rotate(-38 {x:.1f} {h - mb + 14})">{esc(c)}</text>')
                else:
                    self.parts.append(f'<text x="{x:.1f}" y="{h - mb + 20}" text-anchor="middle">{esc(c)}</text>')
        else:
            xt = xticks or nice_ticks(xlo, xhi)
            self.xlo, self.xhi = min(xlo, xt[0]), max(xhi, xt[-1])
            for v in xt:
                x = self.X(v)
                self.parts.append(f'<line class="axis" x1="{x:.1f}" x2="{x:.1f}" y1="{h - mb}" y2="{h - mb + 4}"/>'
                                  f'<text x="{x:.1f}" y="{h - mb + 20}" text-anchor="middle">{esc(xfmt.format(v))}</text>')
        if self.ylo < 0 < self.yhi:
            self.parts.append(f'<line class="axis" x1="{ml}" x2="{w - mr}" y1="{self.Y(0):.1f}" y2="{self.Y(0):.1f}"/>')
        self.parts.append(f'<line class="axis" x1="{ml}" x2="{w - mr}" y1="{h - mb}" y2="{h - mb}"/>')
        self.parts.append(f'<text x="{(ml + w - mr) / 2:.0f}" y="{h - 8}" text-anchor="middle">{esc(xlabel)}</text>')
        self.parts.append(f'<text transform="translate(16,{(mt + h - mb) / 2:.0f}) rotate(-90)" text-anchor="middle">{esc(ylabel)}</text>')

    def X(self, v):
        if self.xcat is not None:
            return self.ml + (self.w - self.ml - self.mr) * (v + 0.5) / len(self.xcat)
        return self.ml + (self.w - self.ml - self.mr) * (v - self.xlo) / (self.xhi - self.xlo)

    def Y(self, v):
        return self.mt + (self.h - self.mt - self.mb) * (1 - (v - self.ylo) / (self.yhi - self.ylo))

    def band(self, lo, hi, color, tip=""):
        y0, y1 = self.Y(hi), self.Y(lo)
        self.parts.insert(0, f'<rect x="{self.ml}" y="{y0:.1f}" width="{self.w - self.ml - self.mr:.1f}" '
                             f'height="{max(y1 - y0, 1.5):.1f}" fill="var({color})" opacity=".16" data-tip="{esc(tip)}"/>')

    def hline(self, y, color, tip="", dash=True, label=None, align="end"):
        yy = self.Y(y)
        da = ' stroke-dasharray="5 4"' if dash else ""
        self.parts.append(f'<line x1="{self.ml}" x2="{self.w - self.mr}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="var({color})" '
                          f'stroke-width="1.5"{da} opacity=".9" data-tip="{esc(tip)}"/>')
        if label:
            x = (self.w - self.mr - 4) if align == "end" else (self.ml + 4)
            self.parts.append(f'<text class="lab" x="{x:.1f}" y="{yy - 6:.1f}" text-anchor="{align}">{esc(label)}</text>')

    def line(self, pts, color, dash=False, width=2):
        d = " ".join(f"{'M' if i == 0 else 'L'}{self.X(x):.1f},{self.Y(y):.1f}" for i, (x, y) in enumerate(pts))
        self.parts.append(f'<path d="{d}" fill="none" stroke="var({color})" stroke-width="{width}"'
                          + (' stroke-dasharray="5 4" opacity=".8"' if dash else '') + '/>')

    def dots(self, pts, color, tips, r=4.5, shape="circle", hollow=False):
        for (x, y, e), tip in zip(pts, tips):
            cx, cy = self.X(x), self.Y(y)
            if e:
                self.parts.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{self.Y(y - e):.1f}" y2="{self.Y(y + e):.1f}" '
                                  f'stroke="var({color})" stroke-width="1.5"/>')
            fill = "var(--surface)" if hollow else f"var({color})"
            sw = 2.4 if hollow else 2
            if shape == "square":
                self.parts.append(f'<rect x="{cx - r:.1f}" y="{cy - r:.1f}" width="{2 * r:.1f}" height="{2 * r:.1f}" rx="1.5" '
                                  f'fill="{fill}" stroke="var({color if hollow else "--surface"})" stroke-width="{sw}" tabindex="0" data-tip="{esc(tip)}"/>')
            else:
                self.parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" '
                                  f'stroke="var({color if hollow else "--surface"})" stroke-width="{sw}" tabindex="0" data-tip="{esc(tip)}"/>')
            self.parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="12" fill="transparent" data-tip="{esc(tip)}"/>')

    def bar(self, i, y, e, color, tip, k=0, nk=1, label=None):
        slot = (self.w - self.ml - self.mr) / len(self.xcat)
        bw = min(38, slot * 0.82 / nk)
        x0 = self.X(i) - bw * nk / 2 + k * bw + 1
        y0, y1 = self.Y(max(self.ylo, 0)), self.Y(y)
        top, ht = min(y0, y1), abs(y1 - y0)
        self.parts.append(f'<rect x="{x0:.1f}" y="{top:.1f}" width="{bw - 2:.1f}" height="{max(ht, 1):.1f}" rx="3" '
                          f'fill="var({color})" tabindex="0" data-tip="{esc(tip)}"/>')
        if e:
            cx = x0 + (bw - 2) / 2
            self.parts.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{self.Y(y - e):.1f}" y2="{self.Y(y + e):.1f}" '
                              f'stroke="var(--ink)" stroke-width="1.2" opacity=".7"/>')
        if label:
            ytop = self.Y(y + (e or 0)) if y >= 0 else self.Y(y)
            self.parts.append(f'<text class="lab" x="{x0 + (bw - 2) / 2:.1f}" y="{(min(ytop, y0) - 5):.1f}" text-anchor="middle" '
                              f'font-size="13">{esc(label)}</text>')

    def text(self, x, y, s, anchor="start", cls="lab", dy=0, size=None):
        f = f' font-size="{size}"' if size else ""
        self.parts.append(f'<text class="{cls}" x="{self.X(x):.1f}" y="{self.Y(y) + dy:.1f}" text-anchor="{anchor}"{f}>{esc(s)}</text>')

    def svg(self, title):
        return f'<svg class="chart" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{esc(title)}">' + "".join(self.parts) + "</svg>"


def legend(items):
    return '<div class="legend">' + "".join(f'<span><i style="background:var({c})"></i>{esc(n)}</span>' for n, c in items) + "</div>"


def cell(x):
    """A table cell: escaped, then `backticks` become <code>. The only markup a cell may carry.

    Table cells used to be handed literal <code> tags, which esc() turned into visible angle brackets
    (the wf4 build printed "<code>eOutBoard</code>" in three tables). Backticks are escape-safe.
    """
    s = esc(x)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", s)


def table(head, rows, num=(), verdict_col=None, cards=False, wide=False):
    """A table. cards=True also stacks each row as a labelled block on a narrow screen."""
    h = "".join(f'<th class="{"n" if i in num else ""}">{esc(x)}</th>' for i, x in enumerate(head))
    b = []
    for r in rows:
        tds = []
        for i, x in enumerate(r):
            lab = f' data-label="{esc(head[i])}"' if cards and i < len(head) else ""
            if verdict_col is not None and i == verdict_col:
                tds.append(f'<td{lab}><span class="v v-{page_text.badge(x)}">{esc(x)}</span></td>')
            else:
                tds.append(f'<td class="{"n" if i in num else ""}"{lab}>{cell(x)}</td>')
        b.append("<tr>" + "".join(tds) + "</tr>")
    cls = ' class="cards"' if cards else ""
    wrap = "tablewrap wide" if wide else "tablewrap"
    return f'<div class="{wrap}"><table{cls}><thead><tr>{h}</tr></thead><tbody>{"".join(b)}</tbody></table></div>'


def forest(rows, xlabel, title, unit="", w=470, rowh=50):
    """A horizontal value-with-interval plot. Each row: dict(label, value, se, lo, hi, kind, color, note)."""
    vals = []
    for r in rows:
        if r.get("kind") == "band":
            vals += [r["lo"], r["hi"]]
        else:
            vals += [r["value"] - 3 * (r.get("se") or 0), r["value"] + 3 * (r.get("se") or 0)]
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.12 or 1
    hi += pad
    lo = lo - pad if lo > 0 and lo - pad > 0 else lo
    if lo < 0 and abs(lo) < 0.09 * (hi - lo):   # a whisker just below zero should not buy a negative axis
        lo = 0
    bands = sum(1 for r in rows if r.get("kind") == "band")
    h = 58 + rowh * (len(rows) - bands) + 24 * bands
    ml, mr, mt = 20, 22, 14
    ticks = nice_ticks(lo, hi)
    lo, hi = min(lo, ticks[0]), max(hi, ticks[-1])
    X = lambda v: ml + (w - ml - mr) * (v - lo) / (hi - lo)
    P = [f'<text x="{(ml + w - mr) / 2:.0f}" y="{h - 5}" text-anchor="middle" font-size="16">{esc(xlabel)}</text>']
    for t in ticks:
        P.append(f'<line class="grid" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{mt}" y2="{h - 36}"/>'
                 f'<text x="{X(t):.1f}" y="{h - 19}" text-anchor="middle" font-size="15">{esc(f"{t:g}")}</text>')
    tab = []
    y, band_i = mt + 24 * bands, 0
    for r in rows:
        if r.get("kind") != "band":
            y += rowh / 2
        col = r.get("color", "--s1")
        if r.get("kind") == "band":
            P.insert(0, f'<rect x="{X(r["lo"]):.1f}" y="{mt}" width="{max(X(r["hi"]) - X(r["lo"]), 2):.1f}" height="{h - 34 - mt:.1f}" '
                        f'fill="var({col})" opacity=".15" data-tip="{esc(r.get("note", r["label"]))}"/>')
            ty = mt + 13 + 20 * band_i
            band_i += 1
            P.append(f'<text class="lab" x="{X((r["lo"] + r["hi"]) / 2):.1f}" y="{ty:.1f}" text-anchor="middle" font-size="14">{esc(r["label"])}</text>')
            tab.append([r["label"], f'{sig(r["lo"], 4)} – {sig(r["hi"], 4)}', "", r.get("note", "")])
            continue
        v, se = r["value"], r.get("se") or 0
        if se:
            P.append(f'<line x1="{X(v - 3 * se):.1f}" x2="{X(v + 3 * se):.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="var({col})" stroke-width="1.5" opacity=".55"/>')
            P.append(f'<line x1="{X(v - se):.1f}" x2="{X(v + se):.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="var({col})" stroke-width="5" stroke-linecap="round"/>')
        tip = f'{r["label"]}: {pm(v, se or None, 3, unit)}' + (f' — {r["note"]}' if r.get("note") else "")
        P.append(f'<circle cx="{X(v):.1f}" cy="{y:.1f}" r="5.5" fill="var({col})" stroke="var(--surface)" stroke-width="2" tabindex="0" data-tip="{esc(tip)}"/>')
        P.append(f'<rect x="{X(v) - 12:.1f}" y="{y - 12:.1f}" width="24" height="24" fill="transparent" data-tip="{esc(tip)}"/>')
        anchor, dx = ("start", 12) if X(v) < w * 0.5 else ("end", -12)
        P.append(f'<text class="lab" x="{X(v) + dx:.1f}" y="{y - 10:.1f}" text-anchor="{anchor}" font-size="16">{esc(r["label"])}</text>')
        P.append(f'<text x="{X(v) + dx:.1f}" y="{y + 19:.1f}" text-anchor="{anchor}" font-size="15">{esc(pm(v, se or None, 3, unit))}</text>')
        tab.append([r["label"], sig(v, 4), sig(se, 3) if se else "", r.get("note", "")])
        y += rowh / 2
    svg = f'<svg class="chart small" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">' + "".join(P) + "</svg>"
    return svg, table(["reading", "value", "SE", "note"], tab, num=(1, 2))


# ----------------------------------------------------------------------------- charts
def chart_d1(R, prim):
    C = R["cards"][prim]
    series = [("d1n", "operands include the all-zero word (the page's design)", "--s1", "circle"),
              ("d1nz", "never a zero word (our control)", "--s2", "square")]
    pts, rows = {}, []
    for key, name, col, shape in series:
        v = []
        for n, it in sorted(C["items"].items()):
            if not n.startswith(key + "_h") or it.get("d_fJ_per_regressor_bit") is None:
                continue
            val = it["d_fJ_per_regressor_bit"]
            se = abs(val) * (it["d_p80_se"] / it["d_p80"]) if it.get("d_p80") else 0
            v.append((it["h"], val, se, n, it))
        pts[key] = sorted(v)
    ys = [y for v in pts.values() for _, y, e, _, _ in v for y in (y - e, y + e)]
    if not ys:
        return "", ""
    hs = sorted({x for v in pts.values() for x, *_ in v})
    p = Plot(0, max(hs) * 1.06, min(ys) * 0.96, max(ys) * 1.03,
             xlabel="h: bits flipping per lane, per instruction", ylabel="fJ per flipped bit (board)",
             xticks=[0] + hs)
    for key, name, col, shape in series:
        v = pts[key]
        if not v:
            continue
        p.line([(x, y) for x, y, _, _, _ in v], col)
        p.dots([(x, y, e) for x, y, e, _, _ in v], col,
               [f"{n}, h = {int(x)}: {pm(y, e, 3, 'fJ')} per flipped bit; {it['d_p80']:.3f} W above the h = 0 rung over "
                f"{it['n_passes']} passes" for x, y, e, n, it in v], shape=shape)
        for x, y, e, n, it in v:
            rows.append([n, name.split("(")[0].strip(), int(x), int(it["regressor_bits_per_op"]), f"{y:.3f}", f"{e:.3f}",
                         f"{it['d_p80']:.3f}", it["n_passes"]])
    return (legend([(n, c) for _, n, c, _ in series]) + p.svg("Energy per flipped bit against h"),
            table(["item", "arm", "h", "port+result bits/op", "fJ per bit", "SE", "W above h = 0", "passes"], rows,
                  num=(2, 3, 4, 5, 6, 7)))


def chart_cell(R, prim, V):
    C = R["cards"][prim]
    q = (C.get("derived") or {}).get("e_cell") or {}
    v = next((x for x in V if x.get("value_fJ") is not None and "cell" in str(x.get("quantity", ""))), {})
    val = v.get("value_fJ", (q.get("value") or 0) * 1e15)
    se = v.get("se_fJ", (q.get("se") or 0) * 1e15)
    rows = [{"label": "measured, 1B − 1A slope difference", "value": val, "se": se, "color": "--s1",
             "note": f"{v.get('n_passes', q.get('n_passes', '–'))} passes on {v.get('card', prim)}; bar one SE, line three"}]
    pr = q.get("prior_fJ")
    if pr:
        rows.append({"kind": "band", "label": "registered prior", "lo": pr[0], "hi": pr[1], "color": "--s3",
                     "note": "the interval written into the pre-registration before the run"})
    jf = g(C, "joint_fit", "coefs", "e_cell", default={})
    if jf.get("fJ") is not None:
        rows.append({"label": "the pooled fit, descriptive only", "value": jf["fJ"], "se": jf.get("se_fJ"), "color": "--thin",
                     "note": "from the pooled fit; one contrast identifies it, so the reduction forbids quoting its standard error"})
    return forest(rows, "fJ per flipped register-file cell bit (board)", "The cell bit's price", "fJ")


def chart_d2(R, prim):
    C = R["cards"][prim]
    cells = [("d2A", "d2A · fand, result held at 0 — the page's Run A", "--s1", "circle"),
             ("d2B", "d2B · fand, result flips — Run B", "--s2", "circle"),
             ("d2C", "d2C · for, result held at all-ones — Run C", "--s3", "square"),
             ("d2D", "d2D · for, result flips", "--s4", "square")]
    pts, rows = {}, []
    for k, name, col, shape in cells:
        v = [(0.0, 0.0, None, k + "_h0")]
        for n, it in sorted(C["items"].items()):
            if n.startswith(k + "_h") and it.get("d_p80") is not None:
                v.append((it["h"], it["d_p80"], it.get("d_p80_se"), n))
        pts[k] = sorted(v)
    ys = [y for v in pts.values() for _, y, _, _ in v]
    if len(ys) < 2:
        return "", ""
    hs = sorted({x for v in pts.values() for x, *_ in v})
    p = Plot(0, max(hs) * 1.05, 0, max(ys) * 1.08, xlabel="h: bits flipping per lane, per instruction",
             ylabel="watts above the cell's own h = 0 rung", xticks=hs)
    for k, name, col, shape in cells:
        v = pts[k]
        p.line([(x, y) for x, y, _, _ in v], col)
        p.dots([(x, y, e) for x, y, e, _ in v[1:]], col,
               [f"{n}: {pm(y, e, 3, 'W')} above {k}_h0" for _, y, e, n in v[1:]], shape=shape)
        for x, y, e, n in v[1:]:
            rows.append([n, name, int(x), f"{y:.3f}", f"{e:.3f}" if e else "–"])
    return (legend([(n, c) for _, n, c, _ in cells]) + p.svg("The 2 x 2 bridge"),
            table(["item", "cell", "h", "W above h = 0", "SE"], rows, num=(2, 3, 4)))


def chart_d2e(R, prim, V, F=None):
    """Every route to the result-bit price that the files carry, so the reader can see the 5 fJ disagreement."""
    C = R["cards"][prim]
    v = next((x for x in V if "e_out" in str(x.get("quantity", ""))), {})
    q = (C.get("derived") or {}).get("e_out_bridge") or {}
    E = (F or {}).get("e_out_routes") or {}
    rows = []
    wf = E.get("within_family_mean") or {}
    if wf.get("value") is not None:
        rows.append({"label": "within family B, the two legs averaged", "value": wf["value"], "se": wf.get("se"),
                     "color": "--s3", "note": "each leg at its own mode's rate; the opcode baseline cancels by construction"})
    raw = v.get("raw_combination_fJ", (q.get("value") or 0) * 1e15)
    raw_se = v.get("raw_combination_se_fJ", (q.get("se") or 0) * 1e15)
    rows.append({"label": "raw (B+D) − (A+C)", "value": raw, "se": raw_se, "color": "--s5",
                 "note": "the bridge as the page designed it, with no changed-word term"})
    if v.get("joint_fit_fJ") is not None:
        rows.append({"label": "quoted: the pooled fit", "value": v["joint_fit_fJ"], "se": v.get("joint_fit_se_fJ"),
                     "color": "--s1", "note": v.get("quoted_from", "")})
    for key, lab in (("cross_family_with_origin", "cross-family (N − X), through the origin"),
                     ("cross_family_free_intercept", "cross-family (N − X), free intercept")):
        r = E.get(key) or {}
        if r.get("value") is not None:
            rows.append({"label": lab, "value": r["value"], "se": r.get("se"), "color": "--thin",
                         "note": "the route family B was built to replace — E60's own method, repeated tonight"})
    band = v.get("E60_interval_fJ") or q.get("E60_interval_fJ")
    if band:
        rows.append({"kind": "band", "label": "E60, another kernel", "lo": band[0], "hi": band[1], "color": "--s4",
                     "note": "measured in the previous experiment by a different route"})
    pg = v.get("page_fJ", q.get("page_fJ"))
    if pg:
        rows.append({"label": "the page's claim", "value": pg, "se": None, "color": "--s2",
                     "note": "from its two-equation decomposition of the catalogue"})
    return forest(rows, "fJ per flipped result bit (board)", "What a result bit costs", "fJ", w=560, rowh=54)


def chart_d5e(R, prim, V, F=None):
    """The address ladder read five legitimate ways, against the two numbers that were registered."""
    A = (F or {}).get("addr") or {}
    rows = []
    for key, lab, col in (("free_intercept", "the registered fit: two rungs, free intercept", "--s1"),
                          ("with_origin", "the same rungs, forced through the origin", "--s5")):
        r = A.get(key) or {}
        if r.get("value") is not None:
            rows.append({"label": lab, "value": r["value"], "se": r.get("se"), "color": col,
                         "note": "both are defensible readings of the same three rungs"})
    if A.get("live_fJ") is not None:
        rows.append({"label": "the live arm's own slope", "value": A["live_fJ"], "se": A.get("live_se_fJ"),
                     "color": "--s3", "note": "every data register non-zero, so the datapath is awake while the index moves"})
    if A.get("joint_fit_fJ") is not None:
        rows.append({"label": "the pooled fit's coefficient", "value": A["joint_fit_fJ"], "se": None, "color": "--thin",
                     "note": "identified by family A alone, so the reduction forbids quoting its SE"})
    pr = A.get("prior_fJ")
    if pr:
        rows.append({"kind": "band", "label": "our registered prior", "lo": pr[0], "hi": pr[1], "color": "--s3",
                     "note": "0 to 2 fJ a bit, written before the run"})
    if A.get("page_fJ"):
        rows.append({"label": "the page's claim", "value": A["page_fJ"], "se": None, "color": "--s2",
                     "note": "32 fJ a bit across three ports"})
    if not rows:
        return "", ""
    return forest(rows, "fJ per toggled register-index bit (board)", "Five readings of three rungs", "fJ",
                  w=560, rowh=54)


def chart_halfdie(R, V, F=None):
    """The half-die result-path load: three cards, and the plan's three spellings of its own target."""
    v = next((x for x in V if "dP_card" in str(x.get("quantity", ""))), {})
    t3 = v.get("half_die_three_ways") or {}
    H = (F or {}).get("half_die") or {}
    rows = []
    for card, d in sorted(H.items(), key=lambda kv: -(kv[1].get("value") or 0)):
        rows.append({"label": f"{card} · {d.get('mhz')} MHz, {d.get('mv')} mV", "value": d.get("value"),
                     "se": d.get("se"), "color": "--s1" if d.get("mhz") == 600 else "--thin",
                     "note": f"half the measured ½[(B−A)+(D−C)] combination over {d.get('n_passes', '–')} passes"})
    for key, lab in (("b_from_joint_fit_e_out_W", "the plan's own formula, from the pooled fit"),
                     ("b_from_raw_bridge_e_out_W", "the plan's own formula, from the raw bridge")):
        if t3.get(key) is not None:
            rows.append({"label": lab, "value": t3[key], "se": None, "color": "--s5",
                         "note": "e_out × 256 result bits an operation × the rate, halved"})
    tgt = v.get("half_die_target_W") or t3.get("c_strict_interval_W")
    if tgt:
        rows.append({"kind": "band", "label": "the registered window", "lo": tgt[0], "hi": tgt[1], "color": "--s4",
                     "note": "the interval the row is scored against"})
    if v.get("page_W"):
        rows.append({"label": "the page's claim", "value": v["page_W"], "se": None, "color": "--s2",
                     "note": "about 2.2 W of switching heat moving from side to side"})
    if not rows:
        return "", ""
    return forest(rows, "watts of result-path load on one half of the mesh", "The half-die load", "W",
                  w=560, rowh=54)


def chart_d3(R, prim):
    C = R["cards"][prim]
    v = [(0.0, 0.0, None, "d3_L0")]
    for n, it in sorted(C["items"].items()):
        if re.match(r"d3_L\d+$", n) and it.get("d_p80") is not None:
            v.append((float(it["L"]), it["d_p80"], it.get("d_p80_se"), n))
    v = sorted(v)
    if len(v) < 3:
        return "", ""
    fit = g(C, "families", "C_curvature", "fits", "linear_L", default={})
    xs = [x for x, *_ in v]
    p = Plot(0, max(xs) * 1.05, 0, max(y for _, y, _, _ in v) * 1.1, xlabel="L: carry run length, bits",
             ylabel="watts above the L = 0 rung", xticks=[int(x) for x in xs])
    if fit.get("slope") is not None:
        p.line([(0, fit["intercept_W"]), (max(xs), fit["intercept_W"] + fit["slope"] * max(xs))], "--faint", dash=True, width=1.5)
    p.line([(x, y) for x, y, _, _ in v], "--s1")
    p.dots([(x, y, e) for x, y, e, _ in v[1:]], "--s1", [f"{n}: {pm(y, e, 3, 'W')} above L = 0" for _, y, e, n in v[1:]])
    rows = [[n, int(x), f"{y:.3f}", f"{e:.3f}" if e else "–"] for x, y, e, n in v[1:]]
    lg = [("measured, one flipped input bit per lane", "--s1")]
    if fit.get("slope") is not None:
        lg.append((f"dashed: the fit in L the reduction prefers, {fit['slope']:.4f} W per stage, rms {fit['resid_rms_W']:.3f} W", "--faint"))
    return legend(lg) + p.svg("Power against carry length"), table(["item", "L", "W above L = 0", "SE"], rows, num=(1, 2, 3))


def chart_d3e(R, prim, V):
    C = R["cards"][prim]
    q = (C.get("derived") or {}).get("e_carry") or {}
    v = next((x for x in V if "carry" in str(x.get("quantity", ""))), {})
    rows = [{"label": "measured", "value": v.get("value_fJ", (q.get("value") or 0) * 1e15),
             "se": v.get("se_fJ", (q.get("se") or 0) * 1e15), "color": "--s1",
             "note": f"slope minus an independently measured result bit, {v.get('card', prim)}"}]
    pr = q.get("prior_fJ")
    if pr:
        rows.append({"kind": "band", "label": "our registered prior", "lo": pr[0], "hi": pr[1], "color": "--s3", "note": "written before the run"})
    if v.get("ours_fJ") is not None:
        rows.append({"label": "our registered point", "value": v["ours_fJ"], "se": None, "color": "--s4", "note": "the pre-registration's own estimate"})
    pg = v.get("page_fJ", q.get("page_fJ"))
    if pg is not None:
        rows.append({"label": "the page's claim", "value": pg, "se": None, "color": "--s2", "note": "the page's own figure for a carry stage"})
    return forest(rows, "fJ per carry stage (board)", "What a carry stage costs", "fJ")


def chart_d4(R, V):
    cards = [(k, c) for k, c in R["cards"].items() if g(c, "families", "M_levels", "k_adj")]
    if not cards:
        return "", ""
    cols = {}
    for i, (k, _) in enumerate(cards):
        cols[k] = ["--s1", "--s2", "--s3"][i % 3]
    allv, rows = [], []
    for k, c in cards:
        L = c["families"]["M_levels"]
        for x, y, st in zip(L["k_adj"], L["dW"], L["steps"] + [{}]):
            allv += [y]
    ses = [s.get("se", 0) for k, c in cards for s in c["families"]["M_levels"].get("steps", [])]
    pad = max(ses or [0.05]) * 3
    p = Plot(0, 1.9, min(allv) - pad, max(allv) + pad, xlabel="k_adj: how much each flipping wire's neighbours flip against it",
             ylabel="watts against the matched reference", xticks=[0, 0.5, 1, 1.5, 2], xfmt="{:g}")
    for k, c in cards:
        L = c["families"]["M_levels"]
        items = L.get("items_per_level") or {}
        se_by = {}
        for nm, q in (c["families"].get("M_items") or {}).items():
            se_by[nm] = g(q, "board", "se")
        pts = []
        for x, y in zip(L["k_adj"], L["dW"]):
            nm = None
            for key, val in (items.items() if isinstance(items, dict) else []):
                if abs(float(key) - x) < 1e-6:
                    nm = val if isinstance(val, str) else (val[0] if val else None)
            pts.append((x, y, se_by.get(nm, 0) if nm else 0, nm))
        p.line([(x, y) for x, y, _, _ in pts], cols[k])
        p.dots([(x, y, e) for x, y, e, _ in pts], cols[k],
               [f"{k}, k_adj = {x:g}{' (' + str(nm) + ')' if nm else ''}: {pm(y, e or None, 3, 'W')} against the reference" for x, y, e, nm in pts])
        for x, y, e, nm in pts:
            rows.append([k, f"{x:g}", nm or "–", f"{y:+.3f}", f"{e:.3f}" if e else "–"])
        rows.append([k, "—", "the whole spread, highest k_adj against lowest", f"{g(L, 'whole_spread', 'dW'):+.3f}", f"{g(L, 'whole_spread', 'se'):.3f}"])
    p.hline(0, "--faint", tip="the matched reference pattern", dash=True)
    return (legend([(f"{k} ({c.get('clock_mhz')} MHz)", cols[k]) for k, c in cards]) + p.svg("The Miller patterns"),
            table(["card", "k_adj", "pattern", "W against the reference", "SE"], rows, num=(3, 4)))


def chart_d5(R, prim, V):
    C = R["cards"][prim]
    v = next((x for x in V if "address" in str(x.get("quantity", "")) or "register-index" in str(x.get("quantity", ""))), {})
    excl = set(v.get("rate_confounded_excluded") or [])
    arms = [("d5_", "gated: every data register zero (the page's design)", "--s1", "circle"),
            ("d5n_", "live: every data register non-zero", "--s3", "square")]
    rows, allv = [], []
    series = {}
    for pre, name, col, shape in arms:
        base = C["items"].get(pre + "a0", {})
        b_addr = g(base, "counts", "addr", default=0)
        v2 = [(0.0, 0.0, None, pre + "a0", False)]
        for n, it in sorted(C["items"].items()):
            if not re.match(re.escape(pre) + r"a\d+$", n) or it.get("d_p80") is None:
                continue
            v2.append((g(it, "counts", "addr", default=0) - b_addr, it["d_p80"], it.get("d_p80_se"), n, n in excl))
        series[pre] = sorted(v2)
        allv += [y for _, y, _, _, _ in v2]
    xs = sorted({x for s in series.values() for x, *_ in s})
    p = Plot(0, max(xs) * 1.06, 0, max(allv) * 1.1, xlabel="register-index bits that toggle per operation",
             ylabel="watts above the matched zero rung", xticks=[round(x, 2) for x in xs])
    slope = v.get("value_fJ")
    for pre, name, col, shape in arms:
        s = series[pre]
        kept = [t for t in s if not t[4]]
        p.line([(x, y) for x, y, _, _, _ in kept], col)
        p.dots([(x, y, e) for x, y, e, _, ex in s if not ex], col,
               [f"{n}: {pm(y, e, 3, 'W')} above {pre}a0" for _, y, e, n, ex in s if not ex], shape=shape)
        hol = [(x, y, e) for x, y, e, _, ex in s if ex]
        if hol:
            p.dots(hol, col, [f"{n}: {pm(y, e, 3, 'W')} — excluded from the fit: it retires at another instruction rate"
                              for _, y, e, n, ex in s if ex], shape=shape, hollow=True)
        for x, y, e, n, ex in s[1:]:
            rows.append([n, name.split(":")[0], f"{x:g}", f"{y:.3f}", f"{e:.3f}" if e else "–", "excluded, rate-confounded" if ex else "in the fit"])
    return (legend([(n, c) for _, n, c, _ in arms] + [("hollow: reported beside the ladder, not inside the slope", "--faint")])
            + p.svg("The address ladder"),
            table(["item", "regime", "index bits/op", "W above the zero rung", "SE", "in the slope?"], rows, num=(2, 3, 4)))


def chart_d6(R, prim, V):
    v = next((x for x in V if x.get("pJ_per_op") is not None), {})
    q = g(R, "cards", prim, "derived", "zero_gate_step", default={})
    rows = [{"label": "measured on silicon tonight", "value": v.get("pJ_per_op", q.get("pJ_per_op")),
             "se": v.get("se_pJ_per_op", q.get("se_pJ_per_op")), "color": "--s1",
             "note": f"{g(q, 'n_passes', default='–')} passes on {v.get('card', prim)}"}]
    if v.get("ours_pJ_per_op") is not None:
        rows.append({"label": "the same step in the catalogue the page cites", "value": v["ours_pJ_per_op"], "se": None,
                     "color": "--s3", "note": "found by the desk check before any card ran"})
    pg = v.get("page_pJ_per_op", q.get("page_pJ_per_op"))
    if pg is not None:
        rows.append({"label": "the page's claim", "value": pg, "se": None, "color": "--s2",
                     "note": "its largest single energy claim"})
    return forest(rows, "pJ per operation, zero operands → a non-zero constant", "The zero gate", "pJ/op")


def chart_ipc(R, V):
    v = next((x for x in V if x.get("rates")), {})
    shapes = {}
    for card, C in R["cards"].items():
        for name, q in (g(C, "ipc", "shapes", default={}) or {}).items():
            shapes.setdefault(name, {})[card] = q
    if not shapes:
        return "", ""
    def short(n):
        m = re.match(r"([\w.]+)\s*/\s*ops_per_iter\s*(\d+)\s*/\s*harts\s*(\d+)", n)
        if not m:
            return n[:16]
        name = re.sub(r"^df\.", "", m.group(1))
        return name + ("" if m.group(3) == "1" else f" ×{m.group(3)} harts")
    names = sorted(shapes, key=lambda n: (next(iter(shapes[n].values()))["ipc"], n))
    cats = [short(n) for n in names]
    ys = [q["ipc"] for n in names for q in shapes[n].values()]
    page = v.get("page_ipc")
    top = max(ys + ([page] if page else []))
    p = Plot(0, 1, 0, top * 1.14, xcat=cats, xlabel="compiled shape", ylabel="operations retired per cycle, per hart",
             rotate=len(cats) > 6, mb=104 if len(cats) > 6 else 58, h=410, ml=78)
    rows = []
    for i, n in enumerate(names):
        byc = shapes[n]
        card = next((c for c in byc if c == g(R, "meta", "primary_card")), next(iter(byc)))
        q = byc[card]
        ref = q.get("vs_registered_0_5791_pct", q.get("vs_mode179_pct"))
        p.bar(i, q["ipc"], None, "--s1",
              f"{n} on {card}: {q['ipc']:.4f} ops/cycle/hart over {q.get('items', '–')} item(s), "
              + (f"{ref:+.2f}% against the registered reference rate" if ref is not None else ""))
        rows.append([short(n), card, f"{q['ipc']:.4f}", q.get("items", "–"),
                     f"{ref:+.2f}%" if ref is not None else "–"])
    if page:
        p.hline(page, "--s2", tip=f"the page assumes {page:g} operations per cycle per hart", label=f"the page: {page:g}")
    e60 = g(R, "cards", g(R, "meta", "primary_card"), "ipc", "E60_reference")
    if e60:
        p.hline(e60, "--s4", tip=f"the same mode measured {e60:g} in the previous experiment's build", label=f"E60's build: {e60:g}", align="start")
    return (legend([("measured tonight", "--s1"), ("the page's assumption", "--s2"), ("the same mode, the previous build", "--s4")])
            + p.svg("The issue rate"), table(["shape", "card", "ops/cycle/hart", "items", "against the registered 0.5791"], rows, num=(2, 3, 4)))


def chart_rho(R, V):
    v = next((x for x in V if x.get("rho") is not None), {})
    if not v:
        return "", ""
    card = v.get("rho_card") or v.get("card")
    notes = " ".join(g(R, "cards", card, "derived", "rho_harts2_over_harts1", "notes") or [])
    m1 = re.search(r"([\d.]+)\s*if operand sharing survives", notes)
    m2 = re.search(r"([\d.]+)\s*-\s*([\d.]+)\s*if interleaving destroys", notes)
    rows = [{"label": "measured", "value": v["rho"], "se": v.get("rho_se"), "color": "--s1",
             "note": f"{card}; bar one SE, line three"}]
    if m2:
        rows.append({"kind": "band", "label": "interleaving destroys sharing", "lo": float(m2.group(1)), "hi": float(m2.group(2)),
                     "color": "--s3", "note": "the catalogue's reading if the two harts interleave"})
    if m1:
        rows.append({"label": "sharing survives", "value": float(m1.group(1)), "se": None, "color": "--s2",
                     "note": "the reading the page's split assumes"})
    if v.get("interleave_fraction") is not None:
        rows[0]["note"] += f"; implied interleave fraction {v['interleave_fraction']:.3f}"
    return forest(rows, "ρ: the per-operation cost at two harts, over one", "Does sharing survive interleaving?")


CAM_FIGURES = {"png_scene_mean_frame": "The scene: the mean frame",
               "png_dipole_hi": "The response: one half warms, the other cools"}


def chart_cam(CAM, images, embed):
    files = g(CAM, "files", default={}) or {}
    want = list(CAM_FIGURES.items())
    out = []
    rows = []
    for key, cap in want:
        src = files.get(key)
        name = os.path.basename(src) if src else None
        path = os.path.join(images, name) if name and images else None
        if not path or not os.path.exists(path):
            continue
        if embed:
            mime = mimetypes.guess_type(path)[0] or "image/png"
            uri = f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()
        else:
            uri = name
        out.append(f'<figure style="margin:0;border:0;padding:0;background:none"><img src="{uri}" alt="{esc(cap)}" decoding="async">'
                   f'<figcaption>{esc(cap)}</figcaption></figure>')  # cap is a literal here, escaping is right
    if not out:
        return "", ""
    t2, t2s, t1 = g(CAM, "tier2_primary", default={}), g(CAM, "tier2_spatial", default={}), g(CAM, "tier1_board_meter", default={})
    arms = [x for x in (g(CAM, "controls", "arm_sensitivity_hi_mk", default={}) or {}).values() if isinstance(x, (int, float))]
    stat = [["the double difference across the swap", pm(t2.get('statistic_mk'), t2.get('se_pass_mk'), 3, "mK"),
             f"p = {sig(t2.get('p_cyclic'), 2)}",
             f"null scatter {sig(t2.get('null_sd_cyclic_mk'), 3)} mK over {t2.get('p_cyclic_labellings', '–')} labellings; "
             f"{sig(min(arms), 4)}–{sig(max(arms), 4)} mK across the four registered arm choices" if arms else ""],
            ["the quiet arm, same statistic", f"{sig(t2.get('lo_mk'), 4)} mK", f"p = {sig(t2.get('lo_p_cyclic'), 2)}", "the dipole is there without the loud half"],
            ["the card mean of the difference image", f"{sig(t2s.get('monopole_hi_mk'), 3)} mK", f"p = {sig(t2s.get('monopole_hi_p_cyclic'), 2)}",
             "the camera's reading of “total power does not change”"],
            ["the same cut, the other way across the frame", f"{sig(g(CAM, 'controls', 'orthogonal_axis', 'stat_mk'), 3)} mK",
             f"p = {sig(g(CAM, 'controls', 'orthogonal_axis', 'p_cyclic'), 2)}", "the signal lives on one axis"],
            ["board meter, the two halves", f"{sig(t1.get('W_minus_E_hi_w'), 3)} W",
             f"|t| = {sig(abs(t1.get('W_minus_E_hi_t_order_adjusted') or 0), 3)} with block order fitted",
             f"against {sig(t1.get('hi_minus_rest_w'), 3)} W drawn by the work itself"]]
    return ('<div class="imgs">' + "".join(out) + "</div>",
            table(["statistic", "value", "significance", "what it says"], stat))


# ----------------------------------------------------------------------------- page
def anchor_ids(body):
    seen = set()

    def add(tag, rest, tail):
        words = re.sub(r"<[^>]+>|&[a-z#0-9]+;", " ", tail)
        slug = "-".join(re.findall(r"[a-z0-9]+", words.lower())[:5]) or tag
        base, k = f"{tag}-{slug}"[:48], 2
        sid = base
        while sid in seen:
            sid, k = f"{base}-{k}", k + 1
        seen.add(sid)
        return f'<{tag} data-ss-id="{sid}"{rest}>'

    out, i = [], 0
    for m in re.finditer(r"<(h2|h3|p|ul|figure|div)((?:\s[^>]*)?)>", body):
        if "data-ss-id" in m.group(2):
            continue
        out.append((m.start(), m.end(), m.group(1), m.group(2)))
    res, last = [], 0
    for s, e, tag, rest in out:
        res.append(body[last:s])
        res.append(add(tag, rest, body[e:e + 170]))
        last = e
    res.append(body[last:])
    return "".join(res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dtf", required=True)
    ap.add_argument("--cam")
    ap.add_argument("--facts", help="facts.json from facts.py: the corrections and the context recomputed from the files")
    ap.add_argument("--images", help="directory holding the camera PNGs cam.json names")
    ap.add_argument("--out", required=True)
    ap.add_argument("--text", help="a page_text.py JSON to use instead of building the prose here")
    ap.add_argument("--copy-images", action="store_true", help="write the PNGs beside index.html instead of embedding them")
    a = ap.parse_args()
    R = json.load(open(a.dtf))
    CAM = json.load(open(a.cam)) if a.cam else {}
    FACTS = json.load(open(a.facts)) if a.facts else {}
    T = json.load(open(a.text)) if a.text else page_text.build(R, CAM, FACTS)
    prim, V = T.get("primary") or g(R, "meta", "primary_card", default="aifoundry3"), R["verdicts"]

    figs = {"d1": chart_d1(R, prim), "cell": chart_cell(R, prim, V), "d2": chart_d2(R, prim),
            "d2e": chart_d2e(R, prim, V, FACTS), "d3": chart_d3(R, prim), "d3e": chart_d3e(R, prim, V),
            "d4": chart_d4(R, V), "d5": chart_d5(R, prim, V), "d5e": chart_d5e(R, prim, V, FACTS),
            "d6": chart_d6(R, prim, V), "halfdie": chart_halfdie(R, V, FACTS),
            "ipc": chart_ipc(R, V), "rho": chart_rho(R, V),
            "cam": chart_cam(CAM, a.images, not a.copy_images)}
    if a.copy_images and a.images:
        outdir = os.path.dirname(os.path.abspath(a.out))
        for key, src in (g(CAM, "files", default={}) or {}).items():
            if key in CAM_FIGURES and src:
                p = os.path.join(a.images, os.path.basename(src))
                if os.path.exists(p):
                    shutil.copy2(p, os.path.join(outdir, os.path.basename(src)))

    body = T["body"]
    missing = []
    for key, (svg, tab) in figs.items():
        block = ""
        if svg:
            cap = T["captions"].get(key, "")   # authored HTML from page_text, not data
            block = (f'<figure>{svg}<figcaption>{cap}</figcaption>'
                     + (f'<details><summary>The numbers</summary>{tab}</details>' if tab else "") + "</figure>")
        elif "{{fig:" + key + "}}" in body:
            missing.append(key)
        body = body.replace("{{fig:" + key + "}}", block)
    for key, spec in (T.get("tables") or {}).items():
        body = body.replace("{{tbl:" + key + "}}", table(spec["head"], spec["rows"], tuple(spec.get("num", ())),
                                                         spec.get("verdict_col"), spec.get("cards", False),
                                                         spec.get("wide", False)))
    left = re.findall(r"\{\{(?:fig|tbl):([a-z0-9_]+)\}\}", body)
    if left:
        print("WARNING: unfilled placeholders:", left)
    if missing:
        print("WARNING: no data for figures:", missing)

    body = anchor_ids(body)
    out = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(T['title'])}</title><meta name="description" content="{esc(T['description'])}">
<style>{CSS}</style></head><body><main>
<h1>{esc(T['title'])}</h1>
<p class="nav" data-ss-id="nav-lab-dashboard" data-ss-react="off"><a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard">← AI Foundry lab dashboard</a> › <a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard#worklog">Worklog</a> › E61, after <a href="{page_text.E60_URL}">E60</a></p>
<p class="byline">{esc(T['byline'])}</p>
{body}
</main><div id="tip" role="tooltip"></div><script>{JS}</script></body></html>
"""
    open(a.out, "w").write(out)
    print(f"wrote {a.out} ({len(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
