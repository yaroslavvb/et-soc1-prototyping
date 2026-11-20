#!/usr/bin/env python3
"""E220 ARM B (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum; E216's desk/selftest_run_e216.py form, landed in 59f5288b): THE
RUNNER ON THE DOUBLES - what box/run_e220b.py adds to E208's runner, each seen working and failing, on E208's doubles and E220's rgm211-host
double (box/fake_card_e220b.py), every case a whole dry session of arm B's registered schedule (box/a2c0-E220.json: 103 runs, s01 E208's three
smoke arms, t01 at runs 1 and 86, s03 at run 87, the G block's 16 runs last) at scale 0.02 in a box root of its own (make_box_e220b.py sync,
the REAL built ELFs copied in from a built root: the identity gate reads them), then E208's reducer UNCHANGED and the frozen scorer
(score_e220.py --b) on what the case left. No device is opened (the doubles); it refuses unless no /dev/et* is a device node (run it inside
W/nodev.sh). Standard library only.

    bash W/slot.sh bash W/nodev.sh /usr/bin/python3 -I -B tools/claims-v3/e220/desk/selftest_run_e220b.py <scratch> --built <built root> [case ...]
        <built root>: a box root after runbook step 6 (desk/desktest_build_e220b.sh's <scratch>/root): build/rgm/kernel/sparsity.elf (E136's
        pin) and build/e220brgm211/kernel/sparsity.elf (rgm211's own ELF, for the gate's refusals) are read from it

THE CASES (a double's arm id is the host's shape: t01 2x4x4-fp32-rnd, n03t 2x6x28-fp32-rnd, s03 nc6x5x10-fp32-rnd, xg08 nc2x14x16-fp32-rnd):
  FULL    the whole schedule: 103 runs in the registered order, 106 processes gated OK (89 'rgm136 gemmL' with the smoke's three, 17
          'rgm136 gemmLnc' on rgm211's host's double: s03 and the G block, the last 17 host calls), every host call under its sized plain
          timeout (`timeout 13` on xf04 alone, `timeout 10` on every other), E220's lines in the stop-path record (70 W x 3, 70 C), no stop;
          the reducer reads 103 runs; the frozen scorer B:R0 PASS, every registered point of arm B read (route c or m)
  LINE71  the board 26 W over the toy card's capped lift in n03t (run 4): above 70 W on 3 samples: THE BOARD STOP (E220's line, not E208's
          85 W); nothing further starts
  LINE69  the same at 20 W (n03t's board at most about 68-70 W, read from the session's own telemetry): no stop; the session runs on to the
          operator's STOP after run 6
  GTRIP   the board 60 W over in every G process alone: THE BOARD STOP in s03 (run 87), the G family's first run; every run before it (1-86)
          ran; the G block (88-103) not started
  KWALK3  s03's process prints walk_ok false: THE KERNEL STOP (the walk check) at run 87; the G block not started; the scorer: B:R0 PASS, s03
          not in R0 (an s03 failure while no gemmLnc point ran is never counted in R0: E220.md 3; the frozen scorer's arm B reader reads s03 as
          no registered point of arm B, so it is not among its flags either), and step 13's readings (rb/post_e220b.py after) REPORT the stop at
          run 087
  KCHECK3 s03's check of C reads wrong: THE KERNEL STOP at run 87; B:R0 PASS, s03 not in R0; the stop REPORTED at run 087 (the same rule)
  KCHECK  xg08's (run 88, the G block's first point) check of C reads wrong: THE KERNEL STOP; the scorer's B:R0 FAILS (a wrong C at a point
          labels the day)
  KTENSOR xg08's first launch reads a tensor error: THE KERNEL STOP at run 88
  KSLOW   s03's host is slow to its first launch past its `timeout 10`: rc 124, THE KERNEL STOP; nothing killed (the plain timeout's TERM)
  KGATE   rgm211's own ELF copied over build/rgm/kernel/sparsity.elf once the second tie's (run 86's) gate has passed: s03's gate refuses (.text rgm211's),
          NO PROCESS STARTS for it, THE IDENTITY GATE STOP; gates.jsonl names it; the scorer: B:R0 PASS (s03 did not run)
  KGATE0  rgm211's ELF in rgm136's place from the start: the smoke's first process refused by the gate (THE IDENTITY GATE STOP): the
          smoke gate fails, no run starts
  ORDER   a schedule with xg08 moved before the pass-2 block: the runner refuses it (no session, no device call)
  OVER    a schedule with xf14's planning peak 67.0 W: the runner refuses it (at or over E220 arm B's 67.0 W drop line)
  TWOFAIL every host after the 8th fails its check (E208's double): E208's rule, unchanged: two failed processes in a row stop the session
Prints one line a case and SELFTEST-RUN-E220B <n> of <m> PASS (or FAIL) last.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import json
import os
import shutil
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
PY = "/usr/bin/python3"
SCALE = "0.02"
CASES = ["FULL", "LINE71", "LINE69", "GTRIP", "KWALK3", "KCHECK3", "KCHECK", "KTENSOR", "KSLOW", "KGATE", "KGATE0", "ORDER", "OVER",
         "TWOFAIL"]
N_RUNS, G_FIRST, N_G = 103, 87, 17


def refuse_devices():
    for d in glob.glob("/dev/et*"):
        st = os.stat(d)
        import stat
        if stat.S_ISCHR(st.st_mode) or stat.S_ISBLK(st.st_mode):
            sys.exit(f"REFUSED: {d} is a device node here: run this inside W/nodev.sh")


def make_root(S, name, built):
    root = os.path.join(S, name, "root")
    os.makedirs(root)
    r = subprocess.run([PY, "-I", "-B", os.path.join(E, "make_box_e220b.py"), "sync", root], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("sync failed: " + r.stdout + r.stderr)
    for rel in ("build/rgm/kernel/sparsity.elf", "build/e220brgm211/kernel/sparsity.elf"):
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        shutil.copyfile(os.path.join(built, rel), os.path.join(root, rel))
    return root


def run_dry(root, extra, sched="src/sched/a2c0-E220.json", watch=None):
    out = os.path.join(root, "dry", "case")
    os.makedirs(out, exist_ok=True)
    cmd = [PY, "-B", "src/run_e220b.py", "session", "--dry", "--scale", SCALE, "--card", "a2c0", "--sched", sched, "--t0", "1",
           "--out", out] + extra
    t0 = time.time()
    with open(os.path.join(out, "runner.out"), "w") as fo:
        p = subprocess.Popen(cmd, cwd=root, stdout=fo, stderr=subprocess.STDOUT, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        if watch:
            threading.Thread(target=watch, args=(out,), daemon=True).start()
        rc = p.wait(timeout=900)
    return rc, out, time.time() - t0


def read(out):
    q = json.load(open(os.path.join(out, "queue.json"))) if os.path.exists(os.path.join(out, "queue.json")) else {}
    gates = [json.loads(ln) for ln in open(os.path.join(out, "gates.jsonl"))] if os.path.exists(os.path.join(out, "gates.jsonl")) else []
    log = open(os.path.join(out, "session.log")).read() if os.path.exists(os.path.join(out, "session.log")) else ""
    calls = open(os.path.join(out, "device-calls.txt")).read().splitlines() if os.path.exists(os.path.join(out, "device-calls.txt")) else []
    return q, gates, log, calls


def reduce_score(root, out, S, name):
    dj = os.path.join(S, name, "data.json")
    r = subprocess.run([PY, "-I", "-B", os.path.join(root, "src", "reduce_mms.py"), out, "--out", dj], capture_output=True, text=True)
    if r.returncode != 0:
        return None, f"reducer rc {r.returncode}: {r.stdout[-200:]}{r.stderr[-200:]}"
    sd = os.path.join(S, name, "scored")
    r = subprocess.run([PY, "-I", "-B", os.path.join(E, "score_e220.py"), "--b", dj, "--out", sd], capture_output=True, text=True)
    if r.returncode != 0:
        return None, f"scorer rc {r.returncode}: {r.stdout[-300:]}{r.stderr[-300:]}"
    return json.load(open(os.path.join(sd, "scores-e220.json"))), json.load(open(dj))


def load_post():
    import importlib.util
    spec = importlib.util.spec_from_file_location("post_e220b", os.path.join(E, "rb", "post_e220b.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def r0(sc):
    return (sc.get("verdicts") or {}).get("B:R0") if isinstance(sc, dict) else None


def bflags(sc):
    return (((sc.get("arms") or {}).get("B") or {}).get("flags") or []) if isinstance(sc, dict) else []


def ran_ids(q):
    return [x["arm"] for x in q.get("queue", []) if x.get("ran")]


def dbl_id(r):
    """the double's arm id of a schedule run (E208's fake card's rule; E220's G double prefixes 'nc')"""
    arm, gen, files = r["values"].split(":", 2)
    nc = arm.startswith("gemmLnc")
    mb, nb, kb = (int(x) for x in arm[7 if nc else 5:].split("x"))
    kind = "rnd" if gen == "randn" else ("zeros" if files.endswith("zeros.bin") else "ones")
    sh = bin(int(r["shires"], 16)).count("1")
    return ("nc" if nc else "") + f"{mb}x{nb}x{kb}-{r['type']}-{kind}" + ("" if sh == 32 else f"-s{sh}")


def sched_runs(root):
    return json.load(open(os.path.join(root, "src/sched/a2c0-E220.json")))["runs"]


def timeouts_of(calls):
    """(timeout, the host's --values) for each host call of the device-call record"""
    out = []
    for c in calls:
        if "sparsity_host" not in c:
            continue
        w = c.split()
        to = w[w.index("timeout") + 1] if "timeout" in w else None
        v = w[w.index("--values") + 1] if "--values" in w else None
        out.append((to, v))
    return out


def case(S, name, built):
    root = make_root(S, name, built)
    runs = sched_runs(root)
    assert len(runs) == N_RUNS and runs[G_FIRST - 1]["arm"] == "s03" and runs[85]["arm"] == "t01", "not E220 arm B's schedule"
    ID = {r["i"]: dbl_id(r) for r in runs}
    assert ID[4] == "2x6x28-fp32-rnd" and not any(ID[4] in ID[k] for k in (1, 2, 3)) and ID[87] == "nc6x5x10-fp32-rnd"
    extra, sched, watch = [], "src/sched/a2c0-E220.json", None
    if name == "LINE71":
        extra = ["--trip-arm", ID[4], "--trip-w", "26"]
    elif name == "LINE69":
        extra = ["--trip-arm", ID[4], "--trip-w", "20", "--stop-after", "6"]
    elif name == "GTRIP":
        extra = ["--g-extra-w", "60"]
    elif name == "KWALK3":
        extra = ["--g-walk-fail", ID[87]]
    elif name == "KCHECK3":
        extra = ["--g-check-wrong", ID[87]]
    elif name == "KCHECK":
        extra = ["--g-check-wrong", ID[88]]
    elif name == "KTENSOR":
        extra = ["--g-tensor-error", ID[88]]
    elif name == "KSLOW":
        extra = ["--g-slow", ID[87]]
    elif name == "TWOFAIL":
        extra = ["--host-fail-after", "8"]
    elif name == "KGATE0":
        shutil.copyfile(os.path.join(root, "build/e220brgm211/kernel/sparsity.elf"), os.path.join(root, "build/rgm/kernel/sparsity.elf"))
    elif name == "KGATE":
        def watch(out):
            deadline = time.time() + 600
            while time.time() < deadline:
                try:
                    gp = os.path.join(out, "gates.jsonl")       # the second tie's own gate passed (its process starts): swap before s03's
                    if os.path.exists(gp) and any(json.loads(ln).get("proc", "").startswith("runs/086-t01") and json.loads(ln).get("ok")
                                                  for ln in open(gp) if ln.strip()):
                        shutil.copyfile(os.path.join(root, "build/e220brgm211/kernel/sparsity.elf"),
                                        os.path.join(root, "build/rgm/kernel/sparsity.elf"))
                        open(os.path.join(S, name, "swapped"), "w").write(str(time.time()))
                        return
                except OSError:
                    pass
                time.sleep(0.05)
    elif name in ("ORDER", "OVER"):
        s = json.load(open(os.path.join(root, sched)))
        if name == "ORDER":
            rr = s["runs"]
            g = [r for r in rr if r["arm"] == "xg08"][0]
            rr.remove(g)
            k = [i for i, r in enumerate(rr) if r["block"] == "pass2"][0]
            rr.insert(k, g)
            for i, r in enumerate(rr, 1):
                r["i"] = i
        else:
            [r for r in s["runs"] if r["arm"] == "xf14"][0]["est_peak_w"] = 67.0
        sched = "src/sched/case.json"
        json.dump(s, open(os.path.join(root, sched), "w"), indent=1)
    rc, out, secs = run_dry(root, extra, sched, watch)
    q, gates, log, calls = read(out)
    ran = ran_ids(q)
    stop = q.get("stop") or ""
    ok, why = False, ""
    after_ran = lambda k: any(x.get("ran") for x in q["queue"][k:])  # noqa: E731
    if name == "FULL":
        sp = json.load(open(os.path.join(out, "stop-path.json")))
        gfam = [g for g in gates if g["family"] == "rgm136 gemmLnc"]
        hostcalls = [c for c in calls if "sparsity_host" in c]
        tos = timeouts_of(calls)
        t13 = sorted({v for to, v in tos if to == "13"})
        t_other = sorted({to for to, v in tos if to != "13"})
        want13 = [r["values"] for r in runs if r.get("timeout_s") == 13]
        sc, dj = reduce_score(root, out, S, name)
        pids = [x["id"] for x in json.load(open(os.path.join(E, "points-e220.json")))["points"]["B"]]
        B = ((sc.get("arms") or {}).get("B") or {}) if isinstance(sc, dict) else {}
        unread = [pid for pid in pids if not ((B.get("measured") or {}).get(pid) or (B.get("route_m_REPORTED") or {}).get(pid))]
        okscore = isinstance(sc, dict) and r0(sc) == "PASS" and len(dj["runs"]) == N_RUNS and not unread
        ok = (rc == 0 and len(ran) == N_RUNS and not stop and len(gates) == 3 + N_RUNS and all(g["ok"] for g in gates) and len(gfam) == N_G
              and all("e220brgm211" in c for c in hostcalls[-N_G:]) and not any("e220brgm211" in c for c in hostcalls[:-N_G])
              and t13 == want13 and t_other == ["10"] and len(tos) == len(hostcalls)
              and sp["real_lines"] == {"board_cap_w": 70.0, "cap_consecutive": 3, "abs_stop_c": 70.0} and sp["ok"] and okscore)
        why = (f"rc {rc}, {len(ran)} runs ran, {len(gates)} gates OK {sum(g['ok'] for g in gates)} ({len(gfam)} G), the last {N_G} host calls "
               f"rgm211's: {all('e220brgm211' in c for c in hostcalls[-N_G:])}; timeout 13 on {t13} (want {want13}), every other {t_other}; real "
               f"lines {sp['real_lines']}; B:R0 {r0(sc)}; {len(dj['runs']) if isinstance(dj, dict) else dj} runs reduced; unread points {unread[:6]}; "
               f"{secs:.0f} s")
    elif name == "LINE71":
        ok = rc == 0 and "board" in stop and "70 W" in stop and ran == ["t01", "n01t", "xf14", "n03t"] and not after_ran(4)
        why = f"rc {rc}, stop '{stop}', ran {ran}"
    elif name == "LINE69":
        tel = [json.loads(ln) for ln in gzip.open(os.path.join(out, "telemetry.jsonl.gz"), "rt")]
        rj = json.load(open(os.path.join(out, "runs", "004-n03t", "run.json")))
        w = [x["board_w"] for x in tel if rj["procs"][0]["t0_ms"] <= x["t_ms"] <= rj["procs"][0]["t1_ms"] and x.get("board_w") is not None]
        top = max(w) if w else None
        ok = rc == 0 and "operator" in stop and "board" not in stop and len(ran) == 6 and top is not None and 65.0 < top <= 70.0
        why = f"rc {rc}, stop '{stop}', {len(ran)} ran; n03t's board at most {top} W (under the 70 W line: no stop)"
    elif name == "GTRIP":
        ok = (rc == 0 and "board" in stop and "70 W" in stop and len(ran) == G_FIRST and ran[-1] == "s03"
              and all(x.get("ran") for x in q["queue"][:G_FIRST - 1]) and not after_ran(G_FIRST))
        why = f"rc {rc}, stop '{stop}', ran {len(ran)} (last {ran[-1] if ran else None}); the G block started: {after_ran(G_FIRST)}"
    elif name in ("KWALK3", "KCHECK3", "KCHECK", "KTENSOR", "KSLOW"):
        word = {"KWALK3": "the walk check", "KCHECK3": "its check of C wrong", "KCHECK": "its check of C wrong", "KTENSOR": "tensor error",
                "KSLOW": "rc 124"}[name]
        at = 88 if name in ("KCHECK", "KTENSOR") else 87
        key = f"{at:03d}-{runs[at - 1]['arm']}"
        rj = json.load(open(os.path.join(out, "runs", key, "run.json")))
        pr = rj["procs"][0]
        sc, dj = reduce_score(root, out, S, name)
        want_r0 = "FAIL" if name == "KCHECK" else "PASS"
        r0f = ((((sc.get("arms") or {}).get("B") or {}).get("rules") or {}).get("R0") or {}).get("failures") or [] if isinstance(sc, dict) else []
        s03_in_r0 = any("s03" in f for f in r0f)
        # the session's stop as step 13's readings REPORT it (rb/post_e220b.py after): the frozen scorer reads s03 as no point of arm B
        # (read_b: a run whose id is not a registered point is not read), so an s03 failure is neither in R0 nor among its flags there
        PO = load_post()
        rep = PO.after(os.path.join(S, name, "data.json"), os.path.join(S, name, "scored", "scores-e220.json")) if isinstance(sc, dict) else {}
        named = str((rep.get("session_stop") or {}).get("run", ""))
        ok = bool(rc == 0 and "KERNEL STOP" in stop and word in stop and len(ran) == at and ran[-1] == runs[at - 1]["arm"] and not after_ran(at)
                  and pr.get("family") == "rgm136 gemmLnc" and r0(sc) == want_r0 and (at != 87 or not s03_in_r0) and named.startswith(f"{at:03d}-")
                  and (name != "KWALK3" or pr["walk"]["ok"] is False) and (name != "KSLOW" or pr["rc"] == 124))
        why = (f"rc {rc}, stop '{stop[:110]}', {len(ran)} ran (last {ran[-1] if ran else None}); {key} rc {pr.get('rc')}, walk "
               f"{(pr.get('walk') or {}).get('words', '')[:60]}; B:R0 {r0(sc)} (want {want_r0}; s03 in R0's failures: {s03_in_r0}); the stop REPORTED "
               f"by post_e220b at run {named!r}")
    elif name == "KGATE":
        swapped = os.path.exists(os.path.join(S, name, "swapped"))
        g3 = [g for g in gates if g["proc"].startswith("runs/087-s03")]
        rj = json.load(open(os.path.join(out, "runs", "087-s03", "run.json")))
        pr = rj["procs"][0]
        sc, dj = reduce_score(root, out, S, name)
        ok = (rc == 0 and swapped and "IDENTITY GATE STOP" in stop and "identity gate refused" in stop and g3 and not g3[0]["ok"]
              and "rgm211" in g3[0]["words"] and pr.get("not_started") and not os.path.exists(os.path.join(out, "runs", "087-s03", "proc-00.out"))
              and not after_ran(G_FIRST) and r0(sc) == "PASS")
        why = (f"rc {rc}, swapped {swapped}, stop '{stop[:100]}', s03's gate {g3[0]['words'][:70] if g3 else None}; no process started: "
               f"{bool(pr.get('not_started'))}; B:R0 {r0(sc)}; flags {[f for f in bflags(sc) if 's03' in f][:2]}")
    elif name == "KGATE0":
        ok = rc == 16 and "smoke gate failed" in log and len(gates) == 1 and not gates[0]["ok"] and not ran and "IDENTITY GATE STOP" in stop
        why = f"rc {rc}, gates {len(gates)} ({gates[0]['words'][:60] if gates else None}), ran {len(ran)}, stop '{stop[:60]}'"
    elif name in ("ORDER", "OVER"):
        ro = open(os.path.join(out, "runner.out")).read()
        word = "the G block is not last" if name == "ORDER" else "at or over the 67.0 W line"
        ok = rc != 0 and word in ro and not calls and not q
        why = f"rc {rc}, '{word}' in its words: {word in ro}, device calls {len(calls)}"
    elif name == "TWOFAIL":
        ok = rc == 0 and "2 failed processes in a row" in stop
        why = f"rc {rc}, stop '{stop}', {len(ran)} ran"
    return ok, why


def main(argv):
    refuse_devices()
    if len(argv) < 3 or argv[1] != "--built":
        print(__doc__)
        return 2
    S, built = os.path.abspath(argv[0]), os.path.abspath(argv[2])
    os.makedirs(S, exist_ok=True)
    if os.listdir(S):
        print("give an empty scratch directory")
        return 2
    want = argv[3:] or CASES
    n = p = 0
    for name in want:
        t = time.time()
        try:
            ok, why = case(S, name, built)
            ok = bool(ok)
        except Exception as e:  # noqa: BLE001
            ok, why = False, f"{type(e).__name__}: {e}"
        n += 1
        p += ok
        print(f"CASE {name}: {'PASS' if ok else 'FAIL'} ({why}) [{time.time() - t:.0f} s]", flush=True)
    print(f"SELFTEST-RUN-E220B {p} of {n} {'PASS' if p == n else 'FAIL'}")
    return 0 if p == n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
