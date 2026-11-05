#!/usr/bin/env python3
"""E171 (Q142(k6)): write harness-e171.json, the sha256 of every file E171's box session runs, sources or reads, after the run kit is final
(E171.md, "The order of the freeze", step 3). check_e171.py, run_e171.py, reduce_e171.py and smoke_gate_e171.py refuse on any difference
from it. E78's card code, E128's guard, Q136(w)'s checker and table, the workload's host source and Q139(k)'s files must also equal E163's
registered values (tools/claims-v3/e163/harness-e163.json > card_code_unchanged_sha256), so the box runs the code E163 ran; the four box
binaries are E163's (the same file's box_binaries_sha256, E153's). The watcher fix (watcher_q142s.py and its two amendments) is pinned, not
imported (E171.md, "The watcher"). Standard library only.

    python3 -B tools/claims-v3/e171/make_harness_e171.py
SPDX-License-Identifier: Apache-2.0
"""
import glob
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E171_FILES = ["e171_common.py", "run_e171.py", "block_e171.sh", "queue_e171.sh", "session_e171.sh", "check_e171.py",
              "preflight_e171.sh", "smoke_gate_e171.py", "reduce_e171.py"]
REGISTRATION = ["tools/claims-v3/e171/E171.md", "tools/claims-v3/e171/plan-e171.json"]
WATCHER = ["tools/claims-v3/hpl/watcher_q142s.py", "tools/claims-v3/hpl/run_hpl.py.dated-note.md", "tools/claims-v3/hpl/run_hpl.py.dated-note-2.md"]
POOL = ["tools/claims-v3/kinds/blind8/blind8.json", "tools/claims-v3/kinds/blind8/MANIFEST", "tools/claims-v3/kinds/blind8/SHA256SUMS",
        "tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry3.json", "tools/claims-v3/kinds/blind8/intervals-pool8.json"]


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def main():
    e163 = json.load(open(os.path.join(TOP, "tools/claims-v3/e163/harness-e163.json")))
    card = {rel: sha(rel) for rel in e163["card_code_unchanged_sha256"]}
    diff = [rel for rel, h in card.items() if h != e163["card_code_unchanged_sha256"][rel]]
    if diff:
        raise SystemExit(f"the reused card code differs from E163's registered values: {diff}")
    pool = {rel: sha(rel) for rel in POOL}
    for p in sorted(glob.glob(os.path.join(TOP, "tools/claims-v3/kinds/blind8/tiles/*/*.bin"))):
        pool[os.path.relpath(p, TOP)] = sha(os.path.relpath(p, TOP))
    man = {t["name"]: t for t in json.load(open(os.path.join(TOP, POOL[0])))["tiles"]}
    for n, t in man.items():
        rel = f"tools/claims-v3/kinds/blind8/{t['file']}"
        assert pool[rel] == t["sha256"]["whole"], rel
    assert len([k for k in pool if k.endswith(".bin")]) == 64
    h = {"_what": "E171 (Q142(k6)): the sha256 of every file E171's box session runs, sources or reads; written by make_harness_e171.py after "
                  "the run kit; check_e171.py, run_e171.py, reduce_e171.py and smoke_gate_e171.py refuse on any difference",
         "card_code_unchanged_sha256": card,
         "card_code_equals_e163": "every value equals tools/claims-v3/e163/harness-e163.json > card_code_unchanged_sha256",
         "e171_card_files_sha256": {f"tools/claims-v3/e171/{f}": sha(f"tools/claims-v3/e171/{f}") for f in E171_FILES},
         "registration_sha256": {rel: sha(rel) for rel in REGISTRATION},
         "watcher_sha256": {rel: sha(rel) for rel in WATCHER},
         "watcher_note": "pinned, not imported: E171's runner is run_e78.py through run_e171.py, which has no run_hpl Watcher (E171.md, 'The watcher')",
         "pool_sha256": pool,
         "box_binaries_sha256": e163["box_binaries_sha256"],
         "box_binaries_note": "E163's four (E153's), read on aifoundry3 (~/aifoundry): E78's sparsity_host (the heater), the kernel every launch runs, "
                              "the C-logging host built by build_host_ccheck.sh, ettelem. If any differs on the box, nothing runs until a dated "
                              "amendment beside E171.md registers the new one"}
    json.dump(h, open(os.path.join(HERE, "harness-e171.json"), "w"), indent=1)
    n = sum(len(h[k]) for k in ("card_code_unchanged_sha256", "e171_card_files_sha256", "registration_sha256", "watcher_sha256", "pool_sha256",
                                "box_binaries_sha256"))
    print(f"wrote tools/claims-v3/e171/harness-e171.json: {n} files ({len(pool)} pool files and tiles, {len(WATCHER)} watcher files, 4 box binaries)")


if __name__ == "__main__":
    main()
