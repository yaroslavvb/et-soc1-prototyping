#!/usr/bin/env python3
"""E188 (Q165, the kit): the self-test of october-forecast-model's reader (arm_read_e188.py) and of its gate (rb/check_arms_e188.py), on
synthetic sessions only (fake_card_e188.py through reduce_e188.py and score_e188.py, as selftest_score_e188.py makes them). No card, no
datum; it writes only under <work dir>.
  R1  a FULL session's scored file (M12's world): v8 reads its seven trains and its two kinds-pass items (BALL, AALL), the other six
      "not covered"; v9 reads its seven trains and its eight kinds-pass items, the tie among them; every item carries its frozen label
      (the five one-bit B trains and PAIR blind, AALL post hoc); no summary key in the output;
  R2  a train the scorer read NOT SCORED (lo null): "not read" in both arms, the other six read;
  R3  a train whose mean is NaN: "not read"; the json written strictly (no NaN);
  R4  the model's file off its pin: REFUSED, exit 2, nothing written;
  R5  a scorer's file without "trains": REFUSED, exit 3;
  R6  the fallback's scored file (no train scored, no FULL kinds pass): every train "not read", every kinds-pass item "not run";
  G1  the gate before the data commit (the data directory untracked in a scratch repository): ARMS NOT READ (16), the reader not run;
  G2  --out inside the repository: 16; G3 --out already written: 16;
  G4  after the data commit: ARMS READ (0), exactly the two outputs written, the repository's status unchanged;
  G5  the committed scored file edited on disk: 16; G6 the kit's list off the sha256 given: 16; G7 the reader changed on disk: 16;
  G8  --reg-override without E188_GATE_DESKTEST=1: usage (10).
The scratch repository holds the reader, the model's file, the registration's list and a stand-in kit list naming the two files it holds;
its first commit stands in for the registration (the gate's --reg-override, read only with E188_GATE_DESKTEST=1).
    /usr/bin/python3 -B selftest_arm_e188.py <work dir>
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import selftest_score_e188 as SS  # noqa: E402  (its session(): fake card, reductions, scorer)
PY = "/usr/bin/python3"
FAILS, N = [], [0]


def say(ok, what):
    N[0] += 1
    print(("PASS " if ok else "FAIL ") + what, flush=True)
    if not ok:
        FAILS.append(what)


def reader(scored_path, stem, model=None):
    args = [PY, "-B", os.path.join(HERE, "arm_read_e188.py"), "--scored", scored_path, "--out", stem]
    if model:
        args += ["--model", model]
    return subprocess.run(args, capture_output=True, text=True)


def load(stem):
    return json.load(open(stem + ".json")) if os.path.exists(stem + ".json") else None


def readers(work):
    s = SS.session(work, "r1", "--world", "M12", "--seed", "18901", "--noise-scale", "0.5")
    sp = os.path.join(work, "r1", "scored-e188.json")
    r = reader(sp, os.path.join(work, "r1", "arm"))
    o = load(os.path.join(work, "r1", "arm"))
    ok = r.returncode == 0 and o is not None
    if ok:
        v8, v9 = o["arms"]["v8"], o["arms"]["v9"]
        labels = {t: v9["trains"][t]["label"] for t in v9["trains"]}
        ok = (v8["counts"]["trains"] == {"read": 7} and v8["counts"]["kinds_pass"] == {"read": 2, "not covered": 6} and
              v9["counts"]["trains"] == {"read": 7} and v9["counts"]["kinds_pass"] == {"read": 8} and
              v9["kinds_pass"]["pi x pi (the tie, built-in)"]["reading"] == "read" and
              labels == {"AALL": "post hoc", "B04": "blind", "B05": "blind", "B10": "blind", "B19": "blind", "B22": "blind", "PAIR": "blind"} and
              not any(k in json.dumps(o) for k in ('"rms', '"mean_error', '"inside":')))
    say(ok, f"R1 a FULL session: v8 {o and o['arms']['v8']['counts']}; v9 {o and o['arms']['v9']['counts']}; labels as frozen; no summary key")
    sc = json.load(open(sp))
    sc2 = json.loads(json.dumps(sc))
    sc2["trains"]["B19"].update(lo=None, hi=None, why="NOT SCORED (a synthetic case)")
    p2 = os.path.join(work, "r1", "scored-r2.json")
    json.dump(sc2, open(p2, "w"))
    r = reader(p2, os.path.join(work, "r1", "arm-r2"))
    o = load(os.path.join(work, "r1", "arm-r2"))
    say(r.returncode == 0 and o["arms"]["v8"]["trains"]["B19"]["reading"] == "not read" and o["arms"]["v9"]["counts"]["trains"] == {"read": 6, "not read": 1},
        f"R2 a train NOT SCORED: v8 B19 {o and o['arms']['v8']['trains']['B19']['reading']}, v9 {o and o['arms']['v9']['counts']['trains']}")
    sc3 = json.loads(json.dumps(sc))
    sc3["trains"]["B05"]["mean"] = float("nan")
    p3 = os.path.join(work, "r1", "scored-r3.json")
    open(p3, "w").write(json.dumps(sc3))
    r = reader(p3, os.path.join(work, "r1", "arm-r3"))
    txt = open(os.path.join(work, "r1", "arm-r3.json")).read() if os.path.exists(os.path.join(work, "r1", "arm-r3.json")) else ""
    o = load(os.path.join(work, "r1", "arm-r3")) if txt else None
    say(r.returncode == 0 and o and o["arms"]["v9"]["trains"]["B05"]["reading"] == "not read" and "NaN" not in txt,
        f"R3 a NaN mean: v9 B05 {o and o['arms']['v9']['trains']['B05']['reading']}; NaN in the json {'NaN' in txt}")
    bad = os.path.join(work, "r1", "ofm-changed.json")
    open(bad, "w").write(open(os.path.join(HERE, "ofm-e188.json")).read() + " ")
    r = reader(sp, os.path.join(work, "r1", "arm-r4"), model=bad)
    say(r.returncode == 2 and not os.path.exists(os.path.join(work, "r1", "arm-r4.json")), f"R4 the model's file off its pin: rc {r.returncode}, nothing written")
    p5 = os.path.join(work, "r1", "scored-r5.json")
    json.dump({"rules": {}}, open(p5, "w"))
    r = reader(p5, os.path.join(work, "r1", "arm-r5"))
    say(r.returncode == 3, f"R5 no trains: rc {r.returncode}")
    s6 = SS.session(work, "r6", "--world", "M12", "--seed", "18902", "--passes", "5", fallback=True)
    r = reader(os.path.join(work, "r6", "scored-e188.json"), os.path.join(work, "r6", "arm"))
    o = load(os.path.join(work, "r6", "arm"))
    say(r.returncode == 0 and o["arms"]["v9"]["counts"]["trains"] == {"not read": 7} and o["arms"]["v9"]["counts"]["kinds_pass"] == {"not run": 8},
        f"R6 the fallback's scored file: v9 trains {o and o['arms']['v9']['counts']['trains']}, kinds pass {o and o['arms']['v9']['counts']['kinds_pass']}")
    return sp


def gate(work, scored_src):
    R = os.path.join(work, "grepo")
    if os.path.isdir(R):
        shutil.rmtree(R)
    os.makedirs(os.path.join(R, "tools/claims-v3/e188"))

    def g(*args):
        return subprocess.run(["git", "-C", R, *args], capture_output=True, text=True)
    g("init", "-q")
    g("config", "user.email", "desk@example.invalid")
    g("config", "user.name", "desk")
    for f in ("arm_read_e188.py", "ofm-e188.json", "SHA256SUMS-e188-registration"):
        shutil.copy(os.path.join(HERE, f), os.path.join(R, "tools/claims-v3/e188", f))
    kl = os.path.join(R, "tools/claims-v3/e188/SHA256SUMS-e188-kit")
    with open(kl, "w") as f:
        for rel in ("tools/claims-v3/e188/arm_read_e188.py", "tools/claims-v3/e188/ofm-e188.json"):
            f.write(f"{hashlib.sha256(open(os.path.join(R, rel), 'rb').read()).hexdigest()}  {rel}\n")
    g("add", "-A")
    g("commit", "-q", "-m", "the stand-in registration and kit")
    reg = g("rev-parse", "HEAD").stdout.strip()
    kls = hashlib.sha256(open(kl, "rb").read()).hexdigest()
    data = "docs/reports/data/2026-11-13-e188-one-number-r4-aifoundry3"
    os.makedirs(os.path.join(R, data))
    shutil.copy(scored_src, os.path.join(R, data, "scored-e188.json"))
    out = os.path.join(work, "gout")
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    env = dict(os.environ, E188_GATE_DESKTEST="1")

    def gate_run(stem, kit=kls, override=True, e=env):
        args = [PY, "-I", "-B", os.path.join(HERE, "rb", "check_arms_e188.py"), "--data", data, "--out", stem, "--kit-list-sha256", kit,
                "--repo", R]
        if override:
            args += ["--reg-override", reg]
        return subprocess.run(args, capture_output=True, text=True, env=e)
    r = gate_run(os.path.join(out, "arm"))
    say(r.returncode == 16 and "not tracked at HEAD" in r.stdout and not os.listdir(out), f"G1 before the data commit: rc {r.returncode}: {r.stdout.strip()[:110]}")
    r = gate_run(os.path.join(R, "arm"))
    say(r.returncode == 16 and "inside the lab repo" in r.stdout, f"G2 --out inside the repository: rc {r.returncode}")
    g("add", data)
    g("commit", "-q", "-m", "the stand-in data commit")
    open(os.path.join(out, "old.json"), "w").write("{}\n")
    r = gate_run(os.path.join(out, "old"))
    say(r.returncode == 16 and "never over an earlier reading" in r.stdout, f"G3 --out already written: rc {r.returncode}")
    st0 = g("status", "--porcelain").stdout
    r = gate_run(os.path.join(out, "arm"))
    new = sorted(os.listdir(out))
    say(r.returncode == 0 and r.stdout.startswith("ARMS READ:") and new == ["arm.json", "arm.txt", "old.json"] and g("status", "--porcelain").stdout == st0,
        f"G4 after the data commit: rc {r.returncode}: {r.stdout.strip()[:90]}; the out directory {new}")
    p = os.path.join(R, data, "scored-e188.json")
    keep = open(p).read()
    open(p, "w").write(keep.replace('"run": "E188"', '"run": "E188 "'))
    r = gate_run(os.path.join(out, "arm5"))
    say(r.returncode == 16 and "differs from HEAD" in r.stdout, f"G5 the committed scored file edited on disk: rc {r.returncode}")
    open(p, "w").write(keep)
    r = gate_run(os.path.join(out, "arm6"), kit="0" * 64)
    say(r.returncode == 16 and "is not at the sha256 given" in r.stdout, f"G6 the kit's list off the sha256 given: rc {r.returncode}")
    rp = os.path.join(R, "tools/claims-v3/e188/arm_read_e188.py")
    rk = open(rp).read()
    open(rp, "w").write(rk + "\n# a change\n")
    r = gate_run(os.path.join(out, "arm7"))
    say(r.returncode == 16 and "not OK" in r.stdout, f"G7 the reader changed on disk: rc {r.returncode}: {r.stdout.strip()[:90]}")
    open(rp, "w").write(rk)
    e2 = dict(os.environ)
    e2.pop("E188_GATE_DESKTEST", None)
    r = gate_run(os.path.join(out, "arm8"), e=e2)
    say(r.returncode == 10, f"G8 --reg-override without E188_GATE_DESKTEST=1: rc {r.returncode}")


def main():
    work = os.path.abspath(sys.argv[1])
    os.makedirs(work, exist_ok=True)
    sp = readers(work)
    gate(work, sp)
    print(f"SELFTEST-ARM-E188 {N[0] - len(FAILS)} of {N[0]} PASS" + ("" if not FAILS else ": " + "; ".join(FAILS)))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
