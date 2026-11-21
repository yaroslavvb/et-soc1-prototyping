#!/usr/bin/env python3
"""E222 (Q236) desk: the kernel and hosts by path and sha256 - rgm136 (E136's binary, unchanged: every E222 point; its gemmL loop for families
R (Y, Gt), T (L3, Y2, G2t), L3b, Y3, G3t, the tie t01 and the smoke s01, its gemmLnc branch for R (G), T-G2 and G3 and the smoke s03) and
rgm211's host (E211's; it runs rgm136's ELF for the gemmLnc branch, E211's family C gate) - every source file re-hashed and compared with E220's
registered record (kernel-e220.json, itself equal to E218's, E215's, E213's, E211's and E206's), and which host and ELF run each arm family. Standard
library only.

    python3 -I -B tools/claims-v3/e222/desk/kernel_e222.py           writes ../kernel-e222.json
    python3 -I -B tools/claims-v3/e222/desk/kernel_e222.py --check   re-hashes the sources and compares with kernel-e222.json (exit 0 = PASS)

The pins the kit gates on are E218's on aifoundry3 (its build record and identity gates, kit 5582edfc); no new device code.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(HERE, "..", "kernel-e222.json")
RGM136 = "tools/claims-v3/e136/rgm136"
RGM211 = "tools/claims-v3/e211/rgm211"
E218_KERNEL = ("tools/claims-v3/e220/kernel-e220.json", "f332b03a9f30aee15ba465c8c497ee31a2cfc758bcb91a6ae10ed8453e54338e")   # E220's record (equal to E218's)


def tree(rel):
    files = {}
    for dp, dns, fns in os.walk(os.path.join(REPO, rel)):
        dns.sort()
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            files[os.path.relpath(p, REPO)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return dict(sorted(files.items()))


def build():
    p = os.path.join(REPO, E218_KERNEL[0])
    got = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if got != E218_KERNEL[1]:
        raise SystemExit(f"kernel_e222: {E218_KERNEL[0]} is {got}, registered {E218_KERNEL[1]}")
    k18 = json.load(open(p))
    s136, s211 = tree(RGM136), tree(RGM211)
    if k18["kernels"]["rgm136"]["sources_sha256"] != s136 or k18["kernels"]["rgm211_host"]["sources_sha256"] != s211:
        raise SystemExit("kernel_e222: a kernel's sources differ from E220's registered record")
    pts = json.load(open(os.path.join(HERE, "..", "points-e222.json")))["points"]
    where = {}
    for q in pts:
        where.setdefault(q["loop"], []).append(q["id"])
    r136 = dict(k18["kernels"]["rgm136"])
    r136["equal_to"] = [E218_KERNEL[0]] + list(k18["kernels"]["rgm136"].get("equal_to", []))
    r211 = dict(k18["kernels"]["rgm211_host"])
    r211["role_in_E222"] = "its host only: it runs rgm136's ELF for the gemmLnc branch (R's rg01, T-G2, G3, the smoke s03); rgm211's own ELF runs no E222 point"
    r211.pop("role_in_E220", None)
    k = {"experiment": "E222", "request": "Q236", "what": "E222's kernel and hosts by path and sha256 and the arm families (desk)",
         "kernels": {"rgm136": r136, "rgm211_host": r211},
         "arm_families": {
             "rgm136 gemmL": {"host": "rgm136", "elf": "rgm136", "arms": "gemmL<MB>x<NB>x<KB>", "points": where.get("rgm136 gemmL", {}),
                              "also": ["t01 (tie)", "s01 (smoke, the session gate)"]},
             "rgm136 gemmLnc": {"host": "rgm211", "elf": "rgm136", "arms": "gemmLnc<MB>x<NB>x<KB>", "points": where.get("rgm136 gemmLnc", {}),
                                "also": ["s03 (smoke, the G block's gate and stop path)"],
                                "gate": "E211's family C gate (E211, E213 arm A, E215 arm A and E218 ran it on aifoundry3 card 0)"}},
         "build": k18.get("build"),
         "host_arguments": ("--test fma --type <fmt> --pattern none --values <arm>:randn:<tile> --shires <mask> --per-shire 32 --seconds 6 "
                            "--budget 7.5 --seed 1 (the kit adds --kernel, --stop-file and its absolute paths); random data: fp32 and fp16 "
                            "kinds/tiles/<fmt>/randn.bin, int8 kinds/tiles/int8/full.bin (E101's grammar)")}
    return k


def main():
    k = build()
    if "--check" in sys.argv:
        old = json.load(open(OUT))
        same = old == json.loads(json.dumps(k))
        print(f"kernel_e222 --check: rgm136 {len(k['kernels']['rgm136']['sources_sha256'])} and rgm211 {len(k['kernels']['rgm211_host']['sources_sha256'])} "
              f"source files re-hashed, equal to E220's record; equal to kernel-e222.json: {same}")
        print("PASS" if same else "FAIL")
        sys.exit(0 if same else 1)
    json.dump(k, open(OUT, "w"), indent=1)
    print(f"kernel_e222: rgm136 ELF {k['kernels']['rgm136']['elf_sha256'][:16]}, .text {k['kernels']['rgm136']['text_sha256'][:16]}, "
          f"loadable {k['kernels']['rgm136']['loadable_identity_sha256'][:16]}; sources equal to E220's record")


if __name__ == "__main__":
    main()
