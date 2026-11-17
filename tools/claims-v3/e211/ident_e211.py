#!/usr/bin/env python3
"""E211 (Q204): THE IDENTITY GATE PER ARM FAMILY (critic-kernel2 fixes 2 and 6), on E206's kernel-gate code. A kernel ELF passes for an arm
family when its .text sha256 (objcopy -O binary -j .text, E206's recipe) equals that family's .text pin AND either its whole ELF equals the
family's ELF pin (a build on a box whose RISC-V gcc prints "() 15.1.0") or its LOADABLE IDENTITY (E206's check_e206.py elf_identity, the second
form of check_e191.py: every byte and header the card's loader can read and nothing else) equals the family's identity pin. The families:

    gemmL   rgm136's ELF (E136's pin, E206's .text and identity pins)          the twins, run by rgm136's own host (E206's and E207's build)
    gemmLn  rgm211's ELF (this registration's desk build; identity re-derived on aifoundry3 by the kit, which must equal these pins)
    gemmLnc rgm136's ELF                                                       run by rgm211's host (--kernel rgm136's ELF): no new device code

    python3 -I -B tools/claims-v3/e211/ident_e211.py --identity <elf>           ELF, .text and loadable-identity sha256 of one ELF
    python3 -I -B tools/claims-v3/e211/ident_e211.py --gate <family> <elf>      GATE OK: ... (exit 0) or GATE FAILED: <why> (exit 1)
    python3 -I -B tools/claims-v3/e211/ident_e211.py --check                    the pins against kernel-e211.json and rgm136's against E206's

Every process of the session is gated by the runner on its arm's family before it starts, and the gate's words are recorded with the run. A
wrong --kernel (a gemmLn process given rgm136's ELF) fails here; if it ever reached the card it would also fail the host's walk check (rgm211's
host: walk_ok false, exit 1). Standard library only (E206's check_e206.py and e206_common.py imported, pinned by sha256).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
E206 = os.path.join(REPO, "tools", "claims-v3", "e206")
PIN_E206 = {"tools/claims-v3/e206/check_e206.py": "fdbd35a63aa6b681322d228d8a50ecaadc70ae76bff51a9f0a57a6869d2b5a7d"}
for _rel, _want in PIN_E206.items():
    _got = hashlib.sha256(open(os.path.join(REPO, _rel), "rb").read()).hexdigest()
    if _got != _want:
        sys.exit(f"ident_e211: {_rel} is {_got}, pinned {_want}")
sys.path.insert(0, E206)
import check_e206 as CK  # noqa: E402

FAMILY_KERNEL = {"gemmL": "rgm136", "gemmLn": "rgm211", "gemmLnc": "rgm136"}


def kernels():
    return json.load(open(os.path.join(HERE, "kernel-e211.json")))["kernels"]


def pins(kernel):
    k = kernels()[kernel]
    return k["elf_sha256"], k["text_sha256"], k["loadable_identity_sha256"]


def identity(elf):
    e = hashlib.sha256(open(elf, "rb").read()).hexdigest()
    t = CK.text_sha(elf)
    ident, why = CK.elf_identity(elf)
    li = CK.identity_sha(ident) if ident is not None else None
    return {"elf_sha256": e, "text_sha256": t, "loadable_identity_sha256": li, "why": why or ""}


def family_of(arm):
    for fam in ("gemmLnc", "gemmLn", "gemmL"):   # longest prefix first
        if arm.startswith(fam):
            return fam
    return None


def gate(family, elf):
    if family not in FAMILY_KERNEL:
        return False, f"no arm family {family!r} (gemmL, gemmLn, gemmLnc)"
    if not os.path.isfile(elf):
        return False, f"no kernel at {elf}"
    want = FAMILY_KERNEL[family]
    pe, pt, pl = pins(want)
    got = identity(elf)
    if got["text_sha256"] != pt:
        ks = kernels()
        others = [k for k in ks if ks[k]["text_sha256"] == got["text_sha256"]]
        return False, (f"{family} needs {want}'s .text {pt[:16]}...; this ELF's .text is {got['text_sha256']}"
                       + (f" ({others[0]}'s)" if others else ""))
    if got["elf_sha256"] == pe:
        return True, f"{family}: {want}, .text {pt[:16]}... and the whole ELF {pe[:16]}... the pinned ones"
    if got["loadable_identity_sha256"] == pl:
        return True, (f"{family}: {want}, .text {pt[:16]}... the pinned one; ELF {got['elf_sha256'][:16]}... not the desk build's (sections the card "
                      f"never loads differ), its loadable identity {pl[:16]}... the pinned one")
    return False, (f"{family}: .text {want}'s, but the ELF {got['elf_sha256']} is not the pinned {pe} and its loadable identity "
                   f"{got['loadable_identity_sha256']} is not the pinned {pl}")


def check():
    ok = True
    e, t, li = pins("rgm136")
    for name, mine, theirs in (("ELF", e, CK.KERNEL_PIN), (".text", t, CK.TEXT_PIN), ("loadable identity", li, CK.LOAD_PIN)):
        same = mine == theirs
        ok &= same
        print(f"rgm136 {name}: kernel-e211.json {mine[:16]}... E206's {theirs[:16]}...: {'SAME' if same else 'DIFFERS'}")
    e2, t2, l2 = pins("rgm211")
    distinct = len({t, t2}) == 2 and len({li, l2}) == 2
    ok &= distinct
    print(f"rgm211 pins: ELF {e2[:16]}... .text {t2[:16]}... identity {l2[:16]}...; distinct from rgm136's: {distinct}")
    print("CHECK PASS" if ok else "CHECK FAILED")
    return 0 if ok else 1


def main(argv):
    if argv[:1] == ["--identity"] and len(argv) == 2:
        print(json.dumps(identity(argv[1]), indent=1))
        return 0
    if argv[:1] == ["--gate"] and len(argv) == 3:
        good, words = gate(argv[1], argv[2])
        print(("GATE OK: " if good else "GATE FAILED: ") + words)
        return 0 if good else 1
    if argv[:1] == ["--check"]:
        return check()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
