#!/usr/bin/env python3
"""E183's runner (Q155, the kit; E183.md sections 3 and 7): one block on aifoundry3 card 0 - a train block (its opening anchors, the
train's processes back to back, its closing anchors), the smoke, or the stop-path test - with E171's live stops, D1's other-user rule
before every burst and every train process, and the in-run watcher. It ports E180's runner v2 (run_e180_v2.py, the bursts: the catalogue's
timing, the stops, the D1 check, the stall rule, its runs.jsonl form, which analyze_catalogue.bursts_of reads unchanged) and E182's train
runner (run_e182t.py: processes back to back, a mark per process, three processes in a row with no record end it).

    python3 -B tools/claims-v3/e183/run_e183.py <out> --root <tree> --block <18310-18315> --tel-live <file> [--processes N] [--dry] [--list]
    python3 -B tools/claims-v3/e183/run_e183.py <out> --root <tree> --smoke --tel-live <file> [--dry] [--list]
    python3 -B tools/claims-v3/e183/run_e183.py <out> --root <tree> --stop-path-test --tel-live <file> --stop-w 1     (E180's)
    python3 -B tools/claims-v3/e183/run_e183.py /dev/null --root <tree> --check-others          (D1's check once: exit 3 / 0 / 2)
EXIT 0 done; 2 usage or a refusal before any device opens; 3 another user or device process; 4 the sampler stopped writing; 5 a stop
fired (board >= 65 W or minshire[0] >= 70 C on a live sample; for --stop-path-test, 5 means both stops fired as they must); 7 three
train processes in a row with no launch record.

A TRAIN BLOCK: a 10 s lead; the opening anchors (fadd.ps zeros, then random: E180's 3 s bursts, each after a 4.5 s gap); a 6 s gap; the
train's processes back to back, process k in the plan's orientation k, each `timeout 10 <host> --pattern fadd.ps --operands file:<F>
--operands-b file:<S> --abba <ori> --launches 13 --harts 2 --seconds 30 --window 240000000` (the stops read before every process, the
watcher every 0.1 s while it runs); the closing anchors (random, then zeros), each after a 4.5 s gap; a 7.5 s tail. THE SMOKE: a 3 s lead,
fadd.ps zeros, random, 5s and 4s as 1 s bursts (each after a 4.5 s gap), a 6 s gap, two train processes of T5 (SFFS, FSSF), a 7.5 s
tail. Writes <out>/runs.jsonl (the bursts' ENERCAT records, E180's form, with "cfg" and "kind"), <out>/train.jsonl (one line per train
launch: the block, train, process, orientation, first, second and the ENERCAT record), <out>/marks.jsonl (a mark per burst and process),
<out>/configs.json, <out>/run.log. Nothing here opens the management node; the host opens the card through the runtime only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e183_common as E  # noqa: E402

EXIT_PLAN, EXIT_OTHERS, EXIT_STALL, EXIT_STOP, EXIT_NORECORDS = 2, 3, 4, 5, 7
D1_CHECK = ". tools/claims-v3/lib.sh && . tools/claims-v3/e180/others_d1_e180.sh && others_present"   # E180 v2's D1 rule, one definition


def last_sample(path):
    """(board_w, minshire[0], t_ms) of the last complete line of the live telemetry file, or (None, None, None) (E180's reader)"""
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 8000))
            lines = f.read().decode(errors="ignore").splitlines()
    except OSError:
        return None, None, None
    for line in reversed(lines):
        if line.startswith("{"):
            try:
                d = json.loads(line)
                return float(d["board_w"]), float(d["temp_c"]["minshire"][0]), d.get("t_ms")
            except (ValueError, KeyError, IndexError, TypeError):
                continue
    return None, None, None


def d1_check():
    return subprocess.run(["bash", "-c", D1_CHECK], stdin=subprocess.DEVNULL, capture_output=True, text=True)


def stop_path_test(a):
    """E180's: the stop path on live samples, with no launch: the check before a run, then the in-run watcher on a harmless child"""
    os.makedirs(a.out, exist_ok=True)
    rec = {"stop_w": a.stop_w, "stop_c": a.stop_c, "t_ms": int(time.time() * 1000)}
    if a.dry:
        print(f"DRY stop-path test ({a.stop_w:g} W / {a.stop_c:g} C)", file=sys.stderr, flush=True)
        json.dump({**rec, "dry": True}, open(os.path.join(a.out, "stoptest.json"), "w"))
        return EXIT_STOP
    t0 = time.time()
    fired = None
    while time.time() - t0 < 5 and not fired:
        w, c, _ = last_sample(a.tel_live)
        if w is not None and (w >= a.stop_w or c >= a.stop_c):
            fired = {"board_w": w, "minshire0_c": c, "after_s": round(time.time() - t0, 2)}
        time.sleep(0.1)
    rec["pre_run_check"] = fired
    child = subprocess.Popen(["sleep", "5"], stdin=subprocess.DEVNULL)
    t1 = time.time()
    killed = None
    while child.poll() is None and time.time() - t1 < 3:
        w, c, _ = last_sample(a.tel_live)
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


def build_items(a):
    """the block's items in order: ("burst", kind, cfg, burst_s, gap_s) and ("train", t, k, orientation), with the lead and tail"""
    items = []
    if a.smoke:
        lead = E.SMOKE_LEAD_S
        sm = E.plan()["smoke"]
        for k in sm["bursts"]:
            items.append(("burst", k, E.smoke_cfg(k), E.SMOKE_BURST_S, E.GAP_S))
        t = E.trains()[sm["train"]]
        items.append(("gap", E.POST_ANCHOR_GAP_S))
        for k, ori in enumerate(sm["train_orientations"][:sm["train_processes"]]):
            items.append(("train", t, k, ori))
        return lead, items, {"train": t["train"], "block": E.SMOKE_PASS, "smoke": True}
    t = E.train_of_block(a.block)
    lead = E.LEAD_S
    for k in t["anchors_open"]:
        items.append(("burst", k, E.anchor_cfg(k, a.block, "open"), E.BURST_S, E.GAP_S))
    items.append(("gap", E.POST_ANCHOR_GAP_S))
    n = t["processes"] if a.processes is None else min(a.processes, t["processes"])
    for k in range(n):
        items.append(("train", t, k, t["orientations"][k]))
    for k in t["anchors_close"]:
        items.append(("burst", k, E.anchor_cfg(k, a.block, "close"), E.BURST_S, E.GAP_S))
    return lead, items, {"train": t["train"], "block": a.block, "smoke": False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--block", type=int)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--processes", type=int, default=None)
    ap.add_argument("--tel-live", default=None)
    ap.add_argument("--stall-s", type=float, default=6.0)
    ap.add_argument("--stop-w", type=float, default=65.0)
    ap.add_argument("--stop-c", type=float, default=70.0)
    ap.add_argument("--card", default=None)
    ap.add_argument("--dry", action="store_true", default=bool(os.environ.get("V3_DRY")))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--stop-path-test", action="store_true")
    ap.add_argument("--check-others", action="store_true")
    a = ap.parse_args()
    os.chdir(a.root)
    if a.check_others:
        r = d1_check()
        print(f"check-others rc {r.returncode}: {(r.stdout.strip() or r.stderr.strip())[-300:]}")
        sys.exit({0: EXIT_OTHERS, 1: 0}.get(r.returncode, 2))
    if a.stop_path_test:
        sys.exit(stop_path_test(a))
    if not a.smoke and a.block is None:
        print("--block <18310-18315>, --smoke or --stop-path-test", file=sys.stderr)
        sys.exit(EXIT_PLAN)
    try:
        lead, items, head = build_items(a)
    except KeyError as e:
        print(str(e), file=sys.stderr)
        sys.exit(EXIT_PLAN)
    if not a.dry:
        probs = E.check_frozen(a.root)
        if probs:
            print("refusing: the registration's files differ from its list: " + "; ".join(probs[:6]), file=sys.stderr)
            sys.exit(EXIT_PLAN)
    proc_s = E.plan()["timing"]["process_s"]
    est = lead + sum(i[4] + i[3] + 0.7 if i[0] == "burst" else (i[1] if i[0] == "gap" else proc_s) for i in items) + E.GAP_S + 3
    if a.list:
        print(json.dumps({"n_bursts": sum(1 for i in items if i[0] == "burst"), "n_processes": sum(1 for i in items if i[0] == "train"),
                          "max_s": int(est) + 1, **head}))
        return
    ENV = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
    os.makedirs(a.out, exist_ok=True)
    host = a.card or socket.gethostname()
    host_bin = E.HOST_BIN
    json.dump({"host": host, "hostname": socket.gethostname(), "pass": head["block"], "smoke": head["smoke"], "train": head["train"],
               "lead_s": lead, "gap_s": E.GAP_S, "stop_w": a.stop_w, "stop_c": a.stop_c, "host_bin": host_bin,
               "cfgs": [{"cfg": i[2], "kind": i[1], "args": E.burst_args(i[1]), "burst_s": i[3]} for i in items if i[0] == "burst"],
               "processes": [{"process": i[2], "orientation": i[3]} for i in items if i[0] == "train"]},
              open(os.path.join(a.out, "configs.json"), "w"), indent=1)
    runs = open(os.path.join(a.out, "runs.jsonl"), "a")
    trainf = open(os.path.join(a.out, "train.jsonl"), "a")
    marks = open(os.path.join(a.out, "marks.jsonl"), "a")
    log = open(os.path.join(a.out, "run.log"), "a")

    def say(msg):
        print(f"{time.strftime('%H:%M:%S')} {msg}", file=log, flush=True)

    def sleep(s):
        if a.dry:
            print(f"DRY sleep {s:.1f}", file=sys.stderr, flush=True)
        elif s > 0:
            time.sleep(s)

    def others_present():
        if a.dry:
            return False
        r = d1_check()
        if r.returncode == 0:
            say(f"others present: {r.stdout.strip()[-300:]}")
        elif r.returncode != 1:
            say(f"others_present check failed (rc {r.returncode}): {r.stderr.strip()[-300:]}")
        return r.returncode != 1           # a check that fails counts as someone present (it fails closed, as D1 does)

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
        w, c, _ = last_sample(a.tel_live)
        if w is not None and w >= a.stop_w:
            return f"board {w:.2f} W >= {a.stop_w:g} W"
        if c is not None and c >= a.stop_c:
            return f"minshire[0] {c:.1f} C >= {a.stop_c:g} C"
        return None

    def stop(why, where):
        say(f"STOP {where}: {why}")
        json.dump({"pass": head["block"], "where": where, "why": why, "t_ms": int(time.time() * 1000)},
                  open(os.path.join(a.out, "stop.json"), "w"))
        sys.exit(EXIT_STOP)

    def checks(where):
        if others_present():
            say(f"{where}: another user or device process on the card: stopping the block")
            sys.exit(EXIT_OTHERS)
        if stalled():
            say(f"{where}: {a.tel_live} has not grown for {a.stall_s:g} s: stopping the block")
            sys.exit(EXIT_STALL)
        why = stop_reading()
        if why:
            stop(why, where)

    def launch(cmd, where):
        """one device process under timeout 10, the watcher beside it; returns (rc, stdout, wall_s, tripped)"""
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
        return pr.returncode, out, err, time.time() - t0, tripped

    say(f"{host}: E183 {'smoke' if head['smoke'] else 'block ' + str(head['block'])} ({head['train']}): "
        f"{sum(1 for i in items if i[0] == 'burst')} bursts and {sum(1 for i in items if i[0] == 'train')} train processes, at most "
        f"{est / 60:.1f} min; stops {a.stop_w:g} W / {a.stop_c:g} C (D1's other-user rule)")
    sleep(lead)
    norec = 0
    for it in items:
        if it[0] == "gap":
            sleep(it[1])
            continue
        if it[0] == "burst":
            _, kind, cfg, burst_s, gap_s = it
            checks(cfg)
            sleep(gap_s)
            why = stop_reading()
            if why:
                stop(why, cfg)
            cmd = ["timeout", "10", host_bin] + E.burst_args(kind) + ["--seconds", f"{burst_s:g}", "--window", E.WINDOW]
            if a.dry:
                print("DRY hold10: " + " ".join(cmd[2:]), file=sys.stderr, flush=True)
                say(f"{cfg}: dry")
                continue
            rc, out, err, wall, tripped = launch(cmd, cfg)
            n = 0
            for line in out.splitlines():
                if line.startswith("ENERCAT {"):
                    runs.write(json.dumps({"host": host, "pass": head["block"], "cfg": cfg, "kind": kind, **json.loads(line[8:])}) + "\n")
                    n += 1
            runs.flush()
            marks.write(json.dumps({"kind": "burst", "cfg": cfg, "item": kind, "t_start_ms": int((time.time() - wall) * 1000),
                                    "t_end_ms": int(time.time() * 1000), "rc": rc, "launches": n}) + "\n")
            marks.flush()
            say(f"{cfg}: {n} launches in {wall:.1f} s (rc {rc})")
            if tripped:
                stop(tripped[0], cfg)
            continue
        _, t, k, ori = it
        where = f"train {head['train']} process {k} ({ori})"
        checks(where)
        cmd = ["timeout", "10", host_bin] + E.train_args(t, ori)
        if a.dry:
            print("DRY hold10: " + " ".join(cmd[2:]), file=sys.stderr, flush=True)
            say(f"{where}: dry")
            continue
        rc, out, err, wall, tripped = launch(cmd, where)
        got = 0
        for line in out.splitlines():
            if line.startswith("ENERCAT {"):
                rec = json.loads(line[8:])
                trainf.write(json.dumps({"host": host, "block": head["block"], "train": t["train"], "process": k, "orientation": ori,
                                         "first": t["first"], "second": t["second"], **rec}) + "\n")
                got += 1
        trainf.flush()
        marks.write(json.dumps({"kind": "train", "item": t["train"], "block": head["block"], "process": k, "orientation": ori,
                                "t_start_ms": int((time.time() - wall) * 1000), "t_end_ms": int(time.time() * 1000), "rc": rc,
                                "launches": got}) + "\n")
        marks.flush()
        if got == 0:
            norec += 1
            say(f"{where}: no launch record (rc {rc}) {err[-200:]!r}")
            if norec >= 3:
                say("STOP: three train processes in a row gave no launch record")
                sys.exit(EXIT_NORECORDS)
        else:
            norec = 0
        if k % 8 == 0 or got != E.LAUNCHES or rc != 0:
            say(f"{where}: {got} launch records, rc {rc}, {wall:.2f} s")
        if tripped:
            stop(tripped[0], where)
    sleep(E.GAP_S + 3)
    say("done")


if __name__ == "__main__":
    main()
