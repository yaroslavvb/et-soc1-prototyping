#!/usr/bin/env python3
"""E188 (Q165, the kit): the train runner's own stop check, LIVE (not V3_DRY), at the desk: E188's test (tools/claims-v3/e188/
selftest_stops_e188t.py, itself E182's) ported to E188's runner and its first train, B05 (block 18810, fp32). No card, no device, no box: run_e188t.py runs as the box would run it, non-dry, but its --sparsity is a stand-in that prints launch records and
opens nothing, its live telemetry file is written by a stand-in sampler thread here (10 Hz is the box's; 5 Hz here), and `ps` is a
stand-in first on PATH (run_e78.others_on_card reads `ps` when no ET_DEVICES is set, as on aifoundry3). The kit's stop-path test (block
18802) drives run_e188.py's die, board and watch paths only; this drives run_e188t.py's check() before every process, and its watcher:

  K1  the newest line reads board_w 66 W (>= 65): exit 6 (EXIT_HOT) before the first process; the STOP file names the board-power stop;
      the stand-in host never ran
  K2  minshire[0] 71 C (>= 70): exit 6, the die stop named; never ran
  K3  the newest line 10 s old (a cool reading): exit 5 (EXIT_STALL), "the sampler is gone"; never ran
  K4  no telemetry line at all: exit 5, "no telemetry line"; never ran
  K5  another user's device process (the stand-in ps prints another uid's sparsity_host): exit 3 (EXIT_OTHERS); never ran
  K6  the block's STOP file already there: exit 2 (EXIT_STOP); never ran
  K7  cool before the first process, then the stand-in sampler turns hot while process 0 runs: the watcher writes STOP, and the check
      before process 1 ends the train with exit 6; the host ran exactly once
  K8  cool throughout, two processes: exit 0, the host ran twice, 28 launch records and 2 marks
Each case's run is bounded (timeout 60 s). Written only under <work dir>.

    /usr/bin/python3 -B tools/claims-v3/e188/selftest_stops_e188t.py <work dir>
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import shutil
import subprocess
import sys
import threading
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FAILS, N = [], [0]

HOST = r'''#!/bin/sh
# the desk test's stand-in train host: it opens nothing; it counts its runs and prints 14 launch records
echo run >> "$STANDIN_MARK"
[ -n "$STANDIN_FLAG" ] && : > "$STANDIN_FLAG"
n=-1
while [ $n -le 12 ]; do echo "SPARSITY {\"launch\": $n, \"ok\": true, \"tensor_errors\": 0}"; n=$((n + 1)); done
sleep 0.6
exit 0
'''
PS_CLEAR = "#!/bin/sh\nexit 0\n"
PS_OTHER = "#!/bin/sh\necho \"  4242 31337 sparsity_host\"\n"


def say(ok, what):
    N[0] += 1
    print(("PASS " if ok else "FAIL ") + what, flush=True)
    if not ok:
        FAILS.append(what)


def sampler(path, stop, hot_board, hot_die, flag, age_s=0.0):
    """a stand-in live sampler: a fresh line every 0.2 s; hot once `flag` exists (K7) or from the start (K1, K2)"""
    while not stop.is_set():
        turned = bool(flag) and os.path.exists(flag)
        w = 66.0 if (hot_board or turned) else 30.0
        c = 71.0 if hot_die else 55.0
        line = {"t_ms": int((time.time() - age_s) * 1000), "board_w": w, "temp_c": {"minshire": [c, c, 60.0]}}
        with open(path, "a") as f:
            f.write(json.dumps(line) + "\n")
        time.sleep(0.2)


def case(work, name, hot_board=False, hot_die=False, age_s=0.0, no_tel=False, others=False, stop_first=False, turn_hot=False,
         processes=2):
    d = os.path.join(work, name)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, "bin"))
    out = os.path.join(d, "out")
    os.makedirs(out)
    host = os.path.join(d, "bin", "standin_host.sh")
    open(host, "w").write(HOST)
    os.chmod(host, 0o755)
    ps = os.path.join(d, "bin", "ps")
    open(ps, "w").write(PS_OTHER if others else PS_CLEAR)
    os.chmod(ps, 0o755)
    tel = os.path.join(d, "telemetry.jsonl.raw")
    open(tel, "w").close()
    mark = os.path.join(d, "host-runs.txt")
    flag = os.path.join(d, "turn-hot") if turn_hot else ""
    if stop_first:
        open(os.path.join(out, "STOP"), "w").write("a stop left by an earlier item (desk test)\n")
    stop = threading.Event()
    th = None
    if not no_tel:
        th = threading.Thread(target=sampler, args=(tel, stop, hot_board, hot_die, flag, age_s), daemon=True)
        th.start()
        time.sleep(0.5)
    env = {k: v for k, v in os.environ.items() if k not in ("V3_DRY", "ET_DEVICES", "V3_DEVICE")}
    env.update(PATH=os.path.join(d, "bin") + os.pathsep + env.get("PATH", ""), STANDIN_MARK=mark, STANDIN_FLAG=flag)
    cmd = ["/usr/bin/python3", "-B", os.path.join(HERE, "run_e188t.py"), out, "--root", TOP, "--tel-live", tel, "--block", "18810",
           "--sparsity", host, "--processes", str(processes)]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60)
        rc, so, se = r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        rc, so, se = "timeout", "", ""
    stop.set()
    if th:
        th.join(2)
    runs = len(open(mark).read().split()) if os.path.exists(mark) else 0
    stopf = open(os.path.join(out, "STOP")).read() if os.path.exists(os.path.join(out, "STOP")) else ""
    recs = sum(1 for _ in open(os.path.join(out, "train.jsonl"))) if os.path.exists(os.path.join(out, "train.jsonl")) else 0
    marks = sum(1 for _ in open(os.path.join(out, "marks.jsonl"))) if os.path.exists(os.path.join(out, "marks.jsonl")) else 0
    last = [x for x in (so + se).splitlines() if "STOP (" in x][-1:] or [""]
    return {"rc": rc, "host_runs": runs, "stop_file": stopf, "records": recs, "marks": marks, "stop_line": last[0].replace(d, "<case dir>"),
            "s": round(time.time() - t0, 1)}


def show(name, r):
    msg = r["stop_line"].split("] ", 1)[-1][:150]
    print(f"   {name}: rc {r['rc']}, host runs {r['host_runs']}, records {r['records']}, marks {r['marks']}, {r['s']} s; {msg}", flush=True)


def main():
    work = os.path.abspath(sys.argv[1])
    os.makedirs(work, exist_ok=True)
    r = case(work, "k1", hot_board=True); show("K1", r)
    say(r["rc"] == 6 and r["host_runs"] == 0 and "board-power stop: board_w 66.0 W >= 65.0 W" in r["stop_file"],
        "K1 board 66 W before the first process: exit 6, the board-power stop in STOP, the host never ran")
    r = case(work, "k2", hot_die=True); show("K2", r)
    say(r["rc"] == 6 and r["host_runs"] == 0 and "die stop: minion-shire reading minshire[0] 71.0 C >= 70.0 C" in r["stop_file"],
        "K2 minshire[0] 71 C: exit 6, the die stop in STOP, the host never ran")
    r = case(work, "k3", age_s=10.0); show("K3", r)
    say(r["rc"] == 5 and r["host_runs"] == 0 and "the sampler is gone" in r["stop_file"],
        "K3 the newest line 10 s old: exit 5 (EXIT_STALL), the host never ran")
    r = case(work, "k4", no_tel=True); show("K4", r)
    say(r["rc"] == 5 and r["host_runs"] == 0 and "no telemetry line" in r["stop_file"], "K4 no telemetry line: exit 5, the host never ran")
    r = case(work, "k5", others=True); show("K5", r)
    say(r["rc"] == 3 and r["host_runs"] == 0 and "another user on this card: ['4242:31337:sparsity_host']" in r["stop_file"],
        "K5 another uid's sparsity_host (stand-in ps): exit 3 (EXIT_OTHERS), the host never ran")
    r = case(work, "k6", stop_first=True); show("K6", r)
    say(r["rc"] == 2 and r["host_runs"] == 0, "K6 the block's STOP file already there: exit 2 (EXIT_STOP), the host never ran")
    r = case(work, "k7", turn_hot=True); show("K7", r)
    say(r["rc"] == 6 and r["host_runs"] == 1 and "E188 train watcher board-power stop" in r["stop_file"] and r["records"] == 14,
        "K7 hot while process 0 runs: the watcher writes STOP, the check before process 1 ends the train (exit 6); the host ran once")
    r = case(work, "k8"); show("K8", r)
    say(r["rc"] == 0 and r["host_runs"] == 2 and r["records"] == 28 and r["marks"] == 2 and not r["stop_file"],
        "K8 cool throughout, two processes: exit 0, the host ran twice, 28 launch records and 2 marks, no STOP")
    print(f"\nSELFTEST-STOPS-E188T {N[0] - len(FAILS)} of {N[0]} {'PASS' if not FAILS else 'FAIL'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
