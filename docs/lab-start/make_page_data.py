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
byte-identical.

Both modes also check that the page's Machine field (select#f-host in docs/reports/sources/lab-start.body.html) offers
exactly the machines START.md's "Then, by machine:" list sends a person's Claude to a card on: every machine with a
bullet there, less any whose bullet says its card is "out of service". Since 14 October 2026 (Q113): the field was
added on 2 October while aifoundry2's card was out of service, and the back-in-service updates of 6 and 9 October
changed the brief but not the field, so new users could not pick aifoundry2 until the owner noticed on 14 October."""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(HERE, "START.md")
OUT = os.path.join(ROOT, "docs", "reports", "data", "2026-09-30-lab-start", "brief.json")
BODY = os.path.join(ROOT, "docs", "reports", "sources", "lab-start.body.html")

FILLS = []  # the page fills nothing into the brief: Claude learns the username with id -un


def brief_machines(md):
    """The machines START.md's "Then, by machine:" list has a card for, in its order (a bullet that says its card is
    out of service has none)."""
    at = md.find("\nThen, by machine:\n")
    if at < 0:
        raise SystemExit("START.md has no 'Then, by machine:' list, so the page's Machine field cannot be checked")
    bullets = md[at:].split("\n\n", 2)[1]
    hosts = []
    for item in re.split(r"\n(?=- )", bullets):
        m = re.match(r"- \*\*([a-z0-9-]+)\*\*:\s*(.*)", item, flags=re.S)
        if m and "out of service" not in " ".join(m.group(2).split()):
            hosts.append(m.group(1))
    if not hosts:
        raise SystemExit("START.md's 'Then, by machine:' list names no machine with a card")
    return hosts


def page_machines():
    """The machines the page's Machine field offers, in its order."""
    body = open(BODY, encoding="utf-8").read()
    m = re.search(r'<select id="f-host">(.*?)</select>', body, flags=re.S)
    if not m:
        raise SystemExit(f"{os.path.relpath(BODY, ROOT)} has no <select id=\"f-host\">")
    return re.findall(r'<option value="([^"]+)"', m.group(1))


def check_machines(md):
    """Exit 1 when the page's Machine field and the brief disagree on which machines have a card for a new user."""
    want, have = brief_machines(md), page_machines()
    if set(want) != set(have):
        add = [h for h in want if h not in have]
        drop = [h for h in have if h not in want]
        print(f"the page's Machine field ({os.path.relpath(BODY, ROOT)}, select#f-host) offers {', '.join(have)}, but "
              f"START.md's 'Then, by machine:' list has a card on {', '.join(want)}"
              + (f"; add {', '.join(add)}" if add else "") + (f"; remove {', '.join(drop)}" if drop else "")
              + ". A card went in or out of service: update both (docs/lab-start/README.md, Keeping it current).")
        sys.exit(1)


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
    check_machines(data["md"])
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
