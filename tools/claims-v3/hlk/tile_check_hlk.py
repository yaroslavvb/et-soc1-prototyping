#!/usr/bin/env python3
"""E85: before the session, one short launch of every operand set the protocol runs, in that set's own
--type, with --dump-tiles, on the session's own mask and minions (E63's tile_check.sh, for typed sets).

    python3 tile_check_hlk.py --protocol protocol-e85.json --out <dir>

The dump must equal the operand file byte for byte (sparsity_host's `file:` path reads A then B, 1,024
bytes each, in the chosen type's layout), and the file must be the one predictions.json pinned (its
sha256 is printed beside it).  Each launch is `--seconds 0` (the heater's calibration launch only), under
the card lock taken WITHOUT waiting (held by someone else: exit 3), `timeout 10`, stdin from /dev/null,
LD_LIBRARY_PATH=/opt/et/lib, its own session (never signalled).  et-who is recorded first and a held
card ends the check.  Writes <dir>/tile_check.json; exits 1 on any mismatch or failed launch.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LOCK = "/run/lock/etsoc-shire0.lock"


def find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return d
        p = os.path.dirname(d)
        if p == d:
            return None
        d = p


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=None)
    a = ap.parse_args()
    root = a.root or find_root(HERE)
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    with open(a.protocol) as f:
        P = json.load(f)
    h = P["heater"]
    heater = os.path.join(root, h["bin"])
    kernel = os.path.join(root, h["kernel"])
    who = subprocess.run(["timeout", "10", "et-who"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    etw = (who.stdout + who.stderr).strip()
    with open(os.path.join(out, "et-who.txt"), "w") as f:
        f.write(etw + "\n")
    print(etw)
    if "No process holds" not in etw:
        print("the card is in use: not ours, not waiting")
        return 3
    fd = os.open(LOCK, os.O_RDWR | os.O_CREAT, 0o666)
    os.set_inheritable(fd, False)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("the card lock is held: not ours, not waiting")
        return 3
    env = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
    rows, bad = [], 0
    try:
        for name, s in P["sets"].items():
            if s.get("idle") or not str(s.get("values", "")).startswith("file:"):
                continue
            rel = s["values"][5:]
            path = os.path.join(root, rel)
            dump = os.path.join(out, name + ".dump")
            cmd = ["timeout", "10", heater, "--test", h["test"], "--type", s["type"], "--pattern", h["pattern"],
                   "--values", "file:" + path, "--shires", s["mask"], "--per-shire", str(s["per_shire"]),
                   "--seconds", "0", "--budget", f"{h['budget']:g}", "--seed", str(h["seed"]),
                   "--kernel", kernel, "--stop-file", os.path.join(out, "STOP"), "--dump-tiles", dump]
            t0 = time.time()
            p = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env,
                               cwd=root, start_new_session=True, close_fds=True)
            wall = time.time() - t0
            with open(os.path.join(out, name + ".out"), "w") as f:
                f.write(p.stdout)
            with open(os.path.join(out, name + ".err"), "w") as f:
                f.write(p.stderr)
            rec = {}
            for line in p.stdout.splitlines():
                if line.startswith("SPARSITY {"):
                    try:
                        rec = json.loads(line[len("SPARSITY "):])
                    except ValueError:
                        pass
                    break
            ok_dump = os.path.isfile(dump) and open(dump, "rb").read() == open(path, "rb").read()
            nd = (sum(x != y for x, y in zip(open(dump, "rb").read(), open(path, "rb").read()))
                  if os.path.isfile(dump) else None)
            ok = p.returncode == 0 and ok_dump
            bad += 0 if ok else 1
            row = dict(set=name, type=s["type"], values=rel, sha256=sha(path), rc=p.returncode, wall_s=round(wall, 3),
                       dump_bytes=os.path.getsize(dump) if os.path.isfile(dump) else 0, byte_for_byte=ok_dump,
                       bytes_differ=nd, record={k: rec.get(k) for k in ("type", "cycles_per_op", "lane_valid",
                                                                        "harts", "mhz", "ops", "tflops") if k in rec},
                       cmd=cmd)
            rows.append(row)
            print(f"{name:7s} {s['type']}: rc {p.returncode}, {row['dump_bytes']} bytes dumped, "
                  f"{'OK byte for byte' if ok_dump else 'MISMATCH (%s bytes differ)' % nd}  {row['record']}  "
                  f"sha256 {row['sha256'][:12]}")
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    with open(os.path.join(out, "tile_check.json"), "w") as f:
        json.dump(dict(protocol=os.path.basename(a.protocol), root_head=None, rows=rows, failures=bad), f, indent=1)
    print("TILE CHECK " + ("PASS" if bad == 0 else f"FAIL ({bad})"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
