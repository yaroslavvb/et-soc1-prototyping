#!/usr/bin/env python3
"""E188 (Q165, the kit): write harness-e188.json, the sha256 of every file E188's box session runs, sources or reads, after the run kit is
final (E188.md section 13, step 3). check_e188.py, run_e188.py, run_e188t.py and smoke_gate_e188.py refuse on any difference from it. A
port of tools/claims-v3/e186/make_harness_e186.py (itself E182's). E78's card code, E128's guard, Q136(w)'s checker and table, the
workload's host source and Q139(k)'s files must equal E182's registered values (tools/claims-v3/e182/harness-e182.json >
card_code_unchanged_sha256, which are E178's, E171's and E163's), so the box runs the code E182 and E186 ran; the four box binaries are
E182's (E178's). The train host is E182's host-only change, built on the box by build_host_e188.sh into build/e188host/ from the committed
workloads/sparsity with E182's patch_host_e182.py, unchanged: what is registered is its patched SOURCE, computed here by applying that patch
to the committed main.cpp and required to equal harness-e182.json's train_host_source_sha256 (the source E182 built and E182 and E186 ran);
the binary's sha256 is recorded on the box at its build (build/e188host/SHA256) and in every block's binaries.sha256, and its train change
is read from its behaviour (train_check_e188.sh), never grepped. E182's files the box calls (the patch, the input check and the two harness
files it reads, E182's v2 build script that the input check pins) and the 8 build inputs (harness-e182-note1.json's) are pinned too, so
step 5's sync sends them. The tiles: the fifteen kinds' tiles E188 runs (E188's six new ones, E78's fp32.ones and fp32.pi, E178's two, E182's
two, E186's list's one, and E60's lq_h0 and E67's aq_h0 at their committed data paths) and E78's six anchor tiles: 21.

    /usr/bin/python3 -B tools/claims-v3/e188/make_harness_e188.py            # writes harness-e188.json
    /usr/bin/python3 -B tools/claims-v3/e188/make_harness_e188.py --check    # rebuilds it in memory and compares: CHECK PASS or FAIL
Standard library only.

    /usr/bin/python3 -B tools/claims-v3/e188/make_harness_e188.py            # writes harness-e188.json
    /usr/bin/python3 -B tools/claims-v3/e188/make_harness_e188.py --check    # rebuilds it in memory and compares: CHECK PASS or FAIL
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "harness-e188.json")
E188_FILES = ["e188_common.py", "run_e188.py", "run_e188t.py", "block_e188.sh", "queue_e188.sh", "session_e188.sh", "check_e188.py",
              "preflight_e188.sh", "smoke_gate_e188.py", "build_host_e188.sh", "train_check_e188.sh"]
E182_CALLED = ["tools/claims-v3/e182/patch_host_e182.py", "tools/claims-v3/e182/check_inputs_e182.py", "tools/claims-v3/e182/harness-e182.json",
               "tools/claims-v3/e182/harness-e182-note1.json", "tools/claims-v3/e182/build_host_e182_v2.sh"]
REGISTRATION = ["tools/claims-v3/e188/E188.md", "tools/claims-v3/e188/SHA256SUMS-e188-registration", "tools/claims-v3/e188/plan-e188.json",
                "tools/claims-v3/e188/plan_e188.py", "tools/claims-v3/e188/forecast-e188.json", "tools/claims-v3/e188/forecast_e188.py",
                "tools/claims-v3/e188/e188_stats.py", "tools/claims-v3/e188/power-e188.json", "tools/claims-v3/e188/kinds-e188.json",
                "tools/claims-v3/e188/ofm-e188.json"]
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
    import e188_common as e  # noqa: E402
    bad = e.check_frozen()
    if bad:
        raise SystemExit("refusing: " + bad)
    items = {it["name"]: it for it in e.load_items()}
    tiles = {}
    for n in list(e.E188_NAMES) + list(e.ANCHORS):
        rel = items[n]["tile"]
        tiles[rel] = sha(rel)
        if tiles[rel] != items[n]["sha256"]:
            raise SystemExit(f"{rel}: sha256 differs from its item's registered sha256")
    if len(tiles) != 21:
        raise SystemExit(f"{len(tiles)} tiles, not 21 (the fifteen kinds' and the six anchors')")
    tsrc = train_source_sha()
    if tsrc != e182["train_host_source_sha256"]["build/e182host/src/host/main.cpp"]:
        raise SystemExit("the patched train host source is not the one E182 registered")
    h = {"_what": "E188 (Q165, the kit): the sha256 of every file E188's box session runs, sources or reads; written by make_harness_e188.py "
                  "after the run kit; check_e188.py, run_e188.py, run_e188t.py and smoke_gate_e188.py refuse on any difference",
         "card_code_unchanged_sha256": card,
         "card_code_equals": "every value equals tools/claims-v3/e182/harness-e182.json > card_code_unchanged_sha256 (E178's, E171's and E163's)",
         "e188_card_files_sha256": {f"tools/claims-v3/e188/{f}": sha(f"tools/claims-v3/e188/{f}") for f in E188_FILES},
         "e182_files_called_sha256": {rel: sha(rel) for rel in E182_CALLED},
         "e182_files_called_note": "called or read on the box unchanged: the train host's patch, the build inputs' check and the two harness "
                                   "files it reads, and E182's v2 build script, which the check's tree mode pins (it is not run by E188)",
         "registration_sha256": {rel: sha(rel) for rel in REGISTRATION},
         "train_host_build_inputs_sha256": dict(sorted(inputs.items())),
         "train_host_build_inputs_note": "harness-e182-note1.json's 8 build inputs (with main.cpp, card_code_unchanged_sha256): every file the "
                                         "train host's build reads from the workload; build_host_e188.sh copies exactly the 9",
         "watcher_sha256": {rel: sha(rel) for rel in WATCHER},
         "watcher_note": "pinned, not imported: E188's runners are run_e78.py through run_e188.py and run_e188t.py, which have no run_hpl Watcher",
         "tiles_sha256": dict(sorted(tiles.items())),
         "box_binaries_sha256": e182["box_binaries_sha256"],
         "box_binaries_note": "E182's four (E178's, E163's), which E182 and E186 ran on aifoundry3 (~/aifoundry) on 8 and 9 Nov 2026: E78's "
                              "sparsity_host (the heater), the kernel every launch runs, the C-logging host built by build_host_ccheck.sh, ettelem. If "
                              "any differs on the box, nothing runs until a dated amendment beside E188.md registers the new one",
         "train_host_source_sha256": {"build/e188host/src/host/main.cpp": tsrc},
         "train_host_note": "the train host is compiled on the box by build_host_e188.sh (the runbook's step 6) from the committed "
                            "workloads/sparsity/host/main.cpp with E182's patch_host_e182.py: its patched source must equal this sha256, "
                            "which is harness-e182.json's for build/e182host/ (the source E182 and E186 ran); the binary's sha256 is written to "
                            "build/e188host/SHA256 at the build and copied into every block's binaries.sha256; its train change is read "
                            "from its behaviour by train_check_e188.sh, never grepped"}
    return json.dumps(h, indent=1) + "\n", h


def main():
    s, h = build()
    n = sum(len(h[k]) for k in ("card_code_unchanged_sha256", "e188_card_files_sha256", "e182_files_called_sha256", "registration_sha256",
                                "train_host_build_inputs_sha256", "watcher_sha256", "tiles_sha256", "box_binaries_sha256",
                                "train_host_source_sha256"))
    if "--check" in sys.argv:
        ok = os.path.exists(OUT) and open(OUT).read() == s
        print("CHECK", "PASS" if ok else "FAIL", f"({n} files)")
        return 0 if ok else 1
    open(OUT, "w").write(s)
    print(f"wrote tools/claims-v3/e188/harness-e188.json: {n} files ({len(h['tiles_sha256'])} tiles, {len(WATCHER)} watcher files, "
          f"4 box binaries, the train host's patched source)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
