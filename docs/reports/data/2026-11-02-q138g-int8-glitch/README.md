# Q138(g): int8's single bits with glitches. A timing-aware count of Q133(a)'s four netlists on E130's and E138's flips

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 12, "int8 at gate level"** (the list at `724c17d3dc0b`). The open points it names: "whether the chip Booth-recodes B, as a registered verdict … and why its even bits cost more than any netlist says; glitches, since the counts are at zero delay". The list's next step (6): "Item 12's structural verdict (more B blocks, or a glitch-aware count)". This is the glitch-aware count; E145 is the more-B-blocks half.*

*Mon 2 Nov 2026 (week 45), Q138, desk lane `desk-q138g-glitch`, on the Intel (`nice -n 10`, at most six processes, on a machine whose load other lanes' work held at 25–72 on 16 CPUs), 18:56 to 20:30 PST. **Desk only: no card was opened, no device command was sent, no box was used, and nothing was measured in watts here.** Every watt and every card interval below is a committed experiment's (E78, E130, E138), named where it is used. The netlists are Q133(a)'s four, unchanged ([`netlists/`](../2026-11-01-q133a-int8-gate-level/netlists/)); the stimulus is Q133(a)'s bench, unchanged; the zero-delay predictions are Q136(a)'s, frozen before E130. How: [METHOD.md](METHOD.md). Code: [`tools/open-flow/glitch/`](../../../../tools/open-flow/glitch/README.md). Every number is in the JSON files here; [`tables.md`](tables.md) is generated from them.*

**In plain words.** While a clock cycle settles, a gate whose inputs arrive at different times can flip more than once; a
zero-delay simulation counts at most one flip. On the card, flipping an odd bit of int8's B operand costs 1.91× an even bit; the
zero-delay netlists say 4.3× (the two that Booth-recode B) or 1.05–1.09× (the two that do not). Counted with the netlists' own cell
delays, **glitches make the Booth-on-B netlists' odd B bits three times dearer and their even bits about 1.5 times, so their ratio
doubles to 9.3–9.5×; the others stay at 0.99–1.12×. No netlist reaches the card's interval, whatever fraction of a full toggle a
glitch is taken to cost.** On the A side glitches leave the odd/even pattern where zero delay had it and lift the A sign bit's
dense-B step, which zero delay put below the card, to the card's level or past it. And on E78's fifteen int8 kinds, glitch-aware
counts predict the card's watts worse than zero-delay counts in every netlist. So glitches, in these netlists, explain neither the
card's B pattern nor its kind-level power: **the model keeps zero-delay gate counts and E138's measured price per B bit.**

## Results

**1. With glitches, no netlist's B odd ÷ even lands in the card's interval, and Booth on B moves further from it.**
B's odd bits (1, 3, 5) over its even bits (0, 2, 4), fJ per flipped bit, item minus its own zero, whole VPU, the middle launch
point ([`glitch_mid.json`](glitch_mid.json) › `arms.<netlist>.zero_delay_fJ` and `glitch_fJ`; the card: E138
[`scored.json`](../2026-11-02-e138-int8-b-rail/scored.json) › `primary.B_odd_over_even`):

| netlist (group) | zero delay (Q136(a)'s frozen numbers) | **with glitches** | the card, E138's rail |
|---|---:|---:|---|
| `booth_tree` (Booth on B, carry-save sums) | 4.38 | **9.32** | **1.91 [1.71, 2.16]** |
| `booth` (Booth on B) | 4.28 | **9.51** | |
| `booth_swap` (Booth on A) | 1.05 | **0.99** | |
| `plain` (no recoder) | 1.07 | **1.12** | |

**No glitch weight helps.** If a glitch costs a fraction w of a full toggle (partial swings, filtering by wires, delay error),
counts = zero delay + w × excess. Booth on B's ratio rises monotonically with w, from 4.3 (w = 0) through 7.3–7.5 (w = 0.5), 9.3–9.5
(w = 1) and 11.8–12.0 (w = 2) toward 18.8–19.1, its glitches' own ratio; `plain`'s stays between 1.07 and 1.22, `booth_swap`'s
between 0.67 and 1.05 (`glitch_weight_scan`). The card's [1.71, 2.16] lies between the two groups at every w ≥ 0. E130's rail ratio,
1.79 [1.68, 1.92], is no help either; only its board ratio, 2.41 [1.26, 38.2], holds Booth on B's 4.3 and 9.3 alike.

**2. The glitches follow the recoder, so they amplify its signature rather than filling in the even bits.** Per flipped bit, from
the middle launch point (`glitch_mid.json` › `arms.<netlist>.items.<tile>`; every bit of the excess is in the multiplier stage,
`by_stage`):

| B bit | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 (sign) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **the card**, board-equivalent fJ (E138's rail ÷ 0.81) | 22 | 69 | 39 | 81 | 58 | 76 | 58 | 102 |
| `booth_tree`, zero delay, fJ | 10 | 90 | 20 | 79 | 24 | 65 | 20 | 127 |
| `booth_tree`, **with glitches**, fJ | 12 | **270** | 35 | **257** | 33 | **225** | 54 | 311 |
| `booth_tree`, the unit's toggles, with ÷ without glitches | 1.33 | 3.00 | 1.80 | 3.30 | 1.40 | 3.50 | 2.71 | 2.44 |
| `plain`, zero delay → with glitches, fJ | 10 → 13 | 8 → 13 | 11 → 16 | 13 → 22 | 12 → 20 | 14 → 20 | 13 → 23 | 135 → 203 |

A radix-4 recoder reads overlapping three-bit windows of B, so an odd bit enters two Booth digits and an even bit one. With A = 1
held, flipping an odd bit changes two digits' select and negate lines, which reach their partial-product rows through recoder paths
of different lengths, and the two changed rows meet in the adder tree at different times, so the tree's XORs pulse: 3.0–3.5× the
zero-delay toggles (`booth`: 3.2–3.8×). An even bit changes one row and gains 1.3–1.9× (bit 6, 2.7–2.9×). **So the even bits do move
toward the card** (`booth_tree`'s bits 2 and 6 at 35 and 54 fJ against the card's 39 and 58), **but the odd bits overshoot it about
threefold** (225–270 fJ against 69–81), where at zero delay they matched it (65–90). No single glitch weight fits both. The two
netlists without a recoder on B gain 1.1–1.8× on every bit alike, so their B list stays flat. "Why the card's even bits cost about
2.2× what Booth on B predicts" (E138 §3) is not answered by glitches in these netlists.

**3. The A side: glitches leave the odd/even pattern as zero delay had it, and bring the sign bit's dense-B step up to the card's.**
(`glitch_mid.json` › `vs_card`, `glitch_weight_scan`; the card: E130 [`scored.json`](../2026-11-02-e130-int8-netlists/scored.json) ›
`primary.statistics`)

| netlist | A odd ÷ even: zero delay → glitches | A sign, B = 0x55 ÷ B = 1: zero delay → glitches | A sign, word 2 ÷ word 1 | all three A shapes inside, for w in |
|---|---|---|---|---|
| the card (E130, board) | **0.98 [0.92, 1.04]** | **1.43 [1.36, 1.51]** | **1.02 [0.98, 1.07]** | |
| `booth_tree` | 1.03 → 1.07 (inside for w ≤ 0.23) | 1.11 → 1.74 (inside for w 0.39–0.61) | 0.99 → 0.97 (inside for w ≤ 0.47) | never |
| `booth` | 1.00 → 1.01 (inside at every w) | 1.11 → 1.66 (inside for w 0.42–0.68) | 1.00 → 0.98 (inside for w ≤ 0.86) | 0.42–0.68 |
| `booth_swap` | 2.48 → 5.50 (never) | 0.96 → 1.03 (never) | 0.99 → 1.01 | never |
| `plain` | 1.11 → 1.17 (never) | 1.21 → **1.49** (inside for w 0.43–1.14) | 1.01 → 1.04 | never |

E130 excluded Booth on A by A's flat odd/even bits; with glitches `booth_swap`'s A alternation more than doubles (2.5× → 5.5×), so
that exclusion grows. On its registered primary E130 excluded the Booth-on-B netlists by the A sign step alone (their zero-delay step
was too small); with glitches the step grows past the card's. A dense B makes four partial-product rows carry A's sign extension, and
they meet in the tree at different times: the excess on `a1d_7` is +239 nets a flip in `booth_tree`, against +31 on `a1_7`. At a
partial glitch weight, 0.42–0.68, `booth`'s three A shapes all land inside the card's intervals; `plain`'s sign step lands inside at
full glitch cost, but its A odd/even bits never do (1.11 at zero delay already).

**No netlist has all four shapes inside the card's intervals at any glitch weight from 0 to 2**: B's ratio rules out every netlist
at every w (result 1), and the A side alone rules out `booth_tree`, `booth_swap` and `plain` at every w.

**4. Refitted with glitches, the price per toggle halves and the kinds' out-of-sample error grows in every netlist.** Q133(a)'s M2
on E78's 15 int8 kinds (aifoundry3, 600 MHz, board watts over int8's zeros), the same stimulus at the middle launch point
([`refit_k.json`](refit_k.json); the zero-delay rows reproduce Q133(a)'s fits):

| netlist | count | k, fJ per net toggle | a, fJ per clocked bit | rms, W | **leave-one-kind-out, W** |
|---|---|---:|---:|---:|---:|
| `booth_tree` | zero delay | 1.006 ± 0.045 | 2.38 ± 0.20 | 0.259 | **0.295** |
| | with glitches | 0.522 ± 0.040 | 2.60 ± 0.36 | 0.369 | **0.433** |
| `booth` | zero delay | 1.018 ± 0.046 | 2.38 ± 0.20 | 0.259 | **0.295** |
| | with glitches | 0.531 ± 0.040 | 2.60 ± 0.36 | 0.369 | **0.433** |
| `booth_swap` | zero delay | 0.856 ± 0.019 | 2.16 ± 0.07 | 0.238 | **0.257** |
| | with glitches | 0.361 ± 0.015 | 2.18 ± 0.12 | 0.334 | **0.371** |
| `plain` | zero delay | 0.832 ± 0.045 | 2.49 ± 0.27 | 0.373 | **0.420** |
| | with glitches | 0.310 ± 0.038 | 3.08 ± 0.65 | 0.627 | **0.733** |

(± a jackknife standard error over kinds.) Glitches multiply the unit's toggles by about 2.0 on the dense random kinds (`full`,
`gauss_q`, `sorted`, `smallint`) in the Booth-on-B netlists and by 2.4–2.7 in the other two, but by 1.3 on `ones` and 1.4–2.0 on
`sparse90` (`refit_k.json` › `kinds`), and the card's watts follow the zero-delay counts better. **Given its own coefficient, a glitch term takes a negative weight in all four**:
w = k_g ÷ k = −0.29, −0.30, −0.09 and −0.26 (w = 1 is 5.7–19 jackknife standard errors away), at leave-one-out 0.282, 0.278,
0.293 and 0.249 W. That term only takes up the dense random kinds' over-prediction (`full` −0.43 W in `booth_tree`), a per-stage
price correction, not a price for glitches. **At the refitted k the single bits stay off the card's** (`refit_k.json` ›
`single_bits_at_refit_k`): B odd − even +116 and +127 fJ for Booth on B against the card's +35.9 [+30.5, +41.4]; A bits 0–6 average
25–37 fJ in the three netlists that do not recode A, against the card's 79.8 [75.9, 83.8].

**5. The simulator is checked three ways.**
- **Against the bench, at every edge.** In every run of the primary and the kinds, the simulator's settled value of every net of
  every one of the 16 units was compared, just before each rising clock edge, with the bench's own zero-delay VCD: **0 mismatches**
  (104 single-bit runs and 64 kind runs, 304 unit clock edges each, 2,101–2,516 nets a unit). No flip-flop's D was still moving at an
  edge (late = 0 in every run): every path settles inside the 1,667 ps period. The zero-delay count of the same window, the bench's
  way, equals `settle_count`'s `ids` for the unit on every B tile and every zero tile (`hb1`, `booth_tree`: 26,548 and 26,548); on
  the A items it is higher by exactly 15,360 an op, the A operand port counted once per unit where the two units of a lane share one
  VCD identifier (a port, never in the excess). Per flip it gives Q136(a)'s unit `nets_map` at the same point within 1.2 nets on the B list and 5.3
  on the A list.
- **Against circuits whose glitch counts are known** ([`validate.json`](validate.json)). y = XOR(x, x delayed by k buffers): no
  pulse for k = 0, one (2 transitions) per toggle of x for k = 2, 4 and 8, and for k = 1 a pulse on one edge only, where the 22–24 ps
  chain outlasts the XOR's 16 ps arc but not its 29 ps one. y = AND(x, NOT^k(x)): the static hazard on a rising x is swallowed for
  k = 1 (an 11 ps pulse into a 22 ps gate) and passed for k = 5 (49 ps). An 8-bit ripple-carry adder with slow carries: sum bits
  1–7 pulse once on every edge of A (8 transitions each over two rises and two falls, where zero delay counts 0), bit 0 moves once
  per edge. **8 of 8 cases equal their expectation.**
- **Against Icarus Verilog, net by net.** Icarus can carry one delay per cell and edge, so here both run the pin-independent model
  (each cell's worst arc per edge). The small circuits, and the adder fed 60 random steps (2,361 transitions), agree on every net.
  Whole netlists with the bench's stimulus, each cell an Icarus user-defined primitive: **7 of 7 runs equal on every net**, all four
  netlists, from 2,404 transitions (`plain`, `hb1`) to 385,491 (`plain`, `a1d_7`) ([`xcheck/`](xcheck/)). With the cells written as
  sum-of-products continuous assignments instead, Icarus reads 1.4% fewer on `booth_tree`'s `b1_5` (13 nets differ): its zero-time
  transients inside an expression move a cell's pending transition, which a primitive does not. The primary runs use the per-arc,
  per-state delays through the same event code.

**6. The verdict holds under every variation tried.** Six arms each change one assumption (which netlists each covers is in the table). Across the primary and all of them, Booth on B's B odd ÷ even stays at 9.27–9.75, `booth_swap`'s at 0.99–1.02 and `plain`'s at 1.06–1.14, so no arm comes near the card's [1.71, 2.16]. A odd ÷ even stays at 1.00–1.09 for Booth on B, 5.42–5.59 for `booth_swap` and 1.17–1.20 for `plain`. The A sign ratio runs 1.62–1.76 (Booth on B), 0.98–1.03 (`booth_swap`) and 1.44–1.50 (`plain`). No conclusion of results 1–3 moves.

Each cell: B odd ÷ even / A odd ÷ even / A sign dense ÷ one, with glitches ([`tables.md`](tables.md), "Every arm at a glance"); the card: **1.91 [1.71, 2.16] / 0.98 [0.92, 1.04] / 1.43 [1.36, 1.51]**; zero delay: 4.38 / 1.03 / 1.11 (`booth_tree`), 4.28 / 1.00 / 1.11 (`booth`), 1.05 / 2.48 / 0.96 (`booth_swap`), 1.07 / 1.11 / 1.21 (`plain`).

| arm | `booth_tree` | `booth` | `booth_swap` | `plain` |
|---|---|---|---|---|
| primary (liberty delays, VHDL's inertial rule, middle launch point) (`glitch_mid.json`) | 9.32 / 1.07 / 1.74 | 9.51 / 1.01 / 1.66 | 0.99 / 5.50 / 1.03 | 1.12 / 1.17 / 1.49 |
| Verilog's inertial rule (`glitch_vstyle.json`) | 9.45 / 1.09 / 1.62 | 9.75 / 1.00 / 1.63 | 1.02 / 5.59 / 0.98 | 1.11 / 1.18 / 1.50 |
| input bits skewed 0–150 ps at random (`glitch_skew150.json`) | 9.27 / 1.06 / 1.71 | 9.44 / 1.01 / 1.67 | 1.01 / 5.42 / 1.03 | 1.14 / 1.17 / 1.47 |
| no wire load (pin capacitance only) (`glitch_wire0.json`) | 9.31 / 1.07 / 1.72 | — | — | — |
| three times the wire load (`glitch_wire3.json`) | 9.43 / 1.08 / 1.65 | — | — | — |
| each cell's delays × its own random factor in [0.8, 1.2] (`glitch_jitter20.json`) | 9.31 / 1.05 / 1.72 | — | — | 1.06 / 1.20 / 1.44 |
| the three launch points' mean (`glitch_3pt.json`) | 9.33 / 1.04 / 1.76 | — | — | — |

## What it does to predicting power and heat

**The term tested: int8's switching term at gate level, zero delay against glitch-aware counts**, in the two places the model uses
it, each scored out of sample:
- **B's per-flip term.** E138 left the model an empirical price per B bit position, which predicts a second session's bits 0–6 to
  3.2 rail fJ rms (7%), against 13.6 for one price (E138 `scored.json` › `out_of_sample_e130`), because no zero-delay netlist gives
  the card's pattern. Each netlist's own prediction of E138's rail prices (bits 0–6, nothing fitted to the bits, k from E78's
  kinds, rail at E78's frozen 0.81 per board fJ; [`tables.md`](tables.md), "Out of sample"): Booth on B **18.2–18.5 rail fJ rms at
  zero delay, 34.5–39.5 with glitches at their own refitted k** (94–105 at the zero-delay k); the other two 39.9–40.1 → 43.9–44.7.
  Glitch-aware counts make the B prediction worse, and every netlist stays worse than one flat price. **E138's measured per-position
  prices stay in the model.**
- **The kind-level term.** On E78's 15 int8 kinds, replacing zero-delay counts by glitch-aware ones raises M2's leave-one-kind-out
  error from **0.295 to 0.433 W** (Booth on B), **0.257 to 0.371 W** (`booth_swap`) and **0.420 to 0.733 W** (`plain`); a separate
  glitch term takes a negative weight. **The model keeps zero-delay gate counts with a fitted price per toggle**, which absorbs
  whatever glitching the chip has; these netlists' glitches are not a term to add.
- **Heat**: nothing here measures heat. The prediction of heat moves only through the power term (M6's die rise per board watt),
  and no power term changes.

## What was asked and what was done

Asked (Q138's brief, lane Q138(g)): a timing-aware event simulation of each of Q133(a)'s four int8 netlists, cell delays from the
flow's liberty at the typical corner, inertial delays, for E130's and E138's single-flip sets; whether any netlist's glitch-aware
odd/even ratio and A-side pattern lands inside the card's intervals; the simulator validated first on a small circuit with a known
glitch count; on the Intel, `nice -n 10`, at most six cores, never on the boxes; about 2.5 hours. Done: all of that, for all 26 of
E130's tiles (E138's 13 B tiles are among them) in all four netlists, with Icarus Verilog as a second check; also a glitch-aware
refit of M2 on E78's int8 kinds, a glitch-weight scan, and five arms (result 6).

**Departures, each decided before the counts it touches unless marked.**
- **D1: an own simulator, not iverilog with SDF.** The open flow on this Mac has no static timing tool (OpenROAD's pinned build is
  linux-64, Q133(a) Departures), so there is no SDF; and a Verilog cell model with one delay per edge cannot carry the liberty's
  per-pin, per-state arcs. The simulator reads the liberty tables itself, and is checked against Icarus Verilog wherever Icarus can
  express the model (result 5).
- **D2: delays without placement.** Loads are pin capacitances plus a fanout wire load (0.2 fF + 0.1 fF a pin), slews are
  propagated statically, the clock is ideal and the input ports move together at the smallest CLK->Q. The wire-load, input-skew and
  delay-error arms test this (result 6).
- **D3: the middle launch point is the primary** (471,698 ops into a 0.5 s launch), as Q133(a) ran single bits; Q136(a)'s frozen
  values at that point are its `fJ_map_by_point[1]`. The three points' mean is an arm, for `booth_tree` only (decided 19:55 PST,
  for time on a loaded machine, before those runs).
- **D4: the glitch-weight scan, the refit and the separate glitch term were added after the first single-bit counts were seen**
  (post hoc), to ask whether any partial cost of a glitch could fit and what the kinds' watts say about one. Nothing here was
  registered: this lane predicts no card run.
- **D5: prices in the frozen frame**: the whole-VPU `nets_map` plus the unit's excess. The rest of the VPU is RTL and cannot glitch
  here; Q136(a) found it adds −0.7 to +2.1 nets a flip in every netlist.
- **D6 (19:40 PST, before its runs):** a sixth arm, every cell's delays scaled by its own random factor in [0.8, 1.2], for
  `booth_tree` and `plain`.
- **D7 (19:50–19:55 PST): a batch paused and rerun.** To shorten the run queue I stopped its parent shell; the batch it was running
  (the Verilog-rule arm) became an orphan, which the Intel's load guard pauses in its warm tier (the machine was thermally clamped to
  54–58% with a load of 59–72). I ended that batch (this lane's own processes, which had written nothing) and reran the remaining
  arms under a live shell. The guard was left alone. No result was lost or changed; the completed runs are cached by file.
- **D8: the validation ran beside the first batch, not strictly before it** (the small circuits 19:12–19:21 PST, the primary batch
  from 19:14). No count was read before it passed. The engine's default path was not changed after the primary runs (the
  Verilog-rule option and the delay-jitter models were added beside it), and the committed code reproduces a primary run's totals and
  stage split exactly (`booth_tree`, `b1_3`) and its models (`plain`) field for field.

## Device commands sent

**None.** A desk lane: no card, no device node, no device-management command, no ssh to any box.

## What this cannot say

- **These are open 7 nm netlists of the public RTL's later revision (Erbium), not the chip's gates**, and the chip's multiplier is
  not public. That neither group fits with glitches or without does not say what silicon has.
- **Delays without placement or wires' resistance, one corner, an ideal clock, and a full swing for every pulse the inertial model
  passes.** Real short pulses are partial; the glitch-weight scan stands in for that, not a circuit simulation.
- **Toggle counts, not energy.** k is a fitting constant per merged net toggle; a glitch on a short net costs less than a full
  toggle of a long one, and nothing here weighs nets by their capacitance.
- **The card's intervals are E130's and E138's**, one card (aifoundry3); E145 reads B on a second card.

## Section 11, item 12, and what a reader can be told

- **Item 12's "glitches, since the counts are at zero delay" is answered**: counted with the cells' own delays, the Booth-on-B
  netlists' B odd ÷ even doubles (4.3 → 9.3–9.5) and the others' stays at 0.99–1.12; the card's 1.91 [1.71, 2.16] is reached by
  none, at any glitch weight. The structural verdict stays where E138 left it: neither netlist group fits B, and glitches reconcile
  neither. **"Why the even bits cost more" stays open**, with glitches in these netlists now excluded as the reason. On the A side
  glitches account for the card's A sign step (no recoder at full glitch cost, Booth on B at about half), the other part of E130's
  misfit; and on E78's kinds glitch-aware counts predict the card worse than zero-delay counts.
- For the blog, each from a committed file:
  - "A gate can flip several times in one clock cycle while its inputs arrive at different times. Counted with the cells' own
    delays, a Booth multiplier's odd B bits switch three times as many nets as at zero delay and its even bits about one and a half
    times, so its odd-to-even cost ratio rises from about 4 to about 9. The chip's is about 1.9" (`glitch_mid.json` ›
    `arms.booth_tree`; E138 `scored.json` › `primary.B_odd_over_even`).
  - "Glitches are not why the chip's even B bits cost more than a Booth multiplier predicts: in these netlists they make the odd bits
    far dearer instead" (`glitch_mid.json` › `arms.*.glitch_weight_scan`).
  - "A random int8 multiply-add in these netlists switches about twice as many nets once glitches are counted, but the chip's watts
    across fifteen kinds of numbers follow the glitch-free count better" (`refit_k.json` › `arms.*.kinds`, `zero_delay`,
    `glitch_aware`).

## Files

| file | what |
|---|---|
| `README.md`, `METHOD.md`, `tables.md` | this, the method, the generated tables (every arm, per bit, the scan, out of sample, the refit) |
| `glitch_mid.json` | the primary: per netlist and tile (minus its zero, per flip) zero-delay, timed and excess counts by stage, prices in the frozen frame, the statistics, the card's intervals, the glitch-weight scan |
| `glitch_3pt.json`, `glitch_vstyle.json`, `glitch_skew150.json`, `glitch_wire0.json`, `glitch_wire3.json`, `glitch_jitter20.json` | the arms (result 6) |
| `refit_k.json` | M2 on E78's 15 int8 kinds, zero delay against glitch-aware and with a separate glitch term, per netlist, and the single bits at the refitted k |
| `summary.json` | the tables' numbers |
| `sims/<run>.json` | every simulation of a run (`primary`, the arms), keyed `<netlist>__<tile>__<point>`: the totals and the stage split over the 16 units, and each unit's totals, checks and largest excess nets (per-net lists dropped) |
| `validate.json`, `xcheck/` | the small circuits, and the whole-netlist Icarus Verilog cross-checks |
| `models.txt`, `versions.txt` | the annotated models' delay summaries; tools, sources, host |

```bash
# the build and the batch runs: tools/open-flow/glitch/README.md. From the committed files, in this directory:
G=../../../../tools/open-flow/glitch
python3 $G/analyze_glitch.py --sims sims/primary.json --point 471698 --out glitch_mid.json
python3 $G/analyze_glitch.py --sims sims/primary.json --point 157232,471698,786163 --out glitch_3pt.json
python3 $G/analyze_glitch.py --sims sims/vstyle.json --point 471698 --out glitch_vstyle.json    # likewise skew150; wire0, wire3 (--arms booth_tree); jitter20 (--arms booth_tree,plain)
python3 $G/refit_k.py --sims sims/primary.json --glitch glitch_mid.json --out refit_k.json      # numpy
python3 $G/summarize.py --dir . --out-md tables.md --out-json summary.json
```
(These reproduce the committed JSON files except their `sims` field, which names the source.)
