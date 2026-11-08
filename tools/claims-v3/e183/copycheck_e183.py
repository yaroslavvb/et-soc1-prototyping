#!/usr/bin/env python3
"""E183 (Q155, the kit): the exact copy-back's check, at the desk (KIT.md box step 11). The box's own manifest of what step 11 copied
(lines "SUM <sha256> <path in the box's tree>", printed by step 11's read before the copy) against the Intel's copy, file by file: every
file the box listed is in the copy at its sha256, and the copy holds nothing the box did not list. Standard library only; it reads two
things and writes nothing.

    /usr/bin/python3 -B tools/claims-v3/e183/copycheck_e183.py <manifest> <raw dir> <day>
        exit 0 "COPY EXACT: <n> files"; 9 "COPY NOT EXACT" with the differences; 2 usage
The map from the box's tree to the copy: build/claims-v3/aifoundry3/<x>/... -> <raw>/<x>/...; build/e183/<f> and the train host's records
(build/enercat-e183/BUILD-E183.json, build/e183-kernel-dis.txt, build/e183-build-attempts.txt, build/e183-build-host.txt) -> <raw>/logs/<f>;
build/e183-build-logs/<day>/<f> -> <raw>/logs/e183-build-logs/<f>.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import os
import sys

sys.dont_write_bytecode = True


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def local_of(box, raw, day):
    if box.startswith("build/claims-v3/aifoundry3/"):
        return os.path.join(raw, box[len("build/claims-v3/aifoundry3/"):])
    if box.startswith(f"build/e183-build-logs/{day}/"):
        return os.path.join(raw, "logs", "e183-build-logs", os.path.basename(box))
    if box.startswith("build/e183/") or box in ("build/enercat-e183/BUILD-E183.json", "build/e183-kernel-dis.txt",
                                                "build/e183-build-attempts.txt", "build/e183-build-host.txt"):
        return os.path.join(raw, "logs", os.path.basename(box))
    return None


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    man, raw, day = argv
    want, bad = {}, []
    for line in open(man):
        parts = line.rstrip("\n").split(" ", 2)
        if len(parts) == 3 and parts[0] == "SUM":
            lp = local_of(parts[2], raw, day)
            if lp is None:
                bad.append(f"the box listed a path outside the map: {parts[2]}")
            else:
                want[os.path.normpath(lp)] = parts[1]
    if not want:
        bad.append("the box's manifest lists no file")
    for lp, h in sorted(want.items()):
        if not os.path.isfile(lp):
            bad.append(f"missing in the copy: {lp}")
        elif sha(lp) != h:
            bad.append(f"differs from the box: {lp}")
    have = set()
    for d, _dirs, files in os.walk(raw):
        for f in files:
            have.add(os.path.normpath(os.path.join(d, f)))
    extra = sorted(have - set(want) - {os.path.normpath(os.path.join(raw, "logs", "absent-on-box.txt")),
                                        os.path.normpath(os.path.join(raw, "logs", "box-manifest.txt"))})
    bad += [f"in the copy, not listed by the box: {p}" for p in extra]
    if bad:
        print("COPY NOT EXACT:\n  " + "\n  ".join(bad[:30]) + (f"\n  (+{len(bad) - 30})" if len(bad) > 30 else ""))
        return 9
    print(f"COPY EXACT: {len(want)} files, each at the box's sha256, and nothing else")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
