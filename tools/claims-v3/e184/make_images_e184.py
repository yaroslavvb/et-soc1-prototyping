#!/usr/bin/env python3
"""E184's operand images: every image arm S can use, by rule, with its sha256 frozen in the registration (images-e184.sha256).

    python3 -B tools/claims-v3/e184/make_images_e184.py --sha > tools/claims-v3/e184/images-e184.sha256     # the frozen list
    python3 -B tools/claims-v3/e184/make_images_e184.py --check tools/claims-v3/e184/images-e184.sha256     # re-made, byte for byte
    python3 -B tools/claims-v3/e184/make_images_e184.py --write <dir> M:N [M:N ...]                         # the box: write, verify

An image is EC_MAX_HARTS x 256 B (e184_common.image_bytes): both harts of each of level n's minions on the m-shire mask hold their own
random [0.5, 2) words, every other word is zero. The list covers the ladder (32 shires), the smoke, the calibration, and every mask
the calibration rule may pick: M_op 10-24 for the operating point's levels and M_s 16-30 for the scan's. --write refuses an image that
is not on the frozen list or whose bytes differ from it, and writes nothing then (exit 3).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402


def wanted():
    plan = json.load(open(os.path.join(HERE, "plan-e184.json")))
    ds = plan["design"]
    out = set(tuple(x) for x in plan["arm_S"]["images_fixed_mask"])
    lo, hi = 10, 24
    for m in range(lo, hi + 1):
        for n in ds["P"]["levels"]:
            out.add((m, n))
    for m in range(16, 31):
        for n in ds["C"]["levels"] + [ds["C"]["ref"]]:
            out.add((m, n))
    return sorted(out)


def sha_lines():
    return ["%s  %s" % (hashlib.sha256(c.image_bytes(m, n)).hexdigest(), c.image_name(m, n)) for m, n in wanted()]


def main(argv):
    if argv[:1] == ["--sha"]:
        sys.stdout.write("\n".join(sha_lines()) + "\n")
        return 0
    if len(argv) == 2 and argv[0] == "--check":
        same = open(argv[1]).read() == "\n".join(sha_lines()) + "\n"
        print("make_images_e184 --check: %s (%d images)" % ("IDENTICAL" if same else "DIFFERS", len(wanted())))
        return 0 if same else 1
    if len(argv) >= 3 and argv[0] == "--write":
        frozen = {}
        for line in open(os.path.join(HERE, "images-e184.sha256")):
            h, name = line.split()
            frozen[name] = h
        todo = []
        for a in argv[2:]:
            m, n = (int(x) for x in a.split(":"))
            name = c.image_name(m, n)
            b = c.image_bytes(m, n)
            h = hashlib.sha256(b).hexdigest()
            if frozen.get(name) != h:
                print("make_images_e184: %s is %s, the frozen list has %s: nothing written" % (name, h, frozen.get(name)), file=sys.stderr)
                return 3
            todo.append((name, b))
        os.makedirs(argv[1], exist_ok=True)
        for name, b in todo:
            p = os.path.join(argv[1], name)
            if os.path.exists(p) and hashlib.sha256(open(p, "rb").read()).hexdigest() == frozen[name]:
                continue
            with open(p + ".tmp", "wb") as f:
                f.write(b)
            os.replace(p + ".tmp", p)
        print("make_images_e184: %d images in %s, each equal to the frozen list" % (len(todo), argv[1]))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
