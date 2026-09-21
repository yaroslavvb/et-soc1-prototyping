#!/usr/bin/env python3
"""Assemble a report from docs/reports/sources/<name>.{body.html,script.js,meta.json} plus a data JSON.

    scripts/build-report.py <name> <data.json> <out.html>

meta.json holds {"title", "description"}. The shared shell and CSS are in report.template.html; the body closes
<main> itself, and the script sees the data as the constant D."""
import json
import os
import sys

S = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "reports", "sources")
name, data_path, out = sys.argv[1:4]
meta = json.load(open(os.path.join(S, name + ".meta.json")))
tpl = open(os.path.join(S, "report.template.html")).read().replace("</script>\n</main>\n</body>", "</script>\n</body>")
html = (tpl.replace("__TITLE__", meta["title"]).replace("__DESC__", meta["description"])
        .replace("__BODY__", open(os.path.join(S, name + ".body.html")).read())
        .replace("__DATA__", json.dumps(json.load(open(data_path)), separators=(",", ":")))
        .replace("__SCRIPT__", open(os.path.join(S, name + ".script.js")).read()))
open(out, "w").write(html)
print("wrote", out, len(html), "bytes")
