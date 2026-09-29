#!/usr/bin/env python3
"""Test doubles for energy.sh --dry (V3_DRY-style): no device, no management node, no lock.

    energy_stub.py sample --seconds T --every-ms M --sched FILE [--truth FILE] [--card base|alt]
        stands in for `ettelem sample`: prints ettelem's JSON lines in real time from a simulated card whose
        dynamic power switches on during the launches the host double appends to FILE; on SIGTERM (or at T) it
        finishes its line, writes the injected energies to --truth and exits 0, as ettelem does
    energy_stub.py host --sched FILE [sparseparity_host arguments]
        stands in for sparseparity_host: --dry prints the plan's JSON line (the real host's model, guard and timeout
        for the presets below); otherwise it sleeps through the phases of a run (plan, device open, --reps launches
        under the host's own --budget rule, readback, checks) and prints a JSON line with the fields the reducer reads

The simulated card, chosen to exercise what the reducer must undo: board power = 12.4 W + the idle law's leakage
(23.257 W e^((T-80)/36), analyze_catalogue.py) + the dynamic power during launches; the board reading is a point
sample refreshed every SP pass (E58 on aifoundry3: 0.296 s under a 20 Hz sampler, 0.255 s at 10 Hz) with 0.05 W of
noise, so a pass that falls between two launches reads idle for a whole pass, as aifoundry3's board_w does
(2026-09-22-horace-aifoundry3); the SP's board average and the rail readings are first-order filtered (tau 1.05 s,
E58) and refresh with it; the die warms first-order (0.5 C/W, tau 20 s) and reads in whole degrees; the rails carry
fixed shares of the dynamic power and of the leakage's rise (the truth is the dynamic energy alone, what the
reducer's leakage corrections must leave, and the board's whole energy over the burst).
--card base is that card, whose laws are the reducer's own (the same leakage law, unit-gain filters with the tau the
reducer assumes, the launch edges exactly the host's, one slow thermal stage): a PLUMBING test, not a test of the
method. --card alt breaks each of those assumptions: another leakage law (20 W e^((T-80)/40): 0.27 W/C at 56 C,
aifoundry3's own idle curve, against the reducer's 0.33), 11-thermal-model.md's thermal chain (stages of 1.5 s and
4 s heat the die within the burst and let it cool within seconds of its end), the SP's board average with gain 1.01
and tau 0.8 s, the rails with tau 1.3 s, board_w one SP pass late (the reading shows the power a pass before it),
other rail shares, the idle die at 55.7 C instead of 55.3 C (the whole-degree reading's rounding the other way), and
the card's power starting 5 ms after the host's launch mark and ending 3 ms before its end mark (the truth's burst is
the card's own edges).
Nothing here is a measurement: the per-instance launch times are the 29 September card runs' (variant b), the watts
are guesses. The process names stay python3: no stub is ever mistaken for a device process (lib.sh matches _host$
and ettelem).
"""
import json
import math
import os
import random
import signal
import sys
import time

P_BASE, NOISE_W = 12.4, 0.05
LAG = 0.1           # the card is simulated 0.1 s behind real time, so a launch the host double records late still counts
RAIL_IDLE = {"minion_w": 5.5, "sram_w": 3.1, "noc_w": 2.4}
# the two simulated cards (module docstring): base = the reducer's own laws (plumbing), alt = each of them broken
CARDS = {
    # thermal: a Foster chain [(tau s, R C/W)]; base one stage, alt 11-thermal-model.md's chain (its 2,500 s stage left
    # out), whose fast stages heat the die within seconds and cool it within seconds of the burst's end
    "base": {"t_idle": 55.3, "a_leak_80": 23.257, "t_l": 36.0, "thermal": [(20.0, 0.5)], "tau_rail": 1.05, "tau_avg": 1.05, "avg_gain": 1.0,
             "board_lag_passes": 0, "edge_s": (0.0, 0.0),
             "rail_share": {"minion_w": 0.55, "sram_w": 0.12, "noc_w": 0.08},     # the rest is unmetered
             "leak_share": {"minion_w": 0.4, "sram_w": 0.3, "noc_w": 0.0}},       # of the leakage's rise
    # alt's law, 20 W e^((T-80)/40): 0.27 W/C at 56 C, aifoundry3's own idle curve (horace-aifoundry3
    # leakage_crosscard.json: 0.26-0.30 W/C at 55-57 C) against the reducer's 0.33
    "alt": {"t_idle": 55.7, "a_leak_80": 20.0, "t_l": 40.0, "thermal": [(1.5, 0.106), (4.0, 0.050), (60.0, 0.234), (150.0, 0.136), (400.0, 0.860)],
            "tau_rail": 1.3, "tau_avg": 0.8, "avg_gain": 1.01,
            "board_lag_passes": 1, "edge_s": (0.005, 0.003),
            "rail_share": {"minion_w": 0.62, "sram_w": 0.09, "noc_w": 0.05},
            "leak_share": {"minion_w": 0.5, "sram_w": 0.2, "noc_w": 0.05}},
}


def sp_pass_s(every_s):
    """E58 (aifoundry3): the SP's pass, 0.296 s under a 20 Hz sampler, 0.255 s at 10 Hz."""
    return 0.296 if every_s < 0.075 else 0.255
# (n, k, m, slice) -> launch seconds (card, variant b), model_s, guard_s, timeout_s, ops, candidates, dynamic W (a guess)
PRESETS = {
    (512, 4, 448, "0/1"): (0.130, 0.112832, 0.162196, 2, 81989040, 2829877120, 14.0),
    (512, 4, 1850, "0/1"): (0.429, 0.427446, 0.654487, 3, 339668880, 2829877120, 16.0),
    (256, 5, 1925, "0/2"): (0.958, 0.877802, 1.43574, 5, 654995125, 5063435554, 15.0),
    (256, 5, 1925, "1/2"): (1.589, 1.43964, 2.75858, 8, 575036887, 3746113502, 15.5),
}


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def preset(argv):
    key = (int(arg(argv, "--n", 32)), int(arg(argv, "--k", 3)), int(arg(argv, "--m", 128)), arg(argv, "--slice", "0/1"))
    return key, PRESETS.get(key, (0.05, 0.04, 0.06, 2, 1000000, 1000000, 10.0))


def read_sched(path):
    try:
        with open(path) as f:
            return [json.loads(l) for l in f if l.startswith("{")]
    except OSError:
        return []


# ---------------------------------------------------------------- the sampler double
def sample(argv):
    seconds = float(arg(argv, "--seconds", 10))
    every = int(arg(argv, "--every-ms", 100)) / 1000.0
    sched_path, truth_path = arg(argv, "--sched"), arg(argv, "--truth")
    card = arg(argv, "--card", "base")
    if card not in CARDS:
        print(f"energy_stub: --card {card}: base or alt", file=sys.stderr)
        return 2
    C = CARDS[card]
    A_LEAK_80, T_L, STAGES, T_IDLE = C["a_leak_80"], C["t_l"], C["thermal"], C["t_idle"]
    RAIL_SHARE, LEAK_SHARE = C["rail_share"], C["leak_share"]
    SP_PASS = sp_pass_s(every)
    e0, e1 = C["edge_s"]
    stop = {"flag": False}
    signal.signal(signal.SIGTERM, lambda *_: stop.update(flag=True))
    signal.signal(signal.SIGINT, lambda *_: stop.update(flag=True))
    rng = random.Random(7)
    t0 = time.time()
    sim_t = t0
    T = T_IDLE
    xs = [0.0] * len(STAGES)                     # the Foster chain's stages, over idle
    rails_f = dict(RAIL_IDLE)
    p_idle = P_BASE + A_LEAK_80 * math.exp((T_IDLE - 80.0) / T_L)
    bavg_f = p_idle                              # the PMIC's running average of the board
    bavg_r = C["avg_gain"] * bavg_f
    board_r, rails_r, T_r, next_sp = p_idle, dict(RAIL_IDLE), round(T_IDLE), t0
    lag_n = C["board_lag_passes"]
    board_hist = [p_idle] * (lag_n + 1)          # board power at the last lag_n + 1 passes
    sched, e_dyn, e_board = [], 0.0, 0.0
    dt = 0.005
    while not stop["flag"] and time.time() - t0 < seconds:
        tick = time.time()
        sched = read_sched(sched_path) if sched_path else []
        while sim_t < tick - LAG:                # advance the card to (just behind) now
            pd = sum(s["dp"] for s in sched if s["t0"] + e0 <= sim_t < s["t1"] - e1)
            e_dyn += pd * dt
            xs = [x + (r * pd - x) * (1 - math.exp(-dt / tau)) for x, (tau, r) in zip(xs, STAGES)]
            T = T_IDLE + sum(xs)
            p_now = P_BASE + A_LEAK_80 * math.exp((T - 80.0) / T_L) + pd
            if sched and sched[0]["t0"] + e0 <= sim_t < sched[-1]["t1"] - e1:
                e_board += p_now * dt            # the board's whole energy over the card's burst
            bavg_f += (p_now - bavg_f) * (1 - math.exp(-dt / C["tau_avg"]))
            dleak = A_LEAK_80 * (math.exp((T - 80.0) / T_L) - math.exp((T_IDLE - 80.0) / T_L))
            for k in rails_f:
                rails_f[k] += (RAIL_IDLE[k] + RAIL_SHARE[k] * pd + LEAK_SHARE[k] * dleak - rails_f[k]) * \
                    (1 - math.exp(-dt / C["tau_rail"]))
            if sim_t >= next_sp:                 # the service processor's pass refreshes the readings
                board_hist = board_hist[1:] + [p_now + rng.gauss(0, NOISE_W)]
                board_r = board_hist[0]          # lag_n passes late
                rails_r = dict(rails_f)
                bavg_r = C["avg_gain"] * bavg_f
                T_r = int(round(T))
                next_sp += SP_PASS
            sim_t += dt
        ms = int(tick * 1000)
        line = {"t_ms": ms, "took_ms": 22, "since_reset_ms": -1, "board_w": round(board_r, 2),
                "sp": {"board_avg_w": round(bavg_r, 2), "board_min_w": 0, "board_max_w": 0,
                       **{k: [round(v, 3), round(v, 3), round(v, 3)] for k, v in rails_r.items()},
                       "minion_mv": [499, 499, 499], "sram_mv": [750, 750, 750], "noc_mv": [750, 750, 750],
                       "minion_c": [T_r, T_r, T_r], "system_c": [T_r, T_r, T_r], "minion_mhz": [600, 600, 600],
                       "noc_mhz": [1000, 1000, 1000]},
                "temp_c": {"pmic": 45, "ioshire": [T_r, T_r, T_r], "minshire": [T_r, T_r - 1, T_r + 1]},
                "die_mv": {"ddr": 767, "sram": 750, "maxion": 750, "minion": 499, "pshire": 750, "noc": 750, "ioshire": 750},
                "reg_mv": {"ddr": 800, "sram": 750, "maxion": 750, "minion": 500, "noc": 750, "pcie_logic": 800,
                           "vddq": 1100, "vddqlp": 600},
                "mhz": {"minion": 600, "noc": 1000, "ddr": 1600}}
        print(json.dumps(line, separators=(",", ":")), flush=True)
        time.sleep(max(0.0, tick + every - time.time()))
    if truth_path:
        launches = [s for s in sched]
        reps = len(launches)
        truth = {"reps": reps, "card": card, "board_dyn_j": e_dyn,
                 "board_dyn_j_per_solve": e_dyn / reps if reps else None,
                 "board_total_j_per_solve": e_board / reps if reps else None,
                 "rails_dyn_j_per_solve": {k: RAIL_SHARE[k] * e_dyn / reps for k in RAIL_SHARE} if reps else None,
                 "unmetered_dyn_j_per_solve": (1 - sum(RAIL_SHARE.values())) * e_dyn / reps if reps else None,
                 "burst": [launches[0]["t0"] + e0, launches[-1]["t1"] - e1] if reps else None,
                 "model": {"p_base_w": P_BASE, "sp_pass_s": SP_PASS,
                           "every_s": every, **{k: v for k, v in C.items()}}}
        with open(truth_path, "w") as f:
            json.dump(truth, f, indent=1)
    return 0


# ---------------------------------------------------------------- the host double
def host(argv):
    t_proc = time.time()
    key, (launch, model, guard, timeout_plan, ops, cand, dp) = preset(argv)
    n, k, m, sl = key
    reps = int(arg(argv, "--reps", 1))
    budget = float(arg(argv, "--budget", 9.0))
    sched_path = arg(argv, "--sched")
    time.sleep(0.12)                             # instance, plan, model
    print(f"sparseparity tensor n={n} k={k} m={m} slice={sl} model={model} s (energy_stub host)", file=sys.stderr)
    if "--dry" in argv:
        print(json.dumps({"workload": "sparseparity", "device": "none", "n": n, "k": k, "m": m, "slice": sl,
                          "model_s": model, "est_s": 1.3 * model, "guard_s": guard, "timeout_s": timeout_plan,
                          "ops": ops, "refused_on_silicon": guard > 4.0, "status": "DRY", "stub": True}))
        return 0
    time.sleep(0.18)                             # the device open
    open_s, setup_s = 0.18, 0.0015
    launches, e0, e1, stop = [], 0, 0, ""
    for r in range(reps):
        elapsed = time.time() - t_proc
        to_s = math.floor(min(timeout_plan, budget - elapsed - 0.5))
        if to_s < 1 or to_s < 1.25 * guard + 0.5:
            stop = f"stopped after {r} launch(es): {budget - elapsed:.3f} s left before --budget"
            print(stop, file=sys.stderr)
            break
        time.sleep(0.002)                        # clear the records
        a = time.time()
        if r == 0:
            e0 = int(a * 1000)
        d = launch * (1 + random.Random(r).uniform(-0.003, 0.003))
        if sched_path:
            with open(sched_path, "a") as f:
                f.write(json.dumps({"t0": a, "t1": a + d, "dp": dp}) + "\n")
        time.sleep(max(0.0, a + d - time.time()))
        launches.append(time.time() - a)
        e1 = int(time.time() * 1000)
        time.sleep(0.002)                        # read the records back
    held = time.time() - t_proc - 0.12
    burst_s = (e1 - e0) / 1000.0 if launches else 0.0
    print(f"device open {open_s} s, load+copy-in {setup_s} s, held {held} s", file=sys.stderr)
    rec = arg(argv, "--records-out")
    if rec:
        open(rec, "wb").write(b"\0" * 64)
    time.sleep(0.3)                              # the checks
    done = len(launches)
    ok = done == reps
    problems = [] if ok else [f"reps: {done} of {reps} done"]
    j = {"workload": "sparseparity", "device": "silicon", "mode": "tensor", "stub": True,
         "m4": {"variant": arg(argv, "--variant", "m4"), "kernel": "m1" if arg(argv, "--variant") == "m1" else "m4",
                "gen": arg(argv, "--gen", "m1"), "cost": arg(argv, "--cost", "fit")},
         "instance": {"n": n, "k": k, "eta": float(arg(argv, "--eta", 0.1)), "m": m, "seed": int(arg(argv, "--seed", 1)),
                      "hash": f"stub{n}.{k}.{m}.{arg(argv, '--seed', 1)}"},
         "plan": {"slice": sl, "coverage": "full" if sl == "0/1" else "partial", "ops": ops, "candidates": cand,
                  "model_s": model, "guard_s": guard, "timeout_s": timeout_plan, "minions": 1024},
         "open_s": open_s, "setup_s": setup_s, "launch_s": launches, "launch_epoch_ms": [e0, e1],
         "reps_requested": reps, "reps_done": done, "reps_consistent": "ok", "stop_reason": stop,
         "device_held_s": held, "kernel": {"cycles_max": int(launches[-1] * 600e6) if launches else 0,
                                           "clock_mhz_est": 600.0 if launches else 0},
         "result": {"solved": True, "unique": True}, "checks": {"records": "ok", "launch": "ok"},
         "problems": problems, "launch_error": "",
         # a host that spins one core through the burst (the real host's runtime polls): a made-up figure
         "host_cpu_s": {"burst": [0.95 * burst_s, 0.05 * burst_s], "process": [0.95 * burst_s + 0.4, 0.05 * burst_s + 0.1],
                        "note": "stub: one core busy through the burst (assumed)"},
         "process_s": time.time() - t_proc,
         "status": "PASS" if ok else "FAIL"}
    print(json.dumps(j, separators=(",", ":")))
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("sample", "host"):
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(sample(sys.argv[2:]) if sys.argv[1] == "sample" else host(sys.argv[2:]))
