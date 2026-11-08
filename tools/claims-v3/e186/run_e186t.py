#!/usr/bin/env python3
"""E186 train runner (Q158, the kit; E186.md sections 5.1 and 7): one A B B A train of a registered pair on aifoundry3 card 0, its
processes back to back. A port of tools/claims-v3/e182/run_e182t.py (E182's, run on this card on 8 Nov 2026) with E186's items, trains,
harness and tags (E186); the train host is E182's host-only change, built by build_host_e186.sh into build/e186host/ from the same pinned
inputs with the same patch (patch_host_e182.py, unchanged), so its patched source is the one E182 ran. Each process is the patched
host through Q139(k)'s C-logging wrapper with
CCHECK_HOST pointing at it: `--values file:<F> --values-b file:<S> --abba <SFFS|FSSF> --launches 13`, one calibration launch and 13
launches of about 0.49 s, under `timeout 10` with stdin from /dev/null (lib.sh's hold10). The opening and closing anchors are E78 runs
that block_e186.sh runs around it (run_e186.py --items), so the train starts at the launch band the last opening anchor's approach left.

The stops are run_e186.py's (E171's, E178's, E182's): before every process the newest line of the block's live sampler file (--tel-live) is read
and the train ends with EXIT_HOT (6) and a STOP line when board_w >= 65 W or temp_c.minshire[0] >= 70 C; a line older than 3 s ends it
(the sampler is gone, EXIT_STALL 5); the in-run watcher (run_e186.start_watcher) reads the same file every 0.1 s and writes the block's
STOP file, which the host checks before every launch (--stop-file), so a process ends within one launch. Another user's device process
or a holder of this card ends it (run_e78.others_on_card, EXIT_OTHERS 3). Three processes in a row with no launch record end it (EXIT 7).

    python3 -B tools/claims-v3/e186/run_e186t.py <block dir> --root <tree> --tel-live <block>/telemetry.jsonl.raw --block <1861N> \
        --sparsity tools/claims-v3/ccheck/sparsity_ccheck.sh [--processes N] [--dry] [--list]
--processes N runs only the train's first N processes (the smoke: 2 of H16's). An fp16 train (H16) runs the same host with --type fp16:
the patch is type-blind (it fills both tile sets with the --type's fillValues), as the kit's desk test shows on the mock runtime. --dry prints every process's command and runs nothing.
Writes <block dir>/train.jsonl (one line per launch: the process, its orientation and the SPARSITY record), marks.jsonl (a "train" mark
per process) and run.log (appended). Nothing here opens the management node. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e186_common as E  # noqa: E402  (puts tools/claims-v3/kinds on sys.path)
import run_e186 as R     # noqa: E402  (the stops, the watcher and the harness check; nothing runs at import)

EXIT_STOP, EXIT_OTHERS, EXIT_STALL, EXIT_HOT, EXIT_NORECORDS = 2, 3, 5, 6, 7


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--root", required=True)
    ap.add_argument("--tel-live")
    ap.add_argument("--block", type=int, required=True)
    ap.add_argument("--sparsity", default="tools/claims-v3/ccheck/sparsity_ccheck.sh")
    ap.add_argument("--processes", type=int, default=None)
    ap.add_argument("--stale-s", type=float, default=3.0)
    ap.add_argument("--card", default=E.CARD)
    ap.add_argument("--dry", action="store_true", default=bool(os.environ.get("V3_DRY")))
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    os.chdir(a.root)
    tr = E.train_of_block(a.block)
    n = tr["processes"] if a.processes is None else min(a.processes, tr["processes"])
    tiles = {k: E.tile_path(k) for k in (tr["first"], tr["second"])}
    bad = E.verify_tiles_of([tr["first"], tr["second"]])
    if a.list:
        print(json.dumps({"block": a.block, "train": tr["train"], "first": tr["first"], "second": tr["second"], "processes": n,
                          "launches_per_process": E.LAUNCHES, "est_s": round(n * E.PROC_S, 1), "tile_problems": bad}))
        sys.exit(9 if bad else 0)
    if bad:
        print("E186 train: tiles failed their registered sha256: " + "; ".join(bad), file=sys.stderr)
        sys.exit(9)
    if not a.dry:
        refuse = R.harness_problems()
        if refuse:
            print("refusing to run - a reused or E186 file differs from the kit's harness:\n  " + "\n  ".join(refuse), file=sys.stderr)
            sys.exit(9)
    st = E.stops()
    os.makedirs(os.path.join(a.out, "tiles"), exist_ok=True)
    stop_file = os.path.join(a.out, "STOP")
    log = open(os.path.join(a.out, "run.log"), "a")
    recs = open(os.path.join(a.out, "train.jsonl"), "a")
    marks = open(os.path.join(a.out, "marks.jsonl"), "a")
    env = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")

    def say(msg):
        line = f"{time.strftime('%H:%M:%S')} [{a.card}] {msg}"
        print(line, file=log, flush=True)
        print(line, flush=True)

    def stop(code, msg):
        say(f"STOP ({code}): {msg}")
        try:
            open(stop_file, "a").write(msg + "\n")
        except OSError:
            pass
        sys.exit(code)

    def check(where):
        if a.dry:
            return
        if os.path.exists(stop_file):
            stop(EXIT_STOP if not R.TRIPPED else EXIT_HOT, f"{where}: {stop_file} exists")
        s = R.last_sample(a.tel_live)
        if s is None:
            stop(EXIT_STALL, f"{where}: no telemetry line")
        age = time.time() - float(s["t_ms"]) / 1000.0
        if age > a.stale_s:
            stop(EXIT_STALL, f"{where}: the newest telemetry line is {age:.1f} s old: the sampler is gone")
        msg = R.check_line(s, st["board_w"], st["die_shire0_c"], "E186 train", a.tel_live)
        if msg:
            R.write_stop(a.out, msg)
            stop(EXIT_HOT, msg)
        o = R.others_on_card()
        if o:
            stop(EXIT_OTHERS, f"{where}: another user on this card: {o}")

    say(f"E186 train {a.block} ({tr['train']}: {tr['first']} - {tr['second']}): {n} processes of {E.LAUNCHES} launches, about "
        f"{n * E.PROC_S / 60:.1f} min; stops board {st['board_w']} W / die {st['die_shire0_c']} C")
    if a.tel_live and not a.dry:
        _, ev = R.start_watcher(R.last_sample, a.tel_live, st["board_w"], st["die_shire0_c"], a.out, tag="E186 train watcher")
        ev.wait(5.0)
    norec = 0
    for k in range(n):
        ori = tr["orientations"][k]
        check(f"train {a.block} process {k}")
        cmd = [a.sparsity, "--test", "fma", "--type", tr["type"], "--pattern", "none",
               "--values", "file:" + os.path.join(a.root, tiles[tr["first"]]), "--values-b", "file:" + os.path.join(a.root, tiles[tr["second"]]),
               "--abba", ori, "--launches", str(E.LAUNCHES), "--seconds", "60", "--shires", "0xffffffff", "--per-shire", "32",
               "--seed", str(a.block + 1), "--stop-file", stop_file]
        if k == 0:
            cmd += ["--dump-tiles", os.path.join(a.out, "tiles", f"train.b{a.block}.bin")]
        t0 = time.time()
        if a.dry:
            print("DRY hold10: " + " ".join(cmd), file=sys.stderr, flush=True)
            r = subprocess.CompletedProcess(cmd, 0, "", "")
        else:
            r = subprocess.run(["timeout", "10"] + cmd, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)
        t1 = time.time()
        got = 0
        for line in r.stdout.splitlines():
            if line.startswith("SPARSITY {"):
                rec = json.loads(line[len("SPARSITY "):])
                recs.write(json.dumps({"card": a.card, "block": a.block, "train": tr["train"], "process": k, "orientation": ori,
                                       "first": tr["first"], "second": tr["second"], **rec}) + "\n")
                got += 1
        recs.flush()
        marks.write(json.dumps({"kind": "train", "item": tr["train"], "block": a.block, "process": k, "orientation": ori,
                                "t_start_ms": int(t0 * 1000), "t_end_ms": int(t1 * 1000), "rc": r.returncode, "launches": got}) + "\n")
        marks.flush()
        if got == 0 and not a.dry:
            norec += 1
            say(f"train {a.block} process {k}: no launch record (rc {r.returncode}) {r.stderr[-200:]!r}")
            if norec >= 3:
                stop(EXIT_NORECORDS, "three train processes in a row gave no launch record")
        else:
            norec = 0
        if k % 8 == 0 or k == n - 1:
            say(f"train {a.block} process {k} ({ori}): {got} launch records, rc {r.returncode}, {t1 - t0:.2f} s")
    say("done")


if __name__ == "__main__":
    main()
