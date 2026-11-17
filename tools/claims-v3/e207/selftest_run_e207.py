#!/usr/bin/env python3
"""E207's runner desk test (Q199, lane kit-e207, Mon 16 Nov 2026, before any E207 datum): run_e207.py on fake_card_e207.py's doubles, each
case its own --dry session (a subprocess) in a scratch directory, E206's selftest_run_e206.py form (landed in 906699ea; E190's before it) for
E207's one arm. No device, no box. Run it ONLY inside a sandbox with no /dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2): case RF
runs the real runner, which must stop at its box check before anything else.

    /usr/bin/python3 -B tools/claims-v3/e207/selftest_run_e207.py <scratch dir> [--only CASE ...] > logs/selftest-run-e207.txt

Cases (the doubles' latch reads 87 C, as aifoundry3 card 0's committed telemetry does):
  G1 the short sequence (the tie t01, two points): rc 0; the identity gate (/dev/et0_mgmt, ID 0); the identity read; the smoke's three
     processes (b01, b02, b03; each at MM1-v1's counter-mean forecast) THEN the stop-path test; three runs; the closing config; the manifest;
     the 87 C latch tripped nothing
  C1 the start config not as found (TDP 65 W): 16, the gate, no sampler, no host        C2 the config names card 1: 16
  C4 the config with no identity block: 16          C5 the config read fails: 16
  C6 the config read hangs past its TERM: HUNG (rc 8), no sampler, no closing read, nothing killed: the hung double ends by itself
  C7 card 0's runtime line ("Opening device 0") on the config read's stdout: dropped, the session runs (rc 0)
  H1 another login on card 0: 16, refused, no device opened (no config read)      H3 another login's line on card 1: 16 (any other login)
  H4 et-who unreadable (rc 1): 16          H5 a device process of ours: 16          H6 a CI job: 16
  L1 the card's lock held: 16, no config read
  S1 the sampler would not start: 16       S2 the sampler holds card 1's node: the identity read stops it, 16, no host process
  S3 the sampler goes silent in the runs: the next run's gate restarts it (SIGTERM to the stale one), rc 0
  S4 the sampler dies in the runs: restarted, rc 0
  P1 the stop-path test on a session with no live samples (in-process): it cannot trip, so it fails
  R1 a smoke check of C wrong: the smoke gate fails, 16, no run      R2 a smoke host crashes: 16      R3 a smoke host names and holds card 1:
     the watch trips at once, the stop file, "stopping:", 16, no second smoke process    R4 the board does not rise in the smoke: 16
  R5 card 0's runtime line INSIDE a smoke record (at byte 77): dropped, the record read whole, the smoke passes, rc 0
  R6 a smoke host's records name another shire mask: not read, the smoke gate fails, 16
  R7 a smoke host's counter mean at 3 x MM1-v1's counter-mean forecast (the doubles' clock at 1,800 MHz would show the same; here the
     double's W and seconds as forecast, its cycles scaled): the smoke's ratio outside 50-250%, the smoke gate fails, 16
  K0 a smoke host says "kernel did not finish": the K1 line, the smoke gate fails, 16, no second smoke process (step 10 reads K1-STOPPED)
  K1 a run's host says "kernel did not finish": the session stops (K1), nothing further, rc 0 (step 10 reads K1-STOPPED)
  HG a run's host IGNORES its timeout's TERM: HUNG (rc 8), the stop file, nothing further, no closing config read, NOTHING KILLED: the hung
     double ends by itself ~14 s after it started (its marker file)
  TO a run's host sleeps past 10 s but ends on TERM: timeout's rc 124, flagged, the session goes on (one failure), rc 0
  SA a run's host prints records of another shire mask (n06, the first point of pass 1): never read as data; the reducer passes the host's
     record on and the FROZEN scorer sets the run aside and flags it (E207.md 7), the point NO DATA
  F2 two failed processes in a row: the session stops, rc 0
  B1 the board above 70 W on 3 samples in a run: the stop, the host ends by its stop file ("stopping:"), nothing further, rc 0
  D1 the die (the shires' mean) at 70 C: the stop          D2 the latch rises to 88 C: the stop ("latch rose")
  D3 the board at 70.0 W (not above 70) on every later sample: no stop, rc 0
  DG the die gate: the die held at 61 C after the first run (gate min(60, rest + 4)): the later runs wait and are NO DATA
  CT the card-time rule (--rule-s 6.5): no run starts after it, rc 0          OP an operator's SIGTERM to the runner mid-run: the stop file,
     the host ends at its boundary, nothing further, rc 0           CR the runner crashes (MM1-v1's file missing in a copied tree): "CRASH:",
     the closing still runs (queue.json, the manifest), rc 1
  SF THE OPERATOR'S STOP FILE touched during run 002: run 003 never starts, the stop names the file, rc 0, the manifest
  S0 a STOP file already in the session's folder when the runner starts: refused before any device (16), no config read, the file kept
  DF a sampler that goes silent and IGNORES SIGTERM past the runner's two waits (90 s): the session stops ("would not stop"), NEVER two
     processes on the stand-in management node at once (a poller over /proc), no closing config read while it lives, rc 0, and the deaf
     double ends by itself (nothing kills it)
  RT card 1's runtime line ("Opening device 1") on a smoke host: the identity trip, the smoke gate fails, 16, no second smoke process; card
     0's line (its own) passes, rc 0      RT2 card 1's line on the first run's host: STOP (identity), nothing further, rc 0
  RTC card 1's line on the start config read: the identity gate, 16, no sampler
  BN the board line (in-process, e207_common.Stops): 95 W on every other sample with no board reading between trips at the third reading
  OR THE ORDER: the whole registered sequence (109 runs) at a tiny scale: every run's key and argv the registered ones (the point's or the
     tie's host_args, --seconds 6 --budget 7.5, the kit's --kernel and --stop-file, under `timeout 10`, never -k), in order, and every host
     record read as its command's (the subset masks in the host's own spelling, 0xf0f0f0f among them)
  E2 END TO END twice at once (the first tie, pass 1's first 24 points, the second tie; a 6 s rest read, since the reducer's rest window is
     the registered 5 s; leakage off) through the reducer and the FROZEN scorer: E2-A with the doubles' watts and seconds at MM1-v1's
     forecasts: every run's t_gemm MM1-v1's seconds, its J over idle the injected watts x seconds; R0, T1, T2, T3, E1, E2, E3, E4, S6 PASS
     and H1, H2 MM1-v1 BETTER (its cycles are the measurement); E2-W with the watts 25% over: T1-T3 PASS, E1 and E2 FAIL
  RF the refusals: the --dry options without --dry, V3_DRY without --dry, `--arm B` (argparse), and the REAL runner on this desk stopping
     at its box check
Every number here comes from the doubles (MM1-v1's frozen forecasts driven through a toy card): a desk check of code, not a measurement and not
a reading of E207. SPDX-License-Identifier: Apache-2.0
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
RUNNER = os.path.join(HERE, "run_e207.py")
sys.path.insert(0, HERE)
import e207_common as C  # noqa: E402

FAST = ["--rest-s", "0.3", "--smoke-rest-s", "1.5", "--tail-s", "0.2", "--gate-wait-s", "3"]


class T:
    def __init__(self, scratch, only):
        self.S, self.only = scratch, set(only or [])
        self.n = self.ok = 0
        self.n_smoke = 21

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
        e = {k: v for k, v in os.environ.items() if not k.startswith("E207_FAKE_")}
        e.update({"E207_FAKE_SCALE": scale, "E207_FAKE_TAU_S": "1"})
        if inject is not None:
            ip = os.path.join(d, "inject.json")
            json.dump(inject, open(ip, "w"))
            e["E207_FAKE_INJECT"] = ip
        e.update(env or {})
        out = os.path.join(d, "T")
        if pre_stop:                  # case S0 (fix-e206): the operator's STOP file there before the runner starts
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
                        else:         # case SF (fix-e206): the operator touches the session's STOP file (CARD-LANE-BRIEF 2)
                            open(os.path.join(out, "STOP"), "a").close()
                        break
                    time.sleep(0.1)
            if watch_mgmt:            # case DF (fix-e206): how many processes hold the stand-in management node at once, polled 5 times a s
                fake = os.path.realpath(os.path.join(out, "fakedev"))
                while p.poll() is None and time.time() - t0 < 1800:
                    self.max_mgmt = max(self.max_mgmt, mgmt_holders(fake))
                    time.sleep(0.2)
            rc = p.wait(timeout=1800)
        log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
        return rc, log, out, time.time() - t0


def mgmt_holders(fake):
    """The processes (of this login) whose open files include a stand-in *_mgmt node under the session's fakedev (fix-e206, case DF)."""
    n, me = 0, os.getuid()
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            if os.stat(f"/proc/{pid}").st_uid != me:      # our own processes only
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
    print(f"selftest_run_e207 ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; /dev/et*: none; "
          f"/run/lock entries: {len(os.listdir('/run/lock')) if os.path.isdir('/run/lock') else 'none'}", flush=True)

    if t.want("G1"):
        rc, log, d, dt = t.session("G1", "A")
        ls = log.splitlines()
        i_sm = max([i for i, x in enumerate(ls) if "smoke b03:" in x] or [-1])
        i_sp = min([i for i, x in enumerate(ls) if "stop-path test passed" in x] or [10 ** 6])
        sm = [json.load(open(os.path.join(d, "smoke", p, "smoke.json"))) for p in C.SMOKE_PIDS if os.path.exists(os.path.join(d, "smoke", p, "smoke.json"))]
        t.n_smoke = sum(x["n_launch"] for x in sm) or t.n_smoke
        idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
        t.case("G1", rc == 0 and "the card's identity: PCIe target /dev/et0_mgmt, physical device ID 0" in log and "the identity read: " in log
               and len(sm) == 3 and all(x["good"] for x in sm) and all("MM1-v1's counter-mean forecast" in x.get("cycles_point_is", "") for x in sm)
               and 0 <= i_sm < i_sp < 10 ** 6 and runs_ran(d) == 3 and "config end: {" in log
               and os.path.exists(os.path.join(d, "MANIFEST.sha256")) and "STOP" not in log and idn.get("config_start", {}).get("minion_mv") == 523
               and [x["run"] for x in q_of(d).get("queue", [])] == ["001-tie-t01", "002-pass1-n06", "003-pass1-b32"],
               f"rc {rc}; the smoke {[x['identity_ok'] and x['good'] for x in sm]} (ratios {[round(x['cycles_ratio'], 3) for x in sm]}) then the "
               f"stop-path test (lines {i_sm} < {i_sp}); {runs_ran(d)} runs; {t.n_smoke} smoke launches; the 87 C latch tripped nothing "
               f"({'STOP' not in log}); {dt:.0f} s")
    for name, mode, want in (("C1", "tdp65", "the gate, no launch"), ("C2", "card1", "/dev/et1_mgmt, not /dev/et0_mgmt"),
                             ("C4", "noident", "no 'PCIe target' line"), ("C5", "fail", "config read rc 1")):
        if t.want(name):
            rc, log, d, dt = t.session(name, "A", {"E207_FAKE_CONFIG": mode})
            t.case(name, rc == 16 and want in log and "the gate, no launch" in log and "sampler started" not in log and not has_proc(d),
                   f"rc {rc}; '{[x[24:200] for x in log.splitlines() if 'config start' in x][:1]}'")
    if t.want("C6"):
        rc, log, d, dt = t.session("C6", "A", {"E207_FAKE_CONFIG": "hang", "E207_FAKE_HANG_S": "16"})
        mk = wait_marker(os.path.join(d, "fake_sched.jsonl.config-hang-ended"), 30)
        t.case("C6", rc == 8 and " HUNG: " in log and "sampler started" not in log and "config end: not read" in log and "ended by itself" in mk
               and q_of(d).get("hung"), f"rc {rc}; the HUNG line {' HUNG: ' in log}; the hung double: '{mk[:90]}'")
    if t.want("C7"):
        rc, log, d, dt = t.session("C7", "A", {"E207_FAKE_CONFIG": "runtime"})
        idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
        t.case("C7", rc == 0 and "physical device ID 0" in log and runs_ran(d) == 3 and idn.get("config_start", {}).get("runtime_cards") == ["0"],
               f"rc {rc}; the config read whole past card 0's runtime line ({idn.get('config_start', {}).get('runtime_cards')})")
    for name, env, want in (("H1", {"E207_FAKE_ETWHO": "other"}, "holder line(s) of another login"),
                            ("H3", {"E207_FAKE_ETWHO": "other1"}, "holder line(s) of another login"),
                            ("H4", {"E207_FAKE_ETWHO": "fail"}, "et-who unreadable (rc 1)"),
                            ("H5", {"E207_FAKE_PS": "ours"}, "other device process(es) of ours"),
                            ("H6", {"E207_FAKE_PS": "ci"}, "CI job")):
        if t.want(name):
            rc, log, d, dt = t.session(name, "A", env)
            t.case(name, rc == 16 and "refused, no device opened: a holder or a device process" in log and want in log
                   and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}; '{[x[24:220] for x in log.splitlines() if 'refused' in x][:1]}'")
    if t.want("L1"):
        d0 = os.path.join(S, "L1", "T")
        os.makedirs(d0, exist_ok=True)
        lk = os.path.join(d0, "dry.lock")
        open(lk, "a").close()
        holder = subprocess.Popen(["flock", "-o", lk, "sleep", "20"], stdin=subprocess.DEVNULL)
        time.sleep(0.5)
        e = {k: v for k, v in os.environ.items() if not k.startswith("E207_FAKE_")}
        r = subprocess.run([sys.executable, "-B", RUNNER, "session", "--dry", "--arm", "A", "--t0", str(int(time.time())), "--out", d0] + FAST,
                           cwd=REPO, capture_output=True, text=True, env=e)
        holder.terminate()
        holder.wait()
        log = open(os.path.join(d0, "session.log")).read()
        t.case("L1", r.returncode == 16 and "refused, no device opened: the card's lock is held" in log and not os.path.exists(os.path.join(d0, "config-start.json")),
               f"rc {r.returncode}")
    if t.want("S1"):
        rc, log, d, dt = t.session("S1", "A", {"E207_FAKE_SAMPLER": "dead"})
        t.case("S1", rc == 16 and "the sampler would not start" in log and not has_proc(d), f"rc {rc}")
    if t.want("S2"):
        rc, log, d, dt = t.session("S2", "A", {"E207_FAKE_SAMPLER": "card1"})
        t.case("S2", rc == 16 and "the identity read (the sampler running, before the smoke)" in log and "the gate, no launch" in log and not has_proc(d),
               f"rc {rc}; '{[x[24:220] for x in log.splitlines() if 'identity read' in x][:1]}'")
    if t.want("S3"):
        rc, log, d, dt = t.session("S3", "A", {"E207_FAKE_SAMPLER": f"hangs:{t.n_smoke + 3}"})
        t.case("S3", rc == 0 and "the sampler is not live" in log and log.count("sampler started") >= 2 and runs_ran(d) >= 2,
               f"rc {rc}; sampler starts {log.count('sampler started')}; runs {runs_ran(d)}")
    if t.want("S4"):
        rc, log, d, dt = t.session("S4", "A", {"E207_FAKE_SAMPLER": f"dies:{t.n_smoke + 3}"})
        t.case("S4", rc == 0 and log.count("sampler started") >= 2 and runs_ran(d) >= 2, f"rc {rc}; sampler starts {log.count('sampler started')}; runs {runs_ran(d)}")
    if t.want("P1"):
        import run_e207 as R
        d = os.path.join(S, "P1")
        os.makedirs(d, exist_ok=True)
        ns = argparse.Namespace(what="session", arm="A", t0=int(time.time()), out=os.path.join(d, "T"), deadline_epoch=0, dry=True,
                                sequence="short", rest_s=0.3, smoke_rest_s=1.5, tail_s=0.2, gate_wait_s=3, rule_s=C.CARD_RULE_S, cap_s=C.CAP_S)
        s = R.Session(ns)
        s.t_first = time.time()
        ok, res = s.stop_path_test()
        t.case("P1", not ok and not res["board"]["tripped"] and not res["die"]["tripped"], f"ok {ok}; {json.dumps({k: v['tripped'] for k, v in res.items()})}")
    for name, env, want in (("R1", {"E207_FAKE_HOST": "wrong"}, "check wrong"), ("R2", {"E207_FAKE_HOST": "crash"}, "rc 134"),
                            ("R4", {"E207_FAKE_HOST": "norise"}, "the board's rise"), ("R6", {"E207_FAKE_HOST": "mismatch"}, "not its command's"),
                            ("R7", {"E207_FAKE_HOST": "cyc3x"}, "cycles ratio 3.0")):
        if t.want(name):
            rc, log, d, dt = t.session(name, "A", env)
            t.case(name, rc == 16 and "smoke gate failed" in log and runs_ran(d) == 0 and want in log
                   and not os.path.isdir(os.path.join(d, "smoke", "b02")), f"rc {rc}; '{[x[24:230] for x in log.splitlines() if 'smoke b01' in x][:1]}'")
    if t.want("R3"):
        rc, log, d, dt = t.session("R3", "A", {"E207_FAKE_HOST": "card1"})
        err = open(os.path.join(d, "smoke", "b01", "proc.err")).read() if os.path.exists(os.path.join(d, "smoke", "b01", "proc.err")) else ""
        t.case("R3", rc == 16 and os.path.exists(os.path.join(d, "STOP")) and "stopping:" in err and "smoke gate failed" in log
               and not os.path.isdir(os.path.join(d, "smoke", "b02")), f"rc {rc}; the host stopped by the file {'stopping:' in err}")
    if t.want("R5"):
        rc, log, d, dt = t.session("R5", "A", {"E207_FAKE_HOST": "runtime"})
        sm = json.load(open(os.path.join(d, "smoke", "b01", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "b01", "smoke.json")) else {}
        t.case("R5", rc == 0 and sm.get("records", {}).get("runtime_lines") == 2 and sm.get("records", {}).get("unparsed") == 0 and "smoke gate passed" in log,
               f"rc {rc}; b01's records {sm.get('records')}")
    if t.want("K0"):
        rc, log, d, dt = t.session("K0", "A", {"E207_FAKE_HOST": "k1"})
        t.case("K0", rc == 16 and "K1: a launch of the smoke's b01 did not finish" in log and "smoke gate failed" in log and runs_ran(d) == 0
               and not os.path.isdir(os.path.join(d, "smoke", "b02")), f"rc {rc}; the K1 line {'K1: a launch of the smoke' in log}; no second smoke process")
    run_from = {"E207_FAKE_HOST_FROM_N": str(t.n_smoke), "E207_FAKE_HOST_COUNT": "1"}   # the first run's host sees the smoke's n_smoke launches
    if t.want("K1"):
        rc, log, d, dt = t.session("K1", "A", dict(run_from, E207_FAKE_HOST="k1"))
        t.case("K1", rc == 0 and "STOP: K1: a launch of run 001-tie-t01 did not finish" in log and runs_ran(d) == 1, f"rc {rc}; runs {runs_ran(d)}")
    if t.want("HG"):
        t0 = time.time()
        rc, log, d, dt = t.session("HG", "A", dict(run_from, E207_FAKE_HOST="hang_term", E207_FAKE_HANG_S="14"))
        mk = wait_marker(os.path.join(d, "fake_sched.jsonl.hang-ended"), 30)
        rj = json.load(open(os.path.join(d, "runs", "001-tie-t01", "run.json"))) if os.path.exists(os.path.join(d, "runs", "001-tie-t01", "run.json")) else {}
        t.case("HG", rc == 8 and " HUNG: a device process (the host of 001-tie-t01" in log and "config end: not read (a device process of ours is HUNG" in log
               and os.path.exists(os.path.join(d, "STOP")) and runs_ran(d) == 1 and [p.get("hung") for p in rj.get("procs", [])] == [True]
               and "ended by itself" in mk and "nothing killed it" in mk, f"rc {rc}; the run's process hung {[p.get('hung') for p in rj.get('procs', [])]}; "
               f"the hung double: '{mk[:100]}' ({time.time() - t0:.0f} s after the session began)")
    if t.want("SA"):
        rc, log, d, dt = t.session("SA", "A", {"E207_FAKE_HOST": "mismatch", "E207_FAKE_HOST_FROM_N": str(t.n_smoke + 1), "E207_FAKE_HOST_COUNT": "1"})
        dj, sj = os.path.join(S, "SA-data.json"), os.path.join(S, "SA-scored.json")
        r1 = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "reduce_e207.py"), "--arm", f"A={d}", "--out", dj], capture_output=True, text=True)
        r2 = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "score_e207.py"), dj, "--out", sj], capture_output=True, text=True)
        data = json.load(open(dj)) if os.path.exists(dj) else {}
        sc = json.load(open(sj)) if os.path.exists(sj) else {}
        run = ((data.get("arms", {}).get("A", {}).get("points", {}).get("n06") or {}).get("runs") or [{}])[0]
        aside = sc.get("set_aside", {}).get("n06")
        t.case("SA", rc == 0 and r1.returncode == 0 and r2.returncode == 0 and run.get("t_gemm_s") is None and run.get("record", {}).get("shire_mask") == "0x1fffffffe"
               and bool(aside) and sc.get("points", {}).get("n06", {}).get("verdict") == "NO DATA",
               f"rc {rc}; n06's run: t_gemm {run.get('t_gemm_s')}, the host's record {run.get('record')}; the scorer set it aside {aside}")
    if t.want("TO"):
        rc, log, d, dt = t.session("TO", "A", dict(run_from, E207_FAKE_HOST="hang"))
        rj = json.load(open(os.path.join(d, "runs", "001-tie-t01", "run.json"))) if os.path.exists(os.path.join(d, "runs", "001-tie-t01", "run.json")) else {}
        t.case("TO", rc == 0 and [p.get("rc") for p in rj.get("procs", [])] == [124] and runs_ran(d) == 3 and " HUNG" not in log,
               f"rc {rc}; the tie's process rc {[p.get('rc') for p in rj.get('procs', [])]}; runs {runs_ran(d)}")
    if t.want("F2"):
        rc, log, d, dt = t.session("F2", "A", {"E207_FAKE_HOST": "crash", "E207_FAKE_HOST_FROM_N": str(t.n_smoke), "E207_FAKE_HOST_COUNT": "2"})
        t.case("F2", rc == 0 and "STOP: two failed processes in a row" in log and runs_ran(d) == 2, f"rc {rc}; runs {runs_ran(d)}")
    for name, inj, want in (("B1", [{"board_w": 71.0, "after_launches": t.n_smoke + 2, "count": 3}], "board 71.0 W above 70 W on 3 samples"),
                            ("D1", [{"die": 70, "after_launches": t.n_smoke + 2, "count": 1}], "die 70 C (the shires' mean) at or above 70 C"),
                            ("D2", [{"high": 88, "after_launches": t.n_smoke + 2, "count": 1}], "latch rose to 88 C (from 87 C")):
        if t.want(name):
            rc, log, d, dt = t.session(name, "A", inject=inj, scale="0.2")
            err = open(os.path.join(d, "runs", "001-tie-t01", "proc-00.err")).read() if os.path.exists(os.path.join(d, "runs", "001-tie-t01", "proc-00.err")) else ""
            t.case(name, rc == 0 and want in log and "nothing further started" in log and runs_ran(d) == 1 and "stopping:" in err,
                   f"rc {rc}; '{[x[24:200] for x in log.splitlines() if 'STOP:' in x][:1]}'; the host ended by the stop file {'stopping:' in err}")
    if t.want("D3"):
        rc, log, d, dt = t.session("D3", "A", inject=[{"board_w": 70.0, "after_launches": t.n_smoke + 1}])
        t.case("D3", rc == 0 and "STOP" not in log and runs_ran(d) == 3, f"rc {rc}; 70.0 W on every later sample: no stop ({'STOP' not in log})")
    if t.want("DG"):
        rc, log, d, dt = t.session("DG", "A", inject=[{"die": 61, "after_launches": t.n_smoke + 2}])
        q = q_of(d).get("queue", [])
        t.case("DG", rc == 0 and runs_ran(d) == 1 and sum(1 for x in q if not x.get("ran") and "the die gate" in str(x.get("why"))) == 2,
               f"rc {rc}; {[(x['run'], x.get('ran'), str(x.get('why'))[:60]) for x in q]}")
    if t.want("CT"):
        rc, log, d, dt = t.session("CT", "A", seq="two", extra=["--rule-s", "6.5", "--rest-s", "2"])
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
        dst = os.path.join(tree, "tools", "claims-v3", "e207")
        os.makedirs(dst)
        for f in ("run_e207.py", "e207_common.py", "e207_ident.py", "fake_card_e207.py", "points-e207.json", "plan-e207.json"):
            shutil.copy2(os.path.join(HERE, f), dst)
        rc, log, d, dt = t.session("CR", "A", runner=os.path.join(dst, "run_e207.py"))
        t.case("CR", rc == 1 and "CRASH: FileNotFoundError" in log and os.path.exists(os.path.join(d, "queue.json")) and os.path.exists(os.path.join(d, "MANIFEST.sha256"))
               and "session end" in log, f"rc {rc}; '{[x[24:160] for x in log.splitlines() if 'CRASH' in x][:1]}'")
    if t.want("SF"):
        rc, log, d, dt = t.session("SF", "A", touch_after=("run 002-", 0.4), scale="0.3")
        q = q_of(d)
        qq = q.get("queue", [])
        last = qq[-1] if qq else {}
        t.case("SF", rc == 0 and len(qq) == 3 and not last.get("ran") and "after a stop" in str(last.get("why"))
               and "the operator's STOP file" in str(q.get("stop")) and "STOP: the operator's STOP file" in log
               and os.path.exists(os.path.join(d, "MANIFEST.sha256")) and os.path.exists(os.path.join(d, "STOP")),
               f"rc {rc}; runs {[(x.get('run'), x.get('ran')) for x in qq]}; the stop {q.get('stop')!r}; {dt:.0f} s")
    if t.want("S0"):
        rc, log, d, dt = t.session("S0", "A", pre_stop=True)
        t.case("S0", rc == 16 and "refused, no device opened: the operator's STOP file is already in the session's folder" in log
               and not os.path.exists(os.path.join(d, "config-start.json")) and "sampler started" not in log and not has_proc(d)
               and os.path.exists(os.path.join(d, "STOP")), f"rc {rc}; '{[x[24:200] for x in log.splitlines() if 'refused' in x][:1]}'")
    if t.want("DF"):
        rc, log, d, dt = t.session("DF", "A", {"E207_FAKE_SAMPLER": f"deaf:{t.n_smoke + 3}", "E207_FAKE_DEAF_S": "110"}, scale="0.3",
                                   watch_mgmt=True)
        mk = wait_marker(os.path.join(d, "fake_sched.jsonl.sampler-deaf-ended"), 120)
        q = q_of(d)
        t.case("DF", rc == 0 and t.max_mgmt <= 1 and "the sampler would not stop on SIGTERM" in str(q.get("stop"))
               and "config end: not read (the sampler did not stop on SIGTERM" in log and log.count("sampler started") == 1
               and bool(q.get("samplers_left")) and "ended by itself" in mk and "nothing killed it" in mk,
               f"rc {rc}; most processes on the stand-in management node at once {t.max_mgmt}; samplers started {log.count('sampler started')}; "
               f"left {q.get('samplers_left')}; the stop {str(q.get('stop'))[:100]!r}; the deaf double: '{mk[:80]}'; {dt:.0f} s")
    if t.want("RT"):
        rc, log, d, dt = t.session("RT", "A", {"E207_FAKE_HOST": "runtime1"})
        rca, loga, da, dta = t.session("RT-0", "A", {"E207_FAKE_HOST": "runtime"})
        t.case("RT", rc == 16 and "smoke gate failed" in log and "ANOTHER by its runtime line: card(s) ['1']" in log
               and not os.path.isdir(os.path.join(d, "smoke", "b02")) and rca == 0 and runs_ran(da) == 3 and "STOP" not in loga,
               f"card 1's line: rc {rc}: '{[x[24:200] for x in log.splitlines() if 'smoke b01' in x][:1]}'; card 0's line (its own) rc {rca}, "
               f"runs {runs_ran(da)}")
    if t.want("RT2"):
        rc, log, d, dt = t.session("RT2", "A", dict(run_from, E207_FAKE_HOST="runtime1"))
        q = q_of(d)
        t.case("RT2", rc == 0 and runs_ran(d) == 1 and "identity: the runtime named card(s) ['1']" in str(q.get("stop"))
               and "nothing further started" in log, f"rc {rc}; runs {runs_ran(d)}; the stop {str(q.get('stop'))[:120]!r}")
    if t.want("RTC"):
        rc, log, d, dt = t.session("RTC", "A", {"E207_FAKE_CONFIG": "runtime1"})
        t.case("RTC", rc == 16 and "its stdout's runtime line(s) name card(s) ['1']" in log and "the gate, no launch" in log
               and "sampler started" not in log and not has_proc(d), f"rc {rc}; '{[x[24:220] for x in log.splitlines() if 'config start' in x][:1]}'")
    if t.want("BN"):
        smp = [{"t_ms": k, "board_w": 95.0} if k % 2 else {"t_ms": k, "temp_c": {"minshire": [50, 46, 87]}} for k in range(1, 8)]
        sa = C.Stops(**C.stops_of("A"))
        ra = [sa.feed(s) for s in smp]
        t.case("BN", ra == [[], [], [], [], ["stop"], [], []] and "95.0 W above 70 W on 3 samples" in (sa.stop or ""),
               f"95 W on every other sample, no board reading between: {ra}, {sa.stop!r}")
    if t.want("OR"):
        rc, log, d, dt = t.session("OR", "A", seq="plan", scale="0.02", extra=["--rest-s", "0.15", "--tail-s", "0.1"])
        seq = C.sequence("A")
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
            if pr["records"]["unparsed"] or pr["records"]["mismatched"] or not pr["n_launch"]:
                bad.append(f"{C.run_key(r)} records {pr['records']}")
            nrec += pr["n_launch"]
        t.case("OR", rc == 0 and len(q) == len(seq) == 109 and not bad, f"rc {rc}; {len(q)} runs of {len(seq)}, every key and argv the registered, "
               f"{nrec} host records read as their commands' ({len(bad)} differ{': ' + '; '.join(bad[:3]) if bad else ''}); {dt:.0f} s")
    if t.want("E2"):
        # twice at once, each the first tie, pass 1's first 24 points and the second tie, a 6 s rest read (the reducer's rest window is the
        # registered 5 s), the doubles' leakage off; E2-A the watts at MM1-v1's forecast, E2-W 25% over
        procs = {}
        for tag, ws in (("A", "1"), ("W", "1.25")):
            d = os.path.join(S, f"E2-{tag}")
            if os.path.exists(d):
                shutil.rmtree(d)
            os.makedirs(d)
            e = {k: v for k, v in os.environ.items() if not k.startswith("E207_FAKE_")}
            e.update({"E207_FAKE_SCALE": "0.2", "E207_FAKE_TAU_S": "1", "E207_FAKE_LEAK": "0", "E207_FAKE_W_SCALE": ws})
            cmd = [sys.executable, "-B", RUNNER, "session", "--dry", "--arm", "A", "--t0", str(int(time.time())), "--out", os.path.join(d, "T"),
                   "--sequence", "e2e"] + FAST + ["--rest-s", "6"]
            procs[tag] = (subprocess.Popen(cmd, cwd=REPO, stdout=open(os.path.join(d, "runner.out"), "w"), stderr=subprocess.STDOUT, env=e),
                          os.path.join(d, "T"), float(ws))
        mm = C.mm1()
        for tag, (p, d, ws) in procs.items():
            rc = p.wait(timeout=3600)
            dj = os.path.join(S, f"E2-data-{tag}.json")
            r1 = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "reduce_e207.py"), "--arm", f"A={d}", "--out", dj],
                                capture_output=True, text=True)
            sj = os.path.join(S, f"E2-scored-{tag}.json")
            r2 = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "score_e207.py"), dj, "--out", sj], capture_output=True, text=True)
            data = json.load(open(dj)) if os.path.exists(dj) else {}
            sc = json.load(open(sj)) if os.path.exists(sj) else {}
            A = data.get("arms", {}).get("A", {})
            worst_t, worst_j, n, nj = 0.0, 0.0, 0, 0
            for pid, P in A.get("points", {}).items():
                for run in P["runs"]:
                    if not run.get("t_gemm_s"):
                        continue
                    n += 1
                    tg = mm[pid]["t"]
                    worst_t = max(worst_t, abs(run["t_gemm_s"] / tg - 1))
                    w_in = mm[pid]["W"] * ws
                    if run.get("p_work_w") is None or run.get("p_rest_w") is None:
                        worst_j = max(worst_j, 1.0)
                        continue
                    if w_in >= 3.0:          # the toy card's noise (0.05 W a sample) is under 2% of 3 W
                        nj += 1
                        jo = (run["p_work_w"] - run["p_rest_w"]) * run["t_gemm_s"]
                        worst_j = max(worst_j, abs(jo / (w_in * tg) - 1))
            rules = {k: v.get("verdict") for k, v in sc.get("rules", {}).items()}
            h2h = {k: v.get("verdict") for k, v in sc.get("head_to_head", {}).items()}
            if tag == "A":
                good = (rc == 0 and r1.returncode == 0 and r2.returncode == 0 and n == 24 and worst_t < 1e-4 and worst_j < 0.03
                        and all(rules.get(k) == "PASS" for k in ("R0", "T1", "T2", "T3", "E1", "E2", "E3", "E4", "S6"))
                        and h2h.get("H1") == "MM1-v1 BETTER" and h2h.get("H2") == "MM1-v1 BETTER")
            else:
                good = (rc == 0 and r1.returncode == 0 and r2.returncode == 0 and n == 24 and worst_t < 1e-4 and worst_j < 0.03
                        and all(rules.get(k) == "PASS" for k in ("R0", "T1", "T2", "T3", "S6")) and rules.get("E1") == "FAIL" and rules.get("E2") == "FAIL")
            t.case(f"E2-{tag}", good, f"session rc {rc}, reduce rc {r1.returncode}, score rc {r2.returncode}; {n} point runs; t_gemm worst {worst_t:.2e}; "
                   f"J over idle against the injected watts x seconds worst {worst_j:.2%} ({nj} runs of 3 W or more); rules {json.dumps(rules, sort_keys=True)}; "
                   f"head to head {json.dumps(h2h, sort_keys=True)}")
    if t.want("RF"):
        r = subprocess.run([sys.executable, "-B", RUNNER, "session", "--arm", "A", "--t0", "1", "--out", os.path.join(S, "RF1"), "--rest-s", "1"],
                           cwd=REPO, capture_output=True, text=True)
        e = dict(os.environ, V3_DRY="1")
        r2 = subprocess.run([sys.executable, "-B", RUNNER, "session", "--arm", "A", "--t0", "1", "--out", os.path.join(S, "RF2")],
                            cwd=REPO, capture_output=True, text=True, env=e)
        e = {k: v for k, v in os.environ.items() if k != "V3_DRY"}
        rb = subprocess.run([sys.executable, "-B", RUNNER, "session", "--dry", "--arm", "B", "--t0", "1", "--out", os.path.join(S, "RFB")],
                            cwd=REPO, capture_output=True, text=True, env=e)
        r3 = subprocess.run([sys.executable, "-B", RUNNER, "session", "--arm", "A", "--t0", str(int(time.time())), "--out", os.path.join(S, "RF3")],
                            cwd=REPO, capture_output=True, text=True, env=e)
        log3 = open(os.path.join(S, "RF3", "session.log")).read() if os.path.exists(os.path.join(S, "RF3", "session.log")) else ""
        t.case("RF", r.returncode == 2 and "read with --dry only" in r.stdout and r2.returncode == 2 and "V3_DRY" in r2.stdout
               and rb.returncode == 2 and "invalid choice: 'B'" in rb.stderr and not os.path.exists(os.path.join(S, "RFB"))
               and r3.returncode == 16 and "refused, no device opened: the box or the build is not the registered one (this host is" in log3
               and not os.path.exists(os.path.join(S, "RF3", "config-start.json")),
               f"rc {r.returncode}, {r2.returncode}, --arm B {rb.returncode}, {r3.returncode}; the real runner: "
               f"'{[x[24:150] for x in log3.splitlines() if 'refused' in x][:1]}'")
    print(f"SELFTEST-RUN-E207 {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
