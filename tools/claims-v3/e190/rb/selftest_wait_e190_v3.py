#!/usr/bin/env python3
"""E190's kit dated note 2 (Q177, lane note2-e190, Sat 14 Nov 2026, after E190's first card day and before any later E190 day): the desk
tests of step 10 v3 (rb/s20_wait_e190_v3.sh) beside step 10 v2 (rb/s20_wait_e190_v2.sh, note 1's, unchanged), each step run for real:
the step script itself, its desk side (k6's rb_common.sh, v3.1's rb_run.py, rb_e190.sh and rb_e190_v2.sh, all unchanged) and its remote
script, which a stand-in ssh serves with `bash -s` on two stand-in boxes under the scratch directory (aifoundry2's
~/claude/et-soc1-prototyping, aifoundry1's ~/nekko); the stand-in refuses any other host or command, and the stand-in rsync and scp refuse
everything. No lab box is reached and no device is opened: every input is a text file, and the only process this test starts beside the
steps is a stand-in session script that sleeps (named session_e190_v2.sh, as the runbook counts the v2 session), in a private PID
namespace (rb/selftest_wait_e190_v3.sh), so that nothing outside the test can see it.

    bash tools/claims-v3/e190/rb/selftest_wait_e190_v3.sh <an empty scratch dir outside the repo> desk|real > <log>
    (it runs /usr/bin/python3 -I -B tools/claims-v3/e190/rb/selftest_wait_e190_v3.py <scratch dir> desk|real in the namespace)

desk (ready-e190's W1-W4 of Fri 13 Nov 2026, on the real path's own session logs: the runner run_e190_v2.py without --dry, with a
stand-in reader, et-who and host, as committed in logs/realpath-e190-v2.txt by note 1, bff31df2):
  W1 arm A, RA1 ended, its manifest written                                 want v3 0  (v2 16)
  W2 arm A, RA1's first 14 lines, a stand-in session_e190_v2.sh running      want v3 17 (v2 16)
  W3 arm B, RB2 (the identity gate: the start config names card 0), ended   want v3 16 (v2 16)
  W4 arm B, RB1 ended, its manifest written                                 want v3 0  (v2 16)
  then v2's other readings, which v3 keeps: W5 RA1's first 14 lines and no session process: RUN-GONE 14; W6 RB1 ended, no manifest:
  MANIFEST-ABSENT 14; W7 the box's T0 is not RB_OUT's: RUN-UNKNOWN 10; W8 the box's T0 written two days ago: RUN-UNKNOWN 10; W9 a stand-in
  running under the v1 name session_e190.sh only: not counted, RUN-GONE 14 (both count session_e190_v2.sh by its own name);
  X1-X12 each of the 12 real-path sessions in that log, ended with a manifest, against the runner's own exit printed there: v3 16 for each
  of its 8 rc-16 sessions (the gates) and 0 for each of its 4 rc-0 ones; v2 16 for all 12;
  D  the text: outside its comment lines v3 differs from v2 in exactly two lines (rb_init's step name; the pattern without
  "|the card.s identity: |the identity read \\("), and v3's pattern is the kit's v1 pattern (rb/s20_wait_e190.sh) byte for byte.
real (E190's card day as committed, docs/reports/data/2026-11-13-e190-large-gemm/, data commit a6fafba4):
  R1-R5 card-e190's five step-10 calls (the data README's departure 3: arm A RUNNING at 16:16:53, ENDED at 16:25:01; arm B RUNNING at
     16:17:38 and 16:26:34, ENDED at 16:28:12), each arm's committed session log cut at that time, with a stand-in session_e190_v2.sh
     running where the session still ran and the committed MANIFEST.sha256 where it had ended: v3 17, 17, 0, 17, 0; v2 16 on all five (as
     card-e190 met); v3 prints the same session lines as v2, without GATE-STOPPED;
  R6, R7 each arm's log cut just after its start config line (the identity gate passed, the session running): v3 17 (v2 16);
  G1-G11 a real gate-stop line written as a test input at its place in an arm's real log, then the runner's closing lines and a manifest:
     G1 arm B's identity gate on card 0's config (the line made by e190_note1.config_identity from aifoundry2's committed start config read
     and its stderr, in run_e190_v2.py's form); G2 the identity read (RB3's line), G3 the smoke on another card (RB4's two lines), G4 the
     lock held (RA2's), G5 a holder (RA4's), G6 the box check (RA5's), all from logs/realpath-e190-v2.txt; G7 no card lock, G8 the lock
     unopenable, G9 the start config not the registered one, G10 the sampler would not start, G11 the stop-path test failed, each in
     run_e190_v2.py's own words (no real-path session printed those five): v3 16 (v2 16); G12 G1's input with the session still running
     (no session end yet): v3 16 (v2 16);
  T1, T2 a stop tripped in the runs (the identity stop, I7's words in logs/selftest-run-e190-v2.txt; a board line, S1's): the runner
     ends rc 0 and v3 reads the session as ended, 0, with its "STOP:" line among the lines it prints (v2 16);
  P  the patterns over every line, by grep -E as the steps run it: both card-day logs (v3 0 hits; v2 the two start config lines), the 12
     real-path sessions (v3 exactly the 8 rc-16 ones; v2 all 12), the gate lines G1-G11 (v3 11 of 11) and the STOP lines of T1-T2 (v3 0).
Both modes end with Z: every call the stand-in ssh served was `true` or `bash -s` to a stand-in box, and no stand-in session is left.
Each case runs v3, then v2, on the same input (a fresh T0, session directory and RB_OUT for each call; RB_WAIT_LOOP_S=6, so a call on a
running session reads RUNNING after one 15 s sleep of the remote loop). Each call's whole output is kept as <scratch>/out/<case>-<v>.txt.
Prints one line a case, then SELFTEST-WAIT-E190-V3 <n> of <m> PASS (desk) or REALREAD-WAIT-E190-V3 <n> of <m> PASS (real), or FAIL.
A desk check of code: nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
STEP = {"v1": os.path.join(HERE, "s20_wait_e190.sh"), "v2": os.path.join(HERE, "s20_wait_e190_v2.sh"),
        "v3": os.path.join(HERE, "s20_wait_e190_v3.sh")}
RP_LOG = os.path.join(E, "logs", "realpath-e190-v2.txt")
RUN_LOG = os.path.join(E, "logs", "selftest-run-e190-v2.txt")
DATA = os.path.join(REPO, "docs", "reports", "data", "2026-11-13-e190-large-gemm")
ARMDIR = {"A": "aifoundry2", "B": "aifoundry1-c1"}
BOX = {"A": "aifoundry2", "B": "aifoundry1"}
TREE = {"A": os.path.join("claude", "et-soc1-prototyping"), "B": "nekko"}
STAMP = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) [A-Z]{3,4} ")
ALT = "|the card.s identity: |the identity read \\("
# card-e190's five step-10 calls, Fri 13 Nov 2026 (the data README's departure 3): arm, time, the session still running then
CALLS = [("R1", "A", "2026-11-13 16:16:53", True), ("R2", "B", "2026-11-13 16:17:38", True), ("R3", "A", "2026-11-13 16:25:01", False),
         ("R4", "B", "2026-11-13 16:26:34", True), ("R5", "B", "2026-11-13 16:28:12", False)]
DROP_ENV = ("RB_DRY", "RB_DESKTEST", "RB_GITLOCK", "RB_OUT", "RB_LOCK", "RB_WAIT_LOOP_S", "V3_DRY", "V3_DEVICE", "ET_DEVICES")


def sha256(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class T:
    def __init__(self, S):
        self.n = self.ok = 0
        self.S = S

    def mask(self, s):
        s = s.replace(self.S, "<scratch>").replace(REPO, "<repo>")
        home = os.path.expanduser("~")
        return s.replace(home, "~") if home not in ("/", "") else s

    def case(self, name, good, detail):
        self.n += 1
        self.ok += 1 if good else 0
        print(self.mask(f"{name}: {'PASS' if good else 'FAIL'} - {detail}"), flush=True)


def pattern(step):
    """The GATE-STOPPED pattern of a step file (its `if grep -qE '...'` line), and that line's number."""
    for i, ln in enumerate(open(STEP[step]).read().split("\n"), 1):
        if ln.startswith("if grep -qE '"):
            return ln.split("grep -qE '", 1)[1].split("'", 1)[0], i
    raise SystemExit(f"no GATE-STOPPED pattern in {STEP[step]}")


def grep_hits(pat, lines, S):
    """grep -E (the steps' own tool) over lines: the indices of the lines that match."""
    p = os.path.join(S, "grep-input.txt")
    with open(p, "w") as f:
        f.write("\n".join(lines) + "\n")
    r = subprocess.run(["grep", "-nE", pat, p], capture_output=True, text=True)
    return [int(x.split(":", 1)[0]) - 1 for x in r.stdout.splitlines() if x]


# ---------------------------------------------------------------- the inputs
def realpath_sessions():
    """The committed real-path log's 12 sessions: {name: (lines, runner rc)} in order; each line exactly as the runner wrote it."""
    lines = open(RP_LOG).read().split("\n")
    assert any(ln.startswith("REALPATH-E190-V2 13 of 13 PASS") for ln in lines), "the committed real-path log is not 13 of 13 PASS"
    sess, rcs, cur, t0, name = {}, {}, None, None, None
    for ln in lines:
        m = re.search(r" session start \(T0 (\d+) = .*its files in ([AB]-R[AB]\d+)\)", ln)
        if m and STAMP.match(ln):
            cur, t0, name = [ln], m.group(1), m.group(2)
            continue
        if cur is not None:
            assert STAMP.match(ln), f"a line inside {name} without the runner's stamp: {ln[:80]}"
            cur.append(ln)
            if ln.endswith(f" session end (T0 {t0})"):
                sess[name], cur = cur, None
            continue
        m = re.match(r"^(R[AB]\d+): PASS - (.*)$", ln)
        if m:
            mm = re.search(r"the runner then rc (\d+)", m.group(2)) or re.match(r"rc (\d+)", m.group(2))
            if mm:
                rcs[m.group(1)] = int(mm.group(1))
    out = {}
    for n, ls in sess.items():
        out[n] = (ls, rcs[n.split("-")[1]])
    return out


def card_day(arm):
    d = os.path.join(DATA, ARMDIR[arm])
    txt = open(os.path.join(d, "session.log")).read()
    assert txt.endswith("\n")
    lines = txt[:-1].split("\n")
    t0 = re.search(r"session start \(T0 (\d+)", lines[0]).group(1)
    return lines, open(os.path.join(d, "MANIFEST.sha256")).read(), t0, d


def stamp_of(line):
    return line[:len("2026-11-13 16:16:53 PST")]


def restamp(line, like):
    """A line's text after its stamp, given the stamp of `like` (a test input written at its place in another log)."""
    m = STAMP.match(line)
    return stamp_of(like) + " " + line[m.end():] if m else stamp_of(like) + " " + line


def find(lines, needle):
    k = [i for i, ln in enumerate(lines) if needle in ln]
    assert len(k) == 1, f"{needle!r}: {len(k)} lines"
    return k[0]


# ---------------------------------------------------------------- the stand-ins
def standins(S):
    b = os.path.join(S, "bin")
    os.makedirs(b)
    with open(os.path.join(b, "ssh"), "w") as f:
        f.write(f"""#!/bin/bash
echo "ssh $*" >> "{S}/calls.log"
host=""; cmd=""
while [ $# -gt 0 ]; do case "$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "$host" ]; then host=$1; shift; else cmd="$*"; break; fi ;; esac; done
case "$host" in aifoundry1|aifoundry2) ;; *) echo "STAND-IN SSH: refusing host $host" >&2; exit 97 ;; esac
[ "$cmd" = true ] && exit 0
[ "$cmd" = "bash -s" ] || {{ echo "STAND-IN SSH: only 'bash -s' and 'true' are served (got: $cmd)" >&2; exit 97; }}
cd "{S}/box/$host" || exit 1
exec env HOME="{S}/box/$host" bash -s
""")
    for c in ("rsync", "scp"):
        with open(os.path.join(b, c), "w") as f:
            f.write(f'#!/bin/sh\necho "{c} $*" >> "{S}/calls.log"\necho "{c} refused by the desk test" >&2\nexit 97\n')
    for c in ("ssh", "rsync", "scp"):
        os.chmod(os.path.join(b, c), 0o755)
    for arm in "AB":
        os.makedirs(os.path.join(S, "box", BOX[arm], TREE[arm], "build", "q141k"))
    sd = os.path.join(S, "standin")
    for name in ("session_e190_v2.sh", "session_e190.sh"):
        d = os.path.join(sd, name.replace(".sh", ""))
        os.makedirs(d)
        with open(os.path.join(d, name), "w") as f:
            f.write("#!/bin/bash\n# a stand-in session process of the desk test: it only sleeps (at most 2 minutes)\n"
                    "for i in $(seq 1 120); do sleep 1; done\n")
    return b


class Runner:
    def __init__(self, S, t):
        self.S, self.t = S, t
        self.bin = standins(S)
        self.k = 0
        self.env0 = {k: v for k, v in os.environ.items() if k not in DROP_ENV and not k.startswith(("E190_", "RB_"))}
        self.env0["PATH"] = self.bin + os.pathsep + os.environ.get("PATH", "/usr/bin:/bin")

    def one(self, case, ver):
        """One call of step <ver> on the case's input; (rc, output)."""
        self.k += 1
        arm = case["arm"]
        t0 = 1794900000 + self.k
        tree = os.path.join(self.S, "box", BOX[arm], TREE[arm])
        tf = os.path.join(tree, "build", "q141k", f"e190{arm}.T0")
        with open(tf, "w") as f:
            f.write(f"{t0}\n")
        if case.get("stale"):
            old = time.time() - 2 * 86400
            os.utime(tf, (old, old))
        sd = os.path.join(tree, "build", "e190", f"T{t0}-{arm}")
        os.makedirs(sd)
        sl = os.path.join(sd, "session.log")
        with open(sl, "w") as f:
            f.write("\n".join(case["lines"]) + "\n")
        if case.get("manifest") == "standin":
            with open(os.path.join(sd, "MANIFEST.sha256"), "w") as f:
                f.write(f"{sha256(sl)}  session.log\n")
        elif case.get("manifest"):
            with open(os.path.join(sd, "MANIFEST.sha256"), "w") as f:
                f.write(case["manifest"])
        out = os.path.join(self.S, "out", f"{case['name']}-{ver}")
        os.makedirs(out)
        with open(os.path.join(out, f"e190-T0-{arm}.txt"), "w") as f:
            f.write(f"{t0 + (1 if case.get('t0_other') else 0)}\n")
        env = dict(self.env0, RB_OUT=out, RB_LOCK=os.path.join(self.S, "rb-lock.txt"), RB_WAIT_LOOP_S="6")
        sp = None
        if case.get("running"):
            name = "session_e190_v2.sh" if case["running"] == "v2" else "session_e190.sh"
            sp = subprocess.Popen(["bash", os.path.join(self.S, "standin", name.replace(".sh", ""), name)], start_new_session=True,
                                  stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=self.env0)
            time.sleep(0.5)
        try:
            r = subprocess.run(["bash", STEP[ver], arm], cwd=self.S, env=env, capture_output=True, text=True, timeout=200)
            rc, txt = r.returncode, r.stdout + r.stderr
        finally:
            if sp is not None:
                try:
                    os.killpg(sp.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                sp.wait(timeout=10)
        with open(os.path.join(self.S, "out", f"{case['name']}-{ver}.txt"), "w") as f:
            f.write(txt)
        return rc, txt


def markers(txt):
    return [ln.split(" (")[0] if ln.startswith("MANIFEST") else ln for ln in txt.splitlines()
            if re.match(r"^(RUN-[A-Z]+|GATE-STOPPED|MANIFEST-[A-Z]+)", ln)]


def printed_session_lines(txt):
    """The session lines the box printed (a stamp, then text); the box's own date line (a stamp alone) left out."""
    return [ln for ln in txt.splitlines() if STAMP.match(ln) and len(ln) > len("2026-11-13 16:16:53 PST")]


def short(ms):
    return ";".join(re.sub(r" after \d+ s$", "", m) for m in ms)


def run_case(R, t, case, extra=None):
    got = {}
    for ver in ("v3", "v2"):
        got[ver] = R.one(case, ver)
    r3, t3 = got["v3"]
    r2, t2 = got["v2"]
    ok = r3 == case["want"]["v3"] and r2 == case["want"]["v2"]
    m3, m2 = markers(t3), markers(t2)
    if case["want"]["v3"] in (0, 17):
        ok = ok and "GATE-STOPPED e190 arm " + case["arm"] not in m3
    note = ""
    if extra:
        good, note = extra(t3, t2)
        ok = ok and good
    stopl = [ln for ln in t3.splitlines() if "STOP:" in ln and ln.startswith("[s20_wait")]
    t.case(case["name"], ok, f"{case['what']}: v3 rc {r3} (want {case['want']['v3']}) [{short(m3)}]; v2 rc {r2} (want "
           f"{case['want']['v2']}) [{short(m2)}]" + (f"; v3 says: {stopl[0][len('[s20_wait_v3_e190] '):][:100]}" if stopl else "")
           + (f"; {note}" if note else ""))


def same_lines(t3, t2):
    a, b = printed_session_lines(t3), printed_session_lines(t2)
    return a == b and len(a) > 0, f"the session lines v3 printed are v2's ({len(a)} lines, the same: {a == b})"


def prints(needle):
    def f(t3, t2):
        good = any(needle in ln for ln in printed_session_lines(t3))
        return good, f"v3 printed the line holding {needle!r}: {good}"
    return f


# ---------------------------------------------------------------- the two modes
def desk(t, R, S):
    rp = realpath_sessions()
    ra1, rb1, rb2 = rp["A-RA1"][0], rp["B-RB1"][0], rp["B-RB2"][0]
    print(f"inputs: logs/realpath-e190-v2.txt sha256 {sha256(RP_LOG)}; sessions {len(rp)}: "
          + ", ".join(f"{n} rc {rc} ({len(ls)} lines)" for n, (ls, rc) in rp.items()), flush=True)
    W = [
        dict(name="W1", arm="A", lines=ra1, manifest="standin", want={"v3": 0, "v2": 16}, what="arm A, RA1 ended, its manifest written"),
        dict(name="W2", arm="A", lines=ra1[:14], running="v2", want={"v3": 17, "v2": 16},
             what="arm A, RA1's first 14 lines (to '" + ra1[13][24:60] + "'), a stand-in session_e190_v2.sh running"),
        dict(name="W3", arm="B", lines=rb2, manifest="standin", want={"v3": 16, "v2": 16}, what="arm B, RB2 (the identity gate on card 0's config) ended"),
        dict(name="W4", arm="B", lines=rb1, manifest="standin", want={"v3": 0, "v2": 16}, what="arm B, RB1 ended, its manifest written"),
        dict(name="W5", arm="A", lines=ra1[:14], want={"v3": 14, "v2": 14}, what="arm A, RA1's first 14 lines, no session process (RUN-GONE)"),
        dict(name="W6", arm="B", lines=rb1, want={"v3": 14, "v2": 14}, what="arm B, RB1 ended, no manifest (MANIFEST-ABSENT)"),
        dict(name="W7", arm="A", lines=ra1, manifest="standin", t0_other=True, want={"v3": 10, "v2": 10},
             what="arm A, the box's T0 is not RB_OUT's (RUN-UNKNOWN)"),
        dict(name="W8", arm="A", lines=ra1, manifest="standin", stale=True, want={"v3": 10, "v2": 10},
             what="arm A, the box's T0 file written two days ago (RUN-UNKNOWN)"),
        dict(name="W9", arm="A", lines=ra1[:14], running="v1", want={"v3": 14, "v2": 14},
             what="arm A, RA1's first 14 lines, a stand-in running under the v1 name session_e190.sh only (RUN-GONE)"),
    ]
    for c in W:
        run_case(R, t, c)
    for i, (n, (ls, rc)) in enumerate(rp.items(), 1):
        run_case(R, t, dict(name=f"X{i}", arm=n[0], lines=ls, manifest="standin", want={"v3": 16 if rc == 16 else 0, "v2": 16},
                            what=f"{n} (the runner's rc {rc}), ended, a manifest"))
    # D: the text
    v1, v2, v3 = (open(STEP[v]).read().split("\n") for v in ("v1", "v2", "v3"))
    c2 = [ln for ln in v2 if not ln.startswith("#")]
    c3 = [ln for ln in v3 if not ln.startswith("#")]
    diff = [(a, b) for a, b in zip(c2, c3) if a != b]
    p1, p2, p3 = pattern("v1")[0], pattern("v2")[0], pattern("v3")[0]
    good = len(c2) == len(c3) and len(diff) == 2 and diff[0] == ("rb_init s20_wait_v2", "rb_init s20_wait_v3") and \
        diff[1][1] == diff[1][0].replace(ALT, "") and p3 == p1 and p3 == p2.replace(ALT, "")
    t.case("D", good, f"code lines (outside comments) v2 {len(c2)}, v3 {len(c3)}, differing {len(diff)}: "
           f"{diff[0] if diff else None} and the pattern (v2's minus {ALT!r}: {p3 == p2.replace(ALT, '')}); v3's pattern is v1's: {p3 == p1}")


def real(t, R, S):
    import importlib
    sys.path.insert(0, E)
    N1 = importlib.import_module("e190_note1")
    CMN = importlib.import_module("e190_common")
    A, man_a, t0a, da = card_day("A")
    B, man_b, t0b, db = card_day("B")
    rp = realpath_sessions()
    print(f"inputs: aifoundry2/session.log sha256 {sha256(os.path.join(da, 'session.log'))} ({len(A)} lines, T0 {t0a}), MANIFEST "
          f"{len(man_a.splitlines())} lines; aifoundry1-c1/session.log sha256 {sha256(os.path.join(db, 'session.log'))} ({len(B)} lines, "
          f"T0 {t0b}), MANIFEST {len(man_b.splitlines())} lines; logs/realpath-e190-v2.txt sha256 {sha256(RP_LOG)}", flush=True)
    L = {"A": (A, man_a), "B": (B, man_b)}
    # R1-R5: card-e190's five calls
    for name, arm, when, running in CALLS:
        lines, man = L[arm]
        cut = [ln for ln in lines if stamp_of(ln)[:19] <= when]
        c = dict(name=name, arm=arm, lines=cut, running="v2" if running else None, manifest=None if running else man,
                 want={"v3": 17 if running else 0, "v2": 16},
                 what=f"arm {arm} at {when[11:]} (card-e190's call): {len(cut)} of {len(lines)} lines, "
                      + ("the session running" if running else "ended, the committed manifest"))
        run_case(R, t, c, same_lines)
    for name, arm in (("R6", "A"), ("R7", "B")):
        lines = L[arm][0]
        k = find(lines, " config start: ")
        run_case(R, t, dict(name=name, arm=arm, lines=lines[:k + 1], running="v2", want={"v3": 17, "v2": 16},
                            what=f"arm {arm}'s log to its start config line (the identity gate passed), the session running"), same_lines)
    # G: a real gate-stop line written as a test input
    cfg_a = open(os.path.join(da, "config-start.json")).read().strip()
    cfg_a_end = open(os.path.join(da, "config-end.json")).read().strip()
    err_a = open(os.path.join(da, "config-start.err")).read()
    idw = N1.config_identity("B", json.loads(cfg_a), err_a)
    assert idw, "config_identity read aifoundry2's start config as card 1"
    g1 = f"config start: {json.dumps(json.loads(cfg_a))}: the card's identity: {idw}: the gate, no launch"
    rpl = {n: ls for n, (ls, rc) in rp.items()}

    def rp_line(name, needle):
        return rpl[name][find(rpl[name], needle)]

    def close(lines, arm, opened=True, end=None):
        """The runner's closing lines: the closing config read (when a device was opened), then "session end"."""
        end = end or [ln for ln in L[arm][0] if " config end: " in ln][0]
        tail = [restamp(end, lines[-1])] if opened else []
        return lines + tail + [f"{stamp_of(lines[-1])} session end (T0 {t0a if arm == 'A' else t0b})"]

    def at(arm, upto, new):
        lines = L[arm][0]
        k = find(lines, upto)
        nxt = lines[k + 1]
        return lines[:k + 1] + [restamp(x, nxt) for x in new]

    lockp = CMN.ARMS["A"]["lock"]
    G = [
        ("G1", "B", at("B", " the box and the build: ", [g1]), True,
         "arm B's identity gate on card 0's config (e190_note1.config_identity on aifoundry2's committed start read)"),
        ("G2", "B", at("B", " stop-path test passed: ", [rp_line("B-RB3", " the identity read (the sampler running, before the smoke): ")]),
         True, "arm B, the identity read's stop (RB3's line)"),
        ("G3", "B", at("B", " smoke rest: ", [rp_line("B-RB4", " smoke fp32: "), rp_line("B-RB4", " smoke gate failed: ")]), True,
         "arm B, the smoke on another card (RB4's two lines)"),
        ("G4", "A", at("A", " the box and the build: ", [rp_line("A-RA2", "no device opened")]), False, "arm A, the lock held (RA2's line)"),
        ("G5", "A", at("A", " the box and the build: ", [rp_line("A-RA4", "no device opened")]), False, "arm A, a holder (RA4's line)"),
        ("G6", "A", at("A", " session start (", [rp_line("A-RA5", "no device opened")]), False, "arm A, the box check (RA5's line)"),
        ("G7", "A", at("A", " the box and the build: ", [f"no card lock {lockp} on this box (it is never created here): no device opened"]),
         False, "arm A, no card lock (run_e190_v2.py's words)"),
        ("G8", "A", at("A", " the box and the build: ", ["the card's lock cannot be opened (PermissionError): no device opened"]), False,
         "arm A, the lock unopenable (run_e190_v2.py's words)"),
        ("G9", "A", at("A", " the box and the build: ", [f"config start: config read rc 124, no JSON line: not {CMN.ARMS['A']['config']}: "
                                                        "the gate, no launch"]), True, "arm A, the start config not the registered one (run_e190_v2.py's words)"),
        ("G10", "A", at("A", " config start: ", ["the sampler would not start: no launch"]), True, "arm A, the sampler would not start (run_e190_v2.py's words)"),
        ("G11", "A", at("A", " sampler started ", ["stop-path test failed: board did NOT trip in 2.0 s, its file NOT touched, start NOT refused; "
                                                   "die tripped in 0.1 s, its file touched, start refused"]), True,
         "arm A, the stop-path test failed (run_e190_v2.py's words)"),
    ]
    gate_lines = []
    ends = {"G1": f"config end: {json.dumps(json.loads(cfg_a_end))}"}      # G1: card 0's own closing read (aifoundry2's, as committed)
    for name, arm, lines, opened, what in G:
        gate_lines.append(lines[-1])
        run_case(R, t, dict(name=name, arm=arm, lines=close(lines, arm, opened, ends.get(name)), manifest="standin",
                            want={"v3": 16, "v2": 16}, what=what + ", ended"))
    run_case(R, t, dict(name="G12", arm="B", lines=G[0][2], running="v2", want={"v3": 16, "v2": 16},
                        what="G1's input with no session end yet, the session running"))
    # T: a stop tripped in the runs (the runner ends rc 0): read as ended, its STOP line printed
    trip = "identity: the host named or held another card (holds /dev/et0_ops; stderr PCIe target /dev/et0_ops; stderr Physical device ID 0)"
    board = "board 90.0 W above 85 W on 3 samples in a row"
    runlog = open(RUN_LOG).read()
    assert "I7: PASS - rc 0; stop 'identity: the host named or held another card (holds /dev/et0_ops; stderr PCIe target /dev/et0_ops" in runlog
    assert "S1: PASS - rc 0; trip 'board 90.0 W above 85 W on 3 samples in a row'" in runlog
    stop_lines = []
    for name, arm, stop, what in (("T1", "B", trip, "arm B, the identity stop in run 01 (I7's words)"),
                                  ("T2", "A", board, "arm A, the board line in run 01 (S1's words)")):
        new = [f"run 01-P1-burst-fp32 done: 1 process(es), rc [0], checks ['approx'], a stop line tripped during this run: {stop}",
               f"STOP: {stop}: nothing further started"]
        lines = at(arm, " run 01-P1-burst-fp32: ", new)
        stop_lines += lines[-2:]
        run_case(R, t, dict(name=name, arm=arm, lines=close(lines, arm), manifest="standin", want={"v3": 0, "v2": 16}, what=what + ", ended"),
                 prints("STOP: " + stop[:20]))
    # P: the patterns over every line
    p2, p3 = pattern("v2")[0], pattern("v3")[0]
    h3 = {a: grep_hits(p3, L[a][0], S) for a in "AB"}
    h2 = {a: grep_hits(p2, L[a][0], S) for a in "AB"}
    good = not h3["A"] and not h3["B"] and len(h2["A"]) == 1 and len(h2["B"]) == 1 and \
        all(" config start: " in L[a][0][h2[a][0]] and "(read, nothing set); the card's identity: PCIe target" in L[a][0][h2[a][0]] for a in "AB")
    t.case("P1", good, f"both card-day logs, {len(A) + len(B)} lines: v3's pattern hits {len(h3['A']) + len(h3['B'])}; v2's hits "
           f"{len(h2['A']) + len(h2['B'])}: line {[h + 1 for h in h2['A']]} of arm A's and {[h + 1 for h in h2['B']]} of arm B's (the start config)")
    s3 = [n for n, (ls, rc) in rp.items() if grep_hits(p3, ls, S)]
    s2 = [n for n, (ls, rc) in rp.items() if grep_hits(p2, ls, S)]
    g16 = [n for n, (ls, rc) in rp.items() if rc == 16]
    t.case("P2", s3 == g16 and len(s2) == len(rp) == 12 and len(g16) == 8,
           f"the 12 real-path sessions: v3's pattern hits {len(s3)} ({', '.join(s3)}), exactly the runner's rc-16 ones: {s3 == g16}; v2's hits {len(s2)}")
    gh = grep_hits(p3, gate_lines, S)
    sh = grep_hits(p3, stop_lines, S)
    t.case("P3", len(gh) == len(gate_lines) == 11 and not sh,
           f"the gate lines G1-G11: v3's pattern hits {len(gh)} of {len(gate_lines)}; the stop lines of T1-T2: {len(sh)} of {len(stop_lines)}")


def main(argv):
    if len(argv) != 2 or argv[1] not in ("desk", "real"):
        print(__doc__)
        return 2
    S = os.path.abspath(argv[0])
    if S == REPO or S.startswith(REPO + os.sep):
        print("the scratch directory must be outside the repository")
        return 2
    if any(n.startswith("et") for n in os.listdir("/dev")):
        print("REFUSED: a /dev/et* node is visible: run this inside the sandbox")
        return 3
    if os.path.isdir("/run/lock") and os.listdir("/run/lock"):
        print("REFUSED: /run/lock is not empty: run this inside the sandbox")
        return 3
    with open("/proc/1/comm") as f:
        init = f.read().strip()
    if init in ("systemd", "init"):
        print("REFUSED: not in a private PID namespace (PID 1 is the host's init): run rb/selftest_wait_e190_v3.sh")
        return 3
    if os.path.exists(S) and os.listdir(S):
        print("the scratch directory is not empty")
        return 2
    os.makedirs(S, exist_ok=True)
    t = T(S)
    py = sys.version.split()[0]
    procs = len([p for p in os.listdir("/proc") if p.isdigit()])
    print(f"selftest_wait_e190_v3 {argv[1]} ({sys.executable} {py}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; /dev/et*: none; "
          f"/run/lock entries: 0; PID 1 {init!r}; processes visible: {procs}", flush=True)
    print("steps: " + "; ".join(f"{v} {os.path.relpath(p, REPO)} sha256 {sha256(p)}" for v, p in STEP.items()), flush=True)
    me = os.path.abspath(__file__)
    print(f"this test: {os.path.relpath(me, REPO)} sha256 {sha256(me)}; {os.path.relpath(os.path.join(HERE, 'selftest_wait_e190_v3.sh'), REPO)} "
          f"sha256 {sha256(os.path.join(HERE, 'selftest_wait_e190_v3.sh'))}", flush=True)
    print(f"patterns: v2 line {pattern('v2')[1]} {pattern('v2')[0]!r}; v3 line {pattern('v3')[1]} {pattern('v3')[0]!r}; "
          f"v1 line {pattern('v1')[1]} {pattern('v1')[0]!r}", flush=True)
    R = Runner(S, t)
    if argv[1] == "desk":
        desk(t, R, S)
    else:
        real(t, R, S)
    calls = open(os.path.join(S, "calls.log")).read().splitlines() if os.path.exists(os.path.join(S, "calls.log")) else []
    bad = [c for c in calls if not re.match(r"^ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry[12] (true|bash -s)$", c)]
    left = 0
    for p in os.listdir("/proc"):
        if p.isdigit():
            try:
                with open(f"/proc/{p}/cmdline", "rb") as f:
                    if b"session_e190" in f.read():
                        left += 1
            except OSError:
                pass
    t.case("Z", not bad and left == 0, f"stand-in calls {len(calls)}, every one 'ssh ... aifoundry1|2 true|bash -s' to a stand-in box "
           f"({len(bad)} other); stand-in session processes left running: {left}")
    tag = "SELFTEST-WAIT-E190-V3" if argv[1] == "desk" else "REALREAD-WAIT-E190-V3"
    print(f"{tag} {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}", flush=True)
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
