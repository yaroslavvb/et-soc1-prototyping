#!/usr/bin/env python3
"""E180's runner: one pass of E180's configurations with the energy catalogue's timing, and E171's live stops.

    python3 tools/claims-v3/e180/run_e180.py <out-dir> --root <tree> --pass <P> [--smoke] --tel-live <sampler's file>
        [--card <id>] [--burst 3] [--gap 4.5] [--lead 10] [--stop-w 65] [--stop-c 70] [--dry] [--list]
    python3 tools/claims-v3/e180/run_e180.py <out-dir> --pass 18002 --stop-path-test --tel-live <file> --stop-w 1
    exit 0 done; 2 usage or the order differs from the plan; 3 another user or device process appeared;
         4 the sampler stopped writing; 5 a stop fired (board >= stop-w W or minshire[0] >= stop-c C on a live sample;
         for --stop-path-test, 5 means both stops fired as they must)

It is tools/claims-v3/cat/run_catalogue_t10.py's protocol (the catfull runner), with these changes, each for E180:
  1. the configurations are E180's (cfgs-e180.json, written by plan_e180.py), selected by exact name (never by prefix:
     a repeat run is "<cfg>@r2"), each with its own host binary (all E180 runs use build/enercat-e180's);
  2. the pass's order is random.Random(pass).shuffle over cfgs-e180.json's list, the runner's own shuffle, and it must
     equal plan-e180.json's order for that pass, else exit 2 before any device opens; the smoke runs plan's smoke list;
  3. E171's stops (tools/claims-v3/e171/run_e171.py, E163's values): before every configuration and every 0.1 s while a
     burst runs, the last complete line of the live telemetry file is read; board_w >= 65 or temp_c.minshire[0] >= 70
     ends the burst (SIGTERM to timeout, which passes it on) and the pass, exit 5, with a STOP line in run.log and
     stop.json. A telemetry file that has not grown for --stall-s (6 s) also ends the pass (exit 4), as catfull's runner;
  4. no heater and no prefill (aifoundry3 is pinned at 600 MHz, and no E180 configuration is a "prefill" one);
  5. every runs.jsonl line carries the kind ("kind") beside "cfg", and the plan's pass number ("pass").
Unchanged from the catfull runner: `timeout 10` on every device process with stdin from /dev/null; the burst command
(<host> <args> --seconds <burst> --window 240000000); the lead before the first configuration and the gap before each;
lib.sh's others_present before each configuration; runs.jsonl / run.log / configs.json in its format, so
workloads/enercat/analyze_catalogue.py's bursts_of reads them unchanged.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import random
import signal
import socket
import subprocess
import sys
import threading
import time

EXIT_PLAN, EXIT_OTHERS, EXIT_STALL, EXIT_STOP = 2, 3, 4, 5
WINDOW = "240000000"


def last_sample(path):
    """(board_w, minshire[0]) of the last complete line of the live telemetry file, or (None, None)."""
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 8000))
            lines = f.read().decode(errors="ignore").splitlines()
    except OSError:
        return None, None
    for line in reversed(lines):
        if line.startswith("{"):
            try:
                d = json.loads(line)
                return float(d["board_w"]), float(d["temp_c"]["minshire"][0])
            except (ValueError, KeyError, IndexError, TypeError):
                continue
    return None, None


def stop_path_test(a):
    """The stop path on live samples, with no launch: (1) the check before a run, (2) the in-run watcher, which must
    SIGTERM a harmless child (sleep 5, standing in for a burst) within a second. Exit 5 when both fired, 1 if either did not.
    """
    os.makedirs(a.out, exist_ok=True)
    rec = {"stop_w": a.stop_w, "stop_c": a.stop_c, "t_ms": int(time.time() * 1000)}
    if a.dry:
        print(f"DRY stop-path test ({a.stop_w:g} W / {a.stop_c:g} C)", file=sys.stderr, flush=True)
        json.dump({**rec, "dry": True}, open(os.path.join(a.out, "stoptest.json"), "w"))
        return EXIT_STOP
    t0 = time.time()
    fired = None
    while time.time() - t0 < 5 and not fired:
        w, c = last_sample(a.tel_live)
        if w is not None and (w >= a.stop_w or c >= a.stop_c):
            fired = {"board_w": w, "minshire0_c": c, "after_s": round(time.time() - t0, 2)}
        time.sleep(0.1)
    rec["pre_run_check"] = fired
    child = subprocess.Popen(["sleep", "5"], stdin=subprocess.DEVNULL)
    t1 = time.time()
    killed = None
    while child.poll() is None and time.time() - t1 < 3:
        w, c = last_sample(a.tel_live)
        if w is not None and (w >= a.stop_w or c >= a.stop_c):
            child.send_signal(signal.SIGTERM)
            child.wait(timeout=2)
            killed = round(time.time() - t1, 2)
            break
        time.sleep(0.1)
    if child.poll() is None:
        child.send_signal(signal.SIGTERM)
        child.wait(timeout=2)
    rec["watcher_sigterm_after_s"] = killed
    ok = fired is not None and killed is not None and killed < 1.0
    rec["result"] = "both fired" if ok else "a stop did not fire"
    json.dump(rec, open(os.path.join(a.out, "stoptest.json"), "w"), indent=1)
    print(f"stop-path test: {rec['result']} ({json.dumps(rec)})")
    return EXIT_STOP if ok else 1


def order_of(cfgs, p):
    order = list(range(len(cfgs)))
    random.Random(p).shuffle(order)
    return [cfgs[i]["cfg"] for i in order]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--pass", dest="p", type=int, required=True)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--cfgs", default="tools/claims-v3/e180/cfgs-e180.json")
    ap.add_argument("--plan", default="tools/claims-v3/e180/plan-e180.json")
    ap.add_argument("--burst", type=float, default=None)
    ap.add_argument("--gap", type=float, default=None)
    ap.add_argument("--lead", type=float, default=None)
    ap.add_argument("--tel-live", default=None)
    ap.add_argument("--stall-s", type=float, default=6.0)
    ap.add_argument("--stop-w", type=float, default=65.0)
    ap.add_argument("--stop-c", type=float, default=70.0)
    ap.add_argument("--card", default=None)
    ap.add_argument("--dry", action="store_true", default=bool(os.environ.get("V3_DRY")))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--stop-path-test", action="store_true",
                    help="no launch: the live stop must fire on the sampler's samples (run with a line below idle)")
    a = ap.parse_args()
    os.chdir(a.root)
    if a.stop_path_test:
        sys.exit(stop_path_test(a))
    sys.dont_write_bytecode = True
    doc = json.load(open(a.cfgs))
    plan = json.load(open(a.plan))
    by = {c["cfg"]: c for c in doc["cfgs"] + doc["smoke"]}
    t = plan["timing"]
    burst = a.burst if a.burst is not None else (plan["smoke"]["burst_s"] if a.smoke else t["burst_s"])
    gap = a.gap if a.gap is not None else t["gap_s"]
    lead = a.lead if a.lead is not None else (plan["smoke"]["lead_s"] if a.smoke else t["lead_s"])
    if a.smoke:
        if a.p != plan["smoke"]["pass"]:
            print(f"the smoke is pass {plan['smoke']['pass']}, not {a.p}", file=sys.stderr)
            sys.exit(EXIT_PLAN)
        names = list(plan["smoke"]["cfgs"])
    else:
        planned = plan["order"].get(str(a.p))
        if planned is None:
            print(f"pass {a.p} is not a planned pass ({', '.join(sorted(plan['order']))})", file=sys.stderr)
            sys.exit(EXIT_PLAN)
        names = order_of(doc["cfgs"], a.p)
        if names != planned:
            print(f"pass {a.p}: the shuffle's order differs from plan-e180.json's: refusing", file=sys.stderr)
            sys.exit(EXIT_PLAN)
    cfgs = [by[n] for n in names]
    est = lead + sum(gap + burst + 2.5 for _ in cfgs) + 3
    if a.list:
        print(json.dumps({"n": len(cfgs), "max_s": int(est) + 1, "cfgs": names}))
        return
    ENV = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
    os.makedirs(a.out, exist_ok=True)
    host = a.card or socket.gethostname()
    json.dump({"host": host, "hostname": socket.gethostname(), "et_devices": os.environ.get("ET_DEVICES"),
               "pass": a.p, "smoke": a.smoke, "burst_s": burst, "gap_s": gap, "lead_s": lead,
               "stop_w": a.stop_w, "stop_c": a.stop_c, "cfgs": cfgs}, open(os.path.join(a.out, "configs.json"), "w"), indent=1)
    runs = open(os.path.join(a.out, "runs.jsonl"), "a")
    log = open(os.path.join(a.out, "run.log"), "a")

    def say(msg):
        print(msg, file=log, flush=True)

    def sleep(s):
        if a.dry:
            print(f"DRY sleep {s:.1f}", file=sys.stderr, flush=True)
        elif s > 0:
            time.sleep(s)

    def others_present():
        if a.dry:
            return False
        r = subprocess.run(["bash", "-c", ". tools/claims-v3/lib.sh && others_present"], stdin=subprocess.DEVNULL,
                           capture_output=True, text=True)
        if r.returncode == 0:
            say(f"others present: {r.stdout.strip()[-300:]}")
        elif r.returncode != 1:
            say(f"others_present check failed (rc {r.returncode}): {r.stderr.strip()[-300:]}")
        return r.returncode == 0

    seen = [None, None]

    def stalled():
        if a.dry or not a.tel_live:
            return False
        try:
            size = os.path.getsize(a.tel_live)
        except OSError:
            size = -1
        now = time.time()
        if seen[0] is None or size > seen[0]:
            seen[0], seen[1] = size, now
            return False
        return now - seen[1] > a.stall_s

    def stop_reading():
        if a.dry or not a.tel_live:
            return None
        w, c = last_sample(a.tel_live)
        if w is not None and w >= a.stop_w:
            return f"board {w:.2f} W >= {a.stop_w:g} W"
        if c is not None and c >= a.stop_c:
            return f"minshire[0] {c:.1f} C >= {a.stop_c:g} C"
        return None

    def stop(why, cfg):
        say(f"STOP pass {a.p} {cfg}: {why}")
        json.dump({"pass": a.p, "cfg": cfg, "why": why, "t_ms": int(time.time() * 1000)},
                  open(os.path.join(a.out, "stop.json"), "w"))
        sys.exit(EXIT_STOP)

    say(f"{host}: E180 pass {a.p}{' (smoke)' if a.smoke else ''}: {len(cfgs)} runs, at most {est / 60:.1f} min; "
        f"stops {a.stop_w:g} W / {a.stop_c:g} C")
    sleep(lead)
    for c in cfgs:
        if others_present():
            say(f"pass {a.p} {c['cfg']}: another user or device process on the card: stopping the pass")
            sys.exit(EXIT_OTHERS)
        if stalled():
            say(f"pass {a.p} {c['cfg']}: {a.tel_live} has not grown for {a.stall_s:g} s: stopping the pass")
            sys.exit(EXIT_STALL)
        why = stop_reading()
        if why:
            stop(why, c["cfg"])
        sleep(gap)
        why = stop_reading()
        if why:
            stop(why, c["cfg"])
        cmd = ["timeout", "10", c["host_bin"]] + c["args"] + ["--seconds", f"{burst:g}", "--window", WINDOW]
        if a.dry:
            print("DRY hold10: " + " ".join(cmd[2:]), file=sys.stderr, flush=True)
            say(f"pass {a.p} {c['cfg']}: dry")
            continue
        t0 = time.time()
        pr = subprocess.Popen(cmd, env=ENV, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        tripped = []

        def watch():
            while pr.poll() is None:
                w = stop_reading()
                if w:
                    tripped.append(w)
                    try:
                        pr.send_signal(signal.SIGTERM)
                    except OSError:
                        pass
                    return
                time.sleep(0.1)

        th = threading.Thread(target=watch, daemon=True)
        th.start()
        out, err = pr.communicate()
        th.join(timeout=1)
        n = 0
        for line in out.splitlines():
            if line.startswith("ENERCAT {"):
                runs.write(json.dumps({"host": host, "pass": a.p, "cfg": c["cfg"], "kind": c["kind"],
                                       **json.loads(line[8:])}) + "\n")
                n += 1
        runs.flush()
        say(f"pass {a.p} {c['cfg']}: {n} launches in {time.time() - t0:.1f} s (rc {pr.returncode})")
        if tripped:
            stop(tripped[0], c["cfg"])
    sleep(gap + 3)
    say("done")


if __name__ == "__main__":
    main()
