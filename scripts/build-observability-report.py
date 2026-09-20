#!/usr/bin/env python3
"""Assemble docs/reports/2026-09-20-et-soc1-limits-of-observability.html from its sources:
the template (CSS and shell), the body (prose), the data (ladder, steps, contrast) and the script."""
import json
import os

S = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "reports", "sources")
tpl = open(os.path.join(S, "limits-of-observability.template.html")).read()
body = open(os.path.join(S, "limits-of-observability.body.html")).read()
data = json.load(open(os.path.join(S, "limits-of-observability.data.json")))
script = open(os.path.join(S, "limits-of-observability.script.js")).read()
# the body closes <main> itself; the template's own </main> after the script is dropped
tpl = tpl.replace("</script>\n</main>\n</body>", "</script>\n</body>")
out = tpl.replace("__BODY__", body).replace("__DATA__", json.dumps(data, separators=(",", ":"))).replace("__SCRIPT__", script)
path = os.path.join(S, "..", "2026-09-20-et-soc1-limits-of-observability.html")
open(path, "w").write(out)
print("wrote", os.path.normpath(path), len(out), "bytes")
