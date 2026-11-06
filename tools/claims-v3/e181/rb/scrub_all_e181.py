#!/usr/bin/env python3
"""E181 (M11's session 2): the login scrub's --check in EVERY directory of E181's data directory (the E181 kit verifier's fault 5, Fri 6 Nov
2026; the kit's README.md.dated-note-1.md). Step 22 v1 ran E164's scrub (tools/claims-v3/e164/scrub_etwho_e164.py, which reads one directory
level and text files only) over logs/ alone, as q143k's v1 and v2 did, so a pass directory's run.log or STOP could carry another account's
holder line unread; E176's records round ran the check by hand in all 8 of its directories, each .gz unpacked beside it. This does the same:

  for every directory under the data directory (the data directory itself included): E164's scrub --check, unchanged, with --owner;
  for every directory holding .gz files: each .gz unpacked into a fresh directory under <work dir> (never inside the data directory), and
  the same --check there.

It rewrites nothing in the data directory. It exits 0 when every check reads clean, 1 when any finds another login (the step stops 16
before the score), 2 on a usage error. Its unpacked copies are removed at the end. Standard library only (the scrub is run as its own
process, /usr/bin/python3 -B).

    python3 -B tools/claims-v3/e181/rb/scrub_all_e181.py <data dir> --owner <login> --work <an empty dir outside the repo>
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
TREE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
SCRUB = os.path.join(TREE, "tools", "claims-v3", "e164", "scrub_etwho_e164.py")


def check(d, owner, label):
    p = subprocess.run(["/usr/bin/python3", "-B", SCRUB, "--check", d, "--owner", owner], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       universal_newlines=True)
    tail = " ".join(p.stdout.strip().splitlines()[-2:])[:300]
    print(f"{'CLEAN' if p.returncode == 0 else 'LOGIN-LEFT'} {label} (rc {p.returncode}){': ' + tail if p.returncode != 0 else ''}")
    return p.returncode == 0


def main(a):
    if len(a) != 5 or a[1] != "--owner" or a[3] != "--work":
        print(__doc__)
        return 2
    d, owner, work = os.path.abspath(a[0]), a[2], os.path.abspath(a[4])
    if not os.path.isdir(d):
        print(f"usage: no such data directory {a[0]}")
        return 2
    if work == d or work.startswith(d + os.sep):
        print("usage: the work directory must be outside the data directory")
        return 2
    if os.path.exists(work) and os.listdir(work):
        print("usage: the work directory must be new or empty")
        return 2
    os.makedirs(work, exist_ok=True)
    ok, n_dirs, n_gz = True, 0, 0
    for cur, dirs, files in os.walk(d):
        dirs.sort()
        rel = os.path.relpath(cur, d)
        n_dirs += 1
        ok &= check(cur, owner, f"{rel}/")
        gz = sorted(f for f in files if f.endswith(".gz"))
        if gz:
            u = os.path.join(work, rel.replace(os.sep, "__") if rel != "." else "_top")
            os.makedirs(u)
            for f in gz:
                with gzip.open(os.path.join(cur, f), "rb") as fi, open(os.path.join(u, f[:-3]), "wb") as fo:
                    shutil.copyfileobj(fi, fo)
                n_gz += 1
            ok &= check(u, owner, f"{rel}/ (its {len(gz)} .gz file(s) unpacked)")
    shutil.rmtree(work)
    print(f"SCRUB-ALL {'CLEAN' if ok else 'LOGIN-LEFT'}: {n_dirs} directories and {n_gz} .gz file(s) unpacked, each read by E164's scrub --check")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
