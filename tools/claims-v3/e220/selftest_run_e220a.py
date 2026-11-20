#!/usr/bin/env python3
"""E220's runner desk test, ARM A (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): run_e220a.py on fake_card_e220a.py's doubles,
each case its own --dry session (a subprocess) in a scratch directory, E218's selftest_run_e218.py form (landed in 5582edfc) for E220 arm A on
aifoundry1 card 1 (E215 arm B's card cases from selftest_run_e215.py, landed in 8bde0182), its two families, its family smoke s03 in its place
and the G block last, end to end through the reducer and the FROZEN scorer (score_e220.py --a). No device, no box. Run it ONLY inside a sandbox
with no /dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2): case RF runs the real runner, which must stop at its box check. In --dry the
identity gate reads each process's ELF path (the family's kernel folder); the real gate on real ELFs is the real-path test's
(desk/realpath_e220a.py).

    /usr/bin/python3 -B tools/claims-v3/e220/selftest_run_e220a.py <scratch dir> [--only CASE ...] > logs/selftest-run-e220a.txt

Cases (the doubles' latch reads 66 C, as card 1's committed telemetry does; E220 arm A's lines 72 W x 3 / 80 C):
  G1  the short sequence (t01, xg09t, p02a): rc 0; the card's identity gate (/dev/et1_mgmt, ID 1, 499 mV); the identity read; THE OPENING SMOKE s01
      ('rgm136 gemmL', the session's gate), gated by its family, its counter's mean in R0's 200-4,000, THEN the stop-path test; three runs, each
      gated; the closing config; the manifest; the latch tripped nothing
  LN  THE G BLOCK (the lnc sequence: the third tie, the G smoke s03 in its place, the 26 G runs): s03 after its own 10 s rest (here 0.3 s), gated by
      its family ('rgm136 gemmLnc': rgm211's host, rgm136's ELF, the walk mn), good, at place 87, then the 26 runs, every G run after its smoke
  LN2 the lnc2 sequence (the third tie, s03, xg08 and n01): each G process on rgm211's host with rgm136's ELF, gated, the walk mn
  C1 the start config not as found (TDP 0 W): 16, the gate, no sampler, no host   C2 the config names card 0: 16   C2B card 1's block at 519 mV: 16
  C4 no identity block: 16
  C5 the config read fails: 16   C8 the threshold 70 C: 16   C9 the clock 800 MHz: 16   C6 the config read hangs past its TERM: HUNG (rc 8),
  nothing killed: the hung double ends by itself   C7 card 1's own runtime line on the config read: dropped, rc 0
  H1 another login on card 1: 16   H3 another login's line on card 0 at the start (the kit's start rule for aifoundry1): 16   H3C a line of ours on
  card 0 (never two of our sessions on aifoundry1): 16   H4 et-who unreadable: 16   H5 a device process of ours: 16   H6 a CI job: 16
  L1 the card's lock held: 16, no config read
  S1 the sampler would not start: 16   S2 the sampler holds card 0's node: 16   S3 the sampler goes silent in the runs: restarted, rc 0
  S4 the sampler dies in the runs: restarted, rc 0   P1 the stop-path test on a session with no live samples: it fails
  R1 a check of C wrong at s01: 16   R2 s01's host crashes: 16   R3 s01's host names and holds card 0: the watch trips, "stopping:", 16
  R4 the board does not rise in the smoke: 16   R5 the card's own runtime line INSIDE a smoke record: dropped, rc 0 (s01's and, in the lnc2
  sequence, s03's rgm211 form with its walk)   R6 s01's records name another shire mask: 16   R7 the counter's mean at 3 x the toy (2,400 cycles
  an op: inside R0's band, rc 0) and R7X at 6 x (4,800: outside R0's 200-4,000, the smoke gate fails, 16)
  K0 s01's host says "kernel did not finish": K1, 16    K1 the first run's host says it: the session stops, rc 0
  HG the first point's host IGNORES its timeout's TERM: HUNG (rc 8), nothing further, no closing config read, NOTHING KILLED
  TO an 'rgm136 gemmL' run's host ends on TERM (rc 124; xg09t): flagged, the session goes on (E206's rule), rc 0
  SA an 'rgm136 gemmL' run's records name another shire mask (xg09t): never read as data; the reducer passes the host's record on and the FROZEN
     scorer sets the run aside
  F2 two failed 'rgm136 gemmL' processes in a row (xg01t and xy04b, runs 004 and 005): the session stops, rc 0
  B1 the board above 72 W on 3 samples in a run: the stop   D1 the die at 80 C: the stop   D2 the latch rises past its session value to 81 C: the stop
  D3 the board at the line (72.0 W, not above) on every later sample: no stop   DG the die held above the gate: the later runs wait and are NO DATA
  CT the card-time rule (--rule-s 4.5, E218's: its opening smoke one process, as E220 arm A's): no run
     starts after it    OP an operator's SIGTERM to the runner mid-run: the stop file, rc 0
  CR the runner crashes mid-run (a copied tree whose order names a run the copied points file lacks): "CRASH: KeyError", the closing still runs, rc 1
  SF THE OPERATOR'S STOP FILE touched during run 002: run 003 never starts    SS THE OPERATOR'S STOP FILE during the opening smoke s01: the smoke
  gate fails naming the stop file    SSG the same during the G smoke s03 (the lnc sequence): the session stops, the family NOT dropped, no G run
  S0 a STOP file there when the runner starts: refused before any device
  DF a sampler that goes silent and IGNORES SIGTERM: the session stops, NEVER two processes on the stand-in management node at once, no closing
     config read while it lives, nothing killed
  RT card 0's runtime line on s01's host: the smoke gate fails; card 1's own passes    RT2 on the first run's host: STOP (identity)
  RTC card 0's line on the config read: 16    BN the board line in process: 95 W on every other sample with no reading between trips at the third
  THE IDENTITY GATE, THE WALK AND THE KERNEL STOPS (both families):
  GS THE IDENTITY GATE refuses s01: the smoke gate fails, s01's process never starts
  GRY THE IDENTITY GATE refuses run 002's process (xg09t, 'rgm136 gemmL'): STOP before it; through the reducer and the FROZEN scorer: R0 FAIL
  GR THE IDENTITY GATE refuses xg08's process ('rgm136 gemmLnc', the lnc2 sequence): STOP before it, nothing further; through the reducer and the
     frozen scorer: its gate words carried, the walk empty, R0 FAIL
  CW a check of C wrong in a G run (xg08): THE KERNEL STOPS    TE a tensor error in xg08: THE KERNEL STOPS    WR THE WALK CHECK fails on xg08: THE
  KERNEL STOPS (R0 FAIL through the frozen scorer)    TL xg08 ends on TERM (rc 124): THE KERNEL STOPS    WG an 'rgm136 gemmL' run's host crashes
  (xg09t): flagged, the session goes on, rc 0
  THE G SMOKE'S OWN STOP PATH (E220.md 3; E213's Amendment A1 form):
  LG3 THE IDENTITY GATE refuses s03 (the whole order at a tiny scale): the family 'rgm136 gemmLnc' DROPPED, its 26 runs never start, rc 0;
     through the reducer and the frozen scorer: R0 PASS, the drop flagged, xg01-xg12 and n01-n07 NO DATA, the other 65 points measured
  LW3 THE WALK CHECK fails at s03 (the lnc sequence): the same, its process ran    LC3 a check of C wrong at s03: the family dropped (both: the
     frozen scorer's R0 PASS on the tie that ran, s03's failure flagged, never counted in R0, while no gemmLnc point ran: E220.md 7)
  LK3 K1 at s03: the session stops (STOP), nothing further, nothing dropped, rc 0    LT3 s03 ends on its timeout's TERM (rc 124): the session
  stops (a failure that is the session's), nothing dropped
  LD3 the die held above the gate before s03: s03 never starts (NO DATA), and its family's runs do not start either (no family runs past a smoke
     that did not pass), rc 0
  OR THE ORDER: the whole registered order (112 runs and the G smoke) at a tiny scale: every run's key and argv the registered ones (the point's
     host and ELF by its loop, its host_args, --seconds 6 --budget 7.5, --kernel, --stop-file, under its sized plain timeout - 10 s, xf04 13 s -
     never -k), in order, every
     process gated (its words recorded), every host record read as its command's, every rgm211-host walk ok; the G smoke in its place with the
     smoke's argv (--seconds 2 --budget 3.5); the G block last
  E2 END TO END (the whole order; a 6 s rest read, the reducer's rest window being the registered 5 s; leakage off), through the reducer and the
     FROZEN scorer: E2-ok with the doubles' watts and seconds at MM1-v3.2's frozen forecasts: arm A's R0, S6, T1-T3 and E1-E4 PASS, H1-H10
     MM1-v3.2 BETTER, CX-T and CX-E SMALLER HERE (the scorer's own stand-in day 'v32'), every arm B rule NO DATA; E2-W with the watts 25% over:
     T1-T3 PASS, E1-E4 FAIL
  RF the refusals: the --dry options without --dry, V3_DRY without --dry, an unknown arm (argparse), --cap-s without --dry, and the REAL runner on
     this desk stopping at its box check
Every number here comes from the doubles (MM1-v3.2's frozen forecasts driven through a toy card): a desk check of code, not a measurement and not a
reading of E220. SPDX-License-Identifier: Apache-2.0
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
RUNNER = os.path.join(HERE, "run_e220a.py")
sys.path.insert(0, HERE)
import e220a_common as C  # noqa: E402

FAST = ["--rest-s", "0.3", "--smoke-rest-s", "1.5", "--tail-s", "0.2", "--gate-wait-s", "3"]
SHORT = ["001-tie-t01", "002-pass1-xg09t", "003-pass1-p02a"]
G_IDS = sorted([f"xg{i:02d}" for i in range(1, 13)] + [f"n{i:02d}" for i in range(1, 8)])
N_RUNS = C.registration()["plan"]["arms"]["A"]["n_runs"]      # 112 (ties and points)


class T:
    def __init__(self, scratch, only):
        self.S, self.only = scratch, set(only or [])
        self.n = self.ok = 0
        self.n_smoke = 7                 # the launches of the opening smoke's one process (the calibration, about five, the check: G1 measures it)

    def want(self, name):
        return not self.only or name in self.only

    def case(self, name, good, detail):
        self.n += 1
        self.ok += 1 if good else 0
        print(f"{name}: {'PASS' if good else 'FAIL'} - {detail}", flush=True)

    def session(self, name, env=None, seq="short", extra=None, scale="0.05", runner=None, signal_after=None, inject=None,
                touch_after=None, pre_stop=False, watch_mgmt=False):
        d = os.path.join(self.S, name)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
        e = {k: v for k, v in os.environ.items() if not k.startswith("E220A_FAKE_")}
        e.update({"E220A_FAKE_SCALE": scale, "E220A_FAKE_TAU_S": "1"})
        if inject is not None:
            ip = os.path.join(d, "inject.json")
            json.dump(inject, open(ip, "w"))
            e["E220A_FAKE_INJECT"] = ip
        e.update(env or {})
        out = os.path.join(d, "T")
        if pre_stop:
            os.makedirs(out)
            open(os.path.join(out, "STOP"), "a").close()
        cmd = [sys.executable, "-B", runner or RUNNER, "session", "--dry", "--arm", "A", "--t0", str(int(time.time())), "--out", out,
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


def reduce_and_score(S, tag, d):
    """The session through the reducer and the FROZEN scorer: (reduce rc, score rc, data, scored)."""
    dj, sd = os.path.join(S, f"{tag}-data.json"), os.path.join(S, f"{tag}-scored")
    r1 = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "reduce_e220a.py"), "--arm", f"A={d}", "--out", dj], capture_output=True, text=True)
    r2 = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "score_e220.py"), "--a", dj, "--a-tag", "A", "--out", sd], capture_output=True, text=True)
    data = json.load(open(dj)) if os.path.exists(dj) else {}
    sj = os.path.join(sd, "scores-e220.json")
    sc = json.load(open(sj)) if os.path.exists(sj) else {}
    return r1.returncode, r2.returncode, data, sc


def verdicts(sc):
    """the frozen scorer's verdicts for arm A ('A:<rule>' in score_e220's output, read here without the prefix)"""
    return {k[2:]: v for k, v in (sc.get("verdicts", {}) or {}).items() if k.startswith("A:")}


def verdicts_all(sc):
    return sc.get("verdicts", {}) or {}


def flags_of(sc):
    return ((sc.get("arms") or {}).get("A") or {}).get("flags", []) or []


def meas_of(sc):
    return ((sc.get("arms") or {}).get("A") or {}).get("measured", {}) or {}


def lnc_keys():
    """the lnc sequence's keys: the third tie, the G smoke, the G block"""
    seq = C.sequence("A")
    ti = [i for i, r in enumerate(seq) if r["block"] == "tie"][-1]
    return [C.run_key(r) for r in seq[ti:]]


def smoke_json(d, pid):
    p = os.path.join(d, "smoke", pid, "smoke.json")
    return json.load(open(p)) if os.path.exists(p) else {}


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
    print(f"selftest_run_e220a ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; /dev/et*: none; "
          f"/run/lock entries: {len(os.listdir('/run/lock')) if os.path.isdir('/run/lock') else 'none'}", flush=True)
    LK = lnc_keys()                     # 28: the third tie (086), s03 (087), the 26 G runs (088-113)

    if t.want("G1"):
        rc, log, d, dt = t.session("G1")
        ls = log.splitlines()
        i_sm = max([i for i, x in enumerate(ls) if "smoke s01: the identity gate GATE OK; rc" in x] or [-1])
        i_sp = min([i for i, x in enumerate(ls) if "stop-path test passed" in x] or [10 ** 6])
        sm = smoke_json(d, "s01")
        t.n_smoke = sm.get("n_launch", 0) or t.n_smoke
        idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
        procs = [run_json(d, k).get("procs", [{}])[0] for k in SHORT]
        gates = [str(sm.get("gate", ""))[:7]] + [str(p.get("gate", ""))[:7] for p in procs]
        t.case("G1", rc == 0 and "the card's identity: PCIe target /dev/et1_mgmt, physical device ID 1" in log and "the identity read: " in log
               and sm.get("good") is True and sm.get("cycles_in_band") and sm.get("family") == "rgm136 gemmL" and sm.get("walk", None) == {}
               and gates == ["GATE OK"] * 4 and 0 <= i_sm < i_sp < 10 ** 6 and runs_ran(d) == 3 and "config end: {" in log
               and os.path.exists(os.path.join(d, "MANIFEST.sha256")) and "STOP" not in log
               and idn.get("config_start", {}).get("minion_mv") == 499 and [x["run"] for x in q_of(d).get("queue", [])] == SHORT
               and not os.path.isdir(os.path.join(d, "smoke", "s03")),
               f"rc {rc}; the smoke s01 good {sm.get('good')} (family {sm.get('family')}, counter mean {sm.get('counted_cycles_per_op')} in R0's band) then "
               f"the stop-path test (lines {i_sm} < {i_sp}); {runs_ran(d)} runs; gates {gates}; {t.n_smoke} smoke launches; the latch tripped nothing "
               f"({'STOP' not in log}); {dt:.0f} s")
    for name, seq in (("LN", "lnc"), ("LN2", "lnc2")):
        if t.want(name):
            rc, log, d, dt = t.session(name, seq=seq)
            keys = LK if seq == "lnc" else LK[:4]
            lj = smoke_json(d, "s03")
            lines = log.splitlines()
            i_s = min([i for i, x in enumerate(lines) if "smoke s03: rc 0" in x] or [10 ** 6])
            i_r = min([i for i, x in enumerate(lines) if "-G-pass1-" in x and " done: " in x] or [-1])
            gk = [k for k in keys if "-G-pass" in k]
            pr = [(run_json(d, k).get("procs") or [{}])[0] for k in gk]
            hk = [os.path.basename(os.path.dirname(os.path.dirname(p.get("argv", ["/x/y/z"])[0]))) for p in pr]
            kk = [os.path.basename(os.path.dirname(os.path.dirname(C.arg_of(p.get("argv"), "--kernel") or "/x/y/z"))) for p in pr]
            good_p = all(h == "rgm211" and k == "rgm136" and p.get("walk", {}).get("want") == "mn" and p.get("walk_ok")
                         and str(p.get("gate", "")).startswith("GATE OK") and p.get("family") == "rgm136 gemmLnc" for h, k, p in zip(hk, kk, pr))
            t.case(name, rc == 0 and [x["run"] for x in q_of(d).get("queue", [])] == keys and runs_ran(d) == len(keys) and lj.get("good") is True
                   and lj.get("sequence_n") == 87 and lj.get("sequence_block") == "G-smoke" and lj.get("family") == "rgm136 gemmLnc"
                   and lj.get("walk", {}).get("want") == "mn" and lj.get("walk_ok") is True and C.arg_of(lj.get("argv"), "--seconds") == "2"
                   and "/rgm136/" in str(C.arg_of(lj.get("argv"), "--kernel")) and "/rgm211/" in str(lj.get("argv", ["x"])[0])
                   and lj.get("board_rise", {}).get("rest_is", "").startswith("this smoke's own") and lj.get("rest", {}).get("samples", 0) > 0
                   and i_s < i_r and len(gk) == (26 if seq == "lnc" else 2) and good_p and "STOP" not in log,
                   f"rc {rc}; s03 good {lj.get('good')} at place {lj.get('sequence_n')}, its own rest {lj.get('rest', {}).get('board_w_median_last5s')} W "
                   f"({lj.get('rest', {}).get('samples')} samples); then {len(gk)} G runs, each on {sorted(set(hk))}'s host with {sorted(set(kk))}'s ELF, "
                   f"walk mn, GATE OK: {good_p}; {dt:.0f} s")
    for name, mode, want in (("C1", "tdp0", "the gate, no launch"), ("C2", "card1", "/dev/et0_mgmt, not /dev/et1_mgmt"),
                             ("C2B", "mv519", "minion_mv 519, not below 510"),
                             ("C4", "noident", "no 'PCIe target' line"), ("C5", "fail", "config read rc 1"),
                             ("C8", "thr70", '"temp_threshold_c": 70'), ("C9", "mhz800", '"minion_mhz": 800')):
        if t.want(name):
            rc, log, d, dt = t.session(name, {"E220A_FAKE_CONFIG": mode})
            t.case(name, rc == 16 and want in log and "the gate, no launch" in log and "sampler started" not in log and not has_proc(d),
                   f"rc {rc}; '{line_of(log, 'config start')}'")
    if t.want("C6"):
        rc, log, d, dt = t.session("C6", {"E220A_FAKE_CONFIG": "hang", "E220A_FAKE_HANG_S": "16"})
        mk = wait_marker(os.path.join(d, "fake_sched.jsonl.config-hang-ended"), 30)
        t.case("C6", rc == 8 and " HUNG: " in log and "sampler started" not in log and "config end: not read" in log and "ended by itself" in mk
               and q_of(d).get("hung"), f"rc {rc}; the HUNG line {' HUNG: ' in log}; the hung double: '{mk[:90]}'")
    if t.want("C7"):
        rc, log, d, dt = t.session("C7", {"E220A_FAKE_CONFIG": "runtime"})
        idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
        t.case("C7", rc == 0 and runs_ran(d) == 3 and idn.get("config_start", {}).get("runtime_cards") == ["1"],
               f"rc {rc}; the config read whole past card 1's own runtime line ({idn.get('config_start', {}).get('runtime_cards')})")
    for name, env, want in (("H1", {"E220A_FAKE_ETWHO": "other"}, "holder line(s) of another login on card 1"),
                            ("H3", {"E220A_FAKE_ETWHO": "other1"}, "another login on card 0 (the kit's start rule for aifoundry1)"),
                            ("H3C", {"E220A_FAKE_ETWHO": "ours1"}, "holder line(s) of ours on card 0"),
                            ("H4", {"E220A_FAKE_ETWHO": "fail"}, "et-who unreadable (rc 1)"),
                            ("H5", {"E220A_FAKE_PS": "ours"}, "other device process(es) of ours"),
                            ("H6", {"E220A_FAKE_PS": "ci"}, "CI job")):
        if t.want(name):
            rc, log, d, dt = t.session(name, env)
            t.case(name, rc == 16 and "refused, no device opened: a holder or a device process" in log and want in log
                   and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}; '{line_of(log, 'refused')}'")
    if t.want("L1"):
        d0 = os.path.join(S, "L1", "T")
        os.makedirs(d0, exist_ok=True)
        lk = os.path.join(d0, "dry.lock")
        open(lk, "a").close()
        holder = subprocess.Popen(["flock", "-o", lk, "sleep", "20"], stdin=subprocess.DEVNULL)
        time.sleep(0.5)
        e = {k: v for k, v in os.environ.items() if not k.startswith("E220A_FAKE_")}
        r = subprocess.run([sys.executable, "-B", RUNNER, "session", "--dry", "--arm", "A", "--t0", str(int(time.time())), "--out", d0] + FAST,
                           cwd=REPO, capture_output=True, text=True, env=e)
        holder.terminate()          # the stand-in holder (a sleep under flock, no device), by SIGTERM
        holder.wait()
        log = open(os.path.join(d0, "session.log")).read()
        t.case("L1", r.returncode == 16 and "refused, no device opened: the card's lock is held" in log and not os.path.exists(os.path.join(d0, "config-start.json")),
               f"rc {r.returncode}")
    if t.want("S1"):
        rc, log, d, dt = t.session("S1", {"E220A_FAKE_SAMPLER": "dead"})
        t.case("S1", rc == 16 and "the sampler would not start" in log and not has_proc(d), f"rc {rc}")
    if t.want("S2"):
        rc, log, d, dt = t.session("S2", {"E220A_FAKE_SAMPLER": "card1"})
        t.case("S2", rc == 16 and "the identity read (the sampler running, before the smoke)" in log and "the gate, no launch" in log and not has_proc(d),
               f"rc {rc}; '{line_of(log, 'identity read')}'")
    if t.want("S3"):
        rc, log, d, dt = t.session("S3", {"E220A_FAKE_SAMPLER": f"hangs:{t.n_smoke + 3}"})
        t.case("S3", rc == 0 and "the sampler is not live" in log and log.count("sampler started") >= 2 and runs_ran(d) >= 2,
               f"rc {rc}; sampler starts {log.count('sampler started')}; runs {runs_ran(d)}")
    if t.want("S4"):
        rc, log, d, dt = t.session("S4", {"E220A_FAKE_SAMPLER": f"dies:{t.n_smoke + 3}"})
        t.case("S4", rc == 0 and log.count("sampler started") >= 2 and runs_ran(d) >= 2, f"rc {rc}; sampler starts {log.count('sampler started')}; runs {runs_ran(d)}")
    if t.want("P1"):
        import run_e220a as R
        d = os.path.join(S, "P1")
        os.makedirs(d, exist_ok=True)
        ns = argparse.Namespace(what="session", arm="A", t0=int(time.time()), out=os.path.join(d, "T"), deadline_epoch=0, dry=True,
                                sequence="short", rest_s=0.3, smoke_rest_s=1.5, tail_s=0.2, gate_wait_s=3, rule_s=C.ARMS["A"]["rule_s"], cap_s=C.ARMS["A"]["cap_s"])
        s = R.Session(ns)
        s.t_first = time.time()
        ok, res = s.stop_path_test()
        t.case("P1", not ok and not res["board"]["tripped"] and not res["die"]["tripped"], f"ok {ok}; {json.dumps({k: v['tripped'] for k, v in res.items()})}")
    for name, env, want in (("R1", {"E220A_FAKE_HOST": "wrong"}, "check wrong"), ("R2", {"E220A_FAKE_HOST": "crash"}, "rc 134"),
                            ("R4", {"E220A_FAKE_HOST": "norise"}, "the board's rise"), ("R6", {"E220A_FAKE_HOST": "mismatch"}, "the counter's mean None")):
        if t.want(name):
            rc, log, d, dt = t.session(name, env)
            t.case(name, rc == 16 and "smoke gate failed" in log and runs_ran(d) == 0 and want in log and "stop-path test" not in log,
                   f"rc {rc}; '{line_of(log, 'smoke gate failed')}'")
    if t.want("R7"):
        rc, log, d, dt = t.session("R7", {"E220A_FAKE_HOST": "cyc3x"})
        t.case("R7", rc == 0 and "smoke gate passed" in log and "(R0's band 200-4000: in;" in log,
               f"the counter's mean at 3 x the toy 800 (2,400 cycles an op, inside R0's 200-4,000): rc {rc}, '{line_of(log, 'smoke s01: the identity gate GATE OK')}'")
    if t.want("R7X"):
        rc, log, d, dt = t.session("R7X", {"E220A_FAKE_HOST": "cyc6x"})
        t.case("R7X", rc == 16 and "smoke gate failed" in log and "OUT" in log and runs_ran(d) == 0,
               f"the counter's mean at 6 x the toy (4,800, outside R0's 200-4,000): rc {rc}; '{line_of(log, 'smoke gate failed')}'")
    if t.want("R3"):
        rc, log, d, dt = t.session("R3", {"E220A_FAKE_HOST": "card1"})
        err = open(os.path.join(d, "smoke", "s01", "proc.err")).read() if os.path.exists(os.path.join(d, "smoke", "s01", "proc.err")) else ""
        t.case("R3", rc == 16 and os.path.exists(os.path.join(d, "STOP")) and "stopping:" in err and "smoke gate failed" in log and runs_ran(d) == 0,
               f"rc {rc}; the host stopped by the file {'stopping:' in err}")
    if t.want("R5"):
        rc, log, d, dt = t.session("R5", {"E220A_FAKE_HOST": "runtime"})
        sm = smoke_json(d, "s01")
        rc2, log2, d2, dt2 = t.session("R5-G", {"E220A_FAKE_HOST": "runtime", "E220A_FAKE_HOST_POINTS": "s03"}, seq="lnc2")
        sm3 = smoke_json(d2, "s03")
        t.case("R5", rc == 0 and sm.get("records", {}).get("runtime_lines") == 2 and sm.get("records", {}).get("unparsed") == 0 and "smoke gate passed" in log
               and rc2 == 0 and sm3.get("records", {}).get("runtime_lines") == 2 and sm3.get("walk_ok") is True and sm3.get("good") is True and runs_ran(d2) == 4,
               f"rc {rc}, {rc2}; s01's records {sm.get('records')}; s03's (rgm211's form, its walk read) {sm3.get('records')}, walk ok {sm3.get('walk_ok')}")
    if t.want("K0"):
        rc, log, d, dt = t.session("K0", {"E220A_FAKE_HOST": "k1"})
        t.case("K0", rc == 16 and "K1: a launch of the smoke's s01 did not finish" in log and "smoke gate failed" in log and runs_ran(d) == 0,
               f"rc {rc}; the K1 line {'K1: a launch of the smoke' in log}")
    if t.want("K1"):
        rc, log, d, dt = t.session("K1", {"E220A_FAKE_HOST": "k1", "E220A_FAKE_HOST_POINTS": "t01"})
        t.case("K1", rc == 0 and "K1: a launch of run 001-tie-t01 did not finish" in log and runs_ran(d) == 1 and "nothing further started" in log,
               f"rc {rc}; runs {runs_ran(d)}; '{line_of(log, 'STOP:')}'")
    if t.want("HG"):
        t0 = time.time()
        rc, log, d, dt = t.session("HG", {"E220A_FAKE_HOST": "hang_term", "E220A_FAKE_HANG_S": "14", "E220A_FAKE_HOST_POINTS": "xg09t"})
        mk = wait_marker(os.path.join(d, "fake_sched.jsonl.hang-ended"), 30)
        rj = run_json(d, SHORT[1])
        t.case("HG", rc == 8 and f" HUNG: a device process (the host of {SHORT[1]}" in log and "config end: not read (a device process of ours is HUNG" in log
               and os.path.exists(os.path.join(d, "STOP")) and runs_ran(d) == 2 and [p.get("hung") for p in rj.get("procs", [])] == [True]
               and "ended by itself" in mk and "nothing killed it" in mk, f"rc {rc}; the run's process hung {[p.get('hung') for p in rj.get('procs', [])]}; "
               f"the hung double: '{mk[:100]}' ({time.time() - t0:.0f} s after the session began)")
    if t.want("SA"):
        rc, log, d, dt = t.session("SA", {"E220A_FAKE_HOST": "mismatch", "E220A_FAKE_HOST_POINTS": "xg09t"})
        r1, r2, data, sc = reduce_and_score(S, "SA", d)
        runs = data.get("arms", {}).get("A", {}).get("points", {}).get("xg09t", {}).get("runs", [])
        flags = flags_of(sc)
        shown = "0x%x" % (int(C.point("xg09t")["shire_mask"], 16) << 1)
        t.case("SA", rc == 0 and r1 == 0 and r2 == 0 and len(runs) == 1 and runs[0].get("t_gemm_s") is None and (runs[0].get("record") or {}).get("shire_mask") == shown
               and any("xg09t" in f and "SET ASIDE" in f for f in flags) and runs_ran(d) == 3,
               f"rc {rc}; xg09t's run: t_gemm {runs[0].get('t_gemm_s') if runs else None}, the host's record {(runs[0].get('record') if runs else None)}; "
               f"the scorer's flags {[f for f in flags if 'xg09t' in f][:2]}")
    if t.want("TO"):
        rc, log, d, dt = t.session("TO", {"E220A_FAKE_HOST": "hang", "E220A_FAKE_HOST_POINTS": "xg09t"})
        rj = run_json(d, "002-pass1-xg09t")
        t.case("TO", rc == 0 and [p.get("rc") for p in rj.get("procs", [])] == [124] and runs_ran(d) == 3 and " HUNG" not in log and "STOP" not in log,
               f"rc {rc}; xg09t's process rc {[p.get('rc') for p in rj.get('procs', [])]}; runs {runs_ran(d)}")
    if t.want("F2"):
        rc, log, d, dt = t.session("F2", {"E220A_FAKE_HOST": "crash", "E220A_FAKE_HOST_POINTS": "xg01t,xy04b"}, seq="plan", scale="0.02",
                                   extra=["--rest-s", "0.15", "--tail-s", "0.1"])
        t.case("F2", rc == 0 and "STOP: two failed processes in a row (the last in run 005-pass1-xy04b)" in log and runs_ran(d) == 5,
               f"rc {rc}; runs {runs_ran(d)}; '{line_of(log, 'STOP:')}'")
    for name, inj, want in (("B1", [{"board_w": 73.0, "after_launches": t.n_smoke + 2, "count": 3}], "board 73.0 W above 72 W on 3 samples"),
                            ("D1", [{"die": 80, "after_launches": t.n_smoke + 2, "count": 1}], "die 80 C (the shires' mean) at or above 80 C"),
                            ("D2", [{"high": 81, "after_launches": t.n_smoke + 2, "count": 1}], "latch rose to 81 C (from 66 C")):
        if t.want(name):
            rc, log, d, dt = t.session(name, inject=inj, scale="0.2")
            err = open(os.path.join(d, "runs", SHORT[0], "proc-00.err")).read() if os.path.exists(os.path.join(d, "runs", SHORT[0], "proc-00.err")) else ""
            t.case(name, rc == 0 and want in log and "nothing further started" in log and runs_ran(d) == 1 and "stopping:" in err,
                   f"rc {rc}; '{line_of(log, 'STOP:')}'; the host ended by the stop file {'stopping:' in err}")
    if t.want("D3"):
        rc, log, d, dt = t.session("D3", inject=[{"board_w": 72.0, "after_launches": t.n_smoke + 1}])
        t.case("D3", rc == 0 and "STOP" not in log and runs_ran(d) == 3, f"rc {rc}; the board at the line (not above it) on every later sample: no stop ({'STOP' not in log}); runs {runs_ran(d)}")
    if t.want("DG"):
        rc, log, d, dt = t.session("DG", inject=[{"die": 61, "after_launches": t.n_smoke + 2}])
        q = q_of(d).get("queue", [])
        t.case("DG", rc == 0 and runs_ran(d) == 1 and sum(1 for x in q if not x.get("ran") and "the die gate" in str(x.get("why"))) == 2,
               f"rc {rc}; {[(x['run'], x.get('ran'), str(x.get('why'))[:60]) for x in q]}")
    if t.want("CT"):
        rc, log, d, dt = t.session("CT", seq="short", extra=["--rule-s", "4.5", "--rest-s", "2"])
        q = q_of(d).get("queue", [])
        first = next((i for i, x in enumerate(q) if not x.get("ran")), None)
        t.case("CT", rc == 0 and runs_ran(d) < 3 and first is not None and "the card-time rule" in str(q[first].get("why"))
               and all(not x.get("ran") for x in q[first:]), f"rc {rc}; {[(x['run'], x.get('ran'), str(x.get('why'))[:50]) for x in q]}")
    if t.want("OP"):
        rc, log, d, dt = t.session("OP", signal_after=("run 001-tie-t01: gemmL2x4x4", 0.5), scale="0.3")
        err = open(os.path.join(d, "runs", "001-tie-t01", "proc-00.err")).read() if os.path.exists(os.path.join(d, "runs", "001-tie-t01", "proc-00.err")) else ""
        t.case("OP", rc == 0 and "the operator's signal 15" in log and runs_ran(d) == 1 and "stopping:" in err and os.path.exists(os.path.join(d, "MANIFEST.sha256")),
               f"rc {rc}; runs {runs_ran(d)}; the host ended by the stop file {'stopping:' in err}")
    if t.want("CR"):
        tree = os.path.join(S, "CR-tree")
        if os.path.exists(tree):
            shutil.rmtree(tree)
        dst = os.path.join(tree, "tools", "claims-v3", "e220")
        os.makedirs(os.path.join(dst, "desk"))
        for f in ("run_e220a.py", "e220a_common.py", "e220a_ident.py", "fake_card_e220a.py", "points-e220.json", "kernel-e220.json", "ident_e220a.py",
                  "plan-e220.json", "forecast-e220.csv", "desk/timeouts-e220.json"):
            shutil.copy2(os.path.join(HERE, f), os.path.join(dst, f))
        os.makedirs(os.path.join(tree, "tools", "claims-v3", "e206"))
        for f in ("check_e206.py", "e206_common.py"):
            shutil.copy2(os.path.join(REPO, "tools", "claims-v3", "e206", f), os.path.join(tree, "tools", "claims-v3", "e206"))
        for f in ("kinds.json",):                                            # the tiles' manifest the common module reads
            os.makedirs(os.path.join(tree, "tools", "claims-v3", "kinds"), exist_ok=True)
            shutil.copy2(os.path.join(REPO, "tools", "claims-v3", "kinds", f), os.path.join(tree, "tools", "claims-v3", "kinds", f))
        pj = os.path.join(dst, "plan-e220.json")                            # the crash: the copy's order names, as its second run, no point
        P = json.load(open(pj))
        P["arms"]["A"]["runs"][2]["id"] = "x999"
        with open(pj, "w") as f:
            json.dump(P, f)
        rc, log, d, dt = t.session("CR", runner=os.path.join(dst, "run_e220a.py"))
        t.case("CR", rc == 1 and "CRASH: KeyError" in log and runs_ran(d) == 1 and os.path.exists(os.path.join(d, "queue.json"))
               and os.path.exists(os.path.join(d, "MANIFEST.sha256")) and os.path.exists(os.path.join(d, "crash.txt")) and "session end" in log
               and os.path.exists(os.path.join(d, "config-end.json")), f"rc {rc}; runs {runs_ran(d)}; '{line_of(log, 'CRASH')}'")
    if t.want("SF"):
        rc, log, d, dt = t.session("SF", touch_after=("run 002-", 0.4), scale="0.3")
        q = q_of(d)
        qq = q.get("queue", [])
        last = qq[-1] if qq else {}
        t.case("SF", rc == 0 and len(qq) == 3 and not last.get("ran") and "after a stop" in str(last.get("why"))
               and "the operator's STOP file" in str(q.get("stop")) and "STOP: the operator's STOP file" in log
               and os.path.exists(os.path.join(d, "MANIFEST.sha256")) and os.path.exists(os.path.join(d, "STOP")),
               f"rc {rc}; runs {[(x.get('run'), x.get('ran')) for x in qq]}; the stop {q.get('stop')!r}; {dt:.0f} s")
    if t.want("SS"):
        rc, log, d, dt = t.session("SS", touch_after=("smoke s01: the identity gate (", 0.25), scale="0.3")
        t.case("SS", rc == 16 and "smoke gate failed: a stop during the smoke's s01: the operator's STOP file" in log and runs_ran(d) == 0
               and os.path.exists(os.path.join(d, "STOP")) and "FAILED for its family alone" not in log and not q_of(d).get("families_dropped"),
               f"rc {rc}; '{line_of(log, 'smoke gate failed')}'")
    if t.want("SSG"):
        rc, log, d, dt = t.session("SSG", touch_after=("smoke s03: the identity gate (", 0.25), scale="0.3", seq="lnc2")
        q = q_of(d)
        qq = {x["run"]: x for x in q.get("queue", [])}
        t.case("SSG", rc == 0 and "the operator's STOP file" in str(q.get("stop")) and "FAILED for its family alone" not in log
               and not q.get("families_dropped") and all(qq.get(k, {}).get("ran") is False for k in LK[2:4])
               and not any(os.path.isdir(os.path.join(d, "runs", k)) for k in LK[2:4]) and qq.get(LK[0], {}).get("ran") is True,
               f"rc {rc}; the stop {str(q.get('stop'))[:90]!r}; {[(k[:22], qq.get(k, {}).get('ran')) for k in LK[:4]]}")
    if t.want("S0"):
        rc, log, d, dt = t.session("S0", pre_stop=True)
        t.case("S0", rc == 16 and "refused, no device opened: the operator's STOP file is already in the session's folder" in log
               and not os.path.exists(os.path.join(d, "config-start.json")) and "sampler started" not in log and not has_proc(d)
               and os.path.exists(os.path.join(d, "STOP")), f"rc {rc}; '{line_of(log, 'refused')}'")
    if t.want("DF"):
        rc, log, d, dt = t.session("DF", {"E220A_FAKE_SAMPLER": f"deaf:{t.n_smoke + 3}", "E220A_FAKE_DEAF_S": "110"}, scale="0.3", watch_mgmt=True)
        mk = wait_marker(os.path.join(d, "fake_sched.jsonl.sampler-deaf-ended"), 120)
        q = q_of(d)
        t.case("DF", rc == 0 and t.max_mgmt <= 1 and "the sampler would not stop on SIGTERM" in str(q.get("stop"))
               and "config end: not read (the sampler did not stop on SIGTERM" in log and log.count("sampler started") == 1
               and bool(q.get("samplers_left")) and "ended by itself" in mk and "nothing killed it" in mk,
               f"rc {rc}; most processes on the stand-in management node at once {t.max_mgmt}; samplers started {log.count('sampler started')}; "
               f"left {q.get('samplers_left')}; the stop {str(q.get('stop'))[:100]!r}; the deaf double: '{mk[:80]}'; {dt:.0f} s")
    if t.want("RT"):
        rc, log, d, dt = t.session("RT", {"E220A_FAKE_HOST": "runtime1"})
        rca, loga, da, dta = t.session("RT-0", {"E220A_FAKE_HOST": "runtime"})
        t.case("RT", rc == 16 and "smoke gate failed" in log and "ANOTHER by its runtime line: card(s) ['0']" in log
               and rca == 0 and runs_ran(da) == 3 and "STOP" not in loga,
               f"card 0's line: rc {rc}: '{line_of(log, 'smoke s01: the identity gate GATE OK')}'; card 1's line (its own) rc {rca}, runs {runs_ran(da)}")
    if t.want("RT2"):
        rc, log, d, dt = t.session("RT2", {"E220A_FAKE_HOST": "runtime1", "E220A_FAKE_HOST_POINTS": "t01"})
        q = q_of(d)
        t.case("RT2", rc == 0 and runs_ran(d) == 1 and "identity: the runtime named card(s) ['0']" in str(q.get("stop"))
               and "nothing further started" in log, f"rc {rc}; runs {runs_ran(d)}; the stop {str(q.get('stop'))[:120]!r}")
    if t.want("RTC"):
        rc, log, d, dt = t.session("RTC", {"E220A_FAKE_CONFIG": "runtime1"})
        t.case("RTC", rc == 16 and "its stdout's runtime line(s) name card(s) ['0']" in log and "the gate, no launch" in log
               and "sampler started" not in log and not has_proc(d), f"rc {rc}; '{line_of(log, 'config start')}'")
    if t.want("BN"):
        smp = [{"t_ms": k, "board_w": 95.0} if k % 2 else {"t_ms": k, "temp_c": {"minshire": [50, 46, 87]}} for k in range(1, 8)]
        sa = C.Stops(**C.stops_of("A"))
        ra = [sa.feed(s) for s in smp]
        t.case("BN", ra == [[], [], [], [], ["stop"], [], []] and "95.0 W above 72 W on 3 samples" in (sa.stop or ""),
               f"95 W on every other sample, no board reading between: {ra} {sa.stop!r}")
    # ---------------------------------------------------------------- the identity gate, the walk and the kernel stops (both families)
    if t.want("GS"):
        rc, log, d, dt = t.session("GS", {"E220A_FAKE_GATE": "fail:s01"})
        sj = smoke_json(d, "s01")
        t.case("GS", rc == 16 and "smoke gate failed: s01: the identity gate failed, no process started" in log and sj.get("ran") is False
               and not os.path.exists(os.path.join(d, "smoke", "s01", "proc.out")) and runs_ran(d) == 0, f"rc {rc}; '{line_of(log, 'smoke gate failed')}'")
    if t.want("GRY"):
        rc, log, d, dt = t.session("GRY", {"E220A_FAKE_GATE": "fail:xg09t"})
        r1, r2, data, sc = reduce_and_score(S, "GRY", d)
        rr = data.get("arms", {}).get("A", {}).get("points", {}).get("xg09t", {}).get("runs", [])
        v = verdicts(sc)
        t.case("GRY", rc == 0 and runs_ran(d) == 1 and "STOP before run 002-pass1-xg09t's process: the identity gate failed" in log
               and not os.path.exists(os.path.join(d, "runs", "002-pass1-xg09t", "proc-00.out")) and r1 == 0 and r2 == 0
               and len(rr) == 1 and rr[0].get("checks") == [] and str((rr[0].get("detail") or {}).get("gate_words", "")).startswith("GATE FAILED")
               and v.get("R0") == "FAIL", f"rc {rc}; runs {runs_ran(d)}; the refused run in the data: checks {rr[0].get('checks') if rr else None}; R0 {v.get('R0')}")
    if t.want("GR"):
        rc, log, d, dt = t.session("GR", {"E220A_FAKE_GATE": "fail:xg08"}, seq="lnc2")
        r1, r2, data, sc = reduce_and_score(S, "GR", d)
        rr = data.get("arms", {}).get("A", {}).get("points", {}).get("xg08", {}).get("runs", [])
        v = verdicts(sc)
        t.case("GR", rc == 0 and runs_ran(d) == 2 and f"STOP before run {LK[2]}'s process: the identity gate failed (GATE FAILED: (dry, by path) rgm136 gemmLnc needs rgm136's ELF" in log
               and "nothing further started" in log
               and not os.path.exists(os.path.join(d, "runs", LK[2], "proc-00.out")) and r1 == 0 and r2 == 0
               and len(rr) == 1 and str(rr[0].get("gate", "")).startswith("GATE FAILED") and rr[0].get("walk") == {"names": [], "ok": [], "launches_bad": None}
               and v.get("R0") == "FAIL", f"rc {rc}; runs {runs_ran(d)}; '{line_of(log, 'STOP before run')}'; the refused run: gate "
               f"{str(rr[0].get('gate'))[:50] if rr else None}; R0 {v.get('R0')}")
    for name, env, want in (("CW", {"E220A_FAKE_HOST": "wrong"}, "the check of C reads 'wrong'"), ("TE", {"E220A_FAKE_HOST": "tensor"}, "tensor error"),
                            ("WR", {"E220A_FAKE_HOST": "walkbad"}, "the walk check failed (walk_ok not true"), ("TL", {"E220A_FAKE_HOST": "hang"}, "rc 124: a launch timeout")):
        if t.want(name):
            rc, log, d, dt = t.session(name, dict(env, E220A_FAKE_HOST_POINTS="xg08"), seq="lnc2")
            extra_ok, extra = True, ""
            if name == "WR":
                r1, r2, data, sc = reduce_and_score(S, name, d)
                extra_ok = r1 == 0 and r2 == 0 and verdicts(sc).get("R0") == "FAIL"
                extra = f"; R0 {verdicts(sc).get('R0')} ({(((sc.get('arms') or {}).get('A') or {}).get('rules', {}).get('R0', {}).get('failures', []))[:1]})"
            t.case(name, rc == 0 and runs_ran(d) == 3 and f"STOP: the kernel stops in run {LK[2]} (rgm136 gemmLnc): " in log and want in log
                   and "nothing further started" in log and not os.path.isdir(os.path.join(d, "runs", LK[3])) and extra_ok,
                   f"rc {rc}; runs {runs_ran(d)}; '{line_of(log, 'STOP:')}'{extra}")
    if t.want("WG"):
        rc, log, d, dt = t.session("WG", {"E220A_FAKE_HOST": "crash", "E220A_FAKE_HOST_POINTS": "xg09t"})
        rj = run_json(d, "002-pass1-xg09t")
        t.case("WG", rc == 0 and runs_ran(d) == 3 and [p.get("rc") for p in rj.get("procs", [])] == [134] and "STOP" not in log
               and "the process rc 134" in str(rj.get("flags")), f"rc {rc}; runs {runs_ran(d)}; xg09t flags {rj.get('flags')}")
    # ---------------------------------------------------------------- the G smoke's own stop path (E220.md 3, E213's Amendment A1 form)
    for name, env, procran, sq in (("LG3", {"E220A_FAKE_GATE": "fail:s03"}, False, "plan"),
                                   ("LW3", {"E220A_FAKE_HOST": "walkbad", "E220A_FAKE_HOST_POINTS": "s03"}, True, "lnc"),
                                   ("LC3", {"E220A_FAKE_HOST": "wrong", "E220A_FAKE_HOST_POINTS": "s03"}, True, "lnc2")):
        if t.want(name):
            if sq == "plan":        # the whole order at a tiny scale: every other point runs, so the frozen scorer reads the drop beside them
                rc, log, d, dt = t.session(name, env, seq="plan", scale="0.02", extra=["--rest-s", "0.15", "--tail-s", "0.1"])
                keys = [C.run_key(r) for r in C.sequence("A")]
            else:
                rc, log, d, dt = t.session(name, env, seq=sq)
                keys = LK if sq == "lnc" else LK[:4]
            lj = smoke_json(d, "s03")
            q = q_of(d)
            skipped = [k for k in keys if "-G-pass" in k]
            qq = {x["run"]: x for x in q.get("queue", [])}
            r1, r2, data, sc = reduce_and_score(S, name, d)
            v = verdicts(sc)
            fl = flags_of(sc)
            proc = os.path.exists(os.path.join(d, "smoke", "s03", "proc.out"))
            sr = [r for r in data.get("arms", {}).get("A", {}).get("smoke", {}).get("runs", []) if r.get("point") == "s03"]
            t.case(name, rc == 0 and "smoke s03: FAILED for its family alone (its own stop path, E220.md 3)" in log
                   and f"the family 'rgm136 gemmLnc' is DROPPED - {', '.join(G_IDS)} never start" in log and "STOP" not in log
                   and lj.get("a1_family_dropped") == "rgm136 gemmLnc" and proc is procran
                   and all(qq.get(k, {}).get("ran") is False and "was dropped by its smoke" in qq.get(k, {}).get("why", "") for k in skipped)
                   and not any(os.path.isdir(os.path.join(d, "runs", k)) for k in skipped)
                   and runs_ran(d) == len(keys) - len(skipped) - (0 if procran else 1)
                   and sorted((q.get("families_dropped") or {}).get("rgm136 gemmLnc", {}).get("points", [])) == G_IDS
                   and r1 == 0 and r2 == 0 and len(sr) == 1 and sr[0].get("block") == "smoke" and sr[0].get("n") == 87
                   and v.get("R0") == "PASS" and any(x.startswith("the G block's smoke s03 failed") for x in fl)
                   and not any(m in meas_of(sc) for m in G_IDS) and len(meas_of(sc)) == (65 if sq == "plan" else 0),
                   f"rc {rc}; ({sq}) '{line_of(log, 'FAILED for its family alone')}'; {len(skipped)} G runs never started; {runs_ran(d)} entries ran; the smoke RUN n "
                   f"{sr[0].get('n') if sr else None} block {sr[0].get('block') if sr else None}; R0 {v.get('R0')} ({[x[:80] for x in fl if x.startswith('the G block')][:1]}); "
                   f"measured {len(meas_of(sc))}")
    for name, env, want in (("LK3", {"E220A_FAKE_HOST": "k1", "E220A_FAKE_HOST_POINTS": "s03"}, "K1: a launch of the gemmLnc smoke s03 did not finish"),
                            ("LT3", {"E220A_FAKE_HOST": "hang", "E220A_FAKE_HOST_POINTS": "s03"}, "a launch timeout (rc 124")):
        if t.want(name):
            rc, log, d, dt = t.session(name, env, seq="lnc2")
            lj = smoke_json(d, "s03")
            q = q_of(d)
            t.case(name, rc == 0 and "nothing further started" in log and lj.get("a1_family_dropped") is None and want in str(lj.get("a1_session_level")) + log
                   and not q.get("families_dropped") and "FAILED for its family alone" not in log and runs_ran(d) == 2
                   and not any(os.path.isdir(os.path.join(d, "runs", k)) for k in LK[2:4]),
                   f"rc {rc}; '{line_of(log, 'STOP:')}'; s03's session-level reading {lj.get('a1_session_level')!r}; runs {runs_ran(d)}")
    if t.want("LD3"):
        rc, log, d, dt = t.session("LD3", seq="lnc", inject=[{"die": 61, "after_launches": t.n_smoke + 2}])
        q = q_of(d)
        qq = {x["run"]: x for x in q.get("queue", [])}
        t.case("LD3", rc == 0 and qq.get(LK[1], {}).get("ran") is False and "the die gate" in str(qq.get(LK[1], {}).get("why"))
               and "its smoke did not start (the die gate" in log and not os.path.exists(os.path.join(d, "smoke", "s03", "smoke.json"))
               and all(qq.get(k, {}).get("ran") is False for k in LK[2:]) and runs_ran(d) == 1
               and "rgm136 gemmLnc" in (q.get("families_dropped") or {}),
               f"rc {rc}; {[(x['run'][:24], x.get('ran'), str(x.get('why'))[:50]) for x in q.get('queue', [])][:3]}")
    if t.want("OR"):
        rc, log, d, dt = t.session("OR", seq="plan", scale="0.02", extra=["--rest-s", "0.15", "--tail-s", "0.1"])
        seq = C.sequence("A")
        q = q_of(d).get("queue", [])
        bad, nrec = [], 0
        for r, x in zip(seq, q):
            if x.get("run") != C.run_key(r) or not x.get("ran"):
                bad.append(f"{C.run_key(r)}: {x.get('run')} ran {x.get('ran')}")
                continue
            if C.is_lnc_smoke(r):
                sj = smoke_json(d, r["id"])
                if not sj.get("good") or sj.get("argv") != C.host_argv(C.REPO, r["id"], C.SMOKE_SECONDS, C.SMOKE_BUDGET, os.path.join(d, "STOP")) \
                        or sj.get("sequence_n") != r["n"]:
                    bad.append(f"{C.run_key(r)}: the G smoke good {sj.get('good')}, place {sj.get('sequence_n')}")
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
        nreg = N_RUNS
        last_g = [x["run"] for x in q][-26:]
        to13 = [x["run"] for x in q if x.get("ran") and (run_json(d, x["run"]).get("procs") or [{}])[0].get("timeout_s") == 13]
        t.case("OR", rc == 0 and len(q) == len(seq) == nreg + 1 and not bad and all("-G-pass" in k for k in last_g)
               and [x["run"] for x in q][-27] == "087-G-smoke-s03" and to13 == [x["run"] for x in q if x["run"].endswith("-xf04")],
               f"rc {rc}; {len(q)} entries of {len(seq)} (the plan's {nreg} runs and the G smoke), every key, argv (host and ELF by loop) and gate the "
               f"registered, {nrec} host records read as their commands' ({len(bad)} differ{': ' + '; '.join(bad[:3]) if bad else ''}); the G block last; "
               f"the 13 s timeout on {to13}; {dt:.0f} s")
    if t.want("E2"):
        procs = {}
        for tag, ws in (("ok", "1"), ("W", "1.25")):
            d = os.path.join(S, f"E2-{tag}")
            if os.path.exists(d):
                shutil.rmtree(d)
            os.makedirs(d)
            e = {k: v for k, v in os.environ.items() if not k.startswith("E220A_FAKE_")}
            e.update({"E220A_FAKE_SCALE": "0.2", "E220A_FAKE_TAU_S": "1", "E220A_FAKE_LEAK": "0", "E220A_FAKE_W_SCALE": ws})
            cmd = [sys.executable, "-B", RUNNER, "session", "--dry", "--arm", "A", "--t0", str(int(time.time())), "--out", os.path.join(d, "T"),
                   "--sequence", "e2e"] + FAST + ["--rest-s", "6"]
            procs[tag] = (subprocess.Popen(cmd, cwd=REPO, stdout=open(os.path.join(d, "runner.out"), "w"), stderr=subprocess.STDOUT, env=e),
                          os.path.join(d, "T"), float(ws))
        rcs = {k: p.wait(timeout=5400) for k, (p, d, ws) in procs.items()}
        for tag in ("ok", "W"):
            d, ws = procs[tag][1], procs[tag][2]
            r1, r2, data, sc = reduce_and_score(S, f"E2-{tag}", d)
            Ad = data.get("arms", {}).get("A", {})
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
            v = verdicts(sc)
            nP = N_RUNS - 3
            base = rcs[tag] == 0 and r1 == 0 and r2 == 0 and n == nP and worst_t < 1e-4 and worst_j < 0.03
            va = verdicts_all(sc)
            nob = all(x == "NO DATA" for k, x in va.items() if k.startswith("B:"))
            if tag == "ok":
                want_better = [h for h in v if h.startswith("H")]
                good = base and nob and all(v.get(k) == "PASS" for k in ("R0", "S6", "T1", "T2", "T3", "E1", "E2", "E3", "E4")) \
                    and all(v.get(k) == "MM1-v3.2 BETTER" for k in want_better) and len(want_better) == 10 \
                    and v.get("CX-T") == "SMALLER HERE" and v.get("CX-E") == "SMALLER HERE"
            else:
                good = base and nob and all(v.get(k) == "PASS" for k in ("R0", "S6", "T1", "T2", "T3")) and all(v.get(k) == "FAIL" for k in ("E1", "E2", "E3", "E4"))
            t.case(f"E2-{tag}", good, f"session rc {rcs[tag]}, reduce rc {r1}, score rc {r2}; runs (points) {n} of {nP}; t_gemm worst {worst_t:.2e}; J over idle "
                   f"against the injected watts x seconds worst {worst_j:.2%} ({nj} runs of 3 W or more); verdicts {json.dumps(v, sort_keys=True)}")
    if t.want("RF"):
        r = subprocess.run([sys.executable, "-B", RUNNER, "session", "--arm", "A", "--t0", "1", "--out", os.path.join(S, "RF1"), "--rest-s", "1"],
                           cwd=REPO, capture_output=True, text=True)
        e = dict(os.environ, V3_DRY="1")
        r2 = subprocess.run([sys.executable, "-B", RUNNER, "session", "--arm", "A", "--t0", "1", "--out", os.path.join(S, "RF2")],
                            cwd=REPO, capture_output=True, text=True, env=e)
        e = {k: v for k, v in os.environ.items() if k != "V3_DRY"}
        rc_ = subprocess.run([sys.executable, "-B", RUNNER, "session", "--dry", "--arm", "B", "--t0", "1", "--out", os.path.join(S, "RFB")],
                             cwd=REPO, capture_output=True, text=True, env=e)
        r3 = subprocess.run([sys.executable, "-B", RUNNER, "session", "--arm", "A", "--t0", str(int(time.time())), "--out", os.path.join(S, "RF3")],
                            cwd=REPO, capture_output=True, text=True, env=e)
        log3 = open(os.path.join(S, "RF3", "session.log")).read() if os.path.exists(os.path.join(S, "RF3", "session.log")) else ""
        r5 = subprocess.run([sys.executable, "-B", RUNNER, "session", "--arm", "A", "--t0", "1", "--out", os.path.join(S, "RF5"), "--cap-s", "100"],
                            cwd=REPO, capture_output=True, text=True, env=e)
        r6 = subprocess.run([sys.executable, "-B", RUNNER, "session", "--arm", "A", "--t0", "1", "--out", os.path.join(S, "RF6"), "--sequence", "lnc"],
                            cwd=REPO, capture_output=True, text=True, env=e)
        t.case("RF", r.returncode == 2 and "read with --dry only" in r.stdout and r2.returncode == 2 and "V3_DRY" in r2.stdout
               and rc_.returncode == 2 and "invalid choice: 'B'" in rc_.stderr and not os.path.exists(os.path.join(S, "RFB"))
               and r3.returncode == 16 and "refused, no device opened: the box or the build is not the registered one (this host is" in log3
               and r5.returncode == 2 and "--cap-s" in r5.stdout and r6.returncode == 2 and "--sequence" in r6.stdout
               and not os.path.exists(os.path.join(S, "RF3", "config-start.json")),
               f"rc {r.returncode}, {r2.returncode}, --arm B {rc_.returncode}, the real runner {r3.returncode} ('{line_of(log3, 'refused')}'), "
               f"--cap-s without --dry {r5.returncode}, --sequence without --dry {r6.returncode}")
    print(f"SELFTEST-RUN-E220A {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
