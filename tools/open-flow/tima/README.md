# open-flow/tima: the int8 multiply-add as gates, with the open flow's own recipe

Q133(a), 1 November 2026. core-et's `tima_top` is the int8 multiply-add (four 9×9 signed products, their sum, the 32-bit add of C; two a vector
lane). Its RTL writes the products as `*` and the sums as `+`, so its gates are the synthesis tool's choice. This directory maps it onto ASAP7
with [`../txfma/synth.sh`](../txfma/synth.sh)'s recipe (the same liberty files, dont-use list, abc period, tie cells), in each multiplier
architecture the open tools offer, and prepares the netlists for the RTL bench ([`rtl-sim/tima_gate`](../../../rtl-sim/tima_gate/)).
Results: [`docs/reports/data/2026-11-01-q133a-int8-gate-level/`](../../../docs/reports/data/2026-11-01-q133a-int8-gate-level/README.md).

| Script | What it does |
| --- | --- |
| `setup_darwin.sh` | `../txfma/setup.sh` for a Mac with an Intel CPU: the same pins, with oss-cad-suite's **darwin-x64** build of the same release (`OSS_REL`). OpenROAD is not fetched: its pinned build is a linux-64 package, and a zero-delay toggle count needs no placement or routing. |
| `synth_tima.sh` | `tima_top` in four architectures: `plain` (`synth -flatten`, txfma/synth.sh's flat recipe exactly), `booth` (`-booth`, radix-4 Booth products), `booth_tree` (`-booth -arith_tree`, Booth products and carry-save trees for the sums), `booth_swap` (`booth_tree` on a copy of `tima_top.v` whose product reads `in2 * in1`, the same function, so the recoder moves to the other operand). |
| `booth_operand.py` | which operand yosys's booth pass recodes: the second of `x * y`, so B (TenB) as the RTL is written, A in `booth_swap`. |
| `synth_txfma_flat.sh` | the float unit, `txfma_top`, as `../txfma/synth.sh`'s `flat` netlist and nothing else, for counting all three formats at gate level in one bench. |
| `liberty_models.py` | simulation models of the liberty cells, one continuous assignment per output, written from the liberty files' own `function`, `ff` and `latch` groups, with tracing and coverage off inside them. |
| `netlist_stages.py` | rewrites a yosys netlist without changing a connection: aliases resolved to one scalar name per net, each internal net named for its stage from the netlist's own cones (the RTL bench's stage convention for this unit), every wire marked public. `--generic` does the same for any netlist with no stage split, naming the gated-clock nets `clk_n*`. |

```bash
export SCRATCH=<a directory outside any synced folder>
bash tools/open-flow/tima/setup_darwin.sh            # 509 MB download, a few minutes
bash tools/open-flow/tima/synth_tima.sh              # four netlists, under a minute each
bash tools/open-flow/tima/synth_txfma_flat.sh        # the float unit, a few minutes
L=$(for l in $SCRATCH/work/lib/*.lib; do printf -- '--lib %s ' $l; done)
python3 tools/open-flow/tima/liberty_models.py $L --out $SCRATCH/work/tima/sim/asap7_cells.v
for a in plain booth booth_tree booth_swap; do
  python3 tools/open-flow/tima/netlist_stages.py --netlist $SCRATCH/work/tima/syn/tima_$a.v $L \
      --out $SCRATCH/work/tima/sim/tima_${a}_staged.v --json $SCRATCH/work/tima/sim/stages_$a.json
done
python3 tools/open-flow/tima/netlist_stages.py --generic --netlist $SCRATCH/work/syn/txfma_flat.v $L \
    --out $SCRATCH/work/tima/sim/txfma_flat_staged.v --json $SCRATCH/work/tima/sim/stages_txfma_flat.json
```

**Two things to know.**
1. **The same Yosys on another platform does not give the same netlist.** The darwin-x64 build of release 2026-10-26 carries Yosys
   `33177a407`, the sha of the published Linux run, and maps `txfma_top` to 16,063 cells against the published 16,087 (2,127.4 against
   2,124.9 µm²), with the same 1,953 flip-flops and 13 latches. abc's mapping differs in detail between platform builds, so a cell or toggle
   count from here can differ by that much from a Linux run.
2. **The stage names are labels, not connectivity.** `netlist_stages.py` assigns a stage from where a net sits between the unit's registers
   (operand: into the F2 registers; multiplier: F2 registers to the F3 product register; adder: after it, to the output). The cells and their
   connections are byte-for-byte what yosys wrote; `sha256.txt` in the data directory pins both versions.
