#!/usr/bin/env python3
"""Assemble a report from docs/reports/sources/<name>.{body.html,script.js,meta.json} plus a data JSON.

    scripts/build-report.py <name> <data.json> <out.html>

meta.json holds {"title", "description"}. The shared shell and CSS are in report.template.html; the body closes
<main> itself, and the script sees the data as the constant D.

TeX between $$ or \\( \\) is rendered to inline SVG by scripts/tex2svg.js, which needs mathjax-full:
    npm install --no-save mathjax-full"""
import json
import os
import re
import subprocess
import sys

S = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "reports", "sources")
name, data_path, out = sys.argv[1:4]
meta = json.load(open(os.path.join(S, name + ".meta.json")))
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
        raise SystemExit("tex2svg.js failed (run `npm install --no-save mathjax-full`):\n" + proc.stderr[-2000:])
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

html = (tpl.replace("__TITLE__", meta["title"]).replace("__DESC__", meta["description"])
        .replace("__BODY__", body)
        .replace("__DATA__", json.dumps(json.load(open(data_path)), separators=(",", ":")))
        .replace("__SCRIPT__", open(os.path.join(S, name + ".script.js")).read()))
open(out, "w").write(html)
print("wrote", out, len(html), "bytes" + (f", {n_math} equations rendered to SVG" if n_math else ""))
