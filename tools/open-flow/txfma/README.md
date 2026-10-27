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
| `setup.sh` | Fetches everything into `$SCRATCH`: oss-cad-suite (Yosys + yosys-slang + Verilator + Icarus), OpenROAD from the litex-hub conda channel, the ORFS `asap7` platform, ASAP7's CDL netlists, and core-et. Nothing is installed system-wide. **Every version is pinned** to the one the published run used (`OSS_REL`, `OPENROAD_PKG`, `ORFS_SHA`, `ASAP7_SHA`, `COREET_SHA` at the top of the file); override one to re-measure on a newer tool. |
| `synth.sh` | Elaborates `txfma_top` with yosys-slang and maps it onto ASAP7 RVT, TT corner. Writes three netlists: `keep` (every module boundary kept, so the census reads per block), `flat`, and `mixed` (flattened everywhere except the four multiplier blocks, which is the one the cell counts should be compared on — see trap 5). |
| `mktiles.sh` | **The stimulus.** Writes every operand file the bench runs, with the exact flags: the 21 Sep `randn`/`ones`/`zeros` patterns at `--seed 1 --iters-before 1000`, V3-HL's Hamming-ladder tiles (`make_hl.py`), and each rung converted with `--from-bin`. Nothing downstream is reproducible without it. |
| `census.py` | Cells, transistors, fins, flip-flops, latches, area and clock-pin capacitance, for the whole unit and for every block, from the Yosys JSON netlist plus ASAP7's own CDL and liberty. |
| `show_blocks.py` | Prints the block table from `census.py`'s JSON. |
| `pnr.tcl` | OpenROAD: floorplan, place, CTS, global route, per-net capacitance, then detailed route, OpenRCX extraction and SPEF. Detailed routing does not close in the 2022 OpenROAD this machine can install — POWER.md § blockers has the five variants tried and what they proved. |
| `tb_gate.sv`, `asap7_seq_behav.v`, `gatesim.sh` | the fma_toggle stimulus driven into the netlist (Verilator, zero delay), writing a SAIF, and optionally a recording of the unit's pins. |
| `power.py` | prices every extracted net at 1/2 C V^2 per toggle at 0.517 V, per block, with the clock tree's share, the capacitance coverage in farads, and (with `--cell-energies`) the cells' own internal energy from ASAP7's liberty. |
| `tb_timed.v`, `gatesim_sdf.sh`, `vcd_toggles.py` | the timed pass: replays that recording under Icarus with the post-CTS SDF and counts every edge. Its SDF half aborts in Icarus 14 — see POWER.md. |

```bash
export SCRATCH=$HOME/scratch-open-flow          # anywhere outside a synced folder
export LAB=$PWD                                 # this checkout of et-soc1-prototyping
bash tools/open-flow/txfma/setup.sh
bash tools/open-flow/txfma/synth.sh             # ~3 minutes, three netlists
bash tools/open-flow/txfma/mktiles.sh           # the operand files, with their seeds

for tag in keep flat mixed; do
  python3 tools/open-flow/txfma/census.py \
      --json  $SCRATCH/work/syn/txfma_$tag.json \
      --cdl   $SCRATCH/asap7cells/CDL/LVS/asap7sc7p5t_28_R.cdl \
      --lib   $SCRATCH/work/lib \
      --out   census_$tag.json
done
python3 tools/open-flow/txfma/show_blocks.py census_mixed.json 3
openroad -no_init -exit tools/open-flow/txfma/pnr.tcl

for p in randn ones zeros lq_h0 lq_h8 lb_h0 lb_h8; do
  TB=tools/open-flow/txfma/tb_gate.sv TILES=$SCRATCH/work/tiles/$p.hex TAG=$p \
      bash tools/open-flow/txfma/gatesim.sh
  python3 tools/open-flow/txfma/power.py \
      --saif $SCRATCH/work/sim/out/${p}_o1.saif --saif-base $SCRATCH/work/sim/out/${p}_o0.saif \
      --netcap $SCRATCH/work/pnr/net_cap_globalroute.txt --muladds 512 \
      --cell-energies docs/reports/data/2026-10-26-asap7-cell-energies/asap7-cell-energies.json \
      --out power_gr_$p.json
done
```

Results and the comparison with the tape-out flow's numbers:
[`docs/reports/data/2026-10-26-open-netlist/`](../../../docs/reports/data/2026-10-26-open-netlist/README.md).

## Six things that cost time, so you do not pay them again

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
5. **…but a fully kept hierarchy inflates every count, so do not compare one against a normal
   flow's.** Keeping all 182 boundaries blocks constant propagation and resource sharing across
   each of them: the same design is 19,822 cells kept against 16,087 flattened, 19% apart, and
   118 flip-flops survive that flattening prunes. That is why `synth.sh` writes a third netlist,
   `mixed`, which marks only the four multiplier blocks `keep_hierarchy` and flattens the rest —
   the per-block numbers in the results directory come from that one.
6. **Pin the tools, not "latest".** `Verilator` alone moves a toggle count by 3× between 5.042 and
   5.052 (Q126(b)), the litex-hub conda `openroad` is a 2022 build whose TritonRoute behaves
   differently from a current one, and a `--depth 1` clone of a moving branch cannot be checked
   out at the sha a report quotes. `setup.sh` now fetches each pinned sha by name instead.
