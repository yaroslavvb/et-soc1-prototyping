#!/usr/bin/env python3
"""E174 (Q142(kg)): writes harness-e174.json, the sha256 of every file E174's session runs, imports or reads on aifoundry1 (its ~/nekko tree is an
rsynced copy with no git), from the Intel's committed tree; check_e174.py compares the box against it (with the three pinned binaries) before any
device opens. No card. E170's make_harness_e170.py with E174's list.

    python3 -B tools/claims-v3/e174/make_harness_e174.py
SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e174_common as C  # noqa: E402

TOP = C.TOP
E = "tools/claims-v3/e174"
CODE = [f"{E}/run_e174.py", f"{E}/queue_e174.py", f"{E}/e174_common.py", f"{E}/check_e174.py", f"{E}/preflight_e174.sh", f"{E}/frozen-sha256-e174.json",
        "tools/claims-v3/e173/e173_common.py", "tools/claims-v3/e173/frozen-sha256-e173.json", "tools/claims-v3/e170/e170_common.py", C.GUARD_REL,
        "tools/claims-v3/kspeed/e84/run_e84.py", "tools/claims-v3/kspeed/run_kspeed.py", "tools/claims-v3/kspeed/predictions.json",
        "tools/claims-v3/kspeed/e101/run_e101s.py", "tools/claims-v3/kinds/e101_common.py", "tools/claims-v3/kinds/e78_common.py",
        "tools/claims-v3/kspeed/e105/run_e105.py", "tools/claims-v3/e119/run_e119.py", "tools/claims-v3/e119/predictions-e119.json",
        "tools/claims-v3/e111/idle_logins_e111.py", "tools/claims-v3/hpl/run_hpl.py", "tools/claims-v3/hpl/watcher_q142s.py", "tools/claims-v3/e165/e165_common.py",
        "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json", "workloads/sparsity/host/main.cpp", "workloads/sparsity/kernel/sparsity.c",
        "tools/claims-v3/kinds/kinds.json"]
DATA = [f"{E}/predictions-e174.json", f"{E}/protocol.json", f"{E}/protocol-subset.json", f"{E}/protocol-dry.json", f"{E}/protocol-stoptest-board.json",
        f"{E}/protocol-stoptest-die.json", f"{E}/protocol-stoptest-board-dry.json", f"{E}/protocol-stoptest-die-dry.json"]
BOX = [f"{E}/box/look_e174.sh", f"{E}/box/check_box_e174.sh", f"{E}/box/launch_e174.sh", f"{E}/box/wait_e174.sh"]


def main():
    pool = [f"{C.POOL_REL}/{x}" for x in ("blind8.json", "MANIFEST", "SHA256SUMS")]
    pool += sorted(os.path.relpath(p, TOP) for p in glob.glob(os.path.join(TOP, C.POOL_REL, "tiles", "*", "*.bin")))
    files = CODE + DATA + BOX + sorted(C.CCHECK_FROZEN) + pool
    seen, out = set(), {}
    for rel in files:
        if rel in seen:
            continue
        seen.add(rel)
        p = os.path.join(TOP, rel)
        if not os.path.isfile(p):
            raise SystemExit(f"refused: {rel} is missing")
        out[rel] = C.sha256_file(p)
    doc = {"_note": "E174's harness: the sha256 of every file the session runs, imports or reads on aifoundry1, from the Intel's committed tree; "
                    "check_e174.py compares the box against it (and the binaries against box_binaries_sha256) before any device opens",
           "files_sha256": out, "box_binaries_sha256": C.BOX_BINARIES, "n_files": len(out)}
    with open(os.path.join(HERE, "harness-e174.json"), "w") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
    print(f"harness-e174.json: {len(out)} files, {len(C.BOX_BINARIES)} binaries")


if __name__ == "__main__":
    main()
