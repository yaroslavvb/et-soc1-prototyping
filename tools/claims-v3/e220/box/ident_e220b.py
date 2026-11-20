#!/usr/bin/env python3
"""E220's kit (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): THE IDENTITY GATE PER PROCESS, by the process's family. E211's
gate (tools/claims-v3/e211/ident_e211.py) as E215 keyed it by family (tools/claims-v3/e215/ident_e215.py, landed 8bde0182), with E220's two
families and E220's pins (kernel-e220.json, equal to E215's record). A kernel ELF passes for a family when its .text sha256 (objcopy -O binary
-j .text, E206's recipe) equals the family's ELF's .text pin AND its WHOLE ELF equals the ELF pin: on aifoundry2 the whole ELF is the gate
(this box's riscv gcc builds rgm136's ELF at E136's pin aace138c..., E208's and E209's gate on this card; E215 arm B's form). The loadable
identity (E206's check_e206.elf_identity) is read and recorded beside it, never taken in place of the whole ELF here.

    family            ELF       host      E220's points
    rgm136 gemmL      rgm136    rgm136    families Gt, Y, F, the smoke and the anchors (E208's host, E208's runner path)
    rgm136 gemmLnc    rgm136    rgm211    family G (E211's family C: rgm136's gemmLnc branch through rgm211's host)

No rgm211 ELF runs in E220 (kernel-e220.json > kernels > rgm211_host > role_in_E220): the rgm211 pins are read only to name an ELF that is refused.
The runner (src/run_e220b.py) gates every process of the session on its family right before it starts and records the gate's words; for
'rgm136 gemmLnc' neither ELF writes a walk tag on a gemmLnc launch, so THIS GATE is the only refusal of a wrong ELF there (E215's note).

    python3 -I -B src/ident_e220b.py --identity <elf>                    ELF, .text and loadable-identity sha256 of one ELF
    python3 -I -B src/ident_e220b.py --gate "<family>" <elf>             GATE OK: ... (exit 0) or GATE FAILED: <why> (exit 1)
    python3 -I -B src/ident_e220b.py --check                             the pins against kernel-e220.json and E206's checker: CHECK PASS

Where it reads from: beside it in the box root (src/), kernel-e220.json and E206's checker src/e206/check_e206.py with its module
src/e206/e206_common.py, each pinned by sha256 here (the lab's tools/claims-v3/e206/ files, copied by make_box_e220b.py). Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E206_DIR = os.path.join(HERE, "e206")
PINS = {"e206/check_e206.py": "fdbd35a63aa6b681322d228d8a50ecaadc70ae76bff51a9f0a57a6869d2b5a7d",
        "e206/e206_common.py": "9278e1f1eca268a6f815b7d7514dd0c01a24ea13835796946142db2c8fb6d79d",
        "kernel-e220.json": "f332b03a9f30aee15ba465c8c497ee31a2cfc758bcb91a6ae10ed8453e54338e"}
FAMILY_KERNEL = {"rgm136 gemmL": "rgm136", "rgm136 gemmLnc": "rgm136"}
FAMILY_HOST = {"rgm136 gemmL": "rgm136", "rgm136 gemmLnc": "rgm211"}


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _pins_ok():
    bad = []
    for rel, want in PINS.items():
        p = os.path.join(HERE, rel)
        got = _sha(p) if os.path.isfile(p) else "missing"
        if got != want:
            bad.append(f"{rel} is {got}, pinned {want}")
    return bad


_bad = _pins_ok()
if _bad:
    sys.exit("ident_e220b: " + "; ".join(_bad))
sys.path.insert(0, E206_DIR)
import check_e206 as CK  # noqa: E402


RGM211_TEXT_E211 = "82c7980716a0f0cacd24364ef9a23435343eb8f2c35c32b0ec5d60b46c8a4069"   # E211's .text pin of rgm211's ELF (kernel-e211.json)


def kernels():
    """kernel-e220.json's kernels: rgm136 as recorded; rgm211 from its "rgm211_host" entry (its whole ELF and loadable identity pins), with
    E211's .text pin beside them (E220's record names rgm211_host's ELF and identity only; E218's kit form, e218_common.KERNELS)."""
    k = json.load(open(os.path.join(HERE, "kernel-e220.json")))["kernels"]
    out = {"rgm136": k["rgm136"]}
    if "rgm211_host" in k:
        out["rgm211"] = dict(k["rgm211_host"], text_sha256=RGM211_TEXT_E211)
    return out


def pins(kernel):
    k = kernels()[kernel]
    return k["elf_sha256"], k["text_sha256"], k["loadable_identity_sha256"]


def identity(elf):
    e = _sha(elf)
    t = CK.text_sha(elf)
    ident, why = CK.elf_identity(elf)
    li = CK.identity_sha(ident) if ident is not None else None
    return {"elf_sha256": e, "text_sha256": t, "loadable_identity_sha256": li, "why": why or ""}


def gate(family, elf):
    """(ok, words): the ELF passes for the family: its .text the family's ELF's pin and its whole ELF the pin (module docstring)."""
    if family not in FAMILY_KERNEL:
        return False, f"no E220 family {family!r} ({', '.join(FAMILY_KERNEL)})"
    if not os.path.isfile(elf):
        return False, f"{family}: no kernel at {os.path.basename(elf)}"
    want = FAMILY_KERNEL[family]
    pe, pt, pl = pins(want)
    got = identity(elf)
    if got["text_sha256"] != pt:
        ks = kernels()
        others = [k for k in ks if ks[k]["text_sha256"] == got["text_sha256"]]
        return False, (f"{family} needs {want}'s .text {pt[:16]}...; this ELF's .text is {got['text_sha256']}"
                       + (f" ({others[0]}'s)" if others else ""))
    if got["elf_sha256"] != pe:
        return False, (f"{family}: .text {want}'s, but E220 gates on the whole ELF {pe} (E208's and E209's gate on this card), and this ELF is "
                       f"{got['elf_sha256']} (its loadable identity {got['loadable_identity_sha256']})")
    return True, (f"{family}: {want}'s ELF, .text {pt[:16]}... and the whole ELF {pe[:16]}... the pinned ones (loadable identity "
                  f"{(got['loadable_identity_sha256'] or 'unread')[:16]}...)")


def check():
    ok = True
    e, t, li = pins("rgm136")
    for name, mine, theirs in (("ELF", e, CK.KERNEL_PIN), (".text", t, CK.TEXT_PIN), ("loadable identity", li, CK.LOAD_PIN)):
        same = mine == theirs
        ok &= same
        print(f"rgm136 {name}: kernel-e220.json {mine[:16]}... E206's {theirs[:16]}...: {'SAME' if same else 'DIFFERS'}")
    e2, t2, l2 = pins("rgm211")
    distinct = len({t, t2}) == 2 and len({li, l2}) == 2 and e != e2
    ok &= distinct
    print(f"rgm211 pins (named only to be refused): ELF {e2[:16]}... .text {t2[:16]}... identity {l2[:16]}...; distinct from rgm136's: {distinct}")
    fam_ok = set(FAMILY_KERNEL) == set(FAMILY_HOST) == {"rgm136 gemmL", "rgm136 gemmLnc"} and set(FAMILY_KERNEL.values()) == {"rgm136"}
    ok &= fam_ok
    print(f"the two families: {sorted(FAMILY_KERNEL)} on rgm136's ELF; hosts {FAMILY_HOST}: {fam_ok}")
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
