"""E194's runner desk test (Q183, the kit, Sun 15 Nov 2026, after E194's registration and before any E194 datum): run_e194.py in --dry
sessions with fake_card_e194.py's doubles, on the desk (aifoundry2, inside a sandbox with no /dev/et* and an empty /run/lock); no box, no
device, no ssh. It is E191's runner desk test (tools/claims-v3/e191/selftest_run_e191.py, unchanged beside it), every case of it on E194's
runner with this card's numbers (card 0, ET_DEVICES unset, the die gate at 57 C, E194's stop lines), with E191's per-sample clock cases
replaced by THE CLOCK RULE's, and E194's own cases (the host's line, the holder re-read) added. The doubles run at a tenth of their time
and THE CLOCK RULE's climb is scaled with them (--climb-s 0.15 for the registered 1.5 s; the doubles climb at 0.09 s); the end-to-end
cases run at full time with the registered 1.5 s.

    /usr/bin/python3 -B tools/claims-v3/e194/selftest_run_e194.py <scratch dir outside the repo> [--no-e2e]

E191's cases, on E194's runner (verdicts stated first):
  R1  plain: the stop-path test (four lines and the clock rule's read), identity (a) and (b) on card 0's forms, the ramped smoke with every
      device-opening host on card 0, six passes in E194.md 8.1's form, each with THE CLOCK RULE ok, the dry check of every device-opening
      command (ET_DEVICES and V3_DEVICE unset on each, nothing of another card), session end, a manifest; the sampler live in every pass;
  R2  THE BOARD LINE (66 W on a sample during a pass) and R3 THE DIE LINE (minshire[0] 70 C): the running process finishes, its idle after
      whole, the queue ends, the closing read;
  R6  THE DIE GATE at 57 C (58 C for 6 s from pass 1's first launch; the desk's bound 2 s): a pass skipped (no data), later passes run;  R6L a die below 46 C: the
      pass runs, labelled "T0 below the forecast band";  R7 THE CAP (6 s on the desk);
  R8  the start config not TDP 65 W: the gate;  R9 a holder of another login on card 0: no device opened;  R10 a failed smoke run;
  R11 a burst the budget cuts short: SHORT in words;  R12 a FAILED RUN;  R13 card 0's lock held: no device opened;  R14 only sparse parity
      built;  R15 the desk's overrides (--climb-s among them) and V3_DRY refused without --dry;  R16 a sampler that never starts;
  R18 THE END BOUND, the closing;  R19 THE END BOUND, the die gate;
  I1-I10 the identity gate both ways on this card: a second card's config (card 1's block), minion_mv 0, no block (a missing node), the
      sampler on a second card, ours on a second card, another login on a second card, ours on card 0's ops node, a host on a second card in
      the smoke and in a pass, a host that shows no card;
  B1, B2 (THE 30 s BOUND, card 0's lock held while the stuck host runs), F1-F7 (the sampler's freshness and the live sample), W1-W4 (et-who
  unreadable), Q1-Q5 (THE EARLY STOP), D1 (the dry check's refusals, for this box: an ET_DEVICES or V3_DEVICE set, another card named, a
  lock not card 0's);
  E2E energy_stub.py's alt card under the doubles' clock (600 MHz at rest, 800 MHz after a 0.9 s climb), the registered 8 s / 10 s idles
      and 1.5 s climb, two passes each of copy-zeros, sha256 and sparse parity, run from a STAND-IN BOX TREE (~/claude/et-soc1-prototyping's
      form, so the session's paths are box paths), then the collection's desk half (collect_e194.py: COPY-BACK EXACT, THE BOX-TREE GATE,
      the reducer unchanged, the scrub, SHA256SUMS, FILES.txt) and score_e194.py (frozen, its clock rule included): each pass's reduced J
      over idle within TOL of the energy the card injected, each pass's reducer output read as the scorer reads it (no hard line but the
      reducer's clock line, which THE CLOCK RULE reads: E194.md 8.2), S1 and S2 NOT DECIDED (3 scored, 3 NO DATA); R2E / R3E a stop during a pass on
      the alt card, reduced and scored, and the cut-tail control; BT the box-tree gate refuses the same session copied with a desk path in it.
E194's own cases:
  C1  THE CLOCK RULE: one pass whose clock steps to 700 MHz after its climb: SET ASIDE ("the clock: ..."), the session goes on;
  C2  a second such pass: "STOP: a second pass off 800 MHz after its climb", the queue ends, the closing read;  C3 a governor that climbs
      late in every pass (past the allowance): the first pass set aside, the second stops the session;  C4 bursts shorter than the climb
      window (the desk's climb set to 5 s): every pass flagged "the clock: no live sample ...", none set aside, the session goes on;
  C5  aifoundry2's own line: the latch minshire[2] at 80 C on a sample: STOP naming the latch; a board of 86 W on 3 samples stops on E189's
      65 W line, which binds first;
  H1  THE HOST'S LINE split by a runtime line (every host): the smoke reads ok, every pass PASS, each host_line 'reassembled' with its span;
      H2 split by a line no lab box printed: fix-e194 (verify-e194's finding 2), that pass reads 'none', a FAILED RUN (not a datum), the
      span named, the session goes on;  H3 split by the line "42" (a reader that continued the head's last number would read width 3242):
      'none', a FAILED RUN, never a wrong width;  H4 split by a lone "}" line: 'none', a FAILED RUN;
  T1  THE HOLDER RE-READ: a stray reader of ours on /dev/et0_mgmt at the first read: read again with the lock held, then the session runs;
      T2 the stray reader stays: refused after 3 re-reads, no device opened.
  F8  fix-e194 (verify-e194's nit 7): the sampler prints six lines of other shapes (temp_c a list or a word, minshire a number, mhz a list,
      board_w a word, t_ms a word) inside pass 1: the reader thread lives on (no restart, no pass flagged for a gap), the lines counted not
      live, nothing raised in the reader, six passes.
Prints SELFTEST-RUN-E194 <n> of <m> PASS or FAIL; exit 0 or 1. SPDX-License-Identifier: Apache-2.0
"""
import fcntl
import gzip
import hashlib
import json
import os
import pwd
import shutil
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
RUN = os.path.join(HERE, "run_e194.py")
REDUCER = os.path.join(REPO, "workloads", "sparseparity", "tools", "energy_reduce.py")
PY = "/usr/bin/python3"
FAST = ["--sequence", "short", "--idle-before", "0.5", "--idle-after", "0.5", "--anchor-s", "0.5", "--die-wait-s", "2", "--climb-s", "0.15"]
SCALE = "0.1"                  # the doubles' time; the climb (0.15 s) and the doubles' own climb (0.09 s) scale with it
EDGES = {"alt": (0.005, 0.003), "base": (0.0, 0.0)}     # energy_stub.py: the card's power starts 5 ms after a launch, ends 3 ms before
results = []


def ok(cond, what):
    results.append(bool(cond))
    print(f"-> {'PASS' if cond else 'FAIL'} ({what})", flush=True)


def session(S, name, env=None, inject=None, extra=None, seq_args=None, double="inject", t0=None, tree=None):
    """One --dry session: (CompletedProcess, out dir, log, queue). With tree (a stand-in box tree), the session runs from that tree's own
    runner with its directory relative to the tree (build/e194/T-<name>), as session_e194.sh runs it on the box."""
    d = os.path.join(S, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    e = dict(os.environ, E194_FAKE_SCALE=SCALE)
    e.pop("V3_DRY", None)
    e.pop("ET_DEVICES", None)
    e.pop("V3_DEVICE", None)
    if inject is not None:
        p = os.path.join(d, "inject.json")
        with open(p, "w") as f:
            json.dump(inject, f)
        e["E194_FAKE_INJECT"] = p
    e.update(env or {})
    run, cwd = RUN, REPO
    if tree:
        rel = os.path.join("build", "e194", f"T-{name}")
        out = os.path.join(tree, rel)
        if os.path.isdir(out):
            shutil.rmtree(out)
        run, cwd, oarg = os.path.join(tree, "tools", "claims-v3", "e194", "run_e194.py"), tree, rel
    else:
        out = oarg = os.path.join(d, "T")
    argv = [PY, "-I", "-B", run, "session", "--dry", "--double", double, "--t0", str(t0 or 1794700000), "--out", oarg] + \
        (seq_args if seq_args is not None else FAST) + (extra or [])
    r = subprocess.run(argv, cwd=cwd, env=e, capture_output=True, text=True, timeout=1800)
    log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
    q = {}
    if os.path.exists(os.path.join(out, "queue.json")):
        q = json.load(open(os.path.join(out, "queue.json")))
    print(f"   [{name}] rc {r.returncode}; " + " | ".join(ln.split(" ", 3)[-1][:220] for ln in log.splitlines()
                                                         if any(w in ln for w in ("STOP", "gate", "stop-path", "SET ASIDE",
                                                                                 "not started", "skipped", "SKIPPED", "no device",
                                                                                 "SIGTERM", "not restarted", "stray"))))
    return r, out, log, q


def session_bg(S, name, env=None, extra=None):
    """A --dry session started in the background (the cases that act on it while it runs: B1, B2, Q1, Q2): (Popen, out dir)."""
    d = os.path.join(S, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    e = dict(os.environ, E194_FAKE_SCALE=SCALE)
    e.pop("V3_DRY", None)
    e.update(env or {})
    out = os.path.join(d, "T")
    p = subprocess.Popen([PY, "-I", "-B", RUN, "session", "--dry", "--double", "inject", "--t0", "1794600000", "--out", out] + FAST + (extra or []),
                         cwd=REPO, env=e, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    return p, out


def finish_bg(p, out, name):
    rc = p.wait(timeout=900)
    log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
    q = json.load(open(os.path.join(out, "queue.json"))) if os.path.exists(os.path.join(out, "queue.json")) else {}
    print(f"   [{name}] rc {rc}; " + " | ".join(ln.split(" ", 3)[-1][:200] for ln in log.splitlines()
                                                if any(w in ln for w in ("STOP", "BOUND", "bound", "config end", "no device"))))
    return rc, log, q


def wait_for(cond, limit=120.0, every=0.02):
    t = time.time()
    while time.time() - t < limit:
        if cond():
            return True
        time.sleep(every)
    return False


def in_log(out, word):
    p = os.path.join(out, "session.log")
    return os.path.exists(p) and word in open(p).read()


def pass_launches(out):
    """The pass launches the host doubles announced so far (their schedule): pass 1 of the short sequence holds 8 (copy-zeros, K 8)."""
    p = os.path.join(out, "fake_sched.jsonl")
    if not os.path.exists(p):
        return 0
    return sum(1 for ln in open(p) if '"tag": "pass"' in ln)


def passes_ran(q):
    return [x for x in q.get("queue", []) if x.get("ran")]


def pj(out, key):
    p = os.path.join(out, "passes", key, "pass.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def rj(out, key):
    p = os.path.join(out, "passes", key, "run.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def not_live_flag(out, key):
    return any(f.startswith("the sampler was not live during this pass") for f in pj(out, key).get("flags") or [])


def flags_consistent(out, q):
    """fix-e191k2 (nit 2): every pass that ran carries the flag exactly when its recorded largest live-sample gap is SAMPLE_FRESH_S (2 s) or
    more, pass.json's sampler_live says the same, and queue.json lists exactly the flagged passes: (ok, [(pass, gap, flagged)])."""
    rows = [(x["pass"], rj(out, x["pass"]).get("live_gap_s_pass"), not_live_flag(out, x["pass"])) for x in passes_ran(q)]
    good = all(g is not None and (g >= 2.0) == fl and pj(out, k).get("sampler_live") is (not fl) for k, g, fl in rows)
    return good and sorted(q.get("passes_sampler_not_live") or []) == sorted(k for k, _, fl in rows if fl), rows


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
    fc = json.load(open(os.path.join(HERE, "forecast-e194.json")))["configs"][cfg]
    K = json.load(open(os.path.join(HERE, "plan-e194.json")))["configs"][cfg]["launches_K"]
    return 0.03 + 0.33 * (K * fc["seconds"]["point"] + 7.0) / (K * fc["j_over_idle"])


def box_tree(S):
    """A stand-in box tree (~/claude/et-soc1-prototyping's form) under a stand-in home: every harness file copied byte for byte."""
    home = os.path.join(S, "boxhome")
    tree = os.path.join(home, "claude", "et-soc1-prototyping")
    if not os.path.isdir(tree):
        sys.path.insert(0, HERE)
        import check_e194 as H
        for rel in list(H.FILES) + ["tools/claims-v3/e194/harness-e194.json"]:
            dst = os.path.join(tree, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(REPO, rel), dst)
    return home, tree


def collect_score(S, name, out, box_home):
    """The collection's desk half on a copy of the session (as the box would leave it), then the frozen scorer on the collected folder."""
    cp = os.path.join(S, name, "copy")
    if os.path.isdir(cp):
        shutil.rmtree(cp)
    shutil.copytree(out, cp)
    os.remove(os.path.join(cp, "dry.lock"))     # --dry's own lock file, which the manifest leaves out (a real session locks /run/lock's)
    open(os.path.join(cp, "runner.rc"), "w").write("0\n")
    data = os.path.join(S, name, "2026-11-15-e194-blind-day-aifoundry2")
    if os.path.isdir(data):
        shutil.rmtree(data)
    lgf = os.path.join(S, name, "box-login.txt")
    open(lgf, "w").write(pwd.getpwuid(os.getuid()).pw_name + "\n")
    rc_ = subprocess.run([PY, "-B", os.path.join(HERE, "collect_e194.py"), cp, data, "--box-home", box_home,
                          "--box-login", lgf, "--data-outside"], cwd=REPO, capture_output=True, text=True, timeout=900, env=dict(os.environ, RB_DESKTEST="1"))
    print("   " + "\n   ".join(ln[:240] for ln in rc_.stdout.splitlines() if ln.startswith(("COPY-BACK", "COLLECTED", "SCRUB", "REDUCER", "BOX-TREE"))))
    home = box_home.encode()
    left = [os.path.join(dp, n) for dp, dn, fn in os.walk(data) for n in fn
            if home in (gzip.decompress(open(os.path.join(dp, n), "rb").read()) if n.endswith(".gz")
                        else open(os.path.join(dp, n), "rb").read())] if os.path.isdir(data) else ["no data"]
    print(f"   files holding the stand-in box home after the scrub: {len(left)}")
    sc = os.path.join(S, name, "scores.json")
    rs = subprocess.run([PY, "-B", os.path.join(HERE, "score_e194.py"), data, "--out", sc], cwd=REPO, capture_output=True,
                        text=True, timeout=600)
    sj = json.load(open(sc)) if os.path.exists(sc) else {}
    return rc_.returncode == 0 and "COLLECTED" in rc_.stdout and "BOX-TREE GATE: every path" in rc_.stdout and not left, data, sj, rs.returncode


def energy(data, key):
    p = os.path.join(data, "passes", key, "energy.json")
    return json.load(open(p)) if os.path.exists(p) else {}


CLOCK_LINE = "minion clock in busy samples"     # the reducer's hard line THE CLOCK RULE reads (E194.md 8.2; score_e194.py's CLOCK_LINE)


def reduced_ok(en):
    """The reducer's output as the registered scorer reads it (score_e194.py read_pass, E194.md 8.2): a board result, and no hard line
    but the clock line, which THE CLOCK RULE reads instead (at 800 MHz the governor's climb from 600 MHz lies inside the reducer's busy
    window [lo + 0.5 s, hi], so the unchanged reducer writes that line and ok false on every pass: E194.md 8.5's scenario A)."""
    hard = [x for x in en.get("hard", []) if not x.startswith(CLOCK_LINE)]
    return bool(en.get("board")) and not hard and (en.get("ok") is True or bool(en.get("hard")))


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
    print("== R1 plain dry session (doubles; THE CLOCK RULE at the desk's time scale)")
    r, out, log, q = session(S, "r1")
    ran = passes_ran(q)
    form = all(os.path.exists(os.path.join(out, "passes", x["pass"], f)) for x in ran
               for f in ("telemetry.jsonl.gz", "host.json", "host-stdout.txt", "run.json", "pass.json"))
    form = form and all(os.path.exists(os.path.join(out, "passes", f"{c}/p1", "host-raw.json"))
                        for c in ("copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled"))
    ok(r.returncode == 0 and "stop-path test passed" in log and "the clock rule read the live samples" in log and "smoke gate passed: queue starts" in log
       and len(ran) == 6 and form and "DRY session end (T0" in log and os.path.exists(os.path.join(out, "MANIFEST.sha256"))
       and log.splitlines()[0].endswith(" DRY"), "six passes in 8.1's form, the stop-path test (four lines, the clock rule read) and the smoke passed, DRY marks")
    idn = json.load(open(os.path.join(out, "identity.json"))) if os.path.exists(os.path.join(out, "identity.json")) else {}
    smk = idn.get("smoke", {})
    print(f"   identity: config {idn.get('config_start')}; et-who {idn.get('etwho_with_sampler', {}).get('counts')}; sampler "
          f"{idn.get('sampler_nodes', {}).get('nodes')}; smoke hosts {sorted({tuple(v['stderr_targets']) for v in smk.values()})}")
    ok(q.get("identity_ok") is True and idn.get("config_start", {}).get("targets") == ["/dev/et0_mgmt"]
       and idn.get("config_start", {}).get("ids") == [0] and idn.get("config_start", {}).get("minion_mv") == 519
       and idn.get("sampler_nodes", {}).get("nodes") == ["/dev/et0_mgmt"] and idn.get("etwho_with_sampler", {}).get("counts", {}).get("ours_off_card0") == 0
       and all(v["right"] and not v["wrong"] for k, v in smk.items() if k != "ledger-selftest") and len(smk) == 8
       and os.path.exists(os.path.join(out, "config-start.err")) and "identity (a): /dev/et0_mgmt, device ID 0" in log
       and all((rj(out, x["pass"]).get("identity") or {}).get("right") for x in ran),
       "the identity gate (a) and (b) passed on card 0's forms; every device-opening host showed card 0 (smoke and passes)")
    dc = q.get("dry_check") or {}
    ok(dc.get("ok") is True and dc.get("n") == 16 and "the device-command check: 16 device-opening command(s), each with ET_DEVICES and V3_DEVICE unset" in log,
       "the dry check: 16 device-opening commands, each with ET_DEVICES and V3_DEVICE unset, nothing of another card")
    clk = [(x["pass"], x.get("clock"), (rj(out, x["pass"]).get("clock_rule") or {}).get("n")) for x in ran]
    print(f"   THE CLOCK RULE per pass (pass, verdict, samples read): {clk}")
    ok(all(c == "ok" and (n or 0) >= 1 for _, c, n in clk) and not q.get("off_clock_passes") and not q.get("set_aside"),
       "THE CLOCK RULE: every pass's live samples from its burst's start + the climb to its end read 800 MHz; none set aside; the idle 600 MHz not checked")
    tel = [json.loads(ln) for ln in gzip.open(os.path.join(out, "passes", "copy-zeros", "p1", "telemetry.jsonl.gz"), "rt")]
    h = json.load(open(os.path.join(out, "passes", "copy-zeros", "p1", "run.json")))
    mz = sorted({(s.get("mhz") or {}).get("minion") for s in tel})
    ok(tel and tel[0]["t_ms"] < h["host_t0_ms"] and tel[-1]["t_ms"] > h["host_t1_ms"] and mz == [600, 800],
       f"a pass's telemetry spans its idle brackets and reads both clocks ({mz}: 600 at rest and in the climb, 800 after it)")
    sl = [(rj(out, x["pass"]), pj(out, x["pass"])) for x in ran]
    ok(len(sl) == 6 and all(a.get("live_gap_s_pass") is not None and a["live_gap_s_pass"] < 2.0 and a.get("sampler_live_during_pass") is True
                            and b.get("sampler_live") is True and not any("not live" in f for f in b.get("flags") or [])
                            and (a.get("live_samples_host") or 0) >= 1 for a, b in sl)
       and q.get("sampler_lines_not_live") == 0 and q.get("passes_sampler_not_live") == [] and all((a.get("host_line") or {}).get("method") == "whole line" for a, b in sl),
       "every pass's sampler live (largest gap under 2 s), no flag; every host's line read whole")

    for name, inj, word in (("r2", [{"during": "pass", "board_w": 66.0, "count": 1}], "STOP: board 66.0 W at or above 65 W"),
                            ("r3", [{"during": "pass", "die": 70, "count": 1}], "STOP: minshire[0] 70 C at or above 70 C")):
        print(f"== {name.upper()} the {'board' if name == 'r2' else 'die'} line on a live sample during a pass")
        r, out, log, q = session(S, name, inject=inj)
        ran = passes_ran(q)
        last = ran[-1]["pass"] if ran else None
        lp = pj(out, last) if last else {}
        ia = idle_after_ms(out, last) if last else 0
        print(f"   the stopped pass {last}: {ia} ms from its host's end to its end (its idle after: 500 ms)")
        ok(r.returncode == 0 and word in log and 1 <= len(ran) < 6 and lp.get("flags") and "stop line tripped" in lp["flags"][0]
           and "config end:" in log and "DRY session end" in log and ia >= 450,
           "the running process finished, its idle after whole, the queue ended, the pass flagged, the closing read")
    print("== C5 aifoundry2's own lines: the latch minshire[2] at 80 C; a board of 86 W on 3 samples (E189's 65 W line binds first)")
    r, out, log, q = session(S, "c5a", inject=[{"during": "pass", "latch": 80, "count": 1}])
    r2_, out2, log2, q2 = session(S, "c5b", inject=[{"during": "pass", "board_w": 86.0, "count": 3}])
    ok(r.returncode == 0 and "STOP: minshire[0]" in log and "or the latch minshire[2] 80 C at or above 80 C" in log and len(passes_ran(q)) < 6
       and r2_.returncode == 0 and "STOP: board 86.0 W at or above 65 W" in log2,
       "the latch at 80 C stops the queue on aifoundry2's line; 86 W stops it on E189's 65 W line first")
    print("== C1 THE CLOCK RULE: one pass steps to 700 MHz after its climb: set aside, the session goes on")
    r, out, log, q = session(S, "c1", inject=[{"during": "busy", "burst_after_s": 0.2, "mhz": 700, "count": 1}])
    sa = [x for x in passes_ran(q) if str(x.get("set_aside") or "").startswith("the clock:")]
    ok(r.returncode == 0 and len(passes_ran(q)) == 6 and len(sa) == 1 and "[700] MHz, not 800" in sa[0]["set_aside"] and "STOP" not in log
       and q.get("off_clock_passes") == [sa[0]["pass"]] and pj(out, sa[0]["pass"]).get("clock_rule") == "off",
       "one pass set aside by the clock (no data), six passes ran, no stop")
    print("== C2 a second pass off the clock (another configuration): the session stops")
    r, out, log, q = session(S, "c2", inject=[{"during": "busy", "burst_after_s": 0.2, "mhz": 700, "count": 40}])
    sa = [x for x in passes_ran(q) if str(x.get("set_aside") or "").startswith("the clock:")]
    ok(r.returncode == 0 and "STOP: a second pass off 800 MHz after its climb" in log and len(sa) == 2 and len(passes_ran(q)) == 2
       and "config end: TDP" in log and q.get("stop", "").startswith("a second pass off 800 MHz"),
       "both passes set aside, the second stopped the queue (the card is not at the forecast's clock), the closing read")
    print("== C3 a governor that climbs late in every pass (0.4 s against the desk's 0.15 s allowance)")
    r, out, log, q = session(S, "c3", env={"E194_FAKE_CLIMB_S": "0.4"})
    sa = [x for x in passes_ran(q) if str(x.get("set_aside") or "").startswith("the clock:")]
    ok(r.returncode == 0 and len(sa) == 2 and "STOP: a second pass off 800 MHz after its climb" in log and "[600] MHz" in sa[0]["set_aside"],
       "the first pass set aside (600 MHz after the allowance), the second stopped the session")
    print("== C4 bursts shorter than the clock window (the desk's climb set to 5 s): every pass flagged, none set aside")
    r, out, log, q = session(S, "c4", extra=["--climb-s", "5"], seq_args=[x for x in FAST if x not in ("--climb-s", "0.15")])
    ran = passes_ran(q)
    fl = [any(f.startswith("the clock: no live sample") for f in pj(out, x["pass"]).get("flags") or []) for x in ran]
    ok(r.returncode == 0 and len(ran) == 6 and all(fl) and not q.get("off_clock_passes") and len(q.get("unread_clock_passes") or []) == 6
       and "STOP" not in log, "each pass flagged 'the clock: no live sample ...' (the scorer reads its telemetry), none set aside, the session went on")
    print("== R6 the die gate at 57 C: 58 C for 6 s from the first pass's first launch; the bound 2 s")
    r, out, log, q = session(S, "r6", inject=[{"after_pass_launches": 1, "die": 58, "for_s": 6}])
    sk = [x for x in q.get("queue", []) if not x.get("ran") and str(x.get("why", "")).startswith("die gate")]
    ok(r.returncode == 0 and len(sk) >= 1 and len(passes_ran(q)) >= 3 and "STOP" not in log,
       "a pass skipped by the die gate at 58 C (no data), later passes ran, no stop")
    print("== R6L a die below the forecast band (44 C throughout)")
    r, out, log, q = session(S, "r6l", inject=[{"die": 44}])
    p1 = pj(out, "copy-zeros/p1")
    ok(r.returncode == 0 and any("T0 below the forecast band" in f for f in p1.get("flags") or []) and len(passes_ran(q)) == 6,
       f"the pass ran and is labelled 'T0 below the forecast band' (its T0 {p1.get('die_start_c')} C)")
    print("== R7 the cap (6 s on the desk; 108 card-minutes on the box)")
    r, out, log, q = session(S, "r7", extra=["--cap-pass-s", "6"])
    nc = [x for x in q.get("queue", []) if not x.get("ran") and "the cap" in str(x.get("why", ""))]
    ok(r.returncode == 0 and len(nc) >= 1 and "DRY session end" in log, "passes after the cap not started")
    print("== R8 the start config is not TDP 65 W")
    r, out, log, q = session(S, "r8", env={"E194_FAKE_CONFIG": "tdp0"})
    ok(r.returncode == 16 and "the gate, no launch" in log and "smoke" not in log and not passes_ran(q), "the gate, rc 16")
    print("== R9 a holder of another login on card 0")
    r, out, log, q = session(S, "r9", env={"E194_FAKE_ETWHO": "other"})
    ok(r.returncode == 16 and "no device opened" in log and "config start" not in log, "no device opened, rc 16")
    print("== R10 a failed smoke run")
    r, out, log, q = session(S, "r10", env={"E194_FAKE_HOST": "fail"})
    ok(r.returncode == 16 and "smoke gate failed" in log and not passes_ran(q), "smoke gate failed, no pass")
    print("== R11 a burst the budget cuts short")
    r, out, log, q = session(S, "r11", env={"E194_FAKE_HOST": "short"})
    h = json.load(open(os.path.join(out, "passes", "copy-zeros", "p1", "host.json"))) if r.returncode == 0 else {}
    ok(r.returncode == 0 and h.get("problems") == ["reps: 6 of 8 done"] and h.get("reps_consistent") == "ok"
       and h.get("reps_done") == 6 and "copy-zeros p1 done: host rc 1, status FAIL, reading SHORT (6 of 8 launches, the host's own budget" in log,
       "host.json says 'reps: 6 of 8 done' (SHORT, scored) and the session log reads SHORT in words")
    print("== R12 a FAILED RUN in a pass")
    r, out, log, q = session(S, "r12", env={"E194_FAKE_HOST": "fail-pass"})
    h = json.load(open(os.path.join(out, "passes", "sha256", "p1", "host.json"))) if r.returncode == 0 else {}
    ok(r.returncode == 0 and h.get("reps_consistent") == "bad" and h.get("problems", [""])[0].startswith("checks:")
       and "sha256 p1 done: host rc 1, status FAIL, reading FAILED RUN (not a datum)" in log,
       "reps_consistent bad, problems name the checks (not a datum); the log reads FAILED RUN")
    print("== R13 card 0's lock held by another process")
    d = os.path.join(S, "r13")
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "T"))
    hold = open(os.path.join(d, "T", "dry.lock"), "a+")
    fcntl.flock(hold.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    e = dict(os.environ, E194_FAKE_SCALE=SCALE)
    r = subprocess.run([PY, "-I", "-B", RUN, "session", "--dry", "--t0", "1", "--out", os.path.join(d, "T")] + FAST, cwd=REPO,
                       env=e, capture_output=True, text=True, timeout=300)
    hold.close()
    log = open(os.path.join(d, "T", "session.log")).read()
    ok(r.returncode == 16 and "card 0's lock is held: no device opened" in log, "no device opened, rc 16")
    print("== R14 only sparse parity built today")
    r, out, log, q = session(S, "r14", extra=["--programs", "spp"])
    sk = [x for x in q.get("queue", []) if "SKIPPED" in str(x.get("why", ""))]
    ok(r.returncode == 0 and len(sk) == 5 and len(passes_ran(q)) == 1 and "smoke ledger" not in log
       and "smoke sparse-parity-r1" in log, "five ledger passes SKIPPED, sparse parity's ran, its smoke alone")
    print("== R15 the desk's overrides and V3_DRY are refused without --dry")
    rr = []
    for k, extra_, env_ in (("a", ["--idle-before", "1"], {}), ("b", [], {"V3_DRY": "1"}), ("c", ["--cap-end-s", "20"], {}),
                            ("d", ["--host-bound-s", "2"], {}), ("e", ["--climb-s", "0.15"], {})):
        x = subprocess.run([PY, "-I", "-B", RUN, "session", "--t0", "1", "--out", os.path.join(S, "r15" + k)] + extra_, cwd=REPO,
                           capture_output=True, text=True, timeout=60, env=dict(os.environ, **env_))
        rr.append((x.returncode, x.stdout.strip()[:80]))
    print(f"   {rr}")
    ok(all(c == 2 for c, _ in rr) and "--climb-s" in rr[4][1] and "--host-bound-s" in rr[3][1]
       and not any(os.path.exists(os.path.join(S, "r15" + k)) for k in "abcde"), "rc 2 each (THE CLOCK RULE's --climb-s among them), nothing started")
    print("== R16 a sampler that never starts: the stop path cannot be shown, no launch")
    r, out, log, q = session(S, "r16", env={"E194_FAKE_SAMPLER": "dead"})
    ok(r.returncode == 16 and "the sampler would not start: no launch" in log and "smoke" not in log, "no launch, rc 16")
    print("== R18 THE END BOUND, the closing: a sampler that ignores its first SIGTERM; the desk's cap 6 s, end bound 20 s")
    r, out, log, q = session(S, "r18", env={"E194_FAKE_SAMPLER": "stubborn"}, extra=["--cap-pass-s", "6", "--cap-end-s", "20"])
    span = ((q.get("t_close_ms") or 0) - (q.get("t_first_ms") or 0)) / 1000.0
    ok(r.returncode == 0 and "SIGTERM once more" in log and "left running" not in log and "config end: TDP 65 W" in log
       and "DRY session end" in log and 0 < span <= 20.0, f"the closing bounded: the second SIGTERM, the closing read, closed by the bound ({span:.1f} s)")
    print("== R19 THE END BOUND, the die gate: 58 C from the first pass's first launch on, the 10-minute wait, the desk's cap 8 s")
    r, out, log, q = session(S, "r19", inject=[{"after_pass_launches": 1, "die": 58}], extra=["--die-wait-s", "600", "--cap-pass-s", "8"])
    span = ((q.get("t_close_ms") or 0) - (q.get("t_first_ms") or 0)) / 1000.0
    dg = [x for x in q.get("queue", []) if not x.get("ran") and "the cap" in str(x.get("why", "")) and "die gate" in str(x.get("why", ""))]
    ok(r.returncode == 0 and len(dg) == 1 and len(passes_ran(q)) >= 1 and "STOP" not in log and "DRY session end" in log
       and 0 < span <= 60.0, f"the die gate stopped waiting at the cap; the session closed within 60 s ({span:.1f} s), not 10 minutes")

    # ---- the identity gate both ways (card 0's forms pass in R1; a second card's and a missing node's forms are refused here)
    def nohost(out):
        return not os.path.isdir(os.path.join(out, "smoke")) and not os.path.isdir(os.path.join(out, "passes"))
    for name, env, word in (("i1", {"E194_FAKE_CONFIG": "card1"}, "IDENTITY GATE FAILED: PCIe target /dev/et1_mgmt, not /dev/et0_mgmt alone"),
                            ("i2", {"E194_FAKE_CONFIG": "mv0"}, "IDENTITY GATE FAILED: minion_mv 0, not between 450 and 600"),
                            ("i3", {"E194_FAKE_CONFIG": "noident"}, "IDENTITY GATE FAILED: no 'PCIe target' line")):
        print(f"== {name.upper()} the start config read: {env['E194_FAKE_CONFIG']}")
        r, out, log, q = session(S, name, env=env)
        ok(r.returncode == 16 and word in log and "the gate, no launch" in log and "sampler started" not in log and nohost(out)
           and os.path.exists(os.path.join(out, "config-start.err")),
           f"{name}: the identity gate (a) refused it before the sampler and any host, rc 16")
    print("== I4 the sampler holds a second card's node")
    r, out, log, q = session(S, "i4", env={"E194_FAKE_SAMPLER": "card1"})
    ok(r.returncode == 16 and "identity (b): IDENTITY GATE FAILED" in log and "the sampler does not hold /dev/et0_mgmt" in log
       and "the gate, no launch" in log and nohost(out), "the identity read (b) refused it before any host, rc 16")
    for name, mode, word in (("i5", "ours1", "holder line(s) of ours off card 0"), ("i6", "other1", "holder line(s) of another login"),
                             ("i7", "ops", "holder line(s) of ours on /dev/et0_ops while no host of ours runs")):
        print(f"== {name.upper()} et-who before the first card command: {mode}")
        r, out, log, q = session(S, name, env={"E194_FAKE_ETWHO": mode})
        ok(r.returncode == 16 and word in log and "no device opened" in log and "config start" not in log and nohost(out)
           and len(q.get("holder_reads_at_start") or []) == 1,
           f"{name}: refused before the first card command at the first read (not a stray reader: no re-read), rc 16")
    print("== I8 a host names and holds a second card in the smoke")
    r, out, log, q = session(S, "i8", env={"E194_FAKE_HOST": "card1"})
    sm = sorted(os.listdir(os.path.join(out, "smoke"))) if os.path.isdir(os.path.join(out, "smoke")) else []
    ok(r.returncode == 16 and "smoke copy-64m-random: rc 0, ok" in log and "the host's card: ANOTHER CARD" in log
       and "smoke gate failed: copy-64m-random: the host's card: ANOTHER CARD" in log and sm == ["copy-64m-random", "ledger-selftest"]
       and not passes_ran(q), "the smoke gate failed at the first device-opening host; no second host, no pass, rc 16")
    print("== I9 a host names and holds a second card in a pass (the 8th device-opening host: pass 1)")
    r, out, log, q = session(S, "i9", env={"E194_FAKE_HOST": "card1", "E194_FAKE_HOST_FROM": "8", "E194_FAKE_HOST_COUNT": "1"})
    ran = passes_ran(q)
    sa = [x for x in ran if str(x.get("set_aside") or "").startswith("identity:")]
    ok(r.returncode == 0 and len(ran) == 1 and len(sa) == 1 and "STOP: identity: the host named or held another card" in log
       and "config end:" in log and "DRY session end" in log,
       "that pass SET ASIDE by its identity, the session stopped after it, the closing read")
    print("== I10 a host that shows no card in a pass")
    r, out, log, q = session(S, "i10", env={"E194_FAKE_HOST": "noident", "E194_FAKE_HOST_FROM": "8", "E194_FAKE_HOST_COUNT": "1"})
    fl = pj(out, "copy-zeros/p1").get("flags") or []
    ok(r.returncode == 0 and len(passes_ran(q)) == 6 and any("the host's card was not seen" in f for f in fl) and "STOP" not in log,
       "flagged 'the host's card was not seen' (reported), the session went on")
    # ---- E194: the host's line, and the holder re-read
    print("== H1 THE HOST'S LINE split by a runtime line in every ledger host (smoke and passes)")
    r, out, log, q = session(S, "h1", env={"E194_FAKE_HOST": "split"})
    ran = passes_ran(q)
    lines = [(x["pass"], (rj(out, x["pass"]).get("host_line") or {})) for x in ran]
    smj = json.load(open(os.path.join(out, "smoke", "copy-64m-random", "smoke.json"))) if os.path.isdir(os.path.join(out, "smoke")) else {}
    ok(r.returncode == 0 and "smoke gate passed" in log and (smj.get("host_line") or {}).get("dropped") == ["Opening device 0"] and len(ran) == 6
       and all(x.get("reading") == "PASS" for x in ran)
       and all(hl.get("method") == ("reassembled" if not k.startswith("sparse") else "whole line") for k, hl in lines)
       and all(hl.get("dropped") == ["Opening device 0"] for k, hl in lines if not k.startswith("sparse"))
       and "the host's line reassembled around 1 foreign span(s) ('Opening device 0'; each a runtime line seen before)" in log,
       "the smoke read ok and every pass PASS; each ledger host's line reassembled around the one runtime span, recorded (run.json, smoke.json, the log)")
    print("== H2 a line split by a line no lab box printed (pass 1): fix-e194, 'none', a FAILED RUN")
    r, out, log, q = session(S, "h2", env={"E194_FAKE_HOST": "splitjunk", "E194_FAKE_HOST_FROM": "8", "E194_FAKE_HOST_COUNT": "1"})
    ran = passes_ran(q)
    hl = rj(out, ran[0]["pass"]).get("host_line") or {} if ran else {}
    ok(r.returncode == 0 and len(ran) == 6 and ran[0].get("reading") == "FAILED RUN (not a datum)" and hl.get("method") == "none"
       and "not a whole known runtime line" in (hl.get("why") or "") and all(x.get("reading") == "PASS" for x in ran[1:])
       and "the host's line could not be read (a dropped span is not a whole known runtime line" in log,
       "the pass read 'none', a FAILED RUN (never read around a span no lab box printed), the span named; the other passes PASS")
    for name, mode, word in (("h3", "splitdigit", "a raw newline inside the object read"), ("h4", "splitbrace", "no status")):
        print(f"== {name.upper()} a line split by {'the line 42' if mode == 'splitdigit' else 'a lone brace line'} (pass 1): 'none', a FAILED RUN")
        r, out, log, q = session(S, name, env={"E194_FAKE_HOST": mode, "E194_FAKE_HOST_FROM": "8", "E194_FAKE_HOST_COUNT": "1"})
        ran = passes_ran(q)
        hl = rj(out, ran[0]["pass"]).get("host_line") or {} if ran else {}
        raw = open(os.path.join(out, "passes", ran[0]["pass"], "host-raw.json")).read().strip() if ran else "x"
        print(f"   pass 1 {ran[0]['pass'] if ran else None}: reading {ran[0].get('reading') if ran else None}; host_line {hl.get('method')}: "
              f"{str(hl.get('why'))[:120]}; host-raw.json {raw[:40]!r}")
        ok(r.returncode == 0 and len(ran) == 6 and ran[0].get("reading") == "FAILED RUN (not a datum)" and hl.get("method") == "none"
           and word in (hl.get("why") or "") and raw == "" and all(x.get("reading") == "PASS" for x in ran[1:]),
           f"{name}: the pass read 'none' ({word}), a FAILED RUN with an empty host-raw.json, never a wrong head field; the other passes PASS")
    print("== T1 THE HOLDER RE-READ: a stray reader of ours on /dev/et0_mgmt at the first read only")
    r, out, log, q = session(S, "t1", env={"E194_FAKE_ETWHO": "mgmt", "E194_FAKE_ETWHO_UNTIL": "2"})
    rr = q.get("holder_reads_at_start") or []
    ok(r.returncode == 0 and len(rr) == 2 and rr[0].get("transient") is True and not rr[1].get("why") and "read again in 2 s (1 of 3)" in log
       and len(passes_ran(q)) == 6, "read again with the lock held, clear, then the session ran (six passes)")
    print("== T2 the stray reader stays")
    r, out, log, q = session(S, "t2", env={"E194_FAKE_ETWHO": "mgmt"})
    rr = q.get("holder_reads_at_start") or []
    ok(r.returncode == 16 and len(rr) == 4 and "no device opened" in log and not os.path.exists(os.path.join(out, "config-start.json")),
       "refused after 3 re-reads (4 reads), no device opened, rc 16")
    # ---- the real day's fixes
    print("== B1 THE 30 s BOUND: a host that ignores SIGTERM past the runner's bound (the desk's 2 s); card 0's lock held while it runs")
    t = time.time()
    p, out = session_bg(S, "b1", env={"E194_FAKE_HOST": "wedge", "E194_FAKE_HOST_FROM": "8", "E194_FAKE_HOST_COUNT": "1",
                                      "E194_FAKE_WEDGE_S": "6"}, extra=["--host-bound-s", "2"])
    seen = wait_for(lambda: in_log(out, "BOUND: the host process"), 120)
    held = None
    if seen:
        time.sleep(0.5)
        with open(os.path.join(out, "dry.lock"), "a+") as lk:
            try:
                fcntl.flock(lk.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                held = False
                fcntl.flock(lk.fileno(), fcntl.LOCK_UN)
            except OSError:
                held = True
    rc, log, q = finish_bg(p, out, "b1")
    b = (q.get("bound") or [{}])[0]
    lines = log.splitlines()
    i_end = next((i for i, ln in enumerate(lines) if "the host past the bound" in ln and "has ended" in ln), None)
    i_cfg = next((i for i, ln in enumerate(lines) if "config end: TDP" in ln), None)
    print(f"   the session's wall time {time.time() - t:.1f} s; the lock while the stuck host ran: {'HELD' if held else held}; bound records {q.get('bound')}")
    ok(rc == 0 and "BOUND: the host process" in log and "nothing is killed; the queue stops" in log and len(passes_ran(q)) == 1
       and len(q.get("bound") or []) == 1 and "config end:" in log and "DRY session end" in log
       and "BOUND" in " ".join(pj(out, "copy-zeros/p1").get("flags") or []),
       "BOUND logged, the queue stopped after that pass, nothing killed, the closing read")
    ok(held is True and b.get("ended_ms") and not b.get("alive_at_close") and i_end is not None and i_cfg is not None and i_end < i_cfg
       and q.get("lock_released_with_bound_host_alive") is False,
       "finding 4: card 0's lock HELD while the stuck host ran; its end polled (nothing killed); the closing read only after it ended")
    print("== B2 THE BOUND WAIT'S OWN BOUND: the stuck host outlives the end bound less the closing's share (the desk's end bound 30 s)")
    p, out = session_bg(S, "b2", env={"E194_FAKE_HOST": "wedge", "E194_FAKE_HOST_FROM": "8", "E194_FAKE_HOST_COUNT": "1",
                                      "E194_FAKE_WEDGE_S": "30"}, extra=["--host-bound-s", "2", "--cap-pass-s", "20", "--cap-end-s", "30"])
    rc, log, q = finish_bg(p, out, "b2")
    b = (q.get("bound") or [{}])[0]
    ok(rc == 0 and b.get("alive_at_close") is True and not b.get("ended_ms") and "config end: NOT RUN" in log and "config end: TDP" not in log
       and "card 0's lock is released with it running" in log and q.get("lock_released_with_bound_host_alive") is True
       and "DRY session end" in log and os.path.exists(os.path.join(out, "MANIFEST.sha256")),
       "the lock released with the stuck host still running (recorded, reported), the closing config read not run beside it, rc 0")
    pid = b.get("pid")
    gone = wait_for(lambda: not os.path.exists(f"/proc/{pid}"), 45, 0.5) if pid else True
    print(f"   the stand-in stuck host (pid {pid}) ended by itself afterwards: {gone} (never killed)")
    # ---- finding 2: the sampler's freshness
    for name, mode, word in (("f1", "hangs:9", "the sampler is not live (alive True"), ("f2", "dies:9", "the sampler is not live (alive False")):
        print(f"== {name.upper()} the sampler {mode.split(':')[0]} inside pass 1 (the schedule's 9th launch): restarted; every host on a live sample")
        r, out, log, q = session(S, name, env={"E194_FAKE_SAMPLER": mode})
        ran = passes_ran(q)
        ages = [rj(out, x["pass"]).get("sample_age_s_at_host_start") for x in ran]
        sm = [json.load(open(os.path.join(out, "smoke", n, "smoke.json"))).get("sample_age_s_at_start")
              for n in sorted(os.listdir(os.path.join(out, "smoke"))) if n != "ledger-selftest"] if os.path.isdir(os.path.join(out, "smoke")) else []
        print(f"   passes {len(ran)}; the last sample's age at each pass's host start {ages}; at each smoke process {sm}")
        ok(r.returncode == 0 and word in log and "restarting it" in log and log.count("sampler started (attempt") >= 2 and len(ran) >= 5
           and all(a is not None and a < 2.0 for a in ages + sm) and len(sm) == 7,
           f"{name}: the sampler restarted; every host process (smoke and passes) started on a sample under 2 s old")
        fc, rows = flags_consistent(out, q)
        print(f"   fix-e191k2: (pass, largest live-sample gap s, flagged) {rows}")
        ok(fc, f"{name} (fix-e191k2, nit 2): each pass flagged 'the sampler was not live during this pass' exactly when its largest "
               "live-sample gap was 2 s or more; queue.json lists those passes")
    print("== F3 every sampler of the session silent from the schedule's 9th launch on: the restart fails, the queue stops")
    r, out, log, q = session(S, "f3", env={"E194_FAKE_SAMPLER": "hangs-all:9"})
    ran = passes_ran(q)
    ages = [rj(out, x["pass"]).get("sample_age_s_at_host_start") for x in ran]
    fc, rows = flags_consistent(out, q)
    print(f"   passes {len(ran)}; ages at host start {ages}; fix-e191k2: (pass, largest live-sample gap s, flagged) {rows}")
    ok(r.returncode == 0 and "STOP: the sampler would not restart" in log and 1 <= len(ran) < 6 and all(a is not None and a < 2.0 for a in ages)
       and "DRY session end" in log and fc, "no host started on a stale sample; 'the sampler would not restart' ended the queue; the closing; "
       "each pass flagged exactly when its largest live-sample gap was 2 s or more (fix-e191k2)")
    # ---- fix-e191k2: the second verifier's nits 1 and 2 (a live sample; the sampler during a pass)
    print("== F4 (nit 1) the sampler keeps printing, but without board_w, from the schedule's 9th launch (once): those lines are not live")
    r, out, log, q = session(S, "f4", env={"E194_FAKE_SAMPLER": "noboard:9"})
    ran = passes_ran(q)
    ages = [rj(out, x["pass"]).get("sample_age_s_at_host_start") for x in ran]
    fc, rows = flags_consistent(out, q)
    print(f"   passes {len(ran)}; lines not live {q.get('sampler_lines_not_live')}; ages at host start {ages}; (pass, gap, flagged) {rows}")
    ok(r.returncode == 0 and "line(s) since without a stop line's reading): restarting it" in log and log.count("sampler started (attempt") >= 2
       and (q.get("sampler_lines_not_live") or 0) > 0 and len(ran) >= 5 and all(a is not None and a < 2.0 for a in ages) and fc
       and "DRY session end" in log,
       "F4: lines without board_w never kept the sampler live: it was restarted (SIGTERM), every host started on a live sample, each pass "
       "flagged exactly when its largest live-sample gap was 2 s or more (verify-e191k2's break case kept the session 'live' on them)")
    print("== F5 (nit 1) every sampler of the session prints without board_w from the schedule's 9th launch: none counts as started")
    r, out, log, q = session(S, "f5", env={"E194_FAKE_SAMPLER": "noboard-all:9"})
    ran = passes_ran(q)
    ages = [rj(out, x["pass"]).get("sample_age_s_at_host_start") for x in ran]
    fc, rows = flags_consistent(out, q)
    print(f"   passes {len(ran)}; lines not live {q.get('sampler_lines_not_live')}; ages at host start {ages}; (pass, gap, flagged) {rows}")
    ok(r.returncode == 0 and "STOP: the sampler would not restart" in log and 1 <= len(ran) < 6 and all(a is not None and a < 2.0 for a in ages)
       and fc and (q.get("sampler_lines_not_live") or 0) > 0 and "DRY session end" in log,
       "F5: a sampler printing only lines without board_w never counts as started: 'the sampler would not restart' ended the queue")
    print("== F6 (nit 2) the sampler prints nothing for 3 s from the schedule's 9th launch (pass 1's 2nd), then prints again; idles 3 s")
    r, out, log, q = session(S, "f6", env={"E194_FAKE_SAMPLER": "pause:9:3"},
                             seq_args=["--sequence", "short", "--idle-before", "3", "--idle-after", "3", "--anchor-s", "0.5", "--die-wait-s", "2"])
    ran = passes_ran(q)
    fc, rows = flags_consistent(out, q)
    p1 = rj(out, "copy-zeros/p1")
    print(f"   passes {len(ran)}; pass 1: ages at host start/end and pass end {p1.get('sample_age_s_at_host_start')} / "
          f"{p1.get('sample_age_s_at_host_end')} / {p1.get('sample_age_s_at_pass_end')}, largest gap {p1.get('live_gap_s_pass')} s; (pass, gap, flagged) {rows}")
    ok(r.returncode == 0 and len(ran) == 6 and fc and q.get("passes_sampler_not_live") == ["copy-zeros/p1"]
       and 2.0 <= (p1.get("live_gap_s_pass") or 0) <= 4.0 and (p1.get("sample_age_s_at_host_end") or 9) < 2.0
       and "the sampler was not live during this pass: no live sample for" in log and "STOP" not in log,
       "F6: the pass in which the sampler paused is flagged by its largest live-sample gap (its age at the host's end alone was under 2 s); "
       "no other pass is flagged; the session goes on")
    print("== F8 (fix-e194, nit 7) six sampler lines of other shapes inside pass 1 (the schedule's 9th launch): the reader lives on")
    r, out, log, q = session(S, "f8", env={"E194_FAKE_SAMPLER": "malformed:9"})
    ran = passes_ran(q)
    fc, rows = flags_consistent(out, q)
    print(f"   passes {len(ran)}; lines not live {q.get('sampler_lines_not_live')}; lines whose reading raised {q.get('sampler_lines_unreadable')} "
          f"{q.get('sampler_line_errors')}; sampler starts {log.count('sampler started (attempt')}; (pass, gap, flagged) {rows}")
    ok(r.returncode == 0 and len(ran) == 6 and all(x.get("reading") == "PASS" for x in ran) and (q.get("sampler_lines_not_live") or 0) >= 6
       and q.get("sampler_lines_unreadable") == 0 and log.count("sampler started (attempt") == 1 and "the sampler is not live" not in log
       and not q.get("passes_sampler_not_live") and fc,
       "F8: the six lines read as not live, none raised in the reader, the sampler never restarted, no pass flagged, six passes PASS")
    print("== F7 (nit 2) the sampler goes quiet at the schedule's 9th launch, with the REGISTERED 8 s / 10 s idles (the verifier's X9b)")
    r, out, log, q = session(S, "f7", env={"E194_FAKE_SAMPLER": "hangs:9"},
                             seq_args=["--sequence", "short", "--anchor-s", "0.5", "--die-wait-s", "2", "--cap-pass-s", "30"])
    ran = passes_ran(q)
    fc, rows = flags_consistent(out, q)
    p1 = rj(out, "copy-zeros/p1")
    print(f"   passes {len(ran)}; pass 1's host span: {p1.get('live_samples_host')} live sample(s), gap {p1.get('live_gap_s_host')} s; "
          f"(pass, gap, flagged) {rows}")
    ok(r.returncode == 0 and len(ran) >= 2 and fc and (q.get("passes_sampler_not_live") or [None])[0] == "copy-zeros/p1"
       and not not_live_flag(out, ran[1]["pass"]) and "restarting it" in log and "DRY session end" in log,
       "F7: with the registered idles the pass in which the sampler went quiet is flagged (X9b: no runner flag); the sampler restarted "
       "before pass 2, which is not flagged")
    # ---- finding 3: et-who unreadable
    for name, env, word in (("w1", {"E194_FAKE_ETWHO": "fail"}, "et-who unreadable (rc 1, nothing on its stdout)"),
                            ("w2", {"E194_FAKE_ETWHO": "garbled"}, "et-who unreadable (rc 0, but neither a holder line nor its no-holder sentence)")):
        print(f"== {name.upper()} et-who before the first card command: {env['E194_FAKE_ETWHO']}")
        r, out, log, q = session(S, name, env=env)
        ok(r.returncode == 16 and word in log and "no device opened" in log and "config start" not in log
           and not os.path.exists(os.path.join(out, "config-start.json")), f"{name}: unreadable, refused before the first card command, rc 16")
    print("== W3 et-who refused from its 4th call on (the holder rule before pass 2)")
    r, out, log, q = session(S, "w3", env={"E194_FAKE_ETWHO": "fail", "E194_FAKE_ETWHO_FROM": "4"})
    ok(r.returncode == 0 and len(passes_ran(q)) == 1 and "STOP before pass 2: et-who unreadable (rc 1" in log and "config end: TDP" in log,
       "STOP before pass 2 (an unread holder rule is never 'no holder'), the closing read, rc 0")
    print("== W4 et-who refused at its 2nd call (the identity read, with the sampler running)")
    r, out, log, q = session(S, "w4", env={"E194_FAKE_ETWHO": "fail", "E194_FAKE_ETWHO_FROM": "2"})
    ok(r.returncode == 16 and "identity (b): IDENTITY GATE FAILED: et-who unreadable" in log and "the gate, no launch" in log
       and not os.path.isdir(os.path.join(out, "smoke")), "the identity gate (b) fails, rc 16, no host")
    # ---- finding 5: the early stop
    for name, how in (("q1", "the stop file"), ("q2", "a SIGTERM to the runner")):
        print(f"== {name.upper()} {how} while pass 2's host runs")
        p, out = session_bg(S, name)
        started = wait_for(lambda: pass_launches(out) > 8, 120, 0.01)
        if started:
            if name == "q1":
                open(os.path.join(out, "STOP"), "w").close()
            else:
                p.send_signal(signal.SIGTERM)
        rc, log, q = finish_bg(p, out, name)
        ran = [x["pass"] for x in passes_ran(q)]
        ia = idle_after_ms(out, "copy-random/p1")
        ok(started and rc == 0 and ran == ["copy-zeros/p1", "copy-random/p1"] and f"STOP: an early stop was asked for ({how}" in log
           and ia >= 450 and "config end: TDP" in log and (q.get("early_stop") or "").startswith(f"an early stop was asked for ({how}")
           and "DRY session end" in log and os.path.exists(os.path.join(out, "MANIFEST.sha256")),
           f"{name}: pass 2's host ended by itself and kept its idle after ({ia} ms), no further pass, the closing read, queue.json, the manifest, rc 0")
    print("== Q3 the stop file present before the session")
    d = os.path.join(S, "q3")
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, "T"))
    open(os.path.join(d, "T", "STOP"), "w").close()
    r = subprocess.run([PY, "-I", "-B", RUN, "session", "--dry", "--t0", "1", "--out", os.path.join(d, "T")] + FAST, cwd=REPO,
                       env=dict(os.environ, E194_FAKE_SCALE="0.05"), capture_output=True, text=True, timeout=300)
    log = open(os.path.join(d, "T", "session.log")).read()
    ok(r.returncode == 16 and "before the first card command: no device opened" in log and not os.path.exists(os.path.join(d, "T", "config-start.json")),
       "no device opened, rc 16")
    # ---- fix-e191k2: the second verifier's nit 3 (an early stop asked for at the gate is logged as one, never as a failed stop path)
    for name, after, delay, word in (("q4", "config start:", 0.0, "before the stop-path test: the gate, no launch"),
                                     ("q5", "identity (b): et-who with the sampler running", 0.05,
                                      "during the stop-path test (its lines not read): the gate, no launch")):
        print(f"== {name.upper()} the stop file written {delay * 1000:.0f} ms after the session log reads '{after[:40]}' (verify-e191k2's break case; "
              f"the stop-path test's three lines take 0.3 s or more)")
        p, out = session_bg(S, name)
        seen = wait_for(lambda: in_log(out, after), 120, 0.002)
        if seen:
            time.sleep(delay)
            open(os.path.join(out, "STOP"), "w").close()
        rc, log, q = finish_bg(p, out, name)
        sp = json.load(open(os.path.join(out, "stop-path.json"))) if os.path.exists(os.path.join(out, "stop-path.json")) else {}
        ok(seen and rc == 16 and word in log and "stop-path test failed" not in log and "stop-path test passed" not in log
           and (q.get("early_stop") or "").startswith("an early stop was asked for (the stop file") and "config end: TDP" in log
           and not os.path.isdir(os.path.join(out, "smoke")) and "DRY session end" in log and os.path.exists(os.path.join(out, "MANIFEST.sha256"))
           and (name == "q4" or (sp.get("early_stop") or "").startswith("an early stop was asked for")),
           f"{name}: an early stop at the gate, logged as one ('{word[:40]}...'; step 10 reads GATE-STOPPED), never 'stop-path test failed'; "
           "no smoke, the closing read, queue.json's early_stop, rc 16")
    print("== D1 the dry check's refusals on recorded command lines (for this box: ET_DEVICES and V3_DEVICE unset, nothing of another card)")
    sys.path.insert(0, HERE)
    import run_e194 as RR
    d = os.path.join(S, "d1")
    os.makedirs(d, exist_ok=True)
    good = {"kind": "host", "real": ["timeout", "10", "build/e194ledger/host/ledger_host", "--card"], "et_devices": None, "v3_device": None,
            "opens_device": True, "lock": "/run/lock/etsoc-shire0.lock"}
    rows_bad = {"ET_DEVICES set": dict(good, et_devices="0"), "V3_DEVICE set": dict(good, v3_device="1"),
                "etsoc-shire1": dict(good, real=["flock", "/run/lock/etsoc-shire1.lock", "x"]), "/dev/et1_": dict(good, real=["cat", "/dev/et1_mgmt"]),
                "ET_DEVICES=0 in a command": dict(good, real=["env", "ET_DEVICES=0", "x"]), "V3_DEVICE=1 in a command": dict(good, real=["env", "V3_DEVICE=1", "x"]),
                "dev_mngt_service": dict(good, real=["dev_mngt_service", "-n", "1"]), "et-powertop": dict(good, real=["et-powertop"]),
                "a lock not card 0's": dict(good, lock="/run/lock/etsoc-shire1.lock")}
    verdicts = {}
    for k, row in [("good", good)] + list(rows_bad.items()):
        with open(os.path.join(d, "commands.jsonl"), "w") as f:
            f.write(json.dumps(row) + "\n")
        why, nn = RR.Session.dry_check(type("O", (), {"out": d})())
        verdicts[k] = "ok" if not why else "FAILED"
    print(f"   {verdicts}")
    ok(verdicts["good"] == "ok" and all(verdicts[k] == "FAILED" for k in rows_bad), "each forbidden form read FAILED; the good line ok")
    if e2e:
        home, tree = box_tree(S)
        print("== E2E energy_stub's alt sampler under the doubles' clock, the registered 8 s / 10 s idles and 1.5 s climb, from a stand-in box tree")
        r, out, log, q = session(S, "e2e", seq_args=["--sequence", "e2e"], double="alt", env={"E194_FAKE_SCALE": "1"}, tree=tree)
        okred, data, sj, rsc = collect_score(S, "e2e", out, home)
        flags, nclock = [], 0
        for x in passes_ran(q):
            en = energy(data, x["pass"])
            okred = okred and reduced_ok(en) and en.get("dir") == os.path.join(os.path.basename(data), "passes", x["pass"])
            flags += en.get("flags", [])
            nclock += any(h.startswith(CLOCK_LINE) for h in en.get("hard", []))
        okj = check_energies(out, data, [x["pass"] for x in passes_ran(q)])
        cfg = sj.get("configs", {})
        nod = sorted(k for k, c in cfg.items() if c.get("verdict") == "NO DATA")
        scored = sorted(k for k, c in cfg.items() if c.get("passes") == 2)
        v = sj.get("verdict_of_the_day") or {}
        for k in scored:
            c = cfg[k]
            print(f"   scored {k}: e_j_over {100 * c['e_j_over']:+.1f}%, e_j_total {100 * c['e_j_total']:+.1f}%, t_k/point "
                  f"{c['t_k_mean'] / c['t_point']:.4f}, e_j_total_forecast {100 * c['e_j_total_forecast']:+.1f}%")
        print(f"   scorer rc {rsc}; scored {scored}; NO DATA {nod}; verdicts {v}; not used {sj.get('not_used')}")
        print(f"   the reducer's clock line (read by THE CLOCK RULE, never a failure): {nclock} of {len(passes_ran(q))} passes; any other hard "
              f"line: none in a pass read ok")
        ok(r.returncode == 0 and len(passes_ran(q)) == 6 and all(x.get("clock") == "ok" for x in passes_ran(q)) and okred
           and any("DRY" in f for f in flags) and scored == ["copy-zeros", "sha256", "sparse-parity"]
           and nod == ["copy-random", "sort-shuffled", "sort-sorted"],
           "from the box tree: every pass's clock ok (the registered 1.5 s climb), COPY-BACK EXACT and THE BOX-TREE GATE passed, every pass "
           "reduced (flagged DRY; no hard line but the clock line, as the scorer reads it), the frozen scorer (its clock rule) read three "
           "configurations and three NO DATA")
        ok(okj, "each pass's reduced J over idle within TOL of the energy the alt card injected (fault 1)")
        ok(v.get("E194-S1") == "NOT DECIDED" and v.get("E194-S2") == "NOT DECIDED" and len(v) == 4
           and set(v.values()) <= {"PASS", "FAIL", "NOT DECIDED"},
           "the verdict words: S1 and S2 NOT DECIDED (as injected: 3 scored, all within; 3 NO DATA); S1T and S2T words only")
        print("== BT THE BOX-TREE GATE: the same session with a desk path written in (the lab clone's form) and with a scratch root")
        res = []
        for nm, text in (("bt1", f"{home}/git/et-soc1-prototyping/tools/claims-v3/e194/run_e194.py"), ("bt2", "/tmp/claude-9999/x/scratchpad/y")):
            cp = os.path.join(S, nm, "copy")
            if os.path.isdir(os.path.join(S, nm)):
                shutil.rmtree(os.path.join(S, nm))
            shutil.copytree(out, cp)
            os.remove(os.path.join(cp, "dry.lock"))
            open(os.path.join(cp, "runner.rc"), "w").write("0\n")
            with open(os.path.join(cp, "session.log"), "a") as f:
                f.write(f"2026-11-15 12:00:00 PST note: {text}\n")
            man = os.path.join(cp, "MANIFEST.sha256")
            rows = [ln.rstrip("\n").split("  ", 1) for ln in open(man) if ln.strip()]
            with open(man, "w") as f:
                f.write("\n".join(f"{hashlib.sha256(open(os.path.join(cp, p), 'rb').read()).hexdigest() if p == 'session.log' else h}  {p}"
                                  for h, p in rows) + "\n")
            data = os.path.join(S, nm, "2026-11-15-e194-blind-day-aifoundry2")
            lgf = os.path.join(S, nm, "box-login.txt")
            open(lgf, "w").write(pwd.getpwuid(os.getuid()).pw_name + "\n")
            x = subprocess.run([PY, "-B", os.path.join(HERE, "collect_e194.py"), cp, data, "--box-home", home, "--box-login", lgf, "--data-outside"],
                               cwd=REPO, capture_output=True, text=True, timeout=300, env=dict(os.environ, RB_DESKTEST="1"))
            gl = [ln for ln in x.stdout.splitlines() if ln.startswith("BOX-TREE GATE")]
            said = (gl[0] if gl else x.stdout[-200:]).replace(S, "<scratch>")       # the scratch root masked in the log
            print(f"   {nm}: rc {x.returncode}; {said[:200]}; data written {os.path.exists(data)}")
            res.append(x.returncode == 3 and gl and "a desk path in the session's files" in gl[0] and not os.path.exists(data)
                       and "COPY-BACK EXACT" in x.stdout)
        ok(all(res) and len(res) == 2, "COPY-BACK EXACT, then the box-tree gate refused a desk path under the home outside the box tree, and a "
                                       "scratch root: nothing written (exit 3)")
        for name, inj, word, stopped, want_ran, want_scored in (
                ("r2e", [{"during": "pass", "after_pass_launches": 27, "board_w": 66.0, "count": 1}], "STOP: board 66.0 W at or above 65 W",
                 "copy-zeros/p2", 4, ["copy-zeros"]),
                ("r3e", [{"during": "pass", "after_pass_launches": 35, "die": 70, "count": 1}], "STOP: minshire[0] 70 C at or above 70 C",
                 "sha256/p2", 5, ["copy-zeros", "sha256"])):
            print(f"== {name.upper()} the {'board' if name == 'r2e' else 'die'} line during {stopped} on the alt card; reduced and scored")
            r, out, log, q = session(S, name, inject=inj, double="inject", env={"E194_FAKE_SCALE": "1", "E194_FAKE_BASE": "alt"},
                                     seq_args=["--sequence", "e2e", "--anchor-s", "5"], tree=tree)
            ran = [x["pass"] for x in passes_ran(q)]
            lp = pj(out, stopped)
            ia = idle_after_ms(out, stopped)
            print(f"   passes run {ran}; the stopped pass {stopped}: {ia} ms from its host's end to its end; flags {lp.get('flags')}")
            okr = (r.returncode == 0 and word in log and ran and ran[-1] == stopped and len(ran) == want_ran
                   and (lp.get("flags") or [""])[0].startswith("a stop line tripped") and ia >= 9950)
            okred, data, sj, rsc = collect_score(S, name, out, home)
            en = energy(data, stopped)
            cutflag = [f for f in en.get("flags", []) if "telemetry ends" in f]
            okj = check_energies(out, data, ran, card="alt")
            cfg = sj.get("configs", {})
            scored = sorted(k for k, c in cfg.items() if c.get("verdict") != "NO DATA")
            pp = [row.get("pass") for row in (cfg.get(stopped.split("/")[0]) or {}).get("per_pass", [])]
            notused = [x for x in sj.get("not_used", []) if x.startswith(stopped)]
            print(f"   scorer rc {rsc}; scored {scored}; {stopped.split('/')[0]}'s scored passes {pp}; not used {sj.get('not_used')}")
            ok(okr, f"{name}: the process finished, its pass flagged and its 10 s after whole, the queue ended after it")
            ok(okred and reduced_ok(en) and not cutflag and okj and scored == want_scored and pp == [1, 2] and not notused,
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
    print(f"SELFTEST-RUN-E194 {n} of {len(results)} {'PASS' if n == len(results) else 'FAIL'}")
    return 0 if n == len(results) else 1


if __name__ == "__main__":
    S = sys.argv[1]
    if os.path.abspath(S).startswith(REPO + os.sep):
        sys.exit("the scratch directory must be outside the repository")
    os.makedirs(S, exist_ok=True)
    sys.exit(main(os.path.abspath(S), e2e="--no-e2e" not in sys.argv))
