#!/usr/bin/env python3
"""E213 (Q216) desk: the kernels by path and sha256 - rgm136 (E136's binary, unchanged; every rgm136 gemmL and gemmLnc point of both arms) and
rgm211 (E211's second kernel, unchanged; arm A's rgm211 gemmLn and rgm211 gemmL points), every source file re-hashed and compared with E206's and
E211's registered records, the pins the kits gate on, and which host and ELF run each arm family. Standard library only.

    python3 -I -B tools/claims-v3/e213/desk/kernel_e213.py           writes ../kernel-e213.json
    python3 -I -B tools/claims-v3/e213/desk/kernel_e213.py --check   re-hashes the sources and compares with the committed kernel-e213.json (exit 0 = PASS)

THE ARM FAMILIES (E211's, and one more): gemmL on rgm136's host with rgm136's ELF (E206, E207, E211); gemmLn on rgm211's host with rgm211's ELF
(E211); gemmLnc on rgm211's host with rgm136's ELF (E211: no new device code); and, NEW in E213, rgm211's own gemmL loop - rgm211's host with
rgm211's ELF and the gemmL arm (arm A's a074, a078, a081, a085). E211's identity gate refused 'gemmL on rgm211' by design (its kit's gate-desktest:
'gemmL on rgm211 FAILED'): E213's kit must add this family's gate (rgm211's pins, the walk tag of a gemmL launch) before any datum, or those four
points are NO DATA by a dated amendment. Arm B runs rgm136's gemmL and gemmLnc only: rgm211's host is built on aifoundry1 for gemmLnc (no rgm211
device code on card 1); if arm B's kit cannot build and gate it, arm B's gemmLnc points (k37-k40) are NO DATA by a dated amendment before any datum.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
OUT = os.path.join(HERE, "..", "kernel-e213.json")
RGM136 = "tools/claims-v3/e136/rgm136"
RGM211 = "tools/claims-v3/e211/rgm211"
E206_KERNEL = ("tools/claims-v3/e206/kernel-e206.json", "5591ba0cc88289f471f5deb320cb772d2a4f362bbde360aa0d560d8d247ffc74")
E211_KERNEL = ("tools/claims-v3/e211/kernel-e211.json", "d2951e36f9b715540e41fe8e5a54c6463851eb8508d5de7b169561a1d7c65209")


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
        raise SystemExit(f"kernel_e213: {path} is {got}, registered {want}")
    return json.load(open(p))


def build():
    k6 = rec(*E206_KERNEL)
    k11 = rec(*E211_KERNEL)
    s136, s211 = tree(RGM136), tree(RGM211)
    eq136 = k6["source_sha256"] == s136 and k11["kernels"]["rgm136"]["sources_sha256"] == s136
    eq211 = k11["kernels"]["rgm211"]["sources_sha256"] == s211
    if not (eq136 and eq211):
        raise SystemExit("kernel_e213: a kernel's sources differ from the registered records")
    return {"experiment": "E213", "request": "Q216", "what": "E213's kernels by path and sha256, their pins and the arm families (desk)",
            "kernels": {
                "rgm136": {"tree": RGM136, "sources_sha256": s136, "equal_to": [E206_KERNEL[0], E211_KERNEL[0]],
                           "elf_sha256": "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0",
                           "text_sha256": "61315bf6a449c2823fbffc33834b4c0a68aa19e8436a29c1124b15c04114b763",
                           "loadable_identity_sha256": k11["kernels"]["rgm136"]["loadable_identity_sha256"],
                           "pins_note": ("E136's build record (aifoundry2's and aifoundry1's builds byte-identical: arm B gates on the whole ELF, as E206 arm "
                                         "B did); aifoundry3's GCC prints '(g1b306039a) 15.1.0' into the ELF, so arm A gates on the .text and the "
                                         "loadable identity (E191's kit fix; E206, E207 and E211 on aifoundry3)")},
                "rgm211": dict(k11["kernels"]["rgm211"], tree=RGM211, equal_to=[E211_KERNEL[0]],
                               pins_note=("E211's registration and kit (kit-e211 built it on aifoundry3 at its .text and loadable identity; E211 ran "
                                          "gemmLn on aifoundry3 card 0, data 38aaf004); arm A only"))},
            "arm_families": {
                "rgm136 gemmL": {"host": "rgm136", "elf": "rgm136", "arms": "gemmL<MB>x<NB>x<KB>", "where": "both arms", "gate": "E206's / E207's"},
                "rgm136 gemmLnc": {"host": "rgm211", "elf": "rgm136", "arms": "gemmLnc<MB>x<NB>x<KB>", "where": "both arms (arm B: k37-k40)",
                                   "gate": "E211's family C gate; arm B: built and gated on aifoundry1 by the kit, else NO DATA by amendment"},
                "rgm211 gemmLn": {"host": "rgm211", "elf": "rgm211", "arms": "gemmLn<MB>x<NB>x<KB>", "where": "arm A", "gate": "E211's"},
                "rgm211 gemmL": {"host": "rgm211", "elf": "rgm211", "arms": "gemmL<MB>x<NB>x<KB>", "where": "arm A (a074, a078, a081, a085)",
                                 "gate": "NEW: the kit adds it (rgm211's pins; a gemmL launch's walk tag), else NO DATA by amendment"}},
            "build": k11["build"],
            "host_arguments": ("--test fma --type <fmt> --pattern none --values <arm>:<gen>:<tiles> --shires <mask> --per-shire 32 --seconds 6 "
                               "--budget 7.5 --seed 1 (the kit adds --kernel, --stop-file and its absolute paths); gen randn, tiles or sparse50 "
                               "(E101's grammar); tiles under tools/claims-v3/kinds/tiles/")}


def main():
    k = build()
    if "--check" in sys.argv:
        old = json.load(open(OUT))
        same = old == json.loads(json.dumps(k))
        print(f"kernel_e213 --check: rgm136 {len(k['kernels']['rgm136']['sources_sha256'])} and rgm211 {len(k['kernels']['rgm211']['sources_sha256'])} "
              f"source files re-hashed, equal to E206's and E211's records; equal to kernel-e213.json: {same}")
        print("PASS" if same else "FAIL")
        sys.exit(0 if same else 1)
    json.dump(k, open(OUT, "w"), indent=1)
    for name in ("rgm136", "rgm211"):
        for p, h in k["kernels"][name]["sources_sha256"].items():
            print(h, p)


if __name__ == "__main__":
    main()
