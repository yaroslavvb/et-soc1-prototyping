#!/usr/bin/env python3
"""E183 (Q155, the kit): what every E183 box and desk file shares - the registration's kinds, trains, plan and images, the train
schedule, each run's host arguments, and the frozen checks. Standard library only; it opens no device and reaches no box.

    /usr/bin/python3 -B tools/claims-v3/e183/e183_common.py --verify      # the registration's list, the images, the plan re-made, the
                                                                          # schedule; prints "E183 VERIFY OK ..." or the faults (exit 1)
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REL = "tools/claims-v3/e183"
CARD = "aifoundry3"
REG_LIST = "SHA256SUMS-e183-registration"
REG_COMMIT = "c98a7287"          # the registration, committed alone (Sat 7 Nov 2026 20:47:49 PST)
HOST_BIN = "build/enercat-e183/host/enercat_host"
KERNEL_ELF = "build/enercat-e183/kernel/enercat.elf"
BUILD_RECORD = "build/enercat-e183/BUILD-E183.json"
WINDOW = "240000000"             # E180's: 0.4 s at 600 MHz
LAUNCHES = 13                    # a train process: the settle (launch 0), then three quads
TRAIN_SECONDS = "30"             # the host's --seconds for a train process: never reached (the launch count ends it)
BURST_S, GAP_S, LEAD_S = 3.0, 4.5, 10.0          # E180's catalogue timing for the anchor bursts
SMOKE_BURST_S, SMOKE_LEAD_S = 1.0, 3.0
POST_ANCHOR_GAP_S = 6.0          # the kit's: after the opening anchors, before the train (the last anchor's idle bracket stays idle)
SMOKE_PASS, STOPTEST_PASS = 18301, 18302
PLAN_BUDGET_S = {"FULL": 3900, "SHORT": 1920}     # the caps from E183_T0 (plan-e183.json), 60 s of each reserved
RESERVE_S = 60


def _j(name):
    return json.load(open(os.path.join(HERE, name)))


def kinds():
    return _j("kinds-e183.json")


def plan():
    return _j("plan-e183.json")


def forecast():
    return _j("forecast-e183.json")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def image_rel(kind):
    """the repo-relative image of a one-number kind (E180's committed image, or this registration's)"""
    return kinds()["kinds"][kind]["image"]


def trains():
    return {t["train"]: t for t in plan()["trains"]}


def train_of_block(block):
    for t in plan()["trains"]:
        if t["block"] == int(block):
            return t
    raise KeyError(f"block {block} is not a planned train block (18310-18315)")


def blocks(name):
    return list(plan()["plans"][name]["blocks"])


def schedule(ori, n=LAUNCHES):
    """the kind of launch k: launch 0 (the settle) the orientation's first letter, launch k >= 1 letter (k - 1) mod 4"""
    if ori not in ("SFFS", "FSSF"):
        raise ValueError(ori)
    return [ori[0] if k < 1 else ori[(k - 1) % 4] for k in range(n)]


def anchor_args(kind):
    """an anchor burst's host arguments (E180's: the catalogue's own fills)"""
    fill = {"fadd.ps/zeros": "zeros", "fadd.ps/random": "random"}[kind]
    return ["--pattern", "fadd.ps", "--operands", fill, "--harts", "2"]


def burst_args(kind):
    """a one-number burst's host arguments (the smoke's 5s and 4s): its image by its tree-relative path, E180's form (the runner
    runs every device process from the tree's root, so no home path enters a record)"""
    if kind in ("fadd.ps/zeros", "fadd.ps/random"):
        return anchor_args(kind)
    return ["--pattern", "fadd.ps", "--operands", "file:" + image_rel(kind), "--harts", "2"]


def train_args(t, ori):
    """a train process's host arguments: F the train's first kind (--operands), S its second (--operands-b), tree-relative images"""
    return ["--pattern", "fadd.ps", "--operands", "file:" + image_rel(t["first"]),
            "--operands-b", "file:" + image_rel(t["second"]), "--abba", ori, "--launches", str(LAUNCHES),
            "--harts", "2", "--seconds", TRAIN_SECONDS, "--window", WINDOW]


def anchor_cfg(kind, block, side):
    return f"e183/{kind}/h2@b{block}-{side}"


def smoke_cfg(kind):
    return f"e183/{kind}/h2@smoke"


def check_frozen(root=TOP):
    """the registration's hash list, every entry OK (the kit reads only frozen inputs)"""
    probs = []
    for line in open(os.path.join(root, REL, REG_LIST)):
        parts = line.split()
        if len(parts) != 2:
            continue
        want, rel = parts
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            probs.append(f"missing {rel}")
        elif sha(p) != want:
            probs.append(f"changed {rel}")
    return probs


def verify(root=TOP):
    probs = check_frozen(root)
    kd = kinds()
    for name, k in kd["kinds"].items():
        p = os.path.join(root, k["image"])
        if not os.path.exists(p):
            probs.append(f"image missing for {name}: {k['image']}")
        elif sha(p) != k["image_sha256"]:
            probs.append(f"image of {name} differs from kinds-e183.json")
    spec = importlib.util.spec_from_file_location("plan_e183", os.path.join(HERE, "plan_e183.py"))
    pm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pm)
    if json.loads(json.dumps(pm.build(HERE))) != plan():
        probs.append("plan-e183.json differs from plan_e183.py's output")
    want_sffs = "SSFFSSFFSSFFS"
    if "".join(schedule("SFFS")) != want_sffs or "".join(schedule("FSSF")) != "FFSSFFSSFFSSF":
        probs.append("the schedule is not the registered one")
    for t in plan()["trains"]:
        if len(t["orientations"]) != t["processes"] or any(a == b for a, b in zip(t["orientations"], t["orientations"][1:])):
            probs.append(f"{t['train']}: its orientations do not alternate over its {t['processes']} processes")
    return probs


def main():
    if sys.argv[1:] != ["--verify"]:
        print(__doc__)
        sys.exit(2)
    probs = verify()
    if probs:
        print("E183 VERIFY FAULTS: " + "; ".join(probs))
        sys.exit(1)
    p = plan()
    print(f"E183 VERIFY OK: the registration's list, {len(kinds()['kinds'])} images, the plan ({', '.join(p['order'])}), the schedule")


if __name__ == "__main__":
    main()
