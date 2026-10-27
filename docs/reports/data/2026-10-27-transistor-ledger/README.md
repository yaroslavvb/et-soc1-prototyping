# The transistor ledger: one switch, one net, one multiply-add, and Landauer's floor

**Request Q128(d). Monday 26 – Tuesday 27 October 2026 (week 44).** Run on **aifoundry2**, under
`nice`, in `$HOME/q128d` — CPU only, no card, no `/dev/et*`. Everything here is **open data**:
ASAP7's own device models and cell netlists, the open synthesis and placement of the public RTL
([Q126(e)](../2026-10-26-open-netlist/)), and the card measurements already in this repository.

**What this answers.** The chain from "zeros run faster than random data" down to the chip has had
a gap at the bottom. [Q126(d)](../2026-10-26-asap7-cell-energies/) priced a *cell* per edge and
[part 2](../2026-10-26-asap7-one-switch/) ran its devices in SPICE, but nobody had put a number on
**one transistor switching**, nor said how much of a toggle's energy is transistor at all and how
much is wire. This closes that, and then carries it up: one device → one gate pin → one physical
net → one random fp32 multiply-add → the board → Landauer.

## One convention, held throughout

| | |
|---|---|
| **Energy** | the energy **drawn from VDD** by one event, at **0.517 V** (the minion rail the open flow prices at) |
| **Electrons** | charge / e, with charge = energy / VDD and e = 1.602176634 × 10⁻¹⁹ C |
| **Cycle vs toggle** | a *cycle* is one rise plus one fall; a *toggle* is one edge. A capacitance C takes C·VDD² from the rail per cycle, so **½CV² per toggle** — which is exactly what Q126(e)'s power accounting charges, so the two agree by construction |
| **Temperature** | 25 °C for every SPICE number (ASAP7's TT corner). The die temperature enters only Landauer's floor, where it is stated |

🛑 **One convention this page does not share.** `docs/reports/data/2026-10-20-bitflip-ladder/reduce.txt`
prints its electron column as C·V/e, i.e. **2E/(V·e)** — the charge of the equivalent capacitor, not
the charge drawn per transition. Every electron figure of E60's that is quoted here is **halved** to
match the convention above, and both forms are in the JSON.

## Files

| File | What |
|---|---|
| `transistor-ledger.json` | every number on this page, with its provenance |
| `ledger.py` | builds that JSON from the three measurements below plus the committed card data |
| `gen_decks3.py`, `parse3.py`, `spice3.log` | the 50 SPICE decks: gate charge, the inverter by load, short circuit, a net as built |
| `gen_pinq.py`, `parse_pinq.py`, `pinq.log`, `pinq-meta.json` | the per-cell pin-charge run on the 15 cell types this multiply-add actually drives |
| `one-switch3.json`, `pinq.json` | the two SPICE runs, parsed |
| `fanout2.py`, `fanout2_randn_keep.json` | the DEF × capacitance × SAIF join: what one net toggle charges |
| `strip_logs.py` | takes ngspice's `Reference value :` progress chatter out of the two logs before they are committed; the parsers read the stripped files to the same digits |

The ASAP7 kit is not committed: `../2026-10-26-asap7-one-switch/setup.sh` fetches it and builds
ngspice with OSDI. To re-run the arithmetic alone:

```
python3.12 -I ledger.py <repo root> one-switch3.json fanout2_randn_keep.json pinq.json out.json
```

## 1. One transistor switching

One minimum-size ASAP7 RVT device — one fin, L<sub>g</sub> 20 nm — with its gate driven 0 → VDD
through a dedicated 0 V ammeter whose current is integrated into a 1 F capacitor. At **0.517 V**:

| device, drain held at | charge (aC) | **electrons** | **E from VDD (aJ)** | C<sub>gg</sub> (fF) |
|---|---:|---:|---:|---:|
| nmos, 0 | 17.85 | **111.4** | **9.23** | 0.0345 |
| nmos, VDD | 15.54 | 97.0 | 8.04 | 0.0301 |
| pmos, 0 | 16.69 | 104.1 | 8.63 | 0.0323 |
| pmos, VDD | 19.10 | 119.2 | 9.88 | 0.0369 |
| **mean of the four** | **17.30** | **108.0** | **8.94** | **0.0335** |

**So one transistor switching is about 110 electrons and 9 aJ.** The spread across the four cases is
1.23×, and it is the only honest error bar: where the drain sits when the gate moves changes the
charge by that much.

Two checks that the measurement is a capacitance and not an artefact:

- **it is linear in fins.** The same deck with `nfin=3` reads 53.56 aC against one fin's 17.85 —
  **3.0000×**. So "per fin" is the right unit, and a wider device is simply more of them.
- **the charge comes back.** The integrator returns to −1.0 × 10⁻²¹ C at the end of the falling
  edge, 6 × 10⁻⁵ of what went in. The gate loses nothing; the energy is lost in whatever drives it.

### The same fin inside a working cell

Measured at the input pin of the 15 cell types this multiply-add actually drives — the pin driven
0 → VDD through an ammeter, the other inputs held at 0 in one deck and at VDD in another, the
outputs loaded with 0.5 fF — and divided by the fins that pin gates in the CDL:

| | |
|---|---:|
| 47 (cell, pin) pairs × 2 hold states × 2 rails | 188 decks, **186 kept** |
| fins behind one driven pin, mix-weighted | **6.09** |
| charge into one driven pin | **110.9 aC** = 692 electrons |
| what the driver pays for that pin | **57.3 aJ** |
| **per fin** | **18.22 aC = 113.7 electrons = 9.42 aJ** |
| against the isolated device's static mean | **1.053×** |

(Two decks were dropped, and they are the same failure twice: `NOR2xp33`'s A and B pins at **0.7 V**
in the low hold state, where the DC solution puts the cell's internal node at −1,112 V. One aborted
with *"timestep too small"* and the other returned 2.3 × 10¹⁰ aC per fin. Both are named in the
JSON with their reason. **Every deck at 0.517 V converged**, which is the rail the ledger uses.)

**A fin in a working cell costs 5% more than the same fin measured alone**, and the per-hold-state
spread says why: it is **the Miller term, measured directly**. Across the 47 (cell, pin) pairs the
charge per fin runs 13.2 to 24.3 aC, and the ratio between the two hold states is

- **1.00 – 1.06** where the pin's edge cannot move the output in either state (`AO21x1`'s A1,
  `MAJx2`'s A and B) — that is the gate alone;
- up to **2.38** where it can (`OA211x2`'s B, `NAND2x1`'s B, `AND2x2`'s B);
- and exactly **1.00 at 24.31 aC per fin** for `INVx1`'s A, `BUFx2`'s A and `DFFHQx4`'s CLK — the
  three pins that drive a plain inverter stage, whose output *always* moves, so they carry the full
  Miller charge in both states and have no state to vary.

One more number falls out of the same run and §2 uses it: the **schematic** pin capacitance is
**0.370** of the **liberty's** pin capacitance, mix-weighted (range 0.24 – 0.46 across the 47 pins).
ASAP7's liberty was characterised on the parasitic-extracted netlist and this SPICE is the LVS
(schematic) one, so that ratio is what the cell's **own layout interconnect** adds to its
transistors — wire, inside the cell.

### The inverter per edge, with no load and with a real net

`internal = rail − C_load·V²`, in fJ per **cycle**, at 0.517 V:

| C_load | 0 fF | 0.596 fF | 0.785 fF | 1.32 fF | **2.105 fF** | 7.793 fF |
|---|---:|---:|---:|---:|---:|---:|
| rail, total | 0.0241 | 0.2008 | 0.2524 | 0.3970 | **0.6077** | 2.1293 |
| of which the load's CV² | 0 | 0.1593 | 0.2098 | 0.3528 | **0.5626** | 2.0830 |
| of which the cell's own | 0.0241 | 0.0415 | 0.0426 | 0.0442 | **0.0451** | 0.0463 |
| the cell's share | 100% | 20.7% | 16.9% | 11.1% | **7.4%** | 2.2% |

The loads are not round numbers because they are the ones §2 measures: **2.105 fF is what an
average toggling signal net in this design actually carries**, 1.32 fF its pin half, 0.785 fF its
wire half, 7.793 fF an average clock net, 0.596 fF one driven gate pin.

**With a real net on it, an INVx1 costs 0.608 fJ per cycle — 7,337 electrons — and 92.6% of that is
the net, not the cell.** The 0 fF column is Q126(d)'s; the rest is this run, and it reproduces
Q126(d)'s own table where they overlap (0.0415 fJ at 0.596 fF against its 0.0407 at 0.5 fF;
0.0451 at 2.105 against its 0.0450 at 2 fF).

### The short-circuit share, at a real net's load

The same inverter at 2.105 fF, swept over input edge time, rail energy per cycle above the
cheapest edge:

| input edge | 1 ps | 2 ps | 5 ps | 10 ps | 20 ps | 50 ps | 100 ps |
|---|---:|---:|---:|---:|---:|---:|---:|
| **0.517 V**, excess (fJ) | 0.0153 | 0.0149 | 0.0139 | 0.0124 | 0.0098 | 0.0044 | **0** |
| as a share of the cycle | 2.5% | 2.5% | 2.3% | 2.0% | 1.6% | 0.7% | — |
| **0.700 V**, excess (fJ) | 0.0288 | 0.0270 | 0.0221 | 0.0155 | 0.0070 | **0** | 0.0119 |
| as a share of the cycle | 2.6% | 2.4% | 2.0% | 1.4% | 0.6% | — | 1.1% |

🛑 **At 0.517 V the curve still falls monotonically out to a 100 ps edge**, so short circuit is not
separable from gate–drain (Miller) coupling by this method; what the table bounds is their sum, and
that sum is **at most 2.5% of the 0.608 fJ a real net costs**. Q126(d)'s "+70% for a slow edge" is
the **0.7 V** case at **2 fF** with a **200 ps** edge, and it does not describe this rail at this
load. On the question the chain asks — does short circuit explain why some switches cost more? — the
answer at the minion's rail is **no, not at the percent level**.

## 2. One physical-net toggle: what it charges

The placed design's own numbers, joined net by net: the **DEF** for fanout (the capacitance table
names nets hierarchically and the written Verilog is flat, so the Verilog misses 26% of them), the
**global-route Steiner estimate** for wire capacitance, ASAP7's **liberty** for pin capacitance, the
bench's **SAIF** for activity — read with Q126(e)'s own reader, so the weights are exactly the ones
behind its published 1.516 pJ.

The DEF names **16,799 of the 20,383 extracted nets**, and the signal row below is restricted to
those, so a net the DEF does not name cannot read as fanout 0 and drag the mean down; they carry
3,106 of the 3,623 signal toggles a random multiply-add makes, **86%**. The row that includes the
rest is in the JSON and reads 2.02 pins instead of 2.36 — a floor, not a second estimate.

The transistor share uses the **static** per-fin figure above (0.0335 fF), because the extractor's
pin column and the liberty behind it are static capacitances too. The larger in-cell figure of §1 is
real energy the driver pays, but it is Miller charge moving to the output, not capacitance sitting
on the net.

| per toggling net, activity-weighted | **signal nets** | **clock-tree nets** |
|---|---:|---:|
| gate pins driven | **2.36** | **9.56** |
| transistor fins behind those pins | **14.5** | **39.8** |
| total capacitance | **2.233 fF** | **7.794 fF** |
| — the transistor gates | 0.485 fF (**21.7%**) | 1.330 fF (**17.1%**) |
| — wire inside the cells | 0.892 fF (**39.9%**) | 3.343 fF (**42.9%**) |
| — wire between the cells | 0.856 fF (**38.3%**) | 3.121 fF (**40.0%**) |
| **energy per toggle** | **0.2985 fJ** | **1.0416 fJ** |
| **electrons per toggle** | **3,603** | **12,574** |
| toggles per multiply-add | 3,106 (3,623 with the nets the DEF does not name) | 476.6 |

**So about one fifth of what a toggle costs is transistor, and four fifths is wire** — and that is
the *generous* reading, because the between-cell capacitance is a Steiner estimate with no coupling
term (detailed routing never closed, Q126(e)), so the wire share is a floor and the transistor share
a ceiling.

**Two independent routes agree on it.** Route A is the table above: count the fins each net drives
and price every fin at the isolated device's 0.0335 fF. Route B never counts a fin — it takes the
whole pin capacitance from the extractor and multiplies by the measured **schematic ÷ liberty** pin
ratio of §1, 0.370. For signal nets they give **21.7%** and **22.8%**, 5% apart. For the clock tree
they give 17.1% and 22.2%, 23% apart, and route A is the one to quote there: route B's ratio was
measured on combinational cells while the clock drives flop CLK pins, which is a different mix.

Three checks, all exact:

| check | this join | Q126(e)'s own file |
|---|---:|---:|
| signal toggles per multiply-add | 3,623.361 | 3,623.361 |
| fJ per signal toggle (½CV² vs energy ÷ toggles) | 0.281357 | 0.281357 |
| total extracted capacitance | 47,093.21 fF | 47,093.21 fF |

and a fourth that the join is reading the right *pins*: on the nets the DEF names, the **sum of the
liberty's own input-pin capacitances reproduces the extractor's pin column to 0.2%** (1.380 against
1.377 fF, toggle-weighted). Over all 20,383 extracted nets it is 0.929 of it, and the 7% shortfall
is exactly the nets the DEF does not name.

## 3. The ledger: bottom-up against the board

**Per flipped operand bit.** The open netlist's ladder, fitted the way E60's reducer fits it (a line
over h ≥ 1 against the *designed* flip count, free intercept), against the card:

| | open netlist, switching | + the cells' internal | **E60 at the board** | at the rail (×0.75) | closure vs board | **closure vs rail** |
|---|---:|---:|---:|---:|---:|---:|
| `lq`, quiet partner A = 1.0 | 32.9 fJ | 46.3 fJ | **116.7 ± 0.6 fJ** | 87.5 fJ | 28% / 40% | **38% / 53%** |
| `lb`, busy partner A = π | 38.5 fJ | 54.9 fJ | **129.9 ± 0.5 fJ** | 96.9 fJ | 30% / 42% | **40% / 57%** |

E60's own rail column is 0.750 and 0.745 of its board column, which is where the chain's "≈ 0.75"
comes from; it is measured, not assumed.

**Per random fp32 multiply-add.**

| | pJ |
|---|---:|
| open netlist, switching | **1.516** |
| — of which the clock tree | 0.496 (32.7%) |
| — of which signal nets | 1.019 |
| the cells' own internal energy | 0.431 |
| **bottom-up total** | **1.946** |
| E38/E39 at the board, over idle, three-card mean | **5.783** |
| the same at the rail (×0.75) | 4.337 |
| **closure** | **26% / 34% of the board; 35% / 45% of the rail** |
| electrons, bottom-up | 23.5 million |
| electrons, at the board | 69.8 million |

And split by **what the energy charges**, which is the thing this request was for:

| | pJ per random multiply-add | share of the switching |
|---|---:|---:|
| transistor gates | **0.306** | **20.2%** |
| wire inside the cells | 0.620 | 40.9% |
| wire between the cells | 0.590 | 38.9% |
| *(the cells' own internal energy sits on top of all three)* | *0.431* | — |

**The answer to the chain's bottom question, in one line: of the 5.78 pJ the card pays for one
random fp32 multiply-add, about 0.31 pJ — roughly 5% — is charge going onto transistor gates in the
arithmetic.** The rest is wire inside the cells, wire between them, the clock tree, the cells' own
internal nodes, and everything outside the lane that the board pays for and this netlist does not
contain.

### Why the bottom-up number is a floor, three times over

1. **Half the capacitance is unpriced.** 23,762 fF of the design's 47,093 fF are on nets the
   simulation can name; the other 50.5% belongs to nets CTS and `repair_design` made after the
   netlist was simulated. They switch.
2. **The between-cell wire has no coupling term.** Detailed routing never closed, so there is no
   SPEF; the Steiner estimate is a lower bound on every wire.
3. **The ledger is one lane's arithmetic.** The board also pays for the register file's read ports,
   the operand bus, the result path, the accumulator and leakage.

Each of the three pushes the same way, which is why the closure ratios land where they do and why
they should be read as "the arithmetic is a minority of the bill", not as a discrepancy.

### What this does not close

**E65's per-position prices.** E65 measured 32 individual B-side bit positions (83 fJ at bit 6 to
1,008 fJ at bit 22) and the flow-M flip (`b` bit 11 against `a` = π) at **745 ± 56 fJ** at the board.
The open flow was only run on the ladder's own h = 0, 1, 2, 4, 8 rungs, so there is no like-for-like
bottom-up number for a *named* bit position yet. Running `mktiles.sh` on E65's own operand files
would give one, and it is the obvious next hour of work.

**The zeros pattern is not a closure check.** The open flow prices `zeros` at 0.217 pJ against E38's
0.27 pJ over idle, which looks like 80% agreement. It is not: the open flow's figure is the ungated
root of *this lane's* clock tree, which on a card is already inside the idle the measurement
subtracts. 🛑 Do not quote it as closure.

## 4. The floor: Landauer

kT ln 2, at the temperatures this chip actually runs at:

| | 25 °C (the SPICE corner) | 58 °C (E65's blocks) | **66 °C (the governor's trip)** | 80 °C (the leakage corner) |
|---|---:|---:|---:|---:|
| kT ln 2 | 2.853 zJ | 3.169 zJ | **3.246 zJ** | 3.379 zJ |

Every rung of the chain against the 66 °C floor:

| rung | energy | **× Landauer** | electrons |
|---|---:|---:|---:|
| one electron across the 0.517 V rail | 82.8 zJ | **25.5** | 1 |
| one minimum device's gate, isolated | 8.94 aJ | **2,755** | 108 |
| one transistor fin, driven inside a working cell | 9.42 aJ | 2,902 | 114 |
| one gate pin of the cells this unit drives | 57.3 aJ | 1.8 × 10⁴ | 692 |
| one toggle of an average signal net | 0.2985 fJ | 9.2 × 10⁴ | 3,603 |
| one toggle of an average clock net | 1.042 fJ | 3.2 × 10⁵ | 12,574 |
| one flipped operand bit, open netlist (`lq`) | 32.9 fJ | 1.0 × 10⁷ | 3.97 × 10⁵ |
| one flipped operand bit, E60 at the board | 116.7 fJ | 3.6 × 10⁷ | 1.40 × 10⁶ |
| E65's flow-M flip at the board | 745 fJ | 2.3 × 10⁸ | 9.0 × 10⁶ |
| one random fp32 multiply-add, bottom-up | 1.946 pJ | 6.0 × 10⁸ | 2.35 × 10⁷ |
| one random fp32 multiply-add, E38 at the board | 5.783 pJ | 1.8 × 10⁹ | 6.98 × 10⁷ |

**The cleanest statement of the floor is not a ratio but a factorisation.** Moving a single electron
across this chip's 0.517 V rail already costs **25.5 kT ln 2** at the die's 66 °C. The smallest
switch in the design moves **108 of them**. 25.5 × 108 = 2,755, and that is the whole distance from
Landauer to one transistor. Everything above it — the 14.5 fins a net drives, the wire that is four
fifths of a toggle, the 3,623 toggles a multiply-add makes, the clock tree, and the 3× the board
charges over the lane — is the other six orders of magnitude.

Neither factor is a thermodynamic limit. The 25.5 is the rail divided by kT; the 108 is a gate
capacitance, which is geometry. Both are design, and both are what the rest of this chain measures.
