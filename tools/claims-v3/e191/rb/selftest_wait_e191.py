#!/usr/bin/env python3
"""E191's desk test of step 10's two readings (Q178, the kit, Sat 14 Nov 2026, after E189's data commit fa9098c4 and before any E191
datum): THE GATE-STOP PATTERN and THE SESSION'S NAME of rb/s20_wait_e191.sh, read out of that file's own text (never retyped), the lessons
of E183's day (its wait grepped a name its session did not have) and of E190's (its step 10 v2 read the identity gate's PASS line as a
gate stop). No box, no device. Cases (verdicts stated first):
  G1  the pattern matches NONE of the lines of a whole E191 session: a dry session of run_e191.py made here (its identity (a) and (b) pass
      lines, the box check's form is the real path's: realpath case RP1's log, read from logs/realpath-e191.txt);
  G2  the pattern matches EVERY gate-stop line the runner writes: each of the runner's gate-stop sentences, read out of run_e191.py's source
      (every self.say(...) whose words end in "no device opened", "the gate, no launch", "smoke gate failed", "would not start" or
      "stop-path test failed"), and the gate-stop lines of real-path cases RP2-RP12 in logs/realpath-e191.txt;
  G3  the pattern matches no line of E189's committed real session (2026-11-14, aifoundry3 card 0: it ran whole) nor of E190 arm B's (2026-11-13,
      aifoundry1 card 1: it ran whole, its identity lines among them);
  B1  the BOUND line the runner writes (run_e191.py's source) matches step 10's 'BOUND: ' and no gate-stop phrase;
  N1  step 10's session reading is E191's ours_live by each process's own script, called with the name step 9 launches: in a private PID
      namespace a stand-in `bash .../tools/claims-v3/e191/session_e191.sh` is counted (1); a `bash -c` string naming it, a `grep` naming it
      as its first argument (E190's ours_live counted it: E191's requires an interpreter's script), the desk's own step script
      `bash .../s11_a1_session_e191.sh`, and a dry run (`... session_e191.sh --dry`) are not (0, each);
  N2  step 9's launch line names exactly that script (bash tools/claims-v3/e191/session_e191.sh), and session_e191.sh runs the runner as
      its child (no exec), so the script's command line stays to the end.
    /usr/bin/python3 -B tools/claims-v3/e191/rb/selftest_wait_e191.py <scratch dir>     (inside W/nodev.sh; prints SELFTEST-WAIT-E191 <n> of <m>)
A desk check of code: nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
S20 = os.path.join(HERE, "s20_wait_e191.sh")
S11 = os.path.join(HERE, "s11_a1_session_e191.sh")
RUN = os.path.join(E, "run_e191.py")
E189_LOG = os.path.join(REPO, "docs/reports/data/2026-11-14-e189-blind-day-aifoundry3/session/session.log")
E190B_LOG = os.path.join(REPO, "docs/reports/data/2026-11-13-e190-large-gemm/aifoundry1-c1/session.log")
RP_LOG = os.path.join(E, "logs", "realpath-e191.txt")
res = []


def ok(cond, name, what):
    res.append(bool(cond))
    print(f"-> {'PASS' if cond else 'FAIL'} ({name} {what})", flush=True)


def main(S):
    s20 = open(S20).read()
    m = re.search(r"if grep -qE '([^']+)' \"\$L\" 2>/dev/null; then echo \"GATE-STOPPED", s20)
    pat = re.compile(m.group(1)) if m else None
    print(f"step 10's GATE-STOPPED pattern, read from rb/s20_wait_e191.sh: {m.group(1) if m else 'NOT FOUND'}")
    # G1: a whole dry session, and the real path's RP1
    out = os.path.join(S, "g1")
    r = subprocess.run([sys.executable, "-B", RUN, "session", "--dry", "--double", "inject", "--t0", str(int(time.time())), "--out", out,
                        "--sequence", "short", "--idle-before", "0.3", "--idle-after", "0.3", "--anchor-s", "0.3", "--die-wait-s", "2"],
                       cwd=REPO, env=dict(os.environ, E191_FAKE_SCALE="0.05"), capture_output=True, text=True, timeout=600)
    log = open(os.path.join(out, "session.log")).read().splitlines() if os.path.exists(os.path.join(out, "session.log")) else []
    rp = open(RP_LOG).read() if os.path.exists(RP_LOG) else ""
    rp1 = [ln for ln in rp.split("RP1:")[0].splitlines() if re.match(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d [A-Z]+ ", ln)]
    hits = [ln for ln in log + rp1 if pat and pat.search(ln)]
    idl = [ln for ln in log + rp1 if "identity (a)" in ln or "identity (b)" in ln or "the box check: aifoundry1" in ln]
    print(f"   G1: the dry session rc {r.returncode}, {len(log)} lines; RP1's real-path log {len(rp1)} lines; identity and box-check pass lines "
          f"{len(idl)}; pattern hits {hits[:2]}")
    ok(pat and r.returncode == 0 and len(log) > 20 and len(rp1) > 20 and len(idl) >= 5 and not hits, "G1",
       "no line of a whole E191 session (dry, and the real path's RP1, identity pass lines among them) reads as a gate stop")
    # G2: every gate-stop sentence in the runner's source, and the real path's gate-stop lines
    src = open(RUN).read()
    says = re.findall(r'self\.say\(f?"([^"]*(?:no device opened|the gate, no launch|smoke gate failed|would not start|stop-path test failed)[^"]*)"', src)
    says += [s for s in re.findall(r'self\.say\(f?"([^"]*)"', src) if "stop-path test" in s and "failed" in s]
    rpg = [ln for ln in rp.splitlines() if re.match(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d [A-Z]+ ", ln) and
           any(w in ln for w in ("no device opened", "IDENTITY GATE FAILED", "smoke gate failed"))]
    says = [s.replace("{'passed' if ok else 'failed'}", "failed") for s in says]       # the f-string as the gate stop renders it
    miss = [s for s in says if not (pat and pat.search(s))] + [ln for ln in rpg if not (pat and pat.search(ln))]
    sp = "stop-path test {'passed' if ok else 'failed'}"
    print(f"   G2: {len(says)} gate-stop sentences in run_e191.py, {len(rpg)} gate-stop lines in the real-path log; not matched: {miss[:3]}")
    ok(pat and len(says) >= 9 and len(rpg) >= 8 and not miss and pat.search(sp.replace("{'passed' if ok else 'failed'}", "failed")),
       "G2", "every gate-stop sentence of the runner and every real-path gate-stop line reads as a gate stop")
    # G3: the committed real sessions that ran whole
    e189 = open(E189_LOG).read().splitlines() if os.path.exists(E189_LOG) else []
    e190 = open(E190B_LOG).read().splitlines() if os.path.exists(E190B_LOG) else []
    h3 = [ln for ln in e189 + e190 if pat and pat.search(ln)]
    print(f"   G3: E189's real session {len(e189)} lines, E190 arm B's {len(e190)} lines ({sum('identity' in x for x in e190)} identity lines); hits {h3[:2]}")
    ok(pat and len(e189) > 50 and len(e190) > 20 and not h3, "G3", "no line of E189's or E190 arm B's committed real session reads as a gate stop")
    # B1
    bl = re.findall(r'why = \(f"(BOUND: [^"]*)"', src)
    ok(bl and "'BOUND: '" in s20 and not pat.search(bl[0]), "B1", "the runner's BOUND line is BOUND-SEEN's and no gate stop's")
    # N1: E191's ours_live by each process's own script, in a private PID namespace
    tree = os.path.join(S, "n1", "tools", "claims-v3", "e191")
    os.makedirs(os.path.join(tree, "rb"), exist_ok=True)
    for n in ("session_e191.sh", "rb/s11_a1_session_e191.sh"):
        with open(os.path.join(tree, n), "w") as f:
            f.write("#!/bin/bash\nsleep 8\n")
    drv = os.path.join(S, "n1", "drive.sh")
    with open(drv, "w") as f:
        f.write(f'''#!/bin/bash
. "{os.path.join(HERE, 'rb_e191.sh')}" >/dev/null 2>&1
eval "$(e191_live_text)"
T={tree}
bash "$T/session_e191.sh" & a=$!
sleep 0.5; echo "counted-real $(ours_live 'session_e191.sh')"; kill $a; wait $a 2>/dev/null
bash -c "sleep 8; echo $T/session_e191.sh" & a=$!
sleep 0.5; echo "counted-dashc $(ours_live 'session_e191.sh')"; kill $a; wait $a 2>/dev/null
grep -q session_e191.sh /dev/zero & a=$!
sleep 0.5; echo "counted-grep $(ours_live 'session_e191.sh')"; kill $a; wait $a 2>/dev/null
bash "$T/rb/s11_a1_session_e191.sh" & a=$!
sleep 0.5; echo "counted-step9 $(ours_live 'session_e191.sh') $(ours_live)"; kill $a; wait $a 2>/dev/null
bash "$T/session_e191.sh" --dry & a=$!
sleep 0.5; echo "counted-dry $(ours_live 'session_e191.sh')"; kill $a; wait $a 2>/dev/null
''')
    r = subprocess.run(["/usr/bin/bwrap", "--dev-bind", "/", "/", "--unshare-pid", "--proc", "/proc", "--die-with-parent", "--", "bash", drv],
                       capture_output=True, text=True, timeout=120)
    got = dict(ln.split(" ", 1) for ln in r.stdout.splitlines() if ln.startswith("counted-"))
    print(f"   N1: {got} (stderr {r.stderr.strip()[:120]!r})")
    ok(got.get("counted-real") == "1" and got.get("counted-dashc") == "0" and got.get("counted-grep") == "0"
       and got.get("counted-step9") == "0 0" and got.get("counted-dry") == "0", "N1",
       "the session counted by its own script; a -c string, a grep, the desk's step 9 script and a dry run not counted")
    s11 = open(S11).read()
    sess = open(os.path.join(E, "session_e191.sh")).read()
    ok("setsid nohup bash tools/claims-v3/e191/session_e191.sh" in s11 and "ours_live \"session_$RUN.sh\"" in s20 and "run=e191" in s20
       and re.search(r"^python3 -B tools/claims-v3/e191/run_e191.py session", sess, re.M) and "exec python3" not in sess, "N2",
       "step 9 launches session_e191.sh by that name, step 10 looks for that name, and the runner is its child (no exec)")
    n = sum(res)
    print(f"SELFTEST-WAIT-E191 {n} of {len(res)} {'PASS' if n == len(res) else 'FAIL'}")
    return 0 if n == len(res) else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    S = os.path.abspath(sys.argv[1])
    if S.startswith(REPO + os.sep):
        sys.exit("the scratch directory must be outside the repository")
    if [x for x in os.listdir("/dev") if x.startswith("et")]:
        sys.exit("REFUSED: a /dev/et* node is visible: run this inside the sandbox")
    os.makedirs(S, exist_ok=True)
    print(f"selftest_wait_e191 ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    sys.exit(main(S))
