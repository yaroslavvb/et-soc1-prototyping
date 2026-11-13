#!/usr/bin/env python3
"""E189's collection at the desk (Q167, the kit, Thu 12 Nov 2026, before any E189 datum): step 11's desk half, after the copy-back.

    /usr/bin/python3 -B tools/claims-v3/e189/collect_e189.py COPY DATA --box-home PATH
        COPY  the session's directory as rsync copied it from the box (RB_OUT/e189-raw/T<T0>/)
        DATA  docs/reports/data/<day>-e189-blind-day-aifoundry3 (new; refused if it exists)

  1. COPY-BACK EXACT: every file of the box's MANIFEST.sha256 is in COPY at its sha256, and COPY holds nothing else but MANIFEST.sha256
     itself and runner.rc (the one file the wrapper writes after it); else exit 3, nothing written;
  2. DATA in E189.md section 8.1's form: passes/<config>/p<k>/ (telemetry.jsonl.gz, host.json, host-raw.json for the ledger programs,
     host.err, host.rec for sparse parity, run.json, pass.json) and session/ (session.log, the two config reads, stop-path.json, the smoke,
     the anchors, queue.json, the session's whole telemetry, runner.out, runner.rc, MANIFEST.sha256);
  3. each pass reduced by workloads/sparseparity/tools/energy_reduce.py, UNCHANGED (run as its own process with numpy), into its
     energy.json; the one field it writes with the reducing machine's path, "dir", is then set to the pass's path in the repository
     (the reducer records os.path.abspath of the folder it read, which here is a desk path);
  4. THE SCRUB: the box's home path (as the box reported it) becomes "~" in every text file, and no file may then hold it, any other
     /home/ path, or a desk path (the desk-path gate, nopath_q142s.py, runs after this, from step 11);
  5. DATA/SHA256SUMS (paths beside it, as the lab's data lists).
The scorer is NOT run here: s24_score_e189.sh runs score_e189.py on the committed DATA, after the data commit. Exit 0 collected, 3 a
gate, 2 usage. RB_DESKTEST=1 with --data-outside lets the runner's desk test write DATA in its scratch (never on the card day).
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
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


def scrub_file(p, box_home):
    raw = open(p, "rb").read()
    if p.endswith(".gz"):
        data = gzip.decompress(raw)
        new = data.replace(box_home.encode(), b"~")
        if new != data:
            with gzip.open(p, "wb") as f:
                f.write(new)
        return new
    if p.endswith(TEXT) or os.path.basename(p) in ("runner.rc",):
        new = raw.replace(box_home.encode(), b"~")
        if new != raw:
            open(p, "wb").write(new)
        return new
    return raw


def main(argv):
    if len(argv) < 4 or argv[2] != "--box-home":
        print(__doc__)
        return 2
    copy, data, box_home = os.path.abspath(argv[0]), argv[1], argv[3].rstrip("/")
    if not box_home.startswith("/") or len(box_home) < 6:
        print(f"COLLECT-REFUSED: the box's home path {box_home!r} is not an absolute path")
        return 2
    dabs = os.path.join(REPO, data) if not os.path.isabs(data) else data
    rel = os.path.relpath(dabs, REPO)
    base = REPO
    if os.environ.get("RB_DESKTEST") == "1" and "--data-outside" in argv:   # the runner's desk test only: a data folder in its scratch
        rel, base = os.path.basename(dabs), os.path.dirname(dabs)
    if not (rel.startswith("docs/reports/data/") or base != REPO) or "e189" not in rel:
        print(f"COLLECT-REFUSED: {rel} is not an E189 data directory under docs/reports/data/")
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
            body = scrub_file(p, box_home)
            if box_home.encode() in body or b"/home/" in body:
                left.append(os.path.relpath(p, dabs))
    if left:
        print("SCRUB FAILED: a /home/ path is left in " + ", ".join(left[:10]))
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
    if nbad:
        print("REDUCER FAILED: " + "; ".join(nbad))
        return 3
    print(f"COLLECTED {rel}: {npass} passes reduced; {len(rows)} files in SHA256SUMS; the scrub clean (no /home/ path)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
