# The transistor ledger: one switch, one net, one multiply-add, and Landauer's floor

**Request Q128(d). Monday 26 – Tuesday 27 October 2026 (week 44).** Run on **aifoundry2**, under
`nice`, in `$HOME/q128d` and `$HOME/q128dfix` — CPU only, no card, no `/dev/et*`. Everything here is **open data**:
ASAP7's own device models and cell netlists, the open synthesis and placement of the public RTL
([Q126(e)](../2026-10-26-open-netlist/)), and the card measurements already in this repository.

**What this answers.** The chain from "zeros run faster than random data" down to the chip has had
a gap at the bottom. [Q126(d)](../2026-10-26-asap7-cell-energies/) priced a *cell* per edge and
[part 2](../2026-10-26-asap7-one-switch/) ran its devices in SPICE, but nobody had put a number on
**one transistor switching**, nor said how much of a toggle's energy is transistor at all and how
much is wire. This closes that, and then carries it up: one device → one gate pin → one physical
net → one random fp32 multiply-add → the board → Landauer.

**Amended the same night, 22:45 PDT**, after a check against the committed files found four things, all
fixed here: the Landauer ladder was priced per *toggle* while §1 was priced per *rise*, exactly 2×
apart (§4 is now per rise throughout, and the convention table says which unit each section uses);
the unpriced share of the design's capacitance was printed as 50.5% when 50.5% is the *priced* share;
the short-circuit bound rested on a minimum that was never bracketed (34 more decks now bracket it);
and the attribution of E60's two board numbers is spelled out in §3, because another record on `main`
has them on the wrong card. No measured quantity moved.

## One convention, held throughout

| | |
|---|---|
| **Energy** | the energy **drawn from VDD** by one event, at **0.517 V** (the minion rail the open flow prices at) |
| **Electrons** | charge / e, with charge = energy / VDD and e = 1.602176634 × 10⁻¹⁹ C |
| **Cycle, toggle, rise** | a *cycle* is one rise plus one fall; a *toggle* is one edge; a *rise* is the 0 → 1 edge. A capacitance C takes **C·VDD² from the rail on the rise and nothing on the fall**, so a *toggle* — the per-edge average over a cycle — costs **½CV²**, which is exactly what Q126(e)'s power accounting charges, so the two agree by construction |
| 🛑 **which unit each section uses** | **§1 and §4's ladder price one rise**, because that is the event a device SPICE deck measures and the event anyone means by "one transistor switching". **§2's net table prices one toggle**, because that is the event the SAIF counts. The two differ by exactly 2×, every table says which it is, and §2 gives both. The totals in §3 are sums over a whole multiply-add and belong to neither |
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
| `gen_sc4.py`, `gen_sc5.py`, `parse_sc4.py`, `sc4.log`, `sc5.log`, `one-switch4.json` | 34 more decks that bracket the short-circuit minimum out to a 2 ns edge, measure the static leakage that has to come out of it, and measure the output edge this inverter actually delivers |
| `gen_pinq.py`, `parse_pinq.py`, `pinq.log`, `pinq-meta.json` | the per-cell pin-charge run on the 15 cell types this multiply-add actually drives |
| `one-switch3.json`, `pinq.json` | the first two SPICE runs, parsed |
| `fanout2.py`, `fanout2_randn_keep.json` | the DEF × capacitance × SAIF join: what one net toggle charges |
| `strip_logs.py` | takes ngspice's `Reference value :` progress chatter out of each log before it is committed; the parsers read the stripped files to the same digits |
| `check_page.py` | asserts every number printed on this page against the two JSONs — run it after any edit to either |

The ASAP7 kit is not committed: `../2026-10-26-asap7-one-switch/setup.sh` fetches it and builds
ngspice with OSDI. To re-run the arithmetic alone:

```
python3.12 -I ledger.py <repo root> one-switch3.json fanout2_randn_keep.json pinq.json \
           out.json one-switch4.json
python3.12 -I parse_sc4.py one-switch4.json one-switch3.json sc4.log sc5.log   # the sweep alone
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
average toggling signal net in this design carries**, 1.32 fF its pin half, 0.785 fF its wire half,
7.793 fF an average clock net, 0.596 fF one driven gate pin. (2.105 fF is the mean over **all**
20,383 extracted nets, which is what the decks were cut against; §2's headline row restricts to the
16,799 the DEF names and reads 2.233 fF. Both rows are in the JSON. Nothing here turns on which:
the two differ by 6%, and this table is about the *shape* of the split, not the net's exact size.)

**With a real net on it, an INVx1 costs 0.608 fJ per cycle — 7,337 electrons — and 92.6% of that is
the net, not the cell.** The 0 fF column is Q126(d)'s; the rest is this run, and it reproduces
Q126(d)'s own table where they overlap (0.0415 fJ at 0.596 fF against its 0.0407 at 0.5 fF;
0.0451 at 2.105 against its 0.0450 at 2 fF).

### The short-circuit share, at a real net's load, with the minimum bracketed

The same inverter at 2.105 fF, swept over input edge time. The first sweep went to 100 ps
(`one-switch3.json`) and at 0.517 V was **still falling at its slowest edge**, so its "2.5%" was the
spread over the edges sampled and not a bound on anything. The sweep was redone out to **2 ns**
(`one-switch4.json`, 34 more decks): one measurement window shared by every deck, 0.95 → 14.95 ns,
and the static leakage of each input state measured in its own deck and subtracted, because a slower
edge spends less of a fixed window in the steady state and that difference is the same size as the
term being measured. Rail energy per cycle, leakage out:

| input edge | 1 ps | 5 ps | 20 ps | 50 ps | 100 ps | 200 ps | 300 ps | 500 ps | 1 ns | 2 ns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **0.517 V**, fJ/cycle | 0.6090 | 0.6077 | 0.6035 | 0.5982 | 0.5937 | 0.5908 | **0.5905** | 0.5928 | 0.6047 | 0.6383 |
| above its own minimum | 3.0% | 2.8% | 2.2% | 1.3% | 0.5% | 0.05% | **—** | 0.4% | 2.3% | **7.5%** |
| **0.700 V**, fJ/cycle | 1.1259 | 1.1191 | 1.1041 | **1.0971** | 1.1090 | 1.1590 | 1.2228 | 1.3683 | 1.7771 | 2.6641 |
| above its own minimum | 2.6% | 2.0% | 0.6% | **—** | 1.1% | 5.3% | 10.3% | 19.8% | 38.3% | **58.8%** |

**Both curves are U-shaped and both minima are now inside the window: 300 ps at 0.517 V, 50 ps at
0.700 V.** Below the minimum the cost rises through gate–drain (Miller) coupling, above it through
short circuit — and that second arm is the whole difference between the two rails. At 0.700 V a 2 ns
edge costs **+59%**; at 0.517 V the same edge costs **+7.5%**, and the entire 1 ps – 2 ns range spans
7.5% of a cycle. 🛑 **So short circuit does not explain why one switch costs more than another at
the minion's rail; at 0.7 V it would.**

**And this design never gets near the slow arm.** The same INVx1 driving the same 2.105 fF puts out
an edge of **23.4 ps rising and 17.0 ps falling** (20–80%) — that is the input edge the next gate
actually sees, and it is the same 20–80% time as a linear ramp of 39 and 28 ps. Over 1–50 ps the
inverter sits **1.3 – 3.0% above its own minimum**, which is the honest size of short circuit plus
Miller together here: a couple of percent of a switch, the same couple of percent for every switch.

Three things check out. The extended run **reproduces the first sweep to 5 × 10⁻⁶ relative** at all
seven shared edges on both rails, once both are de-leaked with the measured currents (0.035 nA input
low, 0.043 nA input high at 0.517 V — 0.00028 fJ over the 14 ns window, 0.05% of a cycle, and exactly
the 0.0002 fJ by which the two runs' *raw* numbers differ). At 0.700 V and a 200 ps edge it reads
**+0.0620 fJ** against Q126(d)'s **+0.0639 fJ** at 2.0 fF. And Q126(d)'s headline **"+70% for a slow
edge"** is that same +0.064 fJ expressed over the cell's own *internal* energy (0.0875 fJ), not over
a cycle: the two runs agree, and what is new here is that the 0.517 V curve, which Q126(d) saw
falling out to 200 ps, turns at 300 ps and is still only 7.5% up at 2 ns.

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
| **energy per toggle** (½CV²) | **0.2985 fJ** | **1.0416 fJ** |
| **electrons per toggle** | **3,603** | **12,574** |
| *the same per rise* (C·V², §4's unit) | *0.5969 fJ, 7,206 electrons* | *2.0831 fJ, 25,149 electrons* |
| toggles per multiply-add | 3,106 (3,623 with the nets the DEF does not name) | 476.6 |

The two unit rows are one measurement in two units: a net that toggles *n* times rises *n*/2 times,
and (per toggle × toggles) = (per rise × rises) exactly. §3's **1.019 pJ** of signal switching is
that product over all 20,383 nets — 0.2814 fJ × 3,623 toggles, or 0.5627 fJ × 1,812 rises. The
per-rise row is the one that lines up with §1: **14.5 fins × 108 electrons = 1,565 against the net's
7,206 — 21.7%**, exactly the transistor share in the table.

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

🛑 **Both board numbers are E60's, and both are the same card.** `lq` 116.746 ± 0.613 fJ and `lb`
129.918 ± 0.480 fJ are the two ladders of E60's **aifoundry3** block —
[`reduce.txt`](../2026-10-20-bitflip-ladder/reduce.txt), 600 MHz, 521.8 mV, 4 passes each. They are
not two experiments and not two cards. aifoundry1's card 0 ran the same `lq` ladder at 800 MHz and
603.9 mV and read **102.490 ± 4.418 fJ**; E65's own flip, flow-M (`b` bit 11 against `a` = π), is
**745 ± 56 fJ** ([05-claims.md](../../../findings/05-claims.md)). `tools/claims-v3/sm/README.md`'s
amendment A6 of 26 Oct attributes 116.7 fJ to aifoundry1's card 0 at 800 MHz and 129.9 fJ to E65;
the attribution above is the one to quote. It is not bookkeeping: this page's electron counts all
divide by 0.517 V, which is 0.9% from aifoundry3's rail and 17% from aifoundry1 card 0's.

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

The 0.431 pJ of internal energy is Q126(e)'s `internal_estimate`: every signal transition priced at
Q126(d)'s census-weighted VDD-group internal energy, 0.1188 fJ at 0.517 V. It covers the 14,119
**combinational** cells' output transitions and skips the 1,953 flip-flops' and 13 clock gates' own
clock-pin energy, on a design whose clock is a third of the switching — so the "+ internal" column
everywhere above is itself a floor.

### Why the bottom-up number is a floor, three times over

1. **Half the capacitance is unpriced.** Only **50.5%** of the design's farads are priced here:
   23,762 fF of 47,093 fF are on nets the simulation can name, and the other **23,331 fF — 49.5%**
   — belongs to nets CTS and `repair_design` made after the netlist was simulated. They switch.
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

Every rung of the chain against the 66 °C floor. **Every single-edge rung is one rise** (0 → 1,
C·V² from the rail), which is the event §1 measures; the composite rungs below them are whole
events. The per-*toggle* figures of §2 are half the two net rungs, by definition:

| rung | energy | **× Landauer** | electrons |
|---|---:|---:|---:|
| one electron across the 0.517 V rail | 82.8 zJ | **25.5** | 1 |
| one minimum device's gate, isolated | 8.94 aJ | **2,755** | 108 |
| one transistor fin, driven inside a working cell | 9.42 aJ | 2,902 | 114 |
| one gate pin of the cells this unit drives | 57.3 aJ | 1.8 × 10⁴ | 692 |
| one **rise** of an average signal net (2.233 fF) | 0.5969 fJ | 1.8 × 10⁵ | 7,206 |
| one **rise** of an average clock net (7.794 fF) | 2.083 fJ | 6.4 × 10⁵ | 25,149 |
| one flipped operand bit, open netlist (`lq`) | 32.9 fJ | 1.0 × 10⁷ | 3.97 × 10⁵ |
| one flipped operand bit, E60 at the board | 116.7 fJ | 3.6 × 10⁷ | 1.40 × 10⁶ |
| E65's flow-M flip at the board | 745 fJ | 2.3 × 10⁸ | 9.0 × 10⁶ |
| one random fp32 multiply-add, bottom-up | 1.946 pJ | 6.0 × 10⁸ | 2.35 × 10⁷ |
| one random fp32 multiply-add, E38 at the board | 5.783 pJ | 1.8 × 10⁹ | 6.98 × 10⁷ |

**The cleanest statement of the floor is not a ratio but a factorisation.** Moving a single electron
across this chip's 0.517 V rail already costs **25.5 kT ln 2** at the die's 66 °C. The smallest
switch in the design moves **108 of them**. 25.5 × 108 = 2,755, and that is the whole distance from
Landauer to one transistor. Everything above it — the 14.5 fins a net drives, the wire that is four
fifths of a net, the **1,812 signal rises** a multiply-add makes (3,623 toggles), the clock tree, and
the 3× the board charges over the lane — is the other six orders of magnitude.

Neither factor is a thermodynamic limit. The 25.5 is the rail divided by kT; the 108 is a gate
capacitance, which is geometry. Both are design, and both are what the rest of this chain measures.
