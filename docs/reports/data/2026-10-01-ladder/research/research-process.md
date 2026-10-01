# TSMC N7, the ET-SoC-1 and the electronics underneath: research for the ladder

Research for the owner's request of 1 October 2026 (`OWNER-REQUEST.md` beside this file): make the chip diagram and the
memory levels zoom in "all the way to computing transistors, and to the individual atoms, assuming it's using TSMC 7nm
process", with "the electronics bits filled in". This file gives the process facts (TSMC N7), Esperanto's own facts
about the ET-SoC-1, and the electronics a beginner needs at each inward scale, with a citation and a verbatim quote for
every outside number. `process.json` beside this file holds the same facts, machine-readable (99 facts: id, statement,
value, unit, kind, label, source, url, quote, note, repo_fact); `build_process.py` writes it and checks that every
outside, generic and spec fact has a URL and a quote and every derived or inferred fact shows its arithmetic.

Written 1 October 2026 in the `ladder` worktree, from web sources read that day and the repository at `bb0eb78`. No card
was touched. Local copies of the downloaded sources are in `src/` (Hot Chips 33 slides, Hu's textbook chapters, the
WikiChip pages from the Internet Archive, the Berkeley FinFET report, the ALD metal-gate review, IRDS More Moore).

## How the facts are labelled

The build's vocabulary (`research/build_inside.py`), with the label the pages print:

| kind | meaning | page label |
|---|---|---|
| spec | an Esperanto / ET document says so (Hot Chips 33, IEEE Micro, manuals) | documented |
| measured | measured on the lab's cards (this repository) | measured |
| derived | arithmetic on sourced values; the arithmetic is in the `quote` field | model |
| inferred | our estimate with stated assumptions; no source states it | inference |
| outside | a published outside source about the process or the physics | outside source |
| generic | a textbook rule or industry practice, not specific to this chip or TSMC | outside source (generic) |
| unknown | not published anywhere we could read | unknown |

## In brief

- **The chip** (Esperanto, Hot Chips 33 and IEEE Micro 2022): TSMC 7 nm (WikiChip names it N7), over 24 billion
  transistors, 570 mm², 89 mask layers, a 45 x 45 mm package with 2,494 balls and over 30,000 bumps to the die,
  over 160 million bytes of SRAM, 1,088 minions + 4 Maxions + 1 service processor. Average density 42 MTr/mm², 46% of
  N7's densest logic (91.2). Esperanto designed for **0.3-0.5 V** where "0.75 V [is] the nominal voltage in 7 nm",
  re-characterised its cell libraries at 0.4 V, put the whole minion with its L1 on one low-voltage plane, and (per
  WikiChip, quoting CEO Art Swift) built "its own custom SRAM instead of using TSMC's standard SRAM offering ... on the
  order of 400 mV". The cards here measure 0.517 V on the minion rail at 600 MHz, 0.705 V on the SRAM rail, 0.485 V on
  the mesh; 20-29 W of leakage at 80 °C, doubling every 25 °C.
- **N7, the process** (TSMC's IEDM 2016 paper as reported, and WikiChip's analysis of production parts): fin pitch
  **30 nm**, fin width **6 nm**, fin height **52 nm**, contacted gate pitch **57 nm** (64 nm in high-performance cells),
  effective gate length **~16.5 nm**, subthreshold swing **~65 mV/decade**, DIBL ~40 mV/V, **four threshold-voltage
  options spanning ~200 mV**, metal pitch **40 nm** for M0-M4, 76 nm for M5-M9, 124 nm M10, 720 nm M11-M12, a
  **12-layer copper/low-k** stack, **cobalt trench contacts** (half the resistance of the tungsten they replaced),
  copper with a **cobalt liner and cap** in the finest metals, standard cells **240 nm** tall (6 tracks, 8 fin
  pitches; about 2 fins per transistor) or 300 nm (7.5 tracks), a **0.027 µm² high-density 6T SRAM cell** working down
  to 0.5 V, 4th-generation FinFET, 5th-generation high-k metal gate, gate-last, two gate-oxide thicknesses, all on
  193 nm immersion lithography (no EUV). The fin numbers supersede the chipzoom research's inference (6-7 nm, 45-50 nm,
  from 10 nm-generation cross-sections): WikiChip's TSMC page, unreachable directly, was read through the Internet
  Archive.
- **Not published by TSMC**: the gate-stack materials and thicknesses, the absolute threshold voltages, the doping, the
  physical gate length. Industry practice and comparable published cross-sections fill these in, labelled as such:
  HfO2 (k ~24) on a thin SiO2 interlayer, an equivalent oxide under 1 nm, TiAl (n-type) and TiN (p-type) work-function
  metals filled with W or Al; an undoped or lightly doped fin channel (1e16-1e18 cm^-3) with a punch-through stopper
  (2.5-5e18) at its base; in-situ-doped epitaxial source/drain, Si:P up to 1.75e21 cm^-3 (3% of the atoms; only 1.3e20
  electrically active) for NMOS and SiGe:B above 1e20 for PMOS.
- **Atoms**: a fin is **about 31 planes of silicon atoms across** (11 unit cells), the channel under the gate about 86
  planes long and 383 planes tall; it holds about **257,000 silicon atoms and 0.05 to 5 dopant atoms** (often none).
  Pure silicon at room temperature has 1e10 free carriers per cm³: 0.00000005 of one in a channel. Every carrier that
  conducts is put there by the gate's field from the heavily doped source and drain.
- **Electrons, the numbers a beginner can hold on to** (derived or inferred, assumptions stated): a fin that is on at
  0.517 V holds **about 100 electrons** in its channel; a 6T SRAM node holds **roughly a thousand** (440-1,300) at
  0.705 V; a DRAM cell **roughly 45,000-70,000**; clocking one register bit in the tensor unit draws **about 38,000**
  from the supply; one minion-cycle of random fp32 matmul moves **540 million**; the average transistor leaks **about 10
  billion electrons a second** while "off".

## 1. The ET-SoC-1, from Esperanto and from the cards

| Fact | Value | Kind | Source and quote |
|---|---|---|---|
| Process | TSMC 7 nm (N7 per WikiChip) | spec / outside | IEEE Micro p. 37: "fabricated in TSMC 7-nm technology and contains over 24 billion transistors"; WikiChip: "Physically, the chip is fabricated on TSMC's N7 process technology." |
| Transistors | over 24 billion | spec | IEEE Micro p. 31; HC33 slide 20 "24 billion transistors" (WikiChip before Hot Chips: "23.8 billion") |
| Die | 570 mm², 89 mask layers | spec | IEEE Micro p. 37: "It has a die area of 570 mm2 and uses 89 mask layers." |
| Package | 45 x 45 mm, 2,494 balls, >30,000 bumps | spec | HC33 slide 20: "Package: 45x45mm with 2494 balls to PCB, over 30,000 bumps to die" |
| On-die SRAM | over 160 million bytes | spec | HC33 slide 20: "Over 160 million bytes of on-die SRAM used for caches and scratchpad memory" |
| Cores | 1,088 minions, 4 Maxions, 1 service processor | spec | HC33 slides 2 and 20 |
| Minion clock | 300 MHz - 2 GHz range; typical 500 MHz - 1.5 GHz | spec | HC33 slide 7 "OPERATING RANGE: 300 MHz TO 2 GHz"; slide 20 |
| Power | typically < 20 W; 10 to 60+ W under software control | spec | HC33 slide 20 |
| Per-shire supplies | each minion shire has its own low-voltage inputs | spec | HC33 slide 20: "...finely adjusted to mitigate Vt variation effects and enable DVFS" |
| Nominal 7 nm voltage | 0.75 V | spec | IEEE Micro p. 33: "0.75 V, the nominal voltage in 7 nm" |
| Design voltage | 300-500 mV sweet spot; libraries at 0.4 V | spec | IEEE Micro p. 33: "between 300 and 500 mV"; "libraries recharacterized at 0.4 V" |
| Minion power plane | whole minion incl. 4 KB L1 on one low-voltage plane | spec | IEEE Micro p. 33 |
| Minion memory cells | Esperanto's own low-voltage cells, larger, ~400 mV | outside | WikiChip quoting A. Swift: "designed its own custom SRAM instead of using TSMC's standard SRAM offering. The cells, while physically larger, can stably operate at considerably lower voltage ... on the order of 400 mV" |
| Shire SRAM banks | near process-nominal voltage, for density | spec | IEEE Micro p. 35 |
| Mesh | own low-voltage domain | spec | IEEE Micro p. 35 |
| Why neighbourhoods of 8 | "7-nm wires are relatively slow" | spec | IEEE Micro p. 34 |
| Peak per minion | 128 int8 ops/cycle; 16 fp32, 32 fp16 | spec | HC33 slide 7 |
| Tensor instructions | up to 512 cycles; integer pipeline sleeps | spec | IEEE Micro pp. 33-34 |
| Transcendental unit | ROM-based | outside | WikiChip: "The trans unit is ROM-based, favoring lower power over silicon." |
| Power target | 10 mW/minion at 1 GHz, 0.425 V, 0.04 nF | spec | HC33 slide 5 |
| Average density | 42.1 MTr/mm² (46% of 91.2) | derived | 24e9 / 570 |
| Transistors per minion | at most ~15 million | inferred | (24e9 - 7.0e9 shire-cache bitcells) / 1,088 |
| Minion rail | 0.517 V at 600 MHz (0.568 / 700, 0.618 / 800) | measured | docs/findings/16-dvfs-and-leakage.md:20 |
| SRAM rail | 0.703-0.707 V | measured | chip fact volt.sram |
| Mesh rail | 0.483-0.486 V | measured | chip fact mesh.voltage |
| Leakage at 80 °C | 20-29 W (fit 23.3 W x exp((T-80)/36)) | measured | 16-dvfs-and-leakage.md; why-low-power.md |
| Switched capacitance per minion | 0.168 nF (random fp32), 0.012 (zeros) | measured | why-low-power.md |

The minion and its units, as the repository already documents them (chip facts `minion.*`, spec): RV64IMFC, two
hardware threads, in-order single issue; a 4 KB L1 (16 sets x 4 ways x 64 B lines) that can become a 3 KB scratchpad;
a vector unit of 8 identical 32-bit lanes in lockstep, each with one FMA unit (one fp32 or two fp16 multiply-adds a
cycle), two integer multiply-add units (four int8 MACs each), one integer unit and one transcendental unit; 32
registers of 256 bits per thread; an eight-stage VPU pipeline; tensor instructions sequenced by state machines over
the lanes (one fp32 TensorFMA is 4,096 multiply-adds). Eight minions share a 32 KB instruction cache (a
neighbourhood); four neighbourhoods and four 1 MB SRAM banks make a shire. Esperanto's Figure 2 (IEEE Micro p. 34,
"drawn roughly to scale") shows the vector/tensor unit taking "far more area than the integer pipeline".

The "over 160 million bytes": the 35 shire caches are 146.8 million bytes (35 x 4 MiB; the datasheet's 140 MB), the
1,088 L1s and 136 I-caches add 4.5 million each, about 156 million; the rest (Maxion L1s, tags, ECC, buffers) is not
itemised anywhere (inference).

## 2. TSMC N7: the process

TSMC published its 7 nm platform at IEDM 2016 (S.-Y. Wu et al., "A 7nm CMOS platform technology featuring 4th
generation FinFET transistors with a 0.027um2 high density 6-T SRAM cell for mobile SoC applications", paper 2.6). The
paper itself is paywalled; what it says comes through Dick James (TechInsights) and Electronics Weekly. WikiChip then
analysed production parts (A12, Snapdragon 855) and published the pitches actually used in the standard cells: "while
at IEDM TSMC reported slightly more aggressive pitches, the numbers shown in this article are the actual pitches used
in their standard cells (and the actual pitches you will find in the A12 and the SDM855)".

| Parameter | N7 | Source and quote |
|---|---|---|
| Volume production | April 2018 | WikiChip Fuse: "TSMC started mass production of their 7-nanometer node in April 2018." |
| Generation | 4th-gen FinFET, 5th-gen HKMG, gate-last, dual gate oxide | WikiChip Fuse: "This is a fourth-generation FinFET, fifth-generation HKMG, gate-last, dual gate oxide process." |
| Lithography | 193 nm immersion (no EUV); fins SAQP, gates and M0-M4 SADP | WikiChip Fuse, design-rule table |
| Fin pitch | 30 nm (10 nm node: 36) | WikiChip Fuse, "Transistor Profile": "Fin Pitch 36 nm 30 nm 0.83x"; also Wikipedia |
| Fin width | 6 nm (10 nm node: 6) | same table: "Fin Width 6 nm 6 nm 1.00x" |
| Fin height | 52 nm (10 nm node: 42) | same table: "Fin Height 42 nm 52 nm 1.24x" |
| Channel width per fin | ~110 nm (2 x 52 + 6) | derived, with Hu: "The channel width, W, is the sum of twice the fin height and the width of the fin." WikiChip: "Compared to N16, N7 has over twice the effective channel width." |
| Contacted gate pitch | 57 nm (HD), 64 nm (HP) | WikiChip Fuse: "the gate pitch has been further scaled down to 57 nm"; flavours table 57 / 64 nm |
| Effective gate length | ~16.5 nm | Dick James: "effective gate length (leff) centered around 16.5 nm" |
| Subthreshold swing | ~65 mV/decade | Dick James: "Sub-threshold swing has been pushed down to ~65mV/decade, and DIBL is ~40 mV/V" |
| Threshold options | 4, spanning ~200 mV | Dick James: "four device Vt options with a range of ~200 mV"; WikiChip: "a Vt range of around 200 mV" |
| Metal pitches | M0-M4 40 nm; M5-M9 76; M10 124; M11-M12 720 | WikiChip Fuse design-rule table; Dick James: "1x metal pitch is 40 nm for M0 to M4, and M5 - M9 are 1.9x (76 nm)" |
| Metal layers | 12 Cu/low-k (paper); M0-M12 listed by WikiChip | Dick James: "a 12-layer copper/low-k interconnect stack" |
| Contacts | cobalt trench contacts (were tungsten), -50% resistance | WikiChip Fuse: "TSMC introduced cobalt fill at the trench contact, replacing the tungsten contact. This has the effect of reducing the resistance at that area by 50%."; Semiconductor Digest 2022: "both TSMC and Samsung have cobalt contacts in their 7- and 5-nm products." |
| Interconnect | copper with cobalt liner and cap in the minimum-pitch metals | Semiconductor Digest 2022: "in TSMC's 16FF process, the M1 - M3 layers had Co liners and caps ... it has been used in the minimum pitch metals every generation since then, including the N5" |
| Standard cells | 240 nm (6T, 8 fin pitches, CPP 57) / 300 nm (7.5T, 10 fin pitches, CPP 64) / 360 nm (9T) | WikiChip Fuse: "Those cells are 240 nm and 300 nm tall respectively."; WikiChip 7 nm page adds H360 |
| Fins per transistor (HD) | 2 | Angstronomics: N7 2-fin descriptor "H240g57" |
| Logic density | 91.2 MTr/mm² (HD), ~65 (HP) | WikiChip Fuse |
| HD 6T SRAM cell | 0.027 µm² | WikiChip Fuse; TSMC paper title |
| SRAM test chip | 256 Mbit, works down to 0.5 V | Electronics Weekly: "full read/write functionality down to 0.5V" |
| vs N16 | ~30% speed or 55% power, ~3x density (TSMC page); 35-40% / >65% / 3.3x (IEDM) | TSMC N7 page; Electronics Weekly |
| vs N16FFC (symposium) | +33% performance at the same Ioff, or -58% Ioff at the same Ion | SemiWiki (Dillinger 2017) |
| SRAM cell geometry | ~114 x 240 nm (2 CPP x 8 fin pitches), one fin per transistor | inferred (layout arithmetic) |

TSMC describes the device side only in words: "an optimized fin width and profile, a raised source/drain epitaxial
process that strains the transistor channel and reduces parasitics, a novel contact process, and a copper/low-k
interconnect scheme featuring different metal pitches and stacks" (Electronics Weekly). WikiChip on the fin: "Continuing
to scale the fin width gives you a narrower channel while increasing the height to maintain a good effective width is
done in order to improve the short channel characteristics and subthreshold slope (i.e., improved Ieff / Ceff) but it
also degrades the overall parasitics."

**Comparable published cross-sections** (TechInsights' N7 teardowns are subscriber-only; the free summaries give no
numbers). Dick James' Siliconics slides (AVS, July 2018) give what the fins and gates of the neighbouring processes look
like:

- GlobalFoundries 7 nm (IEDM 2017, the other "7 nm" paper of that year): "FP 30 nm, CGP 56 nm, MMP 40 nm, quad-WF NFETs
  & PFETs"; "Active fin height ~41 nm, width ~6 nm, gate width ~ 88 nm"; "Co contacts, up to 17 metal layers".
- Intel 10 nm: "Fin height up from 34 to 42 to 53 nm, (IEDM17 46 nm) fin width 5 - 15 nm, ~7 nm at half height";
  "Solid-source diffusion punch-stopper used again"; "5th generation HKMG but 4 - 6 WFs"; "Cobalt M0 & M1".
- TSMC 10 nm (A11): "SAQP minimum fin pitch ~33 nm, fin width ~6 nm, functional gate height ~44 nm".
- Shape: fins are tapered (wider at the base) with rounded tops ("Vertical fins! But still rounded fin tops", Intel
  14 nm). A drawing of an N7 fin should be a slightly tapered slab about 6 nm wide and 52 nm tall above the isolation
  oxide, 30 nm from its neighbour.

## 3. Inside one transistor: gate stack, dopants, crystal

**The gate stack** (TSMC does not publish N7's; industry practice):

- Insulator: hafnium oxide on a thin SiO2 interfacial layer. Hu: "HfO2 has a relative dielectric constant (k) of ~24,
  six times larger than that of SiO2. A 6 nm thick HfO2 film is equivalent to 1 nm thick SiO2 ... These problems are
  minimized by inserting a thin SiO2 interfacial layer between the silicon substrate and the high-k dielectric."
- Equivalent oxide thickness: below 1 nm in FinFETs of this generation; the Berkeley FinFET study uses "EOT (nm) 0.7"
  for a 15 nm gate (comparable, simulated).
- Metals: Zhao and Xiang (2019): "The metal gate for nMOS was TiAl, and that for pMOS was TiN, integrated with HfO2
  dielectric by a gate last process ... To fill the gap, a conductive metal such as Al or W was deposited." / "The PVD
  TiAl and PVD TiN in gate stacks with HfO2 show EWF around 4.1 eV and 4.85 eV." Gate-last means a dummy polysilicon
  gate is made first, the source/drain is grown and annealed, then the dummy is etched out and the metals are laid into
  the trench. The four Vt options come from different work-function metal stacks (GF 7 nm has four per polarity).
- Why the metal sets the threshold: "For undoped FinFETs, much less charges are available" (Zhao and Xiang): with no
  dopants in the channel, the work function of the gate metal decides where the transistor turns on.
- One fin's gate as a capacitor: 110 nm x 16.5 nm at an EOT of 0.7-1 nm is about 63-90 aF (inferred; oxide term only).

**Dopants**:

- Channel: undoped or lightly doped. Hu: "There is no need for heavy doping in the channel to reduce Wdep. This leads to
  low vertical field and less impurity scattering; as a result the mobility is higher". The Berkeley report: in a
  conventional bulk FinFET "dopants within the fin (channel region), on the order of 1 x 10^18 cm^-3", which a
  super-steep retrograde profile cuts to 1e16, with a punch-through stopper peaking at 2.5-5e18 at the fin's base.
- NMOS source/drain: phosphorus-doped silicon, grown epitaxially. Applied Materials (2014): "total [P] by SIMS in HS
  Si:P epitaxial film is 1.75E+21 at/cc (~ 3 at.% in silicon)" and "only ~1.3E+20 at/cc phosphorous atoms are
  electrically active".
- PMOS source/drain: boron-doped silicon-germanium (the larger germanium atoms compress the channel, which speeds
  holes); a Qualcomm FinFET patent gives boron "less than 1E20 ... greater than 2E20 at/cm3".
- How dopants work (Hu): a group-V atom "bring[s] five valence electrons ... the fifth electron may escape to become a
  mobile electron"; boron, with three, leaves a hole; "the donor ionization energy (about 50 meV)" is about 2 kT, so
  nearly every dopant is ionised.

**The crystal and the atom**:

| Fact | Value | Source |
|---|---|---|
| Lattice parameter of silicon | 0.5431020511 nm | NIST CODATA 2022 |
| Structure | diamond cubic; every atom has 4 neighbours | Ioffe NSM; Hu ch. 1 |
| Si-Si bond | 0.2352 nm (a x sqrt 3 / 4) | derived |
| Atoms per volume | 5 x 10^22 cm^-3 = 50 per nm³ | Ioffe NSM ("Number of atoms in 1 cm3: 5*10^22") |
| Relative permittivity | 11.7 | Ioffe NSM |
| Band gap | 1.12 eV at 300 K (1.110 eV at 80 °C by Eg = 1.17 - 4.73e-4 T²/(T+636)) | Ioffe NSM; Hu |
| Intrinsic carriers | 1 x 10^10 cm^-3 at 300 K (~4 x 10^11 at 80 °C) | Ioffe NSM; Hu; 80 °C derived |
| Mobility | electrons <= 1,400, holes <= 450 cm²/V·s | Ioffe NSM |
| Saturation velocity | 8 x 10^6 cm/s electrons, 6 x 10^6 holes | Hu ch. 6 |
| Isotopes | 92.223% Si-28, 4.685% Si-29, 3.092% Si-30 | NIST |
| Silicon atom | 14 protons, 14 electrons, 4 valence | Hu ch. 1 (group IV); NIST |
| Si-28 nucleus | charge radius 3.1224 fm | König et al. (arXiv:2309.02037), Table 1, from Angeli and Marinova 2013 |

Counting atoms in one N7 channel (derived; the channel taken as 6 x 16.5 x 52 nm, the fin's width, the effective gate
length and the fin's height; the usual orientation, a (100) wafer with the channel along <110>, so the fin's sidewalls
are (110) planes, assumed):

- Across the fin: (220) planes are a/sqrt 8 = 0.192 nm apart: 6 / 0.192 = **31 planes**, 11 unit cells.
- Along the channel: 16.5 / 0.192 = **86 planes**, 30 unit cells.
- Up the fin: (400) planes are a/4 = 0.136 nm apart: 52 / 0.136 = **383 planes**, 96 unit cells.
- Volume 5,148 nm³ x 49.9 per nm³ = **257,000 silicon atoms**.
- Dopants at 1e16 / 1e17 / 1e18 cm^-3: **0.05 / 0.5 / 5 atoms**. A transistor that relied on channel doping would
  have its threshold set by whether it happened to get 2 or 7 dopants; this "random dopant fluctuation" (Hu: "The
  statistical variation of the number of dopant atoms and their location in small size MOSFET creates significant
  variations in the threshold voltage") is one reason the fin is left undoped and the metal sets the threshold.
- Free carriers in undoped silicon at room temperature: 1e10 cm^-3 x 5.15e-18 cm³ = **5 x 10^-8** (2 x 10^-6 at 80 °C).
- In the source/drain: 1.75 phosphorus atoms per nm³, one atom in about 30.
- Electrons cross the 16.5 nm channel in about 0.2 ps at the saturation velocity: 8,000 crossings per 600 MHz cycle.

**Wires**: copper (fcc, 0.3615 nm cube, 16.78 nΩ·m in bulk: Wikipedia). A 20 nm M0-M4 wire (40 nm pitch) is about 78
copper atoms across (derived), with a cobalt liner and cap; at these widths electrons scattering off the surfaces and
grain boundaries raise the resistivity well above bulk (generic).

## 4. The electronics a beginner needs, scale by scale

Each item says what to show and the number to print, with its fact id in `process.json`.

**Die and package** (`et.*`). 24 billion switches on 570 mm², fed through over 30,000 bumps. Power is
`P = Cdyn x V² x f + leakage` (HC33 slide 5): every switch event charges a capacitance from the supply and dumps it to
ground (`el.dynamic`, Hu: "In each switching cycle, a charge CVdd is transferred from the power supply to the load").
That is why voltage matters squared, and why Esperanto runs the minions at 0.4-0.52 V instead of the nominal 0.75 V:
(0.517/0.75)² = 0.48, half the energy per switch. The card's rails: minion 0.517 V, SRAM 0.705 V, mesh 0.485 V, DDR
0.77 V (`et.v-*`).

**Shire / minion** (`et.cdyn-measured`, `et.electrons-per-cycle`). A minion on random fp32 matmul switches an effective
0.168 nF per cycle: 87 pC, **540 million electrons per cycle**, 45 pJ. On zeros it switches 0.012 nF: the data decide how
many nodes flip. Leakage is the other term: 20-29 W of the card at 80 °C, about 1 nW per transistor, **about 10 billion
electrons a second through each "off" transistor** (`et.leak-per-tr`), doubling every 25 °C (`et.leak-double`).

**Lane, register, wire** (`et.flip-reg`, `el.bus-bit`). The energy manual prices the tensor unit by events: clocking
one register bit costs 3.18 fJ, an effective 11.9 fF charged at 0.517 V, **about 38,000 electrons**; toggling one
operand bit on the bus outside the unit costs 15.5 fJ, an effective 58 fF, **about 190,000 electrons**. The wires, not
the transistors, carry most of the switched charge.

**Standard cell and gate** (`n7.cells`, `n7.two-fin`, `n7.cpp`). Logic is built from cells 240 nm tall and a few
57 nm gate pitches wide; an inverter is one PMOS (pulls the output up to Vdd) and one NMOS (pulls it down to ground),
each typically 2 fins. CMOS draws current only while switching, apart from leakage.

**SRAM cell, latch, DRAM cell** (`n7.sram-hd`, `el.sram-node`, `el.dram-cell`, `el.dram-leak`). A 6T SRAM bit is two
cross-coupled inverters; each storage node is roughly 0.1-0.3 fF, so at the 0.705 V SRAM rail the bit is held by
**roughly a thousand electrons** (440-1,300; at the minion's 0.517 V in a latch, 320-970), continuously restored by the
inverters. A DRAM bit is charge on one capacitor of under 10 fF: **roughly 45,000-70,000 electrons**, with no restoring
circuit, so it must leak less than about 30 fA (190,000 electrons a second) to survive the 32 ms between refreshes:
about 50,000 times less than the average logic transistor here leaks.

**The FinFET** (`el.switch`, `el.finfet-why`, `el.off-not-off`, `n7.ss`, `n7.dibl`, `n7.vt-options`). A voltage-
controlled switch: source and drain are heavily doped silicon, the channel between them is undoped, and the gate wraps
three sides of the fin. With the gate at 0 V the channel is empty and only leakage flows; raise the gate past the
threshold Vt and its field pulls a thin layer of electrons (for NMOS) to the fin's surfaces, joining source to drain.
"Off" is not totally off: below Vt the current falls tenfold per 65 mV in N7 (the room-temperature limit is 60 mV;
about 77 at the card's 80 °C, `el.ss-80c`). A drain at full voltage lowers the barrier by about 40 mV per volt (DIBL).
Four Vt options, about 200 mV apart end to end, trade speed for leakage. N7's absolute Vt is not published
(`n7.vt-abs`); operating at 0.4-0.52 V means near-threshold. When one fin is on at 0.517 V its channel holds **about
85-120 electrons** (inferred, with an assumed 0.3 V threshold; `el.channel-electrons`).

**The fin and the gate stack** (`n7.fin-*`, `n7.weff`, `gate.*`). A silicon slab 6 nm wide and 52 nm tall, 30 nm from
the next; the gate drapes over it, so one fin is about 110 nm of channel width in a 30 nm footprint. Between metal and
silicon: a thin SiO2 interlayer and HfO2 (k ~24), together electrically like less than 1 nm of SiO2. The gate metal's
work function (TiAl about 4.1 eV for NMOS, TiN about 4.85 eV for PMOS) sets the threshold. Source and drain are grown
crystal, Si:P with 3% phosphorus for NMOS and boron-doped SiGe for PMOS, contacted by cobalt.

**The channel and the crystal** (`dope.count-channel`, `si.*`, `el.kt`). About 31 atoms across, 86 along, 383 tall:
257,000 atoms and at most a handful of dopants. Each silicon atom shares its four outer electrons in bonds with four
neighbours; freeing one takes the band-gap energy, 1.12 eV, about 43 times the thermal energy kT (25.9 meV), so pure
silicon has almost no free electrons. The supply voltage (0.517 V) is less than half the band gap: electrons in the
channel are not freed from bonds but supplied by the source.

**The atom and the nucleus** (`si.atom`, `si.nucleus`). 14 protons and 14 electrons; 92% of silicon is Si-28 with 14
neutrons; its nucleus has a charge radius of 3.12 fm, about 75,000 times smaller than the 0.235 nm bond. (Protons and
neutrons as quarks, and the cosmic scales, are outside this file's research.)

## 5. Suggested inward rungs (sizes for the scale readout)

| Rung | Characteristic size | Fact |
|---|---|---|
| Standard cell (HD) | 240 nm tall | n7.cells |
| 6T SRAM cell | ~114 x 240 nm (0.027 µm²) | n7.sram-hd, n7.sram-dims |
| FinFET (one gate over its fins) | 57 nm gate pitch, 30 nm fin pitch | n7.cpp, n7.fin-pitch |
| Fin | 52 nm tall, 6 nm wide | n7.fin-height, n7.fin-width |
| Finest wire | 40 nm pitch (~20 nm wide), ~78 Cu atoms across | n7.mmp, wire.cu |
| Channel | 16.5 nm long (effective) | n7.leff |
| Gate insulator | under 1 nm equivalent; HfO2 a few nm | gate.hfo2, gate.eot |
| Unit cell of silicon | 0.543 nm | si.lattice |
| Si-Si bond | 0.235 nm | si.lattice |
| Si-28 nucleus | 3.12 fm (charge radius) | si.nucleus |

## 6. What changes for the existing chip-diagram data

The chipzoom research (the chip diagram's `research/research-inside.md`, and the deep-zoom nodes in
`docs/reports/data/2026-09-27-chip-diagram/research/build_inside.py`) labelled N7's fin as an inference ("about 6-7 nm
wide and 45-50 nm tall, by analogy with TSMC 10 nm ... TSMC does not publish N7's") and its gate length as "about 20 nm
for a 7 nm-class process (IRDS)", and cited WikiChip Fuse "as the search summary reported them, the page itself refused
the connection". These can now be outside facts with quotes: fin 6 nm wide, 52 nm tall (WikiChip Fuse, Transistor
Profile table), effective gate length 16.5 nm (Dick James on the IEDM paper), and the WikiChip Fuse values are confirmed
from the archived page. Its derived counts stay right: 31 planes across a 6 nm fin. Its channel atom count (6 x 20 x 45 nm,
about 270,000) becomes 6 x 16.5 x 52 nm, about 257,000. Its "A high-k metal gate: a hafnium-based oxide on a thin
silicon-oxide interlayer under work-function metals" can cite Hu and Zhao and Xiang. Cobalt contacts and the Co-lined
copper are new.

## 7. Not published, or open

- Which N7 flavour (N7 or N7P), which standard-cell library and track height, which Vt options the ET-SoC-1 uses
  (the RTL names HDBULT08 / HDBULT11 cell families: memory-levels `l1:l1.u-library`).
- N7's absolute threshold voltages, gate-stack thicknesses and materials, physical gate length, doping profile.
- The ET-SoC-1's metal-layer count (89 masks in all) and the bitcell its SRAM macros use (`u.bitcell`).
- Any floorplan below the shire; transistors per minion (only an upper bound here).
- The DRAM cell: the card's Micron LPDDR4X generation and its cell capacitance and array voltage.
- Storage-node capacitances of N7 SRAM: no public number; the thousand-electron figure is an estimate.

## Sources (read 1 October 2026)

Esperanto and the chip:

- D. Ditzel et al., Hot Chips 33 slides, 24 Aug 2021:
  <https://hc33.hotchips.org/assets/program/conference/day2/HC2021.Esperanto.Dave_Ditzel.presentation.v1submitted.pdf>
  (local `src/hc33-esperanto.txt`).
- D. Ditzel et al., IEEE Micro 42(3), May/June 2022: <https://www.esperanto.ai/wp-content/uploads/2022/05/Dave-IEEE-Micro.pdf>
  (a local text copy was kept in the work directory).
- D. Schor, "A Look At The ET-SoC-1, Esperanto's Massively Multi-Core RISC-V Approach To AI", WikiChip Fuse, 2021:
  <https://fuse.wikichip.org/news/4911/a-look-at-the-et-soc-1-esperantos-massively-multi-core-risc-v-approach-to-ai/>
  (fuse.wikichip.org refuses connections; read through the Internet Archive capture of 10 July 2021).
- The repository: `docs/findings/16-dvfs-and-leakage.md`, `docs/research/why-low-power.md`,
  `docs/energy-manual/03-instructions.md`, the chip diagram's `facts.json` (volt.*, mesh.voltage, minion.*, chip.*,
  L123) and the memory levels' `facts.json`.

TSMC N7:

- D. James, "IEDM 2016 - Setting the Stage for 7.5 nm", 18 Jan 2017:
  <https://sst.semiconductor-digest.com/chipworks_real_chips_blog/2017/01/18/iedm-2016-setting-the-stage-for-75-nm/>
  (it prints the SRAM cell as "0.27 µm2", a typo for 0.027).
- D. Manners, "7nm processes at IEDM", Electronics Weekly, 20 Oct 2016: <https://www.design-reuse.com/news/3017-7nm-processes-at-iedm/>.
- D. Schor, "TSMC 7nm HD and HP Cells, 2nd Gen 7nm, And The Snapdragon 855 DTCO", WikiChip Fuse, 16 Jun 2019:
  <https://fuse.wikichip.org/news/2408/tsmc-7nm-hd-and-hp-cells-2nd-gen-7nm-and-the-snapdragon-855-dtco/>
  (Internet Archive capture of 13 Nov 2019; local `src/fuse-2408.txt`).
- WikiChip, "7 nm lithography process": <https://en.wikichip.org/wiki/7_nm_lithography_process> (capture of
  16 Jun 2025; local `src/wikichip-7nm.txt`).
- P. Singer with D. James, Semiconductor Digest, 1 Oct 2022 (cobalt contacts and liners):
  <https://www.semiconductor-digest.com/intel-4-process-drops-cobalt-interconnect-goes-with-tried-and-tested-copper-with-cobalt-liner-cap/>.
- D. James (Siliconics), "A Quick Look at 14-nm and 10-nm", AVS JTG, July 2018:
  <https://nccavs-usergroups.avs.org/wp-content/uploads/JTG2018/JTG718-4-James-Siliconics.pdf>.
- Wikipedia, "7 nm process": <https://en.wikipedia.org/wiki/7_nm_process>.
- T. Dillinger, SemiWiki, 23 Mar 2017: <https://semiwiki.com/semiconductor-manufacturers/tsmc/6676-top-10-updates-from-the-tsmc-technology-symposium-part-ii/>.
- TSMC, N7/N6 page: <https://www.tsmc.com/english/dedicatedFoundry/technology/platform_DCE_N7_N6>.
- Angstronomics, "The Truth of TSMC 5nm": <https://www.angstronomics.com/p/the-truth-of-tsmc-5nm>.
- TechInsights' N7 reports (Apple A12, Kirin 980, SMIC N+2 comparison) are subscriber-only: their public blog posts
  give no dimensions.

Devices and physics:

- C. Hu, Modern Semiconductor Devices for Integrated Circuits (2010), chapters 1, 6, 7 (author's free PDFs):
  <https://www.chu.berkeley.edu/wp-content/uploads/2020/01/Chenming-Hu_ch1-3.pdf>,
  <https://www.chu.berkeley.edu/wp-content/uploads/2020/01/Chenming-Hu_ch6-1.pdf>,
  <https://www.chu.berkeley.edu/wp-content/uploads/2020/01/Chenming-Hu_ch7.pdf>.
- C. Zhao and J. Xiang, "Atomic Layer Deposition (ALD) of Metal Gates for CMOS", Appl. Sci. 9 (2019) 2388:
  <https://doi.org/10.3390/app9112388>.
- X. Zhang, UC Berkeley EECS-2016-3 (bulk FinFET doping): <https://www2.eecs.berkeley.edu/Pubs/TechRpts/2016/EECS-2016-3.pdf>.
- X. Li et al. (Applied Materials), ECS 2014, Si:P epitaxy: <https://ecs.confex.com/ecs/226/webprogram/Paper40706.html>.
- Qualcomm, US 9,564,518 B2 (SiGe:B source/drain): <https://patents.google.com/patent/US9564518B2/en>.
- J. Choe (TechInsights), "DRAM Scaling Trend and Beyond", June 2022: <https://www.techinsights.com/blog/dram-scaling-trend-and-beyond>.
- Ioffe Institute NSM Archive, silicon: <https://www.ioffe.ru/SVA/NSM/Semicond/Si/> (basic, bandstr, electric pages;
  read through the mirror at www-f9.ijs.si because ioffe.ru served a self-signed certificate).
- NIST CODATA 2022: lattice parameter of silicon <https://physics.nist.gov/cgi-bin/cuu/Value?asil>, elementary charge
  <https://physics.nist.gov/cgi-bin/cuu/Value?e>, Boltzmann constant <https://physics.nist.gov/cgi-bin/cuu/Value?k>;
  silicon isotopes <https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Si>.
- K. König et al., "Nuclear charge radii of silicon isotopes", arXiv:2309.02037: <https://arxiv.org/abs/2309.02037>.
- Wikipedia, "Copper": <https://en.wikipedia.org/wiki/Copper>.
