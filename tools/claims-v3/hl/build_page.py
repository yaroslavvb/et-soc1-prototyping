#!/usr/bin/env python3
"""V3-HL report page: docs/reports/2026-10-20-bitflip-ladder/index.html, from reduce_hl.py's output.

    python3 tools/claims-v3/hl/build_page.py --hl <hl.json> --gen <make_hl.py dir> --text <page text .json> --out <index.html>

Charts are inline SVG drawn here (no libraries), in the dataviz reference palette (light and dark), each with a
hover tooltip and a data table. The prose comes from --text (a JSON of named HTML fragments) so numbers quoted in the
text are written after the reduction, from it.
"""
import argparse
import html
import json
import math

E = 1.602176634e-19
CSS = """
:root{color-scheme:light;--bg:#f4f6f9;--card:#ffffff;--surface:#fcfcfb;--line:#dfe4ec;--ink:#18202b;--muted:#4a5462;--faint:#7a8494;
--accent:#1f4e8c;--grid:#e6e9ee;--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--code:#eef1f6;
--font-head:Charter,'Bitstream Charter','Sitka Text',Cambria,serif;--font-body:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,Roboto,sans-serif;
--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){color-scheme:dark;--bg:#12161c;--card:#1a2029;--surface:#1a1a19;--line:#2e3846;
--ink:#e8edf3;--muted:#b6c0cc;--faint:#8c97a6;--accent:#8ab8f2;--grid:#2a2f37;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--code:#0e1217}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#12161c;--card:#1a2029;--surface:#1a1a19;--line:#2e3846;--ink:#e8edf3;--muted:#b6c0cc;--faint:#8c97a6;
--accent:#8ab8f2;--grid:#2a2f37;--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--code:#0e1217}
*{box-sizing:border-box}html,body{background:var(--bg);color:var(--ink);font-family:var(--font-body)}
body{margin:0;font-size:18px;line-height:1.6;-webkit-text-size-adjust:100%}
main{max-width:46rem;margin:0 auto;padding:0 16px 4rem;overflow-wrap:break-word}a,code{overflow-wrap:anywhere}figure{overflow:hidden}
h1,h2,h3{font-family:var(--font-head);line-height:1.25}h1{font-size:2rem;margin:1.2rem 0 .4rem}h2{font-size:1.45rem;margin:2.4rem 0 .6rem}
h3{font-size:1.12rem;margin:1.6rem 0 .4rem}a{color:var(--accent)}p,li{color:var(--ink)}.muted{color:var(--muted)}
.nav{font-size:.92rem;margin:1rem 0 0}.lede{font-size:1.08rem}.byline{color:var(--muted);font-size:.92rem;margin:.2rem 0 1rem}
code{font-family:var(--mono);font-size:.86em;background:var(--code);padding:.05em .3em;border-radius:4px}
table{border-collapse:collapse;width:100%;font-size:.88rem;margin:.6rem 0}th,td{border-bottom:1px solid var(--line);padding:.35rem .4rem;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600}td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
.tablewrap{overflow-x:auto}
figure{margin:1.2rem 0;background:var(--card);border:1px solid var(--line);border-radius:6px;padding:12px}
figcaption{font-size:.9rem;color:var(--muted);margin-top:.4rem}.chart{width:100%;height:auto;display:block}
.chart text{font-family:var(--font-body);fill:var(--muted);font-size:15px}.chart .lab{fill:var(--ink);font-size:15px}
.chart .axis{stroke:var(--faint);stroke-width:1}.chart .grid{stroke:var(--grid);stroke-width:1}
.chart [data-tip]{cursor:default}.chart [data-tip]:focus{outline:2px solid var(--accent)}
.legend{display:flex;flex-wrap:wrap;gap:.3rem 1rem;font-size:.85rem;color:var(--muted);margin:.2rem 0 .4rem}
.legend i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:.35rem;vertical-align:-1px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(10rem,1fr));gap:10px;margin:1rem 0}
.stat{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:10px 12px}
.stat b{display:block;font-family:var(--font-head);font-size:1.35rem;color:var(--ink)}.stat span{font-size:.85rem;color:var(--muted)}
details{margin:.4rem 0}summary{cursor:pointer;color:var(--muted);font-size:.9rem}
#tip{position:fixed;pointer-events:none;background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:.3rem .5rem;
font-size:.82rem;box-shadow:0 2px 8px rgba(0,0,0,.18);display:none;z-index:9;max-width:18rem}
.note{border:1px solid var(--line);border-radius:6px;padding:.5rem .8rem;color:var(--muted);font-size:.95rem}
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
    a = math.floor(lo / step) * step
    out = []
    v = a
    while v <= hi + step * 1e-9:
        out.append(round(v, 10))
        v += step
    return out


class Plot:
    """A small scatter/line/bar plotter writing SVG, with error bars, dashed reference lines and tooltips."""

    def __init__(self, xlo, xhi, ylo, yhi, w=600, h=380, ml=62, mr=18, mt=18, mb=54, xlabel="", ylabel="", xticks=None, yticks=None,
                 xfmt="{:g}", yfmt="{:g}", xcat=None):
        self.w, self.h, self.ml, self.mr, self.mt, self.mb = w, h, ml, mr, mt, mb
        self.xlo, self.xhi, self.ylo, self.yhi = xlo, xhi, ylo, yhi
        self.parts = []
        self.xcat = xcat
        yt = yticks or nice_ticks(ylo, yhi)
        self.ylo, self.yhi = min(ylo, yt[0]), max(yhi, yt[-1])
        for v in yt:
            y = self.Y(v)
            self.parts.append(f'<line class="grid" x1="{ml}" x2="{w - mr}" y1="{y:.1f}" y2="{y:.1f}"/>'
                              f'<text x="{ml - 6}" y="{y + 5:.1f}" text-anchor="end">{esc(yfmt.format(v))}</text>')
        if xcat:
            for i, c in enumerate(xcat):
                self.parts.append(f'<text x="{self.X(i):.1f}" y="{h - mb + 20}" text-anchor="middle">{esc(c)}</text>')
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
            n = len(self.xcat)
            return self.ml + (self.w - self.ml - self.mr) * (v + 0.5) / n
        return self.ml + (self.w - self.ml - self.mr) * (v - self.xlo) / (self.xhi - self.xlo)

    def Y(self, v):
        return self.mt + (self.h - self.mt - self.mb) * (1 - (v - self.ylo) / (self.yhi - self.ylo))

    def line(self, pts, color, dash=False, width=2):
        d = " ".join(f"{'M' if i == 0 else 'L'}{self.X(x):.1f},{self.Y(y):.1f}" for i, (x, y) in enumerate(pts))
        self.parts.append(f'<path d="{d}" fill="none" stroke="var({color})" stroke-width="{width}"'
                          + (' stroke-dasharray="5 4" opacity=".8"' if dash else '') + '/>')

    def dots(self, pts, color, tips, r=4.5, shape="circle"):
        for (x, y, e), tip in zip(pts, tips):
            cx, cy = self.X(x), self.Y(y)
            if e:
                self.parts.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{self.Y(y - e):.1f}" y2="{self.Y(y + e):.1f}" stroke="var({color})" stroke-width="1.5"/>')
            if shape == "square":
                self.parts.append(f'<rect x="{cx - r:.1f}" y="{cy - r:.1f}" width="{2 * r:.1f}" height="{2 * r:.1f}" rx="1.5" fill="var({color})" '
                                  f'stroke="var(--surface)" stroke-width="2" tabindex="0" data-tip="{esc(tip)}"/>')
            else:
                self.parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="var({color})" stroke="var(--surface)" stroke-width="2" '
                                  f'tabindex="0" data-tip="{esc(tip)}"/>')
            self.parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="11" fill="transparent" data-tip="{esc(tip)}"/>')

    def bar(self, i, y, e, color, tip, k=0, nk=1, label=None):
        n = len(self.xcat)
        slot = (self.w - self.ml - self.mr) / n
        bw = min(34, slot * 0.8 / nk)
        x0 = self.X(i) - bw * nk / 2 + k * bw + 1
        y0, y1 = self.Y(0), self.Y(y)
        top, ht = min(y0, y1), abs(y1 - y0)
        self.parts.append(f'<rect x="{x0:.1f}" y="{top:.1f}" width="{bw - 2:.1f}" height="{max(ht, 1):.1f}" rx="3" fill="var({color})" tabindex="0" data-tip="{esc(tip)}"/>')
        if e:
            cx = x0 + (bw - 2) / 2
            self.parts.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{self.Y(y - e):.1f}" y2="{self.Y(y + e):.1f}" stroke="var(--ink)" stroke-width="1.2" opacity=".7"/>')
        if label:
            ytop = self.Y(y + (e or 0)) if y >= 0 else self.Y(y)
            self.parts.append(f'<text class="lab" x="{x0 + (bw - 2) / 2:.1f}" y="{(min(ytop, y0) - 5):.1f}" text-anchor="middle">{esc(label)}</text>')

    def text(self, x, y, s, anchor="start", cls="lab", dy=0):
        self.parts.append(f'<text class="{cls}" x="{self.X(x):.1f}" y="{self.Y(y) + dy:.1f}" text-anchor="{anchor}">{esc(s)}</text>')

    def svg(self, title):
        return (f'<svg class="chart" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{esc(title)}">' + "".join(self.parts) + "</svg>")


def legend(items):
    return '<div class="legend">' + "".join(f'<span><i style="background:var({c})"></i>{esc(n)}</span>' for n, c in items) + "</div>"


def table(head, rows, num=()):
    h = "".join(f'<th class="{"n" if i in num else ""}">{esc(x)}</th>' for i, x in enumerate(head))
    b = "".join("<tr>" + "".join(f'<td class="{"n" if i in num else ""}">{esc(x)}</td>' for i, x in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="tablewrap"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def f2(x, n=2):
    return "–" if x is None else f"{x:.{n}f}"


def chart_ladders(C, man):
    """The two Hamming ladders on the reference card: measured differences from h = 0, and the RTL predictions."""
    fams = [("lq", "quiet partner, A = 1.0", "--s1"), ("lb", "busy partner, A = pi", "--s2")]
    ys = [r["dW"] for f, _, _ in fams for r in C[f]["rungs"].values() if r["dW"] is not None]
    ys += [r["pred_dW"] for f, _, _ in fams for r in C[f]["rungs"].values()]
    p = Plot(0, 23, min(0, min(ys)), max(ys) * 1.06, xlabel="h: B mantissa bits flipping every cycle, every lane",
             ylabel="watts above h = 0", xticks=[0, 1, 2, 4, 8, 12, 16, 23], yfmt="{:g}")
    rows = []
    for f, name, col in fams:
        rr = sorted(C[f]["rungs"].values(), key=lambda r: r["h"])
        p.line([(r["h"], r["pred_dW"]) for r in rr], col, dash=True, width=1.5)
        meas = [(r["h"], r["dW"], r["se"]) for r in rr if r["dW"] is not None]
        p.line([(x, y) for x, y, _ in meas], col)
        p.dots(meas, col, [f"{name}, h = {x}: {y:+.2f} W" + (f" ± {e:.2f}" if e else "") + f" (predicted {pr['pred_dW']:+.2f} W)"
                           for (x, y, e), pr in zip(meas, [r for r in rr if r["dW"] is not None])])
        last = meas[-1]
        p.text(last[0], last[1], name.split(",")[0], anchor="end", dy=-10)
        for r in rr:
            rows.append([name.split(",")[0], r["h"], f2(r["dW"]), f2(r["se"]), f2(r["pred_dW"])])
    return (legend([(n, c) for _, n, c in fams] + [("dashed: the RTL prediction, made before the run", "--faint")])
            + p.svg("Hamming ladder") , table(["ladder", "h", "measured W above h0", "SE", "predicted W"], rows, num=(1, 2, 3, 4)))


def chart_ord(R):
    cards = [(c, R["cards"][c]) for c in ("aifoundry3", "aifoundry2") if c in R["cards"] and R["cards"][c].get("ord")]
    cats = []
    for pos in (0, 19):
        for o in ("binary", "shuffled", "maxflip"):
            cats.append((pos, o))
    allv = []
    for _, C in cards:
        for pos in (0, 19):
            for o in ("binary", "shuffled", "maxflip"):
                q = C["ord"].get(pos, {}).get(o) or C["ord"].get(str(pos), {}).get(o)
                if q:
                    allv += [q["W"] + (q["se"] or 0), q["W"] - (q["se"] or 0)]
    labels = [f"{'bits 0–3' if pos == 0 else 'bits 19–22'}: {o.replace('maxflip', 'max-flip')}" for pos, o in cats]
    short = [o.replace("maxflip", "max-flip") for _, o in cats]
    p = Plot(0, 1, min(0, min(allv or [0])), max(allv or [1]) * 1.15, xcat=short, xlabel="order of the same 16 A values",
             ylabel="watts above Gray order", yfmt="{:g}")
    rows = []
    top = max(allv or [1]) * 1.12
    p.text(1, top, "changing bits 0–3", anchor="middle", cls="")
    p.text(4, top, "changing bits 19–22", anchor="middle", cls="")
    p.parts.append(f'<line class="grid" x1="{(p.X(2) + p.X(3)) / 2:.1f}" x2="{(p.X(2) + p.X(3)) / 2:.1f}" y1="{p.mt}" y2="{p.h - p.mb}"/>')
    cols = {"aifoundry3": "--s1", "aifoundry2": "--s2"}
    for k, (card, C) in enumerate(cards):
        for i, (pos, o) in enumerate(cats):
            q = C["ord"].get(pos, {}).get(o) or C["ord"].get(str(pos), {}).get(o)
            if not q:
                continue
            clock = C["clock_mhz"]
            p.bar(i, q["W"], q["se"], cols[card], f"{card} ({clock} MHz), {labels[i]}: {q['W']:+.3f} W ± {q['se'] or 0:.3f} over {q['n']} passes; predicted {q['pred_W']:+.3f} W",
                  k=k, nk=len(cards), label=f"{q['W']:+.2f}" if o == "maxflip" else None)
            rows.append([card, clock, labels[i], q["extra_A_bits_per_op"], f2(q["W"], 3), f2(q["se"], 3), q["n"], f2(q["pred_W"], 3)])
    return (legend([(f"{c} ({C['clock_mhz']} MHz)", cols[c]) for c, C in cards]) + p.svg("Same arithmetic, different order"),
            table(["card", "MHz", "order", "extra A bits per op", "W above Gray", "SE", "passes", "predicted W"], rows, num=(1, 3, 4, 5, 6, 7)))


def chart_ec(C, man):
    fams = [("xin", "XOR, inputs flip, result constant", "--s1"), ("ain", "AND, inputs flip, result constant", "--s3"),
            ("xio", "XOR, inputs and result flip (result alternates with 0)", "--s2"), ("xnz", "XOR, inputs and result flip, result never 0", "--s4")]
    pts = {}
    for f, _, _ in fams:
        z = "ain_h0" if f == "ain" else "xin_h0"
        ps = [(0.0, 0.0, None, "zero")]
        for n, it in man.items():
            if it.get("family") == f and n in C["items"] and n != z and C["items"][n].get("d_p80") is not None:
                ps.append((it["per_op"]["in"], C["items"][n]["d_p80"], C["items"][n]["d_p80_se"], n))
        pts[f] = sorted(ps)
    ys = [y for v in pts.values() for _, y, _, _ in v]
    p = Plot(0, 512, min(0, min(ys)), max(ys) * 1.1, xlabel="read-port bits that flip per instruction",
             ylabel="watts above the no-flip rung", xticks=[0, 64, 128, 192, 256, 320, 384, 448, 512])
    rows = []
    for f, name, col in fams:
        v = pts[f]
        if len(v) < 2:
            continue
        p.line([(x, y) for x, y, _, _ in v], col)
        p.dots([(x, y, e) for x, y, e, _ in v[1:]], col, [f"{n}: {y:+.3f} W" + (f" ± {e:.3f}" if e else "") for x, y, e, n in v[1:]],
               shape="square" if f in ("xio", "xnz") else "circle")
        for x, y, e, n in v[1:]:
            rows.append([n, man[n]["op"], int(man[n]["per_op"]["in"]), int(man[n]["per_op"]["out"]), f2(y, 3), f2(e, 3)])
    return legend([(n, c) for _, n, c in fams]) + p.svg("One bit, one gate"), table(["item", "op", "port bits/op", "result bits/op", "W above zero", "SE"], rows, num=(2, 3, 4, 5))


def chart_bits(C):
    bits = sorted(((int(b), q) for b, q in C["bits"].items()), key=lambda t: -t[0])
    field = lambda b: "sign" if b == 31 else ("exponent" if b >= 23 else "mantissa")
    col = {"sign": "--s2", "exponent": "--s3", "mantissa": "--s1"}
    cats = [f"{b}" for b, _ in bits]
    ys = [q["dW"] + (q["se"] or 0) for _, q in bits]
    p = Plot(0, 1, 0, max(ys) * 1.15, xcat=cats, xlabel="the B bit that flips (31 sign, 23 exponent, 22–0 mantissa)",
             ylabel="watts above constant operands", yfmt="{:g}")
    rows = []
    for i, (b, q) in enumerate(bits):
        p.bar(i, q["dW"], q["se"], col[field(b)], f"bit {b} ({field(b)}): {q['dW']:+.2f} W ± {q['se'] or 0:.2f}; predicted {q['pred_dW']:+.2f} W", label=f"{q['dW']:.1f}")
        rows.append([b, field(b), f2(q["dW"]), f2(q["se"]), q["n"], f2(q["pred_dW"])])
    return (legend([("sign", "--s2"), ("exponent", "--s3"), ("mantissa", "--s1")]) + p.svg("Which bit"),
            table(["bit", "field", "W above constant", "SE", "passes", "predicted W"], rows, num=(0, 2, 3, 4, 5)))


def chart_v2(R):
    order = [c for c in ("aifoundry3", "aifoundry1-c0", "aifoundry2") if c in R.get("v2", {})]
    col = {"aifoundry3": "--s1", "aifoundry1-c0": "--s3", "aifoundry2": "--s2"}
    xs = [R["v2"][c]["v"] ** 2 for c in order]
    ser = [("xin_rail_J", "input-port bit (XOR ladder)", "circle"), ("lq_h2_h8_rail_J", "B mantissa bit, quiet multiply-add (h 2 → 8)", "square")]
    ys = [R["v2"][c][k] * 1e15 for c in order for k, _, _ in ser if R["v2"][c].get(k)]
    if not ys:
        return "", ""
    p = Plot(0, max(xs) * 1.08, 0, max(ys) * 1.15, xlabel="rail voltage squared, V² (cards at 0.52, 0.60, 0.62 V)",
             ylabel="fJ per flipped bit (minion rail)", xfmt="{:.2f}")
    rows = []
    for k, name, shape in ser:
        ref = R["v2"].get("aifoundry3", {}).get(k)
        if ref:
            v0 = R["v2"]["aifoundry3"]["v"] ** 2
            p.line([(0, 0), (max(xs) * 1.05, ref * 1e15 * max(xs) * 1.05 / v0)], "--faint", dash=True, width=1.2)
        for c in order:
            e = R["v2"][c].get(k)
            if e:
                p.dots([(R["v2"][c]["v"] ** 2, e * 1e15, None)], col[c],
                       [f"{c}: {e * 1e15:.1f} fJ at {R['v2'][c]['v'] * 1000:.0f} mV ({R['v2'][c]['clock']} MHz); ratio to aifoundry3 {R['v2'][c].get(k + '_ratio') or 1:.2f}, V² ratio {R['v2'][c]['v2_ratio']:.2f}"],
                       shape=shape)
                rows.append([name, c, R["v2"][c]["clock"], f2(R["v2"][c]["v"] * 1000, 0), f2(e * 1e15, 1), f2(R["v2"][c].get(k + "_ratio"), 2), f2(R["v2"][c]["v2_ratio"], 2)])
    return (legend([(c, col[c]) for c in order] + [("dashed: proportional to V², through aifoundry3", "--faint")]) + p.svg("Does a flip cost ½CV²?"),
            table(["bit", "card", "MHz", "mV", "fJ per bit (minion rail)", "ratio to aifoundry3", "V² ratio"], rows, num=(2, 3, 4, 5, 6)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hl", required=True)
    ap.add_argument("--gen", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = json.load(open(a.hl))
    man = {it["name"]: it for it in json.load(open(a.gen + "/manifest.json"))["items"]}
    T = json.load(open(a.text))
    C3 = R["cards"]["aifoundry3"]
    figs = {}
    figs["ladder"] = chart_ladders(C3, man)
    figs["ord"] = chart_ord(R)
    figs["ec"] = chart_ec(C3, man)
    figs["bits"] = chart_bits(C3 if C3.get("bits") else R["cards"].get("aifoundry1-c0", C3))
    figs["v2"] = chart_v2(R)

    def fig(key, caption):
        svg, tab = figs[key]
        if not svg:
            return ""
        return f'<figure>{svg}<figcaption>{caption}</figcaption><details><summary>The numbers</summary>{tab}</details></figure>'

    body = T["body"]
    for key in ("ladder", "ord", "ec", "bits", "v2"):
        body = body.replace("{{fig:" + key + "}}", fig(key, T["captions"][key]))
    import re as _re
    seen = set()

    def anchor(m):
        tag, rest = m.group(1), m.group(2)
        if "data-ss-id" in rest:
            return m.group(0)
        tail = body_src[m.end():m.end() + 160]
        words = _re.sub(r"<[^>]+>|&[a-z#0-9]+;", " ", tail)
        slug = "-".join(_re.findall(r"[a-z0-9]+", words.lower())[:5]) or tag
        base, k = f"{tag}-{slug}"[:48], 2
        sid = base
        while sid in seen:
            sid, k = f"{base}-{k}", k + 1
        seen.add(sid)
        return f'<{tag} data-ss-id="{sid}"{rest}>'

    body_src = body
    body = _re.sub(r"<(h2|h3|p|figure|ul|div class=\"tablewrap\"|div class=\"stats\")((?:\s[^>]*)?)>", lambda m: anchor(m) if not m.group(1).startswith("div") else
                   m.group(0).replace("<div", f'<div data-ss-id="{("stats" if "stats" in m.group(1) else "table") + "-" + str(len(seen))}"', 1) if seen.add(("stats" if "stats" in m.group(1) else "table") + "-" + str(len(seen))) is None else m.group(0), body)
    out = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(T['title'])}</title><meta name="description" content="{esc(T['description'])}">
<style>{CSS}</style></head><body><main>
<h1>{esc(T['title'])}</h1>
<p class="nav" data-ss-id="nav-lab-dashboard" data-ss-react="off"><a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard">← AI Foundry lab dashboard</a> › <a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard#worklog">Worklog</a></p>
<p class="byline">{T['byline']}</p>
{body}
</main><div id="tip" role="tooltip"></div><script>{JS}</script></body></html>
"""
    open(a.out, "w").write(out)
    print(f"wrote {a.out} ({len(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
