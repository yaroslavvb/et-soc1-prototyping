#!/usr/bin/env python3
"""E144 runner (Q138): Q138(t)'s frozen heat-over-minutes holds on aifoundry3 card 0 (600 MHz pinned; nothing set).

A port of tools/claims-v3/e97/run_e97b.py (E97 Part B; imported, unchanged, for its card classes and readers) with these changes,
each marked E144:
  1. the plan is Q138(t)'s (docs/reports/data/2026-11-02-q138t-heat-model/predictions-e144.json with amendment A1, c2f9920d):
     --design subset (the registered subset: R0 8 min, H_H 13, R1 9, H_L 13, R2 2; 44.9 card-minutes) or --design full
     (R0 10, H_L 13, R1 9, H_M 13, R2 9, H_H 13, R3 9; 75.9). Rests are fixed lengths (the frozen minutes): no slope or level rule.
  2. H_H runs duty-cycled from its first launch (A1.1): --seconds 3.20 once every 7.56 s, start to start. H_H' (--seconds 2.60
     every 7.98 s) runs instead when the rest die before it (34-sensor mean, last 120 s) is above 51.5 C and at most 53.0 C; above
     53.0 C no H_H runs (its 13 minutes are a rest). H_L and H_M run E97's natural chain (back-to-back 6.8 s launches).
  3. the stops are Q138(t)'s (rules.stops): no launch starts at a firmware die reading >= 70 C; a hold ends at any sample >= 72 C
     or a board reading >= 65 W; the pass ends at >= 74 C. A watcher thread reads every new live sampler line (10 Hz) while
     launches run and writes the hold's stop file, which sparsity_host's --stop-file reads before each dispatch, so a
     hold-ending sample ends the launch in flight. The 34-sensor mean is held to the 72 and 74 C lines too (stricter, never looser).
  4. the rest die is recorded before each hold: a "rest_die" mark with the 34-sensor mean and the firmware reading, last 120 s.
  5. --smoke: R0 15 s, H_H 16 s duty-cycled, R1 10 s, H_L 8 s, R2 5 s. --stoptest (after the smoke plan when both are given): each
     stop path on live samples, with a line the idle card already meets: the launch gate at 1 C (no launch), the hold's die line
     at 1 C and board line at 1 W (the hold ends, no launch), a board line 4 W over the idle (the launch in flight ends early) and
     the session line at 1 C (the pass ends with exit 6, which --stoptest then reports as passed and exits 0).
marks.jsonl and runs.jsonl keep run_e97b.py's formats (amendment A1: score_e144.py reads them).

    python3 tools/claims-v3/e144/run_e144.py <out-dir> --root <tree> --tel-live <sampler file> --sparsity <bin>
        [--pass-no 14420] [--design subset|full] [--deadline-epoch N] [--smoke] [--stoptest] [--dry] [--list]
    exit 0 done; 3 another user on this card; 4 the sampler stopped writing; 5 no telemetry; 6 the session stop (74 C);
         8 STOP file; 9 a tile failed its sha256
Nothing here opens the management node (the sampler, E89's pvt_sample.py, does); nothing is set.
"""
import argparse
import json
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E97_DIR = os.path.join(os.path.dirname(HERE), "e97")
sys.path.insert(0, E97_DIR)
import e97_common as c  # noqa: E402
import run_e97b as b    # noqa: E402  E97's runner: RealCard, DryCard, die_mean, Finished, unchanged

EXIT_OTHERS, EXIT_STALL, EXIT_NOTEL, EXIT_HOT, EXIT_STOP, EXIT_TILES = 3, 4, 5, 6, 8, 9
ITEMS = {"H_L": "int8.neg_ones", "H_M": "int8.full", "H_H": "fp32.randn", "H_H'": "fp32.randn"}
DUTY = {"H_H": (3.20, 7.56), "H_H'": (2.60, 7.98)}                      # A1.1: --seconds, period start to start
WARM_LO, WARM_HI = 51.5, 53.0                                           # H_H_warm_room's rule
DESIGNS = {
    "subset": [("rest", "R0", 480.0), ("hold", "H_H", 780.0), ("rest", "R1", 540.0), ("hold", "H_L", 780.0), ("rest", "R2", 120.0)],
    "full": [("rest", "R0", 600.0), ("hold", "H_L", 780.0), ("rest", "R1", 540.0), ("hold", "H_M", 780.0), ("rest", "R2", 540.0),
             ("hold", "H_H", 780.0), ("rest", "R3", 540.0)],
    "smoke": [("rest", "R0", 15.0), ("hold", "H_H", 16.0), ("rest", "R1", 10.0), ("hold", "H_L", 8.0), ("rest", "R2", 5.0)],
}


def run_plan(a, card, out, items):
    """The frozen plan. Returns normally when done; raises b.Finished(code, msg) on a stop that ends the pass."""
    os.makedirs(os.path.join(out, "tiles"), exist_ok=True)
    stop_file = os.path.join(out, "STOP")
    hold_stop = os.path.join(out, "HOLDSTOP")
    runs = open(os.path.join(out, "runs.jsonl"), "a")
    marks = open(os.path.join(out, "marks.jsonl"), "a")
    log = open(os.path.join(out, "run.log"), "a")
    lk, wl = threading.Lock(), threading.Lock()
    dumped = set()
    st = {"abort_holds": False, "last_check": 0.0, "off_clock": 0, "hold": None, "hold_stop": None, "session_hot": None,
          "done": False}

    def say(msg):
        line = f"{time.strftime('%H:%M:%S', time.localtime(card.now()))} [{a.card}] {msg}"
        with lk:
            print(line, file=log, flush=True)
            print(line, flush=True)

    def mark(**kw):
        with lk:
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
        raise b.Finished(code, msg)

    def values(s):
        die = float(s["temp_c"]["minshire"][0])
        pmic = float(s["temp_c"].get("pmic", 0))
        return die, pmic, float(s.get("board_w", 0.0)), b.die_mean(s)

    def watch_once(s, where):
        """E144 change 3: the hold's and the session's lines on one live sample. True if a line fired."""
        try:
            die, pmic, w, m34 = values(s)
        except (KeyError, IndexError, TypeError, ValueError):
            return False
        hot = max(die, m34 if m34 is not None else -1e9)
        with wl:
            if hot >= a.session_c and st["session_hot"] is None:
                st["session_hot"] = {"rule": "session", "line_c": a.session_c, "t_sample_ms": s.get("t_ms"), "t_seen_ms": ms(),
                                     "die_c": die, "mean34_c": m34, "board_w": w, "where": where}
                for f in (hold_stop, stop_file):
                    try:
                        open(f, "a").write(json.dumps(st["session_hot"]) + "\n")
                    except OSError:
                        pass
                fired = dict(st["session_hot"])
            elif st["hold"] is not None and st["hold_stop"] is None and (hot >= a.hold_c or w >= a.hold_w):
                rule = "die" if hot >= a.hold_c else "board"
                st["hold_stop"] = {"rule": rule, "line": a.hold_c if rule == "die" else a.hold_w, "hold": st["hold"],
                                   "t_sample_ms": s.get("t_ms"), "t_seen_ms": ms(), "die_c": die, "mean34_c": m34, "board_w": w,
                                   "where": where}
                try:
                    open(hold_stop, "a").write(json.dumps(st["hold_stop"]) + "\n")
                except OSError:
                    pass
                fired = dict(st["hold_stop"])
            else:
                return False
        mark(kind="watch", **fired)
        say(f"watch ({where}): {fired['rule']} line fired at die {die:g} C (34-sensor mean "
            f"{'-' if m34 is None else round(m34, 2)}), board {w:.2f} W")
        return True

    def watcher():
        last = None
        while not st["done"]:
            try:
                s = card.latest()
            except Exception:  # noqa: BLE001 - the loop's own reading() reports a sampler fault
                s = None
            if s is not None and s.get("t_ms") != last:
                last = s.get("t_ms")
                watch_once(s, "watcher")
            time.sleep(a.watch_every_s)

    def reading():
        """the newest sample; E97's guards (a stale or absent sampler ends the pass), then E144's lines"""
        s = card.latest()
        if s is None:
            stop(EXIT_NOTEL, "no telemetry line")
        age = card.now() - s["t_ms"] / 1000.0
        if age > a.stale_s:
            stop(EXIT_STALL, f"the newest telemetry line is {age:.1f} s old: the sampler is gone")
        try:
            die, pmic, w, m34 = values(s)
        except (KeyError, IndexError, TypeError, ValueError):
            stop(EXIT_NOTEL, "telemetry line without temp_c.minshire")
        watch_once(s, "loop")
        if st["session_hot"] is not None:
            stop(EXIT_HOT, f"the session line {a.session_c:g} C: {st['session_hot']}")
        if pmic >= a.session_c + 10:
            stop(EXIT_HOT, f"PMIC field {pmic} C >= {a.session_c + 10:g} C")
        mhz = (s.get("mhz") or {}).get("minion")
        st["off_clock"] = st["off_clock"] + 1 if (mhz is not None and mhz != 600) else 0
        return {"die": die, "pmic": pmic, "w": w, "mhz": mhz, "m34": m34}

    def check(where):
        if card.now() - st["last_check"] < a.check_every_s:
            return
        st["last_check"] = card.now()
        o = card.others()
        if o:
            stop(EXIT_OTHERS, f"{where}: another user on this card: {o}")
        if os.path.exists(stop_file):
            stop(EXIT_STOP, f"{where}: {stop_file} exists")

    def wait_until(t_end, where="wait", brk=None):
        while True:
            now = card.now()
            if now >= t_end:
                return
            reading()
            check(where)
            if brk is not None and brk():
                return
            card.sleep(min(0.2, t_end - now))

    def recent(ago_s, win_s, fn):
        now = card.now()
        vals = []
        for r in card.tail(ago_s + win_s + 5):
            tt = r.get("t_ms", 0) / 1000.0
            if now - ago_s - win_s <= tt < now - ago_s:
                try:
                    v = fn(r)
                except (KeyError, IndexError, TypeError, ValueError):
                    v = None
                if v is not None:
                    vals.append(v)
        need = 0.5 * win_s * a.min_rate_hz
        return (sum(vals) / len(vals)) if len(vals) >= need and vals else None

    def mean34(ago_s, win_s):
        return recent(ago_s, win_s, b.die_mean)

    def firmware(ago_s, win_s):
        return recent(ago_s, win_s, lambda r: float(r["temp_c"]["minshire"][0]))

    def rest(name, dur_s):
        """E144 change 1: idle for the frozen minutes, the sampler reading"""
        t0 = card.now()
        dur = max(0.0, min(dur_s, left()))
        mark(kind="rest_start", name=name, mode="fixed", t_start_ms=int(t0 * 1000), min_s=dur, max_s=dur, level=None)
        say(f"rest {name}: {dur:.0f} s")
        wait_until(t0 + dur, f"rest {name}")
        idle = mean34(0.0, c.IDLE_WINDOW_S)
        t1 = card.now()
        mark(kind="rest", name=name, mode="fixed", why_end="time" if dur >= dur_s - 0.5 else "deadline", t_start_ms=int(t0 * 1000),
             t_end_ms=int(t1 * 1000), level=None, idle_c=idle)
        say(f"rest {name} ends after {t1 - t0:.0f} s: 34-sensor mean {idle if idle is None else round(idle, 3)} C")
        return idle

    def rest_die(hold_name):
        """E144 change 4"""
        m34, fw = mean34(0.0, 120.0), firmware(0.0, 120.0)
        mark(kind="rest_die", hold=hold_name, t_ms=ms(), window_s=120.0, mean34_c=m34, firmware_c=fw)
        say(f"rest die before {hold_name}: 34-sensor mean {m34 if m34 is None else round(m34, 3)} C, firmware "
            f"{fw if fw is None else round(fw, 2)} C (last 120 s)")
        return m34

    def launch(item, secs, hold_name, phase):
        it = items[item]
        cmd = [a.sparsity, "--test", "fma", "--type", it["type"], "--pattern", "none",
               "--values", "file:" + os.path.join(a.root, it["tile"]), "--shires", "0xffffffff", "--per-shire", "32",
               "--seconds", f"{secs:.2f}", "--seed", str(a.pass_no + 1), "--stop-file", hold_stop]     # E144 change 3
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

    def hold(name, item, dur_s, duty=None):
        """E144 changes 2 and 3: launches of `item` for dur_s, back to back (duty None) or duty-cycled from the first launch."""
        try:
            os.remove(hold_stop)
        except FileNotFoundError:
            pass
        st["hold_stop"] = None
        t0 = card.now()
        t_end = t0 + dur_s
        phase = "reduced" if duty else "natural"
        mark(kind="hold_start", name=name, item=item, t_start_ms=int(t0 * 1000), planned_s=dur_s, chained=False,
             launch_s=duty[0] if duty else a.launch_s, period_s=duty[1] if duty else None)
        mark(kind="phase", hold=name, phase=phase, t_ms=int(t0 * 1000))
        say(f"hold {name}: {item} for {dur_s:.0f} s, " + (f"{duty[0]:.2f} s every {duty[1]:.2f} s" if duty else "back to back"))
        st["hold"] = name
        why, nl, fails, gated = "time", 0, 0, 0
        stopped = lambda: st["hold_stop"] is not None or os.path.exists(hold_stop)  # noqa: E731
        while True:
            rem = t_end - card.now() - a.overhead_s
            if rem < a.min_launch_s:
                break
            check(f"hold {name}")
            s = reading()
            if stopped():
                why = "stop"
                mark(kind="stop", hold=name, phase=phase, t_ms=ms(), die_c=s["die"], board_w=s["w"], smoke=False,
                     rule=(st["hold_stop"] or {}).get("rule"))
                say(f"hold {name}: the hold's line fired ({(st['hold_stop'] or {}).get('rule')}): the hold ends")
                break
            if st["off_clock"] >= 5:
                why = "clock"
                st["abort_holds"] = True
                mark(kind="clock_off", hold=name, t_ms=ms(), mhz=s["mhz"], die_c=s["die"])
                say(f"hold {name}: the clock read {s['mhz']} MHz in 5 samples: this hold and any later one end")
                break
            if s["die"] >= a.gate_c:
                if gated == 0:
                    mark(kind="gate", hold=name, t_ms=ms(), die_c=s["die"], line_c=a.gate_c)
                    say(f"hold {name}: no launch at a firmware reading of {s['die']:g} C (>= {a.gate_c:g} C)")
                gated += 1
                card.sleep(0.5)
                continue
            tl = card.now()
            n = launch(item, min(duty[0] if duty else a.launch_s, rem), name, phase)
            if duty:
                wait_until(min(tl + duty[1], t_end), f"hold {name}", brk=stopped)
            nl += 1
            fails = 0 if (n or a.dry) else fails + 1
            if fails >= 3 and not stopped():
                why = "launches failed"
                st["abort_holds"] = True
                say(f"hold {name}: three launches failed in a row: this hold and any later one end")
                break
        if why == "time":
            wait_until(t_end, f"hold {name}")
        st["hold"] = None
        t1 = card.now()
        r = reading()
        mark(kind="hold", name=name, item=item, chained=False, t_start_ms=int(t0 * 1000), t_end_ms=int(t1 * 1000),
             planned_s=dur_s, why_end=why, launches=nl, last_phase=phase, die_c=r["die"], gated=gated, hold_stop=st["hold_stop"])
        say(f"hold {name} ends ({why}) after {t1 - t0:.0f} s, {nl} launches, die {r['die']:g} C")
        return why, nl

    def decide(choice, **kw):
        mark(kind="decision", t_ms=ms(), left_s=round(left(), 1), choice=choice, **kw)
        say(f"decision: {choice}; {left() / 60:.1f} min left to the deadline")

    def plan(steps):
        for kind, name, dur in steps:
            if kind == "rest":
                rest(name, dur)
                continue
            if st["abort_holds"]:
                decide(f"no {name}: an earlier hold ended on a card condition")
                rest(f"{name}-skipped", dur)
                continue
            if not a.smoke and left() < dur + 30.0:
                decide(f"no {name}: {left() / 60:.1f} min left, the hold needs {dur / 60:.0f}")
                continue
            m34 = rest_die(name)
            hname = name
            if name == "H_H" and not a.smoke and m34 is not None:
                if m34 > WARM_HI:
                    decide(f"no H_H: the rest die {m34:.3f} C is above {WARM_HI} C (Q138(t)'s warm-room rule)")
                    rest(f"{name}-skipped", dur)
                    continue
                if m34 > WARM_LO:
                    hname = "H_H'"
                    decide(f"H_H': the rest die {m34:.3f} C is in ({WARM_LO}, {WARM_HI}] C, so 2.60 s every 7.98 s")
            hold(hname, ITEMS[hname], dur, DUTY.get(hname))

    def stoptests():
        """E144 change 5: each stop path on live samples, with a line the idle card already meets"""
        keep = (a.gate_c, a.hold_c, a.hold_w, a.session_c)
        res = {}
        rest("T0", 5.0)
        a.gate_c = 1.0
        why, nl = hold("T_gate", "fp32.randn", 3.0, DUTY["H_H"])
        a.gate_c = keep[0]
        res["gate"] = {"launches": nl, "pass": nl == 0}
        a.hold_c = 1.0
        why, nl = hold("T_die", "fp32.randn", 3.0, DUTY["H_H"])
        a.hold_c = keep[1]
        res["hold_die"] = {"why": why, "launches": nl, "pass": why == "stop" and nl == 0}
        a.hold_w = 1.0
        why, nl = hold("T_board", "fp32.randn", 3.0, DUTY["H_H"])
        a.hold_w = keep[2]
        res["hold_board"] = {"why": why, "launches": nl, "pass": why == "stop" and nl == 0}
        rest("T1", 3.0)
        w0 = reading()["w"]
        a.hold_w = w0 + a.inlaunch_dw
        why, nl = hold("T_inlaunch", "fp32.randn", 12.0, DUTY["H_H"])
        a.hold_w = keep[2]
        res["in_launch"] = {"line_w": round(w0 + a.inlaunch_dw, 2), "why": why, "launches": nl, "pass": why == "stop" and nl >= 1}
        rest("T2", 3.0)
        a.session_c = 1.0
        try:
            reading()
            res["session"] = {"pass": False, "why": "no stop"}
        except b.Finished as e:
            res["session"] = {"pass": e.code == EXIT_HOT, "exit": e.code}
        a.session_c = keep[3]
        mark(kind="stoptest", t_ms=ms(), results=res, all_pass=all(v["pass"] for v in res.values()))
        say("stop tests: " + json.dumps(res))
        return res

    say(f"E144 pass {a.pass_no}: design {'smoke' if a.smoke else a.design}"
        f"{' + stop tests' if a.stoptest else ''}; deadline {time.strftime('%F %T %Z', time.localtime(a.deadline_epoch))}, "
        f"{left() / 60:.1f} min left; lines: gate {a.gate_c:g} C, hold {a.hold_c:g} C / {a.hold_w:g} W, session {a.session_c:g} C")
    w = None
    if not a.dry:
        w = threading.Thread(target=watcher, daemon=True)
        w.start()
    try:
        check("start")
        if a.smoke or not a.stoptest:
            plan(DESIGNS["smoke" if a.smoke else a.design])
        if a.stoptest:
            res = stoptests()
            if not all(v["pass"] for v in res.values()):
                raise b.Finished(1, "a stop test failed")
        say("done")
    finally:
        st["done"] = True


def parse_args(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--root", required=True)
    ap.add_argument("--tel-live", default=None)
    ap.add_argument("--sparsity", default="build/sparsity/host/sparsity_host")
    ap.add_argument("--pass-no", type=int, default=14420)
    ap.add_argument("--card", default="aifoundry3")
    ap.add_argument("--design", choices=("subset", "full"), default="subset")
    ap.add_argument("--deadline-epoch", type=float, default=None, help="default: now + 50 min")
    ap.add_argument("--launch-s", type=float, default=c.LAUNCH_S)
    ap.add_argument("--overhead-s", type=float, default=0.75, help="E89's: a launch's start-up and exit")
    ap.add_argument("--min-launch-s", type=float, default=1.0)
    ap.add_argument("--gate-c", type=float, default=70.0, help="no launch starts at a firmware reading at or above this")
    ap.add_argument("--hold-c", type=float, default=72.0, help="a hold ends at a sample at or above this")
    ap.add_argument("--hold-w", type=float, default=65.0, help="a hold ends at a board reading at or above this")
    ap.add_argument("--session-c", type=float, default=74.0, help="the pass ends at a sample at or above this")
    ap.add_argument("--inlaunch-dw", type=float, default=4.0, help="--stoptest: the in-launch board line over the idle")
    ap.add_argument("--watch-every-s", type=float, default=0.05)
    ap.add_argument("--stale-s", type=float, default=3.0)
    ap.add_argument("--check-every-s", type=float, default=60.0)
    ap.add_argument("--min-rate-hz", type=float, default=5.0)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--stoptest", action="store_true")
    ap.add_argument("--dry", action="store_true", default=bool(os.environ.get("V3_DRY")))
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args(argv)
    if a.deadline_epoch is None:
        a.deadline_epoch = time.time() + 50 * 60
    return a


def main():
    a = parse_args()
    bad = c.check_reused()
    if bad:
        raise SystemExit("E144: a file E97 reused differs from E97's freeze: " + "; ".join(bad))
    run_e89 = c.install_runner()
    ec = run_e89.ec
    os.chdir(a.root)
    items = {it["name"]: it for it in ec.load_items()}
    used = sorted(set(ITEMS.values()))
    bad = ec.verify_tiles(a.root, [items[n] for n in used])
    steps = DESIGNS["smoke" if a.smoke else a.design]
    plan_s = sum(d for _, _, d in steps) + (40 if a.stoptest else 0)
    if a.list:
        print(json.dumps({"design": "smoke" if a.smoke else a.design, "steps": steps, "items": used, "plan_s": plan_s,
                          "max_s": int(plan_s + 300), "left_s": int(a.deadline_epoch - time.time()), "tile_problems": bad}))
        sys.exit(EXIT_TILES if bad else 0)
    if bad:
        print("tiles failed their kinds.json sha256: " + "; ".join(bad), file=sys.stderr)
        sys.exit(EXIT_TILES)
    env = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
    os.makedirs(a.out, exist_ok=True)
    json.dump({"card": a.card, "args": vars(a), "holds": ITEMS, "duty": DUTY, "steps": steps, "items": [items[n] for n in used],
               "et_devices": os.environ.get("ET_DEVICES"), "experiment": "E144"},
              open(os.path.join(a.out, "configs.json"), "w"), indent=1)
    card = b.DryCard() if a.dry else b.RealCard(a, env)
    try:
        run_plan(a, card, a.out, items)
    except b.Finished as e:
        sys.exit(e.code)


if __name__ == "__main__":
    main()
