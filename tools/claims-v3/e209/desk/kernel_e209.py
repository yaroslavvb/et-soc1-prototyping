#!/usr/bin/env python3
"""E209 (Q202) desk: the kernel by path and sha256 - rgm136 (E136's binary, unchanged; E206 and E208 ran it, E208 on this card), every source file's
sha256 at registration (equal to E206's record and to E208's committed kit copy, checked), and the build pin the kit gates on. Standard library only.

    python3 -I -B tools/claims-v3/e209/desk/kernel_e209.py           writes ../kernel-e209.json and prints desk/kernel-e209.txt's lines
    python3 -I -B tools/claims-v3/e209/desk/kernel_e209.py --check   re-hashes the sources and compares with the committed kernel-e209.json (exit 0 = PASS)

THE PINS: the kernel ELF aace138c... (E136's build record; aifoundry2's and aifoundry1's builds byte-identical; E208's kit gated its aifoundry2 build
on it) and its .text 61315bf6.... On aifoundry2 the ELF itself is the gate (E208's KERNEL_PIN). SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = "tools/claims-v3/e136/rgm136"
E208_COPY = "tools/claims-v3/e208/proposal/src/rgm136"
OUT = os.path.join(HERE, "..", "kernel-e209.json")
E206_KERNEL = ("tools/claims-v3/e206/kernel-e206.json", "5591ba0cc88289f471f5deb320cb772d2a4f362bbde360aa0d560d8d247ffc74")
ELF = "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0"


def h(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def build():
    files = {}
    for dp, dns, fns in os.walk(os.path.join(REPO, SRC)):
        dns.sort()
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            files[os.path.relpath(p, REPO)] = h(p)
    k6p = os.path.join(REPO, E206_KERNEL[0])
    k6 = json.load(open(k6p))
    same6 = h(k6p) == E206_KERNEL[1] and k6["source_sha256"] == dict(sorted(files.items()))
    copy = {}
    for rel in files:
        q = os.path.join(REPO, E208_COPY, os.path.relpath(rel, SRC))
        copy[rel] = os.path.exists(q) and h(q) == files[rel]
    same8 = all(copy.values())
    mc = open(os.path.join(REPO, "tools/claims-v3/e208/proposal/src/mms_common.py")).read()
    pin8 = f'KERNEL_PIN = "{ELF}"' in mc
    if not (same6 and same8 and pin8):
        raise SystemExit("kernel_e209: the rgm136 sources differ from E206's record or E208's copy, or E208's kernel pin is not E136's")
    return {"experiment": "E209", "kernel": "rgm136 (E136's, unchanged; E146, E158, E159, E168, E169, E190, E206 and E208 ran it; E208 on aifoundry2 card 0)",
            "source_dir": SRC, "source_sha256": dict(sorted(files.items())),
            "equal_to_e206_record": {"path": E206_KERNEL[0], "sha256": E206_KERNEL[1], "sources_equal": same6},
            "equal_to_e208_kit_copy": {"dir": E208_COPY, "files_equal": sum(copy.values()), "of": len(copy)},
            "kernel_elf_sha256": ELF, "kernel_elf_pin_source": "E136's build record; E208's kit (mms_common.KERNEL_PIN) gated its aifoundry2 build on it",
            "kernel_text_sha256": "61315bf6a449c2823fbffc33834b4c0a68aa19e8436a29c1124b15c04114b763",
            "arm_used": {"gemmL<MB>x<NB>x<KB>": "SP_GEMM_LARGE (E136): C (MB x NB blocks of 1,024 x 512) = A (MB x KB blocks) x B (KB x NB blocks); "
                                                "a shire mask runs the masked shires only (shire s: rows 128 (s >> 2), columns 128 (s & 3) of each C block)"},
            "host_arguments": "--test fma --type <fmt> --pattern none --values <arm>:<gen>:<tiles> --shires <mask> --per-shire 32 --seconds 6 "
                              "--budget 7.5 --seed 1 --kernel <ELF> --stop-file <file> (E208's host_argv); gen randn or tiles (E101's grammar)"}


def main():
    k = build()
    if "--check" in sys.argv:
        old = json.load(open(OUT))
        same = old == json.loads(json.dumps(k))
        print(f"kernel_e209 --check: {len(k['source_sha256'])} source files re-hashed; equal to E206's record: {k['equal_to_e206_record']['sources_equal']}; "
              f"equal to E208's kit copy: {k['equal_to_e208_kit_copy']['files_equal']} of {k['equal_to_e208_kit_copy']['of']}; equal to kernel-e209.json: {same}")
        print("PASS" if same else "FAIL")
        sys.exit(0 if same else 1)
    json.dump(k, open(OUT, "w"), indent=1)
    open(OUT, "a").write("\n")
    for p, x in k["source_sha256"].items():
        print(x, p)


if __name__ == "__main__":
    main()
