# open-flow/glitch: switching with glitches, from the netlist's own liberty delays

Q138(g), 2 November 2026. Q133(a)'s int8 netlists ([`../tima/`](../tima/README.md)) were counted at zero delay, so a net moved at
most once a cycle. This directory counts every transition a net makes while a cycle settles: an event-driven simulation of a
gate-level netlist with each cell's delays read from the liberty files it was mapped to, inertial delays, driven by the stimulus the
whole-`vpu_top` bench ([`rtl-sim/tima_gate`](../../../rtl-sim/tima_gate/README.md)) gives each `tima_top` instance.
Results: [`docs/reports/data/2026-11-02-q138g-int8-glitch/`](../../../docs/reports/data/2026-11-02-q138g-int8-glitch/README.md);
method: its [METHOD.md](../../../docs/reports/data/2026-11-02-q138g-int8-glitch/METHOD.md).

| Script | What it does |
| --- | --- |
| `mkvcd.py` | one tile through one bench binary at one launch point, as `run_kinds.py`'s VCD run does it (C from `accum.c`, one warm op, one dumped op) |
| `vcdread.py` | the 16 `tima_top` instances out of a bench VCD: every port and net, as the zero-delay bench settled them |
| `batch_vcd.py` | `mkvcd.py` + `vcdread.py` over tiles, netlists and launch points; each VCD is read, saved as a gzipped pickle and deleted |
| `annotate.py` | a netlist plus its liberty files -> a model: truth tables, loads, slews, and per-arc, per-state rise and fall delays |
| `esim.py` | the event-driven simulator, inertial delays (VHDL's rule; `verilog_style=True` for Verilog's) |
| `run_tile.py` | one tile's 16 instances through `esim.py`, with the bench's own zero-delay count and a settled-value check against the VCD at every edge |
| `batch_sim.py` | `run_tile.py` over tiles, netlists and points, and the arms (`--extra`, `--model-suffix`) |
| `analyze_glitch.py` | per item (minus its own zero, per flip): zero-delay, timed and excess counts; prices in Q136(a)'s frozen frame; the card's intervals; the glitch-weight scan |
| `refit_k.py` | Q133(a)'s M2 on E78's int8 kinds with zero-delay and glitch-aware counts |
| `summarize.py` | `tables.md` and `summary.json` |
| `validate.py` | small circuits with known glitch counts, against first principles and Icarus Verilog |
| `xcheck_iverilog.py` | one whole netlist instance with the bench's stimulus, this simulator against Icarus Verilog net by net (`--udp`: each cell a user-defined primitive) |

```bash
# Q133(a)'s bench binaries and liberty files (tools/open-flow/tima/README.md, rtl-sim/tima_gate/README.md)
export Q138G_BUILD=<bench build dir: obj_<arm>/Vtb, accum>  Q138G_WORK=<work dir>  LIBDIR=<dir of the five .lib files>
N=docs/reports/data/2026-11-01-q133a-int8-gate-level/netlists
G=tools/open-flow/glitch
L=$(for l in $LIBDIR/*.lib; do printf -- '--lib %s ' $l; done)
for a in booth_tree booth booth_swap plain; do
  python3 $G/annotate.py --netlist $N/tima_${a}_staged.v.gz $L --out $Q138G_WORK/models/$a.pkl
done
python3 $G/batch_vcd.py --points 157232,471698,786163 --out $Q138G_WORK/stim --jobs 6
python3 $G/batch_vcd.py --points 471698 --out $Q138G_WORK/stim --tiles-dir tools/claims-v3/kinds/tiles/int8 --jobs 6
python3 $G/batch_sim.py --points 157232,471698,786163 --tag primary --jobs 6
python3 $G/analyze_glitch.py --sims $Q138G_WORK/sims/primary --point 157232,471698,786163 --out glitch_3pt.json
python3 $G/validate.py <out dir> $LIBDIR <path to iverilog>
```
