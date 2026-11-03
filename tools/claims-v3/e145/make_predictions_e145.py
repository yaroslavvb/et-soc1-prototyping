#!/usr/bin/env python3
"""E145's freeze (Q138): writes predictions-e145.json from E138's frozen registration (tools/claims-v3/e138/predictions-e138.json, which
copies E130's and so Q136(a)'s d64ea98c number for number), with E145's rules, the plan, the precision sized from E138's measured block
scatter, card 0's per-bit rail prices (computed here from E130's and E138's committed runs.csv by score_e145.py's own Book, the
prediction card 1 is scored against) and the sha256 of every file E145 runs. Nothing is fitted to card 1: no card-1 int8 single-bit
data exists before this freeze.

    python3 tools/claims-v3/e145/make_predictions_e145.py
"""
import hashlib
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
P138 = os.path.join(ROOT, "tools/claims-v3/e138/predictions-e138.json")
P130 = os.path.join(ROOT, "tools/claims-v3/e130/predictions-e130.json")
D130 = "docs/reports/data/2026-11-02-e130-int8-netlists"
D138 = "docs/reports/data/2026-11-02-e138-int8-b-rail"
CARD_FILES = ["e145_common.py", "run_e145.py", "block_e145.sh", "queue_e145.sh", "session_e145.sh", "preflight_e145.sh",
              "smoke_gate_e145.py", "e130-items.json"]
DESK_FILES = ["check_e145.py", "reduce_e145.py", "score_e145.py", "collect_e145.sh", "make_predictions_e145.py", "selftest_e145.py",
              "telemetry_max_e145.py"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rel_sha(rels):
    return {r: sha(os.path.join(ROOT, r)) for r in rels}


def main():
    q = json.load(open(P138))
    p = json.load(open(P130))
    import score_e145 as sc  # noqa: E402  (its Book and statistics; it reads no predictions-e145.json at import)
    c_rb = q["plan"]["c_rb"]
    mini = {"plan": {"c_rb": c_rb, "train_gate_w": q["plan"]["train_gate_w"]}}
    tiles = {"int8." + t["tile"]: t for t in json.load(open(os.path.join(HERE, "e130-items.json")))["tiles"]}
    b130 = sc.make_book(f"{ROOT}/{D130}/runs.csv", f"{ROOT}/{D130}/e130.json", "rail_raw", True, mini, tiles, "e130")
    b138 = sc.make_book(f"{ROOT}/{D138}/runs.csv", f"{ROOT}/{D138}/e138.json", "rail_raw", True, mini, tiles, "e138")
    # card 0's per-bit rail prices (rail fJ): B bits 0-6 the mean over E130's 6 and E138's 9 kept B blocks; A bits 0-6 E130's 4 A blocks
    card0 = {"B": {}, "A": {}}
    for j in range(7):
        vals = list(b130.series(f"b1_{j}").values()) + list(b138.series(f"b1_{j}").values())
        card0["B"][f"b1_{j}"] = sum(vals) / len(vals)
        va = list(b130.series(f"a1_{j}").values())
        card0["A"][f"a1_{j}"] = sum(va) / len(va)
    nB = {"E130": len(b130.blocks["B"]), "E138": len(b138.blocks["B"]), "E130_A": len(b130.blocks["A"])}
    # the precision, sized from E138's measured block scatter (the B odd - even per block, rail fJ, E138's 9 kept blocks)
    per = list(sc.S.per_block_stat(b138, sc.S.combos()["B_odd_minus_even_fJ"]).values())
    sd_rail = statistics.stdev(per)
    sd_beq = sd_rail / c_rb
    per130 = list(sc.S.per_block_stat(b130, sc.S.combos()["B_odd_minus_even_fJ"]).values())
    T = q["thresholds"]["T_B"]["value"]
    prec = {}
    for n in range(8, 17):
        hw = sc.t975_e145(n - 1) * sd_beq / math.sqrt(n)
        prec[str(n)] = {"half_width_board_equivalent_fJ": hw, "half_width_rail_fJ": hw * c_rb, "R1_RECODED_needs_mean_at_least": T + hw}
    rules = {
        "E145-R1": {"what": "is B recoded? E138-R1 on card 1: B's odd bits (1, 3, 5) minus its even bits (0, 2, 4), mean per flipped bit, "
                            "on the MINION RAIL (rail_raw) / c_rb 0.81 (board-equivalent fJ), against E130's T_B",
                    "verdicts": "RECODED if the 95% interval's low end >= T_B; FLAT if its high end <= T_B; else INCONCLUSIVE; NOT SCORED "
                                "under 3 kept B blocks", "threshold": T},
        "E145-R1n": {"what": "E138-R1n on card 1: the same interval against the two groups' frozen bands", "verdicts": q["rules"]["E138-R1n"]["verdicts"]},
        "E145-R1q": {"what": "E138-R1q on card 1: B's odd / even on the rail (Fieller, paired over blocks; no unit, no c_rb) against the "
                             "two groups' frozen ratio bands", "verdicts": q["rules"]["E138-R1q"]["verdicts"]},
        "E145-R2": {"what": "the A control, E130-R2 on card 1: A's odd - even, board-equivalent fJ (rail / 0.81), against T_A",
                    "verdicts": "RECODED / FLAT / INCONCLUSIVE as E130-R2; NOT SCORED under 3 kept A blocks", "threshold": p["thresholds"]["T_A"]["value"]},
        "E145-R3": {"what": "the A control, E130-R3 on card 1: A's sign bit with B = 0x55 minus with B = 1, board-equivalent fJ, against T_S",
                    "verdicts": "RISES / FLAT / INCONCLUSIVE as E130-R3; NOT SCORED under 3 kept A blocks", "threshold": p["thresholds"]["T_S"]["value"]},
        "E145-C1": {"what": "the control: does card 1's A side read as card 0's (E130's registered primary: R2 FLAT, R3 RISES)?",
                    "verdicts": "REPRODUCES card 0 if E145-R2 FLAT and E145-R3 RISES; DIFFERS from card 0 if E145-R2 RECODED or E145-R3 "
                                "FLAT; NOT SCORED if either is; else INCONCLUSIVE"},
        "E145-R4": {"what": "which multiplier, on card 1 alone: E130-R4's rule (the group whose three predicted verdicts no decided rule "
                            "contradicts) on (E145-R1, E145-R2, E145-R3)", "verdicts": p["rules"]["E130-R4"]["verdicts"]},
        "E145-R5": {"what": "E130-R5 on card 1 (A's sign, word 2 / word 1, in the shared band: a prediction all four netlists make)",
                    "verdicts": "HOLDS / FAILS (ABOVE|BELOW) / NOT SCORED"},
        "E145-R6": {"what": "E130-R6 on card 1 (B's sign, word 2 / word 1, in the shared band)", "verdicts": "HOLDS / FAILS (ABOVE|BELOW) / NOT SCORED"},
        "E145-N": {"what": "E130-N on card 1: each netlist SURVIVES if the card's interval overlaps its frozen band on all three separators "
                           "(B odd - even, A odd - even, A's sign step), board-equivalent fJ", "verdicts": "SURVIVES / EXCLUDED by <separators>"},
        "E130-R4": p["rules"]["E130-R4"],
    }
    out = {
        "experiment": "E145", "date": "2026-11-02",
        "request": "Q138 (settle the power model's open questions; prediction is the goal); the kinds page's section 11, item 12 "
                   "('int8 at gate level'): its structural verdict on a second card",
        "card": {"name": "aifoundry1 card 1 (V3_DEVICE=1, CARD aifoundry1-c1, lock etsoc-shire1.lock)",
                 "firmware": "release 1.4.0, BL1 and BL2 0.22.0, PMIC 1.3.0 since 31 Oct 2026 (E82 A1; E128 C1)",
                 "clock": "600 MHz in every sample since 25 Sep (its governor never raises it); TDP 65 W / threshold 65 C as read, never set",
                 "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65},
                                 "what": "E78's configuration pass gate accepts these reads on card 1 (E137's reduce_e137.py change 2)"}},
        "units": "fJ per flipped bit; the primary is the minion rail, converted to board-equivalent fJ at c_rb = 0.81 (E78's, frozen)",
        "source": {"e138_registration": "tools/claims-v3/e138/predictions-e138.json", "e138_registration_sha256": sha(P138),
                   "e130_registration": "tools/claims-v3/e130/predictions-e130.json", "e130_registration_sha256": sha(P130),
                   "q136a_freeze": q["source"]["q136a_freeze"]},
        "netlists": q["netlists"], "thresholds": q["thresholds"], "group_bands": q["group_bands"], "shared_bands": q["shared_bands"],
        "separators": q["separators"], "item_order": p["item_order"], "rules": rules,
        "card0_prices_rail_fJ": card0 | {"blocks": nB, "what": "card 0 = aifoundry3 card 0; rail_raw prices by score_e145.make_book "
                                                               "(E130's and E138's committed runs.csv, their own pass numbers)"},
        "precision": {"from": "E138's 9 kept B blocks: the per-block B odd - even on the rail", "per_block_sd_rail_fJ": sd_rail,
                      "per_block_sd_board_equivalent_fJ": sd_beq, "e130_per_block_sd_rail_fJ": statistics.stdev(per130),
                      "by_kept_B_blocks": prec,
                      "what": "half-width = t(0.975, n - 1) x sd / sqrt(n), board-equivalent fJ; R1 reads RECODED only if the mean is at "
                              "least T_B + half-width"},
        "expected": {"E145-R1": "INCONCLUSIVE", "E145-R1n": "NEITHER (BETWEEN)", "E145-R1q": "NEITHER (BETWEEN)", "E145-R2": "FLAT",
                     "E145-R3": "RISES", "E145-C1": "REPRODUCES card 0", "E145-R4": "INCONCLUSIVE between BOOTH ON B / NO BOOTH",
                     "E145-R5": "HOLDS", "E145-R6": "FAILS (BELOW)",
                     "E145-N": {n: "EXCLUDED by B_odd_minus_even_fJ" for n in q["netlists"]},
                     "cross_card_B": "per position < parity < flat in rms; per position about 5 rail fJ (about 10%), flat about 13 (about 29%)",
                     "why": "card 0's two sessions read +33.2 and +35.9 board-equivalent fJ (pool +34.8 [+31.6, +38.1]); at about 12 kept "
                            "B blocks and E138's block sd the half-width is about 4.5, so RECODED needs a mean of at least 35.2: about "
                            "even odds at card 0's pooled mean, if card 1's rail reads card 0's scale. R1n and R1q are far from every band. "
                            "The A control and R5 as card 0's registered primary and rail arm; R6 as card 0's rail (b2_7 / b1_7 = 0.69 in "
                            "E138, E130's rail arm FAILS (BELOW))."},
        "plan": {
            "primary": "minion rail rail_raw over [t0+2 s, t0+4 s), no temperature term, minus the item's own zero interpolated in time, "
                       "divided by designed flips x the run's rate, then by c_rb = 0.81; reduce_e78.py unchanged via reduce_e145.py "
                       "--drop-dips (E82 A2), leakage auto, the configuration gate at card 1's 65/65; E78's per-run and pass gates; E130's "
                       "train gate (0.25 W on the board's p_raw)",
            "c_rb": c_rb,
            "arms": ["board (p_raw: E130's primary meter)", "board_p80", "rail_dips_kept", "rail_gates_off",
                     "pools with card 0's B blocks (E130's 6, E138's 9; reported only)"],
            "sequence": [14510, 14530, 14511, 14512, 14513, 14531, 14514, 14515, 14516, 14532, 14517, 14518, 14519, 14520, 14521, 14522, 14523],
            "blocks": "B: E138's B design (34 runs); A: E130's A design (25 runs); each order seeded Random('E145|aifoundry1-c1|<pass>')",
            "smoke_pass": 14501, "stoptest_pass": 14502, "runs_per_block": {"B": 34, "A": 25}, "first_estimates_s": {"B": 200, "A": 160},
            "min_kept_blocks": 3, "train_gate_w": q["plan"]["train_gate_w"],
            "stops": {"board_w": 60.0, "die_hottest_shire_c": 72.0, "run_e78_max_c": 72.0, "stoptest_board_w": 1.0, "stoptest_die_c": 1.0,
                      "stoptest_age_max_s": 2.0,
                      "what": "read from the newest line of the running sampler's file (telemetry.jsonl.raw) before every launch and every "
                              "0.1 s while the runner waits; the stop-path test fires both before any launch"},
            "budget_s_from_session_start": 3000, "reserve_s": 90, "card_minutes_max": 50, "gap_s": 5,
            "deadline": "2026-11-02 23:30 PST (no session starts after 23:00 PST; every run ends by 23:50 PST)",
            "fma_s": 4, "train_options": "--preheat 0 --target 200 --quiet-s 0.2 --burnin 0 (E102's int8 block I)",
            "t": "exact t(0.975, n - 1) beyond n - 1 = 10 (score_e145.py change 2); E130's table up to 10"},
        "harness": {
            "reused_unchanged_sha256": q["harness"]["reused_unchanged_sha256"],
            "card_code_unchanged_sha256": rel_sha(["tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py",
                                                   "tools/claims-v3/kinds/run_e78.py", "tools/claims-v3/kinds/reduce_e78.py",
                                                   "tools/claims-v3/kinds/kinds.json", "tools/claims-v3/e128/ettelem_guard.sh",
                                                   "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json",
                                                   "tools/claims-v3/kinds/e130/e130.json", "tools/claims-v3/kinds/e130/sha256.txt"]),
            "e145_card_files_sha256": rel_sha([f"tools/claims-v3/e145/{f}" for f in CARD_FILES]),
            "e145_desk_files_sha256": rel_sha([f"tools/claims-v3/e145/{f}" for f in DESK_FILES if os.path.exists(os.path.join(HERE, f))]),
            "e145_tiles_sha256": q["harness"]["e138_tiles_sha256"],
            "box_binaries_sha256": {"build/sparsity/host/sparsity_host": "e0fbecce35f252c546e6e8390f6a4694519674dc4d6dea359b0db9c4d1a3fbbe",
                                    "build/ettelem/ettelem": "8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325"},
            "box_binaries_note": "card 1's binaries as E137 registered and ran them today (predictions-e137.json > harness.box_binaries_sha256), "
                                 "read again on aifoundry1 at 19:04 PST",
            "score_e130_sha256": sha(os.path.join(ROOT, "tools/claims-v3/e130/score_e130.py")),
            "score_e138_sha256": sha(os.path.join(ROOT, "tools/claims-v3/e138/score_e138.py"))},
    }
    # E138's tile list names E138's copy of e130-items.json; E145 runs its own copy (byte-identical, checked here)
    tl = dict(out["harness"]["e145_tiles_sha256"])
    w = tl.pop("tools/claims-v3/e138/e130-items.json", None)
    assert w == sha(os.path.join(HERE, "e130-items.json")) == sha(os.path.join(ROOT, "tools/claims-v3/e130/e130-items.json"))
    tl["tools/claims-v3/e145/e130-items.json"] = w
    out["harness"]["e145_tiles_sha256"] = tl
    json.dump(out, open(os.path.join(HERE, "predictions-e145.json"), "w"), indent=1)
    open(os.path.join(HERE, "predictions-e145.json"), "a").write("\n")
    print(json.dumps({"card0_prices_rail_fJ": card0, "blocks": nB, "precision": {"sd_rail": sd_rail, "sd_beq": sd_beq},
                      "half_widths": {n: round(v["half_width_board_equivalent_fJ"], 3) for n, v in prec.items()}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
