#!/usr/bin/env python3
"""E194's collection at the desk (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): step 11's
desk half, after the copy-back. E191's collector (tools/claims-v3/e191/collect_e191.py, eb1ac923, unchanged beside it) with E194's names
and one gate added for a desk that IS the box (E183's kit note 5's lesson, ported: on aifoundry2 every path the session writes carries the
desk's own home as its prefix, so the scrub alone would hide a desk path under "~"):

    /usr/bin/python3 -B tools/claims-v3/e194/collect_e194.py COPY DATA --box-home PATH --box-login LOGINFILE
        COPY      the session's directory as rsync copied it from the box (RB_OUT/e194-raw/T<T0>/)
        DATA      docs/reports/data/<day>-e194-blind-day-aifoundry2 (new; refused if it exists)
        LOGINFILE RB_OUT/box-login-aifoundry2.txt (the look writes it: our own login on the box, one line)

  1. COPY-BACK EXACT: every file of the box's MANIFEST.sha256 is in COPY at its sha256, and COPY holds nothing else but MANIFEST.sha256
     itself and runner.rc (the one file the wrapper writes after it); else exit 3, nothing written;
  2. THE BOX-TREE GATE (new, before anything is written; KIT.md section 4): in every text and .gz file of COPY, each place the box's home
     is written must begin a path inside the box tree (<home>/claude/et-soc1-prototyping/, read lexically: a path through ".", ".." or "//"
     that leaves the tree stops it), or be the home itself; and no file may hold a session scratch root (/tmp/claude-); else exit 3, nothing
     written ("a desk path in the session's files"): the lab clone, the round's own state, a scratch file or any other folder of this
     account's home is a desk path on this box, never part of the data;
  3. DATA in E194.md section 8.1's form: passes/<config>/p<k>/ (telemetry.jsonl.gz, host.json, host-raw.json for the ledger programs,
     host-stdout.txt (the host's raw stdout, kept beside the object read from it), host.err, host.rec for sparse parity, run.json,
     pass.json) and session/ (session.log, the two config reads and their stderr, the identity record, et-who's counts, stop-path.json, the
     smoke, the anchors, queue.json, commands.jsonl, the session's whole telemetry, runner.out, runner.rc, MANIFEST.sha256);
  4. each pass reduced by workloads/sparseparity/tools/energy_reduce.py, UNCHANGED (run as its own process with numpy), into its
     energy.json; its "dir" field is then set to the pass's path in the repository;
  5. THE SCRUB: the box's home path becomes "~" and our own box login "<login>" (as a whole word) in every text and .gz file, and no file
     may then hold the home, any other /home/ path, or the login (the desk-path gate, nopath_q142s.py, runs after this, from step 11);
  6. DATA/SHA256SUMS (paths beside it, as the lab's data lists), and DATA/FILES.txt: every file under DATA by its path.
The scorer is NOT run here: s24_score_e194.sh runs score_e194.py on the committed DATA, after the data commit. Exit 0 collected, 3 a
gate, 2 usage. RB_DESKTEST=1 with --data-outside lets the runner's desk test write DATA in its scratch (never on the card day).
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
REDUCER = os.path.join(REPO, "workloads/sparseparity/tools/energy_reduce.py")
TEXT = (".json", ".txt", ".log", ".err", ".out", ".rc", ".rec", ".sha256", ".jsonl")
TREE = "claude/et-soc1-prototyping"          # e194_common.TREE (k6's rb_tree for aifoundry2; the quick set checks they agree)
SCRATCH = b"/tmp/claude-"                    # a session scratch root: never in the data
PATH_END = b" \t\r\n\"'`<>()[]{},;:=|$"      # what ends a path written in text


def file_bytes(p):
    raw = open(p, "rb").read()
    return gzip.decompress(raw) if p.endswith(".gz") else raw


def box_tree_gate(copy, box_home):
    """THE BOX-TREE GATE (the module docstring, item 2): ([hits], files read). A hit names the file and the path written there."""
    home = box_home.encode()
    tree = os.path.normpath(box_home + "/" + TREE)
    hits, nread = [], 0
    for dp, dn, fn in os.walk(copy):
        for n in sorted(fn):
            p = os.path.join(dp, n)
            if not (n.endswith(TEXT) or n.endswith(".gz") or n in ("runner.rc",)):
                continue
            try:
                body = file_bytes(p)
            except (OSError, EOFError, gzip.BadGzipFile):
                hits.append(f"{os.path.relpath(p, copy)}: unreadable")
                continue
            nread += 1
            rel = os.path.relpath(p, copy)
            if SCRATCH in body:
                hits.append(f"{rel}: a session scratch root ({SCRATCH.decode()}...)")
            k = body.find(home)
            while k >= 0:
                j = k
                while j < len(body) and body[j:j + 1] not in PATH_END:
                    j += 1
                tok = body[k:j].decode("utf-8", "replace")
                after = body[k + len(home):k + len(home) + 1]
                if after in (b"",) or after in PATH_END:
                    pass                                             # the home itself, not a path under it
                else:
                    norm = os.path.normpath(tok)
                    if not (norm == tree or norm.startswith(tree + "/")) or "/./" in tok or "//" in tok[1:] or "/../" in tok:
                        hits.append(f"{rel}: {tok[:120]}")
                k = body.find(home, j if j > k else k + 1)
    return hits, nread


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def copy_back_exact(copy):
    man = os.path.join(copy, "MANIFEST.sha256")
    if not os.path.exists(man):
        return ["no MANIFEST.sha256"]
    want = {}
    for ln in open(man):
        if ln.strip():
            h, p = ln.rstrip("\n").split("  ", 1)
            want[p] = h
    have = set()
    for dp, dn, fn in os.walk(copy):
        for n in fn:
            have.add(os.path.relpath(os.path.join(dp, n), copy))
    bad = [f"missing {p}" for p in want if p not in have] + [f"differs {p}" for p in want if p in have and sha(os.path.join(copy, p)) != h_of(want, p)]
    extra = sorted(have - set(want) - {"MANIFEST.sha256", "runner.rc"})
    bad += [f"not in the manifest: {p}" for p in extra]
    return bad


def h_of(want, p):
    return want[p]


def login_re(login):
    return re.compile(rb"(?<![A-Za-z0-9_.-])" + re.escape(login.encode()) + rb"(?![A-Za-z0-9_-])")


def scrub_bytes(data, box_home, login):
    new = data.replace(box_home.encode(), b"~")
    if login:
        new = login_re(login).sub(b"<login>", new)
    return new


def scrub_file(p, box_home, login):
    raw = open(p, "rb").read()
    if p.endswith(".gz"):
        data = gzip.decompress(raw)
        new = scrub_bytes(data, box_home, login)
        if new != data:
            with gzip.open(p, "wb") as f:
                f.write(new)
        return new
    if p.endswith(TEXT) or os.path.basename(p) in ("runner.rc",):
        new = scrub_bytes(raw, box_home, login)
        if new != raw:
            open(p, "wb").write(new)
        return new
    return raw


def main(argv):
    if len(argv) < 6 or argv[2] != "--box-home" or argv[4] != "--box-login":
        print(__doc__)
        return 2
    copy, data, box_home = os.path.abspath(argv[0]), argv[1], argv[3].rstrip("/")
    if not box_home.startswith("/") or len(box_home) < 6:
        print(f"COLLECT-REFUSED: the box's home path {box_home!r} is not an absolute path")
        return 2
    try:
        login = open(argv[5]).read().split()[0]
    except (OSError, IndexError):
        login = ""
    if not re.match(r"^[a-z_][a-z0-9_-]{1,31}$", login or ""):
        print("COLLECT-REFUSED: the box login file gives no login (the look writes RB_OUT/box-login-aifoundry2.txt)")
        return 2
    dabs = os.path.join(REPO, data) if not os.path.isabs(data) else data
    rel = os.path.relpath(dabs, REPO)
    base = REPO
    if os.environ.get("RB_DESKTEST") == "1" and "--data-outside" in argv:   # the runner's desk test only: a data folder in its scratch
        rel, base = os.path.basename(dabs), os.path.dirname(dabs)
    if not (rel.startswith("docs/reports/data/") or base != REPO) or "e194" not in rel:
        print(f"COLLECT-REFUSED: {rel} is not an E194 data directory under docs/reports/data/")
        return 2
    if os.path.exists(dabs):
        print(f"COLLECT-REFUSED: {rel} exists already (never merge into an earlier copy)")
        return 3
    bad = copy_back_exact(copy)
    if bad:
        print("COPY-BACK NOT EXACT: " + "; ".join(bad[:10]))
        return 3
    print("COPY-BACK EXACT: every file of the box's MANIFEST.sha256 at its sha256, nothing else but runner.rc")
    hits, nread = box_tree_gate(copy, box_home)
    if hits:
        print(f"BOX-TREE GATE: a desk path in the session's files ({len(hits)}): " + "; ".join(hits[:10]) + ": nothing written")
        return 3
    print(f"BOX-TREE GATE: every path under the box's home in the {nread} text files read lies in its tree ~/{TREE}/; no scratch root")
    os.makedirs(os.path.join(dabs, "session"))
    if os.path.isdir(os.path.join(copy, "passes")):
        shutil.copytree(os.path.join(copy, "passes"), os.path.join(dabs, "passes"))
    for n in sorted(os.listdir(copy)):
        if n == "passes":
            continue
        s = os.path.join(copy, n)
        (shutil.copytree if os.path.isdir(s) else shutil.copy2)(s, os.path.join(dabs, "session", n))
    npass, nbad = 0, []
    pdir = os.path.join(dabs, "passes")
    for cfg in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
        for k in sorted(os.listdir(os.path.join(pdir, cfg))):
            d = os.path.join(pdir, cfg, k)
            r = subprocess.run([sys.executable, "-B", REDUCER, d], capture_output=True, text=True, timeout=600)
            ej = os.path.join(d, "energy.json")
            if r.returncode not in (0, 1) or not os.path.exists(ej):
                nbad.append(f"{cfg}/{k}: the reducer rc {r.returncode}")
                continue
            with open(os.path.join(d, "energy.txt"), "w") as f:
                f.write(r.stdout)
            en = json.load(open(ej))
            en["dir"] = os.path.relpath(d, base)
            with open(ej, "w") as f:
                json.dump(en, f, indent=1)
            npass += 1
            print(f"reduced {cfg}/{k}: ok {en.get('ok')}, J over idle a launch {(en.get('board') or {}).get('j_per_solve')}, "
                  f"hard {en.get('hard')}")
    left = []
    for dp, dn, fn in os.walk(dabs):
        for n in fn:
            p = os.path.join(dp, n)
            body = scrub_file(p, box_home, login)
            if box_home.encode() in body or b"/home/" in body or login_re(login).search(body):
                left.append(os.path.relpath(p, dabs))
    if left:
        print("SCRUB FAILED: a /home/ path or the box login is left in " + ", ".join(left[:10]))
        return 3
    rows = []
    for dp, dn, fn in os.walk(dabs):
        dn.sort()
        for n in sorted(fn):
            p = os.path.join(dp, n)
            r2 = os.path.relpath(p, dabs)
            if r2 != "SHA256SUMS":
                rows.append(f"{sha(p)}  {r2}")
    with open(os.path.join(dabs, "SHA256SUMS"), "w") as f:
        f.write("\n".join(sorted(rows, key=lambda x: x[66:])) + "\n")
    with open(os.path.join(dabs, "FILES.txt"), "w") as f:      # every file by its path (README.md and FILES.txt themselves aside)
        f.write("\n".join(sorted(r[66:] for r in rows)) + "\n")
    if nbad:
        print("REDUCER FAILED: " + "; ".join(nbad))
        return 3
    print(f"COLLECTED {rel}: {npass} passes reduced; {len(rows)} files in SHA256SUMS (and FILES.txt); the scrub clean (no /home/ path, "
          f"no box login)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
