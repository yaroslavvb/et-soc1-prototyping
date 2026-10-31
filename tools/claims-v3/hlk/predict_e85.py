#!/usr/bin/env python3
"""E85: freeze the predictions and the decision rules before the claim and the first launch.

    python3 predict_e85.py            # writes predictions.json and predictions.txt beside this file

Inputs: committed files only, each refused unless its sha256 is the one pinned below.

  * E80 and E83 (aifoundry2, this card, Sat 31 Oct 2026): each kind's board power at 800 MHz on the
    full card in the first second after reaching it (`burst_p800_w`), the mean of both experiments
    where both ran the kind.  A kind's step over ITS OWN TYPE'S zeros on 192 of the 1,024 minions is
    predicted as (p800_kind - p800_zeros) x 192 / 1024: E63 measured the rung's step on 256 and 192
    minions at 5.443 and 4.020 W, 1.5% from linear in minions.
  * E63 A1 (s2, 192 minions) and E73 (192 minions): the reference rung's step, the board's 0.05 Hz
    fundamental per watt of step (the ~9 s launches in 10 s phases), and the camera's transfer.
  * E63's pooled 0.05 Hz transfer (Q126 post hoc, four top-rung blocks): 52.71 mK per watt of
    fundamental at a 95.4 degree lag.  The task text: "each kind's amplitude in proportion to its
    switching W at E63's measured mK per W, drift-corrected by the reference".

The physics being tested: heat is heat.  Every kind runs on the same 192 minions, so a watt of
switching should warm the back of the board by the same millikelvin whatever the numbers are, and
the camera should weigh the kinds exactly as the board's meter does.  So the core prediction is a
ratio of 1: each kind's mK per W over the reference rung's, both measured in this session, the
reference corrected for the camera's gain drift by a line through three reference blocks.
"""
from __future__ import annotations

import hashlib
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MINIONS, FULL = 192, 1024

PINNED = {
    "e80": ("docs/reports/data/2026-10-31-e80-kinds-speed/results.json",
            "f8ab6fc08ef73a5f0e91fe518c2d33162fe14687235ab763ac50639dd49ae6fd"),
    "e83": ("docs/reports/data/2026-10-31-e83-kinds-speed-rest/results.json",
            "3717f1767bdb76f536b7af8dbedf01865984638e649f892c2893e47d59676b3e"),
    "e63s2": ("docs/reports/data/2026-10-23-e63-camera-hamming-ladder/s2/analysis/lockin.json",
              "30f7e8707dd0d87370777196d6325000eec479037b89b3c7f6f6809b1821f3a1"),
    "e63pool": ("docs/reports/data/2026-10-23-e63-camera-hamming-ladder/posthoc/h3-rails-pooled.json",
                "98a48db142d51156f572796582e34f5a7f750b324cce8f38cb4d3dd0cf372ba3"),
    "e73": ("docs/reports/data/2026-10-27-e73-camera-frequencies/analysis/lockin.json",
            "d29e801f263fa42aeed5d33e5388b191df95aa6abbfbb439197ba003dc8ae4c4"),
    "kinds": ("tools/claims-v3/kinds/kinds.json",
              "9586568f23a97757e34b3cdacdffe5bee0122d236e28a9f76f06e8598b7b1337"),
}

KINDS = {  # block id: (format, kind, set A, set B)
    "E85-F32": ("fp32", "randn", "F32R", "F32Z"),
    "E85-I8": ("int8", "full", "I8F", "I8Z"),
    "E85-F16": ("fp16", "randn", "F16R", "F16Z"),
    "E85-SP90": ("fp32", "sparse90", "F32S90", "F32Z"),
}
MAIN = ("E85-F32", "E85-I8", "E85-F16")
REFS = ("E85-REF1", "E85-REF2", "E85-REF3")
STEP_BAND = 0.20      # a kind's predicted step, +-20%
REF_STEP_BAND = 0.10  # the reference rung's, +-10% (measured five times before at 192 minions)


def load(key):
    path, want = PINNED[key]
    full = os.path.join(ROOT, path)
    got = hashlib.sha256(open(full, "rb").read()).hexdigest()
    if got != want:
        raise SystemExit(f"{path}: sha256 {got} is not the pinned {want}")
    with open(full) as f:
        return json.load(f)


def p800(e80, e83, cell):
    vals = [r["cells"][cell]["burst_p800_w"] for r in (e80, e83) if cell in r["cells"]]
    return sum(vals) / len(vals), vals


def main():
    e80, e83, s2, pool, e73, kinds = (load(k) for k in ("e80", "e83", "e63s2", "e63pool", "e73", "kinds"))
    scale = MINIONS / FULL

    # ---- the reference rung at 192 minions: five earlier blocks
    prior = []
    for src, L, names in (("E63 s2", s2, ("E63-TOP", "E63-MID", "E63-TOP2")),
                          ("E73", e73, ("E73-REF1", "E73-REF2", "E73-REF3"))):
        for b in names:
            r = L["blocks"][b]
            prior.append(dict(source=src, block=b, step_w=r["board_step_w"]["mean"],
                              fund_w=r["power"]["amp"], fund_per_step=r["power"]["amp"] / r["board_step_w"]["mean"],
                              cam_mk=r["roi"]["amp"], se_cam_mk=r["roi"]["se_along"],
                              H=r["transfer_roi"]["mag"], se_H=r["transfer_roi"]["se_mag"],
                              lag_deg=r["transfer_roi"]["phase_deg"]))
    tops = [p for p in prior if p["block"] != "E63-MID"]
    ref_step = sum(p["step_w"] for p in tops) / len(tops)
    fps = sum(p["fund_per_step"] for p in prior) / len(prior)
    H_vals = [p["H"] for p in prior]
    H_lo, H_hi = min(H_vals), max(H_vals)
    H0 = pool["pooled"]["H_f_mk_per_w"]
    H0_se = pool["pooled"]["se_H_f"]
    lag0 = pool["pooled"]["H_f_phase_deg"]

    # ---- board levels at 192 minions (E63 s2's own telemetry, README): ones 33.98 W, lq_h0 34.28,
    # lq_h23 38.62, idle tail 24.00 (600 MHz).  zeros sits below ones by fp32 ones' step.
    ones192 = 33.98
    p_ones, _ = p800(e80, e83, "fp32/ones")
    p_z32, _ = p800(e80, e83, "fp32/zeros")
    zeros192 = ones192 - (p_ones - p_z32) * scale
    die_line = e83["posthoc"]["die_line_e83"]

    blocks = {}
    for bid, (fmt, kind, sa, sb) in KINDS.items():
        pk, pk_vals = p800(e80, e83, f"{fmt}/{kind}")
        pz, pz_vals = p800(e80, e83, f"{fmt}/zeros")
        step = (pk - pz) * scale
        fund = fps * step
        loud = zeros192 + step
        mean_w = 0.5 * (loud + zeros192)
        blocks[bid] = dict(
            role="kind", format=fmt, kind=kind, sets=[sa, sb],
            tiles_sha256={s: kinds["kinds"][fmt][k]["sha256"] for s, k in ((sa, kind), (sb, "zeros"))},
            p800_full_card_w=dict(kind=round(pk, 3), kind_runs=pk_vals, zeros=round(pz, 3), zeros_runs=pz_vals),
            board_step_w=round(step, 3), board_step_band_w=[round(step * (1 - STEP_BAND), 3),
                                                            round(step * (1 + STEP_BAND), 3)],
            board_fundamental_w=round(fund, 3),
            camera_roi_mk=round(H0 * fund, 1),
            camera_roi_band_mk=[round(H_lo * (1 - STEP_BAND) * fund, 1), round(H_hi * (1 + STEP_BAND) * fund, 1)],
            lag_deg_band=[80.0, 120.0],
            ratio_to_reference=1.0,
            board_levels_w=dict(loud_arm=round(loud, 2), zeros_arm=round(zeros192, 2), block_mean=round(mean_w, 2)),
            die_mean_c_below=round(die_line["a_c"] + die_line["k_c_per_w"] * loud, 1))
    for bid in REFS:
        fund = fps * ref_step
        blocks[bid] = dict(
            role="ref", format="fp32", kind="lq_h23", sets=["REF23", "REF0"],
            board_step_w=round(ref_step, 3),
            board_step_band_w=[round(ref_step * (1 - REF_STEP_BAND), 3), round(ref_step * (1 + REF_STEP_BAND), 3)],
            board_fundamental_w=round(fund, 3),
            camera_roi_mk=round(H0 * fund, 1),
            camera_roi_band_mk=[round(H_lo * fund, 1), round(H_hi * fund, 1)],
            transfer_mk_per_w=round(H0, 2), transfer_band=[round(H_lo, 2), round(H_hi, 2)],
            lag_deg_band=[80.0, 120.0],
            board_levels_w=dict(loud_arm=38.62, zeros_arm=34.28, block_mean=36.45),
            die_mean_c_below=60.0)

    rules = {
        "E85-R1_seen": ("each main kind (F32, I8, F16): the ROI amplitude's sign-flip p < 0.001 and its transfer "
                        "phase (lag behind the board power) in (0, 180) degrees: warming that follows the kind"),
        "E85-R2_heat_follows_watts": ("each main kind: R = |H_kind| / Href(t_kind) equals 1 within max(3 SE_R, "
                                      "0.10), where H_kind = the kind's camera fundamental over its own board "
                                      "fundamental (mK/W), Href(t) the reference line at the kind block's mid-time, "
                                      "and SE_R the quadrature of the kind's jackknife SE of |H| and the line's SE "
                                      "at t, both divided by Href(t)"),
        "E85-R3_pooled": ("the inverse-variance mean of the three main kinds' R equals 1 within max(3 SE, 0.05)"),
        "E85-R4_same_lag": ("each main kind's transfer phase equals the reference line's phase within max(3 SE, "
                            "15 degrees), SE = the kind's jackknife phase SE and the line's phase SE in quadrature"),
        "E85-R5_near_null": ("E85-SP90 (no detection required): its ROI amplitude projected on the reference "
                             "line's camera direction equals Href(t) x its own board fundamental projected on "
                             "the reference power direction, within 3 SE (its own SE along that direction)"),
        "E85-R6_electrical": ("each kind's measured board step (arm A's steady median minus arm B's, mean over "
                              "analysed laps) inside its predicted band; each reference block's inside +-10% of "
                              "the earlier 192-minion mean; scored per block"),
        "E85-R7_reference_line": ("the three reference blocks' |H| lie on a weighted straight line in time: worst "
                                  "residual <= 3 SE (E73's R2); with fewer than three references it is not scored "
                                  "and R2-R5 use the line through what there is"),
        "E85-R8_hold": ("every block: >= 95% of the 10 Hz samples from 1.5 s after each analysed launch's start "
                        "to its end read >= 790 MHz, and the block's die mean is below 65 C (E73's R6); the "
                        "per-launch idle-reset dips are counted and reported with no verdict"),
        "E85-R9_absolute": ("each main kind's ROI amplitude inside its frozen band [H_lo x 0.8, H_hi x 1.2] x its "
                            "predicted fundamental, H_lo..H_hi = the six earlier 192-minion transfers: E63's mK per "
                            "W, not drift-corrected"),
    }
    out = dict(
        experiment="E85", request="Q130", frozen="Sat 31 Oct 2026, before the claim and the first launch",
        inputs={k: dict(path=v[0], sha256=v[1]) for k, v in PINNED.items()},
        constants=dict(minions=MINIONS, full_card_minions=FULL, scale=scale,
                       step_band=STEP_BAND, ref_step_band=REF_STEP_BAND,
                       fund_per_step=round(fps, 4),
                       reference_step_w_prior=round(ref_step, 3),
                       H_e63_pooled_mk_per_w=round(H0, 3), H_e63_pooled_se=round(H0_se, 3),
                       H_e63_pooled_lag_deg=round(lag0, 2),
                       H_prior_192_range=[round(H_lo, 2), round(H_hi, 2)],
                       zeros_192_board_w=round(zeros192, 2), ones_192_board_w=ones192,
                       die_line_e83=die_line),
        prior_reference_blocks=prior, blocks=blocks, rules=rules,
        main_kinds=list(MAIN), reference_blocks=list(REFS))
    with open(os.path.join(HERE, "predictions.json"), "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    lines = ["E85 predictions (frozen before the claim)",
             f"  board fundamental per W of step {fps:.4f} (6 earlier 192-minion blocks); E63 pooled H "
             f"{H0:.2f} +- {H0_se:.2f} mK/W at {lag0:.1f} deg; earlier 192-minion H {H_lo:.1f}-{H_hi:.1f}",
             f"  zeros arm at 192 minions ~{zeros192:.2f} W (E63 s2 ones 33.98 W less fp32 ones' step)",
             "  block      kind            step W (band)          fund W   camera mK (band)        die <"]
    order = ("E85-REF1", "E85-F32", "E85-I8", "E85-REF2", "E85-F16", "E85-SP90", "E85-REF3")
    for bid in order:
        b = blocks[bid]
        lines.append(f"  {bid:9s}  {b['format']} {b['kind']:9s}  {b['board_step_w']:6.3f} "
                     f"({b['board_step_band_w'][0]:.3f}-{b['board_step_band_w'][1]:.3f})  "
                     f"{b['board_fundamental_w']:6.3f}  {b['camera_roi_mk']:6.1f} "
                     f"({b['camera_roi_band_mk'][0]:.1f}-{b['camera_roi_band_mk'][1]:.1f})  "
                     f"{b['die_mean_c_below']:.1f}")
    lines.append("  every kind: R = H_kind / Href(t) = 1.00 (E85-R2), lag = the reference's (E85-R4)")
    txt = "\n".join(lines) + "\n"
    with open(os.path.join(HERE, "predictions.txt"), "w") as f:
        f.write(txt)
    print(txt, end="")


if __name__ == "__main__":
    main()
