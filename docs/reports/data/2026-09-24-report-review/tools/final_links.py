#!/usr/bin/env python3
"""Render all 18 finished pages and check every link: spacesheep slugs are public pages of the set, #anchors exist on
the target page, GitHub repo paths exist in the working tree, in-page anchors resolve, nothing links the private brief."""
import json, os, re, subprocess, sys, urllib.parse
A = os.environ.get("AUDIT_DIR", "/tmp/report-review")
R = "/home/yaroslavvb/claude/et-soc1-prototyping"
os.chdir(R)
pages = {}
for line in open(A + "/manifest.tsv").read().splitlines()[1:]:
    slug, uuid, html = line.split("\t")[:3]
    if slug == "david-kanter-power-brief": continue
    if slug == "et-soc1-spatial-temperature-brief": html = "docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html"
    if slug == "2026-09-22-et-soc1-l2-mainline-starvation": html = "docs/reports/2026-09-22-et-soc1-l2-mainline-starvation.html"
    pages[slug] = html
os.makedirs(A + "/final", exist_ok=True)
data = {}
for slug, html in pages.items():
    subprocess.run([A + "/render_text.sh", html, f"{A}/final/{slug}"], check=True)
    data[slug] = json.load(open(f"{A}/final/{slug}.json"))
bad = []
for slug, d in data.items():
    ids = set(d["ids"])
    for l in d["links"]:
        h = l["href"]
        if h.startswith("#"):
            if h[1:] and h[1:] not in ids: bad.append((slug, "missing in-page anchor", h))
        elif "spacesheep.dev/@yaroslavvb/" in h:
            u = urllib.parse.urlparse(h); t = u.path.rstrip("/").split("/")[-1]
            if t == "david-kanter-power-brief": bad.append((slug, "links the private Kanter brief", h))
            elif t not in pages: bad.append((slug, "unknown or non-set space", h))
            elif u.fragment and u.fragment not in set(data[t]["ids"]): bad.append((slug, "anchor missing on target", h))
        elif "github.com/yaroslavvb/et-soc1-prototyping" in h:
            m = re.search(r"et-soc1-prototyping/(?:tree|blob)/main/(.*)", h)
            if m:
                p = urllib.parse.unquote(m.group(1)).split("#")[0].rstrip("/")
                if p and not os.path.exists(p): bad.append((slug, "repo path missing", p))
        elif not h.startswith(("http", "mailto:")) and not h.endswith(".gif"):
            bad.append((slug, "relative link", h))
    t = d["title"]
    rel = any("related" in x["text"].lower() for x in d["headings"])
    hub = any("et-soc1-limits-of-observability" in l["href"] for l in d["links"])
    print(f"{slug:44s} links={len(d['links']):3d} related={rel} hub={hub} title={t}")
print("\nPROBLEMS:", len(bad))
for b in bad: print("  ", b)
