#!/usr/bin/env python3
"""E180 (Q146(f); the kit's dated note 1, KIT.md.dated-note-1.md section 4): the path list of the runbook's step 7 v2
(rb/s07_a3_sync_e180_v2.sh), read from the harness itself, so that what step 8 checks on the box (check_e180_v2.py harness) and what step 7
copies there agree by construction (the adversarial verifier's fault 8, the E174 class: v1's sync copied E180's directory and
workloads/enercat only, while the harness also names lib.sh, E128's guard, dmcmd_audit.py and its table). tools/claims-v3/e178/
sync_paths_e178.py's form; E180's harness names no box binary (build_e180.sh records them in build/enercat-e180/BUILD-E180.json on the
box, never synced).

It prints, one per line, "SYNC <path>": first the paths given (rb_e180.sh's E180_PATHS, as v1 synced them), then every file
harness-e180-v2.json names that none of them covers, in the harness's own order. Then "COVER <harness files> <covered by the paths given>
<added> <synced in all>". A path given covers a harness file when it equals it, or is a directory (ending in "/") that holds it. It refuses
(exit 3, nothing printed but the reason) when a path given or a harness file is not a file or directory of this tree (run it from the
repository's root), or when a harness file lies under build/. Standard library only; it reads two things and writes nothing.

    python3 -B tools/claims-v3/e180/sync_paths_e180.py tools/claims-v3/e180/harness-e180-v2.json <path> ...
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys


def main(argv):
    if len(argv) < 2:
        print("usage: sync_paths_e180.py <harness json> <path> ...")
        return 2
    h = json.load(open(argv[0]))
    given = argv[1:]
    files = list(h["files"])
    bad = [f"a path given is not in this tree: {p}" for p in given if not (os.path.isfile(p) or (p.endswith("/") and os.path.isdir(p)))]
    bad += [f"a harness file is under build/ (built on the box, never synced): {p}" for p in files if p.startswith("build/")]

    def covered(p):
        return any(p == q or (q.endswith("/") and p.startswith(q)) for q in given)

    n_cov = sum(1 for p in files if covered(p))
    extra = [p for p in files if not covered(p)]
    bad += [f"a harness file to sync is not in this tree: {p}" for p in extra if not os.path.isfile(p)]
    if bad:
        print("REFUSED: " + "; ".join(bad))
        return 3
    for p in given + extra:
        print("SYNC " + p)
    print(f"COVER {len(files)} {n_cov} {len(extra)} {n_cov + len(extra)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
