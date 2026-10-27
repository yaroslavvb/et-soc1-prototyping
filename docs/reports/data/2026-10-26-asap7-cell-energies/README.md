# The price of one transistor flip, by kind of gate, from open data

**Request Q126(d), part 1. Monday 26 October 2026 (week 44).** Written on a Mac from the open
[ASAP7](https://github.com/The-OpenROAD-Project/asap7) kit alone. No card, no lab box, no private
file was touched.

The Horace project wants a model that turns a load into watts, and the price list below the gate was
a gap in it: the counted toggles had no per-kind price from a source anyone can re-run. This
directory prices each kind of gate the ET-SoC-1's multiply-add is built from, out of ASAP7's
BSD-3-Clause 7 nm standard-cell library, and sets the result beside the chip diagram's census
(Q124) and the lab's own measurement (E60).

Part 2, the same cells in SPICE, is
[`../2026-10-26-asap7-one-switch/`](../2026-10-26-asap7-one-switch/). It settles a factor-of-two
convention question this part could only flag, and its answer is already folded into the headline
here.

## Files

| File | What |
|---|---|
| `asap7_cell_energies.py` | the whole of part 1: reads the liberty, writes the JSON and the table |
| `libparse.py` | a small Liberty reader (group tree, LUT interpolation) |
| `asap7-cell-energies.json` | every number, with its units, conventions and caveats |
| `table.md` | the headline table below |

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

Three conventions decide what the numbers mean, and all three bit:

1. **The 4× drawing scale does not touch the liberty.** ASAP7's layout is drawn at four times the
   real dimensions, so every length in the GDS, the LEF and the QRC techfile must be divided by 4
   (and area by 16). **The liberty is not scaled**: the capacitances, energies, delays and leakages
   below are real-world 7 nm values and need no correction. Q126(e) hit the same thing from the
   other side — the ORFS `asap7` platform is already 1×, so the 4× must *not* be applied there.
2. **Internal energy is split between the rails, and summing double-counts.** ASAP7 characterises
   each event against both VDD and VSS, with a negative cross term: INVx1's output rise is
   +0.120 fJ on VDD and −0.028 fJ on VSS. Summing the two (what a power tool reports as total
   internal energy) gives 0.0975 fJ per transition; the VDD group alone gives 0.0487 fJ. **Part 2
   settles it: SPICE on the kit's own transistor netlist measures 0.0875 fJ of internal energy per
   full cycle for INVx1 at 2 fF and 0.7 V, against 0.0974 fJ for the VDD-only reading and 0.195 fJ
   for the summed one.** So **the VDD-only column is the energy drawn from the rail**, and it is
   the one the headline uses. Both are in the table and in the JSON, because a reader coming from a
   power tool will see the other.
3. **Leakage is not scaled to 0.517 V.** It falls with voltage through DIBL and the subthreshold
   slope, not as V². Part 2 measures it: INVx1 leaks 37.0 pW at 0.7 V and 20.4 pW at 0.517 V
   (25 °C), a factor 1.8 for a factor 1.35 in voltage — nothing like V².

`E per transition` below is the task's formula, `internal + ½·C_load·V²`, at a **stated operating
point: 10 ps input slew (10–90%) and 2.0 fF output load**, bilinearly interpolated in the cell's own
7×7 tables. The `@0.517 V` column scales by (0.517/0.7)² = 0.5454, which is exact for the capacitive
part and slightly optimistic for the short-circuit part. The JSON carries the full tables, the
per-arc rise and fall, and a load sweep from 0.5 to 8 fF.

## The table

See `table.md` for the generated copy. Internal energy is per output transition, averaged over rise
and fall; leakage is the state-averaged VDD entry at 0.7 V and 25 °C.

| cell | input pin cap (fF) | leakage (pW) | internal E/transition, VDD only (fJ) | summed (fJ) | E/transition @0.7 V (fJ) | @0.517 V (fJ) |
|---|---|---:|---:|---:|---:|---:|
| INVx1 | A 0.620 | 51.2 | 0.0487 | 0.0975 | 0.5875 | 0.3205 |
| INVxp33 | A 0.276 | 17.1 | 0.0243 | 0.0484 | 0.5384 | 0.2937 |
| BUFx2 | A 0.534 | 136.4 | 0.2517 | 0.5033 | 0.9933 | 0.5418 |
| NAND2x1 | A 0.990, B 0.990 | 91.2 | 0.1103 | 0.2232 | 0.7132 | 0.3890 |
| NOR2x1 | A 1.001, B 1.017 | 82.1 | 0.1166 | 0.2293 | 0.7193 | 0.3924 |
| XOR2x1 | A 1.519, B 1.523 | 232.1 | 0.4896 | 0.9763 | 1.4663 | 0.7998 |
| XNOR2x1 | A 1.520, B 1.516 | 232.3 | 0.4858 | 0.9742 | 1.4642 | 0.7987 |
| AOI21x1 | A1 1.113, A2 0.963, B 1.134 | 127.0 | 0.2214 | 0.4413 | 0.9313 | 0.5080 |
| MAJIxp5 | A 0.595, B 1.122, C 0.963 | 94.3 | 0.2112 | 0.4219 | 0.9119 | 0.4974 |
| FAx1 | A 1.827, B 1.997, CI 1.494 | 212.2 | 0.4255 | 0.8503 | 1.3403 | 0.7311 |
| DFFHQNx1 | CLK 0.475, D 0.559 | 229.7 | 0.4965 | 1.1010 | 1.5910 | 0.8679 |
| ICGx1 | CLK 2.191, ENA 0.427, SE 0.428 | 319.2 | 0.6517 | 0.8090 | 1.2990 | 0.7086 |

The smaller drives (`INVxp33`, `NAND2xp33`, `NOR2xp33`, `AOI21xp33`, `OAI21xp33`, `XOR2xp5`,
`XNOR2xp5`, `HAxp5`) and `MAJx2`, `OAI21x1` are in `table.md` and the JSON.

**The sequential cells carry two separate prices,** and only the first is marginal to a data flip:

- `DFFHQNx1`, **output switching** (CLK→QN): 0.4965 fJ per transition, VDD only.
- `DFFHQNx1`, **clock pin with the data held**: 0.49–0.60 fJ per clock cycle, VDD only
  (0.88–1.20 fJ summed), by state. This is the cost a clocked bit pays whether or not it changes.
  The 20 October plan's "0.6 fJ a cycle even with its data held" is this number, on the VDD-only
  reading, and it checks out.
- `ICGx1`, clock pin: 0.41 fJ per clock cycle, VDD only (0.59 fJ summed), averaged over states.

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
  number needs a SPICE sweep.
- **FO4.** The paper prints none, so it is computed here from the liberty itself — an INVx1 driving
  four INVx1 input pins, with the input slew iterated until it equals the stage's own output slew,
  which is what a chain of these cells settles at:

| | RVT | LVT | SLVT | SRAM |
|---|---:|---:|---:|---:|
| FO4 at 0.7 V, 25 °C, TT | **19.60 ps** | 15.78 ps | 13.48 ps | 24.31 ps |

🛑 **The brief for this request quoted "about 8.1 ps RVT at 0.7 V" as the kit's FO4. No threshold
flavour gives that from the liberty.** Part 2 resolves it: SPICE on the kit's *schematic* (LVS)
netlist gives **9.63 ps** at 0.7 V, close to 8.1, while the liberty — characterised on the
*parasitic-extracted* netlist — says 19.60 ps. The 8.1 ps class of number is pre-layout; the
parasitics roughly double it. Anyone quoting an ASAP7 FO4 has to say which.

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
transition is **0.379 fJ at 0.7 V, VDD only**. Two hand-built pools (the x1 drives, and the minimum
drives) are carried as a sensitivity.

Flip-flops contribute their **data-switching** arc only: the clock reaches 1,586 of the lane's 1,851
flops on every multiply-add either way (`tfma.clocked`), so the clock-pin energy is not marginal to
a flip.

| per-net load | 1 fF | 2 fF | 4 fF |
|---|---:|---:|---:|
| **census mix, VDD only (headline)** | **0.132 pJ** | **0.183 pJ** | **0.285 pJ** |
| minimum-drive pool, VDD only | 0.086 pJ | 0.137 pJ | 0.239 pJ |
| x1 pool, VDD only | 0.105 pJ | 0.156 pJ | 0.258 pJ |

**Against the two things it can be checked on:**

| | pJ per flip |
|---|---|
| **This estimate, ASAP7 alone** | 0.13 – 0.28 (census mix, 1–4 fF per net) |
| **Q124, priced with the real cells** (`tfma.flip.energy`) | 0.11 – 0.13 |
| **E60, measured at the board** | 0.117 – 0.130 |
| **E60, measured at the minion rail** | 0.0875 – 0.0969 |

So **ASAP7 alone lands within about 1.0–2.2× of the real-cell figure, erring dear**, and the light
end of the net-load assumption (1 fF) sits right on Q124's top. That is the right order from a
predictive kit that knows nothing about the ET-SoC-1, and it is the first outside check on the
flip price.

**The dominant uncertainty is the per-net load, not the cells.** Going from 1 fF to 4 fF per net
moves the answer by 2.2×; swapping the whole cell mix moves it by 1.5×. A real extraction of the
unit's wires would settle it, and that is the gap this estimate leaves open.

Other things the estimate assumes, all listed in the JSON's `assumptions`: one toggling wire is one
cell-output transition; zero delay, like Q124's count, so no glitches (`tfma.glitch` puts the timed
tree at 1.5× the toggles and 1.4× the energy); the open synthesis made 7,967 cells for the
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
- The flip price has its first outside check: 0.13–0.28 pJ from open data against 0.11–0.13 pJ from
  the real cells and 0.117–0.130 pJ measured.
- Still open: the unit's real wire capacitances. Every number here is one extraction away from being
  a prediction rather than a bracket.
