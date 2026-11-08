#!/usr/bin/env python3
# E186 kit note 4 (Q158, fix-arms): note M2's gate v2 and its reader v2's run, in step 11 v4 after step 11 v2 (and so after note M1's
# reader). It is note M2's gate v1 (rb/check_m2_e186.py, which stays as committed) line for line, with the reader v2
# (arm_m2_read_e186_v2.py; E186.md.dated-note-M2.md.dated-note-1.md, section 2) in place of v1, step 11 v4 named in two messages, and the
# read line naming the reader v2. Step 11 v4 pins note M2's list v2 (SHA256SUMS-e186-m2-v2) at its count and its own sha256 and passes
# both here; this gate reads the list at those pins with every entry at its bytes, then runs the reader v2 by its own run line, on a copy of
# the scorer's file, and puts only the reader's two outputs into the data directory.
#
#   /usr/bin/python3 -I -B tools/claims-v3/e186/rb/check_m2_e186_v2.py --list tools/claims-v3/e186/SHA256SUMS-e186-m2-v2 --count N \
#       --sha256 HEX --data <data dir> --work <a new directory outside the repo>
#
# Run from the lab's top (step 11 v4's rb_local runs it there). In order:
#   1. the list at its own sha256 (--sha256) and its count (--count), every entry's file at its bytes, the reader v2 and its json among the
#      entries, and no uncommitted change to any entry or to the list (git status);
#   2. the scorer's file <data>/scored-e186.json there;
#   3. a copy of the scorer's file in --work (made here; refused inside the repo), the reader v2 run on that copy, bounded at 50 s (inside
#      the runbook's 60 s read): /usr/bin/python3 -B tools/claims-v3/e186/arm_m2_read_e186_v2.py --scored <work>/scored-e186.json --out
#      <work>/arm-m2-e186; the reader never sees the data directory;
#   4. its two outputs, arm-m2-e186.json and .txt, copied into the data directory; then nothing else in the data directory may differ.
# It prints one of:
#   M2-READ arm-m2-e186.json and arm-m2-e186.txt (note M2's reader v2)   exit 0
#   M2 NOT READ: <why> (the gate refused; the reader never ran)           exit 4   recorded for the data README, never a stop
#   M2 NOT READ: the reader refused, rc <n> / killed at its bound         exit 5   recorded for the data README, never a stop
#   M2-WROTE-OTHER <files>                                                exit 16  the data directory changed beside the two outputs:
#                                                                                  read it before any commit (step 11 v4 stops, 16)
# 10 is usage. On the card day a change to any file this gate's list names, committed or not, is refused first by the history check
# (16) in step 2 v2 and again in step 11 v2, before this gate runs (kit note 4, section 3): here, "M2 NOT READ" comes from its other
# causes (no scorer's file, the reader's refusal or its bound, a work directory inside the repo). Python's own modules only. In the
# runbook's desk test alone (RB_DESKTEST=1), K6E186_M2READER names a stand-in reader; without RB_DESKTEST=1 that variable is refused (10).
# SPDX-License-Identifier: Apache-2.0
import argparse
import hashlib
import os
import shutil
import subprocess
import sys

READER = "tools/claims-v3/e186/arm_m2_read_e186_v2.py"   # note M2's dated note 1: the reader v2
MODEL = "tools/claims-v3/e186/m2-october-forecast-model-e186.json"
OUTPUTS = ("arm-m2-e186.json", "arm-m2-e186.txt")
READER_BOUND_S = 50


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_list(rel):
    try:
        text = open(rel, "rb").read().decode("utf-8", "replace")
    except OSError:
        return None
    out = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split(None, 1)
        if len(parts) < 2:
            out.append(("", "<unreadable line>"))
            continue
        p = parts[1].strip()
        out.append((parts[0], os.path.normpath(p[1:] if p.startswith("*") else p)))
    return out


def status(paths):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", LC_ALL="C", GIT_PAGER="cat")
    try:
        p = subprocess.run(["git", "status", "--porcelain=v1", "--untracked-files=all", "--", *paths], stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=60, env=env)
    except subprocess.TimeoutExpired:
        return ["git status: killed at its 60 s bound"]
    if p.returncode != 0:
        return [f"git status failed (rc {p.returncode})"]
    return [l for l in p.stdout.splitlines() if l.strip()]


def snapshot(d):
    out = {}
    for base, _, files in os.walk(d):
        for f in files:
            p = os.path.join(base, f)
            try:
                out[os.path.relpath(p, d)] = sha256_file(p)
            except OSError:
                out[os.path.relpath(p, d)] = "<unreadable>"
    return out


def main():
    ap = argparse.ArgumentParser(description="note M2's gate v2 and reader v2 run (step 11 v4; run from the lab's top)")
    ap.add_argument("--list", required=True)
    ap.add_argument("--count", required=True, type=int)
    ap.add_argument("--sha256", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--work", required=True)
    a = ap.parse_args()
    if not os.path.isfile("tools/claims-v3/e186/E186.md"):
        print("run from the lab's top (no tools/claims-v3/e186/E186.md here)")
        return 10
    stand = os.environ.get("K6E186_M2READER")
    if stand and os.environ.get("RB_DESKTEST") != "1":
        print("K6E186_M2READER is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)")
        return 10
    top = os.path.realpath(os.getcwd())
    work = os.path.realpath(a.work)
    if (work + os.sep).startswith(top + os.sep):
        print("M2 NOT READ: the work directory is inside the repo (the gate refused; the reader never ran; recorded for the data README, never a stop)")
        return 4
    why = []
    ent = read_list(a.list)
    if ent is None:
        why.append(f"{a.list} unreadable")
    else:
        if len(ent) != a.count:
            why.append(f"{os.path.basename(a.list)} holds {len(ent)} entries, pinned {a.count}")
        if sha256_file(a.list) != a.sha256:
            why.append(f"{os.path.basename(a.list)}'s own bytes differ from step 11 v4's pin")
        bad = [p for h, p in ent if not os.path.isfile(p) or sha256_file(p) != h]
        if bad:
            why.append(f"{len(bad)} entr(ies) not at their bytes: " + ", ".join(bad[:3]))
        names = {p for _, p in ent}
        for need in (READER, MODEL):
            if need not in names:
                why.append(f"the list does not name {need}")
        st = status(sorted(names | {a.list}))
        if st:
            why.append(f"{len(st)} uncommitted change(s) to note M2's files: " + "; ".join(s.strip() for s in st[:3]))
    scored = os.path.join(a.data, "scored-e186.json")
    if not os.path.isfile(scored):
        why.append(f"no {scored}")
    if why:
        print("M2 NOT READ: " + "; ".join(why) + " (the gate refused; the reader never ran; recorded for the data README, never a stop)")
        return 4
    os.makedirs(work, exist_ok=True)
    for f in ("scored-e186.json",) + OUTPUTS:
        if os.path.exists(os.path.join(work, f)):
            os.remove(os.path.join(work, f))
    shutil.copyfile(scored, os.path.join(work, "scored-e186.json"))
    before = snapshot(a.data)
    reader = stand if stand else READER
    cmd = ["/usr/bin/python3", "-B", reader, "--scored", os.path.join(work, "scored-e186.json"), "--out", os.path.join(work, "arm-m2-e186")]
    try:
        p = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=READER_BOUND_S)
        rrc, out = p.returncode, (p.stdout + p.stderr)
    except subprocess.TimeoutExpired:
        rrc, out = 124, f"(killed at its {READER_BOUND_S} s bound)"
    sys.stdout.write(out[-4000:])
    if not out.endswith("\n"):
        print()
    have = rrc == 0 and all(os.path.isfile(os.path.join(work, o)) for o in OUTPUTS)
    if have:
        for o in OUTPUTS:
            shutil.copyfile(os.path.join(work, o), os.path.join(a.data, o))
    after = snapshot(a.data)
    other = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k) and not (have and k in OUTPUTS))
    if other:
        print("M2-WROTE-OTHER " + ", ".join(other[:8]) + f" (the data directory changed beside note M2's two outputs; reader rc {rrc})")
        return 16
    if not have:
        print("M2 NOT READ: " + (f"the reader refused, rc {rrc}" if rrc not in (0, 124) else ("the reader was killed at its bound" if rrc == 124 else
                                  "the reader wrote no output")) + " (recorded for the data README, never a stop)")
        return 5
    print("M2-READ " + " and ".join(OUTPUTS) + " (note M2's reader v2)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
