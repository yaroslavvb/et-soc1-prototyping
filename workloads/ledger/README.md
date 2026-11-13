# workloads/ledger: the blind day's plain programs

Step 3 of the November checkpoint's plan (Q166, Thu 12 Nov 2026). This folder holds three plain programs: a copy through
DRAM, SHA-256 of one message per hart, and a merge sort. It also names a sparse-parity instance that no committed run
used. Each program was built with the ET toolchain, run in the simulator, checked there, and counted by `tools/counter/`.
Each carries a first ledger estimate of its joules on aifoundry3 at 600 MHz.

**Nothing here is frozen or registered.** The estimates are first ones, for the blind day's design. The blind day (the
plan's step 4) freezes its own forecasts in the lab repo before any card is claimed. **No card ran.** Nothing in this
folder has opened a device: the host refuses to run without `--sysemu`, `--card`, `--dry` or `--selftest`. Only
`--sysemu`, `--dry` and `--selftest` were ever given (the last two return before any device opens); `--card` never was.

*Dated note (Thu 12 Nov 2026, Q166's fix lane, on its verifier's findings): text corrections throughout, marked where they
change a claim; two host changes, the sort's work area pre-filled and an `--expect` mismatch named in `first_mismatch`,
checked in the simulator; comment and licence lines in four sources, after which the kernel ELF rebuilt byte for byte
(`78708041…`). No estimate changed.*

## Results first

Every claim carries one of these labels:
- **sim**: the simulator ran it and the program checked its own output.
- **counted**: the simulator's instruction log, exact for the participants it logged.
- **scaled**: arithmetic from counted units to the card's configuration.
- **estimate**: the ledger's arithmetic on the energy manual's prices and the ledger v2 (Q166's step 1). These are not
  frozen, not blind and not held out.
- **desk check**: code checked against another implementation on the desk.

In the records' (05-claims) words: **sim**, **counted** and **desk check** are desk checks of code (in the simulator, or
against its own log); **scaled** and **estimate** are desk arithmetic, an estimate: not registered, not blind, not held out.

| program (card configuration) | checks in the simulator | counted per unit of work | seconds at 600 MHz (estimate) | J over idle (estimate) | J with the card at rest (estimate) |
|---|---|---|---|---|---|
| copy, 1 GiB, 14 passes, **zeros** | the destination equals the source: 64 of 64 participants, and 2,048 of 2,048 with 64 MiB in all (sim) | 19 instructions a 256 B (8 `flw.ps`, 8 `fsw.ps`, 3 loop); 1.00 B read and 1.00 B written a byte copied | 0.66 [0.56, 0.75] | 5.1 [4.3, 6.1] | 21.7 [17.5, 27.2] |
| copy, 1 GiB, 14 passes, **random bytes** | the same: PASS (sim) | the same | 0.66 [0.56, 0.75] | 6.8 [6.4, 7.8] | 23.4 [19.6, 29.1] |
| SHA-256, 2,048 messages of 800 x 2 KiB | every digest equals Python `hashlib`'s computed on the desk: 64 of 64 in three runs (two block sizes), and 2,048 of 2,048 at the card's participant count (sim) | 4,577 instructions a 64 B block (one compression), 69 taken branches; 928 B read, 384 B written | 0.57 [0.57, 0.93] | 2.3 [2.1, 5.2] | 16.6 [15.6, 31.0] |
| merge sort of 512 keys per hart, 1,500 sorts, **sorted** input | sorted, the same multiset: 64 of 64 (sim) | 55,058 instructions a sort; 6,261 taken, 6,257 not-taken branches | 0.62 [0.62, 0.77] | 2.3 [1.7, 4.0] | 17.7 [16.3, 25.4] |
| the same, **shuffled** input (same keys) | 64 of 64, and 2,048 of 2,048 (sim) | 71,397 instructions a sort; 6,648 taken, 9,733 not taken | 0.75 [0.75, 0.95] | 2.7 [2.2, 4.9] | 21.5 [19.9, 31.2] |
| sparse parity (544, 4, 0.39, m = 1,792, seed 3): never ran | three 1/20000 slices: the host's records, count and best-rescore checks, and its oracle exact on the minion: PASS (sim). A whole small instance with the same k, eta and m, (64, 4, 0.39, 1792): solved, the answer the planted secret and unique (sim) | 416.8 M int8 ops a solve (the plan). Counted work: 111 instructions an op, 46.4 G a solve (hart 0 26.5 G, hart 1 19.9 G), spin loops left out (counted, scaled) | 0.515 (the fitted cycle model; 0.67 with its x1.3 margin) | 7.4 [6.1, 11.3] | 20.5 [18.8, 25.3] |

The table's figures:
- The seconds are one launch's, at 600 MHz, from the catalogue's issue rates. Sparse parity's come from the host's fitted
  cycle model.
- The bands are boxes: the sum of every term's own band.
- The card at rest is aifoundry3's footing law at a 55 C starting die (band 52-60 C), plus the run's own leakage rise.
- `estimates.json` in the data folder has every term.

What the counts say about the programs:
- **The copy is the DRAM write path.** 72% of its joules over idle are the stores' write-back path, 325.8 pJ a byte on
  random data (energy manual 4.1). That is 2.5 times the tensor store's DRAM price.
- So this plain copy should cost 0.49 J over idle a GiB copied on random bytes and 0.37 J on zeros (estimate). The
  tensor paths' prices (04 §4.1: 132.6 + 141.9 pJ/B random, 94.6 + 94.4 on zeros) would put it at 0.29 and 0.20 J. The
  blind day decides which path a plain copy pays.
- **SHA-256 is 92% one-cycle integer instructions.** Its 69 taken branches a block are 1.5% of its instructions and about
  9% of its hart-cycles (a taken branch issues at 0.058 a hart-cycle).
- **The sort's sorted and shuffled inputs differ by 30% in instructions** (the merge's inner loop ends early on sorted
  input), and by 22% in hart-cycles. The data-dependent branch is priced by outcome: a taken branch costs 23.9 pJ and a
  not-taken one 6.5 pJ. The catalogue's `*_data` rows (13.6-16.0 pJ on random operands) sit where a 50/50 mix of the
  two lands (desk check of the rule).

## The programs

`kernel/ledger.c`:
- One device kernel: user mode, no libc, no threads.
- No floating-point arithmetic, so none of the thirteen instructions that trap in U-mode (03a) appears. The
  disassembly has no `fdiv`, `fsqrt` or float conversion at all.
- Every participating hart works on its own data and touches whole cache lines only. The minions' L1 data caches are not
  coherent and write back whole lines (`workloads/sgemm`).
- Only hart 0 of a minion reads `hpmcounter3` (erratum 1.23, as `workloads/sparseparity`), with `workloads/memprobe`'s
  late-carry fix.

`host/main.cpp` is `workloads/enercat`'s session pattern (ops node only, so `ettelem` can sample the card meanwhile), with
the inputs, the checks and one JSON line.

1. **Copy** (`--prog copy`):
   - `--bytes` (default 1 GiB) is split evenly over the participants. Every part is a multiple of 256 B.
   - It is copied `--passes` times from a source to a destination buffer: eight 32 B vector loads, then eight 32 B vector
     stores, per 256 B (`--width 32`; `--width 8` uses `ld`/`sd`).
   - `--data zeros|random`: the source is all zero, or splitmix64 bytes.
   - The destination is first filled with 0x5A, so a missed store shows. The host reads the whole destination back and
     compares it with the source.
2. **SHA-256** (`--prog sha256`):
   - One message is a serial chain of compressions, so each hart hashes its own.
   - Participant p's message is its own `--block`-byte block (random, splitmix64), repeated `--repeat` times, then the
     standard padding.
   - The blocks should stay in the shire's caches: 128 KiB a shire, against a 512 KB L2. The work is the compression
     function and almost nothing else: no multiply in it, no float, no data-dependent branch.
   - The host checks every digest against its own SHA-256 (FIPS 180-2's four test vectors pass with `--selftest`), or a
     sample when the messages exceed 1 GiB in all. With `--expect FILE` it also checks every digest against digests
     computed on the desk by `ledger_desk.py digests` (Python's `hashlib`).
3. **Sort** (`--prog sort`):
   - A bottom-up merge sort of `--keys` (a power of two) 32-bit keys per participant, `--reps` times.
   - Each time, the input is copied into the work area and sorted there, ping-pong between two buffers.
   - `--order sorted|shuffled` gives the same multiset of keys, ascending or in a Fisher-Yates order.
   - The merge's comparison is a branch whose outcome follows the data (`bgeu` in `merge_sort`). On sorted input it always
     goes one way and the merge ends early.
   - The host checks every participant's result against `std::sort` of its input. The kernel counts out-of-order
     neighbours too.
4. **Sparse parity**:
   - The never-run instance is `workloads/sparseparity`'s own kernel and host. The kernel is the 29 Sep card file, `.text`
     `3e14be32...`.
   - It runs in variant b on all 1,024 minions, as `energy.sh`'s presets do:
     `--mode tensor --shires 0xffffffff --per-shire 32 --n 544 --k 4 --eta 0.39 --m 1792 --seed 3 --variant m1 --cost fit --gen inc`.
   - `spp_never_ran.py` reads every file under `workloads/sparseparity/` and `docs/`. Its result is in the data folder's
     `spp-never-ran.txt`. It ran with that folder left out (`--exclude`), since once landed the folder names the
     instance itself:
     - no committed file names n = 544, with any k;
     - none names eta = 0.39 or m = 1,792;
     - the (n, k) pairs named run from (10, 5) to (1024, 5): n = 10-64, 128, 256, 512 and 1024;
     - the eta values named are 0, 0.1, 0.2, 0.3 and 0.4.
   - m(1 - 2 eta)^2 = 86.7: L1 has 72 and L2 74, so the planted secret should stand out. Its expected score is
     m(1 - 2 eta) = 394, 9.3 standard deviations (sqrt(m) = 42). The best of the 3.6 x 10^9 null candidates sits near
     sqrt(2 ln C(544, 4)) = 6.6 (desk arithmetic; L1 and L2 have 8.5 and 8.6). The host allows m up to 2,560;
     this lane's first choice, (448, 4, 0.42, 3584), was outside that range and was refused before any run.
   - A launch is 0.515 s by the host's fitted cycle model (`--dry` model_s; est_s 0.669 with its x1.3 margin), against
     L2's 0.427 s by the same model. The layout is the scratchpad with one buffer (2,104 KB), as L2's.

## Meterable on the card later

These are not registered: the blind day writes its own.
- **One launch.** Each card configuration above is sized to about 0.5-0.75 s by its estimate, at least 0.5 s at the
  point.
- **A burst.** `--launches K` repeats it in one process, as `workloads/sparseparity/energy.sh` meters bursts of about 6 s:
  - copy: 8 launches;
  - SHA-256: 9 launches or fewer. *(Corrected; the first text said 10.)* The guard starts a launch only while the time
    left is at least its model (0.768 s) plus 0.5 s, so none starts after about 8.23 s. With about 0.4 s of set-up, a
    10th launch is refused once a launch takes 0.87 s or more, inside the estimate's band (high end 0.928 s). A burst the
    budget cuts short then reports FAIL (`launched != launches`), though every record is good. The kit picks K from
    the guard's arithmetic at the band's high end.
  - sort: 8 launches;
  - sparse parity: about 12 launches (`--reps`), as `energy.sh` sizes a burst to 6 s.
- **The process ends inside 10 s.**
  - `--budget` defaults to 9.5 s from the process's start.
  - A launch starts only if its timeout still fits.
  - A launch's timeout is min(8 s, 2 x the guard's model + 1.5 s, the time left).
  - The guard's model is slower than each estimate's point, not than its band. *(Corrected; the first text said
    "deliberately slow".)* SHA-256 is modelled at 0.768 s against the band [0.570, 0.928]; the sort at 0.952 s, the
    shuffled band's high end; the copy at 1.503 s against [0.557, 0.755]. A launch over `--max-kernel-s` (4 s) is
    refused.
  - The host's own work in the copy (1 GiB of random bytes made, written, read back and compared) should take about
    2-3 s (an estimate; not measured on a card).
  - Run it as the lab's runners do: `flock -n /run/lock/etsoc-shire0.lock timeout 10 ledger_host --card ...`.
- **The meter.** The host opens the card's ops node only, so `ettelem sample --every-ms 100` can hold the management node.
- **The card path is untested.** `--card` has never run, and the blind day's kit must give it a smoke run and its device
  command audit, as every card kit does.
- **For the kit:**
  - Always pass `--expect` with the card configuration's SHA-256 digests. Above 1 GiB of messages, the host checks only
    64 participants itself.
  - The sort's work area is now pre-filled with 0x5A, as the copy's destination is (fix-q166; sort PASS in the simulator,
    sorted and shuffled). So an identical sort left in DRAM by an earlier run cannot hide a missing write-back.
  - An `--expect` mismatch now names its participant in `first_mismatch` (`participant 2 (--expect)` on a deliberately
    altered digest in the simulator).
  - Add the new instance as an `energy.sh` preset: only l1, l2, f5h0 and f5h1 exist.

## Build and run

```bash
cmake -S workloads/ledger -B build/ledger -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build/ledger -j4
build/ledger/host/ledger_host --selftest                                   # the host's SHA-256 on FIPS vectors
build/ledger/host/ledger_host --dry --prog sha256 --block 2048 --repeat 800    # the inputs and the guard's model only
build/ledger/host/ledger_host --sysemu --prog sort --shires 0x1 --keys 512 --reps 1 --order shuffled
python3 -I -B workloads/ledger/ledger_desk.py digests --seed 1 --block 2048 --repeat 2 --participants 64 --out e.txt
build/ledger/host/ledger_host --sysemu --prog sha256 --shires 0x1 --block 2048 --repeat 2 --expect e.txt
```

To count a run, build against the profiling simulator's prefix and follow `tools/counter/README.md`:
`run_counted.sh --dis ledger.dis --out DIR -- ledger_host --sysemu --sim-args @SIM@ ...`. Then run
`python3 -I -B workloads/ledger/ledger_estimate.py --runs <the cases> --out estimates.json`.

## How the counts and the estimates were made

**Counts.** Each program ran twice in the simulator on shire 0 (64 participants), every hart logged:
- the copy with 1 and 2 passes;
- SHA-256 with the block repeated 1 and 2 times;
- the sort with 1 and 2 sorts.

The difference of the two runs is one unit of work, exact. Its two parts are kept apart:
- The copy's per-byte part is its loop body, found by its addresses in the disassembly and its per-address counts.
- The rest of each pass is a per-pass overhead.

The card's counts are fixed + units x per unit, times 2,048 participants (scaled). The simulator runs one instruction a
cycle on each hart: it neither shares the pipeline between a minion's two harts nor models the caches. So its cycles are
reported beside the counts, not used.

**Seconds.**
- SHA-256 and the sort: the sum over instructions of 1 / the catalogue's issue rate for that row, with both harts issuing
  (03a's "issue per hart per cycle"). The band's high end puts every one-cycle integer op at the in-place rows' rate (about
  0.21, `add_norvc` and `c.add`). L2 stalls are not in it.
- **The band is one-sided by construction:** its point is its low end, the catalogue's issue rates with both harts
  issuing. For the sort that low end is not a floor. Taken branches and jumps are 43% (shuffled) and 47% (sorted) of its
  modelled hart-cycles, at 17.3 hart-cycles each. That rate (`beq_taken`) was measured with both harts branching back to
  back, and the catalogue has no one-hart branch row; a lone hart issues `add` at 0.581 a cycle against 0.373 with both.
  If the other hart issues at the one-hart rate during a branch bubble, the sort runs about 20% under its band's low end:
  sorted about 0.50 s, shuffled about 0.60 s. SHA-256 is less exposed (branches are 9% of its hart-cycles): about 0.53 s
  at worst. *(Desk arithmetic of Q166's verifier, on catalogue.json and estimates.json.)*
  - The blind day's frozen seconds need a two-sided band.
  - About 1,800 sorts a launch keeps the fast end at 0.5 s or more.
  - Score joules given the measured seconds first, as the checkpoint's scoring rule does.
- The copy is DRAM-bound: the stores at the write-back path's 27 GB/s (04 §4.1) at the low end, plus the loads' bytes at
  76 GB/s at the high end.

**Joules over idle.**
- Every instruction is priced at its catalogue row: aifoundry3's mean on random operands, and its band from the row's low
  across passes and cards to its high. For one-cycle integer ops, the high end is the row's own high times 2.06.
  - 2.06 is the in-place row's high (`add_norvc`, 19.80 pJ) over `add`'s aifoundry3 mean (9.61 pJ). For `add` it gives
    21.2 pJ, 2.2x its mean.
  - *(Corrected; the first text said "up to the in-place rows' 1.73x", the ratio of the two rows' means. The code
    applies 2.06.)*
- Branches are priced by outcome.
- The copy's loads are priced at the tensor-load DRAM row, by analogy. Its stores are priced at the fsw.ps write-back path.
  These per-byte prices include their own instructions, which are not priced again.
- Bytes past the L1 are bracketed for SHA-256 and the sort, from none to every line once a merge level (or a compression's
  message line and 8 more) at the L2's price (04 §4.2).
- Energy manual 4.2's L2 and DRAM rows were measured with tensor loads (memhier, "hart 0 of every minion streaming 1 KB
  tensor loads"); only its L1 row is `flw.ps`. So the copy's vector loads, and SHA-256's and the sort's bytes past the L1,
  are all priced **by analogy with tensor loads**. *(Corrected; the first text called these rows memhier's and the L2's
  "flw.ps" prices.)*
- The copy's two columns come from different references. Zeros use the three-card means (94.6 and 247.4 pJ/B), because
  4.1 has no per-card zeros. Random uses aifoundry3's own values (127.3 and 325.8). aifoundry3 runs at 0.95-0.96x the means
  on random data, so the zeros figure may read about 4% high, inside its band.

**The card at rest and the leakage rise.** These are the ledger v2 of Q166's step 1: `tools/ledger/ledger_v2.py` and
`docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json`, frozen at sha256 59ff9117....

**Sparse parity.** Its whole estimate is the ledger v2. It is built as `loads_ledger_v2.py` builds E59:
- the planner's counts for the new (n, k, m);
- the fitted cycle model's busy cycles;
- 2 KB of tensor loads an op (the counter's figure);
- the host's `--dry` model_s as the forecast seconds.

The counter's own split and fit (`tools/counter/card_compare_sparseparity.py`'s functions) gives the counts beside it:
- **The split.** An instruction inside `wait_count` is a spin, whose count follows the simulator's timing. Every other
  instruction is work.
- **The fit.** Hart 0's work = 1,649 an output tile + 1,195 a row tile. Hart 1's work = 11,996 a row tile.
- **The data.** Least squares over the three slices, then scaled to the plan's 14.9 M output tiles and 1.66 M row tiles.
- **Residuals.** The worst class residual is 23%, for not-taken branches.
- **Rescans.** The kernel's rescans add 1.7% int8 ops over the plan.

As a cross-check, the counted work priced at one catalogue row a class lands near v2's instruction and staging terms:
1.15 J against 1.29 J (desk arithmetic, not a score). Half of it is the 1.49 G staging stores.
*(Corrected:)* those stores are `fswg.ps`, global stores into the own scratchpad by its explicit shire address, and the
counter puts them in the region `scratchpad_own`. The first text called them `fswl.ps` at 386 pJ each.
- The catalogue has no `fswg.ps` row. Its `fswl.ps` row (386.3 pJ on aifoundry3) was measured on a DRAM buffer, the L2/L3
  path.
- By analogy with the own scratchpad's tensor-store path (04 §4.1, aifoundry3: 4.65 pJ/B on zeros, 7.87 on random, so
  149-252 pJ a 32 B store), the staging half reads 0.22-0.38 J instead of 0.58 J, and the cross-check about 0.80-0.95 J.
- No estimate uses this cross-check.

**Four weak points of sparse parity's estimate** (named by Q166's verifier; none changes a figure above):
- **Its seconds' band is not in its joules' band.** The J-with-rest band [18.8, 25.3] is computed at the fixed model_s,
  0.515 s. At est_s, 0.669 s, the card at rest adds about 3.8 J (24.93 W x 0.154 s). The plain programs' bands carry
  their seconds' band. Sparse parity's is not widened because it is the ledger v2 exactly as v2 prices E59 given its
  seconds: the blind day's registration freezes a seconds band of its own.
- **One buffer or two.** The three counted slices ran with nbuf 2 and a 1,264 KB layout, the host's own choice for one
  minion a shire. The card plan uses nbuf 1 and 2,104 KB. Q166's fix lane counted slice 0 again with `--nbuf 1`
  (aifoundry3, the same kernel, 19:25-19:27 PST; the plan's cut then gives that slice 29,456 ops and 31 row tiles,
  against 25,704 and 27).
  - Per unit, the work is the same within 0.6%: hart 0 59.41 instructions an op against 59.75; hart 1 16,483 a row tile
    against 16,549.
  - The spin loops differ, as they follow the timing.
  - *Desk check of code against the simulator's own log.*
- **The ledger's double count.** v2 prices each op's cycles inside both the tensor price and the scratchpad-load price
  (3.3-4.9% of each E59 solve; `docs/reports/data/2026-11-12-q166-ledger-v2/posthoc-v2.json`). This estimate inherits it.
- **Hart 1's fit goes through the origin.** For the L1 solve, the counter's fit with an intercept moves the occupancy
  from 0.199 to 0.193 (`card-compare-l1b.json`).

## What the estimates do not know

- **The write-back path inside a copy.** The 325.8 pJ/B was measured on a store-only stream. A copy's loads may change
  the stores' cost, and the vector loads' DRAM price is by analogy with tensor loads.
- **Real issue rates.** The rates are the catalogue's, measured on one instruction repeated. SHA-256's rounds are
  dependency chains and the sort's inner loop is branch-heavy. The bands try to cover this; only the card's cycle counter
  will say.
- **Caches.** The simulator does not say which level served each access. The L1 is 512 B a hart (E48). SHA-256's
  schedule and constants (512 B together) and the sort's 6 KB a hart do not fit it. The bands bracket this. The card's
  `hpmcounter6` (L1 misses to L2) and the shire caches' counters (`tools/counter/README.md`, "Bytes by level") can
  measure it on the blind day.
- **Operand data.** It is the random column throughout. SHA-256's state words and the sort's keys are random. The copy's
  addresses and counters are not, and the zeros column is inside their band.

## Builds on

The stock-take's rule for lanes (MAP § 3).
- **(1) Checked:** the stock-take's inventory, read Thu 12 Nov 2026. Public rows read:
  - L02 (E1-E4: the counter carry, pmcsel);
  - L06 (the energy manual and the full catalogue);
  - L08 (the V3 three-card check, E48 by level);
  - P23 (test-compute-kernels' scaffolding, which `crt.S` and `sections.ld` come from through `workloads/enercat`);
  - P27 (counter and observability pieces);
  - H04 (Q126(c)'s joined load model).
- **(2) Used:**
  - L06: `docs/energy-manual/03a-every-instruction.md` (rows and issue rates), `04-bytes-memory.md` §4.1 (the DRAM paths,
    the fsw.ps write-back path) and §4.2 (L2), and `docs/reports/data/2026-09-23-energy-manual/catalogue.json`.
  - `workloads/enercat` (the session, the CMake pattern, `crt.S`, `sections.ld`).
  - `workloads/sparseparity` (its kernel and host as they are; the erratum 1.23 rule) and `workloads/memprobe` (the late
    carry).
  - `workloads/sgemm` (whole lines per hart).
  - Q166's step 1: the ledger v2, `tools/ledger/`.
  - Q166's step 2: `tools/counter/` and its profiling simulator.
  - The checks against earlier measurements of the same quantity:
    - the copy's per-byte prices are 04 §4.1's own rows;
    - SHA-256's and the sort's prices are 03a's own rows;
    - nothing here was measured on a card, so nothing is scored.
- **(3) Not used:**
  - the joined model's v1 (retired; v2 replaces it);
  - the tensor paths' DRAM prices for the copy (beside its estimate above, not in it);
  - the archive.
- **(4) Tiers:** public pieces only; no check of any private tier was made for this folder.
- **(5) Readiness:** not a registration. Nothing here gates a card.

## Files

| file | what |
|---|---|
| `kernel/ledger.c`, `kernel/crt.S`, `kernel/sections.ld`, `kernel/CMakeLists.txt` | the device kernel (crt and linker script as `workloads/enercat`'s) |
| `host/main.cpp`, `host/CMakeLists.txt`, `host/Constants.h.in` | the host program |
| `ledger_args.h` | the arguments and the 64 B record, shared |
| `CMakeLists.txt` | builds both |
| `ledger_desk.py` | the inputs' generator mirrored in Python, the desk's digests (`hashlib`), a digest comparison |
| `ledger_estimate.py` | counts per unit from two runs, scaled to the card configuration, and the first estimates |
| `spp_never_ran.py` | every sparse-parity instance a committed file names, against a candidate |

The runs, their counts, the build facts and the estimates are in
[`docs/reports/data/2026-11-12-q166-progs/`](../../docs/reports/data/2026-11-12-q166-progs/README.md).

SPDX-License-Identifier: Apache-2.0
