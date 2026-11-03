# Q138(g): how the glitch-aware counts were made

*The method behind [README.md](README.md). Mon 2 Nov 2026 (week 45), desk work on the Intel, `nice -n 10`, at most six processes.
Code: [`tools/open-flow/glitch/`](../../../../tools/open-flow/glitch/README.md).*

## 1. The stimulus: the bench's own, unit by unit

Each of E130's 26 tiles (the 13 B tiles E138 read again are among them) went through Q133(a)'s bench binaries
(`rtl-sim/tima_gate`, one binary per netlist, built in Q133(a) and unchanged), at a launch point, exactly as `run_kinds.py`'s VCD
run does it: `accum.c` computes C at that point, one warm op, one dumped op ([`mkvcd.py`](../../../../tools/open-flow/glitch/mkvcd.py)).
From each VCD, [`vcdread.py`](../../../../tools/open-flow/glitch/vcdread.py) keeps the 16 `tima_top` instances
(`VPU_LANES[0..7].lane.LANE_TIMA[0..1].lane_tima.tima`): every port and every internal net, as the bench's zero-delay simulation
settled them at each timestamp. Every port change happens at a rising edge of the bench clock; the unit's clock is the lane's
gated `tima_clock`, read from the VCD.

## 2. Delays: the flow's own liberty files

[`annotate.py`](../../../../tools/open-flow/glitch/annotate.py) reads the same five liberty files the netlists were mapped to (the
open flow's 7 nm library, RVT, typical corner, NLDM tables) and, for every cell instance:
- its truth table from the liberty `function`;
- its output load: the fanout pins' liberty capacitance plus a wire load of 0.2 fF + 0.1 fF per fanout pin (there is no placement;
  an output port gets one flip-flop D pin and the same wire);
- every net's transition time, propagated in topological order from the flip-flops (CLK->Q at a 10 ps clock edge) and the input
  ports (the flip-flops' mean output transition);
- for every input pin, and every state of the cell's inputs after that pin moves, the delay to a rising and to a falling output,
  read from the timing group whose `when` holds in that state (`cell_rise`/`cell_fall`, bilinear in input transition and load,
  linear outside the table); the flip-flop's CLK->Q rise and fall.

Delays per arc: 9.0–192 ps (median 29.7 ps) in `booth_tree`; CLK->Q 66–110 ps. The longest path from a flip-flop or an input to a
flip-flop D is 1,212–1,510 ps over the four netlists, inside the 1,667 ps period at 600 MHz. No placement, no wires' own resistance,
no clock tree: the clock reaches every flip-flop at its edge.

## 3. The simulation: events, inertial delays

[`esim.py`](../../../../tools/open-flow/glitch/esim.py) is an event-driven simulator of one netlist. Per cell output, at most one
transaction is pending. When an input pin moves at time t, the cell is evaluated on its present inputs, giving v:
- v equals the projected value (the pending one, or the present output): nothing;
- a transaction is pending and v is the present output: it is cancelled. The pulse is swallowed: the inertial delay, with the
  rejection window equal to the arc's own delay;
- otherwise: v is scheduled at t + the delay of that pin, in that state, for that edge.

This is VHDL's inertial rule (the first cause of a transition keeps its time). The arm `vstyle` uses Verilog's continuous-assignment
rule instead (a re-evaluation that gives the pending value replaces it by one at t + d). Flip-flops sample D at the unit clock's
rising edge and move Q at edge + CLK->Q. Input ports move at edge + t_in, t_in = the smallest CLK->Q (66.0 ps; transport); the arm
`skew150` adds a random 0–150 ps to each input bit. The bench timestamps are mapped to a 600 MHz clock (833.3 ps a half period).

**What is counted.** Every matured transaction is one toggle of its net (a full swing). The window starts at the bench's settled
sample 1 (`settle_count --skip 1`) and ends when the last activity settles. The zero-delay count of the same window is computed the
bench's way, from the bench VCD's own settled samples: per net, bit changes between consecutive even-timestamp samples. Summed over
the unit's internal and output nets it equals `settle_count`'s `ids` count for the unit (`hb1`, `booth_tree`, middle point: 26,548
with the ports, the bench's committed 26,548), and per flip it reproduces Q136(a)'s unit `nets_map` within about 1 net on the B
list and 3 on the A list. Ports move once per change in both counts, so the **excess** (timed minus zero delay) is the glitches.

**Checks in every run.** Before each rising edge the simulator's settled value of every net of every instance is compared with the
bench VCD's: 0 mismatches in all runs that carried the check (the primary and the kinds; the arms ran without it). A flip-flop whose
D still had a transaction pending at an edge is counted as late: 0 in every checked run.

## 4. From counts to prices

For an item (a tile one bit away from its own zero), per designed flip: (item − zero) / flips per op (1,024 on the B list, 8,192 on
the A list), summed over the 16 units. The glitch-aware price in Q136(a)'s frozen frame is the frozen whole-VPU `nets_map` per flip
at the same launch point plus the unit's excess per flip, times the netlist's frozen k (Q136(a) `inputs.k_fJ_per_net_toggle`).
Shapes (odd ÷ even, the A sign's held-operand ratio, word 2 ÷ word 1) carry no k. **Glitch weight w**: counts = zero delay + w ×
excess, for w from 0 (zero delay) through 1 (every inertial glitch a full toggle) to 2, standing for partial swings, wire filtering
and delay error that the model does not have.

**The refit** ([`refit_k.py`](../../../../tools/open-flow/glitch/refit_k.py)): Q133(a)'s M2, D = rate × (k × VPU nets + a × clocked
register bits), each over int8's zeros, on E78's 15 int8 kinds (aifoundry3, 600 MHz, board watts), with Q133(a)'s committed VPU
`nets_hier` at the middle launch point (zero delay) and the same plus the unit's excess from this simulation of the same stimulus
(glitch-aware). Clocked bits are the RTL run's (Q132(b)), as in Q133(a). Leave-one-kind-out is the out-of-sample error.

## 5. Validation

[`validate.py`](../../../../tools/open-flow/glitch/validate.py) builds small circuits from the same cells, annotates them the same
way, and compares the simulator's transition counts with first-principles expectations and with Icarus Verilog
([`validate.json`](validate.json)); [`xcheck_iverilog.py`](../../../../tools/open-flow/glitch/xcheck_iverilog.py) runs a whole
netlist instance with the bench's stimulus through both ([`xcheck/`](xcheck/)). Icarus can express one delay per cell and edge, so
both run the pin-independent version of the model there (each cell's worst arc per edge); the primary runs use the per-arc,
per-state delays, through the same event code.
