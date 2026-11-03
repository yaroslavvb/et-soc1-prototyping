#!/usr/bin/env python3
"""E147 (Q138): the freeze - every prediction, threshold and rule of E147, and the sha256 of every file the run uses, written
to predictions-e147.json before any E147 block has run. Standard library only. Every number is computed here from committed
files named below (each with its sha256 in `sources`); nothing is typed in but the rules' fixed bands, stated in README.md.
A port of tools/claims-v3/e134/make_predictions_e134.py.

    python3 tools/claims-v3/e147/predict_m6_e147.py         # first (numpy): M6's and M5's predictions, bench/m6-e147.json
    python3 tools/claims-v3/e147/make_predictions_e147.py   # writes tools/claims-v3/e147/predictions-e147.json

MODELS (each item's step over its own zero, board W on aifoundry3 card 0 at 600 MHz):
  m6                 Q137(m)'s M6, frozen (m6.json 87c17e08...), computed mechanically by predict_m6_e147.py from the bench's
                     counts and the tile bytes, exactly as predict_blind4.py computes blind pool 4's: D(item) - D(own zero).
                     E147-M1 scores it. M6's fit left out every single-bit ladder (E134's included), so every E147 item is
                     out of its sample.
  m5                 Q133(b)'s M5, frozen, the same way (reported).
  bench              E134's model: the fixed RTL bench (Q132(b)'s vpu_top, -fno-dfg) run on E147's tiles on the Intel on
                     2 Nov 2026 (bench/counts-e147.json; E134's counts-e134.json for a67q, bj_16 and bp_16), priced with E92's
                     frozen nets_map coefficients at E78's fp32 rate on this card, scale 1 (reported; R4 reads its signs).
  position_only      A: E67's measured list on this card (word W67, all-in), the same at that bit for any word; B: E65's list
                     (a fresh word per bit); scaled to the item's designed flips. The "price is the position's" null.
  count_model        the swing only (all-in minus balanced scaled to the all-in count): the real accumulators' counts
                     (make_e102.exact_counts, in e147-tiles.json) at E88's fp32 result-bit coefficient and E92's flop price.
                     Its level runs high (E102 C4); reported.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REL = lambda p: os.path.relpath(p, ROOT)  # noqa: E731
DATA = "docs/reports/data/2026-11-02-e147-bit-prices-rest"
TILES = "tools/claims-v3/e147/e147/e147-tiles.json"
BENCH = f"{DATA}/bench/counts-e147.json"
BENCH_E134 = "docs/reports/data/2026-11-02-e134-bit-prices-more/bench/counts-e134.json"
M6P = f"{DATA}/bench/m6-e147.json"
BENCH_PRED = "docs/reports/data/2026-11-01-q132-rtl-bench/e92-bench-prediction.json"
E78_JSON = "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json"
E65_HL = "docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/hl.json"
E67_HL = "docs/reports/data/2026-10-27-e67-a-side-bit-prices/hl.json"
E88_FIT = "tools/claims-v3/rpath/e88.json"
E92_PRED = "tools/claims-v3/kinds/predictions-e92.json"
E134_REG = "tools/claims-v3/e134/predictions-e134.json"
E134_SCORED = "docs/reports/data/2026-11-02-e134-bit-prices-more/scored.json"
M6_JSON = "docs/reports/data/2026-11-02-q137m-model/m6.json"
REUSED = ("tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
          "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/kinds.json")
FILES = ("e147_common.py", "run_e147.py", "block_e147.sh", "queue_e147.sh", "run_e147.sh", "reduce_e147.py",
         "score_e147.py", "collect_e147.sh", "make_e147.py", "selftest_e147.py", "predict_m6_e147.py", "m6_on_e134.py",
         "carry_e134.py")
A79_BITS = (8, 9, 10, 12, 13, 14, 15, 17, 18, 19, 21, 24, 25, 26, 28, 29)
A67_BITS = (9, 17, 18, 19)
B_BITS = (1, 2, 3, 4, 5, 17, 18, 19, 21, 24, 25, 26, 28, 29)
B_LINK = (16,)
SCALE_B = 4096 / 3968
SCALE_A = 2048 / 1920
EXP_BITS = (24, 25, 26, 28, 29)


def sha(p):
    return hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()


def load(p):
    return json.load(open(os.path.join(ROOT, p)))


def main():
    spec = load(TILES)
    tiles = spec["tiles"]
    bench = dict(load(BENCH_E134)["rows"])
    bench147 = load(BENCH)["rows"]
    # the bench re-run equals E134's counts on the zeros it re-counted (a check of the bench, not of the card)
    for name in ("fp32.aq", "fp32.hq"):
        a, b = bench147[name]["mean"], bench[name]["mean"]
        assert a["vpu"]["nets_map"] == b["vpu"]["nets_map"] and a["ff"]["all"]["clocked"] == b["ff"]["all"]["clocked"], name
    bench.update(bench147)
    for name, row in bench147.items():
        assert row["mean"].get("check_mismatch", 0) == 0, f"{name}: the bench's accumulator check failed"
    m6 = load(M6P)
    assert m6["m6_sha256"] == sha(M6_JSON), "m6-e147.json was not written from the committed m6.json"
    assert m6["tiles_json_sha256"] == sha(TILES), "m6-e147.json was not written from the committed tile manifest"
    bp = load(BENCH_PRED)["variants"]["nets_map"]
    rate = load(E78_JSON)["items"]["fp32.randn"]["rate"]["mean"]
    e67 = load(E67_HL)["cards"]["aifoundry3"]["a_bits"]
    e65 = load(E65_HL)["cards"]["aifoundry3"]["bits"]
    c88 = load(E88_FIT)["fit"]["fp32"]
    w_res = c88["coef"][c88["features"].index("N_res")]
    w_flop = load(E92_PRED)["models"]["f_w_per_flop_bit_per_op"]

    def bench_w(name):
        m = bench[name]["mean"]
        return (m["vpu"]["nets_map"] * bp["k_fJ_per_net_toggle"] + m["ff"]["all"]["clocked"] * bp["a_fJ_per_clocked_bit"]) * 1e-15 * rate

    items = {}
    for name, t in tiles.items():
        if t["zero"] is None:
            continue
        z, j, fl = t["zero"], t["bit"], t["designed_flips_per_op"]
        mi = m6["items"][name]
        pred = {"m6": mi["M6_step_w"], "m5": mi["M5_step_w"], "bench": bench_w(name) - bench_w(z)}
        if t["side"] == "a":
            pred["position_only"] = e67[str(j)]["dW"] * fl / 2048
        else:
            pred["position_only"] = e65[str(j)]["dW"] * fl / 4096
        ex, exz = t.get("exact"), tiles[z].get("exact")
        items[name] = {"side": t["side"], "layout": t["layout"], "word": t["word"], "bit": j, "zero": z,
                       "designed_flips_per_op": fl, "source": t["source"],
                       "res_bits_over_zero": (ex["res_bits_per_op"] - exz["res_bits_per_op"]) if ex and exz else None,
                       "flops_over_zero": (ex["flops"] - exz["flops"]) if ex and exz else None,
                       "booth_digit_changes": t.get("booth_digit_changes"), "digit_class": t.get("digit_class"),
                       "m6_fJ_per_flip": mi["M6_fJ_per_flip"],
                       "m6_step_terms_w": mi["M6_step_terms_w"],
                       "pred_W": {k: round(v, 4) for k, v in pred.items()}}

    cpred = {}
    cls = spec["a67_choice"]
    for j in A67_BITS:
        c79, c67 = cls[str(j)]["W79"], cls[str(j)]["W67"]
        reading = "+" if (c67, c79) == ("cross", "same") else "-" if (c67, c79) == ("same", "cross") else "0"
        for lay, a, b in (("allin", f"a67j_{j}", f"aj_{j}"), ("bal", f"a67p_{j}", f"ap_{j}")):
            pa, pb = items["fp32." + a]["pred_W"], items["fp32." + b]["pred_W"]
            cpred[f"A_word_{lay}_{j}"] = {k: round(pa[k] - pb[k], 4) for k in ("bench", "m6", "m5", "position_only")}
            cpred[f"A_word_{lay}_{j}"]["reading"] = reading
    for side, bits, aj, ap_, sc in (("A", A79_BITS, "aj", "ap", SCALE_A), ("B", B_BITS + B_LINK, "bj", "bp", SCALE_B)):
        for j in bits:
            a, b = items[f"fp32.{aj}_{j}"], items[f"fp32.{ap_}_{j}"]
            row = {k: round(a["pred_W"][k] - sc * b["pred_W"][k], 4) for k in ("bench", "m6", "m5")}
            if a["res_bits_over_zero"] is not None and b["res_bits_over_zero"] is not None:
                row["res_bits_allin_minus_bal"] = round(a["res_bits_over_zero"] - sc * b["res_bits_over_zero"], 1)
                row["count_model"] = round(w_res * (a["res_bits_over_zero"] - sc * b["res_bits_over_zero"]) +
                                           w_flop * (a["flops_over_zero"] - sc * b["flops_over_zero"]), 4)
            cpred[f"{side}_swing_{j}"] = row

    # R4's bits: where the bench puts the word difference at 0.10 W or more (E134-R5's choice)
    r4_bits = [j for j in A67_BITS if abs(cpred[f"A_word_allin_{j}"]["bench"]) >= 0.10]
    # R5's signs: E134's digit-class reading, from the words alone (make_e147.digit_class)
    r5_signed = {str(j): (1 if cpred[f"A_word_allin_{j}"]["reading"] == "+" else -1)
                 for j in A67_BITS if cpred[f"A_word_allin_{j}"]["reading"] != "0"}
    r5_same = [j for j in A67_BITS if cpred[f"A_word_allin_{j}"]["reading"] == "0"]
    assert len(r5_same) == 1, r5_same

    e134 = load(E134_REG)["harness"]
    reused = {p: sha(p) for p in REUSED}
    assert reused == e134["reused_unchanged_sha256"], "the reused E78 code changed since E134's freeze"
    e134s = load(E134_SCORED)["primary"]["prices"]
    link = {f"{k}_{j}": {"mean": round(e134s[f"{k}_{j}"]["W"]["mean"], 4), "se": round(e134s[f"{k}_{j}"]["W"]["se"], 4)}
            for j in B_LINK for k in ("bj", "bp")}
    tile_files = {TILES: sha(TILES), "tools/claims-v3/e147/e147/sha256.txt": sha("tools/claims-v3/e147/e147/sha256.txt")}
    for name, t in sorted(tiles.items()):
        p = f"tools/claims-v3/e147/e147/{t['file']}"
        tile_files[p] = sha(p)
        assert tile_files[p] == t["sha256"]
    files = {f"tools/claims-v3/e147/{f}": sha(f"tools/claims-v3/e147/{f}") for f in FILES}
    new_items = [n[5:] for n, it in items.items() if it["source"] not in ("E134",)]
    lists = {"new_items": sorted(new_items),
             "A_W79_allin": [f"aj_{j}" for j in A79_BITS], "A_W79_balanced": [f"ap_{j}" for j in A79_BITS],
             "A_W67": [f"a67j_{j}" for j in A67_BITS] + [f"a67p_{j}" for j in A67_BITS],
             "B_allin": [f"bj_{j}" for j in B_BITS], "B_balanced": [f"bp_{j}" for j in B_BITS],
             "mantissa_new": sorted(n for n in new_items if items["fp32." + n]["bit"] <= 22),
             "exponent_new": sorted(n for n in new_items if items["fp32." + n]["bit"] >= 23),
             "B_link": [f"bj_{j}" for j in B_LINK] + [f"bp_{j}" for j in B_LINK]}
    m6j = load(M6_JSON)
    reg = {
        "experiment": "E147", "date": "2026-11-02",
        "request": "Q138 (the owner's words of Mon 2 Nov 2026 ~18:40 PST); kinds page section 11 item 15, the open single-bit positions",
        "card": {"host": "aifoundry3", "card": 0, "clock_mhz": 600, "tdp_w": 0, "threshold_c": 65,
                 "note": "read with ettelem config at the session's start and end and both ends of every block, never set"},
        "units": "board W over the item's own zero; fJ per designed flipped bit; ratios per flipped bit",
        "design": {"A79_bits": list(A79_BITS), "A67_bits": list(A67_BITS), "B_bits": list(B_BITS), "B_link": list(B_LINK),
                   "words": spec["words"], "a67_choice": cls,
                   "balanced_to_allin_flip_scale_B": SCALE_B, "balanced_to_allin_flip_scale_A": SCALE_A,
                   "rate_ops_per_s": rate, "rate_source": f"{E78_JSON} items.fp32.randn.rate.mean (aifoundry3)"},
        "models": ["m6", "m5", "bench", "position_only"],
        "model_notes": {"m6": "Q137(m)'s M6 (G6_gtr_psgn_fields), frozen, via predict_m6_e147.py: D(item) - D(own zero)",
                        "m5": "Q133(b)'s M5, frozen, the same way",
                        "bench": "Q132(b)'s fixed RTL bench, E92's frozen nets_map coefficients, scale 1 on aifoundry3 (E134's model)",
                        "position_only": "A: E67's measured list on this card (word W67); B: E65's list; scaled to designed flips",
                        "count_model": f"swing only: E88 fp32 N_res {w_res:.6g} W per bit an op + E92's {w_flop:.6g} W per flop bit an op",
                        "m6_row_band_w": m6["m6_row_band_w"],
                        "m6_row_band_what": "1.96 x M6's nested rms for fp32 on aifoundry3 (m6.json), the interval M6 claims for one row"},
        "items": items, "contrasts_pred_W": cpred, "lists": lists,
        "published": {"e67_allin_W": {str(j): round(e67[str(j)]["dW"], 4) for j in A67_BITS},
                      "e67_allin_se_W": {str(j): round(e67[str(j)]["se"], 4) for j in A67_BITS},
                      "e65_allin_W": {str(j): round(e65[str(j)]["dW"], 4) for j in B_BITS}},
        "rules": {
            "E147-R1": {"what": "B's low bits carry no accumulator swing: the swing's watts (all-in minus balanced x 4096/3968), their mean over B bits 1-5 paired by block (the registered contrast) and each bit's",
                        "bits": [1, 2, 3, 4, 5], "none_band_w": 0.10,
                        "verdicts": "FLAT if the mean's interval lies inside +-0.10 W and no bit's lower bound exceeds 0.10 W; SWING if the mean's or any bit's lower bound > 0.10 W; else INCONCLUSIVE",
                        "expected": "FLAT (E134-R4: the swing starts at bit 8; the real sums part at no bit below 8)"},
            "E147-R2": {"what": "B's exponent reverses the layouts: all-in / balanced per flipped bit at B bits 24, 25, 26, 28, 29",
                        "bits": list(EXP_BITS), "threshold": 1.0,
                        "verdicts": "INVERTED if every upper bound < 1; NOT INVERTED if any lower bound >= 1; else INCONCLUSIVE",
                        "expected": "INVERTED (E102 card 1: 0.42, 0.30, 0.46 at bits 23, 27, 30)"},
            "E147-R3": {"what": "A's exponent reverses the layouts on W79: all-in / balanced per flipped bit at A bits 24, 25, 26, 28, 29",
                        "bits": list(EXP_BITS), "threshold": 1.0,
                        "verdicts": "INVERTED if every upper bound < 1; NOT INVERTED if any lower bound >= 1; else INCONCLUSIVE",
                        "expected": "INVERTED (E102 card 1: 0.52, 0.31, 0.39 at bits 23, 27, 30)"},
            "E147-R4": {"what": "the bench's word differences above bit 7 (all-in, W67 minus W79; E134-R5's form): at every bit of 9, 17, 18, 19 where the bench puts it at 0.10 W or more",
                        "bits": r4_bits,
                        "verdicts": "AGREES if every bit whose interval excludes zero has the bench's sign and at least half of the bits resolve; DISAGREES if any resolved bit has the other sign; else INCONCLUSIVE",
                        "expected": "AGREES (E134-R5 AGREES at bits 0-7)"},
            "E147-R5": {"what": "E134's digit-class reading above bit 7 (a flip that moves a radix-4 digit between zero-or-positive and negative is dear): the sign of W67 minus W79, all-in, at the bits where one word crosses and the other does not, and no difference at the bit where both make the same digit changes",
                        "signed_bits": r5_signed, "same_bit": r5_same[0], "same_band_w": 0.10, "min_resolved": 2,
                        "verdicts": "HOLDS if every resolved signed bit has the reading's sign, at least 2 resolve, and the same-change bit's interval lies inside +-0.10 W (E134-R2's SAME band); FAILS if a resolved signed bit has the other sign or the same-change bit's interval lies wholly outside +-0.10 W; else INCONCLUSIVE",
                        "expected": "INCONCLUSIVE (the bench puts bit 19 at -0.18 W, between the reading's 0 and its own; HOLDS if the reading is right there)"},
            "E147-M1": {"what": "M6's frozen step at every new position (all new items, both sides, both layouts, both words): rms of measured minus M6, board W",
                        "rms_line_w": round(m6j["families"]["float"]["interval_pool_by_format_card"]["fp32|a3"]["rms_w"], 4),
                        "min_items": 34,
                        "verdicts": "HOLDS if the rms <= M6's own nested rms for fp32 on aifoundry3 (0.245 W); FAILS if above; NOT SCORED under 3 kept blocks of either kind or fewer than 34 items",
                        "expected": "HOLDS (post hoc, M6 reads E134's 54 single-bit items to 0.098 W rms, README)"},
            "E147-S1": {"what": "the session link: E134's bj_16 and bp_16, byte for byte, against E134's primary values (E134-S1's bands)",
                        "e134_W": link, "band_abs_w": 0.15, "band_rel": 0.25, "band_se_mult": 2.0, "min_inside": 2,
                        "verdicts": "PASS if both lie within max(0.15 W, 25% of E134's value, 2 x E134's s.e.) of E134's value; else FAIL",
                        "expected": "PASS"},
        },
        "plan": {"primary": "board p_raw over [t0+1 s, t0+3 s), no temperature term, minus the item's own zero interpolated in time; reduce_e78.py unchanged via reduce_e147.py --drop-dips --dip-w 2.0 (E82 A2's rule at a 2 W line, E134 C1), leakage auto; train gate 0.25 W on the board",
                 "arms": ["rail (rail_raw)", "board p80 (E78's temperature term at the auto slope)", "E134's 4 W dip line (the frame arm)", "dips kept", "gates off (E78's pass gates and the train gate)"],
                 "sequence": [14710, 14720, 14711, 14721, 14712, 14722, 14713, 14723],
                 "smoke_pass": 14701, "stoptest_passes": {"board": 14702, "die": 14703},
                 "runs_per_block": {"A": 68, "B": 49}, "first_estimates_s": {"A": 360, "B": 265},
                 "min_kept_blocks": 3, "train_gate_w": 0.25, "board_power_stop_w": 65.0, "die_stop_c": 70.0, "dip_line_w": 2.0,
                 "budget_s_from_session_start": 2640, "card_minutes_max": 45, "gap_s": 2,
                 "deadline": "2026-11-02 23:45 PST (every run ends by 23:50 PST; no session starts after 23:00 PST)",
                 "fma_s": 4, "train_options": "--preheat 0 --target 200 --quiet-s 0.2 --burnin 0 (E102's trains, E130's, E134's)"},
        "sources": {p: sha(p) for p in (TILES, BENCH, BENCH_E134, M6P, BENCH_PRED, E78_JSON, E65_HL, E67_HL, E88_FIT, E92_PRED,
                                         E134_REG, E134_SCORED, M6_JSON)},
        "harness": {"reused_unchanged_sha256": reused, "binaries_sha256": e134["binaries_sha256"],
                    "e147_files_sha256": files, "e147_tiles_sha256": tile_files},
    }
    out = os.path.join(HERE, "predictions-e147.json")
    json.dump(reg, open(out, "w"), indent=1, sort_keys=False)
    print(json.dumps({"wrote": REL(out), "items": len(items), "new_items": len(new_items), "R4_bits": r4_bits,
                      "R5_signed": r5_signed, "R5_same": r5_same[0], "bench_check": "aq, hq equal E134's counts"}))


if __name__ == "__main__":
    main()
