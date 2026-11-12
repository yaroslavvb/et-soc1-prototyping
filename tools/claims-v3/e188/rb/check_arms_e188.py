#!/usr/bin/env python3
"""E188 (Q165, the kit): THE GATE of october-forecast-model's reader (arm_read_e188.py), in the form of E186's notes M1 and M2 gates
(tools/claims-v3/e186/rb/check_history_e186.py m1, check_m2_e186_v2.py): the reader runs ONLY AFTER E188's data commit, on the committed
scored file, with the reader and the model's file at their pins, and writes nothing but its two outputs, outside the lab repo.

    /usr/bin/python3 -I -B tools/claims-v3/e188/rb/check_arms_e188.py --data docs/reports/data/<day>-e188-one-number-r4-aifoundry3 \
        --out <a stem outside the repo, e.g. $RB_OUT/arms/arm-ofm-e188> --kit-list-sha256 <SHA256SUMS-e188-kit's sha256, E188's anchor line>
        [--repo <the lab clone>]

It refuses (16, "ARMS NOT READ: <why>") unless, in this order:
  1. --out's directory exists and lies outside the repo, and neither <stem>.json nor <stem>.txt exists (never over an earlier reading);
  2. HEAD descends from E188's registration (878b6f63) and the kit's list tools/claims-v3/e188/SHA256SUMS-e188-kit reads at the sha256 given
     (the anchor line's), every entry OK;
  3. the reader (arm_read_e188.py) is at the kit list's sha256, and the model's file (ofm-e188.json) at the registration list's
     (SHA256SUMS-e188-registration, itself at e188_common's pin);
  4. THE DATA COMMIT: <data>/scored-e188.json is tracked at HEAD, nothing under <data> differs from HEAD or is untracked (git status
     --porcelain --untracked-files=all), and the file on disk equals HEAD's blob byte for byte; a data dir not yet committed is refused;
  5. nothing under tools/claims-v3/e188 differs from HEAD or is untracked;
then it runs the reader under a 50 s bound with -I -B, and reads back: the reader's exit 0; exactly <stem>.json and <stem>.txt new in
--out's directory and nothing else; the repo's status unchanged. Prints "ARMS READ: ..." and exits 0, or "ARMS NOT READ: ..." and 16 (a
refusal of the reader itself is recorded the same way). It is never a stop of the session or of the data commit, which come before it: a
reported arm. Standard library only; it writes nothing but what the reader writes.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
E188D = os.path.dirname(HERE)
REG = "878b6f6302f4b40d57c9577e3cb46b00cd741592"
REG_LIST = "tools/claims-v3/e188/SHA256SUMS-e188-registration"
REG_LIST_SHA256 = "b098561b055e9d85b87ea7e501105fda2f84234699a2b50b7ee8724fa0b9970e"
KIT_LIST = "tools/claims-v3/e188/SHA256SUMS-e188-kit"
READER = "tools/claims-v3/e188/arm_read_e188.py"
MODEL = "tools/claims-v3/e188/ofm-e188.json"
EXIT_GATE, EXIT_USAGE = 16, 10


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def git(repo, *args, binary=False):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, timeout=60)
    return r.returncode, (r.stdout if binary else r.stdout.decode("utf-8", "replace")), r.stderr.decode("utf-8", "replace")


def list_of(repo, rel):
    out = {}
    for line in open(os.path.join(repo, rel)):
        if line.strip():
            h, p = line.split(None, 1)
            out[p.strip().lstrip("*")] = h
    return out


def refuse(why):
    print(f"ARMS NOT READ: {why}")
    sys.exit(EXIT_GATE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="E188's data directory, relative to the repo's top")
    ap.add_argument("--out", required=True, help="the reader's output stem, outside the repo")
    ap.add_argument("--kit-list-sha256", required=True)
    ap.add_argument("--repo", default=os.path.abspath(os.path.join(E188D, "..", "..", "..")))
    ap.add_argument("--python", default="/usr/bin/python3")
    ap.add_argument("--reg-override", help="the desk test's stand-in registration commit; read only with E188_GATE_DESKTEST=1")
    a = ap.parse_args()
    reg = REG
    if a.reg_override:
        if os.environ.get("E188_GATE_DESKTEST") != "1":
            print("usage: --reg-override is the desk test's, read only with E188_GATE_DESKTEST=1 (the card day never sets it)")
            sys.exit(EXIT_USAGE)
        reg = a.reg_override
    repo = os.path.realpath(a.repo)
    data = a.data.rstrip("/")
    if os.path.isabs(data) or ".." in data.split("/"):
        print("usage: --data is the data directory relative to the repo's top")
        sys.exit(EXIT_USAGE)
    stem = os.path.abspath(a.out)
    od = os.path.dirname(stem)
    # 1. the output
    if not os.path.isdir(od):
        refuse(f"--out's directory {od} does not exist")
    if (os.path.realpath(od) + os.sep).startswith(repo + os.sep):
        refuse("--out lies inside the lab repo: the reader's readings stay outside it (a reported arm's readings are private by the tier)")
    for ext in (".json", ".txt"):
        if os.path.exists(stem + ext):
            refuse(f"{stem + ext} exists: never over an earlier reading")
    # 2. ancestry and the kit's list
    rc, _, _ = git(repo, "merge-base", "--is-ancestor", reg, "HEAD")
    if rc != 0:
        refuse(f"HEAD does not descend from E188's registration {reg[:8]}")
    kl = os.path.join(repo, KIT_LIST)
    if not os.path.exists(kl) or sha(kl) != a.kit_list_sha256:
        refuse(f"{KIT_LIST} is not at the sha256 given ({a.kit_list_sha256[:12]}...)")
    kit = list_of(repo, KIT_LIST)
    bad = [p for p, h in kit.items() if not os.path.exists(os.path.join(repo, p)) or sha(os.path.join(repo, p)) != h]
    if bad:
        refuse(f"the kit's list has {len(bad)} entr{'y' if len(bad) == 1 else 'ies'} not OK: {bad[:3]}")
    # 3. the reader and the model
    if kit.get(READER) != sha(os.path.join(repo, READER)):
        refuse(f"{READER} is not at the kit list's sha256")
    rl = os.path.join(repo, REG_LIST)
    if sha(rl) != REG_LIST_SHA256:
        refuse(f"{REG_LIST} is not at its pin")
    if list_of(repo, REG_LIST).get(MODEL) != sha(os.path.join(repo, MODEL)):
        refuse(f"{MODEL} is not at the registration list's sha256")
    # 4. the data commit
    scored = f"{data}/scored-e188.json"
    rc, so, _ = git(repo, "ls-files", "--error-unmatch", "--", scored)
    if rc != 0:
        refuse(f"{scored} is not tracked at HEAD: the reader runs only after E188's data commit")
    rc, so, se = git(repo, "status", "--porcelain=v1", "--untracked-files=all", "--", data)
    if rc != 0 or so.strip():
        refuse(f"{data} differs from HEAD or holds untracked files: {(so or se).strip()[:200]}")
    rc, blob, _ = git(repo, "show", f"HEAD:{scored}", binary=True)
    if rc != 0 or hashlib.sha256(blob).hexdigest() != sha(os.path.join(repo, scored)):
        refuse(f"{scored} on disk is not HEAD's blob")
    # 5. the kit's directory clean
    rc, so, se = git(repo, "status", "--porcelain=v1", "--untracked-files=all", "--", "tools/claims-v3/e188")
    if rc != 0 or so.strip():
        refuse(f"tools/claims-v3/e188 differs from HEAD or holds untracked files: {(so or se).strip()[:200]}")
    before = set(os.listdir(od))
    _, st0, _ = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    try:
        r = subprocess.run([a.python, "-I", "-B", os.path.join(repo, READER), "--scored", os.path.join(repo, scored), "--out", stem],
                           capture_output=True, text=True, timeout=50, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        refuse("the reader ran past its 50 s bound")
    after = set(os.listdir(od))
    _, st1, _ = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    new = sorted(after - before)
    want = sorted({os.path.basename(stem) + ".json", os.path.basename(stem) + ".txt"})
    if r.returncode != 0:
        refuse(f"the reader refused (rc {r.returncode}): {(r.stdout + r.stderr).strip().splitlines()[-1:] or ''}")
    if new != want:
        refuse(f"the reader wrote {new}, not exactly {want}")
    if st0 != st1:
        refuse("the repo's status changed while the reader ran")
    print(f"ARMS READ: october-forecast-model v8 and v9 read on the committed {scored} (HEAD descends from {reg[:8]}; the kit's list at "
          f"{a.kit_list_sha256[:12]}..., {len(kit)} entries OK; the reader and the model at their pins); wrote {want} in {od}")
    sys.exit(0)


if __name__ == "__main__":
    main()
