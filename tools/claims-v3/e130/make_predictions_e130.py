#!/usr/bin/env python3
"""E130 (Q136): the freeze. Desk compute only; nothing here opens a card. Writes, from committed files only:

  tools/claims-v3/e130/e130-items.json      Q136(a)'s 26 tiles as E130's items: every field copied from
                                            tools/claims-v3/kinds/e130/e130.json, plus each half's sha256 (computed here
                                            from the committed tile files, whose whole-file sha256 must equal e130.json's)
  tools/claims-v3/e130/predictions-e130.json the four netlists' frozen predictions, copied number for number from Q136(a)'s
                                            predictions.json (docs/reports/data/2026-11-02-q136a-int8-netlist-predictions/,
                                            frozen in d64ea98c, sha256 checked), the rules' thresholds and each netlist's
                                            band derived from them, the plan, and the sha256 of every file the run uses

    python3 tools/claims-v3/e130/make_predictions_e130.py

THE THRESHOLDS are midpoints between the two groups' NEAREST frozen predictions over both merges (nets_map, nets_hier):
  T_B (E130-R1) on B's odd - even: between Booth on B (booth, booth_tree) and the rest (booth_swap, plain);
  T_A (E130-R2) on A's odd - even: between Booth on A (booth_swap) and the rest;
  T_S (E130-R3) on A's sign step with the dense held B (B = 0x55 minus B = 1): between booth_swap and the rest.
THE BANDS (per netlist, per statistic or item): the hull of its nets_map and nets_hier values, each widened by twice k's
relative jackknife s.e. for a value in fJ (a level or a difference carries k; a ratio does not and is not widened).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
Q = "docs/reports/data/2026-11-02-q136a-int8-netlist-predictions/predictions.json"
Q_SHA = "e009571db4180faebcb6dd7be793a83958bc8e5f7b5876979296c918361980fe"     # as committed in d64ea98c, unchanged since
TILES = "tools/claims-v3/kinds/e130"
MAN_SHA = "bcbced62117ac4d10c42d077c6d3344edff1a7c42ae38aa58eb5be1dda86092e"
REUSED = {   # E78's card code and reduction, unchanged (E127's registration of this morning holds the same values)
    "tools/claims-v3/lib.sh": "033d07762548c4abad0bb1721d338bb2333e58d6f07bc0d9a93bdcac0301eaaa",
    "tools/claims-v3/kinds/e78_common.py": "c58923a522849ea033a2d14b7981b0589bcd8a1d5c3129e608d3a418578a552e",
    "tools/claims-v3/kinds/run_e78.py": "f3efd7838686dbd158c8f45a82ab59f4beda68479d792d73a36265e48784bb73",
    "tools/claims-v3/kinds/reduce_e78.py": "6a158ceedc000fae884762d7e273231bfd4e4f42c09bf0b0723afc2da6c05d39",
    "tools/claims-v3/kinds/kinds.json": "9586568f23a97757e34b3cdacdffe5bee0122d236e28a9f76f06e8598b7b1337",
}
BINARIES = {   # aifoundry3's tree, the binaries E127's device-command list was classified for (its run_e127.sh setup read them)
    "build/ettelem/ettelem": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2",
    "build/sparsity/host/sparsity_host": "20e760c20e9b99c789ef96f1e4e950d51f534410275bfb933c2aaf96d1090fd0",
}
CODE = ("e130_common.py", "run_e130.py", "block_e130.sh", "queue_e130.sh", "run_e130.sh", "reduce_e130.py", "score_e130.py",
        "selftest_e130.py", "collect_e130.sh", "make_predictions_e130.py")
NETS = ("booth_tree", "booth", "booth_swap", "plain")
GROUP_OF = {"booth_tree": "booth_on_b", "booth": "booth_on_b", "booth_swap": "booth_on_a", "plain": "no_booth"}
SEPARATORS = ("B_odd_minus_even_fJ", "A_odd_minus_even_fJ", "A_sign_dense_minus_one_fJ")
STATS = ("B_odd_minus_even_fJ", "A_odd_minus_even_fJ", "A_sign_dense_minus_one_fJ", "B_sign_dense_minus_one_fJ",
         "B_mean_bits0to6_fJ", "A_mean_bits0to6_fJ", "B_sign_w2_minus_w1_fJ", "A_sign_w2_minus_w1_fJ",
         "B_odd_over_even", "A_odd_over_even", "B_sign_w2_over_w1", "A_sign_w2_over_w1", "B_sign_dense_over_one",
         "A_sign_dense_over_one")
ITEM_ORDER = tuple([f"b1_{j}" for j in range(8)] + ["b2_7", "b1d_7"] + [f"a1_{j}" for j in range(8)] + ["a2_7", "a1d_7"])


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def band(vals, rel):
    """Hull of the merges' values, each widened by 2 x rel x |value| (rel = 0 for a ratio)."""
    lo = min(v - 2 * rel * abs(v) for v in vals)
    hi = max(v + 2 * rel * abs(v) for v in vals)
    return {"lo": lo, "hi": hi, "map": vals[0], "hier": vals[1]}


def main():
    qp = os.path.join(ROOT, Q)
    if sha(qp) != Q_SHA:
        raise SystemExit(f"{Q} differs from Q136(a)'s freeze")
    man_p = os.path.join(ROOT, TILES, "e130.json")
    if sha(man_p) != MAN_SHA:
        raise SystemExit("tools/claims-v3/kinds/e130/e130.json differs from Q136(a)'s freeze")
    q = json.load(open(qp))
    man = json.load(open(man_p))
    # ---- the items
    tiles = []
    for it in man["items"]:
        b = open(os.path.join(ROOT, TILES, it["file"]), "rb").read()
        if hashlib.sha256(b).hexdigest() != it["sha256"] or len(b) != 2048:
            raise SystemExit(f"{it['kind']}: tile file differs from e130.json")
        if it["sha256"] != q["inputs"]["tiles"][it["kind"]]:
            raise SystemExit(f"{it['kind']}: e130.json and predictions.json name different tiles")
        tiles.append({"tile": it["kind"], "file": it["file"], "bytes": len(b), "sha256": it["sha256"],
                      "sha256_a": hashlib.sha256(b[:1024]).hexdigest(), "sha256_b": hashlib.sha256(b[1024:]).hexdigest(),
                      "side": it["side"], "bit": it["bit"], "zero": it["zero"], "base_word": it["base_word"],
                      "held": it["held"], "designed_flips_per_op": it["designed_flips_per_op"], "rule": it["rule"]})
    items_doc = {"experiment": "E130", "written_by": "tools/claims-v3/e130/make_predictions_e130.py",
                 "source": f"{TILES}/e130.json (Q136(a), lab commit d64ea98c), sha256 {MAN_SHA}; the halves' sha256 added here",
                 "tiles_dir": TILES, "tiles": tiles}
    ip = os.path.join(HERE, "e130-items.json")
    json.dump(items_doc, open(ip, "w"), indent=1)
    open(ip, "a").write("\n")
    # ---- the netlists' predictions, copied
    nets = {}
    for n in NETS:
        arm = q["arms"][n]
        k = q["inputs"]["k_fJ_per_net_toggle"][n]
        kse = q["inputs"]["k_jackknife_se_fJ"][n]
        rel = kse / k
        e = {"group": arm["group"], "group_key": GROUP_OF[n], "k_fJ_per_net_toggle": k, "k_se": kse, "k_rel_se": rel,
             "items": {}, "stats": {"map": {}, "hier": {}}, "bands": {}}
        for t in ITEM_ORDER:
            x = arm["items"][t]
            e["items"][t] = {"fJ_map": x["fJ_map"], "fJ_hier": x["fJ_hier"], "dW_map": x["dW_map"], "dW_hier": x["dW_hier"],
                             "flips_per_op": x["flips_per_op"], "zero": x["zero"]}
            bd = band([x["fJ_map"], x["fJ_hier"]], rel)
            e["items"][t]["band_lo"], e["items"][t]["band_hi"] = bd["lo"], bd["hi"]
        for m in ("map", "hier"):
            for s in STATS:
                e["stats"][m][s] = arm["stats"][m][s]
        for s in STATS:
            e["bands"][s] = band([arm["stats"]["map"][s], arm["stats"]["hier"][s]], rel if s.endswith("_fJ") else 0.0)
        nets[n] = e

    def vals(stat, which):
        return [nets[n]["stats"][m][stat] for n in which for m in ("map", "hier")]

    b_rec = [n for n in NETS if GROUP_OF[n] == "booth_on_b"]
    not_b = [n for n in NETS if GROUP_OF[n] != "booth_on_b"]
    a_rec = [n for n in NETS if GROUP_OF[n] == "booth_on_a"]
    not_a = [n for n in NETS if GROUP_OF[n] != "booth_on_a"]
    TB = (max(vals("B_odd_minus_even_fJ", not_b)) + min(vals("B_odd_minus_even_fJ", b_rec))) / 2
    TA = (max(vals("A_odd_minus_even_fJ", not_a)) + min(vals("A_odd_minus_even_fJ", a_rec))) / 2
    TS = (max(vals("A_sign_dense_minus_one_fJ", a_rec)) + min(vals("A_sign_dense_minus_one_fJ", not_a))) / 2
    thresholds = {
        "T_B": {"value": TB, "statistic": "B_odd_minus_even_fJ", "low_group_max": max(vals("B_odd_minus_even_fJ", not_b)),
                "high_group_min": min(vals("B_odd_minus_even_fJ", b_rec)),
                "what": "midpoint between Booth on B's lowest prediction and the others' highest, over both merges"},
        "T_A": {"value": TA, "statistic": "A_odd_minus_even_fJ", "low_group_max": max(vals("A_odd_minus_even_fJ", not_a)),
                "high_group_min": min(vals("A_odd_minus_even_fJ", a_rec)),
                "what": "midpoint between booth_swap's lowest prediction and the others' highest, over both merges"},
        "T_S": {"value": TS, "statistic": "A_sign_dense_minus_one_fJ",
                "low_group_max": max(vals("A_sign_dense_minus_one_fJ", a_rec)),
                "high_group_min": min(vals("A_sign_dense_minus_one_fJ", not_a)),
                "what": "midpoint between booth_swap's highest prediction and the others' lowest, over both merges"},
    }
    shared = {}
    for s in ("A_sign_w2_over_w1", "B_sign_w2_over_w1"):
        v = vals(s, NETS)
        shared[s] = {"lo": min(v), "hi": max(v), "what": "the hull of the four netlists' predictions over both merges"}

    def verdict_of(n, stat, T, hi_w, lo_w):
        v = [nets[n]["stats"][m][stat] for m in ("map", "hier")]
        return hi_w if min(v) >= T else lo_w if max(v) <= T else "INCONCLUSIVE"
    for n in NETS:
        nets[n]["predicted_verdicts"] = {
            "E130-R1": verdict_of(n, "B_odd_minus_even_fJ", TB, "RECODED", "FLAT"),
            "E130-R2": verdict_of(n, "A_odd_minus_even_fJ", TA, "RECODED", "FLAT"),
            "E130-R3": verdict_of(n, "A_sign_dense_minus_one_fJ", TS, "RISES", "FLAT")}
    groups = {"booth_on_b": {"E130-R1": "RECODED", "E130-R2": "FLAT", "E130-R3": "RISES"},
              "booth_on_a": {"E130-R1": "FLAT", "E130-R2": "RECODED", "E130-R3": "FLAT"},
              "no_booth": {"E130-R1": "FLAT", "E130-R2": "FLAT", "E130-R3": "RISES"}}
    for n in NETS:
        assert nets[n]["predicted_verdicts"] == groups[GROUP_OF[n]], (n, nets[n]["predicted_verdicts"])
    rules = {
        "E130-R1": {"what": "is B recoded? B's odd bits (1, 3, 5) minus its even bits (0, 2, 4), mean per flipped bit, board fJ",
                    "statistic": "B_odd_minus_even_fJ", "threshold": "T_B",
                    "verdicts": "RECODED if the 95% interval's low end >= T_B; FLAT if its high end <= T_B; else INCONCLUSIVE; "
                                "NOT SCORED under 3 kept B blocks"},
        "E130-R2": {"what": "is A recoded? A's odd bits minus its even bits", "statistic": "A_odd_minus_even_fJ", "threshold": "T_A",
                    "verdicts": "RECODED if low end >= T_A; FLAT if high end <= T_A; else INCONCLUSIVE; NOT SCORED under 3 kept A blocks"},
        "E130-R3": {"what": "does A's sign bit price rise with a dense held B (B = 0x55 minus B = 1)? It does where A is the multiplicand "
                            "of every partial-product row, i.e. where A is not recoded",
                    "statistic": "A_sign_dense_minus_one_fJ", "threshold": "T_S",
                    "verdicts": "RISES if low end >= T_S; FLAT if high end <= T_S; else INCONCLUSIVE; NOT SCORED under 3 kept A blocks"},
        "E130-R4": {"what": "which multiplier (the registered primary): the group whose three predicted verdicts no decided rule contradicts",
                    "groups": groups, "names": {"booth_on_b": "BOOTH ON B", "booth_on_a": "BOOTH ON A", "no_booth": "NO BOOTH"},
                    "verdicts": "one group left with R1-R3 all decided: that group; one left with some INCONCLUSIVE: that group, "
                                "with '(n of 3 rules decided)'; none left: NONE OF THE FOUR; two or more: INCONCLUSIVE between them; "
                                "NOT SCORED if R1 or R2 is"},
        "E130-R5": {"what": "the shared prediction, A: the sign bit priced the same at both base words (a2_7 / a1_7, Fieller, paired)",
                    "statistic": "A_sign_w2_over_w1", "band": "shared_bands.A_sign_w2_over_w1",
                    "verdicts": "HOLDS if the 95% interval overlaps the band; FAILS (ABOVE or BELOW) if not; NOT SCORED if unbounded "
                                "or under 3 kept A blocks"},
        "E130-R6": {"what": "the shared prediction, B: b2_7 / b1_7", "statistic": "B_sign_w2_over_w1",
                    "band": "shared_bands.B_sign_w2_over_w1", "verdicts": "as E130-R5, on B blocks"},
        "E130-N": {"what": "each netlist's frozen prediction scored (reported per netlist, not a verdict on the multiplier): each "
                           "separating statistic against the netlist's own band",
                   "verdicts": "SURVIVES if CONSISTENT (interval overlaps band) on all three separators; else EXCLUDED by the ones "
                               "it misses; every other statistic and every item are reported CONSISTENT / ABOVE / BELOW beside"},
    }
    files = {f"tools/claims-v3/e130/{f}": sha(os.path.join(HERE, f)) for f in CODE if os.path.exists(os.path.join(HERE, f))}
    tiles_sha = {f"{TILES}/{t['file']}": t["sha256"] for t in tiles}
    tiles_sha[f"{TILES}/e130.json"] = MAN_SHA
    tiles_sha[f"{TILES}/sha256.txt"] = sha(os.path.join(ROOT, TILES, "sha256.txt"))
    tiles_sha["tools/claims-v3/e130/e130-items.json"] = sha(ip)
    for rel, want in REUSED.items():
        if sha(os.path.join(ROOT, rel)) != want:
            raise SystemExit(f"{rel} differs from E78's freeze")
    out = {
        "experiment": "E130", "date": "2026-11-02",
        "request": "Q136, critic 8 of Q134's final critic; the kinds page's section 11, item 12 ('int8 at gate level': which multiplier)",
        "card": "aifoundry3 card 0, 600 MHz as its boot-time TDP of 0 latches it, TDP 0 / threshold 65 C as read, never set",
        "units": "fJ per flipped bit on the board (aifoundry3's board meter), the footing of Q136(a)'s k (E78's board watts on this card)",
        "source": {"predictions": Q, "predictions_sha256": Q_SHA, "frozen_in": "d64ea98c (07:48 PST), corrections in 8ab2ed9d change no number",
                   "primary_there": q["inputs"]["primary"], "rate_ops_per_s": q["inputs"]["rate_ops_per_s"]},
        "netlists": nets, "thresholds": thresholds, "shared_bands": shared, "separators": list(SEPARATORS),
        "statistics": list(STATS), "item_order": list(ITEM_ORDER), "rules": rules,
        "card_precision_e79": q["card_precision_e79"],
        "expected": {
            "E130-R1": "RECODED", "E130-R2": "FLAT", "E130-R3": "RISES", "E130-R4": "BOOTH ON B", "E130-R5": "HOLDS", "E130-R6": "HOLDS",
            "why": "E79 (this card) and E102 (aifoundry1 card 1) read B's odd bits at about 2.8x its even bits and A's list flat, "
                   "at E79's base words; E130's words are new, and this is the frozen guess, not a prior on the rules",
            "per_netlist": "booth and booth_tree SURVIVE on R1-R3's statistics or are EXCLUDED only by B's amplitude (E79's odd - even, "
                           "+40 board-fJ, was 0.7x the netlists' +60); booth_swap and plain are EXCLUDED by B's odd - even"},
        "plan": {
            "primary": "board p_raw over [t0+1 s, t0+3 s), no temperature term, minus the item's own zero interpolated in time; "
                       "reduce_e78.py unchanged via reduce_e130.py --drop-dips (E82 A2), leakage auto; train gate 0.25 W on the board",
            "arms": ["rail (rail_raw)", "board p80 (E78's temperature term at the auto slope)", "dips kept", "gates off (E78's pass "
                     "gates and the train gate)"],
            "sequence": [13010, 13020, 13011, 13021, 13012, 13022, 13013, 13023, 13014, 13015],
            "smoke_pass": 13001, "runs_per_block": {"B": 34, "A": 25}, "first_estimates_s": {"B": 200, "A": 160},
            "min_kept_blocks": 3, "train_gate_w": 0.25, "board_power_stop_w": 65.0, "die_stop_c": 70.0,
            "budget_s_from_session_start": 1740, "card_minutes_max": 30, "gap_s": 5,
            "deadline": "2026-11-02 15:50 PST (every run ends by 16:00 PST; no session starts after 15:00 PST)",
            "fma_s": 4, "train_options": "--preheat 0 --target 200 --quiet-s 0.2 --burnin 0 (E102's int8 block I)"},
        "harness": {"reused_unchanged_sha256": REUSED, "binaries_sha256": BINARIES, "e130_files_sha256": files,
                    "e130_tiles_sha256": tiles_sha},
    }
    json.dump(out, open(os.path.join(HERE, "predictions-e130.json"), "w"), indent=1)
    open(os.path.join(HERE, "predictions-e130.json"), "a").write("\n")
    print(f"T_B {TB:.2f}  T_A {TA:.2f}  T_S {TS:.2f} fJ; shared bands {json.dumps(shared)}")
    for n in NETS:
        print(n, nets[n]["predicted_verdicts"], {s: (round(nets[n]['bands'][s]['lo'], 2), round(nets[n]['bands'][s]['hi'], 2)) for s in SEPARATORS})
    return 0


if __name__ == "__main__":
    sys.exit(main())
