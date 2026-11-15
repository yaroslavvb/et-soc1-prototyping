# Request 1113-x01-intbits: scalar integer bit-flip and carry ladders

Family X01. Designer ee-x01-intbits, Fri 13 Nov 2026; revision 1 the same evening, after two reviews (isolation,
physics, statistics; public safety, feasibility). STATUS: see `STATUS`. Forecast frozen before any datum:
`prediction.json`, sha256 in `log.md` (the revision-1 line is the one in force). Source: `src/` (public-safe: written
from the public instruction set, the runtime's public interface and the public lab repo's workload and kit style;
`src/BUILD.md`).

## 1. Question

On every minion, a stream of register-to-register scalar integer instructions with no load and no store, in arms that
differ in one thing only. What does an issuing core cost per instruction (the no-op sled), and what does an add add;
then, per instruction, the price of one flipped bit on operand port A as the bits flipped grow (4, 8, 16 in one field;
32 over two fields; 64), by 16-bit field position, on port B, when the bits move from port A to port B with the
result held, when the result is held at zero by an `and`, and the price of one position of carry propagation, from two
carry ladders with different held operands. Each in pJ and in electrons per instruction through the core rail (at
its measured voltage) and through the 12 V input. The lab has priced such ladders only in the 8-lane vector integer
unit (E60, E61) and the scalar instructions only on zeros, one constant and random data (the catalogue): these scalar
ladders are new and build on both (same harness style, same meter method, the catalogue's `nop` and `add` as anchors
of scale).

## 2. Arms

A "pair" arm alternates `op x5, x6, x7` and `op x5, x28, x29` (128 pairs per loop body); "same" repeats
`op x5, x6, x7`; "nop" is the 32-bit `nop`. Every loop body is 256 instructions plus the loop's own `addi`, `csrr`,
`bltu` (259 per iteration), all 32-bit encodings, head 64-byte aligned (`src/check_elf.py` checks all 16 loops; the
kernel ELF is unchanged from the first version, sha256 50cb1d64...). The four sources are fixed per arm and the same
on every hart; the background bits are fixed random values (seed 1) with the two sources' ones disjoint, so outside
the carry arms an add has no carries and its result equals the xor; the `and` of the sources is zero throughout.
Fields: f0 = bits 0-15, f1 = 16-31, f2 = 32-47, f3 = 48-63; `add.a.f2.k4` and `.k8` flip bits 32-35 and 32-39;
`add.a.f12` flips bits 16-47.

Carry ladders, both from bit 16 and inside bits 16-47 (L = 0, 8, 16, 24, 31):
- `add.cr.lL` (result held): A = (run of L ones from bit 16) + (one at bit 16), carrying L positions; B = (one at bit
  16+L) + 0. The result is held; port A changes in L+1 bits, port B in one.
- `add.crb.lL` (port A held): port A holds the run of L ones in both instructions; port B alternates 0 and one at bit
  16. The carry runs L positions; port B changes in one bit; the result changes in L+1 bits.
`add.ripple` (all ones + 0, then all ones + 1) is kept as a demonstration and reported alone, outside every fit.

Designed changes per instruction between neighbours (bits) and the control each arm is differenced against in the
same pass (the forecast for each arm is sealed in `prediction.json`; only its sha256 is given here):

| arm | form, op | port A | port B | result | carry | enc | control | role |
|---|---|---|---|---|---|---|---|---|
| `nop` | nop nop | 0 | 0 | 0 | 0 | 0 | - | floor |
| `add.same` | same add | 0 | 0 | 0 | 0 | 0 | `nop` | lone contrast |
| `add.z` | pair add | 0 | 0 | 0 | 0 | 6 | `add.same` | lone contrast; zero rung |
| `xor.z` | pair xor | 0 | 0 | 0 | 0 | 6 | `add.z` | lone contrast |
| `and.z` | pair and | 0 | 0 | 0 | 0 | 6 | `add.z` | lone contrast; zero rung |
| `add.a.f0` | pair add | 16 | 0 | 16 | 0 | 6 | `add.z` | field ladder (reported alone) |
| `add.a.f1` | pair add | 16 | 0 | 16 | 0 | 6 | `add.z` | field ladder |
| `add.a.f2` | pair add | 16 | 0 | 16 | 0 | 6 | `add.z` | Hamming ladder (f2) |
| `add.a.f3` | pair add | 16 | 0 | 16 | 0 | 6 | `add.z` | field ladder |
| `add.a.f2.k4` | pair add | 4 | 0 | 4 | 0 | 6 | `add.z` | Hamming ladder (f2) |
| `add.a.f2.k8` | pair add | 8 | 0 | 8 | 0 | 6 | `add.z` | Hamming ladder (f2) |
| `add.a.f12` | pair add | 32 | 0 | 32 | 0 | 6 | `add.z` | field ladder |
| `add.a.all` | pair add | 64 | 0 | 64 | 0 | 6 | `add.z` | field ladder |
| `add.b.f0` | pair add | 0 | 16 | 16 | 0 | 6 | `add.z` | reported alone |
| `add.b.f2` | pair add | 0 | 16 | 16 | 0 | 6 | `add.z` | port ladder |
| `add.s.f0` | pair add | 16 | 16 | 0 | 0 | 6 | `add.z` | reported alone |
| `add.s.f2` | pair add | 16 | 16 | 0 | 0 | 6 | `add.z` | port ladder |
| `xor.a.f2` | pair xor | 16 | 0 | 16 | 0 | 6 | `xor.z` | lone contrast vs add.a.f2 |
| `and.a.f1` | pair and | 16 | 0 | 0 | 0 | 6 | `and.z` | and fields |
| `and.a.f2` | pair and | 16 | 0 | 0 | 0 | 6 | `and.z` | and fields |
| `and.a.f3` | pair and | 16 | 0 | 0 | 0 | 6 | `and.z` | and fields |
| `add.cr.l0` | pair add | 1 | 1 | 0 | 0 | 6 | `add.z` | carry ladder, result held |
| `add.cr.l8` | pair add | 9 | 1 | 0 | 8 | 6 | `add.cr.l0` | carry ladder, result held |
| `add.cr.l16` | pair add | 17 | 1 | 0 | 16 | 6 | `add.cr.l0` | carry ladder, result held |
| `add.cr.l24` | pair add | 25 | 1 | 0 | 24 | 6 | `add.cr.l0` | carry ladder, result held |
| `add.cr.l31` | pair add | 32 | 1 | 0 | 31 | 6 | `add.cr.l0` | carry ladder, result held |
| `add.crb.l0` | pair add | 0 | 1 | 1 | 0 | 6 | `add.z` | carry ladder, port A held |
| `add.crb.l8` | pair add | 0 | 1 | 9 | 8 | 6 | `add.crb.l0` | carry ladder, port A held |
| `add.crb.l16` | pair add | 0 | 1 | 17 | 16 | 6 | `add.crb.l0` | carry ladder, port A held |
| `add.crb.l24` | pair add | 0 | 1 | 25 | 24 | 6 | `add.crb.l0` | carry ladder, port A held |
| `add.crb.l31` | pair add | 0 | 1 | 32 | 31 | 6 | `add.crb.l0` | carry ladder, port A held |
| `add.ripple` | pair add | 0 | 1 | 64 | 63 | 6 | `add.z` | reported alone |

The anchor is `add.a.f2`, run first and last in every pass. `intbits_host --list` prints every arm's four values.
Removed in revision 1: the two split-destination arms (their difference was below what eight passes resolve), the
47-position carry rungs (they crossed into field 3; the ladders now stay inside bits 16-47), `add.a.hi32` (replaced by
the f2 count ladder and `add.a.f12`) and `xor.a.f0`.

## 3. Cores, harts, card, clock

All 32 shires x 32 minions, hart 0 of each (one instruction stream per pipeline: two harts would interleave two
streams and the designed neighbours would be lost). Reference card: **aifoundry3 card 0, pinned 600 MHz**, lock
`shire0`. Before opening anything the host counts the card nodes and runs on a host with several cards only when `ET_DEVICES`
names one and the linked device layer reads it; after opening, the runtime must list exactly one device. No change of
voltage, frequency, firmware, governor or fan; no root.

## 4. What is measured, and how

Board power (`board_w`, 12 V input), the minion rail with its voltage, die temperature and `mhz.minion`, from one
sampler at 10 Hz for the whole session, started first and stopped with SIGTERM only at the end. On this card the lab's
per-sensor sampler (`SAMPLER=pvt`) also gives the 34 raw temperature codes (0.06 C a code); it is preferred, and the
plain sampler is the fallback. Per run: one device process under `timeout 10`, 0.4 s launches back to back for 4 s,
`--stop-file OUT/STOP`. Before every run the lab's E78 approach: heater launches up to 59 C, idle down to 58 C, at least
2 s with no device process (`src/run_block.py`; each run's record carries its approach, including any wait that timed
out). Per pass (one block, card lock held): 10 s idle (marked), two unrecorded burn-in runs of the anchor, the anchor,
the 31 other arms shuffled by `hostname|pass`, the anchor, 10 s idle (marked). A smoke block of three arms first. 9
passes, the first a registered warm-up set aside: 8 measured passes.

**Reduction, registered before any datum** (`src/reduce_intbits.py`, sha256 in `log.md`):
- Board window seconds 1-3 of the run; **dip rule**: a board sample more than 2 W below the window's median is dropped,
  and the count is reported per arm. Rail: from 2.5 s to the end, over the pass's idle, divided by the fraction a
  first-order average with tau 1.05 s reaches over that window (about 0.95), so `(P_rail - P_idle) / frac`.
- Rate on the lab's basis: body instructions over the wall time from the first launch's start to the last launch's end
  (the gaps between launches are in the time and in the power window). The device rate is reported beside it.
- Anchor drift out linearly in run order. Idle per pass from the marked idle periods (7 s each side).
- **Temperature**: per run the window mean of the raw-code mean (or of the whole-degree reading). A pooled slope of
  arm-minus-control power on arm-minus-control temperature, one intercept per pair, is fitted over all pairs of all
  used passes, per meter, and every arm is corrected to the temperature of its control chain (primary); uncorrected
  values are reported beside. The per-arm energy over idle carries the lab's leakage correction
  `23.257/36 * exp((T-80)/36)` W per C times (T_run - T_idle).
- Energies: E = (P - P_idle) / rate per arm; contrasts E_arm - E_control in the same pass; mean and SE over the 8 used
  passes (the pass is the unit of replication). A lone contrast whose 95 % interval contains zero is reported as a
  bound.
- Ladders per pass, then mean and SE: the f2 count slope and its quadratic term (K = 0, 4, 8, 16); per-bit field prices
  (f0-f3, f12) and additivity (`add.a.all` against the four fields; `add.a.f12` against f1 + f2); the `and` field
  prices (f1-f3) and `and12` (mean of f1, f2); `d12 = a12 - and12`; f2 minus f3 for `add` and for `and`; the slopes
  `S_cr`, `S_crb` on L and their quadratic terms; **C1 = (S_cr + S_crb - a12) / 2**, which under a model linear in the
  flips of each port, of the result and of the carry vector is the price of one carry position; C2 and C3 (formulas in
  the reducer). Field 0 arms and `add.ripple` are reported alone.

## 5. Rates, joules per event, and the signal budget

Assumed for the budget: 3.82e11 instructions a second (1,024 minions x 600 MHz x 0.622, the lab's one-hart rate for
its short `addi` loop; with 259-instruction bodies the card rate may be 0.9-1.0 per cycle, which makes every step
larger); measured per run. At that rate 1 pJ per instruction is 0.38 W; one flipped bit at the vector unit's prices
(20.8 fJ a port bit, 31.2 fJ a result bit) is 8-12 mW.

Floor: E60's 0.032 W rms per run about its line on this card, 8 passes. Expected standard errors (board, at the
budget's rate): a single arm-control contrast 0.016 W (42 fJ per instruction); a per-bit price from one 16-bit field
2.6 fJ, from `add.a.f12` 1.3 fJ; a carry-ladder slope 1.2 fJ per position (span 0.014 W); the f2 count slope 2.5 fJ
per bit; **C1 about 1.1 fJ**; `and12` 1.9 fJ; f2 minus f3 3.7 fJ per bit.

Sizing (not a forecast): the smallest rung of each ladder in designed bits, priced at the vector unit's public per-bit
prices above, with no price for a carry position (the lab has none), at the budget's rate:

| ladder | rungs | smallest rung (designed bits per instruction) | at the public prices | over single-contrast SE |
|---|---|---|---|---|
| f2 count | K 0, 4, 8, 16 | 4 port A + 4 result | 0.079 W | 5x |
| result-held carry | L 0, 8, 16, 24, 31 | 7 port A (L 24 to 31) | 0.056 W | 3.5x |
| port-held carry | L 0, 8, 16, 24, 31 | 7 result (L 24 to 31) | 0.083 W | 5x |
| fields, f12 | 16, 32 bits | 16 port A + 16 result | 0.32 W | 20x |

The ladder steps are rungs of a fit, not decisions on their own; the per-step resolution (3.5-5 times at these
prices) is what rule 3's "lengthen, widen or drop" was weighed against. The lone contrasts (`add.same - nop`, `add.z - add.same`, `xor.z`, `and.z`, `xor.a.f2 - xor.z` against
`add.a.f2`) are registered as measured with their SE, or as bounds; none is a decision.

## 6. Denominators

Per hart: cycles (`hpmcounter3`) and loop iterations (body instructions = iterations x 256). Per neighbourhood
(counted once): thread-0 instructions retired (`hpmcounter4`, before and after the loop; expected retired / body =
259/256 within 0.1 %), instruction-cache requests and misses (`hpmcounter7`, `hpmcounter8`), L1 data misses
(`hpmcounter6`, expected 0 in the loop). The clock from the sampler.

**Emulator here** (the open system emulator, same kernel ELF, one minion, a 20,000-cycle window, one launch per arm,
one session, revision 1; 177 s): every arm ran 78 iterations = 19,968 body instructions; the retired counter read
21,581-21,590 (loop 78 x 259 = 20,202 plus 1,379-1,388 of kernel entry and exit); the check of x5 passed on all 32
arms; the instruction-cache counters read 0 in the emulator (not modelled) and its cycle count is not timing.

| arm | iterations | body instructions | retired (counter) | retired - loop | check |
|---|---|---|---|---|---|
| `nop` | 78 | 19968 | 21587 | 1385 | ok |
| `add.same` | 78 | 19968 | 21588 | 1386 | ok |
| `add.z` | 78 | 19968 | 21590 | 1388 | ok |
| `xor.z` | 78 | 19968 | 21581 | 1379 | ok |
| `and.z` | 78 | 19968 | 21589 | 1387 | ok |
| `add.a.f0` | 78 | 19968 | 21590 | 1388 | ok |
| `add.a.f1` | 78 | 19968 | 21590 | 1388 | ok |
| `add.a.f2` | 78 | 19968 | 21590 | 1388 | ok |
| `add.a.f3` | 78 | 19968 | 21590 | 1388 | ok |
| `add.a.f2.k4` | 78 | 19968 | 21590 | 1388 | ok |
| `add.a.f2.k8` | 78 | 19968 | 21590 | 1388 | ok |
| `add.a.f12` | 78 | 19968 | 21590 | 1388 | ok |
| `add.a.all` | 78 | 19968 | 21590 | 1388 | ok |
| `add.b.f0` | 78 | 19968 | 21590 | 1388 | ok |
| `add.b.f2` | 78 | 19968 | 21590 | 1388 | ok |
| `add.s.f0` | 78 | 19968 | 21590 | 1388 | ok |
| `add.s.f2` | 78 | 19968 | 21590 | 1388 | ok |
| `xor.a.f2` | 78 | 19968 | 21581 | 1379 | ok |
| `and.a.f1` | 78 | 19968 | 21589 | 1387 | ok |
| `and.a.f2` | 78 | 19968 | 21589 | 1387 | ok |
| `and.a.f3` | 78 | 19968 | 21589 | 1387 | ok |
| `add.cr.l0` | 78 | 19968 | 21590 | 1388 | ok |
| `add.cr.l8` | 78 | 19968 | 21590 | 1388 | ok |
| `add.cr.l16` | 78 | 19968 | 21590 | 1388 | ok |
| `add.cr.l24` | 78 | 19968 | 21590 | 1388 | ok |
| `add.cr.l31` | 78 | 19968 | 21590 | 1388 | ok |
| `add.crb.l0` | 78 | 19968 | 21590 | 1388 | ok |
| `add.crb.l8` | 78 | 19968 | 21590 | 1388 | ok |
| `add.crb.l16` | 78 | 19968 | 21590 | 1388 | ok |
| `add.crb.l24` | 78 | 19968 | 21590 | 1388 | ok |
| `add.crb.l31` | 78 | 19968 | 21590 | 1388 | ok |
| `add.ripple` | 78 | 19968 | 21590 | 1388 | ok |

## 7. Sanity checks (registered before the data)

- `check_bad` = 0 and 1,024 participants on every launch; retired / body within 0.1 % of 259/256 on every run.
- Every board sample in a window at 600 MHz; rail voltage within +-3 mV of the pass median; L1 data misses 0.
- Instruction-cache misses per iteration equal across arms (the 1 KB loop stays resident).
- Rates equal across arms within 0.5 %; a slower arm is reported. Runs whose approach was off protocol are counted.
- Additivity: `add.a.all - add.z` = the sum of the four field rungs within 2 SE; `add.a.f12` = f1 + f2 within 2 SE.
- Linearity: the quadratic terms of the f2 count ladder and of both carry ladders within 2 SE of zero.
- The zero rungs: `xor.z` and `and.z` against `add.z` (the opcode alone).
- Charge per instruction (energy / V) is what the electron counts use; the rail and board splits are both reported.

## 8. Box and card constraints; what must not be done

- Nothing opens a card node, and no sampler starts, until the card is free: `et-who --check` exits 0, no other
  user's device process runs, and a probe of the card lock succeeds (`src/run_session.sh`; exit 3 otherwise). One
  card only: on a host with several cards `ET_DEVICES` must name one and every binary run must read it (exit 2).
- One sampler for the session, nothing else on the management node; it is stopped with SIGTERM by the session's EXIT
  trap, always. Card lock per pass, the existing lock file opened read-only and taken with `flock -n`, never waited
  for; between passes it is released for 30 s, then the holder check is repeated (only this session's own sampler may
  hold a node) before it is taken again; a holder stops the session.
- Each device process under `timeout 10`, with `--stop-file`; `OUT/STOP` stops within one 0.4 s launch. The host
  starts no launch that could end after its 8.5 s budget, in every mode.
- Live stops (`src/stopwatch.py`, on the session's telemetry): board above 80 W on three distinct readings in a row
  (about 10 W over the highest heater reading in the lab's public record, so the preheat cannot trip it), die reading
  at or above 70 C, or a sampler gone quiet for 10 s; `run_block.py` also stops on a die reading at or above 70 C, and
  the smoke block checks the heater's highest board reading on this card against 70 W before any pass.
- No change of voltage, clock, firmware, governor, fan; no `et-reset`, no root, no other user's process.
- Build in a folder of our own (`~/claude/work/ee-1113-x01-intbits/`), never in the lab session's trees.
- No host compute beside the run; no simulation on the lab box.
- To be supplied by the lab session's kit, as for its own runs: the login check, the device-command audit, the
  40-minute rest rule on this card, the dry run (`DRY=1 bash src/run_session.sh OUT 9` prints every device call). The
  reference scripts make the holder check and the lock probe themselves (above).

## 9. Card time

36 runs a pass at about 8.7 s (the lab's measured run time with the E78 approach) + 20 s idle = about 5.6 minutes a
pass; 9 passes = 50 minutes, plus the smoke and the first heat (about 1.5 minutes): **about 52 card-minutes** on
aifoundry3 card 0 (cap 65), with the 40-minute rest rule before and after; wall time 1.5-3 h.

## 10. Status and open points

- STATUS `draft`: revision 1 changed `src/` (the host's arm table, `--stop-file` and one-device check; the new
  `run_block.py`, `stopwatch.py`, `run_session.sh`; the reducer). The first version's line-by-line public-safety read
  passed; revision 1 then had two reads (public safety; build and lab rules). The safety fix of the same evening
  answered them: the holder check and card-lock probe before the sampler and before every pass, a 30 s gap between
  passes, the lock opened as the lab's tools open it, one card only (node count and `ET_DEVICES` before opening), the
  host's budget in every mode, and a board stop the preheat cannot trip; the bottom-up and per-arm forecast numbers
  left this file. The kernel, the arm table and the reducer are unchanged (hashes in `log.md`). The operator sets
  STATUS.
- Builds with the open SDK here (kernel and host, `src/` card-only); the emulator has run every arm (counts above;
  the emulator-capable host is the same code with the open simulator's device layer linked in, kept on this box);
  `python3 -I -B E/scan/scan.py --names E/scan/names.txt E/labq/1113-x01-intbits/src` prints HITS 0; the forecast is
  frozen (revision 1). A dry session of 9 passes prints 327 device calls (smoke 3, 36 a pass; one more, the smoke
  block's heater check, with a heater). Fake-card sessions here: a holder at the start, or a busy card lock, and
  nothing is opened; a holder appearing between passes stops the session; a synthetic 85 W board stops it within one
  launch; two cards without a usable `ET_DEVICES` are refused; the sampler ended on SIGTERM every time.
- No arm needs a value from the design database: every value is generic (16-bit fields, a random background, carry
  runs from bit 16).
- The rate on the card for this 32-bit-encoded loop is unknown until the first run (assumed 0.622 per minion-cycle).
- Whether the per-sensor sampler is used is the lab session's call (it is a READ on this card's firmware).
