#!/usr/bin/env python3
"""E215 (Q224) desk: the kernels by path and sha256 - rgm136 (E136's binary, unchanged: every rgm136 gemmL and gemmLnc point of both arms) and
rgm211 (E211's second kernel, unchanged: the rgm211 gemmLn and rgm211 gemmL points), every source file re-hashed and compared with E206's, E211's
and E213's registered records, the pins the kits gate on, and which host and ELF run each arm family. Standard library only.

    python3 -I -B tools/claims-v3/e215/desk/kernel_e215.py           writes ../kernel-e215.json
    python3 -I -B tools/claims-v3/e215/desk/kernel_e215.py --check   re-hashes the sources and compares with the committed kernel-e215.json (exit 0 = PASS)

THE ARM FAMILIES (E211's and E213's): gemmL on rgm136's host with rgm136's ELF; gemmLn on rgm211's host with rgm211's ELF; gemmLnc on rgm211's host
with rgm136's ELF (no new device code); rgm211's own gemmL loop on rgm211's host with rgm211's ELF (E213 arm A ran it on aifoundry3: its family
smoke s04 and four points). NEW IN E215: rgm211's ELF on aifoundry1 card 1 (arm B's rgm211 gemmLn points) - it never ran on card 1; arm B's kit
builds rgm211 on aifoundry1 and gates every process of that family by E211's identity (the ELF's sha256 where the build is byte-identical to the
desk build, else its .text and loadable identity); if the kit cannot build and gate it before any datum, arm B's rgm211 points are NO DATA by a
dated amendment (E215.md section 2); arm B's gemmLnc point runs rgm211's host with rgm136's ELF as E213 arm B did.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(HERE, "..", "kernel-e215.json")
RGM136 = "tools/claims-v3/e136/rgm136"
RGM211 = "tools/claims-v3/e211/rgm211"
E206_KERNEL = ("tools/claims-v3/e206/kernel-e206.json", "5591ba0cc88289f471f5deb320cb772d2a4f362bbde360aa0d560d8d247ffc74")
E211_KERNEL = ("tools/claims-v3/e211/kernel-e211.json", "d2951e36f9b715540e41fe8e5a54c6463851eb8508d5de7b169561a1d7c65209")
E213_KERNEL = ("tools/claims-v3/e213/kernel-e213.json", "b2f1358ff90c518157dfed8aed1d996f23c5e05dd55dee67175862049d12ffe0")


def tree(rel):
    files = {}
    for dp, dns, fns in os.walk(os.path.join(REPO, rel)):
        dns.sort()
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            files[os.path.relpath(p, REPO)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return dict(sorted(files.items()))


def rec(path, want):
    p = os.path.join(REPO, path)
    got = hashlib.sha256(open(p, "rb").read()).hexdigest()
    if got != want:
        raise SystemExit(f"kernel_e215: {path} is {got}, registered {want}")
    return json.load(open(p))


def build():
    k6 = rec(*E206_KERNEL)
    k11 = rec(*E211_KERNEL)
    k13 = rec(*E213_KERNEL)
    s136, s211 = tree(RGM136), tree(RGM211)
    eq136 = k6["source_sha256"] == s136 and k11["kernels"]["rgm136"]["sources_sha256"] == s136 and k13["kernels"]["rgm136"]["sources_sha256"] == s136
    eq211 = k11["kernels"]["rgm211"]["sources_sha256"] == s211 and k13["kernels"]["rgm211"]["sources_sha256"] == s211
    if not (eq136 and eq211):
        raise SystemExit("kernel_e215: a kernel's sources differ from the registered records")
    pts = json.load(open(os.path.join(HERE, "..", "points-e215.json")))["arms"]
    where = {}
    for tag in ("A", "B"):
        for p in pts[tag]["points"]:
            where.setdefault(p["loop"], {}).setdefault(tag, []).append(p["id"])
    k = {"experiment": "E215", "request": "Q224", "what": "E215's kernels by path and sha256, their pins and the arm families (desk)",
         "kernels": {"rgm136": dict(k13["kernels"]["rgm136"], equal_to=[E206_KERNEL[0], E211_KERNEL[0], E213_KERNEL[0]]),
                     "rgm211": dict(k13["kernels"]["rgm211"], equal_to=[E211_KERNEL[0], E213_KERNEL[0]],
                                    pins_note=("E211's registration and kit (kit-e211 built it on aifoundry3 at its .text and loadable identity; E211 and "
                                               "E213 arm A ran it on aifoundry3 card 0); NEW in E215: arm B runs rgm211's ELF on aifoundry1 card 1, built "
                                               "there by its kit and gated by E211's identity (the whole ELF where byte-identical to the desk build, as "
                                               "rgm136's aifoundry1 build was; else its .text and loadable identity)"))},
         "arm_families": {
             "rgm136 gemmL": {"host": "rgm136", "elf": "rgm136", "arms": "gemmL<MB>x<NB>x<KB>", "points": where.get("rgm136 gemmL", {}),
                              "gate": "E206's / E207's / E213's"},
             "rgm136 gemmLnc": {"host": "rgm211", "elf": "rgm136", "arms": "gemmLnc<MB>x<NB>x<KB>", "points": where.get("rgm136 gemmLnc", {}),
                                "gate": "E211's family C gate (E213 arm A on aifoundry3; E213 arm B built rgm211's host on aifoundry1 and gated it)"},
             "rgm211 gemmLn": {"host": "rgm211", "elf": "rgm211", "arms": "gemmLn<MB>x<NB>x<KB>", "points": where.get("rgm211 gemmLn", {}),
                               "gate": "E211's (aifoundry3); on aifoundry1 NEW: the kit builds and gates rgm211's ELF, else arm B's points NO DATA by amendment"},
             "rgm211 gemmL": {"host": "rgm211", "elf": "rgm211", "arms": "gemmL<MB>x<NB>x<KB>", "points": where.get("rgm211 gemmL", {}),
                              "gate": "E213's (its Amendment A1 family gate and smoke s04)"}},
         "build": k13["build"],
         "host_arguments": ("--test fma --type <fmt> --pattern none --values <arm>:<gen>:<tiles> --shires <mask> --per-shire 32 --seconds 6 "
                            "--budget 7.5 --seed 1 (the kit adds --kernel, --stop-file and its absolute paths); gen randn, tiles or e37 (E101's "
                            "grammar, as E207 and E212 ran the S kinds); tiles under tools/claims-v3/kinds/ and tools/claims-v3/e212/proposal/src/tiles/")}
    return k


def main():
    k = build()
    if "--check" in sys.argv:
        old = json.load(open(OUT))
        same = old == json.loads(json.dumps(k))
        print(f"kernel_e215 --check: rgm136 {len(k['kernels']['rgm136']['sources_sha256'])} and rgm211 {len(k['kernels']['rgm211']['sources_sha256'])} "
              f"source files re-hashed, equal to E206's, E211's and E213's records; equal to kernel-e215.json: {same}")
        print("PASS" if same else "FAIL")
        sys.exit(0 if same else 1)
    json.dump(k, open(OUT, "w"), indent=1)
    for name in ("rgm136", "rgm211"):
        for p, h in k["kernels"][name]["sources_sha256"].items():
            print(h, p)


if __name__ == "__main__":
    main()
