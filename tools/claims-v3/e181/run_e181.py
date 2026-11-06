#!/usr/bin/env python3
"""E181 runner (M11's session 2, aifoundry3 card 0, 600 MHz pinned; nothing set): M11's heat-over-minutes holds as
tools/claims-v3/m11/REGISTRATION.md section 5 (3c31a91d) registers them, amended by A1 (f49b7ddd), A2 (d3d97fe2), A3 (ed24bc6e),
A4 (0b554d25), A5 (9b084c66), A6 (95c75047), A7 (65a93fbb) and A8 (80b92990). A port of tools/claims-v3/e176/run_e176.py (03582d2f, which
stays as committed; itself E166's run_e166.py ported), with these changes, each marked E181:
  1. A6-3: H_E's warm pattern in (51.5, 53.9] C (WARM_HI 53.9); the cool one at a room at or under 51.5 C, unchanged.
  2. A6-1: the floor mark F0 in the smoke pass, before its first launch: the 34-sensor mean (E97's code_to_c) over the first 3 s of the
     pass's sampler file, with the firmware reading and the board W over the same samples; if F0 is above 53.9 C, or unreadable, the pass
     ends before the smoke's first launch with exit 7 (no hold), since R0 could not then pass.
  3. A6-2 and A8-4, the start gate after R0 (R0 unchanged: 5 minutes; its room the 34-sensor mean over its last 120 s): holds run only if
     R0's room is at or under 53.9 C AND R0's room less F0 less 0.414 C (A8's frozen prediction of the smoke's residue) is at or under
     0.50 C. F0 is read from the smoke pass's floor mark (--floor-marks). Else exit 7 and no hold. The start_gate mark records every reading,
     both lines and `passed`, which M11's scorer reads.
  4. --dry only: E181_DRY_ROOM_C=<C> (R0's room the toy reads, as E176's) and E181_DRY_FLOOR_C=<C> (F0, in the smoke or, with no floor
     marks, in the measured pass); both are refused without --dry.
  5. the pass numbers: 18101 (the smoke) and 18120 (the measured pass) by default; configs.json names E181 and the eight commits.
Everything else is E176's, unchanged: the design (R0 5, H_E 10, R1 6, Z 10, R2 2, L1 10, R3 6, S 10, R4 2, L2 10, R5 2.5 min) and the
smoke (each hold once, then E166's five stop tests on H_E's tile); the stops (no launch at a firmware reading >= 70 C; a hold ends at any
live sample >= 72 C, firmware or 34-sensor mean, or a board reading >= 65 W; the pass ends at >= 74 C), refused if looser; the watcher
thread on every live line (10 Hz) that writes the hold's stop file, which sparsity_host --stop-file reads before each dispatch; the
rest_die mark before each hold; E97's guards (a stale sampler, another user on the card, a clock off 600 MHz in 5 samples, three failed
launches); the launches through the binary --sparsity names (block_e181.sh: Q139(k)'s C-check wrapper with the C-logging host);
marks.jsonl and runs.jsonl in run_e97b.py's formats (score_e166.py's readers, which M11's scorer calls unchanged, read them).

    python3 tools/claims-v3/e181/run_e181.py <out-dir> --root <tree> --tel-live <sampler file> --sparsity <bin>
        [--pass-no 18120] [--deadline-epoch N] [--floor-marks <smoke pass marks.jsonl>] [--smoke] [--stoptest] [--dry] [--list]
    exit 0 done; 3 another user on this card; 4 the sampler stopped writing; 5 no telemetry; 6 the session stop (74 C);
         7 a gate: A6-1 (F0 above 53.9 C or unreadable, before the smoke's first launch) or the start gate (R0's room above 53.9 C, the
           residue over A8-4's line, or either unreadable); 8 STOP file; 9 a tile failed its sha256
Nothing here opens the management node (the sampler, E89's pvt_sample.py, does); nothing is set.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
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

EXIT_OTHERS, EXIT_STALL, EXIT_NOTEL, EXIT_HOT, EXIT_GATE, EXIT_STOP, EXIT_TILES = 3, 4, 5, 6, 7, 8, 9
# the hold items (REGISTRATION.md section 5), E78's (kinds.json): E176's, unchanged
ITEMS = {"H_E": "fp32.randn", "Z": "fp32.zeros", "L1": "int8.full", "S": "int8.neg_ones", "L2": "int8.full"}
# H_E's duty, E144's H_H pattern (A1.1): the cool pattern at a room at or under 51.5 C; E181 change 1 (A6-3): the warm one in (51.5, 53.9]
HE_SECONDS_COOL, HE_PERIOD_COOL = 3.20, 7.56
HE_SECONDS_WARM, HE_PERIOD_WARM = 2.60, 7.98
WARM_LO, WARM_HI = 51.5, 53.9
STOPTEST_ITEM = "fp32.randn"
ROOM_MAX_C = 53.9                    # E181 change 3: A6-2's room line
FLOOR_MAX_C = 53.9                   # E181 change 2: A6-1's stop before the smoke's first launch
FLOOR_WINDOW_S = 3.0                 # A6-1: the first 3 s of the smoke pass's samples
RESIDUE_PRED_C = 0.414               # E181 change 3: A8-4's frozen prediction (tools/claims-v3/m11/residue-a8.json > E181)
RESIDUE_LINE_C = 0.50                # A6-2's line, referred to the predicted residue by A8-4
EPS_C = 1e-9                         # "at or under" a line, read through floating point (0.914 - 0.414 is 0.5000000000000016)
REGISTRATION = {"m11": "3c31a91d", "a1": "f49b7ddd", "a2": "d3d97fe2", "a3": "ed24bc6e", "a4": "0b554d25", "a5": "9b084c66",
                "a6": "95c75047", "a7": "65a93fbb", "a8": "80b92990"}
# the registered design (minutes x 60) and the smoke: E176's, unchanged
DESIGNS = {
    "full": [("rest", "R0", 300.0), ("hold", "H_E", 600.0), ("rest", "R1", 360.0), ("hold", "Z", 600.0), ("rest", "R2", 120.0),
             ("hold", "L1", 600.0), ("rest", "R3", 360.0), ("hold", "S", 600.0), ("rest", "R4", 120.0), ("hold", "L2", 600.0),
             ("rest", "R5", 150.0)],
    "smoke": [("rest", "R0", 8.0), ("hold", "H_E", 11.0), ("rest", "R1", 2.0), ("hold", "Z", 5.0), ("rest", "R2", 2.0),
              ("hold", "L1", 5.0), ("rest", "R3", 2.0), ("hold", "S", 5.0), ("rest", "R4", 2.0), ("hold", "L2", 5.0),
              ("rest", "R5", 3.0)],
}


def sha256_bytes(x):
    return hashlib.sha256(x).hexdigest()


def head_samples(path, n=200):
    """the first n sampler lines of a live sampler file (E181 change 2: A6-1 reads the pass's FIRST 3 s, not its newest lines)"""
    out = []
    try:
        with open(path, "rb") as f:
            for raw in f:
                line = raw.decode(errors="ignore").strip()
                if line.startswith("{") and line.endswith("}"):
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        continue
                if len(out) >= n:
                    break
    except OSError:
        return []
    return out


def floor_from_marks(path):
    """E181 change 3: F0 from the smoke pass's last floor mark, or (None, why)"""
    if not path:
        return None, "no --floor-marks (the smoke pass's marks.jsonl)"
    try:
        fl = [json.loads(x) for x in open(path) if x.strip().startswith("{") and '"floor"' in x]
    except (OSError, ValueError) as e:
        return None, f"the floor marks unreadable ({type(e).__name__})"
    fl = [m for m in fl if m.get("kind") == "floor"]
    if not fl:
        return None, "the smoke pass recorded no floor mark"
    v = fl[-1].get("mean34_c")
    if not isinstance(v, (int, float)):
        return None, "the smoke pass's floor mark holds no 34-sensor mean"
    return float(v), None


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
          "done": False, "room": None, "he_duty": None, "gate_ok": None}

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
        """E144's hold and session lines on one live sample. True if a line fired."""
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

    def floor_mark():
        """E181 change 2 (A6-1): F0, the 34-sensor mean over the first 3 s of this pass's samples, before the smoke's first launch"""
        if a.dry:
            recs = card.tail(FLOOR_WINDOW_S)                                  # E97's toy card: its own samples
        else:
            t_wait = card.now() + 10.0                                        # the block starts the sampler 3 s before the runner
            recs = head_samples(a.tel_live)
            while (not recs or recs[-1]["t_ms"] / 1000.0 < recs[0]["t_ms"] / 1000.0 + FLOOR_WINDOW_S) and card.now() < t_wait:
                card.sleep(0.5)
                recs = head_samples(a.tel_live)
        t_first = min((r.get("t_ms", 0) for r in recs), default=None)
        win = [r for r in recs if t_first is not None and r.get("t_ms", 0) < t_first + FLOOR_WINDOW_S * 1000]
        m = [v for v in (b.die_mean(r) for r in win) if v is not None]
        fw = [float(r["temp_c"]["minshire"][0]) for r in win if (r.get("temp_c") or {}).get("minshire")]
        bw = [float(r["board_w"]) for r in win if r.get("board_w") is not None]
        f0 = (sum(m) / len(m)) if len(m) >= 0.5 * FLOOR_WINDOW_S * a.min_rate_hz else None
        dry_floor = os.environ.get("E181_DRY_FLOOR_C")
        if dry_floor:
            if not a.dry:
                stop(EXIT_GATE, "E181_DRY_FLOOR_C is for --dry only")
            f0 = float(dry_floor)
        ok = f0 is not None and f0 <= FLOOR_MAX_C + EPS_C
        mark(kind="floor", t_ms=ms(), first_sample_ms=t_first, window_s=FLOOR_WINDOW_S, samples=len(win), samples_34=len(m),
             mean34_c=f0, firmware_c=(sum(fw) / len(fw)) if fw else None, board_w=(sum(bw) / len(bw)) if bw else None,
             line_c=FLOOR_MAX_C, passed=ok, dry_floor=bool(dry_floor),
             why=("F0 at or under 53.9 C: the smoke runs" if ok else ("F0 unreadable" if f0 is None else f"F0 {f0:.3f} C > {FLOOR_MAX_C} C")))
        say(f"floor F0 (A6-1, the first {FLOOR_WINDOW_S:g} s of the pass's samples): 34-sensor mean "
            f"{f0 if f0 is None else round(f0, 3)} C over {len(m)} samples, firmware "
            f"{round(sum(fw) / len(fw), 2) if fw else None} C, board {round(sum(bw) / len(bw), 2) if bw else None} W")
        if not ok:
            mark(kind="decision", t_ms=ms(), left_s=round(left(), 1), choice="A6-1: the session ends before the smoke's first launch: no hold",
                 floor_c=f0)
            stop(EXIT_GATE, "A6-1: " + ("F0 unreadable" if f0 is None else f"F0 {f0:.3f} C above {FLOOR_MAX_C} C")
                 + ": the session ends before the smoke's first launch, no hold")

    def rest(name, dur_s):
        """E144's: idle for the frozen minutes, the sampler reading"""
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
        """E144's"""
        m34, fw = mean34(0.0, 120.0), firmware(0.0, 120.0)
        mark(kind="rest_die", hold=hold_name, t_ms=ms(), window_s=120.0, mean34_c=m34, firmware_c=fw)
        say(f"rest die before {hold_name}: 34-sensor mean {m34 if m34 is None else round(m34, 3)} C, firmware "
            f"{fw if fw is None else round(fw, 2)} C (last 120 s)")
        return m34

    def room_rule():
        """H_E's pattern (E144's H_H room rule, A6-3) and the start gate (A6-2 with A8-4), read once at R0's end"""
        m34, fw = mean34(0.0, 120.0), firmware(0.0, 120.0)
        dry_room = os.environ.get("E181_DRY_ROOM_C")
        if dry_room:
            if not a.dry:
                stop(EXIT_GATE, "E181_DRY_ROOM_C is for --dry only")
            m34 = float(dry_room)
        if a.smoke:
            duty, why = (HE_SECONDS_COOL, HE_PERIOD_COOL), "smoke: the cool pattern"
        elif m34 is None:
            duty, why = (HE_SECONDS_WARM, HE_PERIOD_WARM), "R0's rest die unreadable: the warm pattern (the lower peak)"
        elif m34 <= WARM_LO:
            duty, why = (HE_SECONDS_COOL, HE_PERIOD_COOL), f"room {m34:.3f} C <= {WARM_LO} C: the cool pattern"
        elif m34 <= WARM_HI:
            duty, why = (HE_SECONDS_WARM, HE_PERIOD_WARM), f"room {m34:.3f} C in ({WARM_LO}, {WARM_HI}] C: the warm pattern"
        else:
            duty, why = None, f"room {m34:.3f} C > {WARM_HI} C: no hold (G0-A6)"
        st["room"], st["he_duty"] = m34, duty
        mark(kind="room", t_ms=ms(), window_s=120.0, mean34_c=m34, firmware_c=fw, he_seconds=duty[0] if duty else None,
             he_period_s=duty[1] if duty else None, why=why, dry_room=bool(dry_room))
        say(f"room (R0's rest die): 34-sensor mean {m34 if m34 is None else round(m34, 3)} C, firmware "
            f"{fw if fw is None else round(fw, 2)} C; H_E: {why}")
        if a.smoke:
            mark(kind="start_gate", t_ms=ms(), room_c=m34, max_c=ROOM_MAX_C, passed=None, why="smoke: not applied")
            st["gate_ok"] = True
            return
        # E181 change 3: F0 from the smoke pass's floor mark (or, in --dry with no floor marks, E181_DRY_FLOOR_C)
        f0, fwhy = floor_from_marks(a.floor_marks)
        dry_floor = os.environ.get("E181_DRY_FLOOR_C")
        if dry_floor and not a.floor_marks:
            if not a.dry:
                stop(EXIT_GATE, "E181_DRY_FLOOR_C is for --dry only")
            f0, fwhy = float(dry_floor), None
        resid = (m34 - f0) if (m34 is not None and f0 is not None) else None
        excess = (resid - RESIDUE_PRED_C) if resid is not None else None
        ok_room = m34 is not None and m34 <= ROOM_MAX_C + EPS_C
        ok_res = excess is not None and excess <= RESIDUE_LINE_C + EPS_C
        ok = ok_room and ok_res
        st["gate_ok"] = ok
        if ok:
            why = (f"room {m34:.3f} C <= {ROOM_MAX_C} C and R0's room - F0 - {RESIDUE_PRED_C} = {excess:+.3f} C <= {RESIDUE_LINE_C} C: "
                   "the design runs")
        elif m34 is None:
            why = "R0's room unreadable"
        elif not ok_room:
            why = f"room {m34:.3f} C > {ROOM_MAX_C} C"
        elif f0 is None:
            why = f"F0 unreadable ({fwhy})"
        else:
            why = f"R0's room - F0 - {RESIDUE_PRED_C} = {excess:+.3f} C > {RESIDUE_LINE_C} C (A8-4)"
        mark(kind="start_gate", t_ms=ms(), room_c=m34, max_c=ROOM_MAX_C, floor_c=f0, floor_from=a.floor_marks or ("dry" if dry_floor else None),
             residue_c=resid, residue_pred_c=RESIDUE_PRED_C, residue_excess_c=excess, residue_line_c=RESIDUE_LINE_C,
             room_ok=ok_room, residue_ok=ok_res, passed=ok, why=why, rule="A6-2 with A8-4")
        say(f"start gate (G0-A6 with A8-4): {'passed' if ok else 'NOT passed'}: {why}")

    def launch(item, secs, hold_name, phase):
        it = items[item]
        cmd = [a.sparsity, "--test", "fma", "--type", it["type"], "--pattern", "none",
               "--values", "file:" + os.path.join(a.root, it["tile"]), "--shires", "0xffffffff", "--per-shire", "32",
               "--seconds", f"{secs:.2f}", "--seed", str(a.pass_no + 1), "--stop-file", hold_stop]
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
        """E144's: launches of `item` for dur_s, back to back (duty None) or duty-cycled from the first launch."""
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
                if name == "R0":
                    room_rule()
                    if not st["gate_ok"]:
                        decide("E181 not started: the start gate (G0-A6 with A8-4): no hold runs", room_c=st["room"])
                        stop(EXIT_GATE, f"the start gate: R0's room {st['room']} C (at most {ROOM_MAX_C} C; and the residue line of A8-4)")
                continue
            if st["abort_holds"]:
                decide(f"no {name}: an earlier hold ended on a card condition")
                rest(f"{name}-skipped", dur)
                continue
            if not a.smoke and left() < dur + 30.0:
                decide(f"no {name}: {left() / 60:.1f} min left, the hold needs {dur / 60:.0f}")
                continue
            rest_die(name)
            duty = None
            if name == "H_E":
                if st["he_duty"] is None:
                    decide(f"no H_E: the room {st['room']} C is above {WARM_HI} C: its {dur / 60:.0f} minutes are a rest")
                    rest(f"{name}-skipped", dur)
                    continue
                duty = st["he_duty"]
            hold(name, ITEMS[name], dur, duty)

    def stoptests():
        """E144's five stop-path tests (E176's: on H_E's tile at the cool pattern), each with a line the idle card already meets"""
        keep = (a.gate_c, a.hold_c, a.hold_w, a.session_c)
        duty = (HE_SECONDS_COOL, HE_PERIOD_COOL)
        res = {}
        rest("T0", 5.0)
        a.gate_c = 1.0
        why, nl = hold("T_gate", STOPTEST_ITEM, 3.0, duty)
        a.gate_c = keep[0]
        res["gate"] = {"launches": nl, "pass": nl == 0}
        a.hold_c = 1.0
        why, nl = hold("T_die", STOPTEST_ITEM, 3.0, duty)
        a.hold_c = keep[1]
        res["hold_die"] = {"why": why, "launches": nl, "pass": why == "stop" and nl == 0}
        a.hold_w = 1.0
        why, nl = hold("T_board", STOPTEST_ITEM, 3.0, duty)
        a.hold_w = keep[2]
        res["hold_board"] = {"why": why, "launches": nl, "pass": why == "stop" and nl == 0}
        rest("T1", 3.0)
        w0 = reading()["w"]
        a.hold_w = w0 + a.inlaunch_dw
        why, nl = hold("T_inlaunch", STOPTEST_ITEM, 12.0, duty)
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

    say(f"E181 pass {a.pass_no}: design {'smoke' if a.smoke else 'full'}"
        f"{' + stop tests' if a.stoptest else ''}; deadline {time.strftime('%F %T %Z', time.localtime(a.deadline_epoch))}, "
        f"{left() / 60:.1f} min left; lines: gate {a.gate_c:g} C, hold {a.hold_c:g} C / {a.hold_w:g} W, session {a.session_c:g} C")
    w = None
    if not a.dry:
        w = threading.Thread(target=watcher, daemon=True)
        w.start()
    try:
        check("start")
        if a.smoke:
            floor_mark()                                                                 # E181 change 2: A6-1, before any launch
        if a.smoke or not a.stoptest:
            plan(DESIGNS["smoke" if a.smoke else "full"])
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
    ap.add_argument("--pass-no", type=int, default=18120)
    ap.add_argument("--card", default="aifoundry3")
    ap.add_argument("--deadline-epoch", type=float, default=None, help="default: now + 80 min")
    ap.add_argument("--floor-marks", default=None, help="the smoke pass's marks.jsonl, whose floor mark is F0 (A6-1)")
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
        a.deadline_epoch = time.time() + 80 * 60
    # the registered lines may only be stricter (REGISTRATION.md section 5, E166's stops): refuse a looser one
    if a.gate_c > 70.0 or a.hold_c > 72.0 or a.hold_w > 65.0 or a.session_c > 74.0:
        raise SystemExit("E181: a stop line is looser than registered (gate 70 C, hold 72 C / 65 W, session 74 C)")
    for k in ("E181_DRY_ROOM_C", "E181_DRY_FLOOR_C"):
        if os.environ.get(k) and not a.dry:
            raise SystemExit(f"E181: {k} is for --dry only")
    return a


def main():
    a = parse_args()
    bad = c.check_reused()
    if bad:
        raise SystemExit("E181: a file E97 reused differs from E97's freeze: " + "; ".join(bad))
    run_e89 = c.install_runner()
    ec = run_e89.ec
    os.chdir(a.root)
    items = {it["name"]: it for it in ec.load_items()}
    steps = DESIGNS["smoke" if a.smoke else "full"]
    used = sorted({ITEMS[n] for k, n, _ in steps if k == "hold"} | ({STOPTEST_ITEM} if a.stoptest else set()))
    bad = [f"{n}: not an E78 item" for n in used if n not in items]                    # the E78 tiles by sha256 (E176's)
    bad += ec.verify_tiles(a.root, [items[n] for n in used if n in items])            # e78_common.verify_tiles: whole file, A, B
    plan_s = sum(d for _, _, d in steps) + (40 if a.stoptest else 0)
    if a.list:
        print(json.dumps({"design": "smoke" if a.smoke else "full", "steps": steps, "items": used, "plan_s": plan_s,
                          "max_s": int(plan_s + 300), "left_s": int(a.deadline_epoch - time.time()), "tile_problems": bad,
                          "he_pattern": {"cool_at_or_under_51.5C": [HE_SECONDS_COOL, HE_PERIOD_COOL],
                                         "warm_51.5_to_53.9C": [HE_SECONDS_WARM, HE_PERIOD_WARM]},
                          "gates": {"A6-1_floor_max_c": FLOOR_MAX_C, "A6-2_room_max_c": ROOM_MAX_C, "A8-4_residue_pred_c": RESIDUE_PRED_C,
                                    "A8-4_residue_line_c": RESIDUE_LINE_C}}))
        sys.exit(EXIT_TILES if bad else 0)
    if bad:
        print("tiles failed their sha256: " + "; ".join(bad), file=sys.stderr)
        sys.exit(EXIT_TILES)
    env = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib")
    os.makedirs(a.out, exist_ok=True)
    json.dump({"card": a.card, "args": vars(a), "holds": ITEMS, "he": {"cool": [HE_SECONDS_COOL, HE_PERIOD_COOL],
               "warm": [HE_SECONDS_WARM, HE_PERIOD_WARM], "warm_lo_c": WARM_LO, "warm_hi_c": WARM_HI}, "start_gate_room_max_c": ROOM_MAX_C,
               "floor_max_c": FLOOR_MAX_C, "floor_window_s": FLOOR_WINDOW_S, "residue_pred_c": RESIDUE_PRED_C,
               "residue_line_c": RESIDUE_LINE_C, "steps": steps, "items": [items[n] for n in used], "et_devices": os.environ.get("ET_DEVICES"),
               "ccheck_log": os.environ.get("CCHECK_LOG"), "dry_room_c": os.environ.get("E181_DRY_ROOM_C"),
               "dry_floor_c": os.environ.get("E181_DRY_FLOOR_C"), "experiment": "E181", "registration": REGISTRATION},
              open(os.path.join(a.out, "configs.json"), "w"), indent=1)
    card = b.DryCard() if a.dry else b.RealCard(a, env)
    try:
        run_plan(a, card, a.out, items)
    except b.Finished as e:
        sys.exit(e.code)


if __name__ == "__main__":
    main()
