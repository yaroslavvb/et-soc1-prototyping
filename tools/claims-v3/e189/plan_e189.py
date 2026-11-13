#!/usr/bin/env python3
"""E189's session plan: launches a burst (K), the pass order, the card-minute arithmetic, the window, the stops.

    python3 -I -B tools/claims-v3/e189/plan_e189.py            # writes plan-e189.json beside this file
    python3 -I -B tools/claims-v3/e189/plan_e189.py --check    # recomputes and compares byte for byte

Everything here is arithmetic on the frozen forecast (forecast-e189.json) and on the two hosts' own guard rules
(workloads/ledger/host/main.cpp modelSeconds() and its launch rule; workloads/sparseparity/energy.sh's fit rule). The
order is a seeded shuffle written out in full: the kit's runner reads the list and never shuffles. Standard library
only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 189
ORDER = ["copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled", "sparse-parity"]
GiB = 1 << 30
LEDGER_BUDGET_S, TARGET_S, GAP_S = 9.5, 6.0, 0.010
# the set-up before a burst's first launch and the host's work after its last (estimates, stated: Q166 verify-progs
# for the copy and SHA-256; the sort's inputs are 4 MiB)
SETUP_S = {"copy-zeros": 1.5, "copy-random": 1.5, "sha256": 0.4, "sort-sorted": 0.3, "sort-shuffled": 0.3}
AFTER_S = {"copy-zeros": 1.0, "copy-random": 1.0, "sha256": 0.3, "sort-sorted": 0.2, "sort-shuffled": 0.2}
SPP_BUDGET_S, SPP_FIRST_S, SPP_PER_EXTRA_S = 9.0, 0.6, 0.006
ARGS = {
    "copy-zeros": "--prog copy --bytes 1G --passes 14 --data zeros --width 32",
    "copy-random": "--prog copy --bytes 1G --passes 14 --data random --width 32",
    "sha256": "--prog sha256 --block 2048 --repeat 800 --expect docs/reports/data/2026-11-12-q166-progs/digests/"
              "expect-card-b2048-r800.txt",
    "sort-sorted": "--prog sort --keys 512 --reps 1800 --order sorted",
    "sort-shuffled": "--prog sort --keys 512 --reps 1800 --order shuffled",
    "sparse-parity": "--mode tensor --shires 0xffffffff --per-shire 32 --n 544 --k 4 --eta 0.39 --m 1792 --seed 3 "
                     "--variant m1 --cost fit --gen inc --oracle sample --oracle-work 3e8 --budget 9",
}


def guard_model(key):
    """workloads/ledger/host/main.cpp modelSeconds(), for the registered configurations."""
    if key.startswith("copy"):
        return GiB * 14 * 2.0 / 20e9
    if key == "sha256":
        return (800 * (2048 // 64) + 1) * 4500.0 / (0.25 * 600e6)
    return 1800 * 512 * (20.0 * math.log2(512) + 6.0) / (0.25 * 600e6)


def plan(fc):
    out = {"schema": "e189-plan/1", "seed": SEED, "configs": {}}
    for key in ORDER:
        s = fc["configs"][key]["seconds"]
        pt, hi = s["point"], s["band"][1]
        if key == "sparse-parity":
            guard = fc["configs"][key]["plan"]["guard_s"]
            need = math.ceil(max(1.0, 1.25 * guard + 0.5) - 1e-9)
            last = SPP_BUDGET_S - 0.5 - need
            fit = max(0, math.floor((last - 0.15 - SPP_FIRST_S) / (hi + SPP_PER_EXTRA_S)) + 1)
            want = max(1, round(TARGET_S / (pt + SPP_PER_EXTRA_S)))
            k = min(fit, want)
            out["configs"][key] = {
                "host": "workloads/sparseparity build (kernel .text 3e14be32...), through E189's own runner",
                "args": ARGS[key], "launches_K": k, "reps_flag": f"--reps {k}",
                "rule": "energy.sh's fit rule at the band's slow end: the host starts a launch only while "
                        "floor(min(timeout, budget - elapsed - 0.5)) >= max(1, 1.25 guard + 0.5)",
                "guard_s": guard, "need_s": need, "last_start_s": last, "first_s": SPP_FIRST_S,
                "fit_at_slow_end": fit, "want_at_point": want,
                "burst_s_at_point": k * (pt + SPP_PER_EXTRA_S), "burst_s_at_slow_end": k * (hi + SPP_PER_EXTRA_S)}
            continue
        model = guard_model(key)
        s0 = SETUP_S[key]
        last_start = LEDGER_BUDGET_S - model - 0.5
        k_guard = max(0, math.floor((last_start - s0) / (hi + GAP_S) + 1e-9) + 1)
        k_target = max(1, round(TARGET_S / (pt + GAP_S)))
        k = min(k_guard, k_target)
        end_hi = s0 + k * (hi + GAP_S) + AFTER_S[key]
        out["configs"][key] = {
            "host": "workloads/ledger build (kernel .text 5e00e45a...), --card, through E189's own runner",
            "args": ARGS[key] + f" --launches {k}", "launches_K": k,
            "rule": "main.cpp: a launch starts only while 9.5 s - elapsed >= the guard's model + 0.5 s; K = the most "
                    "that start at the band's slow end, capped at energy.sh's 6 s target at the point",
            "guard_model_s": model, "setup_s": s0, "last_start_s": last_start, "k_guard_at_slow_end": k_guard,
            "k_target_at_point": k_target, "burst_s_at_point": k * (pt + GAP_S), "burst_s_at_slow_end": k * (hi + GAP_S),
            "process_end_s_at_slow_end": end_hi, "process_end_under_10_s": end_hi < 10.0}
    # the order: four rounds, each configuration once a round, shuffled within the round by the fixed seed
    rng = random.Random(SEED)
    rounds = []
    for r in range(4):
        x = list(ORDER)
        rng.shuffle(x)
        rounds.append(x)
    seq = ["stop-path test", "smoke (ramped)", "idle anchor 1 (2 min)"]
    idx = 0
    for r, x in enumerate(rounds, start=1):
        for key in x:
            idx += 1
            seq.append(f"pass {idx}: {key} p{r}")
        if r == 2:
            seq.append("idle anchor 2 (2 min)")
    seq += ["idle anchor 3 (2 min)", "the counters arm (6 launches; only if its desk test passed; REPORTED)",
            "the closing reads (ettelem config: TDP and threshold), release"]
    out["order"] = {"rounds": rounds, "sequence": seq,
                    "rule": "four independent passes a configuration, one host process each; each round holds every "
                            "configuration once, shuffled by random.Random(189); written out here, never re-drawn"}
    per_pass_min_s = {k: 8.0 + (SETUP_S.get(k, SPP_FIRST_S) + v["burst_s_at_point"] + AFTER_S.get(k, 0.5)) + 10.0 + 3.0 + 5.0
                      for k, v in out["configs"].items()}
    passes_min = 4 * sum(per_pass_min_s.values()) / 60.0
    out["card_minutes"] = {
        "a_checks_look_dry_stoppath_smoke": 12, "b_three_idle_anchors": 6, "c_24_passes": 50, "d_counters_arm": 6,
        "e_margin": 20, "total": 12 + 6 + 50 + 6 + 20, "cap": 110,
        "c_arithmetic": {"per_pass_without_the_die_gate_s": per_pass_min_s, "24_passes_without_the_gate_min": passes_min,
                         "die_gate_and_sampler_retries_allowance_min": 50 - passes_min,
                         "how": "a pass = 8 s idle + the host process (set-up, K launches, its checks) + 10 s idle + the "
                                "sampler's start and stop (3 s) + bookkeeping (5 s); the rest of the 50 minutes is "
                                "the die gate's waits (heat carries over) and the sampler's retries"},
        "rule": "about 95 card-minutes, cap 110: no pass starts after 108 card-minutes from the first card command; "
                "the session ends by 110"}
    out["window"] = {
        "alone": "from his go at G (a fresh approval in hand): last start G+1:30, last end G+3:30, inside one Pacific "
                 "day and at least 30 minutes before the approval lapses; the post 'for 2 h'",
        "after_E183": "E183 first (its own window, G+1:15 / G+2:30); E189's first card command at least 40 minutes "
                      "after E183's session end (or after that run's latest file write, if it ended without "
                      "'session end'); E189's last start G+3:00, last end G+5:00; the day's ONE post 'for 4 h'",
        "one_session": "never two sessions of ours on aifoundry3 at once"}
    out["die_gate"] = {"rule": "a pass starts only when minshire[0] reads 60 C or less (waits up to 10 minutes, then the "
                               "pass is skipped, no data); a die below 52 C does not block (the pass is scored given "
                               "its own T0 and labelled 'T0 below the forecast band')", "band_c": [52, 60]}
    out["stops"] = {"board_w": 65.0, "minshire0_c": 70.0,
                    "rule": "a live sample at or above 65 W board or 70 C on minshire[0] ends the queue: the running "
                            "process finishes (never killed), no further pass starts, the closing reads, release",
                    "clock": "every sample must read 600 MHz: the first sample off it sets its pass aside; a second "
                             "one (any pass) stops the session"}
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    fc = json.load(open(os.path.join(HERE, "forecast-e189.json")))
    js = json.dumps(plan(fc), indent=1, sort_keys=True) + "\n"
    if a.check:
        same = open(os.path.join(HERE, "plan-e189.json")).read() == js
        print("PLAN CHECK " + ("PASS" if same else "FAIL"))
        return 0 if same else 1
    open(os.path.join(HERE, "plan-e189.json"), "w").write(js)
    p = json.loads(js)
    for k, v in p["configs"].items():
        print(f"{k:14s} K {v['launches_K']:2d}  burst {v['burst_s_at_point']:.2f} s at the point, "
              f"{v['burst_s_at_slow_end']:.2f} s at the slow end")
    print("card-minutes", p["card_minutes"]["total"], "cap", p["card_minutes"]["cap"],
          "; 24 passes without the gate %.1f min" % p["card_minutes"]["c_arithmetic"]["24_passes_without_the_gate_min"])
    for r in p["order"]["rounds"]:
        print("round:", ", ".join(r))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
