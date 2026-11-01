#!/usr/bin/env python3
"""E107's frozen numbers (Q133): predictions-e107.json and predictions-e107.txt, from E105's and E101's committed aifoundry3 records only. Standard library.

    python3 tools/claims-v3/e107/make_predictions_e107.py

Every number is at aifoundry3's pinned 600 MHz. T is the time per op of one minion, us: the chip's 1,024 minions over the reducer's `rate`.
- The ends: T(c1) and T(c16) are E105's by-column gemmc1 and gemmc16 on aifoundry3 (e105c.json gemm1.* and gemm16.*, the mean of zeros and random).
- The repeat ladder, reuse as the variable: a block's first pass costs what a pass of the cold walk costs, and its other R - 1 passes what a repeated
  block's pass costs, so T(R) = T(c1) + (T(c16) - T(c1)) / R.
- c4s and c8s, the walk inside the L3: an L2 miss the L3 serves costs what it costs in E101's packed gemm1, whose block (5 MB) sits in the L3 and whose
  desk L2 model has 144 of each op's 192 lines per shire missing: (T(as run) - T(c1)) / 144 per missing line. A cold pass by column has 128 of the 192
  missing (desk/l2sim.txt, E105's), so T = T(c1) + 128 x that.
- c8, C per block: 24 MB of A + B and 16 MB of C, 40 MB cycling through a 32 MB L3; under LRU nothing survives a pass, so T = T(c16).
- c16s, C shared: of the 80 MB a pass moves past the L3 in E105's walk, 48 MB are A + B reads and 32 MB C's stores; if the DRAM side's cost follows its
  bytes, 0.6 of the cold excess stays.
- S, board power over idle: E_op x 1,024 / T, with E_op the energy per op. c4s, c8s: E_op = E(c1) + 128 x (E(as run) - E(c1)) / 144, the L3-served miss
  priced as T is. The other arms: E_op = E(c1) + x (E(c16) - E(c1)), x the arm's frozen share of the cold excess in T. Zeros and random only; sparse50 has no
  cold-walk record to anchor it, so it is measured, not predicted.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e107_common as e7  # noqa: E402

DATA = os.path.join(ROOT, "docs", "reports", "data")
E105C = os.path.join(DATA, "2026-11-01-e105-gemm-layout", "e105c.json")
E101 = os.path.join(DATA, "2026-11-01-e101-real-matmul", "e101.json")
TYPES = ("fp32", "fp16", "int8")
RK = {"fp32": "randn", "fp16": "randn", "int8": "full"}
MISS_ASRUN, MISS_COLD, LINES = 144, 128, 192
REUSED = ["tools/claims-v3/kinds/run_e78.py", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/reduce_e78.py",
          "tools/claims-v3/kinds/kinds.json", "tools/claims-v3/lib.sh"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    c = json.load(open(E105C))["items"]
    e = json.load(open(E101))["items"]
    T = lambda d, k: 1024.0 / d[k]["rate"]["mean"] * 1e6
    E = lambda d, k: d[k]["pj_op_S"]["mean"] / 1000.0          # nJ per op
    ends, model = {}, {}
    pred = {"T_us": {}, "f": {}, "S_w": {}, "E_nj_op": {}}
    for ty in TYPES:
        kz, kr = f"{ty}.zeros", f"{ty}.{RK[ty]}"
        t1 = (T(c, f"gemm1.{kz}") + T(c, f"gemm1.{kr}")) / 2
        t16 = (T(c, f"gemm16.{kz}") + T(c, f"gemm16.{kr}")) / 2
        tas = (T(e, f"gemm1.{kz}") + T(e, f"gemm1.{kr}")) / 2
        per_miss = (tas - t1) / MISS_ASRUN
        ends[ty] = {"T_c1": t1, "T_c16": t16, "T_asrun_e101": tas, "us_per_missing_line_l3": per_miss}
        tl3 = t1 + MISS_COLD * per_miss
        f = {"c1": 0.0, "c16": 1.0, "c16r2": 0.5, "c16r4": 0.25, "c16r8": 0.125, "c16r32": 1 / 32, "c8": 1.0, "c16s": 0.6}
        tt = {a: t1 + x * (t16 - t1) for a, x in f.items()}
        tt["c4s"] = tt["c8s"] = tl3
        f["c4s"] = f["c8s"] = (tl3 - t1) / (t16 - t1)
        for a in e7.ARMS:
            pred["T_us"][f"{a}.{ty}"] = round(tt[a], 4)
            pred["f"][f"{a}.{ty}"] = round(f[a], 4)
        for kind in ("zeros", RK[ty]):
            k = f"{ty}.{kind}"
            e1, e16, eas = E(c, f"gemm1.{k}"), E(c, f"gemm16.{k}"), E(e, f"gemm1.{k}")
            model[k] = {"E_c1": e1, "E_c16": e16, "E_asrun_e101": eas}
            for a in e7.ARMS:
                if a in ("c4s", "c8s"):
                    eop = e1 + MISS_COLD * (eas - e1) / MISS_ASRUN
                else:
                    eop = e1 + f[a] * (e16 - e1)
                pred["E_nj_op"][f"{a}.{k}"] = round(eop, 3)
                pred["S_w"][f"{a}.{k}"] = round(eop * 1e-9 * 1024 / (tt[a] * 1e-6), 3)
    rules = {
        "R1_tie": {"text": "T(c1) within 2% and T(c16) within 3% of E105's aifoundry3 values, in each format", "c1_rel": 0.02, "c16_rel": 0.03,
                   "fail_means": "the rebuilt arms are not E105's: every other verdict is labelled"},
        "R2_kind": {"text": "in every arm and format, each kind's T within 1% of that arm's zeros", "rel": 0.01},
        "R3_reuse": {"text": "per format, fit T(R) = Tinf + D / R over R in {1, 2, 4, 8, 32} (c16, c16r2, c16r4, c16r8, c16r32)",
                     "REUSE": "|Tinf - T(c1)| <= 0.05 T(c1) and every point within 3% of the fit: reuse is the variable, a block's first pass costs the same "
                              "whatever follows it",
                     "NOT_REUSE": "T(c16r32) - T(c1) >= 0.5 (T(c16) - T(c1)): 32 passes over a block leave more than half the cold excess",
                     "PARTIAL": "otherwise", "tinf_rel": 0.05, "point_rel": 0.03, "not_frac": 0.5, "primary": "fp32", "frozen": "REUSE in all three formats"},
        "R4_walk": {"text": "f8 = (T(c8s) - T(c1)) / (T(c16) - T(c1)), the share of the cold walk's excess left when its blocks stay in the L3",
                    "DRAM": "f8 <= 0.50: DRAM (the walk's misses past the L3) sets most of the cold walk's pace", "NOT_DRAM": "f8 >= 0.85: it does not",
                    "SHARED": "between", "dram_max": 0.50, "notdram_min": 0.85, "primary": "fp32",
                    "frozen": {ty: pred["f"][f"c8s.{ty}"] for ty in TYPES}},
        "R4b_resident": {"text": "|T(c4s) - T(c8s)| <= 0.05 T(c8s): the 26 MB walk behaves as the 14 MB one; if not, R4 is read on c4s and labelled",
                         "rel": 0.05},
        "R4c_dram_check": {"text": "the DDR rail's droop, mV over the idle just before the run, window [t0+2 s, t0+4 s) against [t0-1.5 s, t0-0.1 s): "
                                   "droop(c8s) - droop(c1) <= 0.5 (droop(c16) - droop(c1)) on fp32 zeros and on fp32 random: the 8-block walk left DRAM",
                           "frac": 0.5},
        "R5_c_in_l3": {"text": "f8c = (T(c8) - T(c1)) / (T(c16) - T(c1)) against f8, fp32", "C_ALLOCATES": "f8c >= f8 + 0.30: C's 16 MB push the walk out of the L3",
                       "C_DOES_NOT": "|f8c - f8| <= 0.10", "PARTIAL": "otherwise", "frozen": pred["f"]["c8.fp32"]},
        "R6_c_traffic": {"text": "f16s = (T(c16s) - T(c1)) / (T(c16) - T(c1)), fp32", "PART": "f16s <= 0.85: C's 32 MB of stores are part of the cold walk's limit",
                         "NOT": "f16s >= 0.95", "PARTIAL": "between", "frozen": pred["f"]["c16s.fp32"]},
        "R7_power": {"text": "S over idle, zeros and random in every format on the eight new arms (48 cells), against the frozen S_w: PASS at rms <= 2.0 W",
                     "rms_w": 2.0},
        "R8_energy_order": {"text": "random fp32's energy per op rises along the repeat ladder: c1 < c16r32 < c16r8 < c16r4 < c16r2 < c16, means"},
        "clock": "every kept run's sampled clock is 600 MHz (reduce_e78.py's gate); a pass with TDP other than 0 or a threshold other than 65 C is reported apart",
    }
    out = {"experiment": "E107", "question": "section 11 item 1 of the kinds page as of 1fe8377a18af: where a large GEMM falls",
           "card": "aifoundry3 card 0, 600 MHz pinned (TDP 0 / 65 C), nothing set",
           "sources": {"e105c": os.path.relpath(E105C, ROOT), "e101": os.path.relpath(E101, ROOT),
                       "desk_l2": "tools/claims-v3/kspeed/e105/desk/l2sim.txt (by column: 0% steady, 66.7% one pass cold; packed: 75% steady)"},
           "arms": {a: {"values_arm": v[0], "blocks": v[1], "repeats": v[2], "c_shared": v[3], "ab_mb": v[4], "l3_footprint_mb": v[5], "what": v[6]}
                    for a, v in e7.ARMS.items()},
           "ends": ends, "energy_inputs_nj_op": model, "predictions": pred, "rules": rules,
           "speed_half": "not measured here: aifoundry3's clock is pinned, so what a clock gap buys needs a governed card (aifoundry2). Reported as a labelled "
                         "bound only: if no more than the FMA's 529 cycles of an fp32 op follow the clock (true of every fp32 arm E105 fitted), x1.333 of clock "
                         "buys at most T600 / (T600 - 529 (1/600 - 1/800) us).",
           "passes": list(e7.PASSES), "smoke_pass": e7.SMOKE_PASS, "cap_card_minutes": 60, "queue_deadline_min": 54,
           "harness": {"reused_unchanged_sha256": {p: sha(os.path.join(ROOT, p)) for p in REUSED}}}
    json.dump(out, open(os.path.join(HERE, "predictions-e107.json"), "w"), indent=1)
    L = ["E107 frozen numbers (make_predictions_e107.py), aifoundry3 at 600 MHz. T us per op of one minion; S W over idle.", ""]
    for ty in TYPES:
        en = ends[ty]
        L.append(f"{ty}: T(c1) {en['T_c1']:.4f}, T(c16) {en['T_c16']:.4f}, E101 as run {en['T_asrun_e101']:.4f}; an L3-served missing line "
                 f"{1000 * en['us_per_missing_line_l3']:.3f} ns")
    L.append("")
    L.append("arm      " + "  ".join(f"{ty:>18s}" for ty in TYPES))
    for a in e7.ARMS:
        L.append(f"{a:8s} " + "  ".join(f"T {pred['T_us'][f'{a}.{ty}']:.3f} f {pred['f'][f'{a}.{ty}']:.3f}" for ty in TYPES))
    L.append("")
    L.append("S over idle, W (zeros / random)")
    for a in e7.ARMS:
        L.append(f"{a:8s} " + "  ".join(f"{pred['S_w'][f'{a}.{ty}.zeros']:6.2f} / {pred['S_w'][f'{a}.{ty}.{RK[ty]}']:6.2f}" for ty in TYPES))
    L.append("")
    for k, v in rules.items():
        L.append(f"{k}: {v if isinstance(v, str) else v['text']}")
    open(os.path.join(HERE, "predictions-e107.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
