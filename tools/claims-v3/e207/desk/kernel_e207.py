#!/usr/bin/env python3
"""E207 (Q199) desk: the kernel by path and sha256 - rgm136 (E136's binary, unchanged; E206 arm A ran it on aifoundry3 card 0 on Mon 16 Nov 2026),
every source file's sha256 at registration (equal to E206's record, checked), and the build pins the kit gates on. Standard library only.

    python3 -I -B tools/claims-v3/e207/desk/kernel_e207.py           writes ../kernel-e207.json
    python3 -I -B tools/claims-v3/e207/desk/kernel_e207.py --check   re-hashes the sources and compares with the committed kernel-e207.json (exit 0 = PASS)

THE PINS (E136's build record and E190's kit, as E206 registered them): the kernel ELF aace138c... as built on aifoundry2 and aifoundry1; its .text
section 61315bf6.... aifoundry3's RISC-V GCC prints '(g1b306039a) 15.1.0' where aifoundry1's prints '() 15.1.0' and the string lands in the ELF, so
on aifoundry3 the kernel is gated on its .text (E191's kit fix, E206's kit). SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = "tools/claims-v3/e136/rgm136"
OUT = os.path.join(HERE, "..", "kernel-e207.json")
E206_KERNEL = ("tools/claims-v3/e206/kernel-e206.json", "5591ba0cc88289f471f5deb320cb772d2a4f362bbde360aa0d560d8d247ffc74")


def build():
    files = {}
    for dp, dns, fns in os.walk(os.path.join(REPO, SRC)):
        dns.sort()
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            files[os.path.relpath(p, REPO)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    k6p = os.path.join(REPO, E206_KERNEL[0])
    k6_sha = hashlib.sha256(open(k6p, "rb").read()).hexdigest()
    k6 = json.load(open(k6p))
    same = k6_sha == E206_KERNEL[1] and k6["source_sha256"] == dict(sorted(files.items()))
    if not same:
        raise SystemExit("kernel_e207: the rgm136 sources differ from E206's registered record")
    return {"experiment": "E207", "kernel": "rgm136 (E136's, unchanged; E146, E158, E159, E168, E169, E190 and E206 ran it; E206 arm A on aifoundry3 card 0)",
            "source_dir": SRC, "source_sha256": dict(sorted(files.items())),
            "equal_to_e206_record": {"path": E206_KERNEL[0], "sha256": E206_KERNEL[1], "sources_equal": same},
            "kernel_elf_sha256": "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0",
            "kernel_elf_pin_source": "E136's build record; E190's kit (aifoundry2's and aifoundry1's builds byte-identical)",
            "kernel_text_sha256": "61315bf6a449c2823fbffc33834b4c0a68aa19e8436a29c1124b15c04114b763",
            "kernel_text_pin_source": "E190's kit (KIT.md); the gate for aifoundry3's build (E191's kit fix; E206's kit on aifoundry3)",
            "arm_used": {"gemmL<MB>x<NB>x<KB>": "SP_GEMM_LARGE (E136): C (MB x NB blocks of 1,024 x 512) = A (MB x KB blocks) x B (KB x NB blocks); "
                                                "a shire mask runs the masked shires only (shire s: rows 128 (s >> 2), columns 128 (s & 3) of each C block)"},
            "host_arguments": "--test fma --type <fmt> --pattern none --values <arm>:<gen>:<tiles> --shires <mask> --per-shire 32 --seconds 6 "
                              "--budget 7.5 --seed 1 (the kit adds --kernel, --stop-file and its absolute paths); gen randn, e37 or tiles (E101's grammar)"}


def main():
    k = build()
    if "--check" in sys.argv:
        old = json.load(open(OUT))
        same = old == json.loads(json.dumps(k))
        print(f"kernel_e207 --check: {len(k['source_sha256'])} source files re-hashed; equal to E206's record: {k['equal_to_e206_record']['sources_equal']}; "
              f"equal to kernel-e207.json: {same}")
        print("PASS" if same else "FAIL")
        sys.exit(0 if same else 1)
    json.dump(k, open(OUT, "w"), indent=1)
    for p, h in k["source_sha256"].items():
        print(h, p)


if __name__ == "__main__":
    main()
