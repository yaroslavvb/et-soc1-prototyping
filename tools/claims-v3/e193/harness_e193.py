#!/usr/bin/env python3
"""E193's harness (Q177, lane kit-e193, Sat 14 Nov 2026, before any E193 datum): every file the box runs or reads for E193, at its
sha256, E189's harness form (check_e189.py --list/--box) for one box root.

    python3 -I -B harness_e193.py --list               the sync list, one repository path a line (harness-e193.json last)
    python3 -I -B harness_e193.py --make               write harness-e193.json from the files as they are (the kit's own step)
    python3 -I -B harness_e193.py --check              harness-e193.json re-made in memory equals the committed one: CHECK PASS
    python3 -I -B harness_e193.py --box [--root DIR]   every file of harness-e193.json at its sha256 under DIR (default: the repository's
                                                       top): HARNESS OK: <n> files, or HARNESS FAIL naming each

The files: the registration's (every path SHA256SUMS-e193-registration names, and the list itself: E193.md, proposal/ byte for byte,
desk/), the kit's box files (the session's wrapper, the checker, the build, the preflight, this file), E128's guard (the only way the
session reaches the telemetry reader) and the device-command checker with its table (the preflight runs them on the box). The box root
is <tree>/build/claims-v3/aifoundry3/e193 on aifoundry3, where step 5's rsync -R puts each file at its repository path. The launch
passes harness-e193.json's own sha256 (read from the lab clone, where step 2 pins it by the kit's list) and the session checks it before
this file runs. Exit 0, 3 a failed check, 2 usage. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
E = "tools/claims-v3/e193"
JSON = os.path.join(HERE, "harness-e193.json")
REG_LIST = E + "/SHA256SUMS-e193-registration"
KIT_BOX = [E + "/session_e193.sh", E + "/check_e193.py", E + "/build_e193.sh", E + "/preflight_e193.sh", E + "/harness_e193.py"]
OTHERS = ["tools/claims-v3/e128/ettelem_guard.sh", "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json"]


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def paths():
    reg = []
    with open(os.path.join(REPO, REG_LIST)) as f:
        for ln in f:
            if ln.strip():
                reg.append(ln.rstrip("\n").split("  ", 1)[1])
    return sorted(set(reg + [REG_LIST] + KIT_BOX + OTHERS))


def made():
    ps = paths()
    return {"schema": "e193-harness/1", "count": len(ps), "files": {p: sha(os.path.join(REPO, p)) for p in ps}}


def main(argv):
    if argv == ["--list"]:
        for p in paths():
            print(p)
        print(E + "/harness-e193.json")
        return 0
    if argv == ["--make"]:
        with open(JSON, "w") as f:
            json.dump(made(), f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"harness-e193.json written: {made()['count']} files")
        return 0
    if argv == ["--check"]:
        with open(JSON) as f:
            have = json.load(f)
        want = made()
        if have == want:
            print(f"CHECK PASS: harness-e193.json re-made equals the committed one ({want['count']} files)")
            return 0
        diff = sorted(set(have.get("files", {}).items()) ^ set(want["files"].items()))
        print("CHECK FAIL: harness-e193.json differs from the files as they are: " + ", ".join(p for p, _ in diff[:8]))
        return 3
    if argv[:1] == ["--box"]:
        root = argv[argv.index("--root") + 1] if "--root" in argv else REPO
        with open(os.path.join(root, E, "harness-e193.json")) as f:
            h = json.load(f)
        bad = []
        for p, want in sorted(h["files"].items()):
            q = os.path.join(root, p)
            if not os.path.isfile(q):
                bad.append(f"missing {p}")
            elif sha(q) != want:
                bad.append(f"differs {p}")
        if bad or len(h["files"]) != h.get("count"):
            print("HARNESS FAIL: " + ", ".join(bad[:10]) + (f" (and {len(bad) - 10} more)" if len(bad) > 10 else ""))
            return 3
        print(f"HARNESS OK: {len(h['files'])} files at their sha256 under the root")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
