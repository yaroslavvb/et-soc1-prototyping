#!/usr/bin/env python3
"""E180 (Q146(f), the kit): write harness-e180.json, the sha256 of every file E180's box session runs, sources, builds from or
reads, after the kit is final (E180.md section 12, step 3). check_e180.py harness refuses on any difference from it, before any
device opens. The reused files are named with their commits' content: lib.sh must equal the one E171 and E178 run
(tools/claims-v3/e178/harness-e178.json), and the enercat tree the build copies is hashed file by file. Standard library only.

    python3 -B tools/claims-v3/e180/make_harness_e180.py            # writes harness-e180.json
    python3 -B tools/claims-v3/e180/make_harness_e180.py --check    # rebuilds it in memory and compares: CHECK PASS or FAIL
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "harness-e180.json")
E180 = ["run_e180.py", "block_e180.sh", "queue_e180.sh", "session_e180.sh", "check_e180.py", "preflight_e180.sh", "build_e180.sh",
        "gen_acc_e180.py", "acc-modes-e180.inc", "cfgs-e180.json", "plan-e180.json", "kinds-e180.json", "plan_e180.py", "E180.md",
        "SHA256SUMS-e180-registration"]
REUSED = ["tools/claims-v3/lib.sh", "tools/claims-v3/e128/ettelem_guard.sh", "tools/claims-v3/dmcmd_audit.py",
          "tools/claims-v3/dmcmd_table.json"]


def sha(p):
    return hashlib.sha256(open(os.path.join(TOP, p), "rb").read()).hexdigest()


def build():
    files = {}
    for f in E180:
        files[f"tools/claims-v3/e180/{f}"] = sha(f"tools/claims-v3/e180/{f}")
    for f in REUSED:
        files[f] = sha(f)
    for d, _s, fs in os.walk(os.path.join(TOP, "workloads", "enercat")):
        if "__pycache__" in d:
            continue
        for fn in sorted(fs):
            if fn.endswith(".pyc"):
                continue
            rel = os.path.relpath(os.path.join(d, fn), TOP)
            files[rel] = sha(rel)
    e178 = json.load(open(os.path.join(TOP, "tools/claims-v3/e178/harness-e178.json")))
    flat = {}

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if isinstance(v, str) and len(v) == 64 and k.endswith("lib.sh"):
                    flat[k] = v
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(e178)
    lib_e178 = flat.get("tools/claims-v3/lib.sh")
    return {"what": "E180's harness (make_harness_e180.py)", "files": dict(sorted(files.items())),
            "acc_modes_inc_sha256": files["tools/claims-v3/e180/acc-modes-e180.inc"],
            "lib_sh_equals_e178": lib_e178 == files["tools/claims-v3/lib.sh"], "lib_sh_e178": lib_e178}


def main():
    doc = build()
    if "--check" in sys.argv:
        have = json.load(open(OUT))
        print("CHECK PASS" if have == doc else "CHECK FAIL")
        sys.exit(0 if have == doc else 1)
    json.dump(doc, open(OUT, "w"), indent=1)
    print(f"harness-e180.json: {len(doc['files'])} files; lib.sh equals E178's: {doc['lib_sh_equals_e178']}")


if __name__ == "__main__":
    main()
