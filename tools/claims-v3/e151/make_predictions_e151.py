#!/usr/bin/env python3
"""E151's freeze (Q139): writes predictions-e151.json from E145's frozen registration (tools/claims-v3/e145/predictions-e145.json, which
copies E138's and E130's, and so Q136(a)'s d64ea98c, number for number), with E151's rules, the registered rail filter and its test on
E145's committed data, the aifoundry3 rail census, the plan, the precision sized from E138's measured block scatter on this card, card 0's
earlier per-bit rail prices (E130's and E138's, recomputed here and checked equal to E145's frozen ones), card 1's per-bit rail prices
under E151's filter (from e145_under_filter.py's reduction of E145's blocks, frozen here before any E151 data) and the sha256 of every
file E151 runs. Nothing is fitted to E151: no E151 data exist before this freeze.

    python3 tools/claims-v3/e151/make_predictions_e151.py
"""
import glob
import hashlib
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
P145 = os.path.join(ROOT, "tools/claims-v3/e145/predictions-e145.json")
D = "docs/reports/data"
D130 = f"{D}/2026-11-02-e130-int8-netlists"
D138 = f"{D}/2026-11-02-e138-int8-b-rail"
D145 = f"{D}/2026-11-02-e145-int8-b-card1"
F145 = "tools/claims-v3/e151/e145-filtered"
CARD_FILES = ["e151_common.py", "run_e151.py", "block_e151.sh", "queue_e151.sh", "session_e151.sh", "preflight_e151.sh",
              "smoke_gate_e151.py", "railfilter_e151.py", "check_e151.py", "e130-items.json"]
DESK_FILES = ["reduce_e151.py", "score_e151.py", "collect_e151.sh", "make_predictions_e151.py", "selftest_e151.py",
              "telemetry_max_e151.py", "e145_under_filter.py"]
# every committed aifoundry3 card-0 session since 1 Nov 2026 with block telemetry (the rail census; their READMEs name the card)
A3_SESSIONS = ["2026-11-01-e92-sign-split", "2026-11-01-e95-real-tensors-energy", "2026-11-01-e97-heat-low-power-steady",
               "2026-11-01-e99-dram-mechanism", "2026-11-01-e101-real-matmul", "2026-11-01-e105-gemm-layout",
               "2026-11-01-e107-gemm-placement", "2026-11-01-e109-int8-zeros", "2026-11-01-e110-memory-width",
               "2026-11-01-e113-a-side-saturation", "2026-11-01-e115-blind-pool", "2026-11-01-e116-split-replicate",
               "2026-11-01-e121-zero-gate-replicate", "2026-11-01-e122-signs-replicate", "2026-11-01-e123-tile-spread-rest",
               "2026-11-02-e127-b-gate", "2026-11-02-e130-int8-netlists", "2026-11-02-e132-memory-split",
               "2026-11-02-e134-bit-prices-more", "2026-11-02-e138-int8-b-rail", "2026-11-02-e139-memory-split-more-passes",
               "2026-11-02-e140-blind4", "2026-11-02-e141-blind5-aifoundry3", "2026-11-02-e144-heat-minutes",
               "2026-11-02-e147-bit-prices-rest"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rel_sha(rels):
    return {r: sha(os.path.join(ROOT, r)) for r in rels}


def census():
    import railfilter_e151 as rf
    per, tot = {}, {"sessions": 0, "files": 0, "samples": 0, "F1": 0, "F2": 0, "union": 0, "running_max_field_w": set()}
    for s in A3_SESSIONS:
        fs = sorted(glob.glob(os.path.join(ROOT, D, s, "**", "telemetry.jsonl.gz"), recursive=True)) + \
            sorted(glob.glob(os.path.join(ROOT, D, s, "**", "telemetry.jsonl"), recursive=True))
        n = f1 = f2 = u = 0
        for f in fs:
            rows = rf.load(f)
            fl = rf.flags(rows)
            _, M = rf.rail_and_max(rows)
            tot["running_max_field_w"] |= {m for m in M if m is not None}
            n += len(rows)
            f1, f2, u = f1 + len(fl["F1"]), f2 + len(fl["F2"]), u + len(fl["union"])
        per[s] = {"files": len(fs), "samples": n, "F1": f1, "F2": f2, "union": u}
        tot["sessions"] += 1
        tot["files"] += len(fs)
        tot["samples"] += n
        tot["F1"] += f1
        tot["F2"] += f2
        tot["union"] += u
    tot["running_max_field_w"] = sorted(tot["running_max_field_w"])
    return {"total": tot, "per_session": per}


def main():
    q = json.load(open(P145))
    import score_e151 as S151  # noqa: E402  (loads score_e145, score_e138, score_e130 unchanged)
    S145, S = S151.S145, S151.S
    import railfilter_e151 as rf
    c_rb = q["plan"]["c_rb"]
    mini = {"plan": {"c_rb": c_rb, "train_gate_w": q["plan"]["train_gate_w"]}}
    tiles = {"int8." + t["tile"]: t for t in json.load(open(os.path.join(HERE, "e130-items.json")))["tiles"]}
    b130 = S145.make_book(f"{ROOT}/{D130}/runs.csv", f"{ROOT}/{D130}/e130.json", "rail_raw", True, mini, tiles, "e130")
    b138 = S145.make_book(f"{ROOT}/{D138}/runs.csv", f"{ROOT}/{D138}/e138.json", "rail_raw", True, mini, tiles, "e138")
    b145f = S145.make_book(f"{ROOT}/{F145}/runs.csv", f"{ROOT}/{F145}/e145-filtered.json", "rail_raw", True, mini, tiles, "e145")
    card0 = {"B": {}, "A": {}}
    card1f = {"B": {}, "A": {}}
    for j in range(7):
        vals = list(b130.series(f"b1_{j}").values()) + list(b138.series(f"b1_{j}").values())
        card0["B"][f"b1_{j}"] = sum(vals) / len(vals)
        va = list(b130.series(f"a1_{j}").values())
        card0["A"][f"a1_{j}"] = sum(va) / len(va)
        card1f["B"][f"b1_{j}"] = S.mean_ci(b145f.series(f"b1_{j}").values())["mean"]
        card1f["A"][f"a1_{j}"] = S.mean_ci(b145f.series(f"a1_{j}").values())["mean"]
    for side in ("B", "A"):
        for k, v in card0[side].items():
            assert abs(v - q["card0_prices_rail_fJ"][side][k]) < 1e-9, (side, k, v)
    combo = S.combos()["B_odd_minus_even_fJ"]
    per = {name: list(S.per_block_stat(b, combo).values()) for name, b in (("E138", b138), ("E130", b130), ("E145f", b145f))}
    sd_rail = {k: statistics.stdev(v) for k, v in per.items()}
    T = q["thresholds"]["T_B"]["value"]
    t975 = S145.t975_e145
    prec = {}
    for n in range(6, 15):
        row = {}
        for k in ("E138", "E130", "E145f"):
            hw = t975(n - 1) * sd_rail[k] / c_rb / math.sqrt(n)
            row[k] = {"half_width_board_equivalent_fJ": hw, "R1_RECODED_needs_mean_at_least": T + hw}
        prec[str(n)] = row
    # the chance that R1 reads RECODED or FLAT, by simulation (normal block values; the session's own sd and exact t, as scored)
    rng = random.Random(151)
    means = {"E130 rail (+33.15)": 33.15, "card 0 pool E130+E138 (+34.8)": 34.83, "E138 (+35.95)": 35.95,
             "E145 under E151's filter (+36.12)": 36.12}
    sim = {}
    for n in (9, 10, 11):
        for sk in ("E138", "E130"):
            sig = sd_rail[sk] / c_rb
            for mk, mu in means.items():
                rec = flat = 0
                N = 20000
                for _ in range(N):
                    x = [rng.gauss(mu, sig) for _ in range(n)]
                    m = sum(x) / n
                    s = statistics.stdev(x)
                    h = t975(n - 1) * s / math.sqrt(n)
                    rec += m - h >= T
                    flat += m + h <= T
                sim[f"n={n} sd={sk} mean={mk}"] = {"P_RECODED": rec / N, "P_FLAT": flat / N}
    # the filter's test on E145's committed data (before any E151 data)
    e145_blocks = sorted(glob.glob(os.path.join(ROOT, D145, "aifoundry1-c1", "kinds", "p145[1-3][0-9]", "telemetry.jsonl.gz")))
    f145 = {"F1": 0, "F2": 0, "union": 0, "samples": 0}
    for f in e145_blocks:
        rows = rf.load(f)
        fl = rf.flags(rows)
        f145["samples"] += len(rows)
        for k in ("F1", "F2", "union"):
            f145[k] += len(fl[k])
    r145 = S151.score_session((f"{ROOT}/{F145}/runs.csv", f"{ROOT}/{F145}/e145-filtered.json"), {}, {},
                              q | {"card1_prices_rail_fJ_filtered": card1f}, tiles, "e145")
    eB = r145["primary"]["B_odd_minus_even_board_equivalent_fJ"]
    cen = census()
    rules = {
        "E151-R1": {"what": "is B recoded? E145-R1 (E138-R1's rule) on aifoundry3 card 0: B's odd bits (1, 3, 5) minus its even bits (0, 2, 4), "
                            "mean per flipped bit, on the MINION RAIL (rail_raw, the board's dips and E151's rail glitches removed) / c_rb "
                            "0.81 (board-equivalent fJ), against E130's T_B",
                    "verdicts": "RECODED if the 95% interval's low end >= T_B (the interval clears the 30.68 fJ line: the critic's decisive "
                                "test); FLAT if its high end <= T_B; else INCONCLUSIVE; NOT SCORED under 3 kept B blocks", "threshold": T},
        "E151-R1n": {"what": "E145-R1n: the same interval against the two groups' frozen bands", "verdicts": q["rules"]["E145-R1n"]["verdicts"]},
        "E151-R1q": {"what": "E145-R1q: B's odd / even on the rail (Fieller, paired over blocks; no unit, no c_rb) against the two groups' "
                             "frozen ratio bands", "verdicts": q["rules"]["E145-R1q"]["verdicts"]},
        "E151-R2": {"what": "the A control, E145-R2 on this session: A's odd - even, board-equivalent fJ, against T_A",
                    "verdicts": "RECODED / FLAT / INCONCLUSIVE; NOT SCORED under 3 kept A blocks", "threshold": q["rules"]["E145-R2"]["threshold"]},
        "E151-R3": {"what": "the A control, E145-R3: A's sign bit with B = 0x55 minus with B = 1, board-equivalent fJ, against T_S",
                    "verdicts": "RISES / FLAT / INCONCLUSIVE; NOT SCORED under 3 kept A blocks", "threshold": q["rules"]["E145-R3"]["threshold"]},
        "E151-C1": {"what": "the control: does today's A side read as E130's registered primary on this card (R2 FLAT, R3 RISES)?",
                    "verdicts": "REPRODUCES E130 / DIFFERS from E130 / INCONCLUSIVE / NOT SCORED (E145-C1's rule)"},
        "E151-R4": {"what": "which multiplier, on card 0: E138-R4's rule on E151-R1, with this card's A side as E130 registered it "
                            "(E130-R2 FLAT, E130-R3 RISES), as E138 did",
                    "verdicts": "BOOTH ON B if E151-R1 RECODED; NO BOOTH if FLAT; else INCONCLUSIVE between BOOTH ON B / NO BOOTH; NOT SCORED"},
        "E151-R4s": {"what": "E145-R4's form: E130-R4's rule on this session's own E151-R1, R2 and R3", "verdicts": q["rules"]["E145-R4"]["verdicts"]
                     + "; NOT SCORED unless 3 A blocks are kept"},
        "E151-R5": {"what": "E130-R5 (A's sign, word 2 / word 1, in the shared band)", "verdicts": "HOLDS / FAILS (ABOVE|BELOW) / NOT SCORED"},
        "E151-R6": {"what": "E130-R6 (B's sign, word 2 / word 1, in the shared band)", "verdicts": "HOLDS / FAILS (ABOVE|BELOW) / NOT SCORED"},
        "E151-N": {"what": "E130-N: each netlist SURVIVES if the session's interval overlaps its frozen band on all three separators",
                   "verdicts": "SURVIVES / EXCLUDED by <separators> / NOT SCORED (the A separators need 3 A blocks)"},
        "E130-R4": q["rules"]["E130-R4"],
    }
    plan_seq = [15110, 15111, 15112, 15113, 15114, 15115, 15116, 15117, 15118, 15119, 15130, 15120, 15131, 15132]
    import e151_common as c151
    assert tuple(plan_seq) == c151.SEQUENCE
    out = {
        "experiment": "E151", "date": "2026-11-03",
        "request": "Q139 (the critic's open list while the cards are free; prediction is the goal): Q138's final critic rank 11, the kinds "
                   "page's section 11 item 12 ('int8 at gate level'): E145's design on aifoundry3 with its rail filter registered first",
        "card": {"name": "aifoundry3 card 0 (no V3_DEVICE, CARD aifoundry3, lock etsoc-shire0.lock)",
                 "firmware": "a non-public thermal build first flashed on 7 Oct 2026 (E130's A1); classes rest on et-platform 836a4ab's handlers",
                 "clock": "600 MHz, latched by its boot-time TDP of 0; TDP 0 W / threshold 65 C as read, never set",
                 "config_gate": {"expected": {"tdp_w": 0, "temp_threshold_c": 65}, "what": "E78's own gate (no substitution)"}},
        "units": "fJ per flipped bit; the primary is the minion rail, converted to board-equivalent fJ at c_rb = 0.81 (E78's, frozen)",
        "source": {"e145_registration": "tools/claims-v3/e145/predictions-e145.json", "e145_registration_sha256": sha(P145),
                   "e138_registration_sha256": q["source"]["e138_registration_sha256"],
                   "e130_registration_sha256": q["source"]["e130_registration_sha256"], "q136a_freeze": q["source"]["q136a_freeze"]},
        "netlists": q["netlists"], "thresholds": q["thresholds"], "group_bands": q["group_bands"], "shared_bands": q["shared_bands"],
        "separators": q["separators"], "item_order": q["item_order"], "rules": rules,
        "rail_filter": {
            "file": "tools/claims-v3/e151/railfilter_e151.py", "sha256": sha(os.path.join(HERE, "railfilter_e151.py")),
            "rule": "a sample is a rail glitch when F1: sp.minion_w[0] > max(sp.minion_w[0] at i-2, at i+2) + 4.0 W (E82 A2's dip rule "
                    "mirrored; E145's post-hoc definition) or F2: sp.minion_w[0] == sp.minion_w[2] (the running maximum the sample "
                    "reports); glitch samples are removed whole, with the board's dips, before the reduction reads the telemetry",
            "reads": "the telemetry samples only, one block at a time; never an item, run, step, price or contrast",
            "test_on_e145": {"samples": f145["samples"], "F1": f145["F1"], "F2": f145["F2"], "union": f145["union"],
                             "equals_e145_posthoc": "the union is E145's 15 post-hoc spikes; E145's reducer with it reproduces "
                                                    "posthoc/runs-posthoc.csv and e145-posthoc.json byte for byte (e145_under_filter.py)",
                             "E145_B_odd_minus_even_board_equivalent_fJ": eB,
                             "E145_R1_under_the_filter": r145["primary"]["verdicts"]["E151-R1"]},
            "aifoundry3_census": cen},
        "card0_prices_rail_fJ": card0 | {"blocks": {"E130": len(b130.blocks["B"]), "E138": len(b138.blocks["B"]), "E130_A": len(b130.blocks["A"])},
                                         "what": "card 0's earlier sessions (E130's 6 and E138's 9 B blocks, E130's 4 A blocks), equal to "
                                                 "predictions-e145.json's frozen card0_prices_rail_fJ"},
        "card1_prices_rail_fJ_filtered": card1f | {"blocks": {"B": len(b145f.blocks["B"]), "A": len(b145f.blocks["A"])},
                                                   "what": "aifoundry1 card 1 (E145's 13 B and 3 A blocks) under E151's rail filter"},
        "precision": {"from": "the per-block B odd - even on the rail (rail fJ) of E138's 9, E130's 6 and E145's 13 (filtered) B blocks",
                      "per_block_sd_rail_fJ": sd_rail, "by_kept_B_blocks": prec, "simulated_chances": sim,
                      "what": "half-width = t(0.975, n - 1) x sd / c_rb / sqrt(n), board-equivalent fJ; R1 reads RECODED only if the mean "
                              "is at least T_B + half-width"},
        "expected": {"E151-R1": "INCONCLUSIVE", "E151-R1n": "NEITHER (BETWEEN)", "E151-R1q": "NEITHER (BETWEEN)",
                     "E151-R2": "NOT SCORED", "E151-R3": "NOT SCORED", "E151-C1": "NOT SCORED",
                     "E151-R4": "INCONCLUSIVE between BOOTH ON B / NO BOOTH", "E151-R4s": "NOT SCORED", "E151-R5": "NOT SCORED",
                     "E151-R6": "FAILS (BELOW)", "E151-N": {n: "NOT SCORED" for n in q["netlists"]},
                     "blocks": "10 B and 1 A (the budget rule decides; 9 B and 1 A if the blocks run slow)",
                     "cross_session_card0": "per position < parity < flat in rms; per position about 3-5 rail fJ (7-10%), flat about 13-14 (about 29%)",
                     "cross_card_from_card1_filtered": "per position < parity < flat; per position about 3-5 rail fJ (7-10%), flat about 13-15 (30-35%)",
                     "why": "card 0's sessions read +33.15 (E130) and +35.95 (E138) board-equivalent fJ; at 10 kept B blocks and E138's "
                            "block sd (5.77 rail fJ) the half-width is about 5.1, so RECODED needs a mean of at least 35.8: the simulated "
                            "chance is about 0.3-0.5 at card 0's means (precision.simulated_chances), and about 0.9 or more if the scatter is "
                            "E130's (2.77). FLAT is near impossible. The rail on this card has shown no glitch in about 700,000 samples, so "
                            "the filter is expected to remove nothing. One A block is too few to score the control (E145's minimum is 3); "
                            "R6 as card 0's rail (E138's b2_7 / b1_7 = 0.69)."},
        "plan": {
            "primary": "minion rail rail_raw over [t0+2 s, t0+4 s), no temperature term, minus the item's own zero interpolated in time, "
                       "divided by designed flips x the run's rate, then by c_rb = 0.81; reduce_e78.py unchanged via reduce_e151.py "
                       "--drop-dips --rail-filter (E82 A2's board dips and E151's rail glitches removed), leakage auto, E78's configuration "
                       "gate (aifoundry3's 0 W / 65 C); E78's per-run and pass gates; E130's train gate (0.25 W on the board's p_raw)",
            "c_rb": c_rb,
            "arms": ["board (p_raw)", "board_p80", "rail_filter_off (E145's registered primary form: dips removed, the filter off)",
                     "rail_dips_kept (the filter on, dips kept)", "rail_gates_off", "pools (reported only)"],
            "sequence": plan_seq,
            "blocks": "B: E138's B design (34 runs); A: E130's A design (25 runs); each order seeded Random('E151|aifoundry3|<pass>')",
            "smoke_pass": 15101, "stoptest_pass": 15102, "runs_per_block": {"B": 34, "A": 25}, "first_estimates_s": {"B": 185, "A": 140},
            "min_kept_blocks": q["plan"]["min_kept_blocks"], "train_gate_w": q["plan"]["train_gate_w"],
            "stops": {"board_w": 45.0, "die_shire0_c": 68.0, "run_e78_max_c": 70.0, "stoptest_board_w": 1.0, "stoptest_die_c": 1.0,
                      "stoptest_age_max_s": 2.0,
                      "what": "the newest line of the running sampler's file (telemetry.jsonl.raw), read by the main path before every launch "
                              "and every 0.1 s while it waits (E145's guard) and by the in-run watcher every 0.1 s for the whole pass (E141's); "
                              "the die stop reads temp_c.minshire[0] (aifoundry3's minshire[2] is a constant 87 C latch); the stop-path test "
                              "fires all three before any launch"},
            "budget_s_from_session_start": 2100, "reserve_s": 45, "card_minutes_max": 35, "gap_s": 5,
            "time_gates": "no session starts after 2026-11-03 10:30 PST (session_e151.sh); the queue's deadline 11:25 PST (every run ends by 11:30)",
            "fma_s": 4, "train_options": "--preheat 0 --target 200 --quiet-s 0.2 --burnin 0 (E102's int8 block I)",
            "t": "E145's: exact t(0.975, n - 1) beyond n - 1 = 10; E130's table up to 10"},
        "harness": {
            "reused_unchanged_sha256": q["harness"]["reused_unchanged_sha256"],
            "card_code_unchanged_sha256": rel_sha(["tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py",
                                                   "tools/claims-v3/kinds/run_e78.py", "tools/claims-v3/kinds/reduce_e78.py",
                                                   "tools/claims-v3/kinds/kinds.json", "tools/claims-v3/e128/ettelem_guard.sh",
                                                   "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json",
                                                   "tools/claims-v3/kinds/e130/e130.json", "tools/claims-v3/kinds/e130/sha256.txt"]),
            "e151_card_files_sha256": rel_sha([f"tools/claims-v3/e151/{f}" for f in CARD_FILES]),
            "e151_desk_files_sha256": rel_sha([f"tools/claims-v3/e151/{f}" for f in DESK_FILES]),
            "e151_tiles_sha256": {(k if not k.endswith("e130-items.json") else "tools/claims-v3/e151/e130-items.json"): v
                                  for k, v in q["harness"]["e145_tiles_sha256"].items()},
            "box_binaries_sha256": {"build/sparsity/host/sparsity_host": "20e760c20e9b99c789ef96f1e4e950d51f534410275bfb933c2aaf96d1090fd0",
                                    "build/ettelem/ettelem": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2"},
            "box_binaries_note": "aifoundry3's binaries as E138 and E141 registered and ran them (predictions-e138.json, predictions-e141.json), "
                                 "read again on aifoundry3 at 04:06 PST on 3 Nov",
            "score_e145_sha256": sha(os.path.join(ROOT, "tools/claims-v3/e145/score_e145.py")),
            "score_e138_sha256": sha(os.path.join(ROOT, "tools/claims-v3/e138/score_e138.py")),
            "score_e130_sha256": sha(os.path.join(ROOT, "tools/claims-v3/e130/score_e130.py")),
            "e145_filtered_sha256": rel_sha([f"{F145}/runs.csv", f"{F145}/e145-filtered.json"])},
    }
    assert out["harness"]["e151_tiles_sha256"]["tools/claims-v3/e151/e130-items.json"] == sha(os.path.join(HERE, "e130-items.json"))
    json.dump(out, open(os.path.join(HERE, "predictions-e151.json"), "w"), indent=1)
    open(os.path.join(HERE, "predictions-e151.json"), "a").write("\n")
    print(json.dumps({"card0_prices_rail_fJ": card0, "card1_prices_rail_fJ_filtered": card1f, "sd_rail": sd_rail,
                      "half_widths_E138sd": {n: round(v["E138"]["half_width_board_equivalent_fJ"], 3) for n, v in prec.items()},
                      "sim": sim, "filter_on_e145": f145, "E145_under_filter": eB,
                      "E145_R1_under_filter": r145["primary"]["verdicts"]["E151-R1"], "census_total": cen["total"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
