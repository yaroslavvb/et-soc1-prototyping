#!/usr/bin/env python3
"""E170 (Q141(w)): writes harness-e170.json, the sha256 of every file E170's session runs, imports or reads on aifoundry1 (its ~/nekko tree is an
rsynced copy with no git), from the Intel's committed tree; check_e170.py compares the box against it before any device opens. The binaries are
pinned in e170_common.BOX_BINARIES and checked there too. No card.

    python3 -B tools/claims-v3/e170/make_harness_e170.py
SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e170_common as C  # noqa: E402

ROOT = C.ROOT
E = "tools/claims-v3/e170"
# what the session imports (the import trace of run_e170.py and queue_e170.py, Wed 4 Nov 2026) and the files it reads
CODE = [f"{E}/run_e170.py", f"{E}/queue_e170.py", f"{E}/e170_common.py", f"{E}/ettelem_guard_e170.sh", f"{E}/preflight_e170.sh", f"{E}/check_e170.py",
        "tools/claims-v3/kspeed/e84/run_e84.py", "tools/claims-v3/kspeed/run_kspeed.py", "tools/claims-v3/kspeed/predictions.json",
        "tools/claims-v3/kspeed/e101/run_e101s.py", "tools/claims-v3/kinds/e101_common.py", "tools/claims-v3/kinds/e78_common.py",
        "tools/claims-v3/kspeed/e105/run_e105.py", "tools/claims-v3/e119/run_e119.py", "tools/claims-v3/e119/predictions-e119.json",
        "tools/claims-v3/e111/idle_logins_e111.py", "tools/claims-v3/hpl/run_hpl.py", "tools/claims-v3/e165/e165_common.py",
        "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json", "workloads/sparsity/host/main.cpp", "workloads/sparsity/kernel/sparsity.c",
        "tools/claims-v3/kinds/kinds.json"]
DATA = [f"{E}/predictions-e170.json", f"{E}/protocol.json", f"{E}/protocol-subset.json", f"{E}/protocol-dry.json",
        f"{E}/protocol-stoptest-board.json", f"{E}/protocol-stoptest-die.json", f"{E}/protocol-stoptest-board-dry.json", f"{E}/protocol-stoptest-die-dry.json"]
BOX = [f"{E}/box/look_e170.sh", f"{E}/box/check_box_e170.sh", f"{E}/box/launch_e170.sh", f"{E}/box/wait_e170.sh"]


def pool_files():
    fs = [f"{C.POOL_REL}/{x}" for x in ("blind7.json", "MANIFEST", "SHA256SUMS", "predictions-blind7-aifoundry2.json", "a2-inputs-aifoundry2.json",
                                         "admission-aifoundry2-82w.json")]
    fs += sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, C.POOL_REL, "tiles", "*", "*.bin")))
    return fs


def main():
    files = CODE + DATA + BOX + sorted(C.CCHECK_FROZEN) + sorted(k for k in C.FROZEN if not k.startswith(C.POOL_REL)) + pool_files()
    seen, out = set(), {}
    for rel in files:
        if rel in seen:
            continue
        seen.add(rel)
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p):
            raise SystemExit(f"refused: {rel} is missing")
        out[rel] = C.sha256_file(p)
    doc = {"_note": "E170's harness: the sha256 of every file the session runs, imports or reads on aifoundry1, from the Intel's committed tree; "
                    "check_e170.py compares the box against it (and the binaries against box_binaries_sha256) before any device opens",
           "files_sha256": out, "box_binaries_sha256": C.BOX_BINARIES, "n_files": len(out)}
    json.dump(doc, open(os.path.join(HERE, "harness-e170.json"), "w"), indent=1, sort_keys=True)
    print(f"harness-e170.json: {len(out)} files, {len(C.BOX_BINARIES)} binaries")


if __name__ == "__main__":
    main()
