#!/usr/bin/env python3
"""Sparse parity's L1 solve: instructions counted in the simulator against the card's cycles and the cycle model.

    card_compare_sparseparity.py --dis sparseparity.dis --sites-all all-addr2line.txt.gz --run SLICE_RUNDIR
        [--run ...] --card-json m5-l1-b.json --card-rec m5-l1-b.rec --cycle-model tools/cycle_model.py [--out F.json]

Post hoc and desk only: no card runs. Each SLICE_RUNDIR is a `sparseparity_host --sysemu` run of one minion on a
slice of the same instance the card solved (variant b: --variant m1 --cost fit --gen inc), counted in log mode
(counts-log.json) with its records.bin and out.json. Every executed instruction is split by its source inline chain
(--sites-all: the ET toolchain's addr2line -f -i -a for every kernel address, from the -g build whose .text is the
run's): `spin` = inside wait_count (the polls of the other hart's line and their multiply pauses), whose count follows
the simulator's timing and not the card's; `work` = the rest. The work instructions are fitted as
hart 0 = a * output tiles + b * row tiles and hart 1 = c * row tiles (least squares over the slices; output tiles =
ops / S; hart 1 is also fitted with an intercept, c' * row tiles + d a launch, and both fits are reported), then scaled to every minion the card ran (its records give ops and row tiles) and set beside that minion's
measured cycles (hpmcounter3, hart 0, entry to exit) and the cycle model's fitted per-tile and per-op cycles
(workloads/sparseparity/tools/cycle_model.py FITTED, read as text; variant b's generation constants from its
variant_constants rule). The same fit, class by class and for the tensor unit's ops and bytes, gives the ledger's
counts for the whole solve (`per_solve`): an estimate scaled from three slices, labelled so. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import ast
import importlib.util
import gzip
import json
import os
import statistics
import struct
import sys

REC = struct.Struct("<qQQQiIQQII")


def read_sites(path):
    op = gzip.open if path.endswith(".gz") else open
    lines = [l.strip() for l in op(path, "rt").read().splitlines() if l.strip()]
    sites, cur, i = {}, None, 0
    while i < len(lines):
        if lines[i].startswith("0x"):
            cur = int(lines[i], 16)
            sites[cur] = []
            i += 1
            continue
        sites[cur].append(lines[i])
        i += 2
    return sites


def fitted(path):
    tree = ast.parse(open(path).read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "FITTED" for t in node.targets):
            call = node.value
            return {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}
    raise SystemExit("no FITTED in " + path)


def lstsq2(xs, ys):
    """y = a*x1 + b*x2, least squares, two unknowns."""
    s11 = sum(x[0] * x[0] for x in xs)
    s12 = sum(x[0] * x[1] for x in xs)
    s22 = sum(x[1] * x[1] for x in xs)
    t1 = sum(x[0] * y for x, y in zip(xs, ys))
    t2 = sum(x[1] * y for x, y in zip(xs, ys))
    det = s11 * s22 - s12 * s12
    a = (t1 * s22 - t2 * s12) / det
    b = (s11 * t2 - s12 * t1) / det
    return a, b


def line_fit(xs, ys):
    """y = m*x + q, least squares."""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    m = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return m, my - m * mx


def load_counter():
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("ledger_count_kernel", os.path.join(here, "count_kernel.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def classes_of(per_pc, by_addr, keep):
    """Instructions by class over the PCs `keep` accepts (conditional branches split by direction)."""
    out = {}
    for pc, (n, tk) in per_pc.items():
        a = int(pc, 16)
        if not keep(a):
            continue
        ins = by_addr[a]
        if ins.cls == "branch":
            out["branch_taken"] = out.get("branch_taken", 0) + tk
            out["branch_not_taken"] = out.get("branch_not_taken", 0) + n - tk
        else:
            out[ins.cls] = out.get(ins.cls, 0) + n
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dis", required=True)
    ap.add_argument("--sites-all", required=True)
    ap.add_argument("--run", action="append", required=True)
    ap.add_argument("--card-json", required=True)
    ap.add_argument("--card-rec", required=True)
    ap.add_argument("--cycle-model", required=True)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    sites = read_sites(a.sites_all)
    spin_pcs = set(pc for pc, ch in sites.items() if "wait_count" in ch)
    ck = load_counter()
    by_addr = {i.addr: i for i in ck.parse_dis(a.dis)}
    slices = []
    for run in a.run:
        cnt = json.load(open(os.path.join(run, "counts-log.json")))
        j = json.loads([l for l in open(os.path.join(run, "out.json")).read().splitlines() if l.startswith("{")][-1])
        rec = open(os.path.join(run, "records.bin"), "rb").read()
        S = j["geometry"]["S"]
        h = {}
        for t in ("0", "1"):
            pp = cnt["harts"][t]["per_pc"]
            spin = sum(n for pc, (n, tk) in pp.items() if int(pc, 16) in spin_pcs)
            h[t] = {"instructions": cnt["harts"][t]["instructions"], "spin": spin,
                    "work": cnt["harts"][t]["instructions"] - spin,
                    "work_by_class": classes_of(pp, by_addr, lambda x: x not in spin_pcs),
                    "spin_by_class": classes_of(pp, by_addr, lambda x: x in spin_pcs),
                    "tensor": cnt["harts"][t]["tensor"], "memory": cnt["harts"][t].get("memory", {})}
        r0, r1 = REC.unpack_from(rec, 0), REC.unpack_from(rec, 64)
        ops, tiles = r0[8], r1[2]
        slices.append({"run": os.path.basename(run.rstrip("/")), "slice": j["plan"]["slice"], "ops": ops,
                       "row_tiles": tiles, "output_tiles": ops / S, "S": S, "hart0": h["0"], "hart1": h["1"],
                       "sim_cycles_h0": r0[6], "sim_polls_h1": r1[7]})
    xs = [(s["output_tiles"], s["row_tiles"]) for s in slices]
    a0, b0 = lstsq2(xs, [s["hart0"]["work"] for s in slices])
    c1 = sum(s["hart1"]["work"] for s in slices) / sum(s["row_tiles"] for s in slices)
    res0 = [s["hart0"]["work"] - (a0 * s["output_tiles"] + b0 * s["row_tiles"]) for s in slices]
    res1 = [s["hart1"]["work"] - c1 * s["row_tiles"] for s in slices]
    c1i, d1i = line_fit([s["row_tiles"] for s in slices], [s["hart1"]["work"] for s in slices])
    res1i = [s["hart1"]["work"] - (c1i * s["row_tiles"] + d1i) for s in slices]
    # the card
    cj = json.loads([l for l in open(a.card_json).read().splitlines() if l.startswith("{")][-1])
    crec = open(a.card_rec, "rb").read()
    S = cj["geometry"]["S"]
    mins = []
    for g in range(len(crec) // 128):
        shire, mi = g // 32, g % 32
        h0 = shire * 64 + mi * 2
        r0, r1 = REC.unpack_from(crec, 64 * h0), REC.unpack_from(crec, 64 * (h0 + 1))
        ops, tiles, cyc = r0[8], r1[2], r0[6]
        if not ops:
            continue
        w0 = a0 * ops / S + b0 * tiles
        w1 = c1 * tiles
        w1i = c1i * tiles + d1i
        mins.append({"ops": ops, "tiles": tiles, "cycles": cyc, "work0": w0, "work1": w1,
                     "occupancy": (w0 + w1) / cyc, "h0_share": w0 / cyc, "h1_share": w1 / cyc,
                     "work1_intercept_fit": w1i, "occupancy_hart1_intercept_fit": (w0 + w1i) / cyc,
                     "polls_card": r1[7], "wait0_card": r0[7]})
    med = lambda k: statistics.median(m[k] for m in mins)
    P = fitted(a.cycle_model)
    g_tile_b = P["G_TILE"] * 0.5                 # variant_constants(gen_inc=True)
    g_slice_b = P["G_SLICE"] + P["G_K"] / 8.0
    model = {"hart0_per_row_tile_instr_cycles": P["H_TILE"], "hart0_per_output_tile_epilogue_cycles": P["E_OUT"],
             "hart0_per_op_tensor_cycles_streamed": P["C_OP_str"], "hart0_per_output_tile_tensor_extra": P["D_OUT_str"],
             "hart1_per_row_tile_cycles_variant_b": g_tile_b + S * g_slice_b,
             "note": "FITTED to M1-kernel card records (29 Sep); variant b's generation constants are the model's "
                     "prediction (variant_constants), not a fit"}
    counted = {"hart0_work_per_output_tile": a0, "hart0_work_per_row_tile": b0, "hart1_work_per_row_tile": c1,
               "fit_residuals_hart0": res0, "fit_residuals_hart1": res1,
               "hart1_fit_with_intercept": {"per_row_tile": c1i, "per_launch": d1i, "residuals": res1i,
                                            "note": "hart 1's work fitted as c' x row tiles + d a launch (added by "
                                                    "fix-q166 on verify-counter's finding: the fit through the origin "
                                                    "leaves a 27% residual on slice 0)"}}
    med_cycles = med("cycles")
    out = {"label": "post hoc, desk: simulator counts of three slices scaled to the card's L1 variant-b solve",
           "slices": slices, "counted_rates": counted, "cycle_model": model,
           "card": {"run": os.path.basename(a.card_json), "launch_s": cj["launch_s"], "clock_mhz_est":
                    cj["kernel"]["clock_mhz_est"], "minions": len(mins), "median_cycles": med_cycles,
                    "max_cycles": max(m["cycles"] for m in mins), "median_ops": med("ops"),
                    "median_row_tiles": med("tiles"), "median_polls_hart1": med("polls_card"),
                    "median_wait_cycles_hart0": med("wait0_card")},
           "comparison": {"median_counted_work_instructions_hart0": med("work0"),
                          "median_counted_work_instructions_hart1": med("work1"),
                          "median_issue_occupancy_by_counted_work": med("occupancy"),
                          "median_hart0_share": med("h0_share"), "median_hart1_share": med("h1_share"),
                          "hart1_ipc_vs_model": c1 / model["hart1_per_row_tile_cycles_variant_b"],
                          "median_issue_occupancy_hart1_intercept_fit": med("occupancy_hart1_intercept_fit"),
                          "median_counted_work_instructions_hart1_intercept_fit": med("work1_intercept_fit"),
                          "hart1_ipc_vs_model_intercept_fit": c1i / model["hart1_per_row_tile_cycles_variant_b"],
                          "hart0_tile_overhead_ipc_vs_model": b0 / P["H_TILE"],
                          "hart0_epilogue_ipc_vs_model": a0 / (P["E_OUT"])},
           "total_counted_work_instructions_card_solve": sum(m["work0"] + m["work1"] for m in mins)}
    # the ledger's counts for the card's whole solve, scaled from the slices by the same fits
    cls_names = sorted(set(k for sl in slices for t in ("hart0", "hart1") for k in sl[t]["work_by_class"]))
    per_solve = {"label": "estimate (desk): per-class rates fitted on three simulated slices, scaled by every "
                          "minion's ops and row tiles from the card's records; spin loops left out",
                 "minions": len(mins), "work_by_class": {}, "fit_residual_max_fraction": {}}
    sum_out = sum(m["ops"] / S for m in mins)
    sum_tiles = sum(m["tiles"] for m in mins)
    for c in cls_names:
        ac, bc = lstsq2(xs, [sl["hart0"]["work_by_class"].get(c, 0) for sl in slices])
        cc = sum(sl["hart1"]["work_by_class"].get(c, 0) for sl in slices) / sum(sl["row_tiles"] for sl in slices)
        per_solve["work_by_class"][c] = ac * sum_out + bc * sum_tiles + cc * sum_tiles
        resid = [abs(sl["hart0"]["work_by_class"].get(c, 0) + sl["hart1"]["work_by_class"].get(c, 0)
                     - (ac * sl["output_tiles"] + bc * sl["row_tiles"] + cc * sl["row_tiles"])) for sl in slices]
        tot = [sl["hart0"]["work_by_class"].get(c, 0) + sl["hart1"]["work_by_class"].get(c, 0) for sl in slices]
        per_solve["fit_residual_max_fraction"][c] = max((r / t) if t else 0 for r, t in zip(resid, tot))
    ops_card = sum(m["ops"] for m in mins)
    resc = [sl["hart0"]["tensor"].get("fma_int8", {}).get("ops", 0) - sl["ops"] for sl in slices]
    ar, br = lstsq2(xs, resc)
    bytes_per_op = [(sl["hart0"]["tensor"].get("load", {}).get("bytes", 0)
                     + sl["hart0"]["tensor"].get("load_tenb", {}).get("bytes", 0))
                    / sl["hart0"]["tensor"]["fma_int8"]["ops"] for sl in slices]
    stage_per_tile = [sl["hart1"]["memory"].get("store_past_l1", {}).get("scratchpad_own", {}).get("write_bytes", 0)
                      / sl["row_tiles"] for sl in slices]
    per_solve["tensor"] = {
        "int8_ops_counted_by_kernel": ops_card,
        "int8_ops_rescans_estimate": ar * sum_out + br * sum_tiles,
        "macs_per_op": 16384,
        "tensor_load_bytes_per_op_own_scratchpad": bytes_per_op,
        "staging_store_bytes_per_row_tile_own_scratchpad": stage_per_tile,
        "staging_store_instruction": "fswg.ps (a global store into the own scratchpad by its explicit shire "
                                     "address; the catalogue prices fswl.ps, not fswg.ps)",
        "l2scp_copy_in_bytes_per_shire_per_launch": [sl["hart0"]["tensor"].get("load_l2scp", {}).get("bytes", 0)
                                                     for sl in slices],
        "l2scp_copy_in_note": "X_B is copied into each shire's scratchpad once a launch, its chunks dealt to the "
                              "shire's minions (sparseparity.c: for ch = mi; ch < nJ*S; ch += P); the slices ran one "
                              "minion a shire, which copied its shire's whole share",
        "l2scp_copy_in_bytes_per_launch_card": [32 * sl["hart0"]["tensor"].get("load_l2scp", {}).get("bytes", 0)
                                                for sl in slices]}
    out["per_solve"] = per_solve
    if a.out:
        with open(a.out, "w") as f:
            json.dump(out, f, indent=1)
            f.write("\n")
    c = out["comparison"]
    print(f"counted work: hart 0 {a0:.1f} per output tile + {b0:.1f} per row tile; hart 1 {c1:.1f} per row tile")
    print(f"cycle model: hart 0 {P['H_TILE']} per row tile + {P['E_OUT']} epilogue + {S}x{P['C_OP_str']} tensor "
          f"per output tile; hart 1 {model['hart1_per_row_tile_cycles_variant_b']:.0f} per row tile (variant b)")
    print(f"card median minion: {med_cycles:.0f} cycles, {med('ops'):.0f} ops, {med('tiles'):.0f} row tiles; "
          f"counted work {c['median_counted_work_instructions_hart0']:.0f} + {c['median_counted_work_instructions_hart1']:.0f}"
          f" instructions = {c['median_issue_occupancy_by_counted_work']:.3f} of its cycles")
    print(f"hart 1 with an intercept: {c1i:.1f} per row tile + {d1i:.0f} a launch (residuals "
          f"{', '.join(f'{r:.0f}' for r in res1i)}); occupancy {c['median_issue_occupancy_hart1_intercept_fit']:.3f}, "
          f"hart 1 per model cycle {c['hart1_ipc_vs_model_intercept_fit']:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
