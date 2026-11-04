#!/usr/bin/env python3
"""E170 (Q141(w)): the machine form of the registration, frozen before any E170 data. Standard library only. It fits nothing and adds no
prediction: every model number is copied by key from files frozen in earlier commits after their sha256 is checked (pool 7 and its aifoundry2
predictions, lab 75802201 / 3c9bb2ba; M9's aifoundry2 part 5b98bd5c; E165's references, 3ef06839; E84's card-0 cells, 337b03b2's data; E118's
README table), and it writes beside them what E170's rules need: the admitted tiles and the ones left out by name, the tiers, the registered order,
the card term's constant, the references, the stops and the rules.

    python3 -B tools/claims-v3/e170/make_predictions_e170.py > tools/claims-v3/e170/predictions-e170.txt

writes tools/claims-v3/e170/predictions-e170.json beside itself.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e170_common as C  # noqa: E402

ROOT = C.ROOT


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


def main():
    bad = C.check_frozen()
    for rel, want in C.PARENT_SHA256.items():
        got = C.sha256_file(os.path.join(ROOT, rel))
        if got != want:
            bad.append(f"{rel}: sha256 {got}, registered {want}")
    adm_sha = C.sha256_file(os.path.join(ROOT, C.ADM_A2_REL))
    if adm_sha != C.FROZEN.get(C.ADM_A2_REL, adm_sha):
        bad.append(f"{C.ADM_A2_REL}: sha256 {adm_sha}")
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    man = C.manifest()
    P2 = load(C.PRED_A2_REL)
    ADM = load(C.ADM_A2_REL)
    E84 = load(C.E84_RESULTS_REL)
    E165 = load(C.E165_PRED_REL)
    z0 = {t: E84["cells"][k]["p800_w"] for t, k in C.E84_ZEROS_P800_KEYS.items()}
    tiles, left = {}, {}
    for n, t in sorted(man.items()):
        rec = P2["tiles"][n]
        a = rec["M9"]["a2_q140l"]
        # E165's admission value: the largest of the tile's three frozen 95% upper peaks on aifoundry2 (the 82 W list, per_tile.peak_hi95_w)
        adm_a2 = max(ADM["per_tile"][n]["peak_hi95_w"].values())
        est = C.est_card0(adm_a2, a["P800_w"], a["zeros_board_w"], z0[t["type"]])
        lo, hi = rec["M9"]["D600_a3_95"]
        row = {"type": t["type"], "label": C.label_of(n), "priority": t["priority"], "anchor": t["anchor"], "aim": t.get("aim"), "real": t.get("real"),
               "est_card0_peak_w": round(est, 3), "adm_a2_peak_w": round(adm_a2, 3), "a2_P800_w": a["P800_w"], "a2_zeros_board_w": a["zeros_board_w"],
               "models": {"M9": {"D600_a3_footing_w": rec["M9"]["D600_a3_footing_w"], "D_band_hw": round((hi - lo) / 2.0, 6), "a2_q140l": a},
                          "M8": {"D600_a3_footing_w": rec["M8"]["D600_a3_footing_w"]}, "M7": {"D600_a3_footing_w": rec["M7"]["D600_a3_footing_w"]},
                          "M6": {"D600_a3_footing_w": rec["M6"]["D600_a3_footing_w"]}}}
        if est <= C.ADMIT_LINE_W:
            row["tier"] = "A" if est <= C.TIER_B_ABOVE_W else "B"
            row["group"] = "pinned"
            tiles[n] = row
        else:
            left[n] = {"type": t["type"], "est_card0_peak_w": round(est, 3), "why": f"card-0 estimate {est:.2f} W > {C.ADMIT_LINE_W:g} W"}
    # every admitted tile must be predicted below the cap by M9's part at its fallback (pinned): the governor never acts at these powers
    gov = [n for n, r in tiles.items() if r["models"]["M9"]["a2_q140l"]["group"] != "pinned"]
    # the registered order: half A (passes 1-3), then half B (passes 4-6); each pass opens with the three zeros anchors (a seeded order); half A's
    # other tiles are shuffled with Random("E170|A|<pass>"), half B's run in ascending card-0 estimate, the hottest last
    zeros = list(C.ZEROS_ANCHORS)
    A = sorted(n for n, r in tiles.items() if r["tier"] == "A" and n not in zeros)
    B = sorted((n for n, r in tiles.items() if r["tier"] == "B"), key=lambda n: (tiles[n]["est_card0_peak_w"], n))
    order = []
    for half, members, passes in (("A", A, (1, 2, 3)), ("B", B, (4, 5, 6))):
        for p in passes:
            rng = random.Random(f"E170|{half}|{p}")
            z = list(zeros)
            rng.shuffle(z)
            rest = list(members)
            if half == "A":
                rng.shuffle(rest)
            for n in z + rest:
                order.append({"idx": len(order), "pass": p, "half": half, "name": n, "label": C.label_of(n), "type": man[n]["type"]})
    scored = sorted(n for n in tiles if n not in zeros)
    p1_new = sorted(n for n in scored if tiles[n]["priority"] == 1 and not tiles[n]["anchor"])
    ref = E165["reference"]
    pin = ref["e2e"]["pinned"]
    plan_s = 11.94 * len(order)
    # a planning forecast (information only): the pinned board error drawn from the end-to-end reference, plus a card-scale error d ~ U(-6%, +2%)
    # of the predicted D (E84's 800 MHz pairs read 0.88-0.94 of aifoundry2, E118's 600 MHz pairs 0.94-0.96: kappa0 may sit 0-6% high)
    rng = random.Random(1703)
    predD = [C.KAPPA0 * tiles[n]["models"]["M9"]["a2_q140l"]["burst_D_w"] for n in scored]
    lo95, hi95 = C.boot_rms_range(pin["w_err"], len(scored), draws=4000, seed=C.BOOT_SEED)
    w_pass = b_pass = 0
    sims = 4000
    for _ in range(sims):
        d = rng.uniform(-0.06, 0.02)
        e = [pin["w_err"][rng.randrange(len(pin["w_err"]))] + d * D for D in predD]
        r = C.rms(e)
        m = C.mean(e)
        w_pass += r <= hi95
        b_pass += abs(m) <= 0.5 and r <= 1.0
    out = {"experiment": C.EXPERIMENT, "request": C.REQUEST, "card": C.CARD,
           "_note": "E170's machine registration (E170.md); every model number copied by key from frozen files after their sha256 was checked; nothing fitted",
           "inputs_sha256": {**C.FROZEN, **C.PARENT_SHA256},
           "commits": {"pool7": ["75802201", "3c9bb2ba"], "M9": ["1f244140", "8dfafae3"], "M9_a2": ["5b98bd5c", "245caffe", "5c98c0c5"],
                       "heat_replicates": ["11174d20", "c9aaf179", "a4fe976d", "ac06c9be"], "G4_stride": ["49575094", "e39d06da", "1bfaa4e4"],
                       "E165": ["3ef06839", "a5c56d17", "e3c4eafc", "fe6f4862", "a509ff8b"], "E164": ["4286f0a8", "f4e75c95", "ce10e301", "45aeda12"],
                       "E160": ["2e016917", "6a330635", "42ba850f"], "E84": ["337b03b2", "1713a3f9"], "E118": ["28e625c9", "f37fa285"], "Q139k": ["60b91395", "4946a992"]},
           "card_term": {"kappa0": C.KAPPA0, "kappa0_ratios": {k: round(v, 6) for k, v in C.kappa0_ratios().items()}, "kappa0_sources": C.KAPPA0_SOURCES,
                         "kappa0_source": C.E118_README_REL + " (table 'Three cards at 600 MHz now': E118 on card 0 against E72 on aifoundry2)",
                         "level": "the session's own zeros anchors, every counted burst at >= 795 MHz, per format, referred to each tile's die starts by m9_a2's kT, in full (E170.md)",
                         "kT_w_per_c": C.m9a2().KT, "T_ref_c": C.m9a2().TREF},
           "admission": {"line_w": C.ADMIT_LINE_W, "peak_lock_w": C.PEAK_LOCK_W, "tier_b_above_w": C.TIER_B_ABOVE_W, "switch_ceiling": C.SWITCH_CEIL,
                         "card0_zeros_p800_w": z0, "card0_zeros_source": C.E84_RESULTS_REL + " cells.<type>/zeros.p800_w",
                         "formula": "E165's admission value (the largest of the tile's three frozen 95% upper peaks on aifoundry2) - (M9.a2_q140l.zeros_board_w - card 0's E84 zeros p800) - 0.05 x (M9.a2_q140l.P800_w - M9.a2_q140l.zeros_board_w)"},
           "tiles": tiles, "left_out": left, "n_admitted": len(tiles), "n_scored": len(scored), "scored": scored, "priority1_new": p1_new,
           "tier_A": A, "tier_B": B, "governed_admitted": gov, "order": order, "order_seed": "Random('E170|<half>|<pass>')", "passes": [1, 2, 3, 4, 5, 6],
           "runs": len(order),
           "reference": {"pinned_board_w_err": pin["w_err"], "pinned_mhz_err": pin["mhz_err"], "pinned_rms_w": pin["rms_w"], "pinned_rms_mhz": pin["rms_mhz"],
                         "heat_rise_err_c": ref["heat"]["rise_err_c"], "heat_rms_c": ref["heat"]["rms_c"],
                         "source": f"{C.E165_PRED_REL} reference.e2e.pinned (Q140(l)'s 42 end-to-end pinned cells) and reference.heat (112 residuals)"},
           "plan_bars_at_full_n": {"W": [round(lo95, 4), round(hi95, 4)], "n": len(scored)},
           "forecast_information_only": {"P_W_pass": round(w_pass / sims, 3), "P_B_pass": round(b_pass / sims, 3), "kappa_error": "U(-6%, +2%)", "sims": sims},
           "safety": C.SAFETY, "min_mhz_alarm": C.MIN_MHZ_ALARM, "want_config": C.WANT_CONFIG, "want_idle_mhz": C.WANT_IDLE_MHZ,
           "identity": {"e84_read_epoch": C.E84_READ_EPOCH, "e84_uptime_min": C.E84_UPTIME_MIN, "tol_min": C.UPTIME_TOL_MIN, "host_boot_before": C.HOST_BOOT_BEFORE,
                        "identity": C.E84_IDENTITY},
           "card_time": {"bursts": len(order), "s_per_burst_E160": 11.94, "session_min": round(plan_s / 60.0, 1), "smoke_and_stop_tests_min": 2.5,
                         "cap_card_min": C.CAP_CARD_MIN, "slot_min": C.SLOT_MIN,
                         "subset": "passes 1, 2, 4 and 5 (the first two of each half): --subset, --cap 25 in a 30-minute slot"},
           "rules": {"min_passes": 2, "min_tiles": C.MIN_TILES, "min_tiles_m1": C.MIN_TILES_M1, "boot": [C.BOOT_DRAWS, C.BOOT_SEED],
                     "paired": [C.PAIRED_DRAWS, C.PAIRED_SEED], "ratio": [C.RATIO_DRAWS, C.RATIO_SEED],
                     "E170-C": "every launch of every BURST run has a C record reading PASS (it decides which runs count)",
                     "E170-W": "pinned board, rms(board - primary) at or below the 97.5% point of the bootstrap of the 42 pinned board errors: PASS, else FAIL",
                     "E170-B": "|mean(board - primary)| <= 0.5 W and rms <= 1.0 W: PASS, else FAIL (rank 2's pinned lines on a second governed card)",
                     "E170-M1": "rank 1 on card 0: d = rms(M9 D errors) - rms(M6 D errors) over the admitted priority-1 new kinds, each model's D600 through the same card term; paired 95%: BETTER if the upper end < 0, WORSE if the lower end > 0, else NOT RESOLVED",
                     "E170-M2": "the same, M9 against M8",
                     "E170-X0": "the median over scored non-anchor tiles with a2 burst_D >= 5 W of measured D / (a2 burst_D): PASS if its 95% interval holds kappa0, else FAIL",
                     "E170-F": "pinned clock rms at or below the 97.5% point of the bootstrap of the 42 pinned clock errors",
                     "E170-W3": "coverage of the primary's board band (+-1.264 W): inside >= the 2.5% point of Binomial(n, 0.95)",
                     "E170-H1": "die rise rms against the bootstrap of the burst heat law's 112 residuals",
                     "E170-H3": "coverage of the die-rise band (+-1.406 C)",
                     "E170-S": "no safety stop, no sampler line under 590 MHz in any counted run, no peak at or above 62 W: PASS, else FAIL (the day's behaviour)"}}
    json.dump(out, open(os.path.join(HERE, "predictions-e170.json"), "w"), indent=1, sort_keys=True)
    print(f"E170 machine registration: {len(tiles)} admitted ({len(scored)} scored, {len(p1_new)} priority-1 new kinds), {len(left)} left out by name")
    print(f"  kappa0 {C.KAPPA0} (median of {json.dumps({k: round(v, 4) for k, v in C.kappa0_ratios().items()})})")
    print(f"  card 0's 800 MHz zeros (E84): {z0}")
    print(f"  tier A {len(A)} + 3 zeros anchors, tier B {len(B)}; governed among the admitted: {gov}")
    print(f"  the order: {len(order)} bursts, {plan_s / 60:.1f} min at E160's 11.94 s a burst (+ about 2.5 min smoke and stop tests)")
    print(f"  W's line at n = {len(scored)}: {lo95:.3f}-{hi95:.3f} W; forecast P(W PASS) {w_pass / sims:.2f}, P(B PASS) {b_pass / sims:.2f}")
    print("admitted (card-0 estimate of the 95% upper peak, W):")
    for n in sorted(tiles, key=lambda n: tiles[n]["est_card0_peak_w"]):
        r = tiles[n]
        print(f"  {n:44s} {r['type']:4s} p{r['priority']} tier {r['tier']}  est {r['est_card0_peak_w']:6.2f}  (aifoundry2 {r['adm_a2_peak_w']:6.2f})  "
              f"M9 D600 {r['models']['M9']['D600_a3_footing_w']:7.3f}  a2 burst D {r['models']['M9']['a2_q140l']['burst_D_w']:7.3f}")
    print("left out by name:")
    for n, r in sorted(left.items(), key=lambda kv: kv[1]["est_card0_peak_w"]):
        print(f"  {n:44s} {r['type']:4s} est {r['est_card0_peak_w']:6.2f}")


if __name__ == "__main__":
    main()
