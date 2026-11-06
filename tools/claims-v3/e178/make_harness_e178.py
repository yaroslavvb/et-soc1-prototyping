#!/usr/bin/env python3
"""E178 (Q146, the kit): write harness-e178.json, the sha256 of every file E178's box session runs, sources or reads, after the run kit is
final (E178.md section 12, step 3). check_e178.py, run_e178.py, reduce_e178.py and smoke_gate_e178.py refuse on any difference from it.
A port of tools/claims-v3/e171/make_harness_e171.py. E78's card code, E128's guard, Q136(w)'s checker and table, the workload's host
source and Q139(k)'s files must equal E163's registered values (tools/claims-v3/e163/harness-e163.json > card_code_unchanged_sha256), and
E171's (tools/claims-v3/e171/harness-e171.json), so the box runs the code E163 and E171 ran; the four box binaries are E163's (E153's),
which E171 ran on 5 Nov 2026. The watcher fix (watcher_q142s.py and its two amendments) is pinned, not imported. The tiles: E178's 34 new
tiles, E78's six committed one-number tiles the registration runs under their own labels, and E78's six anchor tiles. Standard library only.

    python3 -B tools/claims-v3/e178/make_harness_e178.py            # writes harness-e178.json
    python3 -B tools/claims-v3/e178/make_harness_e178.py --check    # rebuilds it in memory and compares: CHECK PASS or FAIL
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "harness-e178.json")
E178_FILES = ["e178_common.py", "run_e178.py", "block_e178.sh", "queue_e178.sh", "session_e178.sh", "check_e178.py",
              "preflight_e178.sh", "smoke_gate_e178.py", "reduce_e178.py"]
REGISTRATION = ["tools/claims-v3/e178/E178.md", "tools/claims-v3/e178/E178.md.dated-note-A1.md",
                "tools/claims-v3/e178/SHA256SUMS-e178-registration", "tools/claims-v3/e178/SHA256SUMS-e178-a1",
                "tools/claims-v3/e178/kinds-e178.json", "tools/claims-v3/e178/plan-e178.json", "tools/claims-v3/e178/plan_e178.py",
                "tools/claims-v3/e178/kit-e178.json"]
WATCHER = ["tools/claims-v3/hpl/watcher_q142s.py", "tools/claims-v3/hpl/run_hpl.py.dated-note.md", "tools/claims-v3/hpl/run_hpl.py.dated-note-2.md"]


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def build():
    e163 = json.load(open(os.path.join(TOP, "tools/claims-v3/e163/harness-e163.json")))
    e171 = json.load(open(os.path.join(TOP, "tools/claims-v3/e171/harness-e171.json")))
    card = {rel: sha(rel) for rel in e163["card_code_unchanged_sha256"]}
    diff = [rel for rel, h in card.items() if h != e163["card_code_unchanged_sha256"][rel] or h != e171["card_code_unchanged_sha256"].get(rel)]
    if diff:
        raise SystemExit(f"the reused card code differs from E163's or E171's registered values: {diff}")
    if e163["box_binaries_sha256"] != e171["box_binaries_sha256"]:
        raise SystemExit("E163's and E171's box binaries differ")
    sys.path.insert(0, HERE)
    import e178_common as e  # noqa: E402
    bad = e.check_frozen()
    if bad:
        raise SystemExit("refusing: " + bad)
    items = {it["name"]: it for it in e.load_items()}
    tiles = {}
    for n in list(e.E178_NAMES) + list(e.ANCHORS):
        rel = items[n]["tile"]
        tiles[rel] = sha(rel)
        if tiles[rel] != items[n]["sha256"]:
            raise SystemExit(f"{rel}: sha256 differs from its item's registered sha256")
    if len(tiles) != 46:
        raise SystemExit(f"{len(tiles)} tiles, not 46 (34 new, 6 committed one-number, 6 anchors)")
    h = {"_what": "E178 (Q146, the kit): the sha256 of every file E178's box session runs, sources or reads; written by make_harness_e178.py "
                  "after the run kit; check_e178.py, run_e178.py, reduce_e178.py and smoke_gate_e178.py refuse on any difference",
         "card_code_unchanged_sha256": card,
         "card_code_equals": "every value equals tools/claims-v3/e163/harness-e163.json and tools/claims-v3/e171/harness-e171.json > "
                             "card_code_unchanged_sha256",
         "e178_card_files_sha256": {f"tools/claims-v3/e178/{f}": sha(f"tools/claims-v3/e178/{f}") for f in E178_FILES},
         "registration_sha256": {rel: sha(rel) for rel in REGISTRATION},
         "watcher_sha256": {rel: sha(rel) for rel in WATCHER},
         "watcher_note": "pinned, not imported: E178's runner is run_e78.py through run_e178.py, which has no run_hpl Watcher (E171.md, 'The watcher')",
         "tiles_sha256": dict(sorted(tiles.items())),
         "box_binaries_sha256": e163["box_binaries_sha256"],
         "box_binaries_note": "E163's four (E153's), which E171 ran on aifoundry3 (~/aifoundry) on 5 Nov 2026: E78's sparsity_host (the heater), "
                              "the kernel every launch runs, the C-logging host built by build_host_ccheck.sh, ettelem. If any differs on the "
                              "box, nothing runs until a dated amendment beside E178.md registers the new one"}
    return json.dumps(h, indent=1) + "\n", h


def main():
    s, h = build()
    n = sum(len(h[k]) for k in ("card_code_unchanged_sha256", "e178_card_files_sha256", "registration_sha256", "watcher_sha256", "tiles_sha256",
                                "box_binaries_sha256"))
    if "--check" in sys.argv:
        ok = os.path.exists(OUT) and open(OUT).read() == s
        print("CHECK", "PASS" if ok else "FAIL", f"({n} files)")
        return 0 if ok else 1
    open(OUT, "w").write(s)
    print(f"wrote tools/claims-v3/e178/harness-e178.json: {n} files ({len(h['tiles_sha256'])} tiles, {len(WATCHER)} watcher files, 4 box binaries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
