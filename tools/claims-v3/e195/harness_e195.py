#!/usr/bin/env python3
"""E195's harness (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): every file the box runs or reads for E195, at its
sha256, E193's harness form (harness_e193.py) for one box root.

    python3 -I -B harness_e195.py --list               the sync list, one repository path a line (harness-e195.json last)
    python3 -I -B harness_e195.py --make               write harness-e195.json from the files as they are (the kit's own step)
    python3 -I -B harness_e195.py --check              harness-e195.json re-made in memory equals the committed one: CHECK PASS
    python3 -I -B harness_e195.py --box [--root DIR]   every file of harness-e195.json at its sha256 under DIR (default: the repository's
                                                       top): HARNESS OK: <n> files, or HARNESS FAIL naming each

The files: the registration's (every path SHA256SUMS-e195-registration names, and the list itself: E195.md, proposal/ byte for byte,
desk/); the kit's box files (the session, its blocks and library, its runner, the checker, the build, the preflight, this file, the
generator's output gen-e195-noms/ and the dry listing the dry pass is checked against); the lab's block library, text hash and E128's guard
(the only way the blocks reach the telemetry reader); and the device-command checker with its table (the preflight runs them on the box).
The box root is <tree>/build/claims-v3/aifoundry3/e195 on aifoundry3, where step 5's rsync -R puts each file at its repository path. The
launch passes harness-e195.json's own sha256 (read from the lab clone, where step 2 pins it by the kit's list) and the session checks it
before this file runs. Exit 0, 3 a failed check, 2 usage. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
E = "tools/claims-v3/e195"
JSON = os.path.join(HERE, "harness-e195.json")
REG_LIST = E + "/SHA256SUMS-e195-registration"
KIT_BOX = [E + "/session_e195.sh", E + "/block_e195.sh", E + "/lib_e195.sh", E + "/runitems_e195.py", E + "/check_e195.py",
           E + "/build_e195.sh", E + "/preflight_e195.sh", E + "/harness_e195.py", E + "/gen-e195-noms/manifest.json",
           E + "/gen-e195-noms/counts.json", E + "/desk/dry-e195-noms-aifoundry3.txt"]
OTHERS = ["tools/claims-v3/lib.sh", "tools/claims-v3/text_hash.sh", "tools/claims-v3/e128/ettelem_guard.sh",
          "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json"]


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
    return {"schema": "e195-harness/1", "count": len(ps), "files": {p: sha(os.path.join(REPO, p)) for p in ps}}


def main(argv):
    if argv == ["--list"]:
        for p in paths():
            print(p)
        print(E + "/harness-e195.json")
        return 0
    if argv == ["--make"]:
        with open(JSON, "w") as f:
            json.dump(made(), f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"harness-e195.json written: {made()['count']} files")
        return 0
    if argv == ["--check"]:
        with open(JSON) as f:
            have = json.load(f)
        want = made()
        if have == want:
            print(f"CHECK PASS: harness-e195.json re-made equals the committed one ({want['count']} files)")
            return 0
        diff = sorted(set(have.get("files", {}).items()) ^ set(want["files"].items()))
        print("CHECK FAIL: harness-e195.json differs from the files as they are: " + ", ".join(p for p, _ in diff[:8]))
        return 3
    if argv[:1] == ["--box"]:
        root = argv[argv.index("--root") + 1] if "--root" in argv else REPO
        with open(os.path.join(root, E, "harness-e195.json")) as f:
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
