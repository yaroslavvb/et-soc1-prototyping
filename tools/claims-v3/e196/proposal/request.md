# Request 1113-x14-zeroshare: the tensor multiply-add at graded issue, with fields flipped, zeros shared

Family X14 (the tensor anchor), with an issue ladder. Version 3, Sat 14 Nov 2026. STATUS: see `STATUS`. The forecast
is frozen before any datum: `prediction.json`, its sha256 in `log.md` (the latest forecast line). Source: `src/`
(public-safe: the lab repo's sparsity kernel unchanged, a host trimmed from the lab's sparsity host with an A B B A
train mode, a tile and arm generator, a reference session and the reduction; `src/BUILD.md`).

## 1. Question

On the reference card, the lab's resident fp32 TensorFMA loop (hart 0 of all 1,024 minions; A and B in the L1
scratchpad; 16 x 16 x 16, 4,096 multiply-adds an op, 546 cycles) has a measured price: 5.816 pJ a multiply-add on
random data, 0.433 on zeros, ones 8.257 W over zeros (E78); a tile whose products all flush to zero costs what ones
cost within 0.045 W (E178). So the full-issue difference between a live lane that changes nothing and a gated lane is
already a lab number. What is not known is how the clocked part and the data part follow the issue:

1. **The issue ladders**: the same instruction, the same reads, the same op rate, with 0, 4, 8, 12 or 16 of the 16 A
   rows issuing micro-ops (the row mask: a masked row issues nothing, the sequencer still steps, E109), on a zero tile
   (every lane gated) and on a held live tile whose every element is 1.5 x 2^-64 (every lane live, every product below
   the smallest normal, so the accumulators stay +0.0 and no operand or result bit changes from one micro-op to the
   next); and on random normal values at 0, 8 and 16 rows. The slopes give energy per issued micro-op; the shape of
   each ladder (a straight line, or steps that differ at the ends) says whether energy follows the issued micro-ops
   alone.
2. **The spacing of the issued rows at equal issue**: on the held tile at 8 rows, the issued rows grouped 8, 4, 2 or
   1 at a time (masks 0x00FF, 0x0F0F, 0x3333, 0x5555: equal micro-ops, equal reads, equal rate); and on the zero tile,
   where no lane computes, two A B B A trains read the spread-against-packed difference to about 0.01 W: 4 rows
   (0x1111 against 0x000F) and 8 rows (0x5555 against 0x00FF). The lab-linear view says 0 for all of them.
3. **The data part by field**: against a held partner, B's sign or all 8 exponent bits flipping on every micro-op
   (A = 1.0), and A's exponent bits on every second micro-op (B = 1.0). B's sign is the tie to E65's bit-31 price; B's
   mantissa and A's sign and mantissa are the lab's E70 and E67 prices and are not re-run.
4. **Zeros**: what a multiply-add with one zero operand costs against a live one (r), from the random tile with half
   of A's elements zero (whole micro-ops gated), half of B's (single lanes gated), and both (the lab's sparse50
   tile); and the lab's A-zero tile with random B (every micro-op gated by A, B's random words still read) with every
   row issued (the E78 tie) and with none: the difference separates B's transport through gated micro-ops from the
   gated multiply-add itself.

Each in board watts over idle and over its reference, pJ per op and per issued multiply-add, and electrons per op
(and per flipped bit) through the core rail (at its measured volts) and through the 12 V input.

## 2. Arms (29 in every pass, 2 trains; `src/arms.json`, written and re-checked by `src/make_x14.py`)

Tiles: `lab:<kind>` is the lab repo's own E78 tile file (`tools/claims-v3/kinds/tiles/fp32`); `h.bin` holds 1.5 x 2^-64
(0x1FC00000) everywhere; `fb*` and `fa*` share base words (B: one per lane, exponent 127, seeded mantissa; A: one word);
`za50`/`zb50` are `lab:randn` with exactly 128 of A's (B's) 256 elements set to +0.0 at seeded positions. A mask means
the MSK bit and `tensor_mask` (`--row-mask`); "none" is the lab's unmasked E78 item. Every pass arm is read against its
reference in the same pass. Family T arms run only inside the trains.

| arm | tile | row mask | reference | role |
|---|---|---|---|---|
| I.Z.m0000 | lab:zeros | 0x0000 | - | zero tile, 0 rows issued: the floor every tile shares |
| I.Z.m000F | lab:zeros | 0x000F | I.Z.m0000 | zero tile, 4 rows issued |
| I.Z.m00FF | lab:zeros | 0x00FF | I.Z.m0000 | zero tile, 8 rows issued |
| I.Z.m0FFF | lab:zeros | 0x0FFF | I.Z.m0000 | zero tile, 12 rows issued |
| I.Z.full | lab:zeros | none | I.Z.m0000 | zero tile, every row (the lab's E78 zeros item) |
| I.H.m0000 | h.bin | 0x0000 | I.Z.m0000 | held live tile, 0 rows issued |
| I.H.m000F | h.bin | 0x000F | I.H.m0000 | held live tile, 4 rows issued |
| I.H.m00FF | h.bin | 0x00FF | I.H.m0000 | held live tile, 8 rows issued |
| I.H.m0FFF | h.bin | 0x0FFF | I.H.m0000 | held live tile, 12 rows issued |
| I.H.full | h.bin | none | I.H.m0000 | held live tile, every row, no MSK bit |
| I.H.mFFFF | h.bin | 0xFFFF | I.H.full | held live tile, every row, MSK bit set: equals I.H.full? |
| I.H.m5555 | h.bin | 0x5555 | I.H.m00FF | held live tile, 8 rows in groups of 1 row |
| I.H.m3333 | h.bin | 0x3333 | I.H.m00FF | held live tile, 8 rows in groups of 2 rows |
| I.H.m0F0F | h.bin | 0x0F0F | I.H.m00FF | held live tile, 8 rows in groups of 4 rows |
| I.R.m0000 | lab:randn | 0x0000 | I.Z.m0000 | random tile, 0 rows issued |
| I.R.m00FF | lab:randn | 0x00FF | I.R.m0000 | random tile, 8 rows issued |
| I.R.full | lab:randn | none | I.R.m0000 | random tile, every row (the lab's E78 randn item) |
| F.B0 | fb0.bin | none | I.Z.full | A = 1.0, B held (per-lane base words): the B fields' zero |
| F.Bs | fbs.bin | none | F.B0 | B's sign field flips every micro-op, A = 1.0 |
| F.Be | fbe.bin | none | F.B0 | B's exponent field (8 bits) flips every micro-op, A = 1.0 |
| F.A0 | fa0.bin | none | I.Z.full | B = 1.0, A held (one base word): the A fields' zero |
| F.Ae | fae.bin | none | F.A0 | A's exponent field (8 bits) flips every second micro-op, B = 1.0 |
| Z.a50 | za50.bin | none | I.R.full | the random tile with half of A's elements +0.0 |
| Z.b50 | zb50.bin | none | I.R.full | the random tile with half of B's elements +0.0 |
| Z.ab50 | lab:sparse50 | none | I.R.full | the lab's sparse50 tile: half of each side +0.0 |
| Z.a0 | lab:a_zeros_b_randn | none | I.Z.full | the lab's tile with A all +0.0 and B random, every row |
| Z.a0.m0000 | lab:a_zeros_b_randn | 0x0000 | I.Z.m0000 | the same tile with nothing issued |
| K.ones | lab:ones | none | I.Z.full | the lab's ones tile (E78) |
| K.pi | built-in pi | none | - | the host's built-in pi: the block anchor, first and last |
| T.Z.m1111 | lab:zeros | 0x1111 | I.Z.m000F | zero tile, 4 rows in groups of 1 row (train only) |
| T.Z.m5555 | lab:zeros | 0x5555 | I.Z.m00FF | zero tile, 8 rows in groups of 1 row (train only) |

Designed counts per op (one minion; the generator re-derives them from the files with `--check`; operand flips
counted between consecutive issued micro-ops in issue order, 8 lanes; live-lane flips between consecutive live
lane-micro-ops of each lane, which is what a lane's operand registers see if a gated micro-op loads nothing; the
accumulator flips are an IEEE fp32 emulation of the accumulation at mid-launch, an estimate; "C rows zero / non-zero"
are the rows the read-backs check). The emulator columns: the open system emulator here, one minion of shire 0,
`--iters 4`, the same kernel ELF and tiles and this `src/` host (with the emulator's device layer added at the desk),
counted from the emulator's instruction log by the lab's `tools/counter/count_kernel.py`.

| arm | rows | micro-ops issued | MACs issued | operand flips A / B | gated lane-micro-ops (fraction) | live-lane flips A / B | accumulator flips, input / result (est., mid-launch) | skipped runs / op | C rows zero / non-zero | emulator: instr. (4 ops), tensor instr., ok, read-backs |
|---|---|---|---|---|---|---|---|---|---|---|
| I.Z.m0000 | 0 | 0 | 0 | 0 / 0 | 0 (0.000) | 0 / 0 | 0 / 0 | 16 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| I.Z.m000F | 4 | 128 | 1024 | 0 / 0 | 1024 (1.000) | 0 / 0 | 0 / 0 | 16 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| I.Z.m00FF | 8 | 256 | 2048 | 0 / 0 | 2048 (1.000) | 0 / 0 | 0 / 0 | 16 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| I.Z.m0FFF | 12 | 384 | 3072 | 0 / 0 | 3072 (1.000) | 0 / 0 | 0 / 0 | 16 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| I.Z.full | 16 | 512 | 4096 | 0 / 0 | 4096 (1.000) | 0 / 0 | 0 / 0 | 0 | 0xFFFF / - | 245, 9, yes, zero 0, live -1: ok |
| I.H.m0000 | 0 | 0 | 0 | 0 / 0 | 0 (0.000) | 0 / 0 | 0 / 0 | 16 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| I.H.m000F | 4 | 128 | 1024 | 0 / 0 | 0 (0.000) | 0 / 0 | 0 / 0 | 16 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| I.H.m00FF | 8 | 256 | 2048 | 0 / 0 | 0 (0.000) | 0 / 0 | 0 / 0 | 16 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| I.H.m0FFF | 12 | 384 | 3072 | 0 / 0 | 0 (0.000) | 0 / 0 | 0 / 0 | 16 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| I.H.full | 16 | 512 | 4096 | 0 / 0 | 0 (0.000) | 0 / 0 | 0 / 0 | 0 | 0xFFFF / - | 245, 9, yes, zero 0, live -1: ok |
| I.H.mFFFF | 16 | 512 | 4096 | 0 / 0 | 0 (0.000) | 0 / 0 | 0 / 0 | 0 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| I.H.m5555 | 8 | 256 | 2048 | 0 / 0 | 0 (0.000) | 0 / 0 | 0 / 0 | 128 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| I.H.m3333 | 8 | 256 | 2048 | 0 / 0 | 0 (0.000) | 0 / 0 | 0 / 0 | 64 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| I.H.m0F0F | 8 | 256 | 2048 | 0 / 0 | 0 (0.000) | 0 / 0 | 0 / 0 | 32 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| I.R.m0000 | 0 | 0 | 0 | 0 / 0 | 0 (0.000) | 0 / 0 | 0 / 0 | 16 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| I.R.m00FF | 8 | 256 | 2048 | 14240 / 27046 | 0 (0.000) | 14240 / 27046 | 27171 / 27170 | 16 | 0xFF00 / 0x00FF | 247, 10, yes, zero 0, live 0: ok |
| I.R.full | 16 | 512 | 4096 | 28192 / 54022 | 0 (0.000) | 28192 / 54022 | 55293 / 55301 | 0 | - / 0xFFFF | 245, 9, yes, zero -1, live 0: ok |
| F.B0 | 16 | 512 | 4096 | 0 / 0 | 0 (0.000) | 0 / 0 | 303 / 299 | 0 | - / 0xFFFF | 245, 9, yes, zero -1, live 0: ok |
| F.Bs | 16 | 512 | 4096 | 0 / 4096 | 0 (0.000) | 0 / 4096 | 4399 / 4395 | 0 | - / 0xFFFF | 245, 9, yes, zero -1, live 0: ok |
| F.Be | 16 | 512 | 4096 | 0 / 32768 | 0 (0.000) | 0 / 32768 | 8495 / 8491 | 0 | - / 0xFFFF | 245, 9, yes, zero -1, live 0: ok |
| F.A0 | 16 | 512 | 4096 | 0 / 0 | 0 (0.000) | 0 / 0 | 256 / 256 | 0 | - / 0xFFFF | 245, 9, yes, zero -1, live 0: ok |
| F.Ae | 16 | 512 | 4096 | 16384 / 0 | 0 (0.000) | 16384 / 0 | 4352 / 4352 | 0 | - / 0xFFFF | 245, 9, yes, zero -1, live 0: ok |
| Z.a50 | 16 | 512 | 4096 | 24368 / 54022 | 2048 (0.500) | 14784 / 26976 | 55821 / 55811 | 0 | - / 0xFFFF | 245, 9, yes, zero -1, live 0: ok |
| Z.b50 | 16 | 512 | 4096 | 28192 / 48988 | 2048 (0.500) | 20956 / 14790 | 55679 / 55673 | 0 | - / 0xFFFF | 245, 9, yes, zero -1, live 0: ok |
| Z.ab50 | 16 | 512 | 4096 | 25968 / 48582 | 3171 (0.774) | 9502 / 6486 | 57308 / 57247 | 0 | - / 0xFFFF | 245, 9, yes, zero -1, live 0: ok |
| Z.a0 | 16 | 512 | 4096 | 0 / 55798 | 4096 (1.000) | 0 / 0 | 0 / 0 | 0 | 0xFFFF / - | 245, 9, yes, zero 0, live -1: ok |
| Z.a0.m0000 | 0 | 0 | 0 | 0 / 0 | 0 (0.000) | 0 / 0 | 0 / 0 | 16 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| K.ones | 16 | 512 | 4096 | 0 / 0 | 0 (0.000) | 0 / 0 | 248 / 256 | 0 | - / 0xFFFF | 245, 9, yes, zero -1, live 0: ok |
| K.pi | 16 | 512 | 4096 | 0 / 0 | 0 (0.000) | 0 / 0 | 248 / 248 | 0 | - / 0xFFFF | 245, 9, yes, zero -1, live 0: ok |
| T.Z.m1111 | 4 | 128 | 1024 | 0 / 0 | 1024 (1.000) | 0 / 0 | 0 / 0 | 64 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |
| T.Z.m5555 | 8 | 256 | 2048 | 0 / 0 | 2048 (1.000) | 0 / 0 | 0 / 0 | 128 | 0xFFFF / - | 247, 10, yes, zero 0, live -1: ok |

Per op the loop retires 5 instructions (one TensorFMA control write, 3 scalar integer, 1 taken branch), the same for a
masked and an unmasked arm; a row mask adds 2 instructions a launch (the tensor_mask write and its operand). The
emulator's cycle counts are not timing (it ran 11 cycles an op); the card's 546 (544 with a row masked) are the lab's
(E78, E109); with every row enabled and the MSK bit set the lab's September record on this card reads 546.

Trains (E182's method: one process alternates two kinds launch by launch; the calibration launch and launch 0 take the
order's first letter, launch n >= 1 takes letter (n - 1) mod 4 of SFFS or FSSF; 13 launches of about 0.5 s after the
calibration launch; 24 processes back to back, the order alternating):

| train | F kind (--values) | S kind (--values-b) | processes | launches | what differs |
|---|---|---|---|---|---|
| T1 | T.Z.m1111 (0x1111) | I.Z.m000F (0x000F) | 24 | 13 | zero tile, 4 rows: spread evenly against packed; 64 against 16 skipped runs an op |
| T2 | T.Z.m5555 (0x5555) | I.Z.m00FF (0x00FF) | 24 | 13 | zero tile, 8 rows: spread evenly against packed; 128 against 16 skipped runs an op |

In the emulator, a 3-launch process of each train in each order, and a desk test that alternates the random tile at
8 rows with the zero tile at 8 rows (so a launch that ran the wrong kind would fail its read-back):

| train process | launches (kinds, in order) | U-mode instructions | read-backs of C (after launch: kind ok) |
|---|---|---|---|
| T1-SFFS-l3 | -1:S 0:S 1:S 2:F | 973 | -1: S ok, 2: F ok |
| T1-FSSF-l3 | -1:F 0:F 1:F 2:S | 973 | -1: F ok, 2: S ok |
| T2-SFFS-l3 | -1:S 0:S 1:S 2:F | 973 | -1: S ok, 2: F ok |
| T2-FSSF-l3 | -1:F 0:F 1:F 2:S | 973 | -1: F ok, 2: S ok |
| X-SFFS-l3 | -1:S 0:S 1:S 2:F | 973 | -1: S ok, 2: F ok |
| X-FSSF-l3 | -1:F 0:F 1:F 2:S | 973 | -1: F ok, 2: S ok |

## 3. Protocol

- **Card and clock**: the reference card (aifoundry3 card 0), pinned at 600 MHz, core rail about 522 mV. User level,
  reads only; nothing set.
- **Harness**: the passes run the lab's unchanged sparsity host through the lab's E78 frame as well as through the
  reference here (every pass arm is `--test fma --type fp32 --pattern none --values file:<tile>` with an optional
  `--row-mask`); the trains need the host's train mode with a second row mask (`x14_host`, `src/host`; E182's train
  host alternates tiles only). The reference: one device process per run under `timeout 10`, `--stop-file`; the card
  lock per block, released between blocks; one sampler (10 Hz) for the session; `et-who --check` before the sampler
  and before every block.
- **The session, in order**: the configuration read (`ettelem config`, read only, under the card lock, timeout 10);
  the sampler, started as the lab's `lib.sh` does (it must write its first line within 10 s, else it is stopped with
  SIGTERM and started again, up to six times; its own time bound is the session's deadline plus 5 minutes); the smoke
  block; train T1; train T2; the passes; the sampler stopped (SIGTERM); the closing configuration read, only when the
  card is free: after a session that ended because another holder was seen (exit 3), or on a signal, it is not made
  and `config-end.json` says why; otherwise the holder check must pass again first (`et-who --check` exit 0 with our
  sampler stopped, no other user's device process, the card lock free on a probe). 30 s with the lock released before
  every block after the smoke, then the holder check and a check that the live stops are running. A block starts only
  if it can end before the session's deadline (60 card-minutes from the start unless the window is shorter), using the
  first pass's measured length; a window too short for the smoke opens nothing.
- **The smoke and its gate**: the heater check (one heater launch: it must exit 0 with every launch record ok and no
  tensor error, else the gate fails at once and nothing more runs; its highest board reading at most 70 W);
  I.H.m00FF, I.R.m00FF (a masked random arm: its read-back is the riskiest premise), Z.a0 and I.R.full, 2 s each; the
  first two processes of train T1. The gate: every smoke arm and both processes have launch records; every launch is ok
  with no tensor error; every read-back of C is ok; cycles per op within 0.5 % of 546 (unmasked) or 544 (a row
  masked); the train records follow their order. A failed gate runs no train and no pass.
- **A pass**: 10 s idle; two unrecorded burn-in runs of K.pi; K.pi; the 28 other pass arms shuffled by
  "hostname|pass"; K.pi; 10 s idle. Before every run the lab's approach: heater launches (`x14_host --values randn
  --label heater --seconds 2`: this request's own host, the session's default heater; the lab's sparsity host takes
  other arguments) to a 59 C reading, idle to 58 C, at least 2 s with no device process (E60, E78). A run is on protocol
  only when that approach was kept (the approach gate sets the others aside); two failed heater launches in a row end
  the block. Each run: 4 s of launches of about 0.5 s.
- **A train block**: 10 s idle; K.pi (with the approach); the train's 24 processes back to back (the opening anchor's
  approach sets the launch band, as in E182), each a calibration launch and 13 launches; K.pi; 10 s idle.
- **Passes**: 6, every one counted (a 7th if the window allows); results from fewer than 5 kept passes are reported
  as provisional.
- **Measured**: board watts over seconds 1-3 of each run; the run's own idle bracket [-1.2, -0.2) s; the die reading;
  the core rail over the same window, its 1 s first-order lag undone; the rail's volts; the clock in every sample. A
  train launch: the mean board watts from its start + 170 ms to its end (E182).
- **Denominators**: tensor ops completed inside the window from the device (each launch's op count, prorated by
  overlap), never the wall clock; cycles per op from the cycle counter; issued micro-ops, issued multiply-adds and
  designed flips per op from the arm table. **C is read back after the first (calibration) launch and after the last
  launch of every process only**, never between measured launches, so every measured launch is the same for every arm:
  the rows that must read zero (+0.0 or -0.0: a zero A times a negative B leaves -0.0) and the rows that must hold a
  non-zero word (issued rows of live tiles: issue is shown to have happened).
- **Gates** (registered in `src/reduce_x14.py`, the E78 frame's): at least 15 kept board samples in the window and 8 in
  the bracket; no gap over 0.5 s between kept window samples; launches covering at least 0.97 of the window; every
  window sample at the pass's clock; rail volts within 3 mV of the pass median; cycles per op within 0.5 %; no tensor
  error and every launch ok; both read-backs ok; the approach on protocol. The dip rule is E82's amendment A2: board
  sample i is dropped when it is more than 4 W under both samples i-2 and i+2; nothing is set aside for a dip. A pass
  is kept when both K.pi runs pass and differ by at most 0.3 W; when only one passes, the pass is kept with its drift
  unmeasured (flagged); otherwise it is set aside. Leak slope 0.1994 W/C (E78's fit), every result also at 0 and
  0.3803 W/C.
- **Stops**: `stopwatch.py` (board above 80 W on three distinct readings, die at or above 70 C, a quiet sampler);
  `run_block.py` (die at or above 70 C, telemetry older than 5 s, before every device process and between train
  processes); the host's budget (no launch that cannot end inside 8 s of holding the device). Highest board reading
  expected: the random arm, about 50 W (the lab's E78 level).

## 4. What is derived (all registered; `src/reduce_x14.py`; unit of replication: the pass, the train's unit)

Per arm: S (W over idle) and D over its reference in two forms: the difference of the leak-corrected busy means (the
primary form, the lab's E60 form) and of the bracketed S; per op and per issued multiply-add (pJ, board and rail),
with the per-op difference S/rate - S_ref/rate_ref beside every D (the form to compare where rates differ); electrons
per op through the core rail and the 12 V input. Then: the ladders' S and their steps (zero and held tile, 0 to 16
rows; random 0, 8, 16); the slopes per issued micro-op over the three structurally equal rungs (4, 8, 12 rows) and in
W per row; the held line's intercept against the mask-0 arm and the full arm's distance from it (pJ an op); the
middle-step ratio of the held ladder and the first-step ratio of the zero ladder; the held tile over the zero tile per
multiply-add at full issue (board and rail); random over held per multiply-add; the spread contrasts at 8 rows;
the MSK bit alone per op; held, random and A-zero over zeros with nothing issued; B through gated micro-ops ((Z.a0 -
I.Z.full) - (Z.a0.m0000 - I.Z.m0000)); per field, fJ per designed operand flip and per all designed flips (operand +
accumulator estimates), and electrons per operand flip on the rail; zero shares (S(Z) - S(zeros)) / (S(random) -
S(zeros)) and r = (share - (1 - g)) / g, g the arm's gated lane-micro-op fraction; the ties (E78's zeros S, randn D,
ones D, sparse50 D, a_zeros_b_randn D, random per multiply-add, pi; E65's B sign). Trains: E182's statistic (a quad
sigma (L2 + L3 - L1 - L4) / 2 over launches 4q+1 to 4q+4, a process the mean of its quads, a unit the mean of one
SFFS and one FSSF process, the estimate and its 95 % interval over units; at least 8 units or not scored), in W and pJ
per op; the trains' anchors' drift.

## 5. Signal budget (the lab's prices; board W; the reference card's noise)

The noise, from the lab's own records on this card: E60's ladders left 0.032 W rms about the line with eight passes;
per-pass sd 0.05-0.10 W for sub-watt to 2 W arms and 0.06-0.18 W for 3-10 W arms (E60, E65, E67, E70, E109), so with
6 passes a per-arm SE of 0.02-0.04 W at the zero tile's level and 0.025-0.075 W at the held tile's; a train of 24
processes reads its pair to about +-0.010 W (95 %) at E182's quad sd (0.038 W), +-0.018 W at E183's (0.069 W).
###### [LAB REDACTION R1, written Sun 15 Nov 2026 23:04 PST (Q191, lane fix-e196), before any E196 datum: in lines 233-249 (the table below) and line 251 every number (each digit run with its decimals and a sign written against it; names such as T1, E78 and sparse50, and the mask 0xFFFF, kept) is replaced by [withheld] until the model session's private scoring of E196. Why: the table's column "expected (top-down)" gives an expected value for each ladder step, spread contrast, null, field, zero share and train, and line 251 restates one; they may be the sealed forecast's own numbers, and the lab publishes no forecast number before the data (the registration's verifier found them, Q191; the model session may say in the owner's private coordination thread, topic #6, that they are not its forecast's). Lines 1-231, 250 and 252-331 are the received file's, byte for byte; this line, 232, was blank; lines 233-249 and 251 keep every word and mark. The received file (version 3, 30,305 B) has sha256 88ddd2b4078fd98d5f4adb9a15cc38b34feac1ac4c84ce058c2a5c7bd651cbe0; E196.md section 0 registers it and the withheld lines' own sha256; the full file is added after the private scoring, as a new file, never an edit of this one.]
| step or contrast | expected (top-down) | from |
|---|---|---|
| zero tile, each [withheld] rows ([withheld] to [withheld]), then [withheld] to [withheld] | [withheld] each, [withheld] | E109 ([withheld] W with nothing issued; [withheld] W of gated micro-ops), E78 zeros |
| held tile, each [withheld] rows | [withheld] | E78 ones, E178 held kind, E109 floor |
| random tile, [withheld] to [withheld] to [withheld] rows | [withheld], [withheld] | E78 randn, E109 |
| held tile at [withheld] rows, groups of [withheld] / [withheld] / [withheld] rows over packed | [withheld] / [withheld] / [withheld] (no spacing term); a transition at most one lane-gate flip: up to [withheld] / [withheld] / [withheld] | E127 gate-flip price |
| train T1 (zero tile, [withheld] rows spread over packed) | [withheld]; a transition at most one lane-gate flip: up to [withheld] | E127 |
| train T2 (zero tile, [withheld] rows spread over packed) | [withheld]; up to [withheld] | E127 |
| MSK bit alone (0xFFFF over no mask, equal rate) | [withheld] | a null |
| held over zeros, nothing issued | [withheld] | a null |
| random over zeros, nothing issued | [withheld] | E109: [withheld] W for B's bytes, twice |
| A zero with random B over zeros, nothing issued | [withheld] | E109 |
| B sign over held (the tie) | [withheld] | E65 bit [withheld]: [withheld] +- [withheld] |
| B exponent ([withheld] bits) over held | [withheld] | E65 bits [withheld]-[withheld], E70's law |
| A exponent ([withheld] bits) over held | [withheld] | E67 bit [withheld] and more bits |
| half of A / of B zero, over random | [withheld] / [withheld] | E78 sparse50 and randn |
| A zero with random B over zeros, every row (the tie) | [withheld] | E78 a_zeros_b_randn: [withheld] +- [withheld] |

The ladders' steps of [withheld] W and more, the fields and the zero shares are well above ten times the floor. The spread
contrasts and the nulls are what is new and small: on the held tile at 8 rows the spread rungs are read with the 4 s
protocol (groups of 1 resolve against 0 at its noise; groups of 4 are a bound unless they are larger than the
lab-linear view allows); on the zero tile the two trains read them to +-0.010 W. The MSK bit alone and the held tile
over zeros with nothing issued are nulls, bounded to about +-0.05-0.15 W.

Rates: 1.121e9 ops a second unmasked and with every row enabled (546 cycles, E78), 1.125e9 with a row masked (544);
4,096 multiply-adds an op at full issue, 256 per issued row.

## 6. Sanity checks

- I.Z.full, I.R.full, K.ones, Z.ab50 and Z.a0 reproduce E78's zeros S (1.99 W), randn D (24.7 W), ones D (8.26 W),
  sparse50 D (7.30 W) and a_zeros_b_randn D (0.81 W) within their pass-to-pass scatter; K.pi reproduces E78's pi;
  F.Bs over F.B0 reproduces E65's bit-31 price (0.563 W) within the transfer to the new base words; I.Z.m0000
  reproduces E109's 0.38 W with nothing issued.
- I.H.mFFFF equals I.H.full within the noise at equal rate (546 cycles both), or the difference is reported.
- The held ladder's middle steps (4 to 8, 8 to 12 rows) are equal within the noise, or the curvature is reported
  (the lab's E60 rule: ladders that bend are reported as bent).
- Every read-back of C is ok (masked rows and products that flush stay zero; issued live rows are not all zero).
- Cycles per op: 546.0 unmasked and with every row enabled, 544.0 with a row masked, the same for every tile.
- Each train's anchors agree within 0.3 W; each train's carry-over (L2 - L3 in SFFS quads against FSSF) is reported.

## 7. Constraints, and what must not be done

User-level only: no clock, voltage, firmware, governor or fan change; no root; no reset. One card: the host refuses on
a host with several card nodes unless the selection variable names one and its device layer reads it. Never more than
10 s holding a device; the lock per block, released between blocks; never beside another session of ours on the same
host; never rebuild a build directory another kit uses (build into a folder of your own). Host CPU quiet during the
session (no builds or simulations beside it).

## 8. Card time

A pass: 32 runs (2 burn-in, K.pi twice, 28 arms) at 9.8-11.4 s a run with the approach (the pace of E70, E109 and
E178 on this card), about 5.9 card-minutes. A train block: 24 processes of about 7.9 s (E182's pace) and two anchor
runs, about 3.9 card-minutes. The smoke about 1, the 30 s gaps 4, the sampler and the configuration reads 0.5.
**About 49 card-minutes in all (46-53)** with 6 passes; a 7th pass adds about 6. The session's deadline stops it
cleanly: a block starts only if it fits. Cut order if the window is short: 5 passes (about 43, the minimum for a
reported result); then drop F.Ae, Z.b50 and I.H.mFFFF from the passes (about 40: `DROP_ARMS=F.Ae,Z.b50,I.H.mFFFF`;
the reference session leaves them out of every pass and records them in each pass's plan mark, and the reduction
reports them, and the six derived quantities that need them, as empty); the trains stay (they carry the new
question).

## 9. Evidence here (no card)

- **Build**: `cmake -S src -B build -DCMAKE_PREFIX_PATH=/opt/et` with the open SDK installed here builds `x14_host`
  (`-Wall -Wextra`, no warning) and `kernel/sparsity.elf`, sha256
  `abbdbe40976f7413e9c246e0992dcf52a56885ab69e1746351f9903cb8f7de46`: byte-identical to the ELF that the lab repo's
  unchanged `workloads/sparsity` (commit 49a4152e) builds with the same SDK here. On the lab box, build again with
  its own `/opt/et` (older) in a folder of your own; the ELF hash may differ there and is to be recorded with the run.
- **Tiles**: `make_x14.py --check` re-derives every tile and count: no problem; the five lab tiles' sha256 equal the
  lab's `kinds.json`; the session regenerates `gen/` on the box and refuses to start if `gen/arms.json` differs from
  `src/arms.json`.
- **Emulator**: every arm and both trains ran (section 2's tables): every launch ok, no tensor error, every read-back
  of C ok, every train process's kinds in its order. Rebuilt after the second read's fixes (the host's source is
  unchanged), every one of these runs gave the same instruction counts, launch records and read-backs again; the
  heater's own arguments (random values, label heater) ran too: every launch ok, no tensor error.
- **Reduction**: `reduce_x14.py` on a synthetic session in the session's layout (five passes of every pass arm at
  known watts, board noise 0.04 W, the rail's 1.05 s lag; both trains, 24 processes each, at known differences, with a
  drift inside each process; injected faults) returns every arm's S within 4 standard errors (or 0.02 W) of what was
  put in; sets aside the run with a launch not ok and the run with a failed read-back; keeps the pass whose first
  anchor was set aside, with its drift unmeasured; drops exactly the injected dips (40 samples) and nothing else;
  excludes the train process with a launch off its order; and reads the trains' differences inside their 95 %
  intervals (+0.300 W read as +0.3005 [+0.2921, +0.3089]; -0.150 W as -0.1475 [-0.1542, -0.1408]; four other seeds
  alike). With the cut order applied (F.Ae, Z.b50 and I.H.mFFFF absent from every pass) it finishes with every other
  arm inside its noise, the three cut arms and the six derived quantities that need them empty, both trains scored.
- **Dry session**: `DRY=1 run_session.sh OUT 6` prints 251 device calls (the smoke: the heater check, 4 arms and 2
  train processes; the two trains: 2 x 26; 6 passes: 6 x 32), each under `timeout 10`, the approach with the heater
  before each of the 196 measured runs, and opens nothing; with `DROP_ARMS=F.Ae,Z.b50,I.H.mFFFF`, 233 (6 x 29 in the
  passes).
- **The session's paths without a card**: the reference session run in its real mode against stand-ins for the
  holder check, the sampler and the host (16 scenarios, here only). After a normal end the closing configuration read
  is made only once the holder check has passed with the sampler stopped; after another holder was seen with the
  sampler running or between blocks (exit 3), with a holder present at the end, or on a signal, it is not made and
  `config-end.json` says why. A heater that rejects the heater arguments (as the lab's sparsity host rejects
  `--label`) fails the smoke gate at the heater check (exit 10) and nothing more runs; a relative heater path is made
  absolute, a missing heater is refused before anything opens, an unset one is the host; a heater that fails twice in
  a row ends the block (exit 11); with `PREHEAT=0` no measured run is on protocol. With `DROP_ARMS` the pass runs the
  other 25 arms and K.pi and its plan mark names the three; an unknown name or the anchor is refused before anything
  opens. A session whose live stops are not running runs no block (exit 5); a window shorter than the smoke opens
  nothing.
- **Names**: `python3 -I -B scan.py --names names.txt src` (the study's scanner): HITS 0.
