#!/usr/bin/env python3
"""E189's host check (Q167, the kit, Thu 12 Nov 2026, before any E189 datum): the two hosts E189 runs, read from their BEHAVIOUR, never
from a string grepped out of their bytes (E183's kit note 4's lesson; Q166's critic, 6(a)). Python's own modules only.

    python3 -B tools/claims-v3/e189/hostcheck_e189.py ledger <ledger_host>                 # from the tree's root
    python3 -B tools/claims-v3/e189/hostcheck_e189.py spp <sparseparity_host> [--selftest-bin <spp_selftest>]
    python3 -B tools/claims-v3/e189/hostcheck_e189.py --make <a desk build of the ledger host>   # writes hostcheck-e189.json
    python3 -B tools/claims-v3/e189/hostcheck_e189.py --check-json                               # the frozen lines against their sources

The ledger host (workloads/ledger at 46a16bd0) must:
  L1 print the FIPS 180-2 self-test exactly (`--selftest`: four vectors OK, SELFTEST PASS), rc 0;
  L2 print, for each of E189's five ledger configurations with its K (`--dry <args> --launches K`), exactly the JSON line frozen in
     hostcheck-e189.json (participants 2,048, the configuration's sizes, the guard's model, status DRY), rc 0;
  L3 refuse a run with no device flag (rc 2, "give exactly one of --sysemu, --card, --dry");
  L4 refuse --budget 9.6 (rc 2, "--budget at most 9.5 s": every process ends inside 10 s);
  L5 refuse --launches 101 (rc 2, "--launches 1-100");
  L6 read --expect: a missing file is refused (rc 2, "cannot read <file>") before any device;
sparse parity's host (workloads/sparseparity, the 29 Sep sources) must:
  S1 print for E189's instance (`--dry` with E189's whole argument list) exactly the committed --dry line of Q166's progs folder
     (runs/p2-dry/new-dry.json, made by the box's own build), rc 0;
  S2 refuse an unknown option (rc 2) with a usage line that offers --variant m4|m1 (energy.sh's own behavioural check of its host);
  S3 (with --selftest-bin) its CPU-only self-test prints SELFTEST PASS, rc 0.
Every run here returns before any device can open, by the sources (--selftest, --dry and the option checks all come before
Session's constructor); none passes --card or --sysemu; each is bounded at 20 s. On the desk, E189_DEVICE_RECORD shows they reach no
device call (desk/desktest_hosts_e189.sh). Prints HOST-BEHAVIOUR OK <ledger|spp> (<n> checks) or HOST-BEHAVIOUR FAIL <...>: <why>.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
JSON = os.path.join(HERE, "hostcheck-e189.json")
SPP_DRY = "docs/reports/data/2026-11-12-q166-progs/runs/p2-dry/new-dry.json"
LEDGER_KEYS = ["copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled"]


def run(argv):
    try:
        r = subprocess.run(argv, cwd=REPO, capture_output=True, text=True, timeout=20, stdin=subprocess.DEVNULL)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except OSError as e:
        return 127, "", str(e)


def plan_args():
    p = json.load(open(os.path.join(HERE, "plan-e189.json")))
    return {k: p["configs"][k]["args"] for k in LEDGER_KEYS}, p["configs"]["sparse-parity"]["args"]


def check_ledger(host, J):
    bad = []
    rc, so, se = run([host, "--selftest"])
    if rc != 0 or so.strip() != J["ledger_selftest"]:
        bad.append(f"L1 --selftest rc {rc}")
    args, _ = plan_args()
    for k in LEDGER_KEYS:
        rc, so, se = run([host, "--dry"] + args[k].split())
        if rc != 0 or so.strip() != J["ledger_dry"][k]:
            bad.append(f"L2 {k} --dry rc {rc}: {so.strip()[:120]!r}")
    for tag, argv, want in (("L3", ["--prog", "copy"], "give exactly one of --sysemu, --card, --dry"),
                            ("L4", ["--dry", "--prog", "copy", "--budget", "9.6"], "--budget at most 9.5 s"),
                            ("L5", ["--dry", "--prog", "copy", "--launches", "101"], "--launches 1-100"),
                            ("L6", ["--dry", "--prog", "sha256", "--block", "2048", "--repeat", "1", "--expect",
                                    "/nonexistent/e189-expect.txt"], "cannot read /nonexistent/e189-expect.txt")):
        rc, so, se = run([host] + argv)
        first = (se.splitlines()[0] if se.splitlines() else "").replace(host, "<host>")
        if rc != 2 or not first.endswith(want) or so.strip():
            bad.append(f"{tag} rc {rc}: {first[:100]!r}")
    return bad, 10


def check_spp(host, J, selftest_bin=None):
    bad = []
    _, sargs = plan_args()
    rc, so, se = run([host, "--dry"] + sargs.split())
    want = open(os.path.join(REPO, SPP_DRY)).read().strip()
    if rc != 0 or so.strip() != want:
        bad.append(f"S1 --dry rc {rc}: {so.strip()[:120]!r}")
    rc, so, se = run([host, "--no-such-option"])
    if rc != 2 or "unknown option --no-such-option" not in se or "[--variant m4|m1]" not in se:
        bad.append(f"S2 an unknown option rc {rc}")
    n = 2
    if selftest_bin:
        n = 3
        rc, so, se = run([selftest_bin])
        if rc != 0 or not so.strip().endswith("SELFTEST PASS"):
            bad.append(f"S3 spp_selftest rc {rc}")
    return bad, n


def make(host):
    J = {"what": "E189's host check: the ledger host's frozen outputs (made from a desk build at 46a16bd0's sources and checked on four "
                 "builds by desk/desktest_hosts_e189.sh); sparse parity's --dry line is the committed one (SPP_DRY)",
         "ledger_selftest": run([host, "--selftest"])[1].strip(), "ledger_dry": {}, "spp_dry_file": SPP_DRY,
         "spp_dry_sha256": hashlib.sha256(open(os.path.join(REPO, SPP_DRY), "rb").read()).hexdigest(),
         "kernels": {"ledger": {"elf_sha256": "78708041a22c28bd4c4fff59c1a0f7373f03a6b71d22decd559bc050db6890db",
                                "text_sha256": "5e00e45ad0ae204781a451de8f1c807e74719a137ef28e1d517933f6b7d97e40",
                                "source": "docs/reports/data/2026-11-12-q166-progs/build/BUILD-INFO.txt and its dated note 1"},
                     "spp": {"elf_sha256": "65dd07dac840d9895fc06272dc234677fde66e4c06368422d7d438bce44f6ad5",
                             "text_sha256": "3e14be325df307751f424372d0a1dccad244b3ffe0e46e43d82baefb300cb820",
                             "source": "docs/reports/data/2026-11-12-q166-counter-sparseparity/kernel/kernel.sha256"}}}
    args, _ = plan_args()
    for k in LEDGER_KEYS:
        J["ledger_dry"][k] = run([host, "--dry"] + args[k].split())[1].strip()
    with open(JSON, "w") as f:
        json.dump(J, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"wrote {os.path.relpath(JSON, REPO)}")
    return 0


def check_json(J):
    bad = []
    if hashlib.sha256(open(os.path.join(REPO, SPP_DRY), "rb").read()).hexdigest() != J["spp_dry_sha256"]:
        bad.append("the committed sparse-parity --dry line changed")
    args, _ = plan_args()
    for k in LEDGER_KEYS:
        d = json.loads(J["ledger_dry"][k])
        a = args[k].split()
        if d.get("status") != "DRY" or d.get("participants") != 2048 or d.get("prog") != a[a.index("--prog") + 1]:
            bad.append(f"{k}: {J['ledger_dry'][k][:80]}")
    for kind, src, key in (("ledger", "docs/reports/data/2026-11-12-q166-progs/build/BUILD-INFO.dated-note-1.txt", "text_sha256"),
                           ("spp", "docs/reports/data/2026-11-12-q166-counter-sparseparity/kernel/kernel.sha256", "text_sha256")):
        if J["kernels"][kind][key] not in open(os.path.join(REPO, src)).read():
            bad.append(f"{kind} .text pin not in {src}")
    if J["kernels"]["ledger"]["elf_sha256"] not in open(os.path.join(REPO, "docs/reports/data/2026-11-12-q166-progs/build/BUILD-INFO.txt")).read():
        bad.append("ledger ELF pin")
    if J["kernels"]["spp"]["elf_sha256"] not in open(os.path.join(REPO, "docs/reports/data/2026-11-12-q166-counter-sparseparity/kernel/kernel.sha256")).read():
        bad.append("spp ELF pin")
    print("HOSTCHECK-JSON " + ("CHECK PASS" if not bad else "CHECK FAIL: " + "; ".join(bad)))
    return 0 if not bad else 1


def main(argv):
    if argv[:1] == ["--make"] and len(argv) == 2:
        return make(argv[1])
    J = json.load(open(JSON))
    if argv[:1] == ["--check-json"]:
        return check_json(J)
    if len(argv) < 2 or argv[0] not in ("ledger", "spp"):
        print(__doc__)
        return 2
    kind, host = argv[0], argv[1]
    if kind == "ledger":
        bad, n = check_ledger(host, J)
    else:
        sb = argv[argv.index("--selftest-bin") + 1] if "--selftest-bin" in argv else None
        bad, n = check_spp(host, J, sb)
    if bad:
        print(f"HOST-BEHAVIOUR FAIL {kind}: " + "; ".join(bad))
        return 1
    print(f"HOST-BEHAVIOUR OK {kind} ({n} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
