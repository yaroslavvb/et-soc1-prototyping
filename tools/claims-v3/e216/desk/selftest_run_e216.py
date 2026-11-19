#!/usr/bin/env python3
"""E216 (Q227, lane kit-e216, Thu 19 Nov 2026, before any E216 datum): THE RUNNER ON THE DOUBLES - what src/run_e216.py adds to E208's runner,
each seen working and failing, on E208's doubles and E216's rgm211-host double (src/fake_card_e216.py), every case a whole dry session of
E216's registered schedule at scale 0.02 in a box root of its own (make_box_e216.py sync, the REAL built ELFs copied in from a built root:
the identity gate reads them), then E208's reducer UNCHANGED and the frozen scorer on what the case left. No device is opened (the doubles);
it refuses unless no /dev/et* is a device node (run it inside W/nodev.sh). Standard library only.

    bash W/slot.sh bash W/nodev.sh /usr/bin/python3 -I -B tools/claims-v3/e216/desk/selftest_run_e216.py <scratch> --built <built root> [case ...]
        <built root>: a box root after runbook step 6 (desk/desktest_build_e216.sh's <scratch>/root): build/rgm/kernel/sparsity.elf (E136's
        pin) and build/e216rgm211/kernel/sparsity.elf (rgm211's own ELF, for the gate's refusals) are read from it

THE CASES:
  FULL    the whole schedule: 69 runs in the registered order, 70 processes gated OK (60 'rgm136 gemmL', 10 'rgm136 gemmLnc' on rgm211's host's
          double, the last ten host calls), E216's lines in the stop-path record (70 W x 3, 70 C), no stop; the reducer reads 69 runs; the
          frozen scorer R0 PASS, every registered point read (route c or m)
  LINE71  the board 26 W over the toy card's capped lift in f03 (run 3): above 70 W on 3 samples: THE BOARD STOP (E216's line, not E208's
          85 W); nothing further starts
  LINE69  the same at 20 W (f03's board at most about 68-70 W, read from the session's own telemetry): no stop; the session runs on to the
          operator's STOP after run 6
  GTRIP   the board 60 W over in every G process alone (the double names G arms 'nc...'): THE BOARD STOP in g07, the G block's first run;
          every run before it (1-59) ran; g08-g01 not started
  KWALK   g07's process prints walk_ok false: THE KERNEL STOP (the walk check); g08-g01 not started; the scorer: g07 set aside (no ok launch)
          and R0 still PASS (only runs that ran are read), H2w TOO FEW or NO DATA
  KCHECK  g07's check of C reads wrong: THE KERNEL STOP; the scorer's R0 FAILS (a wrong C labels the day)
  KTENSOR g07's first launch reads a tensor error: THE KERNEL STOP
  KSLOW   g07's host is slow to its first launch past `timeout 10`: rc 124, THE KERNEL STOP; nothing killed (the plain timeout's TERM)
  KGATE   rgm211's own ELF copied over build/rgm/kernel/sparsity.elf while N2 (run 59) runs: g07's gate refuses (.text rgm211's), NO PROCESS
          STARTS for it, THE IDENTITY GATE STOP; gates.jsonl names it; the scorer reads g07 'did not run', R0 PASS
  KGATE0  rgm211's ELF in rgm136's place from the start: the smoke's first process refused by the gate (THE IDENTITY GATE STOP): the
          smoke gate fails, no run starts
  ORDER   a schedule with g07 moved before the pass-2 block: the runner refuses it (no session, no device call)
  OVER    a schedule with f03's planning peak 64.5 W: the runner refuses it (over E216's 64.0 W line)
  TWOFAIL every host after the 8th fails its check (E208's double): E208's rule, unchanged: two failed processes in a row stop the session
Prints one line a case and SELFTEST-RUN-E216 <n> of <m> PASS (or FAIL) last.
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
CASES = ["FULL", "LINE71", "LINE69", "GTRIP", "KWALK", "KCHECK", "KTENSOR", "KSLOW", "KGATE", "KGATE0", "ORDER", "OVER", "TWOFAIL"]


def refuse_devices():
    for d in glob.glob("/dev/et*"):
        st = os.stat(d)
        import stat
        if stat.S_ISCHR(st.st_mode) or stat.S_ISBLK(st.st_mode):
            sys.exit(f"REFUSED: {d} is a device node here: run this inside W/nodev.sh")


def make_root(S, name, built):
    root = os.path.join(S, name, "root")
    os.makedirs(root)
    r = subprocess.run([PY, "-I", "-B", os.path.join(E, "make_box_e216.py"), "sync", root], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("sync failed: " + r.stdout + r.stderr)
    for rel in ("build/rgm/kernel/sparsity.elf", "build/e216rgm211/kernel/sparsity.elf"):
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        shutil.copyfile(os.path.join(built, rel), os.path.join(root, rel))
    return root


def run_dry(root, extra, sched="src/sched/a2c0-E216.json", watch=None):
    out = os.path.join(root, "dry", "case")
    os.makedirs(out, exist_ok=True)
    cmd = [PY, "-B", "src/run_e216.py", "session", "--dry", "--scale", SCALE, "--card", "a2c0", "--sched", sched, "--t0", "1",
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
    sj = os.path.join(S, name, "scores.json")
    r = subprocess.run([PY, "-I", "-B", os.path.join(E, "score_e216.py"), dj, "--out", sj], capture_output=True, text=True)
    if r.returncode != 0:
        return None, f"scorer rc {r.returncode}: {r.stdout[-300:]}{r.stderr[-300:]}"
    return json.load(open(sj)), json.load(open(dj))


def ran_ids(q):
    return [x["arm"] for x in q.get("queue", []) if x.get("ran")]


def g_ids():
    return ["g07", "g08", "g09", "g10", "g03", "g04", "g05", "g06", "g02", "g01"]


def case(S, name, built):
    root = make_root(S, name, built)
    extra, sched, watch = [], "src/sched/a2c0-E216.json", None
    if name == "LINE71":
        extra = ["--trip-arm", "10x15x2-fp32-rnd", "--trip-w", "26"]
    elif name == "LINE69":
        extra = ["--trip-arm", "10x15x2-fp32-rnd", "--trip-w", "20", "--stop-after", "6"]
    elif name == "GTRIP":
        extra = ["--g-extra-w", "60"]
    elif name == "KWALK":
        extra = ["--g-walk-fail", "nc3x5x10-fp32-rnd"]
    elif name == "KCHECK":
        extra = ["--g-check-wrong", "nc3x5x10-fp32-rnd"]
    elif name == "KTENSOR":
        extra = ["--g-tensor-error", "nc3x5x10-fp32-rnd"]
    elif name == "KSLOW":
        extra = ["--g-slow", "nc3x5x10-fp32-rnd"]
    elif name == "TWOFAIL":
        extra = ["--host-fail-after", "8"]
    elif name == "KGATE0":
        shutil.copyfile(os.path.join(root, "build/e216rgm211/kernel/sparsity.elf"), os.path.join(root, "build/rgm/kernel/sparsity.elf"))
    elif name == "KGATE":
        def watch(out):
            deadline = time.time() + 600
            while time.time() < deadline:
                try:
                    if "run 059-null-2:" in open(os.path.join(out, "session.log")).read():
                        shutil.copyfile(os.path.join(root, "build/e216rgm211/kernel/sparsity.elf"),
                                        os.path.join(root, "build/rgm/kernel/sparsity.elf"))
                        open(os.path.join(S, name, "swapped"), "w").write(str(time.time()))
                        return
                except OSError:
                    pass
                time.sleep(0.05)
    elif name in ("ORDER", "OVER"):
        s = json.load(open(os.path.join(root, sched)))
        if name == "ORDER":
            runs = s["runs"]
            g = [r for r in runs if r["arm"] == "g07"][0]
            runs.remove(g)
            k = [i for i, r in enumerate(runs) if r["block"] == "pass2"][0]
            runs.insert(k, g)
            for i, r in enumerate(runs, 1):
                r["i"] = i
        else:
            [r for r in s["runs"] if r["arm"] == "f03"][0]["est_peak_w"] = 64.5
        sched = "src/sched/case.json"
        json.dump(s, open(os.path.join(root, sched), "w"), indent=1)
    rc, out, secs = run_dry(root, extra, sched, watch)
    q, gates, log, calls = read(out)
    ran = ran_ids(q)
    stop = q.get("stop") or ""
    G = g_ids()
    ok, why = False, ""
    if name == "FULL":
        sp = json.load(open(os.path.join(out, "stop-path.json")))
        gfam = [g for g in gates if g["family"] == "rgm136 gemmLnc"]
        hostcalls = [c for c in calls if "sparsity_host" in c]
        sc, dj = reduce_score(root, out, S, name)
        pids = [x["id"] for x in json.load(open(os.path.join(E, "points-e216.json")))["points"]]
        okscore = isinstance(sc, dict) and sc["rules"]["R0"]["verdict"] == "PASS" and len(dj["runs"]) == 69 and \
            all(pid in sc["points"] and (sc["points"][pid].get("measured_route_c") or sc["points"][pid].get("measured_route_m_REPORTED"))
                for pid in pids)
        ok = (rc == 0 and len(ran) == 69 and not stop and len(gates) == 70 and all(g["ok"] for g in gates) and len(gfam) == 10
              and all("e216rgm211" in c for c in hostcalls[-10:]) and not any("e216rgm211" in c for c in hostcalls[:-10])
              and sp["real_lines"] == {"board_cap_w": 70.0, "cap_consecutive": 3, "abs_stop_c": 70.0} and sp["ok"] and okscore)
        why = (f"rc {rc}, {len(ran)} runs ran, {len(gates)} gates OK {sum(g['ok'] for g in gates)} ({len(gfam)} G), the last 10 host calls rgm211's: "
               f"{all('e216rgm211' in c for c in hostcalls[-10:])}, real lines {sp['real_lines']}, R0 {sc['rules']['R0']['verdict'] if isinstance(sc, dict) else dj}, "
               f"{len(dj['runs']) if isinstance(dj, dict) else '?'} runs reduced, {secs:.0f} s")
    elif name == "LINE71":
        ok = rc == 0 and "board" in stop and "70 W" in stop and ran == ["4x8x8-int8-rnd", "null-1", "f03"]
        why = f"rc {rc}, stop '{stop}', ran {ran}"
    elif name == "LINE69":
        tel = [json.loads(ln) for ln in gzip.open(os.path.join(out, "telemetry.jsonl.gz"), "rt")]
        rj = json.load(open(os.path.join(out, "runs", "003-f03", "run.json")))
        w = [x["board_w"] for x in tel if rj["procs"][0]["t0_ms"] <= x["t_ms"] <= rj["procs"][0]["t1_ms"] and x.get("board_w") is not None]
        top = max(w) if w else None
        ok = rc == 0 and "operator" in stop and "board" not in stop and len(ran) == 6 and top is not None and 65.0 < top <= 70.0
        why = f"rc {rc}, stop '{stop}', {len(ran)} ran; f03's board at most {top} W (under the 70 W line: no stop)"
    elif name == "GTRIP":
        before = [x["arm"] for x in q["queue"][:59]]
        ok = (rc == 0 and "board" in stop and "70 W" in stop and len(ran) == 60 and ran[-1] == "g07" and all(x.get("ran") for x in q["queue"][:59])
              and not any(x.get("ran") for x in q["queue"][60:]))
        why = f"rc {rc}, stop '{stop}', ran {len(ran)} (last {ran[-1] if ran else None}), the first 59 all ran: {len(before)}"
    elif name in ("KWALK", "KCHECK", "KTENSOR", "KSLOW"):
        word = {"KWALK": "the walk check", "KCHECK": "its check of C wrong", "KTENSOR": "tensor error", "KSLOW": "rc 124"}[name]
        rj = json.load(open(glob.glob(os.path.join(out, "runs", "060-g07", "run.json"))[0]))
        pr = rj["procs"][0]
        sc, dj = reduce_score(root, out, S, name)
        r0 = sc["rules"]["R0"]["verdict"] if isinstance(sc, dict) else None
        want_r0 = "FAIL" if name == "KCHECK" else "PASS"
        ok = (rc == 0 and "KERNEL STOP" in stop and word in stop and len(ran) == 60 and ran[-1] == "g07"
              and not any(x.get("ran") for x in q["queue"][60:]) and pr.get("family") == "rgm136 gemmLnc" and r0 == want_r0
              and (name != "KWALK" or pr["walk"]["ok"] is False) and (name != "KSLOW" or pr["rc"] == 124))
        why = (f"rc {rc}, stop '{stop[:110]}', {len(ran)} ran (last {ran[-1] if ran else None}); g07 rc {pr.get('rc')}, walk "
               f"{(pr.get('walk') or {}).get('words', '')[:60]}; R0 {r0} (want {want_r0})")
    elif name == "KGATE":
        swapped = os.path.exists(os.path.join(S, name, "swapped"))
        g07 = [g for g in gates if g["proc"].startswith("runs/060-g07")]
        rj = json.load(open(os.path.join(out, "runs", "060-g07", "run.json")))
        pr = rj["procs"][0]
        sc, dj = reduce_score(root, out, S, name)
        r0 = sc["rules"]["R0"]["verdict"] if isinstance(sc, dict) else None
        g07sa = [f for f in (sc.get("flags", {}).get("g07") or [])] if isinstance(sc, dict) else None
        ok = (rc == 0 and swapped and "IDENTITY GATE STOP" in stop and "identity gate refused" in stop and g07 and not g07[0]["ok"]
              and "rgm211" in g07[0]["words"] and pr.get("not_started") and not os.path.exists(os.path.join(out, "runs", "060-g07", "proc-00.out"))
              and not any(x.get("ran") for x in q["queue"][60:]) and r0 == "PASS")
        why = (f"rc {rc}, swapped {swapped}, stop '{stop[:100]}', g07 gate {g07[0]['words'][:70] if g07 else None}; no process started: "
               f"{bool(pr.get('not_started'))}; R0 {r0}; g07 flags {g07sa}")
    elif name == "KGATE0":
        ok = rc == 16 and "smoke gate failed" in log and len(gates) == 1 and not gates[0]["ok"] and not ran and "IDENTITY GATE STOP" in stop
        why = f"rc {rc}, gates {len(gates)} ({gates[0]['words'][:60] if gates else None}), ran {len(ran)}, stop '{stop[:60]}'"
    elif name in ("ORDER", "OVER"):
        ro = open(os.path.join(out, "runner.out")).read()
        word = "the G block is not last" if name == "ORDER" else "over the 64.0 W line"
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
        except Exception as e:  # noqa: BLE001
            ok, why = False, f"{type(e).__name__}: {e}"
        n += 1
        p += ok
        print(f"CASE {name}: {'PASS' if ok else 'FAIL'} ({why}) [{time.time() - t:.0f} s]", flush=True)
    print(f"SELFTEST-RUN-E216 {p} of {n} {'PASS' if p == n else 'FAIL'}")
    return 0 if p == n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
