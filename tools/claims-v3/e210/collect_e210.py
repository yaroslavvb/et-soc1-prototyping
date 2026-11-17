#!/usr/bin/env python3
"""E210's collection at the desk (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum; ported from kit-e207's E207 kit, its local commit 4bd6e38c): the desk half of steps 11 and 12, after the
copy-back, E206's collector (tools/claims-v3/e206/collect_e206.py, landed in 906699ea, which made E206 arm A's committed data directory) for
E210's one data directory, with E202's gate-stop record. Python's own modules only.

    /usr/bin/python3 -B tools/claims-v3/e210/collect_e210.py copy-check COPY
        COPY-BACK EXACT: every file of the box's MANIFEST.sha256 is in COPY at its sha256, and COPY holds nothing else but MANIFEST.sha256
        itself, runner.out and runner.rc (the wrapper's two files); else exit 3
    /usr/bin/python3 -B tools/claims-v3/e210/collect_e210.py data DAY A COPY BOXHOME LOGINFILE [--neverrun DIR] [--neverrun-late DIR]
        DAY the window's day (YYYY-MM-DD); the arm A (E210's one). THE DIRECTORY: docs/reports/data/<DAY>-e210-switch-test-aifoundry3/ when
        at least one run started (queue.json); else the session stopped before any run (a gate, a HUNG smoke or probe process, a crash) and its
        record goes to docs/reports/gate-stops/<DAY>-e210-switch-test-T<T0>-aifoundry3/ (E202's form), never under docs/reports/data/ (step 2
        reads every docs/reports/data/*e210* path as an E210 datum). Refused if it exists.
  1. the copy checked again (COPY-BACK EXACT), then copied whole into <dir>/session/;
  2. THE SCRUB: the box's home path (as the box reported it) becomes "~", and OUR OWN BOX LOGIN (as the look read it on that box, the one
     line of LOGINFILE) becomes "<login>", in every text and .gz file; then no file may hold a /home/ path or the login (exit 3);
  3. a data directory only: the reducer (reduce_e210.py, as committed) over the session: <dir>/data-e210.json (the frozen scorer's input)
     and <dir>/reduce-e210.txt;
  3n. with --neverrun DIR (step 6n's folder, RB_OUT/e210-neverrun-dir.txt names it) and --neverrun-late DIR (step 12n's, RB_OUT/
     e210-neverrun-late-dir.txt): each report's three files (neverrun-e210-card.txt and .json, named-by.json; their paths already written as
     labels) copied in as <dir>/neverrun-e210-card.* and <dir>/neverrun-e210-late.* (named-by-card.json, named-by-late.json), scrubbed like
     the rest; refused (exit 3) if a named folder is not whole;
  4. <dir>/SHA256SUMS (paths beside it, as the lab's data lists).
The scorer is NOT run here: rb/s24_score_e210.sh runs score_e210.py on the committed data, after the data commit. It prints the directory
on its last line ("COLLECTED <dir>" or "COLLECTED-GATE-STOP <dir>"). Exit 0 collected, 3 a gate, 2 usage. RB_DESKTEST=1 with --outside
<dir> lets the desk tests write the directory in their scratch (never on the card day). SPDX-License-Identifier: Apache-2.0
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
sys.path.insert(0, HERE)
import e210_common as C  # noqa: E402

TEXT = (".json", ".txt", ".log", ".err", ".out", ".rc", ".sha256", ".jsonl")
EXTRA_OK = {"MANIFEST.sha256", "runner.rc", "runner.out"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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
    bad = [f"missing {p}" for p in want if p not in have]
    bad += [f"differs {p}" for p in want if p in have and sha(os.path.join(copy, p)) != want[p]]
    bad += [f"not in the manifest: {p}" for p in sorted(have - set(want) - EXTRA_OK)]
    return bad


def scrub_file(p, box_home, login):
    raw = open(p, "rb").read()
    gz = p.endswith(".gz")
    data = gzip.decompress(raw) if gz else raw
    if not gz and not (p.endswith(TEXT) or os.path.basename(p) == "STOP" or os.path.basename(p).startswith("STOPTEST")):
        return data
    new = data.replace(box_home.encode(), b"~")
    if login:
        new = re.sub(rb"(?<![A-Za-z0-9_.-])" + re.escape(login.encode()) + rb"(?![A-Za-z0-9_-])", b"<login>", new)
    if new != data:
        if gz:
            with gzip.open(p, "wb") as f:
                f.write(new)
        else:
            open(p, "wb").write(new)
    return new


def left_over(body, home, login):
    return home.encode() in body or b"/home/" in body or \
        re.search(rb"(?<![A-Za-z0-9_.-])" + re.escape(login.encode()) + rb"(?![A-Za-z0-9_-])", body) is not None


def main(argv):
    if len(argv) >= 2 and argv[0] == "copy-check":
        bad = copy_back_exact(os.path.abspath(argv[1]))
        if bad:
            print("COPY-BACK NOT EXACT: " + "; ".join(bad[:10]))
            return 3
        print("COPY-BACK EXACT: every file of the box's MANIFEST.sha256 at its sha256, nothing else but runner.out and runner.rc")
        return 0
    if len(argv) < 6 or argv[0] != "data":
        print(__doc__)
        return 2
    day, arm, copy, home, lf = argv[1], argv[2], os.path.abspath(argv[3]), argv[4].rstrip("/"), argv[5]
    rest = argv[6:]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day) or arm != "A":
        print(f"COLLECT-REFUSED: unreadable day {day!r} or arm {arm!r}")
        return 2
    outside = nrdir = nrlate = None
    while rest:
        if rest[0] == "--outside" and len(rest) >= 2:
            if os.environ.get("RB_DESKTEST") != "1":
                print("COLLECT-REFUSED: --outside is the desk tests' own (RB_DESKTEST=1)")
                return 2
            outside = os.path.abspath(rest[1])
            rest = rest[2:]
        elif rest[0] == "--neverrun" and len(rest) >= 2:
            nrdir = os.path.abspath(rest[1])
            rest = rest[2:]
        elif rest[0] == "--neverrun-late" and len(rest) >= 2:
            nrlate = os.path.abspath(rest[1])
            rest = rest[2:]
        else:
            print(f"COLLECT-REFUSED: unreadable arguments {rest!r}")
            return 2
    nrfiles = []
    for d_, tag in ((nrdir, "card"), (nrlate, "late")):
        if not d_:
            continue
        one = [(os.path.join(d_, "neverrun-e210-card.txt"), f"neverrun-e210-{tag}.txt"),
               (os.path.join(d_, "neverrun-e210-card.json"), f"neverrun-e210-{tag}.json"),
               (os.path.join(d_, "named-by.json"), f"named-by-{tag}.json")]
        miss = [x for x, _ in one if not os.path.isfile(x)]
        if miss:
            print(f"COLLECT-REFUSED: the never-run report ({'step 6n' if tag == 'card' else 'step 12n'}) is not whole in {d_} (missing {len(miss)} of 3 files)")
            return 3
        nrfiles += one
    if not home.startswith("/") or len(home) < 6:
        print(f"COLLECT-REFUSED: the box home {home!r} is not an absolute path")
        return 2
    try:
        login = open(lf).read().strip()
    except OSError:
        login = ""
    if not re.fullmatch(r"[a-z_][a-z0-9_-]{1,31}", login):
        print("COLLECT-REFUSED: the login file gives no login (the look writes it: RB_OUT/box-login-<box>.txt)")
        return 2
    bad = copy_back_exact(copy)
    if bad:
        print("COPY-BACK NOT EXACT: " + "; ".join(bad[:10]))
        return 3
    print("COPY-BACK EXACT: every file of the box's MANIFEST.sha256 at its sha256")
    try:
        q = json.load(open(os.path.join(copy, "queue.json")))
    except (OSError, ValueError):
        q = {}
    ran = any(x.get("ran") for x in q.get("queue", []))
    m = re.search(r"T(\d+)-A$", os.path.basename(copy.rstrip("/")))
    t0 = m.group(1) if m else str(q.get("t0", "0"))
    box = C.ARMS[arm]["data_dir"]
    rel = (f"docs/reports/data/{day}-e210-switch-test-{box}" if ran else f"docs/reports/gate-stops/{day}-e210-switch-test-T{t0}-{box}")
    dabs = os.path.join(outside, os.path.basename(rel)) if outside else os.path.join(REPO, rel)
    if os.path.exists(dabs):
        print(f"COLLECT-REFUSED: {rel} exists already (never merge into an earlier copy)")
        return 3
    os.makedirs(dabs)
    dst = os.path.join(dabs, "session")
    shutil.copytree(copy, dst)
    left = []
    for dp, dn, fn in os.walk(dst):
        for n in fn:
            p = os.path.join(dp, n)
            body = scrub_file(p, home, login)
            if left_over(body, home, login):
                left.append(os.path.relpath(p, dabs))
    if left:
        print(f"SCRUB FAILED: a /home/ path or the box login is left in " + ", ".join(left[:10]))
        return 3
    print("scrubbed: the box home -> '~', the box login -> '<login>', no /home/ path left")
    for src, name in nrfiles:              # the never-run reports (3n), scrubbed like the rest
        dst2 = os.path.join(dabs, name)
        shutil.copyfile(src, dst2)
        body = scrub_file(dst2, home, login)
        if left_over(body, home, login):
            print(f"SCRUB FAILED: a /home/ path or the box login is left in {name}")
            return 3
    if nrfiles:
        print("the never-run report(s) copied in: " + ", ".join(n for _, n in nrfiles))
    if ran:
        cmd = [sys.executable, "-I", "-B", os.path.join(HERE, "reduce_e210.py"), "--arm", f"{arm}={dst}",
               "--out", os.path.join(dabs, "data-e210.json"), "--txt", os.path.join(dabs, "reduce-e210.txt")]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(os.path.join(dabs, "data-e210.json")):
            print(f"REDUCER FAILED: rc {r.returncode}: {r.stdout[-300:]} {r.stderr[-300:]}")
            return 3
        for p in ("data-e210.json", "reduce-e210.txt"):
            body = scrub_file(os.path.join(dabs, p), home, login)
            if left_over(body, home, login):
                print(f"SCRUB FAILED: a /home/ path or the box login is left in {p}")
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
    print(f"{len(rows)} files in SHA256SUMS; the scrub clean" + ("; data-e210.json written" if ran else "; no run started: a gate stop's record"))
    print(("COLLECTED " if ran else "COLLECTED-GATE-STOP ") + (dabs if outside else rel))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
