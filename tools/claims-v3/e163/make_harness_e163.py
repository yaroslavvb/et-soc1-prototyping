#!/usr/bin/env python3
"""E163 (Q141): write harness-e163.json, the sha256 of every file E163's box session runs, sources or reads, after the run kit is final
(E163.md, "The order of the freeze", step 3). check_e163.py, run_e163.py, reduce_e163.py and smoke_gate_e163.py refuse on any
difference from it. E78's card code, E128's guard, Q136(w)'s checker and table, the workload's host source and Q139(k)'s five files must
also equal E153's registered values (tools/claims-v3/e153/predictions-e153.json > harness), so the box runs the code E153 ran; the four
box binaries are E153's (the same file's box_binaries_sha256). Standard library only.

    python3 -B tools/claims-v3/e163/make_harness_e163.py
SPDX-License-Identifier: Apache-2.0
"""
import glob
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CARD_CODE = ["tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
             "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json", "tools/claims-v3/e128/ettelem_guard.sh",
             "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json", "workloads/sparsity/host/main.cpp",
             "tools/claims-v3/ccheck/sparsity_ccheck.sh", "tools/claims-v3/ccheck/patch_host_ccheck.py",
             "tools/claims-v3/ccheck/build_host_ccheck.sh", "tools/claims-v3/ccheck/ccheck.py", "tools/claims-v3/ccheck/pick6.py"]
E163_FILES = ["e163_common.py", "run_e163.py", "block_e163.sh", "queue_e163.sh", "session_e163.sh", "check_e163.py",
              "preflight_e163.sh", "smoke_gate_e163.py", "reduce_e163.py"]
REGISTRATION = ["tools/claims-v3/e163/E163.md", "tools/claims-v3/e163/predictions-e163.json", "tools/claims-v3/e163/rerun-ref.json"]
REUSED_E151 = ["tools/claims-v3/e151/railfilter_e151.py", "tools/claims-v3/e151/e130-items.json", "tools/claims-v3/kinds/e130/e130.json"]


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def main():
    e153 = json.load(open(os.path.join(ROOT, "tools/claims-v3/e153/predictions-e153.json")))["harness"]
    card = {rel: sha(rel) for rel in CARD_CODE}
    diff = [rel for rel in CARD_CODE if card[rel] != e153["card_code_unchanged_sha256"].get(rel)]
    if diff:
        raise SystemExit(f"the reused card code differs from E153's registered values: {diff}")
    rr = json.load(open(os.path.join(HERE, "rerun-ref.json")))
    pool = {rel: sha(rel) for rel in ("tools/claims-v3/kinds/blind7/blind7.json", "tools/claims-v3/kinds/blind7/MANIFEST",
                                      "tools/claims-v3/kinds/blind7/SHA256SUMS",
                                      "tools/claims-v3/kinds/blind7/predictions-blind7-aifoundry3.json",
                                      "tools/claims-v3/kinds/blind5/blind5.json", "tools/claims-v3/e152/e152-tiles.json")}
    for p in sorted(glob.glob(os.path.join(ROOT, "tools/claims-v3/kinds/blind7/tiles/*/*.bin"))):
        pool[os.path.relpath(p, ROOT)] = sha(os.path.relpath(p, ROOT))
    for src in ("pool5", "e152"):
        for t, x in rr[src]["tiles"].items():
            have = sha(x["file"])
            assert have == x["sha256"], (t, have, x["sha256"])
            pool[x["file"]] = have
    for t in json.load(open(os.path.join(ROOT, "tools/claims-v3/e151/e130-items.json")))["tiles"]:
        rel = f"tools/claims-v3/kinds/e130/{t['file']}"
        assert sha(rel) == t["sha256"], rel
        pool[rel] = sha(rel)
    assert len([k for k in pool if k.endswith(".bin")]) == 61 + 16 + 26
    h = {"_what": "E163 (Q141): the sha256 of every file E163's box session runs, sources or reads; written by make_harness_e163.py "
                  "after the run kit; check_e163.py, run_e163.py, reduce_e163.py and smoke_gate_e163.py refuse on any difference",
         "card_code_unchanged_sha256": card,
         "card_code_equals_e153": "every value equals tools/claims-v3/e153/predictions-e153.json > harness.card_code_unchanged_sha256",
         "e163_card_files_sha256": {f"tools/claims-v3/e163/{f}": sha(f"tools/claims-v3/e163/{f}") for f in E163_FILES},
         "registration_sha256": {rel: sha(rel) for rel in REGISTRATION},
         "reused_e151_sha256": {rel: sha(rel) for rel in REUSED_E151},
         "pool_sha256": pool,
         "box_binaries_sha256": e153["box_binaries_sha256"],
         "box_binaries_note": "E153's four, read on aifoundry3 (~/aifoundry) at 06:40 PST on Tue 3 Nov 2026: E78's sparsity_host (the "
                              "heater), the kernel every launch runs, the C-logging host built by build_host_ccheck.sh, ettelem. If any "
                              "differs on the box, nothing runs until a dated amendment beside E163.md registers the new one"}
    json.dump(h, open(os.path.join(HERE, "harness-e163.json"), "w"), indent=1)
    n = sum(len(h[k]) for k in ("card_code_unchanged_sha256", "e163_card_files_sha256", "registration_sha256", "reused_e151_sha256",
                                "pool_sha256", "box_binaries_sha256"))
    print(f"wrote tools/claims-v3/e163/harness-e163.json: {n} files ({len(pool)} pool files and tiles, 4 box binaries)")


if __name__ == "__main__":
    main()
