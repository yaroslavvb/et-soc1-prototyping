#!/usr/bin/env python3
"""E89 runner (Q130): one pass of the low-power heat lock-in on the local card (aifoundry3 card 0, 600 MHz pinned).

A pass is: the start gate (wait, idle, until the die reading is at most --gate-c, for at most --gate-max-s), an idle
bracket of --idle-s with no device process, then the blocks in the registered order. A block switches one kind
against its reference as a square wave: a lead-in half of the reference (--lead-s), then --cycles cycles of
[kind for --half-s][reference for --half-s]. Every half is filled with back-to-back launches of the half's tile
(`sparsity_host --test fma`, 1,024 minions, under `timeout 10`, at most --launch-s each), scheduled against the
block's own clock so each half starts on time; an "idle" reference half launches nothing. The lock-in reduction
(reduce_e89.py) reads the die from the sampler's file; this runner only schedules, records and guards.

    python3 tools/claims-v3/e89/run_e89.py <out-dir> --root <tree> --tel-live <sampler file> --sparsity <bin>
        [--pass-no 8910] [--card aifoundry3] [--smoke] [--dry] [--list]
    exit 0 done; 3 another user on this card; 4 the sampler stopped writing; 5 no telemetry; 6 the die reached
         --max-c; 8 STOP file; 9 a tile failed its kinds.json sha256

The blocks (registered in tools/claims-v3/e89/E89.md; kind against reference, both kinds.json tiles):
    i8full   int8.full     vs int8.zeros       i8neg1   int8.neg_ones vs int8.zeros
    i8gauss  int8.gauss_q  vs int8.zeros       i8zero   int8.zeros    vs idle (no launch)
    i8small  int8.smallint vs int8.zeros       f32ones  fp32.ones     vs fp32.zeros
    i8sp50   int8.sparse50 vs int8.zeros       f32randn fp32.randn    vs fp32.zeros  (the reference block, last)
Order: the seven low-power blocks shuffled with Random("E89|<card>|<pass>"), then f32randn.
Nothing here opens the management node; nothing is set.
"""
import argparse
import json
import os
import random
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kinds"))
import e78_common as ec  # noqa: E402

BLOCKS = {  # name: (kind item, reference item or "idle")
    "i8full": ("int8.full", "int8.zeros"),
    "i8gauss": ("int8.gauss_q", "int8.zeros"),
    "i8small": ("int8.smallint", "int8.zeros"),
    "i8sp50": ("int8.sparse50", "int8.zeros"),
    "i8neg1": ("int8.neg_ones", "int8.zeros"),
    "i8zero": ("int8.zeros", "idle"),
    "f32ones": ("fp32.ones", "fp32.zeros"),
    "f32randn": ("fp32.randn", "fp32.zeros"),
}
REF_BLOCK = "f32randn"
LOW_BLOCKS = [b for b in BLOCKS if b != REF_BLOCK]
FIRST_PASS = 8910
EXIT_OTHERS, EXIT_STALL, EXIT_NOTEL, EXIT_HOT, EXIT_STOP, EXIT_TILES = 3, 4, 5, 6, 8, 9
DEV_COMM = ("ettelem", "dev_mngt_servi", "et-powertop", "mmbench_launch", "sys_emu", "Runner.Worker")


def pass_order(card, pass_no):
    low = sorted(LOW_BLOCKS)
    random.Random(f"E89|{card}|{pass_no}").shuffle(low)
    return low + [REF_BLOCK]


def last_sample(path):
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 12000))
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
    """Another user on this card (run_e78.py's test, unchanged)."""
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
    ap.add_argument("--tel-live", default=None)
    ap.add_argument("--sparsity", default="build/sparsity/host/sparsity_host")
    ap.add_argument("--pass-no", type=int, default=FIRST_PASS)
    ap.add_argument("--card", default="aifoundry3")
    ap.add_argument("--half-s", type=float, default=30.0)
    ap.add_argument("--cycles", type=int, default=2)
    ap.add_argument("--lead-s", type=float, default=20.0)
    ap.add_argument("--launch-s", type=float, default=6.8, help="the longest launch; + ~0.7 s start-up < timeout 10")
    ap.add_argument("--overhead-s", type=float, default=0.75, help="a launch's start-up and exit, measured in E78")
    ap.add_argument("--min-launch-s", type=float, default=1.0)
    ap.add_argument("--idle-s", type=float, default=15.0)
    ap.add_argument("--gate-c", type=float, default=62.0)
    ap.add_argument("--gate-max-s", type=float, default=60.0)
    ap.add_argument("--max-c", type=float, default=78.0)
    ap.add_argument("--stale-s", type=float, default=3.0)
    ap.add_argument("--blocks", default=None, help="smoke only: exactly these blocks, in this order")
    ap.add_argument("--smoke", action="store_true", help="i8full only, 10 s halves, one cycle, 5 s lead-in and idle")
    ap.add_argument("--dry", action="store_true", default=bool(os.environ.get("V3_DRY")))
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        a.half_s, a.cycles, a.lead_s, a.idle_s, a.gate_max_s = 10.0, 1, 5.0, 5.0, 0.0
        a.blocks = a.blocks or "i8full"
    os.chdir(a.root)
    items = {it["name"]: it for it in ec.load_items()}
    order = a.blocks.split(",") if a.blocks else pass_order(a.card, a.pass_no)
    miss = [b for b in order if b not in BLOCKS]
    if miss:
        raise SystemExit(f"unknown blocks {miss}")
    used = sorted({x for b in order for x in BLOCKS[b] if x != "idle"})
    bad = ec.verify_tiles(a.root, [items[n] for n in used])
    block_s = a.lead_s + a.cycles * 2 * a.half_s
    est = a.gate_max_s + a.idle_s + len(order) * block_s + 10
    if a.list:
        print(json.dumps({"blocks": order, "items": used, "block_s": block_s, "est_s": int(est),
                          "max_s": int(est + 600), "tile_problems": bad}))
        sys.exit(EXIT_TILES if bad else 0)
    if bad:
        print("tiles failed their kinds.json sha256: " + "; ".join(bad), file=sys.stderr)
        sys.exit(EXIT_TILES)
    dev_n = os.environ.get("ET_DEVICES")
    dev_n = int(dev_n) if dev_n not in (None, "") else None
    ENV = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
    os.makedirs(os.path.join(a.out, "tiles"), exist_ok=True)
    stop_file = os.path.join(a.out, "STOP")
    json.dump({"card": a.card, "args": vars(a), "blocks": {b: BLOCKS[b] for b in order}, "order": order,
               "items": [items[n] for n in used], "et_devices": dev_n, "experiment": "E89"},
              open(os.path.join(a.out, "configs.json"), "w"), indent=1)
    runs = open(os.path.join(a.out, "runs.jsonl"), "a")
    marks = open(os.path.join(a.out, "marks.jsonl"), "a")
    log = open(os.path.join(a.out, "run.log"), "a")

    def say(msg):
        line = f"{time.strftime('%H:%M:%S')} [{a.card}] {msg}"
        print(line, file=log, flush=True)
        print(line, flush=True)

    def mark(**kw):
        marks.write(json.dumps(kw) + "\n")
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
            return 58.0
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

    def check(where):
        if a.dry:
            return
        o = others_on_card(dev_n)
        if o:
            stop(EXIT_OTHERS, f"{where}: another user on this card: {o}")
        if os.path.exists(stop_file):
            stop(EXIT_STOP, f"{where}: {stop_file} exists")

    def wait_until(t_end):
        if a.dry:
            return
        while True:
            now = time.time()
            if now >= t_end:
                return
            reading()
            time.sleep(min(0.2, t_end - now))

    dumped = set()

    def launch(item, secs, blk_name, half_idx, role):
        it = items[item]
        cmd = [a.sparsity, "--test", "fma", "--type", it["type"], "--pattern", "none",
               "--values", "file:" + os.path.join(a.root, it["tile"]), "--shires", "0xffffffff", "--per-shire", "32",
               "--seconds", f"{secs:.2f}", "--seed", str(a.pass_no + 1), "--stop-file", stop_file]
        if item not in dumped:
            cmd += ["--dump-tiles", os.path.join(a.out, "tiles", f"{item}.p{a.pass_no}.bin")]
            dumped.add(item)
        t0 = time.time()
        if a.dry:
            print("DRY hold10: " + " ".join(cmd), file=sys.stderr, flush=True)
            time.sleep(0.0)
            r = subprocess.CompletedProcess(cmd, 0, "", "")
        else:
            r = subprocess.run(["timeout", "10"] + cmd, env=ENV, stdin=subprocess.DEVNULL, capture_output=True, text=True)
        t1 = time.time()
        n = 0
        for line in r.stdout.splitlines():
            if line.startswith("SPARSITY {"):
                rec = json.loads(line[len("SPARSITY "):])
                runs.write(json.dumps({"card": a.card, "pass": a.pass_no, "block": blk_name, "half": half_idx,
                                       "role": role, "item": item, "type": it["type"], "kind_name": it["kind"],
                                       "secs": round(secs, 2), **rec}) + "\n")
                n += 1
        runs.flush()
        mark(kind="launch", block=blk_name, half=half_idx, role=role, item=item, secs=round(secs, 2),
             t_start_ms=int(t0 * 1000), t_end_ms=int(t1 * 1000), rc=r.returncode, records=n)
        if not n and not a.dry:
            say(f"{blk_name} half {half_idx} {item}: no launch record (rc {r.returncode}) {r.stderr[-200:]!r}")
        return n

    def fill_half(item, t_start, t_end, blk_name, half_idx, role):
        """Back-to-back launches of `item` from t_start to t_end (an idle half launches nothing)."""
        wait_until(t_start)
        mark(kind="half", block=blk_name, half=half_idx, role=role, item=item,
             t_start_ms=int(t_start * 1000), t_end_ms=int(t_end * 1000))
        nl = 0
        if item == "idle":
            wait_until(t_end)
            return 0
        while True:
            rem = t_end - time.time() - a.overhead_s
            if rem < a.min_launch_s:
                break
            reading()
            launch(item, min(a.launch_s, rem), blk_name, half_idx, role)
            nl += 1
            if a.dry:
                break
        wait_until(t_end)
        return nl

    say(f"E89 pass {a.pass_no}: {len(order)} blocks {order}; halves {a.half_s:g} s x {a.cycles} cycles after a "
        f"{a.lead_s:g} s lead-in ({block_s:g} s a block); gate <= {a.gate_c:g} C for <= {a.gate_max_s:g} s, idle "
        f"{a.idle_s:g} s; cap {a.max_c:g} C; ET_DEVICES={dev_n}; tiles verified against kinds.json")
    check("start")
    # the start gate: idle until the die reading is at most --gate-c (bounded)
    g0 = time.time()
    t = reading()
    while t > a.gate_c and time.time() - g0 < a.gate_max_s:
        time.sleep(0.5)
        t = reading()
    g1 = time.time()
    mark(kind="gate", t_start_ms=int(g0 * 1000), t_end_ms=int(g1 * 1000), die_c=t, reached=bool(t <= a.gate_c),
         gate_c=a.gate_c)
    say(f"gate: die {t:g} C after {g1 - g0:.1f} s ({'reached' if t <= a.gate_c else 'NOT reached, going on'})")
    # the idle bracket
    i0 = time.time()
    wait_until(i0 + a.idle_s)
    mark(kind="idle", t_start_ms=int(i0 * 1000), t_end_ms=int(time.time() * 1000), die_c=reading())
    for bi, b in enumerate(order):
        kind, ref = BLOCKS[b]
        check(f"pass {a.pass_no} block {b}")
        tb = time.time() + 0.3
        mark(kind="block", block=b, pos=bi, item=kind, ref=ref, t_start_ms=int(tb * 1000),
             t_end_ms=int((tb + block_s) * 1000), half_s=a.half_s, cycles=a.cycles, lead_s=a.lead_s,
             die_c=reading())
        h = 0
        fill_half(ref, tb, tb + a.lead_s, b, h, "lead")
        t_c = tb + a.lead_s
        for c in range(a.cycles):
            h += 1
            fill_half(kind, t_c, t_c + a.half_s, b, h, "K")
            h += 1
            fill_half(ref, t_c + a.half_s, t_c + 2 * a.half_s, b, h, "Z")
            t_c += 2 * a.half_s
        say(f"pass {a.pass_no} block {bi + 1}/{len(order)} {b} ({kind} vs {ref}) done, die {reading():g} C")
    t_tail = time.time()
    wait_until(t_tail + (0 if a.dry else 5.0))
    mark(kind="tail", t_start_ms=int(t_tail * 1000), t_end_ms=int(time.time() * 1000))
    say("done")


if __name__ == "__main__":
    main()
