#!/usr/bin/env python3
"""E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): harness-e183-v3.json, the pins of
note 6's box files and of note 4's harness file and check, which harness_e183_v3.py reads on the box and at the desk.

    /usr/bin/python3 -B tools/claims-v3/e183/make_harness_e183_v3.py           # writes harness-e183-v3.json beside this file
    /usr/bin/python3 -B tools/claims-v3/e183/make_harness_e183_v3.py --check   # re-makes it in memory and compares: CHECK PASS or exit 1

  harness_v2       tools/claims-v3/e183/harness-e183-v2.json (24b9b99e) and its sha256: v1's harness file's pin and note 4's 7 box files;
  harness_v2_code  tools/claims-v3/e183/harness_e183_v2.py (24b9b99e) and its sha256: v2's check, which harness_e183_v3.py runs unchanged;
  files            note 6's five box files: block_e183_v3.sh, queue_e183_v3.sh, session_e183_v3.sh, preflight_e183_v3.sh and
                   harness_e183_v3.py, each at its sha256.
Step 5 (rb/s07_a3_sync_e183.sh, unchanged) syncs E183's whole directory, so it carries these files and every harness file to the box.
With --check it refuses unless every file it pins is committed and clean (git), so the pins it passes are the committed bytes; it writes
the file from the files as they stand (note 6's commit holds the files and this file together). Standard library only.
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
V2 = f"{REL}/harness-e183-v2.json"
V2_CODE = f"{REL}/harness_e183_v2.py"
NOTE6_BOX = ["block_e183_v3.sh", "queue_e183_v3.sh", "session_e183_v3.sh", "preflight_e183_v3.sh", "harness_e183_v3.py"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", TOP] + list(a), capture_output=True, text=True, check=True).stdout


def build(committed):
    paths = [V2, V2_CODE] + [f"{REL}/{f}" for f in NOTE6_BOX]
    if committed:
        tracked = set(git("ls-files", "--", *paths).splitlines())
        missing = [p for p in paths if p not in tracked]
        if missing:
            raise SystemExit("not committed: " + " ".join(missing) + ": refusing")
        dirty = git("status", "--porcelain", "--", *paths).strip()
        if dirty:
            raise SystemExit("uncommitted changes: refusing\n" + dirty)
    files = {f"{REL}/{f}": sha(os.path.join(TOP, REL, f)) for f in NOTE6_BOX}
    return {"what": "E183's harness, v3 (make_harness_e183_v3.py, the kit's dated note 6): note 4's harness file and check at their sha256, "
                    "and note 6's box files, each at its sha256; harness_e183_v3.py checks them, and runs note 4's check (harness_e183_v2.py) "
                    "unchanged",
            "harness_v2": {"path": V2, "sha256": sha(os.path.join(TOP, V2))},
            "harness_v2_code": {"path": V2_CODE, "sha256": sha(os.path.join(TOP, V2_CODE))},
            "files": dict(sorted(files.items())),
            "counts": {"files": len(files)}}


def main():
    check = sys.argv[1:] == ["--check"]
    js = json.dumps(build(check), indent=1, sort_keys=True) + "\n"
    dst = os.path.join(HERE, "harness-e183-v3.json")
    if check:
        ok = os.path.exists(dst) and open(dst).read() == js
        print("CHECK PASS" if ok else "CHECK FAIL")
        sys.exit(0 if ok else 1)
    if sys.argv[1:]:
        print(__doc__)
        sys.exit(2)
    open(dst, "w").write(js)
    print(f"wrote {dst}: note 4's harness file and check, and {json.loads(js)['counts']['files']} box files of note 6")


if __name__ == "__main__":
    main()
