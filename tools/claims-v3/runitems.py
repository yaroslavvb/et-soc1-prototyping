#!/usr/bin/env python3
"""A manifest-driven runner for version-3 blocks whose items need their own device-tool arguments.

    python3 tools/claims-v3/runitems.py <out-dir> --root <tree> --gen <make_*.py dir> --items NAMES
        --tool <binary> [--tool-key enercat] [--tel-live <file>] [--heater <binary>] [--sparsity <binary>]
        [--blocks 1] [--first-block 1] [--seed 1] [--target 58] [--preheat 59] [--max-c 78] [--item-s 4]
        [--burnin 2] [--card <id>] [--dry] [--list]

hl/run_hl.py does this for the bit-flip ladder, where every item is one of two fixed command shapes. E75 and E76
need per-item flags (--slice-bytes, --region, --stride, --scp, --window, --harts), so the command line lives in
the manifest instead: each item carries

    {"name": ..., "kind": "cmd", "tool": "enercat"|"sparsity", "args": [ ... ], "tag": "ENERCAT {", ...}

and `args` is appended to the tool's path verbatim, with %GEN% in any argument replaced by the generator
directory. Everything else — the approach protocol, the shuffled order, the repeated drift anchor, the launch
caps, the record format — is run_hl.py's, kept identical so the same reductions read both:

  * every device process runs under `timeout 10` and with stdin closed;
  * each launch waits until the die reading first shows --target or less, after heating to --preheat, and a pass
    that cannot reach the launch reading three runs in a row stops (exit 5);
  * a reading at or above --max-c stops the pass (exit 6); a stale telemetry line stops it (exit 4, 7);
  * an item named `anchor_pi` (kind "fma") runs first and last in every block as the drift anchor;
  * records: runs.jsonl (one line per launch), marks.jsonl (one line per device event), run.log.

Exit codes are run_hl.py's: 3 another user, 4 no telemetry, 5 launch reading unreachable, 6 over the cap,
7 the sampler is gone, 8 a STOP file.
"""
import argparse
import json
import os
import random
import subprocess
import sys
import time

EXIT_OTHERS, EXIT_NOTEL, EXIT_UNREACHED, EXIT_HOT, EXIT_STALL, EXIT_STOP = 3, 4, 5, 6, 7, 8
HEATER_ARGS = ["--test", "fma", "--type", "fp32", "--pattern", "none", "--values", "randn",
               "--shires", "0xffffffff", "--per-shire", "32", "--seconds", "2", "--seed", "1"]


def last_sample(path):
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            end = f.tell()
            f.seek(max(0, end - 65536))
            lines = [l for l in f.read().decode(errors="replace").splitlines() if l.startswith("{")]
        return json.loads(lines[-1]) if lines else None
    except (OSError, ValueError):
        return None


def others_on_card(dev_n):
    """et-who's own view, kept to the lines that name a device node or a lock (14-card-behaviour.md)."""
    try:
        r = subprocess.run(["sudo", "-n", "/usr/local/sbin/et-holders"], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return "et-holders unreadable"
    if r.returncode != 0:
        return "et-holders unreadable"
    me = os.environ.get("USER", "")
    out = []
    want = f"/dev/et{dev_n if dev_n is not None else 0}_"
    lock = f"lock:etsoc-shire{dev_n if dev_n is not None else 0}.lock"
    for line in r.stdout.splitlines():
        if "et-holders" in line:
            continue
        f = line.split()
        if len(f) >= 2 and (f[0].startswith(want) or f[0] == lock) and f[1] not in ("", me):
            out.append(":".join(f[1:3]))
    return ",".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--root", required=True)
    ap.add_argument("--gen", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--tool", required=True, help="the binary that item['tool'] == 'main' resolves to")
    ap.add_argument("--sparsity", default="build/sparsity/host/sparsity_host")
    ap.add_argument("--heater", default="build/sparsity/host/sparsity_host")
    ap.add_argument("--tel-live", default="")
    ap.add_argument("--blocks", type=int, default=1)
    ap.add_argument("--first-block", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--target", type=float, default=58.0)
    ap.add_argument("--preheat", type=float, default=59.0)
    ap.add_argument("--max-c", type=float, default=78.0)
    ap.add_argument("--max-heats", type=int, default=150)
    ap.add_argument("--max-wait", type=float, default=240.0)
    ap.add_argument("--stale-s", type=float, default=20.0)
    ap.add_argument("--item-s", type=float, default=4.0)
    ap.add_argument("--fma-s", type=float, default=4.0)
    ap.add_argument("--burnin", type=int, default=2)
    ap.add_argument("--card", default="unknown")
    ap.add_argument("--dry", action="store_true", default=bool(os.environ.get("V3_DRY")))
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    os.chdir(a.root)
    man = json.load(open(os.path.join(a.gen, "manifest.json")))
    sel = lambda it, w: it["name"] == w or (w.endswith("_") and it["name"].startswith(w))
    want = a.items.split(",")
    items = [it for it in man["items"] if any(sel(it, w) for w in want)]
    missing = [w for w in want if not any(sel(it, w) for it in man["items"])]
    if missing:
        raise SystemExit(f"--items that select nothing: {missing}")
    bad = []
    for it in items:   # the operand files that will run, by size, before anything opens the card
        p = it.get("src")
        if p:
            p = p.replace("%GEN%", a.gen)
            if not os.path.isfile(p) or os.path.getsize(p) != it.get("src_bytes", 256):
                bad.append(f"{p}: want {it.get('src_bytes', 256)} bytes")
    if bad:
        raise SystemExit("operand files: " + "; ".join(bad))
    has_pi = any(it["name"] == "anchor_pi" for it in items)
    per_block = len(items) + (1 if has_pi else 0)
    est = a.burnin * 50 + a.blocks * sum(50 + (a.fma_s if it["kind"] == "fma" else a.item_s)
                                         for it in items + ([items[0]] if has_pi else []))
    if a.list:
        print(json.dumps({"n": len(items), "runs_per_block": per_block, "blocks": a.blocks, "max_s": int(est),
                          "items": [it["name"] for it in items]}))
        return
    dev_n = os.environ.get("ET_DEVICES")
    dev_n = int(dev_n) if dev_n not in (None, "") else None
    ENV = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
    os.makedirs(a.out, exist_ok=True)
    stop_file = os.path.join(a.out, "STOP")
    json.dump({"card": a.card, "args": vars(a), "items": items, "et_devices": dev_n},
              open(os.path.join(a.out, "configs.json"), "w"), indent=1)
    runs = open(os.path.join(a.out, "runs.jsonl"), "a")
    marks = open(os.path.join(a.out, "marks.jsonl"), "a")
    log = open(os.path.join(a.out, "run.log"), "a")

    def say(msg):
        line = f"{time.strftime('%H:%M:%S')} [{a.card}] {msg}"
        print(line, file=log, flush=True)
        print(line, flush=True)

    def dev(cmd):
        if a.dry:
            print("DRY hold10: " + " ".join(cmd), file=sys.stderr, flush=True)
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return subprocess.run(["timeout", "10"] + cmd, env=ENV, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True)

    def mark(kind, name, t0, t1, blk, **extra):
        marks.write(json.dumps({"kind": kind, "item": name, "block": blk, "t_start_ms": int(t0 * 1000),
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

    def approach(name, blk):
        if a.dry:
            print(f"DRY approach: heat to {a.preheat:g}, wait for {a.target:g}", file=sys.stderr, flush=True)
            return {"start_c": a.target, "start_hot_c": a.preheat, "heats": 0, "wait_s": 0.0, "on_protocol": True}
        t = reading()
        heats = 0
        while a.preheat > 0 and t < a.preheat and heats < a.max_heats:
            h0 = time.time()
            r = dev([a.heater] + HEATER_ARGS + ["--stop-file", stop_file])
            mark("heater", name, h0, time.time(), blk, die_c=t, rc=r.returncode)
            heats += 1
            time.sleep(0.4)
            t = reading()
        hot = t
        w0 = time.time()
        while t > a.target and time.time() - w0 < a.max_wait:
            time.sleep(0.1)
            t = reading()
        on = (a.preheat <= 0 or hot >= a.preheat) and t <= a.target
        return {"start_c": t, "start_hot_c": hot, "heats": heats, "wait_s": round(time.time() - w0, 2),
                "on_protocol": on}

    def command(it, blk):
        if it["kind"] == "fma":   # the drift anchor, exactly hl/run_hl.py's
            return ([a.sparsity, "--test", "fma", "--type", "fp32", "--pattern", "none", "--values",
                     it.get("values", "pi"), "--shires", "0xffffffff", "--per-shire", "32",
                     "--seconds", str(a.fma_s), "--seed", str(blk + 1), "--stop-file", stop_file], "SPARSITY {")
        args = [str(x).replace("%GEN%", a.gen).replace("%ITEM_S%", str(a.item_s)) for x in it["args"]]
        return [a.tool] + args, it.get("tag", "ENERCAT {")

    def check_others(where):
        if a.dry:
            return
        o = others_on_card(dev_n)
        if o:
            stop(EXIT_OTHERS, f"{where}: another user on this card: {o}")
        if os.path.exists(stop_file):
            stop(EXIT_STOP, f"{where}: {stop_file} exists")

    say(f"{len(items)} items, {per_block} runs per block x {a.blocks} blocks, at most {est / 60:.0f} min; "
        f"launch at {a.target:g} C after {a.preheat:g} C; cap {a.max_c:g} C; ET_DEVICES={dev_n}")
    pi = next((it for it in items if it["name"] == "anchor_pi"), None)
    for i in range(a.burnin):
        check_others("burn-in")
        it = pi or items[0]
        ap_ = approach("burnin", -1)
        cmd, _ = command(it, -1)
        t0 = time.time()
        r = dev(cmd)
        mark("burnin", it["name"], t0, time.time(), -1, rc=r.returncode, **ap_)
        say(f"burn-in {i + 1}/{a.burnin}: {it['name']} at {ap_['start_c']} C (rc {r.returncode})")
    unreached = 0
    for blk in range(a.first_block, a.first_block + a.blocks):
        rest = [it for it in items if it is not pi]
        random.Random(f"{a.card}|{a.seed}|{blk}").shuffle(rest)
        order = ([pi] if pi else []) + rest + ([pi] if pi else [])
        for pos, it in enumerate(order):
            check_others(f"block {blk} {it['name']}")
            for attempt in (1, 2):
                ap_ = approach(it["name"], blk)
                if not ap_["on_protocol"]:
                    unreached += 1
                    mark("skipped", it["name"], time.time(), time.time(), blk, pos=pos, **ap_)
                    say(f"block {blk} {it['name']}: launch reading not reached (hot {ap_.get('start_hot_c')} C, "
                        f"now {ap_['start_c']} C after {ap_['heats']} heats, {ap_['wait_s']} s): skipped")
                    if unreached >= 3:
                        stop(EXIT_UNREACHED, "three runs in a row could not reach the launch reading")
                    break
                unreached = 0
                cmd, tag = command(it, blk)
                t0 = time.time()
                r = dev(cmd)
                t1 = time.time()
                n = 0
                for line in r.stdout.splitlines():
                    if line.startswith(tag):
                        rec = json.loads(line[len(tag) - 1:])
                        runs.write(json.dumps({"card": a.card, "block": blk, "pos": pos, "item": it["name"],
                                               "kind": it["kind"], "attempt": attempt,
                                               **{k: it[k] for k in it if k in ("level", "k", "w", "family",
                                                                               "line_bits", "designed")},
                                               **{k: ap_[k] for k in ("start_c", "start_hot_c", "heats", "wait_s")},
                                               **rec}) + "\n")
                        n += 1
                runs.flush()
                mark("run", it["name"], t0, t1, blk, pos=pos, attempt=attempt, rc=r.returncode, launches=n, **ap_)
                say(f"block {blk} #{pos} {it['name']}: {n} launches, start {ap_['start_c']} C "
                    f"(hot {ap_['start_hot_c']}) after {ap_['heats']} heats and {ap_['wait_s']} s"
                    + ("" if n or a.dry else f"; rc={r.returncode} {r.stderr[-200:]!r}"))
                if n or a.dry:
                    break
                say(f"block {blk} {it['name']}: no launch record (rc {r.returncode}): one retry")
    time.sleep(0 if a.dry else 3)
    say("done")


if __name__ == "__main__":
    main()
