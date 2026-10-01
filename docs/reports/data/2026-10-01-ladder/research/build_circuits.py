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
# the constructions inside.json already names (their name, lead and facts stay; a short name and the textbook's fact join)
nodes['lib.adder'] = {'short': 'Adder'}
nodes['lib.booth'] = {'short': 'Booth encoder'}
nodes['lib.icg'] = {'short': 'Clock gate'}
more.update({'lib.adder': ['tb.prefix', 'tb.kogge'], 'lib.booth': ['tb.booth', 'tb.booth.table'], 'lib.icg': ['tb.icg'], 'lib.senseamp': ['tb.senseamp'],
             'vpu.lane.fma': ['tb.fma'], 'lib.nand2': ['tb.gates'], 'lib.inverter': ['tb.gates']})

if __name__ == '__main__':
    out = os.path.join(HERE, 'circuits.json')
    json.dump({'meta': {'written': '2026-10-01', 'by': 'research/build_circuits.py', 'what': 'textbook constructions below the chip\'s blocks: facts, scales, facts for existing scales'},
               'facts': facts, 'nodes': nodes, 'more': more}, open(out, 'w'), indent=1, ensure_ascii=False)
    open(out, 'a').write('\n')
    print('wrote', out, len(facts), 'facts,', len(nodes), 'scales')
