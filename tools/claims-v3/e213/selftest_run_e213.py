#!/usr/bin/env python3
"""E213's runner desk test (Q216, lane kit-e213, Tue 17 Nov 2026, before any E213 datum): run_e213.py on fake_card_e213.py's doubles, each case its
own --dry session (a subprocess) in a scratch directory, E211's selftest_run_e211.py form (landed in 2b7f261f) with E206's arm B cases, for E213's
two arms and four families, end to end through the reducer and the FROZEN scorer. No device, no box. Run it ONLY inside a sandbox with no /dev/et*
and an empty /run/lock (W/nodev.sh on aifoundry2): case RF runs the real runner, which must stop at its box check. In --dry the identity gate reads
each process's ELF path (the family's kernel folder); the real gate on real ELFs is the real-path test's (desk/realpath_e213.py).

    /usr/bin/python3 -B tools/claims-v3/e213/selftest_run_e213.py <scratch dir> [--only CASE ...] > logs/selftest-run-e213.txt

Cases (arm A unless named B; the doubles' latch reads 87 C on arm A, 66 C on arm B, as the cards' committed telemetry does):
  G1 / G1B the short sequence (arm A t01, a039, a005; arm B t02, k03, k18): rc 0; the card's identity gate (A /dev/et0_mgmt, ID 0; B /dev/et1_mgmt,
     ID 1, 499 mV); the identity read; the smoke (A s01 'rgm136 gemmL', s02 'rgm211 gemmLn', s03 'rgm136 gemmLnc', s04 'rgm211 gemmL' (Amendment
     A1); B s11-s13 'rgm136 gemmL', s14
     'rgm136 gemmLnc' on rgm211's host), each gated by its family, its counter's mean in R0's 200-4,000, the walk on rgm211's host, THEN the
     stop-path test; three runs, each gated; the closing config; the manifest; the latch tripped nothing
  K4 / K4B THE FOUR FAMILIES: every run of rgm211's host in pass 1 (A 13: rgm211 gemmLn, rgm211 gemmL, rgm136 gemmLnc; B 4: gemmLnc), each on its
     loop's host with its loop's ELF, gated, the walk nm for gemmLn and mn for the others; on arm A the family smoke s04 good before them
  C1 the start config not as found (TDP 65 W on arm A; C1B TDP 0 W on arm B): 16, the gate, no sampler, no host     C2 the config names the
  other card: 16    C2B arm B's config at 519 mV: 16    C4 no identity block: 16    C5 the config read fails: 16    C6 the config read hangs past
  its TERM: HUNG (rc 8), nothing killed: the hung double ends by itself    C7 the arm's own runtime line on the config read: dropped, rc 0
  H1 another login on the arm's card: 16    H3 another login's line on card 1 (arm A: any other login): 16    H3B another login on card 0 at
  arm B's start (the kit's start rule): 16    H3C a line of ours on card 0 (arm B): 16    H4 et-who unreadable: 16    H5 a device process of
  ours: 16    H6 a CI job: 16    L1 the card's lock held: 16, no config read
  S1 the sampler would not start: 16    S2 the sampler holds the other card's node: 16    S3 the sampler goes silent in the runs: restarted, rc 0
  S4 the sampler dies in the runs: restarted, rc 0    P1 the stop-path test on a session with no live samples: it fails
  R1 a smoke check of C wrong: 16    R2 a smoke host crashes: 16    R3 a smoke host names and holds the other card: the watch trips, "stopping:",
  16    R4 the board does not rise in the smoke: 16    R5 the arm's own runtime line INSIDE a smoke record: dropped, rc 0    R6 a smoke host's
  records name another shire mask: 16    R7 a smoke host's counter mean at 3 x (2,400 cycles an op: inside R0's band, rc 0) and R7X at 6 x (4,800:
  outside R0's 200-4,000, the smoke gate fails, 16)
  K0 a smoke host says "kernel did not finish": K1, 16    K1 the first run's host says it: the session stops, rc 0
  HG the first point's host IGNORES its timeout's TERM: HUNG (rc 8), nothing further, no closing config read, NOTHING KILLED
  TO an 'rgm136 gemmL' run's host ends on TERM (rc 124): flagged, the session goes on (E206's rule), rc 0
  SA an 'rgm136 gemmL' run's records name another shire mask: never read as data; the reducer passes the host's record on and the FROZEN scorer
     sets the run aside
  F2 two failed 'rgm136 gemmL' processes in a row (a005 and a032, runs 003 and 004): the session stops, rc 0
  B1 the board above 70 W on 3 samples in a run (arm A): the stop    B1B arm B: 71 W on every sample does not stop, 73 W on 3 does (72 W line)
  D1 the die at 70 C (arm A): the stop    D1B arm B: 80 C the stop    D2 the latch rises past its session value: the stop
  D3 / D3B the board at the arm's line (70.0 W, 72.0 W; not above) on every later sample: no stop    DG the die held above the gate: the later runs
     wait and are NO DATA    D3C arm B's die at 79 C (below its 80 C stop, above its gate min(63, rest + 3)): no stop; the next starts NO DATA by the gate
  CT the card-time rule (--rule-s 6.5): no run starts after it    OP an operator's SIGTERM to the runner mid-run: the stop file, rc 0
  CR the runner crashes mid-run (a copied tree whose order names a run the copied points file lacks: E211's crash, its smoke gate reading a
     forecast that was not copied, cannot happen in E213, whose smoke band is absolute): "CRASH: KeyError", the closing still runs, rc 1
  SF THE OPERATOR'S STOP FILE touched during run 002: run 003 never starts    SS THE OPERATOR'S STOP FILE during the smoke's s02: the smoke gate
  fails naming the stop file    S0 a STOP file there when the runner starts: refused before any device
  DF a sampler that goes silent and IGNORES SIGTERM: the session stops, NEVER two processes on the stand-in management node at once, no closing
     config read while it lives, nothing killed
  RT the other card's runtime line on a smoke host: the smoke gate fails; the arm's own passes    RT2 on the first run's host: STOP (identity)
  RTB arm B: card 0's runtime line on the tie's host: STOP (identity); card 1's own lines dropped    RTC the other card's line on the config read: 16
  BN the board line in process: 95 W on every other sample with no reading between trips at the third reading
  GS THE IDENTITY GATE refuses the smoke's s02: the smoke gate fails, s02's process never starts
  GR THE IDENTITY GATE refuses run 003's process (a005): STOP before it, rc 0; the refused run through the reducer and the FROZEN scorer: R0 FAIL
  G211 THE IDENTITY GATE refuses THE NEW FAMILY's first scored run ('rgm211 gemmL', a085, in the kernels sequence; its smoke s04 passed): STOP
     before its process, nothing further (a run's gate stays session-wide); through the reducer and the frozen scorer: its gate words carried, R0 FAIL
  WS THE WALK CHECK fails in the smoke's s02: the kernel stops, the smoke gate fails, 16    WR THE WALK CHECK fails on a085 ('rgm211 gemmL', its
  first scored run; s04 passed): THE KERNEL STOPS, rc 0; the reducer and the frozen scorer: R0 FAIL
  AMENDMENT A1, THE FAMILY SMOKE'S OWN STOP PATH (arm A's s04, 'rgm211 gemmL'): GF4 THE IDENTITY GATE refuses s04: no process, the family DROPPED,
  the stop-path test and the session go on; in the kernels sequence the nine other runs of rgm211's host run and a085 a081 a078 a074 never start
  (no run folder, "Amendment A1" in queue.json, families_dropped); through the reducer and the frozen scorer: R0 PASS, the drop flagged, the four
  NO DATA    WF4 THE WALK CHECK fails at s04: the same (its process ran, no kernel stop raised)    CF4 a check of C wrong at s04: the family
  dropped, the short sequence's three runs run, rc 0    KF4 K1 at s04: the session stops (the smoke gate fails, 16), nothing dropped, no run
  TF4 s04 ends on its timeout's TERM (rc 124, a launch timeout): the session stops (16), no run    SF4 the sampler dies inside s04 (the sampler
  is the session's): the session stops at the smoke (16), nothing dropped, no run
  CW a check of C wrong in an 'rgm211 gemmLn' run (a084): THE KERNEL STOPS    TL an 'rgm211 gemmL' run (a085) ends on TERM (rc 124): THE KERNEL
  STOPS    TE a tensor error in an 'rgm136 gemmLnc' run (a086): THE KERNEL STOPS    TEB the same on arm B's k40: THE KERNEL STOPS
  WG an 'rgm136 gemmL' run's host crashes: flagged, the session goes on, rc 0
  OR / ORB THE ORDER: each arm's whole registered order (A 105 runs, B 85) at a tiny scale: every run's key and argv the registered ones (the
     point's host and ELF by its loop, its host_args, --seconds 6 --budget 7.5, --kernel, --stop-file, under `timeout 10`, never -k), in order,
     every process gated (its words recorded), every host record read as its command's, every rgm211-host walk ok
  E2 END TO END, both arms at once (the whole order each; a 6 s rest read, the reducer's rest window being the registered 5 s; leakage off), through
     the reducer (both arms in one data file) and the FROZEN scorer: E2-A with the doubles' watts and seconds at MM1-v3's frozen forecasts: every
     run's t_gemm the forecast's seconds, its J over idle the injected watts x seconds; per arm R0, S6, T1-T3, E1-E4 PASS and H1-H5 MM1-v3 BETTER,
     pooled HP1-HP5 MM1-v3 BETTER; E2-W with the watts 25% over: T1-T3 PASS, E1 and E2 FAIL on both arms
  RF the refusals: the --dry options without --dry, V3_DRY without --dry, an unknown arm (argparse), and the REAL runner on this desk stopping at
     its box check (both arms)
Every number here comes from the doubles (MM1-v3's frozen forecasts driven through a toy card): a desk check of code, not a measurement and not a
reading of E213. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
RUNNER = os.path.join(HERE, "run_e213.py")
sys.path.insert(0, HERE)
import e213_common as C  # noqa: E402

FAST = ["--rest-s", "0.3", "--smoke-rest-s", "1.5", "--tail-s", "0.2", "--gate-wait-s", "3"]
SHORT = {"A": ["001-tie-t01", "002-pass1-a039", "003-pass1-a005"], "B": ["001-tie-t02", "002-pass1-k03", "003-pass1-k18"]}


class T:
    def __init__(self, scratch, only):
        self.S, self.only = scratch, set(only or [])
        self.n = self.ok = 0
        self.n_smoke = {"A": 28, "B": 28}           # 7 launches a smoke process: arm A's four (s04 by Amendment A1), arm B's four

    def want(self, name):
        return not self.only or name in self.only

    def case(self, name, good, detail):
        self.n += 1
        self.ok += 1 if good else 0
        print(f"{name}: {'PASS' if good else 'FAIL'} - {detail}", flush=True)

    def session(self, name, arm, env=None, seq="short", extra=None, scale="0.05", runner=None, signal_after=None, inject=None,
                touch_after=None, pre_stop=False, watch_mgmt=False):
        d = os.path.join(self.S, name)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
        e = {k: v for k, v in os.environ.items() if not k.startswith("E213_FAKE_")}
        e.update({"E213_FAKE_SCALE": scale, "E213_FAKE_TAU_S": "1"})
        if inject is not None:
            ip = os.path.join(d, "inject.json")
            json.dump(inject, open(ip, "w"))
            e["E213_FAKE_INJECT"] = ip
        e.update(env or {})
        out = os.path.join(d, "T")
        if pre_stop:
            os.makedirs(out)
            open(os.path.join(out, "STOP"), "a").close()
        cmd = [sys.executable, "-B", runner or RUNNER, "session", "--dry", "--arm", arm, "--t0", str(int(time.time())), "--out", out,
               "--sequence", seq] + FAST + (extra or [])
        t0 = time.time()
        self.max_mgmt = 0
        with open(os.path.join(d, "runner.out"), "w") as fo:
            p = subprocess.Popen(cmd, cwd=REPO, stdout=fo, stderr=subprocess.STDOUT, env=e)
            if signal_after or touch_after:
                want_text, secs = signal_after or touch_after
                tq = time.time()
                while time.time() - tq < 120 and p.poll() is None:
                    if os.path.exists(os.path.join(out, "session.log")) and want_text in open(os.path.join(out, "session.log")).read():
                        time.sleep(secs)
                        if signal_after:
                            p.send_signal(signal.SIGTERM)
                        else:
                            open(os.path.join(out, "STOP"), "a").close()
                        break
                    time.sleep(0.1)
            if watch_mgmt:
                fake = os.path.realpath(os.path.join(out, "fakedev"))
                while p.poll() is None and time.time() - t0 < 1800:
                    self.max_mgmt = max(self.max_mgmt, mgmt_holders(fake))
                    time.sleep(0.2)
            rc = p.wait(timeout=3600)
        log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
        return rc, log, out, time.time() - t0


def mgmt_holders(fake):
    n, me = 0, os.getuid()
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            if os.stat(f"/proc/{pid}").st_uid != me:
                continue
            for fd in os.listdir(f"/proc/{pid}/fd"):
                t = os.readlink(f"/proc/{pid}/fd/{fd}")
                if t.startswith(fake + "/") and t.endswith("_mgmt"):
                    n += 1
                    break
        except OSError:
            continue
    return n


def has_proc(d):
    for dp, dn, fn in os.walk(d):
        if any(n.startswith("proc") and n.endswith(".out") for n in fn):
            return True
    return False


def q_of(d):
    p = os.path.join(d, "queue.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def runs_ran(d):
    return sum(1 for x in q_of(d).get("queue", []) if x.get("ran"))


def wait_marker(path, secs=30):
    t = time.time()
    while time.time() - t < secs:
        if os.path.exists(path):
            return open(path).read().strip()
        time.sleep(0.5)
    return ""


def run_json(d, key):
    p = os.path.join(d, "runs", key, "run.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def line_of(log, word):
    return [x[24:230] for x in log.splitlines() if word in x][:1]


def reduce_and_score(S, tag, arms):
    """The session(s) through the reducer (all given arms in one data file) and the FROZEN scorer: (reduce rc, score rc, data, scored)."""
    dj, sj = os.path.join(S, f"{tag}-data.json"), os.path.join(S, f"{tag}-scored.json")
    cmd = [sys.executable, "-I", "-B", os.path.join(HERE, "reduce_e213.py")]
    for arm, d in arms.items():
        cmd += ["--arm", f"{arm}={d}"]
    r1 = subprocess.run(cmd + ["--out", dj], capture_output=True, text=True)
    r2 = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "score_e213.py"), dj, "--out", sj], capture_output=True, text=True)
    data = json.load(open(dj)) if os.path.exists(dj) else {}
    sc = json.load(open(sj)) if os.path.exists(sj) else {}
    return r1.returncode, r2.returncode, data, sc


def verdicts(sc, arm):
    return (sc.get("arms", {}).get(arm) or {}).get("verdicts", {})


def kseq(arm):
    return [C.run_key(r) for r in C.sequence(arm) if r["block"] == "pass1" and C.rgm211_host(r["id"])]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    S = os.path.abspath(a.scratch)
    if S == REPO or S.startswith(REPO + os.sep):
        print("the scratch directory must be outside the repository")
        return 2
    if [x for x in os.listdir("/dev") if x.startswith("et")]:
        print("REFUSED: a /dev/et* node is visible: run this inside the sandbox (no /dev/et*, an empty /run/lock)")
        return 3
    os.makedirs(S, exist_ok=True)
    t = T(S, a.only)
    print(f"selftest_run_e213 ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; /dev/et*: none; "
          f"/run/lock entries: {len(os.listdir('/run/lock')) if os.path.isdir('/run/lock') else 'none'}", flush=True)

    for arm, name in (("A", "G1"), ("B", "G1B")):
        if t.want(name):
            rc, log, d, dt = t.session(name, arm)
            ls = log.splitlines()
            last_sm = C.ARMS[arm]["smoke"][-1]
            i_sm = max([i for i, x in enumerate(ls) if f"smoke {last_sm}: the identity gate GATE OK; rc" in x] or [-1])
            i_sp = min([i for i, x in enumerate(ls) if "stop-path test passed" in x] or [10 ** 6])
            sm = [json.load(open(os.path.join(d, "smoke", p, "smoke.json"))) for p in C.ARMS[arm]["smoke"] if os.path.exists(os.path.join(d, "smoke", p, "smoke.json"))]
            t.n_smoke[arm] = sum(x.get("n_launch", 0) for x in sm) or t.n_smoke[arm]
            idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
            procs = [run_json(d, k).get("procs", [{}])[0] for k in SHORT[arm]]
            gates = [str(x.get("gate", ""))[:7] for x in sm] + [str(p.get("gate", ""))[:7] for p in procs]
            card = C.ARMS[arm]["card_index"]
            want_fam = ["rgm136 gemmL", "rgm211 gemmLn", "rgm136 gemmLnc", "rgm211 gemmL"] if arm == "A" else ["rgm136 gemmL"] * 3 + ["rgm136 gemmLnc"]
            want_walk = [None, "nm", "mn", "mn"] if arm == "A" else [None, None, None, "mn"]
            t.case(name, rc == 0 and f"the card's identity: PCIe target /dev/et{card}_mgmt, physical device ID {card}" in log and "the identity read: " in log
                   and len(sm) == len(want_fam) and all(x["good"] for x in sm) and all(x.get("cycles_in_band") for x in sm)
                   and [x.get("family") for x in sm] == want_fam and [x.get("walk", {}).get("want") for x in sm] == want_walk
                   and all(x.get("walk_ok") for x in sm) and gates == ["GATE OK"] * (len(sm) + 3)
                   and 0 <= i_sm < i_sp < 10 ** 6 and runs_ran(d) == 3 and "config end: {" in log
                   and os.path.exists(os.path.join(d, "MANIFEST.sha256")) and "STOP" not in log
                   and idn.get("config_start", {}).get("minion_mv") == (523 if arm == "A" else 499)
                   and [x["run"] for x in q_of(d).get("queue", [])] == SHORT[arm],
                   f"rc {rc}; the smoke {[x['identity_ok'] and x['good'] for x in sm]} (families {[x.get('family') for x in sm]}, counter means "
                   f"{[x.get('counted_cycles_per_op') for x in sm]} in R0's band) then the stop-path test (lines {i_sm} < {i_sp}); {runs_ran(d)} runs; "
                   f"gates {gates}; {t.n_smoke[arm]} smoke launches; the latch tripped nothing ({'STOP' not in log}); {dt:.0f} s")
    for arm, name in (("A", "K4"), ("B", "K4B")):
        if t.want(name):
            rc, log, d, dt = t.session(name, arm, seq="kernels")
            keys = kseq(arm)
            pr = [(run_json(d, k).get("procs") or [{}])[0] for k in keys]
            fams = [C.family(run_json(d, k).get("id", "")) if run_json(d, k) else None for k in keys]
            hk = [os.path.basename(os.path.dirname(os.path.dirname(p.get("argv", ["/x/y/z"])[0]))) for p in pr]
            kk = [os.path.basename(os.path.dirname(os.path.dirname(C.arg_of(p.get("argv"), "--kernel") or "/x/y/z"))) for p in pr]
            good = all(h == C.LOOPS[f]["host"] and k == C.LOOPS[f]["elf"] and p.get("walk", {}).get("want") == C.LOOPS[f]["walk"] and p.get("walk_ok")
                       and str(p.get("gate", "")).startswith("GATE OK") for h, k, f, p in zip(hk, kk, fams, pr) if f)
            s4 = json.load(open(os.path.join(d, "smoke", "s04", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "s04", "smoke.json")) else {}
            s4ok = arm == "B" or (s4.get("good") is True and s4.get("family") == "rgm211 gemmL" and s4.get("walk", {}).get("want") == "mn"
                                  and str(s4.get("gate", "")).startswith("GATE OK") and "/rgm211/" in str(C.arg_of(s4.get("argv"), "--kernel"))
                                  and not q_of(d).get("families_dropped"))
            t.case(name, rc == 0 and [x["run"] for x in q_of(d).get("queue", [])] == keys and runs_ran(d) == len(keys) == (13 if arm == "A" else 4)
                   and good and s4ok and (arm == "B" or fams.count("rgm211 gemmL") == 4),
                   f"rc {rc}; {len(keys)} runs of rgm211's host: (family, host, ELF, walk) {[(f.split()[1] + '@' + f.split()[0][3:], h[3:], k[3:], p.get('walk', {}).get('want')) for f, h, k, p in zip(fams, hk, kk, pr) if f]}")
    for name, arm, mode, want in (("C1", "A", "tdp65", "the gate, no launch"), ("C1B", "B", "tdp0", "the gate, no launch"),
                                  ("C2", "A", "card1", "/dev/et1_mgmt, not /dev/et0_mgmt"), ("C2B", "B", "mv519", "minion_mv 519, not below 510"),
                                  ("C4", "A", "noident", "no 'PCIe target' line"), ("C5", "A", "fail", "config read rc 1")):
        if t.want(name):
            rc, log, d, dt = t.session(name, arm, {"E213_FAKE_CONFIG": mode})
            t.case(name, rc == 16 and want in log and "the gate, no launch" in log and "sampler started" not in log and not has_proc(d),
                   f"rc {rc}; '{line_of(log, 'config start')}'")
    if t.want("C6"):
        rc, log, d, dt = t.session("C6", "A", {"E213_FAKE_CONFIG": "hang", "E213_FAKE_HANG_S": "16"})
        mk = wait_marker(os.path.join(d, "fake_sched.jsonl.config-hang-ended"), 30)
        t.case("C6", rc == 8 and " HUNG: " in log and "sampler started" not in log and "config end: not read" in log and "ended by itself" in mk
               and q_of(d).get("hung"), f"rc {rc}; the HUNG line {' HUNG: ' in log}; the hung double: '{mk[:90]}'")
    for name, arm in (("C7", "A"), ("C7B", "B")):
        if t.want(name):
            rc, log, d, dt = t.session(name, arm, {"E213_FAKE_CONFIG": "runtime"})
            idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
            t.case(name, rc == 0 and runs_ran(d) == 3 and idn.get("config_start", {}).get("runtime_cards") == [C.ARMS[arm]["card_index"]],
                   f"rc {rc}; the config read whole past the arm's own runtime line ({idn.get('config_start', {}).get('runtime_cards')})")
    for name, arm, env, want in (("H1", "A", {"E213_FAKE_ETWHO": "other"}, "holder line(s) of another login"),
                                 ("H3", "A", {"E213_FAKE_ETWHO": "other1"}, "holder line(s) of another login"),
                                 ("H3B", "B", {"E213_FAKE_ETWHO": "other1"}, "another login on card 0 (the kit's start rule for arm B)"),
                                 ("H3C", "B", {"E213_FAKE_ETWHO": "ours1"}, "holder line(s) of ours on card 0"),
                                 ("H1B", "B", {"E213_FAKE_ETWHO": "other"}, "holder line(s) of another login on card 1"),
                                 ("H4", "A", {"E213_FAKE_ETWHO": "fail"}, "et-who unreadable (rc 1)"),
                                 ("H5", "A", {"E213_FAKE_PS": "ours"}, "other device process(es) of ours"),
                                 ("H6", "B", {"E213_FAKE_PS": "ci"}, "CI job")):
        if t.want(name):
            rc, log, d, dt = t.session(name, arm, env)
            t.case(name, rc == 16 and "refused, no device opened: a holder or a device process" in log and want in log
                   and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}; '{line_of(log, 'refused')}'")
    if t.want("L1"):
        d0 = os.path.join(S, "L1", "T")
        os.makedirs(d0, exist_ok=True)
        lk = os.path.join(d0, "dry.lock")
        open(lk, "a").close()
        holder = subprocess.Popen(["flock", "-o", lk, "sleep", "20"], stdin=subprocess.DEVNULL)
        time.sleep(0.5)
        e = {k: v for k, v in os.environ.items() if not k.startswith("E213_FAKE_")}
        r = subprocess.run([sys.executable, "-B", RUNNER, "session", "--dry", "--arm", "A", "--t0", str(int(time.time())), "--out", d0] + FAST,
                           cwd=REPO, capture_output=True, text=True, env=e)
        holder.terminate()          # the stand-in holder (a sleep under flock, no device), by SIGTERM
        holder.wait()
        log = open(os.path.join(d0, "session.log")).read()
        t.case("L1", r.returncode == 16 and "refused, no device opened: the card's lock is held" in log and not os.path.exists(os.path.join(d0, "config-start.json")),
               f"rc {r.returncode}")
    if t.want("S1"):
        rc, log, d, dt = t.session("S1", "A", {"E213_FAKE_SAMPLER": "dead"})
        t.case("S1", rc == 16 and "the sampler would not start" in log and not has_proc(d), f"rc {rc}")
    for name, arm in (("S2", "A"), ("S2B", "B")):
        if t.want(name):
            rc, log, d, dt = t.session(name, arm, {"E213_FAKE_SAMPLER": "card1"})
            t.case(name, rc == 16 and "the identity read (the sampler running, before the smoke)" in log and "the gate, no launch" in log and not has_proc(d),
                   f"rc {rc}; '{line_of(log, 'identity read')}'")
    if t.want("S3"):
        rc, log, d, dt = t.session("S3", "A", {"E213_FAKE_SAMPLER": f"hangs:{t.n_smoke['A'] + 3}"})
        t.case("S3", rc == 0 and "the sampler is not live" in log and log.count("sampler started") >= 2 and runs_ran(d) >= 2,
               f"rc {rc}; sampler starts {log.count('sampler started')}; runs {runs_ran(d)}")
    if t.want("S4"):
        rc, log, d, dt = t.session("S4", "B", {"E213_FAKE_SAMPLER": f"dies:{t.n_smoke['B'] + 3}"})
        t.case("S4", rc == 0 and log.count("sampler started") >= 2 and runs_ran(d) >= 2, f"rc {rc}; sampler starts {log.count('sampler started')}; runs {runs_ran(d)}")
    if t.want("P1"):
        import run_e213 as R
        d = os.path.join(S, "P1")
        os.makedirs(d, exist_ok=True)
        ns = argparse.Namespace(what="session", arm="A", t0=int(time.time()), out=os.path.join(d, "T"), deadline_epoch=0, dry=True,
                                sequence="short", rest_s=0.3, smoke_rest_s=1.5, tail_s=0.2, gate_wait_s=3, rule_s=C.ARMS["A"]["rule_s"], cap_s=C.ARMS["A"]["cap_s"])
        s = R.Session(ns)
        s.t_first = time.time()
        ok, res = s.stop_path_test()
        t.case("P1", not ok and not res["board"]["tripped"] and not res["die"]["tripped"], f"ok {ok}; {json.dumps({k: v['tripped'] for k, v in res.items()})}")
    for name, arm, env, want in (("R1", "A", {"E213_FAKE_HOST": "wrong"}, "check wrong"), ("R2", "B", {"E213_FAKE_HOST": "crash"}, "rc 134"),
                                 ("R4", "A", {"E213_FAKE_HOST": "norise"}, "the board's rise"), ("R6", "A", {"E213_FAKE_HOST": "mismatch"}, "the counter's mean None")):
        if t.want(name):
            rc, log, d, dt = t.session(name, arm, env)
            s0, s1 = C.ARMS[arm]["smoke"][0], C.ARMS[arm]["smoke"][1]
            t.case(name, rc == 16 and "smoke gate failed" in log and runs_ran(d) == 0 and want in log
                   and not os.path.isdir(os.path.join(d, "smoke", s1)), f"rc {rc}; '{line_of(log, 'smoke gate failed')}'")
    if t.want("R7"):
        rc, log, d, dt = t.session("R7", "A", {"E213_FAKE_HOST": "cyc3x"})
        t.case("R7", rc == 0 and "smoke gate passed" in log and "(R0's band 200-4000: in;" in log,
               f"the counter's mean at 3 x the toy 800 (2,400 cycles an op, inside R0's 200-4,000): rc {rc}, '{line_of(log, 'smoke s01: the identity gate GATE OK')}'")
    if t.want("R7X"):
        rc, log, d, dt = t.session("R7X", "A", {"E213_FAKE_HOST": "cyc6x"})
        t.case("R7X", rc == 16 and "smoke gate failed" in log and "OUT" in log and runs_ran(d) == 0,
               f"the counter's mean at 6 x the toy (4,800, outside R0's 200-4,000): rc {rc}; '{line_of(log, 'smoke gate failed')}'")
    for name, arm in (("R3", "A"), ("R3B", "B")):
        if t.want(name):
            rc, log, d, dt = t.session(name, arm, {"E213_FAKE_HOST": "card1"})
            s0 = C.ARMS[arm]["smoke"][0]
            err = open(os.path.join(d, "smoke", s0, "proc.err")).read() if os.path.exists(os.path.join(d, "smoke", s0, "proc.err")) else ""
            t.case(name, rc == 16 and os.path.exists(os.path.join(d, "STOP")) and "stopping:" in err and "smoke gate failed" in log
                   and not os.path.isdir(os.path.join(d, "smoke", C.ARMS[arm]["smoke"][1])), f"rc {rc}; the host stopped by the file {'stopping:' in err}")
    if t.want("R5"):
        rc, log, d, dt = t.session("R5", "A", {"E213_FAKE_HOST": "runtime"})
        sm = json.load(open(os.path.join(d, "smoke", "s01", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "s01", "smoke.json")) else {}
        sm2 = json.load(open(os.path.join(d, "smoke", "s02", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "s02", "smoke.json")) else {}
        t.case("R5", rc == 0 and sm.get("records", {}).get("runtime_lines") == 2 and sm.get("records", {}).get("unparsed") == 0
               and sm2.get("records", {}).get("runtime_lines") == 2 and sm2.get("walk_ok") is True and "smoke gate passed" in log,
               f"rc {rc}; s01's records {sm.get('records')}; s02's (rgm211's form, its walk read) {sm2.get('records')}, walk ok {sm2.get('walk_ok')}")
    if t.want("K0"):
        rc, log, d, dt = t.session("K0", "A", {"E213_FAKE_HOST": "k1"})
        t.case("K0", rc == 16 and "K1: a launch of the smoke's s01 did not finish" in log and "smoke gate failed" in log and runs_ran(d) == 0
               and not os.path.isdir(os.path.join(d, "smoke", "s02")), f"rc {rc}; the K1 line {'K1: a launch of the smoke' in log}")
    if t.want("K1"):
        rc, log, d, dt = t.session("K1", "A", {"E213_FAKE_HOST": "k1", "E213_FAKE_HOST_POINTS": "t01"})
        t.case("K1", rc == 0 and "K1: a launch of run 001-tie-t01 did not finish" in log and runs_ran(d) == 1 and "nothing further started" in log,
               f"rc {rc}; runs {runs_ran(d)}; '{line_of(log, 'STOP:')}'")
    for name, arm in (("HG", "A"), ("HGB", "B")):
        if t.want(name):
            t0 = time.time()
            pt = SHORT[arm][1].split("-")[-1]
            rc, log, d, dt = t.session(name, arm, {"E213_FAKE_HOST": "hang_term", "E213_FAKE_HANG_S": "14", "E213_FAKE_HOST_POINTS": pt})
            mk = wait_marker(os.path.join(d, "fake_sched.jsonl.hang-ended"), 30)
            rj = run_json(d, SHORT[arm][1])
            t.case(name, rc == 8 and f" HUNG: a device process (the host of {SHORT[arm][1]}" in log and "config end: not read (a device process of ours is HUNG" in log
                   and os.path.exists(os.path.join(d, "STOP")) and runs_ran(d) == 2 and [p.get("hung") for p in rj.get("procs", [])] == [True]
                   and "ended by itself" in mk and "nothing killed it" in mk, f"rc {rc}; the run's process hung {[p.get('hung') for p in rj.get('procs', [])]}; "
                   f"the hung double: '{mk[:100]}' ({time.time() - t0:.0f} s after the session began)")
    if t.want("SA"):
        rc, log, d, dt = t.session("SA", "A", {"E213_FAKE_HOST": "mismatch", "E213_FAKE_HOST_POINTS": "a039"})
        r1, r2, data, sc = reduce_and_score(S, "SA", {"A": d})
        runs = data.get("arms", {}).get("A", {}).get("points", {}).get("a039", {}).get("runs", [])
        flags = (sc.get("arms", {}).get("A") or {}).get("flags", [])
        t.case("SA", rc == 0 and r1 == 0 and r2 == 0 and len(runs) == 1 and runs[0].get("t_gemm_s") is None and (runs[0].get("record") or {}).get("shire_mask") == "0x1fffffffe"
               and any("a039" in f and "SET ASIDE" in f for f in flags) and runs_ran(d) == 3,
               f"rc {rc}; a039's run: t_gemm {runs[0].get('t_gemm_s') if runs else None}, the host's record {(runs[0].get('record') if runs else None)}; "
               f"the scorer's flags {[f for f in flags if 'a039' in f][:2]}")
    if t.want("TO"):
        rc, log, d, dt = t.session("TO", "A", {"E213_FAKE_HOST": "hang", "E213_FAKE_HOST_POINTS": "a039"})
        rj = run_json(d, "002-pass1-a039")
        t.case("TO", rc == 0 and [p.get("rc") for p in rj.get("procs", [])] == [124] and runs_ran(d) == 3 and " HUNG" not in log and "STOP" not in log,
               f"rc {rc}; a039's process rc {[p.get('rc') for p in rj.get('procs', [])]}; runs {runs_ran(d)}")
    if t.want("F2"):
        rc, log, d, dt = t.session("F2", "A", {"E213_FAKE_HOST": "crash", "E213_FAKE_HOST_POINTS": "a005,a032"}, seq="plan", scale="0.02",
                                   extra=["--rest-s", "0.15", "--tail-s", "0.1"])
        t.case("F2", rc == 0 and "STOP: two failed processes in a row (the last in run 004-pass1-a032)" in log and runs_ran(d) == 4,
               f"rc {rc}; runs {runs_ran(d)}; '{line_of(log, 'STOP:')}'")
    for name, arm, inj, want in (("B1", "A", [{"board_w": 71.0, "after_launches": t.n_smoke["A"] + 2, "count": 3}], "board 71.0 W above 70 W on 3 samples"),
                                 ("B1B", "B", [{"board_w": 73.0, "after_launches": t.n_smoke["B"] + 2, "count": 3}], "board 73.0 W above 72 W on 3 samples"),
                                 ("D1", "A", [{"die": 70, "after_launches": t.n_smoke["A"] + 2, "count": 1}], "die 70 C (the shires' mean) at or above 70 C"),
                                 ("D1B", "B", [{"die": 80, "after_launches": t.n_smoke["B"] + 2, "count": 1}], "die 80 C (the shires' mean) at or above 80 C"),
                                 ("D2", "A", [{"high": 88, "after_launches": t.n_smoke["A"] + 2, "count": 1}], "latch rose to 88 C (from 87 C")):
        if t.want(name):
            rc, log, d, dt = t.session(name, arm, inject=inj, scale="0.2")
            k0 = SHORT[arm][0]
            err = open(os.path.join(d, "runs", k0, "proc-00.err")).read() if os.path.exists(os.path.join(d, "runs", k0, "proc-00.err")) else ""
            t.case(name, rc == 0 and want in log and "nothing further started" in log and runs_ran(d) == 1 and "stopping:" in err,
                   f"rc {rc}; '{line_of(log, 'STOP:')}'; the host ended by the stop file {'stopping:' in err}")
    for name, arm, inj in (("D3", "A", [{"board_w": 70.0, "after_launches": t.n_smoke["A"] + 1}]),
                           ("D3B", "B", [{"board_w": 72.0, "after_launches": t.n_smoke["B"] + 1}])):
        if t.want(name):
            rc, log, d, dt = t.session(name, arm, inject=inj)
            t.case(name, rc == 0 and "STOP" not in log and runs_ran(d) == 3, f"rc {rc}; the board at the line (not above it) on every later sample: no stop ({'STOP' not in log}); runs {runs_ran(d)}")
    if t.want("D3C"):
        rc, log, d, dt = t.session("D3C", "B", inject=[{"die": 79, "after_launches": t.n_smoke["B"] + 1}])
        q = q_of(d).get("queue", [])
        t.case("D3C", rc == 0 and "STOP" not in log and runs_ran(d) == 1 and sum(1 for x in q if not x.get("ran") and "the die gate" in str(x.get("why"))) == 2,
               f"rc {rc}; the die at 79 C on every later sample: no stop ({'STOP' not in log}); {[(x['run'], x.get('ran'), str(x.get('why'))[:50]) for x in q]}")
    if t.want("DG"):
        rc, log, d, dt = t.session("DG", "A", inject=[{"die": 61, "after_launches": t.n_smoke["A"] + 2}])
        q = q_of(d).get("queue", [])
        t.case("DG", rc == 0 and runs_ran(d) == 1 and sum(1 for x in q if not x.get("ran") and "the die gate" in str(x.get("why"))) == 2,
               f"rc {rc}; {[(x['run'], x.get('ran'), str(x.get('why'))[:60]) for x in q]}")
    if t.want("CT"):
        rc, log, d, dt = t.session("CT", "B", seq="short", extra=["--rule-s", "8.5", "--rest-s", "2"])
        q = q_of(d).get("queue", [])
        first = next((i for i, x in enumerate(q) if not x.get("ran")), None)
        t.case("CT", rc == 0 and runs_ran(d) < 3 and first is not None and "the card-time rule" in str(q[first].get("why"))
               and all(not x.get("ran") for x in q[first:]), f"rc {rc}; {[(x['run'], x.get('ran'), str(x.get('why'))[:50]) for x in q]}")
    if t.want("OP"):
        rc, log, d, dt = t.session("OP", "A", signal_after=("run 001-tie-t01: gemmL2x4x4", 0.5), scale="0.3")
        err = open(os.path.join(d, "runs", "001-tie-t01", "proc-00.err")).read() if os.path.exists(os.path.join(d, "runs", "001-tie-t01", "proc-00.err")) else ""
        t.case("OP", rc == 0 and "the operator's signal 15" in log and runs_ran(d) == 1 and "stopping:" in err and os.path.exists(os.path.join(d, "MANIFEST.sha256")),
               f"rc {rc}; runs {runs_ran(d)}; the host ended by the stop file {'stopping:' in err}")
    if t.want("CR"):
        tree = os.path.join(S, "CR-tree")
        if os.path.exists(tree):
            shutil.rmtree(tree)
        dst = os.path.join(tree, "tools", "claims-v3", "e213")
        os.makedirs(dst)
        for f in ("run_e213.py", "e213_common.py", "e213_ident.py", "fake_card_e213.py", "points-e213.json", "kernel-e213.json", "ident_e213.py",
                  "forecast-e213b-v3.csv"):
            shutil.copy2(os.path.join(HERE, f), dst)
        os.makedirs(os.path.join(tree, "tools", "claims-v3", "e206"))
        for f in ("check_e206.py", "e206_common.py"):
            shutil.copy2(os.path.join(REPO, "tools", "claims-v3", "e206", f), os.path.join(tree, "tools", "claims-v3", "e206"))
        fc = os.path.join(tree, "tools", "matmul", "mm1", "v3", "out")       # the doubles read arm A's frozen forecast at every process
        os.makedirs(fc)
        shutil.copy2(os.path.join(REPO, "tools", "matmul", "mm1", "v3", "out", "mm1_v3_e213.csv"), fc)
        pj = os.path.join(dst, "points-e213.json")                          # the crash: the copy's arm A order names, as its second run, no point
        P = json.load(open(pj))
        P["arms"]["A"]["order"]["sequence"][1]["id"] = "a999"
        with open(pj, "w") as f:
            json.dump(P, f)
        rc, log, d, dt = t.session("CR", "A", runner=os.path.join(dst, "run_e213.py"))
        t.case("CR", rc == 1 and "CRASH: KeyError" in log and runs_ran(d) == 1 and os.path.exists(os.path.join(d, "queue.json"))
               and os.path.exists(os.path.join(d, "MANIFEST.sha256")) and os.path.exists(os.path.join(d, "crash.txt")) and "session end" in log
               and os.path.exists(os.path.join(d, "config-end.json")), f"rc {rc}; runs {runs_ran(d)}; '{line_of(log, 'CRASH')}'")
    if t.want("SF"):
        rc, log, d, dt = t.session("SF", "A", touch_after=("run 002-", 0.4), scale="0.3")
        q = q_of(d)
        qq = q.get("queue", [])
        last = qq[-1] if qq else {}
        t.case("SF", rc == 0 and len(qq) == 3 and not last.get("ran") and "after a stop" in str(last.get("why"))
               and "the operator's STOP file" in str(q.get("stop")) and "STOP: the operator's STOP file" in log
               and os.path.exists(os.path.join(d, "MANIFEST.sha256")) and os.path.exists(os.path.join(d, "STOP")),
               f"rc {rc}; runs {[(x.get('run'), x.get('ran')) for x in qq]}; the stop {q.get('stop')!r}; {dt:.0f} s")
    if t.want("SS"):
        rc, log, d, dt = t.session("SS", "A", touch_after=("smoke s02: the identity gate (", 0.25), scale="0.3")
        t.case("SS", rc == 16 and "smoke gate failed: a stop during the smoke's s02: the operator's STOP file" in log and runs_ran(d) == 0
               and not os.path.isdir(os.path.join(d, "smoke", "s03")) and os.path.exists(os.path.join(d, "STOP")),
               f"rc {rc}; '{line_of(log, 'smoke gate failed')}'")
    if t.want("S0"):
        rc, log, d, dt = t.session("S0", "B", pre_stop=True)
        t.case("S0", rc == 16 and "refused, no device opened: the operator's STOP file is already in the session's folder" in log
               and not os.path.exists(os.path.join(d, "config-start.json")) and "sampler started" not in log and not has_proc(d)
               and os.path.exists(os.path.join(d, "STOP")), f"rc {rc}; '{line_of(log, 'refused')}'")
    if t.want("DF"):
        rc, log, d, dt = t.session("DF", "A", {"E213_FAKE_SAMPLER": f"deaf:{t.n_smoke['A'] + 3}", "E213_FAKE_DEAF_S": "110"}, scale="0.3",
                                   watch_mgmt=True)
        mk = wait_marker(os.path.join(d, "fake_sched.jsonl.sampler-deaf-ended"), 120)
        q = q_of(d)
        t.case("DF", rc == 0 and t.max_mgmt <= 1 and "the sampler would not stop on SIGTERM" in str(q.get("stop"))
               and "config end: not read (the sampler did not stop on SIGTERM" in log and log.count("sampler started") == 1
               and bool(q.get("samplers_left")) and "ended by itself" in mk and "nothing killed it" in mk,
               f"rc {rc}; most processes on the stand-in management node at once {t.max_mgmt}; samplers started {log.count('sampler started')}; "
               f"left {q.get('samplers_left')}; the stop {str(q.get('stop'))[:100]!r}; the deaf double: '{mk[:80]}'; {dt:.0f} s")
    if t.want("RT"):
        rc, log, d, dt = t.session("RT", "A", {"E213_FAKE_HOST": "runtime1"})
        rca, loga, da, dta = t.session("RT-0", "A", {"E213_FAKE_HOST": "runtime"})
        t.case("RT", rc == 16 and "smoke gate failed" in log and "ANOTHER by its runtime line: card(s) ['1']" in log
               and not os.path.isdir(os.path.join(d, "smoke", "s02")) and rca == 0 and runs_ran(da) == 3 and "STOP" not in loga,
               f"card 1's line: rc {rc}: '{line_of(log, 'smoke s01: the identity gate GATE OK')}'; card 0's line (its own) rc {rca}, runs {runs_ran(da)}")
    if t.want("RT2"):
        rc, log, d, dt = t.session("RT2", "A", {"E213_FAKE_HOST": "runtime1", "E213_FAKE_HOST_POINTS": "t01"})
        q = q_of(d)
        t.case("RT2", rc == 0 and runs_ran(d) == 1 and "identity: the runtime named card(s) ['1']" in str(q.get("stop"))
               and "nothing further started" in log, f"rc {rc}; runs {runs_ran(d)}; the stop {str(q.get('stop'))[:120]!r}")
    if t.want("RTB"):
        rc, log, d, dt = t.session("RTB", "B", {"E213_FAKE_HOST": "runtime1", "E213_FAKE_HOST_POINTS": "t02"})
        q = q_of(d)
        rcb, logb, db, dtb = t.session("RTB-1", "B", {"E213_FAKE_HOST": "runtime"})
        t.case("RTB", rc == 0 and runs_ran(d) == 1 and "identity: the runtime named card(s) ['0']" in str(q.get("stop")) and rcb == 0 and runs_ran(db) == 3,
               f"card 0's line on arm B's tie: rc {rc}, the stop {str(q.get('stop'))[:90]!r}; card 1's own lines: rc {rcb}, runs {runs_ran(db)}")
    if t.want("RTC"):
        rc, log, d, dt = t.session("RTC", "A", {"E213_FAKE_CONFIG": "runtime1"})
        t.case("RTC", rc == 16 and "its stdout's runtime line(s) name card(s) ['1']" in log and "the gate, no launch" in log
               and "sampler started" not in log and not has_proc(d), f"rc {rc}; '{line_of(log, 'config start')}'")
    if t.want("BN"):
        smp = [{"t_ms": k, "board_w": 95.0} if k % 2 else {"t_ms": k, "temp_c": {"minshire": [50, 46, 87]}} for k in range(1, 8)]
        sa = C.Stops(**C.stops_of("A"))
        ra = [sa.feed(s) for s in smp]
        sb = C.Stops(**C.stops_of("B"))
        rb = [sb.feed(s) for s in smp]
        t.case("BN", ra == [[], [], [], [], ["stop"], [], []] and "95.0 W above 70 W on 3 samples" in (sa.stop or "") and rb == ra and "above 72 W" in (sb.stop or ""),
               f"95 W on every other sample, no board reading between: arm A {ra} {sa.stop!r}; arm B {rb} {sb.stop!r}")
    # ---------------------------------------------------------------- the identity gate, the walk and the kernel stops (four families)
    if t.want("GS"):
        rc, log, d, dt = t.session("GS", "A", {"E213_FAKE_GATE": "fail:s02"})
        sj = json.load(open(os.path.join(d, "smoke", "s02", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "s02", "smoke.json")) else {}
        t.case("GS", rc == 16 and "smoke gate failed: s02: the identity gate failed, no process started" in log and sj.get("ran") is False
               and not os.path.exists(os.path.join(d, "smoke", "s02", "proc.out")) and os.path.exists(os.path.join(d, "smoke", "s01", "proc.out"))
               and not os.path.isdir(os.path.join(d, "smoke", "s03")) and runs_ran(d) == 0, f"rc {rc}; '{line_of(log, 'smoke gate failed')}'")
    if t.want("GR"):
        rc, log, d, dt = t.session("GR", "A", {"E213_FAKE_GATE": "fail:a005"})
        r1, r2, data, sc = reduce_and_score(S, "GR", {"A": d})
        rr = data.get("arms", {}).get("A", {}).get("points", {}).get("a005", {}).get("runs", [])
        v = verdicts(sc, "A")
        t.case("GR", rc == 0 and runs_ran(d) == 2 and "STOP before run 003-pass1-a005's process: the identity gate failed" in log
               and not os.path.exists(os.path.join(d, "runs", "003-pass1-a005", "proc-00.out")) and r1 == 0 and r2 == 0
               and len(rr) == 1 and rr[0].get("checks") == [] and str((rr[0].get("detail") or {}).get("gate_words", "")).startswith("GATE FAILED") and v.get("R0") == "FAIL",
               f"rc {rc}; runs {runs_ran(d)}; the refused run in the data: checks {rr[0].get('checks') if rr else None}, gate words "
               f"{str((rr[0].get('detail') or {}).get('gate_words'))[:40] if rr else None}; R0 {v.get('R0')} ({(sc.get('arms', {}).get('A') or {}).get('R0_failures', [])[:1]})")
    if t.want("G211"):
        rc, log, d, dt = t.session("G211", "A", {"E213_FAKE_GATE": "fail:a085"}, seq="kernels")
        k = kseq("A")
        i85 = next(i for i, x in enumerate(k) if x.endswith("-a085"))
        r1, r2, data, sc = reduce_and_score(S, "G211", {"A": d})
        rr = data.get("arms", {}).get("A", {}).get("points", {}).get("a085", {}).get("runs", [])
        v = verdicts(sc, "A")
        t.case("G211", rc == 0 and runs_ran(d) == i85 and f"STOP before run {k[i85]}'s process: the identity gate failed (GATE FAILED: (dry, by path) rgm211 gemmL needs rgm211's ELF" in log
               and not os.path.exists(os.path.join(d, "runs", k[i85], "proc-00.out")) and "nothing further started" in log and r1 == 0 and r2 == 0
               and len(rr) == 1 and str(rr[0].get("gate", "")).startswith("GATE FAILED") and rr[0].get("walk") == {"names": [], "ok": [], "launches_bad": None}
               and v.get("R0") == "FAIL",
               f"rc {rc}; runs before it {runs_ran(d)} ({[x[10:] for x in k[:i85]]}); '{line_of(log, 'STOP before run')}'; the refused run in the data: gate "
               f"{str(rr[0].get('gate'))[:50] if rr else None}; R0 {v.get('R0')}")
    if t.want("WS"):
        rc, log, d, dt = t.session("WS", "A", {"E213_FAKE_HOST": "walkbad"})
        sm1 = json.load(open(os.path.join(d, "smoke", "s01", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "s01", "smoke.json")) else {}
        t.case("WS", rc == 16 and sm1.get("good") is True and "smoke gate failed: a stop during the smoke's s02: the kernel stops in the smoke's s02" in log
               and "walk_ok not true" in log and not os.path.isdir(os.path.join(d, "smoke", "s03")) and runs_ran(d) == 0,
               f"rc {rc}; s01 good {sm1.get('good')}; '{line_of(log, 'smoke gate failed')}'")
    if t.want("WR"):
        rc, log, d, dt = t.session("WR", "A", {"E213_FAKE_HOST": "walkbad", "E213_FAKE_HOST_POINTS": "a085"}, seq="gemmL211")
        r1, r2, data, sc = reduce_and_score(S, "WR", {"A": d})
        v = verdicts(sc, "A")
        k85 = [C.run_key(r) for r in C.sequence("A") if r["block"] == "pass1" and C.family(r["id"]) == "rgm211 gemmL"][0]
        t.case("WR", rc == 0 and runs_ran(d) == 1 and f"STOP: the kernel stops in run {k85} (rgm211 gemmL): " in log and "the walk check failed (walk_ok not true" in log
               and "nothing further started" in log and r1 == 0 and r2 == 0 and v.get("R0") == "FAIL",
               f"rc {rc}; runs {runs_ran(d)}; '{line_of(log, 'STOP:')}'; R0 {v.get('R0')} ({(sc.get('arms', {}).get('A') or {}).get('R0_failures', [])[:1]})")
    # ---------------------------------------------------------------- Amendment A1: the family smoke's own stop path (arm A's s04)
    fam_keys = [C.run_key(r) for r in C.sequence("A") if r["block"] == "pass1" and C.family(r["id"]) == "rgm211 gemmL"]
    for name, env in (("GF4", {"E213_FAKE_GATE": "fail:s04"}), ("WF4", {"E213_FAKE_HOST": "walkbad", "E213_FAKE_HOST_POINTS": "s04"})):
        if t.want(name):
            rc, log, d, dt = t.session(name, "A", env, seq="kernels")
            k = kseq("A")
            q = q_of(d)
            qq = {x["run"]: x for x in q.get("queue", [])}
            s4 = json.load(open(os.path.join(d, "smoke", "s04", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "s04", "smoke.json")) else {}
            skipped = [x for x in k if x in fam_keys]
            r1, r2, data, sc = reduce_and_score(S, name, {"A": d})
            v = verdicts(sc, "A")
            fl = (sc.get("arms", {}).get("A") or {}).get("flags", [])
            meas = (sc.get("arms", {}).get("A") or {}).get("measured", {})
            proc4 = os.path.exists(os.path.join(d, "smoke", "s04", "proc.out"))
            t.case(name, rc == 0 and "smoke s04: FAILED for its family alone (Amendment A1: its own stop path)" in log
                   and "the family 'rgm211 gemmL' is DROPPED - a074, a078, a081, a085 never start" in log
                   and "smoke gate passed: the runs start (Amendment A1: the family 'rgm211 gemmL' dropped by its smoke s04" in log
                   and "stop-path test passed" in log and "smoke gate failed" not in log and "STOP" not in log
                   and s4.get("a1_family_dropped") == "rgm211 gemmL" and s4.get("a1_session_level") == "" and s4.get("good") is False
                   and (proc4 is False if name == "GF4" else (proc4 and s4.get("walk_ok") is False))
                   and len(skipped) == 4 and runs_ran(d) == len(k) - 4 == 9
                   and all(qq.get(x, {}).get("ran") is False and "Amendment A1" in qq.get(x, {}).get("why", "") for x in skipped)
                   and not any(os.path.isdir(os.path.join(d, "runs", x)) for x in skipped)
                   and sorted((q.get("families_dropped") or {}).get("rgm211 gemmL", {}).get("points", [])) == ["a074", "a078", "a081", "a085"]
                   and r1 == 0 and r2 == 0 and v.get("R0") == "PASS" and any(x.startswith("A1: the family smoke of 'rgm211 gemmL' failed") for x in fl)
                   and not any(i in meas for i in ("a074", "a078", "a081", "a085")) and all(i in meas for i in ("a073", "a075", "a084", "a086")),
                   f"rc {rc}; '{line_of(log, 'FAILED for its family alone')}'; runs {runs_ran(d)} of {len(k)} ({[x[10:] for x in skipped]} never started); "
                   f"s04 dropped {s4.get('a1_family_dropped')!r}, its process {'ran' if proc4 else 'never started'}; R0 {v.get('R0')} "
                   f"({[x[:70] for x in fl if x.startswith('A1')][:1]})")
    if t.want("CF4"):
        rc, log, d, dt = t.session("CF4", "A", {"E213_FAKE_HOST": "wrong", "E213_FAKE_HOST_POINTS": "s04"})
        s4 = json.load(open(os.path.join(d, "smoke", "s04", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "s04", "smoke.json")) else {}
        t.case("CF4", rc == 0 and "smoke s04: FAILED for its family alone (Amendment A1: its own stop path)" in log and runs_ran(d) == 3
               and s4.get("check") == "wrong" and s4.get("a1_family_dropped") == "rgm211 gemmL" and "STOP" not in log
               and "the check of C wrong" in log,
               f"rc {rc}; s04's check {s4.get('check')!r}, dropped {s4.get('a1_family_dropped')!r}; runs {runs_ran(d)}; '{line_of(log, 'FAILED for its family')}'")
    if t.want("SF4"):
        rc, log, d, dt = t.session("SF4", "A", {"E213_FAKE_SAMPLER": f"dies:{t.n_smoke['A'] - 4}"})
        s4 = json.load(open(os.path.join(d, "smoke", "s04", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "s04", "smoke.json")) else {}
        t.case("SF4", rc == 16 and "smoke gate failed" in log and runs_ran(d) == 0 and s4.get("a1_family_dropped") is None
               and "FAILED for its family alone" not in log and not q_of(d).get("families_dropped"),
               f"rc {rc}; '{line_of(log, 'smoke gate failed')}'; s04 good {s4.get('good')}, its session-level reading {s4.get('a1_session_level')!r}, "
               f"dropped {s4.get('a1_family_dropped')!r}; runs {runs_ran(d)}")
    for name, mode, want in (("KF4", "k1", "K1: a launch of the smoke's s04 did not finish"), ("TF4", "hang", "rc 124")):
        if t.want(name):
            rc, log, d, dt = t.session(name, "A", {"E213_FAKE_HOST": mode, "E213_FAKE_HOST_POINTS": "s04"})
            s4 = json.load(open(os.path.join(d, "smoke", "s04", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "s04", "smoke.json")) else {}
            t.case(name, rc == 16 and "smoke gate failed: a stop during the smoke's s04" in log and want in log and runs_ran(d) == 0
                   and s4.get("a1_family_dropped") is None and s4.get("a1_session_level") and not q_of(d).get("families_dropped")
                   and "FAILED for its family alone" not in log,
                   f"rc {rc}; '{line_of(log, 'smoke gate failed')}'; s04's session-level reading {s4.get('a1_session_level')!r}; runs {runs_ran(d)}")
    for name, arm, env, pt, fam, want in (("CW", "A", {"E213_FAKE_HOST": "wrong"}, "a084", "rgm211 gemmLn", "the check of C reads 'wrong'"),
                                          ("TL", "A", {"E213_FAKE_HOST": "hang"}, "a085", "rgm211 gemmL", "rc 124: a launch timeout"),
                                          ("TE", "A", {"E213_FAKE_HOST": "tensor"}, "a086", "rgm136 gemmLnc", "tensor error"),
                                          ("TEB", "B", {"E213_FAKE_HOST": "tensor"}, "k40", "rgm136 gemmLnc", "tensor error")):
        if t.want(name):
            rc, log, d, dt = t.session(name, arm, dict(env, E213_FAKE_HOST_POINTS=pt), seq="kernels")
            k = kseq(arm)
            i = next(j for j, x in enumerate(k) if x.endswith("-" + pt))
            t.case(name, rc == 0 and runs_ran(d) == i + 1 and f"STOP: the kernel stops in run {k[i]} ({fam}): " in log and want in log
                   and "nothing further started" in log, f"rc {rc}; runs {runs_ran(d)}; '{line_of(log, 'STOP:')}'")
    if t.want("WG"):
        rc, log, d, dt = t.session("WG", "A", {"E213_FAKE_HOST": "crash", "E213_FAKE_HOST_POINTS": "a039"})
        rj = run_json(d, "002-pass1-a039")
        t.case("WG", rc == 0 and runs_ran(d) == 3 and [p.get("rc") for p in rj.get("procs", [])] == [134] and "STOP" not in log
               and "the process rc 134" in str(rj.get("flags")), f"rc {rc}; runs {runs_ran(d)}; a039 flags {rj.get('flags')}")
    for arm, name in (("A", "OR"), ("B", "ORB")):
        if t.want(name):
            rc, log, d, dt = t.session(name, arm, seq="plan", scale="0.02", extra=["--rest-s", "0.15", "--tail-s", "0.1"])
            seq = C.sequence(arm)
            q = q_of(d).get("queue", [])
            bad, nrec = [], 0
            for r, x in zip(seq, q):
                if x.get("run") != C.run_key(r) or not x.get("ran"):
                    bad.append(f"{C.run_key(r)}: {x.get('run')} ran {x.get('ran')}")
                    continue
                rj = json.load(open(os.path.join(d, "runs", C.run_key(r), "run.json")))
                pr = rj["procs"][0]
                argv = pr["argv"]
                want = C.host_argv(C.REPO, r["id"], C.RUN_SECONDS, C.RUN_BUDGET, os.path.join(d, "STOP"))
                if argv != want or "-k" in argv:
                    bad.append(f"{C.run_key(r)} argv")
                if not str(pr.get("gate", "")).startswith("GATE OK") or rj.get("gate_words") != pr.get("gate"):
                    bad.append(f"{C.run_key(r)} gate {str(pr.get('gate'))[:40]}")
                if pr["records"]["unparsed"] or pr["records"]["mismatched"] or not pr["n_launch"] or not pr.get("walk_ok"):
                    bad.append(f"{C.run_key(r)} records {pr['records']} walk {pr.get('walk_ok')}")
                nrec += pr["n_launch"]
            nreg = C.plan()["arms"][arm]["runs"]
            t.case(name, rc == 0 and len(q) == len(seq) == nreg and not bad, f"rc {rc}; {len(q)} runs of {len(seq)} (the plan's {nreg}), every key, argv (host "
                   f"and ELF by loop) and gate the registered, {nrec} host records read as their commands' ({len(bad)} differ{': ' + '; '.join(bad[:3]) if bad else ''}); {dt:.0f} s")
    if t.want("E2"):
        procs = {}
        for arm in ("A", "B"):
            for tag, ws in (("ok", "1"), ("W", "1.25")):
                d = os.path.join(S, f"E2-{arm}-{tag}")
                if os.path.exists(d):
                    shutil.rmtree(d)
                os.makedirs(d)
                e = {k: v for k, v in os.environ.items() if not k.startswith("E213_FAKE_")}
                e.update({"E213_FAKE_SCALE": "0.2", "E213_FAKE_TAU_S": "1", "E213_FAKE_LEAK": "0", "E213_FAKE_W_SCALE": ws})
                cmd = [sys.executable, "-B", RUNNER, "session", "--dry", "--arm", arm, "--t0", str(int(time.time())), "--out", os.path.join(d, "T"),
                       "--sequence", "e2e"] + FAST + ["--rest-s", "6"]
                procs[(arm, tag)] = (subprocess.Popen(cmd, cwd=REPO, stdout=open(os.path.join(d, "runner.out"), "w"), stderr=subprocess.STDOUT, env=e),
                                     os.path.join(d, "T"), float(ws))
        rcs = {k: p.wait(timeout=5400) for k, (p, d, ws) in procs.items()}
        for tag in ("ok", "W"):
            arms = {arm: procs[(arm, tag)][1] for arm in ("A", "B")}
            ws = procs[("A", tag)][2]
            r1, r2, data, sc = reduce_and_score(S, f"E2-{tag}", arms)
            stats = {}
            for arm in ("A", "B"):
                Ad = data.get("arms", {}).get(arm, {})
                worst_t, worst_j, n, nj = 0.0, 0.0, 0, 0
                for pid, P in Ad.get("points", {}).items():
                    for run in P["runs"]:
                        if not run.get("t_gemm_s"):
                            continue
                        n += 1
                        db = C.double_of(pid)
                        worst_t = max(worst_t, abs(run["t_gemm_s"] / db["t"] - 1))
                        w_in = db["W"] * ws
                        if run.get("p_work_w") is None or run.get("p_rest_w") is None:
                            worst_j = max(worst_j, 1.0)
                            continue
                        if w_in >= 3.0:
                            nj += 1
                            jo = (run["p_work_w"] - run["p_rest_w"]) * run["t_gemm_s"]
                            worst_j = max(worst_j, abs(jo / (w_in * db["t"]) - 1))
                stats[arm] = (n, worst_t, worst_j, nj)
            va, vb, pooled = verdicts(sc, "A"), verdicts(sc, "B"), {k: v.get("verdict") for k, v in (sc.get("pooled") or {}).items()}
            nA, nB = C.plan()["arms"]["A"]["runs"] - 3, C.plan()["arms"]["B"]["runs"] - 3
            base = (all(v == 0 for (arm, tg), v in rcs.items() if tg == tag) and r1 == 0 and r2 == 0 and stats["A"][0] == nA and stats["B"][0] == nB
                    and max(stats["A"][1], stats["B"][1]) < 1e-4 and max(stats["A"][2], stats["B"][2]) < 0.03)
            if tag == "ok":
                good = base and all(v.get(k) == "PASS" for v in (va, vb) for k in ("R0", "S6", "T1", "T2", "T3", "E1", "E2", "E3", "E4")) \
                    and all(v.get(k) == "MM1-v3 BETTER" for v in (va, vb) for k in ("H1", "H2", "H3", "H4", "H5")) \
                    and all(pooled.get(k) == "MM1-v3 BETTER" for k in ("HP1", "HP2", "HP3", "HP4", "HP5"))
            else:
                good = base and all(v.get(k) == "PASS" for v in (va, vb) for k in ("R0", "S6", "T1", "T2", "T3")) and \
                    all(v.get(k) == "FAIL" for v in (va, vb) for k in ("E1", "E2"))
            t.case(f"E2-{tag}", good, f"sessions rc {[rcs[(a_, tag)] for a_ in ('A', 'B')]}, reduce rc {r1}, score rc {r2}; runs (points) A {stats['A'][0]} "
                   f"B {stats['B'][0]}; t_gemm worst {max(stats['A'][1], stats['B'][1]):.2e}; J over idle against the injected watts x seconds worst "
                   f"{max(stats['A'][2], stats['B'][2]):.2%} ({stats['A'][3] + stats['B'][3]} runs of 3 W or more); arm A {json.dumps(va, sort_keys=True)}; "
                   f"arm B {json.dumps(vb, sort_keys=True)}; pooled {pooled}")
    if t.want("RF"):
        r = subprocess.run([sys.executable, "-B", RUNNER, "session", "--arm", "A", "--t0", "1", "--out", os.path.join(S, "RF1"), "--rest-s", "1"],
                           cwd=REPO, capture_output=True, text=True)
        e = dict(os.environ, V3_DRY="1")
        r2 = subprocess.run([sys.executable, "-B", RUNNER, "session", "--arm", "B", "--t0", "1", "--out", os.path.join(S, "RF2")],
                            cwd=REPO, capture_output=True, text=True, env=e)
        e = {k: v for k, v in os.environ.items() if k != "V3_DRY"}
        rc_ = subprocess.run([sys.executable, "-B", RUNNER, "session", "--dry", "--arm", "C", "--t0", "1", "--out", os.path.join(S, "RFC")],
                             cwd=REPO, capture_output=True, text=True, env=e)
        r3 = subprocess.run([sys.executable, "-B", RUNNER, "session", "--arm", "A", "--t0", str(int(time.time())), "--out", os.path.join(S, "RF3")],
                            cwd=REPO, capture_output=True, text=True, env=e)
        r4 = subprocess.run([sys.executable, "-B", RUNNER, "session", "--arm", "B", "--t0", str(int(time.time())), "--out", os.path.join(S, "RF4")],
                            cwd=REPO, capture_output=True, text=True, env=dict(e, ET_DEVICES="1"))
        log3 = open(os.path.join(S, "RF3", "session.log")).read() if os.path.exists(os.path.join(S, "RF3", "session.log")) else ""
        log4 = open(os.path.join(S, "RF4", "session.log")).read() if os.path.exists(os.path.join(S, "RF4", "session.log")) else ""
        r5 = subprocess.run([sys.executable, "-B", RUNNER, "session", "--arm", "B", "--t0", "1", "--out", os.path.join(S, "RF5"), "--cap-s", "100"],
                            cwd=REPO, capture_output=True, text=True, env=e)
        t.case("RF", r.returncode == 2 and "read with --dry only" in r.stdout and r2.returncode == 2 and "V3_DRY" in r2.stdout
               and rc_.returncode == 2 and "invalid choice: 'C'" in rc_.stderr and not os.path.exists(os.path.join(S, "RFC"))
               and r3.returncode == 16 and "refused, no device opened: the box or the build is not the registered one (this host is" in log3
               and r4.returncode == 16 and "refused, no device opened: the box or the build is not the registered one (this host is" in log4
               and r5.returncode == 2 and "--cap-s" in r5.stdout
               and not os.path.exists(os.path.join(S, "RF3", "config-start.json")) and not os.path.exists(os.path.join(S, "RF4", "config-start.json")),
               f"rc {r.returncode}, {r2.returncode}, --arm C {rc_.returncode}, the real runner arm A {r3.returncode} and arm B {r4.returncode} "
               f"('{line_of(log4, 'refused')}'), --cap-s without --dry {r5.returncode}")
    print(f"SELFTEST-RUN-E213 {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
