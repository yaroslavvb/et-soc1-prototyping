#!/usr/bin/env python3
"""E173 (Q142(kg)): writes harness-e173.json, the sha256 of every file E173's session runs, imports or reads on aifoundry2 and every file its
desk scorer reads, from the Intel's committed tree; check_e173.py compares a tree against it (on the box with the three pinned binaries) before
any device opens, and the collector checks the desk's tree against it before anything is scored. No card. E170's form.

    python3 -B tools/claims-v3/e173/make_harness_e173.py
SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e173_common as C  # noqa: E402

TOP = C.TOP
E = "tools/claims-v3/e173"
KIT = [f"{E}/{x}" for x in ("E173.md", "e173_common.py", "make_predictions_e173.py", "predictions-e173.json", "frozen-sha256-e173.json",
                            "make_protocol_e173.py", "run_e173.py", "queue_e173.py", "check_e173.py", "make_harness_e173.py", "preflight_e173.sh",
                            "score_e173.py", "p8gov.py", "collect_e173_bounded.sh", "protocol.json", "protocol-subset.json", "protocol-dry.json",
                            "protocol-stoptest-board.json", "protocol-stoptest-die.json", "protocol-stoptest-board-dry.json", "protocol-stoptest-die-dry.json")]
CHAIN = ["tools/claims-v3/e119/run_e119.py", "tools/claims-v3/e119/predictions-e119.json", "tools/claims-v3/kspeed/e105/run_e105.py",
         "tools/claims-v3/kspeed/e101/run_e101s.py", "tools/claims-v3/kinds/e101_common.py", "tools/claims-v3/kinds/e78_common.py",
         "tools/claims-v3/kspeed/run_kspeed.py", "tools/claims-v3/kspeed/predictions.json", "tools/claims-v3/e111/idle_logins_e111.py",
         "tools/claims-v3/hpl/run_hpl.py", "tools/claims-v3/hpl/watcher_q142s.py", "tools/claims-v3/e165/e165_common.py", "tools/claims-v3/e165/score_e165.py",
         "tools/claims-v3/hpl/reduce_hpl.py", "tools/claims-v3/hpl/sptrace_full.py", "tools/claims-v3/dv2/sptrace_events.py",
         "tools/claims-v3/kspeed/reduce_kspeed.py", "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json", "tools/claims-v3/kinds/kinds.json",
         "tools/claims-v3/kinds/tiles/fp16/randn.bin", "tools/claims-v3/kinds/tiles/int8/full.bin", "workloads/sparsity/host/main.cpp",
         "workloads/sparsity/kernel/sparsity.c", "tools/claims-v3/q141k-runbook/v3.1/ccdone_q142s.py", "tools/claims-v3/q141k-runbook/v3.1/nopath_q142s.py"]


def main():
    tiles = sorted(os.path.relpath(p, TOP) for p in glob.glob(os.path.join(TOP, C.POOL_REL, "tiles", "*", "*.bin")))
    files = KIT + CHAIN + sorted(C.CCHECK_FROZEN) + sorted(C.frozen()) + tiles
    seen, out = set(), {}
    for rel in files:
        if rel in seen:
            continue
        seen.add(rel)
        p = os.path.join(TOP, rel)
        if not os.path.isfile(p):
            raise SystemExit(f"refused: {rel} is missing")
        out[rel] = C.sha256_file(p)
    doc = {"_note": "E173's harness: the sha256 of every file the session runs, imports or reads on aifoundry2 and every file the desk scorer reads, "
                    "from the Intel's committed tree; check_e173.py compares a tree against it (and, on the box, the binaries against box_binaries_sha256)",
           "files_sha256": out, "box_binaries_sha256": {C.CC_HOST_REL: C.CC_HOST_SHA256, **C.E80_SHA256}, "n_files": len(out)}
    with open(os.path.join(HERE, "harness-e173.json"), "w") as f:
        json.dump(doc, f, indent=1, sort_keys=True)
    print(f"harness-e173.json: {len(out)} files ({len(tiles)} pool tiles), {len(doc['box_binaries_sha256'])} binaries")


if __name__ == "__main__":
    main()
