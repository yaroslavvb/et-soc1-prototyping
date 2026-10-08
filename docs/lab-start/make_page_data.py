#!/usr/bin/env python3
"""Write the "New user? Start here" page's data from START.md, the brief the Claude on a lab machine reads.

    python3 docs/lab-start/make_page_data.py           # writes docs/reports/data/2026-09-30-lab-start/brief.json
    python3 docs/lab-start/make_page_data.py --check   # exit 1 if brief.json is stale

Since the ninth edition (2 October 2026) the page gives a person three steps: from their own computer, create their
account as root and start Claude on the lab machine as themselves (the commands are in the page's script), then give
that Claude one line, which has it read START.md (fetched from GitHub into ~/lab-start.md). Since the twelfth (8
October 2026) a step 0 comes first: a Tailscale invite from the lab lead, asked for by direct message, never in
#community-lab. The page shows START.md verbatim in a fold, unfilled. Since 8 October 2026 the page is the raw steps
only: no card tiles, so no card data either. No timestamps go into the output, so a rebuild with the same inputs is
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

FILLS = []  # the page fills nothing into the brief: Claude learns the username with id -un


def build():
    md = open(SRC, encoding="utf-8").read()
    # The data is inlined in a <script>; the build's json.dumps does not escape "<", so refuse what would end it.
    for bad in ("</script", "<!--"):
        if bad in md.lower():
            raise SystemExit(f"START.md contains {bad!r}, which would break the page's inline script")
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
