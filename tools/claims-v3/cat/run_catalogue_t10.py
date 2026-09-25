#!/usr/bin/env python3
"""V3-CAT runner: a patched copy of workloads/enercat/run_catalogue.py (PLAN3 N6, "run_catalogue_t10.py").

    python3 tools/claims-v3/cat/run_catalogue_t10.py <out-dir> --root <tree root> --only NAMES [--passes 1]
        [--burst 3] [--gap 5] [--seed 7] [--host-bin build/enercat_v2/host/enercat_host]
        [--hold-hot C --heater PATH] [--tel-live PATH] [--heat-settle 1.5] [--stall-s 6] [--no-yield]
        [--lead 10] [--dry] [--list]
    exit 0 done; 3 another user or device process appeared (pass stopped); 4 the sampler stopped writing

What is the same as run_catalogue.py: the configurations (imported from workloads/enercat/run_catalogue.py itself,
so the argument lists cannot drift from the committed catalogue's), the --only prefix match, the per-pass shuffle
random.Random(seed + p), the scratchpad prefill before every "prefill" configuration, the gap, the burst command
(--seconds <burst> --window 240000000) and the runs.jsonl / run.log formats.

What is changed (each is recorded in tools/claims-v3/cat/README.md):
  1. every device process runs under `timeout 10` (was 12), with stdin from /dev/null (lib.sh's hold10);
  2. --host-bin chooses the enercat build (default build/enercat_v2/host/enercat_host: dramrow2 needs
     --jump-every / --jump-bytes);
  3. no sampler of its own: block.sh starts and stops ettelem through lib.sh's start_sampler / stop_sampler, and
     --tel-live names the file that sampler is writing (the heater hold reads the die temperature from it; nothing
     here opens the management node);
  4. --hold-hot C: before a configuration's prefill and gap, up to --hold-max (5) heater launches until the last
     telemetry sample's minshire >= C. The first heater launch waits until --hold-after (5.8) s after the previous
     burst ended, so analyze_catalogue.py's idle window after that burst (2.3-5.5 s after it) stays free of heater
     power. After the last heater launch the runner waits --heat-settle (1.5) s more before the prefill and the
     gap, so the next burst's window before it (3.5-0.3 s before it) starts >= 2.3 s after the heater ended: the
     same settling time analyze_catalogue.py gives a preceding burst (prev_hi + 2.3). Heater and prefill intervals
     are logged in marks.jsonl;
  5. --root: the tree root, set explicitly (block.sh passes lib.sh's V3_ROOT), and the process chdirs there;
  6. --lead (default 10, the original's fixed sleep before the first configuration) so --smoke can shorten it;
  7. --dry (or V3_DRY=1): print every device command as lib.sh's dry hold10 does, sleep nowhere, touch nothing;
  8. --list: print the selected configurations and the duration bound as JSON and exit (no card);
  9. an --only prefix that selects nothing is an error (a stale copy of run_catalogue.py on the other host would
     otherwise drop configurations silently); the selected configurations are written to configs.json;
 10. before every configuration: if --tel-live has not grown for --stall-s (6) s, the sampler has died or run out
     of --seconds, so the pass stops (exit 4) instead of running bursts nobody measures; and if lib.sh's
     others_present finds another user or another user's device process, the pass stops (exit 3, the queue's
     "someone else on the card" code), because another kernel spoils the idle brackets and the card is shared.
"""
import argparse
import json
import os
import random
import socket
import subprocess
import sys
import time

HEATER_ARGS = ["--test", "fma", "--type", "fp32", "--pattern", "none", "--values", "randn",
               "--shires", "0xffffffff", "--per-shire", "32", "--seconds", "2", "--seed", "1"]   # lib.sh heat_to's launch
PREFILL_S, LAUNCH_OVERHEAD_S, HEATER_S = 1.5, 2.5, 4.5   # bounds used only for the sampler's duration
EXIT_OTHERS, EXIT_STALL = 3, 4


def die_c(path):
    """minshire[0] of the last complete telemetry line in the file the running sampler writes, or None."""
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 6000))
            lines = f.read().decode(errors="ignore").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        if line.startswith("{"):
            try:
                return float(json.loads(line)["temp_c"]["minshire"][0])
            except (ValueError, KeyError, IndexError, TypeError):
                continue
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--root", default=os.getcwd(), help="tree root (block.sh passes V3_ROOT)")
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--burst", type=float, default=3.0)
    ap.add_argument("--gap", type=float, default=5.0)
    ap.add_argument("--only", default="")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--host-bin", default="build/enercat_v2/host/enercat_host")
    ap.add_argument("--hold-hot", type=float, default=None, help="heat before each configuration until minshire >= C")
    ap.add_argument("--hold-max", type=int, default=5)
    ap.add_argument("--hold-limit", type=int, default=None, help="heater launches allowed in the whole run (--smoke: 1)")
    ap.add_argument("--hold-after", type=float, default=5.8, help="s after the previous burst before the first heater launch")
    ap.add_argument("--heat-settle", type=float, default=1.5, help="extra s after the last heater launch before the prefill/gap")
    ap.add_argument("--heater", default=None, help="sparsity_host used as the heater (lib.sh HEATER)")
    ap.add_argument("--tel-live", default=None, help="the telemetry file the running sampler writes")
    ap.add_argument("--stall-s", type=float, default=6.0, help="stop the pass when --tel-live has not grown for this long")
    ap.add_argument("--no-yield", action="store_true", help="do not stop when lib.sh others_present finds someone")
    ap.add_argument("--lead", type=float, default=10.0, help="idle seconds before the first configuration")
    ap.add_argument("--dry", action="store_true", default=bool(os.environ.get("V3_DRY")))
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    os.chdir(a.root)
    sys.path.insert(0, os.path.join(a.root, "workloads", "enercat"))
    sys.dont_write_bytecode = True
    import run_catalogue as orig   # the configuration list, unchanged

    cfgs = orig.configs()
    if a.only:
        keep = a.only.split(",")
        empty = [k for k in keep if not any(c["cfg"].startswith(k) for c in cfgs)]
        if empty:
            raise SystemExit(f"--only prefixes that select nothing: {empty}")
        cfgs = [c for c in cfgs if any(c["cfg"].startswith(k) for k in keep)]
    per = a.gap + a.burst + LAUNCH_OVERHEAD_S
    est = a.lead + a.gap + 3 + a.passes * sum(per + (PREFILL_S if c.get("prefill") else 0) for c in cfgs)
    if a.hold_hot is not None:
        est += a.passes * len(cfgs) * (a.hold_after + a.hold_max * HEATER_S + a.heat_settle)
    if a.list:
        print(json.dumps({"n": len(cfgs), "prefill": sum(1 for c in cfgs if c.get("prefill")), "max_s": int(est) + 1,
                          "cfgs": [c["cfg"] for c in cfgs]}))
        return
    if a.hold_hot is not None and not (a.heater and a.tel_live):
        raise SystemExit("--hold-hot needs --heater and --tel-live")
    H = a.host_bin
    ENV = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")

    def dev(cmd, **kw):
        """One device process, at most 10 s (lib.sh hold10)."""
        full = ["timeout", "10"] + cmd
        if a.dry:
            print("DRY hold10: " + " ".join(cmd), file=sys.stderr, flush=True)
            return subprocess.CompletedProcess(full, 0, "", "")
        return subprocess.run(full, env=ENV, stdin=subprocess.DEVNULL, capture_output=True, text=True, **kw)

    def sleep(s):
        if a.dry:
            print(f"DRY sleep {s:.1f}", file=sys.stderr, flush=True)
        elif s > 0:
            time.sleep(s)

    def others_present():
        """lib.sh's own others_present (another user logged in, or another user's device process); no device access."""
        if a.dry or a.no_yield:
            return False
        r = subprocess.run(["bash", "-c", ". tools/claims-v3/lib.sh && others_present"], stdin=subprocess.DEVNULL,
                           capture_output=True, text=True)
        if r.returncode == 0:
            print(f"others present: {r.stdout.strip()[-300:]}", file=log, flush=True)
        return r.returncode == 0

    tel_seen = [None, None]   # [size, time it last grew]

    def sampler_stalled():
        if a.dry or not a.tel_live:
            return False
        try:
            size = os.path.getsize(a.tel_live)
        except OSError:
            size = -1
        now = time.time()
        if tel_seen[0] is None or size > tel_seen[0]:
            tel_seen[0], tel_seen[1] = size, now
            return False
        return now - tel_seen[1] > a.stall_s

    os.makedirs(a.out, exist_ok=True)
    host = socket.gethostname()
    json.dump({"host": host, "host_bin": H, "args": vars(a), "cfgs": cfgs}, open(os.path.join(a.out, "configs.json"), "w"), indent=1)
    runs = open(os.path.join(a.out, "runs.jsonl"), "a")
    marks = open(os.path.join(a.out, "marks.jsonl"), "a")
    log = open(os.path.join(a.out, "run.log"), "a")

    def mark(kind, cfg, t0, t1, p, **extra):
        marks.write(json.dumps({"kind": kind, "cfg": cfg, "pass": p, "t_start_ms": int(t0 * 1000), "t_end_ms": int(t1 * 1000), **extra}) + "\n")
        marks.flush()

    print(f"{host}: {len(cfgs)} configurations x {a.passes} passes, at most {est / 60:.0f} min; host {H}"
          + (f"; hold {a.hold_hot:g} C" if a.hold_hot is not None else ""), file=log, flush=True)
    sleep(a.lead)
    last_hi = 0.0   # no burst yet: the first heater launch needs no wait
    heats_total = 0
    for p in range(a.passes):
        order = list(range(len(cfgs)))
        random.Random(a.seed + p).shuffle(order)
        for i in order:
            c = cfgs[i]
            if others_present():
                print(f"pass {p} {c['cfg']}: another user or device process on the card: stopping the pass", file=log, flush=True)
                sys.exit(EXIT_OTHERS)
            if sampler_stalled():
                print(f"pass {p} {c['cfg']}: {a.tel_live} has not grown for {a.stall_s:g} s (sampler gone): stopping the pass",
                      file=log, flush=True)
                sys.exit(EXIT_STALL)
            t_now = None if a.dry else die_c(a.tel_live) if a.tel_live else None
            heats = 0
            if a.hold_hot is not None and (a.hold_limit is None or heats_total < a.hold_limit):
                if a.dry:
                    print(f"DRY hold-hot {a.hold_hot:g}: first heater launch >= {a.hold_after:g} s after the previous burst, "
                          f"then up to {a.hold_max} launches until minshire >= {a.hold_hot:g}", file=sys.stderr, flush=True)
                    dev([a.heater] + HEATER_ARGS)
                    heats = 1
                    heats_total += 1
                    sleep(a.heat_settle)
                elif t_now is None:
                    print(f"pass {p} {c['cfg']}: no telemetry, no hold", file=log, flush=True)
                else:
                    while heats < a.hold_max and (a.hold_limit is None or heats_total < a.hold_limit):
                        t = die_c(a.tel_live)
                        if t is not None and t >= a.hold_hot:
                            break
                        if heats == 0:
                            sleep(last_hi + a.hold_after - time.time())
                        h0 = time.time()
                        r = dev([a.heater] + HEATER_ARGS)
                        mark("heater", c["cfg"], h0, time.time(), p, die_c=t, rc=r.returncode)
                        heats += 1
                        heats_total += 1
                        sleep(0.3)   # let the 10 Hz sampler write a line from after the launch before the next read
                    if heats:
                        sleep(a.heat_settle)   # next burst's idle window starts >= 2.3 s after the heater (see 4.)
            t_pre = None if a.dry else die_c(a.tel_live) if a.tel_live else None
            if c.get("prefill"):
                f0 = time.time()
                dev([H, "--pattern", "tstore", "--operands", c["prefill"], "--slice-bytes", "32K", "--scp", "--seconds", "0.3",
                     "--window", "60000000"])
                mark("prefill", c["cfg"], f0, time.time(), p)
            sleep(a.gap)
            r = dev([H] + c["args"] + ["--seconds", str(a.burst), "--window", "240000000"])
            n = 0
            for line in r.stdout.splitlines():
                if line.startswith("ENERCAT {"):
                    runs.write(json.dumps({"host": host, "pass": p, "cfg": c["cfg"], **json.loads(line[8:])}) + "\n")
                    n += 1
            runs.flush()
            last_hi = time.time()
            print(f"pass {p} {c['cfg']}: {n} launches" + (f" (die {t_now:g} -> {t_pre:g} C, {heats} heater)" if t_pre is not None and t_now is not None else "")
                  + ("" if n or a.dry else f" rc={r.returncode} {r.stderr[-200:]!r}"), file=log, flush=True)
    sleep(a.gap + 3)
    print("done", file=log, flush=True)


if __name__ == "__main__":
    main()
