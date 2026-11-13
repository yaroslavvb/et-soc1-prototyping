#!/usr/bin/env python3
"""E190's collection at the desk (Q169, the kit, Fri 13 Nov 2026, before any E190 datum): the desk half of steps 11 and 12, after each
arm's copy-back. Python's own modules only.

    /usr/bin/python3 -B tools/claims-v3/e190/collect_e190.py copy-check COPY
        COPY-BACK EXACT: every file of the box's MANIFEST.sha256 is in COPY at its sha256, and COPY holds nothing else but MANIFEST.sha256
        itself, runner.out and runner.rc (the wrapper's two files); else exit 3
    /usr/bin/python3 -B tools/claims-v3/e190/collect_e190.py data DATA --arm A COPY BOXHOME LOGINFILE [--arm B COPY BOXHOME LOGINFILE]
        DATA  docs/reports/data/<the window's day>-e190-large-gemm (new; refused if it exists)
  1. each arm's copy checked again (COPY-BACK EXACT), then copied whole into DATA/aifoundry2/ (arm A) or DATA/aifoundry1-c1/ (arm B);
  2. THE SCRUB: the box's home path (as the box reported it) becomes "~", and OUR OWN BOX LOGIN (as the look read it on that box, the
     one line of LOGINFILE) becomes "<login>", in every text and .gz file; then no file may hold a /home/ path or the login (exit 3);
  3. the reducer (reduce_e190.py, as committed) over the arms collected: DATA/data-e190.json (the frozen scorer's input) and
     DATA/reduce-e190.txt;
  4. DATA/SHA256SUMS (paths beside it, as the lab's data lists).
The scorer is NOT run here: s24_score_e190.sh runs score_e190.py on the committed DATA, after the data commit. Exit 0 collected, 3 a
gate, 2 usage. RB_DESKTEST=1 with --data-outside lets the desk tests write DATA in their scratch (never on the card day).
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e190_common as C  # noqa: E402

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


def main(argv):
    if len(argv) >= 2 and argv[0] == "copy-check":
        bad = copy_back_exact(os.path.abspath(argv[1]))
        if bad:
            print("COPY-BACK NOT EXACT: " + "; ".join(bad[:10]))
            return 3
        print("COPY-BACK EXACT: every file of the box's MANIFEST.sha256 at its sha256, nothing else but runner.out and runner.rc")
        return 0
    if len(argv) < 6 or argv[0] != "data" or "--arm" not in argv:
        print(__doc__)
        return 2
    data = argv[1]
    arms, i = {}, 2
    while i < len(argv):
        if argv[i] == "--arm" and i + 4 < len(argv) + 0 and argv[i + 1] in ("A", "B"):
            arms[argv[i + 1]] = (os.path.abspath(argv[i + 2]), argv[i + 3].rstrip("/"), argv[i + 4])
            i += 5
        elif argv[i] == "--data-outside":
            i += 1
        else:
            print(f"COLLECT-REFUSED: unreadable arguments at {argv[i]!r}")
            return 2
    dabs = os.path.join(REPO, data) if not os.path.isabs(data) else data
    rel, base = os.path.relpath(dabs, REPO), REPO
    if os.environ.get("RB_DESKTEST") == "1" and "--data-outside" in argv:     # the desk tests only: a data folder in their scratch
        rel, base = os.path.basename(dabs), os.path.dirname(dabs)
    if not (rel.startswith("docs/reports/data/") or base != REPO) or not re.search(r"\d{4}-\d{2}-\d{2}-e190-large-gemm$", rel):
        print(f"COLLECT-REFUSED: {rel} is not an E190 data directory docs/reports/data/<day>-e190-large-gemm")
        return 2
    if os.path.exists(dabs):
        print(f"COLLECT-REFUSED: {rel} exists already (never merge into an earlier copy)")
        return 3
    logins = {}
    for arm, (copy, home, lf) in arms.items():
        if not home.startswith("/") or len(home) < 6:
            print(f"COLLECT-REFUSED: arm {arm}'s box home {home!r} is not an absolute path")
            return 2
        try:
            lg = open(lf).read().strip()
        except OSError:
            lg = ""
        if not re.fullmatch(r"[a-z_][a-z0-9_-]{1,31}", lg):
            print(f"COLLECT-REFUSED: arm {arm}'s login file gives no login (the look writes it: RB_OUT/box-login-<box>.txt)")
            return 2
        logins[arm] = lg
        bad = copy_back_exact(copy)
        if bad:
            print(f"COPY-BACK NOT EXACT (arm {arm}): " + "; ".join(bad[:10]))
            return 3
        print(f"COPY-BACK EXACT (arm {arm}): every file of the box's MANIFEST.sha256 at its sha256")
    os.makedirs(dabs)
    for arm, (copy, home, lf) in arms.items():
        dst = os.path.join(dabs, C.ARMS[arm]["data_dir"])
        shutil.copytree(copy, dst)
        left = []
        for dp, dn, fn in os.walk(dst):
            for n in fn:
                p = os.path.join(dp, n)
                body = scrub_file(p, home, logins[arm])
                if home.encode() in body or b"/home/" in body or re.search(rb"(?<![A-Za-z0-9_.-])" + re.escape(logins[arm].encode()) + rb"(?![A-Za-z0-9_-])", body):
                    left.append(os.path.relpath(p, dabs))
        if left:
            print(f"SCRUB FAILED (arm {arm}): a /home/ path or the box login is left in " + ", ".join(left[:10]))
            return 3
        print(f"scrubbed arm {arm}: the box home -> '~', the box login -> '<login>', no /home/ path left")
    cmd = [sys.executable, "-I", "-B", os.path.join(HERE, "reduce_e190.py")]
    for arm in sorted(arms):
        cmd += ["--arm", f"{arm}={os.path.join(dabs, C.ARMS[arm]['data_dir'])}"]
    cmd += ["--out", os.path.join(dabs, "data-e190.json"), "--txt", os.path.join(dabs, "reduce-e190.txt")]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0 or not os.path.exists(os.path.join(dabs, "data-e190.json")):
        print(f"REDUCER FAILED: rc {r.returncode}: {r.stdout[-300:]} {r.stderr[-300:]}")
        return 3
    for p in ("data-e190.json", "reduce-e190.txt"):     # the reducer names the session folders only; scrub its files too
        for arm in arms:
            scrub_file(os.path.join(dabs, p), arms[arm][1], logins[arm])
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
    print(f"COLLECTED {rel}: arms {', '.join(sorted(arms))}; {len(rows)} files in SHA256SUMS; the scrub clean; data-e190.json written")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
