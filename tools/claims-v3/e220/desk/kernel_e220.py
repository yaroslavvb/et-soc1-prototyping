#!/usr/bin/env python3
"""E220 (Q233) desk: the kernel and hosts by path and sha256 - rgm136 (E136's binary, unchanged: every E220 point; its gemmL loop for families
XGt, XY, XF, L3, Y2, G2t, the tie t01 and the smoke s01, its gemmLnc branch for families XG and G2 and the smoke s03) and rgm211's host (E211's; it
runs rgm136's ELF for the gemmLnc branch, E211's family C gate) - every source file re-hashed and compared with E218's registered record (itself equal
to E215's, E213's, E211's and E206's), and which host and ELF run each arm family on each arm. Standard library only.

    python3 -I -B tools/claims-v3/e220/desk/kernel_e220.py           writes ../kernel-e220.json
    python3 -I -B tools/claims-v3/e220/desk/kernel_e220.py --check   re-hashes the sources and compares with kernel-e220.json (exit 0 = PASS)

The pins the kits gate on are E215 arm B's on aifoundry1 (the whole ELF and its .text, the pinned ones) and E216's on aifoundry2 (its build record);
the kit lane names them per arm. No new device code.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(HERE, "..", "kernel-e220.json")
RGM136 = "tools/claims-v3/e136/rgm136"
RGM211 = "tools/claims-v3/e211/rgm211"
E218_KERNEL = ("tools/claims-v3/e218/kernel-e218.json", "b8f83b80fbac0b4d3e339a69d558dc9cf7abb471fabce6237ccf9896f9ac110e")


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
        raise SystemExit(f"kernel_e220: {E218_KERNEL[0]} is {got}, registered {E218_KERNEL[1]}")
    k18 = json.load(open(p))
    s136, s211 = tree(RGM136), tree(RGM211)
    if k18["kernels"]["rgm136"]["sources_sha256"] != s136 or k18["kernels"]["rgm211_host"]["sources_sha256"] != s211:
        raise SystemExit("kernel_e220: a kernel's sources differ from E218's registered record")
    pts = json.load(open(os.path.join(HERE, "..", "points-e220.json")))["points"]
    where = {}
    for arm in ("A", "B"):
        for q in pts[arm]:
            where.setdefault(q["loop"], {}).setdefault(arm, []).append(q["id"])
    r136 = dict(k18["kernels"]["rgm136"])
    r136["equal_to"] = [E218_KERNEL[0]] + list(k18["kernels"]["rgm136"].get("equal_to", []))
    r211 = dict(k18["kernels"]["rgm211_host"])
    r211["role_in_E220"] = "its host only: it runs rgm136's ELF for the gemmLnc branch (families XG and G2, the smoke s03); rgm211's own ELF runs no E220 point"
    k = {"experiment": "E220", "request": "Q233", "what": "E220's kernel and hosts by path and sha256 and the arm families per arm (desk)",
         "kernels": {"rgm136": r136, "rgm211_host": r211},
         "arm_families": {
             "rgm136 gemmL": {"host": "rgm136", "elf": "rgm136", "arms": "gemmL<MB>x<NB>x<KB>", "points": where.get("rgm136 gemmL", {}),
                              "also": ["t01 (tie)", "s01 (smoke, the session gate)"]},
             "rgm136 gemmLnc": {"host": "rgm211", "elf": "rgm136", "arms": "gemmLnc<MB>x<NB>x<KB>", "points": where.get("rgm136 gemmLnc", {}),
                                "also": ["s03 (smoke, the G block's gate and stop path)"],
                                "gate": "E211's family C gate (E213 arm B and E215 arm B ran it on aifoundry1 card 1; E216 on aifoundry2 card 0)"}},
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
        print(f"kernel_e220 --check: rgm136 {len(k['kernels']['rgm136']['sources_sha256'])} and rgm211 {len(k['kernels']['rgm211_host']['sources_sha256'])} "
              f"source files re-hashed, equal to E218's record; equal to kernel-e220.json: {same}")
        print("PASS" if same else "FAIL")
        sys.exit(0 if same else 1)
    json.dump(k, open(OUT, "w"), indent=1)
    print(f"kernel_e220: rgm136 ELF {k['kernels']['rgm136']['elf_sha256'][:16]}, .text {k['kernels']['rgm136']['text_sha256'][:16]}, "
          f"loadable {k['kernels']['rgm136']['loadable_identity_sha256'][:16]}; sources equal to E218's record")


if __name__ == "__main__":
    main()
