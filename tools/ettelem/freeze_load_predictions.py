#!/usr/bin/env python3
"""Freeze the joined load model's predictions for four loads it has never seen. Q126, 26 Oct 2026.

Writes docs/reports/data/2026-10-26-load-model/frozen_predictions.json. The predictions are committed and pushed
BEFORE any of the four loads' measurements are read, so the scoring that follows (score_load_predictions.py) is
against numbers nobody could tune. The four:

  E59  sparse parity, three sizes (aifoundry3, 600 MHz, int8 TensorIMA8A32 on +-1 bytes)
  E43  the relay, three routes (three cards, 600 MHz), in pJ per byte as well as watts
  E39  the gemv sparsity ladder, six useful-slot fractions on three cards
  E37  mmbench fp32 streamed from DRAM, three cards

Nothing in load_model.py is fitted on any of them. Each prediction records the rule it used, the assumptions it
rests on and a bracket, so a miss can be read.

    /usr/local/bin/python3.12 freeze_load_predictions.py [--out <path>]
"""
import argparse
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import load_model as LM  # noqa: E402

OUT_DIR = os.path.join(LM.DATA, "2026-10-26-load-model")
TOG = json.load(open(os.path.join(LM.D21, "toggles.json")))


def git_head():
    try:
        return subprocess.run(["git", "-C", LM.REPO, "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def over_idle(card, f_mhz, die_c, active, switching_w):
    """The model's board power above the card's own pre-launch idle: the static terms the idle does not carry,
    plus the load's switching. This is the quantity E37, E39, E43 and E59 all report."""
    v = LM.volts_of(card, f_mhz)
    s = LM.sfv(f_mhz, v)
    return LM.STATIC["k_clk_w"] * (s - 1.0) + LM.STATIC["c0_w"] * s \
        + LM.K.p_sm * (active / 1024.0) * s + switching_w


# ---------------------------------------------------------------- the +-1 int8 rule, frozen here
def int8_pm1_coefficient():
    """E64 measured int8 at 1,024 minions referred to 600 MHz / 0.517 V: zeros 2.123, ones 2.684, randn 9.101 W.
    Sparse parity's operands are +-1 bytes (0x01 and 0xFF), which is neither.

    The rule, frozen: the switching above the int8 zeros floor splits into a TRANSPORT part (operand words moved
    and register bits clocked) and a DATAPATH part (the multiplier tree and the rest of the unit), in the share
    the fp32 flip model gives for random operands. Then
      transport scales with the operand bits that flip: +-1 bytes flip 3.5 of 8 bits between successive random
        draws, random int8 bytes flip 4.0 of 8          -> 0.875
      datapath scales with the product bits that move: a +-1 product occupies 1 bit of the 15-bit int8 product,
        a random int8 product about 7.5                 -> 0.133
    """
    fl = LM.flips_from_toggles(TOG, "randn")
    _, parts = LM.flip_w(fl, 1024, 600.0, LM.V_REF, "aifoundry2", LM.T_FIT, 0.0, 1.0)
    transport = parts["bus"] + parts["ffclk"]
    datapath = parts["mult"] + parts["rest"]
    tot = transport + datapath
    w_tr, w_dp = transport / tot, datapath / tot
    phi = w_tr * 0.875 + w_dp * (1.0 / 7.5)
    c_zero = LM.K.c64["SUS-06-int8-zeros-1024-r1"]
    c_rand = LM.K.c64["SUS-08-int8-randn-1024-r1"]
    c_ones = LM.K.c64["SUS-07-int8-ones-1024-r1"]
    return {"c_w": c_zero + (c_rand - c_zero) * phi, "phi": phi,
            "transport_share": w_tr, "datapath_share": w_dp,
            "c_zeros_w": c_zero, "c_ones_w": c_ones, "c_randn_w": c_rand,
            "bracket_w": [c_ones, c_rand]}


# ---------------------------------------------------------------- E59
E59_SIZES = [
    # name, ops per solve (plan.ops), solves per second, die C, active minions
    {"name": "L1 (512,4,0.3,448)", "ops": 81989040, "solves_per_s": 7.3211, "die_c": 53.3},
    {"name": "L2 (512,4,0.4,1850)", "ops": 339668880, "solves_per_s": 2.3361, "die_c": 53.2},
    {"name": "(256,5,0.4,1925) first half", "ops": 654995125, "solves_per_s": 1.0571, "die_c": 53.6},
    {"name": "(256,5,0.4,1925) second half", "ops": 575036887, "solves_per_s": 0.6468, "die_c": 53.3},
]
E59_CYCLES_IDEAL = 280.35      # int8 TensorIMA8A32 cycles an op, mmbench's measured shared-tile rate (E37 MMB-a)
E59_BYTES_PER_OP = 4096        # hart 1's row generation: 16 rows x 64 B written + 3 feature vectors x 64 B read


def predict_e59(pm1):
    card, f, active = "aifoundry3", 600.0, 1024
    v = LM.volts_of(card, f)
    s = LM.sfv(f, v)
    scp_pj = LM.K.levels_per_card["scp-local"][card]
    rows = []
    for z in E59_SIZES:
        ops_s = z["ops"] * z["solves_per_s"]
        cyc_per_op = f * 1e6 * active / ops_s
        duty = E59_CYCLES_IDEAL / cyc_per_op
        k_T = 1.0 + 0.004 * (z["die_c"] - LM.T_REF)
        w_tensor = pm1["c_w"] * s * k_T * LM.CARDS[card]["scale"] * duty
        bps = ops_s * E59_BYTES_PER_OP
        w_scp = bps * scp_pj * 1e-12
        w = over_idle(card, f, z["die_c"], active, w_tensor + w_scp)
        rows.append({
            "size": z["name"], "card": card, "f_mhz": f, "die_c": z["die_c"],
            "tensor_ops_per_s": ops_s, "cycles_per_op": cyc_per_op, "tensor_duty": duty,
            "scratchpad_bytes_per_s": bps,
            "predicted_over_idle_w": w,
            "parts_w": {"kernel_offset_and_state_machines": over_idle(card, f, z["die_c"], active, 0.0),
                        "tensor": w_tensor, "scratchpad": w_scp},
            "predicted_j_per_solve_over_idle": w / z["solves_per_s"],
            "work_unit": "solve", "solves_per_s": z["solves_per_s"],
        })
    return rows


# ---------------------------------------------------------------- E43
E43_ROUTES = [
    # name, the catalogue level the stage's output is read back from, measured GB/s (finding 18's first run)
    {"name": "DRAM, read back next stage", "level": "dram", "gb_s": 48.4},
    {"name": "the next shire's scratchpad", "level": "scp-remote", "gb_s": 592.9},
    {"name": "this shire's own scratchpad", "level": "scp-local", "gb_s": 1483.7},
]
# the relay's own arithmetic: one vector add per element, 8 lanes of fp32, on one constant per slab
E43_ADD_PJ = None   # filled from the catalogue below


def predict_e43():
    global E43_ADD_PJ
    pj_add = LM.instr_pj("fadd.ps", "const", "h2")
    if pj_add is None:
        pj_add = LM.instr_pj("fadd.ps", "random", "h2")
    E43_ADD_PJ = pj_add
    add_pj_per_byte = pj_add / 32.0     # 8 lanes x 4 B an instruction
    rows = []
    for card in ("aifoundry2", "aifoundry3", "aifoundry1-c1"):
        for r in E43_ROUTES:
            lvl = LM.K.levels_per_card[r["level"]].get(card) or LM.K.levels_pj_per_byte[r["level"]]
            pj = lvl + add_pj_per_byte
            rows.append({"route": r["name"], "level": r["level"], "card": card,
                         "predicted_pj_per_byte": pj,
                         "level_pj_per_byte": lvl, "vector_add_pj_per_byte": add_pj_per_byte,
                         "measured_gb_s_used_for_watts": r["gb_s"],
                         "predicted_w_over_idle": pj * r["gb_s"] * 1e9 * 1e-12
                                                  + over_idle(card, 600.0, 58.0, 1024, 0.0)})
    pooled = []
    for r in E43_ROUTES:
        v = [x["predicted_pj_per_byte"] for x in rows if x["route"] == r["name"]]
        pooled.append({"route": r["name"], "predicted_pj_per_byte_pooled": sum(v) / len(v)})
    return rows, pooled


# ---------------------------------------------------------------- E39
E39_X = {"fma-dense": 1.0, "fma-50": 0.503, "fma-rowmask": 0.5, "fma-col50": 0.438, "fma-875": 0.105,
         "fma-zero": 0.0}
E39_DIE = {"aifoundry2": 80.5, "aifoundry3": 58.0, "aifoundry1-c1": 80.3}
E39_PROXY = "pow2"          # the fma-* configs run the host's default SMALL-INTEGER operands (v3-energy.cfg:5)
E39_BRACKET = ("ternary", "uniform")


def predict_e39():
    rows, lines = [], []
    for card, die in E39_DIE.items():
        fl = LM.flips_from_toggles(TOG, E39_PROXY)
        w_dense, _ = LM.flip_w(fl, 1024, 600.0, None, card, die, 0.004, None, False, "counted")
        lo, _ = LM.flip_w(LM.flips_from_toggles(TOG, E39_BRACKET[0]), 1024, 600.0, None, card, die, 0.004)
        hi, _ = LM.flip_w(LM.flips_from_toggles(TOG, E39_BRACKET[1]), 1024, 600.0, None, card, die, 0.004)
        base = over_idle(card, 600.0, die, 1024, 0.0)
        pts = []
        for cfg, x in E39_X.items():
            rows.append({"card": card, "config": cfg, "useful_slot_fraction": x, "die_c": die,
                         "predicted_over_idle_w": base + x * w_dense,
                         "bracket_w": [base + x * lo, base + x * hi]})
            pts.append((x, base + x * w_dense))
        n = len(pts)
        sx = sum(p[0] for p in pts); sy = sum(p[1] for p in pts)
        sxx = sum(p[0] ** 2 for p in pts); sxy = sum(p[0] * p[1] for p in pts)
        m = (n * sxy - sx * sy) / (n * sxx - sx * sx)
        lines.append({"card": card, "predicted_slope_w": m, "predicted_intercept_w": (sy - m * sx) / n,
                      "predicted_dense_w": base + w_dense, "predicted_zero_w": base})
    return rows, lines


# ---------------------------------------------------------------- E37
E37_CARDS = {"aifoundry2": 76.94, "aifoundry3": 58.85, "aifoundry1-c1": 70.95}
E37_CYCLES_PER_OP = 15266.7     # MMB-a's kept band mean for fp32-tensor-DRAM (15,042-15,491)
E37_BYTES_PER_OP = 2048         # the A and B 16x16 fp32 tiles read from DRAM; C accumulated on the minion


def predict_e37():
    rows = []
    fl = LM.flips_from_toggles(TOG, "randn")
    for card, die in E37_CARDS.items():
        duty = 546.0 / E37_CYCLES_PER_OP
        w_t, _ = LM.flip_w(fl, 1024, 600.0, None, card, die, 0.004)
        w_tensor = w_t * duty
        ops_s = 1024 * 600e6 / E37_CYCLES_PER_OP
        bps = ops_s * E37_BYTES_PER_OP
        pj = LM.K.levels_per_card["dram"].get(card) or LM.K.levels_pj_per_byte["dram"]
        w_dram = bps * pj * 1e-12
        w = over_idle(card, 600.0, die, 1024, w_tensor + w_dram)
        rows.append({"card": card, "die_c": die, "tensor_duty": duty, "dram_bytes_per_s": bps,
                     "dram_pj_per_byte": pj, "predicted_over_idle_w": w,
                     "parts_w": {"kernel_offset_and_state_machines": over_idle(card, 600.0, die, 1024, 0.0),
                                 "tensor": w_tensor, "dram": w_dram},
                     "predicted_pj_per_byte_whole_load": w / bps * 1e12,
                     "bracket_w_bytes_1024_to_3072": [
                         over_idle(card, 600.0, die, 1024, w_tensor + w_dram * 0.5),
                         over_idle(card, 600.0, die, 1024, w_tensor + w_dram * 1.5)],
                     "predicted_tflops": 1024 * 8192 / E37_CYCLES_PER_OP * 600e6 / 1e12})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(OUT_DIR, "frozen_predictions.json"))
    a = ap.parse_args()

    pm1 = int8_pm1_coefficient()
    e59 = predict_e59(pm1)
    e43, e43p = predict_e43()
    e39, e39l = predict_e39()
    e37 = predict_e37()

    doc = {
        "what": "Frozen predictions of the joined load model (tools/ettelem/load_model.py) for four loads it "
                "has never seen. Written and pushed before the measurements were read; scored afterwards by "
                "tools/ettelem/score_load_predictions.py into scores.json.",
        "request": "Q126",
        "written_utc": "2026-10-26",
        "repo_head_at_freeze": git_head(),
        "model": {
            "form": "P_board = idle(T, card) + k_clk*(s(f)-1) + c0*s(f) + p_sm*(active/1024)*s(f) "
                    "+ flips*prices*s(f)*k_T*k_card + catalogue rows",
            "s_of_f_V": "(f/600) * (V/0.517)^2",
            "fitted_static": LM.STATIC,
            "leakage_refit_51_67C": (None if not LM.LEAK_COOL else
                                     {"P_fix_w": LM.LEAK_COOL[0], "A_at_80C_w": LM.LEAK_COOL[1],
                                      "e_fold_c": LM.LEAK_COOL[2], "bins": LM.LEAK_COOL[3],
                                      "band_c": LM.LEAK_COOL[4], "rms_w": LM.LEAK_COOL[5],
                                      "source": "E44 idle.json, aifoundry3's own idle cycles"}),
            "flip_prices_fJ": LM.K.e_fJ,
            "p_sm_w": LM.K.p_sm,
            "card_scales": {c: LM.CARDS[c]["scale"] for c in LM.CARDS},
            "temp_coeff_per_c": 0.004,
            "sources": LM.COEFF_SOURCES,
            "not_fitted_on": ["E37 mmb", "E39 ablb", "E43 rl", "E59 sparse parity"],
        },
        "predictions": {
            "E59_sparse_parity": {
                "rule": "int8 TensorIMA8A32 at a duty of (280.35 ideal cycles an op) / (the measured cycles an "
                        "op), on the +-1 operand coefficient below, plus hart 1's row generation priced as "
                        f"{E59_BYTES_PER_OP} B an op through the shire's own scratchpad.",
                "int8_pm1_coefficient": pm1,
                "assumptions": [
                    "the +-1 coefficient rule (transport 0.875, datapath 1/7.5 of random int8)",
                    f"{E59_BYTES_PER_OP} B of scratchpad traffic per tensor op (16 rows x 64 B written, "
                    "3 feature vectors x 64 B read)",
                    "the tensor unit's own operand fetch is already inside the measured int8 coefficient",
                    "no term for the 1,606-cycle epilogue or the host link",
                ],
                "rows": e59,
            },
            "E43_relay": {
                "rule": "the energy manual's measured pJ per byte for the level the stage's output comes back "
                        "from, plus one 8-lane fp32 vector add per element on constant operands "
                        f"({E43_ADD_PJ:.1f} pJ an instruction / 32 B).",
                "caveat": "the weakest of the four as a held-out test: the level prices and the relay were "
                          "measured in the same campaign (reruns.json), and energy manual S7.2 already prices "
                          "the relay by hand. What is new here is that the arithmetic is mechanical and "
                          "per-card.",
                "rows": e43, "pooled": e43p,
            },
            "E39_gemv_sparsity_ladder": {
                "rule": f"the flip model on the '{E39_PROXY}' toggle counts as the proxy for the host's default "
                        "small-integer operands, scaled linearly by the useful-slot fraction (the zero gate as "
                        f"a hard gate), with a bracket from '{E39_BRACKET[0]}' and '{E39_BRACKET[1]}'.",
                "assumptions": ["the bench has no toggle count for the small-integer pattern, so a proxy is "
                                "frozen here", "a zero operand slot costs exactly nothing"],
                "rows": e39, "lines": e39l,
            },
            "E37_mmbench_fp32_from_DRAM": {
                "rule": f"random fp32 tiles at a duty of 546 / {E37_CYCLES_PER_OP:.0f} cycles an op, plus "
                        f"{E37_BYTES_PER_OP} B an op from DRAM at the catalogue's per-card price.",
                "assumptions": [f"{E37_BYTES_PER_OP} B an op (the A and B tiles) reach DRAM and nothing is "
                                "caught by the 32 MB L3; the bracket halves and doubles that"],
                "rows": e37,
            },
        },
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(doc, f, indent=1)
    print("wrote", a.out)
    print()
    print(f"int8 +-1 coefficient: {pm1['c_w']:.3f} W (phi {pm1['phi']:.4f}; "
          f"transport share {pm1['transport_share']:.3f}); bracket {pm1['bracket_w'][0]:.2f}-{pm1['bracket_w'][1]:.2f} W")
    print("\nE59 sparse parity (aifoundry3, 600 MHz):")
    for r in e59:
        print(f"  {r['size'][:34]:34s} duty {r['tensor_duty']:.3f}  over idle {r['predicted_over_idle_w']:6.2f} W  "
              f"J/solve {r['predicted_j_per_solve_over_idle']:7.3f}")
    print("\nE43 relay, pooled pJ/B:")
    for r in e43p:
        print(f"  {r['route'][:34]:34s} {r['predicted_pj_per_byte_pooled']:8.3f} pJ/B")
    print("\nE39 gemv ladder:")
    for r in e39l:
        print(f"  {r['card']:14s} slope {r['predicted_slope_w']:6.2f} W  intercept "
              f"{r['predicted_intercept_w']:+5.2f} W  dense {r['predicted_dense_w']:6.2f} W")
    print("\nE37 mmbench from DRAM:")
    for r in e37:
        print(f"  {r['card']:14s} over idle {r['predicted_over_idle_w']:6.2f} W  "
              f"(tensor {r['parts_w']['tensor']:.2f} + DRAM {r['parts_w']['dram']:.2f})  "
              f"{r['predicted_tflops']:.4f} TFLOPS")


if __name__ == "__main__":
    main()
