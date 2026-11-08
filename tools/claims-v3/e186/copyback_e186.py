#!/usr/bin/env python3
"""E186 (Q158, the kit): the exact copy-back (E185's form, tools/claims-v3/e185/collect_e185_v2.sh's check, ported to E186's layout), run by
step 11 (rb/s22_collect_e186.sh) after its copies and before any reduction. The session's last act on the box is
build/e186/T<T0>/MANIFEST.sha256 (session_e186.sh): the sha256 of every file of its session directory and of every block directory its
blocks.txt names. Here every manifest line is read back from the desk copy, and the copied directories must hold nothing else:

    build/e186/T<T0>/<f>                       ->  <raw>/logs/<f>
    build/claims-v3/aifoundry3/<tree>/<p>/<f>  ->  <raw>/<tree>/<p>/<f>       (<tree>: e186, e186-smoke, e186-stoptest)

    /usr/bin/python3 -B tools/claims-v3/e186/copyback_e186.py <raw copy> <T0>

Prints "COPY-BACK EXACT <n> files (every manifest line read back, and nothing else)" and exits 0; or "COPY-BACK NO-MANIFEST", "COPY-BACK
DIFFERS: ..." (a file missing or with other bytes) or "COPY-BACK EXTRA: ..." (a copied file the manifest does not list) and exits 4. The
desk's own additions are not the session's and are read apart: <raw>/logs/step6/ (the day's step-6 record), <raw>/logs/absent-on-box.txt
and the manifest itself. Standard library only; it reads and writes nothing else.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import os
import sys

TREES = ("e186", "e186-smoke", "e186-stoptest")
DESK_OWN = ("MANIFEST.sha256", "absent-on-box.txt")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def local(raw, t0, p):
    pre = f"build/e186/T{t0}/"
    if p.startswith(pre):
        return os.path.join(raw, "logs", p[len(pre):])
    pre = "build/claims-v3/aifoundry3/"
    if p.startswith(pre) and p[len(pre):].split("/", 1)[0] in TREES:
        return os.path.join(raw, p[len(pre):])
    return None


def main(argv):
    raw, t0 = argv[0], argv[1]
    man = os.path.join(raw, "logs", "MANIFEST.sha256")
    if not os.path.exists(man):
        print("COPY-BACK NO-MANIFEST: the session's MANIFEST.sha256 is not in the copy (a session that never ended, or nothing copied)")
        return 4
    want, bad = {}, []
    for line in open(man):
        if not line.strip():
            continue
        h, p = line.split(None, 1)
        p = p.strip()
        q = local(raw, t0, p)
        if q is None:
            bad.append(f"{p}: outside the session's directory and its blocks")
            continue
        want[os.path.abspath(q)] = (h, p)
    for q, (h, p) in sorted(want.items()):
        if not os.path.isfile(q):
            bad.append(f"{p}: not copied")
        elif sha(q) != h:
            bad.append(f"{p}: copied with other bytes")
    have = set()
    logs = os.path.join(raw, "logs")
    for dp, dns, fs in os.walk(logs):
        if os.path.relpath(dp, logs).split(os.sep)[0] == "step6":
            continue
        for f in fs:
            if dp == logs and f in DESK_OWN:
                continue
            have.add(os.path.abspath(os.path.join(dp, f)))
    araw, alogs = os.path.abspath(raw), os.path.abspath(logs)
    blocks = set()
    for q in want:
        if not q.startswith(alogs + os.sep):
            parts = os.path.relpath(q, araw).split(os.sep)
            blocks.add(os.path.join(parts[0], parts[1]))
    for t in TREES:
        td = os.path.join(raw, t)
        if not os.path.isdir(td):
            continue
        for b in os.listdir(td):
            bd = os.path.join(td, b)
            if os.path.isdir(bd) and os.path.join(t, b) not in blocks:
                bad.append(f"{t}/{b}: a block directory the manifest does not name")
            for dp, _, fs in os.walk(bd):
                for f in fs:
                    have.add(os.path.abspath(os.path.join(dp, f)))
    extra = sorted(have - set(want))
    if bad:
        print("COPY-BACK DIFFERS: " + "; ".join(bad[:20]) + (f" (and {len(bad) - 20} more)" if len(bad) > 20 else ""))
        return 4
    if extra:
        print("COPY-BACK EXTRA: files the session's manifest does not list: " + "; ".join(os.path.relpath(x, raw) for x in extra[:20]))
        return 4
    print(f"COPY-BACK EXACT {len(want)} files (every manifest line read back, and nothing else)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
