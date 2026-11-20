#!/usr/bin/env python3
"""Build the matmul model report's page (second version) from this folder's README.md and figures. Desk; standard library only; deterministic.

    /usr/bin/python3 -I -B build_page.py [--folder <this folder>] --out <index.html> [--check]

The page is one self-contained HTML file (no request leaves the page): the README rendered by a small Markdown reader for the subset
the README uses (headings, paragraphs, lists, tables, a quote, a code block, bold, italics, code and links), each figure embedded as an
image (the SVG's dark-mode block dropped, since the page is light), every relative link rewritten to the file on the lab's GitHub main
(blob/main for a file, tree/main for a folder), and every wide table in its own horizontal scroll box. With --check it builds into memory
and exits 1 if <out> differs from what it would write.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import base64
import html
import os
import posixpath
import re
import sys

REPO_URL = "https://github.com/yaroslavvb/et-soc1-prototyping"
HERE = "docs/reports/data/2026-11-19-matmul-model-v2"
TITLE = "The lab's matmul model, MM1, second version"
DESC = ("MM1, the lab's matmul model for the ET-SoC-1, second version: a GEMM's cycles, joules and transistor switches from its sizes, "
        "format, data and the kernel's operations; MM1-v3 blind on two cards (E213), the switch count checked through energy, MM1-v3.1's "
        "declared refit and its blind day (E215), and two candidate terms frozen before it.")

CSS = """
:root{--ink:#1d1d1b;--ink2:#52514e;--muted:#6f6e69;--rule:#e1e0d9;--acc:#2a78d6;--bg:#ffffff;--soft:#f6f6f4;color-scheme:light}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:780px;width:100%;margin:0 auto;padding:24px 16px 64px}
h1{font-size:clamp(24px,5vw,32px);line-height:1.2;margin:0 0 12px}
h2{font-size:clamp(20px,4vw,24px);line-height:1.25;margin:40px 0 10px;padding-top:12px;border-top:1px solid var(--rule)}
h3{font-size:18px;margin:28px 0 8px}
p,li{margin:0 0 12px}
ul,ol{padding-left:22px;margin:0 0 14px}
a{color:var(--acc);text-decoration:underline;text-underline-offset:2px;overflow-wrap:anywhere}
code{font:0.88em/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--soft);padding:1px 4px;border-radius:4px;overflow-wrap:anywhere}
pre{background:var(--soft);padding:12px;border-radius:8px;overflow-x:auto;font-size:13px;line-height:1.45}
pre code{background:none;padding:0;overflow-wrap:normal;white-space:pre}
blockquote{margin:0 0 14px;padding:4px 0 4px 14px;border-left:3px solid var(--acc);color:var(--ink2)}
.tw{overflow-x:auto;margin:0 0 16px;border:1px solid var(--rule);border-radius:8px}
table{border-collapse:collapse;font-size:14px;line-height:1.35;min-width:100%}
th,td{padding:6px 8px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}
th{background:var(--soft);font-weight:600}
td{font-variant-numeric:tabular-nums}
figure{margin:18px 0 22px;text-align:center}
figure img{max-width:100%;width:400px;height:auto}
.lede{color:var(--ink2);font-size:15px}
footer{margin-top:40px;color:var(--muted);font-size:14px}
"""


def strip_dark(svg):
    return re.sub(r"\s*@media \(prefers-color-scheme: dark\)\{.*?\n  \}", "", svg, flags=re.S)


def svg_title(svg):
    m = re.search(r"<title[^>]*>(.*?)</title>", svg, re.S)
    return html.unescape(m.group(1)) if m else "figure"


def link_target(href):
    """A README link -> the page's link: external links unchanged, relative ones to the file on GitHub main."""
    if re.match(r"^[a-z]+://", href) or href.startswith("#"):
        return href
    p = posixpath.normpath(posixpath.join(HERE, href))
    if p.startswith(".."):
        raise SystemExit(f"link outside the repository: {href}")
    kind = "tree" if href.endswith("/") else "blob"
    return f"{REPO_URL}/{kind}/main/{p}"


def inline(s):
    """Inline Markdown -> HTML. Links and code spans become placeholders first (a link's text may hold code; a code span's text is
    literal), then bold and italics run over the whole line, then the placeholders come back."""
    ph = []

    def keep(h):
        ph.append(h)
        return "\x00%d\x00" % (len(ph) - 1)

    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: keep('<a href="%s">%s</a>' % (html.escape(link_target(m.group(2))), inline(m.group(1)))), s)
    s = re.sub(r"`([^`]*)`", lambda m: keep("<code>" + html.escape(m.group(1), quote=False) + "</code>"), s)
    t = html.escape(s, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    while "\x00" in t:
        t = re.sub("\x00(\\d+)\x00", lambda m: ph[int(m.group(1))], t)
    return t


def render(md, folder):
    lines = md.split("\n")
    out, i, n = [], 0, len(lines)
    para = []

    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(x.strip() for x in para)) + "</p>")
            para.clear()

    while i < n:
        ln = lines[i]
        if not ln.strip():
            flush_para()
            i += 1
            continue
        if ln.startswith("```"):
            flush_para()
            j = i + 1
            buf = []
            while j < n and not lines[j].startswith("```"):
                buf.append(lines[j])
                j += 1
            out.append("<pre><code>" + html.escape("\n".join(buf), quote=False) + "</code></pre>")
            i = j + 1
            continue
        m = re.match(r"^(#{1,3}) (.*)$", ln)
        if m:
            flush_para()
            lvl = len(m.group(1))
            txt = m.group(2)
            hid = re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")[:60]
            out.append(f'<h{lvl} id="{hid}">' + inline(txt) + f"</h{lvl}>")
            i += 1
            continue
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", ln)
        if m:
            flush_para()
            svg = open(os.path.join(folder, m.group(2)), encoding="utf-8").read()
            svg = strip_dark(svg)
            b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
            alt = svg_title(svg)
            out.append(f'<figure><img src="data:image/svg+xml;base64,{b64}" alt="{html.escape(alt)}" width="400"></figure>')
            i += 1
            continue
        if ln.startswith(">"):
            flush_para()
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i][1:].strip())
                i += 1
            out.append("<blockquote><p>" + inline(" ".join(buf)) + "</p></blockquote>")
            continue
        if ln.startswith("|"):
            flush_para()
            rows = []
            while i < n and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(set(c) <= set("-: ") for c in r)]
            t = ["<div class=\"tw\"><table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"]
            for r in body:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.) (.*)$", ln)
        if m and not para:
            ordered = m.group(2)[0].isdigit()
            items = []
            while i < n:
                mm = re.match(r"^([-*]|\d+\.) (.*)$", lines[i])
                if mm and ((mm.group(1)[0].isdigit()) == ordered):
                    items.append([mm.group(2)])
                    i += 1
                elif items and lines[i].startswith("  ") and lines[i].strip():
                    sub = re.match(r"^\s+([-*]) (.*)$", lines[i])
                    if sub:
                        items[-1].append(("SUB", sub.group(2)))
                    elif items[-1] and isinstance(items[-1][-1], tuple):
                        items[-1][-1] = ("SUB", items[-1][-1][1] + " " + lines[i].strip())
                    else:
                        items[-1].append(lines[i].strip())
                    i += 1
                else:
                    break
            tag = "ol" if ordered else "ul"
            h = [f"<{tag}>"]
            for it in items:
                main_txt = " ".join(x for x in it if isinstance(x, str))
                subs = [x[1] for x in it if isinstance(x, tuple)]
                h.append("<li>" + inline(main_txt))
                if subs:
                    h.append("<ul>" + "".join("<li>" + inline(s) + "</li>" for s in subs) + "</ul>")
                h.append("</li>")
            h.append(f"</{tag}>")
            out.append("".join(h))
            continue
        para.append(ln)
        i += 1
    flush_para()
    return "\n".join(out)


def summary_first(md):
    """For the page, the summary ("On one screen") comes right after the title and the header paragraph, before the labels, the words
    and the meter, which follow it unchanged; every other part keeps the README's order."""
    i, j = md.index("\n**Labels.**"), md.index("\n## On one screen")
    k = md.index("\n## 1. ")
    return md[:i] + md[j:k] + md[i:j] + md[k:]


def build(folder):
    md = open(os.path.join(folder, "README.md"), encoding="utf-8").read()
    md = md.replace("\nSPDX-License-Identifier: Apache-2.0\n", "\n")
    md = summary_first(md)
    body = render(md, folder)
    src = f"{REPO_URL}/tree/main/{HERE}"
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "<meta name=\"color-scheme\" content=\"light\">\n"
            f"<title>{html.escape(TITLE)}</title>\n<meta name=\"description\" content=\"{html.escape(DESC)}\">\n"
            f"<style>{CSS}</style>\n</head>\n<body>\n<main>\n{body}\n"
            f"<footer>Built by <a href=\"{src}/build_page.py\">build_page.py</a> from <a href=\"{src}/README.md\">README.md</a> "
            f"in <a href=\"{src}\">{HERE}</a> on the lab's GitHub main. SPDX-License-Identifier: Apache-2.0</footer>\n"
            "</main>\n</body>\n</html>\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--out", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    page = build(a.folder)
    if a.check:
        cur = open(a.out, encoding="utf-8").read() if os.path.isfile(a.out) else None
        print("SAME" if cur == page else "DIFFERS")
        return 0 if cur == page else 1
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(page)
    print(f"wrote {a.out} ({len(page.encode('utf-8')):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
