#!/usr/bin/env python3
"""E183 (Q155, the kit): is the kernel's fadd.ps loop (catalogue mode 160) the one E180 ran? A REPORTED check at the desk, never a verdict.

    /usr/bin/python3 -B tools/claims-v3/e183/loopcmp_e183.py <E183's kernel listing> [<E180's committed listing>]
    /usr/bin/python3 -B tools/claims-v3/e183/loopcmp_e183.py --selftest

It finds mode 160's loop in each listing with E180's own walk (tools/claims-v3/e180/check_elf_e180.py: its parse, its body search and its
loop walk, imported unchanged): the RUN body of 64 fadd.ps ops found once, then the loop from its backward branch's target to that branch.
The two loops are compared instruction by instruction, by mnemonic and operands, with a branch's target written as its distance from the
branch (the addresses themselves may move with the build's layout). The default E180 listing is the one E180's data commit keeps
(docs/reports/data/2026-11-06-e180-vector-add-aifoundry3/logs/e180-kernel-dis.txt). It prints one line, LOOP-SAME, LOOP-DIFFERS (with the
first difference) or UNREAD (a loop not found once), and exits 0 for all three: the reading is reported beside the rules, and E183.md
section 11 says why (E180's price was read on this loop; a different loop is a different gap structure). Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(TOP, "tools", "claims-v3", "e180"))
import check_elf_e180 as W  # noqa: E402  (E180's walk, unchanged)

E180_LISTING = os.path.join(TOP, "docs/reports/data/2026-11-06-e180-vector-add-aifoundry3/logs/e180-kernel-dis.txt")
HEX = re.compile(r"[0-9a-f]+")


def loop_of(path):
    ins = W.parse(path)
    body = [W.norm(o) for o in W.M160["body"]] * 8
    hits = W.find(ins, body)
    if len(hits) != 1:
        return None, f"mode 160's body found {len(hits)} time(s)"
    i = hits[0]
    j = i + len(body)
    tail = ins[j:j + 30]
    br = next((k for k, t in enumerate(tail) if t[1].startswith("b") and t[2] and HEX.fullmatch(t[2][-1].split()[0])
               and int(t[2][-1].split()[0], 16) <= ins[i][0]), None)
    if br is None:
        return None, "no backward branch to the body within 30 instructions"
    target = int(tail[br][2][-1].split()[0], 16)
    loop = [t for t in ins[:j + br + 1] if t[0] >= target]
    out = []
    for addr, mn, ops in loop:
        o = list(ops)
        if (mn.startswith("b") or mn.startswith("j")) and o and re.fullmatch(r"[0-9a-f]{5,}", o[-1].split()[0]):
            o[-1] = f"{int(o[-1].split()[0], 16) - addr:+d}"      # the target, as its distance from the branch
        out.append((mn, tuple(o)))
    return out, f"{len(out)} instructions from {target:x}"


def compare(a, b):
    la, wa = loop_of(a)
    lb, wb = loop_of(b)
    if la is None or lb is None:
        return "UNREAD", f"E183's listing: {wa}; E180's: {wb}"
    if la == lb:
        return "LOOP-SAME", f"mode 160's loop, {len(la)} instructions, equals E180's instruction by instruction (E183: {wa}; E180: {wb})"
    k = next((n for n, (x, y) in enumerate(zip(la, lb)) if x != y), min(len(la), len(lb)))
    return "LOOP-DIFFERS", (f"mode 160's loop differs from E180's at instruction {k} ({la[k] if k < len(la) else 'end'} against "
                            f"{lb[k] if k < len(lb) else 'end'}; E183: {wa}; E180: {wb})")


def selftest():
    ok = []
    w, m = compare(E180_LISTING, E180_LISTING)
    ok.append(w == "LOOP-SAME")
    print(f"S1 E180's listing against itself: {w} - {m}")
    lines = open(E180_LISTING, errors="replace").read().splitlines()
    la, _ = loop_of(E180_LISTING)
    # S2: the same listing with every address moved by 0x40 (a layout change): still the same loop
    moved = []
    for ln in lines:
        mm = re.match(r"(\s*)([0-9a-f]+)(:\s+[0-9a-f]+\s+)(\S+)(\s*)(.*)", ln)
        if mm:
            ops = mm.group(6)
            if mm.group(4).startswith(("b", "j")):
                ops = re.sub(r"\b([0-9a-f]{4,})\b", lambda x: f"{int(x.group(1), 16) + 0x40:x}", ops)
            ln = f"{mm.group(1)}{int(mm.group(2), 16) + 0x40:x}{mm.group(3)}{mm.group(4)}{mm.group(5)}{ops}"
        moved.append(ln)
    d = tempfile.mkdtemp(prefix="loopcmp-e183-")
    p2 = os.path.join(d, "moved.txt")
    open(p2, "w").write("\n".join(moved) + "\n")
    w, m = compare(p2, E180_LISTING)
    ok.append(w == "LOOP-SAME")
    print(f"S2 every address moved by 0x40: {w}")
    # S3: one of mode 160's own csrr reads (the last before its loop's branch) changed to another counter: the loop differs
    head = next(k for k, ln in enumerate(lines) if "fadd.ps\tfs0,ft0,ft1" in ln)
    br = next(k for k in range(head, len(lines)) if re.search(r"\tb[a-z]*\t", lines[k]))
    k3 = next((k for k in range(br, head, -1) if "csrr" in lines[k] and "hpmcounter3" in lines[k]), None)
    p3 = os.path.join(d, "changed.txt")
    if k3 is not None:
        ch = list(lines)
        ch[k3] = ch[k3].replace("hpmcounter3", "hpmcounter4")
        open(p3, "w").write("\n".join(ch) + "\n")
        w, m = compare(p3, E180_LISTING)
        ok.append(w == "LOOP-DIFFERS")
        print(f"S3 a counter read in the loop changed: {w}")
    else:
        ok.append(False)
        print("S3 no csrr hpmcounter3 line in mode 160's loop to change")
    # S4: the body removed: UNREAD
    p4 = os.path.join(d, "nobody.txt")
    open(p4, "w").write("\n".join(ln for ln in lines if "fadd.ps\tft0" not in ln and "fadd.ps\tfs0" not in ln) + "\n")
    w, m = compare(p4, E180_LISTING)
    ok.append(w == "UNREAD")
    print(f"S4 mode 160's body taken out: {w}")
    for p in (p2, p3, p4):
        if os.path.exists(p):
            os.remove(p)
    os.rmdir(d)
    print(f"SELFTEST-LOOPCMP-E183 {sum(ok)} of {len(ok)} {'PASS' if all(ok) else 'FAIL'}")
    return 0 if all(ok) else 1


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    if not argv or len(argv) > 2:
        print(__doc__)
        return 2
    if not os.path.exists(argv[0]):
        print(f"UNREAD: no kernel listing at {os.path.basename(argv[0])} (the box had no objdump, or step 6 wrote none)")
        return 0
    w, m = compare(argv[0], argv[1] if len(argv) > 1 else E180_LISTING)
    print(f"{w}: {m}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
