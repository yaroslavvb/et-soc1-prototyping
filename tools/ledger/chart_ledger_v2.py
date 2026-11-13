#!/usr/bin/env python3
"""Draw the load ledger v2's one chart, forecast against measured, from chart-data-v2.json alone (Q166, step 1).

Writes chart-v2.html beside the data file: one self-contained page (inline SVG, no external file, no network), a
log-log scatter with the line of agreement and a +-10% wash, every scored number one dot (colour and shape by how
honest the score is), v1's committed forecasts as grey rings joined to v2's, a hover readout and the full table.
Retitled and relabelled by fix-q166 (Thu 12 Nov 2026): the DRAM arm of E101 is post hoc for the awake rule, E37
depends on that rule, and E136 carries a dated correction (every one in chart-data-v2.json's labels).

    python3 -I -B tools/ledger/chart_ledger_v2.py [--data PATH] [--out PATH]

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import html
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
D = os.path.join(REPO, "docs", "reports", "data", "2026-11-12-q166-ledger-v2")

KEEP = {  # (load, quantity, seconds) drawn on the chart; every row stays in the table
    ("E39", "W over idle per unit of useful-slot fraction", "given"),
    ("E39", "W over idle at zero useful slots", "given"),
    ("E37", "J over idle per op", "given"),
    ("E37", "W over the pre-launch idle", "given"),
    ("E59", "J a solve over idle", "given"),
    ("E59", "J a solve over idle", "forecast"),
    ("E59", "J a solve with the card at rest", "given"),
    ("E59", "J a solve with the card at rest", "forecast"),
}


def group(r):
    if r["load"] in ("E39", "E37", "E59"):
        return "heldout"
    if str(r["label"]).startswith("in sample"):
        return "insample"
    if str(r["label"]).startswith("post hoc"):
        return "posthoc"
    return "beside"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(D, "chart-data-v2.json"))
    ap.add_argument("--out", default=os.path.join(D, "chart-v2.html"))
    a = ap.parse_args()
    rows = json.load(open(a.data))["rows"]
    pts = []
    for r in rows:
        if r["load"] in ("E39", "E37", "E59") and (r["load"], r["quantity"], r["seconds"]) not in KEEP:
            continue
        if r["measured"] is None or r["measured"] <= 0 or r["forecast"] <= 0:
            continue
        pts.append(r)
    lo, hi = 0.5, 400.0
    W, H = 720, 560
    ml, mr, mt, mb = 64, 24, 20, 56
    pw, ph = W - ml - mr, H - mt - mb

    def X(v):
        return ml + (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * pw

    def Y(v):
        return mt + ph - (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * ph

    ticks = [0.5, 1, 2, 5, 10, 20, 50, 100, 200]
    svg = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="ctitle cdesc" class="plot">']
    svg.append('<title id="ctitle">Ledger v2: forecast against measured</title>')
    svg.append('<desc id="cdesc">Log-log scatter of every scored number: forecast on the vertical axis, measured on the '
               'horizontal, each in its own unit (watts, joules or nanojoules). The diagonal is agreement; the band is '
               'plus or minus ten percent. The full table follows the chart.</desc>')
    for t in ticks:
        svg.append(f'<line class="grid" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{mt}" y2="{mt + ph}"/>')
        svg.append(f'<line class="grid" x1="{ml}" x2="{ml + pw}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/>')
        svg.append(f'<text class="tick" x="{X(t):.1f}" y="{mt + ph + 18}" text-anchor="middle">{t:g}</text>')
        svg.append(f'<text class="tick" x="{ml - 8}" y="{Y(t) + 4:.1f}" text-anchor="end">{t:g}</text>')
    poly = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in [(lo, lo * 1.1), (hi / 1.1, hi), (hi, hi / 1.1), (lo * 1.1, lo)])
    svg.append(f'<polygon class="wash" points="{poly}"/>')
    svg.append(f'<line class="diag" x1="{X(lo):.1f}" y1="{Y(lo):.1f}" x2="{X(hi):.1f}" y2="{Y(hi):.1f}"/>')
    svg.append(f'<line class="axis" x1="{ml}" x2="{ml + pw}" y1="{mt + ph}" y2="{mt + ph}"/>')
    svg.append(f'<line class="axis" x1="{ml}" x2="{ml}" y1="{mt}" y2="{mt + ph}"/>')
    svg.append(f'<text class="axl" x="{ml + pw / 2:.1f}" y="{H - 14}" text-anchor="middle">measured (each number in its '
               f'own unit: W, J or nJ)</text>')
    svg.append(f'<text class="axl" transform="translate(16,{mt + ph / 2:.1f}) rotate(-90)" text-anchor="middle">forecast'
               f'</text>')
    # v1's committed forecasts: grey rings joined to v2's dot
    for r in pts:
        if r.get("v1_forecast") and lo <= r["v1_forecast"] <= hi:   # off-scale v1 values stay in the table
            svg.append(f'<line class="v1link" x1="{X(r["measured"]):.1f}" y1="{Y(r["v1_forecast"]):.1f}" '
                       f'x2="{X(r["measured"]):.1f}" y2="{Y(r["forecast"]):.1f}"/>')
            svg.append(f'<circle class="v1" cx="{X(r["measured"]):.1f}" cy="{Y(r["v1_forecast"]):.1f}" r="4.5"/>')
    data = []
    for i, r in enumerate(pts):
        x, y = X(r["measured"]), Y(r["forecast"])
        g = group(r)
        if g == "heldout":
            mark = f'<circle class="m {g}" cx="{x:.1f}" cy="{y:.1f}" r="5"/>'
        elif g == "beside":
            mark = f'<rect class="m {g}" x="{x - 4.5:.1f}" y="{y - 4.5:.1f}" width="9" height="9" rx="1.5"/>'
        elif g == "posthoc":
            mark = f'<rect class="m {g}" x="{x - 4.5:.1f}" y="{y - 4.5:.1f}" width="9" height="9" rx="1.5"/>'
        else:
            mark = (f'<polygon class="m {g}" points="{x:.1f},{y - 6:.1f} {x + 5.5:.1f},{y + 4:.1f} '
                    f'{x - 5.5:.1f},{y + 4:.1f}"/>')
        svg.append(f'<g class="pt" tabindex="0" data-i="{i}">{mark}<circle class="hit" cx="{x:.1f}" cy="{y:.1f}" '
                   f'r="12"/></g>')
        data.append({"load": r["load"], "name": r["name"], "q": r["quantity"], "u": r["unit"], "s": r["seconds"],
                     "m": r["measured"], "f": r["forecast"], "e": r["error_pct"], "lab": r["label"],
                     "v1": r.get("v1_forecast")})
    # direct labels on the held-out loads' three clusters only
    for txt, xv, yv in (("E37, nJ an op", 120.0, 300.0),):
        svg.append(f'<text class="dl" x="{X(xv):.1f}" y="{Y(yv):.1f}">{html.escape(txt)}</text>')
    svg.append("</svg>")

    trs = []
    for r in rows:
        e = "" if r["error_pct"] is None else f'{r["error_pct"]:+.1f}%'
        v1 = "" if r.get("v1_forecast") is None else f'{r["v1_forecast"]:.3g}'
        trs.append("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in (
            r["load"], r["name"], r["quantity"], r["seconds"], f'{r["measured"]:.4g} {r["unit"]}',
            f'{r["forecast"]:.4g}', e, v1, r["label"], r["measured_source"])) + "</tr>")

    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ledger v2 forecasts</title>
<style>
html {{ color-scheme: light; --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781; --grid:#e1e0d9;
  --axis:#c3c2b7; --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --wash:rgba(42,120,214,0.08); --ring:#898781; }}
@media (prefers-color-scheme: dark) {{ html:not([data-theme="light"]) {{ color-scheme: dark; --surface:#1a1a19;
  --ink:#f0efec; --ink2:#c3c2b7; --grid:#2c2c2a; --axis:#383835; --s1:#3987e5; --s2:#d95926; --s3:#199e70;
  --wash:rgba(57,135,229,0.12); }} }}
html[data-theme="dark"] {{ color-scheme: dark; --surface:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --grid:#2c2c2a;
  --axis:#383835; --s1:#3987e5; --s2:#d95926; --s3:#199e70; --wash:rgba(57,135,229,0.12); }}
body {{ margin:0; background:var(--surface); color:var(--ink); font:16px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif; }}
main {{ max-width:760px; margin:0 auto; padding:16px; }}
h1 {{ font-size:clamp(20px,4vw,26px); margin:8px 0 4px; }} p {{ color:var(--ink2); margin:6px 0; }}
.legend {{ display:flex; flex-wrap:wrap; gap:6px 18px; margin:12px 0; color:var(--ink2); font-size:14px; }}
.legend span {{ display:inline-flex; align-items:center; gap:6px; }}
svg.plot {{ width:100%; height:auto; display:block; }}
.grid {{ stroke:var(--grid); stroke-width:1; }} .axis {{ stroke:var(--axis); stroke-width:1; }}
.diag {{ stroke:var(--muted); stroke-width:1.5; }} .wash {{ fill:var(--wash); }}
.tick {{ fill:var(--muted); font-size:12px; font-variant-numeric:tabular-nums; }} .axl {{ fill:var(--ink2); font-size:13px; }}
.dl {{ fill:var(--ink2); font-size:12px; }}
.m {{ stroke:var(--surface); stroke-width:2; }} .heldout {{ fill:var(--s1); }} .beside {{ fill:var(--s2); }}
.insample {{ fill:var(--s3); }} .posthoc {{ fill:var(--surface); stroke:var(--s2); stroke-width:2; }}
.hit {{ fill:transparent; }} .v1 {{ fill:none; stroke:var(--ring); stroke-width:1.5; }}
.v1link {{ stroke:var(--ring); stroke-width:1; }}
.pt:hover .m, .pt:focus .m {{ stroke:var(--ink); }} .pt:focus {{ outline:none; }}
#tip {{ position:fixed; pointer-events:none; background:var(--surface); color:var(--ink); border:1px solid var(--axis);
  border-radius:6px; padding:8px 10px; font-size:13px; max-width:300px; display:none; box-shadow:0 2px 8px rgba(0,0,0,.12); }}
#tip b {{ font-size:15px; }}
.tablewrap {{ overflow-x:auto; margin-top:16px; }} table {{ border-collapse:collapse; font-size:12px; min-width:900px; }}
td, th {{ border-bottom:1px solid var(--grid); padding:4px 6px; text-align:left; vertical-align:top; }}
th {{ color:var(--ink2); font-weight:600; }} td:nth-child(5), td:nth-child(6), td:nth-child(7) {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
</style></head><body><main>
<h1>Sparse parity's joules over idle land within 5%; the DRAM stream reads 13-14% high</h1>
<p>The load ledger v2 (Q166) against every number it was scored on, frozen before any score. Blue: the three held-out
loads (held out, not blind). Orange: beside them, held out by price or by kind. Hollow orange: E101's DRAM arm, post
hoc for the awake rule. Green: beside them, in sample. Grey rings: v1's committed forecasts of 26 Oct, joined to v2's.</p>
<p>Within 5% is sparse parity's joules over idle, given its seconds; with the card at rest and the seconds forecast,
L1 reads 14.4% low and the halves 6.0% low. E37's forecast depends on the awake rule, which was set during the build
after arithmetic beside E101's DRAM arm, the same benchmark: without the rule E37 reads 27-28% high an op, and the
DRAM arm 36% (zeros) and 16% (random) high. Sparse parity's op cycles sit inside two prices (3-5% of each solve);
priced once, its joules over idle read 6-8% low. These are dated corrections, post hoc (posthoc-v2.json).</p>
<div class="legend" aria-hidden="true">
<span><svg width="14" height="14"><circle cx="7" cy="7" r="5" fill="var(--s1)"/></svg>E39, E37, E59: held out, not blind</span>
<span><svg width="14" height="14"><rect x="2.5" y="2.5" width="9" height="9" rx="1.5" fill="var(--s2)"/></svg>E101 loop, E136, E86, E95: beside, held out by price or kind</span>
<span><svg width="14" height="14"><rect x="2.5" y="2.5" width="9" height="9" rx="1.5" fill="none" stroke="var(--s2)" stroke-width="2"/></svg>E101 DRAM arm: post hoc for the awake rule</span>
<span><svg width="14" height="14"><polygon points="7,1 12.5,11 1.5,11" fill="var(--s3)"/></svg>E101 L2-streamed: in sample</span>
<span><svg width="14" height="14"><circle cx="7" cy="7" r="4.5" fill="none" stroke="var(--ring)" stroke-width="1.5"/></svg>v1's forecast</span>
</div>
{''.join(svg)}
<p>The diagonal is agreement and the wash is plus or minus 10%. v1's forecast of card 1's E39 intercept, 0.017 W,
is below the axis and is in the table only. The axes are logarithmic, and each number is in its own unit:
watts for powers, joules a solve for sparse parity, nanojoules an op for E37. The E39 intercept on aifoundry3 (measured
0.93 W, forecast 2.08 W) sits furthest off: E39's own record says its reduction reads that card 0.81-1.34 W low.
E136 (dated correction, post hoc): its frozen label said the L3 row's share of random minus zeros is zero by construction;
it is -0.12 W, and without it fp32 reads -2.6%, fp16 +2.4% and int8 -9.6% (frozen: -3.3%, +1.7%, -11.5%).</p>
<div class="tablewrap"><table><thead><tr><th>load</th><th>number</th><th>quantity</th><th>seconds</th><th>measured</th>
<th>forecast</th><th>error</th><th>v1</th><th>label</th><th>measured at</th></tr></thead><tbody>
{''.join(trs)}
</tbody></table></div>
<div id="tip" role="status"></div>
</main>
<script>
const D = {json.dumps(data)};
const tip = document.getElementById('tip');
function show(ev, g) {{
  const d = D[+g.dataset.i]; tip.textContent = '';
  const b = document.createElement('b'); b.textContent = 'forecast ' + d.f.toPrecision(4) + ' ' + d.u +
    ' against ' + d.m.toPrecision(4) + (d.e === null ? '' : ' (' + (d.e > 0 ? '+' : '') + d.e.toFixed(1) + '%)');
  tip.appendChild(b);
  for (const t of [d.load + ' ' + d.name, d.q + ', seconds ' + d.s, d.v1 ? 'v1 ' + d.v1.toPrecision(4) : '', d.lab]) {{
    if (!t) continue; const p = document.createElement('div'); p.textContent = t; tip.appendChild(p); }}
  const r = g.getBoundingClientRect(); tip.style.display = 'block';
  const x = (ev && ev.clientX) || r.left, y = (ev && ev.clientY) || r.top;
  tip.style.left = Math.min(x + 12, window.innerWidth - 310) + 'px'; tip.style.top = (y + 12) + 'px';
}}
document.querySelectorAll('.pt').forEach(g => {{
  g.addEventListener('pointermove', e => show(e, g)); g.addEventListener('focus', () => show(null, g));
  g.addEventListener('pointerleave', () => tip.style.display = 'none'); g.addEventListener('blur', () => tip.style.display = 'none');
}});
</script>
<!-- SPDX-License-Identifier: Apache-2.0 -->
</body></html>
"""
    with open(a.out, "w") as f:
        f.write(page)
    print("wrote", os.path.relpath(a.out, REPO), "points", len(pts), "table rows", len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
