# open-flow/txfma — the multiply-add as gates, with tools anyone can re-run

Q126, 26 October 2026. The gate-level numbers this project has quoted so far (cells, transistors,
flip-flops clocked per multiply-add, glitches) came from a netlist synthesized with a tape-out flow
that is not public, so no reader could check them. This directory builds the **same RTL** with
**open tools and an open 7 nm library**, so every number below can be reproduced from a clean
machine with the commands in this file.

The unit is `txfma_top` — core-et's seven-stage fused multiply-add, one vector lane, the module
`rtl-sim/fma_toggle` already simulates eight copies of.

## Licences

| Piece | Licence |
| --- | --- |
| core-et RTL (`openhwfoundation/core-et`, branch `erbium`) | Apache-2.0 |
| ASAP7 PDK and standard cells (`The-OpenROAD-Project/asap7`, `asap7sc7p5t_28`) | BSD-3-Clause |
| OpenROAD-flow-scripts' `asap7` platform (LEF, liberty, RC, rcx rules) | BSD-3-Clause |
| Yosys, yosys-slang, Verilator, Icarus, OpenROAD | ISC / MIT / LGPL / BSD-3 |

ASAP7 is a **predictive** 7 nm library from ASU, not the process the ET-SoC-1 was built in. It is a
stand-in that is legal to publish, not a copy of the real thing. Every number here is "what an open
7 nm library makes of this RTL", and that is the point: it can be checked.

## Scripts

| Script | What it does |
| --- | --- |
| `setup.sh` | Fetches everything into `$SCRATCH`: oss-cad-suite (Yosys + yosys-slang + Verilator + Icarus), OpenROAD from the litex-hub conda channel, the ORFS `asap7` platform, ASAP7's CDL netlists, and core-et. Nothing is installed system-wide. |
| `synth.sh` | Elaborates `txfma_top` with yosys-slang and maps it onto ASAP7 RVT, TT corner. Writes a hierarchical netlist (module boundaries kept, so the census can be read per block) and a flat one. |
| `census.py` | Cells, transistors, fins, flip-flops, latches, area and clock-pin capacitance, for the whole unit and for every block, from the Yosys JSON netlist plus ASAP7's own CDL and liberty. |
| `show_blocks.py` | Prints the block table from `census.py`'s JSON. |
| `pnr.tcl` | OpenROAD: floorplan, place, CTS, route, OpenRCX extraction, SPEF. |

```bash
export SCRATCH=$HOME/scratch-open-flow          # anywhere outside a synced folder
bash tools/open-flow/txfma/setup.sh
bash tools/open-flow/txfma/synth.sh             # ~1 minute
python3 tools/open-flow/txfma/census.py \
    --json  $SCRATCH/work/syn/txfma_keep.json \
    --cdl   $SCRATCH/asap7cells/CDL/LVS/asap7sc7p5t_28_R.cdl \
    --lib   $SCRATCH/work/lib \
    --out   census_keep.json
python3 tools/open-flow/txfma/show_blocks.py census_keep.json 3
openroad -no_init -exit tools/open-flow/txfma/pnr.tcl
```

Results and the comparison with the tape-out flow's numbers:
[`docs/reports/data/2026-10-26-open-netlist/`](../../../docs/reports/data/2026-10-26-open-netlist/README.md).

## Four things that cost time, so you do not pay them again

1. **core-et's RTL is not strict SystemVerilog.** Files under `txfma_7s` use the Verilog-1995
   single-value parameter form (`txfma_csa #64 inst(...)`), and they rely on one compilation unit
   for the types in `rtl/inc/*.vh` — they do not include `soc.vh` themselves. So slang needs
   `--single-unit --compat vcs`, every file listed explicitly with `txfma_top.v` first, and `-I
   rtl/inc -I rtl`. A `-y` library-directory search fails: slang compiles those files as separate
   units, where the types are not visible.
2. **Yosys reads one `library()` group per `-liberty` file.** Concatenating ASAP7's five NLDM files
   into one silently hides everything after the first, and `dfflibmap` then dies with "D flip-flops
   are not supported". Pass each file with its own `-liberty`.
3. **The ORFS `asap7` platform is already at 1×.** Its tech LEF is `asap7_tech_1x_*.lef` and its
   cell LEFs are `*_1x_*.lef`: `INVx1_ASAP7_75t_R` is `SIZE 0.162 BY 0.27`, and the liberty says
   `area : 0.04374`, the product of the two. So **do not apply ASAP7's 4× drawing scale** to
   anything taken from this platform, and do not scale `setRC.tcl`'s per-micron RC either. The 4×
   scale applies to ASAP7's own GDS and to the un-suffixed LEFs in the upstream PDK.
4. **Keep hierarchy if you want a per-block answer.** After `synth -flatten`, abc renames every
   instance to `_13280_` and the block each cell came from is gone. yosys-slang inlines the
   hierarchy by default; `--keep-hierarchy` (or `--best-effort-hierarchy`) is what preserves it,
   and `hierarchy -check` alone will not bring it back.
