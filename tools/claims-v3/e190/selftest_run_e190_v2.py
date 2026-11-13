#!/usr/bin/env python3
"""E190's runner desk test v2 (Q169, the kit's dated note 1, lane fix-e190, Fri 13 Nov 2026, before any E190 datum): EVERY case of
selftest_run_e190.py (the kit, unchanged beside it; imported, its RUNNER pointed at run_e190_v2.py, its doubles the v2 ones through the
runner), then note 1's own cases, each its own --dry session on fake_card_e190_v2.py's doubles in a scratch directory. No device, no box.
On a box with a card run it ONLY inside a sandbox with no /dev/et* and an empty /run/lock (case R2 runs the real runner, which must stop at
its box check before anything else).

    /usr/bin/python3 -B tools/claims-v3/e190/selftest_run_e190_v2.py <scratch dir> [--only CASE ...] > selftest-run-e190-v2.txt

The v1 cases (G1-G11, S1-S5, D1-D2, H1-H2, O1, R1-R2, E1-E2) are described in selftest_run_e190.py. Note 1's cases:
  I1 arm B's config read names card 0 (its stderr /dev/et0_mgmt, ID 0, 519 mV: aifoundry1's device layer had ignored ET_DEVICES): 16,
     the gate, no sampler, no host process                            I2 card 1's block but 519 mV: 16, the gate
  I3 arm A's config read with no identity block on its stderr: 16 (the card cannot be told)
  I4 arm B's sampler holds card 0's mgmt node: the identity read (et-who and the sampler's own files) stops it before the smoke: 16, no
     host process; et-who's counts written, no login                  I5 another login on card 1, seen only once the sampler runs: 16
  I6 arm B's host names and holds card 0 in the smoke's first process: the watch trips at once (identity), the stop file touched, the host
     ends at its next launch boundary ("stopping:"), 16, no second smoke process
  I7 the same in the runs (P1 fp32): the session stops (identity), nothing further starts, the closing and the manifest
  I8 arm A's host names and holds nothing in the smoke: its card cannot be told: the smoke gate fails, 16
  I9 arm B's board does not rise over the rest in the smoke (launches with no watts): the smoke gate fails, 16
  F1 the sampler dies in S1's second process: S1 ends before its next process (flagged), the sampler is restarted, the session ends rc 0
  F2 the sampler dies inside P1 fp32's one process (the verifier's case): that process runs out (no check inside a process), then the
     next run's die gate finds no live sample, restarts the sampler and P1 fp16 runs on live samples
  F3 the sampler hangs (alive, silent) in S1: S1 ends before its next process (flagged), the stale sampler is stopped (SIGTERM) and
     restarted
Every number here comes from the doubles (the frozen forecast's points driven through a toy card): a desk check of code, not a
measurement and not a reading of E190. SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import selftest_run_e190 as V1  # noqa: E402  (the kit's desk test, unchanged: its cases and helpers)

V1.RUNNER = os.path.join(HERE, "run_e190_v2.py")
N_SMOKE = V1.N_SMOKE_LAUNCHES     # the smoke's launches on the doubles (22): an injection or a mode after them lands in the runs


def log_has(d, text):
    p = os.path.join(d, "session.log")
    return os.path.exists(p) and text in open(p).read()


def ident(d):
    p = os.path.join(d, "identity.json")
    return json.load(open(p)) if os.path.exists(p) else {}


def smoke_dirs(d):
    sd = os.path.join(d, "smoke")
    return sorted(x for x in os.listdir(sd) if os.path.isdir(os.path.join(sd, x))) if os.path.isdir(sd) else []


def identity_cases(t):
    rc, log, d, s, _ = t.session("I1", "B", {"E190_FAKE_CONFIG": "card0"})
    t.case("I1", rc == 16 and "the card's identity" in log and "/dev/et0_mgmt, not /dev/et1_mgmt" in log and "minion_mv 519" in log
           and not log_has(d, "sampler started") and not V1.has_proc(d) and os.path.exists(os.path.join(d, "config-start.err")),
           f"rc {rc}; '{[ln[24:200] for ln in log.splitlines() if 'identity' in ln][:1]}'; sampler {'started' if log_has(d, 'sampler started') else 'none'}; "
           f"host processes {'some' if V1.has_proc(d) else 'none'}")
    rc, log, d, s, _ = t.session("I2", "B", {"E190_FAKE_CONFIG": "mv519"})
    t.case("I2", rc == 16 and "minion_mv 519, not below 510" in log and not V1.has_proc(d), f"rc {rc}")
    rc, log, d, s, _ = t.session("I3", "A", {"E190_FAKE_CONFIG": "noident"})
    t.case("I3", rc == 16 and "no 'PCIe target' line" in log and not V1.has_proc(d), f"rc {rc}")
    rc, log, d, s, _ = t.session("I4", "B", {"E190_FAKE_SAMPLER": "card0"})
    who = open(os.path.join(d, "etwho-identity.txt")).read() if os.path.exists(os.path.join(d, "etwho-identity.txt")) else ""
    me = __import__("pwd").getpwuid(os.getuid()).pw_name
    t.case("I4", rc == 16 and "the identity read" in log and "no holder line of ours on /dev/et1_mgmt" in log and "holds ['/dev/et0_mgmt']" in log
           and not V1.has_proc(d) and '"ours_off_card": 1' in who and me not in who,
           f"rc {rc}; '{[ln[24:220] for ln in log.splitlines() if 'identity read' in ln][:1]}'; et-who counts written, our login in them: {me in who}")
    rc, log, d, s, _ = t.session("I5", "B", {"E190_FAKE_ETWHO": "other"})
    t.case("I5", rc == 16 and not V1.has_proc(d),
           f"rc {rc} (another login on card 1: the first holder read refuses it before the config; the identity read would too)")
    rc, log, d, s, _ = t.session("I6", "B", {"E190_FAKE_HOST": "card0"})
    marks = V1.jl(os.path.join(d, "marks.jsonl"))
    err = open(os.path.join(d, "smoke", "fp32", "proc.err")).read() if os.path.exists(os.path.join(d, "smoke", "fp32", "proc.err")) else ""
    sj = json.load(open(os.path.join(d, "smoke", "fp32", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "fp32", "smoke.json")) else {}
    t.case("I6", rc == 16 and any(m["kind"] == "identity_trip" for m in marks) and os.path.exists(os.path.join(d, "STOP")) and "stopping:" in err
           and smoke_dirs(d) == ["fp32"] and "smoke gate failed" in log and not V1.run_dirs(d) and sj.get("n_launch", 99) < 8,
           f"rc {rc}; trip {[m['detail'][:90] for m in marks if m['kind'] == 'identity_trip']}; the host stopped by the file {'stopping:' in err} "
           f"after {sj.get('n_launch')} launches (8 unstopped); smoke processes {smoke_dirs(d)}")
    # arm B's smoke has 21 launches on the doubles (fp32 7 at 600 MHz, fp16 7, int8 7): the mode from launch 21 is P1 fp32's process
    rc, log, d, s, _ = t.session("I7", "B", {"E190_FAKE_HOST": "card0", "E190_FAKE_HOST_FROM_N": str(N_SMOKE - 1)})
    q = V1.queue(d)
    after = [x for x in q.get("queue", []) if not x.get("ran")]
    t.case("I7", rc == 0 and "identity" in (q.get("stop") or "") and V1.run_dirs(d) == ["01-P1-burst-fp32"] and after
           and all("after a stop" in x.get("why", "") for x in after) and "config end" in log and V1.manifest_ok(d),
           f"rc {rc}; stop '{(q.get('stop') or '')[:120]}'; runs started {V1.run_dirs(d)}; not started after it {len(after)}")
    rc, log, d, s, _ = t.session("I8", "A", {"E190_FAKE_HOST": "noident"})
    t.case("I8", rc == 16 and "NOT SEEN" in log and "smoke gate failed" in log and not V1.run_dirs(d), f"rc {rc}")
    rc, log, d, s, _ = t.session("I9", "B", {"E190_FAKE_HOST": "norise"})
    sj = json.load(open(os.path.join(d, "smoke", "fp32", "smoke.json"))) if os.path.exists(os.path.join(d, "smoke", "fp32", "smoke.json")) else {}
    t.case("I9", rc == 16 and "smoke gate failed" in log and sj.get("board_rise", {}).get("ok") is False and not V1.run_dirs(d),
           f"rc {rc}; the board's rise {sj.get('board_rise')}")


def freshness_cases(t):
    # P1's launches on the doubles: fp32 18, fp16 17, int8 15 (the virtual clock); S1's processes 18 each
    n_s1_p2 = N_SMOKE + 18 + 17 + 15 + 18 + 5
    rc, log, d, s, _ = t.session("F1", "A", {"E190_FAKE_SAMPLER": f"dies:{n_s1_p2}"})
    rj = json.load(open(os.path.join(d, "runs", "04-S1-sus-fp32", "run.json"))) if os.path.exists(os.path.join(d, "runs", "04-S1-sus-fp32", "run.json")) else {}
    fl = "; ".join(rj.get("flags", []))
    t.case("F1", rc == 0 and "the sampler was not live before process" in fl and 1 <= len(rj.get("procs", [])) < 12
           and "restarting it" in log and V1.manifest_ok(d),
           f"rc {rc}; S1's processes {len(rj.get('procs', []))} of 12; flags '{fl[:160]}'; restarted {'restarting it' in log}")
    rc, log, d, s, _ = t.session("F2", "A", {"E190_FAKE_SAMPLER": f"dies:{N_SMOKE + 1}"})
    q = V1.queue(d)
    ran = [x["run"] for x in q.get("queue", []) if x.get("ran")]
    lines = log.splitlines()
    i_restart = next((i for i, ln in enumerate(lines) if "restarting it" in ln), None)
    i_run2 = next((i for i, ln in enumerate(lines) if "run 02-P1-burst-fp16:" in ln), None)
    t.case("F2", rc == 0 and i_restart is not None and i_run2 is not None and i_restart < i_run2 and "02-P1-burst-fp16" in ran
           and "01-P1-burst-fp32" in ran,
           f"rc {rc}; P1 fp32's process ran out (a burst is one process: no check inside it); the sampler restarted before run 02: "
           f"{i_restart is not None and i_run2 is not None and i_restart < i_run2}; runs {ran}")
    rc, log, d, s, _ = t.session("F3", "A", {"E190_FAKE_SAMPLER": f"hangs:{n_s1_p2}"})
    rj = json.load(open(os.path.join(d, "runs", "04-S1-sus-fp32", "run.json"))) if os.path.exists(os.path.join(d, "runs", "04-S1-sus-fp32", "run.json")) else {}
    fl = "; ".join(rj.get("flags", []))
    t.case("F3", rc == 0 and "the sampler was not live before process" in fl and "alive True" in fl and 1 <= len(rj.get("procs", [])) < 12
           and "restarting it" in log,
           f"rc {rc}; S1's processes {len(rj.get('procs', []))} of 12; flags '{fl[:160]}'")


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    s = os.path.abspath(argv[0])
    if s == V1.REPO or s.startswith(V1.REPO + os.sep):
        print("the scratch directory must be outside the repository")
        return 2
    if os.path.exists(s) and os.listdir(s):
        print(f"{s} is not empty")
        return 2
    os.makedirs(s, exist_ok=True)
    only = argv[argv.index("--only") + 1:] if "--only" in argv else None
    t = V1.T(s)
    devs = [x for x in os.listdir("/dev") if x.startswith("et")]
    print(f"selftest_run_e190_v2 ({V1.PY} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; the runner {os.path.basename(V1.RUNNER)}; "
          f"/dev/et*: {devs or 'none'}; /run/lock entries: {len(os.listdir('/run/lock')) if os.path.isdir('/run/lock') else 'no /run/lock'}", flush=True)
    if devs:
        print("REFUSED: a /dev/et* node is visible: run this inside the sandbox (no /dev/et*, an empty /run/lock)")
        return 3
    for name, fn in (("I", identity_cases), ("F", freshness_cases), ("G", V1.gates), ("S", V1.stops), ("D", V1.gates_between),
                     ("H", V1.hosts), ("O", V1.order), ("R", V1.refusals), ("E", V1.end_to_end)):
        if only and name not in only:
            continue
        fn(t)
    print(f"SELFTEST-RUN-E190-V2 {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
