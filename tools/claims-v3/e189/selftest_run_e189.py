#!/usr/bin/env python3
"""E189's runner desk test (Q167, the kit, Thu 12 Nov 2026, before any E189 datum; fixed Fri 13 Nov 2026, fix-e189b): run_e189.py in --dry
sessions with fake_card_e189.py's doubles, on the desk (the Intel or aifoundry2; on a box with a card, inside a sandbox with no /dev/et* and
an empty /run/lock); no box, no device, no ssh. THE STOP PATH: a desk case that trips each line, plus every gate.

    /usr/bin/python3 -B tools/claims-v3/e189/selftest_run_e189.py <scratch dir outside the repo> [--no-e2e]

Cases (each a whole dry session; the doubles' launches are scaled to 5% of the forecast's seconds, idles to 0.5 s; verdicts stated first):
  R1  plain: the stop-path test passes, the ramped smoke passes, six passes run, each in E189.md 8.1's form, session end, a manifest;
  R2  THE BOARD LINE: 66 W on a sample during a pass's launch: the running process finishes (its line is there), the queue ends, no
      further pass, the closing read; the pass is flagged, and its idle after the host runs whole (fault 2);
  R3  THE DIE LINE: minshire[0] 70 C during a pass's launch: the same;
  R4  THE CLOCK LINE, first sample: one sample at 800 MHz during a pass's launch sets that pass aside; the session goes on (six passes);
  R5  THE CLOCK LINE, second sample: two such samples: the pass set aside and the session stopped;
  R6  THE DIE GATE: minshire[0] 62 C for 3 s from the first pass's first launch: the next pass waits 2 s (the desk's bound) and is
      skipped (no data); later passes run; no stop;
  R7  THE CAP: the cap set to 6 s: passes after it are not started ("the cap"), the session ends normally;
  R8  the start config not TDP 0 W (5 W): the gate, no smoke, no pass, rc 16;
  R9  a holder of another login (et-who): no device opened, rc 16;
  R10 a failed smoke run (a mismatch): smoke gate failed, no pass, rc 16;
  R11 a burst the budget cuts short (6 of 8 launches): every ledger pass's host.json says "reps: 6 of 8 done" (scored, flagged SHORT);
  R12 a FAILED RUN in a pass (a mismatch): its host.json reps_consistent bad, problems "checks: ...";
  R13 card 0's lock held by another process: no device opened, rc 16;
  R14 only sparse parity built: the ledger passes SKIPPED, the smoke runs sparse parity only;
  R15 the runner refuses the desk's overrides (--cap-end-s among them) and V3_DRY without --dry (rc 2, nothing started);
  R16 the stop-path test cannot trip (a sampler that never starts): no launch;
  R18 THE END BOUND, the closing: a sampler that ignores its first SIGTERM, the desk's cap 6 s and end bound 20 s: the closing waits on it
      only to 15 s before the bound (at least 2 s), SIGTERMs it once more, reads the config, and the session closes within 20 s of the
      first card command (the first kit waited 30 s, then 60 s: about 38 s here);
  R19 THE END BOUND, the die gate: minshire[0] 62 C from the first pass's first launch on, the registered 10-minute die wait, the desk's
      cap 8 s: the die gate stops waiting at the cap ("the cap", in the die gate's wait) and the session closes within 60 s (the first kit
      waited the whole 10 minutes past the cap);
  E2E energy_stub.py's alt sampler, the registered 8 s / 10 s idles, two passes each of copy-zeros, sha256 and sparse parity; then the
      collection's desk half on a copy of the session (collect_e189.py: COPY-BACK EXACT, the data folder, every pass reduced by
      energy_reduce.py, unchanged, with no hard check failed and its "dir" set to the folder's own path, the scrub of a stand-in box home,
      SHA256SUMS), then score_e189.py (frozen) on the collected folder: three configurations scored, three NO DATA. FIXED (verify-e189's
      fault 1): the doubles announce each launch at its start, and EACH PASS'S REDUCED J OVER IDLE A LAUNCH is checked against the
      energy the alt card injected (the schedule's launches, less the card's 5 ms and 3 ms edges), within TOL(c) = 3% (the reducer's
      claim) + 0.33 W/C x (K t_point + 7 s) / (K J_point): one whole degree of the die reading, at the reducer's leakage slope near
      55 C, over the long window [lo - 1 s, hi + 6 s], as a share of the burst's injected energy (copy 12.8%, SHA-256 22.3%, sparse
      parity 8.8%; the low-power burst carries the widest share); and the verdict words: by construction t_k is the point and J over
      idle the point, so with three configurations scored and three NO DATA the right word for E189-S1 and E189-S2 is NOT DECIDED (PASS
      needs 5 scored, FAIL 2 outside); E189-S1T and E189-S2T compare J with the card at rest, and the alt card idles about 2 W below
      the footing law the forecast's rest term uses, so their words carry no information here: each must only be one of the three words;
  R2E THE BOARD LINE, REDUCED AND SCORED (fault 2): the alt card under the injections (E189_FAKE_BASE=alt), the registered idles, 66 W on
      a sample during copy-zeros p2 (the 27th pass launch): the running process finishes, its pass keeps its whole 10 s after (no
      "telemetry ends" flag), the queue ends; the collection reduces all four passes, the stopped pass's J over idle within TOL of what
      the card injected, and the scorer scores copy-zeros on its two passes, the stopped one among them; THE CUT TAIL (a control): the
      same pass's telemetry cut 0.5 s after its host, where the first kit cut it, reduced: flagged and lower by more than 3%;
  R3E THE DIE LINE, REDUCED AND SCORED: the same with minshire[0] 70 C during sha256 p2 (the 35th pass launch): five passes; SHA-256 scored
      on its two passes, the stopped one among them, within TOL.
Prints SELFTEST-RUN-E189 <n> of <m> PASS or FAIL; exit 0 or 1. SPDX-License-Identifier: Apache-2.0
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
RUN = os.path.join(HERE, "run_e189.py")
REDUCER = os.path.join(REPO, "workloads", "sparseparity", "tools", "energy_reduce.py")
PY = "/usr/bin/python3"
FAST = ["--sequence", "short", "--idle-before", "0.5", "--idle-after", "0.5", "--anchor-s", "0.5", "--die-wait-s", "2"]
EDGES = {"alt": (0.005, 0.003), "base": (0.0, 0.0)}     # energy_stub.py: the card's power starts 5 ms after a launch, ends 3 ms before
results = []


def ok(cond, what):
    results.append(bool(cond))
    print(f"-> {'PASS' if cond else 'FAIL'} ({what})", flush=True)


def session(S, name, env=None, inject=None, extra=None, seq_args=None, double="inject", t0=None):
    d = os.path.join(S, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    e = dict(os.environ, E189_FAKE_SCALE="0.05")
    e.pop("V3_DRY", None)
    if inject is not None:
        p = os.path.join(d, "inject.json")
        with open(p, "w") as f:
            json.dump(inject, f)
        e["E189_FAKE_INJECT"] = p
    e.update(env or {})
    out = os.path.join(d, "T")
    argv = [PY, "-I", "-B", RUN, "session", "--dry", "--double", double, "--t0", str(t0 or 1794600000), "--out", out] + \
        (seq_args if seq_args is not None else FAST) + (extra or [])
    r = subprocess.run(argv, cwd=REPO, env=e, capture_output=True, text=True, timeout=1800)
    log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
    q = {}
    if os.path.exists(os.path.join(out, "queue.json")):
        q = json.load(open(os.path.join(out, "queue.json")))
    print(f"   [{name}] rc {r.returncode}; " + " | ".join(ln.split(" ", 3)[-1] for ln in log.splitlines()
                                                         if any(w in ln for w in ("STOP", "gate", "stop-path", "SET ASIDE",
                                                                                 "not started", "skipped", "SKIPPED", "no device",
                                                                                 "SIGTERM", "not restarted"))))
    return r, out, log, q


def passes_ran(q):
    return [x for x in q.get("queue", []) if x.get("ran")]


def pj(out, key):
    p = os.path.join(out, "passes", key, "pass.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def rj(out, key):
    p = os.path.join(out, "passes", key, "run.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def idle_after_ms(out, key):
    """From the host process's end to the pass's end (the idle after the host, as the runner kept it)."""
    return (pj(out, key).get("t_end_ms") or 0) - (rj(out, key).get("host_t1_ms") or 0)


def injected(out, key, card="alt"):
    """(J over idle a launch the card injected, launches): the schedule's pass launches inside the pass's host process, each its watts
    times its length less the card's edges (energy_stub.py: power from 5 ms after the launch mark to 3 ms before its end mark)."""
    run = rj(out, key)
    a, b = run.get("host_t0_ms", 0) / 1000.0, run.get("host_t1_ms", 0) / 1000.0
    e0, e1 = EDGES[card]
    rows = [json.loads(ln) for ln in open(os.path.join(out, "fake_sched.jsonl")) if ln.startswith("{")]
    ls = [x for x in rows if x.get("tag") == "pass" and a <= x["t0"] <= b]
    if not ls:
        return None, 0
    return sum(x["dp"] * max(0.0, (x["t1"] - e1) - (x["t0"] + e0)) for x in ls) / len(ls), len(ls)


def tol(cfg):
    """TOL(c) (the module docstring): 3% + one whole degree at 0.33 W/C over the long window, as a share of the burst's injected J."""
    fc = json.load(open(os.path.join(HERE, "forecast-e189.json")))["configs"][cfg]
    K = json.load(open(os.path.join(HERE, "plan-e189.json")))["configs"][cfg]["launches_K"]
    return 0.03 + 0.33 * (K * fc["seconds"]["point"] + 7.0) / (K * fc["j_over_idle"])


def collect_score(S, name, out):
    """The collection's desk half on a copy of the session (as the box would leave it), then the frozen scorer on the collected folder."""
    cp = os.path.join(S, name, "copy")
    shutil.copytree(out, cp)
    os.remove(os.path.join(cp, "dry.lock"))     # --dry's own lock file, which the manifest leaves out (a real session locks /run/lock's)
    open(os.path.join(cp, "runner.rc"), "w").write("0\n")
    data = os.path.join(S, name, "2026-11-13-e189-blind-day-aifoundry3")
    rc_ = subprocess.run([PY, "-B", os.path.join(HERE, "collect_e189.py"), cp, data, "--box-home", os.path.expanduser("~"),
                          "--data-outside"], cwd=REPO, capture_output=True, text=True, timeout=900, env=dict(os.environ, RB_DESKTEST="1"))
    print("   " + "\n   ".join(ln for ln in rc_.stdout.splitlines() if ln.startswith(("COPY-BACK", "COLLECTED", "SCRUB", "REDUCER"))))
    home = os.path.expanduser("~").encode()
    left = [os.path.join(dp, n) for dp, dn, fn in os.walk(data) for n in fn
            if home in (gzip.decompress(open(os.path.join(dp, n), "rb").read()) if n.endswith(".gz")
                        else open(os.path.join(dp, n), "rb").read())]
    print(f"   files holding the stand-in box home after the scrub: {len(left)}")
    sc = os.path.join(S, name, "scores.json")
    rs = subprocess.run([PY, "-B", os.path.join(HERE, "score_e189.py"), data, "--out", sc], cwd=REPO, capture_output=True,
                        text=True, timeout=600)
    sj = json.load(open(sc)) if os.path.exists(sc) else {}
    return rc_.returncode == 0 and "COLLECTED" in rc_.stdout and not left, data, sj, rs.returncode


def energy(data, key):
    p = os.path.join(data, "passes", key, "energy.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def check_energies(out, data, keys, card="alt"):
    """Each pass's reduced J over idle a launch against the injected, within TOL of its configuration; prints each row."""
    good = True
    for key in keys:
        cfg = key.split("/")[0]
        en = energy(data, key)
        j = (en.get("board") or {}).get("j_per_solve")
        inj, n = injected(out, key, card)
        e = (j / inj - 1.0) if (j is not None and inj) else None
        within = e is not None and abs(e) <= tol(cfg)
        good = good and within
        print(f"   {key}: reduced {j if j is None else round(j, 4)} J a launch over idle, injected {inj if inj is None else round(inj, 4)}"
              f" ({n} launches): {'n/a' if e is None else f'{100 * e:+.1f}%'} against TOL {100 * tol(cfg):.1f}%: "
              f"{'within' if within else 'OUTSIDE'}; ok {en.get('ok')}, hard {en.get('hard')}")
    return good


def cut_tail_control(S, name, data, key):
    """The first kit's cut: the stopped pass's telemetry kept only to 0.5 s after its host, reduced by the unchanged reducer."""
    src = os.path.join(data, "passes", key)
    d = os.path.join(S, name, "cut-tail", key.replace("/", "-"))
    if os.path.isdir(d):
        shutil.rmtree(d)
    shutil.copytree(src, d)
    os.remove(os.path.join(d, "energy.json"))
    h1 = json.load(open(os.path.join(d, "run.json")))["host_t1_ms"]
    rows = [ln for ln in gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt") if ln.startswith("{")]
    keep = [ln for ln in rows if json.loads(ln)["t_ms"] <= h1 + 500]
    with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "wt") as g:
        g.writelines(keep)
    r = subprocess.run([PY, "-B", REDUCER, d], cwd=REPO, capture_output=True, text=True, timeout=300)
    en = json.load(open(os.path.join(d, "energy.json"))) if os.path.exists(os.path.join(d, "energy.json")) else {}
    print(f"   the cut tail ({len(keep)} of {len(rows)} samples kept): reducer rc {r.returncode}, J over idle a launch "
          f"{(en.get('board') or {}).get('j_per_solve')}, flags {[f for f in en.get('flags', []) if 'telemetry ends' in f]}")
    return en


def main(S, e2e=True):
    print("== R1 plain dry session (doubles)")
    r, out, log, q = session(S, "r1")
    ran = passes_ran(q)
    form = all(os.path.exists(os.path.join(out, "passes", x["pass"], f)) for x in ran
               for f in ("telemetry.jsonl.gz", "host.json", "run.json", "pass.json"))
    form = form and all(os.path.exists(os.path.join(out, "passes", f"{c}/p1", "host-raw.json"))
                        for c in ("copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled"))
    ok(r.returncode == 0 and "stop-path test passed" in log and "smoke gate passed: queue starts" in log and len(ran) == 6
       and form and "DRY session end (T0" in log and os.path.exists(os.path.join(out, "MANIFEST.sha256"))
       and log.splitlines()[0].endswith(" DRY"), "six passes in 8.1's form, the stop-path test and the smoke passed, DRY marks")
    tel = [json.loads(ln) for ln in gzip.open(os.path.join(out, "passes", "copy-zeros", "p1", "telemetry.jsonl.gz"), "rt")]
    h = json.load(open(os.path.join(out, "passes", "copy-zeros", "p1", "run.json")))
    ok(tel and tel[0]["t_ms"] < h["host_t0_ms"] and tel[-1]["t_ms"] > h["host_t1_ms"], "a pass's telemetry spans its idle brackets")

    for name, inj, word in (("r2", [{"during": "pass", "board_w": 66.0, "count": 1}], "STOP: board 66.0 W at or above 65 W"),
                            ("r3", [{"during": "pass", "die": 70, "count": 1}], "STOP: minshire[0] 70 C at or above 70 C")):
        print(f"== {name.upper()} the {'board' if name == 'r2' else 'die'} line on a live sample during a pass")
        r, out, log, q = session(S, name, inject=inj)
        ran = passes_ran(q)
        last = ran[-1]["pass"] if ran else None
        lp = pj(out, last) if last else {}
        hraw = os.path.join(out, "passes", last, "host-raw.json" if not last.startswith("sparse") else "host.json") if last else ""
        ia = idle_after_ms(out, last) if last else 0
        print(f"   the stopped pass {last}: {ia} ms from its host's end to its end (its idle after: 500 ms)")
        ok(r.returncode == 0 and word in log and 1 <= len(ran) < 6 and lp.get("flags") and "stop line tripped" in lp["flags"][0]
           and os.path.getsize(hraw) > 10 and "config end:" in log and "DRY session end" in log and ia >= 450,
           "the running process finished (its line kept), its idle after whole, the queue ended, the pass flagged, the closing read")

    print("== R4 the clock line, ONE sample off 600 MHz during a pass: that pass set aside, the session goes on")
    r, out, log, q = session(S, "r4", inject=[{"during": "pass", "mhz": 800, "count": 1}])
    sa = [x for x in passes_ran(q) if x.get("set_aside")]
    ok(r.returncode == 0 and len(passes_ran(q)) == 6 and len(sa) == 1 and "800 MHz" in sa[0]["set_aside"]
       and "STOP" not in log, "one pass set aside, six passes ran, no stop")
    print("== R5 the clock line, a SECOND sample off 600 MHz in a pass: the session stops")
    r, out, log, q = session(S, "r5", inject=[{"during": "pass", "mhz": 800, "count": 2}])
    sa = [x for x in passes_ran(q) if x.get("set_aside")]
    ok(r.returncode == 0 and "STOP: a second sample off 600 MHz in a pass" in log and len(sa) == 1 and len(passes_ran(q)) < 6,
       "the pass set aside and the queue stopped")
    print("== R6 the die gate: 62 C for 3 s from the first pass's first launch; the bound 2 s")
    r, out, log, q = session(S, "r6", inject=[{"after_pass_launches": 1, "die": 62, "for_s": 3}])
    sk = [x for x in q.get("queue", []) if not x.get("ran") and str(x.get("why", "")).startswith("die gate")]
    ok(r.returncode == 0 and len(sk) >= 1 and len(passes_ran(q)) >= 3 and "STOP" not in log,
       "a pass skipped by the die gate (no data), later passes ran, no stop")
    print("== R7 the cap (6 s on the desk; 108 card-minutes on the box)")
    r, out, log, q = session(S, "r7", extra=["--cap-pass-s", "6"])
    nc = [x for x in q.get("queue", []) if not x.get("ran") and "the cap" in str(x.get("why", ""))]
    ok(r.returncode == 0 and len(nc) >= 1 and "DRY session end" in log, "passes after the cap not started")
    print("== R8 the start config is not TDP 0 W")
    r, out, log, q = session(S, "r8", env={"E189_FAKE_CONFIG": "tdp5"})
    ok(r.returncode == 16 and "the gate, no launch" in log and "smoke" not in log and not passes_ran(q), "the gate, rc 16")
    print("== R9 a holder of another login")
    r, out, log, q = session(S, "r9", env={"E189_FAKE_ETWHO": "held"})
    ok(r.returncode == 16 and "no device opened" in log and "config start" not in log, "no device opened, rc 16")
    print("== R10 a failed smoke run")
    r, out, log, q = session(S, "r10", env={"E189_FAKE_HOST": "fail"})
    ok(r.returncode == 16 and "smoke gate failed" in log and not passes_ran(q), "smoke gate failed, no pass")
    print("== R11 a burst the budget cuts short")
    r, out, log, q = session(S, "r11", env={"E189_FAKE_HOST": "short"})
    h = json.load(open(os.path.join(out, "passes", "copy-zeros", "p1", "host.json"))) if r.returncode == 0 else {}
    ok(r.returncode == 0 and h.get("problems") == ["reps: 6 of 8 done"] and h.get("reps_consistent") == "ok"
       and h.get("reps_done") == 6, "host.json says 'reps: 6 of 8 done' (SHORT, scored)")
    print("== R12 a FAILED RUN in a pass")
    r, out, log, q = session(S, "r12", env={"E189_FAKE_HOST": "fail-pass"})
    h = json.load(open(os.path.join(out, "passes", "sha256", "p1", "host.json"))) if r.returncode == 0 else {}
    ok(r.returncode == 0 and h.get("reps_consistent") == "bad" and h.get("problems", [""])[0].startswith("checks:"),
       "reps_consistent bad, problems name the checks (the reducer fails it: not a datum)")
    print("== R13 card 0's lock held by another process")
    d = os.path.join(S, "r13")
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "T"))
    hold = open(os.path.join(d, "T", "dry.lock"), "a+")
    fcntl.flock(hold.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    e = dict(os.environ, E189_FAKE_SCALE="0.05")
    r = subprocess.run([PY, "-I", "-B", RUN, "session", "--dry", "--t0", "1", "--out", os.path.join(d, "T")] + FAST, cwd=REPO,
                       env=e, capture_output=True, text=True, timeout=300)
    hold.close()
    log = open(os.path.join(d, "T", "session.log")).read()
    ok(r.returncode == 16 and "lock is held: no device opened" in log, "no device opened, rc 16")
    print("== R14 only sparse parity built today")
    r, out, log, q = session(S, "r14", extra=["--programs", "spp"])
    sk = [x for x in q.get("queue", []) if "SKIPPED" in str(x.get("why", ""))]
    ok(r.returncode == 0 and len(sk) == 5 and len(passes_ran(q)) == 1 and "smoke ledger" not in log
       and "smoke sparse-parity-r1" in log, "five ledger passes SKIPPED, sparse parity's ran, its smoke alone")
    print("== R15 the desk's overrides and V3_DRY are refused without --dry")
    r1 = subprocess.run([PY, "-I", "-B", RUN, "session", "--t0", "1", "--out", os.path.join(S, "r15a"), "--idle-before", "1"],
                        cwd=REPO, capture_output=True, text=True, timeout=60)
    r2 = subprocess.run([PY, "-I", "-B", RUN, "session", "--t0", "1", "--out", os.path.join(S, "r15b")], cwd=REPO,
                        capture_output=True, text=True, timeout=60, env=dict(os.environ, V3_DRY="1"))
    r3 = subprocess.run([PY, "-I", "-B", RUN, "session", "--t0", "1", "--out", os.path.join(S, "r15c"), "--cap-end-s", "20"],
                        cwd=REPO, capture_output=True, text=True, timeout=60)
    ok(r1.returncode == 2 and "refused" in r1.stdout and r2.returncode == 2 and r3.returncode == 2 and "--cap-end-s" in r3.stdout
       and not any(os.path.exists(os.path.join(S, x)) for x in ("r15a", "r15b", "r15c")), "rc 2 each, nothing started")
    print("== R16 a sampler that never starts: the stop path cannot be shown, no launch")
    r, out, log, q = session(S, "r16", env={"E189_FAKE_SAMPLER": "dead"})
    ok(r.returncode == 16 and "the sampler would not start: no launch" in log and "smoke" not in log, "no launch, rc 16")
    print("== R18 THE END BOUND, the closing: a sampler that ignores its first SIGTERM; the desk's cap 6 s, end bound 20 s")
    r, out, log, q = session(S, "r18", env={"E189_FAKE_SAMPLER": "stubborn"}, extra=["--cap-pass-s", "6", "--cap-end-s", "20"])
    span = ((q.get("t_close_ms") or 0) - (q.get("t_first_ms") or 0)) / 1000.0
    print(f"   from the first card command to the close: {span:.1f} s (the end bound 20 s)")
    ok(r.returncode == 0 and "SIGTERM once more" in log and "left running" not in log and "config end: TDP 0 W" in log
       and "DRY session end" in log and 0 < span <= 20.0, "the closing bounded: the second SIGTERM, the closing read, closed by the bound")
    print("== R19 THE END BOUND, the die gate: 62 C from the first pass's first launch on, the 10-minute wait, the desk's cap 8 s")
    t = time.time()
    r, out, log, q = session(S, "r19", inject=[{"after_pass_launches": 1, "die": 62}], extra=["--die-wait-s", "600", "--cap-pass-s", "8"])
    span = ((q.get("t_close_ms") or 0) - (q.get("t_first_ms") or 0)) / 1000.0
    dg = [x for x in q.get("queue", []) if not x.get("ran") and "the cap" in str(x.get("why", "")) and "die gate" in str(x.get("why", ""))]
    print(f"   from the first card command to the close: {span:.1f} s; the session's wall time {time.time() - t:.0f} s")
    ok(r.returncode == 0 and len(dg) == 1 and len(passes_ran(q)) >= 1 and "STOP" not in log and "DRY session end" in log
       and 0 < span <= 60.0, "the die gate stopped waiting at the cap; the session closed within 60 s, not 10 minutes")

    if e2e:
        print("== E2E energy_stub's alt sampler, the registered 8 s / 10 s idles, then the reducer (unchanged) and the scorer (frozen)")
        r, out, log, q = session(S, "e2e", seq_args=["--sequence", "e2e"], double="alt", env={"E189_FAKE_SCALE": "1"})
        okred, data, sj, rsc = collect_score(S, "e2e", out)
        flags = []
        for x in passes_ran(q):
            en = energy(data, x["pass"])
            okred = okred and en.get("ok") is True and en.get("dir") == os.path.join(os.path.basename(data), "passes", x["pass"])
            flags += en.get("flags", [])
        okj = check_energies(out, data, [x["pass"] for x in passes_ran(q)])
        cfg = sj.get("configs", {})
        nod = sorted(k for k, c in cfg.items() if c.get("verdict") == "NO DATA")
        scored = sorted(k for k, c in cfg.items() if c.get("passes") == 2)
        v = sj.get("verdict_of_the_day") or {}
        for k in scored:
            c = cfg[k]
            print(f"   scored {k}: e_j_over {100 * c['e_j_over']:+.1f}%, e_j_total {100 * c['e_j_total']:+.1f}%, t_k/point "
                  f"{c['t_k_mean'] / c['t_point']:.4f}, e_j_total_forecast {100 * c['e_j_total_forecast']:+.1f}%")
        print(f"   scorer rc {rsc}; scored {scored}; NO DATA {nod}; verdicts {v}")
        ok(r.returncode == 0 and len(passes_ran(q)) == 6 and okred and any("DRY" in f for f in flags)
           and scored == ["copy-zeros", "sha256", "sparse-parity"] and nod == ["copy-random", "sort-shuffled", "sort-sorted"],
           "every pass reduced (flagged DRY), the scorer read three configurations and three NO DATA")
        ok(okj, "each pass's reduced J over idle within TOL of the energy the alt card injected (fault 1)")
        ok(v.get("E189-S1") == "NOT DECIDED" and v.get("E189-S2") == "NOT DECIDED" and len(v) == 4
           and set(v.values()) <= {"PASS", "FAIL", "NOT DECIDED"},
           "the verdict words: S1 and S2 NOT DECIDED (as injected: 3 scored, all within; 3 NO DATA); S1T and S2T words only")

        for name, inj, word, stopped, want_ran, want_scored in (
                ("r2e", [{"during": "pass", "after_pass_launches": 27, "board_w": 66.0, "count": 1}], "STOP: board 66.0 W at or above 65 W",
                 "copy-zeros/p2", 4, ["copy-zeros"]),
                ("r3e", [{"during": "pass", "after_pass_launches": 35, "die": 70, "count": 1}], "STOP: minshire[0] 70 C at or above 70 C",
                 "sha256/p2", 5, ["copy-zeros", "sha256"])):
            print(f"== {name.upper()} the {'board' if name == 'r2e' else 'die'} line during {stopped} on the alt card; reduced and scored")
            r, out, log, q = session(S, name, inject=inj, double="inject", env={"E189_FAKE_SCALE": "1", "E189_FAKE_BASE": "alt"},
                                     seq_args=["--sequence", "e2e", "--anchor-s", "5"])
            ran = [x["pass"] for x in passes_ran(q)]
            lp = pj(out, stopped)
            ia = idle_after_ms(out, stopped)
            print(f"   passes run {ran}; the stopped pass {stopped}: {ia} ms from its host's end to its end; flags {lp.get('flags')}")
            okr = (r.returncode == 0 and word in log and ran and ran[-1] == stopped and len(ran) == want_ran
                   and (lp.get("flags") or [""])[0].startswith("a stop line tripped") and ia >= 9950)
            okred, data, sj, rsc = collect_score(S, name, out)
            en = energy(data, stopped)
            cutflag = [f for f in en.get("flags", []) if "telemetry ends" in f]
            okj = check_energies(out, data, ran, card="alt")
            cfg = sj.get("configs", {})
            scored = sorted(k for k, c in cfg.items() if c.get("verdict") != "NO DATA")
            pp = [row.get("pass") for row in (cfg.get(stopped.split("/")[0]) or {}).get("per_pass", [])]
            notused = [x for x in sj.get("not_used", []) if x.startswith(stopped)]
            print(f"   scorer rc {rsc}; scored {scored}; {stopped.split('/')[0]}'s scored passes {pp}; not used {sj.get('not_used')}")
            ok(okr, f"{name}: the process finished, its pass flagged and its 10 s after whole, the queue ended after it")
            ok(okred and en.get("ok") is True and not cutflag and okj and scored == want_scored and pp == [1, 2] and not notused,
               f"{name}: every pass reduced within TOL, the stopped one with no cut-tail flag, and scored on its configuration's two passes")
            if name == "r2e":
                ce = cut_tail_control(S, name, data, stopped)
                jw, jc = (en.get("board") or {}).get("j_per_solve"), (ce.get("board") or {}).get("j_per_solve")
                lost = (1.0 - jc / jw) if (jw and jc) else None
                print(f"   the whole pass {jw} J a launch; cut where the first kit cut it {jc}: "
                      f"{'n/a' if lost is None else f'{100 * lost:.1f}%'} lower")
                ok(any("telemetry ends" in f for f in ce.get("flags", [])) and lost is not None and lost > 0.03,
                   "THE CUT TAIL (control): the pass cut 0.5 s after its host is flagged and reads more than 3% low")
    n = sum(results)
    print(f"SELFTEST-RUN-E189 {n} of {len(results)} {'PASS' if n == len(results) else 'FAIL'}")
    return 0 if n == len(results) else 1


if __name__ == "__main__":
    S = sys.argv[1]
    if os.path.abspath(S).startswith(REPO + os.sep):
        sys.exit("the scratch directory must be outside the repository")
    os.makedirs(S, exist_ok=True)
    sys.exit(main(os.path.abspath(S), e2e="--no-e2e" not in sys.argv))
