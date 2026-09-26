#!/usr/bin/env python3
"""Check that every public spacesheep page listed in docs/reports/MIRROR.md equals its file in this repository.

    python3 scripts/check-mirror.py [--via auto|cli|https] [--only SLUG ...] [--mirror PATH] [--json] [-j N]

MIRROR.md lists every page of the set in tables between <!-- mirror:begin --> and <!-- mirror:end -->: the page with
its address, the space uuid, the intended visibility, the repo file (or "not mirrored") and how it is deployed (a
folder deploy names its extra files in backticks).

For each PUBLIC row with a repo file, the live index.html is fetched and compared with the repo file after removing
the ` data-ss-id="..."` attributes the host adds to elements (and adding a final newline if one is missing), as the
review's deploy_all.sh did:
  --via cli    `spacesheep read <uuid> index.html -o <tmp>`: the stored file. Needs a key (`spacesheep login`, or
               SPACESHEEP_KEY). The command is `spacesheep` on PATH, or SPACESHEEP_CLI (e.g. "node /path/spacesheep.js").
  --via https  an anonymous GET of https://<uuid>.spacesheep.app/, the raw page. The host also inserts its viewer
               scripts just before </body>; they are removed after checking that the insertion holds only <style>
               and <script> blocks and the host's own `ss-` elements (its print mark), and that everything before
               and after it equals the repo file.
  --via auto   (default) cli when a key is configured and the CLI is found, else https. A page the CLI cannot read
               falls back to https.
Over HTTPS the host's insertion is identical on every page, so a page whose insertion differs from the others' is
flagged: that is how an extra <style> or <script> block at the very end of a live body shows up in this mode.
The raw address refuses Python's default user agent (403), so requests carry their own.
Extra files of a folder deploy (the Horace GIFs) are always fetched over HTTPS and compared byte for byte: the CLI's
`read` returns binary files mangled. Every public row's viewer address (https://spacesheep.dev/@owner/slug) must
answer 200 anonymously. Every private row with a uuid must not be served anonymously: the raw address may only return
the host's sign-in bootstrap (no <title>), and the viewer address must redirect.

With a key, `spacesheep list --json` is also read: each row's live visibility and slug must match MIRROR.md, and any
public space whose slug starts with one of --prefix (default et-soc1, etsoc1, aifoundry, 2026-09-22-et-soc1) that
MIRROR.md does not list as public is reported as a warning.

Read-only: it never deploys, shares or edits anything, and it never prints the key.
Exit status: 0 all equal and as listed; 1 any difference (content, visibility, slug, a private page served); 2 some
page unreachable and nothing else wrong."""
import argparse
import collections
import concurrent.futures as cf
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
URL_RE = re.compile(r"https://spacesheep\.dev/@([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")
TICKS = re.compile(r"`([^`]+)`")
SSID = re.compile(rb' data-ss-id="[^"]*"')
# What the host inserts before </body> on the raw address: its print stylesheet, its print mark (a div of class
# ss-print-mark holding an inline SVG) and its viewer scripts. Anything else inserted there counts as a difference.
INJECTED = re.compile(rb"\s*(?:<style\b[^>]*>.*?</style>|<script\b[^>]*>.*?</script>"
                      rb"|<div\b[^>]*\bclass=\"ss-[^\"]*\"[^>]*>(?:(?!<div\b).)*?</div>)\s*", re.S)
UA = "et-soc1-prototyping/check-mirror (read-only)"


def rel(path):
    path = os.path.abspath(path)
    return os.path.relpath(path, ROOT) if path.startswith(ROOT + os.sep) else path


# ---------------------------------------------------------------- MIRROR.md
def parse_mirror(path):
    text = open(path, encoding="utf-8").read()
    m = re.search(r"<!-- mirror:begin -->(.*?)<!-- mirror:end -->", text, re.S)
    if not m:
        sys.exit(f"{path}: no <!-- mirror:begin --> ... <!-- mirror:end --> block")
    rows, header = [], None
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            header = None                      # a heading or a blank line ends a table; the next one has its own header
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        rec = dict(zip(header, cells))
        page = rec.get("page", "")
        um = URL_RE.search(page)
        title = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", page)
        sm = UUID_RE.search(rec.get("space", ""))
        vis = (rec.get("visibility", "").split() or [""])[0].lower()
        rf = rec.get("repo file", "")
        rfm = TICKS.search(rf)
        repo = None if ("not mirrored" in rf.lower() or not rfm) else rfm.group(1)
        assets = [a for a in TICKS.findall(rec.get("deploy", "")) if not a.endswith((".html", "/"))]
        rows.append({"title": title, "owner": um.group(1) if um else None, "slug": um.group(2) if um else None,
                     "url": um.group(0) if um else None, "uuid": sm.group(0) if sm else None,
                     "visibility": vis, "repo": repo, "assets": assets})
    return rows


# ---------------------------------------------------------------- fetching
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def http_get(url, timeout, follow=True):
    """(status, body bytes); status None and the reason in body on a network error."""
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(_NoRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:  # DNS, TLS, timeout
        return None, str(e).encode()


def cli_command():
    env = os.environ.get("SPACESHEEP_CLI")
    if env:
        return shlex.split(env)
    exe = shutil.which("spacesheep")
    return [exe] if exe else None


def key_configured():
    if os.environ.get("SPACESHEEP_KEY"):
        return True
    cfg = os.path.join(os.path.expanduser("~"), ".config", "spacesheep", "config.json")
    return os.path.isfile(cfg) and os.path.getsize(cfg) > 2


def cli_read(cli, uuid, path, timeout):
    with tempfile.TemporaryDirectory(prefix="check-mirror-") as d:
        p = subprocess.run(cli + ["read", uuid, path, "-o", d], capture_output=True, timeout=timeout)
        f = os.path.join(d, path)
        if p.returncode != 0 or not os.path.isfile(f):
            err = (p.stderr or p.stdout).decode(errors="replace").strip().splitlines()
            raise RuntimeError(f"spacesheep read failed (rc {p.returncode}): {err[-1] if err else 'no output'}")
        return open(f, "rb").read()


def cli_list(cli, timeout):
    p = subprocess.run(cli + ["list", "--json"], capture_output=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError("spacesheep list failed")
    return json.loads(p.stdout)


# ---------------------------------------------------------------- comparing
def norm(b):
    b = SSID.sub(b"", b)
    return b if b.endswith(b"\n") else b + b"\n"


def first_diff_line(a, b):
    n = min(len(a), len(b))
    i = next((k for k in range(n) if a[k] != b[k]), n)
    return a[:i].count(b"\n") + 1


def compare_exact(live, repo):
    live, repo = norm(live), norm(repo)
    if live == repo:
        return "equal", ""
    return "differs", f"first difference at line {first_diff_line(live, repo)} (live {len(live)} B, repo {len(repo)} B)"


def compare_served(live, repo):
    """The raw HTTPS page: the stored file with the host's blocks inserted just before the last </body>.
    Returns (status, detail, sha256 of the insertion or None)."""
    live, repo = norm(live), norm(repo)
    if live == repo:
        return "equal", "", None
    i = repo.rfind(b"</body>")
    j = live.rfind(b"</body>")
    if i < 0 or j < 0:
        return compare_exact(live, repo) + (None,)
    pre, post = repo[:i], repo[i:]
    if not live.startswith(pre) or live[j:] != post or j < len(pre):
        return ("differs", f"first difference at line {first_diff_line(live, repo)} (live {len(live)} B, repo {len(repo)} B)",
                None)
    extra = live[len(pre):j]
    if INJECTED.sub(b"", extra).strip():
        return ("differs", f"{len(extra)} B inserted before </body> that are not only the host's style, script and ss- "
                "blocks", None)
    return "equal", f"host insertion {len(extra)} B removed", hashlib.sha256(extra).hexdigest()


# ---------------------------------------------------------------- one page
def check_page(row, via, cli, timeout):
    res = {"slug": row["slug"] or row["title"], "repo": row["repo"], "visibility": row["visibility"],
           "status": None, "detail": "", "via": via, "problems": [], "unreachable": []}
    if row["visibility"] != "public":
        res["status"] = "private"
        if row["uuid"]:
            st, body = http_get(f"https://{row['uuid']}.spacesheep.app/", timeout)
            served = st == 200 and re.search(rb"<title>\s*[^<\s]", body) is not None
            if st is None:
                res["unreachable"].append(f"raw address: {body.decode(errors='replace')}")
            elif served:
                res["problems"].append("SERVED ANONYMOUSLY at its raw address")
        if row["url"]:
            st, _ = http_get(row["url"], timeout, follow=False)
            if st == 200:
                res["problems"].append("SERVED ANONYMOUSLY at its viewer address")
        if not row["uuid"] and not row["url"]:
            res["detail"] = "no address listed, not checked"
        elif not res["problems"] and not res["unreachable"]:
            res["detail"] = "not served anonymously"
        return res
    if row["url"]:
        st, _ = http_get(row["url"], timeout, follow=False)
        if st is None:
            res["unreachable"].append("viewer address unreachable")
        elif st != 200:
            res["problems"].append(f"viewer address {row['url']} answers {st} anonymously, not 200 (private or moved?)")
    if not row["repo"]:
        res["status"] = "not mirrored"
        return res
    repo_path = os.path.join(ROOT, row["repo"])
    if not os.path.isfile(repo_path):
        res["status"] = "differs"
        res["detail"] = f"repo file {row['repo']} is missing"
        res["problems"].append(res["detail"])
        return res
    repo = open(repo_path, "rb").read()
    live = None
    if via == "cli":
        try:
            live = cli_read(cli, row["uuid"], "index.html", timeout)
            res["status"], res["detail"] = compare_exact(live, repo)
        except Exception as e:  # fall back to the public page
            res["via"], res["detail"] = "https", f"(cli: {e}) "
            live = None
    if live is None:
        st, body = http_get(f"https://{row['uuid']}.spacesheep.app/", timeout)
        if st != 200:
            res["status"] = "unreachable"
            res["detail"] += f"raw address answered {st if st else body.decode(errors='replace')}"
            res["unreachable"].append(res["detail"])
            return res
        status, detail, res["insertion"] = compare_served(body, repo)
        res["status"], res["detail"] = status, res["detail"] + detail
    if res["status"] == "differs":
        res["problems"].append(res["detail"])
    for a in row["assets"]:
        st, body = http_get(f"https://{row['uuid']}.spacesheep.app/{a}", timeout)
        local = os.path.join(os.path.dirname(repo_path), a)
        if st != 200:
            res["unreachable"].append(f"{a}: {st if st else body.decode(errors='replace')}")
        elif not os.path.isfile(local):
            res["problems"].append(f"{a}: no repo file {rel(local)}")
        elif body != open(local, "rb").read():
            res["problems"].append(f"{a}: live differs from {rel(local)}")
    if row["assets"]:
        bad = [p for p in res["problems"] + res["unreachable"] if p.split(":")[0] in row["assets"]]
        res["detail"] += ("; " if res["detail"] else "") + (f"{len(row['assets'])} folder files equal" if not bad
                                                            else f"folder files: {len(bad)} not equal or unreachable")
    return res


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mirror", default=os.path.join(ROOT, "docs", "reports", "MIRROR.md"))
    ap.add_argument("--via", choices=["auto", "cli", "https"], default="auto")
    ap.add_argument("--only", nargs="+", metavar="SLUG", help="check only these slugs (or uuids)")
    ap.add_argument("--prefix", default="et-soc1,etsoc1,aifoundry,2026-09-22-et-soc1",
                    help="slug prefixes of this set, for the unlisted-public-space warning (comma-separated)")
    ap.add_argument("--timeout", type=int, default=180, help="seconds per request")
    ap.add_argument("-j", "--jobs", type=int, default=4)
    ap.add_argument("--json", action="store_true", help="print the results as JSON")
    args = ap.parse_args()

    rows = parse_mirror(args.mirror)
    if args.only:
        rows = [r for r in rows if r["slug"] in args.only or r["uuid"] in args.only]
        if not rows:
            sys.exit(f"--only matched no row of {args.mirror}")
    cli = cli_command()
    have_key = key_configured()
    via = args.via
    if via == "auto":
        via = "cli" if (cli and have_key) else "https"
    if via == "cli" and not cli:
        sys.exit("--via cli: no spacesheep CLI (put it on PATH or set SPACESHEEP_CLI)")

    with cf.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        results = list(ex.map(lambda r: check_page(r, via, cli, args.timeout), rows))

    # Over HTTPS the host's insertion is the same on every page (16,757 B on 2026-09-25). A page whose insertion differs
    # from the others' may carry an extra block of its own at the end of its body, which compare_served cannot tell
    # apart from the host's: flag it. (With one page, e.g. --only, there is nothing to compare against.)
    ins = collections.Counter(r["insertion"] for r in results if r.get("insertion"))
    if len(ins) > 1 and ins.most_common(1)[0][1] >= 2:
        common = ins.most_common(1)[0][0]
        for r in results:
            if r.get("insertion") and r["insertion"] != common:
                r["status"] = "differs"
                r["problems"].append("the host insertion differs from the other pages' (an extra block at the end of "
                                     "the body?): check with --via cli")

    # Visibility and slugs from the account's own listing (needs the key).
    listing_note, warnings = "", []
    if cli and have_key:
        try:
            spaces = {s["id"]: s for s in cli_list(cli, args.timeout)}
            listed_public = {r["uuid"] for r in rows if r["visibility"] == "public" and r["uuid"]}
            for r, res in zip(rows, results):
                s = spaces.get(r["uuid"]) if r["uuid"] else None
                if r["uuid"] and not s:
                    res["problems"].append("space not in `spacesheep list` (deleted, or another account?)")
                    continue
                if not s:
                    continue
                res["live_visibility"] = s.get("visibility")
                if s.get("visibility") != r["visibility"]:
                    res["problems"].append(f"VISIBILITY: listed {r['visibility']}, live {s.get('visibility')}")
                if r["slug"] and s.get("slug") != r["slug"]:
                    res["problems"].append(f"SLUG: listed {r['slug']}, live {s.get('slug')}")
            if not args.only:
                prefixes = tuple(p for p in args.prefix.split(",") if p)
                for s in spaces.values():
                    if (s.get("visibility") == "public" and (s.get("slug") or "").startswith(prefixes)
                            and s["id"] not in listed_public):
                        warnings.append(f"public space not listed as public in MIRROR.md: {s.get('slug')} ({s['id']})")
            listing_note = "visibility and slugs checked against `spacesheep list --json`"
        except Exception as e:
            listing_note = f"visibility not checked ({e})"
    else:
        listing_note = ("visibility checked by anonymous requests only (no spacesheep key); "
                        "`spacesheep list` was not read")

    n_diff = sum(1 for r in results if r["problems"])
    n_unr = sum(1 for r in results if r["unreachable"] and not r["problems"])
    code = 1 if n_diff else (2 if n_unr else 0)
    if args.json:
        print(json.dumps({"via": via, "listing": listing_note, "results": results, "warnings": warnings,
                          "exit": code}, indent=1))
        return code

    print(f"check-mirror: {len(rows)} rows from {rel(args.mirror)}; content via {via}; {listing_note}")
    w = max(len(r["slug"] or "") for r in results)
    for r in results:
        flag = "FAIL" if r["problems"] else ("WARN" if r["unreachable"] else "ok")
        line = f"  {flag:<4} {r['status']:<12} {r['slug']:<{w}}  "
        line += r["repo"] or ("(private)" if r["visibility"] != "public" else "(not mirrored)")
        extra = [r["detail"]] if r["detail"] else []
        extra += [p for p in r["problems"] if p != r["detail"]] + r["unreachable"]
        if extra:
            line += "  [" + "; ".join(e for e in extra if e) + "]"
        print(line)
    for wmsg in warnings:
        print(f"  WARN {'':<12} {wmsg}")
    eq = sum(1 for r in results if r["status"] == "equal" and not r["problems"] and not r["unreachable"])
    mirrored = sum(1 for r in results if r["repo"] and r["visibility"] == "public")
    print(f"summary: {eq} of {mirrored} mirrored public pages equal; {n_diff} rows with a difference; "
          f"{n_unr} unreachable; {len(warnings)} warnings; exit {code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
