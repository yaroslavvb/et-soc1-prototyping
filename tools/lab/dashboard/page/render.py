#!/usr/bin/env python3
"""Build the lab dashboard page: one self-contained index.html with the data baked in (DESIGN.md §4.1).

    python3 tools/lab/dashboard/page/render.py <data.json> <out.html> [--fixture] [--now-ms MS]

It does what scripts/build-report.py does, without the math step: the shared report template and chart toolkit
(docs/reports/sources/report.template.html and chartkit.js, unchanged) around this directory's body.html, script.js
and meta.json. The output has no external script, style, font or image, and the page never fetches anything.

- The data goes into the page as a JSON literal in which every <, > and & is written as a \\u escape, so no string in
  the data can close the script element or open a comment. Placeholders are substituted in one pass, so a
  placeholder's name inside the data or the page code is never expanded.
- A last privacy check refuses (exit 3) data with an e-mail address, an IPv4 address, a URL, a *.ts.net name or a
  Tailscale login address anywhere in it, printing the JSON path of the match, never its text. The collector's check
  (DESIGN.md §6) is the real one; this one catches a data file from anywhere else.
- --fixture moves every time in the data (keys ending in _ms or _at, ISO strings) by one offset, so that
  generated_at is 4 minutes before now (or before --now-ms): a made-up fixture renders as fresh data. The clock times
  written into its text (the headline, alert titles and details, card reasons: "DOWN since 12:47") move with them, in
  the lab's zone, so the text agrees with the panels.
- The page gets a build stamp (D._build: the render time and a hash of the page sources), shown in "About this page".

Exit 0 when the page was written, 2 on a usage or input error, 3 on a privacy refusal."""
import hashlib
import html
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
SOURCES = os.path.join(REPO, "docs", "reports", "sources")

PRIVACY = [  # (name, pattern) for the last check; names only are printed
    # an address, but not a systemd template unit such as apport-coredump-hook@3-2211-1000.service
    ("e-mail", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.(?!(service|socket|timer|mount|scope|slice|"
                          r"target|path|device|swap|automount)\b)[A-Za-z]{2,}\b")),
    ("ipv4", re.compile(r"(?<![\w.])(25[0-5]|2[0-4]\d|1?\d?\d)(\.(25[0-5]|2[0-4]\d|1?\d?\d)){3}(?![\w.])")),
    ("url", re.compile(r"\b(https?|ssh|ftp)://", re.I)),
    ("tailnet name", re.compile(r"\.ts\.net\b", re.I)),
    ("tailscale login", re.compile(r"login\.tailscale\.com", re.I)),
]
ISO = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d(:\d\d(\.\d+)?)?(Z|[+-]\d\d:?\d\d)$")


def usage(msg):
    print("render.py: " + msg, file=sys.stderr)
    print(__doc__.split("\n\n")[1], file=sys.stderr)
    sys.exit(2)


def walk(v, path="$"):
    """yield (path, key, value) for every string, key and number in v"""
    if isinstance(v, dict):
        for k, x in v.items():
            yield path, k, None
            yield from walk(x, f"{path}.{k}")
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from walk(x, f"{path}[{i}]")
    else:
        yield path, None, v


def privacy_check(data):
    bad = []
    for path, key, val in walk(data):
        for s in (key, val):
            if isinstance(s, str):
                for name, pat in PRIVACY:
                    if pat.search(s):
                        bad.append(f"{path}: {name}")
    return bad


def shift_times(v, delta_ms, key=None):
    """a copy of v with every time moved by delta_ms (numbers under *_ms keys, ISO strings)"""
    if isinstance(v, dict):
        return {k: shift_times(x, delta_ms, k) for k, x in v.items()}
    if isinstance(v, list):
        return [shift_times(x, delta_ms, key) for x in v]
    if isinstance(v, (int, float)) and not isinstance(v, bool) and key and key.endswith("_ms") and v > 1e11:
        return int(v + delta_ms)
    if isinstance(v, str) and ISO.match(v):
        d = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return (d + timedelta(milliseconds=delta_ms)).isoformat(timespec="seconds")
    return v


CLOCK = re.compile(r"(?<![\d:])([01]\d|2[0-3]):([0-5]\d)(?![\d:])")


def shift_clock_text(data, delta_ms):
    """--fixture: the HH:MM times in the fixture's text fields, moved by delta_ms in the lab's zone (a time later than
    generated_at is taken as the day before). Changes data in place; call it before shift_times."""
    tzname = (data.get("usage") or {}).get("tz") or (data.get("collector") or {}).get("lab_tz")
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(tzname)
    except Exception:  # no zone name or no tz database: the renderer's own zone
        tz = datetime.now().astimezone().tzinfo
    gen = datetime.fromtimestamp(data["generated_ms"] / 1000, tz)

    def one(m):
        t = gen.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0, microsecond=0)
        if t > gen + timedelta(minutes=1):
            t -= timedelta(days=1)
        return (t + timedelta(milliseconds=delta_ms)).astimezone(tz).strftime("%H:%M")

    def fix(s):
        return CLOCK.sub(one, s) if isinstance(s, str) else s
    st = data.get("status") or {}
    if "headline" in st:
        st["headline"] = fix(st["headline"])
    for a in data.get("alerts") or []:
        if isinstance(a, dict):
            a["title"], a["detail"] = fix(a.get("title")), fix(a.get("detail"))
    for c in (data.get("cards") or {}).values():
        if isinstance(c, dict) and isinstance(c.get("reasons"), list):
            c["reasons"] = [fix(r) for r in c["reasons"]]


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    now_ms = None
    if "--now-ms" in flags:
        i = argv.index("--now-ms")
        try:
            now_ms = int(argv[i + 1])
        except (IndexError, ValueError):
            usage("--now-ms needs a number")
        args.remove(argv[i + 1])
        flags.remove("--now-ms")
    fixture = "--fixture" in flags
    unknown = [f for f in flags if f != "--fixture"]
    if unknown or len(args) != 2:
        usage("unknown option " + unknown[0] if unknown else "expected <data.json> <out.html>")
    src, out = args
    try:
        data = json.load(open(src, encoding="utf-8"))
    except (OSError, ValueError) as e:
        usage(f"cannot read {src}: {e}")
    if not isinstance(data, dict) or data.get("schema") != 1:
        usage(f"{src}: not a lab-dashboard data file (schema 1)")

    bad = privacy_check(data)
    if bad:
        print(f"render.py: refused: {len(bad)} string(s) look like personal or access data:", file=sys.stderr)
        for b in bad[:20]:
            print("  " + b, file=sys.stderr)
        sys.exit(3)

    now_ms = now_ms or int(time.time() * 1000)
    if fixture:
        gen = data.get("generated_ms")
        if not isinstance(gen, (int, float)):
            usage("--fixture needs generated_ms in the data")
        shift_clock_text(data, now_ms - 4 * 60 * 1000 - gen)
        data = shift_times(data, now_ms - 4 * 60 * 1000 - gen)

    parts = {}
    for name in ("body.html", "script.js", "meta.json"):
        parts[name] = open(os.path.join(HERE, name), encoding="utf-8").read()
    meta = json.loads(parts["meta.json"])
    src_hash = hashlib.sha256("\0".join(parts[n] for n in sorted(parts)).encode()).hexdigest()[:8]
    data["_build"] = {"at_ms": now_ms, "page": src_hash, "fixture": fixture}

    tpl = open(os.path.join(SOURCES, "report.template.html"), encoding="utf-8").read()
    tpl = tpl.replace("</script>\n</main>\n</body>", "</script>\n</body>")  # the body closes <main> itself
    js = (json.dumps(data, separators=(",", ":"), ensure_ascii=False)
          .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
          .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))
    subst = {
        "CHARTKIT": open(os.path.join(SOURCES, "chartkit.js"), encoding="utf-8").read(),
        "TITLE": html.escape(meta["title"]),
        "DESC": html.escape(meta["description"]),
        "BODY": parts["body.html"],
        "DATA": js,
        "SCRIPT": parts["script.js"],
    }
    seen = set()

    def put(m):
        seen.add(m.group(1))
        return subst[m.group(1)]

    page = re.sub(r"__(CHARTKIT|TITLE|DESC|BODY|DATA|SCRIPT)__", put, tpl)
    if seen != set(subst):
        usage("the template lacks " + ", ".join(sorted(set(subst) - seen)))
    tmp = out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(page)
    os.replace(tmp, out)
    print(f"wrote {out} {len(page.encode())} bytes (page {src_hash}{', fixture' if fixture else ''})")


if __name__ == "__main__":
    main(sys.argv[1:])
