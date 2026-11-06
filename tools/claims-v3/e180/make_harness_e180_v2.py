#!/usr/bin/env python3
"""E180 (Q146(f); the kit's dated note 1, KIT.md.dated-note-1.md section 4), v2: write harness-e180-v2.json, the sha256 of every file E180's
v2 box session runs, sources, builds from or reads. make_harness_e180.py (v1, which stays as committed, with harness-e180.json) with the v2
file set: v1's block, runner, queue, session, check and preflight are replaced by block_e180_v2.sh, run_e180_v2.py, queue_e180_v2.sh,
session_e180_v2.sh, check_e180_v2.py (which imports v1's check_e180.py, so that stays in) and preflight_e180_v2.sh; others_d1_e180.sh (D1's
test, which the block and the runner source) and check_elf_e180.py (the build step's disassembly walk) are added; the registration's dated
note A1 and its hash list ride along as v1's E180.md and its list do. The reused files are v1's: lib.sh (it must equal the one E171 and E178
run), E128's guard, the checker and its table, and the committed workloads/enercat tree, file by file. check_e180_v2.py harness refuses on
any difference from it, before any device opens. Standard library only.

    python3 -B tools/claims-v3/e180/make_harness_e180_v2.py            # writes harness-e180-v2.json
    python3 -B tools/claims-v3/e180/make_harness_e180_v2.py --check    # rebuilds it in memory and compares: CHECK PASS or FAIL
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_harness_e180 as m1  # noqa: E402  (v1's sha, REUSED and its lib.sh check, unchanged)

OUT = os.path.join(HERE, "harness-e180-v2.json")
E180_V2 = ["run_e180_v2.py", "block_e180_v2.sh", "others_d1_e180.sh", "queue_e180_v2.sh", "session_e180_v2.sh", "check_e180_v2.py",
           "check_e180.py", "preflight_e180_v2.sh", "check_elf_e180.py", "build_e180.sh", "gen_acc_e180.py", "acc-modes-e180.inc",
           "cfgs-e180.json", "plan-e180.json", "kinds-e180.json", "plan_e180.py", "E180.md", "SHA256SUMS-e180-registration",
           "E180.md.dated-note-A1.md", "SHA256SUMS-e180-a1"]


def build():
    v1 = m1.build()
    files = {f"tools/claims-v3/e180/{f}": m1.sha(f"tools/claims-v3/e180/{f}") for f in E180_V2}
    for k, v in v1["files"].items():
        if not k.startswith("tools/claims-v3/e180/"):
            files[k] = v                      # REUSED and the workloads/enercat tree, exactly as v1 hashes them
    return {"what": "E180's harness, v2 (make_harness_e180_v2.py; the kit's dated note 1)", "files": dict(sorted(files.items())),
            "acc_modes_inc_sha256": files["tools/claims-v3/e180/acc-modes-e180.inc"],
            "lib_sh_equals_e178": v1["lib_sh_equals_e178"], "lib_sh_e178": v1["lib_sh_e178"],
            "v1_files_replaced": sorted(set(v1["files"]) - set(files))}


def main():
    doc = build()
    if "--check" in sys.argv:
        have = json.load(open(OUT))
        print("CHECK PASS" if have == doc else "CHECK FAIL")
        sys.exit(0 if have == doc else 1)
    json.dump(doc, open(OUT, "w"), indent=1)
    print(f"harness-e180-v2.json: {len(doc['files'])} files; lib.sh equals E178's: {doc['lib_sh_equals_e178']}; "
          f"v1 files replaced: {', '.join(p.split('/')[-1] for p in doc['v1_files_replaced'])}")


if __name__ == "__main__":
    main()
