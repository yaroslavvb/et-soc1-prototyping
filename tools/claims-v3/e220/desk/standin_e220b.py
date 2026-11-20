#!/usr/bin/env python3
"""E220 (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): THE STAND-INS of the real-path desk test (desk/realpath_e220b.py), E209's
desk/standin_e209.py form, for every device tool the REAL path of E220's runner (src/run_e220b.py: E208's runner, imported) calls: the reader
behind the guard (build/ettelem/ettelem: `config`, `sample`), rgm136's host (build/rgm/host/sparsity_host), RGM211'S HOST for family G
(build/e220brgm211/host/sparsity_host: `g-host`), and et-who. They are E208's own doubles (src/fake_card_mms.py, unchanged, imported from the box
root's src/: its toy card, its config and et-who, its scenario words MMS_FAKE_*) with what E209's lessons add and what family G needs, each a
desk test's arbitrary value, never a forecast and never a measurement:
  E220B_SI_DIE_ADD=<C>, E220B_SI_DIE_ARM=<the double's arm id>   the die reads <C> more while that arm's process runs (THE DIE STOP)
  E220B_SI_STEP_S=<s>, E220B_SI_STEP_ARM=<arm id>                the governor steps that arm's clock DOWN to 600 MHz <s> seconds into its
                                                               process (A STEP INSIDE THE BUSY WINDOW: the sampler and the launches read it)
  E220B_SI_RUNTIME=between|split, E220B_SI_RUNTIME_ARM=<arm id>  runtime lines in the host's stdout (E191's lesson): between two records, or
                                                               splitting a record's line (the check record's, by 'split')
  E220B_SI_IGNORE_TERM_S=<s>, E220B_SI_HANG_ARM=<arm id>         that arm's host ignores SIGTERM and lives <s> s past its end, then ends by itself
                                                               and writes <MMS_FAKE_DIR>/host-hang.ended (nothing may kill it: no SIGKILL)
  E220B_SI_LATCH0=<C>                                           the hottest-sensor latch's reading from the first sample (default 60: a latch
                                                               already high from before the session reads, say, 85 here)
  E220B_SI_LATCH_RISE=<C>, E220B_SI_LATCH_ARM=<arm id>           the latch rises by <C> while that arm's process runs and holds it (a latch
                                                               holds its maximum: THE LATCH STOP once it is at or above 70 C)
  E220B_SI_WALK_FAIL_ARM=<arm id>                               that G process's launches print walk_ok false (THE WALK CHECK, a kernel stop)
The double's arm id is fake_card_mms.py's: <MB>x<NB>x<KB>-<type>-<rnd|zeros|ones>[-s<shires>], and a family-G process's is 'nc' + it (rgm211's
host running a gemmLnc arm), so a desk test's MMS_FAKE_TRIP_ARM=nc lifts the toy board in the G block alone. The G host prints rgm211's walk
fields ('mn', no tag, walk_ok) on every launch and walk_launches_bad on its check record, and refuses any arm but gemmLnc (exit 1), as the
kit's dry double does (src/fake_card_e220b.py).
Each stand-in opens what the real tool opens (the reader the card's mgmt node, the hosts their ops node), so the runner's identity read and
host watch see them: the sandbox's /dev holds two REGULAR FILES named et0_ops and et0_mgmt, and MMS_FAKE_DIR is /dev there.
    standin_e220b.py reader config | reader sample --seconds S --every-ms M | host <argv...> | g-host <argv...> | etwho [--check]
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import random
import signal
import sys
import time

sys.path.insert(0, os.environ.get("E220B_SI_SRC", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")))
import fake_card_mms as F  # noqa: E402  (E208's doubles, unchanged)
import mms_common as C  # noqa: E402


G = {"on": False}       # set by the g-host mode: rgm211's host running a gemmLnc arm


def arm_id(argv):
    a = {argv[i]: argv[i + 1] for i in range(len(argv) - 1) if argv[i].startswith("--") and not argv[i + 1].startswith("--")}
    mb, nb, kb, kind = F.parse_values(a["--values"])
    shires = bin(int(a["--shires"], 16)).count("1")
    return ("nc" if G["on"] else "") + f"{mb}x{nb}x{kb}-{a['--type']}-{kind}" + ("" if shires == 32 else f"-s{shires}")


def cmd_sample(argv):
    """fake_card_mms.cmd_sample's loop, with E220B_SI_DIE_ADD (and the clock the host writes, as there)"""
    secs = float(argv[argv.index("--seconds") + 1])
    every = float(argv[argv.index("--every-ms") + 1])
    stall = int(os.environ.get("MMS_FAKE_SAMPLER_STALL") or 0)
    node = open(os.path.join(F.FD, f"et{F.NUM}_mgmt"), "a")
    rng = random.Random(7)
    die, t0 = F.REST_DIE, time.time()
    latch0 = int(os.environ.get("E220B_SI_LATCH0") or 60)
    latch = latch0
    l_rise, l_arm = int(os.environ.get("E220B_SI_LATCH_RISE") or 0), os.environ.get("E220B_SI_LATCH_ARM") or ""
    add_c, add_arm = float(os.environ.get("E220B_SI_DIE_ADD") or 0), os.environ.get("E220B_SI_DIE_ARM") or ""
    trip_w, trip_arm = float(os.environ.get("MMS_FAKE_TRIP") or 0), os.environ.get("MMS_FAKE_TRIP_ARM") or ""
    taus = C.CARDS[F.CARD]["tau_s"]
    rail = {r: v[0] for r, v in F.RAIL_SHARE.items()}
    prev_true = dict(rail)
    n, t_pass = 0, time.time()
    while time.time() - t0 < secs * F.SCALE:
        st = F.read_state()
        f, lift = 600, 0.0
        if st.get("running"):
            f = st.get("f", 600)
            lift = F.lift_at(st, f)
            if F.GOV and f >= 790:
                lift = min(lift, F.CAP_W - F.REST_W)
            if trip_w and trip_arm and trip_arm in st.get("arm", ""):
                lift += trip_w
        board = F.REST_W + F.LEAK_W_C * (die - F.REST_DIE) + lift + rng.gauss(0, 0.15)
        target = F.REST_DIE + F.HEAT_C_W * (board - F.REST_W)
        die += (target - die) * min(1.0, every / 1000.0 / F.DIE_TAU_S)
        die_read = die + (add_c if (add_c and st.get("running") and add_arm and add_arm == st.get("arm")) else 0.0)
        if l_rise and st.get("running") and l_arm and l_arm == st.get("arm"):
            latch = max(latch, latch0 + l_rise)          # a latch holds its maximum
        if n % 2 == 0:
            now = time.time()
            for r, (r0, share) in F.RAIL_SHARE.items():
                a = math.exp(-(now - t_pass) / (taus[r] * F.SCALE))
                rail[r] = a * rail[r] + (1 - a) * prev_true[r]
                prev_true[r] = r0 + share * lift + F.LEAK_W_C * share * (die - F.REST_DIE)
            t_pass = now
        n += 1
        if stall and n > stall:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            time.sleep(25.0)
            break
        s = {"t_ms": F.now_ms(), "took_ms": 22, "since_reset_ms": -1, "board_w": round(board, 2),
             "sp": {"board_avg_w": round(board, 2), "minion_w": [round(rail["minion"], 3), 5.0, 40.0], "sram_w": [round(rail["sram"], 3), 2.0, 9.0],
                    "noc_w": [round(rail["noc"], 3), 1.0, 6.0], "minion_mv": [F.MV, F.MV, F.MV + 100], "minion_mhz": [f, 600, 800]},
             "temp_c": {"pmic": 40, "ioshire": [45, 40, 50], "minshire": [int(die_read), int(die_read) - 3, latch]},
             "die_mv": {"ddr": 800, "sram": 750, "maxion": 750, "minion": F.MV, "pshire": 750, "noc": 750, "ioshire": 750},
             "mhz": {"minion": f, "noc": 400, "ddr": 1600}}
        print(json.dumps(s), flush=True)
        F.nap(every / 1000.0)
    node.close()
    return 0


def parent_timeout():
    """the plain timeout this stand-in host runs under, read from its parent's command line (`timeout <T> <host> ...`); None if none"""
    try:
        w = open(f"/proc/{os.getppid()}/cmdline", "rb").read().split(b"\0")
        return w[1].decode() if len(w) > 1 and os.path.basename(w[0].decode()) == "timeout" else None
    except OSError:
        return None


def cmd_host(argv):
    """fake_card_mms.cmd_host with the step, the runtime lines and the TERM-deaf hang above; otherwise E208's double. Its stderr's first line
    names the plain timeout it runs under (kit-e220: the real-path test reads E220's sized timeout from it)"""
    sys.stderr.write(f"STANDIN-TIMEOUT {parent_timeout()}\n")
    sys.stderr.flush()
    aid = arm_id(argv)
    step_s = float(os.environ.get("E220B_SI_STEP_S") or 0) if os.environ.get("E220B_SI_STEP_ARM") == aid else 0.0
    rt = os.environ.get("E220B_SI_RUNTIME") if os.environ.get("E220B_SI_RUNTIME_ARM") == aid else None
    hang_s = float(os.environ.get("E220B_SI_IGNORE_TERM_S") or 0) if os.environ.get("E220B_SI_HANG_ARM") == aid else 0.0
    walk_fail = G["on"] and os.environ.get("E220B_SI_WALK_FAIL_ARM") == aid
    if not (step_s or rt or hang_s or G["on"]):
        return F.cmd_host(argv)
    a = {argv[i]: argv[i + 1] for i in range(len(argv) - 1) if argv[i].startswith("--") and not argv[i + 1].startswith("--")}
    t = a["--type"]
    mb, nb, kb, kind = F.parse_values(a["--values"])
    shires = bin(int(a["--shires"], 16)).count("1")
    seconds, budget, stop = float(a["--seconds"]), float(a["--budget"]), a.get("--stop-file")
    ops_node = open(os.path.join(F.FD, f"et{F.NUM}_ops"), "a")
    sys.stderr.write(F.IDENT.format(c=F.NUM, k="ops"))
    if hang_s:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        sys.stderr.write("a desk test's host that ignores SIGTERM (E220B_SI_HANG_ARM)\n")
    reg = F.regime(mb, nb, kb)
    c600 = F.CYC600[reg][t] if reg == "l2" else F.CYC600[reg]
    T600 = c600 / 600e6
    T800 = T600 / F.X[reg]
    st = {"running": True, "t0": time.time(), "lift600": F.LIFT600[kind][t], "regime": reg, "share": shires / 32.0, "arm": aid, "f": 600}
    F.write_state(st)
    F.nap(0.3)
    ops_pass = mb * nb * 2 * kb * 32
    v_age, launch, spent, iters = 0.3, -1, 0.0, max(1, 64000 // ops_pass)

    def clock(age):
        if age <= 1.0:
            return 600
        return 600 if (step_s and age > step_s) else 800

    n_fma = [0]

    def emit(rec):
        if G["on"]:
            rec = dict(rec, arm="gemmLnc" + rec["arm"][len("gemmL"):])
            if rec.get("test") == "fma":
                n_fma[0] += 1
                rec.update(walk="mn", walk_tagged=0, walk_ok=not walk_fail)
                if walk_fail:
                    rec["ok"] = False
            elif rec.get("test") == "check":
                rec.update(walk="mn", walk_launches_bad=n_fma[0] if walk_fail else 0)
                if walk_fail:
                    rec["ok"] = False
        line = "SPARSITY " + json.dumps(rec)
        if rt == "split" and rec.get("test") == "check":
            k = len(line) // 2
            sys.stdout.write(line[:k] + "\n[runtime] ET [DEVICE_LAYER]: a print of the device layer inside a record\n" + line[k:] + "\n")
        else:
            sys.stdout.write(line + "\n")
            if rt == "between":
                sys.stdout.write("[runtime] ET [DEVICE_LAYER]: a print of the device layer between records\n")
        sys.stdout.flush()

    while True:
        f = clock(v_age)
        st["f"] = f
        F.write_state(st)
        T = T600 * 600.0 / f if f != 800 else T800
        wall = iters * ops_pass * T + 0.002
        t_s = F.now_ms()
        F.nap(wall)
        cmax = (wall - 0.002) * f * 1e6
        ops = iters * ops_pass
        emit({"test": "fma", "arm": f"gemmL{mb}x{nb}x{kb}", "type": t, "minions": 32 * shires, "iters": ops, "passes": iters, "launch": launch,
              "cycles_max": int(cmax), "cycles_mean": round(cmax * 0.985, 1), "cycles_per_op": round(cmax * 0.985 / ops, 3),
              "wall_s": round(wall, 6), "t_start_ms": t_s, "t_end_ms": F.now_ms(), "ghz": round(cmax / wall / 1e9, 4), "tensor_errors": 0,
              "result": "unchecked", "ok": True})
        v_age += wall
        if launch == -1:
            iters = max(1, int(iters * 0.5 / wall))
        else:
            spent += wall
        launch += 1
        if spent >= seconds:
            break
        if v_age > budget:
            sys.stderr.write(f"stopping: device-time budget of {budget:.1f} s used\n")
            break
        if stop and os.path.exists(stop):
            sys.stderr.write(f"stopping: {stop} exists\n")
            break
    f = clock(v_age)
    T = T600 * 600.0 / f if f != 800 else T800
    wall = ops_pass * T + 0.003
    t_s = F.now_ms()
    F.nap(wall)
    emit({"test": "fma", "arm": f"gemmL{mb}x{nb}x{kb}", "type": t, "iters": ops_pass, "passes": 1, "launch": -3,
          "cycles_max": int((wall - 0.003) * f * 1e6), "cycles_mean": 0, "cycles_per_op": 0, "wall_s": round(wall, 6), "t_start_ms": t_s,
          "t_end_ms": F.now_ms(), "ok": True})
    res = "approx" if (kind == "rnd" and t != "int8") else "exact"
    F.write_state({"running": False})
    F.nap(0.2)
    emit({"test": "check", "arm": f"gemmL{mb}x{nb}x{kb}", "type": t, "launch": -2, "cycles_per_op": round(c600, 3), "wall_s": 0, "words": 8192,
          "exact": 8192 if res == "exact" else 0, "within": 8192, "result": res, "ok": True})
    if hang_s:
        sys.stderr.write(f"alive {hang_s:g} s more, deaf to SIGTERM\n")
        sys.stderr.flush()
        time.sleep(hang_s)
        open(os.path.join(F.FD, "host-hang.ended"), "a").write(f"{time.time()}\n")     # it ended by itself: nothing killed it
    ops_node.close()
    sys.stderr.write(f"device held for {v_age:.2f} s\n")
    return 1 if walk_fail else 0


def cmd_g_host(argv):
    """rgm211's host for family G: a gemmLnc arm only (else rgm211's own refusal words, exit 1), read as its gemmL twin by the toy card"""
    i = argv.index("--values") if "--values" in argv else -1
    v = argv[i + 1] if i >= 0 else ""
    arm = v.split(":", 1)[0]
    if not arm.startswith("gemmLnc"):
        sys.stderr.write(f"error: the desk stand-in of rgm211's host runs gemmLnc arms here, not {arm}\n")
        return 1
    argv = list(argv)
    argv[i + 1] = "gemmL" + v[len("gemmLnc"):]
    G["on"] = True
    return cmd_host(argv)


def main(argv):
    if argv[:2] == ["reader", "config"]:
        return F.cmd_config()
    if argv[:2] == ["reader", "sample"]:
        return cmd_sample(argv[2:])
    if argv[:1] == ["host"]:
        return cmd_host(argv[1:])
    if argv[:1] == ["g-host"]:
        return cmd_g_host(argv[1:])
    if argv[:1] == ["etwho"]:
        if "--check" in argv:
            busy = os.environ.get("E220B_SI_ETWHO_CHECK_RC") or "0"
            return int(busy)
        return F.cmd_etwho()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
