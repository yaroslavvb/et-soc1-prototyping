#!/usr/bin/env python3
"""E182 (Q153, the kit's dated note 1): write harness-e182-note1.json, the sha256 of every file the train host's box build reads that
harness-e182.json does not pin, and of the two box files note 1 adds (KIT.md.dated-note-1.md section 2, the verifier's MAJOR 2, the
E174 class). harness-e182.json and every file of the kit stay as committed.

THE BUILD'S INPUTS, read from the build itself (workloads/sparsity, unchanged since 28 Sep 2026): the top CMakeLists.txt builds the
kernel as an ExternalProject and adds host/; host/CMakeLists.txt configures host/Constants.h.in and compiles host/main.cpp (pinned
already: harness-e182.json > card_code_unchanged_sha256) with the workload's top directory on its include path; `sparsity_host` depends
on `sparsity_kernel`, so `cmake --build --target sparsity_host` also compiles kernel/CMakeLists.txt's kernel/sparsity.c and kernel/crt.S
with kernel/sections.ld; host/main.cpp and kernel/sparsity.c include sparsity_args.h. That is 8 files beside main.cpp. The other 4
committed files of workloads/sparsity (README.md, analyze.py, run_energy.py, run_lab.sh) are not read by the build, and build_host_e182_v2.sh
copies only the 9. Every claim of this paragraph is asserted below from the files' own text, and the 13 committed files are asserted to be
exactly the 9 and the 4 (git ls-files), so no build input can be missed.

    /usr/bin/python3 -B tools/claims-v3/e182/make_harness_e182_note1.py            # writes harness-e182-note1.json
    /usr/bin/python3 -B tools/claims-v3/e182/make_harness_e182_note1.py --check    # rebuilds it in memory: CHECK PASS or FAIL
Desk only (it runs git); standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(HERE, "harness-e182-note1.json")
WL = "workloads/sparsity"
BUILD_INPUTS = ["CMakeLists.txt", "host/CMakeLists.txt", "host/Constants.h.in", "kernel/CMakeLists.txt", "kernel/crt.S",
                "kernel/sections.ld", "kernel/sparsity.c", "sparsity_args.h"]
MAIN = "host/main.cpp"
NOT_READ = ["README.md", "analyze.py", "run_energy.py", "run_lab.sh"]
NOTE1_BOX_FILES = ["tools/claims-v3/e182/build_host_e182_v2.sh", "tools/claims-v3/e182/check_inputs_e182.py"]
GENERATED = {"Constants.h"}          # host/CMakeLists.txt's configure_file output, in the build directory


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def text(rel):
    return open(os.path.join(TOP, WL, rel)).read()


def derive():
    """assert, from the files' own text, that the build reads exactly BUILD_INPUTS beside main.cpp"""
    bad = []
    tracked = subprocess.run(["git", "-C", TOP, "ls-files", WL], capture_output=True, text=True, check=True).stdout.split()
    tracked = sorted(os.path.relpath(p, WL) for p in tracked)
    if tracked != sorted(BUILD_INPUTS + [MAIN] + NOT_READ):
        bad.append(f"git ls-files {WL} is {tracked}, not the 9 build inputs and the 4 files the build does not read")
    top = text("CMakeLists.txt")
    if "SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/kernel" not in top or "add_subdirectory(host)" not in top \
            or "add_dependencies(sparsity_host sparsity_kernel)" not in top:
        bad.append("the top CMakeLists.txt no longer builds kernel/ as a dependency of host/")
    host = text("host/CMakeLists.txt")
    if "configure_file(Constants.h.in" not in host or "add_executable(sparsity_host main.cpp)" not in host \
            or "${CMAKE_CURRENT_SOURCE_DIR}/.." not in host:
        bad.append("host/CMakeLists.txt no longer reads Constants.h.in and main.cpp with the top directory included")
    kern = text("kernel/CMakeLists.txt")
    for f in ("sections.ld", "sparsity.c", "crt.S"):
        if f not in kern:
            bad.append(f"kernel/CMakeLists.txt no longer names {f}")
    for rel in (MAIN, "kernel/sparsity.c", "kernel/crt.S", "sparsity_args.h"):
        for inc in re.findall(r'^\s*#\s*include\s+"([^"]+)"', text(rel), flags=re.M):
            if inc in GENERATED or inc == "sparsity_args.h" or inc.startswith("etsoc/"):
                continue
            bad.append(f"{rel} includes a local file the list does not hold: {inc}")
    for rel in (MAIN, "kernel/sparsity.c"):
        if '#include "sparsity_args.h"' not in text(rel):
            bad.append(f"{rel} no longer includes sparsity_args.h")
    return bad


def build():
    bad = derive()
    if bad:
        raise SystemExit("refusing:\n  " + "\n  ".join(bad))
    h182 = json.load(open(os.path.join(HERE, "harness-e182.json")))
    main_pin = h182["card_code_unchanged_sha256"][f"{WL}/{MAIN}"]
    if sha(f"{WL}/{MAIN}") != main_pin:
        raise SystemExit(f"{WL}/{MAIN} differs from harness-e182.json's pin")
    h = {"_what": "E182 (Q153, the kit's dated note 1): the sha256 of the train host's box build inputs that harness-e182.json does not pin, "
                  "and of note 1's two box files; written by make_harness_e182_note1.py; check_inputs_e182.py and build_host_e182_v2.sh "
                  "refuse on any difference; rb/s07_a3_sync_e182_v2.sh syncs every file named here",
         "train_host_build_inputs_sha256": {f"{WL}/{rel}": sha(f"{WL}/{rel}") for rel in BUILD_INPUTS},
         "train_host_build_inputs_note": "with workloads/sparsity/host/main.cpp, pinned by harness-e182.json > card_code_unchanged_sha256 "
                                         f"({main_pin}), these are every file `cmake --build --target sparsity_host` reads from the "
                                         "workload (the kernel is built too: sparsity_host depends on sparsity_kernel); README.md, "
                                         "analyze.py, run_energy.py and run_lab.sh are not read, and build_host_e182_v2.sh copies only the 9",
         "kit_note1_box_files_sha256": {rel: sha(rel) for rel in NOTE1_BOX_FILES}}
    return json.dumps(h, indent=1) + "\n", h


def main():
    s, h = build()
    n = len(h["train_host_build_inputs_sha256"]) + len(h["kit_note1_box_files_sha256"])
    if "--check" in sys.argv:
        ok = os.path.exists(OUT) and open(OUT).read() == s
        print("CHECK", "PASS" if ok else "FAIL", f"({n} files: 8 build inputs, 2 box files)")
        return 0 if ok else 1
    open(OUT, "w").write(s)
    print(f"wrote tools/claims-v3/e182/harness-e182-note1.json: {n} files (8 build inputs, 2 box files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
