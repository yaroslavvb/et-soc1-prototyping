#!/usr/bin/env python3
"""E190's runner desk test (Q169, the kit, Fri 13 Nov 2026, before any E190 datum): run_e190.py on the doubles (fake_card_e190.py), no
device, no box, every case its own --dry session in a scratch directory; then the end-to-end chain on the doubles' sessions: the reducer
(reduce_e190.py) and the frozen scorer (score_e190.py, unchanged), each run's reduced joules checked against what the doubles injected.
On a box with a card run it ONLY inside a sandbox with no /dev/et* and an empty /run/lock (case R2 runs the real runner, which must stop
at its box check before anything else).

    /usr/bin/python3 -B tools/claims-v3/e190/selftest_run_e190.py <scratch dir> [--only CASE ...] > selftest-run-e190.txt

Cases (the gates before any device; the stop lines on live samples; the gates between runs; the order; the refusals; end to end):
  G1 arm A's start config at 70 W: 16, the gate, no smoke process      G2 arm B's at 800 MHz: 16; arm A's at 800 MHz is no gate: it runs
  G3 the config read fails: 16                                          G4 the card's lock held: 16, no config read
  G5 et-who: another login on arm A's card: 16, no config read          G6 arm B: ours on card 0: 16; another login on card 0 only: no block
  G7 a device process of another user (A), of ours (B), a CI job (B): 16 each, no config read
  G8 the sampler will not start: 16, no smoke process                   G9 the stop-path test on a sampler with no board reading: 16
  G10 a smoke check of C wrong: 16, no run                              G11 a smoke process crashing with no check: 16, no run
  S1 arm A's board line (above 85 W on 3 live samples) in P1 fp32: the stop file touched, the host ends at its next launch boundary,
     nothing further starts, the tail read, the closing config, session end, the manifest
  S2 arm B's die line (the shires' mean at 80 C) in a run: the same     S3 the die line on the hottest sensor alone (the mean 70 C)
  S4 no trip at exactly 85.0 W, nor on 2 samples above it (arm A)      S5 arm B's line: 75.5 W on 3 samples trips
  D1 the die gate held above 55 C: each run skipped (NO DATA), the queue goes on, no process
  D2 the card-time rule: no run starts once it passes (a shortened rule, --dry only)
  H1 a host that hangs: `timeout 10` ends it (rc 124), flagged; H2 two crashing processes in one run: the session stops after them
  O1 THE ORDER: the whole plan (arm A, the durations scaled): the 18 runs in the registered order, 4 bursts and 2 sustained runs a
     format, 1 and 12 processes, each process's argv the registered one (--seconds 6 --budget 7.5, the format's --values)
  R1 the dry-only options refused without --dry, V3_DRY without --dry  R2 the REAL runner on the desk: it stops at its box check (16), no lock
  E1 END TO END at the forecast's points: both arms at once, the whole plan, a 6 s rest read (the reducer's rest window is the
     registered last 5 s before a run's first process), the doubles' leakage off: every run's reduced t_gemm the injected
     seconds within 0.2%, its J over idle (p_work - p_rest) t the injected watts x seconds within 2%; the frozen scorer reads R0, S1-S4,
     S6 PASS, S7 THE SAME SCALED, S8 STRICT (S5 is reported: the doubles' die is a toy)
  E2 END TO END with the watts 25% over (bursts only): S1 PASS, S2 FAIL, S3 FAIL
Every number here comes from the doubles (the frozen forecast's points driven through a toy card): a desk check of code, not a
measurement and not a reading of E190. SPDX-License-Identifier: Apache-2.0
"""
import fcntl
import gzip
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e190_common as C  # noqa: E402

PY = sys.executable
RUNNER = os.path.join(HERE, "run_e190.py")
FAST = ["--rest-s", "0.5", "--smoke-rest-s", "1.5", "--tail-s", "0.3", "--gate-wait-s", "3"]
BASE_ENV = {"E190_FAKE_SCALE": "0.1", "E190_FAKE_TAU_S": "0.5"}
N_SMOKE_LAUNCHES = 22          # the smoke's launches on the doubles (fp32 8, fp16 7, int8 7): an injection after them lands in the runs


class T:
    def __init__(self, scratch):
        self.s = scratch
        self.n = 0
        self.ok = 0
        self.lines = []

    def case(self, name, good, detail):
        self.n += 1
        self.ok += 1 if good else 0
        line = f"{name}: {'PASS' if good else 'FAIL'} - {detail}"
        self.lines.append(line)
        print(line, flush=True)

    def prep(self, name, arm, env=None, extra=None, seq="short", dry=True):
        d = os.path.join(self.s, name)
        e = dict(os.environ)
        for k in list(e):
            if k.startswith("E190_FAKE_") or k in ("V3_DRY", "ET_DEVICES", "V3_DEVICE"):
                e.pop(k)
        e.update(BASE_ENV)
        e.update(env or {})
        cmd = [PY, "-B", RUNNER, "session", "--arm", arm, "--t0", str(int(time.time())), "--out", d]
        if dry:
            cmd += ["--dry", "--sequence", seq] + FAST
        cmd += extra or []
        return d, e, cmd

    def session(self, name, arm, env=None, extra=None, seq="short", dry=True, timeout=900):
        d, e, cmd = self.prep(name, arm, env, extra, seq, dry)
        t0 = time.time()
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout, env=e, stdin=subprocess.DEVNULL)
        log = open(os.path.join(d, "session.log")).read() if os.path.exists(os.path.join(d, "session.log")) else ""
        return r.returncode, log, d, round(time.time() - t0, 1), r.stdout + r.stderr

    def sessions_parallel(self, specs, timeout=1800):
        """[(name, arm, env, extra, seq)] run at the same time (the two arms' own doubles and schedules); [(rc, d, seconds)]"""
        ps = []
        for name, arm, env, extra, seq in specs:
            d, e, cmd = self.prep(name, arm, env, extra, seq)
            ps.append((d, time.time(), subprocess.Popen(cmd, cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=e,
                                                         stdin=subprocess.DEVNULL)))
        out = []
        for d, t0, p in ps:
            try:
                rc = p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                p.terminate()
                rc = p.wait()
            out.append((rc, d, round(time.time() - t0, 1)))
        return out


def jl(p):
    return [json.loads(x) for x in open(p)] if os.path.exists(p) else []


def queue(d):
    p = os.path.join(d, "queue.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def has_proc(d):
    for dp, dn, fn in os.walk(d):
        if any(n.startswith("proc") and n.endswith(".out") for n in fn):
            return True
    return False


def run_dirs(d):
    rd = os.path.join(d, "runs")
    return sorted(os.listdir(rd)) if os.path.isdir(rd) else []


def inject(t, name, items):
    p = os.path.join(t.s, f"inject-{name}.json")
    json.dump(items, open(p, "w"))
    return p


def manifest_ok(d):
    m = os.path.join(d, "MANIFEST.sha256")
    return os.path.exists(m) and os.path.getsize(m) > 0


def gates(t):
    rc, log, d, s, _ = t.session("G1", "A", {"E190_FAKE_CONFIG": "tdp70"})
    t.case("G1", rc == 16 and "the gate, no launch" in log and not has_proc(d) and "session end" in log,
           f"rc {rc}; {'gate' if 'the gate, no launch' in log else 'NO GATE'}; smoke process {'started' if has_proc(d) else 'none'}")
    rc, log, d, s, _ = t.session("G2", "B", {"E190_FAKE_CONFIG": "mhz800"})
    rc2, log2, d2, s2, _ = t.session("G2a", "A", {"E190_FAKE_CONFIG": "mhz800"}, seq="short")
    t.case("G2", rc == 16 and "the gate, no launch" in log and not has_proc(d) and rc2 == 0 and "smoke gate passed" in log2,
           f"arm B rc {rc} (gate {'yes' if 'the gate' in log else 'no'}); arm A at 800 MHz rc {rc2}, smoke {'passed' if 'smoke gate passed' in log2 else 'NOT passed'}")
    rc, log, d, s, _ = t.session("G3", "A", {"E190_FAKE_CONFIG": "fail"})
    t.case("G3", rc == 16 and "config read rc" in log and not has_proc(d), f"rc {rc}")
    d4 = os.path.join(t.s, "G4")
    os.makedirs(d4, exist_ok=True)
    hold = open(os.path.join(d4, "dry.lock"), "a+")
    fcntl.flock(hold.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    rc, log, d, s, _ = t.session("G4", "A")
    hold.close()
    t.case("G4", rc == 16 and "lock is held" in log and not os.path.exists(os.path.join(d, "config-start.json")),
           f"rc {rc}; config read {'made' if os.path.exists(os.path.join(d, 'config-start.json')) else 'none'}")
    rc, log, d, s, _ = t.session("G5", "A", {"E190_FAKE_ETWHO": "other"})
    t.case("G5", rc == 16 and "no device opened" in log and not os.path.exists(os.path.join(d, "config-start.json")), f"rc {rc}")
    rc, log, d, s, _ = t.session("G6", "B", {"E190_FAKE_ETWHO": "ours0"})
    rc2, log2, d2, s2, _ = t.session("G6a", "B", {"E190_FAKE_ETWHO": "other0"})
    t.case("G6", rc == 16 and "ours on card 0" in log and rc2 == 0 and "smoke gate passed" in log2,
           f"ours on card 0: rc {rc}; another login on card 0 only: rc {rc2}, {'ran' if 'smoke gate passed' in log2 else 'did NOT run'}")
    res = []
    for arm, ps in (("A", "other"), ("B", "ours"), ("B", "ci")):
        rc, log, d, s, _ = t.session(f"G7-{arm}-{ps}", arm, {"E190_FAKE_PS": ps})
        res.append((arm, ps, rc, not os.path.exists(os.path.join(d, "config-start.json"))))
    t.case("G7", all(r[2] == 16 and r[3] for r in res), "; ".join(f"arm {a} {p}: rc {rc}, no config read {nc}" for a, p, rc, nc in res))
    rc, log, d, s, _ = t.session("G8", "A", {"E190_FAKE_SAMPLER": "dead"})
    t.case("G8", rc == 16 and "the sampler would not start" in log and not has_proc(d), f"rc {rc} after {s} s")
    rc, log, d, s, _ = t.session("G9", "A", {"E190_FAKE_SAMPLER": "noboard"})
    sp = json.load(open(os.path.join(d, "stop-path.json"))) if os.path.exists(os.path.join(d, "stop-path.json")) else {}
    t.case("G9", rc == 16 and "stop-path test failed" in log and not has_proc(d) and sp.get("lines", {}).get("board", {}).get("tripped") is False
           and sp.get("lines", {}).get("die", {}).get("tripped") is True,
           f"rc {rc}; board line tripped {sp.get('lines', {}).get('board', {}).get('tripped')}, die line {sp.get('lines', {}).get('die', {}).get('tripped')}")
    rc, log, d, s, _ = t.session("G10", "A", {"E190_FAKE_HOST": "wrong"})
    t.case("G10", rc == 16 and "smoke gate failed" in log and not run_dirs(d), f"rc {rc}; runs {len(run_dirs(d))}")
    rc, log, d, s, _ = t.session("G11", "B", {"E190_FAKE_HOST": "crash"})
    t.case("G11", rc == 16 and "smoke gate failed" in log and not run_dirs(d), f"rc {rc}; runs {len(run_dirs(d))}")


def stop_case(t, name, arm, items, want_line, run_key):
    rc, log, d, s, _ = t.session(name, arm, {"E190_FAKE_INJECT": inject(t, name, items)})
    q = queue(d)
    marks = jl(os.path.join(d, "marks.jsonl"))
    rj = os.path.join(d, "runs", run_key, "run.json")
    rec = json.load(open(rj)) if os.path.exists(rj) else {}
    errs = "".join(open(os.path.join(d, "runs", run_key, f)).read() for f in os.listdir(os.path.join(d, "runs", run_key))
                   if f.endswith(".err")) if os.path.isdir(os.path.join(d, "runs", run_key)) else ""
    after = [x for x in q.get("queue", []) if not x.get("ran")]
    tel = [json.loads(x) for x in gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt")] if os.path.exists(os.path.join(d, "telemetry.jsonl.gz")) else []
    t_trip = marks[0]["t_ms"] if marks else None
    ends = [p["t1_ms"] for p in rec.get("procs", [])]
    good = (rc == 0 and bool(marks) and want_line in (marks[0]["detail"] if marks else "") and os.path.exists(os.path.join(d, "STOP"))
            and "stopping:" in errs and len(run_dirs(d)) == 1 and after and all("after a stop" in x.get("why", "") for x in after)
            and "STOP:" in log and "config end" in log and "session end" in log and manifest_ok(d)
            and rec.get("tail_end_ms", 0) - rec.get("work", {}).get("t1_ms", 0) >= 250 and ends and ends[-1] - t_trip <= 3000)
    return good, (f"rc {rc}; trip '{marks[0]['detail'] if marks else None}'; the host stopped by the file: {'stopping:' in errs}; process "
                  f"ended {ends[-1] - t_trip if ends and t_trip else None} ms after the trip; runs started {len(run_dirs(d))}, not started after it "
                  f"{len(after)}; tail {rec.get('tail_end_ms', 0) - rec.get('work', {}).get('t1_ms', 0)} ms; closing config "
                  f"{'read' if 'config end' in log else 'NOT read'}; manifest {manifest_ok(d)}; samples {len(tel)}")


def stops(t):
    n = N_SMOKE_LAUNCHES + 4
    good, det = stop_case(t, "S1", "A", [{"board_w": 90.0, "after_launches": n, "count": 5}], "board 90.0 W above 85 W on 3 samples", "01-P1-burst-fp32")
    t.case("S1", good, det)
    good, det = stop_case(t, "S2", "B", [{"die": 80, "after_launches": n, "count": 2}], "die 80 C at or above 80 C", "01-P1-burst-fp32")
    t.case("S2", good, det)
    good, det = stop_case(t, "S3", "A", [{"die": 70, "high": 80, "after_launches": n, "count": 2}], "the hottest 80", "01-P1-burst-fp32")
    t.case("S3", good, det)
    rc, log, d, s, _ = t.session("S4", "A", {"E190_FAKE_INJECT": inject(t, "S4", [{"board_w": 85.0, "after_launches": n, "count": 8},
                                                                                 {"board_w": 85.5, "after_launches": n + 12, "count": 2}])})
    q = queue(d)
    t.case("S4", rc == 0 and not os.path.exists(os.path.join(d, "STOP")) and not jl(os.path.join(d, "marks.jsonl"))
           and all(x.get("ran") for x in q.get("queue", [])) and len(q.get("queue", [])) == 4,
           f"rc {rc}; STOP file {'present' if os.path.exists(os.path.join(d, 'STOP')) else 'absent'}; runs {sum(1 for x in q.get('queue', []) if x.get('ran'))} of {len(q.get('queue', []))}")
    good, det = stop_case(t, "S5", "B", [{"board_w": 75.5, "after_launches": n, "count": 4}], "board 75.5 W above 75 W on 3 samples", "01-P1-burst-fp32")
    t.case("S5", good, det)


def gates_between(t):
    rc, log, d, s, _ = t.session("D1", "A", {"E190_FAKE_INJECT": inject(t, "D1", [{"die": 60, "after_launches": N_SMOKE_LAUNCHES - 4, "count": 100000}])},
                                 extra=["--gate-wait-s", "1.5"])
    q = queue(d)
    sk = [x for x in q.get("queue", []) if not x.get("ran")]
    t.case("D1", rc == 0 and len(sk) == 4 and all("the die gate" in x.get("why", "") for x in sk) and not run_dirs(d),
           f"rc {rc}; skipped by the die gate {sum(1 for x in sk if 'the die gate' in x.get('why', ''))} of {len(q.get('queue', []))}; run directories {len(run_dirs(d))}")
    rc, log, d, s, _ = t.session("D2", "A", extra=["--rule-s", "7"])
    q = queue(d)
    ran = [x for x in q.get("queue", []) if x.get("ran")]
    ruled = [x for x in q.get("queue", []) if not x.get("ran") and "card-time rule" in x.get("why", "")]
    t.case("D2", rc == 0 and ran and ruled and all(not x.get("ran") for x in q["queue"][q["queue"].index(ruled[0]):]),
           f"rc {rc}; ran {len(ran)}, refused by the rule {len(ruled)}")


def hosts(t):
    n = N_SMOKE_LAUNCHES
    rc, log, d, s, _ = t.session("H1", "A", {"E190_FAKE_HOST": "hang", "E190_FAKE_HOST_FROM_N": str(n), "E190_FAKE_HOST_COUNT": "1"},
                                 timeout=300)
    rj = json.load(open(os.path.join(d, "runs", "01-P1-burst-fp32", "run.json"))) if os.path.exists(os.path.join(d, "runs", "01-P1-burst-fp32", "run.json")) else {}
    q = queue(d)
    t.case("H1", rc == 0 and [p["rc"] for p in rj.get("procs", [])] == [124] and any("rc 124" in f for f in rj.get("flags", []))
           and sum(1 for x in q.get("queue", []) if x.get("ran")) == 4 and not q.get("stop"),
           f"rc {rc}; P1 fp32's process rc {[p['rc'] for p in rj.get('procs', [])]}, after {s} s; the queue went on: {sum(1 for x in q.get('queue', []) if x.get('ran'))} runs")
    rc, log, d, s, _ = t.session("H2", "A", {"E190_FAKE_HOST": "crash", "E190_FAKE_HOST_FROM_N": str(n + 40)})
    q = queue(d)
    sus = os.path.join(d, "runs", "04-S1-sus-fp32", "run.json")
    rj = json.load(open(sus)) if os.path.exists(sus) else {}
    t.case("H2", rc == 0 and "two processes of run 04-S1-sus-fp32 failed" in (q.get("stop") or "") and len(rj.get("procs", [])) == 2,
           f"rc {rc}; stop '{q.get('stop')}'; S1's processes {len(rj.get('procs', []))}")


def order(t):
    rc, log, d, s, _ = t.session("O1", "A", {"E190_FAKE_SCALE": "0.05"}, seq="plan", timeout=1200)
    q = queue(d)
    keys = [x["run"] for x in q.get("queue", [])]
    want = [f"{i:02d}-{b}-{k}-{f}" for i, b, k, f, r in C.sequence()]
    nproc, argv_ok = {}, True
    for k in run_dirs(d):
        rj = json.load(open(os.path.join(d, "runs", k, "run.json")))
        nproc[k] = len(rj.get("procs", []))
        for p in rj.get("procs", []):
            a = p["argv"]
            sec, bud, _ = C.proc_form(rj["kind"])
            argv_ok = argv_ok and a[a.index("--seconds") + 1] == f"{sec:g}" and a[a.index("--budget") + 1] == f"{bud:g}" and \
                a[a.index("--values") + 1] == C.values(rj["format"]) and a[a.index("--type") + 1] == rj["format"] and \
                a[a.index("--stop-file") + 1] == os.path.join(d, "STOP") and a[0].endswith(C.HOST) and a[a.index("--kernel") + 1].endswith(C.ELF)
    cells = {}
    for i, b, k, f, r in C.sequence():
        cells[f"{f}.{k}"] = cells.get(f"{f}.{k}", 0) + 1
    good = rc == 0 and keys == want and all(x.get("ran") for x in q.get("queue", [])) and \
        all(nproc.get(k) == (12 if "-sus-" in k else 1) for k in want) and argv_ok and cells == {f"{f}.{k}": (4 if k == "burst" else 2) for f in C.FMTS for k in C.KINDS}
    t.case("O1", good, f"rc {rc} after {s} s; {len(keys)} runs in the registered order: {keys == want}; processes a run "
                       f"{sorted(set(nproc.values()))}; every argv the registered one: {argv_ok}; card minutes (scaled) {q.get('card_min')}")
    return d


def refusals(t):
    out = []
    for extra, env in ((["--rest-s", "1"], {}), (["--sequence", "short"], {}), ([], {"V3_DRY": "1"})):
        e = dict(os.environ, **env)
        r = subprocess.run([PY, "-B", RUNNER, "session", "--arm", "A", "--t0", "1", "--out", os.path.join(t.s, "R1x")] + extra,
                           cwd=REPO, capture_output=True, text=True, env=e, timeout=60)
        out.append((extra or env, r.returncode, r.stdout.strip()[:80]))
    t.case("R1", all(rc == 2 and o.startswith("refused") for _, rc, o in out), "; ".join(f"{a}: rc {rc}" for a, rc, o in out))
    rc, log, d, s, txt = t.session("R2", "A", dry=False, timeout=120)
    rcb, logb, db, sb, _ = t.session("R2b", "B", dry=False, timeout=120)
    t.case("R2", rc == 16 and "no device opened" in log and not os.path.exists(os.path.join(d, "config-start.json")) and
           rcb == 16 and "not arm B's 'aifoundry1'" in logb,
           f"arm A on this desk: rc {rc}, '{[ln for ln in log.splitlines() if 'no device opened' in ln][:1]}'; arm B: rc {rcb}")


def e2e(t, name, wscale, seq, scale):
    env = {"E190_FAKE_LEAK": "0", "E190_FAKE_W_SCALE": str(wscale), "E190_FAKE_SCALE": str(scale), "E190_FAKE_TAU_S": "0.4"}
    # the rest read at 6 s: the reducer's rest window is the registered last 5 s before a run's first process, so it must be rest
    res = t.sessions_parallel([(f"{name}-{arm}", arm, env, ["--rest-s", "6"], seq) for arm in ("A", "B")])
    sess = {"A": res[0], "B": res[1]}
    data = os.path.join(t.s, f"{name}-data.json")
    r = subprocess.run([PY, "-I", "-B", os.path.join(HERE, "reduce_e190.py"), "--arm", f"A={sess['A'][1]}", "--arm", f"B={sess['B'][1]}",
                        "--out", data, "--txt", os.path.join(t.s, f"{name}-reduce.txt")], cwd=REPO, capture_output=True, text=True, timeout=300)
    D = json.load(open(data)) if os.path.exists(data) else {"arms": {}}
    fc = C.forecast()
    worst_t, worst_j, n = 0.0, 0.0, 0
    for arm, A in D["arms"].items():
        f = C.ARMS[arm]["clock_mhz"]
        for cell, c in A["cells"].items():
            fmt, kind = cell.split(".")
            t_inj = fc["speed"][fmt][f"t{f}_s"]["point"]
            w_inj = fc["cells"][f"{arm}.{fmt}.{kind}"]["W_over"]["point"] * wscale
            for run in c["runs"]:
                n += 1
                worst_t = max(worst_t, abs(run["t_gemm_s"] / t_inj - 1))
                worst_j = max(worst_j, abs((run["p_work_w"] - run["p_rest_w"]) * run["t_gemm_s"] / (w_inj * t_inj) - 1))
    sc_out = os.path.join(t.s, f"{name}-scored.json")
    r2 = subprocess.run([PY, "-I", "-B", os.path.join(HERE, "score_e190.py"), data, "--out", sc_out], cwd=REPO, capture_output=True,
                        text=True, timeout=300)
    S = json.load(open(sc_out)) if os.path.exists(sc_out) else {"rules": {}}
    v = {k: (x.get("verdict") or x.get("reading")) for k, x in S["rules"].items()}
    return sess, n, worst_t, worst_j, v, r.returncode, r2.returncode


def end_to_end(t):
    sess, n, wt, wj, v, rr, rs = e2e(t, "E1", 1.0, "plan", 0.1)
    want = {"R0": "PASS", "S1": "PASS", "S2": "PASS", "S3": "PASS", "S4": "PASS", "S6": "PASS", "S7": "THE SAME SCALED", "S8": "STRICT"}
    good = all(sess[a][0] == 0 for a in "AB") and n == 36 and wt <= 0.002 and wj <= 0.02 and all(v.get(k) == w for k, w in want.items()) and rr == 0 and rs == 0
    t.case("E1", good, f"sessions rc {sess['A'][0]}, {sess['B'][0]} ({sess['A'][2]} s, {sess['B'][2]} s); {n} runs reduced; worst |t / injected - 1| "
                       f"{wt:.2e}, worst |J over idle / injected - 1| {wj:.2%}; the scorer: {v}")
    sess, n, wt, wj, v, rr, rs = e2e(t, "E2", 1.25, "bursts", 0.1)
    good = all(sess[a][0] == 0 for a in "AB") and n == 24 and v.get("S1") == "PASS" and v.get("S2") == "FAIL" and v.get("S3") == "FAIL"
    t.case("E2", good, f"sessions rc {sess['A'][0]}, {sess['B'][0]}; {n} runs reduced; worst |J over idle / injected - 1| {wj:.2%}; the scorer: {v}")


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    s = os.path.abspath(argv[0])
    if s == REPO or s.startswith(REPO + os.sep):
        print("the scratch directory must be outside the repository")
        return 2
    if os.path.exists(s) and os.listdir(s):
        print(f"{s} is not empty")
        return 2
    os.makedirs(s, exist_ok=True)
    only = argv[argv.index("--only") + 1:] if "--only" in argv else None
    t = T(s)
    devs = [x for x in os.listdir("/dev") if x.startswith("et")]
    print(f"selftest_run_e190 ({PY} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; /dev/et*: {devs or 'none'}; "
          f"/run/lock entries: {len(os.listdir('/run/lock')) if os.path.isdir('/run/lock') else 'no /run/lock'}", flush=True)
    if devs:
        print("REFUSED: a /dev/et* node is visible: run this inside the sandbox (no /dev/et*, an empty /run/lock)")
        return 3
    for name, fn in (("G", gates), ("S", stops), ("D", gates_between), ("H", hosts), ("O", order), ("R", refusals), ("E", end_to_end)):
        if only and name not in only:
            continue
        fn(t)
    print(f"SELFTEST-RUN-E190 {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
