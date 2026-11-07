#!/usr/bin/env python3
"""E184 (Q153), kit v2 (KIT.md.dated-note-1.md section 4): harness-e184-v2.json, the sha256 of every file a kit-v2 box session of either arm
runs, sources, builds from or reads. make_harness_e184.py's form (v1, which stays as committed) with kit v2's box files in place of v1's.

    python3 -B tools/claims-v3/e184/make_harness_e184_v2.py > tools/claims-v3/e184/harness-e184-v2.json      (from the repository top)
    python3 -B tools/claims-v3/e184/make_harness_e184_v2.py --check      ("CHECK PASS" if the committed file is what this makes)

Kit v2's box files: both arms' v2 blocks and sessions, the v2 queue, the v2 runner and the module it imports, the image maker and its frozen
list, the plan and the inputs the runner reads, the v2 checks and the v1 checks they import, the v2 preflight, the build and its patch
script, arm B's telemetry guard; then lib.sh, E180's D1 test (sourced unchanged), E128's telemetry guard, Q136(w)'s dmcmd_audit and its
table, and every committed file of workloads/enercat the build copies; plus the patched host/main.cpp's pinned sha256 (build_e184.sh records
it, check_e184_v2.py harness --binaries compares it). The reducer, the scorer and the readers never run on a box and are left out.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import subprocess
import sys

E = "tools/claims-v3/e184/"
BOX = ["block_e184s_v2.sh", "block_e184b_v2.sh", "run_e184_v2.py", "e184_common.py", "make_images_e184.py", "images-e184.sha256",
       "plan-e184.json", "inputs-e184.json", "queue_e184_v2.sh", "session_e184s_v2.sh", "session_e184b_v2.sh", "check_e184_v2.py",
       "check_e184.py", "preflight_e184_v2.sh", "build_e184.sh", "host_patch_e184.py", "ettelem_guard_e184.sh"]
OTHER = ["tools/claims-v3/lib.sh", "tools/claims-v3/e180/others_d1_e180.sh", "tools/claims-v3/e128/ettelem_guard.sh",
         "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def make():
    files = [E + f for f in BOX] + OTHER
    enercat = subprocess.run(["git", "ls-files", "workloads/enercat"], capture_output=True, text=True, check=True).stdout.split()
    files += sorted(enercat)
    sys.path.insert(0, E)
    import host_patch_e184 as hp  # noqa: E402
    out = {"what": "E184's kit-v2 harness (make_harness_e184_v2.py): every file a kit-v2 box session runs, sources, builds from or reads",
           "files": {f: sha(f) for f in files}, "patched_main_sha256": hp.OUT_SHA256, "committed_main_sha256": hp.SRC_SHA256}
    return json.dumps(out, indent=1, sort_keys=True) + "\n"


if __name__ == "__main__":
    text = make()
    if "--check" in sys.argv:
        ok = open(E + "harness-e184-v2.json").read() == text
        print("CHECK PASS" if ok else "CHECK FAIL: harness-e184-v2.json is not what make_harness_e184_v2.py makes")
        sys.exit(0 if ok else 1)
    sys.stdout.write(text)
