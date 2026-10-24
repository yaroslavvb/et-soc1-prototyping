#!/usr/bin/env python3
"""E64 report page: docs/reports/2026-10-23-horace-power-limit/index.html, from reduce_hpl.py's results and
surface_hpl.py's figures.

    python3 tools/claims-v3/hpl/build_page_hpl.py --results results.json --figures figures.json
        --text page_text_hpl.json --out <index.html>

Charts are inline SVG from E60's page builder (tools/claims-v3/hl/build_page.py: the palette, light and dark,
tooltips, data tables), as E63's page. The prose comes from --text, a JSON of named HTML fragments written after
the analysis, from its numbers; {{fig:<key>}} in the body places a figure.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hl"))
from build_page import CSS, JS, Plot, esc, legend, table, f2  # noqa: E402

EXTRA_CSS = """
.verdict{font-weight:600}.pass{color:var(--s3)}.fail{color:var(--s2)}
.chart .wall{stroke:var(--s2);stroke-width:1.5;stroke-dasharray:6 4}
.chart .cell{stroke:none}
.swatch{display:inline-block;width:14px;height:10px;border-radius:2px;margin-right:4px;vertical-align:0}
"""
TYPE_COL = {"fp32": "--s1", "fp16": "--s3", "int8": "--s4"}
VAL_NAME = {"zeros": "zeros", "sparse75": "75% zeros", "ones": "ones", "signs": "random signs ±1",
            "pow2": "random powers of 2", "a_randn_b_ones": "A random, B ones", "a_ones_b_randn": "A ones, B random",
            "mant": "random mantissas", "uniform": "uniform [0,1)", "randn": "random normal"}


def by(runs, block):
    return [r for r in runs if r["block"] == block]


def chart_ladder(F, R):
    """Mean clock after the start ramp against the work's board power at 800 MHz, every LAD and MIN run, with the
    governor model's curve over the same axis."""
    runs = [r for r in F["runs"] if r["block"] in ("LAD", "MIN") and r.get("p800_w") and r.get("mhz_steady")]
    p = Plot(30, 90, 600, 820, xlabel="what the work draws at 800 MHz, board W", ylabel="mean clock after the ramp, MHz",
             xticks=[30, 40, 50, 60, 65, 70, 80, 90], yticks=[600, 650, 700, 750, 800])
    p.parts.append(f'<line class="wall" x1="{p.X(65):.1f}" x2="{p.X(65):.1f}" y1="{p.mt}" y2="{p.h - p.mb}"/>')
    p.text(65, 815, "65 W TDP", anchor="middle", cls="lab", dy=-2)
    S = F.get("surface")
    if S:
        i65 = S["tdp_w"].index(min(S["tdp_w"], key=lambda t: abs(t - 65)))
        pts = [(x, y) for x, y in zip(S["p800_of_c"], S["mhz"][i65]) if 30 <= x <= 90]
        p.line(pts, "--faint", dash=True, width=1.5)
    rows = []
    for r in sorted(runs, key=lambda r: r["p800_w"]):
        col = "--s1" if r["block"] == "LAD" else "--s3"
        nm = VAL_NAME.get(r["values"], r["values"]) + ("" if r["minions"] == 1024 else f", {r['minions']} minions")
        tip = f"{nm} (pass {r['rep']}): {r['p800_w']:.1f} W at 800 MHz, mean clock {r['mhz_steady']:.0f} MHz, " \
              f"{r['rate_t']:.2f} TFLOPS over the whole run"
        p.dots([(r["p800_w"], r["mhz_steady"], None)], col, [tip], r=5.5, shape="circle" if r["rep"] == 1 else "square")
        rows.append([nm, r["rep"], f2(r["p800_w"], 1), f2(r["mhz_steady"], 0), f2(r["rate_t"], 2),
                     (r.get("events") or {}).get("power_down", 0), r.get("die_start"), r.get("die_max")])
    leg = legend([("fp32 operand patterns, all 1,024 minions", "--s1"), ("random normal on 768, 640, 512 minions", "--s3"),
                  ("dashed: the governor model at 65 W", "--faint")])
    return leg + p.svg("Mean clock against the work's power at 800 MHz"), table(
        ["operands", "pass", "W at 800 MHz", "mean MHz after 1.5 s", "TFLOPS, whole run", "power steps down",
         "die at start, °C", "die max, °C"], rows, num=(1, 2, 3, 4, 5, 6, 7))


def chart_traces(R, F):
    """The clock through three 6 s runs from a cool die: zeros, A random B ones, random normal (pass 1)."""
    want = [("zeros", "--faint"), ("a_randn_b_ones", "--s4"), ("randn", "--s2")]
    runs = {r["values"]: r for r in R["runs"] if r["block"] == "LAD" and r["rep"] == 1}
    p = Plot(-0.5, 7.5, 560, 830, h=300, xlabel="seconds from the launch", ylabel="minion clock, MHz",
             xticks=[0, 1, 2, 3, 4, 5, 6, 7], yticks=[600, 700, 800])
    rows = []
    for k, (v, col) in enumerate(want):
        r = runs.get(v)
        if not r:
            continue
        off = (1 - k) * 9
        pts = []
        prev = None
        for t, die, w, mhz in r["trace"]:
            if mhz is None or not (-0.5 <= t <= 7.5):
                continue
            if prev is not None:
                pts.append((t, prev + off))
            pts.append((t, mhz + off))
            prev = mhz
        p.line(pts, col, width=2.2)
        for e in r.get("event_list") or []:
            if e["kind"] in ("power_down", "thermal_down") and e.get("t_s") is not None and -0.5 <= e["t_s"] <= 7.5:
                tip = (f"{VAL_NAME[v]}: {'power' if e['kind'] == 'power_down' else 'thermal'} step down at "
                       f"{e['t_s']:.2f} s, governor's power {e['pwr_mw'] / 1000:.2f} W, die {e['die']} °C"
                       if e["kind"] == "power_down" else f"{VAL_NAME[v]}: thermal step down at {e['t_s']:.2f} s, {e['T']} °C")
                p.dots([(e["t_s"], 822 - 4 * k, None)], col, [tip], r=3.2,
                       shape="square" if e["kind"] == "thermal_down" else "circle")
        rows.append([VAL_NAME[v], f2(r.get("p800_w"), 1), f2(r.get("mhz_mean"), 0), f2(r.get("rate_t"), 2),
                     (r.get("events") or {}).get("power_down", 0), r.get("die_start"), r.get("die_max")])
    leg = legend([(VAL_NAME[v], c) for v, c in want] + [("dots on top: each power step down the SP logged", "--muted")])
    return leg + p.svg("The clock through three runs from a cool die"), table(
        ["operands", "W at 800 MHz", "mean MHz", "TFLOPS", "power steps down", "die at start, °C", "die max, °C"], rows,
        num=(1, 2, 3, 4, 5, 6))


def chart_map(R):
    """Every governor step of every run: where the die and the governor's power stood when it moved."""
    pts = {"power_down": [], "power_up": [], "thermal_down": []}
    for r in R["runs"]:
        if r["block"] == "SMOKE":
            continue
        for e in r.get("event_list") or []:
            if not e.get("in_work") or e.get("die") is None:
                continue
            if e["kind"] in ("power_down", "power_up") and e.get("pwr_mw"):
                pts[e["kind"]].append((e["die"], e["pwr_mw"] / 1000.0, r["label"], r["block"]))
            elif e["kind"] == "thermal_down":
                w = next((x["sp_w"] for x in r["event_list"] if x["kind"] == "pstat" and x.get("ts") and e.get("ts")
                          and 0 <= x["ts"] - e["ts"] < 200000), None)
                pts["thermal_down"].append((e["T"] or e["die"], w, r["label"], r["block"]))
    allx = [x for v in pts.values() for x, *_ in v] or [50, 70]
    ally = [y for v in pts.values() for _, y, *_ in v if y is not None] or [30, 90]
    p = Plot(min(48, min(allx) - 1), max(72, max(allx) + 1), min(30, min(ally) - 2), max(70, max(ally) + 2),
             xlabel="die reading when the governor moved, °C (mean of 34 sensors)",
             ylabel="the governor's power reading, W")
    p.parts.append(f'<line class="wall" x1="{p.X(65.5):.1f}" x2="{p.X(65.5):.1f}" y1="{p.mt}" y2="{p.h - p.mb}"/>')
    p.parts.append(f'<line class="wall" x1="{p.ml}" x2="{p.w - p.mr}" y1="{p.Y(65):.1f}" y2="{p.Y(65):.1f}"/>')
    p.text(65.6, p.ylo + 1, "65 °C", anchor="start")
    p.text(p.xlo + 0.3, 65.6, "65 W", anchor="start", dy=-4)
    cols = {"power_down": "--s2", "power_up": "--s1", "thermal_down": "--s3"}
    names = {"power_down": "power step down", "power_up": "power step up", "thermal_down": "thermal step down"}
    rows = []
    for k, v in pts.items():
        dots = [(x, y, None) for x, y, *_ in v if y is not None]
        tips = [f"{names[k]}: die {x} °C, {y:.2f} W ({lab}, {blk})" for x, y, lab, blk in v if y is not None]
        p.dots(dots, cols[k], tips, r=3.6, shape="square" if k == "thermal_down" else "circle")
        rows.append([names[k], len(v), f2(min((x for x, *_ in v), default=None), 0),
                     f2(max((x for x, *_ in v), default=None), 0),
                     f2(min((y for _, y, *_ in v if y is not None), default=None), 2),
                     f2(max((y for _, y, *_ in v if y is not None), default=None), 2)])
    leg = legend([(names[k], cols[k]) for k in pts] + [("dashed: the two limits", "--s2")])
    return leg + p.svg("Every governor step, by the die's reading and the governor's power"), table(
        ["step", "count", "die min, °C", "die max, °C", "power min, W", "power max, W"], rows, num=(1, 2, 3, 4, 5))


def chart_sus(F):
    """The sustained runs: the mean clock in 2 s bins over about 80 s, every number type."""
    runs = [r for r in F["runs"] if r["block"] == "SUS" and r.get("sus_bins")]
    if not runs:
        return None
    p = Plot(0, 82, 580, 820, h=320, xlabel="seconds from the first launch (nine 8 s launch processes)",
             ylabel="mean clock in each 2 s, MHz", xticks=[0, 10, 20, 30, 40, 50, 60, 70, 80],
             yticks=[600, 650, 700, 750, 800])
    rows = []
    dash = {"zeros": True, "ones": False, "randn": False}
    for r in sorted(runs, key=lambda r: (r["type"], r["values"])):
        pts = [(b["t_s"] + 1, b["mhz"]) for b in r["sus_bins"]]
        if r["values"] == "ones":
            col = "--muted"
        else:
            col = TYPE_COL[r["type"]]
        p.line(pts, col if r["values"] != "zeros" else "--faint", dash=dash[r["values"]], width=2 if r["values"] == "randn" else 1.5)
        sl = r.get("sus_last") or {}
        rows.append([r["type"], r["values"], f2(r.get("sus_mhz_mean"), 0), f2(r.get("sus_rate_t"), 2),
                     f2(r.get("sus_rate_wall_t"), 2), f2(r.get("sus_die_mean"), 1), f2(r.get("sus_w_mean"), 1),
                     f2(sl.get("800"), 2), f2(sl.get("thermal"), 2), f2(sl.get("power"), 2)])
    leg = legend([("fp32 random", "--s1"), ("fp16 random", "--s3"), ("int8 random", "--s4"), ("ones (each type)", "--muted"),
                  ("dashed: zeros", "--faint")])
    return leg + p.svg("The clock through the sustained runs"), table(
        ["type", "operands", "mean MHz, last 40 s", "TFLOPS or TOPS, last 40 s (kernel)", "with the gaps between launches",
         "die °C", "board W", "share at 800 MHz", "below 800: thermal", "below 800: power"], rows,
        num=(2, 3, 4, 5, 6, 7, 8, 9))


def chart_types(F):
    """Speed by number type: on a cool die (the first seconds) and sustained (the last 40 s of SUS)."""
    cool = {}
    for r in F["runs"]:
        # the cool-die rate: each SUS run's first launch process, from 1.5 s to 8 s (it starts at 57 C or below)
        if r["block"] == "SUS" and r.get("first8_mhz"):
            cool.setdefault((r["type"], r["values"]), []).append(r["first8_mhz"])
    sus = {(r["type"], r["values"]): r for r in F["runs"] if r["block"] == "SUS"}
    cats = [(t, v) for t in ("fp32", "fp16", "int8") for v in ("zeros", "ones", "randn")]
    cats = [c for c in cats if c in sus or c in cool]
    if not cats:
        return None
    OPS = {"fp32": 8192, "fp16": 16384, "int8": 32768}
    CYC = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}

    def rate(t, mhz):
        return 1024 * OPS[t] / CYC[t] * mhz * 1e6 / 1e12
    vals = []
    for (t, v) in cats:
        cm = cool.get((t, v))
        c_rate = rate(t, sum(cm) / len(cm)) if cm and all(cm) else None
        s = sus.get((t, v))
        s_rate = s.get("sus_rate_t") if s else None
        vals.append((t, v, c_rate, s_rate, rate(t, 800.0)))
    short = {"zeros": "zeros", "ones": "ones", "randn": "random"}
    p = Plot(0, len(cats), 0, 105, h=360, mb=76, xcat=[short[v] for t, v in cats], ylabel="% of the type's rate at 800 MHz",
             yticks=[0, 25, 50, 75, 100])
    # the number type once under each group of three bars
    for typ in ("fp32", "fp16", "int8"):
        idx = [i for i, (t, v) in enumerate(cats) if t == typ]
        if idx:
            xm = (p.X(idx[0]) + p.X(idx[-1])) / 2
            p.parts.append(f'<text class="lab" x="{xm:.1f}" y="{p.h - p.mb + 42}" text-anchor="middle">{typ}</text>')
    rows = []
    unit = {"fp32": "TFLOPS", "fp16": "TFLOPS", "int8": "TOPS"}
    for i, (t, v, a, b, peak) in enumerate(vals):
        if a:
            p.bar(i, 100 * a / peak, None, TYPE_COL[t], f"{t} {v}: {a:.1f} {unit[t]} on a cool die "
                                                         f"({100 * a / peak:.0f}% of {peak:.1f})", k=0, nk=2)
        if b:
            p.bar(i, 100 * b / peak, None, "--faint", f"{t} {v}: {b:.1f} {unit[t]} sustained "
                                                      f"({100 * b / peak:.0f}% of {peak:.1f})", k=1, nk=2)
        rows.append([t, v, unit[t], f2(peak, 1), f2(a, 2), f2(b, 2), f2(b / a, 3) if a and b else "–"])
    leg = legend([("on a cool die: the first seconds (fp32 blue, fp16 green, int8 amber)", "--s1"),
                  ("sustained: the last 40 s of 80", "--faint")])
    return leg + p.svg("Speed by number type"), table(
        ["type", "operands", "unit", "at 800 MHz", "cool die", "sustained", "sustained ÷ cool"], rows, num=(3, 4, 5, 6))


def chart_surface(F):
    """The governor model's mean clock over the data's power at 800 MHz and the TDP: the power-limit surface."""
    S = F.get("surface")
    if not S:
        return None
    xs, ys, grid = S["p800_of_c"], S["tdp_w"], S["mhz"]
    p = Plot(min(xs), max(xs), min(ys), max(ys) + 2, h=420, xlabel="what the work draws at 800 MHz, board W (the data)",
             ylabel="power cap (TDP), W", xticks=[35, 45, 55, 65, 75, 85, 95], yticks=[30, 40, 50, 60, 65, 70, 80, 90])
    dx = (xs[1] - xs[0]) if len(xs) > 1 else 1
    dy = (ys[1] - ys[0]) if len(ys) > 1 else 1

    def shade(m):
        # 600 MHz -> s2 (warm), 800 -> s1 (cool) via opacity on two layers
        return (m - 600) / 200.0
    for j, cap in enumerate(ys):
        for i, x in enumerate(xs):
            m = grid[j][i]
            fr = max(0.0, min(1.0, shade(m)))
            x0, x1 = p.X(x - dx / 2), p.X(x + dx / 2)
            y0, y1 = p.Y(cap + dy / 2), p.Y(cap - dy / 2)
            tip = f"data at {x:.0f} W (800 MHz), cap {cap} W: mean clock {m:.0f} MHz, fp32 {1024 * 8192 / 546 * m / 1e6:.1f} TFLOPS"
            # opaque cells (the accent mixed into the card colour), overlapping by a hair, so no seam shows between them
            pct = round(100 * (0.08 + 0.85 * fr))
            p.parts.append(f'<rect class="cell" x="{x0:.2f}" y="{y0:.2f}" width="{x1 - x0 + 0.6:.2f}" height="{y1 - y0 + 0.6:.2f}" '
                           f'fill="color-mix(in srgb, var(--s1) {pct}%, var(--card))" shape-rendering="crispEdges" '
                           f'data-tip="{esc(tip)}"/>')
    p.parts.append(f'<line class="wall" x1="{p.ml}" x2="{p.w - p.mr}" y1="{p.Y(65):.1f}" y2="{p.Y(65):.1f}"/>')
    p.text(min(xs) + 1, 66, "the card's 65 W", anchor="start", dy=-4)
    T = F.get("thermal") or {}
    if T.get("cap_w_at_65_5"):
        c = T["cap_w_at_65_5"]
        if min(ys) <= c <= max(ys):
            p.parts.append(f'<line x1="{p.ml}" x2="{p.w - p.mr}" y1="{p.Y(c):.1f}" y2="{p.Y(c):.1f}" stroke="var(--s4)" '
                           f'stroke-width="2"/>')
            p.text(max(xs) - 1, c, f"sustained, 65 °C on this cooling: {c:.0f} W", anchor="end", dy=-5)
    runs = [r for r in F["runs"] if r["block"] in ("LAD", "MIN") and r.get("p800_w") and r.get("mhz_steady")]
    p.dots([(r["p800_w"], 65, None) for r in runs], "--ink",
           [f"measured: {VAL_NAME.get(r['values'], r['values'])}, {r['minions']} minions: {r['mhz_steady']:.0f} MHz"
            for r in runs], r=3)
    rows = [[cap] + [f"{grid[j][i]:.0f}" for i in range(0, len(xs), 5)] for j, cap in enumerate(ys) if cap % 10 == 0]
    head = ["cap W \\ data W"] + [f"{xs[i]:.0f}" for i in range(0, len(xs), 5)]
    leg = ('<div class="legend"><span><i style="background:var(--s1);opacity:.15"></i>600 MHz</span>'
           '<span><i style="background:var(--s1);opacity:.55"></i>700 MHz</span>'
           '<span><i style="background:var(--s1);opacity:.93"></i>800 MHz</span>'
           '<span>dots: the measured runs at 65 W</span></div>')
    return leg + p.svg("The power-limit surface: mean clock by the data's power and the cap"), table(
        head, rows, num=tuple(range(len(head))))


def ids(body):
    seen = {}

    def one(m):
        tag, rest = m.group(1), m.group(2)
        if "data-ss-id" in rest:
            return m.group(0)
        n = seen.get(tag, 0) + 1
        seen[tag] = n
        return f'<{tag} data-ss-id="{tag}-{n}"{rest}>'
    return re.sub(r"<(h2|h3|p|figure|ul|ol)((?:\s[^>]*)?)>", one, body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--figures", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = json.load(open(a.results))
    F = json.load(open(a.figures))
    T = json.load(open(a.text))
    figs = {"ladder": chart_ladder(F, R), "traces": chart_traces(R, F), "map": chart_map(R), "sus": chart_sus(F),
            "types": chart_types(F), "surface": chart_surface(F)}

    def figure(key, caption):
        if not figs.get(key):
            return f'<p class="note">(figure {key}: no data yet)</p>'
        svg, tab = figs[key]
        return (f'<figure>{svg}<figcaption>{caption}</figcaption>'
                f'<details><summary>The numbers</summary>{tab}</details></figure>')
    body = T["body"]
    for key in figs:
        body = body.replace("{{fig:" + key + "}}", figure(key, T["captions"].get(key, "")))
    body = ids(body)
    out = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(T['title'])}</title><meta name="description" content="{esc(T['description'])}">
<style>{CSS}{EXTRA_CSS}</style></head><body><main>
<h1 data-ss-id="title">{esc(T['title'])}</h1>
<p class="nav" data-ss-id="nav-lab-dashboard" data-ss-react="off"><a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard">← AI Foundry lab dashboard</a> › <a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard#worklog">Worklog</a></p>
<p class="byline" data-ss-id="byline">{T['byline']}</p>
{body}
</main><div id="tip" role="tooltip"></div><script>{JS}</script></body></html>
"""
    with open(a.out, "w") as f:
        f.write(out)
    print(f"wrote {a.out} ({len(out) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
