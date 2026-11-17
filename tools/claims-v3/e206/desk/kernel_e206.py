#!/usr/bin/env python3
"""E206 (Q198) desk: the kernel by path and sha256 - rgm136 (E136's binary, unchanged; E190 ran it), every source file's sha256 at registration, and
the build pins the kit gates on. Standard library only.

    python3 -I -B tools/claims-v3/e206/desk/kernel_e206.py           writes ../kernel-e206.json
    python3 -I -B tools/claims-v3/e206/desk/kernel_e206.py --check   re-hashes the sources and compares with the committed kernel-e206.json (exit 0 = PASS)

THE PINS (E136's build record and E190's kit, copied here): the kernel ELF aace138c... as built on aifoundry2 and aifoundry1 (byte-identical there);
its .text section 61315bf6.... aifoundry3's RISC-V GCC prints a different version string ('(g1b306039a) 15.1.0' against '() 15.1.0'), which lands in
the ELF, so arm A's kernel is gated on its .text (E191's kit fix); the host is gated by its behaviour (E190's four refusals). SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
SRC = "tools/claims-v3/e136/rgm136"
OUT = os.path.join(HERE, "..", "kernel-e206.json")


def build():
    files = {}
    for dp, dns, fns in os.walk(os.path.join(REPO, SRC)):
        dns.sort()
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            files[os.path.relpath(p, REPO)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return {"experiment": "E206", "kernel": "rgm136 (E136's, unchanged; E146, E158, E159, E168, E169 and E190 ran it)", "source_dir": SRC,
            "source_sha256": dict(sorted(files.items())),
            "kernel_elf_sha256": "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0",
            "kernel_elf_pin_source": "E136's build record; E190's kit (aifoundry2's and aifoundry1's builds byte-identical)",
            "kernel_text_sha256": "61315bf6a449c2823fbffc33834b4c0a68aa19e8436a29c1124b15c04114b763",
            "kernel_text_pin_source": "E190's kit (KIT.md); the gate for arm A's build on aifoundry3 (E191's kit fix)",
            "arms_used": {"gemmL<MB>x<NB>x<KB>": "SP_GEMM_LARGE (E136): C (MB x NB blocks of 1,024 x 512) = A (MB x KB blocks) x B (KB x NB blocks)",
                          "gemmc1 / gemmc8s / gemmc16s": "run_gemm's arms (rgm107's, in the same binary): one block; 8 blocks, C shared; 16 blocks, C shared"},
            "host_arguments": "--test fma --type <fmt> --pattern none --values <arm>:<kind>:<tiles> --shires <mask> --per-shire 32 --seconds 6 "
                              "--budget 7.5 --seed 1 (the kit adds --kernel, --stop-file and its absolute paths)"}


def main():
    k = build()
    if "--check" in sys.argv:
        old = json.load(open(OUT))
        same = old == json.loads(json.dumps(k))
        print(f"kernel_e206 --check: {len(k['source_sha256'])} source files re-hashed; equal to kernel-e206.json: {same}")
        print("PASS" if same else "FAIL")
        sys.exit(0 if same else 1)
    json.dump(k, open(OUT, "w"), indent=1)
    for p, h in k["source_sha256"].items():
        print(h, p)


if __name__ == "__main__":
    main()
