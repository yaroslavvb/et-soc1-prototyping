# Request 1113-x02-regfile: the integer register file's reads and writes, bit by bit

Family X02. Designed Sat 14 Nov 2026; revised the same evening after two reviews (revision 2: a new control for the
stored-bit train, a fixed loop frame, the reducer's smoke, rate and bound rules, an optional second sitting) and again
after two independent line-by-line reads of revision 2's source (revision 3: the reference session's robustness on
its side paths and the reducer's reading of a hand-made stop; section 11). STATUS: see `STATUS`. Forecast frozen
before any datum: `prediction.json` (never pushed), sha256 in `log.md` (its second line supersedes the first;
revision 3 changes no forecast and re-registers only the reducer). Source: `src/` (public-safe: written from the
public instruction set, the runtime's public interface and the public lab repo's workload and train-kit style;
`src/BUILD.md`). It builds on E192 (the lab's registration of request 1113-x01-intbits, the scalar bit-flip ladders),
on the vector unit's read-port and result-bit prices (E60, E61), on the register-file cell ladder (E74) and on the
train form of E182 and E183.

## 1. Question

On every minion, one hart, streams of register-to-register scalar integer instructions with no load, no store and no
branch in the timed body, in pairs of kinds that run the same instruction count at the same issue rate and differ in
one thing. What does the scalar register file cost, per event, in pJ and in electrons through the core rail and
through the 12 V input:

1. **a stored bit that changes on a write** (a register-file cell), with the source, port and result streams, and how
   often each encoding bit changes, held identical between the two kinds;
2. **a result bit along the result path into the register file**, with the sources fixed (no read-port bit changes);
3. **one register write**, against the same instruction writing x0;
4. **the destination changing** between neighbouring instructions (two destinations against one; in an optional
   second sitting, eight against two);
5. **a read-port bit**: on port 2 when the register is only named by bits 24:20 of an immediate instruction and no
   operand uses it, on port 1 when it is only named by bits 19:15 of an upper-immediate instruction, and on port 2
   when the register is the operand of an `and` whose result is held at zero by the other source being x0. RISC-V
   keeps register fields in fixed places so that a core can read the register file before it decodes the
   instruction (the unprivileged manual's own rationale); these arms ask whether this core does so for instructions
   that use no register operand, and what it costs;
6. **a held one** in the two registers named in turn, when nothing at the port changes (both hold all ones, against
   both zero);
7. **a bit of the read field**: the second source field changing in 1, 3 or 5 bits (zero contents: a 0, 1, 3, 5
   ladder), and, in the second sitting, eight source registers in turn against two.

No scalar register-file ladder has run on a card: E60 and E61 priced the vector unit's read port and result bits, E74
the vector register file's cell, the catalogue the scalar instructions on zeros, a constant and random data (its
sinks are rewritten with the value they already hold, so no scalar cell ever flips there), and E192 (1113-x01) prices
flipped operand and result bits with one destination, so its result bits and its destination's cells change together.

## 2. Kinds and trains

A **form** is one loop body of 128 instructions (all 32-bit encodings, head 64-byte aligned); an **image** is the
values of the registers the form names; a **kind** is a (form, image) pair, `form.image`. Every kind of one form runs
byte-identical code. Forms (sources are never written, sinks never read):

| form | body (repeated to 128 instructions) | what moves |
|---|---|---|
| `rot` | `mv d_i, s_i` (i = 0..7), then `mv d_(i+3 mod 8), s_i` (i = 0..7) | each sink receives s_m and s_(m-3) in turn |
| `rot2` | `mv d_i, s_i`, then `mv d_(i+2 mod 8), s_i` | each sink receives s_m and s_(m-2) in turn: on the images used, the same value twice |
| `res` | `and x5, x18, x19 ; or x6, x18, x19` | fixed sources; result alternates a&b, a\|b; each destination holds |
| `resf` | `and x5, x18, x19 ; or x5, x18, x19` | the same results into one destination |
| `resz` | `and x0, x18, x19 ; or x0, x18, x19` | the same results, destination x0 |
| `rd2i` | `andi x5, x0, 21 ; andi x5, x0, 26` | bits 24:20 name x21, x26; no operand used; result 0 |
| `rd2r` | `and x5, x0, x21 ; and x5, x0, x26` | x21, x26 read as the second operand; result 0 |
| `rd1u` | `lui x5, 168 ; lui x5, 208` | bits 19:15 name x21, x26; no operand used |
| `idx0`, `idx1`, `idx3`, `idx5` | `and x5, x0, x22` ; with `x23` / `x24` / `x9` in turn | the second source field changes in 0, 1, 3, 5 bits |
| `rn8` | `and x5, x0, p` over x16, x17, x19, x18, x26, x27, x25, x24 | one field bit changes a step, eight registers |
| `wn1`, `wn2`, `wn8` | `and d, x0, x0` with d = x16 / x16, x17 / the same eight | one destination, two, eight (one field bit a step) |
| `nop` | `nop` | the floor (anchor) |

For `rot` and `rot2`, s = x18..x25 and d = x11, x12, x9, x15, x30, x14, x6, x8. The two forms run the same sources in
the same order (so the same port and result streams) and differ only in the order of the destinations. The eight sinks
are chosen from the encoding so that the destination field changes in the same bits, bit position by bit position,
between instructions 1, 2, 4 and 8 apart, in `rot` and `rot2` alike (`make_images.py --check` verifies it): the two
forms' code changes the same encoding bits as often at every power-of-two distance up to eight instructions.

**The loop frame.** After the body every loop has the same words: its own `addi x10, x10, 1 ; csrr x13, hpmcounter3 ;
bltu x13, x28, head` (131 instructions an iteration), on registers that no form names and that are written out in the
assembly, so no compiler chooses them; then 29 copies of `addi x28, x28, 2` (the deadline register is dead once the
loop ends; they run once, at its end), so the 64-byte block holding the branch and the block after it are the same
bytes in every form. That instruction's fields are chosen from the encoding so that where a body meets the frame, the
two kinds of each train change about the same number of fetched bits, at every aligned block size from 8 to 64 bytes
with or without the block after the branch: 0 for the same-form trains, T5 and T12, at most 4 bits an iteration for
T1, T2 and T15, at most 14 for T6 and T13 (`make_images.py --frame`; `check_elf.py` checks the frame word for word
in every loop of the built kernel). The second sitting's T7 and T14 are equal in every per-instruction count but not
at a coarser grain: their two bodies differ by about 250 fetched-bit changes an iteration at 8- and 16-byte blocks
(about 2 a body instruction) and by at most 4 from 32 bytes up (`--frame`). If this core's front end moves the
instruction stream in 8- or 16-byte units, T7 and T14 carry that difference too: a non-zero T7 or T14 is then not a
register-file price alone, and their BOUNDED reading bounds the two together.

Images: M is a fixed 64-bit word with 32 ones (seeded); `x64` = the sources alternate M and ~M (every `rot` write
changes all 64 cells of its sink, every `rot2` write none; the port and the result change in 64 bits an instruction in
both); `x0` = every source M (no cell changes in either form); `k0`/`k32`/`k64` = (a, b) with a = b = M, 32 bits apart
(32 ones each), b = ~a; `d64` = (M, ~M); `e0` = both 0; `e32` = both M; `e64` = both all ones; `z` = every named register 0.
`make_images.py --list` prints every kind's designed counts per instruction (`f1`, `f2`: bits changing in the
registers the two source fields name; `res`; `cell`; `i1`, `i2`, `iw`: field bits; `enc`; `h1`, `h2`: held ones), and
`--check` re-derives them from the values.

**The trains** (`src/trains.tsv`). A train is a number of device processes back to back; each process is 13 launches
of 0.4 s in one process (launch 0 settles, then three quads S F F S or F S S F, the orientation alternating process to
process), and every quad reads D(F) - D(S): the public lab repo's train form (E182, E183), which reads a pair to a few
milliwatts and cancels drift inside a quad. Designed differences per instruction, F minus S:

| train | F | S | processes | changes, F - S, per instruction | role |
|---|---|---|---|---|---|
| T2 | `rot.x0` | `rot2.x0` | 18 | none (every count equal) | check for T1: the destination order alone, zero by design |
| T1 | `rot.x64` | `rot2.x64` | 134 (+230 in the second sitting) | cell +64 | stored bits |
| T3 | `res.k64` | `res.k0` | 18 | res +64 | result bits along the result path |
| T5 | `resf.k0` | `resz.k0` | 52 | one write to x5 (value unchanged) against x0 | a write |
| T6 | `wn2.z` | `wn1.z` | 18 | iw +1 | two destinations against one |
| T4 | `res.k32` | `res.k0` | 18 | res +32 | linearity of T3 |
| T8 | `rd2i.d64` | `rd2i.e0` | 18 | f2 +64 (if the named register is read); h2 +32 | port 2, field only |
| T10 | `rd2r.d64` | `rd2r.e0` | 18 | f2 +64, a2 +64; h2 +32 | port 2 as the operand, result held |
| T9 | `rd2i.e64` | `rd2i.e0` | 26 | h2 +64 held ones; f2 0 | held ones, no change |
| T11 | `rd1u.d64` | `rd1u.e0` | 18 | f1 +64 (if read); h1 +32 | port 1, field only |
| T13 | `idx1.z` | `idx0.z` | 26 | i2 +1 (and a change of register) | the first field bit |
| T12 | `idx5.z` | `idx1.z` | 18 | i2 +4 | four more field bits |
| T15 | `idx3.z` | `idx1.z` | 18 | i2 +2 | two more field bits (the ladder's middle rung) |
| T7 | `wn8.z` | `wn2.z` | 18, second sitting | 0 (one field bit a step in both) | eight destinations against two (bounded) |
| T14 | `rn8.z` | `idx1.z` | 18, second sitting | 0 (one field bit a step in both) | eight source registers against two (bounded) |

The F kinds of T8, T10 and T11 hold 32 ones in each named register (h2 or h1 +32 an instruction), as `e64` holds 64
and `e0` none: T9 prices the held ones alone, and (T8 - T9/2)/64 is reported beside the port-2 price as that price
less their share. The zeros image is the baseline of all four because a read that switches between two registers
holding the same ones is the case T9 measures, whatever it costs; it is kept out of the port arms. T9's F kind also
stores 128 more ones than its S kind (and the d64 kinds 64 more than e0): any static difference that makes (leakage by
stored value) rides on those trains, unseparated, and is expected small beside them. T3 and T4 price the whole result
path, of which the register file's write is one part; no arm here splits the file's share from the rest.

**Blocks.** First sitting: A (T2, T1), B (T3, T5, T6, T4), C (T8, T10, T9, T11), D (T13, T12, T15), in that order
(each train's first orientation from a fixed seed). The short plan (if the window cannot fit the full one) keeps T1,
T2, T3, T5, T8, T10, T12, T13. An optional second sitting (block E: 230 more processes of T1, then T7 and T14) runs
only in a window of its own; its T1 units pool with block A's.

**Anchors**: each block opens with `nop.z`, `res.k0`, `res.k64` as 3 s bursts of 0.4 s launches, each after 4.5 s of
idle, and closes with them in reverse. They measure the card's state across the session, give each block's
over-idle levels on the board and the core rail, give the core rail's share of a data-dependent difference
(`res.k64 - nop.z`: the trains read the board only), and calibrate the train method: `res.k64 - res.k0` as bursts is
T3 in expectation, so T3 over it is the train's gain, reported beside every price.

## 3. Cores, harts, card, clock

All 32 shires x 32 minions, hart 0 of each (one instruction stream per pipeline: a second hart would interleave
two streams and the designed neighbours would be lost). Hart 1 of every minion returns to the firmware at once. The
loop reads `hpmcounter3` once an iteration; the public errata ask for four reads in one aligned half line when both
threads of a core read different counters within 3 cycles, which does not arise with one thread in the loop as long
as the returned thread reads no counter: each launch reports the fewest iterations of any hart (`iters_min`), and a
launch where a hart falls more than 1 % below the mean hart is reported. Reference card: **lab host 3, card 0,
pinned 600 MHz**, lock `shire0`. Before opening anything the host counts the card nodes; on a host with several cards
it runs only when `ET_DEVICES` names one and the linked device layer reads it; after opening, the runtime must list
exactly one device. The host's own text never spells the selection variable's name (it assembles it at run time from
a reversed literal), so that the lab's `grep -aqw` test on the binary answers what it asks: whether the linked device
layer reads it. Built here, the binary carries no copy, so on a several-card host it refuses unless that host's device
layer carries one. No change of voltage, frequency, firmware, governor or fan; no root.

## 4. What is measured, and how

Board power (`board_w`, 12 V input), the minion rail with its voltage, die temperature and `mhz.minion`, from one
sampler at 10 Hz for the whole session, started first and stopped with SIGTERM only at the end; on this card the
lab's per-sensor sampler is preferred, the plain one is the fallback. Each train process is one device process under
`timeout -k 1 10`, with `--stop-file OUT/STOP`. No heater: inside a train two kinds alternate launch by launch from
one thermal state; every kind draws a few watts over the card at rest.

**Reduction, registered before any datum** (`src/reduce_regfile.py`):
- A launch's reading: the mean of the board samples in [its start + 170 ms, its end] after two dip rules (the lab's:
  a sample more than 4.0 W below both samples two away; and, because a low reading is held for a whole meter pass,
  a sample more than 4.0 W below the median of the 11 samples centred on it); fewer than 2 samples: no reading.
- A quad: s (L2 + L3 - L1 - L4) / 2, s = +1 in SFFS, -1 in FSSF; a process's value: the mean of its complete quads;
  a unit: processes 2j and 2j+1 of a train in one block of one session, when both give a value; the train's estimate:
  the mean over units (all blocks, all sessions: a second sitting pools), t(0.975, n - 1). Processes are keyed by
  (session, block, process number); the smoke block's two processes carry the label `smoke` and enter no train.
- **Gates.** A process gives no value with other than 13 launches, a launch not ok or with `check_bad` > 0, a launch
  reporting other than 1,024 participants, letters off plan, a non-zero exit, a launch's device rate more than 0.5 %
  off the train's median, a sample off the session's clock by more than 1 MHz, or a STOP written before its last
  launch ended (the scripts write the time into STOP; one made by hand carries none, and the reducer takes the file's
  modification time as the block read it on the box, else the file's own). A train is NOT
  SCORED with fewer than 8 units, or when the median device rates of its F and its S launches differ by more than
  0.05 % (an issue-rate difference between the kinds would change the power without changing the event; the ratio
  F/S is printed beside every train and every price). A derived price is NOT SCORED when any train in it is.
- Energy per instruction: D / R, R the train's median device rate (body instructions a second over all harts). Board
  energy; electrons through the 12 V input E / (e x 12 V) (the input's voltage is not metered: 12 V nominal); the
  core rail with the anchors' measured rail share, electrons E_rail / (e x V_rail) at the rail's measured voltage.
- Derived prices (each a combination of independent trains): `cell` = T1/64; `cell_ctrl` = (T1 - T2)/64; `order` =
  T2; `result_bit` = T3/64; `result_bit32` = T4/32; `lin_result` = T4 - T3/2; `write` = T5; `dest_switch` = T6;
  `read2_field` = T8/64; `read2_net` = (T8 - T9/2)/64; `held_one` = T9/128; `read2_operand` = T10/64; `operand_path`
  = (T10 - T8)/64; `read1_field` = T11/64; `field_bit` = T12/4; `field_bit3` = T15/2; `lin_field` = T15 - T12/2;
  `field_first` = T13; `field_base` = T13 - T12/4; second sitting: `dest_n8` = T7, `read_n8` = T14.
- **Verdicts.** POSITIVE / NEGATIVE when the 95 % interval excludes 0, else NOT RESOLVED. The five prices that are zero
  by design or by a linear law (`order`, `lin_result`, `lin_field`, `dest_n8`, `read_n8`) read BOUNDED when the
  interval holds 0, the bound being the interval itself, printed in W and in fJ an instruction (at the planned sizes
  about +-0.028 W, +-56 fJ an instruction at 5.0 x 10^11, for an 18-process train); else POSITIVE / NEGATIVE. SIZE words against
  each frozen forecast line, by a separate agent after the data.
- **Reading rules.** `cell` (T1/64) is the stored-bit price when `order` (T2) reads BOUNDED; when T2 reads POSITIVE or
  NEGATIVE, `cell_ctrl` is read first and the reason printed. When the train gain lies outside 0.95-1.05, the
  gain-corrected prices are read first.
- Beside, never a verdict: each train's carry-over (L3 - L2 by orientation), the train gain (T3 over the anchors'
  burst difference) and every price divided by it, the anchors per block, and the reports of section 7.

## 5. Rates, joules per event, and the signal budget

Rate: 1,024 harts at 600 MHz; the open emulator runs every kind at 131 instructions an iteration (section 6); the
card's issue rate for this loop is measured per launch. For sizing, from the catalogue's public figures: its one-hart
add loop runs 0.581 adds a cycle, 64 adds in about 110 cycles, so about 46 cycles go to its tail of four counter
reads, a compare and a branch. A 128-instruction body with that whole tail would run 128/174 of 1,024 x 600 MHz,
4.5 x 10^11 body instructions a second; with this loop's single counter read, about a quarter of that tail (12
cycles), 128/140, 5.6 x 10^11. Sizing uses 4.5 to 5.6 x 10^11 (5.0 x 10^11 central): there 1 fJ per instruction is
0.5 mW.

Floor: the train form's measured noise on a 0.4 s-launch loop (E183: quad sd 0.069 W, reach 1.30 of plan), so a
train of n processes has a standard error of about 0.090 / sqrt(3 n) W: 0.0045 W at 134 processes, 0.0072 at 52,
0.0102 at 26, 0.0122 at 18, 0.0027 for T1 with the second sitting (364); 95 % half-widths about twice these (E183's
committed trains on this card read about a fifth narrower than this floor).
###### [LAB REDACTION R1, written Sun 15 Nov 2026 21:56 PST (Q191, lane fix-e197), before any E197 datum: in lines 207-237 every number (each digit run with its decimals; names such as T13 and E189 kept) is replaced by [withheld] until the model session's private scoring of E197. Why: the proposal calls these lines "the frozen top-down lines"; they may hold its sealed forecast's own numbers, and the lab publishes no forecast number before the data (asked in the owner's private coordination thread, topic #7, at 21:33:26 PST Sun 15 Nov 2026; no answer by 21:36:09). Lines 1-205 and 238-417 are the received file's, byte for byte; this line, 206, was blank; lines 207-237 keep every word and mark. The received file (revision 3, 41,068 B) has sha256 9de88ef46ca77fdffe7077844927987e77646d40f3baebbac7a96ddd558877f0; E197.md section 0 registers it and the withheld lines' own sha256; the full file is added after the private scoring, as a new file, never an edit of this one.]
Sizing at the lab's public prices (one scalar pair for every port and result line: the catalogue's add data
dependence, [withheld] to [withheld] pJ an add over [withheld] flipped port bits and [withheld] to [withheld] result bits, split by the vector unit's
port : result ratio [withheld] : [withheld], which gives [withheld] fJ a port bit and [withheld] fJ a result bit, the vector unit's own
prices as the low band). The bit counts are the catalogue's random operands: each [withheld]-bit word holds two floats in
[[withheld], [withheld]), [withheld] random bits apiece (the mantissa and the exponent's last bit), so about [withheld] bits change in each operand
from one add to the next ([withheld] at the two ports) and [withheld] to [withheld] in the sum (half its random bits, carries included). The
held-operand price below is E183 round [withheld]'s rule c: [withheld] fJ an instruction for one more [withheld]-bit held in each lane's
operand word in both sources, over eight lanes and two sources, [withheld] fJ a held bit. These are the frozen top-down
lines, at [withheld] x [withheld]^[withheld]:

| train | public price used | board pJ an instruction | W | over the train's SE |
|---|---|---|---|---|
| T1 | [withheld] cell bits at the register-file cell price ([withheld] fJ; E61, E74's bound [withheld]); the field changes alike | [withheld] | [withheld] | [withheld]x ([withheld]x with the second sitting) |
| T2 | zero by design | [withheld] | [withheld] | bound about +-[withheld] W |
| T3 | [withheld] result bits at [withheld] fJ | [withheld] | [withheld] | [withheld]x |
| T4 | [withheld] of the same | [withheld] | [withheld] | [withheld]x |
| T5 | a [withheld]-bit register clocked once ([withheld]-[withheld] fJ a bit edge, E109 post hoc) | [withheld] | [withheld] | [withheld]x |
| T6, T13 | one field bit at the vector unit's read-index price ([withheld]-[withheld] fJ, E61) | [withheld] | [withheld] | [withheld]x, [withheld]x |
| T12 | four of the same | [withheld] | [withheld] | [withheld]x |
| T15 | two of the same | [withheld] | [withheld] | [withheld]x |
| T8, T11 | [withheld] if the named register is not read; if it is read like a used port: [withheld] bits at [withheld] fJ | [withheld] ([withheld]) | [withheld] ([withheld]) | ([withheld]x) |
| T9 | [withheld] if not read; if read: [withheld] held ones at the held-operand price ([withheld] fJ a bit, E183) | [withheld] ([withheld]) | [withheld] ([withheld]) | ([withheld]x) |
| T10 | [withheld] read-port bits into a result-constant op at [withheld] fJ | [withheld] | [withheld] | [withheld]x |
| T7, T14 | zero (second sitting) | [withheld] | [withheld] | bound about +-[withheld] W |

The study's rule [withheld] (the smallest step at least ten times the floor) holds here for T3, T4, T6, T10, T12, T13, T15 (and
T8, T11 if the field is read); T1 sits at [withheld]x and is registered as an interval result at the first sitting's size (the
second sitting takes it to about [withheld]x); T5 and T9 sit under [withheld]x at these prices: they are kept because the vector-unit
and post-hoc prices are poor guides to the scalar file, and a bound is a result. A ladder step of [withheld] W and a lone
contrast of [withheld] W, the catalogue protocol's rule of thumb, are met only by the trains of [withheld] W and more; the train form
reads a pair to about [withheld] W, which is why it is used.

## 6. Denominators

Per hart: cycles (`hpmcounter3`) and loop iterations (body instructions = iterations x 128), with the fewest and
most iterations of any hart. Per neighbourhood (counted once): thread-0 instructions retired (`hpmcounter4`, before
and after the loop; expected retired / body = 131/128 within 0.1 % plus the fixed entry and exit),
instruction-cache requests and misses (`hpmcounter7`, `hpmcounter8`), L1 data misses (`hpmcounter6`, expected 0 in
the loop). The clock from the sampler. Every launch checks every written register against the kind's model
(`check_bad`).

**Emulator here** (the open system emulator, the kernel of this request built with the open SDK, one minion, a
20,000-cycle window, one launch per kind, one session; 184 s): every kind ran 153 iterations = 19,584 body
instructions; the retired counter read 21,400-21,462 (the loop's 153 x 131 = 20,043 plus 1,357-1,419 of kernel entry
and exit, the frame's 29 closing words included: the forms that load and store more registers take more);
`check_bad` 0 on all 34 kinds; every hart's iterations equal (one hart); the instruction-cache counters read 0 in the
emulator (not modelled) and its cycle count is not timing. Rerun for revision 3 (the same kernel ELF): the same
iterations, body instructions, retired counts and checks on all 34 kinds; and one train process of T1's kinds (13
launches, letters S then S F F S three times): every launch ok, `check_bad` 0, 153 iterations each, the image switching
between launches inside one process.

| kind | iterations | body | retired | retired - loop | check | kind | iterations | body | retired | retired - loop | check |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `rot.x64` | 153 | 19584 | 21462 | 1419 | ok | `rd2r.d64` | 153 | 19584 | 21414 | 1371 | ok |
| `rot2.x64` | 153 | 19584 | 21458 | 1415 | ok | `rd2r.e32` | 153 | 19584 | 21414 | 1371 | ok |
| `rot.x0` | 153 | 19584 | 21462 | 1419 | ok | `rd2r.e0` | 153 | 19584 | 21414 | 1371 | ok |
| `rot2.x0` | 153 | 19584 | 21458 | 1415 | ok | `rd2r.e64` | 153 | 19584 | 21414 | 1371 | ok |
| `res.k0` | 153 | 19584 | 21420 | 1377 | ok | `rd1u.d64` | 153 | 19584 | 21414 | 1371 | ok |
| `res.k32` | 153 | 19584 | 21420 | 1377 | ok | `rd1u.e32` | 153 | 19584 | 21414 | 1371 | ok |
| `res.k64` | 153 | 19584 | 21420 | 1377 | ok | `rd1u.e0` | 153 | 19584 | 21414 | 1371 | ok |
| `resf.k0` | 153 | 19584 | 21413 | 1370 | ok | `rd1u.e64` | 153 | 19584 | 21414 | 1371 | ok |
| `resf.k32` | 153 | 19584 | 21413 | 1370 | ok | `idx0.z` | 153 | 19584 | 21412 | 1369 | ok |
| `resf.k64` | 153 | 19584 | 21413 | 1370 | ok | `idx1.z` | 153 | 19584 | 21416 | 1373 | ok |
| `resz.k0` | 153 | 19584 | 21413 | 1370 | ok | `idx3.z` | 153 | 19584 | 21414 | 1371 | ok |
| `resz.k32` | 153 | 19584 | 21413 | 1370 | ok | `idx5.z` | 153 | 19584 | 21415 | 1372 | ok |
| `resz.k64` | 153 | 19584 | 21413 | 1370 | ok | `rn8.z` | 153 | 19584 | 21443 | 1400 | ok |
| `rd2i.d64` | 153 | 19584 | 21415 | 1372 | ok | `wn1.z` | 153 | 19584 | 21401 | 1358 | ok |
| `rd2i.e32` | 153 | 19584 | 21415 | 1372 | ok | `wn2.z` | 153 | 19584 | 21413 | 1370 | ok |
| `rd2i.e0` | 153 | 19584 | 21415 | 1372 | ok | `wn8.z` | 153 | 19584 | 21428 | 1385 | ok |
| `rd2i.e64` | 153 | 19584 | 21415 | 1372 | ok | `nop.z` | 153 | 19584 | 21400 | 1357 | ok |

(`rd2i.e32`, `rd2r.e32`, `rd2r.e64`, `rd1u.e32`, `rd1u.e64`, `resf.k32`, `resf.k64`, `resz.k32`, `resz.k64` are in the
kernel and the emulator run but in no train.)

## 7. Sanity checks (registered before the data; each a gate or a report)

| check | gate or report | consequence |
|---|---|---|
| `check_bad` = 0, the launch ok | gate | the process gives no value |
| 1,024 participants on every launch | gate | the process gives no value |
| every sample of a train process within 1 MHz of the session's clock (600 MHz) | gate | the process gives no value |
| a launch's device rate within 0.5 % of its train's median | gate | the process gives no value |
| the median rates of a train's F and S launches within 0.05 % | gate | the train is NOT SCORED (its estimate printed beside) |
| at least 8 units in a train | gate | the train is NOT SCORED |
| retired / body within 0.5 % of 131/128 plus the entry and exit, per kind | report | flagged beside the train |
| L1 data misses 0 in the loop; instruction-cache misses per iteration equal for F and S | report | printed beside the train |
| a hart's iterations within 1 % of the mean hart's, every launch | report | launches counted beside the train |
| rail voltage within +-3 mV of the session median in the trains' spans | report | samples counted beside the train |
| the anchors' first and last bursts of a block within 0.3 W | report | flagged per block and kind |
| the train gain (T3 over the anchors' burst difference) within 0.95-1.05 | report and reading rule | outside it, the gain-corrected prices are read first |
| the smoke gate: 26 launches ok, letters as planned, rates within 3 % | gate (run time) | no train block runs (exit 7) |
| a fresh OUT: no file of an earlier session in it | gate (run time) | refused before anything opens (exit 2) |
| a device process killed by its timeout or a signal; two failed device processes in a row | stop (run time) | `OUT/STOP`, the session ends (exit 5) |
| charge per instruction (energy / V) is what the electron counts use | convention | |

## 8. Box and card constraints; what must not be done

- Run a session only inside a window that the lab session has named for this request: the reference scripts' holder
  check sees other users' device processes and the card's holders and locks, not the queue of the same account
  between that queue's blocks.
- Nothing opens a card node, and no sampler starts, until the card is free: `et-who --check` exits 0, no other
  user's device process runs, and a probe of the card lock succeeds (`src/run_session.sh`; exit 3 otherwise). One
  card only: on a host with several cards `ET_DEVICES` must name one and every binary run must read it (exit 2).
- A fresh OUT for every session (the reducer pools several): a folder holding a file of an earlier session is refused
  before anything opens (exit 2), because its `SESSION_DONE` would end the live stops at once and its records would
  mix two sessions.
- One sampler for the session, nothing else on the management node; it is stopped with SIGTERM by the session's EXIT
  trap, always, and at once when the session ends on a holder, a busy lock, a stop or a failure. Card lock per block,
  the existing lock file opened read-only and taken with `flock -n`, never waited for; every device process of the
  block keeps the lock's descriptor, and the lock is released by closing it, never by an explicit unlock, so it lasts
  while any of them runs. The smoke block and block A run back to back (the lock free only while the holder check is
  made); between two blocks of `trains.tsv` it is released for 30 s; before every block the holder check is repeated
  (only this session's own sampler may hold a node); a holder stops the session.
- Each device process under `timeout -k 1 10`, with `--stop-file`; `OUT/STOP` stops within one 0.4 s launch. The
  host starts no launch that could end after its 8.5 s budget, in every mode, and no train process starts unless it
  would end before the session's cap less 60 s even at its timeout's 11 s bound. A device process killed by its
  timeout or a signal, or two failed device processes in a row, write `OUT/STOP` and end the session (exit 5).
  `-k 1` sends KILL to a host still there 1 s after its timeout's TERM (a hang in teardown); the lab's own kits use
  plain `timeout 10` and the field manual's
  never-list names kill -9, so the lab session either accepts `-k 1` for this request's own processes or the operator
  drops it (one line: `TIMEOUT` in `src/run_trains.py`).
- A TERM, INT or HUP to the session writes `OUT/STOP` at once; the device process in flight ends after its launch (it
  is sent TERM if it is still there 5 s later); then the sampler is stopped (0.14-0.26 s from the signal to the end,
  on the stand-in card of section 11).
- Live stops (`src/stopwatch.py`, on the session's telemetry): board above 65 W on three distinct readings in a row,
  die reading at or above 70 C, or a sampler gone quiet for 10 s; `run_trains.py` also stops on a die reading at or
  above 70 C or telemetry older than 5 s. A stopwatch that finds `SESSION_DONE` already there when it starts (a used
  OUT, the second guard) writes `OUT/STOP`.
- No change of voltage, clock, firmware, governor, fan; no `et-reset`, no root, no other user's process.
- Build in a folder of our own (`~/claude/work/ee-1113-x02-regfile/`), never in the lab session's trees. The kernel
  built on the box need not have this request's ELF sha256 (the box's SDK may differ): `src/check_elf.py` on the box's
  own build is the gate (every loop word for word, the frame included), and the box ELF's sha256 is recorded with
  the data; the emulator counts above are this box's build.
- No host compute beside the run; no simulation on the lab box.
- To be supplied by the lab session's kit, as for its own runs: the login check, the device-command audit, the
  40-minute rest rule on this card, the dry run (`DRY=1 bash src/run_session.sh OUT full` prints every device call:
  429 for the full plan, 331 for the short, 277 for the second sitting). The reference scripts make the holder check
  and the lock probe themselves (above).

## 9. Card time

Train processes about 5.6-5.8 s each (13 launches of 0.4 s and the device's opening and closing; E183 measured 5.63 s
start to start), 400 of them in the first sitting; 24 anchor bursts at about 8.2 s with their idle; 10 s idles at
both ends of four blocks; three 30 s gaps between blocks; the smoke and a stop-path test: **about 45 card-minutes full
(cap 50, `CAP_S` 3,000 s)**, about 36 short (cap 40); the optional second sitting about 28 (cap 35). At 6.2 s a
process every train still starts before its cap (48, 38 and 30 card-minutes). Lab host 3 card 0, with the 40-minute
rest rule before and after each sitting; wall time about 1 h a sitting with the gaps, plus the kit's own steps.

## 10. Status and open points

- STATUS `ready` (revision 3). Two readers other than the author read revision 2's `src/` line by line: both found
  it public-safe with nothing to remove; the second made seven should-change findings on the reference session's side
  paths, all closed in revision 3 (section 11). The independent read of revision 3's diff of `src/` comes next.
  The source builds with the open SDK here (kernel and host; `check_elf.py`: 17 loops, every body and the frame word
  for word as generated; the kernel ELF is the registered one); the emulator has run every kind and one train process
  (section 6); the study's name scanner prints HITS 0 on `src/`, `request.md` and `PROPOSAL.md`; the forecast is
  frozen (`log.md`) and revision 3 changes none of it; a dry session prints every device call; the reducer recovers
  synthetic trains with known differences, a smoke block included (every scored train inside its interval in two
  clean sessions; a 263 ms held meter reads the largest train about 3 % low, which the gain shows; a 0.3 % issue-rate
  split is NOT SCORED; a second sitting pools by unit), and a stop made by hand now drops only what came after it.
- No arm needs a value from outside the public manuals and the lab repo: every image is generic (a seeded word with
  32 ones, its complement, a second seeded word 32 bits from it, zeros, all ones), the sinks and the frame's words are
  chosen from the encoding alone, and the forms and the frame use registers x5-x30 only.
- The card's issue rate for this loop is unknown until the first run (sized at 4.5-5.6 x 10^11 a second).
- The trains read the board only; the core rail's share comes from the anchors.
- Whether the per-sensor sampler is used is the lab session's call (it is a READ on this card's firmware).
- Whether the second sitting runs is the lab session's and the owner's call (a window of its own, about 28
  card-minutes); without it T1 is an interval result at the first sitting's size and T7, T14 are not run.
- The lab hosts are written "lab host 3" here and in `PROPOSAL.md` (the third of the lab's three hosts, the one
  whose card 0 is pinned at 600 MHz); the operator may put the lab's own host name back.

## 11. Revision 3: two reads of revision 2's source, and what changed

Two readers independent of the designer read revision 2's `src/` line by line. The public-safety read found it clean:
nothing to remove or change, seven notes. The builder's read found it public-safe, building with the open SDK, its
self-checks passing and every lab rule kept on the normal path, and made seven should-change findings on side paths of
the reference session (S1-S7) and six notes (its notes 1-6). Revision 3 changes `src/run_session.sh`, `src/run_trains.py`,
`src/stopwatch.py`, `src/reduce_regfile.py` (re-registered before any datum, `log.md`) and `src/BUILD.md`. The kernel,
the host, `make_images.py`, `check_elf.py`, `trains.tsv` and the two generated files are unchanged, and so is the
kernel ELF; no arm, train, kind, rate or forecast changed.

Each fix was tested here against a stand-in card: a stand-in holder check, sampler and host (the host prints the
launch records the scripts read, honours `--stop-file`, and reports whether the lock's descriptor reached it), a
stand-in lock file and a small plan. The session script under test differs from `src/` only in where it counts the
card nodes. The same tests ran revision 2's scripts for comparison.

| finding | the fault | the change | tested here: revision 2, then revision 3 |
|---|---|---|---|
| S1: a used OUT turns the live stops off | `stopwatch.py` ends when `OUT/SESSION_DONE` exists, and nothing refused an OUT that held one | `run_session.sh` refuses, before anything opens (exit 2), an OUT holding `SESSION_DONE`, `STOP`, the telemetry, the run or mark records or the error files of an earlier session (a dry run leaves only `session.log`); `stopwatch.py`, the second guard, writes `OUT/STOP` when it finds `SESSION_DONE` at its start | each of the eight files: refused; a second session into a finished session's OUT: refused; the stopwatch on such an OUT writes STOP in 0.03 s |
| S2: a stop made by hand drops the whole session in the reducer | `touch OUT/STOP` leaves an empty file, read as time 0, so every process counted as ending after the stop | a STOP's time is the t_ms of its JSON line; one without (empty, or plain text) is timed by the file's modification time as `run_trains.py` read it on the box when it saw the file (a new mark, `stop_seen`: a copy of OUT need not keep the file's own time), else by the file's own; the reducer reports the time and its source | revision 2's synthetic sessions: the same output from both reducers apart from the new report. A stop in the middle of T5 (empty; empty with its time lost in a copy; plain text): 400 of 400 train processes dropped, no train scored; now the 204 that end after it are dropped, the 196 before it kept, and T1, T2, T3 and T5 scored. A STOP with t_ms reads alike in both |
| S3: the explicit unlock frees the card while a device process still runs | `flock -u` releases the lock for every process sharing the descriptor; and no device process held it anyway (Python's subprocess closes inherited descriptors in its children by default), so closing alone would not have kept it either | no explicit unlock anywhere: the lock is released by closing; `run_trains.py --lock-fd 9` keeps the descriptor open in every device process (through `timeout`), so the lock lasts until the last of them ends; on a signal `run_trains.py` waits for its device process (S5) | a stand-in lock with a device process left running when the block's Python dies: free with the explicit unlock, still free with close only, held until it ends only with the descriptor passed on. In a session, `kill -9` of `run_trains.py` during a device process: the lock was free while it ran on; now held until it ends. The descriptor reached no device process; now every one |
| S4: failing device processes never stop a block | a non-zero exit, a process with no records or a timeout kill was only logged, and the deadline was checked only before a train | a device process killed by its timeout, ended by a signal or not started (exit 124 or more, or a signal) writes `OUT/STOP` and ends the block at once; so do two failed device processes in a row (a non-zero exit, no launch record, a launch not ok, a train process short of 13 launches): exit 5. A train process starts only if it would end before the deadline even at its timeout's 11 s bound (a mark `cut`) | every device process failing from block A on: 20 failing processes over 109 s, on into the next block; now STOP and exit 5 after the second, 19 s after the smoke. A hung device process: now killed at 10 s (exit 124), then STOP and exit 5. A 16-process train running 9 s a process against a deadline its plan fitted: all 16 ran, the last ending 12 s after the deadline; now cut before process 14, the last ending 6 s before it |
| S5: a signal to the session shell waits for the block | bash runs a trap only after the foreground command returns, so the block (about 15 minutes for block A) or the 30 s gap ran on, and the sampler with it | blocks and pauses run in the background while the shell waits (a trapped signal interrupts the wait); a TERM, INT or HUP writes `OUT/STOP` with its time at once, the device process in flight ends after its launch (sent TERM if still there 5 s later), then the sampler is stopped | TERM during a train process: the session ended 44.7 s later, with its block; now 0.18-0.26 s later, the device process ending by itself on the STOP. TERM 2 s into a 20 s gap: 18.0 s; now 0.14-0.18 s. The sampler stopped and `SESSION_DONE` written each time |
| S6: `BUILD.md`'s one-run example names a dropped kind | `rotz.x64` left in revision 2 | `rot.x64,rot2.x64` | the kind table lists `rot2.x64` |
| S7: the sampler is kept 8 s after another holder is seen | the closing 8 s pause ran whatever the session's exit | the closing pause only after a session that ended well; a STOP seen between blocks ends the session with exit 8 | a foreign holder seen before block A: the session ended 8.1 s later; now 0.12-0.18 s |

A whole session on the stand-in card (the smoke block and four blocks) ends with exit 0: the lock held during a train
process of block A and free in the gap after that block, the sampler stopped at the end, the lock's descriptor in
every device process, and a second session into the same OUT refused. The dry runs print the same device calls as
before (429, 331, 277).

Notes taken up: the builder's note 1 (section 8: `-k 1` is the lab session's to accept or drop, one line); its note 2
(`BUILD.md` and the session script's header: the smoke block and block A run back to back); its note 3 and the
public-safety read's note 7 (the T7 and T14 fetch residue, section 2); its note 4 (on a several-card host the selection
test covers the sampler in use, the per-sensor one included); the public-safety read's notes 2-5 (the designer's
label left out of the header; E192 named as the lab's registration of request 1113-x01-intbits; the derivations of
the catalogue's bit counts and of the held-operand price, section 5; why the host builds the selection variable's
name at run time, section 3). Left as they are: the public-safety read's note 1 and the builder's remark on the
extended name list (its four hits are the public lab repo's own workload name, in attribution comments: public); the
builder's notes 5 (section 8 says it) and 6 (a board meter stuck at one value above 65 W would not trip the
stopwatch; every kind draws a few watts over the card at rest).
