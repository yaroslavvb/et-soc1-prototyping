#!/usr/bin/env python3
"""E184's runner (the kit; E184.md sections 2 and 6): one pass of either arm, item by item in plan-e184.json's order, with the live stops.

    python3 -B tools/claims-v3/e184/run_e184.py <out> --pass P --tel-live <sampler file> [--card C] [--dry] [--list]
    python3 -B tools/claims-v3/e184/run_e184.py <out> --pass 18402 --stop-path-test --tel-live <file> --stop-w 1     (or 18432)
    python3 -B tools/claims-v3/e184/run_e184.py /dev/null --pass 18410 --check-others
    exit 0 done; 2 usage, the plan refused, cal.json missing or an image off the frozen list; 3 another user or device process;
         4 the sampler stopped writing; 5 a stop fired (for --stop-path-test: both stops fired, as they must); 6 a host process failed

Arm S (passes 1840x-1841x, aifoundry3 card 0): an item is a quad, one host process of build/enercat-e184's patched host under
`timeout 10`: --pattern fadd.ps --harts 2 --shires <the mask> --window 240000000 --operands zeros --budget 9.5 --schedule <file>
--stop-file <out>/STOP, the schedule S + A B B A or B A A B (e184_common.schedule_lines), its images made by make_images_e184.py and
checked against the frozen list. The calibration pass (18413) reads its own two quads and pass 18412's A blocks from the telemetry,
fits the base line and writes cal.json (M_op, M_s) by E184.md section 2.1's rule, then makes those masks' images.
Arm B (passes 1843x-1844x, aifoundry1 card 1): bursts (one process, --seconds <burst>) and holds (back-to-back 6.4 s processes for
20 s; the idle level sleeps), the catalogue's arguments; marks.jsonl gives every item's start and end and every process's.
Both arms: before every process D1's other-user test (E180's others_d1_e180.sh, sourced unchanged after lib.sh; an idle login does
not block, another user's device process or lock does, and a check that fails counts as someone present) and the stall check; before
and every 0.1 s during every process the live stop on the sampler's newest complete line: aifoundry3 board >= 65 W or
temp_c.minshire[0] >= 70 C; card 1 board >= 66 W or any temp_c.minshire >= 72 C (E184.md section 2.3). A stop writes <out>/STOP (the
patched host reads it before every launch), SIGTERMs the process (timeout passes it on) and ends the pass, exit 5.
--dry prints every command and runs none. --desk (the Intel's desk test only: refused on a lab box) skips D1's test, whose
et-holders call exists only on the boxes, reads E184_DESK_HOST as the host binary and passes E184_DESK_KERNEL as its --kernel.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import signal
import socket
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402

EXIT_PLAN, EXIT_OTHERS, EXIT_STALL, EXIT_STOP, EXIT_HOST = 2, 3, 4, 5, 6
HOST_BIN = "build/enercat-e184/host/enercat_host"
IMAGES = "build/e184/images"
CAL = "build/e184/cal.json"
STOPS = {"aifoundry3": (65.0, 70.0, "minshire0"), "aifoundry1-c1": (66.0, 72.0, "minshire_any")}
D1_CHECK = ". tools/claims-v3/lib.sh && . tools/claims-v3/e180/others_d1_e180.sh && others_present"


def last_sample(path):
    """(board_w, minshire[0], max(minshire)) of the newest complete line of the live telemetry file, or Nones."""
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 8000))
            lines = f.read().decode(errors="ignore").splitlines()
    except OSError:
        return None, None, None
    for line in reversed(lines):
        if line.startswith("{") and line.endswith("}"):
            try:
                d = json.loads(line)
                ms = [float(x) for x in d["temp_c"]["minshire"]]
                return float(d["board_w"]), ms[0], max(ms)
            except (ValueError, KeyError, IndexError, TypeError):
                continue
    return None, None, None


def stop_why(path, card, stop_w=None, stop_c=None):
    sw, sc, kind = STOPS[card]
    sw = stop_w if stop_w is not None else sw
    sc = stop_c if stop_c is not None else sc
    w, c0, cmax = last_sample(path)
    if w is not None and w >= sw:
        return "board %.2f W >= %g W" % (w, sw)
    t = c0 if kind == "minshire0" else cmax
    if t is not None and t >= sc:
        return "%s %.1f C >= %g C" % ("minshire[0]" if kind == "minshire0" else "a minshire reading", t, sc)
    return None


def find_pass(plan, p):
    for arm in ("arm_S", "arm_B"):
        for q in plan[arm]["passes"]:
            if q["pass"] == p:
                return arm, q
    return None, None


def d1_check():
    return subprocess.run(["bash", "-c", D1_CHECK], stdin=subprocess.DEVNULL, capture_output=True, text=True)


def stop_path_test(a, card):
    os.makedirs(a.out, exist_ok=True)
    rec = {"stop_w": a.stop_w, "stop_c": a.stop_c, "card": card, "t_ms": int(time.time() * 1000)}
    if a.dry:
        json.dump(dict(rec, dry=True), open(os.path.join(a.out, "stoptest.json"), "w"))
        print("DRY stop-path test (%s W / %s C)" % (a.stop_w, a.stop_c), file=sys.stderr, flush=True)
        return EXIT_STOP
    t0, fired = time.time(), None
    while time.time() - t0 < 5 and not fired:
        why = stop_why(a.tel_live, card, a.stop_w, a.stop_c)
        if why:
            fired = {"why": why, "after_s": round(time.time() - t0, 2)}
        time.sleep(0.1)
    rec["pre_run_check"] = fired
    child = subprocess.Popen(["sleep", "5"], stdin=subprocess.DEVNULL)
    t1, killed = time.time(), None
    while child.poll() is None and time.time() - t1 < 3:
        if stop_why(a.tel_live, card, a.stop_w, a.stop_c):
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
    print("stop-path test: %s (%s)" % (rec["result"], json.dumps(rec)))
    return EXIT_STOP if ok else 1


def read_jsonl(path):
    import gzip
    out = []
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            op = gzip.open if p.endswith(".gz") else open
            with op(p, "rt") as f:
                for line in f:
                    if line.startswith("{"):
                        try:
                            out.append(json.loads(line))
                        except ValueError:
                            pass
            break
    return out


def base_of(samples, launches):
    """The A blocks' mean board reading of each quad in launches (one dict per launch), by e184_common.read_process."""
    by = {}
    for ln in launches:
        by.setdefault(ln["seq"], []).append(ln)
    out = {}
    for seq, lns in sorted(by.items()):
        r = c.read_process(samples, lns)
        if r["reason"] is None:
            out[seq] = (lns[0]["mask_m"], c.quad_contrast(r["blocks"])[1])
    return out


def calibrate(a, out_dir, plan, items, cal_launches):
    """E184.md section 2.1's rule: the least-squares line of the base reading on the shire count through the calibration's two quads
    and pass 18412's A blocks at 32 shires; M_op and M_s from it, clipped. Writes cal.json; returns it."""
    ds = plan["design"]
    pts = []
    if a.dry:
        spec = os.environ.get("E184_DRY_BASES", "16:30.40,24:33.10,32:35.60")
        pts = [(float(m), float(w)) for m, w in (x.split(":") for x in spec.split(","))]
    else:
        tel = read_jsonl(a.tel_live)
        for seq, (m, w) in base_of(tel, cal_launches).items():
            pts.append((float(m), w))
        prev = os.path.join(os.path.dirname(out_dir.rstrip("/")), "p18412")
        ptel, pruns = read_jsonl(os.path.join(prev, "telemetry.jsonl")), read_jsonl(os.path.join(prev, "runs.jsonl"))
        b32 = [w for _, (m, w) in base_of(ptel, pruns).items() if m == 32]
        if b32:
            pts.append((32.0, c.fmean(b32)))
    if len(pts) < 2:
        return None
    mx, my = c.fmean(p[0] for p in pts), c.fmean(p[1] for p in pts)
    z = math.fsum((p[0] - mx) * (p[1] - my) for p in pts) / math.fsum((p[0] - mx) ** 2 for p in pts)
    a0 = my - z * mx
    target = json.load(open(os.path.join(HERE, "inputs-e184.json")))["e178_op"]["target_board_w"]
    scan_w = ds["C"]["scan_start_w"]
    m_op = int(min(24, max(10, round((target - a0) / z))))
    m_s = int(min(30, max(16, round((scan_w - a0) / z))))
    cal = {"points": pts, "a_w": a0, "z_w_per_shire": z, "target_board_w": target, "scan_start_w": scan_w, "M_op": m_op, "M_s": m_s,
           "rule": "E184.md section 2.1", "dry": bool(a.dry), "t_ms": int(time.time() * 1000)}
    return cal


def make_images(pairs, dry):
    args = ["python3", "-B", os.path.join(HERE, "make_images_e184.py"), "--write", IMAGES] + ["%d:%d" % p for p in sorted(set(pairs))]
    r = subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--pass", dest="p", type=int, required=True)
    ap.add_argument("--tel-live", default=None)
    ap.add_argument("--card", default=None)
    ap.add_argument("--stall-s", type=float, default=6.0)
    ap.add_argument("--stop-w", type=float, default=None)
    ap.add_argument("--stop-c", type=float, default=None)
    ap.add_argument("--dry", action="store_true", default=bool(os.environ.get("V3_DRY")))
    ap.add_argument("--desk", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--stop-path-test", action="store_true")
    ap.add_argument("--check-others", action="store_true")
    a = ap.parse_args()
    os.chdir(a.root)
    plan = json.load(open(os.path.join(HERE, "plan-e184.json")))
    arm, ps = find_pass(plan, a.p)
    if arm is None:
        print("pass %d is not in plan-e184.json" % a.p, file=sys.stderr)
        sys.exit(EXIT_PLAN)
    card = a.card or ("aifoundry3" if arm == "arm_S" else "aifoundry1-c1")
    if card != plan[arm]["card"]:
        print("pass %d belongs to %s, not %s" % (a.p, plan[arm]["card"], card), file=sys.stderr)
        sys.exit(EXIT_PLAN)
    if a.desk and socket.gethostname().startswith("aifoundry"):
        print("--desk is the Intel's desk test only: refused on a lab box", file=sys.stderr)
        sys.exit(EXIT_PLAN)
    if a.check_others:
        r = d1_check()
        print("check-others rc %d: %s" % (r.returncode, (r.stdout.strip() or r.stderr.strip())[-300:]))
        sys.exit({0: EXIT_OTHERS, 1: 0}.get(r.returncode, 2))
    if a.stop_path_test:
        if ps["items"]:
            print("pass %d is not a stop-path test" % a.p, file=sys.stderr)
            sys.exit(EXIT_PLAN)
        sys.exit(stop_path_test(a, card))
    items = ps["items"]
    if not items:
        print("pass %d has no items (the stop-path test runs with --stop-path-test)" % a.p, file=sys.stderr)
        sys.exit(EXIT_PLAN)
    lead = 3.0 if a.p in (18401, 18431) else 10.0
    est = int(lead + ps["est_s"] + 15)
    if a.list:
        print(json.dumps({"n": len(items), "max_s": est, "arm": arm, "card": card, "what": ps["what"]}))
        return
    host_bin = os.environ.get("E184_DESK_HOST") if a.desk else HOST_BIN
    desk_kernel = ["--kernel", os.environ["E184_DESK_KERNEL"]] if a.desk and os.environ.get("E184_DESK_KERNEL") else []
    os.makedirs(a.out, exist_ok=True)
    stop_file = os.path.join(a.out, "STOP")
    runs = open(os.path.join(a.out, "runs.jsonl"), "a")
    marks = open(os.path.join(a.out, "marks.jsonl"), "a")
    log = open(os.path.join(a.out, "run.log"), "a")
    ENV = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
    hostname = socket.gethostname()

    def say(msg):
        print(msg, file=log, flush=True)

    def mark(**kw):
        kw["t_ms"] = int(time.time() * 1000)
        marks.write(json.dumps(kw, sort_keys=True) + "\n")
        marks.flush()

    def sleep(s):
        if a.dry:
            print("DRY sleep %.1f" % s, file=sys.stderr, flush=True)
        elif s > 0:
            time.sleep(s)

    def others_present():
        if a.dry or a.desk:
            return False
        r = d1_check()
        if r.returncode == 0:
            say("others present: %s" % r.stdout.strip()[-300:])
        elif r.returncode != 1:
            say("others_present check failed (rc %d): %s" % (r.returncode, r.stderr.strip()[-300:]))
        return r.returncode != 1

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
        return stop_why(a.tel_live, card, a.stop_w, a.stop_c)

    def stop(why, where):
        open(stop_file, "a").write(why + "\n")
        say("STOP pass %d %s: %s" % (a.p, where, why))
        json.dump({"pass": a.p, "where": where, "why": why, "t_ms": int(time.time() * 1000)}, open(os.path.join(a.out, "stop.json"), "w"))
        sys.exit(EXIT_STOP)

    def gate(where):
        if others_present():
            say("pass %d %s: another user or device process on the card: stopping the pass" % (a.p, where))
            sys.exit(EXIT_OTHERS)
        if stalled():
            say("pass %d %s: %s has not grown for %g s: stopping the pass" % (a.p, where, a.tel_live, a.stall_s))
            sys.exit(EXIT_STALL)
        why = stop_reading()
        if why:
            stop(why, where)

    def launch(cmd, meta, where):
        """One device process under timeout 10 with the in-run watcher; its ENERCAT lines go to runs.jsonl with meta."""
        if a.dry:
            print("DRY hold10: " + " ".join(cmd[2:]), file=sys.stderr, flush=True)
            return 0
        cmd = cmd + desk_kernel
        t0 = time.time()
        mark(event="proc_start", where=where, **meta)
        pr = subprocess.Popen(cmd, env=ENV, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        tripped = []

        def watch():
            while pr.poll() is None:
                w = stop_reading()
                if w:
                    tripped.append(w)
                    open(stop_file, "a").write(w + "\n")
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
                rec = dict(meta, host=hostname, **{"pass": a.p})
                rec.update(json.loads(line[8:]))
                runs.write(json.dumps(rec) + "\n")
                n += 1
        runs.flush()
        mark(event="proc_end", where=where, rc=pr.returncode, launches=n, **meta)
        say("pass %d %s: %d launches in %.1f s (rc %d)%s" % (a.p, where, n, time.time() - t0, pr.returncode,
                                                             (" stderr: " + err.strip()[-200:]) if pr.returncode else ""))
        if tripped:
            stop(tripped[0], where)
        return pr.returncode

    json.dump({"host": hostname, "card": card, "arm": arm, "pass": a.p, "what": ps["what"], "items": items, "host_bin": host_bin,
               "stops": STOPS[card], "lead_s": lead, "dry": a.dry, "desk": a.desk},
              open(os.path.join(a.out, "configs.json"), "w"), indent=1)
    say("%s: E184 pass %d (%s): %d items, at most %.1f min; stops %s" % (card, a.p, arm, len(items), est / 60.0, STOPS[card][:2]))

    if arm == "arm_S":
        cal = None
        if any(isinstance(it["mask_m"], str) for it in items):
            if not os.path.exists(CAL):
                say("pass %d needs %s (the calibration pass 18413): refusing" % (a.p, CAL))
                sys.exit(EXIT_PLAN)
            cal = json.load(open(CAL))
            if cal.get("dry") and not a.dry:
                say("%s is a dry pass's: refusing" % CAL)
                sys.exit(EXIT_PLAN)
        resolved = []
        for it in items:
            m = it["mask_m"] if isinstance(it["mask_m"], int) else cal[it["mask_m"]]
            resolved.append(dict(it, mask=m, img_a=c.image_name(m, it["ref"]), img_b=c.image_name(m, it["n"])))
        rc, msg = make_images([(r["mask"], r["ref"]) for r in resolved] + [(r["mask"], r["n"]) for r in resolved], a.dry)
        say("images: %s" % msg)
        if rc != 0:
            sys.exit(EXIT_PLAN)
        sdir = os.path.join(a.out, "sched")
        os.makedirs(sdir, exist_ok=True)
        sleep(lead)
        cal_launches = []
        for r in resolved:
            where = "item %d (%s n=%d ref=%d m=%d %s)" % (r["seq"], r["part"], r["n"], r["ref"], r["mask"], r["orient"])
            gate(where)
            sched = os.path.join(sdir, "q%04d.txt" % r["seq"])
            with open(sched, "w") as f:
                f.write("\n".join(c.schedule_lines(r["orient"], os.path.join(IMAGES, r["img_a"]), os.path.join(IMAGES, r["img_b"]))) + "\n")
            cmd = ["timeout", "10", host_bin, "--pattern", "fadd.ps", "--harts", "2", "--shires", "0x%x" % c.mask_of(r["mask"]),
                   "--window", str(c.WINDOW_CYCLES), "--operands", "zeros", "--budget", "9.5", "--schedule", sched,
                   "--stop-file", stop_file]
            meta = {"seq": r["seq"], "part": r["part"], "n": r["n"], "ref": r["ref"], "mask_m": r["mask"], "orient": r["orient"]}
            n0 = sum(1 for _ in open(os.path.join(a.out, "runs.jsonl")))
            rc = launch(cmd, meta, where)
            if rc not in (0,):
                say("pass %d %s: the host process ended rc %d: stopping the pass" % (a.p, where, rc))
                sys.exit(EXIT_HOST)
            if r["part"] == "Cal" and not a.dry:
                with open(os.path.join(a.out, "runs.jsonl")) as f:
                    cal_launches.extend(json.loads(x) for x in list(f)[n0:])
        if a.p == 18413:
            sleep(1.0)
            cal = calibrate(a, a.out, plan, items, cal_launches)
            if cal is None:
                say("calibration: fewer than two base readings: no cal.json, so parts P and C do not run")
                sys.exit(EXIT_PLAN)
            os.makedirs(os.path.dirname(CAL), exist_ok=True)
            json.dump(cal, open(os.path.join(a.out, "cal.json"), "w"), indent=1)
            json.dump(cal, open(CAL, "w"), indent=1)
            say("calibration: %s" % json.dumps(cal))
            ds = plan["design"]
            pairs = [(cal["M_op"], n) for n in ds["P"]["levels"]] + [(cal["M_s"], n) for n in ds["C"]["levels"] + [ds["C"]["ref"]]]
            rc, msg = make_images(pairs, a.dry)
            say("images for M_op %d and M_s %d: %s" % (cal["M_op"], cal["M_s"], msg))
            if rc != 0:
                sys.exit(EXIT_PLAN)
    else:
        sleep(lead)
        for it in items:
            where = "item %d (%s %s m=%s)" % (it["seq"], it["kind"], it["cfg"], it["mask_m"])
            gate(where)
            sleep(it["gap_s"])
            gate(where)
            meta = {"seq": it["seq"], "kind": it["kind"], "cfg": it["cfg"], "mask_m": it["mask_m"]}
            mark(event="item_start", **meta)
            if it["kind"] == "burst":
                cmd = ["timeout", "10", host_bin] + it["args"] + ["--seconds", "%g" % it["burst_s"], "--window", str(c.WINDOW_CYCLES)]
                rc = launch(cmd, meta, where)
                if rc != 0:
                    sys.exit(EXIT_HOST)
            elif it["cfg"] == "idle":
                sleep(it["hold_s"])
            else:
                t_end = time.time() + it["hold_s"]
                k = 0
                while k < int(math.ceil(it["hold_s"] / it["proc_s"] - 1e-9)):
                    secs = it["proc_s"] if a.dry else max(0.5, min(it["proc_s"], t_end - time.time()))
                    cmd = ["timeout", "10", host_bin] + it["args"] + ["--seconds", "%g" % round(secs, 2), "--window", str(c.WINDOW_CYCLES)]
                    rc = launch(cmd, dict(meta, proc=k), where + " proc %d" % k)
                    if rc != 0:
                        sys.exit(EXIT_HOST)
                    k += 1
                    if not a.dry:
                        why = stop_reading()
                        if why:
                            stop(why, where)
            mark(event="item_end", **meta)
    sleep(3)
    say("done")


if __name__ == "__main__":
    main()
