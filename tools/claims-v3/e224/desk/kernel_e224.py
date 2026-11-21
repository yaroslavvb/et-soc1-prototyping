#!/usr/bin/env python3
"""E224 (Q237) desk: E224's kernel and hosts by path and sha256 (E220's registered record, tools/claims-v3/e220/kernel-e220.json, re-hashed at this
registration's HEAD: every source equal or the tool refuses), the arm families per arm, and every tile file E224's points name (the lab's random,
zeros and ones tiles; E212's and E217's operand-pattern tiles) by sha256. Standard library only.

    /usr/bin/python3 -I -B tools/claims-v3/e224/desk/kernel_e224.py            writes kernel-e224.json
    /usr/bin/python3 -I -B tools/claims-v3/e224/desk/kernel_e224.py --check    re-makes it and compares (exit 0 = PASS)
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
K220 = ("tools/claims-v3/e220/kernel-e220.json", "f332b03a9f30aee15ba465c8c497ee31a2cfc758bcb91a6ae10ed8453e54338e")
POINTS = ("points-e224.json", "44c790ffa5bc619029dd3f16c1cd8cf269c91f45d6681b9642ddd133ac30e340")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def make():
    if sha(os.path.join(REPO, K220[0])) != K220[1] or sha(os.path.join(E, POINTS[0])) != POINTS[1]:
        print("kernel_e224: REFUSED, an input is not at its pin")
        sys.exit(4)
    k = json.load(open(os.path.join(REPO, K220[0])))
    bad = {}
    for name, kr in k["kernels"].items():
        for rel, h in kr["sources_sha256"].items():
            g = sha(os.path.join(REPO, rel))
            if g != h:
                bad[rel] = g
    if bad:
        print("kernel_e224: REFUSED, a kernel source differs from E220's record:", bad)
        sys.exit(4)
    P = json.load(open(os.path.join(E, POINTS[0])))
    fam, tiles = {}, {}
    for arm in ("A", "B"):
        for p in P["points"][arm]:
            f = fam.setdefault(p["loop"], {"host": p["host"], "elf": p["elf"], "points": {"A": [], "B": []}})
            f["points"][arm].append(p["id"])
            for t, h in p["tile_sha256"].items():
                if tiles.setdefault(t, h) != h:
                    print(f"kernel_e224: REFUSED, {t} has two hashes")
                    sys.exit(4)
    for t, h in tiles.items():
        if sha(os.path.join(REPO, t)) != h:
            print(f"kernel_e224: REFUSED, {t} changed")
            sys.exit(4)
    rec = {"experiment": "E224", "request": "Q237", "what": ("E224's kernel and hosts by path and sha256 (E220's record re-hashed at this HEAD, every "
                                                             "source equal), the arm families per arm and every tile file the points name (desk)"),
           "kernels": k["kernels"], "kernels_equal_to_E220_record": True, "e220_kernel_record_sha256": K220[1], "build": k["build"],
           "arm_families": fam, "tiles_sha256": dict(sorted(tiles.items())),
           "host_arguments": ("--test fma --type <fmt> --pattern none --values <arm>:<gen>:<tile files> --shires <mask> --per-shire 32 --seconds 6 "
                              "--budget 7.5 --seed 1 (the kit adds --kernel, --stop-file and its absolute paths); random: fp32 and fp16 "
                              "kinds/tiles/<fmt>/randn.bin, int8 kinds/tiles/int8/full.bin (E101's grammar); zeros and ones: kinds/tiles/<fmt>/; "
                              "family P's patterns: E212's tiles (tools/claims-v3/e212/proposal/src/tiles/<fmt>/) and E217's (tools/claims-v3/e217/"
                              "proposal/src/tiles/<fmt>/), each point's own values string in points-e224.json")}
    return json.dumps(rec, indent=1, sort_keys=True) + "\n"


def main():
    txt = make()
    path = os.path.join(E, "kernel-e224.json")
    if "--check" in sys.argv:
        same = open(path).read() == txt
        print("kernel_e224 --check:", "PASS" if same else "DIFFER")
        sys.exit(0 if same else 1)
    open(path, "w").write(txt)
    print("kernel-e224.json", sha(path))


if __name__ == "__main__":
    main()
