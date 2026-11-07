#!/usr/bin/env python3
"""E182 (Q153, the kit; a copy of tools/claims-v3/e178/sync_paths_e178.py with one change): the path list of the runbook's step 7
(rb/s07_a3_sync_e182.sh), read from the harness itself, so that what step 8 checks on the box (HARNESS OK with the binaries and the train host) and what step 7
copies there agree by construction (the kit verifier's fault 1, the E174 class: the day critic's kit v4 item "gate and sync must agree").

It prints, one per line, "SYNC <path>": first the paths given (rb_e182.sh's E182_PATHS, as v1 synced them), then every file harness-e182.json
names that none of them covers, in the harness's own order; only the harness's box binaries (box_binaries_sha256, every one under build/:
built on the box, never synced) are left out. Then "COVER <harness files> <binaries> <covered by the paths given> <added> <synced in all>".
A path given covers a harness file when it equals it, or is a directory (ending in "/") that holds it.
It refuses (exit 3, nothing printed but the reason) when a path given or a harness file to sync is not a file or directory of this tree
(run it from the repository's root), or a box binary is not under build/. Standard library only; it reads two things and writes nothing.

    python3 -B tools/claims-v3/e182/sync_paths_e182.py tools/claims-v3/e182/harness-e182.json <path> ...
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

BINARIES = "box_binaries_sha256"
BUILT_ON_BOX = ("box_binaries_sha256", "train_host_source_sha256")   # E182: the train host's patched source is made on the box by its build


def main(argv):
    if len(argv) < 2:
        print("usage: sync_paths_e182.py <harness json> <path> ...")
        return 2
    h = json.load(open(argv[0]))
    given = argv[1:]
    files = [p for k, v in h.items() if isinstance(v, dict) and k not in BUILT_ON_BOX for p in v]
    bins = [p for k in BUILT_ON_BOX for p in h.get(k, {})]
    bad = [f"a path given is not in this tree: {p}" for p in given if not (os.path.isfile(p) or (p.endswith("/") and os.path.isdir(p)))]
    bad += [f"a box binary is not under build/: {p}" for p in bins if not p.startswith("build/")]

    def covered(p):
        return any(p == q or (q.endswith("/") and p.startswith(q)) for q in given)

    n_cov = sum(1 for p in files if covered(p))
    extra = []
    for p in files:
        if not covered(p) and p not in extra:
            extra.append(p)
    bad += [f"a harness file to sync is not in this tree: {p}" for p in extra if not os.path.isfile(p)]
    if bad:
        print("REFUSED: " + "; ".join(bad))
        return 3
    for p in given + extra:
        print("SYNC " + p)
    print(f"COVER {len(files)} {len(bins)} {n_cov} {len(extra)} {n_cov + len(extra)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
