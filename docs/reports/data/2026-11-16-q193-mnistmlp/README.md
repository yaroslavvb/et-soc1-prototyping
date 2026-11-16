# E202's program built and checked: one pass over MNIST in int8 (Q193, lanes mnist-kernel and fix-mnist)

*Sun 15 Nov 2026 23:05 PST to Mon 16 Nov 2026 02:3x PST. **No card was used, no device was opened, nothing was set.**
The program is [`workloads/mnistmlp`](../../../../workloads/mnistmlp/README.md); this folder holds what ran on the desk
(aifoundry2's CPU, inside the round's CPU slots, every host run inside the box's no-device wrapper) and in the
simulator (sys_emu inside the host, on aifoundry3's CPU, one short run at a time, while no lane booked aifoundry3).
Lane mnist-kernel built and checked the program; its verifier (verify-mnist) found two minor items and some smaller
ones, and lane fix-mnist answered them before the program's registration (section 6). Interpreter for every Python
step: `/usr/bin/python3` 3.12.3 with numpy 1.26.4 (aifoundry2), `python3` 3.12.3 (aifoundry3, the counter). Labels:
**measured on the desk**, **simulator**, **desk check of code**, **REPORTED** (from another lane's record).*

## 1. The data and the weights (measured on the desk)

| item | value |
|---|---|
| MNIST, four files | fetched by `model/fetch_mnist.sh`; each `.gz` and each decompressed file equal to `model/MNIST-SHA256SUMS` (`desk/fetch_mnist.out`) |
| trained weights | `model/train_int8.py`, seed 20261116, 6 epochs, 4 BLAS threads, 157.9 s (`desk/train-report.json`) |
| float accuracy, test / train | 98.49% / 99.98% (epochs 1-6 on test: 95.65, 97.38, 98.16, 98.35, 98.46, 98.49%) |
| int8 as the kernel computes, test / train | **98.49% / 99.98%**; the int8 and float labels agree on 99.98% of the test images |
| multipliers M, layers 1-4 | 4,492,549; 5,426,027; 4,596,950; 5,296,301 |
| largest accumulator, layers 1-5 (train) | 454,057; 349,965; 425,870; 309,399; 1,644,386 (int32 bound 2^31; design bound 58,490,880) |
| hidden activations that are 0, layers 1-4 (train) | 68.2%, 64.5%, 58.9%, 55.0% |
| random weights | `mnist_model.py make-random`: splitmix64, M = 1,726,822; 2,147,734; 2,186,718; 2,268,014; zero activations 53.7-57.0%; labels meaningless (13.9% / 14.1% "accuracy") |
| pins | `model/PINS-SHA256SUMS`: the 8 MNIST files, both weights files, the 8 expected-output files |

The trained int8 tensors are byte-identical (all five layers' sha256) to the E202 design lane's feasibility run of
the same recipe on the same box, and its expected labels' sha256 equal that run's (post hoc). The random
configuration folds the rounding offset floor(2^31 / M) into its zero biases, as the trained one does (its stored
hidden-layer biases are therefore 1,243; 999; 982 and 946, not 0), so its multipliers for layers 2-4 differ from the
design run's (which used no offset there). Its bytes also depend on numpy's default (linear) percentile method and on
M rounded to nearest (`workloads/mnistmlp/README.md`); a verifier's independent regeneration with those two choices
reproduced its pin, and with a floor instead gave another file (REPORTED, Q193 lane verify-mnist).

## 2. Desk checks (measured on the desk; `desk/`)

- `mnistmlp_host --selftest`: SELFTEST PASS, 8 of 8 (SHA-256, splitmix64, the B-tile interleave against a direct product,
  449 chunks and 10,892 tiles, the resident layout fits 360 tiles a shire, the requantization's floor and clamp).
- `model/selftest_model.py`: MODEL-SELFTEST PASS, 12 of 12 (float64 product = int64 at K = 1,792 with extreme
  operands; the B-tile interleave; splitmix64 vectorised = scalar; argmax's first maximum; floor and clamp; the file
  formats; the checksum's wrap).
- **The bit-exact numpy model against the host's reference, 4 groups (64 images) per case, trained and random weights,
  train and test splits:** `mnistmlp_host --ref` (the host's own C++ emulation of the kernel's arithmetic on the packed
  tiles it sends the card) read PASS in all 4 cases: 64 of 64 labels, 4 of 4 checksums and 4 of 4 raw layer-5 C tiles
  equal to the model's expected files; and `mnist_model.py compare-ref` (the model in int64 against the host's output
  file) read EQUAL in all 4. A negative control (trained weights against the random expected file) read FAIL as it
  must (27 label mismatches in 32 images).

## 3. The simulator (aifoundry3; `sim/`)

**The first build stopped, and why.** Its hidden layers wrote each C tile with one TensorStore into the next layer's
buffer. In sys_emu the run stopped at layer 2's first TensorLoad of that buffer (both minions, after 1,456
TensorIMA8A32 and 112 TensorStores each): sys_emu's memory checker, on by default in every host-run simulation,
reported "FATAL EMU: [Mem-Checker] (Coherency Read Hazard)" on every line of the buffer (a log-free rerun, `sim/
diag-d1/`, peak resident set 310 MB, showed the messages that the counted runs' instruction-log stream had carried
away). A TensorStore passes through the shire cache's coalescing buffer, which must be drained before a TensorLoad
reads the line (`workloads/sparsity`'s README says the same). The build now writes the activations with whole
32-byte `fswg.ps` stores, two column blocks at a time (`workloads/mnistmlp/README.md`, "Two changes from the design").

**The runs of the final build** (kernel `.text` `ace7bcb0...`, the same on both boxes and in every run; every run's
host compared every label line, checksum and, where named, every layer-5 C tile with the model's expected files, bit
for bit). *host* is the host process's time in `RUN.txt`; *wall* is `sysemu_check.sh`'s line for the run, the counter's
start and finish included (an earlier version of this table mixed the two).

| run | staging | shires x minions | groups | weights | checks | host result | host | wall |
|---|---|---|---|---|---|---|---|---|
| S0a | dram | 1 x 2 | 2 (1 round) | trained | labels, checksums, 2 C tiles | **PASS** | 78 s | 83 s |
| S0b | dram | 1 x 2 | 2 (1 round) | trained | labels, checksums | **PASS** | 79 s | 84 s |
| S0c | dram | 1 x 2 | 4 (2 rounds) | trained | labels, checksums | **PASS** | 119 s | 124 s |
| S0r | dram | 1 x 2 | 2 (1 round) | random | labels, checksums, 2 C tiles | **PASS** | 80 s | 85 s |
| S2 | dram | 1 x 32 | 32 (1 round) | trained | labels, checksums | **PASS** | 212 s | 217 s |
| S1 | scp (remote copies) | 32 x 1 | 32 | trained | labels, checksums, 32 C tiles | **PASS** | 212 s | 217 s |
| S3 | dram | 1 x 2 | 3 (2 rounds; 1 padding group) | trained | labels, checksums, 3 C tiles, the discard line | **PASS** (core PASS, logits PASS) | 119 s | 124 s |
| S3x | dram | 1 x 2 | 3 (2 rounds; 1 padding group) | trained, the random configuration's logits file | as S3: the logits must disagree | **FAIL as wanted** (core PASS, logits FAIL, exit 1) | 117 s | 122 s |
| S1b | scp (remote copies) | 32 x 2 | 63 (1 round a shire; 1 padding group) | trained | labels, checksums, 63 C tiles, the discard line | **PASS** (core PASS, logits PASS) | 362 s | 367 s |

Every run: every working minion's record correct (this epoch, no error flag, `tensor_error` 0, groups = rounds, ops =
groups x 10,892, barriers = groups x 449); ops 21,784 (S0a, S0b, S0r), 43,568 (S0c, S3, S3x), 348,544 (S1, S2) and
697,088 (S1b) as planned; 0 label lines unwritten, 0 label and 0 checksum mismatches; 102 of 102 checked C tiles
bit-exact in the runs that wanted them (S0a 2, S0r 2, S1 32, S3 3, S1b 63), and 3 of 3 different in S3x, whose
expected-logits file is the other configuration's.
S1 also ran the resident copy (the largest share 5,760 lines = 360 tiles, the layout's limit), the chip barrier and
every chunk copy from another shire's scratchpad. The simulator's checkers (memory coherence, L1 and L2 scratchpad,
FLB, TensorStore; all on by default, `SysEmuOptions`) stopped no run of the final build.

**The padding path (S3, S3x, S1b; lane fix-mnist).** A launch of N groups at P minions a shire has ceil(N / P)
rounds, and in the last round the minions past group N - 1 take a padding group: input group 0, the whole group's
work, and the slot's discard line (line N + slot) in place of a label line. The six first runs had no padding group;
every planned one-pass smoke (26 padding groups) and the test split's launch (15) has some. In S3 minion 1's second
group was a padding group: its discard line read correct (1 of 1; group N + slot, this epoch, done and discard flags,
slot, input group 0), the records counted 4 groups with 1 padding group and 43,568 operations, and every TensorIMA8A32,
TensorLoad, TensorLoadB, TensorLoadL2Scp and `fswg.ps` count equals S0c's (whose second round had a real group there;
`counts_scale.py`'s padding check: 0 differences). In S1b (scp staging, 2 minions a shire) shire 31's minion 1 took
the padding group (discard line 1 of 1), and every shire split its resident copy and every chunk copy between its two
minions. **The debug-logits gate:** S3x repeats S3 with the random configuration's expected-logits file, so that only
the logits can disagree: the host read `core_status` PASS, `logits_status` FAIL and `status` FAIL (exit 1), as wanted,
and its counts equal S3's in every field (the run is deterministic; the explicit checker flags S3 adds change
nothing). The three runs' host stderr held only the device layer's INFO lines and two lines naming the UART logs: 0
fatal, 0 error and 0 memory-checker lines (`sim/fix-mnist-stderr-summary.txt`; the logs, 38-109 MB each, were removed
after the summary). They ran the fixed host (`build/BUILD-INFO.txt`); the six first runs ran the earlier host, whose
checks are the same less the two new status fields.

A log-free rerun in S0b's configuration
(`sim/diag-d2/summary.txt`; the counted runs' checker messages go into the instruction-log stream) read PASS with 0
fatal and 0 error lines and 240 `-vpurf_warn` warnings, none at a kernel PC: all in firmware code (the master shire,
the service processor, and an idle minion of shire 0). The
simulator has no timing: its cycle counts equal the instructions, so the records' cycles say nothing about seconds.
Memory: the host with the simulator inside peaked at about 310 MB resident (`sim/diag-d1/time-v.txt`); every counted
run ran under a 4 GB address-space limit (`prlimit --as`).

## 4. The counts (simulator, counted by `tools/counter`; `counts/`)

Counted by `tools/counter` (the instruction-log route, exact for every logged hart), reduced by
`workloads/mnistmlp/counts_scale.py` (`counts/counts-summary.json`, `counts/counts-tables.txt`). **Per group** = the
counts of one more group on one minion; **P = 32** is a card's shire-round (S2's minion 0 less the per-launch part
measured at P = 2), **P = 2** is S0c - S0b. The two differ only in the copy loop (at P = 2 a minion copies half of every
chunk; at P = 32, 1 tile or none) and the barrier polls. Minions 0, 27 and 31 of S2 retire 492,883, 492,881 and
492,882 instructions a group: the copy loop and the polls trade places.

| class (energy manual) | per group, P = 32 | per group, P = 2 | per launch, a minion (P = 2) | per pass (3,750 groups, P = 32 pattern) |
|---|---|---|---|---|
| `scalar_int` | 276,106 | 347,193 | 7,952 | 1,035,397,500 |
| `vector_int` | 69,440 | 69,440 | 0 | 260,400,000 |
| `tensor` | 56,731 | 66,388 | 6 | 212,741,250 |
| `float_int_xfer` | 20,640 | 20,640 | 32 | 77,400,000 |
| `load` | 15,708 | 30,867 | 2,760 | 58,905,000 |
| `store` | 6,810 | 7,069 | 86 | 25,537,500 |
| `store_past_l1` | 3,584 | 3,584 | 0 | 13,440,000 |
| `branch_taken` | 14,995 | 14,642 | 1,242 | 56,231,250 |
| `branch_not_taken` | 14,528 | 24,206 | 1,924 | 54,480,000 |
| `jump` | 4,958 | 9,540 | 6 | 18,592,500 |
| `mask_broadcast` | 3,136 | 3,136 | 1 | 11,760,000 |
| `system` | 4,041 | 4,041 | 23 | 15,153,750 |
| `sync` | 2,204 | 1,684 | 3 | 8,265,000 |
| `int_muldiv` | 2 | 2 | 1 | 7,500 |
| **instructions** | **492,883** | **602,432** | **14,036** | **1,848,311,250** |

*Simulator count for the per-group columns; the per-pass column is a desk scaling (every group runs the same path; the
data change only the argmax's branch outcomes, and the `sync` class and the poll loop's branches follow the
simulator's timing, not the card's: the card's records give its barrier-wait cycles).* The tile loop issues about 30
scalar instructions and 5 tensor-unit CSR writes per TensorIMA8A32; the vector-integer count is the requantization,
exactly 310 instructions per pair of column blocks (224 pairs a group). About 20,640 `fmv.x.w` a group are the
errata's register touches.

**Tensor operations and bytes, exact by construction and equal to every counted run:**

| item | per group | per shire-round | per pass (3,750 groups, 117.1875 shire-rounds) |
|---|---|---|---|
| TensorIMA8A32 (16 x 64 x 16, int8 x uint8 -> int32) | 10,892 ops, 178,454,528 MACs | | 40,845,000 ops, 6.692 x 10^11 MACs |
| TensorLoad A, own scratchpad -> L1 scratchpad | 10,892 x 1 KiB | | 41.83 GB |
| TensorLoadB, own scratchpad (staging) -> TenB | 10,892 x 1 KiB | | 41.83 GB |
| TensorLoadL2Scp, the group's input, DRAM -> own scratchpad | 13 x 1 KiB | | 49.9 MB |
| TensorLoadL2Scp, the chunk copies (dram staging: from DRAM; scp: from the keeping shire's scratchpad) | | 10,892 x 1 KiB | 1.307 GB |
| `fswg.ps` activation stores, 32 B, own scratchpad | 3,584 (114,688 B) | | 13,440,000 (430.1 MB) |
| label line (plain stores), DRAM | 64 B | | 240 KB |
| scp staging only, per launch: the resident copy, DRAM -> the keeping shires' scratchpads | | | 10,892 x 1 KiB a launch |

In S1 (scp staging, P = 1) shire 0's minion copied 10,532 tiles from other shires' scratchpads
(`bytes_scratchpad_remote` 10,784,768 B), 360 from its own resident region and 373 from DRAM (13 input tiles and its
360 resident tiles): the remote path ran, and every label, checksum and C tile was right. Other per-group traffic
(simulator count, minion 0 at P = 32): 249,480 B of scalar and vector loads from DRAM addresses (the chunk table, the
bias rows, the stack) and 184,104 B of stores to DRAM addresses (the stack: rows 14-15's spill, the even blocks' slots,
the output tile; and the label line): 433,584 B a group, about 1.63 GB a pass. **Which level serves it is not known:**
the simulator has no cache model, and these addresses are cacheable DRAM. In scratchpad mode a hart has 512 B of L1
(`docs/et-soc1-notes.md`), which the even block's 512 B slot alone fills, so most of this traffic is likely refills
from and write-backs to the shire's L2, not L1 hits (an earlier version of this README called it "L1 traffic in the
main"; that was wrong). E202's registration should bracket it between the L1 and the L2 prices, for joules and for
seconds.

**Every counted hart against the code** (lane fix-mnist; `counts_scale.py`'s derivation checks, desk check of code):
the TensorIMA8A32, TensorLoad and TensorLoadB counts, the `fswg.ps` count and TensorLoadL2Scp by source (each round's
13 input tiles from DRAM; tile t of every chunk copied by minion t mod P, once a round, from DRAM or from the keeping
shire's scratchpad; with scp staging the resident copy, the shire's kept tiles k copied by minion k mod P) equal the
counter's in all 18 counted harts of the nine runs. In S1b shire 0's two minions copied 5,320 and 5,212 tiles from
other shires' scratchpads, 182 and 178 from their own resident region and 193 each from DRAM (13 input tiles and half
of the 360 resident tiles), as derived.

**A launch, exactly** (desk check of code; `counts/counts-summary.json`, `launch_scaling`). The per-pass column above
counts the 3,750 real groups of a pass. A launch issues whole shire-rounds: ceil(groups / 32) of them at P = 32,
working shire i taking rounds i, i + 32, ...; the last round's minions past the last group take padding groups (a whole
group's work each). The launch's seconds follow its busiest shire.

| launch (P = 32, 32 shires) | groups | shire-rounds | group slots | padding groups | busiest shire: rounds (shires) | TensorIMA8A32 issued | chunk-copy tiles |
|---|---|---|---|---|---|---|---|
| one pass of the training split | 3,750 | 118 | 3,776 | 26 | 4 (22) | 41,128,192 | 1,285,256 |
| 16 passes | 60,000 | 1,875 | 60,000 | 0 | 59 (19) | 653,520,000 | 20,422,500 |
| 96 passes | 360,000 | 11,250 | 360,000 | 0 | 352 (18) | 3,921,120,000 | 122,535,000 |
| one pass of the test split | 625 | 20 | 640 | 15 | 1 (20) | 6,970,880 | 217,840 |

Each slot also issues 10,892 TensorLoads and 10,892 TensorLoadBs of 1 KiB, 13 input tiles and 3,584 `fswg.ps`; scp
staging adds the resident copy, 10,892 tiles a launch.

## 5. Files

| path | what |
|---|---|
| `build/BUILD-INFO.txt`, `build/mnistmlp.dis` | toolchains, the sources' and binaries' sha256 on both boxes, the disassembly checks; the kernel's disassembly |
| `desk/` | the self-tests, the training report and log, the random configuration, the expected outputs' summaries, the host's reference against the model; `fix-mnist-desk.txt`, the desk tests re-run with the fixed host |
| `sim/<run>/` | each run's host result (`host-result.json`), the counter's command (`RUN.txt`), its counts (`counts-log.json.gz`); S3, S3x and S1b from lane fix-mnist |
| `sim/fix-mnist-stderr-summary.txt` | the host stderr of S3, S3x and S1b, summarized on the box before the logs were removed |
| `sim/first-build-tstore/` | the first build's two stopped runs (S0a, S0b): their commands and counts |
| `sim/diag-d1/` | the log-free rerun of the first build: the memory checker's messages (`sysemu-excerpt.txt`), `time -v` |
| `sim/diag-d2/` | the log-free rerun of the final build: its warnings classified (`summary.txt`) |
| `counts/` | `counts_scale.py`'s output from all nine runs: per group, per launch, per pass, the padding check, the derivation checks, each planned launch |
| `SHA256SUMS` | every file here |

Folder names on the boxes are written as `~/RUN` in the copied records.

## 6. Fixes before the registration (lane fix-mnist, Mon 16 Nov 2026 01:22-02:3x PST)

The program's verifier (lane verify-mnist, Q193) read HOLDS WITH FIXES: two minor items, four low risks, notes for the
registration and nits; it found no defect in the arithmetic, the traps, the counts or the data's handling. Lane
fix-mnist answered them in these files before E202's registration. **The kernel did not change:** its ELF and `.text`
are byte-identical to the verified build on both boxes (`build/BUILD-INFO.txt`), so the six first runs and their counts
stand.

| the verifier's finding | the answer |
|---|---|
| minor: the padding path had never run in the simulator | S3 (dram, 2 minions, one padding group, every checker) and S1b (scp, 32 x 2, one padding group) read PASS: the discard lines, the records and the work counts right (section 3) |
| minor: "L1 traffic in the main" | corrected (section 4): the level is not known; most of it is likely shire-L2 traffic; to be bracketed |
| low: UA = 1 has not run on silicon | named in the program's README as a risk for the registration, the smoke its gate; the exact UA = 0 fallback described there, not built |
| low: the debug logits' TensorStore of 64 B rows has not run on silicon | the host's result gains `core_status` (every check but the logits) and `logits_status`; S3x read a logits-only failure apart (core PASS, logits FAIL) |
| low: scp staging at 32 x 32 has not run as a whole | S1b (32 x 2) adds the copies split between a shire's minions; 32 x 32 stays too long for the simulator |
| low: the trained weights live only in scratch folders | named in the program's README; their home is the registration's to decide (unchanged here) |
| notes: seconds follow the busiest shire; the one-pass scaling left out its 26 padding groups; keep `--labels-out` | `counts_scale.py` counts each planned launch exactly (section 4) and checks every counted hart against the code; the README gives the rounds, the padding and `--labels-out` |
| nits | `mnistmlp_args.h`'s header (how the activations are stored), the README's random-weights sentence (the biases, the percentile method, M's rounding), `sysemu_check.sh`'s S0b description (the checkers are on by default), the commit message's attribution line, this folder's time columns |

The desk tests ran again with the fixed host (`desk/fix-mnist-desk.txt`: self-tests, the host's reference against the
model in all four cases with byte-equal outputs, the negative control, the dry plans of the four launches against
`counts_scale.py`'s accounting): all as wanted. Files changed or added: `workloads/mnistmlp/` `mnistmlp_args.h`,
`host/main.cpp`, `sysemu_check.sh`, `counts_scale.py` and `README.md`; here `README.md`, `build/BUILD-INFO.txt`,
`counts/`, `sim/S3/`, `sim/S3x/`, `sim/S1b/`, `sim/fix-mnist-stderr-summary.txt`, `desk/fix-mnist-desk.txt` and
`SHA256SUMS`. The box ran `sysemu_check.sh` one comment line older than the committed one (the S3 description); its
code is the same.
