#!/usr/bin/env python3
"""E195's kit (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): the dry listing the session's dry pass is checked against.

    python3 -I -B drylisting_e195.py <scratch dir> [--write]

It runs the kit's runner (runitems_e195.py) in its own dry mode (--dry: every device call printed, nothing opened) for the smoke 901 and
each of passes 910-917, exactly as block_e195.sh calls it (the same arguments, --card aifoundry3, the kit's --no-ms manifest
gen-e195-noms/), and takes every "DRY hold10:" line in order, each pass's STOP path written <OUT>/p<pass>/STOP. Then it checks the
listing against the REGISTRATION's (desk/dry-e195-aifoundry3.txt, made with runitems.py unchanged and the registered default manifest):
call for call equal, but that every x09mem_host call carries " --no-ms" at its end (the kit's reading of E195.md section 4) and nothing
else differs. With --write it writes desk/dry-e195-noms-aifoundry3.txt. Prints DRYLISTING-E195 PASS or FAIL. No device is opened
(the runner's dry mode runs no command; run it in the no-device sandbox all the same). SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
STOPF = re.compile(r"--stop-file \S*/(p[0-9]+)/STOP")
SMOKE = ("901", "anchor_pi,x9_rd_rnd,x9_wr_u4,x9_wrh_rnd,x9_wrh_nst")
PASSES = [(str(p), "anchor_pi,x9_") for p in range(910, 918)]


def calls(text):
    return [STOPF.sub(r"--stop-file <OUT>/\1/STOP", ln) for ln in text.splitlines() if ln.startswith("DRY hold10: ")]


def run(scratch, p, items):
    out = os.path.join(scratch, "x09-dry", "p" + p)
    cmd = [sys.executable, "-I", "-B", os.path.join(E, "runitems_e195.py"), out, "--root", REPO, "--gen", os.path.join(E, "gen-e195-noms"),
           "--items", items, "--tool", "build/x09mem/host/x09mem_host", "--tel-live", os.path.join(out, "telemetry.jsonl.raw"),
           "--heater", "build/sparsity/host/sparsity_host", "--sparsity", "build/sparsity/host/sparsity_host", "--blocks", "1",
           "--first-block", p, "--seed", p, "--target", "58", "--preheat", "59", "--max-c", "70", "--item-s", "4", "--fma-s", "4",
           "--burnin", "2", "--card", "aifoundry3", "--dry"]
    r = subprocess.run(cmd, capture_output=True, text=True, env={"PATH": os.environ.get("PATH", "/usr/bin:/bin")})
    if r.returncode != 0:
        raise SystemExit(f"DRYLISTING-E195 FAIL: the runner's dry mode exited {r.returncode} for p{p}: {r.stderr[-300:]}")
    return calls(r.stderr)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    scratch = argv[0]
    os.makedirs(scratch, exist_ok=True)
    got = []
    per = {}
    for p, items in [SMOKE] + PASSES:
        c = run(scratch, p, items)
        per[p] = len(c)
        got += c
    reg = calls(open(os.path.join(E, "desk", "dry-e195-aifoundry3.txt")).read())
    want = [ln + " --no-ms" if "x09mem_host" in ln else ln for ln in reg]
    bad = []
    if len(got) != len(want):
        bad.append(f"{len(got)} calls against the registration's {len(want)}")
    for i, (a, b) in enumerate(zip(got, want)):
        if a != b:
            bad.append(f"call {i + 1}: {a!r} against {b!r}")
            break
    nx = sum(1 for ln in got if "x09mem_host" in ln)
    nn = sum(1 for ln in got if "x09mem_host" in ln and ln.endswith(" --no-ms"))
    print(f"calls per pass: {per}; x09mem_host calls {nx}, each ending --no-ms: {nn}; sparsity_host calls {len(got) - nx}")
    if "--write" in argv[1:]:
        with open(os.path.join(E, "desk", "dry-e195-noms-aifoundry3.txt"), "w") as f:
            f.write("# E195's kit: the dry pass's expected device calls on aifoundry3 (desk/drylisting_e195.py; runitems_e195.py --dry, "
                    "gen-e195-noms/; the registration's listing with --no-ms on every x09mem_host call)\n")
            for ln in got:
                f.write(ln + "\n")
        print("written desk/dry-e195-noms-aifoundry3.txt")
    if bad:
        print("DRYLISTING-E195 FAIL: " + "; ".join(bad))
        return 1
    print(f"DRYLISTING-E195 PASS: {len(got)} device calls (the smoke's {per['901']} and 35 for each of the 8 passes), equal call for call "
          f"to the registration's listing for aifoundry3 (runitems.py unchanged, the default manifest) but for ' --no-ms' at the end of "
          f"each of the {nx} x09mem_host calls; the order unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
