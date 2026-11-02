#!/usr/bin/env python3
"""E138's freeze (Q137): writes predictions-e138.json from E130's frozen registration (tools/claims-v3/e130/predictions-e130.json,
which copies Q136(a)'s d64ea98c number for number), with E138's rules, the rail-per-board constant, the two groups' bands, the
plan and the sha256 of every file E138 runs. Nothing here is fitted to E130's or anyone's card data except where named: c_rb is
E78's frozen constant (reduce_e78.py --c-rb default 0.81, "frozen from E79"), and E130's R2 and R3 are its registered verdicts.

    python3 tools/claims-v3/e138/make_predictions_e138.py
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P130 = os.path.join(ROOT, "tools/claims-v3/e130/predictions-e130.json")
CODE = ["e138_common.py", "run_e138.py", "block_e138.sh", "queue_e138.sh", "run_e138.sh", "reduce_e138.py", "score_e138.py",
        "collect_e138.sh", "make_predictions_e138.py", "e130-items.json"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def hull(nets, group_names, key):
    los = [nets[n]["bands"][key]["lo"] for n in group_names]
    his = [nets[n]["bands"][key]["hi"] for n in group_names]
    return [min(los), max(his)]


def main():
    p = json.load(open(P130))
    nets = p["netlists"]
    on_b = [n for n, v in nets.items() if v["group"] == "Booth on B"]
    off_b = [n for n, v in nets.items() if v["group"] != "Booth on B"]
    assert sorted(on_b) == ["booth", "booth_tree"] and sorted(off_b) == ["booth_swap", "plain"], (on_b, off_b)
    gb = {k: {"booth_on_b": hull(nets, on_b, k), "no_recoder_on_b": hull(nets, off_b, k),
              "what": "the hull of each group's frozen bands over both merges (predictions-e130.json > netlists.<n>.bands)"}
          for k in ("B_odd_minus_even_fJ", "B_odd_over_even")}
    T_B = p["thresholds"]["T_B"]
    c_rb = 0.81
    rules = {
        "E138-R1": {"what": "is B recoded? B's odd bits (1, 3, 5) minus its even bits (0, 2, 4), mean per flipped bit, on the MINION "
                            "RAIL (rail_raw), converted to board-equivalent fJ by dividing by c_rb = 0.81, against E130's T_B",
                    "verdicts": "RECODED if the 95% interval's low end >= T_B; FLAT if its high end <= T_B; else INCONCLUSIVE; "
                                "NOT SCORED under 3 kept B blocks", "threshold": T_B["value"],
                    "same_in_rail_fJ": T_B["value"] * c_rb},
        "E138-R1n": {"what": "the same board-equivalent interval against the two groups' frozen bands (group_bands.B_odd_minus_even_fJ)",
                     "verdicts": "IN BOOTH ON B's BAND if it overlaps that band only; IN NO RECODER's BAND if it overlaps the other "
                                 "only; NEITHER (BETWEEN / ABOVE / BELOW) if it overlaps neither; INCONCLUSIVE if both; NOT SCORED "
                                 "under 3 kept B blocks"},
        "E138-R1q": {"what": "B's odd / even on the rail (Fieller, paired over blocks): a ratio of two rail readings, so no unit and no "
                             "c_rb; against group_bands.B_odd_over_even",
                     "verdicts": "as E138-R1n; NOT SCORED if the Fieller interval is unbounded"},
        "E138-R4": {"what": "which multiplier: E138-R1 with E130's registered R2 FLAT and R3 RISES (E130's primary, lab b259be11)",
                    "verdicts": "R1 RECODED: BOOTH ON B; R1 FLAT: NO BOOTH; R1 INCONCLUSIVE: INCONCLUSIVE between BOOTH ON B / NO "
                                "BOOTH; NOT SCORED if R1 is"},
    }
    seq = list(range(13810, 13820))
    out = {
        "experiment": "E138", "date": "2026-11-02",
        "request": "Q137 (prediction is the goal); the kinds page's section 11, item 12 ('int8 at gate level'): settle E130's B side",
        "card": "aifoundry3 card 0, 600 MHz as its boot-time TDP of 0 latches it, TDP 0 / threshold 65 C as read, never set",
        "units": "fJ per flipped bit; the primary is the minion rail, converted to board-equivalent fJ at c_rb = 0.81",
        "source": {"e130_registration": "tools/claims-v3/e130/predictions-e130.json", "e130_registration_sha256": sha(P130),
                   "q136a_freeze": p["source"]},
        "netlists": nets, "thresholds": p["thresholds"], "group_bands": gb, "shared_bands": p["shared_bands"],
        "separators": p["separators"], "rules": rules,
        "e130_registered_verdicts_used": {"E130-R2": "FLAT", "E130-R3": "RISES", "commit": "b259be11"},
        "expected": {"E138-R1": "INCONCLUSIVE", "E138-R1n": "NEITHER (BETWEEN)", "E138-R1q": "NEITHER (BETWEEN)",
                     "E138-R4": "INCONCLUSIVE between BOOTH ON B / NO BOOTH",
                     "why": "E130's rail arm read +26.9 [+23.9, +29.8] rail-fJ over 6 blocks, +33.2 [+29.6, +36.7] board-equivalent at "
                            "0.81, 2.5 fJ above T_B; with 9 blocks at E130's rail block sd (2.77 rail fJ) the half-width is about "
                            "2.6 board-equivalent fJ, so R1 RECODED needs the mean to stay above about 33.3: close to even odds. "
                            "Both bands lie 20 fJ and more from that interval, and E130's rail ratio 1.79 [1.68, 1.92] lies between "
                            "the ratio bands."},
        "plan": {
            "primary": "minion rail rail_raw over [t0+2 s, t0+4 s), no temperature term, minus the item's own zero interpolated in "
                       "time, divided by designed flips x the run's rate, then by c_rb = 0.81; reduce_e78.py unchanged via "
                       "reduce_e138.py --drop-dips (E82 A2), leakage auto; E78's per-run and pass gates; E130's train gate (0.25 W on "
                       "the board's p_raw)",
            "c_rb": c_rb,
            "arms": ["board (p_raw: E130's primary)", "board_p80", "rail_dips_kept", "rail_gates_off",
                     "pool: E130's six rail B blocks with E138's (reported only; E130's rail was seen before this freeze)"],
            "sequence": seq, "blocks": "B only (E130's B block design, its order seeded Random('E138|aifoundry3|<pass>'))",
            "smoke_pass": 13801, "runs_per_block": {"B": 34}, "first_estimates_s": {"B": 200}, "min_kept_blocks": 3,
            "train_gate_w": 0.25, "board_power_stop_w": 65.0, "die_stop_c": 70.0, "budget_s_from_session_start": 1740,
            "card_minutes_max": 30, "gap_s": 5,
            "deadline": "2026-11-02 21:40 PST (no session starts after 21:00 PST; every run ends by 21:45 PST)",
            "fma_s": 4, "train_options": "--preheat 0 --target 200 --quiet-s 0.2 --burnin 0 (E102's int8 block I)"},
        "harness": {"reused_unchanged_sha256": p["harness"]["reused_unchanged_sha256"],
                    "binaries_sha256": p["harness"]["binaries_sha256"],
                    "score_e130_sha256": sha(os.path.join(ROOT, "tools/claims-v3/e130/score_e130.py")),
                    "e138_files_sha256": {f"tools/claims-v3/e138/{f}": sha(os.path.join(HERE, f)) for f in CODE
                                          if os.path.exists(os.path.join(HERE, f))},
                    "e138_tiles_sha256": p["harness"]["e130_tiles_sha256"] | {
                        "tools/claims-v3/e138/e130-items.json": sha(os.path.join(HERE, "e130-items.json"))}},
    }
    assert sha(os.path.join(HERE, "e130-items.json")) == sha(os.path.join(ROOT, "tools/claims-v3/e130/e130-items.json"))
    out["harness"]["e138_tiles_sha256"].pop("tools/claims-v3/e130/e130-items.json", None)
    json.dump(out, open(os.path.join(HERE, "predictions-e138.json"), "w"), indent=1)
    open(os.path.join(HERE, "predictions-e138.json"), "a").write("\n")
    print("T_B", T_B["value"], "rail", T_B["value"] * c_rb, "group bands", json.dumps(gb))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
