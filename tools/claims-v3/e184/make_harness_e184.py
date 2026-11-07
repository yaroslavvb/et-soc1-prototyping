#!/usr/bin/env python3
"""E184 (Q153, the kit): harness-e184.json, the sha256 of every file a box session of either arm runs, sources, builds from or reads.

    python3 -B tools/claims-v3/e184/make_harness_e184.py > tools/claims-v3/e184/harness-e184.json      (from the repository top)

E184's box files (both arms' blocks, the runner and the module it imports, the image maker and its frozen list, the plan and the inputs
the runner reads, the queue, the session, the checks, the preflight, the build and its patch script, arm B's telemetry guard, E184-T's
reader and the reducer pieces the box never runs are left out), lib.sh, E180's D1 test (sourced unchanged), E128's telemetry guard,
Q136(w)'s dmcmd_audit and its table, and every committed file of workloads/enercat the build copies; plus the patched host/main.cpp's
pinned sha256, which build_e184.sh records and check_e184.py harness --binaries compares.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import subprocess
import sys

E = "tools/claims-v3/e184/"
BOX = ["block_e184s.sh", "block_e184b.sh", "run_e184.py", "e184_common.py", "make_images_e184.py", "images-e184.sha256", "plan-e184.json",
       "inputs-e184.json", "queue_e184.sh", "session_e184s.sh", "session_e184b.sh", "check_e184.py", "preflight_e184.sh", "build_e184.sh", "host_patch_e184.py",
       "ettelem_guard_e184.sh"]
OTHER = ["tools/claims-v3/lib.sh", "tools/claims-v3/e180/others_d1_e180.sh", "tools/claims-v3/e128/ettelem_guard.sh",
         "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


files = [E + f for f in BOX] + OTHER
enercat = subprocess.run(["git", "ls-files", "workloads/enercat"], capture_output=True, text=True, check=True).stdout.split()
files += sorted(enercat)
sys.path.insert(0, E)
import host_patch_e184 as hp  # noqa: E402
out = {"what": "E184's harness (make_harness_e184.py): every file a box session runs, sources, builds from or reads",
       "files": {f: sha(f) for f in files}, "patched_main_sha256": hp.OUT_SHA256, "committed_main_sha256": hp.SRC_SHA256}
print(json.dumps(out, indent=1, sort_keys=True))
