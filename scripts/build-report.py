#!/usr/bin/env python3
"""Assemble a report from docs/reports/sources/<name>.{body.html,script.js,meta.json} plus a data JSON.

    scripts/build-report.py <name> <data.json> <out.html>

meta.json holds {"title", "description"}. The shared shell and CSS are in report.template.html; the body closes
<main> itself, and the script sees the data as the constant D. The shared chart toolkit, sources/chartkit.js, is
inlined in its own script just before the page script, so the script also sees CK (PLAN2 §2.5 lists its API).

TeX between $$ or \\( \\) is rendered to inline SVG by scripts/tex2svg.js, which needs mathjax-full. package.json
pins it to 3.2.1, the version that built the published pages (3.2.2 gives byte-identical SVGs); install it once, at
the repo root, with
    npm ci
In a git worktree without its own node_modules, set NODE_PATH to a checkout's node_modules.

A page whose script needs a block that a separate step adds to its data refuses to build without it (REQUIRED below:
dvfs-leakage needs `cards`, which tools/ettelem/build_cards_data.py --merge writes into dvfs.json)."""
import json
import os
import re
import subprocess
import sys

S = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "reports", "sources")
name, data_path, out = sys.argv[1:4]
meta = json.load(open(os.path.join(S, name + ".meta.json")))
# Data blocks a page's script cannot run without, and the step that adds each. Without this check the page builds,
# then throws in the reader's browser and leaves whole sections empty.
REQUIRED = {
    "dvfs-leakage": {"cards": "run tools/ettelem/build_cards_data.py ... --merge <dvfs.json> after analyze_dvfs.py "
                              "(the full chain is in the page's Method section and docs/getting-started.md)"},
}
data = json.load(open(data_path))
missing = [f"no '{k}' block: {how}" for k, how in REQUIRED.get(name, {}).items() if k not in data]
if missing:
    raise SystemExit(f"{data_path} is incomplete for {name}:\n  " + "\n  ".join(missing))
tpl = open(os.path.join(S, "report.template.html")).read().replace("</script>\n</main>\n</body>", "</script>\n</body>")
body = open(os.path.join(S, name + ".body.html")).read()
# Math is rendered to standalone SVG here, at build time: the hosts these reports are published to block
# external scripts, so a runtime MathJax from a CDN would leave the equations as raw TeX. Display math is
# $$ ... $$, inline math is \( ... \). Anything inside <pre> or <code> is left alone.
CODE = re.compile(r"<pre\b.*?</pre>|<code\b.*?</code>", re.S)
MATH = re.compile(r"\$\$(.+?)\$\$|\\\((.+?)\\\)", re.S)


def render_math(html):
    """Replace every TeX fragment outside code with the SVG MathJax renders for it."""
    spans, pos, parts = [], 0, []
    for m in CODE.finditer(html):  # split into (text, code, text, code, ...)
        parts.append(("t", html[pos:m.start()]))
        parts.append(("c", m.group(0)))
        pos = m.end()
    parts.append(("t", html[pos:]))
    items = []
    for kind, chunk in parts:
        if kind == "t":
            for m in MATH.finditer(chunk):
                items.append({"tex": (m.group(1) or m.group(2)).strip(), "display": m.group(1) is not None})
    if not items:
        return html, 0
    proc = subprocess.run(["node", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex2svg.js")],
                          input=json.dumps({"items": items}), capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit("tex2svg.js failed (run `npm ci` at the repo root; it installs mathjax-full 3.2.1):\n"
                         + proc.stderr[-2000:])
    svgs = iter(json.loads(proc.stdout)["svg"])
    out = []
    for kind, chunk in parts:
        if kind == "c":
            out.append(chunk)
            continue
        out.append(MATH.sub(lambda m: ('<span class="math-display">%s</span>' if m.group(1) is not None
                                       else '<span class="math-inline">%s</span>') % next(svgs), chunk))
    return "".join(out), len(items)


body, n_math = render_math(body)

html = (tpl.replace("__CHARTKIT__", open(os.path.join(S, "chartkit.js")).read())
        .replace("__TITLE__", meta["title"]).replace("__DESC__", meta["description"])
        .replace("__BODY__", body)
        .replace("__DATA__", json.dumps(data, separators=(",", ":")))
        .replace("__SCRIPT__", open(os.path.join(S, name + ".script.js")).read()))
open(out, "w").write(html)
print("wrote", out, len(html), "bytes" + (f", {n_math} equations rendered to SVG" if n_math else ""))
