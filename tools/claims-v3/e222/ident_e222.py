#!/usr/bin/env python3
"""E222's kit (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum; E218's landed kit 5582edfc ported, the kit that ran E218 FULL on aifoundry3 card 0 at 03:11-03:56 PST that day): THE IDENTITY GATE PER ARM FAMILY, E215 arm A's gate
(tools/claims-v3/e215/ident_e215.py, landed in 8bde0182: run before every process of E215 arm A's session on aifoundry3 card 0 on Thu 19 Nov 2026, 123 of 123
GATE OK; E211's gate, tools/claims-v3/e211/ident_e211.py, behind it) keyed by E222's two families (kernel-e222.json > arm_families; a point's
"loop"), both of which run rgm136's ELF. A kernel ELF passes for a family when its .text sha256 (objcopy -O binary -j .text, E206's recipe) equals
rgm136's .text pin AND either its whole ELF equals rgm136's ELF pin or its LOADABLE IDENTITY (E206's check_e206.py elf_identity: every byte and
header the card's loader can read and nothing else) equals rgm136's identity pin. aifoundry3's riscv gcc prints "(g1b306039a) 15.1.0" into
.comment, a section the card never loads, so on aifoundry3 the identity branch is the one that passes (E215 arm A's gate words read "GATE OK:
rgm136 gemmL ... the pinned one").

    family            ELF       host      where
    rgm136 gemmL      rgm136    rgm136    T-L3, T-Y2, T-G2t, L3b, Y3, G3t, R's ry01a, ry01b, rg01t, the tie t01 and the session's smoke s01
                                          (E206's, E207's, E215's and E218's gate)
    rgm136 gemmLnc    rgm136    rgm211    R's rg01, T-G2 (wn01-wn07), G3 (k01-k07) and their smoke s03 (E211's family C; E213 arm A's,
                                          E215 arm A's and E218's on this card)

THE TREE GATE (the build only, never a process gate): rgm211's tree (tools/claims-v3/e211/rgm211, E211's, unchanged) is built for its HOST, which
runs rgm136's ELF for the gemmLnc branch; its own ELF runs no E222 point (kernel-e222.json "rgm211_host": "its host only"). The build reads that
ELF all the same - its whole ELF at kernel-e222.json's rgm211_host ELF pin or its loadable identity at that entry's identity pin - so the tree the
host comes from is shown to be E211's on the box's toolchain (E213 arm A's and E215 arm A's builds there read the same pins).

    python3 -I -B tools/claims-v3/e222/ident_e222.py --identity <elf>                     ELF, .text and loadable-identity sha256 of one ELF
    python3 -I -B tools/claims-v3/e222/ident_e222.py --gate "<family>" <elf>              GATE OK: ... (exit 0) or GATE FAILED: <why> (exit 1)
    python3 -I -B tools/claims-v3/e222/ident_e222.py --tree rgm211 <elf>                  TREE OK: ... (exit 0) or TREE FAILED: <why> (exit 1)
    python3 -I -B tools/claims-v3/e222/ident_e222.py --check                              the pins against kernel-e222.json, E206's and E211's

The runner gates every process of the session on its point's family before it starts and records the gate's words with the run. For the gemmLnc
family rgm211's host runs, a wrong ELF (rgm211's own, say) would read walk mn, tag 0, like rgm136's (neither tags a gemmLnc launch): THIS GATE is
the only refusal of a wrong ELF there. Standard library only (E206's check_e206.py imported, pinned by sha256).
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
        sys.exit(f"ident_e222: {_rel} is {_got}, pinned {_want}")
sys.path.insert(0, E206)
import check_e206 as CK  # noqa: E402

FAMILY_KERNEL = {"rgm136 gemmL": "rgm136", "rgm136 gemmLnc": "rgm136"}
TREES = {"rgm211": "rgm211_host"}        # the build's tree gate: kernel-e222.json > kernels > rgm211_host


def kernels():
    return json.load(open(os.path.join(HERE, "kernel-e222.json")))["kernels"]


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
    """(ok, words): the ELF passes for the family (the module docstring); whole=True requires the whole ELF at its pin (no E222 caller sets it:
    aifoundry3's builds pass by the loadable identity)."""
    if family not in FAMILY_KERNEL:
        return False, f"no arm family {family!r} ({', '.join(FAMILY_KERNEL)})"
    if not os.path.isfile(elf):
        return False, f"no kernel at {elf}"
    want = FAMILY_KERNEL[family]
    pe, pt, pl = pins(want)
    got = identity(elf)
    if got["text_sha256"] != pt:
        ks = kernels()
        others = [k for k in ks if ks[k].get("text_sha256") == got["text_sha256"]]
        t211 = "82c7980716a0f0cacd24364ef9a23435343eb8f2c35c32b0ec5d60b46c8a4069"      # rgm211's .text (E211's kernel-e211.json; --check reads it)
        return False, (f"{family} needs {want}'s .text {pt[:16]}...; this ELF's .text is {got['text_sha256']}"
                       + (f" ({others[0]}'s)" if others else " (rgm211's)" if got["text_sha256"] == t211 else ""))
    if got["elf_sha256"] == pe:
        return True, f"{family}: {want}, .text {pt[:16]}... and the whole ELF {pe[:16]}... the pinned ones"
    if whole:
        return False, (f"{family}: .text {want}'s, but the whole ELF {pe} is required, and this ELF is "
                       f"{got['elf_sha256']} (its loadable identity {got['loadable_identity_sha256']})")
    if got["loadable_identity_sha256"] == pl:
        return True, (f"{family}: {want}, .text {pt[:16]}... the pinned one; ELF {got['elf_sha256'][:16]}... not the desk build's (sections the card "
                      f"never loads differ), its loadable identity {pl[:16]}... the pinned one")
    return False, (f"{family}: .text {want}'s, but the ELF {got['elf_sha256']} is not the pinned {pe} and its loadable identity "
                   f"{got['loadable_identity_sha256']} is not the pinned {pl}")


def tree_gate(tree, elf):
    """(ok, words): the build's tree gate on the rgm211 tree's own ELF (never a process gate: that ELF runs no E222 point): its whole ELF at
    kernel-e222.json's rgm211_host ELF pin, or its loadable identity at that entry's identity pin."""
    if tree not in TREES:
        return False, f"no tree {tree!r} ({', '.join(TREES)})"
    if not os.path.isfile(elf):
        return False, f"no ELF at {elf}"
    k = kernels()[TREES[tree]]
    pe, pl = k["elf_sha256"], k["loadable_identity_sha256"]
    got = identity(elf)
    if got["elf_sha256"] == pe:
        return True, f"{tree}'s tree: its ELF {pe[:16]}... the pinned one (kernel-e222.json's {TREES[tree]})"
    if got["loadable_identity_sha256"] == pl:
        return True, (f"{tree}'s tree: its ELF {got['elf_sha256'][:16]}... not the desk build's (sections the card never loads differ), its loadable "
                      f"identity {pl[:16]}... the pinned one (kernel-e222.json's {TREES[tree]})")
    return False, (f"{tree}'s tree: its ELF {got['elf_sha256']} is not the pinned {pe} and its loadable identity {got['loadable_identity_sha256']} "
                   f"is not the pinned {pl}")


def check():
    ok = True
    e, t, li = pins("rgm136")
    for name, mine, theirs in (("ELF", e, CK.KERNEL_PIN), (".text", t, CK.TEXT_PIN), ("loadable identity", li, CK.LOAD_PIN)):
        same = mine == theirs
        ok &= same
        print(f"rgm136 {name}: kernel-e222.json {mine[:16]}... E206's {theirs[:16]}...: {'SAME' if same else 'DIFFERS'}")
    k2 = kernels()["rgm211_host"]
    e211 = json.load(open(os.path.join(REPO, "tools/claims-v3/e211/kernel-e211.json")))["kernels"]["rgm211"]
    same211 = (k2["elf_sha256"], k2["loadable_identity_sha256"]) == (e211["elf_sha256"], e211["loadable_identity_sha256"]) and \
        e211["text_sha256"] == "82c7980716a0f0cacd24364ef9a23435343eb8f2c35c32b0ec5d60b46c8a4069"
    distinct = len({li, k2["loadable_identity_sha256"]}) == 2 and len({t, e211["text_sha256"]}) == 2
    ok &= same211 and distinct
    print(f"rgm211's tree pins (kernel-e222.json rgm211_host): ELF {k2['elf_sha256'][:16]}... identity {k2['loadable_identity_sha256'][:16]}...; "
          f"E211's kernel-e211.json's: {same211}; distinct from rgm136's: {distinct}")
    fams = json.load(open(os.path.join(HERE, "kernel-e222.json")))["arm_families"]
    same_f = all(fams[f]["elf"] == k for f, k in FAMILY_KERNEL.items()) and set(fams) == set(FAMILY_KERNEL)
    ok &= same_f
    print(f"the two families' ELFs as kernel-e222.json names them (both rgm136's): {same_f}")
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
    if argv[:1] == ["--tree"] and len(argv) == 3:
        good, words = tree_gate(argv[1], argv[2])
        print(("TREE OK: " if good else "TREE FAILED: ") + words)
        return 0 if good else 1
    if argv[:1] == ["--check"]:
        return check()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
