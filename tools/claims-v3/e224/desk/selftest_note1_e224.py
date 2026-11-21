#!/usr/bin/env python3
"""E224's kit (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum): THE SELF-TEST OF STEP 6n's JUDGEMENT (desk/neverrun_card_e224.py
run), E224's form of E220's SELFTEST-NOTE1: the REAL registered scanner (desk/neverrun_e224.py at its registered sha256) and the kit's wider scan
run for real, by the tool itself, over a STAND-IN LAB (a folder whose tools/ is the lab clone's own tools/, read only through a symbolic link,
and whose docs/reports/data/ holds five stand-in folders) and a STAND-IN LANES folder, each planting one arm A point's shape token in a session
record. The cases (E224.md 4: a point counts as run on its arm's card only by a session record on that card, dated note 1's reading; E224's
scanner never opens a name holding e220, e222 or e224; the kit's wider scan opens e220's and e222's, never e224's):
  N1 d02's token in a committed-data-form folder naming aifoundry1 card 1: the registered scan and the wider scan both read it run: LABELLED
  N2 d03's token in a folder naming e220 and aifoundry1 card 1 (E220's own sessions' form): the registered scan never opens it, the wider scan
     reads it run: LABELLED (the wider scan's reason to exist)
  N3 d12's token in a folder naming e224 and the card: never opened by either scan: not labelled
  N4 d07's token in a card-less lane copy (W/out/data-*/work/, a desk copy naming no card): never a session record on the card: not labelled;
     the literal reading (REPORTED) reads it run in both scans
  N5 d08's token in E224's own card lane (W/out/card-e224a/runs/...): never opened: not labelled
  N6 the labels file is the scorer's form, every label a registered point of arm A (check-labels: LABELS-OK) and a foreign id refused (10)
  N7 the tool's DIR holds both scans' reports (registered/, wider/), the two together in DIR/neverrun-e224.json and .txt, the judgement and its line

    bash W/slot.sh bash W/nodev.sh /usr/bin/python3 -I -B tools/claims-v3/e224/desk/selftest_note1_e224.py <empty scratch dir>
Prints one line a case and SELFTEST-NOTE1-E224 <n> of <m> PASS last. Writes only in its scratch folder. Standard library only (the scanner
reads MM1-v3.2's measured points through its data loader, numpy through it: run inside the round's slot, single-threaded).
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
TOOL = os.path.join(HERE, "neverrun_card_e224.py")


def rec(token):
    return ('SPARSITY {"test":"fma","arm":"%s","gen":"randn","type":"fp32","pattern":"none","values":"%s:randn:tools/claims-v3/kinds/tiles/fp32/'
            'randn.bin","minions":1024,"shire_mask":"0xffffffff","iters":1,"passes":1,"launch":0,"ok":true}\n' % (token, token))


def put(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    S = os.path.abspath(argv[0])
    if S == REPO or S.startswith(REPO + os.sep):
        print("the scratch directory must be outside the repository")
        return 2
    os.makedirs(S, exist_ok=True)
    if os.listdir(S):
        print("give an empty scratch directory")
        return 2
    lab, lanes, out = os.path.join(S, "lab"), os.path.join(S, "lanes"), os.path.join(S, "nr")
    os.makedirs(os.path.join(lab, "docs", "reports", "data"))
    os.symlink(os.path.join(REPO, "tools"), os.path.join(lab, "tools"))
    D = os.path.join(lab, "docs", "reports", "data")
    put(os.path.join(D, "2026-11-20-x01-standin-aifoundry1-c1", "session", "runs", "001-x", "proc-00.out"), rec("gemmL1x5x1"))     # d02
    put(os.path.join(D, "2026-11-20-e220-standin-aifoundry1-c1", "session", "runs", "001-x", "proc-00.out"), rec("gemmL1x8x2"))   # d03
    put(os.path.join(D, "2026-11-20-e224-standin-aifoundry1-c1", "session", "runs", "001-x", "proc-00.out"), rec("gemmL4x2x5"))   # d12
    put(os.path.join(D, "README.md"), "stand-in\n")
    put(os.path.join(lanes, "data-x04", "work", "reg-tree", "configs.json"), json.dumps({"tokens": ["gemmL1x3x3"]}) + "\n")         # d07
    put(os.path.join(lanes, "card-e224a", "runs", "001-x", "proc-00.out"), rec("gemmL4x2x2"))                                       # d08
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    env.pop("RB_DESKTEST", None)
    env.pop("E224_NR_SCANNER", None)
    r = subprocess.run([sys.executable, "-I", "-B", TOOL, "run", out, "--arm", "A", "--lab", lab, "--lanes", lanes], capture_output=True, text=True,
                       env=env)
    open(os.path.join(S, "run.txt"), "w").write(r.stdout + r.stderr)
    n = ok = 0

    def case(name, good, words):
        nonlocal n, ok
        n += 1
        ok += 1 if good else 0
        print(f"{name}: {'PASS' if good else 'FAIL'} - {words}", flush=True)

    if r.returncode != 0:
        print(f"the tool ended rc {r.returncode}: {(r.stdout + r.stderr)[-600:]}")
        print("SELFTEST-NOTE1-E224 0 of 7 FAIL")
        return 1
    J = json.load(open(os.path.join(out, "judge-e224-A.json")))
    L = json.load(open(os.path.join(out, "labels-e224-A.json")))["ran_before_points"]["A"]
    ran_r, ran_w = J["scans"]["registered"]["ran_of_arm"], J["scans"]["wider"]["ran_of_arm"]
    lit = J["literal_reading_REPORTED"]["ran_before"]
    case("N1", "d02" in L and "d02" in ran_r and "d02" in ran_w, f"d02 (a session record on the card): registered {'d02' in ran_r}, wider {'d02' in ran_w}, labelled {'d02' in L}")
    case("N2", "d03" in L and "d03" not in ran_r and "d03" in ran_w,
         f"d03 (a folder naming e220 and the card): registered {'d03' in ran_r} (never opened), wider {'d03' in ran_w}, labelled {'d03' in L}")
    case("N3", "d12" not in L and "d12" not in ran_r + ran_w, f"d12 (a folder naming e224): never opened by either scan, labelled {'d12' in L}")
    case("N4", "d07" not in L and "d07" in lit["registered"] and "d07" in lit["wider"],
         f"d07 (a card-less desk copy): labelled {'d07' in L}; the literal reading (REPORTED) reads it run: {'d07' in lit['registered']} / {'d07' in lit['wider']}")
    case("N5", "d08" not in L and "d08" not in lit["registered"] + lit["wider"], f"d08 (E224's own card lane card-e224a): never opened, labelled {'d08' in L}")
    c1 = subprocess.run([sys.executable, "-I", "-B", TOOL, "check-labels", os.path.join(out, "labels-e224-A.json"), "--arm", "A"], capture_output=True, text=True)
    bad = os.path.join(S, "bad-labels.json")
    json.dump({"ran_before_points": {"A": ["d02", "x999"]}}, open(bad, "w"))
    c2 = subprocess.run([sys.executable, "-I", "-B", TOOL, "check-labels", bad, "--arm", "A"], capture_output=True, text=True)
    case("N6", sorted(L) == ["d02", "d03"] and c1.returncode == 0 and c1.stdout.startswith("LABELS-OK") and c2.returncode == 10,
         f"labels {sorted(L)}; check-labels rc {c1.returncode} '{c1.stdout.strip()[:60]}', a foreign id rc {c2.returncode}")
    nj = json.load(open(os.path.join(out, "neverrun-e224.json")))
    files = all(os.path.exists(os.path.join(out, p)) for p in ("registered/scan-e224-reg.json", "registered/neverrun-e224.json", "wider/scan-e224-reg.json",
                                                               "wider/neverrun-e224.json", "neverrun-e224.txt", "judge-e224-A.txt"))
    line = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    case("N7", files and set(nj) >= {"registered", "wider"} and line.startswith("NEVER-RUN-E224 arm A: 62 of 64") and
         (J.get("kit_wider_scan") or {}).get("read_here_never_by_the_registered_scan", {}).get("data_folders") == ["2026-11-20-e220-standin-aifoundry1-c1"],
         f"both reports and the judgement in DIR: {files}; the line '{line[:120]}'; the wider scan read {J.get('kit_wider_scan', {}).get('read_here_never_by_the_registered_scan')}")
    print(f"SELFTEST-NOTE1-E224 {ok} of {n} {'PASS' if ok == n else 'FAIL'}")
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
