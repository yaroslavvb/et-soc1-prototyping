#!/usr/bin/env python3
"""E194's stub card for the scorer's self-test (score_e194.py --selftest-stub): a day's data folder made with no device.

Each pass is energy.sh's form (idle 8 s, ONE burst of K launches, idle 10 s) on a simulated card in SIMULATED time, with
workloads/sparseparity/tools/energy_stub.py's 'alt' laws, the ones that break the reducer's own: another leakage law
(20 W e^((T-80)/40)), 11-thermal-model.md's thermal chain, the SP's board average with gain 1.01 and tau 0.8 s, the
rails with tau 1.3 s, board_w a pass late, the idle die at 55.7 C, the card's power 5 ms after the host's launch mark
and 3 ms before its end. Only the base power differs from energy_stub.py: it is set so the card's idle equals the
ledger's idle law for aifoundry2 (E194's card; E191's stub used card 1's, E189's aifoundry3's) at the die reading (so a
correct forecast can pass). E191's stub (tools/claims-v3/e191/stub_e191.py) with E194's card and E194's clock: the
sampler's minion clock reads 600 MHz at rest and through the governor's climb (the first 0.9 s of a burst unless a pass
says otherwise), 800 MHz from there to the burst's end; the hosts' cycles are their seconds at 800 MHz; scenario F
breaks THE CLOCK RULE three ways (E194.md 8.2). The telemetry, host.json, host-raw.json, run.json and pass.json follow
E194.md section 8.1; the reducer (energy_reduce.py, unchanged) then writes energy.json.

The injected energy is chosen per scenario from the frozen forecast itself: dynamic power p during each launch of d s
so that p (d - 5 ms - 3 ms) = the forecast's given-seconds J over idle at t_k = d (times the scenario's factor).
Nothing here is a measurement. SPDX-License-Identifier: Apache-2.0
"""
import gzip
import importlib.util
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
F_HZ = 800e6         # E194's clock: the hosts' cycles are their seconds at 800 MHz
CLIMB_S = 0.9        # the stub's governor climb from 600 to 800 MHz (E190 arm A's median, 0.852 s, rounded up)
EVERY = 0.1
GAP = 0.004          # the host's record clear and readback between launches (energy_stub's 2 ms + 2 ms)
IDLE_BEFORE, IDLE_AFTER, SETUP = 8.0, 10.0, 0.5
K = {"copy-zeros": 8, "copy-random": 8, "sha256": 9, "sort-sorted": 8, "sort-shuffled": 7, "sparse-parity": 9}
ALL = ["copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled", "sparse-parity"]

# Each scenario: per configuration a list of passes {factor: injected energy over the forecast, slow: seconds over the
# point, short: launches done (else K), set_aside}; and the verdicts expected, stated before the run.
SCENARIOS = [
    {"name": "A-as-forecast", "what": "every configuration, 4 passes, at the forecast's point seconds and energy",
     "passes": {k: [{}] * 4 for k in ALL},
     "expect": {"verdicts": {"E194-S1": "PASS", "E194-S1T": "PASS", "E194-S2": "PASS", "E194-S2T": "PASS"}}},
    {"name": "B-two-energies-off", "what": "copy-random and sha256 add 25% more energy over idle than forecast; at "
                                           "aifoundry2's 800 MHz shares (J over idle 30% and 25% of J with the card at "
                                           "rest) the same excess moves J with the card at rest by about 7.5% and 6.2%, "
                                           "beyond S1T's 5%, so S1T fails too (E191's card 1, with its larger rest, "
                                           "kept it under 5%; E194.md 8.5 states the correction of this expectation)",
     "passes": dict({k: [{}] * 2 for k in ALL}, **{"copy-random": [{"factor": 1.25}] * 2, "sha256": [{"factor": 1.25}] * 2}),
     "expect": {"verdicts": {"E194-S1": "FAIL", "E194-S1T": "FAIL", "E194-S2": "PASS", "E194-S2T": "PASS"}}},
    {"name": "C-a-failed-build", "what": "sort-shuffled has no pass (a failed build: no data); the rest as forecast",
     "passes": dict({k: [{}] * 2 for k in ALL}, **{"sort-shuffled": []}),
     "expect": {"verdicts": {"E194-S1": "PASS", "E194-S1T": "PASS", "E194-S2": "PASS", "E194-S2T": "PASS"},
                "no_data": ["sort-shuffled"]}},
    {"name": "D-two-slow", "what": "sort-sorted and sparse parity run 30% longer than the point; their energy follows "
                                   "the given-seconds forecast (so score 1 holds, score 2 does not)",
     "passes": dict({k: [{}] * 2 for k in ALL}, **{"sort-sorted": [{"slow": 1.30}] * 2, "sparse-parity": [{"slow": 1.30}] * 2}),
     "expect": {"verdicts": {"E194-S1": "PASS", "E194-S1T": "PASS", "E194-S2": "FAIL", "E194-S2T": "FAIL"}}},
    {"name": "E-short-and-set-aside", "what": "copy-zeros' first pass cut short by the budget (6 of 8 launches, scored, "
                                              "flagged); sparse parity's passes set aside by the runner but one (a "
                                              "pass off 800 MHz after its climb: NO DATA)",
     "passes": dict({k: [{}] * 2 for k in ALL}, **{"copy-zeros": [{"short": 6}, {}],
                                                    "sparse-parity": [{"set_aside": "a pass off 800 MHz after its climb"}] * 3
                                                    + [{}]}),
     "expect": {"verdicts": {"E194-S1": "PASS", "E194-S1T": "PASS", "E194-S2": "PASS", "E194-S2T": "PASS"},
                "no_data": ["sparse-parity"], "short_flagged": ["copy-zeros"]}},
    {"name": "F-the-clock-rule", "what": "THE CLOCK RULE (E194.md 8.2): copy-zeros p1 steps to 700 MHz 2.5 s into its "
                                         "burst (set aside), p2 climbs late, at 1.4 s (counts), p3 stays at 600 MHz "
                                         "throughout (set aside: the reducer passes it, the rule does not), p4 as "
                                         "forecast; sparse parity p1's last launch ran at 600 MHz by its own count "
                                         "(set aside), p2 and p3 as forecast; the rest as forecast",
     "passes": dict({k: [{}] * 2 for k in ALL}, **{"copy-zeros": [{"clock": "step700"}, {"climb_s": 1.4},
                                                                  {"clock": "all600"}, {}],
                                                    "sparse-parity": [{"last_launch_mhz": 600.0}, {}, {}]}),
     "expect": {"verdicts": {"E194-S1": "PASS", "E194-S1T": "PASS", "E194-S2": "PASS", "E194-S2T": "PASS"},
                "set_aside_by_the_clock": ["copy-zeros/p1", "copy-zeros/p3", "sparse-parity/p1"]}},
]


def _mod(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def simulate(path, lo, d, n, p_dyn, t_end, F, LV, seed, clock=None):
    """Telemetry at 10 Hz from t = 0 to t_end (s, simulated), launches at lo + i (d + GAP), i < n, power p_dyn; the
    minion clock 600 MHz at rest and in the climb, 800 MHz from lo + climb_s to the burst's end (clock: a pass's spec)."""
    clock = clock or {}
    climb = clock.get("climb_s", CLIMB_S)
    ES = _mod("energy_stub_e194", "workloads/sparseparity/tools/energy_stub.py")
    C = ES.CARDS["alt"]
    a80, tl, stages, t_idle = C["a_leak_80"], C["t_l"], C["thermal"], C["t_idle"]
    law_idle = LV.idle_w(F, "aifoundry2", float(round(t_idle)))[0]  # aifoundry2's idle law (E194)
    p_base = law_idle / C["avg_gain"] - a80 * math.exp((t_idle - 80.0) / tl)
    sp_pass = ES.sp_pass_s(EVERY)
    e0, e1 = C["edge_s"]
    launches = [(lo + i * (d + GAP), lo + i * (d + GAP) + d) for i in range(n)]
    rng = random.Random(seed)
    dt = 0.005
    T, xs = t_idle, [0.0] * len(stages)
    rails_f = dict(ES.RAIL_IDLE)
    p_idle = p_base + a80 * math.exp((t_idle - 80.0) / tl)
    bavg_f = p_idle
    board_hist = [p_idle] * (C["board_lag_passes"] + 1)
    board_r, rails_r, bavg_r, T_r, next_sp = p_idle, dict(ES.RAIL_IDLE), C["avg_gain"] * p_idle, round(t_idle), 0.0
    lines, sim, next_sample, e_dyn = [], 0.0, 0.0, 0.0
    t0_ms = 1_800_000_000_000
    while sim < t_end:
        pd = p_dyn if any(a + e0 <= sim < b - e1 for a, b in launches) else 0.0
        e_dyn += pd * dt
        xs = [x + (r * pd - x) * (1 - math.exp(-dt / tau)) for x, (tau, r) in zip(xs, stages)]
        T = t_idle + sum(xs)
        p_now = p_base + a80 * math.exp((T - 80.0) / tl) + pd
        bavg_f += (p_now - bavg_f) * (1 - math.exp(-dt / C["tau_avg"]))
        dleak = a80 * (math.exp((T - 80.0) / tl) - math.exp((t_idle - 80.0) / tl))
        for k in rails_f:
            rails_f[k] += (ES.RAIL_IDLE[k] + C["rail_share"][k] * pd + C["leak_share"][k] * dleak - rails_f[k]) * \
                (1 - math.exp(-dt / C["tau_rail"]))
        if sim >= next_sp:
            board_hist = board_hist[1:] + [p_now + rng.gauss(0, ES.NOISE_W)]
            board_r, rails_r, bavg_r, T_r = board_hist[0], dict(rails_f), C["avg_gain"] * bavg_f, int(round(T))
            next_sp += sp_pass
        if sim >= next_sample - 1e-9:
            busy = lo + climb <= sim <= launches[-1][1]
            mhz = 800 if busy else 600
            if clock.get("clock") == "all600":
                mhz = 600
            elif clock.get("clock") == "step700" and busy and sim >= lo + 2.5:
                mhz = 700
            lines.append({"t_ms": t0_ms + int(round(sim * 1000)), "took_ms": 22, "since_reset_ms": -1,
                          "board_w": round(board_r, 2),
                          "sp": {"board_avg_w": round(bavg_r, 2), **{k: [round(v, 3)] * 3 for k, v in rails_r.items()}},
                          "temp_c": {"minshire": [T_r, T_r - 1, T_r + 1]}, "mhz": {"minion": mhz}})
            next_sample += EVERY
        sim += dt
    with gzip.open(path, "wt") as f:
        for ln in lines:
            f.write(json.dumps(ln, separators=(",", ":")) + "\n")
    return t0_ms, launches, e_dyn


def make_pass(d, key, k, spec, rec, F, LV, FC, ER):
    os.makedirs(d, exist_ok=True)
    point = rec["seconds"]["point"]
    dur = point * spec.get("slow", 1.0)
    n_req = K[key]
    n = spec.get("short", n_req)
    C_edges = (0.005, 0.003)
    g = FC.given(rec, dur, dur + GAP, 56.0, F, LV)
    p_dyn = spec.get("factor", 1.0) * g["j_over_idle"] / (dur - C_edges[0] - C_edges[1])
    lo = IDLE_BEFORE + SETUP
    hi_end = lo + n * (dur + GAP) - GAP
    t_end = hi_end + IDLE_AFTER
    t0_ms, launches, e_dyn = simulate(os.path.join(d, "telemetry.jsonl.gz"), lo, dur, n, p_dyn, t_end, F, LV,
                                      seed=100 * ALL.index(key) + k, clock=spec)
    ms = lambda s: t0_ms + int(round(s * 1000))  # noqa: E731
    short = n < n_req
    launch_s = [dur] * n
    if spec.get("last_launch_mhz"):         # the last launch's own count: the same cycles at a lower clock
        launch_s[-1] = dur * F_HZ / (spec["last_launch_mhz"] * 1e6)
    host = {"status": "FAIL" if short else "PASS", "reps_requested": n_req, "reps_done": n, "reps_consistent": "ok",
            "launch_s": launch_s, "launch_epoch_ms": [ms(launches[0][0]), ms(launches[-1][1])],
            "problems": [f"reps: {n} of {n_req} done"] if short else [], "stop_reason": "budget" if short else "",
            "host_cpu_s": {"burst": [0.95 * (hi_end - lo), 0.05 * (hi_end - lo)]}, "stub": True}
    if key == "sparse-parity":
        host.update({"kernel": {"cycles_max": int(round(dur * F_HZ))}, "result": {"solved": True, "unique": True},
                     "instance": {"n": 544, "k": 4, "eta": 0.39, "m": 1792, "seed": 3, "hash": "stub"},
                     "plan": {"slice": "0/1"}})
    else:
        P = 2048
        raw = {"ledger": 1, "participants": P, "records_ok": P, "records_bad": 0, "mismatches": 0, "checked": P,
               "expect_checked": P if key == "sha256" else 0, "expect_mismatches": 0, "units": 1, "units_expected": 1,
               "launches": n, "wall_s": launch_s, "hart0_cycles": {"max": int(round(dur * F_HZ))},
               "status": "FAIL" if short else "PASS", "stub": True}
        with open(os.path.join(d, "host-raw.json"), "w") as f:
            f.write(json.dumps(raw) + "\n")
    with open(os.path.join(d, "host.json"), "w") as f:
        f.write(json.dumps(host) + "\n")
    json.dump({"host_t0_ms": ms(IDLE_BEFORE), "host_t1_ms": ms(hi_end + 0.3), "dry": True, "foreign": None, "host_rc": 0},
              open(os.path.join(d, "run.json"), "w"))
    json.dump({"config": key, "pass": k, "order_index": None, "launches_requested": n_req,
               "set_aside": spec.get("set_aside"), "stub": True, "injected_j_over_per_launch": e_dyn / n},
              open(os.path.join(d, "pass.json"), "w"))
    r = ER.reduce_dir(d)
    json.dump(ER.rnd(r, 5), open(os.path.join(d, "energy.json"), "w"), indent=1)


def make_day(d, sc, fc, F, LV, FC):
    ER = _mod("energy_reduce_e194", "workloads/sparseparity/tools/energy_reduce.py")
    for key in ALL:
        for k, spec in enumerate(sc["passes"].get(key, []), start=1):
            make_pass(os.path.join(d, "passes", key, f"p{k}"), key, k, spec, fc["configs"][key], F, LV, FC, ER)
