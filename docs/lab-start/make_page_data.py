#!/usr/bin/env python3
"""Write the "New user? Start now" page's data from START.md, the agent brief.

    python3 docs/lab-start/make_page_data.py           # writes docs/reports/data/2026-09-30-lab-start/brief.json
    python3 docs/lab-start/make_page_data.py --check   # exit 1 if brief.json is stale

The page (docs/reports/sources/lab-start.*) shows START.md verbatim in its one copy box, with the viewer's username
filled into `<login>` (the only placeholder the page fills; `<host>` and `<N>` stay, for the agent's own choice), so
START.md is the only copy of the prompt: edit it, run this, then rebuild the page (README.md here).
The card tiles at the top of the page come from CARDS below (facts of 2 October 2026, from AGENT.md §4 and
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
# The agent, not the person, chooses among the usable ones (START.md, step 2).
CARDS = [
    {"id": "aifoundry2", "host": "aifoundry2", "n": 0, "firmware": "1.3.1",
     "clock": "DVFS 600–800 MHz, usually 600", "note": "out of service since 2 Oct: overheats at idle, drops off the bus",
     "use": False},
    {"id": "aifoundry3", "host": "aifoundry3", "n": 0, "firmware": "1.3.1",
     "clock": "pinned at 600 MHz", "note": "a demo service can use it without the lock", "use": True},
    {"id": "aifoundry1-c1", "host": "aifoundry1", "n": 1, "firmware": "1.2.0",
     "clock": "600 MHz until 30 Sep, not rechecked since", "note": "select with ET_DEVICES=1; a CI runner shares the host",
     "use": True},
    {"id": "aifoundry1-c0", "host": "aifoundry1", "n": 0, "firmware": "1.4.1",
     "clock": "idles at 300 MHz", "note": "select with ET_DEVICES=0; fan replaced 2 Oct: 52–56 °C under load",
     "use": True},
]


FILLS = ["login"]  # the placeholders the page fills from its one field


def build():
    md = open(SRC, encoding="utf-8").read()
    # The data is inlined in a <script>; the build's json.dumps does not escape "<", so refuse what would end it.
    for bad in ("</script", "<!--"):
        if bad in md.lower():
            raise SystemExit(f"START.md contains {bad!r}, which would break the page's inline script")
    if "`<login>`" not in md.split("\n## ", 1)[0]:
        raise SystemExit("START.md's opening lines (the person's own words) must name `<login>`, which the page fills")
    m = re.search(r"^Version of ([^.,\n]+)", md, flags=re.M)
    if not m:
        raise SystemExit("START.md has no 'Version of <date>' line")
    words = len(md.split())
    prose = len(re.sub(r"```.*?```", "", md, flags=re.S).split())
    return {
        "source": "docs/lab-start/START.md",
        "md": md,
        "sha256": hashlib.sha256(md.encode("utf-8")).hexdigest(),
        "version": m.group(1).strip(),
        "words": words,
        "words_prose": prose,
        "fills": FILLS,
        "fill_count": {k: md.count(f"<{k}>") for k in FILLS},
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
