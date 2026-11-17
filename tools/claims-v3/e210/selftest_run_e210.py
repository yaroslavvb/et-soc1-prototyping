#!/usr/bin/env python3
"""E210's runner desk test (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum; ported from kit-e207's E207 kit, its local commit
4bd6e38c): run_e210.py on fake_card_e210.py's doubles, each case its own --dry session (a subprocess) in a scratch directory, E206's
selftest_run_e206.py form (landed in 906699ea; E190's before it) for E210's one arm. No device, no box. Run it ONLY inside a sandbox with no
/dev/et* and an empty /run/lock (W/nodev.sh on aifoundry2): case RF runs the real runner, which must stop at its box check before anything else.

    /usr/bin/python3 -B tools/claims-v3/e210/selftest_run_e210.py <scratch dir> [--only CASE ...] > logs/selftest-run-e210.txt

Cases (the doubles' latch reads 87 C, as aifoundry3 card 0's committed telemetry does):
  G1 the short sequence (the warm-up tie 001, then 004 sparse50@S1 and 007 bhalfeq@S1, a pattern of 61 tile files): rc 0; the identity gate
     (/dev/et0_mgmt, ID 0); the identity read; the opening's rest; the smoke's three processes (random@S1, zeros@S1, random@S2; each at E206's
     cycles an op at the shape); THE PROBE (maxalte@S2: IN under the doubles' R1 watts) THEN the stop-path test; three runs; the closing config;
     the manifest; the 87 C latch tripped nothing; every host read its tile files from the box tree's root (the double reads them as fillPools)
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
  R7 a smoke host's counter mean at 3 x the shape's: the smoke's ratio outside 50-250% of E206's, the smoke gate fails, 16
  R8 THE OPERATOR'S STOP FILE touched during the first smoke process: the smoke gate fails and its words name the STOP file (verify-e207's V4)
  R9 a tile file missing from the box tree: the host double, like rgm136 after its device opened, fails "cannot read 2 x 1024 bytes of tiles
     from ...": that run's process fails, flagged, the session goes on (rc 0)
  K0 a smoke host says "kernel did not finish": the K1 line, the smoke gate fails, 16, no second smoke process (step 10 reads K1-STOPPED)
  K1 a run's host says "kernel did not finish": the session stops (K1), nothing further, rc 0 (step 10 reads K1-STOPPED)
  HG a run's host IGNORES its timeout's TERM: HUNG (rc 8), the stop file, nothing further, no closing config read, NOTHING KILLED: the hung
     double ends by itself ~14 s after it started (its marker file)
  TO a run's host sleeps past 10 s but ends on TERM: timeout's rc 124, flagged, the session goes on (one failure), rc 0
  SA a run's host prints records of another shire mask (the first run): never read as data; the reducer passes the host's record on and the
     FROZEN scorer's quorum sets the run aside (its record not the case's)
  F2 two failed processes in a row: the session stops, rc 0
  B1 the board above 70 W on 3 samples in a run: the stop, the host ends by its stop file ("stopping:"), nothing further, rc 0
  D1 the die (the shires' mean) at 70 C: the stop          D2 the latch rises to 88 C: the stop ("latch rose")
  D3 the board at 70.0 W (not above 70) on every later sample: no stop, rc 0
  DG the die gate: the die held at 61 C after the first run (gate min(60, rest + 4)): the later runs wait and are NO DATA
  CT the card-time rule (--rule-s 7): no run starts after it, rc 0          OP an operator's SIGTERM to the runner mid-run: the stop file,
     the host ends at its boundary, nothing further, rc 0           CR the runner crashes (forecast-e210.json missing in a copied tree):
     "CRASH:", the closing still runs (queue.json, the manifest), rc 1
  SF THE OPERATOR'S STOP FILE touched during run 004: run 007 never starts, the stop names the file, rc 0, the manifest
  S0 a STOP file already in the session's folder when the runner starts: refused before any device (16), no config read, the file kept
  DF a sampler that goes silent and IGNORES SIGTERM past the runner's two waits (90 s): the session stops ("would not stop"), NEVER two
     processes on the stand-in management node at once (a poller over /proc), no closing config read while it lives, rc 0, and the deaf
     double ends by itself (nothing kills it)
  RT card 1's runtime line ("Opening device 1") on a smoke host: the identity trip, the smoke gate fails, 16, no second smoke process; card
     0's line (its own) passes, rc 0      RT2 card 1's line on the first run's host: STOP (identity), nothing further, rc 0
  RTC card 1's line on the start config read: the identity gate, 16, no sampler
  BN the board line (in-process, e210_common.Stops): 95 W on every other sample with no board reading between trips at the third reading
  PB THE PROBE, its registered rule (pass 2's first three blocks: highmant8, hd4, maxalte at S2): PB-IN the doubles' R1 watts (board about
     51 W): IN, maxalte's two runs start; PB-W maxalte's watts 15 W over (board about 66 W, above 64, under the 70 W stop): OUT, maxalte leaves
     the session: its two runs NOT STARTED (the probe's reason named), the other runs run, no stop, rc 0; PB-D the die read 63 C in the probe's
     window (not under 63): OUT; PB-C the probe's process crashes: OUT (the line not shown), one failed process, the session goes on, rc 0
  OR THE ORDER: the whole registered sequence (171 runs) at a tiny scale: every run's key and argv the registered ones (the run's host_args,
     --seconds 6 --budget 7.5, the kit's --kernel and --stop-file, under `timeout 10`, never -k), in order, and every host record read as its
     command's (the patterns' 61-file --values strings among them)
  E2 END TO END three times at once on the registered cut subset (the warm-up ties and passes 1-4: 126 runs, every case's blocks at least
     twice; a 6 s rest read, since the reducer's rest window is the registered 5 s; the doubles' leakage off) through the reducer and the FROZEN
     scorer: E2-R1 the truth on R1, badjeq@S1's counter 0.2% over (the time equality): R0 PASS, badjeq@S1 T FAIL (reported, not scored), B5
     PASS on the 12 others, H1 H2 H3 R1 BETTER; E2-R3L the truth on R3L: B5 FAIL, H3 R3L BETTER; E2-R3 the truth on raw R3: maxalte@S2's board
     about 68 W, so the probe takes it out (NO DATA), nothing stops
  RF the refusals: the --dry options without --dry, V3_DRY without --dry, `--arm B` (argparse), and the REAL runner on this desk stopping
     at its box check
  QS (fix-e210, before any datum; verify-e210's finding 2 and its case V6; E210.md A1 item 6) A SAMPLER SILENT THROUGH A RUN: a finished
     session (pass 2's first three blocks, the probe IN) copied, every telemetry sample inside the counted launches of two runs taken out of the
     copy (the random run shared by highmant8's and hd4's blocks, maxalte's first run; their rest samples kept); the reducer rc 0 (the two runs
     without clock keys, p_work null, flagged; the table prints them), the collection's data step rc 0 (COLLECTED), the frozen scorer rc 0 (the
     three blocks set aside by their clock, their cases NO DATA; the random drift on the three random runs with a power; R0 PASS)
Every number here comes from the doubles (E206's measured random at the shape and the frozen routes driven through a toy card): a desk check of
code, not a measurement and not a reading of E210. SPDX-License-Identifier: Apache-2.0
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
RUNNER = os.path.join(HERE, "run_e210.py")
sys.path.insert(0, HERE)
import e210_common as C  # noqa: E402

FAST = ["--rest-s", "0.3", "--smoke-rest-s", "1.5", "--tail-s", "0.2", "--gate-wait-s", "3"]
SHORT_RUNS = ["001-open-random-S1", "004-pass1-sparse50-S1", "007-pass1-bhalfeq-S1"]


class T:
    def __init__(self, scratch, only):
        self.S, self.only = scratch, set(only or [])
        self.n = self.ok = 0
        self.n_open = 30           # the launches of the smoke and the probe (G1 measures it)

    def want(self, name):
        return not self.only or name in self.only

    def case(self, name, good, detail):
        self.n += 1
        self.ok += 1 if good else 0
        print(f"{name}: {'PASS' if good else 'FAIL'} - {detail}", flush=True)

    def session(self, name, arm, env=None, seq="short", extra=None, scale="0.05", runner=None, signal_after=None, inject=None,
                touch_after=None, pre_stop=False, watch_mgmt=False, cwd=None):
        d = os.path.join(self.S, name)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
        e = {k: v for k, v in os.environ.items() if not k.startswith("E210_FAKE_")}
        e.update({"E210_FAKE_SCALE": scale, "E210_FAKE_TAU_S": "1"})
        if inject is not None:
            ip = os.path.join(d, "inject.json")
            json.dump(inject, open(ip, "w"))
            e["E210_FAKE_INJECT"] = ip
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
            p = subprocess.Popen(cmd, cwd=cwd or REPO, stdout=fo, stderr=subprocess.STDOUT, env=e)
            if signal_after or touch_after:
                want_text, secs = signal_after or touch_after
                tq = time.time()
                while time.time() - tq < 120 and p.poll() is None:
                    if os.path.exists(os.path.join(out, "session.log")) and want_text in open(os.path.join(out, "session.log")).read():
                        time.sleep(secs)
                        if signal_after:
                            p.send_signal(signal.SIGTERM)
                        else:         # the operator touches the session's STOP file (CARD-LANE-BRIEF 2)
                            open(os.path.join(out, "STOP"), "a").close()
                        break
                    time.sleep(0.05)
            if watch_mgmt:            # case DF (fix-e206): how many processes hold the stand-in management node at once, polled 5 times a s
                fake = os.path.realpath(os.path.join(out, "fakedev"))
                while p.poll() is None and time.time() - t0 < 1800:
                    self.max_mgmt = max(self.max_mgmt, mgmt_holders(fake))
                    time.sleep(0.2)
            rc = p.wait(timeout=3600)
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


def sm_json(d, case):
    p = os.path.join(d, "smoke", case.replace("@", "-"), "smoke.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def probe_json(d):
    p = os.path.join(d, "probe", "maxalte-S2", "probe.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def first_run_dir(d):
    return os.path.join(d, "runs", "001-open-random-S1")


def reduce_score(S, tag, d):
    dj, sj = os.path.join(S, f"{tag}-data.json"), os.path.join(S, f"{tag}-scored.json")
    r1 = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "reduce_e210.py"), "--arm", f"A={d}", "--out", dj], capture_output=True, text=True)
    r2 = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "score_e210.py"), dj, "--out", sj], capture_output=True, text=True)
    data = json.load(open(dj)) if os.path.exists(dj) else {}
    sc = json.load(open(sj)) if os.path.exists(sj) else {}
    return r1.returncode, r2.returncode, data, sc


def qs_case(t, S):
    """QS (fix-e210, before any datum; verify-e210's finding 2, its case V6; E210.md A1 item 6): A SAMPLER SILENT THROUGH A RUN. A finished
    session on the doubles (pass 2's first three blocks, the probe IN) is copied and, in the copy, every telemetry sample inside the counted
    launches of two runs is taken out - the random run shared by the highmant8 and hd4 blocks and maxalte's first run - as a sampler silent
    through those runs leaves the telemetry (its rest samples kept), and the copy's manifest re-made for that file. Then the reducer (rc 0: the
    two runs carry no clock key, p_work null and the flag; the table prints them), the collection's data step (RB_DESKTEST=1 --outside: rc 0,
    COLLECTED, its reducer run inside it) and the frozen scorer on the collected data-e210.json (rc 0: the three blocks set aside by their clock
    reading, so their cases NO DATA; the random-drift report on the three random runs with a power; R0 PASS). The first freeze of the scorer
    crashed on such data (A1 item 6); the reducer as kitted crashed in its table (V6)."""
    import gzip
    import getpass
    import hashlib
    rc, log, d, dt = t.session("QS-base", "A", {"E210_FAKE_LEAK": "0"}, seq="s2", scale="0.2")
    seq = [r for r in C.sequence("A") if r["pass"] == "pass2"][:10]
    keys = [C.run_key(r) for r in seq]
    quiet_keys = [keys[3], keys[7]]                 # the shared random run between highmant8 and hd4; maxalte's first run
    pr = probe_json(d)
    qd = os.path.join(S, "QS-copy")
    if os.path.exists(qd):
        shutil.rmtree(qd)
    os.makedirs(qd)
    copy = os.path.join(qd, "T1794000000-A")       # the box's session folder form (the collection reads T0 from the folder's name)
    shutil.copytree(d, copy)
    for x in ("dry.lock",):                        # the dry pass's own lock: never in a copy-back (the manifest leaves it out)
        if os.path.exists(os.path.join(copy, x)):
            os.remove(os.path.join(copy, x))
    windows, before = {}, {}
    for k in quiet_keys:
        rj = json.load(open(os.path.join(copy, "runs", k, "run.json")))
        ws = []
        for p in rj.get("procs") or []:
            txt = open(os.path.join(copy, "runs", k, p["name"] + ".out"), errors="replace").read()
            fma, chk, info = C.host_records(txt, p.get("argv"))
            ws += [(L["t_start_ms"], L["t_end_ms"]) for L in fma if C.counted(L)]
        windows[k] = ws
    tp = os.path.join(copy, "telemetry.jsonl.gz")
    lines = gzip.open(tp, "rt").read().splitlines()
    kept, dropped = [], {k: 0 for k in quiet_keys}
    for ln in lines:
        try:
            tm = json.loads(ln).get("t_ms") if ln.startswith("{") else None
        except ValueError:
            tm = None
        hit = [k for k in quiet_keys if tm is not None and any(a <= tm <= b for a, b in windows[k])]
        if hit:
            dropped[hit[0]] += 1
            continue
        kept.append(ln)
    with gzip.open(tp, "wt") as f:
        f.write("\n".join(kept) + "\n")
    man = os.path.join(copy, "MANIFEST.sha256")
    rows = []
    for ln in open(man):
        h, p = ln.rstrip("\n").split("  ", 1)
        if p == "telemetry.jsonl.gz":
            h = hashlib.sha256(open(tp, "rb").read()).hexdigest()
        rows.append(f"{h}  {p}")
    open(man, "w").write("\n".join(rows) + "\n")
    dj, txt = os.path.join(S, "QS-data.json"), os.path.join(S, "QS-reduce.txt")
    r1 = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "reduce_e210.py"), "--arm", f"A={copy}", "--out", dj, "--txt", txt],
                        capture_output=True, text=True)
    data = json.load(open(dj)) if os.path.exists(dj) else {}
    runs = data.get("runs", {})
    red_ok = r1.returncode == 0 and all(runs.get(k, {}).get("ran") and (runs[k].get("n_launch_counted") or 0) >= 1 and "mhz_min" not in runs[k]
                                        and "mhz_max" not in runs[k] and runs[k].get("p_work_w") is None
                                        and any("no telemetry sample inside" in f for f in runs[k].get("detail", {}).get("flags", []))
                                        for k in quiet_keys) \
        and sorted(data.get("runs_without_a_sample_inside", [])) == sorted(quiet_keys) and r1.stdout.count("the clock not read") == 2
    od = os.path.join(S, "QS-collected")
    if os.path.exists(od):
        shutil.rmtree(od)
    os.makedirs(od)
    lf = os.path.join(S, "QS-login.txt")
    open(lf, "w").write(getpass.getuser() + "\n")
    day = time.strftime("%Y-%m-%d")
    r2 = subprocess.run([sys.executable, "-B", os.path.join(HERE, "collect_e210.py"), "data", day, "A", copy, os.path.expanduser("~"), lf,
                         "--outside", od], capture_output=True, text=True, env=dict(os.environ, RB_DESKTEST="1"))
    cdir = os.path.join(od, f"{day}-e210-switch-test-aifoundry3")
    cdata = os.path.join(cdir, "data-e210.json")
    sj = os.path.join(S, "QS-scored.json")
    r3 = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "score_e210.py"), cdata, "--out", sj], capture_output=True, text=True)
    sc = json.load(open(sj)) if os.path.exists(sj) else {}
    cs = sc.get("cases", {})
    whys = " ".join(b.get("why", "") for c in ("highmant8@S2", "hd4@S2", "maxalte@S2") for b in cs.get(c, {}).get("blocks", []))
    drift = ((sc.get("reported") or {}).get("random_drift") or {}).get("random@S2", {}).get("n")
    good = (rc == 0 and pr.get("verdict") == "IN" and runs_ran(d) == 10 and all(v > 0 for v in dropped.values()) and red_ok
            and r2.returncode == 0 and "COLLECTED " in r2.stdout and os.path.exists(cdata) and r3.returncode == 0
            and all(cs.get(c, {}).get("Q") == "NO DATA" for c in ("highmant8@S2", "hd4@S2", "maxalte@S2"))
            and whys.count("clock None-None MHz") == 3 and drift == 3 and (sc.get("R0") or {}).get("verdict") == "PASS")
    t.case("QS", good, f"session rc {rc}, the probe {pr.get('verdict')}, runs {runs_ran(d)}; samples taken out of the copy "
           f"{ {k[:3]: v for k, v in dropped.items()} }; reduce rc {r1.returncode} (the two runs without clock keys, p_work null, flagged: {red_ok}); "
           f"collect rc {r2.returncode} ({'COLLECTED' if 'COLLECTED ' in r2.stdout else (r2.stdout.strip().splitlines() or ['?'])[-1][:60]}); "
           f"score rc {r3.returncode}: highmant8@S2 {cs.get('highmant8@S2', {}).get('Q')}, hd4@S2 {cs.get('hd4@S2', {}).get('Q')}, maxalte@S2 "
           f"{cs.get('maxalte@S2', {}).get('Q')} ({whys.count('clock None-None MHz')} blocks set aside by the clock), random drift on {drift} runs, "
           f"R0 {(sc.get('R0') or {}).get('verdict')}")


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
    print(f"selftest_run_e210 ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; /dev/et*: none; "
          f"/run/lock entries: {len(os.listdir('/run/lock')) if os.path.isdir('/run/lock') else 'none'}", flush=True)
    e2 = {}
    if t.want("E2"):                  # the three end-to-end sessions start first and run beside the other cases (about 17 minutes)
        for tag, truth, more in (("R1", "R1", {"E210_FAKE_HOST": "cyc1001", "E210_FAKE_HOST_CASE": "badjeq@S1"}), ("R3L", "R3L", {}), ("R3", "R3", {})):
            d = os.path.join(S, f"E2-{tag}")
            if os.path.exists(d):
                shutil.rmtree(d)
            os.makedirs(d)
            e = {k: v for k, v in os.environ.items() if not k.startswith("E210_FAKE_")}
            e.update({"E210_FAKE_SCALE": "0.2", "E210_FAKE_TAU_S": "1", "E210_FAKE_LEAK": "0", "E210_FAKE_TRUTH": truth})
            e.update(more)
            cmd = [sys.executable, "-B", RUNNER, "session", "--dry", "--arm", "A", "--t0", str(int(time.time())), "--out", os.path.join(d, "T"),
                   "--sequence", "cut"] + FAST + ["--rest-s", "6"]
            e2[tag] = (subprocess.Popen(cmd, cwd=REPO, stdout=open(os.path.join(d, "runner.out"), "w"), stderr=subprocess.STDOUT, env=e),
                       os.path.join(d, "T"))

    if t.want("G1"):
        rc, log, d, dt = t.session("G1", "A")
        ls = log.splitlines()
        i_sm = max([i for i, x in enumerate(ls) if "smoke random@S2:" in x] or [-1])
        i_pr = max([i for i, x in enumerate(ls) if "the probe maxalte@S2: IN" in x] or [-1])
        i_sp = min([i for i, x in enumerate(ls) if "stop-path test passed" in x] or [10 ** 6])
        sm = [sm_json(d, c) for c in C.SMOKE_CASES]
        pr = probe_json(d)
        t.n_open = sum(x.get("n_launch", 0) for x in sm) + (pr.get("proc") or {}).get("n_launch", 0) or t.n_open
        idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
        errs = "".join(open(os.path.join(dp, f)).read() for dp, dn, fn in os.walk(d) for f in fn if f.endswith(".err") and f.startswith("proc"))
        t.case("G1", rc == 0 and "the card's identity: PCIe target /dev/et0_mgmt, physical device ID 0" in log and "the identity read: " in log
               and all(x.get("good") for x in sm) and len([x for x in sm if x]) == 3
               and all("E206's measured cycles an op at the shape" in x.get("cycles_ref_is", "") for x in sm)
               and 0 <= i_sm < i_pr < i_sp < 10 ** 6 and pr.get("verdict") == "IN" and runs_ran(d) == 3 and "config end: {" in log
               and os.path.exists(os.path.join(d, "MANIFEST.sha256")) and "STOP" not in log and idn.get("config_start", {}).get("minion_mv") == 523
               and [x["run"] for x in q_of(d).get("queue", [])] == SHORT_RUNS and "cannot read" not in errs,
               f"rc {rc}; the smoke {[x.get('good') for x in sm]} (ratios {[round(x.get('cycles_ratio') or 0, 4) for x in sm]}), the probe "
               f"{pr.get('verdict')} (board max {pr.get('board_max_w')} W, die max {pr.get('die_max_c')} C) then the stop-path test (lines {i_sm} < "
               f"{i_pr} < {i_sp}); {runs_ran(d)} runs {[x['run'] for x in q_of(d).get('queue', [])]}; {t.n_open} opening launches; the 87 C latch "
               f"tripped nothing ({'STOP' not in log}); every tile file read ({'cannot read' not in errs}); {dt:.0f} s")
    for name, mode, want in (("C1", "tdp65", "the gate, no launch"), ("C2", "card1", "/dev/et1_mgmt, not /dev/et0_mgmt"),
                             ("C4", "noident", "no 'PCIe target' line"), ("C5", "fail", "config read rc 1")):
        if t.want(name):
            rc, log, d, dt = t.session(name, "A", {"E210_FAKE_CONFIG": mode})
            t.case(name, rc == 16 and want in log and "the gate, no launch" in log and "sampler started" not in log and not has_proc(d),
                   f"rc {rc}; '{[x[24:200] for x in log.splitlines() if 'config start' in x][:1]}'")
    if t.want("C6"):
        rc, log, d, dt = t.session("C6", "A", {"E210_FAKE_CONFIG": "hang", "E210_FAKE_HANG_S": "16"})
        mk = wait_marker(os.path.join(d, "fake_sched.jsonl.config-hang-ended"), 30)
        t.case("C6", rc == 8 and " HUNG: " in log and "sampler started" not in log and "config end: not read" in log and "ended by itself" in mk
               and q_of(d).get("hung"), f"rc {rc}; the HUNG line {' HUNG: ' in log}; the hung double: '{mk[:90]}'")
    if t.want("C7"):
        rc, log, d, dt = t.session("C7", "A", {"E210_FAKE_CONFIG": "runtime"})
        idn = json.load(open(os.path.join(d, "identity.json"))) if os.path.exists(os.path.join(d, "identity.json")) else {}
        t.case("C7", rc == 0 and "physical device ID 0" in log and runs_ran(d) == 3 and idn.get("config_start", {}).get("runtime_cards") == ["0"],
               f"rc {rc}; the config read whole past card 0's runtime line ({idn.get('config_start', {}).get('runtime_cards')})")
    for name, env, want in (("H1", {"E210_FAKE_ETWHO": "other"}, "holder line(s) of another login"),
                            ("H3", {"E210_FAKE_ETWHO": "other1"}, "holder line(s) of another login"),
                            ("H4", {"E210_FAKE_ETWHO": "fail"}, "et-who unreadable (rc 1)"),
                            ("H5", {"E210_FAKE_PS": "ours"}, "other device process(es) of ours"),
                            ("H6", {"E210_FAKE_PS": "ci"}, "CI job")):
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
        e = {k: v for k, v in os.environ.items() if not k.startswith("E210_FAKE_")}
        r = subprocess.run([sys.executable, "-B", RUNNER, "session", "--dry", "--arm", "A", "--t0", str(int(time.time())), "--out", d0] + FAST,
                           cwd=REPO, capture_output=True, text=True, env=e)
        holder.terminate()
        holder.wait()
        log = open(os.path.join(d0, "session.log")).read()
        t.case("L1", r.returncode == 16 and "refused, no device opened: the card's lock is held" in log and not os.path.exists(os.path.join(d0, "config-start.json")),
               f"rc {r.returncode}")
    if t.want("S1"):
        rc, log, d, dt = t.session("S1", "A", {"E210_FAKE_SAMPLER": "dead"})
        t.case("S1", rc == 16 and "the sampler would not start" in log and not has_proc(d), f"rc {rc}")
    if t.want("S2"):
        rc, log, d, dt = t.session("S2", "A", {"E210_FAKE_SAMPLER": "card1"})
        t.case("S2", rc == 16 and "the identity read (the sampler running, before the smoke)" in log and "the gate, no launch" in log and not has_proc(d),
               f"rc {rc}; '{[x[24:220] for x in log.splitlines() if 'identity read' in x][:1]}'")
    if t.want("S3"):
        rc, log, d, dt = t.session("S3", "A", {"E210_FAKE_SAMPLER": f"hangs:{t.n_open + 3}"})
        t.case("S3", rc == 0 and "the sampler is not live" in log and log.count("sampler started") >= 2 and runs_ran(d) >= 2,
               f"rc {rc}; sampler starts {log.count('sampler started')}; runs {runs_ran(d)}")
    if t.want("S4"):
        rc, log, d, dt = t.session("S4", "A", {"E210_FAKE_SAMPLER": f"dies:{t.n_open + 3}"})
        t.case("S4", rc == 0 and log.count("sampler started") >= 2 and runs_ran(d) >= 2, f"rc {rc}; sampler starts {log.count('sampler started')}; runs {runs_ran(d)}")
    if t.want("P1"):
        import run_e210 as R
        d = os.path.join(S, "P1")
        os.makedirs(d, exist_ok=True)
        ns = argparse.Namespace(what="session", arm="A", t0=int(time.time()), out=os.path.join(d, "T"), deadline_epoch=0, dry=True,
                                sequence="short", rest_s=0.3, smoke_rest_s=1.5, tail_s=0.2, gate_wait_s=3, rule_s=C.CARD_RULE_S, cap_s=C.CAP_S)
        s = R.Session(ns)
        s.t_first = time.time()
        ok, res = s.stop_path_test()
        t.case("P1", not ok and not res["board"]["tripped"] and not res["die"]["tripped"], f"ok {ok}; {json.dumps({k: v['tripped'] for k, v in res.items()})}")
    second = os.path.join("smoke", "zeros-S1")
    for name, env, want in (("R1", {"E210_FAKE_HOST": "wrong"}, "check wrong"), ("R2", {"E210_FAKE_HOST": "crash"}, "rc 134"),
                            ("R4", {"E210_FAKE_HOST": "norise"}, "the board's rise"), ("R6", {"E210_FAKE_HOST": "mismatch"}, "not its command's"),
                            ("R7", {"E210_FAKE_HOST": "cyc3x"}, "cycles ratio 3.0")):
        if t.want(name):
            rc, log, d, dt = t.session(name, "A", env)
            t.case(name, rc == 16 and "smoke gate failed" in log and runs_ran(d) == 0 and want in log
                   and not os.path.isdir(os.path.join(d, second)), f"rc {rc}; '{[x[24:230] for x in log.splitlines() if 'smoke random@S1' in x][:1]}'")
    if t.want("R3"):
        rc, log, d, dt = t.session("R3", "A", {"E210_FAKE_HOST": "card1"})
        err = open(os.path.join(d, "smoke", "random-S1", "proc.err")).read() if os.path.exists(os.path.join(d, "smoke", "random-S1", "proc.err")) else ""
        t.case("R3", rc == 16 and os.path.exists(os.path.join(d, "STOP")) and "stopping:" in err and "smoke gate failed" in log
               and not os.path.isdir(os.path.join(d, second)), f"rc {rc}; the host stopped by the file {'stopping:' in err}")
    if t.want("R5"):
        rc, log, d, dt = t.session("R5", "A", {"E210_FAKE_HOST": "runtime"})
        sm = sm_json(d, "random@S1")
        t.case("R5", rc == 0 and sm.get("records", {}).get("runtime_lines") == 2 and sm.get("records", {}).get("unparsed") == 0 and "smoke gate passed" in log,
               f"rc {rc}; random@S1's records {sm.get('records')}")
    if t.want("R8"):
        rc, log, d, dt = t.session("R8", "A", touch_after=("the opening's rest:", 0.05), scale="0.3")
        gl = [x[24:260] for x in log.splitlines() if "smoke gate failed" in x]
        t.case("R8", rc == 16 and bool(gl) and "the operator's STOP file" in gl[0] and runs_ran(d) == 0 and os.path.exists(os.path.join(d, "STOP")),
               f"rc {rc}; '{gl[:1]}'")
    if t.want("R9"):
        tree = os.path.join(S, "R9-tree")
        if os.path.exists(tree):
            shutil.rmtree(tree)
        for rel in [r for r in C.tiles()] + ["tools/claims-v3/e210/" + f for f in ("run_e210.py", "e210_common.py", "e210_ident.py", "fake_card_e210.py",
                                                                                   "points-e210.json", "forecast-e210.json", "SHA256SUMS-e210-registration")]:
            os.makedirs(os.path.dirname(os.path.join(tree, rel)), exist_ok=True)
            shutil.copy2(os.path.join(REPO, rel), os.path.join(tree, rel))
        os.remove(os.path.join(tree, "tools/claims-v3/e210/tiles/fp32/bhalfeq/bhalfeq_37.bin"))
        rc, log, d, dt = t.session("R9", "A", runner=os.path.join(tree, "tools/claims-v3/e210/run_e210.py"), cwd=tree)
        rj = os.path.join(d, "runs", "007-pass1-bhalfeq-S1", "run.json")
        rj = json.load(open(rj)) if os.path.exists(rj) else {}
        err = open(os.path.join(d, "runs", "007-pass1-bhalfeq-S1", "proc-00.err")).read() if os.path.exists(os.path.join(d, "runs", "007-pass1-bhalfeq-S1", "proc-00.err")) else ""
        t.case("R9", rc == 0 and [p.get("rc") for p in rj.get("procs", [])] == [1] and "cannot read 2 x 1024 bytes of tiles from tools/claims-v3/e210/tiles/fp32/bhalfeq/bhalfeq_37.bin" in err
               and "the process rc 1" in " ".join(rj.get("flags", [])) and runs_ran(d) == 3,
               f"rc {rc}; run 007's process rc {[p.get('rc') for p in rj.get('procs', [])]}: '{err.strip().splitlines()[-1][:120] if err.strip() else ''}'")
    if t.want("K0"):
        rc, log, d, dt = t.session("K0", "A", {"E210_FAKE_HOST": "k1"})
        t.case("K0", rc == 16 and "K1: a launch of the smoke's random@S1 did not finish" in log and "smoke gate failed" in log and runs_ran(d) == 0
               and not os.path.isdir(os.path.join(d, second)), f"rc {rc}; the K1 line {'K1: a launch of the smoke' in log}; no second smoke process")
    run_from = {"E210_FAKE_HOST_FROM_N": str(t.n_open), "E210_FAKE_HOST_COUNT": "1"}   # the first run's host sees the opening's launches
    if t.want("K1"):
        rc, log, d, dt = t.session("K1", "A", dict(run_from, E210_FAKE_HOST="k1"))
        t.case("K1", rc == 0 and "STOP: K1: a launch of run 001-open-random-S1 did not finish" in log and runs_ran(d) == 1, f"rc {rc}; runs {runs_ran(d)}")
    if t.want("HG"):
        t0 = time.time()
        rc, log, d, dt = t.session("HG", "A", dict(run_from, E210_FAKE_HOST="hang_term", E210_FAKE_HANG_S="14"))
        mk = wait_marker(os.path.join(d, "fake_sched.jsonl.hang-ended"), 30)
        rj = json.load(open(os.path.join(first_run_dir(d), "run.json"))) if os.path.exists(os.path.join(first_run_dir(d), "run.json")) else {}
        t.case("HG", rc == 8 and " HUNG: a device process (the host of 001-open-random-S1" in log and "config end: not read (a device process of ours is HUNG" in log
               and os.path.exists(os.path.join(d, "STOP")) and runs_ran(d) == 1 and [p.get("hung") for p in rj.get("procs", [])] == [True]
               and "ended by itself" in mk and "nothing killed it" in mk, f"rc {rc}; the run's process hung {[p.get('hung') for p in rj.get('procs', [])]}; "
               f"the hung double: '{mk[:100]}' ({time.time() - t0:.0f} s after the session began)")
    if t.want("SA"):
        rc, log, d, dt = t.session("SA", "A", dict(run_from, E210_FAKE_HOST="mismatch"))
        r1, r2, data, sc = reduce_score(S, "SA", d)
        run = data.get("runs", {}).get("001-open-random-S1", {})
        t.case("SA", rc == 0 and r1 == 0 and r2 == 0 and run.get("ran") and run.get("t_gemm_s") is None and run.get("record", {}).get("shire_mask") == "0x1fffffffe"
               and any("another command" in f for f in run.get("detail", {}).get("flags", [])) and sc.get("R0", {}).get("verdict") == "PASS",
               f"rc {rc}; the first run: t_gemm {run.get('t_gemm_s')}, the host's record {run.get('record')}; the scorer's R0 {sc.get('R0', {}).get('verdict')}")
    if t.want("TO"):
        rc, log, d, dt = t.session("TO", "A", dict(run_from, E210_FAKE_HOST="hang"))
        rj = json.load(open(os.path.join(first_run_dir(d), "run.json"))) if os.path.exists(os.path.join(first_run_dir(d), "run.json")) else {}
        t.case("TO", rc == 0 and [p.get("rc") for p in rj.get("procs", [])] == [124] and runs_ran(d) == 3 and " HUNG" not in log,
               f"rc {rc}; the tie's process rc {[p.get('rc') for p in rj.get('procs', [])]}; runs {runs_ran(d)}")
    if t.want("F2"):
        rc, log, d, dt = t.session("F2", "A", {"E210_FAKE_HOST": "crash", "E210_FAKE_HOST_FROM_N": str(t.n_open), "E210_FAKE_HOST_COUNT": "2"})
        t.case("F2", rc == 0 and "STOP: two failed processes in a row" in log and runs_ran(d) == 2, f"rc {rc}; runs {runs_ran(d)}")
    for name, inj, want in (("B1", [{"board_w": 71.0, "after_launches": t.n_open + 2, "count": 3}], "board 71.0 W above 70 W on 3 samples"),
                            ("D1", [{"die": 70, "after_launches": t.n_open + 2, "count": 1}], "die 70 C (the shires' mean) at or above 70 C"),
                            ("D2", [{"high": 88, "after_launches": t.n_open + 2, "count": 1}], "latch rose to 88 C (from 87 C")):
        if t.want(name):
            rc, log, d, dt = t.session(name, "A", inject=inj, scale="0.2")
            err = open(os.path.join(first_run_dir(d), "proc-00.err")).read() if os.path.exists(os.path.join(first_run_dir(d), "proc-00.err")) else ""
            t.case(name, rc == 0 and want in log and "nothing further started" in log and runs_ran(d) == 1 and "stopping:" in err,
                   f"rc {rc}; '{[x[24:200] for x in log.splitlines() if 'STOP:' in x][:1]}'; the host ended by the stop file {'stopping:' in err}")
    if t.want("D3"):
        rc, log, d, dt = t.session("D3", "A", inject=[{"board_w": 70.0, "after_launches": t.n_open + 1}])
        t.case("D3", rc == 0 and "STOP" not in log and runs_ran(d) == 3, f"rc {rc}; 70.0 W on every later sample: no stop ({'STOP' not in log})")
    if t.want("DG"):
        rc, log, d, dt = t.session("DG", "A", inject=[{"die": 61, "after_launches": t.n_open + 2}])
        q = q_of(d).get("queue", [])
        t.case("DG", rc == 0 and runs_ran(d) == 1 and sum(1 for x in q if not x.get("ran") and "the die gate" in str(x.get("why"))) == 2,
               f"rc {rc}; {[(x['run'], x.get('ran'), str(x.get('why'))[:60]) for x in q]}")
    if t.want("CT"):
        rc, log, d, dt = t.session("CT", "A", seq="two", extra=["--rule-s", "7", "--rest-s", "2"])
        q = q_of(d).get("queue", [])
        first = next((i for i, x in enumerate(q) if not x.get("ran")), None)
        t.case("CT", rc == 0 and runs_ran(d) < 3 and first is not None and "the card-time rule" in str(q[first].get("why"))
               and all(not x.get("ran") for x in q[first:]), f"rc {rc}; {[(x['run'], x.get('ran'), str(x.get('why'))[:50]) for x in q]}")
    if t.want("OP"):
        rc, log, d, dt = t.session("OP", "A", signal_after=("run 001-open-random-S1: random@S1", 0.5), scale="0.3")
        err = open(os.path.join(first_run_dir(d), "proc-00.err")).read() if os.path.exists(os.path.join(first_run_dir(d), "proc-00.err")) else ""
        t.case("OP", rc == 0 and "the operator's signal 15" in log and runs_ran(d) == 1 and "stopping:" in err and os.path.exists(os.path.join(d, "MANIFEST.sha256")),
               f"rc {rc}; runs {runs_ran(d)}; the host ended by the stop file {'stopping:' in err}")
    if t.want("CR"):
        tree = os.path.join(S, "CR-tree")
        if os.path.exists(tree):
            shutil.rmtree(tree)
        dst = os.path.join(tree, "tools", "claims-v3", "e210")
        os.makedirs(dst)
        for f in ("run_e210.py", "e210_common.py", "e210_ident.py", "fake_card_e210.py", "points-e210.json"):
            shutil.copy2(os.path.join(HERE, f), dst)
        rc, log, d, dt = t.session("CR", "A", runner=os.path.join(dst, "run_e210.py"))
        t.case("CR", rc == 1 and "CRASH: FileNotFoundError" in log and os.path.exists(os.path.join(d, "queue.json")) and os.path.exists(os.path.join(d, "MANIFEST.sha256"))
               and "session end" in log, f"rc {rc}; '{[x[24:160] for x in log.splitlines() if 'CRASH' in x][:1]}'")
    if t.want("SF"):
        rc, log, d, dt = t.session("SF", "A", touch_after=("run 004-", 0.4), scale="0.3")
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
        rc, log, d, dt = t.session("DF", "A", {"E210_FAKE_SAMPLER": f"deaf:{t.n_open + 3}", "E210_FAKE_DEAF_S": "110"}, scale="0.3",
                                   watch_mgmt=True)
        mk = wait_marker(os.path.join(d, "fake_sched.jsonl.sampler-deaf-ended"), 120)
        q = q_of(d)
        t.case("DF", rc == 0 and t.max_mgmt <= 1 and "the sampler would not stop on SIGTERM" in str(q.get("stop"))
               and "config end: not read (the sampler did not stop on SIGTERM" in log and log.count("sampler started") == 1
               and bool(q.get("samplers_left")) and "ended by itself" in mk and "nothing killed it" in mk,
               f"rc {rc}; most processes on the stand-in management node at once {t.max_mgmt}; samplers started {log.count('sampler started')}; "
               f"left {q.get('samplers_left')}; the stop {str(q.get('stop'))[:100]!r}; the deaf double: '{mk[:80]}'; {dt:.0f} s")
    if t.want("RT"):
        rc, log, d, dt = t.session("RT", "A", {"E210_FAKE_HOST": "runtime1"})
        rca, loga, da, dta = t.session("RT-0", "A", {"E210_FAKE_HOST": "runtime"})
        t.case("RT", rc == 16 and "smoke gate failed" in log and "ANOTHER by its runtime line: card(s) ['1']" in log
               and not os.path.isdir(os.path.join(d, second)) and rca == 0 and runs_ran(da) == 3 and "STOP" not in loga,
               f"card 1's line: rc {rc}: '{[x[24:200] for x in log.splitlines() if 'smoke random@S1' in x][:1]}'; card 0's line (its own) rc {rca}, "
               f"runs {runs_ran(da)}")
    if t.want("RT2"):
        rc, log, d, dt = t.session("RT2", "A", dict(run_from, E210_FAKE_HOST="runtime1"))
        q = q_of(d)
        t.case("RT2", rc == 0 and runs_ran(d) == 1 and "identity: the runtime named card(s) ['1']" in str(q.get("stop"))
               and "nothing further started" in log, f"rc {rc}; runs {runs_ran(d)}; the stop {str(q.get('stop'))[:120]!r}")
    if t.want("RTC"):
        rc, log, d, dt = t.session("RTC", "A", {"E210_FAKE_CONFIG": "runtime1"})
        t.case("RTC", rc == 16 and "its stdout's runtime line(s) name card(s) ['1']" in log and "the gate, no launch" in log
               and "sampler started" not in log and not has_proc(d), f"rc {rc}; '{[x[24:220] for x in log.splitlines() if 'config start' in x][:1]}'")
    if t.want("BN"):
        smp = [{"t_ms": k, "board_w": 95.0} if k % 2 else {"t_ms": k, "temp_c": {"minshire": [50, 46, 87]}} for k in range(1, 8)]
        sa = C.Stops(**C.stops_of("A"))
        ra = [sa.feed(s) for s in smp]
        t.case("BN", ra == [[], [], [], [], ["stop"], [], []] and "95.0 W above 70 W on 3 samples" in (sa.stop or ""),
               f"95 W on every other sample, no board reading between: {ra}, {sa.stop!r}")
    if t.want("PB"):
        mx = [r["run"] for r in C.sequence("A") if r["pass"] == "pass2" and r["case"] == "maxalte@S2"][:2]
        n_smoke_l = None
        for tag, env, inj, want_v in (("PB-IN", {}, None, "IN"), ("PB-W", {"E210_FAKE_HOTCASE": "maxalte@S2", "E210_FAKE_HOT_W": "15"}, None, "OUT"),
                                      ("PB-D", {}, "die", "OUT"), ("PB-C", {"E210_FAKE_HOST": "crash", "E210_FAKE_HOST_CASE": "maxalte@S2",
                                                                            "E210_FAKE_HOST_COUNT": "1"}, None, "OUT")):
            injs = None
            if inj == "die":            # the die at 63 C on samples inside the probe's window (after the smoke's launches, before the runs')
                injs = [{"die": 63, "after_launches": (n_smoke_l or t.n_open - 12) + 2, "count": 2}]
            rc, log, d, dt = t.session(tag, "A", dict(env, E210_FAKE_LEAK="0"), seq="s2", scale="0.2", inject=injs)
            if tag == "PB-IN":
                n_smoke_l = sum(sm_json(d, c).get("n_launch", 0) for c in C.SMOKE_CASES)
            pr = probe_json(d)
            q = q_of(d)
            qm = [x for x in q.get("queue", []) if x.get("run") in mx]
            others = [x for x in q.get("queue", []) if x.get("run") not in mx]
            if want_v == "IN":
                good = rc == 0 and pr.get("verdict") == "IN" and len(qm) == 2 and all(x.get("ran") for x in qm) and all(x.get("ran") for x in others)
            else:
                good = rc == 0 and pr.get("verdict") == "OUT" and len(qm) == 2 and not any(x.get("ran") for x in qm) \
                    and all("left the session at its probe" in str(x.get("why")) for x in qm) and all(x.get("ran") for x in others) \
                    and q.get("dropped", {}).get("maxalte@S2") and "STOP" not in log
            t.case(tag, good, f"rc {rc}; the probe {pr.get('verdict')} (board max {pr.get('board_max_w')} W, die max {pr.get('die_max_c')} C; "
                   f"{str(pr.get('why'))[:110]!r}); maxalte's runs {[(x.get('run'), x.get('ran')) for x in qm]}; the other {len(others)} runs ran "
                   f"{sum(1 for x in others if x.get('ran'))}; {dt:.0f} s")
    if t.want("QS"):   # fix-e210 (verify-e210's finding 2; E210.md A1 item 6): A QUIET SAMPLER, then the reducer, the collection and the scorer
        qs_case(t, S)
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
            want = C.host_argv(C.REPO, r["host_args"], C.RUN_SECONDS, C.RUN_BUDGET, os.path.join(d, "STOP"))
            if argv != want or "-k" in argv or C.arg_of(argv, "--values") != C.cases()[r["case"]]["values"]:
                bad.append(f"{C.run_key(r)} argv")
            if pr["records"]["unparsed"] or pr["records"]["mismatched"] or not pr["n_launch"]:
                bad.append(f"{C.run_key(r)} records {pr['records']}")
            nrec += pr["n_launch"]
        n61 = sum(1 for r in seq if len(C.arg_of(r["host_args"], "--values").split(":", 2)[2].split(",")) == 61)
        t.case("OR", rc == 0 and len(q) == len(seq) == 171 and not bad, f"rc {rc}; {len(q)} runs of {len(seq)}, every key and argv the registered "
               f"({n61} of them a 61-file --values string), {nrec} host records read as their commands' ({len(bad)} differ"
               f"{': ' + '; '.join(bad[:3]) if bad else ''}); {dt:.0f} s")
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
    if e2:
        fc = C.forecast()
        for tag, (p, d) in e2.items():
            rc = p.wait(timeout=3600)
            r1, r2, data, sc = reduce_score(S, f"E2-{tag}", d)
            rules = {k: v.get("verdict") for k, v in sc.get("rules", {}).items()}
            cases = sc.get("cases", {})
            # the reducer against the injected seconds and watts: every run's t_gemm the shape's, its W over idle the injected one
            worst_t, worst_w, n = 0.0, 0.0, 0
            for k, r in data.get("runs", {}).items():
                if not r.get("ran") or not r.get("t_gemm_s"):
                    continue
                n += 1
                case = C.cases()[r["case"]]
                cal = fc["calibration"][case["shape"]]
                worst_t = max(worst_t, abs(r["t_gemm_s"] / cal["t_gemm_s"] - 1))
                w_in = float(cal["W_random"])
                if case["kind"] != "random":
                    v = fc["cases"][case["case"]]["routes_W"].get(tag)
                    w_in += v if isinstance(v, (int, float)) else fc["cases"][case["case"]]["routes_W"]["R4"]
                if w_in >= 3.0 and r.get("p_work_w") is not None and r.get("p_rest_w") is not None:
                    worst_w = max(worst_w, abs((r["p_work_w"] - r["p_rest_w"]) / w_in - 1))
            if tag == "R1":
                good = (rc == 0 and r1 == 0 and r2 == 0 and sc.get("R0", {}).get("verdict") == "PASS" and cases.get("badjeq@S1", {}).get("T") is False
                        and cases.get("badjeq@S1", {}).get("scored") is False and rules.get("B5") == "PASS" and sc["rules"]["B5"]["scored"] == 12
                        and rules.get("H1") == "R1 BETTER" and rules.get("H2") == "R1 BETTER" and rules.get("H3") == "R1 BETTER"
                        and worst_t < 1e-4 and worst_w < 0.03)
            elif tag == "R3L":
                good = (rc == 0 and r1 == 0 and r2 == 0 and sc.get("R0", {}).get("verdict") == "PASS" and rules.get("B5") == "FAIL"
                        and rules.get("H3") == "R3L BETTER" and worst_t < 1e-4 and worst_w < 0.03)
            else:
                good = (rc == 0 and r1 == 0 and r2 == 0 and data.get("probe_reading", {}).get("verdict") == "OUT"
                        and cases.get("maxalte@S2", {}).get("Q") == "NO DATA" and not (data.get("queue") or {}).get("stop")
                        and all(not r.get("ran") for k, r in data.get("runs", {}).items() if r.get("case") == "maxalte@S2"))
            t.case(f"E2-{tag}", good, f"session rc {rc}, reduce rc {r1}, score rc {r2}; {n} runs reduced; t_gemm worst {worst_t:.2e}; W over idle "
                   f"against the injected worst {worst_w:.2%}; R0 {sc.get('R0', {}).get('verdict')}; rules {json.dumps(rules, sort_keys=True)}; "
                   f"badjeq@S1 T {cases.get('badjeq@S1', {}).get('T')}; the probe {(data.get('probe_reading') or {}).get('verdict')} "
                   f"(board max {(data.get('probe_reading') or {}).get('board_max_w')} W); maxalte@S2 {cases.get('maxalte@S2', {}).get('Q')}; "
                   f"stop {(data.get('queue') or {}).get('stop')}")
    print(f"SELFTEST-RUN-E210 {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
