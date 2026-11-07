#!/usr/bin/env python3
"""E182 (Q153, the kit): write harness-e182.json, the sha256 of every file E182's box session runs, sources or reads, after the run kit is
final (E182.md section 12, step 2). check_e182.py, run_e182.py, run_e182t.py and smoke_gate_e182.py refuse on any difference from it. A
port of tools/claims-v3/e178/make_harness_e178.py. E78's card code, E128's guard, Q136(w)'s checker and table, the workload's host source
and Q139(k)'s files must equal E178's registered values (tools/claims-v3/e178/harness-e178.json > card_code_unchanged_sha256, which are
E163's and E171's), so the box runs the code E178 ran on 6 Nov 2026; the four box binaries are E178's. The train host is new: it is built
on the box from the committed workloads/sparsity with patch_host_e182.py, so what is registered is its patched SOURCE (the patch is
deterministic text: train_host_source_sha256, computed here by applying the patch to the committed main.cpp); the binary's sha256 is
recorded on the box at its build (build/e182host/SHA256) and in every block's binaries.sha256. The tiles: E182's 16 new tiles, E178's six
reused tiles, E78's two committed one-number tiles and E78's six anchor tiles. Standard library only.

    /usr/bin/python3 -B tools/claims-v3/e182/make_harness_e182.py            # writes harness-e182.json
    /usr/bin/python3 -B tools/claims-v3/e182/make_harness_e182.py --check    # rebuilds it in memory and compares: CHECK PASS or FAIL
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "harness-e182.json")
E182_FILES = ["e182_common.py", "run_e182.py", "run_e182t.py", "block_e182.sh", "queue_e182.sh", "session_e182.sh", "check_e182.py",
              "preflight_e182.sh", "smoke_gate_e182.py", "patch_host_e182.py", "build_host_e182.sh"]
REGISTRATION = ["tools/claims-v3/e182/E182.md", "tools/claims-v3/e182/SHA256SUMS-e182-registration", "tools/claims-v3/e182/kinds-e182.json",
                "tools/claims-v3/e182/plan-e182.json", "tools/claims-v3/e182/plan_e182.py", "tools/claims-v3/e182/forecast-e182.json",
                "tools/claims-v3/e182/e182_stats.py", "tools/claims-v3/e182/noise/noise-e182.json"]
WATCHER = ["tools/claims-v3/hpl/watcher_q142s.py", "tools/claims-v3/hpl/run_hpl.py.dated-note.md", "tools/claims-v3/hpl/run_hpl.py.dated-note-2.md"]


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def train_source_sha():
    sys.path.insert(0, HERE)
    import patch_host_e182 as P  # noqa: E402  (patch_text only)
    raw = open(os.path.join(TOP, "workloads/sparsity/host/main.cpp"), "rb").read()
    return hashlib.sha256(P.patch_text(raw.decode()).encode()).hexdigest()


def build():
    e178 = json.load(open(os.path.join(TOP, "tools/claims-v3/e178/harness-e178.json")))
    card = {rel: sha(rel) for rel in e178["card_code_unchanged_sha256"]}
    diff = [rel for rel, h in card.items() if h != e178["card_code_unchanged_sha256"][rel]]
    if diff:
        raise SystemExit(f"the reused card code differs from E178's registered values: {diff}")
    sys.path.insert(0, HERE)
    import e182_common as e  # noqa: E402
    bad = e.check_frozen()
    if bad:
        raise SystemExit("refusing: " + bad)
    items = {it["name"]: it for it in e.load_items()}
    tiles = {}
    for n in list(e.E182_NAMES) + list(e.ANCHORS):
        rel = items[n]["tile"]
        tiles[rel] = sha(rel)
        if tiles[rel] != items[n]["sha256"]:
            raise SystemExit(f"{rel}: sha256 differs from its item's registered sha256")
    if len(tiles) != 30:
        raise SystemExit(f"{len(tiles)} tiles, not 30 (16 new, 6 of E178's, 2 of E78's one-number, 6 anchors)")
    h = {"_what": "E182 (Q153, the kit): the sha256 of every file E182's box session runs, sources or reads; written by make_harness_e182.py "
                  "after the run kit; check_e182.py, run_e182.py, run_e182t.py and smoke_gate_e182.py refuse on any difference",
         "card_code_unchanged_sha256": card,
         "card_code_equals": "every value equals tools/claims-v3/e178/harness-e178.json > card_code_unchanged_sha256 (E163's and E171's)",
         "e182_card_files_sha256": {f"tools/claims-v3/e182/{f}": sha(f"tools/claims-v3/e182/{f}") for f in E182_FILES},
         "registration_sha256": {rel: sha(rel) for rel in REGISTRATION},
         "watcher_sha256": {rel: sha(rel) for rel in WATCHER},
         "watcher_note": "pinned, not imported: E182's runners are run_e78.py through run_e182.py and run_e182t.py, which have no run_hpl Watcher",
         "tiles_sha256": dict(sorted(tiles.items())),
         "box_binaries_sha256": e178["box_binaries_sha256"],
         "box_binaries_note": "E178's four (E163's), which E178 ran on aifoundry3 (~/aifoundry) on 6 Nov 2026: E78's sparsity_host (the heater), "
                              "the kernel every launch runs, the C-logging host built by build_host_ccheck.sh, ettelem. If any differs on the "
                              "box, nothing runs until a dated amendment beside E182.md registers the new one",
         "train_host_source_sha256": {"build/e182host/src/host/main.cpp": train_source_sha()},
         "train_host_note": "the train host is compiled on the box by build_host_e182.sh (the runbook's step 6) from the committed "
                            "workloads/sparsity/host/main.cpp with patch_host_e182.py: its patched source must equal this sha256; the "
                            "binary's sha256 is written to build/e182host/SHA256 at the build and copied into every block's binaries.sha256"}
    return json.dumps(h, indent=1) + "\n", h


def main():
    s, h = build()
    n = sum(len(h[k]) for k in ("card_code_unchanged_sha256", "e182_card_files_sha256", "registration_sha256", "watcher_sha256", "tiles_sha256",
                                "box_binaries_sha256", "train_host_source_sha256"))
    if "--check" in sys.argv:
        ok = os.path.exists(OUT) and open(OUT).read() == s
        print("CHECK", "PASS" if ok else "FAIL", f"({n} files)")
        return 0 if ok else 1
    open(OUT, "w").write(s)
    print(f"wrote tools/claims-v3/e182/harness-e182.json: {n} files ({len(h['tiles_sha256'])} tiles, {len(WATCHER)} watcher files, "
          f"4 box binaries, the train host's patched source)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
