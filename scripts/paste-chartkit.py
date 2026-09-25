#!/usr/bin/env python3
"""Paste the shared chart toolkit into standalone report pages (the ones not built by scripts/build-report.py).

    scripts/paste-chartkit.py PAGE.html [PAGE.html ...]           insert or refresh the block
    scripts/paste-chartkit.py --check PAGE.html [PAGE.html ...]   exit 1 if any page's block is missing or stale

The block sits just before </head>, between <!-- chartkit:begin --> and <!-- chartkit:end -->, and holds
  1. token aliases: the template tokens the kit uses (--c1..--c5, --c7, --ref, --ink, --ink-2, --muted, --grid,
     --axis, --surface, --page, --border) that the page does not define, mapped to the page's own name for the same
     thing (--et -> --c1, --text-primary -> --ink, ...) or else set to the template's light and dark values, in the
     three :root blocks the template uses (light; prefers-color-scheme: dark unless data-theme="light"; data-theme="dark");
  2. the kit's CSS, copied from docs/reports/sources/report.template.html between chartkit:css:begin and :end;
  3. docs/reports/sources/chartkit.js, which defines the global CK.
Running it again refreshes the block in place; nothing outside the markers is ever changed (checked before writing).
Page scripts that use CK must come after </head>, which every standalone page's scripts do."""
import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "reports", "sources")
BEGIN, END = "<!-- chartkit:begin -->", "<!-- chartkit:end -->"
BLOCK = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.S)
TOKENS = ["--c1", "--c2", "--c3", "--c4", "--c5", "--c7", "--ref", "--ink", "--ink-2", "--muted", "--grid", "--axis",
          "--surface", "--page", "--border"]
# The page's own name for a token, in order of preference, when the page lacks the template's name.
ALIASES = {"--c1": ["--et", "--accent"], "--c2": ["--et2"], "--c3": ["--et3"], "--ink": ["--text-primary"],
           "--ink-2": ["--text-secondary"], "--muted": ["--text-muted", "--ink-3"], "--grid": ["--hairline", "--line"],
           "--axis": ["--rule"], "--page": ["--surface"]}


def template_parts():
    tpl = open(os.path.join(SRC, "report.template.html")).read()
    m = re.search(r"/\* chartkit:css:begin.*?\*/\n(.*?)/\* chartkit:css:end \*/", tpl, re.S)
    if not m:
        raise SystemExit("report.template.html has no chartkit:css block")
    light = re.search(r":root \{(.*?)\}", tpl, re.S).group(1)
    dark = re.search(r':root\[data-theme="dark"\] \{(.*?)\}', tpl, re.S).group(1)
    val = lambda block: dict(re.findall(r"(--[\w-]+):\s*([^;]+);", block))
    js = open(os.path.join(SRC, "chartkit.js")).read()
    for bad in ("</script", "<!--", "-->"):
        if bad in js.lower():
            raise SystemExit(f"chartkit.js contains {bad!r}, which would break an inline <script>")
    if re.search(r"__[A-Z]+__", js + m.group(1)):
        raise SystemExit("chartkit.js or its CSS contains a __PLACEHOLDER__ token that page builders would replace")
    return m.group(1), val(light), val(dark), js


def page_tokens(html):
    """Custom properties the page itself defines (outside any chartkit block)."""
    css = "".join(re.findall(r"<style[^>]*>(.*?)</style>", BLOCK.sub("", html), re.S))
    return set(re.findall(r"(--[\w-]+)\s*:", css))


def block_for(html):
    css, light, dark, js = template_parts()
    have = page_tokens(html)
    alias, fixed = [], []
    for t in TOKENS:
        if t in have:
            continue
        src = next((a for a in ALIASES.get(t, []) if a in have), None)
        if src:
            alias.append(f"{t}: var({src})")
        elif t in light and t in dark:
            fixed.append(t)
        else:
            raise SystemExit(f"no value for {t}")
    root = alias + [f"{t}: {light[t]}" for t in fixed]
    dk = "; ".join(f"{t}: {dark[t]}" for t in fixed)
    lines = [BEGIN, "<!-- pasted by scripts/paste-chartkit.py from docs/reports/sources/{chartkit.js, report.template.html};"
             " do not edit here -->", "<style>"]
    if root:
        lines.append("/* the template tokens the chart kit uses, in this page's names */")
        lines.append(":root { " + "; ".join(root) + "; }")
    if dk:
        lines.append('@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { ' + dk + "; } }")
        lines.append(':root[data-theme="dark"] { ' + dk + "; }")
    lines += [css.rstrip("\n"), "</style>", "<script>", js.rstrip("\n"), "</script>", END]
    return "\n".join(lines) + "\n"


def pasted(html):
    new_block = block_for(html)
    found = BLOCK.findall(html)
    if len(found) > 1:
        raise SystemExit("more than one chartkit block")
    if found:
        out = BLOCK.sub(lambda m: new_block, html, count=1)
    else:
        if html.count("</head>") != 1:
            raise SystemExit("expected exactly one </head>")
        out = html.replace("</head>", new_block + "</head>", 1)
    if BLOCK.sub("", out) != BLOCK.sub("", html):  # nothing outside the markers may change
        raise SystemExit("internal error: the page outside the chartkit block would change")
    return out


def main(argv):
    check = "--check" in argv
    pages = [a for a in argv if a != "--check"]
    if not pages:
        raise SystemExit(__doc__)
    stale = 0
    for p in pages:
        html = open(p, encoding="utf-8").read()
        out = pasted(html)
        if out == html:
            print(f"{p}: chartkit block up to date")
        elif check:
            stale += 1
            print(f"{p}: chartkit block {'stale' if BEGIN in html else 'missing'}")
        else:
            open(p, "w", encoding="utf-8").write(out)
            print(f"{p}: chartkit block {'refreshed' if BEGIN in html else 'inserted'}")
    sys.exit(1 if stale else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
