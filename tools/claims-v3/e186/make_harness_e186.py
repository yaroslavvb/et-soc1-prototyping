#!/usr/bin/env python3
"""E186 (Q158, the kit): write harness-e186.json, the sha256 of every file E186's box session runs, sources or reads, after the run kit is
final (E186.md section 12, step 4). check_e186.py, run_e186.py, run_e186t.py and smoke_gate_e186.py refuse on any difference from it. A
port of tools/claims-v3/e182/make_harness_e182.py. E78's card code, E128's guard, Q136(w)'s checker and table, the workload's host source
and Q139(k)'s files must equal E182's registered values (tools/claims-v3/e182/harness-e182.json > card_code_unchanged_sha256, which are
E178's, E171's and E163's), so the box runs the code E182 ran on 8 Nov 2026; the four box binaries are E182's (E178's). The train host is
E182's host-only change, built on the box by build_host_e186.sh into build/e186host/ from the committed workloads/sparsity with E182's
patch_host_e182.py, unchanged: what is registered is its patched SOURCE, computed here by applying that patch to the committed main.cpp
and required to equal harness-e182.json's train_host_source_sha256 (the source E182 built and ran); the binary's sha256 is recorded on the
box at its build (build/e186host/SHA256) and in every block's binaries.sha256. E182's files the box calls (the patch, the input check
and the two harness files it reads, E182's v2 build script that the input check pins) and the 8 build inputs (harness-e182-note1.json's)
are pinned too, so step 5's sync sends them. The tiles: the 14 M12 tiles and E78's fp32.ones that E186 runs, and E78's six anchor tiles.
Standard library only.

    /usr/bin/python3 -B tools/claims-v3/e186/make_harness_e186.py            # writes harness-e186.json
    /usr/bin/python3 -B tools/claims-v3/e186/make_harness_e186.py --check    # rebuilds it in memory and compares: CHECK PASS or FAIL
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "harness-e186.json")
E186_FILES = ["e186_common.py", "run_e186.py", "run_e186t.py", "block_e186.sh", "queue_e186.sh", "session_e186.sh", "check_e186.py",
              "preflight_e186.sh", "smoke_gate_e186.py", "build_host_e186.sh"]
E182_CALLED = ["tools/claims-v3/e182/patch_host_e182.py", "tools/claims-v3/e182/check_inputs_e182.py", "tools/claims-v3/e182/harness-e182.json",
               "tools/claims-v3/e182/harness-e182-note1.json", "tools/claims-v3/e182/build_host_e182_v2.sh"]
REGISTRATION = ["tools/claims-v3/e186/E186.md", "tools/claims-v3/e186/SHA256SUMS-e186-registration", "tools/claims-v3/e186/plan-e186.json",
                "tools/claims-v3/e186/plan_e186.py", "tools/claims-v3/e186/forecast-e186.json", "tools/claims-v3/e186/e186_stats.py",
                "tools/claims-v3/e186/power-e186.json", "tools/claims-v3/m12/SHA256SUMS-m12-e186", "tools/claims-v3/m12/kinds-m12-e186.json",
                "tools/claims-v3/m12/candidates-m12-e186.json"]
WATCHER = ["tools/claims-v3/hpl/watcher_q142s.py", "tools/claims-v3/hpl/run_hpl.py.dated-note.md", "tools/claims-v3/hpl/run_hpl.py.dated-note-2.md"]


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def train_source_sha():
    sys.path.insert(0, os.path.join(TOP, "tools", "claims-v3", "e182"))
    import patch_host_e182 as P  # noqa: E402  (patch_text only)
    raw = open(os.path.join(TOP, "workloads/sparsity/host/main.cpp"), "rb").read()
    return hashlib.sha256(P.patch_text(raw.decode()).encode()).hexdigest()


def build():
    e182 = json.load(open(os.path.join(TOP, "tools/claims-v3/e182/harness-e182.json")))
    n1 = json.load(open(os.path.join(TOP, "tools/claims-v3/e182/harness-e182-note1.json")))
    card = {rel: sha(rel) for rel in e182["card_code_unchanged_sha256"]}
    diff = [rel for rel, h in card.items() if h != e182["card_code_unchanged_sha256"][rel]]
    if diff:
        raise SystemExit(f"the reused card code differs from E182's registered values: {diff}")
    inputs = {rel: sha(rel) for rel in n1["train_host_build_inputs_sha256"]}
    if inputs != n1["train_host_build_inputs_sha256"]:
        raise SystemExit("the train host's build inputs differ from harness-e182-note1.json's")
    for rel, h in n1["kit_note1_box_files_sha256"].items():
        if sha(rel) != h:
            raise SystemExit(f"{rel} differs from harness-e182-note1.json's pin")
    sys.path.insert(0, HERE)
    import e186_common as e  # noqa: E402
    bad = e.check_frozen()
    if bad:
        raise SystemExit("refusing: " + bad)
    items = {it["name"]: it for it in e.load_items()}
    tiles = {}
    for n in list(e.E186_NAMES) + list(e.ANCHORS):
        rel = items[n]["tile"]
        tiles[rel] = sha(rel)
        if tiles[rel] != items[n]["sha256"]:
            raise SystemExit(f"{rel}: sha256 differs from its item's registered sha256")
    if len(tiles) != 21:
        raise SystemExit(f"{len(tiles)} tiles, not 21 (14 of M12's, E78's fp32.ones, 6 anchors)")
    tsrc = train_source_sha()
    if tsrc != e182["train_host_source_sha256"]["build/e182host/src/host/main.cpp"]:
        raise SystemExit("the patched train host source is not the one E182 registered")
    h = {"_what": "E186 (Q158, the kit): the sha256 of every file E186's box session runs, sources or reads; written by make_harness_e186.py "
                  "after the run kit; check_e186.py, run_e186.py, run_e186t.py and smoke_gate_e186.py refuse on any difference",
         "card_code_unchanged_sha256": card,
         "card_code_equals": "every value equals tools/claims-v3/e182/harness-e182.json > card_code_unchanged_sha256 (E178's, E171's and E163's)",
         "e186_card_files_sha256": {f"tools/claims-v3/e186/{f}": sha(f"tools/claims-v3/e186/{f}") for f in E186_FILES},
         "e182_files_called_sha256": {rel: sha(rel) for rel in E182_CALLED},
         "e182_files_called_note": "called or read on the box unchanged: the train host's patch, the build inputs' check and the two harness "
                                   "files it reads, and E182's v2 build script, which the check's tree mode pins (it is not run by E186)",
         "registration_sha256": {rel: sha(rel) for rel in REGISTRATION},
         "train_host_build_inputs_sha256": dict(sorted(inputs.items())),
         "train_host_build_inputs_note": "harness-e182-note1.json's 8 build inputs (with main.cpp, card_code_unchanged_sha256): every file the "
                                         "train host's build reads from the workload; build_host_e186.sh copies exactly the 9",
         "watcher_sha256": {rel: sha(rel) for rel in WATCHER},
         "watcher_note": "pinned, not imported: E186's runners are run_e78.py through run_e186.py and run_e186t.py, which have no run_hpl Watcher",
         "tiles_sha256": dict(sorted(tiles.items())),
         "box_binaries_sha256": e182["box_binaries_sha256"],
         "box_binaries_note": "E182's four (E178's, E163's), which E182 ran on aifoundry3 (~/aifoundry) on 8 Nov 2026: E78's sparsity_host (the "
                              "heater), the kernel every launch runs, the C-logging host built by build_host_ccheck.sh, ettelem. If any differs on "
                              "the box, nothing runs until a dated amendment beside E186.md registers the new one",
         "train_host_source_sha256": {"build/e186host/src/host/main.cpp": tsrc},
         "train_host_note": "the train host is compiled on the box by build_host_e186.sh (the runbook's step 6) from the committed "
                            "workloads/sparsity/host/main.cpp with E182's patch_host_e182.py: its patched source must equal this sha256, "
                            "which is harness-e182.json's for build/e182host/ (the source E182 ran); the binary's sha256 is written to "
                            "build/e186host/SHA256 at the build and copied into every block's binaries.sha256"}
    return json.dumps(h, indent=1) + "\n", h


def main():
    s, h = build()
    n = sum(len(h[k]) for k in ("card_code_unchanged_sha256", "e186_card_files_sha256", "e182_files_called_sha256", "registration_sha256",
                                "train_host_build_inputs_sha256", "watcher_sha256", "tiles_sha256", "box_binaries_sha256",
                                "train_host_source_sha256"))
    if "--check" in sys.argv:
        ok = os.path.exists(OUT) and open(OUT).read() == s
        print("CHECK", "PASS" if ok else "FAIL", f"({n} files)")
        return 0 if ok else 1
    open(OUT, "w").write(s)
    print(f"wrote tools/claims-v3/e186/harness-e186.json: {n} files ({len(h['tiles_sha256'])} tiles, {len(WATCHER)} watcher files, "
          f"4 box binaries, the train host's patched source)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
