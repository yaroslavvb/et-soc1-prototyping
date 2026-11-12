#!/usr/bin/env python3
"""E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): harness-e183-v2.json, the pins of note 4's
box files and of v1's harness file, which harness_e183_v2.py reads on the box and at the desk.

    /usr/bin/python3 -B tools/claims-v3/e183/make_harness_e183_v2.py           # writes harness-e183-v2.json beside this file
    /usr/bin/python3 -B tools/claims-v3/e183/make_harness_e183_v2.py --check   # re-makes it in memory and compares: CHECK PASS or exit 1

  harness_v1  tools/claims-v3/e183/harness-e183.json (cc597bf2) and its sha256: v1's 80 box files, 40 build inputs and 38-file build tree,
              unchanged; harness_e183_v2.py runs v1's own check on them.
  files       note 4's seven box files: train_check_e183.sh, build_host_e183_v2.sh, block_e183_v2.sh, queue_e183_v2.sh,
              session_e183_v2.sh, preflight_e183_v2.sh and harness_e183_v2.py, each at its sha256.
Step 5 (rb/s07_a3_sync_e183.sh, unchanged) syncs E183's whole directory, so it carries these files and both harness files to the box.
With --check it refuses unless every file it pins is committed and clean (git), so the pins it passes are the committed bytes; it writes
the file from the files as they stand (note 4's commit holds the files and this file together). Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REL = "tools/claims-v3/e183"
V1 = f"{REL}/harness-e183.json"
NOTE4_BOX = ["train_check_e183.sh", "build_host_e183_v2.sh", "block_e183_v2.sh", "queue_e183_v2.sh", "session_e183_v2.sh",
             "preflight_e183_v2.sh", "harness_e183_v2.py"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", TOP] + list(a), capture_output=True, text=True, check=True).stdout


def build(committed):
    paths = [V1] + [f"{REL}/{f}" for f in NOTE4_BOX]
    if committed:
        tracked = set(git("ls-files", "--", *paths).splitlines())
        missing = [p for p in paths if p not in tracked]
        if missing:
            raise SystemExit("not committed: " + " ".join(missing) + ": refusing")
        dirty = git("status", "--porcelain", "--", *paths).strip()
        if dirty:
            raise SystemExit("uncommitted changes: refusing\n" + dirty)
    files = {f"{REL}/{f}": sha(os.path.join(TOP, REL, f)) for f in NOTE4_BOX}
    return {"what": "E183's harness, v2 (make_harness_e183_v2.py, the kit's dated note 4): v1's harness file at its sha256, and note 4's "
                    "box files, each at its sha256; harness_e183_v2.py checks both, and runs v1's own check (check_e183.py) on v1's",
            "harness_v1": {"path": V1, "sha256": sha(os.path.join(TOP, V1))},
            "files": dict(sorted(files.items())),
            "counts": {"files": len(files)}}


def main():
    check = sys.argv[1:] == ["--check"]
    js = json.dumps(build(check), indent=1, sort_keys=True) + "\n"
    dst = os.path.join(HERE, "harness-e183-v2.json")
    if check:
        ok = os.path.exists(dst) and open(dst).read() == js
        print("CHECK PASS" if ok else "CHECK FAIL")
        sys.exit(0 if ok else 1)
    if sys.argv[1:]:
        print(__doc__)
        sys.exit(2)
    open(dst, "w").write(js)
    print(f"wrote {dst}: v1's harness file and {json.loads(js)['counts']['files']} box files of note 4")


if __name__ == "__main__":
    main()
