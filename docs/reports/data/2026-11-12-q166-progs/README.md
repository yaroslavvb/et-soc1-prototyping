# Q166(c): the blind day's programs in the simulator, counted, with first estimates (Thu 12 Nov 2026)

This folder holds the November checkpoint's plan, step 3: three plain programs and a sparse-parity instance that has
never run, made ready for the blind day. Their code is in [`workloads/ledger/`](../../../../workloads/ledger/README.md),
and the results and the method are in its README. This folder holds the runs, the build facts and the numbers.

- **No card ran.** Nothing here opened a device.
- **Nothing here is frozen or registered.**
- Every run was the simulator, `--sysemu`, on aifoundry3's host CPU on Thu 12 Nov 2026, 16:57-17:33 PST. It used the
  profiling simulator of Q166's step 2 (`tools/counter/`, et-platform 353f20e, sha256 `ce4469ea...`), one job at a time.
  `--dry` and `--selftest` ran too; neither opens a device.

*Dated note (Thu 12 Nov 2026, Q166's fix lane, on its verifier's findings; none changes an estimate):*
- **The counts were made by the counter as it then was.** Two cases were counted again with the fixed counter
  (o-shuf-r1 and s-b256-r2, aifoundry3, 19:23-19:25 PST, the same binaries). Every field of their counts files is
  identical, and the fixed counter only adds fields: the firmware's work outside the kernel, CSR names, and branch
  direction changes.
- **The sources changed in comments, licence lines and two host behaviours.**
  - The comments are `ledger_args.h`'s, and `kernel/crt.S`, `kernel/sections.ld` and `host/Constants.h.in` gained an
    SPDX line.
  - The host now pre-fills the sort's work area and names an `--expect` mismatch.
  - Rebuilt against `/opt/et`, the kernel ELF is byte for byte `78708041…`, and `--selftest` passes.
  - In the simulator, the sort passes sorted and shuffled, and a deliberately altered `--expect` digest reads FAIL with
    `first_mismatch` "participant 2 (--expect)".
  - So the counts and estimates here stand; `build/BUILD-INFO.txt` records the first build's sources.

## What ran, and what each run checked

| case | what | participants | the program's own check | counted |
|---|---|---|---|---|
| `c-v32-rand-p1`, `-p2` | copy, random bytes, 4 KiB each, 1 and 2 passes, 32 B vector moves | 64 (shire 0) | destination = source, byte for byte: PASS, PASS | every instruction |
| `c-v32-zero-p1`, `-p2` | copy, zeros, the same | 64 | PASS, PASS | every instruction |
| `c-x8-rand-p1`, `-p2` | copy, random, 8 B `ld`/`sd` moves | 64 | PASS, PASS | every instruction |
| `sha-b256-r1`, `s-b256-r2` | SHA-256 of a 256 B block repeated 1 and 2 times | 64 | each digest = the host's SHA-256: PASS, PASS; = Python `hashlib` on the desk: 64/64, 64/64 | every instruction |
| `s-b2048-r2` | SHA-256 of a 2 KiB block repeated twice (the card's block size) | 64 | = the host's and, with `--expect`, = the desk's `hashlib` digests: 64/64, PASS | every instruction |
| `o-sorted-r1`, `-r2` | merge sort, 512 keys, sorted input, 1 and 2 sorts | 64 | = `std::sort`, no out-of-order neighbour: PASS, PASS | every instruction |
| `o-shuf-r1`, `-r2` | the same keys shuffled | 64 | PASS, PASS | every instruction |
| `f-sort-2048` | the sort at the card's participant count, shuffled, 1 sort | 2,048 (32 shires) | 2,048 of 2,048 = `std::sort`: PASS | no (functional) |
| `f-sha-2048` | SHA-256, 2 KiB once, at the card's participant count | 2,048 | 2,048 of 2,048 = the host's SHA-256: PASS; = the desk's `hashlib` digests: 2,048/2,048 | no (functional) |
| `f-copy-64m-rand`, `-zero` | the copy at 2,048 participants, 64 MiB in all | 2,048 | every participant's 32 KiB = its source: PASS, PASS | no (functional) |
| `f-copy-1g` | the copy at 2,048 participants, 1 GiB | 2,048 | not finished: stopped by this lane at 5 min 18 s, when the simulator's memory had grown past 10 GB on a shared box | no |
| `p2-dry` | sparse parity's `--dry` for the never-run instance, and for L1 and L2 beside it (no device) | (plan) | the plan and the fitted cycle model: the new instance 0.515 s, L2 0.427 s, L1 0.113 s | no |
| `p2-new-s0`, `-s10000`, `-s19999` | three 1/20000 slices of the never-run instance on one minion | 2 harts | PASS x3: records, count and best rescore ok; the oracle exact on the minion | harts 0 and 1 |
| `p2-small-whole` | a whole small instance with the same k, eta and m, (64, 4, 0.39, 1792, seed 3), on 4 minions | 8 harts | PASS: all 635,376 candidates; the closed forms ok; the oracle exact on all 4 minions; the answer (5, 26, 52, 62) = the planted secret, unique | no (functional) |

Logged runs: every hart of shire 0 (`-ls 0,ffffffffffffffff`) or, for the slices, harts 0 and 1 (`-ls 0,3`). Each was
streamed through a FIFO into `count_kernel.py`, so no log was kept. In all 16 counted runs:
- the counter resolved every run: unresolved 0, no unknown mnemonic, no trap executed;
- no hart was killed and restarted;
- every hart's span of simulator cycles equals its instruction count.

So the simulator runs one instruction a cycle on each hart. It does not share a minion's pipeline between its two harts
and has no cache model, so its cycles are reported, never used as seconds. The kernel's own `hpmcounter3` reading
(`hart0_cycles` in `out.json`) times the work alone.

The kernels' digests against Python `hashlib`'s computed on the desk (`digests/compare.txt`): 64/64, 64/64 and 64/64 on
shire 0, and 2,048/2,048 at the card's participant count. `digests/expect-card-b2048-r800.txt` holds the card
configuration's 2,048 digests, for the blind day's `--expect`.

## The numbers

[`estimates.json`](estimates.json) holds every program's numbers:
- its counts per unit and fixed;
- the card configuration's totals by mnemonic and by the counter's classes;
- its bytes;
- its seconds;
- every ledger term with its band;
- the card at rest, and the leakage rise.

[`estimates.txt`](estimates.txt) is the one-table view. Labels:
- The counts are **counted** for 64 participants (the simulator's log) and **scaled** to 2,048 by arithmetic.
- The seconds and joules are an **estimate**, not frozen.
- In the records' (05-claims) words, **sim** and **counted** are desk checks of code (in the simulator, or against its
  own log); **scaled** and **estimate** are desk arithmetic, an estimate (not registered, not blind, not held out).

## The never-run instance

[`spp-never-ran.txt`](spp-never-ran.txt) is `workloads/ledger/spp_never_ran.py`'s output. It ran over the lab tree at
7ea49400 plus Q166's three lanes' files, with this folder left out (once landed, this folder names the instance itself):
- no committed file names n = 544, or eta = 0.39, or m = 1,792;
- the instance (544, 4, 0.39, 1792) has never run, by the committed record.
- The first candidate, (448, 4, 0.42, 3584), was outside the host's range (m <= 2,560) and was refused before any run;
  its refusal is not kept.

## Build

[`build/BUILD-INFO.txt`](build/BUILD-INFO.txt) has:
- the kernel's ELF, its `.text` and the host, by sha256;
- the source tarball;
- the toolchain;
- the C flags;
- the prefix;
- the counter's files, the same bytes as `tools/counter/`.

[`kernel/ledger.dis.gz`](kernel/ledger.dis.gz) is the disassembly the counter read.

Built with `-DCMAKE_PREFIX_PATH` at the profiling simulator's shadow prefix. Its `bin/` and `lib/` link to the installed
ET tree except `sys_emu` and `libsw-sysemu.a`, so the kernel was compiled by the installed `riscv64-unknown-elf-gcc`
15.1.0.

## Reproduce

From the top of the tree:
- **Every estimate, byte for byte, with Python 3.12 or later.** This was checked on a tree with all three lanes' files.
  Under Python 3.9 (`/usr/bin/python3`, the interpreter the day-2 check uses), `sum()` rounds differently. Sparse parity's
  `j_over_idle_band` low end then reads 6.1273900107608 against 6.1273900107607995 here.

  ```bash
  D=docs/reports/data/2026-11-12-q166-progs
  python3 -I -B workloads/ledger/ledger_estimate.py --runs $D/runs --dis $D/kernel/ledger.dis.gz \
      --spp-dry $D/runs/p2-dry/new-dry.json --spp-slices $D/runs/p2-new-s0,$D/runs/p2-new-s10000,$D/runs/p2-new-s19999 \
      --out estimates-check.json && cmp estimates-check.json $D/estimates.json
  ```

- **The never-ran survey:**
  `python3 -I -B workloads/ledger/spp_never_ran.py --exclude $D --n 544 --k 4 --eta 0.39 --m 1792 --seed 3`.

- **What the estimator reads from the other two steps:**
  - `tools/ledger/` and its frozen constants;
  - `tools/counter/card_compare_sparseparity.py`'s functions;
  - `count_kernel.py`;
  - the sparse-parity kernel's disassembly and address map in
    `docs/reports/data/2026-11-12-q166-counter-sparseparity/kernel/`.

## Files

| path | what |
|---|---|
| `runs/<case>/out.json` | the host's JSON line (home paths written as `~`) |
| `runs/<case>/counts-log.json.gz` | the counter's ledger-counts/1, every logged hart, per address |
| `runs/<case>/RUN.txt`, `counter.out`, `err.tail` | the command, the counter's summary, the last 6 KB of the host's stderr |
| `runs/*.digests`, `digests/` | the kernels' digests, the desk's `hashlib` digests, the comparisons |
| `estimates.json`, `estimates.txt` | `ledger_estimate.py`'s output |
| `spp-never-ran.txt` | the never-ran survey |
| `batch-log.txt` | the box batches' own log, with times |
| `runs-fixq166/` | the fix lane's simulator checks (`COMMANDS.txt`): the sort with its pre-filled work area, the `--expect` mismatch, two cases counted again with the fixed counter (`recount-regression.txt`: 0 differences), and the never-run instance's slice 0 with `--nbuf 1` (`nbuf-units.json`) |
| `build/BUILD-INFO.dated-note-1.txt` | the rebuild from the fixed sources: the kernel ELF byte for byte, the changed sources' sha256 |
| `SHA256SUMS` | every other file here |

SPDX-License-Identifier: Apache-2.0
