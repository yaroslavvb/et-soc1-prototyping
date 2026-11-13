#!/usr/bin/env python3
"""The loads the ledger v2 is scored on, described by their inputs only, and their frozen predictions (Q166).

Writes docs/reports/data/2026-11-12-q166-ledger-v2/predictions-v2.json from frozen-v2.json and the loads below.
It reads each load's OPERATING POINT and COUNTS from its committed record (die temperature, cycles per op, op and
tile counts, the host's model of a launch, the measured seconds) and never a measured energy or watt: those are read
only by score_ledger_v2.py, after this file's output is committed.

Held out, not blind: every measurement below existed before this file was written (E39 26 Sep, E37 26 Sep, E59
29 Sep), and the November checkpoint page quotes several of them. Counts a counter (step 2) would replace are named
in each load's `counts` with their bracket.

    python3 -I -B tools/ledger/loads_ledger_v2.py [--frozen PATH] [--out PATH]

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ledger_v2 as L  # noqa: E402

REPO = L.REPO
DATA = os.path.join(REPO, "docs", "reports", "data")
OUT_DIR = os.path.join(DATA, "2026-11-12-q166-ledger-v2")
F_HZ = 600e6
N_MIN = 1024

P_MMB = "docs/reports/data/2026-09-25-claims-v3/results/mmb.json"
P_SP = "workloads/sparseparity/data/2026-09-29-aifoundry3-m5-energy/energy"
P_E101 = "docs/reports/data/2026-11-01-e101-real-matmul/e101.json"
P_E136 = "docs/reports/data/2026-11-02-e136-large-gemm/results.json"

# Set-bit and changed-bit shares of the data kinds (hand-counted from each kind's definition; random = 0.5, 0.5)
DATA = {
    "zeros": (0.0, 0.0, "all zero words"),
    "random": (0.5, 0.5, "random bits"),
    "pm1_int8": (4.5 / 8, 3.5 / 8, "random 0x01 / 0xFF bytes: 1 and 8 set bits; a change flips 7 bits, half the time"),
    "mmbench_fp32": (4.5 / 32, 4.5 / 32, "fp32 {-2,-1,1,2}: 1.0f has 7 set bits, 2.0f 1, the sign 0.5; a change of "
                                         "magnitude flips 8 bits half the time, the sign half the time"),
}


def rd(rel):
    return json.load(open(os.path.join(REPO, rel)))


# ---------------------------------------------------------------- the sparse-parity plan's counts (pure Python port)
class Geom:
    """workloads/sparseparity/tools/cycle_model.py Geom, line for line (no numpy)."""

    def __init__(self, n, k, m):
        self.n, self.k, self.m = n, k, m
        self.S = (m + 63) // 64
        self.nJ = (n + 15) // 16
        self.nrows = math.comb(n - 1, k - 1)
        self.ntiles = (self.nrows + 15) // 16
        rs = [self.ntiles] * (self.nJ + 2)
        for J in range(self.nJ + 1):
            if J == 0:
                rs[J] = 0
            elif k == 1:
                rs[J] = self.ntiles
            else:
                rs[J] = min(self.ntiles, (math.comb(16 * J - 1, k - 1) + 15) // 16)
        rs[self.nJ + 1] = self.ntiles
        self.runStart = rs
        self.workTiles = rs[self.nJ]

    def rle(self, t0, t1):
        out = []
        for J in range(self.nJ):
            a, b = max(self.runStart[J], t0), min(self.runStart[J + 1], t1)
            if b > a:
                out.append((self.nJ - J, b - a))
        return out


def host_tile_cycles(nJ, J, S):
    """cycle_model.py host_tile_cycles (M1's cost, which --slice-cost m1 cuts the halves by)."""
    nout = float(nJ - J)
    ops = nout * S
    res = S <= 3
    hart0 = ops * (270.0 if res else 280.35) + nout * 450.0 + (S * 1024.0 / 4.0 if res else 0.0)
    by = ops * 1024.0 + (S * 1024.0 if res else ops * 1024.0) + S * 1024.0
    return max(hart0, S * 800.0, by / 4.0)


def cut_first_block(G, nblocks, t0, t1):
    """cycle_model.py cut_blocks, enough of it for slice 0 of 2 (the boundary between the halves)."""
    cost = lambda J: host_tile_cycles(G.nJ, J, G.S)  # noqa: E731
    total = 0.0
    for J in range(G.nJ + 1):
        a, b = max(G.runStart[J], t0), min(G.runStart[J + 1], t1)
        if b > a:
            total += (b - a) * cost(J)
    cur0, acc, made = t0, 0.0, 0
    blocks = []
    for J in range(G.nJ + 1):
        if made + 1 >= nblocks:
            break
        a, b = max(G.runStart[J], t0), min(G.runStart[J + 1], t1)
        if b <= a:
            continue
        c = cost(J)
        t = a
        while t < b and made + 1 < nblocks:
            target = total * (made + 1) / nblocks
            need = (target - acc) / c
            take = 0 if need <= 0 else int(math.ceil(need - 1e-9))
            if take > b - t:
                acc += (b - t) * c
                t = b
                break
            t += take
            acc += take * c
            blocks.append((cur0, t - cur0))
            cur0 = t
            made += 1
    blocks.append((cur0, t1 - cur0))
    return blocks


def sp_counts(n, k, m, slice_i, slice_n):
    G = Geom(n, k, m)
    if slice_n <= 1:
        t0, t1 = 0, G.workTiles
    else:
        tb, nt = cut_first_block(G, slice_n, 0, G.workTiles)[slice_i]
        t0, t1 = tb, tb + nt
    rle = G.rle(t0, t1)
    rows = sum(c for _, c in rle)
    outs = sum(nout * c for nout, c in rle)
    return {"S": G.S, "row_tiles": rows, "output_tiles": outs, "ops": outs * G.S, "tiles": [t0, t1], "nJ": G.nJ}


def e59_loads(F):
    cy = F["cycle_model"]["FITTED"]
    runs = [("L1 (512,4,0.3,448)", "aifoundry3-1136-l1", 512, 4, 448, 0, 1),
            ("L2 (512,4,0.4,1850)", "aifoundry3-1136-l2", 512, 4, 1850, 0, 1),
            ("(256,5,0.4,1925) first half", "aifoundry3-1136-f5h0", 256, 5, 1925, 0, 2),
            ("(256,5,0.4,1925) second half", "aifoundry3-1136-f5h1", 256, 5, 1925, 1, 2)]
    loads = []
    for name, d, n, k, m, si, sn in runs:
        plan = rd(f"{P_SP}/{d}/plan.json")
        en = rd(f"{P_SP}/{d}/energy.json")
        cnt = sp_counts(n, k, m, si, sn)
        assert cnt["ops"] == plan["ops"], (name, cnt["ops"], plan["ops"])          # the port reproduces the plan
        assert cnt["output_tiles"] == plan["dump_tiles"], name
        S, U = cnt["S"], plan["model_U"]
        rows, outs, ops = cnt["row_tiles"], cnt["output_tiles"], cnt["ops"]
        gen_per_tile = (cy["G_TILE"] / 2.0 + S * (cy["G_SLICE"] + cy["G_K"] / 8.0)) * (1.0 + cy["KAPPA_G"] * U)
        store_cov = S * 1024.0 / F["probe_rates_b_per_minion_cycle"]["scp_store"]   # inside scp_store's price
        cyc = {"epilogue": outs * cy["E_OUT"], "row_tile_overhead": rows * cy["H_TILE"],
               "generation_hart1_beyond_its_stores": rows * max(0.0, gen_per_tile - store_cov)}
        hart0_busy = ops * cy["C_OP_str"] * (1.0 + cy["KAPPA_T"] * U) + outs * (cy["D_OUT_str"] + cy["E_OUT"]) \
            + rows * cy["H_TILE"]
        hart1_busy = rows * gen_per_tile
        x = DATA["pm1_int8"]
        common = {
            "card": "aifoundry3", "f_mhz": 600.0, "die_start_c": en["die_c"]["before"],
            "work_units": 1, "work_unit": "solve (one launch)",
            "tensor": [{"format": "int8", "kind": "int8.pm1", "ops": ops}],
            "instr": [{"class": "vec_int", "hart_cycles": cyc["epilogue"], "what": "epilogue (hart 0)"},
                      {"class": "vec_int", "hart_cycles": cyc["row_tile_overhead"], "what": "row-tile set-up (hart 0)"},
                      {"class": "vec_int", "hart_cycles": cyc["generation_hart1_beyond_its_stores"],
                       "what": "row generation beyond its stores (hart 1)"}],
            "bytes": [{"path": "scp_load", "bytes": 2048.0 * ops, "rho": x[0], "tau": x[1],
                       "what": "A and B tensor loads, 2 KB an op"},
                      {"path": "scp_store", "bytes": 1024.0 * S * rows, "rho": x[0], "tau": x[1],
                       "what": "hart 1's staged rows, S KB a row tile"},
                      {"path": "dram_load", "bytes": 32.0 * n * S * 64.0, "rho": x[0], "tau": x[1],
                       "what": "X copied into each shire's scratchpad, once a launch"},
                      {"path": "l2_stream", "bytes": 192.0 * S * rows, "rho": x[0], "tau": x[1],
                       "what": "hart 1's reads of X slice-major, about 3 lines a slice"}],
        }
        inputs = {"n": n, "k": k, "m": m, "slice": f"{si}/{sn}", "S": S, "U_planner": U,
                  "counts": {"ops": ops, "output_tiles": outs, "row_tiles": rows,
                             "how": "exact: the planner's geometry (workloads/sparseparity/tools/cycle_model.py Geom and "
                                    "cut_blocks, ported) reproduces plan.json's ops and dump_tiles; a counter would "
                                    "confirm them from the kernel's own records"},
                  "hart_cycles": cyc, "hart0_busy_cycles": hart0_busy, "hart1_busy_cycles": hart1_busy,
                  "gen_cycles_per_row_tile": gen_per_tile, "store_covered_cycles_per_row_tile": store_cov,
                  "hart_cycles_how": "the cycle model's fitted constants (C_OP_str, D_OUT_str, E_OUT per output tile, "
                                     "H_TILE per row tile, generation per row tile in variant b) times the counts; "
                                     "hart 1's cycles inside its stores' price (S KB at the catalogue probe's 2.0 B a "
                                     "minion-cycle) are not priced again (frozen-v2.json awake_rule); a counter would "
                                     "replace these with instructions by class; bracket via issue_rate and the class band",
                  "bytes_how": "hand-counted from the kernel's description (README 'The kernel, per minion'): 2 KB of "
                               "tensor loads an op (A streamed, S > 3), S KB staged a row tile, X copied once a launch "
                               "per shire, about 3 lines of X read a slice; bracket: each path's catalogue bar",
                  "sources": {"plan": f"{P_SP}/{d}/plan.json (ops, dump_tiles, model_U, model_s)",
                              "seconds": f"{P_SP}/{d}/energy.json solves_per_s, launch_s_mean (measured)",
                              "die_start": f"{P_SP}/{d}/energy.json die_c.before"}}
        variants = {}
        for which, t_wall, t_kernel in (("given_seconds", 1.0 / en["solves_per_s"], en["launch_s_mean"]),
                                        ("forecast_seconds", plan["model_s"], plan["model_s"])):
            ld = dict(common)
            ld["seconds"] = t_wall
            per_hart = N_MIN * F_HZ * t_kernel
            aw0 = max(0.0, per_hart - hart0_busy)
            aw1 = max(0.0, per_hart - hart1_busy)
            ld["awake_hart_cycles"] = aw0 + aw1
            ld["_note"] = {"t_kernel_s": t_kernel, "t_wall_s": t_wall, "hart_cycles_per_hart": per_hart,
                           "hart0_busy_share": hart0_busy / per_hart, "hart1_busy_share": hart1_busy / per_hart,
                           "awake_hart0": aw0, "awake_hart1": aw1}
            variants[which] = ld
        loads.append({"load": "E59", "name": name, "inputs": inputs, "variants": variants,
                      "quantity": "over idle, leak-corrected (E59's headline subtracts the leakage law on the measured "
                                  "die): compare w_over_idle and per_unit.j_over_idle; j_total includes the rise",
                      "label": "held out, not blind"})
    return loads


# ---------------------------------------------------------------- E37: mmbench fp32 from DRAM
def e37_loads(F):
    mm = rd(P_MMB)["items"]
    cyc = {}
    die = {}
    for it in mm:
        if it.get("item") == "MMB-a":
            for card, v in it["per_card"].items():
                lo, hi = v["fp32-tensor-DRAM"]["cycles_per_op_mean_based"]
                cyc[card] = 0.5 * (lo + hi)
        if it.get("item") == "MMB-c":
            for card, v in it["per_card"].items():
                die[card] = v["fp32-tensor-DRAM"]["die_c_mean"]
    bw = L._c(F, "dram_bandwidth_gb_s") * 1e9
    c_fore = 2048.0 * N_MIN * F_HZ / bw
    x = DATA["mmbench_fp32"]
    loads = []
    for card in ("aifoundry2", "aifoundry3", "aifoundry1-c1"):
        variants = {}
        for which, c in (("given_seconds", cyc[card]), ("forecast_seconds", c_fore)):
            ops = N_MIN * F_HZ / c
            variants[which] = {
                "card": card, "f_mhz": 600.0, "die_start_c": die[card], "seconds": 1.0,
                "work_units": ops, "work_unit": "op (one minion's 16x16x16 fp32 TensorFMA)",
                "tensor": [{"format": "fp32", "kind": "fp32.small_int", "ops": ops}],
                "awake_hart_cycles": max(0.0, c - 546.0 - 2048.0 / F["probe_rates_b_per_minion_cycle"]["dram_load"]) * ops,
                "bytes": [{"path": "dram_load", "bytes": 2048.0 * ops, "rho": x[0], "tau": x[1],
                           "what": "A and B tiles, 2 KB an op, every one from DRAM"}],
                "_note": {"cycles_per_op": c},
            }
        loads.append({"load": "E37", "name": f"mmbench fp32 from DRAM, {card}",
                      "inputs": {"cycles_per_op_measured": cyc[card], "cycles_per_op_forecast": c_fore,
                                 "die_c_mean": die[card],
                                 "counts": {"bytes_per_op": 2048, "bracket": [1024, 2048],
                                            "how": "hand-counted: launchers/mmbench (64 private tiles a minion, 128 MB, "
                                                   "past the 32 MB L3: 'a large private pool per minion makes every "
                                                   "load come from DRAM', kernels/mmbench/mmbench.cc); bracket down to "
                                                   "half for whatever the L3 still catches; a counter's DRAM-side "
                                                   "read counts (the two system calls) would replace it"},
                                 "data": "launchers/mmbench/mmbench.cpp fills A and B with {-2, -1, 1, 2}: v2's "
                                         "fp32.small_int kind and the mmbench_fp32 set-bit shares, not random data",
                                 "sources": {"cycles": P_MMB + " MMB-a per_card.<card>['fp32-tensor-DRAM']."
                                                       "cycles_per_op_mean_based (midpoint of the pass means)",
                                             "die": P_MMB + " MMB-c ...die_c_mean"},
                                 "seconds_forecast_how": "DRAM-bound: 2,048 B an op over 1,024 minions at the "
                                                         "catalogue's 76 GB/s"},
                      "variants": variants,
                      "quantity": "board power over the pre-launch idle, the run's own heating included "
                                  "(compare w_over_idle_with_heat)",
                      "label": "held out, not blind"})
    return loads


# ---------------------------------------------------------------- E39: the gemv sparsity ladder (fp32 in the L1)
E39_X = {"fma-dense": 1.0, "fma-50": 0.503, "fma-rowmask": 0.5, "fma-col50": 0.438, "fma-875": 0.105, "fma-zero": 0.0}
E39_DIE = {"aifoundry2": 80.5, "aifoundry3": 58.0, "aifoundry1-c1": 80.3}


def e39_loads(F):
    loads = []
    for card, die in E39_DIE.items():
        ops = N_MIN * F_HZ / 546.0
        rungs = {}
        for cfg, xf in E39_X.items():
            rungs[cfg] = {"card": card, "f_mhz": 600.0, "die_start_c": die, "seconds": 1.0,
                          "work_units": ops, "work_unit": "op",
                          "tensor": [{"format": "fp32", "kind": "fp32.small_int", "ops": ops, "live": xf}]}
        loads.append({"load": "E39", "name": f"gemv sparsity ladder, {card}", "rungs": rungs,
                      "inputs": {"useful_slot_fraction": E39_X, "die_start_c": die, "cycles_per_op": 546.0,
                                 "data": "the sparsity host's default fp32 operands, random non-zero integers in "
                                         "[-3, 3] (workloads/sparsity/host smallNonzero; tools/claims-v3/ablb/"
                                         "v3-energy.cfg 'fma-* use the host's default small-integer operands')",
                                 "sources": {"x and die": "tools/ettelem/freeze_load_predictions.py E39_X and E39_DIE "
                                                          "(v1's operating points, read from E39's record)"},
                                 "rule": "D scales with the useful-slot fraction (a zero word gates its lane's "
                                         "data-dependent switching); the zeros anchor Z is paid at every rung"},
                      "quantity": "board power over the pre-launch idle, the run's own heating included; scored as "
                                  "v1 was: the line's slope and intercept (six independent predictions)",
                      "label": "held out, not blind"})
    return loads


# ---------------------------------------------------------------- beside them: E101, E136, E86, E95
def e101_loads(F):
    e = rd(P_E101)
    cyc = e["cycles_per_op"]
    loads = []
    kind_of = {("fp32", "random"): "fp32.randn", ("fp16", "random"): "fp16.randn", ("int8", "random"): "int8.full",
               ("fp32", "zeros"): "fp32.zeros", ("fp16", "zeros"): "fp16.zeros", ("int8", "zeros"): "int8.zeros",
               ("fp32", "e37"): "fp32.small_int"}
    loop = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
    cells = []
    for fmt in ("fp32", "fp16", "int8"):
        rk = "full" if fmt == "int8" else "randn"
        for dk, ik in (("zeros", "zeros"), ("random", rk)):
            cells.append(("res", fmt, dk, f"{fmt}.{ik}", None))
            cells.append(("mm16", fmt, dk, f"mm16.{fmt}.{ik}", "l2_stream"))
    cells.append(("res", "fp32", "e37", "res.fp32.e37", None))
    cells.append(("mm16", "fp32", "e37", "mm16.fp32.e37", "l2_stream"))
    cells.append(("mmp64", "fp32", "zeros", "mmp64.fp32.zeros", "dram_load"))
    cells.append(("mmp64", "fp32", "random", "mmp64.fp32.randn", "dram_load"))
    for arm, fmt, dk, item, path in cells:
        c = cyc[fmt] if arm == "res" else cyc[f"{arm}:{fmt}"]
        ops = N_MIN * F_HZ / c
        dd = {"zeros": DATA["zeros"], "random": DATA["random"], "e37": DATA["mmbench_fp32"]}[dk]
        ld = {"card": "aifoundry3", "f_mhz": 600.0, "die_start_c": 58.0, "seconds": 1.0,
              "work_units": ops, "work_unit": "op",
              "tensor": [{"format": fmt, "kind": kind_of[(fmt, dk)], "ops": ops}]}
        if path:
            ld["bytes"] = [{"path": path, "bytes": 2048.0 * ops, "rho": dd[0], "tau": dd[1]}]
        if arm == "mmp64":
            ld["awake_hart_cycles"] = max(0.0, c - loop[fmt] - 2048.0 / F["probe_rates_b_per_minion_cycle"]["dram_load"]) * ops
        cells_label = ("in sample for the l2_stream price (E101's own post hoc path cost)" if path == "l2_stream"
                       else "held out for every price it uses (the catalogue's DRAM row; E101 in sample for w_set "
                            "only through phi of random and zeros, where w_set cancels)" if path == "dram_load"
                       else "the loop: M10's kernel term on a session M10 never saw")
        loads.append({"load": "E101", "name": f"{arm} {fmt} {dk}", "item": item, "variants": {"given_seconds": ld},
                      "inputs": {"cycles_per_op": c, "source": P_E101 + " cycles_per_op"},
                      "quantity": "S, board power over each run's idle, leak-corrected at E101's registered slope "
                                  "(compare w_over_idle)",
                      "label": cells_label})
    return loads


def e136_loads(F):
    r = rd(P_E136)
    loads = []
    for fmt, rk in (("fp32", "randn"), ("fp16", "randn"), ("int8", "full")):
        T = r["per_gemm"][f"g4k.{fmt}"]["T800"] * 1e-6
        ops = N_MIN / T
        pair = {}
        for dk, kind, dd in (("random", f"{fmt}.{rk}" if fmt != "int8" else "int8.full", DATA["random"]),
                             ("zeros", f"{fmt}.zeros", DATA["zeros"])):
            pair[dk] = {"card": "aifoundry2", "f_mhz": 800.0, "die_start_c": 50.0, "seconds": 1.0,
                        "work_units": ops, "work_unit": "op",
                        "tensor": [{"format": fmt, "kind": kind, "ops": ops}],
                        "bytes": [{"path": "l3_load", "bytes": 106.1 * 64.0 / 32.0 * ops, "rho": dd[0], "tau": dd[1],
                                   "what": "E136.md's desk split P1: 106.1 lines a shire-op from the L3"},
                                  {"path": "dram_load", "bytes": 85.9 * 64.0 / 32.0 * ops, "rho": dd[0], "tau": dd[1],
                                   "what": "and 85.9 fresh lines from DRAM"}]}
        loads.append({"load": "E136", "name": f"g4k {fmt}, random over zeros, burst at 800 MHz",
                      "pair": pair,
                      "inputs": {"T800_us": T * 1e6, "source": P_E136 + f" per_gemm.g4k.{fmt}.T800 (measured)",
                                 "bytes_source": "tools/claims-v3/e136/E136.md 'Its own reuse and footprint' (P1, "
                                                 "frozen before E136 ran: 192 lines a shire-op, 106.1 from the L3, "
                                                 "85.9 fresh; cooperative loads, so 384 B a minion-op beyond the L2)"},
                      "quantity": "random minus zeros, board power at 800 MHz in a burst (burst_p800_w), so the card at "
                                  "rest and the clock's static part cancel; v2 has no validated 800 MHz static term",
                      "label": "held out, not blind; differences only; aifoundry2's D carried from aifoundry3 by E38's "
                               "card scale; the L3 row has no zeros/random split, so its share of the difference is "
                               "zero by construction"})
    return loads


def e86_e95_loads(F):
    loads = []
    for kind, per in sorted(F["kinds"].items()):
        e = per.get("a3")
        if not e or not e.get("m10_kinds"):
            continue
        exps = set(x for u in e["m10_kinds"] for x in u["rows"])
        if not exps & {"E86", "E95"}:
            continue
        fmt = kind.split(".")[0]
        rate = F["zeros_anchor"][fmt]["a3"]["rate_ops_per_s"]
        ld = {"card": "aifoundry3", "f_mhz": 600.0, "die_start_c": 58.0, "seconds": 1.0, "work_units": rate,
              "work_unit": "op", "tensor": [{"format": fmt, "kind": kind, "ops": rate}]}
        for ex in sorted(exps & {"E86", "E95"}):
            loads.append({"load": ex, "name": kind, "variants": {"given_seconds": ld},
                          "quantity": "S, board power over the run's idle in the resident loop (compare w_over_idle)",
                          "label": "held out by kind (M10 was fitted on these rows, each predicted with its own kind "
                                   "left out, and its session's own random anchors setting the float scale)"})
    return loads


def run(load_variant, F):
    out = L.predict(load_variant, F)
    out["inputs_echo"] = {k: v for k, v in load_variant.items() if not k.startswith("_")}
    if "_note" in load_variant:
        out["note"] = load_variant["_note"]
    return out


def tensor_live(ld, F):
    """predict() with a live fraction on the tensor term (E39's rungs): Z at every op, D times the live share."""
    ld2 = json.loads(json.dumps(ld))
    live = ld2["tensor"][0].pop("live", 1.0)
    full = L.predict(ld2, F)
    zeros = json.loads(json.dumps(ld2))
    fmt = zeros["tensor"][0]["format"]
    zeros["tensor"][0]["kind"] = f"{fmt}.zeros"
    z = L.predict(zeros, F)
    # interpolate every additive quantity between the zeros run and the full run
    def mix(a, b):
        return a + live * (b - a)
    j_over = mix(z["j_over_idle"], full["j_over_idle"])
    lo = mix(z["j_over_idle_band"][0], full["j_over_idle_band"][0])
    hi = mix(z["j_over_idle_band"][1], full["j_over_idle_band"][1])
    t = ld["seconds"]
    k_leak = full["heat"]["k_leak_w_per_c"]
    kr = L._c(F, "k_rise_c_per_w")
    kr_lo, kr_hi = L._cb(F, "k_rise_c_per_w")
    kb = F["leak_slope_band_rel"]
    dT = kr * j_over / t
    j_heat = k_leak * dT * t
    return {"live": live, "w_over_idle": j_over / t, "w_over_idle_band": [lo / t, hi / t],
            "heat": {"k_leak_w_per_c": k_leak, "die_rise_c": dT, "w": j_heat / t},
            "w_over_idle_with_heat": (j_over + j_heat) / t,
            "w_over_idle_with_heat_band": [(lo + k_leak * kb[0] * kr_lo * lo) / t, (hi + k_leak * kb[1] * kr_hi * hi) / t],
            "rest_w": full["rest"]["w"],
            "terms_full_kind": {k: {"j": v["j"], "band": v["band"]} for k, v in full["terms"].items()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frozen", default=L.FROZEN_DEFAULT)
    ap.add_argument("--out", default=os.path.join(OUT_DIR, "predictions-v2.json"))
    a = ap.parse_args()
    F = L.load_frozen(a.frozen)
    import hashlib
    fz_sha = hashlib.sha256(open(a.frozen, "rb").read()).hexdigest()
    P = {"what": "load ledger v2's frozen predictions (Q166, calc-a), from frozen-v2.json and the loads' inputs only",
         "frozen_v2_sha256": fz_sha, "frozen_pst": F["frozen_pst"], "loads": []}
    for ld in e59_loads(F) + e37_loads(F):
        ld["predicted"] = {w: run(v, F) for w, v in ld["variants"].items()}
        P["loads"].append(ld)
    for ld in e39_loads(F):
        pr = {cfg: tensor_live(v, F) for cfg, v in ld["rungs"].items()}
        cfgs = list(ld["rungs"])
        xs = [ld["inputs"]["useful_slot_fraction"][c] for c in cfgs]
        for q in ("w_over_idle", "w_over_idle_with_heat"):
            ys = [pr[c][q] for c in cfgs]
            n = len(xs)
            sx, sy = sum(xs), sum(ys)
            sxx = sum(x * x for x in xs)
            sxy = sum(x * y for x, y in zip(xs, ys))
            m = (n * sxy - sx * sy) / (n * sxx - sx * sx)
            pr[f"line_{q}"] = {"slope_w": m, "intercept_w": (sy - m * sx) / n}
        lo_d = pr["fma-dense"]["w_over_idle_with_heat_band"]
        lo_z = pr["fma-zero"]["w_over_idle_with_heat_band"]
        pr["line_w_over_idle_with_heat"]["slope_band_w"] = [lo_d[0] - lo_z[1], lo_d[1] - lo_z[0]]
        pr["line_w_over_idle_with_heat"]["intercept_band_w"] = lo_z
        ld["predicted"] = pr
        P["loads"].append(ld)
    for ld in e101_loads(F) + e86_e95_loads(F):
        ld["predicted"] = {w: run(v, F) for w, v in ld["variants"].items()}
        P["loads"].append(ld)
    for ld in e136_loads(F):
        pr = {dk: run(v, F) for dk, v in ld["pair"].items()}
        d = pr["random"]["w_over_idle"] - pr["zeros"]["w_over_idle"]
        dlo = pr["random"]["w_over_idle_band"][0] - pr["zeros"]["w_over_idle_band"][1]
        dhi = pr["random"]["w_over_idle_band"][1] - pr["zeros"]["w_over_idle_band"][0]
        pr["difference_w"] = d
        pr["difference_band_w"] = [dlo, dhi]
        ld["predicted"] = pr
        P["loads"].append(ld)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(P, f, indent=1)
        f.write("\n")
    print("wrote", os.path.relpath(a.out, REPO), "loads", len(P["loads"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
