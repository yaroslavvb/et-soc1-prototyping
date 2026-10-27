# The price of one transistor flip, by kind of gate, from open data

**Request Q126(d), part 1. Monday 26 October 2026 (week 44).** Written on a Mac from the open
[ASAP7](https://github.com/The-OpenROAD-Project/asap7) kit alone. No card, no lab box, no private
file was touched.

> **Corrected the same day, after review.** The first version of this directory summed each arc's
> mutually exclusive `when` states instead of averaging them, and built its headline `E/transition`
> columns from the VDD+VSS sum its own text called double-counting. Both are fixed below; every
> published number was regenerated. What changed, and by how much, is in
> [What the first version got wrong](#what-the-first-version-got-wrong) at the foot of this file.

The Horace project wants a model that turns a load into watts, and the price list below the gate was
a gap in it: the counted toggles had no per-kind price from a source anyone can re-run. This
directory prices each kind of gate the ET-SoC-1's multiply-add is built from, out of ASAP7's
BSD-3-Clause 7 nm standard-cell library, and sets the result beside the chip diagram's census
(Q124) and the lab's own measurement (E60).

Part 2, the same cells in SPICE, is
[`../2026-10-26-asap7-one-switch/`](../2026-10-26-asap7-one-switch/). It settles a factor-of-two
convention question this part could only flag, and its answer is folded into the headline here.

## Files

| File | What |
|---|---|
| `asap7_cell_energies.py` | the whole of part 1: reads the liberty, writes the JSON and the table |
| `libparse.py` | a small Liberty reader (group tree, LUT interpolation) |
| `asap7-cell-energies.json` | every number, with its units, conventions and caveats |
| `table.md` | the headline table below, as generated |

**To re-run.** Clone `asap7sc7p5t_28` and `asap7_pdk_r1p7`, unpack the six `*_RVT_TT_nldm_*.lib.7z`
files from `asap7sc7p5t_28/LIB/NLDM/` into one directory, then:

```
python3.12 -I asap7_cell_energies.py <libdir> <outdir> [<vtdir>] [<census_flat.json>]
```

`<vtdir>` holds the four `INVBUF_*_TT` liberties (for FO4 by threshold flavour).
`<census_flat.json>` is Q126(e)'s cell census, `../2026-10-26-open-netlist/census_flat.json`.

## The corner, and what the numbers mean

ASAP7 7.5-track, **RVT, typical (TT) corner, NLDM, 0.7 V, 25 °C**. Liberty's derived energy unit
here is 1 V × 1 mA × 1 ps = **1 fJ**; capacitance is fF, leakage pW, time ps.

**Four conventions decide what the numbers mean, and all four bit.**

1. **The 4× drawing scale does not touch the liberty.** ASAP7's layout is drawn at four times the
   real dimensions, so every length in the GDS, the LEF and the QRC techfile must be divided by 4
   (and area by 16). **The liberty is not scaled**: the capacitances, energies, delays and leakages
   below are real-world 7 nm values and need no correction. Q126(e) hit the same thing from the
   other side — the ORFS `asap7` platform is already 1×, so the 4× must *not* be applied there.
2. **Internal energy is split between the rails, and summing double-counts.** ASAP7 characterises
   each event against both VDD and VSS, with a negative cross term: INVx1's output rise is
   +0.120 fJ on VDD and −0.028 fJ on VSS. **Part 2 settles it: SPICE on the kit's own transistor
   netlist measures 0.0875 fJ of internal energy per full cycle for INVx1 at 2 fF and 0.7 V,
   against 0.0974 fJ for the VDD-only reading and 0.195 fJ for the summed one.** So **the VDD group
   alone is the energy drawn from the rail**, and it is what every headline column here uses. The
   summed column is kept, labelled `summed reference`, because a reader coming from a power tool
   will see it.
3. **An arc's `when` states are mutually exclusive, so they are averaged, not summed.** FAx1's
   `A→SN` arc carries four of them — `(B·CI)`, `(B·!CI)`, `(!B·CI)`, `(!B·!CI)` — and exactly one
   holds at any moment. The averaging is **uniform**: the liberty carries no state probabilities, so
   a real workload's state statistics would move a cell within the spread its `by_state` block
   carries (FAx1's `A→SN` runs 0.129 to 0.148 fJ per transition across its four states, a 15%
   spread; XOR2x1's `A→Y` runs 0.166 to 0.326, a factor of 2).
4. **Leakage is not scaled to 0.517 V.** It falls with voltage through DIBL and the subthreshold
   slope, not as V². Part 2 measures it: INVx1 leaks 37.0 pW at 0.7 V and 20.4 pW at 0.517 V
   (25 °C), a factor 1.8 for a factor 1.35 in voltage — nothing like V².

`E per transition` below is the task's formula, `internal (VDD only) + ½·C_load·V²`, at a **stated
operating point: 10 ps input slew (10–90%) and 2.0 fF output load**, bilinearly interpolated in the
cell's own 7×7 tables. The `@0.517 V` column scales by (0.517/0.7)² = 0.5454, which is exact for the
capacitive part and slightly optimistic for the short-circuit part. The JSON carries the full
tables, the per-arc rise and fall, the per-state breakdown and a load sweep from 0.5 to 8 fF.

## The table

Generated copy: `table.md`. Internal energy is per output transition, averaged over rise and fall,
over the arc's `when` states, then over the cell's arcs; leakage is the state-averaged VDD entry at
0.7 V and 25 °C.

| cell | input pin cap (fF) | leakage (pW) | when states | **internal E/transition, VDD only (fJ)** | summed reference (fJ) | **E/transition @0.7 V (fJ)** | **@0.517 V (fJ)** |
|---|---|---:|---:|---:|---:|---:|---:|
| INVx1 | A 0.620 | 51.2 | 1 | **0.0487** | 0.0975 | 0.5387 | 0.2939 |
| INVxp33 | A 0.276 | 17.1 | 1 | **0.0243** | 0.0484 | 0.5143 | 0.2806 |
| BUFx2 | A 0.534 | 136.4 | 1 | **0.2517** | 0.5033 | 0.7417 | 0.4046 |
| NAND2x1 | A 0.990, B 0.990 | 91.2 | 1 | **0.1103** | 0.2232 | 0.6003 | 0.3274 |
| NOR2x1 | A 1.001, B 1.017 | 82.1 | 1 | **0.1166** | 0.2293 | 0.6066 | 0.3309 |
| XOR2x1 | A 1.519, B 1.523 | 232.1 | 2 | **0.2448** | 0.4881 | 0.7348 | 0.4008 |
| XNOR2x1 | A 1.520, B 1.516 | 232.3 | 2 | **0.2429** | 0.4871 | 0.7329 | 0.3998 |
| AOI21x1 | A1 1.113, A2 0.963, B 1.134 | 127.0 | 3 | **0.1426** | 0.2834 | 0.6326 | 0.3451 |
| OAI21x1 | A1 1.112, A2 0.952, B 1.251 | 140.1 | 3 | **0.1439** | 0.2889 | 0.6339 | 0.3458 |
| MAJIxp5 | A 0.595, B 1.122, C 0.963 | 94.3 | 2 | **0.1056** | 0.2110 | 0.5956 | 0.3249 |
| MAJx2 | A 0.598, B 1.128, C 0.959 | 196.6 | 2 | **0.3146** | 0.6292 | 0.8046 | 0.4389 |
| HAxp5 | A 0.981, B 0.914 | 137.0 | 2 | **0.1023** | 0.2052 | 0.5923 | 0.3231 |
| FAx1 | A 1.827, B 1.997, CI 1.494 | 212.2 | 4 | **0.1421** | 0.2840 | 0.6321 | 0.3448 |
| DFFHQNx1 | CLK 0.475, D 0.559 | 229.7 | 1 | **0.4965** | 1.1010 | 0.9865 | 0.5381 |
| DFFHQx4 | CLK 0.476, D 0.559 | 485.5 | 1 | **0.9892** | 2.0865 | 1.4792 | 0.8069 |
| ICGx1 | CLK 2.191, ENA 0.427, SE 0.428 | 319.2 | 2 | **0.3258** | 0.4045 | 0.8158 | 0.4450 |

The smaller drives (`INVxp33`, `NAND2xp33`, `NOR2xp33`, `AOI21xp33`, `OAI21xp33`, `XOR2xp5`,
`XNOR2xp5`) are in `table.md` and the JSON. The two flops are both here because they differ by 2.0×
and the census netlist contains only the larger one (see the flip estimate below).

**The sequential cells carry two separate prices,** and only the first is marginal to a data flip:

- `DFFHQNx1`, **output switching** (CLK→QN): 0.4965 fJ per transition, VDD only.
  `DFFHQx4` (CLK→Q): 0.9892 fJ, almost exactly 2×.
- `DFFHQNx1`, **clock pin with the data held**: 0.49–0.60 fJ per clock cycle by state, mean
  0.565 fJ, VDD only. This is the cost a clocked bit pays whether or not it changes. The
  20 October plan's "0.6 fJ a cycle even with its data held" is this number, and it checks out.
  `DFFHQx4`'s clock pin is the same to three figures (0.566 fJ), which makes sense — the clock pin
  drives the master latch, not the output drive.
- `ICGx1`, clock pin: 0.41 fJ per clock cycle, VDD only, averaged over its enable states (0.17 fJ
  disabled, 0.65 fJ enabled — a clock gate that is actually gating costs a quarter of one that is
  passing).

Four numbers the 20 October plan had already quoted from ASAP7 reproduce exactly: inverter input
0.62 fF, full-adder input 2.0 fF, flip-flop clock pin 0.475 fF, clock gate 2.19 fF.

## ASAP7's published device numbers

Lifted from the paper the kit ships, `asap7_pdk_r1p7/docs/mej_paper_asap7.pdf`, Tables 3 and 4
(typical corner, **per fin**, 25 °C, 0.7 V):

| | NMOS SRAM | NMOS RVT | NMOS LVT | NMOS SLVT | PMOS SRAM | PMOS RVT | PMOS LVT | PMOS SLVT |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| I_dsat (µA) | 28.57 | 37.85 | 45.19 | 50.79 | 26.90 | 32.88 | 39.88 | 45.60 |
| I_eff (µA) | 13.07 | 18.13 | 23.56 | 28.67 | 11.37 | 14.08 | 18.18 | 22.64 |
| I_off (nA) | 0.001 | 0.019 | 0.242 | 2.444 | 0.004 | 0.023 | 0.230 | 2.410 |
| V_tsat (V) | 0.25 | 0.17 | 0.10 | 0.04 | −0.20 | −0.16 | −0.10 | −0.04 |
| V_tlin (V) | 0.27 | 0.19 | 0.12 | 0.06 | −0.22 | −0.19 | −0.13 | −0.07 |
| SS (mV/decade) | 62.44 | 63.03 | 62.90 | 63.33 | 64.34 | 64.48 | 64.44 | 64.94 |
| DIBL (mV/V) | 19.23 | 21.31 | 22.32 | 22.55 | 24.10 | 30.36 | 31.06 | 31.76 |

Geometry (§3.1, §4.1, Table 1): **CPP 54 nm**, fin pitch 27 nm, M1–M3 pitch 36 nm, fin width 6.5 nm
actual / 7 nm drawn, fin height 32 nm, gate length 21 nm actual / 20 nm drawn, 7.5-track cell row
(7.5 × 36 nm = 270 nm). The cells here are 3 fins per device for an x1 drive (`nfin=3` in the CDL).

**Citation:** L.T. Clark, V. Vashishtha, L. Shifren, A. Gujja, S. Sinha, B. Cline, C. Ramamurthy,
G. Yeric, *ASAP7: A 7-nm finFET predictive process design kit*, Microelectronics Journal 53 (2016)
105–115, [doi:10.1016/j.mejo.2016.04.006](https://doi.org/10.1016/j.mejo.2016.04.006), open access
under CC BY-NC-ND.

**Two things the paper does not give**, against the brief for this request:

- **Gate leakage.** The paper gives no figure. Its I_off is drain current at V_gs = 0, not gate
  leakage. The BSIM-CMG cards do enable it (`igcmod = 1` in `models/hspice/7nm_TT_160803.pm`), so a
  number needs a SPICE sweep, which part 2 did not have time for either.
- **FO4.** The paper prints none, so it is computed here from the liberty itself — an INVx1 driving
  four INVx1 input pins, with the input slew iterated until it equals the stage's own output slew,
  which is what a chain of these cells settles at:

| | RVT | LVT | SLVT | SRAM |
|---|---:|---:|---:|---:|
| FO4 at 0.7 V, 25 °C, TT | **19.60 ps** | 15.78 ps | 13.48 ps | 24.31 ps |

🛑 **The brief for this request quoted "about 8.1 ps RVT at 0.7 V" as the kit's FO4. No threshold
flavour gives that from the liberty.** Part 2 resolves it: SPICE on the kit's *schematic* (LVS)
netlist gives **9.63 ps** at 0.7 V, close to 8.1, while the liberty — characterised on the
*parasitic-extracted* netlist — says 19.60 ps. The 8.1 ps class of number is pre-layout. Anyone
quoting an ASAP7 FO4 has to say which netlist it came from. **This is a delay ratio and nothing
else**: part 2 measured no matching energy ratio, and what it did measure went both ways by cell.

## Pricing the flow-M flip from ASAP7 alone

Q124's census (`../2026-09-27-chip-diagram/research/tensorfma32.json`, fact `tfma.flip.gate`) counted
**381 physical wires** toggling in a zero-delay gate-level run of lane 0 for the E60 case
"b bit 11 flipped, a = π": 129 in f1 (19 of them flip-flop outputs) and 252 in f2 (16 of them the
product register's). So **346 combinational cell outputs and 35 flip-flop outputs**.

Each toggling wire is priced as one cell-output transition at 0.517 V:

```
E_flip = 346 · (E_int_cell·0.5454 + ½·C_net·0.517²) + 35 · (E_int_flop·0.5454 + ½·C_net·0.517²)
```

The cell mix is the one **Q126(e) measured on this very unit** the same day: core-et's `txfma_top`
synthesized onto this library with Yosys, 16,087 cells flattened
(`../2026-10-26-open-netlist/census_flat.json`). All 33 combinational cell types in that histogram
are priced here, none missing, covering 14,119 cells; the weighted mean internal energy per
transition is **0.218 fJ at 0.7 V, VDD only**. The flop is that netlist's own flop, **DFFHQx4** —
the only flop type it contains, 1,953 of them. Two hand-built pools (the x1 drives, and the minimum
drives, both with the minimum-drive DFFHQNx1) are carried as a sensitivity.

Flip-flops contribute their **data-switching** arc only: the clock reaches 1,586 of the lane's 1,851
flops on every multiply-add either way (`tfma.clocked`), so the clock-pin energy is not marginal to
a flip.

| per-net load | 1 fF | 2 fF | 4 fF |
|---|---:|---:|---:|
| **census mix + DFFHQx4, VDD only (headline)** | **0.111 pJ** | **0.162 pJ** | **0.264 pJ** |
| minimum-drive pool + DFFHQNx1, VDD only | 0.075 pJ | 0.126 pJ | 0.228 pJ |
| x1 pool + DFFHQNx1, VDD only | 0.088 pJ | 0.139 pJ | 0.240 pJ |

The model is linear in the net load, which is the clearest way to state it:

```
E_flip(C) = 60.0 fJ  +  50.9 fJ/fF · C          (0.517 V, census mix, VDD only, zero delay)
```

60.0 fJ is what the cells cost with no net capacitance at all; everything above that is wire and pin.

### Against Q124 — the one like-for-like check

Q124 priced the same 381 wires, over the same scope (Booth rows, Wallace tree, product adder), on
the same zero-delay basis, using the **real** cells' energies. It is the only comparison here that
needs no correction.

| | pJ per flip | implied per-net load |
|---|---|---|
| **This estimate, ASAP7 alone** | 0.111 – 0.264 (1–4 fF per net) | — |
| **Q124, priced with the real cells** (`tfma.flip.energy`) | 0.11 – 0.13 | **0.98 – 1.37 fF** |

So **the estimate brackets Q124 rather than erring dear**: its light-load end lands on Q124's low
end, and Q124's whole band corresponds to a per-net load of **about 1.0 to 1.4 fF** in this model —
squarely in the plausible range for a tree-level wire plus the pin it drives. That is a good outcome
from a predictive kit that knows nothing about the ET-SoC-1, and it is the first outside check on
the flip price.

### Against E60 — three scope differences, and only one operand case matches

E60's Hamming ladder reports **two operand cases, not an uncertainty band**
(`docs/findings/03-experiments.md`). The case Q124 counted, and therefore the case this estimate
models, is **a = π**:

| E60, aifoundry3, 600 MHz, 0.522 V | board | minion rail |
|---|---:|---:|
| **a = π, b bit 11 — the case modelled here** | **129.9 ± 0.5 fJ** | **96.9 fJ** |
| a = 1.0 — a different multiply, not this one | 116.7 ± 0.6 fJ | 87.5 fJ |

Three things still separate the estimate from that measurement, and they do not cancel:

1. **Board versus rail.** 129.9 fJ is board energy, including the regulator's conversion loss. The
   minion-rail figure, 96.9 fJ, is the one to set beside a cell-level estimate — and even that is
   the whole rail, not the one unit.
2. **Scope.** E60 is measured "the cascade included"; the estimate and Q124 cover the Booth rows,
   the tree and the product adder only.
3. **Glitches.** E60 is silicon and contains them; the estimate and Q124 are zero-delay.
   `tfma.glitch` puts the timed tree at 1.4× the energy, so the comparable number is this estimate
   **× 1.4**, which is 0.155 – 0.369 pJ for 1–4 fF.

On those terms the estimate sits **above** E60's rail figure: hitting 96.9 fJ would need a per-net
load of 0.72 fF zero-delay, or 0.18 fF once the glitch factor is carried, and neither is a real
wire. That is a scope gap to be closed, not a contradiction — but it is the honest reading, and it
says the next thing to measure is the unit's actual net capacitances.

**The dominant uncertainty is still the per-net load, not the cells.** Going from 1 fF to 4 fF per
net moves the answer by **2.4×**. Swapping the whole combinational cell mix moves it by only
**1.3×** at 2 fF (0.126 to 0.162 pJ) even though the pools' mean cell energies differ by 2.8×
(0.077 to 0.218 fJ), because the net load dominates; and the flop choice (DFFHQx4 against
DFFHQNx1, 35 wires of 381) by **6%**.

Other things the estimate assumes, all listed in the JSON's `assumptions`: one toggling wire is one
cell-output transition; uniform `when`-state weighting; the open synthesis made 7,967 cells for the
multiplier against the tape-out flow's 4,487, so its histogram is used as the *mix*, not the count;
and ASAP7 is a predictive 7 nm PDK, not TSMC N7.

## Does the short-circuit path close at 0.517 V?

The 20 October plan hoped it might: "It vanishes if the supply is below the two thresholds added
together, which may be true at 0.517 V."

**It is not true.** For ASAP7 RVT, V_tn + |V_tp| = 0.17 + 0.16 = **0.33 V** on the saturation
thresholds, 0.19 + 0.19 = **0.38 V** on the linear ones. The minion's 0.517 V is **0.19 V above** the
first and 0.14 V above the second, so both devices can conduct during an input edge and the
short-circuit path stays open.

Part 2 measures what it costs, and the answer is kinder than the threshold test alone suggests:
the overlap window is 36% of the swing at 0.517 V against 53% at 0.7 V, and in SPICE an INVx1 at
0.517 V shows **no rise at all** in rail energy out to a 200 ps input edge, while at 0.7 V a 200 ps
edge costs **+0.064 fJ per cycle, about 70% above its fast-edge internal energy**.

## Where this leaves the Horace model

- The price list below the gate now has a sourced, re-runnable row per kind of gate, at both 0.7 V
  and 0.517 V, with leakage beside it.
- The factor-of-two in liberty internal energy is closed: **the VDD group alone is the rail energy**,
  and anything quoting a summed internal power against a rail measurement is double-counting.
- A second, independent factor is closed with it: **`when` states are averaged, not summed** — the
  trap that makes a full adder look three times dearer than it is.
- The flip price has its first outside check: 0.111–0.264 pJ from open data, which brackets Q124's
  0.11–0.13 pJ at a per-net load of 1.0–1.4 fF.
- Still open: the unit's real wire capacitances. Every number here is one extraction away from being
  a prediction rather than a bracket, and the gap to E60's rail figure cannot be read until it is.

## What the first version got wrong

Both defects were found in review on the same day, before anything was published outside this
repository. They are recorded here because each is a trap any later liberty reader will meet.

**1. Mutually exclusive `when` states were summed, not averaged.** The reader keyed each arc only by
`related_pin → output_pin`, so a cell whose arc is characterised separately for each side-input
state had all those states added together. The inflation is exactly the number of states:

| cell | published before | corrected | factor |
|---|---:|---:|---:|
| INVx1, NAND2x1 (no `when`) | 0.0487, 0.1103 | 0.0487, 0.1103 | 1.00× |
| HAxp5 | 0.1517 | 0.1023 | 1.48× |
| AOI21x1 | 0.2214 | 0.1426 | 1.55× |
| XOR2x1, MAJIxp5 | 0.4896, 0.2112 | 0.2448, 0.1056 | 2.00× |
| FAx1 | 0.4255 | 0.1421 | 2.99× |
| AO221x1 (census) | 0.9024 | 0.2146 | 4.20× |
| AO222x2 (census) | 2.9595 | 0.3406 | 8.69× |

The census-weighted mean went from 0.3792 to **0.2179 fJ**, a 1.74× inflation, and the headline flip
estimate from 0.132–0.285 pJ to 0.111–0.264 pJ.

Part 2's own SPICE data would have caught it: SPICE measures FAx1's `A→SN` arc (with B = CI = 0) at
0.324 fJ per cycle against the published liberty figure of 0.851 fJ per cycle, 2.6× apart, while the
correctly averaged liberty value for that exact state is 0.272 fJ per cycle — 1.19× apart, which is
the ordinary schematic-versus-liberty scatter part 2 now measures across eight cases.

**2. The headline `E/transition` columns used the summed convention this file calls double-counting.**
The text said the VDD group alone is the rail energy, and then built `E/transition = internal +
½C_load V²` from the VDD+VSS sum. Corrected, with the `when` fix as well: FAx1 1.3403 → **0.6321 fJ**,
XOR2x1 1.4663 → **0.7348**, DFFHQNx1 1.5910 → **0.9865**, INVx1 0.5875 → **0.5387**.

**3. Smaller, same review.** The flip estimate priced its 35 flop outputs with `DFFHQNx1` while
claiming the Q126(e) census's mix; that census contains only `DFFHQx4`, at 2.0× the energy. It now
uses the census's own flop and carries the swap as an explicit sensitivity (+6%). The E60 comparison
quoted "0.117–0.130 pJ" as though it were an uncertainty band, when those are two different operand
cases and only a = π matches; it is now split out with its three scope differences stated.
