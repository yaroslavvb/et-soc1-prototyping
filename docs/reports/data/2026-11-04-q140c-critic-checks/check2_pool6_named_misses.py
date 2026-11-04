#!/usr/bin/env python3
"""Q140(c) check 2 (post hoc, desk only; nothing registered): pool 6's blind power error on both 600 MHz cards with the six
tiles that carry Q139's named shared misses taken out, with a selection control.

    python3 -I -B check2_pool6_named_misses.py <lab repo root> --out check2-pool6-named-misses.json > check2-pool6-named-misses.txt

Standard library only. Inputs (committed, read only): E153's scored.json (aifoundry3 card 0, primary.primary.power_rows,
Q139(u)'s footing) and E157's scored.json (aifoundry1 card 1, primary.power_rows, the same footing). The registered set is
pool 6's 30 priority-1 new kinds (12 fp32, 6 fp16, 12 int8; anchors out), as E153-P1..P3 and E157-P1..P3 score them.

The six tiles (Q139's final critic, rank 1 and its desk check): fp32.b_onebit_b20_third (a high single B bit on a 1/3 base
word); int8.a_zeros_b_lineflip and int8.b_line_zero_ff (M8's near-whole-byte discount); int8.bheld_bit1, bheld_bit4,
bheld_bit7 (int8 with B held). Their selection was made after pool 6 was scored, so every figure here is post hoc.

What this script adds beyond re-deriving the critic's 24-tile rms:
  * the selection control: each model's OWN six largest |errors| removed instead (what any post hoc removal of six of 30
    tiles buys), and the mean over 20,000 random six-tile removals (what removal itself does, about nothing);
  * per tile, whether the six are misses of every model (shared) or of one;
  * the same on all 44 non-anchor new kinds (priority 1 and 2), with the critic's six removed, and with the critic's six
    plus the priority-2 tiles of the same named classes (fp16.b_onebit_b6_third: a single B bit on a 1/3 base word;
    int8.b_line_55_aa: an int8 whole-line flip-flop under M8's near-whole-byte discount);
  * bootstrap intervals over tiles (inside one session per card);
  * the within-session readout noise per format: rms over tiles of each tile's sd over its passes / sqrt(n passes).
"""
import argparse

import json
import math
import os
import random

E153 = "docs/reports/data/2026-11-03-e153-blind6-aifoundry3/scored.json"
E157 = "docs/reports/data/2026-11-03-e157-blind6-card1/scored.json"
SIX = ["fp32.b_onebit_b20_third", "int8.a_zeros_b_lineflip", "int8.b_line_zero_ff", "int8.bheld_bit1", "int8.bheld_bit4", "int8.bheld_bit7"]
SAME_CLASS_P2 = ["fp16.b_onebit_b6_third", "int8.b_line_55_aa"]
MODELS = ("M8", "M7", "M6")
FORMATS = ("fp32", "fp16", "int8")
BOOT = 5000
RAND = 20000
SEED = 1402


def rms(e):
    return math.sqrt(sum(x * x for x in e) / len(e)) if e else None


def boot_rms(e, rng, n=BOOT):
    k = len(e)
    v = sorted(rms([e[rng.randrange(k)] for _ in range(k)]) for _ in range(n))
    return [v[int(0.025 * n)], v[int(0.975 * n) - 1]]


def load(root):
    a3 = json.load(open(os.path.join(root, E153)))["primary"]["primary"]["power_rows"]
    c1 = json.load(open(os.path.join(root, E157)))["primary"]["power_rows"]
    return {"aifoundry3": a3, "aifoundry1c1": c1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    rows = load(root)
    rng = random.Random(SEED)
    out = {"_note": "Q140(c) check 2: post hoc desk check, nothing registered. Pool 6's blind power (switching W over the format's "
                    "zeros, Q139(u)'s footing) on aifoundry3 card 0 (E153) and aifoundry1 card 1 (E157), measured - predicted.",
           "inputs": {"aifoundry3": E153 + " primary.primary.power_rows", "aifoundry1c1": E157 + " primary.power_rows"},
           "six": SIX, "same_class_priority2": SAME_CLASS_P2}
    L = ["CHECK 2. POOL 6 WITHOUT THE SIX TILES THAT CARRY THE NAMED SHARED MISSES (post hoc; W rms of measured - predicted)"]
    for card, R in rows.items():
        p1 = sorted(n for n, v in R["M8"].items() if v["priority"] == 1 and not v["pool_anchor"])
        na = sorted(n for n, v in R["M8"].items() if not v["pool_anchor"])
        assert len(p1) == 30 and len(na) == 44, (card, len(p1), len(na))
        assert all(n in p1 for n in SIX) and all(n in na and n not in p1 for n in SAME_CLASS_P2)
        err = {m: {n: R[m][n]["measured"] - R[m][n]["pred"] for n in na} for m in MODELS}
        chk = max(abs(err[m][n] - R[m][n]["error"]) for m in MODELS for n in na)
        res = {"n_priority1": len(p1), "n_nonanchor": len(na), "max_abs_error_recomputed_minus_committed_w": chk, "models": {}}
        L.append("")
        L.append(f"  {card}: 30 priority-1 new kinds (12 fp32, 6 fp16, 12 int8), anchors out; 44 non-anchor new kinds with priority 2. "
                 f"Errors recomputed from measured and pred: max |d| from the committed 'error' {chk:.1e} W")
        rest = [n for n in p1 if n not in SIX]
        for m in MODELS:
            e30 = [err[m][n] for n in p1]
            e24 = [err[m][n] for n in rest]
            own = sorted(p1, key=lambda n: -abs(err[m][n]))[:6]
            e24own = [err[m][n] for n in p1 if n not in own]
            rr = []
            for _ in range(RAND):
                drop = set(rng.sample(p1, 6))
                rr.append(rms([err[m][n] for n in p1 if n not in drop]))
            by_fmt = {}
            for t in FORMATS:
                f30 = [err[m][n] for n in p1 if n.startswith(t + ".")]
                f24 = [err[m][n] for n in rest if n.startswith(t + ".")]
                meanD = sum(R[m][n]["measured"] for n in p1 if n.startswith(t + ".")) / len(f30)
                by_fmt[t] = {"n30": len(f30), "rms30": rms(f30), "rms30_95": boot_rms(f30, rng), "bias30": sum(f30) / len(f30),
                             "mean_measured_D_w": meanD, "rms30_over_mean_D": rms(f30) / meanD, "n24": len(f24), "rms24": rms(f24)}
            e44 = [err[m][n] for n in na]
            e38 = [err[m][n] for n in na if n not in SIX]
            e36 = [err[m][n] for n in na if n not in SIX and n not in SAME_CLASS_P2]
            # the fourth named miss, exponent-heavy fp32 (case E), is a class-wide offset, not a tile: give it a perfect class
            # offset (its own mean error subtracted, an oracle) on top of the six removed
            ecls = [n for n in rest if n.startswith("fp32.") and R["M8"][n]["case"].startswith("E")]
            emean = sum(err[m][n] for n in ecls) / len(ecls)
            e24x = [err[m][n] - (emean if n in ecls else 0.0) for n in rest]
            res.setdefault("fp32_exponent_heavy_priority1", ecls)
            res["models"].setdefault(m, {})
            res["models"][m] = {
                "rms30": rms(e30), "rms30_95": boot_rms(e30, rng), "bias30": sum(e30) / 30,
                "rms24_without_six": rms(e24), "rms24_without_six_95": boot_rms(e24, rng),
                "rms24_without_own_six_worst": rms(e24own), "own_six_worst": own,
                "own_six_worst_overlap_with_six": sorted(set(own) & set(SIX)),
                "rms24_random_six_removed_mean": sum(rr) / len(rr),
                "share_of_rms30_removed_by_six": 1 - rms(e24) / rms(e30),
                "by_format": by_fmt,
                "rms44_nonanchor": rms(e44), "rms38_without_six": rms(e38), "rms36_without_six_and_same_class_p2": rms(e36),
                "fp32_exponent_heavy_mean_error_w": emean, "rms24_without_six_and_fp32_exponent_offset_removed": rms(e24x)}
            q = res["models"][m]
            L.append(f"    {m}: 30 tiles {q['rms30']:.3f} [{q['rms30_95'][0]:.3f}, {q['rms30_95'][1]:.3f}] -> without the six {q['rms24_without_six']:.3f} "
                     f"[{q['rms24_without_six_95'][0]:.3f}, {q['rms24_without_six_95'][1]:.3f}] ({100 * q['share_of_rms30_removed_by_six']:.0f}% of the rms); "
                     f"its own six worst removed {q['rms24_without_own_six_worst']:.3f} (overlap with the six: {len(q['own_six_worst_overlap_with_six'])} of 6); "
                     f"six random removed {q['rms24_random_six_removed_mean']:.3f}")
            L.append(f"        by format, 30 -> 24: " + "; ".join(f"{t} {by_fmt[t]['rms30']:.3f} ({by_fmt[t]['n30']}) -> {by_fmt[t]['rms24']:.3f} ({by_fmt[t]['n24']})" for t in FORMATS))
            L.append(f"        by format, the registered 30: " + "; ".join(
                f"{t} rms {by_fmt[t]['rms30']:.3f} [{by_fmt[t]['rms30_95'][0]:.2f}, {by_fmt[t]['rms30_95'][1]:.2f}] bias {by_fmt[t]['bias30']:+.3f}, "
                f"{100 * by_fmt[t]['rms30_over_mean_D']:.1f}% of the mean kind's {by_fmt[t]['mean_measured_D_w']:.1f} W" for t in FORMATS))
            L.append(f"        own six worst: {', '.join(own)}")
            L.append(f"        the fourth named miss, exponent-heavy fp32 ({len(ecls)} priority-1 tiles, mean error {emean:+.3f} W): with a perfect class offset on top of "
                     f"the six removed, {q['rms24_without_six_and_fp32_exponent_offset_removed']:.3f} W")
            L.append(f"        44 non-anchor new kinds {q['rms44_nonanchor']:.3f} -> without the six (38) {q['rms38_without_six']:.3f} -> "
                     f"also without fp16.b_onebit_b6_third and int8.b_line_55_aa (36) {q['rms36_without_six_and_same_class_p2']:.3f}")
        # the six, tile by tile: whose miss is it
        tl = {}
        for n in SIX + SAME_CLASS_P2:
            tl[n] = {m: err[m][n] for m in MODELS}
            tl[n]["measured_w"] = R["M8"][n]["measured"]
            tl[n]["shared_over_0.2_w_in_every_model"] = all(abs(err[m][n]) >= 0.2 for m in MODELS)
        res["tiles"] = tl
        L.append("    the six (and the two priority-2 tiles of the same classes), M8 / M7 / M6 error in W; 'shared' = |error| >= 0.2 W in every model:")
        for n, v in tl.items():
            L.append(f"      {n:28s} D {v['measured_w']:6.3f} W: {v['M8']:+.2f} / {v['M7']:+.2f} / {v['M6']:+.2f}   shared: {v['shared_over_0.2_w_in_every_model']}")
        # within-session readout noise
        noise = {}
        for t in FORMATS:
            se = [R["M8"][n]["sd"] / math.sqrt(R["M8"][n]["n_passes"]) for n in p1 if n.startswith(t + ".")]
            noise[t] = {"rms_sd_over_sqrt_n_w": rms(se), "max_w": max(se), "n": len(se)}
        res["readout_noise_priority1"] = noise
        L.append("    within-session readout noise on D (rms over priority-1 tiles of sd / sqrt(n passes)): "
                 + ", ".join(f"{t} {noise[t]['rms_sd_over_sqrt_n_w']:.3f} W (max {noise[t]['max_w']:.3f})" for t in FORMATS))
        out[card] = res
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True)
    print("\n".join(L))


if __name__ == "__main__":
    main()
