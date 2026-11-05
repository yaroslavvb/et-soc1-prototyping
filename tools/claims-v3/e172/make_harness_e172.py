#!/usr/bin/env python3
"""E172 (Q142(k6)): write harness-e172.json, the sha256 of every file E172's box session runs, sources or reads, after the run kit is final
(E172.md, "The order of the freeze", step 3). check_e172.py, run_e172.py, reduce_e172.py and smoke_gate_e172.py refuse on any difference
from it. E78's card code, E128's guard, Q136(w)'s checker and table, the workload's host source and Q139(k)'s files must also equal E164's
registered values (tools/claims-v3/e164/harness-e164.json > card_code_unchanged_sha256), so the box runs the code E164 ran on this card; the four
box binaries are E164's pins (the same file's box_binaries_sha256, E157's). The watcher fix (watcher_q142s.py and its two amendments) is pinned, not
imported (E172.md, "The watcher"). Standard library only.

    python3 -B tools/claims-v3/e172/make_harness_e172.py
SPDX-License-Identifier: Apache-2.0
"""
import glob
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E172_FILES = ["e172_common.py", "run_e172.py", "block_e172.sh", "queue_e172.sh", "session_e172.sh", "check_e172.py",
              "preflight_e172.sh", "smoke_gate_e172.py", "reduce_e172.py", "box/launch_e172.sh"]
REGISTRATION = ["tools/claims-v3/e172/E172.md", "tools/claims-v3/e172/plan-e172.json"]
WATCHER = ["tools/claims-v3/hpl/watcher_q142s.py", "tools/claims-v3/hpl/run_hpl.py.dated-note.md", "tools/claims-v3/hpl/run_hpl.py.dated-note-2.md"]
POOL = ["tools/claims-v3/kinds/blind8/blind8.json", "tools/claims-v3/kinds/blind8/MANIFEST", "tools/claims-v3/kinds/blind8/SHA256SUMS",
        "tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry1c1.json", "tools/claims-v3/kinds/blind8/intervals-pool8.json"]


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def main():
    e164 = json.load(open(os.path.join(TOP, "tools/claims-v3/e164/harness-e164.json")))
    card = {rel: sha(rel) for rel in e164["card_code_unchanged_sha256"]}
    diff = [rel for rel, h in card.items() if h != e164["card_code_unchanged_sha256"][rel]]
    if diff:
        raise SystemExit(f"the reused card code differs from E164's registered values: {diff}")
    pool = {rel: sha(rel) for rel in POOL}
    for p in sorted(glob.glob(os.path.join(TOP, "tools/claims-v3/kinds/blind8/tiles/*/*.bin"))):
        pool[os.path.relpath(p, TOP)] = sha(os.path.relpath(p, TOP))
    man = {t["name"]: t for t in json.load(open(os.path.join(TOP, POOL[0])))["tiles"]}
    for n, t in man.items():
        rel = f"tools/claims-v3/kinds/blind8/{t['file']}"
        assert pool[rel] == t["sha256"]["whole"], rel
    assert len([k for k in pool if k.endswith(".bin")]) == 64
    h = {"_what": "E172 (Q142(k6)): the sha256 of every file E172's box session runs, sources or reads; written by make_harness_e172.py after "
                  "the run kit; check_e172.py, run_e172.py, reduce_e172.py and smoke_gate_e172.py refuse on any difference",
         "card_code_unchanged_sha256": card,
         "card_code_equals_e164": "every value equals tools/claims-v3/e164/harness-e164.json > card_code_unchanged_sha256",
         "e172_card_files_sha256": {f"tools/claims-v3/e172/{f}": sha(f"tools/claims-v3/e172/{f}") for f in E172_FILES},
         "registration_sha256": {rel: sha(rel) for rel in REGISTRATION},
         "watcher_sha256": {rel: sha(rel) for rel in WATCHER},
         "watcher_note": "pinned, not imported: E172's runner is run_e78.py through run_e172.py, which has no run_hpl Watcher (E172.md, 'The watcher')",
         "pool_sha256": pool,
         "box_binaries_sha256": e164["box_binaries_sha256"], "patched_main_cpp_sha256": e164.get("patched_main_cpp_sha256"),
         "box_binaries_note": "E164's four pins on aifoundry1 card 1 (~/nekko; E157's): E78's sparsity_host (the heater), the kernel every launch runs, "
                              "the patched C-logging host built by build_host_ccheck.sh, ettelem. If any differs on the box, nothing runs until a dated "
                              "amendment beside E172.md registers the new one"}
    json.dump(h, open(os.path.join(HERE, "harness-e172.json"), "w"), indent=1)
    n = sum(len(h[k]) for k in ("card_code_unchanged_sha256", "e172_card_files_sha256", "registration_sha256", "watcher_sha256", "pool_sha256",
                                "box_binaries_sha256"))
    print(f"wrote tools/claims-v3/e172/harness-e172.json: {n} files ({len(pool)} pool files and tiles, {len(WATCHER)} watcher files, 4 box binaries)")


if __name__ == "__main__":
    main()
