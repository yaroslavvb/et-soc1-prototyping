#!/usr/bin/env python3
"""E194's session plan: launches a burst (K), the pass order, the card-minute arithmetic, the card, the window, the die
gate, the stops, the clock rule and the predicted peaks.

    /usr/bin/python3 -I -B tools/claims-v3/e194/plan_e194.py            # writes plan-e194.json beside this file
    /usr/bin/python3 -I -B tools/claims-v3/e194/plan_e194.py --check    # recomputes and compares byte for byte

E191's plan code (tools/claims-v3/e191/plan_e191.py, sha256 3bc1a4ec..., in E191's registration list e458fa82...), itself
E189's with E191's seed and card, with E194's seed (194), its own forecast file and aifoundry2's card, window, die gate,
stops, clock rule and peaks (E194.md sections 9-13). The configurations, their arguments and E189.md 4's launches a burst
(K) are E189's, unchanged: at 800 MHz the K rule would give more launches (it is computed and reported, not used), and
the bursts are E189's, shorter. The card-minute arithmetic and the cap are E189's.
Everything here is arithmetic on the frozen forecast (forecast-e194.json) and on the two hosts' own guard rules
(workloads/ledger/host/main.cpp modelSeconds() and its launch rule; workloads/sparseparity/energy.sh's fit rule). The
order is a seeded shuffle written out in full: the kit's runner reads the list and never shuffles. It refuses (exit 3)
if the predicted board peak at the bands' top, with E136's base at 800 MHz added, passes aifoundry2's 82 W line.
Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SEED = 194
ORDER = ["copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled", "sparse-parity"]
GiB = 1 << 30
LEDGER_BUDGET_S, TARGET_S, GAP_S = 9.5, 6.0, 0.010
# the set-up before a burst's first launch and the host's work after its last (estimates, stated: Q166 verify-progs
# for the copy and SHA-256; the sort's inputs are 4 MiB)
SETUP_S = {"copy-zeros": 1.5, "copy-random": 1.5, "sha256": 0.4, "sort-sorted": 0.3, "sort-shuffled": 0.3}
AFTER_S = {"copy-zeros": 1.0, "copy-random": 1.0, "sha256": 0.3, "sort-sorted": 0.2, "sort-shuffled": 0.2}
SPP_BUDGET_S, SPP_FIRST_S, SPP_PER_EXTRA_S = 9.0, 0.6, 0.006
# E189.md section 4's launches a burst, kept (E194.md section 4)
K_E189 = {"copy-zeros": 8, "copy-random": 8, "sha256": 9, "sort-sorted": 8, "sort-shuffled": 7, "sparse-parity": 9}
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
LINE_W = 82.0                             # aifoundry2's predicted-peak line (E190.md section 3, arm A)
CLIMB_S = 1.5                             # the clock rule's allowance for the governor's climb (E194.md section 11)
DIE_GATE_C = 57.0                         # E194's die gate (E194.md section 11), stricter than E189's 60 C


def guard_model(key):
    """workloads/ledger/host/main.cpp modelSeconds(), for the registered configurations (the host's own constants)."""
    if key.startswith("copy"):
        return GiB * 14 * 2.0 / 20e9
    if key == "sha256":
        return (800 * (2048 // 64) + 1) * 4500.0 / (0.25 * 600e6)
    return 1800 * 512 * (20.0 * math.log2(512) + 6.0) / (0.25 * 600e6)


def peaks(fc):
    """Predicted board peaks (E190.md section 3's form), from the frozen forecast and the frozen ledger's own laws: at the
    points, aifoundry2's idle law at the forecast die plus the largest W over idle with its own rise; at the bands' top,
    the idle law at the die band's top plus its rest band (0.5 W) plus the largest W over idle a band allows (the dearest
    J over idle at a seconds band's end over that end's seconds) plus that power's rise at the bands' tops (k_leak at the
    die band's top x 1.25 x 0.20 C a W); and both again with E136's base difference at 800 MHz added (the frozen ledger
    has no such term)."""
    sys.path.insert(0, os.path.join(REPO, "tools", "ledger"))
    import ledger_v2 as LV  # noqa: E402  (the frozen ledger's laws; pinned by forecast_e194.py)
    F = LV.load_frozen(os.path.join(REPO, "docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json"))
    dB = fc["readings_reported"]["e136_base_w"]["difference_800_minus_600"]
    Ttop = fc["die_start_band_c"][1]
    pts, tops = {}, {}
    for k in ORDER:
        c = fc["configs"][k]
        t, (tlo, thi) = c["seconds"]["point"], c["seconds"]["band"]
        rest_w = c["terms"]["the card at rest"]["w"]
        heat_w = c["terms"]["the run's own leakage rise"]["j"] / t
        pts[k] = rest_w + c["w_over_idle"] + heat_w
        if "j_over_idle_band_at_band_ends" in c:
            b_lo, b_hi = c["j_over_idle_band_at_band_ends"]
            tops[k] = max(b_lo[1] / tlo, b_hi[1] / thi)
        else:
            tops[k] = c["j_over_idle_band"][1] / tlo
    w_top = max(tops.values())
    rest_top = LV.idle_w(F, "aifoundry2", Ttop)[0] + F["idle_laws"]["aifoundry2"]["rest_band_w"]
    rise_top = LV.leak_slope(F, "aifoundry2", Ttop) * F["leak_slope_band_rel"][1] * LV._cb(F, "k_rise_c_per_w")[1] * w_top
    p_pts = max(pts.values())
    p_top = rest_top + w_top + rise_top
    return {"line_w": LINE_W, "at_points_w": p_pts, "at_points_by_config_w": pts,
            "at_bands_top_w": p_top, "w_over_idle_band_top_by_config": tops, "rest_at_die_band_top_w": rest_top,
            "rise_at_bands_top_w": rise_top, "e136_base_difference_w": dB,
            "at_points_with_e136_base_w": p_pts + dB, "at_bands_top_with_e136_base_w": p_top + dB,
            "under_the_line": p_top + dB <= LINE_W,
            "how": "points: P_idle(55 C) + W over idle + its rise at the point; bands' top: P_idle(57 C) + 0.5 W + the "
                   "largest W over idle a band allows + its rise at k_leak(57 C) x 1.25 x 0.20 C a W; E136's base "
                   "difference (B(800) - B(600)) added to both as an outside term"}


def plan(fc):
    out = {"schema": "e194-plan/1", "seed": SEED, "configs": {}}
    for key in ORDER:
        s = fc["configs"][key]["seconds"]
        pt, hi = s["point"], s["band"][1]
        k = K_E189[key]
        if key == "sparse-parity":
            guard = fc["configs"][key]["plan"]["guard_s"]
            need = math.ceil(max(1.0, 1.25 * guard + 0.5) - 1e-9)
            last = SPP_BUDGET_S - 0.5 - need
            fit = max(0, math.floor((last - 0.15 - SPP_FIRST_S) / (hi + SPP_PER_EXTRA_S)) + 1)
            want = max(1, round(TARGET_S / (pt + SPP_PER_EXTRA_S)))
            out["configs"][key] = {
                "host": "workloads/sparseparity build (kernel .text 3e14be32...), through E194's runner (to be made "
                        "from E189's kit, with aifoundry2's clock rule)",
                "args": ARGS[key], "launches_K": k, "reps_flag": f"--reps {k}",
                "k_from": "E189.md section 4, kept (E194.md section 4)",
                "rule_e189": "energy.sh's fit rule at the band's slow end: the host starts a launch only while "
                             "floor(min(timeout, budget - elapsed - 0.5)) >= max(1, 1.25 guard + 0.5)",
                "guard_s": guard, "need_s": need, "last_start_s": last, "first_s": SPP_FIRST_S,
                "k_rule_at_e194_bands_reported": min(fit, want), "fit_at_slow_end": fit, "want_at_point": want,
                "all_k_start_at_slow_end": k <= fit,
                "burst_s_at_point": k * (pt + SPP_PER_EXTRA_S), "burst_s_at_slow_end": k * (hi + SPP_PER_EXTRA_S)}
            continue
        model = guard_model(key)
        s0 = SETUP_S[key]
        last_start = LEDGER_BUDGET_S - model - 0.5
        k_guard = max(0, math.floor((last_start - s0) / (hi + GAP_S) + 1e-9) + 1)
        k_target = max(1, round(TARGET_S / (pt + GAP_S)))
        end_hi = s0 + k * (hi + GAP_S) + AFTER_S[key]
        out["configs"][key] = {
            "host": "workloads/ledger build (kernel .text 5e00e45a...), --card, through E194's runner (to be made from "
                    "E189's kit, with aifoundry2's clock rule)",
            "args": ARGS[key] + f" --launches {k}", "launches_K": k,
            "k_from": "E189.md section 4, kept (E194.md section 4)",
            "rule_e189": "main.cpp: a launch starts only while 9.5 s - elapsed >= the guard's model + 0.5 s; E189's K = "
                         "the most that start at the band's slow end, capped at energy.sh's 6 s target at the point",
            "guard_model_s": model, "setup_s": s0, "last_start_s": last_start, "k_guard_at_slow_end": k_guard,
            "k_target_at_point": k_target, "k_rule_at_e194_bands_reported": min(k_guard, k_target),
            "all_k_start_at_slow_end": k <= k_guard,
            "burst_s_at_point": k * (pt + GAP_S), "burst_s_at_slow_end": k * (hi + GAP_S),
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
    seq += ["idle anchor 3 (2 min)", "the counters arm: not run (E189's kit dropped it, its KIT.md section 5)",
            "the closing reads (ettelem config: TDP, threshold, clock at rest), release"]
    out["order"] = {"rounds": rounds, "sequence": seq,
                    "rule": "four independent passes a configuration, one host process each; each round holds every "
                            "configuration once, shuffled by random.Random(194); written out here, never re-drawn"}
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
        "d_note": "E189's kit dropped the counters arm (its KIT.md section 5): its 6 card-minutes go unused",
        "rule": "about 95 card-minutes, cap 110 (E189's): no pass starts after 108 card-minutes from the first card "
                "command; the session ends by 110. The clock shortens every cycle-bound burst (x 600/800) and changes "
                "no step, so the estimate and the cap stand"}
    out["card"] = {"which": "aifoundry2 card 0 (the ledger's card 'aifoundry2'), its own governor as found; nothing set, "
                            "reads only; the box this round's orchestration runs on",
                   "select": "the box's one card: /dev/et0_mgmt and /dev/et0_ops",
                   "lock": "/run/lock/etsoc-shire0.lock, held for the session (flock -n)",
                   "config_read": "ettelem config through the kit's guard at the start and the end, holding the card's "
                                  "lock under timeout 10: expected TDP 65 W, threshold 65 C and 600 MHz at rest (as E190 "
                                  "arm A read it, Fri 13 Nov 2026: 65 W, 65 C, 600 MHz, 519 mV, low_power); a different "
                                  "TDP, threshold or rest clock at the start stops the session before its first launch "
                                  "(a gate: no data, and the governor is not touched); the end reading is reported",
                   "governor": "as found: under load it climbs to 800 MHz (the forecast's clock) while the shires' mean "
                               "is at most 65 C and the board's ~1 s average under the TDP; nothing of it is set, "
                               "reset or read beyond ettelem config and ettelem sample",
                   "processes": "one host process at a time on the card, under timeout 10"}
    out["window"] = {
        "alone": "from his go at G: last start G+1:30, last end G+3:30, inside one Pacific day (E189.md 13's form)",
        "post": "none: the owner's standing waiver, his words Sun 15 Nov 2026 10:22:36 PST, 'don't worry about discord "
                "post, just use the machines, nobody is using them'; every other etiquette check stays (et-who, who, "
                "uptime, ps before; the card's lock held for the run; timeout 10 a process)",
        "quiet_desk": "the session runs on the round's orchestrating box: from the look before step 0 to the copy-back, "
                      "the round's quiet-desk flag for aifoundry2 is held and no lane of ours starts on aifoundry2 a "
                      "process whose name matches _host$, ^ettelem$, ^dev_mngt_servi, ^et-powertop$, ^mmbench_launch or "
                      "^sys_emu$, nor a script named session_eNNN*.sh or queue_eNNN* (E190's card-lane brief, dated note "
                      "1, section 4: a stand-in or built host of another lane is read as a foreign holder and stops the "
                      "session)",
        "one_session": "never two sessions of ours on aifoundry2's card at once; the rest rule of E189's kit (40 "
                       "minutes after a session of ours on the same card) holds"}
    out["die_gate"] = {"rule": "a pass starts only when minshire[0] reads 57 C or less (waits up to 10 minutes, then the "
                               "pass is skipped, no data); a die below 46 C does not block (the pass is scored given its "
                               "own T0 and labelled 'T0 below the forecast band')", "band_c": [46, 57],
                       "gate_c": DIE_GATE_C,
                       "why": "stricter than E189's 60 C for the clock: the governor steps down when the shires' mean "
                              "passes 65 C; E136's burst law (die_max = die_start + 0.1445 (P - 21.5)) puts the "
                              "hottest burst's rise at about 5 C at its predicted board power with E136's base"}
    out["stops"] = {"board_w": 65.0, "minshire0_c": 70.0,
                    "rule": "E189's runner's lines: a live sample at or above 65 W board or 70 C on minshire[0] ends the "
                            "queue: the running process finishes (never killed), no further pass starts, the closing "
                            "reads, release",
                    "aifoundry2_lines": {"board_w_above": 85.0, "consecutive_samples": 3, "die_c": 80.0,
                                         "rule": "E190 arm A's lines on this card, kept beside E189's: board above 85 W "
                                                 "on 3 samples in a row, or the shires' mean or the latch minshire[2] "
                                                 "at or above 80 C, ends the queue the same way (E189's lines bind "
                                                 "first; minshire[2] read 70 C throughout E190 arm A, so it is never "
                                                 "read against the 70 C line)"},
                    "clock": "the governor's climb: in each burst the samples from its first launch's start + 1.5 s to "
                             "its last launch's end must read 800 MHz; the first pass with one off it is set aside; a "
                             "second such pass (any configuration) stops the session (the card is not at the forecast's "
                             "clock)"}
    out["clock_rule"] = {"forecast_mhz": 800, "climb_allowance_s": CLIMB_S,
                         "pass_counts_if": ["every busy sample (the reducer's window [lo + 0.5 s, hi]) at or after lo + "
                                            "1.5 s reads 800 MHz",
                                            "the burst's last launch ran at 800 MHz by its own count: its slowest "
                                            "minion's cycles over its wall seconds read 780-810 MHz"],
                         "t_k": "the last launch's slowest-minion cycles over 800 MHz",
                         "reducer_line": "the reducer's hard line 'minion clock in busy samples' is read by this rule, "
                                         "not as a failure; every other hard check stands",
                         "evidence": "E190 arm A (13 Nov 2026), 84 processes: the first 800 MHz sample came 0.014-1.325 "
                                     "s after the launch window's start (median 0.852 s); in its 12 burst processes no sample left "
                                     "800 MHz after it (desk/climb-e190.txt)"}
    out["peaks"] = peaks(fc)
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    fc = json.load(open(os.path.join(HERE, "forecast-e194.json")))
    p = plan(fc)
    js = json.dumps(p, indent=1, sort_keys=True) + "\n"
    if not p["peaks"]["under_the_line"]:
        print(f"REFUSED: the predicted peak at the bands' top with E136's base, "
              f"{p['peaks']['at_bands_top_with_e136_base_w']:.1f} W, passes the {LINE_W:g} W line")
        return 3
    if a.check:
        same = open(os.path.join(HERE, "plan-e194.json")).read() == js
        print("PLAN CHECK " + ("PASS" if same else "FAIL"))
        return 0 if same else 1
    open(os.path.join(HERE, "plan-e194.json"), "w").write(js)
    for k, v in p["configs"].items():
        print(f"{k:14s} K {v['launches_K']:2d} (the K rule at E194's bands: {v['k_rule_at_e194_bands_reported']:2d})  burst "
              f"{v['burst_s_at_point']:.2f} s at the point, {v['burst_s_at_slow_end']:.2f} s at the slow end; all K start "
              f"at the slow end: {v['all_k_start_at_slow_end']}")
    print("card-minutes", p["card_minutes"]["total"], "cap", p["card_minutes"]["cap"],
          "; 24 passes without the gate %.1f min" % p["card_minutes"]["c_arithmetic"]["24_passes_without_the_gate_min"])
    pk = p["peaks"]
    print("peaks: %.1f W at the points, %.1f W at the bands' top; with E136's base %.1f and %.1f W (line %g W)"
          % (pk["at_points_w"], pk["at_bands_top_w"], pk["at_points_with_e136_base_w"], pk["at_bands_top_with_e136_base_w"],
             LINE_W))
    for r in p["order"]["rounds"]:
        print("round:", ", ".join(r))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
