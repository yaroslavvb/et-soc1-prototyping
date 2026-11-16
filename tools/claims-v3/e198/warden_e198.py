#!/usr/bin/env python3
"""E198's kit (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum): THE WARDEN, run by session_e198.sh OUTSIDE the private /dev for
the whole sitting. Two jobs, both reads:

  1. THE HOLDER CHECK FOR THE INSIDE (E198.md 3): holdercheck_e198.sh, the runner's --holder-check inside the private /dev, leaves an empty
     request file in DIR/req/; the warden runs the box's own `et-who --check` (outside: its sudo works here, and it lists every holder of
     both cards) under `timeout 25`, and writes its stdout, its stderr and, last, its exit status into DIR/rsp/ (each by a rename), so the
     runner's others_holding() reads the box's own answer, unchanged. Every answer is logged in DIR/served.jsonl (time, status, holder lines).
  2. THE WATCH (E191's kit's host watch, a stop made stricter for safety, named so): every 0.5 s, every process of our own login whose
     environment carries this sitting's E198_SESSION_T0 (the session, the runner, its sampler, its holder checks, every host and its
     wrapper) is read from outside: the card nodes it holds open or mapped (e191_ident.proc_nodes, E191's code imported unchanged: its
     /proc/<pid>/fd links and maps; read from outside the sandbox they name /dev/et1_ops and /dev/et1_mgmt). A card node of any card but 1
     is a WATCH HIT: DIR/WATCH-STOP gets the line, and each --stop file is touched (the runner's own stop files: it starts no further run).
     Inside the private /dev no card-0 node exists, so a hit should never come: the watch is the record that none did.

    python3 -I -B warden_e198.py DIR --t0 T0 --session-pid PID [--stop FILE ...] [--etwho et-who]
It writes DIR/ready when it serves, and ends when DIR/stop appears or the session's process is gone, writing DIR/summary.json (requests
served, their statuses, the processes that held a card node and which, the hits). Standard library and E191's e191_ident.py only.
SPDX-License-Identifier: Apache-2.0
"""
import importlib.util
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
IDENT_PATH = os.path.normpath(os.path.join(HERE, "..", "e191", "e191_ident.py"))


def load_ident():
    spec = importlib.util.spec_from_file_location("e191_ident_for_e198", IDENT_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def write_atomic(path, data):
    tmp = os.path.join(os.path.dirname(path), "." + os.path.basename(path) + ".tmp")
    with open(tmp, "w") as f:
        f.write(data)
    os.replace(tmp, path)


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def ours_of_sitting(me, tag):
    """The process IDs of our login whose environment carries tag (b'E198_SESSION_T0=<T0>')."""
    out = []
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            if os.stat("/proc/" + d).st_uid != me:
                continue
            with open("/proc/%s/environ" % d, "rb") as f:
                env = f.read().split(b"\0")
        except OSError:
            continue
        if tag in env:
            out.append(int(d))
    return out


def comm_of(pid):
    try:
        with open("/proc/%d/comm" % pid) as f:
            return f.read().strip()
    except OSError:
        return "?"


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__, file=sys.stderr)
        return 2
    d = argv[0]
    a = argv[1:]
    t0 = a[a.index("--t0") + 1] if "--t0" in a else ""
    spid = int(a[a.index("--session-pid") + 1]) if "--session-pid" in a else 0
    etwho = a[a.index("--etwho") + 1] if "--etwho" in a else "et-who"
    stops = [a[i + 1] for i, x in enumerate(a) if x == "--stop" and i + 1 < len(a)]
    if not t0.isdigit() or spid <= 0:
        print("warden_e198: --t0 <epoch> and --session-pid <pid> are required", file=sys.stderr)
        return 2
    ident = load_ident()
    me = os.getuid()
    tag = ("E198_SESSION_T0=%s" % t0).encode()
    os.makedirs(os.path.join(d, "req"), exist_ok=True)
    os.makedirs(os.path.join(d, "rsp"), exist_ok=True)
    served = open(os.path.join(d, "served.jsonl"), "a")
    watchlog = open(os.path.join(d, "watch.jsonl"), "a")
    held = {}                     # pid -> {"comm", "nodes", "first", "last"}
    hits = []
    rcs = {}
    n_served = 0
    write_atomic(os.path.join(d, "ready"), json.dumps({"pid": os.getpid(), "t": time.time(), "etwho": etwho}) + "\n")
    next_watch = 0.0
    while True:
        if os.path.exists(os.path.join(d, "stop")) or not alive(spid):
            break
        for rid in sorted(os.listdir(os.path.join(d, "req"))):
            if rid.startswith("."):
                continue
            t = time.time()
            try:
                p = subprocess.run([etwho, "--check"], capture_output=True, text=True, timeout=25, stdin=subprocess.DEVNULL)
                out, err, rc = p.stdout, p.stderr, p.returncode
            except (OSError, subprocess.TimeoutExpired) as e:
                out, err, rc = "", "warden_e198: et-who --check failed: %s\n" % e, 2
            write_atomic(os.path.join(d, "rsp", rid + ".out"), out)
            write_atomic(os.path.join(d, "rsp", rid + ".err"), err)
            write_atomic(os.path.join(d, "rsp", rid + ".rc"), "%d\n" % rc)
            try:
                os.remove(os.path.join(d, "req", rid))
            except OSError:
                pass
            nh = sum(1 for ln in out.splitlines() if ln.startswith("/dev/et") or ln.startswith("lock:"))
            served.write(json.dumps({"t": round(t, 3), "id": rid, "rc": rc, "holder_lines": nh,
                                     "seconds": round(time.time() - t, 3)}) + "\n")
            served.flush()
            n_served += 1
            rcs[str(rc)] = rcs.get(str(rc), 0) + 1
        now = time.time()
        if now >= next_watch:
            next_watch = now + 0.5
            for pid in ours_of_sitting(me, tag):
                nodes = ident.proc_nodes(pid)
                if not nodes:
                    continue
                names = sorted("/dev/et%s_%s" % n for n in nodes)
                h = held.setdefault(pid, {"comm": comm_of(pid), "nodes": [], "first": round(now, 3)})
                h["nodes"] = sorted(set(h["nodes"]) | set(names))
                h["last"] = round(now, 3)
                off = [x for x in names if not x.startswith("/dev/et1_")]
                if off:
                    line = "WATCH-HIT: process %d (%s) of this sitting holds %s, not card 1's node(s) only" % (pid, h["comm"], off)
                    if line not in hits:
                        hits.append(line)
                        with open(os.path.join(d, "WATCH-STOP"), "a") as f:
                            f.write(time.strftime("%Y-%m-%d %H:%M:%S %Z ") + line + "\n")
                        for s in stops:
                            try:
                                os.makedirs(os.path.dirname(s), exist_ok=True)
                                open(s, "a").close()
                            except OSError:
                                pass
                        watchlog.write(json.dumps({"t": round(now, 3), "hit": line}) + "\n")
                        watchlog.flush()
        time.sleep(0.1)
    ops = [h for h in held.values() if any(x.endswith("_ops") for x in h["nodes"])]
    mgmt = [h for h in held.values() if any(x.endswith("_mgmt") for x in h["nodes"])]
    summary = {"requests_served": n_served, "statuses": rcs, "processes_holding_a_card_node": len(held),
               "held_ops": len(ops), "held_mgmt": len(mgmt),
               "nodes_seen": sorted({x for h in held.values() for x in h["nodes"]}),
               "comms": sorted({h["comm"] for h in held.values()}), "watch_hits": hits,
               "ended": "stop file" if os.path.exists(os.path.join(d, "stop")) else "the session's process ended"}
    write_atomic(os.path.join(d, "summary.json"), json.dumps(summary, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
