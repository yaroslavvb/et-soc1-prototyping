#!/usr/bin/env python3
"""E191's collection at the desk (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191 datum): step 11's
desk half, after the copy-back. E189's collector (tools/claims-v3/e189/collect_e189.py, unchanged beside it) with E191's names, and one
addition, E190's scrub of the box login (collect_e190.py's form):

    /usr/bin/python3 -B tools/claims-v3/e191/collect_e191.py COPY DATA --box-home PATH --box-login LOGINFILE
        COPY      the session's directory as rsync copied it from the box (RB_OUT/e191-raw/T<T0>/)
        DATA      docs/reports/data/<day>-e191-blind-day-aifoundry1-c1 (new; refused if it exists)
        LOGINFILE RB_OUT/box-login-aifoundry1.txt (the look writes it: our own login on the box, one line)

  1. COPY-BACK EXACT: every file of the box's MANIFEST.sha256 is in COPY at its sha256, and COPY holds nothing else but MANIFEST.sha256
     itself and runner.rc (the one file the wrapper writes after it); else exit 3, nothing written;
  2. DATA in E191.md section 8.1's form: passes/<config>/p<k>/ (telemetry.jsonl.gz, host.json, host-raw.json for the ledger programs,
     host.err, host.rec for sparse parity, run.json, pass.json) and session/ (session.log, the two config reads and their stderr, the
     identity record, et-who's counts, stop-path.json, the smoke, the anchors, queue.json, commands.jsonl, the session's whole telemetry,
     runner.out, runner.rc, MANIFEST.sha256);
  3. each pass reduced by workloads/sparseparity/tools/energy_reduce.py, UNCHANGED (run as its own process with numpy), into its
     energy.json; its "dir" field is then set to the pass's path in the repository;
  4. THE SCRUB: the box's home path becomes "~" and our own box login "<login>" (as a whole word) in every text and .gz file, and no file
     may then hold the home, any other /home/ path, or the login (the desk-path gate, nopath_q142s.py, runs after this, from step 11);
  5. DATA/SHA256SUMS (paths beside it, as the lab's data lists), and DATA/FILES.txt: every file under DATA by its path, so the README's
     Files table can be checked against it (E189's README left out sparse parity's host.rec: its card lane's incident 1).
The scorer is NOT run here: s24_score_e191.sh runs score_e191.py on the committed DATA, after the data commit. Exit 0 collected, 3 a
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
        print("COLLECT-REFUSED: the box login file gives no login (the look writes RB_OUT/box-login-aifoundry1.txt)")
        return 2
    dabs = os.path.join(REPO, data) if not os.path.isabs(data) else data
    rel = os.path.relpath(dabs, REPO)
    base = REPO
    if os.environ.get("RB_DESKTEST") == "1" and "--data-outside" in argv:   # the runner's desk test only: a data folder in its scratch
        rel, base = os.path.basename(dabs), os.path.dirname(dabs)
    if not (rel.startswith("docs/reports/data/") or base != REPO) or "e191" not in rel:
        print(f"COLLECT-REFUSED: {rel} is not an E191 data directory under docs/reports/data/")
        return 2
    if os.path.exists(dabs):
        print(f"COLLECT-REFUSED: {rel} exists already (never merge into an earlier copy)")
        return 3
    bad = copy_back_exact(copy)
    if bad:
        print("COPY-BACK NOT EXACT: " + "; ".join(bad[:10]))
        return 3
    print("COPY-BACK EXACT: every file of the box's MANIFEST.sha256 at its sha256, nothing else but runner.rc")
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
