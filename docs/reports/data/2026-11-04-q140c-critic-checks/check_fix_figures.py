#!/usr/bin/env python3
"""Q140(c), after its verifier (Wed 4 Nov 2026): the figures this folder's dated corrections quote, derived from its own
committed check outputs. Post hoc, desk only; nothing registered, no number re-measured. Standard library; reads only.

  check 1 (check1-exponent-e160.json): how far the board exponent moves E160's pinned board, pinned clock and the die's
           rise per arm, against M7 as frozen (A0); and the governed clock's mean error by model and session.
  check 2 (check2-pool6-named-misses.json): the six named-miss tiles' cut of the rms and their share of the summed squared
           error per card and model (computed twice: from the two rms values, and from the six tiles' own errors); the
           30 kinds' rms against a mean fp32 kind and each format's own share; the B-held and near-whole-byte tiles per
           model and card; and `fp32.b_onebit_b20_third`'s range over the models and both cards.

Usage, from the repository root:
  python3 -I -B docs/reports/data/2026-11-04-q140c-critic-checks/check_fix_figures.py . \
      --out docs/reports/data/2026-11-04-q140c-critic-checks/check-fix-figures.json \
      > docs/reports/data/2026-11-04-q140c-critic-checks/check-fix-figures.txt
"""
import json
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
OUT = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
DIR = ROOT + "/docs/reports/data/2026-11-04-q140c-critic-checks/"
C1 = json.load(open(DIR + "check1-exponent-e160.json", encoding="utf-8"))
C2 = json.load(open(DIR + "check2-pool6-named-misses.json", encoding="utf-8"))
CARDS = ("aifoundry3", "aifoundry1c1")
MODELS = ("M8", "M7", "M6")
out = {"_note": "Q140(c) after its verifier: post hoc figures derived from check1-exponent-e160.json and "
                "check2-pool6-named-misses.json (this folder); nothing registered, no number re-measured.",
       "inputs": ["check1-exponent-e160.json", "check2-pool6-named-misses.json"]}

print("Q140(c), AFTER ITS VERIFIER: FIGURES FOR THE DATED CORRECTIONS (post hoc; from this folder's committed check outputs)")

# ---------------------------------------------------------------- check 1: what the exponent moves outside the governed clock
print("\nCHECK 1. E160, each arm against A0 (M7 as frozen): rms of measured - predicted")
print(f"  {'arm':44s} {'pinned board W':>22s} {'pinned clock MHz':>24s} {'die rise C, all 48':>24s} {'governed board W':>22s}")
a0 = C1["E160"]["A0_M7_frozen"]
moves = {}
for arm in ("A2_n2.00_chain_refit", "A5_n2.28_chain_on_committed_powers", "A5c_n2.28_chain_on_E66_rereferred_powers",
            "A4c_ramp_slopes_at_E66_slope_rereferred", "A3_n2.43_chain_refit"):
    s = C1["E160"][arm]
    m = {"pinned_board_w": [a0["pinned"]["w_rms"], s["pinned"]["w_rms"]],
         "pinned_clock_mhz": [a0["pinned"]["mhz_rms"], s["pinned"]["mhz_rms"]],
         "rise_all_c": [a0["all"]["rise_rms"], s["all"]["rise_rms"]],
         "governed_board_w": [a0["governed"]["w_rms"], s["governed"]["w_rms"]]}
    moves[arm] = {k: {"A0": v[0], "arm": v[1], "move": v[1] - v[0]} for k, v in m.items()}
    cells = [f"{v[0]:.3f} -> {v[1]:.3f} ({v[1] - v[0]:+.3f})" for v in m.values()]
    print(f"  {arm:44s} {cells[0]:>22s} {cells[1]:>24s} {cells[2]:>24s} {cells[3]:>22s}")
out["check1_moves_against_A0_E160"] = moves
print("  So at n = 2.28 (A5) the pinned board moves +%.3f W, the pinned clock %+.3f MHz and the die's rise %+.3f C; at n = 2.43 (A3) "
      "%+.3f W, %+.3f MHz and %+.3f C." % tuple(moves[a][k]["move"] for a in ("A5_n2.28_chain_on_committed_powers",
                                                                             "A3_n2.43_chain_refit")
                                                for k in ("pinned_board_w", "pinned_clock_mhz", "rise_all_c")))
sg = {"M7 (A0) on E143": C1["E143"]["A0_M7_frozen"]["governed"]["mhz_mean"],
      "M7 on E143, registered F1": C1["E143_registered"]["E143-F1"]["mean_err"],
      "M7 (A0) on E160": C1["E160"]["A0_M7_frozen"]["governed"]["mhz_mean"],
      "M8 on E160, registered F1": C1["E160_registered_M8"]["E160-F1"]["mean_err"]}
out["check1_governed_clock_mean_error_by_model"] = sg
print("  The governed clock's mean error by model and session (MHz): " + "; ".join(f"{k} {v:+.3f}" for k, v in sg.items()))
print("  (M8 was frozen after E143 ran, so E143 has no M8 score.)")

# ---------------------------------------------------------------- check 2: the six tiles' share, the shares of watts, the tiles
print("\nCHECK 2. POOL 6's 30 PRIORITY-1 NEW KINDS: what the six named-miss tiles carry (W)")
six = C2["six"]
res2 = {}
for c in CARDS:
    for mo in MODELS:
        q = C2[c]["models"][mo]
        r30, r24 = q["rms30"], q["rms24_without_six"]
        share_from_rms = 1.0 - 24.0 * r24 ** 2 / (30.0 * r30 ** 2)
        share_from_tiles = sum(C2[c]["tiles"][t][mo] ** 2 for t in six) / (30.0 * r30 ** 2)
        assert abs(share_from_rms - share_from_tiles) < 1e-9, (c, mo, share_from_rms, share_from_tiles)
        res2[f"{c}.{mo}"] = {"rms30": r30, "rms24_without_six": r24, "rms_cut": 1.0 - r24 / r30,
                             "six_share_of_squared_error": share_from_rms,
                             "rms24_without_own_six_worst": q["rms24_without_own_six_worst"]}
        print(f"  {c:12s} {mo}: rms {r30:.3f} -> {r24:.3f} without the six, a cut of {100 * (1 - r24 / r30):.0f}%; the six carry "
              f"{100 * share_from_rms:.0f}% of the summed squared error (from their own errors: {100 * share_from_tiles:.0f}%); "
              f"each model's own six worst removed {q['rms24_without_own_six_worst']:.3f}")
cuts = [v["rms_cut"] for v in res2.values()]
shares = [v["six_share_of_squared_error"] for v in res2.values()]
out["check2_six_tiles"] = res2
out["check2_six_tiles_range"] = {"rms_cut": [min(cuts), max(cuts)], "share_of_squared_error": [min(shares), max(shares)]}
print(f"  Over both cards and three models: the six (a fifth of the 30 tiles) cut the rms by {100 * min(cuts):.0f}-"
      f"{100 * max(cuts):.0f}% and carry {100 * min(shares):.0f}-{100 * max(shares):.0f}% of the summed squared error.")

print("\n  The 30 kinds' rms against a mean fp32 kind, and each format's own rms over its mean kind (M8):")
res_sh = {}
for c in CARDS:
    q = C2[c]["models"]["M8"]
    bf = q["by_format"]
    r = {"rms30": q["rms30"], "mean_fp32_kind_w": bf["fp32"]["mean_measured_D_w"],
         "rms30_over_mean_fp32_kind": q["rms30"] / bf["fp32"]["mean_measured_D_w"],
         "by_format": {f: {"rms30": bf[f]["rms30"], "mean_kind_w": bf[f]["mean_measured_D_w"],
                           "share": bf[f]["rms30"] / bf[f]["mean_measured_D_w"]} for f in ("fp32", "fp16", "int8")}}
    for f in ("fp32", "fp16", "int8"):
        assert abs(r["by_format"][f]["share"] - bf[f]["rms30_over_mean_D"]) < 1e-12
    res_sh[c] = r
    print(f"  {c:12s}: all 30 {r['rms30']:.3f} W = {100 * r['rms30_over_mean_fp32_kind']:.1f}% of a mean fp32 kind "
          f"({r['mean_fp32_kind_w']:.2f} W); per format " + ", ".join(
              f"{f} {r['by_format'][f]['rms30']:.3f} W of {r['by_format'][f]['mean_kind_w']:.2f} W = "
              f"{100 * r['by_format'][f]['share']:.1f}%" for f in ("fp32", "fp16", "int8")))
out["check2_shares_M8"] = res_sh

print("\n  The named-miss tiles, error per model (M8 / M7 / M6, W), |error| >= 0.2 W marked *:")
tl = {}
for t in six + C2["same_class_priority2"]:
    for c in CARDS:
        e = {mo: C2[c]["tiles"][t][mo] for mo in MODELS}
        tl[f"{c}.{t}"] = e
        miss = [mo for mo in MODELS if abs(e[mo]) >= 0.2]
        print(f"    {t:28s} {c:12s} " + " / ".join(f"{e[mo]:+.3f}{'*' if abs(e[mo]) >= 0.2 else ' '}" for mo in MODELS)
              + f"   missed by {', '.join(miss) if miss else 'none'}")
out["check2_tiles"] = tl
bh = [C2[c]["tiles"][t][mo] for c in CARDS for t in ("int8.bheld_bit1", "int8.bheld_bit4", "int8.bheld_bit7") for mo in MODELS]
bh87 = [C2[c]["tiles"][t][mo] for c in CARDS for t in ("int8.bheld_bit1", "int8.bheld_bit4", "int8.bheld_bit7") for mo in ("M8", "M7")]
b20 = [C2[c]["tiles"]["fp32.b_onebit_b20_third"][mo] for c in CARDS for mo in MODELS]
out["check2_ranges"] = {"bheld_all_models_both_cards_w": [min(bh), max(bh)], "bheld_M8_M7_both_cards_w": [min(bh87), max(bh87)],
                        "b20_third_all_models_both_cards_w": [min(b20), max(b20)]}
print(f"  B held, all three models on both cards: {max(bh):+.3f} to {min(bh):+.3f} W (M8 and M7 only: {max(bh87):+.3f} to "
      f"{min(bh87):+.3f}); every reading negative (every model low).")
print(f"  fp32.b_onebit_b20_third, all three models on both cards: {max(b20):+.3f} to {min(b20):+.3f} W.")

if OUT:
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
