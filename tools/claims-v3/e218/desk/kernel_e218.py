#!/usr/bin/env python3
"""E218 (Q230) desk: the kernel and hosts by path and sha256 - rgm136 (E136's binary, unchanged: every E218 point; its gemmL loop for families
Gt, Y, F and its gemmLnc branch for family G) and rgm211's host (E211's; it runs rgm136's ELF for the gemmLnc branch, E211's family C gate), every
source file re-hashed and compared with E215's registered record (itself equal to E206's, E211's and E213's), the pins the kit gates on, and which
host and ELF run each arm family. Standard library only.

    python3 -I -B tools/claims-v3/e218/desk/kernel_e218.py           writes ../kernel-e218.json
    python3 -I -B tools/claims-v3/e218/desk/kernel_e218.py --check   re-hashes the sources and compares with kernel-e218.json (exit 0 = PASS)

THE ARM FAMILIES (E211's, E213's and E215's): gemmL on rgm136's host with rgm136's ELF (families Gt, Y, F; the tie t01; the smoke s01); gemmLnc on
rgm211's host with rgm136's ELF, no new device code (family G; its smoke s03). aifoundry3 card 0 ran both families (E211, E213 arm A, E215 arm
A), each gated by its identity: rgm136's .text and loadable identity on this box (aifoundry3's GCC prints its own version string into the ELF).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(HERE, "..", "kernel-e218.json")
RGM136 = "tools/claims-v3/e136/rgm136"
RGM211 = "tools/claims-v3/e211/rgm211"
E215_KERNEL = ("tools/claims-v3/e215/kernel-e215.json", "a4940986978ac154302a63b70ef3d528afc9bc28554e70fde65044970467db8a")


def tree(rel):
    files = {}
    for dp, dns, fns in os.walk(os.path.join(REPO, rel)):
        dns.sort()
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            files[os.path.relpath(p, REPO)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return dict(sorted(files.items()))


def build():
    p = os.path.join(REPO, E215_KERNEL[0])
    got = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if got != E215_KERNEL[1]:
        raise SystemExit(f"kernel_e218: {E215_KERNEL[0]} is {got}, registered {E215_KERNEL[1]}")
    k15 = json.load(open(p))
    s136, s211 = tree(RGM136), tree(RGM211)
    if k15["kernels"]["rgm136"]["sources_sha256"] != s136 or k15["kernels"]["rgm211"]["sources_sha256"] != s211:
        raise SystemExit("kernel_e218: a kernel's sources differ from E215's registered record")
    pts = json.load(open(os.path.join(HERE, "..", "points-e218.json")))
    where = {}
    for q in pts["points"]:
        where.setdefault(q["loop"], []).append(q["id"])
    r136 = dict(k15["kernels"]["rgm136"])
    r136["equal_to"] = [E215_KERNEL[0]] + list(k15["kernels"]["rgm136"].get("equal_to", []))
    r211 = {k: v for k, v in k15["kernels"]["rgm211"].items() if k in ("sources_sha256", "elf_sha256", "loadable_identity_sha256", "tree")}
    r211["role_in_E218"] = "its host only: it runs rgm136's ELF for the gemmLnc branch (family G and the smoke s03); rgm211's own ELF runs no E218 point"
    k = {"experiment": "E218", "request": "Q230", "what": "E218's kernel and hosts by path and sha256, the pins and the arm families (desk)",
         "kernels": {"rgm136": r136, "rgm211_host": r211},
         "arm_families": {
             "rgm136 gemmL": {"host": "rgm136", "elf": "rgm136", "arms": "gemmL<MB>x<NB>x<KB>", "points": where.get("rgm136 gemmL", []),
                              "also": ["t01 (tie)", "s01 (smoke, the session gate)"], "gate": "E206's / E207's / E213's / E215's on aifoundry3"},
             "rgm136 gemmLnc": {"host": "rgm211", "elf": "rgm136", "arms": "gemmLnc<MB>x<NB>x<KB>", "points": where.get("rgm136 gemmLnc", []),
                                "also": ["s03 (smoke, family G's own stop path)"],
                                "gate": "E211's family C gate (E213 arm A and E215 arm A ran it on aifoundry3 card 0)"}},
         "build": k15.get("build"),
         "host_arguments": ("--test fma --type <fmt> --pattern none --values <arm>:randn:<tile> --shires <mask> --per-shire 32 --seconds 6 "
                            "--budget 7.5 --seed 1 (the kit adds --kernel, --stop-file and its absolute paths); random data: fp32 and fp16 "
                            "kinds/tiles/<fmt>/randn.bin, int8 kinds/tiles/int8/full.bin (E101's grammar, as E213 and E215 ran random)")}
    return k


def main():
    k = build()
    if "--check" in sys.argv:
        old = json.load(open(OUT))
        same = old == json.loads(json.dumps(k))
        print(f"kernel_e218 --check: rgm136 {len(k['kernels']['rgm136']['sources_sha256'])} and rgm211 {len(k['kernels']['rgm211_host']['sources_sha256'])} "
              f"source files re-hashed, equal to E215's record; equal to kernel-e218.json: {same}")
        print("PASS" if same else "FAIL")
        sys.exit(0 if same else 1)
    json.dump(k, open(OUT, "w"), indent=1)
    print(f"kernel_e218: rgm136 ELF {k['kernels']['rgm136']['elf_sha256'][:16]}, .text {k['kernels']['rgm136']['text_sha256'][:16]}, "
          f"loadable {k['kernels']['rgm136']['loadable_identity_sha256'][:16]}; sources equal to E215's record")


if __name__ == "__main__":
    main()
