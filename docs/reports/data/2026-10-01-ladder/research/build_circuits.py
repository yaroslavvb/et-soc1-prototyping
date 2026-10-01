#!/usr/bin/env python3
"""The textbook constructions the ladder draws below the chip's blocks (1 Oct 2026, the owner's second update: "for the
compute units, can you maybe use the textbook definition of the compute units or the transistors? ... Make sure in all
the places I eventually go all the way down to the lowest transistor level and then I go down to the atoms").

The ET-SoC-1's own circuits are not published; its RTL (core-et, Erbium branch) names the blocks only. So each block a
reader opens is drawn as the construction the standard textbooks give, labelled as such, down to a gate drawn as
transistors. This file holds what the drawings say about them: one fact per construction (kind generic, with its book
or paper), and the scales' names, leads and sizes (an order of magnitude, inferred, the reasoning in the note).

    python3 build_circuits.py   writes circuits.json beside this file (build_ladder.py merges it into ladder.json)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WH = 'N. Weste and D. Harris, CMOS VLSI Design: A Circuits and Systems Perspective, 4th ed. (Addison-Wesley, 2011)'
RB = 'J. Rabaey, A. Chandrakasan and B. Nikolić, Digital Integrated Circuits: A Design Perspective, 2nd ed. (Prentice Hall, 2003)'
KO = 'I. Koren, Computer Arithmetic Algorithms, 2nd ed. (A K Peters, 2002)'

facts = []


def F(fid, statement, kind, source, note=None):
    facts.append({k: v for k, v in (('id', fid), ('statement', statement), ('kind', kind), ('source', source), ('note', note)) if v})


F('tb.gates', 'A static CMOS gate pairs a pull-up network of PMOS transistors with a complementary pull-down network of NMOS '
  'transistors: a NOR has its PMOS in series and its NMOS in parallel, a NAND the reverse, and a compound gate such as '
  'AND-OR-INVERT combines series and parallel transistors in one stage.', 'generic', f'{WH}, ch. 1 (CMOS logic) and ch. 9 (combinational circuits)')
F('tb.prefix', 'A parallel-prefix adder computes for each bit a generate g = a·b and a propagate p = a XOR b, combines them in '
  'a tree of carry cells (G = Gi + Pi·Gj, P = Pi·Pj) of log2 n levels, and forms each sum bit as p XOR the carry into it; '
  'a ripple-carry adder instead passes the carry through all n bits one after another.', 'generic', f'{WH}, ch. 11 (addition: tree adders); {KO}, ch. 5')
F('tb.kogge', 'In the Kogge-Stone prefix tree, level k combines every position with the one 2^k places below it, so that n '
  'bits need log2 n levels, each cell driving at most two others.', 'generic',
  'P. M. Kogge and H. S. Stone, "A Parallel Algorithm for the Efficient Solution of a General Class of Recurrence Equations", '
  f'IEEE Transactions on Computers C-22(8), 1973, pp. 786-793; {WH}, ch. 11')
F('tb.shifter', 'A logarithmic (barrel) shifter shifts n bits by any amount in log2 n stages: stage k is a row of 2:1 '
  'multiplexers, one per bit, that pass each bit straight on or take the bit 2^k places away, as bit k of the shift amount says.',
  'generic', f'{WH}, ch. 11 (shifters)')
F('tb.booth', 'Radix-4 (modified) Booth recoding looks at overlapping triples of multiplier bits (bits 2i+1, 2i and 2i-1) and '
  'makes each partial product 0, +X, +2X, -X or -2X, halving the number of partial products to add; each bit of a partial '
  'product is a multiplexer choosing x(j) or x(j-1), followed by an XOR with the sign.', 'generic',
  'A. D. Booth, "A Signed Binary Multiplication Technique", Quarterly Journal of Mechanics and Applied Mathematics 4(2), 1951; '
  f'O. L. MacSorley, "High-Speed Arithmetic in Binary Computers", Proceedings of the IRE 49(1), 1961; {KO}, ch. 6; {WH}, ch. 11 (multiplication)')
F('tb.booth.table', 'The radix-4 Booth table: multiplier bits 000 give 0, 001 and 010 give +X, 011 gives +2X, 100 gives -2X, '
  '101 and 110 give -X, and 111 gives 0.', 'generic', f'{KO}, ch. 6; {WH}, ch. 11')
F('tb.lzd', 'A leading-zero counter for n bits is a tree of log2 n levels: each leaf takes two bits, and each node takes the '
  'count of its left half if that half holds a 1, else the count of its right half with one more bit set.', 'generic',
  'V. G. Oklobdzija, "An Algorithmic and Novel Design of a Leading Zero Detector Circuit: Comparison with Logic Synthesis", '
  'IEEE Transactions on VLSI Systems 2(1), 1994, pp. 124-128')
F('tb.lza', 'A leading-zero anticipator predicts the normalisation shift of a floating-point sum from the adder\'s operands, '
  'in parallel with the addition; its prediction can be one position off, which a final one-bit correction fixes.', 'generic',
  'M. S. Schmookler and K. J. Nowka, "Leading Zero Anticipation and Detection: A Comparison of Methods", Proceedings of the '
  '15th IEEE Symposium on Computer Arithmetic (ARITH-15), 2001, pp. 7-12')
F('tb.decoder', 'An n-to-2^n decoder has one AND gate per output, fed by each address bit or its complement; a memory\'s row '
  'decoder predecodes groups of two or three address bits first and drives each selected row through a buffer.', 'generic',
  f'{WH}, ch. 12 (SRAM row circuitry: decoders)')
F('tb.regfile', 'A register file keeps each bit in a latch or a multi-ported memory cell; a write decodes its address to enable '
  'one row (through a clock gate or a write wordline), and each read port picks one row per bit through a multiplexer tree '
  'or a read wordline and bitline.', 'generic', f'{WH}, ch. 12 (multiported register files)')
F('tb.icg', 'An integrated clock gate latches the enable while the clock is high and ANDs it with the clock: a block whose '
  'enable is low gets no clock edges, so its flip-flops and clock wires do not switch.', 'generic', f'{WH}, ch. 10 (sequential circuits) and ch. 5 (power: clock gating)')
F('tb.stdcell', 'Logic synthesis maps a block\'s register-transfer-level description onto a library of standard cells '
  '(inverters, NAND, NOR, AND-OR-INVERT and XOR gates, multiplexers, flip-flops, clock gates), typically a few hundred '
  'kinds of cell of one height, placed in rows.', 'generic', f'{WH}, ch. 14 (design methodology and tools: standard-cell design)')
F('tb.counter', 'A binary counter is a register and an incrementer: a chain of half adders adds one, each half adder\'s sum an '
  'XOR of its bit and the carry in and its carry an AND of the two.', 'generic', f'{WH}, ch. 11 (counters)')
F('tb.compare', 'An equality comparator XNORs each pair of bits and combines the results in a tree of NAND and NOR gates: '
  'the output is 1 only when every pair agrees.', 'generic', f'{WH}, ch. 11 (comparators)')
F('tb.fifo', 'A first-in, first-out queue is a small memory addressed by a write pointer and a read pointer, two counters; '
  'comparing the pointers tells a full queue from an empty one.', 'generic', f'{WH}, ch. 12 (serial-access memories: queues)')
F('tb.pll', 'A phase-locked loop multiplies a reference clock: a phase-frequency detector compares the reference with the '
  'output divided by N, a charge pump and loop filter turn the difference into a control voltage, and a voltage-controlled '
  'oscillator, often a ring of an odd number of inverters, settles at N times the reference.', 'generic', f'{WH}, ch. 13 (clocks: PLLs and DLLs)')
F('tb.ecc', 'A single-error-correcting, double-error-detecting (SECDED) code adds check bits, each the XOR of a subset of the '
  'data bits; recomputed on a read, they give a syndrome that is zero for no error, names the flipped bit for one error and '
  'flags two; 64 data bits need 8 check bits, a (72, 64) code.', 'generic',
  'R. W. Hamming, "Error Detecting and Error Correcting Codes", Bell System Technical Journal 29(2), 1950; M. Y. Hsiao, '
  f'"A Class of Optimal Minimum Odd-Weight-Column SEC-DED Codes", IBM Journal of Research and Development 14(4), 1970; {WH}, ch. 11 (coding)')
F('tb.rom', 'A NOR ROM stores each bit as a transistor present or absent where a wordline crosses a bitline: the bitlines are '
  'precharged high, and when a row rises its transistors pull their bitlines low.', 'generic', f'{WH}, ch. 12 (read-only memory)')
F('tb.senseamp', 'A latch-type SRAM sense amplifier is two cross-coupled inverters with a tail NMOS switched by a sense-enable '
  'signal: it turns a bitline difference of tens of millivolts into full logic levels; precharge PMOS transistors equalise '
  'the bitlines between reads.', 'generic', f'{WH}, ch. 12 (SRAM column circuitry: sense amplifiers); {RB}, ch. 12')
F('tb.fma', 'A fused multiply-add computes a x b + c with one rounding: Booth-recoded partial products reduced by a tree of '
  'carry-save adders, the addend aligned by a shifter in parallel, one wide addition, a leading-zero count, a normalising '
  'shift and a rounding increment.', 'generic',
  'R. K. Montoye, E. Hokenek and S. L. Runyon, "Design of the IBM RISC System/6000 Floating-Point Execution Unit", IBM Journal '
  f'of Research and Development 34(1), 1990, pp. 59-70; {KO}, ch. 7')

# ---- part 1b (1 Oct 2026): the last dead ends and short cuts, each opened onto its construction (the owner: "Make sure in
# all the places I eventually go all the way down to the lowest transistor level and then I go down to the atoms")
RZ = 'B. Razavi, Design of Analog CMOS Integrated Circuits, 2nd ed. (McGraw-Hill, 2017)'
DT = 'W. J. Dally and B. Towles, Principles and Practices of Interconnection Networks (Morgan Kaufmann, 2004)'
EM = 'R. W. Erickson and D. Maksimović, Fundamentals of Power Electronics, 3rd ed. (Springer, 2020)'
F('tb.serdes', 'A serial link\'s transmitter turns parallel words into one bit stream with a serialiser (a tree of 2:1 '
  'multiplexers, each stage at twice the rate of the one before), shapes it with a few-tap FIR equaliser and drives a '
  'differential pair of wires; its receiver equalises the attenuated signal (a continuous-time linear equaliser, then a '
  'decision-feedback equaliser), samples it with clocked comparators, recovers the clock from the data\'s own transitions '
  '(a phase detector steering a phase interpolator) and deserialises the bits; a PLL makes the fast clock.', 'generic',
  f'{WH}, ch. 13 (I/O and high-speed links); no ET source describes the PHY\'s circuits')
F('pcie.gen4.eq', 'PCIe 4.0 at 16 GT/s: the transmitter has a 3-tap feed-forward equaliser (one tap before the bit, one after) '
  'with ten presets that the receiver asks for during link training; the reference receiver has a continuous-time linear '
  'equaliser with seven settings and a 2-tap decision-feedback equaliser.', 'outside',
  'MathWorks, SerDes Toolbox documentation, "PCIe4 Transmitter/Receiver IBIS-AMI Model" (after the PCI Express Base Specification 4.0)',
  'https://www.mathworks.com/help/serdes/ug/PCIe4TxRxIBISAMIModel.html')
F('pcie.gen4.loss', 'A PCIe 4.0 link may lose up to 28 dB at 8 GHz, the Nyquist frequency of a 16 Gb/s signal: up to 20 dB on '
  'the system board (5 dB of it in the root complex\'s package) and 8 dB on the add-in card (3 dB in the endpoint). 28 dB is '
  'a signal 25 times weaker in voltage.', 'outside',
  'Teledyne LeCroy, "PCIe 4.0 Transmitter Electrical Testing" (blog, 12 January 2018); 10^(28/20) = 25 (arithmetic)',
  'https://blog.teledynelecroy.com/2018/01/pcie-40-transmitter-electrical-testing.html')
F('pcie.gen4.ui', 'At 16 GT/s each bit lasts 62.5 ps (1 / 16 x 10^9 s); 128b/130b coding sends 130 bits for every 128 of data, '
  'so one lane carries 1.97 GB/s each way.', 'derived', 'arithmetic on the PCI Express 4.0 rate and coding (in.pcie.phy.3)',
  note='1 / 16e9 s = 62.5 ps; 16e9 x 128 / 130 / 8 = 1.969e9 B/s')
F('tb.strongarm', 'A clocked comparator (the StrongARM latch) is a sense amplifier: a differential input pair under two '
  'cross-coupled inverters; on each clock edge it turns the input difference into a full 0 or 1, drawing no current between '
  'decisions. SerDes receivers sample with such latches.', 'generic',
  'B. Razavi, "The StrongARM Latch [A Circuit for All Seasons]", IEEE Solid-State Circuits Magazine 7(2), 2015, pp. 12-17',
  'https://www.seas.ucla.edu/brweb/papers/Journals/BR_Magzine4.pdf')
F('tb.bangbang', 'A bang-bang (Alexander) phase detector samples each bit in its middle and at its edge: if the edge sample '
  'equals the bit before it the clock is late, if it equals the bit after it the clock is early; XORs of neighbouring '
  'samples give each vote, and the votes nudge the sampling clock.', 'generic',
  'J. D. H. Alexander, "Clock Recovery from Random Binary Signals", Electronics Letters 11(22), 1975, pp. 541-542')
F('tb.diffpair', 'A differential pair: two matched transistors whose sources share one tail current source. The input that is '
  'higher steers more of the tail current through its own side\'s load, so the outputs swing with the difference of the two '
  'inputs and ignore what the two have in common.', 'generic', f'{RZ}, ch. 4 (differential amplifiers)')
F('tb.ctle', 'A continuous-time linear equaliser is a differential pair whose two sources are joined by a resistor and a '
  'capacitor in parallel (source degeneration): at low frequencies the resistor cuts the gain, at high frequencies the '
  'capacitor shorts it out, so the stage boosts the high frequencies the wire attenuated most. "The most common approach to '
  'creating a boost at high frequencies incorporates resistive and capacitive degeneration in a differential pair" (Razavi).',
  'generic', 'B. Razavi, "The Design of an Equalizer, Part One" (The Analog Mind), IEEE Solid-State Circuits Magazine 13(4), 2021',
  'https://www.seas.ucla.edu/brweb/papers/Journals/BR_SSCM_4_2021.pdf')
F('tb.xbar', 'A crossbar switch connects any of its inputs to any output: each output is a multiplexer over all the inputs, its '
  'select set each cycle by an arbiter (often round robin, so that every input gets its turn) among the inputs that want that '
  'output. Its area is mostly wires: every input crosses every output, each as wide as the datapath.', 'generic',
  f'{DT}, ch. 17 (router datapath components: the switch) and ch. 18 (arbitration)')
F('tb.round', 'Rounding to nearest, ties to even, the default of IEEE 754: of the exact result\'s bits beyond the last one kept, '
  'the first is the guard bit G, the next the round bit R, and the OR of all the rest the sticky bit S. The result rounds up '
  '(adds one at the last kept place) when G = 1 and any of R, S or the last kept bit L is 1; a tie (G = 1, R = S = 0) goes to '
  'the even neighbour. A carry out of the top shifts the result right by one and adds one to the exponent.', 'generic',
  f'IEEE Std 754-2019, IEEE Standard for Floating-Point Arithmetic, §4.3 (rounding-direction attributes; roundTiesToEven the default for binary formats); {KO}, ch. 4')
F('tb.buck', 'A buck converter steps a voltage down by switching: a high-side transistor connects an inductor to the input, a '
  'low-side one to ground, alternately, hundreds of thousands of times a second; the inductor and the output capacitor '
  'average the pulses. In steady state the output is the input times the share of time the high side is on (the duty cycle '
  'D = Vout / Vin). A multiphase converter runs several such stages in parallel, their pulses spread through the cycle, to '
  'share a large current and cancel ripple.', 'generic', f'{EM}, ch. 2 (principles of steady-state converter analysis: the buck converter)')
F('card.tpsm', 'The card\'s core regulator, a Texas Instruments TPSM831D31, is a power module: a D-CAP+ controller with four '
  'Smart Power Stages and their inductors in one package, 15 by 48 mm; one output of 3 phases up to 120 A, one of 1 phase up '
  'to 40 A, from 8-14 V in, switching at 350-700 kHz.', 'outside', 'Texas Instruments, TPSM831D31 product page (ti.com)',
  'https://www.ti.com/product/TPSM831D31')
F('card.ltm', 'The card\'s SRAM-rail regulator, an Analog Devices LTM4680, is a dual 30 A or single 60 A step-down µModule '
  'regulator (its switches and inductors inside a 16 x 16 mm package), 4.5-16 V in, 0.5-3.3 V out.', 'outside',
  'Analog Devices, LTM4680 data sheet and product page (analog.com)', 'https://www.analog.com/en/products/ltm4680.html')
F('buck.duty', 'Turning the card\'s 12 V into the minion rail\'s 0.517 V, a buck converter\'s high-side switch is on about 4% '
  'of each cycle (D = 0.517 / 12 = 0.043): at 500 kHz, about 86 ns of every 2 µs.', 'derived',
  'arithmetic on tb.buck (D = Vout / Vin), out.card.6 (12 V at the card edge) and et.v-minion (0.517 V on die)',
  note='Losses and the drop between the regulator and the die make the true duty cycle a little higher; 500 kHz is a value inside the TPSM831D31\'s 350-700 kHz range, not a measured one.')
F('tb.powerfet', 'A power MOSFET is thousands of small cells in parallel: in a trench-gate device, current flows vertically, '
  'from the source on top, down a channel along each trench wall through the p-type body, across a lightly doped drift layer '
  'to the heavily doped substrate, the drain, underneath; its on-resistance is milliohms and it blocks tens of volts.',
  'generic', 'B. J. Baliga, Fundamentals of Power Semiconductor Devices, 2nd ed. (Springer, 2019), ch. 6 (power MOSFETs)')
F('card.stages', 'Which transistors the regulators\' power stages use is not published in the card\'s documents.', 'unknown',
  'Esperanto, "PCIe Dev Card (V3)", ET-PCIe-Dev-Card-V3.pdf (github.com/aifoundry-org/et-man); TI\'s and ADI\'s product pages give no device structure')
F('tb.strap', 'A strap (boot-option) pin: a resistor pulls the pin up to the I/O supply, and a switch can tie it to ground '
  'instead; the chip\'s input receiver (often a Schmitt trigger, an inverter with hysteresis, so that a slow or noisy edge '
  'gives one clean change) reads its level, and a flip-flop holds it when the chip comes out of reset.', 'generic',
  'P. Horowitz and W. Hill, The Art of Electronics, 3rd ed. (Cambridge University Press, 2015)')
F('card.dip', 'The card has DIP switches to set all its boot options.', 'spec',
  'Esperanto, "PCIe Dev Card (V3)", ET-PCIe-Dev-Card-V3.pdf (github.com/aifoundry-org/et-man), p. 1 (features) and p. 3 (DIP switches)')
F('et.bootpins', 'The chip records the state of its boot pins: bits 10:0 of the reset manager\'s status register rm_status2 '
  '"provide status information about various boot pins": 11 bits.', 'spec',
  'Esperanto, ET Programmer\'s Reference Manual (github.com/aifoundry-org/et-man), §15.2.3.18 (SPIO CRU address space), pdf p. 431')
F('p.cu.1', 'A copper atom has 29 electrons: 2, 8, 18 and 1 in its four shells (ground state [Ar] 3d10 4s1); pulling the one '
  'outer electron off a lone atom takes 7.726 eV.', 'outside', 'NIST Atomic Spectra Database, ground states and ionization energies (Cu I)',
  'https://physics.nist.gov/PhysRefData/ASD/ionEnergy.html')
F('p.cu.2', 'Natural copper is 69.15% copper-63 (29 protons, 34 neutrons) and 30.85% copper-65 (29 protons, 36 neutrons); '
  'its standard atomic weight is 63.546.', 'outside', 'NIST, Atomic Weights and Isotopic Compositions (Cu)',
  'https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Cu')
F('cu.free', 'In the metal each copper atom gives its one outer electron to a shared sea: 4 atoms per 0.3615 nm cube make '
  '8.47 x 10^28 free electrons per cubic metre, which carry the current, while the atoms stay put.', 'derived',
  'arithmetic on wire.cu (the face-centred cubic cell, 0.3615 nm); one conduction electron per atom: C. Kittel, Introduction to Solid State Physics, 8th ed. (Wiley, 2005), ch. 6',
  note='4 / (0.3615e-9 m)^3 = 4 / 4.724e-29 m^3 = 8.47e28 per m^3 (Kittel lists 8.47e22 per cm^3 for copper)')
F('size.p.cu', 'One copper atom takes about 0.256 nm in the metal: the distance between neighbours, 0.3615 nm / sqrt(2).',
  'derived', 'arithmetic on wire.cu (the face-centred cubic cell, 0.3615 nm)', note='0.3615 / 1.4142 = 0.2556 nm')
F('host.intel14', 'Intel\'s 14 nm process, the host processors\', is a FinFET process too: fins 42 nm apart, gates 70 nm apart '
  'and the finest wires 52 nm apart (TSMC N7: 30, 57 and 40 nm).', 'outside',
  'S. Natarajan et al., "A 14nm Logic Technology Featuring 2nd-Generation FinFET, Air-Gapped Interconnects, Self-Aligned Double Patterning and a 0.0588 µm² SRAM cell size", IEDM 2014; out.host.5 (the hosts\' 14 nm)',
  'https://people.eecs.berkeley.edu/~pister/140sp16/resources/Intel14nmIEDM2014.pdf')
F('host.ddr4', 'The hosts\' processors (Core i7-11700K, i5-11600) take DDR4 memory, up to DDR4-3200 on two channels: DRAM, the '
  'same kind of one-transistor, one-capacitor cell as the card\'s LPDDR4X.', 'outside',
  'Intel, Core i7-11700K and Core i5-11600 specifications (ark.intel.com: memory types up to DDR4-3200, 2 channels); the cell: ml:dram:gen.cell')

SIZE = 'an order of magnitude only: no layout of the ET-SoC-1\'s circuits is published'


def S(nid, name, m, how):
    F(f'size.{nid}', f'{name}: about {fmt(m)} across, the width of the view that frames it (an order of magnitude).', 'inferred',
      'the ladder\'s textbook constructions (research/build_circuits.py)', f'{how}; {SIZE}.')
    return f'size.{nid}'


def fmt(m):
    return f'{m * 1e6:g} µm' if m >= 1e-6 else f'{m * 1e9:g} nm'


nodes, more = {}, {}


def N(nid, name, short, blurb, m, how, fl):
    nodes[nid] = {'name': name, 'short': short, 'blurb': blurb, 'm': m, 'kind': 'inferred', 'f': S(nid, name, m, how), 'facts': fl + [f'size.{nid}']}


N('lib.nor2', 'NOR gate', 'NOR gate', 'Out is 1 only when both inputs are 0: two p-type transistors in series pull it up, two n-type side by side pull it down. With the NAND, any logic can be built from it.',
  2.4e-7, 'about 3 gate pitches (171 nm) wide in a 240 nm-tall N7 cell, like the NAND', ['tb.gates'])
N('lib.aoi21', 'AND-OR-INVERT gate', 'AOI gate', 'One stage of transistors that computes not (A·B + C): cheaper and faster than an AND, an OR and an inverter. A fast adder\'s carry cells are made of these.',
  3e-7, 'about 4 gate pitches wide (inference)', ['tb.gates', 'tb.prefix'])
N('lib.shifter', 'Shifter (stages of multiplexers)', 'Shifter', 'Moves a number left or right by any number of places in a few steps: each stage shifts by 1, 2, 4, ... places or not. The multiply-add uses one to line up the numbers it adds and another to normalise the result.',
  2e-5, 'a 64-bit shifter is 6 rows of 64 multiplexers, each about 0.3 µm wide', ['tb.shifter'])
N('lib.lzd', 'A leading-zero counter', 'Leading zeros', 'Counts the zeros before the first 1 of a number, in a tree of small cells: it tells the normaliser how far to shift a sum so that its first digit is a 1.',
  5e-6, 'a 64-bit counter is about 60 small cells in six levels', ['tb.lzd', 'tb.lza'])
N('lib.decoder', 'Decoder', 'Decoder', 'Turns an address into one raised line: 3 bits pick one of 8 rows, 7 bits one of 128. Every memory and register file has one for its rows.',
  3e-6, 'a 7-to-128 row decoder spans the 128 rows of an array, a few µm', ['tb.decoder'])
N('lib.regfile', 'Register file', 'Register file', 'A small, fast memory with several doors: rows of latches, a decoder that picks the row to write, and multiplexers that read one row out per port. Processors keep their registers in these.',
  4e-5, 'like the core\'s integer register file: 4,096 latch bits with their ports', ['tb.regfile'])
N('lib.logic', 'Control logic: standard cells', 'Logic cells', 'What any block of control logic is made of when its own netlist is not published: flip-flops that hold its state and a few kinds of gate that compute the next state, all from a library of standard cells.',
  2e-5, 'a control block of a few thousand cells at 0.1-0.3 µm² each', ['tb.stdcell'])
N('lib.counter', 'Counter', 'Counter', 'A register that adds one to itself on every clock (or every event): flip-flops and a chain of half adders. Barrier counters, credit counters and performance counters are all of this kind.',
  3e-6, 'an 8- to 40-bit counter: a few dozen cells', ['tb.counter'])
N('lib.cmpeq', 'Equality comparator', 'Comparator', 'Says whether two numbers are equal: an XNOR gate per bit, then a tree of gates that is 1 only if every bit agreed. A cache uses one per way to find its hit.',
  2e-6, 'a 23-bit comparator: 23 XNORs and a small tree', ['tb.compare'])
N('lib.fifo', 'Queue (first in, first out)', 'Queue', 'Where requests wait their turn: a small register file, a counter that points where the next one is written, another where the next one is read, and a compare that says full or empty.',
  2e-5, 'a few entries of a cache line or a request, with their pointers', ['tb.fifo'])
N('lib.pll', 'A phase-locked loop (PLL)', 'PLL', 'Makes a fast clock from a slow, steady one: it compares the two, and nudges an oscillator (a ring of inverters) until its output, divided down, matches the reference.',
  1e-4, 'on the order of 100 µm across, like the shire\'s clock generation (size.shire.clock)', ['tb.pll'])
N('lib.ecc', 'Error correction (SECDED)', 'ECC', 'Extra check bits stored with the data, each the parity of some of the bits: on a read they show whether a bit flipped, which one, so it can be put right, and whether two did.',
  1e-5, 'the XOR trees of a 72-bit code: a few hundred gates', ['tb.ecc'])
N('lib.rom', 'A read-only memory (ROM)', 'ROM', 'A table fixed when the chip is made: a transistor where a bit is 0, none where it is 1. The vector unit\'s transcendental functions read their coefficients from small tables like this.',
  2e-5, 'a small table of coefficients: a few thousand bits', ['tb.rom'])
def N2(nid, name, short, blurb, m, kind, note, fl):
    F(f'size.{nid}', f'{name}: about {fmt(m) if m < 1e-3 else str(round(m * 100, 1)) + " cm"} across, the width of the view that frames it.', kind,
      'the ladder\'s textbook constructions (research/build_circuits.py)', note)
    nodes[nid] = {'name': name, 'short': short, 'blurb': blurb, 'm': m, 'kind': kind, 'f': f'size.{nid}', 'facts': fl + [f'size.{nid}']}


# part 1b: the last dead ends' constructions
N('lib.diffamp', 'A differential amplifier', 'Differential pair', 'Two matched transistors that share one current: the higher input takes more of it. It amplifies the difference between two wires and ignores what they share, which is how a receiver hears a weak signal through noise.',
  1e-6, 'a few transistors of several fins each, sized for matching (inference)', ['tb.diffpair', 'tb.ctle'])
N('lib.xbar', 'A crossbar switch', 'Crossbar', 'Connects any input to any output for one cycle: a multiplexer per output picks the input its arbiter chose. In the chip it is 512 bits wide, so it is mostly wires.',
  1e-4, 'like the router\'s 8 x 8 switch of 512-bit datapaths (size.shire.meshstop.router.xbar)', ['tb.xbar'])
N('lib.round', 'Rounding', 'Rounding', 'The exact product and sum are longer than a float can keep: three extra bits say whether the kept part rounds up by one at its last place, to the nearest value, a tie to the even one.',
  5e-6, 'a sticky OR, a compound gate and a 24-bit incrementer: a few hundred cells', ['tb.round', 'tb.fma'])
# the wire: inside.json's scale (its name, lead and facts stay); the view is wider than one pitch, so its size is the view's
F('size.lib.wire.view', 'Copper wiring, in section: about 300 nm across, the width of the view that frames it (seven wires at the 40 nm pitch of M0-M4).',
  'inferred', 'arithmetic on n7.mmp (7.5 pitches of 40 nm)', 'the drawing\'s heights are not to scale: the stack\'s are not published')
nodes['lib.wire'] = {'name': 'Copper wiring, in section', 'short': 'Copper wire', 'm': 3e-7, 'kind': 'inferred', 'f': 'size.lib.wire.view',
                     'blurb': 'The chip\'s finest wires are copper, about 20 nm wide and 40 nm apart, wrapped in a thin cobalt liner so that copper atoms do not wander; cobalt contacts take them down to the transistors.'}
N2('lib.buck', 'A buck converter (a switching regulator)', 'Buck converter', 'How 12 volts becomes half a volt without burning the rest as heat: two transistors connect an inductor to 12 V or to ground, hundreds of thousands of times a second, and the inductor and a capacitor smooth the pulses into a steady supply.',
   2e-2, 'inferred', 'about the size of the card\'s regulator modules: the TPSM831D31 is 15 x 48 mm (card.tpsm), the LTM4680 16 x 16 mm (card.ltm)', ['tb.buck', 'card.tpsm', 'card.ltm', 'buck.duty', 'card.stages'])
N2('lib.powerfet', 'A power transistor, in section', 'Power transistor', 'A switch for tens of amps: thousands of small transistor cells side by side, each passing current straight down through the silicon from its source on top to the drain underneath.',
   5e-6, 'inferred', 'a few cells of a trench MOSFET, each a micrometre or two wide (tb.powerfet); order of magnitude only, the regulators\' own devices are not published', ['tb.powerfet', 'card.stages', 'dope.donor-acceptor'])
N2('lib.strap', 'A boot switch and its pin', 'Boot pin', 'A switch on the card holds one of the chip\'s pins at 0 or lets a resistor pull it to 1; when the chip comes out of reset it reads the pin and starts accordingly.',
   2e-2, 'inferred', 'a block of DIP switches is about 2 cm long on the card\'s photo (out.card.1 gives the card\'s 167.6 mm width); the pin and its receiver are far smaller', ['tb.strap', 'card.dip', 'et.bootpins'])
nodes['p.cu'] = {'name': 'A copper atom', 'short': 'Copper atom', 'm': 2.556e-10, 'kind': 'derived', 'f': 'size.p.cu',
                 'blurb': 'Copper: 29 electrons around a nucleus of 29 protons. In the metal each atom gives its one outer electron to a shared sea that flows when a voltage pushes it: that is the current in every wire of the chip.',
                 'facts': ['p.cu.1', 'p.cu.2', 'cu.free', 'size.p.cu', 'wire.cu']}

# the constructions inside.json already names (their name, lead and facts stay; a short name and the textbook's fact join)
nodes['lib.adder'] = {'short': 'Adder'}
nodes['lib.booth'] = {'short': 'Booth encoder'}
nodes['lib.icg'] = {'short': 'Clock gate'}
more.update({'lib.adder': ['tb.prefix', 'tb.kogge'], 'lib.booth': ['tb.booth', 'tb.booth.table'], 'lib.icg': ['tb.icg'], 'lib.senseamp': ['tb.senseamp'],
             'vpu.lane.fma': ['tb.fma'], 'lib.nand2': ['tb.gates'], 'lib.inverter': ['tb.gates'],
             'lib.wire': ['n7.mmp', 'wire.cu', 'n7.cu-co-liner', 'n7.contacts-co', 'n7.metal-layers', 'cu.free', 'size.lib.wire.view'],
             'pcie.lane': ['tb.serdes', 'pcie.gen4.eq', 'pcie.gen4.loss', 'pcie.gen4.ui', 'tb.strongarm', 'tb.bangbang', 'tb.ctle'],
             'lib.senseamp': ['tb.strongarm']})
# the numbers the new drawings print: key -> (fact, the text as it occurs in the fact[, the text drawn])
num = {'pcie_gt': ('pcie.gen4.ui', '16 GT/s'), 'pcie_ui': ('pcie.gen4.ui', '62.5 ps'), 'pcie_loss': ('pcie.gen4.loss', '28 dB at 8 GHz'),
       'pcie_ffe': ('pcie.gen4.eq', '3-tap'), 'pcie_dfe': ('pcie.gen4.eq', '2-tap'), 'buck_d': ('buck.duty', 'about 4%'),
       'buck_12': ('buck.duty', '12 V'), 'tps_a': ('card.tpsm', 'up to 120 A'), 'tps_f': ('card.tpsm', '350-700 kHz'), 'ltm_a': ('card.ltm', 'single 60 A'),
       'cu_29': ('p.cu.1', '29 electrons'), 'cu_shells': ('p.cu.1', '2, 8, 18 and 1'), 'cu_ion': ('p.cu.1', '7.726 eV'),
       'cu_n': ('cu.free', '8.47 x 10^28 free electrons per cubic metre', '8.47 × 10²⁸ free electrons per m³'), 'cu_iso': ('p.cu.2', '69.15% copper-63'),
       'cu_78': ('wire.cu', 'about 78 copper atoms across'), 'm_w20': ('n7.mmp', 'about 20 nm wide'), 'm_p40': ('n7.mmp', '40 nm'),
       'i14_fp': ('host.intel14', 'fins 42 nm apart'), 'boot_11': ('et.bootpins', '11 bits')}


if __name__ == '__main__':
    out = os.path.join(HERE, 'circuits.json')
    json.dump({'meta': {'written': '2026-10-01', 'by': 'research/build_circuits.py', 'what': 'textbook constructions below the chip\'s blocks: facts, scales, facts for existing scales'},
               'facts': facts, 'nodes': nodes, 'more': more, 'num': num}, open(out, 'w'), indent=1, ensure_ascii=False)
    open(out, 'a').write('\n')
    print('wrote', out, len(facts), 'facts,', len(nodes), 'scales')
