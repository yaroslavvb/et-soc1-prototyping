#!/usr/bin/env python3
"""Fill each page's "Checked on three cards" note with both counts of the claims the version-3 campaign tested there.

The hub's claims scoreboard (§1, `claims_status` in the hub's data, written by sync_hub_data.py from the campaign's
results/pagemap.json) and each page's own note count the same claims by two rules:

  the page's own reading   judges the number the page quotes: a claim "held" when what the page states held on the
                           three cards (the hub keeps these counts, by hand, as reports[].v3_note);
  the scoreboard's rule    V3_ORDER in sync_hub_data.py: a claim counts under "a test behind it failed" when any part
                           of any registered test covering it failed, even a part the page does not quote, else under
                           "fewer than three repeats" when a card lacked them, then "differs by card", then "proven on
                           the cards"; a tested claim the campaign only reported per card keeps its earlier verdict.

The two rules are written out once, in the hub's scoreboard caption (#claims-cap, in
limits-of-observability.body.html); each page's span is one sentence with both counts and a link to that caption.

Each page source carries an empty or stale <span class="v3-counts" data-v3-counts="SLUG">...</span> in its note; this
script writes both counts into it, from the hub's data file. Nothing else in the file changes.

    python3 tools/ettelem/v3_counts.py            # rewrite every span in the page sources (FILES below)
    python3 tools/ettelem/v3_counts.py --check    # exit 1 if a span is missing or stale
    python3 tools/ettelem/v3_counts.py --print SLUG

Run it after sync_hub_data.py and before the page builds (MIRROR.md, "How each page is built"): a source-built page
takes the span from its body, a standalone page carries it in its HTML. `sync_hub_data.py --check` runs this
script's --check too.
"""
import argparse
import html
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HUB = os.path.join(ROOT, "docs/reports/sources/limits-of-observability.data.json")
HUB_URL = "https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability"
# The page sources that carry a note (slug -> the file edited by hand; MIRROR.md's "How each page is built"). A page is
# listed once it carries the span; --check fails on a listed file without it.
FILES = {
    "et-soc1-limits-of-observability": "docs/reports/sources/limits-of-observability.body.html",
    "et-soc1-hot-line": "docs/reports/sources/hot-line.body.html",
    "et-soc1-on-chip-relay": "docs/reports/sources/on-chip-relay.body.html",
    "et-soc1-on-chip-communication": "docs/reports/2026-09-18-et-soc1-on-chip-communication.html",
    "2026-09-22-et-soc1-l2-mainline-starvation": "docs/reports/2026-09-22-et-soc1-l2-mainline-starvation.html",
    "et-soc1-memory-anatomy": "workloads/memprobe/report_template.html",
    "et-soc1-memory-hierarchy": "docs/reports/2026-09-18-et-soc1-memory-hierarchy.html",
    "et-soc1-ridge-points": "docs/reports/2026-09-18-et-soc1-ridge-points.html",
    "et-soc1-matmul-efficiency": "docs/reports/2026-09-18-et-soc1-matmul-efficiency.html",
    "et-soc1-sparse-compute": "docs/reports/2026-09-18-et-soc1-sparsity.html",
    "et-soc1-testdrive": "docs/report/index.html",
    "et-soc1-spatial-temperature-brief": "docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html",
    "et-soc1-energy-manual": "docs/reports/sources/energy-manual.body.html",
    "et-soc1-heat-per-mm": "docs/reports/sources/heat-per-mm.body.html",
    "et-soc1-dvfs-leakage": "docs/reports/sources/dvfs-leakage.body.html",
    "et-soc1-power-temperature": "docs/reports/sources/power-temperature.body.html",
    "et-soc1-horace-experiment": "docs/reports/sources/horace-experiment.body.html",
    "et-soc1-why-low-power": "docs/reports/sources/why-low-power.body.html",
}
SPAN = re.compile(r'(<span class="v3-counts" data-v3-counts="(?P<slug>[^"]+)">)(?P<body>[^<]*(?:<(?!/span>)[^<]*)*)(</span>)', re.S)


def slug_of(url):
    return url.split("#")[0].rstrip("/").split("/")[-1]


def listing(parts):
    parts = list(parts)
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def counts(hub):
    """{slug: (n, [(count, page words)], [(count, scoreboard label)])} for every page the campaign tested."""
    series = next(s for s in hub["claims_status"]["series"] if s.get("tested"))
    label = {v[0]: v[1] for v in hub["claims_status"]["verdicts"]}
    out = {}
    for r in hub["reports"]:
        slug = slug_of(r["url"])
        tested = series["pages"].get(slug, {}).get("tested")
        if not tested:
            continue
        note = r.get("v3_note") or []
        n = sum(tested.values())
        if sum(k for k, _ in note) != n:
            sys.exit(f"{os.path.relpath(HUB, ROOT)}: reports[{slug}].v3_note counts {sum(k for k, _ in note)} claims; "
                     f"the scoreboard counts {n} tested there")
        out[slug] = (n, [(k, w) for k, w in note], [(v, label.get(c, c.lower())) for c, v in tested.items()])
    return out


def text(slug, c, self_page):
    """One sentence: the page's own count, then the scoreboard's (the rules are in the hub's #claims-cap)."""
    n, note, board = c
    page_part = listing(f"{k:,} {html.escape(w)}" for k, w in note)
    board_part = listing(f"{k:,} “{html.escape(w)}”" for k, w in board)
    where = ('<a href="#claims-cap">§1’s scoreboard</a>' if self_page else
             f'the <a href="{HUB_URL}#claims-cap">hub’s scoreboard</a>')
    if [k for k, _ in note] == [k for k, _ in board]:
        return f"Of {n:,} claims tested here: {page_part}, as {where} counts them."
    return f"Of {n:,} claims tested here, this page counts {page_part}; {where}, {board_part}."


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if any span is missing or stale")
    ap.add_argument("--print", metavar="SLUG", help="print one page's text and exit")
    ap.add_argument("--hub", default=HUB)
    a = ap.parse_args()
    with open(a.hub) as fh:
        hub = json.load(fh)
    cs = counts(hub)
    if a.print:
        print(text(a.print, cs[a.print], a.print == "et-soc1-limits-of-observability"))
        return
    bad, changed = [], []
    for slug, rel in FILES.items():
        p = os.path.join(ROOT, rel)
        with open(p, encoding="utf-8") as fh:
            src = fh.read()
        found = [m for m in SPAN.finditer(src)]
        if not found:
            bad.append(f"{rel}: no v3-counts span")
            continue
        new = src
        for m in found:
            if m["slug"] not in cs:
                bad.append(f"{rel}: v3-counts span for {m['slug']}, which the campaign did not test")
                continue
            if m["slug"] != slug:
                bad.append(f"{rel}: v3-counts span for {m['slug']}; this file is {slug}'s")
            want = text(m["slug"], cs[m["slug"]], m["slug"] == "et-soc1-limits-of-observability")
            if m["body"] != want:
                new = new.replace(m.group(0), m.group(1) + want + m.group(4), 1)
        if new != src:
            if a.check:
                bad.append(f"{rel}: stale v3-counts span")
            else:
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(new)
                changed.append(rel)
    missing = sorted(set(cs) - set(FILES))
    if missing:
        bad.append("tested pages with no file here: " + ", ".join(missing))
    for b in bad:
        print(b, file=sys.stderr)
    if a.check:
        if bad:
            sys.exit(1)
        print(f"v3-counts: {len(FILES)} page sources up to date")
        return
    print(f"v3-counts: rewrote {len(changed)} of {len(FILES)} page sources" + (": " + ", ".join(changed) if changed else ""))
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
