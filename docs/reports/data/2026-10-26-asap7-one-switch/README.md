# One switch, in SPICE: ASAP7's transistors at 0.517 V and 0.7 V

**Request Q126(d), part 2 (Track D of the 20 October "speed to atoms" plan). Monday 26 October
2026 (week 44).** Run on **aifoundry2**, under `nice`, in `$HOME/q126d` — CPU only, no card, no
`/dev/et*`, nothing private on the box. Part 1, the same cells priced from the liberty, is
[`../2026-10-26-asap7-cell-energies/`](../2026-10-26-asap7-cell-energies/).

> **Corrected the same day, after review**, with a second SPICE run of 28 decks
> (`decks-fixups/`, `spice-run-fixups.log`). Two claims in the first version did not survive it: that
> the device models matched the ASAP7 paper "within about 5%" (true of the drive currents, not of
> the off-currents), and that every SPICE energy here is a *device-only lower bound* because
> parasitics double it (a delay ratio carried across to energy on the strength of one cell; measured
> properly it goes both ways). See [What the first version got
> wrong](#what-the-first-version-got-wrong).

What this answers: what one transistor actually costs when it switches, measured on ASAP7's own
BSIM-CMG device models and its own cell netlists, at the minion's 0.517 V and at the library's
0.7 V — the energy per edge by load, how far that moves with the cell's hold state, the
short-circuit energy against input edge time, leakage per device at 25 and 80 °C, the delay, and
whether 0.517 V sits above V_tn + |V_tp|.

## Files

| File | What |
|---|---|
| `setup.sh` | the whole toolchain, in user space: build ngspice with OSDI, fetch the BSIM-CMG OSDI, convert ASAP7's cards and netlists |
| `mkmodels.py` | HSPICE `level = 72` → the OSDI module `bsimcmg_va`, `TYPE = ±1` |
| `gen_decks.py` | writes the 60 decks of the first run |
| `gen_decks2.py` | writes the 28 decks of the review fix-up run |
| `parse_spice.py` | turns both runs' text into `asap7-one-switch.json` |
| `decks/`, `decks-fixups/` | the decks as run, plus their `runall` scripts |
| `spice-run.log`, `spice-run-fixups.log` | the runs' output, with the simulator's progress lines stripped |
| `asap7-one-switch.json` | every number |

The kit itself is **not** committed here: `setup.sh` fetches ASAP7 and the OSDI library. To re-parse:

```
python3.12 -I parse_spice.py spice-run.log <outdir> \
                             spice-run-fixups.log \
                             ../2026-10-26-asap7-cell-energies/asap7-cell-energies.json
```

## Getting an engine to load the models

This was most of the work, so it is written down. ASAP7 ships its devices as an **HSPICE BSIM-CMG
card** (`models/hspice/7nm_TT_160803.pm`, `.model … level = 72`, version 107). Four routes were
tried:

| Route | Result |
|---|---|
| ngspice's built-in device levels | **No.** ngspice has no BSIM-CMG: this binary supports levels 1–6, 8–10, 14, 49, 54–58, 60, 68, 73. BSIM-CMG is only reachable through OSDI. |
| Xyce from conda-forge | **No.** There is no `xyce` package on conda-forge, for osx-64 or linux-64. |
| OpenVAF from conda-forge, or a GitHub release | **No.** No conda-forge package; neither `pascalkuthe/OpenVAF` nor `arpadbuermen/OpenVAF` publishes release assets. |
| **ngspice + a prebuilt BSIM-CMG OSDI** | **Yes**, with one platform catch. |

The catch: Homebrew's macOS **ngspice 47 does have OSDI** (`pre_osdi` works), but the only prebuilt
BSIM-CMG OSDI — `dwarning/VA-Models` v2.2, `VA-Models-osdilibs.tar.gz` — is an **ELF x86-64 shared
object**, so it cannot load on macOS. And conda-forge's **Linux ngspice 41 is built without OSDI**
(`pre_osdi: no such command`). So the one working combination is **ngspice built from source on
Linux with `--enable-osdi`**, which is what `setup.sh` does (it needs `--with-readline=no`; the
headers are absent on aifoundry2 and batch mode does not want them).

Two conversions are then needed, and both are easy to miss:

- **The model card.** `.model nmos_rvt nmos level = 72` becomes `.model nmos_rvt bsimcmg_va TYPE=1`
  (`TYPE=-1` for pmos). Five parameters are **ignored by the OSDI model** and ngspice says so:
  `version`, `coremod`, `capmod`, `nseg`, `etaqm`. The OSDI library is BSIM-CMG **111.1.0** while
  ASAP7's card is written for **107**, which is why. The device check below is what makes this
  acceptable, not an assumption.
- **The cell netlists.** ngspice binds an OSDI device to an instance name starting with **`N`**, not
  `M`, and `bsimcmg_va` has **no `w` parameter** (it sizes by `nfin`). So the CDL needs
  `sed -e 's/^M/N/' -e 's/ w=[0-9.]*[munp]//'`.

## The device check: do the models run as the kit intends?

One fin of each RVT device, TT, swept in DC, against the paper's own Tables 3 and 4
(`asap7_pdk_r1p7/docs/mej_paper_asap7.pdf`):

| per fin, RVT | SPICE 25 °C | **paper, TT 25 °C** | error | SPICE 80 °C |
|---|---:|---:|---:|---:|
| I_dsat NMOS (µA) | 35.87 | **37.85** | −5.2% | 34.60 |
| SS NMOS (mV/decade) | 61.8 | **63.03** | −2.0% | 73.2 |
| I_dsat PMOS (µA) | 31.86 | **32.88** | −3.1% | 30.10 |
| I_off NMOS (nA) | 0.0173 | **0.019** | **−8.9%** | 0.1240 |
| I_off PMOS (nA) | 0.0186 | **0.023** | **−19.1%** | 0.2752 |

**The drive currents and the subthreshold slope land within 5%; the off-currents do not — 9% and
19% under.** The paper prints I_off to two significant figures, and an off-current is exponentially
sensitive to the threshold, so a disagreement of that size is expected rather than alarming. But it
is not 5%, and **the leakage section below is built on those off-currents**, so the wider tolerance
travels with it. With that said, the models are loading and running as ASAP7 intends, despite the
five ignored parameters and the 107-vs-111 version gap.

The 80 °C column is a result in its own right: **the subthreshold slope goes from 61.8 to
73.2 mV/decade** — the thermal limit tracking temperature, 60 mV/decade at 300 K becoming about 70
at 353 K — and **I_off rises 7.2× (NMOS) and 14.8× (PMOS)** for a 55 K rise.

## FO4, and the 8.1 ps question

A proper FO4 chain (every stage loaded with four INVx1, so the DUT sees the slew a real chain
settles at), 50%-to-50% delay:

| | 0.7 V | 0.517 V |
|---|---:|---:|
| **FO4, SPICE on the LVS netlist** | **9.63 ps** | **16.74 ps** |
| FO4, from the liberty (part 1) | 19.60 ps | — |
| output slew, 10–90% (rise/fall) | 14.4 / 12.3 ps | 22.7 / 18.4 ps |

The brief for this request quoted "about 8.1 ps RVT at 0.7 V" and part 1 could not find it in the
liberty. **Both numbers are right, about different netlists.** The CDL here is the **LVS
(schematic) netlist** — transistors only, no interconnect parasitics — and gives 9.63 ps, the same
class as 8.1. ASAP7's liberty was characterised on the **parasitic-extracted** netlist and gives
19.60 ps, so **the parasitics roughly double the delay (2.04×)**. Anyone quoting an ASAP7 FO4 has to
say which netlist it came from.

🛑 **That 2.04× is a DELAY ratio and nothing else.** It has no measured energy counterpart — see the
next section, where the energy comparison was actually done and came out near 1.0, both ways.

Dropping 0.7 V → 0.517 V costs **1.74× in delay**, which is the price the minion pays for its rail.

## Energy per edge, by load

Measured by integrating the DUT's own VDD current with a dedicated 0 V ammeter (the driver is a
separate supply), over a full cycle. `internal = rail − C_load·V²`, in fJ per **cycle** (one rise
and one fall):

| cell (state) | V | 0 fF | 0.5 fF | 1 fF | 2 fF | 4 fF | 8 fF |
|---|---|---:|---:|---:|---:|---:|---:|
| INVx1 | 0.700 | 0.0431 | 0.0709 | 0.0805 | 0.0875 | 0.0917 | 0.0940 |
| INVx1 | 0.517 | 0.0241 | 0.0407 | 0.0434 | 0.0450 | 0.0459 | 0.0464 |
| NAND2x1 (B = 1) | 0.700 | 0.2207 | 0.2381 | 0.2445 | 0.2497 | 0.2532 | 0.2552 |
| NAND2x1 (B = 1) | 0.517 | 0.1112 | 0.1174 | 0.1190 | 0.1201 | 0.1208 | 0.1211 |
| FAx1 A→SN (**B = CI = 0**) | 0.700 | 0.3150 | 0.3209 | 0.3227 | 0.3241 | 0.3248 | 0.3251 |
| FAx1 A→SN (**B = CI = 0**) | 0.517 | 0.1518 | 0.1533 | 0.1537 | 0.1539 | 0.1539 | 0.1537 |

The hold state belongs in the row label, because **a full adder's arc energy moves 1.8× with it**
(2 fF, internal fJ per cycle):

| FAx1, A toggling | B=0 CI=0 | B=0 CI=1 | B=1 CI=0 | B=1 CI=1 |
|---|---:|---:|---:|---:|
| 0.700 V | 0.3241 | 0.5556 | 0.5710 | 0.3148 |
| 0.517 V | 0.1539 | 0.2717 | 0.2808 | 0.1491 |

The two dear states are the ones where **the carry-out CON follows A as well as SN does**: with
exactly one of B, CI high, carry = A, so the cell delivers two output transitions instead of one.
The liberty says the same thing structurally — it carries an `A→CON` arc for exactly those two
states and none for the other two.

At 2 fF the **total** rail energy per cycle is 1.0675 fJ for INVx1 at 0.7 V (9,518 electrons) and
0.5796 fJ at 0.517 V (6,997 electrons) — the load dominates, exactly as ½CV² says it should.

The internal energy is nearly flat in load — it is the cell's own drain and internal-node
capacitance, not the load. At C_load = 0 and 0.7 V, INVx1's 0.0431 fJ per cycle implies a self-load
of **0.088 fF** (schematic only).

## What SPICE settles about the liberty

🛑 **1. The factor of two: the VDD group alone is the rail energy.** ASAP7's liberty splits each
internal-power event between VDD and VSS. For INVx1 at 2 fF and 0.7 V the two readings are
0.0974 fJ per cycle (VDD group alone) and 0.195 fJ (the two summed). **SPICE measures 0.0875 fJ**,
10% under the VDD-only reading and less than half the summed one. So **the VDD group alone is the
energy drawn from the rail**, and summing the pg-pin groups double-counts the same charge in through
VDD and out through VSS. Part 1's flip price and every per-toggle number derived from a liberty
should use it.

**2. The schematic netlist is *not* a general lower bound on the extracted one.** With the arc, the
`when` state and the set of outputs driven all matched — the full adder's mixed states need
`A→SN` **and** `A→CON` summed — eight cases at 0.7 V and 2 fF:

| cell, input, state | SPICE (fJ/cycle) | liberty, VDD only | SPICE / liberty |
|---|---:|---:|---:|
| INVx1 A | 0.0875 | 0.0974 | 0.90× |
| NAND2x1 A, B = 1 | 0.2497 | 0.2710 | 0.92× |
| FAx1 A, (!B·CI) | 0.5556 | 0.5866 | 0.95× |
| FAx1 A, (B·!CI) | 0.5710 | 0.5906 | 0.97× |
| XOR2x1 A, B = 0 | 0.6609 | 0.6519 | 1.01× |
| FAx1 A, (!B·!CI) | 0.3241 | 0.2719 | 1.19× |
| FAx1 A, (B·CI) | 0.3148 | 0.2574 | 1.22× |
| XOR2x1 A, B = 1 | 0.4531 | 0.3329 | 1.36× |

**It goes both ways, 0.90× to 1.36×, with no systematic sign.** The honest statement is that the
schematic netlist and the parasitic-characterised liberty agree on energy to within about ±35% per
case — not that one bounds the other, and not that the 2.04× delay ratio has an energy twin.

(The decks drive a 5 ps input edge against the liberty's 10 ps slew; the short-circuit sweep puts
that at under 0.01 fJ per cycle for INVx1, which flips no row's sign.)

**3. Scaling internal energy by V² is conservative.** Part 1 scales 0.7 V → 0.517 V by
(0.517/0.7)² = **0.5455**. SPICE measures **0.474 to 0.515** for the same eight cases, so the real
fall is 6–13% steeper: the short-circuit and internal-node terms drop faster than V², as the
short-circuit sweep below also shows. Part 1's 0.517 V column therefore errs slightly high, in the
direction it already warned about.

## Short circuit, and whether 0.517 V closes it

**It does not close.** For ASAP7 RVT, V_tn + |V_tp| = **0.33 V** (saturation thresholds) or
**0.38 V** (linear). The minion's 0.517 V is well above both, so both devices can conduct during an
input edge.

But the cost is strongly suppressed at the lower rail. An INVx1 with a 2 fF load, driven by an ideal
edge of a stated length, rail energy per cycle above the cheapest edge:

| input edge | 1 ps | 2 ps | 5 ps | 10 ps | 20 ps | 50 ps | 100 ps | 200 ps |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **0.700 V** (fJ) | +0.0291 | +0.0272 | +0.0221 | +0.0153 | +0.0067 | 0 | +0.0126 | **+0.0639** |
| **0.517 V** (fJ) | +0.0184 | +0.0180 | +0.0170 | +0.0154 | +0.0127 | +0.0072 | +0.0028 | **0** |

At **0.7 V the curve is U-shaped**: very fast edges cost extra through gate–drain (Miller) coupling,
and slow edges through short circuit, with a minimum near 50 ps. A 200 ps edge costs **+0.064 fJ per
cycle, about 70% on top of that inverter's 0.0875 fJ of internal energy.**

At **0.517 V there is no rise at all out to a 200 ps edge** — the curve falls monotonically. The
overlap window is (0.517 − 0.33)/0.517 = **36% of the swing** against (0.7 − 0.33)/0.7 = **53%** at
0.7 V, and the devices are far weaker there. So running at the minion's rail does not eliminate
short-circuit energy, but on these devices it does make it negligible for any edge a real design
would have. That is a point for the "why some switches cost more" stop: **the short-circuit slider
matters at 0.7 V and essentially stops mattering at 0.517 V.**

This is measured as excess rail energy over the cheapest edge, not as overlap current directly: the
VSS charge during an output rise turns out to be dominated by the falling input's gate coupling. A
direct overlap-current measurement would be cleaner if the number ever has to be precise rather
than bounded.

## Leakage, per device and per cell

`.op` with the input held, both states of INVx1, and one fin of each device:

| | 0.700 V, 25 °C | 0.700 V, 80 °C | 0.517 V, 25 °C | 0.517 V, 80 °C |
|---|---:|---:|---:|---:|
| INVx1, state-averaged (pW) | **37.00** | **418.52** | **20.35** | **257.43** |
| NMOS, 1 fin (pW) | 12.13 | 86.80 | 6.09 | 54.52 |
| PMOS, 1 fin (pW) | 13.04 | 192.66 | 7.64 | 117.17 |

The liberty's INVx1 figure is 51.2 pW at 0.7 V and 25 °C against SPICE's 37.0. Carry the
off-current tolerance from the device check with these: the PMOS off-current runs 19% under the
paper's.

**Leakage does not scale as V².** Dropping 0.7 V → 0.517 V (a factor 1.35 in voltage, 1.84 in V²)
cuts INVx1's leakage only 1.82× at 25 °C and 1.63× at 80 °C. And **80 °C costs 11.3× at 0.7 V and
12.6× at 0.517 V** over 25 °C — this is the term that makes the card's idle power a temperature
problem.

**Beside the card.** The ET-SoC-1 leaks **23.3 W at 80 °C** ([finding
16](../../findings/16-dvfs-and-leakage.md)) over about 24 billion transistors, which is
**0.97 nW per transistor**. ASAP7 RVT at 0.517 V and 80 °C leaks **129 pW per transistor** (INVx1's
257 pW over its two devices). The card is **7.5× leakier per transistor** than an all-RVT ASAP7
design would be. That gap is a real finding, not an error: the chip is certainly not all-RVT (the
paper's own table has LVT leaking 12× and SLVT 130× RVT's I_off), parts of the die run hotter than
80 °C, and the 24 billion count includes SRAM. It does say that **the leakage term cannot be
modelled with one device flavour**, which the power model will have to carry.

## What this gives the Horace model

1. **The liberty convention is settled**: VDD-group-only is the rail energy. Part 1's flip price and
   every per-toggle number derived from a liberty should use it.
2. **A sourced price per edge** for the inverter, the NAND and the full adder, at both rails, by
   load and — for the adder — by hold state, from device physics rather than a table.
3. **The schematic netlist and the liberty agree on energy to ±35%, both ways**, over eight matched
   cases. There is no measured energy counterpart to the 2.04× delay gap, so SPICE here is a
   cross-check on the liberty, not a bound below it.
4. **The V² voltage rule is conservative by 6–13%** on internal energy.
5. **The short-circuit slider is quantified**: up to +70% at 0.7 V for a slow edge, negligible at
   0.517 V, and 0.517 V is *not* below V_tn + |V_tp|.
6. **Leakage has its voltage and temperature law measured**, and the card is 7.5× leakier per
   transistor than all-RVT ASAP7 — a flag for the model, and a question for the vault.
7. **State matters inside a cell**: a full adder's own arc energy spans 1.8× across its four hold
   states, which is the same size as the whole spread between gate kinds. A power model that prices
   a cell by type alone is leaving that on the table.

**What is still missing.** The parasitic-extracted netlist (`CDL/xAct3D_extracted/`) ships with the
kit as a hierarchical Calibre PEX deck and was not run here for time. It would say directly what
the eight-case comparison above can only bound, and it needs no card. Gate leakage still has no
number either: the ASAP7 paper gives none (its I_off is drain current at V_gs = 0) though the
BSIM-CMG cards enable it (`igcmod = 1`), so it wants a dedicated gate-current sweep.

## What the first version got wrong

Both were found in review on the same day and settled by the 28-deck fix-up run, not by argument.

**1. "Every figure is within about 5% of the paper's" was false for the off-currents** — 8.9% (NMOS)
and 19.1% (PMOS). The validation still stands, but the tolerance is per quantity, and the leakage
section depends on exactly the figures with the wider error. Restated above and in the JSON's
`device_check.deviation_vs_paper_25C`.

**2. "Every SPICE energy here is a device-only lower bound" was a generalisation from one cell, and
it is wrong.** The 2.04× is a *delay* ratio between the schematic and extracted netlists; the only
energy gap the first version actually measured was INVx1's 10%, and it read a factor 1.1 as
evidence for a factor 2. Measuring seven more cases, with the state and the driven outputs matched,
gives 0.90× to 1.36× **in both directions**. The extracted netlist was never run, so nothing here
can be called a bound on it.

**3. Two smaller things, same review.** The FAx1 energy decks hung `Ccout = 0.5 fF` on the carry-out
pin, which `internal = rail − C_load·V²` never subtracted, so charge reaching CON was booked as
FAx1's internal energy. Re-run with that load removed, the error turns out to be **+0.0007 fJ per
cycle at 0.7 V, 0.2%** — real but negligible; the table above now uses the clean numbers. (CON is
the *inverted* carry, so with B = CI = 0 it sits high and only glitches, 0.631 to 0.767 V.) And the
FAx1 row never said which hold state it was: it was B = CI = 0, the cheapest of four, and the state
now appears in the label with the full 1.8× spread beside it.
