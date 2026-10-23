#!/usr/bin/env python3
"""E63 report page: docs/reports/2026-10-23-camera-hamming-ladder/index.html, from lockin_hlc.py's and
figures_hlc.py's output.

    python3 tools/claims-v3/hlc/build_page_hlc.py --lockin <session 1 lockin.json> [--lockin2 <session 2 lockin.json>]
        --figures <figures.json> --text <page text .json> --out <index.html>

The charts are inline SVG from E60's page builder (tools/claims-v3/hl/build_page.py: the same palette, light and dark,
tooltips and data tables); the maps are figures_hlc.py's PNGs, copied beside the page as img/. The prose comes from
--text, a JSON of named HTML fragments written after the analysis, from its numbers.
"""
import argparse
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hl"))
from build_page import CSS, JS, Plot, esc, legend, table, f2  # noqa: E402

COL = {"E63-TOP": "--s1", "E63-TOP2": "--s1", "E63-MID": "--s2", "E63-NULL": "--faint"}
NAME = {"E63-TOP": "top rung, lq_h23", "E63-TOP2": "top rung again", "E63-MID": "middle rung, lq_h8",
        "E63-NULL": "null: ones vs pi"}

EXTRA_CSS = """
.maps{display:grid;grid-template-columns:repeat(auto-fit,minmax(14rem,1fr));gap:10px}
.maps figure{margin:0;padding:8px}.maps img{width:100%;height:auto;display:block;border-radius:4px}
.key{width:100%;max-width:28rem;height:auto;display:block;margin:.4rem auto 0}
.verdict{font-weight:600}.pass{color:var(--s3)}.fail{color:var(--s2)}
"""


def along(st, u):
    z = complex(st["Z_re"], st["Z_im"])
    return (z * u.conjugate()).real, math.sqrt(0.5 * (st["se_re"] ** 2 + st["se_im"] ** 2))


def top_phase(res):
    tops = [res["blocks"][b]["roi"] for b in ("E63-TOP", "E63-TOP2") if "roi" in res["blocks"].get(b, {})]
    z = sum(complex(t["Z_re"], t["Z_im"]) for t in tops) / len(tops)
    return z / abs(z)


def chart_watts(sessions):
    """Camera amplitude at f (along each session's top-rung phase) against the watts switched (the board's step),
    every block of every session on one pair of axes: session 1 as circles, session 2 as squares."""
    pts = []
    for si, (label, res) in enumerate(sessions):
        u = top_phase(res)
        for b in ("E63-NULL", "E63-MID", "E63-TOP", "E63-TOP2"):
            r = res["blocks"].get(b)
            if not r or "roi" not in r:
                continue
            y, ey = along(r["roi"], u)
            x, ex = r["board_step_w"]["mean"], r["board_step_w"]["se"]
            pts.append((si, label, b, x, ex, y, ey))
    xmax = math.ceil(max(p[3] for p in pts) * 1.1)
    ymax = 50 * math.ceil(max(p[5] + p[6] for p in pts) * 1.05 / 50)
    ymin = 50 * math.floor(min(0, min(p[5] - p[6] for p in pts)) / 50)
    p = Plot(-0.3, xmax, ymin, ymax, xlabel="watts switched: the board's step between the two arms",
             ylabel="camera, mK at 0.05 Hz", yfmt="{:g}", xticks=list(range(0, xmax + 1)),
             yticks=list(range(ymin, ymax + 1, 50)))
    rungs = [q for q in pts if q[2] != "E63-NULL"]
    k = sum(q[3] * q[5] for q in rungs) / sum(q[3] ** 2 for q in rungs)      # least squares through zero
    p.line([(0, 0), (xmax, k * xmax)], "--faint", dash=True, width=1.5)
    rows = []
    for (si, label, b, x, ex, y, ey) in pts:
        tip = f"{label}, {NAME[b]}: {x:+.2f} W switched, camera {y:+.1f} ± {ey:.1f} mK"
        p.dots([(x, y, ey)], COL[b], [tip], r=6 if si == 0 else 5, shape="circle" if si == 0 else "square")
        rows.append([label, NAME[b], f"{x:+.3f}", f"{ex:.3f}", f"{y:+.1f}", f"{ey:.1f}"])
    s0 = [q for q in pts if q[0] == 0]
    for (si, label, b, x, ex, y, ey) in s0:
        if b in ("E63-TOP", "E63-MID", "E63-NULL"):
            p.text(x, y, NAME[b].split(",")[0], anchor="end" if b == "E63-TOP" else "start", dy=-12)
    leg = legend([(NAME[b], COL[b]) for b in ("E63-TOP", "E63-MID", "E63-NULL")]
                 + [(f"dashed: {k:.1f} mK per watt, through zero", "--faint")])
    leg += ('<div class="legend"><span>● ' + esc(sessions[0][0]) + '</span>'
            + (f'<span>■ {esc(sessions[1][0])}</span>' if len(sessions) > 1 else "") + "</div>")
    return leg + p.svg("Camera amplitude against watts switched"), table(
        ["session", "block", "board step, W", "SE", "camera along the top rung's phase, mK", "SE"], rows,
        num=(2, 3, 4, 5)), k


def chart_cycle(fig, key, unit, ylabel, blocks, title):
    C = fig["cycles"]
    t = C["E63-TOP"]["t_s"]
    ys = [v for b in blocks if b in C and key in C[b] for v in C[b][key]]
    lo, hi = min(ys), max(ys)
    pad = 0.12 * (hi - lo or 1)
    p = Plot(0, 20, lo - pad, hi + pad, h=260, xlabel="seconds into the 20 s cycle (the rung runs in the first half)",
             ylabel=ylabel, xticks=[0, 5, 10, 15, 20])
    p.parts.insert(0, f'<rect x="{p.X(0):.1f}" y="{p.mt}" width="{p.X(10) - p.X(0):.1f}" height="{p.h - p.mt - p.mb}" '
                      f'fill="var(--grid)" opacity=".55"/>')
    rows = []
    for b in blocks:
        if b not in C or key not in C[b]:
            continue
        pts = list(zip(t, C[b][key]))
        p.line(pts, COL[b], width=2)
        rows.append([NAME[b]] + [f"{v:+.{1 if unit == 'mK' else 2}f}" for v in C[b][key][::4]])
    head = ["block"] + [f"{x:g} s" for x in t[::4]]
    return legend([(NAME[b], COL[b]) for b in blocks if b in C]) + p.svg(title), table(head, rows,
                                                                                    num=tuple(range(1, len(head))))


def chart_laps(res):
    """Every analysed lap's complex amplitude at f, ROI mean: the in-phase and quadrature parts."""
    pts = {}
    for b in ("E63-NULL", "E63-MID", "E63-TOP", "E63-TOP2"):
        r = res["blocks"].get(b)
        if r and "per_lap" in r:
            pts[b] = [complex(a, c) for a, c in r["per_lap"]["roi"]]
    allv = [v for vs in pts.values() for v in vs]
    m = max(max(abs(v.real), abs(v.imag)) for v in allv) * 1.1
    p = Plot(-m, m, -m, m, w=460, h=460, xlabel="in phase with the switching, mK",
             ylabel="a quarter cycle later, mK", yfmt="{:g}")
    rows = []
    for b, vs in pts.items():
        p.dots([(v.real, v.imag, None) for v in vs], COL[b],
               [f"{NAME[b]}, lap {i + 1}: {v.real:+.0f}, {v.imag:+.0f} mK" for i, v in enumerate(vs)],
               r=3.5, shape="square" if b == "E63-TOP2" else "circle")
        mean = sum(vs) / len(vs)
        rows.append([NAME[b], len(vs), f"{mean.real:+.1f}", f"{mean.imag:+.1f}", f"{abs(mean):.1f}",
                     f"{math.degrees(math.atan2(mean.imag, mean.real)):.0f}"])
    return legend([(NAME[b], COL[b]) for b in pts]) + p.svg("Each lap's amplitude at 0.05 Hz"), table(
        ["block", "laps", "in phase, mK", "quarter cycle later, mK", "amplitude, mK", "phase, degrees"], rows,
        num=(1, 2, 3, 4, 5))


def ids(body):
    """Stable data-ss-id anchors on the page's blocks (spacesheep comments attach to them)."""
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
    ap.add_argument("--lockin", required=True, help="session 1's lockin.json")
    ap.add_argument("--lockin2", default=None, help="session 2's lockin.json (amendment A1)")
    ap.add_argument("--figures", required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = json.load(open(a.lockin))
    sessions = [("session 1, 256 minions", res)]
    if a.lockin2:
        sessions.append(("session 2, 192 minions", json.load(open(a.lockin2))))
    fig = json.load(open(a.figures))
    T = json.load(open(a.text))
    figs = {}
    figs["watts"] = chart_watts(sessions)[:2]
    figs["power"] = chart_cycle(fig, "power_w", "W", "board power, W from its mean", ["E63-TOP", "E63-MID", "E63-NULL"],
                                "The board's power over one cycle")
    figs["roi"] = chart_cycle(fig, "roi_mk", "mK", "back of the board, mK", ["E63-TOP", "E63-MID", "E63-NULL"],
                              "The back of the board over one cycle")
    figs["laps"] = chart_laps(res)

    def figure(key, caption):
        svg, tab = figs[key]
        return (f'<figure>{svg}<figcaption>{caption}</figcaption>'
                f'<details><summary>The numbers</summary>{tab}</details></figure>')

    body = T["body"]
    for key in figs:
        body = body.replace("{{fig:" + key + "}}", figure(key, T["captions"][key]))
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
