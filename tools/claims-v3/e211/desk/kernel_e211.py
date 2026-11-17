#!/usr/bin/env python3
"""E211 (Q204): the two kernels by path and sha256, their build commands and their identities (kernel-e211.json). Desk; standard library.

    python3 -I -B tools/claims-v3/e211/desk/kernel_e211.py --make <build dir>   writes ../kernel-e211.json from the sources and the desk build in
                                                                                <build dir> (b-rgm136/kernel/sparsity.elf, b-rgm211/kernel/sparsity.elf)
    python3 -I -B tools/claims-v3/e211/desk/kernel_e211.py --check              re-hashes every source and compares with kernel-e211.json, and
                                                                                checks rgm136's entries against E206's kernel-e206.json (exit 0 = PASS)

The identities come from the registration's own desk build (aifoundry2, riscv64-unknown-elf-gcc "() 15.1.0", cmake 3.28.3, inside the round's CPU
slot and without devices; nothing built was run). The kit rebuilds rgm211 on aifoundry3, whose gcc prints "(g1b306039a) 15.1.0": its .text and
loadable identity must equal the pins here (its whole ELF may differ, in sections the card never loads).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(HERE, "..", "kernel-e211.json")
FILES = ("CMakeLists.txt", "README.md", "sparsity_args.h", "host/CMakeLists.txt", "host/Constants.h.in", "host/main.cpp", "kernel/CMakeLists.txt",
         "kernel/crt.S", "kernel/sections.ld", "kernel/sparsity.c")
TREES = {"rgm136": "tools/claims-v3/e136/rgm136", "rgm211": "tools/claims-v3/e211/rgm211"}


def sha(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def sources():
    return {k: {f"{t}/{f}": sha(f"{t}/{f}") for f in FILES} for k, t in TREES.items()}


def make(build):
    sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "e211"))
    import ident_e211 as I
    ks = {}
    for k in TREES:
        idt = I.identity(os.path.join(build, f"b-{k}", "kernel", "sparsity.elf"))
        ks[k] = {"tree": TREES[k], "elf_sha256": idt["elf_sha256"], "text_sha256": idt["text_sha256"],
                 "loadable_identity_sha256": idt["loadable_identity_sha256"], "sources_sha256": sources()[k]}
    ks["rgm136"]["note"] = ("E136's kernel, unchanged: its whole ELF is E136's build record aace138c..., its .text E206's TEXT_PIN, its loadable "
                            "identity E206's LOAD_PIN (check_e206.py); E206 arm A ran it on aifoundry3 by .text and identity (gcc 'g1b306039a')")
    ks["rgm211"]["note"] = ("made by make_rgm211.py from rgm136 as committed (rgm211.diff is the whole difference); never run anywhere: the desk "
                            "builds of Q202 (mm-kernel2, critic-kernel2) and Q204 (this) ran nothing they built")
    out = {"experiment": "E211", "request": "Q204",
           "what": "E211's two kernels by path and sha256, their build commands and identities (desk build on aifoundry2)",
           "build": {"commands": ["cmake -S <tree> -B <build> -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev", "cmake --build <build> -j4"],
                     "where": "aifoundry2, inside the round's CPU slot (nice 10) and nodev.sh (no device node), from the registration's scratch clone",
                     "toolchain": "riscv64-unknown-elf-gcc () 15.1.0; cmake 3.28.3; g++ 13.3.0", "kernel": "<build>/kernel/sparsity.elf",
                     "host": "<build>/host/sparsity_host (its bytes carry the build path: hosts are gated by behaviour, E190's form)",
                     "text_recipe": "objcopy -O binary -j .text <elf> (E206's check_e206.text_sha)",
                     "identity_recipe": "E206's check_e206.elf_identity / identity_sha (check_e191.py's second form)"},
           "arm_families": {"gemmL": {"kernel": "rgm136", "host": "rgm136 (E206's and E207's build of rgm136's host)"},
                            "gemmLn": {"kernel": "rgm211", "host": "rgm211"}, "gemmLnc": {"kernel": "rgm136", "host": "rgm211"}},
           "kernels": ks}
    open(OUT, "w").write(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: {x: v[x] for x in ("elf_sha256", "text_sha256", "loadable_identity_sha256")} for k, v in ks.items()}, indent=1))


def check():
    have = json.load(open(OUT))
    ok = True
    for k, srcs in sources().items():
        same = srcs == have["kernels"][k]["sources_sha256"]
        ok &= same
        print(f"{k} sources: {'SAME' if same else 'DIFFER'} ({len(srcs)} files)")
    e206 = json.load(open(os.path.join(REPO, "tools", "claims-v3", "e206", "kernel-e206.json")))
    flat = json.dumps(e206)
    for x in ("elf_sha256", "text_sha256"):
        v = have["kernels"]["rgm136"][x]
        found = v in flat
        ok &= found
        print(f"rgm136 {x} {v[:16]}... in kernel-e206.json: {found}")
    print("CHECK PASS" if ok else "CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:2] == ["--make"] and len(sys.argv) == 3:
        make(sys.argv[2])
    elif sys.argv[1:] == ["--check"]:
        sys.exit(check())
    else:
        sys.exit(__doc__)
