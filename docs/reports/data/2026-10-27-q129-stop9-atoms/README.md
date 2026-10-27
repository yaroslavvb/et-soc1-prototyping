# Atoms, the floor: where a flip's half-CV-squared becomes heat, and what "25,000×" was

**Request Q129, stop 9 of the Horace chain. Tuesday 27 October 2026 (week 44).** A **desk note**: no
card, no `/dev/et*`, no pre-registration, nothing measured here. Every number is either a physical
constant, a figure already published in this repository (Q124/Q126/Q128, E38/E60/E63/E65), or a value
read out of the public literature and cited in [§8](#8-references). The arithmetic is in
[`atoms.py`](atoms.py) and its output in [`atoms.json`](atoms.json); `python3 atoms.py` reproduces
every number below.

**What this answers.** Stop 9 of the chain — the bottom of
[*From matmul speed to one transistor switch*](../2026-10-27-matmul-to-transistor/) — was marked
*missing* on four counts: **phonons, the fin's self-heating, materials, and "the 25,000×"**. The
public page [*Why a flip makes heat: following the electrons*](https://spacesheep.dev/@yaroslavvb/et-soc1-why-a-flip-makes-heat) already walks the
½CV² split, the inverter electron by electron, and a Landauer ladder. This note does **not** repeat
that. It goes one level down: *where in the lattice the energy lands, how long it stays there, how far
it has to travel, and which of the three Landauer ratios the pages print is the right one.*

## Results first

1. **"25,000×" is reproduced exactly and is wrong anyway.** It comes from the 20 Oct plan's §3.4 and
   rests on the 16 Oct outline's ruler rung *"minimum inverter input, 83 aJ, 2,000 e⁻"*. That implies
   **C = 0.621 fF**, a pre-measurement guess: it is **18.5×** the gate capacitance Q128 then measured
   for one minimum ASAP7 device (0.0335 fF), **9.3×** a whole INVx1 input pin, and **0.28×** the design's
   average signal net. The two defensible replacements are **2,645×** (a bare INVx1 pin, heat per edge,
   80 °C floor) and **88,300×** (an INVx1 toggling the design's average signal net). The plan's own
   *formula* — ½CV²/kT ln 2 = (CV/e)·(eV/kT)/(2 ln 2) — is right; only the C was invented.
2. **2,755×, 1,410× and 25,000× are one number under three conventions.** [§2](#2-the-25000-found-reproduced-corrected)
   is the table that reconciles them: the ratio is always *(electrons) × (eV/kT ln 2) × (1 for energy
   drawn per rise, ½ for heat per edge)*, and the floor moves 18% between 25 °C and 80 °C.
3. **Each electron sheds about four of silicon's optical phonons on each edge, eight over a cycle.**
   Silicon's zone-centre mode is **64.6 meV (15.6 THz)**, and 0.517 V ÷ 64.6 meV = **8.01**. The plan's
   "about eight per electron" is right *for a full cycle*; per edge it is four, because an electron
   falls only half the rail on average. One toggle of an average net is **28,900 optical phonons**; one
   random fp32 multiply-add is **4.2 × 10⁸** on the minion rail, or **1.9 × 10²¹ a second** at 9.18 TFLOPS.
4. **99.5% of a flip's heat is born inside transistor channels, although 80% of the capacitance is
   wire.** The between-cell wire of an average net is ~5.2 µm at ASAP7's 26.6 Ω/µm = **137 Ω**, against
   **14.4 kΩ** for one minimum fin's on-resistance at 0.517 V. The wire decides *how much* heat a flip
   makes; the transistor decides *where it is born*. The crossover is at roughly **1 mm** of tightest
   metal for a one-fin driver.
5. **The fin's self-heating cannot be felt by one flip.** Published 3-D simulation of a 7 nm-class bulk
   FinFET gives **R_th = 1.05 K/mW** (1,050 K/W) rising to 1.10 at 350 K. One fin carrying full I_dsat at
   0.517 V (18.5 µW) heats itself **19.5 mK**; an average net toggling at 10% activity at 800 MHz is
   **50 µK**. Measurements put FinFET self-heating's time constant "on the order of nanoseconds", which
   is **far longer than this design's 17–23 ps edges** — so a switching event is adiabatic with respect
   to the fin's heat path, and its transient is set by heat capacity, not by thermal resistance.
6. **The ps → ns → µs → ms ladder is calculable, and it rules the camera out of the die.** The die's own
   vertical path is **0.25 ms** and one shire's lateral spread **11 ms** — 10³ to 10⁵ times faster than the
   camera's 0.05–0.15 Hz lock-in. **E63 and Q126's second frequency are reading the board, not the die**,
   which agrees with E63's own conclusion (τ ≥ 3.2 s, no upper bound; more phase than one pole can give).
   A lock-in that could resolve the die's path would have to run near **1 kHz**.

🛑 **This moves no picojoule from "unaccounted" to "accounted".** Stop 9 sits *below* Q128's ledger: it
explains where the already-counted ½CV² goes once it is spent, not where the missing 3.837 pJ comes
from. What it changes is listed in [§7](#7-what-this-changes).

## 1. One convention, taken from Q128

Identical to [the transistor ledger](../2026-10-27-transistor-ledger/#one-convention-held-throughout),
and worth restating because it is exactly what the three Landauer ratios disagree about:

| | |
|---|---|
| **a rise** | the 0 → 1 edge. The rail delivers **C·V²**; the node keeps ½CV² and the pull-up dissipates ½CV² |
| **a fall** | the 1 → 0 edge. The rail delivers nothing; the stored ½CV² goes to ground through the pull-down |
| **heat per edge** | **½CV²**, either edge, always |
| **the floor** | kT ln 2 at the die temperature. 2.853 zJ at 25 °C, **3.169 at 58 °C** (E60/E65's launch), **3.246 at 66 °C** (the governor's trip), 3.380 at 80 °C |
| **electrons** | charge ÷ e, charge = (energy drawn) ÷ V, at V = 0.517 V |

## 2. The 25,000×: found, reproduced, corrected

**Where it is.** The Horace Hub's Levels tab, stop 9, column *Missing*: "the 25,000×". Its definition is
the 20 Oct plan's **§3.4, "Why a switch costs 25,000 times Landauer's floor"**, which reads:

> ½CV² ÷ kT ln 2 = (CV/e) × (eV/kT) ÷ 2 ln 2. For a minimum inverter at 0.517 V and 80 °C that is
> 2,000 electrons × 17 kT each ÷ 1.39 ≈ **24,500**.

**It reproduces.** 2,000 × (0.517 / 0.030434) / (2 ln 2) = **24,509**; taking the ruler's 83 aJ directly
against the 80 °C floor gives **24,559**. Both match the quoted 24,500, and eV/kT at 80 °C is 16.99, the
plan's "17 kT". The arithmetic is sound.

**It is still wrong, because its C was never measured.** 83 aJ of heat per edge at 0.517 V implies
C = 0.621 fF, and 2,000 electrons implies 0.620 fF — self-consistent, and sourced to nothing. Six days
later Q128 measured the parts:

**The table.** Every Landauer ratio these pages print, in one place. `×` is energy ÷ kT ln 2 at the
floor named; *rise* prices C·V² drawn, *edge* prices ½CV² of heat.

| event | energy | e⁻ | convention | floor | **× floor** | factorisation |
|---|---:|---:|:--|---:|---:|:--|
| one electron across the 0.517 V rail | 82.8 zJ | 1 | rise | 66 °C | **25.5** | — |
| one minimum device's gate (C = 0.0335 fF) | 8.94 aJ | 108 | rise | 66 °C | **2,754** | 108 × 25.5 |
| the same gate, heat per edge | 4.47 aJ | 108 | edge | 58 °C | **1,410** | 108 × 26.1 ÷ 2 |
| an INVx1's own input pin, 2 fins | 8.94 aJ | 216 | edge | 80 °C | **2,645** | 216 × 24.5 ÷ 2 |
| 🛑 *the plan's row*: "minimum inverter", C **assumed** 0.621 fF | 83 aJ | 2,000 | edge | 80 °C | **24,559** | 2,000 × 24.5 ÷ 2 = 24,509 |
| **corrected**: an INVx1 toggling the average signal net (2.233 fF) | 0.2984 fJ | 7,206 | edge | 80 °C | **88,310** | 7,206 × 24.5 ÷ 2 |
| one rise of that net | 0.5969 fJ | 7,206 | rise | 66 °C | **1.84 × 10⁵** | 7,206 × 25.5 |
| one rise of an average clock net (7.794 fF) | 2.083 fJ | 25,149 | rise | 66 °C | **6.42 × 10⁵** | 25,149 × 25.5 |
| one flipped MAC input bit, a = 1.0, board (E60) | 116.7 fJ | — | event | 66 °C | **3.60 × 10⁷** | — |
| E65's flow-M flip, board | 745 fJ | — | event | 66 °C | **2.30 × 10⁸** | — |
| one random fp32 MAC, bottom-up (Q128) | 1.946 pJ | — | event | 66 °C | **6.00 × 10⁸** | — |
| one random fp32 MAC, board (E38) | 5.783 pJ | — | event | 66 °C | **1.78 × 10⁹** | — |

The `e⁻` column is always **charge drawn on the rise** ÷ e, so an *edge* row's factorisation carries the
÷ 2. Three rounding notes, so nobody chases a last digit: Q128 prints the second row as **2,755** and the
flip-heat page prints the third as **1,410** (exact values 2,754.0 and 1,410.5); and the plan's rung is
0.2% inconsistent with itself — 83 aJ implies C = 0.621 fF while 2,000 e⁻ implies 0.620 fF — which is the
whole gap between 24,559 and the plan's own 24,509.

**Three ways the same event's ratio moves, none of them physics.** Pricing one minimum gate at four
floors and two conventions spans 1,323× to 3,134× — a factor of 2.4 — with no change in the device:

| | 25 °C | 58 °C | 66 °C | 80 °C |
|---|---:|---:|---:|---:|
| the gate, per **rise** (C·V²) | 3,134 | 2,821 | **2,754** | 2,645 |
| the gate, **heat per edge** (½CV²) | 1,567 | **1,410** | 1,377 | 1,323 |
| an average net, **heat per edge** | 1.05 × 10⁵ | 9.42 × 10⁴ | 9.20 × 10⁴ | **8.83 × 10⁴** |

**The recommendation for the post.** Drop "25,000×" and say the two ends: *a bare minimum transistor's
gate costs about 2,700 times Landauer's floor; a real inverter driving a real wire in this design costs
about 90,000*. Then give the plan's own factorisation, which is the only part that teaches anything:
**25.5 (the rail ÷ kT) × 108 (electrons on one gate)**, and note that neither factor is thermodynamic.

## 3. Where the half-CV-squared becomes heat

**It is Joule heating, and it happens in two places only: a conducting channel and a resistive wire.**
Carriers accelerated by the field along the conducting path hand their energy to the lattice by emitting
phonons; nothing else in the electron's life takes net energy from it (Pop 2006 §II). The split between
channel and wire is the resistance split on the path — [§6](#6-the-wire-80-of-the-capacitance-05-of-the-heat)
puts a number on it: **0.5%** in the wire for an average net.

**In the channel.** At the fields a 20 nm gate makes, an electron scatters off a phonon every
**0.05–0.10 ps** and travels **5–10 nm** between inelastic events, shedding at most one optical phonon
(50–60 meV) each time (Pop 2006 §II, from the saturation velocity 10⁷ cm/s). Because an electron gains a
sizeable fraction of an eV but can only shed it 60 meV at a time, it must cross several mean free paths
before it is done — so in a quasi-ballistic device **essentially the whole Joule heat is dissipated in
the drain**, in a region of order 10 nm (Pop 2006 §II). Below 50 meV an electron scatters mainly off
acoustic phonons; above it, off optical modes.

**What is emitted, and in what share.** In bulk silicon at high field the generation spectrum is broad:
**longitudinal optical just over half** the dissipated energy, **longitudinal acoustic about a third**,
**transverse optical about a tenth** (Pop 2006 §II, Monte Carlo). This matters because the optical modes
carry almost no heat: their group velocity is ~**1,000 m/s** against **5,000 m/s** (TA) and **9,000 m/s**
(LA) for the acoustic modes. Half of the energy is therefore born in modes that cannot move it.

**The bottleneck, and how long it lasts.** The zone-centre optical phonon's lifetime in silicon at 300 K
is **2 ps**, measured by time-resolved incoherent anti-Stokes Raman scattering (Cahill 2009 and its APL
2007; Pop 2006 assumes 5 ps for the g-type LO mode and finds its occupation can approach unity above
10¹² W/cm³). In one lifetime an optical phonon travels **2 nm**; an acoustic phonon travels 10–18 nm. So
for the first couple of picoseconds the energy of a flip simply **sits where it was made**, inside the
drain, as a non-thermal phonon population for which "temperature" is not defined (Pop 2006 §III).

**Counting them.** Silicon's Raman mode at 520.7 cm⁻¹ is **64.6 meV** = 1.035 × 10⁻²⁰ J. One electron
falling the whole 0.517 V rail can make **8.01** of them; averaged over a charging edge, where an
electron falls half the rail, **4.00**:

| event | heat | optical phonons |
|---|---:|---:|
| one minimum fin's gate, per edge | 4.47 aJ | **432** |
| an average signal net, per edge | 0.2984 fJ | **28,850** |
| an average clock net, per edge | 1.042 fJ | **100,700** |
| one flipped MAC input bit, rail share of E60's 116.7 fJ | 87.5 fJ | **8.46 × 10⁶** |
| one random fp32 MAC, rail share of E38's 5.783 pJ | 4.337 pJ | **4.19 × 10⁸** |
| the card at 9.18 TFLOPS (4.59 × 10¹² MAC/s) | — | **1.92 × 10²¹ /s** |

**In the wire.** A metal's Joule heat goes first into its electron gas, not its lattice. Copper's thermal
conductivity is essentially all electronic — Wiedemann–Franz with L = 2.44 × 10⁻⁸ WΩ/K² and
ρ = 1.70 × 10⁻⁸ Ωm gives **431 W/(m·K)** against a measured ~400 — so the phonon mean free path in the
metal is not the quantity that matters; the **electron** mean free path is, and at 300 K it is **39.9 nm**
for copper (Gall 2016). The tightest metal in ASAP7 is **18 nm** wide at a 36 nm pitch, i.e.
**2.2 electron mean free paths narrow**, which is why a wire's resistivity at this pitch is several times
bulk. The heat then has to leave through the dielectric, and that is the worst conductor in the whole
path: dense SiOC:H measures **0.7 W/(m·K)** and 30% porosity takes it to **0.1** (Alam 2014) — **210× to
1,480× worse than bulk silicon's 148**.

## 4. The fin: atoms, materials, self-heating

**Atoms.** Silicon has 8 atoms in a 0.5431 nm cell, **4.994 × 10²² cm⁻³**. ASAP7's fin is 6.5 nm wide and
32 nm tall at a 27 nm pitch, with a 20 nm gate in this repository's decks (Clark 2016; the paper's table
prints 21 nm):

| | value |
|---|---:|
| fin segment under one gate (6.5 × 32 × 20 nm) | 4,160 nm³ |
| **silicon atoms in it** | **207,700** |
| atoms in a 1.5 nm inversion shell on three sides | 105,600 |
| atoms in one fin pitch × one gate pitch × fin height | 2.33 × 10⁶ |
| electrons the gate holds per rise (Q128) | **108** |
| **silicon atoms per electron on the gate** | **1,924** |
| dopant atoms at 10¹⁷ cm⁻³ / 10¹⁸ cm⁻³ | **0.42** / 4.16 |
| heat capacity of that segment (ρc = 1.64 MJ/(m³·K)) | 6.83 × 10⁻¹⁸ J/K |

So the smallest switch in this design moves about **one electron for every 1,900 silicon atoms** in the
channel it opens, and at a nominally undoped channel there is **less than one dopant atom in the whole
device**.

**Materials, and why they are the problem.** Thermal conductivity along the heat path, every value cited:

| material | κ, W/(m·K) | against bulk Si | source |
|---|---:|---:|:--|
| bulk silicon, 300 K | 148 | 1× | Glassbrenner & Slack 1964 |
| the **narrow fin** | 25 | **5.9× worse** | Yoo 2016 (0.25 W/(K·cm)) |
| the source/drain region | 62 | 2.4× worse | Yoo 2016 |
| copper (Wiedemann–Franz, 300 K) | 431 | 2.9× better | computed; see §3 |
| dense low-k SiOC:H | 0.70 | **211× worse** | Alam 2014 |
| low-k at 30% porosity | 0.10 | **1,480× worse** | Alam 2014 |

A 10 nm silicon film is expected to conduct **an order of magnitude** worse than bulk, and a buried oxide
about **two orders** worse (Pop 2006 §IV). On top of that, every dissimilar-material interface in the
stack adds a boundary resistance "on the order of the thermal resistance of a 20-nm-thick silicon dioxide
film" — about **1.4 × 10⁻⁸ m²·K/W** — and it is "fairly independent of processing conditions or the
specific type of metal and dielectric involved" (Pop 2006 §IV). The fin is thus a worse conductor than
the silicon it is cut from, sitting on interfaces, under a dielectric 200–1,500× worse again.

**The fin's self-heating, from published 7 nm-class work.** Yoo 2016's 3-D simulation of a 7 nm-node
non-rectangular bulk FinFET, with contact via and pad, at V_GS = V_DS = 0.78 V:

| | K/mW | K/W |
|---|---:|---:|
| total, 300 K | **1.05** | 1,050 |
| total, 325 K / 350 K | 1.07 / **1.10** | 1,070 / 1,100 |
| drain node | 1.96 | 1,960 |
| substrate node (the main heat path; the gate's is the largest) | 1.18 | 1,180 |

**What that resistance does and does not say.** Applied to this design's numbers:

| | power | ΔT at 1,050 K/W |
|---|---:|---:|
| one fin carrying full I_dsat (35.87 µA, SPICE TT 25 °C) at 0.517 V | 18.5 µW | **19.5 mK** |
| the mean power during one 23 ps rising edge of an average net | 13.0 µW | 13.6 mK |
| an average net toggling at 10% activity at 800 MHz | 47.8 nW | **50 µK** |

**A lumped R_th·C_th is the wrong instrument for one flip, and it is easy to show why.** Measurements put
FinFET self-heating's time constant "on the order of nanoseconds" (Prasad 2017, as quoted by Karmokar
2024), and Prasad's own conclusion is that for logic it "is still well below the operating frequency of
typical logic circuits, hence resulting in negligible self heating effect". A 1 ns time constant at
1,050 K/W implies C_th = 9.5 × 10⁻¹³ J/K, which in silicon is a **cube 834 nm on a side** — a region 140,000
times the volume of the channel. Within this design's 17–23 ps edges the heat has not filled anything like
that, so the quasi-steady 13.6 mK is not what the lattice sees. The capacity-limited bound is:

| if one edge's heat landed here and stayed | one fin's gate (4.47 aJ) | an average net (0.2984 fJ) |
|---|---:|---:|
| the channel segment, 4,160 nm³ | 0.65 K | **43.7 K** (7.3 K if the driver is 6 fins) |
| one fin pitch × gate pitch × fin height | 0.058 K | 3.9 K |
| a 10 nm drain cube (Pop's hot spot) | 2.7 K | 182 K |
| per silicon atom in the channel | 0.13 meV = 0.005 kT | 8.97 meV = **0.31 kT** |

Both columns are upper bounds and should be read as such: the heat is generated along several 5–10 nm
mean free paths rather than at a point, and a driver of a 2.233 fF net is more than one fin. The honest
statement is the last row: **one toggle of an average wire puts about a third of a kT on every silicon
atom in one channel** — enough to matter as a non-equilibrium phonon population for a few picoseconds,
and nothing at all once it has spread 300 nm.

## 5. The ladder: ps → ns → µs → ms

Diffusion times are L²/α with α = κ/ρc: **9.0 × 10⁻⁵ m²/s** for bulk silicon, 1.5 × 10⁻⁵ for the narrow
fin, 5.4 × 10⁻⁷ for dense low-k. Where the length is below one phonon mean free path, diffusion does not
apply and the row says so.

| scale | length | time | what is actually happening |
|---|---:|---:|:--|
| electron–phonon scattering | 5–10 nm | **0.05–0.10 ps** | one optical phonon emitted per event (Pop 2006) |
| the optical phonon's life | 2 nm of travel | **2 ps** | the energy sits in modes that cannot carry it (Cahill 2009) |
| across the fin | 6.5 nm | (2.8 ps) | **below one mean free path: not diffusion** |
| along the gate | 20 nm | (26 ps) | **below one mean free path: not diffusion** |
| one heat-carrying phonon's mean free path | 300 nm | **1.0 ns** | the shortest length at which Fourier conduction means anything; those phonons' own lifetime is ~30 ps (Cahill 2009) |
| the fin's lumped self-heating pole | ~834 nm equivalent | **~1 ns** | measured "order of nanoseconds" (Prasad 2017) |
| drain to the bulk, 90 nm-class SOI | — | **~100 ns** | measured/simulated (Pop 2006 §III, ref. 25) |
| the wire's heat down through 3 µm of dense low-k | 3 µm | **17 µs** | the slowest leg per unit length in the whole stack |
| half a 300 µm die, vertically | 150 µm | **0.25 ms** | the die's own time constant |
| across one shire, laterally | 1 mm | **11 ms** | what E62's movies watch move |
| the back of the board | — | **≥ 3.2 s** (E63); 61 s if read as one pole from the 87° lag | E63/Q126's two lock-in points |

**40% of silicon's thermal conductivity at 311 K is carried by phonons with mean free paths longer than
1 µm** (Regner 2013, measured over 0.3–8.0 µm). So even the die-scale rows above are only approximately
Fourier: a hot spot smaller than a micron is partly ballistic, and a diffusive estimate under-predicts
its temperature (Pop 2006 §III).

**What this says about the camera, and about E73.** The die's own path is **0.25 ms** vertical and **11 ms**
lateral. E63 ran its lock-in at **0.05 Hz** (20 s) and Q126 added a post-hoc point at **0.15 Hz** (6.7 s):
both are **10³ to 10⁵ times slower** than anything on the die. The roll-off E63 measured — 52.7 ± 2.0
mK/W at 0.05 Hz against 18.4 ± 5.4 at 0.15 Hz, a ratio of 0.34 ± 0.10 — is therefore a **board** property,
exactly as E63 concluded (τ ≥ 3.2 s with no upper bound, and 87–151° of phase, which no single pole can
give). **Adding a third camera frequency anywhere the camera can reach cannot resolve the die's heat
path**; it can only pin down the board's pole count. Resolving the die would need a lock-in near **1 kHz**,
which the camera's frame rate forbids, and a 1 kHz drive would have to be read from the chip's own
sensors instead. The Levels tab's coda row should say so.

## 6. The wire: 80% of the capacitance, 0.5% of the heat

Q128 found that **four fifths of an average net's capacitance is wire** (0.892 fF inside the cells,
0.856 fF between them, against 0.485 fF of transistor gates). It is tempting to read that as "most of a
flip's heat is made in the wire". It is not. The ½CV² of charging a node is dissipated in the resistances
along the charging path, in proportion to their share:

| | value |
|---|---:|
| ASAP7's average signal wire (ORFS `setRC.tcl`) | **26.6 Ω/µm**, 0.166 fF/µm |
| the between-cell wire of an average net, 0.856 fF ÷ 0.166 fF/µm | 5.16 µm |
| its resistance | **137 Ω** |
| one minimum fin's on-resistance, 0.517 V ÷ 35.87 µA | **14.4 kΩ** |
| **the wire's share of the heat** (distributed, R_wire/2) | **0.47%** |
| the length at which a tightest-metal wire's share equals the driver's | **1,085 µm** |
| the same on M8 (8.45 Ω/µm) | 3,412 µm |

The capacitance cross-check: 0.166 fF/µm agrees with this project's published 0.2 fF per µm, and
26.6 Ω/µm agrees within 2× with a slab estimate for an 18 nm × 36 nm conductor at a few times bulk
copper resistivity, so the units of the ORFS file (kΩ/µm, fF/µm) are what they appear to be.

**The sentence this earns.** *The wire decides how much heat a flip makes; the transistor decides where
it is born.* For local nets that is a 200:1 split in favour of the channel, and it is why the chip's heat
appears where the logic is, not where the wires run — which is exactly what E62's movies show when work
is moved across the die at constant total power. The crossover is around a millimetre on tight metal for
a one-fin driver, which is the same length at which repeaters start to be inserted.

## 7. What this changes

**In Q128's waterfall: nothing.** No pJ moves from "unaccounted" (3.837 pJ against the board, 2.39 pJ
against the rail) to "accounted". Stop 9 is beneath the ledger.

**In the Levels tab, stop 9** (currently *missing*, with "phonons, the fin's self-heating, materials, the
25,000×"):

| was missing | now |
|---|:--|
| phonons | §3: 64.6 meV mode, 4 per electron per edge / 8 per cycle, 28,850 per average-net toggle, 4.19 × 10⁸ per MAC, LO/LA/TO shares just over ½ / ⅓ / ⅒, 2 ps optical lifetime, 1,000 vs 5,000–9,000 m/s |
| the fin's self-heating | §4: R_th 1.05–1.10 K/mW from published 7 nm-class simulation, τ "order of nanoseconds" measured, 19.5 mK at full I_dsat, 50 µK at realistic activity, and why a lumped R_th is the wrong instrument for a 20 ps edge |
| materials | §4: κ for the narrow fin (25), S/D (62), bulk Si (148), copper (431), dense and porous low-k (0.70, 0.10), plus the 20 nm-oxide-equivalent boundary resistance; §4: 207,700 silicon atoms and < 1 dopant per channel |
| the 25,000× | §2: reproduced (24,509), its C shown to be a guess, replaced by 2,645× and 88,310×, and all three published ratios reconciled in one table |

**Three published figures are corrected or qualified.**
1. **The 20 Oct plan §3.4's "25,000×"** — see §2. Replace it.
2. **The 16 Oct outline's energy ruler**, rung *"Minimum inverter input · 83 aJ, 2,000 e⁻"* — the
   capacitance behind it (0.621 fF) is 18.5× the measured minimum gate and 0.28× the measured average
   net. It should be split into two rungs, 8.94 aJ/108 e⁻ and 0.597 fJ/7,206 e⁻, both of which Q128 has.
3. **The 20 Oct plan's "about eight of silicon's 64 meV optical phonons" per electron** — right over a
   full cycle, 4 per edge. Worth stating, because every other number in these pages is per edge.

**It extends, and does not repeat, *Why a flip makes heat: following the electrons*.** That page's §1
states the mechanism and cites Pop 2006 in one sentence; its §5 ladder prints 1,410× and explains the
2,755× difference as a convention. This note supplies what it leaves out: the scattering times and mean
free paths, the generation spectrum, the optical-phonon bottleneck and its 2 ps, the phonon counts, the
fin's R_th and τ, the materials table, the atoms, the ps-to-ms ladder, the wire's 0.5%, and the
correction to the plan's 25,000×. Nothing here contradicts that page.

## 8. What is still open

1. **No measurement of this chip's own thermal path at any scale below the board.** Every self-heating
   number here is an open-literature 7 nm-class figure, and the κ of the narrow fin (25 W/(m·K)) is a
   simulation input, not a measurement.
2. **The driver's fin count for an average net is not in the data**, so §4's capacity-limited ΔT is a
   range (43.7 K for one fin, 7.3 K for six), not a number. The placed netlist can give it.
3. **The 0.5% wire share uses one on-resistance** (V/I_dsat for one fin at 0.517 V) as the driver's
   effective resistance. A SPICE integration of i²R in the PMOS against i²R in a distributed line, on
   the same decks Q126(d) already runs, would turn 0.5% into a number with a bound.
4. **No ballistic correction.** Every length below ~1 µm in §5 is treated with a Fourier α; Regner 2013
   and Pop 2006 both say that under-predicts a sub-micron hot spot's temperature. A Boltzmann estimate
   would raise the ps rows.
5. **The 1 kHz claim in §5 is arithmetic, not a plan.** Whether the chip's own sensors can be read fast
   enough to lock in on the die's 0.25 ms path has never been tested.

## Files

| file | what |
|---|:--|
| [`atoms.py`](atoms.py) | every number above: constants, this repository's published figures, the literature values, and the arithmetic. No inputs beyond the file itself |
| [`atoms.json`](atoms.json) | its output |

## 9. References

**Measurement and simulation in the literature**

1. E. Pop, S. Sinha, K. E. Goodson, "Heat Generation and Transport in Nanometer-Scale Transistors,"
   *Proceedings of the IEEE* **94**(8), 1587–1601 (2006). doi:10.1109/JPROC.2006.879794. — electron and
   phonon mean free paths (5–10 nm, 200–300 nm); electron–phonon scattering time 0.05–0.10 ps; optical vs
   acoustic group velocities; LO/LA/TO generation shares; the drain hot spot; the ~100 ns SOI heat pulse;
   "several tens of picoseconds" per switching event; the 20 nm-oxide-equivalent boundary resistance;
   thin-film and buried-oxide κ degradation.
2. D. G. Cahill, Y. Wang, K. Kang, F. Watanabe, Y. K. Koh, J. Letcher, B. Daly, "Phonon lifetimes in
   silicon from 50 GHz to 15 THz," MRS Fall Meeting 2009 (Univ. of Illinois / Vassar). Primary results:
   *Appl. Phys. Lett.* **90**, 252104 (2007) — zone-centre optical phonon lifetime **2 ps** at 300 K by
   time-resolved incoherent anti-Stokes Raman; *Phys. Rev. B* **80**, 174112 (2009) — 100 GHz LA lifetime
   ~5 ns; *Phys. Rev. B* **71**, 235202 (2005) and *J. Appl. Phys.* **104**, 024905 (2008) — dominant
   heat-carrying phonon mean free path **300 nm**, lifetime ~30 ps.
3. A. J. Minnich, J. A. Johnson, A. J. Schmidt, K. Esfarjani, M. S. Dresselhaus, K. A. Nelson, G. Chen,
   "Thermal Conductivity Spectroscopy Technique to Measure Phonon Mean Free Paths," *Phys. Rev. Lett.*
   **107**, 095901 (2011). doi:10.1103/PhysRevLett.107.095901 — the method;
   and K. T. Regner, D. P. Sellan, Z. Su, C. H. Amon, A. J. H. McGaughey, J. A. Malen, "Broadband phonon
   mean free path contributions to thermal conductivity measured using frequency domain
   thermoreflectance," *Nature Communications* **4**, 1640 (2013). doi:10.1038/ncomms2630 — **40 ± 5%** of
   silicon's κ at 311 K from phonons with mean free path > 1 µm, measured over 0.3–8.0 µm.
4. S.-W. Yoo, H. Kim, M. Kang, H. Shin, "Analysis on Self-Heating Effect in 7 nm Node Bulk FinFET
   Device," *Journal of Semiconductor Technology and Science* **16**(2), 204–209 (2016).
   doi:10.5573/JSTS.2016.16.2.204 — 3-D simulation with contact via and pad: R_th 1.05/1.07/1.10 K/mW at
   300/325/350 K, drain 1.96, substrate 1.18; κ 0.25 (narrow fin), 0.62 (S/D), 1.5 (bulk) W/(K·cm);
   hot spot 337.1 K isolated against 329.3 K with an interconnected neighbour.
5. C. Prasad, S. Ramey, L. Jiang, "Self-Heating in Advanced CMOS Technologies," *IEEE IRPS* 2017,
   6A-4.1–6A-4.7. doi:10.1109/IRPS.2017.7936336 — scaled FinFETs show higher normalised thermal
   resistance, but the self-heating time constant stays well below logic operating periods.
6. N. Karmokar, S.-W. Tam, T. V. Dinh, V. A. Chhabria, R. Harjani, S. S. Sapatnekar, "Analyzing the
   Impact of FinFET Self-Heating on the Performance of RF Power Amplifiers," *ICCAD* 2024.
   doi:10.1145/3676536.3676829 — "based on measurements, the thermal time constant of FinFET SH is very
   fast, on the order of nanoseconds"; array time constants grow with finger count.
7. V. A. Chhabria, S. S. Sapatnekar, "Impact of Self-heating on Performance and Reliability in FinFET
   and GAAFET Designs," *IEEE ISQED* 2019, 235–240. doi:10.1109/ISQED.2019.8697786 — logic gates heat
   12 K (7 nm SOI FinFET) and 17 K (5 nm GAAFET) on average.
8. M. T. Alam, R. A. Pulavarthy, J. Bielefeld, S. W. King, M. A. Haque, "Thermal conductivity measurement
   of low-k dielectric films: effect of porosity and density," *Journal of Electronic Materials* **43**(3),
   746–754 (2014). doi:10.1007/s11664-013-2949-5 — dense SiOC:H/SiC:H **0.7 W/(m·K)**, falling to
   **0.1** at 30% porosity.
9. D. Gall, "Electron mean free path in elemental metals," *Journal of Applied Physics* **119**, 085101
   (2016). doi:10.1063/1.4942216 — Cu **39.9 nm** at room temperature (Ag 53.3, Au 37.7, Be 68.2).
10. C. J. Glassbrenner, G. A. Slack, "Thermal Conductivity of Silicon and Germanium from 3 K to the
    Melting Point," *Phys. Rev.* **134**, A1058 (1964). doi:10.1103/PhysRev.134.A1058 — bulk silicon
    **148 W/(m·K)** at 300 K.
11. R. Landauer, "Irreversibility and Heat Generation in the Computing Process," *IBM J. Res. Dev.* **5**,
    183 (1961). doi:10.1147/rd.53.0183 — the floor, kT ln 2.

**The open kit**

12. L. T. Clark, V. Vashishtha, L. Shifren, A. Gujja, S. Sinha, B. Cline, C. Ramamurthy, G. Yeric,
    "ASAP7: A 7-nm finFET predictive process design kit," *Microelectronics Journal* **53**, 105–115
    (2016). doi:10.1016/j.mejo.2016.04.006 — fin width 6.5 nm, fin height 32 nm, fin pitch 27 nm, CPP
    54 nm, gate length 20–21 nm, device tables this repository checked its SPICE against.
13. The OpenROAD Project, OpenROAD-flow-scripts, `flow/platforms/asap7/` — `setRC.tcl` (per-layer
    R and C: average signal wire 26.5684 kΩ/µm… 0.165790 fF/µm) and `asap7_tech_1x_201209.lef`
    (M1–M3 width 18 nm, pitch 36 nm).

**This repository**

14. [Q128, the transistor ledger](../2026-10-27-transistor-ledger/) — one minimum device's gate 8.94 aJ /
    108 electrons / 0.0335 fF; average signal net 2.233 fF and 0.5969 fJ a rise; average clock net
    7.794 fF; 14.5 fins a net drives; the floors at four temperatures; 2,755×.
15. [Q128, matmul to transistor](../2026-10-27-matmul-to-transistor/) — the 5.783 pJ board MAC, the
    1.946 pJ bottom-up ledger, the 3.837 pJ unaccounted, the four-way capacitance split.
16. [Q126(d), ASAP7 one switch](../2026-10-26-asap7-one-switch/) and
    [cell energies](../2026-10-26-asap7-cell-energies/) — I_dsat 35.87 µA per fin at TT 25 °C, the 23/17 ps
    edges, the device check against ASAP7's own tables.
17. [Q126(e), the open netlist](../2026-10-26-open-netlist/) and
    [the toggle recount](../2026-10-26-toggle-recount/) — 3,623 signal and 477 clock net toggles per
    random fp32 MAC.
18. [E60, the Hamming ladder](../../../../tools/claims-v3/hl/) — 116.7 fJ a flipped MAC input bit at the
    board, 20.8 fJ a read-port bit into an XOR, the 0.75 rail share, the V² test.
19. [E63, the camera half of the ladder](../2026-10-23-e63-camera-hamming-ladder/) — 194 ± 9 mK at
    0.05 Hz, 59 ± 3 mK/W, 87° of lag; and Q126's post-hoc second frequency, 18.4 ± 5.4 mK/W at 0.15 Hz
    against 52.7 ± 2.0 at 0.05 Hz, ratio 0.34 ± 0.10, τ ≥ 3.2 s with no upper bound.
20. [E62, the heat movies](../2026-10-21-e62-heat-movies/) — heat following where the work runs at
    constant total power.
