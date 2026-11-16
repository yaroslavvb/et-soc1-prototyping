#!/usr/bin/env python3
"""E197 (Q185, lane kit-e197, Sun 15 Nov 2026, before any E197 datum): the kit's small checks, in one log (logs/checks-e197.txt).
  1. harness-e197.json re-made equals the committed one (CHECK PASS) and every file of it at its sha256 (HARNESS OK);
  2. the history check's names (sys.stdlib_module_names, the day's own modules, the folders read);
  3. THE KIT'S CHECKER ON THE REGISTRATION'S OWN SYNTHETIC SESSIONS (desk/synth_session_e197.py, the registration's, with its arbitrary
     test values, not a forecast and not a measurement; the registered reducer run unchanged, never with --prediction): for the exact,
     noisy and stop variants, `check_e197.py checks` reads the reducer's output and prints E197.md 8's rows (CHECKS READ), each train's
     gate rows APPLIED or NOT SCORED as the reducer decided, every report row REPORTED or FLAGGED, nothing scored; and `check_e197.py
     summary` on the synthetic sessions' own files (the stop variant's hand-made STOP read as not naming the card);
  4. drycmp's negative control: the registration's full listing against its short one: LISTING DIFFERS.
Prints CHECKS-E197 <n> of <m> PASS last. Standard library only; it opens no device.
    /usr/bin/python3 -I -B tools/claims-v3/e197/desk/checks_e197.py <the lab clone's top> <an empty scratch dir>
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import subprocess
import sys

E = "tools/claims-v3/e197"


def main(argv):
    top, s = argv[0], argv[1]
    os.makedirs(s, exist_ok=True)
    py = ["/usr/bin/python3", "-I", "-B"]
    rows = []

    def row(what, ok, detail=""):
        rows.append(ok)
        print("%s %s%s" % ("ok  " if ok else "FAIL", what, ("  [" + str(detail)[:300] + "]") if detail != "" else ""), flush=True)

    def run(args, cwd=top):
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True)

    r = run(py + [E + "/harness_e197.py", "--check"])
    row("harness-e197.json re-made: " + r.stdout.strip(), r.returncode == 0 and r.stdout.startswith("CHECK PASS"))
    r = run(py + [E + "/harness_e197.py", "--box"])
    row("every harness file at its sha256: " + r.stdout.strip(), r.returncode == 0 and r.stdout.startswith("HARNESS OK"))
    r = run(py + [E + "/rb/check_history_e197.py", "names"])
    row("the history check's names: " + r.stdout.strip()[:220], r.returncode == 0 and "SHADOW NAMES:" in r.stdout)
    for v in ("exact", "noisy", "stop"):
        o = os.path.join(s, "synth-" + v)
        r = run(py + [E + "/desk/synth_session_e197.py", E + "/proposal/src/trains.tsv", E + "/desk/host-list-e197.jsonl", o,
                      "--plan", "full", "--variant", v])
        if r.returncode != 0:
            row("the registration's synthetic session (%s)" % v, False, r.stderr[-200:])
            continue
        j = os.path.join(s, "regfile-%s.json" % v)
        r = run(py + [E + "/proposal/src/reduce_regfile.py", o, "--out", j])
        row("the registered reducer on the synthetic %s session: rc 0" % v, r.returncode == 0, r.stderr[-200:])
        c = run(py + [E + "/check_e197.py", "checks", j, "--out", os.path.join(s, "checks-%s.json" % v)])
        last = c.stdout.strip().splitlines()[-1] if c.stdout.strip() else ""
        print("    | " + "\n    | ".join(c.stdout.strip().splitlines()[:3]))
        ck = json.load(open(os.path.join(s, "checks-%s.json" % v))) if c.returncode == 0 else {"checks": []}
        words = {x["verdict"] for x in ck["checks"]}
        row("check_e197.py checks (%s): %s" % (v, last), c.returncode == 0 and last.startswith("CHECKS READ:") and
            words <= {"APPLIED", "PASS", "NOT SCORED", "REPORTED", "FLAGGED", "NOT COMPUTED"})
        if v == "noisy":
            red = json.load(open(j))
            ns = [t for t, x in red["trains"].items() if x.get("sign") == "NOT SCORED" and x.get("units", 0) >= 8]
            row("the noisy session's T11 (F 0.3 % slower) read NOT SCORED by its F/S rate gate, as the checker prints it",
                "T11" in ns and any(x["check"].startswith("T11 gate: F and S") and x["verdict"] == "NOT SCORED" for x in ck["checks"]), ns)
        sm = run(py + [E + "/check_e197.py", "summary", o, "--plan", "full"])
        print("    | " + "\n    | ".join(sm.stdout.strip().splitlines()))
        if v == "stop":
            row("check_e197.py summary on the stop session: the hand-made STOP read as not naming the card",
                "stop: by hand: an empty STOP file (does not name the card)" in sm.stdout and "card stop none" in sm.stdout)
        else:
            row("check_e197.py summary on the %s session: 4 blocks complete, stop none" % v,
                "complete: 4 (A B C D)" in sm.stdout and "stop: none" in sm.stdout)
    r = run(py + [E + "/check_e197.py", "drycmp", E + "/desk/dry-e197-full.txt", E + "/desk/dry-e197-short.txt", "--host",
                  "build/host/regfile_host", "--out", "out-full"])
    row("drycmp's negative control (the full listing against the short one): LISTING DIFFERS, exit 3", r.returncode == 3 and
        r.stdout.startswith("LISTING DIFFERS"), r.stdout.splitlines()[0] if r.stdout else "")
    n = sum(rows)
    print("\nCHECKS-E197 %d of %d %s" % (n, len(rows), "PASS" if n == len(rows) else "FAIL"))
    return 0 if n == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
