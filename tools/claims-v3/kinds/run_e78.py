#!/usr/bin/env python3
"""E78 runner (Q130): one pass of the kinds-of-numbers energy matrix on the local card. A port of
tools/claims-v3/hlp/run_hlp.py (E79), itself a port of hl/run_hl.py (E60/E65/E67/E70), with the changes marked
`E78` below:

  1. the items are kinds.json's 51 (type, kind) tiles plus the built-in pi tie (e78_common.py), and every tile is
     checked against kinds.json's sha256 before anything opens the card (exit 9 on a mismatch);
  2. the order is e78_common.pass_order: the tie first and last, three segments, every anchor (each type's zeros
     and its random kind) once per segment, the other kinds shuffled across the segments per pass;
  3. THE QUIET RULE: a run is spawned only after at least --quiet-s seconds without any device process (heater or
     run), with the die reading still inside the launch band, so the idle bracket in front of it
     ([t0-1.2 s, t0-0.2 s)) begins at least ~0.8 s after the previous process ended. E79's amendment A7 found its
     bracket contaminated: in 109 of its 480 runs the bracket began before the previous process had ended, while
     board power settles within 0.2 s of a process ending (e78_desk_checks.txt [1], [2]);
  4. each run records the end time of the previous device process and the quiet time it actually had.

    python3 tools/claims-v3/kinds/run_e78.py <out-dir> --root <tree root> --tel-live <sampler file>
        --heater <sparsity_host> --sparsity <sparsity_host> [--first-block 7810] [--seed 7810] [--tiers 1,2]
        [--target 58] [--preheat 59] [--quiet-s 2.0] [--fma-s 4] [--burnin 2] [--card <id>] [--dry] [--list]
        [--items a,b,...  (smoke only: run exactly these, in this order)]
    exit 0 done; 3 another user on this card; 4 the sampler stopped writing; 5 no telemetry; 6 the die reached
         --max-c; 7 the launch reading could not be reached; 8 STOP file; 9 a tile failed its sha256

Every device process runs under `timeout 10` with stdin from /dev/null (lib.sh hold10); sparsity launches carry
--stop-file <out>/STOP; nothing here opens the management node: the die reading comes from the file the block's
sampler writes (--tel-live), and a reading older than --stale-s stops the pass instead of heating blind.
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e78_common as ec  # noqa: E402

HEATER_ARGS = ["--test", "fma", "--type", "fp32", "--pattern", "none", "--values", "randn",
               "--shires", "0xffffffff", "--per-shire", "32", "--seconds", "2", "--seed", "1"]
EXIT_OTHERS, EXIT_STALL, EXIT_NOTEL, EXIT_HOT, EXIT_UNREACHED, EXIT_STOP, EXIT_TILES = 3, 4, 5, 6, 7, 8, 9
DEV_COMM = ("ettelem", "dev_mngt_servi", "et-powertop", "mmbench_launch", "sys_emu", "Runner.Worker")


def last_sample(path):
    """The last complete telemetry line the running sampler wrote, or None."""
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 8000))
            lines = f.read().decode(errors="ignore").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        if line.startswith("{"):
            try:
                return json.loads(line)
            except ValueError:
                continue
    return None


def others_on_card(dev):
    """Another user on this card (unchanged from run_hlp.py)."""
    me, hits = os.environ.get("USER", ""), []
    if dev is not None:
        r = subprocess.run(["sudo", "-n", "/usr/local/sbin/et-holders"], capture_output=True, text=True)
        if r.returncode != 0:
            return [f"et-holders unreadable (rc {r.returncode}): {r.stderr.strip()[:80]}"]
        for line in r.stdout.splitlines():
            f = line.split()
            if len(f) >= 2 and f[1] != me and (f[0].startswith(f"/dev/et{dev}_") or f[0] == f"lock:etsoc-shire{dev}.lock"):
                hits.append(" ".join(f[:3]))
        return hits
    uid = os.getuid()
    r = subprocess.run(["ps", "-eo", "uid=,pid=,comm="], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        p = line.split(None, 2)
        if len(p) == 3 and int(p[0]) != uid and (p[2].strip().endswith("_host") or p[2].strip().startswith(DEV_COMM)):
            hits.append(":".join(x.strip() for x in p))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--root", required=True)
    ap.add_argument("--kinds", default=None, help="kinds.json (default: the one beside this file)")
    ap.add_argument("--tel-live", default=None)
    ap.add_argument("--heater", default="build/sparsity/host/sparsity_host")
    ap.add_argument("--sparsity", default="build/sparsity/host/sparsity_host")
    ap.add_argument("--first-block", type=int, default=ec.FIRST_PASS)
    ap.add_argument("--seed", type=int, default=None, help="unused beyond the record: the order is seeded by pass")
    ap.add_argument("--tiers", default="1,2")
    ap.add_argument("--items", default=None, help="smoke only: exactly these items, in this order")
    ap.add_argument("--target", type=float, default=58.0)
    ap.add_argument("--preheat", type=float, default=59.0, help="heat to this reading first (0: never heat)")
    ap.add_argument("--quiet-s", type=float, default=2.0, help="E78: s without any device process before a spawn")
    ap.add_argument("--max-heats", type=int, default=15, help="heater launches allowed per run's approach")
    ap.add_argument("--max-wait", type=float, default=600.0, help="s to wait for the reading to fall to --target")
    ap.add_argument("--max-c", type=float, default=78.0, help="stop the pass at this minion-shire (or PMIC) reading")
    ap.add_argument("--stale-s", type=float, default=3.0, help="a telemetry line older than this: the sampler is gone")
    ap.add_argument("--fma-s", type=float, default=4.0)
    ap.add_argument("--shires", default="0xffffffff")
    ap.add_argument("--per-shire", default="32")
    ap.add_argument("--burnin", type=int, default=2)
    ap.add_argument("--card", default=None)
    ap.add_argument("--dry", action="store_true", default=bool(os.environ.get("V3_DRY")))
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    os.chdir(a.root)
    items = ec.load_items(a.kinds or ec.KINDS_JSON)
    by = {it["name"]: it for it in items}
    blk = a.first_block
    tiers = tuple(int(x) for x in a.tiers.split(","))
    card = a.card or "aifoundry3"
    if a.items:
        want = a.items.split(",")
        miss = [w for w in want if w not in by]
        if miss:
            raise SystemExit(f"--items not in kinds.json: {miss}")
        order = [{"pos": i, "item": n, "segment": 0} for i, n in enumerate(want)]
    else:
        order = ec.pass_order(items, card, blk, tiers)
    # E78 change 1: every tile that will run, against kinds.json, before anything opens the card
    used = sorted({r["item"] for r in order})
    bad = ec.verify_tiles(a.root, [by[n] for n in used])
    est = a.burnin * 9 + len(order) * (a.fma_s + 5.3)    # E79 measured 8.7 s a run; + the quiet rule
    if a.list:
        print(json.dumps({"runs": len(order), "items": len(used), "max_s": int(3 * est + 600), "est_s": int(est),
                          "tiers": list(tiers), "tile_problems": bad, "order": [r["item"] for r in order]}))
        sys.exit(EXIT_TILES if bad else 0)
    if bad:
        print("tiles failed their kinds.json sha256: " + "; ".join(bad), file=sys.stderr)
        sys.exit(EXIT_TILES)
    dev_n = os.environ.get("ET_DEVICES")
    dev_n = int(dev_n) if dev_n not in (None, "") else None
    ENV = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
    os.makedirs(os.path.join(a.out, "tiles"), exist_ok=True)
    stop_file = os.path.join(a.out, "STOP")
    json.dump({"card": card, "args": vars(a), "items": [by[n] for n in used], "order": order,
               "et_devices": dev_n, "experiment": "E78"},
              open(os.path.join(a.out, "configs.json"), "w"), indent=1)
    json.dump(order, open(os.path.join(a.out, "plan.json"), "w"), indent=0)
    runs = open(os.path.join(a.out, "runs.jsonl"), "a")
    marks = open(os.path.join(a.out, "marks.jsonl"), "a")
    log = open(os.path.join(a.out, "run.log"), "a")
    last_end = [time.time() - 3600.0]     # E78 change 4: the end of the newest device process

    def say(msg):
        line = f"{time.strftime('%H:%M:%S')} [{card}] {msg}"
        print(line, file=log, flush=True)
        print(line, flush=True)

    def dev(cmd):
        if a.dry:
            print("DRY hold10: " + " ".join(cmd), file=sys.stderr, flush=True)
            return subprocess.CompletedProcess(cmd, 0, "", "")
        try:
            return subprocess.run(["timeout", "10"] + cmd, env=ENV, stdin=subprocess.DEVNULL,
                                  capture_output=True, text=True)
        finally:
            last_end[0] = time.time()

    def mark(kind, name, t0, t1, blk_, **extra):
        marks.write(json.dumps({"kind": kind, "item": name, "block": blk_, "t_start_ms": int(t0 * 1000),
                                "t_end_ms": int(t1 * 1000), **extra}) + "\n")
        marks.flush()

    def stop(code, msg):
        say(f"STOP ({code}): {msg}")
        try:
            open(stop_file, "a").write(msg + "\n")
        except OSError:
            pass
        sys.exit(code)

    def reading():
        if a.dry:
            return a.target
        s = last_sample(a.tel_live)
        if s is None:
            stop(EXIT_NOTEL, "no telemetry line")
        age = time.time() - s["t_ms"] / 1000.0
        if age > a.stale_s:
            stop(EXIT_STALL, f"the newest telemetry line is {age:.1f} s old: the sampler is gone")
        try:
            t = float(s["temp_c"]["minshire"][0])
            pmic = float(s["temp_c"].get("pmic", 0))
        except (KeyError, IndexError, TypeError, ValueError):
            stop(EXIT_NOTEL, "telemetry line without temp_c.minshire")
        if t >= a.max_c or pmic >= a.max_c + 10:
            stop(EXIT_HOT, f"die reading {t} C (PMIC {pmic} C) >= cap {a.max_c} C")
        return t

    def in_band(t):
        return a.preheat <= 0 or (a.target - 0.5 <= t <= a.target)

    def approach(name, blk_):
        """Heat to --preheat if below it, idle until the reading first shows --target or less, then (E78 change 3)
        keep idling until --quiet-s have passed since the last device process, as long as the reading stays in
        the launch band [target-0.5, target]. If it falls out of the band below, heat again and start over."""
        if a.dry:
            print(f"DRY approach: heat to {a.preheat:g}, wait for {a.target:g}, then {a.quiet_s:g} s quiet",
                  file=sys.stderr, flush=True)
            return {"start_c": a.target, "start_hot_c": a.preheat, "heats": 0, "wait_s": 0.0,
                    "quiet_s": a.quiet_s, "prev_end_ms": int(last_end[0] * 1000), "on_protocol": True}
        t = reading()
        heats = 0
        w0 = time.time()
        while True:
            while a.preheat > 0 and t < a.preheat and heats < a.max_heats:
                h0 = time.time()
                r = dev([a.heater] + HEATER_ARGS + ["--stop-file", stop_file])
                mark("heater", name, h0, time.time(), blk_, die_c=t, rc=r.returncode)
                heats += 1
                time.sleep(0.4)
                t = reading()
            hot = t
            c0 = time.time()
            while t > a.target and time.time() - c0 < a.max_wait:
                time.sleep(0.1)
                t = reading()
            while time.time() - last_end[0] < a.quiet_s and in_band(t) and t <= a.target:
                time.sleep(0.1)
                t = reading()
            if a.preheat > 0 and t < a.target - 0.5 and heats < a.max_heats:
                continue                       # fell below the band while waiting: heat again
            break
        quiet = time.time() - last_end[0]
        on = (a.preheat <= 0 or hot >= a.preheat) and t <= a.target and in_band(t) and quiet >= a.quiet_s
        return {"start_c": t, "start_hot_c": hot, "heats": heats, "wait_s": round(time.time() - w0, 2),
                "quiet_s": round(quiet, 2), "prev_end_ms": int(last_end[0] * 1000), "on_protocol": on}

    dumped = set()

    def command(it, blk_, dump=True):
        vals = it["values"] if it["values"] else "file:" + os.path.join(a.root, it["tile"])
        cmd = [a.sparsity, "--test", "fma", "--type", it["type"], "--pattern", "none", "--values", vals,
               "--shires", a.shires, "--per-shire", a.per_shire, "--seconds", str(a.fma_s), "--seed", str(blk_ + 1),
               "--stop-file", stop_file]
        if dump and it["name"] not in dumped:      # the first run of each item in the pass dumps what it ran
            cmd += ["--dump-tiles", os.path.join(a.out, "tiles", f"{it['name']}.b{blk_}.bin")]
            dumped.add(it["name"])
        return cmd

    def check_others(where):
        if a.dry:
            return
        o = others_on_card(dev_n)
        if o:
            stop(EXIT_OTHERS, f"{where}: another user on this card: {o}")
        if os.path.exists(stop_file):
            stop(EXIT_STOP, f"{where}: {stop_file} exists")

    say(f"E78 pass {blk}: {len(order)} runs of {len(used)} items (tiers {a.tiers}), about {est / 60:.0f} min; "
        f"launch at {a.target:g} C after {a.preheat:g} C, {a.quiet_s:g} s quiet; cap {a.max_c:g} C; "
        f"ET_DEVICES={dev_n}; tiles verified against kinds.json")
    pi = by[ec.TIE]
    for i in range(a.burnin):
        check_others("burn-in")
        ap_ = approach("burnin", -1)
        cmd = command(pi, -1, dump=False)
        t0 = time.time()
        r = dev(cmd)
        mark("burnin", pi["name"], t0, time.time(), -1, rc=r.returncode, **ap_)
        say(f"burn-in {i + 1}/{a.burnin}: {pi['name']} at {ap_['start_c']} C (rc {r.returncode})")
    unreached = 0
    for row in order:
        it = by[row["item"]]
        pos = row["pos"]
        check_others(f"pass {blk} {it['name']}")
        for attempt in (1, 2):
            ap_ = approach(it["name"], blk)
            if not ap_["on_protocol"]:
                unreached += 1
                mark("skipped", it["name"], time.time(), time.time(), blk, pos=pos, segment=row["segment"], **ap_)
                say(f"pass {blk} #{pos} {it['name']}: launch reading not reached (hot {ap_.get('start_hot_c')} C, "
                    f"now {ap_['start_c']} C after {ap_['heats']} heats, {ap_['wait_s']} s, quiet {ap_['quiet_s']} s)"
                    ": skipped")
                if unreached >= 3:
                    stop(EXIT_UNREACHED, "three runs in a row could not reach the launch reading")
                break
            unreached = 0
            cmd = command(it, blk)
            t0 = time.time()
            r = dev(cmd)
            t1 = time.time()
            n = 0
            for line in r.stdout.splitlines():
                if line.startswith("SPARSITY {"):
                    rec = json.loads(line[len("SPARSITY "):])
                    runs.write(json.dumps({"card": card, "block": blk, "pos": pos, "segment": row["segment"],
                                           "item": it["name"], "type": it["type"], "kind_name": it["kind"],
                                           "attempt": attempt,
                                           **{k: ap_[k] for k in ("start_c", "start_hot_c", "heats", "wait_s",
                                                                  "quiet_s", "prev_end_ms")},
                                           **rec}) + "\n")
                    n += 1
            runs.flush()
            mark("run", it["name"], t0, t1, blk, pos=pos, segment=row["segment"], attempt=attempt,
                 rc=r.returncode, launches=n, **ap_)
            say(f"pass {blk} #{pos} {it['name']}: {n} launches, start {ap_['start_c']} C (hot {ap_['start_hot_c']}) "
                f"after {ap_['heats']} heats, {ap_['wait_s']} s, quiet {ap_['quiet_s']} s"
                + ("" if n or a.dry else f"; rc={r.returncode} {r.stderr[-200:]!r}"))
            if n or a.dry:
                break
            say(f"pass {blk} {it['name']}: no launch record (rc {r.returncode}): one retry")
    time.sleep(0 if a.dry else 3)
    say("done")


if __name__ == "__main__":
    main()
