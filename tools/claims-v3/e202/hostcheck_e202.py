#!/usr/bin/env python3
"""E202's host check (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): the mnistmlp host read by its BEHAVIOUR, never by a
string grepped from its bytes (E183's kit note 4; E189's hostcheck_e189.py form). Every run opens no device:

    python3 -B tools/claims-v3/e202/hostcheck_e202.py HOST FILESDIR      (from the tree's root; FILESDIR: files_e202.sh's directory)

  1. --selftest (CPU only): 8 SELFTEST lines OK and SELFTEST PASS, exit 0;
  2. its refusals at parse, with --card: no mode; --budget 9.6; --passes 1001; --stage xyz; --debug-logits without --expect-logits;
     an unknown option. Each must exit 2 with its usage line and write no --out file. EVERY such case also carries --pins naming a
     missing file, a second refusal main.cpp makes before any device (it then writes its --out file with "REFUSED"): so even a host
     whose tested refusal failed would stop before the card, and this check would read FAIL;
  3. --dry (the plan, no device) of every launch E202 registers: the smoke's train R = 1 (3,750 groups, 118 rounds) at scp and dram,
     the test split's R = 1 (625 groups, 20 rounds), and R = 16, 96 at both stagings (60,000 / 360,000 groups; 1,875 / 11,250 rounds);
     each status DRY, pins OK, model_s under the host's 6 s guard; --passes 1000 reads a model over it (the guard a card launch meets);
  4. --ref (the host's own reference of the kernel's arithmetic, no device) on 2 groups, trained and random, both splits, with every
     layer-5 tile: PASS; the negative control (trained weights against random's expected file) FAIL, exit 1;
  5. a pins file with one wrong hash: REFUSED, exit 2, pins FAIL.
Prints each case and, last, HOST-BEHAVIOUR OK: <n> of <n> or HOST-BEHAVIOUR FAIL: <cases>. Python's own modules only.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import subprocess
import sys
import tempfile


def run(host, args, tmp, out=True):
    o = os.path.join(tmp, "out.json")
    if os.path.exists(o):
        os.remove(o)
    a = [host] + args + (["--out", o] if out else [])
    r = subprocess.run(["timeout", "60"] + a, capture_output=True, text=True)
    j = None
    if os.path.exists(o):
        try:
            j = json.loads(open(o).read().splitlines()[-1])
        except (ValueError, IndexError):
            j = {"unreadable": True}
    return r.returncode, r.stdout, r.stderr, j


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    host, fd = argv
    M, F = os.path.join(fd, "mnist"), os.path.join(fd, "files")
    pins = os.path.join(F, "PINS-SHA256SUMS")
    tmp = tempfile.mkdtemp(prefix="hostcheck-e202-")
    missing = os.path.join(tmp, "no-such-pins-file")

    def inputs(w, sp):
        tag = "train" if sp == "train" else "test"
        img = os.path.join(M, "train-images-idx3-ubyte" if sp == "train" else "t10k-images-idx3-ubyte")
        return ["--images", img, "--weights", os.path.join(F, f"mnist-int8-{w}.mlpw"), "--expect",
                os.path.join(F, f"expect-{w}-{tag}.mlpe"), "--split", sp]

    res = []

    def case(name, ok, detail=""):
        res.append((name, ok))
        print(f"{'PASS' if ok else 'FAIL'} {name}{': ' + detail if detail else ''}")

    rc, so, se, _ = run(host, ["--selftest"], tmp, out=False)
    n_ok = sum(1 for ln in so.splitlines() if ln.startswith("SELFTEST ") and ln.rstrip().endswith(" OK"))
    case("selftest", rc == 0 and so.strip().splitlines()[-1:] == ["SELFTEST PASS"] and n_ok == 8, f"rc {rc}, {n_ok} OK lines")
    base = inputs("trained", "train") + ["--pins", missing]
    refusals = {
        "no mode": inputs("trained", "train") + ["--pins", missing],
        "--budget 9.6": ["--card"] + base + ["--budget", "9.6"],
        "--passes 1001": ["--card"] + base + ["--passes", "1001"],
        "--stage xyz": ["--card"] + base + ["--stage", "xyz"],
        "--debug-logits without --expect-logits": ["--card"] + base + ["--debug-logits"],
        "an unknown option": ["--card"] + base + ["--frobnicate"],
    }
    for name, a in refusals.items():
        rc, so, se, j = run(host, a, tmp)
        case(f"refusal at parse: {name}", rc == 2 and "usage:" in se and j is None,
             f"rc {rc}, usage {'printed' if 'usage:' in se else 'NOT printed'}, --out {'absent' if j is None else 'WRITTEN: ' + str(j.get('status'))}")
    plans = [("train R1 scp", "trained", "train", "scp", 1, 3750, 118), ("train R1 dram", "random", "train", "dram", 1, 3750, 118),
             ("test R1 scp", "trained", "test", "scp", 1, 625, 20), ("train R16 scp", "trained", "train", "scp", 16, 60000, 1875),
             ("train R96 scp", "trained", "train", "scp", 96, 360000, 11250), ("train R96 dram", "random", "train", "dram", 96, 360000, 11250)]
    for name, w, sp, st, R, groups, rounds in plans:
        rc, so, se, j = run(host, ["--dry"] + inputs(w, sp) + ["--stage", st, "--passes", str(R), "--pins", pins], tmp)
        j = j or {}
        case(f"--dry {name}", rc == 0 and j.get("status") == "DRY" and j.get("pins") == "OK" and j.get("groups") == groups
             and j.get("rounds") == rounds and isinstance(j.get("model_s"), (int, float)) and j["model_s"] < 6.0,
             f"rc {rc}, status {j.get('status')}, pins {j.get('pins')}, groups {j.get('groups')}, rounds {j.get('rounds')}, model_s {j.get('model_s')}")
    rc, so, se, j = run(host, ["--dry"] + inputs("trained", "train") + ["--passes", "1000", "--pins", pins], tmp)
    j = j or {}
    case("--dry R1000: the guard's model over 6 s", rc == 0 and isinstance(j.get("model_s"), (int, float)) and j["model_s"] > 6.0,
         f"model_s {j.get('model_s')}")
    for w in ("trained", "random"):
        for sp in ("train", "test"):
            tag = "train" if sp == "train" else "test"
            rc, so, se, j = run(host, ["--ref", "--ref-groups", "2"] + inputs(w, sp) + [
                "--expect-logits", os.path.join(F, f"logits-{w}-{tag}.mlpl"), "--pins", pins], tmp)
            j = j or {}
            case(f"--ref {w} {sp}", rc == 0 and j.get("status") == "PASS" and j.get("ref_groups") == 2
                 and j.get("ref_logit_tiles_checked") == 2 and j.get("ref_logit_tile_mismatches") == 0,
                 f"rc {rc}, status {j.get('status')}, labels {j.get('ref_label_mismatches')}, tiles {j.get('ref_logit_tile_mismatches')}")
    a = inputs("trained", "train")
    a[a.index("--expect") + 1] = os.path.join(F, "expect-random-train.mlpe")
    rc, so, se, j = run(host, ["--ref", "--ref-groups", "2"] + a + ["--pins", pins], tmp)
    j = j or {}
    case("--ref negative control (trained weights, random's expected file)", rc == 1 and j.get("status") == "FAIL",
         f"rc {rc}, status {j.get('status')}, label mismatches {j.get('ref_label_mismatches')}")
    bad_pins = os.path.join(tmp, "PINS-bad")
    with open(pins) as fi, open(bad_pins, "w") as fo:
        for ln in fi:
            if ln.strip().endswith("mnist-int8-trained.mlpw"):
                ln = "0" * 64 + ln[64:]
            fo.write(ln)
    rc, so, se, j = run(host, ["--dry"] + inputs("trained", "train") + ["--pins", bad_pins], tmp)
    j = j or {}
    case("a wrong pin refused", rc == 2 and j.get("status") == "REFUSED" and j.get("pins") == "FAIL",
         f"rc {rc}, status {j.get('status')}, pins {j.get('pins')}")
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    bad = [n for n, ok in res if not ok]
    print(f"HOST-BEHAVIOUR OK: {len(res)} of {len(res)}" if not bad else f"HOST-BEHAVIOUR FAIL: {', '.join(bad)}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
