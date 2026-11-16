#!/usr/bin/env python3
"""E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): the kit's small checks, in one log (logs/checks-e200.txt). E197's
(tools/claims-v3/e197/desk/checks_e197.py, unchanged beside it) for E200:
  1. harness-e200.json re-made equals the committed one (CHECK PASS) and every file of it at its sha256 (HARNESS OK);
  2. the history check's names (sys.stdlib_module_names, the day's own modules, the folders read);
  3. THE KIT'S CHECKER ON THE REGISTRATION'S OWN SYNTHETIC GOVERNED SESSIONS (E200's desk/synth_session_e200.py, with its arbitrary test
     values, not a forecast and not a measurement; E200's registered reduction reduce_e200.py run unchanged, never with --prediction):
     for the governor, faults, noisy and nogov variants, `check_e200.py checks` reads the reduction's output and prints E197.md 8's rows
     with the clock row by C1 and THE CLOCK RULE's tallies (CHECKS READ): governor every process kept by the clock; faults the planted
     clock faults set aside by their clauses (a step to 700 MHz, a last launch at 600 MHz by its own count, a climb at 1.60 s) and the
     planted ones the rule keeps kept (a climb at 1.45 s, a sample with no clock field); nogov the session's median clock NOT 800, every
     process set aside; and `check_e200.py summary` on the synthetic sessions' own files; and the checker refuses E197's reducer's output
     (no "e200" key);
  4. drycmp: the W1 listing made from E197's registered full listing against it (SAME); E197's registered listing as a box listing (no W1
     window: DIFFERS); the W1 full listing against E197's short (DIFFERS);
  5. THE WAIT'S SESSION NAME ON THE REAL SCRIPT: step 10's `ours_live <name>` and step 11's box read name the script step 9 launches
     (session_e200.sh), read from the three files' own lines;
  6. the guard's mode: ettelem_guard_e200.sh executable (100755 in git): E197's run_session.sh runs "$ETTELEM" as a program;
  7. A FWGATE RECORD ADDED AFTER THE KIT, on a copy of the harness's files in the scratch dir: a stand-in record added under
     tools/claims-v3/fwgate/records/ (a copy of a committed record's bytes under a new name): --check CHECK PASS naming it, --list
     carrying it, --box HARNESS OK; a pinned record changed by one byte: CHECK FAIL; a pinned box file (session_e200.sh) changed by one
     byte: CHECK FAIL.
Prints CHECKS-E200 <n> of <m> PASS last. Standard library only; it opens no device.
    /usr/bin/python3 -I -B tools/claims-v3/e200/desk/checks_e200.py <the lab clone's top> <an empty scratch dir>
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import re
import shutil
import subprocess
import sys

E = "tools/claims-v3/e200"
E7 = "tools/claims-v3/e197"


def main(argv):
    top, s = argv[0], argv[1]
    os.makedirs(s, exist_ok=True)
    py = ["/usr/bin/python3", "-I", "-B"]
    rows = []

    def row(what, ok, detail=""):
        rows.append(bool(ok))
        print("%s %s%s" % ("ok  " if ok else "FAIL", what, ("  [" + str(detail)[:300] + "]") if detail != "" else ""), flush=True)

    def run(args, cwd=top):
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True)

    r = run(py + [E + "/harness_e200.py", "--check"])
    row("harness-e200.json re-made: " + r.stdout.strip(), r.returncode == 0 and r.stdout.startswith("CHECK PASS"))
    r = run(py + [E + "/harness_e200.py", "--box"])
    row("every harness file at its sha256: " + r.stdout.strip(), r.returncode == 0 and r.stdout.startswith("HARNESS OK"))
    r = run(py + [E + "/rb/check_history_e200.py", "names"])
    row("the history check's names: " + r.stdout.strip()[:220], r.returncode == 0 and "SHADOW NAMES:" in r.stdout)
    climbs = os.path.join(top, "tools/claims-v3/e194/desk/climb-e190.txt")
    for v in ("governor", "faults", "noisy", "nogov"):
        o = os.path.join(s, "synth-" + v)
        args = py + [E + "/desk/synth_session_e200.py", E7 + "/proposal/src/trains.tsv", E7 + "/desk/host-list-e197.jsonl", o,
                     "--plan", "full", "--variant", v]
        if os.path.exists(climbs):
            args += ["--climbs", climbs]
        r = run(args)
        if r.returncode != 0:
            row("the registration's synthetic governed session (%s)" % v, False, r.stderr[-200:])
            continue
        j = os.path.join(s, "regfile-%s.json" % v)
        r = run(py + [E + "/reduce_e200.py", o, "--out", j])
        row("E200's registered reduction on the synthetic %s session: rc 0" % v, r.returncode == 0, r.stderr[-200:])
        if r.returncode != 0:
            continue
        c = run(py + [E + "/check_e200.py", "checks", j, "--out", os.path.join(s, "checks-%s.json" % v)])
        last = c.stdout.strip().splitlines()[-1] if c.stdout.strip() else ""
        print("    | " + "\n    | ".join(c.stdout.strip().splitlines()[:2]))
        ck = json.load(open(os.path.join(s, "checks-%s.json" % v))) if c.returncode == 0 else {"checks": []}
        words = {x["verdict"] for x in ck["checks"]}
        clock = [x for x in ck["checks"] if x["check"].startswith("THE CLOCK RULE (C1)")]
        d = clock[0]["detail"] if clock else {}
        row("check_e200.py checks (%s): %s" % (v, last), c.returncode == 0 and last.startswith("CHECKS READ:") and
            words <= {"APPLIED", "PASS", "NOT SCORED", "REPORTED", "FLAGGED", "NOT COMPUTED", "NOT 800"} and len(clock) == 1)
        if v == "governor":
            row("governor: THE CLOCK RULE row APPLIED, 400 of 400 train processes kept by the clock, launches 0-4 not read",
                clock and clock[0]["verdict"] == "APPLIED" and d.get("processes_judged") == 400 and d.get("processes_kept_by_clock") == 400
                and d.get("launches_before_2s_not_read") == 2000, {k: d.get(k) for k in ("processes_judged", "processes_kept_by_clock",
                                                                                      "launches_before_2s_not_read")})
        if v == "faults":
            row("faults: the planted clock faults set aside by their clauses (samples after 1.5 s: the 700 MHz step and the 1.60 s climb; own "
                "count: the 600 MHz last launch), the rest kept (1.45 s climb, a sample with no clock)",
                d.get("set_aside_samples_after_allowance") == 2 and d.get("set_aside_own_count") == 1 and
                d.get("processes_kept_by_clock") == 397, {k: d.get(k) for k in ("set_aside_samples_after_allowance", "set_aside_own_count",
                                                                               "processes_kept_by_clock", "samples_without_clock")})
        if v == "nogov":
            row("nogov: the session's median clock NOT 800: the clock row reads NOT 800 and every process is set aside",
                clock and clock[0]["verdict"] == "NOT 800" and d.get("set_aside_median_clock") == 400, d.get("median_clock_mhz"))
        sm = run(py + [E + "/check_e200.py", "summary", o, "--plan", "full"])
        print("    | " + "\n    | ".join(sm.stdout.strip().splitlines()))
        row("check_e200.py summary on the %s session: 4 blocks complete, stop none" % v, "complete: 4 (A B C D)" in sm.stdout and
            "stop: none" in sm.stdout and "SITTING-RESULT: " in sm.stdout)
    o = os.path.join(s, "synth-governor")
    j7 = os.path.join(s, "regfile-e197reducer.json")
    r = run(py + [E7 + "/proposal/src/reduce_regfile.py", o, "--out", j7])
    c = run(py + [E + "/check_e200.py", "checks", j7])
    row("the checker refuses E197's reducer's output (no 'e200' key: not reduce_e200.py's), exit 3", r.returncode == 0 and c.returncode == 3
        and "CHECKS REFUSED" in c.stdout, c.stdout.strip()[:160])
    w1 = os.path.join(s, "w1-full.txt")
    with open(w1, "w") as f:
        for ln in open(os.path.join(top, E7, "desk/dry-e197-full.txt")):
            f.write(ln.replace("--window 240000000", "--window 320000000") if ln.startswith("DRY: timeout 10 ") else ln)
    r = run(py + [E + "/check_e200.py", "drycmp", w1, E7 + "/desk/dry-e197-full.txt", "--host", "build/host/regfile_host", "--out", "out-full"])
    row("drycmp: the W1 full listing against E197's registered full listing: LISTING SAME, 429 device calls, each with W1's window",
        r.returncode == 0 and r.stdout.startswith("LISTING SAME full: ") and "429 device calls, each with W1's window" in r.stdout, r.stdout.strip()[:160])
    r = run(py + [E + "/check_e200.py", "drycmp", E7 + "/desk/dry-e197-full.txt", E7 + "/desk/dry-e197-full.txt", "--host",
                  "build/host/regfile_host", "--out", "out-full"])
    row("drycmp's negative control: E197's own listing as a box listing (no W1 window): LISTING DIFFERS, exit 3", r.returncode == 3 and
        r.stdout.startswith("LISTING DIFFERS full: 429 device calls, 0 with W1's"), r.stdout.strip()[:160])
    r = run(py + [E + "/check_e200.py", "drycmp", w1, E7 + "/desk/dry-e197-short.txt", "--host", "build/host/regfile_host", "--out", "out-full"])
    row("drycmp's negative control: the W1 full listing against E197's short: LISTING DIFFERS, exit 3", r.returncode == 3 and
        r.stdout.startswith("LISTING DIFFERS"), r.stdout.strip()[:160])
    s20 = open(os.path.join(top, E, "rb/s20_wait_e200.sh")).read()
    s22 = open(os.path.join(top, E, "rb/s22_collect_e200.sh")).read()
    s11 = open(os.path.join(top, E, "rb/s11_session_e200.sh")).read()
    w = re.findall(r'ours_live (session_e\d+\.sh)\)', s20)
    c22 = re.findall(r'ours_live (session_e\d+\.sh)\)', s22)
    launched = re.findall(r'setsid nohup bash "\$ROOT/tools/claims-v3/e200/(session_e\d+\.sh)"', s11)
    row("the wait's session name on the real script: step 10 `ours_live %s`, step 11 `ours_live %s`, step 9 launches %s" % (w, c22, launched),
        w == ["session_e200.sh"] and c22 == ["session_e200.sh"] and launched == ["session_e200.sh"] and
        os.path.exists(os.path.join(top, E, "session_e200.sh")))
    r = run(["git", "ls-files", "-s", E + "/ettelem_guard_e200.sh"])
    mode = r.stdout.split()[0] if r.stdout.split() else os.stat(os.path.join(top, E, "ettelem_guard_e200.sh")).st_mode
    exe = os.access(os.path.join(top, E, "ettelem_guard_e200.sh"), os.X_OK)
    row("E200's guard is executable (E197's run_session.sh runs \"$ETTELEM\" sample as a program): working tree %s, git %s" % (
        "x" if exe else "-", mode if r.stdout.split() else "not committed yet"), exe and (not r.stdout.split() or mode == "100755"))
    # 7. a fwgate record added after the kit
    hn = os.path.join(s, "harness-records")
    lst = run(py + [E + "/harness_e200.py", "--list"]).stdout.split()
    for p in lst + [E + "/harness_e200.py"]:
        os.makedirs(os.path.dirname(os.path.join(hn, p)), exist_ok=True)
        shutil.copy2(os.path.join(top, p), os.path.join(hn, p))
    recs = sorted(p for p in lst if p.startswith("tools/claims-v3/fwgate/records/"))
    newrec = "tools/claims-v3/fwgate/records/aifoundry2-c0-2099-01-01-standin.json"
    shutil.copyfile(os.path.join(hn, recs[-1]), os.path.join(hn, newrec))
    hpy = py + [os.path.join(hn, E, "harness_e200.py")]
    r1 = run(hpy + ["--check"], cwd=hn)
    r2 = run(hpy + ["--list"], cwd=hn)
    r3 = run(hpy + ["--box"], cwd=hn)
    row("a fwgate record added after the kit (%d pinned records): --check %s; --list carries it: %s; --box: %s" % (
        len(recs), r1.stdout.strip()[-150:], newrec in r2.stdout.split(), r3.stdout.strip()),
        r1.returncode == 0 and r1.stdout.startswith("CHECK PASS") and "aifoundry2-c0-2099-01-01-standin.json" in r1.stdout and
        newrec in r2.stdout.split() and r3.returncode == 0 and r3.stdout.startswith("HARNESS OK"))
    for p in (recs[0], E + "/session_e200.sh"):
        q = os.path.join(hn, p)
        b = open(q, "rb").read()
        open(q, "ab").write(b"\n")
        r = run(hpy + ["--check"], cwd=hn)
        open(q, "wb").write(b)
        row("a pinned %s changed by one byte: %s" % ("record" if "records/" in p else "box file", r.stdout.strip()[:160]),
            r.returncode == 3 and r.stdout.startswith("CHECK FAIL") and p in r.stdout)
    n = sum(rows)
    print("\nCHECKS-E200 %d of %d %s" % (n, len(rows), "PASS" if n == len(rows) else "FAIL"))
    return 0 if n == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
