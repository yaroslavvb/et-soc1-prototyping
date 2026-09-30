#!/usr/bin/env python3
"""Write the "New user? Start now" page's data from START.md, the agent brief.

    python3 docs/lab-start/make_page_data.py           # writes docs/reports/data/2026-09-30-lab-start/brief.json
    python3 docs/lab-start/make_page_data.py --check   # exit 1 if brief.json is stale

The page (docs/reports/sources/lab-start.*) shows START.md verbatim in its copy box and renders the same text below
it, so START.md is the only copy of the brief: edit it, run this, then rebuild the page (README.md here).
The card tiles at the top of the page come from CARDS below (facts of 30 September 2026, from AGENT.md §4 and
docs/findings/14-card-behaviour.md). No timestamps go into the output, so a rebuild with the same inputs is
byte-identical."""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(HERE, "START.md")
OUT = os.path.join(ROOT, "docs", "reports", "data", "2026-09-30-lab-start", "brief.json")

# One tile per card, in the chart toolkit's card ids (CK.card gives the colour). "use" is what a new user may do.
CARDS = [
    {"id": "aifoundry2", "host": "aifoundry2", "n": 0, "firmware": "1.3.1",
     "clock": "firmware DVFS, usually 600 MHz", "note": "the main card; a CI runner shares it", "use": True},
    {"id": "aifoundry3", "host": "aifoundry3", "n": 0, "firmware": "1.3.1",
     "clock": "pinned at 600 MHz", "note": "a demo service can use it without the lock", "use": True},
    {"id": "aifoundry1-c1", "host": "aifoundry1", "n": 1, "firmware": "1.2.0",
     "clock": "600 MHz always", "note": "select with ET_DEVICES=1; the host's disk is nearly full", "use": True},
    {"id": "aifoundry1-c0", "host": "aifoundry1", "n": 0, "firmware": "1.4.1",
     "clock": "idles at 300 MHz", "note": "overheats: nobody uses it", "use": False},
]


def build():
    md = open(SRC, encoding="utf-8").read()
    # The data is inlined in a <script>; the build's json.dumps does not escape "<", so refuse what would end it.
    for bad in ("</script", "<!--"):
        if bad in md.lower():
            raise SystemExit(f"START.md contains {bad!r}, which would break the page's inline script")
    words = len(md.split())
    prose = len(re.sub(r"```.*?```", "", md, flags=re.S).split())
    return {
        "source": "docs/lab-start/START.md",
        "md": md,
        "sha256": hashlib.sha256(md.encode("utf-8")).hexdigest(),
        "words": words,
        "words_prose": prose,
        "placeholders": sorted(set(re.findall(r"<(login|host|N)>", md))),
        "cards": CARDS,
    }


def main():
    data = build()
    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    if "--check" in sys.argv[1:]:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != text:
            print(f"{os.path.relpath(OUT, ROOT)} is stale: run python3 docs/lab-start/make_page_data.py")
            sys.exit(1)
        print("brief.json is current")
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(text)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {data['words']} words ({data['words_prose']} outside code blocks), "
          f"sha256 {data['sha256'][:12]}")


if __name__ == "__main__":
    main()
