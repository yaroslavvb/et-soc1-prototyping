#!/usr/bin/env python3
"""1119-mmsweep4: the harness, every file of src/ at its sha256 (src/SRC-SHA256SUMS), so a box runs exactly the kit that was
read at the desk (Python's own modules only).

    python3 -I -B src/check_mms.py --make              writes src/SRC-SHA256SUMS (the desk)
    python3 -I -B src/check_mms.py --check             re-makes it in memory and compares: CHECK PASS
    python3 -B src/check_mms.py --box [--only-src]     on a box: every listed file at its sha256 and no unlisted file in src/
                                                       (HARNESS OK: <n> files); --only-src: src/rgm136 and src/ettelem only
    python3 -B src/check_mms.py --prune                on a box, after a re-push left files the new src/ no longer lists:
                                                       removes those files from src/ only (regular files, never a link or
                                                       anything outside src/), refused while a session of the kit runs
SPDX-License-Identifier: Apache-2.0
"""
import fcntl
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
SUMS = os.path.join(HERE, "SRC-SHA256SUMS")
SKIP_DIRS = {"__pycache__"}


def files():
    out = []
    for dp, dn, fn in os.walk(HERE):
        dn[:] = sorted(d for d in dn if d not in SKIP_DIRS)
        for n in sorted(fn):
            p = os.path.join(dp, n)
            r = os.path.relpath(p, ROOT)
            if r == "src/SRC-SHA256SUMS" or n.endswith(".pyc"):
                continue
            out.append(r)
    return sorted(out)


def sha(r):
    with open(os.path.join(ROOT, r), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def make():
    return "".join(f"{sha(r)}  {r}\n" for r in files())


def read_sums():
    out = {}
    for ln in open(SUMS):
        h, r = ln.rstrip("\n").split("  ", 1)
        out[r] = h
    return out


def main(argv):
    if "--make" in argv:
        txt = make()
        with open(SUMS, "w") as f:
            f.write(txt)
        print(f"wrote src/SRC-SHA256SUMS ({txt.count(chr(10))} files)")
        return 0
    if "--check" in argv:
        same = open(SUMS).read() == make()
        print(f"src/SRC-SHA256SUMS re-made: {'equal' if same else 'DIFFERS'}")
        print("CHECK PASS" if same else "CHECK FAIL")
        return 0 if same else 1
    if "--prune" in argv:
        os.makedirs(os.path.join(ROOT, "run"), exist_ok=True)
        with open(os.path.join(ROOT, "run", "box.lock"), "a+") as lk:
            try:
                fcntl.flock(lk.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                print("PRUNE REFUSED: run/box.lock is held (a session, a build or a dry pass of this kit runs on this box)")
                return 3
            want = read_sums()
            gone = []
            for r in files():
                p = os.path.join(ROOT, r)
                if r in want or not r.startswith("src/") or os.path.islink(p) or not os.path.isfile(p) \
                        or not os.path.realpath(p).startswith(os.path.realpath(HERE) + os.sep):
                    continue
                os.remove(p)
                gone.append(r)
            print(f"PRUNED {len(gone)} file(s) the harness does not list: {gone}")
        return 0
    if "--box" in argv:
        want = read_sums()
        only = "--only-src" in argv
        if only:
            want = {r: h for r, h in want.items() if r.startswith("src/rgm136/") or r.startswith("src/ettelem/")}
        bad = []
        for r, h in sorted(want.items()):
            got = sha(r) if os.path.isfile(os.path.join(ROOT, r)) else "missing"
            if got != h:
                bad.append(f"{r}: {got[:16]} (want {h[:16]})")
        if not only:
            extra = [r for r in files() if r not in want]
            bad += [f"{r}: not in SRC-SHA256SUMS" for r in extra]
        if bad:
            print("HARNESS DIFFERS: " + "; ".join(bad))
            return 9
        print(f"HARNESS OK: {len(want)} files at src/SRC-SHA256SUMS's sha256" + (" (the two build sources)" if only else ""))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
