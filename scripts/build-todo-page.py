#!/usr/bin/env python3
"""Build docs/reports/TODO.md into a standalone HTML page for spacesheep (needs `pip install markdown`)."""
import html, re, sys, markdown

src = sys.argv[1] if len(sys.argv) > 1 else "docs/reports/TODO.md"
out = sys.argv[2] if len(sys.argv) > 2 else "docs/reports/2026-09-26-review-todo.html"
text = open(src, encoding="utf-8").read()
text = re.sub(r"^(\s*)- \[ \] ", r"\1- ☐ ", text, flags=re.M)
text = re.sub(r"^(\s*)- \[x\] ", r"\1- ☑ ", text, flags=re.M)
body = markdown.markdown(text, extensions=["extra", "sane_lists", "toc"])
title = "ET-SoC-1 review: the TODO list"
page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1f1f1c;--muted:#5d5b55;--line:#dedbd2;--accent:#2f5d8a;--code:#f0eee8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#17171a;--fg:#e8e6e1;--muted:#a3a09a;--line:#34343a;--accent:#8fb6de;--code:#24242a}}}}
body{{background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;margin:0}}
main{{max-width:52rem;margin:0 auto;padding:2rem 16px 4rem}}
h1{{font-size:1.7rem;line-height:1.25}} h2{{margin-top:2.5rem;border-bottom:1px solid var(--line);padding-bottom:.3rem}}
h3{{margin-top:1.8rem}} a{{color:var(--accent)}} li{{margin:.25rem 0}}
code{{background:var(--code);padding:.05rem .3rem;border-radius:4px;font-size:.88em;overflow-wrap:anywhere}}
.note{{color:var(--muted);font-size:.9rem}}
</style></head><body><main>
<p class="note">Rendered from <code>docs/reports/TODO.md</code> in
<a href="https://github.com/yaroslavvb/et-soc1-prototyping">yaroslavvb/et-soc1-prototyping</a> by
<code>scripts/build-todo-page.py</code>. Part of the
<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#reports">ET-SoC-1 measurement reports</a>.</p>
{body}
</main></body></html>
"""
open(out, "w", encoding="utf-8").write(page)
print(f"wrote {out} ({len(page):,} bytes)")
