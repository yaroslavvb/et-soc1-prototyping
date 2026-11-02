#!/usr/bin/env python3
"""E134 (Q136): the freeze - every prediction, threshold and rule of E134, and the sha256 of every file the run uses, written
to predictions-e134.json before any E134 block has run. Standard library only. Every number is computed here from committed
files named below (each with its sha256 in `sources`); nothing is typed in but the rules' fixed bands, stated in README.md.

    python3 tools/claims-v3/e134/make_predictions_e134.py      # writes tools/claims-v3/e134/predictions-e134.json

MODELS (each item's step over its own zero, board W on aifoundry3 card 0 at 600 MHz):
  bench              the fixed RTL bench (Q132(b)'s vpu_top, -fno-dfg) run on E134's 57 tiles on the Intel on 2 Nov 2026
                     (docs/reports/data/2026-11-02-e134-bit-prices-more/bench/counts-e134.json), priced with E92's frozen
                     nets_map coefficients (1.871 fJ per merged-net toggle + 1.092 fJ per clocked register bit, fitted on E78's
                     float kinds alone, on this card), at E78's fp32 rate on this card; card scale 1 (E78's own card). E102's
                     frozen prediction, re-run: on E102's twelve reused tiles its counts equal counts-e102.json's.
  position_only_e67  A side: E67's measured list on this card (its word, W67, all-in, E67's hl.json), the same at that bit
                     for any word, scaled to the item's designed flips. B side: E65's list (fresh words per bit) the same way.
                     It is the "price is the position's" null.
  count_model        B's swing only (all-in minus balanced scaled to 4,096 flips): the real accumulators' counts
                     (make_e102.exact_counts, in e134-tiles.json) priced at E88's fp32 result-bit coefficient and E92's flop
                     price. Known to count some of the same toggles twice (E102 correction C4): its level is high; it is used
                     for WHERE the swing starts, which needs no price.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REL = lambda p: os.path.relpath(p, ROOT)  # noqa: E731
DATA = "docs/reports/data/2026-11-02-e134-bit-prices-more"
TILES = "tools/claims-v3/e134/e134/e134-tiles.json"
BENCH = f"{DATA}/bench/counts-e134.json"
BENCH_E102 = "docs/reports/data/2026-11-01-e102-balanced-bit-prices/bench/counts-e102.json"
BENCH_PRED = "docs/reports/data/2026-11-01-q132-rtl-bench/e92-bench-prediction.json"
E78_JSON = "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json"
E65_HL = "docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/hl.json"
E67_HL = "docs/reports/data/2026-10-27-e67-a-side-bit-prices/hl.json"
E88_FIT = "tools/claims-v3/rpath/e88.json"
E92_PRED = "tools/claims-v3/kinds/predictions-e92.json"
REUSED = ("tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
          "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json")
E130_REG = "tools/claims-v3/e130/predictions-e130.json"     # the registered hashes of the reused code and the two binaries
FILES = ("e134_common.py", "run_e134.py", "block_e134.sh", "queue_e134.sh", "run_e134.sh", "reduce_e134.py",
         "score_e134.py", "collect_e134.sh", "make_e134.py", "selftest_e134.py")
A_BITS = tuple(range(8))
B_BITS = tuple(range(6, 17))
SCALE_B = 4096 / 3968


def sha(p):
    return hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()


def load(p):
    return json.load(open(os.path.join(ROOT, p)))


def main():
    tiles = load(TILES)["tiles"]
    bench = load(BENCH)["rows"]
    b102 = load(BENCH_E102)["rows"]
    bp = load(BENCH_PRED)["variants"]["nets_map"]
    rate = load(E78_JSON)["items"]["fp32.randn"]["rate"]["mean"]
    e67 = load(E67_HL)["cards"]["aifoundry3"]["a_bits"]
    e65 = load(E65_HL)["cards"]["aifoundry3"]["bits"]
    c88 = load(E88_FIT)["fit"]["fp32"]
    i_res = c88["features"].index("N_res")
    w_res = c88["coef"][i_res]                       # W per (result bit per op), E88's fp32 fit
    w_flop = load(E92_PRED)["models"]["f_w_per_flop_bit_per_op"]   # W per (flop bit per op), E92's frozen price

    def bench_w(name):
        m = bench[name]["mean"]
        return (m["vpu"]["nets_map"] * bp["k_fJ_per_net_toggle"] + m["ff"]["all"]["clocked"] * bp["a_fJ_per_clocked_bit"]) * 1e-15 * rate

    # the bench re-run equals E102's frozen counts on every reused tile (a check of the bench, not of the card)
    same = {}
    for name, t in tiles.items():
        if t["source"] == "E102":
            a, b = bench[name]["mean"], b102[name]["mean"]
            same[name] = (a["vpu"]["nets_map"] == b["vpu"]["nets_map"] and a["ff"]["all"]["clocked"] == b["ff"]["all"]["clocked"])
    assert all(same.values()), same

    items = {}
    for name, t in tiles.items():
        if t["zero"] is None:
            continue
        z = t["zero"]
        j = t["bit"]
        fl = t["designed_flips_per_op"]
        pred = {"bench": bench_w(name) - bench_w(z)}
        if t["side"] == "a":
            pred["position_only_e67"] = e67[str(j)]["dW"] * fl / 2048
        else:
            pred["position_only_e65"] = e65[str(j)]["dW"] * fl / 4096
        ex, exz = t["exact"], tiles[z]["exact"]
        items[name] = {"side": t["side"], "layout": t["layout"], "word": t["word"], "bit": j, "zero": z,
                       "designed_flips_per_op": fl, "source": t["source"],
                       "res_bits_over_zero": ex["res_bits_per_op"] - exz["res_bits_per_op"],
                       "flops_over_zero": ex["flops"] - exz["flops"],
                       "booth_digit_changes": t.get("booth_digit_changes"),
                       "pred_W": {k: round(v, 4) for k, v in pred.items()}}

    cpred = {}
    for j in A_BITS:
        for lay, a, b in (("allin", f"a67j_{j}", f"aj_{j}"), ("bal", f"a67p_{j}", f"ap_{j}")):
            pa, pb = items["fp32." + a]["pred_W"], items["fp32." + b]["pred_W"]
            cpred[f"A_word_{lay}_{j}"] = {"bench": round(pa["bench"] - pb["bench"], 4),
                                          "position_only_e67": round(pa["position_only_e67"] - pb["position_only_e67"], 4)}
    for j in B_BITS:
        a, b = items[f"fp32.bj_{j}"], items[f"fp32.bp_{j}"]
        cnt = w_res * (a["res_bits_over_zero"] - SCALE_B * b["res_bits_over_zero"]) + \
            w_flop * (a["flops_over_zero"] - SCALE_B * b["flops_over_zero"])
        cpred[f"B_swing_{j}"] = {"bench": round(a["pred_W"]["bench"] - SCALE_B * b["pred_W"]["bench"], 4),
                                 "count_model": round(cnt, 4),
                                 "res_bits_allin_minus_bal": round(a["res_bits_over_zero"] - SCALE_B * b["res_bits_over_zero"], 1)}

    # R2's contrast and threshold: bit 6, where E67's word read 0.99 W on this card and E79's 0.26 W on card 1
    d6 = cpred["A_word_allin_6"]["bench"]
    # R4's two bits, from the frozen real-sum counts: the onset is the lowest B bit whose all-in result bits exceed
    # 1,000 an op over the balanced layout; the quiet bit is the one below it
    onset = min(j for j in B_BITS if cpred[f"B_swing_{j}"]["res_bits_allin_minus_bal"] > 1000)
    quiet = onset - 1
    assert quiet in B_BITS and cpred[f"B_swing_{quiet}"]["res_bits_allin_minus_bal"] < 100
    # R5's bits: where the bench puts the word difference at 0.10 W or more
    r5_bits = [j for j in A_BITS if abs(cpred[f"A_word_allin_{j}"]["bench"]) >= 0.10]

    e130 = load(E130_REG)["harness"]
    reused = {p: sha(p) for p in REUSED}
    assert reused == e130["reused_unchanged_sha256"], "the reused E78 code changed since E130's freeze"
    tile_files = {TILES: sha(TILES), "tools/claims-v3/e134/e134/sha256.txt": sha("tools/claims-v3/e134/e134/sha256.txt")}
    for name, t in sorted(tiles.items()):
        p = f"tools/claims-v3/e134/e134/{t['file']}"
        tile_files[p] = sha(p)
        assert tile_files[p] == t["sha256"]
    files = {f"tools/claims-v3/e134/{f}": sha(f"tools/claims-v3/e134/{f}") for f in FILES}

    reg = {
        "experiment": "E134", "date": "2026-11-02", "request": "Q136, critic 12 of Q134's final critic; kinds page section 11 item 15",
        "card": {"host": "aifoundry3", "card": 0, "clock_mhz": 600, "tdp_w": 0, "threshold_c": 65,
                 "note": "read with ettelem config at the session's start and end, never set"},
        "units": "board W over the item's own zero; fJ per designed flipped bit; ratios per flipped bit",
        "design": {"A_bits": list(A_BITS), "B_bits": list(B_BITS), "words": load(TILES)["words"],
                   "balanced_to_allin_flip_scale_B": SCALE_B, "rate_ops_per_s": rate,
                   "rate_source": f"{E78_JSON} items.fp32.randn.rate.mean (aifoundry3)"},
        "models": ["bench", "position_only_e67", "position_only_e65"],
        "model_notes": {"bench": "Q132(b)'s fixed RTL bench, E92's frozen nets_map coefficients, scale 1 on aifoundry3",
                        "position_only_e67": "E67's measured A list on this card (word W67), the same for any word",
                        "position_only_e65": "E65's measured B list on this card (a fresh word per bit)",
                        "count_model": f"B swing only: E88 fp32 N_res coefficient {w_res:.6g} W per bit an op + E92's {w_flop:.6g} W per flop bit an op over the real-sum counts"},
        "items": items, "contrasts_pred_W": cpred,
        "published": {"e67_allin_W": {str(j): round(e67[str(j)]["dW"], 4) for j in A_BITS},
                      "e67_allin_se_W": {str(j): round(e67[str(j)]["se"], 4) for j in A_BITS},
                      "e65_allin_W": {str(j): round(e65[str(j)]["dW"], 4) for j in B_BITS}},
        "rules": {
            "E134-R1": {"what": "A's low bits on W79 (E102-R2's low-bit half, on a second card): the ratio all-in / balanced per flipped bit at bits 0 and 6",
                        "bits": [0, 6], "threshold": 4.0,
                        "verdicts": "POSITION if the upper bound < 4 at both; CONSTANT if the lower bound >= 4 at both; else INCONCLUSIVE; NOT SCORED under 3 kept A blocks",
                        "expected": "POSITION (the bench: 1.00 at both; real sums: no result-path change at either; E102 post hoc 0.95 and 0.99 on card 1)"},
            "E134-R2": {"what": "does a single A bit's price depend on its base word? all-in at bit 6, W67 minus W79, board W, paired by block",
                        "contrast": "A_word_allin_6", "bench_W": d6, "sign": 1 if d6 > 0 else -1,
                        "word_threshold_w": round(0.5 * abs(d6), 4), "same_band_w": 0.10,
                        "verdicts": "WORD if the interval's end nearer zero is beyond half the bench's difference, on the bench's side; SAME if the interval lies inside +-0.10 W; else INCONCLUSIVE",
                        "expected": "WORD (the bench and E67 against E102 both say W67 is dearer at bit 6; position-only and the real-sum counts say 0)"},
            "E134-R3": {"what": "where W67's bit-6 cost sits: the ratio all-in / balanced per flipped bit on W67 at bit 6",
                        "ratio": "A_W67_allin_over_bal_6", "flip_band": [0.5, 2.0], "swing_threshold": 2.0,
                        "verdicts": "FLIP if the interval lies inside [0.5, 2.0); SWING if the lower bound >= 2.0; else INCONCLUSIVE",
                        "expected": "FLIP (the word acts through the multiplier, which both layouts drive alike; the sums do not part at bit 6)"},
            "E134-R4": {"what": "where B's accumulator swing starts: the swing's watts (all-in minus balanced x 4096/3968) at the frozen counts' quiet and onset bits",
                        "quiet_bit": quiet, "onset_bit": onset, "none_band_w": 0.10,
                        "verdicts": f"AT {onset} if the quiet bit's interval lies inside +-0.10 W and the onset bit's lower bound > 0; EARLIER if the quiet bit's lower bound > 0; LATER if both lie inside +-0.10 W; else INCONCLUSIVE",
                        "expected": f"AT {onset} (real sums: 0 result bits an op at bit {quiet}, {cpred[f'B_swing_{onset}']['res_bits_allin_minus_bal']:.0f} at bit {onset})"},
            "E134-R5": {"what": "the bench's word differences over A's low bits (all-in, W67 minus W79): at every bit where the bench puts it at 0.10 W or more",
                        "bits": r5_bits,
                        "verdicts": "AGREES if every bit whose interval excludes zero has the bench's sign and at least half of the bits resolve; DISAGREES if any resolved bit has the other sign; else INCONCLUSIVE",
                        "expected": "AGREES"},
            "E134-S1": {"what": "E67's own tiles (W67 all-in, bits 0-7, byte for byte E67's) against E67's list on this card",
                        "band_abs_w": 0.15, "band_rel": 0.25, "band_se_mult": 2.0, "min_inside": 6,
                        "verdicts": "PASS if at least 6 of 8 lie within max(0.15 W, 25% of E67's value, 2 x E67's s.e.) of E67's value; else FAIL",
                        "expected": "PASS"},
        },
        "plan": {"primary": "board p_raw over [t0+1 s, t0+3 s), no temperature term, minus the item's own zero interpolated in time; reduce_e78.py unchanged via reduce_e134.py --drop-dips (E82 A2), leakage auto; train gate 0.25 W on the board",
                 "arms": ["rail (rail_raw)", "board p80 (E78's temperature term at the auto slope)", "dips kept", "gates off (E78's pass gates and the train gate)"],
                 "sequence": [13410, 13420, 13411, 13421, 13412, 13422, 13413, 13423, 13424, 13414],
                 "smoke_pass": 13401, "runs_per_block": {"A": 55, "B": 43}, "first_estimates_s": {"A": 300, "B": 240},
                 "min_kept_blocks": 3, "train_gate_w": 0.25, "board_power_stop_w": 65.0, "die_stop_c": 70.0,
                 "budget_s_from_session_start": 2340, "card_minutes_max": 40, "gap_s": 2,
                 "deadline": "2026-11-02 15:50 PST (every run ends by 16:00 PST; no session starts after 15:00 PST)",
                 "fma_s": 4, "train_options": "--preheat 0 --target 200 --quiet-s 0.2 --burnin 0 (E102's trains, E130's)"},
        "sources": {p: sha(p) for p in (TILES, BENCH, BENCH_E102, BENCH_PRED, E78_JSON, E65_HL, E67_HL, E88_FIT, E92_PRED, E130_REG)},
        "harness": {"reused_unchanged_sha256": reused, "binaries_sha256": e130["binaries_sha256"],
                    "e134_files_sha256": files, "e134_tiles_sha256": tile_files},
    }
    out = os.path.join(HERE, "predictions-e134.json")
    json.dump(reg, open(out, "w"), indent=1, sort_keys=False)
    print(json.dumps({"wrote": REL(out), "R2_bench_d6_W": d6, "R4_quiet_onset": [quiet, onset], "R5_bits": r5_bits,
                      "bench_reuse_check": "equal on all 12 E102 tiles"}))


if __name__ == "__main__":
    main()
