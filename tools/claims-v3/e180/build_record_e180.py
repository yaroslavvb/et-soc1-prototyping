#!/usr/bin/env python3
"""E180 (the kit's dated note 2, KIT.md.dated-note-2.md section 2): the build record and the box's kernel listing, brought into the
collection's logs/ at the desk (collect_e180_v3.sh runs it), so A1-7's evidence and the kernel's sha256 are in the data.

    python3 -B tools/claims-v3/e180/build_record_e180.py --raw <build/e180-raw/build-record> --out <the collection's logs/>

<raw> holds what step 22 v3 copied back from the box: BUILD-E180.json (build_e180.sh's record: the host's and the kernel's sha256, the
appended modes' sha256, the build time, and the toolchain's listing, `ls -l /opt/et/bin | head -3; cat /opt/et/VERSION`, its last 400
characters) and e180-kernel-dis.txt (step 6 v2's objdump -d of build/enercat-e180/kernel/enercat.elf). It writes:
  logs/build-e180.json      BUILD-E180.json's binaries, modes sha256 and build time unchanged; the toolchain listing with every `ls -l`
                            line's owner, group and symlink target withheld (a lab account's login must never reach a committed file)
                            and any line that is not an ls -l entry, a total or a bare version string withheld whole (the 400-character
                            cut can leave a partial first line), with the sha256 of the listing as recorded; plus the kernel listing's
                            own record: {"sha256", "bytes", "lines", "instructions"} or {"absent": ...};
  logs/e180-kernel-dis.txt  the listing, byte for byte (check_elf_e180_v2.py reads it there).
Prints one line. Exit 0, also when a file is absent (it is recorded as absent: the walk then reads UNREAD, no objdump); exit 2 only on a
usage error. Standard library only; it reads <raw> and writes two files in <out>.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import sys

LS_L = re.compile(r"^([-bcdlps][-rwxsStT]{9}[.+@]?\s+\d+\s+)(\S+)(\s+)(\S+)(\s.*)$")
TOTAL = re.compile(r"^total \d+$")
VERSION = re.compile(r"^[vV]?\d+(\.\d+)+[-+._A-Za-z0-9]*$")
INSN = re.compile(r"\s*[0-9a-f]+:\s+[0-9a-f]+\s+\S+")
CUT = 400


def mask_listing(text):
    """the toolchain listing with every ls -l line's owner, group and symlink target withheld; any other line kept only when it is
    'total N' or a bare version string (/opt/et/VERSION's), else withheld whole (the 400-character cut can leave a partial first line)"""
    out = []
    for line in text.split("\n"):
        m = LS_L.match(line)
        if m:
            rest = re.sub(r" -> .*$", " -> <target withheld>", m.group(5))
            out.append(f"{m.group(1)}<owner>{m.group(3)}<group>{rest}")
        elif not line or TOTAL.match(line) or VERSION.match(line.strip()):
            out.append(line)
        else:
            out.append("<a line withheld: not an ls -l entry, a total or a bare version string>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="the build record copied back: build/e180-raw/build-record")
    ap.add_argument("--out", required=True, help="the collection's logs/ directory")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    bj, lst = os.path.join(a.raw, "BUILD-E180.json"), os.path.join(a.raw, "e180-kernel-dis.txt")
    rec = {"what": "build_record_e180.py (KIT.md.dated-note-2.md section 2): the box's BUILD-E180.json, its toolchain listing's owner "
                   "and group withheld, and the box's kernel listing's record"}
    if os.path.isfile(bj):
        try:
            b = json.load(open(bj))
        except ValueError as e:
            b = None
            rec["build"] = {"unreadable": f"BUILD-E180.json is not JSON ({e})"}
        if b is not None and not isinstance(b, dict):
            rec["build"] = {"unreadable": "BUILD-E180.json is not a JSON object"}
        if isinstance(b, dict):
            for k in ("binaries", "acc_modes_inc_sha256", "built"):
                if k in b:
                    rec[k] = b[k]
            if isinstance(b.get("toolchain_listing"), str):
                rec["toolchain_listing"] = mask_listing(b["toolchain_listing"])
                rec["toolchain_listing_sha256_as_recorded"] = hashlib.sha256(b["toolchain_listing"].encode()).hexdigest()
            rec["fields_not_kept"] = sorted(k for k in b if k not in ("binaries", "acc_modes_inc_sha256", "built", "toolchain_listing"))
    else:
        rec["build"] = {"absent": "BUILD-E180.json did not come back from the box"}
    if os.path.isfile(lst):
        data = open(lst, "rb").read()
        text = data.decode("utf-8", errors="replace")
        rec["kernel_listing"] = {"file": "e180-kernel-dis.txt", "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                                 "lines": text.count("\n"), "instructions": sum(1 for ln in text.splitlines() if INSN.match(ln))}
        if os.path.abspath(lst) != os.path.abspath(os.path.join(a.out, "e180-kernel-dis.txt")):
            shutil.copyfile(lst, os.path.join(a.out, "e180-kernel-dis.txt"))
    else:
        rec["kernel_listing"] = {"absent": "the box's kernel listing did not come back (step 6 v2 found no objdump or no kernel, "
                                           "or it was not asked for): A1-7 reads UNREAD, no objdump"}
    json.dump(rec, open(os.path.join(a.out, "build-e180.json"), "w"), indent=1, sort_keys=True)
    kl = rec["kernel_listing"]
    kern = (rec.get("binaries") or {}).get("build/enercat-e180/kernel/enercat.elf")
    print(f"build record: kernel sha256 {kern[:16] + '...' if kern else 'not recorded'}; listing "
          f"{kl['sha256'][:16] + '... ' + str(kl['instructions']) + ' instructions' if 'sha256' in kl else 'absent'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
