#!/usr/bin/env python3
"""E213's kit (Q216, lane kit-e213, Tue 17 Nov 2026, before any E213 datum): THE IDENTITY GATE PER ARM FAMILY, E211's gate
(tools/claims-v3/e211/ident_e211.py, landed in 1393a649; run before every process of E211's session on aifoundry3, 41 of 41 GATE OK) keyed by
E213's four families (kernel-e213.json > arm_families; a point's "loop"), with the fourth family new: "rgm211 gemmL", rgm211's own copy of gemmL's
walk, gated on rgm211's pins (E211's gate refused 'gemmL on rgm211' by design; the orchestrator's answer of 21:27 PST Tue 17 Nov 2026 keeps
those four points if every process is gated by its ELF's .text and loadable identity, the family pinned as its own, and a desk test shows a wrong
ELF refused for it). A kernel ELF passes for a family when its .text sha256 (objcopy -O binary -j .text, E206's recipe) equals that family's
ELF's .text pin AND either its whole ELF equals the ELF pin or its LOADABLE IDENTITY (E206's check_e206.py elf_identity: every byte and header
the card's loader can read and nothing else) equals the identity pin. ON ARM B (aifoundry1 card 1) the whole ELF is required (E213.md 2: "arm B
gates on the whole ELF, as E206 arm B did": aifoundry1's riscv gcc prints "() 15.1.0", as this desk's, and its rgm136 build reached the whole-ELF
pin in E206 arm B); on arm A (aifoundry3, whose gcc prints "(g1b306039a) 15.1.0" into .comment) the identity branch is the one that passes.

    family            ELF       host      where
    rgm136 gemmL      rgm136    rgm136    both arms (E206's and E207's gate)
    rgm136 gemmLnc    rgm136    rgm211    both arms (E211's family C; arm B's k37-k40 and smoke s14: no new device code)
    rgm211 gemmLn     rgm211    rgm211    arm A (E211's)
    rgm211 gemmL      rgm211    rgm211    arm A (NEW: a074, a078, a081, a085)

    python3 -I -B tools/claims-v3/e213/ident_e213.py --identity <elf>                     ELF, .text and loadable-identity sha256 of one ELF
    python3 -I -B tools/claims-v3/e213/ident_e213.py --gate "<family>" <elf> [--whole]    GATE OK: ... (exit 0) or GATE FAILED: <why> (exit 1)
    python3 -I -B tools/claims-v3/e213/ident_e213.py --check                              the pins against kernel-e213.json and E206's

The runner gates every process of the session on its point's family before it starts and records the gate's words with the run. For the
families rgm211's host runs, a wrong ELF that somehow passed would also meet the host's walk check, but only for 'rgm211 gemmLn' (rgm136's ELF
writes no walk tag): for 'rgm136 gemmLnc' and 'rgm211 gemmL' neither ELF tags a launch, so THIS GATE is the only refusal of a wrong ELF there.
Standard library only (E206's check_e206.py imported, pinned by sha256).
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
        sys.exit(f"ident_e213: {_rel} is {_got}, pinned {_want}")
sys.path.insert(0, E206)
import check_e206 as CK  # noqa: E402

FAMILY_KERNEL = {"rgm136 gemmL": "rgm136", "rgm136 gemmLnc": "rgm136", "rgm211 gemmLn": "rgm211", "rgm211 gemmL": "rgm211"}


def kernels():
    return json.load(open(os.path.join(HERE, "kernel-e213.json")))["kernels"]


def pins(kernel):
    k = kernels()[kernel]
    return k["elf_sha256"], k["text_sha256"], k["loadable_identity_sha256"]


def identity(elf):
    e = hashlib.sha256(open(elf, "rb").read()).hexdigest()
    t = CK.text_sha(elf)
    ident, why = CK.elf_identity(elf)
    li = CK.identity_sha(ident) if ident is not None else None
    return {"elf_sha256": e, "text_sha256": t, "loadable_identity_sha256": li, "why": why or ""}


def gate(family, elf, whole=False):
    """(ok, words): the ELF passes for the family (the module docstring); whole=True (arm B) requires the whole ELF at its pin."""
    if family not in FAMILY_KERNEL:
        return False, f"no arm family {family!r} ({', '.join(FAMILY_KERNEL)})"
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
    if whole:
        return False, (f"{family}: .text {want}'s, but arm B requires the whole ELF {pe} (E206 arm B's gate), and this ELF is "
                       f"{got['elf_sha256']} (its loadable identity {got['loadable_identity_sha256']})")
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
        print(f"rgm136 {name}: kernel-e213.json {mine[:16]}... E206's {theirs[:16]}...: {'SAME' if same else 'DIFFERS'}")
    e2, t2, l2 = pins("rgm211")
    e211 = json.load(open(os.path.join(REPO, "tools/claims-v3/e211/kernel-e211.json")))["kernels"]["rgm211"]
    same211 = (e2, t2, l2) == (e211["elf_sha256"], e211["text_sha256"], e211["loadable_identity_sha256"])
    distinct = len({t, t2}) == 2 and len({li, l2}) == 2
    ok &= same211 and distinct
    print(f"rgm211 pins: ELF {e2[:16]}... .text {t2[:16]}... identity {l2[:16]}...; E211's kernel-e211.json's: {same211}; distinct from rgm136's: {distinct}")
    fams = json.load(open(os.path.join(HERE, "kernel-e213.json")))["arm_families"]
    same_f = all(fams[f]["elf"] == k for f, k in FAMILY_KERNEL.items()) and set(fams) == set(FAMILY_KERNEL)
    ok &= same_f
    print(f"the four families' ELFs as kernel-e213.json names them: {same_f}")
    print("CHECK PASS" if ok else "CHECK FAILED")
    return 0 if ok else 1


def main(argv):
    if argv[:1] == ["--identity"] and len(argv) == 2:
        print(json.dumps(identity(argv[1]), indent=1))
        return 0
    if argv[:1] == ["--gate"] and len(argv) in (3, 4):
        if len(argv) == 4 and argv[3] != "--whole":
            print(__doc__)
            return 2
        good, words = gate(argv[1], argv[2], whole=len(argv) == 4)
        print(("GATE OK: " if good else "GATE FAILED: ") + words)
        return 0 if good else 1
    if argv[:1] == ["--check"]:
        return check()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
