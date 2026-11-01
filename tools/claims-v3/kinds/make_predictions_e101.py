#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E101 (Q132): writes predictions-e101.json, the FROZEN predictions and rules of E101, from committed inputs only. No E101 data exists when this runs.

    /usr/bin/python3 tools/claims-v3/kinds/make_predictions_e101.py > tools/claims-v3/kinds/predictions-e101.txt

THE PREDICTION, per (arm, format, kind), of S, board power over idle at aifoundry3's 600 MHz, in E78's frame:

    S(arm, t, kind) = r(arm, t) x S_res(t, kind)  +  [E_base(arm) + E_data(arm, t, kind)] x rate(arm, t)

  S_res    the resident loop's S from E78 (e78.json); an E37-fill tile, never measured resident, takes E78's nearest kinds with a wide interval; the real set's first tile
           takes Q132(r)'s frozen D plus the format's zeros.
  r, rate  the multiply-adds' energy per op stays, the op rate follows the cycles per op: 546 / 546 / 318 resident (E78), 529 / 529 / 270 with B through TenB (E39),
           529 / 529 / 280.35 with A and B streamed (E37). The cooperative GEMM is given the benchmark's cycles.
  E_data   the memory path's data-dependent part, from E75's prices per changed bit, L2 0.274 pJ [0.183, 0.366], L1 0.0492 pJ, and each tile's changed bits between
           consecutive lines: a B line pays L2, an A line L2 and L1. Cooperative loads pay the L2 once per group (A 8 minions, B 4).
  E_base   the path's cost with nothing changing. mm16: from E37, S_E37 (leakage difference taken off) less r x S_res(e37) less E_data(e37), per format; the frozen value is
           their mean and its interval their range +- 0.5 nJ. tenb: E39's int8 ones cost, less the rate. gemm1: part of mm16's, plus one TensorStore per 32 ops.

THE CLOCK, per cell on aifoundry2: E83's frozen relation (predict_e83.Rel, the W* and sigma of predictions-real2.json's relation_e83) on c = c_zeros(t) + (S - S_res(t, zeros)) / xfer.
Nothing in this file has seen an E101 run.
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "kspeed", "e83"))
import e101_common as e101  # noqa: E402
import e78_common as ec  # noqa: E402
import predict_e83 as PE  # noqa: E402

E78J = "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json"
R2P = "tools/claims-v3/kinds/real2/predictions-real2.json"
E87P = "tools/claims-v3/kspeed/e87/predictions.json"
E37J = "docs/reports/data/2026-09-25-claims-v3/results/mmb.json"
INPUTS = {E78J: None, R2P: "0957e0c295990ac95cded56430697fb0683c9cf451d90f6943c8ff8d6a0b021a", E87P: "025f4e15950e75c3b21ea405ea15f04487cd1e56db4a7b308b19aa2ab7565ae8", E37J: None,
          "tools/claims-v3/kinds/kinds.json": "9586568f23a97757e34b3cdacdffe5bee0122d236e28a9f76f06e8598b7b1337",
          "tools/claims-v3/kinds/real2/real2.json": "6e259fd2e9edaa3d4fdeb663461ec39389ec8c24436c114719536a51d26c8715"}
CLOCK = 600e6
MINIONS = 1024
DUTY = 0.996                 # E78: launches cover 0.996-0.997 of the time at about 0.5 s a launch
TYPES = ("fp32", "fp16", "int8")
CPO = {"res": {"fp32": 546.0, "fp16": 546.0, "int8": 318.0},          # E78
       "tenb": {"fp32": 529.0, "fp16": 529.0, "int8": 270.0},         # E39, 05-claims.md:480
       "mm16": {"fp32": 529.0, "fp16": 529.0, "int8": 280.35},        # E37, 05-claims.md:468
       "gemm1": {"fp32": 529.0, "fp16": 529.0, "int8": 280.35},       # given the benchmark's; a prediction, not a measurement
       "gemmnc1": {"fp32": 529.0, "fp16": 529.0, "int8": 280.35}}
E75 = {"l2_pj_per_bit": (0.274, 0.183, 0.366), "l1_pj_per_bit": (0.0492, 0.0482, 0.0501),
       "dram_chord_w_per_75GBps": 3.250, "lines_per_s_75GBps": 1.1729e9, "source": "03-experiments.md E75 (docs/reports/data/2026-10-28-e75-memory-flip-ladder/); E81 repeats the DRAM chord"}
E39 = {"int8_ones_tenb_minus_l1_w": (2.40, 1.71, 3.10), "int8_random_tenb_minus_l1_w": (6.04, 3.65, 8.43), "fp16_random_tenb_minus_l1_w": 2.20,
       "source": "05-claims.md:481, aifoundry3, 99% over 3 blocks; these values are the register's"}
E37_LEAK_W = 0.8             # E37's S is not leakage-corrected: 0.2 W/C x its 62 C die against the 58 C launch E78's p80 refers to
E46_L3_PJ_B = 14.7           # the energy manual's L3 price, for the TensorStore of 1 KB per 32 ops (05-claims.md, Memory anatomy)
E_BASE_GEMM = (3.3, 1.5, 6.1)     # nJ per op: half of mm16's base stays (delivery) and half falls to 3/16 (coop), plus the store; the ends: all of it falls to 3/16, none of it does
KIND_ORDER = ("zeros", "ones", "random", "sparse50", "real")
FLOPS_PER_OP = {"fp32": 8192, "fp16": 16384, "int8": 32768}    # E80's 'operations per op'


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def line_bits(tile):
    """Mean changed bits between consecutive 64 B lines of a 1 KB tile, and over all 16 pairs in a repeating stream."""
    a = np.frombuffer(tile, dtype=np.uint8).reshape(16, 64)
    d = np.bitwise_xor(a, np.roll(a, -1, axis=0))
    return float(np.unpackbits(d, axis=1).sum(axis=1).mean())


def main():
    shas = {}
    for rel, want in INPUTS.items():
        got = sha(rel)
        if want and got != want:
            raise SystemExit(f"refused: {rel} sha256 {got}, frozen {want}")
        shas[rel] = got
    E78 = json.load(open(os.path.join(ROOT, E78J)))["items"]
    R2 = json.load(open(os.path.join(ROOT, R2P)))
    C87 = json.load(open(os.path.join(ROOT, E87P)))["constants"]
    M = json.load(open(os.path.join(ROOT, E37J)))
    e37c = next(i for i in M["items"] if i["item"] == "MMB-c")["per_card"]["aifoundry3"]
    S37 = {"fp32": e37c["fp32-tensor-L2"]["mean"], "fp16": e37c["fp16-tensor-L2"]["mean"], "int8": e37c["int8-tensor-L2"]["mean"]}
    S37_DRAM = e37c["fp32-tensor-DRAM"]["mean"]
    items = {it["name"]: it for it in e101.load_items()}

    def rate(arm, t):
        return CLOCK * MINIONS / CPO[arm][t] * DUTY / 1e9     # Gop/s

    def tile_of(t, k):
        name = f"{t}.{e101.kind_name(t, k)}" if k not in ("e37", "real") else f"res.{t}.{k}"
        return open(os.path.join(ROOT, items[name]["tile"]), "rb").read()

    bits = {t: {k: (line_bits(tile_of(t, k)[:1024]), line_bits(tile_of(t, k)[1024:])) for k in KIND_ORDER + ("e37",)} for t in TYPES}
    # the resident S
    Sres = {}
    for t in TYPES:
        Sres[t] = {}
        for k in ("zeros", "ones", "random", "sparse50"):
            e = E78[f"{t}.{e101.kind_name(t, k)}"]["S"]
            Sres[t][k] = (e["mean"], e["mean"] - e["ci95"], e["mean"] + e["ci95"])
        r2 = R2["tiles"][f"{t}/{e101.REAL_SET[t][0]}"]["a_aifoundry3_600mhz"]
        z = Sres[t]["zeros"][0]
        Sres[t]["real"] = (r2["D_w"] + z, r2["scoring_interval_w"][0] + z, r2["scoring_interval_w"][1] + z)
    pow2 = E78["fp32.pow2"]["S"]["mean"]
    Sres["fp32"]["e37"] = (pow2, pow2 - 3.0, pow2 + 3.0)
    si = E78["fp16.smallint"]["S"]["mean"]
    Sres["fp16"]["e37"] = (si, si - 3.0, si + 3.0)
    m8 = 0.5 * (E78["int8.ternary"]["S"]["mean"] + E78["int8.smallint"]["S"]["mean"])
    Sres["int8"]["e37"] = (m8, m8 - 1.0, m8 + 1.0)

    # the memory path's data part, nJ per op
    def e_data(arm, t, k, which=0):
        """which: 0 point, 1 low, 2 high (E75's L2 interval)."""
        l2 = E75["l2_pj_per_bit"][which]
        l1 = E75["l1_pj_per_bit"][which]
        ba, bb = bits[t][k]
        if arm in ("mm16", "gemmnc1"):
            pj = 16 * ba * (l2 + l1) + 16 * bb * l2
        elif arm == "tenb":
            pj = 16 * bb * l2
        elif arm == "gemm1":
            pj = 16 * ba * (l2 / 8 + l1) + 16 * bb * l2 / 4
            if which == 2:      # the high end: the group's L2 price does not fall
                pj = 16 * ba * (l2 + l1) + 16 * bb * l2
        else:
            raise SystemExit(arm)
        return pj / 1000.0

    # E_base from E37
    r_mm = {t: CPO["res"][t] / CPO["mm16"][t] for t in TYPES}
    base37 = {t: (S37[t] - E37_LEAK_W - r_mm[t] * Sres[t]["e37"][0]) / rate("mm16", t) - e_data("mm16", t, "e37") for t in TYPES}
    b = float(np.mean(list(base37.values())))
    E_BASE = {"mm16": (b, min(base37.values()) - 0.5, max(base37.values()) + 0.5)}
    E_BASE["gemmnc1"] = tuple(x + E46_L3_PJ_B * 1024 / 32 / 1000.0 for x in E_BASE["mm16"])
    E_BASE["gemm1"] = E_BASE_GEMM
    # B through TenB: E39's int8 ones
    z = E39["int8_ones_tenb_minus_l1_w"]
    r_t = CPO["res"]["int8"] / CPO["tenb"]["int8"]
    tb = [(v - (r_t - 1) * Sres["int8"]["ones"][0]) / rate("tenb", "int8") for v in z]
    E_BASE["tenb"] = (tb[0], tb[1], tb[2])

    def predict(arm, t, k):
        r = CPO["res"][t] / CPO[arm][t]
        R = rate(arm, t)
        s = Sres[t][k]
        p = r * s[0] + (E_BASE[arm][0] + e_data(arm, t, k, 0)) * R
        lo = r * s[1] + (E_BASE[arm][1] + e_data(arm, t, k, 1)) * R
        hi = r * s[2] + (E_BASE[arm][2] + e_data(arm, t, k, 2)) * R
        return p, lo, hi

    cells = {}
    for arm, kinds in e101.ARMS.items():
        if arm in ("gemm16", "mmp64"):
            continue
        for t in e101.ARM_TYPES[arm]:
            for k, tier in kinds.items():
                if tier is None:
                    continue
                p, lo, hi = predict(arm, t, k)
                cells[f"{arm}.{t}.{e101.kind_name(t, k)}"] = {"arm": arm, "type": t, "kind": k, "tier": tier, "S_w": round(p, 2), "S_lo_w": round(lo, 2), "S_hi_w": round(hi, 2),
                                                               "S_res_w": round(Sres[t][k][0], 3), "r": round(CPO["res"][t] / CPO[arm][t], 4), "rate_gops": round(rate(arm, t), 4),
                                                               "bits_a": round(bits[t][k][0], 1), "bits_b": round(bits[t][k][1], 1)}
    # The E37 tie: mm16 on E37's fill reads E37's value, leakage difference taken off
    tie37 = {t: {"S_e37_w": round(S37[t], 3), "S_w": round(S37[t] - E37_LEAK_W, 3), "band_w": 1.5, "cpo": CPO["mm16"][t]} for t in TYPES}
    # The kernel clause: mm16 over resident on E37's fill
    clause = {t: {"mm16_minus_res_w": round(S37[t] - E37_LEAK_W - Sres[t]["e37"][0], 2), "lo": round(S37[t] - E37_LEAK_W - 1.5 - Sres[t]["e37"][2], 2),
                  "hi": round(S37[t] - E37_LEAK_W + 1.5 - Sres[t]["e37"][1], 2)} for t in TYPES}
    # Memory path's data dependence: M(arm, t) = [S(arm, random) - S(arm, zeros)] - r [S_res(random) - S_res(zeros)]
    Mem = {}
    for arm in ("mm16", "gemm1"):
        for t in TYPES:
            R = rate(arm, t)
            Mem[f"{arm}.{t}"] = {"M_w": round(e_data(arm, t, "random", 0) * R, 2), "lo": round(e_data(arm, t, "random", 1) * R, 2), "hi": round(e_data(arm, t, "random", 2) * R, 2),
                                 "const_w": 0.0, "const_band_w": 1.0}
    # DRAM: mmp64 from E37's 15,144-15,662 cycles per op
    cpo_d = 15400.0
    ops = CLOCK * MINIONS / cpo_d
    lines = ops * 32
    dram = E75["dram_chord_w_per_75GBps"] * lines / E75["lines_per_s_75GBps"]
    fma = (E78["fp32.randn"]["pj_op_S"]["mean"] - E78["fp32.zeros"]["pj_op_S"]["mean"]) * ops * 1e-12
    dram_rule = {"cpo_e37": [15144.5, 15662.7], "ops_per_s": round(ops), "lines_per_s": round(lines), "GBps": round(lines * 64 / 1e9, 1), "dram_chord_w": round(dram, 2),
                 "fma_w": round(fma, 2), "random_minus_zeros_w": round(dram + fma, 2), "lo": round((dram + fma) * 0.75, 2), "hi": round((dram + fma) * 1.25, 2),
                 "zeros_S_lo_w": 3.0, "zeros_S_hi_w": round(S37_DRAM, 2),
                 "why": "E75's zeros-to-random chord at DRAM, scaled to the lines per second E37's private pools reached, plus the multiply-adds' own part at that rate; +-25%, about E75's +14% against the catalogue and E81's 1.636 W of the 3.250 W chord being arrangement"}
    # The clock
    B = {int(k): v for k, v in C87["B_registered_w"].items()}
    rel = PE.Rel(B)
    RR = R2["relation_e83"]
    Wb, sb, Ws, ss = RR["burst"]["W_star_w"], RR["burst"]["sigma_w"], RR["sustained"]["W_star_w"], RR["sustained"]["sigma_w"]
    xfer = RR["xfer"]
    cz = RR["c_zeros_w"]
    rms_b, rms_s = RR["relation_rms_mhz"]["burst"], RR["relation_rms_mhz"]["sustained"]

    def clocks(t, S, Slo, Shi):
        z = Sres[t]["zeros"][0]
        c, clo, chi = (cz[t] + (x - z) / xfer for x in (S, Slo, Shi))
        fb, sh_b = rel.f(c, Wb, sb)
        fs, sh_s = rel.f(c, Ws, ss)
        blo, bhi = rel.f(chi, Wb, sb)[0], rel.f(clo, Wb, sb)[0]
        slo, shi = rel.f(chi, Ws, ss)[0], rel.f(clo, Ws, ss)[0]
        P = rel.p(c)
        return {"c_w": round(c, 2), "burst_mhz": round(fb, 1), "burst_lo": round(max(600.0, blo - 1.96 * rms_b), 1), "burst_hi": round(min(800.0, bhi + 1.96 * rms_b), 1), "burst_share800": round(sh_b, 3),
                "sus_mhz": round(fs, 1), "sus_lo": round(max(600.0, slo - 1.96 * rms_s), 1), "sus_hi": round(min(800.0, shi + 1.96 * rms_s), 1), "sus_share800": round(sh_s, 3),
                "board_w_at_800": round(P[800], 1), "board_w_at_700": round(P[700], 1), "board_w_at_600": round(P[600], 1)}
    speed = {}
    for name, e in cells.items():
        if e["arm"] in ("mm16", "gemm1"):
            speed[name] = clocks(e["type"], e["S_w"], e["S_lo_w"], e["S_hi_w"])
    for t in TYPES:        # the resident anchors, for the ties to E80 and E83
        for k in ("zeros", "random"):
            s = Sres[t][k]
            speed[f"res.{t}.{e101.kind_name(t, k)}"] = clocks(t, *s)
    gaps = {}
    for arm in ("res", "mm16", "gemm1"):
        for t in TYPES:
            zn, rn = f"{arm}.{t}.zeros", f"{arm}.{t}.{e101.RANDOM_KIND[t]}"
            cp = CPO[arm][t]
            f = lambda n, key: speed[n][key]
            gaps[f"{arm}.{t}"] = {"burst_clock_ratio": round(f(zn, "burst_mhz") / f(rn, "burst_mhz"), 3), "sus_clock_ratio": round(f(zn, "sus_mhz") / f(rn, "sus_mhz"), 3),
                                  "burst_top_rate": round(f(rn, "burst_mhz") * 1e6 * MINIONS / cp * FLOPS_PER_OP[t] / 1e12, 2), "sus_top_rate": round(f(rn, "sus_mhz") * 1e6 * MINIONS / cp * FLOPS_PER_OP[t] / 1e12, 2)}
    pred = {
        "experiment": "E101", "request": "Q132", "date": "2026-11-01", "what": "frozen predictions and decision rules for E101, the same kinds of numbers in a matmul that streams its operands",
        "inputs_sha256": shas, "inputs": {"E75": E75, "E39": E39, "e37_leak_w": E37_LEAK_W, "e46_l3_pj_b": E46_L3_PJ_B, "cpo": CPO, "duty": DUTY},
        "bits_per_line": {t: {k: [round(x, 1) for x in v] for k, v in bits[t].items()} for t in TYPES},
        "S_res": {t: {k: [round(x, 3) for x in v] for k, v in Sres[t].items()} for t in TYPES},
        "E_base_nj_per_op": {k: [round(x, 3) for x in v] for k, v in E_BASE.items()}, "e_base_from_e37_by_format": {t: round(v, 3) for t, v in base37.items()},
        "cells": cells, "tie_e37": tie37, "kernel_clause": clause, "memory_path": Mem, "dram": dram_rule,
        "clock": {"relation": {"burst": RR["burst"], "sustained": RR["sustained"], "xfer": xfer, "c_zeros_w": cz, "rms_mhz": RR["relation_rms_mhz"], "B_registered_w": C87["B_registered_w"], "s_f": C87["s_f"]},
                  "cells": speed, "gaps": gaps},
    }
    pred["rules"] = json.load(open(os.path.join(HERE, "rules-e101.json")))
    # The freeze of the code the session runs
    reused = ["tools/claims-v3/kinds/run_e78.py", "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/lib.sh"]
    mine = ["tools/claims-v3/kinds/e101_common.py", "tools/claims-v3/kinds/run_e101.py", "tools/claims-v3/kinds/reduce_e101.py", "tools/claims-v3/kinds/block_e101.sh", "tools/claims-v3/kinds/queue_e101.sh",
            "tools/claims-v3/kinds/run_e101.sh", "tools/claims-v3/rgm/host/main.cpp", "tools/claims-v3/rgm/kernel/sparsity.c", "tools/claims-v3/rgm/sparsity_args.h"]
    pred["harness"] = {"reused_unchanged_sha256": {r: sha(r) for r in reused}, "e101_files_sha256": {r: sha(r) for r in mine}}
    json.dump(pred, open(os.path.join(HERE, "predictions-e101.json"), "w"), indent=1)
    # the table
    print("E101 frozen predictions, S over idle at 600 MHz on aifoundry3 (W), and the clock on aifoundry2 (MHz)")
    print(f"E_base nJ/op: {pred['E_base_nj_per_op']}; from E37 by format: {pred['e_base_from_e37_by_format']}")
    print(f"{'cell':26s} {'S':>6s} {'lo':>6s} {'hi':>6s} {'S_res':>6s} | {'c':>6s} {'burst':>6s} [{'lo':>5s},{'hi':>5s}] {'sus':>6s} [{'lo':>5s},{'hi':>5s}] {'P@800':>6s}")
    for n, e in cells.items():
        s = speed.get(n)
        tail = f"{s['c_w']:6.2f} {s['burst_mhz']:6.1f} [{s['burst_lo']:5.0f},{s['burst_hi']:5.0f}] {s['sus_mhz']:6.1f} [{s['sus_lo']:5.0f},{s['sus_hi']:5.0f}] {s['board_w_at_800']:6.1f}" if s else ""
        print(f"{n:26s} {e['S_w']:6.2f} {e['S_lo_w']:6.2f} {e['S_hi_w']:6.2f} {e['S_res_w']:6.2f} | {tail}")
    print("gaps", json.dumps(gaps, indent=0))
    print("memory path", json.dumps(Mem))
    print("kernel clause", json.dumps(clause))
    print("tie e37", json.dumps(tie37))
    print("dram", json.dumps(dram_rule))


if __name__ == "__main__":
    main()
