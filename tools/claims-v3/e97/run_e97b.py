#!/usr/bin/env python3
"""E97 Part B runner (Q132): measured steady states on the local card (aifoundry3 card 0, 600 MHz pinned; nothing set).

The plan is frozen in E97.md: rest R0 sets the starting idle; hold H1 (int8 full) for 30 minutes; then, by the time left to the
deadline, H2 (fp32 ones) either after its own rest or chained on H1 for 15 minutes, or not at all; a rest; hold H3 (fp32 random);
a last rest. A hold is back-to-back launches of `sparsity_host --test fma` on 1,024 minions, each at most 6.8 s under `timeout 10`,
E89's chain. A rest launches nothing. The sampler (tools/claims-v3/e89/pvt_sample.py, E89's) runs for the whole pass, so the
idle before and after each hold, and the cooling curve between, are on the same reading as the hold.

The lab's stop is kept as E89 has it: no launch starts at a firmware die reading of 78 C or more. Reaching it in a hold's
"natural" phase moves the hold to its "reduced" phase once the reading is back at 75 C: 3.5 s launches, one every 7 s. Reaching it again
ends the hold. A reading of 82 C, a telemetry stall or another user on the card ends the pass, as in E89. The clock leaving 600 MHz or
three failed launches in a row ends the hold and any later one (a last rest still runs).

    python3 tools/claims-v3/e97/run_e97b.py <out-dir> --root <tree> --tel-live <sampler file> --sparsity <bin>
        [--pass-no 9720] [--card aifoundry3] [--deadline '2026-11-01 07:13 PST' | --deadline-epoch N] [--smoke] [--dry] [--list]
    exit 0 done; 3 another user on this card; 4 the sampler stopped writing; 5 no telemetry; 6 the die reached 82 C;
         8 STOP file; 9 a tile failed its sha256

Only standard library: the runner works without numpy. Nothing here opens the management node; nothing is set.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e97_common as c  # noqa: E402

EXIT_OTHERS, EXIT_STALL, EXIT_NOTEL, EXIT_HOT, EXIT_STOP, EXIT_TILES = 3, 4, 5, 6, 8, 9
G_TS, H_TS, CAL5 = 57400, 249400, 4096


def code_to_c(n):
    """the firmware's conversion in floating point (E89 amendment A1)"""
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


def die_mean(rec):
    pv = rec.get("pvt") or {}
    cs = pv.get("c") or []
    if pv.get("st") == 0 and len(cs) == 34 and not pv.get("f"):
        return sum(code_to_c(x) for x in cs) / 34.0
    return None


class Finished(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


class RealCard:
    def __init__(self, a, env):
        self.a = a
        self.env = env
        import run_e89 as base          # last_sample, others_on_card: E89's, unchanged
        self.base = base
        d = os.environ.get("ET_DEVICES")
        self.dev = int(d) if d not in (None, "") else None

    def now(self):
        return time.time()

    def sleep(self, s):
        time.sleep(s)

    def latest(self):
        return self.base.last_sample(self.a.tel_live)

    def tail(self, seconds):
        """the sampler's lines of about the last `seconds` (a line is under 1 kB, ten a second)"""
        try:
            with open(self.a.tel_live, "rb") as f:
                f.seek(0, 2)
                f.seek(max(0, f.tell() - int(seconds * 10 * 1000 + 4000)))
                lines = f.read().decode(errors="ignore").splitlines()
        except OSError:
            return []
        out = []
        for line in lines:
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
        return out

    def launch(self, cmd):
        r = subprocess.run(["timeout", "10"] + cmd, env=self.env, stdin=subprocess.DEVNULL, capture_output=True, text=True)
        recs = []
        for line in r.stdout.splitlines():
            if line.startswith("SPARSITY {"):
                recs.append(json.loads(line[len("SPARSITY "):]))
        return r.returncode, recs, r.stderr

    def others(self):
        return self.base.others_on_card(self.dev)


class DryCard:
    """V3_DRY: no device, no sampler. A virtual clock that a launch or a sleep moves, a die that always reads the same, so the plan's
    decisions run through in moments and every launch is printed, like E89's dry pass."""

    def __init__(self, t0=None):
        self.t = t0 if t0 is not None else time.time()

    def now(self):
        return self.t

    def sleep(self, s):
        self.t += s

    def latest(self):
        return {"t_ms": int(self.t * 1000), "temp_c": {"minshire": [51, 40, 70], "pmic": 51}, "board_w": 24.0,
                "mhz": {"minion": 600}}

    def tail(self, seconds):
        recs = []
        for i in range(int(seconds * 5)):
            recs.append({"t_ms": int((self.t - i * 0.2 - 0.01) * 1000), "board_w": 24.0, "pvt": {"st": 0, "f": 0, "c": [1950] * 34}})
        return recs

    def launch(self, cmd):
        print("DRY hold10: " + " ".join(cmd), file=sys.stderr, flush=True)
        self.t += float(cmd[cmd.index("--seconds") + 1]) + 0.32
        return 0, [], ""

    def others(self):
        return []


def run_plan(a, card, out, items):
    """The frozen plan. Returns normally when done; raises Finished(code, msg) on a stop that ends the pass."""
    os.makedirs(os.path.join(out, "tiles"), exist_ok=True)
    stop_file = os.path.join(out, "STOP")
    runs = open(os.path.join(out, "runs.jsonl"), "a")
    marks = open(os.path.join(out, "marks.jsonl"), "a")
    log = open(os.path.join(out, "run.log"), "a")
    dumped = set()
    st = {"abort_holds": False, "last_check": 0.0, "off_clock": 0}

    def say(msg):
        line = f"{time.strftime('%H:%M:%S', time.localtime(card.now()))} [{a.card}] {msg}"
        print(line, file=log, flush=True)
        print(line, flush=True)

    def mark(**kw):
        marks.write(json.dumps(kw) + "\n")
        marks.flush()

    def ms():
        return int(card.now() * 1000)

    def left():
        return a.deadline_epoch - card.now()

    def stop(code, msg):
        say(f"STOP ({code}): {msg}")
        try:
            open(stop_file, "a").write(msg + "\n")
        except OSError:
            pass
        raise Finished(code, msg)

    def reading():
        """the newest sample; E89's guards: a stale or absent sampler ends the pass"""
        s = card.latest()
        if s is None:
            stop(EXIT_NOTEL, "no telemetry line")
        age = card.now() - s["t_ms"] / 1000.0
        if age > a.stale_s:
            stop(EXIT_STALL, f"the newest telemetry line is {age:.1f} s old: the sampler is gone")
        try:
            t = float(s["temp_c"]["minshire"][0])
            pmic = float(s["temp_c"].get("pmic", 0))
        except (KeyError, IndexError, TypeError, ValueError):
            stop(EXIT_NOTEL, "telemetry line without temp_c.minshire")
        if t >= a.hard_c or pmic >= a.hard_c + 10:
            stop(EXIT_HOT, f"die reading {t} C (PMIC field {pmic} C) >= the hard stop {a.hard_c} C")
        mhz = (s.get("mhz") or {}).get("minion")
        st["off_clock"] = st["off_clock"] + 1 if (mhz is not None and mhz != 600) else 0
        return {"die": t, "pmic": pmic, "w": float(s.get("board_w", 0.0)), "mhz": mhz,
                "hot": t >= a.max_c or pmic >= a.max_c + 10 or float(s.get("board_w", 0.0)) >= a.max_board_w}

    def check(where):
        if card.now() - st["last_check"] < a.check_every_s:
            return
        st["last_check"] = card.now()
        o = card.others()
        if o:
            stop(EXIT_OTHERS, f"{where}: another user on this card: {o}")
        if os.path.exists(stop_file):
            stop(EXIT_STOP, f"{where}: {stop_file} exists")

    def wait_until(t_end, where="wait"):
        while True:
            now = card.now()
            if now >= t_end:
                return
            reading()
            check(where)
            card.sleep(min(0.2, t_end - now))

    def recent_mean(ago_s, win_s):
        """mean of the 34-sensor mean over [now - ago_s - win_s, now - ago_s); None if fewer than half the samples are there"""
        now = card.now()
        vals = []
        for r in card.tail(ago_s + win_s + 5):
            tt = r.get("t_ms", 0) / 1000.0
            if now - ago_s - win_s <= tt < now - ago_s:
                v = die_mean(r)
                if v is not None:
                    vals.append(v)
        need = 0.5 * win_s * a.min_rate_hz
        return (sum(vals) / len(vals)) if len(vals) >= need and vals else None

    def rest(name, mode, min_s, max_s, level=None, extra_s=0.0):
        """Idle, the sampler reading. mode "slope": ends when the mean of the last 60 s is at most SLOPE below the mean of the 60 s
        ending 5 minutes ago. mode "level": ends when the mean of the last 60 s is at most `level`. Never before min_s, never after
        max_s. Returns the mean of the last IDLE_WINDOW_S."""
        t0 = card.now()
        max_s = max(min_s, max_s) if max_s >= 0 else 0.0
        max_s = min(max_s, max(0.0, left()))
        min_s = min(min_s, max_s)
        mark(kind="rest_start", name=name, mode=mode, t_start_ms=int(t0 * 1000), min_s=min_s, max_s=max_s, level=level)
        say(f"rest {name}: {mode}, {min_s:.0f}-{max_s:.0f} s" + (f", level {level:.3f} C" if level is not None else ""))
        why = "cap"
        next_eval = t0 + min_s
        while True:
            now = card.now()
            if now - t0 >= max_s:
                why = "cap" if left() > 1.0 else "deadline"
                break
            reading()
            check(f"rest {name}")
            if now >= next_eval:
                next_eval = now + a.eval_every_s
                t_now = recent_mean(0.0, 60.0)
                if mode == "slope":
                    t_then = recent_mean(300.0, 60.0)
                    if t_now is not None and t_then is not None and t_then - t_now <= a.slope_c:
                        why = "slope"
                        break
                elif t_now is not None and level is not None and t_now <= level:
                    why = "level"
                    break
            card.sleep(min(1.0, max(0.05, t0 + max_s - now)))
        if why in ("level", "slope") and extra_s > 0:
            t_x = min(card.now() + extra_s, card.now() + max(0.0, left()))
            wait_until(t_x, f"rest {name}")
        idle = recent_mean(0.0, c.IDLE_WINDOW_S)
        t1 = card.now()
        mark(kind="rest", name=name, mode=mode, why_end=why, t_start_ms=int(t0 * 1000), t_end_ms=int(t1 * 1000), level=level,
             idle_c=idle)
        say(f"rest {name} ends ({why}) after {t1 - t0:.0f} s: 34-sensor mean {idle if idle is None else round(idle, 3)} C")
        return idle

    def launch(item, secs, hold_name, phase):
        it = items[item]
        cmd = [a.sparsity, "--test", "fma", "--type", it["type"], "--pattern", "none",
               "--values", "file:" + os.path.join(a.root, it["tile"]), "--shires", "0xffffffff", "--per-shire", "32",
               "--seconds", f"{secs:.2f}", "--seed", str(a.pass_no + 1), "--stop-file", stop_file]
        if item not in dumped:
            cmd += ["--dump-tiles", os.path.join(out, "tiles", f"{item}.p{a.pass_no}.bin")]
            dumped.add(item)
        t0 = card.now()
        rc, recs, err = card.launch(cmd)
        t1 = card.now()
        for rec in recs:
            runs.write(json.dumps({"card": a.card, "pass": a.pass_no, "block": hold_name, "half": phase, "role": "H", "item": item,
                                   "type": it["type"], "kind_name": it["kind"], "secs": round(secs, 2), **rec}) + "\n")
        runs.flush()
        mark(kind="launch", block=hold_name, half=phase, role="H", item=item, secs=round(secs, 2),
             t_start_ms=int(t0 * 1000), t_end_ms=int(t1 * 1000), rc=rc, records=len(recs))
        if not recs and not a.dry:
            say(f"{hold_name} {phase} {item}: no launch record (rc {rc}) {err[-200:]!r}")
        return len(recs)

    def hold(name, item, dur_s, chained=False):
        """Back-to-back launches of `item` for dur_s, with the lab's stop."""
        t0 = card.now()
        t_end = t0 + dur_s
        mark(kind="hold_start", name=name, item=item, t_start_ms=int(t0 * 1000), planned_s=dur_s, chained=chained)
        mark(kind="phase", hold=name, phase="natural", t_ms=int(t0 * 1000))
        say(f"hold {name}: {item} for {dur_s:.0f} s" + (" (chained)" if chained else ""))
        phase, why, nl, fails = "natural", "time", 0, 0
        forced = a.smoke
        while True:
            rem = t_end - card.now() - a.overhead_s
            if rem < a.min_launch_s:
                break
            check(f"hold {name}")
            s = reading()
            if st["off_clock"] >= 5:
                why = "clock"
                st["abort_holds"] = True
                mark(kind="clock_off", hold=name, t_ms=ms(), mhz=s["mhz"], die_c=s["die"])
                say(f"hold {name}: the clock read {s['mhz']} MHz in 5 samples: this hold and any later one end")
                break
            smoke_stop = forced and card.now() - t0 >= a.smoke_stop_after_s
            if s["hot"] or smoke_stop:
                mark(kind="stop", hold=name, phase=phase, t_ms=ms(), die_c=s["die"], board_w=s["w"], smoke=bool(smoke_stop))
                say(f"hold {name}: the stop at {s['die']:g} C, {s['w']:.1f} W, in phase {phase}")
                if smoke_stop:
                    forced = False
                if phase == "natural":
                    while reading()["die"] > a.resume_c and card.now() < t_end:
                        check(f"hold {name}")
                        card.sleep(0.5)
                    phase = "reduced"
                    mark(kind="phase", hold=name, phase="reduced", t_ms=ms(), die_c=reading()["die"])
                    continue
                why = "stop"
                break
            if phase == "natural":
                n = launch(item, min(a.launch_s, rem), name, phase)
            else:
                tl = card.now()
                n = launch(item, min(a.reduced_launch_s, rem), name, phase)
                wait_until(min(tl + a.reduced_period_s, t_end), f"hold {name}")
            nl += 1
            fails = 0 if (n or a.dry) else fails + 1
            if fails >= 3:
                why = "launches failed"
                st["abort_holds"] = True
                say(f"hold {name}: three launches failed in a row: this hold and any later one end")
                break
        if why == "time":
            wait_until(t_end, f"hold {name}")
        t1 = card.now()
        mark(kind="hold", name=name, item=item, chained=chained, t_start_ms=int(t0 * 1000), t_end_ms=int(t1 * 1000),
             planned_s=dur_s, why_end=why, launches=nl, last_phase=phase, die_c=reading()["die"])
        say(f"hold {name} ends ({why}) after {t1 - t0:.0f} s, {nl} launches, die {reading()['die']:g} C")

    def decide(choice, **kw):
        mark(kind="decision", t_ms=ms(), left_s=round(left(), 1), choice=choice, **kw)
        say(f"decision: {choice}; {left() / 60:.1f} min left to the deadline")

    say(f"E97 Part B pass {a.pass_no}: deadline {time.strftime('%F %T %Z', time.localtime(a.deadline_epoch))}, "
        f"{left() / 60:.1f} min left; stop {a.max_c:g} C, resume {a.resume_c:g} C, hard {a.hard_c:g} C; tiles verified")
    check("start")
    if a.smoke:
        rest("R0", "slope", a.smoke_rest_s, a.smoke_rest_s)
        hold("H1", c.HOLD_ITEMS["H1"], a.smoke_hold_s)
        rest("R1", "level", a.smoke_rest_s, a.smoke_rest_s, level=None)
        say("done")
        return
    if left() < c.REST_MIN_S + c.H3_MIN_S + c.R3_MIN_S:
        decide("no hold fits")
        say("done")
        return
    # R0: the starting idle
    t_i = rest("R0", "slope", c.REST_MIN_S, min(c.R0_MAX_S, left() - c.HOLD_S - c.R3_MIN_S))
    if t_i is None:
        t_i = recent_mean(0.0, 60.0)
    level = None if t_i is None else t_i + c.RISE_LEVEL_C
    mark(kind="starting_idle", t_ms=ms(), t_i=t_i, level=level)
    # H1: the priority hold (item 8's own kind)
    d1 = min(c.HOLD_S, left() - c.R3_MIN_S)
    if d1 < c.H3_MIN_S:
        decide("no hold fits after R0")
        say("done")
        return
    hold("H1", c.HOLD_ITEMS["H1"], d1)
    if st["abort_holds"]:
        decide("no later hold: the last hold ended on a card condition")
        rest("R1", "level", c.REST_MIN_S, left(), level=level, extra_s=300.0)
        say("done")
        return
    # the rest of the plan, by the time left
    ll = left()
    if ll >= c.LEFT_FULL_S:
        decide("full: R1, H2 for 30 min, R2, H3, R3")
        rest("R1", "level", c.REST_MIN_S, min(c.R_MAX_S, left() - c.HOLD_S - 1200.0 - c.HOLD_S - c.R3_MIN_S), level=level)
        hold("H2", c.HOLD_ITEMS["H2"], c.HOLD_S)
        rest_name = "R2"
    elif ll >= c.LEFT_CHAIN_S:
        decide("chain: H2 for 15 min on H1, R1, H3, R3")
        hold("H2", c.HOLD_ITEMS["H2"], c.CHAIN_S, chained=True)
        rest_name = "R1"
    elif ll >= c.LEFT_H3_S:
        decide("no H2: R1, H3, R3")
        rest_name = "R1"
    else:
        decide("no H2, no H3: a last rest")
        rest("R1", "level", min(c.REST_MIN_S, left()), left(), level=level, extra_s=300.0)
        say("done")
        return
    if st["abort_holds"]:
        decide("no later hold: the last hold ended on a card condition")
        rest(rest_name, "level", c.REST_MIN_S, left(), level=level, extra_s=300.0)
        say("done")
        return
    rest(rest_name, "level", c.REST_MIN_S, min(c.R_MAX_S, max(1200.0, left() - c.HOLD_S - c.R3_MIN_S)), level=level)
    d3 = min(c.HOLD_S, left() - c.R3_MIN_S)
    last = "R3" if rest_name == "R2" else "R2"
    if d3 < c.H3_MIN_S:
        decide("no H3: too little time after the rest")
        rest(last, "level", min(c.REST_MIN_S, left()), left(), level=level, extra_s=300.0)
        say("done")
        return
    hold("H3", c.HOLD_ITEMS["H3"], d3)
    rest(last, "level", min(c.REST_MIN_S, left()), left(), level=level, extra_s=300.0)
    say("done")


def parse_args(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--root", required=True)
    ap.add_argument("--tel-live", default=None)
    ap.add_argument("--sparsity", default="build/sparsity/host/sparsity_host")
    ap.add_argument("--pass-no", type=int, default=c.HOLDS_PASS)
    ap.add_argument("--card", default="aifoundry3")
    ap.add_argument("--deadline", default=c.DEADLINE)
    ap.add_argument("--deadline-epoch", type=float, default=None)
    ap.add_argument("--launch-s", type=float, default=c.LAUNCH_S)
    ap.add_argument("--reduced-launch-s", type=float, default=c.REDUCED_LAUNCH_S)
    ap.add_argument("--reduced-period-s", type=float, default=c.REDUCED_PERIOD_S)
    ap.add_argument("--overhead-s", type=float, default=0.75, help="E89's: a launch's start-up and exit")
    ap.add_argument("--min-launch-s", type=float, default=1.0)
    ap.add_argument("--max-c", type=float, default=c.MAX_C)
    ap.add_argument("--resume-c", type=float, default=c.RESUME_C)
    ap.add_argument("--hard-c", type=float, default=c.HARD_C)
    ap.add_argument("--max-board-w", type=float, default=c.MAX_BOARD_W)
    ap.add_argument("--slope-c", type=float, default=c.SLOPE_C_PER_5MIN)
    ap.add_argument("--stale-s", type=float, default=3.0)
    ap.add_argument("--check-every-s", type=float, default=60.0)
    ap.add_argument("--eval-every-s", type=float, default=10.0)
    ap.add_argument("--min-rate-hz", type=float, default=5.0)
    ap.add_argument("--smoke", action="store_true", help="R0 20 s, H1 25 s with a forced stop at 8 s, R1 20 s")
    ap.add_argument("--smoke-rest-s", type=float, default=20.0)
    ap.add_argument("--smoke-hold-s", type=float, default=25.0)
    ap.add_argument("--smoke-stop-after-s", type=float, default=8.0)
    ap.add_argument("--dry", action="store_true", default=bool(os.environ.get("V3_DRY")))
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)
    if a.deadline_epoch is None:
        r = subprocess.run(["date", "-d", a.deadline, "+%s"], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            a.deadline_epoch = float(r.stdout.strip())
        else:                      # a Mac's date has no -d: the desk's dry run; the box's date does
            a.deadline_epoch = time.time() + 3 * 3600
    return a


def main():
    a = parse_args()
    bad = c.check_reused()
    if bad:
        raise SystemExit("E97: a reused file differs from the freeze: " + "; ".join(bad))
    run_e89 = c.install_runner()         # also installs E86's load_items on e78_common
    ec = run_e89.ec
    os.chdir(a.root)
    items = {it["name"]: it for it in ec.load_items()}
    used = sorted(set(c.HOLD_ITEMS.values()))
    bad = ec.verify_tiles(a.root, [items[n] for n in used])
    left = a.deadline_epoch - time.time()
    if a.list:
        print(json.dumps({"holds": c.HOLD_ITEMS, "items": used, "left_s": int(left), "max_s": int(max(120, left) + 300),
                          "tile_problems": bad}))
        sys.exit(EXIT_TILES if bad else 0)
    if bad:
        print("tiles failed their kinds.json sha256: " + "; ".join(bad), file=sys.stderr)
        sys.exit(EXIT_TILES)
    env = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
    os.makedirs(a.out, exist_ok=True)
    json.dump({"card": a.card, "args": vars(a), "holds": c.HOLD_ITEMS, "items": [items[n] for n in used],
               "et_devices": os.environ.get("ET_DEVICES"), "experiment": "E97-B"},
              open(os.path.join(a.out, "configs.json"), "w"), indent=1)
    card = DryCard() if a.dry else RealCard(a, env)
    try:
        run_plan(a, card, a.out, items)
    except Finished as e:
        sys.exit(e.code)


if __name__ == "__main__":
    main()
