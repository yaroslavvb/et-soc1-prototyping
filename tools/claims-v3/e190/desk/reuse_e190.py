#!/usr/bin/env python3
"""E190 (Q169) desk: the 8,192^3 GEMM's own reuse, per L2-sized block, and where each missing line is served, by E136's desk model UNCHANGED
(tools/claims-v3/e136/desk/reuse_e136.py, imported: shire_ops, l2_model, l3_model). No card. Standard library only.

    python3 -I -B tools/claims-v3/e190/desk/reuse_e190.py > tools/claims-v3/e190/desk/reuse_e190.txt     (writes reuse_e190.json beside it)

THE SHAPES. An 8,192 x 8,192 x 8,192 GEMM in each format is rgm136's SP_GEMM_LARGE with MB = 8 and NB = 16 blocks (a block is 1,024 x 512 of C),
and K = 8,192 elements in KB blocks of 32 k tiles: a tile row holds 16 fp32, 32 fp16 or 64 int8 elements, so KB = 16 (fp32), 8 (fp16), 4 (int8):
  fp32 gemmL8x16x16, fp16 gemmL8x16x8, int8 gemmL8x16x4.
E136's g4k (gemmL4x8x8) ran the SAME arm in all three formats, so its fp16 and int8 were 4,096 x 4,096 x 8,192 and x 16,384. E190's fp16 has g4k's
per-block bytes (KB = 8) on a twice larger C; its int8 half of them (KB = 4); its fp32 twice (KB = 16). So the reuse changes by format here, which it
did not in E136.

THE TIE. g4k is re-run through the same functions first: its L2 and L3 numbers must equal E136's committed reuse_e136.json to the last digit, or
this script stops (the model is the one E136 froze).

THE OWN ARITHMETIC (printed, no model): per C block the chip streams the A row panel (64 row tiles x KB x 32 k tiles x 1 KB) and the B column panel
(32 column tiles x KB x 32 x 1 KB), and stores 2 MB of C. A row panel's next use is in the next C block of its row (after the rest of A's panel, B's
panel and C); a B column panel's next use is the minion's second row tile r = 1 (after B's panel and half of A's), then the next mb (a whole row of
C blocks later). Against the 32 MB L3 (E107 measured 26 MB served, C included, and 40 MB not), those distances say which panel can still be there.
DRAM bytes a GEMM at the two ends: nothing reused from the L3 (each C block reads its whole A and B panels, B twice) and the model's own shares.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E136_DESK = os.path.normpath(os.path.join(HERE, "..", "..", "e136", "desk"))
sys.path.insert(0, E136_DESK)
import reuse_e136 as R  # noqa: E402  (E136's desk model, unchanged)

SHAPES = {"g4k": (4, 8, 8), "fp32": (8, 16, 16), "fp16": (8, 16, 8), "int8": (8, 16, 4)}
ELEM = {"fp32": 4, "fp16": 2, "int8": 1}
CAPS = (32, 28, 24)
MiB = 2 ** 20


def arithmetic(MB, NB, KB):
    a_panel = 64 * KB * 32 * 1024            # bytes of one A row panel (one C block's A), chip-wide
    b_panel = 32 * KB * 32 * 1024            # one B column panel
    c_blk = 64 * 32 * 1024
    steps = MB * NB * 2 * KB * 32            # op steps a GEMM (= ops per minion)
    nothing = MB * NB * (a_panel + 2 * b_panel) + MB * NB * c_blk     # A once and B twice per C block, C written once
    return {"A_panel_MB": a_panel / MiB, "B_panel_MB": b_panel / MiB, "C_block_MB": c_blk / MiB,
            "A_reuse_distance_MB": (a_panel + b_panel + c_blk) / MiB,              # A(mb) in block (mb, nb) -> (mb, nb + 1)
            "B_reuse_distance_r_MB": (b_panel + a_panel / 2 + c_blk / 2) / MiB,    # B(nb) at r = 0 -> r = 1
            "B_reuse_distance_mb_MB": NB * (a_panel + b_panel + c_blk) / MiB,      # B(nb) at mb -> mb + 1
            "ops_per_minion": steps, "unique_bytes_per_op_step": (32 + 32) * 1024,
            "dram_bytes_nothing_reused_GB": nothing / 1e9,
            "footprint_MB": {"A": MB * KB * R.ABLK / MiB, "B": KB * NB * R.BBLK / MiB, "C": MB * NB * R.CBLK / MiB}}


def dram_bytes_model(MB, NB, KB, a_in, b_in):
    """the model's own shares: the tile requests that find their tile in the L3 are not DRAM reads; per shire-op 64 A and 128 B line requests are
    4 and 8 shires' requests of 32 + 32 distinct tiles, so a fresh share f of A's requests reads A's distinct tiles at f (likewise B)."""
    steps = MB * NB * 2 * KB * 32
    per_step = 32 * 1024 * (1 - a_in) + 32 * 1024 * (1 - b_in)
    return (steps * per_step + MB * NB * R.CBLK) / 1e9


def main():
    committed = json.load(open(os.path.join(E136_DESK, "reuse_e136.json")))["gemms"]["g4k"]
    out = {"what": "E190 desk: the 8,192^3 GEMM's reuse per L2-sized block and where its missing lines are served (E136's models, unchanged; "
                   "models and arithmetic, not measurements)", "model": "tools/claims-v3/e136/desk/reuse_e136.py (imported)", "shapes": {}}
    print(__doc__.split("\n\n")[0])
    for name, (MB, NB, KB) in SHAPES.items():
        l2 = R.l2_model(("large", MB, NB, KB))
        l3 = {f"{cap}MB": R.l3_model(("large", MB, NB, KB), cap * 1024) for cap in CAPS}
        ar = arithmetic(MB, NB, KB)
        lines = {}
        for cap, v in l3.items():
            nl = 64.0 * v["A_in_L3"] + 128.0 * v["B_in_L3"]
            lines[cap] = {"n_L3": round(nl, 3), "n_fresh": round(192.0 - nl, 3),
                          "dram_GB_per_gemm": round(dram_bytes_model(MB, NB, KB, v["A_in_L3"], v["B_in_L3"]), 3)}
        rec = {"blocks": [MB, NB, KB], "arm": f"gemmL{MB}x{NB}x{KB}", "L2": l2, "L3": l3, "lines_per_shire_op": lines, "arithmetic": ar}
        if name == "g4k":
            tie = (l2 == committed["L2"] and all(l3[c] == committed["L3"][c] for c in committed["L3"]))
            rec["tie_with_e136_committed"] = tie
            if not tie:
                print("TIE FAILED: g4k does not reproduce reuse_e136.json", l2, l3, committed["L2"], committed["L3"])
                sys.exit(3)
        out["shapes"][name] = rec
        el = "x".join(str(x) for x in (MB * 1024, NB * 512, KB * 512 * 4 // ELEM.get(name, 4)))
        print(f"\n{name}: {rec['arm']}; M x N x K {el}; ops per minion a GEMM {ar['ops_per_minion']}; footprint A {ar['footprint_MB']['A']:.0f} MB, "
              f"B {ar['footprint_MB']['B']:.0f} MB, C {ar['footprint_MB']['C']:.0f} MB")
        print(f"  per C block: A panel {ar['A_panel_MB']:.0f} MB, B panel {ar['B_panel_MB']:.0f} MB, C {ar['C_block_MB']:.0f} MB; reuse distance of A "
              f"(next C block) {ar['A_reuse_distance_MB']:.0f} MB, of B (second row tile) {ar['B_reuse_distance_r_MB']:.0f} MB, of B (next mb) "
              f"{ar['B_reuse_distance_mb_MB']:.0f} MB; the L3 is 32 MB (E107: 26 MB served, 40 MB not)")
        print(f"  L2 (one shire, model): missing lines per op, first pass {l2['first_pass_missing_lines_per_op']}, steady "
              f"{l2['steady_missing_lines_per_op']} of {l2['lines_per_op']}")
        for cap in l3:
            v, w = l3[cap], lines[cap]
            print(f"  L3 at {cap} (model): A requests found {v['A_in_L3']:.4f}, B {v['B_in_L3']:.4f}; lines a shire-op from the L3 {w['n_L3']:.1f}, "
                  f"fresh {w['n_fresh']:.1f}; DRAM {w['dram_GB_per_gemm']:.2f} GB a GEMM")
        print(f"  DRAM if nothing were reused from the L3: {ar['dram_bytes_nothing_reused_GB']:.2f} GB a GEMM "
              f"({ar['unique_bytes_per_op_step'] // 1024} KB of distinct A and B tiles an op step, B read twice a C block)")
    json.dump(out, open(os.path.join(HERE, "reuse_e190.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
